"""Keep code/remote/deployment/observer completion states distinct."""
from __future__ import annotations
import argparse, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
INPUT=HERE/"deployment_targets_20260827.json"
OUT=HERE/"evidence"/"deployment_observer_audit_20260827.json"
FIELDS=("implemented","actual_tested","remote_verified","deployed","deployed_smoke","observer_reachable")

def evaluate(row:dict)->dict:
    missing=[key for key in FIELDS if row.get(key) is not True]
    if not missing: status="DEPLOYED_COMPLETE"
    elif row.get("external_dependency"): status="VERIFIED_EXTERNAL_LIMIT"
    else: status="IMPLEMENTED_NOT_DEPLOYED"
    return {"target":row["target"],"root_id":row["root_id"],**{k:bool(row.get(k)) for k in FIELDS},"missing":missing,"status":status,"next_trigger":row.get("external_dependency")}

def audit(doc:dict)->dict:
    rows=[evaluate(r) for r in doc["targets"]]
    return {"schema_version":1,"targets":rows,"implemented_not_deployed_total":sum(r["status"]=="IMPLEMENTED_NOT_DEPLOYED" for r in rows),"external_limit_total":sum(r["status"]=="VERIFIED_EXTERNAL_LIMIT" for r in rows),"observer_intent_gap_total":sum(not r["observer_reachable"] for r in rows),"pass":not any(r["status"]=="IMPLEMENTED_NOT_DEPLOYED" for r in rows)}

def self_test()->None:
    complete={"target":"OK","root_id":"R1",**{k:True for k in FIELDS}}
    incomplete=dict(complete,target="BAD",root_id="R2",deployed=False)
    external=dict(incomplete,target="EXT",root_id="R3",external_dependency="DEVICE")
    result=audit({"targets":[complete,incomplete,external]})
    assert result["targets"][0]["status"]=="DEPLOYED_COMPLETE"
    assert result["targets"][1]["status"]=="IMPLEMENTED_NOT_DEPLOYED"
    assert result["targets"][2]["status"]=="VERIFIED_EXTERNAL_LIMIT"
    print("PASS: deployment and observer intent fail-closed fixtures")

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");p.add_argument("--record",action="store_true");a=p.parse_args()
    if a.self_test:self_test();return
    result=audit(json.loads(INPUT.read_text(encoding="utf-8")))
    if a.record:OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if not result["pass"]:raise SystemExit(1)

if __name__=="__main__":main()
