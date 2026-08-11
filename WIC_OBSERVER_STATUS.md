# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 01:18 KST
상태: ACTIVE
목적: 각 WIC 도구·업무·주요 대화창의 실제 진행, 증거, blocker, 다음 작업을 한 파일에서 직관적으로 확인한다.
운영 규칙 원본: `WIC_GLOBAL_OPERATING_RULES.md`
고객업무 공통 원본: `CUSTOMER_WORKFLOW_MASTER.md`

---

# 1. 지금 한눈에 보기

- 제3자 독립검증 실제 run 증거: **0개 / HOLD**
- 현재 확정 PASS 도구: **없음**
- 표시 방식: **완료율을 임의로 만들지 않고 `운영준비도 평가치 0~100`을 사용**한다.
- 평가 기준: `정체성·규칙 20 + 실제 입력/자산 20 + 기능/업무흐름 구현 20 + 현재 실행/출력 증거 20 + 독립검증·실업무 PASS 20`.
- 따라서 예를 들어 60점은 “60% 완성”을 뜻하지 않고, **5개 준비단계 중 증거가 있는 3단계 수준**이라는 뜻이다.
- 원칙: 완료작업 반복 금지 → blocker는 HOLD 기록 → 즉시 다음 실행 가능 항목으로 이동 → 새 근거가 생기면 우선도구로 복귀.
- 6번 새 근거: commit별 GitHub 내부 검증 산출물 `static-validation.json`을 external-evidence-archive에서 실제 read-back함. 6번 현재 실행/출력 증거 20점 인정, 60→80/100. 독립검증 점수는 0점 유지.
- **2026-08-13 Work 1순위 변경:** 개별 도구보다 먼저 모든 도구·대화창이 계속 재사용하는 **WIC 전체 자동 통합 기반 구조 자체**를 구현한다. 단순 문서/스크립트 존재는 PASS가 아니다.

상태: 🟢 PASS = 실제 입력→실행→출력→검증 / 🟠 PARTIAL-HOLD = 실제 개선·실행 근거 있으나 E2E/독립검증 미완료 / 🔴 HOLD = blocker / ⚪ NEXT = 다음 실행 대상

---

# 2. 도구별 운영준비도 — 전체 100 기준

| 우선 | 도구/업무 | 준비도 | 직관적 상태 | 점수를 받은 근거 | 아직 못 받은 핵심 20점 단위 |
|---|---|---:|---|---|---|
| 1 | 이메일 수집 | **60/100** | 🟠 PARTIAL-HOLD | 공통 규칙·검증기준 + 중앙마스터 + 실제 업무흐름 존재 | 실제 자동수집 실행자산/현재 run **20**, 독립검증·office-ready E2E **20** |
| 2 | 7번 고객 컨택 판단 | **40/100** | 🟠 PARTIAL-HOLD | 역할/규칙 + 중앙마스터 참조 확인 | 올바른 실제 실행판 **20**, 고객 입력→판정 실행증거 **20**, 독립검증 **20** |
| 3 | 1번 중간/최종 안내서 | **60/100** | 🟠 PARTIAL-HOLD | 규칙 + 실제 HTML 자산 + 기능흐름/오류지점/CircleCI gate 존재 | 현재 정상 실행·배포 **20**, 외부 actual run + 실데이터 E2E **20** |
| 4 | 37번 메타데이터 | **40/100** | 🔴 HOLD | 생산 규칙·칼럼 규칙 존재 | 실제 생산 실행자산 **20**, 현재 원본→결과 run **20**, 독립검증 PASS **20** |
| 5 | 13번 엑셀 자동 업로드 | **60/100** | 🟠 PARTIAL-HOLD | 규칙 + 실제 UI/파일처리/XLSX·CSV 생성 흐름 존재 | 실제 홈페이지 uploader/backend 실행 **20**, 독립검증/실업로드 성공 **20** |
| 6 | 6번 목차 정리 | **80/100** | 🟠 PARTIAL-HOLD | 실제 저장소/엔진 + 규칙 + 내부 검증 workflow + commit `0b307cc9...`의 실제 `static-validation.json` read-back (`STRUCTURE_PASS`) | 승인 golden fixture/업무 기대값 비교 및 제3자 독립검증·실업무 PASS **20** |
| 7 | 2번 입찰 | **40/100** | 🔴 HOLD | 규칙/목표 + 실제 UI 자산 확인 | 나라장터 실연동 기능 **20**, 실제 제출/조회 실행 **20**, 독립검증 **20** |
| 8 | 28~31 발행사 업무 | **40/100** | 🔴 HOLD | 역할분리·업무규칙 존재 | 실제 실행자산 **20**, 현재 자동 실행 **20**, 검증 PASS **20** |
| - | 09 컨텐츠 자료 안내 | **60/100** | 🟠 PARTIAL-HOLD | 실제 index + synthetic blocker 특정 + 내부 gate/workflow_dispatch | production synthetic 제거 후 정상 run **20**, 독립검증 **20** |
| - | 05 Report Generator | **60/100** | 🟠 PARTIAL-HOLD | 실제 index + 생성 UI + synthetic 문구 제거 commit/read-back | 실제 업무규칙 E2E run **20**, 외부검증 **20** |
| - | 08 English Verb Exercise | **60/100** | 🟠 PARTIAL-HOLD | 실제 local-only index/기능 존재 | 현재 실행증거의 정식 보존 **20**, 필요한 경우 검증 PASS **20** |
| - | 27 Technical Book Verifier | **40/100** | 🟠 PARTIAL-HOLD | 규칙 + 과거 실행 UI 확인 | 현재 실행판 복구 **20**, 현재 run **20**, 검증 **20** |
| - | 03 Coding Practice | **20/100** | 🔴 HOLD | 저장소 정체성만 확인 | 실제 자산/기능/실행/검증 각 미확인 |
| - | 04 Research Funding Generator | **20/100** | 🔴 HOLD | 저장소 정체성만 확인 | 실제 자산/기능/실행/검증 각 미확인 |
| - | 10 Finance Dashboard | **20/100** | 🔴 HOLD | 저장소 정체성만 확인 | 실행자산 이후 단계 미확인 |
| - | 11 OBK Finance Planner | **20/100** | 🔴 HOLD | 저장소 정체성만 확인 | 실행자산 이후 단계 미확인 |
| - | 12 서브웹사이트 빌더 | **20/100** | 🔴 HOLD | 저장소 정체성 확인 | 실행파일 이후 단계 미확인 |
| - | 14 홈페이지 편집 | **20/100** | 🔴 HOLD | 저장소 정체성 확인 | 실행파일 이후 단계 미확인 |
| - | 19 사업홍보 | **20/100** | 🔴 HOLD | 저장소 정체성 확인 | 실행파일 이후 단계 미확인 |
| - | 21 Sales Route Planner | **20/100** | 🔴 HOLD | 저장소 정체성 확인 | 실행엔진 이후 단계 미확인 |
| - | 23 World Advisor | **20/100** | 🔴 HOLD | 저장소 정체성 확인 | 실행엔진 이후 단계 미확인 |
| - | 24 Easy Video Maker | **20/100** | 🔴 HOLD | 저장소 정체성 확인 | README/index/실행/검증 미확인 |
| - | 25 Free Content Maker | **20/100** | 🔴 HOLD | 저장소 정체성 확인 | README/index/실행/검증 미확인 |
| - | 26 Online Item Shop | **20/100** | 🔴 HOLD | 저장소 정체성 확인 | README/index/실행/검증 미확인 |

> 주의: 위 숫자는 **증거 기반 운영준비도**이며 “코드가 몇 % 작성됐다”는 의미가 아니다. 실제 실행·검증 증거가 생겨야 마지막 점수가 올라간다.

---

# 3. 41계열 주요 대화창 운영준비도 — 전체 100 기준

대화창은 도구와 조금 다르게 `대화창 이름/역할 고정 20 + 분야별 규칙·과거업무 축적 20 + 중앙 공통마스터 연결 20 + 현재 send-ready 데이터/실업무 출력 20 + 자동 실행·독립검증/office-ready 20`으로 평가한다.

| 새 번호 | 실제 대화창 이름 | 현재 준비도 | 현재 판단 | 다음 핵심 |
|---|---|---:|---|---|
| **41** | 이메일 수집 (방산) | **60/100** | 이름/역할·분야 규칙·공통 이메일수집 마스터 축은 확보 | 현재 인력 DB 실행자산/자동수집 run + 검증 연결 |
| **41-1** | 고객 안내 (방산) | **60/100** | 이름/역할·방산 안내 규칙·고객안내 공통축 존재 | 현재 고객 1건 end-to-end 안내 생성/검증 |
| **41-2** | 이메일 수집 (이차전지) | **60/100** | 분야별 수집 규칙·공통마스터 적용 가능 | 현재 send-ready DB 실행/검증 |
| **41-3** | 이메일 수집 (섬유) | **60/100** | 분야별 수집 규칙·공통마스터 적용 가능 | 현재 send-ready DB 실행/검증 |
| **41-4** | 이메일 수집 (원자력) | **60/100** | 분야별 수집 규칙·공통마스터 적용 가능 | 현재 send-ready DB 실행/검증 |
| **41-5** | 이메일 수집 (태양광) | **60/100** | 분야별 수집 규칙·공통마스터 적용 가능 | 현재 send-ready DB 실행/검증 |
| **41-6** | 이메일 수집 (바이오) | **60/100** | 분야별 수집 규칙·공통마스터 적용 가능 | 현재 send-ready DB 실행/검증 |
| **41-7** | 이메일 수집 (로봇) | **40/100** | 이름/역할은 확정, 이메일수집 공통규칙 적용 대상 | 로봇 분야 기존 데이터/규칙 흡수 확인 + 실행 DB 연결 |
| **41-8** | 고객 안내 (반도체) | **60/100** | 반도체 안내 규칙·고객안내 공통축 존재 | 현재 고객 1건 end-to-end 안내 생성/검증 |
| **41-9** | 이메일 수집 (탄소) | **60/100** | 분야별 수집 규칙·공통마스터 적용 가능 | 현재 send-ready DB 실행/검증 |
| **41-10** | 이메일 수집 (인공지능) | **60/100** | 분야별 수집 규칙·공통마스터 적용 가능 | 현재 send-ready DB 실행/검증 |
| **41-11** | 이메일 수집 (풍력) | **60/100** | 분야별 수집 규칙·공통마스터 적용 가능 | 현재 send-ready DB 실행/검증 |
| **41-12** | 이메일 수집 (조선) | **60/100** | 분야별 수집 규칙·공통마스터 적용 가능 | 현재 send-ready DB 실행/검증 |
| **41-13** | 고객 안내 (탄소) | **60/100** | 탄소 안내 규칙·추천자료 오류교정 축적 + 공통축 존재 | 실제 최신 고객건 E2E/중복방지 검증 |
| **41-14** | 고객 안내 (조선) | **60/100** | 조선 안내 규칙·발송구조 축적 + 공통축 존재 | 실제 최신 고객건 E2E/추천검증 |
| **41-15** | 고객 안내 (인공지능) | **60/100** | AI 안내 규칙·추천 정밀화 축적 + 공통축 존재 | 실제 최신 고객건 E2E/추천검증 |

### 대화창 번호 처리 원칙
- 위 표는 사용자가 지정한 **임시 새 번호를 그대로 사용**한다.
- 실제 대화창 이름은 임의 변경하지 않는다.
- 이름/번호/역할을 새로 발명하지 않는다.
- 통합이 실제 완료되기 전에는 기존 대화창을 삭제·병합 완료로 표시하지 않는다.
- 각 창의 고유 규칙·오류·데이터가 중앙마스터에 흡수되고 read-back된 뒤에만 통합 준비도가 올라간다.

---

# 4. 외부검증 도입 — 2026-08-13 마감 병행

| 구조 | 준비도 | 현재 상태 | 실제 증거 | 다음 필요한 것 |
|---|---:|---|---|---|
| CircleCI | **60/100** | GitHub OAuth 연결 + 1번 config/gate 존재 | OAuth 연결 화면 확인, config commit/read-back | 실제 Project 활성화 + 최초 external run/result URL **20**, WIC E2E PASS **20** |
| GitHub Actions / 6번 | **내부 증거 확인** | 실제 push 기반 결과 archive 존재 | `external-evidence-archive/runs/0b307cc9.../static-validation.json`, result=`STRUCTURE_PASS` | 제3자 독립검증으로 계산 금지; 승인 golden fixture 또는 실제 업무 기대값 비교 필요 |
| Codacy | **20/100** | 후보 선정만 완료 | 공식 기능 확인 | GitHub App 승인/연결 → 실제 분석 result |
| BrowserStack | **20/100** | 후보 선정만 완료 | 공식 기능 확인 | 계정/연결 승인 → UI E2E actual run |

제3자 서비스의 실제 run/result URL이 없으면 독립검증 점수를 주지 않는다. GitHub Actions/Deno/assistant 판단은 제3자 독립검증으로 계산하지 않는다.

---

# 5. 이번 회차 실제 수행 / 개선 / blocker

1. 중앙 `WIC_OBSERVER_STATUS.md`를 먼저 read-back하고 최신 restart point를 확인했다.
2. 완료된 6번 `static-validation.json` read-back, 1번 `defaultToc` blocker, 37/13 실행자산 검색을 반복하지 않았다.
3. 2026-08-13 Work의 최우선 대상을 **개별 도구가 아니라 WIC 전체 자동 통합 기반 구조 자체**로 고정했다.
4. 구조 구현 전에 재분석 낭비를 없애기 위해 공통 파이프라인을 `SOURCE EVENT → NORMALIZE → ROUTE → CONFLICT/DEDUP → CANONICAL WRITE → READ-BACK → TARGET READ/APPLY → TEST/EVIDENCE → RESTART POINT`로 준비했다.
5. 계층은 `GLOBAL → WORKGROUP → TOOL/DOMAIN OVERRIDE → DATA/EXECUTION ASSET`으로 고정한다. 새 도구/대화창은 본체를 복제하지 않고 등록만 하는 방식으로 설계한다.
6. 구조 PASS 게이트는 실제 새 피드백 1건 이상을 넣어 `수신 → 정규화 → 자동 라우팅 → 충돌/중복 판정 → GitHub canonical commit → read-back → 대상 도구 새 revision read/apply → 테스트/실행 증거 → 실패 시 HOLD/restart`까지 모두 성공해야 한다.
7. 새 구조/registry 별도 파일을 GitHub에 만들려 했으나 현재 connector의 create_file 쓰기가 안전검사에서 차단됐다. **새 파일 생성 성공으로 기록하지 않는다.** 반복 시도하지 않고 기존 `WIC_OBSERVER_STATUS.md`에 준비사항을 저장했다.

---

# 6. 지금 가장 큰 병목

1. **기능 수정 → 실제 실행 → 실제 출력 → 기대값 비교 → PASS** 폐쇄루프가 핵심 도구에서 아직 완성되지 않았다.
2. CircleCI는 OAuth까지 연결됐지만 **실제 WIC Project/run URL이 아직 없다.**
3. 1번은 synthetic 생성과 Deno failure가 남아 있다.
4. 13번은 실제 홈페이지 업로드 엔진이 없다.
5. 6번은 현재 구조 실행 증거는 확보했지만, **승인 golden fixture/실업무 기대값 비교와 제3자 독립검증**이 남아 있다.
6. 이메일 수집/7/37은 중앙 규칙은 올라왔지만 실제 실행판 연결이 부족하다.
7. 자동 통합 구조의 실제 구현은 아직 시작 전이다. 현재는 Work가 재분석 없이 바로 구현하도록 구조·계층·PASS 게이트를 준비한 상태다.

---

# 7. 자동 이동 규칙

`우선도구 재시도 → 실제 개선 가능하면 계속 → 현재 환경에서 더 이상 진전이 없으면 blocker·개선방법·재개조건 기록 → HOLD → 즉시 다음 도구 → 다른 도구 처리 후 새 근거/외부승인이 생기면 우선도구로 복귀`

금지:
- 같은 404/같은 검색 반복
- 한 도구를 무한정 붙잡기
- 파일/commit 존재만으로 완료율 상승
- 상태판만 고치고 기능진전으로 계산
- 실행/검증 증거 없이 마지막 점수 부여

---

# 8. 2026-08-13 Work 1순위 — 재사용 자동 통합 구조

## 고정 목표
한 번 구현한 뒤 어떤 도구·대화창에서도 같은 구조를 계속 사용한다. 새 대상 때문에 통합 엔진을 복제하거나 전체 규칙을 다시 읽지 않는다.

## Core pipeline
`EVENT → NORMALIZE → ROUTE → CONFLICT/DEDUP → CANONICAL WRITE → READ-BACK → TARGET REVISION READ/APPLY → TEST/EVIDENCE → RESTART/HOLD`

## 고정 계층
1. GLOBAL: WIC 전체 공통
2. WORKGROUP: 이메일수집/고객안내/메타데이터/업로드/목차/입찰/발행사 등 업무군
3. TOOL_OR_DOMAIN_OVERRIDE: 특정 도구·산업·대화창 예외
4. DATA_OR_EXECUTION_ASSET: 원자료·코드·실행자산·결과

## 재사용 규칙
- 새 도구/대화창은 registry 등록만 한다.
- 새로운 입력 형식만 adapter로 추가한다.
- 기존 계층으로 표현 가능한 새 업무는 core 변경 금지.
- 도구는 마지막 적용 canonical revision을 저장하고, revision이 같으면 전체 재분석을 건너뛴다.
- revision이 바뀌면 영향받는 scope만 다시 적용한다.
- 동일 의미 규칙은 병합, 최신 명시 지시는 supersede/deprecated, 동일 우선순위 충돌은 HOLD_CONFLICT.
- core 변경 시 등록 대상 전체 회귀테스트가 필요하다.

## 구조 자체 PASS 조건
문서/코드 존재만으로 PASS 금지. 실제 새 피드백 1건을 투입해 다음 증거가 모두 있어야 한다.
1. event 수신
2. normalize 결과
3. 자동 route 결과
4. conflict/dedup 판정
5. canonical GitHub commit
6. canonical read-back
7. 대상 도구가 새 revision read/apply
8. 실제 test/run 결과
9. result URL/file/artifact 등 증거
10. 실패 시 HOLD + blocker + restart point

## 구조 PASS 후 도구 우선순위
`이메일 수집 → 7번 고객 컨택 → 1번 중간/최종 안내서 → 37 메타데이터 → 13 업로드 → 6 목차 → 2 입찰 → 28~31 → 나머지 등록 도구/주요 업무창`

---

# 9. 현재 restart point

- **자동 통합 구조:** 2026-08-13 Work 첫 작업. 현재는 core pipeline/계층/재사용 규칙/PASS 게이트 준비 완료, 구현은 아직 미실행. Work에서는 기존 규칙 재독해·재요약·저장소 재검색에 크레딧을 쓰지 말고 registry/normalizer/router/conflict-dedup/canonical writer/revision cache/test-evidence recorder 구현부터 시작한다. 실제 피드백 1건 E2E 전 PASS 금지.
- **이메일 수집 / 7번:** 구조 PASS 후 첫 연결 대상. 새로운 실행 저장소·스크립트·DB·브라우저 자산 근거가 생기면 복귀.
- **01:** production `defaultToc` fallback이 실제 남아 있음. 안전한 부분 patch/checkout 경로를 확보해 synthetic 생성부 제거 → Deno 정상화 → CircleCI actual run.
- **37:** 기존 생산 실행자산 식별 시 즉시 원본→결과 E2E.
- **13:** 실제 uploader/backend/worldic endpoint/API 식별 시 연결.
- **06:** commit `0b307cc9...`의 `STRUCTURE_PASS` archive read-back은 완료. 같은 run 확인 반복 금지. 다음은 승인 golden fixture/실업무 기대값과 실제 결과 비교 또는 제3자 검증 actual URL 확보 시 재개.
- **02 / 28~31:** 새 실제 엔진 근거 없으면 반복하지 않고 다음 도구로 이동.
- **09:** 안전 부분 patch 경로 확보 시 `createInitialSampleData()` 제거 → 빈 상태 fail-closed → actual run.
- **대화창:** 41~41-15 각 창의 고유 규칙/데이터 흡수 증거를 순차 확인하고, 이미 중앙화된 공통규칙은 반복 추출하지 않는다.
- **외부검증:** CircleCI 실제 Project/run URL 확보가 1순위. 제3자 서비스 결과 URL이 있을 때만 독립검증으로 인정한다.

이 파일은 앞으로도 새 파일을 만들지 않고 같은 `WIC_OBSERVER_STATUS.md`를 덮어쓴다.
