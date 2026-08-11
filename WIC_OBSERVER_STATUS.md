# WIC OBSERVER STATUS

최종 갱신: 2026-08-11 13:17 KST
상태: ACTIVE
목적: 링크 하나에서 각 도구의 현재 상태·개선된 부분·막힌 부분·다음 작업을 바로 이해할 수 있게 보여주는 사람용 관찰판.
운영 규칙 원본: `WIC_GLOBAL_OPERATING_RULES.md` 단일 원본만 사용.

---

# 1. 지금 한눈에 보기

- 제3자 외부검증 실제 run 증거: **0개 / HOLD**
- CircleCI: GitHub OAuth는 `obk369369-spec` 연결됨. 이번 회차에 **1번 저장소 `.circleci/config.yml` 실제 commit + read-back 완료**. 그러나 CircleCI 실제 run/result URL은 아직 없음.
- 현재 기능 PASS 도구: **확정 가능한 PASS 없음**
- 전체 완료율: **산정중(HOLD)** — 검증 완료 작업단위 전수 수치화 전에는 임의 % 금지
- 진행 원칙: **우선도구 실제 개선 시도 → 더 못 나가면 HOLD 기록 → 즉시 다음 실행 가능한 도구 → 새 근거가 생기면 우선도구로 복귀**

상태: 🟢 PASS = 실제 입력→실행→출력→검증 / 🟠 PARTIAL-HOLD = 일부 실기능 존재 또는 코드 개선 commit 확보했으나 E2E 미검증 / 🔴 HOLD = 현재 blocker / ⚪ NEXT = 다음 실행 대상

---

# 2. 이번 회차 실제 수행·증거

1. 기존 `WIC_OBSERVER_STATUS.md`를 먼저 읽고 최신 restart point를 확인했다. 05 완료 수정 반복 없이 09의 sample fallback 제거 지점에서 재개했다.
2. `09-contents-making-tool/index.html`에서 `loadState()`가 localStorage 없음/파싱 오류 시 `createInitialSampleData()`를 호출하는 실제 코드를 다시 확인했다. 예시 고객·발행사·자료 자동주입 위험은 기존 판정과 동일하다.
3. 현재 GitHub connector에는 대형 기존 파일의 부분 patch 기능이 없고 `update_file`은 전체 UTF-8 파일 교체만 가능하다. 전체 파일을 안전하게 재구성하지 못한 상태에서 09를 덮어쓰면 손상 위험이 있으므로 **09 수정은 HOLD 유지**했다. 같은 조사 반복 금지.
4. 우선순위가 높은 **1번 안내서**로 즉시 이동해 실제 Deno 응답 처리 코드를 읽었다.
5. **1번 synthetic TOC 실제 경로 재확인:** `firstNormalized.toc`가 비어 있으면 `defaultToc(...)`를 호출해 시장개요·시장동향·기술·정책·기업·전망 형식의 목차를 임의 생성한다. 이는 원자료 검증 원칙과 충돌한다.
6. 1번 기존 `.circleci/config.yml`이 없는 것을 404로 확인한 뒤, 외부검증 준비를 실제로 추가했다.
7. **1번 CircleCI validation gate commit:** `ec69102f276cb319c9e4b7aa939e359bf8847190`
   - `index.html`, `guide_template.html` 존재 검사
   - `firstNormalized.toc = defaultToc`가 남아 있으면 FAIL
   - `function defaultToc`가 남아 있으면 FAIL
   - Deno `fetch(endpoint)` 및 결과없음 HOLD 경로 존재 확인
8. GitHub read-back으로 `.circleci/config.yml` blob `eb2f944cb3a94911120babe3cfd7a418b81ada31`을 확인했다.
9. 단, CircleCI 사이트에서 WIC 저장소 Project/파이프라인 실제 실행은 아직 연결되지 않아 **외부 run/result URL은 0개**다. 따라서 독립검증 PASS 금지.

---

# 3. 최우선 도구

| 우선 | 도구 | 상태 | 실제 확인된 것 | blocker | 개선방법 / 복귀조건 |
|---|---|---|---|---|---|
| 1 | 이메일 수집 | 🔴 HOLD | 공통 규칙·검증기준 | 전용 실행자산 미확인 | 새 실행파일/run URL 근거 발견 시 복귀 |
| 2 | 7번 고객 컨택 판단 | 🔴 HOLD | 잘못된 `07-wic-setting-tool-v1` 배제 | 실제 실행판 미확인 | 올바른 실행자산 근거 발견 시 복귀 |
| 3 | 1번 중간/최종 안내서 | 🟠 PARTIAL-HOLD | 실제 HTML + Deno POST 코드 + synthetic TOC fallback 위험 + CircleCI gate commit | synthetic TOC 본체 제거 미완료, CircleCI 실제 run 없음, 브라우저 E2E 미확보 | 부분 patch 가능한 쓰기 경로에서 synthetic TOC 제거 → CircleCI 실제 run → 입력 E2E |
| 4 | 37번 메타데이터 | 🔴 HOLD | 규칙 존재 | 생산 실행자산 미확인 | 실행자산 근거 발견 시 E2E |
| 5 | 13번 엑셀 자동 업로드 | 🟠 PARTIAL-HOLD | 입력→매핑→미리보기→XLSX 생성 | 실제 홈페이지 업로드 endpoint/API 없음 | endpoint/브라우저 자동화 근거 발견 시 복귀 |
| 6 | 6번 목차 정리 | 🟠 PARTIAL-HOLD | 저장소·엔진 흔적 | 승인 golden fixture/expected output 부족 | 승인 fixture 발견 시 회귀검증 |
| 7 | 2번 입찰 | 🔴 HOLD | 수동 UI 확인 | 나라장터 자동수집/API/로그인/투찰 엔진 없음 | 기존 실엔진 근거 발견 시 재사용 |
| 8 | 28~31 | 🔴 HOLD | 역할·규칙 분리 | 실행 저장소/파일 참조 없음 | 구체 실행자산 발견 시 복귀 |

---

# 4. 다음 실행 가능한 도구

| 도구 | 상태 | 이번 판단 | 다음 행동 |
|---|---|---|---|
| 01 Auto Guide | 🟠 PARTIAL-HOLD | **CircleCI 검증 게이트 commit + read-back 완료** | CircleCI Project 연결 후 최초 실제 run URL 확보. 본체 synthetic TOC 제거는 안전한 부분 patch 경로 확보 시 수행 |
| 05 Report Generator | 🟠 PARTIAL-HOLD | 안전 수정 commit + read-back 완료 | 외부/브라우저 E2E가 생기면 실제 입력 검증 후 PASS 판단 |
| 09 Contents Making Tool | 🟠 PARTIAL-HOLD | sample data 자동주입 위험 특정 | 부분 patch 가능한 쓰기 경로 확보 시 fallback을 `contents=[]`로 변경. 그 전에는 전체파일 덮어쓰기 금지 |
| 13 Excel Upload | 🟠 PARTIAL-HOLD | 로컬 XLSX 기능 존재 | 실제 업로드 endpoint/API 근거 탐색 시 복귀 |
| 06 TOC Check | 🟠 PARTIAL-HOLD | 엔진 흔적 존재 | 승인 fixture 발견 시 회귀검증 |

---

# 5. 외부검증 도입 상태 — 2026-08-13 기준 병행

| 외부구조 | 현재 | 실제 증거 | 다음 단계 |
|---|---|---|---|
| CircleCI | 🟠 OAuth 연결 + config commit / run 0 | OAuth 연결 사용자 화면 + 1번 `.circleci/config.yml` commit `ec69102f...` + read-back | CircleCI에서 `01-auto-guide-v1` Project/파이프라인을 실제 연결해 최초 외부 run URL 확보 |
| Codacy | 🔴 0 | 연결 증거 없음 | CircleCI 실 run이 막힐 때 사용자 승인 묶음 후보 |
| BrowserStack | 🔴 0 | 연결 증거 없음 | UI E2E가 필요한 우선도구에 후순위 연결 |

GitHub Actions·상태판·자체 코드 추론은 내부검증으로만 사용하며 제3자 독립검증으로 가장하지 않는다. CircleCI도 실제 run URL이 생기기 전에는 독립검증 완료로 계산하지 않는다.

---

# 6. 실제 개선됨 / 남음

**실제 개선됨**
- 05 입력 밖 사실 자동 생성 제거 commit 및 read-back은 이전 회차 완료 상태 유지.
- 1번 synthetic TOC 발생 코드 위치를 실제 Deno 성공 경로에서 다시 확인.
- 1번 저장소에 CircleCI 검증 게이트를 실제 commit으로 추가하고 read-back 확인.
- 외부검증은 설명 수준에서 벗어나, 실제 파이프라인 config 자산 1개가 생김.

**남음**
- CircleCI `01-auto-guide-v1` 최초 실제 run/result URL
- 1번 synthetic TOC fallback 본체 제거 commit + E2E
- 09 sample fallback 실제 제거 commit + E2E
- 05 실제 브라우저 E2E run/result URL
- 13 실제 업로드 연결
- 6 승인 fixture 확보
- 이메일/7/37 실제 실행자산 식별

---

# 7. 막힘 처리 규칙

`원인 확인 → 가능한 최소 수정 1회 → 실행/검증 → 실패하면 HOLD + 개선방법 + restart point → 즉시 다음 도구`

같은 404/같은 저장소 검색/같은 HOLD 진단 반복 금지. 상태판 변경만 기능개선으로 계산하지 않는다.

---

# 8. 현재 restart point

- **01:** `.circleci/config.yml` commit `ec69102f276cb319c9e4b7aa939e359bf8847190`, read-back blob `eb2f944cb3a94911120babe3cfd7a418b81ada31`. 같은 config 생성 반복 금지. 다음 목표는 CircleCI 실제 Project 연결/run URL 또는 안전한 부분 patch 경로에서 synthetic TOC 제거.
- **05:** 안전 수정 commit `b2af1f445477b7c7fbdbebbe36b26418dbd49276` 및 read-back 완료. 같은 코드수정 반복 금지. 외부/브라우저 E2E가 확보될 때만 복귀.
- **09:** `loadState()` sample fallback 위험 확인 완료. 현재 connector 전체파일 교체만 가능하여 안전수정 HOLD. 부분 patch 가능한 쓰기 경로가 생길 때까지 동일 조사 반복 금지.
- **우선도구 복귀 조건:** 이메일/7/37 실행자산, 13 endpoint, 6 fixture 중 새 근거가 생기면 즉시 우선순위로 복귀.
- **외부검증:** CircleCI OAuth 승인과 1번 config 준비는 끝났다. 다음 사용자 개입이 필요하다면 여러 번 나누지 말고 `01-auto-guide-v1` 실제 Project 연결에 필요한 클릭을 승인 묶음으로 제시한다.

이 파일은 새 파일을 만들지 않고 계속 같은 파일을 덮어쓴다.