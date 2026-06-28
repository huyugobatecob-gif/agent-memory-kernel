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

## Notifications

The baseline notification queue is also machine-readable. It creates open
notifications for:

- pending or quarantined review candidates;
- sensitive export approval requests;
- expired export artifacts that need external cleanup confirmation.

```bash
agent-memory notifications --db .memory/demo.db list --status open
agent-memory notifications --db .memory/demo.db assign ntf_xxxxxxxxxxxxxxxx --assigned-to reviewer-a --actor lead
agent-memory notifications --db .memory/demo.db list --status open --sla-status overdue
agent-memory notifications --db .memory/demo.db ack ntf_xxxxxxxxxxxxxxxx --actor reviewer
agent-memory notifications --db .memory/demo.db resolve ntf_xxxxxxxxxxxxxxxx --actor reviewer
```

Approving or rejecting a candidate resolves candidate notifications. Approving
or rejecting an export approval resolves export approval notifications. Purging
an export retention record resolves the export retention notification.
Assignments add `assigned_to`, `assigned_by`, `assigned_at`, and optional
`due_at`, so Hermes or a UI can filter one reviewer queue without changing
memory state. Each notification also returns computed `sla.status`
(`overdue`, `due_soon`, `on_track`, `no_due_date`, `invalid_due_date`, or
`resolved`) and can be filtered with `sla_status`.

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
- `POST /memory/lifecycle-batch`
- `POST /memory/delete`
- `POST /memory/distrust`
- `POST /memory/expire`
- `POST /notifications/list`
- `POST /notifications/escalations`
- `POST /notifications/assign`
- `POST /notifications/ack`
- `POST /notifications/resolve`

MCP tools:

- `memory_review_inbox`
- `memory_review_batch`
- `memory_review_approve`
- `memory_review_reject`
- `memory_correct`
- `memory_lifecycle_batch`
- `memory_delete`
- `memory_distrust`
- `memory_expire`
- `memory_notifications_list`
- `memory_notification_escalations`
- `memory_notification_assign`
- `memory_notification_ack`
- `memory_notification_resolve`

## Integration Pattern

After `after_saved_turn` or a background worker creates Keeper candidates:

1. Call `memory_changes` to inspect what the turn changed.
2. Call `review inbox --status open` or `memory_review_inbox` to see all
   pending/quarantined candidates in operator form.
3. Call `notifications list --status open` or `memory_notifications_list` when
   the operator needs one queue across review, export approval, and retention
   cleanup.
4. Assign notifications to a reviewer when a human owner is needed.
5. Filter `sla_status=overdue` or call `memory_notification_escalations` for
   escalation candidates before long-running review queues drift.
6. Read `review.risk_flags`, `review.conflict_warnings`, `graph_preview`,
   `audit_trail`, and `operator_handles` before approving.
7. Use `review batch ... --dry-run` or `memory_review_batch` dry-run to preview
   approve/reject policy before mutating memory.
8. Approve only candidates that are safe, scoped correctly, and useful.
9. Reject quarantined or low-quality candidates.
10. Use `lifecycle-batch --dry-run` or `memory_lifecycle_batch` dry-run when
   several active memories need correction, deletion, distrust, or expiry.
11. Use correct/delete/distrust/expire on already active memories when the
   source truth changes.

This keeps the main agent out of memory maintenance. The agent gets selected
prompt context; the operator or governing policy controls durable memory.

## Still Backlog

The current inbox is a stable data/API baseline. Future product layers can add:

- browser-based review UI;
- browser UI over graph browser source previews;
- browser-assisted batch approve/reject and lifecycle correction;
- richer conflict-resolution UI over inline candidate warnings;
- hosted key-management and export custody controls;
- push/email/web notification transports.
