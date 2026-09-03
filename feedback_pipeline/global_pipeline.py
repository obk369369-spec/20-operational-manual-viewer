"""Registry-driven WIC feedback orchestration state machine.

Transport receipts are inputs: this module never claims commit/push/read-back from
an intention. It prepares evidence/work packets and advances only on verified gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "wic_target_registry.json"
ROUTE_REGISTRY = ROOT.parent / "WIC_CHAT_ROUTING_REGISTRY.md"
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


def validate_registry(registry: Mapping[str, Any], *, target: str | None = None) -> None:
    if registry.get("schema_version") != 1: raise ValueError("unsupported registry schema")
    seen: dict[str, str] = {}
    rows = registry.get('targets', {})
    selected = {target: rows[target]} if target is not None else rows
    for target_id, row in selected.items():
        missing = REQUIRED_TARGET_FIELDS - set(row)
        if missing: raise ValueError(f"{target_id} missing {sorted(missing)}")
        if row['status'] == 'COMPLETE':
            proof = row.get('first_validation', {})
            if (proof.get('status') != 'PASS' or not proof.get('run_id')
                    or not row.get('latest_verified_commit')
                    or row['latest_verified_commit'] != row.get('latest_safe_checkpoint')):
                raise ValueError(f'{target_id} COMPLETE lacks verified checkpoint evidence')
        elif row['status'] not in {'ACTIVE', 'STAGING_REMOTE_VERIFIED'}:
            raise ValueError(f'{target_id} unsupported registry status')
        for chat_id in row["chat_ids"]:
            if chat_id in seen: raise ValueError(f"duplicate chat id {chat_id}")
            seen[chat_id] = target_id
    if target is not None:
        return  # Selected transport validates only its resolved target, not all WIC.
    route_targets = {
        line.split("=", 1)[0].removeprefix("route:").strip()
        for line in ROUTE_REGISTRY.read_text(encoding="utf-8").splitlines()
        if line.startswith("route:") and "=" in line
    }
    uncovered = sorted(route_targets - set(registry.get("targets", {})) - set(seen))
    if uncovered: raise ValueError(f"routing registry target(s) lack canonical coverage: {uncovered}")


def _loaded_file_receipt(phase: str, repository: str, revision: str, path: Path, relative_path: str) -> dict[str, Any]:
    raw = path.read_bytes()
    if not raw:
        raise RuntimeError(f"MASTER_LOAD_FAIL: empty {phase} {relative_path}")
    return {"phase":phase,"repository":repository,"path":relative_path,"revision":revision,"sha256":hashlib.sha256(raw).hexdigest(),"read_back":True}


def load_master_context(registry: Mapping[str, Any], event: Mapping[str, Any], workspace: Path, *, central_root: Path | None = None) -> dict[str, Any]:
    """Fail-closed WIC entry gate: CENTRAL -> TOOL master -> checkpoint/handoff."""
    gate = registry.get("master_load_gate", {})
    central = gate.get("central_master", {})
    root = central_root or ROOT.parent
    loaded: list[dict[str, Any]] = []
    try:
        central_rel = str(central.get("path") or "WIC_GLOBAL_OPERATING_RULES.md")
        loaded.append(_loaded_file_receipt("CENTRAL_COMMON_MASTER",str(central.get("repository") or registry["targets"]["CENTRAL"]["repository"]),str(central.get("branch") or "main"),root/central_rel,central_rel))
    except (OSError, RuntimeError, KeyError) as exc:
        return {"status":"HOLD","reason":"MASTER_LOAD_FAIL","detail":str(exc),"loaded":loaded,"work_entry_allowed":False}
    try:
        target, row = resolve(registry,str(event.get("source_chat","")),str(event.get("tool_id","")))
    except KeyError:
        return {"status":"HOLD","reason":"TOOL_MASTER_NOT_FOUND","loaded":loaded,"work_entry_allowed":False}
    if row.get("status") != "ACTIVE":
        return {"status":"HOLD","reason":"TARGET_NOT_ACTIVE","target":target,"loaded":loaded,"work_entry_allowed":False}
    revision = str(row.get("latest_safe_checkpoint") or row.get("latest_verified_commit") or "")
    try:
        for rel in row["master_paths"]:
            loaded.append(_loaded_file_receipt("TOOL_CANONICAL_MASTER",str(row["repository"]),revision,workspace/rel,str(rel)))
        checkpoint = str(row["state_path"])
        loaded.append(_loaded_file_receipt("LATEST_CHECKPOINT_HANDOFF",str(row["repository"]),revision,workspace/checkpoint,checkpoint))
    except (OSError, RuntimeError, KeyError) as exc:
        return {"status":"HOLD","reason":"MASTER_LOAD_FAIL","target":target,"detail":str(exc),"loaded":loaded,"work_entry_allowed":False}
    phases=[item["phase"] for item in loaded]
    expected=["CENTRAL_COMMON_MASTER",*(["TOOL_CANONICAL_MASTER"]*len(row["master_paths"])), "LATEST_CHECKPOINT_HANDOFF"]
    if phases != expected:
        return {"status":"HOLD","reason":"MASTER_LOAD_ORDER_INVALID","target":target,"loaded":loaded,"work_entry_allowed":False}
    return {"status":"PASS","target":target,"load_order":["CENTRAL_COMMON_MASTER","TOOL_CANONICAL_MASTER","LATEST_CHECKPOINT_HANDOFF"],"loaded":loaded,"work_entry_allowed":True}


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


def recover_evidence(event: Mapping[str, Any]) -> dict[str, Any]:
    """Recover linked evidence from the source-chat envelope without inventing facts."""
    recovered = dict(event)
    context = event.get("source_context") if isinstance(event.get("source_context"), Mapping) else {}
    recovered["actual_input_ref"] = event.get("actual_input_ref") or context.get("actual_input_ref") or context.get("current_input_ref") or event.get("source_ref")
    recovered["wrong_output_ref"] = event.get("wrong_output_ref") or context.get("wrong_output_ref") or context.get("previous_output_ref")
    recovered["expected"] = event.get("expected") or context.get("expected") or context.get("user_correction") or event.get("user_correction")
    recovered["evidence_recovered_from_source_context"] = any(not event.get(k) and recovered.get(k) for k in ("actual_input_ref", "wrong_output_ref", "expected"))
    return recovered


def build_packets(event: Mapping[str, Any], target: str, row: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    event = recover_evidence(event)
    root = str(event.get("root_cause_id") or stable_id(target, str(event["feedback"])))
    evidence = {
        "source_chat":event["source_chat"], "source_ref":event["source_ref"],
        "actual_user_feedback":event["feedback"], "actual_input_ref":event.get("actual_input_ref"),
        "wrong_output_ref":event.get("wrong_output_ref"), "expected":event.get("expected"),
        "root_cause_id":root, "recurrence":max(1,int(event.get("recurrence",1))),
        "severity":event.get("severity","MEDIUM"), "customer_impact":event.get("customer_impact","OPERATIONAL"),
        "target":target, "repository":row["repository"], "master_paths":row["master_paths"],
        "existing_pass":event.get("existing_pass",[]), "pii_persisted":False,
        "evidence_recovered_from_source_context":event.get("evidence_recovered_from_source_context",False),
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
    result = subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=900)
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


def verify_material_change(event: Mapping[str, Any], workspace: Path, head: str, registry:Mapping[str,Any]|None=None, row:Mapping[str,Any]|None=None, bundled_python:str="") -> dict[str, Any]:
    """Block receipt-only completion; verify a real fix commit or a hashed no-diff decision."""
    decision=str(event.get("material_decision", ""))
    if decision in {"TARGET_DIFF_APPLIED", "CENTRAL_DIFF_APPLIED"}:
        if str(event.get("fix_commit", "")) != head:
            raise RuntimeError("fix_commit must equal current verified HEAD")
        changed=git(workspace,"diff-tree","--no-commit-id","--name-only","-r",head).stdout.splitlines()
        material=[p for p in changed if p and not p.startswith(".wic/pipeline_receipts/") and not p.startswith("feedback_pipeline/evidence/")]
        if not material: raise RuntimeError("RECEIPT_ONLY_FALSE_COMPLETE_BLOCKED: no material target/central diff")
        return {"decision":decision,"fix_commit":head,"material_files":material}
    if decision == "NO_TARGET_DIFF_REQUIRED":
        proof=event.get("no_diff_proof")
        if not isinstance(proof,dict) or proof.get("master_revision") != head or registry is None or row is None:
            raise RuntimeError("verified NO_TARGET_DIFF_REQUIRED proof is incomplete")
        required=list(dict.fromkeys((registry.get("runtime_overrides",{}).get(str(event.get("tool_id") or event.get("source_chat")),{}).get("required_assets") or [*row["master_paths"],row["state_path"]])))
        hashes={name:hashlib.sha256((workspace/name).read_bytes()).hexdigest() for name in required if (workspace/name).is_file() and (workspace/name).stat().st_size}
        if len(hashes)!=len(required): raise RuntimeError("NO_TARGET_DIFF_REQUIRED required asset missing")
        override=registry.get("runtime_overrides",{}).get(str(event.get("tool_id") or event.get("source_chat")),{})
        validator=execute_test(workspace,list(override.get("validator") or row["test_command"]),bundled_python)
        output_gate=execute_test(workspace,list(override.get("output_gate") or row["test_command"]),bundled_python)
        return {"decision":decision,"master_revision":head,"asset_hashes":hashes,"validator_receipt":validator,"output_gate_receipt":output_gate}
    raise RuntimeError("material_decision required before transport")


def canonical_execution_audit() -> dict[str, Any]:
    legacy=("apply_feedback_event.py","cross_chat_feedback_ingest.py","target_dispatcher.py")
    executable=[]
    for name in legacy:
        text=(ROOT/name).read_text(encoding="utf-8")
        if '__name__ == "__main__"' in text: executable.append(name)
    workflow_text="\n".join(p.read_text(encoding="utf-8") for p in (ROOT.parent/".github"/"workflows").glob("*.yml"))
    invoked=[name for name in legacy if f"python feedback_pipeline/{name}" in workflow_text]
    return {"ACTIVE_EXECUTABLE_PIPELINE_COUNT":1,"CANONICAL_PIPELINE":"feedback_pipeline/global_pipeline.py","LEGACY_EXECUTABLE_ENTRYPOINTS":executable,"LEGACY_WORKFLOW_ROUTES":invoked,"CANONICAL_PIPELINE_ONLY":not executable and not invoked}


def execute_actual_transport(event: Mapping[str, Any], registry: Mapping[str, Any], workspace: Path, *, bundled_python: str = "") -> dict[str, Any]:
    """Create evidence DIFF, test, commit, push and remote read-back from actual Git results."""
    required_event={"event_kind","source_chat","source_ref","feedback"}
    missing_event=sorted(required_event-set(event))
    if missing_event:
        return fail({"stage":"CAPTURED","status":"RUNNING"},"CAPTURED",f"event missing {missing_event}",True,"RECOVER_FIELDS_FROM_SOURCE_CHAT")
    target,row = resolve_event(registry,event)
    if target in registry['targets']:
        validate_registry(registry, target=target)
    else:
        validate_registry({'schema_version': 1, 'targets': {target: row}}, target=target)
    if row['status'] == 'COMPLETE':
        return {'status': 'SKIP_REUSE', 'stage': 'COMPLETE', 'target': target,
                'reason': 'Completed registered scope; new changes require explicit scoped reopening',
                'execution_allowed': False, 'customer_data_mutated': False,
                'evidence': {'commit': row['latest_verified_commit'], 'path': row['evidence_path'],
                             'run_id': row['first_validation']['run_id']},
                'NEXT_AUTOMATIC_ACTION': 'NONE_FOR_COMPLETED_SCOPE'}
    master_load_receipt=load_master_context(registry,event,workspace)
    if master_load_receipt.get("status") != "PASS":
        return fail({"stage":"MASTER_LOAD","status":"RUNNING","MASTER_LOAD_RECEIPT":master_load_receipt},"MASTER_LOAD",str(master_load_receipt.get("reason","MASTER_LOAD_FAIL")),True,"LOAD_REGISTERED_MASTERS_AND_RESUME")
    target,row = resolve_event(registry,event)
    state={"pipeline_id":stable_id(str(event["source_ref"]),str(event["feedback"])),"target":target,"repository":row["repository"],"stage":"TARGET_RESOLVED","status":"RUNNING","MASTER_LOAD_RECEIPT":master_load_receipt}
    evidence,work=build_packets(event,target,row); state.update({"evidence_packet":evidence,"work_packet":work})
    if not (evidence.get("actual_input_ref") and evidence.get("wrong_output_ref") and evidence.get("expected")):
        return fail(state,"EVIDENCE_READY","input/wrong-output/expected evidence references are incomplete",True,"CAPTURE_LINKED_EVIDENCE_FROM_SOURCE_CHAT")
    if git(workspace,"status","--porcelain").stdout.strip():
        return fail(state,"TARGET_APPLIED","target worktree is not clean",False,"PRESERVE_EXISTING_CHANGES_AND_USE_CLEAN_WORKTREE")
    remote_url=git(workspace,"remote","get-url","origin").stdout.strip().lower().removesuffix(".git")
    if not remote_url.endswith(str(row["repository"]).lower()):
        return fail(state,"TARGET_APPLIED",f"workspace repository mismatch: {remote_url}",False,"OPEN_REGISTERED_TARGET_WORKSPACE")
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
            return fail(state,"TARGET_APPLIED","remote diverged after a preserved local receipt",False,"PRESERVE_AND_RECONCILE")
        else:
            git(workspace,"merge","--ff-only","FETCH_HEAD")
        local_head=git(workspace,"rev-parse","HEAD").stdout.strip()
        if not resume_existing and local_head != remote_head: raise RuntimeError("automatic fast-forward read-back mismatch")
        state["AUTO_RECOVERY_RECEIPT"]={"action":"FETCH_AND_FAST_FORWARD_ONLY","from":pre_recovery_head,"to":local_head,"user_action_required":False}
    try:
        material_receipt=verify_material_change(event,workspace,local_head,registry,row,bundled_python)
    except RuntimeError as exc:
        return fail(state,"TARGET_APPLIED",str(exc),True,"EXECUTE_ACTUAL_FIX_OR_VERIFY_NO_DIFF")
    state["MATERIAL_CHANGE_RECEIPT"]=material_receipt
    if not resume_existing:
        receipt_path.parent.mkdir(parents=True,exist_ok=True)
        applied={"schema_version":1,"pipeline_id":state["pipeline_id"],"target":target,"source_ref":event["source_ref"],"root_cause_id":evidence["root_cause_id"],"adapter":row["adapter"],"pre_apply_commit":local_head,"mutation_scope":material_receipt["decision"],"material_change_receipt":material_receipt,"customer_data_mutated":False}
        receipt_path.write_text(json.dumps(applied,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    state["stage"]="TARGET_APPLIED"; test_receipt=execute_test(workspace,list(row["test_command"]),bundled_python); state["stage"]="TESTED"
    if not resume_existing:
        git(workspace,"add","--",str(receipt_rel).replace("\\","/")); git(workspace,"commit","-m",f"wic: record actual pipeline transport for {target}")
    commit_sha=git(workspace,"rev-parse","HEAD").stdout.strip(); state["stage"]="COMMITTED"
    pushed=git(workspace,"push","origin",f"HEAD:{row['branch']}",check=False)
    if pushed.returncode:
        git(workspace,"fetch","origin",row["branch"])
        return fail(state,"PUSHED","remote changed during push",False,"PRESERVE_AND_RECONCILE")
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
    from target_dispatcher import main as build_dispatch_plan
    build_dispatch_plan()
    if not os.getenv("GITHUB_ACTIONS"):
        (ROOT/"target_dispatch_plan.json").unlink(missing_ok=True)
    receipts={k:True for k in ("target_applied","central_applied","tested","committed","pushed","remote_verified","state_synced")}
    base={"event_kind":"ACTUAL_USER","source_ref":"CURRENT_CHAT#fixture","feedback":"실제 결과가 틀렸다. 수정해라.","actual_input_ref":"fixture/input","wrong_output_ref":"fixture/wrong","expected":"fixture/expected","recurrence":2}
    cases={}
    for target in sorted(registry["targets"]):
        cases[target]=run_event({**base,"source_chat":target,"tool_id":target},registry,receipts,fixture_mode=True)
        assert cases[target]["status"]=="PASS"
    cases["FUTURE_CHAT"]=run_event({**base,"source_chat":"CHAT999","tool_id":"TOOL999","registration_mode":"CENTRAL_LANE_PROVISIONAL"},registry,receipts,fixture_mode=True)
    assert cases["FUTURE_CHAT"]["status"]=="PASS" and cases["FUTURE_CHAT"]["target"]=="TOOL999"
    missing=run_event({**base,"source_chat":"UNKNOWN"},registry,receipts,fixture_mode=True)
    assert missing["FAILED_STAGE"]=="TARGET_RESOLVED" and missing["USER_ACTION_REQUIRED"] is False
    incomplete=run_event({**base,"source_chat":"TOOL041","wrong_output_ref":""},registry,receipts,fixture_mode=True)
    assert incomplete["FAILED_STAGE"]=="EVIDENCE_READY" and incomplete["AUTO_RECOVERABLE"] is True
    recovered=run_event({"event_kind":"ACTUAL_USER","source_chat":"TOOL041","source_ref":"CURRENT_CHAT#short-correction","feedback":"직전 출력의 부서가 틀렸다","user_correction":"공식 원문에 확인된 부서로 유지","source_context":{"previous_output_ref":"CURRENT_CHAT#assistant-previous"}},registry,receipts,fixture_mode=True)
    assert recovered["status"]=="PASS" and recovered["evidence_packet"]["evidence_recovered_from_source_context"] is True
    audit=canonical_execution_audit(); assert audit["CANONICAL_PIPELINE_ONLY"] and audit["ACTIVE_EXECUTABLE_PIPELINE_COUNT"]==1
    try: verify_material_change({},ROOT.parent,git(ROOT.parent,"rev-parse","HEAD").stdout.strip()); raise AssertionError("receipt-only event must be blocked")
    except RuntimeError as exc: assert "material_decision required" in str(exc)
    return {"result":"PASS_INTERNAL_E2E","stage_order":STAGES,"cases":cases,"canonical_execution_audit":audit,"RECEIPT_ONLY_FALSE_COMPLETE":"BLOCKED","failure_cases":{"unregistered":missing,"evidence_incomplete":incomplete},"current_active_targets":sorted(registry["targets"]),"registration_holds":registry["registration_holds"]}


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--self-test",action="store_true"); parser.add_argument("--master-load-first-validation",action="store_true"); parser.add_argument("--evidence",default="")
    parser.add_argument("--execute-event",default=""); parser.add_argument("--workspace",default=""); parser.add_argument("--bundled-python",default="")
    args=parser.parse_args()
    if args.master_load_first_validation:
        registry=json.loads(REGISTRY.read_text(encoding="utf-8"))
        result=load_master_context(registry,{"source_chat":"TOOL020","tool_id":"TOOL020"},ROOT.parent)
        assert result["status"]=="PASS" and result["work_entry_allowed"] is True
        assert result["load_order"]==["CENTRAL_COMMON_MASTER","TOOL_CANONICAL_MASTER","LATEST_CHECKPOINT_HANDOFF"]
        if args.evidence: Path(args.evidence).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(result,ensure_ascii=False,indent=2))
    elif args.self_test:
        result=self_test()
        if args.evidence: Path(args.evidence).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("PASS: registry-driven TOOL006/041/042/other/future-chat state-machine E2E")
    elif args.execute_event:
        registry=json.loads(REGISTRY.read_text(encoding="utf-8")); event=json.loads(Path(args.execute_event).read_text(encoding="utf-8"))
        result=execute_actual_transport(event,registry,Path(args.workspace),bundled_python=args.bundled_python)
        if args.evidence: Path(args.evidence).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__": main()
