# WIC FEEDBACK → REGRESSION / CHAT → WORK GATE LEDGER

상태: ACTIVE / NON-NORMATIVE EVIDENCE LEDGER
규범 원본: `WIC_GLOBAL_OPERATING_RULES.md`
목적: 과거 대화·파일·사용자 피드백을 실제 도구의 입력·기대출력·회귀테스트로 변환하고, Chat/일반 실행으로 처리 가능한 일을 Work에 넘겨 시간·크레딧을 낭비하지 않도록 실행 증거를 누적한다.

> 이 파일은 규칙 원본이 아니다. 규칙은 `WIC_GLOBAL_OPERATING_RULES.md` 한 곳만 수정한다. 이 파일은 처리 대기/처리 결과/Work 이관 근거를 기록하는 감사·재시작 장부다.

## 1. 사용자 역할 잠금
- 사용자는 관찰자다.
- 사용자는 과거 오류 재설명, 동일 파일 재전송, 반복 테스트, 스크린샷 재제공, PASS/FAIL 판정, 규칙 문서 정리, Work 이관 판단을 담당하지 않는다.
- 필요한 과거 증거는 Chat/Files/GitHub에서 먼저 회수한다.
- 이미 기록된 오류는 새 증거가 없는 한 사용자에게 재현을 요구하지 않는다.

## 2. 영구 처리 파이프라인
각 도구/업무 대화창은 다음 순서로 처리한다.

`HISTORY_EVIDENCE -> CLASSIFY -> RULE/EXPECTED_OUTPUT -> FIXTURE/ERROR_HASH -> ACTUAL_PATCH -> VERIFY -> READ_BACK -> REUSE -> RESTART_POINT`

필수 필드:
- tool_or_chat
- source_file_or_chat
- source_location
- input_example
- expected_output
- rule_extracted
- regression_fixture
- error_hash_or_signature
- implementation_target
- verification_method
- verification_result
- reusable_scope
- last_processed_evidence
- next_unprocessed_evidence

## 3. Work 이관 차단 게이트
Work로 넘기기 전에 아래를 순서대로 검사한다.

### G1 — Chat/Files로 가능한가
가능 예:
- 과거 대화·파일 검색
- 규칙 추출/충돌 제거
- 고객 DB/스키마 정리
- 실제 공식 출처 조사
- HTML/문서/엑셀 구조 분석
- fixture/error_hash/기대출력 작성

가능하면 Work 이관 금지.

### G2 — GitHub 연결도구로 가능한가
가능 예:
- 저장소 코드/문서 읽기
- 실제 파일 수정/커밋
- 테스트 파일/fixture 추가
- read-back 검증

가능하면 Work 이관 금지.

### G3 — 일반 실행/터미널로 가능한가
가능 예:
- 로컬 HTML/JS/Python 실행
- 정규식/파서 회귀테스트
- 파일 변환/비교
- 결정형 테스트
- 대량 정적 데이터 검사

일반 실행으로 충분하면 Work 이관 금지.

### G4 — Work 전용성이 실제로 남았는가
Work 후보는 다음에 한정한다.
- 여러 파일/저장소를 오랫동안 연속 수정해야 하는 통합 구현
- 실제 브라우저/runtime E2E를 장시간 반복해야 하는 작업
- 대량 통합 회귀를 지속 실행하고 여러 실패를 연쇄 수정해야 하는 작업
- Chat/연결도구/일반 실행으로 안정적으로 마칠 수 없다는 구체적 blocker가 확인된 작업

### G5 — Work 이관 패키지가 완성됐는가
Work에 넘기기 전에 반드시 준비:
- exact source files
- known-good baseline
- failing fixture
- expected output
- error signature
- exact PASS criteria
- 이미 시도한 Chat/terminal 조치
- Work에서 하지 말아야 할 재분석 범위

G1~G3 중 하나라도 YES이면 `WORK_DEFER_DENIED`.
G4와 G5가 모두 YES일 때만 `WORK_ELIGIBLE`.

## 4. 시간·크레딧 낭비 검증
각 Work 후보마다 다음을 기록한다.

| 필드 | 값 |
|---|---|
| 작업 |  |
| Chat 처리 가능 여부 | YES/NO + 근거 |
| GitHub 처리 가능 여부 | YES/NO + 근거 |
| 일반 실행 처리 가능 여부 | YES/NO + 근거 |
| Work만 필요한 핵심 |  |
| 재분석 금지 범위 |  |
| 예상 크레딧 낭비 위험 | LOW/MEDIUM/HIGH |
| 판정 | WORK_DEFER_DENIED / WORK_ELIGIBLE / HOLD |

원칙: Work에서 과거 1년 대화를 다시 읽거나 규칙을 다시 정리하게 하는 것은 `CREDIT_WASTE_FAIL`로 판정한다.

## 5. 도구별 과거 피드백 흡수 상태 — 초기 인덱스

### TOOL001 — 고객 자동화 안내서
현재 발견된 핵심 과거 증거:
- `안내서_전체_연결버전.html`: 실제 안내서 슬롯 매핑 후보.
- `1번도구_정상미리보기_좌중우_5안내서_v14.html`: 좌/중/우 구조와 진단 흔적은 있으나 synthetic title/page/price/link 생성이 있어 생산 경로로 직접 사용 금지.
- `RUN23_1번고객자동화안내서_로컬완성후보.html` 및 RUN 계열: shell-risk, 실제 카드 수, 오른쪽 실데이터 여부, P5 PASS 선행 여부를 검사하는 진단 코드 존재.
- `34번 통합+자동화.txt`: 실제 HTML + 입력반영 + 가운데 데이터 + 오른쪽 안내서 + 점검표 + 실제 로그 동시 확인 전 PASS 금지; META/JSON/패치 존재만으로 PASS 금지.
- `1번 고객 자동화 안내서 10(6).doc`: 고객정보 -> 자료 5개 -> 메일 5개 -> 스팸회피 -> 발송 직전 완성형 구조.
- 고객 최근 활동 기반 전화 멘트/질문, 일반 영업 멘트 금지, 통화 결과를 다시 안내서에 반영하는 선순환 규칙 존재.

초기 변환 작업:
- synthetic generation signature -> `TOOL001_SYNTHETIC_REPORT_DATA` error class.
- shell-only PASS -> `TOOL001_SHELL_PASS_WITHOUT_REAL_OUTPUT` error class.
- 실제 공개 보고서 입력 -> DOM/안내서 실제 출력 -> 기대값 비교 fixture를 복구/생성해야 함.
- 안정판은 과거 사용자 승인/실제 출력 증거가 가장 강한 후보를 선택하며 새 껍데기 UI로 교체 금지.

현재 판정: HISTORY RECOVERY ACTIVE / PRODUCTION E2E HOLD.

### TOOL006 — TOC
현재 발견된 핵심 과거 증거:
- MarketsandMarkets: 상위 목차 인식 실패, 들여쓰기 무시, 숫자 계층 처리, 병합/분할 라인 문제가 반복 기록됨.
- MarketsandMarkets 실제 metadata column 변형: `Table of Contents`, `Table of Contents 2`, `List Of Tables`, `List Of Tables 2/3/...`, `List Of Figures` 등 복수 구조 존재.
- 과거 강제 학습 대상에 MarketsandMarkets, Allied, Acumen, GlobalData, Technavio가 기록됐고 발행사별 오류 유형이 분리돼 있음.
- 숫자만 떨어지는 라인 제거, 번호+제목 보존, PASS/X 이력 저장 등 구현 흔적 존재.
- 변경 전 snapshot -> 수정 후 핵심 기능 재검사 -> 실패 시 자동 복원의 자가 안정화 규칙이 과거 자료에 존재.

초기 변환 작업:
- 사용자 승인 원본 TOC -> 최종 TOC 쌍을 발행사별 golden fixture로 회수.
- MarketsandMarkets부터 `upper-level / indent / merged-line / numeric-only / list-of-* / toc2` 회귀 fixture 분리.
- Chat one-off TOC도 동일 fixture를 참조하며 자유추론만으로 출력 금지.
- Tool6 batch engine과 Chat one-off 경로가 동일 publisher fixture를 공유해야 함.

현재 판정: HISTORY RECOVERY ACTIVE / GOLDEN FIXTURE SET INCOMPLETE.

### TOOL013 — Excel 자동 업로드
- 37번과 완전 분리.
- known regression: Publishing Date serial `46145`.
- Work 이관 전에 Chat/GitHub/일반 실행에서 날짜 변환 로직과 결정형 fixture를 먼저 복구·수정·검증한다.
현재 판정: REGRESSION KNOWN / FIX NOT YET VERIFIED.

### TOOL037 — 메타데이터
- 13번과 완전 분리.
- 한글 상품명/영문 원문명, ISBN/CODE, 행 무결성, 발행사별 구조 차이를 과거 원본/완성본에서 fixture화해야 함.
현재 판정: RULE RECOVERY ACTIVE / NEW INPUT E2E HOLD.

## 6. 전 도구 공통 적용
각 도구에 무조건 같은 비즈니스 규칙을 복제하지 않는다. 공통으로 재사용 가능한 것은 아래뿐이다.
- 실제 입력 -> 실제 실행 -> 실제 출력 -> 기대값 비교
- 안정판 보존
- 동일 오류 error_hash/fixture 승격
- 사용자 반복테스트 금지
- 변경 전 snapshot / 변경 후 핵심 회귀 / 실패 시 rollback
- shell/status/META만으로 PASS 금지

발행사별/도구별 의미가 다른 규칙은 해당 도구 구현과 fixture에만 둔다.

## 7. 고객응대 루틴과 도구 학습 연결
실제 고객 업무에서 생기는 데이터는 다음처럼 도구 개선 자산으로 전환한다.

| 실무 사건 | 자동 축적 대상 |
|---|---|
| 신규 고객 공식 검증 | email/customer verification fixture |
| 소개서/명함 발송 상태 | send-state regression |
| 7번 고객 컨택 판단 | PASS/HOLD/FAIL expected-output fixture |
| 실제 전화 결과 | branch fixture |
| 정식 안내서 | Tool1 real-output fixture |
| 중간 안내서 | Tool1 intermediate-guide fixture |
| 실제 TOC | Tool6 publisher source fixture |
| 사용자 승인 TOC | Tool6 golden expected output |
| 고객 답신 | response-branch fixture |
| 같은 오류 재발 | existing error_hash regression FAIL |

## 8. 진행/재시작 원칙
- 한 회차마다 새로 처리한 과거 증거만 기록한다.
- 이미 처리한 파일/규칙은 source/commit/blocker 변화가 없으면 `SKIP — unchanged evidence`.
- 각 도구별 `last_processed_evidence`와 `next_unprocessed_evidence`를 상태판 또는 이 장부에 남긴다.
- HOLD가 생겨도 다른 처리 가능한 도구로 즉시 이동한다.
- 사용자의 새 지시는 피드백으로 분류하여 위 폐루프에 투입하되, 기존 목표와 충돌하는지 먼저 검사한다.

## 9. 완료 정의
이 데이터 작업은 "규칙 문서를 많이 만들었다"로 완료하지 않는다.
도구별로 다음이 쌓여야 완료도가 올라간다.
1. 과거 근거 인덱스
2. 검증된 규칙
3. 실제 입력 fixture
4. 기대출력 golden fixture
5. error_hash/known regression
6. 실제 구현 patch
7. 실행 검증 결과
8. 재사용 연결

전체 과거자료 전수 흡수는 현재 진행 중이며, 확인하지 않은 자료까지 완료라고 표시하지 않는다.
