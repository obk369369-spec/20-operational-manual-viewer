"""Classify no-evidence claims and block redundant HOLD research."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGETS = HERE / "work_execution_targets_20260827.json"
HOLDS = HERE / "evidence_hold_registry.json"
REPORT = HERE / "evidence" / "evidence_classification_audit_20260827.json"
CLASSES = {"A", "B", "C", "D"}
A_REQUIRED = ("missing_evidence", "search_scope_already_checked", "last_search_checkpoint", "next_trigger", "next_start")


def fingerprint(gate: dict) -> str:
    body = {key: gate.get(key) for key in A_REQUIRED}
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def evaluate(row: dict, hold_registry: dict) -> dict:
    gate = row.get("evidence_gate")
    if not gate:
        return {"target": row["target"], "classification": None, "action": "UNCLASSIFIED", "errors": ["UNCLASSIFIED_NO_EVIDENCE"]}
    classification = gate.get("classification")
    errors: list[str] = []
    action = ""
    if classification not in CLASSES:
        return {"target": row["target"], "classification": classification, "action": "UNCLASSIFIED", "errors": ["UNCLASSIFIED_NO_EVIDENCE"]}
    if classification == "A":
        missing = [key for key in A_REQUIRED if not gate.get(key)]
        if missing: errors.append("FALSE_EVIDENCE_HOLD:" + ",".join(missing))
        prior = hold_registry.get(row["target"])
        if not prior or prior.get("fingerprint") != fingerprint(gate): errors.append("HOLD_TRIGGER_NOT_CHECKED")
        trigger_observed = bool(gate.get("trigger_observed"))
        if prior and not trigger_observed and gate.get("recovery_attempted"):
            errors.append("REDUNDANT_HOLD_RESEARCH")
        action = "RECOVERY" if trigger_observed else "SKIP_WAITING_FOR_TRIGGER"
    elif classification == "B":
        if not gate.get("recovery_scope") or gate.get("recovery_performed") is not True:
            errors.append("EVIDENCE_RECOVERY_BYPASS")
        action = "RECOVERY"
    elif classification == "C":
        if row.get("actual_smoke", {}).get("result") not in {"PASS", "FAIL"}:
            errors.append("FALSE_EVIDENCE_HOLD")
        action = "ACTUAL_SMOKE"
    else:
        if row.get("actual_work") or row.get("verified_skip_evidence"):
            errors.append("WORK_EVIDENCE_CLASSIFICATION_FALSE")
        action = "NOT_WORKED_FAIL"
        errors.append("WORK_EVIDENCE_MISSING")
    return {"target":row["target"],"classification":classification,"action":action,"errors":errors,"hold_fingerprint":fingerprint(gate) if classification == "A" else None}


def audit_targets(document: dict, hold_registry: dict) -> dict:
    results = [evaluate(row, hold_registry) for row in document["targets"]]
    errors = [{"target": row["target"], "kind": err} for row in results for err in row["errors"]]
    counts = {key: sum(row["classification"] == key for row in results) for key in CLASSES}
    counts.update({"unclassified":sum(row["classification"] not in CLASSES for row in results),"redundant_hold_research":sum(err["kind"] == "REDUNDANT_HOLD_RESEARCH" for err in errors)})
    return {"schema_version":1,"counts":counts,"results":results,"errors":errors,"pass":not errors}


def self_test() -> None:
    base_a = {"classification":"A","missing_evidence":"real payload","search_scope_already_checked":["one"],"last_search_checkpoint":"abc","next_trigger":"NEW_FILE","next_start":"resume","trigger_observed":False,"recovery_attempted":False}
    registry = {"A":{"fingerprint":fingerprint(base_a)}}
    rows = {"targets":[
        {"target":"A","evidence_gate":base_a,"actual_work":False},
        {"target":"B","evidence_gate":{"classification":"B","recovery_scope":["one"],"recovery_performed":True},"actual_work":True},
        {"target":"C","evidence_gate":{"classification":"C"},"actual_work":True,"actual_smoke":{"result":"PASS"}},
        {"target":"D","evidence_gate":{"classification":"D"},"actual_work":False},
    ]}
    result = audit_targets(rows, registry)
    assert result["counts"] == {"A":1,"B":1,"C":1,"D":1,"unclassified":0,"redundant_hold_research":0}
    assert any(e["kind"] == "WORK_EVIDENCE_MISSING" for e in result["errors"])
    repeat = dict(base_a, recovery_attempted=True)
    assert "REDUNDANT_HOLD_RESEARCH" in evaluate({"target":"A","evidence_gate":repeat}, registry)["errors"]
    assert "UNCLASSIFIED_NO_EVIDENCE" in evaluate({"target":"U"}, {})["errors"]
    bad_c = evaluate({"target":"C","evidence_gate":{"classification":"C"},"actual_smoke":{"result":"HOLD"}}, {})
    assert "FALSE_EVIDENCE_HOLD" in bad_c["errors"]
    print("PASS: A/B/C/D, unclassified, false-HOLD and redundant-research gates")


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--self-test",action="store_true"); parser.add_argument("--record",action="store_true"); args=parser.parse_args()
    if args.self_test: self_test(); return
    result=audit_targets(json.loads(TARGETS.read_text(encoding="utf-8")),json.loads(HOLDS.read_text(encoding="utf-8")))
    if args.record: REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if not result["pass"]: raise SystemExit(1)


if __name__ == "__main__": main()
