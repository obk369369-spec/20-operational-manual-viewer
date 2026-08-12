# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 11:27 KST
상태: ACTIVE / STRUCTURE_FIRST
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 현재 결론
- 2026-08-13 Work 1순위는 개별 도구가 아니라 WIC 전체 재사용 자동 통합 구조의 실제 구현과 E2E 검증이다.
- 이 구조의 목표는 단순 규칙 통합이 아니라 **Work 없이도 이후 Chat+GitHub에서 도구 기능을 추가·교체·수정·검증할 수 있는 공통 개발 기반**까지 제공하는 것이다.
- 새 registry는 만들지 않는다. 기존 `WIC_CHAT_ROUTING_REGISTRY.md`를 재사용한다.
- 실제 새 피드백 1건이 전체 체인을 통과하기 전 구조 PASS 금지.
- 최신 사용자 우선순위는 구조 PASS 후 **6번 목차 정리 → 13번 엑셀 자동 업로드 → 7번 고객 컨택 판단 → 2번 입찰**이다.
- 이메일 수집, 1번, 37번은 이번 Work 개발 우선순위에서 제외한다.
- 4개 우선도구 완료 뒤 크레딧이 남아도 임의로 다른 도구/규칙 작업에 사용하지 않고 사용자 지시를 기다린다.

## 구조 보완의 핵심 범위 — 재개발 방지
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
사용자가 말한 “도구별 기능 어댑터/플러그인 공통 규격”은 별도 방향이 아니라 아래 큰 목표의 한 구성요소다.
- 새 기능을 Work 전용 작업으로 만들지 않고 **Chat에서 기능 요구를 말하면 기존 도구에 안전하게 붙일 수 있는 표준 기능모듈 규격**을 둔다.
- 모든 도구 기능모듈은 최소 `input schema / output schema / validation / apply hook / rollback hook / test fixture / evidence hook` 인터페이스를 따른다.
- 새 기능은 통합 코어 본체를 수정하지 않고 해당 도구의 module/adapter만 추가·교체할 수 있어야 한다.
- 예: 13번의 `원본 칼럼 자동판별 → 자동매핑 → confidence 판정 → 애매한 칼럼 HOLD → 결과 검증`은 통합코어 자체 기능이 아니라 **13번 기능모듈**이지만, 이 기능을 나중에 Chat+GitHub만으로 추가할 수 있게 하는 공통 개발 규격은 구조 1순위 보완 범위다.
- 동일 방식으로 6번 발행사별 목차 parser/normalizer, 7번 판단 모듈, 2번 수집/판정 모듈도 플러그인처럼 교체 가능해야 한다.
- 대형 단일 HTML 전체 덮어쓰기 없이 안전한 부분 patch/모듈 교체가 가능해야 한다.
- 기능 추가 시 자동으로 영향범위만 테스트하고 실패하면 기존 정상 버전으로 rollback해야 한다.
- 따라서 최악의 경우 Work 크레딧이 구조 완성에 모두 소진되어도, 이후 Chat+GitHub에서 실제 도구 기능개선과 완료 작업이 계속 가능해야 구조 PASS 후보가 된다.

## 이번 회차 새 증거
- 최신 중앙 observer와 restart point를 먼저 read-back했고 완료 작업은 반복하지 않았다.
- 기존 `WIC_CHAT_ROUTING_REGISTRY.md` 안에 machine-readable `route:` map을 추가했다. 새 registry 파일은 만들지 않았다.
- `feedback_pipeline/cross_chat_feedback_ingest.py`에서 하드코딩된 routing keyword map을 제거하고 기존 registry를 실행 시 직접 읽어 파싱하도록 변경했다.
- registry 누락/중복 target/필수 route 누락 시 silent fallback하지 않고 error가 나도록 했다.
- `.github/workflows/cross-chat-feedback-audit.yml`이 registry 변경에도 자동 실행되도록 경로를 추가했다.
- GitHub commits: registry `8cfafa09b022df0c6718b61e1b1924045866f577`, runtime `71f44ca32eee6cd68872a7df61d073c0720ef5e2`, workflow `974e3a16a5a1c00e225bf22486a6a3f79a00fe12`.
- runtime read-back blob `0d6c58f39b49a1de796807e8dd036b7bb9f60491`에서 `WIC_CHAT_ROUTING_REGISTRY.md` 직접 참조와 parser가 반영된 것을 확인했다.
- GitHub Actions `Cross-chat feedback pipeline audit` run `31556600820`, job `93990199519`가 completed/success.
- 같은 run에서 `Run deterministic feedback fixtures`와 `Validate collector state`가 모두 success.
- 따라서 최신 restart point의 **기존 registry를 실제 route source로 연결** 단계는 PASS했다.
- 하지만 conflict/supersede/HOLD → canonical write/read-back → per-target changed-scope apply → target test/evidence 전체 후반 체인은 아직 없어 구조 전체 PASS는 HOLD다.
- 이번 사용자 보완 요구에 따라 **Chat 기반 실제 도구개발 코어**를 구조 1순위 필수 범위로 추가했다. 문서 반영 자체는 기능 PASS가 아니며 13일 실제 구현·E2E가 필요하다.

## 반복 금지
- 기존 feedback ingest 기본 기능 재개발 금지.
- 기존 state schema와 audit workflow 재작성 금지.
- TOOL002 키워드/최신 우선순위 classifier 보강 작업 반복 금지.
- registry route-source 연결 작업 반복 금지.
- 새 routing registry 생성 금지.
- 1번 defaultToc 위치 재검색 금지.
- 6번 STRUCTURE_PASS archive 재확인 금지.
- 7번 저장소 목적 불일치 재판정 금지.
- 13번 backend/API 동일 검색 반복 금지.
- 이메일 수집/1번/37번은 이번 Work 우선순위 개발 대상으로 다시 올리지 않는다.
- 새 기능마다 통합코어를 다시 뜯어고치는 구조 금지.
- 단순 기능규칙 문서 추가를 도구개발 완료로 계산 금지.

## 최신 restart point
1. 기존 ingest + registry-source routing을 그대로 재사용한다.
2. 다음은 **conflict/supersede/HOLD 판정 + canonical single-source write/read-back**을 구현한다.
3. 이후 per-target revision cache + changed-scope apply + test/evidence recorder를 붙인다.
4. 같은 feedback_id 재처리 금지와 partial failure restart/rollback을 실제 state에 연결한다.
5. 동시에 공통 기능모듈 규격(`input/output schema, validation, apply, rollback, fixture, evidence`)을 구현해 Chat+GitHub에서 도구 기능을 추가·교체할 수 있는 개발 기반을 만든다.
6. 실제 새 피드백 1건으로 자동 ingest → registry route → conflict/dedup → canonical write → target apply → test 전체 E2E를 검증한다.
7. 실제 도구 기능변경 샘플 1건도 공통 기능모듈 규격으로 추가/적용/테스트/rollback 가능한지 E2E 검증한다. 가능하면 13번 자동 칼럼매핑의 최소 모듈 또는 6번의 작은 parser rule을 시험 대상으로 사용한다.
8. 전체 체인 성공 증거가 생긴 뒤에만 구조 PASS로 전환한다.
9. 구조 PASS 후 **6 → 13 → 7 → 2** 순으로 개발완료를 목표로 진행한다.
10. 2번까지 완료 후 크레딧이 남으면 다음 작업은 임의 진행하지 않는다.

## blocker / 개선방법
- **자동 통합 구조:** conflict/supersede/HOLD 이후 canonical write와 target apply/test를 이어주는 후반 core actual E2E 증거가 없다.
  - 개선: 다음 구현을 후반 core에만 제한하고 기존 ingest/registry를 재사용한다.
- **Chat 기반 실제 도구개발:** 공통 기능모듈 규격과 안전한 부분 적용/rollback/evidence 체인이 아직 실제 코드로 검증되지 않았다.
  - 개선: Work에서 범용 module contract를 먼저 구현하고 실제 도구 기능변경 1건으로 E2E 검증한다. 이후 새 기능은 본체 수정이 아니라 adapter/module 추가를 기본으로 한다.
- **restart/rollback:** processed id dedupe는 있으나 partial failure 단계별 checkpoint/rollback 증거가 없다.
  - 개선: stage별 state와 last_success_stage를 기록하고 같은 feedback_id는 마지막 성공 단계 다음부터 재개하도록 한다.
- **제3자 독립검증:** actual external run/result 증거 없음.
  - 개선: 실제 외부 run/result URL 확보 전 독립검증 PASS 금지.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
