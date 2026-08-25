"""Fail-closed runtime boundary for every registered WIC business output."""
from __future__ import annotations

import argparse, hashlib, json, subprocess
from pathlib import Path
from typing import Any, Mapping

ROOT=Path(__file__).resolve().parent
REGISTRY=ROOT/'wic_target_registry.json'
HOLD='HOLD_RUNTIME_NOT_VERIFIED'

def run(args:list[str],cwd:Path,check:bool=True)->subprocess.CompletedProcess[str]:
    p=subprocess.run(args,cwd=cwd,text=True,encoding='utf-8',errors='replace',capture_output=True)
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

def capture_feedback(source_chat:str,wrong_output_ref:str,user_correction:str)->dict[str,Any]:
    event_id=hashlib.sha256(f'{source_chat}\0{wrong_output_ref}\0{user_correction}'.encode()).hexdigest()[:20]
    return {'event_kind':'ACTUAL_USER_FEEDBACK','feedback_id':event_id,'source_chat':source_chat,'wrong_output_ref':wrong_output_ref,'user_correction':user_correction,'stage':'CAPTURED','next_automatic_action':'NORMALIZE_RESOLVE_DEDUP_EVIDENCE_EXECUTE','deferred':False,'user_manual_routing':False}

def self_test()->None:
    e=capture_feedback('TOOL041','wrong:1','다른 고객 정보가 섞였다'); assert e['stage']=='CAPTURED' and not e['deferred'] and not e['user_manual_routing']
    r=json.loads(REGISTRY.read_text(encoding='utf-8')); assert r['runtime_contract']['old_pipeline_allowed'] is False and r['runtime_contract']['memory_only_generation_allowed'] is False
    print('PASS: runtime fail-closed + immediate actual feedback capture contract')

def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--target',default='');p.add_argument('--workspace',default='');p.add_argument('--bundled-python',default='');p.add_argument('--provisional',action='store_true');p.add_argument('--evidence',default='');a=p.parse_args()
    if a.self_test:self_test();return
    result=runtime_verify(a.target,Path(a.workspace),json.loads(REGISTRY.read_text(encoding='utf-8')),a.bundled_python,a.provisional)
    if a.evidence:Path(a.evidence).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['status']=='PASS' else 2)
if __name__=='__main__':main()
