import importlib.util
from pathlib import Path

module_path = Path(__file__).resolve().parents[1] / "CONTROL_TOWER" / "controller" / "runtime_progress_gate.py"
spec = importlib.util.spec_from_file_location("runtime_progress_gate", module_path)
runtime_progress_gate = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(runtime_progress_gate)
evaluate = runtime_progress_gate.evaluate
initial_state = runtime_progress_gate.initial_state

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

# The same gate now guards fresh handoffs against missing or stale canonical rules.
root = module_path.parents[2]
manifest = runtime_progress_gate.canonical_rule_manifest(root, "TOOL042")
assert not manifest["missing"], manifest
context = {**manifest, "source_records_verified": True, "conflicts": []}
registry = {"components": [{"id": "EXISTING", "status": "VERIFIED_REUSE"}]}
def handoff(trace_id, supplied):
    return runtime_progress_gate.accept_handoff(
        {}, {"handoff_inbox": []}, registry,
        {"trace_id": trace_id, "root_id": "RULE-LIFECYCLE", "task_id": "TOOL042",
         "input": {"source": "verified"}, "expected_output": "receipt",
         "rule_context": supplied}, initial_state())

assert handoff("missing", None)["reason"] == "RULE_CONTEXT_MISSING"
assert handoff("stale", {**context, "version": "old"})["reason"] == "RULE_CONTEXT_STALE_OR_TAMPERED"
assert handoff("conflict", {**context, "conflicts": ["unresolved"]})["reason"] == "RULE_CONFLICT_UNRESOLVED"
assert handoff("source", {**context, "source_records_verified": False})["reason"] == "REQUIRED_SOURCE_RECORDS_UNVERIFIED"
allowed = handoff("verified", context)
assert allowed["status"] == "ACCEPTED" and allowed["rule_gate_receipt"]["decision"] == "ALLOW", allowed
print({"rule_gate_negative_cases": 4, "verified_handoff": "ACCEPTED", "rule_version": manifest["version"]})
