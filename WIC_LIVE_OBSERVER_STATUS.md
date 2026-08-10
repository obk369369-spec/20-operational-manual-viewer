# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 13:14 KST
상태: ACTIVE — watchdog recovery / 고객응대 P1 구현 우선

규범 원본은 `WIC_GLOBAL_OPERATING_RULES.md`. 이 파일은 실제 외부 증거와 재시작점만 기록한다. 37번=metadata production/integrated verification, 13번=Excel automatic upload로 분리 유지.

## stall / collision guard
- 직전 observer: 12:50 KST. 현재 확인시각 13:14 KST로 12분 collision window를 초과했다.
- GitHub 최신 concrete evidence도 12:52 KST commit `15378a62...` 이후 새 commit이 없었다. 따라서 겹침 실행이 아니라 stale/no-advance로 판정하고 같은 회차에서 복구했다.
- 직전 P1 스키마/과거 V5/V4 규칙은 재처리하지 않았다: `SKIP — unchanged evidence`.

## 이번 복구 실제 작업
- 저장된 재시작점 `P1 실제 고객 DB/send-ready target 연결`에서 시작.
- GitHub 중앙 repo에서 기존 customer DB 구현을 검색했으나 별도 구현 target을 식별하지 못했다.
- File Library 검색에서는 V5.0/V4.0 규칙 문서만 재확인되어 규칙 재흡수는 SKIP했다. 실제 DB artifact는 검색결과에서 식별되지 않았다.
- 껍데기 fixture 누적을 막기 위해 중앙 repo에 실행 가능한 결정형 P1 gate `customer_pipeline/customer_db_state_machine.py`를 구현했다.
- 구현: 필수필드/공식출처/실담당업무/email 검증 → `MAIN_DB / TRACKING_HOLD`; 기관+이름+email 중복 → `UPDATE_EXISTING`; 영구ID 미할당 → `MAIN_DB_PENDING_ID`; 소개서/명함 `SENT` 무근거 재발송 차단; `SEND_READY`는 명시적 발송권한 대기. 외부 발송 side effect는 항상 false.
- 코드 내 4개 결정형 fixture를 포함했다: 정상 MAIN_DB, 담당업무 누락 HOLD, 중복 UPDATE_EXISTING, 소개서 재발송/SEND_READY lock.
- 생성 commit: `9d66624b742aac678703ed89886dc3431fa3a994`.
- 독립 read-back: GitHub에서 생성 파일 전체와 blob sha `d1c7f50e...` 확인. 이 runtime에는 Python 실행 GitHub action이 없어 실제 실행 PASS는 아직 주장하지 않는다.

## 판정
| 작업 | 상태 | 증거/블로커 | 다음 실행 |
|---|---|---|---|
| P1 과거규칙 | SKIP — unchanged evidence | V5/V4 이미 흡수 | 반복 금지 |
| 기존 실제 customer DB target 탐색 | HOLD | GitHub/Library 검색에서 구현 artifact 미식별 | 새 증거가 생기기 전 같은 검색 반복 금지 |
| P1 결정형 DB gate 구현 | PASS — code stored/read-back | `customer_pipeline/customer_db_state_machine.py`, commit `9d66624...` | 실행 가능한 runner/test hook 연결 |
| P1 실제 실행 | HOLD | 현재 connector는 파일 read/write만 가능, 실행증거 없음 | 일반 runtime/CI hook 식별 시 4 fixture 실행 |
| 외부 고객 발송 | NOT EXECUTED | 자동 발송 금지 | SEND_READY까지만 관리 |

## self-improvement / structure change
- 원인: fixture와 스키마만 누적되고 실제 판정 구현이 따라오지 않으면 껍데기화와 반복 HOLD가 발생한다.
- 변경: P1을 `문서/fixture 추가`에서 `결정형 state-machine 코드 + fixture` 우선으로 전환했다.
- 이점: 실제 DB 연결 전에도 MAIN_DB/HOLD/중복/발송대기 규칙을 한 함수 경계에서 재사용·회귀검증할 수 있고, 불필요한 규칙 재검색/채팅 사용을 줄인다.
- 새 단점/위험: 아직 실제 회사 DB 저장소와 연결되지 않았고, Python runner 실행증거가 없어 저장된 코드와 실제 운영 데이터 사이에 integration gap이 있다.
- rollback 조건: 실제 고객 DB의 기존 엔진이 발견되어 필드/ID 정책과 충돌하거나 fixture 실행에서 현행 규칙과 불일치가 확인되면 이 파일을 adapter/test helper로 강등하고 기존 엔진을 우선한다. 자동 발송 기능은 추가하지 않는다.
- 검증결과: GitHub create commit + read-back PASS; execution HOLD.

## 누적 우선순위
P1 이메일/3고객군/발송대기 DB: IN PROGRESS — schema + deterministic gate 저장, 실제 DB/runner 연결 HOLD.
P2 7 고객-contact 판단: NEXT.
P3 1 정식/중간 안내서: P2 handoff 이후.
P4 개별 TOC: P3 이후.
P5 reply/CRM: state branch schema 있음, 실연결 HOLD.
P7 37 metadata: 별도 작업 유지.
P8 13 Excel upload: 별도 작업 유지.

## 재시작 지점
1. P1: 새 evidence가 없다면 기존 target 검색을 반복하지 말고 `SKIP — unchanged evidence`.
2. P2: 7번 historical actual-customer 사례를 회수해 deterministic input→expected-output fixture로 만들고 `customer_db_state_machine.py` 출력과 handoff 연결.
3. P3: P2 fixture가 저장되면 1번 FULL/INTERMEDIATE guide mapping으로 이동.
4. runner/CI가 식별되는 즉시 P1 4 fixture 실제 실행 후 PASS/HOLD 갱신.

실행시간: duration not exposed
