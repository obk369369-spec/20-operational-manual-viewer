# WIC OBSERVER STATUS

최종 갱신: 2026-08-11 20:22 KST
상태: ACTIVE
목적: 각 WIC 도구·업무의 실제 진행, 증거, blocker, 다음 작업을 한 파일에서 확인한다.
운영 규칙 원본: `WIC_GLOBAL_OPERATING_RULES.md`
고객업무 공통 원본: `CUSTOMER_WORKFLOW_MASTER.md`

---

# 1. 지금 한눈에 보기

- 제3자 독립검증 실제 run 증거: **0개 / HOLD**
- CircleCI: 1번 `.circleci/config.yml` 존재 및 이번 회차 synthetic-data 차단 규칙 강화 commit/read-back 완료. actual CircleCI run/result URL은 아직 없음.
- GitHub/Deno/GitHub Actions 실행 증거는 제3자 독립검증으로 계산하지 않는다.
- 현재 확정 PASS 도구: **없음**
- 전체 완료율: **산정중(HOLD)** — 검증 완료 단위를 전수 확인하기 전 임의 % 금지.
- 원칙: 완료작업 반복 금지 → blocker는 HOLD 기록 → 즉시 다음 실행 가능 항목으로 이동.

상태: 🟢 PASS = 실제 입력→실행→출력→검증 / 🟠 PARTIAL-HOLD = 실제 개선·실행 근거 있으나 E2E/독립검증 미완료 / 🔴 HOLD = blocker / ⚪ NEXT = 다음 실행 대상

---

# 2. 이번 회차 실제 수행 및 새 증거

1. 기존 `WIC_OBSERVER_STATUS.md`를 먼저 read-back하고 최신 restart point를 확인했다. 기존 이메일/7번 중앙마스터 통합, 13번 uploader blocker 확인, 6번 workflow 오표기 수정, 2번 local-only 판정은 반복하지 않았다.
2. GitHub App 연결 저장소 목록을 다시 확인했고 01~27 계열만 식별됐다. 이메일 수집/7번의 신규 실행 저장소 근거는 이번 회차에도 새로 식별되지 않아 같은 문서 검색을 반복하지 않고 HOLD 유지했다.
3. 1번 `index.html`을 직접 read-back하여 synthetic 데이터 경로가 실제로 여전히 남아 있음을 새로 확인했다.
   - `function defaultToc(keyword)` 존재
   - `firstNormalized.toc = defaultToc(...)` fallback 존재
   - 고정 `var TOC_TEMPLATE` 존재
   - `function publisherCatalog()` 하드코딩 카탈로그 존재
   - `example.com` placeholder 링크 존재
   - 현재 `index.html` blob: `6380858c7720d065d749fc9fe8395f0dbf117cbe`
4. 대형 `index.html`을 무리하게 전체 덮어써 손상시키지 않고, 외부검증 게이트부터 실제 강화했다.
   - 파일: `01-auto-guide-v1/.circleci/config.yml`
   - commit: `fca0955c5e12ce1c25886c6ba6595aac1601ab86`
   - read-back blob: `49f08323e12eb551e57ff874e8a521c7d6f15347`
   - 새 차단 규칙: `defaultToc`, `TOC_TEMPLATE`, `publisherCatalog`, `example.com/`이 production `index.html`에 남아 있으면 CircleCI에서 FAIL하도록 설정.
5. 위 commit에 대한 GitHub Actions workflow run을 조회했으나 `workflow_runs = 0개`였다. 이는 GitHub 플랫폼 run이 없다는 뜻이며 CircleCI actual run 증거를 대신하지 않는다.
6. 따라서 1번은 **PARTIAL-HOLD 유지**. synthetic 요소가 남은 본체를 PASS로 올리지 않았고, 외부검증도 actual CircleCI run URL이 없으므로 독립검증 PASS로 계산하지 않았다.
7. 이 파일은 새 파일을 만들지 않고 같은 `WIC_OBSERVER_STATUS.md` 경로에 덮어쓰기 갱신했다.

---

# 3. 최우선 업무/도구 상태

| 우선 | 업무/도구 | 상태 | 실제 근거 | blocker | 다음 행동 |
|---|---|---|---|---|---|
| 1 | 이메일 수집 | 🟠 PARTIAL-HOLD | 중앙 공통마스터 commit/read-back 존재 | 실제 자동수집 실행자산/실행 URL 미식별 | 새로운 실행자산 근거가 발견되면 즉시 연결 |
| 2 | 7번 고객 컨택 판단 | 🟠 PARTIAL-HOLD | 중앙마스터 참조 확인 | 실제 7번 실행판 미확인 | 실행판 식별 후 고객 입력→판정 E2E |
| 3 | 1번 중간/최종 안내서 | 🟠 PARTIAL-HOLD | `index.html` synthetic 경로 직접 확인 + CircleCI 차단게이트 강화 commit `fca0955c...` / read-back `49f0832...` | production 본체에 synthetic TOC/catalog/link 남음, CircleCI actual run 0 | 안전한 본체 수정 경로로 synthetic 생성 제거 → CircleCI 실제 project/run 연결 후 result URL 기록 |
| 4 | 37번 메타데이터 | 🔴 HOLD | 규칙 존재 | 생산 실행자산 미확인 | 실행자산 식별 즉시 원본→결과 E2E |
| 5 | 13번 엑셀 자동 업로드 | 🟠 PARTIAL-HOLD | 본체 read-back: `uploadBtn`은 `downloadCSV('upload')` 호출 | 실제 홈페이지 uploader/backend/endpoint 미식별 | 별도 uploader 저장소·스크립트·API 자산 추적. 현재 UI 재배포 반복 금지 |
| 6 | 6번 목차 정리 | 🟠 PARTIAL-HOLD | workflow 오표기 수정 commit `0b307cc...`; 해당 commit workflow run 0개 | 승인 golden output 및 actual run/result URL 부족 | 승인 golden fixture 확보 후 회귀 run |
| 7 | 2번 입찰 | 🔴 HOLD | current body localStorage 기반 Local-only UI | 나라장터 실조회/로그인/수집/제출 엔진 미식별 | 별도 실엔진 자산 발견 시에만 연결 |
| 8 | 28~31 | 🔴 HOLD | 현재 GitHub App 설치 목록에서 전용 실행 저장소 미식별 | 기존 실행자산 근거 부족 | 기존 외부구조/파일/저장소 근거 발견 시 연결; 새 껍데기 생성 금지 |

---

# 4. 외부검증 도입 — 2026-08-13 마감 병행

| 구조 | 현재 상태 | 실제 증거 | 판정 |
|---|---|---|---|
| CircleCI | config 존재 + synthetic-data gate 강화 | commit `fca0955c5e12ce1c25886c6ba6595aac1601ab86`, read-back `49f08323e12eb551e57ff874e8a521c7d6f15347` | actual run URL 0 → HOLD |
| GitHub Actions | 6번의 독립검증 오표기 수정 완료 | commit `0b307cc...`; actual run 0 | 내부/플랫폼 검증으로만 표기 |
| Deno Deploy | 실제 배포 상태 존재 | 1번 failure / 13번 success 근거 기존 보존 | 배포 증거일 뿐 독립검증 아님 |
| Codacy | 미연결 | 증거 없음 | HOLD |
| BrowserStack | 미연결 | 증거 없음 | HOLD |

자체 추론, GitHub 상태, Deno 배포, GitHub Actions를 제3자 독립검증으로 가장하지 않는다.

---

# 5. 실제 개선됨 / 남음

**실제 개선·확인됨**
- 1번 production `index.html`의 synthetic TOC fallback뿐 아니라 고정 TOC template, 하드코딩 publisher catalog, placeholder link까지 직접 확인했다.
- CircleCI 외부검증 config를 강화하여 위 synthetic 요소가 남아 있으면 FAIL하도록 실제 commit했다.
- commit/read-back 증거를 확보했고 actual CircleCI run이 아직 없다는 점은 PASS로 과장하지 않았다.

**남음**
- 이메일 수집 실제 실행자산/수집 run
- 7번 실제 실행판 및 고객 입력 E2E
- 1번 production synthetic TOC/template/catalog/link 제거
- 1번 Deno build log 원문 또는 실패 원인 직접 로그
- CircleCI 최초 actual run/result URL
- 37번 생산 실행자산
- 13번 실제 홈페이지 uploader/backend/endpoint/API
- 6번 승인 golden fixture + 회귀 run
- 2번 나라장터 실연동 엔진
- 28~31 기존 실행자산 근거 연결

---

# 6. 현재 restart point

- **이메일 수집 / 7번:** 중앙 규칙 통합은 완료 사실로 보존. 같은 문서 검색 반복 금지. 새로운 실행 저장소·스크립트·DB·브라우저 자산 근거가 생길 때만 복귀.
- **01:** `index.html` blob `6380858...`에 `defaultToc`, `TOC_TEMPLATE`, `publisherCatalog`, `example.com` placeholder가 실제 남아 있다. CircleCI gate는 commit `fca0955...`로 강화 완료. 다음은 대형 본체를 손상시키지 않는 수정 경로 확보 후 synthetic 생성부를 fail-closed/HOLD 방식으로 제거하고, CircleCI 실제 project/run URL을 확보한다.
- **13:** 현재 본체의 `uploadBtn`은 `downloadCSV('upload')`만 수행. 다음은 별도 uploader/backend/worldic endpoint 자산 식별.
- **37:** 생산 실행자산 식별 전 PASS 금지.
- **06:** commit `0b307cc...` actual workflow run 0개. 승인 golden fixture 또는 새로운 run 근거가 생길 때 복귀.
- **02:** current body는 local-only localStorage UI. 별도 나라장터 실연동 엔진 근거 식별 전 PASS 금지.
- **28~31:** 현재 GitHub App 설치 저장소 목록에서 전용 저장소 미식별. 새 껍데기 저장소 생성 금지.
- **외부검증:** CircleCI actual run이 최우선. 사용자 개입 필요 시 OAuth/project 승인 클릭을 다른 승인 항목과 묶어서 제시.

이 파일은 앞으로도 새 파일을 만들지 않고 같은 파일을 덮어쓴다.