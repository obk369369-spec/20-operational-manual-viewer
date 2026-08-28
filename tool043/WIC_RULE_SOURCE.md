# 43번 소형 앱 출시 실행도구 Rule Source Pointer

상태: ACTIVE POINTER
정식 번호: `43번`
도구명: `43번 소형 앱 출시 실행도구`
대화창 제목: `소형 앱 출시`
Machine route key: `TOOL043`

규범 실행 원본은 이 디렉터리에 복제하지 않는다.

- Global SOT: `../WIC_GLOBAL_OPERATING_RULES.md`
- Routing ledger: `../WIC_CHAT_ROUTING_REGISTRY.md`

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

역할 잠금:
- 실제 실행 주체는 Work/Codex 또는 기존 승인불필요 자동 실행 엔진이다.
- TOOL043은 `OBSERVATION/STATE/HANDOFF BRIDGE`이며 직접 업무를 수행하지 않는다.
- 스마트폰은 Observer view 전용이고 `SMARTPHONE_DIRECT_WORK_EXECUTION=FORBIDDEN`이다.
- `REMOTE_APPROVAL_FROM_SMARTPHONE=BLOCKED_PLATFORM/NON_BLOCKING/SKIP_REUSE`이며 완료조건이 아니다.

완전 PASS는 실제 외부 배포/출시 경로, 재조회 가능한 외부 증거, 필요한 배포 검증까지 확인된 경우에만 판정한다.
