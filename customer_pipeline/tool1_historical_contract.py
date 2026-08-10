"""Tool1 historical contract recovered from user-approved development records.
This is a deterministic regression contract, not a replacement UI.
"""

FIXED_INPUT_FIELDS = (
    "title_en", "title_ko", "publisher", "publication_date", "pages",
    "list_price", "supply_price", "report_link", "toc",
)

RIGHT_SLOT_MAP = {
    "title_en": "TITLE.EN",
    "publisher": "META.PUBLISHER",
    "publication_date": "META.DATE",
    "pages": "META.PAGES",
    "list_price": "META.PRICE",
    "report_link": "LINK.TEXT",
    "toc": "TOC.TEXT",
}

FORBIDDEN_SCOPE_CHANGES = (
    "rebuild_right_guide",
    "new_html_structure",
    "replace_stable_baseline",
    "unrequested_feature",
)


def validate_left_contract(fields, button_count):
    missing = [f for f in FIXED_INPUT_FIELDS if f not in fields]
    extras = [f for f in fields if f not in FIXED_INPUT_FIELDS]
    if missing or extras or button_count != 1:
        return {
            "state": "FAIL",
            "error_hash": "TOOL001_LEFT_9_FIELDS_ONE_BUTTON_CONTRACT",
            "missing": missing,
            "extras": extras,
            "button_count": button_count,
        }
    return {"state": "PASS", "missing": [], "extras": [], "button_count": 1}


def validate_slot_mapping(mapping):
    wrong = {k: mapping.get(k) for k, v in RIGHT_SLOT_MAP.items() if mapping.get(k) != v}
    if wrong:
        return {"state": "FAIL", "error_hash": "TOOL001_RIGHT_SLOT_MAPPING_MISMATCH", "wrong": wrong}
    return {"state": "PASS", "wrong": {}}


def validate_scope(changes):
    hits = [x for x in changes if x in FORBIDDEN_SCOPE_CHANGES]
    return {
        "state": "FAIL" if hits else "PASS",
        "error_hash": "TOOL001_STABLE_BASELINE_SCOPE_VIOLATION" if hits else None,
        "hits": hits,
    }


def validate_render_probe(middle, right, mutation_log):
    middle_missing = [k for k, v in middle.items() if v in (None, "")]
    right_missing = [k for k, v in right.items() if v in (None, "", "__MISSING__")]
    if middle_missing or right_missing:
        return {
            "state": "FAIL",
            "error_hash": "THREE_AREA_VALUE_GAP",
            "middle_missing": middle_missing,
            "right_missing": right_missing,
            "last_mutation_target": mutation_log[-1]["target_id"] if mutation_log else "",
        }
    return {"state": "PASS", "middle_missing": [], "right_missing": [], "last_mutation_target": ""}


def run_fixtures():
    assert validate_left_contract(list(FIXED_INPUT_FIELDS), 1)["state"] == "PASS"
    bad = validate_left_contract(list(FIXED_INPUT_FIELDS) + ["extra_option"], 2)
    assert bad["state"] == "FAIL"
    assert bad["error_hash"] == "TOOL001_LEFT_9_FIELDS_ONE_BUTTON_CONTRACT"

    assert validate_slot_mapping(dict(RIGHT_SLOT_MAP))["state"] == "PASS"
    wrong = dict(RIGHT_SLOT_MAP); wrong["publication_date"] = "guideDateWrong"
    assert validate_slot_mapping(wrong)["error_hash"] == "TOOL001_RIGHT_SLOT_MAPPING_MISMATCH"

    assert validate_scope(["connect_left_to_existing_right"])["state"] == "PASS"
    assert validate_scope(["new_html_structure"])["error_hash"] == "TOOL001_STABLE_BASELINE_SCOPE_VIOLATION"

    middle = {"title": "A", "date": "2026-08"}
    right = {"guideTitle": "A", "guideDate": "2026-08", "guideLink": "https://publisher.example/r"}
    assert validate_render_probe(middle, right, [])["state"] == "PASS"
    right["guideDate"] = ""
    gap = validate_render_probe(middle, right, [{"target_id": "guideDate"}])
    assert gap["state"] == "FAIL"
    assert gap["error_hash"] == "THREE_AREA_VALUE_GAP"
    assert gap["last_mutation_target"] == "guideDate"

    return "PASS: 8 deterministic Tool1 historical-contract fixtures"


if __name__ == "__main__":
    print(run_fixtures())
