# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-13 21:18 KST
상태: ACTIVE — 중앙 통합 계속 진행 / CHAT IDENTITY LOCK 강화 / GitHub stall 자동 재실행 구조 보완

규범 원본은 `WIC_GLOBAL_OPERATING_RULES.md`. 37번=metadata production/integrated verification, 13번=Excel automatic upload로 분리 유지.

## 현재 우선순위 및 restart
- 직전 실제 데이터 체크포인트: `EMAIL_COLLECTION_EXECUTION_STATE.json` 2026-08-13 21:06 KST, 진행 상태 `IN_PROGRESS_LEGACY_DATA_RECOVERY`, progress 44%.
- 직전 체크포인트가 현재 실행 직전 1시간 이내에 실제 갱신되었으므로 이번 회차는 `STALL=false`.
- EMAIL_COLLECTION 정확한 restart point: 기존 3개 HOLD fingerprint의 영구번호/인계대장 대조, SEM-002..070 실제 번호행, DEF/SHP/CAR/ROB/BAT 실제 영구번호행 회수. 이미 처리한 이메일 스레드는 재독해하지 않고 직접 번호 증거 없이는 새 번호를 부여하지 않는다.

## 이번 회차 실제 개선
| 항목 | 상태 | 증거 |
|---|---|---|
| CHAT IDENTITY 검증 게이트 | PASS_INTERNAL_GITHUB | `rule-governance-audit.yml`에 NO_NEW_CHAT, EXPLICIT_NEW_CHAT_APPROVAL, UI_TITLE_HOLD, 사용자 전용 생성/이름변경 잠금 검사 추가. commit `cef7c353efe0bcb9d9a728b9ecec07642bbf198e` |
| identity + restart fixtures 실제 GitHub 실행 | PASS | GitHub Actions run `31699196474` conclusion=`success` |
| 5분 stall 감시 | ACTIVE | 기존 `wic-stall-monitor.yml` 유지, cron `*/5 * * * *` |
| stall 후 실제 재실행 | IMPLEMENTED / NEXT-RUN VERIFY | stale 시 기존 `rule-governance-audit.yml`을 `gh workflow run`으로 재호출하도록 변경. commit `6aeb4a734aab994abfa1145fb3ad4148fd445ae1` |
| 새 대화창/새 역할/새 이름 생성 | 금지 유지 | `WIC_CHAT_ROUTING_REGISTRY.md` + `CHAT_WINDOW_OWNERSHIP_LOCK.md`를 CI가 직접 검사. 논리 role은 `UI_TITLE_HOLD`/`LOGICAL ROLE ONLY`여야 함 |

## CHAT IDENTITY LOCK 판정
- 사용자 명시 승인 없는 새 대화창/새 역할/새 준비창/새 관찰창/재명명/별칭 승계: `FAIL-NO_NEW_CHAT-VIOLATION` 또는 `CHAT_IDENTITY_MUTATION_FAIL`.
- `CONTROL_PRIMARY`, `WORK_PREP` 등 내부 논리 role을 실제 UI 제목으로 승격하면 CI FAIL.
- 실제 UI 대화창 제목은 직접 UI/접근 가능한 대화 기록 근거가 없으면 `UI_TITLE_HOLD`.
- GitHub는 ChatGPT UI 자체의 생성 버튼을 기술적으로 차단할 수는 없으므로, 이 구조의 실제 강제 범위는 WIC 라우팅·자동화·GitHub 실행이 새 이름을 생성/채택/승계하지 못하게 하는 검증 게이트다.

## stall 복구 구조
- GitHub `WIC Stall Heartbeat Monitor`가 5분마다 `WIC_LIVE_OBSERVER_STATUS.md`의 마지막 commit age를 검사한다.
- 현재 threshold는 35분이며 stale이면 기존 single stall issue를 갱신한 뒤 기존 `WIC Rule Governance Audit`을 재-dispatch한다.
- 재-dispatch되는 audit은 중앙 rule 검증 + CHAT IDENTITY gate + integration ingest/canonical/target dispatch + rollback/restart E2E를 실행한다.
- 새 workflow/새 대화창/새 역할은 생성하지 않는다.
- 새 stall monitor 코드 자체의 다음 scheduled run 성공 여부는 아직 실행 전이므로 `NEXT-RUN VERIFY`; 이전 코드 run 73 failure를 새 코드 성공으로 소급해 PASS 처리하지 않는다.

## PASS / HOLD / FAIL
- PASS: 중앙 identity gate 코드 반영 + GitHub Actions 실제 성공.
- PASS: EMAIL_COLLECTION 21:06 체크포인트 실제 read-back, 이번 회차 stall 아님.
- HOLD: 새 stall monitor 버전의 실제 scheduled stale/non-stale 분기 실행 증거는 다음 GitHub run에서 확인 필요.
- HOLD: legacy permanent-number/other-sector ledger 복구는 계속 미완료.
- FAIL 없음: 이번 회차 새 무단 대화창/이름 변경 실행은 하지 않음.

## 정확한 다음 restart point
1. 새 stall monitor 버전 첫 scheduled run conclusion을 확인하고 실패 시 같은 기존 workflow 파일에서 즉시 수정한다.
2. EMAIL_COLLECTION은 21:06 restart point에서 영구번호/인계대장 직접 증거 회수를 계속한다.
3. identity gate는 매 관련 push/manual recovery마다 재검증하며 `UI_TITLE_HOLD`가 빠지거나 role이 UI 제목으로 승격되면 즉시 FAIL한다.
4. 완료 단계는 반복하지 않고 우선순위의 다음 미완료 단계로 이동한다.

사용자 역할: 관찰자. 재설명·복사/붙여넣기·터미널·대화창 선택·반복 테스트를 요구하지 않는다.
