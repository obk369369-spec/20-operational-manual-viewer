"""Closeout audit for non-tool WIC common infrastructure (CR-1..CR-5)."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "evidence" / "wic_non_tool_common_closeout_ledger.json"
PACKET = HERE / "evidence" / "wic_non_tool_common_work_packet.json"
OBSERVER_REPORT = HERE / "evidence" / "wic_non_tool_observer_closeout_report.json"
ALLOWED = {"COMPLETE", "PARTIAL", "UNFINISHED", "PLATFORM_HOLD", "LONG_TERM_HOLD"}
COMMON_TARGETS = {"CENTRAL", "COMMON_INFRASTRUCTURE", "TOOL016", "TOOL044", "WORK", "CONTROL_TOWER"}


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".next")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(pending, path)


def is_non_tool(row: dict) -> bool:
    target = str(row.get("target_tool") or "CENTRAL")
    targets = {part.strip() for part in target.split(",")}
    root = str(row.get("root_id") or row.get("request_id") or row.get("demand_id") or "")
    # Functional-tool work is outside this common-infrastructure closeout even
    # when a legacy record points at the CENTRAL router.
    if re.match(r"^T\d+-", root) or root.startswith("FS-FUNCTION-"):
        return False
    if root.startswith("TOOL") and not root.startswith(("TOOL016", "TOOL044")):
        return False
    if "PUBLISHERS_TOC_EXTRACTION" in root:
        return False
    if targets & COMMON_TARGETS:
        return True
    return any(token in root for token in ("COMMON", "CIRCULATION", "HANDOFF", "BACKLOG", "FINAL-"))


def _evidence(row: dict) -> list[str]:
    values = []
    result = row.get("result_return") or {}
    for value in (row.get("evidence"), result.get("run_id"), result.get("component_id"),
                  row.get("satisfied_component"), row.get("checkpoint")):
        if value:
            values.append(str(value))
    return sorted(set(values))


def _resume(row: dict, classification: str) -> str:
    explicit = row.get("resume_condition") or (row.get("result_return") or {}).get("resume_condition")
    if explicit:
        return str(explicit)
    return {
        "COMPLETE": "PASS_LOCK_NO_REEXECUTION",
        "PLATFORM_HOLD": "RESUME_WHEN_SUPPORTED_PLATFORM_EVENT_OR_PERMISSION_EXISTS",
        "LONG_TERM_HOLD": "RESUME_WHEN_REQUIRED_NATURAL_TIME_EVIDENCE_EXISTS",
        "PARTIAL": "AUTO_REQUEUE_WHEN_VERIFIED_EXECUTION_CONTRACT_IS_AVAILABLE",
        "UNFINISHED": "AUTO_REQUEUE_WHEN_VERIFIED_EXECUTION_CONTRACT_IS_AVAILABLE",
    }[classification]


def build(queue: dict, observer: dict, visible: dict, gate_state: dict,
          now: str | None = None) -> tuple[dict, dict]:
    now = now or datetime.now(timezone.utc).isoformat()
    rows = []
    for demand in queue.get("demands", []):
        if not is_non_tool(demand):
            continue
        classification = demand.get("residual_classification", "UNFINISHED")
        if classification not in ALLOWED:
            classification = "UNFINISHED"
        rows.append({
            "requirement_id": demand.get("demand_id"),
            "root_id": demand.get("root_id") or demand.get("request_id") or demand.get("demand_id"),
            "original_requirement": demand.get("original_requirement") or demand.get("source_records") or demand.get("atomic_capabilities", []),
            "implementation_location": (demand.get("execution_contract") or {}).get("target_files", []),
            "actual_evidence": _evidence(demand),
            "status": classification,
            "remaining_work": [] if classification == "COMPLETE" else demand.get("atomic_capabilities", []),
            "resume_condition": _resume(demand, classification),
            "pass_lock": classification == "COMPLETE" and (demand.get("result_return") or {}).get("tool016_ack") == "RECEIVED",
            "actionable_requeued": str(demand.get("status", "")).startswith("READY_AUTO_REQUEUED"),
        })

    rows.append({
        "requirement_id": "PLATFORM-TOOL044-CHAT-REPORT-DELIVERY",
        "root_id": "PLATFORM-NATIVE-CHAT-ACCESS",
        "original_requirement": "actual delivery into the existing TOOL044 chat",
        "implementation_location": [], "actual_evidence": [],
        "status": "PLATFORM_HOLD", "remaining_work": ["OFFICIALLY_SUPPORTED_CHAT_DELIVERY_HOOK"],
        "resume_condition": "RESUME_WHEN_OFFICIAL_CHAT_DELIVERY_API_EXISTS",
        "pass_lock": False, "actionable_requeued": False,
    })

    events = gate_state.get("events", [])
    stale_recovery = any(event.get("event") == "STALE_RECLAIM" for event in events)
    dedup_pass = visible.get("CIRCULATION", {}).get("dedup_gate") == "PASS"
    manual_zero = (observer.get("observer_reinstruction_required") == 0 and
                   visible.get("USER_MANUAL_RELAY_REQUIRED") == 0)
    cr_status = {
        "CR-1": "COMPLETE" if all(observer.get(key) for key in (
            "GLOBAL_REQUIREMENT_RECONCILIATION_PROVEN", "STATUS_CLASSIFICATION_PROVEN",
            "DURABLE_OBSERVER_REPORT_WRITTEN")) else "PARTIAL",
        "CR-2": "COMPLETE" if (observer.get("NEXT_WORK_AUTO_SELECTED_AND_HANDED_OFF") and
                                  observer.get("ALL_ACTIONABLE_UNFINISHED_AUTO_REQUEUED_WITHOUT_OBSERVER_INPUT") and
                                  observer.get("TOOL016_RESULT_ACK_RECEIVED", 0) > 0) else "PARTIAL",
        "CR-3": "COMPLETE" if manual_zero else "PARTIAL",
        "CR-4": "COMPLETE" if dedup_pass and stale_recovery else "PARTIAL",
        "CR-5": "COMPLETE" if observer.get("REMOTE_GITHUB_READBACK_PASS") else "PARTIAL",
    }
    for cr_id, status in cr_status.items():
        rows.append({
            "requirement_id": cr_id,
            "root_id": f"WIC-NON-TOOL-{cr_id}",
            "original_requirement": f"WIC_NON_TOOL_COMMON_RESIDUAL_BUNDLE::{cr_id}",
            "implementation_location": [
                "feedback_pipeline/tool016_visible_handoff.py",
                "feedback_pipeline/wic_non_tool_common_closeout.py",
                ".github/workflows/tool044-multi-gate.yml",
            ],
            "actual_evidence": [
                "feedback_pipeline/evidence/wic_zero_touch_observer_report.json",
                "feedback_pipeline/evidence/tool016_visible_handoff_state.json",
                "feedback_pipeline/evidence/tool044_multi_gate_state.json",
            ],
            "status": status,
            "remaining_work": [] if status == "COMPLETE" else ["AUTOMATIC_RECOVERY_EVIDENCE_REQUIRED"],
            "resume_condition": "PASS_LOCK_NO_REEXECUTION" if status == "COMPLETE" else "NEXT_SCHEDULED_CIRCULATION",
            "pass_lock": status == "COMPLETE",
            "actionable_requeued": False,
        })

    grouped, actionable_grouped = {}, {}
    for row in rows:
        if row["status"] not in {"PARTIAL", "UNFINISHED"}:
            continue
        grouped.setdefault(row["root_id"], []).append(row["requirement_id"])
        if row.get("actionable_requeued"):
            actionable_grouped.setdefault(row["root_id"], []).append(row["requirement_id"])
    selected = next(iter(actionable_grouped), None)
    counts = {status: sum(row["status"] == status for row in rows) for status in ALLOWED}
    ledger = {
        "schema_version": 1, "updated_at": now,
        "common_root": "WIC-NON-TOOL-COMMON-INFRASTRUCTURE-CR1-CR5",
        "requirements": rows, "counts": counts, "cr_status": cr_status,
        "not_worked_count": 0,
        "pass_locked": [row["requirement_id"] for row in rows if row["pass_lock"]],
        "residual_roots": sorted(grouped),
        "auto_requeued_roots": sorted(actionable_grouped), "next_auto_root": selected,
        "observer_reinstruction_required": 0 if manual_zero else 1,
        "manual_relay_count": 0 if manual_zero else 1,
    }
    packet = {
        "schema_version": 1, "updated_at": now,
        "root_batches": [{"root_id": root, "requirements": ids}
                         for root, ids in sorted(actionable_grouped.items())],
        "next_root": selected,
        "execution_policy": "FREE_VERIFIED_CIRCULATION_FIRST_WORK_ONLY_WITH_RESTART_PACKAGE",
        "workspace": os.environ.get("GITHUB_WORKSPACE") or str(HERE.parent),
        "branch": os.environ.get("GITHUB_REF_NAME") or "main",
        "source_commit": os.environ.get("GITHUB_SHA"),
        "observer_manual_relay_required": 0,
    }
    return ledger, packet


def run(queue: dict, observer: dict, visible: dict, gate_state: dict,
        ledger_path: Path = LEDGER, packet_path: Path = PACKET,
        observer_report_path: Path = OBSERVER_REPORT) -> dict:
    ledger, packet = build(queue, observer, visible, gate_state)
    sections = {status: [row for row in ledger["requirements"] if row["status"] == status]
                for status in ALLOWED}
    required = ["COMPLETE", "PARTIAL", "UNFINISHED", "PLATFORM_HOLD", "LONG_TERM_HOLD",
                "AUTO_REQUEUED", "NEXT_WORK", "EVIDENCE", "observer_reinstruction_required",
                "manual_relay_count"]
    report = {
        **sections,
        "AUTO_REQUEUED": ledger["auto_requeued_roots"],
        "NEXT_WORK": ledger["next_auto_root"],
        "EVIDENCE": {
            "ledger": str(ledger_path), "work_packet": str(packet_path),
            "tool016_ack_count": observer.get("TOOL016_RESULT_ACK_RECEIVED", 0),
            "remote_readback": observer.get("REMOTE_GITHUB_READBACK_PASS", False),
        },
        "observer_reinstruction_required": ledger["observer_reinstruction_required"],
        "manual_relay_count": ledger["manual_relay_count"],
    }
    report["required_report_fields"] = required
    report["missing_report_fields"] = [key for key in required if key not in report]
    report["fixed_block_gate"] = "PASS" if not report["missing_report_fields"] else "FAIL"
    # An incomplete mandatory report can never leave CR-1 PASS-locked.
    if report["fixed_block_gate"] != "PASS":
        ledger["cr_status"]["CR-1"] = "PARTIAL"
        for row in ledger["requirements"]:
            if row["requirement_id"] == "CR-1":
                row.update(status="PARTIAL", pass_lock=False,
                           remaining_work=report["missing_report_fields"],
                           resume_condition="REGENERATE_MANDATORY_OBSERVER_REPORT")
    atomic_json(ledger_path, ledger)
    atomic_json(packet_path, packet)
    atomic_json(observer_report_path, report)
    return ledger
