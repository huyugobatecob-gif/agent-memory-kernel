# Implementation Plan

This is the v1 implementation plan for Agent Memory Kernel.

Agent Memory Kernel is a universal, local-first, auditable memory kernel. It is
not a Hermes rollout, not an SEO workflow, not a hosted product, and not an
agent runtime. Runtime adapters, domain packs, hosted services, MCP/HTTP
surfaces, dashboards, embeddings, and provider integrations can exist, but they
must consume the kernel contract instead of defining it.

The governing documents are [../SPEC.md](../SPEC.md),
[kernel-charter.md](kernel-charter.md),
[amk-000-kernel-invariants.md](amk-000-kernel-invariants.md),
[backlog-cutover.md](backlog-cutover.md), [threat-model.md](threat-model.md),
and [invariant-verifier-map.md](invariant-verifier-map.md). Current evidence is
tracked in [core-status-audit.md](core-status-audit.md).

## V1 Acceptance Test

V1 is complete when a fresh local store can prove this loop without a live model
provider, hosted service, private runtime, or domain-specific project data:

```text
source event
-> candidate memory
-> review or policy decision
-> active memory
-> graph/evidence model
-> Router-selected context pack
-> provider-neutral prompt envelope
-> saved turn
-> Keeper proposal for the next memory update
```

Every transition must be auditable. Every selected memory item must have
provenance and a selection reason. The main agent must never scan the full
graph; it receives only selected, policy-filtered, budgeted memory.

## Core Boundary

V1 core includes only behavior that changes memory truth, safety, lifecycle,
retrieval, prompt injection, portability, or conformance.

Core includes:

- SQLite local-first reference storage and migrations.
- Raw source events and saved turns.
- Candidate memories and active memories.
- Generic `scope`, `lane`, `namespace`, `actor`, `policy`, and `surface`
  primitives.
- The shipped personal/professional starter pack as a default policy pack, not
  as the only valid ontology.
- Graph nodes, graph edges, evidence links, and derivation links.
- Keeper proposal contract.
- Router retrieval contract.
- Provider-neutral prompt envelope and selected Memory Tree Supplement
  contract.
- Review lifecycle: approve, reject, correct, delete, distrust, expire,
  supersede, quarantine, and rollback.
- Read, write, export, inject, lifecycle, and redaction policies.
- Audit trails and explainability for why memory exists and why it was shown.
- Import/export with provenance, tombstones, trust state, review history,
  review queues, policy metadata, lifecycle state, evidence chains, and derived
  invalidations.
- Deterministic ranking without mandatory embeddings.
- Conformance scenarios, golden traces, and local resource budgets.

Not core for v1:

- Hermes rollout or any named runtime rollout.
- SEO loop traces or any domain pack as an architecture requirement.
- Hosted identity, tenancy, RBAC, team administration, hosted dashboards,
  hosted billing, hosted sync, or hosted collaboration.
- Remote MCP deployment, hosted API deployment, managed schedulers, managed
  alerts, live notification transports, KMS, or managed off-host backup.
- ANN/vector search as required infrastructure, live embedding provider
  certification, live provider prompt certification, or advanced graph
  compaction.
- Browser UI, rich graph UI, dashboards, billing reports, notification queues,
  markdown vault adapters, full agent turn runners, and domain demos as v1
  blockers.

Those items may remain under `adapters/`, `examples/`, `extensions/`, or a
later hosted roadmap. They must not be needed to understand, install, verify, or
use the local kernel.

## Public Model

The public project should answer four questions:

- What was stored?
- Who or what is allowed to read it?
- How can it be corrected, hidden, distrusted, exported, or deleted?
- Why did the agent receive this memory for this request?

Glossary:

- `source_event`: raw observed evidence such as a message, tool result, import,
  document excerpt, or maintenance event.
- `candidate_memory`: proposed durable memory awaiting review or policy
  promotion.
- `active_memory`: reviewed or policy-approved memory that can enter retrieval.
- `scope`: access boundary for read, write, inject, lifecycle, and export.
- `lane`: policy grouping inside or across scopes. `personal` and
  `professional` are starter lanes.
- `namespace`: stable owner or package boundary for projects, agents,
  workspaces, apps, or imports.
- `surface`: where memory can appear: prompt, export, graph browser, summary,
  API response, review queue, or audit report.
- `policy`: local rules that decide read, write, inject, export, lifecycle, and
  redaction behavior.
- `Keeper`: post-turn writer that proposes candidates and graph commands after
  a turn is saved.
- `Router`: pre-call reader that selects allowed, relevant, budgeted memory.
- `prompt envelope`: provider-neutral payload for the main model.
- `Memory Tree Supplement`: optional renderer over selected memory, not the
  source of truth.

## Gates

Work is complete only when the matching gate has evidence.

| Gate | Required proof |
| --- | --- |
| Boundary | The item is classified as `core`, `extension`, or `later-hosted`; non-core work is not a v1 blocker. |
| Kernel law | Schema, docs, and machine-readable contract describe the same primitives, lifecycle states, and policies. |
| Invariants | Each AMK-000 law maps to code paths, audit events, unit tests, and conformance scenarios. |
| Local loop | The source-event -> prompt-envelope -> Keeper-proposal loop runs locally with deterministic fallbacks. |
| Lifecycle safety | Deleted, distrusted, expired, superseded, quarantined, denied, or cross-scope memory cannot reach prompt, graph, summary, export, or derived surfaces. |
| Policy and capability | Local actors can perform only allowed actions; denied actions are auditable and non-mutating. |
| Prompt boundary | Prompt envelopes include selected, filtered, budgeted content only, never the full graph. |
| Portability | Import/export preserves ids, provenance, tombstones, trust state, review history, review queues, policy metadata, lifecycle state, evidence chains, and derived invalidations. |
| Recovery | Migration, backup, restore, rollback, interrupted import/export, corrupted-store, and partial-write behavior fail closed or recover deterministically. |
| Resource budget | Large stores have bounded retrieval, prompt size, export size, and local latency/resource fixtures. |

## Phase 0: Scope Reset

Goal: make the repository read as a kernel before adding more surface area.

Tasks:

1. Keep one public promise: local-first, auditable agent memory.
2. Maintain `core`, `extension`, and `later-hosted` labels in
   [backlog-cutover.md](backlog-cutover.md).
3. Keep Hermes, SEO, hosted, UI, MCP/HTTP deployment, provider, notifications,
   billing, and dashboard work out of v1 completion criteria.
4. Keep personal/professional as the default pack over generic lane policy.
5. Keep Memory Tree as a renderer over selected memory, not the ontology.
6. Keep glossary and "is / is not" language plain enough for a new GitHub
   reader.

Done when:

- a contributor can tell what belongs to v1 core;
- examples and adapters cannot accidentally become architecture;
- [core-status-audit.md](core-status-audit.md) lists only true kernel blockers.

Verification:

```bash
rg -n "core|extension|later-hosted|not core|not a hosted|not a Hermes|Memory Tree" README.md SPEC.md docs
```

## Phase 1: Kernel Schema And Laws

Goal: lock the normative data model and safety laws.

Tasks:

1. Version schema for source events, turns, candidates, active memories,
   evidence, graph nodes/edges, lanes, namespaces, policies, capability grants,
   reviews, tombstones, revisions, audit records, and derived invalidations.
2. Define allowed lifecycle transitions and blocked transitions.
3. Define policy inheritance across prompt, graph, summary, export, review, and
   derived surfaces.
4. Keep the threat model current for prompt injection, malicious imports,
   distrusted evidence, private-lane leaks, stale evidence revival, partial
   writes, corrupted stores, and audit tampering.
5. Keep schema, contract, bundle, conformance, lifecycle, and policy versions
   visible in the local status surface.

Done when:

- docs and `memory_contract()` describe the same kernel law;
- adapters cannot define their own lifecycle semantics;
- breaking changes require version and migration/conformance evidence.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_memory_store tests.test_contract_acceptance
```

## Phase 2: Executable Invariant Harness

Goal: make memory-safety laws executable before claiming completion.

Tasks:

1. Maintain invariant -> schema/table -> store path -> read path -> audit event
   -> unit test -> conformance scenario mapping.
2. Keep golden traces for deletion, distrust, correction, rollback,
   expiration, supersession, quarantine, lane/scope/namespace isolation,
   deterministic ranking, prompt budget trimming, export/import, recovery, and
   no-full-graph prompts.
3. Add negative fixtures for poisoned imports, malicious bundles, distrusted
   evidence, denied scopes, stale retained evidence, and policy bypass.
4. Keep conformance runnable with no private data and no live provider.
5. Make failures name the memory id, source id, policy decision, and blocked
   surface where possible.

Done when:

- every AMK-000 invariant has an executable verifier;
- a new adapter can run conformance locally and understand failures;
- the invariant map and machine-readable contract stay synchronized.

Verification:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance seed --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance run --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m unittest tests.test_contract_acceptance tests.test_memory_store
```

## Phase 3: Local Reference Loop

Goal: prove the baseline loop end to end with SQLite and deterministic logic.

Tasks:

1. Persist saved turns and raw source events before Keeper extraction.
2. Let Keeper propose candidates and graph commands without silently trusting
   assistant, tool, web, external document, or imported claims.
3. Promote candidates only through review or explicit write policy.
4. Let Router retrieve active memory through lifecycle, trust, sensitivity,
   scope, lane, namespace, conflict, capability, and budget filters.
5. Build prompt envelopes containing selected content, provenance, reasons,
   warnings, and budget metadata.
6. Keep no-memory, failed-Keeper, and failed-Router fallbacks explicit and
   auditable.
7. Persist prompt snapshots that show exactly what was injected.

Done when:

- the deterministic vertical slice passes;
- the main model receives selected memory, not tags and not the full graph;
- inactive, unsafe, denied, or cross-scope memory stays out of prompt-facing
  retrieval.

Verification:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice seed --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice run --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice assert --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m unittest tests.test_orchestrator tests.test_worker tests.test_memory_store
```

## Phase 4: Review And Explainability

Goal: make memory inspectable, correctable, permissioned, and auditable.

Tasks:

1. Keep approve, reject, correct, delete, distrust, expire, supersede,
   quarantine, and rollback available through stable local APIs.
2. Enforce local actor/capability grants for read, write, inject, export, and
   lifecycle actions.
3. Add or strengthen policy dry-run output for allowed and denied operations.
4. Add or strengthen human-readable diffs for memory changes.
5. Expose "why this memory exists": source evidence, reviewer, scope, lane,
   namespace, policy decision, trust state, lifecycle history, and audit trail.
6. Expose "why this memory was shown": Router run, score, selection reason,
   prompt role, budget decision, warning, and prompt snapshot.
7. Ensure derived graph, summary, export, prompt, and style surfaces inherit
   lifecycle restrictions.

Done when:

- a reviewer can inspect evidence before promotion;
- denied actions are auditable and do not mutate state;
- lifecycle changes are reflected in all prompt-facing and export-facing
  surfaces.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_review_inbox tests.test_memory_store tests.test_operational_failure
```

## Phase 5: Durability, Recovery, And Portability

Goal: make memory durable and movable without reviving unsafe state.

Tasks:

1. Keep schema migration status, migration changelog, backup, restore, and
   restore-drill behavior versioned and testable.
2. Add fixtures for failed migrations, partial writes, interrupted exports,
   interrupted imports, corrupted SQLite, stale backups, and oversized stores.
3. Define portable `.amk` bundle semantics with schema, contract, lifecycle,
   policy, conformance, checksum, and redaction metadata.
4. Preserve ids, provenance, graph/evidence chains, trust state, review
   history, pending/rejected review queues, policy metadata, tombstones,
   lifecycle state, and derived invalidations.
5. Keep redacted bundles from restoring hidden content.
6. Keep deleted, distrusted, expired, superseded, quarantined, rejected, pending,
   and denied memory inactive after import unless a later explicit review or
   policy action changes it.
7. Add cross-version import/export fixtures before declaring public stability.

Done when:

- a profile or bundle can move between local stores without changing lifecycle
  semantics;
- adversarial imports cannot activate unsafe or inactive memory;
- recovery checks fail closed with readable operator output.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_backup_migration tests.test_memory_store tests.test_contract_acceptance
```

## Phase 6: Public Surface And Adapter Contract

Goal: let outside runtimes use the kernel without copying internals.

Tasks:

1. Freeze the stable local Python and CLI surface for init, record, review,
   retrieve, explain, lifecycle, import, export, conformance, and status.
2. Expose schema, contract, conformance, bundle, lifecycle, policy, and
   migration compatibility status.
3. Document adapter capability levels: read-only, write-capable,
   lifecycle-capable, graph-capable, export-capable, and prompt-injection
   capable.
4. Treat HTTP/MCP as optional adapters over the same contract, not separate
   truth paths.
5. Keep provider prompt formatters and embeddings as optional extension checks
   after policy filtering.
6. Keep adapter certification local and reproducible.

Done when:

- a new adapter can run conformance without private project assumptions;
- local API/CLI versioning is visible and testable;
- optional HTTP/MCP/provider surfaces cannot bypass policy checks.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_contract_acceptance tests.test_mcp_server tests.test_http_auth
```

## Phase 7: Public V1 Package And Universal Demo

Goal: make the repository shareable without making examples part of the core.

Tasks:

1. Keep one canonical universal demo: local conversation memory with review,
   correction, deletion, distrust, retrieval, prompt envelope, and export/import.
2. Keep personal/professional templates as default starter packs over generic
   policy primitives.
3. Keep all runtime/domain examples thin and explicitly optional.
4. Publish a release checklist: conformance, migrations, recovery, prompt
   snapshots, export/import, latency/resource fixture, and docs links.
5. Keep hosted/platform/domain/provider items out of v1 completion criteria.

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

## Phase 8: Optional Enhancements After V1

Goal: add power without making the kernel heavier.

Allowed extension tracks:

- Runtime adapters for chat apps, coding agents, Hermes, LangGraph, AutoGen,
  CrewAI, OpenAI Agents SDK, Claude/Codex-style workflows, and CLI scripts.
- Domain packs for SEO, research, support, CRM, QA, and outcome loops.
- Notes/document/vault importer-exporter bridges.
- HTTP/MCP services and richer local UI.
- Optional embeddings, ANN indexes, provider rerankers, and live provider
  certification.
- Notification senders, managed schedulers, hosted sync, hosted teams, hosted
  dashboards, billing operations, and cloud custody.

Rules:

1. Extensions consume the kernel contract.
2. Extensions run after policy filtering, not before it.
3. Extensions are not required for deterministic v1 conformance.
4. Extensions cannot weaken AMK-000 memory-safety invariants.
5. Hosted work stays in [hosted-roadmap.md](hosted-roadmap.md).

Verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
