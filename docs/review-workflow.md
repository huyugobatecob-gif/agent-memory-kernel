# Review Workflow

Review is the human/operator control surface for memory writes proposed by
Keeper.

The baseline review inbox is machine-readable, not a web UI. It is intended for
Hermes, MCP agents, CLI operators, and future UI layers that need one stable
shape for source preview, risk flags, graph preview, and action handles.

## Inbox

```bash
agent-memory review --db .memory/demo.db inbox --status open --scope professional
```

Status filters:

- `open`: pending and quarantined candidates.
- `pending`: candidates waiting for approve/reject.
- `quarantined`: candidates blocked by admission policy.
- `approved`: candidates already promoted to active memory.
- `rejected`: candidates rejected by a reviewer.
- `all`: all candidate statuses.

The inbox response contains:

- `candidate`: proposed memory text, kind, scope, trust, sensitivity, status,
  reason, and raw extraction metadata.
- `source_event`: event actor, source type/ref, source excerpt, and metadata.
- `graph_preview`: compact nodes, edges, and extracted facts proposed by
  Keeper.
- `review`: recommended action plus risk flags such as quarantined, secret,
  untrusted source, low confidence, or prompt-injection-like content.
- `active_memories`: promoted memory rows for approved candidates.
- `review_history` and `audit_trail`.
- `operator_handles`: CLI, HTTP, and MCP handles for the next safe action.

## Actions

Candidate review:

```bash
agent-memory review --db .memory/demo.db approve cand_xxxxxxxxxxxxxxxx --actor reviewer
agent-memory review --db .memory/demo.db reject cand_xxxxxxxxxxxxxxxx --actor reviewer
```

Batch review:

```bash
agent-memory review --db .memory/demo.db batch approve cand_a cand_b --actor reviewer --dry-run
agent-memory review --db .memory/demo.db batch reject cand_a cand_b --actor reviewer --reason "low quality"
```

Batch responses return one result per candidate. A missing, already-active, or
policy-blocked candidate is reported on that item without hiding the rest of
the batch unless `--stop-on-error` is set.

Active memory lifecycle:

```bash
agent-memory correct --db .memory/demo.db mem_xxxxxxxxxxxxxxxx "Corrected memory text" --actor reviewer
agent-memory delete --db .memory/demo.db mem_xxxxxxxxxxxxxxxx --actor reviewer
agent-memory distrust --db .memory/demo.db mem_xxxxxxxxxxxxxxxx --actor reviewer
agent-memory expire --db .memory/demo.db mem_xxxxxxxxxxxxxxxx --actor reviewer
```

HTTP endpoints:

- `POST /review/inbox`
- `POST /review/batch`
- `POST /review/approve`
- `POST /review/reject`
- `POST /memory/correct`
- `POST /memory/delete`
- `POST /memory/distrust`
- `POST /memory/expire`

MCP tools:

- `memory_review_inbox`
- `memory_review_batch`
- `memory_review_approve`
- `memory_review_reject`
- `memory_correct`
- `memory_delete`
- `memory_distrust`
- `memory_expire`

## Integration Pattern

After `after_saved_turn` or a background worker creates Keeper candidates:

1. Call `memory_changes` to inspect what the turn changed.
2. Call `review inbox --status open` or `memory_review_inbox` to see all
   pending/quarantined candidates in operator form.
3. Use `review batch ... --dry-run` or `memory_review_batch` dry-run to preview
   approve/reject policy before mutating memory.
4. Approve only candidates that are safe, scoped correctly, and useful.
5. Reject quarantined or low-quality candidates.
6. Use correct/delete/distrust/expire on already active memories when the
   source truth changes.

This keeps the main agent out of memory maintenance. The agent gets selected
prompt context; the operator or governing policy controls durable memory.

## Still Backlog

The current inbox is a stable data/API baseline. Future product layers can add:

- browser-based review UI;
- graph browser with source previews;
- browser-assisted batch approve/reject;
- conflict warnings inline with candidates;
- encrypted export controls;
- reviewer assignment and notification queues.
