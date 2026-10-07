"""Shared runtime gate for deduplication, progress and root-local stop decisions."""
from __future__ import annotations

import hashlib
import json
from typing import Any

FORBIDDEN_SCOPES = {"ALL_TOOLS", "FILE_DISCOVERY", "HISTORICAL_CHAT_AUDIT"}
READ_HEAVY_ACTIONS = {"SEARCH", "READBACK", "PLANNING", "HISTORY", "EVIDENCE_REGEN", "TEST", "E2E"}


def signature(action: dict[str, Any]) -> str:
    selected = {key: action.get(key) for key in ("root_id", "action_kind", "target", "checkpoint")}
    return hashlib.sha256(json.dumps(selected, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def initial_state(previous: dict[str, Any] | None = None) -> dict[str, Any]:
    previous = previous or {}
    return {"seen_signatures": list(previous.get("seen_signatures", [])),
            "stopped_roots": dict(previous.get("stopped_roots", {})),
            "last_checkpoint": dict(previous.get("last_checkpoint", {})),
            "events": list(previous.get("events", []))[-100:]}


def evaluate(gate: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    root = str(action["root_id"])
    action_signature = signature(action)
    decision, reason = "ALLOW", None
    if action.get("scope") in FORBIDDEN_SCOPES:
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
               "signature": action_signature, "deltas": deltas}
    gate["events"] = (gate["events"] + [receipt])[-100:]
    return receipt


def accept_handoff(state: dict[str, Any], queue: dict[str, Any], registry: dict[str, Any],
                   envelope: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    required = {"trace_id", "root_id", "input", "expected_output"}
    if required.difference(envelope) or not all(envelope.get(key) for key in required):
        return {"status": "BLOCKED", "reason": "HANDOFF_CONTRACT_INCOMPLETE"}
    trace_id = str(envelope["trace_id"])
    traces = state.setdefault("handoff_traces", {})
    if trace_id in traces:
        return {"status": "BLOCKED", "reason": "DUPLICATE_TRACE", "trace_id": trace_id}
    receipt_gate = evaluate(gate, {"root_id": envelope["root_id"],
        "scope": envelope.get("scope", "COMMON_PLATFORM"), "action_kind": "EXECUTION",
        "target": envelope["expected_output"], "checkpoint": envelope.get("checkpoint", trace_id),
        "checkpoint_advance": 1})
    if receipt_gate["decision"] != "ALLOW":
        return {"status": "BLOCKED", "reason": receipt_gate["reason"], "trace_id": trace_id}
    selected = [item["id"] for item in registry.get("components", []) if item.get("status") == "VERIFIED_REUSE"]
    if not selected:
        return {"status": "HOLD", "reason": "NO_VERIFIED_COMPONENT", "trace_id": trace_id}
    receipt = {"status": "ACCEPTED", "trace_id": trace_id, "root_id": envelope["root_id"],
               "ready_made_first": True, "selected_components": selected,
               "backend_route": "TOOL43_BACKEND", "user_manual_repetition": 0}
    traces[trace_id] = receipt
    queue.setdefault("handoff_inbox", []).append(receipt)
    return receipt
