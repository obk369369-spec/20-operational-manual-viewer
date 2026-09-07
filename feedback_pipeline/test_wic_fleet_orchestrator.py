from wic_fleet_orchestrator import orchestrate


FINAL_KEYS = (
    "master_loaded", "checkpoint_loaded", "actual_input_ready", "cause_grouped",
    "expected_defined", "actual_executed", "compare_match", "impacted_regression_pass",
    "git_push", "remote_readback", "actual_use_deploy", "deployed_copy_test",
    "safe_checkpoint_written",
)


def lane(tool, operation, lock):
    return {"target_tool": tool, "operation_id": operation, "lock_key": lock}


manifest = {
    "max_workers": 4,
    "lanes": [
        {**lane("TOOL013", "reuse-idb-and-bulk", "repo13"),
         "existing_deployed_pass": True, "change_detected": False},
        {**lane("TOOL044", "reuse-fast-deploy", "central"),
         "existing_deployed_pass": True, "change_detected": False},
        {**lane("ORCHESTRATOR_CANARY", "changed-complete", "canary-a"),
         "change_detected": True, "impact_known": True, "stage": "COMPLETE",
         "status": "COMPLETE", "layer_health": {},
         "evidence": {key: True for key in FINAL_KEYS}},
        {**lane("ORCHESTRATOR_CANARY", "unknown-impact", "canary-b"),
         "change_detected": True, "impact_known": False,
         "safe_checkpoint_stage": "DIAGNOSE"},
        {**lane("ORCHESTRATOR_CANARY", "safe-recovery", "canary-c"),
         "change_detected": True, "impact_known": True, "status": "FAIL",
         "safe_auto_recovery": True, "safe_checkpoint_stage": "TEST",
         "failure_method_id": "method-b", "previous_failure_method_id": "method-a"},
        {**lane("ORCHESTRATOR_CANARY", "repeat-block", "canary-d"),
         "change_detected": True, "impact_known": True, "status": "FAIL",
         "safe_auto_recovery": True, "safe_checkpoint_stage": "TEST",
         "failure_method_id": "same", "previous_failure_method_id": "same"},
    ],
}

result = orchestrate(manifest)
assert result["status"] == "PASS"
assert result["parallel_lock_groups"] == 6
assert result["user_action_queue"] == []
assert result["execution_policy"]["arbitrary_manifest_commands"] is False
decisions = {(r["target_tool"], r["operation_id"]): r["decision"] for r in result["results"]}
assert decisions[("TOOL013", "reuse-idb-and-bulk")] == "SKIP_REUSE"
assert decisions[("TOOL044", "reuse-fast-deploy")] == "SKIP_REUSE"
assert decisions[("ORCHESTRATOR_CANARY", "changed-complete")] == "DEPLOYED_PASS"
assert decisions[("ORCHESTRATOR_CANARY", "unknown-impact")] == "HOLD_IMPACT_UNKNOWN"
assert decisions[("ORCHESTRATOR_CANARY", "safe-recovery")] == "FAIL_ISOLATED_RECOVERY_READY"
assert decisions[("ORCHESTRATOR_CANARY", "repeat-block")] == "REPEAT_FAILURE_ISOLATED"
print("6/6 PASS")
