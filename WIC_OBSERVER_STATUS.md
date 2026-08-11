# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 02:19 KST
상태: ACTIVE
목적: 각 WIC 도구·업무·주요 대화창의 실제 진행, 증거, blocker, 개선방법, restart point를 한 파일에서 확인한다.
운영 규칙 원본: `WIC_GLOBAL_OPERATING_RULES.md`
고객업무 공통 원본: `CUSTOMER_WORKFLOW_MASTER.md`

---

# 1. 지금 한눈에 보기

- 제3자 독립검증 실제 run 증거: **0개 / HOLD**
- 현재 확정 PASS 도구: **없음**
- 표시 방식: 임의 완료율 대신 **운영준비도 0~100**을 사용한다.
- 평가 기준: `정체성·규칙 20 + 실제 입력/자산 20 + 기능/업무흐름 구현 20 + 현재 실행/출력 증거 20 + 독립검증·실업무 PASS 20`.
- 완료작업 반복 금지 → blocker는 HOLD → 다음 실행 가능 항목으로 이동 → 새 근거가 생기면 우선항목으로 복귀.
- 2026-08-13 Work 1순위: 개별 도구보다 먼저 모든 도구·대화창이 재사용하는 **WIC 전체 자동 통합 기반 구조 자체**를 구현한다.
- 이번 회차 새 사실: 현재 `07-wic-setting-tool-v1`은 중앙 포인터 파일 자체가 최신 7번 `고객 컨택 판단` 목적과 불일치한다고 명시한다. **7번 실행판으로 사용 금지 / HOLD 유지.**
- 이번 회차 새 사실: `13-excel-upload` 루트에는 `.github`, `WIC_RULE_SOURCE.md`, `index.html`이 확인됐으나 실제 홈페이지 uploader/backend/API 실행자산은 식별되지 않았다. **13번 점수 상승 없음.**

상태: 🟢 PASS = 실제 입력→실행→출력→검증 / 🟠 PARTIAL-HOLD = 실제 개선·실행 근거 있으나 E2E/독립검증 미완료 / 🔴 HOLD = blocker / ⚪ NEXT = 다음 실행 대상

---

# 2. 도구별 운영준비도 — 전체 100 기준

| 우선 | 도구/업무 | 준비도 | 상태 | 현재 핵심 근거 / blocker |
|---|---|---:|---|---|
| 1 | 이메일 수집 | **60/100** | 🟠 PARTIAL-HOLD | 중앙 공통 규칙·업무흐름 존재. 실제 자동수집 실행자산/current run 미식별 |
| 2 | 7번 고객 컨택 판단 | **40/100** | 🔴 HOLD | 중앙 규칙은 존재. `07-wic-setting-tool-v1`의 `WIC_RULE_SOURCE.md`가 기존 실행물이 세팅 도구이며 최신 7번 목적과 불일치한다고 명시 |
| 3 | 1번 중간/최종 안내서 | **60/100** | 🟠 PARTIAL-HOLD | 실제 HTML/규칙/CircleCI gate 존재. production synthetic 및 Deno failure 남음 |
| 4 | 37번 메타데이터 | **40/100** | 🔴 HOLD | 생산 규칙 존재. 실제 생산 실행자산 미식별 |
| 5 | 13번 엑셀 자동 업로드 | **60/100** | 🟠 PARTIAL-HOLD | `13-excel-upload` 실제 repo/index 존재. 루트 read-back 결과 backend/uploader/API 자산 미식별 |
| 6 | 6번 목차 정리 | **80/100** | 🟠 PARTIAL-HOLD | commit `0b307cc9...`의 `static-validation.json` 실제 read-back, `STRUCTURE_PASS`; 제3자 독립검증 아님 |
| 7 | 2번 입찰 | **40/100** | 🔴 HOLD | local-only UI 확인. 나라장터 실연동 엔진 미식별 |
| 8 | 28~31 발행사 업무 | **40/100** | 🔴 HOLD | 역할/규칙 존재. 실제 전용 실행자산 근거 부족 |
| - | 09 컨텐츠 자료 안내 | **60/100** | 🟠 PARTIAL-HOLD | 실제 index + synthetic blocker + 내부 gate. production synthetic 제거 미완료 |
| - | 05 Report Generator | **60/100** | 🟠 PARTIAL-HOLD | 실제 index/생성 UI 존재. 업무규칙 E2E/외부검증 미완료 |
| - | 08 English Verb Exercise | **60/100** | 🟠 PARTIAL-HOLD | local-only 실행자산 존재. 정식 run evidence 미완료 |
| - | 27 Technical Book Verifier | **40/100** | 🟠 PARTIAL-HOLD | 규칙/과거 UI 확인. 현재 실행판/run 미확인 |
| - | 03/04/10/11/12/14/19/21/23/24/25/26 | **20/100** | 🔴 HOLD | 저장소 정체성 수준만 확인; 실행/검증 미확인 |

> 숫자는 증거 기반 운영준비도이며 코드 작성률이 아니다. 실행·검증 증거 없이 마지막 점수는 부여하지 않는다.

---

# 3. 41계열 주요 대화창 — 전체 100 기준

대화창 기준: `이름/역할 20 + 분야 규칙/과거업무 20 + 중앙마스터 연결 20 + 현재 send-ready/실업무 출력 20 + 자동실행·독립검증/office-ready 20`.

| 대화창 | 준비도 | 현재 상태 |
|---|---:|---|
| 41 이메일 수집(방산) | **60/100** | 중앙 공통축 확보, 현재 자동수집 run/DB 연결 필요 |
| 41-1 고객 안내(방산) | **60/100** | 규칙/공통축 확보, 최신 고객 1건 E2E 필요 |
| 41-2 이메일 수집(이차전지) | **60/100** | send-ready DB 실행/검증 필요 |
| 41-3 이메일 수집(섬유) | **60/100** | send-ready DB 실행/검증 필요 |
| 41-4 이메일 수집(원자력) | **60/100** | send-ready DB 실행/검증 필요 |
| 41-5 이메일 수집(태양광) | **60/100** | send-ready DB 실행/검증 필요 |
| 41-6 이메일 수집(바이오) | **60/100** | send-ready DB 실행/검증 필요 |
| 41-7 이메일 수집(로봇) | **40/100** | 이름/역할 확보, 분야 데이터/실행 DB 흡수 확인 필요 |
| 41-8 고객 안내(반도체) | **60/100** | 최신 고객 1건 E2E 필요 |
| 41-9 이메일 수집(탄소) | **60/100** | send-ready DB 실행/검증 필요 |
| 41-10 이메일 수집(인공지능) | **60/100** | send-ready DB 실행/검증 필요 |
| 41-11 이메일 수집(풍력) | **60/100** | send-ready DB 실행/검증 필요 |
| 41-12 이메일 수집(조선) | **60/100** | send-ready DB 실행/검증 필요 |
| 41-13 고객 안내(탄소) | **60/100** | 최신 고객 E2E/중복방지 검증 필요 |
| 41-14 고객 안내(조선) | **60/100** | 최신 고객 E2E/추천검증 필요 |
| 41-15 고객 안내(인공지능) | **60/100** | 최신 고객 E2E/추천검증 필요 |

기존 대화창 이름/번호/역할을 임의 변경하지 않는다. 각 창의 고유 규칙·오류·데이터가 중앙마스터에 흡수되고 read-back된 뒤에만 통합 준비도를 올린다.

---

# 4. 외부검증 — 2026-08-13 병행

| 구조 | 준비도 | 실제 상태 |
|---|---:|---|
| CircleCI | **60/100** | GitHub OAuth + 1번 config/gate 존재. 실제 WIC Project/run/result URL 없음 → HOLD |
| GitHub Actions / 6번 | 내부 증거 | `static-validation.json` read-back 존재. **제3자 독립검증으로 계산 금지** |
| Codacy | **20/100** | 후보만 선정. 실제 연결/result 없음 |
| BrowserStack | **20/100** | 후보만 선정. 실제 연결/run 없음 |

제3자 서비스 actual run/result URL이 있을 때만 독립검증으로 인정한다. assistant 추론, GitHub Actions, Deno 상태는 독립검증으로 가장하지 않는다.

---

# 5. 이번 회차 실제 수행 / 새 증거

1. 기존 `WIC_OBSERVER_STATUS.md`를 먼저 read-back하고 최신 restart point를 확인했다.
2. 완료된 6번 archive 검증, 1번 synthetic blocker 확인 등을 반복하지 않았다.
3. 이메일 수집/7번 실행자산 탐색에서 `07-wic-setting-tool-v1`을 확인했다.
4. `07-wic-setting-tool-v1/WIC_RULE_SOURCE.md` read-back 결과: **기존 실행물은 '세팅 도구' 성격이며 최신 7번 '고객 컨택 판단' 목적과 불일치, 실행판 HOLD**라는 중앙 경고를 확인했다. 따라서 잘못된 저장소를 7번 실행판으로 재사용하지 않는다.
5. 13번은 `13-excel-upload` 저장소를 재식별하고 루트 contents를 read-back했다. 확인된 루트 자산은 `.github`, `WIC_RULE_SOURCE.md`, `index.html`이며 실제 홈페이지 uploader/backend/API 파일은 식별되지 않았다.
6. 13번 repo 코드검색에서 `fetch/axios/XMLHttpRequest/endpoint/API/upload/worldic/form action` 실행연동 후보는 검색되지 않았다. **실제 업로드 엔진이 있다고 추정하지 않는다.**
7. 위 두 새 사실은 실행자산 확인 결과이므로 상태판에 기록했지만, 실제 기능 실행/PASS 증거가 아니므로 운영준비도 점수를 올리지 않았다.
8. 자동 통합 구조 본체 구현은 2026-08-13 Work 첫 작업으로 유지하며, 오늘은 재분석 대신 기존 도구 blocker를 더 정확히 좁혔다.

---

# 6. 가장 큰 병목 / 개선방법

1. **자동 통합 구조:** 아직 구현 전. 개선: 13일에 registry → normalizer → router → conflict/dedup → canonical writer → revision cache → test/evidence recorder를 한 core로 구현하고 실제 피드백 1건으로 E2E 검증.
2. **7번:** 현재 발견 repo가 잘못된 목적. 개선: 새 껍데기 생성 금지. 실제 고객 컨택 실행판이 발견되거나 구조 PASS 후 중앙 규칙을 읽는 최소 실행판을 구현할 때까지 HOLD.
3. **13번:** UI/index는 있으나 실제 홈페이지 backend/API 없음. 개선: worldic 실제 업로드 endpoint/backend 자산을 식별하거나 Work에서 실제 연결 가능한 uploader를 구현하고 실업로드 결과로 검증.
4. **1번:** synthetic 생성 + Deno failure. 개선: 안전한 부분 patch/checkout 경로 확보 후 synthetic 제거 → Deno 정상화 → CircleCI actual run.
5. **6번:** 내부 구조 검증은 확보. 개선: 승인 golden fixture/실업무 기대값 비교 또는 실제 제3자 run URL 확보.
6. **외부검증:** CircleCI OAuth 이후 actual project/run 없음. 개선: 실제 project 활성화 및 result URL 확보.

---

# 7. 2026-08-13 Work 1순위 — 재사용 자동 통합 구조

## 고정 목표
한 번 구현한 뒤 어떤 도구·대화창에서도 같은 구조를 계속 사용한다. 새 대상마다 core를 복제하거나 전체 규칙을 다시 읽지 않는다.

## Core pipeline
`EVENT → NORMALIZE → ROUTE → CONFLICT/DEDUP → CANONICAL WRITE → READ-BACK → TARGET REVISION READ/APPLY → TEST/EVIDENCE → RESTART/HOLD`

## 고정 계층
1. GLOBAL: WIC 전체 공통
2. WORKGROUP: 이메일수집/고객안내/메타데이터/업로드/목차/입찰/발행사 등 업무군
3. TOOL_OR_DOMAIN_OVERRIDE: 특정 도구·산업·대화창 예외
4. DATA_OR_EXECUTION_ASSET: 원자료·코드·실행자산·결과

## 재사용 규칙
- 새 도구/대화창은 registry 등록만 한다.
- 새 입력 형식만 adapter로 추가한다.
- 기존 계층으로 표현 가능한 새 업무는 core 변경 금지.
- 대상은 마지막 적용 canonical revision을 저장하고 revision이 같으면 전체 재분석을 건너뛴다.
- revision이 바뀌면 영향받는 scope만 다시 적용한다.
- 동일 의미는 병합, 최신 명시 지시는 supersede/deprecated, 동일 우선순위 충돌은 `HOLD_CONFLICT`.
- core 변경 시 등록 대상 전체 회귀테스트를 수행한다.

## 구조 자체 PASS 조건
문서/코드 존재만으로 PASS 금지. 실제 새 피드백 1건을 넣어 아래 증거가 모두 있어야 한다.
1. event 수신
2. normalize 결과
3. 자동 route 결과
4. conflict/dedup 판정
5. canonical GitHub commit
6. canonical read-back
7. 대상 도구 새 revision read/apply
8. 실제 test/run 결과
9. result URL/file/artifact
10. 실패 시 HOLD + blocker + restart point

구조 PASS 후 우선순위:
`이메일 수집 → 7번 고객 컨택 → 1번 중간/최종 안내서 → 37 메타데이터 → 13 업로드 → 6 목차 → 2 입찰 → 28~31 → 나머지 등록 도구/주요 업무창`

---

# 8. 현재 restart point

- **자동 통합 구조:** 2026-08-13 Work 첫 작업. 기존 규칙 재독해·재요약·저장소 재검색에 크레딧 사용 금지. `registry/normalizer/router/conflict-dedup/canonical writer/revision cache/test-evidence recorder` 구현부터 시작. 실제 피드백 1건 E2E 전 PASS 금지.
- **이메일 수집:** 구조 PASS 후 첫 연결 대상. 실제 자동수집 실행자산/current run 근거가 생기면 즉시 복귀.
- **7번:** `07-wic-setting-tool-v1`은 최신 목적과 불일치함이 read-back으로 확인됨. 이 repo를 실행판으로 다시 검토하지 않는다. 올바른 실행판 근거 또는 구조 PASS 후 새 최소 실행판 구현 시 재개.
- **01:** production `defaultToc` fallback 제거 → Deno 정상화 → CircleCI actual run.
- **37:** 실제 생산 실행자산 식별 시 원본→결과 E2E.
- **13:** `13-excel-upload` 루트/코드에서 실제 homepage backend/API 미식별. 동일 검색 반복 금지. 실제 endpoint/backend 자산이 발견되거나 Work에서 연결 구현할 때 재개.
- **06:** `STRUCTURE_PASS` archive 확인은 완료. 같은 확인 반복 금지. 다음은 golden fixture/실업무 기대값 비교 또는 제3자 actual URL.
- **02 / 28~31:** 새 실제 엔진 근거 없으면 반복하지 않는다.
- **09:** 안전 부분 patch 경로 확보 시 `createInitialSampleData()` 제거 → 빈 상태 fail-closed → actual run.
- **대화창:** 각 창 고유 규칙/데이터 흡수 증거만 순차 확인하고 이미 중앙화된 공통규칙은 재추출하지 않는다.
- **외부검증:** CircleCI 실제 Project/run/result URL 또는 다른 제3자 actual run/result가 있을 때만 독립검증 인정.

이 파일은 앞으로도 새 파일을 만들지 않고 같은 `WIC_OBSERVER_STATUS.md`를 덮어쓴다.
