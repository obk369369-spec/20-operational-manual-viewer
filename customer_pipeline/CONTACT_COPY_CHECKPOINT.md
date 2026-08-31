# TOOL007 / TOOL042 멘트 개선 — 2026-08-31

범위: 실제 고객 3건의 첫 질문/후속 멘트와 답변 분기. 전체 안내서·견적 이메일 재개발, 실제 고객 발송, 278개 대화 정본화는 하지 않음.

| 실제 사례 | 이전 문제와 사용자 피드백 | 개선 질문 | 검토 |
|---|---|---|---|
| ROB-010 회사소개서 발송 후 유선 미사용 | 휴대전화 회신 요구, 정기 안내 허락을 얻으려는 목적이 드러난다는 최근 지적 | 재난로봇과 의료로봇 중 요즘 더 살펴보시는 쪽이 있을까요? | 발송은 관심 증거가 아님. 이메일 초안만 작성, 번호 요구 없음. |
| SEM-071 실제 통화·국내 보고서 요청 | 이미 국내 보고서와 두 분야 요청이 있는데 일반적인 관심분야 질문 반복 | 방산용 반도체와 시험 장비, 두 분야 모두 보면 될까요? | 직전 문장에서 국내 보고서 요청을 회수. 전문어를 줄이고 범위만 확인. |
| 경남테크노파크 실제 견적 문의 | 주문·결제·고객등록·이용전환 설명이 긴 첫 안내 | 견적에서 더 확인하실 내용이 있을까요? | 실제 문의를 연결한 후 한 질문. 견적 계약조건 자체를 삭제하거나 변경한 것이 아님. |

출처는 `contact_copy_actual_cases.json`의 source_ref와 원문 발췌에 보존. 현재 42번 사용자 정정 `cc87c8e2-8873-465a-b241-88e3349e90be` 포함. 이전 42번 관련 300줄 첨부의 해당 고객 구간과 해당 EML만 회수. 전체 archive 조사 없음.

자연스러움 평가는 작성자 문장 검토이며 실제 통화 녹음·고객 호응 PASS가 아니다. verified 입력은 회수된 당시 사례이며 현재 재직 상태의 신규 검증이 아니다.

## 실행 / 한계

- 7번 `tool7_contact_judgment.py:prepare_contact_copy` 및 `--copy-stdin`.
- 42번 `scripts/customer_branch_engine.js:branchCustomer`에서 `prepareContactCopy` 호출. 추천 판정과 멘트 판정 분리.
- 두 native 경로에 3건씩 CLI input→output: `test_contact_copy_quality.py`, 결과 `contact_copy_validation.json`.
- STOP/OTHER/LATER/SCOPE/CONFIRMED 분기, 출처 누락, 발송→문의 오인, 장문·질문 중복·압박 표현 차단.
- recommendation_allowed는 확인된 범위의 자료 검토 단계만 의미. send_allowed=false. 자동 발송/동의 추정 없음.
- DRAFT_VALIDATED는 문장 제약 검사 결과. 일반 Chat 자동 호출, 사용자 품질 승인, 실제 고객 응답 효과, TOOL 전체 완료를 의미하지 않음.

## 체크포인트

- CENTRAL 시작: `9237d2bbe3f78e2a47c8da39ff32dd3bfc24326b`.
- TOOL042 시작: `b340c701f08a95594af27c12830417aba3bff91e`.
- 본 파일을 포함하는 commit이 로컬 변경 단위. 실제 push 및 SHA/file read-back 전 원격 승격 금지.
- PUBLICATION: PENDING. 이후 원격 read-back 영수증으로 확인하며 이 로컬 기록만으로 PASS 금지.
- NEXT_START: 두 저장소 변경 commit의 정상 push/read-back. 이후 새로운 실제 멘트 피드백만 기존 2026-08-11 고객 전화 컨택 멘트 보완 root와 scoped 대조.
- 일반 Chat 자동 호출 및 실제 통화 품질 전체 검증: NOT_VERIFIED. 사용자에게 테스트 전화나 자료 재전달을 요구하지 않는다.


## 2026-08-31 — TOOL041/042 native 자동 선조회 연결 증분

- 최신 정본은 이번 Work가 직접 조회했으며 사용자 checkpoint/피드백 재전달 0회.
- TOOL041 current-master guard / TOOL042 CLI native preload 연결: 구현 및 변경부 9개 검사 PASS. 구현 8개 파일 remote read-back exact MATCH.
- 인증된 GitHub connector snapshot으로 preload→generation 연결을 검증했다. Native shell private GitHub 인증 및 실제 최신 고객 판매자료 E2E는 검증하지 못했다.
- 실제 최근 실패 ACTUAL-OUTBOUND-EMAIL-FIRST: FAIL 문구의 turns/cue_card 누출 차단, 다른 질문으로 1회 역사 재현 DRAFT_VALIDATED. 실제 최신 CLEAN MASTER에서는 ROB-010 식별이 고유 연결되지 않아 HOLD.
- TOOL041 과거 actual fixture는 현재 필드 부족으로 HOLD; 과거 데이터를 CLEAN MASTER로 되살리지 않음.
- 실제 판매자료 필수 paid/tradable/source 누락은 문구 생성 전 차단.
- 자동 의미검사 8개 전부/자유 재작성/native 종료 자동 저장/모든 진입점 강제는 아직 내부 OPEN. 외부·근거 HOLD와 구분한다.
- 본 Work 결과 저장은 agent GitHub connector로 수행했으므로 native 자동 저장 PASS로 주장하지 않는다.
- 기존 정상 테스트/43번 actual-device PASS는 SKIP_REUSE, 동일 실패 재실행 없음.
- Root: T41-T42-NATIVE-AUTOMATION; 증거: customer_pipeline/TOOL041_042_AUTOMATION_20260831.json. 다음 작업은 위 root의 미연결부 및 실제 고객 1건만.


## 2026-08-31 — 단일 FAIL-CLOSED 출력 경계 연결

- 기존 c53e4b142ae6bc8f71a5572e388188bc0f660c7f PASS는 SKIP_REUSE; 전수조사/기존 fixture 재실행 없음.
- CENTRAL `customer_pipeline/customer_release_gate.py` 동일 코드가 41·42에 배포되며, 선조회 source와 구현 본문 불일치 시 HOLD.
- 공개 native 진입점과 guidance emit 경로는 공통 최종 게이트를 거친다. 기존 내부 생성기/format test는 출력 허가가 아니다.
- 실제 과거 실패 입력 2건의 원문을 그대로 넣어 USER_EXPLICIT_FAIL 차단, 기존 교정안으로 각 1회 내부 재작성. 재작성문도 최종 의미판정 없이는 출력하지 않음.
- 8항목 의미실행기 미연결: 전 항목 HOLD_NOT_EXECUTED. 현재 revision은 고객 PASS 출력 자체를 허용하지 않음. 정규식/해시 로그를 의미검사 완료로 주장하지 않음.
- 사용자 지정 고객은 제한 검색과 현재 CLEAN MASTER에서 연결 근거 미확보. 다른 고객으로 대체하거나 과거 삭제 데이터를 복원하지 않음.
- Native 저장은 기존 CENTRAL root의 redacted CAS update/read-back/idempotency 연결. 모의 검증 PASS와 실제 인증 저장 미검증을 구분.
- 내부 OPEN: 실제 의미실행기, 자연어 구규칙 충돌 해결, 자유 재작성. HOLD: 지정 고객 현재 식별/접촉·실패원문·실제 자료 및 runtime 인증.
- NEXT_WORK: 실제 source/customer/output-bound 의미실행기 및 해당 고객 근거가 연결되면 남은 positive 고객 E2E/인증 저장만 검증. 이번 차단경계 검사는 반복 금지.
- 증거: CENTRAL `customer_pipeline/TOOL041_042_RELEASE_GATE_20260831.json`. 사용자 수동 전달 0회, 실제 발송 없음.


## 2026-08-31 — 의미검사 실행층 한정 HOLD 확정

- 9e63063264234fc2df24a3e135cf7fc57c6ad0c9 PASS 범위 SKIP_REUSE. 기존 차단/FAIL/모의저장 재검사 0회, 코드 수정 0건, 모델 호출 0회.
- 정확한 차단: customer_release_gate.py:73은 8항목 HOLD_NOT_EXECUTED 고정이며 모델 호출 없음. 42번 customer_release_bridge.js는 HOLD 응답만 수용하도록 되어 있음.
- 현재 process/user 환경에 모델 API 인증·endpoint·semantic reviewer 설정 없음. 설치된 Codex CLI login status 1회는 'Could not find home directory' 설정 오류로 인증 확인 전 중단. 계정 자체의 영구 불가를 주장하지 않음.
- 필요한 실행층: 정상 설정·인증된 native 모델 호출 환경과 허용된 네트워크. 준비되면 기존 gate/bridge 안에 8항목 의미판정→1회 재작성→재판정→검증된 PASS 전달을 연결해야 함. 이번에 우회 wrapper/service 또는 키워드 검사기를 추가하지 않음.
- 현재 확보된 CLEAN MASTER의 지정 고객 이름 연결 없음: CUSTOMER_EVIDENCE_REQUIRED. 전체 대화/전체 고객 검색, 다른 고객 대체, 의미검사 PASS 주장 없음.
- 출력차단 그대로 유지. 기존 native 중앙저장 인증 HOLD도 재실행하지 않음.
- 최신 증거: customer_pipeline/TOOL041_042_SEMANTIC_EXECUTOR_HOLD_20260831.json. 다음 재개 trigger는 CONFIGURED_AUTHENTICATED_NATIVE_SEMANTIC_RUNTIME_AVAILABLE.
