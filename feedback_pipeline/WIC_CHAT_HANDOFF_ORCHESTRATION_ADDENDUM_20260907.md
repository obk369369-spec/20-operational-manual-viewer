# WIC CHAT HANDOFF / ORCHESTRATION ADDENDUM — 2026-09-07

상태: ACTIVE / REQUIRED
목적: 2026-09-06~07 대화에서 확정·검증된 신규 피드백을 CENTRAL 실행기준에 증분 승격한다. 기존 WIC_WORK_COMMON_EXECUTION_BLOCK과 충돌 시 최신 사용자의 명시적 지시를 우선하고, 이미 같은 규칙은 SKIP_REUSE한다.

## 1. TOOL043 확장 기준선
- TOOL043 로컬 실행 복구 결과: `LOCAL_DEPLOY_VERIFY = PASS`, `DEPLOYED_UI_MATCH_PASS = PASS`, `SAFE_CHECKPOINT = RECORDED`.
- 로컬·Pages 장부 시각: `2026-09-06 19:55:44 KST` 일치.
- 로컬 화면: 관찰판 정상, `Failed to fetch` 없음, 브라우저 오류 0.
- 핵심 상태값: 야간 1 / OPEN 2 / 미처리 6 / 대기 4 / 진행 0. 미처리·최근 완료 목록 일치.
- 로컬 `Failed to fetch` 원인은 실행기 `%~dp0` 후행 `\`가 Python `--directory` 인수를 깨뜨려 요청이 404가 된 것이며, `TOOL043_DIR=%~dp0.` 한 줄 최소 수정으로 로컬 HTTP의 `index.html`, `status.json`, `status_snapshot.js`, `night_queue.json` 200을 확인했다.
- 위 결과는 TOOL043의 최소 확장 기준선으로 재사용하며 직접 영향이 없는 한 처음부터 재검증하지 않는다: `TOOL043_BASELINE = SKIP_REUSE`.

## 2. 정상자료와 껍데기 강제 분리 / 정본 승격
- USB, 노트북, 사무실 PC, Work 작업폴더, 대화 유래 산출물 등 위치와 무관하게 파일 존재만으로 정본 취급하지 않는다.
- 실제 실행 + 독립 EXPECTED + EXPECTED↔ACTUAL + 직접 영향 회귀를 통과한 자료만 `VERIFIED`로 승격한다.
- `SHELL / DRAFT / TEST_NOT_RUN / FAIL / PARTIAL / 출처불명`은 canonical MASTER/GitHub 정본 승격 금지.
- 정상자료의 표준 흐름은 `ACTUAL EXECUTION → TEST → EXPECTED↔ACTUAL → IMPACTED REGRESSION → PASS → VERIFIED → GitHub/해당 정본 저장소 → REMOTE READ-BACK → 실제 사용본 배포 → DEPLOYED COPY TEST → DEPLOYED_PASS → SAFE_CHECKPOINT`.
- 작업 중 정상임이 확인된 자료는 껍데기와 분리하여 해당 GitHub/MASTER/registry에 증분 승격한다. 이미 검증·승격된 정상자료는 SKIP_REUSE한다.
- commit만으로 완료하지 않고 remote read-back까지 PASS해야 CENTRAL 반영으로 인정한다.

## 3. 실행기기 비종속 / USB 연결불량 복구
- WIC 실행상태를 특정 USB, 노트북, 사무실 PC 또는 단일 Work 실행환경에 종속시키지 않는다.
- canonical state / rules / evidence / SAFE_CHECKPOINT는 GitHub/CENTRAL을 기준으로 다른 worker/기기가 이어받을 수 있어야 한다.
- USB나 특정 기기가 연결 불량이면 사용자에게 반복 연결·파일찾기·복구를 전가하지 않는다. 재감지/대체 정본/다른 worker를 사용하고 마지막 SAFE_CHECKPOINT에서 재개한다.
- 동일 방식 재시도는 최대 1회. 같은 조건에서 반복 실패하면 다른 복구경로 또는 실제 외부 HOLD로 전환한다.
- 사용자 기기에 Work가 직접 들어가 수정·삭제하는 방식은 기본 실행경로가 아니다. 원격/CENTRAL/GitHub에서 가능한 작업은 사용자 기기 접근 없이 처리한다.
- 사용자 기기 접근이 불가피해도 자동 삭제, 대량 이동/정리, 정상본 덮어쓰기는 금지한다.
- 목표 실행구조: `GitHub/CENTRAL = canonical → 노트북/PC 내부 SSD = actual runtime/deployment → USB = 보조 데이터/백업`.

## 4. 관찰자 보호
- 사용자 = 관찰자/결과 수령자. 정상적인 기술 작업은 시스템이 수행한다.
- 파일찾기, 로그복사, 수동테스트, 오류분석, 재시작, 배포, 체크포인트 복구, 반복 승인, 중간 수리를 사용자에게 전가하지 않는다.
- 사용자만 가능한 진짜 외부 행동은 `USER_ACTION_QUEUE`로 분리하고 가능한 한 한 번에 묶는다.
- 불필요한 허용 버튼/중간 승인을 만들지 않는다.
- 정상 운영·시험·복구·배포는 Work/Codex 크레딧, 유료 API/SaaS에 지속 의존하지 않는 LOCAL/FREE 구조를 우선한다.

## 5. 대량 병렬 확장 목표
정식 구조명: `WIC 대량 병렬 무중단 자율복구·검증·배포 오케스트레이션 시스템`.

목표:
- 한 번의 관찰자 지시로 다수 TOOL/프로그램/대화 유래 작업의 대상을 자동 식별·분류한다.
- 독립 대상은 병렬 처리하고 충돌/의존 대상만 자동 직렬화한다.
- 각 대상은 착수/원인수렴/검증부품 조달/후보검증/수정감시/독립시험/중단감지/상호감사/실패패턴 학습/GitHub 승격/실사용 배포/배포본 감사/관찰자 보호/비용 방화벽/Watchdog 흐름을 통과한다.
- 실패한 worker/layer가 전체 작업을 멈추게 하지 않고 peer recovery와 SAFE_CHECKPOINT resume을 사용한다.
- 최종 성공 기준은 파일 생성이나 commit이 아니라 대상별 `DEPLOYED_PASS`다.
- TOOL044 역할은 외부에서 이미 완성·공유·실사용·검증된 무료 부품을 대량 후보로 가져와 독립 sandbox에서 병렬 검증하고 PASS 후보만 무수정 장착하는 것이다. 수정/커스터마이즈가 필요하면 `NO_READY_COMPONENT`.
- 기존 `wic_mutual_supervision.py` 및 이미 PASS한 공통 구조는 재개발하지 않고 확장 기반으로 SKIP_REUSE한다.

## 6. TOOL041 / TOOL042 투입 순서
- TOOL041/TOOL042는 고질적인 개별 문제를 지금 다시 처음부터 파고들지 않는다.
- 먼저 위 공통 대량 병렬/자가복구/검증/정본승격 구조의 최소 동작 검증을 마친다.
- 이후 TOOL041/TOOL042를 대상 작업으로 투입한다.
- TOOL041은 기존 `ONLINE_COLLECTION_EXECUTION_PATH_INCOMPLETE` 동일 실패방법을 그대로 반복하지 않는다.
- TOOL042는 `CURRENT_LEDGER_ROW_NOT_RESOLVED`만을 핵심 blocker로 오판하지 않는다. 기존 분석의 핵심 blocker family인 expected/gate contract alignment + semantic/runtime + renderer/runtime을 재사용하며, 이미 확보된 실제 고객 EML 증거를 다시 사용자에게 요구하지 않는다.

## 7. 다음 확장 전 최소 마감 / SSD 이전
- TOOL043 최종 검증 증거는 CENTRAL/GitHub evidence 정식 위치로 승격하고 remote read-back해야 한다. 단, 이 addendum 자체는 TOOL043 원본 체크포인트 파일의 승격을 대체하지 않는다.
- `SSD_MIGRATION_MANIFEST`를 만들어 USB 전체 복사가 아니라 실제 runtime, CENTRAL/MASTER/checkpoint, 필요한 fixture/evidence만 내부 SSD로 선별 이전한다.
- 현재 확실한 우선 이전 대상은 `GPT 도구 작업/43번 모바일 관찰판/` 전체다.
- 다른 TOOL/공통폴더의 정확한 경로는 실제 확인 후 manifest에 기록하며 추정 경로를 만들지 않는다.
- 대용량 과거 백업/구버전/중복/보관자료는 실행 필수성이 검증되지 않으면 우선 이전 대상에서 제외한다.

## 8. 대화 인계 / 업데이트 명령 강화
- 대화 최대 길이에 도달하기 전에 신규 영구 피드백을 CENTRAL과 해당 TOOL canonical에 증분 승격한다.
- 사용자가 `업데이트` 또는 `여기까지 피드백 업데이트`라고 지시하면: `MASTER_LOAD → 신규 영구 피드백 추출 → 중복/충돌 대조 → DIFF ONLY → GitHub commit/push → remote read-back → 증거 보고`를 수행한다.
- 별도 새 MASTER를 임의 생성하거나 기존 정본을 재작성하지 않는다.
- 다음 대화는 MASTER + latest SAFE_CHECKPOINT부터 RESUME하며 사용자가 과거 내용을 재설명하게 하지 않는다.

## 9. 현재 NEXT_START
1. 이 addendum의 remote read-back 확인.
2. TOOL043 실제 checkpoint/evidence 파일의 canonical evidence 승격 여부를 확인하고 미승격이면 최소 승격 + remote read-back.
3. 기존 common block에 위 규칙이 이미 있으면 SKIP_REUSE하고, 누락된 강제규칙만 적절한 canonical 위치에 최소 반영.
4. `SSD_MIGRATION_MANIFEST` 확정.
5. 공통 대량 병렬 오케스트레이션 구조의 최소 동작 검증으로 이동.
6. 그 검증 후 TOOL041/TOOL042 투입.

ADDENDUM_DATE = 2026-09-07
OBSERVER_ONLY = REQUIRED
DEVICE_INDEPENDENT_RESUME = REQUIRED
VERIFIED_ONLY_CANONICAL_PROMOTION = REQUIRED
SHELL_CANONICAL_PROMOTION = FORBIDDEN
REMOTE_READBACK_REQUIRED = TRUE
TOOL043_BASELINE_REUSE = REQUIRED
FLEET_ORCHESTRATION_NEXT = TRUE
TOOL041_042_AFTER_COMMON_EXPANSION = TRUE
