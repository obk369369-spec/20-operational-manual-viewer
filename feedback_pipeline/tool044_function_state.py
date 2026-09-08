"""Build the bounded, evidence-first TOOL044 function-state input."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
UNRESOLVED = {
    "IMPROVED_PARTIAL", "REPEATED_ERROR", "HOLD", "FAIL", "MISSING_CAPABILITY",
    "NO_READY_COMPONENT", "RUNTIME_NOT_ENFORCED", "ACTUAL_USE_NOT_VERIFIED",
    "DEPLOYMENT_NOT_VERIFIED",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build(base: Path = HERE) -> dict:
    targets = load(base / "wic_target_registry.json")["targets"]
    prechecks = load(base / "tool044_precheck_targets.json").get("targets", {})
    ledger = load(base / "unified_open_ledger.json").get("entries", [])
    queue = load(base / "tool044_atomic_demand_queue.json").get("demands", [])
    registry = load(base / "VERIFIED_COMPONENT_REGISTRY.json")
    atomic = registry.get("verified_atomic_component_pool", [])
    cap_components = {
        cap: row["component_id"] for row in atomic if row.get("status") == "VERIFIED_REUSABLE"
        for cap in row.get("atomic_capabilities", [])
    }
    rows = []

    # Registered TOOL baseline. PASS claims require explicit actual/deployed evidence.
    for tool, target in sorted(targets.items()):
        if tool == "CENTRAL":
            continue
        pre = prechecks.get(tool, {})
        validation = target.get("first_validation", {})
        deployed = bool(pre.get("existing_deployed_pass")) or (
            validation.get("status") == "PASS" and
            validation.get("run_scope") == "DEPLOYED_CANONICAL_REAL_USE"
        )
        status = "IMPROVED_VERIFIED" if deployed else "ACTUAL_USE_NOT_VERIFIED"
        if target.get("status") in {"COMPLETE", "STAGING_REMOTE_VERIFIED"} and validation.get("status") == "PASS":
            status = "IMPROVED_VERIFIED"
        rows.append({
            "TOOL_ID": tool, "FUNCTION_ID": f"{tool}-CANONICAL-RUNTIME",
            "FUNCTION_NAME": "canonical runtime and deployed actual-use path",
            "CURRENT_STATUS": status,
            "LAST_VERIFIED_DATE": None,
            "IMPROVEMENT_EVIDENCE": target.get("evidence_path"),
            "REMAINING_ERROR": None if status == "IMPROVED_VERIFIED" else pre.get("first_blocker", "ACTUAL_USE_EVIDENCE_NOT_EXPLICIT"),
            "REPEATED_ERROR_COUNT": 1 if pre.get("repeat_failure") else 0,
            "ROOT_ID": pre.get("first_blocker"),
            "EXISTING_VERIFIED_COMPONENT": pre.get("reuse_component"),
            "EXISTING_VERIFIED_FRAMEWORK": target.get("adapter"),
            "MISSING_CAPABILITY": None,
            "TOOL044_SEARCH_REQUIRED": False,
            "SEARCH_PRIORITY": "NONE",
            "ACTION": "SKIP_REUSE" if status == "IMPROVED_VERIFIED" else "TOOL016_OR_TOOL_LOCAL_REVIEW",
        })

    # Canonical unresolved roots override broad target-level optimism, but evidence/platform
    # waits are not external-component searches.
    for item in ledger:
        state = str(item.get("status", "UNKNOWN"))
        if any(word in state for word in ("HOLD", "WAIT", "LIMIT", "BLOCK")):
            status = "HOLD"
        elif "FAIL" in state:
            status = "FAIL"
        else:
            status = "UNKNOWN"
        rows.append({
            "TOOL_ID": item.get("target", "UNKNOWN"), "FUNCTION_ID": item.get("root_id", "UNKNOWN"),
            "FUNCTION_NAME": item.get("display_label") or item.get("label") or item.get("root_id", "UNKNOWN"),
            "CURRENT_STATUS": status, "LAST_VERIFIED_DATE": None,
            "IMPROVEMENT_EVIDENCE": item.get("evidence"),
            "REMAINING_ERROR": item.get("last_actual_point") or state,
            "REPEATED_ERROR_COUNT": int(item.get("recurrence_count", 0)),
            "ROOT_ID": item.get("root_id"), "EXISTING_VERIFIED_COMPONENT": None,
            "EXISTING_VERIFIED_FRAMEWORK": None, "MISSING_CAPABILITY": None,
            "TOOL044_SEARCH_REQUIRED": False, "SEARCH_PRIORITY": "NONE",
            "ACTION": "TOOL016_OR_EXTERNAL_EVIDENCE_GATE",
        })

    # Atomic demands are the only existing bounded declarations that establish an
    # external capability need. A component receipt alone is only PARTIAL until the
    # target-tool deployed-copy evidence exists.
    external_demands = []
    for demand in queue:
        caps = demand.get("atomic_capabilities", [])
        matched = {cap: cap_components[cap] for cap in caps if cap in cap_components}
        missing = [cap for cap in caps if cap not in matched]
        status = "IMPROVED_PARTIAL" if matched else "MISSING_CAPABILITY"
        search = bool(missing)
        row = {
            "TOOL_ID": "TOOL042", "FUNCTION_ID": demand["demand_id"],
            "FUNCTION_NAME": demand["demand_id"].removeprefix("T42-").replace("-", " ").title(),
            "CURRENT_STATUS": status, "LAST_VERIFIED_DATE": None,
            "IMPROVEMENT_EVIDENCE": list(matched.values()),
            "REMAINING_ERROR": missing or "TARGET_TOOL_DEPLOYED_COPY_NOT_VERIFIED",
            "REPEATED_ERROR_COUNT": int(demand.get("repeated_error_count", 0)),
            "ROOT_ID": demand["demand_id"],
            "EXISTING_VERIFIED_COMPONENT": list(matched.values()),
            "EXISTING_VERIFIED_FRAMEWORK": "DUAL_RECEIPT_ASSEMBLY_GATE",
            "MISSING_CAPABILITY": missing,
            "TOOL044_SEARCH_REQUIRED": search,
            "SEARCH_PRIORITY": "HIGH" if demand.get("repeated_error_count", 0) else ("NORMAL" if search else "NONE"),
            "ACTION": "SEARCH" if search else "ASSEMBLY_AND_DEPLOY_VALIDATION_REQUIRED",
        }
        rows.append(row)
        if search:
            external_demands.append({"demand_id": demand["demand_id"], "missing_capabilities": missing,
                                     "search_priority": row["SEARCH_PRIORITY"]})

    counts = {name: sum(r["CURRENT_STATUS"] == name for r in rows) for name in
              ["IMPROVED_VERIFIED", "IMPROVED_PARTIAL", "REPEATED_ERROR", "HOLD", "FAIL",
               "MISSING_CAPABILITY", "NO_READY_COMPONENT", "RUNTIME_NOT_ENFORCED",
               "ACTUAL_USE_NOT_VERIFIED", "DEPLOYMENT_NOT_VERIFIED", "UNKNOWN"]}
    return {
        "schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_contract": "MASTER+SAFE_CHECKPOINT+ERROR_ROOT_LEDGER+VERIFIED_REGISTRY+DEPLOYMENT_EVIDENCE",
        "classification_counts": counts, "functions": rows,
        "tool044_external_demand_candidates": external_demands,
        "observer_labels": {
            "IMPROVED_VERIFIED": "개선 완료", "IMPROVED_PARTIAL": "부분 개선",
            "REPEATED_ERROR": "고질 오류", "MISSING_CAPABILITY": "외부부품 검색 중",
            "COMPONENT_VERIFIED": "검증부품 확보", "ASSEMBLY_TESTING": "조합시험 중",
            "DEPLOYMENT_NOT_VERIFIED": "배포 검증 대기", "DEPLOYED_PASS": "배포 완료",
        },
    }


def write(base: Path = HERE) -> dict:
    result = build(base)
    (base / "tool044_function_state.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(write(), ensure_ascii=False))
