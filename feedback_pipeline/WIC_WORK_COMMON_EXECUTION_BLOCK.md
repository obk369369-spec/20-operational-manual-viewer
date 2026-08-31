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

## 전 대화창 피드백 자동화 전수감사 — 보류
- 사용자가 2026-08-31에 요청한 `전 대화창/전 도구 피드백 자동수집 → 중앙마스터 자동반영 → 다음 작업 자동호출 → 사전 강제게이트 → E2E 검증` 전체 감사는 가치 판단 후 지금 즉시 계속하지 않고 보류한다.
- 이 감사의 목적은 과거 완료 주장과 실제 작동 상태의 차이를 찾고, `일반 Chat 자동반영 / MASTER 자동호출 / 라우팅 / pre-check gate / E2E`의 실제 구현 수준을 증거로 판정하는 것이다.
- 사용자가 나중에 명시적으로 재개하라고 할 때만 다시 시작한다.
- 재개 시 이미 확인된 MASTER/checkpoint/PASS 범위를 다시 전수검사하지 않고, 저장소·코드·checkpoint·최근 실행증거로 직접 판정한다.
- 278개 과거대화 catch-up과는 연결하지 않는다.
DEFERRED_CROSS_CHAT_AUTOMATION_AUDIT = HOLD_USER_RESUME
RESUME_TRIGGER = USER_EXPLICITLY_REQUESTS_CROSS_CHAT_AUTOMATION_AUDIT

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
   - 정본 확인 → 기존 배포경로 재사용 → 배포 → 변경범위 FIRST_VALIDATION 1회 → 실행 증거 저장.
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
