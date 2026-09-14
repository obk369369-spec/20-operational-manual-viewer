# WIC Work 운영 매뉴얼

1. ChatGPT에서 가능한 조사·검색·설계·비교·시험설계는 Work 전에 완료한다.
2. Work는 실제 변경·실행·시험·배포·commit/push/read-back만 수행한다.
3. 기존 검증 결과는 `SKIP_REUSE_VERIFIED`한다.
4. Work 한 ROUND는 초소형 실제 기능 1개만 처리한다.
5. 실패 시 관련 원인을 일괄 확인하고 수정 1회, 검증 1회만 수행한다. 같은 원인 재실패 시 HOLD한다.
6. 기존 PASS production을 보호하며 미검증 결과로 덮어쓰지 않는다.
7. permission은 최소화하고 동일 범위의 반복 승인을 요구하지 않는다.
8. 사용자의 수동 handoff·반복 지시·상태 전달을 최소화하고 사용자는 Observer로 유지한다.
9. USB는 USB에만 필요한 실제 artifact가 있다는 증거가 있을 때만 연결한다.
10. USB/로컬 자료 자체를 검증하는 TOOL044 회차에서는 필요한 범위에 한해 USB를 사용할 수 있다.
11. GitHub 정본으로 가능한 작업 때문에 USB 또는 I: 전체 조사를 선행하지 않는다.
12. 모든 Work ROUND는 다음 순서로 강제 자동 종료한다.

`지정 작업 완료 또는 실제 blocker 확정 → 결과/증거 출력 → SAFE_CHECKPOINT 저장 → checkpoint read-back → 즉시 자동중단 → 다음 ROUND 자동 시작 금지`

## EMERGENCY_CREDIT_EXPIRY_MODE

- 발동 조건: Work 사용량 초기화·소멸 시각이 임박하고, 잔여량을 이월할 수 없으며, 사용자가 비상모드를 명시적으로 승인한 경우에만 적용한다.
- 비상모드에서는 평상시 소규모 사용 제한을 일시 해제하되 사용자가 지정한 최소 reserve를 보존한다.
- 현재 독립적으로 실행 가능하고 실제 미완료를 닫는 작업만 병렬 처리한다.
- 기존 PASS는 `SKIP_REUSE_VERIFIED`하며, 무의미한 반복시험·가짜 작업·사용량 소진 목적 작업은 금지한다.
- 각 lane은 `원인 확인 1회 → 묶음 수정 1회 → 재검증 1회`로 제한하고 같은 원인 재실패 시 격리한다.
- reserve 도달 또는 실행 가능한 독립 작업 소진 시 진행 중 원자 작업을 안전하게 닫고 종료한다.
- 비상 회차가 끝나면 추가 조치 없이 `NORMAL_MODE`로 자동 복귀한다.
- 2026-09-14 승인 사례: `START_REMAINING=44%`, `MAX_USE=40 percentage points`, `MINIMUM_RESERVE=4%`.
