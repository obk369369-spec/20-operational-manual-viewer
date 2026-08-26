"""Canonical single-source mutation/read-back contract for the WIC integration core.

The repository code owns deterministic canonical mutation, idempotency, and hash
verification. Authenticated GitHub transport is deliberately external (connector/Work)
so credentials never live in this module.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any, Iterable, Mapping

START_MARKER = "<!-- WIC_CANONICAL_FEEDBACK_START -->"
END_MARKER = "<!-- WIC_CANONICAL_FEEDBACK_END -->"
SECTION_RE = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.S)
RECORDS_END_RE = re.compile(r'(\n  \],\n  "schema_version": 1\n})')


def _stable_records(records: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for record in records:
        normalized.append({
            "feedback_id": str(record.get("feedback_id", "")),
            "root_cause_id": str(record.get("root_cause_id", record.get("feedback_id", ""))),
            "recur_count": max(1, int(record.get("recur_count", 1))),
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
    count = existing_text.count(START_MARKER)
    end_count = existing_text.count(END_MARKER)
    if count != end_count or count > 1:
        raise ValueError("canonical machine section must be absent or exactly one well-formed block")
    section = render_machine_section(records)
    if SECTION_RE.search(existing_text):
        return SECTION_RE.sub(section, existing_text, count=1)
    suffix = "" if existing_text.endswith("\n") else "\n"
    return f"{existing_text}{suffix}\n{section}\n"


def append_machine_record(existing_text: str, record: Mapping[str, Any]) -> str:
    """Insert one record without rewriting, sorting, or reformatting existing bytes."""
    if existing_text.count(START_MARKER) != 1 or existing_text.count(END_MARKER) != 1:
        raise ValueError("canonical machine section must exist exactly once")
    section_match = SECTION_RE.search(existing_text)
    if not section_match:
        raise ValueError("canonical machine section missing")
    section = section_match.group(0)
    insertion = RECORDS_END_RE.search(section)
    if not insertion:
        raise ValueError("canonical records array terminator missing")
    rendered = json.dumps(dict(record), ensure_ascii=False, indent=2, sort_keys=True)
    indented = "\n".join("    " + line for line in rendered.splitlines())
    updated_section = section[:insertion.start()] + ",\n" + indented + section[insertion.start():]
    return existing_text[:section_match.start()] + updated_section + existing_text[section_match.end():]


def content_hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _human_owned_text(text: str) -> str:
    return SECTION_RE.sub("", text, count=1)


def record_hashes(records: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for record in records:
        feedback_id = str(record.get("feedback_id", ""))
        if not feedback_id or feedback_id in result:
            raise ValueError("canonical feedback_id must be non-empty and unique")
        payload = json.dumps(dict(record), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        result[feedback_id] = content_hash(payload)
    return result


def verify_non_destructive_update(
    before_text: str,
    before_records: list[Mapping[str, Any]],
    after_text: str,
    after_records: list[Mapping[str, Any]],
    *,
    allowed_changed_ids: Iterable[str] = (),
    expected_new_ids: Iterable[str] = (),
    expected_after_text: str | None = None,
) -> dict[str, Any]:
    """Reject whole-file rewrites and any unapproved canonical record mutation."""
    before_hashes = record_hashes(before_records)
    after_hashes = record_hashes(after_records)
    allowed = set(allowed_changed_ids)
    expected_new = set(expected_new_ids)
    lost = sorted(set(before_hashes) - set(after_hashes))
    changed = sorted(
        feedback_id for feedback_id in set(before_hashes) & set(after_hashes)
        if before_hashes[feedback_id] != after_hashes[feedback_id] and feedback_id not in allowed
    )
    actual_new = set(after_hashes) - set(before_hashes)
    unexpected_new = sorted(actual_new - expected_new)
    missing_new = sorted(expected_new - actual_new)
    human_preserved = content_hash(_human_owned_text(before_text)) == content_hash(_human_owned_text(after_text))
    diff_only_match = expected_after_text is None or after_text == expected_after_text
    verified = not lost and not changed and not unexpected_new and not missing_new and human_preserved and diff_only_match
    return {
        "verified": verified,
        "human_owned_preserved": human_preserved,
        "lost_record_ids": lost,
        "unintentionally_changed_record_ids": changed,
        "unexpected_new_record_ids": unexpected_new,
        "missing_expected_record_ids": missing_new,
        "diff_only_match": diff_only_match,
    }


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
    before = upsert_machine_section(base, [r1])
    new_record = {**r1, "feedback_id": "fixture-new", "sanitized_excerpt": "permanent rule only"}
    after = append_machine_record(before, new_record)
    gate = verify_non_destructive_update(
        before, [r1], after, [r1, new_record], expected_new_ids={"fixture-new"}, expected_after_text=after
    )
    assert gate["verified"] is True
    assert gate["lost_record_ids"] == []
    assert gate["unintentionally_changed_record_ids"] == []
    assert verify_read_back(after, after)["verified"] is True
    return "PASS: one CENTRAL_MASTER_DESTRUCTIVE_UPDATE fixture"


if __name__ == "__main__":
    print(run_fixtures())
