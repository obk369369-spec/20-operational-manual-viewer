# WIC OBSERVER STATUS

최종 갱신: 2026-08-11 23:23 KST
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
2. 09번 `index.html`에서 실제 blocker 구간을 다시 정확히 확인했다.
   - 저장 데이터가 없으면 `contents = createInitialSampleData();`
   - 예외 발생 시에도 `contents = createInitialSampleData();`
   - `createInitialSampleData()` 안에 `sample-1` 등 embedded sample record가 존재.
3. 09번 production synthetic 제거를 위해 안전한 checkout/patch 경로를 시도했으나 현재 실행 환경의 로컬 Git checkout은 `Could not resolve host: github.com`으로 실패했다. GitHub connector는 현재 파일 전체 replace는 가능하지만 대형 `index.html`의 부분 patch primitive가 없어 전체 덮어쓰기는 안전하지 않다고 판단했다.
4. 따라서 09번 synthetic 본체 제거는 **HOLD**로 남기고, 같은 실패를 반복하지 않도록 restart point를 갱신했다.
5. 09번 내부 플랫폼 게이트 commit `f28840d3...`에 연결된 workflow run을 조회했으나 connector가 제공하는 commit-run 조회는 PR-triggered run만 반환하며 결과는 0개였다. 이것을 actual run 부재의 절대 증거로 과장하지 않는다.
6. 다음 실행 가능한 개선으로 09번 `.github/workflows/platform-evidence.yml`에 `workflow_dispatch`를 추가해 수동 실행 가능한 내부 플랫폼 증거 경로를 만들었다.
   - commit: `1c0c1609ee4a53104c00d5ca94b93293db4a9d33`
   - read-back blob: `237d6a03f41fd28196a2a668932e89628c5e6d14`
   - 분류 문구는 그대로 `Internal platform validation`, `not independent validation` 유지.
7. CircleCI public search에서 `01-auto-guide-v1`의 공개 actual run/result URL은 식별되지 않았다. CircleCI API 기반 자동 project setup은 token/write 권한이 필요하므로 현재 연결 구조만으로는 신규 project/run 생성 불가.
8. 28번 저장소명 검색 및 `publisher` 관련 설치 저장소 검색에서도 신규 전용 실행자산은 식별되지 않았다.
9. 이 파일은 새 파일을 만들지 않고 기존 `WIC_OBSERVER_STATUS.md`를 같은 경로에서 덮어쓰기 갱신한다.

---

# 3. 최우선 업무/도구 상태

| 우선 | 업무/도구 | 상태 | 실제 근거 | blocker | 다음 행동 |
|---|---|---|---|---|---|
| 1 | 이메일 수집 | 🟠 PARTIAL-HOLD | 중앙 공통마스터 commit/read-back 존재 | 실제 자동수집 실행자산/실행 URL 미식별 | 새로운 실행 저장소·스크립트·DB·브라우저 자산 발견 시 즉시 연결 |
| 2 | 7번 고객 컨택 판단 | 🟠 PARTIAL-HOLD | 중앙마스터 참조 확인 | 실제 7번 실행판 미확인 | 실행판 식별 후 고객 입력→판정 E2E |
| 3 | 1번 중간/최종 안내서 | 🟠 PARTIAL-HOLD | production synthetic 경로 확인 + CircleCI 차단게이트 commit `fca0955c...` / read-back `49f0832...` | 대형 단일 HTML 안전 수정경로 미확보, CircleCI actual run/result URL 미확보 | 안전한 patch/checkout 경로 확보 후 synthetic 생성 제거 → CircleCI 실제 project/run URL 기록 |
| 4 | 37번 메타데이터 | 🔴 HOLD | 규칙 존재, GitHub App 설치 목록에서 전용 실행 저장소 미식별 | 생산 실행자산 미확인 | 기존 파일/저장소/외부구조 증거 발견 시 원본→결과 E2E |
| 5 | 13번 엑셀 자동 업로드 | 🟠 PARTIAL-HOLD | `uploadBtn → downloadCSV('upload')`; workflow 오표기 수정 commit `c3f43ce...`, read-back `0943d2f...` | 실제 홈페이지 uploader/backend/endpoint 미식별 | 별도 uploader/backend/worldic endpoint 자산 발견 시 연결. 현재 UI 재배포 반복 금지 |
| 6 | 6번 목차 정리 | 🟠 PARTIAL-HOLD | workflow 오표기 수정 commit `0b307cc...` | 승인 golden output 및 신뢰 가능한 actual run/result URL 부족 | 승인 golden fixture 확보 후 회귀 run |
| 7 | 2번 입찰 | 🔴 HOLD | current body localStorage 기반 Local-only UI | 나라장터 실조회/로그인/수집/제출 엔진 미식별 | 별도 실엔진 자산 발견 시에만 연결 |
| 8 | 28~31 | 🔴 HOLD | 28/publisher 설치 저장소 검색에서도 신규 전용 실행자산 미식별 | 기존 실행자산 근거 부족 | 기존 외부구조/파일/저장소 근거 발견 시 연결; 새 껍데기 생성 금지 |
| 9 | 09번 컨텐츠 자료 안내 | 🟠 PARTIAL-HOLD | synthetic fallback 실코드 확인 + 내부 gate `f28840d3...`; manual trigger 추가 commit `1c0c1609...`, read-back `237d6a0...` | production synthetic 함수 제거용 안전 부분 patch 경로 없음; 로컬 checkout DNS 실패 | 안전한 부분 patch 가능 connector/checkout 경로 확보 후 `createInitialSampleData()` 제거/빈 상태 fail-closed 처리 → 내부 run URL 기록 |

---

# 4. 외부검증 도입 — 2026-08-13 마감 병행

| 구조 | 현재 상태 | 실제 증거 | 판정 |
|---|---|---|---|
| CircleCI | 1번 config 존재 + synthetic-data gate 강화 | commit `fca0955c5e12ce1c25886c6ba6595aac1601ab86`, read-back `49f08323e12eb551e57ff874e8a521c7d6f15347` | 공개 actual run/result URL 미식별 → HOLD |
| GitHub Actions / 6번 | 독립검증 오표기 수정 완료 | commit `0b307cc...` | 내부/플랫폼 검증으로만 표기 |
| GitHub Actions / 13번 | 독립검증 오표기 수정 완료 | commit `c3f43ce...`, read-back `0943d2f...` | 내부/플랫폼 검증으로만 표기 |
| GitHub Actions / 09번 | synthetic fallback 차단 gate + manual trigger 경로 | commits `f28840d3...`, `1c0c1609...`; read-back `237d6a0...` | 내부/플랫폼 검증이며 actual result URL 전 PASS 금지 |
| Deno Deploy | 실제 배포 상태 존재 | 1번 failure / 13번 success 근거 기존 보존 | 배포 증거일 뿐 독립검증 아님 |
| Codacy | 미연결 | 증거 없음 | HOLD |
| BrowserStack | 미연결 | 증거 없음 | HOLD |

자체 추론, GitHub 상태, Deno 배포, GitHub Actions를 제3자 독립검증으로 가장하지 않는다.

---

# 5. 실제 개선됨 / 남음

**실제 개선·확인됨**
- 중앙 상태와 restart point를 가장 먼저 read-back했다.
- 09번 synthetic 제거를 안전한 checkout/patch 방식으로 시도했고, 현재 로컬 checkout DNS blocker와 connector의 부분 patch 부재를 실제로 확인했다.
- 위험한 대형 HTML 전체 덮어쓰기를 하지 않았다.
- 09번 내부 플랫폼 workflow에 `workflow_dispatch`를 실제 추가해 이후 수동 run 경로를 확보했다.
- commit `1c0c1609...` 및 read-back blob `237d6a0...` 증거를 확보했다.
- GitHub Actions를 독립검증으로 오표기하지 않았다.

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
- **01:** synthetic blocker와 CircleCI gate는 확인 완료. 전체 HTML 덮어쓰기가 아닌 안전한 부분 patch/checkout 경로를 확보해 synthetic 생성부를 fail-closed/HOLD 방식으로 제거. 실제 CircleCI project/run URL 없이는 PASS 금지.
- **37:** GitHub App 설치 검색에서 전용 실행 저장소 미식별. 기존 파일·외부구조·저장소 증거 발견 시 즉시 생산 E2E로 전환.
- **13:** 실제 uploader/backend/worldic endpoint/API 미식별. 신규 자산 근거 없이는 반복 검색/재배포 금지.
- **06:** 승인 golden fixture 또는 신뢰 가능한 새 run 근거가 생길 때 복귀.
- **02:** current body는 local-only localStorage UI. 별도 나라장터 실연동 엔진 근거 식별 전 PASS 금지.
- **28~31:** 28/publisher 검색에서도 신규 전용 실행 저장소 미식별. 새 껍데기 저장소 생성 금지.
- **09:** 내부 gate와 `workflow_dispatch` 추가까지 완료. production synthetic 제거는 현재 안전 부분 patch 경로 부재 때문에 HOLD. 다음 회차에는 같은 checkout 실패를 반복하지 말고, connector에서 부분 수정 primitive가 제공되거나 기존 외부 checkout 자산이 식별될 때 즉시 `createInitialSampleData()` 두 호출+함수+embedded sample records를 제거하고 빈 배열/fail-closed로 전환한다.
- **외부검증:** CircleCI actual run/result URL 또는 다른 실제 제3자 서비스 run/result URL 확보가 최우선. 제3자 검증은 실제 외부 서비스 결과 URL이 있을 때만 인정한다.

이 파일은 앞으로도 새 파일을 만들지 않고 같은 파일을 덮어쓴다.