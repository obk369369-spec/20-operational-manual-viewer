"""Read-only reconciliation engine for the WIC incomplete ledger and TOOL044 queue."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MASTER = HERE / "WIC_MASTER_INCOMPLETE_LEDGER_20261004.json"
QUEUE = ROOT / "_wic_speed_runner_audit" / "feedback_pipeline" / "tool044_atomic_demand_queue.json"
CANONICAL = ROOT / "_wic_speed_runner_audit" / "feedback_pipeline" / "unified_open_ledger.json"
EVIDENCE = HERE / "evidence" / "WIC_LEDGER_RECONCILIATION_E2E.json"
STATE = HERE / "tool_state.json"

TERMINAL = {
    "PASS", "PASS_LOCKED", "SATISFIED_BY_COMMON_COMPONENT",
    "SKIP_REUSE_VERIFIED_PASS", "SKIP_REUSE_VERIFIED_COMPONENT_TARGET_RETEST_REQUIRED",
}
HOLD_MARKERS = ("HOLD", "WAITING", "PLATFORM_LIMIT", "DEFERRED")
ACTION_MARKERS = ("OPEN", "READY", "AUTO_HANDED_OFF")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def classify(status: str) -> str:
    if status in TERMINAL:
        return "TERMINAL"
    if any(marker in status for marker in HOLD_MARKERS):
        return "HOLD"
    if any(marker in status for marker in ACTION_MARKERS):
        return "ACTIONABLE"
    return "REVIEW_REQUIRED"


def build(queue_override: dict | None = None) -> dict:
    master = load(MASTER)
    queue = queue_override or load(QUEUE)
    canonical = load(CANONICAL)
    demands = queue.get("demands", [])
    classes = Counter(classify(str(row.get("status", ""))) for row in demands)
    roots: dict[str, list[str]] = defaultdict(list)
    for row in demands:
        if classify(str(row.get("status", ""))) == "ACTIONABLE":
            roots[str(row.get("root_id") or row.get("demand_id"))].append(str(row.get("demand_id")))
    duplicate_active_ids = sorted(
        demand_id for demand_id, count in Counter(
            str(row.get("demand_id")) for row in demands
            if classify(str(row.get("status", ""))) == "ACTIONABLE"
        ).items() if count > 1
    )
    canonical_open = sorted(
        str(row.get("root_id")) for row in canonical.get("entries", [])
        if str(row.get("status", "")) not in {"VERIFIED_CLOSED", "DEPLOYED_COMPLETE"}
    )
    false_complete = [
        item["id"] for item in master["items"]
        if item.get("current_status") == "COMPLETE" and not item.get("existing_evidence")
    ]
    return {
        "schema_version": 1,
        "run_id": "WIC-LEDGER-RECONCILIATION-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "master": str(MASTER.relative_to(ROOT)).replace("\\", "/"),
            "master_sha256": sha256(MASTER),
            "queue": str(QUEUE.relative_to(ROOT)).replace("\\", "/"),
            "queue_sha256": sha256(QUEUE),
            "canonical": str(CANONICAL.relative_to(ROOT)).replace("\\", "/"),
            "canonical_sha256": sha256(CANONICAL),
        },
        "master_item_count": len(master["items"]),
        "queue_demand_count": len(demands),
        "queue_classification": dict(sorted(classes.items())),
        "actionable_common_root_count": len(roots),
        "actionable_common_roots": [
            {"root_id": root, "demand_count": len(ids), "demand_ids": sorted(ids)}
            for root, ids in sorted(roots.items())
        ],
        "canonical_nonclosed_roots": canonical_open,
        "duplicate_active_demand_ids": duplicate_active_ids,
        "false_complete_without_evidence": false_complete,
        "pass": not duplicate_active_ids and not false_complete,
        "closure": "RECONCILIATION_AUDIT_PASS" if not duplicate_active_ids and not false_complete else "RECONCILIATION_BLOCKED",
    }


def negative_test() -> None:
    queue = load(QUEUE)
    actionable = next(row for row in queue["demands"] if classify(str(row.get("status", ""))) == "ACTIONABLE")
    queue["demands"].append(dict(actionable))
    result = build(queue)
    assert actionable["demand_id"] in result["duplicate_active_demand_ids"]
    assert result["pass"] is False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-test", action="store_true")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    if args.negative_test:
        negative_test()
        print("PASS: duplicate actionable demand blocks reconciliation")
        return
    result = build()
    if args.record:
        EVIDENCE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        state = {
            "tool": "WIC_MASTER_INCOMPLETE_RECONCILER",
            "status": "PASS" if result["pass"] else "HOLD",
            "current_step": "중앙 미완료와 44번 작업 목록을 대조했습니다.",
            "progress": 100,
            "actual_result": result["closure"],
            "evidence": str(EVIDENCE.relative_to(ROOT)).replace("\\", "/"),
            "updated_at": result["executed_at"],
        }
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
