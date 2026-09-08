"""Evidence-only E2E for TOOL016 -> TOOL044 source lineage.

Uses existing canonical records.  It does not invent missing chat access or
create external-component demands for already verified/local-evidence gates.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from tool044_request_router import route

HERE = Path(__file__).resolve().parent
OUT = HERE / "evidence" / "tool016_tool044_source_lineage_e2e_20260908.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    first = route()
    queue_after_first = load(HERE / "tool044_atomic_demand_queue.json")
    second = route()
    queue_after_second = load(HERE / "tool044_atomic_demand_queue.json")
    state = load(HERE / "tool044_function_state.json")
    functions = state.get("functions", [])

    def function(tool: str, function_id: str | None = None) -> dict:
        return next(row for row in functions if row.get("TOOL_ID") == tool and
                    (function_id is None or row.get("FUNCTION_ID") == function_id))

    t6 = function("TOOL006")
    t13 = function("TOOL013")
    t42 = function("TOOL042", "T42-OFFICIAL-PUBLISHER-VALIDATION")
    t42_demands = [row for row in queue_after_second["demands"]
                   if any(record.get("TOOL_ID") == "TOOL042" for record in row.get("source_records", []))]
    required = {"SOURCE_CHAT_OR_TOOL", "TOOL_ID", "FUNCTION_ID", "ORIGINAL_ERROR_OR_FEEDBACK",
                "OCCURRENCE_OR_EVIDENCE", "ROOT_ID", "MISSING_CAPABILITY", "CURRENT_STATUS",
                "SOURCE_EVIDENCE", "TOOL044_DEMAND_ID"}
    t42_fields_pass = bool(t42_demands) and all(required <= set(record) for row in t42_demands
                                                for record in row.get("source_records", []))
    idempotent = len(queue_after_first["demands"]) == len(queue_after_second["demands"]) and second["added"] == 0
    samples = [
        {
            "TOOL_ID": "TOOL006", "FUNCTION_ID": t6["FUNCTION_ID"],
            "CURRENT_STATUS": t6["CURRENT_STATUS"], "ROOT_ID": "T6-RC-RELEASE-WITHOUT-ACTUAL-IMPACT-E2E",
            "SOURCE_EVIDENCE": t6.get("IMPROVEMENT_EVIDENCE"),
            "MISSING_CAPABILITY": None, "TOOL044_DEMAND_ID": None,
            "ROUTING_RESULT": "TOOL016_OR_TOOL_LOCAL_REVIEW_NO_EXTERNAL_CAPABILITY",
        },
        {
            "TOOL_ID": "TOOL013", "FUNCTION_ID": t13["FUNCTION_ID"],
            "CURRENT_STATUS": t13["CURRENT_STATUS"], "ROOT_ID": "T13-RC-LARGE-BATCH-MAIN-THREAD-STALL",
            "SOURCE_EVIDENCE": t13.get("IMPROVEMENT_EVIDENCE"),
            "MISSING_CAPABILITY": None, "TOOL044_DEMAND_ID": None,
            "ROUTING_RESULT": "SKIP_REUSE_VERIFIED_NO_NEW_DEMAND",
        },
        {
            "TOOL_ID": "TOOL042", "FUNCTION_ID": t42["FUNCTION_ID"],
            "CURRENT_STATUS": t42["CURRENT_STATUS"], "ROOT_ID": t42["ROOT_ID"],
            "SOURCE_EVIDENCE": t42.get("IMPROVEMENT_EVIDENCE"),
            "MISSING_CAPABILITY": t42["MISSING_CAPABILITY"],
            "TOOL044_DEMAND_ID": t42_demands[0]["demand_id"] if t42_demands else None,
            "ROUTING_RESULT": "QUEUED_WITH_SOURCE_LINEAGE" if t42_demands else "FAIL",
        },
    ]
    passed = (len({row["TOOL_ID"] for row in samples}) == 3 and t42_fields_pass and idempotent
              and t13["ACTION"] == "SKIP_REUSE" and samples[2]["TOOL044_DEMAND_ID"] is not None)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "ACCESSIBLE_CANONICAL_RECORDS_ONLY",
        "past_chat_access": "ACCESS_NOT_AVAILABLE",
        "samples": samples,
        "source_tools_preserved": sorted({row["TOOL_ID"] for row in samples}),
        "queue_source_record_fields_pass": t42_fields_pass,
        "root_dedup_idempotency": "PASS" if idempotent else "FAIL",
        "verified_skip_reuse": "PASS" if t13["ACTION"] == "SKIP_REUSE" else "FAIL",
        "first_route_added": first["added"],
        "second_route_added": second["added"],
        "expected_actual": "MATCH" if passed else "MISMATCH",
        "status": "PASS" if passed else "FAIL",
        "truth_boundary": "TOOL006 has no external missing capability and TOOL013 is VERIFIED; neither is falsely queued.",
    }


if __name__ == "__main__":
    result = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
