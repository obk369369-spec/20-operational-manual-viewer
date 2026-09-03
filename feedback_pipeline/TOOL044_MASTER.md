# TOOL044 — 무수정 완성부품 실무 장착

실행본: `feedback_pipeline/tool044_acquire.py` (Python 표준 라이브러리, 정상 운영 유료 호출 없음).
기존 CENTRAL `work_gate_handoff`의 범위 승인을 거친 작업만 수행한다.

- 최초 파일럿: TOOL013의 3MB 초과 배치 재개 캐시. 번역 완료와 구분한다.
- 부품: idb-keyval 6.2.2, Apache-2.0, 무의존성, 공식 tarball SHA512와 원본 JS SHA256 고정.
- 실행: `python feedback_pipeline/tool044_acquire.py --acquire <sandbox>`.
- 같은 공식 패키지가 검증돼 있으면 네트워크 요청 없이 SKIP_REUSE. 일치하지 않는 기존 파일은 덮어쓰지 않고 BLOCKED.
- 배포 확인: `python feedback_pipeline/tool044_acquire.py --target <TOOL013 repo> --deployed <실제 운영폴더>`.
- 다운로드 검증은 업무 PASS가 아니다. 실제 입력/EXPECTED/ACTUAL/회귀/remote/배포본 증거가 모두 필요하다.
- 외부 부품 수정·재설계 금지. WIC 고유 매핑·판단규칙은 보존한다.
- 기능당 검색 2회, 후보 3개, 후보 기능시험 1회, 환경 재시도 1회, 대상 장착 후보 2개, 같은 실패 수정 재시도 1회 상한.
- 첫 READY 부품 통과 시 검색 종료. 같은 조건의 FAIL/HOLD 반복 금지.
- PASS 없는 후보는 canonical에 배포하거나 VERIFIED로 승격하지 않는다.

## 첫 파일럿 실제 증거

- TOOL013 코드 SHA: `3a1ce0a2f1fb9e839adec91eb37f07116941f2c3`.
- 실제 XLSX 1개 6행 재개/미리보기/다운로드 재개봉 검증.
- 4,050,383문자 160행의 제목/개요/카테고리 항목별 대조와 초기화 재열기 검증.
- `tests/tool13_idb_resume_evidence.json`, `tests/tool13_idb_deployed_evidence.json`.
- 114개/823행 기존 PASS는 파서·행 생성·변환엔진 미변경으로 SKIP_REUSE.
- Argos 번역: 모델 이용조건 미확정/설치 미완료로 미장착. NLLB: CC-BY-NC-4.0으로 상업 실무용 채택 제외.
- 번역은 다음 별도 기능이며 이번 캐시 PASS로 승격하지 않는다.
