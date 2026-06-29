# Invariant Verifier Map

This document maps AMK-000 kernel laws to implementation paths and executable
verifiers. The machine-readable version lives in
`memory_contract()["kernel_invariants"]`.

Core work is not considered complete because a command exists. It is complete
when the relevant invariant has code paths and verifier coverage.

| Invariant id | Code paths | Verifiers |
| --- | --- | --- |
| `deleted_memory_absent_from_retained_evidence` | `delete_memory`, `search`, `before_model_call`, `graph_browser`, `export_profile` | `deleted_memory_absent`, `derived_invalidation_is_auditable` |
| `distrusted_sources_do_not_influence_outputs` | `distrust_memory`, `search`, `before_model_call`, `export_profile`, `derived_invalidations` | `distrusted_memory_absent_from_summaries_and_derived`, `tool_prompt_injection_is_quarantined`, `secret_like_memory_is_quarantined` |
| `scope_lane_namespace_isolation` | `resolve_scope_access`, `before_model_call`, `graph_browser`, `export_profile`, semantic analysis listing | `personal_lane_is_withheld`, `personal_lane_absent_from_derived_surfaces`, `personal_lane_absent_from_graph_surfaces`, `stored_read_policy_denies_injection` |
| `lifecycle_mutations_invalidate_derived_memory` | `correct_memory`, `rollback_memory`, `delete_memory`, `distrust_memory`, `expire_memory`, `supersede_memory`, `derived_invalidations` | `derived_invalidation_is_auditable`, `golden_trace_import_restores_lifecycle_tombstones`, `golden_trace_import_preserves_policy_metadata` |
| `prompt_envelope_selected_budgeted_content_only` | `before_model_call`, `context_pack`, `memory_tree_pack`, prompt formatter | `prompt_envelope_contains_selected_content_only`, `golden_trace_prompt_budget_trims_context_pack`, `golden_trace_provider_prompt_formatters_preserve_boundaries` |
| `deterministic_retrieval_without_embeddings` | `before_model_call`, `current_best`, `search` | `golden_trace_deterministic_ranking_snapshot`, `golden_trace_large_history_prompt_is_bounded` |
| `import_export_preserves_provenance_and_lifecycle` | `export_profile`, `import_profile`, `export_bundle`, `verify_bundle`, `import_bundle` | `golden_trace_portable_bundle_manifest_roundtrip`, `golden_trace_poisoned_bundle_import_quarantines_prompt_injection`, `golden_trace_interrupted_import_rolls_back_partial_writes`, `golden_trace_import_restores_lifecycle_tombstones`, `golden_trace_import_preserves_policy_metadata`, `golden_trace_import_preserves_graph_evidence_chains` |
| `auditable_memory_actions` | `remember`, `before_model_call`, `memory_changes`, `explain_router_run`, `export_profile`, `audit_integrity_report` | `professional_memory_injected_with_provenance`, `keeper_change_is_inspectable`, `golden_trace_graph_browser_shows_source_previews`, `audit_log_integrity_detects_tampering` |
| `capability_grants_gate_local_actions` | `capability_report`, `set_read_policy`, `set_write_policy`, `before_model_call`, `approve_candidate` | `capability_report_blocks_denied_actions`, `stored_read_policy_denies_injection` |
| `large_histories_stay_bounded` | `before_model_call`, `prompt_budget_profile`, `migration_status`, `kernel_status` | `golden_trace_large_history_prompt_is_bounded`, `golden_trace_prompt_budget_trims_context_pack`, `kernel_status_reports_compatible_versions` |

## How To Use This Map

When adding core behavior:

1. Identify which invariant the change affects.
2. Add or update the relevant code path.
3. Add a unit test, conformance scenario, or golden trace.
4. Update `memory_contract()["kernel_invariants"]` if the invariant, path, or
   verifier changes.

When adding an adapter or extension:

1. Consume the existing contract.
2. Run the conformance suite locally.
3. Do not bypass policy filters, lifecycle filters, or prompt-envelope
   boundaries.

## Remaining Hardening

The map currently points to baseline verifiers. Remaining v1 work should expand:

- namespace-specific adversarial fixtures;
- capability denied-action fixtures for every action family;
- broader Import Trust Gateway fixtures across source events, vault imports,
  graph evidence, and adapter importer paths;
- corrupted-store, interrupted export, and non-bundle importer recovery fixtures;
- imported/subset audit-chain fixtures and optional external notarization hooks;
- latency/resource fixtures for very large local stores.
