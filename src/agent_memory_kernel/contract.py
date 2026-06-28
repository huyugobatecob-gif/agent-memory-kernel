"""Formal memory contract for runtime integrations.

The contract is intentionally data-shaped. Adapters can render it into docs,
tests, or capability negotiation without importing storage internals.
"""

from __future__ import annotations

from typing import Any


CONTRACT_VERSION = "memory-contract-v0.2"

LANES: dict[str, dict[str, Any]] = {
    "personal": {
        "purpose": "User preferences, communication style, and stable personal context.",
        "default_visibility": "user_owned",
        "retrieval_default": "explicit_only",
        "precedence": 10,
        "retention": "until corrected, deleted, or explicitly expired",
        "write_policy": "direct user statements may be proposed; inferred facts require review",
    },
    "professional": {
        "purpose": "Work context, projects, decisions, rules, lessons, gotchas, and patterns.",
        "default_visibility": "workspace_owned",
        "retrieval_default": "default_work_lane",
        "precedence": 20,
        "retention": "until corrected, superseded, deleted, or expired",
        "write_policy": "agent and system writes are candidates until policy or review approves them",
    },
    "project": {
        "purpose": "Project-specific facts, rules, decisions, outcomes, and constraints.",
        "default_visibility": "project_scoped",
        "retrieval_default": "when project identity is present",
        "precedence": 30,
        "retention": "project lifecycle or explicit expiry",
        "write_policy": "project agents may propose; destructive mutations require owner or admin",
    },
    "agent": {
        "purpose": "Operational memory for a specific agent role or capability.",
        "default_visibility": "agent_scoped",
        "retrieval_default": "same agent or trusted shared role only",
        "precedence": 40,
        "retention": "bounded by agent role and usefulness",
        "write_policy": "agents may write events and propose; promotion requires policy",
    },
    "session": {
        "purpose": "Short-lived context that may later be summarized into durable memory.",
        "default_visibility": "thread_scoped",
        "retrieval_default": "current thread only",
        "precedence": 50,
        "retention": "short-lived; summarize or expire",
        "write_policy": "append-only during a session; durable promotion requires Keeper review",
    },
}

MEMORY_KINDS = [
    "fact",
    "preference",
    "rule",
    "decision",
    "attempt",
    "outcome",
    "gotcha",
    "pattern",
]

WRITE_ACTIONS = [
    "record",
    "auto_approve",
    "approve",
    "reject",
    "correct",
    "delete",
    "distrust",
    "expire",
    "outcome",
    "conflict",
    "supersede",
]

TRUST_LEVELS = {
    "trusted": "Direct user/profile/manual source or explicitly approved memory.",
    "user": "Direct user-owned identity flow.",
    "system": "Controlled system process; still reviewable for high-impact rules.",
    "untrusted": "Assistant output, tools, web pages, logs, external documents, or model output.",
}

SENSITIVITY_LEVELS = {
    "public": "Safe to expose in normal prompt context.",
    "internal": "Default work memory; expose only inside allowed scope.",
    "personal": "User-private context; explicit lane access required.",
    "secret": "Never retrieve into prompts; quarantine or redact.",
}

ACCEPTANCE_GATES = [
    {
        "gate": "automatic_runtime_loop",
        "requires": [
            "before_model_call runs before a non-incognito main model call",
            "after_saved_turn stores turns and runs or queues Keeper after the answer",
            "Router and Keeper runs are auditable by thread, actor, model, and source ids",
        ],
    },
    {
        "gate": "semantic_recall_with_provenance",
        "requires": [
            "retrieval returns expanded memory content, not only labels or tags",
            "prompt context exposes source ids, trust, confidence, and why branches were selected",
            "no-memory and denied-memory modes fail closed",
        ],
    },
    {
        "gate": "lane_and_permission_safety",
        "requires": [
            "personal memory is absent from professional-only prompts",
            "project and agent memory are scoped by policy",
            "write policy blocks unauthorized review and lifecycle mutations",
        ],
    },
    {
        "gate": "keeper_quality",
        "requires": [
            "Keeper proposes typed candidates with source evidence",
            "assistant/tool/external claims are not trusted facts by default",
            "unsafe or secret-like content is quarantined",
        ],
    },
    {
        "gate": "lifecycle_correctness",
        "requires": [
            "corrections and rollbacks update active retrieval",
            "deleted, distrusted, expired, and superseded memory is absent from prompt-facing retrieval",
            "conflicts are recorded and reviewable",
        ],
    },
    {
        "gate": "behavioral_eval",
        "requires": [
            "a repeatable fixture proves memory improves task context versus no-memory baseline",
            "stale, unsafe, and cross-lane memory are rejected by tests",
            "review decisions are regression-testable",
        ],
    },
]


def memory_contract() -> dict[str, Any]:
    """Return the public contract that integrations should target."""
    return {
        "version": CONTRACT_VERSION,
        "default_lanes": ["personal", "professional"],
        "extension_lanes": ["project", "agent", "session"],
        "lanes": LANES,
        "memory_kinds": MEMORY_KINDS,
        "write_actions": WRITE_ACTIONS,
        "trust_levels": TRUST_LEVELS,
        "sensitivity_levels": SENSITIVITY_LEVELS,
        "acceptance_gates": ACCEPTANCE_GATES,
        "closed_loop": [
            "observe",
            "encode_with_provenance",
            "route_relevant_memory",
            "act_with_selected_context",
            "verify_behavior",
            "revise_or_forget",
        ],
    }


def assert_contract_shape(contract: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate enough shape for adapters and docs to depend on it."""
    data = contract or memory_contract()
    checks = {
        "version_present": bool(data.get("version")),
        "personal_lane_present": "personal" in data.get("lanes", {}),
        "professional_lane_present": "professional" in data.get("lanes", {}),
        "project_extension_present": "project" in data.get("lanes", {}),
        "write_actions_present": set(WRITE_ACTIONS).issubset(set(data.get("write_actions", []))),
        "acceptance_gates_present": len(data.get("acceptance_gates", [])) >= 6,
        "closed_loop_present": len(data.get("closed_loop", [])) >= 6,
    }
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "status": "pass" if not failed else "fail",
        "checks": checks,
        "failed": failed,
    }
