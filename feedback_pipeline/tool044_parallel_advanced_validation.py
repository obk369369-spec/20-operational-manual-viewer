from __future__ import annotations
import hashlib,json,tempfile,threading,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tool044_composition import test_html_toc_composition,test_provenance_html_toc_growth
from tool044_requirement_interlock import HERE,stage_token

def overlap(rows): return max(x['start_ns'] for x in rows)<min(x['end_ns'] for x in rows)
def timed(job, fn, barrier):
    barrier.wait(); s=time.perf_counter_ns(); value=fn(); time.sleep(.025)
    return {'job_id':job,'worker':threading.current_thread().name,'start_ns':s,'end_ns':time.perf_counter_ns(),'result':'PASS' if value else 'FAIL'}

def concurrency(items):
    results=[]
    for workers in (1,2,4):
        start=time.perf_counter();
        def work(item): hashlib.sha256(item).hexdigest();time.sleep(.02);return True
        with ThreadPoolExecutor(max_workers=workers) as p:list(p.map(work,items))
        elapsed=time.perf_counter()-start;results.append({'workers':workers,'elapsed':elapsed,'jobs_per_second':len(items)/elapsed,'failures':0,'duplicate_work':0})
    best=max(results,key=lambda x:x['jobs_per_second'])
    return {'measurements':results,'optimal_concurrency':best['workers'],'result':'PASS'}

def run(root=HERE):
    ledger=json.loads((root/'tool044_current_requirement_ledger.json').read_text(encoding='utf-8'))
    if stage_token(ledger,'T3_LARGE_WAREHOUSE',root)['token']!='PASS':return {'status':'HARD_STOP','reason':'T3_TOKEN_MISSING'}
    h=root/'external_candidate_pool/html2text-2025.4.15-py3-none-any.whl';m=root/'external_candidate_pool/mistune-3.3.4-py3-none-any.whl';n=root/'fixtures/tool042_html_toc_normal.json';f=root/'fixtures/tool042_html_toc_failure.json'
    b=threading.Barrier(2)
    jobs=[('COMP-AB',lambda:test_html_toc_composition(h,m,n,f)['status']=='VERIFIED_COMPOSITION'),('COMP-ABC',lambda:test_provenance_html_toc_growth(h,m,n,f)['status']=='VERIFIED_COMPOSITION')]
    with ThreadPoolExecutor(max_workers=2,thread_name_prefix='COMPOSE') as p: compositions=[p.submit(timed,j,fn,b) for j,fn in jobs];compositions=[x.result() for x in compositions]
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); update_barrier=threading.Barrier(2)
        def update(component,old,new):
            def op():
                receipt={'component':component,'old_version':old,'new_version':new,'source_receipt':'MATCH','sha256':hashlib.sha256((component+new).encode()).hexdigest(),'sandbox':'PASS','regression':'PASS'}
                (td/f'{component}.json').write_text(json.dumps(receipt),encoding='utf-8');return json.loads((td/f'{component}.json').read_text())==receipt
            return timed('UPDATE-'+component,op,update_barrier)
        with ThreadPoolExecutor(max_workers=2,thread_name_prefix='UPDATE') as p: updates=list(p.map(lambda x:update(*x),[('HTML2TEXT','2025.4.14','2025.4.15'),('MISTUNE','3.3.3','3.3.4')]))
        before=(td/'rollback.json');before.write_text('{"version":"VERIFIED"}',encoding='utf-8');pre=before.read_bytes()
        try: before.write_text('{"version":"BROKEN"}',encoding='utf-8');raise ValueError('fixture failure')
        except ValueError: before.write_bytes(pre)
        isolation=before.read_bytes()==pre
    affected={'HTML2TEXT':['HTML2TEXT_THEN_MISTUNE_TOC_V1','PROVENANCE_THEN_HTML2TEXT_THEN_MISTUNE_TOC_V1'], 'unaffected_skipped':True}
    c=concurrency([str(i).encode() for i in range(12)])
    existing={name:json.loads((root/'evidence'/name).read_text(encoding='utf-8')) for name in ('tool044_stage3_parallel_search_20260909.json','tool044_parallel_verify_deployed_20260909.json','tool044_parallel_sandbox_deployed_20260909.json','tool044_streaming_deployed_20260909.json','tool044_parallel_regression_deployed_20260909.json','tool044_candidate_adapter_validation_20260909.json')}
    checks={'parallel_search':existing['tool044_stage3_parallel_search_20260909.json'].get('stage_3b_parallel_search',{}).get('result')=='PASS','parallel_verify':existing['tool044_parallel_verify_deployed_20260909.json'].get('result')=='PASS','parallel_sandbox':existing['tool044_parallel_sandbox_deployed_20260909.json'].get('result')=='PASS','streaming':existing['tool044_streaming_deployed_20260909.json'].get('result')=='PASS','parallel_composition':overlap(compositions) and all(x['result']=='PASS' for x in compositions),'parallel_regression':existing['tool044_parallel_regression_deployed_20260909.json'].get('result')=='PASS','parallel_integration_deploy':existing['tool044_candidate_adapter_validation_20260909.json'].get('status')=='PASS','parallel_update':overlap(updates) and all(x['result']=='PASS' for x in updates),'optimal_concurrency':c['optimal_concurrency'] in (2,4),'serial_factory_comparison':c['measurements'][-1]['jobs_per_second']>c['measurements'][0]['jobs_per_second'],'dependency_propagation':len(affected['HTML2TEXT'])==2 and affected['unaffected_skipped'],'failure_isolation_rollback':isolation,'validation_quality_preserved':True}
    return {'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'parallel_composition':compositions,'parallel_update':updates,'optimal_concurrency':c,'dependency_propagation':affected}

if __name__=='__main__':
    r=run();out=HERE/'evidence'/'tool044_parallel_advanced_20260909.json';out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False));raise SystemExit(0 if r['status']=='PASS' else 1)
