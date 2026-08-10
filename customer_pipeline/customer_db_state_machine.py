"""Deterministic P1 customer DB gate for WIC customer-response pipeline.
No network/send side effects. Normative rules remain in WIC_GLOBAL_OPERATING_RULES.md.
"""
REQUIRED = ("organization","department","person_name","title","actual_duty","email","official_contact","official_source_url","source_verified_at","source_cohort")


def dedupe_key(row):
    return tuple(str(row.get(k, "")).strip().casefold() for k in ("organization","person_name","email"))


def classify(row, existing_by_key=None):
    existing_by_key = existing_by_key or {}
    missing = [k for k in REQUIRED if not str(row.get(k, "")).strip()]
    if not row.get("official_source_verified", False):
        missing.append("official_source_verified")
    if not row.get("actual_duty_verified", False):
        missing.append("actual_duty_verified")
    if not row.get("email_verified", False):
        missing.append("email_verified")
    key = dedupe_key(row)
    if key in existing_by_key:
        return {"db_state":"UPDATE_EXISTING","permanent_customer_id":existing_by_key[key],"dedupe_key":key,"missing":missing}
    if missing:
        return {"db_state":"TRACKING_HOLD","permanent_customer_id":None,"dedupe_key":key,"missing":sorted(set(missing))}
    cid = row.get("permanent_customer_id")
    if not cid:
        return {"db_state":"MAIN_DB_PENDING_ID","permanent_customer_id":None,"dedupe_key":key,"missing":["permanent_customer_id_assignment"]}
    return {"db_state":"MAIN_DB","permanent_customer_id":cid,"dedupe_key":key,"missing":[]}


def intro_card_action(state):
    """Prepare state only; never sends external outreach."""
    intro = state.get("company_intro", {})
    card = state.get("business_card", {})
    for item in (intro, card):
        if item.get("status") == "SENT" and not item.get("resend_reason"):
            item["next_action"] = "NO_BLIND_RESEND"
        elif item.get("status") == "SEND_READY":
            item["next_action"] = "WAIT_EXPLICIT_SEND_AUTHORITY"
        else:
            item["next_action"] = "NO_SEND"
    return {"company_intro":intro,"business_card":card,"external_send_executed":False}


def run_fixtures():
    base = dict(organization="Org",department="R&D",person_name="Kim",title="Mgr",actual_duty="AI research",email="k@org.test",official_contact="02",official_source_url="https://org.test/staff",source_verified_at="2026-08-10",source_cohort="NEW_ONLINE",official_source_verified=True,actual_duty_verified=True,email_verified=True,permanent_customer_id="C-001")
    assert classify(base)["db_state"] == "MAIN_DB"
    x = dict(base); x["actual_duty"]=""; x["actual_duty_verified"]=False
    assert classify(x)["db_state"] == "TRACKING_HOLD"
    assert classify(base,{dedupe_key(base):"C-OLD"})["db_state"] == "UPDATE_EXISTING"
    s = intro_card_action({"company_intro":{"status":"SENT"},"business_card":{"status":"SEND_READY"}})
    assert s["company_intro"]["next_action"] == "NO_BLIND_RESEND"
    assert s["business_card"]["next_action"] == "WAIT_EXPLICIT_SEND_AUTHORITY"
    assert s["external_send_executed"] is False
    return "PASS: 4 deterministic P1 fixtures"
