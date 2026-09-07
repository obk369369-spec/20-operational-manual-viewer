# SSD_MIGRATION_MANIFEST

Scope: minimum verified runtime set for device-independent WIC resume. This is a manifest only; it does not authorize copying, deleting, moving, cleaning, or overwriting user-device files.

## Include

| Class | Verified path | Purpose | Status |
|---|---|---|---|
| Actual TOOL runtime | `I:\\GPT 도구 작업\\43번 모바일 관찰판\\tool043` | TOOL043 deployed observer runtime | `VERIFIED`; hashes in `tool043_local_deploy_verify_20260906.json` |
| CENTRAL / MASTER | this repository root | canonical policies, registries and state | GitHub canonical; remote read-back required for this change |
| SAFE_CHECKPOINT | `feedback_pipeline/evidence/tool043_local_deploy_verify_20260906.json` | TOOL043 final local/Pages baseline | canonical evidence candidate in this change |
| Common execution block | `feedback_pipeline/WIC_WORK_COMMON_EXECUTION_BLOCK.md` | validation, promotion, deployment and device-independent resume gates | required |
| Global policy | `WIC_GLOBAL_OPERATING_RULES.md` | shared WIC invariants | required |
| Actual test fixture/evidence | `tool043/screen_off_actual_20260831.json` | actual Android screen-off/background/reopen evidence | `REMOTE_VERIFIED / SKIP_REUSE` |
| Validation evidence | `feedback_pipeline/evidence/tool043_proof_e2e.json` | completion-proof E2E evidence | `VERIFIED / SKIP_REUSE` |
| Validation evidence | `feedback_pipeline/evidence/tool043_proof_deployed.json` | deployed-copy proof evidence | `VERIFIED / SKIP_REUSE` |
| Deployment runtime | `tool043/` and `.github/workflows/tool043-pages.yml` | canonical Pages build/runtime | required |

## Exclude

- old backups, duplicate copies, large archives and unrelated historical chat exports
- `SHELL / DRAFT / TEST_NOT_RUN / FAIL / PARTIAL / BROKEN / LEGACY / TEMP`
- any path not verified above

## Resume contract

`GitHub/CENTRAL canonical → validation evidence → SAFE_CHECKPOINT → target actual-use folder`

If one device is unavailable: detect once, retry once, verify another canonical path, then resume from the last SAFE_CHECKPOINT. Do not request repeated reconnects and do not treat USB as the only state store.
