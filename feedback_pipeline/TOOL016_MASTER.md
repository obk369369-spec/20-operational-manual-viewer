# TOOL016 MASTER — 16번 Work 작업 조정·피드백 운영

상태: ACTIVE / CENTRAL ORCHESTRATION MASTER
기준일: 2026-09-07
저장 위치: WIC CENTRAL `feedback_pipeline/`

이 문서는 16번 대화창의 고유 역할만 정의한다. WIC 전체 공통 운영규칙은 `WIC_GLOBAL_OPERATING_RULES.md`, Work 공통 실행은 `feedback_pipeline/WIC_WORK_COMMON_EXECUTION_BLOCK.md`, 실제 각 TOOL 규칙은 해당 TOOL canonical master를 우선한다.

## 1. 16번 역할
- 16번은 모든 도구 기능을 직접 개발하는 도구가 아니다.
- 각 실제 대화창에서 발견된 오류·누락·재발·HOLD를 수집하고 같은 root/recurrence를 묶어 **어떤 실제 TOOL을 Work에 투입할지, 무엇을 건드리지 말아야 할지, 어떤 PASS 컴포넌트를 재사용할지** 좁혀 주는 조정 역할이다.
- Work에 넘길 때는 과거 전체를 다시 설명하지 않고 최신 중앙마스터·checkpoint·root/occurrence ledger·handoff를 먼저 읽게 한다.

## 2. 실제 작업 중심 피드백 수집
흐름:
`실제 업무 진행 → 새 오류/구멍 발견 → 기존 root인지 새 root인지 분류 → recurrence/OPEN 누적 → 당장 안전하게 닫을 수 있으면 최소 수정+1회 검증 → 그렇지 않으면 HOLD/RESUME_TRIGGER → 실제 업무 계속`

- 구멍을 찾기 위해 전체 시스템을 조사하지 않는다.
- 기존 PASS/CLOSED/VERIFIED/REMOTE_VERIFIED를 이유 없이 다시 열지 않는다.
- 같은 root는 새 항목을 계속 만들지 않고 recurrence로 누적한다.
- 실사용을 막는 HIGH 오류는 묶음 대기 없이 우선 투입할 수 있다.

## 3. Work 투입
- Work 지시문은 `대상 TOOL / 현재 실제 실패 / 기존 PASS 재사용 / 수정 범위 / 금지 범위 / FIRST_VALIDATION / 완료 증거 / HOLD trigger`를 포함한다.
- 전체 WIC 재조사, 모든 repo 재탐색, 이미 PASS한 테스트 재실행을 기본 Work로 만들지 않는다.
- 한 번에 여러 TOOL을 투입할 때도 각 TOOL root를 분리하고, 공통 원인만 공통 수정한다.
- Work가 저장소/경로/과거 상태를 사용자에게 다시 물으면 중앙 registry/checkpoint/handoff에서 먼저 복구한다.

## 4. 크레딧 보호
- 기존 결과 재사용 → 아직 OPEN인 부분만 DIFF ONLY → 바뀐 범위 FIRST_VALIDATION 1회 → commit/read-back 순으로 처리한다.
- 동일 repo·파일·SHA·CI를 같은 조건에서 반복 조회/검증하지 않는다.
- 같은 실패를 같은 방법으로 반복 패치하지 않는다.
- full audit, broad regression, 모든 대화 전수분석은 명시적 사용자 요청과 실제 필요 없이는 금지한다.
- COMPLETE에 가까운 안전한 항목을 먼저 닫고 BLOCKED/HOLD는 trigger 전까지 반복 소비하지 않는다.

## 5. Chat handoff
- 대화가 길어져 문맥 누락/로딩/응답 악화 위험이 커지면 사용자가 먼저 알아차리기 전에 `CHAT_HANDOFF_REQUIRED`를 제안한다.
- 인계 내용은 SAFE_CHECKPOINT / OPEN / INCOMPLETE / HOLD-WAIT / 최근 실제 결과 / NEXT_WORK_QUEUE / NEXT_START / 영구규칙을 압축한다.
- **대화창을 옮기기 전에 현재 대화에서 새로 확정된 영구규칙과 실제 PASS 증거를 CENTRAL/해당 TOOL master에 DIFF ONLY로 실제 반영하고 commit/push/remote read-back까지 수행한다.**
- GitHub write/read-back이 끝나지 않았으면 handoff를 `CENTRAL_UPDATED`로 표시하지 않는다.
- 사용자는 새 대화창을 여는 것 외에 과거 내용을 다시 설명·정리하지 않는다.
- 새 창은 최신 CENTRAL/checkpoint/handoff부터 읽고 이어간다.
- 이미 중앙 반영된 내용은 새 대화에서 다시 작성하지 않고 `SKIP_REUSE`한다.

CHAT_HANDOFF_REQUIRES_CENTRAL_FLUSH = TRUE
HANDOFF_CENTRAL_REMOTE_READBACK_REQUIRED = TRUE
HANDOFF_USER_REEXPLANATION = FORBIDDEN

## 6. 자동화 가능/플랫폼 한계 구분
- WIC가 통제하는 GitHub gateway/feedback pipeline 내부에서는 routing→master write→commit/read-back을 자동화할 수 있다.
- ordinary ChatGPT 모든 메시지를 Work가 제품 차원에서 자동 감시하는 interceptor가 있다고 가정하지 않는다.
- 플랫폼에서 실제 제공되지 않는 기능은 `PLATFORM_LIMIT`으로 표시하고 내부 구현 완료처럼 과장하지 않는다.
- 플랫폼 한계가 있다고 해서 GitHub write 자체가 불가능한 것처럼 말하지 않는다. 현재 대화에서 명시적 실행명령을 받으면 GitHub connector로 실제 write할 수 있다.

## 7. `업데이트` 명령 — 중앙 저장 버튼
- 사용자가 WIC 대화창에서 `업데이트`라고 입력하면 **직전까지의 해당 대화창 신규 영구 피드백을 중앙/TOOL master에 저장하는 명시적 실행명령**으로 해석한다.
- `업데이트`는 Work가 ChatGPT 전체에 설치한 자동 hook이 아니다. 현재 대화의 assistant가 실제 GitHub write를 실행하는 수동 shorthand command다.
- 처리: `현재 대화 신규 영구피드백 → 대상 TOOL/canonical resolve → 기존 규칙 대조 → 중복 SKIP_REUSE → 최신 명시지시로 충돌 해결 → DIFF ONLY → commit → remote read-back → 증거 보고`.
- 일회성 질문·현재상태·특정 고객 사실은 공통 master가 아니라 필요 시 DATA/checkpoint에 둔다.
- 실제 write/read-back 실패 시 `미반영`으로 보고한다.

## 8. 운영 단축명령 제안 의무
- 사용자가 무엇을 물어봐야 하는지 모를 수 있으므로, 반복되는 사용자 노동이나 Work 낭비를 줄일 수 있는 **단축명령/운영규칙/기존 기능 재사용 방법**을 assistant가 발견하면 사용자가 먼저 질문할 때까지 기다리지 않고 즉시 제안한다.
- 특히 `같은 설명 반복 / 같은 상태 조회 / 같은 검증 / 같은 배포 / 같은 재개 / 같은 저장`이 반복되면 짧은 명령어로 고정할 가치가 있는지 먼저 설명한다.
- 단어 자체를 assistant가 임의 영구확정하지 않는다. 사용자가 의미와 단어를 승인하면 이후 그 명령을 고정 운영한다.
- Work가 필요 없는 현재-chat 직접 처리 방법이 있으면 Work 투입보다 먼저 알려준다.

## 9. 과거 지시문/공격감사 정리
- 과거 16번 기록의 거대한 full-audit/`NEW_HOLES=0 연속 N회`/모든 층 OPEN 0 공격검사 지시를 현재 기본 운영으로 반복하지 않는다.
- 이미 검증된 중앙 pipeline, approval batching, no-repeat, no-full-audit, verified reuse 규칙은 SKIP_REUSE한다.
- 실제 새 증상이 나온 범위만 incremental gap capture 한다.
- 증거 없는 과거 `모든 구멍 0`, `자동완료` 보고를 현재 사실로 승계하지 않는다.

## 10. 검증자료 정본 승격 — REQUIRED
- USB, 노트북, 사무실 PC, Work 임시폴더, 기타 실행기기에 있는 자료는 위치만으로 신뢰하지 않는다.
- 실제 실행·EXPECTED↔ACTUAL·직접 영향 회귀를 통과한 정상 자료만 `VERIFIED / DEPLOYED_PASS / SAFE_CHECKPOINT`로 판정한다.
- 정상 검증된 자료는 껍데기·샘플·중간본·실패본과 분리하여 해당 TOOL GitHub canonical repo와 CENTRAL MASTER/checkpoint/registry에 필요한 최소 범위로 계속 승격한다.
- `SHELL / DRAFT / TEST_NOT_RUN / FAIL / PARTIAL / SHELL_OR_INVALID`는 정본 승격 금지다.
- 승격 완료는 commit/push만이 아니라 GitHub remote read-back PASS까지 요구한다.
- 검증자료 승격은 대화창 이동 직전에도 동일하게 적용한다.

VERIFIED_ASSET_CANONICAL_PROMOTION = REQUIRED
SHELL_ASSET_CANONICAL_PROMOTION = FORBIDDEN
CANONICAL_PROMOTION_REQUIRES_REMOTE_READBACK = TRUE

## 11. 실행기기 독립·USB 장애 복구 원칙 — REQUIRED
- USB, 노트북, 사무실 PC, 기타 한 장치나 한 경로에 WIC 작업의 지속성을 종속시키지 않는다.
- 특정 장치가 연결 불량·미감지·접근불가여도 마지막 `SAFE_CHECKPOINT + CENTRAL MASTER + GitHub canonical + 검증 증거`를 기준으로 다른 실행환경에서 이어받을 수 있어야 한다.
- 사용자 PC/노트북에 Work가 직접 들어가 파일을 수정·삭제하는 방식을 기본 실행방식으로 하지 않는다. GitHub/CENTRAL/원격 검증으로 가능한 작업은 사용자 기기 직접 접근 없이 수행한다.
- 사용자 기기 접근이 실제로 필요한 경우에도 자동 삭제·대량 이동·대량 정리·정상본 덮어쓰기는 금지하고, 좁은 읽기/검증/최소 배포만 허용한다.
- USB 미감지는 즉시 전체 HOLD로 종료하지 않고, 재감지 1회 또는 다른 검증된 경로를 시도한 뒤 실제 외부 blocker인지 판정한다.
- 같은 USB 연결 실패를 같은 방식으로 반복하여 Work/Codex 크레딧을 소모하지 않는다.
- 내부 SSD 이전은 USB 전체복사가 아니라 실제 실행 TOOL, CENTRAL/MASTER/checkpoint, 필수 fixture/evidence만 `SSD_MIGRATION_MANIFEST`로 선별한다.

DEVICE_INDEPENDENT_RESUME = REQUIRED
USB_SINGLE_POINT_OF_FAILURE = FORBIDDEN
USER_DEVICE_DIRECT_MUTATION = FORBIDDEN_BY_DEFAULT
USB_RETRY_SAME_METHOD = FORBIDDEN
SSD_MIGRATION_MANIFEST = REQUIRED_BEFORE_BULK_MOVE

## 12. TOOL043 2026-09-06/07 확장 기준선
- TOOL043 로컬 실행 복구 및 원격 Pages 동일성 검증 결과를 다음 확장의 기준선으로 재사용한다.
- `LOCAL_DEPLOY_VERIFY = PASS`
- `DEPLOYED_UI_MATCH_PASS = PASS`
- `SAFE_CHECKPOINT = RECORDED`
- 로컬·Pages 장부 시각 `2026-09-06 19:55:44 KST` 일치.
- 로컬 화면 `Failed to fetch` 없음, 브라우저 오류 0.
- 핵심 상태값 `야간 1 / OPEN 2 / 미처리 6 / 대기 4 / 진행 0` 및 미처리·최근 완료 목록 일치.
- 확인된 로컬 원인은 실행기 `%~dp0`의 후행 `\`가 Python `--directory` 인수를 깨뜨려 404를 발생시킨 것이며, 최소 수정 `TOOL043_DIR=%~dp0.` 후 로컬 HTTP 핵심 파일 200 및 실제 렌더 PASS.
- 이 합의 범위는 다음 확장 시 `SKIP_REUSE`하고 처음부터 재시험하지 않는다. 직접 영향이 생긴 경우에만 영향범위 테스트한다.
- 다음 확장 준비 마감의 잔여 순서는 `TOOL043 검증 증거 CENTRAL/GitHub 정식 evidence 승격 → remote read-back → VERIFIED/SHELL 분리 규칙 확인 → SSD_MIGRATION_MANIFEST → NEXT_START`이다.

TOOL043_EXPANSION_BASELINE = VERIFIED
TOOL043_BASELINE_RETEST = SKIP_REUSE_UNLESS_IMPACTED

## 13. 다음 확장 순서
- 먼저 16번의 중단된 확장 준비 마감 작업을 마지막 실제 완료지점부터 RESUME한다.
- 그 다음 `WIC 대량 병렬 무중단 자율복구·검증·배포 오케스트레이션 시스템`의 최소 동작 범위를 구축·검증한다.
- 공통 확장 구조가 최소 동작 검증되기 전에는 TOOL041·TOOL042의 고질적인 개별 문제를 다시 전면적으로 파고들지 않는다.
- TOOL041·TOOL042는 공통 확장 구조의 검증 이후 실제 대상 workload로 투입한다.
- 기존 mutual-supervision engine 및 이미 PASS된 공통부품은 `SKIP_REUSE`한다.

NEXT_MAJOR_SCOPE = WIC_MASS_PARALLEL_SELF_RECOVERY_VALIDATION_DEPLOY_ORCHESTRATION
TOOL041_TOOL042_AFTER_COMMON_EXPANSION_BASELINE = TRUE

## 14. 2026-09-07 대화창 handoff 반영
- 이 대화창에서 확정된 신규 영구규칙을 TOOL016 CENTRAL MASTER에 DIFF 성격으로 통합했다.
- 공통층 inventory: `feedback_pipeline/evidence/common_layer_inventory_20260907.json`.
- 기기 자산 정본 gate: `feedback_pipeline/wic_asset_provenance.py`; 현재 작업 manifest에 직접 관련된 경로만 검사하며 VERIFIED만 canonical/registry/실사용 reference로 승격한다.
- 핵심 신규사항은 `대화창 이동 전 CENTRAL flush 강제`, `검증자료와 껍데기 분리 및 정상자료 정본승격`, `실행기기 독립/USB 단일장애점 제거`, `사용자 기기 직접변경 기본금지`, `TOOL043 최종 확장 기준선`, `공통 확장 후 TOOL041·TOOL042 투입 순서`다.
- 이후 새 대화는 이 master + 최신 checkpoint/handoff를 먼저 읽고 마지막 실제 작업지점부터 재개한다.
- 실제 GitHub write/commit/read-back 없이 업데이트 완료라고 보고하지 않는다.
