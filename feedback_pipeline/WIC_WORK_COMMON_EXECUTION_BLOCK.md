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
