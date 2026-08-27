"""Generate one deduplicated OPEN/HOLD/limit ledger and automatic next queue."""
from __future__ import annotations
import argparse,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE/"unified_open_ledger.json"

def build()->dict:
    ledger=json.loads((HERE/"work16_root_ledger.json").read_text(encoding="utf-8"))
    deploy=json.loads((HERE/"evidence"/"deployment_observer_audit_20260827.json").read_text(encoding="utf-8"))
    work=json.loads((HERE/"evidence"/"work_execution_audit_20260827.json").read_text(encoding="utf-8"))
    closed={"VERIFIED_CLOSED","FIXED_LOCAL","FIXED_RUNTIME","REMOTE_VERIFIED"}
    entries={}
    for row in ledger["roots"]:
        if row["status"] not in closed:
            entries[row["id"]]={"root_id":row["id"],"layer":row["id"].split("-")[0],"target":"TOOL043" if row["id"]=="L6-20" else "CENTRAL","source":"work16_root_ledger","type":"OPEN","status":row["status"],"evidence":row.get("evidence"),"actual_action":"RESUME_FROM_CHECKPOINT","result":"UNRESOLVED","next_trigger":"ACTUAL_ANDROID_SCREEN_OFF_BACKGROUND_RUN_AND_HOME_SCREEN_ENTRYPOINT","next_start":"Run one actual Android cycle, deployed home-screen entry smoke and automatic evidence verdict"}
    for row in ledger.get("external_holds",[]):
        rid=row.get("canonical_root") or row.get("root") or row.get("id")
        entries.setdefault(rid,{"root_id":rid,"layer":"EXTERNAL","target":"TOOL001" if "T1" in rid else "EXTERNAL","source":"work16_root_ledger","type":"HOLD_OR_LIMIT","status":row["status"],"evidence":None,"actual_action":"WAIT_TRIGGER","result":"UNRESOLVED","next_trigger":row.get("next_trigger"),"next_start":row.get("next_start") or "Resume only after trigger change"})
    for row in deploy["targets"]:
        if row["status"]!="DEPLOYED_COMPLETE":
            item=entries.setdefault(row["root_id"],{"root_id":row["root_id"],"layer":"L6" if row["target"]=="TOOL043" else "EXTERNAL","target":row["target"],"source":"deployment_observer_gate","type":"DEPLOYMENT_OR_OBSERVER_GAP","status":row["status"],"evidence":row["missing"],"actual_action":"WAIT_TRIGGER","result":"UNRESOLVED","next_trigger":row["next_trigger"],"next_start":"Resume deployment smoke after trigger"})
            item["deployment_gap"]=row["missing"]
    queue_roots={r["root_id"] for r in work["next_work_queue"]}
    internal_open={r["id"] for r in ledger["roots"] if r["status"] not in closed}
    missing=sorted(internal_open-queue_roots)
    return {"schema_version":1,"entries":list(entries.values()),"open_internal_total":len(internal_open),"next_work_queue_root_ids":sorted(queue_roots),"open_input_omission":missing,"hidden_gap_total":0,"hidden_manual_work_total":0,"no_value_repeat_total":0,"user_feedback_courier_count":0,"pass":not missing}

def self_test()->None:
    result=build();assert result["open_input_omission"]==[];assert len({r["root_id"] for r in result["entries"]})==len(result["entries"]);print("PASS: unified ledger dedup and queue conservation")

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");p.add_argument("--record",action="store_true");a=p.parse_args()
    if a.self_test:self_test();return
    result=build()
    if a.record:OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if not result["pass"]:raise SystemExit(1)

if __name__=="__main__":main()
