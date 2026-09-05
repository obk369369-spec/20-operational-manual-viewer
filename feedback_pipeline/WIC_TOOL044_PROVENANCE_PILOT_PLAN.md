# TOOL044 Provenance Pilot Plan

상태: READY_FOR_ONE_RUN_WORK / NOT_DEPLOYED

## 목적
TOOL044를 `외부부품 진위증명 → 조달 → 조합 → 독립검증 → 배포` 공통계층으로 확장하고, 첫 실증대상으로 TOOL043의 최소 관찰자/증거연결 범위를 사용해 한 번의 Work 실행에서 DEPLOYED_PASS까지 닫는다.

## 첫 대상 선정
- TOOL041/042는 다중 구조와 반복실패 이력 때문에 첫 실증에서 제외.
- TOOL043은 기존 TOOL044 적용 어댑터와 실제 DEPLOYED_PASS 증거가 이미 있어 기존 PASS를 SKIP_REUSE하면서 provenance/receipt 계층만 증분 확장할 수 있으므로 ONE_RUN_DEPLOYABLE 가능성이 가장 높다.
- TOOL043 전체 24시간 자율실행을 이번 범위에 포함하지 않는다. 이번 실증은 `외부부품 진위증명 + receipt chain + 독립검증 + 43번 관찰표시/증거연결 + 저장소/실사용 배포본 재검증`만 닫는다.

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
- EVIDENCE_LOCATION
- NEXT_ALLOWED_STATE

## 외부부품 진위 게이트
`NO_PROVENANCE = NOT_EXTERNAL_COMPONENT`
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

TOOL044 무수정 부품은 원칙적으로 `UPSTREAM_HASH = SANDBOX_HASH = INTEGRATED_HASH = DEPLOYED_HASH`여야 한다. 불일치 시 REJECT.

## 독립 검증 구조
- Producer: 결과 생성. 자기 PASS 확정 금지.
- Attestor/Verifier A: provenance/identity/digest 검증.
- Functional Verifier B: 실제 입력/기능/EXPECTED↔ACTUAL 검증.
- Deployment Verifier C: 저장소 read-back 및 배포본 digest/E2E 검증.
- A/B/C가 같은 자체 생성 코드 하나를 공유해 자기검증하지 않도록 외부 검증도구/서로 다른 검증 경로를 TOOL044로 우선 조달한다.
- receipt 발행자는 자기 receipt를 최종 검증하지 못한다.

## 외부 검증부품 후보 원칙
새 자체 검증기를 먼저 만들지 않는다. TOOL044가 아래 계열을 후보로 조사하되 실제 채택은 라이선스/유지보수/무수정 사용/sandbox PASS 후에만 한다.
- in-toto 계열 supply-chain layout/link 검증
- Sigstore/cosign 계열 signature/attestation 검증
- 투명 로그가 적합한 비민감 artifact에 한해 Rekor 계열
- pytest/Playwright 등 독립 functional/E2E verifier
- Git/hash/read-back verifier
유료 SaaS/API 의존은 기본 차단한다.

## 저장용량 최소화
GitHub에는 receipt/manifest/hash/서명 참조만 저장한다.
- 같은 artifact는 SHA256 content-addressed 방식으로 한 번만 참조.
- 재현 가능한 중간 artifact/로그는 local evidence cache에서 TTL 후 정리.
- FAIL 분석에 필요한 최소 증거와 DEPLOYED_PASS 최종 증거만 장기 보존.
- 대형 로그/영상/스크린샷은 Git commit에 상시 누적 금지.

## 충돌 방지
- Strict state machine: PLAN → SOURCE_VERIFIED → SANDBOX_PASS → INTEGRATION_PASS → REGRESSION_PASS → REMOTE_VERIFIED → DEPLOYED → DEPLOYED_PASS
- Single Writer: 동일 repo/file/MASTER 동시 write 금지.
- Lock Scheduler: 충돌 write 자동 직렬화.
- Immutable Receipt: 기존 receipt 수정 금지, 새 receipt append.
- Interpretation Gate: 동일 REQUIREMENT_ID를 독립 해석 2개로 비교; 불일치 시 실행 중단 후 canonical requirement/제3 auditor로 수렴.
- 각 층은 다른 층의 내부상태를 직접 수정하지 않고 receipt/state transition만 전달.

## Work 사용 게이트
Work는 처음부터 끝까지 한 번에 닫을 수 있는 범위만 시작한다.
착수 전 반드시:
1. 기존 PASS/SKIP_REUSE 확인
2. 실제 TOOL043 canonical/실사용 배포경로 확인
3. TOOL044 기존 mechanical/local-first/fast-deploy 재사용
4. 외부 검증부품 후보를 bounded search
5. 원인/범위/EXPECTED 고정
6. 배포본 재시험까지 가능한지 확인

중간 산출물만 만들고 다음 Work로 넘기는 방식 금지.
동일 실패방법 반복 금지.

## 한 번의 실행 목표
1. MASTER/checkpoint/TOOL044 existing PASS 로드
2. TOOL043 현 배포본 read-back/actual-use 경로 확인
3. provenance/receipt 외부 검증부품 후보 조달
4. upstream/digest/license 검증
5. sandbox 검증
6. receipt-chain 최소 구현/연결
7. TOOL043에 provenance 상태를 최소 표시 또는 status JSON 연결
8. 실제 기능/회귀시험
9. GitHub commit/push/read-back
10. 실제 TOOL044/TOOL043 폴더 배포
11. 배포본 동일 입력 재시험
12. DEPLOYED_PASS
13. SAFE_CHECKPOINT + VERIFIED_COMPONENT_REGISTRY 등록

## 완료조건
아래 전부 없으면 COMPLETE 금지:
- 외부부품 provenance 증거
- independent verifier PASS
- actual input/function PASS
- impacted regression PASS
- remote read-back PASS
- actual-use deploy PASS
- deployed-copy retest PASS
- final receipt chain validation PASS

이번 파일 생성은 계획 정본이며 실제 Windows 배포 완료를 의미하지 않는다.
