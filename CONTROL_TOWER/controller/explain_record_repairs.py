"""Evidence-bound, plain-Korean explanation of real record validation and repair.

A report is not a PASS certificate. It only describes supplied execution evidence.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def explain_repairs(before_records, gate_result, *, source_ref, rule_ref, output_ref=None):
    """Build an auditable report without inventing before/after values or proof."""
    if not source_ref or not rule_ref:
        raise ValueError("SOURCE_AND_RULE_REFERENCES_REQUIRED")
    original = {}
    from CONTROL_TOWER.controller.universal_enforcement import stable_record_id
    for row in before_records:
        key = stable_record_id(row)
        if key in original:
            raise ValueError("DUPLICATE_SOURCE_RECORD")
        original[key] = row
    final = {stable_record_id(row): row for row in gate_result.get("output_records", [])}
    items = []
    for entry in gate_result.get("record_evidence", []):
        key = entry.get("stable_record_id")
        old = original.get(key)
        new = final.get(key)
        if old is None:
            items.append({"record_id": key, "status": "확인 필요", "reason": "원본 행을 찾지 못했습니다.", "proof": None})
            continue
        changes = []
        if entry.get("result") == "AUTO_REPAIRED" and new is not None:
            for field in sorted(set(old) | set(new)):
                if old.get(field) != new.get(field):
                    changes.append({"field": field, "before": old.get(field), "after": new.get(field)})
        status = {"NORMAL": "원래 정상", "AUTO_REPAIRED": "수정 후 재검사 통과",
                  "QUARANTINED": "수정하지 못해 분리"}.get(entry.get("result"), "확인 필요")
        items.append({
            "record_id": key, "status": status, "changes": changes,
            "reason": entry.get("reason") or ("검사에서 문제가 없었습니다." if status == "원래 정상" else
                "허용된 항목만 수정하고 다시 검사했습니다." if changes else "자동 수정 근거가 부족합니다."),
            "validation_before": entry.get("validation_before", entry.get("validation")),
            "validation_after": entry.get("validation_after"),
            "repair_attempts": entry.get("repair_attempts", 0),
            "before_sha256": _digest(old), "after_sha256": _digest(new) if new else None,
        })
    integrity_ok = gate_result.get("identity_integrity_pass") is True
    counts_ok = gate_result.get("count_reconciliation_pass") is True
    all_accounted = len(items) == len(before_records)
    report = {
        "report_kind": "EXPLANATION_NOT_FINAL_PASS",
        "status": "검사 기록 확인" if integrity_ok and counts_ok and all_accounted else "전체 확인 보류",
        "source_ref": source_ref, "rule_ref": rule_ref, "output_ref": output_ref,
        "input_sha256": _digest(before_records), "gate_sha256": _digest(gate_result),
        "input_count": len(before_records), "explained_count": len(items),
        "auto_repaired_count": sum(x["status"] == "수정 후 재검사 통과" for x in items),
        "unresolved_count": sum(x["status"] in ("수정하지 못해 분리", "확인 필요") for x in items),
        "records": items,
        "remote_readback_verified": False,
        "final_business_pass": False,
    }
    return report


def save_explanation(report, target):
    """Write an independent JSON explanation; remote verification remains separate."""
    path = Path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n"
    path.write_text(payload, encoding="utf-8")
    if path.read_text(encoding="utf-8") != payload:
        raise IOError("REPORT_LOCAL_READBACK_FAILED")
    return hashlib.sha256(path.read_bytes()).hexdigest()
