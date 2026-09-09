from __future__ import annotations
import json, tempfile
from pathlib import Path
from tool016_feedback_bridge import ingest
from tool044_factory_observer_v2 import snapshot

HERE=Path(__file__).resolve().parent
BASE_FILES=("tool044_cloud_state.json","tool044_factory_runtime.json","tool044_atomic_demand_queue.json","VERIFIED_COMPONENT_REGISTRY.json","TOOL044_REQUEST_INBOX.json")

def run():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); (root/"evidence").mkdir()
        for name in BASE_FILES: (root/name).write_bytes((HERE/name).read_bytes())
        (root/"tool044_function_state.json").write_bytes((HERE/"tool044_function_state.json").read_bytes())
        (root/"evidence"/"tool044_verified_composition_pool.json").write_bytes((HERE/"evidence"/"tool044_verified_composition_pool.json").read_bytes())
        base={"source_chat_or_tool":"TOOL006_CHAT","tool_id":"TOOL006","user_original_text":"목차 계층 오류를 고쳐라.","timestamp":"2026-09-09T00:00:00Z"}
        a=ingest(base,root); b=ingest({**base,"timestamp":"2026-09-09T00:01:00Z"},root)
        direct=ingest({"source_chat_or_tool":"TOOL044_OBSERVER_V2","tool_id":"TOOL044","user_original_text":"PDF 브로셔도 별도로 제외해라.","timestamp":"2026-09-09T00:02:00Z"},root)
        other=ingest({"source_chat_or_tool":"TOOL013_CHAT","tool_id":"TOOL013","user_original_text":"카테고리 자동 매칭이 필요하다.","timestamp":"2026-09-09T00:03:00Z"},root)
        snap=snapshot(root); ledger=json.loads((root/"tool016_feedback_intake_ledger.json").read_text(encoding="utf-8")); queue=json.loads((root/"tool044_atomic_demand_queue.json").read_text(encoding="utf-8"))
        assert a["tool044_demand_id"] and direct["tool044_demand_id"] and other["tool044_demand_id"]
        assert a["root_id"]==b["root_id"] and b["duplicate"] and b["occurrence"]==2
        assert len(ledger["roots"])==3 and snap["latest_feedback"][0]["root_id"]==other["root_id"]
        for result in (a,direct,other): assert any(d.get("request_id")==result["tool044_demand_id"] for d in queue["demands"])
        assert snap["truth_boundary"]["any_chat_auto_access"]=="ACCESS_NOT_AVAILABLE"
        return {"status":"PASS","tests":{"tool_a_to_016_to_044":"PASS","tool_b_to_016_to_044":"PASS","tool044_direct_loop":"PASS","root_dedup_occurrence":"PASS","observer_readback":"PASS","unavailable_chat_truth_boundary":"PASS"},"roots":3,"requests":3}

if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False))
