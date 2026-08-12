# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 13:58 KST
상태: ACTIVE / STRUCTURE_FIRST / PREWORK_LOCKED
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 0. 2026-08-13 Work 직전 최종 우선순위 LOCK
1. **WIC 전체 재사용 자동 통합 구조 + Chat 기반 실제 도구개발 코어**를 최우선으로 완성한다.
2. 구조가 실제 E2E PASS한 뒤 **6번 목차 정리 → 13번 엑셀 자동 업로드 → 7번 고객 컨택 판단 → 2번 입찰** 순으로 진행한다.
3. **이메일 수집, 1번, 37번은 이번 Work 개발 우선순위에서 제외**한다. 이메일 수집/37은 Chat 작업 중심으로 유지하고, 1번은 기능이 너무 복합적이므로 이번 크레딧으로 직접 완성하려 하지 않는다.
4. 2번까지 처리한 뒤 Work 크레딧이 남아도 **사용자 허락 없이 다른 도구·규칙·문서·껍데기 작업에 사용하지 않는다.** 반드시 다음 작업을 사용자에게 묻는다.
5. Work 크레딧은 구조 구현·실행·E2E·실제 도구 기능개발처럼 Chat/GitHub에서 막히는 구간에만 쓴다. 기존 규칙 재독해·재요약·저장소 재검색·새 규칙문서 생성에는 사용하지 않는다.

## 1. 13일 전 Chat+GitHub에서 미리 끝내야 할 준비 — Work 크레딧 절약
아래는 Work에서 다시 생각하거나 설계하지 않도록 13일 전에 최대한 확정/준비한다.

### A. 기존 자산 재사용 잠금
- 기존 `WIC_CHAT_ROUTING_REGISTRY.md`를 재사용하고 새 registry를 만들지 않는다.
- 기존 feedback ingest / routing / state / audit workflow / canonical writer를 재사용한다.
- 완료된 ingest, registry-source routing, conflict/dedup/revision/checkpoint/module-contract, canonical_writer를 재개발하지 않는다.
- 각 도구/대화창의 기존 코드·규칙·테스트·실패기록을 먼저 재사용한다.

### B. 자동 통합 코어 필수 범위
- 모든 주요 대화창/도구의 새 피드백·오류·규칙을 event 단위로 흡수.
- `공통마스터 → 업무군 → 분야/도구 예외 → 데이터/실행자산` 계층 자동 라우팅.
- 최신 사용자 지시 우선의 conflict/supersede/HOLD 판정.
- 중복 제거 및 같은 feedback_id 재처리 금지(idempotency).
- 전체 문서를 매번 다시 읽지 않는 증분 처리.
- canonical single-source write + 즉시 GitHub read-back + hash/내용 검증.
- target별 revision cache와 changed-scope 식별.
- 변경된 범위만 대상 도구에 적용.
- stage checkpoint / last_success_stage / restart point 저장.
- partial failure 시 마지막 성공 단계 다음부터 재개.
- 잘못된 변경 rollback.
- 어떤 피드백이 어느 canonical 규칙/도구 코드에 반영됐는지 추적 가능한 evidence 기록.
- 동일 오류 재발 시 회귀테스트로 승격.

### C. Chat 기반 실제 도구개발 코어 — Work 없이 이후 개발하기 위한 핵심 보완
목표는 구조 PASS 후 사용자가 Chat에서 기능 추가/수정을 말하면 Work를 기다리지 않고 GitHub에서 실제 기능개선이 계속되게 하는 것이다.

- 새 기능은 통합코어 본체를 다시 뜯어고치지 않고 도구별 module/adapter/plugin으로 추가·교체.
- 공통 기능모듈 최소 계약:
  - input schema
  - output schema
  - validation
  - apply hook
  - rollback hook
  - test fixture
  - evidence hook
- 대형 단일 HTML 전체 덮어쓰기 금지. 안전한 부분 patch 또는 모듈 교체 우선.
- 새 기능 추가 시 영향 범위만 테스트.
- 실패하면 기존 정상 버전으로 자동/안전 rollback 가능.
- 새 도구/대화창은 본체 확장 재개발이 아니라 registry 등록 + 공통 모듈 규격으로 연결.
- 완전히 새로운 데이터 유형/권한 방식만 adapter 수준에서 최소 확장.

### D. 구조가 나중에 다시 뜯어고쳐지지 않도록 추가 보완
- 등록만으로 새 도구가 붙는 범용 registry 구조.
- 변경 이력 및 rollback 가능한 version/revision 기록.
- 동일 피드백 중복 처리 방지.
- 실패 항목 HOLD queue 및 재시도 조건.
- 민감정보/Secret/계정권한을 코드·규칙과 분리.
- 도구별 adapter 규격 통일.
- 처리시간·오류율·실행증거 기록.
- 구조 자체 regression test.
- 외부검증과 내부검증 명확히 분리.
- 외부 서비스는 실제 run/result URL이 있을 때만 독립검증으로 인정.

## 2. 구조 PASS의 실제 완료조건
단순 스크립트/문서/commit 존재는 완료가 아니다.

### 실제 피드백 E2E 1건
`실제 새 피드백 → ingest → registry route → conflict/dedup → canonical GitHub write → commit SHA → read-back 검증 → target changed-scope 식별 → target 적용 → 실제 test/evidence → restart/rollback 기록`

위 전체 체인이 실제 증거와 함께 성공해야 한다.

### 실제 도구 기능변경 E2E 1건
`Chat 지시 → 기능 module/adapter 생성/교체 → GitHub 반영 → 대상 도구 적용 → 실제 테스트 → evidence → 실패 시 rollback 가능 확인`

시험 후보:
- 13번: `원본 칼럼 자동판별 → 자동매핑 → confidence → 애매한 칼럼 HOLD → 결과 검증`의 최소 모듈
- 또는 6번: 발행사별 parser/normalizer의 작은 규칙 1건

둘 중 실제 구현이 더 안전하고 빠른 것을 사용하되, 구조 자체를 특정 도구에 종속시키지 않는다.

## 3. Work가 60~80%에서 끝날 경우의 최소 성공선
100% 구조 PASS가 목표지만 크레딧이 먼저 끝나는 최악의 경우에도 아래 체인은 반드시 살아 있어야 한다.

`Chat 피드백 → registry route → conflict/dedup → GitHub canonical write/read-back → 대상 changed-scope 식별 → 안전한 코드수정 진입`

이 체인이 살아 있으면 이후 Work 없이 Chat+GitHub에서 6/13/7/2의 실제 개발을 계속할 수 있어야 한다.
자동테스트/rollback/외부독립검증 일부가 남더라도 다음 Work까지 아무것도 못 하는 구조는 실패로 본다.

## 4. 구조 PASS 후 Work 개발 우선순위
### 1순위: 6번 목차 정리
- 목표: 이번 Work에서 실사용 개발완료를 우선적으로 닫는다.
- 모든 발행사 규칙을 누적 적용할 수 있는 parser/normalizer 구조.
- 승인 golden fixture 기반 실제 입력→결과 비교.
- 안내서에 넣을 수 있는 충분한 목차 출력 형식.
- 여러 건 배치 처리 및 속도 측정. 3~5개를 짧은 시간에 처리할 수 있는 결정형 경로 우선.
- 같은 오류는 regression fixture로 승격.
- 단순 STRUCTURE_PASS가 아니라 실제 업무 결과 검증까지 완료해야 PASS.

### 2순위: 13번 엑셀 자동 업로드
- 원본 파일을 넣으면 원본 칼럼명과 값 형태를 자동 분석.
- 홈페이지 업로드 양식 칼럼으로 자동 매핑.
- 발행사별/기존 매핑 규칙 재사용.
- confidence 기반 자동판정.
- 확실한 칼럼은 자동매핑, 애매한 칼럼은 억지 추정하지 않고 HOLD.
- 매핑 결과 미리보기/검증.
- 잘못된 매핑 재발방지 규칙 누적.
- 실제 홈페이지 uploader/backend/API가 존재하는 범위까지 연결하되, 존재하지 않는 기능을 만들어진 것으로 가장하지 않는다.
- 37번 결과 파일은 13번 자동매핑 검증 샘플로 재사용 가능하지만 37번 자체를 Work 개발 대상으로 만들지 않는다.

### 3순위: 7번 고객 컨택 판단
- 현재 Chat에서 가능한 판단을 결정형/반결정형 도구로 전환.
- 실제 고객 원자료/회사/부서/업무/과거 이력을 입력.
- PASS/HOLD/FAIL, 지금 할 행동, 전화/메일/후속분기, 추천자료까지 업무 기준에 맞게 출력.
- 없는 사실/링크/업무를 지어내지 않는 fail-closed.
- 실제 고객 사례로 E2E 검증.
- 채팅판단보다 빠르고 반복 가능하게 만드는 것이 목표.

### 4순위: 2번 입찰 도구
- 마지막 우선순위.
- 현재 localStorage UI를 실도구로 오인하지 않는다.
- 실제 나라장터 조회/수집/판정/로그인/제출 중 기존 자산이 있는 범위를 우선 재사용.
- 외부 로그인·사용자 승인 필요 구간은 최소 클릭 승인 queue로 분리.
- 실제 실행증거 없는 기능은 HOLD.

## 5. 이번 Work 우선순위에서 제외
- 이메일 수집: Chat 작업으로 충분하며 피드백은 자동 통합구조가 GitHub에 즉시 흡수하도록 한다.
- 1번 고객 자동화 안내서: 여러 기능이 결합된 대형 도구라 이번 한정 크레딧으로 직접 완성하려 하지 않는다. 향후 6번 등 완성된 전문도구를 조립/호출하는 modular architecture로 단축한다.
- 37번 메타데이터 생산: 현재 Chat 중심 생산업무로 유지. 13번 테스트 데이터로만 재사용 가능.
- 28~31 및 나머지 도구: 2번까지 끝난 뒤 크레딧이 남아도 사용자 허락 전에는 Work로 진행 금지.

## 6. 1번 같은 복합도구를 향후 빨리 완성하기 위한 기반
- 1번 내부에 모든 기능을 다시 구현하지 않는다.
- 6번 목차, 7번 판단, 추천/검증 등 완성된 전문모듈을 호출·조립하는 orchestrator 구조로 전환.
- 기능별 독립 module + 공통 contract + 독립 test fixture.
- 한 기능 실패가 전체 도구를 깨지 않도록 fail-closed/HOLD.
- 기능별 revision/rollback.
- 이 기반은 이번 구조 1순위의 Chat 기반 실제 도구개발 코어에 포함한다.

## 7. 현재 실제 확보된 구조 증거
- 기존 `WIC_CHAT_ROUTING_REGISTRY.md` machine-readable route map 존재.
- feedback ingest가 registry를 직접 읽어 routing.
- registry 오류 시 silent fallback 없이 error.
- GitHub Actions feedback audit 성공 기록 존재.
- conflict/dedup/revision/checkpoint/module-contract 기반 코드 존재.
- `feedback_pipeline/canonical_writer.py` 추가 완료.
- canonical preserve/replace/idempotency/hash fixture 코드 read-back 완료.
- 아직 실제 GitHub canonical write transport → target apply/test → rollback 전체 E2E는 HOLD.

## 8. 13일 Work 시작 restart point
1. 기존 ingest/registry/conflict/canonical_writer를 다시 만들지 않는다.
2. 실제 GitHub canonical write transport 연결.
3. 실제 새 피드백 1건 canonical write → commit SHA → read-back hash 검증.
4. target revision cache 영속화.
5. changed-scope target apply 연결.
6. 실제 target test/evidence recorder 연결.
7. checkpoint/restart/rollback 실제 run 검증.
8. 실제 도구 기능변경 module/adapter E2E 1건 검증.
9. 구조 PASS 후 6 → 13 → 7 → 2.
10. 이후 크레딧이 남으면 멈추고 사용자에게 다음 작업을 묻는다.

## 9. 절대 금지
- 새 규칙문서/새 registry를 반복 생성.
- Work에서 기존 규칙을 처음부터 다시 읽고 재요약.
- 이미 완료된 앞단 재개발.
- 저장소/commit 존재만으로 완료 판정.
- GitHub 내부검증을 제3자 독립검증으로 표현.
- 사용자의 허락 없이 남은 Work 크레딧을 다른 도구/규칙 작업에 사용.
- 도구별 새 기능마다 통합코어를 다시 뜯어고침.
- 실제 기능개선 없이 상태판/규칙/껍데기만 늘리는 작업.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.