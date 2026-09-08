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

def source_record(row, demand_id, source):
    return {
        'SOURCE_CHAT_OR_TOOL': row.get('source_chat_or_tool') or row.get('SOURCE_CHAT_OR_TOOL') or source,
        'TOOL_ID': row.get('related_tool') or row.get('tool_id') or row.get('TOOL_ID'),
        'FUNCTION_ID': row.get('function_id') or row.get('FUNCTION_ID') or row.get('demand_id'),
        'ORIGINAL_ERROR_OR_FEEDBACK': row.get('original_error_or_feedback') or row.get('REMAINING_ERROR') or row.get('purpose'),
        'OCCURRENCE_OR_EVIDENCE': row.get('occurrence_or_evidence') or row.get('REPEATED_ERROR_COUNT'),
        'ROOT_ID': row.get('root_id') or row.get('ROOT_ID') or row.get('demand_id'),
        'MISSING_CAPABILITY': row.get('missing_capabilities') or row.get('MISSING_CAPABILITY') or row.get('required_capabilities'),
        'CURRENT_STATUS': row.get('current_status') or row.get('CURRENT_STATUS') or row.get('status'),
        'SOURCE_EVIDENCE': row.get('source_evidence') or row.get('IMPROVEMENT_EVIDENCE'),
        'TOOL044_DEMAND_ID': demand_id,
    }

def add_or_merge(queue, demand, record):
    existing=next((d for d in queue['demands'] if d.get('demand_id')==demand['demand_id']),None)
    if existing is None:
        demand['source_records']=[record]
        queue['demands'].append(demand)
        return True
    records=existing.setdefault('source_records',[])
    signature=lambda r:(r.get('SOURCE_CHAT_OR_TOOL'),r.get('TOOL_ID'),r.get('FUNCTION_ID'),r.get('ROOT_ID'))
    if signature(record) not in {signature(r) for r in records}:
        records.append(record)
    return False

def route(inbox_path=INBOX, queue_path=QUEUE, function_state_path=FUNCTION_STATE):
    inbox=load(inbox_path,{'requests':[]}); queue=load(queue_path,{'schema_version':1,'demands':[]})
    existing={d.get('demand_id') for d in queue.get('demands',[])}
    added=[]
    for r in inbox.get('requests',[]):
        caps=atomic_from_request(r)
        rid=r.get('request_id') or 'REQ-'+hashlib.sha256(json.dumps(r,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:12]
        for cap in caps:
            did=f'{rid}-{cap}'
            demand={'demand_id':did,'target_tool':r.get('related_tool') or r.get('tool_or_program_name'),'atomic_capabilities':[cap],'status':'OPEN','source':'TOOL044_REQUEST_INBOX','request_id':rid,'root_id':r.get('root_id')}
            if add_or_merge(queue,demand,source_record(r,did,'TOOL044_REQUEST_INBOX')):
                existing.add(did); added.append(did)
    fs=load(function_state_path,{})
    function_rows=fs.get('functions',[]) or []
    for row in fs.get('tool044_external_demand_candidates',[]) or []:
        detail=next((f for f in function_rows if f.get('FUNCTION_ID')==row.get('demand_id') or f.get('ROOT_ID')==row.get('demand_id')),row)
        for cap in row.get('missing_capabilities',[]) or []:
            canonical=next((d for d in queue['demands'] if d.get('demand_id')==row.get('demand_id') and cap in (d.get('atomic_capabilities') or [])),None)
            if canonical is not None:
                add_or_merge(queue,canonical,source_record(detail,canonical['demand_id'],'TOOL016_FUNCTION_STATE'))
                continue
            base=str(row.get('demand_id') or row.get('function_id') or row.get('tool_id') or 'FUNCTION')
            did=f'FS-{re.sub("[^A-Za-z0-9_-]+","-",base)}-{cap}'
            demand={'demand_id':did,'target_tool':detail.get('TOOL_ID') or row.get('tool_id'),'atomic_capabilities':[cap],'status':'OPEN','source':'TOOL016_FUNCTION_STATE','root_id':detail.get('ROOT_ID') or row.get('demand_id')}
            if add_or_merge(queue,demand,source_record(detail,did,'TOOL016_FUNCTION_STATE')):
                existing.add(did); added.append(did)
    queue_path.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'added':len(added),'demand_ids':added,'total':len(queue.get('demands',[]))}

def self_test():
    assert atomic_from_request({'name':'목차 정리'})[:3]==['LINE_SPLIT','TOC_NUMBER_DETECTION','TOC_DEPTH_DETECTION']
    assert atomic_from_request({'name':'unknown'})==['INPUT_CONTRACT_VALIDATION','EXPECTED_ACTUAL_VALIDATION','FAILURE_ISOLATION']
    demand={'demands':[]}; row={'related_tool':'TOOL006','function_id':'T6-F','root_id':'R','purpose':'목차 오류'}
    did='R-TOC'; assert add_or_merge(demand,{'demand_id':did},source_record(row,did,'CHAT'))
    assert not add_or_merge(demand,{'demand_id':did},source_record(row,did,'CHAT'))
    assert len(demand['demands'][0]['source_records'])==1
    return 'PASS'

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--self-test',action='store_true'); a=p.parse_args()
    print(self_test() if a.self_test else json.dumps(route(),ensure_ascii=False))
