# WIC WORK COMMON EXECUTION BLOCK

상태: ACTIVE / REQUIRED
목적: 현재 작업 중인 TOOL에서 반복되는 공통 실행을 매번 새로 조사·설계·질문하지 않고 재사용하여 크레딧과 사용자 작업을 줄인다.

## 최상위 원칙
- 이 블록은 모든 Work TOOL 작업 지시문에 기본 포함된 것으로 취급한다.
- 사용자가 폴더 경로, 배포 위치, GitHub 정본 위치, checkpoint 위치를 매번 다시 알려주게 하지 않는다.
- 현재 작업 중인 TOOL 하나만 대상으로 기존 canonical pointer / repo / checkpoint / 배포 경로 / 로컬·USB 운영 경로를 좁게 회수한다.
- WIC 전체 전수조사, 전체 USB 조사, 전도구 재검증은 금지한다.
- 이미 PASS / VERIFIED / REMOTE_VERIFIED된 공통 절차·부품은 SKIP_REUSE한다.
- 같은 공통 작업을 TOOL마다 새로 개발·재설계·재검증하지 않는다.

## 공통 실행 순서
1. CURRENT_TOOL_SCOPE_LOCK
   - 현재 지정 TOOL만 연다.
   - 다른 TOOL은 현재 TOOL이 실제 BLOCKED/HOLD로 확정된 경우에만 이동한다.

2. CANONICAL_POINTER_RESOLVE
   - CENTRAL registry → 기존 GitHub repo → latest checkpoint → 현재 TOOL 관련 Library/USB handoff 순서로 좁게 확인한다.
   - 기존 정본이 있으면 그대로 재사용한다.
   - 새 repo, 새 복제품, 임의 새 폴더 생성 금지.
   - canonical pointer가 없다고 즉시 종료하지 말고 현재 TOOL 범위에서만 복구 가능한 기존 위치를 좁게 확인한다.

3. PATH_AUTO_RESOLVE
   - 폴더 경로·배포 경로·정본 경로·실행 경로를 사용자에게 매번 질문하지 않는다.
   - 기존에 검증된 경로 규칙과 해당 TOOL의 기존 경로를 자동 재사용한다.
   - 경로가 충돌하거나 실제 근거가 없을 때만 HOLD_PATH_UNRESOLVED로 남긴다.

4. VERIFIED_USB_CANONICALIZATION
   - 현재 작업 TOOL의 USB 자료만 scoped 확인한다.
   - CANONICAL_NORMAL / 실제 검증 자료만 기존 GitHub canonical repo에 흡수한다.
   - HOLD_UNKNOWN / SHELL / DUPLICATE / OBSOLETE / STALE / 미검증 자료는 업로드 금지.
   - 새 repo·중복 보관소·검증본 복제 폴더 생성 금지.
   - commit + REMOTE_HEAD + remote read-back 증거가 있는 자산만 USB_DELETE_READY 후보.
   - 실제 USB 삭제는 별도 명시적 승인 전 금지.

5. COMMON_DEPLOY
   - 배포 방식과 경로를 TOOL마다 처음부터 다시 조사하지 않는다.
   - 기존 PASS된 배포 구조가 있으면 입력값(repo/path/artifact)만 바꿔 재사용한다.
   - 정본 확인 → 기존 배포경로 재사용 → 배포 → 변경범위 FIRST_VALIDATION 1회 → 실행 증거 저장.
   - GitHub Pages/Actions 등 기존 배포 수단이 있으면 우선 재사용한다.
   - 배포 설정이 비활성이고 현재 권한으로 활성화 가능하면 같은 현재 TOOL 범위에서 처리한다.
   - 권한/플랫폼상 불가능할 때만 BLOCKED_EXTERNAL + 정확한 RESUME_TRIGGER를 남긴다.
   - 단순 UI 404를 이유로 새 repo/새 배포 구조를 만들지 않는다.

6. COMMON_GITHUB_CANONICALIZE
   - 변경 후 commit → REMOTE_HEAD → remote read-back을 공통 절차로 수행한다.
   - 같은 절차를 TOOL마다 새로 설계하거나 사용자에게 확인시키지 않는다.

7. FIRST_VALIDATION_ONCE
   - 새로 변경된 범위만 최초 검증 1회 수행한다.
   - 동일 조건·동일 코드의 PASS 범위 재검증 금지.
   - 같은 실패를 같은 방법으로 반복 패치·재실행 금지.

8. CENTRAL_REGISTER
   - canonical pointer / 상태 / commit / blob / validation evidence / HOLD·BLOCKED / RESUME_TRIGGER를 기존 CENTRAL registry에 갱신한다.
   - 새 중앙 파일·중복 registry를 만들지 않는다.

9. COMMON_CLOSE
   - COMPLETE / REMOTE_VERIFIED 또는 HOLD / BLOCKED_EXTERNAL / BLOCKED_CANONICAL_NOT_FOUND 중 실제 증거로 닫는다.
   - COMPLETE된 기존 범위는 SKIP_REUSE.
   - SAFE_CHECKPOINT / NEXT_START / 증거를 남긴다.

## 반복 공통작업 승격 규칙
- 현재 실제 TOOL 작업 중 동일 작업이 반복되면 별도 전수조사 없이 REUSE_CANDIDATE로 기록한다.
- 실제 PASS된 뒤 공통 실행부로 승격한다.
- 첫 등장: 현재 TOOL에서 최소 구현.
- 두 번째 반복: 공통화 후보.
- 세 번째 이상 반복: 검증된 공통 실행부 우선 재사용.
- 공통화를 위해 별도 대형 프로젝트나 WIC 전체 재설계를 시작하지 않는다.

## 현재 공통화 우선 대상
- canonical/path 자동 해석
- 기존 배포 경로 자동 재사용 및 배포
- GitHub commit / REMOTE_HEAD / remote read-back
- CENTRAL canonical pointer 등록
- 변경범위 FIRST_VALIDATION 1회
- 현재 TOOL USB 정상자산만 GitHub 정본화
- COMPLETE/HOLD/BLOCKED + RESUME_TRIGGER 기록
- checkpoint/handoff 저장

## 향후 PASS 부품 자동 재사용 후보
- watchdog / liveness
- 안전 자동복구 1회
- immutable original_run_id / transaction identity
- 실패 후에도 살아남는 상태기록
- event ingress → classify → dedup → CENTRAL write
- 공통 E2E evidence packet

## 금지
FULL_AUDIT = FORBIDDEN
FULL_USB_AUDIT = FORBIDDEN
REBUILD_VERIFIED_COMPONENT = FORBIDDEN
RETEST_UNCHANGED_VERIFIED_COMPONENT = FORBIDDEN
NEW_REPO_FOR_REUSE = FORBIDDEN
DUPLICATE_VERIFIED_STORAGE = FORBIDDEN
USER_REPEATED_PATH_INPUT = FORBIDDEN
USER_REPEATED_DEPLOY_INSTRUCTION = FORBIDDEN
SAFE_WORK_EXHAUSTED_BECAUSE_COMMON_PATH_NOT_REUSED = FORBIDDEN

## 사용자 역할
USER_ROLE = OBSERVER_ONLY
사용자는 경로·배포법·checkpoint·정본 위치를 매 작업마다 다시 설명하지 않는다.
플랫폼상 본인 승인/MFA/권한 변경이 필수인 경우에만 최소 1회 행동을 요청한다.
