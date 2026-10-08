"""Small reusable fail-closed gate for all WIC execution shapes."""
from __future__ import annotations

from typing import Any


REQUIRED_CLOSURE_FIELDS = {
    "actual_input", "actual_output", "expected_output", "validation_pass",
    "positive_pass", "negative_pass", "failure_injection_pass",
    "recovery_pass", "rollback_pass", "evidence_ref", "readback_pass",
}


def verdict(receipt: dict[str, Any]) -> str:
    if receipt.get("repeat_blocked") is False or receipt.get("no_progress_stopped") is False:
        return "FAIL"
    status = str(receipt.get("status", "UNKNOWN"))
    if status in {"UNKNOWN", "PARTIAL"}:
        return "HOLD"
    if status == "FAIL" or receipt.get("validation_pass") is False:
        return "FAIL"
    total = receipt.get("total")
    checked = receipt.get("checked")
    if not isinstance(total, int) or not isinstance(checked, int) or checked < total:
        return "HOLD"
    if receipt.get("skipped", 0) or receipt.get("unresolved", 0):
        return "HOLD"
    if not receipt.get("evidence_ref") or not receipt.get("readback_pass"):
        return "HOLD"
    return "PASS"


def closure_verdict(receipt: dict[str, Any]) -> str:
    """Fail closed unless an execution receipt proves the complete shared contract."""
    if REQUIRED_CLOSURE_FIELDS.difference(receipt):
        return "HOLD"
    if receipt.get("actual_output") != receipt.get("expected_output"):
        return "FAIL"
    if not all(receipt.get(field) is True for field in (
        "validation_pass", "positive_pass", "negative_pass",
        "failure_injection_pass", "recovery_pass", "rollback_pass", "readback_pass"
    )):
        return "FAIL"
    return verdict({**receipt, "status": "VALIDATED", "total": 1, "checked": 1,
                    "skipped": 0, "unresolved": 0})


def promote_failure(failure: dict[str, Any]) -> dict[str, Any]:
    """Convert one concrete correction into a reusable rule, sample and hard gate."""
    required = {"failure_class", "root_cause", "bad_input", "expected_behavior", "scope"}
    missing = sorted(required.difference(failure))
    if missing:
        return {"status": "HOLD", "reason": "INCOMPLETE_FAILURE_CONTRACT", "missing": missing}
    key = f"{failure['failure_class']}::{failure['root_cause']}"
    return {
        "status": "PROMOTED",
        "promotion_key": key,
        "rule": {"id": key, "expected_behavior": failure["expected_behavior"]},
        "negative_golden_sample": {"input": failure["bad_input"], "must_be_blocked": True},
        "hard_gate": {"scope": failure["scope"], "fail_closed": True},
        "system_control_failure_on_repeat": True,
    }


def self_test() -> dict[str, Any]:
    cases = {
        "valid": ({"status": "VALIDATED", "total": 2, "checked": 2, "skipped": 0,
                   "unresolved": 0, "validation_pass": True, "evidence_ref": "e.json",
                   "readback_pass": True}, "PASS"),
        "partial": ({"status": "PARTIAL", "total": 2, "checked": 2, "evidence_ref": "e.json",
                     "readback_pass": True}, "HOLD"),
        "coverage_gap": ({"status": "VALIDATED", "total": 2, "checked": 1,
                          "evidence_ref": "e.json", "readback_pass": True}, "HOLD"),
        "missing_evidence": ({"status": "VALIDATED", "total": 1, "checked": 1,
                              "readback_pass": False}, "HOLD"),
        "validation_failure": ({"status": "VALIDATED", "total": 1, "checked": 1,
                                "validation_pass": False, "evidence_ref": "e.json",
                                "readback_pass": True}, "FAIL"),
    }
    actual = {name: verdict(payload) for name, (payload, _) in cases.items()}
    expected = {name: expected for name, (_, expected) in cases.items()}
    closure = {"actual_input": "x", "actual_output": "y", "expected_output": "y",
               "validation_pass": True, "positive_pass": True, "negative_pass": True,
               "failure_injection_pass": True, "recovery_pass": True,
               "rollback_pass": True, "evidence_ref": "e.json", "readback_pass": True}
    incomplete = dict(closure); incomplete.pop("rollback_pass")
    wrong = dict(closure); wrong["actual_output"] = "wrong"
    promotion = promote_failure({"failure_class": "DUPLICATE", "root_cause": "NO_PRELOOKUP",
        "bad_input": "same work twice", "expected_behavior": "BLOCK", "scope": "COMMON_PLATFORM"})
    extended = {"closure": closure_verdict(closure),
                "incomplete": closure_verdict(incomplete), "wrong": closure_verdict(wrong),
                "promotion": promotion["status"]}
    expected_extended = {"closure": "PASS", "incomplete": "HOLD",
                         "wrong": "FAIL", "promotion": "PROMOTED"}
    return {"pass": actual == expected and extended == expected_extended,
            "total": len(cases) + len(expected_extended), "checked": len(actual) + len(extended),
            "expected": {**expected, **expected_extended}, "actual": {**actual, **extended}}
