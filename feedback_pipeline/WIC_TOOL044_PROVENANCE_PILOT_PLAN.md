# TOOL044 Provenance Pilot Plan

상태: READY_FOR_ONE_RUN_WORK / NOT_DEPLOYED

## 목적
TOOL044를 `외부부품 진위증명 → 조달 → 조합 → 독립검증 → 배포` 공통계층으로 확장하고, 첫 실증대상으로 TOOL043의 최소 관찰자/증거연결 범위를 사용해 한 번의 Work 실행에서 DEPLOYED_PASS까지 닫는다.

이번 파일의 핵심은 WIC 내부 문구나 AI 자기진술을 증거로 인정하지 않는 것이다. 외부부품·검증기·실행기는 외부의 독립된 공식 기록을 기계적으로 조회·대조해야 하며, 사람이/AI가 receipt 필드에 URL·버전·hash를 임의 기입한 것만으로는 다음 상태로 진행할 수 없다.

## 첫 대상 선정
- TOOL041/042는 다중 구조와 반복실패 이력 때문에 첫 실증에서 제외.
- TOOL043은 기존 TOOL044 적용 어댑터와 실제 DEPLOYED_PASS 증거가 이미 있어 기존 PASS를 SKIP_REUSE하면서 provenance/receipt 계층만 증분 확장할 수 있으므로 ONE_RUN_DEPLOYABLE 가능성이 가장 높다.
- TOOL043 전체 24시간 자율실행을 이번 범위에 포함하지 않는다.
- 이번 실증 범위는 `외부부품 진위증명 + 외부증거 교차대조 + receipt chain + 독립검증 + 43번 관찰표시/증거연결 + Work 예외대기열 표시 + 저장소/실사용 배포본 재검증`까지다.
- Work 자체를 TOOL043이 플랫폼 밖에서 자동 기동할 수 있다는 증거가 없으면 자동 Work 시작을 구현했다고 주장하지 않는다. 대신 `WORK_EXCEPTION_READY / WORK_HANDOFF_REQUIRED / STALLED / LAST_SAFE_CHECKPOINT`를 43번에서 명확히 표시하고, 플랫폼이 실제 외부기동 인터페이스를 제공할 때만 TOOL044 검증 후 연결한다.

## Receipt 정의
각 실행층은 작은 JSON `검증 영수증(receipt)`만 발행한다. 원본 로그/스크린샷/바이너리를 GitHub에 중복 저장하지 않는다.
필수 필드:
- TASK_ID / REQUIREMENT_ID / LAYER_ID
- INPUT_SOURCE / INPUT_SHA256
- EXECUTOR / COMPONENT_ID / VERSION
- UPSTREAM_URL / UPSTREAM_RELEASE_OR_COMMIT
- UPSTREAM_ARTIFACT_SHA256
- EXPECTED_ID / ACTUAL_SHA256
- PREVIOUS_RECEIPT_SHA256
- RESULT
- SIGNATURE_OR_ATTESTATION_REF
- EXTERNAL_EVIDENCE_REFS[]
- EXTERNAL_EVIDENCE_QUORUM_RESULT
- EVIDENCE_LOCATION
- NEXT_ALLOWED_STATE

중요: 위 필드는 `자기기입 사실`이 증거가 아니다. 각 값은 외부 검증기가 독립적으로 다시 조회하여 일치해야 한다.

## 외부부품 진위 게이트
`NO_PROVENANCE = NOT_EXTERNAL_COMPONENT`
`SELF_REPORTED_SOURCE = NOT_EVIDENCE`
`ONE_EXTERNAL_URL_ONLY = INSUFFICIENT`

외부부품 인정조건:
1. upstream 원본 URL 또는 공식 배포처
2. exact release/tag/commit
3. 원본 artifact digest
4. 라이선스
5. 원본 artifact 보존 또는 재획득 가능성
6. sandbox에서 시험한 digest
7. 장착 artifact digest
8. 배포 artifact digest
9. 가능한 경우 공급자 서명/provenance/attestation
10. hash chain 일치
11. 최소 2개의 서로 독립된 외부 근거가 동일 identity/version/digest를 지지하거나, 하나의 강한 cryptographic attestation + 독립 artifact digest 재계산이 일치할 것
12. 공식 package registry / upstream release / signature-transparency log / signed attestation 등 서로 성격이 다른 근거를 우선 조합할 것

예시 외부증거 조합:
- 공식 package registry metadata + upstream official release/tag + 실제 다운로드 artifact SHA256
- upstream signed release + Sigstore/cosign bundle/Rekor inclusion proof + 실제 artifact SHA256
- GitHub artifact attestation + repository/commit identity + 실제 artifact SHA256

WIC/AI가 만든 receipt의 URL·version·hash 텍스트는 외부근거 개수에 포함하지 않는다.
TOOL044 무수정 부품은 원칙적으로 `UPSTREAM_HASH = SANDBOX_HASH = INTEGRATED_HASH = DEPLOYED_HASH`여야 한다. 불일치 시 REJECT.

## 검증도구 외부조달 원칙
검증층/검증기를 WIC에서 새로 만들어 신뢰하지 않는다.
- provenance/signature/attestation/hash/E2E 검증 핵심은 외부에서 실제 사용·공유·유지되는 검증도구를 TOOL044가 직접 획득하여 담당하게 한다.
- 외부도구 자체도 공식 upstream, release/version, license, digest, 사용기록, 유지보수 상태를 검증한다.
- 외부 검증도구가 출력한 native verification output/bundle/log reference를 receipt에 참조한다.
- WIC 코드는 외부 검증기 실행 순서·입출력 연결·상태전이만 담당할 수 있으며 외부 검증기의 PASS를 임의 생성하거나 대체하지 못한다.
- 자체 작성 validator가 필요해지는 순간 `EXTERNAL_VALIDATOR_NOT_READY`로 판정하고, 먼저 외부 READY_COMPONENT를 다시 찾는다.

후보 계열(채택 전 TOOL044 검증 필수):
- in-toto 계열 supply-chain layout/link 검증
- Sigstore/cosign 계열 signature/attestation 검증
- 비민감 공개 artifact에 한해 Rekor transparency proof
- pytest/Playwright 등 실제 functional/E2E 검증
- Git/공식 VCS read-back + OS 표준 hash 도구를 이용한 독립 digest 재계산

유료 SaaS/API 의존은 기본 차단한다.

## 독립 검증 구조
- Producer: 결과 생성. 자기 PASS 확정 금지.
- Attestor/Verifier A: provenance/identity/digest를 외부 공식기록과 독립 대조.
- Functional Verifier B: 실제 입력/기능/EXPECTED↔ACTUAL 검증.
- Deployment Verifier C: 저장소 read-back 및 배포본 digest/E2E 검증.
- Evidence Quorum Verifier D: receipt 안의 source/version/hash/signature 값과 외부 공식 기록 2개 이상 또는 cryptographic attestation+digest가 실제로 일치하는지 최종 대조.
- A/B/C/D가 같은 자체 생성 코드 하나를 공유해 자기검증하지 않는다.
- receipt 발행자는 자기 receipt를 최종 검증하지 못한다.
- verifier 자체 PASS도 다른 verifier 또는 외부 cryptographic proof로 확인되지 않으면 FINAL PASS에 사용할 수 없다.

## 저장용량 최소화
GitHub에는 receipt/manifest/hash/서명·attestation 참조만 저장한다.
- receipt는 작은 JSON 텍스트를 기본으로 한다.
- 같은 artifact는 SHA256 content-addressed 방식으로 한 번만 참조한다.
- 외부 transparency log/attestation은 가능하면 원문 전체 복사 대신 stable ID, digest, verification bundle 또는 재검증 가능한 최소 증거만 보존한다.
- 재현 가능한 중간 artifact/로그는 local evidence cache에서 TTL 후 정리한다.
- FAIL 분석에 필요한 최소 증거와 DEPLOYED_PASS 최종 증거만 장기 보존한다.
- 대형 로그/영상/스크린샷은 Git commit에 상시 누적 금지.

## 충돌 방지
- Strict state machine: PLAN → SOURCE_VERIFIED → EXTERNAL_EVIDENCE_VERIFIED → SANDBOX_PASS → INTEGRATION_PASS → REGRESSION_PASS → REMOTE_VERIFIED → DEPLOYED → DEPLOYED_PASS
- Single Writer: 동일 repo/file/MASTER 동시 write 금지.
- Lock Scheduler: 충돌 write 자동 직렬화.
- Immutable Receipt: 기존 receipt 수정 금지, 새 receipt append.
- Interpretation Gate: 동일 REQUIREMENT_ID를 독립 해석 2개로 비교; 불일치 시 canonical requirement/제3 auditor로 수렴하기 전 실행 금지.
- 각 층은 다른 층의 내부상태를 직접 수정하지 않고 receipt/state transition만 전달.
- receipt chain의 PREVIOUS_RECEIPT_SHA256가 끊기거나 순서가 뒤바뀌면 다음 단계 차단.
- verifier disagreement 발생 시 다수결로 강행하지 않고 `VERIFICATION_CONFLICT`로 격리 후 독립 외부근거로 수렴.

## TOOL043 관찰자 상태
43번은 다음 최소 상태를 관찰자가 쉽게 볼 수 있게 한다.
- RUNNING
- VERIFYING
- DEPLOYING
- DEPLOYED_PASS
- WORK_EXCEPTION_READY
- WAITING_EXTERNAL
- STALLED
- VERIFICATION_CONFLICT
- LAST_SAFE_CHECKPOINT

일정 heartbeat/receipt 진행이 없으면 `STALLED`로 바꾸고, 마지막 실제 receipt/state와 원인을 표시한다. 사용자가 수리·로그복사·재실행을 하지 않는다.

## Work 사용 게이트
Work는 처음부터 끝까지 한 번에 닫을 수 있는 범위만 시작한다.
착수 전 반드시:
1. 기존 PASS/SKIP_REUSE 확인
2. 실제 TOOL043 canonical/실사용 배포경로 확인
3. TOOL044 기존 mechanical/local-first/fast-deploy 재사용
4. 외부 검증부품 후보를 bounded search
5. 외부근거 quorum을 확보할 수 있는지 확인
6. 원인/범위/EXPECTED 고정
7. 배포본 재시험까지 가능한지 확인

중간 산출물만 만들고 다음 Work로 넘기는 방식 금지.
동일 실패방법 반복 금지.
현재 Work 한 번에 DEPLOYED_PASS 가능성이 낮으면 코드를 변경하지 않고 `NO_START_ONE_RUN_NOT_CONFIDENT`로 종료한다.

## 한 번의 실행 목표
1. MASTER/checkpoint/TOOL044 existing PASS 로드
2. TOOL043 현 배포본 read-back/actual-use 경로 확인
3. provenance/receipt 외부 검증부품 후보 조달
4. 각 후보의 공식 upstream/registry/release/signature/attestation 외부근거를 독립 조회
5. identity/version/digest external evidence quorum 검증
6. sandbox 검증
7. receipt-chain 최소 구현/연결
8. 외부 verifier native output과 receipt 연결
9. TOOL043에 provenance/receipt/WORK_EXCEPTION/STALLED 상태 최소 표시 또는 status JSON 연결
10. 실제 기능/회귀시험
11. GitHub commit/push/read-back
12. 실제 TOOL044/TOOL043 폴더 배포
13. 배포본 동일 입력 재시험
14. final receipt chain + external evidence quorum 재검증
15. DEPLOYED_PASS
16. SAFE_CHECKPOINT + VERIFIED_COMPONENT_REGISTRY 등록

## 완료조건
아래 전부 없으면 COMPLETE 금지:
- 외부부품 provenance 증거
- 외부 공식기록 2개 이상 교차일치 또는 cryptographic attestation + 독립 digest 일치
- 외부에서 가져온 independent verifier PASS
- receipt 값과 외부 공식기록 MATCH
- actual input/function PASS
- impacted regression PASS
- remote read-back PASS
- actual-use deploy PASS
- deployed-copy retest PASS
- final receipt chain validation PASS
- TOOL043에서 현재 상태/중단/마지막 checkpoint 관찰 가능

이번 파일 생성/수정은 계획 정본이며 실제 Windows 배포 완료를 의미하지 않는다.
