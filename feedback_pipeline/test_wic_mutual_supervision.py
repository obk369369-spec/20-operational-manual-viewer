from wic_mutual_supervision import evaluate


def base(stage="START", status="RUNNING"):
    return {
        "target_tool": "TOOL042",
        "stage": stage,
        "status": status,
        "safe_checkpoint_stage": "DIAGNOSE",
        "layer_health": {},
        "evidence": {},
    }

# 1. Start cannot pass without canonical inputs.
s = base("START")
r = evaluate(s)
assert r["decision"] == "STAGE_BLOCKED_REPAIR_AND_RESUME"
assert "master_loaded" in r["reason"]

# 2. False HOLD is rejected and resumes from checkpoint.
s = base("DIAGNOSE", "HOLD")
r = evaluate(s)
assert r["decision"] == "STOP_REJECTED_RESUME_REQUIRED"
assert r["next_stage"] == "DIAGNOSE"
assert r["user_action"] == "NONE"

# 3. Genuine external/user-only HOLD is allowed only after independent search/audit.
s = base("DIAGNOSE", "HOLD")
s["evidence"] = {
    "evidence_search_complete": True,
    "external_hold_confirmed": True,
    "user_only_action_confirmed": True,
}
s["queued_user_action"] = "APPROVE_EXTERNAL_LOGIN"
r = evaluate(s)
assert r["decision"] == "HOLD_EXTERNAL_CONFIRMED"
assert r["user_action"] == "APPROVE_EXTERNAL_LOGIN"

# 4. Test stage requires EXPECTED/ACTUAL/compare/regression.
s = base("TEST")
s["evidence"] = {"expected_defined": True, "actual_executed": True, "compare_match": True}
r = evaluate(s)
assert r["decision"] == "STAGE_BLOCKED_REPAIR_AND_RESUME"
assert "impacted_regression_pass" in r["reason"]

# 5. Unhealthy supervisor is recovered by independent peer; observer is not asked.
s = base("FIX")
s["layer_health"] = {"L3_CHANGE_GUARD": "FAIL", "L4_TEST_AUDIT": "OK"}
r = evaluate(s)
assert r["decision"] == "RECOVER_LAYER_AND_RESUME"
assert r["recovery_owner"] == "L4_TEST_AUDIT"
assert r["user_action"] == "NONE"

# 6. If both primary and peer fail, system restores canonical checkpoint, not user repair.
s = base("FIX")
s["layer_health"] = {"L3_CHANGE_GUARD": "FAIL", "L4_TEST_AUDIT": "FAIL"}
r = evaluate(s)
assert r["decision"] == "SYSTEM_RECOVERY_REQUIRED"
assert r["recovery_owner"] == "DETERMINISTIC_BOOTSTRAP"
assert r["user_action"] == "NONE"

# 7. COMPLETE without deployed-copy proof is rejected.
s = base("COMPLETE", "COMPLETE")
s["evidence"] = {k: True for k in (
    "master_loaded", "checkpoint_loaded", "actual_input_ready", "cause_grouped",
    "expected_defined", "actual_executed", "compare_match", "impacted_regression_pass",
    "git_push", "remote_readback", "actual_use_deploy", "safe_checkpoint_written",
)}
r = evaluate(s)
assert r["decision"] == "COMPLETE_REJECTED_RESUME_REQUIRED"
assert "deployed_copy_test" in r["reason"]

# 8. Full evidence reaches DEPLOYED_PASS.
s["evidence"]["deployed_copy_test"] = True
r = evaluate(s)
assert r["decision"] == "DEPLOYED_PASS"

print("8/8 PASS")
