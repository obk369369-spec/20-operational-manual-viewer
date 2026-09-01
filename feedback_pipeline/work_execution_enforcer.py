"""Fail-closed audit for observer directives and actual Work execution."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from evidence_classification_gate import audit_targets

HERE = Path(__file__).resolve().parent
TARGETS = HERE / "work_execution_targets_20260827.json"
REPORT = HERE / "evidence" / "work_execution_audit_20260827.json"
FINAL = {"ACTUALLY_FIXED", "ACTUALLY_TESTED", "VERIFIED_SKIP", "FAIL", "HOLD_EVIDENCE", "EXTERNAL_ESCALATION", "PLATFORM_LIMIT"}
RELEASE_FIELDS = ("regression_passed", "actual_business_input_e2e", "final_output_verified",
                  "same_failed_input_retested", "github_published", "remote_readback",
                  "local_canonical_deployed", "deployed_canonical_e2e", "real_use_pass")
RELEASE_SEQUENCE = ("MODIFIED", "REGRESSION_PASSED", "ACTUAL_INPUT_E2E_PASSED",
                    "FINAL_OUTPUT_VERIFIED", "GITHUB_PUBLISHED", "REMOTE_READBACK_PASSED",
                    "LOCAL_CANONICAL_DEPLOYED", "DEPLOYED_CANONICAL_RETEST_PASSED", "COMPLETE")


def preflight_attempt(candidate: dict, ledger: dict) -> dict:
    """Before Work eligibility; authority and receipts come from CENTRAL, not candidate flags."""
    def stop(decision, reason):
        return {"decision": decision, "reason": reason, "execution_allowed": False,
                "missing_handoff": []}
    root = candidate.get('root_id')
    rows = ledger.get('entries', ledger.get('roots', []))
    row = next((r for r in rows if (r.get('root_id') or r.get('id')) == root), None)
    if row is None:
        return stop('WORK_HOLD_SCOPE', 'Unregistered root; record OPEN/HOLD before selection')
    operation = candidate.get('operation_id')
    if not operation:
        return stop('WORK_HOLD_OPERATION_REQUIRED', 'Exact operation identity required')
    receipts = row.get('execution_receipts', [])
    same = [r for r in receipts if r.get('operation_id') == operation]
    completed = {'PASS', 'VERIFIED', 'REMOTE_VERIFIED', 'VERIFIED_CLOSED', 'VERIFIED_SKIP'}
    if row.get('status') in completed or any(r.get('status') in completed for r in same):
        return stop('SKIP_REUSE', 'Canonical completed evidence; do not execute again')
    trigger = row.get('next_trigger')
    if trigger and trigger not in {'IMMEDIATE', 'NONE'}:
        proof = row.get('trigger_release', {})
        if (proof.get('trigger') != trigger or not proof.get('evidence_ref')
                or not proof.get('previous_fingerprint') or not proof.get('current_fingerprint')
                or proof['previous_fingerprint'] == proof['current_fingerprint']):
            return stop('SKIP_NO_VALUE', 'HOLD condition has no canonical changed-condition evidence')
    for prior in same:
        if str(prior.get('status', '')).startswith('HOLD') or prior.get('status') == 'SKIP_NO_VALUE':
            release = row.get('trigger_release', {})
            if (not release.get('evidence_ref') or not release.get('current_fingerprint')
                    or release.get('previous_fingerprint') != prior.get('condition_fingerprint')
                    or release.get('current_fingerprint') == prior.get('condition_fingerprint')):
                return stop('SKIP_NO_VALUE', 'Prior held operation has no changed-condition receipt')
        if prior.get('status') == 'FAIL':
            if not candidate.get('cause_id') or not candidate.get('method_id'):
                return stop('WORK_HOLD_FAILURE_IDENTITY', 'Failure cause and method required')
            if (prior.get('cause_id'), prior.get('method_id')) == (candidate['cause_id'], candidate['method_id']):
                return stop('SKIP_NO_VALUE', 'Same failed cause and method')
    policy = ledger.get('execution_policy', {})
    grants = policy.get('scope_grants', [])
    grant = next((g for g in grants if g.get('root_id') == root
                  and g.get('directive_ref') == candidate.get('directive_ref')), None)
    if not grant or not grant.get('directive_ref'):
        return stop('WORK_HOLD_SCOPE', 'No canonical current scoped authorization')
    action = candidate.get('action')
    assets = candidate.get('target_assets')
    if (action not in grant.get('actions', []) or not assets
            or not set(assets).issubset(set(grant.get('assets', [])))):
        return stop('WORK_HOLD_SCOPE', 'Action/assets exceed authorized scope')
    if action.startswith('CREATE_'):
        if (not grant.get('explicit_new_structure') or not grant.get('existing_structure_infeasible_evidence')
                or grant.get('reusable_assets')):
            return stop('WORK_HOLD_REUSE_REQUIRED', 'Creation requires explicit approval and evidenced infeasibility')
    elif not grant.get('reusable_assets'):
        return stop('WORK_HOLD_REUSE_REQUIRED', 'Locate existing assets before repair')
    return {'decision': 'ATTEMPT_ALLOWED', 'execution_allowed': True,
            'reason': 'Scoped incremental work; lower-cost/handoff gates still required'}


def audit(data: dict) -> dict:
    rows = data["targets"]
    anomalies: list[dict] = []
    queue: list[dict] = []
    hold_registry = json.loads((HERE / "evidence_hold_registry.json").read_text(encoding="utf-8"))
    evidence_gate = audit_targets(data, hold_registry)
    anomalies.extend(evidence_gate["errors"])
    for row in rows:
        target = row["target"]
        status = row.get("final_status", "")
        worked = bool(row.get("actual_work") or row.get("verified_skip_evidence"))
        modified = row.get("modification_occurred")
        smoke = bool(row.get("actual_smoke", {}).get("result") in {"PASS", "FAIL", "HOLD"})
        if not worked:
            anomalies.append({"target": target, "kind": "NOT_WORKED"})
        if row.get("actual_work") and not isinstance(modified, bool):
            anomalies.append({"target": target, "kind": "MODIFICATION_DECLARATION_MISSING"})
        if row.get("actual_smoke_required", True) and not smoke:
            anomalies.append({"target": target, "kind": "ACTUAL_SMOKE_MISSING"})
        if status not in FINAL:
            anomalies.append({"target": target, "kind": "FINAL_STATUS_MISSING"})
        if status in {"ACTUALLY_FIXED", "ACTUALLY_TESTED"} and not smoke:
            anomalies.append({"target": target, "kind": "UNVERIFIED_RESULT"})
        if modified is True or status == "ACTUALLY_FIXED" or row.get("changed_files"):
            release = row.get("release_gate", {})
            missing = [field for field in RELEASE_FIELDS if release.get(field) is not True]
            sequence = tuple(row.get("release_sequence", ()))
            if sequence != RELEASE_SEQUENCE:
                missing.append("release_sequence")
            if missing or release.get("blockers") or status not in {"ACTUALLY_FIXED", "ACTUALLY_TESTED"}:
                anomalies.append({"target": target, "kind": "DEPLOY_INCOMPLETE", "missing": missing,
                                  "blockers": release.get("blockers", [])})
        unresolved = status in {"", "FAIL", "HOLD_EVIDENCE", "EXTERNAL_ESCALATION"} or any(a["target"] == target for a in anomalies)
        if unresolved:
            queue.append({
                "target": target,
                "root_id": row["root_id"],
                "last_actual_point": row.get("last_actual_point", "TARGET_REGISTERED"),
                "failed_approach": row.get("failed_approach", "NONE"),
                "next_trigger": row.get("next_trigger", "RESUME_FROM_LAST_ACTUAL_POINT"),
            })
    counts = {
        "work_target_total": len(rows),
        "actually_worked": sum(bool(r.get("actual_work") or r.get("verified_skip_evidence")) for r in rows),
        "not_worked_total": sum(a["kind"] == "NOT_WORKED" for a in anomalies),
        "actual_smoke_missing_total": sum(a["kind"] == "ACTUAL_SMOKE_MISSING" for a in anomalies),
        "premature_exit_total": sum(a["kind"] == "FINAL_STATUS_MISSING" for a in anomalies),
        "partial_work_total": sum(r.get("final_status") == "PARTIAL_WORK" for r in rows),
        "unverified_result_total": sum(a["kind"] == "UNVERIFIED_RESULT" for a in anomalies),
        "post_work_anomaly_total": len(anomalies),
    }
    return {"schema_version": 1, "counts": counts, "evidence_classification": evidence_gate, "anomalies": anomalies, "next_work_queue": queue, "execution_quality_pass": not anomalies, "overall_complete": not anomalies and not queue}


def self_test() -> None:
    fixture = {"targets": [
        {"target": "OK", "root_id": "R1", "evidence_gate":{"classification":"C"}, "actual_work": True, "modification_occurred": True, "actual_smoke": {"result": "PASS"}, "final_status": "ACTUALLY_TESTED", "release_gate":{k:True for k in RELEASE_FIELDS}, "release_sequence": list(RELEASE_SEQUENCE)},
        {"target": "MISS", "root_id": "R2", "evidence_gate":{"classification":"D"}, "actual_work": False, "actual_smoke": {}, "final_status": ""},
        {"target": "ORDER", "root_id": "R3", "evidence_gate":{"classification":"C"}, "actual_work": True, "modification_occurred": True, "actual_smoke": {"result": "PASS"}, "final_status": "ACTUALLY_TESTED", "release_gate":{k:True for k in RELEASE_FIELDS}, "release_sequence": list(reversed(RELEASE_SEQUENCE))},
        {"target": "UNDECLARED", "root_id": "R4", "evidence_gate":{"classification":"C"}, "actual_work": True, "actual_smoke": {"result": "PASS"}, "final_status": "ACTUALLY_TESTED"},
    ]}
    result = audit(fixture)
    assert not result["execution_quality_pass"]
    assert result["counts"]["not_worked_total"] == 1
    assert result["counts"]["actual_smoke_missing_total"] == 1
    assert result["next_work_queue"][0]["root_id"] == "R2"
    assert any(a["target"] == "ORDER" and a["kind"] == "DEPLOY_INCOMPLETE" for a in result["anomalies"])
    assert any(a["target"] == "UNDECLARED" and a["kind"] == "MODIFICATION_DECLARATION_MISSING" for a in result["anomalies"])
    print("PASS: work execution fail-closed audit")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = audit(json.loads(TARGETS.read_text(encoding="utf-8")))
    if args.record:
        REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
