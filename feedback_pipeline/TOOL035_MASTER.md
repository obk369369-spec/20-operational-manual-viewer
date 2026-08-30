# TOOL035 MASTER — 월드 운영시스템 통합

상태: ACTIVE / INCREMENTAL VERIFIED-INTEGRATION
기준일: 2026-08-30

WIC 공통 운영규칙은 `WIC_GLOBAL_OPERATING_RULES.md`를 먼저 로드한다. 이 문서는 TOOL035 고유 통합 계약만 보관한다.

## 1. 목적
- 기존 WIC TOOL에서 실제 PASS/VERIFIED된 기능만 최소 연결하여 운영 인계를 단순화한다.
- 새로운 거대 시스템이나 개별 TOOL 복제품을 만들지 않는다.
- 미완성/HOLD 기능을 연결 가능한 기능으로 승격하지 않는다.

## 2. 통합 순서
`검증된 개별 TOOL → 최소 연결 manifest → integration gate 실행 → FIRST_VALIDATION 1회 → PASS 범위만 유지`

## 3. 최초 연결 범위
- TOOL012 runtime commit `aa9cc2e89726a4b388b148067f6dc4be40a0599e`: 정적 서브사이트의 mailto/HTTPS 자료 CTA 생성 PASS.
- TOOL014 runtime commit `ae41bc0c93492d940df90049d894b19deab2ebaf`: 위험 CTA 차단 및 `WIC_SAFE_CHANGE autoDeploy=false` manifest 생성 PASS.
- 각 TOOL의 GitHub Pages 비활성/라이브 배포 HOLD는 그대로 보존하며 통합 완료로 오인하지 않는다.

## 4. 안전 계약
- manifest의 remote commit/blob read-back이 없는 구성요소는 READY에 포함하지 않는다.
- source TOOL 전체 상태와 재사용 가능한 PASS scope를 분리한다.
- 실제 자동배포, 라이브 홈페이지 변경, DB/API 연결은 현재 범위가 아니다.
- 실패 시 해당 연결만 HOLD하고 다른 검증된 TOOL 상태를 변경하지 않는다.

## 5. canonical
- 통합 상태: `feedback_pipeline/tool035_verified_integration.json`
- 실행 gate: `feedback_pipeline/tool035_verified_integration.py`
- 새 repo 생성 금지. CENTRAL 기존 저장소를 canonical로 사용한다.
