from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from tool044_requirement_interlock import HERE

FILES=('tool044_candidate_adapter.py','tool044_candidate_deployed_validation.py','tool044_requirement_interlock.py','tool044_requirement_ledger.py','tool044_current_requirement_ledger.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(candidate:Path,production:Path):
    deployed=json.loads((candidate/'evidence'/'tool044_candidate_deployed_copy_20260909.json').read_text(encoding='utf-8'))
    matches={f:{'repo':sha(HERE/f),'candidate':sha(candidate/f),'match':sha(HERE/f)==sha(candidate/f)} for f in FILES}
    checks={'deployed_copy':deployed.get('status')=='DEPLOYED_PASS','all_file_hashes_match':all(x['match'] for x in matches.values()),'two_targets':deployed.get('checks',{}).get('two_structurally_different_candidates') is True,'incompatible_blocked':deployed.get('checks',{}).get('incompatible_target_blocked') is True,'production_unchanged':deployed.get('checks',{}).get('production_sha_unchanged') is True and sha(production)==deployed.get('production_sha_after')}
    return {'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'file_receipts':matches,'deployed_receipt':deployed}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--production',type=Path,required=True);a=p.parse_args();r=run(a.candidate,a.production);out=HERE/'evidence'/'tool044_candidate_actual_use_readback_20260909.json';out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False));raise SystemExit(0 if r['status']=='PASS' else 1)
