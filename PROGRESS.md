# PROGRESS (최신 항목이 위)

## 대화창 번호 대장
| 번호 | 날짜 | 주제 |
|---|---|---|
| #20-01 | 2026-11-14 | 감독 워크플로 admission 수정, CLAUDE.md·PROGRESS.md 고정, 13번 아카이브 확인, 최종 무결성 점검 |

## 2026-11-14 — [대화창 #20-01] 초기화 전 최종 무결성 점검
- 결과: PASS(아래 항목) / 기준 문서 2건 없음으로 HOLD
- 기준 문서: `ALL_PROJECTS_18MONTHS_MASTER.md`, `EXTRACTED_ALL_RULES.md`는 이 저장소·13번 main 어디에도 없음 → "최신 규칙 기준 전수 재점검"은 수행 불가. 기존 정본(AGENTS.md 등) 기준 테스트만 재실행.
- 테스트: 이 저장소 tests/test_*.py 4종 PASS. 13번 저장소 rules_spec.js, openrefine_integration_template.test.js, tool13_batch_resume.test.js, tool13_v2_translation_acceptance.py PASS (실행 후 덮어쓴 추적 파일 2개는 원복).
- index.html: 변경 없음(origin/main과 동일, sha256 bed349ca…, `tool044_thin_observer_deployed.json` 기록값과 일치). 네트워크 차단 상태에서 정상 로드.
- 13번 V2 최종운영판(13번 main 8f52c3d): 네트워크 차단 상태에서 오류·외부 요청 0건, XLSX·idbKeyval 로드 확인. 단 **단일 파일이 아님** — `vendor/`, `scripts/`를 같은 폴더에 두어야 동작.
- 주의: 이 저장소의 `CONTROL_TOWER/work/tool013_user_output_closure/13번_V2_최종운영판.html`은 13번 main 버전과 내용이 다른 옛 사본이며 vendor 없이는 깨짐. 최종 산출물로 쓰지 말 것.
- git: 브랜치 claude/vigilant-brown-je3j6n 푸시 완료·작업 트리 깨끗. main에는 자동 기록 커밋만 추가됨(정본 규칙·index.html·테스트 변경 없음). main은 건드리지 않음.
- 마지막 실제 지점: 위 점검 완료. 다음 트리거: main 병합 + 변수 `WIC_RULE_ADMISSION_JSON` 교체(이전 항목), 13번 비공개 전환(개인정보).

## 2026-11-14 — [대화창 #20-01] 13번 아카이브 읽기 전용 확인 및 CLAUDE.md 반영
- 결과: PASS(확인·기록) / 이슈 해결은 해당 없음
- 증거: 13번 main 8f52c3d, `GPT_18M_PART_01~12.bin` 합침 → ZIP 무결성 통과(138개 파일). 상세는 CLAUDE.md 5절.
- 사실 정정: 범위는 2026-07-13~11-12(약 4개월), `EXTRACTED_ALL_RULES.md` 없음, 새 업무 규칙 없음(기존 정본과 동일 내용).
- 개인정보 위험(사용자 전용 조치): 공개 저장소 13번에 개인 대화(건강·육아 등)와 업무 자료 약 600MB가 올라가 있음. 비공개 전환 또는 삭제 검토 필요.
  삭제해도 git 기록에 남으므로 비공개 전환이 먼저.
- 마지막 실제 지점: CLAUDE.md 0절(번호 규칙)·5절 반영.
- 다음 트리거: 이슈 #73~#78은 승인·외부 증거 필요로 HOLD 유지.

## 2026-11-14 — [대화창 #20-01] ROOT A Recovery Supervisor 실패 원인 수정
- 결과: 수정 커밋 준비 완료(브랜치 푸시) / 실제 복구는 **HOLD — 사용자 전용 조치 1건 필요**
- 원인: 저장소 변수 `WIC_RULE_ADMISSION_JSON`에 `workflow:root-a-recovery-supervisor:supervise` 항목이 없어
  `pre_work_admission.py`가 `WORK_ADMISSION_IDENTITY_MISMATCH`로 BLOCK (런 43589793491 로그 확인, 최근 8회 연속 실패).
- 수정: `make_compact_admission.py`에 해당 work 추가 + 작업별 영수증
  `feedback_pipeline/evidence/ADMISSION_SOURCE_RECEIPT_CENTRAL_ROOT_A_RECOVERY_SUPERVISOR_20261114.json`. 기존 영수증 2건은 바이트 불변.
- 테스트: tests/test_*.py 4종 전부 통과(수정 전·후).
- 로컬 재현: 기존 변수 → BLOCK(CI 로그와 동일), 신규 값(`feedback_pipeline/evidence/WIC_RULE_ADMISSION_JSON_VALUE_20261114.json`, 해시만 포함) → ALLOW.
- 사용자 전용 조치: main 병합 후 저장소 변수 `WIC_RULE_ADMISSION_JSON`을 위 파일 내용으로 교체.
- 마지막 실제 지점: 영수증·생성기 푸시. 변수 값은 에이전트가 설정할 수 없어 미반영.
- 다음 트리거: main에 병합 + 변수 갱신 후 다음 스케줄 런(매시 :07)의 supervise 잡 성공 여부.
