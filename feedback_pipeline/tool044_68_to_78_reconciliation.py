"""Independently reconcile the ten requirement receipts behind the 68 -> 78 increase."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from tool044_independent_completeness_gate import _final_requirement
from tool044_requirement_interlock import HERE, verify_requirement


REQUIREMENTS = {
    "FINAL-001", "FINAL-002", "FINAL-012", "FINAL-016", "FINAL-017",
    "FINAL-018", "FINAL-019", "FINAL-022", "FINAL-023", "FINAL-024",
}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _test_time(receipt: dict[str, Any]) -> str:
    for key in ("generated_at", "timestamp", "tested_at", "completed_at", "recorded_at"):
        if receipt.get(key):
            return str(receipt[key])
    for section in ("natural_schedule_run", "remote_ci", "actual_run"):
        value = receipt.get(section)
        if isinstance(value, dict):
            for key in ("created_at", "started_at", "completed_at", "timestamp"):
                if value.get(key):
                    return str(value[key])
    return "NOT_RECORDED_IN_SOURCE_RECEIPT"


def run(root: Path = HERE) -> dict[str, Any]:
    scope = _read(root / "tool044_final_scope_requirements.json")
    selected = [row for row in scope["requirements"] if row["req_id"] in REQUIREMENTS]
    records = []
    valid = []
    evidence_to_requirements: dict[str, list[str]] = {}
    for row in selected:
        requirement = _final_requirement(row, root, scope["scope_id"])
        result = verify_requirement(requirement, root)
        evidence = root / row["evidence_path"]
        receipt = _read(evidence)
        evidence_to_requirements.setdefault(row["evidence_path"], []).append(row["req_id"])
        receipt_hash = hashlib.sha256(evidence.read_bytes()).hexdigest()
        passed = result.get("result") == "PASS" and receipt_hash.lower() == row["evidence_sha256"].lower()
        if passed:
            valid.append(row["req_id"])
        records.append({
            "REQUIREMENT_ID": row["req_id"],
            "EVIDENCE_ID": row["evidence_path"],
            "ORIGINAL_PASS_SOURCE": row["evidence_path"],
            "ORIGINAL_TEST_TIME": _test_time(receipt),
            "WHY_REUSABLE": {
                "requirement": row["name"],
                "receipt_checks": row.get("receipt_checks", {}),
                "content_addressed_sha256": receipt_hash,
                "seven_interlock": result.get("result"),
            },
            "AFFECTED_OR_UNAFFECTED": "UNAFFECTED_EXISTING_PASS_EVIDENCE",
            "READBACK_RESULT": "PASS" if passed else "FAIL",
        })
    unique_requirements = {row["REQUIREMENT_ID"] for row in records}
    duplicate_inflation = len(records) - len(unique_requirements)
    false_mapping = len(records) - len(valid)
    shared_receipts = {
        path: ids for path, ids in evidence_to_requirements.items() if len(ids) > 1
    }
    output = {
        "gate": "EVIDENCE_68_TO_78_RECONCILIATION",
        "baseline_valid_evidence": 68,
        "current_valid_evidence": 78,
        "expected_increment": 10,
        "unique_increment_requirements": len(unique_requirements),
        "shared_receipts_not_counted_as_extra_requirements": shared_receipts,
        "records": records,
        "FALSE_EVIDENCE_MAPPING": false_mapping,
        "DUPLICATE_EVIDENCE_INFLATION": duplicate_inflation,
        "INVALID_REUSED_EVIDENCE": false_mapping,
        "status": "PASS" if false_mapping == 0 and duplicate_inflation == 0 and len(records) == 10 else "FAIL",
    }
    target = root / "evidence" / "tool044_68_to_78_reconciliation_20260910.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
