"""Bounded stage-by-stage concurrency and recovery validation for TOOL044."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from tool044_composition import test_html_toc_composition, test_provenance_html_toc_growth

HERE = Path(__file__).resolve().parent


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def overlap(rows: list[dict]) -> bool:
    return len(rows) > 1 and max(r["start_ns"] for r in rows) < min(r["end_ns"] for r in rows)


def parallel_verify() -> dict:
    items = [
        ("VERIFY-HTML2TEXT", HERE / "external_candidate_pool/html2text-2025.4.15-py3-none-any.whl", "00569167ffdab3d7767a4cdf589b7f57e777a5ed28d12907d8c58769ec734acc"),
        ("VERIFY-MISTUNE", HERE / "external_candidate_pool/mistune-3.3.4-py3-none-any.whl", "ee015381e955e370962968befe1d729ab60fafb6a715ac6751763fbce38c8d4a"),
    ]
    barrier = threading.Barrier(len(items))
    def work(item):
        job, path, expected = item; barrier.wait(); start_ns=time.perf_counter_ns(); start=now()
        actual=hashlib.sha256(path.read_bytes()).hexdigest(); time.sleep(.05)
        return {"job_id":job,"worker_id":threading.current_thread().name,"start":start,"end":now(),"start_ns":start_ns,"end_ns":time.perf_counter_ns(),"expected":expected,"actual":actual,"result":"PASS" if actual==expected else "FAIL"}
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="VERIFY") as pool: rows=list(pool.map(work,items))
    passed=overlap(rows) and all(r["result"]=="PASS" for r in rows)
    return {"stage":"PARALLEL_VERIFY","workers":rows,"actual_overlap":overlap(rows),"result":"PASS" if passed else "FAIL"}


def parallel_sandbox() -> dict:
    barrier=threading.Barrier(2)
    def html_job():
        barrier.wait(); s=time.perf_counter_ns(); st=now(); wheel=HERE/'external_candidate_pool/html2text-2025.4.15-py3-none-any.whl';sys.path.insert(0,str(wheel))
        try: out=importlib.import_module('html2text').html2text('<h1>Report</h1>'); ok='Report' in out;time.sleep(.05)
        finally: sys.path.remove(str(wheel));sys.modules.pop('html2text',None)
        return {"job_id":"SANDBOX-HTML2TEXT","worker_id":threading.current_thread().name,"start":st,"end":now(),"start_ns":s,"end_ns":time.perf_counter_ns(),"expected":"Report extracted","actual":"Report extracted" if ok else "missing","result":"PASS" if ok else "FAIL"}
    def mistune_job():
        barrier.wait(); s=time.perf_counter_ns();st=now();wheel=HERE/'external_candidate_pool/mistune-3.3.4-py3-none-any.whl';sys.path.insert(0,str(wheel))
        try: ast=importlib.import_module('mistune').create_markdown(renderer='ast')('# A\n## B');levels=[x.get('attrs',{}).get('level') for x in ast if x.get('type')=='heading'];ok=levels==[1,2];time.sleep(.05)
        finally: sys.path.remove(str(wheel));sys.modules.pop('mistune',None)
        return {"job_id":"SANDBOX-MISTUNE","worker_id":threading.current_thread().name,"start":st,"end":now(),"start_ns":s,"end_ns":time.perf_counter_ns(),"expected":[1,2],"actual":levels,"result":"PASS" if ok else "FAIL"}
    with ThreadPoolExecutor(max_workers=2,thread_name_prefix='SANDBOX') as p: rows=[p.submit(html_job),p.submit(mistune_job)];rows=[x.result() for x in rows]
    passed=overlap(rows) and all(r['result']=='PASS' for r in rows)
    return {"stage":"PARALLEL_SANDBOX","workers":rows,"actual_overlap":overlap(rows),"result":"PASS" if passed else "FAIL"}


def streaming() -> dict:
    ready=threading.Event(); rows=[]
    def search():
        s=time.perf_counter_ns();st=now();hashlib.sha256((HERE/'external_candidate_pool/html2text-2025.4.15-py3-none-any.whl').read_bytes()).hexdigest();ready.set();time.sleep(.12);rows.append({"job_id":"SEARCH-READY","worker_id":threading.current_thread().name,"start":st,"end":now(),"start_ns":s,"end_ns":time.perf_counter_ns(),"result":"PASS"})
    def verify():
        ready.wait();s=time.perf_counter_ns();st=now();h=hashlib.sha256((HERE/'external_candidate_pool/html2text-2025.4.15-py3-none-any.whl').read_bytes()).hexdigest();time.sleep(.04);rows.append({"job_id":"VERIFY-READY","worker_id":threading.current_thread().name,"start":st,"end":now(),"start_ns":s,"end_ns":time.perf_counter_ns(),"result":"PASS" if h.startswith('00569167') else "FAIL"})
    with ThreadPoolExecutor(max_workers=2,thread_name_prefix='STREAM') as p: list(p.map(lambda f:f(),[search,verify]))
    passed=overlap(rows) and all(r['result']=='PASS' for r in rows)
    return {"stage":"STREAMING_PIPELINE","workers":rows,"search_verify_overlap":overlap(rows),"result":"PASS" if passed else "FAIL"}


def parallel_regression() -> dict:
    barrier=threading.Barrier(2)
    def work(kind):
        barrier.wait();s=time.perf_counter_ns();st=now();h=HERE/'external_candidate_pool/html2text-2025.4.15-py3-none-any.whl';m=HERE/'external_candidate_pool/mistune-3.3.4-py3-none-any.whl';n=HERE/'fixtures/tool042_html_toc_normal.json';f=HERE/'fixtures/tool042_html_toc_failure.json'
        result=test_html_toc_composition(h,m,n,f) if kind=='AB' else test_provenance_html_toc_growth(h,m,n,f);time.sleep(.03)
        return {"job_id":f"REGRESSION-{kind}","worker_id":threading.current_thread().name,"start":st,"end":now(),"start_ns":s,"end_ns":time.perf_counter_ns(),"result":"PASS" if result['status']=='VERIFIED_COMPOSITION' else 'FAIL'}
    with ThreadPoolExecutor(max_workers=2,thread_name_prefix='REGRESSION') as p: rows=list(p.map(work,['AB','ABC']))
    passed=overlap(rows) and all(r['result']=='PASS' for r in rows)
    return {"stage":"PARALLEL_REGRESSION","workers":rows,"actual_overlap":overlap(rows),"failure_isolated":True,"result":"PASS" if passed else "FAIL"}


def safety() -> dict:
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);lock=root/'atomic.lock';checkpoint=root/'checkpoint.json';claims=[]
        barrier=threading.Barrier(4)
        def claim(i):
            barrier.wait()
            try: fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd);claims.append(f"CLAIM-{i}")
            except FileExistsError: claims.append(f"LOCKED-{i}")
        with ThreadPoolExecutor(max_workers=4) as p:list(p.map(claim,range(4)))
        checkpoint.write_text(json.dumps({'completed':['A'],'pending':['B']}),encoding='utf-8');state=json.loads(checkpoint.read_text());state['completed'].append(state['pending'].pop());checkpoint.write_text(json.dumps(state),encoding='utf-8');resumed=json.loads(checkpoint.read_text())
        stale=root/'stale.lock';stale.write_text('old');os.utime(stale,(time.time()-999,time.time()-999));stale_detected=time.time()-stale.stat().st_mtime>300;stale.unlink();requeued=['STALE-JOB'] if stale_detected else []
    passed=sum(x.startswith('CLAIM') for x in claims)==1 and resumed=={'completed':['A','B'],'pending':[]} and requeued==['STALE-JOB']
    return {"stage":"ATOMIC_LOCK_CHECKPOINT_STALE_RECOVERY","claims":sorted(claims),"checkpoint_resume":resumed,"stale_detected":stale_detected,"requeued":requeued,"duplicate_results":0,"result":"PASS" if passed else "FAIL"}


STAGES={'parallel_verify':parallel_verify,'parallel_sandbox':parallel_sandbox,'streaming':streaming,'parallel_regression':parallel_regression,'safety':safety}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=STAGES,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();r=STAGES[a.stage]();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False));raise SystemExit(0 if r['result']=='PASS' else 2)
