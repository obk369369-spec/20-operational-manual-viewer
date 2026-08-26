# Work16 Next Work Queue

## OPEN candidate — cross-chat historical record auto-retrieval

- source: 16번 워크 이어서 하기 / TOOL002 lookup incident
- observed symptom: 2번 대화창이 TOOL002의 최근 자동화 논의 기록을 찾을 때 현재 대화/직접 보이는 기록만 보고 2026-03-16을 가장 직접적인 기록으로 판단했고, Library/GitHub에 보존된 다른 TOOL002 자료를 자동으로 먼저 조회하지 못함.
- user impact: 사용자가 다른 대화창에서 이미 논의한 내용을 다시 설명하거나, 어느 대화창에서 논의했는지 직접 찾아 전달해야 함.
- proposed root: GAP-CROSSCHAT-HISTORICAL-RECORD-AUTO-RETRIEVAL
- relation to existing roots: L4-12(master propagation) 및 L4-13(handoff)와 관련되지만 동일 root로 단정하지 말 것. 다음 Work 시작 시 기존 root/evidence와 dedup 판정 후 동일 원인이면 recurrence로 병합.
- required behavior: 도구번호/업무가 식별되면 현재 대화만 보지 말고 해당 TOOL의 GitHub master/checkpoint/handoff와 Library 보존 기록을 우선 검색하여 최근 관련 논의/마지막 작업지점을 회수. 사용자가 과거 내용을 복사해 다시 입력하게 하지 않음.
- PASS gate: TOOL002 대표 사례에서 현재 chat only 판정이 아니라 Library + GitHub records를 자동 회수하여 최신 관련 기록/마지막 작업지점을 재현하고, 다른 canonical TOOL 1건에서도 동일 경로가 재사용됨을 최소 fixture로 확인.
- constraints: 전 대화 전수조사 금지, 전체 Library 스캔 금지, 해당 TOOL 식별 후 scoped search만 수행, 기존 PASS는 SKIP-REUSE, DIFF ONLY, 정상 commit/push/read-back 후 checkpoint 갱신.
- status: OPEN_CANDIDATE / WORK_READY_FOR_DEDUP
