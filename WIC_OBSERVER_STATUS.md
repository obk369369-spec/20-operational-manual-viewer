# WIC OBSERVER STATUS

최종 갱신: 2026-08-14 00:12 KST
상태: ACTIVE / STRUCTURE_FIRST / PRE_WORK_PREFLIGHT
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 사용자 보고 형식 LOCK
- 모든 진행상황 보고는 기본적으로 Markdown 테이블 표로 구분해서 표시한다.
- 최소 열은 `구분 / 작업 / 상태 / 근거 / 다음 작업`으로 한다.
- 필요 시 `Work 크레딧 필요 여부 / 우선순위 / blocker / 재개지점` 열을 추가한다.
- 실제 실행 완료 / 진행 중 / HOLD / 아직 실행하지 않음을 명확히 분리한다.

## 운영준비도
| 구분 | 상태 | 근거 | 다음 작업 |
|---|---|---|---|
| 기존 안티그래비티 추출본 | 재사용 LOCK | 기존 RULE_PACKET/STATE_PACKET 계열은 재추출 금지 | 이후 누적 규칙만 차분 통합 |
| integration core 재구축 | 반복 금지 | 기존 구현/fixtures 존재 | 완료 단계 재실행 금지 |
| 실제 새 feedback canonical E2E | 실제 실행 완료 | feedback `37a4a2166bb5e2a08a8c`, run `31670039251`, job `94352602812`, conclusion `success` | 반복 금지 |
| 중앙 GitHub write/read-back | 실제 실행 완료 | canonical commit `59f388df9601503cd205885f6fa4e839aacd9f03`, revision `3f0c83fe635a4067354e8456`, hash read-back verified | 반복 금지 |
| 승인 없는 구조변경 사전차단 guard | 실제 fixture PASS | run `31712529019`의 `Deny structural changes without explicit user-directive provenance` step success | 전체 WIC material change 공통 preflight로 확대 |
| 대상 저장소 apply/read-back/test | HOLD | 교차 저장소 실제 통로 검증 필요 | Chat/GitHub에서 가능한 준비 종료 후 Work-only 여부 판정 |
| 구조 최종 PASS | 아직 아님 | Work 전 준비 체크 미완료 항목 존재 | 아래 PRE-WORK CHECKLIST를 모두 닫거나 WORK_ONLY_HOLD로 고정 |
| 제3자 독립검증 | 없음 | external independent run/result 증거 없음 | 내부 GitHub E2E와 분리 유지 |

## 사용자 지시 대조 최상위 게이트 — USER DIRECTIVE PROVENANCE GUARD
- WIC의 모든 대화창·도구·규칙·자동화·GitHub 구조에서 **새 구조/새 기능/기능변경/규칙변경/우선순위변경/대화창 생성·이름변경·자동이전/새 registry/새 파일구조 등 중요한 변경**은 실행 전에 사용자 지시 기록과 대조한다.
- 사용자의 실제 지시 원문 또는 이미 승인된 중앙 운영규칙에서 근거를 찾지 못하면 `STRUCTURAL_ERROR_UNAUTHORIZED` 또는 `UNAUTHORIZED_CHANGE`로 분류하고 먼저 `DENY_HOLD`한다.
- DENY된 변경은 정상 구조로 승계하거나 다음 작업의 전제로 사용하지 않는다.
- DENY 발생 시 관찰자인 사용자에게 `무엇을 막았는지 / 왜 사용자 지시와 불일치했는지 / 어떤 작업에는 영향이 없는지`를 보고한다.
- 단순 업무 실행처럼 기존 승인 규칙 안에서 데이터만 처리하는 것은 새 구조 변경으로 보지 않는다. **구조·규칙·기능·자동화 방식이 달라지는 material mutation만** 이 게이트의 대상이다.
- 기존 사용자가 명시한 금지/제외 지시는 승인으로 해석하지 않는다.
- 승인 근거가 애매하면 추정하여 실행하지 않고 HOLD한다.
- 동일 유형이 실제 1회 발생하면 회귀테스트로 승격한다.

## 구조적 오류 감지 게이트 — 현재 실제 적용 범위
| 대상 | 현재 상태 | 실제 근거 | 남은 작업 |
|---|---|---|---|
| 새 대화창 생성 | DENY fixture PASS | `unauthorized_structure_guard.py`, run `31712529019` guard step success | 실제 operation preflight 호출지점 확대 |
| 대화창 이름 변경 | DENY fixture PASS | negative rename fixture | 동일 |
| 새 registry 생성 | DENY fixture PASS | negative registry fixture | 동일 |
| 사용자 기록에 없는 구조 생성 | DENY fixture PASS | not-in-record fixture | 동일 |
| 전체 feedback pipeline 선행 게이트 | 연결됨 | `.github/workflows/cross-chat-feedback-audit.yml`에서 integration audit 전 guard 실행 | 전체 run 최종 state validation 별도 정리 |
| 모든 개별 도구 저장소의 직접 mutation | 부분 적용 | 중앙 규칙 포인터/target 구조 사용 | 공통 adapter 호출 규격으로 연결 필요 |
| 모든 대화창의 실제 ChatGPT 앱 레벨 생성/rename | 직접 실행 제어 불가 | GitHub guard는 WIC 운영구조 승인 여부 판정 가능 | 미승인 사건 감지 시 DENY 보고, 앱 객체 삭제는 사용자 권한 범위 |

## DENY 관찰자 보고 규칙
- `DENY_HOLD`가 발생하면 다음 사용자 보고에 반드시 포함한다.
  - 차단 대상 action/target
  - 사용자 승인 근거를 찾지 못한 이유
  - `STRUCTURAL_ERROR_UNAUTHORIZED` 여부
  - 실제 변경이 실행되기 전에 막혔는지 여부
  - 이미 생성된 GitHub 자산이면 rollback/delete/read-back 결과
- DENY를 조용히 삼키지 않는다.
- DENY된 것을 실패한 정상 기능처럼 수정해서 살리지 않는다. 사용자 지시가 없었던 구조 자체라면 제거/미승계가 기본이다.

## 현재 실제 개선
| 작업 | 상태 | 실제 증거 |
|---|---|---|
| 승인 없는 구조 변경 guard 최초 구현 | 완료 | `feedback_pipeline/unauthorized_structure_guard.py` |
| guard를 중앙 audit 첫 단계로 연결 | 완료 | workflow commit `6abddab1031bc3e8537f1cc358eb0c1c607785c6` |
| fixture 오류 수정 | 완료 | commit `ab5f1b558ee2859a71791fbfc744729415b2d13d` |
| 수정 후 guard step | PASS | run `31712529019`, step `Deny structural changes without explicit user-directive provenance` success |
| 기존 integration 단계 | PASS 유지 | 동일 run에서 integration core/rollback/restart/lane ACK 단계 success |
| 전체 run final state validation | HOLD/FAIL | 동일 run 마지막 `Validate collector and integration-core state` failure | 원인만 분리 수정, 이미 PASS한 guard/core는 반복 금지 |
| evidence artifact | 생성 완료 | artifact `9185853930` |

## PRE-WORK CHECKLIST — Work 진입 전 반드시 확인
| 체크항목 | 상태 | Work 전 목표 |
|---|---|---|
| 사용자 지시 출처 없는 구조/규칙/기능 변경 DENY | PASS fixture / 범용연결 진행중 | 모든 material mutation의 공통 preflight 계약 고정 |
| DENY 시 관찰자 보고 | 규칙 고정 | evidence/ledger에서 다음 보고에 자동 포함되는 계약 고정 |
| Chat 피드백 → conflict/dedup → canonical write/read-back | PASS 증거 있음 | 반복 금지 |
| revision cache / SKIP_UNCHANGED | PASS 증거 있음 | 반복 금지 |
| checkpoint / restart / rollback | PASS 증거 있음 | 반복 금지 |
| 공통 module/adapter 계약 | 기반 있음 | 새 도구 기능 변경이 같은 계약을 사용하도록 범용 적용점 고정 |
| Chat에서 기능수정 → 테스트 → rollback | 부분 완료 | Work 없이 가능한 범위를 최대화하고 Work-only blocker만 남기기 |
| Work 종료 시 handoff | 준비 필요 | 마지막 성공 checkpoint + 남은 항목 + blocker + 수정파일 + 다음 테스트 + rollback 지점을 자동 기록 |
| Work 크레딧 사용범위 | LOCK | Chat/GitHub에서 불가능한 실제 실행/E2E만 허용 |
| Work 진입판정 | 아직 HOLD | Chat/GitHub 선행작업을 더 이상 진행할 수 없는 지점까지 완료 후 사용자에게 보고 |

## 현재 blocker
| blocker | 원인 | 개선방법 | Work 크레딧 |
|---|---|---|---|
| MATERIAL_GUARD_COMMON_CALLSITE | guard는 중앙 audit에서 실제 실행되지만 모든 개별 tool mutation의 공통 callsite까지 완전히 강제되지 않음 | 중앙 adapter/module 계약의 validate 이전 단계에 guard 호출 규격 고정 | Chat+GitHub 선행 가능 |
| FINAL_STATE_VALIDATION | run `31712529019` 마지막 state assertion이 현재 state와 불일치 | 로그에서 정확한 assertion만 찾아 최신 사용자 우선순위/상태와 충돌 없이 수정 | Chat+GitHub 선행 가능 |
| CROSS_REPOSITORY_TARGET_APPLY | 실제 repo target 자동 write/read-back/test 통로는 환경/권한 의존 | Chat/GitHub 선행준비 후 실제 Work-only인지 확정 | Work 필요 가능성 있음 |
| INDEPENDENT_VERIFICATION | 제3자 run/result 없음 | 외부 실제 runner가 있을 때 별도 증거로 기록 | 구조 내부 PASS와 분리 |

## Work 크레딧 사용 잠금
- 기존 규칙 재독해·재요약·저장소 재검색·안티그래비티 재추출에는 Work 크레딧을 사용하지 않는다.
- Chat/GitHub에서 가능한 guard 범용화·state 정합성·handoff/restart 준비는 Work 전에 끝낸다.
- Work에 들어가면 **Chat/GitHub에서 실제로 불가능하다고 확인된 실행·E2E**부터 시작한다.
- 이미 PASS한 canonical/revision cache/restart/rollback/guard fixture는 Work에서 반복하지 않는다.
- Work 크레딧이 끝나도 `WORK_ONLY_HOLD`만 남도록 하고, 나머지는 Chat+GitHub에서 계속 개발 가능해야 한다.

## 최신 restart point
1. 승인 없는 구조변경 guard fixture와 중앙 audit 첫 단계 연결은 재실행하지 않는다.
2. run `31712529019` 마지막 `Validate collector and integration-core state` 실패 assertion을 정확히 확인한다.
3. 사용자 최신 우선순위와 충돌하는 stale state assertion만 최소 수정한다.
4. material mutation 공통 계약을 `PRECHECK_USER_DIRECTIVE -> VALIDATE -> APPLY -> TEST -> EVIDENCE -> ROLLBACK/HOLD` 순서로 고정한다.
5. DENY evidence를 observer report 대상으로 남기는 계약을 고정한다.
6. Work 종료 handoff 스키마를 checkpoint/state에 연결한다.
7. Chat/GitHub에서 더 진행할 수 없는 실제 blocker만 `WORK_ONLY_HOLD`로 분류한다.
8. 그 시점에 사용자에게 `사전준비 완료율 / 남은 Work-only 항목 / Work 첫 작업 / 예상 크레딧 사용처 / Work 중단 시 재개점`을 한 번에 보고한다.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.

<!-- WIC_DENY_OBSERVER_AUTO_START -->
## 최근 DENY 자동 관찰자 보고
- generated_at_utc: `2026-08-25T05:23:50.601669+00:00`
- decision: `DENY_HOLD`
- action: `APPLY_FEEDBACK`
- target: `WIC_GLOBAL_OPERATING_RULES.md`
- reason: `directive text not found as an exact approved user-record entry`
- error_class: `STRUCTURAL_ERROR_UNAUTHORIZED`
- blocked_before_mutation: `true`
- directive_source_ref: `CURRENT_CHAT#user-feedback-2026-08-25-toc-output-gate-execution-failure`
<!-- WIC_DENY_OBSERVER_AUTO_END -->

<!-- WIC_EXECUTION_STATE_SYNC_START -->
## 중앙 실행상태 자동 동기화

| 항목 | 실제 값 |
|---|---|
| 중앙 상태 | `HOLD_EXTERNAL_RUNTIME_ACCESS` |
| 중앙 상태 갱신 | `2026-08-18 02:01 KST` |
| checkpoint | `HOLD_DELTA_RECONCILIATION` |
| 대화 identity 보호 | `PASS_INTERNAL_GITHUB_PREFLIGHT_VERIFIED` |
| restart point | TOOL040 legacy delta is closed by verified TOOL043 migration. Continue current-tool-manifest lookup and targeted post-baseline omission checks without repeating Antigravity RAW extraction, prior Work preflight gates, or hierarchy creation. |
| blocker | ANTIGRAVITY_ALL_CURRENT_TOOLS_COMPLETENESS: The retained Antigravity crosscheck proves the June extraction scope, not completeness for every tool that exists now. No authoritative all-current-tools manifest/hash set has been located yet; therefore all-current-tools completeness remains HOLD. / CONTROL_TOWER_34_ASSET_LOCATION: Existing WIC34/CONTROL TOWER runtime root is D:\오부장 AI (인공지능)\WIC34_C_REBUILD. The current Work cannot access that external Windows path. Resume when the existing asset is made accessible to this Work or an approved external runner exposes its state; do not create a replacement. |

- 이 구역은 `WIC_EXECUTION_STATE.json`에서 자동 생성한다.
- Observer가 자체적으로 RUNNING을 추정하지 않고 중앙 실행상태를 그대로 표시한다.
<!-- WIC_EXECUTION_STATE_SYNC_END -->
