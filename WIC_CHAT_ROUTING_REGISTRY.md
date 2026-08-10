# WIC CHAT ROUTING REGISTRY

상태: ACTIVE / NON-NORMATIVE ROUTING LEDGER
규범 원본: `WIC_GLOBAL_OPERATING_RULES.md`
목적: 유사 대화창 증가, 역할 중복, 이름 혼선, 사용자 피드백 부담 증가를 차단한다.

## 1. CHAT PROLIFERATION GUARD
- 기본값: `NO_NEW_CHAT`.
- 사용자가 명시적으로 새 대화창 분리를 요청하지 않는 한 새 역할/새 이름/새 준비창/새 관찰창을 만들거나 만들도록 유도하지 않는다.
- assistant는 ChatGPT UI의 대화창을 직접 생성·이름변경·삭제할 수 있다고 주장하지 않는다.
- 새 업무가 기존 역할과 겹치면 기존 허용 lane으로 라우팅한다.
- 어디에 넣을지 애매하면 새 창을 만들지 않고 `CONTROL` lane에서 처리한다.
- 이름이 비슷한 중복 대화창은 active destination으로 늘리지 않고 `EVIDENCE_SOURCE_ONLY`로 취급한다.
- 대화창 이름을 설명용 별칭으로 재정의하지 않는다. UI 실제 제목과 논리적 역할 ID를 분리한다.

## 2. ACTIVE LANES — 최대 허용 구조
| lane_id | 역할 | 새 대화창 생성 여부 |
|---|---|---|
| CONTROL | 전체 개발 관찰, Work 전 준비, 중앙규칙, 상태, 피드백 흡수, 우선순위 통제 | 금지 — 현재 기준 대화창 사용 |
| EMAIL_COLLECTION | 분야별 신규/기존 고객 이메일 검증·DB | 금지 — 기존 분야별 대화창 재사용 |
| TOOL007 | 고객 컨택 판단·전화 멘트·추천자료 | 금지 — 기존 7번 관련 대화창 재사용 |
| TOOL001 | FULL/INTERMEDIATE 안내서 | 금지 — 기존 1번 관련 대화창 재사용 |
| TOOL006 | TOC 정리·golden fixture | 금지 — 기존 6번/TOC 대화창 재사용 |
| CRM_RESPONSE | 통화/회신 후 분기·다음행동 | 금지 — 기존 고객후속/CRM 대화창 재사용 |

위 6 lane 외 새 개발/관찰/준비 대화창은 사용자가 명시적으로 분리 요청하기 전까지 만들지 않는다.

## 3. ROUTING RULE
1. 사용자의 현재 요청을 lane으로 분류한다.
2. 기존 lane이 있으면 그 lane의 기존 대화창/자료를 재사용한다.
3. 새 feedback은 사용자가 전달하지 않는다. `WIC 대화창 피드백 수집`이 접근 가능한 prior-interaction context에서 회수한다.
4. feedback은 전체 대화맥락을 합치지 않고 `event` 단위로 중앙 GitHub에 흡수한다.
5. 중앙 규칙/fixture/error_hash/patch 반영 후 원래 lane의 다음 작업에 재사용한다.
6. 동일 오류/규칙은 두 번째 대화창을 만들 이유가 되지 않는다.

## 4. DUPLICATE CHAT HANDLING
- 유사한 목적의 기존 대화창이 여러 개 발견되면 하나를 새로 합치거나 이름변경하지 않는다.
- 최신 업무에 실제 사용 중인 1개만 `ACTIVE_DESTINATION`으로 지정하고, 나머지는 `EVIDENCE_SOURCE_ONLY`로 둔다.
- 사용자가 기존 제목을 기억해 찾고 있으면 임의 별칭으로 바꾸지 않는다.
- 어느 창이 active인지 확정 증거가 없으면 UI 제목을 추측하지 않고 CONTROL에서 업무를 계속한다.

## 5. REPORTING CONSOLIDATION
- 개발 진행/관찰/Work gate/피드백 흡수 보고는 CONTROL 한 곳에만 모은다.
- 전문 업무 산출물은 해당 전문 lane에서만 출력한다.
- 같은 상태보고를 여러 대화창에 반복 게시하지 않는다.
- 자동화는 새 대화창 생성을 전제로 하지 않으며 GitHub 상태판과 CONTROL 보고를 기준으로 한다.

## 6. USER BURDEN FAIL CONDITIONS
다음 발생 시 구조 FAIL로 기록한다.
- 사용자가 어느 비슷한 대화창을 써야 할지 매번 판단해야 함
- 사용자가 같은 피드백을 여러 대화창에 복사해야 함
- assistant가 새 준비창/관찰창/개발창을 계속 제안함
- 설명용 별칭 때문에 사용자가 원래 UI 제목을 찾지 못함
- 같은 업무 결과가 여러 창에서 서로 다른 규칙으로 생성됨

목표: `ACTIVE_CONTROL_CHATS = 1`, 전문 lane은 기존 창 재사용, `MANUAL_FEEDBACK_FORWARDING = 0`.

## 7. CURRENT DECISION — 2026-08-10
- 사용자 피드백: 대화창이 많아져 오히려 피드백 부담이 증가함.
- 분류: `CONSTRAINT + STRUCTURE_CORRECTION`.
- 조치: `NO_NEW_CHAT` 기본값, CONTROL 단일화, 전문 lane 제한, 중복창 evidence-only, 피드백 자동수집 유지.
- Work gate: `WORK_DEFER_DENIED` — Chat/GitHub/automation으로 처리 가능.
