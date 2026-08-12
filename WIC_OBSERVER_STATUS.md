# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 11:31 KST
상태: ACTIVE / STRUCTURE_FIRST / PREWORK_LOCKED
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 현재 결론
- 2026-08-13 Work 1순위는 개별 도구가 아니라 **WIC 전체 재사용 자동 통합 구조 + Chat 기반 실제 도구개발 코어**의 실제 구현과 E2E 검증이다.
- 목표는 단순 규칙 통합이 아니라 **이후 Work 없이도 Chat+GitHub에서 도구 기능을 추가·교체·수정·검증할 수 있는 공통 개발 기반**을 확보하는 것이다.
- 새 registry는 만들지 않는다. 기존 `WIC_CHAT_ROUTING_REGISTRY.md`를 재사용한다.
- 실제 새 피드백 1건과 실제 도구 기능변경 1건이 전체 체인을 통과하기 전 구조 PASS 금지.
- 구조 PASS 후 우선순위는 **6번 목차 정리 → 13번 엑셀 자동 업로드 → 7번 고객 컨택 판단 → 2번 입찰**이다.
- 이메일 수집, 1번, 37번은 이번 Work 개발 우선순위에서 제외한다.
- 4개 우선도구 완료 뒤 크레딧이 남아도 임의로 다른 도구/규칙 작업에 사용하지 않고 사용자 지시를 기다린다.

## 13일 전 Chat+GitHub에서 끝내야 하는 준비 — Work 크레딧 절약 잠금
1. 기존 ingest / registry / state / audit workflow 재사용 범위 확정 — 완료된 부분 재개발 금지.
2. conflict / supersede / HOLD 우선순위와 판정 조건을 구현 가능한 형태로 고정.
3. canonical writer가 갱신할 단일 원본과 금지 대상(민감데이터/중복규칙)을 명확히 고정.
4. revision cache / changed-scope apply / feedback_id idempotency / stage checkpoint / rollback state schema를 Work가 바로 구현할 수 있게 준비.
5. 공통 기능모듈 계약을 `input schema / output schema / validation / apply hook / rollback hook / fixture / evidence hook`으로 고정.
6. 대형 단일 HTML 전체 덮어쓰기 금지, 안전한 부분 patch 또는 module/adapter 교체 우선 원칙 고정.
7. 실제 E2E 시험 입력 2개를 미리 고정:
   - 통합구조 시험: 실제 새 피드백 1건 → route → conflict/dedup → canonical write → target apply → test/evidence.
   - 개발코어 시험: 실제 작은 기능변경 1건 → module/adapter 추가 → apply → test → 실패 시 rollback.
8. 13번 자동 칼럼판별/자동매핑은 통합코어 기능이 아니라 13번 전용 module 후보로 두고, 공통 개발코어 시험용으로 최소 범위만 사용 가능.
9. 6번 parser/normalizer의 작은 규칙 1건도 개발코어 시험용 대체 후보로 유지.
10. Work에서는 기존 규칙 재독해·재요약·저장소 재검색·새 규칙문서 만들기에 크레딧 사용 금지.

## 최소 성공선 — Work가 60~80%에서 끝나도 이후 Chat 개발이 빨라져야 함
- 반드시 살아 있어야 하는 체인:
  `Chat 피드백 → registry route → conflict/dedup → GitHub canonical write/read-back → 대상 changed-scope 식별 → 안전한 코드 수정 진입`
- 위 체인까지 되면 Work가 끝나도 Chat+GitHub에서 6/13/7/2 기능개발을 계속 진행할 수 있어야 한다.
- 자동테스트/rollback/외부독립검증 일부가 남더라도 다음 Work까지 아무것도 못 하는 구조는 실패로 본다.

## 100% 구조 PASS 조건
### A. 자동 통합 코어
- registry 기반 대상 등록
- 증분 ingest
- conflict/supersede/HOLD 판정
- dedup/idempotency
- canonical single-source write/read-back
- revision cache / changed-scope apply
- restart/checkpoint/rollback
- evidence recorder / regression test

### B. Chat 기반 실제 도구개발 코어
- 새 기능은 통합코어 본체를 수정하지 않고 도구별 module/adapter만 추가·교체 가능.
- 기능모듈 표준 계약: `input schema / output schema / validation / apply / rollback / fixture / evidence`.
- 기능 추가 시 영향범위만 테스트하고 실패하면 기존 정상 버전으로 rollback.
- 실제 도구 기능변경 1건을 Chat 지시 → GitHub 반영 → 도구 적용 → 테스트/증거까지 E2E 성공.
- 최악의 경우 Work 크레딧이 구조에 모두 소진돼도 이후 Chat+GitHub에서 실제 도구개선과 완료 작업이 계속 가능해야 한다.

## 현재 실제 증거
- 기존 `WIC_CHAT_ROUTING_REGISTRY.md`에 machine-readable `route:` map 존재.
- `feedback_pipeline/cross_chat_feedback_ingest.py`는 registry를 직접 읽어 routing.
- registry 누락/중복 target/필수 route 누락 시 silent fallback 없이 error.
- `.github/workflows/cross-chat-feedback-audit.yml`은 registry 변경에도 실행.
- commits: registry `8cfafa09b022df0c6718b61e1b1924045866f577`, runtime `71f44ca32eee6cd68872a7df61d073c0720ef5e2`, workflow `974e3a16a5a1c00e225bf22486a6a3f79a00fe12`.
- runtime read-back blob `0d6c58f39b49a1de796807e8dd036b7bb9f60491`.
- GitHub Actions `Cross-chat feedback pipeline audit` run `31556600820`, job `93990199519` completed/success.
- `Run deterministic feedback fixtures`, `Validate collector state` success.
- 따라서 registry를 실제 route source로 연결하는 앞단은 PASS.
- 후반 core 전체 E2E와 Chat 기반 기능개발 module contract actual E2E는 아직 HOLD.

## 반복 금지
- 기존 feedback ingest 기본 기능 재개발 금지.
- 기존 state schema와 audit workflow 재작성 금지.
- TOOL002 키워드/최신 우선순위 classifier 보강 반복 금지.
- registry route-source 연결 반복 금지.
- 새 routing registry 생성 금지.
- 1번 defaultToc 위치 재검색 금지.
- 6번 STRUCTURE_PASS archive 재확인 금지.
- 7번 저장소 목적 불일치 재판정 금지.
- 13번 backend/API 동일 검색 반복 금지.
- 이메일 수집/1번/37번을 이번 Work 우선순위로 재등록 금지.
- 새 기능마다 통합코어를 다시 뜯어고치는 구조 금지.
- 단순 기능규칙 문서 추가를 도구개발 완료로 계산 금지.

## 최신 restart point
1. 기존 ingest + registry-source routing을 그대로 재사용.
2. **conflict/supersede/HOLD 판정 + canonical single-source write/read-back** 구현.
3. per-target revision cache + changed-scope apply + test/evidence recorder 연결.
4. feedback_id idempotency + partial failure stage checkpoint/restart/rollback 연결.
5. 공통 기능모듈 계약을 실제 코드로 구현.
6. 실제 새 피드백 1건으로 통합구조 E2E 검증.
7. 실제 작은 도구 기능변경 1건으로 module/adapter 적용/테스트/rollback E2E 검증.
8. 전체 성공 증거가 생긴 뒤에만 구조 PASS.
9. 구조 PASS 후 **6 → 13 → 7 → 2** 개발완료 목표.
10. 2번까지 완료 후 크레딧이 남으면 임의 진행 금지.

## blocker / 개선방법
- 자동 통합 후반 core actual E2E 없음 → Work 구현 범위를 후반 core에 집중.
- Chat 기반 실제 도구개발 module contract actual E2E 없음 → 실제 작은 기능변경 1건으로 검증.
- restart/rollback stage checkpoint 증거 없음 → last_success_stage 기반 재개와 rollback 구현.
- 제3자 독립검증 actual external run/result 없음 → 실제 외부 run/result URL 전 독립검증 PASS 금지.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.