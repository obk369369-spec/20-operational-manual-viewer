"""Automatic fail-closed Work startup gate for the mandatory credit-waste manual."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
MANUAL = HERE / "WIC_WORK_CREDIT_WASTE_PREVENTION_MANUAL.md"
REQUIRED_MARKERS = (
    "상태: ACTIVE / REQUIRED", "WASTE_INSTRUCTION_SCAN",
    "ONE_ROOT_ONE_PUSH = FORBIDDEN", "ONE_ROOT_ONE_CLOUD_RUN = FORBIDDEN",
    "ONE_ROOT_ONE_READBACK = FORBIDDEN", "STOP_DUPLICATE_REMOTE_ACTION",
    "STOP_LOW_CLOSURE_DENSITY", "FILE_BY_FILE_EXECUTION_PATH = DO_NOT_CREATE",
    "COLLECT_ALL_ERRORS_BEFORE_MUTATION = REQUIRED",
)
TEXT_FIELDS = ("instruction", "prompt", "plan", "execution_goal", "restart_point", "exact_next_step", "steps")
WASTE_PATTERNS = (
    ("FILE_BY_FILE", r"(파일|file)\s*[^\n,;]{0,80}(마다|별로|하나씩).{0,100}(수정|test|테스트|commit|push|run|read[- ]?back|검증)"),
    ("ONE_ERROR_ONE_OPERATION", r"(?:오류|error|ROOT)\s*(?:하나(?:씩|마다)?|1개(?:씩|마다)?|마다|별로).{0,100}(?:수정|test|commit|push|run|read[- ]?back|검증)"),
    ("PER_ITEM_REMOTE_LOOP", r"(각|each).{0,80}(ROOT|파일|file|오류|error).{0,160}(commit|push).{0,120}(cloud|run).{0,120}(read[- ]?back|remote)"),
    ("REPEAT_PASS", r"(PASS|VERIFIED|REMOTE_VERIFIED|DEPLOYED_PASS).{0,80}(다시|재확인|recheck|rerun|재실행)"),
    ("UNCHANGED_HOLD_RETRY", r"HOLD.{0,100}(조건.{0,30}(변화|변경).{0,20}(없|없이)|다시|재시도|rerun)"),
    ("IMMEDIATE_FIX_REMOTE_LOOP", r"(수정|fix).{0,80}(push|commit).{0,80}(run|cloud).{0,80}(read[- ]?back|remote).{0,80}(수정|fix)"),
    ("ROUND_BY_ROUND", r"(1회차|round\s*1).{0,80}(보고|report).{0,80}(계속|continue|2회차|round\s*2)"),
    ("BLIND_RETRY", r"(거부|denied|실패|failed).{0,80}(동일|같은).{0,50}(명령|command).{0,50}(다시|재시도|retry)"),
)

def manual_receipt(path: Path | None = None) -> dict[str, Any]:
    target = path or MANUAL
    try:
        raw = target.read_bytes(); text = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        return {"allowed": False, "decision": "WORK_HOLD_WASTE_MANUAL_UNREADABLE", "reason": str(exc)}
    missing = [m for m in REQUIRED_MARKERS if m not in text]
    if missing:
        return {"allowed": False, "decision": "WORK_HOLD_WASTE_MANUAL_INVALID", "missing_markers": missing}
    return {"allowed": True, "decision": "WASTE_MANUAL_READ", "path": target.name, "sha256": hashlib.sha256(raw).hexdigest()}

def _instruction_text(candidate: Mapping[str, Any]) -> str:
    chunks=[]
    for key in TEXT_FIELDS:
        value=candidate.get(key)
        if value not in (None, "", [], {}):
            chunks.append(json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value)
    return "\n".join(chunks)

def waste_instruction_scan(candidate: Mapping[str, Any]) -> dict[str, Any]:
    text=_instruction_text(candidate)
    findings=[]
    for code, pattern in WASTE_PATTERNS:
        if re.search(pattern, text, flags=re.I|re.S): findings.append(code)
    steps=candidate.get("steps")
    if isinstance(steps, list) and len(steps) > 1:
        remote=[]
        for i, step in enumerate(steps):
            s=json.dumps(step, ensure_ascii=False) if not isinstance(step,str) else step
            if re.search(r"\b(commit|push|cloud|run|read[- ]?back|fetch|status|diff)\b", s, re.I): remote.append(i)
        if len(remote) >= 3: findings.append("FRAGMENTED_REMOTE_STEPS")
    findings=list(dict.fromkeys(findings))
    return {"passed": not findings, "findings": findings, "scanned_fields": [k for k in TEXT_FIELDS if candidate.get(k) not in (None,"",[],{})]}

def enforce_start(candidate: Mapping[str, Any]) -> dict[str, Any]:
    receipt=manual_receipt()
    if not receipt.get("allowed"): return receipt
    scan=waste_instruction_scan(candidate)
    if not scan["passed"]:
        return {**receipt, "allowed": False, "decision": "STOP_WASTE_PLAN", "reason": "Wasteful file/error-by-file execution plan blocked before Work starts; collect all errors first and repair in cross-file batches.", **scan}
    return {**receipt, "allowed": True, "decision": "WORK_WASTE_GATE_PASS", **scan}

def self_test() -> None:
    r=manual_receipt(); assert r["allowed"], r
    assert enforce_start({"execution_goal":"전체 오류를 먼저 수집하고 원인별로 통합 수정 후 묶음 테스트"})["decision"]=="WORK_WASTE_GATE_PASS"
    bad={"instruction":"각 파일마다 하나씩 수정하고 commit push cloud run read-back을 반복한다"}
    assert enforce_start(bad)["decision"]=="STOP_WASTE_PLAN"
    bad2={"instruction":"PASS 결과를 다시 재확인한다"}
    assert enforce_start(bad2)["decision"]=="STOP_WASTE_PLAN"
    print("PASS: automatic waste-manual gate")
if __name__ == "__main__": self_test()
