"""Deterministic approval batching and fast-deploy planning for TOOL044."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FAST_DEPLOY_STAGES = [
    "target_test", "expected_actual_compare", "impacted_regression", "evidence",
    "git_commit_push_readback", "actual_use_deploy", "deployed_copy_retest",
    "safe_checkpoint",
]


def plan(local_first: dict, platform_actions: list[dict] | None = None) -> dict:
    actions = platform_actions or []
    required = [a for a in actions if a.get("platform_required") is True]
    avoidable = [a for a in actions if a.get("platform_required") is not True]
    precheck = local_first.get("precheck", "NO")
    local_result = local_first.get("local_result", "EXCLUDE_THIS_RUN")
    component = local_first.get("registry_result") or local_first.get("reuse_component")

    if local_result == "SKIP_REUSE":
        resolution, status = "A_EXISTING_VERIFIED_COMPONENT", "SKIP_REUSE"
        stages = []
    elif precheck != "YES":
        resolution, status = "D_HOLD_NOT_READY", local_result
        stages = []
    elif local_first.get("work_handoff_required") == "YES":
        resolution, status = "B_EXTERNAL_READY_COMPONENT", "WORK_DECISION_REQUIRED"
        stages = []
    elif local_first.get("internal_wic_rule") is True:
        resolution, status = "C_INTERNAL_WIC_RULE", "CANDIDATE_ONLY"
        stages = []
    else:
        resolution, status = ("A_EXISTING_VERIFIED_COMPONENT" if component else
                              "D_HOLD_NOT_READY"), ("FAST_DEPLOY_READY" if component else
                              "EXCLUDE_THIS_RUN")
        stages = list(FAST_DEPLOY_STAGES) if status == "FAST_DEPLOY_READY" else []

    # All unavoidable operations are deliberately represented as one concentrated batch.
    queue = ({"batch_id": "PLATFORM_APPROVAL_BATCH_1", "actions": required}
             if required else None)
    return {
        "target_tool": local_first.get("target_tool", "UNKNOWN"),
        "resolution_type": resolution,
        "status": status,
        "execution_mode": local_first.get("execution_mode", "LOCAL"),
        "fast_deploy_stages": stages,
        "user_action_queue": queue,
        "user_approval_count": 1 if required else 0,
        "platform_required_approval_count": 1 if required else 0,
        "avoidable_approval_count": 0,
        "blocked_avoidable_action_count": len(avoidable),
        "approval_policy": "ONE_CONCENTRATED_BATCH" if required else "NO_APPROVAL",
        "normal_runtime_cost": {"work": 0, "codex": 0, "paid_api": 0, "paid_saas": 0},
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--local-first-result", type=Path, required=True)
    p.add_argument("--actions", type=Path)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    local = json.loads(a.local_first_result.read_text(encoding="utf-8"))
    actions = json.loads(a.actions.read_text(encoding="utf-8")) if a.actions else []
    result = plan(local, actions)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
