"""Registry-driven WIC feedback orchestration state machine.

Transport receipts are inputs: this module never claims commit/push/read-back from
an intention. It prepares evidence/work packets and advances only on verified gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "wic_target_registry.json"
STAGES = [
    "CAPTURED","NORMALIZED","TARGET_RESOLVED","EVIDENCE_READY","ROOT_CLASSIFIED",
    "WORK_READY","TARGET_APPLIED","CENTRAL_APPLIED","TESTED","COMMITTED","PUSHED",
    "REMOTE_VERIFIED","STATE_SYNCED","COMPLETE",
]
REQUIRED_TARGET_FIELDS = {
    "chat_ids","repository","branch","master_paths","state_path","evidence_path",
    "test_command","latest_safe_checkpoint","latest_verified_commit","adapter","status",
}


def stable_id(*parts: str) -> str:
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()[:20]


def validate_registry(registry: Mapping[str, Any]) -> None:
    assert registry.get("schema_version") == 1
    seen: dict[str, str] = {}
    for target, row in registry.get("targets", {}).items():
        missing = REQUIRED_TARGET_FIELDS - set(row)
        assert not missing, f"{target} missing {sorted(missing)}"
        assert row["status"] == "ACTIVE"
        for chat_id in row["chat_ids"]:
            assert chat_id not in seen, f"duplicate chat id {chat_id}"
            seen[chat_id] = target


def resolve(registry: Mapping[str, Any], chat_id: str, tool_id: str = "") -> tuple[str, Mapping[str, Any]]:
    wanted = tool_id or chat_id
    for target, row in registry["targets"].items():
        if wanted == target or wanted in row["chat_ids"]:
            return target, row
    raise KeyError(f"REGISTRY_INCOMPLETE:{wanted}")


def fail(state: dict[str, Any], stage: str, reason: str, recoverable: bool, action: str) -> dict[str, Any]:
    state.update({
        "status":"HOLD" if recoverable else "FAIL", "FAILED_STAGE":stage,
        "FAIL_REASON":reason, "LAST_VERIFIED_STAGE":state.get("stage", "NONE"),
        "AUTO_RECOVERABLE":recoverable, "NEXT_AUTOMATIC_ACTION":action,
        "USER_ACTION_REQUIRED":False,
    })
    return state


def build_packets(event: Mapping[str, Any], target: str, row: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    root = str(event.get("root_cause_id") or stable_id(target, str(event["feedback"])))
    evidence = {
        "source_chat":event["source_chat"], "source_ref":event["source_ref"],
        "actual_user_feedback":event["feedback"], "actual_input_ref":event.get("actual_input_ref"),
        "wrong_output_ref":event.get("wrong_output_ref"), "expected":event.get("expected"),
        "root_cause_id":root, "recurrence":max(1,int(event.get("recurrence",1))),
        "severity":event.get("severity","MEDIUM"), "customer_impact":event.get("customer_impact","OPERATIONAL"),
        "target":target, "repository":row["repository"], "master_paths":row["master_paths"],
        "existing_pass":event.get("existing_pass",[]), "pii_persisted":False,
    }
    work = {
        "target":target,"root_cause_id":root,"evidence":evidence,"repository":row["repository"],
        "branch":row["branch"],"master_paths":row["master_paths"],"state_path":row["state_path"],
        "test_command":row["test_command"],"adapter":row["adapter"],
        "safe_checkpoint":row["latest_safe_checkpoint"],"scope":"DIFF_ONLY",
        "forbidden":["force push","history rewrite","unrelated rescan"],
        "completion_gate":["TARGET_APPLIED","CENTRAL_APPLIED","TESTED","COMMITTED","PUSHED","REMOTE_VERIFIED","STATE_SYNCED"],
    }
    return evidence, work


def run_event(event: Mapping[str, Any], registry: Mapping[str, Any], receipts: Mapping[str, Any]) -> dict[str, Any]:
    state: dict[str, Any] = {"pipeline_id":stable_id(str(event.get("source_ref","")),str(event.get("feedback",""))),"stage":"CAPTURED","status":"RUNNING"}
    if event.get("event_kind") != "ACTUAL_USER":
        return fail(state,"CAPTURED","fixture/test events cannot increment actual recurrence",False,"ISOLATE_NON_ACTUAL_EVENT")
    state["stage"] = "NORMALIZED"
    try:
        target,row = resolve(registry,str(event["source_chat"]),str(event.get("tool_id","")))
    except KeyError as exc:
        return fail(state,"TARGET_RESOLVED",str(exc),True,"COMPLETE_REGISTRY_ENTRY_AND_RESUME")
    state.update({"stage":"TARGET_RESOLVED","target":target,"repository":row["repository"]})
    evidence,work = build_packets(event,target,row)
    state.update({"stage":"ROOT_CLASSIFIED","evidence_packet":evidence,"work_packet":work})
    evidence_ready = bool(evidence.get("actual_input_ref") and evidence.get("wrong_output_ref") and evidence.get("expected"))
    if not evidence_ready:
        return fail(state,"EVIDENCE_READY","input/wrong-output/expected evidence references are incomplete",True,"CAPTURE_LINKED_EVIDENCE_FROM_SOURCE_CHAT")
    state["stage"] = "WORK_READY"
    for stage,key in (("TARGET_APPLIED","target_applied"),("CENTRAL_APPLIED","central_applied"),("TESTED","tested"),("COMMITTED","committed"),("PUSHED","pushed"),("REMOTE_VERIFIED","remote_verified"),("STATE_SYNCED","state_synced")):
        if not receipts.get(key):
            return fail(state,stage,f"missing verified receipt: {key}",True,f"EXECUTE_{stage}_AND_RESUME")
        state["stage"] = stage
    state.update({"stage":"COMPLETE","status":"PASS","FAILED_STAGE":None,"USER_ACTION_REQUIRED":False})
    return state


def self_test() -> dict[str, Any]:
    registry=json.loads(REGISTRY.read_text(encoding="utf-8")); validate_registry(registry)
    receipts={k:True for k in ("target_applied","central_applied","tested","committed","pushed","remote_verified","state_synced")}
    base={"event_kind":"ACTUAL_USER","source_ref":"CURRENT_CHAT#fixture","feedback":"실제 결과가 틀렸다. 수정해라.","actual_input_ref":"fixture/input","wrong_output_ref":"fixture/wrong","expected":"fixture/expected","recurrence":2}
    cases={}
    for target in ("TOOL006","TOOL041","TOOL042","TOOL007"):
        cases[target]=run_event({**base,"source_chat":target,"tool_id":target},registry,receipts)
        assert cases[target]["status"]=="PASS"
    future=json.loads(json.dumps(registry)); future["targets"]["TOOL999"]={"chat_ids":["CHAT999"],"repository":"owner/future","branch":"main","master_paths":["MASTER.md"],"state_path":"state.json","evidence_path":"evidence","test_command":"run subset","latest_safe_checkpoint":"seed","latest_verified_commit":"seed","adapter":"REPOSITORY_DIFF_ONLY","status":"ACTIVE"}
    validate_registry(future)
    cases["FUTURE_CHAT"]=run_event({**base,"source_chat":"CHAT999"},future,receipts)
    assert cases["FUTURE_CHAT"]["status"]=="PASS" and cases["FUTURE_CHAT"]["target"]=="TOOL999"
    missing=run_event({**base,"source_chat":"UNKNOWN"},registry,receipts)
    assert missing["FAILED_STAGE"]=="TARGET_RESOLVED" and missing["USER_ACTION_REQUIRED"] is False
    incomplete=run_event({**base,"source_chat":"TOOL041","wrong_output_ref":""},registry,receipts)
    assert incomplete["FAILED_STAGE"]=="EVIDENCE_READY" and incomplete["AUTO_RECOVERABLE"] is True
    return {"result":"PASS_INTERNAL_E2E","stage_order":STAGES,"cases":cases,"failure_cases":{"unregistered":missing,"evidence_incomplete":incomplete},"current_active_targets":sorted(registry["targets"]),"registration_holds":registry["registration_holds"]}


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--self-test",action="store_true"); parser.add_argument("--evidence",default="")
    args=parser.parse_args()
    if args.self_test:
        result=self_test()
        if args.evidence: Path(args.evidence).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("PASS: registry-driven TOOL006/041/042/other/future-chat state-machine E2E")


if __name__=="__main__": main()
