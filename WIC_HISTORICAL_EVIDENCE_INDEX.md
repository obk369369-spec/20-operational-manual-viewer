# WIC HISTORICAL EVIDENCE INDEX

상태: ACTIVE IMPLEMENTATION INDEX — 규범 원본은 `WIC_GLOBAL_OPERATING_RULES.md`
최종 갱신: 2026-08-10 11:56 KST

목적: 사용자가 지난 대화/파일/스크린샷 피드백을 다시 설명하지 않도록, 도구별로 이미 회수한 역사증거와 아직 처리할 증거를 기록한다. 이 파일은 새 규칙 원본이 아니라 `이미 처리한 증거의 색인 + 회귀 fixture 후보 + 재시작점`이다.

## 공통 폐쇄루프
`새/과거 피드백 회수 -> 대상 도구/기능 분류 -> 기대 동작 추출 -> 현재 구현 비교 -> fixture/error_hash 생성 -> 실제 구현 패치 또는 정확한 Work handoff -> 검증 -> evidence index 갱신`

금지: 같은 역사자료를 매 회차 처음부터 다시 읽기 / 사용자가 같은 오류를 다시 사진으로 증명하게 하기 / status·shell만 고치고 실제 엔진을 고쳤다고 판정하기.

## TOOL001 — 1번 고객 자동화 안내서
### 실제 저장소
- `obk369369-spec/01-auto-guide-v1`
- 현재 GitHub `index.html`: RUN23_B_CLEAN_QUALITY 계열. 중앙규칙 포인터 commit `55098c827d8e834143232b4e91c5f199448605eb`.

### 이번에 새로 회수·처리한 역사증거
1. `1번 고객 자동화 안내서 12.doc` — 1번의 안정판 정의와 작업경계.
   - 오른쪽 성공판을 먼저 잠그고 새 HTML 구조를 만들지 않는다.
   - 당시 왼쪽 최소 입력은 영문/한글제목, 발행사, 발행일, 페이지, 정가, 공급가, 링크, 목차 9칸 + 생성버튼 1개였다.
   - 이후 사용자가 실제 기준 양식으로 `안내자료양식(시장 보고서)-월드산업정보센터.htm`을 제공했고, 오른쪽 양식 자체보다 연결 작업을 우선해야 한다는 피드백이 축적됐다.
2. `1번 고객 자동화 안내서 9.doc`
   - 실제 목표 흐름: 고객입력 -> 분석 -> 실제 존재 보고서/링크 검증 -> 서로 다른 보고서 5개 -> 오른쪽 카드/안내서 -> 사용자 선택.
   - 오류 피드백은 다음 생성에 재사용되어야 한다.
3. `1번 고객 자동화 안내서 10.doc`
   - 자동발송이 아니라 발송 직전 완성형이 우선.
   - 제목/첫문장/자료배열을 분산한 5개 메일 세트 + 스팸회피 + 위험표시가 목표.
4. `1번 고객 자동화 안내서 14.doc`
   - clicked_trace / first_fail / diag_packet / 변경감지 구조가 존재했지만, 사용자가 직접 찍어 보내야 확인되는 구조 자체가 실패로 지적됨.
5. `1번 고객 자동화 안내서 21.txt`
   - `5개 생성`이라는 기능명은 실제 5개 카드가 보일 때만 PASS 후보.
   - ONLINE_FETCH가 OFF였던 단계가 명시되어 있어 과거 `5개 카드 생성`만으로 실데이터 PASS 처리하면 안 됨.
6. Library의 `안내서_전체_연결버전.html`
   - 검증된 실제 데이터를 넣는 입력->오른쪽 양식 매퍼 후보.
7. Library의 `1번도구_정상미리보기_좌중우_5안내서_v14.html`
   - 자동 제목/가격/페이지 및 placeholder URL 생성이 있어 생산경로 synthetic generator로 격리.

### TOOL001 회귀 fixture 후보
- T1-F001 `STABLE_BASELINE_PRESERVE`: 오른쪽 기준양식 DOM/스타일은 입력연결 패치 전후 동일해야 함.
- T1-F002 `REAL_DATA_ONLY`: 보고서 제목/발행사/연도/페이지/가격/링크/TOC는 검증된 실제 데이터 없이는 출력 금지.
- T1-F003 `FIVE_MEANS_FIVE`: `안내서 5개 생성` PASS는 서로 다른 검증 보고서 5개 + 실제 오른쪽 5개 출력이 동시에 있어야 함.
- T1-F004 `NO_PLACEHOLDER_REPORT`: example.com, 가상 제목, 산술식 페이지/가격, 회사 홈페이지를 개별 보고서 링크처럼 대체하는 생성 금지.
- T1-F005 `USER_FEEDBACK_NO_RETEST`: 동일 first_fail/error_hash가 이미 기록됐으면 같은 사용자 스크린샷/클릭을 다시 요구하지 않고 자동 회귀검증 대상으로 이동.
- T1-F006 `CONTACT_TO_GUIDE_LOOP`: 실제 최근활동 기반 전화멘트 -> 통화에서 얻은 직접정보 -> 고객입력 보강 -> 안내서/메일 재생성.
- T1-F007 `SEND_READY_NOT_AUTO_SEND`: 검증 결과는 발송 직전 완성형까지 자동화하며 실제 외부발송은 별도 권한 게이트.

### 현재 판정
- 역사규칙 회수: PASS(부분, 계속 증분 회수)
- 실제 Tool1 엔진에 위 fixture 자동테스트 연결: HOLD
- 생산 안정판 확정 + 실데이터 E2E: HOLD

### 다음 미처리 증거
- `1번 고객 자동화 안내서 16/21/22/23`에서 stable baseline 후보명, 최초 성공본, first_fail/error_hash, 목차 배치 규칙을 추가 추출.
- GitHub RUN23 실제 index의 synthetic/실데이터 경계와 기존 test hook을 코드 수준으로 매핑.

## TOOL006 — 6번 목차 정리
### 실제 저장소
- `obk369369-spec/06-toc-check`
- 중앙규칙 포인터 commit `4f8ef03f4fac2ae0a317697b8d20d544c123451b`.
- 과거 저장소에 `index_ 그나마 안정 버전.html` 명칭의 역사 안정 후보 흔적이 있음.

### 이번에 새로 회수·처리한 역사증거
1. `6번 목차 정리 도구 2.doc`
   - MarketsandMarkets는 다른 발행사보다 난도가 높고 과거 반복 테스트에도 완전통과하지 못한 경험이 명시됨.
   - 따라서 `Chat이 자동으로 더 안정적`이라고 가정하지 않는다.
2. `Full 버전 목차.doc` 계열
   - MarketsandMarkets: 상위목차 인식 실패/들여쓰기 무시.
   - Allied: 중간 숫자 목차 누락.
   - Acumen: 소문자 섞인 상위목차 오탐.
   - GlobalData: 하위 항목 병합 오류.
   - Technavio: 분할 라인 연결 실패.
   - 숫자 기반 계층, `.1/.1.1` 구조, List of/Figures/Companies/Abbreviations 제거, 병합문 재분리 규칙이 역사적으로 시도됨. 과거 선언된 테스트 횟수/성공률은 실제 외부증거 없이는 현재 PASS 근거로 사용하지 않는다.
3. `붙여넣은 텍스트 (1).txt` — 실제 MarketsandMarkets clicked_trace/first_fail 기록.
   - 다수 실제 M&M metadata 파일이 입력으로 기록됨.
   - clicked_trace에 `1 INTRODUCTION 28 1.1 STUDY OBJECTIVES ...` 형태 실제 목차가 존재.
   - first_fail=`05 재검증 미완료`, state=`TESTED`, reason=`재검증 버튼 미통과`.
4. `MarketsandMarkets_칼럼불일치_파일명보고.txt`
   - M&M 원본 자체가 `Table of Contents`, `Table of Contents 2`, `List Of Tables`, `List Of Tables 2/3...`, `List Of Figures` 등 여러 칼럼 변형을 가지며 파일마다 구조가 달랐음.

### TOOL006 회귀 fixture 후보
- T6-MNM-001 `HIERARCHY`: `1 INTRODUCTION`, `1.1 ...`, `1.3.1 ...` 깊이를 보존하며 페이지번호 숫자만 독립 항목으로 남기지 않음.
- T6-MNM-002 `COLUMN_VARIANTS`: Table of Contents / Table of Contents 2 / List Of Tables n / List Of Figures 변형을 원본 소스구분과 함께 처리.
- T6-MNM-003 `NO_NUMERIC_GARBAGE`: 29/34/45 같은 페이지번호 단독 줄 제거. 제목에 속한 번호는 보존.
- T6-MNM-004 `MERGE_SPLIT`: 줄이 붙거나 분리된 원문을 제목 손실 없이 재결합/재분리.
- T6-MNM-005 `REVALIDATION`: first_fail 05가 TESTED에서 사라졌다고 PASS하지 말고 재검증 결과가 실제 출력과 일치해야 PASS.
- T6-MNM-006 `USER_APPROVED_GOLDEN`: 사용자 승인 최종 TOC가 발견될 때마다 원본->승인본 pair를 golden fixture로 추가하고 동일 패턴 재질문 금지.

### 현재 판정
- M&M 역사 오류군 회수: PASS(첫 묶음)
- 사용자 승인 원본->최종 TOC golden pair 직접 식별: HOLD
- 6번 현행 엔진에 fixture 자동회귀 연결: HOLD

### 다음 미처리 증거
- M&M 실제 원본/사용자 승인 결과 pair를 대화기록에서 우선 탐색.
- 현행 `06-toc-check` index와 과거 안정후보의 처리함수 비교 후 fixture 실행지점을 고정.

## 전체 도구 공통 확장 상태
각 도구마다 아래 색인 필드를 순차 생성한다.
`INPUT / RULE / OUTPUT / VALIDATION / ERROR_HASH / REUSE / STABLE_BASELINE / REGRESSION_FIXTURES / LAST_PROCESSED_EVIDENCE`

현재 우선순위: TOOL001 -> TOOL006 -> 이메일수집/7번 -> 37 -> 13 -> 2 -> 나머지 등록도구.

## LAST PROCESSED EVIDENCE
- 2026-08-10 11:56 KST: TOOL001 역사자료 12/9/10/14/21 + HTML 2종, TOOL006 역사자료 6번2/Full목차/M&M clicked_trace/M&M 칼럼변형 첫 묶음 처리.
- 다음 회차는 위 항목 재검색 금지. `1번 16/21/22/23 세부 성공판·error_hash`와 `M&M 원본->사용자승인 최종 TOC pair`부터 시작.
