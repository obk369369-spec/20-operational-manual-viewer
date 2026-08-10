# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 10:48 KST
상태: ACTIVE — 28번 기존관계 제외표 원문등급화 진행 / 7개 발행사 직접증거 closure

이 파일은 사용자가 직접 테스트하지 않고 진행을 관찰하기 위한 외부 상태판이다. 실제 외부 증거가 있을 때만 진행으로 기록한다.

## 이번 회차 실제 작업 — 10:48
- ANTI-REPEAT: 직전 재시작점과 완료기록을 먼저 읽었다. 13번·6번·2번 및 이미 closure된 Research in China/Technavio/Future Markets/RNCOS/Transparency/GlobalData/INKWOOD는 새 source/메일/commit 변화가 없어 재검사하지 않았다.
- 저장된 재시작점의 7개 업체 `Accuray Research / Global Info Research / KBV Research / Coherent Market Insights / Grand View Research / Kuick Research / Prismane Consulting`을 한 묶음으로 직접증거 우선 검사했다.
- 연결 Gmail에서 7개 발행사 domain을 묶어 검색했으나 직접 발신 메일은 0건이었다. 따라서 Gmail 기준으로 계약·커미션·인보이스 직접증거는 새로 확보되지 않았다.
- File Library에서는 `Global Info Research new metadata (3480 and 4480 USD version) on Jul. 14 2026.xlsx`가 READY_SAMPLE로 존재하며 원본 데이터 648행이 확인됐다. 이는 2026년 실제 메타데이터 수령/취급 근거이므로 Global Info Research의 `relationship_evidence_grade`는 B로 판정한다. 2026-05-29 내부표의 45% commission은 발행사 직접 원문이 아니므로 `commission_evidence_grade=C-HOLD`를 유지한다.
- File Library에서는 `GVR_Metadata_May 2026.xlsx`가 READY_SAMPLE로 존재하며 원본 데이터 283행이 확인됐다. 이는 2026년 실제 메타데이터 수령/취급 근거이므로 Grand View Research의 관계는 B로 판정한다. 내부표의 30% commission 및 월 USD 15,000~20,000 매출 시 40%로 상향한다는 조건은 직접 계약/메일이 아니므로 C-HOLD로 분리한다.
- Coherent Market Insights는 28개 발행사 샘플대조표에서 `미수신 / MISSING_FILE`로 확인됐다. 내부 커미션표에는 50%가 적혀 있으나 직접 발신·계약·메타데이터 원본이 없어 관계/조건 모두 C-HOLD로 유지한다.
- Accuray Research와 Prismane Consulting은 이번 File Library 검색에서 2026-05-29 내부 거래처/커미션표 외 직접 계약·발행사 발신·주문·인보이스·메타데이터 원문을 식별하지 못했다. 각각 내부 주장만 있으므로 C-HOLD로 closure한다.
- KBV Research와 Kuick Research는 과거 내부 TOC/처리 대상 기록에는 포함되지만 이것은 발행사 직접 거래증거가 아니다. 따라서 `operational_handling_evidence=B-` 보조표시만 허용하고, 관계 확정 및 커미션은 C-HOLD로 유지한다. KBV는 내부표에도 `계약서 X, 40%`가 명시되어 있어 현재조건 확정 금지다.
- SELF-IMPROVEMENT 적용: `실제 메타데이터 원본 수령(B)`과 `내부 파이프라인에서 이름이 처리된 흔적(B-)`을 분리했다. 앞으로 내부 테스트/처리 목록만으로 기존 거래사를 B로 승격하지 않는다.

## 이번 회차 판정
| 작업 묶음 | 상태 | 외부 증거 | blocker / 개선 | 다음 실행 |
|---|---|---|---|---|
| 7개 발행사 Gmail 직접증거 검사 | PASS(검색 종료) | 연결 Gmail domain 묶음 검색 0건 | 연결 계정 밖 메일 가능성은 남음 | 새 메일/source 발생 시만 재개 |
| Global Info Research | PASS — 관계 B / 커미션 HOLD-C | 2026-07-14 메타데이터 원본 648행 READY_SAMPLE | 45% 직접 계약/메일 없음 | 28번 기존관계 제외 유지 |
| Grand View Research | PASS — 관계 B / 커미션 HOLD-C | GVR_Metadata_May 2026.xlsx 283행 READY_SAMPLE | 30%·40% 조건 직접근거 없음 | 28번 기존관계 제외 유지 |
| Coherent Market Insights | HOLD — C/C | 샘플대조표 `미수신 / MISSING_FILE` + 내부 50% 표 | 직접 원문 없음 | 새 원본 수신 시 재개 |
| Accuray Research | HOLD — C/C | 내부 50% 표만 확인 | 직접 원문 없음 | closure, 새 증거 시만 재개 |
| KBV Research | HOLD — 운영취급 B- / 관계·조건 C | 과거 내부 처리목록 + 내부표 `계약서 X, 40%` | 발행사 직접 원문 없음 | closure, 새 증거 시만 재개 |
| Kuick Research | HOLD — 운영취급 B- / 관계·조건 C | 과거 내부 TOC 처리목록 + 내부 40% 표 | 발행사 직접 원문 없음 | closure, 새 증거 시만 재개 |
| Prismane Consulting | HOLD — C/C | 내부표 `20%, 최초 1회 30%` 주장만 | 발행사 직접 원문 없음 | closure, 새 증거 시만 재개 |

## 구조 자기개선 상태
- 원인: 과거 자동화/TOC 로그에 발행사명이 등장한 사실을 실제 거래관계와 같은 수준으로 해석하면 기존거래사 제외표가 과대확장될 수 있다.
- 변경: 증거를 `publisher-direct active evidence(B+/A)`, `actual metadata/order handling(B)`, `internal operational/test handling(B-)`, `internal claim only(C)`로 분리한다. 커미션/계약조건은 별도 등급을 유지한다.
- 장점: 단순 테스트 대상·추천 목록·파이프라인 처리명단을 실제 거래사로 오인하는 것을 막고, 28번 신규 후보 제외 정확도를 높인다.
- 새 단점/위험: 로컬 PC나 연결되지 않은 사내 메일에 직접 계약근거가 있으면 현재 등급이 실제보다 낮게 잡힐 수 있다. 따라서 C/B-는 `관계 없음`이 아니라 `현재 연결 증거로 확정 부족`을 뜻한다.
- rollback 조건: 새 발행사 직접 EML/계약/인보이스/주문/메타데이터 발신 원문이 연결되면 해당 업체만 closure 해제 후 재등급한다.
- 검증 결과: Global Info Research 648행, Grand View Research 283행, Coherent MISSING_FILE을 File Library 원본 대조표에서 재확인했고 동일 7개 업체 반복검색 금지 기준을 저장했다.

## 번호 혼동 금지
- 37번 = 메타데이터 생산·통합검증만.
- 13번 = 엑셀 자동 업로드 도구만.
- 29번 = 발행사 파트너십·계약·커미션·정산 공통관리.
- 30번 = 일본 발행사 파트너십·계약·커미션·정산 상세 실행.
- 31번 = 일본 신규 발행사 발굴·검증·접촉 우선순위.
- 과거 동일 번호의 다른 역할 문서는 역사 기록으로만 취급하며 현재 번호 잠금에 자동 승계하지 않는다.

## 누적 우선순위 상태
- 이메일 수집/고객 DB: 새 증거 없음, 반복 재검사 SKIP
- 7번 고객 컨택 판단: 17개 운영 게이트/핵심 규칙 원문 회수 PASS / 전용 실행 엔진 미식별 HOLD
- 1번 고객 자동화 안내서: GitHub 실행본 식별 PASS / 중앙 규칙 연결 PASS / 실제 입력→출력 동작 검증 HOLD
- 37번 메타데이터: 상품명/한글명/ISBN-CODE 핵심 잠금 PASS / 과거 13번 역할 충돌 DEPRECATED / 실제 신규 입력 없음
- 13번 엑셀 자동 업로드: 46145 회귀 FAIL 유지 / 새 commit 없음으로 재실행 SKIP
- 6번 TOC: v2.26 구조 PASS / 최신 실제 100건 실행 HOLD / 새 commit 없음으로 재검사 SKIP
- 2번 입찰: 저장소 존재 PASS / 현재 실행본 식별 HOLD / 새 commit 없음으로 재검사 SKIP
- 28번 해외 신규 발행사 발굴: 기존관계 제외표 등급화 진행. Gardner-CompositesWorld 제외 PASS / GIA 관계·30% 직접근거 A / TMR 관계 B·현재조건 HOLD / Allied·QY·BCC 관계 B, 커미션 C-HOLD / MarketsandMarkets 관계 B+·커미션 C-HOLD / BlueWeave 관계 B+·조건 B-HOLD / Global Market Insights 취급 B·계약/조건 C-HOLD / Research in China 취급·내부관계 B-, 계약·40% C-HOLD / Global Info Research 관계 B·45% C-HOLD / Grand View Research 관계 B·30% 및 40%조건 C-HOLD / Accuray·Coherent·Prismane C-HOLD / KBV·Kuick 운영취급 B-, 관계·조건 C-HOLD / 이미 closure된 업체는 새 source 전 반복금지
- 29번 발행사 계약·정산: 관계·운영취급·커미션조건 근거 분리 구조 적용
- 30번 일본 계약·정산: 역할 경계 PASS / 과거 거래자료 씨앗 확인 / 개별 최신 계약상태 정규화 대기
- 31번 일본 신규 발행사 발굴: 역할 경계 PASS / 실제 후보조사 미착수
- 나머지 도구/업무대화: 미순환
- 전체 역사문서 감사: 진행 중, 현재 번호와 과거 번호 재사용 충돌을 DEPRECATED historical context로 분리

## 사용자 작업 금지
사용자는 이 상태판을 보기만 한다. 테스트, 비교, 캡처, PASS/FAIL 판정, 규칙 저장, 새 대화창 인계문 작성, `계속/진행` 반복 입력을 요구하지 않는다.

## 재시작 지점
1. 2026-05-29 내부 커미션표의 다음 미등급 업체 `Mordor Intelligence → Lucintel → Prof Research → AnalystView Market Insights → Bizwit Research & Consulting → Vantage Market Research → DataM Intelligence → Zion Market Research` 순으로 직접 계약·발행사 메일·주문·인보이스·실제 메타데이터 원문이 잡히는 업체만 등급화한다.
2. 이번 7개 업체는 새 source/메일/commit이 생기기 전 반복검색 금지.
3. 실제 메타데이터 원본이 있으면 관계 B까지 가능하지만 커미션 숫자는 별도 직접근거 없이는 C-HOLD를 유지한다.
4. 내부 테스트/TOC 처리목록만 있으면 `operational_handling B-` 이상으로 승격하지 않는다.
5. 제외표가 충분해지면 28번 실제 신규 후보 조사로 이동한다.
6. 중앙 `WIC_GLOBAL_OPERATING_RULES.md`는 전체 내용 보존이 가능한 안전 병합이 확보될 때만 갱신한다.

실행시간: duration not exposed
