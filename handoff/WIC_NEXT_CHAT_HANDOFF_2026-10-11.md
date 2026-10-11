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
