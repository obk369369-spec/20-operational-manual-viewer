# WIC OBSERVER STATUS

최종 갱신: 2026-08-13 23:42 KST
상태: ACTIVE / STRUCTURE_FIRST / HOLD_CROSS_REPOSITORY_TARGET_APPLY
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
| 실제 새 feedback canonical E2E | 실제 실행 완료 | feedback `37a4a2166bb5e2a08a8c`, run `31670039251`, job `94352602812`, conclusion `success` | target apply로 이동 |
| 중앙 GitHub write/read-back | 실제 실행 완료 | canonical commit `59f388df9601503cd205885f6fa4e839aacd9f03`, revision `3f0c83fe635a4067354e8456`, hash read-back verified | 반복 금지 |
| 대상 저장소 apply/read-back/test | HOLD | `target_apply_manifest.json`의 repository targets가 `HOLD_TARGET_APPLY` | 교차 저장소 실제 실행 통로 필요 |
| 구조 최종 PASS | 아직 아님 | 사용자 PASS 기준의 target apply/read-back/test 미완료 | 이 단계 성공 후에만 PASS 승격 |
| 제3자 독립검증 | 없음 | external independent run/result 증거 없음 | 내부 GitHub E2E와 분리 유지 |

## 이번 실제 개선
| 작업 | 상태 | 실제 증거 |
|---|---|---|
| 중앙 workflow의 실제 feedback 실행 완료 확인 | 완료 | Actions run `31670039251` = completed/success |
| job 단계 전체 확인 | 완료 | job `94352602812`, ingest/canonical/apply/finalize/verify/commit 단계 success |
| canonical 실제 반영 확인 | 완료 | commit `59f388df9601503cd205885f6fa4e839aacd9f03` |
| canonical read-back 증거 확인 | 완료 | evidence `feedback_pipeline/evidence/37a4a2166bb5e2a08a8c.json`, intended/read_back hash 동일 |
| target manifest 확인 | 완료 | revision `3f0c83fe635a4067354e8456`; repository targets `HOLD_TARGET_APPLY` |
| stale execution state 정정 | 완료 | 과거 구조 PASS 표기를 최신 HOLD 기준으로 교체; commit `07258b4e3dc29504fb61122a2caee9e3eeed7a64` |

## 구조적 오류 감지 게이트 — UNAUTHORIZED STRUCTURE GUARD
- 사용자에게서 명시적으로 지시되지 않은 새 대화창 생성, 새 관리/보고 대화창 생성, 대화창 자동 이전, 대화창 이름 변경, 새 구조/새 registry/새 운영분기 생성 시도를 모두 `STRUCTURAL_ERROR_UNAUTHORIZED` 후보로 먼저 분류한다.
- 실행 전 반드시 `사용자 명시 승인 목록 + 기존 registry + 기존 conversation/도구 식별자`와 diff 비교한다.
- 승인 근거가 없으면 생성/변경을 실행하지 않고 `DENY + HOLD`한다.
- GitHub 안에서 생긴 승인 없는 구조/규칙/파일은 가능한 경우 즉시 rollback/delete 대상으로 표시하고, 삭제 가능한 경우 삭제 후 read-back으로 부재를 검증한다.
- ChatGPT 앱 대화창처럼 현재 연결도구로 직접 삭제할 수 없는 객체는 `STRUCTURAL_ERROR_UNAUTHORIZED / USER_DELETE_REQUIRED`로 즉시 보고한다. 사용자가 만들었다고 간주하거나 정상 구조로 승계하지 않는다.
- 감지 대상 키워드/행동: `새 대화창`, `다음 대화창`, `자동 이전`, `별도 관리창`, `별도 보고창`, `새 이름`, `rename`, `create conversation`, `new chat`, `new registry`, `새 운영 구조`.
- 단순 키워드만으로 삭제하지 않고, 사용자 명시 지시와 실제 diff를 함께 대조한다.
- 동일 유형이 1회라도 실제 발생하면 회귀테스트 항목으로 승격하고, 이후 구조 변경 전 preflight에서 반드시 검사한다.
- 이 게이트를 통과하지 못한 구조 변경은 기능상 정상이어도 PASS 금지.

## 현재 blocker
| blocker | 원인 | 개선방법 | Work 크레딧 |
|---|---|---|---|
| CROSS_REPOSITORY_TARGET_APPLY | 중앙 workflow 권한은 중앙 저장소 `contents: write`이며 repository target 자동 write/read-back/test 통로가 검증되지 않음 | 실제 cross-repo dispatch/credential 또는 target runtime의 중앙 revision 직접 소비 경로를 1개 실제 연결하고 E2E 증거 생성 | 필요 가능성이 높음 — 이 구간에만 사용 |
| AUTOMATIC_TRIGGER | 현재 workflow는 CENTRAL_LANE_ACK만 자동 final PASS 가능하며 repo targets는 fail-closed HOLD | 실제 repo target trigger와 결과 회수까지 연결 | 필요 가능성이 높음 |
| INDEPENDENT_VERIFICATION | 제3자 run/result 없음 | 외부 실제 runner가 생겼을 때 별도 증거로 기록 | 현재 필수 PASS 기준과 분리 |
| UNAUTHORIZED_STRUCTURE_DETECTION | 기존 규칙은 임의 생성/이름변경 금지 문구만 있고 구조 변경 preflight 감지/deny gate가 없었음 | 승인목록 diff → DENY/HOLD → rollback/delete → read-back → 회귀테스트 체인을 실제 구현/검증 | Chat+GitHub 선행 가능 |

## Work 크레딧 사용 잠금
- 기존 규칙 재독해·재요약·저장소 재검색·안티그래비티 재추출에는 Work 크레딧을 사용하지 않는다.
- 이번 Work가 필요하다면 **교차 저장소 target 실제 apply/read-back/test E2E를 성립시키는 구간만** 사용한다.
- 구조 PASS 전 개별 도구 기능개발로 우선순위를 바꾸지 않는다.

## 최신 restart point
1. feedback `37a4a2166bb5e2a08a8c`의 ingest/canonical/run `31670039251`은 재실행하지 않는다.
2. canonical revision `3f0c83fe635a4067354e8456`의 `target_apply_manifest.json`에서 시작한다.
3. 실제 repository target 1개 이상에 revision 적용 → target read-back → target-side deterministic test → run/result evidence → 중앙 상태 회수까지 한 E2E로 연결한다.
4. 동시에 `UNAUTHORIZED STRUCTURE GUARD`를 preflight 단계에 연결하고 승인 없는 구조 생성/이름변경/자동이전 fixture를 DENY시키는 회귀테스트를 만든다.
5. 성공 시 동일 구조를 나머지 target에 재사용할 수 있는지 확인하고 `STRUCTURE_PASS_INTERNAL_GITHUB_E2E`로 승격한다.
6. 실패 시 permission/credential/runner/trigger 중 최초 실제 blocker를 HOLD로 기록하고, 완료된 canonical 단계는 반복하지 않는다.
7. 구조 PASS 뒤 사용자 지정 우선순위는 최신 사용자 지시를 다시 읽어 적용하며, 과거 우선순위 목록을 자동 승계하지 않는다.
8. 오후 1시·5시 메일 통합 예약은 별도 예약 작업이며 이 개발 restart point와 혼동하지 않는다.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
