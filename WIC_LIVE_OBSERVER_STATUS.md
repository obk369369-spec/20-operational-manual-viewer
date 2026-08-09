# WIC LIVE OBSERVER STATUS

최종 확인: 2026-08-10 04:51 KST
상태: ACTIVE — 13번 현재 GitHub 실행본 회귀 FAIL 확인 + 6번 v2.26 실행증거 회수

이 파일은 사용자가 직접 테스트하지 않고 야간 진행을 관찰하기 위한 외부 상태판이다. 실제 외부 증거가 있을 때만 진행으로 기록한다.

## 이번 회차 실제 작업 — 04:51
- 직전 재시작 지점대로 13번 엑셀 자동 업로드의 현재 GitHub 저장소 `obk369369-spec/13-excel-upload`를 직접 확인했다.
- 현재 main/index.html의 실제 `applyField(field,row)` 코드를 read-back했다. `cfg.mode==='원본연결'`이면 `sourceValue`를 즉시 반환하고, 발행일 정규화는 preset 분기 안에서만 수행된다.
- 따라서 과거 검증에서 확인된 `원본연결 + Publishing Date=46145` 오류가 현재 GitHub 실행본에도 아직 수정 반영되지 않았음을 코드로 독립 확인했다. 13번 현재 기능 판정은 FAIL(발행일 원본연결 회귀)이다.
- 수정 범위는 기존 잠금대로 발행일 경로 하나다. `field==='발행일'`은 원본연결/preset 여부와 무관하게 최종 반환 전에 날짜 정규화를 통과해야 한다. 체제 pages, 목차/개요, 패널, trace/upload 구조는 기존 PASS 보호 대상이다.
- GitHub index.html 전체 파일은 fetch 응답이 도구 출력 한계로 절단되어 현재 제공된 update_file이 전체 replace 방식인 조건에서 안전하게 직접 수정할 수 없었다. 불완전 원문으로 덮어쓰면 실행본이 파손되므로 수정 쓰기는 HOLD했다.
- 13번에서 안전 수정이 막힌 즉시 다음 우선순위 6번 목차 정리로 이동했다.
- File Library에서 `toc_lock_v2_26_안정본_관찰패널부착_100건자동시뮬레이션.html`, `toc_lock_v2_26_운영창_자동정리실행_통합판.html`, `30번-3 검증 전용 (6번 도구).doc`를 회수했다.
- 6번 v2.26에는 `runTocStable -> render`, input/output/review_flagged, before/after/result hash, HOLD 분류, 자동진단 패킷 구조가 실제 코드에 존재함을 확인했다.
- 과거 실제 AUTO_LOG 증거에서 INPUT_COUNT=257, OUTPUT_COUNT=78, REVIEW_FLAGGED=5, TEST.DISPLAY/RUN/LOG=PASS가 기록되어 있음을 회수했다. 이는 과거 실행 증거이며 현재 최신 전체 E2E PASS로 과장하지 않는다.
- 30-3 검증 규칙의 핵심은 번호 없는 목차 후보, 반복 By 구조 depth, 긴 지역형 줄깨짐, depth 2~4, review_flag 과다, 중복번호, 줄합침, 실제 가독성을 실제 출력 기준으로 판정하고 기존 PASS 영역을 재수정하지 않는 것이다.

## 이번 회차 판정
| 작업 묶음 | 상태 | 외부 증거 | blocker / 개선 | 다음 실행 |
|---|---|---|---|---|
| 13번 현재 GitHub 저장소 식별 | PASS | `obk369369-spec/13-excel-upload`, main/index.html read-back | 없음 | 동일 저장소를 현재 실행 기준으로 사용 |
| 13번 46145 수정 반영 여부 | FAIL | main/index.html `applyField`: 원본연결 즉시 return, 날짜 변환은 preset 내부 | 과거 회귀가 현재 코드에도 존재 | 안전한 전체원문/patch 수단 확보 시 발행일 경로만 수정 |
| 13번 직접 코드 수정 | HOLD(안전) | GitHub fetch가 긴 index.html을 절단, update_file은 전체 replace | 불완전 원문 덮어쓰기 시 실행본 파손 위험 | 부분 patch 가능 수단 또는 전체 원문 확보 전 쓰기 금지 |
| 6번 v2.26 안정본/관찰판 회수 | PASS(구조) | File Library v2.26 HTML 다수 + 30-3 검증 문서 | 현재 브라우저 최신 실행 재검증은 미실행 | 최신 후보본/과거 실행로그를 대조해 PASS/HOLD 범위 확정 |
| 6번 과거 실제 실행 증거 | PASS(과거 증거) | AUTO_LOG: 257 입력 / 78 출력 / review 5 / DISPLAY·RUN·LOG PASS | 과거 실행이므로 현재 전체 기능 PASS 근거로 단독 사용 불가 | 100건 관찰판 HOLD 분류와 최신 출력 검증 규칙 대조 |
| 중앙 운영원본 실제 쓰기 | HOLD(안전) | 긴 중앙 파일 fetch 절단 문제 지속 | 전체 replace 시 규칙 손실 위험 | 안전 patch/전체원문 확보 전 쓰기 금지 |

## 13번 회귀검증 잠금
1. 13번은 엑셀 자동 업로드 도구만 의미한다.
2. 발행일 원본연결 + Publishing Date=46145가 그대로 출력되면 FAIL.
3. `field === 발행일`은 mode/preset과 무관하게 최종 출력 전 날짜 정규화 통과.
4. `2026` 같은 4자리 연도 오변환 금지.
5. 체제 `페이지수+pages`, 목차/개요, 패널, trace/upload 다운로드 기존 PASS 구조 수정 금지.
6. 실제 수정본에서 미리보기와 업로드 결과가 일치해야 최종 PASS.

## 6번 현재 회수 게이트
1. 안정본 계열은 v2.26을 기준으로 한다.
2. 실제 출력이 기준이며 META/로그만 좋아지는 수정으로 PASS 금지.
3. 번호 없는 목차 자동 번호 후보, 반복 By 구조 depth, 긴 지역형 목차 줄깨짐, depth 2~4 들여쓰기, review_flag 과다, 중복번호, 줄합침, 가독성을 검사한다.
4. PASS 영역 반복 수정 금지. 새 HTML 재구성/script 누적 덧붙이기 금지.
5. AUTO_LOG/CORE_LOG/INPUT_COUNT/OUTPUT_COUNT/REVIEW_FLAGGED는 증거로 남기되 실제 출력과 함께 판정한다.

## 번호 혼동 금지
- 37번 = 메타데이터 생산·통합검증만.
- 13번 = 엑셀 자동 업로드 도구만.
- 둘을 하나의 메타데이터 작업으로 묶지 않는다.

## PASS 기준
- GitHub 저장: write 응답 + read-back/SHA
- 기능: 실제 입력 → 실제 처리 → 실제 출력 → 예상값 비교
- 웹/자료 검증: 공식 출처와 결과 일치
- 증거가 부족하면 HOLD

## 사용자 작업 금지
사용자는 이 상태판을 보기만 한다. 테스트, 비교, 캡처, PASS/FAIL 판정, 규칙 저장, 새 대화창 인계문 작성, 정지 여부 감시, `계속/진행` 반복 입력을 요구하지 않는다.

## 재시작 지점
다음 실행은 6번 v2.26의 `안정본_관찰패널부착_100건자동시뮬레이션`과 30-3 검증 규칙을 직접 대조하여 HOLD 분류와 실제 출력 증거 범위를 확정한다. 6번 작업 묶음이 판정되면 즉시 2번 입찰 도구의 최신 규칙/실행본 회수로 이동한다. 13번은 안전한 부분수정 수단이 확보되는 회차에 발행일 경로만 수정하고 회귀검증한다.

실행시간: duration not exposed
