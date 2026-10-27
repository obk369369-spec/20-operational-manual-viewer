"""Small reusable fail-closed gate for all WIC execution shapes."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any, Callable, Iterable


REQUIRED_CLOSURE_FIELDS = {
    "actual_input", "actual_output", "expected_output", "validation_pass",
    "positive_pass", "negative_pass", "failure_injection_pass",
    "recovery_pass", "rollback_pass", "evidence_ref", "readback_pass",
}


def stable_record_id(record: dict[str, Any]) -> str:
    """Return a reproducible identity without relying on machine-specific paths."""
    origin_file = str(record.get("origin_file", "")).strip().replace("\\", "/")
    origin_row = str(record.get("origin_row", "")).strip()
    if not origin_file or not origin_row:
        raise ValueError("origin_file and origin_row are required")
    return sha256(f"{origin_file}\0{origin_row}".encode("utf-8")).hexdigest()


def enforce_record_isolation(
    records: Iterable[dict[str, Any]],
    validator: Callable[[dict[str, Any]], bool | dict[str, Any]],
    repairer: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None,
    *,
    allowed_repair_fields: set[str] | None = None,
) -> dict[str, Any]:
    """Validate, repair once, revalidate, or quarantine while preserving identity.

    ``repairer`` is deliberately invoked at most once per invalid record.  Callers
    may return validation metadata (``{"valid": bool, ...}``); it is retained in
    the per-record evidence so an adapter does not need a second, private retry
    loop.  Callback failures are fail-closed and isolated to the affected record.
    Identity or protected-field mutations remain output-wide integrity failures.
    """
    allowed = set(allowed_repair_fields or ())
    source = [deepcopy(item) for item in records]
    normal: list[dict[str, Any]] = []
    repaired: list[dict[str, Any]] = []
    quarantined: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    seen: set[str] = set()
    integrity_failures: list[dict[str, Any]] = []

    for item in source:
        try:
            expected_id = stable_record_id(item)
        except ValueError as exc:
            quarantined.append(item)
            evidence.append({"stable_record_id": None, "result": "QUARANTINED", "reason": str(exc)})
            continue
        supplied_id = item.get("stable_record_id")
        if supplied_id not in (None, expected_id):
            integrity_failures.append({"stable_record_id": expected_id, "reason": "IDENTITY_MISMATCH"})
            continue
        if expected_id in seen:
            integrity_failures.append({"stable_record_id": expected_id, "reason": "DUPLICATE_ID"})
            continue
        seen.add(expected_id)
        item["stable_record_id"] = expected_id
        try:
            validation = validator(deepcopy(item))
        except Exception as exc:  # adapter failure must not abort unrelated records
            quarantined.append(item)
            evidence.append({
                "stable_record_id": expected_id,
                "result": "QUARANTINED",
                "reason": "VALIDATOR_ERROR",
                "error_type": type(exc).__name__,
                "repair_attempts": 0,
            })
            continue
        valid = validation if isinstance(validation, bool) else bool(validation.get("valid"))
        if valid:
            normal.append(item)
            evidence.append({"stable_record_id": expected_id, "result": "NORMAL",
                             "repair_attempts": 0, "validation": validation})
            continue

        candidate = None
        repair_error = None
        repair_attempts = 0
        if repairer:
            repair_attempts = 1
            try:
                candidate = repairer(deepcopy(item))
            except Exception as exc:  # one failed repair is quarantined, never retried
                repair_error = {"reason": "REPAIRER_ERROR", "error_type": type(exc).__name__}
        if candidate is not None:
            if not isinstance(candidate, dict):
                quarantined.append(item)
                evidence.append({"stable_record_id": expected_id, "result": "QUARANTINED",
                                 "reason": "INVALID_REPAIR_RESULT",
                                 "repair_attempts": repair_attempts})
                continue
            try:
                candidate_id = stable_record_id(candidate)
            except ValueError:
                candidate_id = None
            changed = {key for key in set(item) | set(candidate) if item.get(key) != candidate.get(key)}
            forbidden = changed - allowed
            if candidate_id != expected_id or "stable_record_id" in forbidden or forbidden:
                integrity_failures.append({
                    "stable_record_id": expected_id,
                    "reason": "CROSS_RECORD_OR_PROTECTED_FIELD_CHANGE",
                    "changed_fields": sorted(changed),
                    "repair_attempts": repair_attempts,
                })
                continue
            candidate["stable_record_id"] = expected_id
            try:
                revalidation = validator(deepcopy(candidate))
            except Exception as exc:
                quarantined.append(item)
                evidence.append({"stable_record_id": expected_id, "result": "QUARANTINED",
                                 "reason": "REVALIDATOR_ERROR",
                                 "error_type": type(exc).__name__,
                                 "repair_attempts": repair_attempts})
                continue
            repaired_valid = revalidation if isinstance(revalidation, bool) else bool(revalidation.get("valid"))
            if repaired_valid:
                repaired.append(candidate)
                evidence.append({"stable_record_id": expected_id, "result": "AUTO_REPAIRED",
                                 "repair_attempts": repair_attempts,
                                 "validation_before": validation,
                                 "validation_after": revalidation,
                                 "changed_fields": sorted(changed)})
                continue
        quarantined.append(item)
        evidence.append({"stable_record_id": expected_id, "result": "QUARANTINED",
                         "reason": (repair_error or {}).get("reason", "UNRESOLVED_AFTER_REPAIR"),
                         "error_type": (repair_error or {}).get("error_type"),
                         "repair_attempts": repair_attempts,
                         "validation_before": validation})

    if integrity_failures:
        return {
            "status": "HOLD_IDENTITY_INTEGRITY",
            "input_count": len(source),
            "normal_count": 0,
            "auto_repaired_count": 0,
            "quarantined_count": len(source),
            "final_usable_count": 0,
            "identity_integrity_pass": False,
            "count_reconciliation_pass": True,
            "output_records": [],
            "integrity_failures": integrity_failures,
            "record_evidence": evidence,
        }

    usable = normal + repaired
    reconciled = len(source) == len(usable) + len(quarantined)
    return {
        "status": "PASS" if reconciled else "HOLD_COUNT_MISMATCH",
        "input_count": len(source),
        "normal_count": len(normal),
        "auto_repaired_count": len(repaired),
        "quarantined_count": len(quarantined),
        "final_usable_count": len(usable),
        "identity_integrity_pass": True,
        "count_reconciliation_pass": reconciled,
        "output_records": usable,
        "quarantined_records": quarantined,
        "integrity_failures": [],
        "record_evidence": evidence,
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


def output_self_audit_verdict(receipt: dict[str, Any]) -> str:
    """Gate a new output on complete, independently evidenced self-audit coverage.

    This validates the receipt supplied by the task-specific checker.  It does
    not infer semantic correctness from an AI result or from a successful export.
    Existing locked results are not reopened by this function.
    """
    audit = receipt.get("self_audit")
    if not isinstance(audit, dict):
        return "HOLD"
    stages = audit.get("stages")
    if not isinstance(stages, dict) or set(stages) != {
        "detect", "cause", "repair_revalidate", "prevent_recurrence"
    }:
        return "HOLD"
    if any(not isinstance(stage, dict) or stage.get("executed") is not True
           or not stage.get("evidence_ref") for stage in stages.values()):
        return "HOLD"
    count_keys = ("source_rows", "output_rows", "required_cells", "checked_cells",
                  "initial_errors", "corrected_errors", "residual_errors",
                  "unverified_required")
    if any(type(audit.get(key)) is not int or audit[key] < 0 for key in count_keys):
        return "HOLD"
    expected = audit.get("expected_columns")
    actual = audit.get("actual_columns")
    if (not isinstance(expected, list) or not expected
            or any(not isinstance(name, str) or not name for name in expected)
            or actual != expected):
        return "HOLD"
    if audit["source_rows"] == 0 or audit["source_rows"] != audit["output_rows"]:
        return "FAIL"
    if (audit["required_cells"] != audit["output_rows"] * len(expected)
            or audit["checked_cells"] != audit["required_cells"]):
        return "HOLD"
    if audit["initial_errors"] != audit["corrected_errors"] + audit["residual_errors"]:
        return "HOLD"
    changes = audit.get("before_after")
    if not isinstance(changes, list) or len(changes) != audit["corrected_errors"]:
        return "HOLD"
    if any(not isinstance(change, dict) or not all(
            key in change for key in ("record_id", "field", "before", "after", "cause_id"))
            for change in changes):
        return "HOLD"
    if any(not change["record_id"] or not change["field"] or not change["cause_id"]
           or change["before"] == change["after"] for change in changes):
        return "HOLD"
    if (audit.get("full_revalidation_pass") is not True
            or audit.get("independent_validation_pass") is not True
            or audit.get("source_identity_pass") is not True
            or audit.get("no_duplicate_or_loss_pass") is not True
            or not audit.get("recurrence_rule_ref")):
        return "HOLD"
    if audit["residual_errors"] or audit["unverified_required"]:
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

