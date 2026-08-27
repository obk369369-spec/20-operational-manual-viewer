"""Fail-closed audit for observer directives and actual Work execution."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGETS = HERE / "work_execution_targets_20260827.json"
REPORT = HERE / "evidence" / "work_execution_audit_20260827.json"
FINAL = {"ACTUALLY_FIXED", "ACTUALLY_TESTED", "VERIFIED_SKIP", "FAIL", "HOLD_EVIDENCE", "EXTERNAL_ESCALATION", "PLATFORM_LIMIT"}


def audit(data: dict) -> dict:
    rows = data["targets"]
    anomalies: list[dict] = []
    queue: list[dict] = []
    for row in rows:
        target = row["target"]
        status = row.get("final_status", "")
        worked = bool(row.get("actual_work") or row.get("verified_skip_evidence"))
        smoke = bool(row.get("actual_smoke", {}).get("result") in {"PASS", "FAIL", "HOLD"})
        if not worked:
            anomalies.append({"target": target, "kind": "NOT_WORKED"})
        if row.get("actual_smoke_required", True) and not smoke:
            anomalies.append({"target": target, "kind": "ACTUAL_SMOKE_MISSING"})
        if status not in FINAL:
            anomalies.append({"target": target, "kind": "FINAL_STATUS_MISSING"})
        if status in {"ACTUALLY_FIXED", "ACTUALLY_TESTED"} and not smoke:
            anomalies.append({"target": target, "kind": "UNVERIFIED_RESULT"})
        unresolved = status in {"", "FAIL", "HOLD_EVIDENCE", "EXTERNAL_ESCALATION"} or any(a["target"] == target for a in anomalies)
        if unresolved:
            queue.append({
                "target": target,
                "root_id": row["root_id"],
                "last_actual_point": row.get("last_actual_point", "TARGET_REGISTERED"),
                "failed_approach": row.get("failed_approach", "NONE"),
                "next_trigger": row.get("next_trigger", "RESUME_FROM_LAST_ACTUAL_POINT"),
            })
    counts = {
        "work_target_total": len(rows),
        "actually_worked": sum(bool(r.get("actual_work") or r.get("verified_skip_evidence")) for r in rows),
        "not_worked_total": sum(a["kind"] == "NOT_WORKED" for a in anomalies),
        "actual_smoke_missing_total": sum(a["kind"] == "ACTUAL_SMOKE_MISSING" for a in anomalies),
        "premature_exit_total": sum(a["kind"] == "FINAL_STATUS_MISSING" for a in anomalies),
        "partial_work_total": sum(r.get("final_status") == "PARTIAL_WORK" for r in rows),
        "unverified_result_total": sum(a["kind"] == "UNVERIFIED_RESULT" for a in anomalies),
        "post_work_anomaly_total": len(anomalies),
    }
    return {"schema_version": 1, "counts": counts, "anomalies": anomalies, "next_work_queue": queue, "execution_quality_pass": not anomalies, "overall_complete": not anomalies and not queue}


def self_test() -> None:
    fixture = {"targets": [
        {"target": "OK", "root_id": "R1", "actual_work": True, "actual_smoke": {"result": "PASS"}, "final_status": "ACTUALLY_TESTED"},
        {"target": "MISS", "root_id": "R2", "actual_work": False, "actual_smoke": {}, "final_status": ""},
    ]}
    result = audit(fixture)
    assert not result["execution_quality_pass"]
    assert result["counts"]["not_worked_total"] == 1
    assert result["counts"]["actual_smoke_missing_total"] == 1
    assert result["next_work_queue"][0]["root_id"] == "R2"
    print("PASS: work execution fail-closed audit")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = audit(json.loads(TARGETS.read_text(encoding="utf-8")))
    if args.record:
        REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
