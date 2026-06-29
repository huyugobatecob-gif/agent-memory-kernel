# Prompt And Keeper Snapshots

These snapshots show adapter-shaped behavior without requiring a live model
provider. They are intentionally abbreviated; use the commands to inspect full
JSON locally.

## Snapshot 1: Selected Memory Prompt Envelope

Command:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli before-model-call --db /tmp/amk-demo.db \
  "Plan the next project iteration" \
  --scope professional \
  --thread-id quickstart \
  --agent-id planner \
  --token-budget 800
```

Expected shape:

```json
{
  "router_run_id": "router_...",
  "selected_branch_ids": ["gnode_..."],
  "prompt_envelope": {
    "system": "Use the supplied memory as selected prior context...",
    "messages": [
      {"role": "user", "content": "## Agent Context Builder..."},
      {"role": "user", "content": "<<< MEMORY_TREE_SUPPLEMENT >>>..."},
      {"role": "user", "content": "Plan the next project iteration"}
    ],
    "metadata": {
      "memory_allowed": true,
      "selection_decisions": [
        {
          "memory_id": "mem_...",
          "decision": "selected",
          "reason": "within branch limit"
        }
      ],
      "source_ids": ["quickstart", "mem_..."]
    }
  }
}
```

Adapter expectation: the main model receives selected content with provenance,
not the full graph.

## Snapshot 2: No-Memory Policy Denial

Command:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli before-model-call --db /tmp/amk-demo.db \
  "Plan the next project iteration" \
  --scope professional \
  --thread-id quickstart \
  --agent-id blocked \
  --token-budget 800
```

Expected shape after a deny read policy:

```json
{
  "access_decisions": [{"decision": "deny"}],
  "selected_branch_ids": [],
  "prompt_envelope": {
    "metadata": {
      "memory_allowed": false,
      "selected_branch_ids": []
    }
  },
  "warnings": ["memory access denied by read policy for scope: professional"]
}
```

Adapter expectation: denied memory becomes an explicit no-memory envelope, not a
silent partial prompt.

## Snapshot 3: Keeper Proposal After Saved Turn

Command:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli after-saved-turn --db /tmp/amk-demo.db \
  --thread-id quickstart \
  --scope professional \
  --agent-id planner \
  --user-text "Plan the next project iteration" \
  --assistant-text "Use the previous successful handoff checklist and avoid the failed no-review path." \
  --keeper-mode sync
```

Expected shape:

```json
{
  "status": "completed",
  "mode": "sync",
  "saved_turn_ids": ["turn_...", "turn_..."],
  "event_id": "evt_...",
  "keeper_job_id": "kjob_...",
  "candidate_ids": ["cand_..."],
  "warnings": ["keeper candidate requires review"]
}
```

Adapter expectation: the exchange is saved, Keeper proposes reviewable memory,
and unsafe auto-promotion remains blocked unless policy explicitly allows it.

## Snapshot 4: Imported Or Tool-Output Claims

Use conformance for deterministic imported/tool-output safety checks:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
```

Relevant scenarios:

- `tool_prompt_injection_is_quarantined`
- `untrusted_tool_claim_stays_reviewable`
- `assistant_guess_stays_reviewable`
- `golden_trace_poisoned_bundle_import_quarantines_prompt_injection`

Adapter expectation: external claims can become evidence or review candidates,
but they do not silently become trusted prompt-facing memory.
