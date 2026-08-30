# TOOL016 MASTER — 16번 Work 작업 조정·피드백 운영

상태: ACTIVE / CENTRAL ORCHESTRATION MASTER
기준일: 2026-08-30
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
- 사용자는 새 대화창을 여는 것 외에 과거 내용을 다시 설명·정리하지 않는다.
- 새 창은 최신 CENTRAL/checkpoint/handoff부터 읽고 이어간다.

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

## 10. 2026-08-30 대화기록 catch-up
- 제공된 16번 기록의 지속 가치가 있는 `root/recurrence`, Work 투입, handoff, 사용자 Observer, 플랫폼 한계, 크레딧 보호 규칙을 최신 운영방향에 맞게 통합했다.
- 최신 사용자 운영방식인 `업데이트=저장 버튼`과 `효율화 방법을 먼저 제안` 규칙을 추가했다.
- 이후 16번 대화창에서 `업데이트` 입력 시 신규 영구 피드백만 DIFF ONLY 반영한다.
- 실제 GitHub write/commit/read-back 없이 업데이트 완료라고 보고하지 않는다.
