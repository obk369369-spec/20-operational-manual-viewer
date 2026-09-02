# 43번 소형 앱 출시 실행도구 Rule Source Pointer

상태: ACTIVE POINTER
정식 번호: `43번`
도구명: `43번 소형 앱 출시 실행도구`
대화창 제목: `소형 앱 출시`
Machine route key: `TOOL043`

규범 실행 원본은 이 디렉터리에 복제하지 않는다.

- Global SOT: `../WIC_GLOBAL_OPERATING_RULES.md`
- Routing ledger: `../WIC_CHAT_ROUTING_REGISTRY.md`
- Latest next-Work requirement checkpoint: `../feedback_pipeline/WIC_NEXT_WORK_20260902.md`

번호 중복 조사 결과:
- 28번: 해외 신규 발행사 발굴
- 32번: 기존 13번 도구 내 오류/검증 항목으로 사용
- 35번: 월드 운영시스템 전체 통합
- 36번: 이메일 수집 분야별 공통 운영
- 41번·42번: 이미 별도 업무군으로 사용
- 43번: 별도 도구/대화창 번호로 확정된 기존 기록 없음

따라서 2026-08-17부터 이 도구의 정식 번호를 `43번`으로 고정한다.
과거 `40번 출시 앱 도구`, `TOOL040`, `tool040` 표기는 잘못된 임시 식별자로 폐기한다.

현재 최소 구현 범위:
1. 모바일 관찰자 화면
2. 아이디어 입력 및 잠금
3. 진행/보류 명령 저장
4. 상태 및 타임스탬프 기록
5. 증거 JSON 내보내기
6. 일반 ChatGPT 채팅에서 가능한 작업의 24시간 자동 실행층

역할 잠금 — 2026-09-02 사용자 정정:
- TOOL043의 목표는 Work/Codex 작업 자체를 24시간 실행하거나 복제하는 것이 아니다.
- TOOL043은 일반 ChatGPT 채팅에서 가능한 조사·대조·분류·정리·중복 제거·원인 후보 축소·채팅 범위 검증/확정 같은 작업을 사용자 추가 지시 없이 24시간 실제 수행하는 실행층을 가져야 한다.
- 단순히 NEXT_WORK 목록을 만들거나 Work가 돌아갈 준비만 하는 것은 TOOL043의 실제 작업 성과로 인정하지 않는다.
- Chat에서 가능한 작업은 실제 수행 → 검증 → 결과/증거 누적까지 끝낸다.
- 코드 수정·실행환경 조작·배포 등 Work/Codex가 반드시 필요한 부분만 정확한 근거와 남은 작업을 붙여 NEXT_WORK로 넘긴다.
- Work는 TOOL043이 이미 끝낸 조사/정리/대조를 처음부터 반복하지 않고 SKIP_REUSE한다.
- TOOL043의 효과 검증에는 `실제 처리 작업 수 / 완료 수 / HOLD 수 / Work 이관 수 / 중복 방지 수 / 결과 저장 위치 / Work에서 재조사한 중복량`을 포함하며, Work 작업량이 실제 감소했는지 확인한다.
- 스마트폰은 Observer view 전용이고 `SMARTPHONE_DIRECT_WORK_EXECUTION=FORBIDDEN`이다.
- `REMOTE_APPROVAL_FROM_SMARTPHONE=BLOCKED_PLATFORM/NON_BLOCKING/SKIP_REUSE`이며 완료조건이 아니다.

TOOL043_CHAT_CAPABLE_24H_EXECUTION = REQUIRED
TOOL043_WORK_REPLACEMENT = FORBIDDEN
NEXT_WORK_ONLY_PREPARATION_COUNTS_AS_WORK = FALSE
CHAT_CAPABLE_TASK_EXECUTE_NOT_JUST_QUEUE = TRUE
WORK_RESEARCH_DUPLICATION_AFTER_TOOL043 = FORBIDDEN

완전 PASS는 실제 24시간 채팅가능 작업 실행 증거, 결과 영구저장, Work 이관 분리, Work 중복감소 검증 및 필요한 외부 배포/재조회 증거까지 확인된 경우에만 판정한다.
