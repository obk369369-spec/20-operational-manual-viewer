from __future__ import annotations
import argparse, concurrent.futures, json, os, re, threading, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
QUEUE=HERE/'tool044_atomic_demand_queue.json'
OUT=HERE/'evidence'/'tool044_dynamic_candidate_pool.json'

STOP={'VALIDATION','ENGINE','DETECTION','EXTRACTION','PRESERVATION','RENDERING','HIERARCHY','AUTOMATIC','TARGET','COPY'}

def load(p,fallback):
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else fallback

def query_terms(cap):
    words=[w.lower() for w in re.split(r'[_\- ]+',cap) if w and w not in STOP]
    if not words: words=[w.lower() for w in re.split(r'[_\- ]+',cap) if w]
    return ' '.join(words[:5])

def discover_one(cap):
    started=datetime.now(timezone.utc)
    q=query_terms(cap)
    url='https://api.github.com/search/repositories?q='+urllib.parse.quote(q+' in:name,description,readme')+'&sort=stars&order=desc&per_page=5'
    headers={'Accept':'application/vnd.github+json','User-Agent':'WIC-TOOL044'}
    token=os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token: headers['Authorization']='Bearer '+token
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=20) as r:
        data=json.load(r)
    rows=[]
    for item in data.get('items',[]):
        rows.append({
            'capability':cap,'status':'CANDIDATE_RECEIPT_ONLY','source':'GITHUB_PUBLIC_REPOSITORY',
            'full_name':item.get('full_name'),'official_source':item.get('html_url'),'description':item.get('description'),
            'default_branch':item.get('default_branch'),'license':(item.get('license') or {}).get('spdx_id') or 'NOT_PUBLISHED',
            'stars':item.get('stargazers_count',0),'forks':item.get('forks_count',0),'archived':item.get('archived'),
            'updated_at':item.get('updated_at'),'pushed_at':item.get('pushed_at'),
            'verification':'NOT_VERIFIED_BEHAVIOR','promotion_allowed':False})
    ended=datetime.now(timezone.utc)
    return cap, rows, {'worker_id':threading.current_thread().name,
                       'start':started.isoformat(),'end':ended.isoformat()}

def run(selected_caps=None):
    queue=load(QUEUE,{'demands':[]})
    caps=[]
    for d in queue.get('demands',[]):
        if d.get('status') in ('COMPLETED','VERIFIED'): continue
        caps.extend(d.get('atomic_capabilities',[]) or [])
    caps=list(dict.fromkeys(selected_caps or caps))
    results={}; errors={}; executions=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(8,max(1,len(caps)))) as pool:
        futs={pool.submit(discover_one,c):c for c in caps}
        for fut in concurrent.futures.as_completed(futs):
            cap=futs[fut]
            try:
                _,rows,execution=fut.result(); results[cap]=rows; executions.append({'capability':cap,**execution})
            except Exception as exc:
                errors[cap]=type(exc).__name__
    overlap=any(a['start'] < b['end'] and b['start'] < a['end'] for i,a in enumerate(executions) for b in executions[i+1:])
    payload={'schema_version':1,'updated_at':datetime.now(timezone.utc).isoformat(),'parallel_workers':min(8,max(1,len(caps))),
             'capabilities_queried':len(caps),'candidate_count':sum(map(len,results.values())),'candidates_by_capability':results,
             'errors':errors,'executions':sorted(executions,key=lambda x:x['start']),'actual_overlap':overlap,
             'rule':'DISCOVERY_ONLY_NO_PROMOTION_WITHOUT_RECEIPT_ARTIFACT_BEHAVIOR_TEST'}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return payload

def self_test():
    assert query_terms('TOC_HIERARCHY_VALIDATION')=='toc'
    assert query_terms('SAFE_AUTOMATIC_ROLLBACK')=='safe rollback'
    return 'PASS'

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--self-test',action='store_true'); p.add_argument('--capability',action='append'); a=p.parse_args()
    print(self_test() if a.self_test else json.dumps(run(a.capability),ensure_ascii=False))
