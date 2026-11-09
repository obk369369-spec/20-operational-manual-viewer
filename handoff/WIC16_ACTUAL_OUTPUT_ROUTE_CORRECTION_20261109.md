# WIC16 실제 업무 산출물 우선 — 실행 경로 정정 (2026-11-09)

## 새 검증 증거
- 2026-11-09 14:08~14:09 KST Work 결과: 신규 WIC 업무 실행 0, 산출물 0, 활성 진행 작업 없음. 승인/원본 검증 영수증 없음.
- GitHub의 실제 `feedback_pipeline/wic_24h_tools_revenue_cycle.py` 코드 직접 조회 결과:
  - `build_result()`가 `discover_platforms()`를 호출.
  - `discover_platforms()`가 `https://api.github.com/search/repositories?q=workflow+automation+archived%3Afalse...` 후보를 페이지 단위로 반복 탐색.
  - 결과는 플랫폼 후보 목록, URL 접속 상태, 파일 `public/revenue-lab/state.json`, `feedback_pipeline/evidence/wic_24h_tools_revenue_cycle.json`.
  - 실제 고객/보고서/문서 등 WIC 업무 원본을 처리해 최종 WIC 결과물을 만드는 실행 계약으로 보기 어려움.
- 기존 workflow `.github/workflows/wic-24h-tools-revenue-cycle.yml`는 선행 승인에서 실패. Run https://github.com/obk369369-spec/20-operational-manual-viewer/actions/runs/42458926533 .

## 즉시 정정 — 기존 목표의 구체화
1. `wic-24h-tools-revenue-cycle`은 **신규 WIC 업무 산출물 확보의 실행 대상으로 사용하지 않음**. 승인 없고, 실행 계약도 목표 불일치. 기존 코드를 삭제·변경하거나 안전 게이트를 우회하지 않음.
2. **이전 지시의 “승인만 받아 24시간 revenue cycle을 재실행”을 폐기**. 승인/증거를 만들어도 목표 달성 아님.
3. 기존 GitHub 내 이미 구현된 WIC 업무 도구 중 **실제 입력·출력 계약, 실증 예제, 검증기, 실행 허용 증거**가 함께 존재하는 단일 업무 경로를 먼저 선정한다. 이미 조사된 작업 명부/상태를 우선 활용; 새 도구·새 코드·새 외부 후보 검색 금지.
4. 해당 기존 업무 경로에서 정상 승인 범위 내 **실제 입력→처리→출력→GitHub 저장→별도 재조회**를 수행한다. 고객 개인정보 및 거래/결제 작업은 승인 없이 사용하지 않음.
5. 실행 가능 WIC 업무 경로가 없으면 대상별 구체 원인만 HOLD 기록. 추상 플랫폼 후보 탐색으로 대체하거나 테스트/상태 보고를 업무 성과로 계산하지 않음.
6. 외부 무료 실행층의 분산 운영은 실물 WIC 업무 경로 확인 뒤 기존 연결 자산으로만 이어서 검증한다.

## 다음 Work 실행 지시 — 최초 미완료 단계에서 재개
- 기준 중앙 저장소: `obk369369-spec/20-operational-manual-viewer`.
- 읽기 기준: 이 파일, `handoff/WIC16_ADMISSION_ROOT_CAUSE_20261109.md`, `feedback_pipeline/wic_target_registry.json` 및 기존 검증 증거.
- **딱 한 개의 기존 WIC 업무 도구**를 원본·검증기·허용 게이트가 맞는 것으로 선정한 뒤, 실제 산출물 1건을 성공시키고 증거 URL을 남긴다.
- 적합한 기존 도구가 없다면 HOLD. 비슷한 검색/재감사/승인값 조작 금지.
- Work 크레딧은 사용자 2026-11-09 명시 허용에 따라 이번 실행에 한해 사용 가능. **최종 24시간 무료 독립 운영은 Work/Codex 크레딧 없이 구현**되어야 함.

## 상태
- 실제 완료: GitHub 처리기 코드·실행 계약 불일치 확인 및 본 정정 증거 커밋.
- 진행 중: 최초 실제 산출물의 기존 WIC 업무 경로 선별.
- 아직 실행하지 않음: 실제 WIC 업무 산출물 1건, 외부 무료 플랫폼 연계, 24시간 검증.
- HOLD: 기존 revenue cycle 재실행(원본 승인 증거 없음 + 목적 불일치).
