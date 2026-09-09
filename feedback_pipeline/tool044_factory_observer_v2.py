"""Local-only observer V2 and feedback endpoint; no external dependency."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from tool016_feedback_bridge import ingest, read_json

HERE = Path(__file__).resolve().parent


def snapshot(root: Path) -> dict:
    cloud = read_json(root / "tool044_cloud_state.json", {})
    runtime = read_json(root / "tool044_factory_runtime.json", {})
    queue = read_json(root / "tool044_atomic_demand_queue.json", {"demands": []})
    registry = read_json(root / "VERIFIED_COMPONENT_REGISTRY.json", {"components": []})
    pool = read_json(root / "evidence" / "tool044_verified_composition_pool.json", {"compositions": []})
    jobs = list(cloud.get("jobs", {}).values())
    demands = queue.get("demands", [])
    active = bool(cloud.get("trigger") == "GITHUB_ACTIONS" and cloud.get("checkpoint"))
    latest = jobs[-1] if jobs else {}
    latest_demand = demands[-1] if demands else {}
    counts = {s: sum(1 for j in jobs if str(j.get("status", "")).upper() == s)
              for s in ("COMPLETED", "FAIL", "HOLD", "DEFERRED_BACKOFF")}
    updated = cloud.get("updated_at")
    try:
        recently_alive = datetime.fromisoformat(str(updated).replace("Z", "+00:00")) >= datetime.now(timezone.utc) - timedelta(minutes=20)
    except ValueError:
        recently_alive = False
    recent_error = cloud.get("last_failure") or runtime.get("last_failure")
    if isinstance(recent_error, dict):
        recent_error = recent_error.get("error") or recent_error.get("reason") or json.dumps(recent_error, ensure_ascii=False)
    coverage = read_json(root / "evidence" / "tool016_history_coverage_audit_20260909.json", {})
    cov = coverage.get("coverage", {})
    archive = cov.get("historical_archive_feedback_event_extraction", {})
    structured = cov.get("structured_canonical_sources", {})
    old_counts = coverage.get("existing_structured_counts", {})
    history_coverage = {
        "known_sources": coverage.get("population_inventory", {}).get("known_unique_history_sources", "UNKNOWN"),
        "structured_known": structured.get("known"), "structured_covered": structured.get("covered"),
        "archive_known": archive.get("known_archive_files"),
        "archive_covered": archive.get("covered_with_file_level_raw_feedback_receipt"),
        "archive_raw_covered": archive.get("covered_with_file_level_raw_feedback_receipt"),
        "partial_sources": archive.get("partial_metadata_or_canonicalization_only"),
        "unavailable_sources": archive.get("access_not_available_or_unreadable"),
        "coverage_percent": archive.get("coverage_percent"),
        "full_history_coverage": archive.get("full_history_coverage", "UNKNOWN"),
        "raw_error_events": coverage.get("root_cause", {}).get("raw_error_events", "UNKNOWN"),
        "raw_feedback_events": coverage.get("root_cause", {}).get("raw_feedback_events", "UNKNOWN"),
        "repeated_events": coverage.get("root_cause", {}).get("repeated_events", "UNKNOWN"),
        "unique_records": coverage.get("root_cause", {}).get("unique_feedback_records"),
        "structured_error_feedback": old_counts.get("structured_source_error_feedback_records"),
        "roots_after_dedup": coverage.get("root_cause", {}).get("roots_after_dedup"),
        "tool044_handoffs": old_counts.get("structured_source_tool044_handoff"),
        "atomic_demands": len(demands),
        "label_59": "구조화 7개 source에서 회수한 오류/미검증 59",
        "by_tool": coverage.get("under_extraction_samples", []),
        "under_extraction_tools": [x.get("tool_id") for x in coverage.get("under_extraction_samples", [])
                                    if x.get("result") == "UNDER_EXTRACTION_CONFIRMED"],
    }
    stage_names = ("search", "verify", "receipt_actual", "sandbox", "composition",
                   "regression", "integration", "deploy_validation")
    parallel_status = {
        "configured_parallel_jobs": cloud.get("parallel_jobs", 0),
        "active_workers": runtime.get("active_workers", 0),
        "stages": {name: 0 for name in stage_names},
        "evidence_status": "NOT_PROVEN" if not runtime.get("active_workers", 0) else "ACTIVE",
    }
    return {
        "status": "ACTIVE" if active and recently_alive else "CAPABLE_ONLY",
        "last_heartbeat": runtime.get("last_heartbeat") or cloud.get("updated_at"),
        "last_scheduler": cloud.get("updated_at"), "next_run": "GitHub Actions schedule contract",
        "checkpoint": cloud.get("checkpoint") or runtime.get("checkpoint"),
        "queue_count": len(demands), "job_counts": counts,
        "verified_atomic_count": len([x for x in registry.get("components", [])
                                      if "VERIFIED" in str(x.get("status", ""))]),
        "verified_composition_count": len([x for x in pool.get("compositions", [])
                                           if "VERIFIED" in str(x.get("status", ""))]),
        "current_tool": (latest_demand.get("target_tool") or latest.get("source") or "대상 없음"),
        "current_function": (latest_demand.get("demand_id") or latest.get("demand_id") or "현재 제작 없음"),
        "atomic_capabilities": latest_demand.get("atomic_capabilities", []),
        "latest_composition": (pool.get("compositions", [])[-1] if pool.get("compositions") else None),
        "current_stage": cloud.get("current_stage") or runtime.get("current_stage") or "HOLD",
        "recent_error": recent_error,
        "latest_feedback": read_json(root / "tool016_feedback_intake_ledger.json", {"roots": []}).get("roots", [])[-1:] or [],
        "history_coverage": history_coverage,
        "parallel_status": parallel_status,
        "truth_boundary": {"any_chat_auto_access": "ACCESS_NOT_AVAILABLE",
                           "local_observer_feedback": "AUTO_INGEST_VERIFIED"},
    }


class Handler(SimpleHTTPRequestHandler):
    root = HERE

    def do_GET(self):
        if urlparse(self.path).path == "/api/status":
            return self.send_json(snapshot(self.root))
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/feedback":
            self.send_error(404); return
        origin = self.headers.get("Origin")
        allowed = f"http://127.0.0.1:{self.server.server_address[1]}"
        if origin and origin != allowed:
            self.send_json({"status": "REJECTED", "error": "origin not allowed"}, 403); return
        size = int(self.headers.get("Content-Length", "0"))
        if size <= 0 or size > 65536:
            self.send_error(400); return
        try:
            event = json.loads(self.rfile.read(size).decode("utf-8"))
            result = ingest(event, self.root)
            self.send_json(result, 201)
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json({"status": "REJECTED", "error": str(exc)}, 400)

    def send_json(self, value, status=200):
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--port", type=int, default=8044)
    parser.add_argument("--root", default=str(HERE)); args = parser.parse_args()
    Handler.root = Path(args.root).resolve()
    # Serve only the feedback_pipeline directory; bind loopback, never LAN.
    import os
    os.chdir(Handler.root)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
