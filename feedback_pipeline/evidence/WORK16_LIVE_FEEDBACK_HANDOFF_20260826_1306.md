# WORK16 LIVE FEEDBACK HANDOFF — 2026-08-26 13:06 KST

Status: WORK_READY_EVIDENCE / NON-NORMATIVE
Scope: `모든 WIC 대화창의 지속 피드백 즉시반영 E2E 실제 완성`
Purpose: ordinary Chat에서 현재까지 확인된 실제 사용자 피드백·재발·구조 gap을 다음 Work 실행이 재검색/재질문 없이 바로 소비하도록 누적 보존한다.

## 0. 최우선 운영 원칙
- 사용자 역할은 OBSERVER ONLY. WIC 통제 범위의 route/merge/retry/operator 역할을 사용자에게 넘기지 않는다.
- 단일 목표는 persistent feedback E2E 하나다. 41/42/6은 이 단일 E2E의 대표 실제 회귀 사례다.
- 과거 PASS/FINAL/fixture/self-test/README는 최신 실제 사용자 관찰보다 우선하지 않는다.
- 실제 사용자 경로/실제 runtime/output > independent validator > remote read-back > checkpoint/state > 과거 fixture/PASS.
- 동일 root의 재발은 새 root로 중복 집계하지 말고 recurrence 증가.
- force push, reset --hard, history rewrite, 대량 삭제/덮어쓰기 금지.
- 승인 묶음: (1) 읽기·clone·검색·검증 SAFE BATCH 1회, (2) DIFF ONLY 수정·테스트·정상 commit 가능한 1회 SAFE BATCH, (3) 정상 push·최종 fetch·remote SHA/file read-back SAFE BATCH 1회. 검증 품질/체크포인트 안전성 유지.
- push race 발생 시 반복 merge/rebase/retry loop 금지. 정확한 HOLD 또는 remote-preserving non-merge reconcile만 증거와 함께 사용.
- Work 최종보고 수치는 machine evidence에서 계산하고 손으로 요약 숫자를 만들지 않는다.

## 1. 현재 층별 ZERO 목표
오류(error)=개별 실패/증상/재발 사건. 구멍(hole/gap)=같은 root cause 중복 제거한 구조 결함.
최종 목표는 오류 수가 아니라 각 층의 OPEN_HOLES=0.
- L1_CLOUD_CONTROL: 현재 감사에서 명시 OPEN root 8개 pending revalidation.
- L2_AUTOMATION_WATCHDOG: 현재 감사에서 명시 OPEN root 2개.
- L3_USB_RUNTIME_KNOWN: UNKNOWN, 최소 1개 이상 확인됨. UNKNOWN을 0으로 세지 말 것.
- L4_WORK_LOCAL_PENDING: UNKNOWN. Work/local 직접검증 전 0 처리 금지.
전체 ZERO = L1=0 AND L2=0 AND L3=0 AND L4=0 AND UNKNOWN_CRITICAL=0 AND NEW_HOLES=0 연속 2회.

## 2. 현재 명시 OPEN root — ordinary Chat audit pending
다음은 현재 전수감사에서 아직 VERIFIED_CLOSED로 인정하지 않은 root ID다. Work에서 이미 수정한 항목과 겹치면 recurrence/closed evidence로 대조하고 새 root를 만들지 않는다.
### L1
1. GAP-TARGET07-NO-CI-WORKFLOW
2. GAP-STALL-AUTH-NONEMPTY-BYPASS
3. GAP-STALL-ACTIVITY-STATUS-SUBSTRING
4. GAP-WORK-GATE-MISSING-GATES-AS-FALSE
5. GAP-WORK-HANDOFF-VACUOUS-ZERO-ELIGIBLE-PASS
6. GAP-AUTH-CURRENTCHAT-NEGATION-FALLTHROUGH
7. GAP-FINAL-REPORT-CHECKPOINT-STATE-MISMATCH
8. GAP-FINAL-REPORT-GAP-COUNT-MISMATCH
### L2
9. GAP-WORK-EXIT-PLACEHOLDER-RESUMABLE
10. GAP-AUTOMATION-BOTH-DISABLED

## 3. 최신 final-report/state 불일치
- Work 최종보고: 발견 고유 오류 13 / 수정 13 / 검증 13.
- machine attack evidence: unique_gap_count=14 / fixed_or_verified_count=14 / open_internal_gaps=[] / zero_new_gap_streak=2.
- 따라서 final report 숫자 13↔14 불일치 root를 닫기 전 FINAL PASS 금지.
- Work 최종보고: Remote read-back=PASS.
- 최신 확인 state: `persistent_feedback_e2e_20260826.checkpoint_status=REMOTE_READBACK_REQUIRED_FOR_COMPLETE`.
- 따라서 read-back 실제 증거와 state producer가 모순. 단순 문자열 COMPLETE 변경 금지. producer→write→push→latest main read-back→CI로 실제 폐쇄.

## 4. 최신 main 이동에 대한 규칙
- Work가 완료했던 `bfcb9c33dd2b8e790072f2c19f44ba0d6ca70b00` 이후 중앙 main이 계속 전진했다.
- 2026-08-26 13:06 KST ordinary Chat 확인 시 main=`7b94209fc52c03fc629a9fc7d8d66b44e0657d7b`.
- 그 SHA는 확인 시점 push workflow run 0건이었다. 이것은 새 root 확정 전 candidate recurrence로 취급하며, dedup 후 분류.
- Work 시작 시 반드시 latest main을 다시 읽고 이 파일의 SHA를 고정값으로 신뢰하지 말 것.

## 5. Chat handoff / 대화창 이동 피드백
- 사용자가 `옮겨`라고 하면 source chat identity, persistent feedback, completed/open/HOLD, last verified, restart point, decisions/rules/gates, checkpoint, commit/push/readback/SHA를 먼저 보존.
- `옮겨`는 새 ChatGPT 대화창 생성/재명명 권한이 아니다.
- ChatGPT UI 새 대화창 생성·제목 제어 API는 `EXTERNAL_PLATFORM_LIMIT`로 별도 유지. WIC 내부 handoff persistence는 실제 PASS여야 함.
- 대화창 이동 가능 조건: 최신 main Cross-chat audit SUCCESS + handoff internal gaps 0 + state checkpoint 실제 REMOTE_VERIFIED/COMPLETE + latest evidence read-back + zero_new_gap_streak>=2.
- 조건 충족 전 `이동 완료`/`옮겨도 됨`을 과장하지 말 것.

## 6. 일반 Chat ingress 경계
- ordinary ChatGPT 대화 자체에 repository webhook/interceptor를 삽입할 수 있는 확인된 API가 없으면 `EXTERNAL_PLATFORM_LIMIT` 유지.
- 그러나 WIC gateway 안에서는 user manual routing=0을 목표로 하며, 사용자가 각 피드백을 수동 분배하게 만들지 않는다.
- source chat identity를 keyword routing보다 먼저 확정.

## 7. TOOL042 실제 피드백 회귀 묶음
이 항목들은 세 개 별도 프로젝트가 아니라 persistent feedback E2E의 실제 regression case다.
- 실제 고객 사례에서 보고서가 2종만 출력된 오류. 해당 사례는 3종이 필요했다.
- 이후 일반 규칙은 exact-3 고정이 아니라 customer/context에 따라 3/4/N종 가능. `expected.required_report_count` 또는 `expected.reports.length` 기준으로 검증하고 정확히 필요한 수를 출력.
- 추천 보고서는 서로 실제 거래 가능한 distinct publisher로 구성. publisher duplicate/mix/fallback 혼동 금지.
- 추천 2 TOC가 중간에서 잘린 실제 오류. 최소 실제 확인 사례에서 `16.10 List of abbreviations`까지 존재. 시작/중간/최종 item과 truncation 검사.
- copy output은 번호 포함. 예: `16.10 List of abbreviations`에서 번호가 clipboard/copy 결과에 빠지면 FAIL.
- 기존 root 계열: CUSTOMER-BRANCH / REPORT-COUNT / PUBLISHER-DIVERSITY / TOC-COMPLETENESS / COPY-FORMAT.
- 최신 실제 N-report feedback이 과거 exact-3 문구보다 우선. 단, 과거 3종 실제 회귀 케이스는 regression fixture로 유지.

## 8. TOOL006 실제 피드백 회귀 묶음
- 발행사 구분을 사용자가 반복 지적. profile/detection/rules가 실제 engine/output에 영향을 줘야 하며 empty publisher_profiles/pass 금지.
- 투입타이밍/추가횟수 오류가 실제 사용자 지적으로 존재. 정확한 숫자/예시는 저장된 원문 evidence에서 회수. 찾지 못하면 `SOURCE_EVIDENCE_HOLD`; 숫자를 새로 만들지 말 것.
- 각 구간의 `위로가기` 버튼이 사라지거나 비기능인 실제 오류. present/visible/clickable/not-overlaid/correct scroll target/focus/caret/scroll behavior 실제 확인.
- 실제 고객 경로: raw TOC → publisher distinction → organization → tree/output → copy/navigation.
- GitHub latest와 실제 USB/browser runtime이 달랐던 증거. 알려진 사용자 실제 파일 경로는 과거 `I:\GPT 도구 작업\6번 목차 정리 도구 (워크 작업)\toc_lock_v2_26_v10_실제본체반영_HOLD.html`; drive letter는 고정하지 말고 fingerprint로 실제 USB root 찾기.
- static HTML JS / `tool006_engine.ps1` / `tool006_ui.ps1` 등 dual-engine divergence 조사. 실제 production entrypoint를 식별.
- launcher/VBS/PS1/generator/copier/upstream sync/browser cache/profile/local/session storage/old clone/backup/temp가 최신 파일을 다시 stale로 덮어쓰는지 확인.
- stale runtime RED 재현 → 같은 사용자 경로 GREEN → fresh reopen/reconnect/process/relaunch 후에도 같은 entrypoint 최신 유지.
- known external evidence required는 publisher_identity raw→wrong→user-approved expected pair 및 verified insertion timing/additional count. 실제 source 없이는 완료 과장 금지.

## 9. TOOL041 실제 피드백 회귀 묶음
- 최신 실제 사용자 피드백은 과거 PASS를 reopen할 수 있다.
- known core roots: `DATA-INTEGRITY`, `CONTACT-OUTPUT-QUALITY`.
- exact latest user feedback wording/detail은 canonical feedback/master/checkpoint에서 source evidence 회수. ordinary Chat에서 확인되지 않은 세부를 임의 생성하지 말 것.
- same root면 recurrence 증가. validator PASS였는데 actual output이 실패했다면 validator coverage 부족으로 판단.
- representative actual customer/contact input → latest TOOL041 master → real output → independent validator/output gate.
- broad redevelopment 금지. 해당 root만 DIFF ONLY.
- target commit/push/remote SHA+file read-back → central sync → next-run reuse까지 확인.

## 10. 기타 WIC 공통 누적 피드백
- 대화창/도구 이름을 임의 생성·재명명하지 말 것. UI title이 불확실하면 `UI_TITLE_HOLD`.
- 중앙 master와 개별 target master ownership 혼합 금지. 공통 rule만 CENTRAL, tool-specific rule은 target/domain override.
- 삭제된 옛 42 chat을 재생성/alias/merge/re-register하지 말 것.
- TOOL013은 신규 실제 오류가 없으면 기존 PASS 영역 재작업 금지. 01~32 fixed representative gate를 SKIP-REUSE.
- TOOL001은 dependency stabilization HOLD 범위를 broad dev로 재개하지 말 것.
- TOOL002/007/027/043은 이 단일 E2E를 증명하는 데 필요한 최소 actual-path verification 외 broad dev 금지.
- fail-fast 유지. fixture를 약화하거나 test를 바꿔 PASS 만들기 금지.
- production `assert` 의존 금지, empty target/all-skipped/vacuous PASS 금지, symbolic SHA 금지, evidence ref dereference, unrelated diff를 material change로 인정 금지.
- auto merge/rebase와 `[skip ci]` 우회 금지.
- subprocess/network timeout 유지.
- partial cross-repo transaction은 COMPLETE 금지.
- checkpoint를 무시한 반복작업/rediscovery 금지.
- self-heartbeat/self-report를 독립 증거로 쓰지 말 것.

## 11. 승인/credit 효율
- 이미 성공한 read/search/test는 SKIP-REUSE.
- 동일 조회/gh run list/repo recursive scan 반복 금지.
- retry loop 대신 1회 relevant attempt 후 정확한 HOLD.
- 긴 Work 세션에서 중앙 구조 전체를 재개발하지 말고 현재 OPEN root/새 evidence만 처리.

## 12. Work가 다음에 해야 할 일
1. latest main/target refs를 1회 SAFE BATCH로 읽고 이 handoff와 canonical state/ledger를 대조.
2. 위 10개 audit OPEN root를 Work 내부 14 fixed root와 dedup. 이미 실제로 닫힌 것은 exact evidence로 VERIFIED_CLOSED; 남은 것만 patch.
3. final-report 13↔14와 checkpoint REMOTE_READBACK_REQUIRED 모순부터 producer 기준으로 닫기.
4. 최신 main에서 CI registration/coverage가 change type에 맞게 동작하는지 확인. unrelated content commit에 workflow run이 필요 없는 설계라면 그 근거를 machine state에 명시하고 false gap을 닫기; 필요한 commit인데 run이 없으면 root를 수정.
5. TOOL041/042/006 actual regression evidence를 정확히 대조. source 없는 세부는 HOLD, 임의 생성 금지.
6. L3/L4는 실제 USB/local entrypoint를 직접 읽을 수 있을 때만 0 판정.
7. 최종 보고는 오류 수와 구멍 수를 분리하고 층별 `found/closed/open/new`를 machine evidence에서 출력.

## 13. 완료 기준
- L1/L2/L3/L4 각각 OPEN_HOLES=0.
- UNKNOWN_CRITICAL=0.
- 동일 공격 범위에서 NEW_HOLES=0 연속 2회.
- actual runtime/output + independent validator + remote read-back + next-run latest-master reuse.
- 플랫폼 한계 2건은 별도 `PLATFORM_LIMIT`로 남길 수 있으나 내부 PASS로 위장 금지.
- docs/code/fixture/self-test/ACK만으로 COMPLETE 금지.

## 14. Source completeness note
이 파일은 ordinary Chat에서 현재 확인 가능한 사용자 대화 맥락, 중앙 상태, GitHub evidence, 회수된 WIC 관련 과거 자료를 합친 즉시 handoff다. 모든 과거 대화 원문 전체를 완전히 회수했다고 주장하지 않는다. source가 확인되지 않은 feedback은 `SOURCE_EVIDENCE_HOLD`로 두고, 이미 기록된 원문이 있으면 사용자에게 다시 설명/재입력을 요구하지 말고 먼저 회수한다.
