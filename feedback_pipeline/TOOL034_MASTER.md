# 34번 기준관리창 MASTER

상태: ACTIVE / INDEPENDENT OPERATING CHAT / NON-TOOL
정본 위치: CENTRAL `feedback_pipeline/TOOL034_MASTER.md`
공통 운영원본: `WIC_GLOBAL_OPERATING_RULES.md`
공통 실행블록: `feedback_pipeline/WIC_WORK_COMMON_EXECUTION_BLOCK.md`

## 1. 정체성
- 34번은 실행 도구 개발창이 아니다.
- 34번은 WIC34 기준관리 사령부 역할의 독립 운영 대화창이다.
- 관리 범위: 기준 관리, 공통 보완사항 관리, 문서 관리, 인계문 관리, 개발 방식/방향 결정.
- 개별 도구 개발·엔진 개발·코드 수정·개별 검증·러너 운영은 해당 TOOL 작업창에서 수행한다.

## 2. CENTRAL과의 관계
- 공통 운영규칙 자체는 `WIC_GLOBAL_OPERATING_RULES.md`가 단일 SSoT다.
- 34번 MASTER는 글로벌 규칙을 중복 복제하지 않는다.
- 34번에는 역할·경계·판단 절차·인계 관계 등 34번 고유 운영정보만 남긴다.
- 34번에서 발견된 반복 공통규칙은 검증 후 GLOBAL/CENTRAL의 해당 정본으로 승격하고, 이 파일에는 필요 시 포인터/상태만 둔다.

## 3. 판단 역할
- 기존 문서, 기존 기준, 현재 작업상태, 신규 보완사항 사이에 충돌이 있으면 개발부터 진행하지 않는다.
- 먼저 충돌 원인을 분리하고 우선 기준을 결정한 뒤, 어떤 정본을 수정해야 하는지 판정한다.
- 기준을 정하는 역할과 실제 작업을 수행하는 역할을 분리한다.
- 팀/검증창이 많아 해석 분기 위험이 커지면 분업을 축소하고 단일 운영창 중심으로 전환한다.
- 검증창은 독자 해석·수정·최종 PASS 선언을 하지 않으며, 최종 운영판정은 실제 작업 증거를 가진 운영창에서 한다.

## 4. 사용자 역할
- 사용자는 관찰자다.
- 문서 조합, 기준 선택, 개발 방식, 어떤 작업창을 써야 하는지를 사용자가 외우거나 직접 설계하게 하지 않는다.
- 현재 상황과 정본을 먼저 회수해 필요한 경로를 안내한다.
- 사용자의 `계속/진행/다음` 반복 입력이나 수동 전달이 전제되는 구조는 재설계 대상으로 본다.

## 5. 승계
- 34번 대화창이 무거워지거나 새 창으로 교체되어도 34번 역할은 종료되지 않는다.
- `34번`은 단순 채팅 인스턴스 번호가 아니라 기준관리 역할명으로 취급한다.
- 새 34번 대화창은 이 CENTRAL MASTER와 최신 checkpoint를 먼저 로드하고 이어간다.
- 사용자가 인계문을 직접 작성·복사·붙여넣는 것을 기본 운영으로 요구하지 않는다.

## 6. 역사기록 흡수 원칙
- 278개 역사기록과 USB 자산은 그대로 정본으로 복사하지 않는다.
- 현재 역할과 실제 증거에 맞는 정상 DIFF만 흡수한다.
- 과거 assistant의 근거 없는 PASS/완료/진행률, 샘플, 임시 구조, 조각 패치, 중복 규칙, 폐기된 기준은 정본에 승격하지 않는다.
- 이미 GLOBAL/CENTRAL에 반영된 공통규칙은 SKIP_REUSE한다.
- 껍데기/미검증 자료는 `SHELL_OR_STALE` 또는 `HOLD_UNKNOWN`으로 남기고 canonical 흡수를 금지한다.

## 7. 역사 소스에서 확인된 고유 역할
- 역사 기록은 34번을 `도구 개발창이 아니다`, `기준 관리 / 보완사항 / 문서 / 인계문 / 개발 방식 관리 전용`, `사령부 역할`로 명시한다.
- 실제 개발은 1번·6번·13번 및 신규 TOOL 작업창 등 별도 작업창에서 수행한다.
- 34번과 작업창은 서로 대신하지 않고 분리 운영한다.

## 8. 상태
- 278-file historical numbered-group canonicalization: COMPLETE
- 분류: `INDEPENDENT_OPERATING_CHAT / NON-TOOL`
- 별도 실행 TOOL repo 생성: 금지/불필요
- CENTRAL MASTER 생성: COMPLETE
- 실행 기능 COMPLETE를 의미하지 않음. 이 MASTER는 운영역할 정본화 완료만 의미한다.

## Reopen gate
TOOL034_REOPEN = NEW_CRITERIA_OR_ROLE_CONFLICT_ONLY
RETEST_UNCHANGED_COMMON_RULE = FORBIDDEN
