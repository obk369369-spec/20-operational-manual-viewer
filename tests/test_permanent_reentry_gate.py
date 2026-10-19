from CONTROL_TOWER.controller.runtime_progress_gate import evaluate, initial_state

CASES = [
    ({"central_record_status": "PASS_LOCKED"}, "COMPLETED_WORK_REENTRY_BLOCKED"),
    ({"central_record_status": "FAILED", "same_method": True}, "FAILED_METHOD_REENTRY_BLOCKED"),
    ({"service_status": "DISCONTINUED"}, "DISCONTINUED_SERVICE_REENTRY_BLOCKED"),
    ({"central_record_status": "INVESTIGATED", "unchanged_since_verification": True}, "INVESTIGATED_CANDIDATE_REENTRY_BLOCKED"),
    ({"directive_status": "CANONICAL_VERIFIED", "unchanged_since_verification": True}, "VERIFIED_DIRECTIVE_RELOAD_BLOCKED"),
]

receipts = []
for index, (extra, expected) in enumerate(CASES, 1):
    action = {
        "root_id": f"REENTRY-GATE-{index}",
        "scope": "COMMON_PLATFORM",
        "action_kind": "EXECUTION",
        "target": "MUST_NOT_RUN",
        "checkpoint": "UNCHANGED",
        **extra,
    }
    receipt = evaluate(initial_state(), action)
    assert receipt["decision"] == "BLOCK", receipt
    assert receipt["reason"] == expected, receipt
    assert receipt["blocked_before_execution"] is True, receipt
    receipts.append(receipt)

fresh = evaluate(initial_state(), {
    "root_id": "REENTRY-GATE-FRESH",
    "scope": "COMMON_PLATFORM",
    "action_kind": "EXECUTION",
    "target": "NEW_EXTERNAL_PARALLEL_CONNECTION",
    "checkpoint": "NEW",
    "central_record_status": "NEW",
    "checkpoint_advance": 1,
})
assert fresh["decision"] == "ALLOW", fresh
print({"blocked_cases": len(receipts), "fresh_allowed": True, "receipts": receipts})
