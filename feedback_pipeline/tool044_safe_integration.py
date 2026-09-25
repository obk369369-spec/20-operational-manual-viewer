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

READY_COMPONENT_FIELDS = (
    "component_id", "source", "license", "target_root", "target_tool", "version",
    "input_contract", "output_contract", "install_target", "validator",
    "install_method", "success_condition", "failure_condition", "rollback_method",
    "rollback_condition", "evidence",
)

WORK_REENTRY_RECEIPTS = (
    "target_file_confirmed", "root_confirmed", "ready_component_confirmed",
    "expected_change_confirmed", "validation_method_confirmed", "sandbox_component_pass",
)


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


def component_reentry_gate(component: dict, receipts: dict) -> dict:
    """Fail closed until a TOOL044 component is directly installable and testable."""
    missing_fields = [key for key in READY_COMPONENT_FIELDS if not component.get(key)]
    missing_receipts = [key for key in WORK_REENTRY_RECEIPTS if receipts.get(key) is not True]
    allowed = not missing_fields and not missing_receipts
    return {
        "status": "READY_FOR_WORK_REENTRY" if allowed else "HOLD_COMPONENT_CONTRACT_INCOMPLETE",
        "work_reentry_allowed": allowed,
        "component_id": component.get("component_id"),
        "target_root": component.get("target_root"),
        "target_tool": component.get("target_tool"),
        "missing_fields": missing_fields,
        "missing_receipts": missing_receipts,
    }


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



def registered_target_deploy(component: dict, receipts: dict, workspace: Path) -> dict:
    """Deploy only an explicitly registered target contract; fail closed otherwise."""
    admission = component_reentry_gate(component, receipts)
    if not admission["work_reentry_allowed"]:
        return {**admission, "deployment_status": "HOLD_NOT_REGISTERED_READY"}

    workspace = workspace.resolve()
    canonical = (workspace / component["source_file"]).resolve()
    deployed = (workspace / component["install_target"]).resolve()
    try:
        canonical.relative_to(workspace)
        deployed.relative_to(workspace)
    except ValueError:
        return {**admission, "deployment_status": "HOLD_TARGET_OUTSIDE_WORKSPACE"}

    if not canonical.is_file():
        return {**admission, "deployment_status": "HOLD_CANONICAL_MISSING"}
    deployed.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = deployed.read_bytes() if deployed.exists() else None
    expected_hash = sha256(canonical)

    deployed.write_bytes(canonical.read_bytes())
    copy_match = sha256(deployed) == expected_hash
    validator = component.get("deployed_validator")
    validator_pass = bool(copy_match)
    if validator:
        import subprocess
        proc = subprocess.run(
            [str(x).replace("{deployed}", str(deployed)) for x in validator],
            cwd=workspace, capture_output=True, text=True
        )
        validator_pass = proc.returncode == 0

    rollback = False
    if not (copy_match and validator_pass):
        rollback = True
        if checkpoint is None:
            deployed.unlink(missing_ok=True)
        else:
            deployed.write_bytes(checkpoint)

    final_match = deployed.exists() and sha256(deployed) == expected_hash
    passed = copy_match and validator_pass and final_match
    return {
        **admission,
        "deployment_status": "DEPLOYED_PASS" if passed else "FAIL_ROLLED_BACK",
        "verified_target_deployment": passed,
        "deployed_copy_validation": passed,
        "safe_automatic_rollback": rollback if not passed else True,
        "canonical_sha256": expected_hash,
        "deployed_sha256": sha256(deployed) if deployed.exists() else None,
        "rollback_executed": rollback,
    }


def registered_target_self_test() -> dict:
    """Exercise the reusable registered-target adapter, including forced rollback."""
    with tempfile.TemporaryDirectory(prefix="tool044-registered-target-") as raw:
        root = Path(raw)
        source = root / "canonical.txt"
        target = root / "deployed.txt"
        source.write_text("release-v2\n", encoding="utf-8")
        target.write_text("release-v1\n", encoding="utf-8")
        base = {
            "component_id": "REGISTERED_TARGET_FIXTURE",
            "source": "LOCAL_VERIFIED_FIXTURE",
            "license": "INTERNAL_TEST",
            "target_root": "TOOL044-ARBITRARY-WIC-DEPLOY",
            "target_tool": "TOOL044",
            "version": "1",
            "input_contract": "verified canonical bytes",
            "output_contract": "byte-identical deployed copy",
            "install_target": "deployed.txt",
            "validator": ["hash"],
            "install_method": ["copy"],
            "success_condition": "byte identity",
            "failure_condition": "copy or validator mismatch",
            "rollback_method": ["restore checkpoint"],
            "rollback_condition": "any validation failure",
            "evidence": "self-test",
            "source_file": "canonical.txt",
        }
        receipts = {key: True for key in WORK_REENTRY_RECEIPTS}
        ok = registered_target_deploy(base, receipts, root)

        target.write_text("release-v1\n", encoding="utf-8")
        bad = {**base, "deployed_validator": ["python", "-c", "raise SystemExit(1)"]}
        failed = registered_target_deploy(bad, receipts, root)
        rollback_restored = target.read_text(encoding="utf-8") == "release-v1\n"

        passed = (
            ok["deployment_status"] == "DEPLOYED_PASS"
            and ok["verified_target_deployment"]
            and ok["deployed_copy_validation"]
            and failed["deployment_status"] == "FAIL_ROLLED_BACK"
            and failed["rollback_executed"]
            and rollback_restored
        )
        return {
            "status": "PASS" if passed else "FAIL",
            "scope": "REUSABLE_REGISTERED_TARGET_ADAPTER_MECHANICS",
            "verified_target_deployment": ok["verified_target_deployment"],
            "deployed_copy_validation": ok["deployed_copy_validation"],
            "forced_failure_rollback": rollback_restored,
            "unregistered_target_allowed": False,
            "production_target_claim": False,
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
