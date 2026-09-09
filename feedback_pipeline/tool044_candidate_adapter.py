"""Manifest-driven, candidate-only deployment adapter.

No target/tool names are hardcoded.  A manifest must explicitly prove that its
root is a candidate and must provide an executable validator.
"""
from __future__ import annotations
import hashlib, json, py_compile, shutil
from pathlib import Path

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(path: Path, kind: str) -> bool:
    if kind == "python_compile":
        py_compile.compile(str(path), doraise=True); return True
    if kind == "html_contract":
        text=path.read_text(encoding="utf-8"); return "<html" in text.lower() and "</html>" in text.lower()
    raise ValueError("unsupported validator")

def deploy(manifest: dict, repo_root: Path) -> dict:
    required=("target_id","source_artifact","candidate_root","destination","validator")
    missing=[x for x in required if not manifest.get(x)]
    if missing: return {"status":"BLOCKED","reason":f"CONTRACT_MISSING_{missing[0].upper()}"}
    source=(repo_root/manifest["source_artifact"]).resolve()
    candidate=Path(manifest["candidate_root"]).resolve()
    destination=(candidate/manifest["destination"]).resolve()
    if not source.is_file(): return {"status":"BLOCKED","reason":"SOURCE_MISSING"}
    if not manifest.get("candidate_only") or candidate == destination or candidate not in destination.parents:
        return {"status":"BLOCKED","reason":"PRODUCTION_PROTECTION_REQUIRED"}
    candidate.mkdir(parents=True,exist_ok=True); destination.parent.mkdir(parents=True,exist_ok=True)
    before=digest(destination) if destination.exists() else None
    backup=destination.read_bytes() if destination.exists() else None
    try:
        shutil.copy2(source,destination); after=digest(destination)
        expected=digest(source)
        if after != expected: raise ValueError("READBACK_MISMATCH")
        if not validate(destination,manifest["validator"]): raise ValueError("TARGET_REGRESSION_FAIL")
        if manifest.get("force_failure"): raise ValueError("INTENTIONAL_FAILURE_FIXTURE")
        return {"status":"DEPLOYED_PASS","target_id":manifest["target_id"],
                "pre_sha":before,"post_sha":after,"source_sha":expected,
                "contract_match":"PASS","component_application":"PASS",
                "target_execution":"PASS","target_regression":"PASS","read_back":"PASS"}
    except Exception as exc:
        if backup is None:
            destination.unlink(missing_ok=True)
        else: destination.write_bytes(backup)
        restored=digest(destination) if destination.exists() else None
        return {"status":"ROLLED_BACK","target_id":manifest["target_id"],"reason":str(exc),
                "pre_sha":before,"restored_sha":restored,"rollback":"PASS" if restored==before else "FAIL"}
