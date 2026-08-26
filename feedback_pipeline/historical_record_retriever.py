"""Tool-scoped Library + GitHub checkpoint retrieval without a full archive scan."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "historical_record_index.json"
REGISTRY = ROOT / "wic_target_registry.json"
ROOT_NAMES = {"chat_archive":"대화창 기록 모음", "important_chat_list":"중요한 대화 목록"}


def discover_roots() -> dict[str, Path]:
    roots: dict[str, Path] = {}
    if os.name != "nt":
        return roots
    for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
        drive = Path(f"{letter}:/")
        try:
            available = drive.exists()
        except OSError:
            available = False
        if not available:
            continue
        for alias, name in ROOT_NAMES.items():
            candidate = drive / name
            try:
                if candidate.is_dir():
                    roots[alias] = candidate
            except OSError:
                continue
    return roots


def retrieve(tool_id: str, roots: dict[str, Path] | None = None) -> dict[str, Any]:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if tool_id not in registry["targets"]:
        raise KeyError(f"canonical target not registered: {tool_id}")
    if tool_id not in index["tools"]:
        return {"tool_id":tool_id,"status":"HOLD_EVIDENCE","reason":"tool-scoped historical index not populated","user_input_required":False}
    row = index["tools"][tool_id]
    records = sorted(row["records"], key=lambda item:item["observed_at"], reverse=True)
    resolved_roots = roots if roots is not None else discover_roots()
    readback = []
    for record in records:
        alias = record["source_root_alias"]
        if alias not in resolved_roots:
            continue
        path = resolved_roots[alias] / record["relative_path"]
        if not path.is_file():
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        readback.append({"relative_path":record["relative_path"],"sha256_match":actual == record["sha256"],"size":path.stat().st_size})
    target = registry["targets"][tool_id]
    latest = records[0]
    work = next((item for item in records if item.get("last_work_point")), latest)
    return {
        "tool_id":tool_id,
        "status":"PASS",
        "scope":"TOOL_ONLY_NO_FULL_LIBRARY_SCAN",
        "latest_related_discussion":{"observed_at":latest["observed_at"],"source":latest["relative_path"],"summary":latest["summary"]},
        "last_actual_work_point":work.get("last_work_point","UNKNOWN"),
        "historical_records":records,
        "library_readback":readback,
        "github":{"repository":target["repository"],"latest_verified_commit":target["latest_verified_commit"],"master_paths":target["master_paths"],"checkpoint":target["latest_safe_checkpoint"]},
        "existing_status":row["status"],
        "user_manual_routing":0,
    }


def self_test() -> None:
    tool2 = retrieve("TOOL002")
    assert tool2["status"] == "PASS"
    assert tool2["latest_related_discussion"]["observed_at"].startswith("2026-04-12")
    assert tool2["last_actual_work_point"] == "기관별 누적검사기"
    assert tool2["github"]["latest_verified_commit"] == "9946e7ba59ac812d7f27e287a6abd6b3aba3e2b9"
    assert tool2["user_manual_routing"] == 0
    tool1 = retrieve("TOOL001", {})
    assert tool1["status"] == "PASS" and tool1["last_actual_work_point"].startswith("RUN23")
    assert retrieve("TOOL007", {})["status"] == "HOLD_EVIDENCE"
    print("PASS: TOOL002 actual indexed history + TOOL001 canonical reuse + scoped HOLD")


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument("--self-test",action="store_true");parser.add_argument("--tool",default="");parser.add_argument("--output",default="");args=parser.parse_args()
    if args.self_test:self_test();return
    result=retrieve(args.tool)
    text=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.output:Path(args.output).write_text(text,encoding="utf-8")
    print(text,end="")


if __name__=="__main__":main()
