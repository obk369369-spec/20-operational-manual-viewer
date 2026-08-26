"""WIC cross-chat feedback ingestion and deterministic integration-core contract.

The core is deliberately conservative: a generic CENTRAL route is not sufficient
proof that two rules describe the same scope.  Tool/domain corrections may replace
older rules only when they share a specific non-CENTRAL target.  This prevents an
unrelated global correction from silently disabling normal operating rules.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

CLASSIFICATIONS = (
    "CORRECTION",
    "CONSTRAINT",
    "NEW_FIXTURE",
    "PRIORITY_CHANGE",
    "SIDE_REQUEST",
)
DECISION_ACTIONS = (
    "ACCEPT",
    "DUPLICATE",
    "SUPERSEDE",
    "HOLD_CONFLICT",
)
STAGE_ORDER = (
    "EVENT",
    "NORMALIZE",
    "ROUTE_EXISTING_REGISTRY",
    "CONFLICT_DEDUP",
    "CANONICAL_WRITE",
    "READ_BACK",
    "TARGET_REVISION_READ_APPLY",
    "TEST_EVIDENCE",
    "RESTART_OR_HOLD",
)
MODULE_CONTRACT_KEYS = (
    "input_schema",
    "output_schema",
    "validate",
    "apply",
    "rollback",
    "fixture",
    "evidence",
)

REGISTRY_PATH = Path(__file__).resolve().parents[1] / "WIC_CHAT_ROUTING_REGISTRY.md"
UNREGISTERED_ROUTE = "UNREGISTERED_ROUTE"
ROUTE_LINE_RE = re.compile(r"^route:\s*([A-Z0-9_]+)\s*=\s*(.+?)\s*$", re.I)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?82[- .]?)?(?:0\d{1,2}[- .]?)?\d{3,4}[- .]?\d{4}(?!\d)")
LONG_NUMBER_RE = re.compile(r"(?<!\d)\d{7,}(?!\d)")
WS_RE = re.compile(r"\s+")
CLAUSE_RE = re.compile(r"(?<=[.!?。])\s+|[\r\n]+")
PERMANENT_MARKERS = (
    "정정", "잘못", "틀렸", "오류", "누락", "형식", "변경", "금지", "운영", "반복", "앞으로",
    "항상", "반드시", "규칙", "기준", "고정", "하지 마", "하지마", "하지 말", "하지말",
)
TRANSIENT_MARKERS = ("현재 상태", "크레딧", "오늘 날짜", "지금 날짜", "몇 시", "조회해", "알려줘")


@dataclass(frozen=True)
class FeedbackEvent:
    observed_at: str
    source_chat: str
    text: str
    source_ref: str = ""


@dataclass(frozen=True)
class NormalizedFeedback:
    feedback_id: str
    observed_at: str
    source_chat: str
    source_ref: str
    classification: str
    targets: tuple[str, ...]
    sanitized_excerpt: str
    central_master_candidate: bool
    regression_fixture_candidate: bool
    priority_change: bool


@dataclass(frozen=True)
class ConflictDecision:
    feedback_id: str
    action: str
    reason: str
    supersedes: tuple[str, ...]
    conflicts_with: tuple[str, ...]
    impacted_layers: tuple[str, ...]
    impacted_targets: tuple[str, ...]


def _canonical_text(text: str) -> str:
    return WS_RE.sub(" ", text.strip().lower())


def redact_sensitive(text: str) -> str:
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = PHONE_RE.sub("[REDACTED_PHONE]", text)
    text = LONG_NUMBER_RE.sub("[REDACTED_NUMBER]", text)
    return WS_RE.sub(" ", text).strip()[:500]


def persistent_feedback_text(text: str) -> str:
    """Keep only future-facing rule changes from mixed natural-language messages."""
    clauses = [part.strip() for part in CLAUSE_RE.split(text) if part.strip()]
    kept = [
        clause for clause in clauses
        if any(marker in _canonical_text(clause) for marker in PERMANENT_MARKERS)
        and not (
            any(marker in _canonical_text(clause) for marker in TRANSIENT_MARKERS)
            and not any(marker in _canonical_text(clause) for marker in ("앞으로", "항상", "규칙", "기준", "금지", "반드시"))
        )
    ]
    return " ".join(kept)


def parse_route_registry(text: str) -> dict[str, tuple[str, ...]]:
    routes: dict[str, tuple[str, ...]] = {}
    for raw_line in text.splitlines():
        match = ROUTE_LINE_RE.match(raw_line.strip())
        if not match:
            continue
        target = match.group(1).upper()
        keywords = tuple(dict.fromkeys(
            keyword.strip().lower()
            for keyword in match.group(2).split("|")
            if keyword.strip()
        ))
        if not keywords:
            raise ValueError(f"empty route keywords for {target}")
        if target in routes:
            raise ValueError(f"duplicate route target in registry: {target}")
        routes[target] = keywords
    required = {"CENTRAL", "WORK_GATE"}
    missing = required - routes.keys()
    if missing:
        raise ValueError(f"registry missing required route target(s): {sorted(missing)}")
    return routes


def load_route_registry() -> dict[str, tuple[str, ...]]:
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"route registry missing: {REGISTRY_PATH}")
    return parse_route_registry(REGISTRY_PATH.read_text(encoding="utf-8"))


def classify(text: str) -> str:
    t = _canonical_text(text)
    if any(k in t for k in (
        "우선순위 바꿔", "우선순위를 바꿔", "우선순위는", "우선순위 아래에",
        "이것부터", "먼저 처리", "최우선으로", "제외시켜", "제외해",
    )):
        return "PRIORITY_CHANGE"
    if any(k in t for k in ("그게 아니라", "아니고", "잘못", "틀렸", "정정", "수정해")):
        return "CORRECTION"
    if any(k in t for k in (
        "반드시", "금지", "하지 마", "하지마", "하지 말", "하지말",
        "지 마", "지마", "말고", "없애라", "유지해", "고정", "관찰자",
    )):
        return "CONSTRAINT"
    if any(k in t for k in ("오류", "실패", "재현", "예시", "이 경우", "이렇게 나오", "사진", "스크린샷")):
        return "NEW_FIXTURE"
    return "SIDE_REQUEST"


def route_targets(text: str, route_map: Mapping[str, Iterable[str]] | None = None) -> tuple[str, ...]:
    t = _canonical_text(text)
    routes = route_map if route_map is not None else load_route_registry()
    hits = [
        str(target).upper()
        for target, keys in routes.items()
        if any(str(k).lower() in t for k in keys)
    ]
    # CENTRAL is only the canonical storage lane.  An unknown owner must remain
    # explicit so downstream target-apply gates cannot mistake fallback storage
    # for a verified target repository apply.
    return tuple(sorted(set(hits or ["CENTRAL", UNREGISTERED_ROUTE])))


def _feedback_id(classification: str, targets: Iterable[str], text: str, source_chat: str, source_ref: str) -> str:
    material = "|".join((source_chat, source_ref, classification, ",".join(sorted(targets)), _canonical_text(text)))
    return sha256(material.encode("utf-8")).hexdigest()[:20]


def normalize(event: FeedbackEvent) -> NormalizedFeedback:
    persistent_text = persistent_feedback_text(event.text)
    normalized_text = persistent_text or event.text
    classification = classify(normalized_text)
    targets = route_targets(normalized_text)
    return NormalizedFeedback(
        feedback_id=_feedback_id(classification, targets, normalized_text, event.source_chat, event.source_ref),
        observed_at=event.observed_at,
        source_chat=event.source_chat,
        source_ref=event.source_ref,
        classification=classification,
        targets=targets,
        sanitized_excerpt=redact_sensitive(normalized_text),
        central_master_candidate=bool(persistent_text) and classification in {"CORRECTION", "CONSTRAINT", "PRIORITY_CHANGE"},
        regression_fixture_candidate=(classification in {"CORRECTION", "NEW_FIXTURE"} or any(t.startswith("TOOL") for t in targets)),
        priority_change=(classification == "PRIORITY_CHANGE"),
    )


def process_batch(events: Iterable[FeedbackEvent], processed_ids: set[str]) -> list[NormalizedFeedback]:
    out: list[NormalizedFeedback] = []
    seen = set(processed_ids)
    for event in events:
        item = normalize(event)
        if item.feedback_id in seen:
            continue
        seen.add(item.feedback_id)
        out.append(item)
    return out


def _record_value(record: Any, key: str, default: Any = None) -> Any:
    if isinstance(record, Mapping):
        return record.get(key, default)
    return getattr(record, key, default)


def impacted_layers(item: NormalizedFeedback) -> tuple[str, ...]:
    layers: list[str] = []
    if item.central_master_candidate or item.priority_change or "CENTRAL" in item.targets:
        layers.append("GLOBAL")
    if any(t in {"EMAIL_DB", "CRM_RESPONSE"} for t in item.targets):
        layers.append("WORKGROUP")
    if any(t.startswith("TOOL") for t in item.targets):
        layers.append("TOOL_OR_DOMAIN_OVERRIDE")
    if item.regression_fixture_candidate:
        layers.append("DATA_OR_EXECUTION_ASSET")
    return tuple(dict.fromkeys(layers or ["DATA_OR_EXECUTION_ASSET"]))


def _specific_target_overlap(left: set[str], right: set[str]) -> bool:
    """CENTRAL is a storage/routing lane, not proof that rule subjects match."""
    return bool((left - {"CENTRAL"}) & (right - {"CENTRAL"}))


def decide_conflict(item: NormalizedFeedback, existing: Sequence[Any]) -> ConflictDecision:
    """Conservative deterministic conflict policy.

    Exact normalized rules are duplicates. Priority changes may supersede older
    priority rules when their routed scopes overlap. Corrections/constraints only
    conflict or supersede when a specific non-CENTRAL target overlaps; CENTRAL by
    itself never authorizes cross-scope deactivation.
    """
    duplicate_ids: list[str] = []
    supersedes: list[str] = []
    conflicts: list[str] = []
    item_text = _canonical_text(item.sanitized_excerpt)
    item_targets = set(item.targets)

    for old in existing:
        old_id = str(_record_value(old, "feedback_id", ""))
        old_text = _canonical_text(str(_record_value(old, "sanitized_excerpt", "")))
        old_class = str(_record_value(old, "classification", ""))
        old_targets = set(_record_value(old, "targets", ()) or ())
        if not _record_value(old, "active", True):
            continue
        if old_text == item_text and old_class == item.classification and old_targets == item_targets:
            duplicate_ids.append(old_id)
            continue

        any_overlap = bool(item_targets & old_targets)
        specific_overlap = _specific_target_overlap(item_targets, old_targets)
        if item.classification == "PRIORITY_CHANGE" and old_class == "PRIORITY_CHANGE" and any_overlap:
            supersedes.append(old_id)
        elif item.classification == "CORRECTION" and old_class in {"CORRECTION", "CONSTRAINT", "PRIORITY_CHANGE"} and specific_overlap:
            supersedes.append(old_id)
        elif item.classification == "CONSTRAINT" and old_class == "CONSTRAINT" and specific_overlap:
            conflicts.append(old_id)

    if duplicate_ids:
        action = "DUPLICATE"
        reason = "same normalized classification/targets/excerpt already active"
    elif conflicts:
        action = "HOLD_CONFLICT"
        reason = "same-priority constraint differs within the same specific target; no silent overwrite"
    elif supersedes:
        action = "SUPERSEDE"
        reason = "new explicit priority/correction supersedes an older rule in the same specific scope"
    else:
        action = "ACCEPT"
        reason = "no active duplicate or proven same-scope conflict"

    return ConflictDecision(
        feedback_id=item.feedback_id,
        action=action,
        reason=reason,
        supersedes=tuple(x for x in supersedes if x),
        conflicts_with=tuple(x for x in conflicts if x),
        impacted_layers=impacted_layers(item),
        impacted_targets=tuple(t for t in item.targets if t != "CENTRAL"),
    )


def canonical_revision(records: Sequence[Any]) -> str:
    normalized = [{
        "feedback_id": str(_record_value(record, "feedback_id", "")),
        "classification": str(_record_value(record, "classification", "")),
        "targets": sorted(_record_value(record, "targets", ()) or ()),
        "sanitized_excerpt": _canonical_text(str(_record_value(record, "sanitized_excerpt", ""))),
        "active": bool(_record_value(record, "active", True)),
    } for record in records]
    payload = json.dumps(sorted(normalized, key=lambda x: x["feedback_id"]), ensure_ascii=False, sort_keys=True)
    return sha256(payload.encode("utf-8")).hexdigest()[:24]


def target_apply_decision(target: str, canonical_rev: str, revision_cache: Mapping[str, str]) -> str:
    return "SKIP_UNCHANGED" if revision_cache.get(target) == canonical_rev else "APPLY_CHANGED_SCOPE"


def checkpoint_state(state: Mapping[str, Any], *, feedback_id: str, stage: str,
                     status: str = "PASS", blocker: str = "") -> dict[str, Any]:
    if stage not in STAGE_ORDER:
        raise ValueError(f"unknown integration stage: {stage}")
    if status not in {"PASS", "HOLD", "FAIL"}:
        raise ValueError(f"unknown stage status: {status}")
    checkpoints = dict(state.get("feedback_checkpoints", {}))
    prior = dict(checkpoints.get(feedback_id, {}))
    prior.update({"last_stage": stage, "status": status})
    if blocker:
        prior["blocker"] = blocker
    elif status == "PASS":
        prior.pop("blocker", None)
    checkpoints[feedback_id] = prior
    return {**state, "feedback_checkpoints": checkpoints}


def next_stage(state: Mapping[str, Any], feedback_id: str) -> str:
    cp = state.get("feedback_checkpoints", {}).get(feedback_id)
    if not cp:
        return STAGE_ORDER[0]
    last = cp.get("last_stage")
    if cp.get("status") in {"HOLD", "FAIL"}:
        return str(last)
    idx = STAGE_ORDER.index(last)
    return STAGE_ORDER[min(idx + 1, len(STAGE_ORDER) - 1)]


def validate_module_contract(contract: Mapping[str, Any]) -> tuple[bool, tuple[str, ...]]:
    missing = tuple(key for key in MODULE_CONTRACT_KEYS if key not in contract)
    return (not missing, missing)


def work_gate(*, chat_files_possible: bool, github_possible: bool, terminal_possible: bool,
              concrete_work_only_blocker: bool, handoff_complete: bool) -> str:
    if chat_files_possible or github_possible or terminal_possible:
        return "WORK_DEFER_DENIED"
    if concrete_work_only_blocker and handoff_complete:
        return "WORK_ELIGIBLE"
    return "HOLD"


def state_after(state: dict[str, Any], processed: Iterable[NormalizedFeedback], *, cursor: str) -> dict[str, Any]:
    ids = list(dict.fromkeys([*state.get("processed_feedback_ids", []), *(x.feedback_id for x in processed)]))
    return {
        **state,
        "schema_version": max(2, int(state.get("schema_version", 1))),
        "last_context_cursor": cursor,
        "processed_feedback_ids": ids,
    }


def to_json_record(item: NormalizedFeedback) -> dict[str, Any]:
    record = asdict(item)
    record["targets"] = list(item.targets)
    return record


def run_fixtures() -> str:
    route_map = load_route_registry()
    assert len(route_map) >= 9
    assert "TOOL002" in route_map and "입찰" in route_map["TOOL002"]
    assert "TOOL013" in route_map and "13번" in route_map["TOOL013"]

    events = [
        FeedbackEvent("2026-08-10T15:32:00+09:00", "current", "각 대화창 피드백 자동수집해서 중앙 마스터와 GitHub에 반영해. 사용자가 다시 전달하지 않게 고정해."),
        FeedbackEvent("2026-08-10T15:33:00+09:00", "toc", "MarketsandMarkets 목차에서 숫자만 떨어진 줄이 또 남는 오류가 있다."),
        FeedbackEvent("2026-08-10T15:34:00+09:00", "work", "터미널에서 가능한 일은 Work로 넘기지 마."),
        FeedbackEvent("2026-08-12T12:19:00+09:00", "priority", "구조 PASS 뒤 우선순위는 이메일 수집 → 7번 고객 컨택 판단 → 1번 중간/최종 안내서 → 37 메타데이터 → 13번 엑셀 자동 업로드 → 6번 목차 정리 → 2번 입찰 → 28~31 → 나머지 등록 도구 순서다."),
    ]
    batch = process_batch(events, set())
    assert len(batch) == 4
    assert batch[0].classification == "CONSTRAINT" and "CENTRAL" in batch[0].targets
    assert batch[1].classification == "NEW_FIXTURE" and "TOOL006" in batch[1].targets
    assert batch[2].classification == "CONSTRAINT" and "WORK_GATE" in batch[2].targets
    assert batch[3].classification == "PRIORITY_CHANGE"
    assert {"TOOL002", "TOOL006", "TOOL007", "TOOL013", "TOOL001", "TOOL037", "EMAIL_DB"}.issubset(set(batch[3].targets))

    duplicate = decide_conflict(batch[0], [to_json_record(batch[0])])
    assert duplicate.action == "DUPLICATE"

    old_priority = normalize(FeedbackEvent("2026-08-12T08:30:00+09:00", "old", "우선순위는 6번 → 13번 → 7번 → 2번이다."))
    supersede = decide_conflict(batch[3], [to_json_record(old_priority)])
    assert supersede.action == "SUPERSEDE" and old_priority.feedback_id in supersede.supersedes

    c1 = normalize(FeedbackEvent("2026-08-12T09:00:00+09:00", "a", "13번은 자동매핑 기능을 반드시 사용해."))
    c2 = normalize(FeedbackEvent("2026-08-12T09:01:00+09:00", "b", "13번은 자동매핑 기능을 반드시 사용하지 마."))
    hold = decide_conflict(c2, [to_json_record(c1)])
    assert hold.action == "HOLD_CONFLICT" and c1.feedback_id in hold.conflicts_with

    # Regression: a CENTRAL-only chat-governance correction must not deactivate
    # unrelated CENTRAL-only reporting/work/priority rules merely because CENTRAL overlaps.
    reporting = normalize(FeedbackEvent("2026-08-13T08:00:00+09:00", "report", "진행상황 보고는 표를 사용해."))
    chat_fix = normalize(FeedbackEvent("2026-08-15T10:00:00+09:00", "chat", "정정: 대화창 이름 오류를 수정해."))
    isolated = decide_conflict(chat_fix, [to_json_record(reporting)])
    assert isolated.action == "ACCEPT" and isolated.supersedes == ()
    assert route_targets("등록되지 않은 완전히 새로운 업무") == ("CENTRAL", UNREGISTERED_ROUTE)

    rev1 = canonical_revision([to_json_record(batch[0])])
    rev2 = canonical_revision([to_json_record(batch[0]), to_json_record(batch[3])])
    assert rev1 != rev2 and len(rev1) == 24
    assert target_apply_decision("TOOL013", rev2, {}) == "APPLY_CHANGED_SCOPE"
    assert target_apply_decision("TOOL013", rev2, {"TOOL013": rev2}) == "SKIP_UNCHANGED"

    s0: dict[str, Any] = {"feedback_checkpoints": {}}
    s1 = checkpoint_state(s0, feedback_id=batch[0].feedback_id, stage="NORMALIZE")
    assert next_stage(s1, batch[0].feedback_id) == "ROUTE_EXISTING_REGISTRY"
    s2 = checkpoint_state(s1, feedback_id=batch[0].feedback_id, stage="CANONICAL_WRITE", status="HOLD", blocker="writer unavailable")
    assert next_stage(s2, batch[0].feedback_id) == "CANONICAL_WRITE"

    valid, missing = validate_module_contract({key: {} for key in MODULE_CONTRACT_KEYS})
    assert valid and missing == ()
    valid2, missing2 = validate_module_contract({"input_schema": {}, "output_schema": {}})
    assert not valid2 and "rollback" in missing2 and "evidence" in missing2

    assert work_gate(chat_files_possible=True, github_possible=False, terminal_possible=False,
                     concrete_work_only_blocker=False, handoff_complete=False) == "WORK_DEFER_DENIED"
    assert work_gate(chat_files_possible=False, github_possible=False, terminal_possible=False,
                     concrete_work_only_blocker=True, handoff_complete=True) == "WORK_ELIGIBLE"
    assert process_batch([events[0]], {batch[0].feedback_id}) == []
    redacted = redact_sensitive("a@b.com 010-1234-5678")
    assert "a@b.com" not in redacted and "010-1234-5678" not in redacted
    json.dumps([to_json_record(x) for x in batch], ensure_ascii=False)

    malformed = "route: CENTRAL = central\nroute: WORK_GATE ="
    try:
        parse_route_registry(malformed)
        raise AssertionError("malformed registry must fail")
    except ValueError:
        pass

    return "PASS: routing + conflict/dedup + scope-isolation + revision/cache + checkpoint + module-contract fixtures"


# Library-only routing/dedup helpers. Operational execution is global_pipeline.py.
