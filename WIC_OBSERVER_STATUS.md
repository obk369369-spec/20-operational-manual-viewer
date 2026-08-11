# WIC OBSERVER STATUS

최종 갱신: 2026-08-11 17:19 KST
상태: ACTIVE
목적: 각 WIC 도구·업무의 실제 진행, 증거, blocker, 다음 작업을 한 파일에서 확인한다.
운영 규칙 원본: `WIC_GLOBAL_OPERATING_RULES.md`
고객업무 공통 원본: `CUSTOMER_WORKFLOW_MASTER.md`

---

# 1. 지금 한눈에 보기

- 제3자 독립검증 실제 run 증거: **0개 / HOLD**
- CircleCI: GitHub OAuth 연결 + 1번 `.circleci/config.yml` commit/read-back 완료. actual run/result URL은 아직 없음.
- GitHub/Deno/GitHub Actions 실행 증거는 제3자 독립검증으로 계산하지 않는다.
- 현재 확정 PASS 도구: **없음**
- 전체 완료율: **산정중(HOLD)** — 검증 완료 단위를 전수 확인하기 전 임의 % 금지.
- 원칙: 완료작업 반복 금지 → blocker는 HOLD 기록 → 즉시 다음 실행 가능 항목으로 이동.

상태: 🟢 PASS = 실제 입력→실행→출력→검증 / 🟠 PARTIAL-HOLD = 실제 개선·실행 근거 있으나 E2E/독립검증 미완료 / 🔴 HOLD = blocker / ⚪ NEXT = 다음 실행 대상

---

# 2. 이번 회차 실제 수행 및 새 증거

1. 기존 `WIC_OBSERVER_STATUS.md`를 먼저 read-back하고 최신 restart point를 확인했다. 기존 이메일/7번 중앙마스터 통합, 1번 CircleCI config 생성, 13번 Deno success 확인, 05 수정, 09 blocker는 반복하지 않았다.
2. 1번 Deno 실패 경계를 추가 역추적했다.
   - `4fe5144618133ade09a899606bff0f43f01f03c6` → failure / `https://console.deno.com/obk369369-spec/01-auto-guide-v1/builds/trqm93hqzd5q`
   - `a2b2d3741de27e59ec8d4118d774cf1d4988711d` → failure / `https://console.deno.com/obk369369-spec/01-auto-guide-v1/builds/384xthf59p9a`
   - `506de17ff498625ae80b3eb010071ca7459ce570` → failure / `https://console.deno.com/obk369369-spec/01-auto-guide-v1/builds/v7sq0k06gqc4`
   - `006fa70b38424f11c4aa9172a42d9697cdee4e28` → failure / `https://console.deno.com/obk369369-spec/01-auto-guide-v1/builds/b96exkvgf3pe`
   - `778898b987fa34452fc49deb260520ac88e4bc42` → failure / `https://console.deno.com/obk369369-spec/01-auto-guide-v1/builds/mdyd4x4ye8z5`
3. 따라서 확인 가능한 commit 범위에서 1번 Deno 실패는 최소 **2026-04-23 commit `778898b...` 시점까지 이미 존재**했다. 최근 중앙마스터 연결/CircleCI 추가는 원인이 아니다.
4. 13번 `index.html`을 직접 read-back했다. 현재 UI의 `업로드용 다운로드` 버튼은 실제 홈페이지 전송이 아니라 `els.uploadBtn.addEventListener('click', ()=> downloadCSV('upload'));`로 동작한다. 즉 현재 저장소의 확인 가능한 본체는 **업로드용 CSV 생성/다운로드 도구**이며, 실제 worldic 서버 endpoint/API 전송 코드는 식별되지 않았다.
5. 13번은 따라서 Deno/Pages 배포 성공과 실제 홈페이지 업로드 성공을 동일시할 수 없다. 실제 업로드 E2E는 별도의 uploader/backend/endpoint 자산을 찾아야 한다.
6. 이 파일은 새 파일을 만들지 않고 같은 `WIC_OBSERVER_STATUS.md` 경로에 덮어쓰기 갱신했다.

---

# 3. 최우선 업무/도구 상태

| 우선 | 업무/도구 | 상태 | 실제 근거 | blocker | 다음 행동 |
|---|---|---|---|---|---|
| 1 | 이메일 수집 | 🟠 PARTIAL-HOLD | 중앙 공통마스터 commit/read-back 존재 | 실제 자동수집 실행자산/실행 URL 미식별 | 새로운 실행자산 근거가 발견되면 즉시 연결 |
| 2 | 7번 고객 컨택 판단 | 🟠 PARTIAL-HOLD | 중앙마스터 참조 확인 | 실제 7번 실행판 미확인 | 실행판 식별 후 고객 입력→판정 E2E |
| 3 | 1번 중간/최종 안내서 | 🟠 PARTIAL-HOLD | Deno failure를 2026-04-23까지 actual status URL로 확인 | Deno build log 원문 미확보, synthetic TOC 미제거, CircleCI actual run 0 | build log 원문 확보 또는 더 오래된 status가 존재하는지 확인; CircleCI actual run 연결 |
| 4 | 37번 메타데이터 | 🔴 HOLD | 규칙 존재 | 생산 실행자산 미확인 | 실행자산 식별 즉시 원본→결과 E2E |
| 5 | 13번 엑셀 자동 업로드 | 🟠 PARTIAL-HOLD | 본체 read-back: `uploadBtn`은 `downloadCSV('upload')` 호출 | 실제 홈페이지 uploader/backend/endpoint 미식별 | 별도 uploader 저장소·스크립트·API 자산 추적. 현재 UI 재배포 반복 금지 |
| 6 | 6번 목차 정리 | 🟠 PARTIAL-HOLD | 회귀 fixture commit 존재 | 승인 golden output 및 actual run 부족 | 승인 fixture 확보 후 회귀 run |
| 7 | 2번 입찰 | 🔴 HOLD | 수동 UI 흔적 | 나라장터 실엔진 없음 | 기존 실엔진 근거 발견 시 재사용 |
| 8 | 28~31 | 🔴 HOLD | 역할·규칙 존재 | 구체 실행 저장소/파일 참조 미확인 | 실행자산 식별부터 진행 |

---

# 4. 외부검증 도입 — 2026-08-13 마감 병행

| 구조 | 현재 상태 | 실제 증거 | 판정 |
|---|---|---|---|
| CircleCI | OAuth 연결 + 1번 config 존재 | config commit `ec69102f276cb319c9e4b7aa939e359bf8847190`, read-back 완료 | actual run URL 0 → HOLD |
| GitHub Actions | 일부 저장소 workflow 존재 | 13번 `a45c75e...`, 6번 기존 workflow | 내부/플랫폼 검증, 독립검증으로 계산 금지 |
| Deno Deploy | 실제 배포 상태 존재 | 1번 다수 failure URL / 13번 success URL | 배포 증거일 뿐 독립검증 아님 |
| Codacy | 미연결 | 증거 없음 | HOLD |
| BrowserStack | 미연결 | 증거 없음 | HOLD |

자체 추론, GitHub 상태, Deno 배포, GitHub Actions를 제3자 독립검증으로 가장하지 않는다.

---

# 5. 실제 개선됨 / 남음

**실제 개선·확인됨**
- 1번 Deno 실패 시점을 **2026-04-23**까지 actual status URL로 추가 역추적했다.
- 따라서 최근 중앙 규칙 통합/CircleCI commit을 원인 후보에서 제외할 근거가 더 강화됐다.
- 13번의 현재 `업로드` 기능이 실제 서버 업로드가 아니라 **업로드용 CSV 다운로드**라는 본체 동작을 직접 확인했다.
- 13번에서 현재 UI만 계속 수정/재배포해도 홈페이지 업로드 E2E가 생기지 않는 직접 원인을 특정했다.

**남음**
- 이메일 수집 실제 실행자산/수집 run
- 7번 실제 실행판 및 고객 입력 E2E
- 1번 Deno build log 원문 또는 더 오래된 success status 경계
- 1번 synthetic TOC fallback 제거
- CircleCI 최초 actual run/result URL
- 37번 생산 실행자산
- 13번 실제 홈페이지 uploader/backend/endpoint/API
- 6번 승인 golden fixture + 회귀 run
- 2번 실엔진
- 28~31 실행자산 연결

---

# 6. 현재 restart point

- **이메일 수집 / 7번:** 중앙 규칙 통합은 완료 사실로 보존. 같은 문서 검색 반복 금지. 새로운 실행 저장소·스크립트·DB·브라우저 자산 근거가 생길 때만 복귀.
- **01:** 확인 가능한 Deno failure는 최소 `778898b987fa34452fc49deb260520ac88e4bc42`(2026-04-23)까지 지속. 다음은 build log 원문 확보가 우선이며, 더 오래된 commit/status가 있으면 success→failure 경계 계속 추적. CircleCI config 생성 반복 금지.
- **13:** 현재 본체의 `uploadBtn`은 `downloadCSV('upload')`만 수행. 다음은 **별도 uploader/backend/worldic endpoint 자산 식별**. 현 `index.html` 재배포를 실제 홈페이지 업로드로 간주하지 말 것.
- **37:** 생산 실행자산 식별 전 PASS 금지.
- **06:** 승인 fixture/actual run 근거 전 PASS 금지.
- **05:** 안전 수정 commit 완료 상태 유지. E2E 증거가 생길 때만 복귀.
- **09:** sample fallback 위험 확인 완료. 안전한 부분 수정 경로 없이는 전체 파일 덮어쓰기 금지.
- **외부검증:** CircleCI actual run이 최우선. 사용자 개입 필요 시 승인/클릭을 묶어서 제시.

이 파일은 앞으로도 새 파일을 만들지 않고 같은 파일을 덮어쓴다.