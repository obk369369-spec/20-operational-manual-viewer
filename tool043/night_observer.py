"""Build the lightweight mobile observer state from canonical ledgers."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "feedback_pipeline"


def build() -> tuple[dict, dict]:
    roots = json.loads((PIPE / "evidence" / "work16_root_report.json").read_text(encoding="utf-8"))
    work = json.loads((PIPE / "evidence" / "work_execution_audit_20260827.json").read_text(encoding="utf-8"))
    open_count = roots["open_internal_root_count"]
    blocked = roots["external_hold_count"] + len(work["next_work_queue"])
    status = {
        "schema_version": 1,
        "current_status": "정상" if open_count == 0 and blocked == 0 else "문제",
        "night_processed": work["counts"]["actually_worked"],
        "new_open": open_count,
        "blocked_work": blocked,
        "next_work": "준비완료" if work["next_work_queue"] else "대기",
        "safe_checkpoint": roots.get("safe_checkpoint", "CURRENT_REMOTE_MAIN"),
        "user_manual_action_count": 0,
        "screen_off_test": "HOLD_ACTUAL_DEVICE_REQUIRED",
        "background_runtime": "GITHUB_ACTIONS_SCHEDULED_BATCH",
        "auto_recovery": "QUEUE_PRESERVED",
    }
    queue = {"schema_version": 1, "source": "canonical_work_execution_audit", "items": work["next_work_queue"]}
    return status, queue


def main() -> None:
    status, queue = build()
    (ROOT / "tool043" / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "tool043" / "night_queue.json").write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "queue_items": len(queue["items"]), "mobile": status}, ensure_ascii=False))


if __name__ == "__main__":
    main()
