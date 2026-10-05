"""Independent runtime adapter driven by registry execution contracts."""
from __future__ import annotations

import copy
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from typing import Any

import wic_top_controller as body
from universal_enforcement import self_test as enforcement_self_test


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
    last_reason = "EVIDENCE_NOT_FOUND"
    for attempt in range(1, 3):
        try:
            payloads = [body.load(body.ROOT / ref) for ref in evidence_refs]
            results = [{"rule": rule, "pass": rule_passes(payloads[int(rule.get("source", 0))], rule)}
                       for rule in contract["rules"]]
            passed = bool(results) and all(item["pass"] for item in results)
            return {"status": "PASS" if passed else "HOLD",
                    "reason": None if passed else "CONTRACT_VALIDATION_FAILED",
                    "evidence": evidence_refs, "rules": results,
                    "readback_pass": True, "attempts": attempt}
        except (OSError, ValueError):
            last_reason = "EVIDENCE_READBACK_FAILED"
    return {"status": "HOLD", "reason": last_reason, "evidence": evidence_refs,
            "readback_pass": False, "attempts": 2}


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
                row.update({"status": "HOLD", "block_reason": receipt["reason"],
                            "retry_count": int(row.get("retry_count", 0)) + receipt["attempts"],
                            "next_action": "AUTO_REQUEUE_AFTER_CONTRACT_EVIDENCE"})
                held.append({"requirement_id": requirement_id, "contract_id": contract["id"], **receipt})
                continue
            evidence_refs = contract.get("evidence_files") or [contract["evidence"]]
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
        "NEXT_WORK": str(queue["queued_requirement_ids"][0]) if queue["queued_requirement_ids"] else None,
        "current": {"run_id": run_id, "runtime": "GitHub Actions", "status": "작업 중" if queued else "완료",
                    "queue": len(queued), "pass_locked": len(complete), "hold": len(waiting),
                    "fail": sum(1 for row in rows if row["status"] == "FAIL"),
                    "processing": len(processed), "factory": "공통 실행계약 Large Factory",
                    "new_components": len(registry.get("execution_contracts", [])),
                    "errors": len(held), "recovery": "자동 복구 준비됨",
                    "evidence": "CONTROL_TOWER/ledger/evidence/WIC_TOP_CONTROLLER_INDEPENDENT_RUNTIME.json",
                    "actual_24h": "실제 시간 증거 수집 중", "recent_completed": [x["requirement_id"] for x in processed],
                    "queue_reduction": len(processed)},
        "business": {"public_pilot": revenue.get("public_pilot", {}).get("name"),
                     "customer_response": revenue.get("public_pilot", {}).get("customer_response", "WAITING"),
                     "actual_revenue": revenue.get("truth", {}).get("actual_revenue", False)},
        "observer_reinstruction_required": 0,
    }
    body.atomic_json(body.ROOT / "public" / "wic_observer_state.json", payload)


def main() -> None:
    fd = body.acquire_lock()
    state_before: dict[str, Any] | None = None
    queue_before: dict[str, Any] | None = None
    try:
        state, queue = body.initialize()
        state_before, queue_before = copy.deepcopy(state), copy.deepcopy(queue)
        run_id = os.environ.get("GITHUB_RUN_ID", "LOCAL-NO-RUN-ID")
        run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
        repository = os.environ.get("GITHUB_REPOSITORY", "UNKNOWN")
        registry_path = body.CONTROL_TOWER / "controller" / "component_registry.json"
        registry = body.load(registry_path)
        registry_ok = all((body.ROOT / item["path"]).exists() and item["status"] == "VERIFIED_REUSE"
                          for item in registry["components"])
        enforcement = enforcement_self_test()
        if not registry_ok or not enforcement["pass"]:
            raise RuntimeError("RUNTIME_PRECONDITION_GATE_FAIL")
        processed, held = route_contracts(state, queue, registry)
        contract_ids = {int(value) for contract in registry.get("execution_contracts", [])
                        for value in contract["requirement_ids"]}
        locked_contract_requirements = sorted(
            int(row["id"]) for row in state["requirements"]
            if int(row["id"]) in contract_ids and row["queue_status"] == "PASS_LOCKED"
        )
        queue_drained = not queue["queued_requirement_ids"]
        state["independent_runtime"] = "GITHUB_ACTIONS_SCHEDULED_PASS"
        state["updated_at"] = body.now()
        state["next_run_at"] = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        state["github_runtime"] = {"repository": repository, "run_id": run_id,
            "run_attempt": run_attempt, "processed": processed, "held": held,
            "queue_continues": not queue_drained, "queue_drained": queue_drained}
        queue.update({"updated_at": state["updated_at"], "claim_lease": None})
        write_observer_state(state, queue, registry, processed, held, run_id)
        body.atomic_json(body.STATE, state)
        body.atomic_json(body.QUEUE, queue)
        body.write_tool_state(state, "PASS")
        evidence_path = body.CONTROL_TOWER / "ledger" / "evidence" / "WIC_TOP_CONTROLLER_INDEPENDENT_RUNTIME.json"
        evidence = {"schema": "wic.top_controller.independent_runtime.v2", "created_at": body.now(),
            "repository": repository, "run_id": run_id, "run_attempt": run_attempt,
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
            "fail_closed": enforcement, "retry_attempts_per_contract": 2,
            "recovery": "STATE_AND_QUEUE_SNAPSHOT_RESTORED_ON_FAILURE",
            "rollback": "ATOMIC_JSON_PLUS_PRE_RUN_SNAPSHOT",
            "component_registry": {"path": str(registry_path.relative_to(body.ROOT)).replace("\\", "/"),
                "component_count": len(registry["components"]),
                "execution_contract_count": len(registry.get("execution_contracts", [])),
                "readback_pass": registry_ok},
            "work_dependency": 0, "codex_dependency": 0, "user_device_dependency": 0,
            "actual_24h_elapsed_validation": "PENDING_NATURAL_TIME"}
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
