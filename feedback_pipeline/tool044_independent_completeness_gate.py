"""Independent fail-closed completeness accounting for TOOL044.

This verifier does not trust a producer's aggregate PASS claim. It reads every
requirement receipt, checks its artifact, and performs reverse reconciliation.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tool044_requirement_interlock import HERE, verify_requirement


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(
    requirements: list[dict[str, Any]], root: Path,
    evidence_catalog: list[str], changes: list[dict[str, Any]],
) -> dict[str, Any]:
    requirement_ids = [row.get("req_id") for row in requirements]
    duplicate_requirement_ids = sorted({x for x in requirement_ids if requirement_ids.count(x) > 1})
    valid: list[str] = []
    referenced: set[str] = set()
    seven_interlock_pass = 0
    for row in requirements:
        evidence = row.get("actual_evidence", {}).get("path")
        if evidence:
            referenced.add(evidence)
        result = verify_requirement(row, root)
        if result.get("result") == "PASS":
            valid.append(row["req_id"])
            seven_interlock_pass += 1
    orphan_requirements = sorted(set(requirement_ids) - set(valid))
    catalog = set(evidence_catalog)
    orphan_evidence = sorted(catalog - referenced)
    missing_catalog_evidence = sorted(referenced - catalog)
    untested_changes = sorted(
        row["change_id"] for row in changes if not row.get("test_pass")
    )
    undeployed_changes = sorted(
        row["change_id"] for row in changes
        if row.get("test_pass") and not row.get("deployed_copy_pass")
    )
    total = len(requirements)
    blockers = {
        "duplicate_requirement_ids": duplicate_requirement_ids,
        "orphan_requirements": orphan_requirements,
        "orphan_evidence": orphan_evidence,
        "missing_catalog_evidence": missing_catalog_evidence,
        "untested_changes": untested_changes,
        "undeployed_changes": undeployed_changes,
    }
    complete = (
        total > 0
        and len(valid) == total
        and seven_interlock_pass == total
        and all(not value for value in blockers.values())
    )
    return {
        "COMPLETE_CERTIFICATE": "PASS" if complete else "BLOCKED",
        "TOTAL_REQUIREMENTS": total,
        "REQUIREMENTS_WITH_VALID_EVIDENCE": len(valid),
        "SEVEN_INTERLOCK_PASS_COUNT": seven_interlock_pass,
        "ORPHAN_REQUIREMENTS": len(orphan_requirements),
        "ORPHAN_EVIDENCE": len(orphan_evidence),
        "UNTESTED_CHANGES": len(untested_changes),
        "UNDEPLOYED_CHANGES": len(undeployed_changes),
        "UNACCOUNTED_REQUIREMENTS": len(orphan_requirements),
        "NON_TIME_DEPENDENT_INCOMPLETE": len(orphan_requirements),
        "ZERO_SCAN": "PASS" if complete else "BLOCKED",
        "blockers": blockers,
    }


def current_scope(root: Path = HERE) -> dict[str, Any]:
    ledger = _read(root / "tool044_current_requirement_ledger.json")
    final_scope = _read(root / "tool044_final_scope_requirements.json")
    requirements = list(ledger["requirements"])
    for row in final_scope["requirements"]:
        requirements.append({
            "req_id": row["req_id"], "stage": "FINAL_ONE_SHOT",
            "user_requirement": {"source": final_scope["scope_id"], "section": row["name"]},
            "atomic_requirement": row["name"],
        })
    catalog = sorted({
        row["actual_evidence"]["path"] for row in requirements
        if row.get("actual_evidence", {}).get("path")
    })
    result = evaluate(requirements, root, catalog, [])
    result.update({
        "scope_id": final_scope["scope_id"],
        "starting_queue_sha256": final_scope["starting_queue_sha256"],
        "out_of_scope": final_scope["out_of_scope"],
        "time_bound_exceptions": final_scope["time_bound_exceptions"],
    })
    return result


def self_test(root: Path = HERE) -> dict[str, Any]:
    evidence_rel = "evidence/tool044_interlock_known_answer.json"
    evidence = root / evidence_rel
    from tool044_requirement_interlock import sha256
    digest = sha256(evidence)

    def requirement(req_id: str) -> dict[str, Any]:
        return {
            "req_id": req_id, "stage": "SELF_TEST",
            "user_requirement": {"source": "SELF_TEST", "section": req_id},
            "atomic_requirement": req_id,
            "execution_plan": {"plan_id": f"PLAN-{req_id}", "expected": "PASS"},
            "actual_execution": {"execution_id": f"EXEC-{req_id}", "result": "PASS"},
            "actual_evidence": {"path": evidence_rel, "sha256": digest},
            "independent_verification": {"result": "PASS", "evidence_sha256": digest},
            "reverse_trace": {"chain": [req_id, f"EXEC-{req_id}", f"PLAN-{req_id}"]},
        }

    good = requirement("REQ-GOOD")
    normal = evaluate([good], root, [evidence_rel], [
        {"change_id": "CHANGE-GOOD", "test_pass": True, "deployed_copy_pass": True}
    ])
    fixture_a = evaluate([good, {"req_id": "REQ-MISSING"}], root, [evidence_rel], [])
    fixture_b = evaluate([good], root, [evidence_rel, "evidence/orphan.json"], [])
    fixture_c = evaluate([good], root, [evidence_rel], [
        {"change_id": "CHANGE-NOT-DEPLOYED", "test_pass": True, "deployed_copy_pass": False}
    ])
    checks = {
        "normal_complete_pass": normal["COMPLETE_CERTIFICATE"] == "PASS",
        "missing_requirement_blocks": fixture_a["COMPLETE_CERTIFICATE"] == "BLOCKED"
            and fixture_a["ORPHAN_REQUIREMENTS"] == 1,
        "orphan_evidence_blocks": fixture_b["COMPLETE_CERTIFICATE"] == "BLOCKED"
            and fixture_b["ORPHAN_EVIDENCE"] == 1,
        "undeployed_change_blocks": fixture_c["COMPLETE_CERTIFICATE"] == "BLOCKED"
            and fixture_c["UNDEPLOYED_CHANGES"] == 1,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "normal": normal,
        "fixture_a_missing_requirement": fixture_a,
        "fixture_b_orphan_evidence": fixture_b,
        "fixture_c_undeployed_change": fixture_c,
    }


if __name__ == "__main__":
    test = self_test()
    current = current_scope()
    output = {"gate_self_test": test, "current_scope": current}
    target = HERE / "evidence" / "tool044_independent_completeness_gate_20260910.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"self_test": test["status"], "current_scope": current}, ensure_ascii=False))
    raise SystemExit(0 if test["status"] == "PASS" else 1)
