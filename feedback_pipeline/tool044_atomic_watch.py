"""Local, bounded TOOL044 atomic-demand cycle. No production mutation."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tool044_composition import test_url_provenance_composition
from tool044_function_state import build as build_function_state, write as write_function_state

HERE = Path(__file__).resolve().parent


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def signature(demand: dict) -> str:
    value = json.dumps({"id": demand["demand_id"], "capabilities": sorted(demand["atomic_capabilities"]),
                        "candidates": demand.get("official_candidates", [])}, sort_keys=True)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def harvest_pypi(candidate: dict, artifact_dir: Path) -> dict:
    package, version = candidate["package"], candidate["version"]
    metadata_url = f"https://pypi.org/pypi/{package}/{version}/json"
    with urllib.request.urlopen(metadata_url, timeout=20) as response:
        metadata = json.load(response)
    release = next((item for item in metadata["urls"] if item["filename"] == candidate["filename"]), None)
    if not release:
        return {"status": "NO_OFFICIAL_RECEIPT", "official_source": metadata_url}
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact = artifact_dir / release["filename"]
    if not artifact.exists():
        with urllib.request.urlopen(release["url"], timeout=30) as response:
            artifact.write_bytes(response.read())
    artifact = artifact.resolve()
    actual_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
    receipt_hash = release["digests"]["sha256"]
    if actual_hash != receipt_hash:
        return {"status": "RECEIPT_COMPONENT_MISMATCH", "official_source": metadata_url,
                "receipt_sha256": receipt_hash, "actual_sha256": actual_hash}
    with zipfile.ZipFile(artifact) as archive:
        metadata_name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        package_metadata = archive.read(metadata_name).decode("utf-8", errors="replace")
    verified = False
    verification_detail = {}
    if candidate.get("verifier") == "validators_url":
        sys.path.insert(0, str(artifact))
        try:
            module = importlib.import_module("validators")
            verified = module.url("https://example.com/report") is True and module.url("not a url") is not True
        finally:
            sys.path.remove(str(artifact))
            sys.modules.pop("validators", None)
    elif candidate.get("verifier") == "html2text_extract":
        sys.path.insert(0, str(artifact))
        try:
            module = importlib.import_module("html2text")
            normal = module.html2text("<h1>Report</h1><p>Market growth</p>")
            malformed = module.html2text("")
            verified = "Report" in normal and "Market growth" in normal and malformed.strip() == ""
        finally:
            sys.path.remove(str(artifact))
            sys.modules.pop("html2text", None)
    elif candidate.get("verifier") == "mistune_heading_ast":
        sys.path.insert(0, str(artifact))
        try:
            module = importlib.import_module("mistune")
            parser = module.create_markdown(renderer="ast")
            normal = parser("# 1\n## 1.1\n### 1.1.1\n#### 1.1.1.1\n")
            malformed = parser("plain body without headings")
            levels = [token.get("attrs", {}).get("level") for token in normal if token.get("type") == "heading"]
            malformed_levels = [token for token in malformed if token.get("type") == "heading"]
            verified = levels == [1, 2, 3, 4] and not malformed_levels
        finally:
            sys.path.remove(str(artifact))
            sys.modules.pop("mistune", None)
    elif candidate.get("verifier") == "doit_local_engine":
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            dodo = sandbox / "dodo.py"
            (sandbox / "input.txt").write_text("fixture", encoding="utf-8")
            dodo.write_text('''from pathlib import Path\nimport time\ndef work(name):\n time.sleep(1); Path(name).write_text(name)\ndef mark(name):\n Path(name).write_text(name)\ndef fail():\n raise RuntimeError("fixture failure")\ndef task_a(): return {"actions":[(work,["a.out"])],"file_dep":["input.txt"],"targets":["a.out"]}\ndef task_b(): return {"actions":[(work,["b.out"])],"file_dep":["input.txt"],"targets":["b.out"]}\ndef task_bad(): return {"actions":[fail]}\ndef task_after_failure(): return {"actions":[(mark,["after.out"])],"file_dep":["input.txt"],"targets":["after.out"]}\n''', encoding="utf-8")
            env = dict(os.environ)
            env["PYTHONPATH"] = str(artifact) + os.pathsep + env.get("PYTHONPATH", "")
            command = [sys.executable, "-m", "doit", "-f", str(dodo), "--continue", "-n", "2"]
            started = time.monotonic()
            first = subprocess.run(command, cwd=sandbox, env=env, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=30)
            elapsed = time.monotonic() - started
            # One fixture intentionally fails. Independent jobs must still complete.
            failure_isolated = first.returncode != 0 and (sandbox / "a.out").exists() and (sandbox / "b.out").exists() and (sandbox / "after.out").exists()
            parallel = elapsed < 1.85
            dodo.write_text(dodo.read_text(encoding="utf-8").replace('def task_bad(): return {"actions":[fail]}', 'def task_bad(): return {"actions":[]}'), encoding="utf-8")
            second_started = time.monotonic()
            second = subprocess.run(command, cwd=sandbox, env=env, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=30)
            resume_elapsed = time.monotonic() - second_started
            third_started = time.monotonic()
            third = subprocess.run(command, cwd=sandbox, env=env, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=30)
            skip_elapsed = time.monotonic() - third_started
            verified = failure_isolated and parallel and second.returncode == 0 and third.returncode == 0 and skip_elapsed < 0.8
            verification_detail = {"first_returncode": first.returncode, "parallel_elapsed_seconds": round(elapsed, 3),
                                   "failure_isolated": failure_isolated, "second_returncode": second.returncode,
                                   "resume_elapsed_seconds": round(resume_elapsed, 3),
                                   "third_returncode": third.returncode, "incremental_skip_seconds": round(skip_elapsed, 3),
                                   "first_output": (first.stdout + first.stderr)[-1000:],
                                   "second_output": (second.stdout + second.stderr)[-1000:]}
    return {
        "status": "VERIFIED_REUSABLE" if verified else "SANDBOX_FAIL",
        "component_id": f"{package.upper()}_{version.replace('.', '_')}_{candidate['capability']}",
        "atomic_capability": candidate["capability"], "official_source": metadata_url,
        "artifact_url": release["url"], "artifact": str(artifact), "version": version,
        "receipt_sha256": receipt_hash, "actual_sha256": actual_hash,
        "license": metadata["info"].get("license_expression") or metadata["info"].get("license") or "NOT_PUBLISHED",
        "release_date": release.get("upload_time_iso_8601", "NOT_PUBLISHED"),
        "dependencies": metadata["info"].get("requires_dist") or [],
        "package_metadata_present": bool(package_metadata), "sandbox_expected_actual": "PASS" if verified else "FAIL",
        "verification_detail": verification_detail,
    }


def run_cycle(queue_path: Path, registry_path: Path, state_path: Path, now: datetime | None = None,
              external: bool = False, artifact_dir: Path | None = None,
              trigger_source: str = "MANUAL") -> dict:
    now = now or utc_now()
    function_state_base = queue_path.parent
    function_state = (write_function_state(function_state_base)
                      if (function_state_base / "wic_target_registry.json").exists()
                      else build_function_state(HERE))
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    previous = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"receipts": {}}
    receipts = previous.get("receipts", {})
    # The registry keeps legacy general components and the newer atomic pool.
    # Both are valid reuse sources when they publish atomic_capabilities.
    pool = registry.get("components", []) + registry.get("verified_atomic_component_pool", [])
    capability_map = {
        capability: item["component_id"]
        for item in pool if item.get("status") == "VERIFIED_REUSABLE"
        for capability in item.get("atomic_capabilities", [])
    }
    results, duplicate_blocks, external_queries, verified_external = [], 0, 0, []
    for demand in queue.get("demands", []):
        sig = signature(demand)
        old = receipts.get(sig)
        matched = {cap: capability_map[cap] for cap in demand["atomic_capabilities"] if cap in capability_map}
        missing = [cap for cap in demand["atomic_capabilities"] if cap not in matched]
        # A component verified after an earlier failed search must immediately
        # satisfy the demand. The 24-hour backoff only blocks another external
        # query for capabilities that are still missing.
        if missing and old and old.get("next_eligible_search") and now < datetime.fromisoformat(old["next_eligible_search"]):
            duplicate_blocks += 1
            results.append({"demand_id": demand["demand_id"], "result": "DUPLICATE_SEARCH_BLOCKED", "query_signature": sig})
            continue
        harvests = []
        if external:
            for candidate in demand.get("official_candidates", []):
                if candidate.get("capability") not in missing:
                    continue
                external_queries += 1
                try:
                    harvested = harvest_pypi(candidate, artifact_dir or state_path.parent / "external_artifacts")
                except Exception as exc:
                    harvested = {"status": "SOURCE_FAIL", "error": type(exc).__name__}
                harvests.append(harvested)
                if harvested.get("status") == "VERIFIED_REUSABLE":
                    verified_external.append(harvested)
                    matched[candidate["capability"]] = harvested["component_id"]
            missing = [cap for cap in demand["atomic_capabilities"] if cap not in matched]
        result = "READY_ATOMIC_COMPONENT_FOUND" if matched and not missing else "PARTIAL_ATOMIC_COMPONENT_SET" if matched else "NO_READY_ATOMIC_COMPONENT"
        receipt = {
            "demand_id": demand["demand_id"], "query_signature": sig, "last_searched": now.isoformat(),
            "matched": matched, "missing": missing, "result": result,
            "next_eligible_search": (now + timedelta(hours=24)).isoformat(),
            "external_search_executed": bool(harvests), "external_receipts": harvests,
        }
        receipts[sig] = receipt
        results.append(receipt)
    state = {
        "cycle_id": now.strftime("%Y%m%dT%H%M%SZ"), "runtime": "LOCAL_STANDARD_LIBRARY",
        "scheduled_start": now.isoformat() if trigger_source == "SCHEDULED" else None,
        "actual_start": now.isoformat(), "trigger_source": trigger_source,
        "work_triggered": trigger_source == "WORK", "user_triggered": trigger_source == "USER",
        "paid_api_calls": 0, "paid_saas_calls": 0, "production_mutations": 0,
        "demands_processed": len(results), "duplicate_searches_blocked": duplicate_blocks,
        "external_sources_queried": external_queries, "verified_external_components": verified_external,
        "results": results, "receipts": receipts, "next_state": "WAITING_FOR_NEXT_TRIGGER",
        "function_state": "tool044_function_state.json",
        "external_demand_candidate_count": len(function_state["tool044_external_demand_candidates"]),
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if external_queries:
        candidate_path = state_path.parent / "tool044_external_candidate_pool.json"
        verified_path = state_path.parent / "tool044_verified_external_component_pool.json"
        all_harvests = [receipt for result in results for receipt in result.get("external_receipts", [])]
        candidate_path.write_text(json.dumps({"candidates": all_harvests}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        old_verified = json.loads(verified_path.read_text(encoding="utf-8"))["components"] if verified_path.exists() else []
        merged = {item["component_id"]: item for item in old_verified + verified_external}
        verified_path.write_text(json.dumps({"components": list(merged.values())}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verified_path = state_path.parent / "tool044_verified_external_component_pool.json"
    external_verified = json.loads(verified_path.read_text(encoding="utf-8")).get("components", []) if verified_path.exists() else []
    composition_path = state_path.parent / "tool044_verified_composition_pool.json"
    available = {item.get("component_id") for item in external_verified} | {
        item.get("component_id") for item in registry.get("verified_atomic_component_pool", [])
    }
    provenance_ready = "WIC_MANIFESTED_ASSET_PROVENANCE_GATE" in {
        item.get("component_id") for item in registry.get("verified_atomic_component_pool", [])
    }
    wheel = (artifact_dir or state_path.parent / "external_artifacts") / "validators-0.35.0-py3-none-any.whl"
    composition_candidates = int("VALIDATORS_0_35_0_URL_VALIDATION" in available and provenance_ready and wheel.exists())
    state.update({"composition_candidates": composition_candidates, "compositions_tested": 0,
                  "verified_compositions": 0, "ready_for_integration": 0})
    if composition_candidates:
        fixture = queue_path.parent / "fixtures" / "tool042_customer_branch_actual_kmg.json"
        composition = test_url_provenance_composition(wheel, fixture)
        state.update({"compositions_tested": 1,
                      "verified_compositions": int(composition["status"] == "VERIFIED_COMPOSITION"),
                      "ready_for_integration": int(composition["ready_for_integration"]),
                      "composition_test": composition})
        old_compositions = json.loads(composition_path.read_text(encoding="utf-8")).get("compositions", []) if composition_path.exists() else []
        merged_compositions = {item["composition_id"]: item for item in old_compositions}
        if composition["status"] == "VERIFIED_COMPOSITION":
            merged_compositions[composition["composition_id"]] = composition
        composition_path.write_text(json.dumps({"compositions": list(merged_compositions.values()),
                                                "last_test": composition}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif not composition_path.exists():
        composition_path.write_text(json.dumps({"compositions": [], "reason": "NO_CONTRACT_COMPATIBLE_PAIR_TESTED"}, indent=2) + "\n", encoding="utf-8")
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parent
    parser.add_argument("--queue", type=Path, default=root / "tool044_atomic_demand_queue.json")
    parser.add_argument("--registry", type=Path, default=root / "VERIFIED_COMPONENT_REGISTRY.json")
    parser.add_argument("--state", type=Path, default=root / "evidence" / "tool044_atomic_watch_state.json")
    parser.add_argument("--external", action="store_true")
    parser.add_argument("--trigger-source", choices=["MANUAL", "WORK", "USER", "SCHEDULED"], default="MANUAL")
    args = parser.parse_args()
    print(json.dumps(run_cycle(args.queue, args.registry, args.state, external=args.external,
                               artifact_dir=root / "external_candidate_pool",
                               trigger_source=args.trigger_source), ensure_ascii=False))


if __name__ == "__main__":
    main()
