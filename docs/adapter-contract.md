# Adapter Contract

Adapters connect Agent Memory Kernel to runtimes, tools, import/export formats,
retrieval enhancers, or model providers. They are not the source of memory
truth. They consume the kernel contract.

The machine-readable version is exposed as
`memory_contract()["adapter_contract"]`.

## Principle

Adapters may move memory into and out of host systems, but they must not define
their own memory lifecycle, trust model, prompt boundary, or import/export
semantics. The kernel owns:

- source events;
- candidate and active memory lifecycle;
- policies and capability grants;
- graph/evidence state;
- prompt envelope shape;
- import/export provenance;
- audit and conformance.

## Capability Levels

The public contract defines these adapter capability levels:

- `read-only`: can inspect contract, status, search, retrieval, and explain
  surfaces; cannot write, promote, mutate lifecycle, or export without policy.
- `write-capable`: can record source events, propose candidates, and queue
  Keeper work; cannot auto-promote untrusted claims or bypass review policy.
- `lifecycle-capable`: can approve, reject, correct, delete, distrust, expire,
  and rollback only when actor policy allows it.
- `graph-capable`: can read graph/evidence and propose graph commands; cannot
  show cross-scope evidence or revive inactive memory.
- `export-capable`: can export/import profiles or bundles; cannot restore
  redacted content or activate pending/rejected memory.
- `prompt-injection-capable`: can build or format prompt envelopes; cannot
  inject the full graph or place retrieved memory in an unsafe system surface.

## Adapter Types

### Runtime Adapter

Examples: chat app, coding agent, Hermes, LangGraph, AutoGen, CrewAI.

Required hooks:

- `before_model_call`
- `after_saved_turn`

Required invariants:

- selected, budgeted prompt envelopes only;
- scope/lane/namespace isolation;
- auditable reads and writes.

### Importer / Exporter

Examples: markdown vault, notes import, document import, profile bundle.

Required hooks:

- `export_profile`
- `import_profile`

Required invariants:

- import/export preserves provenance and lifecycle;
- distrusted and inactive sources do not influence outputs.

### Retrieval Enhancer

Examples: embeddings, ANN, provider rerankers.

Required hook:

- `rank_after_policy_filtering`

Required invariants:

- baseline retrieval remains deterministic without the enhancer;
- enhancer runs after policy/lifecycle filtering;
- prompt envelope still contains selected memory only.

### Provider Formatter

Examples: OpenAI, Anthropic, Gemini, local model prompt shapes.

Required hook:

- `format_prompt_envelope`

Required invariant:

- provider formatting must preserve prompt boundaries and keep retrieved memory
  out of unsafe high-priority system surfaces.

## Certification

Adapter certification is local and provider-free:

```bash
agent-memory conformance spec
agent-memory conformance seed --db .memory/conformance.db
agent-memory conformance run --db .memory/conformance.db
agent-memory conformance certify --db .memory/conformance.db --adapter-name my-runtime
```

Certification proves public behavior against the kernel contract. It does not
certify hosted deployment, provider quality, billing, team RBAC, remote MCP
transport, or domain-specific workflow correctness.
