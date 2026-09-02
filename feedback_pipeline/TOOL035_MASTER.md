# TOOL035 MASTER — 월드 운영시스템 통합

상태: ACTIVE / INCREMENTAL VERIFIED-INTEGRATION
기준일: 2026-09-02

WIC 공통 운영규칙은 `WIC_GLOBAL_OPERATING_RULES.md`를 먼저 로드한다. 이 문서는 TOOL035 고유 통합 계약만 보관한다.

## 1. 목적
- 기존 WIC TOOL에서 실제 PASS/VERIFIED된 기능만 최소 연결하여 운영 인계를 단순화한다.
- 새로운 거대 시스템이나 개별 TOOL 복제품을 만들지 않는다.
- 미완성/HOLD 기능을 연결 가능한 기능으로 승격하지 않는다.
- WIC에서 반복적으로 직접 재개발하던 공통 문제는, 이미 외부에서 널리 사용되고 검증된 오픈소스/라이브러리/표준 컴포넌트를 먼저 조사·검증하여 재사용 가능한 부품으로 편입한다.
- 목표는 개별 TOOL의 WIC 고유 규칙만 직접 만들고, 파일처리·스키마검증·상태관리·큐·체크포인트·재시도·로깅·행추적·워크플로 연결·테스트 하네스 같은 공통 기반은 검증된 부품을 우선 재사용하여 Work 시간/크레딧 낭비를 줄이는 것이다.

## 2. 통합 순서
### 2-1. 기존 WIC 내부 PASS 부품
`검증된 개별 TOOL → 최소 연결 manifest → integration gate 실행 → FIRST_VALIDATION 1회 → PASS 범위만 유지`

### 2-2. 외부 검증 부품
반드시 아래 순서를 지킨다.
`외부 부품 후보 → 유지보수 상태/라이선스/실사용 사례 확인 → WIC 입력·출력 계약 적합성 확인 → 작은 샌드박스 시험 → 어댑터로 기존 WIC TOOL에 연결 → 직접 영향 회귀테스트 → PASS → manifest 등록 → remote read-back`

순서 생략 금지. 외부에서 유명하거나 많이 쓰인다는 이유만으로 즉시 본체에 결합하지 않는다.

## 3. 최초 연결 범위
- TOOL012 runtime commit `aa9cc2e89726a4b388b148067f6dc4be40a0599e`: 정적 서브사이트의 mailto/HTTPS 자료 CTA 생성 PASS.
- TOOL014 runtime commit `ae41bc0c93492d940df90049d894b19deab2ebaf`: 위험 CTA 차단 및 `WIC_SAFE_CHANGE autoDeploy=false` manifest 생성 PASS.
- 각 TOOL의 GitHub Pages 비활성/라이브 배포 HOLD는 그대로 보존하며 통합 완료로 오인하지 않는다.

## 4. 안전 계약
- manifest의 remote commit/blob read-back이 없는 구성요소는 READY에 포함하지 않는다.
- source TOOL 전체 상태와 재사용 가능한 PASS scope를 분리한다.
- 실제 자동배포, 라이브 홈페이지 변경, DB/API 연결은 현재 범위가 아니다.
- 실패 시 해당 연결만 HOLD하고 다른 검증된 TOOL 상태를 변경하지 않는다.
- 외부 부품은 WIC 본체 코드를 대체하거나 전체 재설계하는 방식이 아니라 어댑터/경계층으로 연결한다.
- 라이선스 불명, 유지보수 중단, 보안 위험, 실제 사용사례 부족, 입력·출력 계약 불일치가 있으면 HOLD한다.
- USB/과거 산출물에서 껍데기와 정상 구조를 분리하듯, 외부 후보도 `후보 → 검증 → PASS 자산 → 저장소/MASTER 승격` 단계를 거친다.
- 이미 검증된 부품은 이후 TOOL041/042/013/002/006 등에서 SKIP_REUSE하고 같은 공통부를 다시 만들지 않는다.

## 5. 외부 부품 레지스트리 최소 필드
각 승격 후보는 최소 다음을 기록한다.
- component_id / 이름 / 공식 저장소
- 해결하는 공통 문제
- 유지보수 상태(최근 release/commit 등)
- 라이선스와 WIC 사용 가능 여부
- 실사용/채택 근거
- 보안/의존성 위험
- WIC 입력 contract / 출력 contract
- sandbox test input / independent expected / actual / compare
- adapter 위치
- 연결 대상 TOOL
- 영향 회귀테스트 결과
- PASS/HOLD/REJECT
- 저장 commit / remote read-back / SKIP_REUSE 범위

## 6. 첫 실증 원칙
- 전체 WIC를 한꺼번에 바꾸지 않는다.
- 첫 실증은 반복 Work 비용이 큰 실제 끊김 1~2개만 잡는다.
- 우선 후보: TOOL041↔TOOL042의 실제 연결/상태전달/재개 구조, TOOL013의 파일·검증 공통 경로.
- 다음 후보: TOOL002, TOOL006.
- 실증 전후 `Work 투입 횟수 / 수정시간 / 재발횟수 / 테스트시간 / 크레딧`을 비교하여 실제 절감 효과가 확인된 경우에만 확장한다.

## 7. 대화창/이름 운영
- 새 TOOL 번호나 새 repo를 임의 생성하지 않는다.
- 이 목적은 기존 TOOL035의 역할과 직접 일치하므로 canonical 도구명은 `TOOL035 — 월드 운영시스템 통합`을 유지한다.
- 별도 대화창이 필요하면 식별용 제목만 `35번 월드 운영시스템 통합 — 외부 검증부품 조립`으로 사용할 수 있으나, TOOL035 자체를 새 이름/새 번호로 갈아치우지 않는다.

## 8. canonical
- 통합 상태: `feedback_pipeline/tool035_verified_integration.json`
- 실행 gate: `feedback_pipeline/tool035_verified_integration.py`
- 새 repo 생성 금지. CENTRAL 기존 저장소를 canonical로 사용한다.
