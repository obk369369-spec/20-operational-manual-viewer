"""Focused checks for honest before/after repair explanations."""
from CONTROL_TOWER.controller.universal_enforcement import enforce_record_isolation
from CONTROL_TOWER.controller.explain_record_repairs import explain_repairs


def test_explains_only_real_changes():
    before = [{"origin_file": "actual-input.xlsx", "origin_row": 2, "title": "  OK  "},
              {"origin_file": "actual-input.xlsx", "origin_row": 3, "title": ""}]
    def valid(row):
        return {"valid": bool(row["title"]) and row["title"] == row["title"].strip()}
    def repair(row):
        if row["origin_row"] == 2:
            row["title"] = row["title"].strip()
            return row
        return None
    gate = enforce_record_isolation(before, valid, repair, allowed_repair_fields={"title"})
    report = explain_repairs(before, gate, source_ref="actual-input.xlsx#sha256:pending",
                             rule_ref="approved-rule#sha256:pending")
    assert report["auto_repaired_count"] == 1
    assert report["unresolved_count"] == 1
    assert report["records"][0]["changes"][0]["before"] == "  OK  "
    assert report["records"][0]["changes"][0]["after"] == "OK"
    assert report["records"][1]["status"] == "수정하지 못해 분리"
    assert report["final_business_pass"] is False
    assert report["remote_readback_verified"] is False


def test_integrity_hold_is_not_certified():
    before = [{"origin_file": "input.xlsx", "origin_row": 1, "title": "A"}]
    gate = enforce_record_isolation(before, lambda row: False,
        lambda row: {**row, "origin_row": 2}, allowed_repair_fields={"title"})
    report = explain_repairs(before, gate, source_ref="input.xlsx", rule_ref="rule")
    assert report["status"] == "전체 확인 보류"
    assert report["final_business_pass"] is False
