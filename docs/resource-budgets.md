# Resource Budgets

The v0.1.0 alpha should make bounded, honest local-first resource claims. It
does not claim production-scale hosted retrieval, ANN indexing, or provider
reranking performance.

## Current Evidence

The current deterministic evidence is bounded prompt selection, not a broad
benchmark suite:

- conformance scenario `golden_trace_large_history_prompt_is_bounded`;
- prompt-budget metadata in `before-model-call`;
- Router selection and truncation metadata;
- local observability duration fields;
- `prompt-budget` command for model-family memory budgets.

Run:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance seed --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli prompt-budget --db /tmp/amk-conformance.db --model-id local --token-budget 12000
```

## Soft v0.1.0 Targets

These are operator targets, not contractual guarantees:

| Area | v0.1.0 target |
| --- | --- |
| Prompt injection | bounded by requested branch limit and token budget. |
| Retrieval | deterministic local selection with audit reasons. |
| Export/import | suitable for local profile-sized stores. |
| Backup/restore | suitable for local SQLite stores and restore drills. |
| Provider calls | not required for conformance or quickstart. |

## Explicit Non-Goals

- ANN/vector indexes as required infrastructure.
- Live embedding provider certification as a local v0.1.0 blocker.
- Hosted multi-tenant performance guarantees.
- Managed sync or distributed consistency.
- Cloud storage latency guarantees.

## Post-v0.1.0 Benchmark Backlog

Before making stronger performance claims, add repeatable fixtures for:

- retrieval latency across larger local stores;
- prompt-build latency under different branch/token budgets;
- export and import size/time for representative bundles;
- backup/restore drill duration;
- memory-quality report duration;
- optional provider reranker latency after policy filtering.
