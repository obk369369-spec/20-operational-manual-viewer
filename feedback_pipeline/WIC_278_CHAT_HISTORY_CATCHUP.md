# WIC 278개 대화기록 중앙마스터 정본화 체크포인트

시작일: 2026-08-30
상태: IN_PROGRESS
범위: 사용자가 직접 제공한 압축파일 278개만 대상으로 번호별 TOOL 정본화. WIC 전체 전수조사 금지.

## 처리 원칙
- 파일명에 표시된 TOOL 번호별로 묶는다.
- 동일 TOOL 내부에서 반복 피드백은 합치고, 같은 범위에서 충돌하면 더 최신의 명시적 사용자 지시를 현재 규칙으로 채택한다.
- 기존 GitHub canonical/master가 있으면 DIFF ONLY로 반영한다.
- 이미 같은 규칙은 SKIP_REUSE한다.
- 일회성 질문/상태질문은 공통 MASTER에 넣지 않는다.
- 기존 저장소가 없다고 즉시 새 repo를 만들지 않는다. 독립 TOOL 유지 가치와 기존 CENTRAL/canonical 흡수 여부를 먼저 좁게 확인한다.
- 독립 TOOL로 계속 유지할 가치가 있고 실제 canonical repo가 없을 때만 새 저장소/MASTER 생성 후보로 둔다.
- 다른 TOOL에 흡수됨/중복/껍데기/일회성 대화창은 별도 repo를 만들지 않고 MERGED/NO_NEW_MASTER/HOLD로 기록한다.
- 각 TOOL은 실제 GitHub write → commit → remote read-back까지 확인한 경우에만 UPDATED로 표시한다.
- 사용자는 관찰자다. 중간 파일선택/저장소선택/규칙복사 지시를 요구하지 않는다.

## 추출 현황
- 압축파일: 278개
- 텍스트 추출: 278/278 접근 성공(일부 .doc 확장자 파일은 실제 UTF-8 텍스트로 감지하여 직접 읽음)
- 총 추출 텍스트 규모: 약 1.02억 문자
- 번호 확인된 파일: TOOL001,002,003,004,005,006,007,008,009,010,011,012,013,014,016,018,019,020,021,022,023,024,025,026,027,030,033,034,037,038,041,042
- 번호 없는/다른 명명형 파일도 별도 분류 후 기존 TOOL alias 여부를 판단한다.

## 현재 처리
- TOOL041: 2026-08-30 첨부 대화기록 + 현재대화 UPDATE FLUSH 규칙 반영 완료. commit ca4b2f5b8281c4befa223833f6020cf9f62fad46 / read-back PASS.
- TOOL042: 2026-08-30 첨부 대화기록 + 현재대화 UPDATE FLUSH/RESUME 규칙 반영 완료. commit 65302485f1ac26fc51d3edf0a2291b456fa53c91 / read-back PASS.
- 나머지 TOOL: 번호별 정리 및 기존 canonical 대조 진행 중.

## 다음 처리 순서
TOOL001부터 번호순으로 진행하되, 기존 canonical이 명확한 TOOL은 바로 DIFF ONLY 반영하고, 별도 저장소가 없거나 흡수 여부가 애매한 번호는 HOLD/alias 판정 후 다음 TOOL로 이동한다.
