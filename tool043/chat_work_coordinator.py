"""Deterministic TOOL043 chat-job handoff coordinator.

It routes declared chat results; it neither captures nor executes ChatGPT chats.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ERROR_STATES = {"FAIL", "PARTIAL", "HOLD", "REPEATED_ERROR", "ACTUAL_USE_FAILURE"}
CAPABILITY_STATES = {"MISSING_CAPABILITY", "NO_READY_COMPONENT", "REPEATED_ERROR", "EXTERNAL_COMPONENT_REQUIRED"}
COMPONENT_READY = {"COMPONENT_VERIFIED", "FRAMEWORK_VERIFIED", "COMPOSITION_VERIFIED", "READY_FOR_INTEGRATION"}
COMPLETE_STATES = {"PASS", "COMPLETE", "DEPLOYED_PASS"}
REQUIRED = {"CHAT_JOB_ID", "RELATED_TOOL", "JOB_PURPOSE", "RESULT", "STATUS", "REMAINING_WORK", "ERROR", "NEXT_REQUIRED_CAPABILITY", "NEXT_ACTION"}


def empty_state() -> dict:
    return {"schema_version": 1, "chat_auto_execution": "NOT_PROVEN", "processed_event_ids": [],
            "jobs": {}, "zero_work_execution_queue": [], "tool016_error_root_intake": [],
            "tool044_request_demand_queue": [], "chat_resume_queue": [], "work_approval_queue": []}


def route(events: list[dict], previous: dict | None = None) -> dict:
    state = previous or empty_state()
    seen = set(state.get("processed_event_ids", []))
    changed = False
    for event in events:
        missing = REQUIRED - set(event)
        if missing:
            raise ValueError("CHAT_JOB_FIELDS_MISSING:" + ",".join(sorted(missing)))
        event_id = event.get("EVENT_ID") or f'{event["CHAT_JOB_ID"]}:{event["STATUS"]}:{event["RESULT"]}'
        if event_id in seen:
            continue
        changed = True
        seen.add(event_id)
        job_id, status = event["CHAT_JOB_ID"], event["STATUS"]
        state["jobs"][job_id] = dict(event)
        envelope = {"EVENT_ID": event_id, "CHAT_JOB_ID": job_id, "RELATED_TOOL": event["RELATED_TOOL"],
                    "STATUS": status, "NEXT_ACTION": event["NEXT_ACTION"]}
        if status in ERROR_STATES:
            state["tool016_error_root_intake"].append({**envelope, "ERROR": event["ERROR"],
                                                       "RESULT": event["RESULT"]})
        if status in CAPABILITY_STATES or event["NEXT_REQUIRED_CAPABILITY"]:
            state["tool044_request_demand_queue"].append({**envelope,
                "CAPABILITY": event["NEXT_REQUIRED_CAPABILITY"], "SEARCH_ALLOWED": status in CAPABILITY_STATES})
        if status in COMPONENT_READY and event.get("PARENT_CHAT_JOB_ID"):
            state["chat_resume_queue"].append({**envelope, "CHAT_JOB_ID": event["PARENT_CHAT_JOB_ID"],
                                                "RESUME_REASON": status})
        elif event["NEXT_ACTION"] == "ZERO_WORK_EXECUTION" and event["REMAINING_WORK"]:
            state["zero_work_execution_queue"].append({**envelope, "WORK": event["REMAINING_WORK"]})
        elif event["NEXT_ACTION"] == "WORK_APPROVAL_REQUIRED":
            state["work_approval_queue"].append({**envelope, "WORK": event["REMAINING_WORK"],
                                                  "APPROVED": False})
    state["processed_event_ids"] = sorted(seen)
    if changed or "updated_at" not in state:
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
    state["counts"] = {key: len(state[key]) for key in ("jobs", "zero_work_execution_queue",
        "tool016_error_root_intake", "tool044_request_demand_queue", "chat_resume_queue", "work_approval_queue")}
    statuses = [job.get("STATUS") for job in state["jobs"].values()]
    state["display_counts"] = {
        "running_chat_jobs": sum(s in {"RUNNING", "IN_PROGRESS"} for s in statuses),
        "completed_chat_jobs": sum(s in COMPLETE_STATES for s in statuses),
        "zero_work_handoffs": state["counts"]["zero_work_execution_queue"],
        "tool016_error_handoffs": state["counts"]["tool016_error_root_intake"],
        "tool044_searching": sum(row.get("SEARCH_ALLOWED") is True for row in state["tool044_request_demand_queue"]),
        "tool044_component_ready": sum(s in COMPONENT_READY for s in statuses),
        "resume_waiting": state["counts"]["chat_resume_queue"],
        "work_approval_required": state["counts"]["work_approval_queue"],
        "deploying": sum(s == "DEPLOYING" for s in statuses),
        "final_complete": sum(s == "DEPLOYED_PASS" for s in statuses),
    }
    return state


def run(inbox: Path, state_path: Path) -> dict:
    source = json.loads(inbox.read_text(encoding="utf-8")) if inbox.exists() else {"events": []}
    prior = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else None
    state = route(source.get("events", []), prior)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    print(json.dumps(run(root / "chat_job_inbox.json", root / "chat_coordination_state.json"), ensure_ascii=False))
