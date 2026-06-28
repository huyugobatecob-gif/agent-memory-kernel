# Hermes Provider Adapter

This folder is a starter adapter boundary for Hermes.

The current implementation is intentionally thin: Hermes should call the kernel
instead of duplicating memory storage logic.

## Responsibilities

The adapter should:

- build Memory Tree Packs before an agent plans work;
- build full context builder packs for tasks that need profile, summaries,
  recent messages, and graph branches together;
- use compact context packs for small tasks;
- record raw conversation turns;
- record session summaries, decisions, attempts, successes, and failures;
- inspect graph nodes and Keeper runs while debugging retrieval;
- leave durable promotion to policy or review;
- expose pending memory review to the user or operator.

## Non-Responsibilities

The adapter should not:

- silently approve untrusted model output;
- rewrite memory without audit;
- hide source provenance;
- store private project-specific logic in the public kernel.

See `hermes_provider.py` for the minimal provider shape.

Recommended planning call:

```python
memory = provider.context_builder_pack(
    "planning SEO content refresh loop for demo-site",
    scope="professional",
    thread_id="seo-demo",
)
```

Pass the returned markdown to the agent with the task. After the run, call
`record_turn()` for raw conversation history and `remember()` with a session
summary, outcome, decision, or gotcha.
