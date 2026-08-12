# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 15:27 KST
상태: ACTIVE / STRUCTURE_FIRST / CANONICAL_TRANSPORT_PASS / TARGET_APPLY_HOLD
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 현재 최우선 1순위
- 2026-08-13 Work 사용 전후 최우선은 개별 도구가 아니라 **WIC 전체 자동 통합 기반 구조의 실제 완성 + E2E 검증**이다.
- 단순 파일/스크립트/commit 존재는 구조 PASS가 아니다.
- 실제 새 피드백 1건이 `자동 분류 → 충돌/중복 → canonical GitHub write/read-back → 대상 적용 → 실제 테스트/증거 → restart/rollback` 전체를 통과해야 구조 PASS다.
- 구조 PASS 후 우선순위는 **이메일 수집 → 7번 고객 컨택 판단 → 1번 중간/최종 안내서 → 37 메타데이터 → 13 엑셀 자동 업로드 → 6번 목차 정리 → 2번 입찰 → 28~31 → 나머지 등록 도구/주요 업무창**이다.

## 이번 실행에서 실제 개선한 부분
### 1. 완료된 앞단 재개발 금지 준수
- 기존 ingest / registry-source routing / conflict-dedup / revision/checkpoint/module-contract / canonical_writer는 다시 만들지 않았다.
- 최신 restart point `CANONICAL_WRITE`에서 시작했다.

### 2. 실제 canonical GitHub transport 추가
- 새 실행기: `feedback_pipeline/apply_feedback_event.py`
- commit: `2c0b56283f7179644773dc5da38eae4c027c505a`
- 기존 `cross_chat_feedback_ingest.py`와 `canonical_writer.py`를 import하여 재사용한다.
- 토큰/Secret은 코드에 저장하지 않고 GitHub Actions checkout/commit/push transport로 분리했다.

### 3. 실제 GitHub Actions runner 연결
- workflow: `.github/workflows/wic-feedback-event.yml`
- commit: `d0821d3c2b0799b26e58e5f5d0dfd71d982f2dcf`
- 실제 이벤트 파일: `feedback_pipeline/pending_event.json`
- event commit: `6a41899ec1e15370d292cc28d7585a8378e4adbf`

### 4. 실제 새 피드백 1건 canonical 반영 성공
- feedback_id: `f2aeb4e8f5fac3c9618f`
- 분류: `PRIORITY_CHANGE`
- 자동 route: `CENTRAL, EMAIL_DB, TOOL001, TOOL002, TOOL006, TOOL007, TOOL013, TOOL037, WORK_GATE`
- `WIC_GLOBAL_OPERATING_RULES.md`의 machine-managed canonical section에 실제 기록됨.
- canonical write commit: `50d0ca22a5427293c6cdf1987d83110f3e0dbfd4`
- master read-back blob: `ad4882ecb9dbe1c99501105273bfaef69fe0e5e2`
- `feedback_pipeline/state.json`에 processed feedback id와 checkpoint가 실제 저장됨.

### 5. 실제 GitHub Actions 결과
- workflow run: `31569869289`
- job: `94029337925`
- 결과: `completed / success`
- 성공 단계:
  - existing ingest fixtures
  - existing canonical writer fixtures
  - real pending feedback apply
  - canonical section/evidence verification
  - canonical mutation/evidence commit + push
- 이는 GitHub 내부 실행증거다. **제3자 독립검증으로 표시하지 않는다.**

### 6. 대상 저장소 중앙원본 포인터 read-back 확인
- TOOL001 `01-auto-guide-v1/WIC_RULE_SOURCE.md`: 중앙 단일 원본 참조 확인.
- TOOL002 `02-auto-bid-narajangter-v1/WIC_RULE_SOURCE.md`: 중앙 단일 원본 참조 확인.
- TOOL006 `06-toc-check/WIC_RULE_SOURCE.md`: 중앙 단일 원본 참조 확인.
- TOOL007 `07-wic-setting-tool-v1/WIC_RULE_SOURCE.md`: 중앙 단일 원본 참조 확인. 단 실행판 목적 불일치 HOLD 유지.
- TOOL013 `13-excel-upload/WIC_RULE_SOURCE.md`: 중앙 단일 원본 참조 확인.
- 포인터가 이미 존재했으므로 중복 파일을 새로 만들지 않았다.

## 현재 실제 남은 부분
1. canonical revision을 각 실제 target repository가 기계적으로 읽고 적용하는 공통 target adapter/transport.
2. target별 `last applied canonical revision` 실제 영속화.
3. changed-scope만 실제 target code/config에 적용.
4. 실제 target run/test 결과와 URL/file/artifact 저장.
5. 실패 시 last_success_stage부터 재개 + rollback 실제 실행증거.
6. EMAIL_DB / TOOL037 / WORK_GATE처럼 독립 저장소가 아닌 lane의 apply 방식 명확화.
7. 위 전체 후 actual feedback E2E 1건을 `TEST_EVIDENCE`까지 통과.

## blocker
### TARGET_REVISION_READ_APPLY = HOLD
- 원인: 중앙 canonical write/read-back은 실제 성공했지만 cross-repository target apply/test가 아직 자동으로 실행되지 않았다.
- 현재 포인터 read-back은 '중앙 원본을 가리킨다'는 증거이지 '새 revision을 실제 기능에 적용하고 테스트했다'는 증거가 아니다.
- 따라서 구조 전체 PASS 금지.

## 개선방법
- 중앙 repo의 `target_apply_manifest.json`을 입력으로 받는 범용 target adapter/dispatcher를 만든다.
- 각 target은 중앙 revision을 읽고 local `last_applied_revision`과 비교한다.
- 변경이 없으면 SKIP, 변경이 있으면 impacted scope만 적용한다.
- apply 후 해당 target의 실제 fixture/test를 실행하고 결과 URL/artifact를 중앙 evidence에 되돌린다.
- 실패 시 target별 rollback hook 실행 후 checkpoint를 HOLD로 남긴다.
- cross-repo 인증은 저장소 코드에 Secret을 넣지 않고 GitHub App/Actions/connector 권한으로 분리한다.

## 최신 restart point
1. `apply_feedback_event.py`, `canonical_writer.py`, 기존 ingest 로직을 그대로 재사용한다.
2. `feedback_pipeline/target_apply_manifest.json`을 읽는 **cross-repository target adapter/dispatcher**부터 구현한다.
3. 첫 실제 target은 기존 포인터와 테스트 자산이 있는 TOOL006 또는 TOOL013 중 하나를 사용한다.
4. `canonical revision read → changed-scope apply → target test → evidence URL/artifact → central revision cache update`를 실제 1건 성공시킨다.
5. 실패 경로도 1건 실행해 rollback/restart 증거를 남긴다.
6. 그 뒤 동일 feedback_id `f2aeb4e8f5fac3c9618f`의 checkpoint를 `TEST_EVIDENCE`까지 전진시킨다.
7. 전체 체인이 증거와 함께 성공한 뒤에만 구조 PASS로 변경한다.

## Work 크레딧 사용 게이트
- 기존 규칙 재독해/재요약/저장소 반복검색에는 사용 금지.
- 이미 PASS된 ingest/registry/conflict/canonical writer 재개발 금지.
- Work는 cross-repository apply, 실제 target 실행/E2E, 외부 권한/환경 때문에 Chat+GitHub에서 막히는 구간에만 사용한다.

## 독립검증 상태
- GitHub 내부 Actions/run/read-back: 실제 증거 있음.
- 제3자 외부검증: **없음 / HOLD**.
- 실제 외부 run/result URL이 생기기 전 독립검증 PASS 금지.
