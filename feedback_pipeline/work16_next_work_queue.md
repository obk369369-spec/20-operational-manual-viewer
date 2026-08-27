# Work16 Next Work Queue

## OPEN candidate — cross-chat historical record auto-retrieval

- source: 16번 워크 이어서 하기 / TOOL002 lookup incident
- observed symptom: 2번 대화창이 TOOL002의 최근 자동화 논의 기록을 찾을 때 현재 대화/직접 보이는 기록만 보고 2026-03-16을 가장 직접적인 기록으로 판단했고, Library/GitHub에 보존된 다른 TOOL002 자료를 자동으로 먼저 조회하지 못함.
- user impact: 사용자가 다른 대화창에서 이미 논의한 내용을 다시 설명하거나, 어느 대화창에서 논의했는지 직접 찾아 전달해야 함.
- proposed root: GAP-CROSSCHAT-HISTORICAL-RECORD-AUTO-RETRIEVAL
- relation to existing roots: L4-12(master propagation) 및 L4-13(handoff)와 관련되지만 동일 root로 단정하지 말 것. 다음 Work 시작 시 기존 root/evidence와 dedup 판정 후 동일 원인이면 recurrence로 병합.
- required behavior: 도구번호/업무가 식별되면 현재 대화만 보지 말고 해당 TOOL의 GitHub master/checkpoint/handoff와 Library 보존 기록을 우선 검색하여 최근 관련 논의/마지막 작업지점을 회수. 사용자가 과거 내용을 복사해 다시 입력하게 하지 않음.
- PASS gate: TOOL002 대표 사례에서 현재 chat only 판정이 아니라 Library + GitHub records를 자동 회수하여 최신 관련 기록/마지막 작업지점을 재현하고, 다른 canonical TOOL 1건에서도 동일 경로가 재사용됨을 최소 fixture로 확인.
- constraints: 전 대화 전수조사 금지, 전체 Library 스캔 금지, 해당 TOOL 식별 후 scoped search만 수행, 기존 PASS는 SKIP-REUSE, DIFF ONLY, 정상 commit/push/read-back 후 checkpoint 갱신.
- status: CONSUMED_BY_L4-16 / REMOTE_VERIFIED / SKIP_REUSE

## NEXT WORK intake — unresolved recurrent feedback since prior Work

- user directive: 과거에 반복 지적했지만 실제 완료/최종 검증되지 않은 오류를 현재까지 누적된 OPEN/OPEN_CANDIDATE와 함께 다음 Work에 한 번에 투입한다. 사용자가 다시 오류를 열거하거나 과거 대화를 복사하지 않게 한다.
- source recovery: 중앙 master/root ledger/checkpoint/handoff/GitHub evidence + Library의 해당 TOOL 보존 기록에서 scoped retrieval한다. 현재 대화만 근거로 완료 여부를 판정하지 않는다.
- dedup rule: 실제 관측 오류(error)는 모두 회수하되 같은 root cause는 하나의 gap으로 병합하고 recurrence만 증가한다. VERIFIED_CLOSED/REMOTE_VERIFIED는 증거가 유효하면 SKIP-REUSE한다. 수정됐어도 최종 검증이 없으면 OPEN으로 유지한다.
- known recurrent tool groups to recover first: TOOL041/TOOL042 실제 고객업무 반복 피드백, TOOL006 TOC 고질 오류 및 HOLD-T6-PUBLISHER-GOLDEN-PAIR, TOOL013 다수 Excel/재개/중복/필드 누락·이동 계열, TOOL002 cross-chat historical record retrieval incident. 이 목록은 전체 범위를 제한하지 않으며 다른 WIC TOOL의 unresolved persistent feedback도 canonical owner별로 회수한다.
- cross-chat structural checks: 과거 내용을 사용자가 다시 붙여넣게 하는 문제, 현재 chat only 검색, source chat/tool identity 손실, target/central master 반영 누락, recurrence 미병합, checkpoint/handoff 누락, 임의 대화창 생성·재명명·요청 없는 예약 관련 과거 지적은 기존 root/evidence와 먼저 대조한다. 플랫폼 자체 UI 강제제어는 PLATFORM_LIMIT과 내부 실행가능 root를 분리한다.
- E2E completion gate: ACTUAL USER FEEDBACK → source/tool identify → latest target/central/checkpoint read → existing root/dedup/recurrence → DIFF ONLY fix → validator/output gate → minimal regression/E2E → normal commit/push → remote SHA/file read-back → state/checkpoint update. 중간 증거가 없으면 COMPLETE 금지.
- credit-safe: 전체 repo/Library/USB 전수 스캔 금지. tool/root 식별 후 scoped search, 대표 실제 사례 1~2개, 같은 root 묶음 수정, 영향 테스트 후 최종 gate 1회. 크레딧 소진 시 검증 완료분만 SAFE_CHECKPOINT로 보존하고 미완료는 OPEN 유지.
- next Work priority: P0 신규 OPEN/OPEN_CANDIDATE + 과거 unresolved recurrence 회수/dedup, P1 고객업무 BLOCKING/HIGH, P2 TOOL006/013 known-error residuals. 기존 PASS 재개발 금지.
- status: WORK_READY / MERGE_WITH_CURRENT_OPEN_BEFORE_EXECUTION

## CLOSED — TOOL002 institution accumulator

- root: `T2-RC-HEADER-ROW-INSTITUTION-ACCUMULATION-GAP`
- actual input: Narajangter workbook has metadata rows 1-4 and canonical headers at row 5 (`공고기관`, `수요기관`).
- failure: scoped USB candidate assumes `parsed[0]` is the header, so agency columns are missing and institution accumulation is invalid.
- target state: GitHub checkpoint `9946e7ba59ac812d7f27e287a6abd6b3aba3e2b9`; no current root `index.html`.
- completed: bounded header-row detection + actual-derived row-5 fixture + institution count/sum invariant; TOOL002 checkpoint `aa15d0bc9bcb73c434ff3badd2569bbc507392a0`, CI `32951474062`.
- completed runtime: canonical Web Worker actual 48,486-row XLSX E2E PASS; 48,481 deduped rows, 6,264 institutions, header row 5, sum invariant.
- target SAFE_CHECKPOINT: `b496e0f1a51e7c15aa578c5557ae5ac5c2b5fdaa`.
- status: REMOTE_VERIFIED_CLOSED / SKIP_REUSE

## CURRENT WORK_INPUT_OPEN_ROOTS

- `L6-20` — TOOL043 actual Android screen-off/background/state-change/persistent-sync/screen-on/state-restore evidence.
- NEXT_TRIGGER: `ACTUAL_ANDROID_SCREEN_OFF_BACKGROUND_RUN`.
- OPEN_INPUT_OMISSION: fail closed in `post_work_anomaly_audit.py`.
- USER_MANUAL_APPROVAL_COUNT: target `0`; platform-required maximum `1` per Work, after all executable SAFE work is batched first.
