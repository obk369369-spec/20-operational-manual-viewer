# TOOL040 Rule Source Pointer

상태: ACTIVE POINTER
도구: 40번 출시 앱 도구 (TOOL040)

규범 실행 원본은 이 디렉터리에 복제하지 않는다.

- Global SOT: `../WIC_GLOBAL_OPERATING_RULES.md`
- Routing ledger: `../WIC_CHAT_ROUTING_REGISTRY.md`
- Route key: `TOOL040`

TOOL040의 전용 구현은 이 디렉터리에서 관리하되, 공통 운영 규칙은 Global SOT를 따른다.

현재 최소 구현 범위:
1. 모바일 관찰자 화면
2. 아이디어 입력 및 잠금
3. 진행/보류 명령 저장
4. 상태 및 타임스탬프 기록
5. 증거 JSON 내보내기

완전 PASS는 실제 외부 배포/출시 경로, 재조회 가능한 외부 증거, 필요한 배포 검증까지 확인된 경우에만 판정한다.
