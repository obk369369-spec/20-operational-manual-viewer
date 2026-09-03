# WIC WORK END-TO-END COMPLETION GATE

상태: ACTIVE / REQUIRED
목적: 한 번에 끝까지 처리해야 하는 WIC 작업을 여러 Work로 찔끔찔끔 분할하여 크레딧과 시간을 낭비하는 것을 차단하고, 실제 배포·배포본 검증까지 끝난 경우에만 완료로 판정한다.

## 최상위 원칙
- 한 번에 구현→검증→정본반영→실사용배포→배포본재검증까지 이어질 수 있는 작업은 임의로 여러 Work로 쪼개지 않는다.
- MASTER 작성, 후보 탐색, 샘플, sandbox PASS, 로컬 개발 PASS, GitHub push만 하고 종료하지 않는다.
- 사용자가 다음 Work를 다시 열어야 실제 배포나 정상작동 검증이 끝나는 구조는 기본 FAIL이다.
- 작업 시작 전에 현재 Work의 남은 시간·크레딧·필수 단계·외부차단 가능성을 보고 `이번 Work에서 배포본 PASS까지 현실적으로 완주 가능한가`를 먼저 판정한다.
- 완주 가능하면 중간 보고 때문에 멈추지 않고 끝까지 실행한다.
- 완주가 구조적으로 불가능하거나 남은 시간/크레딧으로 안전한 배포본 검증까지 도달할 수 없다고 판단되면, 새 개발·새 후보검색·광범위 조사부터 시작하지 않는다. 먼저 범위를 축소하거나 기존 SAFE_CHECKPOINT에서 대기/HOLD하여 불필요한 반쪽 작업을 만들지 않는다.
- 단, 이미 시작된 변경이 있다면 기존 안정판을 훼손하지 않도록 현재 변경을 검증 가능한 안전 단위까지 마무리하거나 폐기하고, 미검증 상태를 배포하지 않는다.

## Work 시작 전 강제 완주 판정
각 Work는 실제 변경을 시작하기 전에 아래를 판정한다.
1. 구현/수정 범위
2. 실제 테스트 범위
3. EXPECTED↔ACTUAL 비교
4. 영향 회귀
5. GitHub commit/push/read-back
6. 실제 사용폴더 배포
7. 배포본 재실행/재시험
8. SAFE_CHECKPOINT
9. 사용자 승인/MFA/물리조작 같은 외부 차단
10. 남은 Work 시간·크레딧

판정:
- `CAN_FINISH_END_TO_END = TRUE` → 해당 작업을 중간 종료 없이 배포본 PASS까지 계속 실행.
- `CAN_FINISH_END_TO_END = FALSE` → 새 구현을 시작하지 말고 `HOLD_BEFORE_PARTIAL_WORK`로 중단 사유와 필요한 다음 단일 실행범위를 남김.
- 이미 수정 중인 경우 → 새 기능/후보를 추가하지 말고 현재 변경을 SAFE_CHECKPOINT 또는 원복 가능한 상태로 정리.

## 완료 판정 강제 게이트
아래 전체가 필요한 작업에서는 모두 완료되어야 COMPLETE다.
`실제 구현/수정 → 최소충분 실제 테스트 → 독립 EXPECTED → ACTUAL → EXPECTED↔ACTUAL → 영향 회귀 → PASS → canonical MASTER 반영 → GitHub commit/push → remote read-back → 실제 사용폴더 배포 → 배포본 실제 재실행/재시험 → DEPLOYED_PASS → SAFE_CHECKPOINT`

다음은 COMPLETE가 아니다.
- 계획 완료
- MASTER 작성 완료
- 코드 작성 완료
- 샘플 완료
- 후보 선정 완료
- sandbox PASS
- 로컬 PASS
- 테스트 파일 생성
- GitHub commit/push만 완료
- 실제 사용폴더에 복사만 완료
- 배포했다고 보고했지만 배포본을 실제 재실행/재시험하지 않음
- 사용자가 다음 Work에서 다시 열어야 배포/검증이 끝남

## 배포 허위완료 차단
- `배포 완료`는 실제 사용폴더의 배포본이 존재한다는 사실만으로 선언하지 않는다.
- 배포된 사본 자체를 다시 열고/실행하고 관련 대표 입력·버튼·다운로드·저장·재열기 등 실제 기능을 재시험해야 한다.
- 개발본 PASS와 배포본 PASS를 분리 기록한다.
- `DEPLOYED_PASS` 증거가 없으면 `배포 완료` 또는 `COMPLETE` 금지.
- GitHub와 실제 사용폴더가 다르면 해당 배포대상 파일의 정본 일치 여부도 확인한다.

## 크레딧 절약을 위한 분할 금지
- 같은 목표를 상태확인→설계→구현→테스트→배포처럼 불필요하게 여러 Work로 나누지 않는다.
- 매 Work마다 같은 MASTER/checkpoint/CENTRAL을 반복 로드하고 같은 판단을 반복하게 만드는 분할은 금지한다.
- 이미 PASS/VERIFIED된 결과는 `SKIP_REUSE`하고 다시 시험하지 않는다.
- 한 번의 Work에서 여러 필수단계를 연속 자동 실행할 수 있으면 하나로 묶는다.
- 중간 사용자 확인이 기술적으로 필요하지 않은데도 `계속할까요`, `다음 단계로 갈까요`, 테스트 버튼 클릭 등을 요구하지 않는다.

## 사용자 관찰자 모드
- 사용자는 중간 작업자가 아니라 관찰자다.
- 후보 선택, 테스트 실행, 버튼 클릭, 파일 복사, 배포, 재시도 판단을 사용자에게 넘기지 않는다.
- 플랫폼상 반드시 필요한 승인/MFA/물리기기 조작만 `USER_ACTION_QUEUE`에 누적한다.
- 불가피한 사용자 조작이 있어도 가능한 다른 작업은 계속 수행하고, 가능한 한 마지막에 한꺼번에 요청한다.

## 중간 미완료 방지
- Work가 시간/크레딧 부족 때문에 중간에서 끊길 가능성이 높아지면 새 기능·새 후보·새 범위를 시작하지 않는다.
- 현재 PASS 가능한 변경의 테스트→정본→배포→배포본 검증을 먼저 끝낸다.
- 배포본 검증까지 못할 가능성이 명확하면 안정판을 유지하고 `HOLD_BEFORE_PARTIAL_WORK`로 끝낸다.
- 미검증 변경을 실사용 폴더에 덮어쓰는 것은 금지한다.

## TOOL044 특별 적용
- TOOL044처럼 `정식 실행도구 자체 완성 + 실제 타 TOOL 적용 + 테스트 + 배포`가 하나의 실무 목적이면 이를 인위적으로 파일럿/샘플/후속 Work들로 분리하지 않는다.
- TOOL044 자체 정식 실행본, GitHub 정본, 실제 사용폴더, 배포본 재시험이 완료되어야 TOOL044 자체 COMPLETE다.
- TOOL044가 부품을 실제 대상 TOOL에 장착하는 작업도 대상 TOOL의 GitHub read-back + 실제 사용폴더 배포 + 배포본 재시험까지 한 실행흐름으로 처리한다.
- 첫 부품 PASS만으로 TOOL044 전체 COMPLETE를 선언하지 않는다.

## 강제 플래그
END_TO_END_FINISH_IN_ONE_WORK_WHEN_FEASIBLE = REQUIRED
WORK_PRECHECK_CAN_FINISH_END_TO_END = REQUIRED
PARTIAL_WORK_START_WHEN_UNFINISHABLE = FORBIDDEN
HOLD_BEFORE_PARTIAL_WORK = REQUIRED_WHEN_CANNOT_FINISH
MASTER_ONLY_COMPLETE = FORBIDDEN
SANDBOX_ONLY_COMPLETE = FORBIDDEN
LOCAL_PASS_ONLY_COMPLETE = FORBIDDEN
GITHUB_ONLY_COMPLETE = FORBIDDEN
COPY_ONLY_DEPLOYMENT_COMPLETE = FORBIDDEN
DEPLOYED_COPY_RETEST = REQUIRED
DEPLOYED_PASS_REQUIRED_FOR_COMPLETE = TRUE
FALSE_DEPLOYMENT_CLAIM = FAIL
UNNECESSARY_MULTI_WORK_SPLIT = FORBIDDEN
REPEATED_CONTEXT_RELOAD_WASTE = FORBIDDEN
SKIP_REUSE_EXISTING_PASS = REQUIRED
OBSERVER_MODE = REQUIRED
USER_INTERMEDIATE_OPERATION = FORBIDDEN_BY_DEFAULT
SAFE_CHECKPOINT_BEFORE_INTERRUPT = REQUIRED
TOOL044_END_TO_END_SPECIAL_GATE = REQUIRED
