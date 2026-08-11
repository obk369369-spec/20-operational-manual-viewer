# WIC OBSERVER STATUS

최종 갱신: 2026-08-11 12:24 KST
상태: ACTIVE
목적: 링크 하나에서 각 도구의 현재 상태·개선된 부분·막힌 부분·다음 작업을 바로 이해할 수 있게 보여주는 사람용 관찰판.
운영 규칙 원본: `WIC_GLOBAL_OPERATING_RULES.md` 단일 원본만 사용.

---

# 1. 지금 한눈에 보기

- 제3자 외부검증 실제 run 증거: **0개 / HOLD**
- CircleCI: 사용자 화면 기준 GitHub OAuth는 `obk369369-spec` 연결됨. **그러나 WIC 저장소의 실제 외부 CI run/result URL은 아직 없음. 따라서 독립검증 PASS 금지.**
- 현재 기능 PASS 도구: **확정 가능한 PASS 없음**
- 전체 완료율: **산정중(HOLD)** — 검증 완료 작업단위 전수 수치화 전에는 임의 % 금지
- 진행 원칙: **우선도구 실제 개선 시도 → 더 못 나가면 HOLD 기록 → 즉시 다음 실행 가능한 도구 → 새 근거가 생기면 우선도구로 복귀**

상태: 🟢 PASS = 실제 입력→실행→출력→검증 / 🟠 PARTIAL-HOLD = 일부 실기능 존재 또는 코드 개선 commit 확보했으나 E2E 미검증 / 🔴 HOLD = 현재 blocker / ⚪ NEXT = 다음 실행 대상

---

# 2. 이번 회차 실제 수행·증거

1. 기존 `WIC_OBSERVER_STATUS.md`와 최신 restart point를 먼저 읽었다. 이전 회차의 05 쓰기 재시도 → 불가하면 09 이동 지점에서 재개했다.
2. `05-report-generator/index.html` 원본을 다시 읽고, 입력하지 않은 시장동향·기업동향·정책·수요전망·기술동향 등을 고정 본문으로 생성하던 코드를 실제 수정했다.
3. **05 실제 개선 commit:** `b2af1f445477b7c7fbdbebbe36b26418dbd49276`
   - 검증된 요약문을 필수 입력으로 변경
   - 입력하지 않은 사실 자동 생성 제거
   - 결과는 사용자가 입력한 제목·키워드·검증된 요약만 구조화
   - 화면에도 `입력 내용만 사용 / 입력하지 않은 사실은 자동 생성하지 않음` 표시
4. 05 수정 후 GitHub read-back으로 새 파일 blob `5bf19ce1fd9d31319c80a0230ee4c46102881f85`를 확인했다.
5. 단, 이번 환경에서 05의 실제 브라우저 입력→클릭→출력 E2E run/result URL은 확보하지 못했다. 따라서 **PASS가 아니라 PARTIAL-HOLD**다.
6. restart 규칙에 따라 09번으로 즉시 이동하여 `09-contents-making-tool/index.html` 실제 코드를 읽었다.
7. **09 새 blocker 특정:** localStorage가 비었거나 파싱 오류가 나면 `createInitialSampleData()`가 자동 실행되어 검증되지 않은 예시 데이터를 실제 목록에 주입한다. 예시에는 후지경제/SK 스페셜티 수요 분석, Global Insight Services SF6 보고서, `조용준 박사님 요청 후보 1순위`, `WIC 무료 요약 자료` 등의 구체 주장이 포함돼 있다.
8. 09는 대형 단일 HTML이고 현재 connector가 전체 파일을 한 번에 안전하게 재구성하기 어려워, 이번 회차에는 부분 지식만으로 덮어쓰지 않았다. **수정 방향은 `loadState()`의 fallback을 `contents=[]`로 바꾸고 검증되지 않은 sample data 자동주입을 제거하는 것.**

---

# 3. 최우선 도구

| 우선 | 도구 | 상태 | 실제 확인된 것 | blocker | 개선방법 / 복귀조건 |
|---|---|---|---|---|---|
| 1 | 이메일 수집 | 🔴 HOLD | 공통 규칙·검증기준 | 전용 실행자산 미확인 | 새 실행파일/run URL 근거 발견 시 복귀 |
| 2 | 7번 고객 컨택 판단 | 🔴 HOLD | 잘못된 `07-wic-setting-tool-v1` 배제 | 실제 실행판 미확인 | 올바른 실행자산 근거 발견 시 복귀 |
| 3 | 1번 중간/최종 안내서 | 🔴 HOLD | 실제 HTML + Deno POST 코드 + synthetic TOC fallback 위험 | endpoint 성공증거 없음, 브라우저 E2E 미확보 | 실행환경에서 synthetic TOC 제거→TOC 없음 HOLD→실제 입력 E2E |
| 4 | 37번 메타데이터 | 🔴 HOLD | 규칙 존재 | 생산 실행자산 미확인 | 실행자산 근거 발견 시 E2E |
| 5 | 13번 엑셀 자동 업로드 | 🟠 PARTIAL-HOLD | 입력→매핑→미리보기→XLSX 생성 | 실제 홈페이지 업로드 endpoint/API 없음 | endpoint/브라우저 자동화 근거 발견 시 복귀 |
| 6 | 6번 목차 정리 | 🟠 PARTIAL-HOLD | 저장소·엔진 흔적 | 승인 golden fixture/expected output 부족 | 승인 fixture 발견 시 회귀검증 |
| 7 | 2번 입찰 | 🔴 HOLD | 수동 UI 확인 | 나라장터 자동수집/API/로그인/투찰 엔진 없음 | 기존 실엔진 근거 발견 시 재사용 |
| 8 | 28~31 | 🔴 HOLD | 역할·규칙 분리 | 실행 저장소/파일 참조 없음 | 구체 실행자산 발견 시 복귀 |

---

# 4. 다음 실행 가능한 도구

| 도구 | 상태 | 이번 판단 | 다음 행동 |
|---|---|---|---|
| 05 Report Generator | 🟠 PARTIAL-HOLD | **안전 수정 commit + read-back 완료** | 외부/브라우저 E2E가 생기면 실제 입력 검증 후 PASS 판단 |
| 09 Contents Making Tool | 🟠 PARTIAL-HOLD | **검증되지 않은 sample data 자동주입 위험 특정** | 안전한 전체파일 쓰기 경로 확보 시 sample fallback 제거. 불가하면 다음 실행 가능한 업무 도구로 이동 |
| 08 English Verb Exercise | 🟠 PARTIAL-HOLD | Local-only | 업무 우선순위 낮음 |
| 27 Technical Book Verifier | 🟠 PARTIAL-HOLD | 과거 실행 UI만 확인 | 현재 실행자산 새 근거 있을 때 복귀 |
| 나머지 03/04/10/11/12/14/19/21/22/23/24/25/26 | 🔴 HOLD | 기존 확인 반복금지 | 새 파일명/run URL/기능근거가 생길 때만 재개 |

---

# 5. 외부검증 도입 상태 — 2026-08-13 기준 병행

| 외부구조 | 현재 | 실제 증거 | 다음 단계 |
|---|---|---|---|
| CircleCI | 🟠 OAuth 연결 / run 0 | 사용자 화면에서 GitHub OAuth `Connected to obk369369-spec`; 외부 run URL 없음 | WIC 저장소 1개를 실제 Project/파이프라인으로 연결해 최초 외부 run URL 확보 |
| Codacy | 🔴 0 | 연결 증거 없음 | CircleCI 실 run이 막힐 때 사용자 승인 묶음 후보 |
| BrowserStack | 🔴 0 | 연결 증거 없음 | UI E2E가 필요한 우선도구에 후순위 연결 |

GitHub Actions와 자체 코드 추론은 내부검증으로만 사용하며 제3자 독립검증으로 가장하지 않는다.

---

# 6. 이번 실제 개선점과 남은 핵심

**실제 개선됨**
- 05에서 입력 밖 사실을 자동 생성하던 본문을 제거하는 실제 GitHub commit 생성.
- 수정 결과를 GitHub read-back으로 확인.
- 09에서 단순 UI 점검을 넘어 검증되지 않은 고객·발행사·자료 sample data의 자동주입 경로를 코드 수준에서 특정.
- CircleCI는 `미승인`이 아니라 `GitHub OAuth 연결됨 / 실제 외부 run 미완료`로 상태를 정확히 정정.

**남음**
- 05 실제 브라우저 E2E run/result URL
- 09 sample fallback 실제 제거 commit + E2E
- 1번 synthetic TOC fallback 실제 제거 commit + E2E
- 13 실제 업로드 연결
- 6 승인 fixture 확보
- CircleCI WIC 저장소 최초 외부 run URL
- 이메일/7/37 실제 실행자산 식별

---

# 7. 막힘 처리 규칙

`원인 확인 → 가능한 최소 수정 1회 → 실행/검증 → 실패하면 HOLD + 개선방법 + restart point → 즉시 다음 도구`

같은 404/같은 저장소 검색/같은 HOLD 진단 반복 금지. 상태판 변경만 기능개선으로 계산하지 않는다.

---

# 8. 현재 restart point

- **05:** 안전 수정 commit `b2af1f445477b7c7fbdbebbe36b26418dbd49276` 및 read-back 완료. 같은 코드수정 반복 금지. 외부/브라우저 E2E가 확보될 때만 복귀.
- **09:** `loadState()`에서 localStorage 없음/오류 시 `createInitialSampleData()`로 검증되지 않은 예시 데이터를 주입하는 경로 특정 완료. 동일 조사 반복 금지. 다음 실제 수정점은 fallback을 빈 배열로 변경하고 sample 자동주입을 제거하는 것.
- 09 전체파일 안전 수정이 현재 연결에서 막히면 HOLD로 두고 즉시 다음 실행 가능한 업무 도구로 이동.
- **우선도구 복귀 조건:** 이메일/7/37 실행자산, 1번 실행환경, 13 endpoint, 6 fixture 중 새 근거가 생길 때 즉시 우선순위로 복귀.
- **외부검증:** CircleCI OAuth 승인은 끝났으므로 다음 목표는 설명/설정이 아니라 WIC 저장소의 실제 최초 외부 run/result URL 1개를 확보하는 것.

이 파일은 새 파일을 만들지 않고 계속 같은 파일을 덮어쓴다.