"""Build the lightweight mobile observer state from canonical ledgers."""
from __future__ import annotations

import json
import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from completion_proof import valid_proof
from chat_work_coordinator import run as run_chat_coordinator

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "feedback_pipeline"
ALLOWED_NIGHT_ACTIONS = {"REFRESH_OBSERVER_FROM_CENTRAL"}


def verified_checkpoint(roots: dict, previous_status: dict) -> str:
    # Never promote GITHUB_SHA (an unvalidated in-flight revision) to a safe point.
    for candidate in (previous_status.get("safe_checkpoint"), roots.get("safe_checkpoint")):
        if isinstance(candidate, str) and re.fullmatch(r"[0-9a-f]{40}", candidate):
            return candidate
    return "HOLD_CHECKPOINT_NOT_VERIFIED"


def current_work(ledger: dict, root_report: dict, unified: dict, work: dict, incomplete: dict, previous_queue: dict) -> dict:
    """Conserve unresolved IDs; only an evidence-backed canonical closure removes one."""
    closed_states = {"VERIFIED_CLOSED", "REMOTE_VERIFIED", "FIXED_RUNTIME", "DEPLOYED_COMPLETE", "CURRENT_SCOPE_COMPLETE"}
    closed = {r["id"] for r in ledger["roots"] if r.get("status") in closed_states and (r.get("completion_evidence") or r.get("evidence"))}
    # Unified canonical closures also supersede stale queue projections. A
    # conflicting legacy root remains unresolved; a queue can never close a root.
    legacy = {r["id"]: r for r in ledger["roots"]}
    for row in unified["entries"]:
        rid = row.get("root_id")
        if (rid and row.get("status") in closed_states
                and valid_proof(row.get("completion_evidence") or row.get("evidence"))
                and (rid not in legacy or legacy[rid].get("status") in closed_states)):
            closed.add(rid)
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
            if source == 'unified' and state in closed_states and not valid_proof(row.get('completion_evidence') or row.get('evidence')):
                errors.append('INVALID_COMPLETION_PROOF:' + rid)
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
    # The checkpoint report is the canonical INTERNAL-OPEN projection.  The
    # root ledger can also contain externally blocked/incomplete work, which
    # must remain visible in ``remaining`` without being relabelled as an
    # internal OPEN.
    canonical_open = set(root_report.get("open_internal_roots", []))
    if not canonical_open.issubset(rows): errors.append("UNRESOLVED_TASK_LOST")
    # ``root_report`` is a checkpoint projection and may legitimately lag the
    # unified ledger.  The observer's actionable OPEN count must come from the
    # same classified rows as the visible lists, otherwise it can show OPEN 0
    # beside immediate pending work.  Keep the checkpoint count separately for
    # audit/read-back instead of presenting it as the live count.
    actionable_open = {r["root_id"] for r in running + pending}
    recent = [{"root_id": r["id"], "label": r.get("completion_label", r["id"]), "evidence": r["completion_evidence"]}
              for r in ledger["roots"] if r["id"] in closed and r.get("completion_evidence")]
    recent.extend({"root_id": r["root_id"], "label": r.get("completion_label", r["root_id"]), "evidence": r["completion_evidence"]}
                  for r in unified["entries"] if r.get("root_id") in closed
                  and r.get("root_id") not in legacy and r.get("completion_evidence"))
    return {"remaining": list(rows.values()), "running": running, "waiting": waiting, "pending": pending,
            "remaining_total": len(rows), "running_total": len(running), "waiting_total": len(waiting),
            "pending_total": len(pending), "open_internal_total": len(actionable_open),
            "open_internal_roots": sorted(actionable_open),
            "checkpoint_open_internal_total": len(canonical_open),
            "checkpoint_open_internal_roots": sorted(canonical_open),
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
    chat_coordination = run_chat_coordinator(ROOT / "tool043" / "chat_job_inbox.json",
                                              ROOT / "tool043" / "chat_coordination_state.json")
    function_state_path = PIPE / "tool044_function_state.json"
    function_state = json.loads(function_state_path.read_text(encoding="utf-8")) if function_state_path.exists() else {
        "classification_counts": {}, "functions": [], "observer_labels": {},
        "status": "NOT_GENERATED"
    }
    factory_state_path = PIPE / "tool044_factory_runtime.json"
    factory_state = json.loads(factory_state_path.read_text(encoding="utf-8")) if factory_state_path.exists() else {}
    cloud_state_path = PIPE / "tool044_cloud_state.json"
    cloud_state = json.loads(cloud_state_path.read_text(encoding="utf-8")) if cloud_state_path.exists() else {}
    local_required_path = PIPE / "tool044_local_required_queue.json"
    local_required = json.loads(local_required_path.read_text(encoding="utf-8")) if local_required_path.exists() else {}
    atomic_queue_path = PIPE / "tool044_atomic_demand_queue.json"
    atomic_queue = json.loads(atomic_queue_path.read_text(encoding="utf-8")) if atomic_queue_path.exists() else {"demands": []}
    registry_path = PIPE / "VERIFIED_COMPONENT_REGISTRY.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {}
    composition_path = PIPE / "evidence" / "tool044_verified_composition_pool.json"
    compositions = json.loads(composition_path.read_text(encoding="utf-8")) if composition_path.exists() else {"compositions": []}
    candidates_path = PIPE / "evidence" / "tool044_dynamic_candidate_pool.json"
    candidates = json.loads(candidates_path.read_text(encoding="utf-8")) if candidates_path.exists() else {}
    integration_path = PIPE / "evidence" / "tool044_safe_integration_fixture.json"
    integration = json.loads(integration_path.read_text(encoding="utf-8")) if integration_path.exists() else {}
    registry_rows = registry.get("components", []) + registry.get("verified_atomic_component_pool", [])
    verified_rows = [row for row in registry_rows if row.get("status") in {"VERIFIED_REUSABLE", "DEPLOYED_PASS"}]
    atomic_demands = atomic_queue.get("demands", [])
    open_demands = [row for row in atomic_demands if row.get("status", "OPEN") not in {"COMPLETED", "VERIFIED"}]
    current = current_work(ledger, roots, unified, work, incomplete, previous_queue)
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
        "tool044_trust_pipeline": previous_status.get("tool044_trust_pipeline"),
        "tool_function_improvement": {
            "source": "feedback_pipeline/tool044_function_state.json",
            "classification_counts": function_state.get("classification_counts", {}),
            "functions": function_state.get("functions", []),
            "observer_labels": function_state.get("observer_labels", {}),
            "truth_contract": "COMPONENT_VERIFIED_IS_NOT_IMPROVED_VERIFIED_UNTIL_TOOL_DEPLOYED_COPY_TEST_PASSES"
        },
        "tool044_factory_monitor": {
            "source": "feedback_pipeline/tool044_factory_runtime.json",
            "status": "RUNNING" if factory_state.get("active_workers", 0) else "READY",
            "current_stage": factory_state.get("current_stage", "IDLE"),
            "queue_length": factory_state.get("queue_length", 0),
            "active_workers": factory_state.get("active_workers", 0),
            "last_success": factory_state.get("last_success"),
            "last_failure": factory_state.get("last_failure"),
            "last_heartbeat": factory_state.get("last_heartbeat"),
            "checkpoint": factory_state.get("checkpoint"),
            "completed_jobs": factory_state.get("completed_jobs", 0),
            "execution_location": "LOCAL",
            "cloud": {
                "status": "VERIFIED" if cloud_state.get("trigger") == "GITHUB_ACTIONS" else cloud_state.get("status", "NOT_VERIFIED"),
                "checkpoint": cloud_state.get("checkpoint"),
                "jobs": len(cloud_state.get("jobs", {})),
                "deferred_backoff": cloud_state.get("deferred_backoff", 0),
                "paid_api_calls": cloud_state.get("paid_api_calls", 0),
                "paid_saas_calls": cloud_state.get("paid_saas_calls", 0),
            },
            "local_required_queue": local_required.get("queue_length", 0),
            "operational_counts": {
                "open_error_count": sum(1 for row in function_state.get("functions", []) if row.get("current_status") in {"REPEATED_ERROR", "FAIL"}),
                "open_capability_count": len(open_demands),
                "atomic_demand_count": len(atomic_demands),
                "external_candidates_found": candidates.get("candidate_count", 0),
                "verified_component_count": len(verified_rows),
                "verified_atomic_count": len(registry.get("verified_atomic_component_pool", [])),
                "verified_composition_count": len(compositions.get("compositions", [])),
                "rejected_component_count": sum(1 for row in registry_rows if row.get("status") in {"REJECTED", "FAIL", "BROKEN"}),
                "shell_suspect_count": sum(1 for row in registry_rows if row.get("status") in {"SHELL", "DRAFT", "PARTIAL", "UNKNOWN", "TEST_NOT_RUN"}),
                "ready_for_integration_count": sum(1 for row in compositions.get("compositions", []) if row.get("ready_for_integration") is True),
                "deployed_count": sum(1 for row in registry_rows if row.get("status") == "DEPLOYED_PASS"),
                "fixture_rollback_verified": integration.get("safe_fixture_auto_rollback") == "VERIFIED",
                "blocked_count": current["waiting_total"],
                "user_action_queue": len(approvals.get("batches", [])),
            },
            "safe_integration_truth": {
                "fixture_deploy_gate": integration.get("safe_fixture_deploy_gate", "NOT_VERIFIED"),
                "fixture_auto_rollback": integration.get("safe_fixture_auto_rollback", "NOT_VERIFIED"),
                "arbitrary_wic_tool_auto_deploy": integration.get("arbitrary_wic_tool_auto_deploy", "NOT_IMPLEMENTED"),
            },
        },
        "chat_work_coordination": chat_coordination,
        "current_display_validation": previous_status.get("current_display_validation"),
        "work_status": "작업 문제 있음" if open_count else ("작업 진행 중" if current["running"] else ("작업 대기 중" if current["pending"] or blocked else "현재 미처리 작업 없음")),
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
        "execution_bridge": {
            "state": "OBSERVATION_BRIDGE_CONNECTED",
            "executor": "GITHUB_ACTIONS_SCHEDULED_BATCH",
            "observed_sources": [
                "CENTRAL_ROOT_LEDGER", "UNIFIED_OPEN_LEDGER",
                "INCOMPLETE_REGISTER", "SAFE_CHECKPOINT", "TOOL044_TRUST_PIPELINE"
            ],
            "tool_work_orchestration": "QUEUE_HANDOFF_IMPLEMENTED",
            "parallel_tool_execution": "NOT_IMPLEMENTED",
            "automatic_tool_recovery": "NOT_IMPLEMENTED",
            "observer_refresh_recovery": "QUEUE_PRESERVED_ONE_SAFE_REFRESH",
            "chat_auto_execution": "NOT_PROVEN",
            "truth_contract": "QUEUE_HANDOFF_ONLY_DO_NOT_CLAIM_CHATGPT_AUTO_EXECUTION"
        },
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
    # A classic script is readable from file://, unlike fetch(status.json).
    # It makes the deployed folder fail-safe when index.html is double-clicked;
    # HTTP/Pages still fetch status.json as the live source of truth.
    snapshot = "window.TOOL043_STATUS_SNAPSHOT = " + json.dumps(status, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (ROOT / "tool043" / "status_snapshot.js").write_text(snapshot, encoding="utf-8")
    (ROOT / "tool043" / "night_queue.json").write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "queue_items": len(queue["items"]), "mobile": status}, ensure_ascii=False))


def self_test() -> None:
    from copy import deepcopy
    ledger = {"roots": [{"id": "done", "status": "REMOTE_VERIFIED", "completion_evidence": {"commit": "a" * 40}}, {"id": "open", "status": "OPEN"}], "external_holds": [{"root": "wait", "status": "HOLD_EVIDENCE_WAITING"}]}
    root_report = {"open_internal_roots": ["open"]}
    args = [ledger, root_report, {"entries": [{"root_id": "done", "status": "OPEN"}, {"root_id": "open", "status": "OPEN"}]}, {"next_work_queue": []}, {"entries": []}, {"items": [{"root_id": "done"}, {"root_id": "wait"}]}]
    result = current_work(*args)
    assert {r['root_id'] for r in result['remaining']} == {'open', 'wait'}
    assert result['waiting_total'] == 1 and result['open_internal_total'] == 1
    assert result['remaining_total'] == 2 and result['conservation_pass']
    external_only = deepcopy(args)
    external_only[1]['open_internal_roots'] = []
    result = current_work(*external_only)
    assert result['open_internal_total'] == 1 and result['open_internal_roots'] == ['open']
    assert result['checkpoint_open_internal_total'] == 0 and result['remaining_total'] == 2
    no_proof = deepcopy(args)
    no_proof[0]['roots'][0].pop('completion_evidence')
    result = current_work(*no_proof)
    assert result['remaining_total'] == 3 and not result['conservation_pass']
    running = deepcopy(args)
    running[3]['next_work_queue'] = [{'root_id': 'new-task', 'status': 'RUNNING'}]
    result = current_work(*running)
    assert result['remaining_total'] == 3 and result['running_total'] == 1
    assert result['remaining_total'] == result['waiting_total'] + result['running_total'] + result['pending_total']
    print('PASS: task conservation, evidence-backed closure, duplicate dedup, unproven completion blocked, explicit running task')


if __name__ == "__main__":
    self_test() if "--self-test" in sys.argv else main()
