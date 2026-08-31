# B안 최소 고객업무 전용 실행 진입점

`customer_pipeline/customer_mvp.py`는 stdin JSON 요청 하나를 처리하고 결과 JSON 하나만 출력하는 전용 실행 명령이다. 웹 UI/상시 서버/일반 대화창 interception은 만들지 않는다. 초안은 메모리 안에만 있고 streaming/임시 초안 파일/preview가 없다.

## 초기 설정 (실행환경에서 한 번)

- Python 3.10+ (표준 라이브러리만 사용; 이 workspace의 bundled Python 사용 가능).
- `WIC_TOOL041_ROOT`: 기존 TOOL041 저장소 checkout 절대경로. 생성기/검증 코드가 최신 pinned GitHub 내용과 일치해야 한다.
- `OPENAI_API_KEY`: 실행계정의 보안 환경변수/secret store. 채팅이나 저장소에 키를 넣지 않는다.
- `WIC_MODEL`: 해당 API project가 호출할 수 있고 Responses structured outputs를 지원하는 모델 ID. 임의 기본모델/무료 호출을 가정하지 않는다.
- `GH_TOKEN` 또는 `GITHUB_TOKEN`: private TOOL041 및 TOOL042/CENTRAL 읽기와 CENTRAL contents 갱신 권한. 최소 저장소 권한만 부여한다.
- native 실행환경에서 `api.github.com`, `api.openai.com` HTTPS 허용. GitHub connector 로그인은 native 환경변수 인증을 대신하지 않는다.

현재 작업에서는 키·모델·native GitHub 인증이 없어 실제 호출은 HOLD. 로그인 우회/새 인증서비스를 만들지 않았다. Node는 이 전용 Python 명령의 필수조건이 아니다.

## 사용

`python customer_pipeline/customer_mvp.py`에 다음 구조의 JSON을 stdin으로 전달한다.

```json
{"tool":"TOOL042","customer_id":"현재 CLEAN MASTER의 실제 고유번호","task":"해당 고객의 과거 연락을 반영한 짧은 후속 질문 작성","mode":"history_question"}
```

`tool`은 TOOL041 또는 TOOL042. 사용자는 업무·고객만 지정한다. context/verified/review/PASS 필드는 받지 않는다. 규칙·checkpoint 전달/검증 버튼/중간 계속 입력은 없다.

## 강제 순서와 범위

1. 기존 TOOL041 `load_canonical` 재사용 + TOOL042 최신 MASTER/checkpoint 조회.
2. 동일 CLEAN snapshot의 고객 한 명 선택, 실제 접촉이력 존재 확인, 기존 integrity guard/merge 재사용. 전체 고객 업무 재검증이 아니다.
3. 최신 MASTER/피드백/해당 고객 실제 데이터를 생성 모델에 전달. 전체 CUSTOMER_MASTER는 모델에 보내지 않는다.
4. 독립 review API 호출로 8항목 의미판정과 근거를 받는다. keyword 검사는 기존 explicit FAIL 방어를 보조할 뿐 의미판정을 대신하지 않는다.
5. 8항목 모두 PASS + 기존 FAIL 차단 통과가 아니면 모델을 통한 재작성 1회와 의미 재검사 1회. 재실패는 HOLD. 통신/인증/응답형식 실패는 추가 호출 없이 HOLD.
6. 원본 자료 변경 여부 확인 후 기존 `save_central`로 익명화한 receipt 저장/read-back. 저장 실패도 본문 비공개. 같은 저장 실패 재시도 없음.
7. 마지막에만 `output_allowed=true`와 본문 반환. 모든 HOLD는 빈 본문/빈 고객 rows. 자동 발송하지 않는다.

기존 일반 native 진입점의 HOLD 상태는 바꾸지 않는다. B안이 전용 실행층 안에서만 실제 reviewer 결과를 처리한다. 모델의 의미 정확성 100% 보장이 아니라 절차 강제 MVP다.

현 MVP는 `history_question`만 지원한다. 실제 판매자료 추천/안내서 요청은 `ACTUAL_MATERIALS_EVIDENCE_REQUIRED`로 차단한다. 요청문이 자료 업무를 요구하면 의미검사에서도 자료 선확인 누락을 검사한다. 서갑호 등 고객 식별·이력이 미연결이면 `CUSTOMER_EVIDENCE_REQUIRED`/`CUSTOMER_HISTORY_EVIDENCE_REQUIRED`이며 다른 고객으로 대체하지 않는다.

모델 생성/재작성은 동일 최신 source packet을 사용하고 review는 별도 호출이다. 정확한 draft와 source packet hash를 묶은 receipt를 저장하므로 조회 로그만으로 PASS를 만들지 않는다. 모의 모델 PASS는 실제 모델/고객 E2E PASS가 아니다.

## 근거

- https://developers.openai.com/api/docs/guides/structured-outputs
- https://developers.openai.com/api/reference/typescript/resources/responses/methods/create
- https://developers.openai.com/api/reference/overview#authentication
