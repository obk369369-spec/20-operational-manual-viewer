"""Fail-closed TOOL044 deployment/rollback proof using an isolated fixture.

This module never selects or mutates a production WIC tool.  It proves the
mechanical gate that a later, separately verified target adapter may reuse.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence" / "tool044_safe_integration_fixture.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gate(receipt: dict) -> tuple[bool, list[str]]:
    required = (
        "source_receipt", "artifact_match", "sandbox_pass",
        "expected_actual_match", "real_failure_fixture_pass",
        "normal_fixture_pass", "impact_regression_pass",
        "canonical_identity_pass", "rollback_ready",
        "deployment_target_verified",
    )
    missing = [key for key in required if receipt.get(key) is not True]
    return not missing, missing


def run_fixture() -> dict:
    with tempfile.TemporaryDirectory(prefix="tool044-safe-") as raw:
        root = Path(raw)
        canonical = root / "canonical.txt"
        deployed = root / "deployed.txt"
        checkpoint = root / "safe-checkpoint.txt"
        canonical.write_text("verified-release-v1\n", encoding="utf-8")
        deployed.write_bytes(canonical.read_bytes())
        checkpoint.write_bytes(deployed.read_bytes())

        complete = {key: True for key in (
            "source_receipt", "artifact_match", "sandbox_pass",
            "expected_actual_match", "real_failure_fixture_pass",
            "normal_fixture_pass", "impact_regression_pass",
            "canonical_identity_pass", "rollback_ready",
            "deployment_target_verified",
        )}
        allowed, missing = gate(complete)
        canonical.write_text("verified-release-v2\n", encoding="utf-8")
        if allowed:
            deployed.write_bytes(canonical.read_bytes())
        deployed_copy_pass = sha256(deployed) == sha256(canonical)

        # A failed deployed-copy check must restore the previous safe copy.
        deployed.write_text("corrupt-partial-release\n", encoding="utf-8")
        failure_detected = sha256(deployed) != sha256(canonical)
        if failure_detected:
            deployed.write_bytes(checkpoint.read_bytes())
        rollback_pass = deployed.read_text(encoding="utf-8") == "verified-release-v1\n"

        denied, denied_missing = gate({**complete, "impact_regression_pass": False})
        passed = all((allowed, not missing, deployed_copy_pass, failure_detected,
                      rollback_pass, not denied, denied_missing == ["impact_regression_pass"]))
        return {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scope": "ISOLATED_NON_PRODUCTION_FIXTURE",
            "production_tool_mutation": False,
            "tests": {
                "complete_receipt_allows_deploy": allowed,
                "deployed_copy_hash_match": deployed_copy_pass,
                "failed_copy_detected": failure_detected,
                "automatic_rollback_restores_safe_checkpoint": rollback_pass,
                "incomplete_receipt_blocks_deploy": not denied,
                "blocked_reason": denied_missing,
            },
            "expected_actual": "MATCH" if passed else "MISMATCH",
            "safe_fixture_deploy_gate": "VERIFIED" if passed else "FAIL",
            "safe_fixture_auto_rollback": "VERIFIED" if passed else "FAIL",
            "arbitrary_wic_tool_auto_deploy": "NOT_IMPLEMENTED",
            "truth_boundary": "Fixture proof does not authorize an unverified production target adapter.",
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run_fixture()
    if result["expected_actual"] != "MATCH":
        raise SystemExit(json.dumps(result, ensure_ascii=False))
    if not args.self_test:
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
