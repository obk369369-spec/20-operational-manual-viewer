"""Deterministic P1 customer DB + send-order gate for WIC customer-response pipeline.
No network/send side effects. Normative rules remain in WIC_GLOBAL_OPERATING_RULES.md.
"""
from collections import Counter

REQUIRED = ("organization","department","person_name","title","actual_duty","email","official_contact","official_source_url","source_verified_at","source_cohort")
ALLOWED_COHORTS = {"NEW_ONLINE", "DORMANT_LEDGER", "RECENT_TRADE"}

# Historical locked send-order constraints recovered from WIC email-collection rules.
MIN_ORGANIZATIONS = 6
TARGET_ORGANIZATIONS = (8, 10)
MIN_ORG_GAP = 3
MIN_DEPT_GAP = 4
MIN_DOMAIN_GAP = 5
MAX_ORG_RATIO = 0.20


def dedupe_key(row):
    return tuple(str(row.get(k, "")).strip().casefold() for k in ("organization","person_name","email"))


def email_domain(row):
    email = str(row.get("email", "")).strip().casefold()
    return email.rsplit("@", 1)[1] if "@" in email else ""


def classify(row, existing_by_key=None):
    existing_by_key = existing_by_key or {}
    missing = [k for k in REQUIRED if not str(row.get(k, "")).strip()]
    if row.get("source_cohort") not in ALLOWED_COHORTS:
        missing.append("valid_source_cohort")
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


def _gap_violations(rows, field, min_gap, value_fn=None):
    value_fn = value_fn or (lambda r: str(r.get(field, "")).strip().casefold())
    last = {}
    violations = []
    for idx, row in enumerate(rows):
        value = value_fn(row)
        if not value:
            violations.append({"index": idx, "field": field, "error": "MISSING_VALUE"})
            continue
        if value in last and idx - last[value] < min_gap:
            violations.append({"index": idx, "previous_index": last[value], "field": field, "value": value, "error": f"MIN_GAP_{min_gap}_VIOLATION"})
        last[value] = idx
    return violations


def validate_send_order(rows):
    """Validate a proposed send-order table without sending anything.

    Row contents are never recombined; only ordering may change upstream.
    """
    if not rows:
        return {"status": "HOLD", "errors": ["EMPTY_SEND_TABLE"], "details": []}

    organizations = [str(r.get("organization", "")).strip() for r in rows if str(r.get("organization", "")).strip()]
    counts = Counter(organizations)
    unique_orgs = len(counts)
    details = []
    errors = []

    if unique_orgs < MIN_ORGANIZATIONS:
        errors.append("MIN_6_ORGANIZATIONS_NOT_MET")
        details.append({"unique_organizations": unique_orgs, "target": "8-10"})

    total = len(rows)
    for org, count in counts.items():
        ratio = count / total
        if ratio > MAX_ORG_RATIO:
            errors.append("ORGANIZATION_RATIO_OVER_20_PERCENT")
            details.append({"organization": org, "count": count, "total": total, "ratio": ratio})

    checks = [
        ("organization", MIN_ORG_GAP, None),
        ("department", MIN_DEPT_GAP, None),
        ("domain", MIN_DOMAIN_GAP, email_domain),
    ]
    for field, min_gap, fn in checks:
        violations = _gap_violations(rows, field, min_gap, value_fn=fn)
        if violations:
            errors.append(f"{field.upper()}_SPACING_VIOLATION")
            details.extend(violations)

    return {
        "status": "PASS" if not errors else "HOLD",
        "errors": sorted(set(errors)),
        "details": details,
        "unique_organizations": unique_orgs,
        "target_organizations": TARGET_ORGANIZATIONS,
        "external_send_executed": False,
    }


def run_fixtures():
    base = dict(organization="Org",department="R&D",person_name="Kim",title="Mgr",actual_duty="AI research",email="k@org.test",official_contact="02",official_source_url="https://org.test/staff",source_verified_at="2026-08-10",source_cohort="NEW_ONLINE",official_source_verified=True,actual_duty_verified=True,email_verified=True,permanent_customer_id="C-001")
    assert classify(base)["db_state"] == "MAIN_DB"
    x = dict(base); x["actual_duty"]=""; x["actual_duty_verified"]=False
    assert classify(x)["db_state"] == "TRACKING_HOLD"
    assert classify(base,{dedupe_key(base):"C-OLD"})["db_state"] == "UPDATE_EXISTING"
    bad_cohort = dict(base); bad_cohort["source_cohort"] = "UNKNOWN"
    assert classify(bad_cohort)["db_state"] == "TRACKING_HOLD"
    s = intro_card_action({"company_intro":{"status":"SENT"},"business_card":{"status":"SEND_READY"}})
    assert s["company_intro"]["next_action"] == "NO_BLIND_RESEND"
    assert s["business_card"]["next_action"] == "WAIT_EXPLICIT_SEND_AUTHORITY"
    assert s["external_send_executed"] is False

    # Valid 10-row mix: each organization/department/domain is unique.
    good = []
    for i in range(10):
        good.append({"organization":f"Org{i}", "department":f"Dept{i}", "email":f"p{i}@d{i}.test"})
    assert validate_send_order(good)["status"] == "PASS"

    # Same organization too soon.
    bad_org = list(good)
    bad_org[2] = dict(bad_org[2]); bad_org[2]["organization"] = bad_org[0]["organization"]
    assert "ORGANIZATION_SPACING_VIOLATION" in validate_send_order(bad_org)["errors"]

    # Same department too soon.
    bad_dept = list(good)
    bad_dept[3] = dict(bad_dept[3]); bad_dept[3]["department"] = bad_dept[0]["department"]
    assert "DEPARTMENT_SPACING_VIOLATION" in validate_send_order(bad_dept)["errors"]

    # Same domain too soon.
    bad_domain = list(good)
    bad_domain[4] = dict(bad_domain[4]); bad_domain[4]["email"] = "other@d0.test"
    assert "DOMAIN_SPACING_VIOLATION" in validate_send_order(bad_domain)["errors"]

    # Too few institutions must HOLD even when individual rows are otherwise usable.
    too_few = [{"organization":f"O{i%5}", "department":f"D{i}", "email":f"x{i}@z{i}.test"} for i in range(10)]
    assert "MIN_6_ORGANIZATIONS_NOT_MET" in validate_send_order(too_few)["errors"]

    return "PASS: 9 deterministic P1 fixtures"
