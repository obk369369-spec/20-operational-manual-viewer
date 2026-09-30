from pathlib import Path

page = (Path(__file__).parents[1] / "observer" / "index.html").read_text(encoding="utf-8")
for text in ("지금 하는 일", "현재 상태", "끝난 일", "아직 할 일", "지금 할 수 없는 일",
             "다음 할 일", "마지막 상태 변경", "자세히 보기", "setInterval(refresh,60000)"):
    assert text in page, text
first = page.split("<details>", 1)[0]
for hidden_term in ("ROOT", "ACK", "SHA", "read-back", "runtime", "contract", "lane", "handoff", "checkpoint", "PARTIAL", "UNFINISHED"):
    assert hidden_term not in first, hidden_term
assert "wic_non_tool_observer_closeout_report.json" in page
assert "필요한 장치가 준비되면 자동으로 다시 시작합니다." in page
assert '<summary>기술정보</summary>' in page
for text in ("도구별 남은 일과 예상기간", "남은 작업:", "남은 수:", "예상 남은 기간:", "계산 중", "시간 남음"):
    assert text in page, text
print("WIC_OBSERVER_DASHBOARD: PASS (20/20)")
