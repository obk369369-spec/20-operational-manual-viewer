"""Verified TOOL041 -> TOOL007 -> TOOL042 customer-flow contract.

This module only adapts already evidenced facts.  It never performs outreach,
infers a customer's interests, or turns a downstream HOLD into a PASS.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from pathlib import Path

from p1_to_p2_handoff import build_p2_input
from tool7_contact_judgment import judge_contact


REQUIRED_T41 = ("기관", "성명", "부서", "직책", "담당업무_연구분야", "고유번호", "출처")


def _load_tool41(root: Path):
    source = root / "src" / "customer_integrity.py"
    spec = importlib.util.spec_from_file_location("tool41_customer_integrity", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("TOOL041_RUNTIME_NOT_LOADABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def adapt_tool41_to_tool7(row: dict, history: dict) -> dict:
    missing = [field for field in REQUIRED_T41 if not row.get(field)]
    if row.get("검증상태") not in {"PASS", "VERIFIED", "REMOTE_VERIFIED"}:
        missing.append("검증상태")
    if missing:
        return {"status": "HOLD", "reason": "TOOL041_VERIFIED_OUTPUT_MISSING", "missing": sorted(set(missing))}

    p1 = {
        "db_state": "MAIN_DB",
        "permanent_customer_id": row["고유번호"],
        "source_cohort": history.get("source_cohort", "DORMANT_LEDGER"),
        "current_employment_verified": True,
        "company_direction_verified": True,
        "contact_history_verified": history.get("contact_history_verified") is True,
        "moved_or_left": history.get("moved_or_left", False),
        "explicit_stop_or_rejection": history.get("explicit_stop_or_rejection", False),
        "direct_inquiry": history.get("direct_inquiry", False),
        "purchase_history": history.get("purchase_history", False),
        "quote_history": history.get("quote_history", False),
        "one_way_sent_only": history.get("one_way_sent_only", False),
        "cc_only": history.get("cc_only", False),
        "old_ledger_note": history.get("old_ledger_note", False),
        "phone_allowed": history.get("phone_allowed", False),
        "prefers_material_before_call": history.get("prefers_material_before_call", False),
        "research_or_enterprise_customer": True,
    }
    handoff = build_p2_input(p1)
    if handoff["status"] != "PASS":
        return {"status": "HOLD", "reason": "TOOL007_HANDOFF_REJECTED", "handoff": handoff}
    return {"status": "PASS", "p1": p1, "tool7_input": handoff["p2_input"]}


def build_tool42_state(row: dict, history: dict, tool7_result: dict) -> dict:
    topics = [part.strip() for part in row["담당업무_연구분야"].split("|") if part.strip()]
    return {
        "institution": row["기관"],
        "name": row["성명"],
        "current_affiliation_verified": True,
        "department": row["부서"],
        "position": row["직책"],
        "business_directions": topics,
        # Current interests are never inferred from an official work-area page.
        "current_interests": history.get("current_interests", []),
        "contact_history_verified": history.get("contact_history_verified") is True,
        "prior_sent_titles": history.get("prior_sent_titles", []),
        "prior_inquiry": history.get("direct_inquiry", False),
        "prior_quote": history.get("quote_history", False),
        "prior_purchase": history.get("purchase_history", False),
        "explicit_stop_or_rejection": history.get("explicit_stop_or_rejection", False),
        "required_recommendation_count": history.get("required_recommendation_count", 3),
        "upstream_tool7_decision": tool7_result["decision"],
        "source_ref": row["출처"],
    }


def run_actual_flow(fixture: dict, tool41_root: Path, tool42_root: Path) -> dict:
    tool41 = _load_tool41(tool41_root)
    row = fixture["tool41_verified_row"]
    tool41.validate_row(row)
    contract = adapt_tool41_to_tool7(row, fixture["history"])
    if contract["status"] != "PASS":
        return {"status": "HOLD", "first_blocker": contract["reason"], "contract": contract}

    tool7_result = judge_contact(contract["tool7_input"])
    if tool7_result["decision"] != "PASS":
        return {"status": "HOLD", "first_blocker": "TOOL007_JUDGMENT_HOLD", "tool7": tool7_result}

    state = build_tool42_state(row, fixture["history"], tool7_result)
    packet = {"state": state, "candidates": fixture.get("verified_report_candidates", [])}
    runner = Path(__file__).with_name("tool42_contract_runner.js")
    completed = subprocess.run(
        ["node", str(runner), str(tool42_root)], input=json.dumps(packet, ensure_ascii=False),
        text=True, encoding="utf-8", capture_output=True, check=False,
    )
    if completed.returncode != 0:
        return {"status": "FAIL", "first_blocker": "TOOL042_RUNTIME_ERROR", "stderr": completed.stderr.strip()}
    tool42_result = json.loads(completed.stdout)
    expected = fixture["expected"]
    checks = {
        "tool41_verified": row["검증상태"] == expected["tool41_status"],
        "tool7_decision": tool7_result["decision"] == expected["tool7_decision"],
        "tool42_decision": tool42_result["decision"] == expected["tool42_decision"],
        "tool42_reason": tool42_result["reason"] == expected["tool42_reason"],
        "external_send_not_executed": tool42_result.get("send_allowed", False) is False,
    }
    return {
        "status": "CROSS_TOOL_INTEGRATION_PASS" if all(checks.values()) else "FAIL",
        "dependency_order": ["TOOL041", "TOOL007", "TOOL042"],
        "checks": checks,
        "tool41_output": row,
        "tool7_output": tool7_result,
        "tool42_input": state,
        "tool42_output": tool42_result,
        "final_operational_status": "HOLD_EXTERNAL_CUSTOMER_EVIDENCE" if tool42_result["decision"] == "HOLD" else "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--tool41-root", required=True, type=Path)
    parser.add_argument("--tool42-root", required=True, type=Path)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    result = run_actual_flow(json.loads(args.fixture.read_text(encoding="utf-8")), args.tool41_root, args.tool42_root)
    if args.evidence:
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "CROSS_TOOL_INTEGRATION_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
