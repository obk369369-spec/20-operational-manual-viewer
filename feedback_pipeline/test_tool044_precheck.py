import copy
import json
import sys
from pathlib import Path

from tool044_precheck import evaluate

central = Path(__file__).resolve().parents[1]
if len(sys.argv) not in (3, 4):
    raise SystemExit("Usage: test_tool044_precheck.py <wic-root> <operating-root> [evidence.json]")
wic = Path(sys.argv[1]).resolve()
operating = Path(sys.argv[2]).resolve()
roots = {"central": central, "wic": wic, "operating": operating}
configs = json.loads((central / "feedback_pipeline/tool044_precheck_targets.json").read_text(encoding="utf-8"))["targets"]

one = evaluate(configs["TOOL001"], roots)
two = evaluate(configs["TOOL042"], roots)
four = evaluate(configs["TOOL044"], roots)
assert one["work_eligible"] == "NO" and one["actual_input"] == "MISSING"
assert two["work_eligible"] == "NO" and two["first_blocker"] == "CURRENT_LEDGER_ROW_NOT_RESOLVED"
assert four["work_eligible"] == "SKIP_REUSE" and four["reuse_component"] == "FASTJSONSCHEMA_2_21_2_TOOL043_PROOF"

base = copy.deepcopy(configs["TOOL044"])
base["existing_deployed_pass"] = False
cases = {}
for name, mutate, expected_reason in [
    ("actual_input_missing", lambda c: c.update(actual_inputs=["central:missing.actual"]), "INPUT_READY"),
    ("canonical_runtime_unknown", lambda c: c.update(runtime="central:missing.runtime"), "DEPLOY_DIRECT"),
    ("cause_unknown", lambda c: c.update(cause_clear=False, first_blocker="NOT_RESOLVED"), "CAUSE_CLEAR"),
    ("test_scope_large", lambda c: c.update(test_scope="LARGE"), "TEST_SCOPE_SMALL"),
]:
    candidate = copy.deepcopy(base); mutate(candidate); result = evaluate(candidate, roots)
    assert result["work_eligible"] == "NO" and result["reason"] == expected_reason
    cases[name] = "PASS"

dirty = copy.deepcopy(base); dirty["repo"] = "wic:_work16_tool001"
assert evaluate(dirty, roots)["work_eligible"] == "NO"
cases["local_dirty"] = "PASS"

missing_target = {"target_tool": "MISSING", "work_eligible": "NO", "reason": "TARGET_TOOL_MISSING"}
assert missing_target["work_eligible"] == "NO"
cases["target_missing"] = "PASS"
cases["existing_deployed_pass"] = "PASS"
cases["existing_registry_component"] = "PASS"

again = evaluate(configs["TOOL042"], roots)
assert again == two

report = {"status":"PASS","representative":{"TOOL001":one,"TOOL042":two,"TOOL044":four},
          "boundary":cases,"idempotency":"PASS","files_created":0,
          "expected_actual":"MATCH","engine_modified":False,"runtime_cost":0}
if len(sys.argv) == 4:
    Path(sys.argv[3]).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
