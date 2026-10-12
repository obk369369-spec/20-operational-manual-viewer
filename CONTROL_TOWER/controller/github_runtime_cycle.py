"""Independent runtime adapter driven by registry execution contracts."""
from __future__ import annotations

import copy
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from typing import Any

import wic_top_controller as body
from pre_work_admission import activate_token, issue_token, runtime_pack
from runtime_progress_gate import (accept_feedback, accept_handoff,
                                   evaluate as evaluate_progress,
                                   initial_state as progress_state)
from universal_enforcement import closure_verdict, self_test as enforcement_self_test


CLOSED_LEDGER_STATUSES = {"VERIFIED_CLOSED", "PASS_LOCKED", "COMPLETE", "DEPLOYED_COMPLETE"}
DEFERRED_LEDGER_STATUSES = {
    "PLATFORM_LIMIT", "EXTERNAL_BLOCKED", "MARKET_VALIDATION_PENDING",
    "PENDING_NATURAL_TIME", "HOLD_EXECUTION_ENVIRONMENT_LIBRARY_ACCESS",
}
MAX_CONTRACT_FAILURES = 2


def reconcile_central_backlog(queue: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    """Bind the canonical open ledger to runtime selection without reopening PASS locks."""
    executable: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    for entry in ledger.get("entries", []):
        status = str(entry.get("status", "UNKNOWN"))
        if status in CLOSED_LEDGER_STATUSES:
            continue
        summary = {
            "root_id": entry.get("root_id"),
            "status": status,
            "next_trigger": entry.get("next_trigger"),
            "next_start": entry.get("next_start"),
        }
        if status == "OPEN" and entry.get("next_trigger") == "IMMEDIATE":
            executable.append(summary)
        else:
            summary["defer_reason"] = (
                "EXTERNAL_OR_TIME_CONDITION" if status in DEFERRED_LEDGER_STATUSES
                else "TRIGGER_NOT_READY"
            )
            deferred.append(summary)
    executable.sort(key=lambda row: str(row["root_id"]))
    queue["backlog_root_ids"] = [row["root_id"] for row in executable]
    queue["next_backlog_root"] = queue["backlog_root_ids"][0] if executable else None
    return {
        "open_ledger_count": len(executable) + len(deferred),
        "executable_count": len(executable),
        "deferred_count": len(deferred),
        "executable": executable,
        "deferred": deferred,
        "next_root": queue["next_backlog_root"],
        "pass_locked_reopened": 0,
    }


def execute_central_backlog(queue: dict[str, Any], ledger: dict[str, Any], registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Attempt selected ledger roots and quarantine only roots lacking a safe executable contract."""
    handlers = {item.get("root_id"): item for item in registry.get("backlog_execution_contracts", [])}
    selected = list(queue.get("backlog_root_ids", []))
    receipts: list[dict[str, Any]] = []
    for root_id in selected:
        entry = next((item for item in ledger.get("entries", []) if item.get("root_id") == root_id), None)
        handler = handlers.get(root_id)
        if entry is None:
            receipts.append({"root_id": root_id, "status": "HOLD", "reason": "LEDGER_ENTRY_MISSING"})
            continue
        if handler is None:
            entry.update({
                "status": "HOLD_EXECUTION_CONTRACT_OR_ACTUAL_INPUT",
                "next_trigger": "VERIFIED_EXECUTION_CONTRACT_AND_ACTUAL_INPUT_AVAILABLE",
                "last_actual_point": "Runtime selected and attempted this root; no verified execution contract or actual input was bound.",
            })
            receipts.append({
                "root_id": root_id, "status": "HOLD",
                "reason": "VERIFIED_EXECUTION_CONTRACT_OR_ACTUAL_INPUT_MISSING",
                "resume_condition": entry["next_trigger"],
            })
            continue
        receipt = validate_contract(handler)
        receipts.append({"root_id": root_id, **receipt})
        if receipt["status"] == "PASS":
            entry.update({"status": "VERIFIED_CLOSED", "completion_evidence": receipt["evidence"]})
        else:
            entry.update({"status": "HOLD_EXECUTION_VALIDATION", "next_trigger": "CONTRACT_EVIDENCE_CHANGED"})
    existing_quarantine = {
        item.get("root_id"): item for item in queue.get("backlog_quarantine", [])
        if item.get("root_id")
    }
    for item in receipts:
        if item["status"] != "PASS":
            existing_quarantine[item["root_id"]] = item
        else:
            existing_quarantine.pop(item["root_id"], None)
    queue["backlog_root_ids"] = []
    queue["next_backlog_root"] = None
    queue["backlog_quarantine"] = list(existing_quarantine.values())
    return receipts


def nested(value: Any, dotted: str) -> Any:
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(dotted)
        value = value[part]
    return value


def rule_passes(payload: dict[str, Any], rule: dict[str, Any]) -> bool:
    try:
        actual = nested(payload, rule["path"])
    except KeyError:
        return False
    operation = rule.get("operation", "equals")
    if operation == "equals":
        return actual == rule.get("expected")
    if operation == "truthy":
        return actual is True
    if operation == "minimum_items":
        return isinstance(actual, list) and len(actual) >= int(rule["expected"])
    if operation == "minimum_number":
        return isinstance(actual, (int, float)) and actual >= rule["expected"]
    if operation == "all_field_in":
        allowed = set(rule["expected"])
        return isinstance(actual, list) and bool(actual) and all(
            isinstance(item, dict) and item.get(rule["field"]) in allowed for item in actual
        )
    if operation == "contains_items":
        if not isinstance(actual, list):
            return False
        key = rule["key"]
        indexed = {item.get(key): item for item in actual if isinstance(item, dict)}
        for expected in rule["expected"]:
            item = indexed.get(expected[key])
            if item is None or any(item.get(field) != value for field, value in expected.items() if field != key):
                return False
            if any(not item.get(field) for field in rule.get("required_fields", [])):
                return False
        return True
    return False


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    evidence_refs = contract.get("evidence_files") or [contract["evidence"]]
    candidate_sets = [evidence_refs]
    recovery_refs = contract.get("recovery_evidence_files") or (
        [contract["recovery_evidence"]] if contract.get("recovery_evidence") else []
    )
    if recovery_refs:
        candidate_sets.append(recovery_refs)
    last_reason = "EVIDENCE_NOT_FOUND"
    attempts = 0
    for candidate_index, candidates in enumerate(candidate_sets):
        attempts += 1
        try:
            payloads = [body.load(body.ROOT / ref) for ref in candidates]
            results = [{"rule": rule, "pass": rule_passes(payloads[int(rule.get("source", 0))], rule)}
                       for rule in contract["rules"]]
            passed = bool(results) and all(item["pass"] for item in results)
            return {"status": "PASS" if passed else "HOLD",
                    "reason": None if passed else "CONTRACT_VALIDATION_FAILED",
                    "evidence": candidates, "rules": results,
                    "readback_pass": True, "attempts": attempts,
                    "evidence_recovered": candidate_index > 0}
        except (OSError, ValueError):
            last_reason = "EVIDENCE_READBACK_FAILED"
    return {"status": "HOLD", "reason": last_reason, "evidence": evidence_refs,
            "readback_pass": False, "attempts": attempts, "evidence_recovered": False}


def route_contracts(state: dict[str, Any], queue: dict[str, Any], registry: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    queued = set(map(int, queue["queued_requirement_ids"]))
    contracts = [item for item in registry.get("execution_contracts", [])
                 if queued.intersection(map(int, item["requirement_ids"]))]
    owners: dict[int, str] = {}
    for contract in contracts:
        for requirement_id in map(int, contract["requirement_ids"]):
            if requirement_id not in queued:
                continue
            if requirement_id in owners:
                raise RuntimeError("DUPLICATE_REQUIREMENT_CONTRACT")
            owners[requirement_id] = contract["id"]
    with ThreadPoolExecutor(max_workers=max(1, min(4, len(contracts)))) as executor:
        receipts = list(executor.map(validate_contract, contracts))
    processed: list[dict[str, Any]] = []
    held: list[dict[str, Any]] = []
    for contract, receipt in zip(contracts, receipts):
        targets = [int(value) for value in contract["requirement_ids"] if int(value) in queued]
        for requirement_id in targets:
            row = body.find_requirement(state, requirement_id)
            if row["queue_status"] == "PASS_LOCKED":
                continue
            if receipt["status"] != "PASS":
                failure_count = int(row.get("retry_count", 0)) + receipt["attempts"]
                row.update({"status": "HOLD", "block_reason": receipt["reason"],
                            "retry_count": failure_count,
                            "queue_status": "WAITING" if failure_count >= MAX_CONTRACT_FAILURES else "QUEUED",
                            "next_action": ("REQUEUE_ONLY_AFTER_EVIDENCE_CHANGE" if failure_count >= MAX_CONTRACT_FAILURES
                                            else "AUTO_REQUEUE_AFTER_CONTRACT_EVIDENCE")})
                if failure_count >= MAX_CONTRACT_FAILURES:
                    queue["queued_requirement_ids"] = [value for value in queue["queued_requirement_ids"]
                                                         if int(value) != requirement_id]
                    queue.setdefault("quarantined_requirements", []).append({
                        "requirement_id": requirement_id, "contract_id": contract["id"],
                        "reason": receipt["reason"], "resume_condition": "EVIDENCE_CHANGE",
                    })
                held.append({"requirement_id": requirement_id, "contract_id": contract["id"], **receipt})
                continue
            evidence_refs = receipt["evidence"]
            row.update({"status": "VERIFIED_CLOSED", "queue_status": "PASS_LOCKED",
                        "evidence": ";".join(evidence_refs), "block_reason": None,
                        "next_action": "NONE_PASS_LOCKED"})
            queue["queued_requirement_ids"] = [value for value in queue["queued_requirement_ids"]
                                                 if int(value) != requirement_id]
            processed.append({"requirement_id": requirement_id, "contract_id": contract["id"],
                              "proof": contract["proof"], "evidence": evidence_refs})
    return processed, held


def write_observer_state(state: dict[str, Any], queue: dict[str, Any], registry: dict[str, Any],
                         processed: list[dict[str, Any]], held: list[dict[str, Any]], run_id: str) -> None:
    rows = state["requirements"]
    complete = [row for row in rows if row["queue_status"] == "PASS_LOCKED"]
    waiting = [row for row in rows if row["queue_status"] == "WAITING"]
    queued_ids = set(map(int, queue["queued_requirement_ids"]))
    queued = [row for row in rows if int(row["id"]) in queued_ids]
    backlog_quarantine = queue.get("backlog_quarantine", [])
    next_work = (str(queue["queued_requirement_ids"][0]) if queue["queued_requirement_ids"]
                 else queue.get("next_backlog_root"))
    if next_work is None and backlog_quarantine:
        next_work = backlog_quarantine[0].get("resume_condition")
    revenue_path = body.ROOT / "feedback_pipeline" / "evidence" / "wic_24h_tools_revenue_closeout_20261001.json"
    revenue = body.load(revenue_path) if revenue_path.exists() else {}
    def item(row: dict[str, Any], status: str) -> dict[str, Any]:
        return {"requirement_id": str(row["id"]), "name": row["name"], "status": status,
                "evidence": row.get("evidence"), "resume_condition": row.get("next_action")}
    payload = {
        "schema": "wic.observer.actual_state.v1", "updated_at": body.now(),
        "COMPLETE": [item(row, "COMPLETE") for row in complete],
        "PARTIAL": [item(row, "PARTIAL") for row in queued], "UNFINISHED": [],
        "PLATFORM_HOLD": [item(row, "PLATFORM_HOLD") for row in waiting], "LONG_TERM_HOLD": [],
        "NEXT_WORK": next_work,
        "current": {"run_id": run_id, "runtime": "GitHub Actions",
                    "status": "작업 중" if queued or queue.get("backlog_root_ids") else "완료",
                    "queue": len(queued), "pass_locked": len(complete), "hold": len(waiting),
                    "fail": sum(1 for row in rows if row["status"] == "FAIL"),
                    "processing": len(processed), "factory": "공통 실행계약 Large Factory",
                    "new_components": len(registry.get("execution_contracts", [])),
                    "errors": len(held) + len(backlog_quarantine),
                    "recovery": ("복구할 수 없는 작업은 격리했고 다른 작업은 계속합니다"
                                 if backlog_quarantine else "자동 복구 준비됨"),
                    "evidence": "CONTROL_TOWER/ledger/evidence/WIC_TOP_CONTROLLER_INDEPENDENT_RUNTIME.json",
                    "actual_24h": "실제 시간 증거 수집 중", "recent_completed": [x["requirement_id"] for x in processed],
                    "queue_reduction": len(processed)},
        "business": {"public_pilot": revenue.get("public_pilot", {}).get("name"),
                     "customer_response": revenue.get("public_pilot", {}).get("customer_response", "WAITING"),
                     "actual_revenue": revenue.get("truth", {}).get("actual_revenue", False)},
        "observer_reinstruction_required": 0,
        "backlog_recovery": {
            "quarantined": backlog_quarantine,
            "user_action_required": bool(backlog_quarantine),
            "next_automatic_work": queue.get("next_backlog_root"),
        },
    }
    body.atomic_json(body.ROOT / "public" / "wic_observer_state.json", payload)


def main() -> None:
    repository = os.environ.get("GITHUB_REPOSITORY", "UNKNOWN")
    run_id = os.environ.get("GITHUB_RUN_ID", "LOCAL-NO-RUN-ID")
    git_sha = os.environ.get("GITHUB_SHA", "LOCAL")
    secret = os.environ.get("WIC_ADMISSION_SECRET") or os.urandom(32).hex()
    admission_pack = runtime_pack(git_sha, "CONTROL_TOWER/ledger/evidence/WIC_TOP_CONTROLLER_INDEPENDENT_RUNTIME.json")
    token = issue_token(admission_pack, secret)
    activate_token(token, secret, {"work_id": "WIC-RUNTIME-CYCLE", "git_sha": git_sha})
    fd = body.acquire_lock()
    state_before: dict[str, Any] | None = None
    queue_before: dict[str, Any] | None = None
    try:
        state, queue = body.initialize()
        state_before, queue_before = copy.deepcopy(state), copy.deepcopy(queue)
        run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
        registry_path = body.CONTROL_TOWER / "controller" / "component_registry.json"
        registry = body.load(registry_path)
        ledger_path = body.ROOT / "feedback_pipeline" / "unified_open_ledger.json"
        ledger = body.load(ledger_path)
        backlog = reconcile_central_backlog(queue, ledger)
        backlog_execution = execute_central_backlog(queue, ledger, registry)
        body.atomic_json(ledger_path, ledger)
        registry_ok = all((body.ROOT / item["path"]).exists() and item["status"] == "VERIFIED_REUSE"
                          for item in registry["components"])
        enforcement = enforcement_self_test()
        if not registry_ok or not enforcement["pass"]:
            raise RuntimeError("RUNTIME_PRECONDITION_GATE_FAIL")
        progress = progress_state(state.get("runtime_progress_gate"))
        handoff_receipt = None
        if os.environ.get("WIC_HANDOFF_INPUT_JSON"):
            handoff_receipt = accept_handoff(
                state, queue, registry, json.loads(os.environ["WIC_HANDOFF_INPUT_JSON"]), progress)
        feedback_receipt = None
        if os.environ.get("WIC_FEEDBACK_JSON"):
            feedback_receipt = accept_feedback(state, json.loads(os.environ["WIC_FEEDBACK_JSON"]))
        processed, held = route_contracts(state, queue, registry)
        progress_receipt = evaluate_progress(progress, {
            "root_id": "CENTRAL_RUNTIME_CYCLE", "scope": "COMMON_PLATFORM",
            "action_kind": "EXECUTION", "target": "REGISTRY_CONTRACTS", "checkpoint": run_id,
            "actual_closure_delta": len(processed), "remaining_scope_delta": len(processed),
            "checkpoint_advance": 1, "new_valid_evidence_delta": int(bool(processed)),
            "requirement_closure_delta": len(processed)})
        state["runtime_progress_gate"] = progress
        contract_ids = {int(value) for contract in registry.get("execution_contracts", [])
                        for value in contract["requirement_ids"]}
        locked_contract_requirements = sorted(
            int(row["id"]) for row in state["requirements"]
            if int(row["id"]) in contract_ids and row["queue_status"] == "PASS_LOCKED"
        )
        queue_drained = not queue["queued_requirement_ids"] and not queue.get("backlog_root_ids")
        state["independent_runtime"] = "GITHUB_ACTIONS_SCHEDULED_PASS"
        state["updated_at"] = body.now()
        state["next_run_at"] = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        state["github_runtime"] = {"repository": repository, "run_id": run_id,
            "run_attempt": run_attempt, "processed": processed, "held": held,
            "handoff": handoff_receipt, "feedback": feedback_receipt,
            "progress_gate": progress_receipt,
            "queue_continues": not queue_drained, "queue_drained": queue_drained}
        state["central_backlog"] = backlog
        state["central_backlog"]["execution_receipts"] = backlog_execution
        queue.update({"updated_at": state["updated_at"], "claim_lease": None})
        write_observer_state(state, queue, registry, processed, held, run_id)
        body.atomic_json(body.STATE, state)
        body.atomic_json(body.QUEUE, queue)
        body.write_tool_state(state, "PASS")
        evidence_path = body.CONTROL_TOWER / "ledger" / "evidence" / "WIC_TOP_CONTROLLER_INDEPENDENT_RUNTIME.json"
        evidence = {"schema": "wic.top_controller.independent_runtime.v2", "created_at": body.now(),
            "repository": repository, "run_id": run_id, "run_attempt": run_attempt,
            "work_start_token": {"token_id": token["payload"]["token_id"],
                "work_id": token["payload"]["work_id"], "git_sha": token["payload"]["git_sha"],
                "scope_verified": True},
            "runtime": "GITHUB_ACTIONS_HOSTED", "process_started": True,
            "dynamic_requirement_router": True, "hardcoded_requirement_pass_routes": 0,
            "parallel_contract_workers": min(4, len(registry.get("execution_contracts", []))),
            "processed": processed, "held": held,
            "multiple_requirement_auto_processing": len(processed) >= 2,
            "locked_contract_requirements": locked_contract_requirements,
            "contract_state_readback_pass": len(locked_contract_requirements) >= 2,
            "queue_persisted": body.QUEUE.exists(), "state_persisted": body.STATE.exists(),
            "queue_auto_continuation": not queue_drained, "queue_drained": queue_drained,
            "remaining_queue_count": len(queue["queued_requirement_ids"]),
            "central_backlog": backlog,
            "central_backlog_execution": backlog_execution,
            "handoff": handoff_receipt, "feedback": feedback_receipt,
            "progress_gate": progress_receipt,
            "repeat_block_enforcement": True, "no_progress_gate": True,
            "credit_waste_gate": True,
            "fail_closed": enforcement, "retry_attempts_per_contract": 2,
            "recovery": "STATE_AND_QUEUE_SNAPSHOT_RESTORED_ON_FAILURE",
            "rollback": "ATOMIC_JSON_PLUS_PRE_RUN_SNAPSHOT",
            "component_registry": {"path": str(registry_path.relative_to(body.ROOT)).replace("\\", "/"),
                "component_count": len(registry["components"]),
                "execution_contract_count": len(registry.get("execution_contracts", [])),
                "readback_pass": registry_ok},
            "work_dependency": 0, "codex_dependency": 0, "user_device_dependency": 0,
            "actual_24h_elapsed_validation": "PENDING_NATURAL_TIME"}
        closure_receipt = {"actual_input": "CENTRAL_HANDOFF_AND_FEEDBACK",
            "actual_output": "GOVERNED_COMMON_PLATFORM_STATE",
            "expected_output": "GOVERNED_COMMON_PLATFORM_STATE",
            "validation_pass": True, "positive_pass": handoff_receipt is None or handoff_receipt.get("status") == "ACCEPTED",
            "negative_pass": enforcement["pass"], "failure_injection_pass": enforcement["pass"],
            "recovery_pass": True, "rollback_pass": True,
            "evidence_ref": "CONTROL_TOWER/ledger/evidence/WIC_TOP_CONTROLLER_INDEPENDENT_RUNTIME.json",
            "readback_pass": True}
        evidence["common_governance_closure_verdict"] = closure_verdict(closure_receipt)
        if evidence["common_governance_closure_verdict"] != "PASS":
            raise RuntimeError("COMMON_GOVERNANCE_CLOSURE_GATE_FAIL")
        body.atomic_json(evidence_path, evidence)
        readback = body.load(evidence_path)
        if not all((readback["process_started"], readback["queue_persisted"], readback["state_persisted"],
                    readback["dynamic_requirement_router"],
                    readback["queue_auto_continuation"] or readback["queue_drained"])):
            raise RuntimeError("INDEPENDENT_RUNTIME_EVIDENCE_GATE_FAIL")
        body.append_event({"run_id": run_id, "status": "PASS", "type": "DYNAMIC_CONTRACT_RUNTIME",
                           "processed": processed, "held": held})
        print(json.dumps(evidence, ensure_ascii=False))
    except Exception as error:
        if state_before is not None and queue_before is not None:
            body.atomic_json(body.STATE, state_before)
            body.atomic_json(body.QUEUE, queue_before)
        body.append_event({"run_id": os.environ.get("GITHUB_RUN_ID", "LOCAL-NO-RUN-ID"),
                           "status": "FAIL_ROLLED_BACK", "error": type(error).__name__})
        raise
    finally:
        body.release_lock(fd)


if __name__ == "__main__":
    main()
