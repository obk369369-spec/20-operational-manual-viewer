from pathlib import Path
from tool044_composition import test_url_provenance_composition, validate_official_detail_page, extract_webpage_text_and_toc

root = Path(__file__).resolve().parent
result = test_url_provenance_composition(
    root / "external_candidate_pool" / "validators-0.35.0-py3-none-any.whl",
    root / "fixtures" / "tool042_customer_branch_actual_kmg.json",
)
assert result["status"] == "VERIFIED_COMPOSITION"
assert all(result["tests"].values())
print("5/5 PASS", result["composition_id"])

actual = "https://www.kiro.re.kr/enjoy/report.asp?GTXT=&SFIELD=&bcat=&bgbn=R&bidx=5537&gbn=R06&page=1"
assert validate_official_detail_page(actual, ["kiro.re.kr"], ["bidx"])["status"] == "VERIFIED_OFFICIAL_DETAIL_PAGE"
assert validate_official_detail_page("https://www.kiro.re.kr/", ["kiro.re.kr"], ["bidx"])["status"] == "HOLD_NOT_DETAIL_PAGE"
assert validate_official_detail_page("https://kiro.example/report?bidx=5537", ["kiro.re.kr"], ["bidx"])["status"] == "HOLD_NOT_OFFICIAL_DOMAIN"
print("3/3 PASS OFFICIAL_DETAIL_PAGE_VALIDATION")

sample = "<html><body><h1>Annual Report</h1><h2>Overview</h2><p>Verified actual content.</p></body></html>"
structured = extract_webpage_text_and_toc(sample)
assert structured["status"] == "VERIFIED_WEBPAGE_TEXT_AND_TOC"
assert structured["heading_count"] == 2
assert extract_webpage_text_and_toc("<html></html>")["status"] == "HOLD_EMPTY_TEXT"
print("3/3 PASS WEBPAGE_TEXT_AND_TOC_COMPOSITION")
