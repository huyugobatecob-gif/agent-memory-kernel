# Core Status Audit

This audit states the current v1 target and tracks whether the repository proves
that target with code, tests, conformance fixtures, and documentation.

## Factual V1 Goal

Agent Memory Kernel v1 is a universal, local-first, auditable memory kernel. It
must let any runtime record observed events, propose reviewable memory, promote
safe memory, retrieve selected context before a model call, save the resulting
turn, and propose the next memory update after the turn.

V1 is not a Hermes rollout, SEO workflow, hosted SaaS, vector-search product,
dashboard, billing system, or runtime orchestrator. Those may exist as
extensions, adapters, demos, or later hosted work, but they cannot define the
kernel contract.

The release-critical loop is:

```text
source event
-> candidate memory
-> review or policy decision
-> active memory
-> graph/evidence model
-> Router-selected prompt envelope
-> saved turn
-> Keeper proposal for the next update
```

The main agent receives selected, policy-filtered, budgeted memory content. It
does not scan the full graph, raw source event stream, or hidden tags.

## Authority Order

If project documents disagree, use this order:

1. [kernel-charter.md](kernel-charter.md)
2. [amk-000-kernel-invariants.md](amk-000-kernel-invariants.md)
3. `memory_contract()` in `src/agent_memory_kernel/contract.py`
4. [SPEC.md](../SPEC.md)
5. [implementation-plan.md](implementation-plan.md)
6. this audit and the roadmap docs

[full-memory-gap-plan.md](full-memory-gap-plan.md) is historical context unless
it agrees with the charter, AMK-000, and the machine-readable contract.

## Status Labels

- `done`: implemented and covered by current unit tests, conformance fixtures,
  CLI assertions, or other deterministic local evidence.
- `extension`: optional adapter, pack, UI, provider, domain, or local operator
  workflow that consumes the kernel contract.
- `later-hosted`: future hosted/platform layer that must not block local v1.

There are no current `missing` v1 blockers in this audit. Remaining work is
classified as post-v1 hardening unless a future change alters kernel truth,
lifecycle, policy, retrieval, prompt boundaries, import/export, or conformance.

## Core Gate Status

| Gate | Status | Current evidence | Post-v1 hardening |
| --- | --- | --- | --- |
| Gate 0: Normative boundary | done | README, SPEC, `kernel-charter.md`, `implementation-plan.md`, `backlog-cutover.md`, `hosted-roadmap.md`; reference slice now uses a generic project iteration fixture instead of a domain workflow. | Keep future roadmap items labeled `core`, `extension`, or `later-hosted`. |
| Gate 1: Core loop golden trace | done | `slice seed/run/assert`, `acceptance seed/assert`, `tests/test_memory_store.py::test_executable_vertical_slice_seed_run_assert`, `tests/test_contract_acceptance.py`. | Add more domain-neutral examples only after they pass the same slice contract. |
| Gate 2: Lifecycle propagation | done | `correct_memory`, `rollback_memory`, `delete_memory`, `distrust_memory`, `expire_memory`, `supersede_memory`, `derived_invalidations`, `memory-diff-v0.1`, lifecycle import/export conformance. | Add broader cross-version and redacted-bundle edge cases. |
| Gate 3: Scope/lane/namespace isolation | done | read/write policies, denied injection/export/lifecycle fixtures, personal/professional isolation, graph/evidence scope fixtures, derived summary and semantic-analysis filters. | Add more adversarial namespace fixtures for third-party packs and importers. |
| Gate 4: Trust and explainability | done | `memory-explain`, `memory-changes`, `router-explain`, review inbox, capability reports, audit-chain integrity report, human-readable lifecycle diffs. | Add richer operator UX on top of the stable local surfaces. |
| Gate 5: Router and prompt boundary | done | `before_model_call`, selected-content-only prompt envelope, `MEMORY_TREE_SUPPLEMENT`, no-full-graph conformance, deterministic ranking trace, prompt-budget trim trace, provider formatter boundary trace, large-history bounded trace. | Add adapter-specific prompt snapshots as extension certification fixtures. |
| Gate 6: Keeper safety | done | deterministic extractor, `LLMKeeperExtractor` contract, reviewable Keeper writes, idempotent retry, false-trust fixtures for tool output and assistant guesses, secret/prompt-injection quarantine. | Add provider-specific Keeper prompts and tuning as extensions. |
| Gate 7: Portability, recovery, and versioning | done | profile export/import, `.amk` bundle manifest/checksum, lifecycle tombstone restore, review queue restore, policy metadata restore, graph evidence-chain restore, poisoned bundle screening, interrupted import rollback, migration/kernel status. | Add interrupted non-bundle import, interrupted export, stale backup, and cross-version bundle matrices. |
| Gate 8: Public local surface | done | Python API, CLI, local HTTP, stdio MCP, `contract assert`, `conformance spec-assert`, adapter capability contract, kernel status, certification and registry-entry output. | Keep HTTP/MCP as mirrors over the same local contract; do not make them separate truth paths. |
| Gate 9: Public v1 package | done | README points to the kernel spec and reference loop, runtime/domain examples are optional, conformance commands are documented, tests cover installable local behavior. | Release publishing, hosted registry, and live runtime rollout remain outside local v1. |

## Kernel Capability Map

| Capability | Status | Evidence |
| --- | --- | --- |
| SQLite local source of truth | done | `schema.sql`, `MemoryStore`, migration status, backup/restore tests. |
| Source events and saved turns | done | `remember`, `record_turn`, `after_saved_turn`, conversation turns, thread messages, source refs. |
| Candidate memory lifecycle | done | review inbox, approve/reject/batch review, quarantine, unsafe-source tests. |
| Active memory lifecycle | done | correction, rollback, delete, distrust, expire, supersede, tombstones, lifecycle diffs. |
| Scope/lane/namespace isolation | done | generic scope model, personal/professional starter packs, read/write policy fixtures, derived/graph/export filters. |
| Graph nodes, edges, and evidence | done | graph tables, graph commands, node/edge evidence, graph browser source previews, graph evidence import/export. |
| Keeper contract | done | post-turn Keeper job records, candidate output, graph command normalization, idempotent retry, reviewable unsafe claims. |
| Router contract | done | selected branch ids, selection decisions, policy factors, budget metadata, no-memory fallback, feedback and quality reports. |
| Prompt envelope and renderers | done | provider-neutral envelope, selected Memory Tree supplement, provider formatter certification, prompt-budget trim. |
| Review and explainability | done | why remembered, why injected, why changed, why denied, lifecycle history, audit trail and operator handles. |
| Read/write/export/inject policies | done | capability report, read/write policy persistence, denied action dry-runs, import/export policy preservation. |
| Import/export provenance | done | profile and bundle round trips, manifest digest, redaction profiles, review history, rejected queue, policy and graph evidence restoration. |
| Deterministic ranking | done | local lexical/semantic reranking, current-best logic, deterministic ranking conformance, large-history bounded prompt trace. |
| Conformance and golden traces | done | `conformance spec/assert/certify`, acceptance harness, adapter registry entry output, invariant verifier map. |
| Stable local API/versioning | done | machine-readable contract, schema/bundle/lifecycle/policy versions, migration/kernel status surfaces. |
| Threat and recovery model | done | `threat-model.md`, quarantine, poisoned import screening, audit tamper detection, no-memory fallback, interrupted import rollback. |
| Resource and latency visibility | done | prompt-budget profile, large-history bounded trace, Router/Keeper duration metadata, observability latency SLO tests. |

## Not Core

| Capability | Classification | Placement |
| --- | --- | --- |
| Hermes rollout or named runtime rollout | extension | `adapters/`, runtime examples, integration docs. |
| SEO, research, CRM, support, QA, or outcome-loop packs | extension | Domain packs over generic memory kinds and policies. |
| Personal/professional starter templates | extension fixture | Default packs proving generic lane isolation, not the only ontology. |
| HTTP/MCP services | extension surface | Optional local mirrors over the stable contract. |
| Provider prompt formatters | extension surface | Boundary-preserving compatibility fixtures. |
| Embeddings, ANN, and provider rerankers | extension | Optional post-policy retrieval enhancers. |
| Rich browser UI, graph UI, notification queues, billing reports | extension | Operator workflows over core audit/review/observability. |
| Markdown vault/document importers | extension | Import/export bridges that must preserve provenance and review. |
| Hosted identity, tenancy, RBAC, dashboards, registry, KMS, sync | later-hosted | Future hosted/platform layer. |

## Post-V1 Hardening Backlog

These items are useful, but they are not unresolved local v1 blockers:

1. Add wider namespace adversarial fixtures for third-party packs, agent roles,
   import packages, and bundle namespaces.
2. Add cross-version bundle/import matrices once there is more than one public
   contract or schema version.
3. Add interrupted export and interrupted non-bundle importer recovery fixtures.
4. Add corrupted-store and stale-backup drills beyond current migration,
   quick-check, backup/restore, and interrupted bundle rollback evidence.
5. Add larger-scale resource benchmarks beyond deterministic bounded-history
   traces and observability SLO reports.
6. Add optional external notarization hooks for deployments that need
   root-resistant audit evidence.
7. Add adapter-specific prompt and Keeper snapshots as extension certification
   suites.

## Verification Evidence

The current local v1 gate is the release checklist in
[implementation-plan.md](implementation-plan.md):

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli contract assert
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance spec-assert
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice seed --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice run --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice assert --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance seed --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m unittest discover -s tests
```

If any command fails, the failed invariant becomes the next core blocker.
