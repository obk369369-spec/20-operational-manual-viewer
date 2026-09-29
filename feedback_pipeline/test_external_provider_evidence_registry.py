import json
from pathlib import Path

here = Path(__file__).resolve().parent
registry = json.loads((here / "tool044_multi_gate_adapters.json").read_text(encoding="utf-8"))
actual = [row for row in registry["providers"] if row["status"] == "ACTUAL_RUN_PASS"]
assert {row["provider"] for row in actual} == {"GitHub Actions", "CircleCI Cloud", "Deno Deploy"}
assert len({row["provider"] for row in actual}) == 3
for row in actual:
    assert row["actual_test_evidence"] and row["result_return"]
roundtrip = json.loads((here / "evidence/root_a_env1_env2_roundtrip.json").read_text())
failover = json.loads((here / "evidence/root_a_minimum_failover.json").read_text())
assert roundtrip["circleci_state"] == "success" and roundtrip["env1_env2_minimum_roundtrip"] == "PASS"
assert failover["root_a_final_status"] == "PASS" and failover["post_failure_result_return"] == "PASS"
assert failover["checkpoint_resume"] == "PASS" and failover["final_readback"] == "PASS"
print("EXTERNAL_PROVIDER_EVIDENCE_REGISTRY: PASS (10/10)")
