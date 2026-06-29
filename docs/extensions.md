# Extensions

Extensions add runtime surfaces, domain conventions, renderers, provider hooks,
or operator workflows around the kernel. They are useful, but they must not
define the v0.1.0 local memory contract.

## Extension Rule

An extension may consume kernel APIs. It must not bypass:

- candidate review and write policy;
- read policy and prompt-injection boundaries;
- scope/lane/namespace isolation;
- lifecycle suppression for deleted, distrusted, expired, superseded,
  rejected, pending, or quarantined memory;
- import/export provenance and redaction rules;
- conformance invariants.

## Current Extension Areas

| Area | Placement | Notes |
| --- | --- | --- |
| Local HTTP API | `src/agent_memory_kernel/server.py`, [mcp.md](mcp.md) | Local mirror over the same contract. |
| stdio MCP server | `src/agent_memory_kernel/mcp_server.py`, [mcp.md](mcp.md) | Local tool surface, not hosted remote MCP. |
| Browser review/graph pages | local HTTP UI | Operator workflow over review and graph data. |
| Provider prompt formatters | CLI certification and adapter docs | Must keep memory outside hidden provider system surfaces. |
| Embeddings/rerank providers | optional retrieval enhancer | Runs after policy filtering; local fallback remains deterministic. |
| Outcome/domain packs | examples and future packs | May add graph conventions, not kernel assumptions. |
| Digital Brain rendering | graph-derived style extension | Advisory and suppressible. |
| Notifications and billing reconciliation | local operator reports/outbox | Not live delivery or hosted billing. |
| Runtime adapters | `adapters/`, `examples/` | Optional integration examples such as Hermes. |

## Later Hosted Work

Hosted SaaS, remote MCP hosting, hosted team RBAC, cloud KMS/off-host custody,
managed alerting, hosted registry/badges, sync/collaboration, and live provider
certification are tracked in [hosted-roadmap.md](hosted-roadmap.md). They are
not local v0.1.0 blockers.

## Where To Put New Work

- If it changes local memory truth, lifecycle, retrieval, prompt boundaries,
  import/export, or conformance, propose it as core.
- If it adds a runtime, provider, UI, domain pack, renderer, or operator view,
  put it under extension docs/examples/adapters.
- If it requires hosted identity, remote teams, managed billing, cloud custody,
  or live external services, put it under later-hosted.
