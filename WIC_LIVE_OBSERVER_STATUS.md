# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 06:43 KST
상태: ACTIVE — 3단 재개 펄스 + 5분 GitHub heartbeat 감시 추가

이 파일은 사용자가 직접 테스트하지 않고 진행을 관찰하기 위한 외부 상태판이다. 실제 외부 증거가 있을 때만 진행으로 기록한다.

## 이번 회차 실제 작업 — 06:43
- 본 작업 `WIC Overnight Completion`은 매시 50분 실행 유지.
- `WIC Stall Watchdog`은 매시 10분 실행으로 재배치했다.
- 새 보조 재개 작업 `WIC Recovery Pulse`를 매시 30분에 추가했다.
- 따라서 ChatGPT 측 재개 기회는 `:10 → :30 → :50`으로 20분 간격이다. 스케줄러가 정상 실행된다는 전제에서 멈춤 후 다음 재개 시도까지 이론상 최대 약 20분이다.
- GitHub 외부 보완으로 `.github/workflows/wic-stall-monitor.yml`을 새로 추가했다. GitHub Actions가 5분 cron으로 observer 파일의 마지막 commit 시각을 확인하고, 35분 이상 stale이면 단일 `[WIC STALL] Observer heartbeat stale` 이슈를 생성/갱신하며 workflow를 FAIL로 남긴다.
- GitHub heartbeat는 외부 감지 증거를 만드는 역할이며 ChatGPT 작업 자체를 직접 재시작하지는 못한다. 실제 재개는 :10/:30/:50의 세 자동화가 수행한다.
- GitHub monitor 생성 commit: `0f8a3e4f15e45ffcb275b07d4c15a89ef8d2d3ec`.

## 구조 변경의 장점과 새 단점
- 장점: 기존 30~40분 수준의 재개 공백을 스케줄상 최대 약 20분으로 줄였다. GitHub 쪽에는 5분 단위 별도 heartbeat 감시 증거가 생긴다.
- 단점 1: 자동화 작업이 3개가 되어 자동 실행 대화 항목이 더 생길 수 있다.
- 단점 2: 장시간 실행이 서로 겹치면 중복 실행·race condition·상태판 동시갱신 충돌 가능성이 있다. 각 recovery prompt는 unchanged evidence를 SKIP하고 saved restart point를 우선하도록 제한했다.
- 단점 3: 실행 횟수가 늘어 크레딧/도구 사용량이 증가할 수 있다.
- 단점 4: GitHub Actions cron은 정확히 5분마다 즉시 실행된다고 보장할 수 없고 지연될 수 있다.
- 단점 5: GitHub Actions heartbeat는 stall을 외부에서 표시할 수 있지만 ChatGPT 자동화를 직접 호출하여 즉시 재시작시키는 기능은 없다. 따라서 실제 재개 보장은 현재 :10/:30/:50 자동화에 의존한다.
- 단점 6: GitHub Actions 사용량이 계정/저장소 조건에 따라 Actions minutes를 소비할 수 있다.

## 영구 주의사항 / 재발방지 잠금
1. 중간에 멈추면 최대한 다시 이어가도록 하는 감시·재개 장치를 임의로 끄지 않는다.
2. 멈춤 감시는 Watchdog 하나에만 의존하지 않는다. 사용 가능한 외부구조/GitHub Actions/상태 heartbeat/재시작 포인터 등을 병행한다.
3. 구조를 바꿀 때 장점만 보고하지 않는다. 새 공백, 감시 약화, 중복 실행, 비용/크레딧 증가, 대화창 증가, 상태 충돌 같은 단점이 생기면 변경 전에 또는 즉시 보고한다.
4. 자동화 설정 누락·잘못된 중단·번호 혼동·중복 규칙 생성·가짜 완료 같은 운영 실수는 GitHub 상태와 중앙 운영 원본에 기록하고 재발방지 규칙으로 승격한다.
5. 사용자의 주의사항은 임시 대화 기억으로만 두지 않고 중앙 단일원본 `WIC_GLOBAL_OPERATING_RULES.md`에 흡수한다. 긴 파일의 안전한 부분수정 수단이 없는 회차에는 이 상태판에 먼저 증거로 저장하고, 다음 안전한 병합 가능 회차에 중앙원본으로 이동·통합한다.
6. 같은 파일/같은 부분을 새 증거 없이 다시 처리하지 않는다. 반복 확인이 필요한 경우 새 commit/file/evidence/state change 또는 코드수정·실행테스트·회귀검증·독립검증처럼 다른 단계여야 한다.
7. 감시 장치를 끄거나 실행 구조를 단순화하는 변경은 사용자의 명시적 지시 없이 하지 않는다.

## 이번 회차 판정
| 작업 묶음 | 상태 | 외부 증거 | blocker / 개선 | 다음 실행 |
|---|---|---|---|---|
| 3단 재개 펄스 | PASS(설정) / HOLD(실제 stall 복구 실증) | Automations :10/:30/:50 설정 | 실제 stall 발생 시 복구 성공 로그 필요 | 첫 stall에서 실제 재개 및 상태판 read-back 확인 |
| GitHub 5분 heartbeat | PASS(파일 생성) / HOLD(첫 scheduled run 실증) | `.github/workflows/wic-stall-monitor.yml`, commit `0f8a3e4f...` | cron 지연 가능, ChatGPT 직접 재시작 불가 | 첫 scheduled run/FAIL 또는 healthy 결과 확인 |
| 자동 재개 기능 | PASS(프롬프트 설정) / HOLD(실제 재개 실행증거) | watchdog/recovery prompts | 다음 stall 전 실증 불가 | stall 발생 시 보고+즉시재개 동시 수행 |
| 운영 실수 기록 | PASS | 이 상태판 commit/read-back | 중앙원본 직접 병합은 긴 파일 안전수정 문제 | 안전 병합 가능 회차에 `WIC_GLOBAL_OPERATING_RULES.md`로 흡수 |

## 직전 작업 요약
- 6번 v2.26 `classifyHold()`/`runInternalSimulation()` 구조 확인. 최신 100건 실제 실행증거는 없어 HOLD 유지.
- 2번 `obk369369-spec/02-auto-bid-narajangter-v1` 저장소 존재·push 권한 확인. 현재 GitHub 실행본 미식별 HOLD.
- 과거 2번 HTML/규칙에서 예정가격·낙찰하한율 기반 하한가와 추천가 계산, PDF·Excel 공고 분석, 공고유형 분류, 세금/면세 계산 규칙 회수.

## 번호 혼동 금지
- 37번 = 메타데이터 생산·통합검증만.
- 13번 = 엑셀 자동 업로드 도구만.
- 둘을 하나의 메타데이터 작업으로 묶지 않는다.

## 누적 우선순위 상태
- 이메일 수집/고객 DB: 이전 회차 상태 유지, 다음 전체 순환에서 재검증
- 7번 고객 컨택 판단: 이전 회차 상태 유지, 다음 전체 순환에서 재검증
- 1번 고객 자동화 안내서: 최신 GitHub 실행본 미식별 HOLD
- 37번 메타데이터: 규칙 게이트 회수, 과거 충돌 2건 DEPRECATED 판정
- 13번 엑셀 자동 업로드: 현재 GitHub 실행본 발행일 원본연결 46145 회귀 FAIL, 안전 부분수정 수단 대기
- 6번 TOC: v2.26 구조 PASS / 최신 실제 100건 실행 HOLD
- 2번 입찰: 저장소 존재 PASS / 현재 실행본 식별 HOLD / 과거 규칙·HTML 회수 PASS
- 28~31 발행사 업무: 다음 우선 작업
- 나머지 도구/업무대화: 미순환
- 전체 역사문서 감사: 진행 중, 중앙 단일원본에만 흡수

## 사용자 작업 금지
사용자는 이 상태판을 보기만 한다. 테스트, 비교, 캡처, PASS/FAIL 판정, 규칙 저장, 새 대화창 인계문 작성, `계속/진행` 반복 입력을 요구하지 않는다.

## 재시작 지점
1. 현재 우선 작업 흐름을 유지한다.
2. 첫 GitHub heartbeat scheduled run을 확인해 실제 5분 감시가 동작하는지 검증한다.
3. 첫 실제 stall에서 `보고 → 즉시 재개 → 상태판 기록`이 모두 이뤄졌는지 검증한다.
4. 중앙원본 `WIC_GLOBAL_OPERATING_RULES.md`의 안전한 병합 수단이 확보되면 위 영구 주의사항과 2026-08-10 Watchdog 비활성화 실수를 단일원본에 흡수한다.
5. 구조 변경 시 새 단점·공백·중복 위험을 반드시 상태판에 먼저 기록한다.

실행시간: duration not exposed
