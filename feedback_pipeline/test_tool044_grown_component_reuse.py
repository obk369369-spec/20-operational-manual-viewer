import json
from pathlib import Path

from tool044_composition import lookup_verified_composition


root = Path(__file__).resolve().parent
demand = json.loads(
    (root / "fixtures" / "tool042_verified_html_toc_reuse_demand.json").read_text(encoding="utf-8")
)
result = lookup_verified_composition(root / "evidence" / "tool044_verified_composition_pool.json", demand)

assert result["result"] == "VERIFIED_COMPOSITION_DIRECT_REUSE"
assert result["selected_composition"] == "PROVENANCE_THEN_HTML2TEXT_THEN_MISTUNE_TOC_V1"
assert result["warehouse_hits"] == 1
assert result["parent_component_searches"] == 0
assert result["external_queries"] == 0
assert result["compositions_created"] == 0
print(json.dumps(result, ensure_ascii=False))
