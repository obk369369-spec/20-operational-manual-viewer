from __future__ import annotations

import copy
import argparse
import json
import tempfile
from pathlib import Path

from tool044_local_first import HANDOFF_FIELDS, route, validate_work_result


def touch(path: Path, text="x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture(root: Path):
    for name in ("master", "checkpoint", "runtime", "input"):
        touch(root / name)
    (root / "use").mkdir()
    # A non-repository is intentionally used; existing-pass exits before git state matters.
    return {
        "tool": "TOOL044", "function": "PROOF", "master": "central:master",
        "checkpoint": "central:checkpoint", "runtime": "central:runtime",
        "actual_use_folder": "operating:use", "repo": "central:",
        "actual_inputs": ["central:input"], "cause_clear": True,
        "first_blocker": "NONE", "test_scope": "SMALL", "deploy_direct": True,
        "deployed_pass_confident": True, "repeat_failure": False,
        "external_blocker": False, "user_actions": [], "existing_deployed_pass": True,
        "reuse_component": "fastjsonschema-2.21.2",
    }, {"central": root, "wic": root, "operating": root}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        base, roots = fixture(root)
        case1 = route(base, roots)
        assert case1["execution_mode"] == "LOCAL" and case1["work_handoff_required"] == "NO"
        assert case1["local_result"] == "SKIP_REUSE"

        missing = copy.deepcopy(base); missing.update(tool="TOOL001", existing_deployed_pass=False,
            reuse_component=None, actual_inputs=["central:missing"], external_blocker=True,
            first_blocker="VERIFIED_REPORT_PAYLOAD_NOT_READY")
        case2 = route(missing, roots)
        assert case2["work_handoff_required"] == "NO" and case2["local_result"] == "HOLD_EXTERNAL"

        ledger = copy.deepcopy(base); ledger.update(tool="TOOL042", existing_deployed_pass=False,
            reuse_component=None, deploy_direct=False, deployed_pass_confident=False,
            first_blocker="CURRENT_LEDGER_ROW_NOT_RESOLVED")
        case3 = route(ledger, roots)
        assert case3["work_handoff_required"] == "NO" and case3["work_reason"] == "CURRENT_LEDGER_ROW_NOT_RESOLVED"

        # Simulate a clean precheck only to test the judgment boundary, without external search.
        new = copy.deepcopy(base); new["requires_new_judgment"] = True
        new["why_work_required"] = "NEW_COMPONENT_SUITABILITY_JUDGMENT"
        new["existing_deployed_pass"] = False
        import tool044_local_first
        original = tool044_local_first.evaluate
        tool044_local_first.evaluate = lambda c, r: {
            "target_tool":"TOOL099", "target_function":"NEW_COMPONENT", "work_eligible":"YES",
            "first_blocker":"NEW_JUDGMENT", "reuse_component":"NONE",
            "handoff":{"TARGET_TOOL":"TOOL099","TARGET_FUNCTION":"NEW_COMPONENT",
            "ACTUAL_INPUT_PATH":[str(root/'input')],"CANONICAL_RUNTIME_PATH":str(root/'runtime'),
            "ACTUAL_USE_FOLDER":str(root/'use'),"CURRENT_SAFE_CHECKPOINT":str(root/'checkpoint'),
            "CURRENT_GITHUB_STATE":"CLEAN_MATCH","KNOWN_BLOCKER":"NEW_JUDGMENT"}}
        case4 = route(new, roots)
        tool044_local_first.evaluate = original
        assert case4["work_handoff_required"] == "YES" and case4["execution_mode"] == "WORK_REQUIRED"
        assert tuple(case4["handoff"].keys()) == HANDOFF_FIELDS

        boundaries = {}
        variants = {
            "missing_input": dict(existing_deployed_pass=False, actual_inputs=["central:none"]),
            "unknown_runtime": dict(existing_deployed_pass=False, runtime="central:none"),
            "unknown_cause": dict(existing_deployed_pass=False, cause_clear=False),
            "large_scope": dict(existing_deployed_pass=False, test_scope="LARGE"),
            "repeat": dict(existing_deployed_pass=False, repeat_failure=True),
        }
        for name, changes in variants.items():
            c = copy.deepcopy(base); c.update(changes)
            got = route(c, roots); boundaries[name] = got["local_result"]
            assert got["work_handoff_required"] == "NO"
        missing_target = route({}, roots)
        assert missing_target["work_handoff_required"] == "NO"
        boundaries["missing_target"] = missing_target["local_result"]
        original = tool044_local_first.evaluate
        tool044_local_first.evaluate = lambda c, r: {
            "target_tool":"TOOL099", "target_function":"DIRTY", "work_eligible":"NO",
            "first_blocker":"LOCAL_DIRTY", "reason":"LOCAL_REMOTE_CLEAN"}
        dirty = route(base, roots)
        tool044_local_first.evaluate = original
        assert dirty["work_handoff_required"] == "NO"
        boundaries["local_dirty"] = dirty["local_result"]
        invalid = {key: key for key in ("WORK_DECISION","SELECTED_COMPONENT","SOURCE","VERSION","LICENSE",
                   "UNMODIFIED_USE","EXPECTED_CONTRACT","INTEGRATION_TARGET")}
        invalid["UNMODIFIED_USE"] = True
        assert validate_work_result(invalid)
        assert not validate_work_result({})
        assert route(base, roots) == route(base, roots)
        result = {"CASE-1":case1,"CASE-2":case2,"CASE-3":case3,
                  "CASE-4":case4,"boundaries":boundaries,
                  "idempotency":"PASS","work_result_contract":"PASS"}
        if args.evidence:
            args.evidence.parent.mkdir(parents=True, exist_ok=True)
            args.evidence.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
