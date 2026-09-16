"""Deterministic WIC Work admission gate. Fail closed unless the current waste-prevention manual is read and scanned."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

REQUIRED_HANDOFF = (
    "blocker", "restart_point", "target_repository", "target_assets",
    "execution_goal", "success_evidence", "rollback_point",
)


def _waste_gate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Mandatory first gate for every candidate; no other admission logic may bypass it."""
    from work_credit_waste_start_gate import enforce_start
    result = enforce_start(candidate)
    if not result.get("allowed"):
        return {**result, "execution_allowed": False, "missing_handoff": []}
    return result


def evaluate_candidate(candidate: Mapping[str, Any], ledger=None) -> dict[str, Any]:
    waste = _waste_gate(candidate)
    if not waste.get("allowed"):
        return waste

    from work_execution_enforcer import preflight_attempt
    if ledger is None:
        try:
            ledger = json.loads((Path(__file__).parent / "unified_open_ledger.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"decision": "WORK_HOLD_CENTRAL_UNAVAILABLE", "execution_allowed": False,
                    "reason": "Canonical execution state unavailable", "missing_handoff": []}
    preflight = preflight_attempt(dict(candidate), ledger)
    if not preflight["execution_allowed"]:
        return preflight

    gates = candidate.get("gates", {})
    required_gates = ("chat_files", "github", "ordinary_runtime")
    missing_gates = [k for k in required_gates if k not in gates or not isinstance(gates.get(k), bool)]
    if missing_gates:
        return {"decision": "WORK_HOLD_INVALID_GATES", "execution_allowed": False,
                "reason": "Every lower-cost gate must be present as an explicit boolean.",
                "missing_handoff": [], "missing_gates": missing_gates}
    if any(bool(gates[k]) for k in required_gates):
        return {"decision": "WORK_DEFER_DENIED", "execution_allowed": False,
                "reason": "At least one lower-cost execution lane remains available.", "missing_handoff": []}

    missing = [k for k in REQUIRED_HANDOFF if candidate.get(k) in (None, "", [], {})]
    if missing:
        return {"decision": "WORK_HOLD_INCOMPLETE_HANDOFF", "execution_allowed": False,
                "reason": "All lower-cost lanes are unavailable, but exact handoff is incomplete.",
                "missing_handoff": missing}
    return {"decision": "WORK_ELIGIBLE", "execution_allowed": True,
            "reason": "Mandatory waste gate passed; lower-cost lanes unavailable; exact handoff complete.",
            "missing_handoff": [], "waste_manual_sha256": waste["sha256"]}


def load_latest_resume(candidate=None) -> dict[str, Any]:
    """Resume is also an entrance: no candidate means no execution; candidate must pass the same gate."""
    if candidate is None:
        return {"status": "RESUME_LOADED", "work_admission": {"decision": "WORK_HOLD_CANDIDATE_REQUIRED"},
                "execution_allowed": False}
    result = evaluate_candidate(candidate)
    return {"status": "RESUME_LOADED", "work_admission": result,
            "execution_allowed": result.get("decision") == "WORK_ELIGIBLE"}


def build_handoff(state: Mapping[str, Any]) -> dict[str, Any]:
    candidates = state.get("work_gate_candidates", {})
    evaluated = {}
    eligible, deferred, held = [], [], []
    for lane, candidate in candidates.items():
        result = evaluate_candidate(candidate)
        evaluated[lane] = {**candidate, **result}
        if result["decision"] == "WORK_ELIGIBLE": eligible.append(lane)
        elif result["decision"] == "WORK_DEFER_DENIED": deferred.append(lane)
        else: held.append(lane)
    return {"schema_version": 3, "eligible_work_lanes": eligible,
            "deferred_lower_cost_lanes": deferred, "held_lanes": held,
            "candidate_count": len(candidates), "candidates": evaluated,
            "waste_gate": "MANDATORY_FAIL_CLOSED"}


def self_test() -> None:
    from work_credit_waste_start_gate import manual_receipt
    receipt = manual_receipt()
    assert receipt["allowed"], receipt
    # 1) manual not acknowledged => blocked before all other gates
    r = evaluate_candidate({})
    assert r["decision"] == "WORK_HOLD_WASTE_MANUAL_NOT_READ" and not r["execution_allowed"]
    # 2) manual read but scan absent => blocked
    r = evaluate_candidate({"waste_manual_read_sha256": receipt["sha256"]})
    assert r["decision"] == "WORK_HOLD_WASTE_SCAN_REQUIRED" and not r["execution_allowed"]
    # 3) current manual + scan reaches normal admission logic (not waste-blocked)
    r = evaluate_candidate({"waste_manual_read_sha256": receipt["sha256"],
                            "waste_instruction_scan_passed": True})
    assert r["decision"] != "WORK_HOLD_WASTE_MANUAL_NOT_READ"
    assert r["decision"] != "WORK_HOLD_WASTE_SCAN_REQUIRED"
    print("PASS: all Work admission paths enforce current waste manual first")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--resume-latest", action="store_true")
    p.add_argument("--candidate", default="")
    args = p.parse_args()
    if args.self_test:
        self_test(); return
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8")) if args.candidate else None
    if args.resume_latest:
        result = load_latest_resume(candidate)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result["execution_allowed"] else 2)
    print(json.dumps(build_handoff({"work_gate_candidates": {}}), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
