# WIC OBSERVER STATUS

최종 갱신: 2026-08-13 15:10 KST
상태: ACTIVE / STRUCTURE_FIRST / ACTUAL_FEEDBACK_E2E_IN_PROGRESS
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 사용자 보고 형식 LOCK
- 모든 진행상황 보고는 기본적으로 Markdown 테이블 표로 구분해서 표시한다.
- 최소 열은 `구분 / 작업 / 상태 / 근거 / 다음 작업`으로 한다.
- 필요 시 `Work 크레딧 필요 여부 / 우선순위 / blocker / 재개지점` 열을 추가한다.
- 긴 서술형 진행보고만 단독으로 출력하지 않는다.
- 사용자가 링크형 대시보드를 요청하면 표와 함께 직접 확인 가능한 GitHub 파일/Run/Artifact 링크를 우선 제공한다.
- 실제 실행 완료 / 진행 중 / HOLD / 아직 실행하지 않음을 표에서 명확히 분리한다.
- 이 규칙은 향후 WIC 진행상황 보고의 기본 출력 규칙으로 사용하고, 중앙 운영원본 통합 파이프라인에도 승격 대상으로 유지한다.

## 운영준비도
- 기존 integration core 재구축/재검증은 반복 금지.
- 기존 안티그래비티 추출 규칙·RULE_PACKET/STATE_PACKET 계열 자산은 재추출하지 않고 재사용한다.
- 안티그래비티 추출 이후 누적된 새 규칙만 기존 중앙 규칙과 차분 비교·충돌검사·중복제거 후 통합한다.
- 오후 1시·5시 메일 통합 예약 작업은 개발/규칙 통합 준비와 별도 예약 작업으로 분리한다.
- 기존 내부 구조 E2E 증거는 유지하되, 현재 사용자 PASS 기준은 `실제 새 feedback -> canonical write/read-back -> target apply/read-back/test -> restart point` 전체 성공이다.
- 이전 최신 feedback `b6acdbfd3bc4d0de1b66`은 TOOL001 BUSINESS E2E HOLD가 남아 있어 현재 기준의 최종 구조 PASS 근거로 사용하지 않는다.

## Work 크레딧 사용 잠금
- 규칙 검색, 기존 안티그래비티 추출본 회수, 차분 비교, 충돌검사, 중복제거, GitHub 문서 통합처럼 Chat/GitHub에서 가능한 작업에는 Work 크레딧을 사용하지 않는다.
- Work는 Chat/GitHub만으로 실제 실행 증거를 만들 수 없는 브라우저 런타임, 실제 파일 주입, 외부 runner/E2E 등 잔여 구간에만 사용한다.
- 사용자 지정 우선순위를 임의 변경하지 않는다.

## 이번 실제 개선
- 원인 확인: `.github/workflows/wic-feedback-event.yml`이 실제 event를 canonical 반영한 뒤 target apply를 무조건 HOLD하도록 되어 있어, 같은 중앙 저장소에서 검증 가능한 lane도 끝까지 PASS하지 못했다.
- 개선 commit: `e5f7f3f4a773f7ae138d59cf9e7628309fa36da2`.
- 개선 내용: verified `CENTRAL_LANE_ACK` target은 같은 workflow 안에서 apply/read-back/test evidence와 checkpoint를 실제 생성하고, cross-repository/미검증 target은 계속 HOLD하도록 fail-closed 유지.
- 새 실제 feedback queued commit: `ba70ebffac4df56c3f85d77d66ff2562215e822c`.
- 새 feedback 내용: 2026-08-13 구조 우선, 실제 feedback E2E 성공 전 구조 PASS 금지, Work credit는 Chat/GitHub blocker 실행/E2E에만 사용, 구조 PASS 후 사용자 지정 우선순위 유지.

## 현재 실행
- GitHub Actions run: `31670039251` (`WIC feedback event apply`).
- job: `94352602812` (`apply-feedback`).
- 마지막 확인 상태: `in_progress`.
- 현재는 완료/PASS로 표시하지 않는다.

## 현재 blocker
- 없음(실행 중). 실행 실패 시 job log를 원인으로 기록하고 해당 단계부터 수정/재시작한다.
- 제3자 독립검증 증거는 없음. 내부 GitHub E2E와 구분한다.

## 최신 restart point
1. run `31670039251` 완료 결과를 확인한다.
2. success면 새 feedback id/revision, canonical GitHub commit, evidence file, target apply/read-back/test checkpoint를 read-back한다.
3. 위 전체가 실제 일치할 때만 `STRUCTURE_PASS_INTERNAL_GITHUB_E2E`로 승격한다.
4. failure면 job `94352602812` 로그에서 최초 실패 step만 수정하고 완료 단계는 반복하지 않는다.
5. 구조 PASS 뒤 우선순위: 이메일 수집 -> TOOL007 -> TOOL001 중간/최종 안내서 -> TOOL037 -> TOOL013 -> TOOL006 -> TOOL002 -> 28~31 -> 나머지 등록 도구/주요 업무창.
6. Work credit는 Chat/GitHub에서 실제 막힌 실행/E2E에만 사용한다.
7. 모든 사용자 진행상황 보고는 테이블 표 형식을 기본으로 한다.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
