#!/usr/bin/env python3
"""Canonical TOOL016/044 -> Work parallel handoff and no-conflict claim gate."""
from __future__ import annotations
import argparse,json,hashlib
from datetime import datetime,timezone,timedelta
from pathlib import Path

HERE=Path(__file__).resolve().parent
QUEUE=HERE/"tool044_atomic_demand_queue.json"
STATE=HERE/"evidence"/"tool044_work_parallel_state.json"
REQUIRED_PACKAGE=("ROOT_ID","CURRENT_STATE","EXACT_ERROR","COMMON_CAUSE","EXPECTED","FILES_TO_CHANGE","FILES_NOT_TO_TOUCH","EXISTING_PASS_TO_REUSE","DEPENDENCIES","ACCEPTANCE_TEST","DEPLOY_TARGET","CHECKPOINT")
TERMINAL={"PASS","COMPLETED","SATISFIED_BY_COMMON_COMPONENT","SKIP_REUSE_VERIFIED_PASS"}
def terminal(row):
    status=str(row.get("status",""))
    return status in TERMINAL or status.startswith("PASS_") or status.startswith("SKIP_REUSE_VERIFIED_PASS")

def load(p,d):
    try:return json.loads(Path(p).read_text(encoding="utf-8"))
    except (FileNotFoundError,json.JSONDecodeError):return d
def save(p,o):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+".tmp");t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");t.replace(p)
def active(d,now):
    c=d.get("claim") or {}; exp=c.get("lease_expiry")
    if not c.get("owner"): return False
    if not exp:return True
    try:return datetime.fromisoformat(exp.replace("Z","+00:00"))>now
    except ValueError:return True
def assets(d):return set(d.get("files_to_change") or d.get("FILES_TO_CHANGE") or [])
def claim(queue,demand_id,owner,lease_minutes=30):
    now=datetime.now(timezone.utc)
    d=next(x for x in queue["demands"] if x.get("demand_id")==demand_id)
    if active(d,now) and d["claim"]["owner"]!=owner:return {"decision":"ACTIVE_ELSEWHERE","owner":d["claim"]["owner"]}
    for other in queue["demands"]:
        if other is d or not active(other,now):continue
        if assets(d)&assets(other):return {"decision":"ACTIVE_ELSEWHERE","owner":other["claim"]["owner"],"reason":"ASSET_LOCK"}
    d["claim"]={"owner":owner,"claimed_at":now.isoformat(),"lease_expiry":(now+timedelta(minutes=lease_minutes)).isoformat()}
    d["status"]="CLAIMED";d.setdefault("checkpoint",{"stage":"CLAIMED","resume_from":"CLAIMED"})
    return {"decision":"CLAIMED","owner":owner}
def compress(rows):
    groups={}
    for r in rows:
        if terminal(r) or r.get("status")=="SUPERSEDED":continue
        k=(r.get("target_tool"),r.get("root_id",r.get("demand_id")))
        groups.setdefault(k,[]).append(r)
    out=[]
    for (tool,root),xs in groups.items():
        out.append({"ROOT_ID":root,"CURRENT_STATE":xs[0].get("status","OPEN"),
          "EXACT_ERROR":[x.get("exact_error") or x.get("latest_directive") or x.get("demand_id") for x in xs],
          "COMMON_CAUSE":next((x.get("common_cause") for x in xs if x.get("common_cause")), "ROOT_COMPRESSED"),
          "EXPECTED":next((x.get("expected") for x in xs if x.get("expected")), "Resolve root without regression"),
          "FILES_TO_CHANGE":sorted(set().union(*(assets(x) for x in xs))),
          "FILES_NOT_TO_TOUCH":sorted(set().union(*(set(x.get("files_not_to_touch",[])) for x in xs))),
          "EXISTING_PASS_TO_REUSE":[x.get("demand_id") for x in rows if terminal(x)],
          "DEPENDENCIES":sorted(set().union(*(set(x.get("dependencies",[])) for x in xs))),
          "ACCEPTANCE_TEST":next((x.get("acceptance_test") for x in xs if x.get("acceptance_test")), "EXPECTED_ACTUAL_AND_REGRESSION"),
          "DEPLOY_TARGET":tool or "CENTRAL","CHECKPOINT":xs[0].get("checkpoint") or {"stage":"INTAKE","resume_from":"INTAKE"},
          "atomic_demand_ids":[x.get("demand_id") for x in xs]})
    return out
def validate_package(p):return [k for k in REQUIRED_PACKAGE if k not in p]
def self_test():
    now=datetime.now(timezone.utc);q={"demands":[
      {"demand_id":"A","root_id":"R1","target_tool":"TOOL044","status":"OPEN","files_to_change":["a.py"]},
      {"demand_id":"B","root_id":"R1","target_tool":"TOOL044","status":"OPEN","files_to_change":["b.py"]},
      {"demand_id":"C","root_id":"R2","target_tool":"TOOL013","status":"OPEN","files_to_change":["c.py"]},
      {"demand_id":"P","root_id":"RP","target_tool":"TOOL006","status":"PASS"}]}
    packs=compress(q["demands"]);assert len(packs)==2 and all(not validate_package(x) for x in packs)
    assert claim(q,"A","WORK")["decision"]=="CLAIMED"
    assert claim(q,"A","TOOL044")["decision"]=="ACTIVE_ELSEWHERE"
    assert claim(q,"C","TOOL044")["decision"]=="CLAIMED"
    q["demands"].append({"demand_id":"D","root_id":"R3","target_tool":"TOOL007","status":"OPEN","files_to_change":["a.py"]})
    assert claim(q,"D","RUNNER3")["decision"]=="ACTIVE_ELSEWHERE"
    return {"ROOT_COMPRESSION_PASS":"PASS","CROSS_RUNNER_CLAIM_PASS":"PASS","NO_DUPLICATE_EXECUTION_PASS":"PASS","WORK_PACKAGE_PASS":"PASS"}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--self-test",action="store_true");ap.add_argument("--packages",action="store_true");a=ap.parse_args()
    if a.self_test:print(json.dumps(self_test(),sort_keys=True));return
    if a.packages:
      q=load(QUEUE,{"demands":[]});o={"generated_at":datetime.now(timezone.utc).isoformat(),"packages":compress(q.get("demands",[]))}
      save(STATE,o);print(json.dumps({"packages":len(o["packages"])}));return
    ap.error("choose mode")
if __name__=="__main__":main()
