"""Public-safe TOOL044 cloud worker; private/Windows work is fail-closed to local queue."""
from __future__ import annotations
import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE / "tool044_factory_runtime.json"
CLOUD = HERE / "tool044_cloud_state.json"
LOCAL = HERE / "tool044_local_required_queue.json"

def load(path: Path, fallback):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else fallback

def save(path: Path, value):
    pending = path.with_suffix(path.suffix + ".next")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(path)

def public_safe(job: dict) -> bool:
    return job.get("source") == "TOOL016_FUNCTION_STATE" and bool(job.get("missing_capabilities"))

def run(runtime=RUNTIME, cloud=CLOUD, local=LOCAL):
    now = datetime.now(timezone.utc).isoformat()
    source = load(runtime, {"jobs": {}})
    prior = load(cloud, {"schema_version": 1, "jobs": {}, "run_count": 0})
    local_state = load(local, {"schema_version": 1, "jobs": {}})
    claimed = completed = deferred = 0
    for job_id, job in source.get("jobs", {}).items():
        if not public_safe(job):
            local_state["jobs"][job_id] = {**job, "reason": "PRIVATE_OR_LOCAL_SENSITIVE_WORK"}
            continue
        old = prior["jobs"].get(job_id, {})
        row = {**job, "execution_class": "PUBLIC_SAFE_WORK", "worker": "GITHUB_ACTIONS"}
        if job.get("status") == "BACKOFF":
            row.update(status="DEFERRED_BACKOFF", last_checked=now); deferred += 1
        elif old.get("status") == "COMPLETED":
            row = old
        else:
            claimed += 1
            row.update(status="COMPLETED", last_checked=now,
                       result="PUBLIC_SAFE_HANDOFF_ACCEPTED",
                       receipt=hashlib.sha256(json.dumps(job, sort_keys=True).encode()).hexdigest())
            completed += 1
        prior["jobs"][job_id] = row
    checkpoint = os.environ.get("GITHUB_RUN_ID") or "LOCAL-" + now.replace(":", "").replace("-", "")
    prior.update(updated_at=now, checkpoint=checkpoint, run_count=prior.get("run_count", 0)+1,
                 trigger="GITHUB_ACTIONS" if os.environ.get("GITHUB_ACTIONS") == "true" else "LOCAL_TEST",
                 work_triggered=False, user_triggered=False, claimed=claimed, completed=completed,
                 deferred_backoff=deferred, paid_api_calls=0, paid_saas_calls=0)
    local_state.update(updated_at=now, queue_length=len(local_state["jobs"]))
    save(cloud, prior); save(local, local_state)
    return prior

def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        root=Path(d); runtime=root/"runtime.json"; cloud=root/"cloud.json"; local=root/"local.json"
        save(runtime,{"jobs":{"A":{"job_id":"A","source":"TOOL016_FUNCTION_STATE","missing_capabilities":["URL"],"status":"QUEUED"},"B":{"job_id":"B","source":"LOCAL_FILE","missing_capabilities":[],"status":"QUEUED"}}})
        first=run(runtime,cloud,local); second=run(runtime,cloud,local)
        assert first["jobs"]["A"]["status"] == "COMPLETED"
        assert second["jobs"]["A"]["receipt"] == first["jobs"]["A"]["receipt"]
        assert load(local,{})["jobs"]["B"]["reason"] == "PRIVATE_OR_LOCAL_SENSITIVE_WORK"
        assert second["run_count"] == 2 and second["paid_api_calls"] == 0
    return "PASS: public claim + sensitive local routing + persisted restart/resume + idempotency"

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); a=p.parse_args()
    print(self_test() if a.self_test else json.dumps(run(),ensure_ascii=False))
