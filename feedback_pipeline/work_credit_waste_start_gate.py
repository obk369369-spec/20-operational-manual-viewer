"""Fail-closed Work startup gate for the mandatory credit-waste prevention manual."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
MANUAL = HERE / "WIC_WORK_CREDIT_WASTE_PREVENTION_MANUAL.md"
REQUIRED_MARKERS = (
    "상태: ACTIVE / REQUIRED",
    "WASTE_INSTRUCTION_SCAN",
    "ONE_ROOT_ONE_PUSH = FORBIDDEN",
    "ONE_ROOT_ONE_CLOUD_RUN = FORBIDDEN",
    "ONE_ROOT_ONE_READBACK = FORBIDDEN",
    "STOP_DUPLICATE_REMOTE_ACTION",
    "STOP_LOW_CLOSURE_DENSITY",
)


def manual_receipt() -> dict[str, Any]:
    """Read the mandatory manual now. Missing/corrupt manual fails closed."""
    try:
        raw = MANUAL.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        return {"allowed": False, "decision": "WORK_HOLD_WASTE_MANUAL_UNREADABLE", "reason": str(exc)}
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    if missing:
        return {"allowed": False, "decision": "WORK_HOLD_WASTE_MANUAL_INVALID", "missing_markers": missing}
    return {
        "allowed": True,
        "decision": "WASTE_MANUAL_READ",
        "path": str(MANUAL.name),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def enforce_start(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Work cannot start unless this exact manual revision was read and acknowledged."""
    receipt = manual_receipt()
    if not receipt.get("allowed"):
        return receipt
    supplied = str(candidate.get("waste_manual_read_sha256", ""))
    acknowledged = candidate.get("waste_instruction_scan_passed") is True
    if supplied != receipt["sha256"]:
        return {
            "allowed": False,
            "decision": "WORK_HOLD_WASTE_MANUAL_NOT_READ",
            "reason": "Read the current mandatory manual and supply its exact SHA-256 before Work starts.",
            "required_sha256": receipt["sha256"],
        }
    if not acknowledged:
        return {
            "allowed": False,
            "decision": "WORK_HOLD_WASTE_SCAN_REQUIRED",
            "reason": "WASTE_INSTRUCTION_SCAN must pass before Work starts.",
            "required_sha256": receipt["sha256"],
        }
    return {**receipt, "decision": "WORK_WASTE_GATE_PASS"}


def self_test() -> None:
    receipt = manual_receipt()
    assert receipt["allowed"], receipt
    assert enforce_start({})["decision"] == "WORK_HOLD_WASTE_MANUAL_NOT_READ"
    assert enforce_start({"waste_manual_read_sha256": receipt["sha256"]})["decision"] == "WORK_HOLD_WASTE_SCAN_REQUIRED"
    assert enforce_start({"waste_manual_read_sha256": receipt["sha256"], "waste_instruction_scan_passed": True})["decision"] == "WORK_WASTE_GATE_PASS"
    print("PASS: mandatory Work waste-manual start gate")


if __name__ == "__main__":
    self_test()
