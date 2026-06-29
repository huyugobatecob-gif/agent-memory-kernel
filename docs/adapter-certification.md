# Adapter Certification

Adapter certification is the local proof path for external runtimes. It checks
that an adapter-shaped integration respects the kernel contract without needing
a live provider, hosted registry, or private workflow.

## What Certification Means

Certification means the adapter can use the kernel while preserving:

- selected-memory prompt envelopes;
- provenance and source ids;
- reviewable Keeper writes;
- policy-denied no-memory fallback;
- scope/lane/namespace isolation;
- lifecycle propagation;
- import/export provenance;
- no full-graph prompt injection.

Certification does not mean the adapter's hosted deployment, provider quality,
billing, remote MCP security, or team RBAC is certified.

## Commands

Create and verify a local conformance store:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance spec
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance spec-assert
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance seed --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
```

Generate a local adapter certification report and registry entry:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance certify \
  --db /tmp/amk-conformance.db \
  --adapter-name my-runtime

PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance registry-entry \
  --db /tmp/amk-conformance.db \
  --adapter-name my-runtime
```

## Adapter Checklist

- Do not pass the full graph, raw event stream, or hidden tags into the main
  model prompt.
- Call the Router before the model and pass only the returned prompt envelope.
- Save the exchange before running Keeper.
- Treat Keeper output as candidates unless explicit write policy allows
  promotion.
- Preserve source ids, memory ids, candidate ids, review actions, lifecycle
  state, and policy metadata across import/export paths.
- Respect read/write/export/lifecycle policy denials.
- Keep provider prompt formatter behavior outside hidden system-instruction
  surfaces unless the adapter contract explicitly preserves safety boundaries.
- Re-run conformance after adapter or kernel upgrades.

## Minimal Adapter Shape

The neutral example in
[../examples/generic-runtime-adapter/README.md](../examples/generic-runtime-adapter/README.md)
shows the intended call order:

```text
before-model-call
-> main model call
-> after-saved-turn
-> review Keeper candidates
```

Runtime-specific adapters such as Hermes are optional examples. They should not
define the project identity or bypass the generic certification path.
