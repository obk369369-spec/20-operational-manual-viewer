# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 15:49 KST
상태: ACTIVE — P3 Tool1 verified-data/feedback guard 실제 Tool1 저장소 반영

규범 원본은 `WIC_GLOBAL_OPERATING_RULES.md`. 37번=metadata production/integrated verification, 13번=Excel automatic upload로 분리 유지.

## 현재 우선순위
- P0 live customer blocker: 현재 새 입력 증거 없음.
- P1/P2/P1→P2: 기존 deterministic fixture PASS 범위 유지; 실제 회사 DB/오늘 고객 E2E는 HOLD.
- 현재 실행: **P3 Tool1**.
- 이번 새 피드백/과거증거 분류: `CONSTRAINT + NEW_FIXTURE`, absorbed target=`TOOL001`; 명시적 PRIORITY_CHANGE가 아니므로 기존 P0~P10 순서 유지.

## 이번 회차 새로 처리한 과거 증거
- `1번 고객 자동화 안내서 8.doc`: 고객 DB/직접 옵션/온라인 조건을 받아도 실제 검증된 데이터만 각 안내서 슬롯에 넣고, 잘못된 title/link 등의 수정은 오류 수집→판단 코어 개선으로 이어져야 한다는 규칙 회수.
- `1번 고객 자동화 안내서 23.txt`: 실제 공개 URL, 실제 제목·링크·발행사·발행일·가격·TOC 공개범위 검증 전 PASS 금지; 로그인/캡차/비공개는 HOLD; 오른쪽 안정판 재구성 금지.
- processed chain 8/12/16/23은 다음 회차부터 충돌 증거 없으면 재독해 금지.

## 실제 구현/검증
| 항목 | 상태 | 증거 |
|---|---|---|
| Tool1 실제 저장소 regression guard | 저장/read-back PASS | `obk369369-spec/01-auto-guide-v1/regression/tool1_verified_data_contract.py` |
| commit | PASS | `78d92ac9a1aa06639bdce2f278bcbe973ab3f9af` |
| read-back blob | PASS | `1243533ab80cfcf3f8b04e9fc20d09a550afe04c` |
| ordinary runtime fixtures | PASS | `PASS: 12 deterministic Tool1 verified-data/feedback fixtures` |
| CI workflow | 저장 PASS | `.github/workflows/tool1-verified-data-regression.yml`, commit `5948cc7a6fff016b37bd429f87f85e98ed9119b3` |
| Deno deployment on workflow commit | **FAIL/HOLD** | combined status `deploy/obk369369-spec/01-auto-guide-v1 = failure` |
| real customer/report rendered guide E2E | HOLD | real approved payload + DOM/render expected comparison 아직 없음 |

## 새 error_hash / guard
- `TOOL001_REAL_REPORT_VERIFICATION_GATE`
- `TOOL001_CUSTOMER_CONTEXT_UNVERIFIED`
- `TOOL001_UNKNOWN_FEEDBACK_AREA`
- `TOOL001_FEEDBACK_EVENT_INCOMPLETE`

## 기능 경계
- title_en/title_ko/publisher/date/pages/list price/supply price/report link/TOC 중 빈값 또는 미검증 필드가 있으면 HOLD.
- `example.com`, placeholder, synthetic report tokens는 HOLD.
- 고객 실제 담당업무/근거가 검증되지 않으면 고객 맞춤 안내서 생성 HOLD.
- 가이드의 개별 영역 수정은 guide/report/area/observed/corrected 값을 가진 `CORRECTION` event로 변환하는 contract를 추가.
- 이 회차에서는 안정 HTML/오른쪽 원본 구조를 재작성하지 않음.

## Cross-chat collector 상태
- `WIC 대화창 피드백 수집`은 15:37경 생성되어 15:20 예정시각을 이미 지난 뒤였으므로 15:48 현재 `last_run_time=null`은 누락 실행으로 판정하지 않음.
- 첫 eligible scheduled run: 16:20 KST.
- 별도 대화창 신규 피드백 자동회수→GitHub 반영 실E2E는 여전히 HOLD.

## Work gate
- G1 Chat/Files=YES, G2 GitHub=YES, G3 ordinary runtime=YES.
- 판정: `WORK_DEFER_DENIED`.
- 이번 회차 Work credit 사용 없음.

## self-improvement
- 원인: 과거 Tool1 오류 중 title/link mismatch와 사용자의 반복 수동수정 부담이 규칙문구로만 남으면 재발 가능.
- 변경: 실제 Tool1 저장소에 production-data gate + structured feedback-event fixture를 추가.
- 이점: 검증되지 않은 실제값/placeholder가 안내서 생산 단계로 넘어가는 것을 결정형으로 차단 가능.
- 새 위험: fixture PASS는 실제 브라우저 렌더/배포 성공을 증명하지 않음. 현재 Deno deploy는 failure 상태.
- rollback: 사용자 승인 안정판과 의미 충돌이 확인될 때만 guard를 조정; synthetic 생성 복구 금지.

## 정확한 재시작 지점
1. P0 live customer blocker가 새로 나타나면 즉시 전환.
2. P3 real customer + real tradable report 승인 사례를 신규 evidence에서 계속 회수하되 processed 8/12/16/23 chain은 건너뜀.
3. 실제 payload를 verified-data gate에 통과시킨 뒤 stable mapper DOM/slot에 넣고 rendered output↔expected 비교.
4. P4 TOC가 필요한 실보고서면 해당 publisher golden fixture 적용 후 P3 복귀.
5. 16:20 이후 cross-chat collector 첫 실제 run/evidence를 별도 확인.

사용자 역할: 관찰자. 재설명·재전송·반복 테스트·PASS/FAIL 판정·Work 이관 판단을 요구하지 않는다.
