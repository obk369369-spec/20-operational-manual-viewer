# WIC NEXT CHAT HANDOFF — 2026-10-11

## 0. 목적
이 파일은 현재 대화의 최신 결정사항을 다음 대화/Work가 사용자 재설명 없이 이어받기 위한 canonical handoff다.
사용자 = OBSERVER. USER_MANUAL_REPETITION=0.
기존 PASS/Evidence는 재사용하고, 광역 재검색·전체 재실행·중복개발을 금지한다.

## 1. 기준 저장소와 이전 checkpoint
- Repository: obk369369-spec/20-operational-manual-viewer
- 이전 보존 checkpoint: WIC-CP-20261010-18PCT-FINAL-PRESERVATION-HANDOFF
- 이전 기준 commit: f0d5533bf72b0fa491bf28107cece7ef0e17556a
- 기존 global rule: CONTROL_TOWER/ledger/evidence/WIC_GLOBAL_ROW_ISOLATION_AUTORECOVERY_RULE_20261010.md
- 이전 next root: USER_VISIBLE_OUTPUT_AUTONOMOUS_RECOVERY_AND_RECORD_IDENTITY
- Root A 24h: PENDING_NATURAL_TIME_DO_NOT_RESTART

## 2. 이미 보존된 Tool013 상태
- PREVIOUS VERSION:
  CONTROL_TOWER/work/tool013_user_output_closure/13번_V2_최종운영판.before.html
  blob SHA a787c475313efd709c67a65a04c5b4383ba0ba12
- CURRENT UNVERIFIED VERSION:
  CONTROL_TOWER/work/tool013_user_output_closure/13번_V2_최종운영판.html
  blob SHA e6253eda95e6676540138c88afcfbeae22dcc89a
- TOOL013 USER_USABLE_FINAL = HOLD
- AUTONOMOUS_RECOVERY = HOLD
- RECORD_IDENTITY_INTEGRITY = UNVERIFIED
- USER_MANUAL_REPETITION = FAIL
- 보존된 checkpoint commit: f0d5533bf72b0fa491bf28107cece7ef0e17556a

## 3. 실제 사용자 출력이 기존 PASS를 뒤집은 핵심 증거
사용자가 실제 Tool013을 실행한 뒤 내부 PASS와 다른 결과를 발견했다.
실제 사용자 출력은 내부 PASS label보다 우선한다.

확인된 실패/Negative Golden:
- USER_FORCED_MANUAL_VALIDATION
- BLOCK_WITHOUT_AUTONOMOUS_RECOVERY
- RECORD_IDENTITY_INTEGRITY_UNPROVEN
- PASS_CONTRADICTED_BY_ACTUAL_USER_OUTPUT
- CATEGORY_CODE_AS_DISPLAY_VALUE
- EXCEL_DATE_SERIAL_LEAKAGE
- WRONG_COLUMN_MAPPING
- BLANK_REQUIRED_OUTPUT
- OUTPUT_NOT_REOPENED
- CROSS_ROW_FIELD_MIXING
- DUPLICATE_RECORD
- MISSING_RECORD
- IDENTITY_SWAP

초기 실제 화면에서는 category code/비공식 표시값, Excel serial date, blank/field mapping 문제가 관찰되었다.
후속 버전은 오류를 탐지하고 correction XLSX를 생성했지만, "773행을 차단"하고 사용자가 오류필드/실제값/기대값/이유를 보고 직접 수정 후 재업로드하게 했다.
이는 오류탐지/설명은 가능해도 autonomous recovery와 observer-only 원칙에는 실패다.

## 4. 현재 요구되는 공통 오류처리 기능
'공통장치'란 여러 도구가 같이 재사용하는 공통 오류처리 기능을 뜻한다.
Tool013 전용 패치를 뜻하지 않는다.

모든 separable-record 업무에서:
문제 발견
→ 원인 자동판정
→ deterministic 오류 자동수정
→ 자동 재검증
→ 성공하면 usable output에 포함
→ 안전하게 자동수정 불가능하면 해당 record만 quarantine
→ 다른 정상 record는 계속 처리
→ 최종 파일 reopen/검증
→ Evidence

예:
1000 records = 980 normal + 15 auto-repaired + 5 quarantined
=> 995 usable + 5 quarantine.
사용자가 수백 행 Excel을 직접 수정하는 구조는 금지.

예외:
record identity/lineage가 깨져 cross-row contamination 위험이 있으면 unsafe affected final output을 차단한다.

## 5. Record Identity 불변식
각 record는 입력부터 최종까지 다음 identity를 유지해야 한다:
origin_file + origin_row + stable_record_id

순서는 바뀔 수 있으나 identity는 바뀌면 안 된다.
필수 검증:
- MISSING_RECORD_COUNT = 0
- DUPLICATE_RECORD_COUNT = 0
- IDENTITY_SWAP_COUNT = 0
- CROSS_ROW_MIX_COUNT = 0
- INPUT_RECORD_COUNT = FINAL_USABLE_COUNT + QUARANTINED_COUNT + 명시 허용 비업무 record

사용자가 본 correction workbook의 오류_원본행 숫자가 3,12,10,12...처럼 섞여 보이는 것 자체만으로 row mixing을 단정할 수는 없다.
여러 source file의 동일 origin_row가 있을 수 있기 때문이다.
따라서 origin_file + origin_row + stable_record_id 전체 tuple로 실제 무결성을 증명해야 한다.

## 6. 1차 Work — 먼저 이것만 실행
현재 최우선 root:
USER_VISIBLE_OUTPUT_AUTONOMOUS_RECOVERY_AND_RECORD_IDENTITY

42번에서 작성된 WIC 16번 ZERO-RECURRENCE / FAIL-CLOSED 최상위 실행지시와 위 root를 하나의 통합 실행으로 처리한다.

상위 원칙:
- ERROR MAY OCCUR, BUT UNDETECTED ERROR -> FINAL PASS 금지
- Evidence 없는 PASS 금지
- 부분완료를 전체완료로 보고 금지
- UNKNOWN/UNVERIFIED는 PASS 아님
- MASTER_FIXED != RUNTIME_FIXED
- FIXTURE_PASS != ACTUAL_E2E_PASS
- Negative Test + Recovery Test 필수
- Remote/functional read-back 필수
- False-Pass Attack 필수
- 기존 PASS 보호
- Work 중단 시 마지막 VERIFIED CHECKPOINT에서 재개

Preflight는 기존 Evidence를 재사용한다.
변경되지 않은 Gate를 다시 검사하지 않는다.
Preflight가 증명되지 않으면 대규모 개발/실행을 시작하지 말고 BLOCKED_BY_PREFLIGHT로 정확히 종료한다.

Tool013은 첫 actual Proof Case다.
알려진 Registry/Evidence/Handoff/current path에서 실제
"MarketsandMarkets Revamped Reports Metadata 17072025"
입력을 찾을 수 있으면 사용한다.
114 files / 823 rows는 실제 원본에서 재확인될 때만 확정 수치로 사용한다.
이를 찾기 위해 drive/storage 전체 광역검색은 금지한다.
실제 입력이 알려진 경로에서 접근 불가하면 ACTUAL_INPUT=HOLD로 남긴다.

Tool013 전체 재개발 금지.
기존 번역/18-category/date/mapping/validation/XLSX/download/recovery 기능을 재사용하고 없는 연결만 최소 구현한다.
773행을 Work가 수동 개별 수정하는 것도 금지한다.

실제 proof:
ACTUAL INPUT
→ UPLOAD
→ PROCESS
→ DETECT
→ AUTO-RECOVER
→ REVALIDATE
→ QUARANTINE ONLY UNRESOLVED
→ CONTINUE SAFE RECORDS
→ FINAL XLSX
→ DOWNLOAD
→ REOPEN
→ BUSINESS FIELD VALIDATION
→ RECORD IDENTITY VALIDATION

실제 XLSX에서 최소 상품명/한글명/1·2·3차카테고리/발행일/주요필드를 확인한다.

Tool013 HOLD 해제는 실제 증거로 다음 모두 PASS일 때만:
normal continue; deterministic auto-fix; auto-revalidation; unresolved-only quarantine; user mass Excel repair 0; identity tuple preserved; missing 0; duplicate 0; identity swap 0; cross-row mix 0; final XLSX reopen PASS; business-field compare PASS; Evidence PASS; Negative PASS; Recovery PASS; False-Pass Attack PASS; GitHub remote read-back PASS.

## 7. 42번 ZERO-RECURRENCE / FAIL-CLOSED 핵심을 축소해석하지 말 것
원문 지시의 모든 Gate 의미를 유지한다.
필수 실행 chain:
INPUT → IDENTITY → REGISTRY → LATEST MASTER → CURRENT REQUIREMENTS → FEEDBACK/FAILURE HISTORY → REQUIRED DATA → EXECUTION → AUTO-RECOVERY/ISOLATION → VALIDATOR → EVIDENCE → COMPLETION MATH → REGRESSION → READ-BACK → OUTPUT GATE → FINAL OUTPUT → OBSERVER REPORT.

동일 root recurrence이면 one-off patch 금지:
OLD PASS INVALIDATE → ROOT REOPEN → validator가 왜 못 막았는지 조사 → enforcement 수정 → Negative Fixture → RED → FIX → GREEN → Regression → NEW PASS.

## 8. 크레딧/반복작업 보호
금지:
- 3200건 전체 재스캔
- 2,105,850 enumeration 재실행
- D110415/F100k/USB262/D2/C one-shot 재실행
- C/D/F drive 광역검색
- USB 전체검색
- 과거 버전 전체 hunt
- Root A failover 재검사
- 24h natural-time 검증 restart
- 기존 유효 PASS blanket retest
- Tool013 full rebuild
- 773 rows 수동 수정
- 동일 E2E/Negative/Read-back을 두 지시가 요구한다는 이유로 중복실행
- 사용자에게 테스트/Excel수정/과거자료 재제출 요구

같은 segment 반복 실패:
원인 fingerprint → Evidence → safe rollback → checkpoint → exact next resume point.
무한 retry 금지.

## 9. 1차 Work 이후 2차 Work 계획
1차 Work 결과가 확정된 뒤에만 다음 지시를 만든다/실행한다.

2차 범위:
- Tool013 제외 주요 WIC 도구
- 기존 actual-input 대기 3건
- external-original 대기 1건
- 최근 1년간 WIC 도구/작업 전체

중요:
최근 1년 전체를 "전수 재실행"하지 않는다.
1년치는 Root Cause 발견 범위에 처음부터 포함한다.
실제 실행/E2E 우선순위는 주요 도구부터 한다.

흐름:
최근 1년 Registry/Evidence/Failure/Feedback의 알려진 canonical 자료
→ 동일/유사 Failure를 ROOT_FINGERPRINT로 최대한 병합
→ 기존 PASS + 영향 없음 = SKIP-REUSE
→ 주요 도구 대표 actual path 우선 검증
→ 최대 공통 Root 하나를 수정
→ 공통 해결책을 영향받는 나머지 도구에 재사용
→ impact-based validation만 실행
→ 개별 특수오류만 후순위.

즉:
6번/42번/과거 여러 도구가 같은 A 오류면 A를 각각 고치지 말고 공통 Root A 하나를 고친다.

## 10. 아직 남은 작업
- actual-input wait: 3
- external-original wait: 1
- Root A 24h: PENDING_NATURAL_TIME_DO_NOT_RESTART
이들은 1차 공통 auto-recovery/identity + Tool013 actual proof 이후 처리한다.
환경/크레딧이 부족하면 checkpoint 후 defer한다.

## 11. 저장/보고 원칙
각 최소 변경 단위:
CHANGE → TEST → EVIDENCE → COMMIT → REMOTE READ-BACK → CHECKPOINT

말로 "완료/반영/PASS" 금지.
실제 증거와 remote read-back이 있어야 한다.

최종 보고에는 최소:
PRE-WORK
COMMON AUTO-RECOVERY
ROW ISOLATION
RECORD IDENTITY
TOOL013 ACTUAL INPUT
INPUT/NORMAL/AUTO-REPAIRED/QUARANTINED/FINAL USABLE
MISSING/DUPLICATE/IDENTITY SWAP/CROSS-ROW MIX
FINAL XLSX REOPEN
USER MANUAL EXCEL CORRECTION
TOOL013 USER-USABLE
Negative/Recovery/Actual E2E/Regression
GLOBAL PROPAGATION
actual-input remaining
external-original remaining
24H
CHECKPOINT
GitHub commit
REMOTE READ-BACK
NEXT_ROOT
FINAL
을 포함한다.

## 12. 다음 대화가 해야 할 첫 행동
사용자에게 과거 설명을 다시 요구하지 않는다.
먼저 이 handoff와 최신 canonical checkpoint/evidence를 읽어 상태를 복구한다.
그 후:
(1) 1차 통합 Work 지시가 아직 미실행이면 그 지시를 기준으로 실행 준비/판단
(2) 실행 중이면 결과를 판정
(3) 완료되면 결과를 토대로 2차 지시문(13번 제외 주요도구 + 미완료 3+1 + 최근 1년 최대공통 Root 감사)을 작성한다.

새 대화는 이 handoff를 기준으로 이어가며, 이 파일 작성 자체를 runtime implementation PASS로 오인하지 않는다.

## 13. 2026-10-18 TOOL016 대화창 종료 증분 인계

상태: `CENTRAL_RESUME=PASS` / REMOTE READ-BACK 기준 종료 인계.
이 절은 앞선 handoff와 기존 PASS/Evidence를 폐기하거나 재검증하지 않고 최신 실행상태만 증분 추가한다.

### 복원 기준
- 복원 직전 기준 HEAD: `9849a39f01fa358558d2bb576f89103947454f78`
- resume loader 결과: `RESUME_LOADED`
- OPEN: 2
- HOLD: 4
- RUNNING: 0
- NEXT_WORK: 2
  1. `WIC-0702-SCOPED-RECOVERY`
  2. `WIC-PARALLEL-RESIDUAL-20260903`
- 사용자 checkpoint 수동 전달 횟수: 0

### 현재 작업 재개 원칙
- 오래된 로컬 checkpoint로 후퇴하지 않는다.
- 기존 `PASS / VERIFIED / REMOTE_VERIFIED / Evidence`를 정본으로 재사용하고 재처리·재수집·재검증하지 않는다.
- 과거 작업 재조사, 전체 저장소·드라이브·USB 재스캔, 완료 작업 재실행을 금지한다.
- NEXT_WORK는 canonical trigger와 실행계약이 실제 충족된 지점에서만 마지막 실제 완료지점부터 이어간다.
- 변화 없는 HOLD와 같은 원인·같은 방법의 실패는 다시 실행하지 않는다.

### USB 경계
- 현재 정상 연결 USB는 `D:`다.
- WIC 경로·checkpoint·Job Pack·Evidence는 특정 USB 드라이브 문자에 종속시키지 않는다.
- `D:`를 `I:`로 변경하지 않는다.
- USB 전체 스캔, 이동, 삭제, 재구성은 금지한다.
- 현재 TOOL/NEXT_WORK에 직접 필요한 알려진 경로만 좁게 읽는다.

### 병렬 획득·복구 실행 규칙
- 기존 검증 자산을 우선 재사용하고, 필요한 경우 외부의 완성형 Worker·Workspace·검증 부품 및 검증된 부품조합을 독립 lane으로 병렬 획득·검증한다.
- 동일 asset/root에는 기존 owner·lease·checkpoint를 재사용하고 중복 실행하지 않는다.
- 한 경로의 실패가 다른 독립 경로를 중단시키지 않는다. 실패 lane만 원인·증거·checkpoint와 함께 격리하고 나머지 독립 lane은 계속한다.
- 단일 후보·단일 Worker·단일 Workspace 실패를 전체 WIC 중지나 전체 ROOT 실패로 확대하지 않는다.
- 기존 Job Pack이 있으면 그대로 재사용하고 처음부터 다시 만들지 않는다.
- Job Pack은 최신 canonical 상태와 충돌하는 부분만 증분 갱신하며, 기존 target/assets/acceptance/evidence/checkpoint를 보존한다.
- 새 Job Pack·새 Worker·새 Workspace·새 파이프라인은 기존 자산으로 해결 불가능하다는 근거와 현재 scope authorization 없이는 만들지 않는다.
- 병렬 lane의 결과는 각자 Evidence와 remote read-back을 가진 뒤 CENTRAL canonical 상태에 합류한다.

### 정확한 다음 실행
- `WIC-0702-SCOPED-RECOVERY`: 저장된 정확한 source를 재사용한다. 복구 자체를 반복하지 말고 authoritative identity/material link와 허용된 실제 tool test path가 확보될 때만 재개한다.
- `WIC-PARALLEL-RESIDUAL-20260903`: 기존 policy restore와 Job Pack을 재사용한다. 허용된 local-browser test path 또는 concrete business handler/input이 확보된 독립 lane부터 진행하며, 다른 HOLD 때문에 전체를 중단하지 않는다.
- TOOL013/043 및 기존 완료 범위는 변경 직접 영향이 없으면 `SKIP_REUSE`한다.

### 2026-10-18 NEXT_WORK 실제 재개 시도 checkpoint
- 최신 CENTRAL loader: `RESUME_LOADED` at `c5ecfe0c5f9de4195a6499615d6bc39392ff368d`.
- 기존 Job Pack `feedback_pipeline/external_factory_job_pack_20261016.json`을 재사용했다. 새 Job Pack/Worker/Workspace는 만들지 않았다.
- `WIC-JP-ACTUAL-INPUT-BINDING`과 `WIC-JP-ASSEMBLY-OUTPUT-IDENTITY`의 TOOL013 lane에서 기존 실제 입력 경로와 운영본 경로를 복원했다.
  - 실제 입력: `D:\홈페이지 자료 입력\Metadata Sheet (Market Report)\MarketsandMarkets\입력전\MarketsandMarkets_Latest_엑셀파일만_평면압축\MarketsandMarkets New Reports Metadata 01072025.xlsx`
  - 운영본 후보: `D:\GPT 도구 작업\13번 엑셀 업로드 도구\index.html`
  - canonical: `obk369369-spec/13-excel-upload@3a70d84161d0cff9916a7a37d6c88d279df111eb`
  - MASTER 계약: 원본 파일명 + ` - 월드 입력.xlsx`, 시장보고서 체제 `숫자 + Pages`.
- Windows에서는 USB가 `D:`로 정상 연결됐지만 현재 Work 샌드박스는 승인된 위 두 정확한 경로에도 `Access denied`를 반환했다. 파일 부재나 USB 고장으로 재분류하지 않는다.
- 실제 XLSX read/open/browser/download/reopen 검증을 수행하지 못했으므로 TOOL013 runtime을 수정·배포하지 않았고 PASS를 선언하지 않는다.
- 동일 sandbox 조건에서 재시도하지 않는다. 재개 조건은 `EXTERNAL_WORKER_OR_WORKSPACE_WITH_READ_ACCESS_TO_THE_TWO_PINNED_D_PATHS` 또는 해당 실제 입력이 이미 허용된 canonical execution workspace에 자동 mount되는 것이다.
- TOOL043/044는 concrete real business input/handler/verifier가 여전히 없으므로 기존 HOLD를 재사용한다.
- TOOL041/042, TOOL001/006/007은 trigger 변화가 없어 `SKIP_NO_VALUE`; 기존 PASS/HOLD를 재실행하지 않았다.
- 한 lane의 차단을 다른 독립 lane의 실패로 확대하지 않는다. 현재 독립 lane들도 각 필수 actual input/contract가 없어 변경 없는 HOLD로 남긴다.


## 14. 2026-10-18 TOOL013 외부 병렬 조합 실행방식 변경 checkpoint

상태: 기존 코드 중심 단독 조립 즉시 중단. TOOL013 runtime 변경 0건. 기존 checkpoint/PASS/Evidence/Job Pack을 보존·재사용한다.

### 실제 실행한 기존 외부 경로
- canonical directive: `feedback_pipeline/tool044_instruction_inbox.json`
- directive id: `WIC-TOOL013-EXTERNAL-PARALLEL-ASSEMBLY-20261018`
- directive 저장 commit: `4dcb335ada729f48dc7320b32309f8187dc420f6`
- 기존 GitHub Actions canonical intake가 push를 실제 수신하고 TOOL013 기존 지시를 `SUPERSEDE`했다.
- 외부 Actions 증거 자동저장 commit: `1a514261215292005c56e5ece3bec0610ce2b14f`
- evidence: `feedback_pipeline/evidence/tool044_instruction_intake_state.json`
- 기존 Job Pack: `feedback_pipeline/external_factory_job_pack_20261016.json` 재사용. 새 Job Pack/Worker/Workspace/UI/DB/pipeline 생성 0건.

### 독립 lane 결과
1. GitHub Actions intake / claim 전단
   - runner: 기존 `tool044-canonical-instruction-intake` workflow
   - input: 위 canonical directive
   - output: intake state의 TOOL013 `SUPERSEDE` event
   - validator: remote evidence commit/read-back
   - result: `PASS_EXTERNAL_EXECUTED`
2. 실제 XLSX 처리 Worker
   - input: 기존 pinned D: XLSX 경로
   - required output: 원본 파일명 + ` - 월드 입력.xlsx`, 숫자 + `Pages`, identity 보존 결과
   - connection: 기존 factory runtime에 TOOL013 job/socket 미생성
   - evidence: `feedback_pipeline/tool044_factory_runtime.json`은 `active_workers: 0`, TOOL013 matching job 없음
   - result: `HOLD_NO_TOOL013_EXTERNAL_JOB_AND_INPUT_MOUNT`
3. 출력/identity validator
   - 기존 validator 계약과 부품은 재사용 가능하나 lane 2 실제 출력이 없어 실행하지 않음
   - result: `HOLD_NO_ACTUAL_OUTPUT`
4. Kestra orchestration
   - 현재 기존 자산은 health/status linkage뿐이며 TOOL013 XLSX input/output socket이 없음
   - result: `HOLD_HEALTH_LINK_ONLY_NO_TOOL013_SOCKET`
5. Node-RED recovery/ACK
   - 현재 기존 자산은 result recovery/ACK/health linkage뿐이며 TOOL013 workbook 처리 socket이 없음
   - result: `HOLD_RECOVERY_LINK_ONLY_NO_TOOL013_SOCKET`
6. deploy/read-back/Governor
   - 검증된 실제 산출물이 없어 배포·운영본 검증을 시작하지 않음
   - result: `HOLD_NO_VALIDATED_ARTIFACT`

### 차단 경계와 재개 조건
- GitHub Actions 수신 lane 성공은 TOOL013 완성품 PASS가 아니다.
- 기존 외부 조합은 현재 지시 수신까지만 실제 연결됐고, 실제 XLSX를 소비하는 TOOL013 job 생성 socket이 끊어져 있다.
- Kestra/Node-RED 이름 존재나 health link만으로 처리 실행을 주장하지 않는다.
- 동일 조건에서 TOOL013 코드 재조립·동일 실패 재시도를 금지한다.
- 재개는 기존 외부 factory가 TOOL013 job을 생성하고, 허용된 external workspace가 pinned D: XLSX를 mount하여 실제 output을 낸 경우에만 한다.
- 이후 기존 validator가 파일명/정확한 `N Pages`/row identity/download/reopen을 검증하고, 검증 artifact가 있을 때만 deploy/read-back/Governor lane을 실행한다.
- 한 lane HOLD는 다른 독립 lane을 중지시키지 않는다. 이 checkpoint에서는 실제 실행 가능한 intake lane을 완료했고, 나머지는 각각의 정확한 플랫폼 경계로 격리했다.
