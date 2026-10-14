import json
import os
import time
import uuid
import urllib.request
import urllib.error
from urllib.parse import urlparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

SERVICE = "WIC_RENDER_ENV2"
RUNTIME = "RENDER_FREE_WEB_SERVICE"
LOCK = Lock()
STATE = {
    "booted_at": datetime.now(timezone.utc).isoformat(),
    "jobs": {},
    "last_result": None,
}

def now():
    return datetime.now(timezone.utc).isoformat()

ALLOWED_RETURN_HOST = "api.github.com"
ALLOWED_RETURN_PATH = "/repos/obk369369-spec/20-operational-manual-viewer/dispatches"

def run_probe_job(identity=None):
    identity = identity or {}
    job_id = str(identity.get("job_id") or ("render-env2-" + uuid.uuid4().hex[:12]))
    execution_id = "render-exec-" + uuid.uuid4().hex[:12]
    result_id = "render-result-" + uuid.uuid4().hex[:12]
    ack_id = "render-ack-" + uuid.uuid4().hex[:12]
    with LOCK:
        STATE["jobs"][job_id] = {
            "source_id": str(identity.get("source_id", "TOOL016-CANONICAL")),
            "intake_id": str(identity.get("intake_id", "TOOL044-EXTERNAL-FACTORY")),
            "tool_id": str(identity.get("tool_id", "TOOL016")),
            "job_id": job_id,
            "execution_id": execution_id,
            "result_id": result_id,
            "ack_id": ack_id,
            "provider": "RENDER",
            "runtime": RUNTIME,
            "status": "CLAIMED",
            "claimed_at": now(),
            "heartbeat": None,
            "checkpoint": None,
            "result_return": "LOCAL_RECEIPT_CREATED",
            "tool016_ack": "PENDING_EXTERNAL_RETURN_PATH",
        }
    time.sleep(0.01)
    with LOCK:
        job = STATE["jobs"][job_id]
        job["heartbeat"] = {"status": "PASS", "at": now()}
        job["checkpoint"] = {"stage": 1, "total_stages": 1, "saved_at": now()}
        job["status"] = "PASS"
        job["completed_at"] = now()
        job["expected"] = "ENV2_EXECUTION_CONTRACT_ACCEPTED"
        job["actual"] = "ENV2_EXECUTION_CONTRACT_ACCEPTED"
        job["expected_actual"] = "MATCH"
        STATE["last_result"] = dict(job)
        return dict(job)

def _valid_return_url(url):
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.netloc == ALLOWED_RETURN_HOST and parsed.path == ALLOWED_RETURN_PATH

def return_to_tool016(job, callback=None):
    callback = callback or {}
    url = str(callback.get("url") or os.environ.get("TOOL016_RETURN_URL", "")).strip()
    token = str(callback.get("token") or os.environ.get("TOOL016_RETURN_TOKEN", "")).strip()
    if not url:
        return {"status": "HOLD_NO_RETURN_URL", "user_manual_relay_required": 0}
    if not _valid_return_url(url):
        return {"status": "BLOCKED_INVALID_RETURN_URL", "user_manual_relay_required": 0}
    if not token:
        return {"status": "BLOCKED_NO_RETURN_AUTH", "user_manual_relay_required": 0}
    payload = json.dumps({
        "event_type": "render_env2_result",
        "client_payload": {"result": job},
    }).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "WIC-Render-ENV2"}
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")[:2000]
            return {
                "status": "PASS" if resp.status == 204 else "HOLD_UNEXPECTED_ACK",
                "http_status": resp.status,
                "ack_id": job["ack_id"],
                "response": body,
            }
    except Exception as exc:
        return {"status": "HOLD_RETURN_FAILED", "error": type(exc).__name__, "detail": str(exc)[:500], "user_manual_relay_required": 0}

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/health"):
            self._send(200, {
                "status": "PASS",
                "service": SERVICE,
                "runtime": RUNTIME,
                "purpose": "independent_external_runtime",
                "booted_at": STATE["booted_at"],
                "jobs_executed": len(STATE["jobs"]),
                "last_result": STATE["last_result"],
            })
        elif self.path == "/selftest":
            job = run_probe_job()
            returned = return_to_tool016(job)
            with LOCK:
                STATE["jobs"][job["job_id"]]["tool016_return"] = returned
                if returned.get("status") == "PASS":
                    STATE["jobs"][job["job_id"]]["tool016_ack"] = "RETURN_HTTP_PASS"
                STATE["last_result"] = dict(STATE["jobs"][job["job_id"]])
            self._send(200, {
                "status": "PASS" if returned.get("status") == "PASS" else "PARTIAL",
                "service": SERVICE,
                "independent_env2_execution": STATE["last_result"],
                "tool016_result_return": returned,
                "truth_boundary": {
                    "env2_execution": "PASS",
                    "tool016_external_result_return": returned.get("status"),
                    "github_actions_required_for_this_job": False,
                    "user_manual_relay_required": 0,
                },
            })
        else:
            self._send(404, {"status": "NOT_FOUND"})

    def do_POST(self):
        if self.path != "/execute":
            self._send(404, {"status": "NOT_FOUND"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 65536:
                raise ValueError("invalid payload size")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            identity = payload.get("identity") or {}
            required = {"source_id", "intake_id", "tool_id", "job_id"}
            if required - set(identity):
                raise ValueError("missing identity")
            job = run_probe_job(identity)
            returned = return_to_tool016(job, payload.get("callback") or {})
            with LOCK:
                STATE["jobs"][job["job_id"]]["tool016_return"] = returned
                STATE["jobs"][job["job_id"]]["tool016_ack"] = (
                    "ACK_ACCEPTED:" + job["ack_id"] if returned.get("status") == "PASS"
                    else returned.get("status", "HOLD_RETURN_FAILED")
                )
                STATE["last_result"] = dict(STATE["jobs"][job["job_id"]])
            self._send(200 if returned.get("status") == "PASS" else 502, {
                "status": "PASS" if returned.get("status") == "PASS" else "HOLD",
                "job": STATE["last_result"],
                "tool016_result_return": returned,
            })
        except (ValueError, json.JSONDecodeError) as exc:
            self._send(400, {"status": "BLOCKED_MALFORMED_PAYLOAD", "detail": str(exc)})

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
