# 소형 앱 출시 실행도구 Rule Source Pointer

상태: ACTIVE POINTER
도구명: `소형 앱 출시 실행도구`
대화창 제목: `소형 앱 출시`

규범 실행 원본은 이 디렉터리에 복제하지 않는다.

- Global SOT: `../WIC_GLOBAL_OPERATING_RULES.md`
- Routing ledger: `../WIC_CHAT_ROUTING_REGISTRY.md`
- Legacy route key: `TOOL040` — 기존 자동 라우팅 호환용 machine key이며 사용자 도구 번호가 아님

현재 `tool040/` 경로 역시 legacy 기술 경로다. 사용자-facing 이름이나 정식 번호로 해석하지 않는다.

현재 최소 구현 범위:
1. 모바일 관찰자 화면
2. 아이디어 입력 및 잠금
3. 진행/보류 명령 저장
4. 상태 및 타임스탬프 기록
5. 증거 JSON 내보내기

완전 PASS는 실제 외부 배포/출시 경로, 재조회 가능한 외부 증거, 필요한 배포 검증까지 확인된 경우에만 판정한다.
