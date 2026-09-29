import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tool044_unattended_evidence import update_history


def row(run, at, event="schedule", status="PASS"):
    return {"run_id": run, "generated_at_utc": at.isoformat(), "event": event,
            "minimum_circulation": status, "production_mutation": 0,
            "external_runtime": "GITHUB_ACTIONS"}


def test_waiting_then_pass_and_deduplicates(tmp_path: Path):
    history = tmp_path / "history.jsonl"; start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert update_history(history, row("first", start))["status"] == "WAITING"
    for index in range(1, 145):
        verdict = update_history(history, row(str(index), start + timedelta(minutes=10 * index)))
    assert verdict["status"] == "PASS" and verdict["span_hours"] == 24
    before = len(history.read_text(encoding="utf-8").splitlines())
    update_history(history, row("144", start + timedelta(hours=24)))
    assert len(history.read_text(encoding="utf-8").splitlines()) == before


def test_failure_or_large_gap_never_passes(tmp_path: Path):
    history = tmp_path / "history.jsonl"; start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    update_history(history, row("a", start))
    assert update_history(history, row("b", start + timedelta(hours=24, minutes=1)))["status"] == "WAITING"
    broken = tmp_path / "broken.jsonl"
    update_history(broken, row("a", start, status="HOLD"))
    assert update_history(broken, row("b", start + timedelta(hours=24)))["status"] == "WAITING"


def test_legacy_timestamp_record_does_not_stop_evidence_collection(tmp_path: Path):
    history = tmp_path / "history.jsonl"
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    legacy = {"run_id": "legacy", "timestamp": start.isoformat(), "event": "push"}
    history.write_text(json.dumps(legacy) + "\n", encoding="utf-8")

    verdict = update_history(history, row("scheduled", start + timedelta(minutes=5)))

    assert verdict["status"] == "WAITING"
    assert verdict["scheduled_records"] == 1
