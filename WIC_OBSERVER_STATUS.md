# WIC OBSERVER STATUS

최종 갱신: 2026-08-11 09:17 KST
상태: ACTIVE
목적: 사용자가 링크 하나에서 실제 진행상태를 쉽게 확인하도록 하는 사람용 상태판. 운영 규칙 원본은 `WIC_GLOBAL_OPERATING_RULES.md` 하나만 사용한다.

## 한눈에 보기

- 전체 기능 완료율: **산정중(HOLD)** — 전체 등록 도구의 세부 작업단위 전수 수치화 전에는 임의 % 금지
- 제3자 외부검증 후보 공식 확인: **CircleCI / Codacy / BrowserStack 3개**
- 제3자 외부검증 실제 WIC 연결: **0개 / HOLD**
- 기존 GitHub 내부 검증: **PR / GitHub Actions / artifact / Pages 증거는 일부 존재**
- 중요: GitHub Actions 자체를 사용자가 요구한 `GitHub 밖 제3자 독립 외부검증`으로 계산하지 않는다.

## 이번 자동 재개 회차에서 실제 확인된 것

1. 최신 `WIC_OBSERVER_STATUS.md`와 restart point를 먼저 읽고 `03-coding_practice`부터 재개했다.
2. `03-coding_practice`는 public/main, size 26으로 저장소는 실제 존재한다. 그러나 실행자산 코드 검색 결과가 없고 `README.md`도 404여서 현재 실행파일을 특정하지 못했다. **HOLD / PASS 금지**.
3. `05-report-generator`는 public/main, size 12이며 현재 기본 브랜치에 실제 `index.html`이 존재한다. 파일 SHA는 `d8b2c472289245d46ad5faf9fba85825f8def4d9`이다.
4. 5번 `index.html`은 제목·키워드·요약을 받아 정해진 문구를 조합해 보고서를 만드는 브라우저 단독 모듈이고 `localStorage` 저장과 clipboard 복사를 사용한다. 외부 시장데이터/LLM/API 호출이나 독립검증 연결 근거는 파일에서 확인되지 않았다. 따라서 **실행 UI 자산 존재 / 실제 자동 보고서 엔진은 PARTIAL-HOLD**로 구분한다.
5. `09-contents-making-tool`은 public/main, size 20이며 현재 기본 브랜치에 실제 `index.html`이 존재한다. 현재 UI/코드 자산 존재는 확인했으나 이번 회차에는 외부 실행 성공 URL이나 독립검증 run 결과를 확보하지 못했으므로 **PARTIAL/HOLD**다.
6. `08-English-Verb-Exercise`는 public/main, size 12이며 현재 기본 브랜치에 실제 `index.html`이 존재한다. 화면 코드 자체에 `Local-only · Safe DOM · v1.0`, `저장: 브라우저 localStorage`, `서버 통신 · 타이머 없음`이 명시되어 있다. 따라서 로컬 연습도구로는 자산이 있으나 외부 실행/검증 구조는 **HOLD**다.
7. `11-obk-finance-planner`는 public/main, size 14로 저장소는 실제 존재하지만 현재 `index.html`은 404이고 finance/planner 관련 코드 검색 결과도 없어서 현재 실행자산을 특정하지 못했다. **HOLD / PASS 금지**.
8. 외부검증 연결 경로도 병행 확인했다. 현재 ChatGPT 설치 가능 플러그인 검색에서 `CircleCI / Codacy / BrowserStack` 결과가 0개여서 이 대화 환경 안에서 플러그인 1회 설치로 끝내는 경로는 확인되지 않았다. 따라서 실제 연결은 여전히 **0개 / HOLD**이며, 사용자 1회 승인으로 끝내려면 각 서비스의 GitHub App/OAuth 설치 링크를 별도 준비해야 한다.

## 우선 작업 상태

| 우선 | 대상 | 현재 상태 | 실제 확인/개선 | blocker | 다음 실행 |
|---|---|---|---|---|---|
| 1 | 이메일 수집 | HOLD | 전용 GitHub 실행 저장소 미확인 상태 유지 | 실행자산 위치 미확인 | 다른 근거가 생기면 재개 |
| 2 | 7번 고객 컨택 판단 | HOLD | `07-wic-setting-tool-v1`은 다른 목적이라 사용 금지 유지 | 올바른 실행판 미확인 | 다른 근거가 생기면 재개 |
| 3 | 1번 중간/최종 안내서 | HOLD | 최신 Deno deploy failure 확인됨 | JS 오류 위치 미특정, deploy failure | 새 근거가 생길 때만 재개 |
| 4 | 37 메타데이터 | HOLD | 전용 저장소 이름 검색에서 미확인 | 실행자산 미확인 | 다른 근거가 생기면 재개 |
| 5 | 13 엑셀 자동 업로드 | HOLD | 파일입력/매핑/미리보기/XLSX 생성 존재. 실제 업로드는 없음 | 외부 업로드 endpoint/API/브라우저 자동화 미연결 | 기존 실제 업로드 코드 근거 발견 시 재사용 |
| 6 | 6번 목차 정리 | PARTIAL/HOLD | 저장소 존재, golden fixture 1차 검색 완료 | 승인 fixture/expected output 미확인 | 새 승인 샘플 근거 발견 시 재개 |
| 7 | 2번 입찰 | HOLD | 실제 UI 코드와 최신 배포 상태 확인. localStorage 기반 수동 안건관리 화면임을 확정 | 나라장터 자동수집/API/로그인/투찰 엔진 미확인 + Deno deploy failure | 기존 실제 자동입찰 자산 근거 발견 시 재사용 |
| 8 | 28~31 | HOLD | 중앙 규칙/상태 + 조직 저장소를 근거 기반 재검색 | 실제 실행 저장소/파일 참조 미확인 | 다른 자료에서 구체 참조가 발견될 때만 재개 |
| 9 | 12번 서브웹사이트 빌더 | HOLD | 저장소 존재 + 실행자산 키워드 재확인 | 실행파일 위치 미특정 | 새 구체 파일명 근거가 생길 때만 재개 |
| 10 | 21번 Sales Route Planner | HOLD | 저장소 존재 확인 + 실행자산 검색 | 실행파일/엔진 위치 미특정 | 새 구체 파일명 근거가 생길 때만 재개 |
| 11 | 23번 World Advisor | HOLD | 저장소 존재 확인 + 실행자산 검색 | 실행파일/엔진 위치 미특정 | 새 구체 파일명 근거가 생길 때만 재개 |
| 12 | 24번 Easy Video Maker | HOLD | 저장소 존재 확인 | README/index 현재 404 | 과거 커밋 또는 구체 실행파일 참조 발견 시 재개 |
| 13 | 25번 Free Content Maker | HOLD | 저장소 존재 확인 | README/index 현재 404 | 과거 커밋 또는 구체 실행파일 참조 발견 시 재개 |
| 14 | 26번 Online Item Shop | HOLD | 저장소 존재 확인 | README/index 현재 404 | 과거 커밋 또는 구체 실행파일 참조 발견 시 재개 |
| 15 | 27번 Technical Book Verifier | PARTIAL/HOLD | 과거 `index.html` 실행 UI + 현재 중앙규칙 연결 파일 + 최근 커밋 이력 확인 | 현재 기본 브랜치 index 404, 현재 run/result URL 없음 | 구체 현재 실행자산 경로가 새로 발견될 때만 재개 |
| 16 | 04 Research Funding Generator | HOLD | 저장소 실제 존재 확인 | README/index 현재 404, 실행자산 위치 미특정 | 새 구체 파일명 근거가 생길 때만 재개 |
| 17 | 03 Coding Practice | HOLD | 저장소 실제 존재 확인 | 코드 검색 0 + README 404 | 새 구체 파일명 근거가 생길 때만 재개 |
| 18 | 05 Report Generator | PARTIAL/HOLD | 현재 `index.html` 실제 존재, localStorage/clipboard 기반 생성 UI 확인 | 고정 문구 조합형, 외부 데이터/LLM/API/검증 근거 없음 | 실제 요구 규칙 또는 기존 엔진 자산 근거 확인 후 기능화 |
| 19 | 09 Contents Making Tool | PARTIAL/HOLD | 현재 `index.html` 실제 존재 | 실행 성공 URL/외부검증 결과 없음 | 배포/실행 증거 확인 또는 기능 엔진 위치 확인 |
| 20 | 08 English Verb Exercise | PARTIAL/HOLD | 현재 `index.html` 실제 존재, Local-only/서버통신 없음 명시 | 로컬 브라우저 전용 | 로컬 도구로 유지하거나 외부검증 대상에서 제외 판단 |
| 21 | 11 OBK Finance Planner | HOLD | 저장소 실제 존재 확인 | index 404 + 코드검색 0 | 새 구체 파일명 근거가 생길 때만 재개 |

## 외부검증 도입 상태

- 외부 서비스 후보 조사: **완료된 부분 반복 금지**
- CircleCI 실제 WIC 연결: **0 / HOLD**
- Codacy 실제 WIC 연결: **0 / HOLD**
- BrowserStack 실제 WIC 연결: **0 / HOLD**
- 위 서비스가 실제 생성한 WIC run/status/log: **아직 없음**
- ChatGPT 설치 가능 플러그인 검색: **CircleCI/Codacy/BrowserStack 0개**
- 따라서 현재 가능한 다음 단계는 각 외부 서비스의 공식 GitHub App/OAuth 승인 링크를 준비해 사용자 1회 승인으로 연결하는 방식이다.
- GitHub Actions 기반 자체 정적검사는 제3자 외부독립검증으로 인정하지 않는다.

## 막힌 항목 처리 방식

`원인 확인 → 증거 기록 → 현재 가능한 최소 수정 1회 → 계속 막히면 HOLD + restart point → 즉시 다음 실행 가능한 항목으로 이동`

## 재개점

완료된 외부후보 조사, 이메일/7번 저장소 검색, 01 존재확인/오류 종류 확인, 13 업로드 버튼 실동작 확인, 6 golden fixture 1차 검색, 2번 현재 UI/배포 확인, 28~31 중앙/저장소 이름 검색, 12/21/23 일반 실행자산 검색, 24~26 README/index 확인, 27 과거 실행 UI/현재 규칙파일/최근 커밋 확인, 32/34 이름검색, 04 README/index 확인, 03 저장소/README/코드검색, 05 index 존재/기본동작 확인, 09 index 존재 확인, 08 index/Local-only 확인, 11 index/코드검색 확인은 반복하지 않는다.

**다음 즉시 재개 위치: `05-report-generator`와 `09-contents-making-tool`의 현재 배포/실행 증거가 이미 있는지 확인한다. 실행 URL/워크플로우 근거가 없으면 HOLD 유지 후 아직 상태표에 없는 등록 저장소/주요 업무창으로 이동한다. 외부검증은 CircleCI/Codacy/BrowserStack 중 한 곳의 사용자 1회 승인 링크를 만들 수 있는 공식 설치 경로 확인을 병행한다.**
- 과거 자산은 현재 자산과 구분한다.
- 현재 실행 성공 run/result URL 또는 동등한 증거가 없으면 완료/PASS 금지.
- 상태판은 새 파일을 늘리지 않고 이 파일 하나를 계속 덮어쓴다.