# WIC FEEDBACK → REGRESSION / CHAT → WORK GATE LEDGER

상태: ACTIVE / NON-NORMATIVE EVIDENCE LEDGER
규범 원본: `WIC_GLOBAL_OPERATING_RULES.md`
영구 파이프라인: `HISTORY_EVIDENCE -> CLASSIFY -> RULE/EXPECTED_OUTPUT -> FIXTURE/ERROR_HASH -> ACTUAL_PATCH -> VERIFY -> READ_BACK -> REUSE -> RESTART_POINT`

## Work gate
G1 Chat/Files, G2 GitHub, G3 일반 runtime 중 하나라도 가능하면 `WORK_DEFER_DENIED`. G1~G3 모두 불가 + 구체적 Work-only blocker + exact handoff package가 있을 때만 `WORK_ELIGIBLE`. 과거규칙 재독해/파일검색/터미널 가능 테스트를 Work로 보내면 `CREDIT_WASTE_FAIL`.

## P1 customer DB / send-order
- last_processed_evidence: 이메일수집 V5/V4/본표·스팸회피 공통 규칙 + 2026-08-10 사용자 CORRECTION.
- implementation: `customer_pipeline/customer_db_state_machine.py`.
- patch commit: `61052ebbd9e5bf1c8c12bab40e7f0c481cd84430`.
- locked regression assets: 3고객군 검증, MAIN_DB/HOLD/중복, 소개서·명함 재발송 방지, 최소 6기관(권장 8~10), 동일기관 3행/부서 4행/도메인 5행, 기관 20% 초과 HOLD.
- error signatures: `MIN_6_ORGANIZATIONS_NOT_MET`, `ORGANIZATION_SPACING_VIOLATION`, `DEPARTMENT_SPACING_VIOLATION`, `DOMAIN_SPACING_VIOLATION`, `ORGANIZATION_RATIO_OVER_20_PERCENT`.
- verification 2026-08-10 14:05 KST: ordinary Python runtime에서 `run_fixtures()` 실제 실행 → `PASS: 9 deterministic P1 fixtures`.
- functional scope PASS: 결정형 P1 DB/send-order gate fixture 범위.
- still HOLD: 실제 회사 customer DB artifact/runner 연결, 제목·첫 문장 3종 분산 formatter 연결.
- next_unprocessed_evidence: 실제 회사 customer DB/runner 또는 send-ready formatter가 식별될 때만 재개; 동일 문서 재독해 금지.
- Work gate: G1=YES, G2=YES, G3=YES → `WORK_DEFER_DENIED`.

## P2 TOOL007 고객 컨택 판단
- source evidence processed: `7번 고객 컨택 판단 도구 5...`, `7번 고객 컨택 판단.doc`, `7번 고객 컨택 판단 도구 7.txt`.
- implementation: `customer_pipeline/tool7_contact_judgment.py`, commit `84497e2c6e4e6778f8482bdbeec84ce45ee37346`.
- key rule: 고객상태 -> 접촉가능 여부 -> 채널 -> 멘트. 현재 재직/회사방향 확인 전 copy 금지; 일방발송/CC를 고객 직접 니즈로 과대해석 금지; 오래된 장부 메모는 보조 맥락만; 추천자료 실재/유료/거래가능 검증.
- error signatures: `COMPANY_DIRECTION_MISSING`, `CURRENT_EMPLOYMENT_UNVERIFIED`, `MOVED_OR_LEFT_HOLD`, `CONTACT_STOP`, `ONE_WAY_NOTICE_NOT_CUSTOMER_NEED`, `CC_HISTORY_NOT_DIRECT_INQUIRY`, `FREE_REPORT_EXCLUDED`, `NON_TRADABLE_PUBLISHER`.
- verification 2026-08-10 14:05 KST: ordinary Python runtime 실제 실행 → `PASS: 8 deterministic P2 fixtures`.
- functional scope PASS: Tool7 결정형 contact/recommendation gate fixture 범위.
- still HOLD: 실제 오늘 고객 레코드와의 end-to-end 판단/전화문구 출력.
- Work gate: `WORK_DEFER_DENIED`.

## P1 -> P2 deterministic handoff — 2026-08-10 14:05 KST
- feedback classification: 기존 `CONSTRAINT`(의도 추론 금지) 흡수, PRIORITY_CHANGE 없음.
- implementation: `customer_pipeline/p1_to_p2_handoff.py`.
- commit: `1adbcfef1d2b0ad54f87157b9fb8b96b01cabaf2`.
- expected: `NEW_ONLINE/DORMANT_LEDGER/RECENT_TRADE` 모두 동일 handoff 사용; P1 MAIN_DB/UPDATE_EXISTING만 통과; 재직/회사방향 명시 검증 없으면 HOLD; 문의/구매 의도는 누락 시 False로 명시하고 추론하지 않음.
- error signatures: `P1_NOT_READY_FOR_P2`, `INVALID_SOURCE_COHORT`, `P2_VERIFICATION_MISSING`.
- verification: GitHub read-back blob `fe815f4875817e32bdd4c696cae41bacc05b2089`; ordinary Python runtime → `PASS: 6 deterministic P1->P2 handoff fixtures`.
- functional scope PASS: handoff fixture 범위.
- still HOLD: 실제 회사 customer DB 입력.
- Work gate: `WORK_DEFER_DENIED`.

## P3 TOOL001 — newly processed evidence 2026-08-10 14:05 KST
- newly processed Library evidence:
  - `안내서_전체_연결버전.html`: 영문/한글 타이틀, 발행사, 발행일, 페이지, 정가, 공급가, 링크, TOC를 입력값 그대로 오른쪽 안내서 슬롯에 반영하는 mapper 후보. 사용자 과거 지시에는 새로 마음대로 재구성하지 말고 원래 안내서 버전을 기준으로 연결하라는 내용이 있음.
  - `1번도구_정상미리보기_좌중우_5안내서_v14.html`: `${kw} Market Report ${year}`, `${kw} Industry Outlook`, 임의 page `160+i*20`, 임의 가격 `320+i*10만원`, 공통 `https://www.worldic.co.kr` 링크 등 synthetic report generation이 실제 코드에 존재.
- classification: `NEW_FIXTURE` + historical `CORRECTION` recovery.
- error_hash: `TOOL001_SYNTHETIC_REPORT_DATA`; missing real field gate `TOOL001_REAL_REPORT_FIELDS_MISSING`.
- regression asset: `customer_pipeline/tool1_synthetic_data_guard.py`.
- commit: `456fbf27d41a2ba109de9536c8cfe91101522406`.
- GitHub read-back blob: `d731d6cf78230c2c69dd028504e6e4ac6e033b5b`.
- runtime verification: ordinary Python runtime → `PASS: 4 deterministic Tool1 quarantine fixtures`.
- PASS meaning: synthetic-data quarantine test 자체는 PASS. **Tool1 UI/guide production 기능 PASS가 아님**.
- Tool1 production status: HOLD. 실제 검증된 보고서 payload -> `안내서_전체_연결버전.html` 계열 stable mapper -> 실제 안내서 output -> expected 비교가 필요.
- next_unprocessed_evidence: 실제 고객/실제 보고서가 들어간 사용자 승인 안내서 fixture, 원본 안내서 slot mapping, first_fail/error_hash/DOM sync 기록 중 아직 미처리 항목.
- Work gate: G1=YES/G2=YES/G3=YES → `WORK_DEFER_DENIED`; 현재 Work 이관 금지.

## TOOL006
- known: MarketsandMarkets upper-level/indent/merged-split/numeric-only/List-of-*/TOC2/revalidation 문제. P3/P4 실고객 안내서가 요구할 때 golden fixture 우선 회수.

## TOOL013 / TOOL037 NUMBER LOCK
- 13번 = Excel automatic upload only.
- 37번 = metadata production/integrated verification only.
- 결합 금지.

## exact restart point
1. P3: 실제 고객/실제 거래가능 보고서가 포함된 과거 Tool1 승인 fixture를 신규 evidence로 회수.
2. `안내서_전체_연결버전.html`의 실제 slot mapping과 real payload를 비교하여 synthetic 0건 조건으로 guide fixture 생성.
3. 실제 input -> output -> expected comparison이 되기 전 Tool1 생산 PASS 금지.
4. P4 TOC가 필요한 실보고서가 식별되면 해당 publisher golden fixture를 먼저 적용.

## 사용자 역할
관찰자. 과거 오류 재설명, 동일 파일 재전송, 반복 테스트, PASS/FAIL 판정, 규칙 정리, Work 이관 판단을 요구하지 않는다.
