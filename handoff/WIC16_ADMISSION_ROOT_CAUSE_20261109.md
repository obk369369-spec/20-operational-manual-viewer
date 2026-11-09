# WIC16 승인 차단 원인 — 실제 GitHub 코드·실행 증거 (2026-11-09)

## 실측
- 기존 실행: https://github.com/obk369369-spec/20-operational-manual-viewer/actions/runs/42458926533
- job 128663813959: Enforce central admission and user stop before work = failure; actual A-L cycle, validation, persistence, Pages = skipped; artifacts 0.
- 실행 당시 로그의 WIC_USER_STOP, WIC_RULE_ADMISSION_JSON 모두 빈 값. USER_STOP_OR_START_BLOCKED.
- 사용자 후속 설정 주장(WIC_USER_STOP=0)은 이 과거 실행 로그로 확인할 수 없으며, 현재 repo 변수 조회 권한 없음.

## 기존 코드로 확인한 정확한 승인 계약
- .github/workflows/wic-24h-tools-revenue-cycle.yml: --work-id workflow:wic-24h-tools-revenue-cycle --task-id CENTRAL
- CONTROL_TOWER/controller/pre_work_admission.py: WIC_USER_STOP == '0' 필수. WIC_RULE_ADMISSION_JSON에서 work_id별 admission 추출.
- CONTROL_TOWER/controller/runtime_progress_gate.py: verify_work_admission은 정확한 work_id/task_id, 현재 규칙 본문·해시, 실제 원본 증거 경로 및 SHA256, 독립 검증 source_receipt(validation_result PASS, source_records_verified true, validator_id, source_refs), 규칙 버전 일치, 검증 계획을 요구.
- feedback_pipeline/approval_queue.json: TOOL043_SAFE_REMOTE_FINALIZE 과거 완료 기록만 존재; 본 workflow의 admission 아님.

## 결정
1. 기존 승인·검증 증거 없이 WIC_RULE_ADMISSION_JSON을 임의 생성하거나 STOP 게이트를 제거하지 않는다.
2. 동일 실패 workflow 재실행 금지. 상태 감시 성공을 실제 업무 성공으로 계산하지 않는다.
3. 승인 영수증을 만들려면 **실제 원본 및 독립 검증 결과**가 먼저 필요하다. 임의 PASS/해시 금지.
4. 기존 GitHub 연결 도구로 Actions 변수 변경 및 워크플로 수동 dispatch가 불가능한 한, 도구 권한 제한을 사실대로 보고한다.
5. 다음 실질 실행: 승인 대상 원본·독립 검증 결과가 실제로 있는 범위에서만 승인 연결; 그렇지 않으면 해당 lane HOLD, 승인 불필요한 기존 독립 lane의 실제 산출물에 집중한다.

## 상태
- 실제 완료: 기존 실패 run/job/steps 및 승인 계약 코드 확인, GitHub 기록.
- HOLD: 업무별 원본 검증 영수증 부재 및 현재 변수 확인/설정 권한 부재.
- 미완료: 업무 실행, WIC 실물 결과, 24시간 검증.
