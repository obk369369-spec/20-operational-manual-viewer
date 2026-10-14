from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def transform(payload: dict) -> dict:
    multiplier = 3 if os.environ.get("PROBE_BROKEN") == "1" else 2
    return {
        "records": [
            {"id": row["id"], "result": row["value"] * multiplier}
            for row in payload["records"]
        ],
        "status": "PASS",
    }


if __name__ == "__main__":
    source = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    Path(sys.argv[2]).write_text(
        json.dumps(transform(source), ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
