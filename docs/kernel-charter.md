# Kernel Charter

Agent Memory Kernel is a universal local-first, auditable memory kernel for
agents and human workflows.

It is not a hosted agent platform, not a runtime orchestrator, and not a
domain-specific SEO or Hermes system. Those integrations can exist, but they
must consume the kernel contract instead of shaping it.

The executable kernel law is maintained in
[amk-000-kernel-invariants.md](amk-000-kernel-invariants.md).

## Core Promise

The kernel turns raw interaction history into governed, reusable, explainable
context:

```text
source event
-> candidate memory
-> review or policy decision
-> active memory
-> graph/evidence model
-> policy-filtered context pack
-> prompt envelope
-> optional Memory Tree rendering
```

The main agent should never scan the full memory graph. The Router selects
allowed memory before a model call, and the Keeper proposes memory updates after
a saved turn. Memory Tree is a renderer over the read contract, not the kernel
ontology.

## What The Kernel Owns

The kernel owns durable memory truth and every rule that decides whether memory
can be written, read, injected, exported, corrected, or forgotten.

Core responsibilities:

- local-first source of truth, with SQLite as the reference store;
- immutable source events and saved turns;
- candidate memories and active memories;
- generic scope, lane, namespace, actor, policy, and surface primitives;
- starter personal/professional templates and optional project, agent, session,
  or custom lanes through policy;
- memory graph nodes, edges, evidence, and derivation links;
- Keeper extraction and graph-command contracts;
- Router retrieval and read-time decision policy;
- prompt envelope contract and optional Memory Tree renderer contract;
- review lifecycle: approve, reject, correct, delete, distrust, expire,
  supersede, and rollback;
- read, write, inject, export, and lifecycle policies;
- provenance-preserving import and export;
- local actor capability grants;
- audit trails and explainability reports;
- schema, migration, transaction, recovery, and performance contracts;
- deterministic baseline retrieval without requiring embeddings;
- conformance fixtures and invariant tests.

## What Is Not Core

These features can be useful, but they are adapters, examples, extensions, or
hosted-product work:

- Hermes rollout or any other specific runtime rollout;
- SEO loop traces as a required architecture path;
- hosted identity, tenancy, RBAC, or team administration;
- hosted dashboards, billing dashboards, and provider invoice fetchers;
- remote MCP deployment patterns;
- live notification senders;
- KMS, managed off-host backup, and cloud custody integrations;
- managed scheduler recipes and hosted alerting;
- live provider certification;
- ANN/vector search or live embeddings as required infrastructure;
- advanced graph compaction beyond safe evidence-preserving maintenance;
- hosted sync and collaboration.

Those items must be documented under `adapters`, `examples`, `extensions`, or a
later hosted roadmap. They must not be required to understand, install, test, or
use the local kernel.

## Package Boundary

Use this boundary when adding files, docs, and backlog items:

```text
kernel
  schemas, store, lifecycle, policies, Router, Keeper, prompt packs,
  audit, import/export, deterministic conformance

adapters
  optional runtime, tool, store, importer, exporter, and provider bridges

packs
  reusable memory presets such as personal, professional, project, agent,
  session, outcome loops, research, support, CRM

examples
  small runnable demonstrations that prove integrations consume the kernel
  contract without becoming the contract

extensions
  optional retrieval, hosted, notification, scheduling, dashboard, and provider
  enhancements
```

The repository can keep a simple physical layout, but docs and APIs should use
this mental model consistently.

## Default Templates

The kernel supports generic scopes, lanes, and namespaces. The public template
ships two starter lanes:

- `personal`: user preferences, stable personal context, communication style,
  relationships, recurring context, and private defaults.
- `professional`: projects, decisions, rules, constraints, gotchas, working
  knowledge, collaborators, and professional patterns.

Other lanes are optional policy scopes:

- `project`: project-specific decisions, constraints, facts, and outcomes.
- `agent`: operational memory for a specific agent role.
- `session`: short-lived context that may later become durable memory.

Personal/professional is not the only valid memory model. It is the default
starter pack. Personal memory must not enter professional-only prompts unless an
explicit policy allows it and the prompt metadata records that decision.

## Memory Safety Invariants

These invariants are kernel law. They should be enforced by schema, lifecycle
rules, retrieval filters, export/import behavior, and conformance tests.

1. Deleted memory cannot reappear from retained source evidence.
2. Distrusted sources cannot influence retrieval, summaries, derived memory,
   graph-derived style, or exported active memory.
3. Scope, lane, namespace, personal, or private memory cannot leak into another
   prompt, export, graph, summary, or shared surface without an explicit policy
   decision.
4. Derived memory must be invalidated when its source is corrected, deleted,
   distrusted, expired, or superseded.
5. Superseded memory must not win prompt-facing retrieval over its replacement.
6. Quarantined or secret-like content must not become active memory without
   explicit review and policy permission.
7. Assistant, tool, web, and external-document claims remain reviewable by
   default and must not become trusted facts silently.
8. Exports must preserve provenance, tombstones, trust state, review history,
   policy metadata, and evidence chains.
9. Prompt envelopes must contain selected, policy-filtered memory only, never
   the full graph.
10. Every read, write, injection, export, correction, deletion, and denial must
    be auditable.

## Reference Loop

The reference runtime loop is intentionally small:

```text
after_saved_turn
-> store source event and messages
-> Keeper proposes candidate memories and graph commands
-> review or policy promotes safe candidates
-> before_model_call
-> Router selects allowed active memory
-> prompt envelope receives selected memory content
-> main model answers without direct graph access
```

This loop is complete only when correction, deletion, distrust, lane isolation,
export/import, and no-memory fallback behave predictably.

## Completion Bar

The kernel can claim full memory when current evidence proves:

- the local reference loop passes deterministic golden traces;
- selected memory improves or clarifies agent behavior versus no-memory
  baseline in fixtures;
- denied, deleted, distrusted, expired, superseded, and quarantined memory stays
  out of prompt-facing retrieval;
- every selected branch has provenance and a readable selection reason;
- every lifecycle mutation propagates to derived graph, prompt, export, and
  summary surfaces;
- adapters can pass conformance without relying on private project behavior.
