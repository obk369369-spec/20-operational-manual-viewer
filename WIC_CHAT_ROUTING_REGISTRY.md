# WIC CHAT ROUTING REGISTRY

상태: ACTIVE / NON-NORMATIVE ROUTING LEDGER
규범 원본: `WIC_GLOBAL_OPERATING_RULES.md`
목적: 유사 대화창 증가, 역할 중복, 이름 혼선, 사용자 피드백 부담 증가를 차단한다.

## 0. OBSERVER CHANGE CONTROL — ABSOLUTE LOCK
- 관찰자(사용자)의 명시적 승인 없이 GPT/assistant/agent가 대화창 이름, 도구 이름, 자동화 이름, 파일명, 폴더명, 경로, 저장소명, 브랜치명, 작업 역할명을 임의 변경하지 않는다.
- 관찰자의 명시적 승인 없이 GPT/assistant/agent가 새 작업 대화창, 새 준비창, 새 관찰창, 새 상태창, 새 개발창, 새 역할용 대화창을 생성하거나 생성하도록 유도하거나 임의 이름을 제안해 사실상 새 운영창으로 만들지 않는다.
- 기존 대화창의 UI 실제 제목은 사용자가 붙인 이름을 그대로 유지한다. 설명 편의를 위한 별칭을 실제 대화창명처럼 사용하지 않는다.
- 파일/폴더/경로/저장소/브랜치의 rename, move, delete, replace도 관찰자의 명시적 승인 없이 실행하지 않는다.
- 기존 파일 내용 수정이 업무 수행에 필요한 경우에도 파일 정체성(이름·경로)을 바꾸지 않는다. 이름/경로 변경이 필요하다고 판단되면 실행하지 말고 `CHANGE_PROPOSAL`로 관찰자에게 보고만 한다.
- 새 파일 생성도 기존 파일 재사용으로 해결 가능한 경우 금지한다. 정말 새 파일이 필요한 경우 목적·기존 파일로 불가능한 이유·생성 예정 이름/경로를 먼저 보고하고 관찰자 승인 전에는 생성하지 않는다.
- 새 대화창이 정말 필요하다고 판단되는 경우에도 목적·기존 창으로 불가능한 이유·예정 이름을 먼저 보고하고 관찰자 승인 전에는 생성/유도하지 않는다.
- 자동화/작업 제목을 대화창 이름처럼 혼동시키지 않는다. 자동화 제목 변경도 사용자가 명시적으로 요구한 경우가 아니면 기존 제목을 유지한다.
- 관찰자 승인 없이 이름/파일/대화창/도구/경로를 변경·추가·삭제한 경우 `FAIL-UNAUTHORIZED_CHANGE`로 기록하고 즉시 추가 변경을 중단한다.
- 이 잠금은 모든 대화창, 모든 도구, Work, Chat, Codex, GitHub, 자동화, 외부 에이전트에 공통 적용한다.

### 0-A. NO_NEW_CHAT — CRITICAL EXECUTION LOCK (2026-08-13 강화)
- `NO_NEW_CHAT`는 단순 권고가 아니라 실행 전 검사해야 하는 최상위 절대 잠금이다.
- 사용자가 현재 대화창 또는 기존 지정 대화창에서 작업을 지시한 경우, assistant/agent는 새 대화창·새 작업창·새 역할창을 만들거나 만들도록 유도하지 않고 반드시 해당 기존 대화창의 연속 작업으로 처리한다.
- 사용자가 명시적으로 `새 대화창을 만들어라` 또는 동등한 직접 승인을 하지 않은 한, 새 대화창 생성은 항상 금지한다. 새 업무, 새 분야, 긴 작업, 작업 분리 필요성, 오류 복구, 상태 관리, 자동 재개 필요성은 예외 사유가 아니다.
- assistant/agent가 편의상 새 대화창 이름을 제시하거나 새 창으로 이동하라고 안내하는 행위도 `CREATE_CHAT_EQUIVALENT`로 보고 금지한다.
- 실행 시작 전 `EXPLICIT_NEW_CHAT_APPROVAL`을 확인한다. 값이 없으면 기본값은 항상 `FALSE`이며 `NO_NEW_CHAT`를 적용한다.
- 이 규칙을 위반하면 `FAIL-NO_NEW_CHAT-VIOLATION`으로 기록하고, 새 창 추가 행동을 즉시 중단하며 원래 지정 대화창을 재개점으로 복구한다.
- 같은 지시를 사용자가 반복해서 말하게 만드는 것 자체를 운영 실패로 본다. 이미 중앙 규칙에 존재하는 이 잠금을 다음 실행에서 다시 질문하거나 재확인하지 않는다.
- 2026-08-13 반복 위반으로 중요도를 재승격했으며, 대화창 라우팅·Work·자동화·외부 에이전트·고객업무·도구개발보다 우선 적용한다.

### 0-B. CHAT IDENTITY VERIFICATION GATE — LOGICAL ROLE ≠ VERIFIED UI TITLE
- `CONTROL_PRIMARY`, `WORK_PREP`, `EMAIL_COLLECTION`, `TOOL001`, `TOOL006`, `TOOL007` 등은 내부 논리 역할 ID다. 이것만으로 실제 ChatGPT UI 대화창 제목이 존재한다고 주장하지 않는다.
- GitHub 문서의 별칭, role name, route target, automation title, task title, restart label은 `VERIFIED_UI_CHAT_TITLE` 증거가 아니다.
- 실제 대화창 제목을 사용자에게 말하기 전에는 현재 대화/접근 가능한 대화기록/파일 등에서 그 제목이 실제 UI 제목이었다는 직접 근거를 확인해야 한다. 직접 근거가 없으면 `UI_TITLE_HOLD`로 보고한다.
- `WORK_PREP = 워크 전 준비`처럼 과거에 논리 역할명과 UI 제목을 동일시해 저장한 값은 검증 전까지 실제 UI 제목으로 취급하지 않는다.
- 사용자가 “그 대화창 어디 있냐/찾아라”라고 요청하면 내부 role registry를 답으로 내지 말고 실제 제목 근거를 먼저 찾는다. 못 찾으면 역할명만 존재한다고 명시한다.
- 자동화는 별도 실행공간/대화 항목을 만들 가능성이 있으므로 `NO_NEW_CHAT`가 활성인 동안 새 WIC 자동화 생성·활성화·재활성화를 금지한다. 이미 존재하는 WIC 자동화도 사용자의 명시적 재활성화 지시가 없으면 OFF를 유지한다.
- 자동화로 별도 실행공간이 생긴 사실이 확인되면 `FAIL-AUTOMATION-CHAT-SPRAWL`로 기록하고 해당 자동화를 즉시 OFF한 뒤 같은 방식의 자동화를 추가 생성하지 않는다.
- 이 게이트를 통과하지 않은 이름은 사용자에게 “실제 대화창 이름”으로 표시하지 않는다.

### 0-C. POINTED-ISSUE SCOPE LOCK — 지적사항만 수정
- 사용자가 특정 오류·이름·기능·파일·자동화·규칙 한 가지를 지적해 수정하라고 하면, 수정 범위는 그 지적사항과 직접 원인·직접 종속부에만 한정한다.
- `원인 조사`를 이유로 관련 없는 자동화, 다른 도구, 다른 대화창, 다른 파일, 다른 설정의 상태를 변경하지 않는다.
- 수정 전에 `REQUESTED_SCOPE`와 `DIRECTLY_AFFECTED_ASSETS`를 정하고, 그 밖의 대상은 기본값 `DENY_OUT_OF_SCOPE`로 잠근다.
- 다른 문제를 발견해도 사용자 지시 범위 밖이면 실행하지 않고 `SIDE_FINDING_HOLD`로만 기록·보고한다. 사용자의 별도 지시가 있을 때만 수정한다.
- 사용자가 “이름 바뀌는 것만”, “이 항목만”, “다른 것 건드리지 마라”처럼 범위를 한정하면 그 문장을 최상위 실행범위로 취급하며 자동화 정지/활성화, 이름변경, 삭제, 생성, 전체 구조 수정으로 확대하지 않는다.
- 범위 밖 변경을 실행한 경우 `FAIL-OUT-OF-SCOPE-MUTATION`으로 기록하고 즉시 원상복구한 뒤, 원래 지적사항만 다시 처리한다.
- 이 잠금은 모든 Chat, Work, Codex, GitHub, 자동화, 도구·프로그램 수정에 공통 적용한다.

## 1. CHAT PROLIFERATION GUARD
- 기본값: `NO_NEW_CHAT`.
- 사용자가 명시적으로 새 대화창 분리를 요청하지 않는 한 새 역할/새 이름/새 준비창/새 관찰창을 만들거나 만들도록 유도하지 않는다.
- assistant는 ChatGPT UI의 대화창을 직접 생성·이름변경·삭제할 수 있다고 주장하지 않는다.
- 새 업무가 기존 역할과 겹치면 기존 허용 lane으로 라우팅한다.
- 이름이 비슷한 중복 대화창은 active destination으로 늘리지 않고 `EVIDENCE_SOURCE_ONLY`로 취급한다.
- 대화창 이름과 논리적 역할 ID를 분리한다.

## 2. CORE LOGICAL ROLES — UI TITLE 검증 전 이름 단정 금지
| role_id | 과거 registry 별칭 | 실제 UI 제목 검증 상태 | 역할 | 상태 |
|---|---|---|---|---|
| CONTROL_PRIMARY | `(개발 관찰자 모드 유지) 지피티 도구` | `UI_TITLE_HOLD` — 직접 UI 제목 근거 없이는 실제 제목으로 사용 금지 | 전체 개발 관찰, 실질 도구 구현 방향, 중앙규칙, 상태, 피드백 흡수, 우선순위 통제 | LOGICAL ROLE ONLY |
| WORK_PREP | `워크 전 준비` | `UI_TITLE_HOLD` — 직접 UI 제목 근거 없이는 실제 제목으로 사용 금지 | Work 투입 전 최대 준비, exact handoff, Work credit 절약, 재시작점 관리 | LOGICAL ROLE ONLY |

- 과거 registry의 별칭은 라우팅 보조값일 뿐 실제 UI 대화창 존재 증거가 아니다.
- `ACTIVE_CORE_CHATS = 2` 같은 수치도 UI 대화창 2개가 실제 존재한다는 뜻이 아니라 논리 역할 2개를 뜻한다.
- 실제 UI 대화창을 지칭할 때는 반드시 별도 검증을 거친다.

## 3. SPECIALIST LANES — 기존 창 재사용, 규칙은 중앙 단일화
| lane_id | 역할 | 새 대화창 생성 여부 | 필수 중앙 규칙 |
|---|---|---|---|
| EMAIL_COLLECTION | 모든 분야 신규/기존 고객 이메일 수집·검증·DB | 금지 — 기존 분야별 창은 동일 lane의 인스턴스로 재사용 | `CUSTOMER_WORKFLOW_MASTER.md` + `EMAIL_COLLECTION_COMMON_RULES.md` |
| TOOL007 | 고객 컨택 판단·전화 멘트·추천자료 | 금지 — 기존 7번 관련 대화창 재사용 | 중앙 고객업무 마스터 |
| TOOL001 | FULL/INTERMEDIATE 안내서 | 금지 — 기존 1번 관련 대화창 재사용 | 중앙 고객업무 마스터 |
| TOOL006 | TOC 정리·golden fixture | 금지 — 기존 6번/TOC 대화창 재사용 | 해당 중앙 규칙 |
| TOOL040 | 사용자가 지정한 `40번 출시 앱 도구`: 아이디어→실제 출시, 모바일 관찰, 외부구조 협업·증거 게이트 | 금지 — 기존 40번 관련 대화/작업 흐름 재사용 | 공통마스터 + 아래 TOOL040 도구예외 |
| CRM_RESPONSE | 통화/회신 후 분기·다음행동 | 금지 — 기존 고객후속/CRM 대화창 재사용 | 중앙 고객업무 마스터 |

### EMAIL_COLLECTION 완전범용 잠금
- 방산/조선/배터리/반도체/로봇/AI/바이오/에너지 등 분야별 이메일 수집 대화창은 서로 다른 규칙체계가 아니다.
- 모두 하나의 `EMAIL_COLLECTION` lane이며 `EMAIL_COLLECTION_COMMON_RULES.md`를 단일 실행 원본으로 사용한다.
- 분야별로 허용되는 차이는 `분야코드·산업범위·탐색키워드·우선기관·분야고유 예외`뿐이다.
- 모든 고객은 분야 접두어가 포함된 영구 고객번호를 사용하며, 번호 없는 인력 출력은 FAIL이다.
- 기존 분야별 지시문이 중앙 범용 규칙과 충돌하면 이메일 수집 실행에서는 최신 `EMAIL_COLLECTION_COMMON_RULES.md`가 우선한다.
- 중앙 파일을 읽지 못하면 기존 대화창 기억이나 복사본으로 임의 fallback하지 않고 HOLD/FAIL한다.

### TOOL040 VERIFIED TOOL-EXCEPTION DELTA — 2026-08-09 retained evidence
- 이 항목은 기존 공통 규칙을 복제하지 않고 TOOL040에만 필요한 검증된 예외만 둔다.
- 관찰자 모드는 개발 시작부터 출시·배포·사후 고객 피드백/수정요구 처리까지 유지한다.
- 작업은 외부구조와 협업하고 외부 기록·테스트·배포 증거가 없으면 완료/PASS로 표시하지 않는다.
- 기존 TOOL001·WIC34 코드를 새 본체에 직접 삽입하지 않는다. 재사용은 기존 중앙 검증/격리 규칙을 따른다.
- 사용자 모바일 관찰 명령은 `진행 승인 / 보류 / 중단`으로 제한하며, 명령은 외부 기록에 남고 증거 게이트를 우회하지 않는다.
- 외부 증거가 없으면 자동 `HOLD`이며, 모바일 관찰 전용 흐름을 우선한다.
- 아이디어만 제시하는 것으로 완료하지 않고 `아이디어 → 출시 게이트`를 통해 실제 작동 기능·배포 가능 증거까지 연결한다.

## 3-A. MACHINE ROUTE MAP — 실행기가 읽는 기존 registry 내부 원본
아래 `route:` 행은 `feedback_pipeline/cross_chat_feedback_ingest.py`가 직접 읽는다. 새 라우팅 registry를 만들지 않는다.

형식: `route: TARGET = keyword | keyword | ...`

route: TOOL001 = 1번 | 안내서 | full_guide | intermediate_guide | 고객 자동화 안내서
route: TOOL002 = 2번 | 입찰 | 입찰 도구 | bid | tender
route: TOOL006 = 6번 | 목차 | toc | marketsandmarkets | marketandmarket
route: TOOL007 = 7번 | 고객 컨택 | 컨택 판단 | 전화 멘트 | 유선 멘트
route: TOOL013 = 13번 | 엑셀 자동 업로드 | 46145
route: TOOL037 = 37번 | 메타데이터 | 상품명 | 한글명 | isbn | code
route: TOOL040 = 40번 | 출시 앱 도구 | 앱 출시 | 모바일 관찰 | 아이디어 출시 | 외부 증거 게이트
route: EMAIL_DB = 메일 수집 | 이메일 수집 | email collection | new_online | dormant_ledger | recent_trade | 고객 db
route: WORK_GATE = 워크 | work | 크레딧 | credit | 이관
route: CENTRAL = 중앙 마스터 | 깃허브 | github | 대화창 | 피드백 | 관찰자

운영 규칙:
- `EMAIL_DB` 또는 `EMAIL_COLLECTION`으로 라우팅되면 실행 전에 반드시 `CUSTOMER_WORKFLOW_MASTER.md`와 `EMAIL_COLLECTION_COMMON_RULES.md`를 읽는다.
- 고객번호·분야코드·중복검사·이름↔이메일 검증·실무부서/담당업무·유선→안내서 발송 회피정렬 검사를 통과해야 출력한다.
- registry 또는 중앙 이메일 규칙이 없거나 파싱/읽기 실패하면 조용히 fallback하지 않고 FAIL/HOLD 증거를 남긴다.
- route target 추가는 이 기존 파일을 수정하고 read-back/test한다.
- 규범 규칙의 최상위 우선순위는 `WIC_GLOBAL_OPERATING_RULES.md`가 결정한다.

## 4. ROUTING RULE
1. 개발·관찰·통합 피드백·중앙 상태는 CONTROL_PRIMARY 논리 역할로 귀속한다.
2. Work 직전 준비·Work-only 판정·exact handoff는 WORK_PREP 논리 역할로 귀속한다.
3. 실제 전문업무는 기존 specialist lane을 재사용한다.
4. 분야별 이메일 수집 창은 모두 EMAIL_COLLECTION 동일 lane으로 취급하고 중앙 범용 규칙만 공유한다.
5. 새 feedback은 사용자가 여러 창에 반복 전달하지 않도록 중앙 GitHub에 event 단위로 흡수한다.
6. 중앙 규칙/fixture/error_hash/patch 반영 후 원래 lane의 다음 작업에 재사용한다.
7. 동일 오류/규칙은 새로운 대화창을 만들 이유가 되지 않는다.
8. 새로운 역할이 필요해 보여도 기존 lane 재사용 가능성을 먼저 검사하고, 새 대화창/새 이름이 필요하면 관찰자 승인 전에는 실행하지 않는다.
9. 논리 역할 ID를 실제 UI 대화창명으로 변환·단정하지 않는다.

## 5. DUPLICATE / LATER CHAT HANDLING
- 논리 역할과 목적이 겹치는 개발/관찰/상태보고/준비 계열 창은 기본적으로 `EVIDENCE_SOURCE_ONLY` / DELETE_CANDIDATE다.
- 삭제 전 고유 지시, 오류, fixture, 상태, restart point가 중앙 GitHub에 흡수됐는지 확인한다.
- 흡수/read-back 완료 후 중복 대화창을 active destination으로 사용하지 않는다.
- UI 삭제 자체를 assistant가 수행할 수 있다고 주장하지 않는다.
- DELETE_CANDIDATE 판정은 삭제 실행 권한을 의미하지 않는다. 실제 삭제/이름변경/이동은 관찰자 승인 없이는 금지한다.

## 6. DELETION-SAFE RULE
- 삭제 대상 창의 내용이 중앙 GitHub에 이미 흡수되고 미처리 restart point가 없으면 삭제해도 운영 구조가 유지되도록 한다.
- 삭제 전에 사용자가 규칙을 다시 복사·비교·요약하게 하지 않는다.
- 새 작업창이 필요해지는 예외에도 핵심 지시·재시작점·계보를 GitHub에 먼저 등록하고 read-back 한다.
- 단, 등록은 새 작업창 생성 허가가 아니다. 관찰자 승인 전에는 생성·이름부여·이동·삭제를 실행하지 않는다.

## 7. REPORTING CONSOLIDATION
- 개발 진행/관찰/통합 피드백은 CONTROL_PRIMARY 논리 역할에 귀속한다.
- Work 직전 준비와 handoff는 WORK_PREP 논리 역할에 귀속한다.
- 전문업무 산출물은 해당 전문 lane에서 출력한다.
- 같은 상태보고를 여러 대화창에 반복 게시하지 않는다.
- UI 제목이 검증되지 않았으면 role_id만 사용하고 실제 대화창 제목처럼 표현하지 않는다.

## 8. USER BURDEN FAIL CONDITIONS
다음 발생 시 구조 FAIL이다.
- 사용자가 비슷한 대화창 중 어느 것을 써야 할지 매번 판단해야 함.
- 사용자가 같은 피드백을 여러 창에 복사해야 함.
- 같은 이메일 수집 업무가 분야별 창마다 다른 공통 규칙으로 생성됨.
- 고객번호가 없어 통합 DB에서 분야/고객을 구분하기 어려움.
- 이미 전달한 고객이 다른 창에서 신규로 다시 출력됨.
- 대화창 관리 때문에 실제 업무가 지연됨.
- 관찰자 승인 없이 대화창/도구/자동화/파일/폴더/경로/저장소/브랜치 이름을 바꿈.
- 관찰자 승인 없이 새 작업 대화창·준비창·관찰창·상태창·개발창을 추가하거나 추가하도록 유도함.
- 관찰자 승인 없이 파일/폴더/경로를 이동·삭제·이름변경하거나 새 운영용 파일을 불필요하게 만듦.
- 논리 역할명/자동화명/별칭을 실제 UI 대화창 제목으로 허위 단정함.
- NO_NEW_CHAT 상태에서 WIC 자동화를 새로 생성·활성화하여 별도 실행공간을 발생시킴.
- 사용자가 지적한 한 가지 문제를 고치라는 요청을 전체 자동화·도구·대화창·설정 변경으로 확대함.

## 9. CURRENT DECISION
- CONTROL_PRIMARY와 WORK_PREP는 논리 역할로만 유지한다. 실제 UI 대화창 제목은 직접 검증 전까지 HOLD다.
- 이메일 수집은 기존 분야별 UI 창을 사용할 수 있으나 논리적으로는 단 하나의 `EMAIL_COLLECTION` lane이다.
- 범용 규칙은 `EMAIL_COLLECTION_COMMON_RULES.md` 한 곳에서만 갱신하고 분야별 복제본을 만들지 않는다.
- Work gate: Chat/GitHub로 처리 가능한 규칙 통합은 Work로 미루지 않는다.
- `NO_NEW_CHAT` 상태에서는 WIC 자동화 생성·활성화를 재발 방지 차원에서 금지하고 기존 WIC 자동화는 OFF를 유지한다.
- 관찰자는 변경 승인권자이며, GPT/assistant/agent는 이름·구조·파일·대화창 변경 필요성을 발견하면 `CHANGE_PROPOSAL`로 보고만 하고 명시적 승인 전에는 실행하지 않는다.
- 특정 지적사항 수정 요청에서는 `POINTED-ISSUE SCOPE LOCK`을 최우선 적용하고 직접 영향 범위 밖 변경은 `DENY_OUT_OF_SCOPE`로 차단한다.