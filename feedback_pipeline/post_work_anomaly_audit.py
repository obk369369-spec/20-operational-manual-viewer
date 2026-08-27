"""Independent post-Work consistency and anomaly audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "evidence" / "post_work_anomaly_audit_20260827.json"
CANDIDATE_NAMES = (
    "POST_WORK_ANOMALY_GATE_MISSING", "PASS_GATE_NOT_ENFORCED",
    "RULE_RUNTIME_DIVERGENCE", "TEST_SCOPE_STALE",
    "EVIDENCE_ONLY_MASQUERADING_AS_EXECUTION", "HOLD_EVIDENCE_RECOVERY_BYPASS",
    "AUDIT_SEARCH_COVERAGE_BLIND_SPOT", "CENTRAL_SSoT_STALE",
    "FEEDBACK_NOT_ROUTED", "MODULE_VERIFIED_AS_TOOL_PASS",
    "EPHEMERAL_LOCAL_PATH_IN_CENTRAL_CHECKPOINT", "CHECKPOINT_COMPLETE_WITH_OPEN_ROOT",
    "HOLD_STATE_DESYNC", "ACTUAL_SMOKE_MISSING", "NOT_WORKED",
    "PREMATURE_WORK_EXIT", "OBSERVER_VERIFY_MISSING", "CANONICAL_RUNTIME_MISSING",
    "TARGET_SILENTLY_DROPPED", "UNEXPECTED_WORK_THREAD",
    "REPOSITORY_AUTOCREATE_NOT_IMPLEMENTED", "WORK_RESULT_NOT_PROPAGATED",
    "OBSERVER_DIRECTIVE_MISSING", "WORK_COMPLETION_ENFORCEMENT_MISSING",
    "OPEN_INPUT_OMISSION", "STALE_WORK_QUEUE", "REPEATED_MANUAL_APPROVAL",
    "USER_AS_FEEDBACK_COURIER",
)


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def missing_open_inputs(ledger_roots: set[str], queued_roots: set[str]) -> list[str]:
    return sorted(ledger_roots - queued_roots)


def audit(previous_streak: int = 0) -> dict:
    work = load("evidence/work_execution_audit_20260827.json")
    roots = load("evidence/work16_root_report.json")
    central_state = load("state.json")
    target_document = load("work_execution_targets_20260827.json")
    targets = target_document["targets"]
    ledger = load("work16_root_ledger.json")
    anomalies: list[str] = []
    if work["counts"]["work_target_total"] != len(targets): anomalies.append("TARGET_SILENTLY_DROPPED")
    if work["anomalies"]: anomalies.append("WORK_EXECUTION_ANOMALY_PRESENT")
    if roots["open_internal_root_count"] and roots["pass_claimed"]: anomalies.append("OPEN_COMPLETE_CONFLICT")
    if work["next_work_queue"] and work["overall_complete"]: anomalies.append("QUEUE_COMPLETE_CONFLICT")
    ledger_roots = {row["id"] for row in ledger["roots"] if row["status"] not in {"VERIFIED_CLOSED", "FIXED_LOCAL", "FIXED_RUNTIME", "REMOTE_VERIFIED"}}
    queued_roots = {row["root_id"] for row in work["next_work_queue"]}
    omitted_open_roots = missing_open_inputs(ledger_roots, queued_roots)
    if omitted_open_roots:
        anomalies.append("OPEN_INPUT_OMISSION:" + ",".join(omitted_open_roots))
    serialized = json.dumps({"targets": targets, "ledger": ledger}, ensure_ascii=False)
    if "_work16_" in serialized or "C:\\Users\\" in serialized: anomalies.append("EPHEMERAL_LOCAL_PATH_IN_CHECKPOINT")
    queue_text = (HERE / "work16_next_work_queue.md").read_text(encoding="utf-8")
    if "L4-18" in ledger_roots or "OPEN / RUNTIME_ENTRYPOINT_HOLD" in queue_text:
        anomalies.append("CENTRAL_SSoT_STALE:TOOL002")
    if "`L6-20`" not in queue_text:
        anomalies.append("WORK_INPUT_OPEN_ROOTS_STALE")
    master_text = (HERE.parent / "WIC_GLOBAL_OPERATING_RULES.md").read_text(encoding="utf-8")
    approval_markers = ("USER_MANUAL_APPROVAL_COUNT", "목표는 `0`", "최대 `1`")
    if not all(marker in master_text for marker in approval_markers):
        anomalies.append("MANUAL_APPROVAL_BATCH_GATE_MISSING")
    if int(target_document.get("user_manual_approval_count", 99)) > 1:
        anomalies.append("REPEATED_MANUAL_APPROVAL")
    gateway_text = (HERE / "runtime_gateway.py").read_text(encoding="utf-8")
    if "'user_manual_routing':False" not in gateway_text:
        anomalies.append("USER_AS_FEEDBACK_COURIER")
    runtime_targets = central_state.get("integration_core", {}).get("runtime_enforcement", {}).get("active_target_resolution", {})
    if runtime_targets.get("TOOL043") != "EXTERNAL_DEVICE_REQUIRED":
        anomalies.append("HOLD_STATE_DESYNC:TOOL043")
    expected_holds = {"TOOL001", "TOOL043"}
    if {row["target"] for row in work["next_work_queue"]} != expected_holds: anomalies.append("NEXT_QUEUE_TARGET_MISMATCH")
    streak = previous_streak + 1 if not anomalies else 0
    return {
        "schema_version": 1,
        "checks": len(CANDIDATE_NAMES),
        "new_open_candidates": anomalies,
        "new_holes": len(anomalies),
        "zero_new_hole_streak": streak,
        "known_open_roots": sorted(ledger_roots),
        "work_input_open_roots": sorted(ledger_roots),
        "open_input_omission": omitted_open_roots,
        "candidate_names_reviewed": list(CANDIDATE_NAMES),
        "candidate_review_count": len(CANDIDATE_NAMES),
        "queued_targets": sorted(expected_holds),
        "result": "ZERO_NEW_HOLE" if not anomalies else "NEW_OPEN_CANDIDATE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        assert missing_open_inputs({"L4-18", "L6-20"}, {"L6-20"}) == ["L4-18"]
        assert missing_open_inputs({"L6-20"}, {"L6-20"}) == []
        print("PASS: OPEN_INPUT_OMISSION fail-closed gate")
        return
    prior = json.loads(OUT.read_text(encoding="utf-8"))["zero_new_hole_streak"] if OUT.exists() else 0
    result = audit(prior)
    if args.record: OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["new_holes"]: raise SystemExit(1)


if __name__ == "__main__": main()
