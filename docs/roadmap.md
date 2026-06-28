# Roadmap

## v0.1: Local Kernel

Status: implemented in this template.

- SQLite store.
- CLI.
- Events, candidates, active memories.
- Conversation turns, thread messages, and thread summaries.
- Memory items.
- Manual review.
- Conservative auto-approval.
- Quarantine for secret-like text.
- Persistent graph nodes and edges.
- Node and edge evidence.
- Keeper runs and graph commands audit.
- Light Model semantic analyses.
- Profile notes, project profile metadata, and profile export.
- LLM usage stats.
- Graph groups, optimization runs, and Digital Brain calibration.
- Guarded Digital Brain style append in prompt envelopes.
- Context packs.
- Memory Tree Packs.
- Context builder packs.
- Agent write-policy enforcement.
- Memory revision history and rollback.
- Formal Memory Contract and deterministic acceptance harness.
- Dependency-free semantic reranking for Memory Tree retrieval.
- OpenAI-compatible lightweight extractor adapter.
- Markdown vault export.
- Tests.

## v0.2: Outcome Memory

Goal: make iterative work smarter.

Planned:

- first-class `attempt`, `outcome`, `lesson`, `pattern`, `gotcha` kinds;
- outcome scoring;
- success/failure comparison;
- reusable rule extraction;
- conflict detection between old and new rules;
- project-level tree packs;
- success/failure branches inside tree packs.

This is the layer that makes loops powerful for SEO projects, QA projects,
research projects, and agent optimization.

Current status: baseline outcome records are implemented through
`agent-memory outcome record/list/pack`, `/outcome/record`, `/outcome/list`,
`/outcome/pack`, and the Hermes provider wrapper. Outcome records store
project, loop id, status, hypothesis, action, result, cause, lesson, next
recommendation, score, and links to candidate/active memory.

## v0.2 Full Memory Gap

The automatic memory gap plan is tracked in
[full-memory-gap-plan.md](full-memory-gap-plan.md). It adds the missing
production layers around the local kernel:

- pre-turn Memory Router;
- post-turn Keeper;
- prompt envelope;
- Hermes before/after hooks;
- API/MCP service mode;
- background worker;
- review and security hardening;
- production governed read-time ranking and current-best conflict resolution;
- memory quality evals and usefulness feedback;
- derived-memory invalidation for summaries, graph surfaces, cached packs,
  outcome lessons, and graph-derived style;
- capability and consent model for read/write/promote/inject/export/delete;
- inspection and explainability flows for why memory was recalled or changed;
- operational failure model for slow, unavailable, corrupted, migrated, or
  oversized memory stores.

Before v0.2 can be called full memory, these contracts must be implemented and
tested:

- [runtime-contract.md](runtime-contract.md): pre-call Router, post-turn Keeper,
  and failure behavior.
- [memory-lifecycle-contract.md](memory-lifecycle-contract.md): create,
  correct, delete, distrust, expire, conflict, and export behavior.
- [cross-model-context-contract.md](cross-model-context-contract.md):
  provider-neutral prompt envelope and `MEMORY_TREE_SUPPLEMENT`.
- [security-identity-contract.md](security-identity-contract.md): identity,
  scopes, permissions, audit, redaction, and poisoning defense.
- [end-to-end-vertical-slice.md](end-to-end-vertical-slice.md): executable
  save-retrieve-ingest scenario with permission and poisoning checks.
- [memory-contract.md](memory-contract.md): lane rules, typed memory, write
  actions, closed-loop requirements, and deterministic acceptance gates.

Current status: the first local runtime hook slice exists through
`before-model-call`, `after-saved-turn`, `MemoryStore.before_model_call()`,
`MemoryStore.after_saved_turn()`, and the Hermes provider wrapper. It proves the
Router/envelope/Keeper candidate loop. The richer `slice seed/run/assert`
fixture now checks corrected memory, deleted memory, professional/personal lane
separation, success/failure loop retrieval, and poisoning quarantine. Full v0.2
now has a local stdlib HTTP API service through `agent-memory serve`; hosted
auth and MCP are still backlog. Runtime scope allow/deny enforcement is
implemented for Router retrieval.
Baseline read-time policy and Router explainability are implemented through
`prompt_envelope.metadata.read_time_policy`, `selection_decisions`,
`agent-memory read-time-policy`, `agent-memory router-runs`,
`agent-memory router-explain`, `/read-time-policy`, `/router-runs`, and
`/router-explain`.
Agent write-policy enforcement is implemented for record, auto-approve,
approve/reject, correct/delete/distrust/expire, outcome, conflict, and
supersession write paths.
The Hermes-style policy/review acceptance path is covered by tests and
`examples/hermes-e2e-demo`.
Queued Keeper jobs and `agent-memory worker --once` are implemented for
background post-turn processing.
Shadow rollout traces are implemented through `agent-memory shadow-turn`,
`agent-memory shadow-traces`, `/shadow-turn`, `/shadow-traces`, and the Hermes
provider wrapper. These traces link Router selections and Keeper proposals with
`write_policy=propose_only` so real Hermes traffic can be reviewed before live
memory writes.
Baseline shadow evals are implemented through `agent-memory shadow-eval`,
`agent-memory shadow-evals`, `/shadow-eval`, `/shadow-evals`, and the Hermes
provider wrapper. They turn reviewed traces into stored pass/fail checks for
branch selection, candidate text, source IDs, token budget, and access mode.
Conflict and supersession records are implemented through `agent-memory
conflict`, `agent-memory supersede`, `/conflict/record`, `/conflict/list`, and
`/supersede`. Superseded memory is suppressed from active retrieval and graph
export while the resolved relationship remains auditable.
Outcome records and outcome packs are implemented for success/failure loop
planning.
Delete, distrust, and expire now suppress retrieval and active graph export.
Corrections now record `memory_revisions`; `agent-memory revisions` and
`agent-memory rollback` expose operator-visible rollback.
The formal contract is exposed through `agent-memory contract` and
`/contract`; the deterministic full-memory gate is exposed through
`agent-memory acceptance seed/run/assert` and `/acceptance/seed`,
`/acceptance/run`, `/acceptance/assert`.

## v0.3: Adapters

Goal: let agent frameworks use the kernel without copy-pasting logic.

Implemented now:

- Hermes provider adapter;
- simple HTTP API;
- OpenAI-compatible lightweight extractor adapter;
- local deterministic semantic reranker.

Planned:

- MCP server;
- file-based vault adapter;
- optional provider embeddings;
- provider-backed semantic reranker for larger corpora.

## v0.4: Review UI

Goal: make memory maintenance practical for non-technical users.

Planned:

- review inbox;
- approve/reject/correct flows;
- source preview;
- graph browser;
- conflict warnings;
- export controls.

## v1.0: Stable Memory Contract

Goal: stable interfaces for external users.

Requirements:

- documented migration path;
- stable schema;
- stable provider interface;
- stable Memory Contract and passing acceptance harness;
- governed retrieval and lifecycle invalidation gates;
- reference orchestration loop with real before/after memory behavior;
- production eval traces proving memory improves real agent behavior;
- inspect/edit/delete/distrust/export control surface;
- defined operational failure and migration behavior;
- security review;
- import/export format;
- production examples.
