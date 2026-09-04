"""Fail-closed, local-only Work eligibility precheck for registered WIC targets."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

VALID_SCOPE = {"SMALL", "MEDIUM", "LARGE"}


def resolve(spec: str | None, roots: dict[str, Path]) -> Path | None:
    if not spec:
        return None
    prefix, separator, relative = spec.partition(":")
    if not separator or prefix not in roots:
        raise ValueError("INVALID_PATH_SPEC")
    root = roots[prefix].resolve()
    path = (root / relative).resolve()
    if path != root and root not in path.parents:
        raise ValueError("PATH_OUTSIDE_ROOT")
    return path


def git_state(repo: Path | None) -> str:
    if not repo or not (repo / ".git").exists():
        return "UNKNOWN"
    safe = repo.as_posix()
    status = subprocess.run(
        ["git", "-c", f"safe.directory={safe}", "-C", str(repo), "status", "--porcelain"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )
    if status.returncode or status.stdout.strip():
        return "LOCAL_DIRTY" if status.returncode == 0 else "UNKNOWN"
    head = subprocess.run(
        ["git", "-c", f"safe.directory={safe}", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )
    remote = subprocess.run(
        ["git", "-c", f"safe.directory={safe}", "-C", str(repo), "rev-parse", "refs/remotes/origin/main"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )
    if head.returncode or remote.returncode:
        return "UNKNOWN"
    if head.stdout.strip() == remote.stdout.strip():
        return "CLEAN_MATCH"
    ahead = subprocess.run(
        ["git", "-c", f"safe.directory={safe}", "-C", str(repo), "merge-base", "--is-ancestor", remote.stdout.strip(), head.stdout.strip()]
    ).returncode == 0
    behind = subprocess.run(
        ["git", "-c", f"safe.directory={safe}", "-C", str(repo), "merge-base", "--is-ancestor", head.stdout.strip(), remote.stdout.strip()]
    ).returncode == 0
    return "LOCAL_AHEAD" if ahead else "REMOTE_AHEAD" if behind else "CONFLICT"


def evaluate(config: dict, roots: dict[str, Path]) -> dict:
    required = {"tool", "master", "checkpoint", "runtime", "actual_use_folder", "repo",
                "actual_inputs", "cause_clear", "first_blocker", "test_scope", "deploy_direct",
                "deployed_pass_confident", "repeat_failure", "external_blocker", "user_actions",
                "existing_deployed_pass", "reuse_component"}
    missing = sorted(required - config.keys())
    if missing:
        return {"target_tool": config.get("tool", "UNKNOWN"), "work_eligible": "NO",
                "reason": "CONFIG_FIELDS_MISSING:" + ",".join(missing)}
    if config["test_scope"] not in VALID_SCOPE:
        return {"target_tool": config["tool"], "work_eligible": "NO", "reason": "INVALID_TEST_SCOPE"}

    master = resolve(config["master"], roots)
    checkpoint = resolve(config["checkpoint"], roots)
    runtime = resolve(config["runtime"], roots)
    actual_use = resolve(config["actual_use_folder"], roots)
    repo = resolve(config["repo"], roots)
    input_paths = [resolve(item, roots) for item in config["actual_inputs"]]
    input_ready = bool(input_paths) and all(path and path.exists() for path in input_paths)
    canonical_runtime = "READY" if runtime and runtime.is_file() and actual_use and actual_use.exists() else "UNKNOWN"
    local_remote = git_state(repo)
    user_action_count = len(config["user_actions"])

    if config["existing_deployed_pass"]:
        decision, reason = "SKIP_REUSE", "EXISTING_DEPLOYED_PASS"
    else:
        gates = {
            "INPUT_READY": input_ready,
            "CAUSE_CLEAR": config["cause_clear"] is True and config["first_blocker"] not in (None, "NOT_RESOLVED"),
            "NO_EXTERNAL_BLOCKER": config["external_blocker"] is False,
            "NO_REPEAT_FAILURE": config["repeat_failure"] is False,
            "TEST_SCOPE_SMALL": config["test_scope"] == "SMALL",
            "DEPLOY_DIRECT": config["deploy_direct"] is True and canonical_runtime == "READY",
            "DEPLOYED_PASS_NOW_CONFIDENT": config["deployed_pass_confident"] is True,
            "LOCAL_REMOTE_CLEAN": local_remote == "CLEAN_MATCH",
            "USER_ACTION_BOUNDED": user_action_count <= 1,
            "MASTER_CHECKPOINT_READY": bool(master and master.exists() and checkpoint and checkpoint.exists()),
        }
        failed = [name for name, passed in gates.items() if not passed]
        decision = "YES" if not failed else "NO"
        reason = "READY" if not failed else failed[0]

    result = {
        "target_tool": config["tool"],
        "target_function": config.get("function") or "LATEST_REGISTERED_ITEM",
        "master": "READY" if master and master.exists() else "MISSING",
        "checkpoint": "READY" if checkpoint and checkpoint.exists() else "MISSING",
        "actual_input": "READY" if input_ready else "MISSING",
        "canonical_runtime": canonical_runtime,
        "local_remote": local_remote,
        "first_blocker": config["first_blocker"],
        "reuse_component": config["reuse_component"] or "NONE",
        "test_scope": config["test_scope"],
        "deploy_confidence": "HIGH" if config["deployed_pass_confident"] else "LOW",
        "user_action_count": user_action_count,
        "work_eligible": decision,
        "reason": reason,
    }
    if decision == "YES":
        result["handoff"] = {
            "TARGET_TOOL": config["tool"], "TARGET_FUNCTION": result["target_function"],
            "ACTUAL_INPUT_PATH": [str(path) for path in input_paths],
            "CANONICAL_RUNTIME_PATH": str(runtime), "ACTUAL_USE_FOLDER": str(actual_use),
            "CURRENT_SAFE_CHECKPOINT": str(checkpoint), "CURRENT_GITHUB_STATE": local_remote,
            "KNOWN_BLOCKER": config["first_blocker"], "REUSE_COMPONENT": result["reuse_component"],
            "REQUIRED_TEST_SCOPE": config["test_scope"], "EXPECTED_DEPLOY_PATH": str(actual_use),
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--central-root", type=Path, required=True)
    parser.add_argument("--wic-root", type=Path, required=True)
    parser.add_argument("--operating-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    configs = json.loads(args.config.read_text(encoding="utf-8"))["targets"]
    if args.target not in configs:
        result = {"target_tool": args.target, "work_eligible": "NO", "reason": "TARGET_TOOL_MISSING"}
    else:
        roots = {"central": args.central_root, "wic": args.wic_root, "operating": args.operating_root}
        result = evaluate(configs[args.target], roots)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
