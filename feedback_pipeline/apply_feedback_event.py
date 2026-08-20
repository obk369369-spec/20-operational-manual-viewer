"""Apply one WIC feedback event to the canonical master with restart/evidence state.

This runner reuses cross_chat_feedback_ingest.py and canonical_writer.py.  It is
intended to run inside GitHub Actions after checkout.  The workflow provides the
repository transport (checkout + commit + push); this module never stores tokens.

PASS boundary: this runner can prove EVENT through canonical READ_BACK inside the
checked-out repository.  Cross-repository target application is emitted as an
explicit manifest and remains HOLD until a target repository is actually updated,
read back, and tested.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from canonical_writer import (
    START_MARKER,
    END_MARKER,
    SECTION_RE,
    append_machine_record,
    upsert_machine_section,
    verify_non_destructive_update,
    verify_read_back,
)
from cross_chat_feedback_ingest import (
    FeedbackEvent,
    checkpoint_state,
    canonical_revision,
    decide_conflict,
    normalize,
    target_apply_decision,
)

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "WIC_GLOBAL_OPERATING_RULES.md"
STATE = ROOT / "feedback_pipeline" / "state.json"
EVENT = ROOT / "feedback_pipeline" / "pending_event.json"
MANIFEST = ROOT / "feedback_pipeline" / "target_apply_manifest.json"
EVIDENCE_DIR = ROOT / "feedback_pipeline" / "evidence"
JSON_BLOCK_RE = re.compile(
    re.escape(START_MARKER) + r"\s*```json\s*(.*?)\s*```\s*" + re.escape(END_MARKER),
    re.S,
)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_canonical_records(master_text: str) -> list[dict[str, Any]]:
    match = JSON_BLOCK_RE.search(master_text)
    if not match:
        return []
    payload = json.loads(match.group(1))
    if int(payload.get("schema_version", 0)) != 1:
        raise ValueError("unsupported canonical machine-section schema")
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise ValueError("canonical records must be a list")
    return [dict(x) for x in records]


def main() -> int:
    if not (ROOT / ".git").exists():
        print("중앙마스터 반영 실패 / 원인: 저장소 접근 불가 / 코드: REPOSITORY_ACCESS_HOLD / 업무 규칙 반영 미완료")
        return 2
    if not MASTER.is_file():
        print("중앙마스터 반영 실패 / 원인: 중앙마스터 위치 확인 불가 / 코드: CENTRAL_MASTER_NOT_FOUND_HOLD / 업무 규칙 반영 미완료")
        return 2
    event_raw = load_json(EVENT, None)
    if not isinstance(event_raw, dict):
        raise SystemExit("pending_event.json missing or invalid")
    for key in ("observed_at", "source_chat", "text"):
        if not str(event_raw.get(key, "")).strip():
            raise SystemExit(f"pending event missing required field: {key}")

    event = FeedbackEvent(
        observed_at=str(event_raw["observed_at"]),
        source_chat=str(event_raw["source_chat"]),
        text=str(event_raw["text"]),
        source_ref=str(event_raw.get("source_ref", "")),
    )
    item = normalize(event)
    state = load_json(STATE, {})
    integration = dict(state.get("integration_core", {}))
    core_state = {"feedback_checkpoints": integration.get("feedback_checkpoints", {})}

    # Idempotency before any mutation.
    if item.feedback_id in set(state.get("processed_feedback_ids", [])):
        print(json.dumps({"feedback_id": item.feedback_id, "result": "SKIP_ALREADY_PROCESSED"}))
        return 0

    master_before = MASTER.read_text(encoding="utf-8")
    records = read_canonical_records(master_before)

    if not item.central_master_candidate:
        print(json.dumps({"feedback_id": item.feedback_id, "result": "SKIP_ONE_TIME_CONTENT"}))
        return 0
    decision = decide_conflict(item, records)

    for stage in ("EVENT", "NORMALIZE", "ROUTE_EXISTING_REGISTRY", "CONFLICT_DEDUP"):
        core_state = checkpoint_state(core_state, feedback_id=item.feedback_id, stage=stage)

    evidence: dict[str, Any] = {
        "schema_version": 1,
        "feedback_id": item.feedback_id,
        "observed_at": item.observed_at,
        "source_chat": item.source_chat,
        "source_ref": item.source_ref,
        "classification": item.classification,
        "targets": list(item.targets),
        "sanitized_excerpt": item.sanitized_excerpt,
        "decision": asdict(decision),
        "runner": "feedback_pipeline/apply_feedback_event.py",
        "external_independent_verification": False,
    }

    if decision.action == "HOLD_CONFLICT":
        core_state = checkpoint_state(
            core_state,
            feedback_id=item.feedback_id,
            stage="CONFLICT_DEDUP",
            status="HOLD",
            blocker=decision.reason,
        )
        holds = list(integration.get("holds", []))
        holds.append({"feedback_id": item.feedback_id, "stage": "CONFLICT_DEDUP", "reason": decision.reason})
        integration["holds"] = holds[-200:]
        integration["feedback_checkpoints"] = core_state["feedback_checkpoints"]
        state["integration_core"] = integration
        write_json(STATE, state)
        evidence["result"] = "HOLD_CONFLICT"
        write_json(EVIDENCE_DIR / f"{item.feedback_id}.json", evidence)
        print(json.dumps({"feedback_id": item.feedback_id, "result": "HOLD_CONFLICT"}))
        return 0

    if decision.action == "DUPLICATE":
        evidence["result"] = "DUPLICATE"
        write_json(EVIDENCE_DIR / f"{item.feedback_id}.json", evidence)
        print(json.dumps({"feedback_id": item.feedback_id, "result": "DUPLICATE"}))
        return 0

    superseded = set(decision.supersedes)
    if superseded:
        for record in records:
            if str(record.get("feedback_id", "")) in superseded:
                record["active"] = False

    records.append({
        "feedback_id": item.feedback_id,
        "classification": item.classification,
        "targets": list(item.targets),
        "sanitized_excerpt": item.sanitized_excerpt,
        "active": True,
        "supersedes": list(decision.supersedes),
        "impacted_layers": list(decision.impacted_layers),
    })

    new_record = records[-1]
    master_after = append_machine_record(master_before, new_record)
    MASTER.write_text(master_after, encoding="utf-8")

    preservation = verify_non_destructive_update(
        master_before,
        read_canonical_records(master_before),
        master_after,
        read_canonical_records(master_after),
        allowed_changed_ids=superseded,
        expected_new_ids={item.feedback_id},
        expected_after_text=append_machine_record(master_before, new_record),
    )
    evidence["central_master_destructive_update_gate"] = preservation
    if not preservation["verified"]:
        MASTER.write_text(master_before, encoding="utf-8")
        evidence["result"] = "FAIL_CENTRAL_MASTER_DESTRUCTIVE_UPDATE_ROLLED_BACK"
        write_json(EVIDENCE_DIR / f"{item.feedback_id}.json", evidence)
        raise SystemExit("CENTRAL_MASTER_DESTRUCTIVE_UPDATE: rollback complete")
    core_state = checkpoint_state(core_state, feedback_id=item.feedback_id, stage="CANONICAL_WRITE")

    # Immediate local read-back verifies the bytes that the workflow will commit.
    read_back = MASTER.read_text(encoding="utf-8")
    verification = verify_read_back(master_after, read_back)
    if not verification["verified"]:
        core_state = checkpoint_state(
            core_state,
            feedback_id=item.feedback_id,
            stage="READ_BACK",
            status="FAIL",
            blocker="canonical local read-back hash mismatch",
        )
        integration["feedback_checkpoints"] = core_state["feedback_checkpoints"]
        state["integration_core"] = integration
        write_json(STATE, state)
        evidence.update({"result": "FAIL_READ_BACK", "read_back": verification})
        write_json(EVIDENCE_DIR / f"{item.feedback_id}.json", evidence)
        raise SystemExit("canonical read-back hash mismatch")
    core_state = checkpoint_state(core_state, feedback_id=item.feedback_id, stage="READ_BACK")

    revision = canonical_revision(records)
    cache = dict(integration.get("target_revision_cache", {}))
    target_plan: dict[str, Any] = {}
    for target in decision.impacted_targets:
        target_plan[target] = {
            "decision": target_apply_decision(target, revision, cache),
            "canonical_revision": revision,
            "status": "HOLD_TARGET_APPLY",
            "reason": "cross-repository target write/read-back/test has not executed yet",
        }

    # The runner deliberately does not mark target revisions as applied before the
    # target repository has real write/read-back/test evidence.
    manifest = {
        "schema_version": 1,
        "feedback_id": item.feedback_id,
        "canonical_revision": revision,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "targets": target_plan,
    }
    write_json(MANIFEST, manifest)

    core_state = checkpoint_state(
        core_state,
        feedback_id=item.feedback_id,
        stage="TARGET_REVISION_READ_APPLY",
        status="HOLD",
        blocker="canonical GitHub commit/read-back must complete, then target repository apply/read-back/test is required",
    )
    integration["feedback_checkpoints"] = core_state["feedback_checkpoints"]
    integration["target_revision_cache"] = cache
    integration["structure_pass"] = False
    integration["structure_pass_reason"] = (
        "Canonical mutation/read-back prepared; cross-repository target apply/test evidence remains HOLD."
    )
    state["integration_core"] = integration
    ids = list(dict.fromkeys([*state.get("processed_feedback_ids", []), item.feedback_id]))
    state["processed_feedback_ids"] = ids[-2000:]
    state["last_context_cursor"] = item.observed_at
    write_json(STATE, state)

    evidence.update({
        "result": "CANONICAL_PREPARED_TARGET_HOLD",
        "canonical_revision": revision,
        "read_back": verification,
        "target_manifest": str(MANIFEST.relative_to(ROOT)),
        "restart_point": "verify workflow commit/read-back, then apply target manifest to actual target repos and run target tests",
    })
    write_json(EVIDENCE_DIR / f"{item.feedback_id}.json", evidence)
    print(json.dumps({
        "feedback_id": item.feedback_id,
        "result": evidence["result"],
        "canonical_revision": revision,
        "targets": list(target_plan),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
