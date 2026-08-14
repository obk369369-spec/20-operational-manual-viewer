"""Fail-closed preflight for all WIC changes.

Any chat/tool/program/automation/rule/workflow change is allowed only when it carries
an explicit user directive that can be matched to an approved user-record source.
Missing or ambiguous provenance is denied before execution.
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

PROTECTED_ACTIONS = {
    "CREATE_CONVERSATION": ("새 대화창", "대화창 생성", "new chat", "create conversation"),
    "RENAME_CONVERSATION": ("이름 변경", "대화창 이름", "rename"),
    "AUTO_TRANSFER_CONVERSATION": ("자동 이전", "다음 대화창", "auto transfer"),
    "CREATE_MANAGEMENT_CHAT": ("관리 대화창", "보고 대화창", "별도 관리창", "별도 보고창"),
    "CREATE_TOOL": ("도구 생성", "새 도구", "tool create", "new tool"),
    "MODIFY_TOOL": ("도구 수정", "기능 수정", "기능 추가", "도구 보완", "modify tool"),
    "CREATE_PROGRAM": ("프로그램 생성", "새 프로그램", "program create", "new program"),
    "MODIFY_PROGRAM": ("프로그램 수정", "프로그램 보완", "코드 수정", "modify program"),
    "CREATE_AUTOMATION": ("자동화 생성", "예약 작업", "automation create"),
    "MODIFY_AUTOMATION": ("자동화 수정", "예약 변경", "modify automation"),
    "CREATE_REGISTRY": ("새 registry", "new registry", "registry 생성"),
    "MODIFY_RULE": ("규칙 수정", "규칙 추가", "규칙 변경", "modify rule"),
    "MODIFY_WORKFLOW": ("workflow 수정", "workflow 변경", "워크플로 수정", "modify workflow"),
    "CREATE_OPERATING_BRANCH": ("새 운영 구조", "새 운영분기", "new operating branch"),
}

POSITIVE_APPROVAL = (
    "만들어", "생성해", "생성하라", "바꿔", "변경해", "변경하라", "수정해", "수정하라",
    "보완해", "추가해", "추가하라", "옮겨", "이전해", "적용해", "적용하라",
    "create", "rename", "move", "transfer", "add", "modify", "update", "apply",
)
NEGATION = (
    "만들지 마", "만들지마", "생성하지 마", "생성하지마", "바꾸지 마", "바꾸지마",
    "변경하지 마", "변경하지마", "수정하지 마", "수정하지마", "임의로", "금지",
    "하지 마", "하지마", "없어야", "삭제", "deny", "forbid", "do not", "don't",
)

@dataclass(frozen=True)
class ChangeProposal:
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
    observer_report_required: bool


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


def _mentions_action(action: str, directive: str) -> bool:
    return action in PROTECTED_ACTIONS and any(k in _norm(directive) for k in PROTECTED_ACTIONS[action])


def _explicit_approval(directive: str) -> bool:
    t = _norm(directive)
    if any(x in t for x in NEGATION):
        return False
    return any(x in t for x in POSITIVE_APPROVAL)


def deny(reason: str, p: ChangeProposal) -> GuardDecision:
    return GuardDecision("DENY_HOLD", reason, p.action, p.target, p.directive_source_ref, True)


def evaluate(proposal: ChangeProposal, approved_source_text: str | None = None) -> GuardDecision:
    if proposal.action not in PROTECTED_ACTIONS:
        return deny("unknown or unregistered change action", proposal)
    if not proposal.directive_text.strip() or not proposal.directive_source_ref.strip():
        return deny("missing explicit user directive provenance", proposal)
    source = approved_source_text if approved_source_text is not None else load_approved_source_text()
    if _norm(proposal.directive_text) not in _norm(source):
        return deny("directive text not found in approved user-record source", proposal)
    if not _mentions_action(proposal.action, proposal.directive_text):
        return deny("directive does not explicitly name the proposed change", proposal)
    if not _explicit_approval(proposal.directive_text):
        return deny("directive is not an explicit positive approval", proposal)
    return GuardDecision("ALLOW", "explicit user directive provenance verified", proposal.action, proposal.target, proposal.directive_source_ref, False)


def run_fixtures() -> str:
    approved = """
사용자 지시 기록:
- 테스트용 새 대화창을 만들어.
- 6번 도구 기능 수정을 해라.
- 13번 프로그램 수정을 해라.
- 기존 대화창 이름 변경은 하지 마.
- 새 registry를 임의로 만들지 마.
"""
    cases = {
        "missing_provenance": ChangeProposal("CREATE_TOOL", "tool-x", "", ""),
        "unauthorized_chat": ChangeProposal("CREATE_CONVERSATION", "chat-x", "새 고객관리 대화창을 만들어.", "user:999"),
        "unauthorized_tool": ChangeProposal("MODIFY_TOOL", "tool-7", "7번 도구 기능 수정을 해라.", "user:998"),
        "unauthorized_program": ChangeProposal("MODIFY_PROGRAM", "program-x", "프로그램 수정을 해라.", "user:997"),
        "negative_rename": ChangeProposal("RENAME_CONVERSATION", "chat-x", "기존 대화창 이름 변경은 하지 마.", "user:2"),
        "negative_registry": ChangeProposal("CREATE_REGISTRY", "registry-x", "새 registry를 임의로 만들지 마.", "user:3"),
        "approved_chat": ChangeProposal("CREATE_CONVERSATION", "chat-test", "테스트용 새 대화창을 만들어.", "user:1"),
        "approved_tool": ChangeProposal("MODIFY_TOOL", "tool-6", "6번 도구 기능 수정을 해라.", "user:4"),
        "approved_program": ChangeProposal("MODIFY_PROGRAM", "program-13", "13번 프로그램 수정을 해라.", "user:5"),
    }
    result = {name: asdict(evaluate(item, approved)) for name, item in cases.items()}
    for name in ("missing_provenance", "unauthorized_chat", "unauthorized_tool", "unauthorized_program", "negative_rename", "negative_registry"):
        assert result[name]["decision"] == "DENY_HOLD"
        assert result[name]["observer_report_required"] is True
    for name in ("approved_chat", "approved_tool", "approved_program"):
        assert result[name]["decision"] == "ALLOW"
        assert result[name]["observer_report_required"] is False
    evidence = {
        "schema_version": 2,
        "guard": "UNAUTHORIZED_CHANGE_GUARD",
        "scope": "ALL_WIC_CHAT_TOOL_PROGRAM_AUTOMATION_RULE_WORKFLOW_CHANGES",
        "cases": result,
        "result": "PASS_INTERNAL_FIXTURE",
        "external_independent_verification": False,
    }
    (Path(__file__).resolve().parent / "unauthorized_structure_guard_evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return "PASS: universal WIC user-directive provenance guard fixtures"


if __name__ == "__main__":
    print(run_fixtures())
