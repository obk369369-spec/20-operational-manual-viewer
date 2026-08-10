"""P2 Tool7 customer-contact judgment engine.
Recovered from historical Tool7 user-approved rules. No network/send side effects.
Normative rules remain in WIC_GLOBAL_OPERATING_RULES.md.
"""

CONTACT_TYPES = {
    "real_purchase", "quote", "research_project", "new_business", "procurement",
    "researcher", "nonresponse", "moved_hold", "one_way_notice", "reference_only"
}


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
