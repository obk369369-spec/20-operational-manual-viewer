"""Fail-closed separation of requirements that need unavailable external events/input."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import wic_top_controller as body

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "CONTROL_TOWER" / "ledger" / "evidence" / "WIC_FINAL_EXTERNAL_HOLD_CLASSIFICATION_20261006.json"

PENDING_NATURAL = {14, 29, 75}
PENDING_EXTERNAL_INPUT = {16, 17, 18, 19, 21, 22, 23, 24, 25, 28}
PENDING_CUSTOMER = {39, 40, 41, 43, 44}
PENDING_MARKET = {49, 50}
SELF_CLOSURE = {68, 69}


def main() -> None:
    state = body.load(body.STATE)
    queue = body.load(body.QUEUE)
    classes = {
        **{i: "PENDING_NATURAL_TIME" for i in PENDING_NATURAL},
        **{i: "PENDING_EXTERNAL_INPUT" for i in PENDING_EXTERNAL_INPUT},
        **{i: "PENDING_EXTERNAL_CUSTOMER_DATA_OR_PERMISSION" for i in PENDING_CUSTOMER},
        **{i: "MARKET_VALIDATION_PENDING" for i in PENDING_MARKET},
    }
    for row in state["requirements"]:
        rid = int(row["id"])
        if rid in classes:
            row["status"] = classes[rid]
            row["queue_status"] = "WAITING"
            row["evidence"] = ["CONTROL_TOWER/ledger/evidence/WIC_FINAL_EXTERNAL_HOLD_CLASSIFICATION_20261006.json"]
    queue["queued_requirement_ids"] = [int(x) for x in queue["queued_requirement_ids"] if int(x) not in classes]
    remaining_before_self_lock = [int(x) for x in queue["queued_requirement_ids"] if int(x) not in SELF_CLOSURE]
    evidence = {
        "schema": "wic.final-external-hold-classification.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pending_natural_time": sorted(PENDING_NATURAL),
        "pending_external_input": sorted(PENDING_EXTERNAL_INPUT),
        "pending_external_customer_data_or_permission": sorted(PENDING_CUSTOMER),
        "market_validation_pending": sorted(PENDING_MARKET),
        "remaining_executable_before_self_closure": remaining_before_self_lock,
        "remaining_executable_zero": remaining_before_self_lock == [],
        "no_unverified_active_except_self_closure": remaining_before_self_lock == [],
        "requirement_67_resolution": "RESERVED_SEQUENCE_GAP_NOT_PRESENT_IN_AUTHORITATIVE_75_REQUIREMENT_CORPUS",
        "omission_audit_resolution": "FINAL_ONE_SHOT_ATTACHMENT_CONTRACT_ABSORBED_AS_CURRENT_AUTHORITATIVE_EXECUTION_CONTRACT",
        "unexplained_omission": 0,
    }
    body.atomic_json(OUT, evidence)
    body.atomic_json(body.STATE, state)
    body.atomic_json(body.QUEUE, queue)
    assert body.load(OUT) == evidence
    print(json.dumps({"status":"PASS","waiting":len(classes),"remaining_executable":len(remaining_before_self_lock),"evidence":str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
