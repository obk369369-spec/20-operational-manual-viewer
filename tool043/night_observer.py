"""Build the lightweight mobile observer state from canonical ledgers."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "feedback_pipeline"
ALLOWED_NIGHT_ACTIONS = {"REFRESH_OBSERVER_FROM_CENTRAL"}


def consume_safe_tasks(existing: dict) -> tuple[list[dict], list[dict]]:
    completed_now = []
    tasks = []
    for source in existing.get("items", []):
        if source.get("kind") != "SAFE_NIGHT_TASK":
            continue
        task = dict(source)
        current_run = os.environ.get("GITHUB_RUN_ID", "LOCAL_ONLY")
        recurring_due = task.get("execution_mode") == "RECURRING" and task.get("github_actions_run") != current_run
        if task.get("execution_status") == "QUEUED" or recurring_due:
            if task.get("action") not in ALLOWED_NIGHT_ACTIONS or task.get("safe") is not True:
                task["execution_status"] = "BLOCKED_UNSAFE_OR_UNKNOWN"\n                task["result"] = "BLOCKED_UNSAFE_OR_UNKNOWN"
            else:
                task.update({
                    "execution_status": "COMPLETED",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "github_actions_run": os.environ.get("GITHUB_RUN_ID", "LOCAL_ONLY"),
                    "source_revision": os.environ.get("GITHUB_SHA", "LOCAL_ONLY"),
                    "execution_count": int(task.get("execution_count", 0)) + 1,\n                    "result": "CENTRAL_OBSERVER_REFRESHED",
                })
                completed_now.append(task)
        tasks.append(task)
    return tasks, completed_now


def build() -> tuple[dict, dict]:
    roots = json.loads((PIPE / "evidence" / "work16_root_report.json").read_text(encoding="utf-8"))
    work = json.loads((PIPE / "evidence" / "work_execution_audit_20260827.json").read_text(encoding="utf-8"))
    unified = json.loads((PIPE / "unified_open_ledger.json").read_text(encoding="utf-8"))
    approvals = json.loads((PIPE / "approval_queue.json").read_text(encoding="utf-8"))
    queue_path = ROOT / "tool043" / "night_queue.json"
    previous_queue = json.loads(queue_path.read_text(encoding="utf-8")) if queue_path.exists() else {"items": []}
    status_path = ROOT / "tool043" / "status.json"
    previous_status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else {}
    safe_tasks, completed_now = consume_safe_tasks(previous_queue)
    last_completed = completed_now[-1] if completed_now else None
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
        "screen_off_evidence_contract": "tool043/android_screen_off_evidence.template.json",
        "screen_off_verifier": "tool043/android_screen_off_evidence.py",
        "single_device_run_required": True,
        "device_run_user_manual_action_target": 0,
        "background_runtime": "GITHUB_ACTIONS_SCHEDULED_BATCH",
        "auto_recovery": "QUEUE_PRESERVED",
        "unified_open_ledger": "feedback_pipeline/unified_open_ledger.json",
        "hidden_gap_total": unified["hidden_gap_total"],
        "incomplete_total": unified["incomplete_total"],
        "remote_pending_total": unified["remote_pending_total"],
        "deployment_pending_total": unified["deployment_pending_total"],
        "real_use_not_verified_total": unified["real_use_not_verified_total"],
        "user_feedback_courier_count": unified["user_feedback_courier_count"],
        "approval_pending_total": len(approvals.get("batches", [])),
        "approval_wait_does_not_block_safe_work": True,
        "approval_items": approvals.get("batches", []),
        "observer_generated_at": datetime.now(timezone.utc).isoformat(),
        "source_revision": os.environ.get("GITHUB_SHA", "LOCAL_ONLY"),
        "github_actions_run": os.environ.get("GITHUB_RUN_ID", "LOCAL_ONLY"),
        "tool043_role": "OBSERVATION_STATE_HANDOFF_BRIDGE",
        "smartphone_role": "OBSERVER_VIEW_ONLY",
        "smartphone_direct_work_execution": "FORBIDDEN",
        "remote_approval_from_smartphone": "BLOCKED_PLATFORM_NON_BLOCKING_SKIP_REUSE",
        "last_night_task_name": last_completed.get("task_name") if last_completed else previous_status.get("last_night_task_name"),
        "last_night_task_status": last_completed.get("execution_status") if last_completed else previous_status.get("last_night_task_status"),
        "night_automation_real_run": "PASS" if last_completed else previous_status.get("night_automation_real_run", "NOT_VERIFIED"),\n        "night_task_items": [{\n            "task_name": task.get("task_name", task.get("task_id", "UNKNOWN_TASK")),\n            "result": task.get("result", task.get("action", "UNKNOWN")),\n            "executed_at": task.get("completed_at"),\n            "status": task.get("execution_status", "UNKNOWN"),\n        } for task in safe_tasks],
    }
    items = list(work["next_work_queue"])
    known = {row["root_id"] for row in items}
    for row in unified["entries"]:
        if row["root_id"] not in known and row["type"] == "INCOMPLETE":
            items.append({"target":row["target"],"root_id":row["root_id"],"last_actual_point":row["status"],"failed_approach":"NONE","next_trigger":row.get("next_trigger")})
    queue = {"schema_version": 1, "source": "unified_open_ledger+canonical_work_execution_audit", "items": items + safe_tasks}
    return status, queue


def main() -> None:
    status, queue = build()
    (ROOT / "tool043" / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "tool043" / "night_queue.json").write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "queue_items": len(queue["items"]), "mobile": status}, ensure_ascii=False))


if __name__ == "__main__":
    main()

