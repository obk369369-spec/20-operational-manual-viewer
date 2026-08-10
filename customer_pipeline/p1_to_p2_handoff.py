"""Deterministic handoff from P1 customer DB records to P2 Tool7 judgment.
No intent inference and no external send side effects.
"""

ALLOWED_COHORTS = {"NEW_ONLINE", "DORMANT_LEDGER", "RECENT_TRADE"}
P2_REQUIRED_VERIFICATION = (
    "current_employment_verified",
    "company_direction_verified",
)


def build_p2_input(p1_record):
    """Build only from explicit stored facts. Missing P2 facts cause HOLD."""
    errors = []
    if p1_record.get("db_state") not in {"MAIN_DB", "UPDATE_EXISTING"}:
        errors.append("P1_NOT_READY_FOR_P2")
    if p1_record.get("source_cohort") not in ALLOWED_COHORTS:
        errors.append("INVALID_SOURCE_COHORT")

    missing = [k for k in P2_REQUIRED_VERIFICATION if p1_record.get(k) is not True]
    if missing:
        errors.append("P2_VERIFICATION_MISSING")

    # These fields are copied only when explicitly present. No customer intent is inferred.
    p2 = {
        "permanent_customer_id": p1_record.get("permanent_customer_id"),
        "source_cohort": p1_record.get("source_cohort"),
        "current_employment_verified": p1_record.get("current_employment_verified") is True,
        "company_direction_verified": p1_record.get("company_direction_verified") is True,
        "moved_or_left": p1_record.get("moved_or_left") is True,
        "explicit_stop_or_rejection": p1_record.get("explicit_stop_or_rejection") is True,
        "direct_inquiry": p1_record.get("direct_inquiry") is True,
        "purchase_history": p1_record.get("purchase_history") is True,
        "quote_history": p1_record.get("quote_history") is True,
        "one_way_sent_only": p1_record.get("one_way_sent_only") is True,
        "cc_only": p1_record.get("cc_only") is True,
        "old_ledger_note": p1_record.get("old_ledger_note") is True,
        "phone_allowed": p1_record.get("phone_allowed") is True,
        "prefers_material_before_call": p1_record.get("prefers_material_before_call") is True,
        "research_or_enterprise_customer": p1_record.get("research_or_enterprise_customer") is True,
    }

    return {
        "status": "PASS" if not errors else "HOLD",
        "errors": sorted(set(errors)),
        "missing_verification": missing,
        "p2_input": p2 if not errors else None,
        "external_send_executed": False,
    }


def run_fixtures():
    for cohort in sorted(ALLOWED_COHORTS):
        ready = {
            "db_state": "MAIN_DB",
            "permanent_customer_id": "C-001",
            "source_cohort": cohort,
            "current_employment_verified": True,
            "company_direction_verified": True,
            "direct_inquiry": True,
            "phone_allowed": True,
        }
        r = build_p2_input(ready)
        assert r["status"] == "PASS"
        assert r["p2_input"]["source_cohort"] == cohort
        assert r["p2_input"]["direct_inquiry"] is True

    missing = {
        "db_state": "MAIN_DB",
        "source_cohort": "NEW_ONLINE",
        "current_employment_verified": True,
    }
    r = build_p2_input(missing)
    assert r["status"] == "HOLD"
    assert "company_direction_verified" in r["missing_verification"]

    not_ready = {
        "db_state": "TRACKING_HOLD",
        "source_cohort": "NEW_ONLINE",
        "current_employment_verified": True,
        "company_direction_verified": True,
    }
    assert "P1_NOT_READY_FOR_P2" in build_p2_input(not_ready)["errors"]

    no_inference = {
        "db_state": "MAIN_DB",
        "source_cohort": "RECENT_TRADE",
        "current_employment_verified": True,
        "company_direction_verified": True,
    }
    r = build_p2_input(no_inference)
    assert r["status"] == "PASS"
    assert r["p2_input"]["direct_inquiry"] is False
    assert r["p2_input"]["purchase_history"] is False

    return "PASS: 6 deterministic P1->P2 handoff fixtures"


if __name__ == "__main__":
    print(run_fixtures())
