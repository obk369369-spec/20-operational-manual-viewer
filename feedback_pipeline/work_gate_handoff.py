"""Deterministic WIC Chat/GitHub -> Work credit gate and resumable exit contract.

Work is eligible only when Chat/Files, GitHub, and ordinary runtime are all unable
to perform the concrete execution AND an exact restart package is complete.
If a Work session stops before completion, a checkpoint must preserve the last
successful stage, evidence, rollback point, and exact next step so later Work does
not restart from zero.
This module does not execute Work and does not upgrade business PASS by itself.
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
REQUIRED_EXIT_CHECKPOINT = (
    "lane",
    "actual_purpose",
    "status",
    "last_success_stage",
    "last_actual_commit",
    "last_success_run",
    "remaining_blocker",
    "modified_assets",
    "evidence",
    "rollback_point",
    "exact_next_step",
    "ui_chat_identity",
    "ui_chat_identity_evidence",
)


def evaluate_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    gates = candidate.get("gates", {})
    required_gates = ("chat_files", "github", "ordinary_runtime")
    missing_gates = [key for key in required_gates if key not in gates or not isinstance(gates.get(key), bool)]
    if missing_gates:
        return {
            "decision": "WORK_HOLD_INVALID_GATES",
            "reason": "Every lower-cost gate must be present as an explicit boolean.",
            "missing_handoff": [],
            "missing_gates": missing_gates,
        }
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


def validate_exit_checkpoint(checkpoint: Mapping[str, Any]) -> dict[str, Any]:
    missing = []
    for key in REQUIRED_EXIT_CHECKPOINT:
        value = checkpoint.get(key)
        if value in (None, "", [], {}):
            missing.append(key)
    status = str(checkpoint.get("status", ""))
    placeholders = {"NONE_YET", "TODO", "TBD", "PLACEHOLDER", "확인 필요"}
    placeholder_fields = [key for key in REQUIRED_EXIT_CHECKPOINT if str(checkpoint.get(key, "")).strip() in placeholders or (isinstance(checkpoint.get(key), list) and any(str(x).strip() in placeholders for x in checkpoint.get(key, [])))]
    if status and status not in {"PASS", "HOLD", "FAIL"}:
        return {
            "valid": False,
            "decision": "WORK_EXIT_CHECKPOINT_INVALID",
            "missing": missing,
            "reason": "status must be PASS, HOLD, or FAIL",
        }
    if missing:
        return {
            "valid": False,
            "decision": "WORK_EXIT_CHECKPOINT_INCOMPLETE",
            "missing": missing,
            "reason": "Work exit is not resumable until every checkpoint field is persisted.",
        }
    if placeholder_fields:
        return {"valid": False, "decision": "WORK_EXIT_CHECKPOINT_PLACEHOLDER", "missing": [], "placeholder_fields": placeholder_fields, "reason": "Placeholder values are not resumable execution evidence."}
    return {
        "valid": True,
        "decision": "WORK_EXIT_RESUMABLE",
        "missing": [],
        "reason": "Checkpoint is sufficient to resume without repeating completed stages.",
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
        "schema_version": 2,
        "structure_status": state.get("structure_status"),
        "eligible_work_lanes": eligible,
        "deferred_lower_cost_lanes": deferred,
        "held_incomplete_handoff_lanes": held,
        "candidate_count": len(candidates),
        "target_conservation": len(evaluated) == len(candidates),
        "pass_claimed": bool(candidates),
        "candidates": evaluated,
        "policy": "Use Work only for WORK_ELIGIBLE lanes; never repeat prior PASS or repository inventory.",
        "work_exit_policy": "Before Work stops, persist a WORK_EXIT_RESUMABLE checkpoint or mark the lane incomplete; never restart from zero.",
    }


def build_exit_templates(handoff: Mapping[str, Any]) -> dict[str, Any]:
    templates = {}
    for lane in handoff.get("eligible_work_lanes", []):
        candidate = handoff["candidates"][lane]
        templates[lane] = {
            "lane": lane,
            "actual_purpose": candidate["execution_goal"],
            "status": "HOLD",
            "last_success_stage": "PRE_WORK_BASELINE_CAPTURED",
            "last_actual_commit": candidate["rollback_point"],
            "last_success_run": "NONE_YET",
            "remaining_blocker": candidate["blocker"],
            "modified_assets": ["NONE_YET"],
            "evidence": ["record pre-run commit/hash before first Work change"],
            "rollback_point": candidate["rollback_point"],
            "exact_next_step": candidate["restart_point"],
            "ui_chat_identity": "UI_TITLE_HOLD",
            "ui_chat_identity_evidence": "No verified UI title evidence is required for logical Work resumption.",
        }
    return {
        "schema_version": 1,
        "templates": templates,
        "required_fields": list(REQUIRED_EXIT_CHECKPOINT),
        "rule": "Replace placeholders with actual executed evidence before a Work session ends.",
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
    missing_gate = evaluate_candidate({**incomplete, "gates": {"chat_files": False, "github": False}})
    assert missing_gate["decision"] == "WORK_HOLD_INVALID_GATES" and missing_gate["missing_gates"] == ["ordinary_runtime"]

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
    empty = build_handoff({"structure_status": "PASS", "work_gate_candidates": {}})
    assert empty["candidate_count"] == 0 and empty["pass_claimed"] is False and empty["target_conservation"] is True
    assert combined["deferred_lower_cost_lanes"] == ["a"]

    bad_exit = {"lane": "b", "status": "HOLD"}
    assert validate_exit_checkpoint(bad_exit)["decision"] == "WORK_EXIT_CHECKPOINT_INCOMPLETE"

    good_exit = {
        "lane": "b",
        "actual_purpose": "input -> execution -> output compare",
        "status": "HOLD",
        "last_success_stage": "INPUT_HASH_CAPTURED",
        "last_actual_commit": "abc123",
        "last_success_run": "run 456 success",
        "remaining_blocker": "browser step pending",
        "modified_assets": ["index.html"],
        "evidence": ["commit abc", "input sha256:def"],
        "rollback_point": "commit 123",
        "exact_next_step": "run chromium fixture from stage BROWSER_EXECUTION",
        "ui_chat_identity": "UI_TITLE_HOLD",
        "ui_chat_identity_evidence": "No direct UI title evidence available",
    }
    assert validate_exit_checkpoint(good_exit)["decision"] == "WORK_EXIT_RESUMABLE"

    templates = build_exit_templates(combined)
    assert list(templates["templates"]) == ["b"]
    print("PASS: 7 deterministic Work-gate/handoff/exit-checkpoint fixtures")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="WIC_EXECUTION_STATE.json")
    parser.add_argument("--output", default="work-handoff.json")
    parser.add_argument("--exit-template-output", default="")
    parser.add_argument("--validate-exit", default="")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.validate_exit:
        checkpoint = json.loads(Path(args.validate_exit).read_text(encoding="utf-8"))
        result = validate_exit_checkpoint(checkpoint)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result["valid"] else 2)

    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    output = build_handoff(state)
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.exit_template_output:
        templates = build_exit_templates(output)
        Path(args.exit_template_output).write_text(json.dumps(templates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
