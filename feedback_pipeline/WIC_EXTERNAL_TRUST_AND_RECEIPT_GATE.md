# WIC EXTERNAL TRUST AND RECEIPT GATE

상태: ACTIVE DESIGN GATE / NOT_DEPLOYED
적용범위: TOOL044뿐 아니라 모든 WIC 도구·프로그램·대화기반 실행체계·검증층·자가복구층·배포층·향후 신규 층 전체.

## 1. 최상위 원칙
- AI/WIC가 스스로 작성한 `공식 출처`, `버전`, `hash`, `PASS`, `서명 참조` 텍스트는 그 자체로 증거가 아니다.
- 외부부품·외부검증도구·외부실행기는 독립된 외부 공식 기록을 기계적으로 조회하여 서로 대조해야 한다.
- 외부 공식 기록을 직접 변경할 권한이 없는 독립 source에서 검증한다.
- 하나의 URL만으로 외부 진위를 인정하지 않는다.
- `NO_EXTERNAL_EVIDENCE = NO_TRUST`
- `SELF_REPORTED_PROVENANCE = NOT_PROVENANCE`
- `SELF_ATTESTED_PASS = FORBIDDEN`

## 2. 외부 증거 Quorum
각 외부 component/validator/runner는 아래 중 최소 2개 독립 근거가 identity/version/digest를 동일하게 지지해야 한다. 단 하나의 강한 cryptographic attestation이 있을 때도 실제 artifact digest 재계산은 별도로 수행한다.

후보 근거:
- 공식 package registry metadata
- 공식 upstream repository release/tag/commit
- 공식 release asset digest/checksum
- maintainer/publisher signature
- Sigstore/cosign verification bundle
- Rekor transparency log inclusion proof
- GitHub artifact attestation 또는 다른 외부 signed provenance
- 실제 다운로드한 artifact의 독립 SHA256 재계산

WIC/GitHub 내부 receipt의 자기기입값은 quorum의 외부근거 개수에 포함하지 않는다.

## 3. 검증 영수증(receipt)
각 층은 작업 후 작은 immutable JSON receipt를 append-only로 발행한다.
필수 최소 필드:
- TASK_ID / REQUIREMENT_ID / LAYER_ID
- INPUT_SOURCE / INPUT_SHA256
- EXECUTOR / COMPONENT_ID / VERSION
- EXTERNAL_SOURCE_REFS[]
- EXTERNAL_ATTESTATION_REFS[]
- UPSTREAM_ARTIFACT_SHA256
- ACTUAL_SHA256
- PREVIOUS_RECEIPT_SHA256
- RESULT
- NATIVE_VERIFIER_OUTPUT_REF
- NEXT_ALLOWED_STATE

receipt 필드 값은 외부 verifier가 다시 조회·검증하기 전까지 `UNVERIFIED_CLAIM`이다.

## 4. 검증자 독립성
- Producer는 자기 결과를 FINAL PASS 처리하지 못한다.
- Provenance verifier, Functional verifier, Deployment verifier, Evidence-quorum verifier는 역할을 분리한다.
- 핵심 validator는 WIC가 새로 작성해서 신뢰하지 않는다. 외부에서 실제 공유·사용·유지되는 검증도구를 TOOL044가 가져와 실제 sandbox 검증 후 사용한다.
- 외부 validator 자체도 upstream/release/license/digest/maintainer/usage evidence를 동일 방식으로 검증한다.
- validator A/B/C가 동일한 WIC 자체 코드 하나를 공유해 자기검증하는 구조는 FAIL이다.

## 5. 모든 층 공통 적용
사전시뮬레이션, 조달, 조합, 코딩 agent, 테스트, 감사, 자가복구, GitHub/저장소 반영, 배포, 배포본검증 등 모든 층은 다음 상태전이만 사용한다.

`PLAN → SOURCE_VERIFIED → EXTERNAL_EVIDENCE_VERIFIED → SANDBOX_PASS → INTEGRATION_PASS → REGRESSION_PASS → REMOTE_VERIFIED → DEPLOYED → DEPLOYED_PASS`

앞 단계 receipt와 external evidence가 없으면 다음 단계로 이동하지 못한다.

## 6. 충돌·꼬임 방지
- Single Writer: 동일 repo/file/MASTER 동시 write 금지
- Lock Scheduler: 충돌 write 자동 직렬화
- Immutable Receipt: 기존 receipt 수정 금지, 새 receipt append
- Receipt Hash Chain: PREVIOUS_RECEIPT_SHA256로 연속성 검증
- Interpretation Gate: 동일 REQUIREMENT_ID를 독립 해석 2개로 비교. 불일치 시 제3 auditor/canonical requirement로 수렴 전 실행 금지
- Verifier disagreement: 다수결 강행 금지. `VERIFICATION_CONFLICT`로 격리하고 외부근거로 수렴
- 각 층은 다른 층 내부상태 직접수정 금지. receipt/state transition만 전달

## 7. 저장용량 방화벽
- GitHub에는 receipt/manifest/hash/attestation reference만 장기 저장
- 같은 artifact는 content-addressed SHA256으로 한 번만 참조
- 대형 로그/영상/스크린샷/재현 가능한 중간 build는 Git commit 상시 누적 금지
- local evidence cache에 임시 보관 후 TTL 정리
- FAIL 원인 규명에 필수인 최소증거와 DEPLOYED_PASS 최종증거만 장기보존

## 8. 껍데기 차단
다음은 증거가 아니다:
- AI가 적은 공식 URL
- AI가 적은 hash
- WIC가 만든 PASS 문자열
- UI/버튼 존재
- 파일 생성
- commit 존재
- receipt 존재

진짜 증거는 외부 source 조회 + cryptographic/digest 검증 + 실제 기능시험 + 배포본 재검증이 일치한 chain이다.

## 9. 관찰자 보호
외부증거 누락, verifier 충돌, runner 고장, receipt chain 단절은 관찰자에게 수리를 전가하지 않는다.
시스템은 자동복구/다른 verifier/다른 runner/SAFE_CHECKPOINT 재개를 우선하고, 해결 불가하면 43번에 `STALLED / VERIFICATION_CONFLICT / WAITING_EXTERNAL` 상태와 마지막 정상 receipt만 표시한다.

## 10. 구현 경계
이 문서는 강제 설계게이트다. 이 문서 자체가 외부 validator 설치·검증·배포 완료를 뜻하지 않는다. 실제 채택은 TOOL044가 외부 component를 가져와 sandbox/independent verification/실사용 배포본 재검증을 통과해야 한다.
