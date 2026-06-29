# What Agent Memory Kernel Is

Agent Memory Kernel is a local memory kernel for agents and human workflows.
It records what happened, proposes what should be remembered, lets policy or a
reviewer decide what becomes active memory, and gives future agents only the
selected memory they are allowed to see.

The short version:

```text
event -> candidate -> review/policy -> active memory
-> evidence graph -> selected context -> prompt envelope
```

The main agent does not search the whole graph. The Router selects allowed,
relevant, budgeted memory before the model call. The Keeper proposes memory
updates after a turn is saved. The store keeps provenance, lifecycle state,
review history, and audit records so memory can be explained, corrected,
distrusted, deleted, exported, and imported.

## What It Is

- A local-first memory source of truth.
- A SQLite reference implementation.
- A reviewable memory lifecycle.
- A policy-filtered retrieval contract.
- A provider-neutral prompt envelope.
- A provenance and audit layer for agent memory.
- A conformance target for runtimes and adapters.

## What It Is Not

- Not a hosted SaaS product.
- Not a Hermes-specific system.
- Not an SEO-specific workflow.
- Not an agent runtime or orchestration framework.
- Not a vector database requirement.
- Not a dashboard, billing system, notification service, or team admin console.

Those can be built around the kernel, but they are adapters, examples,
extensions, or later hosted work.

## Core Objects

- `source_event`: raw observed evidence such as a message, import, tool result,
  document excerpt, or maintenance event.
- `candidate_memory`: proposed durable memory that still needs review or policy
  promotion.
- `active_memory`: reviewed or policy-approved memory that can be retrieved.
- `scope`, `lane`, and `namespace`: access and grouping boundaries.
- `policy`: local rules for read, write, inject, export, lifecycle, and
  redaction behavior.
- `Keeper`: post-turn writer that proposes candidates and graph commands.
- `Router`: pre-call reader that selects allowed, relevant memory.
- `prompt envelope`: provider-neutral memory payload for the main model.

## Default Packs

The public starter pack includes two useful lanes. The detailed contract lives
in [default-packs.md](default-packs.md).

- `personal`: preferences, stable personal context, relationships, recurring
  context, and communication style.
- `professional`: projects, decisions, rules, constraints, collaborators,
  gotchas, and work patterns.

These are defaults, not a hardcoded ontology. Teams can add project, agent,
session, research, support, CRM, QA, SEO, or custom lanes without changing the
kernel model.

## Public Alpha Promise

The public alpha is trustworthy only when the local conformance suite proves
that:

- deleted or distrusted memory cannot reappear through old evidence;
- personal/private memory does not leak into professional prompts by default;
- derived graph, summary, export, and prompt surfaces follow lifecycle changes;
- import/export preserves provenance, tombstones, review history, review queues,
  trust state, policy metadata, and evidence chains;
- prompt envelopes contain selected memory only, never the full graph;
- every read, write, injection, export, denial, correction, deletion, and
  lifecycle action is auditable.
