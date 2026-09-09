"""Source-preserving feedback intake for TOOL016 -> TOOL044.

This bridge accepts an authenticated/local event, preserves the user's original
text, deduplicates an exact semantic root, and creates a TOOL044 request only
when a known atomic capability can be extracted without guessing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from tool044_request_router import route

HERE = Path(__file__).resolve().parent
CAPABILITY_RULES = {
    "리셀러": "RESELLER_DETECTION",
    "공식 상세페이지": "OFFICIAL_DETAIL_PAGE_VALIDATION",
    "공식 도메인": "OFFICIAL_DOMAIN_VALIDATION",
    "pdf 브로셔": "PDF_BROCHURE_CLASSIFICATION",
    "목차 계층": "TOC_HIERARCHY_VALIDATION",
    "한글 타이틀": "LOCAL_TITLE_TRANSLATION",
    "카테고리 자동": "CANONICAL_CATEGORY_MATCHING",
}
TOOL_ALIASES = {
    "엑셀 자동 업로드": "TOOL013", "온라인 고객 수집": "TOOL041",
    "매일 고객 안내": "TOOL042",
    "완성부품": "TOOL044", "관찰판": "TOOL043",
}


def read_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def infer_tool(text: str) -> str:
    """Infer only an explicit number or one unambiguous WIC term."""
    normalized = canonical(text)
    explicit = re.search(r"(?:tool\s*0*(\d{1,3})(?:\s*번)?|(?<!\d)(\d{1,3})\s*번)", normalized, re.I)
    if explicit:
        return f"TOOL{int(explicit.group(1) or explicit.group(2)):03d}"
    matches = {tool for phrase, tool in TOOL_ALIASES.items() if phrase in normalized}
    return next(iter(matches)) if len(matches) == 1 else "UNKNOWN"


def ingest(event: dict, root: Path = HERE) -> dict:
    for key in ("source_chat_or_tool", "user_original_text"):
        if not str(event.get(key, "")).strip():
            raise ValueError(f"missing required field: {key}")
    text = str(event["user_original_text"]).strip()
    source = str(event["source_chat_or_tool"]).strip()
    supplied_tool = str(event.get("tool_id", "")).strip().upper()
    inferred_tool = infer_tool(text)
    if supplied_tool and inferred_tool != "UNKNOWN" and supplied_tool != inferred_tool:
        tool = "UNKNOWN"
        tool_inference = "CONFLICT_HOLD"
    else:
        tool = supplied_tool or inferred_tool
        tool_inference = "EXPLICIT" if supplied_tool else ("INFERRED" if tool != "UNKNOWN" else "UNKNOWN_HOLD")
    if len(text) > 10000:
        raise ValueError("user_original_text exceeds 10000 characters")
    if not re.fullmatch(r"(?:TOOL\d{3}|CENTRAL|UNKNOWN|[A-Z0-9_-]{2,64})", tool):
        raise ValueError("invalid tool_id")
    occurred = str(event.get("timestamp") or datetime.now(timezone.utc).isoformat())
    root_id = "FB-" + hashlib.sha256(canonical(text).encode("utf-8")).hexdigest()[:16]
    source_id = "SRC-" + hashlib.sha256(f"{source}|{tool}|{occurred}|{text}".encode("utf-8")).hexdigest()[:16]
    explicit = [str(x).strip().upper() for x in event.get("missing_capabilities", []) if str(x).strip()]
    inferred = [cap for phrase, cap in CAPABILITY_RULES.items() if phrase in canonical(text)]
    capabilities = sorted(set(explicit + inferred))

    ledger_path = root / "tool016_feedback_intake_ledger.json"
    inbox_path = root / "TOOL044_REQUEST_INBOX.json"
    ledger = read_json(ledger_path, {"schema_version": 1, "roots": []})
    rows = ledger.setdefault("roots", [])
    existing = next((x for x in rows if x.get("root_id") == root_id), None)
    if existing:
        existing["occurrence"] = int(existing.get("occurrence", 1)) + 1
        if source_id not in existing.setdefault("source_ids", []):
            existing["source_ids"].append(source_id)
        existing.setdefault("sources", []).append({"source_id": source_id, "source": source,
                                                      "tool_id": tool, "timestamp": occurred,
                                                      "user_original_text": text})
        duplicate = True
    else:
        existing = {"root_id": root_id, "occurrence": 1, "source_ids": [source_id],
                    "sources": [{"source_id": source_id, "source": source, "tool_id": tool,
                                 "timestamp": occurred, "user_original_text": text}],
                    "current_resolution": "UNRESOLVED",
                    "missing_capabilities": capabilities}
        rows.append(existing)
        duplicate = False
    write_json(ledger_path, ledger)

    demand_id = None
    if capabilities:
        demand_id = f"{root_id}-" + "-".join(capabilities)
        inbox = read_json(inbox_path, {"schema_version": 1, "requests": []})
        requests = inbox.setdefault("requests", [])
        request = next((x for x in requests if x.get("request_id") == demand_id), None)
        source_record = {"source_id": source_id, "source_chat_or_tool": source, "tool_id": tool,
                         "user_original_text": text, "timestamp": occurred, "root_id": root_id}
        if request:
            if source_id not in {x.get("source_id") for x in request.setdefault("source_records", [])}:
                request["source_records"].append(source_record)
        else:
            requests.append({"request_id": demand_id, "tool_or_program_name": tool,
                             "related_tool": tool, "purpose": text, "desired_result": text,
                             "required_capabilities": capabilities, "priority": "HIGH",
                             "status": "OPEN", "user_action": "NONE", "created_at": occurred,
                             "root_id": root_id, "source_chat_or_tool": source,
                             "function_id": demand_id, "original_error_or_feedback": text,
                             "occurrence_or_evidence": existing["occurrence"],
                             "source_evidence": [source_id], "source_records": [source_record]})
        write_json(inbox_path, inbox)
        route(inbox_path, root / "tool044_atomic_demand_queue.json",
              root / "tool044_function_state.json")
    return {"status": "RECEIVED", "source_id": source_id, "root_id": root_id,
            "tool_id": tool, "tool_inference": tool_inference,
            "duplicate": duplicate, "occurrence": existing["occurrence"],
            "missing_capabilities": capabilities, "tool044_demand_id": demand_id,
            "tool016_status": "ROOT_CHECK_COMPLETE",
            "tool044_status": "DEMAND_READY" if demand_id else "TOOL016_REVIEW_REQUIRED"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("event", help="feedback event JSON file")
    parser.add_argument("--root", default=str(HERE))
    args = parser.parse_args()
    event = read_json(Path(args.event), None)
    print(json.dumps(ingest(event, Path(args.root)), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
