# Implementation Plan

This is the v1 implementation plan for Agent Memory Kernel.

Agent Memory Kernel is a universal, local-first, auditable memory kernel. It is
not a Hermes rollout, not an SEO workflow, not a hosted SaaS, and not an agent
runtime. Adapters, domain packs, UIs, hosted services, provider integrations,
embeddings, MCP/HTTP surfaces, dashboards, and demos may exist, but they must
consume the kernel contract instead of defining it.

The plan is gate-driven. V1 is not complete because a feature exists; it is
complete only when the local kernel proves the required memory behavior through
deterministic tests, golden traces, and conformance scenarios.

## Governing Documents

The normative project boundary is defined by:

- [what-is-amk.md](what-is-amk.md)
- [../SPEC.md](../SPEC.md)
- [kernel-charter.md](kernel-charter.md)
- [amk-000-kernel-invariants.md](amk-000-kernel-invariants.md)
- [backlog-cutover.md](backlog-cutover.md)
- [adapter-contract.md](adapter-contract.md)
- [threat-model.md](threat-model.md)
- [invariant-verifier-map.md](invariant-verifier-map.md)
- [core-status-audit.md](core-status-audit.md)

If those documents disagree, the kernel charter, AMK-000 invariants, and the
machine-readable contract are the source of truth.

## Artifact Classes

Every file, API, command, example, and roadmap item should be labeled mentally
as one of these artifact classes before it becomes release work.

| Class | Meaning | V1 release blocker |
| --- | --- | --- |
| `core spec` | Required kernel behavior and public semantics. | Yes |
| `reference implementation` | Local SQLite implementation of the core spec. | Yes, when it proves core behavior |
| `conformance fixture` | Golden traces, tests, and fixtures that prove the spec. | Yes |
| `extension example` | Adapters, UIs, domain packs, provider hooks, hosted paths, and demos. | No |

This boundary prevents extension work from becoming core through documentation
gravity. HTTP/MCP, browser UI, notifications, billing, Digital Brain UX,
embeddings, Hermes, SEO packs, hosted mode, provider formatters, and demos are
extension examples unless they are used only as thin conformance consumers.

## V1 Core Manifest

V1 core includes only behavior required to own local memory truth safely.

| Area | Artifact class | Required v1 behavior |
| --- | --- | --- |
| Local store | `reference implementation` | SQLite source of truth, migrations, transactions, status. |
| Source events and saved turns | `core spec` + `reference implementation` | Append observed evidence and saved exchanges before memory extraction. |
| Candidate memory | `core spec` + `reference implementation` | Proposed memory remains reviewable, quarantined, or policy-promoted. |
| Active memory | `core spec` + `reference implementation` | Reviewed or policy-approved memory can be retrieved and later corrected, distrusted, deleted, expired, superseded, or rolled back. |
| Scope, lane, namespace | `core spec` | Generic isolation primitive for reads, writes, prompt injection, export, lifecycle, and graph surfaces. |
| Default packs | `extension example` + `conformance fixture` | Personal/professional are starter fixtures proving the generic isolation model, not the ontology. |
| Graph and evidence | `core spec` + `reference implementation` | Nodes, edges, evidence links, and derivations cannot bypass lifecycle or policy. |
| Keeper contract | `core spec` | Post-turn writer proposes candidates and graph commands; it does not silently trust unsafe claims. |
| Router contract | `core spec` | Pre-call reader selects allowed, relevant, budgeted memory; the main agent never scans the full graph. |
| Prompt envelope | `core spec` | Provider-neutral selected-memory payload with provenance, reasons, warnings, and budget metadata. |
| Review lifecycle | `core spec` + `reference implementation` | Approve, reject, correct, delete, distrust, expire, supersede, quarantine, and rollback are auditable and policy-gated. |
| Policy and capabilities | `core spec` | Read, write, inject, export, lifecycle, and redaction decisions fail closed and explain denials. |
| Explainability | `core spec` | Explain why memory exists, why it was rejected, why it was retrieved, why it was omitted, and why it was denied. |
| Import/export | `core spec` + `reference implementation` | Preserve provenance, lifecycle, tombstones, review history, review queues, trust state, policy metadata, evidence chains, and derived invalidations. |
| Versioning and recovery | `core spec` + `reference implementation` | Version schema/contract/bundles, handle migrations, backups, corrupted stores, interrupted writes, and cross-version imports. |
| Conformance | `conformance fixture` | Provider-free golden traces prove the full loop and safety invariants. |

## V1 Acceptance Loop

V1 is complete when a fresh local store can prove this loop without a live
model provider, hosted service, private runtime, domain project, or extension
adapter:

```text
source event
-> candidate memory
-> review or policy decision
-> active memory
-> graph/evidence model
-> Router-selected context
-> provider-neutral prompt envelope
-> saved turn
-> Keeper proposal for the next memory update
```

Required proof:

- every transition is auditable;
- every selected memory item has provenance and a selection reason;
- the main agent receives selected memory, not tags only and not the full graph;
- denied, inactive, unsafe, cross-scope, or stale memory fails closed;
- import/export preserves memory state without reviving unsafe content.

## Non-Negotiable Invariants

These are the release laws for v1:

1. The main agent never scans raw memory or the full graph.
2. Router output is selected, policy-filtered, budgeted, and explainable.
3. Keeper writes are reviewable by default unless explicit policy allows
   promotion.
4. Scope, lane, namespace, personal, and private boundaries hold across
   storage, retrieval, prompt, graph, summary, export, import, and audit.
5. Every active memory can answer: why remembered, from what evidence, under
   what policy, where it may appear, and how to revoke it.
6. Deleted, distrusted, expired, superseded, quarantined, rejected, pending, or
   denied memory cannot reappear through retained evidence or derived surfaces.
7. Prompt envelopes are provider-neutral and do not depend on renderer,
   provider, adapter, or domain semantics.
8. Import/export is atomic, versioned, provenance-preserving, and fail-closed
   under partial, hostile, redacted, corrupted, or cross-version inputs.
9. Deterministic local retrieval works without embeddings or provider rerankers.
10. V1 claims are backed by conformance fixtures, not prose.

## Core Gates

Each gate must have docs, code paths, unit tests, and conformance evidence where
applicable. A gate can use existing implementation, but it is not closed until
the proof is explicit.

### Gate 0: Normative Boundary

Goal: make the repository read as a kernel before any more feature work.

Tasks:

1. Keep `core spec`, `reference implementation`, `conformance fixture`, and
   `extension example` labels consistent in docs and roadmap language.
2. Keep Hermes, SEO, hosted, UI, MCP/HTTP deployment, provider, billing,
   notification, embedding, and dashboard work out of v1 completion criteria.
3. Keep personal/professional as starter fixtures over generic lane policy.
4. Keep Memory Tree and Digital Brain language as optional renderers over
   selected memory, not the kernel ontology.
5. Keep glossary language plain enough for a new contributor to explain
   `scope`, `lane`, `namespace`, `candidate`, `active memory`, `evidence`,
   `Router`, `Keeper`, and `prompt envelope`.

Done when:

- a contributor can tell what is core and what is extension;
- extension examples can be deleted without changing the kernel contract;
- [core-status-audit.md](core-status-audit.md) lists only true kernel blockers.

Verification:

```bash
rg -n "Hermes|SEO|hosted|billing|notification|Digital Brain|embedding|MCP|HTTP" README.md SPEC.md docs
rg -n "core spec|reference implementation|conformance fixture|extension example|core|extension|later-hosted" README.md SPEC.md docs
```

### Gate 1: Core Loop Golden Trace

Goal: prove the smallest complete memory loop end to end.

Tasks:

1. Seed a source event and saved turn.
2. Produce a candidate memory with provenance.
3. Promote it through review or explicit write policy.
4. Link it to graph/evidence.
5. Select it through Router retrieval.
6. Build a provider-neutral prompt envelope.
7. Save the next turn.
8. Produce a Keeper proposal for the next update.
9. Record audit entries for each transition.

Done when:

- the full loop passes from an empty local SQLite store;
- the loop requires no provider, runtime adapter, hosted service, or domain data;
- failures name the memory id, source id, policy decision, and failed surface.

Verification:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice seed --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice run --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice assert --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance seed --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
```

### Gate 2: Lifecycle Propagation

Goal: ensure memory state changes affect every derived and prompt-facing
surface.

Tasks:

1. Prove correction updates active retrieval, graph summaries, compact memory,
   prompt envelopes, exports, and derived invalidation records.
2. Prove rollback restores the prior state and invalidates stale derived data.
3. Prove delete, distrust, expire, supersede, quarantine, reject, and pending
   states stay out of retrieval, graph, summary, export, and prompt surfaces.
4. Prove retained source evidence cannot reactivate inactive memory.
5. Prove lifecycle tombstones survive export/import without becoming active.

Done when:

- every lifecycle mutation has a cross-surface verifier;
- derived invalidation records explain what was refreshed or hidden;
- inactive memory remains auditable but not prompt-facing.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_memory_store tests.test_contract_acceptance
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
```

### Gate 3: Scope, Lane, And Namespace Isolation

Goal: prove access boundaries with adversarial fixtures, not prose.

Tasks:

1. Test personal/professional as starter fixtures over the generic policy
   model.
2. Add namespace-specific fixtures for projects, agents, imports, and bundles.
3. Prove denied memory is absent from prompts, tree packs, graph browser data,
   summaries, semantic analyses, exports, and API responses.
4. Prove cross-lane or cross-namespace access requires explicit policy and is
   visible in prompt metadata and audit.
5. Preserve denied policy paths across export/import.

Done when:

- no prompt, graph, summary, export, or audit surface leaks cross-boundary
  content by default;
- personal/professional proves isolation without becoming the only ontology;
- denied access is explainable and non-mutating.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_memory_store tests.test_contract_acceptance tests.test_http_auth
```

### Gate 4: Trust And Explainability

Goal: make every memory decision inspectable.

Tasks:

1. Expose why a memory exists: source event, candidate, reviewer or policy
   decision, scope/lane/namespace, trust state, sensitivity, graph/evidence,
   lifecycle history, audit trail, and revocation handles.
2. Expose why a candidate was rejected or quarantined.
3. Expose why a memory was retrieved: Router run, score, selection reason,
   warning, prompt role, budget decision, and prompt snapshot.
4. Expose why memory was omitted or denied: policy match, lifecycle state,
   trust state, scope boundary, budget, conflict, or safety reason.
5. Keep explainability available through the stable local surface first; HTTP
   and MCP may mirror it only as extension adapters.

Done when:

- a reviewer can inspect evidence before promotion;
- an operator can explain any read, write, denial, lifecycle change, and prompt
  injection;
- denied actions are auditable and do not mutate memory state.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_review_inbox tests.test_memory_store tests.test_operational_failure
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
```

### Gate 5: Router And Prompt Boundary

Goal: prove the main agent receives only selected, allowed, budgeted memory.

Tasks:

1. Add tests that fail if prompt construction bypasses Router selection.
2. Prove prompt envelopes never include the full graph, raw event stream, or
   unauthorized memory.
3. Keep selected content richer than tags: branch labels, active memory text,
   provenance, reasons, warnings, and budget metadata.
4. Lock deterministic ranking under fixed inputs.
5. Add prompt budget, token-pressure, latency, and large-history fixtures.
6. Keep embeddings, ANN, and provider rerankers as optional post-policy
   enhancers, not required retrieval infrastructure.
7. Keep provider formatters from moving retrieved memory into unsafe
   high-priority system surfaces.

Done when:

- Router receives graph/store access, but the main model receives only the
  filtered envelope;
- large local histories remain bounded;
- retrieval works deterministically without live providers or embeddings.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_memory_store tests.test_embeddings_contract tests.test_contract_acceptance
```

### Gate 6: Keeper Safety

Goal: make the post-turn writer useful without silently trusting bad memory.

Tasks:

1. Keep assistant, tool, web, external document, and imported claims reviewable
   by default.
2. Quarantine secret-like and prompt-injection-like content.
3. Add fixtures for false positives, retries, dedupe, contradiction, deletion,
   policy denial, and partial Keeper failure.
4. Ensure Keeper graph commands are normalized, auditable, and linked to source
   evidence.
5. Ensure failed Keeper runs are visible and do not block no-memory fallback.

Done when:

- Keeper improves memory without bypassing review or policy;
- unsafe or unsupported claims do not become active facts silently;
- retry and dedupe behavior is deterministic.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_llm_keeper_contract tests.test_keeper_eval tests.test_worker tests.test_memory_store
```

### Gate 7: Portability, Recovery, And Versioning

Goal: make memory durable and movable without reviving unsafe state.

Tasks:

1. Preserve ids, provenance, graph/evidence chains, trust state, review
   history, pending/rejected review queues, policy metadata, tombstones,
   lifecycle state, and derived invalidations.
2. Keep redacted exports from restoring hidden content.
3. Keep pending, rejected, inactive, distrusted, deleted, expired, superseded,
   quarantined, denied, or unsafe memory inactive after import.
4. Add fixtures for partial bundles, hostile bundles, unknown adapters,
   interrupted export, interrupted non-bundle import, corrupted SQLite,
   cross-version bundles, stale backups, and oversized stores.
5. Keep schema, contract, bundle, lifecycle, policy, migration, and
   compatibility versions visible in status.
6. Add audit-chain checks for imported or subset histories.

Done when:

- profile or bundle movement does not change lifecycle semantics;
- adversarial imports fail closed;
- recovery checks produce readable operator output.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_backup_migration tests.test_memory_store tests.test_contract_acceptance
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
```

### Gate 8: Public Local Surface

Goal: let outside runtimes use the kernel without copying internals.

Tasks:

1. Freeze stable local Python and CLI surfaces for init, record, review,
   retrieve, explain, lifecycle, import, export, conformance, and status.
2. Expose schema, contract, conformance, bundle, lifecycle, policy, migration,
   and compatibility status.
3. Keep HTTP/MCP as optional mirrors over the same contract, not separate truth
   paths.
4. Keep adapter capability levels local and provider-free:
   `read-only`, `write-capable`, `lifecycle-capable`, `graph-capable`,
   `export-capable`, and `prompt-injection-capable`.
5. Keep adapter certification reproducible without private project data.

Done when:

- a new adapter can run conformance locally;
- optional HTTP/MCP/provider surfaces cannot bypass policy checks;
- local API/CLI versioning is visible and testable.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_contract_acceptance tests.test_mcp_server tests.test_http_auth
```

### Gate 9: Public V1 Package

Goal: make the repository shareable as a kernel.

Tasks:

1. Keep one canonical universal demo that proves the core loop with review,
   correction, deletion, distrust, retrieval, prompt envelope, and
   export/import.
2. Keep runtime/domain examples thin and explicitly optional.
3. Publish a release checklist: conformance, migrations, recovery, prompt
   snapshots, export/import, latency/resource fixture, and docs links.
4. Ensure examples can be removed without changing the kernel contract.
5. Keep hosted/platform/domain/provider items out of v1 completion criteria.

Done when:

- a public user can install, initialize, record, review, retrieve, explain,
  correct, delete, export/import, and run conformance locally;
- the README points to the core spec before optional extensions;
- every v1 claim is backed by a command or test.

Verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m agent_memory_kernel.cli contract assert
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance spec-assert
```

## Deferred Extensions

The following tracks are useful, but they are not v1 core blockers:

- Hermes, Codex, chat-agent, coding-agent, LangGraph, AutoGen, CrewAI, and
  OpenAI Agents SDK adapters.
- SEO, research, support, CRM, QA, outcome-loop, project, agent, and session
  packs beyond fixtures needed for isolation tests.
- HTTP/MCP deployment, remote MCP hosting, and richer local UI.
- Browser review UI, graph UI, dashboards, billing reports, notifications, and
  external sender bridges.
- Digital Brain and Memory Tree presentation beyond selected-memory renderers.
- Optional embeddings, ANN indexes, provider rerankers, and live provider
  certification.
- Provider-specific prompt formatters beyond boundary-preservation tests.
- Markdown vaults, document importers, task-tool bridges, and sync adapters.
- Hosted identity, tenancy, RBAC, teams, hosted dashboards, hosted registry,
  managed alerts, schedulers, KMS, cloud custody, and hosted collaboration.

Extension rules:

1. Extensions consume the kernel contract.
2. Extensions run after policy and lifecycle filtering.
3. Extensions are not required for deterministic v1 conformance.
4. Extensions cannot weaken AMK-000 invariants.
5. Hosted work stays in [hosted-roadmap.md](hosted-roadmap.md).

## Execution Order

Use this order for implementation. Do not add extension work until the matching
core gate is closed.

1. Freeze this implementation plan and keep [core-status-audit.md](core-status-audit.md)
   synchronized with gate status.
2. Add or update conformance scenarios for the full v1 loop before adding more
   feature code.
3. Close lifecycle propagation gaps.
4. Close scope/lane/namespace isolation gaps.
5. Add stable why-remembered, why-rejected, why-retrieved, why-omitted, and
   why-denied explainability surfaces.
6. Harden Router budget, deterministic ranking, prompt-envelope boundaries,
   and no-full-graph tests.
7. Harden Keeper false-positive, retry, dedupe, contradiction, deletion, and
   denial fixtures.
8. Harden import/export, recovery, corrupted-store, interrupted-write, and
   cross-version fixtures.
9. Freeze local API/CLI/status surfaces and adapter capability contract.
10. Run the public release checklist and only then polish extension examples.

## Release Checklist

V1 can be claimed only when these commands pass from a clean checkout:

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

Manual release review:

- README states the kernel promise before extension features.
- SPEC and machine-readable contract describe the same lifecycle and policy.
- Invariant verifier map has no unmapped v1 law.
- Core status audit has no `missing` or unresolved `partial` item for v1 gates.
- Extension docs cannot be mistaken for v1 requirements.
