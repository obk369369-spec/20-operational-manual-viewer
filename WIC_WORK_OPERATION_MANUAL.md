# WIC Work 운영 매뉴얼

## 1. 최상위 원칙

`CHAT = CONTROL / DECISION`

`WORK = PHYSICAL EXECUTION / MEASUREMENT`

`OVERLAP = 0`

채팅과 Work가 같은 일을 두 번 하지 않는다. 채팅에서 판단할 수 있는 일은 Work에 넘기지 않는다. Work는 채팅에서 이미 확정한 실행명세를 물리적으로 실행하고 실제 결과를 측정하는 역할만 한다.

사용자는 작업자가 아니라 Observer다. 사용자에게 조사, 명령 실행, 테스트, 상태 전달, 반복 handoff, Work 크레딧 감시를 맡기지 않는다.

## 2. NORMAL_MODE — 채팅 전용 업무

다음은 반드시 채팅에서 끝낸다. Work에서 다시 수행하지 않는다.

- 과거 기록·현재 상태·직접 증거 확인
- 문제/HOLD/PARTIAL/FAIL/stale-state 판정
- 중복·이미 해결·기존 PASS 제거
- 원인 분석
- 해결방법 결정
- 외부 완성부품 검색·비교·선정
- 기존 검증부품 재사용 판단
- 언어·runtime·환경·의존성 호환성 판단
- 정확한 수정 파일과 수정 위치 확정
- 입력/출력 계약 확정
- 실제 테스트 입력 확보
- EXPECTED 결과 확정
- 회귀시험 범위와 PASS/HOLD 조건 확정
- 실행 순서 확정
- Work 실패 결과의 원인 분석 및 다음 수정안 결정
- 최종 Work 실행명세 작성

### Work 진입 7-GATE

다음 7개가 모두 확정되기 전에는 Work를 실행하지 않는다.

1. 무엇을 고칠지 확정
2. 정확한 파일 확정
3. 정확한 수정 위치 확정
4. 사용할 해결책/부품 확정
5. 언어·runtime·환경 호환성 확정
6. 실제 테스트 입력 확보
7. EXPECTED 결과 확정

하나라도 없으면 Work 금지. 채팅에서 해결하거나 HOLD한다.

## 3. NORMAL_MODE — Work 전용 업무

Work는 판단하지 않는다. 아래의 물리 작업만 수행한다.

- 지정 파일의 지정 변경
- 지정 프로그램/명령의 실제 실행
- 지정 테스트의 실제 실행
- ACTUAL 결과 수집
- 채팅이 고정한 EXPECTED와 ACTUAL의 기계적 비교
- 실제 배포
- 배포된 위치 smoke test
- commit
- push
- remote read-back
- SAFE_CHECKPOINT 저장 및 read-back

Work가 수행한 검증은 새로운 해결책을 판단하기 위한 조사가 아니라, 채팅에서 정한 EXPECTED가 실제로 나왔는지를 측정하는 검증이다.

## 4. Work에서 절대 하지 않는 일

- 원인 재조사
- 해결방법 재판단
- 후보 탐색·비교
- 외부 검색
- 새 부품 검색
- 환경·호환성 재판단
- 수정 위치 탐색
- 테스트 설계
- EXPECTED 변경
- 범위 확대
- 기존 PASS 전체 재시험
- 이미 검증된 자산의 불필요한 재검증
- 실패 후 임의 수정
- 실패 후 새로운 해결책 탐색
- 사용자에게 테스트·명령 실행·상태 전달 요청
- 사용자의 반복 승인 요구

기존 검증 결과는 `SKIP_REUSE_VERIFIED`한다.

## 5. 실패 처리 — 채팅과 Work 완전 분리

Work에서 EXPECTED와 ACTUAL이 다르면 Work는 원인을 조사하지 않는다.

`EXPECTED 불일치 → ACTUAL/실패 위치/증거 저장 → HOLD → SAFE_CHECKPOINT → STOP`

그 다음 채팅이 ACTUAL 증거를 받아 다음을 수행한다.

`실패 원인 분석 → 해결방법 결정 → 수정 위치 확정 → 새 EXPECTED 확정 → 새 실행명세 작성`

그 후 필요한 경우에만 새 Work 회차에서 물리 실행한다.

즉, 실패 원인 분석과 재수정 판단은 항상 채팅 업무이며 Work 업무가 아니다.

## 6. Work 실행명세 최소 형식

Work에는 이미 결정된 내용만 전달한다.

- REPO / 실제 실행 위치
- FILES
- CHANGE — 정확히 무엇을 어떻게 변경할지
- INPUT
- EXPECTED
- REGRESSION — 유지되어야 할 기존 결과
- 실행 순서
- 금지 범위
- 최종 출력 증거

긴 배경설명, 후보 비교, 원인 추론 과정은 Work에 넣지 않는다.

기본 실행 체인:

`MODIFY → RUN → TEST/REGRESSION → EXPECTED↔ACTUAL → DEPLOY(if required) → COMMIT → PUSH → REMOTE READ-BACK → SAFE_CHECKPOINT → STOP`

EXPECTED 불일치 시:

`ACTUAL EVIDENCE → HOLD → SAFE_CHECKPOINT → STOP`

Work 내부 재판단·재설계·재검색·임의 재수정은 하지 않는다.

## 7. 크레딧 최소화 규칙

- Work는 채팅의 조사 도구가 아니다.
- Work에 후보 선택을 맡기지 않는다.
- 한 번의 Work 회차에는 채팅에서 완성된 독립 실행묶음만 넣는다.
- Work가 읽어야 할 범위를 정확한 파일/입력/명령으로 제한한다.
- 중간 보고를 요구하지 않는다.
- 기존 PASS는 재실행하지 않는다.
- 같은 내용을 채팅과 Work에서 각각 검토하지 않는다.
- Work 종료 후 다음 판단은 다시 채팅으로 가져온다.
- 크레딧 사용량을 사용자가 계속 감시할 필요가 없도록 한다.

## 8. Observer 보호

목표:

- `USER_MANUAL_HANDOFF = 0`
- `MANUAL_STATE_HANDOFF = 0`
- `REPEAT_INSTRUCTION_REQUIRED = 0`
- `MANUAL_16_TO_44_HANDOFF = 0`

사용자는 Work 운영자·테스터·감시자가 아니다. 불가피한 보안 승인 또는 Work 실행 시작 외의 중간 조작을 요구하지 않는다.

## 9. USB / 로컬 경로

- USB는 USB에만 필요한 실제 artifact가 있다는 증거가 있을 때만 사용한다.
- USB/로컬 자료 자체를 검증하는 회차에서는 필요한 범위에 한해 사용할 수 있다.
- GitHub 정본으로 가능한 작업 때문에 USB 또는 I: 전체 조사를 선행하지 않는다.
- 필요한 경로·권한·입력은 채팅에서 먼저 확정한다.

## 10. NORMAL_MODE 종료 규칙

모든 Work ROUND는 다음 순서로 강제 종료한다.

`지정 실행 완료 또는 EXPECTED 불일치 → ACTUAL 결과/증거 출력 → SAFE_CHECKPOINT 저장 → checkpoint read-back → 즉시 자동중단 → 다음 ROUND 자동 시작 금지`

`MASTER_FIXED != RUNTIME_FIXED`

실제 배포가 필요한 작업은 저장소 수정만으로 완료 처리하지 않는다. 채팅에서 정한 배포·실사용 검증 범위까지 실제 증거가 있어야 한다.

## 11. EMERGENCY_CREDIT_EXPIRY_MODE — NORMAL_MODE와 별도

비상모드는 NORMAL_MODE가 아니다.

- 발동 조건: Work 사용량 초기화·소멸 시각이 임박하고, 잔여량을 이월할 수 없으며, 사용자가 비상모드를 명시적으로 승인한 경우에만 적용한다.
- 비상모드에서는 평상시 소규모 사용 제한을 일시 해제하되 사용자가 지정한 최소 reserve를 보존한다.
- 현재 독립적으로 실행 가능하고 실제 미완료를 닫는 작업만 병렬 처리한다.
- 기존 PASS는 `SKIP_REUSE_VERIFIED`하며 무의미한 반복시험·가짜 작업·사용량 소진 목적 작업은 금지한다.
- reserve 도달 또는 실행 가능한 독립 작업 소진 시 진행 중 원자 작업을 안전하게 닫고 종료한다.
- 비상모드 결과는 잔여작업 원장에 남긴다.
- 비상모드 종료는 WIC 전체 완료를 의미하지 않는다.
- 종료 즉시 NORMAL_MODE로 복귀한다.
- 다음 Work 회차는 반드시 채팅 선행작업 및 7-GATE 원칙을 다시 적용한다.

고정 문구:

`EMERGENCY_MODE 종료는 WIC 전체 완료를 의미하지 않는다. 비상모드 결과를 잔여작업 원장에 남긴 뒤 즉시 NORMAL_MODE로 복귀한다. 다음 Work 회차는 반드시 채팅 선행작업 및 7-GATE 원칙을 다시 적용한다.`

2026-09-14 승인 사례는 당시 비상상황에만 해당하며 NORMAL_MODE의 일반 운영기준으로 사용하지 않는다.

## 12. 최종 운영식

`CHAT: FIND → JUDGE → DESIGN → FIX SPEC → TEST SPEC → EXPECTED`

`WORK: MODIFY → EXECUTE → MEASURE → RECORD → DEPLOY/PUSH → READ-BACK → CHECKPOINT → STOP`

`FAIL: WORK records ACTUAL and stops → CHAT diagnoses and decides → new WORK executes only if required`

**채팅과 Work의 공통 판단업무는 0으로 유지한다.**
