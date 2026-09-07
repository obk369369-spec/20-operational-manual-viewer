"""Deterministic multi-target WIC orchestration over verified common gates.

This layer does not execute arbitrary manifest commands.  It schedules independent
evidence lanes, reuses completed targets, isolates failures and delegates every
stage decision to the existing mutual-supervision engine.
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Iterable, Mapping

from wic_mutual_supervision import evaluate


def _lane_result(lane: Mapping[str, Any]) -> dict[str, Any]:
    tool = str(lane.get("target_tool", "UNKNOWN"))
    operation = str(lane.get("operation_id", "UNKNOWN"))
    base = {
        "target_tool": tool,
        "operation_id": operation,
        "lock_key": str(lane.get("lock_key", tool)),
    }

    if lane.get("existing_deployed_pass") is True and lane.get("change_detected") is not True:
        return {
            **base,
            "decision": "SKIP_REUSE",
            "next_stage": "COMPLETE",
            "isolated": False,
            "reason": "Existing DEPLOYED_PASS evidence is unchanged.",
        }

    if lane.get("change_detected") is not True:
        return {
            **base,
            "decision": "HOLD_NO_CHANGE_EVIDENCE",
            "next_stage": "START",
            "isolated": True,
            "reason": "No verified change or reusable completion evidence.",
        }

    if lane.get("impact_known") is not True:
        return {
            **base,
            "decision": "HOLD_IMPACT_UNKNOWN",
            "next_stage": str(lane.get("safe_checkpoint_stage", "START")),
            "isolated": True,
            "reason": "Impact scope cannot be bounded safely.",
        }

    if str(lane.get("status", "RUNNING")).upper() in {"FAIL", "FAILED", "STOPPED"}:
        repeat = lane.get("failure_method_id") and (
            lane.get("failure_method_id") == lane.get("previous_failure_method_id")
        )
        if repeat:
            return {
                **base,
                "decision": "REPEAT_FAILURE_ISOLATED",
                "next_stage": str(lane.get("safe_checkpoint_stage", "START")),
                "isolated": True,
                "reason": "The same failed method is blocked.",
            }
        if lane.get("safe_auto_recovery") is True and lane.get("safe_checkpoint_stage"):
            return {
                **base,
                "decision": "FAIL_ISOLATED_RECOVERY_READY",
                "next_stage": str(lane["safe_checkpoint_stage"]),
                "isolated": True,
                "reason": "Resume only the failed impact scope from SAFE_CHECKPOINT.",
            }

    supervised = evaluate(lane)
    return {
        **base,
        **supervised,
        "isolated": supervised["decision"] not in {"CONTINUE", "DEPLOYED_PASS"},
    }


def _run_lock_group(lanes: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    # Lanes sharing one repo/asset lock are intentionally serialized.
    return [_lane_result(lane) for lane in lanes]


def orchestrate(manifest: Mapping[str, Any]) -> dict[str, Any]:
    lanes = list(manifest.get("lanes", []))
    groups: dict[str, list[Mapping[str, Any]]] = {}
    for lane in lanes:
        key = str(lane.get("lock_key", lane.get("target_tool", "UNKNOWN")))
        groups.setdefault(key, []).append(lane)

    results: list[dict[str, Any]] = []
    if groups:
        with ThreadPoolExecutor(max_workers=min(len(groups), int(manifest.get("max_workers", 4)))) as pool:
            for group_results in pool.map(_run_lock_group, groups.values()):
                results.extend(group_results)
    results.sort(key=lambda item: (item["target_tool"], item["operation_id"]))

    counts: dict[str, int] = {}
    for item in results:
        counts[item["decision"]] = counts.get(item["decision"], 0) + 1
    return {
        "schema_version": 1,
        "status": "PASS" if all(item["decision"] != "SYSTEM_RECOVERY_REQUIRED" for item in results) else "FAIL",
        "execution_policy": {
            "skip_reuse": True,
            "change_only": True,
            "impact_only": True,
            "fail_only_retry": True,
            "remote_readback_reuse": True,
            "safe_checkpoint_resume": True,
            "arbitrary_manifest_commands": False,
        },
        "parallel_lock_groups": len(groups),
        "lane_count": len(results),
        "decision_counts": counts,
        "results": results,
        "user_action_queue": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = orchestrate(json.loads(args.manifest.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
