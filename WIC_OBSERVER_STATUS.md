# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 10:20 KST
상태: ACTIVE / STRUCTURE_FIRST
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 현재 결론
- 2026-08-13 Work 1순위는 개별 도구가 아니라 WIC 전체 재사용 자동 통합 구조의 실제 구현과 E2E 검증이다.
- 새 registry는 만들지 않는다. 기존 `WIC_CHAT_ROUTING_REGISTRY.md`를 재사용한다.
- 실제 새 피드백 1건이 전체 체인을 통과하기 전 구조 PASS 금지.
- 최신 사용자 우선순위는 구조 PASS 후 **6번 목차 정리 → 13번 엑셀 자동 업로드 → 7번 고객 컨택 판단 → 2번 입찰**이다.
- 이메일 수집, 1번, 37번은 이번 Work 개발 우선순위에서 제외한다.
- 4개 우선도구 완료 뒤 크레딧이 남아도 임의로 다른 도구/규칙 작업에 사용하지 않고 사용자 지시를 기다린다.

## 이번 회차 새 증거
- 최신 중앙 observer와 restart point를 먼저 read-back했고 완료 작업은 반복하지 않았다.
- `feedback_pipeline/cross_chat_feedback_ingest.py`에 `TOOL002` 라우팅 키워드(`2번`, `입찰`, `입찰 도구`, `bid`, `tender`)를 기존 map에 추가했다.
- 자연어 우선순위 변경 표현 `우선순위는`, `우선순위 아래에`, `제외시켜`, `제외해`를 `PRIORITY_CHANGE`로 잡도록 기존 deterministic classifier를 최소 보강했다.
- 실제 최신 우선순위 문장을 regression fixture로 추가해 `TOOL002/006/007/013/001/037/EMAIL_DB` 라우팅과 `PRIORITY_CHANGE` 판정을 동시에 검증하도록 했다.
- GitHub commit: `29bb18630f18ee6e975465d9011371fedef8bf70`.
- read-back blob: `2291b3227fc6d525375fa1f964685d4ad8d90106`에서 `TOOL002`와 classifier 보강이 실제 반영된 것을 확인했다.
- GitHub Actions `Cross-chat feedback pipeline audit` run `31553365718`에서 `Run deterministic feedback fixtures`와 `Validate collector state` 단계가 둘 다 success로 확인됐다.
- 위 증거로 **TOOL002 라우팅 누락 + 최신 우선순위 문구 분류 blocker는 해소**했다.
- 다만 **자동 ingest → registry route → conflict/dedup → canonical write → target apply → test** 전체 E2E는 아직 성공 증거가 없으므로 구조 PASS는 계속 HOLD다.

## 반복 금지
- 기존 feedback ingest 기본 기능 재개발 금지.
- 기존 state schema와 audit workflow 재작성 금지.
- TOOL002 키워드/최신 우선순위 classifier 보강 작업 반복 금지.
- 1번 defaultToc 위치 재검색 금지.
- 6번 STRUCTURE_PASS archive 재확인 금지.
- 7번 저장소 목적 불일치 재판정 금지.
- 13번 backend/API 동일 검색 반복 금지.
- 이메일 수집/1번/37번은 이번 Work 우선순위 개발 대상으로 다시 올리지 않는다.

## 최신 restart point
1. 기존 feedback ingest의 입력/정규화/기본 dedupe와 이번에 검증된 TOOL002/우선순위 classifier를 그대로 재사용한다.
2. 기존 `WIC_CHAT_ROUTING_REGISTRY.md`를 실제 route source로 연결한다.
3. conflict/supersede/HOLD 기록, canonical write/read-back, per-target revision cache, changed-scope apply, test/evidence recorder를 구현한다.
4. 실제 새 피드백 1건으로 자동 ingest → registry route → conflict/dedup → canonical write → target apply → test 전체 E2E를 검증한다.
5. 전체 체인 성공 증거가 생긴 뒤에만 구조 PASS로 전환한다.
6. 구조 PASS 후 **6 → 13 → 7 → 2** 순으로 개발완료를 목표로 진행한다.
7. 2번까지 완료 후 크레딧이 남으면 다음 작업은 임의 진행하지 않는다.

## blocker / 개선방법
- **자동 통합 구조:** registry 기반 라우팅 이후 후반 core actual E2E 증거가 없다.
  - 개선: 기존 ingest/registry를 재사용하고 후반 core만 구현한다.
- **제3자 독립검증:** actual external run/result 증거 없음.
  - 개선: 실제 외부 run/result URL 확보 전 독립검증 PASS 금지.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
