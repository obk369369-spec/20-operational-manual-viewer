"""Local-first router for TOOL044. Mechanical work stays outside Work/Codex."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tool044_precheck import evaluate

HANDOFF_FIELDS = (
    "TARGET_TOOL", "TARGET_FUNCTION", "CURRENT_STATE", "KNOWN_BLOCKER",
    "ACTUAL_INPUT", "CANONICAL_RUNTIME_PATH", "ACTUAL_USE_FOLDER",
    "SAFE_CHECKPOINT", "GITHUB_STATE", "REGISTRY_RESULT",
    "LOCAL_TEST_RESULT", "WHY_WORK_REQUIRED", "EXPECTED_WORK_OUTPUT",
)
WORK_RESULT_FIELDS = (
    "WORK_DECISION", "SELECTED_COMPONENT", "SOURCE", "VERSION", "LICENSE",
    "UNMODIFIED_USE", "EXPECTED_CONTRACT", "INTEGRATION_TARGET",
)


def route(config: dict, roots: dict[str, Path]) -> dict:
    precheck = evaluate(config, roots)
    base = {
        "target_tool": precheck.get("target_tool", "UNKNOWN"),
        "target_function": precheck.get("target_function", "UNKNOWN"),
        "precheck": precheck.get("work_eligible", "NO"),
        "execution_mode": "LOCAL",
        "local_stage": "PRECHECK",
        "work_handoff_required": "NO",
        "work_reason": "NONE",
        "deploy_result": "NOT_STARTED",
        "user_action": "NONE",
    }
    if precheck.get("work_eligible") == "SKIP_REUSE":
        base.update(local_result="SKIP_REUSE", local_stage="REGISTRY_REUSE",
                    deploy_result="EXISTING_DEPLOYED_PASS")
        return base
    if precheck.get("work_eligible") != "YES":
        blocker = precheck.get("first_blocker") or precheck.get("reason", "UNKNOWN")
        if config.get("repeat_failure"):
            result = "REPEAT_BLOCKED"
        elif config.get("external_blocker"):
            result = "HOLD_EXTERNAL"
        elif config.get("test_scope") == "LARGE" or not config.get("cause_clear"):
            result = "EXCLUDE_THIS_RUN"
        else:
            result = "WORK_ELIGIBLE_NO"
        base.update(local_result=result, work_reason=blocker)
        return base
    if not config.get("requires_new_judgment", False):
        base.update(local_result="LOCAL_READY", local_stage="MECHANICAL_ENGINE")
        return base

    handoff_source = precheck["handoff"]
    handoff = {
        "TARGET_TOOL": handoff_source["TARGET_TOOL"],
        "TARGET_FUNCTION": handoff_source["TARGET_FUNCTION"],
        "CURRENT_STATE": "PRECHECK_PASS_NEW_JUDGMENT_REQUIRED",
        "KNOWN_BLOCKER": handoff_source["KNOWN_BLOCKER"],
        "ACTUAL_INPUT": handoff_source["ACTUAL_INPUT_PATH"],
        "CANONICAL_RUNTIME_PATH": handoff_source["CANONICAL_RUNTIME_PATH"],
        "ACTUAL_USE_FOLDER": handoff_source["ACTUAL_USE_FOLDER"],
        "SAFE_CHECKPOINT": handoff_source["CURRENT_SAFE_CHECKPOINT"],
        "GITHUB_STATE": handoff_source["CURRENT_GITHUB_STATE"],
        "REGISTRY_RESULT": precheck["reuse_component"],
        "LOCAL_TEST_RESULT": "PRECHECK_PASS",
        "WHY_WORK_REQUIRED": config.get("why_work_required", "NEW_JUDGMENT"),
        "EXPECTED_WORK_OUTPUT": list(WORK_RESULT_FIELDS),
    }
    base.update(execution_mode="WORK_REQUIRED", local_stage="HANDOFF_ONLY",
                work_handoff_required="YES", work_reason=handoff["WHY_WORK_REQUIRED"],
                local_result="STOPPED_FOR_WORK_DECISION", handoff=handoff)
    return base


def validate_work_result(value: dict) -> bool:
    return set(WORK_RESULT_FIELDS).issubset(value) and value["UNMODIFIED_USE"] in (True, False)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--central-root", type=Path, required=True)
    p.add_argument("--wic-root", type=Path, required=True)
    p.add_argument("--operating-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--handoff", type=Path)
    a = p.parse_args()
    configs = json.loads(a.config.read_text(encoding="utf-8"))["targets"]
    config = configs.get(a.target, {"tool": a.target})
    result = route(config, {"central": a.central_root, "wic": a.wic_root,
                            "operating": a.operating_root})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    a.output.write_text(payload, encoding="utf-8")
    if result.get("work_handoff_required") == "YES" and a.handoff:
        a.handoff.parent.mkdir(parents=True, exist_ok=True)
        a.handoff.write_text(json.dumps(result["handoff"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
