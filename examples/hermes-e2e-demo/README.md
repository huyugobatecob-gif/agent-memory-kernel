# Hermes End-To-End Memory Demo

This demo shows the production-shaped loop:

1. Router retrieves existing memory before the agent plans.
2. Hermes saves the turn and queues Keeper work.
3. Write policy prevents the agent from auto-approving durable memory.
4. A reviewer approves the candidate.
5. The next Router call sees the newly approved memory.

```bash
DB=/tmp/amk-hermes-e2e.db

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli init --db "$DB"

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli remember --db "$DB" \
  "Pattern: project demo-site successful refresh loops improve internal links." \
  --scope professional \
  --actor reviewer \
  --approve

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli before-model-call --db "$DB" \
  "Plan a demo-site internal link refresh." \
  --thread-id hermes-e2e \
  --scope professional \
  --agent-id writer

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli write-policy --db "$DB" set \
  --agent-id writer \
  --scope professional \
  --action auto_approve \
  --decision deny \
  --reason "writer proposes memory for review"

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli after-saved-turn --db "$DB" \
  --thread-id hermes-e2e \
  --scope professional \
  --agent-id writer \
  --user-text "Decision: project demo-site should reuse the refresh-loop playbook." \
  --assistant-text "I will track outcome memory after the loop." \
  --keeper-mode queued \
  --approve

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli worker --db "$DB" --once --limit 1

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli review --db "$DB" list --status pending
PYTHONPATH=../../src python3 -m agent_memory_kernel.cli review --db "$DB" approve cand_xxxxxxxxxxxxxxxx --actor reviewer

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli before-model-call --db "$DB" \
  "What should demo-site reuse?" \
  --thread-id hermes-e2e \
  --scope professional \
  --agent-id writer
```

The worker output should show a queued Keeper candidate and an
`auto_approve denied by write policy` warning. Replace
`cand_xxxxxxxxxxxxxxxx` with the pending candidate id before approving it.
