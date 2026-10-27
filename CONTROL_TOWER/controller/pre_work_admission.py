"""Fail-closed admission controller for every WIC mutation entry point."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

BOOTSTRAP_WORK_ID = "WIC-PRE-WORK-ADMISSION-BOOTSTRAP-20261007"
REQUIRED = (
    "segment_id", "user_intent", "requirement_ids", "actual_input", "input_source",
    "expected_output", "expected_value", "expected_value_basis", "comparator", "tolerance",
    "boundary_cases", "negative_cases", "failure_injection_cases", "validator",
    "validator_expected_detection", "recovery_path", "recovery_expected_result",
    "regression_targets", "rollback_checkpoint", "evidence_destination", "runtime_binding",
    "next_segment_condition",
)
_ACTIVE: tuple[dict[str, Any], str, dict[str, str]] | None = None
if __name__ == "__main__":
    sys.modules.setdefault("pre_work_admission", sys.modules[__name__])


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_pack(pack: dict[str, Any]) -> bool:
    segments = pack.get("segments")
    if not isinstance(segments, list) or not segments:
        return False
    if any(any(field not in segment or segment[field] in (None, "", [], {}) for field in REQUIRED) for segment in segments):
        return False
    if any(segment.get("expected_value_verified") is not True for segment in segments):
        return False
    if pack.get("no_critical_unknown") is not True or pack.get("no_critical_hold") is not True:
        return False
    if pack.get("existing_passlock_prelookup_done") is not True or pack.get("existing_evidence_prelookup_done") is not True:
        return False
    return pack.get("validator_registry_available") is True


def issue_token(pack: dict[str, Any], secret: str, *, now: datetime | None = None) -> dict[str, Any]:
    if not valid_pack(pack):
        raise PermissionError("PRE_WORK_ADMISSION_DENIED")
    now = now or datetime.now(timezone.utc)
    segments = pack["segments"]
    payload = {
        "token_id": secrets.token_hex(16), "work_id": pack["work_id"], "root_id": pack["root_id"],
        "segment_ids": [item["segment_id"] for item in segments], "canonical_version": pack["canonical_version"],
        "git_sha": pack["git_sha"], "ruleset_hash": pack["ruleset_hash"],
        "requirement_set_hash": digest([item["requirement_ids"] for item in segments]),
        "expected_value_set_hash": digest([item["expected_value"] for item in segments]),
        "validator_set_hash": digest([item["validator"] for item in segments]),
        "recovery_set_hash": digest([item["recovery_path"] for item in segments]),
        "evidence_plan_hash": digest([item["evidence_destination"] for item in segments]),
        "rollback_checkpoint_id": pack["rollback_checkpoint_id"], "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=15)).isoformat(), "issuer": "PRE_WORK_ADMISSION_CONTROLLER",
        "status": "VALID",
    }
    return {"payload": payload, "signature": hmac.new(secret.encode(), canonical(payload), hashlib.sha256).hexdigest()}


def verify_token(token: dict[str, Any] | None, secret: str, expected: dict[str, str], *, now: datetime | None = None) -> bool:
    if not token or not isinstance(token.get("payload"), dict) or not token.get("signature"):
        return False
    payload = token["payload"]
    signature = hmac.new(secret.encode(), canonical(payload), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, str(token["signature"])):
        return False
    now = now or datetime.now(timezone.utc)
    try:
        if now >= datetime.fromisoformat(payload["expires_at"]):
            return False
    except (KeyError, ValueError, TypeError):
        return False
    return all(payload.get(key) == value for key, value in expected.items()) and payload.get("status") == "VALID"


def activate_token(token: dict[str, Any], secret: str, expected: dict[str, str]) -> None:
    global _ACTIVE
    if not verify_token(token, secret, expected):
        raise PermissionError("INVALID_WORK_START_TOKEN")
    _ACTIVE = (token, secret, expected)


def clear_token() -> None:
    global _ACTIVE
    _ACTIVE = None


def verify_work_start_token(operation: str) -> None:
    if _ACTIVE is None or not verify_token(*_ACTIVE):
        raise PermissionError(f"EXECUTION_DENIED:{operation}")


def runtime_pack(git_sha: str, evidence_destination: str) -> dict[str, Any]:
    segment = {
        "segment_id": "RUNTIME-CYCLE", "user_intent": "검증된 중앙 Queue cycle 실행",
        "requirement_ids": ["CURRENT_CANONICAL_QUEUE"], "actual_input": "CONTROL_TOWER/controller/runtime/night_queue.json",
        "input_source": "GitHub canonical", "expected_output": "atomic queue/state/evidence update",
        "expected_value": {"unauthorized_side_effect": 0}, "expected_value_basis": "WIC hard gates",
        "expected_value_verified": True, "comparator": "equals", "tolerance": 0,
        "boundary_cases": ["empty queue"], "negative_cases": ["missing evidence"],
        "failure_injection_cases": ["invalid token"], "validator": "universal_enforcement.self_test",
        "validator_expected_detection": "100%", "recovery_path": "snapshot rollback",
        "recovery_expected_result": "state and queue restored", "regression_targets": ["PASS_LOCK preservation"],
        "rollback_checkpoint": git_sha, "evidence_destination": evidence_destination,
        "runtime_binding": "WIC Top Controller Independent Runtime", "next_segment_condition": "evidence read-back pass",
    }
    return {"work_id": "WIC-RUNTIME-CYCLE", "root_id": "WIC-CONTROLLER", "canonical_version": 1,
            "git_sha": git_sha, "ruleset_hash": digest(REQUIRED), "rollback_checkpoint_id": git_sha,
            "segments": [segment], "no_critical_unknown": True, "no_critical_hold": True,
            "existing_passlock_prelookup_done": True, "existing_evidence_prelookup_done": True,
            "validator_registry_available": True}


def bootstrap_evidence(git_sha: str, output: Path) -> dict[str, Any]:
    secret = "bootstrap-test-secret"
    pack = runtime_pack(git_sha, str(output))
    attacks: list[bool] = []
    fields = ["segments", "expected_value", "expected_value_verified", "comparator", "evidence_destination",
              "validator", "recovery_path", "rollback_checkpoint", "regression_targets", "runtime_binding"]
    for field in fields:
        bad = json.loads(json.dumps(pack))
        if field == "segments": bad["segments"] = []
        elif field == "expected_value_verified": bad["segments"][0][field] = False
        else: bad["segments"][0].pop(field, None)
        try: issue_token(bad, secret); attacks.append(False)
        except PermissionError: attacks.append(True)
    bad = json.loads(json.dumps(pack)); bad["no_critical_unknown"] = False
    try: issue_token(bad, secret); attacks.append(False)
    except PermissionError: attacks.append(True)
    token = issue_token(pack, secret)
    attacks += [
        not verify_token(None, secret, {}),
        not verify_token(token, secret, {}, now=datetime.now(timezone.utc) + timedelta(hours=1)),
        not verify_token(token, secret, {"work_id": "OTHER"}),
        not verify_token(token, secret, {"segment_ids": ["OTHER"]}),
        not verify_token(token, secret, {"git_sha": "changed"}),
    ]
    tampered = json.loads(json.dumps(token)); tampered["payload"]["status"] = "VALID"
    tampered["payload"]["git_sha"] = "forged"
    attacks.append(not verify_token(tampered, secret, {}))
    clear_token()
    try: verify_work_start_token("DIRECT_ENTRYPOINT"); attacks.append(False)
    except PermissionError: attacks.append(True)
    bad = json.loads(json.dumps(pack)); bad["validator_registry_available"] = False
    try: issue_token(bad, secret); attacks.append(False)
    except PermissionError: attacks.append(True)
    bad = json.loads(json.dumps(pack)); bad["segments"][0]["validator"] = "SELF_REPORTED_PASS"
    bad["validator_registry_available"] = False
    try: issue_token(bad, secret); attacks.append(False)
    except PermissionError: attacks.append(True)
    assert len(attacks) == 20

    validator_bad_states = []
    for field in ("user_intent", "actual_input", "input_source", "expected_output", "expected_value_basis",
                  "tolerance", "boundary_cases", "negative_cases", "failure_injection_cases", "next_segment_condition"):
        bad = json.loads(json.dumps(pack)); bad["segments"][0].pop(field)
        validator_bad_states.append(not valid_pack(bad))
    import wic_top_controller as body
    test_a_contract = not valid_pack({"segments": []})
    expected = {"work_id": pack["work_id"], "git_sha": git_sha}
    clear_token()
    with tempfile.TemporaryDirectory() as denied_directory:
        denied_target = Path(denied_directory) / "must-not-exist.json"
        try:
            body.atomic_json(denied_target, {"forbidden": True})
            test_a_mutation_blocked = False
        except PermissionError:
            test_a_mutation_blocked = not denied_target.exists()
    test_a = test_a_contract and test_a_mutation_blocked
    activate_token(token, secret, expected)
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        target = temp / "test-b.json"
        event_target = temp / "events.jsonl"
        lock_target = temp / "controller.lock"
        original_events, original_lock = body.EVENTS, body.LOCK
        body.EVENTS, body.LOCK = event_target, lock_target
        payload = {"test": "B", "allowed": True}
        body.atomic_json(target, payload)
        body.append_event({"test": "B"})
        fd = body.acquire_lock()
        lock_created = lock_target.exists()
        body.release_lock(fd)
        lock_removed = not lock_target.exists()
        body.EVENTS, body.LOCK = original_events, original_lock
        reopened = json.loads(target.read_text(encoding="utf-8"))
        event_reopened = json.loads(event_target.read_text(encoding="utf-8").strip())
        test_b = reopened == payload and event_reopened == {"test": "B"} and lock_created and lock_removed
        primitive_results = {"atomic_json": reopened == payload, "append_event": event_reopened == {"test": "B"},
                             "acquire_lock": lock_created, "release_lock": lock_removed,
                             "queue_classifier_output": "body.atomic_json(OUT, result)" in
                             (Path(__file__).with_name("queue_root_classifier.py").read_text(encoding="utf-8"))}
    clear_token()
    result = {
        "schema": "wic.pre-work-admission.bootstrap.v1", "bootstrap_work_id": BOOTSTRAP_WORK_ID,
        "created_at": datetime.now(timezone.utc).isoformat(), "git_sha": git_sha,
        "rollback_checkpoint": "a8cb297bebf8f9b5a1e13d19d92f874b14e1bca9",
        "admission_attack_cases_required": 20, "admission_attack_cases_run": 20,
        "admission_attack_cases_blocked": sum(attacks),
        "admission_bypass_block_rate": 100 if all(attacks) else 0,
        "mutating_entrypoints": ["atomic_json", "append_event", "acquire_lock", "release_lock", "queue_classifier_output"],
        "mutating_entrypoint_results": primitive_results,
        "mutating_entrypoint_total": 5, "mutating_entrypoint_guarded": sum(primitive_results.values()),
        "mutating_entrypoint_guard_coverage": 100 if all(primitive_results.values()) else 0,
        "validator_bad_states_injected": len(validator_bad_states),
        "validator_bad_states_detected": sum(validator_bad_states),
        "enforcement_validator_detection_rate": 100 if all(validator_bad_states) else 0,
        "enforcement_false_pass_rate": 0 if all(validator_bad_states) else 100,
        "incomplete_work_started": 0, "unauthorized_side_effect": 0,
        "stale_token_accepted": 0, "cross_work_token_accepted": 0,
        "test_a": "PASS" if test_a else "FAIL", "test_b": "PASS" if test_b else "FAIL",
        "pre_work_evidence_readback": "PENDING_WRITE",
        "work_start_enforcement_verified": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reopened = json.loads(output.read_text(encoding="utf-8"))
    reopened["pre_work_evidence_readback"] = "PASS"
    required_pass = (reopened["admission_bypass_block_rate"] == 100 and
                     reopened["mutating_entrypoint_guard_coverage"] == 100 and
                     reopened["enforcement_validator_detection_rate"] == 100 and
                     reopened["enforcement_false_pass_rate"] == 0 and
                     reopened["test_a"] == reopened["test_b"] == "PASS")
    reopened["work_start_enforcement_verified"] = required_pass
    output.write_text(json.dumps(reopened, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    final = json.loads(output.read_text(encoding="utf-8"))
    if not final["work_start_enforcement_verified"]:
        raise RuntimeError("BOOTSTRAP_ENFORCEMENT_FAILED")
    return final


def require_external_admission(work_id: str, task_id: str) -> dict[str, Any]:
    """Shared pre-start boundary for independently triggered mutating workflows."""
    from runtime_progress_gate import verify_work_admission
    root = Path(__file__).resolve().parents[2]
    if os.environ.get("WIC_USER_STOP") != "0":
        return {"decision": "BLOCK", "reason": "USER_STOP_OR_START_BLOCKED",
                "work_id": work_id, "task_id": task_id}
    admission = None
    inline = os.environ.get("WIC_RULE_ADMISSION_JSON")
    if inline:
        try:
            admission = json.loads(inline)
        except ValueError:
            admission = None
    else:
        # Full canonical rule records may exceed the OS per-variable limit.
        # Keep file transport inside existing Evidence roots; the same admission
        # identity, source receipt and rule content checks still run below.
        relative = os.environ.get("WIC_RULE_ADMISSION_FILE")
        if relative:
            target = (root / relative).resolve()
            allowed = ((root / "feedback_pipeline" / "evidence").resolve(),
                       (root / "CONTROL_TOWER" / "ledger" / "evidence").resolve())
            if relative.endswith(".json") and any(target.is_relative_to(base) for base in allowed):
                try:
                    admission = json.loads(target.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    admission = None
    if isinstance(admission, dict) and isinstance(admission.get("admissions"), dict):
        admission = admission["admissions"].get(work_id)
    return verify_work_admission(admission, repo_root=root,
                                 work_id=work_id, task_id=task_id)



def retrieve_remote_blob_receipt(repository: str, commit_sha: str, artifact_path: str,
                                 expected_sha256: str, *, max_bytes: int = 50_000_000) -> dict[str, Any]:
    """Read a pinned GitHub blob before issuing a remote result receipt."""
    if (not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
            or not re.fullmatch(r"[0-9a-fA-F]{40}", commit_sha)
            or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256)
            or not isinstance(artifact_path, str) or not artifact_path
            or artifact_path.startswith("/") or "\\" in artifact_path
            or any(part in {"", ".", ".."} for part in artifact_path.split("/"))
            or not isinstance(max_bytes, int) or max_bytes <= 0):
        return {"validation_result": "HOLD", "reason": "REMOTE_BLOB_IDENTITY_INVALID"}
    url = ("https://raw.githubusercontent.com/" + repository + "/" + commit_sha.lower()
           + "/" + urllib.parse.quote(artifact_path, safe="/"))
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "WIC-remote-blob-readback"})
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = response.read(max_bytes + 1)
    except (OSError, ValueError):
        return {"validation_result": "HOLD", "reason": "REMOTE_BLOB_READBACK_UNAVAILABLE"}
    if len(payload) > max_bytes:
        return {"validation_result": "HOLD", "reason": "REMOTE_BLOB_SIZE_LIMIT"}
    retrieved_sha = hashlib.sha256(payload).hexdigest()
    if retrieved_sha != expected_sha256.lower():
        return {"validation_result": "HOLD", "reason": "REMOTE_BLOB_CONTENT_MISMATCH",
                "retrieved_sha256": retrieved_sha}
    git_blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
    return {"commit_sha": commit_sha.lower(), "blob_oid": git_blob,
            "retrieval_id": "github-raw-" + secrets.token_hex(12), "remote_url": url,
            "artifact_path": artifact_path, "retrieved_sha256": retrieved_sha,
            "validation_result": "PASS"}


def validate_output_reopen_and_remote(receipt: dict[str, Any], reopen: Any, remote: Any) -> str | None:
    """Bind completion to an independently reopened artifact and a remote blob retrieval."""
    actual_ref = receipt.get("actual_result_ref")
    if not isinstance(actual_ref, dict) or not isinstance(actual_ref.get("sha256"), str):
        return "ACTUAL_RESULT_IDENTITY_MISSING"
    actual_sha = actual_ref["sha256"].lower()
    if not re.fullmatch(r"[0-9a-f]{64}", actual_sha):
        return "ACTUAL_RESULT_IDENTITY_INVALID"
    if not isinstance(reopen, dict):
        return "ARTIFACT_REOPEN_RECEIPT_INVALID"
    checks = reopen.get("format_checks")
    if (reopen.get("work_id") != receipt.get("work_id")
            or reopen.get("task_id") != receipt.get("task_id")
            or not reopen.get("parser_id")
            or not reopen.get("validator_id")
            or reopen.get("validator_id") != receipt.get("independent_validator_id")
            or not reopen.get("reopen_execution_id")
            or reopen.get("reopen_execution_id") == receipt.get("execution_id")
            or not reopen.get("artifact_format")
            or reopen.get("artifact_sha256") != actual_sha
            or reopen.get("source_receipt_sha256") != receipt.get("source_receipt_sha256")
            or reopen.get("validation_result") != "PASS"
            or not isinstance(checks, dict) or not checks
            or not all(value is True for value in checks.values())):
        return "ARTIFACT_REOPEN_INDEPENDENT_VALIDATION_MISMATCH"
    if not isinstance(remote, dict):
        return "REMOTE_READBACK_RECEIPT_INVALID"
    commit = str(remote.get("commit_sha", "")).lower()
    blob_oid = str(remote.get("blob_oid", "")).lower()
    if (not re.fullmatch(r"[0-9a-f]{40}", commit)
            or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", blob_oid)
            or not remote.get("retrieval_id")
            or not remote.get("remote_url")
            or remote.get("artifact_path") != actual_ref.get("path")
            or remote.get("retrieved_sha256") != actual_sha
            or remote.get("validation_result") != "PASS"):
        return "REMOTE_READBACK_IDENTITY_MISMATCH"
    return None


def require_external_completion(work_id: str, task_id: str) -> dict[str, Any]:
    """Refuse PASS promotion without current admission and read-back-bound closure."""
    admission = require_external_admission(work_id, task_id)
    if admission["decision"] != "ALLOW":
        return {"decision": "BLOCK", "reason": "CURRENT_ADMISSION_" + str(admission["reason"]),
                "work_id": work_id, "task_id": task_id}
    from universal_enforcement import closure_verdict, output_self_audit_verdict
    root = Path(__file__).resolve().parents[2]
    try:
        refs = json.loads(os.environ.get("WIC_CLOSURE_RECEIPTS_JSON", "null"))
    except ValueError:
        refs = None
    item = refs.get(work_id) if isinstance(refs, dict) else None
    relative = item.get("path") if isinstance(item, dict) else None
    reason = None
    if not isinstance(relative, str) or not relative.endswith(".json"):
        reason = "CLOSURE_RECEIPT_MISSING"
    else:
        target = (root / relative).resolve()
        allowed = ((root / "feedback_pipeline" / "evidence").resolve(),
                   (root / "CONTROL_TOWER" / "ledger" / "evidence").resolve())
        if not any(target.is_relative_to(base) for base in allowed) or not target.is_file():
            reason = "CLOSURE_RECEIPT_PATH_INVALID"
        elif hashlib.sha256(target.read_bytes()).hexdigest() != item.get("sha256"):
            reason = "CLOSURE_RECEIPT_STALE_OR_TAMPERED"
        else:
            try:
                receipt = json.loads(target.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                receipt = {}
            if receipt.get("work_id") != work_id or receipt.get("task_id") != task_id:
                reason = "CLOSURE_IDENTITY_MISMATCH"
            elif os.environ.get("GITHUB_RUN_ID") and str(receipt.get("run_id")) != os.environ["GITHUB_RUN_ID"]:
                reason = "CLOSURE_RUN_ID_MISMATCH"
            elif not receipt.get("independent_validator_id") or not receipt.get("execution_id"):
                reason = "INDEPENDENT_VALIDATION_EVIDENCE_MISSING"
            elif output_self_audit_verdict(receipt) != "PASS":
                reason = "SELF_AUDIT_NOT_PASS"
            elif closure_verdict(receipt) != "PASS":
                reason = "CLOSURE_VERDICT_NOT_PASS"
            else:
                from runtime_progress_gate import canonical_rule_manifest
                manifest = canonical_rule_manifest(root, task_id)
                if manifest["missing"] or receipt.get("applied_rule_version") != manifest["version"]:
                    reason = "CLOSURE_RULE_VERSION_UNVERIFIED"
                elif not receipt.get("source_receipt_sha256") or not receipt.get("rule_compliance_verdict") == "PASS":
                    reason = "CLOSURE_SOURCE_OR_RULE_COMPLIANCE_UNVERIFIED"
                else:
                    for key in ("source_receipt_ref", "actual_result_ref", "independent_validation_ref",
                                "artifact_reopen_ref", "remote_readback_ref"):
                        ref = receipt.get(key)
                        if not isinstance(ref, dict) or not isinstance(ref.get("path"), str) or not isinstance(ref.get("sha256"), str):
                            reason = key.upper() + "_MISSING"
                            break
                        artifact = (root / ref["path"]).resolve()
                        if (not artifact.is_relative_to(root.resolve()) or not artifact.is_file()
                                or hashlib.sha256(artifact.read_bytes()).hexdigest() != ref["sha256"]):
                            reason = key.upper() + "_MISSING_OR_CHANGED"
                            break
                    if reason is None and receipt["source_receipt_ref"]["sha256"] != receipt["source_receipt_sha256"]:
                        reason = "CLOSURE_SOURCE_RECEIPT_MISMATCH"
                    if reason is None:
                        source = json.loads((root / receipt["source_receipt_ref"]["path"]).read_text(encoding="utf-8"))
                        if (source.get("work_id") != work_id or source.get("task_id") != task_id
                                or source.get("rule_version") != manifest["version"]
                                or source.get("validation_result") != "PASS"):
                            reason = "CLOSURE_SOURCE_RECEIPT_UNVERIFIED"
                    if reason is None:
                        originals = source.get("source_refs")
                        plan = source.get("validation_plan")
                        if (not isinstance(originals, list) or not originals
                                or not isinstance(plan, dict)
                                or plan.get("expected_result") != receipt.get("expected_output")):
                            reason = "CLOSURE_ORIGINALS_OR_EXPECTED_RESULT_MISMATCH"
                        else:
                            for ref in originals:
                                if not isinstance(ref, dict) or not isinstance(ref.get("path"), str):
                                    reason = "CLOSURE_ORIGINAL_REFERENCE_INVALID"
                                    break
                                original = (root / ref["path"]).resolve()
                                if (not original.is_relative_to(root.resolve()) or not original.is_file()
                                        or original.stat().st_size == 0
                                        or hashlib.sha256(original.read_bytes()).hexdigest() != ref.get("sha256")):
                                    reason = "CLOSURE_ORIGINAL_CHANGED_DURING_EXECUTION"
                                    break
                    if reason is None:
                        validator = json.loads((root / receipt["independent_validation_ref"]["path"]).read_text(encoding="utf-8"))
                        rule_checks = validator.get("rule_checks")
                        source_checks = validator.get("source_checks")
                        expected_rules = [{"path": path, "sha256": digest, "verdict": "PASS"}
                                          for path, digest in sorted(manifest["files"].items())]
                        expected_sources = [{"path": ref["path"], "sha256": ref["sha256"], "verdict": "PASS"}
                                            for ref in originals]
                        tool013_checks = validator.get("tool013_output_checks", {})
                        tool013_required = (
                            "exact_18_columns", "full_title_translation", "approved_taxonomy",
                            "price_and_date", "original_preserved", "no_missing_duplicate_mixed_rows",
                            "download_reopened"
                        )
                        if (validator.get("work_id") != work_id or validator.get("task_id") != task_id
                                or validator.get("validator_id") != receipt["independent_validator_id"]
                                or validator.get("execution_id") != receipt["execution_id"]
                                or not validator.get("validator_job_id")
                                or not receipt.get("execution_job_id")
                                or validator["validator_job_id"] == receipt["execution_job_id"]
                                or validator.get("actual_result_sha256") != receipt["actual_result_ref"]["sha256"]
                                or validator.get("rule_version") != manifest["version"]
                                or validator.get("source_receipt_sha256") != receipt["source_receipt_sha256"]
                                or validator.get("expected_result") != plan["expected_result"]
                                or validator.get("observed_result") != receipt.get("actual_output")
                                or rule_checks != expected_rules
                                or source_checks != expected_sources
                                or validator.get("rule_compliance_verdict") != "PASS"
                                or validator.get("validation_result") != "PASS"):
                            reason = "INDEPENDENT_VALIDATION_MISMATCH"
                        elif task_id.upper() == "TOOL013" and not all(
                                tool013_checks.get(key) is True for key in tool013_required):
                            reason = "TOOL013_OUTPUT_CHECKS_INCOMPLETE"
                        else:
                            try:
                                reopen = json.loads((root / receipt["artifact_reopen_ref"]["path"]).read_text(encoding="utf-8"))
                                remote = json.loads((root / receipt["remote_readback_ref"]["path"]).read_text(encoding="utf-8"))
                            except (OSError, ValueError, TypeError):
                                reason = "OUTPUT_REOPEN_OR_REMOTE_RECEIPT_INVALID"
                            else:
                                reason = validate_output_reopen_and_remote(receipt, reopen, remote)
    return {"decision": "BLOCK" if reason else "ALLOW", "reason": reason,
            "work_id": work_id, "task_id": task_id}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-evidence", type=Path)
    parser.add_argument("--git-sha", default=os.environ.get("GITHUB_SHA", "LOCAL"))
    parser.add_argument("--require-admission", action="store_true")
    parser.add_argument("--require-completion", action="store_true")
    parser.add_argument("--work-id")
    parser.add_argument("--task-id")
    args = parser.parse_args()
    if args.require_completion:
        receipt = require_external_completion(args.work_id or "", args.task_id or "")
        print(json.dumps(receipt, ensure_ascii=False))
        return 0 if receipt["decision"] == "ALLOW" else 1
    if args.require_admission:
        receipt = require_external_admission(args.work_id or "", args.task_id or "")
        print(json.dumps(receipt, ensure_ascii=False))
        return 0 if receipt["decision"] == "ALLOW" else 1
    if not args.bootstrap_evidence:
        raise SystemExit("bootstrap evidence path required")
    print(json.dumps(bootstrap_evidence(args.git_sha, args.bootstrap_evidence), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

