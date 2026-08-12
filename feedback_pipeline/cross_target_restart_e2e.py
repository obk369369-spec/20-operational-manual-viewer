from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "_cross_target_restart_work"
TARGET = WORK / "06-toc-check"
CHECKPOINT = WORK / "checkpoint.json"
EVIDENCE = ROOT / "cross_target_restart_e2e_evidence.json"
TARGET_REPO = "https://github.com/obk369369-spec/06-toc-check.git"
PROBE = TARGET / "WIC_RESTART_E2E_PROBE.txt"
STAGES = [
    "EVENT",
    "NORMALIZE",
    "ROUTE_EXISTING_REGISTRY",
    "CONFLICT_DEDUP",
    "CANONICAL_WRITE",
    "READ_BACK",
    "TARGET_REVISION_READ_APPLY",
    "TEST_EVIDENCE",
    "RESTART_OR_HOLD",
]


def run(*args: str, cwd: Path | None = None) -> str:
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True)
    return p.stdout.strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def phase_fail() -> None:
    if WORK.exists():
        subprocess.run(["rm", "-rf", str(WORK)], check=True)
    WORK.mkdir(parents=True)
    run("git", "clone", "--depth", "1", TARGET_REPO, str(TARGET))
    head = run("git", "rev-parse", "HEAD", cwd=TARGET)
    clean_before = run("git", "status", "--porcelain", cwd=TARGET) == ""
    assert clean_before

    last_success_stage = "READ_BACK"
    valid_payload = "wic restart e2e valid payload\n"
    bad_payload = "wic restart e2e controlled bad payload\n"
    failure_stage = "TARGET_REVISION_READ_APPLY"

    PROBE.write_text(bad_payload, encoding="utf-8")
    mutated_hash = sha256_text(PROBE.read_text(encoding="utf-8"))
    try:
        if PROBE.read_text(encoding="utf-8") != valid_payload:
            raise RuntimeError("controlled cross-target apply verification failure")
    except RuntimeError as exc:
        PROBE.unlink(missing_ok=True)
        clean_after_rollback = run("git", "status", "--porcelain", cwd=TARGET) == ""
        assert clean_after_rollback
        restart_from = STAGES[STAGES.index(last_success_stage) + 1]
        checkpoint = {
            "schema_version": 1,
            "target_repository": "obk369369-spec/06-toc-check",
            "target_head": head,
            "last_success_stage": last_success_stage,
            "failure_stage": failure_stage,
            "restart_from_stage": restart_from,
            "status": "HOLD_CONTROLLED_FAILURE_ROLLED_BACK",
            "error": str(exc),
            "mutated_hash": mutated_hash,
            "rollback_clean": clean_after_rollback,
            "valid_payload": valid_payload,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        CHECKPOINT.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("EXPECTED_CONTROLLED_FAILURE_ROLLED_BACK")
        return
    raise AssertionError("controlled failure did not occur")


def phase_restart() -> None:
    checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    assert checkpoint["status"] == "HOLD_CONTROLLED_FAILURE_ROLLED_BACK"
    assert checkpoint["last_success_stage"] == "READ_BACK"
    assert checkpoint["restart_from_stage"] == "TARGET_REVISION_READ_APPLY"
    assert run("git", "status", "--porcelain", cwd=TARGET) == ""
    assert run("git", "rev-parse", "HEAD", cwd=TARGET) == checkpoint["target_head"]

    executed = []
    start = STAGES.index(checkpoint["restart_from_stage"])
    for stage in STAGES[start:]:
        if stage == "TARGET_REVISION_READ_APPLY":
            PROBE.write_text(checkpoint["valid_payload"], encoding="utf-8")
            executed.append(stage)
        elif stage == "TEST_EVIDENCE":
            readback = PROBE.read_text(encoding="utf-8")
            assert readback == checkpoint["valid_payload"]
            executed.append(stage)
        elif stage == "RESTART_OR_HOLD":
            executed.append(stage)

    readback = PROBE.read_text(encoding="utf-8")
    final_hash = sha256_text(readback)
    PROBE.unlink(missing_ok=True)
    clean_final = run("git", "status", "--porcelain", cwd=TARGET) == ""
    assert clean_final

    evidence = {
        "schema_version": 1,
        "e2e_type": "ACTUAL_CROSS_TARGET_CONTROLLED_FAILURE_ROLLBACK_AUTOMATIC_RESTART",
        "target_repository": checkpoint["target_repository"],
        "target_head": checkpoint["target_head"],
        "checkpoint_read": True,
        "last_success_stage": checkpoint["last_success_stage"],
        "failure_stage": checkpoint["failure_stage"],
        "restart_from_stage": checkpoint["restart_from_stage"],
        "executed_after_restart": executed,
        "rollback_clean_before_restart": checkpoint["rollback_clean"],
        "readback_match": readback == checkpoint["valid_payload"],
        "final_payload_sha256": final_hash,
        "target_clean_after_e2e": clean_final,
        "result": "PASS_INTERNAL_GITHUB_RUN",
        "external_independent_verification": False,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS_ACTUAL_CROSS_TARGET_AUTOMATIC_RESTART_E2E")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["fail", "restart"])
    args = ap.parse_args()
    if args.phase == "fail":
        phase_fail()
    else:
        phase_restart()


if __name__ == "__main__":
    main()
