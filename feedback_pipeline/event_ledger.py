"""Append-only durable ingress ledger for actual WIC feedback occurrences."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "occurrence_ledger.jsonl"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_occurrence(event: Mapping[str, Any]) -> dict[str, Any]:
    source_chat = str(event.get("source_chat_identity") or event.get("source_chat") or "").strip()
    tool_id = str(event.get("tool_id") or "").strip()
    source_ref = str(event.get("source_ref") or "").strip()
    feedback = str(event.get("feedback") or event.get("user_correction") or event.get("handoff_directive") or "").strip()
    wrong_ref = str(event.get("wrong_output_ref") or "").strip()
    if not source_chat or not source_ref or not feedback:
        raise ValueError("source chat identity, source_ref, and feedback are required")
    occurrence_material = "\0".join((source_chat, tool_id, source_ref, _hash(feedback), wrong_ref))
    occurrence_id = hashlib.sha256(occurrence_material.encode("utf-8")).hexdigest()[:32]
    root_material = "\0".join((tool_id or source_chat, str(event.get("root_cause_id") or ""), _hash(feedback)))
    return {
        "schema_version": 1,
        "occurrence_id": occurrence_id,
        "idempotency_key": occurrence_id,
        "root_hint": hashlib.sha256(root_material.encode("utf-8")).hexdigest()[:20],
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "event_kind": str(event.get("event_kind") or "ACTUAL_USER_FEEDBACK"),
        "source_chat_identity": source_chat,
        "tool_id": tool_id,
        "source_ref": source_ref,
        "directive_sha256": _hash(feedback),
        "wrong_output_ref": wrong_ref,
        "evidence_refs": list(event.get("evidence_refs") or []),
        "checkpoint_ref": str(event.get("checkpoint_ref") or ""),
        "next_start": str(event.get("next_start") or ""),
        "stage": "CAPTURED",
    }


def append_occurrence(event: Mapping[str, Any], ledger: Path = LEDGER) -> dict[str, Any]:
    row = build_occurrence(event)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    existing_ids: set[str] = set()
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing_ids.add(str(json.loads(line)["occurrence_id"]))
    if row["occurrence_id"] in existing_ids:
        return {**row, "append_status": "IDEMPOTENT_REPLAY"}
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
    fd = os.open(ledger, os.O_APPEND | os.O_CREAT | os.O_WRONLY)
    try:
        os.write(fd, payload.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    return {**row, "append_status": "APPENDED"}


def read_ledger(ledger: Path = LEDGER) -> list[dict[str, Any]]:
    if not ledger.exists():
        return []
    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [row["occurrence_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("occurrence ledger contains duplicate IDs")
    return rows
