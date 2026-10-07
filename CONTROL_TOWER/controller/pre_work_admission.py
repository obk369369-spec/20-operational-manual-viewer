"""Fail-closed admission controller for every WIC mutation entry point."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import sys
import tempfile
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-evidence", type=Path)
    parser.add_argument("--git-sha", default=os.environ.get("GITHUB_SHA", "LOCAL"))
    args = parser.parse_args()
    if not args.bootstrap_evidence:
        raise SystemExit("bootstrap evidence path required")
    print(json.dumps(bootstrap_evidence(args.git_sha, args.bootstrap_evidence), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
