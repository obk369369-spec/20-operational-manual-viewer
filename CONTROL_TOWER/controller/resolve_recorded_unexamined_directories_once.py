"""Resolve only the unexamined directory paths preserved by the prior one-shot run."""
from __future__ import annotations
import json, os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/".inventory_runtime/storage_path_delta_20261008/summary.json"
OUT=ROOT/".inventory_runtime/storage_path_delta_20261008/unexamined_resolution.json"

def system_non_target(path: str, error: str) -> tuple[bool,str]:
    low=path.lower().replace("/","\\")
    if low.startswith("c:\\windows\\"): return True,"WINDOWS_SYSTEM_PROTECTED_OR_TRANSIENT"
    if "\\node_modules\\" in low: return True,"DEPENDENCY_VIRTUAL_OR_TRANSIENT_PATH"
    if any(x in low for x in ("\\system volume information", "\\$recycle.bin\\", "\\recovery")):
        return True,"SYSTEM_RECOVERY_OR_RECYCLE"
    if error=="FileNotFoundError" and not os.path.exists(path): return True,"TRANSIENT_PATH_NO_LONGER_EXISTS"
    return False,"POTENTIAL_USER_OR_WIC_PATH"

def inspect_once(path: str) -> tuple[str,int,str|None]:
    count=0; stack=[path]
    try:
        while stack:
            current=stack.pop()
            with os.scandir(current) as entries:
                for entry in entries:
                    if entry.is_dir(follow_symlinks=False):
                        if not entry.is_symlink(): stack.append(entry.path)
                    elif entry.is_file(follow_symlinks=False): count+=1
        return "RESOLVED",count,None
    except OSError as exc:
        return "PERMISSION_BLOCKED",count,type(exc).__name__

def main() -> None:
    if OUT.exists(): raise RuntimeError("REPEAT_UNEXAMINED_RESOLUTION_BLOCKED")
    source=json.loads(SOURCE.read_text(encoding="utf-8")); rows=[]
    initial={x["storage"]:x["unexamined_remainder"] for x in source["storage"]}
    recorded=0; excluded=resolved=additional=blocked=0
    for storage in source["storage"]:
        for item in storage["errors"]:
            recorded+=1; path=item["path"]
            is_system,reason=system_non_target(path,item["error"])
            if is_system:
                excluded+=1; rows.append({"storage":storage["storage"],"path":path,"result":"SYSTEM_NON_TARGET_EXCLUDED","reason":reason}); continue
            result,count,error=inspect_once(path)
            if result=="RESOLVED": resolved+=1; additional+=count
            else: blocked+=1
            rows.append({"storage":storage["storage"],"path":path,"result":result,"additional_file_count":count,"error":error})
    missing=sum(initial.values())-recorded
    result={"schema":"wic.storage.unexamined-resolution.v1","initial":initial,
      "initial_total":sum(initial.values()),"recorded_path_count":recorded,"unrecorded_error_path_count":missing,
      "system_non_target_excluded_count":excluded,"directly_resolved_count":resolved,
      "real_user_wic_path_resolved_count":resolved,"permission_blocked_relevant_count":blocked,
      "additional_file_count_from_recorded_paths":additional,"previous_candidate_count":2105850,
      "final_discovered_file_count":2105850+additional,
      "unexamined_relevant_remainder":"UNKNOWN" if missing else blocked,
      "storage_file_discovery_complete":missing==0 and blocked==0,
      "content_read":False,"hashing":False,"originals_modified":False,"paths":rows}
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="paths"},ensure_ascii=False))
if __name__=="__main__": main()
