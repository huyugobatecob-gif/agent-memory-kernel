# Implementation Plan

This is the working plan for turning Agent Memory Kernel into a stable,
reusable memory kernel.

The governing documents are [../SPEC.md](../SPEC.md),
[kernel-charter.md](kernel-charter.md), and
[backlog-cutover.md](backlog-cutover.md). Backlog items must be classified as
`core`, `extension`, or `later-hosted` before they are treated as core work.
Current implementation state is tracked in
[core-status-audit.md](core-status-audit.md).

## Outcome

Agent Memory Kernel should provide a local-first, auditable memory layer that
any agent runtime or human workflow can use without depending on one product,
provider, hosted service, or domain.

The core loop is:

```text
after_saved_turn
-> store source event
-> Keeper proposes candidate memory
-> review or policy promotes/rejects
-> before_model_call
-> Router retrieves policy-filtered active memory
-> prompt envelope receives Memory Tree Supplement
```

## Scope Model

### Core

Core work changes the local memory contract itself:

- source events, turns, and provenance;
- candidate memories and active memories;
- personal and professional lanes;
- graph nodes, graph edges, evidence, and derivation;
- Keeper proposal contract;
- Router retrieval contract;
- prompt envelope and Memory Tree Supplement;
- review lifecycle and lifecycle mutations;
- read, write, inject, export, and lifecycle policies;
- deterministic baseline retrieval;
- import/export with provenance and tombstones;
- audit, explainability, and conformance.

### Extension

Extension work is optional and must consume the core contract:

- runtime adapters;
- provider formatters;
- importer/exporter bridges;
- domain packs such as outcome loops, SEO, research, support, CRM, or QA;
- optional embeddings and provider-backed rerankers;
- richer local review UI and graph exploration;
- notification sender bridges.

### Later Hosted

Hosted work is not required for local full-memory completion:

- hosted multi-user API/UI;
- tenancy, RBAC, and team administration;
- hosted dashboards and billing operations;
- remote MCP hosting;
- managed alerts and schedulers;
- KMS/off-host backup custody;
- hosted adapter registry and badge publishing.

## Done When

The repository can claim full local memory when:

- the local reference loop passes deterministic tests;
- correction, deletion, distrust, expiration, supersession, and rollback affect
  prompt-facing retrieval correctly;
- denied, private, quarantined, or untrusted memory cannot leak into prompts;
- selected memory is returned with provenance and selection reasons;
- derived graph, prompt, export, and summary surfaces are invalidated when
  source memory changes;
- export/import preserves provenance, policy state, review history, and
  tombstones;
- adapters can pass conformance without private project assumptions.

## Invariant Matrix

Every kernel law must be mapped to a code path and a verifier before the kernel
can claim completion.

| Invariant | Core paths | Required verifier |
| --- | --- | --- |
| Deleted memory cannot reappear from retained evidence | lifecycle mutation, search, tree pack, context builder, graph/evidence export | unit test plus conformance golden trace |
| Distrusted sources cannot influence retrieval, summary, or derived memory | distrust lifecycle, thread summaries, semantic analyses, graph/tree, export | unit test plus conformance golden trace |
| Personal/private lanes cannot leak into professional prompts | read policy, scope filtering, summaries, graph/tree, prompt envelope, export | unit test plus prompt-envelope snapshot |
| Correction/rollback/delete/distrust/expire/supersede invalidate derived memory | lifecycle engine, derived invalidation ledger, graph surfaces, summaries, exports | lifecycle report plus import/export round trip |
| Export/import preserves provenance, tombstones, trust, review, policy, and evidence | profile export/import, vault export/import, lifecycle/policy state | round-trip test plus conformance trace |
| Prompt envelopes contain selected filtered content only | Router, tree pack, context builder, prompt formatter | deterministic envelope snapshot |

This matrix is an implementation gate. A feature is not considered done when it
has a table or command; it is done when the relevant invariant has executable
proof.

## Phase 0: Scope And Status Lock

Goal: make the project understandable as a kernel before adding more features.

Files:

- `SPEC.md`
- `docs/kernel-charter.md`
- `docs/backlog-cutover.md`
- `docs/core-status-audit.md`
- `docs/hosted-roadmap.md`
- `README.md`
- `docs/roadmap.md`

Tasks:

1. Define the one-sentence project promise.
2. Separate `core`, `extension`, and `later-hosted` backlog.
3. Move hosted/platform/runtime/domain rollout language out of the core plan.
4. Make adapter and domain examples visibly optional.
5. Keep a `done`, `partial`, `missing`, `extension`, and `later-hosted` audit
   so future work does not rebuild completed features.
6. Add a plain-language model: collect, extract, review, store, retrieve,
   explain, correct.

Done when:

- new contributors can tell what belongs in the kernel;
- hosted and domain-specific items are not listed as local v1 blockers;
- docs link to the spec, charter, backlog cutover, and status audit.

Verification:

```bash
rg -n "SPEC.md|kernel-charter|backlog-cutover|core-status-audit|later-hosted|extension" README.md docs SPEC.md
```

## Phase 1: Kernel Schema And Laws

Goal: make memory safety invariants enforceable instead of aspirational.

Files:

- `src/agent_memory_kernel/schema.sql`
- `src/agent_memory_kernel/store.py`
- `src/agent_memory_kernel/contract.py`
- `docs/memory-contract.md`
- `docs/memory-lifecycle-contract.md`
- `docs/security-identity-contract.md`
- `tests/test_memory_store.py`
- `tests/test_contract_acceptance.py`

Tasks:

1. Version schemas for source events, candidates, active memories, graph nodes,
   graph edges, evidence, lanes, policies, review actions, mutations,
   tombstones, and audit records.
2. Keep migration behavior explicit and testable.
3. Add or strengthen invariant tests:
   - deleted memory cannot reappear from retained evidence;
   - distrusted sources cannot influence retrieval, summaries, or derived
     memory;
   - personal/private lanes cannot leak into professional prompts;
   - derived memory invalidates on correction, deletion, distrust, expiration,
     or supersession;
   - exports preserve provenance, trust state, policy metadata, review history,
     evidence chains, and tombstones.
4. Keep deterministic behavior as the default path.

Done when:

- invariant tests prove the safety rules;
- the machine-readable contract describes the same laws as the docs;
- migrations and restore checks report schema compatibility.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_memory_store tests.test_contract_acceptance
```

## Phase 2: Local Reference Loop

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
4. Ensure the prompt envelope contains selected branch content, not tags only.
5. Ensure the main model never receives the full graph.
6. Keep no-memory fallback explicit when retrieval fails or policy denies access.

Done when:

- `slice seed/run/assert` passes;
- a corrected memory replaces the old one;
- deleted, distrusted, expired, and superseded memory is absent from the prompt;
- lane isolation is visible in prompt metadata;
- Keeper and Router runs are auditable by ID.

Verification:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice seed --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice run --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice assert --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m unittest tests.test_orchestrator tests.test_memory_store
```

## Phase 3: Review And Explainability

Goal: make memory inspectable and correctable by humans and supervising agents.

Files:

- `src/agent_memory_kernel/store.py`
- `src/agent_memory_kernel/cli.py`
- `src/agent_memory_kernel/server.py`
- `src/agent_memory_kernel/mcp_server.py`
- `docs/review-workflow.md`
- `tests/test_review_inbox.py`
- `tests/test_server_ui.py`
- `tests/test_mcp_server.py`

Tasks:

1. Keep approve, reject, correct, delete, distrust, expire, supersede, and
   rollback available through CLI/API/MCP where appropriate.
2. Add or strengthen human-readable memory diffs.
3. Add or strengthen "why this memory exists" views: source evidence, reviewer,
   lane, policy decision, trust state, lifecycle history, and retrieval history.
4. Keep batch review and lifecycle actions dry-runnable.
5. Keep review UI optional over the same core lifecycle.

Done when:

- a reviewer can inspect source evidence before promotion;
- a reviewer can explain why a memory entered a prompt;
- lifecycle changes are visible and reversible where reversal is allowed;
- API/MCP surfaces cannot bypass policy checks.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_review_inbox tests.test_server_ui tests.test_mcp_server
```

## Phase 4: Default Lanes And Beginner Templates

Goal: make the default memory model useful without domain-specific loops.

Files:

- `templates/vault/README.md`
- `templates/vault/personal.md`
- `templates/vault/professional.md`
- `examples/personal-professional-demo/README.md`
- `docs/memory-contract.md`

Tasks:

1. Define the `personal` lane: preferences, stable facts, relationships,
   recurring context, communication style, and private defaults.
2. Define the `professional` lane: projects, decisions, constraints,
   collaborators, working rules, gotchas, and professional patterns.
3. Keep project, agent, and session lanes documented as optional policy scopes.
4. Provide a beginner workflow: remember, review, retrieve, correct, delete,
   distrust, export.

Done when:

- a user who does not use agents or loops can still understand the template;
- examples do not require domain-specific context;
- personal memory is never returned to professional-only prompts by default.
- docs do not describe personal/professional as domain packs that can bypass
  lane policy.

Verification:

```bash
PYTHONPATH=src python3 -m unittest tests.test_memory_store
```

## Phase 5: Adapter Contracts And Conformance

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

1. Document runtime adapter requirements for pre-call retrieval and post-turn
   Keeper scheduling.
2. Document importer/exporter requirements for preserving provenance and
   lifecycle state.
3. Document retrieval-enhancer requirements so embeddings or provider rerankers
   cannot override policy filters.
4. Add golden traces for correction, deletion, distrust, lane isolation,
   source mutation, export/import, prompt envelope shape, and deterministic
   retrieval.
5. Keep adapter certification local and reproducible.

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

## Phase 6: Examples

Goal: demonstrate integration without turning examples into architecture.

Files:

- `examples/reference-loop-demo/README.md`
- `examples/personal-professional-demo/README.md`
- `examples/agent-loop-demo/README.md`
- `examples/hermes-e2e-demo/README.md`
- `adapters/hermes_provider/README.md`

Tasks:

1. Keep the provider-neutral reference loop as the canonical demo.
2. Keep personal/professional memory as the first beginner example.
3. Keep runtime and domain examples thin.
4. State clearly that examples consume the kernel contract.
5. Do not make any example a requirement for local full-memory completion.

Done when:

- examples can be skipped without losing the core;
- examples point back to the charter and contracts;
- domain examples use packs or adapters, not hardcoded kernel behavior.

Verification:

```bash
rg -n "optional|example|kernel contract|Kernel Charter" examples adapters docs README.md
```

## Phase 7: Optional Enhancements

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
