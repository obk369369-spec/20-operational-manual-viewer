# WIC TOOL044 PRODUCTION EXECUTION BLOCK

상태: ACTIVE / REQUIRED
적용대상: TOOL044 및 TOOL044가 부품을 장착하는 모든 WIC TOOL

## 최상위 목적
TOOL044는 샘플·시범·후보목록·MASTER 문서만 만드는 도구가 아니다.
TOOL044가 만들어지는 즉시 실무에 투입되어야 하며, 현재 WIC TOOL에서 실제로 반복 오류·미완료·공통구조 문제가 발생하는 기능에 필요한 외부의 완성·공유·실사용·검증된 부품을 실제로 가져와 대상 TOOL에 장착하고, 검증하고, GitHub 정본 반영과 실제 사용폴더 배포 및 배포본 재검증까지 끝내야 한다.

## 즉시 실무투입 강제규칙
- TOOL044 자체 완성의 성공조건은 샘플 제작이나 검색 기능 시연이 아니다.
- 최소 1개 실제 WIC TOOL의 실제 문제에 대해 READY_COMPONENT를 가져와 실제 장착·테스트·배포까지 성공하거나, 강제 상한 내에서 NO_READY_COMPONENT/HOLD_EXTERNAL로 근거 있게 종료해야 한다.
- 단계별 문서작성만 조금씩 진행하며 실제 장착과 배포를 다음 Work로 미루는 방식은 금지한다.
- 현재 Work 시간 안에서 가능한 범위는 실제 실무 처리까지 연속 진행한다.
- 이미 검증된 TOOL044/대상 TOOL 결과는 SKIP_REUSE하고 다음 실제 문제로 이동한다.

## TOOL044 실제 작업 흐름 — REQUIRED
현재 CENTRAL/MASTER/ledger/checkpoint의 OPEN·HOLD·반복오류 중 TOOL044 적용 가능한 공통구조 문제 확인
→ 기존 WIC VERIFIED_COMPONENT 우선 재사용
→ 없으면 외부 완성·실사용·검증·무료/로컬 부품을 좁게 검색
→ 라이선스·유지보수·실사용·보안·의존성·무수정 사용 가능 여부 검증
→ 독립 sandbox에서 실제 기능 EXPECTED↔ACTUAL 시험
→ 충분한 첫 PASS 후보에서 검색 즉시 종료
→ 대상 WIC TOOL에 외부부품 자체 수정 없이 실제 장착
→ 대표 실제 업무입력 실행
→ 실제 버튼·입력·다운로드·재열기 등 관련 조작 실행
→ EXPECTED↔ACTUAL 비교
→ 영향범위 회귀
→ PASS
→ 대상 TOOL GitHub commit/push/remote read-back
→ 대상 TOOL 실제 사용폴더 배포
→ 배포된 복사본 자체 재실행·대표 E2E 재시험
→ DEPLOYED_PASS
→ SAFE_CHECKPOINT
→ VERIFIED_COMPONENT_REGISTRY 저장
→ 시간이 허용되고 차단이 없으면 다음 적용 가능한 실제 TOOL 문제로 진행

## 관찰자 모드 — USER INTERVENTION FORBIDDEN BY DEFAULT
- 사용자는 관찰자다.
- 후보 선택, 테스트 실행, 버튼 클릭, 파일 복사, 배포, 재시도 선택, 결과 대조를 사용자에게 중간 작업으로 넘기지 않는다.
- 자동 가능한 작업은 Work/TOOL044가 끝까지 수행한다.
- 사용자에게 중간 승인·테스트·계속 버튼을 반복 요구하는 방식은 FAIL이다.
- 플랫폼 강제 승인, MFA, 물리기기 조작처럼 자동화가 기술적으로 불가능한 행동만 USER_ACTION_QUEUE에 모은다.
- USER_ACTION_QUEUE가 있어도 가능한 다른 작업은 계속 진행한다.
- 불가피한 사용자 행동은 가능한 한 마지막에 한꺼번에 요청한다.

## 모든 TOOL 공통 배포 완료조건 재확인
TOOL044 자체와 TOOL044가 수정·개선하는 모든 대상 TOOL은 다음을 통과하기 전 COMPLETE가 아니다.
실제 도구 구현/변경
→ 최소 충분 실제 테스트
→ EXPECTED↔ACTUAL
→ 영향 회귀
→ PASS
→ 해당 TOOL canonical MASTER/정본
→ GitHub commit/push
→ remote read-back
→ 실제 사용폴더 배포
→ 배포본 자체 재실행·재시험
→ DEPLOYED_PASS
→ SAFE_CHECKPOINT

샘플만 생성 = 미완성
MASTER만 생성 = 미완성
registry만 생성 = 미완성
GitHub 저장만 완료 = 미완성
로컬 개발본 PASS만 완료 = 미완성
실제 사용폴더 복사만 하고 재시험 없음 = 미완성
배포본 재검증 없는 COMPLETE = FAIL

## 단계별 지연 금지
- TOOL044 구축을 구조설계 → 후보목록 → 샘플 → 나중 장착 → 나중 테스트 → 나중 배포처럼 여러 Work로 잘게 쪼개지 않는다.
- 이것이 실제 업무 투입을 늦추는 경우 즉시 실무형 연속 실행으로 전환한다.
- TOOL041/TOOL042처럼 결과가 들쑥날쑥하거나 기존 도구에서 반복오류가 지속되는 경우, WIC 고유 판단이 아닌 공통구조 문제는 TOOL044 적용 후보로 우선 검토한다.
- 단, 전체 대화·전체 파일·전체 TOOL 전수검색은 금지한다. 현재 MASTER/ledger/checkpoint와 직접 관련된 오류 근거만 좁게 사용한다.
- WIC 고유 업무판단·고객판단·TOC 의미판단 자체를 외부부품으로 대체하지 않는다. TOOL044는 그 판단이 안정적으로 실행되게 하는 공통 바깥구조를 가져오는 역할이다.

## 강제 상태 플래그
TOOL044_SAMPLE_ONLY = FAIL
TOOL044_MASTER_ONLY = FAIL
TOOL044_REGISTRY_ONLY = FAIL
TOOL044_MUST_ENTER_REAL_OPERATION = TRUE
REAL_WIC_TOOL_COMPONENT_ACQUISITION = REQUIRED
REAL_COMPONENT_INTEGRATION = REQUIRED
REAL_BUSINESS_INPUT_TEST = REQUIRED
TARGET_TOOL_GITHUB_READBACK = REQUIRED
TARGET_TOOL_ACTUAL_FOLDER_DEPLOY = REQUIRED
DEPLOYED_COPY_RETEST = REQUIRED
OBSERVER_MODE = REQUIRED
USER_INTERMEDIATE_WORK = FORBIDDEN_BY_DEFAULT
USER_ACTION_QUEUE = REQUIRED_FOR_UNAVOIDABLE_ACTIONS
STEPWISE_DELAY_WITHOUT_REAL_DEPLOY = FORBIDDEN
NEXT_APPLICABLE_TOOL_CONTINUE_WHEN_POSSIBLE = REQUIRED
