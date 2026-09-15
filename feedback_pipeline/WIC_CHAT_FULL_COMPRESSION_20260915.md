# WIC 채팅창 전체 압축본 — 2026-09-15

목적: Work에 들어가기 전에 채팅창에서 해야 할 조사·판단·중복제거·우선순위·완료조건을 한 번에 끝낸다. 사용자는 관찰자이며 중간 `계속`, 수동전달, 재설명, 복사/붙여넣기, PASS/HOLD 판단을 하지 않는다.

## 공통 강제규칙
- 기존 PASS/REMOTE_VERIFIED는 증거가 살아 있으면 SKIP_REUSE.
- 같은 원인은 ROOT 하나로 합치고 occurrence/source는 보존.
- 코드/문서/후보 발견만으로 완료 금지. 실제 실행·시험·배포·remote read-back이 필요한 항목은 그 증거까지 있어야 PASS.
- 외부 증거/기기/권한이 진짜 없으면 억지 개발하지 않고 HOLD_EXTERNAL 또는 NO_READY_COMPONENT.
- TOOL044는 외부의 이미 완성·검증된 부품만 무수정 장착한다. 내부 신규개발·커스터마이즈·확장 금지.
- USER_WORK=0 / USER_MANUAL_RELAY=0.
- 전체 repo/Library 재전수조사 금지. 이미 확보한 정본/ledger/checkpoint/evidence를 먼저 사용하고 필요한 범위만 좁게 추가 조회.

# 1회차 — TOOL044 23건 막힘 제거
현재 원본: tool044_atomic_watch_state의 28건 중 DUPLICATE_SEARCH_BLOCKED 23건.

채팅 판단 완료:
1. 23건을 새 지시문으로 재투입하지 않는다. Issue #23에서 원래 23건 대신 일반 3건으로 바뀌는 router 문제가 확인됨.
2. 원래 demand_id 23개를 고정 원본으로 사용.
3. 각 건은 정확히 하나로 분류:
   - VERIFIED_COMPONENT_REUSE: 현재 검증창고에 기능 존재 → 재검색 금지, 즉시 재사용.
   - TRUE_MISSING_COMPONENT: 검증창고에 실제 없음 → 외부 완성부품만 검색/검증.
   - TOOL_LOCAL_OR_EVIDENCE_GATE: 외부부품 문제가 아니라 대상도구 규칙/배포/증거/연결 문제 → 대상 회차로 보냄.
4. 24시간 backoff는 외부 재검색만 막아야 하며 demand 자체의 현재 matched/missing/classification을 숨기면 안 됨.
5. 기존 확인 재사용 부품: WIC_MANIFESTED_ASSET_PROVENANCE_GATE, HTML2TEXT_2025_4_15_WEBPAGE_TEXT_EXTRACTION, MISTUNE_3_3_4_TOC_STRUCTURE_EXTRACTION, DOIT_0_37_0_LOCAL_DAG_EXECUTION_ENGINE.
6. TRUE_MISSING은 실제 외부검증 또는 NO_READY_COMPONENT까지.
7. 완료: 23/23 분류 + 각 결과 evidence + TOOL016 귀환 ACK + remote read-back.

# 2회차 — TOOL044 자동 장착·실패복구
기존 완료 재사용:
- TOOL043 대상으로 fastjsonschema 실제 생산 장착/비교/회귀/배포/read-back 완료 기록 존재.
- TOOL013 대상으로 idb-keyval 6.2.2 무수정 장착, 실제 XLSX/대형 resume 비교, 배포 E2E 완료 기록 존재.
따라서 새 장착엔진을 처음부터 다시 만들지 않는다.

남은 일:
- 위 검증된 생산 패턴을 새 admitted target에 재사용할 수 있게 일반 적용 gate를 검증.
- 장착 전 snapshot → 장착 → 실제 target test → 실패 시 자동 원복 → 원복 후 재시험 → 성공 시 deployed-copy test.
- 임의 도구에 안전하게 적용할 수 없으면 ARBITRARY_WIC_DEPLOY를 PASS로 위장하지 않고 정확한 제한/HOLD를 남김.
완료: 성공 fixture 1 + 실패/rollback fixture 1 + deployed-copy read-back.

# 3회차 — 전체 폐루프 한 바퀴
이미 PASS 재사용: Issue #16/#22 계열에서 TOOL016→TOOL044 전달, result return, central ACK, remote read-back 경로는 재개발 금지.
남은 실제 검증:
오류입력 → 기존 ROOT 조회/중복병합 → TOOL016 → TOOL044 → 기존부품 재사용 또는 진짜 missing 처리 → 장착 → target 실제시험 → 배포 → TOOL016 결과귀환 → remote read-back.
완료: 한 개의 실제 신규/재발 오류가 사용자 수동전달 없이 끝까지 한 바퀴.

# 4회차 — TOOL044 대형공장
현재 worker는 schedule + workflow_dispatch, self-test, request decomposition, lineage, full accessible sweep, external harvest, parallel discovery, checkpoint 저장 구조가 이미 존재. 재작성 금지.
남은 일:
- 여러 atomic demand 병렬처리.
- 하나 실패해도 다른 demand 진행.
- checkpoint/restart-resume.
- 이미 검증된 부품은 검색하지 않음.
- 자연 scheduled run에서 실제 상태 갱신.
완료: 혼합 성공/실패 묶음에서도 나머지 계속 처리 + 재시작 후 이어짐 + remote checkpoint.

# 5회차 — 과거/현재 오류 전체 합치기
TOOL045는 재추출 금지.
확인 정본:
- processed conversations/files: 283
- unprocessed: 0
- occurrences: 171,910
- root candidates: 315
- asset: TOOL045_WIC_1year_error_feedback_asset.zip
- asset library file id: file_00000000f9c88209a870055c3c8ed817
- sha256: 6bc87e9cadd9903c773c163b29e3f2e6198239dce3e99316eaa43f7106cc41fd

합칠 입력:
TOOL045 기존 정본 + 사용자가 준비한 오류 ZIP + TOOL016 root/open ledger + 오늘 신규 오류 + 앞으로 들어오는 오류.
규칙: 같은 ROOT는 합치되 occurrence/source/time/evidence는 보존. VERIFIED_CLOSED는 증거 유효 시 재개 금지. 수정됐지만 최종검증 없으면 OPEN.
완료: 새 전수추출 없이 unified ledger 갱신 + 누락/중복 검사.

# 6회차 — 앞으로 오류 자동수집
기존 receiver/16→44 길은 재사용.
플랫폼 한계: 일반 ChatGPT 대화 자체에서 자동으로 외부 repository_dispatch를 쏘는 source-side producer는 현재 증거상 HOLD_SOURCE_MESSAGE_EVENT_PRODUCER_UNAVAILABLE. 이 한계를 내부 코드 완료로 위장 금지.
실행 가능한 부분:
- source/tool identity가 들어온 이벤트는 자동 ROOT 조회/병합/16→44.
- GitHub/Library에 보존된 해당 TOOL 기록을 scoped retrieval하여 사용자가 과거 설명을 반복하지 않게 함.
- L4-12/L4-13 및 cross-chat retrieval의 기존 PASS 증거는 SKIP_REUSE하고 재발만 검사.
완료: 가능한 자동구간 실제 E2E + 플랫폼 한계 별도 HOLD. 사용자 수동배달을 내부 해결 완료로 위장 금지.

# 7회차 — 고객업무 TOOL041/042/007/034 묶음
기존 완료는 재사용. 중앙 기록상 TOOL042 일부 actual/expected gate와 TOOL007 fixture PASS가 존재.
현재 핵심 잔여:
- TOOL041 기존 267명은 HOLD_REVALIDATION_REQUIRED 범위가 있어 현재 재직/부서/연락처 근거 재검증 필요.
- TOOL041/042 native preflight/dedicated MVP 뼈대는 존재하지만 실제 인증환경 + 실제 고객 E2E가 미완료.
- 오늘 TOOL042 반복오류: PRE_READ_SOURCE_LOCK, official source only, TOC extraction/completeness, official publisher/domain, official detail page, reseller detection, TOC hierarchy, 고객 과거 발송/구매/문의와 outbound-only 구분, 최근 발송 중복회피, 한글 타이틀, 고정 안내형식.
- 외부 실제 고객/발행사 증거가 없는 것은 HOLD_EVIDENCE_WAITING으로 분리.
완료: 대표 실제 고객 1~2명으로 current identity/history/material/source lock/recommendation/output 전체 E2E 후 같은 ROOT에 대량 적용.

# 8회차 — TOOL006/TOOL013 등 핵심도구
TOOL006:
- 기존 PASS는 SKIP_REUSE.
- 남은 publisher golden pair는 실제 pair가 없으면 HOLD-T6-PUBLISHER-GOLDEN-PAIR 유지.
- TOC 고질 오류는 source lock/번호계층/완전성/중복/known-error fixture로 묶음.

TOOL013:
- idb-keyval checkpoint-cache pilot은 REMOTE_VERIFIED, 재설치 금지.
- 남은 다수 Excel 연속처리/재개/중복/필드 누락·이동/카테고리 정합/제목 번역을 같은 ROOT끼리 묶음.
- 번역은 모델 라이선스/runtime 증거 없으면 HOLD를 PASS로 위장하지 않음.
완료: 실제 파일 fixture로 대표 실패 재현→수정→대량/재개/중복 회귀.

# 9회차 — 나머지 도구 + 사용자 수작업 제거
전체 canonical tool에서 다음을 찾아 같은 원인으로 합침:
- 복사/붙여넣기 요구
- 파일 하나씩 업로드
- 같은 고객/도구 정보 재입력
- 사용자가 16↔44 전달
- 사용자가 PASS/HOLD 판정
- 중간 승인 반복
- 과거 대화 다시 설명
플랫폼상 불가피한 실제 기기 조작 등은 마지막 한 번으로 묶고 PLATFORM_LIMIT로 분리.
완료: 내부 실행 가능한 수작업 0, hidden_manual_work 0, observer_repetition 0.

# 10회차 — 새 대화창 상태복구
기존 L4-12/L4-13/L4 audit PASS는 SKIP_REUSE.
새로 확인할 것은 재발 여부와 실제 TOOL별 scoped retrieval.
순서: TOOL 번호/업무 식별 → target master/checkpoint/handoff/GitHub evidence → 필요 시 해당 Library 보존 기록만 검색 → 마지막 작업점 복구.
전체 Library/전체 대화 재검색 금지.
완료: TOOL002 대표사례 + 다른 canonical TOOL 1건에서 사용자가 과거 내용을 다시 말하지 않고 마지막 작업점 회수.

# 11회차 — 과거 찌꺼기/HOLD 정리
unified_open_ledger, root ledger, next work queue, checkpoints를 대조.
분류:
- VERIFIED_CLOSED/REMOTE_VERIFIED → SKIP_REUSE
- 외부 증거 기다림 → HOLD_EXTERNAL/EVIDENCE_WAITING
- 내부 실행 가능 → OPEN
- 조건이 같은 반복검색 → STOP_REPEAT
- 오래된 잘못된 완료표시 → 상태 교정
특히 현재 중앙 open queue의 TOOL001 actual 5 payload, publisher golden pair, ChatGPT source producer, T41/T42 real auth/customer E2E를 서로 섞지 않는다.
완료: stale/duplicate/contradictory state 0 또는 근거 있는 HOLD만 남김.

# 12회차 — TOOL043/044 실제 화면/기기 검증
현재 work16 queue의 P0 L6-20은 TOOL043 actual Android screen-off/background/state-change/persistent-sync/screen-on/state-restore 증거.
기존 fail-closed contract/CI는 재검사 금지.
실제 Android 기기 증거가 없으면 HOLD_EXTERNAL_DEVICE_EVIDENCE.
TOOL043/044 화면은 실제 접근, 상태표시, 버튼/행동, 데이터갱신, 오류/빈화면, 재접속/복원, backend 결과 일치를 검사.
완료: 실제 화면/기기 증거가 있는 부분만 PASS. 나머지는 정확한 HOLD.

# 13회차 — ZERO SCAN 최종검사
전 회차 결과를 다시 처음부터 대조:
- unresolved internal error
- 끊어진 16↔44/result return
- 검증 없이 PASS
- deployed-copy 미검사
- stale HOLD
- duplicate ROOT
- missing source/evidence
- 사용자 수작업/재설명
- 자연 scheduled run 미확인
- 새 대화창 복구 실패
- 실제 화면/기기 증거 위장
0인지 검사.
완료: 내부 실행 가능한 항목 0, 남는 것은 이름/이유/다음 trigger가 명확한 외부 HOLD만. 최종 GitHub remote read-back + SAFE_CHECKPOINT.

# Work 압축 실행 묶음 — 채팅 판단 완료 후
13회차를 13번 따로 실행하지 않는다. 의존성 기준으로 크게 압축한다.

## WORK-BATCH-A — 1~4회차
TOOL044 23건 재분류/실제 missing 검증 → 재사용 → 자동장착/rollback → 폐루프 → 병렬/재시작/자연실행.
A가 통과해야 다음 대량수리에 44번을 사용.

## WORK-BATCH-B — 5~6회차
기존 TOOL045 정본 + ZIP + TOOL016 + 신규 오류 통합/dedup + 가능한 자동수집 경로 검증. 1년치 재추출 금지.

## WORK-BATCH-C — 7~9회차
고객업무 + TOOL006/013 + 나머지 도구의 실제 unresolved ROOT를 우선순위대로 대량수리. 기존 PASS는 재사용. 외부 증거 HOLD는 건드리지 않음.

## WORK-BATCH-D — 10~13회차
상태복구 → stale/HOLD 정리 → 실제 화면/기기 검증 → ZERO SCAN/최종 read-back.

# Work에 넘기기 전 마지막 검사표
- 13회차 모두 채팅 판단 존재: YES
- TOOL045 재추출 금지: YES
- 기존 검증부품/완료작업 재사용: YES
- Issue #23 일반 3건으로 원래 23건 대체 금지: YES
- 외부 증거 없는 것을 내부개발로 위장 금지: YES
- 사용자 중간 `계속`/수동전달 요구 금지: YES
- Work는 조사부터 다시 하지 않고 이 압축본 + 최신 remote state의 DIFF만 실행: YES
- 각 Batch 종료 후 전체 read-back, 실패는 다음 Batch로 숨기지 않고 같은 Batch에서 가능한 만큼 수정/재시험: YES

CHAT_SIDE_STATUS = COMPLETE_FOR_WORK_HANDOFF
WORK_EXECUTION_STATUS = NOT_STARTED
