"""Classify only explicitly manifested PC/USB/SSD assets without modifying them."""
from __future__ import annotations

import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

FORBIDDEN = {"SHELL", "DRAFT", "FAIL", "PARTIAL", "BROKEN", "LEGACY", "TEMP", "UNKNOWN", "TEST_NOT_RUN"}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify(asset: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(asset["path"])
    declared = str(asset.get("declared_state", "UNKNOWN")).upper()
    base = {"asset_id": asset["asset_id"], "path": str(path), "role": asset.get("role"), "declared_state": declared}
    if not path.is_file():
        return {**base, "status": "UNKNOWN", "promotion_allowed": False, "reason": "asset file not found"}
    actual_hash = file_hash(path)
    if declared in FORBIDDEN:
        return {**base, "status": declared, "actual_sha256": actual_hash, "promotion_allowed": False,
                "reason": "non-verified state is isolated before promotion"}
    evidence = Path(asset.get("evidence_path", ""))
    checks = {
        "provenance": bool(asset.get("provenance")), "version": bool(asset.get("version")),
        "hash": actual_hash == str(asset.get("expected_sha256", "")).lower(),
        "evidence": evidence.is_file() and asset.get("evidence_status") in {"VERIFIED", "DEPLOYED_PASS"},
        "actual_execution": asset.get("actual_execution") == "PASS",
        "expected_actual": asset.get("expected_actual") == "MATCH",
    }
    passed = all(checks.values())
    return {**base, "status": "VERIFIED" if passed else "HOLD", "actual_sha256": actual_hash,
            "checks": checks, "promotion_allowed": passed,
            "promotion_routes": asset.get("promotion_routes", []) if passed else [],
            "reason": "all provenance gates passed" if passed else "one or more provenance gates missing"}


def inspect(manifest: Mapping[str, Any]) -> dict[str, Any]:
    assets = [classify(asset) for asset in manifest.get("assets", [])]
    counts: dict[str, int] = {}
    for asset in assets:
        counts[asset["status"]] = counts.get(asset["status"], 0) + 1
    return {"schema_version": 1, "scope": "MANIFESTED_RELATED_ASSETS_ONLY",
            "destructive_actions": 0, "assets": assets, "counts": counts,
            "status": "PASS" if all(item["status"] in {"VERIFIED", *FORBIDDEN} for item in assets) else "HOLD",
            "recorded_at": datetime.now(timezone.utc).isoformat()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = inspect(json.loads(args.manifest.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()
