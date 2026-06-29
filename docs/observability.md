# Observability And Cost Accounting

The memory kernel records three runtime surfaces that should be watched during
production rollout:

- Router runs: selected branch ids, access decisions, warnings, prompt token
  estimates, wall-clock duration, no-memory fallbacks, agent id, model id,
  thread id, and scope.
- Keeper jobs: saved turns, candidate ids, promoted memory ids, status,
  warnings, wall-clock duration, failed extraction metadata, and audit trail.
- LLM usage stats: provider, model, prompt tokens, completion tokens, total
  tokens, cost, currency, thread id, and scope.

Use the combined report when deciding whether memory is cheap, useful, and
healthy enough to keep enabled for a live agent path:

```bash
agent-memory observability --db .memory/demo.db --scope professional
agent-memory observability --db .memory/demo.db --thread-id seo-demo
agent-memory observability --db .memory/demo.db --router-latency-slo-ms 750 --keeper-latency-slo-ms 2500
agent-memory dashboard --db .memory/demo.db --scope professional --summary-only
agent-memory billing-reconcile --db .memory/demo.db --scope professional --expected-cost 0.25 --tolerance 0.01
```

The same report is exposed through:

- HTTP: `POST /observability`
- MCP: `memory_observability`
- Python adapter wrapper: `observability_report()`

Use `dashboard` when an operator or supervising agent needs one compact view
across local health, observability, billing, worker queue, recovery schedules,
and open notifications:

- CLI: `agent-memory dashboard`
- HTTP: `POST /operations/dashboard`
- MCP: `memory_operations_dashboard`
- Python adapter wrapper: `operations_dashboard()`

The report returns:

- `router.run_count`, `warning_run_count`, `no_memory_run_count`,
  `selected_branch_count`, `average_token_estimate`, and
  `average_duration_ms`;
- recent Router runs with selected branch ids, prompt token estimate, and
  `duration_ms`;
- `keeper.status_counts`, warning jobs, candidate count, promoted memory count,
  `average_duration_ms`, and recent Keeper jobs;
- `slo.status`, latency thresholds, breach counts, and local warning alerts for
  Router or Keeper runs that exceed configured thresholds;
- usage totals and cost grouped by provider/model and currency.

For provider billing checks, use `billing-reconcile`. It reads the same
recorded `llm_usage_stats` rows and returns provider/model/currency totals,
cost-per-1K-token summaries, expected-cost deltas, suspicious usage rows, and
latest usage samples. It is exposed through:

- CLI: `agent-memory billing-reconcile`
- HTTP: `POST /billing/reconcile`
- MCP: `memory_billing_reconcile`
- Python adapter wrapper: `billing_reconciliation_report()`

Provider invoice line items can be imported from JSON and then used as the
expected billing amount when `billing-reconcile` is called without
`--expected-cost`:

```json
{
  "invoice_id": "inv_2026_06",
  "provider": "openai",
  "currency": "USD",
  "period_start": "2026-06-01T00:00:00+00:00",
  "period_end": "2026-06-30T23:59:59+00:00",
  "line_items": [
    {
      "model": "keeper-mini",
      "scope": "professional",
      "thread_id": "seo-demo",
      "total_tokens": 1200,
      "amount": 0.25
    }
  ]
}
```

Invoice ingestion surfaces:

- CLI: `agent-memory billing-invoice import --file provider-invoice.json`
- CLI: `agent-memory billing-invoice list --provider openai`
- HTTP: `POST /billing/invoice/import`, `POST /billing/invoice/list`
- MCP: `memory_billing_invoice_import`, `memory_billing_invoice_list`
- Python adapter wrappers: `import_billing_invoice()`,
  `billing_invoice_items()`

This is a baseline local report with local latency SLO checks, a machine-readable
dashboard, and recorded-cost reconciliation. Production deployments should
still add supervisor metrics, live provider invoice fetchers, hosted dashboard
publishing, managed alerts, and hosted retention policy enforcement beyond the
local export retention ledger.
