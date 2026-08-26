"""Deterministic Work-16 candidate assessment for normalized feedback."""
from __future__ import annotations

from typing import Any, Mapping


def assess_work_ready(*, root_cause_id: str, text: str, recur_count: int, classification: str) -> dict[str, Any]:
    normalized = " ".join(text.lower().split())
    customer = any(word in normalized for word in ("고객", "안내서", "컨택", "메일", "엑셀", "목차", "보고서"))
    blocking = any(word in normalized for word in ("업무 중단", "사용 불가", "작동하지", "데이터 손실", "고객업무를 막")) or (customer and "중단" in normalized)
    high = blocking or any(word in normalized for word in ("치명", "반복 오류", "계속 오류", "또 누락", "또 틀"))
    medium = customer or classification in {"CORRECTION", "NEW_FIXTURE"}
    customer_impact = "BLOCKING" if blocking else "OPERATIONAL" if customer else "NONE"
    severity = "HIGH" if high else "MEDIUM" if medium else "LOW"
    repeated = max(1, int(recur_count)) >= 2
    actionable = classification in {"CORRECTION", "NEW_FIXTURE", "CONSTRAINT"}
    work_ready = actionable and (customer_impact != "NONE" or severity in {"MEDIUM", "HIGH"})
    return {
        "root_cause_id": root_cause_id,
        "recur_count": max(1, int(recur_count)),
        "customer_impact": customer_impact,
        "severity": severity,
        "repeatability": "REPEATED" if repeated else "FIRST_SEEN",
        "work_ready": work_ready,
        "work_status": "WORK_READY" if work_ready else "ACCUMULATING",
    }


def update_work_ready_state(integration: Mapping[str, Any], assessment: Mapping[str, Any]) -> dict[str, Any]:
    updated = dict(integration)
    candidates = dict(updated.get("work_ready_candidates", {}))
    candidates[str(assessment["root_cause_id"])] = dict(assessment)
    updated["work_ready_candidates"] = candidates
    updated["work_ready_summary"] = {
        "candidate_count": len(candidates),
        "work_ready_count": sum(bool(item.get("work_ready")) for item in candidates.values()),
        "manual_chat_transfer_required": False,
    }
    return updated


def run_fixtures() -> str:
    first = assess_work_ready(
        root_cause_id="same-root", text="고객 안내서에서 필드가 누락됐다.", recur_count=1, classification="NEW_FIXTURE"
    )
    repeat = assess_work_ready(
        root_cause_id="same-root", text="고객 안내서에서 필드가 누락됐다.", recur_count=2, classification="NEW_FIXTURE"
    )
    different = assess_work_ready(
        root_cause_id="different-root", text="엑셀 고객업무가 중단되는 오류다.", recur_count=1, classification="CORRECTION"
    )
    assert first["work_ready"] is True and first["work_status"] == "WORK_READY"
    assert repeat["work_ready"] is True and repeat["repeatability"] == "REPEATED"
    assert different["work_ready"] is True and different["customer_impact"] == "BLOCKING"
    state = update_work_ready_state({}, first)
    state = update_work_ready_state(state, repeat)
    state = update_work_ready_state(state, different)
    assert len(state["work_ready_candidates"]) == 2
    assert state["work_ready_summary"] == {
        "candidate_count": 2, "work_ready_count": 2, "manual_chat_transfer_required": False
    }
    return "PASS: root-cause recurrence + customer impact + severity + automatic WORK_READY fixtures"


if __name__ == "__main__":
    print(run_fixtures())
