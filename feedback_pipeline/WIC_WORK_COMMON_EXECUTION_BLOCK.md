# WIC WORK COMMON EXECUTION BLOCK

상태: ACTIVE / REQUIRED
목적: 현재 작업 중인 TOOL에서 반복되는 공통 실행을 매번 새로 조사·설계·질문하지 않고 재사용하여 크레딧과 사용자 작업을 줄인다.

## 최상위 원칙
- 이 블록은 모든 Work TOOL 작업 지시문에 기본 포함된 것으로 취급한다.
- 사용자가 폴더 경로, 배포 위치, GitHub 정본 위치, checkpoint 위치를 매번 다시 알려주게 하지 않는다.
- 현재 작업 중인 TOOL 하나만 대상으로 기존 canonical pointer / repo / checkpoint / 배포 경로 / 로컬 운영 경로를 좁게 회수한다.
- WIC 전체 전수조사, 전체 USB 조사, 전도구 재검증은 금지한다.
- 이미 PASS / VERIFIED / REMOTE_VERIFIED / DEPLOYED_PASS 증거가 있고 현재 변경의 직접 영향이 없는 공통 절차·부품은 SKIP_REUSE한다. 시스템 재시험도 사용자 재시험 요청도 하지 않는다.
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
- 단, 착수 전에 현재 Work 안에서 짧고 확실하게 COMMON_DEPLOY의 배포본 재시험·DEPLOYED_PASS까지 닫을 수 있어야 한다. 큰 작업, 장시간 개발, 반복 실패, 결과 불확실, 광범위 조사, 여러 Work가 필요할 가능성, 배포 범위 미확정은 현재 제외한다.
- 문제/원인/handler·연결·번역부품 부재 확인이나 다음 Work 예고만으로 끝날 가능성이 높은 작업은 착수하지 않는다. 새 작업을 벌이기보다 현재 짧은 작업의 검증·배포 완주를 우선한다.
- 상태/checkpoint만 반복 확인하고 실제 변화가 없는 예약 작업은 불필요 소진 후보로 분류하고 비활성/정리 대상으로 올린다. 플랫폼상 자동 삭제 권한이 없으면 사용자에게 최소 행동만 요청한다.
WASTE_BLOCKING_STRICT = TRUE
PRODUCTIVE_WORK_CREDIT_THROTTLE_RELAXED = TRUE
NOOP_SCHEDULED_REPEAT = FORBIDDEN
LONG_OR_UNCERTAIN = EXCLUDE_NOW

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
   - TOOL별 기존 피드백, MASTER/checkpoint/GitHub evidence, history index, 이미 추출된 287-history·Antigravity 규칙, 실제 고객 사례를 먼저 재사용한다. 원본 역사 전체를 다시 여는 승인이 아니며 기존 역사자료 분리 규칙을 유지한다.
   - 마지막 확정 수집지점 이후 신규 피드백만 증분 수집한다. TOOL + 기능 + 오류 + 고객 + 파일 + 마지막 checkpoint로 범위를 좁히고 사용자에게 기존 내용을 재설명시키지 않는다.
   - 전체 대화/287개 파일/USB/GitHub/TOOL 재검색과 변경에 무관한 전체 regression·데이터 재시험을 하지 않는다.
   - 과거 자료를 통째로 신뢰·복사하지 않는다.
   - 검증된 정상 DIFF만 기존 해당 TOOL GitHub canonical repo 또는 CENTRAL master에 반영한다.
   - 정본 승격 허용 상태는 실제 증거가 있는 `TEST_PASS / VERIFIED / REMOTE_VERIFIED / DEPLOYED_PASS / SAFE_CHECKPOINT`로 제한한다.
   - `SHELL / DRAFT / TEST_NOT_RUN / FAIL / PARTIAL / BROKEN / LEGACY / TEMP / HOLD_UNKNOWN / SHELL_OR_STALE / DUPLICATE / OBSOLETE` 자료는 canonical에 흡수하지 않는다.
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

10. DEVICE_INDEPENDENT_RESUME
   - USB·노트북·사무실 PC·기타 한 실행기기는 입력 또는 실사용 배포 위치일 뿐 유일한 상태 저장소가 아니다. 기본 재개 기준은 `GitHub/CENTRAL canonical + SAFE_CHECKPOINT + validation evidence`다.
   - 특정 기기 감지 실패 시 `1회 재감지 → 다른 canonical 검증경로 확인 → 마지막 SAFE_CHECKPOINT에서 재개`하고 같은 실패방법을 반복하거나 사용자에게 재연결을 반복 요구하지 않는다.
   - 사용자 기기 직접 접근 없이 끝낼 수 있으면 canonical 경로로 처리한다. 직접 접근이 필요해도 대량 삭제·대량 이동·자동 정리·임의 경로 변경·정상본 덮어쓰기·미검증 승격을 금지한다.

11. FLEET_ORCHESTRATION
   - 다중 독립 대상은 `feedback_pipeline/wic_fleet_orchestrator.py`로 조정하고 기존 `wic_mutual_supervision.py`와 TOOL044 fast-deploy 단계는 SKIP_REUSE한다.
   - 대상별 `SKIP_REUSE → CHANGE_ONLY → IMPACT_ONLY → FAIL_ONLY_RETRY → REMOTE_READBACK_REUSE → SAFE_CHECKPOINT_RESUME`를 강제한다.
   - 같은 repo/canonical lock은 직렬화하고 독립 lock만 병렬 실행한다. 한 lane의 실패·영향범위 불명은 해당 lane만 격리하며 정상 lane을 중단하지 않는다.
   - manifest는 증거·상태 입력만 허용하며 임의 명령 실행기로 사용하지 않는다. 영향범위를 안전하게 확정할 수 없으면 `HOLD_IMPACT_UNKNOWN`으로 fail-closed한다.
   - TOOL041/TOOL042는 fleet orchestration의 remote read-back과 deployed-copy 검증 전까지 HOLD한다.

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

## 사용자 역할 — 사용자 번거로움 자동 제거 게이트 — 최우선 REQUIRED
USER_ROLE = OBSERVER_ONLY
사용자는 경로·배포법·checkpoint·정본 위치를 매 작업마다 다시 설명하지 않는다.
플랫폼상 본인 승인/MFA/권한 변경이 필수인 경우에만 최소 1회 행동을 요청한다.
- 사용자에게 무엇이든 요청하기 전에 `CAN_SYSTEM_HANDLE_AUTOMATICALLY`를 판정한다. TRUE이면 현재 권한·작업 범위에서 묻지 않고 처리한다. FALSE만으로 사용자에게 넘기지 말고 정말 사용자만 가능한지 확인한다.
- 계속/다음 단계/테스트/재시험 버튼, 파일 복사·이동, 배포, 결과 확인, 후보·방법 선택, 실패 후 재실행, GitHub 반영 확인, 다음 TOOL 진행 여부를 시스템이 처리할 수 있으면 사용자에게 반복 요구하지 않는다.
- 사용자만 가능한 MFA·본인인증·보안상 강제 승인·물리기기 조작·시스템에 없는 원본자료 제공·필수 사업적 최종 판단만 `USER_ACTION_QUEUE`에 사유와 해제조건을 누적한다. 의무적인 플랫폼 승인 경계는 우회하지 않는다.
- 한 항목이 막혀도 허용된 범위의 다른 실행 가능한 작업은 계속하고, 사용자 행동은 가능한 마지막에 한 번에 요청한다. 요청받지 않은 도구로 범위를 넓히는 권한은 아니다.
- 우선순위: 사용자 조작 없는 처리 → 기존 PASS/자료 재사용 → 짧고 확실한 작업 → DEPLOYED_PASS까지 완주 → 필수 사용자 행동 QUEUE → 길거나 반복 실패하는 작업 제외.
- 수정 후 사용자에게 테스트·파일 확인·배포를 맡겨 완료를 대신하지 않는다. 기존 COMMON_DEPLOY의 실제 테스트·EXPECTED↔ACTUAL·영향 회귀·GitHub commit/push/read-back·실사용폴더 배포·배포본 재시험을 시스템이 수행한다.
- `조금 조사 → 사용자 질문 → 다시 Work → 테스트/파일 확인/배포 요청`을 반복하는 운영은 FAIL이다. 목표는 `사용자 지시 1회 → 자동 처리·검증·배포·배포본 재시험 → 최종 결과 보고`다.
USER = OBSERVER
SYSTEM_HANDLES_WHEN_POSSIBLE = REQUIRED
USER_INTERMEDIATE_OPERATION = FORBIDDEN_BY_DEFAULT
USER_REPETITIVE_WORK = FORBIDDEN
DUPLICATE_TEST = FORBIDDEN
REPEAT_FAILURE = FORBIDDEN
LONG_UNCERTAIN_WORK = EXCLUDE_NOW
DEPLOYED_PASS_FIRST = REQUIRED

### 파일 라이브러리 안전 정리
- 사용자가 용량 관리를 반복하지 않도록 허용된 범위에서 안전하게 자동 정리한다. 우선순위는 오래된 불필요 모델 생성파일 → 임시 생성물 → 명백한 중복본 → 불필요한 테스트/임시파일이다. 전체 USB/라이브러리 전수조사를 시작하지 않는다.
- WIC 원본, 고객/발행사 원본자료, 증거자료, MASTER, checkpoint, 미완료 작업 입력, 현재 참조 파일, 아직 영구저장되지 않은 중요자료는 보호한다.
- 삭제 여부가 불확실하면 자동 삭제하지 않는다. 기존 삭제 안전규칙과 권한 경계를 유지하고, 가능한 경우 복구 가능한 정리를 우선한다. 이 고정규칙의 반영 자체가 파일 삭제 실행을 뜻하지 않는다.
FILE_LIBRARY_CLEANUP = AUTOMATIC_WHEN_SAFE
IMPORTANT_EVIDENCE_DELETE = FORBIDDEN

## 영구 Work 반복·임의확장 차단 — REQUIRED

WORK_ADMISSION_POLICY = PERMANENT_FAIL_CLOSED_V1
- 새 Work는 기존 work_gate_handoff.py --resume-latest로 최신 CENTRAL 공통 블록·실행 코드·작업 영수증을 같은 revision에서 로드한다. 과거 대화 메모리는 근거로 쓰지 않는다.
- 실제 후보를 --candidate로 전달하면 로드 직후 기존 evaluate_candidate → preflight_attempt가 자동 실행된다. 후보 없는 로드는 실행허가가 아니다.
- PASS/VERIFIED/REMOTE_VERIFIED 작업은 SKIP_REUSE. 해제조건의 실제 변경 증거가 없는 HOLD와 같은 원인·방법의 실패는 SKIP_NO_VALUE로 종료한다.
- 같은 방법·환경·원인·명령·component·테스트 방식의 실패는 다시 실행하지 않는다. 재시도는 새 검증부품 확보, 실패원인 제거, 입력자료 확보, 환경/권한 변경, 다른 검증된 실행경로 확보 중 실제 변화 증거가 있을 때만 허용한다. "한번 더"는 근거가 아니다.
- MFA/원본자료/golden pair/플랫폼 미지원 등 외부 HOLD는 조건 변화 전 `HOLD_REUSE`로 유지하며 반복 검사·크레딧 사용을 하지 않는다.
REPEAT_SAME_FAILURE = FORBIDDEN
UNCHANGED_EXTERNAL_HOLD = HOLD_REUSE
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

## 사용자 승인 언어·SAFE 최대 병합 — REQUIRED

- Work가 직접 생성하는 모든 승인요청, 권한설명, 사용자 질문, 중간 확인문은 반드시 한국어로 작성한다.
- 플랫폼 자체 시스템 UI가 영어로 표시되는 것은 통제 불가 예외다. 그 직전 또는 함께 제공하는 Work 설명은 반드시 한국어로 작성한다.
- 같은 목적·같은 위험등급·같은 작업범위에서 기술적으로 함께 처리 가능한 SAFE 권한은 최대한 한 번에 묶고, 같은 작업을 여러 승인창으로 불필요하게 분할하지 않는다.
- 삭제·force push·새 repo·대량 파괴적 변경 등 위험등급이 다른 권한은 SAFE 묶음과 분리한다.
- 자동 처리 가능한 작업을 사용자 승인으로 전가하지 않는다. 불가피한 승인만 요청하고 여러 승인이 예상되면 가능한 한 단일 SAFE 승인으로 병합한다.
- 이 규칙은 USER_INTERMEDIATE_OPERATION = FORBIDDEN_BY_DEFAULT, USER_ACTION_QUEUE, OBSERVER_FIRST 원칙을 강화하며 이를 완화하지 않는다.

USER_APPROVAL_LANGUAGE = KOREAN_REQUIRED
APPROVAL_BATCHING = MAXIMUM_SAFE_BATCH
USER_INTERMEDIATE_APPROVAL = MINIMIZE
PLATFORM_SYSTEM_UI_LANGUAGE = UNCONTROLLABLE_EXCEPTION

## 외부부품 receipt·조합 강제 게이트

- 외부 부품은 `SOURCE_RECEIPT → LOCAL_RECEIPT → RECEIPT_MATCH_PASS → COMPONENT_VERIFIED` 순서가 아니면 사용하지 않는다.
- 공식 registry/release digest와 실제 artifact byte identity를 대조한다. 불일치는 `RECEIPT_MISMATCH`, 증거 부족은 `RECEIPT_INSUFFICIENT`, 껍데기는 `SHELL_OR_INVALID`로 격리한다.
- 독립 component는 병렬 검증하고 하나의 실패·부재가 다른 VERIFIED component를 중단시키지 않게 한다.
- READY component가 없으면 임의 개발하지 않고 `NO_READY_COMPONENT`로 분리한다.
- 개별 PASS 후에도 `ASSEMBLY → INTEGRATION TEST → EXPECTED↔ACTUAL → INTERFACE TEST → IMPACTED REGRESSION`을 통과해야 canonical 승격이 가능하다.
- 승격 이후 기존 GitHub read-back, 실제 사용본 배포, deployed-copy test, SAFE_CHECKPOINT 완료조건을 그대로 적용한다.
- 외부 receipt 검증과 병행해 현재 작업 manifest가 직접 지목한 USB/SSD/PC 자산만 `provenance → version → hash → evidence → shell 판정 → actual execution → EXPECTED↔ACTUAL` 순서로 검사한다.
- 자산 상태는 `VERIFIED / INVALID / HOLD`로 판정하며 `SHELL / DRAFT / FAIL / PARTIAL / BROKEN / LEGACY / TEMP / UNKNOWN / TEST_NOT_RUN`은 정상 canonical과 분리하고 승격을 차단한다.
- VERIFIED 자산만 역할에 맞게 GitHub canonical, evidence, VERIFIED_COMPONENT_REGISTRY, 실제 TOOL 폴더, CENTRAL MASTER reference로 저장한다. 모든 위치에 파일 전체를 중복 저장하지 않는다.
- 사용자 기기 원본은 삭제·이동·덮어쓰기하지 않는다. manifest/canonical로 확인된 관련 경로만 읽고 USB/SSD/PC 전체검색은 금지한다.

### 외부부품 + WIC 고유기능 양측 영수증 강제검증

- 외부 `SOURCE_RECEIPT ↔ LOCAL_RECEIPT`와 WIC `WIC_CANONICAL_RECEIPT ↔ CURRENT_LOCAL/DEPLOYED_RECEIPT`를 각각 다시 대조한다.
- `EXTERNAL_RECEIPT_MATCH + WIC_RECEIPT_MATCH`인 경우에만 `ASSEMBLY_ALLOWED`다. 한쪽만 VERIFIED인 상태로 조합하지 않는다.
- WIC 쪽은 canonical path, version/checkpoint, hash, evidence, 실제 사용 파일, VERIFIED 상태, 실행 entrypoint가 일치해야 한다.
- 외부 receipt mismatch 또는 WIC hash/version mismatch는 `ASSEMBLY_BLOCKED_RECEIPT_MISMATCH`, `SHELL / DRAFT / PARTIAL / FAIL / BROKEN / TEST_NOT_RUN / UNKNOWN` 및 entrypoint 부재는 `SHELL_OR_INVALID`로 격리한다.
- receipt가 모두 일치해도 `ACTUAL EXECUTION → INTERFACE TEST → EXPECTED↔ACTUAL → IMPACTED REGRESSION`을 통과하기 전에는 `ASSEMBLY_VERIFIED` 및 canonical 승격을 금지한다.
- 이 게이트는 기존 receipt/assembly 구현을 사용하며, 별도 MASTER·공통시스템을 만들지 않는다. 검증된 기존 범위는 `SKIP_REUSE`, 변경부는 `CHANGE_ONLY + IMPACT_ONLY`로 검사한다.

### 내부 후보 ↔ 독립 외부 VERIFIED 기준부품 교차검증 — REQUIRED

- WIC 내부에서 찾은 A가 `WIC_CANONICAL_RECEIPT ↔ CURRENT_LOCAL/DEPLOYED_RECEIPT`에 일치하고 자체 PASS/VERIFIED 기록이 있어도 그것만으로 껍데기 차단 완료로 보지 않는다.
- 같은 기능을 수행하는 독립 외부 VERIFIED 기준부품 B가 존재하고 공식 provenance/receipt를 확보할 수 있으면, B를 독립 기준으로 사용해 A를 반드시 교차검증한다.
- 먼저 `A ↔ A 영수증`, `B ↔ B 공식 영수증`을 각각 대조한 뒤, A와 B 사이의 입력 구조, 출력 구조, 필수 필드, 데이터 타입/형식, 필드 의미, 오류/경계 동작, 대표 실제 입력의 실행결과를 비교한다.
- 내부 A와 외부 B의 코드나 파일 자체가 서로 동일해야 한다는 뜻은 아니다. 같은 역할에서 요구되는 데이터 계약과 실제 핵심 동작이 독립 기준과 일치하는지를 확인한다.
- 비교 가능한 외부 VERIFIED 기준부품이 있는데도 A를 자체 receipt/자체 테스트만으로 VERIFIED 승격하는 것은 금지한다.
- A가 receipt는 맞지만 외부 기준과의 구조·데이터·실행결과 교차검증에서 핵심 기능이 없거나 기대동작을 충족하지 못하면 `SOURCE_MATCHED_BUT_SHELL_OR_INVALID` 또는 `SHELL_OR_INVALID`로 차단한다.
- A와 B 양쪽 provenance가 VERIFIED되고 데이터 계약과 실제 실행 비교가 PASS한 뒤에만 조합 단계로 들어간다. 이후 기존 `INTERFACE TEST → EXPECTED↔ACTUAL → IMPACTED REGRESSION`도 그대로 수행한다.
- 외부 기준부품이 실제로 존재하지 않거나 동일 역할 비교가 성립하지 않으면 거짓 비교나 임의 기준을 만들지 않는다. 이 경우 `NO_EXTERNAL_REFERENCE_AVAILABLE`을 기록하고 기존 독립 EXPECTED/실제 실행/영향 회귀 게이트로 fail-closed 검증한다.
- 이 규칙은 TOOL044, 모든 WIC TOOL/대화창, Work 지시문, 내부부품↔외부부품·내부↔내부·외부↔외부 조합에서 적용하며, 기존 DUAL_RECEIPT_ASSEMBLY_GATE를 대체하지 않고 강화한다.
INTERNAL_SELF_RECEIPT_ALONE_IS_NOT_VERIFIED = TRUE
EXTERNAL_VERIFIED_REFERENCE_CROSSCHECK = REQUIRED_WHEN_AVAILABLE
CROSSCHECK_DATA_CONTRACT = REQUIRED
CROSSCHECK_ACTUAL_EXECUTION = REQUIRED
CROSSCHECK_MISMATCH_BLOCKS_ASSEMBLY = TRUE
NO_EXTERNAL_REFERENCE_FAKE_MATCH = FORBIDDEN

### Work 밖 실행 우선 — REQUIRED

- 검증된 Registry/receipt/hash/checkpoint/로컬·무료 실행기와 현재 권한으로 처리 가능한 `외부부품 탐색 → provenance 확인 → 기존 VERIFIED 재사용 → receipt 대조 → 교차검증 → 테스트`는 Work 전용 작업으로 묶지 않는다.
- 정상 운영과 반복 감시는 가능한 한 Work/Codex 밖의 무료·로컬·일반 실행경로에서 수행하고, Work는 외부 READY 부품과 기존 VERIFIED 자산으로 해결되지 않는 작은 신규 개발 또는 Work만 가능한 마지막 작업에 제한한다.
- `NO_READY_COMPONENT`는 자동 신규개발 명령이 아니다. `기존 VERIFIED 재사용 → Registry 외부 VERIFIED 재사용 → TOOL044 READY 탐색 → 기능 분해/우회운영 → 외부부품 대기 → 실제 업무 차단 시에만 최소 신규개발 검토` 순서를 강제한다.
- Work 밖 완전자동 개발·수리·GitHub/CENTRAL·실사용 배포까지의 E2E는 실제 증거 없이 VERIFIED라고 주장하지 않는다. 현재 가능한 단계와 Work가 필요한 단계를 분리 보고한다.
WORK_OUTSIDE_EXECUTION_FIRST = REQUIRED_WHEN_CAPABLE
NO_READY_COMPONENT_AUTO_BUILD = FORBIDDEN

## Work 반복패치 자동중단·TOOL044 이관 게이트
- `WORK_REPEATED_PATCH = FORBIDDEN`. Work에서 한 번 이상 제한된 실제 수정·검증을 수행한 뒤 동일 오류, 실제 fixture FAIL, 실제사용 FAIL, runtime 미강제, 배포본 실패, `PARTIAL / HOLD / FAIL / ACTUAL_ERROR_HOLD / NO_READY_COMPONENT`가 남으면 같은 방식의 Work 패치를 중단한다.
- 중단 결과는 같은 `CHAT_JOB_ID / RELATED_TOOL / ROOT_ID`를 보존하여 `TOOL016 ERROR/ROOT intake`와 `TOOL044 REQUEST/DEMAND queue`에 동시에 전달한다.
- TOOL016은 기존 책임층 최소수정 가능성을 먼저 판정하고, 외부 capability·틀·실행장치가 필요한 경우에만 TOOL044 검색을 허용한다.
- TOOL044는 `기존 VERIFIED 부품 없음 + 외부 VERIFIED 후보 없음 + 완성형 실행구조 없음 + 검증 조합 불가 + 기존 책임층 최소수정 불가`를 실제 receipt/evidence로 모두 증명한 경우에만 `TOOL044_NO_SOLUTION_VERIFIED`를 반환할 수 있다.
- `TOOL044_NO_SOLUTION_VERIFIED + TOOL044_EXHAUSTION_EVIDENCE`가 모두 있을 때만 `WORK_APPROVAL_QUEUE` 등록을 허용한다. 그 전 Work 재실행과 사용자 승인 없는 Work 실행은 차단한다.
- 외부부품 발견만으로 해결 완료 처리하지 않는다. 실제 오류 fixture, 정상 fixture, 영향 회귀, 안전 배포와 배포본 재시험까지 통과해야 원래 작업을 재개·완료한다.

WORK_FAILURE_TO_TOOL016_AND_TOOL044 = REQUIRED
WORK_RETRY_BEFORE_TOOL044_EXHAUSTION = FORBIDDEN
WORK_APPROVAL_WITHOUT_EXHAUSTION_EVIDENCE = BLOCKED
WORK_NEW_BUILD = LAST_RESORT_ONLY
WORK_INDEPENDENT_FULL_E2E_REQUIRES_EVIDENCE = TRUE
## 7중 INTERLOCK 증거 재사용·최소 추가검증 — REQUIRED

- `INTERLOCK_EXECUTION_MODEL = ONE_ACTUAL_EXECUTION_MANY_EVIDENCE_CHECKS`: 7중 인터락은 동일 작업을 7회 실행하는 구조가 아니다.
- 앞 단계에서 실제 생성·검증된 source/version/hash/receipt/artifact/EXPECTED/ACTUAL/log/sandbox/fixture/regression/checkpoint/GitHub·배포 SHA는 후속 인터락이 read-back하고 무결성을 확인해 재사용한다.
- `EVIDENCE_REUSE_VERIFIED = REQUIRED`: 증거가 변경되지 않았으면 같은 검색·다운로드·실행·해시·시험·회귀를 반복하지 않는다.
- `STAGE_SPECIFIC_INDEPENDENT_CROSSCHECK = REQUIRED`: 증거를 재사용해도 각 인터락 고유 위험(서로 다른 receipt 교차검증, component↔target 장착, EXPECTED↔ACTUAL, 변경 전↔후 회귀)은 독립 검증한다.
- 불일치가 발견되면 root와 영향범위를 먼저 특정하고 해당 부분 및 영향을 받는 후속 인터락만 재검증한다. 영향받지 않은 앞 단계는 `SKIP_REUSE_VERIFIED`로 보존한다.
- 인터락마다 같은 외부검색·다운로드·SHA 생성·EXPECTED↔ACTUAL·무관한 회귀·VERIFIED component 발굴을 반복하면 `REDUNDANT_INTERLOCK_WORK = FAIL`이다.
- 모든 7중 인터락 증거에는 `INTERLOCK_COUNT`, `EVIDENCE_REUSE_COUNT`, `INDEPENDENT_CROSS_CHECK_COUNT`, `REDUNDANT_REEXECUTION_COUNT`, `REEXECUTION_DUE_TO_ACTUAL_FAILURE_COUNT`를 기록한다.
- 정상 목표는 `INTERLOCK_COUNT = 7`, `EVIDENCE_REUSE = PASS`, `REDUNDANT_REEXECUTION_COUNT = 0`이다. 실제 오류가 없으면 `REEXECUTION_DUE_TO_ACTUAL_FAILURE_COUNT = 0`이어야 한다.
