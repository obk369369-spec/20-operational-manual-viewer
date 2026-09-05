# WIC COMPLETE OBSERVER AUTONOMOUS FACTORY SPEC

상태: CANONICAL DESIGN / NOT_DEPLOYED
목적: 사용자가 아이디어·목적·기능·짧은 설명 또는 음성 지시만 제공하고, 나머지 개발·수리·테스트·검증·저장소 반영·실사용 배포를 관찰자에게 전가하지 않는 WIC 최종 상위 구조를 정의한다.

## 0. 최상위 원칙
- 새 구조를 처음부터 자체 개발하는 것을 기본값으로 삼지 않는다.
- 우선순위는 `기존 WIC VERIFIED_COMPONENT 재사용 → TOOL044 외부 완성·실사용·검증·무료 부품 조달 → 무료/로컬 실행층 → 외부 오픈소스 코딩 에이전트/로컬 모델 → 정말 필요한 예외 판단만 Work`다.
- 사용자는 OBSERVER ONLY다. 개발자·테스터·로그분석가·파일관리자·팀간 전달자가 아니다.
- 부분 완료·껍데기·UI만 존재·버튼만 존재·파일 생성만으로 PASS하지 않는다.
- 하나의 작업은 TEST/검증/GitHub 또는 해당 저장소 read-back/실사용폴더 배포/배포본 재시험까지 닫아야 완료다.
- 정상 운영 중 추가 지속비용 0을 기본 목표로 한다. 크래딧과 유료 API/SaaS는 마지막 수단이다.

## 1. 최상위 흐름
`음성/텍스트 입력 → 43번 Observer Gateway → 요구사항 구조화/사전 시뮬레이션 → Capability Router → TOOL044 대량 부품 조달 → Component Contract 검사 → 자동 조합 후보 생성 → 무료/로컬 Runner 병렬 실행 → 독립 TEST/검증 → 상호감사/자가복구 → GitHub/MASTER 또는 대상 저장소 → remote read-back → 실사용폴더 배포 → 배포본 재시험 → DEPLOYED_PASS → 43번 결과 관찰`

## 2. 43번 역할
- 43번은 계산·개발의 주 실행기가 아니라 스마트폰 관찰 Gateway다.
- 입력 방식: 짧은 텍스트 또는 음성.
- 최소 입력: `도구 목적 / 핵심 기능 / 짧은 설명`.
- 사용자가 repo, checkpoint, 로그, Action, Work 결과를 운반하지 않는다.
- 기본 화면은 `현재 상태 / 진행중 / 완료 / OPEN / HOLD / 마지막 SAFE_CHECKPOINT / DEPLOYED_PASS`만 단순 표시한다.

## 3. 사전 시뮬레이션층 — REQUIRED
새 도구·프로그램·대화기반 작업을 시작하기 전에 실제 개발보다 먼저 아래를 자동 시뮬레이션한다.
- 요구사항 충돌
- 입력/출력 누락
- 기존 WIC 기능과 중복
- 과거 반복 실패 패턴
- 의존성/런타임 충돌
- 저장소/배포 경로 충돌
- 병렬 실행 시 race/lock 위험
- 테스트 가능성 부족
- 사용자 개입 필요 가능성
- 지속비용 발생 가능성
- 외부 부품으로 대체 가능한지

판정:
- 미리 해결 가능 → 구조/부품/순서를 사전 보정 후 착수
- 기존 VERIFIED 재사용 가능 → SKIP_REUSE
- TOOL044 외부부품 가능 → 자체 개발 전 TOOL044로 전환
- 비용 발생 → ZERO_COST 대체 경로 재탐색
- 현재 한 번에 DEPLOYED_PASS까지 닫기 어려움 → 착수 금지 또는 범위 재설계

PRE_SIMULATION_REQUIRED = TRUE
PREVENTABLE_ERROR_BEFORE_BUILD = REQUIRED
START_WITH_KNOWN_CONFLICT = FORBIDDEN

## 4. TOOL044 — VERIFIED COMPONENT FACTORY
TOOL044는 단일 검색도구가 아니라 전체 시스템이 공통으로 사용하는 외부 검증부품 조달·검증 계층으로 사용한다.

순서:
1. 기존 WIC VERIFIED_COMPONENT 검색
2. 외부에서 완성·공유·실사용·유지보수되는 무료 부품 검색
3. 라이선스/보안/의존성/런타임/무수정 사용 가능성 검사
4. Component Interface Contract 작성
5. 독립 sandbox EXPECTED↔ACTUAL
6. PASS 부품만 registry 등록
7. 여러 기능 부품을 조합 후보로 생성
8. 조합별 병렬 sandbox 검증
9. 실제로 작동하는 최소 조합만 채택
10. 대상 TOOL 통합시험
11. 저장소 반영/read-back
12. 실사용폴더 배포/배포본 재시험

외부 부품 자체의 수정·커스터마이즈·추가개발이 필요하면 READY_COMPONENT로 인정하지 않는다.

## 5. Component Interface Contract — REQUIRED
외부 부품 조합 전에 최소 아래를 등록한다.
- INPUT
- OUTPUT
- runtime/language/version
- dependencies
- license
- network requirement
- storage/state
- side effects
- security boundary
- deterministic test fixture
- expected failure modes

계약이 맞지 않는 부품끼리는 조합하지 않는다.

## 6. 무료/로컬 실행층 우선순위
특정 서비스에 고정하지 않고, TOOL044 방식으로 검증 후 채택한다.

기본 우선순위:
`기존 실행결과/cache → 기존 PC 로컬 실행 → self-hosted 무료 runner → 무료 오픈소스 orchestration/runtime → 무료 범위 외부 runner → GitHub Actions 무료 포함범위 → Work → 별도 유료 실행은 기본 차단`

후보군 예시(채택 전 TOOL044 검증 필수):
- 로컬 shell/Python/Node runner
- Playwright 등 실제 브라우저 E2E 실행기
- Git/self-hosted runner
- n8n Community Edition / Kestra / Windmill / Temporal 계열 오픈소스 실행·오케스트레이션 구조
- OpenHands 계열 오픈소스 코딩 에이전트
- Ollama / LM Studio 계열 로컬 모델 실행기

목표는 `24시간 가능한 작업을 Work 밖으로 최대한 이동`하는 것이다.

## 7. Capability Router
새 요청을 아래 순서로 자동 분기한다.
1. 기존 TOOL 그대로 재사용 가능
2. 기존 WIC VERIFIED_COMPONENT 조합 가능
3. TOOL044 외부 READY_COMPONENT 조합 가능
4. 무료/로컬 규칙엔진으로 해결 가능
5. 오픈소스 코딩 에이전트 + 로컬 모델로 해결 가능
6. 그래도 불가능한 새로운 판단만 WORK_EXCEPTION_QUEUE

WORK_IS_DEFAULT = FALSE
WORK_EXCEPTION_ONLY = TRUE

## 8. 자가학습·자가보완 안전 경계
자가학습은 자유 코드변경 권한이 아니다.

허용 흐름:
`오류 증거수집 → fingerprint → 과거 실패/복구 검색 → 복구 후보 생성 → 격리 sandbox → 독립 TEST → EXPECTED↔ACTUAL → 영향 회귀 → 실제 대상 E2E → 저장소 read-back → 실사용 배포 → 배포본 재시험 → DEPLOYED_PASS`

DEPLOYED_PASS를 통과한 복구법만 `VERIFIED_RECOVERY_PATTERN`으로 학습한다.
FAIL 해결법은 성공 패턴으로 학습하지 않고 `KNOWN_FAILED_METHOD`로 저장하여 같은 방법 재시도를 차단한다.

AUTO_LEARN_UNVERIFIED_FIX = FORBIDDEN
LEARN_ONLY_AFTER_DEPLOYED_PASS = REQUIRED
KNOWN_FAILED_METHOD_RETRY = FORBIDDEN

## 9. 검증층도 검증받아야 한다
단일 검증층을 절대 신뢰하지 않는다.
- 검증층 A의 판정을 검증층 B가 독립 근거로 감사한다.
- B도 고장나면 canonical test fixture/known-good baseline/SAFE_CHECKPOINT로 deterministic bootstrap한다.
- 검증층 자체도 가능한 경우 TOOL044에서 외부 검증된 test runner/auditor/validator 부품을 우선 채택한다.
- 한 층의 PASS/HOLD/COMPLETE를 자기 선언만으로 인정하지 않는다.

SELF_ATTESTED_PASS = FORBIDDEN
PEER_AUDIT_REQUIRED = TRUE
EXTERNAL_VERIFIED_VALIDATOR_FIRST = TRUE

## 10. 상호감사·자가복구
한 층 또는 여러 층이 고장나도 관찰자에게 수리를 전가하지 않는다.
- heartbeat/state 감시
- 고장난 층 격리
- peer auditor가 원인 재확인
- 마지막 SAFE_CHECKPOINT에서 재개
- 동일 방법 재시도 최대 1회
- 이후 다른 방법/다른 부품/다른 runner로 전환
- 독립적으로 증명된 외부 HOLD만 사용자에게 보고

USER_REPAIR = FORBIDDEN
PEER_RECOVERY = REQUIRED
SAFE_CHECKPOINT_RESUME = REQUIRED

## 11. 병렬 실행 규칙
대량 도구·프로그램·대화기반 작업은 독립 대상끼리 병렬 실행한다.
같은 repo/파일/MASTER/공통자산을 동시에 수정하는 작업은 Lock Scheduler가 직렬화한다.

PARALLEL_WHEN_INDEPENDENT = REQUIRED
CONFLICTING_WRITE_PARALLELISM = FORBIDDEN
DEPENDENCY_LOCK_SCHEDULER = REQUIRED

## 12. 껍데기 차단 게이트
아래는 PASS 증거가 아니다.
- UI가 보임
- 버튼 존재
- HTML 열림
- 코드 문자열 존재
- 파일 생성
- exit code 0
- commit 존재

최소 PASS 체인:
`실제 입력 → 실제 기능/버튼 실행 → 실제 결과/다운로드 → EXPECTED↔ACTUAL → 영향 회귀 → 저장소 write/read-back → 실사용폴더 배포 → 배포된 복사본 동일 테스트 → DEPLOYED_PASS`

SHELL_PASS = FORBIDDEN
DEPLOYED_COPY_TEST_REQUIRED = TRUE

## 13. 관찰자 보호
사용자에게 아래를 요구하면 구조 FAIL이다.
- 반복 허용버튼
- 로그 복사
- 파일 재업로드
- repo 선택
- checkpoint 선택
- 테스트 반복
- 오류 원인 분석
- 팀간 결과 전달
- GitHub/Actions 수동 실행
- 배포 작업
- 수리/복구

플랫폼상 사용자가 아니면 할 수 없는 외부 행위만 USER_ACTION_QUEUE에 모아 가능한 한 1회로 묶는다.

USER_INTERMEDIATE_OPERATION = FORBIDDEN_BY_DEFAULT
USER_ACTION_QUEUE = REQUIRED_FOR_TRUE_USER_ONLY_ACTIONS

## 14. 비용·크래딧 방화벽
- 정상 운영·테스트·복구·배포에서 추가 지속비용 0을 목표로 한다.
- 유료 API/SaaS/AI를 무료 대체층 조사 전에 채택하지 않는다.
- 비용이 발생할 가능성이 있으면 자동 실행하지 않고 무료 대체경로를 먼저 찾는다.
- Work가 필요하면 `왜 로컬/외부 검증부품으로 해결 불가한지 / 필요한 최소 작업 / 예상 크래딧 범위 / 한 번에 DEPLOYED_PASS까지 닫을 수 있는지`를 먼저 보고한 뒤 착수한다.
- Work 작업은 부분 개발로 끝내지 않는다. 테스트·검증·저장소 반영·실사용배포·배포본 재검증까지 한 번에 닫을 수 있는 범위만 시작한다.

ZERO_COST_PATH_FIRST = REQUIRED
PAID_FALLBACK_WITHOUT_REPORT = FORBIDDEN
WORK_PARTIAL_BUILD = FORBIDDEN
WORK_MUST_TARGET_DEPLOYED_PASS = TRUE

## 15. 저장소/USB/Master
USB/기존 로컬 자료를 GitHub/MASTER로 옮길 때 AI가 모든 파일을 읽는 방식으로 크래딧을 쓰지 않는다.
로컬에서 목록/hash/dedup/diff/type 분류를 먼저 수행하고 의미판단이 필요한 최소 후보만 판단층으로 올린다.

LOCAL_HASH_DIFF_FIRST = REQUIRED
SEMANTIC_REVIEW_ONLY_FOR_AMBIGUOUS = TRUE

## 16. 현재 구현 경계
이 문서는 구조의 canonical design이다.
이 문서 생성 자체는 전체 시스템 구현·배포 완료를 의미하지 않는다.
각 외부 부품·runner·agent·validator는 TOOL044 절차로 실제 무수정 사용 가능성, 라이선스, 보안, 유지보수, sandbox TEST를 통과해야 채택한다.
전체 구조는 실제 다중 TOOL 대상으로 병렬 E2E → 저장소 read-back → 실사용폴더 배포 → 배포본 재시험을 통과해야만 DEPLOYED_PASS로 선언할 수 있다.

CURRENT_STATE = DESIGN_CANONICALIZED_NOT_DEPLOYED
