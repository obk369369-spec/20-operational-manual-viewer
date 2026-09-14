import tempfile
from pathlib import Path
from tool044_function_state import build

result = build(Path(__file__).resolve().parent)
rows = {row["FUNCTION_ID"]: row for row in result["functions"]}
assert rows["TOOL013-CANONICAL-RUNTIME"]["CURRENT_STATUS"] == "IMPROVED_VERIFIED"
assert rows["TOOL013-CANONICAL-RUNTIME"]["ACTION"] == "SKIP_REUSE"
assert rows["T42-WEBPAGE-TEXT-EXTRACTION"]["CURRENT_STATUS"] == "IMPROVED_PARTIAL"
assert rows["T42-WEBPAGE-TEXT-EXTRACTION"]["TOOL044_SEARCH_REQUIRED"] is False
assert rows["T42-RESELLER-DETECTION"]["CURRENT_STATUS"] == "MISSING_CAPABILITY"
assert rows["T42-RESELLER-DETECTION"]["TOOL044_SEARCH_REQUIRED"] is True
assert rows["HOLD-T1-VERIFIED-REPORT-ACQUISITION"]["CURRENT_STATUS"] == "HOLD"
assert rows["HOLD-T1-VERIFIED-REPORT-ACQUISITION"]["TOOL044_SEARCH_REQUIRED"] is False
for function_id in ("CI-REGISTRY-STAGING-STATUS", "TOOL044-PRODUCTION-TOOL043-PROOF-CONTRACT"):
    assert rows[function_id]["CURRENT_STATUS"] == "IMPROVED_VERIFIED"
    assert rows[function_id]["ACTION"] == "SKIP_REUSE"
    assert rows[function_id]["TOOL044_SEARCH_REQUIRED"] is False
    assert rows[function_id]["REMAINING_ERROR"] is None
assert rows["TOOL043-CANONICAL-RUNTIME"]["CURRENT_STATUS"] == "IMPROVED_VERIFIED"
assert rows["TOOL043-CANONICAL-RUNTIME"]["ACTION"] == "SKIP_REUSE"
assert rows["TOOL043-CANONICAL-RUNTIME"]["TOOL044_SEARCH_REQUIRED"] is False
assert rows["TOOL043-CANONICAL-RUNTIME"]["REMAINING_ERROR"] is None
for function_id in ("TOOL002-CANONICAL-RUNTIME", "TOOL020-CANONICAL-RUNTIME"):
    assert rows[function_id]["CURRENT_STATUS"] == "IMPROVED_VERIFIED"
    assert rows[function_id]["ACTION"] == "SKIP_REUSE"
    assert rows[function_id]["TOOL044_SEARCH_REQUIRED"] is False
    assert rows[function_id]["REMAINING_ERROR"] is None
assert result["residual_ledger"]["READY_FOR_PHYSICAL_EXECUTION"] == []
assert "WIC-0702-SCOPED-RECOVERY" in result["residual_ledger"]["NEEDS_CHAT_DECISION"]
assert "T42-RESELLER-DETECTION" in result["residual_ledger"]["MISSING_CAPABILITY"]
assert "TOOL043-CANONICAL-RUNTIME" in result["residual_ledger"]["VERIFIED_REUSE"]
actual_counts = {
    status: sum(row["CURRENT_STATUS"] == status for row in result["functions"])
    for status in result["classification_counts"]
}
assert result["classification_counts"] == actual_counts
assert result["observer_labels"]["REPEATED_ERROR"] == "고질 오류"
print("PASS: verified reuse, partial assembly, external demand, HOLD fail-closed, observer contract")
