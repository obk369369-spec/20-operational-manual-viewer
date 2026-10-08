"""One-shot path-only enumeration; never reads file content or hashes files."""
from __future__ import annotations
import gzip, hashlib, json, os, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / ".inventory_runtime"
DB = RUNTIME / "connected_storage.sqlite"
OUT = RUNTIME / "storage_path_delta_20261008"
DRIVES = ("C:", "D:", "F:", "I:")

def key(path: str) -> str:
    return hashlib.sha256(path.lower().encode("utf-8")).hexdigest()

def known_keys() -> tuple[dict[str, set[str]], dict[str, int]]:
    result = {d: set() for d in DRIVES}
    counts = {d: 0 for d in DRIVES}
    with sqlite3.connect(DB) as conn:
        for path_key, volume in conn.execute("select path_key, volume from files"):
            if volume in result:
                result[volume].add(path_key); counts[volume] += 1
    return result, counts

def enumerate_once(drive: str, known: set[str]) -> dict:
    output = OUT / f"{drive[0]}_new_path_candidates.txt.gz"
    if output.exists():
        raise RuntimeError(f"REPEAT_ENUMERATION_BLOCKED:{drive}")
    stack = [drive + "\\"]
    current = new = directories = 0
    errors: list[dict[str, str]] = []
    with gzip.open(output, "wt", encoding="utf-8", newline="\n") as sink:
        while stack:
            directory = stack.pop(); directories += 1
            try:
                with os.scandir(directory) as entries:
                    for entry in entries:
                        try:
                            if entry.is_dir(follow_symlinks=False):
                                if not entry.is_symlink(): stack.append(entry.path)
                            elif entry.is_file(follow_symlinks=False):
                                current += 1
                                if key(entry.path) not in known:
                                    sink.write(entry.path + "\n"); new += 1
                        except OSError as exc:
                            errors.append({"path": entry.path, "error": type(exc).__name__})
            except OSError as exc:
                errors.append({"path": directory, "error": type(exc).__name__})
    return {"storage": drive, "current_path_enumeration": "PASS" if not errors else "PARTIAL",
            "current_path_count": current, "new_path_candidate_count": new,
            "count_confirmed": not errors, "unexamined_remainder": 0 if not errors else len(errors),
            "directories_visited": directories, "error_count": len(errors),
            "errors": errors[:100], "path_list": str(output.relative_to(ROOT)).replace("\\", "/")}

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    known, counts = known_keys()
    results = []
    for drive in DRIVES:
        row = enumerate_once(drive, known[drive]); row["known_path_count"] = counts[drive]; results.append(row)
        (OUT / "progress.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    confirmed = [x for x in results if x["count_confirmed"]]
    summary = {"schema":"wic.storage.path-delta-once.v1", "method":"CURRENT_PATH_SET_MINUS_KNOWN_PATH_SET",
      "connected_storage_count":len(results), "confirmed_storage_count":len(confirmed),
      "total_new_path_candidate_count":sum(x["new_path_candidate_count"] for x in results) if len(confirmed)==len(results) else "UNKNOWN",
      "count_unconfirmed_storage":len(results)-len(confirmed),
      "unexamined_remainder":sum(x["unexamined_remainder"] for x in results),
      "connected_storage_new_file_count_complete":len(confirmed)==len(results),
      "content_read":False, "file_hashing":False, "originals_modified":False, "storage":results}
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == "__main__": main()
