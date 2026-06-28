# Hermes Provider Adapter

This folder is a starter adapter boundary for Hermes.

The current implementation is intentionally thin: Hermes should call the kernel
instead of duplicating memory storage logic.

## Responsibilities

The adapter should:

- expose the Memory Contract and acceptance gate as a preflight before live
  memory rollout;
- expose the conformance spec and suite as the public adapter-compatibility
  gate;
- run `shadow_turn()` during rollout to collect reviewable Router/Keeper traces;
- run `evaluate_shadow_trace()` after review to keep regression fixtures;
- expose `before_agent_turn()` and `after_agent_turn()` as the high-level
  `MemoryOrchestrator` lifecycle hooks;
- call `before_model_call()` before a main agent/model answers;
- call `after_saved_turn()` after the exchange is persisted;
- expose `retrieve_context()`, `build_prompt_context()`,
  `keeper_analyze_turn()`, and `ingest_graph()` for service-style
  orchestration;
- accept a configured `LLMKeeperExtractor` or `OpenAIExtractor` so Hermes can
  run Keeper extraction through a low-cost model while preserving the memory
  contract;
- build Memory Tree Packs before an agent plans work;
- build full context builder packs for tasks that need profile, summaries,
  recent messages, and graph branches together;
- use compact context packs for small tasks;
- expose `read_time_policy()`, `router_runs()`, and `explain_router_run()` for
  prompt-facing memory audit;
- expose `current_best_report()` so Hermes can inspect resolved winners,
  suppressed loser memories, and unresolved conflicts before prompt injection;
- expose `memory_changes()` so Hermes can inspect what Keeper changed after a
  saved turn and why;
- expose `review_inbox()` so Hermes can show source previews, risk flags,
  graph previews, audit trail, and operator action handles;
- expose `notifications()`, `assign_notification()`, `ack_notification()`,
  and `resolve_notification()` so Hermes can show one operator queue across
  review, export approval, and retention cleanup;
- expose `review_batch()` so Hermes can approve or reject multiple candidates
  with dry-run and per-item results;
- expose `batch_memory_lifecycle()` so Hermes can dry-run and apply batch
  correct/delete/distrust/expire operations for active memories;
- expose `graph_browser()` so Hermes can render or inspect graph nodes, edges,
  and source previews without multiple round trips;
- expose `capability_report()` so Hermes can inspect read/write/export/delete
  permissions before delegating work to an agent;
- expose `export_control_report()` so Hermes can preview export policy,
  aggregate scope counts, and risk flags before memory leaves the store;
- expose `export_profile(..., redaction_profile="safe")` when Hermes needs to
  share memory structure without exporting content-bearing fields;
- expose `export_encrypted_profile()`, `decrypt_encrypted_export()`, and
  `import_encrypted_profile()` for portable encrypted profile handoff;
- expose `request_export_approval()`, `export_approvals()`,
  `approve_export_approval()`, and `reject_export_approval()` for one-time full
  exports that include personal or secret active memory;
- expose `export_retention_records()`, `enforce_export_retention()`, and
  `purge_export_record()` so Hermes can inspect and expire export artifacts;
- expose `derived_invalidations()` so Hermes can audit stale derived surfaces
  after correction, rollback, delete, distrust, expire, or supersede;
- expose `operational_status()` so Hermes can check local memory health and
  fallback behavior before routing critical work through memory;
- expose `migration_status()`, `backup_database()`, and `restore_database()`
  for local SQLite recovery and migration compatibility checks;
- record Router usefulness feedback and inspect `memory_quality_report()`;
- inspect `observability_report()` for Router token estimates, Keeper job
  health, and LLM usage tokens/cost;
- record raw conversation turns;
- record session summaries, decisions, attempts, successes, and failures;
- inspect graph nodes and Keeper runs while debugging retrieval;
- inspect `brain_style_append()` while debugging guarded Digital Brain prompt
  influence;
- disable graph-derived style hints per call when orchestration policy requires
  memory content without style influence;
- record conflicts or supersede stale memory when newer user/project truth wins;
- record structured loop outcomes and retrieve outcome packs before planning;
- configure write policies so agents can propose memory without auto-approving
  or mutating durable memory outside their authority;
- configure read policies so agents cannot inject scopes they are not allowed
  to see;
- leave durable promotion to policy or review;
- expose pending memory review and active-memory lifecycle controls to the user
  or operator.

## Non-Responsibilities

The adapter should not:

- silently approve untrusted model output;
- rewrite memory without audit;
- hide source provenance;
- store private project-specific logic in the public kernel.

See `hermes_provider.py` for the minimal provider shape.

Preflight the shared contract before enabling live memory:

```bash
agent-memory contract assert
agent-memory acceptance seed --db .memory/hermes-memory.db
agent-memory acceptance assert --db .memory/hermes-memory.db
agent-memory conformance seed --db .memory/hermes-memory.db
agent-memory conformance assert --db .memory/hermes-memory.db
```

This proves the deterministic minimum: selected memory beats no-memory,
personal memory does not leak into professional prompts, unsafe memory stays
out, source ids are logged, rollback affects retrieval, Keeper writes remain
reviewable, and write policy blocks unauthorized approval.

The conformance commands are the public adapter-compatibility gate. They verify
professional memory injection, personal-lane isolation, resolved conflict
suppression, deleted-memory absence, unsafe-memory absence, and reviewable
Keeper writes through the same runtime surfaces external adapters use. The gate
also checks that repeated post-turn Keeper calls are idempotent.

Hermes can pass a configured extractor into the provider:

```python
from agent_memory_kernel.extractors import LLMKeeperExtractor


def cheap_model_complete(request: dict):
    return provider_client.responses.create(**request)

provider = HermesMemoryProvider(
    ".memory/hermes-memory.db",
    extractor=LLMKeeperExtractor(cheap_model_complete, model="cheap-memory-model"),
)
```

`OpenAIExtractor` remains available for direct OpenAI-compatible clients. Use
`LLMKeeperExtractor` when Hermes wants the versioned Keeper schema and strict
contract tests.

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

Before production writes, set explicit authority for each agent role:

```python
provider.set_write_policy(
    agent_id="writer",
    scope="professional",
    action="auto_approve",
    decision="deny",
    reason="writer proposes memory; reviewer approves",
)
```

Set read/injection authority for scopes that should not enter an agent prompt:

```python
provider.set_read_policy(
    agent_id="writer",
    scope="personal",
    action="inject",
    decision="deny",
    reason="writer uses professional memory only",
)
```

Check the effective capability matrix before starting an agent:

```python
provider.capability_report(actor="writer", scope="professional")
provider.export_control_report(
    actor="writer",
    scope="professional",
    redaction_profile="safe",
)
provider.export_profile(scope="professional", redaction_profile="safe")
encrypted = provider.export_encrypted_profile(
    passphrase="change-me",
    scope="professional",
    redaction_profile="safe",
)
restored = provider.decrypt_encrypted_export(encrypted, passphrase="change-me")
```

Export redaction profiles are explicit:

- `full`: includes exportable memory content after policy checks.
- `safe`: redacts content-bearing fields while preserving IDs, counts, scopes,
  and graph shape.
- `metadata`: redacts content plus additional human-readable metadata labels for
  safer sharing of structure.

Full exports that include personal or secret active memory require a one-time
approval id. Use `request_export_approval()`, approve it through an operator
role, then pass `approval_id` to `export_profile()`.
Every export returns retention metadata. Use `export_retention_records()` to
inspect active/expired/purged records and `enforce_export_retention()` from a
maintenance worker.
Encrypted profile export wraps the governed profile payload in an authenticated
`encrypted-export-v0.1` envelope, preserving retention metadata without leaving
the plaintext memory payload in the artifact.

After review, preserve the expected behavior:

```python
provider.review_inbox(status="open", scope="professional")
provider.notifications(status="open", scope="professional")
provider.notifications(status="open", sla_status="overdue")
provider.assign_notification("ntf_xxxxxxxxxxxxxxxx", assigned_to="reviewer-a", actor="lead")
provider.review_batch(action="approve", candidate_ids=["cand_a", "cand_b"], actor="reviewer", dry_run=True)
provider.batch_memory_lifecycle(
    [{"action": "delete", "memory_id": "mem_xxxxxxxxxxxxxxxx"}],
    actor="reviewer",
    dry_run=True,
)
provider.graph_browser(scope="professional", limit=25)
provider.approve_candidate("cand_xxxxxxxxxxxxxxxx", actor="reviewer")
provider.correct_memory("mem_xxxxxxxxxxxxxxxx", "Corrected memory text", actor="reviewer")

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

After `after_saved_turn()`, inspect the returned Keeper job:

```python
after = provider.after_saved_turn(
    thread_id="seo-demo",
    scope="professional",
    user_text="Plan the next refresh loop.",
    assistant_text="Reuse the prior successful refresh pattern.",
)

changes = provider.memory_changes(keeper_job_id=after["keeper_job_id"])
```

The change report is the operator-facing audit of saved turns, Keeper event,
candidates, promoted memories, affected graph/context surfaces, review or
lifecycle handles, and audit trail.

When a later decision replaces an older memory, call `supersede_memory()` rather
than leaving both facts active. If the winner is unclear, call
`record_memory_conflict()` and leave the conflict open for review.
Use `current_best_report(query, scope=...)` to verify which memory will be
selected for a live prompt when a resolved conflict has a winner.

If a correction was wrong, inspect `memory_revisions()` and call
`rollback_memory()` instead of overwriting memory silently. Rollback restores
the previous text while preserving the correction and rollback audit trail.

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
