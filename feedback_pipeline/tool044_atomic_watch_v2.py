"""TOOL044 atomic watch compatibility fix.

The legacy watcher correctly avoids repeated external searches for 24 hours, but
it used DUPLICATE_SEARCH_BLOCKED as the whole demand result.  That hid already
verified matches and the still-missing capabilities.  This wrapper keeps the
external-search backoff while always publishing the current demand state.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from tool044_atomic_watch import run_cycle, signature


def visible_backoff_state(queue_path: Path, registry_path: Path, state_path: Path,
                          external: bool, trigger_source: str) -> dict:
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
    # Return the persisted worker outcome through the existing TOOL016 central
    # checkpoint contract.  This is a read-back/ACK of watcher results, not a
    # second transport or a synthetic component PASS.
    root = queue_path.parent
    inbox_path = root / "TOOL044_REQUEST_INBOX.json"
    central_path = root / "state.json"
    if inbox_path.exists() and central_path.exists():
        inbox = json.loads(inbox_path.read_text(encoding="utf-8"))
        central = json.loads(central_path.read_text(encoding="utf-8"))
        checkpoints = central.get("integration_core", {}).get("feedback_checkpoints", {})
        result_by_demand = {item.get("demand_id"): item for item in state.get("results", [])}
        queue_demands = queue.get("demands", [])
        returned = 0
        for request in inbox.get("requests", []):
            request_id = str(request.get("request_id") or "")
            if not request_id or request_id not in checkpoints:
                continue
            demand_ids = [d.get("demand_id") for d in queue_demands if str(d.get("request_id") or "") == request_id]
            demand_results = [result_by_demand[d] for d in demand_ids if d in result_by_demand]
            if not demand_results:
                continue
            receipt = {
                "cycle_id": state.get("cycle_id"),
                "trigger_source": state.get("trigger_source"),
                "work_triggered": state.get("work_triggered"),
                "user_triggered": state.get("user_triggered"),
                "demand_results": [{"demand_id": r.get("demand_id"), "result": r.get("result"),
                                    "matched": r.get("matched", {}), "missing": r.get("missing", [])}
                                   for r in demand_results],
                "ack": "TOOL016_CENTRAL_RECEIVED",
                "user_manual_relay": 0,
            }
            checkpoints[request_id]["tool044_natural_worker_return"] = receipt
            checkpoints[request_id]["tool044_worker_checkpoint"] = state.get("cycle_id")
            checkpoints[request_id]["tool044_worker_return_ack"] = "PASS"
            returned += 1
        if returned:
            central_path.write_text(json.dumps(central, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            read_back = json.loads(central_path.read_text(encoding="utf-8"))
            acknowledged = sum(1 for cp in read_back["integration_core"]["feedback_checkpoints"].values()
                               if cp.get("tool044_worker_checkpoint") == state.get("cycle_id")
                               and cp.get("tool044_worker_return_ack") == "PASS")
            if acknowledged != returned:
                raise RuntimeError("TOOL016 central worker-result return read-back mismatch")
        state["tool016_result_returns"] = returned
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
