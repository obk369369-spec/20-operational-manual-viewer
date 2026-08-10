# WIC OBSERVER STATUS

최종 갱신: 2026-08-10 23:57 KST
상태: ACTIVE
목적: 사용자가 링크 하나에서 실제 진행상태를 쉽게 확인하도록 하는 사람용 상태판. 운영 규칙 원본은 `WIC_GLOBAL_OPERATING_RULES.md` 하나만 사용한다.

## 한눈에 보기

- 전체 기능 완료율: **산정중(HOLD)** — 전체 등록 도구의 세부 작업단위 전수 수치화가 끝나지 않아 임의 % 금지
- 외부검증 후보 공식 확인: **3개 확인 완료**
- 외부검증 실제 연결: **0개 / HOLD**
- 제가 만든 자체 외부검증 구조: **사용 금지**
- 별도 assistant 설계 문서 `WIC_EXTERNAL_VERIFICATION_ROLLOUT_2026-08-13.md`: **삭제 완료**
- 자동 재개: ChatGPT 자동화가 **매시간 활성화됨**. 단, GitHub 자체가 멈춤을 즉시 감지하는 엔진은 아님.

## 이번 회차에서 실제로 바뀐 것

1. assistant가 만든 외부검증 rollout 문서를 GitHub에서 삭제함. 삭제 commit: `4c4fa0a32648fc3192b48ebffffa07f02a9daac7`.
2. 이미 존재하는 외부 서비스만 독립 외부구조 후보로 인정하도록 변경.
3. 공식 문서로 CircleCI / Codacy / BrowserStack의 GitHub 연동·외부 실행/검증 기능을 확인함.
4. ChatGPT Plugin 검색에서 CircleCI·Codacy·BrowserStack 직접 커넥터가 발견되지 않음. 실제 서비스 연결은 HOLD.
5. GitHub에서 이메일 수집 전용 저장소/실행코드를 `EMAIL_COLLECTION`, `이메일 수집`, 고정 규칙 파일명으로 검색했으나 전용 실행 저장소를 확인하지 못함. 같은 검색 반복 금지.
6. 7번 관련 저장소를 재확인한 결과 `obk369369-spec/07-wic-setting-tool-v1`만 확인되며, 이는 최신 7번 `고객 컨택 판단` 목적과 불일치하는 저장소임. 7번 실행판으로 재사용 금지.

## 외부에서 가져올 검증 구조 — 공식 근거

| 외부 서비스 | 외부에서 실제로 하는 일 | WIC 적용 후보 | 실제 연결 상태 | 공식 근거 |
|---|---|---|---|---|
| CircleCI | GitHub 저장소 코드를 CircleCI Cloud에서 별도 실행하고 workflow status를 GitHub Checks로 되돌려줌 | 공통 실행/테스트 게이트 1순위 | HOLD — 계정/관리자 설치·연결 필요 | https://circleci.com/docs/guides/integration/enable-checks/ |
| Codacy | GitHub PR를 외부에서 정적 분석하고 quality gate/status check/분석 로그를 제공 | 코드 품질·보안·복잡도·중복·coverage 보조검증 | HOLD — Codacy GitHub App 연결 필요 | https://docs.codacy.com/repositories-configure/integrations/github-integration/ |
| BrowserStack | BrowserStack 외부 브라우저/디바이스 클라우드에서 Playwright 테스트 실행 | 화면/브라우저 기반 도구의 실제 UI/E2E 검증 | HOLD — BrowserStack 계정 key/연결 필요 | https://www.browserstack.com/docs/automate/playwright/github-actions |

### 중요한 제한
- CircleCI와 BrowserStack은 실행 환경을 외부로 분리하지만 WIC 업무 결과의 의미가 맞는지까지 자동으로 아는 것은 아님.
- Codacy는 코드 품질/정적 문제에는 강하지만 고객 추천이 맞는지 같은 업무 의미 검증기는 아님.
- 외부서비스가 실제로 연결되기 전에는 `외부검증 완료` 또는 기능 PASS로 올리지 않는다.

## 우선 작업 상태

| 우선 | 대상 | 현재 상태 | 실제 확인/개선 | 아직 안 된 부분 | blocker | 다음 실행 |
|---|---|---|---|---|---|---|
| 1 | 이메일 수집 | HOLD | GitHub 전용 실행 저장소 검색 완료 | 실제 신규건 E2E + 실행코드 위치 | 전용 실행 저장소 미확인 | Files/중앙 규칙에서 실행자산 위치 확인 후 없으면 다음 항목 |
| 2 | 7번 고객 컨택 판단 | HOLD | `07-wic-setting-tool-v1`이 다른 목적임을 재확인 | 올바른 실행판/E2E | 전용 실행 저장소 미확인 | 중앙/Files에서 실제 실행자산 확인 후 없으면 다음 항목 |
| 3 | 1번 중간/최종 안내서 | HOLD | 기존 규칙·자료 위치 추적 기록 존재 | 실제 안내서 생성→검증→결과 증거 | 실행판/외부검증 미확정 | **다음 즉시 작업: 01 저장소 실제 실행파일·샘플·테스트 상태 확인** |
| 4 | 37 메타데이터 | PARTIAL/HOLD | 규칙 존재 | 실제 생산 E2E 증거 | 원본→결과 실행 증거 부족 | 실제 샘플/실행 경로 확인 |
| 5 | 13 엑셀 자동 업로드 | HOLD | 과거 코드/기록 존재 | 실제 업로드 성공 증거 | 실제 업로드 대상 환경 미연결 | 현재 GitHub 실행코드 위치 확인 |
| 6 | 6번 목차 정리 | PARTIAL/HOLD | 기존 안정본·규칙 기록 존재 | 실제 정답세트 회귀검증 + 외부 실행 | 외부검증 미연결 | 샘플 원문→결과 실행 경로 확인 |
| 7 | 2번 입찰 | HOLD | 우선순위 등록 | 현재 실행판·증거 재확인 | 미조사 | GitHub/Files 상태 조사 |
| 8 | 28~31 | HOLD | 역할 분리 기록 | 자동화·외부검증 적용 | 미조사 | 각 저장소/대화 근거 흡수 |

## 막힌 항목 처리 방식

`원인 확인 → blocker 기록 → 개선방법 기록 → 현재 가능한 1회 시도 → 계속 막히면 HOLD + restart point → 즉시 다음 실행 가능한 항목으로 이동`

## 외부검증 도입의 현재 정확한 상태

- 공식 외부 서비스 조사: **진행됨**
- 외부 서비스 3개 기능 근거 확인: **완료**
- assistant 자체 설계 rollout 문서 제거: **완료**
- WIC GitHub 저장소에 CircleCI 실제 연결: **아직 안 됨 / HOLD**
- Codacy 실제 연결: **아직 안 됨 / HOLD**
- BrowserStack 실제 연결: **아직 안 됨 / HOLD**
- 외부 서비스가 낸 실제 WIC run/status/log: **아직 없음**

## 재개점

완료된 외부후보 조사와 이메일/7번 GitHub 검색은 반복하지 않는다.

**다음 즉시 재개 위치: `01-auto-guide-v1` 실제 실행파일·샘플·테스트/Actions 상태 확인.**
그 다음 37 → 13 → 6 → 2 → 28~31 순서로 수정 가능한 부분부터 계속 진행한다.

이 상태판은 새 파일을 늘리지 않고 동일 파일을 계속 덮어쓴다.
