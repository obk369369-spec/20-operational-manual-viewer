"""Shared runtime gate for deduplication, progress and root-local stop decisions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

FORBIDDEN_SCOPES = {"ALL_TOOLS", "FILE_DISCOVERY", "HISTORICAL_CHAT_AUDIT"}
READ_HEAVY_ACTIONS = {"SEARCH", "READBACK", "PLANNING", "HISTORY", "EVIDENCE_REGEN", "TEST", "E2E"}
COMPLETED_RECORD_STATES = {"COMPLETE", "COMPLETED", "PASS", "PASS_LOCK", "PASS_LOCKED", "CLOSED"}
FAILED_RECORD_STATES = {"FAIL", "FAILED", "ERROR"}
STOPPED_SERVICE_STATES = {"DISCONTINUED", "RETIRED", "STOPPED", "USE_STOPPED", "QUARANTINED"}
INVESTIGATED_RECORD_STATES = {"INVESTIGATED", "RESEARCHED", "REJECTED"}
VERIFIED_DIRECTIVE_STATES = {"VERIFIED", "UNCHANGED_VERIFIED", "CANONICAL_VERIFIED"}
CANONICAL_RULE_FILES = (
    "WIC_GLOBAL_OPERATING_RULES.md",
    "AGENTS.md",
    "WIC_CHAT_ROUTING_REGISTRY.md",
)
TASK_RULE_FILES = {
    "TOOL016": ("feedback_pipeline/TOOL016_MASTER.md",),
    "TOOL042": ("CUSTOMER_GUIDE_OUTPUT_LOCK.md",),
    "TOOL037": ("feedback_pipeline/TOOL037_MASTER.md",),
    "TOOL043": ("tool043/WIC_RULE_SOURCE.md",),
    "TOOL044": ("feedback_pipeline/TOOL044_MASTER.md",),
}


def canonical_rule_manifest(repo_root: Path, task_id: str = "") -> dict[str, Any]:
    """Build the only accepted rule snapshot from existing canonical files."""
    required = list(CANONICAL_RULE_FILES) + list(TASK_RULE_FILES.get(task_id.upper(), ()))
    files: dict[str, str] = {}
    missing: list[str] = []
    for relative in required:
        target = repo_root / relative
        if not target.is_file():
            missing.append(relative)
            continue
        files[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
    version = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return {"task_id": task_id.upper(), "files": files, "missing": missing, "version": version}


def verify_rule_context(context: Any, *, repo_root: Path, task_id: str) -> dict[str, Any]:
    """Fail closed when a worker did not load the exact current global/task rules."""
    expected = canonical_rule_manifest(repo_root, task_id)
    reason = None
    if expected["missing"]:
        reason = "CANONICAL_RULE_SOURCE_MISSING"
    elif not isinstance(context, dict):
        reason = "RULE_CONTEXT_MISSING"
    elif context.get("version") != expected["version"] or context.get("files") != expected["files"]:
        reason = "RULE_CONTEXT_STALE_OR_TAMPERED"
    elif context.get("conflicts"):
        reason = "RULE_CONFLICT_UNRESOLVED"
    elif context.get("source_records_verified") is not True:
        reason = "REQUIRED_SOURCE_RECORDS_UNVERIFIED"
    decision = "ALLOW" if reason is None else "BLOCK"
    return {
        "decision": decision,
        "reason": reason,
        "task_id": task_id.upper(),
        "version": expected["version"],
        "files": expected["files"],
        "blocked_before_execution": decision == "BLOCK",
    }




def verify_work_admission(admission: Any, *, repo_root: Path, work_id: str, task_id: str) -> dict[str, Any]:
    """Require current per-task rules and a matching independently validated source receipt."""
    reason = None
    if not isinstance(task_id, str) or not task_id.strip():
        reason = "CONTRACT_TASK_ID_MISSING"
    elif task_id.upper() != "CENTRAL" and task_id.upper() not in TASK_RULE_FILES:
        reason = "TASK_RULE_SOURCE_UNMAPPED"
    elif not isinstance(admission, dict) or admission.get("work_id") != work_id or admission.get("task_id") != task_id:
        reason = "WORK_ADMISSION_IDENTITY_MISMATCH"
    else:
        context = admission.get("rule_context")
        rule = verify_rule_context(context, repo_root=repo_root, task_id=task_id)
        if rule["decision"] != "ALLOW":
            reason = rule["reason"]
        elif context.get("task_id") != task_id:
            reason = "RULE_CONTEXT_TASK_MISMATCH"
        else:
            source = admission.get("source_receipt")
            relative = source.get("path") if isinstance(source, dict) else None
            if not isinstance(relative, str) or not relative.endswith(".json"):
                reason = "SOURCE_VALIDATION_RECEIPT_MISSING"
            else:
                allowed_roots = ((repo_root / "feedback_pipeline" / "evidence").resolve(),
                                 (repo_root / "CONTROL_TOWER" / "ledger" / "evidence").resolve())
                target = (repo_root / relative).resolve()
                if not any(target.is_relative_to(root) for root in allowed_roots) or not target.is_file():
                    reason = "SOURCE_VALIDATION_RECEIPT_PATH_INVALID"
                elif hashlib.sha256(target.read_bytes()).hexdigest() != source.get("sha256"):
                    reason = "SOURCE_VALIDATION_RECEIPT_STALE_OR_TAMPERED"
                else:
                    try:
                        evidence = json.loads(target.read_text(encoding="utf-8"))
                    except (OSError, ValueError):
                        evidence = {}
                    if not (evidence.get("work_id") == work_id and evidence.get("task_id") == task_id
                            and evidence.get("source_records_verified") is True
                            and evidence.get("validation_result") == "PASS"
                            and evidence.get("validator_id") and evidence.get("source_refs")):
                        reason = "SOURCE_VALIDATION_RECEIPT_UNVERIFIED"
                    elif evidence.get("rule_version") != context.get("version"):
                        reason = "SOURCE_RECEIPT_RULE_VERSION_MISMATCH"
                    elif not isinstance(evidence.get("validation_plan"), dict) or not all(
                            evidence["validation_plan"].get(key) for key in
                            ("method", "expected_result", "evidence_required")):
                        reason = "WORK_VALIDATION_PLAN_MISSING"
                    else:
                        for ref in evidence["source_refs"]:
                            if not isinstance(ref, dict) or not isinstance(ref.get("path"), str) or not isinstance(ref.get("sha256"), str):
                                reason = "ORIGINAL_SOURCE_REFERENCE_UNVERIFIED"
                                break
                            original = (repo_root / ref["path"]).resolve()
                            if (not original.is_relative_to(repo_root.resolve()) or not original.is_file()
                                    or original.stat().st_size == 0
                                    or hashlib.sha256(original.read_bytes()).hexdigest() != ref["sha256"]):
                                reason = "ORIGINAL_SOURCE_MISSING_OR_CHANGED"
                                break
    return {"work_id": work_id, "task_id": task_id,
            "decision": "BLOCK" if reason else "ALLOW", "reason": reason}



def signature(action: dict[str, Any]) -> str:
    selected = {key: action.get(key) for key in ("root_id", "action_kind", "target", "checkpoint")}
    return hashlib.sha256(json.dumps(selected, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def initial_state(previous: dict[str, Any] | None = None) -> dict[str, Any]:
    previous = previous or {}
    return {"seen_signatures": list(previous.get("seen_signatures", [])),
            "stopped_roots": dict(previous.get("stopped_roots", {})),
            "last_checkpoint": dict(previous.get("last_checkpoint", {})),
            "events": list(previous.get("events", []))[-100:],
            "permission_metrics": dict(previous.get("permission_metrics", {
                "permission_prompt_count": 0,
                "fragmented_permission_prompt_count": 0,
                "user_manual_runtime_permission_required": 0,
                "batched_permission_pass": 0,
                "platform_forced_permission_count": 0,
            }))}


def record_permission_batch(gate: dict[str, Any], *, root_id: str, operations: list[str],
                            prompt_count: int, platform_forced_count: int = 0) -> dict[str, Any]:
    """Measure approval batching without bypassing platform security boundaries."""
    if not operations or prompt_count < 0 or platform_forced_count < 0:
        raise ValueError("INVALID_PERMISSION_BATCH")
    metrics = gate.setdefault("permission_metrics", initial_state()["permission_metrics"])
    fragmented = max(0, prompt_count - max(1, platform_forced_count))
    metrics["permission_prompt_count"] += prompt_count
    metrics["fragmented_permission_prompt_count"] += fragmented
    metrics["user_manual_runtime_permission_required"] += int(prompt_count > 0)
    metrics["platform_forced_permission_count"] += platform_forced_count
    passed = fragmented == 0
    metrics["batched_permission_pass"] += int(passed)
    receipt = {"root_id": root_id, "operations": list(operations),
               "permission_prompt_count": prompt_count,
               "fragmented_permission_prompt_count": fragmented,
               "platform_forced_permission_count": platform_forced_count,
               "decision": "PASS" if passed else "HOLD_PERMISSION_FRAGMENTATION"}
    gate["events"] = (gate.get("events", []) + [receipt])[-100:]
    return receipt


def _permanent_reentry_block(action: dict[str, Any]) -> str | None:
    """Return the durable pre-execution block reason for an unchanged central record."""
    record_state = str(action.get("central_record_status", "")).upper()
    service_state = str(action.get("service_status", "")).upper()
    directive_state = str(action.get("directive_status", "")).upper()
    unchanged = bool(action.get("unchanged_since_verification", True))
    same_method = bool(action.get("same_method", True))

    if record_state in COMPLETED_RECORD_STATES:
        return "COMPLETED_WORK_REENTRY_BLOCKED"
    if record_state in FAILED_RECORD_STATES and same_method:
        return "FAILED_METHOD_REENTRY_BLOCKED"
    if service_state in STOPPED_SERVICE_STATES:
        return "DISCONTINUED_SERVICE_REENTRY_BLOCKED"
    if record_state in INVESTIGATED_RECORD_STATES and unchanged:
        return "INVESTIGATED_CANDIDATE_REENTRY_BLOCKED"
    if directive_state in VERIFIED_DIRECTIVE_STATES and unchanged:
        return "VERIFIED_DIRECTIVE_RELOAD_BLOCKED"
    return None


def evaluate(gate: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    root = str(action["root_id"])
    action_signature = signature(action)
    decision, reason = "ALLOW", None
    permanent_reason = _permanent_reentry_block(action)
    if permanent_reason:
        decision, reason = "BLOCK", permanent_reason
    elif action.get("scope") in FORBIDDEN_SCOPES:
        decision, reason = "BLOCK", "DEFERRED_SCOPE_LOCKED"
    elif action_signature in set(gate["seen_signatures"]):
        decision, reason = "BLOCK", "REPEAT_AROUND_COMPLETED_SCOPE"
    elif root in gate["stopped_roots"] and action.get("checkpoint") == gate["stopped_roots"][root]:
        decision, reason = "BLOCK", "STOPPED_CHECKPOINT_RESTART"
    deltas = [int(action.get(name, 0)) for name in (
        "actual_closure_delta", "remaining_scope_delta", "checkpoint_advance",
        "new_valid_evidence_delta", "requirement_closure_delta")]
    if decision == "ALLOW" and action.get("action_kind") in READ_HEAVY_ACTIONS and not any(deltas):
        decision, reason = "STOP", "NO_PROGRESS_LOOP_CREDIT_WASTE"
        gate["stopped_roots"][root] = action.get("checkpoint")
    gate["seen_signatures"].append(action_signature)
    if any(deltas):
        gate["last_checkpoint"][root] = action.get("checkpoint")
    receipt = {"root_id": root, "decision": decision, "reason": reason,
               "signature": action_signature, "deltas": deltas,
               "blocked_before_execution": decision == "BLOCK"}
    gate["events"] = (gate["events"] + [receipt])[-100:]
    return receipt


def accept_handoff(state: dict[str, Any], queue: dict[str, Any], registry: dict[str, Any],
                   envelope: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    required = {"trace_id", "root_id", "input", "expected_output"}
    if required.difference(envelope) or not all(envelope.get(key) for key in required):
        return {"status": "BLOCKED", "reason": "HANDOFF_CONTRACT_INCOMPLETE"}
    trace_id = str(envelope["trace_id"])
    traces = state.setdefault("handoff_traces", {})
    pass_locked_roots = set(state.get("pass_locked_roots", []))
    if str(envelope["root_id"]) in pass_locked_roots:
        return {"status": "BLOCKED", "reason": "PASS_LOCKED_SCOPE", "trace_id": trace_id}
    if trace_id in traces:
        return {"status": "BLOCKED", "reason": "DUPLICATE_TRACE", "trace_id": trace_id}
    task_id = str(envelope.get("task_id", ""))
    repo_root = Path(__file__).resolve().parents[2]
    rule_receipt = verify_rule_context(
        envelope.get("rule_context"), repo_root=repo_root, task_id=task_id
    )
    if rule_receipt["decision"] != "ALLOW":
        return {"status": "BLOCKED", "reason": rule_receipt["reason"], "trace_id": trace_id,
                "blocked_before_execution": True, "rule_gate_receipt": rule_receipt}
    receipt_gate = evaluate(gate, {"root_id": envelope["root_id"],
        "scope": envelope.get("scope", "COMMON_PLATFORM"), "action_kind": "EXECUTION",
        "target": envelope["expected_output"], "checkpoint": envelope.get("checkpoint", trace_id),
        "checkpoint_advance": 1,
        "central_record_status": envelope.get("central_record_status", ""),
        "service_status": envelope.get("service_status", ""),
        "directive_status": envelope.get("directive_status", ""),
        "unchanged_since_verification": envelope.get("unchanged_since_verification", True),
        "same_method": envelope.get("same_method", True)})
    if receipt_gate["decision"] != "ALLOW":
        return {"status": "BLOCKED", "reason": receipt_gate["reason"], "trace_id": trace_id,
                "blocked_before_execution": True}
    selected = [item["id"] for item in registry.get("components", []) if item.get("status") == "VERIFIED_REUSE"]
    if not selected:
        return {"status": "HOLD", "reason": "NO_VERIFIED_COMPONENT", "trace_id": trace_id}
    intent_lock = hashlib.sha256(json.dumps({"input": envelope["input"],
        "expected_output": envelope["expected_output"]}, sort_keys=True,
        ensure_ascii=False).encode()).hexdigest()
    receipt = {"status": "ACCEPTED", "trace_id": trace_id, "root_id": envelope["root_id"],
               "ready_made_first": True, "selected_components": selected,
               "backend_route": "CENTRAL_COMMON_PLATFORM", "intent_quality_lock": intent_lock,
               "registry_prelookup": True, "pass_lock_prelookup": True,
               "user_manual_repetition": 0, "rule_gate_receipt": rule_receipt,
               "rule_context_verified": True}
    traces[trace_id] = receipt
    queue.setdefault("handoff_inbox", []).append(receipt)
    return receipt


def accept_feedback(state: dict[str, Any], feedback: dict[str, Any]) -> dict[str, Any]:
    """Persist one correction as a shared failure-class rule, never a local-only patch."""
    from universal_enforcement import promote_failure
    promoted = promote_failure(feedback)
    if promoted["status"] != "PROMOTED":
        return promoted
    rules = state.setdefault("shared_failure_rules", {})
    key = promoted["promotion_key"]
    if key in rules:
        rules[key]["repeat_count"] = int(rules[key].get("repeat_count", 1)) + 1
        return {**promoted, "status": "SYSTEM_CONTROL_FAILURE", "repeat_count": rules[key]["repeat_count"]}
    rules[key] = {**promoted, "repeat_count": 1}
    return promoted
