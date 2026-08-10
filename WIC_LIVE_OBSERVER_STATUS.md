# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 13:50 KST
상태: ACTIVE — 고객응대 P2 실제 규칙→코드 전환

규범 원본은 `WIC_GLOBAL_OPERATING_RULES.md`. 이 파일은 실제 외부 증거와 재시작점만 기록한다. 37번=metadata production/integrated verification, 13번=Excel automatic upload로 분리 유지.

## 이번 회차 우선순위 / 피드백
- 시작 우선순위: P2 Tool7 고객 컨택 판단.
- 새 사용자 피드백: 없음. 기존 CONSTRAINT(고객응대 우선, 관찰자 역할, Chat-first)를 유지.
- 직전 P1 스키마/DB gate는 새 실행 hook 증거가 없어 재검색하지 않음: `SKIP — unchanged evidence`.

## 새로 처리한 과거 증거
- File Library `7번 고객 컨택 판단 도구 5 (새 대화창에서 이어서 진행).txt`: 17개 고객 검증/컨택 항목과 고정 출력 구조 회수.
- File Library `7번 고객 컨택 판단.doc`: 핵심 순서 `고객 상태 판별 -> 접촉 가능 여부 -> 채널 선택 -> 멘트 생성`; 멘트는 마지막이라는 사용자 승인 규칙 회수.
- File Library `7번 고객 컨택 판단 도구 7.txt`: 오래된 장부 메모는 최초 연락 이유로 사용 금지, 현재 회사/부서 최신 방향을 먼저 확인; 연구기관/기업은 자료 추천을 전화보다 우선할 수 있음; 추천자료에 최신 발행일/발행사/링크/연결 이유 필요.
- 실제 과거 고객 fixture에서 `일방 발송 메일은 고객 니즈로 과대해석 금지`, `CC 이력은 직접 문의로 표현 금지`, `회사 최신 방향 미확인 시 추천자료/멘트 금지`를 재확인.

## 실제 구현
- 신규 실제 코드: `customer_pipeline/tool7_contact_judgment.py`
- commit: `84497e2c6e4e6778f8482bdbeec84ce45ee37346`
- 구현 경계:
  1. 재직/회사방향/이직/명시적 중단을 먼저 판정하여 copy 생성 전 차단.
  2. 일방 발송과 CC-only 이력을 고객 직접 니즈/문의와 분리.
  3. 구매/직접문의/CC/일방발송/오래된 장부 메모의 사용 가능 문구를 결정형으로 분리.
  4. 연구기관·기업/자료우선 고객은 `MATERIAL_FIRST`, 그 외 허용 채널을 판정한 뒤에만 멘트 생성 허용.
  5. 추천자료는 제목/발행사/발행일/링크/유료/거래가능 검증을 통과해야 PASS.
  6. 코드 내부에 8개 deterministic fixture를 저장.
- 독립 read-back: GitHub blob `c5e8434398256ea8afb40418760c07714a898363` 확인.

## 판정
| 작업 | 상태 | 증거/블로커 | 다음 실행 |
|---|---|---|---|
| P1 기존 DB gate | SKIP — unchanged evidence | 13:14 상태 유지 | runner 발견 시 실행 |
| P2 과거 규칙 신규 회수 | PASS — evidence recovered | Tool7 Library 3계열 + 실제 고객 fixture | 처리 인덱스 갱신 |
| P2 실제 코드 구현 | PASS — stored/read-back | `tool7_contact_judgment.py`, commit `84497e2...` | exact fixture runtime 실행 |
| P2 기능 PASS | HOLD | 현재 GitHub connector read/write는 되나 코드 실행증거는 아직 없음 | Chat/일반 runtime에서 8 fixture 실행 후 판정 |
| Work 이관 | WORK_DEFER_DENIED | P2는 Chat/Files/GitHub/일반 runtime으로 계속 처리 가능 | Work 사용 금지 |

## self-improvement
- 원인: 과거 7번 규칙이 긴 출력지시문으로 남아 있고 실제 접촉허용 gate로 고정되지 않으면, 멘트를 먼저 생성하거나 일방발송을 고객 니즈로 오해하는 재발 위험이 있다.
- 변경: `상태 -> 접촉허용 -> 채널 -> 멘트` 순서를 코드 gate로 고정하고 과거 오류 8종을 fixture화했다.
- 이점: 실제 고객이 들어올 때 멘트 생성 전에 위험한 이력 과대해석을 기계적으로 차단할 수 있다.
- 새 위험: 현재 구현은 고객 최신정보를 스스로 검색하지 않는 순수 판단엔진이며, upstream 검증 데이터가 틀리면 판단도 틀릴 수 있다.
- rollback: 기존 사용자 승인 Tool7 엔진이 발견되어 의미 충돌이 확인되면 이 파일을 regression helper로 강등하고 승인 엔진을 우선한다.

## 누적 우선순위
P1: schema + DB gate 저장 / actual DB runner HOLD.
P2: historical rules -> deterministic engine 저장 / runtime fixture 실행 NEXT.
P3: P2 runtime 확인 후 Tool1 FULL/INTERMEDIATE guide 실제 mapping.
P4: P3에 필요한 개별 TOC.
P5: reply/CRM branch.
P7/P8/P9/P10: 고객업무 우선순위 이후.

## 재시작 지점
1. P2 `tool7_contact_judgment.py` 8 fixture를 일반 runtime에서 실제 실행하고 결과 기록.
2. PASS면 P1 output -> P2 input handoff adapter를 추가해 세 고객군이 동일 판단 gate로 들어가게 연결.
3. 이어서 P3 Tool1 과거 안정판/실제 guide fixture로 이동.

실행시간: duration not exposed
