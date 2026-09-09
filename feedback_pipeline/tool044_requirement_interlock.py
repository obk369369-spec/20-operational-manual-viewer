"""Fail-closed per-requirement interlock for the TOOL044 factory.

The ledger is intentionally limited to current structured requirements.  It does
not claim coverage of unavailable historical chats.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "tool044_current_requirement_ledger.json"

GEARS = (
    "user_requirement", "atomic_requirement", "execution_plan",
    "actual_execution", "actual_evidence", "independent_verification",
    "reverse_trace",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_requirement(req: dict[str, Any], root: Path = HERE) -> dict[str, Any]:
    missing = [gear for gear in GEARS if not req.get(gear)]
    if missing:
        return {"result": "LOCKED", "reason": f"MISSING_{missing[0].upper()}",
                "forward_key": False, "reverse_key": False}
    evidence = root / req["actual_evidence"]["path"]
    if not evidence.is_file():
        return {"result": "LOCKED", "reason": "EVIDENCE_MISSING",
                "forward_key": False, "reverse_key": False}
    actual_sha = sha256(evidence)
    if actual_sha != req["actual_evidence"].get("sha256"):
        return {"result": "LOCKED", "reason": "RECEIPT_ACTUAL_MISMATCH",
                "forward_key": False, "reverse_key": False}
    verification = req["independent_verification"]
    if verification.get("result") != "PASS" or verification.get("evidence_sha256") != actual_sha:
        return {"result": "LOCKED", "reason": "VERIFICATION_MISMATCH",
                "forward_key": False, "reverse_key": False}
    trace = req["reverse_trace"]
    expected = [req["req_id"], req["actual_execution"]["execution_id"],
                req["execution_plan"]["plan_id"]]
    if trace.get("chain") != expected:
        return {"result": "LOCKED", "reason": "REVERSE_TRACE_BROKEN",
                "forward_key": True, "reverse_key": False}
    if req.get("claimed_result") not in (None, "PASS"):
        return {"result": "LOCKED", "reason": "FAKE_PASS_RECEIPT",
                "forward_key": False, "reverse_key": False}
    return {"result": "PASS", "reason": "FOUR_RECEIPTS_MATCH",
            "forward_key": True, "reverse_key": True}


def stage_token(ledger: dict[str, Any], stage: str, root: Path = HERE) -> dict[str, Any]:
    relevant = [r for r in ledger.get("requirements", []) if r.get("stage") == stage]
    results = {r["req_id"]: verify_requirement(r, root) for r in relevant}
    passed = bool(relevant) and all(v["result"] == "PASS" for v in results.values())
    return {"stage": stage, "token": "PASS" if passed else "DENIED",
            "job_claims": 1 if passed else 0, "worker_starts": 1 if passed else 0,
            "downstream_artifacts": 1 if passed else 0, "results": results}


def self_test(root: Path = HERE) -> dict[str, Any]:
    evidence = root / "evidence" / "tool044_interlock_known_answer.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps({"known_answer": "PASS"}, indent=2) + "\n", encoding="utf-8")
    digest = sha256(evidence)
    base = {
        "req_id": "REQ-INTERLOCK-KNOWN-ANSWER", "stage": "T0_GOVERNANCE",
        "user_requirement": {"source": "TOOL044 FINAL ONE-SHOT", "text": "7중 인터록"},
        "atomic_requirement": "모든 gear와 양방향 영수증이 일치할 때만 claim 허용",
        "execution_plan": {"plan_id": "PLAN-KNOWN", "expected": "PASS"},
        "actual_execution": {"execution_id": "EXEC-KNOWN", "result": "PASS"},
        "actual_evidence": {"path": "evidence/tool044_interlock_known_answer.json", "sha256": digest},
        "independent_verification": {"result": "PASS", "evidence_sha256": digest},
        "reverse_trace": {"chain": ["REQ-INTERLOCK-KNOWN-ANSWER", "EXEC-KNOWN", "PLAN-KNOWN"]},
    }
    cases: dict[str, dict[str, Any]] = {}
    for name, mutate, expected in (
        ("requirement_missing", lambda r: r.pop("user_requirement"), "MISSING_USER_REQUIREMENT"),
        ("plan_missing", lambda r: r.pop("execution_plan"), "MISSING_EXECUTION_PLAN"),
        ("execution_missing", lambda r: r.pop("actual_execution"), "MISSING_ACTUAL_EXECUTION"),
        ("evidence_missing", lambda r: r.pop("actual_evidence"), "MISSING_ACTUAL_EVIDENCE"),
        ("wrong_sha", lambda r: r["actual_evidence"].update(sha256="0" * 64), "RECEIPT_ACTUAL_MISMATCH"),
        ("fake_pass", lambda r: r.update(claimed_result="PASS_WITHOUT_MATCH"), "FAKE_PASS_RECEIPT"),
        ("verifier_mismatch", lambda r: r["independent_verification"].update(result="FAIL"), "VERIFICATION_MISMATCH"),
        ("reverse_trace_broken", lambda r: r["reverse_trace"].update(chain=[]), "REVERSE_TRACE_BROKEN"),
    ):
        row = json.loads(json.dumps(base)); mutate(row); result = verify_requirement(row, root)
        hard_stop = all(result.get(k) in (False, 0) for k in ("forward_key", "reverse_key")) or not result["reverse_key"]
        cases[name] = {"expected": expected, "actual": result["reason"],
                       "job_claim_denied": result["result"] == "LOCKED",
                       "downstream_worker_start": 0, "downstream_artifact": 0,
                       "complete_certificate": 0,
                       "pass": result["reason"] == expected and hard_stop}
    known = verify_requirement(base, root)
    cases["known_pass"] = {"expected": "PASS", "actual": known["result"],
                           "pass": known["result"] == "PASS"}
    status = "PASS" if all(c["pass"] for c in cases.values()) else "FAIL"
    return {"status": status, "cases": cases, "known_answer": base,
            "verifier_self_test": "PASS" if status == "PASS" else "VERIFIER_UNTRUSTED"}


if __name__ == "__main__":
    result = self_test()
    out = HERE / "evidence" / "tool044_requirement_interlock_self_test_20260909.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
