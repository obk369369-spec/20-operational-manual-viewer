"""Registry-driven WIC feedback orchestration state machine.

Transport receipts are inputs: this module never claims commit/push/read-back from
an intention. It prepares evidence/work packets and advances only on verified gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
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


def resolve_event(registry: Mapping[str, Any], event: Mapping[str, Any]) -> tuple[str, Mapping[str, Any]]:
    try:
        return resolve(registry,str(event["source_chat"]),str(event.get("tool_id","")))
    except KeyError:
        if event.get("registration_mode") != "CENTRAL_LANE_PROVISIONAL": raise
        provisional_id=str(event.get("tool_id") or event["source_chat"])
        central=dict(registry["targets"][registry["defaults"]["provisional_registration_target"]])
        central.update({"chat_ids":[str(event["source_chat"])],"adapter":registry["defaults"]["provisional_registration_adapter"]})
        return provisional_id,central


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


def run_event(event: Mapping[str, Any], registry: Mapping[str, Any], receipts: Mapping[str, Any], *, fixture_mode: bool = False) -> dict[str, Any]:
    if not fixture_mode:
        raise RuntimeError("receipt injection is fixture-only; use execute_actual_transport for operation")
    state: dict[str, Any] = {"pipeline_id":stable_id(str(event.get("source_ref","")),str(event.get("feedback",""))),"stage":"CAPTURED","status":"RUNNING"}
    if event.get("event_kind") != "ACTUAL_USER":
        return fail(state,"CAPTURED","fixture/test events cannot increment actual recurrence",False,"ISOLATE_NON_ACTUAL_EVENT")
    state["stage"] = "NORMALIZED"
    try:
        target,row = resolve_event(registry,event)
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


def command(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True)
    if check and result.returncode:
        raise RuntimeError(f"command failed {args}: {result.stdout}\n{result.stderr}")
    return result


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    safe = str(cwd.resolve()).replace("\\", "/")
    return command(["git", "-c", f"safe.directory={safe}", *args], cwd, check=check)


def execute_test(cwd: Path, spec: list[str], bundled_python: str = "") -> dict[str, Any]:
    if spec[0] == "WIC_BUILTIN_REQUIRED_FILES":
        checked = []
        for name in spec[1:]:
            path = cwd / name
            if not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError(f"required test asset missing or empty: {name}")
            checked.append({"path":name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
        return {"adapter":spec[0],"status":"PASS","checked":checked}
    actual = list(spec)
    if actual[0] == "WIC_BUNDLED_PYTHON":
        if not bundled_python: raise RuntimeError("bundled python path required")
        actual[0] = bundled_python
    result = command(actual, cwd)
    return {"adapter":"COMMAND","command":spec,"status":"PASS","stdout":result.stdout[-4000:]}


def execute_actual_transport(event: Mapping[str, Any], registry: Mapping[str, Any], workspace: Path, *, bundled_python: str = "") -> dict[str, Any]:
    """Create evidence DIFF, test, commit, push and remote read-back from actual Git results."""
    validate_registry(registry)
    target,row = resolve_event(registry,event)
    state={"pipeline_id":stable_id(str(event["source_ref"]),str(event["feedback"])),"target":target,"repository":row["repository"],"stage":"TARGET_RESOLVED","status":"RUNNING"}
    evidence,work=build_packets(event,target,row); state.update({"evidence_packet":evidence,"work_packet":work})
    if not (evidence.get("actual_input_ref") and evidence.get("wrong_output_ref") and evidence.get("expected")):
        return fail(state,"EVIDENCE_READY","input/wrong-output/expected evidence references are incomplete",True,"CAPTURE_LINKED_EVIDENCE_FROM_SOURCE_CHAT")
    if git(workspace,"status","--porcelain").stdout.strip():
        return fail(state,"TARGET_APPLIED","target worktree is not clean",False,"PRESERVE_EXISTING_CHANGES_AND_USE_CLEAN_WORKTREE")
    receipt_rel=Path(".wic")/"pipeline_receipts"/f"{state['pipeline_id']}.json"
    receipt_path=workspace/receipt_rel
    resume_existing=False
    local_head=git(workspace,"rev-parse","HEAD").stdout.strip()
    reconcile_base=local_head
    remote_head=git(workspace,"ls-remote","origin",f"refs/heads/{row['branch']}").stdout.split("\t")[0]
    if local_head != remote_head:
        pre_recovery_head=local_head
        git(workspace,"fetch","origin",row["branch"])
        remote_head=git(workspace,"rev-parse","FETCH_HEAD").stdout.strip()
        ancestor=git(workspace,"merge-base","--is-ancestor",local_head,"FETCH_HEAD",check=False)
        if ancestor.returncode:
            if not receipt_path.is_file():
                return fail(state,"TARGET_APPLIED",f"divergent local/remote {local_head}/{remote_head}",False,"PRESERVE_BOTH_HISTORIES_FOR_RECONCILE")
            prior=json.loads(receipt_path.read_text(encoding="utf-8")); pre_recovery_head=str(prior["pre_apply_commit"])
            reconcile_base=pre_recovery_head
            if git(workspace,"merge-base","--is-ancestor",pre_recovery_head,"FETCH_HEAD",check=False).returncode:
                return fail(state,"TARGET_APPLIED","saved receipt base is not an ancestor of remote",False,"PRESERVE_BOTH_HISTORIES_FOR_RECONCILE")
            merged=git(workspace,"merge","--no-edit","FETCH_HEAD",check=False)
            if merged.returncode:
                git(workspace,"merge","--abort",check=False)
                return fail(state,"TARGET_APPLIED","saved transport reconcile conflict",False,"PRESERVE_LOCAL_COMMIT_FOR_RECONCILE")
            resume_existing=True
        else:
            git(workspace,"merge","--ff-only","FETCH_HEAD")
        local_head=git(workspace,"rev-parse","HEAD").stdout.strip()
        if not resume_existing and local_head != remote_head: raise RuntimeError("automatic fast-forward read-back mismatch")
        state["AUTO_RECOVERY_RECEIPT"]={"action":"FETCH_AND_FAST_FORWARD_ONLY","from":pre_recovery_head,"to":local_head,"user_action_required":False}
    if not resume_existing:
        receipt_path.parent.mkdir(parents=True,exist_ok=True)
        applied={"schema_version":1,"pipeline_id":state["pipeline_id"],"target":target,"source_ref":event["source_ref"],"root_cause_id":evidence["root_cause_id"],"adapter":row["adapter"],"pre_apply_commit":local_head,"mutation_scope":"PIPELINE_EVIDENCE_ONLY","customer_data_mutated":False}
        receipt_path.write_text(json.dumps(applied,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    state["stage"]="TARGET_APPLIED"; test_receipt=execute_test(workspace,list(row["test_command"]),bundled_python); state["stage"]="TESTED"
    if not resume_existing:
        git(workspace,"add","--",str(receipt_rel).replace("\\","/")); git(workspace,"commit","-m",f"wic: record actual pipeline transport for {target} [skip ci]")
    commit_sha=git(workspace,"rev-parse","HEAD").stdout.strip(); state["stage"]="COMMITTED"
    pushed=git(workspace,"push","origin",f"HEAD:{row['branch']}",check=False)
    if pushed.returncode:
        git(workspace,"fetch","origin",row["branch"])
        safe_reconcile=git(workspace,"merge-base","--is-ancestor",reconcile_base,"FETCH_HEAD",check=False)
        if safe_reconcile.returncode:
            return fail(state,"PUSHED","remote advanced from a non-ancestor base",False,"PRESERVE_LOCAL_COMMIT_FOR_RECONCILE")
        merged=git(workspace,"merge","--no-edit","FETCH_HEAD",check=False)
        if merged.returncode:
            git(workspace,"merge","--abort",check=False)
            return fail(state,"PUSHED","single safe reconcile produced conflicts",False,"PRESERVE_LOCAL_COMMIT_FOR_RECONCILE")
        test_receipt=execute_test(workspace,list(row["test_command"]),bundled_python)
        commit_sha=git(workspace,"rev-parse","HEAD").stdout.strip()
        state["REMOTE_RECONCILE_RECEIPT"]={"attempts":1,"mode":"NORMAL_MERGE_NO_FORCE","test_rerun":"PASS"}
        git(workspace,"push","origin",f"HEAD:{row['branch']}")
    state["stage"]="PUSHED"
    remote_sha=git(workspace,"ls-remote","origin",f"refs/heads/{row['branch']}").stdout.split("\t")[0]
    if remote_sha != commit_sha: raise RuntimeError(f"push read-back mismatch {commit_sha}/{remote_sha}")
    blob=git(workspace,"rev-parse",f"{commit_sha}:{str(receipt_rel).replace(chr(92),'/')}").stdout.strip()
    readback=git(workspace,"show",f"{commit_sha}:{str(receipt_rel).replace(chr(92),'/')}").stdout
    if json.loads(readback)["pipeline_id"] != state["pipeline_id"]: raise RuntimeError("remote file read-back mismatch")
    state.update({"stage":"REMOTE_VERIFIED","status":"TARGET_REMOTE_PASS","TARGET_APPLY_RECEIPT":str(receipt_rel).replace("\\","/"),"TEST_RECEIPT":test_receipt,"COMMIT_SHA":commit_sha,"PUSH_VERIFIED":True,"REMOTE_SHA":remote_sha,"REMOTE_FILE_READBACK":{"blob":blob,"verified":True}})
    return state


def self_test() -> dict[str, Any]:
    registry=json.loads(REGISTRY.read_text(encoding="utf-8")); validate_registry(registry)
    receipts={k:True for k in ("target_applied","central_applied","tested","committed","pushed","remote_verified","state_synced")}
    base={"event_kind":"ACTUAL_USER","source_ref":"CURRENT_CHAT#fixture","feedback":"실제 결과가 틀렸다. 수정해라.","actual_input_ref":"fixture/input","wrong_output_ref":"fixture/wrong","expected":"fixture/expected","recurrence":2}
    cases={}
    for target in ("TOOL006","TOOL041","TOOL042","TOOL007"):
        cases[target]=run_event({**base,"source_chat":target,"tool_id":target},registry,receipts,fixture_mode=True)
        assert cases[target]["status"]=="PASS"
    cases["FUTURE_CHAT"]=run_event({**base,"source_chat":"CHAT999","tool_id":"TOOL999","registration_mode":"CENTRAL_LANE_PROVISIONAL"},registry,receipts,fixture_mode=True)
    assert cases["FUTURE_CHAT"]["status"]=="PASS" and cases["FUTURE_CHAT"]["target"]=="TOOL999"
    missing=run_event({**base,"source_chat":"UNKNOWN"},registry,receipts,fixture_mode=True)
    assert missing["FAILED_STAGE"]=="TARGET_RESOLVED" and missing["USER_ACTION_REQUIRED"] is False
    incomplete=run_event({**base,"source_chat":"TOOL041","wrong_output_ref":""},registry,receipts,fixture_mode=True)
    assert incomplete["FAILED_STAGE"]=="EVIDENCE_READY" and incomplete["AUTO_RECOVERABLE"] is True
    return {"result":"PASS_INTERNAL_E2E","stage_order":STAGES,"cases":cases,"failure_cases":{"unregistered":missing,"evidence_incomplete":incomplete},"current_active_targets":sorted(registry["targets"]),"registration_holds":registry["registration_holds"]}


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--self-test",action="store_true"); parser.add_argument("--evidence",default="")
    parser.add_argument("--execute-event",default=""); parser.add_argument("--workspace",default=""); parser.add_argument("--bundled-python",default="")
    args=parser.parse_args()
    if args.self_test:
        result=self_test()
        if args.evidence: Path(args.evidence).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("PASS: registry-driven TOOL006/041/042/other/future-chat state-machine E2E")
    elif args.execute_event:
        registry=json.loads(REGISTRY.read_text(encoding="utf-8")); event=json.loads(Path(args.execute_event).read_text(encoding="utf-8"))
        result=execute_actual_transport(event,registry,Path(args.workspace),bundled_python=args.bundled_python)
        if args.evidence: Path(args.evidence).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__": main()
