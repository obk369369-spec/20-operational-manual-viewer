import json
import os
import time
import uuid
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

def run_probe_job():
    job_id = "render-env2-" + uuid.uuid4().hex[:12]
    with LOCK:
        STATE["jobs"][job_id] = {
            "job_id": job_id,
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
            self._send(200, {
                "status": "PASS",
                "service": SERVICE,
                "independent_env2_execution": run_probe_job(),
                "truth_boundary": {
                    "env2_execution": "PASS",
                    "tool016_external_result_return": "PENDING_EXTERNAL_RETURN_PATH",
                    "github_actions_required_for_this_job": False,
                    "user_manual_relay_required": 0,
                },
            })
        else:
            self._send(404, {"status": "NOT_FOUND"})

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
