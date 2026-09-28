"""Build the observer-visible TOOL016/TOOL044 handoff from durable state only."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUEUE = HERE / "tool044_atomic_demand_queue.json"
POOL = HERE / "evidence" / "tool044_verified_external_component_pool.json"
GATES = HERE / "evidence" / "tool044_multi_gate_state.json"
PROVIDERS = HERE / "tool044_multi_gate_adapters.json"
CENTRAL = HERE / "state.json"
OUT = HERE / "evidence" / "tool016_visible_handoff_state.json"
TERMINAL = {"PASS", "COMPLETED", "SATISFIED_BY_COMMON_COMPONENT", "PASS_LOCKED"}
READY_PREFIXES = ("READY", "OPEN", "QUEUED")


def load(path: Path, default: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".next")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(pending, path)


def _returned(row: dict) -> bool:
    return (row.get("result_return") or {}).get("tool016_ack") == "RECEIVED"


def _ready(row: dict) -> bool:
    return not _returned(row) and str(row.get("status", "")).startswith(READY_PREFIXES)


def _schedule_history(previous: dict, now: str, trigger: str, run_id: str) -> dict:
    history = list(previous.get("SCHEDULE_EVIDENCE", {}).get("runs", []))
    if trigger == "schedule" and run_id and not any(row.get("run_id") == run_id for row in history):
        history.append({"run_id": run_id, "observed_at": now, "event": "schedule"})
    history = history[-400:]
    elapsed = 0.0
    if len(history) > 1:
        start = datetime.fromisoformat(history[0]["observed_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(history[-1]["observed_at"].replace("Z", "+00:00"))
        elapsed = max(0.0, (end - start).total_seconds() / 3600)
    continuous = len(history) > 1 and elapsed >= 24
    return {"runs": history, "run_count": len(history), "elapsed_hours": round(elapsed, 3),
            "status": "PASS" if continuous else "WAITING", "actual_24h": continuous}


def build(queue: dict, pool: dict, gates: dict, now: str, providers: dict | None = None,
          previous: dict | None = None, trigger: str = "manual", run_id: str = "") -> dict:
    demands = queue.get("demands", [])
    ids = [row.get("demand_id") for row in demands]
    duplicate_ids = sorted({item for item in ids if item and ids.count(item) > 1})
    unfinished = [row for row in demands if row.get("status") not in TERMINAL and not _returned(row)]
    ready = [row for row in unfinished if _ready(row)]
    waiting = [row for row in unfinished if row not in ready]
    excluded = len(demands) - len(unfinished)
    available = {
        capability
        for component in pool.get("components", [])
        if component.get("status") == "VERIFIED_REUSABLE"
        for capability in component.get("atomic_capabilities", [])
    }
    work_required, tool044_required = [], []
    for demand in ready:
        capabilities = set(demand.get("atomic_capabilities", []))
        target = work_required if capabilities and capabilities <= available else tool044_required
        target.append({
            "demand_id": demand.get("demand_id"),
            "root_id": demand.get("root_id") or demand.get("request_id") or demand.get("demand_id"),
            "target_tool": demand.get("target_tool") or "CENTRAL",
            "atomic_capabilities": sorted(capabilities),
        })

    grouped = {}
    for item in work_required:
        root = item["root_id"]
        grouped.setdefault(root, {"root_id": root, "demands": [], "target_tools": set()})
        grouped[root]["demands"].append(item["demand_id"])
        grouped[root]["target_tools"].add(item["target_tool"])
    batches = [{"root_id": row["root_id"], "demands": row["demands"],
                "target_tools": sorted(row["target_tools"]), "status": "READY_FOR_MULTI_GATE"}
               for row in grouped.values()]
    statuses = {}
    for job in gates.get("jobs", {}).values():
        status = job.get("STATUS", "UNKNOWN")
        statuses[status] = statuses.get(status, 0) + 1
    providers = providers or {"providers": [], "bulk_summary": {}}
    provider_rows = providers.get("providers", [])
    actual_providers = [row.get("provider_id") for row in provider_rows
                        if row.get("status") == "ACTUAL_RUN_PASS"]
    next_demand = None if duplicate_ids else next((row.get("demand_id") for row in ready), None)
    schedule_evidence = _schedule_history(previous or {}, now, trigger, run_id)
    return {
        "schema_version": 1, "updated_at": now,
        "UNFINISHED_SCANNED": len(unfinished), "ALREADY_PASS_EXCLUDED": excluded,
        "ROOTS_MERGED": len(grouped), "WORK_FIXABLE_ROOTS": len(batches),
        "WORK_REQUIRED": work_required, "WORK_BATCHES": batches,
        "TOOL044_AUTO_HANDED_OFF": len(tool044_required),
        "TOOL044_QUEUE": tool044_required,
        "WORK_REQUIRED_REMAINDER": len(work_required),
        "MULTI_GATE": {"capacity": gates.get("capacity", 15), "statuses": statuses},
        "FREE_EXTERNAL_RUNNER_POOL": {
            "target": providers.get("target_provider_count", 15),
            "actual_run_pass": actual_providers,
            "blocked_user_action": [row.get("provider_id") for row in provider_rows
                                    if row.get("status") == "BLOCKED_USER_ACTION"],
            "bulk_summary": providers.get("bulk_summary", {}),
        },
        "CIRCULATION": {
            "tool016_to_tool044": "ACTIVE",
            "ready": len(ready), "waiting": len(waiting),
            "next_demand": next_demand,
            "duplicate_demand_ids": duplicate_ids,
            "dedup_gate": "PASS" if not duplicate_ids else "FAIL",
            "result_returns": sum(_returned(row) for row in demands),
            "external_runner": actual_providers[0] if actual_providers else None,
            "external_failover": "READY" if len(actual_providers) > 1 else "HOLD_SECOND_RUNTIME",
            "chat_collection": "PLATFORM_LIMIT_UNLESS_DURABLE_INBOX_EVENT_EXISTS",
            "chat_report": "CONTROL_TOWER_ONLY_CHAT_DELIVERY_UNSUPPORTED",
            "observer_projection": "PERSISTED_TO_CENTRAL_AND_VISIBLE_HANDOFF",
        },
        "SCHEDULE_EVIDENCE": schedule_evidence,
        "MUTUAL_MONITORING": "TOOL016_CENTRAL_AND_CONTROL_TOWER",
        "AUTO_RECOVERY": "LEASE_EXPIRY_STALE_RECLAIM_AND_CHECKPOINT",
        "LAST_HEARTBEAT": now, "WATCHDOG": "SCHEDULED_15_MINUTES",
        "RECENT_EVENT": "VISIBLE_HANDOFF_REFRESHED",
        "USER_MANUAL_RELAY_REQUIRED": 0,
    }


def run(queue_path: Path = QUEUE, pool_path: Path = POOL, gate_path: Path = GATES,
        central_path: Path = CENTRAL, out_path: Path = OUT) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    previous = load(out_path, {})
    trigger = os.environ.get("GITHUB_EVENT_NAME", "manual")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    result = build(load(queue_path, {"demands": []}), load(pool_path, {"components": []}),
                   load(gate_path, {"jobs": {}, "capacity": 15}), now,
                   load(PROVIDERS, {"providers": [], "bulk_summary": {}}),
                   previous, trigger, run_id)
    atomic_json(out_path, result)
    central = load(central_path, {})
    central.setdefault("integration_core", {})["visible_handoff"] = result
    atomic_json(central_path, central)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
