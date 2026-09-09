from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from tool044_candidate_adapter import deploy

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def run(root:Path,production:Path):
    production_before=sha(production)
    if (root/'fixtures'/'tool043_actual_index.html').is_file(): html_source='fixtures/tool043_actual_index.html'
    else: html_source='../tool043/index.html'
    manifests=[
      {'target_id':'TOOL043-HTML-CANDIDATE','source_artifact':html_source,'candidate_root':str(root/'deployed_targets'/'tool043'),'destination':'index.html','validator':'html_contract','candidate_only':True},
      {'target_id':'TOOL044-PYTHON-CANDIDATE','source_artifact':'tool044_factory_observer_v2.py','candidate_root':str(root/'deployed_targets'/'tool044'),'destination':'observer.py','validator':'python_compile','candidate_only':True},
    ]
    rows=[deploy(m,root) for m in manifests]
    bad=deploy({'target_id':'INCOMPATIBLE','source_artifact':html_source,'candidate_root':str(root/'deployed_targets'/'bad'),'destination':'bad.bin','validator':'unsupported','candidate_only':True},root)
    checks={'two_structurally_different_candidates':all(x.get('status')=='DEPLOYED_PASS' for x in rows),
            'cross_repository_readback':all(x.get('post_sha')==x.get('source_sha') for x in rows),
            'incompatible_target_blocked':bad.get('status')=='ROLLED_BACK',
            'production_sha_unchanged':sha(production)==production_before}
    return {'status':'DEPLOYED_PASS' if all(checks.values()) else 'FAIL','checks':checks,
            'targets':rows,'incompatible':bad,'production_sha_before':production_before,
            'production_sha_after':sha(production)}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=Path(__file__).resolve().parent);a.add_argument('--production',type=Path,required=True);args=a.parse_args()
    result=run(args.root.resolve(),args.production.resolve());out=args.root/'evidence'/'tool044_candidate_deployed_copy_20260909.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False));raise SystemExit(0 if result['status']=='DEPLOYED_PASS' else 1)
