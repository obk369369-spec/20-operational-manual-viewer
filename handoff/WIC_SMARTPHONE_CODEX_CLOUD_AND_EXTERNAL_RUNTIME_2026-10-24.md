# WIC 2026-10-24 — 스마트폰 Codex Cloud / 데스크톱 연결 / 외부 실행환경 인계
기록일: 2026-10-24 KST. 출처: 사용자와 본 대화에서 제시한 실제 화면 및 사용자 진술. 기존 중앙 handoff 및 evidence를 대체하지 않는 추가 기록.

## 사용자 최우선 목표
- WIC 최상위 플랫폼 완전 이전 전까지, **노트북/데스크톱 전원을 꺼도 스마트폰 단독으로 Codex Cloud 작업**을 진행한다.
- 스마트폰과 노트북에서 병렬 작업하되 동일 canonical GitHub 저장소를 정본으로 삼고, 채팅 내용의 중요 결정/문제/증거/잔여 작업을 누락 없이 인계한다.
- 사용자에게 동일한 설정·질문·진행 반복을 요구하지 않는다. 제한된 Work 사용량을 실질 작업에 우선 사용한다.
- cloud 작업과 PC 원격제어/USB Windows 실행/Work는 서로 다른 능력이다. 이를 혼동하여 완료 선언하지 않는다.

## 오늘 화면으로 확인한 사항 (실제 확인과 추정 구분)
1. Windows ChatGPT 데스크톱 앱의 '이 PC에 기기 연결' 및 QR/기기 승인을 거쳐 Android ChatGPT 앱 Codex에 DESKTOP-HV1UT8R 장치가 표시되었고, 녹색 상태점과 해당 PC의 'CENTRAL 체크포인트 작업 복원' 스레드가 나타남. **PC 연결/원격 스레드 가시성 확인**. PC 전원 OFF에서도 이 데스크톱 원격 세션이 동작한다는 증거는 없음.
2. Android Codex에는 '전체 / Cloud / DESKTOP-HV1UT8R' 탭이 존재. 최초 Cloud 탭은 '이 호스트에서 불러온 원격 스레드가 없습니다'로 표시되었음. 이 메시지는 cloud 미설치의 증거가 아니라 해당 탭의 스레드가 비어 있음을 나타냄.
3. Windows 앱 설정 > Codex 클라우드에서 GitHub 계정과 저장소 obk369369-spec/20-operational-manual-viewer를 선택하여 환경 생성 진행. 기존 저장소 연결 확인.
4. 클라우드 온보딩 작업이 Python 3.12, Node.js 24, Git 읽기, raw.githubusercontent.com 접속을 확인했다고 보고함. 필수 CENTRAL 조회는 api.github.com 네트워크 프록시 403으로 실패; 실제 도구 실행/테스트는 하지 않음. 온보딩은 네트워크 허용 추가 및 시작 스킬 초안을 저장했다고 보고함.
5. 사용자가 클라우드 환경 편집에서 Codex 인터넷 액세스 허용 ON 및 추가 허용 도메인 api.github.com을 확인하고 '저장 및 게시'를 수행. Windows 앱 화면에 **'환경이 게시되었습니다 · 채팅 시작'** 및 '게시됨'이 실제 표시됨. 이는 **환경 게시 성공** 증거이며 CENTRAL API 재조회/실제 코드 테스트 성공 증거는 아님.
6. 이후 Android Codex > Cloud 탭에서 '20-operational-manual-viewer 편집', '20-operational-manual-viewer 설정' 스레드가 실제 표시됨. **클라우드 스레드가 스마트폰에서 보이는 상태 확인**. 스마트폰에서 신규 Cloud 작업의 실행 결과, PC 전원을 실제 끈 뒤 성공한 실행은 아직 미검증.
7. Windows 앱 UI의 사용량 잔여치는 대화 중 9% → 8% → 6%로 변화. 별도로 사용자가 https://chatgpt.com/settings/usage?tab=overview 화면을 제시했고 5시간 단위 7% 남음, 주간 86% 남음이 당시 보였음. 서로 다른 시점/한도이므로 현재 잔량으로 단정하지 말 것. 모바일 Codex 화면에서 동일 사용량 표시 경로는 확인되지 않음.
8. 사용자가 외부 USB를 Windows 노트북 D:로 연결했으며 D:\오부장 AI (인공지능)\WIC34_C_REBUILD 안에 파일들이 있음을 직접 확인함. **파일 존재만 확인**, 실행·검증·GitHub 연동은 미확인.
9. TOOL013 예상 경로 D:\GPT 도구 작업\13번 엑셀 업로드 도구\index.html 및 원본 Excel 경로는 과거 자료상 후보이며 이번 세션에서 존재/실행 확인되지 않음.
10. GitHub Actions의 work-gate-handoff-audit.yml 'Run workflow / candidate_json'은 candidate gate 평가이며 Windows USB 실행환경 연결이 아님. 사용자에게 불필요한 gate 수동 실행을 반복 요청하지 말 것. GitHub hosted Actions 관찰/상태 업데이트와 실제 외부 Windows 실행을 동일시하지 말 것.

## 중요 미완료 / 재개 지점
- 최우선: Android Codex Cloud에서 저장소 기반 **실제 새 클라우드 작업 1건** 시작하여 결과/로그 확인; 이후 노트북 전원 OFF 상태에서도 실행되는지 검증. 이 검증 전에는 스마트폰 단독 전체 업무 PASS 금지.
- 클라우드 환경 게시 이후 api.github.com 403 해소 여부 및 필수 CENTRAL read/authorized admission 재검증 필요. 실패 시 실패 상태 유지; 토큰 추가 발급/Device Flow 반복하지 말 것.
- WIC34/TOOL013 등 USB 기반 Windows 프로그램은 cloud와 자동 연결되지 않음. 외부 인증 worker, 허가된 원본 입력, 정상 비교본, 실제 실행 evidence가 필요. 노트북 전원이 꺼져 있을 때 USB 로컬 파일에 cloud가 직접 접근할 수 없음.
- 24시간 무인 실행은 노트북 전원에 의존하지 않는 지속 실행 호스트가 따로 필요. 로컬 self-hosted GitHub Actions runner를 외부 PR/미신뢰 workflow에 노출하지 말 것.
- 기존 PASS_LOCK/STOP, ROOT fingerprint, checkpoint, Queue, Evidence, 생산 작업 START_BLOCKED를 유지. 실작업 실행 0건을 성공으로 바꾸지 말 것. 검증된 PASS 재실행 및 약 3200건 전수 재스캔 금지.
- 사용자 지시: GitHub에 **대화 중 중요한 작업 내용 자체를 누적 기록**. cloud 환경 게시와 GitHub 인계 기록은 별개. 새 환경 생성/설정 반복으로 크레딧 소진 금지.

## 정본과 보존
- Canonical: obk369369-spec/20-operational-manual-viewer
- 기존 인계: handoff/WIC_NEXT_CHAT_HANDOFF_2026-10-11.md
- 기존 오늘 Work checkpoint: CONTROL_TOWER/ledger/evidence/WIC_GITHUB_AUTH_CANDIDATE_GATE_CHECKPOINT_20261024.json (이 기록보다 앞선 상태; 스마트폰 Cloud 게시 이후 상황을 반영하지 않음).
- 본 문서는 사용자가 화면에서 확인시킨 사실과 지시를 보존하는 **대화 인계**일 뿐 코드 배포, 환경 재검증, 실제 도구 실행 증거는 아니다. 기존 파일을 덮어쓰거나 성공 판정을 변경하지 않는다.
