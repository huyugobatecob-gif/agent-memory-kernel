# Production Rollout Playbook

This playbook describes how to introduce Agent Memory Kernel into a live
Hermes-style agent system without giving the main agent direct graph access.

The safe production pattern is:

1. Run preflight gates against the target database.
2. Enable shadow traces for real traffic with propose-only writes.
3. Review Router selections and Keeper candidates.
4. Turn reviewed traces into regression fixtures.
5. Enable live before/after hooks for one low-risk agent profile.
6. Add a supervised Keeper worker for queued jobs.
7. Expand scope only after observability and review queues stay healthy.

## Preflight

Run these before any live agent uses memory:

```bash
agent-memory contract assert
agent-memory migration-status --db .memory/hermes-memory.db
agent-memory acceptance seed --db .memory/hermes-memory.db
agent-memory acceptance assert --db .memory/hermes-memory.db
agent-memory conformance seed --db .memory/hermes-memory.db
agent-memory conformance assert --db .memory/hermes-memory.db
agent-memory keeper-eval
```

For an existing live database, create a backup before migrations or large
policy changes:

```bash
agent-memory backup --db .memory/hermes-memory.db --out .memory/backups/hermes-memory.db
```

## Shadow Rollout

Start with a single professional-scope agent profile. Do not auto-approve model
output during shadow rollout.

```bash
agent-memory shadow-turn "Plan the next SEO loop" \
  --db .memory/hermes-memory.db \
  --thread-id seo-demo \
  --scope professional \
  --agent-id seo-planner \
  --model-id priority-model \
  --keeper-mode queued \
  --user-text "Plan the next SEO loop" \
  --assistant-text "Use the prior successful refresh pattern."
```

Review the trace:

```bash
agent-memory shadow-traces --db .memory/hermes-memory.db --thread-id seo-demo
agent-memory memory-changes --db .memory/hermes-memory.db --thread-id seo-demo
agent-memory review inbox --db .memory/hermes-memory.db --status open --scope professional
```

Promote accepted behavior into a regression fixture:

```bash
agent-memory shadow-eval trace_xxxxxxxxxxxxxxxx \
  --db .memory/hermes-memory.db \
  --expected-json '{"expected_branch_labels":["seo-demo"],"require_candidates":true}'
```

## Live Hermes Wrapper

For local Python Hermes runtimes, prefer `run_agent_turn()` when the main agent
call is in the same process:

```python
from adapters.hermes_provider.hermes_provider import HermesMemoryProvider

provider = HermesMemoryProvider(".memory/hermes-memory.db")

result = provider.run_agent_turn(
    "Plan the next SEO loop",
    lambda prompt: {"assistant_text": priority_model.chat(prompt["messages"]).text},
    thread_id="seo-demo",
    scope="professional",
    agent_id="seo-planner",
    model_id="priority-model",
    keeper_mode="queued",
)
```

Hermes should log at least:

- `router_run_id`
- `selected_branch_ids`
- `keeper_job_id`
- `saved_turn_ids`
- `prompt_envelope.metadata.warnings`
- `prompt_envelope.metadata.source_ids`

For service or MCP integrations, use the explicit two-step lifecycle:

```bash
agent-memory before-model-call "Plan the next SEO loop" \
  --db .memory/hermes-memory.db \
  --thread-id seo-demo \
  --scope professional \
  --agent-id seo-planner \
  --model-id priority-model \
  --allowed-scopes professional

agent-memory after-saved-turn \
  --db .memory/hermes-memory.db \
  --thread-id seo-demo \
  --scope professional \
  --agent-id seo-planner \
  --model-id priority-model \
  --keeper-mode queued \
  --user-text "Plan the next SEO loop" \
  --assistant-text "Use the prior successful refresh pattern."
```

## Worker Supervision

Queued Keeper mode is the safest default for production because the user-facing
agent turn does not wait on extraction. Run the worker under a supervisor.

Minimal systemd unit example:

```ini
[Unit]
Description=Agent Memory Keeper Worker
After=network.target

[Service]
WorkingDirectory=/srv/agent-memory-kernel
Environment=PYTHONPATH=/srv/agent-memory-kernel/src
ExecStart=/usr/bin/python3 -m agent_memory_kernel.cli worker --db /srv/agent-memory/hermes-memory.db --daemon --poll-interval 5 --limit 10
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

For bounded maintenance jobs:

```bash
agent-memory worker --db .memory/hermes-memory.db --once --limit 10
agent-memory worker --db .memory/hermes-memory.db --daemon --max-iterations 20 --stop-when-idle
```

## API Deployment

The built-in HTTP API is local-first. For production, bind it to localhost and
place authentication, TLS, and network policy outside the process.

```bash
AGENT_MEMORY_API_TOKEN="change-me" agent-memory serve \
  --db .memory/hermes-memory.db \
  --host 127.0.0.1 \
  --port 8765 \
  --auth-token-env AGENT_MEMORY_API_TOKEN
```

Health and preflight:

```bash
curl http://127.0.0.1:8765/health
curl -H "Authorization: Bearer $AGENT_MEMORY_API_TOKEN" \
  http://127.0.0.1:8765/operational/status
```

Do not expose this local server directly to the public internet. Put it behind
a private network, SSH tunnel, or authenticated reverse proxy if remote agents
must reach it.

## MCP Deployment

The repository ships a stdio MCP server, not a hosted remote MCP server.

Preferred pattern:

```bash
agent-memory mcp --db .memory/hermes-memory.db
```

Run it on the same host as the agent runtime or MCP client. If an agent runs on
a VPS, install the kernel on that VPS and point the MCP server at the local
database or an approved local replica. If a remote agent must access a central
memory store, prefer the HTTP API behind a private tunnel and keep stdio MCP as
the local tool bridge.

Every MCP client should first call:

1. `tools/list`
2. `memory_operational_status`
3. `memory_capability_check`
4. `memory_before_turn`
5. `memory_after_turn`
6. `memory_changes`

## Policies Before Live Writes

For normal production agents, deny auto-approval and require review:

```bash
agent-memory write-policy set \
  --db .memory/hermes-memory.db \
  --agent-id seo-planner \
  --scope professional \
  --action auto_approve \
  --decision deny \
  --reason "production agents propose memory; reviewers approve"
```

For lane isolation:

```bash
agent-memory read-policy set \
  --db .memory/hermes-memory.db \
  --agent-id seo-planner \
  --scope personal \
  --action inject \
  --decision deny \
  --reason "SEO planner uses professional memory only"
```

Check effective permissions before delegation:

```bash
agent-memory capability --db .memory/hermes-memory.db --actor seo-planner --scope professional
```

## Observability

After live traffic starts, check:

```bash
agent-memory operational-status --db .memory/hermes-memory.db
agent-memory observability --db .memory/hermes-memory.db --scope professional --thread-id seo-demo
agent-memory router-runs --db .memory/hermes-memory.db --thread-id seo-demo
agent-memory memory-quality --db .memory/hermes-memory.db --scope professional
agent-memory notifications --db .memory/hermes-memory.db --status open --scope professional
```

Production readiness means:

- no memory-unavailable warnings for normal traffic;
- selected branches include relevant source IDs;
- personal memory is absent from professional-only prompts;
- unsafe candidates are quarantined;
- Keeper jobs are processed within the expected delay;
- review inbox volume is manageable;
- shadow evals pass after prompt, Router, or Keeper changes.

## Rollback

If memory behaves badly, disable prompt injection first and preserve audit:

```bash
agent-memory read-policy set \
  --db .memory/hermes-memory.db \
  --agent-id seo-planner \
  --scope professional \
  --action inject \
  --decision deny \
  --reason "temporary rollback: memory injection disabled"
```

Then inspect the latest runs:

```bash
agent-memory router-runs --db .memory/hermes-memory.db --thread-id seo-demo
agent-memory memory-changes --db .memory/hermes-memory.db --thread-id seo-demo
agent-memory review inbox --db .memory/hermes-memory.db --status open --scope professional
```

For bad active memory, prefer lifecycle controls over database edits:

```bash
agent-memory distrust --db .memory/hermes-memory.db mem_xxxxxxxxxxxxxxxx --reason "bad production memory"
agent-memory correct --db .memory/hermes-memory.db mem_xxxxxxxxxxxxxxxx "Corrected text" --reason "operator correction"
agent-memory delete --db .memory/hermes-memory.db mem_xxxxxxxxxxxxxxxx --reason "remove from retrieval"
```

If the database itself is unsafe, restore from a verified backup into a new
target path and switch Hermes to that database only after `migration-status` and
the conformance suite pass.
