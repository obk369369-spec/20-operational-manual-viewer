# WIC LIVE OBSERVER STATUS

상태: DEPRECATED_COMPATIBILITY_POINTER

이 파일은 과거 야간 관찰용 상태판의 호환 경로이며 현재 상태 원본이 아니다.

- 실제 기계 실행상태: `WIC_EXECUTION_STATE.json`
- 사람용 단일 관찰판: `WIC_OBSERVER_STATUS.md`
- 운영 규칙 단일 원본: `WIC_GLOBAL_OPERATING_RULES.md`
- 감시기: `.github/workflows/wic-stall-monitor.yml`

새 상태·진행률·RUNNING 문구를 이 파일에 직접 기록하지 않는다. 기존 참조는 `WIC_OBSERVER_STATUS.md`로 이동하고, 감시기는 `WIC_EXECUTION_STATE.json`의 실제 활성 상태와 변경시각만 판정한다.
