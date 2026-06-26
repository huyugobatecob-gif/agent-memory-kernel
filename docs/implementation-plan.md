# Implementation Plan

This plan is the working map for turning Agent Memory Kernel from a small local
template into a reusable open-source memory substrate.

## Product Shape

The project should remain universal by default:

- default lanes: `personal` and `professional`;
- optional lanes: `project`, `agent`, `session`;
- optional domain extensions: Hermes, SEO loops, research loops, QA loops,
  support workflows, CRM memory;
- local-first storage;
- auditable lifecycle;
- simple graph model that can deepen over time.

The key rule: domain-specific intelligence should be built as extensions over
the kernel, not hard-coded into the kernel.

## Phase 0: Repository Baseline

Goal: make the project understandable and safe to publish.

Files:

- `README.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `.gitignore`
- `.github/workflows/tests.yml`
- `pyproject.toml`

Tasks:

1. Define the project promise in one sentence.
2. Explain what exists now and what does not.
3. Add install and quickstart commands.
4. Add CI that installs the package and runs tests.
5. Keep the repository free of private project data.

Done when:

- a new user can understand the project in under five minutes;
- tests run locally and in GitHub Actions;
- no private workspace assumptions are required.

Verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Phase 1: Core Local Kernel

Goal: implement the durable memory lifecycle.

Files:

- `src/agent_memory_kernel/schema.sql`
- `src/agent_memory_kernel/store.py`
- `src/agent_memory_kernel/policy.py`
- `src/agent_memory_kernel/cli.py`
- `tests/test_memory_store.py`

Lifecycle:

```text
event -> candidate_memory -> review/policy -> active_memory -> context_pack
```

Tasks:

1. Store raw events append-only.
2. Extract conservative candidate memories.
3. Keep candidate review separate from active memory.
4. Quarantine secret-like content.
5. Preserve source links and audit logs.
6. Support correction and soft-delete.
7. Export human-readable markdown vaults.
8. Return agent-ready context packs.

Done when:

- pending memories do not appear in search;
- approved memories appear in search and context packs;
- quarantined content cannot be approved directly;
- corrections update active memory;
- deleted memory is no longer retrieved;
- export creates readable markdown files.

Verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m agent_memory_kernel.cli init --db /tmp/amk.db
```

## Phase 2: Graph Layer

Goal: make memory navigable without overbuilding ontology too early.

Files:

- `src/agent_memory_kernel/schema.sql`
- `src/agent_memory_kernel/extractors/base.py`
- `src/agent_memory_kernel/extractors/rules.py`
- `docs/v0-memory-contract.md`

Starter nodes:

- `memory`
- `person`
- `project`
- `document`
- `tool`
- `decision`
- `preference`
- `rule`

Starter edges:

- `relates_to`
- `belongs_to`
- `uses`
- `decided_in`
- `derived_from`
- `supersedes`
- `conflicts_with`

Tasks:

1. Create an anchor node for each active memory.
2. Link extracted entities to the anchor node.
3. Keep graph extraction deterministic in v0.
4. Document how richer extractors can add deeper graph structure.

Done when:

- approved memory creates at least one `memory` node;
- extracted project/person nodes are linked by edges;
- tests verify graph creation.

## Phase 3: Personal / Professional Public Template

Goal: support users who only need structured memory, not loops.

Files:

- `templates/vault/README.md`
- `templates/vault/personal.md`
- `templates/vault/professional.md`
- `examples/personal-professional-demo/README.md`

Tasks:

1. Keep the default mental model as two lanes.
2. Show commands for personal preferences.
3. Show commands for professional rules.
4. Export markdown files for review.

Done when:

- a non-technical user can understand what belongs in each lane;
- examples run with the CLI.

## Phase 4: Hermes Adapter

Goal: let Hermes use the kernel without owning memory.

Files:

- `adapters/hermes_provider/hermes_provider.py`
- `adapters/hermes_provider/README.md`
- `docs/hermes-integration.md`

Provider responsibilities:

- request context packs before planning;
- record post-work memories as candidates;
- expose pending review;
- keep memory lifecycle inside `MemoryStore`.

Tasks:

1. Keep the adapter thin.
2. Define the provider interface.
3. Add integration examples.
4. Later, connect the provider to real Hermes runtime hooks.

Done when:

- Hermes can call `context_pack(query)`;
- Hermes can call `remember(summary)`;
- pending candidates stay reviewable.

## Phase 5: Outcome / Loop Extension

Goal: make iterative work improve over time.

This is the SEO-project layer, but it should be generic enough for other
iterative workflows.

New memory kinds:

- `attempt`
- `outcome`
- `lesson`
- `pattern`
- `gotcha`

Suggested graph:

```text
attempt -> produced_outcome
attempt -> failed_because -> gotcha
attempt -> succeeded_because -> pattern
outcome -> created_lesson -> rule
```

Tasks:

1. Add an outcome extractor.
2. Add attempt/outcome schema helpers.
3. Add success/failure comparison queries.
4. Build context packs that include both successes and failures.
5. Add tests using realistic loop examples.

Done when:

- an agent planning a new loop can retrieve similar successes;
- the same agent can retrieve similar failures;
- context packs cite both with provenance;
- no failed model output becomes durable truth without review.

## Phase 6: API / MCP / UI

Goal: make the kernel easier to use across tools.

Options:

- FastAPI server;
- MCP server;
- browser review UI;
- Obsidian/markdown sync;
- embedding search plugin.

Tasks:

1. Keep the SQLite store as source of truth.
2. Expose stable read/write endpoints.
3. Add authentication for hosted modes.
4. Add review inbox UI.
5. Add graph browser only after real data proves useful navigation patterns.

Done when:

- external agents can retrieve context without shelling out;
- humans can approve/reject/correct memory comfortably;
- exports remain possible.

## Phase 7: Security Hardening

Goal: treat memory as part of the prompt boundary.

Tasks:

1. Add stronger secret detection.
2. Add prompt-injection warnings for untrusted sources.
3. Add source-type policies.
4. Add import validation.
5. Add audit export.
6. Add conflict detection for rules.
7. Add deletion/correction tests around FTS and graph edges.

Done when:

- untrusted content cannot silently create active rules;
- active memory always includes provenance;
- dangerous content is quarantined;
- correction/deletion behavior is documented and tested.

## Operating Principle

The kernel should remember actions, but it should not blindly trust them.

The system can record nearly every action as an event. Durable memory is the
reviewed, cited, retrievable layer that future agents use for planning.
