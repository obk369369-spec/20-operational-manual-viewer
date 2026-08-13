# WIC CHAT ROUTING REGISTRY

상태: ACTIVE / NON-NORMATIVE ROUTING LEDGER
규범 원본: `WIC_GLOBAL_OPERATING_RULES.md`
목적: 유사 대화창 증가, 역할 중복, 이름 혼선, 사용자 피드백 부담 증가를 차단한다.

## 1. CHAT PROLIFERATION GUARD
- 기본값: `NO_NEW_CHAT`.
- 사용자가 명시적으로 새 대화창 분리를 요청하지 않는 한 새 역할/새 이름/새 준비창/새 관찰창을 만들거나 만들도록 유도하지 않는다.
- assistant는 ChatGPT UI의 대화창을 직접 생성·이름변경·삭제할 수 있다고 주장하지 않는다.
- 새 업무가 기존 역할과 겹치면 기존 허용 lane으로 라우팅한다.
- 이름이 비슷한 중복 대화창은 active destination으로 늘리지 않고 `EVIDENCE_SOURCE_ONLY`로 취급한다.
- 대화창 이름과 논리적 역할 ID를 분리한다.

## 2. CORE CHATS — 사용자 지정 2개만 유지
| chat_id | 실제 대화창 이름 | 역할 | 상태 |
|---|---|---|---|
| CONTROL_PRIMARY | `(개발 관찰자 모드 유지) 지피티 도구` | 전체 개발 관찰, 실질 도구 구현 방향, 중앙규칙, 상태, 피드백 흡수, 우선순위 통제 | KEEP / ACTIVE |
| WORK_PREP | `워크 전 준비` | Work 투입 전 최대 준비, exact handoff, Work credit 절약, 재시작점 관리 | KEEP / ACTIVE |

- 목표: `ACTIVE_CORE_CHATS = 2`, `MANUAL_FEEDBACK_FORWARDING = 0`.

## 3. SPECIALIST LANES — 기존 창 재사용, 규칙은 중앙 단일화
| lane_id | 역할 | 새 대화창 생성 여부 | 필수 중앙 규칙 |
|---|---|---|---|
| EMAIL_COLLECTION | 모든 분야 신규/기존 고객 이메일 수집·검증·DB | 금지 — 기존 분야별 창은 동일 lane의 인스턴스로 재사용 | `CUSTOMER_WORKFLOW_MASTER.md` + `EMAIL_COLLECTION_COMMON_RULES.md` |
| TOOL007 | 고객 컨택 판단·전화 멘트·추천자료 | 금지 — 기존 7번 관련 대화창 재사용 | 중앙 고객업무 마스터 |
| TOOL001 | FULL/INTERMEDIATE 안내서 | 금지 — 기존 1번 관련 대화창 재사용 | 중앙 고객업무 마스터 |
| TOOL006 | TOC 정리·golden fixture | 금지 — 기존 6번/TOC 대화창 재사용 | 해당 중앙 규칙 |
| CRM_RESPONSE | 통화/회신 후 분기·다음행동 | 금지 — 기존 고객후속/CRM 대화창 재사용 | 중앙 고객업무 마스터 |

### EMAIL_COLLECTION 완전범용 잠금
- 방산/조선/배터리/반도체/로봇/AI/바이오/에너지 등 분야별 이메일 수집 대화창은 서로 다른 규칙체계가 아니다.
- 모두 하나의 `EMAIL_COLLECTION` lane이며 `EMAIL_COLLECTION_COMMON_RULES.md`를 단일 실행 원본으로 사용한다.
- 분야별로 허용되는 차이는 `분야코드·산업범위·탐색키워드·우선기관·분야고유 예외`뿐이다.
- 모든 고객은 분야 접두어가 포함된 영구 고객번호를 사용하며, 번호 없는 인력 출력은 FAIL이다.
- 기존 분야별 지시문이 중앙 범용 규칙과 충돌하면 이메일 수집 실행에서는 최신 `EMAIL_COLLECTION_COMMON_RULES.md`가 우선한다.
- 중앙 파일을 읽지 못하면 기존 대화창 기억이나 복사본으로 임의 fallback하지 않고 HOLD/FAIL한다.

## 3-A. MACHINE ROUTE MAP — 실행기가 읽는 기존 registry 내부 원본
아래 `route:` 행은 `feedback_pipeline/cross_chat_feedback_ingest.py`가 직접 읽는다. 새 라우팅 registry를 만들지 않는다.
형식: `route: TARGET = keyword | keyword | ...`

route: TOOL001 = 1번 | 안내서 | full_guide | intermediate_guide | 고객 자동화 안내서
route: TOOL002 = 2번 | 입찰 | 입찰 도구 | bid | tender
route: TOOL006 = 6번 | 목차 | toc | marketsandmarkets | marketandmarket
route: TOOL007 = 7번 | 고객 컨택 | 컨택 판단 | 전화 멘트 | 유선 멘트
route: TOOL013 = 13번 | 엑셀 자동 업로드 | 46145
route: TOOL037 = 37번 | 메타데이터 | 상품명 | 한글명 | isbn | code
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
1. 개발·관찰·통합 피드백·중앙 상태는 CONTROL_PRIMARY로 귀속한다.
2. Work 직전 준비·Work-only 판정·exact handoff는 WORK_PREP로 귀속한다.
3. 실제 전문업무는 기존 specialist lane을 재사용한다.
4. 분야별 이메일 수집 창은 모두 EMAIL_COLLECTION 동일 lane으로 취급하고 중앙 범용 규칙만 공유한다.
5. 새 feedback은 사용자가 여러 창에 반복 전달하지 않도록 중앙 GitHub에 event 단위로 흡수한다.
6. 중앙 규칙/fixture/error_hash/patch 반영 후 원래 lane의 다음 작업에 재사용한다.
7. 동일 오류/규칙은 새로운 대화창을 만들 이유가 되지 않는다.

## 5. DUPLICATE / LATER CHAT HANDLING
- 두 핵심 대화창과 목적이 겹치는 개발/관찰/상태보고/준비 계열 창은 기본적으로 `EVIDENCE_SOURCE_ONLY` / DELETE_CANDIDATE다.
- 삭제 전 고유 지시, 오류, fixture, 상태, restart point가 중앙 GitHub에 흡수됐는지 확인한다.
- 흡수/read-back 완료 후 중복 대화창을 active destination으로 사용하지 않는다.
- UI 삭제 자체를 assistant가 수행할 수 있다고 주장하지 않는다.

## 6. DELETION-SAFE RULE
- 삭제 대상 창의 내용이 중앙 GitHub에 이미 흡수되고 미처리 restart point가 없으면 삭제해도 운영 구조가 유지되도록 한다.
- 삭제 전에 사용자가 규칙을 다시 복사·비교·요약하게 하지 않는다.
- 새 작업창이 필요해지는 예외에도 핵심 지시·재시작점·계보를 GitHub에 먼저 등록하고 read-back 한다.

## 7. REPORTING CONSOLIDATION
- 개발 진행/관찰/통합 피드백은 CONTROL_PRIMARY에 모은다.
- Work 직전 준비와 handoff는 WORK_PREP에 모은다.
- 전문업무 산출물은 해당 전문 lane에서 출력한다.
- 같은 상태보고를 여러 대화창에 반복 게시하지 않는다.

## 8. USER BURDEN FAIL CONDITIONS
다음 발생 시 구조 FAIL이다.
- 사용자가 비슷한 대화창 중 어느 것을 써야 할지 매번 판단해야 함.
- 사용자가 같은 피드백을 여러 창에 복사해야 함.
- 같은 이메일 수집 업무가 분야별 창마다 다른 공통 규칙으로 생성됨.
- 고객번호가 없어 통합 DB에서 분야/고객을 구분하기 어려움.
- 이미 전달한 고객이 다른 창에서 신규로 다시 출력됨.
- 대화창 관리 때문에 실제 업무가 지연됨.

## 9. CURRENT DECISION
- 개발 핵심 2창은 유지한다.
- 이메일 수집은 기존 분야별 UI 창을 사용할 수 있으나 논리적으로는 단 하나의 `EMAIL_COLLECTION` lane이다.
- 범용 규칙은 `EMAIL_COLLECTION_COMMON_RULES.md` 한 곳에서만 갱신하고 분야별 복제본을 만들지 않는다.
- Work gate: Chat/GitHub/automation으로 처리 가능한 규칙 통합은 Work로 미루지 않는다.
