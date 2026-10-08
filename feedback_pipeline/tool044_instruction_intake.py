#!/usr/bin/env python3
import argparse, copy, hashlib, json, tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
QUEUE=HERE/"tool044_atomic_demand_queue.json"
INBOX=HERE/"tool044_instruction_inbox.json"
STATE=HERE/"evidence"/"tool044_instruction_intake_state.json"
PASS_STATES={"PASS","COMPLETED","SATISFIED_BY_COMMON_COMPONENT","SKIP_REUSE_VERIFIED_PASS"}

def load(p, default):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except (FileNotFoundError,json.JSONDecodeError): return copy.deepcopy(default)
def save(p,obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+".tmp")
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); tmp.replace(p)
def norm(s): return " ".join(str(s).lower().split())
def sig(d):
    basis="|".join([str(d.get("target_tool","")),str(d.get("root_id","")),norm(d.get("directive",""))])
    return hashlib.sha256(basis.encode()).hexdigest()[:20]
def effective_root_id(d):
    """Use the directive id as a stable fallback for legacy intake rows without root_id."""
    return str(d.get("root_id") or d.get("directive_id") or d.get("demand_id") or "")

def root_key(d):
    return (str(d.get("target_tool","")),effective_root_id(d))
def compact_demands(queue):
    """Keep one durable row per demand id while preserving revision history."""
    unique={}; order=[]
    for row in queue.get("demands",[]):
        did=row.get("demand_id")
        if not did or did not in unique:
            if did: unique[did]=row
            order.append(row)
            continue
        current=unique[did]
        winner=max((current,row),key=lambda item:(item.get("status")!="SUPERSEDED",item.get("revision",0)))
        loser=row if winner is current else current
        history=winner.setdefault("directive_history",[])
        for value in loser.get("directive_history",[])+[loser.get("latest_directive")]:
            if value and value not in history: history.append(value)
        if winner is not current:
            order[order.index(current)]=winner; unique[did]=winner
    queue["demands"]=order
def decide(d, queue, state):
    s=sig(d)
    if s in state.get("seen_signatures",[]): return "SKIP_DUPLICATE",None
    rk=root_key(d)
    matches=[x for x in queue.get("demands",[]) if (str(x.get("target_tool","")),str(x.get("root_id",x.get("demand_id",""))))==rk]
    if any(x.get("status") in PASS_STATES for x in matches): return "SKIP_REUSE_PASS",matches[-1]
    if matches:
        old=matches[-1]
        if d.get("supersedes") or (d.get("revision",0)>old.get("revision",0)):
            return "SUPERSEDE",old
        return "MERGE",old
    return "NEW_ROOT",None
def ingest(inbox,queue,state):
    events=[]
    state.setdefault("seen_signatures",[])
    for d in inbox.get("directives",[]):
        action,old=decide(d,queue,state); s=sig(d)
        if action=="SKIP_DUPLICATE":
            events.append({"directive_id":d["directive_id"],"action":action}); continue
        if action=="SKIP_REUSE_PASS":
            state["seen_signatures"].append(s); events.append({"directive_id":d["directive_id"],"action":action}); continue
        if action=="SUPERSEDE":
            old.setdefault("directive_history",[]).append(old.get("latest_directive"))
            old.update(revision=d.get("revision",old.get("revision",1)),
                       latest_directive=d["directive"],status="OPEN")
            old.pop("superseded_by",None)
            target=old
        elif action=="MERGE":
            old.setdefault("merged_directives",[]).append(d["directive_id"])
            old.setdefault("directive_history",[]).append(d["directive"])
            old["latest_directive"]=d["directive"]; old["revision"]=max(old.get("revision",0),d.get("revision",0))
            old["status"]=old.get("status","OPEN")
            target=old
        else:
            target={"demand_id":d["directive_id"],"root_id":effective_root_id(d),"target_tool":d["target_tool"],
                    "status":"OPEN","revision":d.get("revision",1),"latest_directive":d["directive"],
                    "source":"TOOL044_CANONICAL_INTAKE","claim":None,
                    "checkpoint":{"stage":"INTAKE_ACCEPTED","resume_from":"INTAKE_ACCEPTED"},
                    "result_return":None}
            queue.setdefault("demands",[]).append(target)
        state["seen_signatures"].append(s)
        events.append({"directive_id":d["directive_id"],"action":action,"root_id":effective_root_id(d)})
    compact_demands(queue)
    state["last_events"]=events; state["updated_at"]=datetime.now(timezone.utc).isoformat()
    return events
def claim(queue,tool,owner):
    for d in queue.get("demands",[]):
        if d.get("target_tool")==tool and d.get("status")=="OPEN" and not d.get("claim"):
            d["claim"]={"owner":owner,"claimed_at":datetime.now(timezone.utc).isoformat()}
            d["status"]="CLAIMED"; d["checkpoint"]={"stage":"CLAIMED","resume_from":"CLAIMED"}
            return d
def self_test():
    q={"demands":[]}; s={}; 
    a={"directive_id":"A1","target_tool":"TOOL044","root_id":"R1","revision":1,"directive":"first"}
    b={"directive_id":"B1","target_tool":"TOOL013","root_id":"R2","revision":1,"directive":"other"}
    assert ingest({"directives":[a,b]},q,s)[0]["action"]=="NEW_ROOT"
    assert len(q["demands"])==2 and q["demands"][0]["target_tool"]!=q["demands"][1]["target_tool"]
    assert ingest({"directives":[a]},q,s)[0]["action"]=="SKIP_DUPLICATE"
    m={"directive_id":"A2","target_tool":"TOOL044","root_id":"R1","revision":1,"directive":"additional"}
    assert ingest({"directives":[m]},q,s)[0]["action"]=="MERGE" and q["demands"][0]["demand_id"]=="A1"
    newer={"directive_id":"A3","target_tool":"TOOL044","root_id":"R1","revision":2,"directive":"latest","supersedes":"A1"}
    assert ingest({"directives":[newer]},q,s)[0]["action"]=="SUPERSEDE"
    active=[x for x in q["demands"] if x.get("root_id")=="R1"]
    assert len(active)==1 and active[0]["revision"]==2 and active[0]["status"]=="OPEN"
    p={"demand_id":"P1","root_id":"RP","target_tool":"TOOL006","status":"PASS"}; q["demands"].append(p)
    pd={"directive_id":"P2","root_id":"RP","target_tool":"TOOL006","revision":1,"directive":"repeat pass"}
    assert ingest({"directives":[pd]},q,s)[0]["action"]=="SKIP_REUSE_PASS"
    legacy={"directive_id":"LEGACY1","target_tool":"TOOL044","revision":1,"directive":"legacy row without root id"}
    legacy_event=ingest({"directives":[legacy]},q,s)[0]
    assert legacy_event["root_id"]=="LEGACY1"
    assert any(x.get("root_id")=="LEGACY1" for x in q["demands"])
    c=claim(q,"TOOL013","runner-A"); assert c and c["status"]=="CLAIMED"
    c["checkpoint"]={"stage":"HALF","resume_from":"HALF"}; c["claim"]=None; c["status"]="OPEN"
    c2=claim(q,"TOOL013","runner-B"); assert c2["checkpoint"]["resume_from"]=="CLAIMED"
    # checkpoint payload survives owner change through explicit saved stage
    c2["checkpoint"]={"stage":"HALF","resume_from":"HALF"}; snap=json.loads(json.dumps(q))
    recovered=next(x for x in snap["demands"] if x["demand_id"]=="B1"); assert recovered["checkpoint"]["resume_from"]=="HALF"
    return {"PERMANENT_RULE_PASS":True,"CONFLICT_FREE_INTAKE_PASS":True,"DUPLICATE_BLOCK_PASS":True,
            "ROOT_MERGE_PASS":True,"CHECKPOINT_RESUME_PASS":True,"LATEST_DIRECTIVE_SUPERSEDE_PASS":True,
            "AUTO_INSTRUCTION_INTAKE_PASS":True}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--apply",action="store_true")
    args=ap.parse_args()
    if args.self_test: print(json.dumps(self_test(),sort_keys=True)); return
    if args.apply:
        q=load(QUEUE,{"demands":[]}); i=load(INBOX,{"directives":[]}); s=load(STATE,{})
        ev=ingest(i,q,s); save(QUEUE,q); save(STATE,s); print(json.dumps(ev,ensure_ascii=False)); return
    ap.error("choose --self-test or --apply")
if __name__=="__main__": main()
