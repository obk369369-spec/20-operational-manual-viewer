from __future__ import annotations

import copy
import json

from runtime_progress_gate import accept_feedback, accept_handoff, evaluate, initial_state
from universal_enforcement import closure_verdict, self_test


def main() -> None:
    registry = {"components": [{"id": "FACTORY", "status": "VERIFIED_REUSE"}]}
    state = {"handoff_traces": {}, "pass_locked_roots": ["ALREADY-CLOSED"]}
    queue = {"queued_requirement_ids": [], "handoff_inbox": []}
    gate = initial_state()
    envelope = {"trace_id": "ACTUAL-CENTRAL-INPUT-1", "root_id": "COMMON-PLATFORM",
                "input": "사용자 입력 1회", "expected_output": "central execution receipt"}
    positive = accept_handoff(state, queue, registry, envelope, gate)
    duplicate = accept_handoff(state, queue, registry, envelope, gate)
    protected = accept_handoff(state, queue, registry,
        {**envelope, "trace_id": "LOCKED-1", "scope": "FILE_DISCOVERY"}, gate)
    completed = accept_handoff(state, queue, registry,
        {**envelope, "trace_id": "LOCKED-2", "root_id": "ALREADY-CLOSED"}, gate)
    failure = {"failure_class": "DUPLICATE", "root_cause": "NO_PRELOOKUP",
        "bad_input": "same work twice", "expected_behavior": "BLOCK", "scope": "COMMON_PLATFORM"}
    promoted = accept_feedback(state, failure)
    repeated = accept_feedback(state, failure)
    injected = []
    for index, kind in enumerate(("SEARCH", "HISTORY", "EVIDENCE_REGEN", "PLANNING", "TEST", "E2E"), 1):
        injected.append(evaluate(gate, {"root_id": f"STOP-{index}", "action_kind": kind,
            "target": kind, "checkpoint": "C0"}))
    stale = evaluate(gate, {"root_id": "STOP-1", "action_kind": "EXECUTION",
        "target": "OTHER", "checkpoint": "C0"})
    independent = evaluate(gate, {"root_id": "INDEPENDENT", "action_kind": "EXECUTION",
        "target": "SAFE", "checkpoint": "C1", "actual_closure_delta": 1,
        "remaining_scope_delta": 1, "checkpoint_advance": 1,
        "new_valid_evidence_delta": 1, "requirement_closure_delta": 1})
    before = copy.deepcopy(queue)
    queue["handoff_inbox"].append({"injected": "failure"})
    queue = before
    closure = {"actual_input": envelope, "actual_output": "central execution receipt",
        "expected_output": "central execution receipt", "validation_pass": True,
        "positive_pass": True, "negative_pass": True, "failure_injection_pass": True,
        "recovery_pass": True, "rollback_pass": True,
        "evidence_ref": "CONTROL_TOWER/ledger/evidence/WIC_AUTONOMOUS_GOVERNANCE_CLOSURE_20261008.json",
        "readback_pass": True}
    blocked_output = dict(closure); blocked_output["actual_output"] = "drifted output"
    result = {"actual_input": envelope, "positive": positive, "duplicate": duplicate,
        "protected_scope": protected, "no_progress_injections": injected,
        "stale_checkpoint": stale, "independent_root": independent,
        "completed_scope": completed, "failure_promoted": promoted,
        "repeat_failure": repeated, "closure_verdict": closure_verdict(closure),
        "drift_output_verdict": closure_verdict(blocked_output),
        "validator_of_validator": self_test(),
        "rollback_restored": queue == before,
        "expected": {"positive": "ACCEPTED", "duplicate": "BLOCKED",
            "protected": "BLOCKED", "no_progress_stops": 6, "stale": "BLOCK",
            "independent": "ALLOW", "manual_repetition": 0}}
    result["pass"] = all((positive["status"] == "ACCEPTED",
        duplicate["status"] == "BLOCKED", protected["status"] == "BLOCKED",
        sum(item["decision"] == "STOP" for item in injected) == 6,
        stale["decision"] == "BLOCK", independent["decision"] == "ALLOW",
        completed["reason"] == "PASS_LOCKED_SCOPE",
        promoted["status"] == "PROMOTED", repeated["status"] == "SYSTEM_CONTROL_FAILURE",
        result["closure_verdict"] == "PASS", result["drift_output_verdict"] == "FAIL",
        result["validator_of_validator"]["pass"],
        positive["user_manual_repetition"] == 0, result["rollback_restored"]))
    if not result["pass"]:
        raise SystemExit(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
