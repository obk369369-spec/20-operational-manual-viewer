"""Measured cycle audit and fail-closed requirement reconciliation."""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".next")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(pending, path)


def atomic_demands(text: str) -> list[dict]:
    """Split durable instructions without pretending to understand inaccessible chats."""
    rows, seen = [], set()
    for raw in text.splitlines():
        line = re.sub(r"^[#>*\s-]+", "", raw).strip()
        line = re.sub(r"^\d+[.)]\s*", "", line)
        if len(line) < 8 or line.endswith(":"):
            continue
        key = re.sub(r"\s+", " ", line).casefold()
        if key in seen:
            continue
        seen.add(key)
        rows.append({"atomic_id": f"REQ-{len(rows)+1:03d}", "requirement": line})
    return rows


def reconcile(requirements: list[dict], outcomes: dict[str, dict]) -> dict:
    classified, missing = [], []
    for row in requirements:
        outcome = outcomes.get(row["atomic_id"])
        if not outcome:
            missing.append(row["atomic_id"])
            classified.append({**row, "status": "UNFINISHED", "evidence": None})
            continue
        status = outcome.get("status", "UNFINISHED")
        evidence = outcome.get("evidence")
        if status == "COMPLETE" and not evidence:
            status = "UNFINISHED"
            missing.append(row["atomic_id"])
        classified.append({**row, "status": status, "evidence": evidence})
    return {
        "source_requirement_count": len(requirements),
        "classified_requirement_count": len(classified),
        "unclassified_count": len(missing),
        "missing_requirement_ids": missing,
        "closeout_pass": not missing,
        "auto_requeue": missing,
        "items": classified,
    }


class Timeline:
    def __init__(self) -> None:
        self.started = time.perf_counter()
        self.last = self.started
        self.stages: list[dict] = []

    def mark(self, name: str) -> None:
        now = time.perf_counter()
        self.stages.append({"stage": name, "duration_seconds": round(now - self.last, 6)})
        self.last = now

    def result(self) -> dict:
        bottleneck = max(self.stages, key=lambda row: row["duration_seconds"], default=None)
        return {
            "measured_at": datetime.now(timezone.utc).isoformat(),
            "total_seconds": round(time.perf_counter() - self.started, 6),
            "stages": self.stages,
            "measured_bottleneck": bottleneck,
        }


def parallel_overlap(jobs: list[dict]) -> dict:
    intervals = []
    for job in jobs:
        start, end = job.get("started_at"), job.get("completed_at")
        if start and end:
            intervals.append((datetime.fromisoformat(start.replace("Z", "+00:00")),
                              datetime.fromisoformat(end.replace("Z", "+00:00")), job.get("name")))
    overlaps = []
    for index, left in enumerate(intervals):
        for right in intervals[index + 1:]:
            if max(left[0], right[0]) < min(left[1], right[1]):
                overlaps.append([left[2], right[2]])
    return {"jobs_with_timestamps": len(intervals), "overlap_pairs": overlaps,
            "actual_parallel_count": 2 if overlaps else min(1, len(intervals)),
            "parallel_proven": bool(overlaps)}

