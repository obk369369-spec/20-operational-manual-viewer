"""Fail-closed Work execution preflight. Every execution path must pass the current waste-manual gate first."""
from __future__ import annotations


def preflight_attempt(candidate: dict, ledger: dict) -> dict:
    # Execution enforcer is a second independent entrance guard. Even if a caller
    # bypasses work_gate_handoff.evaluate_candidate, execution still fails closed.
    from work_credit_waste_start_gate import enforce_start
    waste = enforce_start(candidate)
    if not waste.get("allowed"):
        return {**waste, "execution_allowed": False, "missing_handoff": []}

    def stop(decision, reason):
        return {"decision": decision, "reason": reason, "execution_allowed": False, "missing_handoff": []}

    root = candidate.get("root_id")
    rows = ledger.get("entries", ledger.get("roots", []))
    row = next((r for r in rows if (r.get("root_id") or r.get("id")) == root), None)
    if row is None:
        return stop("WORK_HOLD_SCOPE", "Unregistered root; record OPEN/HOLD before selection")
    operation = candidate.get("operation_id")
    if not operation:
        return stop("WORK_HOLD_OPERATION_REQUIRED", "Exact operation identity required")
    receipts = row.get("execution_receipts", [])
    same = [r for r in receipts if r.get("operation_id") == operation]
    completed = {"PASS", "VERIFIED", "REMOTE_VERIFIED", "VERIFIED_CLOSED", "VERIFIED_SKIP"}
    if row.get("status") in completed or any(r.get("status") in completed for r in same):
        return stop("SKIP_REUSE", "Canonical completed evidence; do not execute again")
    trigger = row.get("next_trigger")
    if trigger and trigger not in {"IMMEDIATE", "NONE"}:
        proof = row.get("trigger_release", {})
        if (proof.get("trigger") != trigger or not proof.get("evidence_ref")
                or not proof.get("previous_fingerprint") or not proof.get("current_fingerprint")
                or proof["previous_fingerprint"] == proof["current_fingerprint"]):
            return stop("SKIP_NO_VALUE", "HOLD condition has no canonical changed-condition evidence")
    for prior in same:
        if str(prior.get("status", "")).startswith("HOLD") or prior.get("status") == "SKIP_NO_VALUE":
            release = row.get("trigger_release", {})
            if (not release.get("evidence_ref") or not release.get("current_fingerprint")
                    or release.get("previous_fingerprint") != prior.get("condition_fingerprint")
                    or release.get("current_fingerprint") == prior.get("condition_fingerprint")):
                return stop("SKIP_NO_VALUE", "Prior held operation has no changed-condition receipt")
        if prior.get("status") == "FAIL":
            if not candidate.get("cause_id") or not candidate.get("method_id"):
                return stop("WORK_HOLD_FAILURE_IDENTITY", "Failure cause and method required")
            if (prior.get("cause_id"), prior.get("method_id")) == (candidate["cause_id"], candidate["method_id"]):
                return stop("SKIP_NO_VALUE", "Same failed cause and method")
    policy = ledger.get("execution_policy", {})
    grants = policy.get("scope_grants", [])
    grant = next((g for g in grants if g.get("root_id") == root
                  and g.get("directive_ref") == candidate.get("directive_ref")), None)
    if not grant or not grant.get("directive_ref"):
        return stop("WORK_HOLD_SCOPE", "No canonical current scoped authorization")
    action = candidate.get("action")
    assets = candidate.get("target_assets")
    if action not in grant.get("actions", []) or not assets or not set(assets).issubset(set(grant.get("assets", []))):
        return stop("WORK_HOLD_SCOPE", "Action/assets exceed authorized scope")
    if action.startswith("CREATE_"):
        if (not grant.get("explicit_new_structure") or not grant.get("existing_structure_infeasible_evidence")
                or grant.get("reusable_assets")):
            return stop("WORK_HOLD_REUSE_REQUIRED", "Creation requires explicit approval and evidenced infeasibility")
    elif not grant.get("reusable_assets"):
        return stop("WORK_HOLD_REUSE_REQUIRED", "Locate existing assets before repair")
    return {"decision": "ATTEMPT_ALLOWED", "execution_allowed": True,
            "reason": "Waste-manual gate passed; scoped incremental work allowed",
            "waste_manual_sha256": waste["sha256"]}


def self_test() -> None:
    from work_credit_waste_start_gate import manual_receipt
    receipt = manual_receipt(); assert receipt["allowed"], receipt
    ledger = {"entries": []}
    # direct execution bypass attempt must still be blocked
    assert preflight_attempt({}, ledger)["decision"] == "WORK_HOLD_WASTE_MANUAL_NOT_READ"
    assert preflight_attempt({"waste_manual_read_sha256": receipt["sha256"]}, ledger)["decision"] == "WORK_HOLD_WASTE_SCAN_REQUIRED"
    passed = preflight_attempt({"waste_manual_read_sha256": receipt["sha256"],
                                "waste_instruction_scan_passed": True}, ledger)
    assert passed["decision"] == "WORK_HOLD_SCOPE"
    print("PASS: direct Work execution cannot bypass waste-manual gate")


if __name__ == "__main__":
    self_test()
