# Generic Runtime Adapter Example

This example shows the neutral adapter shape for any chat app, coding agent, or
workflow runtime. It is intentionally not Hermes-specific.

## Call Order

```text
user request
-> before-model-call
-> main model call
-> after-saved-turn
-> review Keeper candidates
-> future before-model-call sees approved memory
```

## CLI Walkthrough

```bash
export AMK_DB=/tmp/amk-generic-runtime.db

PYTHONPATH=src python3 -m agent_memory_kernel.cli init --db "$AMK_DB"

PYTHONPATH=src python3 -m agent_memory_kernel.cli remember --db "$AMK_DB" \
  "Rule: before planning a project iteration, review the last successful and failed attempts." \
  --scope professional \
  --source-type user_note \
  --source-ref generic-runtime

PYTHONPATH=src python3 -m agent_memory_kernel.cli review --db "$AMK_DB" list --status pending
PYTHONPATH=src python3 -m agent_memory_kernel.cli review --db "$AMK_DB" approve cand_xxxxxxxxxxxxxxxx \
  --actor reviewer \
  --reason "generic runtime fixture"

PYTHONPATH=src python3 -m agent_memory_kernel.cli before-model-call --db "$AMK_DB" \
  "Plan the next project iteration" \
  --scope professional \
  --thread-id generic-runtime \
  --agent-id planner

# Call your main model with prompt_envelope.messages here.

PYTHONPATH=src python3 -m agent_memory_kernel.cli after-saved-turn --db "$AMK_DB" \
  --thread-id generic-runtime \
  --scope professional \
  --agent-id planner \
  --user-text "Plan the next project iteration" \
  --assistant-text "Use the previous approved rule and record any new lesson." \
  --keeper-mode sync
```

## Python Shape

```python
from agent_memory_kernel import MemoryOrchestrator

memory = MemoryOrchestrator.from_path("/tmp/amk-generic-runtime.db")

prompt = memory.before_turn(
    "Plan the next project iteration",
    thread_id="generic-runtime",
    scope="professional",
    agent_id="planner",
)

# response_text = your_main_model(prompt["prompt_envelope"]["messages"])
response_text = "Use the previous approved rule and record any new lesson."

memory.after_turn(
    thread_id="generic-runtime",
    scope="professional",
    agent_id="planner",
    user_text="Plan the next project iteration",
    assistant_text=response_text,
    keeper_mode="sync",
)
```

## Adapter Rules

- Do not let the main model search the raw database or full graph.
- Pass only the Router-returned prompt envelope.
- Save the turn before Keeper extraction.
- Keep Keeper candidates reviewable unless explicit write policy allows
  promotion.
- Re-run conformance before claiming compatibility.
