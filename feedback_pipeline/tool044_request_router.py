from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
INBOX=HERE/'TOOL044_REQUEST_INBOX.json'
QUEUE=HERE/'tool044_atomic_demand_queue.json'
FUNCTION_STATE=HERE/'tool044_function_state.json'

RULES={
 '목차':['LINE_SPLIT','TOC_NUMBER_DETECTION','TOC_DEPTH_DETECTION','PARENT_CHILD_HIERARCHY','INDENT_RENDERING','DEPTH_PRUNING','SOURCE_TEXT_PRESERVATION','HIERARCHY_ERROR_DETECTION'],
 'toc':['LINE_SPLIT','TOC_NUMBER_DETECTION','TOC_DEPTH_DETECTION','PARENT_CHILD_HIERARCHY','INDENT_RENDERING','DEPTH_PRUNING','SOURCE_TEXT_PRESERVATION','HIERARCHY_ERROR_DETECTION'],
 'url':['URL_VALIDATION','DOMAIN_DECOMPOSITION','PROVENANCE_VALIDATION'],
 'reseller':['RESELLER_DETECTION','PROVENANCE_VALIDATION'],
 '배포':['VERIFIED_TARGET_DEPLOYMENT','DEPLOYED_COPY_VALIDATION','SAFE_AUTOMATIC_ROLLBACK'],
 'deploy':['VERIFIED_TARGET_DEPLOYMENT','DEPLOYED_COPY_VALIDATION','SAFE_AUTOMATIC_ROLLBACK'],
 'rollback':['SAFE_AUTOMATIC_ROLLBACK'],
}

def load(p, fallback):
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else fallback

def atomic_from_request(r):
    text=' '.join(str(r.get(k,'')) for k in ('tool_or_program_name','name','purpose','desired_result','description')).lower()
    caps=[]
    for key, vals in RULES.items():
        if key in text:
            caps.extend(vals)
    caps.extend(r.get('required_capabilities',[]) or [])
    # generic requirements every executable tool needs
    if text and not caps:
        caps=['INPUT_CONTRACT_VALIDATION','EXPECTED_ACTUAL_VALIDATION','FAILURE_ISOLATION']
    return list(dict.fromkeys(caps))

def route():
    inbox=load(INBOX,{'requests':[]}); queue=load(QUEUE,{'schema_version':1,'demands':[]})
    existing={d.get('demand_id') for d in queue.get('demands',[])}
    added=[]
    for r in inbox.get('requests',[]):
        caps=atomic_from_request(r)
        rid=r.get('request_id') or 'REQ-'+hashlib.sha256(json.dumps(r,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:12]
        for cap in caps:
            did=f'{rid}-{cap}'
            if did in existing: continue
            queue['demands'].append({'demand_id':did,'target_tool':r.get('related_tool') or r.get('tool_or_program_name'),'atomic_capabilities':[cap],'status':'OPEN','source':'TOOL044_REQUEST_INBOX','request_id':rid})
            existing.add(did); added.append(did)
    fs=load(FUNCTION_STATE,{})
    for row in fs.get('tool044_external_demand_candidates',[]) or []:
        for cap in row.get('missing_capabilities',[]) or []:
            base=str(row.get('function_id') or row.get('tool_id') or 'FUNCTION')
            did=f'FS-{re.sub("[^A-Za-z0-9_-]+","-",base)}-{cap}'
            if did in existing: continue
            queue['demands'].append({'demand_id':did,'target_tool':row.get('tool_id'),'atomic_capabilities':[cap],'status':'OPEN','source':'TOOL016_FUNCTION_STATE'})
            existing.add(did); added.append(did)
    QUEUE.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'added':len(added),'demand_ids':added,'total':len(queue.get('demands',[]))}

def self_test():
    assert atomic_from_request({'name':'목차 정리'})[:3]==['LINE_SPLIT','TOC_NUMBER_DETECTION','TOC_DEPTH_DETECTION']
    assert atomic_from_request({'name':'unknown'})==['INPUT_CONTRACT_VALIDATION','EXPECTED_ACTUAL_VALIDATION','FAILURE_ISOLATION']
    return 'PASS'

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--self-test',action='store_true'); a=p.parse_args()
    print(self_test() if a.self_test else json.dumps(route(),ensure_ascii=False))
