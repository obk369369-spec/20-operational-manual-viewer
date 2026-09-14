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
