"""P2 Tool7 customer-contact judgment engine.
Recovered from historical Tool7 user-approved rules. No network/send side effects.
Normative rules remain in WIC_GLOBAL_OPERATING_RULES.md.
"""

CONTACT_TYPES = {
    "real_purchase", "quote", "research_project", "new_business", "procurement",
    "researcher", "nonresponse", "moved_hold", "one_way_notice", "reference_only"
}


def prepare_contact_copy(customer, context, reply=None):
    """Short discovery turns, not outreach authorization or a current-interest claim.

    context is a source-backed plain-language projection of recovered evidence.
    Company research never establishes a customer's present interests.
    """
    permission = judge_contact(customer)
    if not permission["copy_generation_allowed"]:
        return {"status": permission["decision"], "issues": permission["blockers"], "turns": []}
    required = ("source_ref", "history_kind", "plain_topic", "addressee")
    if any(not context.get(k) for k in required) or context.get("evidence_verified") is not True:
        return {"status": "HOLD", "issues": ["COPY_EVIDENCE_MISSING"], "turns": []}
    kind = context["history_kind"]
    topic = context["plain_topic"]
    if kind not in ("one_way", "response", "quote", "purchase", "none"):
        return {"status": "HOLD", "issues": ["UNKNOWN_HISTORY_KIND"], "turns": []}
    history = {
        "one_way": "지난번 회사소개서를 보내드렸습니다.",
        "response": f"지난 통화에서 {context.get('requested_format', topic)}를 말씀해 주셨는데요.",
        "quote": f"문의하신 {topic} 견적 건으로 연락드렸습니다.",
        "purchase": f"전에 구매하신 {topic} 건으로 연락드렸습니다.",
        "none": "자료 검토 방향을 짧게 여쭤보려고 연락드렸습니다.",
    }[kind]
    question = (f"{topic}, 두 분야 모두 보면 될까요?" if kind == "response" and context.get("two_options") else
                "견적에서 더 확인하실 내용이 있을까요?" if kind == "quote" else
                "지금도 그쪽 자료를 보고 계실까요?" if kind in ("response", "purchase") else
                f"{topic} 중 요즘 더 살펴보시는 쪽이 있을까요?" if context.get("two_options") else
                f"요즘 {topic} 쪽도 살펴보고 계실까요?")
    turns = [f"{context['addressee']}, 안녕하세요. 월드산업정보센터입니다.", history, question]
    next_action = "WAIT_FOR_CUSTOMER_REPLY"
    if reply is not None:
        if not reply.get("source_ref") or reply.get("verified") is not True:
            return {"status": "HOLD", "issues": ["REPLY_EVIDENCE_MISSING"], "turns": []}
        code = reply.get("code")
        if code == "STOP":
            turns = ["알겠습니다. 더 연락드리지 않겠습니다."]
            next_action = "DO_NOT_CONTACT"
        elif code == "OTHER":
            turns = ["그렇군요. 요즘은 어떤 쪽을 보고 계실까요?"]
            next_action = "WAIT_FOR_CUSTOMER_SCOPE"
        elif code == "LATER":
            turns = ["알겠습니다. 지금은 여기까지 말씀드리겠습니다."]
            next_action = "WAIT_FOR_REQUESTED_FOLLOWUP"
        elif code == "SCOPE" and reply.get("plain_scope"):
            turns = [f"말씀하신 범위는 {reply['plain_scope']} 쪽이 맞을까요?"]
            next_action = "WAIT_FOR_SCOPE_CONFIRMATION"
        elif code == "CONFIRMED" and reply.get("plain_scope"):
            turns = [f"네, {reply['plain_scope']} 범위에 맞춰 자료를 확인하겠습니다."]
            next_action = "SELECT_VERIFIED_MATERIALS_FOR_CONFIRMED_SCOPE"
        else:
            return {"status": "HOLD", "issues": ["REPLY_SCOPE_UNCONFIRMED"], "turns": []}
    result = {
        "status": "DRAFT", "turns": turns, "email_body": "\n\n".join(turns),
        "phone_message": "\n".join(turns) if not context.get("landline_unavailable") else "",
        "channel": "EMAIL" if context.get("landline_unavailable") else permission["channel"],
        "next_action": next_action, "recommendation_allowed": next_action == "SELECT_VERIFIED_MATERIALS_FOR_CONFIRMED_SCOPE",
        "source_ref": context["source_ref"], "history_kind": kind,
        "send_allowed": False,
        "cue_card": {"start": turns[0], "ask": turns[-1], "then": "확인된 범위만 자료 검증" if next_action == "SELECT_VERIFIED_MATERIALS_FOR_CONFIRMED_SCOPE" else "답변을 기다립니다."},
        "quality_scope": "AUTOMATED_CONSTRAINTS_ONLY_NOT_ACTUAL_CALL_RECEPTION",
    }
    issues = validate_contact_copy(result)
    result["status"] = "HOLD" if issues else "DRAFT_VALIDATED"
    result["issues"] = issues
    if issues:
        result["recommendation_allowed"] = False
        result["next_action"] = "VERIFY_COPY_EVIDENCE"
        result["phone_message"] = result["email_body"] = ""
    return result


def validate_contact_copy(result):
    """Reject known quality failures; do not claim mechanical checks prove naturalness."""
    import re
    turns = result.get("turns", [])
    text = " ".join(turns)
    issues = []
    if not turns or any(len(t) > 100 or len(t.split()) > 20 for t in turns):
        issues.append("TURN_TOO_LONG_OR_EMPTY")
    if text.count("?") > 1:
        issues.append("MULTIPLE_QUESTIONS_BEFORE_REPLY")
    if re.search(r"정기적으로|꾸준히|지속적으로|보내드려도|휴대전화 번호|핸드폰 번호|연구하고 계시|현재 관심|업무 기준으로|방향과 직접 관련", text):
        issues.append("PRESSURE_OR_UNVERIFIED_ASSERTION")
    if "·" in text or re.search(r"고신뢰성|실증 기반구축|소자공정", text):
        issues.append("JARGON_LIST")
    if result.get("history_kind") in ("one_way", "none") and re.search(r"문의하신|구매하신|말씀해 주셨", text):
        issues.append("OUTBOUND_HISTORY_AS_CUSTOMER_RESPONSE")
    return issues


def judge_contact(customer):
    """Return deterministic gate before any phone/email copy is generated."""
    blockers = []
    warnings = []

    if not customer.get("current_employment_verified"):
        blockers.append("CURRENT_EMPLOYMENT_UNVERIFIED")
    if not customer.get("company_direction_verified"):
        blockers.append("COMPANY_DIRECTION_MISSING")
    if customer.get("moved_or_left"):
        blockers.append("MOVED_OR_LEFT_HOLD")
    if customer.get("explicit_stop_or_rejection"):
        blockers.append("CONTACT_STOP")

    direct = bool(customer.get("direct_inquiry") or customer.get("purchase_history") or customer.get("quote_history"))
    one_way = bool(customer.get("one_way_sent_only"))
    cc_only = bool(customer.get("cc_only"))

    if one_way and not direct:
        warnings.append("ONE_WAY_NOTICE_NOT_CUSTOMER_NEED")
    if cc_only and not direct:
        warnings.append("CC_HISTORY_NOT_DIRECT_INQUIRY")

    if blockers:
        return {
            "decision": "HOLD" if "CONTACT_STOP" not in blockers else "FAIL",
            "blockers": blockers,
            "warnings": warnings,
            "channel": "NONE",
            "copy_generation_allowed": False,
            "next_action": "VERIFY_OR_STOP_BEFORE_COPY"
        }

    # Historical rule: decide customer state/contact permission/channel first; copy is last.
    if customer.get("prefers_material_before_call") or customer.get("research_or_enterprise_customer"):
        channel = "MATERIAL_FIRST"
    elif customer.get("phone_allowed"):
        channel = "PHONE"
    else:
        channel = "EMAIL_OR_TEXT_FIRST"

    return {
        "decision": "PASS",
        "blockers": [],
        "warnings": warnings,
        "channel": channel,
        "copy_generation_allowed": True,
        "next_action": "GENERATE_PERSONALIZED_COPY_LAST"
    }


def history_usage(customer):
    """Controls what old history may be said in outreach."""
    if customer.get("purchase_history"):
        return "PURCHASE_MAY_BE_STATED_ACCURATELY"
    if customer.get("direct_inquiry"):
        return "DIRECT_INQUIRY_MAY_BE_STATED_ACCURATELY"
    if customer.get("cc_only"):
        return "STATE_CC_CONTEXT_ONLY_NEVER_CALL_IT_CUSTOMER_INQUIRY"
    if customer.get("one_way_sent_only"):
        return "DO_NOT_USE_AS_CUSTOMER_NEED"
    if customer.get("old_ledger_note"):
        return "CURRENT_COMPANY_DIRECTION_FIRST_LEDGER_NOTE_ONLY_AS_SECONDARY_CONTEXT"
    return "NO_HISTORY_CLAIM"


def recommendation_gate(report):
    """A report can enter recommendation output only when required facts are verified."""
    required = ("title", "publisher", "publication_date", "link", "paid", "tradable")
    missing = [k for k in required if report.get(k) in (None, "")]
    if missing:
        return {"state": "HOLD", "missing": missing}
    if report.get("paid") is not True:
        return {"state": "FAIL", "reason": "FREE_REPORT_EXCLUDED"}
    if report.get("tradable") is not True:
        return {"state": "HOLD", "reason": "NON_TRADABLE_PUBLISHER"}
    return {"state": "PASS"}


def run_fixtures():
    base = dict(current_employment_verified=True, company_direction_verified=True,
                moved_or_left=False, explicit_stop_or_rejection=False,
                phone_allowed=True, direct_inquiry=True)
    assert judge_contact(base)["decision"] == "PASS"
    assert judge_contact(base)["copy_generation_allowed"] is True

    x = dict(base); x["company_direction_verified"] = False
    assert judge_contact(x)["decision"] == "HOLD"
    assert judge_contact(x)["copy_generation_allowed"] is False

    x = dict(base); x["direct_inquiry"] = False; x["one_way_sent_only"] = True
    r = judge_contact(x)
    assert "ONE_WAY_NOTICE_NOT_CUSTOMER_NEED" in r["warnings"]
    assert history_usage(x) == "DO_NOT_USE_AS_CUSTOMER_NEED"

    x = dict(base); x["direct_inquiry"] = False; x["cc_only"] = True
    assert history_usage(x) == "STATE_CC_CONTEXT_ONLY_NEVER_CALL_IT_CUSTOMER_INQUIRY"

    x = dict(base); x["research_or_enterprise_customer"] = True
    assert judge_contact(x)["channel"] == "MATERIAL_FIRST"

    old = dict(old_ledger_note=True)
    assert history_usage(old) == "CURRENT_COMPANY_DIRECTION_FIRST_LEDGER_NOTE_ONLY_AS_SECONDARY_CONTEXT"

    good_report = dict(title="T", publisher="P", publication_date="2026-01", link="https://example.test", paid=True, tradable=True)
    assert recommendation_gate(good_report)["state"] == "PASS"
    bad_report = dict(good_report); bad_report["link"] = ""
    assert recommendation_gate(bad_report)["state"] == "HOLD"

    return "PASS: 8 deterministic P2 fixtures"


if __name__ == "__main__":
    import json
    import sys
    if "--copy-stdin" in sys.argv:
        packet = json.load(sys.stdin)
        output = prepare_contact_copy(packet.get("customer", {}), packet.get("context", {}), packet.get("reply"))
        print(json.dumps(output, ensure_ascii=True))
        raise SystemExit(0 if output["status"] == "DRAFT_VALIDATED" else 2)
    print(run_fixtures())
