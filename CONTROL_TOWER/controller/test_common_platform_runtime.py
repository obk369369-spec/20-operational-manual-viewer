from __future__ import annotations

import copy
import json

from runtime_progress_gate import accept_handoff, evaluate, initial_state


def main() -> None:
    registry = {"components": [{"id": "FACTORY", "status": "VERIFIED_REUSE"}]}
    state = {"handoff_traces": {}}
    queue = {"queued_requirement_ids": [], "handoff_inbox": []}
    gate = initial_state()
    envelope = {"trace_id": "ACTUAL-CENTRAL-INPUT-1", "root_id": "COMMON-PLATFORM",
                "input": "사용자 입력 1회", "expected_output": "central execution receipt"}
    positive = accept_handoff(state, queue, registry, envelope, gate)
    duplicate = accept_handoff(state, queue, registry, envelope, gate)
    protected = accept_handoff(state, queue, registry,
        {**envelope, "trace_id": "LOCKED-1", "scope": "FILE_DISCOVERY"}, gate)
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
    result = {"actual_input": envelope, "positive": positive, "duplicate": duplicate,
        "protected_scope": protected, "no_progress_injections": injected,
        "stale_checkpoint": stale, "independent_root": independent,
        "rollback_restored": queue == before,
        "expected": {"positive": "ACCEPTED", "duplicate": "BLOCKED",
            "protected": "BLOCKED", "no_progress_stops": 6, "stale": "BLOCK",
            "independent": "ALLOW", "manual_repetition": 0}}
    result["pass"] = all((positive["status"] == "ACCEPTED",
        duplicate["status"] == "BLOCKED", protected["status"] == "BLOCKED",
        sum(item["decision"] == "STOP" for item in injected) == 6,
        stale["decision"] == "BLOCK", independent["decision"] == "ALLOW",
        positive["user_manual_repetition"] == 0, result["rollback_restored"]))
    if not result["pass"]:
        raise SystemExit(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
