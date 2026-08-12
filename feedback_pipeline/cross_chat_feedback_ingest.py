"""WIC cross-chat feedback ingestion core.

This module is deliberately deterministic. It receives feedback events recovered from
ChatGPT personal-context/history retrieval, removes sensitive customer details,
deduplicates semantically repeated instructions, classifies the feedback, routes it
to the proper tool/workflow, and decides whether it is a central-master candidate,
a regression-fixture candidate, or both.

It does NOT scrape ChatGPT UI conversations directly. Collection is performed by the
scheduled WIC cross-chat collector, which retrieves accessible prior-interaction
context and feeds normalized events through this contract before GitHub persistence.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
import re
from typing import Any, Iterable

CLASSIFICATIONS = (
    "CORRECTION",
    "CONSTRAINT",
    "NEW_FIXTURE",
    "PRIORITY_CHANGE",
    "SIDE_REQUEST",
)

TOOL_KEYWORDS = {
    "TOOL001": ("1번", "안내서", "full_guide", "intermediate_guide", "고객 자동화 안내서"),
    "TOOL002": ("2번", "입찰", "입찰 도구", "bid", "tender"),
    "TOOL006": ("6번", "목차", "toc", "marketsandmarkets", "marketandmarket"),
    "TOOL007": ("7번", "고객 컨택", "컨택 판단", "전화 멘트", "유선 멘트"),
    "TOOL013": ("13번", "엑셀 자동 업로드", "46145"),
    "TOOL037": ("37번", "메타데이터", "상품명", "한글명", "isbn", "code"),
    "EMAIL_DB": ("메일 수집", "이메일 수집", "new_online", "dormant_ledger", "recent_trade", "고객 db"),
    "WORK_GATE": ("워크", "work", "크레딧", "credit", "이관"),
    "CENTRAL": ("중앙 마스터", "깃허브", "github", "대화창", "피드백", "관찰자"),
}

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?82[- .]?)?(?:0\d{1,2}[- .]?)?\d{3,4}[- .]?\d{4}(?!\d)")
LONG_NUMBER_RE = re.compile(r"(?<!\d)\d{7,}(?!\d)")
WS_RE = re.compile(r"\s+")


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


def _canonical_text(text: str) -> str:
    return WS_RE.sub(" ", text.strip().lower())


def redact_sensitive(text: str) -> str:
    """Do not persist customer PII/private transaction details in the central log."""
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = PHONE_RE.sub("[REDACTED_PHONE]", text)
    text = LONG_NUMBER_RE.sub("[REDACTED_NUMBER]", text)
    text = WS_RE.sub(" ", text).strip()
    return text[:500]


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


def route_targets(text: str) -> tuple[str, ...]:
    t = _canonical_text(text)
    hits = []
    for target, keys in TOOL_KEYWORDS.items():
        if any(k.lower() in t for k in keys):
            hits.append(target)
    return tuple(sorted(set(hits or ["CENTRAL"])))


def _feedback_id(classification: str, targets: Iterable[str], text: str) -> str:
    material = "|".join((classification, ",".join(sorted(targets)), _canonical_text(text)))
    return sha256(material.encode("utf-8")).hexdigest()[:20]


def normalize(event: FeedbackEvent) -> NormalizedFeedback:
    classification = classify(event.text)
    targets = route_targets(event.text)
    feedback_id = _feedback_id(classification, targets, event.text)
    central = classification in {"CORRECTION", "CONSTRAINT", "PRIORITY_CHANGE"} or "CENTRAL" in targets
    fixture = classification in {"CORRECTION", "NEW_FIXTURE"} or any(t.startswith("TOOL") for t in targets)
    return NormalizedFeedback(
        feedback_id=feedback_id,
        observed_at=event.observed_at,
        source_chat=event.source_chat,
        source_ref=event.source_ref,
        classification=classification,
        targets=targets,
        sanitized_excerpt=redact_sensitive(event.text),
        central_master_candidate=central,
        regression_fixture_candidate=fixture,
        priority_change=classification == "PRIORITY_CHANGE",
    )


def process_batch(events: Iterable[FeedbackEvent], processed_ids: set[str]) -> list[NormalizedFeedback]:
    out: list[NormalizedFeedback] = []
    seen = set(processed_ids)
    for event in events:
        n = normalize(event)
        if n.feedback_id in seen:
            continue
        seen.add(n.feedback_id)
        out.append(n)
    return out


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
        "schema_version": 1,
        "last_context_cursor": cursor,
        "processed_feedback_ids": ids[-2000:],
    }


def to_json_record(item: NormalizedFeedback) -> dict[str, Any]:
    d = asdict(item)
    d["targets"] = list(item.targets)
    return d


def run_fixtures() -> str:
    events = [
        FeedbackEvent("2026-08-10T15:32:00+09:00", "current", "각 대화창 피드백 자동수집해서 중앙 마스터와 GitHub에 반영해. 사용자가 다시 전달하지 않게 고정해."),
        FeedbackEvent("2026-08-10T15:33:00+09:00", "toc", "MarketsandMarkets 목차에서 숫자만 떨어진 줄이 또 남는 오류가 있다."),
        FeedbackEvent("2026-08-10T15:34:00+09:00", "work", "터미널에서 가능한 일은 Work로 넘기지 마."),
        FeedbackEvent("2026-08-12T08:30:00+09:00", "priority", "우선순위는 6번 목차 정리 → 13번 엑셀 자동 업로드 → 7번 고객 컨택 판단 → 2번 입찰로 하고 이메일 수집과 1번, 37번은 제외해."),
    ]
    batch = process_batch(events, set())
    assert len(batch) == 4
    assert batch[0].classification == "CONSTRAINT"
    assert "CENTRAL" in batch[0].targets
    assert batch[0].central_master_candidate is True
    assert batch[1].classification == "NEW_FIXTURE"
    assert "TOOL006" in batch[1].targets
    assert batch[1].regression_fixture_candidate is True
    assert batch[2].classification == "CONSTRAINT"
    assert "WORK_GATE" in batch[2].targets
    assert batch[3].classification == "PRIORITY_CHANGE"
    assert {"TOOL002", "TOOL006", "TOOL007", "TOOL013", "TOOL001", "TOOL037", "EMAIL_DB"}.issubset(set(batch[3].targets))
    assert batch[3].priority_change is True
    assert work_gate(chat_files_possible=True, github_possible=False, terminal_possible=False,
                     concrete_work_only_blocker=False, handoff_complete=False) == "WORK_DEFER_DENIED"
    assert work_gate(chat_files_possible=False, github_possible=False, terminal_possible=False,
                     concrete_work_only_blocker=True, handoff_complete=True) == "WORK_ELIGIBLE"
    duplicate = process_batch([events[0]], {batch[0].feedback_id})
    assert duplicate == []
    redacted = redact_sensitive("a@b.com 010-1234-5678")
    assert "a@b.com" not in redacted and "010-1234-5678" not in redacted
    json.dumps([to_json_record(x) for x in batch], ensure_ascii=False)
    return "PASS: 15 deterministic cross-chat feedback fixtures"


if __name__ == "__main__":
    print(run_fixtures())
