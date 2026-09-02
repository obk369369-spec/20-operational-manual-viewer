"""Keep code/remote/deployment/observer completion states distinct."""
from __future__ import annotations
import argparse, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
INPUT=HERE/"deployment_targets_20260827.json"
OUT=HERE/"evidence"/"deployment_observer_audit_20260827.json"
FIELDS=("implemented","actual_tested","remote_verified","deployed","deployed_smoke","observer_reachable")
RELEASE_FIELDS=("test_executed","test_input_recorded","expected_defined","actual_captured",
                "expected_actual_match","actual_business_input_e2e","final_output_verified",
                "regression_passed","pass_evidence_recorded","github_published","remote_readback",
                "local_canonical_deployed","deployed_canonical_e2e","real_use_pass")
BLOCKING_SENTINELS=("ROW_ZERO","UNKNOWN","EMPTY_OUTPUT","MID_PROCESS_STALL","HIDDEN_ERROR",
                    "BUTTON_NO_RESPONSE","PREVIEW_MISSING","DOWNLOAD_FAILED","INPUT_MISSING",
                    "DATA_MIXED","EXPECTED_MISMATCH")

def evaluate(row:dict)->dict:
    required=FIELDS + (RELEASE_FIELDS if row.get("release_gate_required", False) else ())
    missing=[key for key in required if row.get(key) is not True]
    blockers=[value for value in row.get("release_blockers", []) if value in BLOCKING_SENTINELS]
    if row.get("test_failed") is True and row.get("same_failed_input_retested") is not True:
        missing.append("same_failed_input_retested")
    if blockers: missing.append("release_blockers_clear")
    if not missing: status="DEPLOYED_COMPLETE"
    elif row.get("external_dependency"): status="VERIFIED_EXTERNAL_LIMIT"
    else: status="IMPLEMENTED_NOT_DEPLOYED"
    return {"target":row["target"],"root_id":row["root_id"],**{k:bool(row.get(k)) for k in required},"release_blockers":blockers,"missing":missing,"status":status,"next_trigger":row.get("external_dependency")}

def audit(doc:dict)->dict:
    rows=[evaluate(r) for r in doc["targets"]]
    return {"schema_version":1,"targets":rows,"implemented_not_deployed_total":sum(r["status"]=="IMPLEMENTED_NOT_DEPLOYED" for r in rows),"external_limit_total":sum(r["status"]=="VERIFIED_EXTERNAL_LIMIT" for r in rows),"observer_intent_gap_total":sum(not r["observer_reachable"] for r in rows),"pass":not any(r["status"]=="IMPLEMENTED_NOT_DEPLOYED" for r in rows)}

def self_test()->None:
    complete={"target":"OK","root_id":"R1","release_gate_required":True,**{k:True for k in FIELDS+RELEASE_FIELDS}}
    incomplete=dict(complete,target="BAD",root_id="R2",deployed=False)
    external=dict(incomplete,target="EXT",root_id="R3",external_dependency="DEVICE")
    blocked=dict(complete,target="BLOCKED",root_id="R4",release_blockers=["ROW_ZERO"])
    result=audit({"targets":[complete,incomplete,external,blocked]})
    assert result["targets"][0]["status"]=="DEPLOYED_COMPLETE"
    assert result["targets"][1]["status"]=="IMPLEMENTED_NOT_DEPLOYED"
    assert result["targets"][2]["status"]=="VERIFIED_EXTERNAL_LIMIT"
    assert result["targets"][3]["status"]=="IMPLEMENTED_NOT_DEPLOYED"
    for field in ("test_executed","test_input_recorded","expected_defined","actual_captured",
                  "expected_actual_match","regression_passed","pass_evidence_recorded"):
        row=dict(complete,target=field,root_id="R-"+field);row[field]=False
        checked=evaluate(row)
        assert checked["status"]=="IMPLEMENTED_NOT_DEPLOYED" and field in checked["missing"]
    print("PASS: deployment and observer intent fail-closed fixtures")

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");p.add_argument("--record",action="store_true");a=p.parse_args()
    if a.self_test:self_test();return
    result=audit(json.loads(INPUT.read_text(encoding="utf-8")))
    if a.record:OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if not result["pass"]:raise SystemExit(1)

if __name__=="__main__":main()
