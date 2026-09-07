from pathlib import Path
from tool044_composition import test_url_provenance_composition

root = Path(__file__).resolve().parent
result = test_url_provenance_composition(
    root / "external_candidate_pool" / "validators-0.35.0-py3-none-any.whl",
    root / "fixtures" / "tool042_customer_branch_actual_kmg.json",
)
assert result["status"] == "VERIFIED_COMPOSITION"
assert all(result["tests"].values())
print("5/5 PASS", result["composition_id"])
