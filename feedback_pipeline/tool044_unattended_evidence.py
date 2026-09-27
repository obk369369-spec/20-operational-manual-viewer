"""Conservative scheduled-run history and 24-hour unattended verdict."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def _time(row: dict) -> datetime:
    return datetime.fromisoformat(row["generated_at_utc"].replace("Z", "+00:00"))


def update_history(path: Path, record: dict, max_gap_minutes: int = 20) -> dict:
    rows = []
    if path.exists():
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(str(row.get("run_id")) == str(record.get("run_id")) for row in rows):
        rows.append(record)
    rows.sort(key=_time)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")

    scheduled = [row for row in rows if row.get("event") == "schedule"]
    good = [row for row in scheduled if row.get("minimum_circulation") == "PASS"
            and row.get("production_mutation") == 0 and row.get("external_runtime") == "GITHUB_ACTIONS"]
    span_hours = (_time(good[-1]) - _time(good[0])).total_seconds() / 3600 if len(good) > 1 else 0
    gaps = [(_time(right) - _time(left)).total_seconds() / 60 for left, right in zip(good, good[1:])]
    max_gap = max(gaps, default=0)
    passed = len(good) == len(scheduled) and len(good) > 1 and span_hours >= 24 and max_gap <= max_gap_minutes
    return {
        "status": "PASS" if passed else "WAITING",
        "scheduled_records": len(scheduled), "passing_records": len(good),
        "span_hours": round(span_hours, 3), "max_gap_minutes": round(max_gap, 3),
        "automatic_resume_condition": "24H_SCHEDULE_SPAN_WITHOUT_FAILED_OR_OVERDUE_INTERVAL",
        "pc_off_logged_off": "HOLD_EXTERNAL_EVIDENCE_UNTIL_24H_VERDICT",
    }
