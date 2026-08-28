"""KST approval-window and single-batch enforcement for normal Work operations."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, time, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUEUE = HERE / "approval_queue.json"
KST = timezone(timedelta(hours=9))


def audit(document: dict, now: datetime | None = None) -> dict:
    current = (now or datetime.now(KST)).astimezone(KST)
    fallback_check = time(14, 0) <= current.time() < time(15, 0)
    batches = document.get("batches", [])
    purposes = [row.get("purpose") for row in batches]
    approval_count = int(document.get("user_manual_approval_count", 0))
    errors: list[str] = []
    if len(purposes) != len(set(purposes)):
        errors.append("DUPLICATE_APPROVAL_PURPOSE")
    if approval_count > 1:
        errors.append("REPEATED_MANUAL_APPROVAL")
    for row in batches:
        if row.get("risk") != "SAFE_NORMAL":
            errors.append("HIGH_RISK_MIXED_IN_SAFE_BATCH")
    action = "CONTINUE_SAFE_WORK"
    if fallback_check and batches:
        action = "PRESENT_BATCH_WITHOUT_BLOCKING_SAFE_WORK"
    return {
        "schema_version": 1,
        "kst_time": current.isoformat(),
        "fallback_approval_check": fallback_check,
        "approval_wait_does_not_block_safe_work": True,
        "queued_batch_count": len(batches),
        "user_manual_approval_count": approval_count,
        "action": action,
        "errors": sorted(set(errors)),
        "pass": not errors,
    }


def self_test() -> None:
    base = {"batches": [{"purpose": "REMOTE_FINALIZE", "risk": "SAFE_NORMAL", "safe_work_exhausted": True}], "user_manual_approval_count": 0}
    before = audit(base, datetime(2026, 8, 27, 13, 0, tzinfo=KST))
    during = audit(base, datetime(2026, 8, 27, 14, 30, tzinfo=KST))
    repeated = audit({**base, "user_manual_approval_count": 2}, datetime(2026, 8, 27, 14, 30, tzinfo=KST))
    dangerous = audit({"batches": [{"purpose": "DELETE", "risk": "HIGH", "safe_work_exhausted": True}]})
    assert before["action"] == "CONTINUE_SAFE_WORK"
    assert during["action"] == "PRESENT_BATCH_WITHOUT_BLOCKING_SAFE_WORK"
    assert before["approval_wait_does_not_block_safe_work"] is True
    assert "REPEATED_MANUAL_APPROVAL" in repeated["errors"]
    assert "HIGH_RISK_MIXED_IN_SAFE_BATCH" in dangerous["errors"]
    print("PASS: approval batching, KST window and high-risk separation")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    print(json.dumps(audit(json.loads(QUEUE.read_text(encoding="utf-8"))), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
