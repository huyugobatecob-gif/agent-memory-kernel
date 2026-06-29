# AMK-000: Kernel Invariants And Conformance Contract

Status: normative draft.

This document is the first implementation gate for Agent Memory Kernel. New
core work should either satisfy this contract or explicitly extend it with a
new verifier.

## Purpose

Agent Memory Kernel is a universal local-first memory kernel. It is a local
causal record of what was observed, proposed, believed, revised, hidden,
expired, exported, and injected into an agent prompt.

The kernel must be usable by any runtime, IDE, chat app, automation, or human
workflow without depending on Hermes, SEO projects, hosted services, a model
provider, or a specific domain.

## Kernel Primitives

The kernel owns these primitives:

- `source_event`: append-only observed input, output, import, tool result, or
  maintenance event.
- `candidate_memory`: proposed durable memory that still needs review or policy
  promotion.
- `active_memory`: reviewed or policy-approved memory that can enter retrieval.
- `scope`: the access boundary requested by a read, write, export, or inject
  operation.
- `lane`: a policy grouping inside or across scopes. `personal` and
  `professional` are starter lanes, not hardcoded ontology.
- `namespace`: a stable owner or package boundary for projects, agents,
  workspaces, apps, or imports.
- `surface`: where memory may appear, such as prompt, export, graph browser,
  summary, API response, or review UI.
- `policy`: local rules that decide read, write, inject, export, lifecycle, and
  redaction behavior.
- `evidence`: auditable links from memory and graph structures back to source
  events.
- `lifecycle_state`: active, pending, rejected, corrected, superseded, deleted,
  distrusted, expired, quarantined, or rolled back state.

## Non-Core

These are not kernel requirements:

- runtime rollouts for any named agent system;
- SEO, trading, CRM, research, support, or other domain-specific workflows;
- hosted identity, tenancy, RBAC consoles, team dashboards, or billing;
- remote MCP hosting, live notification sending, or managed schedulers;
- KMS, cloud custody, or managed off-host backups;
- live provider certification;
- ANN/vector search as mandatory infrastructure.

Those items can exist as adapters, packs, examples, or later hosted work.

## Invariant Matrix

| Invariant | Required verifier |
| --- | --- |
| Deleted memory cannot reappear from retained source evidence. | Unit test plus conformance golden trace covering search, graph, export, summary, and prompt surfaces. |
| Distrusted or quarantined sources cannot influence retrieval, summaries, graph-derived state, exports, or prompts. | Lifecycle test plus unsafe-source conformance fixture. |
| Scope/lane/namespace isolation holds across prompts, graph evidence, summaries, browser previews, and exports. | Leak-prevention fixtures with adversarial cross-scope evidence. |
| Corrections, rollback, delete, distrust, expire, and supersede invalidate derived memory. | Derived invalidation ledger test and prompt/export round trip. |
| Prompt envelopes contain selected, policy-filtered, budgeted memory only. | Deterministic selected-content and budget-trim prompt snapshots. |
| Retrieval ranking is deterministic without embeddings. | Ranking fixture with stable score inputs and tie-breakers. |
| Import/export preserves ids, provenance, evidence, tombstones, trust state, review history, policy metadata, and lifecycle state. | Portable bundle round-trip test. |
| Every read, write, inject, export, correction, deletion, denial, and lifecycle change is auditable. | Audit log fixture and explainability assertion. |
| Local actors can perform only actions allowed by capability grants and policy. | Policy simulator and denied-action conformance fixture. |
| Large histories remain bounded and predictable. | Bounded-selection prompt fixture plus performance fixture covering index use, retrieval latency, export size, and compaction/retention behavior. |

## Lifecycle State Machine

Source events are append-only evidence. They may be hidden from prompt-facing
surfaces by policy, lifecycle, or trust state, but they are not silently
rewritten.

Candidate memory can transition to:

- `active` through review or explicit write policy;
- `rejected` through review;
- `quarantined` when secret-like, prompt-injection-like, unsafe, or unauthorized
  content is detected;
- `expired` when retention policy ends its useful life.

Active memory can transition to:

- `corrected` with revision history and replacement text;
- `superseded` by a newer memory;
- `deleted` with tombstone and provenance retained;
- `distrusted` when its source or evidence chain is no longer allowed;
- `expired` by time or policy;
- `rolled_back` to a prior valid revision when policy allows.

Derived graph nodes, edges, summaries, semantic analyses, prompt packs, exports,
and style hints must inherit source lifecycle restrictions.

## Prompt Contract

The kernel defines a provider-neutral prompt envelope. The envelope contains
only selected, allowed, budgeted memory plus provenance and selection metadata.

Memory Tree is a renderer over that read contract. It may be the default
human-readable prompt section, but it is not the kernel ontology and must not
bypass retrieval or policy filters.

The baseline budget trace is `golden_trace_prompt_budget_trims_context_pack`:
large context-pack material must be trimmed with an explicit marker while the
selected Memory Tree Supplement remains a separate prompt message with its own
provenance and selection metadata.

## Deterministic Read Contract

Baseline retrieval must work without embeddings or live provider calls.

The read contract must define:

- inputs: query, scope, namespace, actor, surface, allowed/denied scopes,
  recency hints, thread/project hints, and token budget;
- filters: lifecycle, trust, sensitivity, policy, quarantine, redaction,
  conflict, supersession, and scope isolation;
- ranking: lexical relevance, exact aliases, graph proximity, recency,
  importance, confidence, outcome value, trust penalties, and stable
  tie-breakers;
- outputs: selected memory content, source ids, reasons, warnings, truncation
  decisions, prompt budget metadata, and no-memory fallback.

Embeddings and vector indexes can improve ranking after policy filtering, but
they cannot be required for correctness.

The baseline golden trace is `golden_trace_deterministic_ranking_snapshot`: the
same local query must produce identical ranks, scores, reasons, and policy
factors without provider calls.

## API And Versioning

The stable kernel surface is:

- CLI commands for init, record, review, retrieve, explain, lifecycle, import,
  export, conformance, and health checks;
- Python API for the same lifecycle and retrieval paths;
- optional HTTP/MCP adapters that consume the kernel contract;
- versioned schema migrations and versioned conformance fixtures.

Breaking changes require a contract version bump and migration/conformance
evidence.

## Portable Bundle

The portable archive target is `.amk`: a local export bundle containing:

- SQLite snapshot or normalized JSON tables;
- manifest with schema and contract versions;
- source events, candidates, active memory, evidence, graph records, policies,
  tombstones, lifecycle history, review history, and audit records;
- redaction profile and export policy decision;
- conformance trace outputs and prompt snapshots when available.

The baseline local envelope is `amk-bundle-v0.1`. Its manifest must include a
schema version, AMK contract marker, lifecycle/policy versions, and canonical
JSON SHA-256 payload digest. Import must verify the manifest before applying the
payload.

Import must preserve inactive states. Deleted, distrusted, expired,
superseded, quarantined, or denied memory must not become active through import.

## Conformance

The canonical conformance corpus must include:

- source event -> candidate -> review -> active -> retrieval -> prompt;
- correction, rollback, delete, distrust, expire, and supersede;
- cross-scope and cross-namespace leak attempts;
- poisoned imports and prompt-injection evidence;
- deterministic ranking fixtures;
- budget-trim prompt envelope fixtures;
- large-history bounded prompt fixtures;
- provider-shaped prompt envelope snapshots;
- import/export round trips;
- migration and recovery checks;
- policy dry-runs and denied-action traces;
- performance/resource budget checks for large local histories.

Core work is complete only when the relevant conformance scenario passes.
