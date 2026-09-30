from __future__ import annotations
import argparse, concurrent.futures, json, math, os, re, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
QUEUE=HERE/'tool044_atomic_demand_queue.json'
OUT=HERE/'evidence'/'tool044_dynamic_candidate_pool.json'

# Permanent multi-angle discovery roots.  Queue capabilities are appended to
# these; a single empty search result can never terminate discovery globally.
DISCOVERY_ROOTS = [
    'ci hosted runner', 'coding agent orchestrator', 'ai agent workspace',
    'cloud development executor', 'serverless background worker',
    'distributed job queue worker', 'workflow automation engine',
    'mcp plugin connector', 'cli remote execution', 'multi agent parallel workspace',
]

STOP={'VALIDATION','ENGINE','DETECTION','EXTRACTION','PRESERVATION','RENDERING','HIERARCHY','AUTOMATIC','TARGET','COPY'}

def load(p,fallback):
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else fallback

def query_terms(cap):
    words=[w.lower() for w in re.split(r'[_\- ]+',cap) if w and w not in STOP]
    if not words: words=[w.lower() for w in re.split(r'[_\- ]+',cap) if w]
    return ' '.join(words[:5])

def discover_one(cap, per_page):
    q=query_terms(cap)
    url='https://api.github.com/search/repositories?q='+urllib.parse.quote(q+' in:name,description,readme')+'&sort=stars&order=desc&per_page='+str(per_page)
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
    return cap, rows

def run():
    queue=load(QUEUE,{'demands':[]})
    previous=load(OUT,{'candidates_by_capability':{},'discovery_history':[]})
    caps=[]
    for d in queue.get('demands',[]):
        if d.get('status') in ('COMPLETED','VERIFIED'): continue
        caps.extend(d.get('atomic_capabilities',[]) or [])
    caps=list(dict.fromkeys(DISCOVERY_ROOTS + caps))
    target=max(1,int(os.environ.get('TOOL044_PRELOAD_TARGET','1000')))
    per_page=min(100,max(5,math.ceil(target/max(1,len(caps)))))
    workers=min(4,max(1,len(caps)))
    results={}; errors={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futs={pool.submit(discover_one,c,per_page):c for c in caps}
        for fut in concurrent.futures.as_completed(futs):
            cap=futs[fut]
            try:
                _,rows=fut.result(); results[cap]=rows
            except Exception as exc:
                errors[cap]=type(exc).__name__
    merged={key:list(rows) for key,rows in previous.get('candidates_by_capability',{}).items()}
    for cap,rows in results.items():
        by_name={row.get('full_name'):row for row in merged.get(cap,[]) if row.get('full_name')}
        for row in rows: by_name[row.get('full_name')]=row
        merged[cap]=list(by_name.values())
    now=datetime.now(timezone.utc)
    history=list(previous.get('discovery_history',[]))[-29:]
    history.append({'date_utc':now.date().isoformat(),'executed_at':now.isoformat(),
                    'new_results':sum(map(len,results.values())),'errors':len(errors)})
    payload={'schema_version':2,'updated_at':now.isoformat(),'discovery_date_utc':now.date().isoformat(),
             'daily_discovery_executed':True,'discovery_roots':DISCOVERY_ROOTS,
             'parallel_workers':workers,'requested_target':target,'per_capability_limit':per_page,
             'capabilities_queried':len(caps),'candidate_count':sum(map(len,merged.values())),
             'new_results_this_run':sum(map(len,results.values())),
             'candidates_by_capability':merged,'discovery_history':history,
             'errors':errors,
             'lifecycle_gate':['DISCOVERED','FREE_TERMS_CHECKED','EXECUTION_CONTRACT_CONFIRMED',
                               'SECURITY_AUTH_CHECKED','MINIMAL_CANARY_EXECUTED','RESULT_RETRIEVED',
                               'CENTRAL_REGISTRY_REGISTERED','CIRCULATION_CONNECTED'],
             'connected_count':0,
             'rule':'DISCOVERY_ONLY_NO_PROMOTION_WITHOUT_FREE_TERMS_AUTH_CONTRACT_CANARY_RESULT_AND_CENTRAL_RETURN'}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return payload

def self_test():
    assert query_terms('TOC_HIERARCHY_VALIDATION')=='toc'
    assert query_terms('SAFE_AUTOMATIC_ROLLBACK')=='safe rollback'
    assert len(DISCOVERY_ROOTS)>=10
    return 'PASS'

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--self-test',action='store_true'); a=p.parse_args()
    print(self_test() if a.self_test else json.dumps(run(),ensure_ascii=True))
