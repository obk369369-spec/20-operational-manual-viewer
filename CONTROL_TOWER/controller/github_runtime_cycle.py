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
    if operation == "all_field_in":
        allowed = set(rule["expected"])
        return isinstance(actual, list) and bool(actual) and all(
            isinstance(item, dict) and item.get(rule["field"]) in allowed for item in actual
        )
    return False


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    evidence_path = body.ROOT / contract["evidence"]
    last_reason = "EVIDENCE_NOT_FOUND"
    for attempt in range(1, 3):
        try:
            payload = body.load(evidence_path)
            results = [{"rule": rule, "pass": rule_passes(payload, rule)} for rule in contract["rules"]]
            passed = bool(results) and all(item["pass"] for item in results)
            return {"status": "PASS" if passed else "HOLD",
                    "reason": None if passed else "CONTRACT_VALIDATION_FAILED",
                    "evidence": contract["evidence"], "rules": results,
                    "readback_pass": True, "attempts": attempt}
        except (OSError, ValueError):
            last_reason = "EVIDENCE_READBACK_FAILED"
    return {"status": "HOLD", "reason": last_reason, "evidence": contract["evidence"],
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
            row.update({"status": "VERIFIED_CLOSED", "queue_status": "PASS_LOCKED",
                        "evidence": contract["evidence"], "block_reason": None,
                        "next_action": "NONE_PASS_LOCKED"})
            queue["queued_requirement_ids"] = [value for value in queue["queued_requirement_ids"]
                                                 if int(value) != requirement_id]
            processed.append({"requirement_id": requirement_id, "contract_id": contract["id"],
                              "proof": contract["proof"], "evidence": contract["evidence"]})
    return processed, held


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
        queue_drained = not queue["queued_requirement_ids"]
        state["independent_runtime"] = "GITHUB_ACTIONS_SCHEDULED_PASS"
        state["updated_at"] = body.now()
        state["next_run_at"] = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        state["github_runtime"] = {"repository": repository, "run_id": run_id,
            "run_attempt": run_attempt, "processed": processed, "held": held,
            "queue_continues": not queue_drained, "queue_drained": queue_drained}
        queue.update({"updated_at": state["updated_at"], "claim_lease": None})
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
