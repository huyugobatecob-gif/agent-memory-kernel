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
- Keeper runs, graph command normalization, and graph command audit.
- Light Model semantic analyses.
- Profile notes, project profile metadata, and profile export.
- LLM usage stats.
- Export control previews and export redaction profiles.
- Encrypted profile export/import envelopes.
- Graph groups, optimization runs, and Digital Brain calibration.
- Guarded Digital Brain style append in prompt envelopes.
- Context packs.
- Memory Tree Packs.
- Context builder packs.
- Agent write-policy enforcement.
- Memory revision history and rollback.
- Formal Memory Contract and deterministic acceptance harness.
- Dependency-free semantic reranking for Memory Tree retrieval.
- Versioned LLM Keeper extraction contract.
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
- production memory quality evals beyond baseline usefulness feedback;
- versioned conformance spec with golden conversation traces and adapter
  compatibility tests;
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
`MemoryStore.after_saved_turn()`, `MemoryOrchestrator`, and the Hermes provider
wrapper. It proves the Router/envelope/Keeper candidate loop and exposes a
single service facade for `before_turn`, `build_prompt_context`,
`retrieve_context`, `record_turn`, `keeper_analyze_turn`, `ingest_graph`, and
`after_turn`. The richer `slice seed/run/assert` fixture now checks corrected
memory, deleted memory, professional/personal lane separation, success/failure
loop retrieval, and poisoning quarantine. Full v0.2 now has a local stdlib HTTP
API service through `agent-memory serve` and a local stdio MCP server; hosted
auth and remote MCP deployment are still backlog. Runtime scope allow/deny
enforcement is implemented for Router retrieval.
Baseline read-time policy and Router explainability are implemented through
`prompt_envelope.metadata.read_time_policy`, `selection_decisions`,
`agent-memory read-time-policy`, `agent-memory router-runs`,
`agent-memory router-explain`, `/read-time-policy`, `/router-runs`, and
`/router-explain`.
Baseline Router usefulness feedback and quality reporting are implemented
through `agent-memory router-feedback`, `agent-memory memory-quality`,
`/router-feedback/record`, `/router-feedback/list`, and `/memory-quality`.
Baseline observability and cost accounting are implemented through
`agent-memory observability`, `/observability`, the Hermes provider wrapper,
and MCP `memory_observability`. The report joins Router selected branches and
prompt token estimates, Keeper status/warnings, and LLM usage tokens/cost.
Production latency, billing reconciliation, dashboards, retention policy, and
alerts are still backlog.
Baseline LLM Keeper extraction is implemented through `LLMKeeperExtractor`,
`keeper-extraction-v0.1`, local schema validation, deterministic fallback, and
candidate extraction metadata. Production Keeper prompt tuning, live provider
configuration, and trace-based quality evals are still backlog.
Baseline graph command normalization is implemented through
`graph-command-v0.1`, `apply_graph_commands`, orchestrator `ingest_graph`,
reviewable proposed commands, approval-time graph mutation, node/edge evidence,
and idempotent graph upserts. Advanced merge/split/consistency heuristics are
still backlog.
Agent write-policy enforcement is implemented for record, auto-approve,
approve/reject, correct/delete/distrust/expire, outcome, conflict, and
supersession write paths.
Agent read-policy enforcement is implemented for prompt-facing memory injection
through `agent-memory read-policy`, `/read-policy/set`, `/read-policy/list`, and
`prompt_envelope.metadata.read_policy`.
Baseline capability/consent reporting is implemented through `agent-memory
capability`, `/capability/check`, the Hermes provider wrapper, and MCP
`memory_capability_check`. Direct search/context/tree-pack and export surfaces
can enforce read/export policy by actor.
Baseline derived-memory invalidation is implemented through `agent-memory
derived-invalidations`, `/derived-invalidations`, the Hermes provider wrapper,
and MCP `memory_derived_invalidations`. Correction, rollback, delete, distrust,
expire, and supersede lifecycle actions record graph/evidence/prompt-pack/export
surfaces that were refreshed or invalidated.
Baseline operational failure handling is implemented through
`operational_status`, `/operational/status`, the Hermes provider wrapper, and
MCP `memory_operational_status`. Prompt retrieval failures return a no-memory
envelope with `metadata.operational_failure`; Keeper extraction failures keep
saved turns and mark the Keeper job failed.
Baseline migration and local recovery are implemented through
`agent-memory migration-status`, `agent-memory backup`, `agent-memory restore`,
`/migration/status`, `/backup`, `/restore`, and MCP recovery tools. Production
SLOs, encrypted off-host backups, restore drills, migration changelogs, worker
supervision, and hosted alerting are still backlog.
Post-turn memory-change inspection is implemented through `agent-memory
memory-changes`, `/memory-changes`, and the Hermes provider wrapper. A Keeper
job report includes saved turns, the Keeper event, candidates, promoted
memories, affected graph/context surfaces, review or lifecycle handles, and
audit trail.
The baseline operator review inbox is implemented through `agent-memory review
inbox`, `/review/inbox`, the Hermes provider wrapper, and MCP
`memory_review_inbox`. It returns candidate source previews, risk flags, graph
previews, inline possible-conflict warnings against active memory, review
history, audit trail, and CLI/HTTP/MCP handles for approve, reject, correct,
delete, distrust, and expire. HTTP and MCP also expose the matching lifecycle
endpoints/tools.
The stdlib HTTP service also exposes baseline browser operator pages at
`/ui/review`, `/ui/graph`, and `/ui/conflicts` for local review, graph
inspection, and conflict scan/record flows. The review page supports individual
and batch approve/reject, dry-run batch preview, and active-memory correction
preview/apply through the lifecycle batch API. The graph page includes node
type/focus links, source/target edge links, and source metadata for evidence
previews.
The baseline operator notification queue is implemented through `agent-memory
notifications`, `/notifications/*`, Hermes notification wrappers, and MCP
`memory_notifications_list` / `memory_notification_assign` /
`memory_notification_ack` / `memory_notification_resolve` /
`memory_notification_escalations`.
Pending/quarantined review candidates, sensitive export approval requests, and
expired export artifacts create open notifications that can be assigned to a
reviewer with optional `due_at`, filtered by computed SLA status, acknowledged,
resolved, surfaced in policy-only escalation reports, or converted into
webhook/email/push payloads through `agent-memory notifications transport`,
`/notifications/transport`, Hermes, and MCP `memory_notifications_transport`.
Baseline batch review is implemented through `agent-memory review batch`,
`/review/batch`, Hermes `review_batch()`, and MCP `memory_review_batch`.
Approve/reject batches support dry-run and per-candidate results.
Baseline active-memory lifecycle batch is implemented through `agent-memory
lifecycle-batch`, `/memory/lifecycle-batch`, Hermes
`batch_memory_lifecycle()`, and MCP `memory_lifecycle_batch`.
Correct/delete/distrust/expire batches support dry-run and per-item results.
Baseline graph browser data is implemented through `agent-memory graph browser`,
`/graph/browser`, Hermes `graph_browser()`, and MCP `memory_graph_browser`.
Nodes and edges include source previews for future UI navigation.
Baseline export governance is implemented through `agent-memory export-control`,
`/export/control`, Hermes `export_control_report()`, and MCP
`memory_export_control`. Export previews return matched policy, aggregate
scope counts, sensitivity/trust breakdowns, denied scopes, and risk flags
without returning memory content.
Baseline export redaction profiles are implemented through
`agent-memory export-profile`, `agent-memory export`, `/export/profile`, Hermes
`export_profile()`, and MCP `memory_export_profile`. The supported profiles are
`full`, `safe`, and `metadata`; safe modes preserve graph/export structure while
replacing content-bearing fields with explicit redaction markers.
Baseline sensitive full-export approval is implemented through `agent-memory
export-approval`, `/export/approval/*`, Hermes export approval wrappers, and MCP
`memory_export_approval_*`. Full exports containing personal or secret active
memory require an approved one-time request; safe/metadata exports remain the
default structure-sharing path.
Baseline export retention is implemented through `agent-memory
export-retention`, `/export/retention/*`, Hermes retention wrappers, and MCP
`memory_export_retention_*`. Real exports are recorded with retention days,
expiry, purge status, and markdown manifests.
Baseline encrypted profile export is implemented through `agent-memory
export-encrypted-profile`, `agent-memory import-encrypted-profile`,
`/export/encrypted-profile`, `/import/encrypted-profile`, Hermes encrypted
export wrappers, and MCP `memory_export_encrypted_profile` /
`memory_import_encrypted_profile`. The local envelope is
`encrypted-export-v0.1`; hosted key management and encrypted off-host backup
recipes are still backlog.
The Hermes-style policy/review acceptance path is covered by tests and
`examples/hermes-e2e-demo`.
Queued Keeper jobs, `agent-memory worker --once`, and `agent-memory worker
--daemon` are implemented for background post-turn processing. Daemon mode can
poll continuously under an external supervisor and supports bounded
`--max-iterations`/`--stop-when-idle` runs for tests and maintenance.
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
conflict`, `agent-memory supersede`, `agent-memory current-best`,
`/conflict/record`, `/conflict/list`, `/conflict/detect`, `/current-best`, and
`/supersede`. `agent-memory conflict detect`, the Hermes provider wrapper, and
MCP `memory_conflict_detect` provide a baseline active-memory conflict detector
with report-only and record-open-conflict modes.
Superseded memory is suppressed from active retrieval and graph export while the
resolved relationship remains auditable. Explicit resolved conflicts also affect
prompt-facing tree retrieval: the winner is selected, the loser is suppressed,
and unresolved conflicts remain visible for review.
Outcome records and outcome packs are implemented for success/failure loop
planning.
Delete, distrust, and expire now suppress retrieval and active graph export.
Corrections now record `memory_revisions`; `agent-memory revisions` and
`agent-memory rollback` expose operator-visible rollback.
The formal contract is exposed through `agent-memory contract` and
`/contract`; the deterministic full-memory gate is exposed through
`agent-memory acceptance seed/run/assert` and `/acceptance/seed`,
`/acceptance/run`, `/acceptance/assert`.
The first public conformance suite is exposed through `agent-memory conformance
spec/seed/run/assert` and `/conformance/spec`, `/conformance/seed`,
`/conformance/run`, `/conformance/assert`. It defines named adapter scenarios
for professional memory injection, personal-lane isolation, current-best
conflict suppression, stored read-policy denial, deleted-memory absence,
unsafe-memory absence, and reviewable/idempotent Keeper writes.

## v0.3: Adapters

Goal: let agent frameworks use the kernel without copy-pasting logic.

Implemented now:

- Hermes provider adapter;
- simple HTTP API;
- dependency-free stdio MCP server;
- OpenAI-compatible lightweight extractor adapter;
- local deterministic semantic reranker.

Planned:

- hosted or remote MCP deployment patterns;
- file-based vault adapter;
- optional provider embeddings;
- provider-backed semantic reranker for larger corpora.

## v0.4: Review UI

Goal: make memory maintenance practical for non-technical users.

Planned:

- deeper graph exploration views;
- richer browser batch editing queues;
- richer conflict-resolution workflows beyond scan/record;
- managed push/email/web delivery beyond local transport payloads;
- hosted key-management and export custody controls.

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
