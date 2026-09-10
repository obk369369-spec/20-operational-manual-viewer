"""Account every requirement in both directions without claiming missing evidence PASS."""
from __future__ import annotations

import json
from pathlib import Path

from tool044_independent_completeness_gate import _final_requirement, _read
from tool044_requirement_interlock import HERE, verify_requirement


def run(root: Path = HERE) -> dict:
    ledger = _read(root / "tool044_current_requirement_ledger.json")
    scope = _read(root / "tool044_final_scope_requirements.json")
    rows = list(ledger["requirements"])
    rows.extend(_final_requirement(row, root, scope["scope_id"]) for row in scope["requirements"])
    ids = [row["req_id"] for row in rows]
    valid = []
    missing = []
    reverse_fail = []
    for row in rows:
        # The reconciliation receipt cannot validate its own content-addressed
        # receipt without creating a hash cycle. Account the requirement's
        # presence here, while the independent completeness gate validates its
        # receipt after this file is written.
        if row["req_id"] == "FINAL-021":
            continue
        result = verify_requirement(row, root)
        if result.get("result") == "PASS":
            valid.append(row["req_id"])
            chain = row.get("reverse_trace", {}).get("chain", [])
            if not chain or chain[0] != row["req_id"]:
                reverse_fail.append(row["req_id"])
        else:
            missing.append(row["req_id"])
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    checks = {
        "FORWARD_ACCOUNTING": len(ids) - 1 == len(valid) + len(missing),
        "REVERSE_VALID_EVIDENCE": not reverse_fail,
        "DUPLICATE_REQUIREMENT_IDS": not duplicate_ids,
        "DENOMINATOR_MATCH": len(ids) == 101,
        "SELF_REQUIREMENT_PRESENT": ids.count("FINAL-021") == 1,
    }
    output = {
        "evidence_id": "TOOL044_FORWARD_REVERSE_REQUIREMENT_EVIDENCE_RECONCILIATION_20260910",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": {key: "PASS" if value else "FAIL" for key, value in checks.items()},
        "TOTAL_REQUIREMENTS": len(ids), "RECONCILED_REQUIREMENTS_EXCLUDING_SELF": len(ids) - 1,
        "VALID_EVIDENCE_EXCLUDING_SELF": len(valid), "UN_EVIDENCE_EXCLUDING_SELF": len(missing),
        "self_requirement": "FINAL-021_RECEIPT_VALIDATED_BY_INDEPENDENT_COMPLETENESS_GATE",
        "valid_requirement_ids": valid,
        "missing_requirement_ids": missing, "duplicate_requirement_ids": duplicate_ids,
        "reverse_trace_failures": reverse_fail,
        "truth_boundary": "Missing requirements are accounted as missing, never promoted to PASS.",
    }
    target = root / "evidence" / "tool044_forward_reverse_reconciliation_20260910.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
