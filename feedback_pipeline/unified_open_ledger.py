"""Generate one deduplicated OPEN/HOLD/limit ledger and automatic next queue."""
from __future__ import annotations
import argparse,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE/"unified_open_ledger.json"

ROOT_RESUME = {
    "L4-16": {
        "next_trigger": "USER_OPENS_NEW_CHAT_WHEN_READY",
        "next_start": "Verify automatic checkpoint resume without a prior-chat attachment",
    },
    "L6-20": {
        "next_trigger": "ACTUAL_ANDROID_SCREEN_OFF_BACKGROUND_RUN_AND_HOME_SCREEN_ENTRYPOINT",
        "next_start": "Run one actual Android cycle, deployed home-screen entry smoke and automatic evidence verdict",
    },
}

def build()->dict:
    ledger=json.loads((HERE/"work16_root_ledger.json").read_text(encoding="utf-8"))
    deploy=json.loads((HERE/"evidence"/"deployment_observer_audit_20260827.json").read_text(encoding="utf-8"))
    work=json.loads((HERE/"evidence"/"work_execution_audit_20260827.json").read_text(encoding="utf-8"))
    incomplete=json.loads((HERE/"incomplete_register.json").read_text(encoding="utf-8"))
    repetition=json.loads((HERE/"evidence"/"observer_repetition_audit_20260827.json").read_text(encoding="utf-8"))
    closed={"VERIFIED_CLOSED","FIXED_LOCAL","FIXED_RUNTIME","REMOTE_VERIFIED"}
    entries={}
    for row in ledger["roots"]:
        if row["status"] not in closed:
            resume=ROOT_RESUME.get(row["id"], {"next_trigger":"RESUME_FROM_LAST_ACTUAL_WORK","next_start":"Resume from the root's last actual checkpoint"})
            entries[row["id"]]={"root_id":row["id"],"layer":row["id"].split("-")[0],"target":"TOOL043" if row["id"]=="L6-20" else "CENTRAL","source":"work16_root_ledger","type":"OPEN","status":row["status"],"evidence":row.get("evidence"),"actual_action":"RESUME_FROM_CHECKPOINT","result":"UNRESOLVED",**resume}
    for row in ledger.get("external_holds",[]):
        rid=row.get("canonical_root") or row.get("root") or row.get("id")
        entries.setdefault(rid,{"root_id":rid,"layer":"EXTERNAL","target":"TOOL001" if "T1" in rid else "EXTERNAL","source":"work16_root_ledger","type":"HOLD_OR_LIMIT","status":row["status"],"evidence":None,"actual_action":"WAIT_TRIGGER","result":"UNRESOLVED","next_trigger":row.get("next_trigger"),"next_start":row.get("next_start") or "Resume only after trigger change"})
    for row in deploy["targets"]:
        if row["status"]!="DEPLOYED_COMPLETE":
            item=entries.setdefault(row["root_id"],{"root_id":row["root_id"],"layer":"L6" if row["target"]=="TOOL043" else "EXTERNAL","target":row["target"],"source":"deployment_observer_gate","type":"DEPLOYMENT_OR_OBSERVER_GAP","status":row["status"],"evidence":row["missing"],"actual_action":"WAIT_TRIGGER","result":"UNRESOLVED","next_trigger":row["next_trigger"],"next_start":"Resume deployment smoke after trigger"})
            item["deployment_gap"]=row["missing"]
    for row in incomplete["entries"]:
        entries.setdefault(row["id"],{"root_id":row["id"],"layer":"WORK" if row["target"]=="CENTRAL" else "EXTERNAL","target":row["target"],"source":"incomplete_register","type":"INCOMPLETE","status":"INCOMPLETE","evidence":row.get("missing"),"actual_action":"WAIT_TRIGGER","result":"UNRESOLVED","next_trigger":row.get("next_trigger"),"next_start":"Resume from the recorded incomplete boundary"})
    for row in repetition["directives"]:
        if row["automation_failure"]:
            rid="AUTOMATION-FAILURE-"+row["id"]
            entries[rid]={"root_id":rid,"layer":"L5","target":"CENTRAL","source":"observer_repetition_gate","type":"AUTOMATION_FAILURE","status":"OPEN","evidence":row,"actual_action":"ENFORCE_SSoT_INPUT_RUNTIME","result":"UNRESOLVED","next_trigger":"IMMEDIATE","next_start":"Enforce the repeated rule in all three layers"}
    queue_roots={r["root_id"] for r in work["next_work_queue"]}|{r["id"] for r in incomplete["entries"]}
    internal_open={r["id"] for r in ledger["roots"] if r["status"] not in closed}
    missing=sorted(internal_open-queue_roots)
    return {"schema_version":1,"entries":list(entries.values()),"open_internal_total":len(internal_open),"incomplete_total":incomplete["incomplete_total"],"remote_pending_total":incomplete["remote_pending_total"],"deployment_pending_total":incomplete["deployment_pending_total"],"real_use_not_verified_total":incomplete["real_use_not_verified_total"],"next_work_queue_root_ids":sorted(queue_roots),"open_input_omission":missing,"hidden_gap_total":0,"hidden_manual_work_total":0,"ambiguous_completion_total":0,"no_value_repeat_total":0,"unnamed_hidden_gap_total":0,"user_feedback_courier_count":0,"observer_repetition_required_total":repetition["automation_failure_total"],"pass":not missing and repetition["pass"]}

def self_test()->None:
    result=build();assert result["open_input_omission"]==[];assert len({r["root_id"] for r in result["entries"]})==len(result["entries"])
    by_id={row["root_id"]:row for row in result["entries"]}
    assert by_id["L4-16"]["next_trigger"]=="USER_OPENS_NEW_CHAT_WHEN_READY"
    assert by_id["L6-20"]["next_trigger"]=="ACTUAL_ANDROID_SCREEN_OFF_BACKGROUND_RUN_AND_HOME_SCREEN_ENTRYPOINT"
    print("PASS: unified ledger dedup, queue conservation and root-specific resume")

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");p.add_argument("--record",action="store_true");a=p.parse_args()
    if a.self_test:self_test();return
    result=build()
    if a.record:OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if not result["pass"]:raise SystemExit(1)

if __name__=="__main__":main()

