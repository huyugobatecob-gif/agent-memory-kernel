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

- `memory_before_model_call`: build the prompt envelope before the main model.
- `memory_after_saved_turn`: save the exchange and run or queue Keeper.
- `memory_worker_run`: process queued Keeper jobs.
- `memory_changes`: inspect what Keeper changed after a saved turn.

Retrieval tools:

- `memory_search`: search active memory with provenance.
- `memory_context_pack`: return compact context text.
- `memory_tree_pack`: return the expanded Memory Tree Supplement.
- `memory_current_best`: explain current-best conflict resolution.
- `memory_router_explain`: explain a stored Router run.

Operator and graph tools:

- `memory_remember`: record a candidate or policy-approved memory.
- `memory_review_list`: list review candidates.
- `memory_review_approve`: approve a candidate.
- `memory_review_reject`: reject a candidate.
- `memory_graph_nodes`: list active graph nodes.
- `memory_graph_edges`: list active graph edges.

## Agent Pattern

For a normal agent loop:

1. Call `memory_before_model_call` with the current user request.
2. Inject the returned prompt envelope or `MEMORY_TREE_SUPPLEMENT` into the
   main model prompt.
3. After the model answers, call `memory_after_saved_turn`.
4. If Keeper was queued, call `memory_worker_run` out of band.
5. Use `memory_changes` to audit what was saved or proposed.

This keeps the main agent from scanning the entire graph. The Router chooses
relevant branches, and Keeper updates memory after the response.
