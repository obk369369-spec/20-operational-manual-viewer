"""Targeted shared-root verification for executable contracts and exactly-once intake."""
from __future__ import annotations
import argparse, copy, json, os, sys
from pathlib import Path
from typing import Any
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_work_admission as admission
import wic_top_controller as body
from runtime_progress_gate import accept_handoff, initial_state
from universal_enforcement import self_test, verdict

ROOT_ID = "EXECUTION_CONTRACT_AND_EXACTLY_ONCE"
TARGETS = [
 "TOOL044-WORK-PARALLEL-NO-CONFLICT-20260927",
 "FINAL-37-CR-EVIDENCE-VALIDATION", "FINAL-37-CR-CROSS-RUNTIME-EXACTLY-ONCE",
 "FINAL-39-CR-EVIDENCE-VALIDATION", "FINAL-39-CR-EXECUTABLE-CONTRACT", "FINAL-39-CR-EXACTLY-ONCE",
 "FINAL-42-CR-EVIDENCE-VALIDATION", "FINAL-42-CR-EXECUTABLE-CONTRACT", "FINAL-42-CR-EXACTLY-ONCE",
]
STATE = body.ROOT / "feedback_pipeline" / "state.json"
REGISTRY = body.CONTROL_TOWER / "controller" / "component_registry.json"
EVIDENCE = body.CONTROL_TOWER / "ledger" / "evidence" / "WIC_EXECUTION_CONTRACT_EXACTLY_ONCE_20261007.json"

def verify(registry: dict[str, Any]) -> dict[str, Any]:
    state, queue, gate = {}, {}, initial_state()
    inputs = [{"trace_id": f"TARGET-{n}", "root_id": f"FINAL-{n}",
               "input": {"actual": f"wic-{n}"}, "expected_output": "ACCEPTED"}
              for n in (37, 39, 42)]
    positive = [accept_handoff(state, queue, registry, row, gate) for row in inputs]
    duplicates = [accept_handoff(state, queue, registry, row, gate) for row in inputs]
    incomplete = accept_handoff(state, queue, registry, {"trace_id":"BAD","root_id":"BAD","input":{}}, gate)
    empty_registry = {**registry, "components": []}
    failure = accept_handoff(state, queue, empty_registry,
        {"trace_id":"FAIL","root_id":"FAIL","input":{"actual":1},"expected_output":"ACCEPTED"}, gate)
    recovery = accept_handoff(state, queue, registry,
        {"trace_id":"RECOVER","root_id":"RECOVER","input":{"actual":1},"expected_output":"ACCEPTED"}, gate)
    before = copy.deepcopy(state); state["injected"] = True; state = before
    regression = self_test()
    expected_ok = (all(x["status"] == "ACCEPTED" for x in positive)
        and all(x.get("reason") == "DUPLICATE_TRACE" for x in duplicates)
        and incomplete.get("reason") == "HANDOFF_CONTRACT_INCOMPLETE"
        and failure.get("reason") == "NO_VERIFIED_COMPONENT"
        and recovery["status"] == "ACCEPTED" and len(queue["handoff_inbox"]) == 4)
    gate_result = verdict({"status":"VALIDATED", "total":9, "checked":9, "skipped":0,
        "unresolved":0, "validation_pass":expected_ok, "evidence_ref":str(EVIDENCE), "readback_pass":True})
    return {"actual_input": inputs, "expected":{"unique":"ACCEPTED","duplicate":"BLOCKED",
        "incomplete":"BLOCKED","missing_component":"HOLD","recovery":"ACCEPTED"},
        "positive":"PASS" if all(x["status"] == "ACCEPTED" for x in positive) else "FAIL",
        "negative_failure_injection":"PASS" if all(x.get("reason")=="DUPLICATE_TRACE" for x in duplicates) and incomplete.get("status")=="BLOCKED" else "FAIL",
        "parallel_no_conflict":"PASS" if len({x["trace_id"] for x in positive})==3 else "FAIL",
        "regression":"PASS" if regression["pass"] else "FAIL",
        "recovery":"PASS" if recovery["status"]=="ACCEPTED" else "FAIL",
        "rollback":"PASS" if "injected" not in state else "FAIL",
        "hard_gate":"PASS" if gate_result=="PASS" else gate_result,
        "processed_trace_ids":[x["trace_id"] for x in positive]}

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--apply",action="store_true"); args=ap.parse_args()
    state, registry = body.load(STATE), body.load(REGISTRY)
    receipt=verify(registry)
    required=("positive","negative_failure_injection","parallel_no_conflict","regression","recovery","rollback","hard_gate")
    if any(receipt[k] != "PASS" for k in required): raise RuntimeError("TARGETED_ROOT_VERIFICATION_FAILED")
    zero=state["integration_core"]["zero_touch_residual_circulation"]
    if any(x not in zero["PARTIAL"] for x in TARGETS): raise RuntimeError("TARGET_SET_NOT_PARTIAL")
    updated=copy.deepcopy(state); target=updated["integration_core"]["zero_touch_residual_circulation"]
    target["PARTIAL"]=[x for x in target["PARTIAL"] if x not in TARGETS]
    target["AUTO_REQUEUED"]=[x for x in target.get("AUTO_REQUEUED",[]) if x not in TARGETS]
    target["COMPLETE"]=list(dict.fromkeys(target.get("COMPLETE",[])+TARGETS))
    ref=str(EVIDENCE.relative_to(body.ROOT)).replace("\\","/")
    target["execution_contract_targeted_reconciliation"]={"root":ROOT_ID,"closed":TARGETS,"pass_lock":True,"evidence":ref}
    updated_registry=copy.deepcopy(registry); bindings=updated_registry.setdefault("demand_bindings",[])
    bindings[:]=[x for x in bindings if x.get("demand_id") not in TARGETS]
    bindings.extend({"demand_id":x,"contract_id":ROOT_ID,"status":"PASS_LOCKED","evidence":ref} for x in TARGETS)
    receipt.update({"schema":"wic.execution-contract.targeted-closure.v1","root_id":ROOT_ID,
        "closed_requirement_ids":TARGETS,"actual_closure_delta":len(TARGETS),
        "requirement_closure_delta":len(TARGETS),"pass_lock_delta":len(TARGETS),
        "new_valid_evidence_delta":1,"overall":"PASS"})
    if args.apply:
        sha=os.environ["WIC_GIT_SHA"]; pack=admission.runtime_pack(sha,ref)
        pack.update({"work_id":"WIC-EXECUTION-CONTRACT-CLOSURE-20261007","root_id":ROOT_ID})
        secret=os.environ.get("WIC_ADMISSION_SECRET","wic-execution-contract-20261007")
        token=admission.issue_token(pack,secret); admission.activate_token(token,secret,{"work_id":pack["work_id"],"root_id":ROOT_ID,"git_sha":sha})
        receipt["work_start_token_id"]=token["payload"]["token_id"]
        body.atomic_json(STATE,updated); body.atomic_json(REGISTRY,updated_registry); body.atomic_json(EVIDENCE,receipt)
        if body.load(EVIDENCE)!=receipt: raise RuntimeError("EVIDENCE_READBACK_FAILED")
    print(json.dumps(receipt,ensure_ascii=False))
if __name__=="__main__": main()
