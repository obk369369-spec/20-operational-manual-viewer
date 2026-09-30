# Chat42 handoff checkpoint — 2026-09-30

## 이동 사유
현재 고객 안내 대화창 길이 한계 도달. 다음 대화창은 이 checkpoint와 중앙 master를 먼저 읽고 이어서 작업한다.

## 현재 작업
CAR-026 장명진 / 한국섬유개발연구원 / 신사업기획팀 / 팀장.

사용자 제공 장부 현재 행은 과거 실제 발송 원문 없음/UNSENT로 적혀 있으나, 이 대화에서 사용자가 첨부한 과거 발송 EML을 직접 확인했다. 다음 창은 UNSENT를 사실로 전제하지 말고 아래 실제 발송 이력을 우선 사용한다.

### 실제 과거 발송 이력
- 2024-09-10: Global Market Insights — Healthcare Fabrics Market; Global Info Research — Global Medical Textile Supply, Demand and Key Producers, 2024-2030; Mordor Intelligence — Medical Textiles Market...
- 2024-11-25: Bizwit Research & Consulting — Global Biomedical Textiles Market...; AnalystView Market Insights — Antimicrobial Medical Textiles Market...; Orion Market Research — Biomedical Textiles Market...
- 2025-06-30: Cognitive Market Research — Plant Fiber Market Report 2025 (Global Edition); Grand View Research — Natural Fiber Market...; IndustryARC — Recycled Fibers Market...
- 2024-11-25 발송문에는 직전 주 유선으로 이야기했다는 WIC 문구가 있어 전화 접촉 흔적은 있으나, 고객이 이메일로 회신했다는 증거로 확대하지 않는다.

### 현재 고객 적합축
- 신사업기획
- 금속사 기반 무납 방사선 차폐 섬유
- 스마트/전도성 섬유
- 스마트·전도성·방사선 차폐/보호 섬유
- 사용자 제공 KCI 근거: https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003309239

## 이번 대화에서 새로 확정된 보고서 선정 HARD RULE
1. CAR-026 이번 선정은 공식 영문 보고서 타이틀의 첫 단어가 정확히 `Global`인 자료만 허용한다. South Korea/국가판/지역판은 금지. 제목 중간에 Global Forecast가 있는 것만으로는 통과 아님.
2. 원발행사 공식 사이트 ONLY. MarketResearch.com, ResearchAndMarkets 등 reseller/aggregator/판매대행 사이트는 검색 근거·검증 근거·후보 선정 근거·최종 링크로 사용 금지.
3. reseller에서 후보를 발견해도 그 데이터를 사용하지 말고 원발행사 공식 상세페이지를 다시 찾아 처음부터 검증한다. 공식 페이지를 못 찾으면 후보 탈락.
4. WIC 거래 발행사 고정 풀 안에서 우선/필수 선정하고 QYResearch 제외.
5. 2026 자료 우선.
6. 고객당 3종은 가능하면 서로 다른 발행사. 동일 발행사를 연속 3회 이상 선정 금지. 최근 고객/선정 발행사 이력을 먼저 확인하고 풀 전체를 순환한다.
7. 과거 CAR-026 발송 주제(의료/바이오메디컬/항균 의료섬유, plant/natural/recycled fiber)와 동일·단순 업데이트 반복을 피하고 현재 스마트/전도성/차폐 업무에 맞춘다.
8. TOC는 해당 원발행사 공식 상세페이지에 실제 공개된 동일 보고서의 full TOC 원문만 사용. title/segmentation/scope/description에서 목차 추론 금지, 다른 보고서 목차 차용 금지, 누락 보충 금지.
9. 안내서 TOC 편집은 검증된 full TOC에서 상위 + 직접 하위까지만 남기는 삭제/filter 작업만 허용.
10. 공식 full TOC 미확보 → TOC_SOURCE_NOT_VERIFIED → 후보 탈락 → 다른 거래 발행사 후보로 교체.
11. 제목/발행일/페이지/가격/TOC/설명은 동일한 공식 상세페이지에서 확인 가능한 값만 사용. 모르면 추정하지 않는다.
12. 공급가격은 항상 공란.
13. GUIDE_GENERATION과 MAIL_COMPOSITION은 분리한다.

## 이번 대화에서 실제 발생한 오류
- Lucintel `Conductive Textile Market in South Korea`를 뽑음: 이번 Global-first-title 규칙 위반 → 폐기.
- The Insight Partners Conductive Textiles 자료: 제목이 Global로 시작하지 않아 이번 조건에서는 탈락.
- MarketResearch.com에서 Global Info Research 자료를 근거로 사용함: reseller 금지 위반.
- ResearchAndMarkets를 후보 근거로 사용함: reseller 금지 위반.
- 공식 full TOC를 확보하지 않은 상태에서 후보를 확정/부분 확정하려 한 오류가 반복됨.
- Coherent Market Insights 후보를 1종만 남기고 나머지를 미완료로 둔 상태이며, 이것도 다음 창에서 공식 상세페이지 + 거래발행사 풀 + full TOC + 최근 발행사 회피를 처음부터 재검증하기 전에는 PASS로 승계하지 않는다.

## 전 WIC 공통 반복오류 ROOT
이 문제를 42번만의 문제로 한정하지 않는다.
모든 WIC 기존/신규 대화창, TOOL, Work, TOOL044 순환구조는 작업 전 중앙 master + tool master + checkpoint를 자동 로드하고 확정규칙과 현재 출력을 pre-output에서 대조해야 한다.
관련 상태:
- PREWORK_CONTEXT_LOADED required
- PREWORK_CONTEXT_NOT_LOADED -> OUTPUT BLOCKED
- RULE_CONFLICT_DETECTED -> OUTPUT BLOCKED -> AUTO_REWORK -> REVALIDATE
- 반복 오류는 신규 단발 규칙이 아니라 기존 ROOT occurrence로 병합
- GitHub comment/대화/메모리만으로 TOOL044 실행 완료를 주장하지 않음
- 실제 완료는 queue/executor/test/result 및 remote evidence가 있을 때만 보고

## 다음 대화창 첫 작업
사용자의 마지막 실무 요청은:
`CAR-026 장명진에게 과거 보냈던 메일도 참고했는지 확인하고, 앞서 자료 선정에 오류가 있었으면 다시 뽑아라.`

따라서 다음 창은 설명 반복보다 먼저:
1. 중앙 master/read-back
2. 이 checkpoint read-back
3. CAR-026 과거 발송 이력 반영
4. WIC 거래 발행사 풀 확인
5. 원발행사 공식사이트만 조사
6. 정확히 Global로 시작하는 2026 우선 보고서 3종을 서로 다른 발행사에서 선정
7. 세 자료 모두 공식 full TOC까지 확보
8. pre-output gate 통과 후 안내서용 데이터 출력

사용자에게 과거 규칙이나 EML을 다시 붙이라고 요구하지 않는다.
