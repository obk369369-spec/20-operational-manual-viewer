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
PHASE5_FIELDS=("runtime_gate_executed","runtime_receipt_recorded",
               "actual_use_receipt_recorded","canonical_receipt_recorded",
               "deployed_receipt_recorded","canonical_deployed_match",
               "provenance_verified","impact_scope_defined",
               "impacted_regression_passed","normal_case_regression_passed")
GOVERNOR_FIELDS=("current_stable_checked","candidate_identity_verified",
                 "independent_test_passed","negative_failure_passed",
                 "artifact_identity_match","product_scope_verified",
                 "final_product_usable")
EXTERNAL_PRODUCT_FIELDS=("actual_business_input_recorded","external_execution_id_recorded",
                         "output_file_recorded","output_reopened","functional_validation_passed",
                         "wic_repeat_execution_passed","remote_evidence_readback_passed")
EXTERNAL_PRODUCT_STAGES=("DISCOVERED","CONNECTED","EXECUTED","VERIFIED","DEPLOYED_COMPLETE")
BLOCKING_SENTINELS=("ROW_ZERO","UNKNOWN","EMPTY_OUTPUT","MID_PROCESS_STALL","HIDDEN_ERROR",
                    "BUTTON_NO_RESPONSE","PREVIEW_MISSING","DOWNLOAD_FAILED","INPUT_MISSING",
                    "DATA_MIXED","EXPECTED_MISMATCH")

def evaluate(row:dict)->dict:
    required=FIELDS + (RELEASE_FIELDS if row.get("release_gate_required", False) else ())
    if row.get("phase5_gate_required", False): required += PHASE5_FIELDS
    if row.get("release_governor_required", False): required += GOVERNOR_FIELDS
    if row.get("external_product_gate_required", False): required += EXTERNAL_PRODUCT_FIELDS
    missing=[key for key in required if row.get(key) is not True]
    blockers=[value for value in row.get("release_blockers", []) if value in BLOCKING_SENTINELS]
    if row.get("test_failed") is True and row.get("same_failed_input_retested") is not True:
        missing.append("same_failed_input_retested")
    if blockers: missing.append("release_blockers_clear")
    if row.get("external_product_gate_required", False):
        claimed=str(row.get("lifecycle_stage","DISCOVERED"))
        if claimed not in EXTERNAL_PRODUCT_STAGES:
            missing.append("valid_lifecycle_stage")
        achieved="DISCOVERED"
        if row.get("connected") is True: achieved="CONNECTED"
        if row.get("actual_business_input_recorded") is True and row.get("external_execution_id_recorded") is True: achieved="EXECUTED"
        if achieved=="EXECUTED" and row.get("output_file_recorded") is True and row.get("output_reopened") is True and row.get("functional_validation_passed") is True: achieved="VERIFIED"
        if not missing: achieved="DEPLOYED_COMPLETE"
        if EXTERNAL_PRODUCT_STAGES.index(claimed) > EXTERNAL_PRODUCT_STAGES.index(achieved):
            missing.append("lifecycle_evidence_gap")
    else:
        achieved=None
    if not missing: status="DEPLOYED_COMPLETE"
    elif row.get("external_dependency"): status="VERIFIED_EXTERNAL_LIMIT"
    else: status="IMPLEMENTED_NOT_DEPLOYED"
    return {"target":row["target"],"root_id":row["root_id"],**{k:bool(row.get(k)) for k in required},"release_blockers":blockers,"missing":missing,"status":status,"lifecycle_stage":achieved,"next_trigger":row.get("external_dependency")}

def audit(doc:dict)->dict:
    rows=[evaluate(r) for r in doc["targets"]]
    incomplete=sum(r["status"]=="IMPLEMENTED_NOT_DEPLOYED" for r in rows)
    external=sum(r["status"]=="VERIFIED_EXTERNAL_LIMIT" for r in rows)
    return {"schema_version":1,"targets":rows,"implemented_not_deployed_total":incomplete,"external_limit_total":external,"observer_intent_gap_total":sum(not r["observer_reachable"] for r in rows),"pass":incomplete==0 and external==0}

def self_test()->None:
    complete={"target":"OK","root_id":"R1","release_gate_required":True,
              "phase5_gate_required":True,"release_governor_required":True,
              **{k:True for k in FIELDS+RELEASE_FIELDS+PHASE5_FIELDS+GOVERNOR_FIELDS}}
    incomplete=dict(complete,target="BAD",root_id="R2",deployed=False)
    external=dict(incomplete,target="EXT",root_id="R3",external_dependency="DEVICE")
    blocked=dict(complete,target="BLOCKED",root_id="R4",release_blockers=["ROW_ZERO"])
    result=audit({"targets":[complete,incomplete,external,blocked]})
    assert result["targets"][0]["status"]=="DEPLOYED_COMPLETE"
    assert result["targets"][1]["status"]=="IMPLEMENTED_NOT_DEPLOYED"
    assert result["targets"][2]["status"]=="VERIFIED_EXTERNAL_LIMIT"
    assert result["external_limit_total"]==1 and result["pass"] is False
    assert result["targets"][3]["status"]=="IMPLEMENTED_NOT_DEPLOYED"
    for field in ("test_executed","test_input_recorded","expected_defined","actual_captured",
                  "expected_actual_match","regression_passed","pass_evidence_recorded",*PHASE5_FIELDS):
        row=dict(complete,target=field,root_id="R-"+field);row[field]=False
        checked=evaluate(row)
        assert checked["status"]=="IMPLEMENTED_NOT_DEPLOYED" and field in checked["missing"]
    # Recovered phase-1..4 failure shapes: every mutation must fail closed.
    past_failures={
        "MASTER_NOT_CALLED": "runtime_gate_executed",
        "SYNTHETIC_ONLY_FALSE_ACTUAL_PASS": "actual_use_receipt_recorded",
        "CANONICAL_NOT_DEPLOYED_COPY": "canonical_deployed_match",
        "SOURCE_UNVERIFIED_VALUE_GENERATED": "provenance_verified",
        "PARTIAL_TEST_FALSE_WHOLE_PASS": "impacted_regression_passed",
    }
    for name,field in past_failures.items():
        mutated=dict(complete,target=name,root_id="PAST-"+name);mutated[field]=False
        checked=evaluate(mutated)
        assert checked["status"]=="IMPLEMENTED_NOT_DEPLOYED" and field in checked["missing"]
    release_escapes={
        "UNVERIFIED_CANDIDATE": "independent_test_passed",
        "REGRESSION_FAILURE": "regression_passed",
        "NO_ACTUAL_E2E": "actual_business_input_e2e",
        "ARTIFACT_IDENTITY_MISMATCH": "artifact_identity_match",
        "PARTIAL_PASS_AS_PRODUCT_PASS": "product_scope_verified",
    }
    for name,field in release_escapes.items():
        mutated=dict(complete,target=name,root_id="GOVERNOR-"+name);mutated[field]=False
        checked=evaluate(mutated)
        assert checked["status"]=="IMPLEMENTED_NOT_DEPLOYED" and field in checked["missing"]
    external_product=dict(complete,target="EXTERNAL_PRODUCT",root_id="R-EXTERNAL",
                          external_product_gate_required=True,lifecycle_stage="DEPLOYED_COMPLETE",
                          connected=True,**{k:True for k in EXTERNAL_PRODUCT_FIELDS})
    assert evaluate(external_product)["status"]=="DEPLOYED_COMPLETE"
    for stage,field in (("CONNECTED","actual_business_input_recorded"),("EXECUTED","output_file_recorded"),
                        ("VERIFIED","wic_repeat_execution_passed")):
        product=dict(external_product,lifecycle_stage="DEPLOYED_COMPLETE");product[field]=False
        checked=evaluate(product)
        assert checked["status"]=="IMPLEMENTED_NOT_DEPLOYED" and checked["lifecycle_stage"]==stage
    assert evaluate(complete)["status"]=="DEPLOYED_COMPLETE"
    print("PASS: DEVELOPMENT_RELEASE_GOVERNOR; 5 release escapes blocked; valid product release allowed")

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");p.add_argument("--record",action="store_true");a=p.parse_args()
    if a.self_test:self_test();return
    result=audit(json.loads(INPUT.read_text(encoding="utf-8")))
    if a.record:OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if not result["pass"]:raise SystemExit(1)

if __name__=="__main__":main()
