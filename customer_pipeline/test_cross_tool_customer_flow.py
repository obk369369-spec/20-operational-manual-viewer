import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from cross_tool_customer_flow import adapt_tool41_to_tool7, run_actual_flow


def main():
    hold = adapt_tool41_to_tool7({"기관": "한국화학연구원", "성명": "김태호"}, {})
    assert hold["status"] == "HOLD"
    assert hold["reason"] == "TOOL041_VERIFIED_OUTPUT_MISSING"

    fixture = json.loads((ROOT / "fixtures" / "cross_tool_actual_kimtaeho_20260907.json").read_text(encoding="utf-8"))
    workspace = ROOT.parents[1]
    result = run_actual_flow(fixture, workspace / "41-wic-email-collection-master", workspace / "repo42")
    assert result["status"] == "CROSS_TOOL_INTEGRATION_PASS"
    assert result["dependency_order"] == ["TOOL041", "TOOL007", "TOOL042"]
    assert result["final_operational_status"] == "HOLD_EXTERNAL_CUSTOMER_EVIDENCE"
    assert all(result["checks"].values())
    print("PASS: missing-upstream fail-closed + actual TOOL041 -> TOOL007 -> TOOL042 contract")


if __name__ == "__main__":
    main()
