# Reference Memory Loop Demo

This provider-neutral demo is the fastest way to see the full memory loop work
without connecting a private agent runtime.

It proves:

- Router selects relevant professional memory before the main model call;
- the prompt envelope contains expanded memory, not only tags;
- Keeper records the post-turn exchange and leaves new memory reviewable;
- corrected memory replaces stale text;
- deleted memory stays absent from retrieval;
- personal memory does not leak into professional prompts;
- hostile tool text is quarantined;
- success and failure outcomes are available for the next loop plan.

```bash
DB=/tmp/amk-reference-loop.db

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli init --db "$DB"

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli slice seed --db "$DB"
PYTHONPATH=../../src python3 -m agent_memory_kernel.cli slice run --db "$DB"
PYTHONPATH=../../src python3 -m agent_memory_kernel.cli slice assert --db "$DB"
```

The final command returns a JSON object with `status: "passed"` and checks such
as:

- `project_fact_retrieved`;
- `success_branch_retrieved`;
- `failure_branch_retrieved`;
- `outcome_pack_has_success_and_failure`;
- `outcome_records_have_active_provenance`;
- `corrected_fact_retrieved`;
- `deleted_fact_absent`;
- `personal_lane_excluded`;
- `poisoning_quarantined`;
- `keeper_left_candidates_reviewable`.

To inspect the same state manually:

```bash
PYTHONPATH=../../src python3 -m agent_memory_kernel.cli before-model-call --db "$DB" \
  "Plan the next slice-site SEO refresh loop using successes and failures." \
  --thread-id slice-thread \
  --scope professional

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli outcome --db "$DB" pack \
  --project slice-site \
  --scope professional

PYTHONPATH=../../src python3 -m agent_memory_kernel.cli memory-changes --db "$DB" \
  --thread-id slice-thread
```

This demo is intentionally not tied to Hermes, Codex, Claude, or any other
runtime. Those runtimes should call the same hooks through Python, HTTP, MCP, or
a thin adapter.
