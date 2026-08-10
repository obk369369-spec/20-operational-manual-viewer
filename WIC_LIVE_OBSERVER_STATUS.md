# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 15:10 KST
상태: ACTIVE — P1/P2 fixture PASS 유지, P3 Tool1 역사 피드백→실행 회귀계약 추가

규범 원본은 `WIC_GLOBAL_OPERATING_RULES.md`. 이 파일은 외부 증거와 재시작점만 기록한다. 37번=metadata production/integrated verification, 13번=Excel automatic upload로 분리 유지.

## 감시 판정 / 복구
- 직전 observer: 14:05 KST. 15:10 기준 12분 collision window를 초과했고, 최신 :50 실행 이후 observer에 새 evidence/restart 갱신이 없었으므로 복구 실행.
- 기존 P1/P2 PASS/HOLD는 재검사하지 않음: `SKIP — unchanged evidence`.
- 복구 우선순위: **P3 Tool1**, 저장된 재시작점에서 이어감.

## 이번 복구 실제 실행
| 항목 | 실제 결과 | 증거 |
|---|---|---|
| Tool1 과거 피드백 신규 회수 | PASS | Library `1번 고객 자동화 안내서 12.doc`, `16.doc` |
| 역사 규칙→회귀계약 변환 | PASS | `customer_pipeline/tool1_historical_contract.py` |
| runtime fixture | `PASS: 8 deterministic Tool1 historical-contract fixtures` | ordinary Python runtime |
| GitHub read-back | PASS | blob `0a745bcd3d757962b47b1ce31b0f0c2141392d8f` |
| Work gate | `WORK_DEFER_DENIED` | G1/G2/G3 모두 YES |

## 새로 흡수한 Tool1 계약
- 왼쪽 입력은 9개 고정: 영문/한글 타이틀, 발행사, 발행일, 페이지, 정가, 공급가격, 보고서 링크, 목차.
- 생성 버튼 1개.
- 기존 오른쪽 성공/안정 구조를 재설계하지 않고 최소 연결만 허용.
- slot contract: `TITLE.EN`, `META.PUBLISHER`, `META.DATE`, `META.PAGES`, `META.PRICE`, `LINK.TEXT`, `TOC.TEXT`.
- 가운데/오른쪽 값 불일치 또는 값 소실은 `THREE_AREA_VALUE_GAP`; mutation target을 재현 지점으로 보존.
- 새 error_hash: `TOOL001_LEFT_9_FIELDS_ONE_BUTTON_CONTRACT`, `TOOL001_RIGHT_SLOT_MAPPING_MISMATCH`, `TOOL001_STABLE_BASELINE_SCOPE_VIOLATION`.

## GitHub 실제 변경 / read-back
- 신규 회귀계약: `customer_pipeline/tool1_historical_contract.py`, commit `c797c5dd1e52610b7c61ab59845544be476e4023`, blob `0a745bcd3d757962b47b1ce31b0f0c2141392d8f`.
- feedback/work ledger: commit `3ed9353adb9f10d154bccdbaec7c2db35c76272d`.

## PASS / HOLD
| 작업 | 상태 | 이유 |
|---|---|---|
| P1 결정형 DB/send-order gate | PASS — fixture 범위 | 기존 9 fixture, unchanged |
| P2 결정형 Tool7 gate | PASS — fixture 범위 | 기존 8 fixture, unchanged |
| P1→P2 handoff | PASS — fixture 범위 | 기존 6 fixture, unchanged |
| Tool1 synthetic quarantine | PASS — fixture 범위 | 기존 4 fixture |
| Tool1 historical contract | PASS — fixture 범위 | 신규 8 fixture runtime PASS |
| Tool1 실제 안내서 생산 | HOLD | real verified customer/report -> rendered guide -> expected 비교 전 |
| Work 이관 | `WORK_DEFER_DENIED` | Chat/Files, GitHub, ordinary runtime으로 현재 단계 처리 가능 |

## 구조 변경 평가
- 원인: 과거 사용자 피드백이 문서에 남아 있었지만 안정판 보호·9입력·1버튼·slot/값소실 규칙이 실행 가능한 회귀계약으로 고정되지 않아 같은 방향이탈을 반복할 위험.
- 변경: 과거 기록을 실행 가능한 Tool1 regression contract로 변환하고 GitHub에 저장/read-back/runtime 검증.
- 이점: 이후 Tool1 패치가 새 HTML 재설계, 입력/버튼 증식, slot drift, 3영역 값소실을 일으키면 사용자 재테스트 전에 차단 가능.
- 단점/남은 위험: 실제 HTML 브라우저 렌더와 실제 고객/보고서 출력 E2E는 아직 증명하지 않음.
- rollback: 더 강한 사용자 승인 안정판 증거가 충돌을 증명할 때만 해당 contract를 수정; synthetic/demo 편의를 이유로 완화 금지.

## Work gate
- G1 Chat/Files: YES.
- G2 GitHub connector: YES.
- G3 ordinary runtime: YES.
- 결정: `WORK_DEFER_DENIED`; 현재 Work 이관은 `CREDIT_WASTE_FAIL` 위험.

## 정확한 재시작점
1. **P3** real customer + real tradable report가 포함된 과거 사용자 승인 fixture를 신규 evidence로 회수.
2. stable mapper의 실제 DOM/slot id와 real payload를 비교.
3. synthetic 0건 + actual rendered output -> expected comparison fixture를 실행.
4. TOC가 필요한 실보고서가 식별되면 P4 publisher golden fixture 적용 후 P3 복귀.

실행시간: duration not exposed
