"""Fail-closed classification of every currently queued WIC requirement."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import wic_top_controller as body

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "CONTROL_TOWER/controller/runtime/controller_state.json"
QUEUE = ROOT / "CONTROL_TOWER/controller/runtime/requirement_queue.json"
OUT = ROOT / "CONTROL_TOWER/ledger/evidence/WIC_QUEUE_54_COMMON_ROOT_CLASSIFICATION.json"

ROOTS = {
    "HOSTED_MULTI_FACTORY_AND_FAILOVER": {3, 4, 5, 7, 13, 14},
    "VERIFIED_COMPONENT_REGISTRY_AND_REUSE": {6, 11, 12},
    "KNOWLEDGE_TO_BUSINESS_DISCOVERY_PIPELINE": set(range(16, 29)),
    "SELF_AUDIT_FAILURE_CLASS_AND_RECOVERY": {29, 30, 31, 32, 33, 36, 37},
    "ACTUAL_CUSTOMER_BUSINESS_E2E": set(range(38, 45)),
    "REVENUE_DISCOVERY_AND_KPI": {49, 50, 53},
    "ASSET_OBSERVER_AND_BULK_CLOSURE": {54, 55, 60, 61, 62, 63, 64, 65, 66},
    "FINAL_ZERO_DEPENDENCY_AND_CONTINUOUS_OPERATION": {68, 69, 70, 74, 75, 76},
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    state = load(STATE)
    queue = load(QUEUE)
    queued = {int(value) for value in queue["queued_requirement_ids"]}
    assignments = {}
    duplicate = []
    for root_id, ids in ROOTS.items():
        for requirement_id in ids:
            if requirement_id in assignments:
                duplicate.append(requirement_id)
            assignments[requirement_id] = root_id
    classified = queued & set(assignments)
    unclassified = sorted(queued - set(assignments))
    stale = sorted(set(assignments) - queued)
    if duplicate or unclassified or stale or len(queued) != 54:
        raise SystemExit(json.dumps({"status": "FAIL_CLOSED", "queue_total": len(queued),
                                     "duplicate": duplicate, "unclassified": unclassified,
                                     "stale_not_queued": stale}, ensure_ascii=False))
    requirements = {int(row["id"]): row for row in state["requirements"]}
    roots = []
    for root_id, ids in ROOTS.items():
        ordered = sorted(ids)
        roots.append({"root_id": root_id, "category": "COMMON_ROOT", "count": len(ordered),
                      "requirement_ids": ordered,
                      "requirements": [requirements[value]["name"] for value in ordered]})
    waiting = [row for row in state["requirements"] if row["queue_status"] == "WAITING"]
    external = sorted(int(row["id"]) for row in waiting if row["status"] == "EXTERNAL_BLOCKED")
    market = sorted(int(row["id"]) for row in waiting if row["status"] == "MARKET_VALIDATION_PENDING")
    outside = set(external) | set(market)
    duplicates_removed = len(queued & outside)
    total_unfinished_unique = len(queued | outside)
    classified_total = len(classified) + len(outside)
    result = {
        "schema": "wic.queue.common_root.classification.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "queue_sha256": hashlib.sha256(QUEUE.read_bytes()).hexdigest().upper(),
        "state_sha256": hashlib.sha256(STATE.read_bytes()).hexdigest().upper(),
        "start_queue": len(queued),
        "queue_54_outside_unfinished_count": len(outside),
        "duplicates_removed": duplicates_removed,
        "total_unfinished_unique": total_unfinished_unique,
        "classified_total": classified_total,
        "unclassified_total": len(unclassified),
        "common_root_count": len(roots),
        "roots": roots,
        "classified_requirement_ids": sorted(classified),
        "sum_matches_queue": sum(row["count"] for row in roots) == len(queued),
        "sum_matches_total_unfinished": sum(row["count"] for row in roots) + len(external) + len(market) == total_unfinished_unique,
        "external_blocked_waiting": external,
        "market_validation_pending": market,
        "time_pending_in_queue": [],
        "independent_roots_in_queue": [],
        "status": "PASS" if classified_total == total_unfinished_unique and not unclassified else "FAIL",
    }
    body.atomic_json(OUT, result)
    readback = load(OUT)
    if (readback["status"] != "PASS" or not readback["sum_matches_queue"]
            or not readback["sum_matches_total_unfinished"]):
        raise SystemExit("CLASSIFICATION_READBACK_FAIL")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
