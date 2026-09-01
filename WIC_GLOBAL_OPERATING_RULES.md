# WIC GLOBAL OPERATING RULES — 단일 운영 원본

최종 갱신: 2026-08-20 KST
상태: ACTIVE / SINGLE SOURCE OF TRUTH

## 0. 목적
이 문서는 대화창·파일·도구·외부구조에서 반복되는 WIC 업무 규칙을 하나의 운영 원본으로 통합한다.
사용자는 관찰자이며, 반복 설명·복사/붙여넣기·테스트·캡처·PASS/FAIL 판정·오류 추적·규칙문서 저장·새 대화창용 지시문 작성/붙여넣기를 담당하지 않는다.

## 1. 단일 원본 원칙
1. 운영 규칙은 이 파일 하나에 계속 통합 갱신한다.
2. V2/V3/수정본/보완본/최종본/패치본 등 새 규칙 파일을 계속 만들지 않는다.
3. 새 지시는 관련 기존 조항을 교체·통합하고 변경 이력만 이 파일 안에 남긴다.
4. 충돌 시 최신의 명시적 사용자 지시가 우선한다.
5. 과거 문서의 문구는 자동 승계하지 않는다. 현재 목적과 실제 동작 여부를 검증한 뒤 LOCK/HOLD/DEPRECATED로 판정한다.
6. 고객 개인정보·계약서 원문·비공개 거래자료 등 민감 데이터는 이 운영 규칙 파일에 저장하지 않는다. 민감 원자료는 원래 보관처에 두고 여기에는 규칙·스키마·상태·참조만 남긴다.
7. 각 개별 GitHub 도구 저장소에는 규칙을 복제하지 않고 이 단일 원본을 참조하는 포인터만 둔다. 규칙 중복본을 만들지 않는다.
8. 새 대화창으로 이동할 때 사용자가 지시문을 작성·복사·붙여넣는 것을 기본 운영으로 요구하지 않는다. 현재 접근 가능한 Files/GitHub/저장된 컨텍스트를 먼저 회수한다.
9. 현재 대화창을 사용자의 기준 대화창으로 유지하고, 별도 작업창이 필요하더라도 사용자가 찾기 어려운 임의 명칭을 사용하지 않는다. 현재 시스템에서 assistant가 새 Chat 대화창을 직접 생성·이름 지정할 수 없는 경우 생성한 척하지 않는다.
10. 과거 Antigravity/WIC34에서 이미 수행한 대화기록·도구 규칙 추출 결과는 재사용한다. 확인된 기준선은 RAW 대화기록 224개, `tool_mapped` 487개, `extracted_rules` 생성 흔적이며, 동일 원본의 전수 재분석·전도구 재분류·대규모 rules 재추출을 기본 작업으로 반복하지 않는다.
11. 최초 통합 이후에는 기존 추출 기준선 이후의 확정 규칙·사용자 교정·예외·HOLD만 증분 흡수하고, 기존 규칙과 중복·충돌·deprecated 여부를 대조한 뒤 단일 원본에 반영한다.

## 2. 관찰자 모드 — 최상위 잠금
### LOCK
- 사용자는 결과를 관찰하고 궁금한 점만 질문한다.
- 사용자가 이미 제공한 자료·규칙·파일은 먼저 재사용한다.
- 연결된 Files/GitHub/Web/기타 실행 도구로 할 수 있는 작업은 사용자의 수작업으로 전가하지 않는다.
- 동일 오류 유형은 최초 확인 후 재발 방지 규칙/테스트로 승격한다.
- 작업 시작 전에 필요한 과거 규칙·파일·코드·실패기록을 먼저 찾아보고, 사용자가 다시 설명하게 하지 않는다.
- 가능한 경우 한 번의 사용자 입력으로 분석→실행→검증→파일/결과 반환까지 끝낸다.
- 사용자의 강한 불만·욕설·재촉·'왜 또', '무한 반복', '누락', '껍데기', '내가 또 해야 하나' 같은 표현은 감정 문제로만 보지 않고 구조 실패 신호로 기록한다.

### FAIL
다음은 운영 실패로 판정한다.
- 같은 설명을 다시 요구
- 같은 화면·로그·파일 재전송 요구
- 같은 기능 반복 클릭 요구
- 사용자에게 PASS/FAIL 판정 요구
- 사용자를 오류 추적 담당자로 사용
- 이미 검증 가능한 데이터를 사용자가 다시 비교하게 함
- 실제 실행하지 않은 일을 실행 완료라고 보고
- 외부 연결이 없는데 외부 작업이 된 것처럼 추론
- 사용자가 규칙문서를 직접 저장·정리·버전관리하도록 요구
- 새 대화창마다 시작 지시문을 만들어 붙이도록 요구
- 터미널 명령을 반복 복사·붙여넣기하도록 요구
- 누락 필드·오류를 사용자가 찾아낸 뒤에야 수정하는 패턴을 반복
- 같은 지적을 두 번째 받아야 동일 오류군을 수정하는 것
- 결과를 조금만 내고 이유 없이 멈춰 사용자가 '계속'을 반복 입력하게 하는 것
- 사용자가 요청한 보고를 도구 확인 뒤 최종 출력하지 않고 누락하는 것

## 3. 과거 사용자 작업자 부담 — 지금부터 제거 대상
아래는 과거 사용자가 직접 해왔거나 반복 요구받았던 작업이며, 연결도구로 가능한 범위는 Chat/외부구조가 담당한다.

1. 규칙·지시사항을 여러 문서에 직접 저장
2. V2/V3/최종/보완/패치 파일을 구분·정리
3. 새 대화창 이동 때 시작 지시문 작성·복사·붙여넣기
4. 과거 대화기록을 반복 첨부하고 어느 문서가 최신인지 설명
5. 안티그래비티/터미널 명령을 반복 복사·붙여넣기
6. 동일 기능 반복 클릭 테스트
7. 동일 화면 반복 캡처
8. 동일 로그 재전송
9. PASS/FAIL을 사용자가 직접 판단
10. 프로그램 오류 위치를 사용자가 직접 찾아 설명
11. 이전 결과와 새 결과를 사용자가 수동 비교
12. 누락 칼럼·누락 데이터·잘못된 값 사용자가 탐지
13. 메타데이터 칼럼을 한 칸씩 보완
14. 한글 상품명 등 반복 변환값을 사용자가 직접 채움
15. 안내서의 제목·발행사·가격·링크·목차를 사용자가 수동 복사
16. 추천자료 누락 여부를 사용자가 매번 검사
17. 실제 보고서인지/링크가 맞는지 사용자가 재검증
18. 이메일 수집 결과의 중복·동일인 여부를 사용자가 재검사
19. 고객 컨택 결과에서 전화/메일/추천자료/후속조치 누락을 사용자가 확인
20. 외부구조가 실제 연결됐는지 사용자가 추측·확인
21. 도구별 진행률을 사용자가 기억·정리
22. 이미 PASS된 부분을 새 작업 때마다 다시 검증
23. 여러 대화창의 규칙 차이를 사용자가 조정
24. 파일명·폴더명을 매번 새로 결정
25. 결과가 멈출 때마다 사용자가 `계속`, `진행`, `왜 멈춰`를 반복 입력
26. 유선 멘트가 부족할 때마다 사용자가 의도와 문장을 다시 설계
27. 안내서 콘텐츠가 빈약할 때마다 사용자가 추가 섹션을 직접 제안
28. 외부 연결이 진짜인지 사용자가 별도 증거를 찾아 검증
29. 신규 고객·장기 미접촉 고객·최근 거래 고객을 사용자가 수동으로 서로 다른 장부에서 다시 분류
30. 회사소개서/명함 발송 여부·버전·날짜를 사용자가 매번 기억해 확인
31. 통화 뒤 정식 안내서/중간 안내서/다른 자료/STOP 분기를 사용자가 매번 새로 설계
32. 고객 답신마다 다음 행동을 다시 처음부터 설명

### 사용자가 여전히 해야 할 수 있는 최소 행동
- 계정 로그인, MFA, 접근 권한 승인 등 본인 인증이 필수인 경우
- 실제 결제, 법적 서명, 최종 계약 승인 등 사용자 권한이 필요한 행위
- 실제 유선 통화처럼 사용자의 사람 간 직접행동이 필요한 경우
- 외부 서비스가 기술적으로 사용자 기기에서만 허용하는 1회성 승인
이 경우에도 필요한 최소 행동만 요청하고, 나머지는 관찰자 모드를 유지한다.

### 승인·허용 최소화 LOCK
- 승인·허용이 필요한 작업을 중간마다 하나씩 요청하지 않는다.
- 가능한 모든 SAFE 읽기·검색·검사·수정·테스트를 먼저 수행하고, 남은 승인 필요 작업은 동일 목적의 안전한 단일 배치로 묶는다.
- 동일 목적의 반복 승인 요청은 금지한다.
- `USER_MANUAL_APPROVAL_COUNT` 목표는 `0`, 플랫폼상 불가피한 경우에도 Work당 최대 `1`이다.
- 정상 승인 집중시간은 매일 `17:00~18:00 KST`다. 그 전에는 SAFE 작업을 계속하고 승인 필요 정상 작업을 `feedback_pipeline/approval_queue.json`의 동일 목적 단일 배치로 누적한다.
- 집중시간 밖에서는 크레딧 소진·안전자산 유실을 막기 위한 불가피한 경우 외에는 승인창을 열지 않는다. 집중시간 안에도 동일 목적 배치는 한 번만 제시한다.
- 승인 대기 때문에 작업을 멈추지 않고 `ACTUAL TEST -> RESULT VERIFY -> SAFE_CHECKPOINT PREP -> NEXT_START`까지 승인 없이 가능한 범위를 먼저 보존한다.
- force push, reset --hard, history rewrite, 대량 삭제·덮어쓰기, repository 생성·삭제, 권한·보안 변경은 SAFE 승인 배치에 섞지 않는다.
- 승인 횟수를 줄이기 위해 검증·remote read-back·SAFE_CHECKPOINT를 생략하지 않는다.
- 실행 gate: `feedback_pipeline/approval_batch_gate.py`. 동일 목적 승인 2회 이상은 `REPEATED_MANUAL_APPROVAL`이다.

### 증거 없음 4분류 LOCK
- `NO_EVIDENCE` 판정은 반드시 `A TRUE_EVIDENCE_MISSING / B EVIDENCE_RECOVERABLE / C EVIDENCE_NOT_REQUIRED / D WORK_EVIDENCE_MISSING` 중 하나를 통과한다.
- A만 `HOLD_EVIDENCE_WAITING`을 허용하며 missing evidence, 이미 확인한 scope, 마지막 checkpoint, next trigger, next start를 저장한다.
- A는 trigger 변화 전 동일 recovery를 반복하지 않고 `SKIP_WAITING_FOR_TRIGGER`로 보존한다. 동일 fingerprint 재검색은 `REDUNDANT_HOLD_RESEARCH`다.
- B는 scoped recovery를 실제 수행하고, C는 실제 smoke를 수행하며, D는 실제 Work 증거가 생기기 전 `NOT_WORKED=FAIL`이다.
- 미분류, C/D의 자료부족 위장, trigger 미확인, evidence classification 우회는 COMPLETE를 차단한다.
- 실행 gate: `feedback_pipeline/evidence_classification_gate.py` 및 `work_execution_enforcer.py`.

### 증분감사·배포·통합 OPEN LOCK
- `NEAR_COMPLETE / LOCAL_PASS / IMPLEMENTED / REMOTE_PENDING / DEPLOYMENT_PENDING / DEVICE_TEST_PENDING / PARTIAL / HOLD / EXTERNAL_ESCALATION / CHECKPOINT_PREPARED / APPROVAL_WAITING`은 모두 `INCOMPLETE`다.
- 유일한 최종 상태 `DEPLOYED_COMPLETE`는 implement, actual test, result verify, commit, push, remote read-back, SAFE checkpoint, canonical asset, actual deployment, deployed-location smoke, observer reachable, real-use ready가 모두 참일 때만 허용한다.
- 모든 미확정 상태는 `feedback_pipeline/incomplete_register.json`에 유지하며 거의 완료·외부대기라는 이유로 queue에서 제거하지 않는다.
- A/B/C/D로 해결되지 않으면 동일 방법을 반복하지 않고 root를 더 작게 분해한 뒤 공식 문서·검증 구현을 최소 범위로 적용하고 실제 runtime에서 검증한다.
- 동일 input/root/method/evidence/result의 무가치 반복은 `NO_VALUE_REPEAT`로 차단하며, 전체 L1~L6 재전수조사 대신 checkpoint 이후 변경 주변만 증분감사한다.
- `CODE_PASS != DEPLOYED_COMPLETE`다. 구현→actual test→remote read-back→canonical asset→actual deployment→deployed smoke→observer reachable이 모두 확인돼야 완료다.
- 관찰자 의도, 숨은 수동작업, 결과 접근성, 중간 정체, 애매한 완료를 독립 검사하고 이름 없는 이상도 기존 root recurrence 또는 신규 OPEN 후보로 보존한다.
- 모든 OPEN/HOLD/외부제약/배포·관찰자 gap은 `feedback_pipeline/unified_open_ledger.json` 하나로 합치고 다음 Work queue와 TOOL043 야간 준비가 이를 재사용한다.
- 실행 gate: `deployment_observer_gate.py`, `unified_open_ledger.py`, `post_work_anomaly_audit.py`.
- 실행 gate: `incomplete_register.py`. 반복 지시와 observer repetition은 자동화 실패 후보로 통합 ledger에 보존한다.
- 반복 관찰자 의도는 `observer_repetition_gate.py`가 증분 집계한다. 5회 이상은 영구규칙 후보, 10회 이상은 SSoT·Work 입력·runtime gate 강제 대상이며 이후 재반복은 `AUTOMATION_FAILURE` OPEN이다.
- 모든 중간·최종 보고는 L1~L6, deployment, observer-intent, hidden, other OPEN 숫자와 후보 NEW/RECURRENCE/CLOSED/DUPLICATE 불변식을 포함한다. 숫자 누락은 `OPEN_COUNT_REPORT_MISSING=FAIL`이다.
- 2026-08-27 추가 후보 22개는 `open_candidate_22.json`에서 기존 root와 대조하며 새 root를 임의 증식하지 않는다. 실행 gate는 `open_count_report_gate.py`다.
- TOOL043 P0는 실제 전화 배포, 홈 화면 진입, observer real use, screen-off background, state persistence/restore가 모두 실제 PASS일 때만 `DEPLOYED_COMPLETE`다.
- TOOL006 자기개선은 `SELF_ANALYZE -> ERROR_CLASSIFY -> FIX_CANDIDATE -> HISTORICAL_REGRESSION -> PASS_ONLY_PROMOTION`을 강제한다. 기존 검증 root만 학습자산으로 사용하고 동일 실패방법, 실제 대표검증 누락, regression FAIL, publisher golden pair 부재 후보는 운영 승격을 거부한다.
- 실행 gate: `tool006_self_improvement_gate.py`; 검증자산: `tool006_learning_assets.json`.
- 대화 누적·문맥 압축·로딩/응답 지연·재조회 증가를 증분 감시한다. 압력 신호가 의미 있게 누적되면 관찰자보다 먼저 `CHAT_HANDOFF_REQUIRED`를 표시하고 SAFE checkpoint, OPEN 숫자, INCOMPLETE/HOLD, queue, NEXT_START, 영구규칙을 자동 압축한다.
- handoff에서 사용자의 유일한 행동은 준비됐을 때 새 대화창을 여는 것이다. Work가 새 대화창을 만들거나 이름을 바꾸지 않는다. 사용자가 먼저 지연을 신고하면 `CHAT_HANDOFF_LATE_DETECTION=ANOMALY`다.
- 실행 gate: `chat_handoff_gate.py`; Work 입력 상태: `chat_handoff_state.json`; post-work audit와 incomplete/unified ledger가 결과를 재사용한다.
- handoff 문장 출력만으로 PASS하지 않는다. 이동 전 `pre_handoff_flush.py`가 LAST_ACTUAL_WORK, OPEN/INCOMPLETE/HOLD/approval, 중요 feedback, 영구지시 참조, TOOL state, NEXT_START를 중앙 snapshot으로 저장한다.
- 새 대화 첫 업무 응답 전 `new_chat_resume_gate.py`가 TOOL master, SSoT, checkpoint, handoff, OPEN/HOLD, last actual work, persistent feedback, NEXT_START를 읽고 `RESUME_FROM_LAST_ACTUAL_WORK`한다. 사용자 첨부는 복구 예외이며 정상 입력이 아니다.
- target/central validation, commit, push, remote SHA/file read-back, checkpoint 전에는 `MASTER_UPDATE=COMPLETE`가 아니다. 현재 단계는 `MEMORY_ONLY/CHAT_ONLY/LOCAL_ONLY/COMMIT_PENDING/PUSH_PENDING/READBACK_PENDING` 중 정확한 값으로 기록한다.
- 중앙 정보 부재는 `HANDOFF_PERSISTENCE_GAP`, 중앙 정보 미선조회는 `RESUME_GATE_GAP`, 원격 미반영은 `MASTER_PROPAGATION_GAP`이다.
- `USER=OBSERVER ONLY`, `NEVER START OVER`, directive target conservation, actual-smoke gate, `NOT_WORKED`, `PREMATURE_WORK_EXIT`, 미해결 자동 queue는 모든 Work의 불변조건이다. 사용자 수동 routing이 1건이라도 있으면 `OBSERVER_MODE=FAIL`이다.
- `MASTER_FIXED != RUNTIME_FIXED`다. latest remote revision, validator, output gate, 실제 결과 PASS가 모두 확인되기 전 COMPLETE를 금지한다.
- 일반 Chat발 중앙 변경은 `UNTRUSTED_CHAT_PATCH`로 분류하고 정상 기준점과 해당 변경만 scoped 비교한다. 검증·정상 commit/push/read-back/checkpoint 없이 운영 승격하지 않으며 reset/전체 rollback은 금지한다.
- repository는 기존 저장소를 우선 재사용한다. 기존 repo가 없고 생성 권한과 실행경로가 모두 확인될 때만 별도 고위험 승인으로 생성하며, 아니면 `REPOSITORY_CREATE_HOLD`다. 실패한 신규 경로가 기존 WIC runtime을 중단시키면 안 된다.
- 현재/미래 WIC는 TOOL 번호 하드코딩 없이 registry 등록만으로 feedback→resolve→root→evidence→apply→validation→remote/state sync를 승계한다.
- 크레딧 중단 시 마지막 remote SAFE checkpoint가 계속 운영 가능해야 한다. 미완성 workflow를 운영 HEAD에 push하지 않는다.
- 실행 gate: `operational_safety_gate.py`; 상태: `operational_safety_state.json`.

## 4. 결과 출력 공통 게이트
모든 업무 결과는 출력 전에 아래 순서를 통과해야 한다.

1. 최신 규칙 회수
2. 오래된/충돌 규칙 제외
3. 입력자료 존재 여부 확인
4. 필수 항목 완전성 검사
5. 원본/공식출처/실제 파일 대조
6. 업무별 전용 규칙 적용
7. 누락·모순·중복 검사
8. PASS / HOLD / FAIL 판정
9. PASS만 완성 결과로 출력
10. HOLD는 원인 + 부족한 근거 + 개선 가능한 방법을 함께 표시
11. FAIL은 잘못된 결과를 생성하지 않고 중단
12. 동일 오류의 재발 여부를 검사하고, 재발 시 규칙/회귀테스트를 갱신
13. 결과가 여러 건이면 가능한 범위까지 연속 처리하고 중간 승인을 요구하지 않는다.
14. 도구/응답 한계로 한 번에 끝나지 않으면 처리한 범위·남은 범위·재개 지점을 정확히 저장하고, 완료라고 하지 않는다.
15. 사용자가 보고 형식을 요청했으면 도구 작업이 끝난 뒤 반드시 최종 사용자 보고까지 출력한다.

### 진행상황·작업상태 보고 형식 LOCK
- 모든 업무 대화창, 모든 도구 개발/검증/운영, GitHub 통합, 예약 통합, PASS/HOLD/FAIL 및 오류 원인/해결/다음 작업 보고는 **테이블(표)을 먼저 제시**한다.
- 기본 칼럼은 `항목 | 현재 상태 | 실제 실행/근거 | 남은 작업 | 판정`이며 상황에 따라 세부 칼럼을 조정할 수 있다.
- 긴 텍스트 덩어리만으로 여러 단계의 상태를 보고하지 않는다. 추가 설명은 표 아래에 짧게 붙인다.
- 실제 실행하지 않은 것은 완료로 표시하지 않고, 불확실한 항목은 HOLD/확인 필요로 표시한다.
- 단순 질문·메일 작성 등 진행상황 보고가 아닌 일반 답변에는 억지로 표를 강제하지 않는다.
- 사용자가 명시적으로 다른 보고 형식을 지정한 경우에만 예외로 한다.

### 상태 정의
- PASS: 필요한 근거와 필수항목을 확인했고 현재 검증 범위에서 출력 가능
- HOLD: 일부 근거·권한·연결·필드가 부족하여 확정 출력 금지
- FAIL: 규칙 위반, 실제 데이터 불일치, 가짜값 생성, 잘못된 연결 등으로 결과 사용 금지

## 5. 실제 작업 증거 잠금 — 자기판정 금지
외부 작업은 assistant의 말이나 화면 모양이 아니라 외부에서 다시 읽을 수 있는 증거로 판정한다.

실행 완료 후보 증거:
- GitHub commit SHA
- 실제 파일 변경 SHA
- Actions Run / test result / artifact
- 실제 생성 파일
- 실제 접속 가능한 결과 URL
- 실제 원본↔결과 비교 결과
- 공식 웹 출처와 결과의 값 일치 기록

### 독립 검증 원칙
1. `내가 실행했다고 말함`은 증거가 아니다.
2. 쓰기 작업은 가능하면 `쓰기 응답 + 다시 읽기(read-back)` 두 단계로 확인한다.
3. 실행 기능은 `코드 존재`가 아니라 `실제 입력→실행→출력→예상값 비교`까지 있어야 기능 PASS다.
4. GitHub commit만 있으면 `저장됨`은 증명하지만 `프로그램이 정상 동작함`까지 증명하지는 않는다.
5. Run/Artifact/스크린샷/결과 URL처럼 사용자가 원하면 외부에서도 확인 가능한 증거를 우선한다.
6. 증거가 불충분하면 assistant가 스스로 낙관적으로 PASS하지 않고 HOLD한다.

터미널 문구, 목업, 상태표, 임의 PASS 문구, 가짜 진행률은 실제 증거가 아니다.

## 6. Chat / Work / Codex 역할 분리
### 최상위 Work 분리 잠금 — 규칙 통합과 Work는 별개
- **대화기록·규칙·GitHub 통합 작업과 Work에서 수행하는 구현/E2E 작업은 서로 상관없는 별도 작업이다.** 진행률·로그·완료판정을 섞지 않는다.
- 과거 규칙 재독해, 대화기록 정리, 전체 도구 규칙 회수, 기존 추출물 재분석, 중앙 규칙 통합에는 Work 크레딧을 사용하지 않는다.
- 이미 존재하는 Antigravity/WIC34 추출물·백업본·GitHub 기록을 먼저 검색·재사용하지 않은 상태에서는 Work 사용 금지다.
- 규칙 회수/통합/대화기록 정리/과거 자료 재추출 목적은 `WORK_REQUIRED=false`로 잠근다.
- Work 실행 전에는 실제 Work-only blocker와 `WORK_REQUIRED=true` 근거가 있어야 한다.
- 이 규칙을 어기고 Work/Antigravity 크레딧을 불필요한 전체 규칙 재추출에 쓰는 것은 `CRITICAL_RESOURCE_MISUSE` / `CREDIT_WASTE_FAIL`로 분류한다.

### Chat 우선 — 최대 처리
Work를 쓰기 전에 Chat + 연결도구로 안전하게 처리 가능한 범위를 최대한 소진한다.
- 기존 규칙/파일 검색
- GitHub 코드·문서 읽기
- 연결 권한이 있는 GitHub 파일 생성/수정
- 웹 조사와 공식출처 검증
- 파일 분석/생성/편집
- 규칙 충돌 제거
- 테스트 케이스 설계
- 결과 검증표 작성
- 규칙 단일 원본 갱신
- 도구 저장소에 단일 원본 참조 연결
- 고객 DB 스키마/분기 로직/결정형 게이트 설계
- 개별 고객의 실제 공개정보 조사와 실제 보고서 추천 검증
- 개별 보고서 TOC 정리 및 안내서 데이터 준비
- 연결된 파일을 이용한 실제 산출물 생성·검증이 가능한 경우의 파일 작업

### Chat의 현실 경계
- Chat은 Work처럼 장시간 독립 실행하는 전용 에이전트 모드가 아니다.
- 한 응답이 끝난 뒤 사용자 요청 없이 계속 새 메시지를 자율 출력한다고 가정하지 않는다.
- 다만 한 번 받은 오더 안에서는 도구/응답 한도가 허용하는 범위까지 중간 승인 없이 최대한 연속 처리한다.
- 장시간·예약·반복 실행이 필요하면 실제 예약 자동화를 사용하고 상태판/재시작점으로 이어간다.

### Work/Codex 사용 조건 — 최소 잔여만 이관
- Chat의 연결도구만으로 실제 실행이 불가능한 지속적 소프트웨어 구현
- 여러 파일·브라우저 런타임·다운로드를 묶는 E2E
- 대량 배치 실행 및 반복 통합회귀
- 실제 업로드/브라우저 자동화 등 Chat에서 안정적으로 실행증거를 만들 수 없는 구간
- 사용 전 Chat에서 규칙·입력·기대출력·테스트케이스·HOLD 원인을 정리해 Work가 과거 자료를 처음부터 다시 읽지 않게 한다.
- 동일한 분석·재개발에 크레딧을 반복 소비하지 않는다.
- 크레딧 사용 시 작업 범위를 작게 고정하고 작업 전후 사용량과 실제 산출물을 기록한다.
- 자동 충전/불필요한 추가 결제를 기본값으로 사용하지 않는다.
- 반복 테스트는 가능한 한 GitHub Actions/Playwright/결정형 테스트로 이관한다.

## 7. 껍데기 차단 규칙
### 절대 금지
- 실제 보고서가 없는데 제목·발행사·가격·목차를 그럴듯하게 만들어 넣기
- 실제 온라인 검증 없이 `검증 완료` 표시
- 구조/버튼 존재만으로 업무기능 PASS
- 로컬 목업을 실제 외부서비스 연결로 표현
- 사용자에게 확인시키기 위해 불완전 결과를 계속 던지는 방식
- 터미널이 움직였다는 이유만으로 외부협업 완료 표시
- Work/Codex 크레딧이 소모됐다는 이유만으로 기능 구현 완료 표시

실제 데이터가 없으면 HOLD다.
외부구조 접근 도구가 없으면 `HOLD: 외부 실행 통로 없음`이라고 표시하고 실행한 척하지 않는다.

## 8. 이메일 수집 공통 규칙
1. 사용자가 지정한 산업 분야만 작업한다.
2. 분야별 고객 DB를 혼합하지 않는다.
3. 공식 출처에서 확인된 정보만 본표에 반영한다.
4. 기본 필드: 관리번호 / 고객군 / 기관 / 기관군 / 부서 / 이름 / 공식 직책 / 담당업무 / 이메일 / 공식 연락처 / 공식 출처 / 최근 공식 수행내용 / 검증결과 / 탐색축 / 담당업무 키워드 / 회사소개서 발송 여부·버전·일자 / 명함 발송 여부·버전·일자 / 2단계 연락 적합도 / 추적 여부 / 다음 행동 / 비고.
5. 필수값이 부족하면 본표에 억지로 넣지 않고 HOLD/추적 대상으로 분리한다.
6. 직책보다 실제 담당업무·현재 사업·과제·공정·장비·정책·기업지원 축을 우선한다.
7. 이름·이메일·직책이 동일인인지 검증한다.
8. 기관+이름+이메일 기준 중복 제거.
9. 기존 고객을 신규 고객으로 중복 등록하지 않는다.
10. 완료 고객 때문에 부족 고객을 기다리지 않는다. PASS는 계속 진행하고 부족 고객만 HOLD한다.
11. 결과는 다음 컨택·추천 작업에서 재사용 가능한 구조로 남긴다.
12. 발송 순서에서 동일 기관 연속 금지(3행), 동일 부서 4행 간격, 동일 도메인 연속 금지(중간 2개), 기관 6개 이상 혼합을 기본으로 한다.
13. 제목·첫 문장 패턴은 분산해 반복성을 낮춘다.
14. 한 기관은 가능한 한 공개자료 범위에서 충분히 파고 다음 기관으로 이동하되, 중간 승인을 반복 요구하지 않는다.
15. 50/100명 단위로 누적 가능하도록 구조화한다.
16. 반송은 시스템 반송/수신자 반송을 분리한다.
17. 관리번호는 영구값으로 취급하고 삭제·재사용·재정렬로 다른 고객에게 번호를 넘기지 않는다.
18. 메일을 추정하거나 대표번호를 개인 연락처로 대체하거나 담당업무를 직책만으로 추정하지 않는다.

### 고객군 3분기 LOCK
- `NEW_ONLINE`: 온라인에서 새로 찾은 예비고객. 공식 웹에서 이름·부서·담당업무·이메일을 검증한다.
- `DORMANT_LEDGER`: 기존 고객장부에 있으나 최근 연락이 거의 없었던 고객. 기존 이력을 보존한 채 최신 소속/담당업무/이메일을 재검증한다.
- `RECENT_TRADE`: 최근 거래가 있었던 고객. 최근 거래·관심자료·담당업무 맥락을 다음 컨택 판단에 연결한다.
- 세 고객군은 같은 사람일 수 있으므로 중복검사를 먼저 하고, 고객군은 `source_cohort`로 이력을 유지한다.
- 회사소개서/명함을 이미 보냈다면 버전·일자·재발송 사유를 확인하고 무조건 재발송하지 않는다.
- 실제 외부 발송은 수신자·첨부·발송권한이 명확하지 않으면 자동 실행하지 않고 `SEND_READY`까지만 만든다.

## 9. 고객 컨택 / 7번 규칙
입력: 고객군 / 고객명 / 기관 / 부서 / 검증된 담당업무 / 기존 메일·통화 이력 / 회사소개서·명함 발송이력 / 고객 직접 발언 / 최근 공식 활동

필수 출력:
1. 고객 유형
2. PASS/HOLD/FAIL
3. 지금 할 행동
4. 전화 또는 메일 우선 판단
5. 실제 전화 멘트
6. 메일 제목·본문
7. 필요 시 문자 멘트
8. 상대 답변별 다음 대응
9. 추천자료 표
10. 금지 표현
11. 후속 연락 여부와 조건
12. 현재 확인 요약
13. 과거 이력
14. 회사/기관 최신 방향
15. 고객 니즈 판단
16. 컨택팅 포인트
17. 3개/4개 우선순위
18. 어려운 용어 쉬운 설명
19. 회사소개서/명함 발송 상태와 다음 발송 판단
20. 통화 후 분기 코드

추천자료 규칙:
- 직책보다 실제 사업축·기관 프로젝트·구매 흐름을 우선한다.
- 실제 발행자료를 먼저 확인하고 담당업무와 제목/목차/조사범위가 연결되는 자료만 추천한다.
- 추천자료는 `핵심 / 확장 / 안전` 3개 역할을 모두 갖춘다. 하나라도 실제 검증된 자료가 없으면 HOLD.
- 가능한 경우 2026년 발행자료를 우선한다.
- 현재 거래 가능한 발행사만 사용한다. 리셀러/거래제한 대상은 제외한다.
- 실제 판매 페이지와 제목·링크 일치 여부를 확인한다.
- Industry Experts, Inc. 자료는 PDF 브로셔보다 HTML 상세페이지를 우선한다.
- 실제 자료가 확인되지 않으면 억지 추천하지 않고 HOLD한다.
- 고객의 직접 발언은 온라인 추정보다 우선한다.

유선 멘트 잠금:
- 새 조사 기반 연락은 `홈페이지를 조금 찾아보니까`처럼 출처를 구분한다. 실제 고객 문의·견적·통화 답변이 있으면 그 이력을 먼저 짧게 연결한다.
- 고객 업무를 과도한 전문용어로 단정하지 않는다.
- 일반인이 공식 홈페이지를 읽고 이해한 수준으로 충분히 풀어 설명한다.
- 멘트 작성 전에 실제 판매 가능한 해외 시장/기술자료를 온라인에서 먼저 조사한다.
- 고객 담당업무와 실제 자료가 연결되지 않으면 멘트를 억지로 만들지 않는다.
- `필요한 자료가 있습니까?`, `어떤 분야에 관심이 있습니까?`처럼 조사 책임을 고객에게 넘기는 질문은 금지한다.
- 새 탐색 연락은 실제 자료에 근거한 두 갈래 질문을 쓸 수 있다. 이미 고객이 지정한 범위/국내외 형식이 있으면 재사용하며, 한 질문 후 답변→범위 확인→그 범위만 자료 검증 순서로 한다. 멘트 품질의 공통 실행 기준은 `CUSTOMER_CALL_SCRIPT_LOCK.md`를 함께 적용한다.
- 일반 템플릿이 아니라 고객 개인/기관의 최근 연구기사·보도자료·과제·발표·인터뷰 등 실제 공개활동을 소재로 한다. 실제 활동근거가 없으면 특정 사실을 만들어내지 않는다.

### 통화 후 고객응답 분기 LOCK
고객 직접 발언을 기준으로 아래 중 하나 이상을 판정한다.
- `FULL_GUIDE`: 구체적 보고서/범위/구매검토가 잡혀 정식 안내서가 적합
- `INTERMEDIATE_GUIDE`: 관심은 있으나 분야/범위/예산을 더 좁혀야 해서 중간 안내서가 적합
- `OTHER_MATERIAL`: 다른 기술/시장/도서/데이터 형태를 요구
- `PRICE_BUDGET`: 가격·예산·구매절차 질문
- `INTERNAL_FORWARD`: 내부 다른 담당자/부서로 전달
- `FOLLOW_UP_DATE`: 추후 연락일 명시
- `NO_INTEREST`: 현재 관심 없음
- `STOP`: 수신거부·부적합·재접촉 금지
- `PURCHASE_PROCUREMENT`: 실제 구매/견적/계약 절차 진입
고객이 말하지 않은 방향을 임의로 승격하지 않는다.

### 7번 실행판이 HOLD일 때의 Chat-native 대체 실행
GitHub 실행판이 최신 7번 목적과 불일치해도 고객 업무를 멈추지 않는다. Chat에서 아래 파이프라인으로 동일 목적을 수행한다.
`고객 식별 → 고객군/과거 이력 회수 → 공식 홈페이지/최신 공개자료 조사 → 담당업무 쉬운 해석 → 실제 판매 가능 보고서 조사 → 핵심/확장/안전 추천 → 유선 멘트 → 상대답변 분기 → 메일/문자 → 안내서/중간안내서/다른자료 판단 → 최종 행동 → 누락검사`
이 파이프라인의 필수 출력이 하나라도 빠지면 PASS 금지.

## 10. 안내서 / 중간 안내서 / 1번 규칙
### 원칙
- 사용자가 빈 안내서 파일을 제공했거나 Library에 기존 양식이 있으면 먼저 원본 양식과 슬롯을 직접 확인한다.
- 제목 / 발행사 / 발행일 / 페이지 / 정가 / 공급가 / 실제 링크 / 목차 등 필요한 슬롯을 매핑한다.
- 원본의 레이아웃·고정문구·표·로고 위치는 가능한 한 보존한다.
- 사용자가 각 칸을 수작업으로 채우게 하지 않는다.
- 검증된 실제 데이터만 삽입한다.
- 실제 보고서 데이터가 없으면 가짜값으로 양식을 채우지 않는다.
- 과거 내부 생성형 `Market Report + 임의 페이지/가격/목차` 로직은 DEPRECATED / 사용 금지.
- 데이터는 직접 수동입력보다 매핑을 우선한다.

### 확인된 HTML 자산 LOCK
- Library의 `안내서_전체_연결버전.html`은 영문/한글 제목, 발행사, 발행일, 페이지, 정가, 공급가격, 링크, TOC 입력을 안내서 레이아웃에 반영하는 단순 매퍼다. 실제 검증 데이터를 넣는 기본양식 후보로 사용할 수 있다.
- Library의 `1번도구_정상미리보기_좌중우_5안내서_v14.html`은 `example.com/report-*`, 자동 생성 제목·페이지·가격·공급가격, placeholder 링크 등 synthetic report data를 생성한다. 이 생성부는 생산용 FAIL / QUARANTINE이며 실제 안내서에 사용 금지. 레이아웃/슬롯 자산만 필요 시 분리 재사용한다.
- HTML 자체가 존재하는 것만으로 실제 고객용 파일 출력 PASS가 아니다. 실제 보고서 1건을 넣어 결과 렌더링/필드일치/필요 시 파일 출력까지 검증해야 한다.

### 정식 안내서 / 중간 안내서 분기
- 정식 안내서: 실제 보고서가 확정됐고 고객업무 연결근거, 실제 메타데이터, 링크, 구매검토에 필요한 상세정보와 TOC를 제공할 수 있을 때.
- 중간 안내서: 고객 관심축은 확인됐으나 정확한 보고서/범위/예산/자료형태를 더 좁혀야 할 때. 검증된 후보·범위·왜 관련되는지·다음 선택지를 제공하되 확정되지 않은 가격/페이지/세부내용을 채우지 않는다.
- 고객 통화/답신 뒤 분기코드가 없는 경우 임의로 정식 안내서로 승격하지 않는다.

### 안내서 콘텐츠 확장 규칙
기존 안내서가 제목·기본서지·링크·목차 중심으로 너무 얇으면, 실제 원문에서 검증 가능한 범위 안에서 아래 섹션을 추가 검토한다.
- 보고서가 다루는 시장/제품 범위 요약
- 고객 담당업무와 연결되는 핵심 포인트
- 조사 범위/세그먼트/지역
- 주요 목차 하이라이트
- 제공되는 표/그래프/데이터 유형
- 조사 방법론 또는 데이터 출처 설명(발행사가 공개한 경우)
- 주요 기업/경쟁구도(원문에 공개된 경우)
- 구매/라이선스/납품 형식 정보(실제 공개정보가 있는 경우)
- 고객에게 왜 이 자료를 보냈는지 2~4문장

원문에 없는 내용을 분량을 늘리기 위해 만들어내지 않는다. 콘텐츠 수는 고정 3개가 아니라 실제 검증 가능한 정보량에 따라 확장한다.

### 결과 방식
A. 파일 직접 편집이 안정적으로 가능한 형식: 완성 파일 생성 + 필드 검증 후 반환
B. 형식 보존이 불확실한 파일: HOLD + 원인 + 안전한 변환/편집 방법
C. 단순 붙여넣기 데이터만 제공하는 방식은 파일 직접 생성이 불가능할 때의 차선책

## 11. 37번 메타데이터 규칙
1. 37번은 메타데이터 생산·한글 타이틀·발행사 규칙 대조·검증·잠금 통합 운영이다.
2. 13번 엑셀 자동 업로드와 별개다. `37/13 메타데이터`처럼 묶어서 표현하거나 한 도구처럼 처리하지 않는다.
3. 작업 전 원본 파일과 결과 파일을 직접 확인한다.
4. 필수 칼럼을 작업 단위 전체에서 한 번에 검사한다.
5. `상품명`은 한국어 번역 제목, `한글명`은 영문 원문 제목으로 유지한다. 두 필드를 뒤바꾸지 않는다.
6. 상품명은 공란 금지. 제품명·화학식·기업명·고유명사·약어는 필요 시 영문 유지.
7. 상품명/한글명/ISBN/CODE/발행일/지역/가격 등 잠금된 핵심 필드의 누락을 전체 범위에서 검사한다.
8. 첫 행·중간 행·마지막 행을 포함한 값 이동/매핑을 검증한다.
9. 발행사별 예외와 공통 규칙을 섞지 않는다.
10. 같은 칼럼명이더라도 의미/값구조가 다르면 발행사별 규칙으로 유지한다.
11. 원본과 결과를 직접 대조하지 않은 상태에서 PASS 금지.
12. 한 필드를 누락해 사용자가 다시 수정시키는 방식은 FAIL.
13. 이미 PASS로 잠긴 영역은 새로운 오류 증거가 없는 한 임의 변경 금지.
14. 별도 버전 사본을 늘리지 않고 지정 마스터를 같은 이름으로 갱신한다.

### 37 발행사 규칙 잠금
- 같은 처리 목적/값 이동이 2개 이상 발행사에서 공통규칙 후보로 승격한다.
- 발행사별 첫/중간/마지막 행에서 동일 값 이동을 확인한다.
- 상태는 `잠금 완료 / 조건부 잠금 / 변경 감지 / 미잠금`으로 관리한다.

## 11A. 13번 엑셀 자동 업로드 규칙
1. 13번은 엑셀 자동 업로드 도구다. 메타데이터 규칙 생산/잠금의 주체는 37번이다.
2. 37번에서 확정된 구조화 규칙을 입력으로 받아 실제 업로드·오류좌표·예외정규화·다운로드 결과를 검증한다.
3. 날짜 serial, 텍스트/날짜 형식, 미리보기/다운로드 차이를 회귀테스트 대상으로 잠근다.
4. 알려진 회귀: 원본연결 Publishing Date 값 `46145`가 노출되는 문제는 FAIL/HOLD이며 수정 전 생산 PASS 금지.
5. G1~G5 등 필수 게이트 중 하나라도 실패하면 실행/저장/다운로드를 PASS 처리하지 않는다.
6. 기능 PASS는 실제 엑셀 입력 → 업로드 처리 → 실제 결과/다운로드 → 기대값 비교가 필요하다.

## 12. 6번 목차 정리 규칙
- 원문 목차를 임의로 재작성하지 않고 구조를 보존해 정리한다.
- 상위→하위 계층, 들여쓰기, 번호 체계를 유지한다.
- 불필요한 페이지번호/잡음 제거는 규칙에 따라 수행한다.
- 과도 제거/잔여 오류는 자동진단 대상으로 남긴다.
- 동일 오류 패턴은 자동진단/회귀검증으로 잠근다.
- 현재 코드/규칙 재사용을 우선하고 전면 재작성하지 않는다.

### Chat / 6번 역할 경계
- 개별 고객 안내서 1건의 TOC는 공식 발행사 페이지/원문에서 실제 TOC를 확보할 수 있으면 Chat이 직접 번호·깊이·줄바꿈·잡음을 정리하고 안내서에 삽입할 수 있다.
- 이 개별 작업은 원본과 결과를 비교할 수 있으면 6번 대량도구의 최종 PASS를 기다리지 않는다.
- 6번 도구는 다량 보고서, 발행사별 반복패턴, golden fixture, 자동 회귀검증, 대량배치에서 우선 사용한다.
- 랜덤/가짜 TOC 시뮬레이션만으로 생산 PASS 금지.

## 13. 도구 개발 공통 규칙
1. 기존 코드·규칙·파일을 먼저 재사용한다.
2. 실제 업무 흐름 1개를 처음부터 끝까지 통과시키는 E2E를 우선한다.
3. 테스트 하나가 실패할 때마다 사용자를 호출하지 않는다.
4. 발견 오류는 자동 회귀 테스트로 등록한다.
5. 동일 오류는 반복 수동검증하지 않는다.
6. 구조 PASS와 기능 PASS를 분리한다.
7. 기능 PASS는 실제 입력 → 처리 → 실제 출력 → 예상값 비교까지 확인해야 한다.
8. 자동 테스트 가능 영역은 Work/Codex 크레딧 없이 반복 검증하도록 설계한다.
9. PASS된 기능은 새 오류 증거가 없으면 수정하지 않는다.
10. 신규 기능보다 기존 실사용 흐름 안정화와 오류 제거를 우선한다.
11. 외부구조가 실제 연결되지 않으면 개발 완료를 주장하지 않는다.
12. Work 사용 전 Chat에서 입력스키마·규칙·기대출력·테스트케이스·실패증거를 준비해 크레딧을 구현/런타임 검증에 집중한다.

## 14. 도구 번호별 단일 등록표
상태 표기: CONNECTED=GitHub 저장소 접근 가능, HOLD=규칙/코드/목적 충돌 또는 실행증거 부족, DEPRECATED=현재 사용 중단/대체.

| 번호 | 목적/이름 | GitHub/저장 상태 | 현재 규칙 상태 |
|---|---|---|---|
| 1 | 고객 자동화 안내서 | obk369369-spec/01-auto-guide-v1 CONNECTED | 실제 데이터 전용, HTML 기본양식 회수, synthetic 생성부 격리, 실제 E2E HOLD |
| 2 | 입찰/나라장터 | obk369369-spec/02-auto-bid-narajangter-v1 CONNECTED | 로컬 관리기능과 실제 나라장터 자동화 분리, 외부 자동수집 HOLD |
| 3 | 코딩 기초 연습 | obk369369-spec/03-coding_practice CONNECTED | 입력-결과 일치/진도 기록 중심, 상세 규칙 추가 회수 시 본 문서에 통합 |
| 4 | 연구비 박사 엑셀 생성기 | obk369369-spec/04-research-funding-generator CONNECTED | 원본→양식 생성→샘플 검증, 상세 규칙 추가 회수 시 통합 |
| 5 | 보고서 생성기 | obk369369-spec/05-report-generator CONNECTED | 원본문서 기준·4번 연동검사, 상세 규칙 추가 회수 시 통합 |
| 6 | 목차 정리 | obk369369-spec/06-toc-check CONNECTED | 대량/발행사별 자동화·golden fixture, 개별 고객 TOC는 Chat 처리 가능 |
| 7 | 고객 컨택 판단 | 저장소명 07-wic-setting-tool-v1 CONNECTED지만 목적 불일치 | 고객 컨택 규칙은 본 마스터에 LOCK, 저장소 실행판 HOLD, Chat-native 실행 ACTIVE |
| 8 | 영어 동사 활용 | obk369369-spec/08-English-Verb-Exercise CONNECTED | 학습입력→활용출력→학습로그 |
| 9 | 콘텐츠 자료 안내 | obk369369-spec/09-contents-making-tool CONNECTED | 분야/키워드→추천안내→발행사 분산검사 |
| 10 | 재무 회계 | obk369369-spec/10-WIC-Finance-Dashboard CONNECTED | 장부입력→계산/출력→계산검사 |
| 11 | 재테크 | obk369369-spec/11-obk-finance-planner CONNECTED | 자산/조건→비교출력→기준표 |
| 12 | 서브 웹사이트 제작 | obk369369-spec/12-wic-subwebsite-builder CONNECTED | 요구→화면→배포검사 |
| 13 | 엑셀 자동 업로드 | obk369369-spec/13-excel-upload CONNECTED | 37번과 분리. 업로드/오류좌표/예외정규화, 46145 날짜 회귀 FAIL/HOLD |
| 14 | 홈페이지 수정 | obk369369-spec/14-wic-homepage-editor CONNECTED | 수정대상→반영화면→연결검사 |
| 15 | 연계도구군 | 전용 GitHub 저장소 미확인 | 조사·검증·안내·후속조치 연계, HOLD |
| 16 | 작업 통제 도구 | 전용 GitHub 저장소 미확인 | 도구상태·지시·상위통제 동기화, HOLD |
| 17 | PC 화면 녹화 | 전용 GitHub 저장소 미확인 | 화면/녹화조건→결과저장, HOLD |
| 18 | 도구 기능 정책 | 전용 GitHub 저장소 미확인 | 허용/금지/보류 정책, HOLD |
| 19 | 사업장 홍보 | obk369369-spec/19-wic-business-promotion CONNECTED | 홍보자료→출력→채널검사 |
| 20 | 운영 매뉴얼 | obk369369-spec/20-operational-manual-viewer CONNECTED | 본 단일 마스터 저장소 역할 추가 |
| 21 | 영업 도우미/동선 | obk369369-spec/21-Sales-Route-Planner CONNECTED | 고객·동선·자료→일정/자료안→출장흐름검사 |
| 22 | 공통 준비물 | obk369369-spec/22-Common-Item-kit CONNECTED | 준비물 입력→목록→사용범위 확인 |
| 23 | 월드 어드바이저 | obk369369-spec/23-world-advisor CONNECTED | 사업모델→조언→평가척도 |
| 24 | 동영상 제작 | obk369369-spec/24-Easy-Video-Maker CONNECTED | 소재/이미지/자막→영상흐름→플랫폼 연동검사, 기능 검증 HOLD |
| 25 | 무료자료 생성 | obk369369-spec/25-free-content-maker CONNECTED | 원천자료→무료자료→품질판정, 기능 검증 HOLD |
| 26 | 과거 비활성/1번 중복 기록 vs 현재 online-item-shop 저장소 | obk369369-spec/26-online-item-shop CONNECTED | 번호 목적 충돌 HOLD, 임의 통합 금지 |
| 27 | 공학도서 안내/기술도서 검증 | obk369369-spec/27-technical-book-verifier CONNECTED | 실제 도서 데이터 검증·추천·1번 이관 규칙, 기존 코드 재사용 |

## 15. 업무 대화창별 단일 등록표
- 이메일 수집 분야별 대화창들: 본 마스터 8장 적용. 산업별 데이터는 섞지 않는다. 새 루틴의 `NEW_ONLINE` 고객군 시작점 역할.
- 고객장부/CRM 계열: `DORMANT_LEDGER / RECENT_TRADE` 고객군과 과거 연락·거래·소개서·명함 발송이력을 유지한다.
- 7번 고객 컨택 판단: 세 고객군 모두의 2단계 판단 허브. 통화 전과 통화 후 분기를 구분한다.
- 1번 고객 자동화 안내서: FULL_GUIDE / INTERMEDIATE_GUIDE 출력 허브. 실제 검증 보고서와 TOC만 사용한다.
- 28번: 전 세계 해외 신규 발행사 발굴·검증·계약 우선순위. 후보 검증과 첫 접촉 준비까지. 고객응대 루틴에 필요한 실제 판매가능 발행사/자료 검증을 지원할 수 있으나 독립 대량조사는 고객응대 루틴 안정화 후순위.
- 29번: 발행사 파트너십·계약·커미션·정산 관리. 후보 발굴 자체·고객별 추천자료·메타데이터 생산은 제외.
- 30번: 일본 발행사 파트너십·계약·커미션·정산·서비스 관리. 일본 후보 상세 발굴은 31번, 실제 협상/계약 이후 30번.
- 31번: 일본 신규 발행사 발굴. 자체 발행/현재 상품/실제 상품정보/중개 여부/기존 거래 중복/한국 판매 가능성/공식 문의처를 검사해 PASS/HOLD/FAIL.
- 34번: 통합+자동화/관찰자/반복차단/STOP_CARD/외부구조 증거 규칙의 원천. 이 핵심은 본 마스터 1~7장에 흡수.
- 35번: 월드 운영시스템 전체 통합 역할이 일부 문서에서 참조됨. 최신 독립 운영문서 확인 전 HOLD.
- 36번 등 분야별 이메일 수집 창: 본 마스터 8~9장 공통규칙 적용, 분야 데이터는 독립 유지.
- 37번: 메타데이터 생산·한글 타이틀·규칙 대조·검증·잠금 통합 운영. 13번과 별개. 본 마스터 11장 적용.
- 39번: 과거 메타데이터 독립검증 창이 있었으나 최신 37번 통합규칙에서는 미사용/삭제 가능으로 기록. DEPRECATED 후보, 최신 사용 지시가 들어오면 재판정.

## 15A. 고객응대 영업루틴 — 최우선 운영 파이프라인
### 전체 흐름
`고객발견/기존고객추출 → 검증 → 회사소개서·명함 발송상태 → 7번 고객컨택 판단 → 유선연락 → 정식/중간 안내서 또는 다른자료 분기 → 고객응답 분기 → CRM/다음행동`

### 상태머신
`DISCOVERED → VERIFIED → INTRO_CARD_READY/SENT → CONTACT_JUDGMENT → CALLED → FULL_GUIDE / INTERMEDIATE_GUIDE / OTHER_MATERIAL / PRICE_BUDGET / INTERNAL_FORWARD / FOLLOW_UP_DATE / NO_INTEREST / STOP / PURCHASE_PROCUREMENT → RESPONSE_BRANCH → NEXT_ACTION`

### 운영 원칙
1. `source_cohort`는 NEW_ONLINE / DORMANT_LEDGER / RECENT_TRADE 중 하나 이상으로 보존한다.
2. 회사소개서/명함 발송이력은 고객 판단 이전부터 확인하고, 중복 발송을 막는다.
3. 7번은 실제 고객정보와 실제 판매가능 자료를 근거로 전화 멘트를 만든다.
4. 실제 통화는 사용자가 수행할 수 있으나, 통화 전 멘트/질문/분기와 통화 후 입력·다음행동은 Chat이 준비한다.
5. 안내서는 고객 답변에 따라 FULL/INTERMEDIATE를 구분하고 실제 HTML 기본양식을 재사용한다.
6. 고객 응답이 오면 직접 발언을 입력으로 하여 다음 안내서/전화/메일/다른 자료/STOP을 결정한다.
7. 각 단계 결과는 다음 단계가 바로 재사용하도록 INPUT/RULE/OUTPUT/VALIDATION/ERROR_HASH/REUSE 구조로 남긴다.
8. 사용자가 매 고객마다 전체 절차를 다시 설명하지 않는다.

## 16. 대화창 결과를 도구화에 가깝게 만드는 공통 구조
모든 반복 업무는 단순 답변으로 끝내지 않고 다음 6개를 남긴다.
1. INPUT_SCHEMA: 다음 건에 필요한 최소 입력
2. RULE_SET: 적용한 고정 규칙
3. OUTPUT_SCHEMA: 반드시 채워야 하는 출력 필드
4. VALIDATION_GATE: 출력 전 검사조건
5. ERROR_HASH: 새로 발견된 오류 유형
6. REUSE_NOTE: 다음부터 생략 가능한 사용자 작업

같은 오류가 다시 발생하면 단순 수정이 아니라 RULE_SET/VALIDATION_GATE/ERROR_HASH를 갱신한다.

## 17. 연결 상태 자체 검증 규칙
현재 Chat에서 확인된 실제 외부 연결:
- Files: 대화/라이브러리 파일 검색·읽기·필요 시 파일 작업 가능
- GitHub: 저장소 조회, 파일 읽기, 파일 생성/수정, 커밋 SHA 확인 가능
- Web: 최신 공개정보 조사/검증 가능
- Gmail/Calendar/Contacts 등 연결 도구는 해당 작업에서 실제 connector 호출로 확인된 범위만 사용 가능으로 판정한다.

현재 Chat에서 직접 연결이 확인되지 않은 것:
- 사용자의 로컬 Antigravity 터미널 직접 제어
- 임의의 로컬 PC 파일시스템 상시 제어
- 연결되지 않은 외부 서비스의 무제한 자율 실행

따라서 Antigravity/로컬 터미널 작업을 실제 실행했다고 표시하려면 별도의 실제 연결 증거가 필요하다. 연결이 없으면 HOLD.

## 18. 규칙 전수조사 상태
- 관찰자/반복작업 금지 규칙: VERIFIED / LOCK
- 사용자 저장·버전관리·새 대화창 지시문 부담 제거: LOCK
- Antigravity 기존 추출 기준선: RAW 224개 → `tool_mapped` 487개 → `extracted_rules` 생성 흔적 VERIFIED. 동일 원본 전수 재분석 금지, 이후 변경분 증분 처리 LOCK.
- Work/규칙 통합 완전 분리: LOCK. 규칙 회수·통합·과거 자료 재추출에 Work 크레딧 사용 금지.
- 모든 대화창/도구 진행보고 테이블 우선: LOCK.
- 고객응대 루틴: 2026-08-10 사용자 실제 업무순서 기반 최상위 LOCK
- 이메일 수집 공통 규칙: VERIFIED / LOCK, 세 고객군으로 확장
- 고객 컨택 7번 규칙: 핵심 규칙 VERIFIED / LOCK, GitHub 실행판 목적 불일치 HOLD, Chat-native 실행 ACTIVE, 통화후 분기 확장
- 안내서/1번 규칙: 실제 HTML 자산 2종 회수. 단순 매퍼 기본양식 후보, v14 synthetic 생성부 FAIL/QUARANTINE. 실제 데이터 전용 LOCK
- 37번 메타데이터: 13번과 분리 잠금. 핵심 검증 원칙 LOCK
- 13번 엑셀 자동 업로드: 독립 도구 LOCK, 46145 회귀 FAIL/HOLD
- 6번 목차: 개별 Chat 처리 vs 대량도구 경계 LOCK, E2E 회귀검증 강화 필요
- 28/29/30/31 발행사 업무: 역할 경계 핵심 통합 완료, 고객응대 루틴 직접지원 외 독립조사는 후순위
- 1~27 GitHub 저장소: 과거 확인상 다수 실제 연결, 15~18 전용 저장소 미확인
- 과거 분노·피로·반복 신호: 대표 패턴 회수 완료, 전체 Library 문서 문장단위 전수대조는 아직 미완료
- 기타 과거 문서: 발견 시 새 문서를 만들지 않고 본 파일의 해당 항목에 흡수

## 19. 사용자 부담 카운터
다음이 발생하면 즉시 운영 오류로 기록하고 다음 작업부터 제거한다.
- 사용자가 같은 규칙을 두 번째 설명함
- 사용자가 누락 필드를 직접 찾아냄
- 사용자가 결과를 수작업 비교해야 함
- 사용자가 동일 테스트를 반복함
- 사용자가 외부작업이 실제인지 확인하기 위해 증거를 따로 요구해야 함
- 사용자가 규칙 저장/새 대화창 인계 문서를 직접 관리함
- 사용자가 결과를 계속 받기 위해 `계속`, `진행`, `왜 멈춰`를 반복 입력함
- 사용자가 유선 멘트의 의도·구조를 다시 설계해야 함
- 사용자가 고객군·소개서/명함 발송상태·안내서 분기를 매번 다시 정리해야 함
- 사용자가 요청한 정식 진행보고를 다시 요구해야 함
- 진행상황 보고를 텍스트 덩어리로 받아 사용자가 표 형식을 다시 요구해야 함
- 기존 Antigravity 추출 결과가 있는데 전체 규칙을 처음부터 다시 추출해 크레딧/시간을 낭비함

목표: USER_BURDEN_COUNTER = 0에 가깝게 유지.

## 19A. 모든 대화창·도구의 피드백 즉시반영 공통 절차

이 절차는 기존 운영 대화창, 앞으로 만드는 일반 작업 대화창, 앞으로 계획하는 도구용 대화창에 동일하게 적용한다. 41번·42번 검증은 대표 사례이며 다른 도구의 규칙을 서로 섞는 근거가 아니다.

1. 새 작업·새 대화 시작 시 대화 기억보다 먼저 `WIC_CHAT_ROUTING_REGISTRY.md`로 업무군을 판별하고, 해당 도구의 GitHub 중앙마스터와 최신 체크포인트를 읽는다.
2. 사용자가 새 규칙·수정·오류·보완사항을 말하면 해당 도구/업무군을 식별한다. 한 도구의 피드백은 그 도구 중앙마스터에만 반영하며 공통성이 입증된 절차만 이 Global 원본에 반영한다.
3. 해당 중앙마스터를 다시 읽고 기존 규칙과 중복·충돌을 검사한다. 중복이면 재작성하지 않고 재사용하고, 충돌이면 자동 병합하지 않고 HOLD하며, 필요한 규칙만 DIFF ONLY로 수정한다.
4. 단순 문구 수정과 실제 실행 오류를 구분한다. 실행 오류이면 규칙 문서만 수정하지 않고 실제 재발을 막는 출력·실행 게이트 또는 결정형 검증 로직을 함께 수정한다. 같은 오류가 다시 발생하면 기존 수정 실패로 판정하고 원인을 재조사한다.
5. 최신 체크포인트에 적용 범위, 중앙마스터 위치, 충돌/중복 판정, 게이트 변경, 마지막 성공 단계와 재개 지점을 기록한다.
6. 변경 파일만 commit/push하고, 원격에서 같은 중앙마스터·체크포인트·게이트를 read-back한다. 원격 Commit SHA와 파일 blob/content 일치를 확인한다.
7. `중앙마스터 수정 + 필요한 게이트 수정 + 체크포인트 갱신 + commit/push + 원격 read-back + Commit SHA 확인`이 모두 끝나기 전에는 `반영 완료`, `통합 완료`, `FINAL PASS`를 표시하지 않는다.
8. 사용자가 이전 규칙을 다시 복사하거나 설명하도록 요구하지 않는다. 과거 대화·구버전 지시·체크포인트는 참고/상태 증거이며 해당 도구 중앙마스터와 경쟁하지 않는다.

### 피드백 분류·영구반영 게이트
- 사용자가 반드시 `피드백`이라는 단어를 써야 하는 것은 아니다. 정정, 오류 지적, 누락 지적, 형식 변경, 금지사항 추가, 운영방식 변경, 반복오류 지적처럼 **향후 작업 기준을 바꾸는 내용**은 피드백 후보로 감지한다.
- 피드백 후보는 `영구 운영규칙/지속 적용`과 `일회성 질문·정보조회·현재 상태 확인`을 먼저 분리한다.
- **영구 운영규칙/지속 적용만 중앙마스터·해당 도구 마스터에 반영**한다. 일회성 질문, 현재 크레딧/초기화 시각, 단발성 사실조회처럼 다음 작업 기준을 바꾸지 않는 내용은 중앙마스터에 저장하지 않는다.
- 한 메시지에 영구규칙과 일회성 질문이 섞여 있으면 영구규칙 부분만 분리하여 반영하고, 일회성 부분은 답변만 한다.
- 일회성인지 영구규칙인지 불명확하면 임의 영구화하지 않고 HOLD/분류 후 다음 실행 규칙을 오염시키지 않는다.
- 이미 같은 규칙이 있으면 중복 추가하지 않고 기존 규칙을 강화·재사용한다. 기존 규칙과 충돌하면 임의 병합하지 않고 HOLD한다.

### 기존·신규 도구 재사용 규칙
- 기존 도구는 등록된 route와 기존 중앙마스터·게이트·체크포인트를 SKIP-REUSE하며 전수조사하거나 전체 회귀검증하지 않는다.
- 완전히 새 도구는 먼저 기존 route·업무군·중앙마스터로 처리 가능한지 확인한다. 가능하면 기존 구조를 참조하고 별도 중앙마스터를 만들지 않는다.
- 기존 구조로 표현할 수 없는 독립 규칙 범위가 실제로 확인된 경우에만 중앙마스터를 최소 생성하고 route·체크포인트·필요한 게이트 포인터만 등록한다.
- 아직 등록되지 않은 일반 대화/도구 피드백은 임의 도구 규칙에 넣지 않고 `CENTRAL` fallback으로 라우팅하여 HOLD/분류한 뒤, 실제 소유 업무군이 확인될 때만 대상 중앙마스터에 적용한다.

## 19B. WORK 진행 중 Canonical Archive 및 TOOL043 역할 잠금

- USB 전체를 조사하지 않고 현재 Work가 실제로 만지는 범위만 `CANONICAL_NORMAL`, `SHELL_OR_STALE`, `HOLD_UNKNOWN`으로 증분 판별한다.
- `CANONICAL_NORMAL`은 기존 GitHub 중앙 구조에 정상 commit하고 remote SHA/content read-back 및 필요한 최초 검증이 끝나기 전까지 USB 삭제 준비로 판정하지 않는다.
- `HOLD_UNKNOWN`과 USB에만 존재하는 미보존 자산은 삭제하지 않는다. 파일 삭제, USB 삭제, force push, destructive reset, repo 초기화·생성은 일반 SAFE 승인 배치에서 제외한다.
- 실제 작업 주체는 Work/Codex 또는 기존 승인불필요 자동 실행 엔진이다. TOOL043은 실제 작업을 수행하지 않고 실행상태를 Observer와 다음 Work 인계에 연결하는 `OBSERVATION/STATE/HANDOFF BRIDGE`다.
- Observer는 TOOL043 상태와 실제 실행상태를 관찰하고, 스마트폰은 Observer 결과만 표시한다. `SMARTPHONE_DIRECT_WORK_EXECUTION=FORBIDDEN`.
- 스마트폰 원격 승인은 플랫폼 경계로 `BLOCKED_PLATFORM / NON_BLOCKING / SKIP_REUSE`하며 TOOL043 완료조건으로 사용하지 않는다.
- 승인 대기 작업은 `WAIT_APPROVAL`로 분리하고 다음 SAFE 작업을 계속한다. 14:00 KST는 고정 정지시각이 아니라 fallback 확인시각이다.
- 각 도구 완료 보고에는 `CANONICAL_NORMAL`, `SHELL_OR_STALE`, `HOLD_UNKNOWN`, `GITHUB_ARCHIVE_STATUS`, `REMOTE_EVIDENCE`, `USB_DELETE_READY`를 포함한다.

## 20. 변경 이력
- 2026-08-28 KST: Work 진행 범위의 USB 자산 증분 분류·GitHub canonical archive·삭제준비 게이트와 TOOL043=관찰/상태/인계 bridge, 스마트폰=Observer view, 승인대기 비차단 원칙을 추가.
- 2026-08-20 KST: 피드백 후보를 영구 운영규칙과 일회성 질문/정보조회로 분류하고, 영구규칙만 중앙마스터에 반영하도록 잠금. 메시지에 두 종류가 섞이면 영구 부분만 분리 저장하며 애매하면 HOLD.
- 2026-08-20 KST: 모든 기존·신규 일반/도구 대화창에 적용되는 피드백 즉시반영 절차를 고정. 업무군 판별→해당 중앙마스터·체크포인트 선조회→중복/충돌→DIFF ONLY→실행 오류 게이트→체크포인트→commit/push→원격 read-back→Commit SHA 전에는 FINAL PASS 금지. 미등록 신규 도구는 CENTRAL fallback 후 최소 등록하도록 잠금.
- 2026-08-13 17:03 KST: 과거 Antigravity/WIC34 추출 기준선(RAW 224개, tool_mapped 487개, extracted_rules 흔적)을 재사용 대상으로 잠금하고 전체 재분석/재추출을 금지. 규칙 통합과 Work 작업을 완전히 분리해 규칙 회수·통합에는 Work 크레딧 사용 금지 및 `CRITICAL_RESOURCE_MISUSE` 게이트를 추가. 모든 대화창/도구의 진행상황·점검·상태보고는 테이블 우선으로 출력하도록 최상위 공통 보고 규칙을 추가.
- 2026-08-10 11:12 KST: 실제 고객응대 영업루틴을 최상위 파이프라인으로 추가. NEW_ONLINE/DORMANT_LEDGER/RECENT_TRADE 3고객군, 회사소개서·명함 발송상태, 7번 통화 전/후 분기, 정식/중간 안내서, 고객응답 재분기, 상태머신을 잠금. `안내서_전체_연결버전.html`을 실제데이터 매퍼 후보로, v14 synthetic 생성부를 FAIL/QUARANTINE로 반영. 개별 TOC는 Chat 처리 가능, 대량 TOC는 6번으로 분리. 37번 메타데이터와 13번 엑셀 자동 업로드를 완전히 분리. Chat 최대처리 후 Work 최소잔여 이관 원칙을 강화.
- 2026-08-09 17:32 KST: 외부작업 자기판정 금지와 read-back/실행증거 원칙, 한 번의 오더로 가능한 범위까지 연속 처리, 7번 Chat-native 실행 파이프라인, 안내서 콘텐츠 확장 규칙, 분노·피로 신호의 구조 실패 판정을 추가.
- 2026-08-09 16:20 KST: 사용자가 과거 수행해온 반복 작업 24종을 제거 대상으로 명시. 1~27 도구 등록표, 28~39 주요 업무 대화창 등록표, Chat 실제 연결상태, 단일 원본/포인터 방식, 대화결과의 INPUT/RULE/OUTPUT/VALIDATION/ERROR_HASH/REUSE 구조를 추가.
- 2026-08-09: 단일 운영 원본 생성. 관찰자 모드, 결과 게이트, 외부증거, Chat/Work/Codex 분리, 껍데기 차단, 이메일 수집, 고객 컨택, 안내서, 메타데이터, 도구개발 규칙을 최초 통합.

<!-- WIC_CANONICAL_FEEDBACK_START -->
```json
{
  "records": [
    {
      "active": true,
      "classification": "CONSTRAINT",
      "feedback_id": "20260820_persistent_feedback_only",
      "impacted_layers": [
        "GLOBAL"
      ],
      "sanitized_excerpt": "모든 자연어 지적·정정·누락·형식변경·금지사항·운영변경을 피드백 후보로 분류하되, 영구 운영규칙/지속 적용만 중앙마스터에 반영한다. 일회성 질문·정보조회·현재 상태 확인은 저장하지 않으며, 한 메시지에 섞여 있으면 영구 부분만 분리 반영한다. 애매하면 HOLD한다.",
      "supersedes": [],
      "targets": [
        "CENTRAL"
      ]
    },
    {
      "active": true,
      "classification": "CONSTRAINT",
      "feedback_id": "20260813_table_reporting",
      "impacted_layers": [
        "GLOBAL"
      ],
      "sanitized_excerpt": "모든 업무 대화창과 도구의 진행상황·점검결과·작업상태 보고는 테이블을 먼저 사용한다. 실제 실행/근거, 남은 작업, PASS/HOLD/FAIL을 한눈에 보이게 하고 텍스트 덩어리만으로 보고하지 않는다.",
      "supersedes": [],
      "targets": [
        "CENTRAL"
      ]
    },
    {
      "active": true,
      "classification": "CONSTRAINT",
      "feedback_id": "20260813_work_rule_split",
      "impacted_layers": [
        "GLOBAL",
        "WORKGROUP",
        "TOOL_OR_DOMAIN_OVERRIDE"
      ],
      "sanitized_excerpt": "Work에서 수행하는 구현/E2E 작업과 대화기록·규칙·GitHub 통합은 서로 상관없는 별도 작업이다. Antigravity에서 이미 추출한 RAW/tool_mapped/extracted_rules 결과를 재사용하고 이후 누적 규칙만 증분 통합한다. 규칙 회수·재정리·과거 자료 재추출에는 Work 크레딧을 사용하지 않는다.",
      "supersedes": [],
      "targets": [
        "CENTRAL",
        "WORK_GATE"
      ]
    },
    {
      "active": true,
      "classification": "PRIORITY_CHANGE",
      "feedback_id": "37a4a2166bb5e2a08a8c",
      "impacted_layers": [
        "GLOBAL",
        "WORKGROUP",
        "TOOL_OR_DOMAIN_OVERRIDE",
        "DATA_OR_EXECUTION_ASSET"
      ],
      "sanitized_excerpt": "최우선은 WIC 전체 자동 통합 기반 구조의 실제 완성이다. 실제 새 피드백이 자동 분류, 충돌검사, 중앙 반영, 대상 적용, read-back, 테스트, restart point까지 성공해야 구조 PASS다. Work는 Chat/GitHub에서 막히는 실행과 E2E에만 사용한다. 구조 PASS 뒤 우선순위는 이메일 수집, 7번, 1번 안내서, 37 메타데이터, 13 엑셀, 6번 목차, 2번 입찰, 28~31, 나머지다.",
      "supersedes": [
        "f2aeb4e8f5fac3c9618f"
      ],
      "targets": [
        "CENTRAL",
        "EMAIL_DB",
        "TOOL001",
        "TOOL002",
        "TOOL006",
        "TOOL007",
        "TOOL037",
        "WORK_GATE"
      ]
    },
    {
      "active": true,
      "classification": "CORRECTION",
      "feedback_id": "686c809c68d37af1540f",
      "impacted_layers": [
        "GLOBAL",
        "DATA_OR_EXECUTION_ASSET"
      ],
      "sanitized_excerpt": "정정: 무허가 작업·예약·대화창 생성 및 중복 작업의 근본 해결 규칙은 WIC_GLOBAL_OPERATING_RULES.md 단일 원본에 통합해야 한다. 사용자의 명시적 승인 없이 새 대화창 생성·명명·변경을 금지하고, 보고·계속·재개·검증 지시나 예약 허가를 새 대화창 권한으로 확대하지 않는다. 직접 확인한 UI 제목 증거가 없으면 UI_TITLE_HOLD로 처리한다. 동일 목적의 규칙·감시·복구·보고 작업은 새로 만들지 않고 기존 대표 규칙과 대조해 중복 제거한다. WIC_CHAT_ROUTING_REGISTRY.md 같은 비규범 문서에는 새로운 실행 규칙이나 TOOL별 DELTA를 추가하지 말고 라우팅·호환 정보만 유지한다. 무허가 새 대화창·이름변경 0건, 신규 중복규칙 0건, 기존 정상 작업 영향 0건을 실제 검증하기 전에는 최종 PASS로 처리하지 않는다.",
      "supersedes": [],
      "targets": [
        "CENTRAL"
      ]
    },
    {
      "active": true,
      "classification": "CONSTRAINT",
      "feedback_id": "7372f5d45a6e681d4add",
      "impacted_layers": [
        "GLOBAL"
      ],
      "sanitized_excerpt": "모든 기존 및 앞으로 만드는 일반·도구 대화창은 새 작업 시작 시 해당 중앙마스터와 최신 체크포인트를 먼저 읽도록 고정하라. 피드백은 업무군 식별, 중앙마스터 중복·충돌 검사, 최소 수정, 실행 오류 게이트 수정, 체크포인트, commit/push, 원격 read-back, Commit SHA 확인까지 처리하고 사용자가 이전 규칙을 다시 복사하지 않게 하라. 기존 도구는 재사용하고 미등록 신규 도구는 기존 공통 구조로 먼저 분류하라.",
      "supersedes": [],
      "targets": [
        "CENTRAL"
      ]
    },
    {
      "active": true,
      "classification": "CONSTRAINT",
      "feedback_id": "b6acdbfd3bc4d0de1b66",
      "impacted_layers": [
        "GLOBAL",
        "TOOL_OR_DOMAIN_OVERRIDE",
        "DATA_OR_EXECUTION_ASSET"
      ],
      "sanitized_excerpt": "고객 안내서 추천 보고서는 타이틀 자체가 글로벌 시장 범위를 대상으로 해야 하며 Asia Pacific, North America, Europe처럼 단일 지역만 대상으로 한 타이틀은 제외한다. 단 글로벌 보고서 제목 뒤에 여러 지역이 함께 나열되는 것은 허용한다. 목차는 상위 목차와 하위 목차까지만 표시하고 하하위 목차는 제외하며, 하위 목차는 상위 목차보다 한 단계 오른쪽으로 들여쓴다. 보고서 정보는 공식 상세페이지의 실제 텍스트 문단만 한국어로 번역하고 그래프·차트·이미지·도표를 모델이 해석해 문장으로 재구성하는 것은 금지한다. 표시한 섹션/위치/줄 번호의 실제 원문과 번역 내용이 직접 대응해야 한다.",
      "supersedes": [],
      "targets": [
        "TOOL001",
        "TOOL006"
      ]
    },
    {
      "active": false,
      "classification": "PRIORITY_CHANGE",
      "feedback_id": "f2aeb4e8f5fac3c9618f",
      "impacted_layers": [
        "GLOBAL",
        "WORKGROUP",
        "TOOL_OR_DOMAIN_OVERRIDE",
        "DATA_OR_EXECUTION_ASSET"
      ],
      "sanitized_excerpt": "GitHub 중앙 상태의 최신 restart point와 WIC_OBSERVER_STATUS.md를 먼저 읽고 완료 작업은 반복하지 마라. 2026-08-13부터 Work를 사용할 때의 최우선 1순위는 개별 도구 개발이 아니라 WIC 전체 자동 통합 기반 구조 자체를 실제로 완성하는 것이다. 이 구조는 모든 주요 대화창/도구의 새 피드백·오류·규칙을 최소 재분석으로 흡수하고, 공통마스터→업무군→분야/도구 예외→데이터/실행자산 계층에 자동 라우팅하며, 기존 규칙과 충돌검사·중복제거·deprecated/HOLD 판정·단일원본 갱신·해당 도구 즉시 참조·read-back/테스트·restart point까지 한 파이프라인으로 처리해야 한다. 단순 스크립트/문서 존재는 완료가 아니며 실제 새 피드백 1건 이상을 넣어 자동 분류→충돌검사→중앙 GitHub 반영→대상 도구 read-back/적용→테스트 증거까지 성공해야 구조 PASS다. 이 구조가 실제 PASS한 뒤 우선순위는 이메일 수집→7번",
      "supersedes": [],
      "targets": [
        "CENTRAL",
        "EMAIL_DB",
        "TOOL001",
        "TOOL002",
        "TOOL006",
        "TOOL007",
        "TOOL013",
        "TOOL037",
        "WORK_GATE"
      ]
    },
    {
      "active": true,
      "classification": "CONSTRAINT",
      "feedback_id": "b51d5eda93f7bece6b5f",
      "impacted_layers": [
        "GLOBAL"
      ],
      "sanitized_excerpt": "앞으로 중앙마스터 피드백 수정은 기존 규칙과 canonical feedback record를 손상시키지 않고 DIFF ONLY로 반영해야 한다. 수정 전 기준선 해시와 수정 후 목록·해시를 비교하여 의도하지 않은 삭제·축약·변경이 하나라도 있으면 push를 금지하고 원상복구한다.",
      "supersedes": [],
      "targets": [
        "CENTRAL"
      ]
    },
    {
      "active": true,
      "classification": "CONSTRAINT",
      "feedback_id": "72c2843cb52fd87ee879",
      "impacted_layers": [
        "GLOBAL"
      ],
      "recur_count": 1,
      "root_cause_id": "72c2843cb52fd87ee879",
      "sanitized_excerpt": "앞으로 WIC에서 사용자가 명시적으로 요청하지 않은 새 대화창 생성, 대화창 이름 변경, 예약 생성, 자동화 활성화, 자동 작업 생성을 금지한다.",
      "supersedes": [],
      "targets": [
        "CENTRAL"
      ]
    }
  ],
  "schema_version": 1
}
```
<!-- WIC_CANONICAL_FEEDBACK_END -->


<!-- TOOL006_USER_ACTION_AND_INCREMENTAL_CANONICALIZATION_LOCK_START -->
## 19C. TOOL006 단일 실행·단일 복구 행동 및 전 TOOL 증분 정본화 LOCK

### TOOL006 사용자 행동 계약

- `NORMAL_USER_ACTION <= 1`: 정상 사용은 `자료 입력 → 실행 1회 → 결과`로 끝낸다.
- `ERROR_RECOVERY_USER_ACTION <= 1 additional action`: 오류 시 사용자의 추가 행동은 `자가분석·개선` 1회까지만 허용한다.
- 그 한 번의 내부 경로는 `오류감지 → 자가분석 → root 분류 → 검증된 기존규칙 적용 → 안전보정 → 재검사`를 일괄 수행한다.
- 분석·분류·보정·재검사를 사용자가 여러 메뉴로 순차 실행하게 하지 않는다.
- 효과가 복잡 목차에서 검증되기 전에는 자가분석 상태를 무조건 숨기지 않는다.
- 추가 1회로 해결되지 않으면 반복 클릭을 요구하지 않고 `HOLD + 실패 원인`으로 종료한다.
- 단순 목차 PASS만으로 TOOL006 전체 COMPLETE를 판정하지 않는다.

### 모든 TOOL / 모든 Work의 USB→GitHub 증분 정본화 계약

- `USB_FULL_AUDIT=FORBIDDEN`; 현재 작업에서 직접 만난 자산만 증분 확인한다.
- 각 자산은 `CANONICAL_NORMAL / SHELL_OR_STALE / HOLD_UNKNOWN` 중 하나로 근거 기반 분류한다.
- 검증된 `CANONICAL_NORMAL`만 기존 해당 TOOL GitHub/CENTRAL 정본으로 승격한다.
- `GITHUB_CANONICAL=TRUE`; `USB_CANONICAL_STORAGE=FORBIDDEN`; `USB_VERIFIED_COPY_STORAGE=FORBIDDEN`.
- `NEW_REPO_FOR_REUSE=FORBIDDEN`; `DUPLICATE_VERIFIED_STORAGE=FORBIDDEN`.
- 정본화 완료에는 remote commit/SHA, 필요한 blob SHA, remote content read-back과 변경범위 최초 검증 근거가 모두 필요하다.
- Work는 USB 파일을 자동 삭제하지 않는다. `HOLD_UNKNOWN` 또는 USB에만 존재하는 필요한 미보존 원본이 있으면 해당 확인범위의 `USB_DELETE_READY=FALSE`다.
- DELETE_READY는 현재 확인범위에만 판정하며 USB 전체로 확대하지 않는다.
<!-- TOOL006_USER_ACTION_AND_INCREMENTAL_CANONICALIZATION_LOCK_END -->


<!-- WORK16_RECOVERED_EXECUTION_LOCKS_START -->
## 19D-0. TEST BEFORE DEPLOY / GLOBAL REAL-USE VALIDATION LOCK

- 모든 WIC 변경의 강제 순서는 `수정 → 실제 업무 입력 E2E → 최종 출력 검증 → 영향받은 기존 기능 회귀검사 → 오류 수정 → 동일 실패 입력 재테스트 → PASS 후 GitHub 반영 → remote SHA/file read-back → 기존 로컬 실행폴더 배포 → 배포된 canonical 파일 자체 E2E → 완료`다.
- `CODE_PASS / SMOKE_PASS / E2E_PASS / DEPLOYED / DEPLOYED_E2E_PASS / REAL_USE_PASS`를 분리한다. 마지막 필수 단계의 실제 증거가 없으면 `BLOCKED` 또는 `DEPLOY_INCOMPLETE`다.
- `행 0 / UNKNOWN / 빈 출력 / 중간 정지 / 오류 은폐 / 버튼 무반응 / 미리보기 미생성 / 다운로드 실패 / 입력 일부 누락 / 데이터 혼합 / 예상 결과 불일치` 중 하나라도 있으면 release를 차단한다.
- 실패 입력을 쉬운 fixture로 교체해 PASS시키지 않는다. 동일 실제 입력으로 수정 전 FAIL과 수정 후 PASS를 모두 보존한다.
- 개발본과 배포본이 다르면 FAIL이다. GitHub canonical과 로컬 canonical의 hash/content 일치 및 배포본 재실행 증거를 요구한다.
- 공통 실행 gate는 `feedback_pipeline/deployment_observer_gate.py`와 `feedback_pipeline/work_execution_enforcer.py`다. 문서만 추가하고 runtime gate를 생략할 수 없다.

## 19D. Work 16 회수 운영 고정규칙 — 실행 연속성·승인 최대 병합

### 조사·반복 차단

- `FULL_AUDIT_BLOCKED = TRUE`; `FULL_AUDIT = FORBIDDEN`; 현재 작업과 직접 연결된 범위만 증분 확인한다.
- `FULL_SYSTEM_RESCAN = FORBIDDEN`; `REPEAT_CROSS_TOOL_SWEEP = FORBIDDEN`; 다음 작업을 찾기 위해 전체 TOOL·GitHub·채팅·과거 기록을 다시 훑지 않는다.
- `REPEAT_WORK_BLOCKED = TRUE`; `RECHECK_EXISTING_PASS = FORBIDDEN`; 기존 `PASS / VERIFIED / REMOTE_VERIFIED / COMPLETE`는 영향받지 않은 한 `SKIP_REUSE`한다.
- 같은 조건의 실패·검증·승인을 반복하지 않는다. 새 변경의 영향범위만 `FIRST_VALIDATION` 1회 수행한다.

### 완료 우선·실행 연속성

- `PRIORITY_MODE = FASTEST_TO_COMPLETE`; `COMPLETE_CLOSE_FIRST = TRUE`.
- 외부자료·사용자 추가자료 없이 독자적으로 닫을 수 있고 COMPLETE까지 남은 작업량이 가장 적은 기존 OPEN/INCOMPLETE부터 처리한다.
- `BLOCKED_DOES_NOT_END_WORK = TRUE`; `REPORT_DOES_NOT_END_WORK = TRUE`; HOLD/WAIT/BLOCKED_EXTERNAL은 붙잡지 않고 다음 내부 완료 가능 항목으로 이동한다.
- `VERIFIED_COMPONENT_REUSE = TRUE`; `REBUILD_VERIFIED_COMPONENT = FORBIDDEN`; 동일 기능은 검증된 구성요소를 재사용하고 달라진 연결부만 최초 검증한다.
- 새 repo, 새 프로젝트, 중앙 작업공간 복제품을 임의 생성하지 않는다.

### SAFE 승인 최대 병합

- `APPROVAL_REQUESTS = MAXIMALLY_BATCHED`
- `ONE_APPROVAL_FLOW_PREFERRED = TRUE`
- `DEFER_SAFE_APPROVAL_UNTIL_BATCH_READY = TRUE`
- `REPEAT_APPROVAL_SAME_SCOPE = FORBIDDEN`
- `SAFE_SCOPE_ONLY = TRUE`
- 같은 repo·목적·변경세트의 비파괴 SAFE 작업은 승인 없는 준비와 변경 계산을 먼저 끝낸 뒤, 플랫폼이 허용하는 최대 한 승인 흐름으로 묶는다.
- 가능한 경우 `network access → file write → blob → tree → commit → main fast-forward → remote read-back`을 연속 처리하며 파일별·단계별로 임의 분할하지 않는다.
- 플랫폼이 단계별 승인을 강제하는 경우에만 같은 SAFE 범위의 추가 승인창을 허용하며 이를 우회·자동 클릭하지 않는다.
- 승인 대기 작업은 `WAIT_APPROVAL`로 분리하고 승인 불필요 SAFE 작업을 계속한다.
- 삭제, USB 삭제, force push, destructive reset, repo 초기화·생성, 대량 이동·삭제 및 복구 곤란 변경은 SAFE batch에 포함하지 않는다.
- 승인 후 중간 보고로 멈추지 않고 가능한 범위에서 commit, remote SHA와 content read-back까지 닫는다.
<!-- WORK16_RECOVERED_EXECUTION_LOCKS_END -->

## WIC MASTER 선행 로드 게이트 (모든 현재/미래 WIC 작업)

WIC와 무관한 일반 개인 대화에는 적용하지 않는다. 현재 존재하는 모든 WIC 대화창·TOOL·Work와 앞으로 생성되는 모든 WIC 대화창·신규 TOOL은 검색·판단·출력·개발·수정·검증·배포 전에 아래 순서를 완료해야 한다.

1. WIC 중앙 공통마스터 최신 정본을 로드한다.
2. CENTRAL registry에서 대상 TOOL을 해석하고 해당 TOOL의 최신 canonical master를 로드한다.
3. 해당 TOOL의 latest checkpoint/handoff를 로드한다.
4. 세 단계의 경로·repository·revision/SHA·content hash read-back receipt가 모두 확인된 경우에만 작업 진입을 허용한다.

`MASTER_LOAD_BEFORE_WORK = REQUIRED`
`WORK_WITHOUT_MASTER_LOAD = FORBIDDEN`
`NEW_WIC_CHAT_MASTER_LOAD_REQUIRED = TRUE`
`MASTER_LOAD_FAIL = HOLD`
`GUESS_WITHOUT_MASTER = FORBIDDEN`

TOOL master가 아직 없으면 중앙 공통마스터 로드 후 기존 registry·canonical·흡수/통합 관계만 좁게 확인하고 `TOOL_MASTER_NOT_FOUND / HOLD`로 판정한다. 임의 규칙이나 추정 경로로 작업을 시작하지 않는다. 경로와 SHA는 registry에서 자동 해석하며 사용자에게 반복 요청하지 않는다. 기존 PASS/VERIFIED/REMOTE_VERIFIED 구조는 SKIP_REUSE하고 변경 연결부만 DIFF ONLY로 처리한다.

## WIC Observer-First 실행·배포·반복문제 자동판별 (모든 현재/미래 WIC 작업)

이 블록은 WIC와 무관한 일반 개인 대화에는 적용하지 않는다. 현재 존재하는 모든 WIC TOOL·Work·Codex 작업과 앞으로 생성되는 모든 WIC TOOL·대화창에 적용한다.

### 기본 실행·배포 순서

1. Work/Codex가 승인 없이 가능한 준비·실행·검증·증거 정리를 먼저 끝낸다.
2. 배포는 (a) Work가 끝까지 수행 가능한 방식, (b) 기존 PASS/VERIFIED 배포 구조 재사용, (c) 사용자가 로컬 파일 하나를 실행·선택하는 단일 행동, (d) 다단계 웹 설정 순으로 선택한다.
3. 가능한 경우 Work가 배포 실행, 공개 URL 확인, 변경범위 FIRST_VALIDATION 1회, 증거 저장, 완료판정까지 연속 처리한다.
4. 사용자 행동이 본질적으로 필요하면 준비를 먼저 끝낸 뒤 경로·파일·버튼·행동을 하나의 요청으로 최대 병합한다. 같은 범위의 행동·승인·경로 설명을 반복 요구하지 않는다.
5. 기존 PASS/VERIFIED/REMOTE_VERIFIED 배포·실행 구조가 있으면 재개발·재검증하지 않고 새 TOOL의 연결부만 DIFF ONLY 처리한다.

### 문제 자동분류

- `TEMPORARY`: 이번 화면·권한·파일·상황에만 해당한다. 현재 작업에서만 해결하고 전역화하지 않는다.
- `TOOL_SPECIFIC`: 특정 TOOL 고유 문제다. 해당 TOOL master/checkpoint에만 반영한다.
- `COMMON_RECURRING`: 여러 TOOL/Work/Codex에서 반복되거나 재발 가능성이 높은 구조적 문제다. 중앙 공통규칙 후보로 승격한다.
- `EXISTING_COMMON_REUSE`: 이미 PASS/VERIFIED된 공통 해결책이 있다. 새로 개발하거나 동일 검증을 반복하지 않고 그대로 재사용한다.

같은 버튼 반복, TOOL별 GitHub 설정 반복, 경로·파일 재질문, 유사 승인 반복, 시스템 검증을 사용자에게 전가, 기존 정보를 재질문, 검증된 배포구조 재개발, TOOL마다 같은 수동절차 재시작은 작업 중 자동 감지하여 위 네 분류 중 하나로 판정한다. 단일 화면 상태나 일시적 권한 문제를 근거 없이 WIC 전체 규칙으로 확대하지 않는다.

`OBSERVER_FIRST = REQUIRED`
`OBSERVER_FIRST_DEPLOY = REQUIRED`
`USER_MANUAL_ACTION = MINIMIZE`
`REPEAT_USER_ACTION = FORBIDDEN`
`REUSE_VERIFIED_COMPONENT = REQUIRED`
`REUSE_VERIFIED_DEPLOYMENT = REQUIRED`
`RETEST_UNCHANGED_VERIFIED_COMPONENT = FORBIDDEN`
`FIRST_VALIDATION_ONCE = REQUIRED`
`COMMON_RULE_AUTO_CLASSIFICATION = REQUIRED`
`TEMPORARY_ISSUE_AUTO_GLOBALIZATION = FORBIDDEN`

## WIC COMPLETE 수렴형 통합 실행 (모든 현재/미래 WIC 작업)

번호순 반복순회보다 실제 COMPLETE 증가를 우선한다. 현재 상태에서 `COMPLETE까지 남은 안전 작업량 / 재사용 효과 / 병목 해제 효과 / 외부 의존성 / 실패 위험`을 비교해 가장 빠른 전략을 선택한다.

### 상태 분류
- `READY_TO_COMPLETE`: 현재 권한·자료·PASS 부품으로 실제 완료 가능.
- `WAITING_FOR_REUSABLE_COMPONENT`: 특정 검증 부품이 생기면 완료 가능.
- `BOTTLENECK_COMPONENT_REQUIRED`: 여러 TOOL이 같은 기능을 실제로 기다림.
- `EXTERNAL_TRIGGER_HOLD`: 외부자료·승인·실사용 증거 없이는 진행 불가.
- `COMPLETE / PASS / REMOTE_VERIFIED`: 동일 조건 재작업·재검증 금지.

### 전략 선택
- `COMPLETE_FIRST`: READY 중 가장 적은 안전 작업으로 닫히는 TOOL 우선.
- `DEPENDENCY_WAVE`: 새 PASS/REMOTE_VERIFIED 부품을 기다린다고 이미 확인된 TOOL만 즉시 연결.
- `BOTTLENECK_COMPONENT`: 여러 TOOL의 실제 병목이면 별도 공통화 프로젝트가 아니라 현재 실제 TOOL 안에서 최소 구현·검증한다.
- `BATCH_CLOSE`: 같은 검증 부품으로 가까운 TOOL 여러 개가 닫히면 atomic unit별로 연속 처리.
- `EXTERNAL_HOLD_SKIP`: trigger 전에는 반복 방문하지 않는다.
- `ROUND_ROBIN`: 특별한 근거가 있을 때만 제한적으로 사용하며 기본 전략으로 삼지 않는다.

### trigger 기반 재방문
같은 TOOL은 새 PASS/REMOTE_VERIFIED 부품, 외부 trigger 충족, 실제 새 오류, 사용자 신규 요구, HOLD 해제 근거 중 하나가 있을 때만 재방문한다. 상태변화 없는 반복순회는 금지한다. 신규 COMPLETE·신규 재사용 PASS·해제 HOLD가 계속 0이면 같은 전략을 반복하지 않고 병목과 전략을 변경한다.

`ROUND_ROBIN_REPEAT = FORBIDDEN`
`TRIGGER_BASED_REVISIT_ONLY = TRUE`
`REBUILD_VERIFIED_COMPONENT = FORBIDDEN`
`RETEST_UNCHANGED_VERIFIED_COMPONENT = FORBIDDEN`
`FIRST_VALIDATION_ON_CHANGED_SCOPE_ONLY = TRUE`

### 중단 안전 atomic unit
각 작업은 가능한 한 `수정 → 변경범위 FIRST_VALIDATION 1회 → PASS → canonical commit → remote read-back → 다음 unit` 순서로 독립 종료한다. 현재 unit을 안전하게 닫을 수 없으면 미검증 변경을 canonical에 반영하지 않고 마지막 VERIFIED 상태를 보존한다. 크레딧·시간 소진이 임박하면 새 대형 작업을 시작하지 않는다. runtime/master/manifest/checkpoint 중 일부만 바뀐 불일치 상태와 검증되지 않은 배포 COMPLETE 판정을 남기지 않는다.

`PARTIAL_BROKEN_STATE = FORBIDDEN`
`SAFE_ATOMIC_PROGRESS = REQUIRED`
`LAST_VERIFIED_STATE_PRESERVE = REQUIRED`
`NO_NEW_LARGE_SCOPE_NEAR_CREDIT_EXHAUSTION = TRUE`
`UNVERIFIED_PARTIAL_CHANGE_TO_CANONICAL = FORBIDDEN`

### 보고 집계
각 보고에는 번호·실제 도구/대화창명·시작상태·이번 작업·현재상태·새 재사용 부품·연결 TOOL·남은 작업·HOLD/trigger·지연원인을 표시한다. 또한 신규 COMPLETE 수, 신규 PASS/REMOTE_VERIFIED 재사용 부품 수, 재사용으로 해제된 HOLD 수, 외부 trigger HOLD 수, 불필요 동일상태 재방문 수를 집계하며 마지막 항목의 목표값은 0이다.

`FULL_AUDIT = FORBIDDEN`
`AUTO_EXPAND_SCOPE = FORBIDDEN`
`FULL_COMMONIZATION_PROJECT = FORBIDDEN`
