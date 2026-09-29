from pathlib import Path

page = (Path(__file__).parents[1] / "observer" / "index.html").read_text(encoding="utf-8")
for text in ("지금 하는 일", "현재 상태", "끝난 일", "아직 할 일", "지금 할 수 없는 일",
             "다음 할 일", "마지막 상태 변경", "자세히 보기", "setInterval(refresh,60000)"):
    assert text in page, text
first = page.split("<details>", 1)[0]
for hidden_term in ("ROOT", "ACK", "SHA", "read-back", "runtime", "contract", "lane", "handoff", "checkpoint", "PARTIAL", "UNFINISHED"):
    assert hidden_term not in first, hidden_term
assert "wic_non_tool_observer_closeout_report.json" in page
print("WIC_OBSERVER_DASHBOARD: PASS (12/12)")
