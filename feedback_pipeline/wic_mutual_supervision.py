"""Deterministic multi-layer WIC supervisor/auditor built on TOOL044 execution rules.

Purpose: keep the human observer out of intermediate repair work. Every stage is
checked by an independent layer; false HOLD/COMPLETE claims are rejected; a
stopped run resumes from the last SAFE_CHECKPOINT whenever the blocker is not a
verified external/user-only condition.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

try:
    from tool044_fast_deploy import FAST_DEPLOY_STAGES
except Exception:  # pragma: no cover - standalone fallback for bootstrap only
    FAST_DEPLOY_STAGES = [
        "target_test", "expected_actual_compare", "impacted_regression", "evidence",
        "git_commit_push_readback", "actual_use_deploy", "deployed_copy_retest",
        "safe_checkpoint",
    ]

LAYERS = (
    "L1_START_PRECHECK",
    "L2_CAUSE_AUDIT",
    "L3_CHANGE_GUARD",
    "L4_TEST_AUDIT",
    "L5_STOP_RECOVERY",
    "L6_DEPLOY_GUARD",
    "L7_POST_DEPLOY_AUDIT",
)

PEER_AUDITOR = {
    "L1_START_PRECHECK": "L7_POST_DEPLOY_AUDIT",
    "L2_CAUSE_AUDIT": "L5_STOP_RECOVERY",
    "L3_CHANGE_GUARD": "L4_TEST_AUDIT",
    "L4_TEST_AUDIT": "L3_CHANGE_GUARD",
    "L5_STOP_RECOVERY": "L7_POST_DEPLOY_AUDIT",
    "L6_DEPLOY_GUARD": "L7_POST_DEPLOY_AUDIT",
    "L7_POST_DEPLOY_AUDIT": "L1_START_PRECHECK",
}

STAGE_ORDER = (
    "START", "DIAGNOSE", "FIX", "TEST", "GITHUB", "DEPLOY", "DEPLOYED_TEST", "COMPLETE"
)
STOP_WORDS = {"HOLD", "WAITING", "NOT_FOUND", "STOPPED", "FAIL", "FAILED", "COMPLETE"}

REQUIRED_BY_STAGE = {
    "START": ("master_loaded", "checkpoint_loaded", "actual_input_ready"),
    "DIAGNOSE": ("cause_grouped",),
    "TEST": ("expected_defined", "actual_executed", "compare_match", "impacted_regression_pass"),
    "GITHUB": ("git_push", "remote_readback"),
    "DEPLOY": ("actual_use_deploy",),
    "DEPLOYED_TEST": ("deployed_copy_test",),
    "COMPLETE": ("safe_checkpoint_written",),
}

FINAL_EVIDENCE = (
    "master_loaded", "checkpoint_loaded", "actual_input_ready", "cause_grouped",
    "expected_defined", "actual_executed", "compare_match", "impacted_regression_pass",
    "git_push", "remote_readback", "actual_use_deploy", "deployed_copy_test",
    "safe_checkpoint_written",
)


@dataclass(frozen=True)
class Decision:
    decision: str
    next_stage: str
    recovery_owner: str
    user_action: str = "NONE"
    reason: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "decision": self.decision,
            "next_stage": self.next_stage,
            "recovery_owner": self.recovery_owner,
            "user_action": self.user_action,
            "reason": self.reason,
        }


def _truth(evidence: Mapping[str, Any], key: str) -> bool:
    return evidence.get(key) is True


def _missing(evidence: Mapping[str, Any], keys: tuple[str, ...] | list[str]) -> list[str]:
    return [k for k in keys if not _truth(evidence, k)]


def _previous_stage(stage: str) -> str:
    try:
        idx = STAGE_ORDER.index(stage)
    except ValueError:
        return "START"
    return STAGE_ORDER[max(0, idx - 1)]


def _next_stage(stage: str) -> str:
    try:
        idx = STAGE_ORDER.index(stage)
    except ValueError:
        return "START"
    return STAGE_ORDER[min(len(STAGE_ORDER) - 1, idx + 1)]


def _required_layer(stage: str) -> str:
    return {
        "START": "L1_START_PRECHECK",
        "DIAGNOSE": "L2_CAUSE_AUDIT",
        "FIX": "L3_CHANGE_GUARD",
        "TEST": "L4_TEST_AUDIT",
        "GITHUB": "L6_DEPLOY_GUARD",
        "DEPLOY": "L6_DEPLOY_GUARD",
        "DEPLOYED_TEST": "L7_POST_DEPLOY_AUDIT",
        "COMPLETE": "L7_POST_DEPLOY_AUDIT",
    }.get(stage, "L1_START_PRECHECK")


def _layer_failure(state: Mapping[str, Any], stage: str) -> Decision | None:
    health = state.get("layer_health", {})
    layer = _required_layer(stage)
    if health.get(layer, "OK") == "OK":
        return None
    peer = PEER_AUDITOR[layer]
    if health.get(peer, "OK") == "OK":
        return Decision(
            "RECOVER_LAYER_AND_RESUME",
            stage,
            peer,
            reason=f"{layer} unhealthy; peer {peer} must repair/reload it before execution continues.",
        )
    return Decision(
        "SYSTEM_RECOVERY_REQUIRED",
        state.get("safe_checkpoint_stage") or _previous_stage(stage),
        "DETERMINISTIC_BOOTSTRAP",
        reason=f"{layer} and peer {peer} unhealthy; restore canonical code/checkpoint then resume.",
    )


def evaluate(state: Mapping[str, Any]) -> dict[str, Any]:
    stage = str(state.get("stage", "START")).upper()
    if stage not in STAGE_ORDER:
        stage = "START"
    status = str(state.get("status", "RUNNING")).upper()
    evidence = state.get("evidence", {})

    layer_problem = _layer_failure(state, stage)
    if layer_problem:
        result = layer_problem.as_dict()
        result.update(target_tool=state.get("target_tool", "UNKNOWN"), stage=stage,
                      observer_role="RESULT_ONLY", fast_deploy_reuse=list(FAST_DEPLOY_STAGES))
        return result

    if status in STOP_WORDS:
        if status == "COMPLETE":
            missing = _missing(evidence, FINAL_EVIDENCE)
            if missing:
                d = Decision(
                    "COMPLETE_REJECTED_RESUME_REQUIRED",
                    state.get("safe_checkpoint_stage") or _previous_stage(stage),
                    "L7_POST_DEPLOY_AUDIT",
                    reason="Missing completion evidence: " + ",".join(missing),
                )
            else:
                d = Decision("DEPLOYED_PASS", "COMPLETE", "L7_POST_DEPLOY_AUDIT",
                             reason="All final evidence present.")
            result = d.as_dict()
            result.update(target_tool=state.get("target_tool", "UNKNOWN"), stage=stage,
                          observer_role="RESULT_ONLY", fast_deploy_reuse=list(FAST_DEPLOY_STAGES))
            return result

        external_confirmed = _truth(evidence, "external_hold_confirmed")
        search_complete = _truth(evidence, "evidence_search_complete")
        user_only = _truth(evidence, "user_only_action_confirmed")
        if external_confirmed and search_complete:
            d = Decision(
                "HOLD_EXTERNAL_CONFIRMED", stage, "L5_STOP_RECOVERY",
                user_action=(state.get("queued_user_action") if user_only else "NONE") or "NONE",
                reason="Independent audit confirmed a genuine external blocker.",
            )
        else:
            d = Decision(
                "STOP_REJECTED_RESUME_REQUIRED",
                state.get("safe_checkpoint_stage") or _previous_stage(stage),
                "L5_STOP_RECOVERY",
                reason="Stop/HOLD/NOT_FOUND not independently proven; resume from SAFE_CHECKPOINT.",
            )
        result = d.as_dict()
        result.update(target_tool=state.get("target_tool", "UNKNOWN"), stage=stage,
                      observer_role="RESULT_ONLY", fast_deploy_reuse=list(FAST_DEPLOY_STAGES))
        return result

    required = REQUIRED_BY_STAGE.get(stage, ())
    missing = _missing(evidence, required)
    if missing:
        d = Decision(
            "STAGE_BLOCKED_REPAIR_AND_RESUME",
            state.get("safe_checkpoint_stage") or _previous_stage(stage),
            PEER_AUDITOR[_required_layer(stage)],
            reason=f"{stage} evidence missing: " + ",".join(missing),
        )
    elif stage == "COMPLETE":
        missing_final = _missing(evidence, FINAL_EVIDENCE)
        if missing_final:
            d = Decision(
                "COMPLETE_REJECTED_RESUME_REQUIRED",
                state.get("safe_checkpoint_stage") or "DEPLOYED_TEST",
                "L7_POST_DEPLOY_AUDIT",
                reason="Missing completion evidence: " + ",".join(missing_final),
            )
        else:
            d = Decision("DEPLOYED_PASS", "COMPLETE", "L7_POST_DEPLOY_AUDIT",
                         reason="All final evidence present.")
    else:
        d = Decision("CONTINUE", _next_stage(stage), PEER_AUDITOR[_required_layer(stage)],
                     reason="Current stage passed independent gate; continue automatically.")

    result = d.as_dict()
    result.update(
        target_tool=state.get("target_tool", "UNKNOWN"),
        stage=stage,
        observer_role="RESULT_ONLY",
        user_intermediate_operation="FORBIDDEN_BY_DEFAULT",
        fast_deploy_reuse=list(FAST_DEPLOY_STAGES),
        layer_count=len(LAYERS),
        layers=list(LAYERS),
    )
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    state = json.loads(a.state.read_text(encoding="utf-8"))
    result = evaluate(state)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
