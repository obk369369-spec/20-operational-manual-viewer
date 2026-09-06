# WIC TOOL044 + TOOL043 ONE-RUN WORK INSTRUCTION

상태: READY_TO_PASTE_OR_LOAD_IN_WORK
목표: TOOL044를 외부부품 진위증명·조달·조합·독립검증·배포 공통계층으로 증분 확장하고, TOOL043에서 그 증거상태와 중단상태를 관찰할 수 있게 한 뒤 실제 Windows 사용폴더 배포본 재시험까지 한 번의 Work 실행에서 `DEPLOYED_PASS`로 닫는다.

## A. 시작 전에 반드시 읽을 정본
1. `feedback_pipeline/WIC_WORK_COMMON_EXECUTION_BLOCK.md`
2. `feedback_pipeline/TOOL044_MASTER.md`
3. `feedback_pipeline/WIC_TOOL044_PROVENANCE_PILOT_PLAN.md`
4. `feedback_pipeline/WIC_EXTERNAL_TRUST_AND_RECEIPT_GATE.md`
5. `tool043/WIC_RULE_SOURCE.md`
6. latest SAFE_CHECKPOINT / VERIFIED_COMPONENT_REGISTRY / TOOL043 deployed evidence

이미 PASS/REMOTE_VERIFIED/DEPLOYED_PASS이고 이번 변경의 직접 영향이 없는 것은 `SKIP_REUSE`. 전체 USB/전체 history/전도구 감사 금지.

## B. 크레딧·시간 운영 원칙
최근 사용자가 제공한 사용량 스냅샷 기록상 Work/Codex 주간 기본 한도는 100% 남음, 추가 구매 크레딧은 0인 상태가 확인됐으나 이것은 현재 실행 시점의 live meter로 간주하지 않는다. 향후 여러 공통층을 확장해야 하므로 이번 Work는 ‘남은 한도를 쓰기 위해’ 작업하지 않는다.

이번 Work에서 허용되는 크레딧 사용은 오직:
- 외부 검증부품 후보의 새로운 적합성 판단
- 외부 공식기록의 의미 비교가 로컬 규칙만으로 결정되지 않는 경우
- TOOL043/044 통합에서 실제 코드변경이 필요한 최소 범위

다음은 Work에서 하지 않는다:
- 기존 PASS 재조사
- 넓은 대화기록 재검색
- 여러 도구 동시수리
- TOOL041/042 착수
- TOOL043 전체 24시간 자율개발 기능 확장
- 같은 검색/같은 실패 반복
- 단순 hash/diff/test/deploy를 AI 추론으로 반복

기계적 작업은 기존 local-first/mechanical/fast-deploy 및 외부 무료 verifier/표준 도구로 내린다.

## C. 절대 착수 게이트
코드 수정 전에 `ONE_RUN_DEPLOYABLE_PRECHECK`를 수행한다.
아래가 모두 YES일 때만 수정 시작:
- TOOL044 기존 실행구조 재사용 가능
- TOOL043 canonical repo와 실제 사용폴더 확인
- 실제 representative input/expected 확보
- 외부 verifier 후보를 bounded search로 확보 가능
- verifier를 수정 없이 설치/사용할 수 있음
- 공식 외부 evidence quorum을 확보할 수 있음
- 영향 회귀 범위가 작고 명확함
- GitHub write/read-back 가능
- TOOL044/TOOL043 실제 사용폴더 배포 가능
- 배포된 복사본을 같은 실행에서 재시험 가능
- 현재 실행 안에서 DEPLOYED_PASS까지 닫을 합리적 확신이 있음

하나라도 NO/UNKNOWN이면 코드를 건드리지 말고 `NO_START_ONE_RUN_NOT_CONFIDENT`로 종료한다. 중간 개발물을 만들어 다음 Work로 넘기지 않는다.

## D. 외부부품/검증기 진위 규칙
AI/WIC가 receipt에 적은 source/version/hash/PASS는 증거가 아니다.
`SELF_REPORTED_SOURCE = NOT_EVIDENCE`
`NO_PROVENANCE = NOT_EXTERNAL_COMPONENT`

외부 component/validator는 반드시 외부 공식기록을 직접 조회하여 검증한다.
최소:
- official upstream/official registry
- exact release/tag/commit
- license
- artifact digest 또는 signed checksum
- 실제 다운로드 artifact의 독립 digest 재계산
- 가능 시 maintainer signature / Sigstore-cosign bundle / Rekor inclusion proof / GitHub or other signed attestation

최소 2개의 독립 외부근거가 identity/version/digest를 동일하게 지지하거나, 강한 cryptographic attestation + 독립 digest 재계산이 일치해야 `EXTERNAL_EVIDENCE_VERIFIED`.
WIC 내부 GitHub 문서나 AI가 기입한 URL은 외부근거 개수에 포함하지 않는다.

## E. 검증도구는 직접 외부에서 가져온다
핵심 provenance/signature/attestation/functional/E2E verifier를 WIC에서 새로 만들어 신뢰하지 않는다.
TOOL044가 외부에서 실제 공유·사용·유지되는 무료 verifier를 직접 획득한다.
후보군 예:
- in-toto
- Sigstore/cosign
- 적합한 공개 artifact의 Rekor proof
- pytest/Playwright
- Git/VCS native read-back
- OS/standard cryptographic hash utility

각 verifier 자체도 upstream/release/license/digest/사용 가능성을 검증한다.
외부 READY verifier가 없고 자체 validator를 새로 만들어야 한다면 이번 범위에서는 `EXTERNAL_VALIDATOR_NOT_READY`로 중단하고 자체 검증기를 새로 개발하지 않는다.

## F. Receipt / 증거체인
각 실행층은 작은 immutable JSON 검증 영수증을 append-only로 발행한다.
필수:
TASK_ID
REQUIREMENT_ID
LAYER_ID
INPUT_SOURCE
INPUT_SHA256
EXECUTOR
COMPONENT_ID
VERSION
EXTERNAL_SOURCE_REFS[]
EXTERNAL_ATTESTATION_REFS[]
UPSTREAM_ARTIFACT_SHA256
ACTUAL_SHA256
PREVIOUS_RECEIPT_SHA256
RESULT
NATIVE_VERIFIER_OUTPUT_REF
NEXT_ALLOWED_STATE

receipt 존재만으로 PASS 금지.
외부 verifier가 receipt의 source/version/hash/attestation을 다시 조회해 일치시켜야 한다.
Receipt chain이 끊기거나 PREVIOUS_RECEIPT_SHA256가 불일치하면 즉시 BLOCK.

## G. 독립 역할 분리
Producer: 결과 생성, 자기 FINAL PASS 금지.
Verifier A: 외부 provenance/identity/digest 검증.
Verifier B: 실제 기능/EXPECTED↔ACTUAL 검증.
Verifier C: GitHub remote read-back + 실제 배포본 digest/E2E 검증.
Verifier D: receipt 값과 외부 공식증거 quorum 최종대조.

같은 WIC 자체코드 하나가 A/B/C/D를 모두 흉내내면 FAIL.
Verifier disagreement는 다수결로 강행하지 않고 `VERIFICATION_CONFLICT`.

## H. 충돌 차단
Strict state:
`PLAN → SOURCE_VERIFIED → EXTERNAL_EVIDENCE_VERIFIED → SANDBOX_PASS → INTEGRATION_PASS → REGRESSION_PASS → REMOTE_VERIFIED → DEPLOYED → DEPLOYED_PASS`

- Single Writer
- Lock Scheduler
- Immutable Receipt
- Receipt Hash Chain
- Interpretation Gate
- 다른 층 내부상태 직접수정 금지

동일 REQUIREMENT_ID를 두 독립 해석으로 비교하고 충돌 시 canonical requirement/제3 auditor로 수렴하기 전 실행 금지.

## I. 이번 실제 범위
1. latest MASTER/checkpoint/TOOL044 existing PASS 로드
2. TOOL043 current deployed evidence 및 실제 폴더 확인
3. 외부 provenance/attestation/receipt validator 후보 bounded search
4. 가장 작은 READY 조합 선정; 첫 PASS에서 검색 중단
5. upstream/registry/release/signature/digest 외부근거 quorum 확인
6. sandbox 실제 실행
7. native verifier output 보존
8. receipt chain 연결
9. TOOL043 status에 최소 표시:
   - RUNNING
   - VERIFYING
   - DEPLOYING
   - DEPLOYED_PASS
   - WORK_EXCEPTION_READY
   - WAITING_EXTERNAL
   - STALLED
   - VERIFICATION_CONFLICT
   - LAST_SAFE_CHECKPOINT
10. representative actual input/function test
11. impacted regression
12. GitHub commit/push/read-back
13. 실제 TOOL044 폴더 배포
14. 실제 TOOL043 폴더 배포
15. 배포된 복사본 동일 input으로 재실행
16. external evidence quorum + final receipt chain 재검증
17. `DEPLOYED_PASS`
18. SAFE_CHECKPOINT + VERIFIED_COMPONENT_REGISTRY

## J. TOOL043 → Work 연결 경계
현재 플랫폼에서 TOOL043이 Work를 외부에서 무인 자동기동할 수 있는 공식 인터페이스가 실제로 확인되기 전에는 ‘자동 Work 시작’이라고 주장하지 않는다.
이번에는 43번이 `WORK_EXCEPTION_READY`와 최소 handoff 위치/마지막 checkpoint/남은 이유를 자동 표시하게 한다.
Work가 실제로 자동기동 가능한 공식 인터페이스가 발견되면 별도의 추론으로 새로 만들지 말고 TOOL044에서 외부/공식 인터페이스 진위를 검증한 뒤만 연결한다.

Work 또는 runner가 일정 heartbeat/receipt 진행 없이 정지하면 43번에 `STALLED` 표시. 관찰자에게 수리·로그복사·재시작을 요구하지 않는다. 가능한 자동복구를 먼저 수행하고, 실패하면 마지막 SAFE_CHECKPOINT와 정지 이유만 보여준다.

## K. 저장용량
GitHub 장기저장:
- receipt JSON
- manifest
- digest
- stable external evidence/attestation refs
- 최소 최종 증거

GitHub 장기저장 금지:
- 대형 전체 로그
- 반복 screenshot
- 재현 가능한 중간 build
- 동일 artifact 복사본

같은 artifact는 SHA256 content-addressed 1회 참조. 큰 임시 증거는 local evidence cache + TTL.

## L. 완료/중단 보고
COMPLETE는 아래 전부 PASS일 때만:
- 외부 component/validator의 official provenance
- 외부증거 quorum
- native independent verifier PASS
- receipt↔외부공식기록 MATCH
- actual function PASS
- impacted regression PASS
- remote read-back PASS
- actual-use deploy PASS
- deployed-copy retest PASS
- final receipt-chain PASS
- TOOL043 observer status PASS

중간에 시간이 부족하거나 새로운 대형 문제가 발생하면:
1. 미검증 변경을 실사용에 배포하지 않는다.
2. 기존 안정본 유지/rollback.
3. 마지막 SAFE_CHECKPOINT 보존.
4. 43번에 `STALLED` 또는 정확한 외부 HOLD 상태만 표시.
5. `진행 중`, `거의 완료`, `다음 Work에서 마무리`를 COMPLETE처럼 보고하지 않는다.

## M. 최종 보고 형식
- ONE_RUN_PRECHECK: PASS/NO_START
- 채택 외부 component/validator 이름, 공식 upstream, version, digest
- 외부증거 quorum 원천
- native verifier 결과
- receipt chain final hash
- actual input/result
- regression
- GitHub commit SHA + remote read-back
- 실제 TOOL044/043 배포 경로
- deployed-copy test
- DEPLOYED_PASS 또는 STALLED/HOLD
- SAFE_CHECKPOINT
- Work 중복조사/재시험을 얼마나 SKIP_REUSE했는지
- 사용자 중간조작 횟수

사용자 중간조작 목표: 0.
