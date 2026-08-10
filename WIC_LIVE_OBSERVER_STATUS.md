# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 09:10 KST
상태: ACTIVE — watchdog stall 복구 + 28/29 발행사 관계근거 등급화 진행

이 파일은 사용자가 직접 테스트하지 않고 진행을 관찰하기 위한 외부 상태판이다. 실제 외부 증거가 있을 때만 진행으로 기록한다.

## 이번 회차 실제 작업 — 09:10
- COLLISION GUARD 확인: 직전 상태판 갱신은 08:48 KST로 12분 보호구간을 초과했다.
- `WIC Overnight Completion`은 08:49 KST에 실행된 기록이 있으나 09:10 현재 observer에는 그 실행의 새 작업묶음/새 재시작점/새 외부증거가 저장되지 않았다. 따라서 `stalled — completion run did not persist new observer evidence`로 판정하고 저장된 재시작점에서 복구했다.
- 이전 회차에서 이미 판정한 13번·6번·2번 HOLD와 28번 Gardner/CompositesWorld 근거는 새 증거가 없어 재검사하지 않았다: `SKIP — unchanged evidence`.
- 29번/28번 재시작점에 따라 Global Industry Analysts(GIA)와 Transparency Market Research(TMR)의 과거 커미션 근거를 File Library 원문에서 다시 등급화했다.
- GIA는 2020-10-20 `info411@strategyr.com` 원문 EML에서 Global Industry Analysts, Inc. Sales Team이 WIC 문의에 대해 해당 보고서 판매 시 `30% commission`을 직접 제안한 원문을 확인했다. 따라서 `EXCLUDE — existing direct transaction/commission evidence`, 근거등급 A(발행사 발신 원문)로 승격한다. 다만 이 메일은 특정 판매건 조건이므로 현재 전상품/장기계약 30%가 지금도 유효하다고 자동 확장하지 않는다.
- TMR은 2026-07-08 WIC가 전 TMR 담당자에게 보낸 메일에서 `When we collaborated at Transparency Market Research, we operated under a 50% commission structure`라는 과거 거래조건 진술을 확인했고, 별도 과거 거래처 현황 파일에도 `Transparency Market Research (50% commission)`이 반복 기록돼 있다. 따라서 `EXCLUDE — existing historical business relationship`, 근거등급 B(복수 내부기록 + 후속 이메일의 과거 거래 진술)로 유지한다. 이번 검색에서는 TMR 자체가 발신한 50% 원문 EML/계약서는 아직 식별되지 않아 현재 조건 확정은 HOLD다.
- 증거등급을 A=`발행사 발신 원문/계약/주문서`, B=`복수 내부기록 + 실제 거래맥락`, C=`추천목록/단일 요약기록`으로 구분해 28번 신규후보 제외판정에 적용했다.

## 이번 회차 판정
| 작업 묶음 | 상태 | 외부 증거 | blocker / 개선 | 다음 실행 |
|---|---|---|---|---|
| stall 감지/복구 | PASS | observer 08:48 이후 미갱신 + completion 08:49 실행기록 대비 새 observer evidence 없음 | completion run 자체 내부 종료원인은 노출되지 않음 | 저장 성공 여부를 다음 watchdog에서도 동일 기준으로 판정 |
| GIA 관계근거 | PASS — A등급 | 2020-10-20 `info411@strategyr.com` EML, GIA Sales Team 30% commission 직접 제안 | 현재 장기계약/현재율 유효성은 별도 HOLD | 29번 타임라인에 historical 30% direct evidence로 사용 |
| TMR 관계근거 | PASS — 기존관계 / HOLD — 원문 조건 | 2026-07-08 후속 EML의 과거 50% 거래 진술 + 복수 거래처 현황 기록 | TMR 발신 50% 원문 계약/메일 미식별 | TMR 원문 발견 시 B→A 승격, 없으면 현재조건 HOLD 유지 |
| 28번 제외표 등급화 | PASS(구조) | A/B/C evidence gate 적용 | 검증 단계가 늘어 단순 이름복사보다 느림 | 다음 발행사도 같은 등급으로만 추가 |

## 구조 자기개선 상태
- 원인: 과거 거래처 요약표에는 실제 발행사 원문, 내부기록, 추천목록이 혼합되어 있어 모두 같은 신뢰도로 자동 승계하면 잘못된 제외/계약조건 확정 위험이 있다.
- 변경: 28/29 발행사 관계근거를 A/B/C 3등급으로 분리하고 `현재 조건`은 역사적 관계와 별도 필드로 취급한다.
- 장점: 오래된 커미션 수치를 현재 계약조건으로 오인하거나 추천목록만으로 거래사 판정하는 오류를 줄인다.
- 새 단점: 발행사별 원문 확인 단계가 추가되어 초기 정규화 속도가 느려진다.
- rollback 조건: 더 신뢰도 높은 최신 계약/발행사 원문이 들어오면 해당 발행사 행만 최신 근거로 재판정한다. 등급 체계 자체는 원문보다 낮은 근거를 상위로 올리지 않는 한 유지한다.
- 감시 자동화 수·간격·크레딧 구조는 이번 회차 변경하지 않았다.

## 직전 회차 실제 작업 — 08:48
- 직전 재시작 지점 `28번 기존 거래·접촉·협상·판매 발행사 제외표 미통합`에서 시작했다.
- File Library의 28·29·30 운영문서와 실제 거래/메일 자료를 교차 검색했다.
- 28번 원문은 신규 후보를 조사하기 전에 거래대장·이메일·계약 목록·29/30/31/37 상태와 대조하고, 최소 2개 식별자 또는 원문 기록이 있어야 제외 확정하도록 규정한다.
- 29번 원문은 기존 거래·접촉·협상 발행사를 관리 범위로 두고 있으나 최신 계약서와 자동 대조 전이므로 전체 확정 목록은 HOLD 상태다. 따라서 과거 추천용 VENDOR 목록을 곧바로 '기존 거래사'로 승격하지 않는다.
- 30번 근거자료에서 일본 과거 거래/관리 씨앗으로 씨엠씨출판, 후지키메라, 후지경제, 야노리서치, 기술정보협회, NTS, TRICEPS 및 관련 일본 발행사 거래자료가 존재함을 확인했다. 이들은 28번 신규후보에서 우선 제외/관계확인 대상으로 사용하되 현재 계약 유효성은 별도 HOLD한다.
- Gardner Business Media / CompositesWorld는 2026-06-24 실제 reseller terms 문의 회신과 2026-07 주문서에 20% reseller discount를 반영한 기록을 회수했다. 따라서 28번 신규 발행사 후보로 재추천하지 않고 `EXCLUDE — existing contact/transaction evidence` 씨앗으로 분류한다. 현재 장기 파트너 계약 전체 조건까지 확정한 것은 아니다.
- 과거 1번 도구의 VENDOR 배열이나 고객 추천 문서에 등장한 MarketsandMarkets, Technavio, Grand View Research, Fortune Business Insights 등은 '추천/검색 대상에 등장'했다는 사실만으로 기존 거래사 판정을 하지 않는다. 거래·계약·접촉 원문이 별도로 확인될 때만 제외표에 승격한다.

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
- 28번 해외 신규 발행사 발굴: 기존관계 제외표 씨앗 등급화 진행 / Gardner-CompositesWorld 제외 씨앗 PASS / GIA A등급 PASS / TMR 기존관계 B등급 PASS·현재조건 HOLD / 일본 과거 거래사 씨앗 PASS-HOLD
- 29번 발행사 계약·정산: 역할 경계 PASS / Gardner-CompositesWorld·GIA 실제 접촉/거래 원문 타임라인 이관 가능 / TMR 현재조건 원문 HOLD / 나머지 발행사 근거 정규화 진행 필요
- 30번 일본 계약·정산: 역할 경계 PASS / 과거 거래자료 씨앗 확인 / 개별 최신 계약상태 정규화 대기
- 31번 일본 신규 발행사 발굴: 역할 경계 PASS / 실제 후보조사 미착수
- 나머지 도구/업무대화: 미순환
- 전체 역사문서 감사: 진행 중, 현재 번호와 과거 번호 재사용 충돌을 DEPRECATED historical context로 분리

## 사용자 작업 금지
사용자는 이 상태판을 보기만 한다. 테스트, 비교, 캡처, PASS/FAIL 판정, 규칙 저장, 새 대화창 인계문 작성, `계속/진행` 반복 입력을 요구하지 않는다.

## 재시작 지점
1. 28/29 제외표를 A/B/C 근거등급으로 계속 확장한다. GIA는 A, TMR은 현재 B로 고정한다.
2. TMR 자체 발신 50% 원문 EML/계약서가 있는지 1회 정밀검색하고, 없으면 동일 검색을 반복하지 않고 HOLD 고정한다.
3. 다음으로 Allied Market Research, QY Research, MarketsandMarkets, BCC Research 등 상위 기존 거래처의 발행사 원문/계약 근거를 A/B/C로 분류한다.
4. 실사용 가능한 기존관계 제외표가 확보되면 28번 실제 신규 후보 조사로 이동한다.
5. 중앙 `WIC_GLOBAL_OPERATING_RULES.md`는 전체 내용 보존이 가능한 안전 병합이 확보될 때만 갱신한다.

실행시간: duration not exposed
