import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import tool044_atomic_watch
from tool044_atomic_watch import run_cycle

root = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as directory:
    state = Path(directory) / "state.json"
    when = datetime(2026, 9, 7, 0, 0, tzinfo=timezone.utc)
    first = run_cycle(root / "tool044_atomic_demand_queue.json", root / "VERIFIED_COMPONENT_REGISTRY.json", state, when)
    assert first["demands_processed"] == 7
    assert first["production_mutations"] == 0 and first["paid_api_calls"] == 0
    by_id = {item["demand_id"]: item for item in first["results"]}
    assert by_id["T42-PROVENANCE-VALIDATION"]["result"] == "READY_ATOMIC_COMPONENT_FOUND"
    assert by_id["T42-OFFICIAL-PUBLISHER-VALIDATION"]["result"] == "PARTIAL_ATOMIC_COMPONENT_SET"
    assert by_id["T42-RESELLER-DETECTION"]["result"] == "NO_READY_ATOMIC_COMPONENT"
    second = run_cycle(root / "tool044_atomic_demand_queue.json", root / "VERIFIED_COMPONENT_REGISTRY.json", state, when)
    assert second["duplicate_searches_blocked"] == 7
    assert not (Path(directory) / "tool044_verified_external_component_pool.json").exists()

with tempfile.TemporaryDirectory() as directory:
    temp = Path(directory)
    queue = temp / "queue.json"
    registry = temp / "registry.json"
    queue.write_text(json.dumps({"demands":[{"demand_id":"X","atomic_capabilities":["URL_VALIDATION"],"official_candidates":[{"capability":"URL_VALIDATION"}]}]}), encoding="utf-8")
    registry.write_text(json.dumps({"verified_atomic_component_pool":[]}), encoding="utf-8")
    original = tool044_atomic_watch.harvest_pypi
    tool044_atomic_watch.harvest_pypi = lambda candidate, artifact_dir: {"status":"VERIFIED_REUSABLE","component_id":"FAKE_VERIFIED","atomic_capability":"URL_VALIDATION"}
    try:
        external = run_cycle(queue, registry, temp / "state.json", when, external=True)
    finally:
        tool044_atomic_watch.harvest_pypi = original
    assert external["external_sources_queried"] == 1
    assert json.loads((temp / "tool044_verified_external_component_pool.json").read_text())["components"][0]["component_id"] == "FAKE_VERIFIED"
print(json.dumps({"status":"PASS","demands":7,"duplicate_searches_blocked":7,"cost":0}))
