import importlib.util
from pathlib import Path


module_path = Path(__file__).resolve().parents[1] / "CONTROL_TOWER" / "controller" / "pre_work_admission.py"
spec = importlib.util.spec_from_file_location("pre_work_admission_output_gate", module_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)

sha = "a" * 64
receipt = {
    "work_id": "W", "task_id": "TOOLX", "execution_id": "producer-1",
    "independent_validator_id": "validator-1", "source_receipt_sha256": "b" * 64,
    "actual_result_ref": {"path": "evidence/output.pdf", "sha256": sha},
}
reopen = {
    "work_id": "W", "task_id": "TOOLX", "parser_id": "pdf-parser-1",
    "validator_id": "validator-1", "reopen_execution_id": "reopen-2",
    "artifact_format": "PDF", "artifact_sha256": sha,
    "source_receipt_sha256": "b" * 64, "validation_result": "PASS",
    "format_checks": {"parseable": True, "page_count_verified": True, "content_verified": True},
}
remote = {
    "commit_sha": "c" * 40, "blob_oid": "d" * 40, "retrieval_id": "remote-fetch-3",
    "remote_url": "https://github.com/example/repo/blob/commit/evidence/output.pdf",
    "artifact_path": "evidence/output.pdf", "retrieved_sha256": sha, "validation_result": "PASS",
}

assert module.validate_output_reopen_and_remote(receipt, reopen, remote) is None

bad = dict(reopen)
bad.pop("parser_id")
assert module.validate_output_reopen_and_remote(receipt, bad, remote) == "ARTIFACT_REOPEN_INDEPENDENT_VALIDATION_MISMATCH"
bad = dict(reopen, reopen_execution_id="producer-1")
assert module.validate_output_reopen_and_remote(receipt, bad, remote) == "ARTIFACT_REOPEN_INDEPENDENT_VALIDATION_MISMATCH"
bad = dict(reopen, format_checks={"parseable": True, "content_verified": False})
assert module.validate_output_reopen_and_remote(receipt, bad, remote) == "ARTIFACT_REOPEN_INDEPENDENT_VALIDATION_MISMATCH"
bad_remote = dict(remote, commit_sha="LOCAL")
assert module.validate_output_reopen_and_remote(receipt, reopen, bad_remote) == "REMOTE_READBACK_IDENTITY_MISMATCH"
bad_remote = dict(remote, retrieved_sha256="e" * 64)
assert module.validate_output_reopen_and_remote(receipt, reopen, bad_remote) == "REMOTE_READBACK_IDENTITY_MISMATCH"
bad_remote = dict(remote, artifact_path="evidence/other.pdf")
assert module.validate_output_reopen_and_remote(receipt, reopen, bad_remote) == "REMOTE_READBACK_IDENTITY_MISMATCH"

tool013 = dict(receipt, task_id="TOOL013")
tool013_reopen = dict(reopen, task_id="TOOL013", artifact_format="XLSX",
                      format_checks={"parseable": True, "exact_18_columns": True,
                                     "download_reopened": True, "content_verified": True})
assert module.validate_output_reopen_and_remote(tool013, tool013_reopen, remote) is None

print("PASS: common output reopen and remote blob readback gate; 6 negative mutations blocked")

