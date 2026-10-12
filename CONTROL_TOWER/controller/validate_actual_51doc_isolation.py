from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from universal_enforcement import enforce_record_isolation


def main(manifest_path: str, evidence_path: str) -> int:
    manifest_file = Path(manifest_path)
    raw = manifest_file.read_bytes()
    manifest = json.loads(raw.decode("utf-8-sig"))
    records = [
        {
            "origin_file": item["Source"],
            "origin_row": 1,
            "conversion_status": item["Status"],
            "text_bytes": item.get("Bytes", 0),
        }
        for item in manifest
    ]
    result = enforce_record_isolation(
        records,
        lambda row: row["conversion_status"] == "PASS" and row["text_bytes"] > 0,
    )
    expected = {
        "input_count": 51,
        "normal_count": 42,
        "auto_repaired_count": 0,
        "quarantined_count": 9,
        "final_usable_count": 42,
        "identity_integrity_pass": True,
        "count_reconciliation_pass": True,
    }
    comparison = {key: result.get(key) == value for key, value in expected.items()}
    evidence = {
        "schema": "wic.actual-record-isolation-evidence.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "root": "USER_VISIBLE_OUTPUT_AUTONOMOUS_RECOVERY_AND_RECORD_IDENTITY",
        "actual_input": {
            "manifest": str(manifest_file),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "records": len(records),
        },
        "expected": expected,
        "actual": {key: result.get(key) for key in expected},
        "comparison": comparison,
        "positive_pass": result["normal_count"] == 42,
        "negative_pass": result["quarantined_count"] == 9,
        "failure_isolation_pass": result["final_usable_count"] == 42,
        "identity_integrity_pass": result["identity_integrity_pass"],
        "count_reconciliation_pass": result["count_reconciliation_pass"],
        "record_evidence": result["record_evidence"],
        "quarantined_record_ids": [row["stable_record_id"] for row in result["quarantined_records"]],
        "overall": "PASS" if all(comparison.values()) else "FAIL",
        "tool013_actual_input_application": "HOLD_SEPARATE_ACTUAL_XLS_INPUT_REQUIRED",
        "actual_24h_elapsed_validation": "PENDING_NATURAL_TIME",
    }
    target = Path(evidence_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    reread = json.loads(target.read_text(encoding="utf-8"))
    print(json.dumps({"overall": reread["overall"], "actual": reread["actual"],
                      "evidence_readback": reread == evidence}, ensure_ascii=False))
    return 0 if reread == evidence and evidence["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
