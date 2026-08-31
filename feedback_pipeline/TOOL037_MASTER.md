# TOOL037 MASTER — 37번 메타데이터 작업

상태: ACTIVE / TOOL-SPECIFIC MASTER / CANONICAL_REPO_UNRESOLVED
정본 위치(현재): CENTRAL `feedback_pipeline/TOOL037_MASTER.md`
공통 운영원본: `WIC_GLOBAL_OPERATING_RULES.md`
공통 실행블록: `feedback_pipeline/WIC_WORK_COMMON_EXECUTION_BLOCK.md`

## 1. 정체성
- TOOL037은 메타데이터 제작·통합 검증 도구/업무다.
- TOOL013은 Excel 자동 업로드 전용이며 TOOL037과 결합하지 않는다.
- TOOL037은 발행사 원본 메타데이터를 해석하고, 홈페이지 표준 입력 구조로 변환·검증하여 후단 업로드에 넘기는 역할을 담당한다.

## 2. 입력 및 출력 원칙
- 발행사별 원본 구조는 서로 다를 수 있으므로 원본 해석과 홈페이지 표준화 단계를 분리한다.
- 기본 흐름: `원본 메타데이터 해석 -> 홈페이지 표준 양식 변환 -> 검증 -> 후단 전달`.
- 원본에 없는 값을 임의 생성하지 않는다. 근거 불충분 항목은 HOLD/공란으로 둔다.
- 홈페이지 입력용으로 정리된 산출물은 원본과 구분하기 위해 사용자 확정 명명 규칙인 `원본파일명 - 월드입력` 형식을 사용한다.

## 3. 컬럼 매핑
- 컬럼 매핑은 단순 추론으로 확정하지 않는다.
- 역사 규칙의 우선 순서: 동일 컬럼명 -> 유사 컬럼명 -> 실제 데이터 내용 -> 샘플 비교 -> HOLD.
- 의미가 불명확하거나 여러 컬럼에 중복 대응될 수 있으면 HOLD로 남기고 근거 없는 자동 확정을 금지한다.

## 4. 날짜 및 표준화
- 발행사별 표시 형식이 달라도 홈페이지용 표준 형식으로 정규화한다.
- 역사 규칙에서 날짜 표준 예시는 `YYYY-MM-DD`다.
- 실제 셀의 날짜값이 존재하면 그 실제 값을 우선한다.
- 연월만 존재하는 경우의 과거 `YYYY-MM-01` 규칙은 활성 데이터/홈페이지 기준과 충돌하지 않는지 확인한 변경 범위에서만 사용한다. 근거가 불충분하면 HOLD한다.

## 5. 발행사별 규칙 누적
- 기존 공통 규칙을 우선 재사용하고, 새 발행사에서만 발생하는 고유 예외를 DIFF ONLY로 추가한다.
- 한 발행사에서 새 규칙이 확인되면 다른 발행사에 기계적으로 전파하지 않는다. 동일/유사 구조와 실제 데이터 근거가 확인되는 영향 범위만 검증한다.
- 기존 PASS 영역 전체 재검증은 금지하며, 새 규칙이 영향을 주는 범위만 FIRST_VALIDATION 1회 수행한다.

## 6. 껍데기 차단
- 과거 assistant가 만든 샘플/예시/가짜 값/근거 없는 '최종본' 주장은 정본 증거가 아니다.
- 실제 원본 파일, 사용자 확정 규칙, 변환 결과, 검증 증거가 연결되지 않으면 PASS/COMPLETE로 승격하지 않는다.
- USB/역사자료는 `CANONICAL_NORMAL / SHELL_OR_STALE / HOLD_UNKNOWN`으로 분류하고 검증된 정상 DIFF만 흡수한다.

## 7. GitHub/CENTRAL 관계
- 현재 접근 가능한 GitHub 범위에서 TOOL037 전용 기존 canonical repo를 확인하지 못했다.
- 새 repo는 역사자료 정리를 위해 임의 생성하지 않는다.
- 현재는 CENTRAL에 TOOL037 정본 규칙과 상태를 보존한다.
- 이후 실제 TOOL037 코드/실행 자산의 기존 repo가 확인되면 이 MASTER를 포인터/정본 관계로 연결하고, 중복 repo를 만들지 않는다.

## 8. 역사 소스에서 확인된 핵심
- `37번 메타데이터 작업` 계열 기록에서 통합규칙관리 파일과 텍스트 운영규칙을 함께 유지하려는 구조가 확인된다.
- Bizwit 등 개별 발행사 처리에서 공통 규칙을 먼저 적용하고 새 예외만 추가하는 방향이 확인된다.
- TOOL037과 TOOL013 분리는 CENTRAL 기존 기록과 일치한다.

## 9. 상태
- 278-file historical numbered-group canonicalization: COMPLETE
- TOOL037 제품/런타임 전체 COMPLETE를 의미하지 않음.
- CANONICAL_REPO: UNRESOLVED / no new repo created
- 기존 저장소 또는 실제 실행자산 발견 시 연결만 수행한다.

## Reopen gate
TOOL037_REOPEN = REAL_USE_NEW_FAILURE_OR_CANONICAL_REPO_FOUND
RETEST_UNCHANGED_SCOPE = FORBIDDEN
