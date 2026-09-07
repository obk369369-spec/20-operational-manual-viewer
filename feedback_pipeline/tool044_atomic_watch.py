"""Local, bounded TOOL044 atomic-demand cycle. No production mutation."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def signature(demand: dict) -> str:
    value = f"{demand['demand_id']}|{','.join(sorted(demand['atomic_capabilities']))}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def run_cycle(queue_path: Path, registry_path: Path, state_path: Path, now: datetime | None = None) -> dict:
    now = now or utc_now()
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    previous = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"receipts": {}}
    receipts = previous.get("receipts", {})
    pool = registry.get("verified_atomic_component_pool", [])
    capability_map = {
        capability: item["component_id"]
        for item in pool if item.get("status") == "VERIFIED_REUSABLE"
        for capability in item.get("atomic_capabilities", [])
    }
    results, duplicate_blocks = [], 0
    for demand in queue.get("demands", []):
        sig = signature(demand)
        old = receipts.get(sig)
        if old and old.get("next_eligible_search") and now < datetime.fromisoformat(old["next_eligible_search"]):
            duplicate_blocks += 1
            results.append({"demand_id": demand["demand_id"], "result": "DUPLICATE_SEARCH_BLOCKED", "query_signature": sig})
            continue
        matched = {cap: capability_map[cap] for cap in demand["atomic_capabilities"] if cap in capability_map}
        missing = [cap for cap in demand["atomic_capabilities"] if cap not in matched]
        result = "READY_ATOMIC_COMPONENT_FOUND" if matched and not missing else "PARTIAL_ATOMIC_COMPONENT_SET" if matched else "NO_READY_ATOMIC_COMPONENT"
        receipt = {
            "demand_id": demand["demand_id"], "query_signature": sig, "last_searched": now.isoformat(),
            "matched": matched, "missing": missing, "result": result,
            "next_eligible_search": (now + timedelta(hours=24)).isoformat(),
            "external_search_executed": False,
        }
        receipts[sig] = receipt
        results.append(receipt)
    state = {
        "cycle_id": now.strftime("%Y%m%dT%H%M%SZ"), "runtime": "LOCAL_STANDARD_LIBRARY",
        "paid_api_calls": 0, "paid_saas_calls": 0, "production_mutations": 0,
        "demands_processed": len(results), "duplicate_searches_blocked": duplicate_blocks,
        "results": results, "receipts": receipts, "next_state": "WAITING_FOR_NEXT_TRIGGER",
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parent
    parser.add_argument("--queue", type=Path, default=root / "tool044_atomic_demand_queue.json")
    parser.add_argument("--registry", type=Path, default=root / "VERIFIED_COMPONENT_REGISTRY.json")
    parser.add_argument("--state", type=Path, default=root / "evidence" / "tool044_atomic_watch_state.json")
    args = parser.parse_args()
    print(json.dumps(run_cycle(args.queue, args.registry, args.state), ensure_ascii=False))


if __name__ == "__main__":
    main()
