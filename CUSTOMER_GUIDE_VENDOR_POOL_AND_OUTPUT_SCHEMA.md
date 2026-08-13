# 고객 안내 거래 발행사 고정 풀 + 안내서 출력 스키마

상태: ACTIVE / CANONICAL
적용 범위: 모든 고객 안내 대화창, 7번 고객 컨택 판단, 1번 고객 자동화 안내서, 고객용 추천자료/중간안내서/최종안내서

## 1. 거래 가능 영문 발행사 고정 풀
아래 목록은 사용자가 이전에 제공한 `자료 추천·안내문 대화창용 완전 범용 지시문 v5.0 – 발행사 리스트 완전 고정 포함`의 고정 발행사 풀을 기준으로 한다.
이 목록 외 발행사는 사용자 확인 없이 추천자료에 넣지 않는다.
발행사명은 유사 이름으로 추정하거나 치환하지 않는다.

- alliedmarketresearch.com
- QY Research
- Markets and Markets
- BCC Research
- Research in China
- Technavio
- Future Markets
- RNCOS
- Transparency Market Research
- GlobalData
- INKWOOD Research
- Accuray Research
- GlobalInfo Research
- KBV Research
- Coherent Market Insights
- Grand View Research
- Kuick Research
- Prismane Consulting
- Mordor Intelligence
- Lucintel
- Prof Research
- AnalystView Market Insights
- Bizwit Research & Consulting
- Blueweave Consulting
- Vantage Market Research
- DataM Intelligence
- Zion Market Research
- Koncept Analytics
- LP Information
- Market Monitor Global
- WishTree Insight
- 99Strategy
- Maia Research
- The Insight Partners
- Hny Research
- MultiMarket Insight
- Introspective Market Research
- Stratview Research
- 360iResearch
- P&S Intelligence
- Stats Market Research
- Data Bridge Market Research
- Fortune Business Insights
- Reports And Data
- Rethink Technology Research
- Azoth Analytics
- Global Market Insights
- Orion Market Research
- Global Industry Analysts
- Next Move Strategy Consulting
- Persistence Market Research
- Stratistics MRC
- Verified Market Research
- Cognitive Market Research
- Credence Research
- ReAnIn Research
- IndustryARC
- Market Research Future
- BIS Research
- SkyQuest Technology
- MIReports
- LogisticsIQ
- M14 Intelligence
- Wharry Sharpe Research
- Straits Research
- Asia Pacific InfoServ
- Reports and Insights
- InsightAce Analytic
- VPA Research
- n-tech Research
- Evolve Business Intelligence
- Zhar Research
- Industry Experts
- market.us
- Cervicorn Consulting
- Acumen Research
- MarkNtel Advisors
- UnivDatos Market Insights

## 2. 발행사명 오인 금지
- `Future Markets`와 `Future Market Insights`는 서로 다른 발행사로 취급한다.
- 고정 풀에는 `Future Markets`가 있고 `Future Market Insights`는 없다.
- 따라서 `Future Market Insights` 자료를 거래 발행사 자료처럼 추천하는 것은 FAIL이다.
- 비슷한 이름, 자회사 추정, 브랜드 유사성만으로 거래 발행사로 승격하지 않는다.

## 3. 추천 3종 기본 규칙
- 신규 가능성 고객 안내서는 기본 3종으로 구성한다.
- 현재가 2026년이면 신규 가능성 고객에게 2026년 자료를 최우선으로 사용한다.
- 2025년 이하 자료는 사용자가 과거자료를 요청했거나 2026년판이 없고 특별한 이유가 있을 때만 예외 검토한다.
- 3종은 가능하면 서로 다른 거래 발행사로 분산한다.
- 각 자료는 실제 상세페이지, 정확한 영문 타이틀, 발행일, 공식 링크, 목차 확인 후 사용한다.
- 제목은 공식 판매페이지 제목을 자르거나 축약하지 않는다.

## 4. 고객용 안내서 자료별 출력항목 — 전 분야 공통 고정
자료 1, 자료 2, 자료 3 모두 아래 항목명과 순서를 동일하게 사용한다.

자료 N
영문 자료명:
한글 자료명:
발행사:
페이지:
가격:
발행일:
공식 링크:
목차:
보고서 정보:

- 영문 자료명은 공식 판매페이지에서 고객이 실제로 보는 보고서 제목/H1 또는 보고서명 블록을 기준으로 그대로 표시한다.
- 검색결과 제목, 브라우저 탭 title, SEO title, 검색엔진이 붙인 문구를 보고서명으로 대신 사용하지 않는다.
- 같은 페이지 안에서도 SEO title과 화면 표시 보고서명이 다르면 화면 표시 보고서명을 우선한다.
- 한글 자료명은 영문 전체 제목의 의미를 빠뜨리지 않도록 번역한다.
- 페이지가 공식적으로 공개되지 않으면 `공식 페이지에서 확인되지 않음`으로 표시한다.
- 가격은 해당 보고서의 같은 공식 상세페이지에서 실제로 보이는 구매옵션만 사용한다. 다른 보고서, 검색 스니펫, 유사 보고서의 가격을 옮겨 쓰지 않는다.
- 가격이 화면상 접힌 구매옵션/PURCHASE OPTIONS에 있어도 같은 상세페이지에서 확인되면 사용할 수 있으나, 확인 위치를 내부적으로 기록한다.
- 가격이 공식적으로 공개되지 않으면 임의 생성하지 않는다.
- 발행일/업데이트일/페이지수/가격/제목은 각 항목별로 같은 상세페이지에서 직접 확인한 값만 사용한다.
- 목차는 영문 원문으로 상위목차 + 하위목차까지만 표시하고 하하위목차는 기본 제외한다.
- 하위목차는 상위목차보다 오른쪽으로 들여쓴다.
- 보고서 정보는 발행사 공식 페이지에 있는 원문만 한국어로 번역한다. 분석·요약·짜깁기·자의적 재구성 금지.
- 고객용 출력은 일반 텍스트를 기본으로 하며 `**`, `__`, ChatGPT 추적 URL, `utm_source=chatgpt.com` 등 복사 흔적을 넣지 않는다.

## 5. 데이터 출처 잠금 및 교차오염 방지
- 안내서 한 자료의 모든 값은 반드시 그 자료의 공식 상세페이지에 묶어서 검증한다.
- 자료 A의 가격/페이지수/발행일을 자료 B에 복사하지 않는다.
- 검색 결과 스니펫만으로 PASS 처리하지 않는다. 공식 상세페이지를 열어 실제 표시값을 다시 확인한다.
- 검색결과 제목과 공식 페이지 화면 제목이 다르면 공식 페이지 화면 제목을 사용한다.
- 고객이 링크를 직접 열었을 때 보이는 제목과 안내서 영문 자료명이 다르면 FAIL이다.
- 사용자가 직접 확인한 화면 제목과 도구 추출 SEO title이 충돌하면, 실제 화면 제목을 우선 재검증하고 고객용 출력은 화면 제목 기준으로 맞춘다.
- 값이 안 보이면 `확인되지 않음`으로 두고, 다른 곳에서 추정해 채우지 않는다.

## 6. 현재 오류의 회귀 방지
- `Industrial Safety Market`처럼 공식 고객용 제목이 `Industrial Safety Market Size & Share Analysis - Growth Trends and Forecast (2026 - 2031)`로 표시되는 경우 전체 제목을 그대로 표시한다.
- `Semiconductor Materials Market` Technavio 사례처럼 검색/메타데이터에 `Growth Analysis - Size and Forecast` 문구가 잡히더라도, 사용자가 실제 상세페이지 화면에서 `Semiconductor Materials Market Analysis, Size, and Forecast 2026-2030`를 확인하면 화면 표시 제목을 기준으로 재검증하고 그 제목을 사용한다.
- 360iResearch의 `1-5 Users License $3,939`처럼 가격은 해당 페이지의 PURCHASE OPTIONS에 실제 표시되는 경우에만 사용한다. 사용자가 화면에서 못 찾는 경우 위치를 설명할 수 있어야 하며, 페이지에 없으면 즉시 삭제한다.
- 타이틀 일부만 잘라 표시한 출력은 FAIL 후 재작성한다.
- 자료 1~3 중 하나라도 항목명이 빠지거나 순서가 달라지면 출력 스키마 FAIL로 판정하고 동일 스키마로 다시 작성한다.
- 고정 풀 밖 발행사가 1종이라도 섞이면 전체 3종 추천을 완료로 보지 않고 교체한다.
