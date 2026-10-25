import importlib.util
import hashlib
import json
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

tool013_manifest = runtime_progress_gate.canonical_rule_manifest(root, "TOOL013")
assert not tool013_manifest["missing"], tool013_manifest
assert any(key.startswith("obk369369-spec/13-excel-upload@9212abf64")
           and key.endswith(":TOOL013_MASTER.md") for key in tool013_manifest["files"])
assert any(key.endswith(":WIC_RULE_SOURCE.md") for key in tool013_manifest["files"])
golden = root / "feedback_pipeline" / "evidence" / ".tool013_human_golden_fixture.xlsx"
source_receipt = root / "feedback_pipeline" / "evidence" / ".tool013_source_receipt.json"
try:
    golden.write_bytes(b"human-authored-golden-fixture")
    golden_ref = {"path": str(golden.relative_to(root)).replace("\\", "/"),
                  "sha256": hashlib.sha256(golden.read_bytes()).hexdigest()}
    evidence = {
        "work_id": "T13-GATE", "task_id": "TOOL013", "source_records_verified": True,
        "validation_result": "PASS", "validator_id": "independent-fixture-validator",
        "rule_version": tool013_manifest["version"], "source_refs": [golden_ref],
        "validation_plan": {"method": "field-by-field", "expected_result": "18-column-xlsx",
                            "evidence_required": "reopen-and-diff"},
        "golden_provenance": {**golden_ref, "author_type": "MODEL_GENERATED"},
    }
    source_receipt.write_text(json.dumps(evidence), encoding="utf-8")
    source_ref = {"path": str(source_receipt.relative_to(root)).replace("\\", "/"),
                  "sha256": hashlib.sha256(source_receipt.read_bytes()).hexdigest()}
    admission = {"work_id": "T13-GATE", "task_id": "TOOL013",
                 "rule_context": {**tool013_manifest, "source_records_verified": True, "conflicts": []},
                 "source_receipt": source_ref}
    blocked = runtime_progress_gate.verify_work_admission(
        admission, repo_root=root, work_id="T13-GATE", task_id="TOOL013")
    assert blocked["reason"] == "TOOL013_HUMAN_GOLDEN_PROVENANCE_UNVERIFIED", blocked
    evidence["golden_provenance"]["author_type"] = "HUMAN_USER"
    source_receipt.write_text(json.dumps(evidence), encoding="utf-8")
    admission["source_receipt"]["sha256"] = hashlib.sha256(source_receipt.read_bytes()).hexdigest()
    assert runtime_progress_gate.verify_work_admission(
        admission, repo_root=root, work_id="T13-GATE", task_id="TOOL013")["decision"] == "ALLOW"
finally:
    source_receipt.unlink(missing_ok=True)
    golden.unlink(missing_ok=True)
allowed = handoff("verified", context)
assert allowed["status"] == "ACCEPTED" and allowed["rule_gate_receipt"]["decision"] == "ALLOW", allowed
print({"rule_gate_negative_cases": 4, "verified_handoff": "ACCEPTED", "rule_version": manifest["version"]})

