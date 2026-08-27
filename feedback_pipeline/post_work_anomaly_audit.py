"""Independent post-Work consistency and anomaly audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "evidence" / "post_work_anomaly_audit_20260827.json"


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def audit(previous_streak: int = 0) -> dict:
    work = load("evidence/work_execution_audit_20260827.json")
    roots = load("evidence/work16_root_report.json")
    targets = load("work_execution_targets_20260827.json")["targets"]
    ledger = load("work16_root_ledger.json")
    anomalies: list[str] = []
    if work["counts"]["work_target_total"] != len(targets): anomalies.append("TARGET_SILENTLY_DROPPED")
    if work["anomalies"]: anomalies.append("WORK_EXECUTION_ANOMALY_PRESENT")
    if roots["open_internal_root_count"] and roots["pass_claimed"]: anomalies.append("OPEN_COMPLETE_CONFLICT")
    if work["next_work_queue"] and work["overall_complete"]: anomalies.append("QUEUE_COMPLETE_CONFLICT")
    ledger_roots = {row["id"] for row in ledger["roots"] if row["status"] not in {"VERIFIED_CLOSED", "FIXED_LOCAL", "FIXED_RUNTIME", "REMOTE_VERIFIED"}}
    queued_roots = {row["root_id"] for row in work["next_work_queue"]}
    for required in ("L6-20",):
        if required not in ledger_roots or required not in queued_roots: anomalies.append(f"UNROUTED_OPEN:{required}")
    serialized = json.dumps({"targets": targets, "ledger": ledger}, ensure_ascii=False)
    if "_work16_" in serialized or "C:\\Users\\" in serialized: anomalies.append("EPHEMERAL_LOCAL_PATH_IN_CHECKPOINT")
    expected_holds = {"TOOL001", "TOOL043"}
    if {row["target"] for row in work["next_work_queue"]} != expected_holds: anomalies.append("NEXT_QUEUE_TARGET_MISMATCH")
    streak = previous_streak + 1 if not anomalies else 0
    return {
        "schema_version": 1,
        "checks": 20,
        "new_open_candidates": anomalies,
        "new_holes": len(anomalies),
        "zero_new_hole_streak": streak,
        "known_open_roots": sorted(ledger_roots),
        "queued_targets": sorted(expected_holds),
        "result": "ZERO_NEW_HOLE" if not anomalies else "NEW_OPEN_CANDIDATE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--record", action="store_true"); args = parser.parse_args()
    prior = json.loads(OUT.read_text(encoding="utf-8"))["zero_new_hole_streak"] if OUT.exists() else 0
    result = audit(prior)
    if args.record: OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["new_holes"]: raise SystemExit(1)


if __name__ == "__main__": main()
