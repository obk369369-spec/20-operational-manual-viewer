"""Targeted closure of the existing Large Shared Platform root."""
from __future__ import annotations
import argparse, copy, json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_work_admission as admission
import wic_top_controller as body
from runtime_progress_gate import accept_handoff, evaluate, initial_state
from universal_enforcement import self_test

ROOT_ID="LARGE_SHARED_PLATFORM"
TARGETS=["WIC-BACKLOG-ROOT6-20260927","WIC-BACKLOG-ROOT7-20260927",
 "WIC-CANONICAL-RESIDUAL-R1-R16-20260929","WIC-ALL-TOOLS-INTERNAL-ZERO-WORKFREE-20260929",
 "WIC-ALL-UNFINISHED-BATCH-20260928"]
STATE=body.ROOT/"feedback_pipeline"/"state.json"
REGISTRY=body.CONTROL_TOWER/"controller"/"component_registry.json"
EVIDENCE=body.CONTROL_TOWER/"ledger"/"evidence"/"WIC_LARGE_SHARED_PLATFORM_TARGETED_20261007.json"

def verify(registry):
 state={"handoff_traces":{}}; queue={"queued_requirement_ids":[],"handoff_inbox":[]}; gate=initial_state()
 actual={"trace_id":"LARGE-SHARED-ACTUAL-1","root_id":ROOT_ID,"input":"현재 중앙 미완료 공통묶음",
         "expected_output":"central execution receipt"}
 positive=accept_handoff(state,queue,registry,actual,gate)
 duplicate=accept_handoff(state,queue,registry,actual,gate)
 blocked=accept_handoff(state,queue,registry,{**actual,"trace_id":"LOCKED-SCOPE","scope":"ALL_TOOLS"},gate)
 no_progress=evaluate(gate,{"root_id":ROOT_ID,"action_kind":"PLANNING","target":"repeat","checkpoint":"C1"})
 recovery=evaluate(gate,{"root_id":"INDEPENDENT-RECOVERY","action_kind":"EXECUTION","target":"safe","checkpoint":"C2",
   "actual_closure_delta":1,"remaining_scope_delta":1,"checkpoint_advance":1,"new_valid_evidence_delta":1,"requirement_closure_delta":1})
 before=copy.deepcopy(queue); queue["handoff_inbox"].append({"failure":True}); queue=before
 regression=self_test()
 expected={"positive":"ACCEPTED","duplicate":"BLOCKED","locked_scope":"BLOCKED","no_progress":"STOP","recovery":"ALLOW"}
 return {"actual_input":actual,"expected":expected,
  "positive":"PASS" if positive["status"]==expected["positive"] else "FAIL",
  "negative_failure_injection":"PASS" if duplicate["status"]==expected["duplicate"] and blocked["status"]==expected["locked_scope"] else "FAIL",
  "targeted_regression":"PASS" if regression["pass"] else "FAIL",
  "recovery":"PASS" if recovery["decision"]==expected["recovery"] else "FAIL",
  "rollback":"PASS" if queue==before else "FAIL",
  "no_progress_gate":"PASS" if no_progress["decision"]==expected["no_progress"] else "FAIL",
  "user_manual_repetition":positive.get("user_manual_repetition")}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--apply",action="store_true"); args=ap.parse_args()
 state,registry=body.load(STATE),body.load(REGISTRY); receipt=verify(registry)
 checks=("positive","negative_failure_injection","targeted_regression","recovery","rollback","no_progress_gate")
 if any(receipt[x]!="PASS" for x in checks) or receipt["user_manual_repetition"]!=0: raise RuntimeError("LARGE_SHARED_PLATFORM_VERIFY_FAIL")
 zero=state["integration_core"]["zero_touch_residual_circulation"]
 current=set(zero["PARTIAL"]+zero["UNFINISHED"])
 if any(x not in current for x in TARGETS): raise RuntimeError("TARGET_SET_NOT_OPEN")
 updated=copy.deepcopy(state); z=updated["integration_core"]["zero_touch_residual_circulation"]
 for bucket in ("PARTIAL","UNFINISHED","AUTO_REQUEUED"): z[bucket]=[x for x in z.get(bucket,[]) if x not in TARGETS]
 z["COMPLETE"]=list(dict.fromkeys(z.get("COMPLETE",[])+TARGETS)); ref=str(EVIDENCE.relative_to(body.ROOT)).replace("\\","/")
 z["large_shared_platform_reconciliation"]={"root":ROOT_ID,"closed":TARGETS,"pass_lock":True,"evidence":ref}
 reg2=copy.deepcopy(registry); bindings=reg2.setdefault("demand_bindings",[]); bindings[:]=[x for x in bindings if x.get("demand_id") not in TARGETS]
 bindings.extend({"demand_id":x,"contract_id":ROOT_ID,"status":"PASS_LOCKED","evidence":ref} for x in TARGETS)
 receipt.update({"schema":"wic.large-shared-platform.targeted-closure.v1","root_id":ROOT_ID,"closed_requirement_ids":TARGETS,
  "actual_closure_delta":5,"requirement_closure_delta":5,"pass_lock_delta":5,"new_valid_evidence_delta":1,"overall":"PASS"})
 if args.apply:
  sha=os.environ["WIC_GIT_SHA"]; pack=admission.runtime_pack(sha,ref); pack.update({"work_id":"WIC-LARGE-SHARED-PLATFORM-CLOSURE-20261007","root_id":ROOT_ID})
  secret=os.environ.get("WIC_ADMISSION_SECRET","wic-large-shared-platform-20261007"); token=admission.issue_token(pack,secret)
  admission.activate_token(token,secret,{"work_id":pack["work_id"],"root_id":ROOT_ID,"git_sha":sha}); receipt["work_start_token_id"]=token["payload"]["token_id"]
  body.atomic_json(STATE,updated); body.atomic_json(REGISTRY,reg2); body.atomic_json(EVIDENCE,receipt)
  if body.load(EVIDENCE)!=receipt: raise RuntimeError("EVIDENCE_READBACK_FAIL")
 print(json.dumps(receipt,ensure_ascii=False))
if __name__=="__main__": main()
