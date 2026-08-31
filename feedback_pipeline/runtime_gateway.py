"""Fail-closed runtime boundary for every registered WIC business output."""
from __future__ import annotations

import argparse, hashlib, json, subprocess
from pathlib import Path
from typing import Any, Mapping

ROOT=Path(__file__).resolve().parent
REGISTRY=ROOT/'wic_target_registry.json'
HOLD='HOLD_RUNTIME_NOT_VERIFIED'

def evaluate_handoff_pressure(runtime_context:Mapping[str,Any]|None)->dict[str,Any]:
    """Return an in-chat handoff warning before the WIC context becomes unsafe."""
    context=runtime_context or {}
    remaining=context.get('remaining_context_ratio')
    messages=context.get('message_count')
    near_limit=(isinstance(remaining,(int,float)) and remaining<=0.20) or (isinstance(messages,int) and messages>=180)
    if not near_limit:return {'handoff_required':False,'status':'CONTINUE_CURRENT_CHAT'}
    return {'handoff_required':True,'status':'PROACTIVE_HANDOFF_REQUIRED','message':'현재 대화가 길어졌습니다. 최신 checkpoint와 NEXT_START를 보존한 뒤 새 대화로 이어가세요.','chat_created':False,'chat_renamed':False}

def execute_feedback_event(event:Mapping[str,Any],workspace:Path,bundled_python:str='')->dict[str,Any]:
    from global_pipeline import execute_actual_transport
    registry=json.loads(REGISTRY.read_text(encoding='utf-8'))
    return execute_actual_transport(event,registry,workspace,bundled_python=bundled_python)

def run(args:list[str],cwd:Path,check:bool=True)->subprocess.CompletedProcess[str]:
    p=subprocess.run(args,cwd=cwd,text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=900)
    if check and p.returncode: raise RuntimeError(f"{args}: {p.stdout}\n{p.stderr}")
    return p

def git(cwd:Path,*args:str,check:bool=True):
    return run(['git','-c',f"safe.directory={str(cwd.resolve()).replace(chr(92),'/')}",*args],cwd,check)

def execute(spec:list[str],cwd:Path,bundled_python:str)->dict[str,Any]:
    if spec[0]=='WIC_BUILTIN_REQUIRED_FILES':
        checked=[]
        for item in spec[1:]:
            p=cwd/item
            if not p.is_file() or not p.stat().st_size: raise RuntimeError(f"missing required file {item}")
            checked.append({'path':item,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        return {'status':'PASS','command':spec,'checked':checked}
    cmd=list(spec)
    if cmd[0]=='WIC_BUNDLED_PYTHON':
        if not bundled_python: raise RuntimeError('bundled python unavailable')
        cmd[0]=bundled_python; cmd.insert(1,'-B')
    p=run(cmd,cwd)
    return {'status':'PASS','command':spec,'stdout':p.stdout[-4000:]}

def resolve(registry:Mapping[str,Any],target:str,provisional:bool=False)->tuple[str,dict[str,Any]]:
    if target in registry['targets']: return target,dict(registry['targets'][target])
    if provisional:
        row=dict(registry['targets'][registry['defaults']['provisional_registration_target']]); row['adapter']='CENTRAL_LANE_DIFF_ONLY'; return target,row
    raise KeyError(target)

def runtime_verify(target:str,workspace:Path,registry:Mapping[str,Any],bundled_python:str='',provisional:bool=False)->dict[str,Any]:
    state={'target':target,'status':HOLD,'LAST_VERIFIED_STAGE':'CHAT_TOOL_IDENTIFIED','USER_ACTION_REQUIRED':False}
    if target in {'TOOL041', 'TOOL042'}:
        # Global fixture PASS cannot authorize a specific customer's output.
        # Do not re-run historical tests while waiting for the native gate.
        return {**state, 'FAILED_STAGE': 'CUSTOMER_RELEASE_GATE',
                'FAIL_REASON': 'Use native canonical startup and customer_release_gate; semantic runtime is not connected',
                'output_allowed': False, 'OLD_PIPELINE_BLOCKED': True,
                'NEXT_AUTOMATIC_ACTION': 'NATIVE_CUSTOMER_RELEASE_GATE'}

    try: resolved,row=resolve(registry,target,provisional)
    except KeyError: return {**state,'FAILED_STAGE':'CANONICAL_REGISTRY','FAIL_REASON':'target not registered','NEXT_AUTOMATIC_ACTION':'REGISTER_PROVISIONAL_CENTRAL_LANE'}
    state.update({'resolved_target':resolved,'repository':row['repository'],'LAST_VERIFIED_STAGE':'CANONICAL_REGISTRY'})
    if git(workspace,'status','--porcelain').stdout.strip(): return {**state,'FAILED_STAGE':'LATEST_TARGET_MASTER_REVISION','FAIL_REASON':'worktree not clean','NEXT_AUTOMATIC_ACTION':'USE_CLEAN_VERIFIED_WORKTREE'}
    local=git(workspace,'rev-parse','HEAD').stdout.strip(); remote=git(workspace,'ls-remote','origin',f"refs/heads/{row['branch']}").stdout.split('\t')[0]
    if local!=remote:
        git(workspace,'fetch','origin',row['branch']); fetched=git(workspace,'rev-parse','FETCH_HEAD').stdout.strip()
        if git(workspace,'merge-base','--is-ancestor',local,'FETCH_HEAD',check=False).returncode: return {**state,'FAILED_STAGE':'LATEST_TARGET_MASTER_REVISION','FAIL_REASON':'local and remote diverged','NEXT_AUTOMATIC_ACTION':'PRESERVE_AND_RECONCILE'}
        git(workspace,'merge','--ff-only','FETCH_HEAD'); local=fetched
    state.update({'latest_revision':local,'LAST_VERIFIED_STAGE':'LATEST_TARGET_MASTER_REVISION'})
    override=registry.get('runtime_overrides',{}).get(resolved,{})
    required=override.get('required_assets') or list(dict.fromkeys([*row['master_paths'],row['state_path']]))
    for item in required:
        p=workspace/item
        if not p.is_file() or not p.stat().st_size: return {**state,'FAILED_STAGE':'REQUIRED_ASSETS','FAIL_REASON':f'missing/empty {item}','NEXT_AUTOMATIC_ACTION':'RECOVER_REQUIRED_ASSET_FROM_CHECKPOINT'}
    state['asset_receipt']={item:hashlib.sha256((workspace/item).read_bytes()).hexdigest() for item in required}; state['LAST_VERIFIED_STAGE']='REQUIRED_ASSETS'
    validator=override.get('validator') or row['test_command']; gate=override.get('output_gate') or row['test_command']
    try: vr=execute(list(validator),workspace,bundled_python); state['LAST_VERIFIED_STAGE']='VALIDATOR'; gr=execute(list(gate),workspace,bundled_python)
    except Exception as exc: return {**state,'FAILED_STAGE':'VALIDATOR_OR_OUTPUT_GATE','FAIL_REASON':str(exc),'NEXT_AUTOMATIC_ACTION':'FIX_RUNTIME_GATE_AND_RETRY'}
    state.update({'status':'PASS','stage':'FINAL_OUTPUT_ALLOWED','validator_receipt':vr,'output_gate_receipt':gr,'LATEST_MASTER_FORCED':True,'VALIDATOR_FORCED':True,'OUTPUT_GATE_FORCED':True,'OLD_PIPELINE_BLOCKED':True,'MEMORY_ONLY_GENERATION_BLOCKED':True})
    return state

def capture_feedback(source_chat:str,wrong_output_ref:str,user_correction:str,*,source_ref:str='',tool_id:str='',execute_actual_pipeline=None,execution_event:Mapping[str,Any]|None=None,runtime_context:Mapping[str,Any]|None=None)->dict[str,Any]:
    from event_ledger import append_occurrence
    ledger_event=execution_event or {'source_chat':source_chat,'tool_id':tool_id,'source_ref':source_ref or wrong_output_ref,'feedback':user_correction,'wrong_output_ref':wrong_output_ref}
    occurrence=append_occurrence(ledger_event)
    event_id=occurrence['occurrence_id']
    stages=['CAPTURED','NORMALIZED','TARGET_RESOLVED','EXISTING_ROOT_SEARCH','DEDUP_RECURRENCE_UPDATE','EVIDENCE_LINK','ROOT_CLASSIFIED','DIRECT_FIX_READY']
    captured={'event_kind':'ACTUAL_USER_FEEDBACK','feedback_id':event_id,'occurrence_receipt':occurrence,'source_chat':source_chat,'wrong_output_ref':wrong_output_ref,'user_correction':user_correction,'stage':'DIRECT_FIX_READY','stage_history':stages,'deferred':False,'user_manual_routing':False,'handoff_pressure':evaluate_handoff_pressure(runtime_context)}
    if execute_actual_pipeline is None or execution_event is None:
        return {**captured,'status':HOLD,'FAILED_STAGE':'ACTUAL_EXECUTOR','FAIL_REASON':'actual executor context unavailable','DIRECT_FIX_READY_AUTO_CONTINUE':False}
    result=execute_actual_pipeline(execution_event)
    return {**captured,'stage':result.get('stage','ACTUAL_EXECUTOR'),'status':result.get('status','FAIL'),'execution_result':result,'DIRECT_FIX_READY_AUTO_CONTINUE':True,'ACTUAL_FEEDBACK_AUTO_EXECUTION':True}

def capture_handoff(source_chat:str,tool_id:str,source_ref:str,checkpoint_ref:str,next_start:str)->dict[str,Any]:
    """Persist handoff metadata without creating, renaming, or selecting a UI chat."""
    from event_ledger import append_occurrence
    if not checkpoint_ref or not next_start:
        return {'status':'HOLD','FAILED_STAGE':'HANDOFF_SYNCED','FAIL_REASON':'checkpoint_ref and next_start required','USER_ACTION_REQUIRED':False}
    row=append_occurrence({'event_kind':'CHAT_HANDOFF_EVENT','source_chat':source_chat,'tool_id':tool_id,'source_ref':source_ref,'handoff_directive':'다음 대화창으로 옮겨','checkpoint_ref':checkpoint_ref,'next_start':next_start})
    return {'status':'PASS','stage':'HANDOFF_SYNCED','occurrence_receipt':row,'chat_created':False,'chat_renamed':False,'latest_master_preload_required':True}

def self_test()->None:
    from tempfile import TemporaryDirectory
    from event_ledger import append_occurrence
    with TemporaryDirectory() as td:
        p=Path(td)/'ledger.jsonl'; base={'source_chat':'TOOL041','tool_id':'TOOL041','source_ref':'fixture:1','feedback':'다른 고객 정보가 섞였다','wrong_output_ref':'wrong:1'}
        a=append_occurrence(base,p); b=append_occurrence(base,p); c=append_occurrence({**base,'source_ref':'fixture:2'},p)
        if not (a['append_status']=='APPENDED' and b['append_status']=='IDEMPOTENT_REPLAY' and c['occurrence_id']!=a['occurrence_id']): raise RuntimeError('durable ledger idempotency fixture failed')
        h=append_occurrence({'event_kind':'CHAT_HANDOFF_EVENT','source_chat':'TOOL041','tool_id':'TOOL041','source_ref':'handoff:1','handoff_directive':'다음 대화창으로 옮겨','checkpoint_ref':'sha:fixture','next_start':'resume'},p)
        if h['event_kind']!='CHAT_HANDOFF_EVENT' or not h['checkpoint_ref']: raise RuntimeError('handoff ledger fixture failed')
    r=json.loads(REGISTRY.read_text(encoding='utf-8'))
    if r['runtime_contract']['old_pipeline_allowed'] is not False or r['runtime_contract']['memory_only_generation_allowed'] is not False: raise RuntimeError('runtime contract drift')
    if evaluate_handoff_pressure({'remaining_context_ratio':0.19})['status']!='PROACTIVE_HANDOFF_REQUIRED':raise RuntimeError('proactive handoff threshold failed')
    if evaluate_handoff_pressure({'remaining_context_ratio':0.80})['handoff_required']:raise RuntimeError('handoff false positive')
    print('PASS: runtime fail-closed + immediate actual feedback capture contract')

def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--target',default='');p.add_argument('--workspace',default='');p.add_argument('--bundled-python',default='');p.add_argument('--provisional',action='store_true');p.add_argument('--evidence',default='');a=p.parse_args()
    if a.self_test:self_test();return
    result=runtime_verify(a.target,Path(a.workspace),json.loads(REGISTRY.read_text(encoding='utf-8')),a.bundled_python,a.provisional)
    if a.evidence:Path(a.evidence).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['status']=='PASS' else 2)
if __name__=='__main__':main()

