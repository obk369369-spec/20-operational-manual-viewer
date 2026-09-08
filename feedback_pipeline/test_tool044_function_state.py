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
assert result["observer_labels"]["REPEATED_ERROR"] == "고질 오류"
print("PASS: verified reuse, partial assembly, external demand, HOLD fail-closed, observer contract")
