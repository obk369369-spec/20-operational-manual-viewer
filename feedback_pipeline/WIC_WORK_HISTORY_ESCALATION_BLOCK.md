# WIC WORK HISTORY ESCALATION BLOCK

상태: REQUIRED / COMMON RULE
기준일: 2026-09-03

## 목적
현재 TOOL의 대표 실제입력, 실제 버튼 조작, 이전 정상판/MASTER 대조까지 했는데도 Work가 테스트 완전성을 충분히 입증하지 못한다고 판정할 때만, 사용자가 과거 첨부한 대화기록에서 해당 TOOL의 장기 테스트 기록을 추가 증거로 반복 검색한다.

## 강제 조건
- 발동 조건: `TEST_INSUFFICIENT`, `EXPECTED_WEAK`, `RECURRENCE_RISK_HIGH`, `NORMAL_BEHAVIOR_UNRESOLVED` 중 하나 이상.
- 발동 전에는 과거 전체대화 전수조사를 하지 않는다.
- 발동 후에는 현재 TOOL 번호·기능명·오류증상·버튼명·필드명·과거 사용자 표현을 키로 관련 기록만 찾는다.
- 첫 검색이 부족하면 동의어·과거 명칭·버튼명·필드명·오류문구를 바꿔 반복 검색한다.
- 1년 이상 누적된 같은 TOOL의 테스트·오류·사용자 수정·정상 기대값·이전 PASS/FAIL 기록을 현재 MASTER/이전 정상판/ACTUAL과 대조한다.
- 과거 기록에서 사용자가 직접 고친 EXPECTED, 동일 입력 반복 실패, 이전 정상판에서 작동한 버튼/출력, 나중에 사라진 기능을 우선 증거로 사용한다.
- 최신 명시 지시와 과거 기록이 충돌하면 최신 명시 지시가 우선이다.
- 기존 TOOL별 index/registry/canonical catch-up/golden pair/fixture가 있으면 먼저 재사용하고, 충분하면 원문 대량검색을 SKIP_REUSE한다.
- 과거 기록을 찾았다는 사실만으로 PASS하지 않는다. 보강된 EXPECTED로 실제 기능을 다시 테스트하여 EXPECTED↔ACTUAL과 영향 회귀가 PASS해야 종료한다.
- 이 역사자료 탐색은 마지막 정확도 보강 수단이며 실제 기능 테스트를 대신하지 않는다.

## 크레딧 보호
- 이 단계는 실제 기능 테스트보다 크레딧을 더 많이 소모할 수 있으므로 자동 상시 실행 금지.
- 먼저 현재 기능 테스트와 이전 정상판 대조를 수행한다.
- 테스트가 충분하면 역사검색은 하지 않는다.
- 테스트가 불충분한 경우에만 해당 TOOL 범위로 좁혀 반복 검색한다.
- 전체 278개/전체 TOOL 일괄 재분석은 금지하고 기존 검색 인덱스와 이미 승격된 MASTER를 우선 재사용한다.

HISTORY_ESCALATION_ONLY_WHEN_TEST_INSUFFICIENT = REQUIRED
TOOL_SCOPED_HISTORY_SEARCH = REQUIRED_ON_ESCALATION
REPEAT_SEARCH_WITH_VARIANTS_UNTIL_EXPECTED_RESOLVED = REQUIRED
ALL_TOOL_HISTORY_AUDIT_BY_DEFAULT = FORBIDDEN
HISTORY_SEARCH_REUSES_INDEX_FIRST = REQUIRED
LATEST_EXPLICIT_USER_RULE_WINS = TRUE
HISTORY_SEARCH_IS_NOT_FUNCTIONAL_PASS = TRUE
HISTORY_SEARCH_CREDIT_HEAVY = TRUE
FUNCTIONAL_TEST_BEFORE_HISTORY_SEARCH = REQUIRED
