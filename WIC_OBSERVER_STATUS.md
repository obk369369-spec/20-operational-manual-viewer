# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 12:19 KST
상태: ACTIVE / STRUCTURE_FIRST / PREWORK_LOCKED / CORE_BACKEND_ADVANCED
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 현재 결론
- 2026-08-13 Work 1순위는 개별 도구가 아니라 **WIC 전체 재사용 자동 통합 구조 + Chat 기반 실제 도구개발 코어**의 실제 구현과 E2E 검증이다.
- 목표는 이후 Work 없이도 Chat+GitHub에서 도구 기능을 추가·교체·수정·검증할 수 있는 공통 개발 기반을 확보하는 것이다.
- 새 registry는 만들지 않는다. 기존 `WIC_CHAT_ROUTING_REGISTRY.md`를 재사용한다.
- 실제 새 피드백 1건이 `자동 분류 → route → conflict/dedup → canonical GitHub write/read-back → target apply → target test/evidence → restart/rollback` 전체를 통과하기 전 구조 PASS 금지.
- 구조 PASS 후 최신 우선순위는 **이메일 수집 → 7번 고객 컨택 판단 → 1번 중간/최종 안내서 → 37 메타데이터 → 13번 엑셀 자동 업로드 → 6번 목차 정리 → 2번 입찰 → 28~31 → 나머지 등록 도구/주요 업무창**이다.

## 이번 실행에서 실제 개선된 부분
### 1. 완료 작업 재개발 방지
- 기존 ingest / registry-source routing / state / audit workflow의 앞단은 재작성하지 않았다.
- 기존 route source인 `WIC_CHAT_ROUTING_REGISTRY.md`를 그대로 사용한다.

### 2. 후반 코어 결정 로직 실제 코드 추가
`feedback_pipeline/cross_chat_feedback_ingest.py`에 다음을 실제 구현했다.
- `ACCEPT / DUPLICATE / SUPERSEDE / HOLD_CONFLICT` 충돌판정
- 최신 PRIORITY_CHANGE가 이전 겹치는 PRIORITY_CHANGE를 supersede하는 규칙
- 명시적 CORRECTION이 이전 겹치는 규범 규칙을 supersede하는 규칙
- 같은 우선순위의 상충 CONSTRAINT는 silent overwrite하지 않고 HOLD_CONFLICT
- canonical layer 영향범위 계산: `GLOBAL / WORKGROUP / TOOL_OR_DOMAIN_OVERRIDE / DATA_OR_EXECUTION_ASSET`
- canonical revision fingerprint
- target revision cache 비교: `APPLY_CHANGED_SCOPE / SKIP_UNCHANGED`
- 단계별 checkpoint + 마지막 성공지점 재개 계약
- 공통 기능모듈 계약 검증: `input_schema / output_schema / validate / apply / rollback / fixture / evidence`
- 실제 기능코드 commit: `ad50baf1564800972f31a242221bb8a52f0e0b2c`
- read-back blob: `aa18cf8970249a72b3391a9354156376e3053e46`

### 3. 실행상태 스키마 확장
`feedback_pipeline/state.json`을 schema v2로 확장했다.
- stage order
- canonical layers
- feedback checkpoints
- target revision cache
- HOLD 저장소
- module contract required keys
- structure_pass=false 명시
- 최신 구조 PASS 후 우선순위 반영
- commit: `34f440cf83dce850c43b48dff6eba3ed73803825`

### 4. CI 계약 확장
`.github/workflows/cross-chat-feedback-audit.yml`에서 다음을 검증하도록 확장했다.
- conflict/dedup fixture
- revision/cache fixture
- checkpoint/restart fixture
- module contract fixture
- state schema v2
- 최신 post-structure priority
- commit: `b0557da24c2d3c5e9fa0386cb0ce92e3412b2f31`
- 현재 이 commit의 deploy status는 `pending`이며 target URL은 Deno build URL로 확인됨. 완료 결과 전 CI/배포 PASS 주장 금지.

### 5. 중앙 restart point 갱신
`WIC_EXECUTION_STATE.json`을 실제 남은 지점으로 이동했다.
- 다음 시작점은 `CANONICAL_WRITE`.
- 이미 구현한 routing/conflict/revision/checkpoint/module-contract는 Work에서 다시 만들지 않는다.
- commit: `64cd123da3d40590066cc2b3746b27c79a77a5f4`

## Work 크레딧 절약을 위한 남은 실제 구현 순서
1. 실제 canonical single-source writer 연결.
2. writer 결과 GitHub commit SHA 저장 + 즉시 read-back.
3. target별 canonical revision cache 영속화.
4. 변경된 scope만 실제 target module/adapter에 apply.
5. target 실제 run/test 결과와 URL/file/artifact 기록.
6. 실패 시 last_success_stage에서 재개하고 rollback 증거 저장.
7. 실제 새 피드백 1건으로 전체 E2E 수행.
8. 실제 작은 도구 기능변경 1건으로 module/adapter 추가 → apply → test → rollback E2E 수행.
9. 위 증거가 모두 생긴 뒤에만 구조 PASS.

## 최소 성공선 — Work가 60~80%에서 끝날 경우
반드시 아래 체인은 실제로 살아 있어야 한다.
`Chat feedback → registry route → conflict/dedup → canonical GitHub write/read-back → changed-scope 식별 → 안전한 target 코드수정 진입`
이 체인이 되면 Work 크레딧이 끝나도 Chat+GitHub에서 후속 도구 기능개발을 계속할 수 있다. 다음 Work까지 아무것도 못 하는 상태면 구조 실패다.

## 아직 HOLD인 부분
- 실제 GitHub canonical writer/read-back 자동 체인: HOLD
- target revision cache의 실제 영속 저장/읽기: HOLD
- target module/adapter 실제 적용: HOLD
- 실제 target run/test/evidence URL: HOLD
- 실제 rollback 실행증거: HOLD
- 전체 새 피드백 E2E: HOLD
- 구조 PASS: HOLD

## blocker / 개선방법
- **blocker:** GitHub connector를 통해 파일 갱신은 가능하지만, 현재 repository 내부 Python runtime 자체가 GitHub contents write 권한으로 canonical commit을 만들고 target repo까지 자동 적용하는 E2E runner는 아직 연결되지 않았다.
- **개선:** Work에서는 이 writer/apply runner와 실제 E2E에만 크레딧 사용. 기존 규칙 재독해·재요약·registry 재생성·이미 구현한 conflict/revision/checkpoint 로직 재개발 금지.
- **독립검증:** GitHub 내부 fixture/CI와 제3자 외부검증을 구분한다. 실제 외부 run/result 증거가 생기기 전 `독립검증 PASS` 금지.

## 반복 금지
- 기존 feedback ingest 기본 기능 재개발 금지.
- registry-source routing 재개발 금지.
- 새 routing registry 생성 금지.
- conflict/dedup 계약 재설계 반복 금지.
- revision fingerprint / changed-scope decision 계약 재설계 반복 금지.
- checkpoint/module-contract 계약 재설계 반복 금지.
- 기존 규칙 재독해·재요약에 Work 크레딧 사용 금지.
- 단순 문서/스크립트 존재를 구조 PASS로 계산 금지.

## 최신 restart point
1. `CANONICAL_WRITE` 실제 runner 연결부터 시작.
2. GitHub commit/read-back 증거 확보.
3. target revision cache 영속화 + changed-scope apply 연결.
4. target test/evidence recorder 연결.
5. failure checkpoint/rollback actual run 연결.
6. 실제 새 피드백 1건 전체 E2E.
7. 실제 작은 도구 기능변경 1건 module/adapter E2E.
8. 전체 성공 후 구조 PASS.
9. 구조 PASS 후 **이메일 수집 → 7 → 1 → 37 → 13 → 6 → 2 → 28~31 → 나머지** 순으로 진행.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
