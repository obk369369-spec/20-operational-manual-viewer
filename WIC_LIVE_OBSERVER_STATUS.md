# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 11:07 KST
상태: ACTIVE — 28번 기존관계 제외표 원문등급화 진행 / 다음 8개 발행사 evidence package 완료

이 파일은 사용자가 직접 테스트하지 않고 진행을 관찰하기 위한 외부 상태판이다. 실제 외부 증거가 있을 때만 진행으로 기록한다.

## 이번 회차 stall / recovery — 11:07
- COLLISION GUARD: 직전 상태판 최종 확인은 10:48 KST였다. 11:07 KST 기준 약 19분 경과했고 12분 보호창을 넘겼으며, 새 commit/evidence/restart-point 변경이 없어 stale로 판정했다.
- 정확한 stale 증거: observer SHA `bfc30c7aa30acbf543eaa2d6618b163d8eb07a68`의 마지막 기록은 10:48이고 재시작점은 `Mordor Intelligence → Lucintel → Prof Research → AnalystView Market Insights → Bizwit Research & Consulting → Vantage Market Research → DataM Intelligence → Zion Market Research`였다.
- 확인 가능한 원인: 이전 coherent package는 완료됐으나 그 이후 중앙 observer에 새 외부증거가 기록되지 않았다. 런타임 자체 중단 원인은 노출되지 않아 추정하지 않는다.
- RECOVERY: 저장된 재시작점의 8개 업체를 File Library + 연결 Gmail로 직접증거 우선 조사했다. 직전 7개 업체 및 13번/6번/2번의 unchanged HOLD는 `SKIP — unchanged evidence`로 재검사하지 않았다.

## 이번 회차 실제 작업
- 연결 Gmail에서 8개 업체 도메인을 묶어 직접 발신 메일을 검색했으나 결과는 0건이었다. 따라서 이번 회차에서 계약·커미션·인보이스 직접증거는 새로 확보되지 않았다.
- Lucintel: `240903_Meta Sheet-Lucintel.xlsx`가 메타데이터 샘플 검증표에서 READY_SAMPLE로 확인됐다. 실제 메타데이터 취급 근거이므로 `relationship_evidence_grade=B`. 계약/커미션 직접근거는 없어 별도 `C-HOLD`.
- Prof Research: `metadata_prof-2024-10-28-worldic.xlsx`가 READY_SAMPLE로 확인됐다. 실제 메타데이터 취급 근거이므로 관계 B. 계약/커미션 직접근거 없음으로 C-HOLD.
- AnalystView Market Insights: `Meta Data Sheet_worldic.co.kr_31052024.xlsx`가 READY_SAMPLE로 확인됐다. 실제 메타데이터 취급 근거이므로 관계 B. 계약/커미션 직접근거 없음으로 C-HOLD.
- Bizwit Research & Consulting: `Bizwit Titlesheet 20-07-2026 Update - 월드입력.xlsx` 및 수정완료본에서 다수 행의 발행사/카테고리 검증 PASS가 확인됐다. 2026년 실제 메타데이터 처리 근거이므로 관계 B. 계약/커미션 직접근거 없음으로 C-HOLD.
- DataM Intelligence: `DataM Intelligence All Products List APRIL 2021(2).xlsx`가 READY_SAMPLE 및 공통규칙 V2 적용 대상으로 확인됐다. 실제 메타데이터 취급 근거이므로 관계 B. 계약/커미션 직접근거 없음으로 C-HOLD.
- Mordor Intelligence: WIC 홈페이지의 2026년 Mordor 보고서 표시 및 과거 1번 도구의 추천/처리 목록은 확인되지만, 이번 package에서는 발행사 원본 메타데이터·계약·주문·인보이스를 식별하지 못했다. `operational_handling_evidence=B-`, 관계/조건은 C-HOLD로 closure한다.
- Vantage Market Research: 과거 1번 도구/서버의 발행사 도메인 목록 외 직접 원문을 식별하지 못했다. 내부 처리목록만으로는 관계 승격 금지 → operational B-, 관계/조건 C-HOLD.
- Zion Market Research: WIC가 보낸 partnership inquiry 대상 목록과 1번 도구의 발행사 목록에는 존재하지만, 이것은 WIC 발신/내부 목록이며 기존 거래를 증명하지 않는다. operational B-, 관계/조건 C-HOLD.

## 이번 회차 판정
| 작업 묶음 | 상태 | 외부 증거 | blocker / 개선 | 다음 실행 |
|---|---|---|---|---|
| 8개 발행사 Gmail 직접증거 | PASS(검색 종료) | 연결 Gmail domain 묶음 검색 0건 | 연결 계정 밖 과거 메일 가능성 | 새 source 발생 시만 재개 |
| Lucintel | PASS — 관계 B / 조건 HOLD-C | `240903_Meta Sheet-Lucintel.xlsx` READY_SAMPLE | 계약·커미션 직접원문 없음 | 28번 신규후보 제외 유지 |
| Prof Research | PASS — 관계 B / 조건 HOLD-C | `metadata_prof-2024-10-28-worldic.xlsx` READY_SAMPLE | 계약·커미션 직접원문 없음 | 28번 신규후보 제외 유지 |
| AnalystView Market Insights | PASS — 관계 B / 조건 HOLD-C | `Meta Data Sheet_worldic.co.kr_31052024.xlsx` READY_SAMPLE | 계약·커미션 직접원문 없음 | 28번 신규후보 제외 유지 |
| Bizwit Research & Consulting | PASS — 관계 B / 조건 HOLD-C | 2026-07-20 Titlesheet 월드입력/검증 PASS | 계약·커미션 직접원문 없음 | 28번 신규후보 제외 유지 |
| DataM Intelligence | PASS — 관계 B / 조건 HOLD-C | `DataM Intelligence All Products List APRIL 2021(2).xlsx` READY_SAMPLE | 계약·커미션 직접원문 없음 | 28번 신규후보 제외 유지 |
| Mordor Intelligence | HOLD — 운영취급 B- / 관계·조건 C | WIC 2026 판매화면 + 내부 도구 처리목록 | 발행사 직접 원본 미식별 | closure, 새 source 시만 재개 |
| Vantage Market Research | HOLD — 운영취급 B- / 관계·조건 C | 내부 도메인/처리 목록 | 직접 원문 없음 | closure, 새 source 시만 재개 |
| Zion Market Research | HOLD — 운영취급 B- / 관계·조건 C | WIC 발신 partnership inquiry 대상 + 내부 목록 | WIC 발신은 거래증거 아님 | closure, 새 source 시만 재개 |

실행시간: duration not exposed

## 구조 자기개선 상태
- 원인: 발행사 목록/추천코드/WIC 발신 inquiry가 실제 거래관계처럼 섞이면 제외표가 과대확장되고 같은 업체를 반복검색하게 된다.
- 변경: 기존 4단계 evidence gate를 이번 package에도 강제했다: `publisher-direct active evidence(B+/A)`, `actual metadata/order handling(B)`, `internal operational/test handling(B-)`, `internal claim/outbound inquiry only(C)`. 각 업체 package가 closure되면 새 source/메일/commit 전 반복검색을 금지한다.
- 장점: 내부 코드·WIC 발신 문의만으로 기존 거래사를 확정하는 오류와 반복 Gmail/File 검색에 따른 chat/credit 낭비를 줄인다.
- 새 단점/위험: 연결되지 않은 사내 메일, 로컬 PC 계약서, 오래된 외부 저장소에 직접 증거가 있으면 현재 B-/C가 실제보다 낮게 평가될 수 있다. B-/C는 `관계 없음`이 아니라 `현재 연결 증거로 확정 부족`을 뜻한다.
- rollback 조건: 새 발행사 직접 EML/계약/인보이스/주문/원본 메타데이터가 연결되면 해당 업체만 closure 해제하고 재등급한다.
- 검증 결과: Lucintel/Prof/AnalystView/Bizwit/DataM의 실제 메타데이터 파일명을 File Library에서 재확인했고, 연결 Gmail 8개 domain search=0을 독립 확인했다.
- 구조 변경으로 모니터링 자체를 줄이거나 비활성화하지 않았다. 따라서 stale 감지 공백은 새로 만들지 않았다.

## 직전 완료 package 보존 — 10:48
- `Accuray Research / Global Info Research / KBV Research / Coherent Market Insights / Grand View Research / Kuick Research / Prismane Consulting` 직접증거 package 완료.
- Global Info Research 관계 B / 커미션 C-HOLD, Grand View Research 관계 B / 조건 C-HOLD.
- Accuray·Coherent·Prismane 관계/조건 C-HOLD, KBV·Kuick operational B- / 관계·조건 C-HOLD.
- 위 7개는 새 source/메일/commit 전 `SKIP — unchanged evidence`.

## 번호 혼동 금지
- 37번 = 메타데이터 생산·통합검증만.
- 13번 = 엑셀 자동 업로드 도구만.
- 29번 = 발행사 파트너십·계약·커미션·정산 공통관리.
- 30번 = 일본 발행사 파트너십·계약·커미션·정산 상세 실행.
- 31번 = 일본 신규 발행사 발굴·검증·접촉 우선순위.
- 과거 동일 번호의 다른 역할 문서는 역사 기록으로만 취급하며 현재 번호 잠금에 자동 승계하지 않는다.

## 누적 우선순위 상태
- 이메일 수집/고객 DB: 새 증거 없음, 반복 재검사 SKIP.
- 7번 고객 컨택 판단: 17개 운영 게이트/핵심 규칙 원문 회수 PASS / 전용 실행 엔진 미식별 HOLD.
- 1번 고객 자동화 안내서: GitHub 실행본 식별 PASS / 중앙 규칙 연결 PASS / 실제 입력→출력 동작 검증 HOLD.
- 37번 메타데이터: 상품명/한글명/ISBN-CODE 핵심 잠금 PASS / 과거 13번 역할 충돌 DEPRECATED / 실제 신규 입력 없음.
- 13번 엑셀 자동 업로드: 46145 회귀 FAIL 유지 / 새 commit 없음으로 재실행 SKIP.
- 6번 TOC: v2.26 구조 PASS / 최신 실제 100건 실행 HOLD / 새 commit 없음으로 재검사 SKIP.
- 2번 입찰: 저장소 존재 PASS / 현재 실행본 식별 HOLD / 새 commit 없음으로 재검사 SKIP.
- 28번 해외 신규 발행사 발굴: 기존관계 제외표 등급화 진행. Gardner-CompositesWorld 제외 PASS / GIA 관계·30% 직접근거 A / TMR 관계 B·현재조건 HOLD / Allied·QY·BCC 관계 B, 커미션 C-HOLD / MarketsandMarkets 관계 B+·커미션 C-HOLD / BlueWeave 관계 B+·조건 B-HOLD / Global Market Insights 취급 B·계약/조건 C-HOLD / Research in China 취급 B-·계약/40% C-HOLD / Global Info Research 관계 B·45% C-HOLD / Grand View Research 관계 B·30%·40%조건 C-HOLD / Lucintel·Prof Research·AnalystView·Bizwit·DataM 관계 B·조건 C-HOLD / Mordor·Vantage·Zion operational B-·관계/조건 C-HOLD / Accuray·Coherent·Prismane C-HOLD / KBV·Kuick operational B-·관계/조건 C-HOLD. closure 업체는 새 source 전 반복금지.
- 29번 발행사 계약·정산: 관계·운영취급·커미션조건 근거 분리 구조 적용.
- 30번 일본 계약·정산: 역할 경계 PASS / 과거 거래자료 씨앗 확인 / 개별 최신 계약상태 정규화 대기.
- 31번 일본 신규 발행사 발굴: 역할 경계 PASS / 실제 후보조사 미착수.
- 나머지 도구/업무대화: 미순환.
- 전체 역사문서 감사: 진행 중, 현재 번호와 과거 번호 재사용 충돌을 DEPRECATED historical context로 분리.

## 사용자 작업 금지
사용자는 이 상태판을 보기만 한다. 테스트, 비교, 캡처, PASS/FAIL 판정, 규칙 저장, 새 대화창 인계문 작성, `계속/진행` 반복 입력을 요구하지 않는다.

## 재시작 지점
1. 기존관계 제외표의 다음 미등급 업체 `Koncept Analytics → LP Information → Market Monitor Global → WishTree Insight → 99Strategy → Maia Research → The Insight Partners → HNY Research`를 동일 evidence gate로 한 package 처리한다.
2. 이번 회차 8개 및 10:48의 7개 업체는 새 source/메일/commit이 생기기 전 `SKIP — unchanged evidence`.
3. 실제 메타데이터 원본이 있으면 관계 B까지 가능하지만 계약/커미션 숫자는 별도 직접근거 없이는 C-HOLD를 유지한다.
4. WIC 발신 partnership inquiry, 추천코드, 단순 publisher list만 있으면 operational B- 또는 C 이상으로 승격하지 않는다.
5. 제외표가 충분해지면 28번 실제 신규 후보 조사로 이동한다.
6. 중앙 `WIC_GLOBAL_OPERATING_RULES.md`는 전체 내용 보존이 가능한 안전 병합이 확보될 때만 갱신한다.
