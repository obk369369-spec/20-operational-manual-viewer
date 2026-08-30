"""TOOL035 verified-component integration gate."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "tool035_verified_integration.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")

def validate(manifest: dict) -> dict:
    if manifest.get("schema_version") != 1 or manifest.get("policy") != "VERIFIED_COMPONENTS_ONLY":
        raise ValueError("invalid TOOL035 manifest contract")
    ready = []
    holds = []
    for component in manifest.get("components", []):
        required = ("source_tool","source_repository","reusable_scope","reusable_scope_status","runtime_commit","runtime_blob","master_commit","master_blob","remote_read_back","capabilities")
        missing = [key for key in required if key not in component]
        if missing:
            raise ValueError(f"{component.get('source_tool','UNKNOWN')} missing {missing}")
        verified = (
            component["reusable_scope_status"] == "PASS"
            and component["remote_read_back"] is True
            and all(SHA40.fullmatch(str(component[key])) for key in ("runtime_commit","runtime_blob","master_commit","master_blob"))
            and bool(component["capabilities"])
        )
        if not verified:
            holds.append({"source_tool":component["source_tool"],"reason":"UNVERIFIED_COMPONENT_BLOCKED"})
            continue
        ready.append({
            "source_tool":component["source_tool"],
            "reusable_scope":component["reusable_scope"],
            "capabilities":component["capabilities"],
            "runtime_commit":component["runtime_commit"],
            "source_tool_state":component.get("source_tool_state"),
        })
        for reason in component.get("holds", []):
            holds.append({"source_tool":component["source_tool"],"reason":reason})
    if not ready:
        raise ValueError("no verified component available")
    return {
        "result":"PASS",
        "target":"TOOL035",
        "ready_components":ready,
        "preserved_holds":holds,
        "shell_integration":False,
        "auto_live_deploy":False,
        "work_entry_allowed":True,
    }

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--first-validation",action="store_true")
    args=parser.parse_args()
    if not args.first_validation:
        raise SystemExit("use --first-validation")
    print(json.dumps(validate(json.loads(MANIFEST.read_text(encoding="utf-8"))),ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
