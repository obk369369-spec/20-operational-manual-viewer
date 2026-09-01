# WIC 278개 대화기록 정본화 — 재개 체크포인트

기록일: 2026-09-01 KST
상태: HOLD_WITH_SAFE_RESUME_POINT
원본 작업: `feedback_pipeline/WIC_278_CHAT_HISTORY_CATCHUP.md`

## 목적
사용자가 나중에 `278개 작업 계속`, `남은 거 해`, `보류했던 대규모 파일 작업 재개`처럼 짧게 말해도 처음부터 다시 찾거나 278개를 재처리하지 않고 이 지점에서 이어간다.

## 확인된 원본 범위
- 압축파일: 278개
- 텍스트 추출: 278/278 접근 성공
- 번호 확인 그룹: 32개
- 기존 체크포인트(2026-08-31)는 29/32 완료, 남은 번호 그룹을 `034,037,038`로 기록했다.

## 2026-09-01 재확인 결과
아래 3개는 현재 GitHub main의 CENTRAL MASTER에서 이미 `278-file historical numbered-group canonicalization: COMPLETE`로 확인된다.

1. TOOL034 — `feedback_pipeline/TOOL034_MASTER.md`
   - 분류: `INDEPENDENT OPERATING CHAT / NON-TOOL`
   - CENTRAL MASTER: COMPLETE
   - 비번호/별칭 역사자료 Batch 1, Batch 2 분류까지 기록됨.

2. TOOL037 — `feedback_pipeline/TOOL037_MASTER.md`
   - 278 번호 그룹 정본화: COMPLETE
   - CANONICAL_REPO: UNRESOLVED, 새 repo 생성 금지
   - 비번호/별칭 역사자료 Batch 1 흡수 기록 있음.

3. TOOL038 — `feedback_pipeline/TOOL038_MASTER.md`
   - 분류: `INDEPENDENT OPERATING CHAT / NON-TOOL`
   - 278 번호 그룹 정본화: COMPLETE
   - 별도 실행 repo 불필요.

따라서 **번호 확인 32개 그룹은 현재 기준 모두 정본화/흡수 판정 완료 상태로 본다.**

## 아직 남은 실제 작업
`WIC_278_CHAT_HISTORY_CATCHUP.md`의 마지막 4번 작업만 남는다.

- 번호 없는 파일
- 별칭 파일
- 중복 사본
- 다른 명명형 기록
- 기존 TOOL/CENTRAL에 흡수될 보조창 기록

이들을 최종 분류하여 다음 중 하나로 판정한다.
- `ALIAS_TO_EXISTING_TOOL`
- `ABSORBED_NO_UNIQUE_DIFF`
- `DUPLICATE / SKIP_REUSE`
- `SHELL_OR_STALE`
- `HOLD_UNKNOWN`
- 실제 고유 DIFF가 있을 때만 기존 canonical에 `DIFF ONLY` 반영

## 재개 시 강제 순서
1. 이 체크포인트를 먼저 읽는다.
2. 기존 32개 번호 그룹은 재분석/재테스트하지 않는다 (`SKIP_REUSE`).
3. 278개 원본 전체를 처음부터 다시 돌리지 않는다.
4. 남은 비번호/별칭/중복 후보만 기존 추출 목록/역사자료 인덱스에서 회수한다.
5. 각 후보를 기존 TOOL master / CENTRAL / alias와 대조한다.
6. 고유 규칙이 없으면 별도 MASTER/repo를 만들지 않는다.
7. 고유 DIFF가 있을 때만 기존 정본에 최소 변경한다.
8. GitHub write가 발생하면 commit → remote read-back까지 확인한다.
9. 최종적으로 `WIC_278_CHAT_HISTORY_CATCHUP.md` 진행률을 갱신하고 `COMPLETE` 또는 정확한 HOLD 사유로 닫는다.

## 금지
- 278개 전체 재처리
- 이미 완료된 32개 번호 그룹 재개발/재검증
- 새 TOOL/repo 임의 생성
- 과거 assistant의 근거 없는 PASS/완료 주장을 현재 증거로 승격
- 현재 다른 TOOL 작업과 278 catch-up을 섞기

## 다음 시작점
`NEXT_START = UNNUMBERED_ALIAS_DUPLICATE_FINAL_CLASSIFICATION_ONLY`

사용자 재개 문구 예: `278개 남은 거 계속`.
그 경우 이 파일을 기준으로 바로 위 NEXT_START부터 이어간다.
