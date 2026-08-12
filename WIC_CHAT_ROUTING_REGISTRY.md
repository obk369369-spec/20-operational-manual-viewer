# WIC CHAT ROUTING REGISTRY

상태: ACTIVE / NON-NORMATIVE ROUTING LEDGER
규범 원본: `WIC_GLOBAL_OPERATING_RULES.md`
목적: 유사 대화창 증가, 역할 중복, 이름 혼선, 사용자 피드백 부담 증가를 차단한다.

## 1. CHAT PROLIFERATION GUARD
- 기본값: `NO_NEW_CHAT`.
- 사용자가 명시적으로 새 대화창 분리를 요청하지 않는 한 새 역할/새 이름/새 준비창/새 관찰창을 만들거나 만들도록 유도하지 않는다.
- assistant는 ChatGPT UI의 대화창을 직접 생성·이름변경·삭제할 수 있다고 주장하지 않는다.
- 새 업무가 기존 역할과 겹치면 기존 허용 lane으로 라우팅한다.
- 어디에 넣을지 애매하면 새 창을 만들지 않고 아래 두 핵심 대화창 중 목적에 맞는 곳으로 처리한다.
- 이름이 비슷한 중복 대화창은 active destination으로 늘리지 않고 `EVIDENCE_SOURCE_ONLY`로 취급한다.
- 대화창 이름을 설명용 별칭으로 재정의하지 않는다. UI 실제 제목과 논리적 역할 ID를 분리한다.

## 2. CORE CHATS — 사용자 지정 2개만 유지
| chat_id | 실제 대화창 이름 | 역할 | 상태 |
|---|---|---|---|
| CONTROL_PRIMARY | `(개발 관찰자 모드 유지) 지피티 도구` | 전체 개발 관찰, 실질 도구 구현 방향, 중앙규칙, 상태, 피드백 흡수, 우선순위 통제 | KEEP / ACTIVE |
| WORK_PREP | `워크 전 준비` | Work 투입 전 Chat/Files/GitHub/일반 runtime에서 최대 준비, exact handoff, Work credit 절약, 재시작점 관리 | KEEP / ACTIVE |

- 위 두 대화창은 서로 대체하지 않는다.
- CONTROL_PRIMARY는 개발/관찰의 기준 창이고, WORK_PREP는 Work 직전 준비와 handoff 전용이다.
- 두 창의 공통 규칙·오류·fixture·restart point는 GitHub 중앙 마스터/ledger에 흡수해 서로 다시 설명하지 않게 한다.
- 목표: `ACTIVE_CORE_CHATS = 2`, `MANUAL_FEEDBACK_FORWARDING = 0`.

## 3. SPECIALIST LANES — 기존 창만 재사용
| lane_id | 역할 | 새 대화창 생성 여부 |
|---|---|---|
| EMAIL_COLLECTION | 분야별 신규/기존 고객 이메일 검증·DB | 금지 — 기존 분야별 대화창 재사용 |
| TOOL007 | 고객 컨택 판단·전화 멘트·추천자료 | 금지 — 기존 7번 관련 대화창 재사용 |
| TOOL001 | FULL/INTERMEDIATE 안내서 | 금지 — 기존 1번 관련 대화창 재사용 |
| TOOL006 | TOC 정리·golden fixture | 금지 — 기존 6번/TOC 대화창 재사용 |
| CRM_RESPONSE | 통화/회신 후 분기·다음행동 | 금지 — 기존 고객후속/CRM 대화창 재사용 |

새 개발/관찰/준비 대화창은 사용자가 명시적으로 분리 요청하기 전까지 만들지 않는다.

## 3-A. MACHINE ROUTE MAP — 실행기가 읽는 기존 registry 내부 원본
아래 `route:` 행은 `feedback_pipeline/cross_chat_feedback_ingest.py`가 직접 읽는다. 새 라우팅 registry를 만들지 않는다.
형식: `route: TARGET = keyword | keyword | ...`

route: TOOL001 = 1번 | 안내서 | full_guide | intermediate_guide | 고객 자동화 안내서
route: TOOL002 = 2번 | 입찰 | 입찰 도구 | bid | tender
route: TOOL006 = 6번 | 목차 | toc | marketsandmarkets | marketandmarket
route: TOOL007 = 7번 | 고객 컨택 | 컨택 판단 | 전화 멘트 | 유선 멘트
route: TOOL013 = 13번 | 엑셀 자동 업로드 | 46145
route: TOOL037 = 37번 | 메타데이터 | 상품명 | 한글명 | isbn | code
route: EMAIL_DB = 메일 수집 | 이메일 수집 | new_online | dormant_ledger | recent_trade | 고객 db
route: WORK_GATE = 워크 | work | 크레딧 | credit | 이관
route: CENTRAL = 중앙 마스터 | 깃허브 | github | 대화창 | 피드백 | 관찰자

운영 규칙:
- 실행 시 이 map을 우선 읽는다.
- registry가 없거나 파싱 실패하면 조용히 임의 fallback하지 않고 테스트/실행에서 FAIL 또는 HOLD 증거를 남긴다.
- route target 추가는 이 기존 파일을 수정하고 read-back/test한다.
- 규범 규칙의 우선순위나 내용은 이 map이 아니라 `WIC_GLOBAL_OPERATING_RULES.md`가 결정한다.

## 4. ROUTING RULE
1. 개발·관찰·통합 피드백·중앙 상태는 CONTROL_PRIMARY로 귀속한다.
2. Work 직전 준비·Work-only 판정·exact handoff는 WORK_PREP로 귀속한다.
3. 실제 전문업무는 기존 specialist lane을 재사용한다.
4. 새 feedback은 사용자가 전달하지 않는다. 접근 가능한 prior-interaction context에서 회수한다.
5. feedback은 전체 대화맥락을 합치지 않고 event 단위로 중앙 GitHub에 흡수한다.
6. 중앙 규칙/fixture/error_hash/patch 반영 후 원래 lane의 다음 작업에 재사용한다.
7. 동일 오류/규칙은 새로운 대화창을 만들 이유가 되지 않는다.

## 5. DUPLICATE / LATER CHAT HANDLING
- 2026-08-09 이후 두 핵심 대화창과 목적이 겹치게 생긴 개발/관찰/상태보고/준비 계열 대화창은 기본적으로 `EVIDENCE_SOURCE_ONLY` / DELETE_CANDIDATE다.
- 확인된 예시 제목: `WIC Stall Watchdog`, 화면에 `WIC status board updated and veri...`로 보였던 상태보고 계열 창. 제목이 잘린 경우 전체 이름을 추측하지 않는다.
- `WIC Overnight Completion`처럼 자동화/작업 명칭으로도 쓰인 이름은 UI 대화창인지 확인 전 삭제 대상 이름으로 단정하지 않는다.
- 삭제 전에 반드시 그 창의 고유 지시, 오류, fixture, 상태, restart point가 `WIC_GLOBAL_OPERATING_RULES.md`, `WIC_FEEDBACK_REGRESSION_AND_WORK_GATE_LEDGER.md`, 관련 tool repo, 또는 상태판에 흡수됐는지 확인한다.
- 흡수/read-back 완료 후에는 해당 중복 대화창을 더 이상 active destination으로 사용하지 않는다.
- assistant는 UI 삭제를 직접 수행할 수 없으므로 삭제는 사용자가 직접 할 수 있으나, 어떤 내용을 보존해야 하는지 다시 정리하게 요구하지 않는다.

## 6. DELETION-SAFE RULE
- 사용자가 삭제하려는 대화창의 내용이 중앙 GitHub에 이미 흡수되어 있고, 고유한 미처리 restart point가 없다면 삭제해도 운영 구조는 유지되도록 한다.
- 삭제 전에 사용자가 복사/붙여넣기, 비교, 요약, PASS/FAIL을 하게 하지 않는다.
- 삭제창 자동감지나 UI 전체 목록 접근을 가능한 것처럼 주장하지 않는다.
- 이후 새 작업창이 정말 필요해지는 예외가 있더라도 핵심 지시·재시작점·계보를 GitHub에 먼저 등록하고 read-back 한 뒤에만 검토한다. 기본값은 여전히 `NO_NEW_CHAT`다.

## 7. REPORTING CONSOLIDATION
- 개발 진행/관찰/통합 피드백 보고는 CONTROL_PRIMARY에 모은다.
- Work 직전 준비와 Work handoff 정보는 WORK_PREP에 모은다.
- 전문 업무 산출물은 해당 전문 lane에서만 출력한다.
- 같은 상태보고를 여러 대화창에 반복 게시하지 않는다.
- 자동화는 새 대화창 생성을 전제로 하지 않으며 GitHub 상태판과 위 두 핵심 창을 기준으로 한다.

## 8. USER BURDEN FAIL CONDITIONS
다음 발생 시 구조 FAIL로 기록한다.
- 사용자가 어느 비슷한 대화창을 써야 할지 매번 판단해야 함
- 사용자가 같은 피드백을 여러 대화창에 복사해야 함
- assistant가 새 준비창/관찰창/개발창을 계속 제안함
- 설명용 별칭 때문에 사용자가 원래 UI 제목을 찾지 못함
- 같은 업무 결과가 여러 창에서 서로 다른 규칙으로 생성됨
- 대화창 관리 때문에 실제 Tool1/Tool6/Tool7/고객DB 등 기능 구현이 지연됨

## 9. CURRENT DECISION — 2026-08-10
- 사용자 명시적 수정: `(개발 관찰자 모드 유지) 지피티 도구`와 `워크 전 준비` 두 기존 핵심 대화창은 모두 유지한다.
- 그 이후 생긴 유사 개발/관찰/상태/준비 대화창은 내용 보존 후 삭제 가능 구조로 정리한다.
- 분류: `CONSTRAINT + STRUCTURE_CORRECTION + PRIORITY_RESTORE`.
- 최우선 목적은 대화창 관리가 아니라 실제 도구 기능 구현이다.
- 조치: `NO_NEW_CHAT` 유지, 핵심 2창 잠금, 중복창 evidence-only/delete-candidate, 피드백 자동수집, GitHub 중심 재사용.
- Work gate: `WORK_DEFER_DENIED` — Chat/GitHub/automation으로 처리 가능.
