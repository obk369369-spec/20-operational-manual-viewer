"""Small reusable fail-closed gate for all WIC execution shapes."""
from __future__ import annotations

from typing import Any


def verdict(receipt: dict[str, Any]) -> str:
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
    return {"pass": actual == expected, "total": len(cases), "checked": len(actual),
            "expected": expected, "actual": actual}
