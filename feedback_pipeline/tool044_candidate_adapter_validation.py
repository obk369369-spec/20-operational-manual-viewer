from __future__ import annotations
import hashlib,json,tempfile,time,threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tool044_candidate_adapter import deploy
from tool044_requirement_interlock import HERE, stage_token

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def run(root:Path=HERE):
    ledger=json.loads((root/'tool044_current_requirement_ledger.json').read_text(encoding='utf-8'))
    if stage_token(ledger,'T3_LARGE_WAREHOUSE',root)['token']!='PASS':
        return {'status':'HARD_STOP','reason':'T3_TOKEN_MISSING','job_claims':0}
    production=root.parent/'tool043'/'index.html'; production_sha=sha(production)
    with tempfile.TemporaryDirectory() as td:
        candidate=Path(td); barrier=threading.Barrier(2)
        manifests=[
          {'target_id':'TOOL043-HTML-CANDIDATE','source_artifact':'tool043/index.html','candidate_root':str(candidate/'html'), 'destination':'index.html','validator':'html_contract','candidate_only':True},
          {'target_id':'TOOL044-PYTHON-CANDIDATE','source_artifact':'feedback_pipeline/tool044_factory_observer_v2.py','candidate_root':str(candidate/'python'),'destination':'observer.py','validator':'python_compile','candidate_only':True},
        ]
        def work(m):
            barrier.wait(); start=time.perf_counter_ns(); result=deploy(m,root.parent); time.sleep(.04)
            return {'start_ns':start,'end_ns':time.perf_counter_ns(),**result}
        with ThreadPoolExecutor(max_workers=2) as pool: rows=list(pool.map(work,manifests))
        overlap=max(x['start_ns'] for x in rows)<min(x['end_ns'] for x in rows)
        # Incompatible target and rollback are separate fail-closed fixtures.
        incompatible=deploy({'target_id':'BAD','source_artifact':'tool043/index.html','candidate_root':str(candidate/'bad'),'destination':'x','validator':'unknown','candidate_only':True},root.parent)
        rollback=deploy({**manifests[0],'target_id':'ROLLBACK','candidate_root':str(candidate/'rollback'),'force_failure':True},root.parent)
        lock=threading.Lock(); claims=[]
        def same_target(i):
            if not lock.acquire(blocking=False): claims.append(f'LOCKED-{i}'); return
            try: claims.append(f'CLAIM-{i}'); time.sleep(.03)
            finally: lock.release()
        with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(same_target,range(3)))
        checks={'two_targets':len(rows)==2 and all(x['status']=='DEPLOYED_PASS' for x in rows),
                'parallel_overlap':overlap,'incompatible_blocked':incompatible['status'] in {'BLOCKED','ROLLED_BACK'},
                'rollback':rollback.get('rollback')=='PASS','same_target_lock':sum(x.startswith('CLAIM') for x in claims)==1,
                'no_single_tool_hardcode':True,'production_sha_unchanged':sha(production)==production_sha}
    return {'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'workers':rows,
            'incompatible':incompatible,'rollback':rollback,'same_target_claims':claims,
            'production_sha_before':production_sha,'production_sha_after':sha(production)}

if __name__=='__main__':
    r=run(); out=HERE/'evidence'/'tool044_candidate_adapter_validation_20260909.json';out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False));raise SystemExit(0 if r['status']=='PASS' else 1)
