# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 15:40 KST
상태: ACTIVE — 각 대화창 피드백 자동수집→중앙 마스터→GitHub 반영 파이프라인 구현/실행 시작

규범 원본은 `WIC_GLOBAL_OPERATING_RULES.md`. 이 파일은 외부 증거와 재시작점만 기록한다. 37번=metadata production/integrated verification, 13번=Excel automatic upload로 분리 유지.

## 현재 최우선
- P0~P5 실제 사무실 고객응대 업무 우선은 유지.
- 이번 사용자 지시는 `CONSTRAINT`로 흡수: 각 대화창의 WIC 피드백을 사용자가 다시 전달하지 않게 자동수집/중앙흡수한다.
- 대화창 전체 문맥을 서로 합치지 않고 피드백 이벤트만 중앙에 승격한다. 명시적 `PRIORITY_CHANGE`가 아니면 기존 우선순위를 바꾸지 않는다.

## Cross-chat feedback pipeline 실제 구현
| 구성 | 상태 | 증거 |
|---|---|---|
| deterministic ingest core | 저장 PASS | `feedback_pipeline/cross_chat_feedback_ingest.py` |
| Korean prohibition classification fix | 저장 PASS | commit `2b5db963f1d18ab6ba0b378dbc8a057a21558750` |
| ordinary runtime regression | PASS | `PASS: 11 deterministic cross-chat feedback fixtures` |
| cursor/dedupe state | 저장/read-back PASS | `feedback_pipeline/state.json`, blob `cc2bc0360b2e5168e3c3501ebc7b290922622321` |
| CI audit workflow | 저장/read-back PASS | `.github/workflows/cross-chat-feedback-audit.yml`, blob `18825b81cf039eb0162eed2662a33fb72db8fedf` |
| runtime collector | ACTIVE | `WIC 대화창 피드백 수집`, 매시 :20 KST |
| user manual forwarding | 제거 | collector가 accessible prior-interaction/personal-context delta를 직접 회수 |

## 파이프라인
`prior-interaction delta -> sanitize -> classify -> route -> semantic feedback_id dedupe -> central-master candidate / fixture candidate -> actual patch/test -> GitHub read-back -> state cursor advance`

분류:
- `CORRECTION`
- `CONSTRAINT`
- `NEW_FIXTURE`
- `PRIORITY_CHANGE`
- `SIDE_REQUEST`

도구 라우팅 초기 범위:
- TOOL001 안내서
- TOOL006 TOC
- TOOL007 고객 컨택
- TOOL013 Excel upload
- TOOL037 metadata
- EMAIL_DB
- WORK_GATE
- CENTRAL

## 개인정보/기밀 게이트
- raw customer PII, private contract text, confidential transaction content는 중앙 피드백 로그에 저장 금지.
- 이메일/전화/긴 식별번호는 redaction 후 규칙 수준 excerpt/hash/reference만 저장.

## Work/크레딧 게이트
- Chat/Files 가능 -> `WORK_DEFER_DENIED`.
- GitHub 가능 -> `WORK_DEFER_DENIED`.
- ordinary terminal/runtime 가능 -> `WORK_DEFER_DENIED`.
- 위 3개 모두 불가 + concrete Work-only blocker + exact handoff package일 때만 `WORK_ELIGIBLE`.
- 과거대화 재독해/규칙정리/터미널 가능한 테스트를 Work로 보내면 `CREDIT_WASTE_FAIL`.

## 검증 중 발견 및 즉시 수정
첫 ordinary-runtime fixture에서 `터미널에서 가능한 일은 Work로 넘기지 마`가 `SIDE_REQUEST`로 오분류되는 오류 발견.
- 원인: 금지 표현 탐지가 `하지 마`에 치우쳐 `지 마/말고`를 놓침.
- 수정: Korean prohibition tokens에 `하지 말/하지말/지 마/지마/말고` 추가.
- 수정 후 regression: `PASS: 11 deterministic cross-chat feedback fixtures`.
- 사용자 재테스트 요구 없음.

## 아직 HOLD인 부분
- **Cross-chat E2E 증명:** 현재 코드/스케줄/상태/회귀검증은 실제 구현됨. 그러나 별도의 다른 대화창에서 새 WIC 피드백이 발생한 뒤 collector가 그것을 자동 회수→dedupe→GitHub 반영한 첫 실사례는 아직 발생 전이므로 E2E는 HOLD.
- CI workflow의 실제 Actions run 결과는 현재 별도 확인 증거가 아직 없음. workflow 파일 저장/read-back은 PASS, CI 실행 PASS는 미판정.

## 기존 고객응대 개발 상태 유지
- P1 customer DB/send-order: fixture PASS 범위 유지.
- P2 Tool7: fixture PASS 범위 유지.
- P1->P2 handoff: fixture PASS 범위 유지.
- P3 Tool1 historical contract: fixture PASS 범위 유지.
- Tool1 actual customer/report rendered guide E2E: HOLD.

## 정확한 재시작점
1. Cross-chat collector: 다음 :20 회차에서 `feedback_pipeline/state.json:last_context_cursor` 이후 새 WIC 피드백만 회수. 새 피드백이 있으면 자동으로 중앙/관련 도구 반영 후 cursor advance.
2. P0~P5 고객응대 실무 차단사항이 있으면 그 작업이 background ingestion보다 우선.
3. P3 Tool1: real customer + real tradable report 승인 fixture 회수 -> stable mapper actual DOM/slot -> rendered output -> expected 비교.
4. P4 TOC 필요 시 publisher golden fixture 적용 후 P3 복귀.

사용자 역할: 관찰자. 대화창 피드백 수동 전달, 과거 오류 재설명, 동일 파일 재전송, 반복 테스트, PASS/FAIL 판정, 규칙 정리, Work 이관 판단을 요구하지 않는다.
