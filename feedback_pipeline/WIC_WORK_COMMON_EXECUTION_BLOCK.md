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

## USB 기존자료 교차검증 + 정상자료 GitHub 승격 — REQUIRED
- TOOL044가 READY_COMPONENT를 대상 TOOL/대화창에 장착할 때뿐 아니라, 모든 WIC TOOL Work에서 현재 대상과 직접 관련된 USB/실사용폴더 기존 자료가 있으면 실제 검증 입력·비교 근거로 함께 사용한다.
- USB 전체 전수검색은 금지한다. 현재 TOOL 번호·기능·오류·파일명·MASTER/checkpoint와 직접 관련된 자료만 좁게 확인한다.
- USB에는 정상본·중간개발본·껍데기·샘플·실패본·중복본이 섞여 있을 수 있으므로 파일 존재 자체를 신뢰하지 않는다.
- USB 자료는 `현재 MASTER/독립 EXPECTED 대조 → 실제 실행/관련 기능 시험 → EXPECTED↔ACTUAL → 직접 영향 회귀`를 통과해야 정상자료로 판정한다.
- 파일 존재, 이름 유사, 최신 날짜, 큰 용량, 화면 열림, 코드 문자열 존재만으로 PASS하지 않는다.
- 껍데기/샘플/기능 미연결/실행실패/기대동작 불일치/출처불명/중복 열화본은 `SHELL_OR_INVALID`로 차단하고 canonical MASTER/registry에 승격하지 않는다.
- 정상 검증된 자료만 해당 TOOL/대화창의 GitHub 정본에 필요한 최소 범위로 옮기고 MASTER/checkpoint/registry에 출처·검증근거·버전/해시·적용범위를 남긴다.
- USB 원본은 GitHub commit/push + remote read-back PASS 전 삭제·덮어쓰기하지 않는다.
- 외부 READY_COMPONENT와 USB 기존자료가 같은 기능을 제공하면 기존 WIC VERIFIED/PASS 자료를 우선 재사용하고, 껍데기이거나 불충분할 때만 TOOL044 외부부품을 사용한다.
- 권장 실행순서: `기존 WIC VERIFIED_COMPONENT 확인 → 필요시 TOOL044 READY_COMPONENT sandbox PASS → 관련 USB 기존자료/실제입력 교차검증 → 대상 TOOL 통합시험 → GitHub 정본/MASTER 승격 → 실사용폴더 배포 → 배포본 재시험 → DEPLOYED_PASS → SAFE_CHECKPOINT`.
- USB 정리 자체를 목적으로 전체 폴더 청소를 벌이지 않고 실제 TOOL 작업 중 증분적으로 검증·승격한다.
USB_RELATED_DATA_NARROW_SCAN_ONLY = REQUIRED
USB_WHOLE_SCAN = FORBIDDEN
USB_FILE_EXISTS_IS_NOT_TRUST = TRUE
USB_SHELL_OR_INVALID_BLOCK = REQUIRED
USB_NORMAL_DATA_REQUIRES_ACTUAL_TEST = TRUE
USB_VERIFIED_ASSET_GITHUB_PROMOTION = REQUIRED
USB_PROMOTION_REQUIRES_REMOTE_READBACK = TRUE
TOOL044_USB_CROSS_VALIDATION = REQUIRED_WHEN_RELEVANT

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

## 모든 WIC 도구·프로그램의 지속비용 0 우선 게이트 — REQUIRED
- 이 규칙은 TOOL044만이 아니라 기존 모든 WIC TOOL, 앞으로 추가되는 모든 TOOL·프로그램·대화창 기반 실행체계, 그리고 모든 개발·확장·통합에 공통 적용한다.
- Work에 신규 개발·기능추가·확장 작업이 들어오면 구현 전에 먼저 `지속비용 없이 구현 가능한가`를 판정한다.
- 기본 우선순위는 `기존 WIC 검증부품 재사용 → TOOL044에서 외부의 완성·공유·실사용·검증된 무료 부품 탐색 → 로컬/무료 실행 방식 → 그래도 불가능할 때만 별도 개발 검토`다.
- 완성된 도구의 정상적인 일상 운영이 Work/Codex 크레딧, 유료 AI 호출, 유료 API, 유료 SaaS, 사용량 기반 과금에 지속 의존하는 구조는 기본 FAIL이다.
- 개발·수리·최초 검증 단계에서 제한적으로 Work를 사용할 수 있으나, 배포된 도구의 정상 런타임이 Work/Codex 크레딧을 계속 소모하도록 설계하지 않는다.
- 규칙엔진, 캐시, 기존 결과 재사용, 로컬 실행, 무료 오픈소스/공개 패키지로 해결 가능한 기능에 유료 AI를 붙이지 않는다.
- 생성형 AI 판단이 정말 필요한 일부 기능은 본체와 분리하고, 규칙화 가능 여부 → 기존 결과/캐시 재사용 → 무료/로컬 대안 검토를 먼저 통과한 뒤 마지막 수단으로만 유료 AI 사용 여부를 별도 판단한다.
- 신규 도구나 신규 기능의 설계 질문은 `어떻게 새로 만들까?`보다 먼저 `돈과 크래딧 없이 기존 검증부품 또는 TOOL044 완성부품으로 해결 가능한가?`를 묻는다.
- TOOL044는 WIC 고유 규칙을 새로 만드는 도구가 아니라, 그 규칙이 반드시 실행되게 하는 검증된 바깥 구조를 가져오는 역할로 사용한다.
- TOOL044 후보는 외부 부품 자체의 수정·개량·커스터마이즈·추가개발이 필요하면 채택하지 않고 `NO_READY_COMPONENT`로 종료한다.
RUNTIME_CREDIT_ZERO = DEFAULT_REQUIRED
RECURRING_PAID_API = REJECT_BY_DEFAULT
PAID_SAAS_DEPENDENCY = REJECT_BY_DEFAULT
PAID_AI_REQUIRED_FOR_NORMAL_OPERATION = FAIL
LOCAL_RULE_ENGINE_FIRST = REQUIRED
CACHE_AND_REUSE_FIRST = REQUIRED
VERIFIED_WIC_COMPONENT_FIRST = REQUIRED
TOOL044_READY_COMPONENT_SEARCH_BEFORE_NEW_COMMON_BUILD = REQUIRED
ZERO_RECURRING_COST_TARGET = TRUE
PAID_AI = LAST_RESORT_ONLY

## 기존 도구·이전 정상판 대조 + 실제 버튼 조작 검증 게이트 — REQUIRED
- 도구의 사소한 기능, 버튼, 입력칸, 선택창, 복사, 초기화, 다운로드, 저장, 미리보기, 오류표시처럼 작은 변경도 `코드가 있어 보인다` 또는 `버튼이 존재한다`는 이유만으로 PASS 처리하지 않는다.
- 현재 도구를 테스트할 때 이전에 실제로 사용되었거나 검증된 정상판/배포본/과거 실행파일이 있으면 우선 그것과 화면·버튼·동작을 나란히 대조한다. 단, 관련 없는 과거 전체 버전을 전수검사하지 않고 현재 변경 기능과 직접 관련된 이전 정상판만 좁게 사용한다.
- 대표 대조항목은 `버튼 수·이름·위치·활성/비활성 상태·클릭 후 동작·입력값 반영·화면 전환·미리보기·복사·초기화·다운로드/저장·오류표시·최종 산출물`이다.
- 버튼이나 조작형 기능은 실제로 눌러야 한다. DOM/handler 존재, 코드 문자열 존재, 버튼 개수 일치만으로 기능 PASS를 선언하지 않는다.
- 현재판 버튼을 실제 클릭하여 ACTUAL을 캡처하고, 이전 정상판에서 동일 기능을 실제 조작해 얻은 기준 동작 또는 MASTER/사용자 확정 EXPECTED와 서로 대조한다.
- 이전판과 현재판이 의도적으로 달라진 경우에는 무조건 이전판으로 되돌리지 않고 `CHANGED_INTENTIONALLY` 근거를 남긴다. 근거 없이 사라졌거나 끊긴 기능은 `MISSING_UI / MISSING_FUNCTION / BROKEN_CONNECTION`으로 분류한다.
- 사소한 변경도 `대표 실제 입력 → 실제 버튼/조작 → EXPECTED → ACTUAL → 이전 정상판/MASTER 대조 → 영향 회귀 → PASS`를 통과해야 한다.
- 자동화 가능한 클릭·입력·다운로드·재열기 검증은 Work가 직접 수행하고, 사용자에게 버튼 테스트를 떠넘기지 않는다. 플랫폼상 사용자 승인/MFA/물리기기 조작이 꼭 필요한 경우만 USER_ACTION_REQUIRED로 묶는다.
- 이전 정상판이 없거나 확보할 수 없으면 MASTER/사용자 확정 동작을 독립 EXPECTED로 사용하고, 없다는 이유로 테스트 자체를 생략하지 않는다.
PRIOR_VERIFIED_TOOL_COMPARISON = REQUIRED_WHEN_AVAILABLE
ACTUAL_BUTTON_CLICK_TEST = REQUIRED_FOR_INTERACTIVE_FUNCTION
BUTTON_EXISTS_IS_NOT_PASS = TRUE
HANDLER_EXISTS_IS_NOT_PASS = TRUE
SMALL_FEATURE_TEST_SKIP = FORBIDDEN
PRIOR_VERSION_WHOLE_AUDIT = FORBIDDEN
INTENTIONAL_CHANGE_REQUIRES_EVIDENCE = TRUE
USER_MANUAL_BUTTON_TEST_BY_DEFAULT = FORBIDDEN

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
- 실제 코드·수정 SHA·회귀검증·실사용 증거가 존재하는 기존 PASS/VERIFIED 범위는 보존하고 SKIP_REUSE한다.
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
