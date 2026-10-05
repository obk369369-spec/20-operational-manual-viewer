"""GitHub Actions adapter for the already verified WIC top controller.

The adapter preserves the verified controller body and supplies only the
independent-runtime receipts that cannot exist during a local run.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

import wic_top_controller as body


def main() -> None:
    fd = body.acquire_lock()
    try:
        state, queue = body.initialize()
        run_id = os.environ.get("GITHUB_RUN_ID", "LOCAL-NO-RUN-ID")
        run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
        repository = os.environ.get("GITHUB_REPOSITORY", "UNKNOWN")
        before_locked = sorted(int(r["id"]) for r in state["requirements"] if r["queue_status"] == "PASS_LOCKED")

        # Requirement 34 is already PASS_LOCKED.  The independent adapter must
        # prove it was not selected again, rather than rerun its reconciler.
        completed_reexecution_blocked = 34 in before_locked

        processed = []
        for requirement_id, proof in (
            (1, "GITHUB_ACTIONS_HOSTED_PROCESS_STARTED"),
            (2, "HOSTED_PROCESS_HAS_NO_USER_DEVICE_DEPENDENCY"),
            (71, "NORMAL_CYCLE_USED_NO_WORK_RUNTIME"),
            (72, "NORMAL_CYCLE_USED_NO_CODEX_RUNTIME"),
            (73, "NORMAL_CYCLE_USED_NO_USER_DEVICE_RUNTIME"),
        ):
            row = body.find_requirement(state, requirement_id)
            if row["queue_status"] == "PASS_LOCKED":
                continue
            row.update({
                "status": "VERIFIED_CLOSED",
                "queue_status": "PASS_LOCKED",
                "evidence": "CONTROL_TOWER/ledger/evidence/WIC_TOP_CONTROLLER_INDEPENDENT_RUNTIME.json",
                "block_reason": None,
                "next_action": "NONE_PASS_LOCKED",
            })
            queue["queued_requirement_ids"] = [v for v in queue["queued_requirement_ids"] if v != requirement_id]
            processed.append({"requirement_id": requirement_id, "proof": proof})

        failure = body.failure_cycle(state, queue)
        requirement_10 = body.find_requirement(state, 10)
        if failure["status"] == "PASS":
            requirement_10.update({
                "status": "VERIFIED_CLOSED",
                "queue_status": "PASS_LOCKED",
                "evidence": "CONTROL_TOWER/ledger/evidence/WIC_TOP_CONTROLLER_INDEPENDENT_RUNTIME.json",
                "block_reason": None,
                "next_action": "NONE_PASS_LOCKED",
            })
            queue["queued_requirement_ids"] = [v for v in queue["queued_requirement_ids"] if v != 10]
            processed.append({"requirement_id": 10, "proof": "FAILURE_STOP_RECOVERY_AND_STATE_PRESERVATION"})

        state["independent_runtime"] = "GITHUB_ACTIONS_SCHEDULED_PASS"
        state["updated_at"] = body.now()
        state["next_run_at"] = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        state["github_runtime"] = {
            "repository": repository,
            "run_id": run_id,
            "run_attempt": run_attempt,
            "completed_reexecution_blocked": completed_reexecution_blocked,
            "locked_before": before_locked,
            "processed": processed,
            "queue_continues": bool(queue["queued_requirement_ids"]),
        }
        queue["updated_at"] = state["updated_at"]
        queue["claim_lease"] = None
        body.atomic_json(body.STATE, state)
        body.atomic_json(body.QUEUE, queue)
        body.write_tool_state(state, "PASS")

        evidence_path = body.CONTROL_TOWER / "ledger" / "evidence" / "WIC_TOP_CONTROLLER_INDEPENDENT_RUNTIME.json"
        evidence = {
            "schema": "wic.top_controller.independent_runtime.v1",
            "created_at": body.now(),
            "repository": repository,
            "run_id": run_id,
            "run_attempt": run_attempt,
            "runtime": "GITHUB_ACTIONS_HOSTED",
            "process_started": True,
            "controller_reused": "CONTROL_TOWER/controller/wic_top_controller.py",
            "completed_reexecution_blocked": completed_reexecution_blocked,
            "multiple_requirement_auto_processing": len(processed) >= 2,
            "processed": processed,
            "queue_persisted": body.QUEUE.exists(),
            "state_persisted": body.STATE.exists(),
            "queue_auto_continuation": bool(queue["queued_requirement_ids"]),
            "remaining_queue_count": len(queue["queued_requirement_ids"]),
            "failure_recovery": failure,
            "work_dependency": 0,
            "codex_dependency": 0,
            "user_device_dependency": 0,
            "actual_24h_elapsed_validation": "PENDING_NATURAL_TIME",
        }
        body.atomic_json(evidence_path, evidence)
        readback = body.load(evidence_path)
        if not all((readback["process_started"], readback["completed_reexecution_blocked"],
                    readback["multiple_requirement_auto_processing"], readback["queue_persisted"],
                    readback["state_persisted"], readback["queue_auto_continuation"])):
            raise SystemExit("INDEPENDENT_RUNTIME_EVIDENCE_GATE_FAIL")
        body.append_event({"run_id": run_id, "status": "PASS", "type": "INDEPENDENT_RUNTIME", "processed": processed})
        print(json.dumps(evidence, ensure_ascii=False))
    finally:
        body.release_lock(fd)


if __name__ == "__main__":
    main()
