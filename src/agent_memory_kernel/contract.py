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

DEFAULT_PACKS: dict[str, dict[str, Any]] = {
    "personal": {
        "lane": "personal",
        "purpose": (
            "Personal preferences, stable personal context, relationships, "
            "recurring context, and communication style."
        ),
        "includes": [
            "directly stated preferences",
            "stable user facts",
            "communication style",
            "relationships and recurring personal context",
        ],
        "excludes": [
            "secrets unless explicitly approved for storage",
            "professional project facts unless policy allows cross-lane use",
            "assistant guesses that were not reviewed",
        ],
        "retrieval_default": "explicit_only",
        "write_policy": "direct user statements may be proposed; inferred facts require review",
        "prompt_boundary": "withheld from professional-only prompts unless explicit policy allows it",
        "template": "templates/vault/personal.md",
    },
    "professional": {
        "lane": "professional",
        "purpose": (
            "Projects, decisions, constraints, collaborators, work rules, "
            "gotchas, attempts, outcomes, and reusable work patterns."
        ),
        "includes": [
            "project rules and decisions",
            "constraints and collaborators",
            "successful patterns and failed attempts",
            "operational lessons and gotchas",
        ],
        "excludes": [
            "private personal context unless policy allows cross-lane use",
            "untrusted tool/web/assistant claims before review",
            "secrets unless explicitly approved for storage",
        ],
        "retrieval_default": "default_work_lane",
        "write_policy": "agent and system writes are candidates until policy or review approves them",
        "prompt_boundary": "default work lane; still filtered by scope, namespace, policy, trust, and lifecycle",
        "template": "templates/vault/professional.md",
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

READ_ACTIONS = [
    "read",
    "inject",
    "export",
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

DERIVED_PROMPT_SURFACES = {
    "brain_style": {
        "priority": "advisory_system_append",
        "source": "digital_brain_state",
        "guardrail": (
            "Never override higher-priority instructions, user format requests, "
            "safety, or factual accuracy."
        ),
        "omit_when": [
            "memory access denied",
            "insufficient classified graph nodes",
            "balanced graph state",
        ],
    }
}

ADAPTER_CONTRACT: dict[str, Any] = {
    "version": "adapter-contract-v0.1",
    "principle": "Adapters consume the kernel contract; they do not define memory truth.",
    "capability_levels": [
        {
            "id": "read-only",
            "allows": ["contract", "status", "search", "retrieve", "explain"],
            "must_not": ["write", "promote", "mutate_lifecycle", "export_without_policy"],
        },
        {
            "id": "write-capable",
            "allows": ["record_source_event", "propose_candidate", "queue_keeper"],
            "must_not": ["auto_promote_untrusted_claims", "bypass_review_policy"],
        },
        {
            "id": "lifecycle-capable",
            "allows": ["approve", "reject", "correct", "delete", "distrust", "expire", "rollback"],
            "must_not": ["mutate_without_actor_policy", "drop_audit_or_review_history"],
        },
        {
            "id": "graph-capable",
            "allows": ["read_graph", "propose_graph_commands", "show_evidence"],
            "must_not": ["show_cross_scope_evidence", "revive_inactive_memory"],
        },
        {
            "id": "export-capable",
            "allows": ["export_profile", "import_profile", "export_bundle", "import_bundle"],
            "must_not": ["restore_redacted_content", "activate_pending_or_rejected_memory"],
        },
        {
            "id": "prompt-injection-capable",
            "allows": ["before_model_call", "build_prompt_envelope", "format_provider_prompt"],
            "must_not": ["inject_full_graph", "place_memory_in_unsafe_system_surface"],
        },
    ],
    "adapter_types": {
        "runtime": {
            "required_hooks": ["before_model_call", "after_saved_turn"],
            "required_invariants": [
                "prompt_envelope_selected_budgeted_content_only",
                "scope_lane_namespace_isolation",
                "auditable_memory_actions",
            ],
        },
        "importer_exporter": {
            "required_hooks": ["export_profile", "import_profile"],
            "required_invariants": [
                "import_export_preserves_provenance_and_lifecycle",
                "distrusted_sources_do_not_influence_outputs",
            ],
        },
        "retrieval_enhancer": {
            "required_hooks": ["rank_after_policy_filtering"],
            "required_invariants": [
                "deterministic_retrieval_without_embeddings",
                "prompt_envelope_selected_budgeted_content_only",
            ],
        },
        "provider_formatter": {
            "required_hooks": ["format_prompt_envelope"],
            "required_invariants": [
                "prompt_envelope_selected_budgeted_content_only",
            ],
        },
    },
    "certification": {
        "local_only": True,
        "requires_live_provider": False,
        "commands": [
            "agent-memory conformance spec",
            "agent-memory conformance seed --db <db>",
            "agent-memory conformance run --db <db>",
            "agent-memory conformance certify --db <db> --adapter-name <name>",
        ],
    },
}

KERNEL_INVARIANTS = [
    {
        "id": "deleted_memory_absent_from_retained_evidence",
        "statement": "Deleted memory cannot reappear from retained source evidence.",
        "code_paths": [
            "MemoryStore.delete_memory",
            "MemoryStore.search",
            "MemoryStore.before_model_call",
            "MemoryStore.graph_browser",
            "MemoryStore.export_profile",
        ],
        "verifiers": [
            "deleted_memory_absent",
            "derived_invalidation_is_auditable",
        ],
    },
    {
        "id": "distrusted_sources_do_not_influence_outputs",
        "statement": "Distrusted or quarantined sources cannot influence retrieval, summaries, graph-derived state, exports, or prompts.",
        "code_paths": [
            "MemoryStore.distrust_memory",
            "MemoryStore.search",
            "MemoryStore.before_model_call",
            "MemoryStore.export_profile",
            "MemoryStore.derived_invalidations",
        ],
        "verifiers": [
            "distrusted_memory_absent_from_summaries_and_derived",
            "tool_prompt_injection_is_quarantined",
            "secret_like_memory_is_quarantined",
        ],
    },
    {
        "id": "scope_lane_namespace_isolation",
        "statement": "Scope, lane, namespace, personal, or private memory cannot leak across prompts, graph evidence, summaries, browser previews, or exports.",
        "code_paths": [
            "resolve_scope_access",
            "MemoryStore.before_model_call",
            "MemoryStore.graph_browser",
            "MemoryStore.export_profile",
            "MemoryStore.list_semantic_analyses",
        ],
        "verifiers": [
            "personal_lane_is_withheld",
            "personal_lane_absent_from_derived_surfaces",
            "personal_lane_absent_from_graph_surfaces",
            "stored_read_policy_denies_injection",
        ],
    },
    {
        "id": "lifecycle_mutations_invalidate_derived_memory",
        "statement": "Correction, rollback, delete, distrust, expire, and supersede invalidate derived memory and prompt/export surfaces.",
        "code_paths": [
            "MemoryStore.correct_memory",
            "MemoryStore.rollback_memory",
            "MemoryStore.list_memory_revisions",
            "MemoryStore.delete_memory",
            "MemoryStore.distrust_memory",
            "MemoryStore.expire_memory",
            "MemoryStore.supersede_memory",
            "MemoryStore.derived_invalidations",
        ],
        "verifiers": [
            "memory_lifecycle_diff_is_human_readable",
            "derived_invalidation_is_auditable",
            "golden_trace_import_restores_lifecycle_tombstones",
            "golden_trace_import_preserves_policy_metadata",
        ],
    },
    {
        "id": "prompt_envelope_selected_budgeted_content_only",
        "statement": "Prompt envelopes contain selected, policy-filtered, budgeted memory only and never the full graph.",
        "code_paths": [
            "MemoryStore.before_model_call",
            "MemoryStore.context_pack",
            "MemoryStore.memory_tree_pack",
            "MemoryStore.format_prompt_envelope",
        ],
        "verifiers": [
            "prompt_envelope_contains_selected_content_only",
            "golden_trace_prompt_budget_trims_context_pack",
            "golden_trace_provider_prompt_formatters_preserve_boundaries",
        ],
    },
    {
        "id": "deterministic_retrieval_without_embeddings",
        "statement": "Baseline retrieval ranking is deterministic without embeddings or live provider calls.",
        "code_paths": [
            "MemoryStore.before_model_call",
            "MemoryStore.current_best",
            "MemoryStore.search",
        ],
        "verifiers": [
            "golden_trace_deterministic_ranking_snapshot",
            "golden_trace_large_history_prompt_is_bounded",
        ],
    },
    {
        "id": "import_export_preserves_provenance_and_lifecycle",
        "statement": "Import/export preserves ids, provenance, evidence, tombstones, trust state, review history, policy metadata, and lifecycle state.",
        "code_paths": [
            "MemoryStore.export_profile",
            "MemoryStore.import_profile",
            "MemoryStore.export_bundle",
            "MemoryStore.verify_bundle",
            "MemoryStore.import_bundle",
        ],
        "verifiers": [
            "golden_trace_portable_bundle_manifest_roundtrip",
            "golden_trace_poisoned_bundle_import_quarantines_prompt_injection",
            "golden_trace_interrupted_import_rolls_back_partial_writes",
            "golden_trace_import_restores_lifecycle_tombstones",
            "golden_trace_import_preserves_review_history",
            "golden_trace_import_preserves_rejected_review_queue",
            "golden_trace_import_preserves_policy_metadata",
            "golden_trace_import_preserves_graph_evidence_chains",
        ],
    },
    {
        "id": "auditable_memory_actions",
        "statement": "Every read, write, inject, export, correction, deletion, denial, and lifecycle change is auditable.",
        "code_paths": [
            "MemoryStore.remember",
            "MemoryStore.before_model_call",
            "MemoryStore.explain_memory",
            "MemoryStore.memory_changes",
            "MemoryStore.explain_router_run",
            "MemoryStore.export_profile",
            "MemoryStore.audit_integrity_report",
        ],
        "verifiers": [
            "professional_memory_injected_with_provenance",
            "memory_explain_shows_why_remembered",
            "keeper_change_is_inspectable",
            "golden_trace_graph_browser_shows_source_previews",
            "audit_log_integrity_detects_tampering",
        ],
    },
    {
        "id": "capability_grants_gate_local_actions",
        "statement": "Local actors can perform only actions allowed by capability grants and policy.",
        "code_paths": [
            "MemoryStore.capability_report",
            "MemoryStore.set_read_policy",
            "MemoryStore.set_write_policy",
            "MemoryStore.before_model_call",
            "MemoryStore.approve_candidate",
        ],
        "verifiers": [
            "capability_report_blocks_denied_actions",
            "stored_read_policy_denies_injection",
        ],
    },
    {
        "id": "large_histories_stay_bounded",
        "statement": "Large histories remain bounded and predictable for retrieval, prompt budget, export size, and local resource usage.",
        "code_paths": [
            "MemoryStore.before_model_call",
            "MemoryStore.prompt_budget_profile",
            "MemoryStore.migration_status",
            "MemoryStore.kernel_status",
        ],
        "verifiers": [
            "golden_trace_large_history_prompt_is_bounded",
            "golden_trace_prompt_budget_trims_context_pack",
            "kernel_status_reports_compatible_versions",
        ],
    },
]

THREAT_MODEL = [
    {
        "id": "prompt_injection_memory",
        "threat": "User, tool, web, log, or imported text tries to store instructions for future models.",
        "required_controls": [
            "secret_or_injection_like_content_is_quarantined",
            "untrusted_sources_stay_reviewable_by_default",
            "prompt_envelope_uses_selected_memory_only",
        ],
        "verifiers": [
            "secret_like_memory_is_quarantined",
            "tool_prompt_injection_is_quarantined",
            "prompt_envelope_contains_selected_content_only",
        ],
    },
    {
        "id": "untrusted_claim_promotion",
        "threat": "Assistant guesses, tool output, or external documents become trusted facts without review.",
        "required_controls": [
            "assistant_tool_web_claims_require_review",
            "write_policy_can_deny_auto_approval",
            "keeper_changes_are_inspectable",
        ],
        "verifiers": [
            "untrusted_tool_claim_stays_reviewable",
            "assistant_guess_stays_reviewable",
            "keeper_write_is_reviewable",
            "capability_report_blocks_denied_actions",
        ],
    },
    {
        "id": "private_lane_leak",
        "threat": "Personal/private memory appears in professional, project, export, graph, or summary surfaces.",
        "required_controls": [
            "scope_lane_namespace_filtering_before_retrieval",
            "derived_surfaces_inherit_source_policy",
            "prompt_metadata_records_access_decisions",
        ],
        "verifiers": [
            "personal_lane_is_withheld",
            "personal_lane_absent_from_derived_surfaces",
            "personal_lane_absent_from_graph_surfaces",
            "stored_read_policy_denies_injection",
        ],
    },
    {
        "id": "stale_or_inactive_evidence_revival",
        "threat": "Deleted, distrusted, corrected, expired, superseded, or stale evidence re-enters retrieval through graph, summary, export, or prompt caches.",
        "required_controls": [
            "inactive_memory_filtered_before_prompt_and_export",
            "derived_memory_invalidates_on_lifecycle_mutation",
            "current_best_suppresses_resolved_losers",
        ],
        "verifiers": [
            "deleted_memory_absent",
            "distrusted_memory_absent_from_summaries_and_derived",
            "derived_invalidation_is_auditable",
            "resolved_conflict_suppresses_loser",
        ],
    },
    {
        "id": "malicious_or_poisoned_import",
        "threat": "A bundle, profile, vault, or imported source changes payloads, revives inactive memory, strips provenance, or bypasses policies.",
        "required_controls": [
            "portable_bundles_verify_manifest_digest_before_import",
            "digest_valid_imported_text_is_screened_before_activation",
            "interrupted_import_rolls_back_partial_writes",
            "imports_preserve_lifecycle_and_policy_state",
            "redacted_imports_cannot_restore_hidden_content",
        ],
        "verifiers": [
            "golden_trace_portable_bundle_manifest_roundtrip",
            "golden_trace_poisoned_bundle_import_quarantines_prompt_injection",
            "golden_trace_interrupted_import_rolls_back_partial_writes",
            "golden_trace_import_restores_lifecycle_tombstones",
            "golden_trace_import_preserves_review_history",
            "golden_trace_import_preserves_rejected_review_queue",
            "golden_trace_import_preserves_policy_metadata",
            "golden_trace_import_preserves_graph_evidence_chains",
        ],
    },
    {
        "id": "provider_prompt_boundary_failure",
        "threat": "Adapter formatting places memory in a higher-priority provider system surface or hides memory provenance.",
        "required_controls": [
            "provider_formatters_preserve_memory_boundaries",
            "memory_tree_supplement_stays_out_of_system_surface",
            "formatter_metadata_records_provider_shape",
        ],
        "verifiers": [
            "golden_trace_provider_prompt_formatters_preserve_boundaries",
            "golden_trace_prompt_budget_trims_context_pack",
        ],
    },
    {
        "id": "corrupt_or_partial_store",
        "threat": "Partially migrated, corrupted, oversized, interrupted, or unavailable local stores silently return unsafe memory.",
        "required_controls": [
            "migration_status_is_visible",
            "sqlite_integrity_check_can_fail_closed",
            "no_memory_fallback_is_explicit",
            "interrupted_import_rolls_back_partial_writes",
        ],
        "verifiers": [
            "migration_status_is_compatible",
            "kernel_status_reports_compatible_versions",
            "golden_trace_interrupted_import_rolls_back_partial_writes",
        ],
    },
    {
        "id": "audit_tampering_or_blind_spots",
        "threat": "Operators cannot reconstruct who wrote, changed, retrieved, denied, exported, or injected memory.",
        "required_controls": [
            "retrieval_and_lifecycle_actions_emit_audit_metadata",
            "why_remembered_and_why_injected_are_available",
            "export_and_import_preserve_review_history_and_provenance",
            "local_audit_entries_are_hash_chained_for_tamper_evidence",
        ],
        "verifiers": [
            "keeper_change_is_inspectable",
            "professional_memory_injected_with_provenance",
            "golden_trace_graph_browser_shows_source_previews",
            "golden_trace_portable_bundle_manifest_roundtrip",
            "audit_log_integrity_detects_tampering",
        ],
    },
]

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
            "post-turn Keeper retries are idempotent for the same runtime payload",
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
            "Router usefulness feedback can mark selected memory as helpful, ignored, missing, or harmful",
            "review decisions are regression-testable",
        ],
    },
    {
        "gate": "inspection_and_operator_control",
        "requires": [
            "operators can inspect what changed after a saved turn by Keeper job or thread",
            "post-turn reports include saved turns, event, candidates, promoted memories, affected surfaces, and audit trail",
            "reports expose review, correction, rollback, distrust, expire, or delete handles without silently mutating memory",
        ],
    },
    {
        "gate": "governed_read_time_policy",
        "requires": [
            "Router ranking accounts for relevance, recency, trust, scope, sensitivity, conflict status, and token budget",
            "retrieved memory is marked as evidence, rule, preference, or advisory style before entering the prompt",
            "operators can explain why a branch was selected, skipped, or truncated",
        ],
    },
    {
        "gate": "derived_memory_invalidation",
        "requires": [
            "correction, deletion, distrust, expiry, and supersession invalidate derived summaries and graph surfaces",
            "stale derived prompt surfaces such as graph-derived style are suppressible",
            "cached envelopes or exports do not reintroduce inactive memory",
        ],
    },
    {
        "gate": "capability_and_consent",
        "requires": [
            "read, write, promote, inject, export, distrust, and delete actions are policy-checkable",
            "multi-agent access is scoped by user, project, agent, source trust, and delegation",
            "audits can replay which memory an agent saw and why it was allowed",
        ],
    },
    {
        "gate": "operational_failure_model",
        "requires": [
            "slow, unavailable, corrupted, partially migrated, or oversized memory has defined fallback behavior",
            "no-memory mode is explicit and auditable",
            "schema and contract versions are visible to adapters",
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
        "default_packs": DEFAULT_PACKS,
        "memory_kinds": MEMORY_KINDS,
        "write_actions": WRITE_ACTIONS,
        "read_actions": READ_ACTIONS,
        "trust_levels": TRUST_LEVELS,
        "sensitivity_levels": SENSITIVITY_LEVELS,
        "derived_prompt_surfaces": DERIVED_PROMPT_SURFACES,
        "adapter_contract": ADAPTER_CONTRACT,
        "kernel_invariants": KERNEL_INVARIANTS,
        "threat_model": THREAT_MODEL,
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
    gate_names = {str(item.get("gate")) for item in data.get("acceptance_gates", [])}
    checks = {
        "version_present": bool(data.get("version")),
        "personal_lane_present": "personal" in data.get("lanes", {}),
        "professional_lane_present": "professional" in data.get("lanes", {}),
        "project_extension_present": "project" in data.get("lanes", {}),
        "default_packs_present": {"personal", "professional"}.issubset(
            set(data.get("default_packs", {}).keys())
        ),
        "default_packs_have_boundaries": all(
            item.get("purpose")
            and item.get("includes")
            and item.get("excludes")
            and item.get("prompt_boundary")
            for item in data.get("default_packs", {}).values()
        ),
        "write_actions_present": set(WRITE_ACTIONS).issubset(set(data.get("write_actions", []))),
        "read_actions_present": set(READ_ACTIONS).issubset(set(data.get("read_actions", []))),
        "acceptance_gates_present": len(data.get("acceptance_gates", [])) >= 6,
        "governed_read_time_policy_present": "governed_read_time_policy" in gate_names,
        "derived_memory_invalidation_present": "derived_memory_invalidation" in gate_names,
        "capability_and_consent_present": "capability_and_consent" in gate_names,
        "inspection_and_operator_control_present": "inspection_and_operator_control" in gate_names,
        "operational_failure_model_present": "operational_failure_model" in gate_names,
        "closed_loop_present": len(data.get("closed_loop", [])) >= 6,
        "brain_style_surface_present": "brain_style" in data.get("derived_prompt_surfaces", {}),
        "adapter_contract_present": bool(data.get("adapter_contract", {}).get("version")),
        "adapter_capability_levels_present": {
            "read-only",
            "write-capable",
            "lifecycle-capable",
            "graph-capable",
            "export-capable",
            "prompt-injection-capable",
        }.issubset(
            {
                str(item.get("id"))
                for item in data.get("adapter_contract", {}).get("capability_levels", [])
            }
        ),
        "adapter_types_have_invariants": all(
            item.get("required_hooks") and item.get("required_invariants")
            for item in data.get("adapter_contract", {}).get("adapter_types", {}).values()
        ),
        "kernel_invariants_present": len(data.get("kernel_invariants", [])) >= 10,
        "kernel_invariants_have_verifiers": all(
            item.get("id")
            and item.get("statement")
            and item.get("code_paths")
            and item.get("verifiers")
            for item in data.get("kernel_invariants", [])
        ),
        "threat_model_present": len(data.get("threat_model", [])) >= 8,
        "threat_model_verifiers_present": all(
            item.get("id")
            and item.get("required_controls")
            and item.get("verifiers")
            for item in data.get("threat_model", [])
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "status": "pass" if not failed else "fail",
        "checks": checks,
        "failed": failed,
    }
