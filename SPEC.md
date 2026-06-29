# Agent Memory Kernel Spec

This spec is the public contract for Agent Memory Kernel. It defines the local
kernel behavior that adapters, examples, hosted services, and domain packs must
consume instead of redefining.

## Purpose

Agent Memory Kernel turns interaction history into governed, reusable,
explainable context:

```text
source event
-> candidate memory
-> review or policy decision
-> active memory
-> graph/evidence model
-> policy-filtered retrieval
-> prompt envelope / Memory Tree Supplement
-> Keeper update after the next saved turn
```

The kernel is local-first. SQLite is the reference store. Hosted services,
runtime rollouts, provider integrations, and domain packs are optional layers.

## Core Objects

### Source Event

An append-only record of something observed by the kernel: a user message,
assistant response, tool result, imported note, document excerpt, or maintenance
event. Source events are evidence, not automatically trusted memory.

Required behavior:

- preserve source type and source reference;
- preserve actor/thread/scope metadata when available;
- remain auditable after memory is corrected, deleted, distrusted, or expired;
- never re-enter prompt-facing context directly after linked memory is inactive.

### Candidate Memory

A proposed durable memory extracted by a Keeper, imported from a source, or
recorded manually.

Required behavior:

- carry scope, kind, trust, confidence, sensitivity, and provenance;
- remain reviewable by default when created from assistant, tool, web, or
  external-document claims;
- quarantine secret-like or prompt-injection-like content;
- require policy or review before becoming active memory.

### Active Memory

A durable fact, rule, decision, preference, attempt, outcome, gotcha, or pattern
that passed review or policy.

Required behavior:

- expose provenance and review history;
- participate in policy-filtered retrieval;
- support correction, rollback, deletion, distrust, expiration, and supersession;
- invalidate or hide derived memory when lifecycle state changes.

### Graph And Evidence

The graph-tree layer groups active memory into nodes, edges, compact items,
summaries, and evidence links.

Required behavior:

- graph nodes and edges must have source evidence or auditable derivation;
- graph/tree branches are retrieval views, not the source of truth;
- stale, deleted, distrusted, expired, superseded, quarantined, denied, or
  cross-lane content must not reappear through graph surfaces;
- graph-derived style hints are advisory and suppressible.

## Lanes

Default lanes:

- `personal`: preferences, stable personal context, communication style,
  relationships, recurring context, and private defaults.
- `professional`: projects, decisions, constraints, rules, gotchas, working
  knowledge, collaborators, and professional patterns.

Optional lanes such as `project`, `agent`, and `session` are policy scopes, not
new kernel assumptions.

Lane law:

- personal/private memory must not enter professional, project, public, or
  shared prompts unless an explicit policy allows it;
- cross-lane retrieval must be visible in prompt metadata and audit;
- summaries, semantic analyses, exports, graph nodes, and prompt envelopes must
  inherit the lane restrictions of their source memory.

## Router Contract

The Router is the pre-model read path.

Input:

- query/current task;
- requested scope and allowed/denied scopes;
- actor identity and policy context;
- optional thread/project/session hints;
- prompt budget.

Required output:

- selected memory branch content, not tags only;
- provenance/source ids;
- selection and truncation reasons;
- access decisions and warnings;
- prompt envelope metadata;
- no-memory fallback when policy denies access or retrieval fails closed.

The main model must never scan the full graph. It receives only the selected,
policy-filtered prompt envelope.

## Keeper Contract

The Keeper is the post-turn write path.

Input:

- saved user/assistant exchange;
- scope, actor, thread, model, and source metadata;
- write policy.

Required output:

- source event and saved turn records;
- candidate memories or graph commands;
- review/audit records;
- failure status if extraction fails.

Keeper writes are reviewable by default. Assistant guesses, tool output, web
claims, and external documents must not silently become trusted active memory.

## Prompt Envelope

The prompt envelope is provider-neutral context for the main model.

Required sections:

1. system core and safety notes;
2. rules/profile digest if allowed;
3. compact active memory if allowed;
4. older thread excerpts and summaries if allowed;
5. `MEMORY_TREE_SUPPLEMENT`;
6. recent messages;
7. current user request.

Required behavior:

- include selected branch content, not only routing tags;
- keep retrieved memory outside higher-priority provider system surfaces unless
  the adapter contract explicitly preserves safety boundaries;
- fit deterministic prompt budgets;
- omit unauthorized, stale, unsafe, or inactive memory rather than hiding it in
  text.

## Lifecycle Law

Every lifecycle mutation must propagate to retrieval, graph, summary, export,
and prompt-facing surfaces.

Kernel invariants:

1. Deleted memory cannot reappear from retained source evidence.
2. Distrusted sources cannot influence retrieval, summaries, derived memory,
   graph-derived style, or exported active memory.
3. Personal/private lanes cannot leak into professional prompts by default.
4. Derived memory invalidates after correction, delete, distrust, expire,
   rollback, or supersede.
5. Superseded memory cannot win prompt-facing retrieval over the replacement.
6. Quarantined or secret-like content cannot become active without explicit
   review and policy permission.
7. Assistant, tool, web, and external-document claims remain reviewable by
   default.
8. Export/import preserves provenance, tombstones, trust state, review history,
   policy metadata, and evidence chains.
9. Prompt envelopes contain selected policy-filtered memory only, never the
   full graph.
10. Every read, write, injection, export, correction, deletion, denial, and
    lifecycle change is auditable.

## Import And Export

Profile export/import is a portability boundary.

Required behavior:

- preserve active memory, source events, candidates, graph/evidence,
  tombstones, revisions, derived invalidations, review history, trust state,
  policy metadata, and audit trails;
- keep inactive memory inactive after import;
- keep denied policy paths denied after import;
- support redaction profiles for safe sharing;
- treat encrypted/off-host custody as an extension unless it changes local
  export safety.

## Conformance Levels

### Level 0: Contract Shape

The adapter can print the machine-readable contract, initialize a local store,
and run schema/migration checks.

### Level 1: Local Memory Loop

The adapter can run:

```text
source event -> candidate -> review -> active memory
-> Router-selected prompt envelope -> Keeper candidate update
```

It proves selected memory includes provenance and improves or clarifies the
fixture compared with no memory.

### Level 2: Safety Invariants

The adapter passes golden traces for deletion, distrust, correction, expiration,
supersession, lane isolation, prompt-envelope filtering, and export/import
round trips.

### Level 3: Extension Compatibility

Optional adapters, provider formatters, embeddings, domain packs, and hosted
layers can run without bypassing policy filters or weakening Level 2 invariants.

## Non-Core

The following are useful but not required for the local kernel spec:

- Hermes rollout or any other runtime rollout;
- SEO, CRM, research, support, or loop-specific packs;
- hosted identity, tenancy, RBAC, team administration, and dashboards;
- remote MCP hosting;
- billing dashboards and live provider invoice fetchers;
- live notification senders and managed schedulers;
- KMS/off-host managed backup custody;
- ANN/vector search as required infrastructure;
- live provider certification;
- hosted registry and badge publishing.
