"""Manifest-driven mechanical gates for an already admitted TOOL044 component.

This runner does not search for components or make WIC business decisions.  It
records immutable source metadata, executes the declared local test, compares
its structured result, prevents duplicate registry entries, and deploys only
after every mechanical gate passes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def subset_matches(expected, actual) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and subset_matches(value, actual[key])
            for key, value in expected.items()
        )
    if isinstance(expected, list):
        return expected == actual
    return expected == actual


def resolve_under(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if root.resolve() not in candidate.parents and candidate != root.resolve():
        raise ValueError("PATH_OUTSIDE_ROOT")
    return candidate


def expand_command(command, workspace: Path, result_path: Path):
    values = {
        "python": sys.executable,
        "workspace": str(workspace),
        "result": str(result_path),
    }
    return [part.format(**values) for part in command]


def run_manifest(manifest_path: Path, workspace: Path, evidence_path: Path,
                 deploy_root: Path | None = None, deployed_mode: bool = False):
    workspace = workspace.resolve()
    manifest = load_json(manifest_path)
    source = resolve_under(workspace, manifest["source_path"])
    expected = load_json(resolve_under(workspace, manifest["expected_path"]))
    registry_path = resolve_under(workspace, manifest["registry_path"])
    registry = load_json(registry_path)
    component_id = manifest["component_id"]
    source_hash = sha256(source)
    if source_hash != manifest["source_sha256"]:
        raise ValueError("SOURCE_HASH_MISMATCH")
    if manifest.get("external_modified") is not False:
        raise ValueError("EXTERNAL_COMPONENT_MODIFICATION_BLOCKED")

    matches = [item for item in registry["components"] if item.get("component_id") == component_id]
    if len(matches) > 1:
        raise ValueError("REGISTRY_IDEMPOTENCY_BLOCKED")
    if matches and matches[0].get("source_sha256") != source_hash:
        raise ValueError("REGISTRY_SOURCE_CONFLICT")

    result_path = evidence_path.with_suffix(".actual.json")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    command = expand_command(manifest["sandbox_command"], workspace, result_path)
    completed = subprocess.run(
        command, cwd=workspace, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=manifest.get("timeout_seconds", 180),
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    actual = load_json(result_path) if result_path.exists() else None
    comparison = completed.returncode == 0 and subset_matches(expected, actual)
    if not comparison:
        raise ValueError("EXPECTED_ACTUAL_MISMATCH")

    registry_action = "SKIP_IDENTICAL"
    if not matches:
        registry["components"].append({
            "component_id": component_id,
            "status": "VERIFIED_REUSABLE",
            "name": manifest["component_name"],
            "version": manifest["version"],
            "source": manifest["official_source"],
            "license": manifest["license"],
            "source_file": manifest["source_path"],
            "source_sha256": source_hash,
            "external_modified": False,
            "runtime_cost": manifest["runtime_cost"],
            "integration_target": manifest["integration_target"],
            "sandbox_result": "PASS",
            "reuse_requires_target_retest": True,
        })
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        registry_action = "REGISTERED_AFTER_PASS"

    deployed_files = []
    if deploy_root is not None:
        deploy_root = deploy_root.resolve()
        for relative in manifest["deploy_files"]:
            src = resolve_under(workspace, relative)
            dst = deploy_root / relative
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists() and sha256(dst) == sha256(src):
                action = "SKIP_IDENTICAL"
            else:
                shutil.copy2(src, dst)
                action = "COPIED"
            if sha256(dst) != sha256(src):
                raise ValueError("DEPLOY_HASH_MISMATCH")
            deployed_files.append({"path": relative, "sha256": sha256(dst), "action": action})

    record = {
        "status": "DEPLOYED_PASS" if deployed_mode else "LOCAL_PASS",
        "component_id": component_id,
        "component_name": manifest["component_name"],
        "version": manifest["version"],
        "official_source": manifest["official_source"],
        "license": manifest["license"],
        "acquired_at": manifest["acquired_at"],
        "runtime_cost": manifest["runtime_cost"],
        "source_path": manifest["source_path"],
        "source_sha256": source_hash,
        "external_modified": False,
        "sandbox_command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
        "expected": expected,
        "actual": actual,
        "compare": "MATCH",
        "registry_existing_count": len(matches),
        "registry_action": registry_action,
        "deployed_files": deployed_files,
        "deployed_retest_result": "PASS" if deployed_mode else "PENDING_REMOTE_AND_ACTUAL_DEPLOY",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    evidence_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deploy-root", type=Path)
    parser.add_argument("--deployed-mode", action="store_true")
    args = parser.parse_args()
    result = run_manifest(args.manifest, args.workspace, args.evidence,
                          args.deploy_root, args.deployed_mode)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
