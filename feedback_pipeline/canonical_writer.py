"""Canonical single-source mutation/read-back contract for the WIC integration core.

The repository code owns deterministic canonical mutation, idempotency, and hash
verification. Authenticated GitHub transport is deliberately external (connector/Work)
so credentials never live in this module.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any, Mapping

START_MARKER = "<!-- WIC_CANONICAL_FEEDBACK_START -->"
END_MARKER = "<!-- WIC_CANONICAL_FEEDBACK_END -->"
SECTION_RE = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.S)


def _stable_records(records: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for record in records:
        normalized.append({
            "feedback_id": str(record.get("feedback_id", "")),
            "classification": str(record.get("classification", "")),
            "targets": sorted(str(x) for x in (record.get("targets") or [])),
            "sanitized_excerpt": " ".join(str(record.get("sanitized_excerpt", "")).split()),
            "active": bool(record.get("active", True)),
            "supersedes": sorted(str(x) for x in (record.get("supersedes") or [])),
            "impacted_layers": list(dict.fromkeys(str(x) for x in (record.get("impacted_layers") or []))),
        })
    return sorted(normalized, key=lambda x: x["feedback_id"])


def render_machine_section(records: list[Mapping[str, Any]]) -> str:
    payload = json.dumps(
        {"schema_version": 1, "records": _stable_records(records)},
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    return f"{START_MARKER}\n```json\n{payload}\n```\n{END_MARKER}"


def upsert_machine_section(existing_text: str, records: list[Mapping[str, Any]]) -> str:
    """Replace only one machine-managed section and preserve all human-owned rules."""
    section = render_machine_section(records)
    if SECTION_RE.search(existing_text):
        return SECTION_RE.sub(section, existing_text, count=1)
    suffix = "" if existing_text.endswith("\n") else "\n"
    return f"{existing_text}{suffix}\n{section}\n"


def content_hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def verify_read_back(intended_text: str, read_back_text: str) -> dict[str, Any]:
    intended_hash = content_hash(intended_text)
    read_back_hash = content_hash(read_back_text)
    return {
        "intended_hash": intended_hash,
        "read_back_hash": read_back_hash,
        "verified": intended_hash == read_back_hash,
    }


def run_fixtures() -> str:
    base = "# WIC GLOBAL\n\nHuman-owned rule stays unchanged.\n"
    r1 = {
        "feedback_id": "abc123",
        "classification": "CONSTRAINT",
        "targets": ["TOOL013", "CENTRAL"],
        "sanitized_excerpt": "  do   not overwrite  ",
        "active": True,
        "impacted_layers": ["GLOBAL", "TOOL_OR_DOMAIN_OVERRIDE"],
    }
    first = upsert_machine_section(base, [r1])
    assert "Human-owned rule stays unchanged." in first
    assert first.count(START_MARKER) == 1 and first.count(END_MARKER) == 1
    second = upsert_machine_section(first, [r1])
    assert second == first, "canonical write must be idempotent"
    assert verify_read_back(first, second)["verified"] is True

    r2 = {**r1, "active": False, "supersedes": ["old001"]}
    third = upsert_machine_section(first, [r2])
    assert third != first
    assert third.count(START_MARKER) == 1
    assert verify_read_back(third, upsert_machine_section(third, [r2]))["verified"] is True
    return "PASS: canonical preserve + replace + idempotency + read-back hash fixtures"


if __name__ == "__main__":
    print(run_fixtures())
