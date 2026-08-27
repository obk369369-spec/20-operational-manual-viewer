"""Fail-closed verifier for one actual Android screen-off observer run."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

REQUIRED = (
    "device_id", "run_id", "started_at", "screen_off_at", "background_task_at",
    "persistent_state_at", "screen_on_at", "state_restored_at", "state_before_sha256",
    "state_after_sha256", "observer_readback_sha256", "github_commit", "github_actions_run",
)


def _time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def verify(row: dict) -> dict:
    missing = [key for key in REQUIRED if not str(row.get(key, "")).strip()]
    errors: list[str] = []
    if missing:
        errors.append("MISSING:" + ",".join(missing))
    try:
        times = [_time(row[key]) for key in REQUIRED[2:8]]
        if times != sorted(times): errors.append("EVENT_ORDER_INVALID")
        if (times[4] - times[1]).total_seconds() < 60: errors.append("SCREEN_OFF_DURATION_LT_60_SECONDS")
    except (KeyError, TypeError, ValueError):
        errors.append("TIMESTAMP_INVALID")
    if row.get("screen_off_confirmed") is not True: errors.append("SCREEN_OFF_NOT_CONFIRMED")
    if row.get("background_task_without_user_input") is not True: errors.append("BACKGROUND_USER_INPUT_REQUIRED")
    if row.get("state_before_sha256") == row.get("state_after_sha256"): errors.append("STATE_DID_NOT_CHANGE")
    if row.get("observer_readback_sha256") != row.get("state_after_sha256"): errors.append("STATE_RESTORE_MISMATCH")
    if len(str(row.get("github_commit", ""))) != 40: errors.append("REMOTE_COMMIT_INVALID")
    return {"status":"PASS" if not errors else "HOLD_ACTUAL_DEVICE_EVIDENCE","actual_android_verified":not errors,"errors":errors,"evidence_sha256":hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()}


def self_test() -> None:
    valid = {"device_id":"fixture-device","run_id":"fixture-only","started_at":"2026-08-27T00:00:00Z","screen_off_at":"2026-08-27T00:00:05Z","background_task_at":"2026-08-27T00:00:40Z","persistent_state_at":"2026-08-27T00:01:20Z","screen_on_at":"2026-08-27T00:01:30Z","state_restored_at":"2026-08-27T00:01:35Z","state_before_sha256":"a"*64,"state_after_sha256":"b"*64,"observer_readback_sha256":"b"*64,"github_commit":"c"*40,"github_actions_run":"fixture","screen_off_confirmed":True,"background_task_without_user_input":True}
    assert verify(valid)["status"] == "PASS"
    invalid = dict(valid, screen_off_confirmed=False, observer_readback_sha256="a"*64)
    assert verify(invalid)["status"] == "HOLD_ACTUAL_DEVICE_EVIDENCE"
    print("PASS: Android evidence contract fixtures (not actual-device PASS)")


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("evidence",nargs="?"); parser.add_argument("--self-test",action="store_true"); args=parser.parse_args()
    if args.self_test: self_test(); return
    if not args.evidence: raise SystemExit("evidence JSON required")
    result=verify(json.loads(Path(args.evidence).read_text(encoding="utf-8"))); print(json.dumps(result,ensure_ascii=False))
    if result["status"] != "PASS": raise SystemExit(1)


if __name__ == "__main__": main()
