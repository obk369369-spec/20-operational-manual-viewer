# WIC OBSERVER STATUS

최종 갱신: 2026-08-11 22:17 KST
상태: ACTIVE
목적: 각 WIC 도구·업무의 실제 진행, 증거, blocker, 다음 작업을 한 파일에서 확인한다.
운영 규칙 원본: `WIC_GLOBAL_OPERATING_RULES.md`
고객업무 공통 원본: `CUSTOMER_WORKFLOW_MASTER.md`

---

# 1. 지금 한눈에 보기

- 제3자 독립검증 실제 run 증거: **0개 / HOLD**
- 현재 확정 PASS 도구: **없음**
- 전체 완료율: **산정중(HOLD)** — 검증 완료 단위를 전수 확인하기 전 임의 % 금지.
- 원칙: 완료작업 반복 금지 → blocker는 HOLD 기록 → 즉시 다음 실행 가능 항목으로 이동.
- GitHub Actions/Deno/GitHub 상태는 제3자 독립검증으로 계산하지 않는다.

상태: 🟢 PASS = 실제 입력→실행→출력→검증 / 🟠 PARTIAL-HOLD = 실제 개선·실행 근거 있으나 E2E/독립검증 미완료 / 🔴 HOLD = blocker / ⚪ NEXT = 다음 실행 대상

---

# 2. 이번 회차 실제 수행 및 새 증거

1. 기존 `WIC_OBSERVER_STATUS.md`를 먼저 read-back하고 최신 restart point를 확인했다. 기존 이메일/7번 중앙마스터 통합, 13번 uploadBtn 판정, 6번 workflow 오표기 수정, 2번 local-only 판정은 반복하지 않았다.
2. 중앙 상태 저장소를 이전 상태 commit `74162586e91079b3ce30a27993befbebb52a3bd5` 검색으로 재식별했다: `obk369369-spec/20-operational-manual-viewer`.
3. 13번 실제 uploader/backend/worldic endpoint/API를 연결 저장소 범위에서 다시 추적했으나 신규 실행자산은 식별되지 않았다. 따라서 기존 blocker를 HOLD 유지하고 UI 재배포는 반복하지 않았다.
4. 다음 실행 가능한 등록 도구로 이동해 09번 본체 `index.html`을 직접 확인했다.
   - 저장 데이터가 없을 때 `contents = createInitialSampleData();`
   - 파싱 예외 발생 시에도 `contents = createInitialSampleData();`
   - 함수 내부에 `sample-1` 등 실제처럼 보이는 고객/발행사/자료 예시가 내장되어 있음.
5. 09번 본체 전체 덮어쓰기는 현재 안전하지 않아 synthetic 생성부 제거 자체는 HOLD로 기록했다.
6. 대신 동일 synthetic 경로가 남은 상태를 자동으로 차단하는 **GitHub 내부 플랫폼 게이트**를 실제 추가했다.
   - 파일: `.github/workflows/platform-evidence.yml`
   - commit: `f28840d3ae71b156af2798a44338d7f7a081e9cc`
   - read-back blob: `5530f00e0b570c9d8f79c8701bd6cefa01b818af`
   - `createInitialSampleData` 또는 `id: "sample-`가 production `index.html`에 남아 있으면 FAIL.
   - job 이름과 증거 파일에 `Internal platform validation`, `not independent validation`을 명시했다.
7. 위 게이트는 GitHub Actions 내부 플랫폼 검사일 뿐 제3자 독립검증으로 계산하지 않는다. actual run/result URL 확보 전 PASS 금지.
8. 이 파일은 새 파일을 만들지 않고 기존 `WIC_OBSERVER_STATUS.md`를 같은 경로에서 덮어쓰기 갱신한다.

---

# 3. 최우선 업무/도구 상태

| 우선 | 업무/도구 | 상태 | 실제 근거 | blocker | 다음 행동 |
|---|---|---|---|---|---|
| 1 | 이메일 수집 | 🟠 PARTIAL-HOLD | 중앙 공통마스터 commit/read-back 존재 | 실제 자동수집 실행자산/실행 URL 미식별 | 새로운 실행 저장소·스크립트·DB·브라우저 자산 발견 시 즉시 연결 |
| 2 | 7번 고객 컨택 판단 | 🟠 PARTIAL-HOLD | 중앙마스터 참조 확인 | 실제 7번 실행판 미확인 | 실행판 식별 후 고객 입력→판정 E2E |
| 3 | 1번 중간/최종 안내서 | 🟠 PARTIAL-HOLD | production synthetic 경로 확인 + CircleCI 차단게이트 commit `fca0955c...` / read-back `49f0832...` | 대형 단일 HTML 안전 수정경로 미확보, CircleCI actual run 0 | 안전한 patch/checkout 경로 확보 후 synthetic 생성 제거 → CircleCI 실제 project/run URL 기록 |
| 4 | 37번 메타데이터 | 🔴 HOLD | 규칙 존재, GitHub App 설치 목록에서 전용 실행 저장소 미식별 | 생산 실행자산 미확인 | 기존 파일/저장소/외부구조 증거 발견 시 원본→결과 E2E |
| 5 | 13번 엑셀 자동 업로드 | 🟠 PARTIAL-HOLD | `uploadBtn → downloadCSV('upload')`; workflow 오표기 수정 commit `c3f43ce...`, read-back `0943d2f...` | 실제 홈페이지 uploader/backend/endpoint 미식별, actual run 0 | 별도 uploader/backend/worldic endpoint 자산 추적. 현재 UI 재배포 반복 금지 |
| 6 | 6번 목차 정리 | 🟠 PARTIAL-HOLD | workflow 오표기 수정 commit `0b307cc...`; 해당 commit workflow run 0 | 승인 golden output 및 actual run/result URL 부족 | 승인 golden fixture 확보 후 회귀 run |
| 7 | 2번 입찰 | 🔴 HOLD | current body localStorage 기반 Local-only UI | 나라장터 실조회/로그인/수집/제출 엔진 미식별 | 별도 실엔진 자산 발견 시에만 연결 |
| 8 | 28~31 | 🔴 HOLD | 현재 GitHub App 설치 목록에서 전용 실행 저장소 미식별 | 기존 실행자산 근거 부족 | 기존 외부구조/파일/저장소 근거 발견 시 연결; 새 껍데기 생성 금지 |
| 9 | 09번 컨텐츠 자료 안내 | 🟠 PARTIAL-HOLD | synthetic fallback 실코드 확인 + 내부 게이트 commit `f28840d3...`, read-back `5530f00...` | production synthetic 함수 제거 미완료, actual run/result URL 없음 | 안전한 patch 경로 확보 후 `createInitialSampleData()` 제거/빈 상태 fail-closed 처리 → 내부 run 확인 |

---

# 4. 외부검증 도입 — 2026-08-13 마감 병행

| 구조 | 현재 상태 | 실제 증거 | 판정 |
|---|---|---|---|
| CircleCI | 1번 config 존재 + synthetic-data gate 강화 | commit `fca0955c5e12ce1c25886c6ba6595aac1601ab86`, read-back `49f08323e12eb551e57ff874e8a521c7d6f15347` | actual run URL 0 → HOLD |
| GitHub Actions / 6번 | 독립검증 오표기 수정 완료 | commit `0b307cc...`; actual run 0 | 내부/플랫폼 검증으로만 표기 |
| GitHub Actions / 13번 | 독립검증 오표기 수정 완료 | commit `c3f43ce83864f8dc72efb48802d5f92149c150c2`, read-back `0943d2f6ebe8869a10e156a18e55806b12dd7d86`; run 조회 0 | 내부/플랫폼 검증으로만 표기 |
| GitHub Actions / 09번 | synthetic fallback 차단 게이트 신규 추가 | commit `f28840d3ae71b156af2798a44338d7f7a081e9cc`, read-back `5530f00e0b570c9d8f79c8701bd6cefa01b818af` | 내부/플랫폼 검증이며 actual run/result URL 전 PASS 금지 |
| Deno Deploy | 실제 배포 상태 존재 | 1번 failure / 13번 success 근거 기존 보존 | 배포 증거일 뿐 독립검증 아님 |
| Codacy | 미연결 | 증거 없음 | HOLD |
| BrowserStack | 미연결 | 증거 없음 | HOLD |

자체 추론, GitHub 상태, Deno 배포, GitHub Actions를 제3자 독립검증으로 가장하지 않는다.

---

# 5. 실제 개선됨 / 남음

**실제 개선·확인됨**
- 중앙 상태 저장소와 최신 restart point를 먼저 read-back했다.
- 13번 uploader/backend/worldic endpoint 추가 검색에서 신규 자산이 없음을 확인하고 같은 UI 작업 반복을 중단했다.
- 09번 production에서 실제처럼 보이는 synthetic fallback 자동주입 경로를 직접 재확인했다.
- 09번 synthetic fallback이 남아 있으면 실패시키는 내부 GitHub 플랫폼 게이트를 실제 추가하고 commit/read-back을 확보했다.
- 새 게이트를 독립검증으로 오표기하지 않았다.

**남음**
- 이메일 수집 실제 실행자산/수집 run
- 7번 실제 실행판 및 고객 입력 E2E
- 1번 production synthetic TOC/template/catalog/link 안전 제거
- 1번 CircleCI 최초 actual run/result URL
- 37번 생산 실행자산
- 13번 실제 홈페이지 uploader/backend/endpoint/API
- 6번 승인 golden fixture + 회귀 run
- 2번 나라장터 실연동 엔진
- 28~31 기존 실행자산 근거 연결
- 09번 production `createInitialSampleData()` 제거 + actual GitHub Actions run/result URL
- 실제 제3자 독립검증 구조 run 증거

---

# 6. 현재 restart point

- **이메일 수집 / 7번:** 중앙 규칙 통합 완료 사실은 보존. 같은 문서 검색 반복 금지. 새로운 실행 저장소·스크립트·DB·브라우저 자산 근거가 생길 때만 복귀.
- **01:** synthetic blocker와 CircleCI gate는 확인 완료. 전체 HTML 덮어쓰기가 아닌 안전한 patch/checkout 경로를 확보해 synthetic 생성부를 fail-closed/HOLD 방식으로 제거. 실제 CircleCI project/run URL 없이는 PASS 금지.
- **37:** GitHub App 설치 검색에서 전용 실행 저장소 미식별. 기존 파일·외부구조·저장소 증거 발견 시 즉시 생산 E2E로 전환.
- **13:** 실제 uploader/backend/worldic endpoint/API는 이번 회차 추가 검색에서도 미식별. 신규 자산 근거 없이는 반복 검색/재배포 금지.
- **06:** commit `0b307cc...` actual workflow run 0개. 승인 golden fixture 또는 새로운 run 근거가 생길 때 복귀.
- **02:** current body는 local-only localStorage UI. 별도 나라장터 실연동 엔진 근거 식별 전 PASS 금지.
- **28~31:** 현재 GitHub App 설치 저장소 목록에서 전용 저장소 미식별. 새 껍데기 저장소 생성 금지.
- **09:** synthetic fallback 차단 내부 게이트는 commit `f28840d3...`로 추가 완료. 다음은 안전한 수정경로를 확보해 `createInitialSampleData()` 호출/함수와 embedded sample records를 제거하고 빈 데이터 상태를 fail-closed로 전환한다. GitHub Actions actual run은 내부 플랫폼 증거로만 기록한다.
- **외부검증:** CircleCI actual run이 최우선. 제3자 검증은 실제 외부 서비스 run/result URL이 있을 때만 인정한다.

이 파일은 앞으로도 새 파일을 만들지 않고 같은 파일을 덮어쓴다.