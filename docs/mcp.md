# MCP Server

Agent Memory Kernel includes a dependency-free stdio MCP server for agents that
should not call Python imports, shell commands, or the HTTP API directly.

Run it with either command:

```bash
agent-memory mcp --db .memory/memory.db
agent-memory-mcp --db .memory/memory.db
```

During development:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.mcp_server --db /tmp/amk-mcp.db
```

For rollout guidance, see [production-rollout.md](production-rollout.md).
The repository ships a stdio MCP server, not a hosted remote MCP service. Run
the stdio server on the same host as the agent runtime or pair it with the
local HTTP API behind a private tunnel or authenticated proxy.

## Transport

The server uses newline-delimited JSON-RPC over stdio. It implements:

- `initialize`
- `ping`
- `tools/list`
- `tools/call`

The server advertises protocol version `2025-06-18` and returns both text
content and `structuredContent` for successful tool calls.

## Tools

Runtime tools:

- `memory_before_turn`: orchestrator hook that retrieves memory and builds
  prompt context before an agent turn.
- `memory_build_prompt_context`: return the final agent-ready prompt envelope.
- `memory_before_model_call`: build the prompt envelope before the main model.
- `memory_prompt_budget`: resolve the effective memory token budget for a
  model/provider family before building the prompt.
- `memory_after_turn`: orchestrator hook that saves the exchange and runs or
  queues Keeper after an agent turn.
- `memory_after_saved_turn`: save the exchange and run or queue Keeper.
- `memory_worker_run`: process one batch of queued Keeper jobs. For a
  long-running polling process, run the CLI worker with `--daemon`.
- `memory_keeper_eval`: run offline Keeper extraction regression evals.
- `memory_changes`: inspect what Keeper changed after a saved turn.
- `memory_capability_check`: report effective read/write permissions before
  delegating work to an agent.
- `memory_derived_invalidations`: inspect derived surfaces refreshed or
  invalidated after correction, rollback, delete, distrust, expire, or
  supersede.
- `memory_derived_lineage`: explain source, item, graph, outcome, audit, and
  invalidation surface dependencies for derived memory.
- `memory_operational_status`: report local memory health, required table
  checks, storage size warning, and configured no-memory/failed-Keeper fallback
  behavior.
- `memory_observability`: summarize Router runs, Keeper jobs, LLM usage
  tokens/cost, and local latency SLO alerts for memory operations.
- `memory_quality_report`: report Router feedback coverage, helpful/harmful
  feedback, shadow trace eval pass rate, Keeper job health, and quality gates.
- `memory_billing_reconcile`: reconcile recorded memory LLM usage costs with
  expected billing and flag suspicious usage rows.
- `memory_worker_status`: report queued, stale, and failed Keeper worker jobs
  for supervisors and operators.
- `memory_outcome_compare`: compare success/failure outcome records and return
  reusable loop lessons, failure anti-patterns, and recommended next actions.
- `memory_migration_status`: check SQLite schema version, required tables and
  columns, and migration compatibility.
- `memory_backup_database`: create a SQLite backup of the memory database.
- `memory_restore_database`: restore a SQLite backup into a target database
  path.
- `memory_restore_drill`: run a backup/restore drill, migration checks, and
  optional restored-memory probe query.

Retrieval tools:

- `memory_retrieve_context`: return expanded graph branches plus the tree
  supplement.
- `memory_search`: search active memory with provenance.
- `memory_context_pack`: return compact context text.
- `memory_tree_pack`: return the expanded Memory Tree Supplement.
- `memory_current_best`: explain current-best conflict resolution and
  conservative near-duplicate heuristics.
- `memory_conflict_detect`: detect likely active-memory conflicts and
  optionally record open conflict records.
- `memory_router_explain`: explain a stored Router run.

Operator and graph tools:

- `memory_ingest_graph`: ingest Keeper-style graph updates as reviewable memory.
- `memory_remember`: record a candidate or policy-approved memory.
- `memory_review_list`: list review candidates.
- `memory_review_inbox`: show review candidates with source context, risk
  flags, inline possible-conflict warnings, graph preview, audit trail, and
  operator handles.
- `memory_review_batch`: approve or reject multiple review candidates with
  dry-run and per-item results.
- `memory_review_approve`: approve a candidate.
- `memory_review_reject`: reject a candidate.
- `memory_notifications_list`: list operator notifications for review,
  export, and maintenance actions; supports assignment and SLA filters.
- `memory_notification_escalations`: list SLA-driven escalation candidates
  without sending notification transports.
- `memory_notifications_transport`: build webhook, email, or push payloads for
  external notification delivery.
- `memory_notification_assign`: assign a notification to a reviewer or
  operator.
- `memory_notification_ack`: acknowledge a notification without resolving it.
- `memory_notification_resolve`: resolve a notification after action is done.
- `memory_correct`: correct active memory text.
- `memory_lifecycle_batch`: dry-run or apply batch correct/delete/distrust/expire
  operations for active memories.
- `memory_delete`: soft-delete active memory and suppress retrieval.
- `memory_distrust`: keep memory for audit but suppress retrieval.
- `memory_expire`: expire active memory and suppress retrieval.
- `memory_conformance_certify`: run public conformance scenarios and return an
  adapter compatibility badge report for CI or README output.
- `memory_conformance_registry_entry`: emit a compact public adapter registry
  entry with adapter metadata, badge, certification summary, and publication
  readiness.
- `memory_prompt_format_certify`: certify provider prompt formatters against
  prompt-boundary invariants for OpenAI, Anthropic, Gemini/Google, and local
  prompt shapes, including hostile memory, tool-output, assistant-guess, and
  secret-like red-team fixtures.
- `memory_embedding_certify`: certify the provider-neutral embedding/rerank
  contract and deterministic local fallback.
- `memory_brain_style_certify`: certify that graph-derived style hints are
  guarded, visible in metadata, suppressible, and omitted when memory access is
  denied.
- `memory_identity_delegation`: report tenant, actor, explicit delegation,
  implicit local allow, wildcard-policy risk, and recommended policy commands.
- `memory_export_control`: preview export policy, aggregate scope counts, and
  risk flags before memory leaves the store. Accepts `redaction_profile`
  (`full`, `safe`, or `metadata`) so operators can preview the intended export
  mode.
- `memory_export_profile`: export the profile, memory tree, graph, evidence,
  outcomes, and related metadata. Accepts `redaction_profile` (`full`, `safe`,
  or `metadata`) to preserve structure while redacting content-bearing fields.
- `memory_export_custody`: check export policy, sensitive approval,
  passphrase-environment configuration, off-host artifact custody, retention,
  and the zero-secret-storage guarantee before an export leaves the local
  machine.
- `memory_vault_export`: export active memory as a machine-readable local
  markdown vault with JSON frontmatter and governed redaction.
- `memory_vault_import`: import a machine-readable local markdown vault through
  the normal review lifecycle, optionally auto-approving when write policy
  allows it.
- `memory_export_encrypted_profile`: export the governed profile payload as an
  authenticated `encrypted-export-v0.1` envelope using a passphrase from a
  configured environment variable.
- `memory_import_encrypted_profile`: import an authenticated encrypted profile
  envelope after decrypting it with the configured passphrase environment
  variable.
- `memory_export_approval_request`: request one-time approval for a sensitive
  full export.
- `memory_export_approval_list`: list sensitive export approval requests.
- `memory_export_approval_approve`: approve a pending sensitive export request.
- `memory_export_approval_reject`: reject a pending sensitive export request.
- `memory_export_retention_list`: list recorded exports and retention status.
- `memory_export_retention_enforce`: mark export records expired after
  `expires_at`.
- `memory_export_retention_purge`: mark an export record purged after external
  artifact cleanup.
- `memory_graph_nodes`: list active graph nodes.
- `memory_graph_edges`: list active graph edges.
- `memory_graph_browser`: return graph nodes, edges, and source previews in one
  browser-ready payload.
- `memory_graph_optimize`: run graph maintenance passes, including
  `consolidate_duplicates` for safe alias-node compaction and `decay_stale`
  for non-mutating stale-node review findings.

## Agent Pattern

For a normal agent loop:

1. Call `memory_capability_check` when the orchestrator needs to verify a
   delegated agent's memory rights.
2. Call `memory_before_turn` with the current user request.
3. Inject the returned prompt envelope or `MEMORY_TREE_SUPPLEMENT` into the
   main model prompt.
4. After the model answers, call `memory_after_turn`.
5. If Keeper was queued, call `memory_worker_run` out of band.
6. Use `memory_changes` to audit what was saved or proposed.
7. Use `memory_review_inbox` and `memory_review_batch` to approve, reject,
   correct, delete, distrust, or expire memory through explicit operator
   handles.

This keeps the main agent from scanning the entire graph. The Router chooses
relevant branches, and Keeper updates memory after the response.
