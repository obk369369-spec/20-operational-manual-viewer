"""Fail-closed preflight for WIC structural changes.

A structural change is allowed only when it carries an explicit user directive
that can be matched to an approved source record. Missing or ambiguous provenance
is denied before any create/rename/transfer/registry mutation is attempted.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
import re
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
APPROVED_SOURCE_PATHS = (
    ROOT / "WIC_GLOBAL_OPERATING_RULES.md",
    ROOT / "WIC_OBSERVER_STATUS.md",
)

STRUCTURAL_ACTIONS = {
    "CREATE_CONVERSATION": ("새 대화창", "대화창 생성", "new chat", "create conversation"),
    "RENAME_CONVERSATION": ("이름 변경", "대화창 이름", "rename"),
    "AUTO_TRANSFER_CONVERSATION": ("자동 이전", "다음 대화창", "auto transfer"),
    "CREATE_MANAGEMENT_CHAT": ("관리 대화창", "보고 대화창", "별도 관리창", "별도 보고창"),
    "CREATE_REGISTRY": ("새 registry", "new registry", "registry 생성"),
    "CREATE_OPERATING_BRANCH": ("새 운영 구조", "새 운영분기", "new operating branch"),
}

POSITIVE_APPROVAL = (
    "만들어", "생성해", "생성하라", "바꿔", "변경해", "변경하라", "옮겨", "이전해", "추가해", "추가하라",
    "create", "rename", "move", "transfer", "add",
)
NEGATION = (
    "만들지 마", "만들지마", "생성하지 마", "생성하지마", "바꾸지 마", "바꾸지마", "변경하지 마", "변경하지마",
    "임의로", "금지", "하지 마", "하지마", "없어야", "삭제", "deny", "forbid", "do not", "don't",
)


@dataclass(frozen=True)
class StructuralProposal:
    action: str
    target: str
    directive_text: str
    directive_source_ref: str


@dataclass(frozen=True)
class GuardDecision:
    decision: str
    reason: str
    action: str
    target: str
    directive_source_ref: str


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def load_approved_source_text(paths: Iterable[Path] = APPROVED_SOURCE_PATHS) -> str:
    chunks = []
    for path in paths:
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    if not chunks:
        raise FileNotFoundError("no approved WIC source records available")
    return "\n".join(chunks)


def _action_is_supported(action: str) -> bool:
    return action in STRUCTURAL_ACTIONS


def _directive_mentions_action(action: str, directive: str) -> bool:
    t = _norm(directive)
    return any(keyword in t for keyword in STRUCTURAL_ACTIONS[action])


def _directive_is_explicit_approval(directive: str) -> bool:
    t = _norm(directive)
    if any(x in t for x in NEGATION):
        return False
    return any(x in t for x in POSITIVE_APPROVAL)


def evaluate(proposal: StructuralProposal, approved_source_text: str | None = None) -> GuardDecision:
    if not _action_is_supported(proposal.action):
        return GuardDecision("DENY_HOLD", "unknown structural action", proposal.action, proposal.target, proposal.directive_source_ref)
    if not proposal.directive_text.strip() or not proposal.directive_source_ref.strip():
        return GuardDecision("DENY_HOLD", "missing explicit user directive provenance", proposal.action, proposal.target, proposal.directive_source_ref)
    source = approved_source_text if approved_source_text is not None else load_approved_source_text()
    if _norm(proposal.directive_text) not in _norm(source):
        return GuardDecision("DENY_HOLD", "directive text not found in approved user-record source", proposal.action, proposal.target, proposal.directive_source_ref)
    if not _directive_mentions_action(proposal.action, proposal.directive_text):
        return GuardDecision("DENY_HOLD", "directive does not explicitly name the proposed structural action", proposal.action, proposal.target, proposal.directive_source_ref)
    if not _directive_is_explicit_approval(proposal.directive_text):
        return GuardDecision("DENY_HOLD", "directive is not an explicit positive approval", proposal.action, proposal.target, proposal.directive_source_ref)
    return GuardDecision("ALLOW", "explicit user directive provenance verified", proposal.action, proposal.target, proposal.directive_source_ref)


def run_fixtures() -> str:
    approved = """
사용자 지시 기록:
- 테스트용 새 대화창을 만들어.
- 기존 대화창 이름 변경은 하지 마.
- 새 registry를 임의로 만들지 마.
"""
    cases = {
        "missing_provenance": StructuralProposal("CREATE_CONVERSATION", "chat-x", "", ""),
        "not_in_record": StructuralProposal("CREATE_CONVERSATION", "chat-x", "새 고객관리 대화창을 만들어.", "user:999"),
        "negative_rename": StructuralProposal("RENAME_CONVERSATION", "chat-x", "기존 대화창 이름 변경은 하지 마.", "user:2"),
        "negative_registry": StructuralProposal("CREATE_REGISTRY", "registry-x", "새 registry를 임의로 만들지 마.", "user:3"),
        "explicit_create": StructuralProposal("CREATE_CONVERSATION", "chat-test", "테스트용 새 대화창을 만들어.", "user:1"),
    }
    result = {name: asdict(evaluate(item, approved)) for name, item in cases.items()}
    assert result["missing_provenance"]["decision"] == "DENY_HOLD"
    assert result["not_in_record"]["decision"] == "DENY_HOLD"
    assert result["negative_rename"]["decision"] == "DENY_HOLD"
    assert result["negative_registry"]["decision"] == "DENY_HOLD"
    assert result["explicit_create"]["decision"] == "ALLOW"
    evidence = {
        "schema_version": 1,
        "guard": "UNAUTHORIZED_STRUCTURE_GUARD",
        "cases": result,
        "result": "PASS_INTERNAL_FIXTURE",
        "external_independent_verification": False,
    }
    (Path(__file__).resolve().parent / "unauthorized_structure_guard_evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return "PASS: unauthorized structural change preflight fixtures"


if __name__ == "__main__":
    print(run_fixtures())
