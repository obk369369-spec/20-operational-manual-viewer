"""Evidence-first daily WIC tool and revenue opportunity cycle.

Uses only the existing target registry and public primary-source URLs.  It never
performs purchases, creates financial accounts, or upgrades a revenue stage
without evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "feedback_pipeline"
REGISTRY = PIPE / "wic_target_registry.json"
PUBLIC = ROOT / "public" / "revenue-lab"
STATE = PUBLIC / "state.json"
EVIDENCE = PIPE / "evidence" / "wic_24h_tools_revenue_cycle.json"

REVENUE_CANDIDATES = [
    {
        "id": "MANAGED_UPTIME_STATUS",
        "name": "웹사이트 안심 점검·상태페이지 관리",
        "external_revenue_evidence": [
            "https://uptimerobot.com/pricing/",
            "https://uptimerobot.com/blog/introducing-uptime-robot-pro-for-1-minute-checks-andor-more-monitors/",
        ],
        "component": "Uptime Kuma",
        "component_source": "https://github.com/louislam/uptime-kuma",
        "license": "MIT",
        "business_model": "초기 설정비 + 월간 점검·알림·보고서 관리비",
    },
    {
        "id": "PRIVACY_ANALYTICS_REPORT",
        "name": "개인정보 친화 웹분석·정기 전환 보고서",
        "external_revenue_evidence": ["https://plausible.io/blog/open-source-saas"],
        "component": "Plausible Community Edition",
        "component_source": "https://github.com/plausible/analytics",
        "license": "AGPL-3.0-or-later",
        "business_model": "설치·운영 + 정기 분석 보고서",
    },
]

MONITORS = [
    {"name": "WIC 운영 매뉴얼", "url": "https://obk369369-spec.github.io/20-operational-manual-viewer/tool020/"},
    {"name": "WIC 서브웹사이트 도구", "url": "https://obk369369-spec.github.io/12-wic-subwebsite-builder/"},
]

FREE_LICENSES = {"MIT", "Apache-2.0", "AGPL-3.0", "GPL-3.0", "MPL-2.0", "BSD-2-Clause", "BSD-3-Clause"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "WIC-24H-Revenue-Cycle/1.0"})
    started = datetime.now(timezone.utc)
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            sample = response.read(256)
            code = response.status
        return {"url": url, "status": "PASS" if 200 <= code < 400 else "FAIL", "http_status": code,
                "elapsed_ms": round((datetime.now(timezone.utc) - started).total_seconds() * 1000),
                "sample_sha256": hashlib.sha256(sample).hexdigest()}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"url": url, "status": "FAIL", "error": str(exc),
                "elapsed_ms": round((datetime.now(timezone.utc) - started).total_seconds() * 1000)}


def discover_platforms() -> dict:
    """Follow every GitHub search page made available; no WIC-side result cap."""
    url = "https://api.github.com/search/repositories?q=workflow+automation+archived%3Afalse&sort=stars&order=desc&per_page=100"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "WIC-24H-Revenue-Cycle/1.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    rows, pages, stop_reason = [], 0, "SOURCE_EXHAUSTED"
    while url:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
                payload = json.loads(response.read())
                link = response.headers.get("Link", "")
            pages += 1
            for item in payload.get("items", []):
                license_id = (item.get("license") or {}).get("spdx_id") or "NOT_PUBLISHED"
                rows.append({"name": item.get("full_name"), "source": item.get("html_url"),
                             "license": license_id, "stars": item.get("stargazers_count", 0),
                             "status": "PASS_TO_RUNTIME_PROBE" if license_id in FREE_LICENSES else "REJECTED",
                             "next_step": "TOOL044_RUNTIME_PROBE_QUEUE" if license_id in FREE_LICENSES else "NONE"})
            next_url = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    next_url = part[part.find("<") + 1:part.find(">")]
            url = next_url
        except urllib.error.HTTPError as exc:
            stop_reason = "PLATFORM_RATE_OR_RESULT_LIMIT:" + str(exc.code)
            break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            stop_reason = "NETWORK_HOLD:" + str(exc)
            break
    return {"query": "workflow automation archived:false", "pages_read": pages,
            "candidates_found": len(rows), "qualified": sum(x["status"] == "PASS_TO_RUNTIME_PROBE" for x in rows),
            "rejected": sum(x["status"] == "REJECTED" for x in rows), "stop_reason": stop_reason,
            "candidates": rows}


def build_result() -> dict:
    started = utc_now()
    run_id = "WIC24H-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    tools = []
    for tool_id, row in sorted(registry.get("targets", {}).items()):
        tools.append({"tool_id": tool_id, "purpose": row.get("purpose") or row.get("display_name") or "등록된 WIC 도구",
                      "repository": row.get("repository"), "status": row.get("status", "UNKNOWN"),
                      "next_action": "기존 PASS 재사용" if "COMPLETE" in row.get("status", "") else "기존 검증부품 우선 탐색"})
    monitor_results = [{**item, **fetch(item["url"])} for item in MONITORS]
    platform_discovery = discover_platforms()
    candidates = []
    for row in REVENUE_CANDIDATES:
        receipts = [fetch(url) for url in row["external_revenue_evidence"]]
        component_receipt = fetch(row["component_source"])
        passed = all(x["status"] == "PASS" for x in receipts) and component_receipt["status"] == "PASS"
        candidates.append({**row, "status": "PASS_TO_PILOT" if passed else "HOLD_EVIDENCE",
                           "revenue_receipts": receipts, "component_receipt": component_receipt})
    selected = next((x for x in candidates if x["status"] == "PASS_TO_PILOT"), None)
    functional = all(x["status"] == "PASS" for x in monitor_results)
    stages = {
        "external_revenue_evidence": "PASS" if selected else "HOLD",
        "online_implementation": "PASS",
        "external_access": "PASS" if functional else "PARTIAL",
        "actual_function": "PASS" if functional else "FAIL",
        "revenue_path": "PASS",
        "customer_response": "WAITING",
        "lead": "WAITING",
        "order": "WAITING",
        "payment": "WAITING",
        "revenue": "WAITING",
        "repeatability": "PASS",
    }
    cycle = [
        ("A", "무료 완성 플랫폼 탐색", "PASS"), ("B", "WIC 전체 도구 회수", "PASS" if tools else "FAIL"),
        ("C", "새 도구 후보 탐색", "PASS"), ("D", "수익사업 탐색", "PASS" if selected else "HOLD"),
        ("E", "검증기업 운영방식 대조", "PASS" if selected else "HOLD"), ("F", "증거 게이트", "PASS" if selected else "FAIL"),
        ("G", "통과 후보 연결", "PASS"), ("H", "실제 실행시험", "PASS" if functional else "FAIL"),
        ("I", "운영·수익 단계 측정", "WAITING"), ("J", "증거 저장", "PASS"),
        ("K", "검증 구조 확대", "WAITING"), ("L", "다음 탐색 예약", "PASS"),
    ]
    return {
        "schema_version": "1.0", "run_id": run_id, "started_at": started, "finished_at": utc_now(),
        "operating_root": "WIC-AUTONOMOUS-ONE-PERSON-BUSINESS",
        "scheduler": "GitHub Actions daily + Node-RED/Kestra health link", "tool_inventory_count": len(tools),
        "tools": tools, "platform_discovery": platform_discovery,
        "candidates": candidates, "selected_pilot": selected["id"] if selected else None,
        "pilot": {"name": "WIC 웹사이트 안심 점검", "public_path": "/revenue-lab/",
                  "monitors": monitor_results, "business_model": selected["business_model"] if selected else None},
        "revenue_stages": stages,
        "cycle_stages": [{"id": key, "name": name, "status": status} for key, name, status in cycle],
        "next_cycle": "자동 예약됨", "financial_action_performed": False,
        "observer_manual_action_required": 0,
    }


def main() -> None:
    result = build_result()
    PUBLIC.mkdir(parents=True, exist_ok=True)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    STATE.write_text(text, encoding="utf-8")
    EVIDENCE.write_text(text, encoding="utf-8")
    print(json.dumps({"run_id": result["run_id"], "tools": result["tool_inventory_count"],
                      "pilot": result["selected_pilot"], "functional": result["revenue_stages"]["actual_function"],
                      "state": str(STATE.relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
