# Observability And Cost Accounting

The memory kernel records three runtime surfaces that should be watched during
production rollout:

- Router runs: selected branch ids, access decisions, warnings, prompt token
  estimates, no-memory fallbacks, agent id, model id, thread id, and scope.
- Keeper jobs: saved turns, candidate ids, promoted memory ids, status,
  warnings, failed extraction metadata, and audit trail.
- LLM usage stats: provider, model, prompt tokens, completion tokens, total
  tokens, cost, currency, thread id, and scope.

Use the combined report when deciding whether memory is cheap, useful, and
healthy enough to keep enabled for a live agent path:

```bash
agent-memory observability --db .memory/demo.db --scope professional
agent-memory observability --db .memory/demo.db --thread-id seo-demo
```

The same report is exposed through:

- HTTP: `POST /observability`
- MCP: `memory_observability`
- Python adapter wrapper: `observability_report()`

The report returns:

- `router.run_count`, `warning_run_count`, `no_memory_run_count`,
  `selected_branch_count`, and `average_token_estimate`;
- recent Router runs with selected branch ids and prompt token estimate;
- `keeper.status_counts`, warning jobs, candidate count, promoted memory count,
  and recent Keeper jobs;
- usage totals and cost grouped by provider/model and currency.

This is a baseline local report. Production deployments should still add
supervisor metrics, wall-clock latency, provider billing reconciliation,
dashboards, alerts, and hosted retention policy enforcement beyond the local
export retention ledger.
