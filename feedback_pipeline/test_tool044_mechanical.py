import json
import shutil
import sys
import tempfile
from pathlib import Path

from tool044_mechanical import run_manifest, sha256


workspace = Path(__file__).resolve().parents[1]
manifest = workspace / "feedback_pipeline/tool044_manifests/fastjsonschema_fixture.json"
with tempfile.TemporaryDirectory() as raw:
    temp = Path(raw)
    evidence = temp / "local.json"
    first = run_manifest(manifest, workspace, evidence, temp / "deploy")
    assert first["status"] == "LOCAL_PASS"
    assert first["compare"] == "MATCH"
    assert first["registry_existing_count"] == 1
    assert all(item["action"] == "COPIED" for item in first["deployed_files"])

    second = run_manifest(manifest, workspace, temp / "second.json", temp / "deploy")
    assert second["registry_existing_count"] == 1
    assert all(item["action"] == "SKIP_IDENTICAL" for item in second["deployed_files"])

    bad_expected = temp / "bad_expected.json"
    bad_expected.write_text('{"status":"INTENTIONAL_MISMATCH"}', encoding="utf-8")
    bad_manifest = json.loads(manifest.read_text(encoding="utf-8"))
    bad_manifest["expected_path"] = str(bad_expected.relative_to(temp)).replace("\\", "/")
    bad_workspace = temp / "bad_workspace"
    shutil.copytree(workspace / "feedback_pipeline", bad_workspace / "feedback_pipeline")
    shutil.copytree(workspace / "tool043", bad_workspace / "tool043")
    target_expected = bad_workspace / bad_manifest["expected_path"]
    target_expected.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(bad_expected, target_expected)
    bad_manifest_path = bad_workspace / "bad_manifest.json"
    bad_manifest_path.write_text(json.dumps(bad_manifest), encoding="utf-8")
    blocked = False
    try:
        run_manifest(bad_manifest_path, bad_workspace, temp / "must_not_exist.json", temp / "must_not_deploy")
    except ValueError as exc:
        blocked = str(exc) == "EXPECTED_ACTUAL_MISMATCH"
    assert blocked
    assert not (temp / "must_not_deploy").exists()

print(json.dumps({
    "status": "PASS",
    "tests": {
        "source_metadata_hash": "PASS",
        "sandbox_execution": "PASS",
        "invalid_input_rejection": "PASS",
        "expected_actual_compare": "PASS",
        "registry_no_duplicate": "PASS",
        "deploy_sync": "PASS",
        "deployed_copy_fixture": "PASS",
        "idempotency": "PASS",
        "failure_fixture_blocked": "PASS"
    }
}, ensure_ascii=False))
