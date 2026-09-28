"""Shared fail-closed execution, registration and exactly-once contract."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

REQUIRED_CONTRACT = ("input", "handler", "output", "expected")


def utcnow():
    return datetime.now(timezone.utc)


def atomic_json(path: Path, value: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".next")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(path)


def identity(demand: dict) -> str:
    explicit = demand.get("demand_id") or demand.get("work_id")
    if explicit:
        return str(explicit)
    raw = json.dumps({k: demand.get(k) for k in ("target_tool", "execution_contract")}, sort_keys=True)
    return "AUTO-" + hashlib.sha256(raw.encode()).hexdigest()[:20]


def validate_contract(contract: dict) -> list[str]:
    missing = [key for key in REQUIRED_CONTRACT if not contract.get(key)]
    if contract.get("handler") and not isinstance(contract["handler"], list):
        missing.append("handler_must_be_argv_list")
    if contract.get("expected") and not isinstance(contract["expected"], dict):
        missing.append("expected_must_be_object")
    return missing


class ClaimStore:
    """Atomic on a shared filesystem. Cross-provider use requires a shared mount."""
    def __init__(self, root: Path):
        self.root = root
        self.claims = root / "claims"
        self.terminals = root / "terminal"
        self.recovery = root / "recovery"
        for folder in (self.claims, self.terminals, self.recovery):
            folder.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def key(job_id: str) -> str:
        return hashlib.sha256(job_id.encode()).hexdigest()

    def terminal(self, job_id: str) -> Path:
        return self.terminals / f"{self.key(job_id)}.json"

    def claim_dir(self, job_id: str) -> Path:
        return self.claims / self.key(job_id)

    def claim(self, job_id: str, owner: str, lease_seconds: int = 300) -> dict:
        if self.terminal(job_id).exists():
            return {"status": "BLOCKED_COMPLETED", "job_id": job_id}
        folder = self.claim_dir(job_id)
        now = utcnow()
        try:
            folder.mkdir()
        except FileExistsError:
            receipt = json.loads((folder / "claim.json").read_text(encoding="utf-8"))
            if datetime.fromisoformat(receipt["lease_expiry"]) > now:
                return {"status": "BLOCKED_CLAIMED", "job_id": job_id, "owner": receipt["owner"]}
            stale = folder.with_name(folder.name + ".stale." + uuid.uuid4().hex)
            try:
                folder.replace(stale)
            except (FileNotFoundError, FileExistsError, PermissionError):
                return {"status": "BLOCKED_RECLAIM_RACE", "job_id": job_id}
            shutil.rmtree(stale, ignore_errors=True)
            try:
                folder.mkdir()
            except FileExistsError:
                return {"status": "BLOCKED_RECLAIM_RACE", "job_id": job_id}
        receipt = {"status": "CLAIMED", "job_id": job_id, "owner": owner,
                   "fencing_token": uuid.uuid4().hex, "claim_time": now.isoformat(),
                   "lease_expiry": (now + timedelta(seconds=lease_seconds)).isoformat()}
        atomic_json(folder / "claim.json", receipt)
        return receipt

    def _owned(self, job_id: str, owner: str, token: str) -> tuple[Path, dict]:
        folder = self.claim_dir(job_id)
        receipt = json.loads((folder / "claim.json").read_text(encoding="utf-8"))
        if receipt["owner"] != owner or receipt["fencing_token"] != token:
            raise PermissionError("FENCING_TOKEN_MISMATCH")
        return folder, receipt

    def checkpoint(self, job_id: str, owner: str, token: str, state: dict):
        folder, _ = self._owned(job_id, owner, token)
        atomic_json(folder / "checkpoint.json", state)

    def heartbeat(self, job_id: str, owner: str, token: str, lease_seconds: int = 300):
        folder, receipt = self._owned(job_id, owner, token)
        receipt["lease_expiry"] = (utcnow() + timedelta(seconds=lease_seconds)).isoformat()
        atomic_json(folder / "claim.json", receipt)

    def finish(self, job_id: str, owner: str, token: str, result: dict):
        folder, _ = self._owned(job_id, owner, token)
        if result.get("final_state") != "PASS" or not result.get("result_return"):
            raise ValueError("TERMINAL_PASS_REQUIRES_VALIDATED_RESULT_RETURN")
        atomic_json(self.terminal(job_id), result)
        shutil.rmtree(folder)

    def release_for_resume(self, job_id: str, owner: str, token: str, checkpoint: dict):
        folder, _ = self._owned(job_id, owner, token)
        atomic_json(self.recovery / f"{self.key(job_id)}.json", checkpoint)
        shutil.rmtree(folder)


def auto_register(queue: dict, demand: dict) -> tuple[dict, bool]:
    demand_id = identity(demand)
    demand = {**demand, "demand_id": demand_id}
    missing = validate_contract(demand.get("execution_contract") or {})
    if missing:
        demand.update(status="HOLD_EXECUTABLE_CONTRACT_REQUIRED", missing_contract=missing)
    else:
        demand.setdefault("status", "READY")
    rows = queue.setdefault("demands", [])
    if any(identity(row) == demand_id for row in rows):
        return next(row for row in rows if identity(row) == demand_id), False
    rows.append(demand)
    return demand, True


def _expand(argv: list[str], workspace: Path, contract: dict) -> list[str]:
    values = {"python": sys.executable, "workspace": str(workspace),
              "input": str((workspace / contract["input"]).resolve()),
              "output": str((workspace / contract["output"]).resolve())}
    return [str(part).format(**values) for part in argv]


def execute_registered(demand: dict, workspace: Path, store: ClaimStore, owner: str) -> dict:
    job_id = identity(demand)
    contract = demand.get("execution_contract") or {}
    missing = validate_contract(contract)
    if missing:
        return {"job_id": job_id, "final_state": "HOLD", "reason": "EXECUTABLE_CONTRACT_REQUIRED",
                "missing": missing, "result_return": {"status": "HOLD", "tool016_ack": "RECEIVED"}}
    claim = store.claim(job_id, owner)
    if claim["status"] != "CLAIMED":
        return {"job_id": job_id, "final_state": "BLOCKED", "reason": claim["status"],
                "result_return": {"status": "BLOCKED", "tool016_ack": "RECEIVED"}}
    token = claim["fencing_token"]
    store.checkpoint(job_id, owner, token, {"stage": "CLAIM_DURABLE", "contract": contract})
    output = (workspace / contract["output"]).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(_expand(contract["handler"], workspace, contract), cwd=workspace,
                          capture_output=True, text=True, timeout=contract.get("timeout", 600))
    expected = contract["expected"]
    actual = {"returncode": proc.returncode, "output_exists": output.is_file(),
              "stdout": proc.stdout, "stderr": proc.stderr}
    if output.is_file():
        actual["output_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    checks = {
        "returncode": actual["returncode"] == expected.get("returncode", 0),
        "output_exists": actual["output_exists"] is expected.get("output_exists", True),
    }
    if "output_sha256" in expected:
        checks["output_sha256"] = actual.get("output_sha256") == expected["output_sha256"]
    if "stdout_contains" in expected:
        checks["stdout_contains"] = expected["stdout_contains"] in actual["stdout"]
    passed = all(checks.values())
    result = {"job_id": job_id, "owner": owner, "fencing_token": token,
              "expected": expected, "actual": actual, "comparison": checks,
              "final_state": "PASS" if passed else "FAIL",
              "checkpoint": "TERMINAL" if passed else "FAILED_RETRYABLE",
              "result_return": {"status": "PASS" if passed else "FAIL", "tool016_ack": "RECEIVED"}}
    if passed:
        store.finish(job_id, owner, token, result)
    else:
        store.release_for_resume(job_id, owner, token, result)
    return result
