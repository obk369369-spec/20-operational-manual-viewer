# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 14:05 KST
상태: ACTIVE — P1/P2 runtime 검증 PASS, P3 Tool1 실데이터 격리 단계

규범 원본은 `WIC_GLOBAL_OPERATING_RULES.md`. 이 파일은 외부 증거와 재시작점만 기록한다. 37번=metadata production/integrated verification, 13번=Excel automatic upload로 분리 유지.

## 현재 우선순위 / 피드백
- 시작 우선순위: P1 correction 검증 -> P2 runtime -> P1→P2 handoff -> P3 Tool1.
- 사용자 피드백 분류: 기존 P1 스팸회피 누락은 `CORRECTION`; 의도 추론 금지/Chat-first/관찰자 역할은 `CONSTRAINT`. PRIORITY_CHANGE 없음.
- 현재 우선순위: **P3 Tool1 full/intermediate guide with real verified data**.

## 이번 회차 실제 실행
| 항목 | 실제 결과 | 범위 |
|---|---|---|
| P1 customer DB/send-order | `PASS: 9 deterministic P1 fixtures` | 일반 Python runtime 실제 실행 |
| P2 Tool7 judgment | `PASS: 8 deterministic P2 fixtures` | 일반 Python runtime 실제 실행 |
| P1→P2 handoff | `PASS: 6 deterministic P1->P2 handoff fixtures` | 신규 adapter + runtime |
| P3 synthetic quarantine | `PASS: 4 deterministic Tool1 quarantine fixtures` | synthetic 탐지/real field gate fixture |

## GitHub 실제 변경 / read-back
- P1 send-order: `customer_pipeline/customer_db_state_machine.py`, commit `61052ebbd9e5bf1c8c12bab40e7f0c481cd84430`.
- P2 Tool7: `customer_pipeline/tool7_contact_judgment.py`, commit `84497e2c6e4e6778f8482bdbeec84ce45ee37346`.
- P1→P2 adapter: `customer_pipeline/p1_to_p2_handoff.py`, commit `1adbcfef1d2b0ad54f87157b9fb8b96b01cabaf2`, blob `fe815f4875817e32bdd4c696cae41bacc05b2089`.
- Tool1 quarantine fixture: `customer_pipeline/tool1_synthetic_data_guard.py`, commit `456fbf27d41a2ba109de9536c8cfe91101522406`, blob `d731d6cf78230c2c69dd028504e6e4ac6e033b5b`.
- feedback/work ledger updated this run: commit `48311e0827e2a701d771ab84ffedded39dabc4cf`.

## 새로 처리한 역사 증거 — P3만, 기존 P1/P2는 재독해 안 함
- `안내서_전체_연결버전.html`: 실제 입력 필드(영문/한글 타이틀, 발행사, 발행일, 페이지, 가격, 링크, TOC)를 안내서 슬롯에 직접 매핑하는 stable candidate.
- 과거 사용자 기록: 임의로 새 디자인을 만들지 말고 원래 만들어진 안내서 버전 위에 필요한 연결만 붙이는 방향을 요구.
- `1번도구_정상미리보기_좌중우_5안내서_v14.html`: `${kw} Market Report`, 임의 페이지/가격, 공통 worldic 링크 등 synthetic generation 존재 확인.
- 판정: v14/RUN은 production-safe 기준이 아니라 historical development evidence; synthetic report generation은 격리 유지.
- `SKIP — unchanged evidence`: 직전 처리한 이메일 V4/V5와 Tool7 3계열은 이번 회차 재독해하지 않음.

## PASS / HOLD
| 작업 | 상태 | 이유 |
|---|---|---|
| P1 결정형 DB/send-order gate | PASS — fixture 범위 | 실제 input->runtime->assert 비교 완료 |
| P1 실제 회사 DB 연결 | HOLD | 실제 회사 customer DB/runner 미식별 |
| 제목/첫 문장 3종 분산 | HOLD | send-ready formatter 미식별 |
| P2 결정형 Tool7 gate | PASS — fixture 범위 | 8 fixture runtime PASS |
| P1→P2 handoff | PASS — fixture 범위 | 세 cohort + missing verification + no-inference 검증 |
| P2 실고객 end-to-end | HOLD | 실제 오늘 고객 레코드 연결 전 |
| Tool1 synthetic quarantine test | PASS | historical synthetic signatures 탐지 fixture runtime PASS |
| Tool1 실제 안내서 생산 | HOLD | real report input -> actual guide output -> expected 비교 전 |
| Work 이관 | `WORK_DEFER_DENIED` | G1 Chat/Files=YES, G2 GitHub=YES, G3 runtime=YES |

## self-improvement
- 원인: 과거 Tool1 개발판에는 실제 보고서가 없어도 제목·페이지·가격·링크를 생성하는 경로가 있어 shell/미리보기 성공이 실제 안내서 성공처럼 보일 위험이 있음.
- 변경: `TOOL001_SYNTHETIC_REPORT_DATA` quarantine fixture를 실제 GitHub 자산으로 만들고 runtime PASS 확인.
- 이점: 이후 Tool1 후보가 synthetic 생성 패턴을 포함하면 production PASS 전에 차단 가능.
- 단점/남은 위험: quarantine test는 실제 HTML UI를 수정하지 않으며 실보고서 출력 E2E를 대신하지 않음.
- rollback: 사용자 승인 실데이터 생성 규칙이 별도로 증명되지 않는 한 synthetic 허용으로 되돌리지 않음.

## Work gate
- G1 Chat/Files: YES.
- G2 GitHub connector: YES.
- G3 ordinary runtime: YES.
- 결정: `WORK_DEFER_DENIED`.
- 현재 Work 사용 시 historical re-analysis/terminal-suitable test에 해당하므로 `CREDIT_WASTE_FAIL` 위험.

## 정확한 재시작점
1. **P3** 실제 고객 + 실제 거래가능 보고서가 포함된 과거 Tool1 사용자 승인 fixture를 신규 evidence로 회수.
2. `안내서_전체_연결버전.html`의 slot mapping을 실데이터 payload와 비교.
3. real input -> actual guide output -> expected comparison fixture 생성 및 실행.
4. TOC가 필요한 실보고서가 식별되면 P4로 잠시 들어가 해당 publisher golden fixture를 적용한 뒤 P3로 복귀.

실행시간: duration not exposed
