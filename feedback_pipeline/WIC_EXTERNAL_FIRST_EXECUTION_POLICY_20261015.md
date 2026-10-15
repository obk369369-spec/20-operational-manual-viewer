# WIC 외부 우선 실행 정책 — 2026-10-15

## 절대 원칙
WIC의 기본 작업장은 ChatGPT/Codex Work가 아니라 독립 외부 클라우드/실행공장이다. 외부 실행을 먼저 시도하며, ChatGPT/Codex Work는 사용자 승인·예외처리·결과 확인에 한정한다. 편의상 Work 내부에서 개발·검증·배포를 시작하지 않는다.

## 외부화 순서
1. 기존 연결된 GitHub canonical / GitHub Actions / repository_dispatch / Render 무료 Web Service / PASS_LOCK / Evidence / Release Governor를 재사용한다.
2. 부족한 기능은 무료·공유 가능한 **완성된 외부 장치**로 우선 채운다. 단일 완성형 플랫폼이 있으면 그것을 우선 사용하고, 없으면 서브에이전트, 영속 Queue/State, 백그라운드 Worker, 감시·자동복구, 독립 검증, 배포기를 Socket/API/Webhook/CLI로 조합한다.
3. 후보 탐색과 실행은 외부 플랫폼 및 공식 연결 API 중심으로 진행한다. 기존 후보 결과를 재사용하고, 반복 조사·내부 거대 플랫폼 자체개발·설계보고서로 종료하지 않는다.
4. Controller 부재는 **외부 조합 구축 작업의 시작 조건**이지 구축 작업의 STOP 조건이 아니다. 단, 실제 WIC 제품 작업과 PASS 선언은 검증 완료 전 금지한다.
5. 최초 계정 연결·자격증명·권한·비용 경계에서만 사용자에게 구체적인 단일 승인을 요청한다. 승인 없는 유료 자원·실제 대외 발송·실결제 금지.
6. 외부 구조가 실제 Job ID와 영속 State를 소유하고 Work 세션 없이 실행·실패 감지·재시도/수정·회귀 테스트·배포·Remote Readback·Evidence 반환하는지 대표 Job으로 확인한다. 24시간 무인 운영 PASS는 실제 관찰 후만 선언한다.

## 현재 보존 체크포인트
- OPEN=26, INTERNAL_OPEN=11, HOLD=15. PASS_LOCK 재개방·3200건 재스캔 금지.
- Render 기존 무료 서비스의 실행/결과반환 Roundtrip PASS_LOCKED. Render 단독 Controller는 FAIL (무료 Web Service 1, Key Value 0, Postgres 0).
- Release Governor PASS_LOCKED.
- EXTERNAL_TOP_PLATFORM=FAIL, EXTERNAL_WORKSPACE_MIGRATION=FAIL, EXTERNAL_EVIDENCE_CHAIN=PARTIAL.
- 기존 4 Socket 연결은 보존. 새 Controller 연결과 제품 실제 운영은 아직 검증되지 않음.

## 즉시 외부 완성품 후보 (공식 자료 확인, 실제 연결 미검증)
- Windmill: Postgres 기반 영속 Queue, 독립 Worker, 워크플로, AI sandbox에서 Codex/Claude Code 실행 기능. 오픈소스 self-host 가능. 다만 24시간 호스팅/DB 비용·무료 한도와 계정 연결은 별도 검증 필요.
- Activepieces: 무료 시작 클라우드/셀프호스트, Agents, Flows, Tables, HTTP/MCP 연결. 무료 운영 한도와 개발·자동수정/복구 소유권은 별도 검증 필요.
- GitHub Actions runner/ARC: 외부 실행기 확장 후보. 별도 영속 Controller를 자동 제공하는 것은 아님.

## 강제 실행 계약
외부 완성품 선택 → 최소 승인/연결 → 기존 4 Socket 결합 → 외부 Job 발행 → 영속 State/Queue → 서브에이전트/Worker 실행 → 실패주입·복구 → 독립검증 → Release Governor → 배포 → Remote Readback → 사용자 결과 → Evidence/Canonical 반환.
각 단계에서 실제 Provider 실행 ID·로그·비용·PASS/HOLD를 기록한다. 문서/커밋만으로 운영 완료를 선언하지 않는다.

## 작업 위치 판정
EXTERNAL_FACTORY=DEFAULT_WORKSPACE.
CHATGPT_CODEX_WORK=EXCEPTION_WORKSPACE.
외부에서 할 수 있는데 Work가 주 실행자가 되면 STRUCTURAL_FAILURE.
목표: CODEX_WORK_AS_PRIMARY_WORKSPACE=0, WORK_CREDIT_EXECUTION_DEPENDENCY=0.

## [최우선 HARD GATE — 반복조사·개선화면만 표시하는 작업 시작 금지, 2026-10-15]
이 규칙은 모든 WIC 16번/44번 실행 및 외부 사업·제품 작업의 시작 판정에 우선한다.

**금지:** 기존 플랫폼 후보 재검색·반복 비교·같은 후보 재평가, 새 지시문/보고서/Evidence만 생성하는 작업, Work 내부 코드 개선/설계/분석을 실제 외부 이전으로 포장하는 작업, “개선 중” 화면만 표시하며 Work 크레딧을 소비하는 실행. GitHub 문서/커밋만으로 CONNECTED 또는 VERIFIED 선언 금지.

**작업 시작 전 필수 판정:**
- `EXTERNAL_EXECUTION_TARGET`: 실제 외부 플랫폼/워크스페이스/서비스 식별자
- `EXTERNAL_AUTHORITY`: 연결된 OAuth/승인된 API/실행 권한의 실제 확인
- `EXTERNAL_ACTION`: 이번 실행에서 실제로 수행할 외부 연결/Job 발행/배포
- `EXTERNAL_RESULT_EVIDENCE`: Provider Job ID, 로그, 외부 실행 URL, 결과 readback
- `USER_APPROVAL_BOUNDARY`: 승인 필요한 경우 정확히 한 가지 행동, 예상 비용 및 안전 영향
- `WORK_PRIMARY_EXECUTION`: 0; 예외적 최초 소켓 연결/bootstrap만 최소 허용
위 조건 중 실행 대상·권한·구체적 외부 동작이 없으면 **장시간 Work 실행을 시작하지 않는다.** 승인이나 계정 연결이 필요한 경우 즉시 최소 한 가지 행동만 요청한다. 승인 없이 유료 서비스·외부 발송·실결제 금지.

**완료 판정:** 실제 외부 Provider에서 Job/State 소유권과 결과 반환이 증명된 경우에만 CONNECTED/EXECUTED. 대표 Job의 외부 실패·복구·독립검증·배포·readback·canonical 증거가 있어야 FACTORY_E2E_PASS. 24시간 실제 관찰 전 24H_VERIFIED 금지. 제품은 기존 Release Governor와 실제 사용자 출력 검증 전 PASS 금지.

**반복 방지:** 이전 Cloud 후보 조사 완료, Canonical socket audit 완료, Local partial 및 routing timeout, Render 무료 자원 확인, 기존 4 Socket PASS 증거를 재사용한다. Render 단독 FAIL을 다른 외부 플랫폼 전체 FAIL로 확대하지 않는다. Windmill/Activepieces 등의 **이름을 찾거나 문서 링크를 붙이는 것은 획득/연결이 아니다.** 해당 외부 계정·인스턴스가 실제 없으면 인증된 외부 연결 수단을 확인하고, 사용자 승인 경계가 나타나면 그 한 가지 승인만 요청한다. 승인 경계 이전에 보고서만 반복하지 않는다.

**상태 보고는 반드시 분리:** `POLICY_REGISTERED`, `PLATFORM_DISCOVERED`, `ACCOUNT_CONNECTED`, `EXTERNAL_JOB_EXECUTED`, `FACTORY_E2E_VERIFIED`, `24H_VERIFIED`. 앞 단계가 성공해도 뒷 단계로 승격하지 않는다.

**최우선 성과지표:** `REPEATED_PLATFORM_RESEARCH=0`, `WORK_ONLY_IMPROVEMENT_LOOP=0`, `EXTERNAL_JOB_ID_PRESENT`, `EXTERNAL_OWNER_INDEPENDENT_OF_WORK`, `WORK_CREDIT_EXECUTION_DEPENDENCY→0`. 외부 Job 실행 ID가 없으면 실제 이전 작업 완료=0.
