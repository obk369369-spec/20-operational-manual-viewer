"""TOOL044 atomic watch compatibility fix.

The legacy watcher correctly avoids repeated external searches for 24 hours, but
it used DUPLICATE_SEARCH_BLOCKED as the whole demand result.  That hid already
verified matches and the still-missing capabilities.  This wrapper keeps the
external-search backoff while always publishing the current demand state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from tool044_atomic_watch import run_cycle, signature


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def _atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + ".tool044-pending")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def return_verified_results(queue_path: Path, registry_path: Path, state_path: Path,
                            state: dict, writer=_atomic_json) -> dict:
    """Cross-check independent inputs before acknowledging the existing TOOL016 contract."""
    root = queue_path.parent
    inbox_path, central_path = root / "TOOL044_REQUEST_INBOX.json", root / "state.json"
    if not inbox_path.exists() or not central_path.exists():
        return {"acknowledged": 0, "blocked": []}
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    inbox = json.loads(inbox_path.read_text(encoding="utf-8"))
    before = central_path.read_bytes()
    central = json.loads(before)
    checkpoints = central.get("integration_core", {}).get("feedback_checkpoints", {})
    results = state.get("results", [])
    result_by_id = {item.get("demand_id"): item for item in results}
    unique_results = len(result_by_id) == len(results)
    queue_demands = queue.get("demands", [])
    unique_demands = len({d.get("demand_id") for d in queue_demands}) == len(queue_demands)
    verified = registry.get("components", []) + registry.get("verified_atomic_component_pool", [])
    verified += json.loads((state_path.parent / "tool044_verified_external_component_pool.json").read_text(encoding="utf-8")).get("components", []) if (state_path.parent / "tool044_verified_external_component_pool.json").exists() else []
    capability_components = set()
    for item in verified:
        if item.get("status") != "VERIFIED_REUSABLE":
            continue
        artifact = item.get("source_file") or item.get("artifact")
        artifact_path = root.parent / artifact if artifact and not Path(artifact).is_absolute() else Path(artifact) if artifact else None
        expected_hash = item.get("source_sha256") or item.get("receipt_sha256")
        if (not artifact_path or not artifact_path.is_file() or not expected_hash or
            hashlib.sha256(artifact_path.read_bytes()).hexdigest() != expected_hash or
            (item.get("actual_sha256") and item["actual_sha256"] != expected_hash) or
            not item.get("sandbox_expected_actual") or
            item.get("sandbox_expected_actual") == "FAIL"):
            continue
        capability_components.update((cap, item.get("component_id")) for cap in
                                     item.get("atomic_capabilities", [item.get("atomic_capability")]))
    blocked, acknowledged, held = [], 0, 0
    updated_requests = set()
    for request in inbox.get("requests", []):
        request_id = str(request.get("request_id") or "")
        if not request_id or request_id not in checkpoints:
            continue
        demands = [d for d in queue_demands if str(d.get("request_id") or "") == request_id]
        if not demands:
            continue
        errors = []
        if not unique_demands or not unique_results:
            errors.append("DUPLICATE_DEMAND_OR_RESULT_ID")
        if any(d.get("root_id") != request.get("root_id") or
               not any(s.get("ROOT_ID") == request.get("root_id") and
                       s.get("TOOL044_DEMAND_ID") == d.get("demand_id") and
                       s.get("SOURCE_EVIDENCE") == request.get("source_evidence")
                       for s in d.get("source_records", [])) for d in demands):
            errors.append("SOURCE_LINEAGE_MISMATCH")
        demand_results = []
        for demand in demands:
            result = result_by_id.get(demand.get("demand_id"))
            receipt = state.get("receipts", {}).get(signature(demand))
            if not result or not receipt or result.get("query_signature") != signature(demand) or result != receipt:
                errors.append("RESULT_RECEIPT_MISMATCH:" + str(demand.get("demand_id")))
                continue
            capabilities = set(demand.get("atomic_capabilities", []))
            matched, missing = result.get("matched", {}), result.get("missing", [])
            expected = ("READY_ATOMIC_COMPONENT_FOUND" if matched and not missing else
                        "PARTIAL_ATOMIC_COMPONENT_SET" if matched else "NO_READY_ATOMIC_COMPONENT")
            if (set(matched) | set(missing) != capabilities or set(matched) & set(missing) or
                result.get("result") != expected or
                any((cap, component) not in capability_components for cap, component in matched.items())):
                errors.append("COMPONENT_OR_CLASSIFICATION_MISMATCH:" + str(demand.get("demand_id")))
                continue
            demand_results.append({"demand_id": result["demand_id"], "result": result["result"],
                                   "matched": matched, "missing": missing})
        if errors or len(demand_results) != len(demands):
            blocked.append({"request_id": request_id, "errors": errors})
            continue
        receipt = {"cycle_id": state.get("cycle_id"), "trigger_source": state.get("trigger_source"),
                   "work_triggered": state.get("work_triggered"), "user_triggered": state.get("user_triggered"),
                   "demand_results": demand_results, "ack": "TOOL016_CENTRAL_RECEIVED", "user_manual_relay": 0,
                   "source_receipt_sha256": _digest({"request_id": request_id, "source_evidence": request.get("source_evidence"),
                                                     "root_id": request.get("root_id"), "demands": demands}),
                   "worker_receipt_sha256": _digest({"cycle_id": state.get("cycle_id"), "results": demand_results})}
        checkpoint = checkpoints[request_id]
        if (checkpoint.get("tool044_worker_checkpoint") == state.get("cycle_id") and
            checkpoint.get("tool044_worker_return_ack") == "PASS"):
            if checkpoint.get("tool044_natural_worker_return") != receipt:
                blocked.append({"request_id": request_id, "errors": ["EXISTING_ACK_RECEIPT_MISMATCH"]})
            continue
        checkpoint["tool044_natural_worker_return"] = receipt
        checkpoint["tool044_worker_checkpoint"] = state.get("cycle_id")
        checkpoint["tool044_worker_return_ack"] = "PASS"
        acknowledged += 1
        updated_requests.add(request_id)
    for item in blocked:
        request_id = item["request_id"]
        checkpoint = checkpoints.get(request_id)
        if checkpoint is None or checkpoint.get("tool044_worker_return_ack") == "PASS":
            continue
        fail_prefixes = ("DUPLICATE_DEMAND_OR_RESULT_ID", "SOURCE_LINEAGE_MISMATCH",
                         "COMPONENT_OR_CLASSIFICATION_MISMATCH", "EXISTING_ACK_RECEIPT_MISMATCH")
        status = "FAIL" if any(error.startswith(fail_prefixes) for error in item["errors"]) else "HOLD"
        receipt = {"cycle_id": state.get("cycle_id"), "ack": "TOOL016_CENTRAL_" + status,
                   "status": status, "errors": item["errors"]}
        if (checkpoint.get("tool044_natural_worker_return") == receipt and
            checkpoint.get("tool044_worker_return_ack") == status):
            continue
        checkpoint["tool044_natural_worker_return"] = receipt
        checkpoint["tool044_worker_checkpoint"] = state.get("cycle_id")
        checkpoint["tool044_worker_return_ack"] = status
        held += 1
        updated_requests.add(request_id)
    if updated_requests:
        try:
            writer(central_path, central)
            actual = json.loads(central_path.read_text(encoding="utf-8"))
            for request_id in updated_requests:
                if actual["integration_core"]["feedback_checkpoints"].get(request_id) != checkpoints[request_id]:
                    raise RuntimeError("TOOL016 central worker-result read-back mismatch")
        except Exception:
            # Restore the exact prior checkpoint if a writer partially mutated it.
            temporary = central_path.with_name(central_path.name + ".tool044-rollback")
            temporary.write_bytes(before)
            os.replace(temporary, central_path)
            raise
    return {"acknowledged": acknowledged, "blocked": blocked, "held": held}


@contextmanager
def _pending_queue(queue_path: Path, pending: list[dict]):
    descriptor, name = tempfile.mkstemp(prefix="tool044-pending-", suffix=".json", dir=queue_path.parent)
    os.close(descriptor)
    path = Path(name)
    try:
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        queue["demands"] = pending
        path.write_text(json.dumps(queue, ensure_ascii=False), encoding="utf-8")
        yield path
    finally:
        path.unlink(missing_ok=True)


def visible_backoff_state(queue_path: Path, registry_path: Path, state_path: Path,
                          external: bool, trigger_source: str) -> dict:
    completed = []
    previous = None
    if state_path.exists():
        queued = json.loads(queue_path.read_text(encoding="utf-8")).get("demands", [])
        central_path = queue_path.parent / "state.json"
        if queued and central_path.exists():
            previous = json.loads(state_path.read_text(encoding="utf-8"))
            checkpoints = json.loads(central_path.read_text(encoding="utf-8")).get(
                "integration_core", {}).get("feedback_checkpoints", {})
            prior_results = {item.get("demand_id"): item for item in previous.get("results", [])}

            def already_returned(demand: dict) -> bool:
                checkpoint = checkpoints.get(demand.get("request_id"), {})
                receipt = checkpoint.get("tool044_natural_worker_return", {})
                return (
                    checkpoint.get("tool044_worker_return_ack") == "PASS"
                    and receipt.get("cycle_id")
                    and checkpoint.get("tool044_worker_checkpoint") == receipt.get("cycle_id")
                    and prior_results.get(demand.get("demand_id"), {}).get("query_signature") == signature(demand)
                    and any(item.get("demand_id") == demand.get("demand_id")
                            for item in receipt.get("demand_results", []))
                )

            if len({item.get("demand_id") for item in queued}) == len(queued):
                completed = [demand for demand in queued if already_returned(demand)]
                if len(completed) == len(queued):
                    idle = dict(previous)
                    idle.update(demands_processed=0, tool016_result_returns=0,
                                duplicate_searches_blocked=0, next_state="WAITING_FOR_NEXT_TRIGGER")
                    state_path.write_text(json.dumps(idle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    return idle
    if completed:
        with _pending_queue(queue_path, [demand for demand in queued if demand not in completed]) as pending_path:
            return _process_pending(pending_path, registry_path, state_path, external, trigger_source,
                                    previous, completed)
    return _process_pending(queue_path, registry_path, state_path, external, trigger_source,
                            previous, completed)


def _process_pending(queue_path: Path, registry_path: Path, state_path: Path,
                     external: bool, trigger_source: str, previous: dict | None,
                     completed: list[dict]) -> dict:
    state = run_cycle(queue_path, registry_path, state_path, external=external,
                      artifact_dir=state_path.parent.parent / "external_candidate_pool",
                      trigger_source=trigger_source)
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    pool = registry.get("components", []) + registry.get("verified_atomic_component_pool", [])
    capability_map = {
        capability: item["component_id"]
        for item in pool if item.get("status") == "VERIFIED_REUSABLE"
        for capability in item.get("atomic_capabilities", [])
    }
    demand_by_id = {d["demand_id"]: d for d in queue.get("demands", [])}
    changed = 0
    now = datetime.now(timezone.utc).isoformat()
    for index, result in enumerate(state.get("results", [])):
        if result.get("result") != "DUPLICATE_SEARCH_BLOCKED":
            continue
        demand = demand_by_id[result["demand_id"]]
        matched = {cap: capability_map[cap] for cap in demand["atomic_capabilities"] if cap in capability_map}
        missing = [cap for cap in demand["atomic_capabilities"] if cap not in matched]
        classification = ("READY_ATOMIC_COMPONENT_FOUND" if matched and not missing
                          else "PARTIAL_ATOMIC_COMPONENT_SET" if matched
                          else "NO_READY_ATOMIC_COMPONENT")
        old_receipt = state.get("receipts", {}).get(signature(demand), {})
        visible = {
            "demand_id": demand["demand_id"],
            "query_signature": signature(demand),
            "last_searched": old_receipt.get("last_searched"),
            "matched": matched,
            "missing": missing,
            "result": classification,
            "next_eligible_search": old_receipt.get("next_eligible_search"),
            "external_search_executed": False,
            "external_search_backoff_active": True,
            "external_search_skipped_reason": "24H_UNCHANGED_QUERY_BACKOFF",
            "state_refreshed_at": now,
            "external_receipts": old_receipt.get("external_receipts", []),
        }
        state["results"][index] = visible
        state["receipts"][signature(demand)] = visible
        changed += 1
    state["backoff_demands_kept_visible"] = changed
    state["duplicate_searches_blocked"] = changed
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    returned = return_verified_results(queue_path, registry_path, state_path, state)
    state["tool016_result_returns"] = returned["acknowledged"]
    state["tool016_result_return_blocks"] = returned["blocked"]
    if completed and previous:
        completed_ids = {demand["demand_id"] for demand in completed}
        state["results"] = [result for result in previous.get("results", [])
                            if result.get("demand_id") in completed_ids] + state["results"]
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, default=root / "tool044_atomic_demand_queue.json")
    parser.add_argument("--registry", type=Path, default=root / "VERIFIED_COMPONENT_REGISTRY.json")
    parser.add_argument("--state", type=Path, default=root / "evidence" / "tool044_atomic_watch_state.json")
    parser.add_argument("--external", action="store_true")
    parser.add_argument("--trigger-source", choices=["MANUAL", "WORK", "USER", "SCHEDULED"], default="MANUAL")
    args = parser.parse_args()
    print(json.dumps(visible_backoff_state(args.queue, args.registry, args.state,
                                           args.external, args.trigger_source), ensure_ascii=False))


if __name__ == "__main__":
    main()
