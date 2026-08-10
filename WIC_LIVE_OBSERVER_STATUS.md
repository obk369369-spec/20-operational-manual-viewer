# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 13:55 KST
상태: ACTIVE — P1 스팸 회피 누락 보완 후 고객응대 루틴 계속

규범 원본은 `WIC_GLOBAL_OPERATING_RULES.md`. 이 파일은 실제 외부 증거와 재시작점만 기록한다. 37번=metadata production/integrated verification, 13번=Excel automatic upload로 분리 유지.

## 이번 회차 우선순위 / 피드백
- 직전 우선순위: P2 Tool7 고객 컨택 판단.
- 사용자 피드백 분류: `CORRECTION` — P1 이메일 수집·3고객군·발송대기 DB에서 과거에 반복 고정된 스팸 회피 구조가 현재 구현/보고에 빠져 있는지 지적.
- absorbed target: P1 customer DB/send-order gate.
- resume point: P1 correction 검증 후 P1->P2 handoff, 이후 P2 기존 재시작점.

## 새로 처리한 과거 증거
- `[이메일 수집 범용 공통 지시문 V5.0].txt`: 원본 수집표와 발송 정렬표 분리; 발송표에는 기관/부서/도메인/직책/기관군 분산을 적용.
- `이메일 수집 대화창용 범용 공통 지시문 v4.0 (스팸 회피 강화형).doc`: 동일 기관 최소 3행, 동일 부서 4행, 동일 도메인 5행, 최소 6개 기관(권장 8~10), 한 기관 최대 20% 규칙.
- `[이메일 수집 대화창 공통 지시문 / 본표 등재·누락 방지·스팸 회피 규칙].txt`: 이메일 수집 단계의 역할에 발송 정렬표 및 기관·도메인 분산이 명시됨.
- `SKIP — unchanged evidence`: 이미 처리한 Tool7 3계열은 이번 P1 correction에서 재독해하지 않음.

## 실제 구현
- 수정 코드: `customer_pipeline/customer_db_state_machine.py`
- commit: `61052ebbd9e5bf1c8c12bab40e7f0c481cd84430`
- 추가된 결정형 gate:
  1. 세 고객군 `NEW_ONLINE / DORMANT_LEDGER / RECENT_TRADE` 외 source cohort HOLD.
  2. 발송표 최소 6개 기관, 권장 목표 8~10개.
  3. 동일 기관 최소 3행 간격.
  4. 동일 부서 최소 4행 간격.
  5. 동일 이메일 도메인 최소 5행 간격.
  6. 한 기관이 전체 발송표 20% 초과 시 HOLD.
  7. 원본 행 데이터 재조합 없이 발송 순서만 다루는 validator.
  8. 스팸 회피 관련 회귀 fixture 추가.
- feedback/work ledger 업데이트: commit `02bc5e5d3e7a07bbb28f4690b7186da51e8381c6`.

## 판정
| 작업 | 상태 | 증거/블로커 | 다음 실행 |
|---|---|---|---|
| P1 과거 스팸 회피 규칙 회수 | PASS — evidence recovered | Library V5/V4/공통지시문 | 처리 인덱스 갱신 |
| P1 스팸 회피 코드 저장 | PASS — GitHub stored | `customer_db_state_machine.py`, commit `61052ebb...` | read-back/runtime |
| P1 기능 PASS | HOLD | 실제 runtime fixture 실행 전 | 일반 runtime 실행 |
| 제목/첫 문장 3종 분산 | HOLD | 실제 send-ready formatter/content module 미식별 | 해당 모듈 발견 후 fixture/patch |
| P2 Tool7 코드 | STORED / FUNCTIONAL HOLD | 직전 8 fixture runtime 미실행 | P1 correction 검증 후 이어서 실행 |
| Work 이관 | WORK_DEFER_DENIED | Chat/Files/GitHub/일반 runtime으로 가능 | Work 사용 금지 |

## 사용자 혼란 방지 구조 설명
- `P0~P10`은 새 대화창 이름이 아니라 **업무 우선순위 표식**이다.
- assistant는 현재 시스템에서 사용자 Chat 목록에 새 대화창을 직접 생성하거나 이름 붙일 수 없다. 과거 파일명에 `새 대화창에서 이어서 진행`이 있어도 그것은 과거 대화 기록/파일 제목이며, 이번 observer 작업이 새 Chat 창을 생성했다는 뜻이 아니다.
- GitHub는 현재 실제 connector로 연결되어 있으며 이 상태판/코드 파일은 GitHub repository에서 직접 fetch/update/read-back 대상으로 사용한다. 단, GitHub 저장 성공은 기능 실행 성공과 동일하지 않으므로 runtime 전에는 HOLD한다.

## self-improvement
- 원인: P1 초기 코드화에서 DB gate를 먼저 만들면서 발송 정렬용 스팸 회피 규칙을 같은 패키지에 흡수하지 못했고, 보고에도 누락이 드러나지 않았다.
- 변경: 사용자 재지적을 P1 correction으로 흡수하고 과거 V5/V4 근거를 실제 validator와 fixture로 전환.
- 이점: 같은 스팸 회피 규칙을 사용자가 준비 대화창마다 다시 말할 필요가 줄고, 발송 순서가 조건을 위반하면 자동 HOLD 가능.
- 남은 위험: 제목/첫 문장 변형과 실제 메일 발송 formatter는 아직 연결되지 않았으므로 수신자 순서 gate와 메일 콘텐츠 분산을 동일한 PASS로 묶지 않는다.
- rollback: 더 최신 사용자 승인 규칙에서 간격 수치가 명시적으로 변경된 증거가 발견되면 fixture와 상수를 함께 교체하고 변경이력을 ledger에 기록.

## 재시작 지점
1. P1 `customer_db_state_machine.py`의 전체 fixture를 일반 runtime에서 실제 실행.
2. PASS면 P1 output -> P2 input handoff adapter 연결.
3. P2 `tool7_contact_judgment.py` 8 fixture 실제 실행.
4. 이어서 P3 Tool1 FULL/INTERMEDIATE guide 실제 mapping.

실행시간: duration not exposed
