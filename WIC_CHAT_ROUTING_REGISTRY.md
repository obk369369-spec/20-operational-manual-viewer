# WIC CHAT ROUTING REGISTRY

상태: ACTIVE / NON-NORMATIVE ROUTING LEDGER
규범 원본: `WIC_GLOBAL_OPERATING_RULES.md`
목적: 실행 규칙을 복제하지 않고 기존 논리 역할·업무 lane·라우팅 키워드만 제공한다.

> 이 파일은 실행 규칙 원본이 아니다. 대화창 생성·이름·자동화·중복 작업·PASS/HOLD/FAIL 등 모든 실행 판단은 `WIC_GLOBAL_OPERATING_RULES.md`를 먼저 적용한다. 이 파일에는 새 규칙, 도구별 실행 DELTA, 예외 규칙 본문을 추가하지 않는다.

## 1. CORE LOGICAL ROLES

| role_id | 과거 registry 별칭 | 실제 UI 제목 검증 상태 | 라우팅 용도 |
|---|---|---|---|
| CONTROL_PRIMARY | `(개발 관찰자 모드 유지) 지피티 도구` | `UI_TITLE_HOLD` | 전체 개발 관찰·중앙 통합·상태 피드백 라우팅 |
| WORK_PREP | `워크 전 준비` | `UI_TITLE_HOLD` | Work 투입 전 준비·handoff 라우팅 |

- `role_id`와 과거 별칭은 라우팅 메타데이터일 뿐 실제 ChatGPT UI 대화창 제목의 존재 증거가 아니다.
- 실제 UI 제목에 대한 판단 규칙은 Global 단일 원본을 따른다.

## 2. SPECIALIST LANES

| lane_id | 라우팅 용도 | 기존 흐름 |
|---|---|---|
| EMAIL_COLLECTION | 모든 분야 신규/기존 고객 이메일 수집·검증·DB | 기존 분야별 흐름 재사용 |
| TOOL007 | 고객 컨택 판단·전화 멘트·추천자료 | 기존 7번 흐름 재사용 |
| TOOL001 | FULL/INTERMEDIATE 안내서 | 기존 1번 흐름 재사용 |
| TOOL006 | TOC 정리 | 기존 6번/TOC 흐름 재사용 |
| TOOL043 | `43번 소형 앱 출시 실행도구` | 기존 `소형 앱 출시` 흐름 재사용 |
| CRM_RESPONSE | 통화/회신 후 분기·다음행동 | 기존 고객후속/CRM 흐름 재사용 |

도구·업무별 실행 규칙과 예외는 이 파일에 두지 않는다. 해당 규범은 Global 단일 원본 및 Global이 명시적으로 가리키는 현재 업무군 원본에서 관리한다.

## 3. MACHINE ROUTE MAP

아래 `route:` 행만 `feedback_pipeline/cross_chat_feedback_ingest.py`가 실행 라우팅 데이터로 읽는다.
형식: `route: TARGET = keyword | keyword | ...`

route: TOOL001 = 1번 | 안내서 | full_guide | intermediate_guide | 고객 자동화 안내서
route: TOOL002 = 2번 | 입찰 | 입찰 도구 | bid | tender
route: TOOL006 = 6번 | 목차 | toc | marketsandmarkets | marketandmarket
route: TOOL007 = 7번 | 고객 컨택 | 컨택 판단 | 전화 멘트 | 유선 멘트
route: TOOL013 = 13번 | 엑셀 자동 업로드 | 46145
route: TOOL037 = 37번 | 메타데이터 | 상품명 | 한글명 | isbn | code
route: TOOL043 = 43번 | 소형 앱 출시 실행도구 | 소형 앱 출시 | 앱 출시 | 모바일 관찰 | 아이디어 출시 | 외부 증거 게이트
route: EMAIL_DB = 메일 수집 | 이메일 수집 | email collection | new_online | dormant_ledger | recent_trade | 고객 db
route: WORK_GATE = 워크 | work | 크레딧 | credit | 이관
route: CENTRAL = 중앙 마스터 | 깃허브 | github | 대화창 | 피드백 | 관찰자

## 4. ROUTING DATA MAINTENANCE

- 기존 target의 키워드 보완은 이 파일의 해당 `route:` 행만 수정한다.
- 새 target이 실제로 필요할 때에도 실행 규칙을 이 파일에 작성하지 않고 라우팅 식별자와 키워드만 추가한다.
- route 변경 후 파서 fixture/read-back을 실행한다.
- 규범 충돌·중복·대화창 소유권·자동화 허가·작업 우선순위는 이 파일에서 판정하지 않는다.

## 5. LEGACY MIGRATION NOTE

과거 이 Registry에 있던 `NO_NEW_CHAT`, UI-title gate, pointed-issue scope lock, 이메일 공통 규칙, TOOL040 실행 DELTA 등의 규범 문구는 라우팅 데이터와 섞여 있던 legacy 내용이다. 현재 실행 기준으로 사용하지 않으며, 최신 확정 규칙은 `WIC_GLOBAL_OPERATING_RULES.md` 단일 원본에서 관리한다.

과거 `TOOL040` / `40번 출시 앱 도구` 표기는 사용자 지정 번호 근거가 없어 폐기한다. 2026-08-17 중복 조사 후 정식 번호는 `43번`, machine route key는 `TOOL043`, 사용자-facing 도구명은 `43번 소형 앱 출시 실행도구`로 고정한다.

이 Registry의 PASS 기준은 **필요한 route 데이터가 파싱되고, 규범 실행 규칙이 다시 유입되지 않는 것**이다.
