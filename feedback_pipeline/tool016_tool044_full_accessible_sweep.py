"""Inventory every currently accessible structured WIC error source.

This is deliberately bounded to canonical registries/ledgers.  It preserves
the originating TOOL for every function-state row, routes only explicit
external-capability gaps through the existing TOOL044 router, and records the
unavailable ChatGPT-history boundary without inventing a conversation count.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from tool044_request_router import route

HERE = Path(__file__).resolve().parent
OUT = HERE / "evidence" / "tool016_tool044_full_accessible_sweep_20260908.json"
SOURCES = [
    "wic_target_registry.json",
    "tool044_function_state.json",
    "work16_root_ledger.json",
    "unified_open_ledger.json",
    "incomplete_register.json",
    "TOOL044_REQUEST_INBOX.json",
    "tool044_atomic_demand_queue.json",
]
UNRESOLVED = {"IMPROVED_PARTIAL", "REPEATED_ERROR", "HOLD", "FAIL",
              "MISSING_CAPABILITY", "NO_READY_COMPONENT", "RUNTIME_NOT_ENFORCED",
              "ACTUAL_USE_NOT_VERIFIED", "DEPLOYMENT_NOT_VERIFIED", "UNKNOWN"}


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8-sig"))


def tools(value: object) -> list[str]:
    return sorted(set(re.findall(r"TOOL\d{3}|CENTRAL|EXTERNAL", str(value or ""))))


def digest(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def build() -> dict:
    # The canonical router is the only writer for the request/demand contract.
    first = route()
    second = route()
    registry = load("wic_target_registry.json")
    state = load("tool044_function_state.json")
    roots = load("work16_root_ledger.json").get("roots", [])
    open_rows = load("unified_open_ledger.json").get("entries", [])
    incomplete = load("incomplete_register.json").get("entries", [])
    queue = load("tool044_atomic_demand_queue.json").get("demands", [])

    registry_tools = sorted(registry.get("targets", {}).keys())
    inventory = []
    for row in state.get("functions", []):
        # Null means a cross-tool atomic capability in the canonical state.  It
        # must remain null (not be silently attributed to a made-up TOOL).
        origin_tools: list[str | None] = tools(row.get("TOOL_ID")) or [None]
        status = row.get("CURRENT_STATUS", "UNKNOWN")
        action = row.get("ACTION")
        external = bool(row.get("TOOL044_SEARCH_REQUIRED") and row.get("MISSING_CAPABILITY"))
        classification = ("SKIP_REUSE" if status == "IMPROVED_VERIFIED" or action == "SKIP_REUSE"
                          else "TOOL044" if external else "TOOL016_LOCAL_OR_HOLD")
        for origin in origin_tools:
            inventory.append({
                "SOURCE_CHAT_OR_TOOL": "TOOL016_FUNCTION_STATE",
                "TOOL_ID": origin,
                "FUNCTION_ID": row.get("FUNCTION_ID"),
                "ROOT_ID": row.get("ROOT_ID") or row.get("FUNCTION_ID"),
                "CURRENT_STATUS": status,
                "ORIGINAL_ERROR_OR_FEEDBACK": row.get("REMAINING_ERROR"),
                "OCCURRENCE_OR_EVIDENCE": row.get("REPEATED_ERROR_COUNT", 0),
                "MISSING_CAPABILITY": row.get("MISSING_CAPABILITY"),
                "IMPROVEMENT_EVIDENCE": row.get("IMPROVEMENT_EVIDENCE"),
                "ROUTING": classification,
            })

    def has_lineage(item: dict) -> bool:
        fid, root = item["FUNCTION_ID"], item["ROOT_ID"]
        return any(any((r.get("FUNCTION_ID") == fid or r.get("ROOT_ID") == root)
                           and r.get("TOOL_ID") == item["TOOL_ID"]
                           for r in demand.get("source_records", [])) for demand in queue)

    routed = [x for x in inventory if x["ROUTING"] == "TOOL044"]
    missing_lineage = [x for x in routed if not has_lineage(x)]
    verified = [x for x in inventory if x["ROUTING"] == "SKIP_REUSE"]
    error_rows = [x for x in inventory if x["CURRENT_STATUS"] in UNRESOLVED]
    unique_roots = sorted({x["ROOT_ID"] for x in error_rows if x["ROOT_ID"]})
    represented = sorted({x["TOOL_ID"] for x in inventory if x["TOOL_ID"]})
    canonical_tools = sorted({t for t in registry_tools if t.startswith("TOOL")} |
                             {t for x in inventory for t in tools(x["TOOL_ID"]) if t.startswith("TOOL")})
    source_receipts = [{"path": f"feedback_pipeline/{name}", "sha256": digest(name)} for name in SOURCES]
    idempotent = second.get("added") == 0
    passed = not missing_lineage and idempotent and len(queue) == len({x.get("demand_id") for x in queue})

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "ALL_CURRENTLY_ACCESSIBLE_STRUCTURED_CANONICAL_WIC_SOURCES",
        "source_receipts": source_receipts,
        "counts": {
            "checked_tools": len(canonical_tools),
            "checked_record_sources": len(SOURCES),
            "automatically_recoverable_records": len(inventory) + len(roots) + len(open_rows) + len(incomplete),
            "access_not_available_source_classes": 1,
            "access_not_available_conversation_count": None,
            "collected_error_records": len(error_rows),
            "roots_after_deduplication": len(unique_roots),
            "verified_skip_reuse_records": len(verified),
            "records_handed_to_tool044": len(routed),
            "atomic_demands": len(queue),
        },
        "checked_tool_ids": canonical_tools,
        "function_state_tool_ids": represented,
        "inventory": inventory,
        "deduplicated_root_ids": unique_roots,
        "tool044_routed_records": routed,
        "queue_lineage_missing": missing_lineage,
        "access_not_available": [{
            "source_type": "CHATGPT_FULL_CONVERSATION_HISTORY_NOT_PERSISTED_TO_CANONICAL_FILES",
            "status": "ACCESS_NOT_AVAILABLE",
            "countable_source_classes": 1,
            "conversation_count": None,
            "reason": "No authenticated full conversation-history reader is available in this runtime.",
            "free_automatic_connection": "AVAILABLE_ONLY_FOR_RECORDS_ALREADY_PERSISTED_IN_LEDGER_EVIDENCE_OR_QUEUE",
            "user_action": "NONE",
        }],
        "router_first_added": first.get("added"),
        "router_second_added": second.get("added"),
        "router_idempotency": "PASS" if idempotent else "FAIL",
        "expected": "Every explicit external gap has source-preserving TOOL044 lineage; VERIFIED rows are not newly routed; inaccessible chats are not claimed.",
        "actual": "MATCH" if passed else "MISMATCH",
        "status": "PASS" if passed else "FAIL",
    }


if __name__ == "__main__":
    result = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "counts": result["counts"],
                      "queue_lineage_missing": len(result["queue_lineage_missing"])}, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
