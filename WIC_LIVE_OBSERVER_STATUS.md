# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 13:57 KST
상태: ACTIVE — P1 스팸 회피 누락 보완 후 고객응대 루틴 계속

규범 원본은 `WIC_GLOBAL_OPERATING_RULES.md`. 이 파일은 실제 외부 증거와 재시작점만 기록한다. 37번=metadata production/integrated verification, 13번=Excel automatic upload로 분리 유지.

## 대화창 계보 / 이름 관리
- 기준 부모 대화창: `워크 전 준비`
- GitHub 관리명 규칙: 새/파생 작업 세션은 항상 부모 이름을 앞에 이어서 기록한다.
- 현재 작업 세션 GitHub 관리명: `워크 전 준비 → WIC observer-mode 고객응대 루틴`
- 주의: GitHub 관리명은 ChatGPT 사이드바의 실제 대화창 제목을 변경하는 기능이 아니다. 현재 시스템에서 assistant가 사용자의 Chat 목록에 새 대화창을 직접 생성하거나 사이드바 제목을 직접 변경했다고 확인할 수 없다.
- 사용자가 ChatGPT에서 대화창을 삭제했는지 여부를 GitHub connector/assistant가 자동 감지하는 기능은 현재 확인되지 않았다. 따라서 삭제 감지를 전제로 운영하지 않는다.

## PERSIST-BEFORE-SESSION 고정 규칙
- 앞으로 새 Work/파생/자동 생성 작업 세션을 전제로 할 때는, 그 세션에서 필요한 핵심 상태를 먼저 GitHub에 저장한 뒤에만 새 세션을 임시 실행창으로 취급한다.
- 선저장 필수 항목: 부모 대화창=`워크 전 준비`, 작업 목적, 적용 규칙/잠금, 현재 코드·fixture 위치, PASS/HOLD, 마지막 검증 증거, 정확한 재시작점, 아직 GitHub에 흡수되지 않은 사용자 교정사항.
- 저장 후 반드시 GitHub read-back으로 실제 보존을 확인한다.
- 새 세션/대화 자체의 전체 원문이 GitHub에 자동 복제된다고 간주하지 않는다. 작업에 필요한 규칙·증거·상태만 명시적으로 흡수한다.
- 사용자가 임시 작업 대화창을 삭제하더라도 GitHub에 선저장+read-back된 상태에서 재시작할 수 있게 한다.
- 사용자에게 같은 오류·규칙을 다시 설명하도록 요구하지 않는다. 삭제된 대화창에서 GitHub에 흡수되지 않은 내용은 자동 복구 가능하다고 주장하지 않는다.

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
- `P0~P10`은 새 대화창 이름이 아니라 업무 우선순위 표식이다.
- assistant는 현재 시스템에서 사용자 Chat 목록에 새 대화창을 직접 생성하거나 이름 붙일 수 있다고 확인되지 않는다.
- GitHub는 실제 connector로 연결되어 있으며 이 상태판/코드 파일은 직접 fetch/update/read-back 대상으로 사용한다. 단, GitHub 저장 성공은 기능 실행 성공과 동일하지 않으므로 runtime 전에는 HOLD한다.

## self-improvement
- 원인: 대화창/세션 생성과 GitHub 보존 순서가 명확히 잠기지 않아 사용자가 임시 대화창을 삭제할 때 미흡수 정보 손실 위험이 있었다.
- 변경: `PERSIST-BEFORE-SESSION`을 고정하고 부모 이름을 `워크 전 준비`로 수정.
- 이점: 임시 작업창 삭제와 무관하게 핵심 규칙·증거·재시작점은 GitHub에서 이어갈 수 있다.
- 남은 위험: 삭제 전에 GitHub로 한 번도 흡수되지 않은 대화 원문은 자동 복구할 수 없다. Chat 삭제 자체도 자동 감지하지 못한다.
- rollback: 없음. 더 강한 자동 보존 경로가 실제 연결되면 이 규칙을 최소 보존 규칙으로 유지한다.

## 재시작 지점
1. P1 `customer_db_state_machine.py`의 전체 fixture를 일반 runtime에서 실제 실행.
2. PASS면 P1 output -> P2 input handoff adapter 연결.
3. P2 `tool7_contact_judgment.py` 8 fixture 실제 실행.
4. 이어서 P3 Tool1 FULL/INTERMEDIATE guide 실제 mapping.

실행시간: duration not exposed
