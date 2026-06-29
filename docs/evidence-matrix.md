# Evidence Matrix

This matrix keeps public readiness claims tied to local evidence. A claim is
ready for the README only when it has a command, test, document, or explicit
non-goal.

Verification baseline:

- package status: `v0.1.0 alpha`
- baseline commit before this public-readiness pass: `f6de1d2`
- local verification date for this public-readiness pass: 2026-06-29
- release checklist: [release-checklist.md](release-checklist.md)
- CI workflow: [../.github/workflows/tests.yml](../.github/workflows/tests.yml)

Update the `Last verified` column when preparing a tag or public release.

| Claim | Command or test | Document | Status | Last verified |
| --- | --- | --- | --- | --- |
| Local SQLite source of truth exists for memory state. | `tests/test_memory_store.py`; `PYTHONPATH=src python3 -m agent_memory_kernel.cli migration-status --db /tmp/amk.db` | [SPEC.md](../SPEC.md), [recovery.md](recovery.md) | implemented | 2026-06-29 local pass |
| Source events become candidates before durable memory. | `remember`, `review list`; `tests/test_orchestrator.py` | [SPEC.md](../SPEC.md), [memory-lifecycle-contract.md](memory-lifecycle-contract.md) | implemented | 2026-06-29 local pass |
| Candidate lifecycle is reviewable and auditable. | `review list`, `review approve`, `review reject`; `tests/test_review_inbox.py` | [review-workflow.md](review-workflow.md) | implemented | 2026-06-29 local pass |
| Active memory has lifecycle controls. | `correct`, `rollback`, `delete`, `distrust`, `expire`, `supersede`; `tests/test_memory_store.py` | [memory-lifecycle-contract.md](memory-lifecycle-contract.md) | implemented | 2026-06-29 local pass |
| Prompt envelopes contain selected memory, not the full graph. | `before-model-call`; `conformance assert`; scenario `prompt_envelope_contains_selected_content_only` | [runtime-contract.md](runtime-contract.md), [cross-model-context-contract.md](cross-model-context-contract.md) | implemented | 2026-06-29 local pass |
| Router selection records reasons and provenance. | `router-explain`, `before-model-call`; `tests/test_memory_observability.py` | [memory-tree-pack.md](memory-tree-pack.md) | implemented | 2026-06-29 local pass |
| Keeper writes are reviewable by default. | `after-saved-turn`; `memory-changes`; scenarios `keeper_write_is_reviewable`, `keeper_retry_is_idempotent` | [keeper-extraction.md](keeper-extraction.md), [runtime-contract.md](runtime-contract.md) | implemented | 2026-06-29 local pass |
| Scope/lane/namespace isolation prevents default cross-boundary prompt leaks. | `conformance assert`; scenarios `personal_lane_is_withheld`, `personal_lane_absent_from_graph_surfaces` | [security-identity-contract.md](security-identity-contract.md), [default-packs.md](default-packs.md) | implemented | 2026-06-29 local pass |
| Read policy denial returns a no-memory envelope. | `read-policy set`; `before-model-call`; scenario `stored_read_policy_denies_injection` | [runtime-contract.md](runtime-contract.md), [trust-and-security.md](trust-and-security.md) | implemented | 2026-06-29 local pass |
| Secret-like and prompt-injection-like content is quarantined. | `conformance assert`; scenarios `secret_like_memory_is_quarantined`, `tool_prompt_injection_is_quarantined` | [threat-model.md](threat-model.md), [trust-and-security.md](trust-and-security.md) | implemented | 2026-06-29 local pass |
| Import/export preserves provenance, lifecycle, and policy metadata. | `export-bundle`, `verify-bundle`, `import-bundle`; conformance bundle scenarios | [SPEC.md](../SPEC.md), [recovery.md](recovery.md) | implemented | 2026-06-29 local pass |
| Recovery detects migration/store compatibility issues. | `migration-status`, `kernel-status`, `restore-drill`; `tests/test_backup_migration.py` | [recovery.md](recovery.md) | implemented | 2026-06-29 local pass |
| Memory explainability is available locally. | `memory-explain`; scenario `memory_explain_shows_why_remembered` | [review-workflow.md](review-workflow.md) | implemented | 2026-06-29 local pass |
| Public conformance can be run without live providers. | `conformance spec`, `conformance seed`, `conformance assert`, `conformance certify` | [adapter-certification.md](adapter-certification.md), [adapter-contract.md](adapter-contract.md) | implemented | 2026-06-29 local pass |
| No-memory fallback is explicit and auditable. | `before-model-call` with denied read policy; `tests/test_operational_failure.py` | [trust-and-security.md](trust-and-security.md), [runtime-contract.md](runtime-contract.md) | implemented | 2026-06-29 local pass |
| Local bounded retrieval avoids full-history prompt injection. | scenario `golden_trace_large_history_prompt_is_bounded` | [resource-budgets.md](resource-budgets.md), [core-status-audit.md](core-status-audit.md) | implemented for bounded selection; broader benchmarks are post-v0.1.0 | 2026-06-29 local pass |
| CI publishes repeatable local evidence. | `.github/workflows/tests.yml` | [release-checklist.md](release-checklist.md) | strengthened in public-readiness pass | verify after push |

## Evidence Rules

- If a README claim cannot point to this matrix, downgrade it or move it to an
  extension/non-goal section.
- If a command fails, the affected claim becomes blocked until the failure is
  fixed or the claim is removed.
- Hosted, provider, billing, notification, team, and cloud custody claims stay
  out of v0.1.0 unless a local deterministic proof exists.
