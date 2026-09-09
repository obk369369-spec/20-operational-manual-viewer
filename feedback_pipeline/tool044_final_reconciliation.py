from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from tool044_requirement_interlock import HERE,stage_token

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(candidate:Path,production:Path,local_sha:str|None=None,remote_sha:str|None=None):
    ledger=read(HERE/'tool044_current_requirement_ledger.json')
    prior={s:stage_token(ledger,s,HERE)['token'] for s in ('T0_GOVERNANCE','T1_CROSS_CHAT','T2_COMPONENT_INTEGRITY','T3_LARGE_WAREHOUSE','T4_PARALLEL_FACTORY','T5_AUTO_DEPLOY','T6_OBSERVER')}
    safety=read(HERE/'evidence'/'tool044_safety_deployed_20260909.json')
    cloud=read(HERE/'evidence'/'tool044_cloud_zero_work_20260908.json')
    state=read(HERE/'tool044_cloud_state.json')
    deployed=read(candidate/'evidence'/'tool044_candidate_deployed_copy_20260909.json')
    browser=read(HERE/'evidence'/'tool044_observer_browser_e2e_20260909.json')
    scheduler_text=(HERE/'evidence'/'TOOL044_ZERO_WORK_24H_FINALIZATION_20260907.md').read_text(encoding='utf-8')
    production_now=sha(production)
    checks={
      'prior_stage_tokens':all(x=='PASS' for x in prior.values()),
      'atomic_lock':safety.get('result')=='PASS' and sum(x.startswith('CLAIM') for x in safety.get('claims',[]))==1,
      'duplicate_elimination':safety.get('duplicate_results')==0,
      'checkpoint_resume':safety.get('checkpointfält','')=='PASS' or safety.get('checkpoint_resume',{}).get('pending')==[],
      'stale_worker_recovery':safety.get('stale_detected') is True and safety.get('requeued')==['STALE-JOB'],
      'watchdog_heartbeat':bool(state.get('last_heartbeat')) and state.get('restart_count',0)>0,
      'natural_schedule':cloud.get('natural_schedule_run',{}).get('event')=='schedule' and cloud.get('natural_schedule_run',{}).get('work_triggered') is False and cloud.get('natural_schedule_run',{}).get('user_triggered') is False,
      'repeated_auto_cycle':'Natural cycle A' in scheduler_text and 'Natural cycle B' in scheduler_text,
      'twenty_four_hour_capable':state.get('work_session_required') is False and state.get('long_running_stability_validation',{}).get('status')=='RUNNING',
      'candidate_final_retest':deployed.get('status')=='DEPLOYED_PASS',
      'observer_deployed_retest':browser.get('deployed_copy_retest',{}).get('result')=='DEPLOYED_COPY_PASS',
      'production_protection':deployed.get('production_sha_after')==production_now and deployed.get('checks',{}).get('production_sha_unchanged') is True,
      'remote_readback':bool(local_sha and remote_sha and local_sha==remote_sha),
    }
    # Zero scan is against the current denominator, not superseded historical receipts.
    unresolved=[r['req_id'] for r in ledger['requirements'] if r['stage'] in prior and r.get('status')!='PASS']
    checks['non_time_dependent_prior_stage_missing_zero']=not unresolved
    return {'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'prior_tokens':prior,
            'unresolved_prior':unresolved,'twenty_four_hour_active':'RUNNING_NOT_YET_PASS',
            'production_sha':production_now,'local_sha':local_sha,'remote_sha':remote_sha,
            'candidate_receipt_sha':sha(candidate/'evidence'/'tool044_candidate_deployed_copy_20260909.json')}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--production',type=Path,required=True);p.add_argument('--local-sha');p.add_argument('--remote-sha');a=p.parse_args();r=run(a.candidate,a.production,a.local_sha,a.remote_sha);out=HERE/'evidence'/'tool044_final_reconciliation_20260909.json';out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False));raise SystemExit(0 if r['status']=='PASS' else 1)
