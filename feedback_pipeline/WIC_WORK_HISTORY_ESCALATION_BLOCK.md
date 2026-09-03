# WIC WORK HISTORY ESCALATION BLOCK

상태: REQUIRED / COMMON RULE
기준일: 2026-09-03

## 목적
현재 TOOL의 대표 실제입력, 실제 버튼 조작, 이전 정상판/MASTER 대조까지 했는데도 Work가 테스트 완전성을 충분히 입증하지 못한다고 판정할 때만, 사용자가 과거 첨부한 대화기록에서 해당 TOOL의 장기 테스트 기록을 추가 증거로 반복 검색한다.

## 강제 조건
- 발동 조건: `TEST_INSUFFICIENT`, `EXPECTED_WEAK`, `RECURRENCE_RISK_HIGH`, `NORMAL_BEHAVIOR_UNRESOLVED` 중 하나 이상.
- 발동 전에는 과거 전체대화 전수조사를 하지 않는다.
- 발동 후에도 `파일명에 TOOL 번호/도구 이름/관련 단어가 있다`는 이유만으로 파일 전체, 폴더 전체, 대화 전체를 열어보거나 전수검색하지 않는다.
- 먼저 현재 문제를 `TOOL 번호 + 기능명 + 오류증상 + 버튼명/필드명 + 사용자 핵심 표현`으로 좁히고, 검색 결과에서 실제 관련 구간만 읽는다.
- 검색 결과가 넓게 나오면 파일 전체를 읽지 말고 더 구체적인 기능명·오류문구·과거 명칭·사용자 표현으로 재검색하여 범위를 축소한다.
- 첫 검색이 부족하면 동의어·과거 명칭·버튼명·필드명·오류문구를 바꿔 반복 검색하되, 매 반복은 이전 검색에서 얻은 관련 단서만 사용해 더 좁아져야 한다.
- `관련 기록을 찾기 위한 반복 검색`은 허용하지만, `관련 기록이 있을 것 같아서 전체를 먼저 뒤지는 방식`은 금지한다.
- 1년 이상 누적된 같은 TOOL 기록도 필요한 관련 구간만 찾아서 테스트·오류·사용자 수정·정상 기대값·이전 PASS/FAIL을 현재 MASTER/이전 정상판/ACTUAL과 대조한다.
- 과거 기록에서 사용자가 직접 고친 EXPECTED, 동일 입력 반복 실패, 이전 정상판에서 작동한 버튼/출력, 나중에 사라진 기능을 우선 증거로 사용한다.
- 최신 명시 지시와 과거 기록이 충돌하면 최신 명시 지시가 우선이다.
- 기존 TOOL별 index/registry/canonical catch-up/golden pair/fixture가 있으면 먼저 재사용하고, 충분하면 원문 검색 자체를 SKIP_REUSE한다.
- 파일명·폴더명·TOOL명 매칭만으로 원문 전체를 읽지 않는다. 반드시 내용 검색으로 관련 구간이 확인된 뒤 필요한 최소 범위만 읽는다.
- 과거 기록을 찾았다는 사실만으로 PASS하지 않는다. 보강된 EXPECTED로 실제 기능을 다시 테스트하여 EXPECTED↔ACTUAL과 영향 회귀가 PASS해야 종료한다.
- 이 역사자료 탐색은 마지막 정확도 보강 수단이며 실제 기능 테스트를 대신하지 않는다.

## 크레딧 보호
- 이 단계는 실제 기능 테스트보다 크레딧을 더 많이 소모할 수 있으므로 자동 상시 실행 금지.
- 먼저 현재 기능 테스트와 이전 정상판 대조를 수행한다.
- 테스트가 충분하면 역사검색은 하지 않는다.
- 테스트가 불충분한 경우에만 해당 TOOL의 해당 기능/오류 범위로 좁혀 반복 검색한다.
- 전체 278개/전체 TOOL/전체 폴더/전체 파일 일괄 재분석은 금지한다.
- 검색은 `좁은 쿼리 → 관련 스니펫/구간 확인 → 필요한 최소 원문 범위 읽기` 순서로만 진행한다.
- 결과가 없다고 즉시 전체검색으로 확대하지 않는다. 먼저 검색어를 기능·오류·버튼·필드·사용자 표현 기준으로 변형한다.
- 기존 검색 인덱스와 이미 승격된 MASTER를 우선 재사용한다.

HISTORY_ESCALATION_ONLY_WHEN_TEST_INSUFFICIENT = REQUIRED
TOOL_SCOPED_HISTORY_SEARCH = REQUIRED_ON_ESCALATION
FUNCTION_SCOPED_HISTORY_SEARCH = REQUIRED
REPEAT_SEARCH_WITH_VARIANTS_UNTIL_EXPECTED_RESOLVED = REQUIRED
ALL_TOOL_HISTORY_AUDIT_BY_DEFAULT = FORBIDDEN
FULL_FILE_SCAN_BY_FILENAME_MATCH = FORBIDDEN
FULL_FOLDER_SCAN_BY_TOOLNAME_MATCH = FORBIDDEN
BROAD_SEARCH_BEFORE_NARROW_QUERY = FORBIDDEN
SEARCH_SNIPPET_BEFORE_FULL_READ = REQUIRED
MINIMUM_RELEVANT_RANGE_READ = REQUIRED
HISTORY_SEARCH_REUSES_INDEX_FIRST = REQUIRED
LATEST_EXPLICIT_USER_RULE_WINS = TRUE
HISTORY_SEARCH_IS_NOT_FUNCTIONAL_PASS = TRUE
HISTORY_SEARCH_CREDIT_HEAVY = TRUE
FUNCTIONAL_TEST_BEFORE_HISTORY_SEARCH = REQUIRED
