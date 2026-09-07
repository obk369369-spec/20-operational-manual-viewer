# Phase 5 atomic component harvest evidence

- Scope: existing TOOL044 precheck and component registry only.
- External search: not run; two already verified components were reused.
- TEST A: whole replacement absent + `PROVENANCE_VALIDATION` present -> `READY_ATOMIC_COMPONENT_FOUND`, `SKIP_REUSE`.
- TEST B: provenance present + TOC hierarchy absent -> `PARTIAL_ATOMIC_COMPONENT_SET`, search limited to the missing capability.
- TEST C: TOC hierarchy only, absent -> `NO_READY_ATOMIC_COMPONENT`.
- TEST D: existing receipt validation match -> `READY_ATOMIC_COMPONENT_FOUND`, `SKIP_REUSE`; duplicate search not run.
- Actual output: `feedback_pipeline/evidence/tool044_atomic_detection_20260907.json`.
- Existing whole-component and deployed-pass behavior: regression PASS in `test_tool044_precheck.py`.
- New verified external component: 0. Existing verified component reuse: 2.
- Status before remote/deployed-copy verification: LOCAL_TEST_PASS.
