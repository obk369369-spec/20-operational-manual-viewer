# 소형 앱 출시 실행도구 Minimal Runtime Evidence

검증일: 2026-08-17 KST
대상: `tool040/index.html` (legacy 기술 경로)
사용자-facing 도구명: `소형 앱 출시 실행도구`
대화창 제목: `소형 앱 출시`

`TOOL040` 및 `tool040`은 기존 자동 라우팅/저장 호환을 위한 legacy machine key/path이며 사용자 도구 번호가 아니다.

## GitHub 저장/read-back
- 최초 규칙 포인터 commit: `f3ccf9bf5c19530431adc3424a858d00f362c2ca`
- 최초 실행본 commit: `8a6234253fa26d0d998b62937ffba726081d8fe2`
- 명칭 정정 후 실행본 commit: `89c89496a83c8582fc72dfdba9e5d44f904763f4`

## 최소 실행 검증
GitHub read-back된 실행본과 동일한 상태 전이 로직 기준:
- 최초 판정: `HOLD`
- 아이디어 입력 + 잠금 후: `PARTIAL PASS`
- `진행 승인` 후 마지막 명령: `진행`
- evidence JSON의 `github_runtime`: `CONNECTED`
- evidence JSON의 `external_launch`: `HOLD`
- 기록 시각 생성: PASS

## 이름 중복 검증
- Library/대화 자료에서 `소형 앱 출시 실행도구` 정확 명칭의 기존 도구 사용 기록 없음
- GitHub 저장소/코드 검색에서 동일 명칭 기존 사용 없음
- `소형 앱 출시`는 실제 대화창 제목으로 확인되므로 대화창 제목은 변경하지 않음
- 과거 `40번 출시 앱 도구` 표기는 사용자 지정 번호 근거가 없어 사용자-facing 명칭에서 폐기

## 판정
- 도구명: `소형 앱 출시 실행도구` — PASS
- 대화창 제목: `소형 앱 출시` — 유지
- `TOOL040`: legacy machine key only — 사용자 번호로 사용 금지
- 실제 외부 배포/앱스토어 출시: HOLD — 별도 실행 검증 범위
