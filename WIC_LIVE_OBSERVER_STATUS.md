# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 11:59 KST
상태: ACTIVE — 과거 피드백 → 회귀 fixture → 실제 도구 개선 선순환 시작

이 파일은 사용자가 직접 테스트하지 않고 진행을 관찰하기 위한 외부 상태판이다. 실제 외부 증거가 있을 때만 진행으로 기록한다. 과거 상세 증거는 `WIC_HISTORICAL_EVIDENCE_INDEX.md`에서 도구별 처리여부와 재시작점을 관리한다.

## 이번 회차 실제 작업 — 11:49~11:59
- 직전 11:10 재시작점을 읽고, 이미 처리한 안내서 HTML 2종과 28번 증거묶음은 반복검사하지 않았다.
- File Library에서 1번/6번 과거 대화기록을 새로 회수했다. 사용자에게 다시 테스트·사진·설명을 요구하지 않고 역사기록 자체를 개선 입력으로 사용했다.
- 중앙 구현색인 `WIC_HISTORICAL_EVIDENCE_INDEX.md`를 신규 생성했다. 규범 원본을 복제하는 문서가 아니라 `도구별 이미 처리한 증거 / regression fixture 후보 / LAST_PROCESSED_EVIDENCE / 다음 재시작점`만 저장한다. commit `d8324831b955119a4d4ecb9f5dd10b78e6994586`.
- 실제 1번 저장소 `obk369369-spec/01-auto-guide-v1`를 다시 식별하고 현재 `index.html`이 RUN23_B_CLEAN_QUALITY 계열임을 확인했다. 최신 중앙규칙 연결 commit은 `55098c827d8e834143232b4e91c5f199448605eb`이다.
- 1번 과거 기록에서 다음을 회귀게이트로 승격했다: `오른쪽 성공판 보존`, `검증 실데이터만`, `5개 생성=실제 서로 다른 검증보고서 5개`, `placeholder/가상 가격·페이지 금지`, `같은 first_fail 사용자 재테스트 금지`, `실제 최근활동→전화→새 정보→안내서 재생성`, `SEND_READY와 실제 발송 분리`.
- 위 7개를 실제 1번 저장소에 `tests/historical_regression_fixtures.json`으로 저장했다. commit `6dd6a2209b121efa26bc3e6d815072653e659fe7`. 아직 실행테스트 연결 전이므로 기능 PASS라고 하지 않는다.
- 실제 6번 저장소 `obk369369-spec/06-toc-check`를 확인했다. 최신 중앙규칙 연결 commit `4f8ef03f4fac2ae0a317697b8d20d544c123451b`, 과거 `index_ 그나마 안정 버전.html` 흔적도 commit history에서 확인했다.
- MarketsandMarkets 역사자료에서 `상위목차 인식/들여쓰기`, `페이지 숫자 단독행`, `병합·분할 라인`, `Table of Contents/List Of Tables/List Of Figures 다중 칼럼`, `first_fail 05 재검증 미완료`를 첫 회귀묶음으로 고정했다.
- 위 6개 M&M fixture를 실제 6번 저장소 `tests/marketsandmarkets_historical_fixtures.json`으로 저장했다. commit `11be9c01dbaef65d22b365f31e451f75931ab178`. 사용자 승인 원본→최종 TOC golden pair는 아직 직접 식별되지 않아 HOLD다.

## 이번 회차 외부 증거
| 작업 | 판정 | 증거 | 의미 |
|---|---|---|---|
| 역사증거 재사용 색인 | PASS — 저장 | `WIC_HISTORICAL_EVIDENCE_INDEX.md`, commit `d832483...` | 같은 자료 반복읽기/사용자 재설명 감소 |
| 1번 과거 피드백 → fixture | PASS — 저장 | Tool1 commit `6dd6a220...` | 과거 피드백 7개가 실제 저장소 회귀게이트로 이동 |
| 1번 fixture 자동실행 | HOLD | 실행 runner/CI 연결 아직 없음 | 저장만으로 기능 PASS 금지 |
| 6번 M&M 과거오류 → fixture | PASS — 저장 | Tool6 commit `11be9c01...` | M&M 오류군을 반복 질문 대신 테스트 입력으로 보존 |
| M&M user-approved golden pair | HOLD | 원본→승인최종 pair 미식별 | 다음 역사자료 탐색 우선 |
| 6번 fixture 자동실행 | HOLD | 현행 엔진 test hook 연결 전 | Work 이전 Chat/GitHub에서 가능한 연결부터 진행 |

## 과거피드백 → 도구 선순환 구조
1. 새 사용자 피드백 또는 미처리 과거자료 회수.
2. 도구/기능/오류군 분류.
3. 기대 출력과 금지조건 추출.
4. `ERROR_HASH / regression fixture / stable baseline 조건`으로 저장.
5. 실제 도구 저장소에서 구현과 비교.
6. Chat/GitHub/일반 런타임으로 가능한 패치를 먼저 수행.
7. 입력→실행→출력→기대값 비교 후 PASS/HOLD.
8. 사용자에게 같은 오류 재증명 요구 금지.
9. Chat/터미널로 불가능한 마지막 durable multi-file/browser/batch E2E만 Work handoff.

## 1번 고객 자동화 안내서 — 현재
- 실제 GitHub 저장소: `obk369369-spec/01-auto-guide-v1`.
- Library에서 회수한 역사자료는 수십 개이며, 과거 자체 인덱스에는 `1번 고객 자동화 안내서 5~23`이 TOOL001 ACCEPTED로 정리돼 있던 기록도 확인됐다. 즉 과거 피드백 데이터가 실제로 많이 남아 있으며 다시 처음부터 사용자에게 학습받을 필요가 없다.
- 새로 회수된 핵심: 오른쪽 안정영역/기준양식 보존, 9개 핵심 매핑 역사, 실제 5개 검증자료 구조, 메일 5세트/스팸회피, first_fail/clicked_trace, 같은 사용자 테스트 반복 금지.
- `안내서_전체_연결버전.html`은 실데이터 매퍼 후보로 유지.
- v14/RUN 계열은 역사 엔진·진단 자산으로 활용하되 synthetic data 생성부는 생산경로에서 격리.
- 다음 목표: `1번 16/21/22/23`에서 실제 성공판 후보명·error_hash·목차/DOM 동기화 규칙을 증분 추출한 뒤 현재 GitHub index의 test hook과 연결한다.

## 6번 목차 — 현재
- 실제 GitHub 저장소: `obk369369-spec/06-toc-check`.
- MarketsandMarkets는 과거 사용자 기록에서도 반복 테스트 후 완전통과하지 못한 고난도 발행사로 명시되어 있다. Chat이 도구보다 자동으로 낫다고 가정하지 않는다.
- M&M 실제 기록에는 `1 INTRODUCTION 28 1.1 STUDY OBJECTIVES 28 ... 1.3.1 ...` 형태 clicked_trace와 `05 재검증 미완료 / TESTED / 재검증 버튼 미통과`가 남아 있었다.
- M&M 메타데이터는 `Table of Contents`, `Table of Contents 2`, `List Of Tables 2/3...`, `List Of Figures`처럼 파일별 칼럼변형도 존재했다.
- 다음 목표: 사용자 승인 원본→최종 목차 pair를 찾아 golden fixture로 추가하고 현행 엔진 처리함수에 fixture 실행지점을 연결한다.

## 고객응대 루틴 — 고정 파이프라인
`NEW_ONLINE / DORMANT_LEDGER / RECENT_TRADE` → 검증 이메일/DB → 회사소개서·명함 상태 → 7번 판단 → 실제 최근활동 기반 전화멘트 → 직접 통화결과 분기 → FULL_GUIDE / INTERMEDIATE_GUIDE / OTHER_MATERIAL / PRICE_BUDGET / INTERNAL_FORWARD / FOLLOW_UP_DATE / NO_INTEREST / STOP / PURCHASE_PROCUREMENT → TOC/안내서 → 고객응답 → next action/CRM.

## Chat / Work 경계
### Chat에서 먼저 끝낼 것
- 역사자료 검색·증분 색인
- 규칙 추출/충돌 제거
- 각 도구 regression fixture/error_hash 생성
- GitHub 저장소 패치/테스트 코드 연결
- 공식 웹 검증과 실제 샘플 준비
- 개별 source-verified TOC 정리
- 안내서 실데이터 매핑/샘플 파일 생성 가능한 범위

### Work에만 남길 것
- Chat/일반 터미널로 안정적으로 끝낼 수 없는 durable multi-file 구현
- 실제 브라우저 런타임 통합 E2E
- 대량 publisher batch 반복 실행
- 여러 도구 통합 회귀를 지속 실행해야 하는 마지막 구간
- Work에는 과거 규칙 재정리/문서 요약을 시키지 않는다.

## 누적 상태
- 이메일 수집/고객 DB: ACTIVE — 고객응대 루틴 최우선.
- 7번 고객 컨택 판단: 규칙 회수 PASS / 전용 실행엔진 HOLD.
- 1번: 역사피드백→fixture 7개 실제 저장 PASS / 자동 fixture 실행 HOLD / 실데이터 E2E HOLD.
- 6번: M&M 역사오류→fixture 6개 실제 저장 PASS / golden pair HOLD / 자동 회귀실행 HOLD.
- 37번: 메타데이터 생산·통합검증만. 13번과 분리.
- 13번: 엑셀 자동 업로드만. `46145` 회귀 FAIL 유지.
- 2번: 실행본 HOLD.
- 28~31: 고객루틴 직접지원 외 독립 대량조사는 후순위.

## 번호 혼동 금지
- 37번 = 메타데이터 생산·통합검증만.
- 13번 = 엑셀 자동 업로드 도구만.
- 29번 = 발행사 파트너십·계약·커미션·정산 공통관리.
- 30번 = 일본 발행사 파트너십·계약·커미션·정산 상세 실행.
- 31번 = 일본 신규 발행사 발굴·검증·접촉 우선순위.

## 구조 자기개선
- 원인: 과거 사용자 피드백이 대화/파일에 많이 축적됐지만 도구별 회귀테스트로 자동 환류되지 않아, 같은 피드백을 사용자가 반복 제공하는 비정상 루프가 생김.
- 변경: `HISTORICAL_EVIDENCE_INDEX + 실제 도구 repo fixture` 구조를 시작했다.
- 장점: 과거 1년 피드백을 재학습 자산으로 바꾸고, 다음 수정부터 같은 오류를 자동 검사할 기반이 생김. Work 크레딧은 규칙 재정리에 소비하지 않게 됨.
- 새 단점/위험: fixture 파일이 존재해도 자동 runner와 실제 엔진 연결 전에는 기능이 개선됐다고 볼 수 없다. fixture만 늘고 구현이 따라오지 않으면 또 다른 문서화 껍데기가 될 위험이 있다.
- 방지: 다음 회차부터 fixture 추가만 하지 않고 `현행 코드 test hook 연결 또는 실제 패치`를 반드시 묶어서 진행한다. 연결이 안 되면 HOLD + exact Work handoff로 남긴다.
- rollback 조건: evidence index가 중복 규칙문서로 변질되면 규범 내용은 중앙 원본으로 되돌리고 index에는 처리상태/참조만 남긴다.

## 사용자 작업 금지
사용자는 이 상태판을 보기만 한다. 테스트, 비교, 캡처, PASS/FAIL 판정, 규칙 저장, 과거자료 재설명, 같은 오류 재현, `계속/진행` 반복 입력을 요구하지 않는다.

## 재시작 지점
1. TOOL001: `1번 고객 자동화 안내서 16/21/22/23`에서 아직 미처리된 안정판 후보명·first_fail/error_hash·실제 slot/DOM/목차 동기화 규칙 추출.
2. TOOL001: 현재 GitHub `index.html`의 existing test/diagnostic hook에 `tests/historical_regression_fixtures.json`을 어떻게 실행 연결할지 코드 수준 확인 후 가능한 패치 수행.
3. TOOL006: M&M 사용자 승인 원본→최종 TOC pair 우선 탐색. 찾으면 golden fixture 추가.
4. TOOL006: 현행 engine function/test hook 확인 후 fixture 자동회귀 연결 가능한 범위 패치.
5. 이후 이메일 수집 3고객군 DB/SEND_READY 결정형 스키마로 이동.
6. 18:00에는 실제 사용가능/HOLD/Work-only를 정식 보고.

실행시간: duration not exposed
