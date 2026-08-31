"""Build the lightweight mobile observer state from canonical ledgers."""
from __future__ import annotations

import json
import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "feedback_pipeline"
ALLOWED_NIGHT_ACTIONS = {"REFRESH_OBSERVER_FROM_CENTRAL"}


def verified_checkpoint(roots: dict, previous_status: dict) -> str:
    # Never promote GITHUB_SHA (an unvalidated in-flight revision) to a safe point.
    for candidate in (previous_status.get("safe_checkpoint"), roots.get("safe_checkpoint")):
        if isinstance(candidate, str) and re.fullmatch(r"[0-9a-f]{40}", candidate):
            return candidate
    return "HOLD_CHECKPOINT_NOT_VERIFIED"


def current_work(ledger: dict, unified: dict, work: dict, incomplete: dict, previous_queue: dict) -> dict:
    """Conserve unresolved IDs; only an evidence-backed canonical closure removes one."""
    closed_states = {"VERIFIED_CLOSED", "REMOTE_VERIFIED", "FIXED_RUNTIME", "DEPLOYED_COMPLETE", "CURRENT_SCOPE_COMPLETE"}
    closed = {r["id"] for r in ledger["roots"] if r.get("status") in closed_states and (r.get("completion_evidence") or r.get("evidence"))}
    rows = {}
    errors = []
    labels = {
        "HOLD-T1-VERIFIED-REPORT-ACQUISITION": ("TOOL001", "검증된 실제 보고서 5건 대기"),
        "HOLD-T6-PUBLISHER-GOLDEN-PAIR": ("TOOL006", "발행사 실제 원문·정답 쌍 대기"),
        "HOLD-T7-CHATGPT-NATIVE-INTERCEPTOR": ("TOOL007", "플랫폼 자동 수집 기능 지원 대기"),
    }
    sources = [
        ("canonical", ledger["roots"]), ("external", ledger.get("external_holds", [])),
        ("unified", unified["entries"]), ("incomplete", incomplete["entries"]),
        ("work_queue", work["next_work_queue"]), ("night_queue", previous_queue.get("items", [])),
    ]
    for source, items in sources:
        for index, row in enumerate(items):
            if row.get("kind") == "SAFE_NIGHT_TASK" and row.get("execution_status") == "COMPLETED":
                continue  # Routine recurring maintenance is not an unresolved user task.
            rid = row.get("canonical_root") or row.get("root_id") or row.get("id") or row.get("root") or row.get("task_id")
            if not rid:
                rid = f"UNIDENTIFIED:{source}:{index}"
                errors.append("TASK_ID_MISSING:" + rid)
            if rid in closed:
                continue
            state = row.get("status") or row.get("execution_status") or "PENDING"
            if state in closed_states and not row.get("completion_evidence") and not row.get("evidence"):
                errors.append("UNPROVEN_COMPLETION:" + rid)
            target, label = labels.get(rid, (row.get("target", "WIC"), row.get("display_label") or row.get("task_name") or rid))
            item = rows.setdefault(rid, {"root_id": rid, "target": target, "label": label, "status": state, "sources": []})
            item["sources"].append(source)
            for key in ("next_trigger", "next_start", "last_actual_point"):
                if row.get(key): item[key] = row[key]
            if state in {"RUNNING", "IN_PROGRESS", "ACTIVE_EXECUTION"}:
                item["status"] = state
    running, waiting, pending = [], [], []
    for row in rows.values():
        state = row["status"]
        if state in {"RUNNING", "IN_PROGRESS", "ACTIVE_EXECUTION"}:
            running.append(row)
        elif any(word in state for word in ("HOLD", "WAIT", "BLOCK", "LIMIT", "ESCALATION")) or row.get("next_trigger") not in (None, "IMMEDIATE", "RESUME_FROM_LAST_ACTUAL_WORK"):
            waiting.append(row)
        else:
            pending.append(row)
    canonical_open = {r["id"] for r in ledger["roots"] if r["id"] not in closed}
    if not canonical_open.issubset(rows): errors.append("UNRESOLVED_TASK_LOST")
    recent = [{"root_id": r["id"], "label": r.get("completion_label", r["id"]), "evidence": r["completion_evidence"]}
              for r in ledger["roots"] if r["id"] in closed and r.get("completion_evidence")]
    return {"remaining": list(rows.values()), "running": running, "waiting": waiting, "pending": pending,
            "remaining_total": len(rows), "running_total": len(running), "waiting_total": len(waiting),
            "pending_total": len(pending), "open_internal_total": len(canonical_open),
            "recent_completed": recent[-3:], "errors": errors, "conservation_pass": not errors}


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
                task["execution_status"] = "BLOCKED_UNSAFE_OR_UNKNOWN"
                task["result"] = "BLOCKED_UNSAFE_OR_UNKNOWN"
            else:
                task.update({
                    "execution_status": "COMPLETED",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "github_actions_run": os.environ.get("GITHUB_RUN_ID", "LOCAL_ONLY"),
                    "source_revision": os.environ.get("GITHUB_SHA", "LOCAL_ONLY"),
                    "execution_count": int(task.get("execution_count", 0)) + 1,
                    "result": "CENTRAL_OBSERVER_REFRESHED",
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
    ledger = json.loads((PIPE / "work16_root_ledger.json").read_text(encoding="utf-8"))
    incomplete = json.loads((PIPE / "incomplete_register.json").read_text(encoding="utf-8"))
    current = current_work(ledger, unified, work, incomplete, previous_queue)
    safe_tasks, completed_now = consume_safe_tasks(previous_queue)
    last_completed = completed_now[-1] if completed_now else None
    open_count = current["open_internal_total"]
    blocked = current["waiting_total"]
    status = {
        "schema_version": 1,
        "central_input_sha256": {str(p.relative_to(ROOT)).replace(chr(92), '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (PIPE / 'work16_root_ledger.json', PIPE / 'incomplete_register.json',
                                           PIPE / 'unified_open_ledger.json', PIPE / 'approval_queue.json',
                                           PIPE / 'evidence' / 'work_execution_audit_20260827.json')},
        "current_status": "관찰판 정상" if current["conservation_pass"] else "관찰판 이상",
        "observer_health": "OK" if current["conservation_pass"] else "ERROR",
        "tool043_scope_status": previous_status.get("tool043_scope_status", "INCOMPLETE"),
        "current_display_validation": previous_status.get("current_display_validation"),
        "work_status": "작업 문제 있음" if blocked or open_count else ("작업 진행 중" if current["running"] else ("작업 대기 중" if current["pending"] else "현재 미처리 작업 없음")),
        "current_work": current,
        "max_status_age_seconds": 28800,
        "night_processed": len(completed_now) if completed_now else sum(r.get("status") == "COMPLETED" for r in previous_status.get("night_task_items", [])),
        "new_open": open_count,
        "blocked_work": blocked,
        "next_work": " / ".join(r["label"] for r in current["pending"][:3]) if current["pending"] else ("대기 조건 충족 후 재개" if current["waiting"] else "현재 예약된 미완료 작업 없음"),
        "safe_checkpoint": verified_checkpoint(roots, previous_status),
        "safe_checkpoint_evidence": previous_status.get("safe_checkpoint_evidence"),
        "user_manual_action_count": 0,
        "screen_off_test": previous_status.get("screen_off_test", "HOLD_ACTUAL_DEVICE_REQUIRED"),
        "device_observer_verification": previous_status.get("device_observer_verification", {}),
        "screen_off_evidence_contract": "tool043/android_screen_off_evidence.template.json",
        "screen_off_verifier": "tool043/android_screen_off_evidence.py",
        "single_device_run_required": previous_status.get("screen_off_test") != "PASS_ACTUAL_DEVICE_REOPEN_NEW_RESULT",
        "device_run_user_manual_action_target": 0,
        "background_runtime": "GITHUB_ACTIONS_SCHEDULED_BATCH",
        "auto_recovery": "QUEUE_PRESERVED",
        "unified_open_ledger": "feedback_pipeline/unified_open_ledger.json",
        "hidden_gap_total": unified["hidden_gap_total"],
        "incomplete_total": current["remaining_total"],
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
        "night_automation_real_run": "PASS" if last_completed else previous_status.get("night_automation_real_run", "NOT_VERIFIED"),
        "night_task_items": [{
            "task_name": task.get("task_name", task.get("task_id", "UNKNOWN_TASK")),
            "result": task.get("result", task.get("action", "UNKNOWN")),
            "executed_at": task.get("completed_at"),
            "status": task.get("execution_status", "UNKNOWN"),
        } for task in safe_tasks],
    }
    items = [{"target": row["target"], "root_id": row["root_id"], "status": row["status"],
              "last_actual_point": row.get("last_actual_point", row["status"]),
              "next_trigger": row.get("next_trigger"), "next_start": row.get("next_start")}
             for row in current["remaining"]]
    queue = {"schema_version": 1, "source": "unified_open_ledger+canonical_work_execution_audit", "items": items + safe_tasks}
    return status, queue


def main() -> None:
    status, queue = build()
    (ROOT / "tool043" / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "tool043" / "night_queue.json").write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "queue_items": len(queue["items"]), "mobile": status}, ensure_ascii=False))


def self_test() -> None:
    from copy import deepcopy
    ledger = {"roots": [{"id": "done", "status": "REMOTE_VERIFIED", "completion_evidence": {"commit": "a" * 40}}, {"id": "open", "status": "OPEN"}], "external_holds": [{"root": "wait", "status": "HOLD_EVIDENCE_WAITING"}]}
    args = [ledger, {"entries": [{"root_id": "done", "status": "OPEN"}, {"root_id": "open", "status": "OPEN"}]}, {"next_work_queue": []}, {"entries": []}, {"items": [{"root_id": "done"}, {"root_id": "wait"}]}]
    result = current_work(*args)
    assert {r['root_id'] for r in result['remaining']} == {'open', 'wait'}
    assert result['waiting_total'] == 1 and result['open_internal_total'] == 1
    assert result['remaining_total'] == 2 and result['conservation_pass']
    no_proof = deepcopy(args)
    no_proof[0]['roots'][0].pop('completion_evidence')
    result = current_work(*no_proof)
    assert result['remaining_total'] == 3 and not result['conservation_pass']
    running = deepcopy(args)
    running[2]['next_work_queue'] = [{'root_id': 'new-task', 'status': 'RUNNING'}]
    result = current_work(*running)
    assert result['remaining_total'] == 3 and result['running_total'] == 1
    assert result['remaining_total'] == result['waiting_total'] + result['running_total'] + result['pending_total']
    print('PASS: task conservation, evidence-backed closure, duplicate dedup, unproven completion blocked, explicit running task')


if __name__ == "__main__":
    self_test() if "--self-test" in sys.argv else main()
