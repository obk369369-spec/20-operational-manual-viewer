"""Deterministic WIC Chat/GitHub -> Work credit gate.

Work is eligible only when Chat/Files, GitHub, and ordinary runtime are all unable
to perform the concrete execution AND an exact restart package is complete.
This module does not execute Work and does not upgrade business PASS.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

REQUIRED_HANDOFF = (
    "blocker",
    "restart_point",
    "target_repository",
    "target_assets",
    "execution_goal",
    "success_evidence",
    "rollback_point",
)


def evaluate_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    gates = candidate.get("gates", {})
    g1 = bool(gates.get("chat_files", False))
    g2 = bool(gates.get("github", False))
    g3 = bool(gates.get("ordinary_runtime", False))

    if g1 or g2 or g3:
        return {
            "decision": "WORK_DEFER_DENIED",
            "reason": "At least one lower-cost execution lane remains available.",
            "missing_handoff": [],
        }

    missing = []
    for key in REQUIRED_HANDOFF:
        value = candidate.get(key)
        if value in (None, "", [], {}):
            missing.append(key)

    if missing:
        return {
            "decision": "WORK_HOLD_INCOMPLETE_HANDOFF",
            "reason": "All lower-cost lanes are unavailable, but exact handoff is incomplete.",
            "missing_handoff": missing,
        }

    return {
        "decision": "WORK_ELIGIBLE",
        "reason": "All lower-cost lanes are unavailable and exact handoff is complete.",
        "missing_handoff": [],
    }


def build_handoff(state: Mapping[str, Any]) -> dict[str, Any]:
    candidates = state.get("work_gate_candidates", {})
    evaluated: dict[str, Any] = {}
    eligible = []
    deferred = []
    held = []

    for lane, candidate in candidates.items():
        result = evaluate_candidate(candidate)
        row = dict(candidate)
        row.update(result)
        evaluated[lane] = row
        if result["decision"] == "WORK_ELIGIBLE":
            eligible.append(lane)
        elif result["decision"] == "WORK_DEFER_DENIED":
            deferred.append(lane)
        else:
            held.append(lane)

    return {
        "schema_version": 1,
        "structure_status": state.get("structure_status"),
        "eligible_work_lanes": eligible,
        "deferred_lower_cost_lanes": deferred,
        "held_incomplete_handoff_lanes": held,
        "candidates": evaluated,
        "policy": "Use Work only for WORK_ELIGIBLE lanes; never repeat prior PASS or repository inventory.",
    }


def self_test() -> None:
    cheap = {
        "gates": {"chat_files": False, "github": True, "ordinary_runtime": False},
        "blocker": "x",
    }
    assert evaluate_candidate(cheap)["decision"] == "WORK_DEFER_DENIED"

    incomplete = {
        "gates": {"chat_files": False, "github": False, "ordinary_runtime": False},
        "blocker": "browser execution unavailable",
        "restart_point": "rerun browser E2E",
    }
    r = evaluate_candidate(incomplete)
    assert r["decision"] == "WORK_HOLD_INCOMPLETE_HANDOFF"
    assert "target_repository" in r["missing_handoff"]

    complete = {
        "gates": {"chat_files": False, "github": False, "ordinary_runtime": False},
        "blocker": "binary injection unavailable",
        "restart_point": "inject workbook and execute",
        "target_repository": "owner/repo",
        "target_assets": ["input.xlsx", "runner"],
        "execution_goal": "input -> execution -> output compare",
        "success_evidence": ["run", "artifact", "read-back"],
        "rollback_point": "pre-work commit",
    }
    assert evaluate_candidate(complete)["decision"] == "WORK_ELIGIBLE"

    combined = build_handoff({"structure_status": "PASS", "work_gate_candidates": {"a": cheap, "b": complete}})
    assert combined["eligible_work_lanes"] == ["b"]
    assert combined["deferred_lower_cost_lanes"] == ["a"]
    print("PASS: 4 deterministic Work-gate/handoff fixtures")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="WIC_EXECUTION_STATE.json")
    parser.add_argument("--output", default="work-handoff.json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    output = build_handoff(state)
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
