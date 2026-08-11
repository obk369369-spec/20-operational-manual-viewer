# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 05:24 KST
상태: ACTIVE
목적: 각 WIC 도구·업무·주요 대화창의 실제 진행, 증거, blocker, 개선방법, restart point를 한 파일에서 확인한다.
운영 규칙 원본: `WIC_GLOBAL_OPERATING_RULES.md`
고객업무 공통 원본: `CUSTOMER_WORKFLOW_MASTER.md`

---

# 1. 지금 한눈에 보기

- 제3자 독립검증 actual run/result 증거: **0개 / HOLD**
- 현재 기능 확정 PASS 도구: **없음**
- 완료작업 반복 금지 → blocker는 HOLD → 다음 실행 가능 항목으로 이동 → 새 근거가 생기면 우선항목으로 복귀.
- 2026-08-13 Work 최우선 1순위: 개별 도구보다 먼저 모든 도구·대화창이 재사용하는 **WIC 전체 자동 통합 기반 구조 자체**를 실제 구현·E2E 검증한다.
- **중요 정정:** 중앙 루트 read-back 결과 `WIC_CHAT_ROUTING_REGISTRY.md`가 이미 실제 존재한다. 따라서 이전의 “registry 재사용 자산 0건” 표현은 폐기한다.
- 기존 registry에는 `NO_NEW_CHAT`, core chat/specialist lane, event 단위 중앙 GitHub 흡수, 원래 lane 재사용 규칙이 이미 있다. **새 registry를 만들지 않고 이것을 재사용/확장한다.**
- 다만 `normalizer → conflict/dedup → canonical writer → revision cache → target apply → test/evidence recorder`가 실제 자동 실행되는 core와 실제 E2E 증거는 아직 없다. 구조 PASS 금지.
- 1번 `defaultToc(keyword)` synthetic fallback 위치 특정, 13번 backend/API 미식별, 7번 잘못된 실행판 판정, 6번 `STRUCTURE_PASS` archive 확인은 완료된 조사이므로 반복 금지.

상태: 🟢 PASS = 실제 입력→실행→출력→검증 / 🟠 PARTIAL-HOLD = 실제 개선·증거 있으나 E2E/독립검증 미완료 / 🔴 HOLD = blocker / ⚪ NEXT = 다음 실행 대상

---

# 2. 도구별 운영준비도

| 우선 | 도구/업무 | 준비도 | 상태 | 현재 핵심 근거 / blocker |
|---|---|---:|---|---|
| 1 | 이메일 수집 | **60/100** | 🟠 PARTIAL-HOLD | 중앙 공통 규칙·업무흐름 존재. actual collector/executor 미식별 |
| 2 | 7번 고객 컨택 판단 | **40/100** | 🔴 HOLD | 중앙 규칙 존재. `07-wic-setting-tool-v1`은 최신 목적과 불일치 |
| 3 | 1번 중간/최종 안내서 | **60/100** | 🟠 PARTIAL-HOLD | 실제 HTML/규칙/regression workflow 존재. `defaultToc` 위치 확인. 안전 부분 patch와 actual run 필요 |
| 4 | 37번 메타데이터 | **40/100** | 🔴 HOLD | 생산 규칙 존재. 실제 생산 실행자산 미식별 |
| 5 | 13번 엑셀 자동 업로드 | **60/100** | 🟠 PARTIAL-HOLD | 실제 repo/index 존재. backend/uploader/API 미식별 |
| 6 | 6번 목차 정리 | **80/100** | 🟠 PARTIAL-HOLD | `static-validation.json` read-back / `STRUCTURE_PASS`; 제3자 독립검증 아님 |
| 7 | 2번 입찰 | **40/100** | 🔴 HOLD | local-only UI 확인. 나라장터 실연동 엔진 미식별 |
| 8 | 28~31 발행사 업무 | **40/100** | 🔴 HOLD | 역할/규칙 존재. 실제 전용 실행자산 근거 부족 |

> 숫자는 증거 기반 운영준비도이며 코드 작성률이 아니다. 실행·검증 증거 없이 마지막 점수는 부여하지 않는다.

---

# 3. 2026-08-13 Work 1순위 — 재사용 자동 통합 구조

## 고정 목표
한 번 구현한 뒤 어떤 도구·대화창에서도 같은 구조를 계속 사용한다. 새 대상마다 core를 복제하거나 전체 규칙을 다시 읽지 않는다.

## 이미 존재하여 재사용할 자산
- `WIC_CHAT_ROUTING_REGISTRY.md` — 실제 존재/read-back 완료.
  - `NO_NEW_CHAT`
  - CONTROL_PRIMARY / WORK_PREP
  - EMAIL_COLLECTION / TOOL007 / TOOL001 / TOOL006 / CRM_RESPONSE specialist lane
  - feedback을 전체 대화 병합이 아니라 event 단위로 중앙 GitHub에 흡수
  - 중앙 반영 후 원래 lane에 재사용
- `WIC_GLOBAL_OPERATING_RULES.md` — 규범 단일 원본
- `CUSTOMER_WORKFLOW_MASTER.md` — 고객업무 공통 원본
- `WIC_EXECUTION_STATE.json` — 과거 실행상태/근거. 단, `updated_kst=2026-08-09 21:58`로 현재 observer보다 오래되므로 restart point의 최신 기준은 이 파일의 현재 섹션을 우선한다.

## Work에서 구현할 실제 core
`EVENT → NORMALIZE → ROUTE(existing registry) → CONFLICT/DEDUP → CANONICAL WRITE → READ-BACK → TARGET REVISION READ/APPLY → TEST/EVIDENCE → RESTART/HOLD`

### 고정 계층
1. GLOBAL: WIC 전체 공통
2. WORKGROUP: 이메일수집/고객안내/메타데이터/업로드/목차/입찰/발행사
3. TOOL_OR_DOMAIN_OVERRIDE: 특정 도구·산업·대화창 예외
4. DATA_OR_EXECUTION_ASSET: 원자료·코드·실행자산·결과

### 재사용 원칙
- 새 도구/대화창은 **기존 registry에 등록만** 한다.
- 새 입력 형식만 adapter로 추가한다.
- 기존 계층으로 표현 가능한 새 업무는 core 변경 금지.
- 대상은 마지막 적용 canonical revision을 저장하고 revision이 같으면 전체 재분석을 건너뛴다.
- revision이 바뀌면 영향받는 scope만 다시 적용한다.
- 동일 의미는 병합, 최신 명시 지시는 supersede/deprecated, 동일 우선순위 충돌은 `HOLD_CONFLICT`.
- core 변경 시 등록 대상 전체 회귀테스트를 수행한다.

## 구조 자체 PASS 조건
문서/코드 존재만으로 PASS 금지. 실제 새 피드백 1건으로 아래 증거가 모두 있어야 한다.
1. event 수신
2. normalize 결과
3. 기존 registry를 이용한 자동 route 결과
4. conflict/dedup 판정
5. canonical GitHub commit
6. canonical read-back
7. 대상 도구 새 revision read/apply
8. 실제 test/run 결과
9. result URL/file/artifact
10. 실패 시 HOLD + blocker + restart point

구조 PASS 후 우선순위:
`이메일 수집 → 7번 고객 컨택 판단 → 1번 중간/최종 안내서 → 37 메타데이터 → 13 엑셀 자동 업로드 → 6번 목차 정리 → 2번 입찰 → 28~31 → 나머지 등록 도구/주요 업무창`

---

# 4. 이번 회차 실제 수행 / 새 증거

1. `WIC_OBSERVER_STATUS.md`를 먼저 read-back했다.
2. 중앙 실행상태 `WIC_EXECUTION_STATE.json`도 read-back했다. 이 파일의 `updated_kst`는 2026-08-09 21:58이어서 현재 observer보다 오래된 상태임을 확인했다.
3. 중앙 repo root contents를 실제 read-back했고 `WIC_CHAT_ROUTING_REGISTRY.md` 존재를 확인했다.
4. `WIC_CHAT_ROUTING_REGISTRY.md` 본문을 read-back해 event 단위 중앙 흡수와 기존 lane 재사용 규칙이 이미 있음을 확인했다.
5. 따라서 이전의 “registry 후보 0건” 판단을 수정하고 **기존 registry 재사용**을 13일 Work restart point로 승격했다.
6. 완료된 1/6/7/13 검색·판정은 반복하지 않았다.
7. 제3자 actual run/result URL은 새로 확보되지 않았으므로 독립검증 PASS는 여전히 0개다.

---

# 5. Blocker / 개선방법

1. **자동 통합 구조:** registry는 존재하지만 자동 실행 core와 E2E가 없음.
   - 개선: 새 registry 생성 금지. 기존 `WIC_CHAT_ROUTING_REGISTRY.md`를 route source로 사용하고 normalizer/conflict-dedup/canonical writer/revision cache/test-evidence를 연결한다.
2. **이메일 수집:** actual collector 미식별.
   - 개선: 구조 PASS 후 첫 연결 대상으로 executor/DB/browser 자산 연결·구현 + current run 증거.
3. **7번:** 현재 repo 목적 불일치.
   - 개선: 구조 PASS 후 올바른 기존 실행판 근거 확보 또는 중앙 규칙을 읽는 최소 실행판 구현.
4. **1번:** synthetic fallback 정확 위치는 확인 완료.
   - 개선: Work/checkout의 안전 부분 patch로 fallback fail-closed화 → synthetic 함수 제거 → regression actual run/result → 외부 actual run.
5. **13번:** backend/API 미식별.
   - 개선: 실제 endpoint/backend 자산 발견 또는 Work에서 uploader 연결 구현 후 실업로드 결과 검증.
6. **6번:** 내부 구조검증만 확보.
   - 개선: 실제 publisher golden fixture/실업무 기대값 비교 또는 제3자 actual URL.
7. **외부검증:** actual 제3자 run/result 없음.
   - 개선: 실제 외부 서비스 Project/run/result URL 확보 전 PASS 금지.

---

# 6. 최신 restart point

- **최우선 / 2026-08-13 Work:** 새 registry를 만들지 않는다. 이미 존재하는 `WIC_CHAT_ROUTING_REGISTRY.md`를 재사용한다. Work 시작 즉시 이 registry를 route source로 연결하고 `normalizer → conflict/dedup → canonical writer → revision cache → target apply → test/evidence recorder` 실제 실행 core 구현으로 들어간다. 실제 새 피드백 1건 E2E 전 구조 PASS 금지.
- **이메일 수집:** 구조 PASS 직후 첫 연결. actual executor/DB/browser 연결 또는 구현.
- **7번:** `07-wic-setting-tool-v1` 재검토 금지. 올바른 실행판 연결/최소 실행판 구현.
- **01:** `defaultToc` 위치 재검색 금지. 안전 patch 환경에서 fail-closed 수정 → actual regression run/result → 외부 run.
- **37:** 실제 생산 실행자산 식별 시 원본→결과 E2E.
- **13:** backend/API 동일 검색 반복 금지. 실제 endpoint 발견 또는 Work 연결 구현 시 재개.
- **06:** `STRUCTURE_PASS` archive 재확인 금지. golden fixture/실업무 비교 또는 제3자 actual URL로 이동.
- **02 / 28~31:** 새 실제 엔진 근거 없으면 반복 조사하지 않는다.
- **외부검증:** CircleCI/기타 제3자 actual Project/run/result URL이 있을 때만 독립검증 인정.

이 파일은 앞으로도 새 파일을 만들지 않고 같은 `WIC_OBSERVER_STATUS.md`를 덮어쓴다.
