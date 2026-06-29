# Runtime Contract

This contract defines the live memory loop. It is the boundary between an
orchestrator, the memory kernel, and any main model provider.

The core invariant:

```text
before_model_call -> selected memory context -> main model call
after_saved_turn  -> keeper analysis        -> graph update
```

The main model must never scan the full memory graph. It receives only a
selected, policy-filtered prompt envelope.

## Actors

- `orchestrator`: an agent runtime that receives user tasks and calls
  models.
- `memory_kernel`: this repository. It owns storage, retrieval, review,
  lifecycle, and graph mutation.
- `router`: the lightweight read path that selects relevant memory before the
  main model answers.
- `keeper`: the lightweight write path that extracts memory after a saved turn.
- `main_model`: the stateless or mostly stateless model that answers the user.

## Required Hooks

### `before_model_call`

Called before every non-incognito main model call.

Input:

```json
{
  "thread_id": "seo-demo",
  "scope": "professional",
  "user_id": "user_default",
  "agent_id": "writer",
  "model_id": "gpt-4.1-mini",
  "query": "Plan the next SEO loop",
  "mode": "planning",
  "token_budget": 12000,
  "requested_lanes": ["professional"],
  "enable_brain_style": true,
  "metadata": {}
}
```

Output:

```json
{
  "prompt_envelope": {},
  "router_run_id": "router_...",
  "selected_branch_ids": ["node_..."],
  "access_decisions": [],
  "warnings": []
}
```

Required behavior:

- choose lanes from request, thread, project, and agent policy;
- retrieve summaries, recent messages, active memories, graph nodes, graph
  neighbors, and raw provenance;
- enforce access control before anything enters the prompt;
- allow orchestration policy to suppress graph-derived style influence while
  still retrieving allowed memory;
- return expanded node content, not only tags;
- resolve the requested token budget against the target model profile and store
  the requested/effective values in prompt metadata;
- fit the output to the effective token budget;
- record why each branch was selected or skipped;
- fail closed for permission, secret, and quarantine violations;
- degrade to no-memory mode when retrieval fails, unless the task explicitly
  requires memory.

### `after_saved_turn`

Called after the user/assistant exchange is persisted.

Input:

```json
{
  "thread_id": "seo-demo",
  "scope": "professional",
  "turn_id": "turn_...",
  "user_id": "user_default",
  "agent_id": "writer",
  "model_id": "gpt-4.1-mini",
  "user_text": "Use the successful content refresh pattern.",
  "assistant_text": "I will reuse the prior pattern...",
  "metadata": {}
}
```

Output:

```json
{
  "keeper_job_id": "job_...",
  "mode": "sync_or_queued",
  "status": "queued"
}
```

Required behavior:

- store the raw exchange before extraction;
- run Keeper synchronously only when configured to do so;
- otherwise enqueue a retryable Keeper job;
- record model, token, cost, and source turn metadata;
- never let assistant guesses become trusted facts without policy or review;
- never promote untrusted external content directly into active rules;
- record extraction failures as audit events.

### `shadow_turn`

Called during rollout before granting production write authority.

Input:

```json
{
  "thread_id": "seo-demo",
  "scope": "professional",
  "user_id": "user_default",
  "agent_id": "writer",
  "model_id": "gpt-4.1-mini",
  "query": "Plan the next SEO loop",
  "user_text": "Plan the next SEO loop",
  "assistant_text": "Reuse the prior successful refresh pattern.",
  "keeper_mode": "sync",
  "metadata": {}
}
```

Output:

```json
{
  "shadow_trace_id": "trace_...",
  "write_policy": "propose_only",
  "router_run_id": "router_...",
  "keeper_job_id": "kjob_...",
  "selected_branch_ids": ["node_..."],
  "candidate_ids": ["cand_..."],
  "warnings": []
}
```

Required behavior:

- call the same Router path as `before_model_call`;
- call the same Keeper path as `after_saved_turn`;
- force `auto_approve=false`;
- record one trace that links Router decisions, selected branches, saved turns,
  Keeper job, candidate IDs, warnings, and token metadata;
- make the trace listable for human review and future eval fixtures;
- never promote candidates into active memory automatically.

### `evaluate_shadow_trace`

Called after a human or QA process reviews a shadow trace.

Input:

```json
{
  "shadow_trace_id": "trace_...",
  "expected": {
    "expected_branch_labels": ["demo-site"],
    "forbidden_branch_labels": ["personal"],
    "expected_candidate_text": ["successful refresh pattern"],
    "max_token_estimate": 4000,
    "require_candidates": true,
    "require_memory_allowed": true
  },
  "actor": "reviewer"
}
```

Output:

```json
{
  "eval_id": "eval_...",
  "shadow_trace_id": "trace_...",
  "status": "pass",
  "score": 1.0,
  "checks": [],
  "findings": []
}
```

Required behavior:

- compare selected branch IDs and labels with expected/forbidden branches;
- compare Keeper candidate text with expected/forbidden snippets;
- check selected source IDs, token budget, candidate presence, and access mode
  when requested;
- store pass/fail checks and findings so the trace becomes a repeatable
  regression fixture.

### `record_router_feedback`

Called after an operator, QA process, or supervising agent reviews whether
selected memory helped the main model.

Input:

```json
{
  "router_run_id": "router_...",
  "memory_id": "mem_...",
  "branch_id": "gnode_...",
  "rating": "helpful",
  "score": 1.0,
  "actor": "reviewer",
  "reason": "selected memory grounded the plan"
}
```

Ratings:

- `helpful`: selected memory improved the answer or plan.
- `neutral`: selected memory was acceptable but not decisive.
- `ignored`: selected memory was present but not used.
- `missing`: the right memory was absent from the prompt.
- `harmful`: selected memory caused confusion, stale context, or wrong action.

Required behavior:

- never mutate active memory automatically from feedback alone;
- link feedback to the Router run and optional memory/branch id;
- make feedback listable and auditable;
- aggregate quality signals by scope for Router and memory-quality evals;
- use prior feedback only as a bounded ranking signal for candidates already
  found by text, graph, semantic, or neighbor retrieval;
- expose `router_feedback_signal` in selection policy factors whenever
  feedback exists for a memory.

## Router Contract

Router inputs:

- current query;
- thread id and recent context;
- requested lanes and project;
- allowed identity and access scopes;
- token budget;
- graph snapshot;
- retrieval mode.

Router output:

```json
{
  "supplement": "<<< MEMORY_TREE_SUPPLEMENT ... >>>",
  "branches": [
    {
      "branch_id": "node_...",
      "label": "project / client-site",
      "why_selected": "query matched project and recent successful outcome",
      "score": 0.82,
      "node_summary": "...",
      "expanded_content": "...",
      "evidence_ids": ["ev_..."],
      "source_refs": ["turn_..."],
      "selection_decisions": [
        {
          "memory_id": "mem_...",
          "decision": "selected",
          "rank": 1,
          "score": 95.2,
          "why": ["active memory text match"],
          "policy_factors": {
            "kind": "outcome",
            "prompt_role": "outcome evidence",
            "scope": "professional",
            "source_trust": "trusted",
            "sensitivity": "internal",
            "conflict_status": {"status": "none"},
            "outcome_signal": {"status": "success", "score": 0.8}
          }
        }
      ]
    }
  ],
  "skipped": [
    {
      "branch_id": "node_...",
      "reason": "permission_denied"
    }
  ],
  "read_time_policy": {
    "version": "read-time-policy-v0.1",
    "ranking_order": ["task relevance", "semantic rerank", "scope filters"]
  },
  "current_best": {
    "policy": "resolved winner suppresses loser at retrieval; open conflict is marked unresolved",
    "resolved": [],
    "unresolved": [],
    "suppressed": []
  },
  "token_estimate": 1800
}
```

Router quality gates:

- include at least one relevant branch when a golden fixture has known memory;
- exclude unrelated personal memory from professional-only requests;
- prefer direct user-stated facts over inferred or assistant-generated facts;
- suppress stale memory when newer conflicting memory exists;
- suppress `superseded` memory from prompt-facing retrieval;
- when an explicit resolved conflict has a winner, select the winner and report
  the loser as `suppressed_current_best_loser`;
- preserve unresolved conflict records for review instead of silently choosing
  between equal-trust memories;
- log selected, skipped, and truncated branches;
- never leak quarantined, secret, or unauthorized content.

## Keeper Contract

Keeper output must be structured and command-oriented:

```json
{
  "facts": [],
  "profile_updates": [],
  "entities": [],
  "relationships": [],
  "attempts": [],
  "outcomes": [],
  "rules": [],
  "gotchas": [],
  "graph_commands": [
    {
      "command": "upsert_node",
      "node_type": "project",
      "label": "client-site",
      "confidence": "medium",
      "source_turn_id": "turn_..."
    }
  ],
  "review_required": true
}
```

Keeper quality gates:

- extraction schema validates before graph mutation;
- commands are idempotent;
- node merges preserve evidence;
- low-confidence or untrusted commands go to review;
- delete/correct commands trigger lifecycle propagation;
- failed extraction is visible in audit and observability.

## Failure Modes

- `memory_unavailable`: return a no-memory envelope and record warning.
- `permission_denied`: omit unauthorized branches and record access decision.
- `token_budget_exceeded`: shrink in this order: raw provenance, expanded
  content, summaries, recent messages. Never drop safety or permission notes.
- `keeper_failed`: keep the saved turn, mark job failed, retry if configured.
- `conflict_detected`: prefer newer trusted user memory; mark conflicting memory
  for review.
- `poisoning_detected`: quarantine the source and prevent graph mutation.

Baseline implementation:

- `before_model_call` catches Router/context retrieval failures by default,
  writes a `memory_unavailable` Router audit entry, and returns a no-memory
  prompt envelope with `metadata.operational_failure`.
- `after_saved_turn` saves the raw user/assistant turns first. If Keeper
  extraction fails, it rolls back the failed Keeper ingest, records a failed
  Keeper job with `metadata.operational_failure`, and keeps the saved turns
  inspectable through `memory-changes`.
- `/operational/status`, Python adapter wrappers, and MCP
  `memory_operational_status` expose local health checks for required tables,
  SQLite quick check, storage size, and configured fallback behavior.
- `agent-memory worker --daemon` provides a long-running polling Keeper worker;
  failed queued extraction is recorded as a failed Keeper job instead of
  crashing the worker path.
- `agent-memory observability`, `/observability`, and MCP
  `memory_observability` summarize Router token estimates, selected branches,
  Router/Keeper wall-clock duration, Keeper job status, warnings, and LLM usage
  tokens/cost.
- `agent-memory migration-status`, `agent-memory backup`, and
  `agent-memory restore` provide local SQLite schema checks and backup/restore
  recovery using the SQLite backup API.

Still production work: latency SLOs, encrypted off-host backups, restore
drills, migration changelogs, hosted health checks, deployment supervisor
recipes, restart policies, and alerting.

## End State

A system implements this contract when an external model can be completely
stateless and still behave memory-aware because the orchestrator injects only
the memory envelope returned by the kernel.

## Acceptance Gate

The runtime contract is backed by the formal Memory Contract in
[memory-contract.md](memory-contract.md). The deterministic gate is:

```bash
agent-memory contract assert
agent-memory acceptance seed --db /tmp/amk-acceptance.db
agent-memory acceptance assert --db /tmp/amk-acceptance.db
```

This gate proves the minimum closed-loop behavior for local development:
contract shape, Router/Keeper vertical slice, selected memory versus no-memory
baseline, lane isolation, unsafe-memory exclusion, source logging, rollback
retrieval, reviewable Keeper writes, and write-policy enforcement.
