# WIC WORK COMMON EXECUTION BLOCK

상태: ACTIVE / REQUIRED
목적: 현재 작업 중인 TOOL에서 반복되는 공통 실행을 매번 새로 조사·설계·질문하지 않고 재사용하여 크레딧과 사용자 작업을 줄인다.

## 최상위 원칙
- 이 블록은 모든 Work TOOL 작업 지시문에 기본 포함된 것으로 취급한다.
- 사용자가 폴더 경로, 배포 위치, GitHub 정본 위치, checkpoint 위치를 매번 다시 알려주게 하지 않는다.
- 현재 작업 중인 TOOL 하나만 대상으로 기존 canonical pointer / repo / checkpoint / 배포 경로 / 로컬 운영 경로를 좁게 회수한다.
- WIC 전체 전수조사, 전체 USB 조사, 전도구 재검증은 금지한다.
- 이미 PASS / VERIFIED / REMOTE_VERIFIED된 공통 절차·부품은 SKIP_REUSE한다.
- 같은 공통 작업을 TOOL마다 새로 개발·재설계·재검증하지 않는다.

## `업데이트` 중앙 반영 명령
- WIC 관련 대화창에서 사용자가 단독 또는 문맥상 저장 의도로 `업데이트`라고 입력하면, 직전까지 나온 신규 영구 피드백을 CENTRAL/해당 TOOL canonical master에 실제 반영하는 명령으로 해석한다.
- 현재 대화에 일회성 질문과 영구규칙이 섞여 있으면 영구규칙만 분리한다.
- 반영 순서: MASTER_LOAD → 신규 피드백 추출 → 기존 규칙과 중복/충돌 대조 → DIFF ONLY → GitHub write/commit → remote read-back → 증거 보고.
- GitHub write/commit/read-back이 실제로 완료되지 않으면 `업데이트 완료`라고 말하지 않고 `미반영/HOLD`로 보고한다.
- `업데이트`라는 단어 자체만으로 반영 성공을 보장하지 않는다. 실제 commit과 remote read-back이 PASS한 경우에만 중앙 반영 확정으로 판정한다.
- `업데이트`는 USB 전체조사나 전수감사를 뜻하지 않는다. 현재 작업 범위와 새로 드러난 피드백만 증분 처리한다.
CENTRAL_FLUSH_COMMAND = 업데이트
CENTRAL_FLUSH_REQUIRES_REMOTE_EVIDENCE = TRUE
UPDATE_WORD_ALONE_IS_NOT_PROOF = TRUE

## 대화창 길이 감시 및 자동 인계
- WIC 대화가 길어져 문맥 누락·응답 저하·반복 가능성이 커지기 전에 시스템이 먼저 `CHAT_HANDOFF_REQUIRED`를 사용자에게 알린다.
- 사용자가 먼저 "길어진 것 같다"고 지적할 때까지 기다리는 것은 FAIL이다.
- 인계 전 현재 대화의 신규 영구 피드백을 `업데이트` 절차로 반영하고 SAFE_CHECKPOINT / 현재 상태 / 미완료 / HOLD / 최근 실제 검증 / NEXT_WORK / NEXT_START를 남긴다.
- 새 대화에서는 사용자가 과거 내용을 다시 설명하지 않도록 MASTER + latest checkpoint를 먼저 불러온다.
- 이미 중앙 반영된 내용은 새 대화에서 다시 적재하지 않고 SKIP_REUSE한다.
CHAT_HANDOFF_EARLY_WARNING = REQUIRED
USER_DETECTS_CONTEXT_DEGRADATION_FIRST = FAIL
HANDOFF_REEXPLANATION_BY_USER = FORBIDDEN

## 보고 형식
- 진행·상태 보고는 사용자가 쉽게 읽을 수 있는 한국어 표를 기본으로 한다.
- 최소 열: `처리한 대화창 번호 | 처리 대상 | 현재 상태 | 아주 쉽게 설명 | 남은 시간`.
- 가능한 경우 각 항목 남은 시간과 전체 남은 시간을 함께 표시한다.
- 전문용어만 나열하지 말고 즉시 쉬운 뜻을 붙인다.
- 완료/PASS 주장에는 실제 실행·commit/read-back 등 확인 가능한 근거가 있어야 한다.
SIMPLE_TABLE_PROGRESS_REPORT = REQUIRED
PROCESSED_CHAT_OR_TOOL_NUMBER = REQUIRED
REMAINING_TIME_REPORT = REQUIRED_WHEN_MEANINGFUL

## 크레딧/Work·Codex 사용량 보호
- 전수조사, 이미 PASS된 범위 재검증, 동일 조건 동일 실패 반복, 결과 변화 없는 상태확인 예약 반복은 금지한다.
- 반대로 실제 미완료 TOOL의 정상 개발·최초 검증·정본 반영은 크레딧 절약을 이유로 과도하게 미루지 않는다.
- 상태/checkpoint만 반복 확인하고 실제 변화가 없는 예약 작업은 불필요 소진 후보로 분류하고 비활성/정리 대상으로 올린다. 플랫폼상 자동 삭제 권한이 없으면 사용자에게 최소 행동만 요청한다.
WASTE_BLOCKING_STRICT = TRUE
PRODUCTIVE_WORK_CREDIT_THROTTLE_RELAXED = TRUE
NOOP_SCHEDULED_REPEAT = FORBIDDEN

## 현재 Work와 역사자료 분리
- 사용자가 별도로 재개하라고 명시하기 전까지 현재 Work는 278개 과거대화 catch-up과 절대 연결하지 않는다.
- 현재 TOOL 작업 중 278 catch-up을 조회·흡수·재개·교차검색하지 않는다.
- 일반 USB 운영자료 규칙과 별개로, 278 catch-up은 명시적 재개 전 독립 HOLD다.
278_CATCHUP_LINK = FORBIDDEN_UNTIL_EXPLICIT_RESUME

## 전 대화창 피드백 자동화 전수감사 — 보류 + 기존 결과 재사용
- 사용자가 2026-08-31에 요청한 `전 대화창/전 도구 피드백 자동수집 → 중앙마스터 자동반영 → 다음 작업 자동호출 → 사전 강제게이트 → E2E 검증` 전체 감사는 더 진행하지 않고 보류한다.
- 사용자가 명시적으로 재개하기 전에는 이 감사를 위한 추가 전수검색·원격조회·수정·재검증을 하지 않는다.
- 단, 중단 전에 이미 확보된 결과는 폐기하지 않고 향후 개별 TOOL 작업의 `재사용 가능한 고장 지도 / PASS 판정 강화 기준`으로만 사용한다.
- 감사 결과의 `완전 자동 연속 E2E 0%`는 WIC 코드 구현률 0% 또는 기존 TOOL 전체 실패를 뜻하지 않는다. 일반 Chat 입력부터 GitHub 반영·다음 실제 출력 강제까지 이어지는 완전 자동 E2E가 확인되지 않았다는 제한된 의미로만 해석한다.
- 실제 코드·수정 SHA·회귀검증·실사용 증거가 존재하는 기존 PASS/VERIFIED 범위는 보존하고 SKIP_REUSE한다. 특히 TOOL041/042 본체 실제 수정·회귀 증거와 TOOL043 스마트폰 실사용 증거를 전 Chat 자동화 미입증과 섞어 무효화하지 않는다.
- 앞으로 `규칙 저장`, `fixture/internal test`, `파일 존재/hash validator`, `실제 본체 수정`, `실사용 검증`, `일반 Chat→최종 출력 연속 E2E`를 서로 다른 증거 등급으로 구분한다. 검사 함수가 존재한다는 사실만으로 실제 업무 출력에 강제 적용됐다고 PASS 처리하지 않는다.
- 일반 Chat 메시지를 자동 수집하는 진입 경로와 WIC 내부에 이벤트가 입력된 뒤 처리하는 경로를 분리 판정한다. 후단 코드가 존재한다는 이유만으로 일반 Chat 자동 연결 완료로 확대 판정하지 않는다.
- 이미 드러난 공통 고장 후보(registry 상태 계약 불일치, 실제 master 대신 상태/포인터 경로, 출력 자체를 검사하지 않는 validator, workflow/실행기 반환 계약 불일치)는 향후 해당 범위를 실제로 작업할 때만 좁게 재사용·확인한다. 이 목록만을 이유로 별도 전수감사를 재개하지 않는다.
- 도구별 감사표의 `일부 자동 / 규칙만 / NOT_VERIFIED` 분류는 다음 해당 TOOL 작업의 출발점 후보로만 사용하며, 미확인 항목을 미구현으로 단정하지 않는다.
- 278개 과거대화 catch-up과는 연결하지 않는다.
DEFERRED_CROSS_CHAT_AUTOMATION_AUDIT = HOLD_USER_RESUME
RESUME_TRIGGER = USER_EXPLICITLY_REQUESTS_CROSS_CHAT_AUTOMATION_AUDIT
AUDIT_EXISTING_FINDINGS_REUSE = SCOPED_ONLY
AUDIT_FINDINGS_DO_NOT_INVALIDATE_VERIFIED_TOOL_WORK = TRUE
FULL_AUTOMATION_E2E_ZERO_IS_NOT_CODE_IMPLEMENTATION_ZERO = TRUE

## TOOL043 현재 합의 범위 완료 증거
- TOOL043 모바일 관찰자 페이지 실제 스마트폰 접근 PASS.
- 화면 OFF 중 새 GitHub Actions 실행 및 저장 PASS: run `33358129860`.
- 화면 ON/재열기 후 스마트폰 상세 상태에서 동일 run `33358129860` 표시를 사용자 실제 확인 PASS.
- 상태 영구저장 PASS.
- SAFE CHECKPOINT 실제 SHA 표시 PASS.
- 현재 합의한 TOOL043 개선 범위는 COMPLETE / REMOTE_VERIFIED로 취급하고 동일 범위를 반복 테스트하지 않는다.
- TOOL043 화면의 `미처리 작업`은 다른 TOOL/HOLD/OPEN 대기 항목이며 TOOL043 자체 고장을 의미하지 않는다.
- `현재 장부`는 WIC 내부 작업 상태표를 뜻하며 고객 매일장부가 아니다. 진행 중 없음과 미처리 대기는 서로 다른 상태다.
- TOOL012/common CI 등 후속 항목은 TOOL043 완료와 분리하여 처리한다.
TOOL043_CURRENT_SCOPE_COMPLETE = TRUE
TOOL043_CURRENT_SCOPE_RETEST = FORBIDDEN

## 공통 실행 순서
1. CURRENT_TOOL_SCOPE_LOCK
   - 현재 지정 TOOL만 연다.
   - 다른 TOOL은 현재 TOOL이 실제 BLOCKED/HOLD로 확정된 경우에만 이동한다.

2. CANONICAL_POINTER_RESOLVE
   - CENTRAL registry → 기존 GitHub repo → latest checkpoint → 현재 TOOL 관련 handoff 순서로 좁게 확인한다.
   - 기존 정본이 있으면 그대로 재사용한다.
   - 새 repo, 새 복제품, 임의 새 폴더 생성 금지.

3. PATH_AUTO_RESOLVE
   - 폴더 경로·배포 경로·정본 경로·실행 경로를 사용자에게 매번 질문하지 않는다.
   - 기존에 검증된 경로 규칙과 해당 TOOL의 기존 경로를 자동 재사용한다.
   - 경로가 충돌하거나 실제 근거가 없을 때만 HOLD_PATH_UNRESOLVED로 남긴다.

4. SCOPED_SOURCE_CANONICALIZATION
   - 현재 작업 TOOL/업무와 직접 관련해 실제 만난 자료만 scoped 확인한다. 전체 전수조사는 금지한다.
   - 과거 자료를 통째로 신뢰·복사하지 않는다.
   - 검증된 정상 DIFF만 기존 해당 TOOL GitHub canonical repo 또는 CENTRAL master에 반영한다.
   - HOLD_UNKNOWN / SHELL_OR_STALE / DUPLICATE / OBSOLETE / 미검증 자료는 canonical에 흡수하지 않는다.
   - commit + REMOTE_HEAD + remote read-back + 변경범위 FIRST_VALIDATION 근거가 확인된 자산만 canonical 반영 완료로 판정한다.

5. COMMON_DEPLOY
   - 기존 PASS된 배포 구조가 있으면 재사용한다.
   - 이 게이트는 실제 파일·코드·규칙·연결 수정이 발생한 현재 대상 TOOL에만 적용한다. 작업하지 않은 다른 TOOL을 조사·테스트·개발하지 않으며 영향받지 않은 기존 PASS/VERIFIED는 `SKIP_REUSE`한다.
   - 강제 순서: 수정 → 영향받은 기존 기능 회귀검사 → 실제 업무 입력 E2E → 최종 출력 정상 검증 → 오류 수정 → 동일 실패 입력 재테스트 → PASS 후 GitHub 반영/remote read-back → 기존 로컬 실행폴더 배포 → canonical 실행파일 정확히 1개 지정 → 배포된 canonical 파일 자체 재테스트 → GitHub본↔로컬 hash/content 대조 → 실행 증거 저장.
   - release gate 필수 개별 증거: `test_executed / test_input_recorded / expected_defined / actual_captured / expected_actual_match / regression_passed / pass_evidence_recorded`. 어느 하나라도 false/누락이면 `DEPLOY_BLOCKED`; commit/push 또는 로컬 복사를 실행하지 않는다.
   - 파일·버튼·handler 존재, 종료코드 0, 행 수만 일치, 파일 생성·다운로드, commit/hash, 자체 PASS 표시는 EXPECTED-vs-ACTUAL 기능 검증을 대신하지 않는다.
   - 변경 기능과 직접 영향범위만 테스트하고 무관한 기존 PASS는 `SKIP_REUSE`; 공통엔진·대량처리 엔진 변경 또는 기존 PASS와 충돌하는 실제 증거가 있을 때만 전체 실제 입력 검증을 확대한다.
   - GitHub/read-back 뒤 로컬 배포·배포본 재테스트가 누락되면 `DEPLOY_INCOMPLETE`로 유지하고 사용자 재지시 없이 `DEPLOY_LOCAL_CANONICAL_AND_RETEST`로 자동 계속한다. 권한·로그인·MFA로 Work가 실행할 수 없을 때만 `USER_ACTION_REQUIRED`와 정확한 차단 원인을 남긴다.
   - `CODE_PASS / SMOKE_PASS / E2E_PASS / DEPLOYED / DEPLOYED_E2E_PASS / REAL_USE_PASS`를 분리한다.
   - `행 0 / UNKNOWN / 빈 출력 / 중간 정지 / 오류 은폐 / 버튼 무반응 / 미리보기 미생성 / 다운로드 실패 / 입력 일부 누락 / 데이터 혼합 / 예상 결과 불일치`는 release 차단 조건이다.
   - 실패 입력을 다른 쉬운 fixture로 바꾸지 않고 동일 실제 입력으로 재시험한다.
   - 위 단계 중 하나라도 빠지면 `DEPLOY_INCOMPLETE`이며 COMPLETE/PASS로 승격하지 않는다.
   - 권한/플랫폼상 불가능할 때만 BLOCKED_EXTERNAL + 정확한 RESUME_TRIGGER를 남긴다.

6. COMMON_GITHUB_CANONICALIZE
   - 변경 후 commit → REMOTE_HEAD → remote read-back을 공통 절차로 수행한다.

7. FIRST_VALIDATION_ONCE
   - 새로 변경된 범위만 최초 검증 1회 수행한다.
   - 동일 조건·동일 코드의 PASS 범위 재검증 금지.
   - 같은 실패를 같은 방법으로 반복 패치·재실행 금지.

8. CENTRAL_REGISTER
   - canonical pointer / 상태 / commit / blob / validation evidence / HOLD·BLOCKED / RESUME_TRIGGER를 기존 CENTRAL registry에 갱신한다.

9. COMMON_CLOSE
   - COMPLETE / REMOTE_VERIFIED 또는 HOLD / BLOCKED_EXTERNAL / BLOCKED_CANONICAL_NOT_FOUND 중 실제 증거로 닫는다.
   - COMPLETE된 기존 범위는 SKIP_REUSE.
   - SAFE_CHECKPOINT / NEXT_START / 증거를 남긴다.

## 반복 공통작업 승격 규칙
- 현재 실제 TOOL 작업 중 동일 작업이 반복되면 별도 전수조사 없이 REUSE_CANDIDATE로 기록한다.
- 실제 PASS된 뒤 공통 실행부로 승격한다.
- 첫 등장: 현재 TOOL에서 최소 구현.
- 두 번째 반복: 공통화 후보.
- 세 번째 이상 반복: 검증된 공통 실행부 우선 재사용.
- 공통화를 위해 별도 대형 프로젝트나 WIC 전체 재설계를 시작하지 않는다.

## 금지
FULL_AUDIT = FORBIDDEN
FULL_USB_AUDIT = FORBIDDEN
REBUILD_VERIFIED_COMPONENT = FORBIDDEN
RETEST_UNCHANGED_VERIFIED_COMPONENT = FORBIDDEN
NEW_REPO_FOR_REUSE = FORBIDDEN
DUPLICATE_VERIFIED_STORAGE = FORBIDDEN
USER_REPEATED_PATH_INPUT = FORBIDDEN
USER_REPEATED_DEPLOY_INSTRUCTION = FORBIDDEN
SAFE_WORK_EXHAUSTED_BECAUSE_COMMON_PATH_NOT_REUSED = FORBIDDEN

## 사용자 역할
USER_ROLE = OBSERVER_ONLY
사용자는 경로·배포법·checkpoint·정본 위치를 매 작업마다 다시 설명하지 않는다.
플랫폼상 본인 승인/MFA/권한 변경이 필수인 경우에만 최소 1회 행동을 요청한다.

## 영구 Work 반복·임의확장 차단 — REQUIRED

WORK_ADMISSION_POLICY = PERMANENT_FAIL_CLOSED_V1
- 새 Work는 기존 work_gate_handoff.py --resume-latest로 최신 CENTRAL 공통 블록·실행 코드·작업 영수증을 같은 revision에서 로드한다. 과거 대화 메모리는 근거로 쓰지 않는다.
- 실제 후보를 --candidate로 전달하면 로드 직후 기존 evaluate_candidate → preflight_attempt가 자동 실행된다. 후보 없는 로드는 실행허가가 아니다.
- PASS/VERIFIED/REMOTE_VERIFIED 작업은 SKIP_REUSE. 해제조건의 실제 변경 증거가 없는 HOLD와 같은 원인·방법의 실패는 SKIP_NO_VALUE로 종료한다.
- 수정 순서: 기존 자산 재사용 → 끊어진 연결 복구 → 최소 수정. 연결/오류/잔여 수정 요청은 새 TOOL/MVP/UI/DB/파이프라인 생성 승인이 아니다.
- 새 구조물은 명시적 승인과 기존 구조 해결불가 증거를 먼저 확인한다. 범위 밖 문제는 기존 OPEN/HOLD에 기록하고 실행하지 않는다.
- 작업 종료 시 기존 장부에 operation_id·증거·PASS/HOLD/FAIL·실패 방법·해제조건·NEXT_WORK를 저장한다. 완료 작업의 이름을 바꿔 재실행하지 않는다.
- 공통 블록 누락, 로컬 실행기와 최신 정본 불일치, 최신 상태 로드 실패는 HOLD. 사용자에게 규칙·checkpoint를 다시 전달시키지 않는다.
- 강제 범위는 이 공통 진입경로를 사용하는 Work다. 플랫폼의 임의 대화/직접 도구 호출 전체를 가로챈다는 의미가 아니다.

## MASTER 강제 START GATE 대표 유형
- 대표 대상은 `TOOL041`(고객정보 수집·정리형), `TOOL042`(고객별 자료 추천·안내 출력형), `TOOL007`(멘트·문구 작성형)이다.
- TOOL041·042의 기존 PASS/registry 연결은 SKIP_REUSE하며 대표대상 기록을 이유로 업무를 재실행하지 않는다.
- TOOL007은 registry 순서대로 `CENTRAL_COMMON_MASTER → customer_pipeline/tool7_contact_judgment.py → WIC_GLOBAL_OPERATING_RULES.md → customer_pipeline/CONTACT_COPY_CHECKPOINT.md`를 모두 실제 로드해야 작업 진입을 허용한다.
- 어느 파일이든 누락·빈 파일·순서 불일치면 `MASTER_LOAD_FAIL` 또는 `MASTER_LOAD_ORDER_INVALID`로 본문 생성을 차단한다.
- TOOL007 과거 근거 검색은 위 현재 정본이 부족한 경우에만 Antigravity TOOL007 범위, 그다음 278 TOOL007 범위로 좁게 내려간다.
START_GATE_REPRESENTATIVE_TARGETS = TOOL041,TOOL042,TOOL007
TOOL007_MASTER_CHAIN_REQUIRED = TRUE
