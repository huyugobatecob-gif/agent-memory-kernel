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
- `memory_after_turn`: orchestrator hook that saves the exchange and runs or
  queues Keeper after an agent turn.
- `memory_after_saved_turn`: save the exchange and run or queue Keeper.
- `memory_worker_run`: process one batch of queued Keeper jobs. For a
  long-running polling process, run the CLI worker with `--daemon`.
- `memory_changes`: inspect what Keeper changed after a saved turn.
- `memory_capability_check`: report effective read/write permissions before
  delegating work to an agent.
- `memory_derived_invalidations`: inspect derived surfaces refreshed or
  invalidated after correction, rollback, delete, distrust, expire, or
  supersede.
- `memory_operational_status`: report local memory health, required table
  checks, storage size warning, and configured no-memory/failed-Keeper fallback
  behavior.
- `memory_observability`: summarize Router runs, Keeper jobs, and LLM usage
  tokens/cost for memory operations.
- `memory_migration_status`: check SQLite schema version, required tables and
  columns, and migration compatibility.
- `memory_backup_database`: create a SQLite backup of the memory database.
- `memory_restore_database`: restore a SQLite backup into a target database
  path.

Retrieval tools:

- `memory_retrieve_context`: return expanded graph branches plus the tree
  supplement.
- `memory_search`: search active memory with provenance.
- `memory_context_pack`: return compact context text.
- `memory_tree_pack`: return the expanded Memory Tree Supplement.
- `memory_current_best`: explain current-best conflict resolution.
- `memory_router_explain`: explain a stored Router run.

Operator and graph tools:

- `memory_ingest_graph`: ingest Keeper-style graph updates as reviewable memory.
- `memory_remember`: record a candidate or policy-approved memory.
- `memory_review_list`: list review candidates.
- `memory_review_inbox`: show review candidates with source context, risk
  flags, graph preview, audit trail, and operator handles.
- `memory_review_batch`: approve or reject multiple review candidates with
  dry-run and per-item results.
- `memory_review_approve`: approve a candidate.
- `memory_review_reject`: reject a candidate.
- `memory_correct`: correct active memory text.
- `memory_delete`: soft-delete active memory and suppress retrieval.
- `memory_distrust`: keep memory for audit but suppress retrieval.
- `memory_expire`: expire active memory and suppress retrieval.
- `memory_export_control`: preview export policy, aggregate scope counts, and
  risk flags before memory leaves the store. Accepts `redaction_profile`
  (`full`, `safe`, or `metadata`) so operators can preview the intended export
  mode.
- `memory_export_profile`: export the profile, memory tree, graph, evidence,
  outcomes, and related metadata. Accepts `redaction_profile` (`full`, `safe`,
  or `metadata`) to preserve structure while redacting content-bearing fields.
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
