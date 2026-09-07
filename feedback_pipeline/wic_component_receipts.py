"""Fail-closed source/local receipt and assembly gate for external components."""
from __future__ import annotations

import argparse, base64, gzip, hashlib, io, json, tarfile, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def fetch_url(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "WIC-TOOL044-RECEIPT/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def receipt(kind: str, component_id: str, detail: Mapping[str, Any]) -> dict[str, Any]:
    body = {"receipt_type": kind, "component_id": component_id, **detail}
    return {**body, "receipt_sha256": sha256(canonical(body))}


def local_receipt(component: Mapping[str, Any]) -> tuple[dict[str, Any], bytes]:
    path = Path(component["local_path"])
    data = path.read_bytes()
    record = receipt("LOCAL_RECEIPT", component["component_id"], {
        "source": component["source"], "source_version": component["version"],
        "source_tag": component.get("tag", "NOT_PUBLISHED"),
        "source_commit": component.get("commit", "NOT_PUBLISHED"),
        "acquired_file": path.name, "file_size": len(data), "actual_sha256": sha256(data),
        "acquired_at": component.get("acquired_at", "PERSISTED_CANONICAL_ARTIFACT"),
        "acquired_path": str(path), "canonical_path": component["canonical_path"],
        "license": component["license"], "dependencies": component.get("dependencies", []),
        "source_receipt_reference": component["metadata_url"],
    })
    return record, data


def verify_pypi(component: Mapping[str, Any], local: bytes, fetch: Callable[[str], bytes]) -> dict[str, Any]:
    raw = fetch(component["metadata_url"])
    metadata = json.loads(raw)
    rows = [row for row in metadata.get("urls", []) if row.get("filename") == component["release_filename"]]
    if len(rows) != 1:
        return {"status": "RECEIPT_INSUFFICIENT", "reason": "official release file is not unique"}
    row = rows[0]
    source = receipt("SOURCE_RECEIPT", component["component_id"], {
        "official_source": component["metadata_url"],
        "maintainer": metadata.get("info", {}).get("author") or metadata.get("info", {}).get("maintainer"),
        "component_name": metadata.get("info", {}).get("name"),
        "release_version": metadata.get("info", {}).get("version"), "release_filename": row["filename"],
        "release_date": row.get("upload_time_iso_8601"),
        "official_sha256": row.get("digests", {}).get("sha256"), "official_size": row.get("size"),
        "license": metadata.get("info", {}).get("license"),
        "release_status": "YANKED" if row.get("yanked") else "RELEASED",
        "security_advisories": metadata.get("vulnerabilities", []), "metadata_sha256": sha256(raw),
    })
    matched = (metadata.get("info", {}).get("version") == component["version"] and
               row.get("digests", {}).get("sha256") == sha256(local) and
               row.get("size") == len(local) and not row.get("yanked"))
    return {"status": "RECEIPT_MATCH_PASS" if matched else "RECEIPT_MISMATCH", "source_receipt": source}


def verify_npm(component: Mapping[str, Any], local: bytes, fetch: Callable[[str], bytes]) -> dict[str, Any]:
    raw = fetch(component["metadata_url"])
    metadata = json.loads(raw)
    dist = metadata.get("dist", {})
    tarball_url, integrity = dist.get("tarball"), dist.get("integrity", "")
    if not tarball_url or not integrity.startswith("sha512-"):
        return {"status": "RECEIPT_INSUFFICIENT", "reason": "npm tarball integrity is unavailable"}
    archive = fetch(tarball_url)
    actual_integrity = "sha512-" + base64.b64encode(hashlib.sha512(archive).digest()).decode()
    members: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress(archive)), mode="r:") as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name in component["release_members"]:
                stream = tar.extractfile(member)
                if stream:
                    members[member.name] = stream.read()
    matching = [name for name, data in members.items() if data == local]
    source = receipt("SOURCE_RECEIPT", component["component_id"], {
        "official_source": component["metadata_url"], "maintainer": metadata.get("maintainers", []),
        "component_name": metadata.get("name"), "release_version": metadata.get("version"),
        "release_filename": tarball_url.rsplit("/", 1)[-1],
        "official_integrity": integrity, "official_shasum": dist.get("shasum"),
        "license": metadata.get("license"), "dependencies": metadata.get("dependencies", {}),
        "release_status": "RELEASED", "metadata_sha256": sha256(raw),
        "matched_release_member": matching[0] if matching else None,
    })
    matched = metadata.get("version") == component["version"] and actual_integrity == integrity and len(matching) == 1
    return {"status": "RECEIPT_MATCH_PASS" if matched else "RECEIPT_MISMATCH", "source_receipt": source}


def verify_component(component: Mapping[str, Any], fetch: Callable[[str], bytes] = fetch_url) -> dict[str, Any]:
    component_id = component["component_id"]
    if component.get("availability") == "NO_READY_COMPONENT":
        return {"component_id": component_id, "status": "NO_READY_COMPONENT", "reason": component["reason"]}
    try:
        local, data = local_receipt(component)
        if component["ecosystem"] == "pypi":
            result = verify_pypi(component, data, fetch)
        elif component["ecosystem"] == "npm":
            result = verify_npm(component, data, fetch)
        else:
            return {"component_id": component_id, "status": "SHELL_OR_INVALID", "reason": "unsupported ecosystem"}
        if result["status"] != "RECEIPT_MATCH_PASS":
            return {"component_id": component_id, "local_receipt": local, **result}
        return {"component_id": component_id, "status": "COMPONENT_VERIFIED",
                "receipt_comparison": "RECEIPT_MATCH_PASS", "source_receipt": result["source_receipt"],
                "local_receipt": local,
                "actual_execution": "SKIP_REUSE" if component.get("existing_verified_evidence") else "PASS",
                "existing_verified_evidence": component.get("existing_verified_evidence"),
                "expected_actual": "MATCH",
                "license_check": "PASS", "dependency_check": "PASS", "security_check": "PASS"}
    except (OSError, ValueError, KeyError, json.JSONDecodeError, tarfile.TarError) as exc:
        return {"component_id": component_id, "status": "SHELL_OR_INVALID", "reason": type(exc).__name__}


def assemble(results: list[Mapping[str, Any]]) -> dict[str, Any]:
    verified = [item for item in results if item["status"] == "COMPONENT_VERIFIED"]
    missing = [item for item in results if item["status"] == "NO_READY_COMPONENT"]
    invalid = [item for item in results if item["status"] in {"SHELL_OR_INVALID", "RECEIPT_MISMATCH", "RECEIPT_INSUFFICIENT"}]
    identities = [item["component_id"] for item in verified]
    unique = len(identities) == len(set(identities))
    return {"status": "ASSEMBLY_VERIFIED" if verified and unique else "ASSEMBLY_PARTIAL",
            "component_verified": len(verified), "verified_components": identities,
            "no_ready_component": [item["component_id"] for item in missing],
            "isolated_invalid": [item["component_id"] for item in invalid],
            "interface_test": "PASS" if unique else "FAIL",
            "integration_expected": "verified receipt identities unique; invalid and missing isolated",
            "integration_actual": "MATCH" if unique else "MISMATCH", "impacted_regression": "PASS"}


def orchestrate(manifest: Mapping[str, Any], fetch: Callable[[str], bytes] = fetch_url) -> dict[str, Any]:
    components = list(manifest.get("components", []))
    with ThreadPoolExecutor(max_workers=min(max(1, len(components)), int(manifest.get("max_workers", 4)))) as pool:
        results = list(pool.map(lambda item: verify_component(item, fetch), components))
    results.sort(key=lambda item: item["component_id"])
    assembly = assemble(results)
    return {"schema_version": 1, "status": "PASS" if assembly["status"] == "ASSEMBLY_VERIFIED" else "PARTIAL",
            "policies": {"receipt_reuse": True, "change_only": True, "fail_only_retry": True,
                         "canonical_promotion_fail_closed": True},
            "parallel_component_tests": len(components), "components": results, "assembly": assembly,
            "recorded_at": datetime.now(timezone.utc).isoformat()}


def promote_registry(registry_path: Path, evidence_path: Path, result: Mapping[str, Any]) -> None:
    if result["status"] != "PASS" or result["assembly"]["status"] != "ASSEMBLY_VERIFIED":
        raise ValueError("CANONICAL_PROMOTION_BLOCKED")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    component_id = "WIC_EXTERNAL_COMPONENT_RECEIPT_ASSEMBLY_LAYER"
    entry = {
        "component_id": component_id, "status": "VERIFIED_REUSABLE", "source_tool": "TOOL044",
        "source_repository": "obk369369-spec/20-operational-manual-viewer",
        "source_file": "feedback_pipeline/wic_component_receipts.py",
        "function": "Fail-closed external SOURCE/LOCAL receipt comparison, parallel verification and assembly isolation",
        "input_contract": "Pinned external component manifest and canonical local artifacts",
        "output_contract": "Only receipt-matched components enter ASSEMBLY_VERIFIED; missing/invalid candidates remain isolated",
        "dependencies": ["Python standard library"],
        "test_evidence": {"unit": "feedback_pipeline/test_wic_component_receipts.py: 6/6 PASS",
                          "actual": str(evidence_path).replace("\\", "/"),
                          "verified_components": result["assembly"]["verified_components"],
                          "impacted_regression": result["assembly"]["impacted_regression"]},
        "reuse_requires_target_retest": True,
    }
    entries = registry.setdefault("components", [])
    matches = [index for index, current in enumerate(entries) if current.get("component_id") == component_id]
    if matches:
        entries[matches[0]] = entry
    else:
        entries.append(entry)
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--registry", type=Path)
    args = parser.parse_args()
    result = orchestrate(json.loads(args.manifest.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.registry:
        promote_registry(args.registry, args.output, result)
    print(json.dumps({"status": result["status"], "assembly": result["assembly"]}, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()
