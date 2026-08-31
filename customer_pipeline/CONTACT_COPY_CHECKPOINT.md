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
