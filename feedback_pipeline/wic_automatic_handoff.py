"""Zero-touch collection, deduplication, routing and Work-batch accounting."""
from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "evidence" / "wic_automatic_handoff_state.json"

BLOCKING_RETURN_PREFIXES = ("HOLD_", "WAITING_", "RETURNED_FAIL", "RETURNED_BLOCKED")


def unresolved_return(row: dict) -> dict | None:
    """Return the latest unresolved item result.

    Generic circulation capabilities describe *how* to run and return evidence;
    they do not satisfy an item's external/input/time resume condition.  Treating
    those wrapper capabilities as the missing business capability caused HOLD
    items to be advertised as immediately executable.
    """
    history = row.get("result_return_history") or []
    latest = history[-1] if history else row.get("result_return") or {}
    status = str(latest.get("status", "")).upper()
    resume = row.get("resume_condition") or latest.get("resume_condition")
    member_states = latest.get("member_state_counts") or {}
    unresolved_members = any(
        count and str(state).upper() not in {"PASS", "PASS_LOCKED", "COMPLETED"}
        for state, count in member_states.items()
    )
    if resume and (status.startswith(BLOCKING_RETURN_PREFIXES) or unresolved_members):
        return {"status": status, "resume_condition": resume}
    return None


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".next")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(pending, path)


def build(queue: dict, pool: dict, gate_state: dict, now: str | None = None) -> dict:
    now = now or datetime.now(timezone.utc).isoformat()
    available = {cap for component in pool.get("components", []) + pool.get("verified_atomic_component_pool", [])
                 if component.get("status") == "VERIFIED_REUSABLE"
                 for cap in component.get("atomic_capabilities", [])}
    terminal = {"PASS", "COMPLETED", "SATISFIED_BY_COMMON_COMPONENT", "PASS_LOCKED"}
    roots, duplicates, easy, work, holds = defaultdict(list), [], [], [], []
    seen = set()
    for row in queue.get("demands", []):
        did, status = row.get("demand_id"), str(row.get("status", ""))
        if status in terminal or status.startswith(("PASS_", "SKIP_REUSE_VERIFIED_PASS")):
            continue
        if "TOOL043" in str(did):
            holds.append({"demand_id": did, "reason": "HOLD_REEVALUATE"})
            continue
        key = (row.get("root_id") or did, tuple(sorted(row.get("atomic_capabilities", []))))
        if key in seen:
            duplicates.append(did)
            continue
        seen.add(key)
        root = key[0]
        roots[root].append(did)
        capabilities = set(row.get("atomic_capabilities", []))
        item = {"root_id": root, "demand_id": did, "capabilities": sorted(capabilities)}
        blocked_return = unresolved_return(row)
        if blocked_return:
            holds.append({**item, "reason": blocked_return["status"],
                          "resume_condition": blocked_return["resume_condition"]})
        elif any(token in status.upper() for token in ("HOLD", "WAITING")):
            holds.append({**item, "reason": status})
        elif capabilities and capabilities <= available:
            easy.append(item)
        else:
            work.append(item)
    completed_jobs = [j for j in gate_state.get("jobs", {}).values() if j.get("STATUS") == "PASS"]
    run_ids = {str(j.get("OWNER", "")).split(":")[1] for j in completed_jobs
               if str(j.get("OWNER", "")).startswith("GITHUB_ACTIONS:")}
    historical_per_run = round(len(completed_jobs) / max(1, len(run_ids)), 2)
    full_threshold = max(10, round(historical_per_run or 10))
    work_units = sum(max(1, len(item["capabilities"])) for item in work)
    anomalies = {
        "duplicate_demands": duplicates,
        "stalled_claims": [j.get("JOB_ID") for j in gate_state.get("jobs", {}).values()
                            if j.get("STATUS") in {"CLAIMED", "RUNNING"} and not j.get("LEASE_EXPIRY")],
        "missing_results": [j.get("JOB_ID") for j in gate_state.get("jobs", {}).values()
                            if j.get("STATUS") == "PASS" and not j.get("RESULT")],
    }
    return {
        "schema_version": 1, "updated_at": now,
        "source_scan": "DURABLE_QUEUE_REGISTRY_CHECKPOINT_AND_ACCESSIBLE_FEEDBACK",
        "unfinished_detected": len(easy) + len(work) + len(holds),
        "common_roots": [{"root_id": root, "demands": ids} for root, ids in sorted(roots.items())],
        "easy_queue": easy, "work_batch": work, "holds": holds,
        "duplicates_removed": duplicates,
        "work_batch_full": work_units >= full_threshold,
        "work_batch_units": work_units,
        "work_batch_full_threshold": full_threshold,
        "threshold_basis": {"completed_jobs": len(completed_jobs), "historical_runs": len(run_ids),
                            "actual_completed_per_run": historical_per_run},
        "work_delivery": "PLATFORM_HOLD_NO_SUPPORTED_UNATTENDED_CHATGPT_WORK_INSERT_API",
        "anomalies": anomalies,
        "next_easy_root": easy[0]["root_id"] if easy else None,
        "observer_reinstruction_required": 0,
        "manual_relay_count": 0,
    }


def run(queue: dict, pool: dict, gate_state: dict, out: Path = OUT) -> dict:
    result = build(queue, pool, gate_state)
    atomic_json(out, result)
    return result
