from pathlib import Path

from tool044_composition import test_html_toc_composition


root = Path(__file__).resolve().parent
result = test_html_toc_composition(
    root / "external_candidate_pool" / "html2text-2025.4.15-py3-none-any.whl",
    root / "external_candidate_pool" / "mistune-3.3.4-py3-none-any.whl",
    root / "fixtures" / "tool042_html_toc_normal.json",
    root / "fixtures" / "tool042_html_toc_failure.json",
)

assert result["status"] == "VERIFIED_COMPOSITION"
assert result["expected_actual"] == "MATCH"
assert all(result["tests"].values())
print("7/7 PASS", result["composition_id"])
