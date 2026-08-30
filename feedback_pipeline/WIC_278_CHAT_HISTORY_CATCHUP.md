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
- 텍스트 추출: 278/278 접근 성공
- 번호 확인된 파일: TOOL001,002,003,004,005,006,007,008,009,010,011,012,013,014,016,018,019,020,021,022,023,024,025,026,027,030,033,034,037,038,041,042
- 번호 없는/다른 명명형 파일도 별도 분류 후 기존 TOOL alias 여부를 판단한다.

## UPDATED / REMOTE READ-BACK
- TOOL001 — `01-auto-guide-v1/TOOL001_MASTER.md` commit `364baca50027dabb895707704be7f82478933662`; pointer commit `1137e2ac89fc7d160e5a37f6866367071f14c59c`.
- TOOL002 — `02-auto-bid-narajangter-v1/TOOL002_MASTER.md` commit `df396721d16339dc0419ae3bb8d230f6df1437b0`; pointer commit `5ed7f36c0b3bdbc5b0e00f60d107486a335cda3e`.
- TOOL003 — `03-coding_practice/TOOL003_MASTER.md` commit `90ff205b1797abd91d7ebf44e91b010425dec03d`; pointer commit `c4892ee9d998ec8ba66106579a92adc77a2471b1`.
- TOOL004 — `04-research-funding-generator/TOOL004_MASTER.md` commit `b40f60d4cf9952a7c895c662613f06777627ed47`; pointer commit `efd816060b6d9836b2aab8eb4e2efc297e735049`.
- TOOL005 — `05-report-generator/TOOL005_MASTER.md` commit `8cdfc0bf49ebed8ae332c001eabdda23cee90fd1`; pointer commit `167079aa6688063124c94f0594b836947f35b129`.
- TOOL006 — `06-toc-check/TOOL006_MASTER.md` commit `e937b9ffa658032c57db4e3072b93941b1288733`. Existing checkpoint/recovery retained; no redundant global pointer created.
- TOOL007 — `07-wic-setting-tool-v1/TOOL007_MASTER.md` commit `a2d926f0d5f5bf775a4a5b1a4572d4e5c567b047`; pointer commit `b340c701f08a95594af27c12830417aba3bff91e`. Existing execution asset remains HOLD-MISMATCH with latest customer-contact role.
- TOOL008 — `08-English-Verb-Exercise/TOOL008_MASTER.md` commit `517a345a887f52660ee4e870eaaf15895781bba0`; pointer commit `447382bbdd05040bc61f08c67e55f91e9c62e7e1`.
- TOOL009 — `09-contents-making-tool/TOOL009_MASTER.md` commit `f345a9bd1a47a575c0f8cd543428d073db90e7a7`; pointer commit `3c20c5483f86cfd6b9a318ab937597b729a74420`.
- TOOL010 — `10-WIC-Finance-Dashboard/TOOL010_MASTER.md` commit `72d8348da20e628aa6d864f9e979584e011d81f1`; pointer commit `510f3415a4fbc632d8e140d16237902380c187d1`.
- TOOL011 — `11-obk-finance-planner/TOOL011_MASTER.md` commit `7727fe2d891b94469447d1702e94bc8ac2f09619`; pointer commit `c497869491dbbc83f84659944eb94155359b3227`.
- TOOL012 — `12-wic-subwebsite-builder/TOOL012_MASTER.md` commit `9a2ce32f64cc8a775ff256f27b6da1c2aedee11f`; pointer commit `70c04baae082882602ad03b9ccdc8db42c69b7c3`.
- TOOL013 — `13-excel-upload/TOOL013_MASTER.md` commit `39fb10de3a72e873b5a642fe9d4c25a6d2f2eda4`; pointer commit `66eac5bc3200484061f89474c33b1548a40a50b3`. Existing PASS/CI scope protected as SKIP_REUSE.
- TOOL014 — `14-wic-homepage-editor/TOOL014_MASTER.md` commit `09ba2c789dc614e8e58350a269f8a02f5ff5a38e`; pointer commit `219ed62a3288b415eca370e2de57044696e937e1`. Current runtime remains `BLOCKED_EXTERNAL(PAGES_NOT_ENABLED)`.
- TOOL016 — CENTRAL `feedback_pipeline/TOOL016_MASTER.md` commit `ae85dd75aeaf67663aa4a0d08d393486bdf5d2c9`; read-back PASS. Includes `업데이트` save-command and proactive efficiency/shortcut proposal duty.
- TOOL018 — CENTRAL `feedback_pipeline/TOOL018_MASTER.md` commit `01540bf72f168e98d8197ddc6245ee8c47ae7553`; read-back PASS. No separate repo required.
- TOOL019 — `19-wic-business-promotion/TOOL019_MASTER.md` commit `fd34b22416e5fadc0ff332604be846ff4cf52aa1`; pointer commit `6e9a512986cdebef0569ab56e8dab472068aeaf7`; read-back PASS.
- TOOL020 — CENTRAL/current repo `TOOL020_MASTER.md` commit `0b8f090f5724db83e1aaa9a9f500a9adc1ecdc5d`; read-back PASS. Existing deployed foundation preserved; auto-manual generation/update remains HOLD_FOR_REUSE.
- TOOL041 — existing `41-wic-email-collection-master/MASTER/COMMON_MASTER.md` catch-up commit `ca4b2f5b8281c4befa223833f6020cf9f62fad46`; read-back PASS.
- TOOL042 — existing central `CUSTOMER_GUIDE_OUTPUT_LOCK.md` catch-up commit `65302485f1ac26fc51d3edf0a2291b456fa53c91`; read-back PASS.

## 진행률
- 번호 확인 TOOL군: 32개
- GitHub 정본 반영 + remote read-back 완료: 20개
- 남은 번호 TOOL군: 12개 (`021,022,023,024,025,026,027,030,033,034,037,038`)
- 번호 TOOL군 기준 진행률: 62.5%
- 추가로 번호 없는/다른 명명형 기록의 alias/흡수 판정이 남아 있다.

## 다음 처리 순서
TOOL021부터 번호순으로 진행한다. 기존 canonical이 명확한 TOOL은 DIFF ONLY로 반영하고, repo가 없거나 역할 흡수 여부가 애매한 번호는 새 repo를 즉시 만들지 않고 기존 CENTRAL/canonical을 좁게 확인한 뒤 MERGED/HOLD/CREATE 후보로 분류한다.
