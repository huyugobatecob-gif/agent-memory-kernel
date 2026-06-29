# Threat Model

This document defines the local Agent Memory Kernel v1 threat model.

The kernel is not a hosted security boundary. It is a local memory contract that
must fail closed when memory is unsafe, unauthorized, stale, corrupted, or
insufficiently explained. Hosted tenancy, cloud key custody, managed schedulers,
and live provider controls belong to extensions or later hosted work.

## Security Goal

The main agent should receive only selected, policy-filtered, budgeted memory
with provenance and reasons. It must not scan the full graph or receive
deleted, distrusted, private, poisoned, stale, or unverifiable memory through a
derived surface.

## Trust Boundaries

| Boundary | Risk | Kernel control |
| --- | --- | --- |
| Source event -> candidate | Raw text may contain false claims, secrets, or prompt injection. | Candidate review, quarantine, trust labels, source metadata. |
| Candidate -> active memory | Untrusted claims may become durable facts. | Review lifecycle and write policy. |
| Active memory -> retrieval | Private, stale, or distrusted memory may be selected. | Read policy, lifecycle filters, current-best conflict handling. |
| Retrieval -> prompt envelope | Full graph or high-priority unsafe content may enter prompts. | Provider-neutral prompt envelope and renderer boundary tests. |
| Lifecycle mutation -> derived surfaces | Old evidence may reappear through graph, summary, export, or style state. | Derived invalidation and surface-specific filters. |
| Export/import | Bundles may be tampered with or revive inactive memory. | Manifest digest, provenance preservation, lifecycle and policy state import. |
| Local storage/recovery | Corrupt or partial stores may produce unsafe context. | Migration status, SQLite integrity checks, explicit no-memory fallback. |
| Audit/explainability | Operators may be unable to explain why memory exists or was injected. | Review history, router runs, source evidence, graph previews, and export metadata. |

## Required Threats

The machine-readable version of this table lives in
`memory_contract()["threat_model"]`.

| Threat id | Required controls | Verifiers |
| --- | --- | --- |
| `prompt_injection_memory` | quarantine injection-like content; keep untrusted sources reviewable; inject selected memory only | `secret_like_memory_is_quarantined`, `tool_prompt_injection_is_quarantined`, `prompt_envelope_contains_selected_content_only` |
| `untrusted_claim_promotion` | keep assistant/tool/web claims reviewable; allow write policy denial; expose Keeper changes | `untrusted_tool_claim_stays_reviewable`, `assistant_guess_stays_reviewable`, `keeper_write_is_reviewable`, `capability_report_blocks_denied_actions` |
| `private_lane_leak` | filter by scope/lane/namespace before retrieval; propagate policy to derived surfaces; record access decisions | `personal_lane_is_withheld`, `personal_lane_absent_from_derived_surfaces`, `personal_lane_absent_from_graph_surfaces`, `stored_read_policy_denies_injection` |
| `stale_or_inactive_evidence_revival` | filter inactive memory before prompts/exports; invalidate derived memory; suppress resolved losers | `deleted_memory_absent`, `distrusted_memory_absent_from_summaries_and_derived`, `derived_invalidation_is_auditable`, `resolved_conflict_suppresses_loser` |
| `malicious_or_poisoned_import` | verify bundle digests; screen digest-valid imported text before activation; roll back interrupted imports; preserve lifecycle and policy state; prevent redacted imports from restoring hidden content | `golden_trace_portable_bundle_manifest_roundtrip`, `golden_trace_poisoned_bundle_import_quarantines_prompt_injection`, `golden_trace_interrupted_import_rolls_back_partial_writes`, `golden_trace_import_restores_lifecycle_tombstones`, `golden_trace_import_preserves_policy_metadata`, `golden_trace_import_preserves_graph_evidence_chains` |
| `provider_prompt_boundary_failure` | keep memory out of unsafe provider system surfaces; preserve formatter metadata; keep Memory Tree as a selected-content renderer | `golden_trace_provider_prompt_formatters_preserve_boundaries`, `golden_trace_prompt_budget_trims_context_pack` |
| `corrupt_or_partial_store` | report migration status; run SQLite integrity checks; roll back interrupted imports; fail closed to no-memory mode | `migration_status_is_compatible`, `kernel_status_reports_compatible_versions`, `golden_trace_interrupted_import_rolls_back_partial_writes` |
| `audit_tampering_or_blind_spots` | expose who/what/why metadata; preserve provenance and review history; keep graph source previews; hash-chain new local audit entries for tamper evidence | `keeper_change_is_inspectable`, `professional_memory_injected_with_provenance`, `golden_trace_graph_browser_shows_source_previews`, `golden_trace_portable_bundle_manifest_roundtrip`, `audit_log_integrity_detects_tampering` |

## Non-Goals For Local V1

The local kernel does not claim to solve:

- hosted tenant isolation;
- cloud KMS custody;
- off-host backup trust;
- organization RBAC consoles;
- live provider-side prompt redaction;
- external notification delivery security;
- malicious local operator/root access.

Those are deployment or hosted-product responsibilities. The kernel still must
export enough policy, provenance, version, and audit metadata for those layers
to enforce their own controls.

## Remaining Hardening

The current repository has baseline executable coverage for the required threat
ids through conformance, acceptance, migration, and bundle tests. Remaining v1
hardening should add:

- broader Import Trust Gateway fixtures across document, vault, source-event,
  graph-evidence, and adapter importer paths;
- explicit corrupted-store fixtures beyond `quick_check`;
- interrupted export recovery fixtures and broader interrupted importer fixtures
  beyond portable bundle imports;
- cross-version bundle compatibility fixtures;
- stronger audit-chain coverage for imported/subset audit rows and external
  notarization hooks where deployments need root-resistant evidence;
