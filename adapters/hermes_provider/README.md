# Hermes Provider Adapter

This folder is a starter adapter boundary for Hermes.

The current implementation is intentionally thin: Hermes should call the kernel
instead of duplicating memory storage logic.

## Responsibilities

The adapter should:

- run `shadow_turn()` during rollout to collect reviewable Router/Keeper traces;
- run `evaluate_shadow_trace()` after review to keep regression fixtures;
- call `before_model_call()` before a main agent/model answers;
- call `after_saved_turn()` after the exchange is persisted;
- build Memory Tree Packs before an agent plans work;
- build full context builder packs for tasks that need profile, summaries,
  recent messages, and graph branches together;
- use compact context packs for small tasks;
- record raw conversation turns;
- record session summaries, decisions, attempts, successes, and failures;
- inspect graph nodes and Keeper runs while debugging retrieval;
- record conflicts or supersede stale memory when newer user/project truth wins;
- record structured loop outcomes and retrieve outcome packs before planning;
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
trace = provider.shadow_turn(
    "planning SEO content refresh loop for demo-site",
    scope="professional",
    thread_id="seo-demo",
    user_text="Plan the next refresh loop.",
    assistant_text="Reuse the prior successful refresh pattern.",
)
```

Use shadow traces first. They connect a Router run and Keeper proposal with
`write_policy=propose_only`, so Hermes can review real traffic without
auto-approving new active memory.

After review, preserve the expected behavior:

```python
provider.evaluate_shadow_trace(
    trace["shadow_trace_id"],
    expected={
        "expected_branch_labels": ["demo-site"],
        "expected_candidate_text": ["successful refresh pattern"],
        "require_candidates": True,
    },
)
```

Production runtime should then use `before_model_call()` to get the prompt
envelope and `after_saved_turn()` to save the exchange and create reviewable
Keeper candidates.

When a later decision replaces an older memory, call `supersede_memory()` rather
than leaving both facts active. If the winner is unclear, call
`record_memory_conflict()` and leave the conflict open for review.

For SEO or agent loops, record measured outcomes:

```python
provider.record_outcome(
    project="demo-site",
    outcome_status="success",
    action="Updated search intent and internal links.",
    result="Organic clicks improved.",
    lesson="Refresh intent and links together.",
    next_recommendation="Reuse this pattern on similar pages.",
    auto_approve=True,
)

pack = provider.outcome_pack("demo-site")
```
