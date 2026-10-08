"""One authorized C: traversal that persists every error path immediately."""
from __future__ import annotations
import json, os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PRIOR=ROOT/".inventory_runtime/storage_path_delta_20261008/summary.json"
OUT=ROOT/".inventory_runtime/c_error_identity_once_20261008"
ERRORS=OUT/"all_error_paths.jsonl"
SUMMARY=OUT/"summary.json"

def normalized(path: str) -> str:
    return os.path.normcase(os.path.normpath(path))

def classification(path: str, error: str) -> tuple[str,str]:
    low=normalized(path)
    system_prefixes=tuple(normalized(x) for x in (
        r"C:\Windows", r"C:\Program Files", r"C:\Program Files (x86)", r"C:\ProgramData",
        r"C:\$Recycle.Bin", r"C:\System Volume Information", r"C:\Recovery"))
    if error=="FileNotFoundError": return "SYSTEM_NON_TARGET_EXCLUDED","TRANSIENT_PATH_NO_LONGER_EXISTS"
    if low.startswith(system_prefixes): return "SYSTEM_NON_TARGET_EXCLUDED","WINDOWS_OR_APPLICATION_PROTECTED"
    if any(x in low for x in ("\\node_modules\\","\\appdata\\local\\packages\\","\\appdata\\local\\temp\\")):
        return "SYSTEM_NON_TARGET_EXCLUDED","DEPENDENCY_CACHE_OR_TEMP"
    return "PERMISSION_BLOCKED_RELEVANT","POTENTIAL_USER_OR_WIC_PATH"

def persist(handle, row: dict) -> None:
    handle.write(json.dumps(row,ensure_ascii=False)+"\n"); handle.flush(); os.fsync(handle.fileno())

def main() -> None:
    OUT.mkdir(parents=True,exist_ok=False)
    prior=json.loads(PRIOR.read_text(encoding="utf-8"))
    prior_c=next(x for x in prior["storage"] if x["storage"]=="C:")
    locked={normalized(x["path"]) for x in prior_c["errors"]}
    stack=["C:\\"]; error_rows=[]; directories=0
    with ERRORS.open("x",encoding="utf-8",newline="\n") as sink:
        while stack:
            directory=stack.pop(); directories+=1
            try:
                with os.scandir(directory) as entries:
                    for entry in entries:
                        try:
                            if entry.is_dir(follow_symlinks=False) and not entry.is_symlink(): stack.append(entry.path)
                        except OSError as exc:
                            row={"path":entry.path,"error":type(exc).__name__}; persist(sink,row); error_rows.append(row)
            except OSError as exc:
                row={"path":directory,"error":type(exc).__name__}; persist(sink,row); error_rows.append(row)
    unique={normalized(x["path"]):x for x in error_rows}
    duplicate=sorted(set(unique).intersection(locked)); new=[unique[k] for k in sorted(set(unique)-locked)]
    classified=[]
    for row in new:
        result,reason=classification(row["path"],row["error"])
        classified.append({**row,"result":result,"reason":reason})
    system=sum(x["result"]=="SYSTEM_NON_TARGET_EXCLUDED" for x in classified)
    blocked=[x for x in classified if x["result"]=="PERMISSION_BLOCKED_RELEVANT"]
    result={"schema":"wic.storage.c-error-identities-once.v1","storage":"C:",
      "c_total_error_path_count":len(unique),"existing_locked_duplicate_count":len(duplicate),
      "new_unprocessed_identity_count":len(new),"system_non_target_excluded_count":system,
      "real_user_wic_related_resolved_count":0,"permission_blocked_count":len(blocked),
      "final_relevant_unconfirmed_count":len(blocked),"storage_c_discovery_complete":len(blocked)==0,
      "directories_visited":directories,"all_errors_path":str(ERRORS.relative_to(ROOT)).replace("\\","/"),
      "permission_blocked_paths":blocked,"normal_file_paths_persisted":0,"content_read":False,
      "file_hashing":False,"other_storage_enumerated":False,"originals_modified":False}
    SUMMARY.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="permission_blocked_paths"},ensure_ascii=False))
if __name__=="__main__": main()
