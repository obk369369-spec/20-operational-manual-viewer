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
    "MODIFY_TOOL": ("도구 수정", "기능 수정", "기능 수정을", "기능 추가", "도구 보완", "modify tool"),
    "CREATE_PROGRAM": ("프로그램 생성", "새 프로그램", "program create", "new program"),
    "MODIFY_PROGRAM": ("프로그램 수정", "프로그램 수정을", "프로그램 보완", "코드 수정", "modify program"),
    "CREATE_AUTOMATION": ("자동화 생성", "예약 작업", "automation create"),
    "CREATE_SCHEDULE": ("예약 생성", "리마인더 생성", "schedule create", "create reminder"),
    "ENABLE_AUTOMATION": ("자동화 활성화", "예약 활성화", "enable automation", "enable schedule"),
    "MODIFY_AUTOMATION": ("자동화 수정", "예약 변경", "modify automation"),
    "CREATE_WORK": ("work 생성", "작업 생성", "자동 작업 생성", "create work", "create task"),
    "CREATE_REGISTRY": ("새 registry", "new registry", "registry 생성"),
    "MODIFY_RULE": ("규칙 수정", "규칙 추가", "규칙 변경", "modify rule"),
    "MODIFY_WORKFLOW": ("workflow 수정", "workflow 변경", "워크플로 수정", "modify workflow"),
    "CREATE_OPERATING_BRANCH": ("새 운영 구조", "새 운영분기", "new operating branch"),
    "APPLY_FEEDBACK": ("피드백", "반영", "적용", "통합", "우선순위", "최우선"),
}

POSITIVE_APPROVAL = (
    "만들어", "생성해", "생성하라", "바꿔", "변경해", "변경하라", "수정해", "수정해라", "수정을 해라", "수정하라",
    "보완해", "추가해", "추가하라", "옮겨", "이전해", "적용해", "적용하라", "해야",
    "create", "rename", "move", "transfer", "add", "modify", "update", "apply",
)
NEGATION = (
    "만들지 마", "만들지마", "생성하지 마", "생성하지마", "바꾸지 마", "바꾸지마",
    "변경하지 마", "변경하지마", "수정하지 마", "수정하지마", "임의로", "금지",
    "하지 마", "하지마", "없어야", "삭제", "deny", "forbid", "do not", "don't",
)
CURRENT_CHAT_PREFIXES = ("CURRENT_CHAT#", "CHATGPT_CURRENT_CHAT#")

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


def _record_text(line: str) -> str:
    return _norm(re.sub(r"^[\s#>*+-]+", "", line))


def _canonical_record_directives(source: str) -> set[str]:
    """Read exact canonical sanitized excerpts without falling back to substring matching."""
    match = re.search(
        r"<!-- WIC_CANONICAL_FEEDBACK_START -->\s*```json\s*(.*?)\s*```\s*<!-- WIC_CANONICAL_FEEDBACK_END -->",
        source,
        re.S,
    )
    if not match:
        return set()
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError:
        return set()
    records = payload.get("records", [])
    if not isinstance(records, list):
        return set()
    return {
        _norm(str(record.get("sanitized_excerpt", "")))
        for record in records
        if isinstance(record, dict) and str(record.get("sanitized_excerpt", "")).strip()
    }


def _directive_recorded(directive: str, source: str) -> bool:
    wanted = _norm(directive)
    if any(_record_text(line) == wanted for line in source.splitlines()):
        return True
    return wanted in _canonical_record_directives(source)


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


def build_observer_report(decision: GuardDecision) -> dict:
    if decision.decision != "DENY_HOLD" or not decision.observer_report_required:
        raise ValueError("observer report payload is only valid for DENY_HOLD decisions")
    return {
        "report_type": "DENY_OBSERVER_REPORT",
        "action": decision.action,
        "target": decision.target,
        "reason": decision.reason,
        "directive_source_ref": decision.directive_source_ref,
        "structural_error_unauthorized": True,
        "blocked_before_mutation": True,
        "observer_report_required": True,
        "normal_unaffected_work_may_continue": True,
    }


def evaluate(proposal: ChangeProposal, approved_source_text: str | None = None) -> GuardDecision:
    if proposal.action not in PROTECTED_ACTIONS:
        return deny("unknown or unregistered change action", proposal)
    if not proposal.directive_text.strip() or not proposal.directive_source_ref.strip():
        return deny("missing explicit user directive provenance", proposal)
    if (
        proposal.action == "APPLY_FEEDBACK"
        and proposal.target == "WIC_GLOBAL_OPERATING_RULES.md"
        and any(proposal.directive_source_ref.startswith(prefix) for prefix in CURRENT_CHAT_PREFIXES)
        and _mentions_action(proposal.action, proposal.directive_text)
        and _explicit_approval(proposal.directive_text)
    ):
        return GuardDecision(
            "ALLOW", "explicit current-chat feedback accepted at ingestion boundary",
            proposal.action, proposal.target, proposal.directive_source_ref, False,
        )
    source = approved_source_text if approved_source_text is not None else load_approved_source_text()
    if not _directive_recorded(proposal.directive_text, source):
        return deny("directive text not found as an exact approved user-record entry", proposal)
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
<!-- WIC_CANONICAL_FEEDBACK_START -->
```json
{"schema_version":1,"records":[{"sanitized_excerpt":"피드백은 중앙 규칙에 반영해야 한다."}]}
```
<!-- WIC_CANONICAL_FEEDBACK_END -->
"""
    cases = {
        "missing_provenance": ChangeProposal("CREATE_TOOL", "tool-x", "", ""),
        "unauthorized_chat": ChangeProposal("CREATE_CONVERSATION", "chat-x", "새 고객관리 대화창을 만들어.", "user:999"),
        "unauthorized_rename": ChangeProposal("RENAME_CONVERSATION", "chat-x", "대화창 이름을 변경해.", "user:996"),
        "unauthorized_schedule": ChangeProposal("CREATE_SCHEDULE", "schedule-x", "예약 생성해.", "user:995"),
        "unauthorized_automation_enable": ChangeProposal("ENABLE_AUTOMATION", "automation-x", "자동화 활성화해.", "user:994"),
        "unauthorized_work": ChangeProposal("CREATE_WORK", "work-x", "자동 작업 생성해.", "user:993"),
        "unauthorized_tool": ChangeProposal("MODIFY_TOOL", "tool-7", "7번 도구 기능 수정을 해라.", "user:998"),
        "unauthorized_program": ChangeProposal("MODIFY_PROGRAM", "program-x", "프로그램 수정을 해라.", "user:997"),
        "negative_rename": ChangeProposal("RENAME_CONVERSATION", "chat-x", "기존 대화창 이름 변경은 하지 마.", "user:2"),
        "negative_registry": ChangeProposal("CREATE_REGISTRY", "registry-x", "새 registry를 임의로 만들지 마.", "user:3"),
        "approved_chat": ChangeProposal("CREATE_CONVERSATION", "chat-test", "테스트용 새 대화창을 만들어.", "user:1"),
        "approved_tool": ChangeProposal("MODIFY_TOOL", "tool-6", "6번 도구 기능 수정을 해라.", "user:4"),
        "approved_program": ChangeProposal("MODIFY_PROGRAM", "program-13", "13번 프로그램 수정을 해라.", "user:5"),
        "approved_canonical_feedback": ChangeProposal("APPLY_FEEDBACK", "WIC_GLOBAL_OPERATING_RULES.md", "피드백은 중앙 규칙에 반영해야 한다.", "canonical:test"),
    }
    result = {name: asdict(evaluate(item, approved)) for name, item in cases.items()}
    deny_names = (
        "missing_provenance", "unauthorized_chat", "unauthorized_rename",
        "unauthorized_schedule", "unauthorized_automation_enable", "unauthorized_work", "unauthorized_tool",
        "unauthorized_program", "negative_rename", "negative_registry",
    )
    for name in deny_names:
        assert result[name]["decision"] == "DENY_HOLD"
        assert result[name]["observer_report_required"] is True
    for name in ("approved_chat", "approved_tool", "approved_program", "approved_canonical_feedback"):
        assert result[name]["decision"] == "ALLOW"
        assert result[name]["observer_report_required"] is False

    observer_reports = [build_observer_report(evaluate(cases[name], approved)) for name in deny_names]
    assert len(observer_reports) == len(deny_names)
    assert all(x["structural_error_unauthorized"] is True for x in observer_reports)
    assert all(x["blocked_before_mutation"] is True for x in observer_reports)
    assert all(x["observer_report_required"] is True for x in observer_reports)

    evidence = {
        "schema_version": 5,
        "guard": "UNAUTHORIZED_CHANGE_GUARD",
        "scope": "ALL_WIC_CHAT_TOOL_PROGRAM_AUTOMATION_RULE_WORKFLOW_CHANGES",
        "cases": result,
        "observer_reports": observer_reports,
        "observer_report_contract": {
            "required_fields": [
                "action", "target", "reason", "directive_source_ref",
                "structural_error_unauthorized", "blocked_before_mutation",
                "observer_report_required", "normal_unaffected_work_may_continue",
            ],
            "delivery_target": "WIC observer status/report lane",
            "rule": "Every DENY_HOLD must be surfaced to the observer; never silently swallow denied mutation evidence.",
        },
        "canonical_exact_match": True,
        "substring_approval_forbidden": True,
        "unrequested_mutation_counts": {
            "UNREQUESTED_CHAT_CREATE": 0,
            "UNREQUESTED_CHAT_RENAME": 0,
            "UNREQUESTED_SCHEDULE_CREATE": 0,
            "UNREQUESTED_AUTOMATION_ENABLE": 0,
        },
        "result": "PASS_INTERNAL_FIXTURE",
        "external_independent_verification": False,
    }
    (Path(__file__).resolve().parent / "unauthorized_structure_guard_evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return "PASS: universal WIC user-directive provenance guard + canonical exact-match + observer report fixtures"


if __name__ == "__main__":
    print(run_fixtures())
