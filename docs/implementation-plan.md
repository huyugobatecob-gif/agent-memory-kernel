# Implementation Plan

This is the working plan for turning Agent Memory Kernel into a stable,
reusable local-first memory kernel.

The governing documents are [../SPEC.md](../SPEC.md),
[kernel-charter.md](kernel-charter.md),
[amk-000-kernel-invariants.md](amk-000-kernel-invariants.md), and
[backlog-cutover.md](backlog-cutover.md). Backlog items must be classified as
`core`, `extension`, or `later-hosted` before they are treated as core work.
Current implementation state is tracked in [core-status-audit.md](core-status-audit.md).

## Outcome

Agent Memory Kernel should provide a local-first, auditable memory kernel that
any agent runtime, IDE, chat app, automation, or human workflow can use without
depending on one product, model provider, hosted service, or domain.

The kernel is a local causal record of what was observed, proposed, believed,
revised, hidden, expired, exported, and injected.

The core loop is:

```text
after_saved_turn
-> store source event
-> Keeper proposes candidate memory
-> review or policy promotes/rejects
-> before_model_call
-> Router retrieves policy-filtered active memory
-> prompt envelope receives selected memory content
```

Memory Tree is a default renderer over the read contract. It is not the kernel
ontology and must not bypass policy filters.

## Scope Model

### Core

Core work changes the local memory contract itself:

- source events, turns, and provenance;
- candidate memories and active memories;
- generic `scope`, `lane`, `namespace`, `actor`, `policy`, and `surface`
  primitives;
- graph nodes, graph edges, evidence, and derivation;
- lifecycle state machine for review, correction, delete, distrust, expire,
  supersede, quarantine, and rollback;
- Keeper proposal contract;
- Router retrieval contract;
- provider-neutral prompt envelope;
- read, write, inject, export, and lifecycle policies;
- deterministic baseline retrieval without mandatory embeddings;
- import/export with provenance, tombstones, policy metadata, and evidence;
- local identity and capability grants;
- schema, migration, transaction, recovery, and performance contracts;
- audit, explainability, conformance, and golden traces.

### Extension

Extension work is optional and must consume the core contract:

- runtime adapters;
- provider prompt formatters;
- importer/exporter bridges;
- default personal/professional templates;
- domain packs such as outcome loops, SEO, research, support, CRM, or QA;
- Memory Tree and other prompt renderers over the prompt envelope contract;
- optional embeddings, ANN indexes, and provider-backed rerankers;
- richer local review UI and graph exploration;
- notification sender bridges.

### Later Hosted

Hosted work is not required for local full-memory completion:

- hosted multi-user API/UI;
- hosted tenancy, RBAC, organization administration, and team dashboards;
- billing dashboards and provider invoice operations;
- remote MCP hosting;
- managed alerts and schedulers;
- KMS/off-host backup custody;
- hosted adapter registry and badge publishing;
- hosted sync and collaboration.

## Done When

The repository can claim full local memory when:

- the local reference loop passes deterministic tests;
- correction, deletion, distrust, expiration, supersession, quarantine, and
  rollback affect prompt-facing retrieval correctly;
- denied, private, cross-scope, quarantined, or untrusted memory cannot leak
  into prompts, graph previews, exports, summaries, or derived state;
- selected memory is returned with provenance, source ids, selection reasons,
  warnings, and truncation decisions;
- derived graph, prompt, export, style, and summary surfaces are invalidated
  when source memory changes;
- export/import preserves ids, provenance, policy state, review history,
  lifecycle state, evidence chains, and tombstones;
- schema, migration, transaction, recovery, and performance behavior is
  versioned and testable;
- local actors can perform only actions allowed by policy and capability grants;
- stable CLI/API contracts and adapter capability levels are documented;
- adapters can pass conformance without private project assumptions.

## Invariant Matrix

Every kernel law must be mapped to a code path and a verifier before the kernel
can claim completion.

| Invariant | Core paths | Required verifier |
| --- | --- | --- |
| Deleted memory cannot reappear from retained evidence | lifecycle mutation, search, tree/renderer output, context builder, graph/evidence export | unit test plus conformance golden trace |
| Distrusted sources cannot influence retrieval, summary, graph, export, or derived memory | distrust lifecycle, summaries, semantic analyses, graph/tree, export, prompt envelope | unit test plus conformance golden trace |
| Scope/lane/namespace boundaries cannot leak across prompt, graph, summary, browser, and export surfaces | read policy, scope filtering, graph/evidence, summaries, prompt envelope, export | unit test plus prompt-envelope snapshot |
| Correction/rollback/delete/distrust/expire/supersede invalidate derived memory | lifecycle engine, derived invalidation ledger, graph surfaces, summaries, exports | lifecycle report plus import/export round trip |
| Export/import preserves provenance, ids, tombstones, trust, review, policy, and evidence | profile import/export, bundle import/export, lifecycle/policy state, graph evidence chains | portable bundle plus graph evidence-chain/derived-invalidation round-trip tests and conformance trace |
| Prompt envelopes contain selected, filtered, budgeted content only | Router, context builder, prompt formatter, renderer | deterministic selected-content, budget-trim, and provider-boundary envelope snapshots |
| Local actors cannot bypass capability grants | read/write/export/inject/lifecycle policies, policy simulator | denied-action trace plus dry-run report |
| Retrieval is deterministic without live providers | lexical/rule ranking, current-best resolver, tie-breakers | ranking fixture and golden prompt snapshot |
| Local histories stay bounded and predictable | indexes, compaction/retention, retrieval/export paths | bounded-selection fixture plus latency/resource fixture |

This matrix is an implementation gate. A feature is not considered done when it
has a table or command; it is done when the relevant invariant has executable
proof.

## Phase 0: Scope, Terms, And Status Lock

Goal: make the project understandable as a kernel before adding more features.

Files:

- `SPEC.md`
- `docs/kernel-charter.md`
- `docs/amk-000-kernel-invariants.md`
- `docs/backlog-cutover.md`
- `docs/core-status-audit.md`
- `README.md`
- `docs/roadmap.md`

Tasks:

1. Define the one-sentence project promise.
2. Separate `core`, `extension`, and `later-hosted` backlog.
3. Move hosted, provider, runtime, and domain rollout language out of the core
   plan.
4. Define `scope`, `lane`, `namespace`, `actor`, `policy`, and `surface`.
5. Keep `personal` and `professional` as starter templates, not hardcoded
   architecture.
6. State that Memory Tree is a renderer over the prompt envelope, not the
   kernel ontology.
7. Keep a `done`, `partial`, `missing`, `extension`, and `later-hosted` audit
   so future work does not rebuild completed features.
8. Add a plain-language model: collect, extract, review, store, retrieve,
   explain, correct.

Done when:

- new contributors can tell what belongs in the kernel;
- hosted and domain-specific items are not listed as local v1 blockers;
- personal/professional examples do not define the core data model;
- docs link to the spec, charter, AMK-000, backlog cutover, and status audit.

Verification:

```bash
rg -n "AMK-000|scope|namespace|policy|surface|later-hosted|extension" README.md docs SPEC.md
```

## Phase 1: AMK-000, Schema, And Kernel Laws

Goal: make memory safety invariants enforceable instead of aspirational.

Files:

- `src/agent_memory_kernel/schema.sql`
- `src/agent_memory_kernel/store.py`
- `src/agent_memory_kernel/contract.py`
- `docs/amk-000-kernel-invariants.md`
- `docs/memory-contract.md`
- `docs/memory-lifecycle-contract.md`
- `docs/security-identity-contract.md`
- `tests/test_memory_store.py`
- `tests/test_contract_acceptance.py`

Tasks:

1. Version schemas for source events, candidates, active memories, graph nodes,
   graph edges, evidence, scopes, lanes, namespaces, actors, policies, review
   actions, mutations, tombstones, and audit records.
2. Define the lifecycle state machine for candidate, active, corrected,
   deleted, distrusted, expired, superseded, quarantined, and rolled-back
   memory.
3. Keep migration, transaction, locking, concurrency, corruption detection,
   backup, restore, and recovery behavior explicit and testable.
4. Add or strengthen invariant tests:
   - deleted memory cannot reappear from retained evidence;
   - distrusted sources cannot influence retrieval, summaries, graph, export,
     or derived memory;
   - denied scopes, lanes, namespaces, and private content cannot leak into
     prompts;
   - derived memory invalidates on correction, deletion, distrust, expiration,
     rollback, or supersession;
   - exports preserve provenance, trust state, policy metadata, review history,
     evidence chains, and tombstones.
5. Keep deterministic behavior as the default path.

Done when:

- invariant tests prove the safety rules;
- the machine-readable contract describes the same laws as the docs;
- migrations and restore checks report schema compatibility.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_memory_store tests.test_contract_acceptance
```

## Phase 2: Local Reference Kernel Loop

Goal: prove the full memory loop locally before broad adapter work.

Files:

- `src/agent_memory_kernel/orchestrator.py`
- `src/agent_memory_kernel/store.py`
- `src/agent_memory_kernel/cli.py`
- `docs/runtime-contract.md`
- `docs/end-to-end-vertical-slice.md`
- `tests/test_orchestrator.py`
- `tests/test_memory_store.py`

Tasks:

1. Keep `after_saved_turn` responsible for raw exchange persistence.
2. Keep Keeper writes reviewable by default.
3. Keep `before_model_call` responsible for policy-filtered retrieval.
4. Ensure the prompt envelope contains selected content, not tags only.
5. Ensure the main model never receives the full graph.
6. Keep no-memory fallback explicit when retrieval fails or policy denies access.
7. Define deterministic ranking inputs, filters, score components, and stable
   tie-breakers.
8. Persist prompt snapshots that prove what was injected and why.

Done when:

- `slice seed/run/assert` passes;
- a corrected memory replaces the old one;
- deleted, distrusted, expired, superseded, quarantined, and denied memory is
  absent from the prompt;
- scope isolation is visible in prompt metadata;
- Keeper and Router runs are auditable by ID.

Verification:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice seed --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice run --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice assert --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m unittest tests.test_orchestrator tests.test_memory_store
```

## Phase 3: API, Review, Policy Simulation, And Explainability

Goal: make memory inspectable, correctable, and permissioned.

Files:

- `src/agent_memory_kernel/store.py`
- `src/agent_memory_kernel/cli.py`
- `src/agent_memory_kernel/server.py`
- `src/agent_memory_kernel/mcp_server.py`
- `docs/review-workflow.md`
- `docs/security-identity-contract.md`
- `tests/test_review_inbox.py`
- `tests/test_server_ui.py`
- `tests/test_mcp_server.py`

Tasks:

1. Freeze the stable local CLI/API surface for init, record, review, retrieve,
   explain, lifecycle, import, export, conformance, and health checks.
2. Keep approve, reject, correct, delete, distrust, expire, supersede,
   quarantine, and rollback available through CLI/API/MCP where appropriate.
3. Add policy dry-run/simulator output for read, write, inject, export, and
   lifecycle actions.
4. Add local actor/capability grants without hosted tenancy or RBAC consoles.
5. Add or strengthen human-readable memory diffs.
6. Add or strengthen "why this memory exists" and "why this memory was shown"
   views: source evidence, reviewer, scope/lane/namespace, policy decision,
   trust state, lifecycle history, and retrieval history.
7. Keep batch review and lifecycle actions dry-runnable.
8. Keep review UI optional over the same core lifecycle.

Done when:

- a reviewer can inspect source evidence before promotion;
- a reviewer can explain why a memory entered or did not enter a prompt;
- lifecycle changes are visible and reversible where reversal is allowed;
- API/MCP surfaces cannot bypass policy checks.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_review_inbox tests.test_server_ui tests.test_mcp_server
```

## Phase 4: Portable Bundles And Import/Export

Goal: make memory portable without reactivating unsafe or inactive state.

Files:

- `src/agent_memory_kernel/store.py`
- `src/agent_memory_kernel/cli.py`
- `docs/memory-contract.md`
- `docs/recovery.md`
- `tests/test_memory_store.py`

Tasks:

1. Define a portable `.amk` bundle target: manifest, schema version, contract
   version, source events, candidates, active memories, graph/evidence, policy,
   tombstones, lifecycle history, review history, and audit records.
2. Preserve ids, provenance, scope/lane/namespace boundaries, trust state,
   redaction profile, and policy decisions across export/import.
3. Keep deleted, distrusted, expired, superseded, quarantined, or denied memory
   inactive after import.
4. Add checksum or manifest validation for portable exports.
5. Add poisoned-import and stale-evidence fixtures.

Done when:

- a bundle can move between local stores without changing lifecycle state;
- redacted exports cannot restore hidden content;
- imported inactive memory cannot enter active retrieval;
- policy-denied paths remain denied after import.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_memory_store tests.test_contract_acceptance
```

## Phase 5: Prompt Contract, Adapter Contracts, And Conformance

Goal: let outside tools use the kernel without copying internal assumptions.

Files:

- `src/agent_memory_kernel/conformance.py`
- `src/agent_memory_kernel/contract.py`
- `docs/runtime-contract.md`
- `docs/cross-model-context-contract.md`
- `docs/mcp.md`
- `tests/test_contract_acceptance.py`
- `tests/test_mcp_server.py`

Tasks:

1. Document the prompt envelope as the canonical read surface.
2. Treat Memory Tree as a default renderer over that envelope, not as source of
   truth.
3. Document runtime adapter requirements for pre-call retrieval and post-turn
   Keeper scheduling.
4. Document importer/exporter requirements for preserving provenance and
   lifecycle state.
5. Document retrieval-enhancer requirements so embeddings or provider rerankers
   cannot override policy filters.
6. Define adapter capability levels: read-only, write-capable,
   lifecycle-capable, graph-capable, export-capable, and prompt-injection
   capable.
7. Add golden traces for correction, deletion, distrust, scope/lane/namespace
   isolation, source mutation, export/import, prompt envelope shape, provider
   prompt snapshots, deterministic retrieval, and resource budgets.
8. Keep adapter certification local and reproducible.

Done when:

- a new adapter can run conformance without private data;
- conformance catches policy bypasses and lifecycle leaks;
- optional adapters can fail without breaking the kernel.

Verification:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance seed --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance run --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m unittest tests.test_contract_acceptance tests.test_mcp_server
```

## Phase 6: Starter Packs And Examples

Goal: demonstrate integration without turning examples into architecture.

Files:

- `templates/vault/README.md`
- `templates/vault/personal.md`
- `templates/vault/professional.md`
- `examples/reference-loop-demo/README.md`
- `examples/personal-professional-demo/README.md`
- `examples/agent-loop-demo/README.md`
- `examples/hermes-e2e-demo/README.md`
- `adapters/hermes_provider/README.md`

Tasks:

1. Keep the provider-neutral reference loop as the canonical demo.
2. Keep personal/professional memory as starter templates over generic
   scope/lane/namespace primitives.
3. Keep runtime and domain examples thin.
4. State clearly that examples consume the kernel contract.
5. Do not make any example a requirement for local full-memory completion.

Done when:

- examples can be skipped without losing the core;
- examples point back to the charter, AMK-000, and contracts;
- domain examples use packs or adapters, not hardcoded kernel behavior.

Verification:

```bash
rg -n "optional|example|kernel contract|Kernel Charter|AMK-000" examples adapters docs README.md
```

## Phase 7: Out-Of-Core Enhancements

Goal: add power without making the kernel heavier.

Extension candidates:

- embeddings and ANN retrieval;
- provider-specific prompt format certification;
- richer graph optimization;
- local review UI improvements;
- notification sender bridges;
- importer/exporter bridges;
- outcome loop packs;
- hosted sync experiments.

Rules:

1. Enhancements must run after policy filtering, not before it.
2. Enhancements must not become required for deterministic conformance.
3. Enhancements must not weaken any memory-safety invariant.
4. Hosted features stay in [hosted-roadmap.md](hosted-roadmap.md).

Verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
