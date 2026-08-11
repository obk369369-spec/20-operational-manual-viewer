# WIC OBSERVER STATUS

최종 갱신: 2026-08-11 21:20 KST
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
2. 중앙 상태 저장소를 실제 commit 검색으로 재식별했다: `obk369369-spec/20-operational-manual-viewer`.
3. 1번 production `index.html`은 대형 단일 파일이라 connector의 전체파일 덮어쓰기만으로 synthetic 코드 제거를 강행하면 손상 위험이 커 HOLD 유지했다. 기존 synthetic blocker와 CircleCI gate 증거는 그대로 보존한다.
4. 37번 실행 저장소를 GitHub App 설치 저장소에서 검색했으나 `37` 전용 저장소는 새로 식별되지 않았다. 실행자산 미확인으로 HOLD 유지했다.
5. 13번 저장소 `obk369369-spec/13-excel-upload`의 과거 외부검사 workflow를 직접 read-back했다.
   - 기존 `.github/workflows/external-evidence.yml`에서 job 이름이 `Independent validation`으로 표시되어 있었다.
   - 실제 내용은 GitHub Actions 내부 정적 HTML 검사이므로 제3자 독립검증으로 표기하면 안 된다.
6. 13번 workflow 오표기를 실제 수정했다.
   - commit: `c3f43ce83864f8dc72efb48802d5f92149c150c2`
   - read-back blob: `0943d2f6ebe8869a10e156a18e55806b12dd7d86`
   - `External collaboration evidence` → `GitHub platform evidence`
   - `Independent validation` → `Internal platform validation`
   - `Generate evidence from real source` → `Generate GitHub platform evidence from real source`
   - archive 명칭도 platform-evidence로 수정.
7. 위 commit에 대해 connector의 workflow run 조회 결과는 0개였다. 따라서 13번은 PASS로 올리지 않았다.
8. 13번 저장소 코드 검색에서 uploader/backend/worldic endpoint/API를 새로 식별하지 못했다. 현재 본체 `uploadBtn → downloadCSV('upload')` blocker는 그대로 유지한다.
9. 이 파일은 새 파일을 만들지 않고 같은 `WIC_OBSERVER_STATUS.md` 경로에 덮어쓰기 갱신한다.

---

# 3. 최우선 업무/도구 상태

| 우선 | 업무/도구 | 상태 | 실제 근거 | blocker | 다음 행동 |
|---|---|---|---|---|---|
| 1 | 이메일 수집 | 🟠 PARTIAL-HOLD | 중앙 공통마스터 commit/read-back 존재 | 실제 자동수집 실행자산/실행 URL 미식별 | 새로운 실행 저장소·스크립트·DB·브라우저 자산 발견 시 즉시 연결 |
| 2 | 7번 고객 컨택 판단 | 🟠 PARTIAL-HOLD | 중앙마스터 참조 확인 | 실제 7번 실행판 미확인 | 실행판 식별 후 고객 입력→판정 E2E |
| 3 | 1번 중간/최종 안내서 | 🟠 PARTIAL-HOLD | production synthetic 경로 확인 + CircleCI 차단게이트 commit `fca0955c...` / read-back `49f0832...` | 대형 단일 HTML 안전 수정경로 미확보, CircleCI actual run 0 | 안전한 patch/checkout 경로 확보 후 synthetic 생성 제거 → CircleCI 실제 project/run URL 기록 |
| 4 | 37번 메타데이터 | 🔴 HOLD | 규칙 존재, 이번 회차 전용 GitHub 실행 저장소 검색 0 | 생산 실행자산 미확인 | 기존 파일/저장소/외부구조 증거 발견 시 원본→결과 E2E |
| 5 | 13번 엑셀 자동 업로드 | 🟠 PARTIAL-HOLD | `uploadBtn → downloadCSV('upload')`; workflow 오표기 수정 commit `c3f43ce...`, read-back `0943d2f...` | 실제 홈페이지 uploader/backend/endpoint 미식별, actual run 0 | 별도 uploader/backend/worldic endpoint 자산 추적. 현재 UI 재배포 반복 금지 |
| 6 | 6번 목차 정리 | 🟠 PARTIAL-HOLD | workflow 오표기 수정 commit `0b307cc...`; 해당 commit workflow run 0 | 승인 golden output 및 actual run/result URL 부족 | 승인 golden fixture 확보 후 회귀 run |
| 7 | 2번 입찰 | 🔴 HOLD | current body localStorage 기반 Local-only UI | 나라장터 실조회/로그인/수집/제출 엔진 미식별 | 별도 실엔진 자산 발견 시에만 연결 |
| 8 | 28~31 | 🔴 HOLD | 현재 GitHub App 설치 목록에서 전용 실행 저장소 미식별 | 기존 실행자산 근거 부족 | 기존 외부구조/파일/저장소 근거 발견 시 연결; 새 껍데기 생성 금지 |

---

# 4. 외부검증 도입 — 2026-08-13 마감 병행

| 구조 | 현재 상태 | 실제 증거 | 판정 |
|---|---|---|---|
| CircleCI | 1번 config 존재 + synthetic-data gate 강화 | commit `fca0955c5e12ce1c25886c6ba6595aac1601ab86`, read-back `49f08323e12eb551e57ff874e8a521c7d6f15347` | actual run URL 0 → HOLD |
| GitHub Actions / 6번 | 독립검증 오표기 수정 완료 | commit `0b307cc...`; actual run 0 | 내부/플랫폼 검증으로만 표기 |
| GitHub Actions / 13번 | 이번 회차 독립검증 오표기 수정 완료 | commit `c3f43ce83864f8dc72efb48802d5f92149c150c2`, read-back `0943d2f6ebe8869a10e156a18e55806b12dd7d86`; run 조회 0 | 내부/플랫폼 검증으로만 표기 |
| Deno Deploy | 실제 배포 상태 존재 | 1번 failure / 13번 success 근거 기존 보존 | 배포 증거일 뿐 독립검증 아님 |
| Codacy | 미연결 | 증거 없음 | HOLD |
| BrowserStack | 미연결 | 증거 없음 | HOLD |

자체 추론, GitHub 상태, Deno 배포, GitHub Actions를 제3자 독립검증으로 가장하지 않는다.

---

# 5. 실제 개선됨 / 남음

**실제 개선·확인됨**
- 13번 GitHub Actions 내부 검사가 `Independent validation`이라고 오표기된 것을 직접 발견했다.
- 13번 workflow 명칭을 내부/플랫폼 검증으로 실제 수정하고 commit/read-back을 확보했다.
- 37번 전용 실행 저장소가 현재 GitHub App 설치 검색에서 새로 발견되지 않았음을 확인했다.
- actual run이 없는 상태를 PASS로 과장하지 않았다.

**남음**
- 이메일 수집 실제 실행자산/수집 run
- 7번 실제 실행판 및 고객 입력 E2E
- 1번 production synthetic TOC/template/catalog/link 안전 제거
- 1번 CircleCI 최초 actual run/result URL
- 37번 생산 실행자산
- 13번 실제 홈페이지 uploader/backend/endpoint/API
- 13번 새 GitHub Actions actual run/result 확인
- 6번 승인 golden fixture + 회귀 run
- 2번 나라장터 실연동 엔진
- 28~31 기존 실행자산 근거 연결
- 실제 제3자 독립검증 구조 run 증거

---

# 6. 현재 restart point

- **이메일 수집 / 7번:** 중앙 규칙 통합은 완료 사실로 보존. 같은 문서 검색 반복 금지. 새로운 실행 저장소·스크립트·DB·브라우저 자산 근거가 생길 때만 복귀.
- **01:** synthetic blocker와 CircleCI gate는 이미 확인 완료. 다음은 전체 HTML 덮어쓰기 아닌 안전한 patch/checkout 경로를 확보해서 synthetic 생성부를 fail-closed/HOLD 방식으로 제거한다. 실제 CircleCI project/run URL 없이는 PASS 금지.
- **37:** GitHub App 설치 검색에서 전용 실행 저장소 미식별. 기존 파일·외부구조·저장소 증거가 발견되면 즉시 생산 E2E로 전환.
- **13:** workflow 독립검증 오표기는 commit `c3f43ce...`로 수정 완료. 다음은 실제 uploader/backend/worldic endpoint/API 자산 식별. 새 workflow run이 나타나더라도 내부 플랫폼 증거로만 기록한다.
- **06:** commit `0b307cc...` actual workflow run 0개. 승인 golden fixture 또는 새로운 run 근거가 생길 때 복귀.
- **02:** current body는 local-only localStorage UI. 별도 나라장터 실연동 엔진 근거 식별 전 PASS 금지.
- **28~31:** 현재 GitHub App 설치 저장소 목록에서 전용 저장소 미식별. 새 껍데기 저장소 생성 금지.
- **외부검증:** CircleCI actual run이 최우선. 사용자 개입 필요 시 OAuth/project 승인 클릭을 다른 승인 항목과 묶어서 제시.

이 파일은 앞으로도 새 파일을 만들지 않고 같은 파일을 덮어쓴다.