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

## USB 기존자료 교차검증 + 정상자료 승격 게이트 — REQUIRED
- TOOL044가 READY_COMPONENT를 대상 TOOL/대화창에 실제 장착하고 시험할 때, 그 대상과 직접 관련된 USB/실사용폴더의 기존 자료가 있으면 이를 별도의 실전 검증 입력·비교 근거로 함께 사용한다.
- 단, USB 전체를 전수검색하지 않는다. 대상 TOOL 번호·기능·파일명·현재 오류·MASTER/checkpoint와 직접 관련된 자료만 좁게 조회한다.
- USB 자료는 오래된 정상본, 중간개발본, 껍데기, 샘플, 실패본, 중복본이 섞여 있을 수 있으므로 존재 자체를 신뢰하지 않는다.
- USB에서 찾은 자료는 최소한 `현재 MASTER/기대동작 대조 → 실제 실행 또는 관련 기능 시험 → EXPECTED↔ACTUAL → 직접 영향 회귀`를 통과해야 정상자료 후보가 된다.
- 파일 존재, 이름 유사, 최신 날짜, 큰 용량, 코드 문자열, 화면이 열림만으로 정상본으로 판정하지 않는다.
- 껍데기/샘플/기능 미연결/실행실패/기대동작 불일치/출처불명/중복 열화본은 `SHELL_OR_INVALID`로 분류하고 GitHub canonical MASTER나 VERIFIED_COMPONENT_REGISTRY로 승격하지 않는다.
- 정상 검증된 자료만 해당 TOOL/대화창의 GitHub 정본에 필요한 범위로 옮기고, 해당 TOOL MASTER/checkpoint/registry에 출처·검증근거·버전/해시·적용범위를 남긴다.
- USB 원본은 GitHub 승격 성공 전 삭제·덮어쓰기하지 않는다. GitHub commit/push 및 remote read-back PASS 후에야 canonical 승격 완료로 본다.
- USB 자료를 통째로 GitHub에 복사하지 않는다. 정상 판정된 실제 운영 코드·규칙·fixture·golden input/output·증거 중 정본 유지에 필요한 것만 최소 승격한다.
- 외부 READY_COMPONENT와 USB 기존자료가 같은 기능을 제공하면, 현재 WIC VERIFIED/PASS 자료를 먼저 재사용하고 그 자료가 껍데기이거나 불충분할 때만 TOOL044 외부부품을 사용한다.
- TOOL044 부품 장착 테스트는 가능하면 `새 부품 단독 sandbox PASS → USB 기존 정상자료/실제 입력 교차검증 → 대상 TOOL 통합 PASS → GitHub 정본 승격 → 실사용폴더 배포 → 배포본 재시험` 순서로 수행한다.
- USB 자료 정리 자체를 목적으로 전체 폴더 청소를 벌이지 않는다. 각 실제 TOOL 작업 중 관련 자료가 발견될 때 증분적으로 검증·승격한다.
- 검증되지 않은 USB 자료를 MASTER에 합치거나, MASTER에 적었다는 이유만으로 실제 코드/자료가 정상이라고 판정하는 것은 FAIL이다.
USB_RELATED_DATA_NARROW_SCAN_ONLY = REQUIRED
USB_WHOLE_SCAN = FORBIDDEN
USB_FILE_EXISTS_IS_NOT_TRUST = TRUE
USB_SHELL_OR_INVALID_BLOCK = REQUIRED
USB_NORMAL_DATA_REQUIRES_ACTUAL_TEST = TRUE
USB_TO_GITHUB_PROMOTION_REQUIRES_PASS = TRUE
USB_TO_MASTER_PROMOTION_REQUIRES_EVIDENCE = TRUE
USB_SOURCE_PRESERVE_UNTIL_REMOTE_VERIFIED = REQUIRED
PROMOTE_ONLY_VERIFIED_CANONICAL_MATERIAL = REQUIRED
READY_COMPONENT_USB_CROSS_VALIDATION = REQUIRED_WHEN_RELEVANT

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
