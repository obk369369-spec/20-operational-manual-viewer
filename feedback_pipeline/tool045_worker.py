from __future__ import annotations
import json, re, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'feedback_pipeline'/'tool045_input'
STATE=ROOT/'feedback_pipeline'/'tool045_state.json'
OUT=ROOT/'feedback_pipeline'/'tool045_occurrences.jsonl'
HANDOFF=ROOT/'feedback_pipeline'/'tool045_tool016_handoff.json'

ERROR_TERMS=('오류','실패','안됨','안 돼','문제','불편','수정','개선','재발','검증','테스트','껍데기','PASS','GitHub','배포','중간승인','떠넘','크레딧','누락','전달','받지','시작하지')
TOOL_RE=re.compile(r'(?:TOOL\s*0*(\d{1,3})|(?<!\d)(\d{1,3})번)')

def now(): return datetime.now(timezone.utc).isoformat()
def sid(path, n, text): return hashlib.sha256(f'{path}:{n}:{text}'.encode()).hexdigest()[:20]
def load_state():
    if STATE.exists(): return json.loads(STATE.read_text(encoding='utf-8'))
    return {'schema_version':1,'processed_files':{},'last_run':None}
def detect_tool(text, path):
    m=TOOL_RE.search(path+' '+text)
    if not m: return 'TOOL_UNCERTAIN'
    n=int(m.group(1) or m.group(2)); return f'TOOL{n:03d}'

def main():
    INPUT.mkdir(parents=True, exist_ok=True)
    state=load_state(); processed=state.setdefault('processed_files',{})
    occurrences=[]
    if OUT.exists():
        occurrences=[json.loads(x) for x in OUT.read_text(encoding='utf-8').splitlines() if x.strip()]
    known={o['occurrence_id'] for o in occurrences}
    files=[p for p in INPUT.rglob('*') if p.is_file() and p.suffix.lower() in {'.txt','.md','.json','.jsonl'}]
    for p in files:
        rel=p.relative_to(ROOT).as_posix(); raw=p.read_text(encoding='utf-8',errors='replace')
        digest=hashlib.sha256(raw.encode()).hexdigest()
        if processed.get(rel)==digest: continue
        for i,line in enumerate(raw.splitlines(),1):
            t=line.strip()
            if len(t)<4 or not any(k.lower() in t.lower() for k in ERROR_TERMS): continue
            oid=sid(rel,i,t)
            if oid in known: continue
            occurrences.append({'occurrence_id':oid,'source_id':rel,'source_chat':p.name,'tool_id':detect_tool(t,rel),'line':i,'original_feedback':t[:2000],'status':'STATUS_UNVERIFIED','root':'ROOT_UNVERIFIED','missing_capability':'MISSING_CAPABILITY_UNVERIFIED'})
            known.add(oid)
        processed[rel]=digest
    OUT.write_text('\n'.join(json.dumps(o,ensure_ascii=False) for o in occurrences)+('\n' if occurrences else ''),encoding='utf-8')
    unresolved=[o for o in occurrences if o['status']!='RESOLVED_VERIFIED']
    handoff={'schema_version':1,'source':'TOOL045','state':'EXTRACTED_READY_FOR_TOOL016_HANDOFF','updated_at':now(),'occurrence_count':len(occurrences),'records':unresolved}
    HANDOFF.write_text(json.dumps(handoff,ensure_ascii=False,indent=2),encoding='utf-8')
    state.update({'last_run':now(),'total_input_files':len(files),'processed_input_files':len(processed),'occurrence_count':len(occurrences),'handoff_state':'EXTRACTED_READY_FOR_TOOL016_HANDOFF'})
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(state,ensure_ascii=False))

if __name__=='__main__': main()
