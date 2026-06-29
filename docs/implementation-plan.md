# Implementation Plan

This is the v1 implementation plan for Agent Memory Kernel.

The project is a universal, local-first, auditable memory kernel for agents and
human workflows. It is not a private runtime rollout, not a hosted platform, and
not a domain pack. Runtime adapters, personal/professional starter templates,
Memory Tree renderers, browser UI, MCP/HTTP services, embeddings, notifications,
and domain workflows are allowed in the repository, but they must consume the
kernel contract rather than define it.

The governing documents are [../SPEC.md](../SPEC.md),
[kernel-charter.md](kernel-charter.md),
[amk-000-kernel-invariants.md](amk-000-kernel-invariants.md), and
[backlog-cutover.md](backlog-cutover.md). Current implementation state is
tracked in [core-status-audit.md](core-status-audit.md).

## Public V1 Outcome

Agent Memory Kernel v1 is complete when a local store can prove, without a live
model provider or hosted service, that it can:

```text
observe source event
-> propose candidate memory
-> review or apply policy
-> promote active memory
-> retrieve selected allowed memory
-> build a provider-neutral prompt envelope
-> explain why memory was stored and shown
-> correct, delete, distrust, expire, supersede, quarantine, or roll back memory
-> export/import the record without reviving unsafe or inactive state
```

The main agent must not scan the full graph. It receives only selected,
policy-filtered, budgeted memory with provenance and selection reasons.

## V1 Core Boundary

Core work changes memory truth, lifecycle, policy, retrieval, prompt injection,
portability, or conformance.

V1 core includes:

- SQLite local source of truth and migration checks.
- Source events, saved turns, candidates, active memories, graph nodes, graph
  edges, and evidence links.
- Generic `scope`, `lane`, `namespace`, `actor`, `policy`, and `surface`
  primitives.
- Keeper proposal contract and Router retrieval contract.
- Review lifecycle and lifecycle mutations: approve, reject, correct, delete,
  distrust, expire, supersede, quarantine, and rollback.
- Read, write, inject, export, and lifecycle policies.
- Local actor capability grants and policy simulation.
- Provider-neutral prompt envelope with selected content, provenance, reasons,
  warnings, and budget decisions.
- Audit and explainability for why memory exists and why it was shown.
- Deterministic retrieval without mandatory embeddings.
- Provenance-preserving import/export with tombstones, trust state, policy
  metadata, review history, lifecycle state, evidence chains, and derived
  invalidations.
- Threat model, recovery model, stable local API/versioning, conformance
  fixtures, golden traces, and latency/resource budgets.

V1 core does not include:

- Hermes, SEO, trading, CRM, research, support, or other domain rollout.
- Hosted identity, tenancy, RBAC, hosted dashboards, billing dashboards, hosted
  sync, or team collaboration.
- Remote MCP deployment, hosted API servers, managed schedulers, managed alerts,
  live notification sending, or KMS/off-host custody.
- Mandatory ANN/vector search, live embeddings, live provider certification, or
  provider-specific prompts as correctness requirements.
- Browser review UI, rich graph UI, Digital Brain presentation, Memory Tree
  branding, markdown vault adapters, and full agent runners as v1 blockers.

Those items may remain as extensions, examples, or later hosted work. They must
not be listed as requirements for local v1 completion.

## Plain-Language Model

For public users, the kernel should answer four questions:

- What was stored?
- Who or what is allowed to read it?
- How can it be corrected, hidden, distrusted, exported, or deleted?
- Why did the agent receive this memory for this request?

Internal terms should map back to those questions:

- `source_event`: raw observed evidence.
- `candidate_memory`: a proposed memory awaiting review or policy promotion.
- `active_memory`: approved memory that may enter retrieval.
- `scope/lane/namespace`: access boundaries and grouping rules.
- `policy`: local rules for write, read, inject, export, redaction, and
  lifecycle actions.
- `Keeper`: post-turn writer that proposes memories from saved events.
- `Router`: pre-call reader that selects allowed memory.
- `prompt envelope`: provider-neutral payload given to the main agent.
- `Memory Tree`: optional renderer over selected memory, not the source of
  truth.

## Completion Gates

Every v1 feature must pass the gate that matches the risk it creates.

| Gate | Required proof |
| --- | --- |
| Kernel boundary | The item is classified as `core`, `extension`, or `later-hosted`; non-core work is not a v1 blocker. |
| Invariant map | Each memory-safety invariant maps to schema, code path, audit event, and test/conformance verifier. |
| Deterministic loop | The local event -> candidate -> review -> active -> retrieval -> prompt envelope path passes without provider calls. |
| Lifecycle safety | Deleted, distrusted, expired, superseded, quarantined, denied, or cross-scope memory cannot reach prompt, graph, summary, export, or derived surfaces. |
| Policy and capability | Local actors can perform only actions allowed by policy and capability grants; denied actions are auditable. |
| Prompt boundary | Prompt envelopes contain selected, filtered, budgeted content only, with provenance and reasons; they never include the full graph. |
| Portability | Import/export preserves ids, provenance, tombstones, trust state, review history, policy metadata, lifecycle state, evidence chains, and derived invalidations. |
| Recovery | Migration, backup, restore, rollback, partial writes, interrupted import/export, and corrupted-store checks have deterministic failure or recovery behavior. |
| Threat model | Prompt injection through imported memory, malicious bundles, distrusted evidence, private-lane leaks, and audit tampering have explicit mitigations and tests where practical. |
| Resource budget | Large histories have bounded selection, prompt size, export size, and local latency/resource fixtures. |

## Phase 0: Scope Freeze And Public Contract

Goal: make the repository understandable as a kernel before adding or expanding
features.

Files:

- `README.md`
- `SPEC.md`
- `docs/kernel-charter.md`
- `docs/backlog-cutover.md`
- `docs/core-status-audit.md`
- `docs/implementation-plan.md`

Tasks:

1. Keep one public promise: local-first, auditable agent memory.
2. Classify all work as `core`, `extension`, or `later-hosted`.
3. Remove runtime, hosted, domain, UI, provider, and notification work from v1
   completion criteria.
4. Keep personal/professional as starter templates, not the data model.
5. Keep Memory Tree as an optional renderer over selected memory, not the
   ontology.
6. Add a glossary that explains terms in public, non-insider language.

Done when:

- a contributor can tell what belongs in v1 core;
- examples and adapters cannot accidentally become architecture;
- the status audit identifies only true kernel blockers.

Verification:

```bash
rg -n "core|extension|later-hosted|Memory Tree|prompt envelope|scope|namespace" README.md SPEC.md docs
```

## Phase 1: Kernel Law, Data Model, And Threat Model

Goal: lock the normative memory contract before expanding surfaces.

Files:

- `docs/amk-000-kernel-invariants.md`
- `docs/memory-contract.md`
- `docs/memory-lifecycle-contract.md`
- `docs/security-identity-contract.md`
- `src/agent_memory_kernel/schema.sql`
- `src/agent_memory_kernel/contract.py`
- `src/agent_memory_kernel/store.py`
- `tests/test_memory_store.py`
- `tests/test_contract_acceptance.py`

Tasks:

1. Define the versioned schema for source events, turns, candidates, active
   memories, evidence, graph records, policies, capability grants, lifecycle
   mutations, tombstones, reviews, audit records, and derived invalidations.
2. Define lifecycle state transitions and blocked transitions.
3. Define policy inheritance for graph, summary, export, prompt, and review
   surfaces.
4. Add the threat model: prompt injection through imports, malicious bundles,
   distrusted evidence, private-lane leaks, stale evidence revival, partial
   writes, corrupted stores, and audit tampering.
5. Define stable local API/versioning rules: contract version, schema version,
   bundle version, conformance version, and compatibility status.

Done when:

- the docs and machine-readable contract describe the same kernel law;
- lifecycle and policy behavior is not left to adapter interpretation;
- breaking changes require a version bump plus migration/conformance evidence.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_memory_store tests.test_contract_acceptance
```

## Phase 2: Executable Invariant Harness

Goal: make the safety laws executable before declaring features complete.

Files:

- `src/agent_memory_kernel/conformance.py`
- `src/agent_memory_kernel/acceptance.py`
- `src/agent_memory_kernel/evals.py`
- `tests/test_contract_acceptance.py`
- `tests/test_memory_store.py`

Tasks:

1. Build an invariant map: invariant -> schema/table -> store path -> read path
   -> audit event -> unit test -> conformance scenario.
2. Keep golden traces for deletion, distrust, correction, rollback, expiration,
   supersession, quarantine, lane/scope/namespace isolation, deterministic
   ranking, prompt budget trimming, export/import, and no-full-graph prompts.
3. Add negative fixtures for poisoned imports, malicious bundles, distrusted
   evidence, denied scopes, and stale retained evidence.
4. Add adapter budget fixtures and local latency/resource measurements for
   large histories.
5. Keep failure messages readable enough for adapter authors.

Done when:

- every AMK-000 invariant has an executable verifier;
- conformance can run locally with no private data and no live provider;
- a failed invariant names the memory id, source id, policy decision, and
  blocked surface where possible.

Verification:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance seed --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance run --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m unittest tests.test_contract_acceptance tests.test_memory_store
```

## Phase 3: Minimal Local Reference Loop

Goal: prove the memory loop end to end with SQLite and deterministic logic.

Files:

- `src/agent_memory_kernel/store.py`
- `src/agent_memory_kernel/orchestrator.py`
- `src/agent_memory_kernel/worker.py`
- `src/agent_memory_kernel/cli.py`
- `docs/runtime-contract.md`
- `docs/end-to-end-vertical-slice.md`
- `tests/test_orchestrator.py`
- `tests/test_worker.py`
- `tests/test_memory_store.py`

Tasks:

1. Persist saved turns and source events.
2. Let the Keeper propose candidate memories and graph commands without
   silently trusting assistant, tool, web, or imported claims.
3. Promote candidates only through review or explicit write policy.
4. Retrieve active memory through the Router with lifecycle, trust, sensitivity,
   scope, lane, namespace, conflict, and capability filters.
5. Build a prompt envelope containing selected memory content, provenance,
   reasons, warnings, and budget metadata.
6. Keep no-memory and failed-Keeper fallbacks explicit and auditable.
7. Persist prompt snapshots that show exactly what was injected.

Done when:

- the deterministic vertical slice passes;
- the main model receives selected memory, not tags and not the full graph;
- corrected, deleted, distrusted, expired, superseded, quarantined, and denied
  memory stays out of prompt-facing retrieval.

Verification:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice seed --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice run --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice assert --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m unittest tests.test_orchestrator tests.test_worker tests.test_memory_store
```

## Phase 4: Governance, Lifecycle, Policy, And Explainability

Goal: make memory inspectable, correctable, permissioned, and auditable.

Files:

- `src/agent_memory_kernel/store.py`
- `src/agent_memory_kernel/policy.py`
- `src/agent_memory_kernel/cli.py`
- `docs/review-workflow.md`
- `docs/security-identity-contract.md`
- `tests/test_review_inbox.py`
- `tests/test_memory_store.py`
- `tests/test_operational_failure.py`

Tasks:

1. Keep approve, reject, correct, delete, distrust, expire, supersede,
   quarantine, and rollback available through stable local APIs.
2. Enforce local actor/capability grants for read, write, inject, export, and
   lifecycle actions.
3. Add or strengthen policy dry-run output for allowed and denied operations.
4. Add or strengthen human-readable diffs for memory changes.
5. Keep "why this memory exists" and "why this memory was shown" available:
   source evidence, reviewer, scope/lane/namespace, policy decision, trust
   state, lifecycle history, retrieval history, and prompt snapshot.
6. Ensure derived graph, summary, export, prompt, and style surfaces inherit
   lifecycle restrictions.

Done when:

- a reviewer can inspect evidence before promotion;
- denied actions are auditable and do not mutate state;
- lifecycle changes are reflected in all prompt-facing and export-facing
  surfaces;
- rollback is possible only where policy permits it.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_review_inbox tests.test_memory_store tests.test_operational_failure
```

## Phase 5: Durability, Migration, Recovery, And Portability

Goal: make memory durable and portable without reviving unsafe state.

Files:

- `src/agent_memory_kernel/store.py`
- `src/agent_memory_kernel/cli.py`
- `docs/recovery.md`
- `docs/memory-contract.md`
- `docs/memory-lifecycle-contract.md`
- `tests/test_backup_migration.py`
- `tests/test_memory_store.py`

Tasks:

1. Keep schema migration status, migration changelog, backup, restore, and
   restore-drill behavior versioned and testable.
2. Add failed-migration, partial-write, interrupted import/export, corrupted
   SQLite, and stale backup recovery fixtures where practical.
3. Define the `.amk` bundle manifest with schema, contract, lifecycle, policy,
   conformance, checksum, and redaction metadata.
4. Preserve ids, provenance, graph/evidence chains, trust state, review history,
   policy metadata, tombstones, lifecycle state, and derived invalidations.
5. Keep redacted bundles from restoring hidden content.
6. Keep deleted, distrusted, expired, superseded, quarantined, and denied memory
   inactive after import.

Done when:

- a bundle can move between local stores without changing lifecycle semantics;
- adversarial imports cannot reactivate unsafe memory;
- recovery checks fail closed with readable operator output.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_backup_migration tests.test_memory_store tests.test_contract_acceptance
```

## Phase 6: Stable Public Surface And Adapter Contract

Goal: let outside runtimes use the kernel without copying internals.

Files:

- `src/agent_memory_kernel/contract.py`
- `src/agent_memory_kernel/cli.py`
- `src/agent_memory_kernel/server.py`
- `src/agent_memory_kernel/mcp_server.py`
- `docs/runtime-contract.md`
- `docs/cross-model-context-contract.md`
- `docs/mcp.md`
- `tests/test_contract_acceptance.py`
- `tests/test_mcp_server.py`
- `tests/test_http_auth.py`

Tasks:

1. Freeze the stable local library and CLI surface for init, record, review,
   retrieve, explain, lifecycle, import, export, conformance, and health/status
   checks.
2. Expose version and compatibility status: schema version, contract version,
   conformance version, bundle version, lifecycle/policy versions, and migration
   status.
3. Document adapter capability levels: read-only, write-capable,
   lifecycle-capable, graph-capable, export-capable, and prompt-injection
   capable.
4. Treat HTTP/MCP as optional adapters over the same contract, not separate
   truth paths.
5. Define prompt formatter boundaries so provider adapters cannot place memory
   in a higher-priority unsafe surface.
6. Keep adapter certification local and reproducible.

Done when:

- a new adapter can run conformance without private project assumptions;
- local API/CLI versioning is visible and testable;
- optional HTTP/MCP surfaces cannot bypass policy checks;
- adapter failures do not break the kernel.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_contract_acceptance tests.test_mcp_server tests.test_http_auth
```

## Phase 7: Public V1 Polish And Universal Demo

Goal: make the repository shareable without making examples part of the core.

Files:

- `README.md`
- `CONTRIBUTING.md`
- `templates/vault/README.md`
- `examples/reference-loop-demo/README.md`
- `examples/personal-professional-demo/README.md`
- `examples/agent-loop-demo/README.md`
- `docs/roadmap.md`
- `docs/hosted-roadmap.md`

Tasks:

1. Keep one canonical universal demo: local conversation memory with correction,
   deletion, distrust, retrieval, prompt envelope, and export/import.
2. Keep personal/professional templates as optional starter packs over generic
   policy primitives.
3. Keep all runtime/domain examples thin and explicitly optional.
4. Publish a release checklist: conformance, migrations, recovery, prompt
   snapshots, export/import, latency/resource fixture, and docs links.
5. Keep out-of-core roadmap items out of v1 completion criteria.

Done when:

- a public user can install, run the demo, inspect memory, correct it, retrieve
  it, export/import it, and run conformance locally;
- examples can be deleted without changing the kernel contract;
- extension docs point back to the charter, AMK-000, and conformance suite.

Verification:

```bash
rg -n "optional|example|extension|kernel contract|AMK-000|conformance" README.md docs examples templates
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Phase 8: Extensions After V1

Goal: add power without making the kernel heavier.

Allowed extension tracks:

- HTTP/MCP services and richer local UI.
- Runtime adapters for chat apps, coding agents, Hermes, or other systems.
- Domain packs for personal/professional workflows, SEO, research, support,
  CRM, QA, or outcome loops.
- Markdown vault import/export bridges.
- Optional embeddings, ANN indexes, provider rerankers, and live provider
  certification.
- Notification senders, managed schedulers, hosted sync, hosted teams, hosted
  dashboards, billing operations, and cloud custody.

Rules:

1. Extensions must consume the kernel contract.
2. Extensions must run after policy filtering, not before it.
3. Extensions must not become required for deterministic v1 conformance.
4. Extensions must not weaken memory-safety invariants.
5. Hosted features stay in [hosted-roadmap.md](hosted-roadmap.md).

Verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
