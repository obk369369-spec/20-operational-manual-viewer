# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 09:50 KST
상태: ACTIVE — 28번 기존관계 제외표 확장 / BlueWeave 계약원문 등급화

이 파일은 사용자가 직접 테스트하지 않고 진행을 관찰하기 위한 외부 상태판이다. 실제 외부 증거가 있을 때만 진행으로 기록한다.

## 이번 회차 실제 작업 — 09:50
- 저장된 재시작점과 직전 완료기록을 먼저 읽었다. 13번·6번·2번, TMR, Allied/QY/MarketsandMarkets/BCC는 새 commit·원문·상태변화가 없어 `SKIP — unchanged evidence` 처리했다.
- 28번 제외표의 다음 묶음으로 2026-05-29 내부 커미션 현황과 실제 원문 파일을 대조했다.
- BlueWeave Consulting은 `BWC Publisher Agreement 2020_World Industrial Information Center.doc` 원문이 존재하며, 계약문서 자체에 Publisher=BlueWeave Consulting, Reseller=World Industrial Information Center, Reseller name=KYUNG ROK OH, Date=10.12.2020가 기재되어 있다. 따라서 단순 추천목록이나 내부 커미션표보다 강한 실제 관계근거로 판정한다.
- 같은 계약문서 Part IV 11항은 Reseller가 Publisher에 매 판매건의 판매가 기준 최소 50%를 royalty로 지급하도록 규정하고, 할인 발생 시 royalty 금액도 조정하도록 한다. 다만 문서에 Publisher 서명이 확인되지 않고 계약 시작일 상단은 DD/MM/YYYY placeholder가 남아 있으므로 현재 유효한 50% 커미션 확정으로 승격하지 않는다.
- BlueWeave 판정: `relationship_evidence_grade = B+ (계약원문/당사 식별)` / `commission_evidence_grade = B-HOLD (계약문구 존재, 서명·현재 유효성 미확정)` / 28번 신규 발행사 후보에서는 기존관계 제외 대상으로 취급한다.
- Global Market Insights는 2026년 WIC 고객 안내 메일에서 실제 보고서를 판매안내한 흔적이 다수 확인됐지만 이는 WIC 발신 자료이며 발행사 자체 계약·회신 증거가 아니다. 따라서 `실제 취급 흔적 = B`, `발행사와의 계약관계/40% 조건 = C-HOLD`로 분리하고 현재 계약관계 확정 근거로 오인하지 않는다.
- 2026-05-29 내부 커미션표에는 다수 발행사별 조건이 기록돼 있으나, 29번 통합 규칙 자체가 이 표를 기준 스냅샷으로만 쓰고 계약서·최신 이메일·최근 거래로 재검증하도록 잠그고 있다. 따라서 이번 회차에도 내부표 숫자만으로 조건을 A/B 확정하지 않았다.

## 이번 회차 판정
| 작업 묶음 | 상태 | 외부 증거 | blocker / 개선 | 다음 실행 |
|---|---|---|---|---|
| 13·6·2 기존 HOLD | SKIP — unchanged evidence | 직전 observer 재시작점 | 새 증거 없음 | 새 commit/실행증거 발생 시만 재개 |
| TMR/Allied/QY/M&M/BCC | SKIP — unchanged evidence | 직전 등급화 완료 | 새 원문 없음 | 새 원문 발견 시만 조건 승격 |
| BlueWeave 기존관계 | PASS — B+ | `BWC Publisher Agreement 2020_World Industrial Information Center.doc` | Publisher 서명/현재 효력 미확정 | 28번 신규 후보에서 제외 유지 |
| BlueWeave 커미션 조건 | HOLD — B | 계약 Part IV 11~12항: Publisher royalty 최소 50%, 할인 시 조정 | Publisher 서명/현재 유효성 미확정 | 최신 계약/직접 이메일 발견 시 승격 |
| Global Market Insights 취급흔적 | PASS — B(취급) / HOLD-C(계약·조건) | 2026 WIC 고객 발송 안내 메일 다수 | 발행사 자체 계약/회신 미식별 | 발행사 원문 있을 때만 관계조건 승격 |

## 구조 자기개선 상태
- 원인: `고객에게 실제 판매안내한 발행사`와 `발행사와 계약이 확인된 발행사`가 과거 기록에서 한 범주로 섞일 수 있었다.
- 변경: 관계 증거를 `계약/직접발신`, `실제 데이터·취급`, `내부표·자체발신`으로 분리하고, 커미션 조건 등급은 별도 유지한다.
- 장점: 고객 안내메일만 보고 발행사 계약이 확정됐다고 잘못 판단하는 오류를 막는다.
- 새 단점: 동일 발행사에 관계·취급·조건 3개 상태를 유지해야 해 초기 정규화 필드가 늘어난다.
- rollback 조건: 최신 서명계약이나 발행사 직접발신 메일이 확보되면 해당 발행사 관계/조건 등급만 상향한다. 분리 구조 자체는 유지한다.
- 감시 자동화 수·간격·크레딧 구조는 이번 회차 변경하지 않았다.

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
- 28번 해외 신규 발행사 발굴: 기존관계 제외표 등급화 진행 / Gardner-CompositesWorld 제외 PASS / GIA 관계·30% 직접근거 A / TMR 관계 B·현재조건 HOLD / Allied·QY·MarketsandMarkets·BCC 관계 B, 커미션 C-HOLD / BlueWeave 관계 B+·조건 B-HOLD 추가
- 29번 발행사 계약·정산: 관계·취급·커미션조건 근거 분리 구조 적용 / BlueWeave 현재효력 재검증 필요
- 30번 일본 계약·정산: 역할 경계 PASS / 과거 거래자료 씨앗 확인 / 개별 최신 계약상태 정규화 대기
- 31번 일본 신규 발행사 발굴: 역할 경계 PASS / 실제 후보조사 미착수
- 나머지 도구/업무대화: 미순환
- 전체 역사문서 감사: 진행 중, 현재 번호와 과거 번호 재사용 충돌을 DEPRECATED historical context로 분리

## 사용자 작업 금지
사용자는 이 상태판을 보기만 한다. 테스트, 비교, 캡처, PASS/FAIL 판정, 규칙 저장, 새 대화창 인계문 작성, `계속/진행` 반복 입력을 요구하지 않는다.

## 재시작 지점
1. 2026-05-29 내부 커미션표의 다음 상위 업체들 중 실제 계약/직접발신/주문/메타데이터 원문이 있는 업체만 묶어서 등급화한다.
2. `계약/직접발신`과 `실제 취급`을 분리 유지하고, 내부표 수치는 원문 없으면 C-HOLD를 유지한다.
3. BlueWeave 최신 서명계약 또는 직접발신 갱신메일이 별도 자료에서 발견될 때만 현재조건 등급을 올린다. 동일 계약파일 반복검사는 금지한다.
4. 제외표가 충분해지면 28번 실제 신규 후보 조사로 이동한다.
5. 중앙 `WIC_GLOBAL_OPERATING_RULES.md`는 전체 내용 보존이 가능한 안전 병합이 확보될 때만 갱신한다.

실행시간: duration not exposed
