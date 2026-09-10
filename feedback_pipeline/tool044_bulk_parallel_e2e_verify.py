"""Fail-closed independent verifier for a TOOL044 bulk lineage receipt."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_PARALLEL_STAGES = (
    "PARALLEL_SEARCH", "PARALLEL_RECEIPT_VERIFY", "PARALLEL_SANDBOX",
    "PARALLEL_FUNCTION_VERIFY", "PARALLEL_COMPOSITION", "PARALLEL_REGRESSION",
    "PARALLEL_DEPLOYMENT", "POST_DEPLOY_REGRESSION",
)


def verify(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.get("stages", {})
    stage_checks = {
        name: all([
            name in stages,
            stages.get(name, {}).get("status") == "PASS",
            stages.get(name, {}).get("overlap") is True,
            stages.get(name, {}).get("max_concurrency", 0) >= 2,
            len(stages.get(name, {}).get("jobs", [])) >= 2,
            all(job.get("JOB_ID") and job.get("WORKER_ID") and job.get("START_TIME") and job.get("END_TIME")
                for job in stages.get(name, {}).get("jobs", [])),
        ])
        for name in REQUIRED_PARALLEL_STAGES
    }
    scalar_checks = {
        "bulk_count": data.get("BULK_INPUT_COUNT", 0) >= 7 and data.get("UNIQUE_ROOT_COUNT", 0) >= 6,
        "dedup": data.get("DEDUPLICATED_COUNT") == 1 and data.get("DUPLICATE_WORK_COUNT") == 0,
        "real_parallel": data.get("MAX_ACTUAL_CONCURRENCY", 0) >= 4,
        "forced_failure_isolated": data.get("failure_isolation", {}).get("status") == "PASS"
            and data.get("failure_isolation", {}).get("GLOBAL_STOP_DUE_TO_SINGLE_JOB_FAILURE") == 0,
        "zero_loss": all(data.get(key) == 0 for key in
            ("JOB_LOSS", "SOURCE_LOSS", "ARTIFACT_LOSS", "DEPLOYMENT_LOSS", "DUPLICATE_COMPLETION")),
        "deployed_readback": data.get("DEPLOYED_ARTIFACT_READBACK") == "PASS",
        "deployed_function": data.get("DEPLOYED_FUNCTION_RETEST") == "PASS",
        "post_deploy_regression": data.get("POST_DEPLOY_REGRESSION") == "PASS",
        "production_protected": data.get("production_unchanged") is True,
        "producer_final": data.get("BULK_PARALLEL_E2E") == "PASS",
    }
    status = "PASS" if all(stage_checks.values()) and all(scalar_checks.values()) else "FAIL"
    return {"status": status, "source": str(path), "run_id": data.get("run_id"),
            "stage_checks": stage_checks, "scalar_checks": scalar_checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    result = verify(args.receipt)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
