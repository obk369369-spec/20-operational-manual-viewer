# WIC OBSERVER STATUS

최종 갱신: 2026-08-11 10:27 KST
상태: ACTIVE
목적: 링크 하나에서 각 도구의 현재 상태·개선된 부분·막힌 부분·다음 작업을 바로 이해할 수 있게 보여주는 사람용 관찰판.
운영 규칙 원본: `WIC_GLOBAL_OPERATING_RULES.md` 단일 원본만 사용.

---

# 1. 지금 한눈에 보기

- 자동 재개: **ON**
- 제3자 외부검증 실제 연결: **0개 / HOLD**
- 제3자 외부검증 후보: **CircleCI / Codacy / BrowserStack**
- 현재 기능 PASS 도구: **확정 가능한 PASS 없음**
- 현재 전략: **우선 도구를 먼저 실제 수정 → 실행 → 검증 시도. 현재 환경에서 더 이상 개선 불가하면 HOLD 기록 후 즉시 다음 도구로 이동**
- 전체 완료율: **산정중(HOLD)** — 검증 완료 작업단위 수가 아직 완전 수치화되지 않아 임의 % 금지

### 상태 표시
- 🟢 PASS = 실제 입력 → 실행 → 출력 → 검증 증거 확인
- 🟠 PARTIAL/HOLD = 일부 실제 기능/자산 존재하지만 핵심 실행·검증 미완료
- 🔴 HOLD = 현재 환경에서 다음 단계가 막힘
- ⚪ NEXT = 다음 확인/개선 대상

---

# 2. 이번 회차에서 실제로 수행한 것

1. 최신 restart point를 읽고 완료/반복금지 항목은 건너뛰었다.
2. `05-report-generator` 저장소를 다시 만들거나 수정하지 않고 현재 배포 근거만 확인했다. 저장소는 public/main으로 존재하지만 배포/Pages/Actions 관련 코드 검색 결과가 없었고, 공개 GitHub Pages 주소도 검색엔진에서 확인되지 않았다. **현재 실행 URL 증거 없음 → PARTIAL/HOLD 유지**.
3. `09-contents-making-tool`도 저장소 존재를 확인했고 공개 GitHub Pages 주소 검색 결과가 없었다. **현재 실행 성공 URL 증거 없음 → PARTIAL/HOLD 유지**.
4. 아직 상태판에 없던 등록 저장소를 추가 확인했다: `10-WIC-Finance-Dashboard`, `14-wic-homepage-editor`, `19-wic-business-promotion`, `22-Common-Item-kit`.
5. 위 4개 저장소 모두 현재 기본 브랜치의 `index.html`이 404였다. 이번 회차에는 실행자산을 특정하지 못했으므로 모두 **HOLD / PASS 금지**.
6. 설치된 GitHub 저장소 목록의 다음 페이지까지 확인했으며 추가 저장소 결과는 없었다. 현재 연결로 확인 가능한 등록 저장소 목록은 이번 상태판에 반영된 범위까지다.
7. 1번 `01-auto-guide-v1/index.html`은 현재 기본 브랜치에 실제로 존재함을 다시 확인했다. 다만 파일이 대형 단일 HTML이며 Word HTML 조각과 여러 진단/품질엔진 코드가 혼재되어 있고, 이번 회차의 GitHub 코드검색은 인덱싱되지 않아 기존 Deno 실패의 정확한 JS 오류 위치를 특정하지 못했다. **수정하지 않았으며 PASS로 올리지 않음**.
8. 외부검증 공식 경로를 재확인했다. CircleCI는 공식적으로 GitHub App 설치를 권장하며 관리자 1회 설치 후 저장소를 선택하는 구조다. BrowserStack Playwright 연동은 `BROWSERSTACK_USERNAME`과 `BROWSERSTACK_ACCESS_KEY`를 GitHub Secrets에 넣어야 실제 외부 실행이 가능하다. 따라서 현재 Chat/GitHub 연결만으로 계정 승인·비밀키 입력을 대신할 수 없어 **실제 외부검증 연결 0개/HOLD**다.

---

# 3. 최우선 도구

| 우선 | 도구 | 상태 | 지금 실제로 된 것 | 아직 안 된 핵심 | 다음 개선 |
|---|---|---|---|---|---|
| 1 | 이메일 수집 | 🔴 HOLD | 공통 규칙·검증기준 존재 | 전용 실행자산 위치 미확인 | 새 근거가 생기면 즉시 재개, 반복검색 금지 |
| 2 | 7번 고객 컨택 판단 | 🔴 HOLD | `07-wic-setting-tool-v1`이 다른 도구임을 확인 | 실제 7번 실행판 미확인 | 올바른 자산 근거 발견 시 재개 |
| 3 | 1번 중간/최종 안내서 | 🔴 HOLD | 현재 `index.html` 존재, 대형 단일 HTML 구조 확인 | 기존 Deno 실패의 정확한 JS 오류 위치 미특정 | Work/로컬 런타임처럼 실제 브라우저 콘솔·파일 전체 분석 가능한 환경에서 오류 위치 특정 후 최소 수정 |
| 4 | 37번 메타데이터 | 🔴 HOLD | 규칙 존재 | 실제 생산 실행자산 미확인 | 실행자산 근거 발견 시 E2E 검증 |
| 5 | 13번 엑셀 자동 업로드 | 🟠 PARTIAL/HOLD | 파일입력→매핑→미리보기→XLSX 생성 | 실제 홈페이지 업로드 기능 없음 | 외부 endpoint/API/브라우저 자동화 연결 |
| 6 | 6번 목차 정리 | 🟠 PARTIAL/HOLD | 실제 저장소·기존 엔진 흔적 | 승인 golden fixture/expected output 부족 | 승인 fixture 발견 시 실제 원문→결과 회귀검증 |
| 7 | 2번 입찰 | 🔴 HOLD | 현재 UI 실제 확인 | 나라장터 자동수집/API/로그인/투찰 엔진 없음 + 배포 실패 | 기존 실제 자동입찰 자산 근거 발견 시 재사용 |
| 8 | 28~31 | 🔴 HOLD | 역할·업무 규칙 분리 확인 | 실제 실행 저장소/파일 참조 없음 | 구체 자산 근거 발견 시만 재개 |

---

# 4. 나머지 등록 도구

| 도구 | 상태 | 확인된 실제 자산/상태 | blocker |
|---|---|---|---|
| 03 Coding Practice | 🔴 HOLD | 저장소 존재 | 코드검색 0 + README 404 |
| 04 Research Funding Generator | 🔴 HOLD | 저장소 존재 | README/index 404 |
| 05 Report Generator | 🟠 PARTIAL/HOLD | `index.html` 존재, localStorage/clipboard UI | 배포/실행 URL 증거 없음, 외부 데이터/API/검증 없음 |
| 08 English Verb Exercise | 🟠 PARTIAL/HOLD | `index.html`, Local-only 명시 | 서버 통신/외부검증 없음 |
| 09 Contents Making Tool | 🟠 PARTIAL/HOLD | `index.html` 존재 | 배포/실행 성공 URL 없음 |
| 10 WIC Finance Dashboard | 🔴 HOLD | 저장소 존재 | 현재 `index.html` 404 |
| 11 OBK Finance Planner | 🔴 HOLD | 저장소 존재 | index 404 + 코드검색 0 |
| 12 서브웹사이트 빌더 | 🔴 HOLD | 저장소 존재 | 실행파일 위치 미특정 |
| 14 WIC Homepage Editor | 🔴 HOLD | 저장소 존재 | 현재 `index.html` 404 |
| 19 WIC Business Promotion | 🔴 HOLD | 저장소 존재 | 현재 `index.html` 404 |
| 20 Operational Manual Viewer | 🟠 운영허브 | 중앙 규칙/상태판 저장소로 사용 중 | 기능도구 PASS와 별도 |
| 21 Sales Route Planner | 🔴 HOLD | 저장소 존재 | 실행파일/엔진 미특정 |
| 22 Common Item Kit | 🔴 HOLD | 저장소 존재 | 현재 `index.html` 404 |
| 23 World Advisor | 🔴 HOLD | 저장소 존재 | 실행파일/엔진 미특정 |
| 24 Easy Video Maker | 🔴 HOLD | 저장소 존재 | README/index 404 |
| 25 Free Content Maker | 🔴 HOLD | 저장소 존재 | README/index 404 |
| 26 Online Item Shop | 🔴 HOLD | 저장소 존재 | README/index 404 |
| 27 Technical Book Verifier | 🟠 PARTIAL/HOLD | 과거 실행 UI 확인 | 현재 기본 브랜치 index 404 |

---

# 5. 외부검증 연결 상태

| 외부구조 | 실제 상태 | 지금 확인된 연결 조건 | 판단 |
|---|---|---|---|
| CircleCI | 🔴 0개 연결 | CircleCI 조직의 VCS Connections에서 GitHub App 관리자 1회 설치 + 저장소 선택 필요 | 사용자 승인 단계 필요 |
| Codacy | 🔴 0개 연결 | Git provider/저장소 연결이 선행되어야 함 | 사용자 승인 단계 필요 |
| BrowserStack | 🔴 0개 연결 | 실제 Playwright 외부 실행에는 BrowserStack username/access key를 GitHub Secrets에 등록해야 함 | 계정/비밀키 단계 필요 |

GitHub Actions 자체는 GitHub 내부 검증이며 제3자 독립 외부검증으로 계산하지 않는다.

---

# 6. 막힘 처리 규칙

`실제 원인 확인 → 현재 가능한 최소 수정 1회 → 실행/검증 → 계속 막히면 HOLD + blocker + 개선방법 + restart point 기록 → 즉시 다음 도구로 이동`

금지:
- 같은 저장소/같은 404 반복 검색
- 실행 증거 없이 PASS
- 상태판/문서만 고치고 기능 개선으로 계산
- 한 도구를 계속 붙잡아 전체 시간을 소모

---

# 7. 현재 restart point

이번 회차에서 `05/09` 배포증거 확인, `10/14/19/22` 현재 index 확인, 설치된 저장소 목록 끝까지 확인은 완료했으므로 반복하지 않는다.

**다음 우선 재개:**
1. 우선도구 중 새 근거가 없는 이메일/7/37은 반복검색하지 않는다.
2. 1번은 Chat/GitHub만으로 정확한 JS 오류 위치 특정이 계속 막히므로 HOLD 유지하되, 브라우저 콘솔/전체 파일 정적분석이 가능한 실행환경이 생기면 최우선 복귀한다.
3. 13번은 기존 실제 업로드 코드나 endpoint 근거가 새로 발견되는 경우 즉시 재개한다.
4. 6번은 승인 fixture/expected output 근거가 생기면 즉시 회귀검증으로 복귀한다.
5. 새 근거가 없으면 **14/19/22/10을 다시 보지 말고**, 남은 주요 업무창/과거 자산에서 `실제 실행파일명·run URL·승인 fixture·업로드 endpoint`처럼 blocker를 직접 해제할 수 있는 구체 근거를 찾는 단계로 이동한다.

이 파일은 새 상태판을 만들지 않고 계속 같은 파일을 덮어쓴다.