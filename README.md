# Agent Memory Kernel

[![CI](https://github.com/huyugobatecob-gif/agent-memory-kernel/actions/workflows/tests.yml/badge.svg)](https://github.com/huyugobatecob-gif/agent-memory-kernel/actions/workflows/tests.yml)

Local-first, auditable memory for AI agents.

Agent Memory Kernel is a small Python/SQLite reference implementation for
turning observed events into governed, reusable agent context. It is designed
to be embedded by runtimes, chat apps, coding agents, workflow tools, and
domain packs without making any one runtime, provider, vector database, or
hosted service part of the memory contract.

## Current Status

`v0.1.0 alpha`: kernel-complete local reference implementation with executable
conformance contracts.

That means the local kernel loop is implemented and covered by deterministic
tests, conformance scenarios, and command-line checks. It does not mean this is
a hosted platform, a stable ecosystem standard, or a managed memory service.
The package metadata intentionally uses `Development Status :: 3 - Alpha`.

The public contract is:

```text
source event
-> candidate memory
-> review or policy decision
-> active memory
-> graph/evidence model
-> Router-selected prompt envelope
-> saved turn
-> Keeper proposal for the next update
```

The main model receives selected, policy-filtered, budgeted memory content. It
does not scan the full database, raw event stream, hidden tags, or full graph.

## What This Is

- A local SQLite source of truth for source events, candidate memory, active
  memory, graph/evidence records, review history, and audit trails.
- A governed memory lifecycle: propose, review, approve, correct, rollback,
  delete, distrust, expire, supersede, export, and import.
- A Router contract that builds provider-neutral prompt envelopes from selected
  memory with provenance, reasons, warnings, and budget metadata.
- A Keeper contract that records saved turns and proposes reviewable memory
  updates after an exchange.
- A conformance suite that external adapters can run without a live LLM
  provider.

## What This Is Not

- Not a hosted SaaS product.
- Not an agent runtime or workflow orchestrator.
- Not a vector database or ANN service.
- Not a billing, notification, dashboard, team-RBAC, or cloud-KMS product.
- Not specific to Hermes, SEO projects, personal/professional memory, or any
  single domain pack.

Optional HTTP, MCP, UI, provider, embedding, Digital Brain, Hermes, SEO, and
hosted/team ideas live as extensions or later-hosted work. They must consume
the kernel contract instead of redefining it.

## Install

From this repository:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

During development you can also run the CLI directly:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli --help
```

## Five-Minute Kernel Quickstart

This proves the local memory loop without a hosted service, runtime adapter,
domain pack, vector index, or live model provider.

Use a temporary database:

```bash
export AMK_DB=/tmp/amk-demo.db
```

Initialize the store:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli init --db "$AMK_DB"
```

Expected shape:

```text
initialized /tmp/amk-demo.db
```

Record a memory candidate:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli remember --db "$AMK_DB" \
  "Rule: before planning a project iteration, review the last successful and failed attempts." \
  --scope professional \
  --source-type user_note \
  --source-ref quickstart
```

Expected shape:

```json
{
  "event_id": "evt_...",
  "candidates": [
    {
      "candidate_id": "cand_...",
      "status": "pending",
      "reason": "candidate requires review"
    }
  ]
}
```

Review and approve the candidate:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli review --db "$AMK_DB" list --status pending
PYTHONPATH=src python3 -m agent_memory_kernel.cli review --db "$AMK_DB" approve cand_xxxxxxxxxxxxxxxx \
  --actor reviewer \
  --reason "quickstart approval"
```

Expected approval shape:

```json
{
  "memory_id": "mem_...",
  "status": "active"
}
```

Build the prompt envelope the main agent would receive:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli before-model-call --db "$AMK_DB" \
  "Plan the next project iteration" \
  --scope professional \
  --thread-id quickstart \
  --agent-id planner \
  --token-budget 800
```

Look for:

- `prompt_envelope.messages`
- `MEMORY_TREE_SUPPLEMENT`
- `metadata.selected_branch_ids`
- `metadata.selection_decisions`
- `source_ids`

Explain why a memory exists:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli memory-explain --db "$AMK_DB" mem_xxxxxxxxxxxxxxxx
```

Look for the source event, candidate, review history, graph evidence, audit
trail, and lifecycle handles.

Save a turn and run the conservative Keeper path:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli after-saved-turn --db "$AMK_DB" \
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
  "saved_turn_ids": ["turn_...", "turn_..."],
  "candidate_ids": ["cand_..."],
  "warnings": ["keeper candidate requires review"]
}
```

Check the fail-closed no-memory path:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli read-policy --db "$AMK_DB" set \
  --agent-id blocked \
  --scope professional \
  --action inject \
  --decision deny \
  --reason "quickstart no-memory fallback"

PYTHONPATH=src python3 -m agent_memory_kernel.cli before-model-call --db "$AMK_DB" \
  "Plan the next project iteration" \
  --scope professional \
  --thread-id quickstart \
  --agent-id blocked \
  --token-budget 800
```

Expected shape:

```json
{
  "access_decisions": [{"decision": "deny"}],
  "prompt_envelope": {
    "metadata": {
      "memory_allowed": false,
      "selected_branch_ids": []
    }
  },
  "warnings": ["memory access denied by read policy for scope: professional"]
}
```

Run the public conformance shape check:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance spec-assert
```

Expected shape:

```json
{
  "status": "pass",
  "failed": []
}
```

For the full deterministic slice, see
[examples/reference-loop-demo/README.md](examples/reference-loop-demo/README.md).

## Evidence

Public readiness claims are tracked in
[docs/evidence-matrix.md](docs/evidence-matrix.md). The release checklist is
in [docs/release-checklist.md](docs/release-checklist.md).

The strongest local verification commands are:

```bash
git diff --check
python3 -m compileall -q src tests
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m agent_memory_kernel.cli contract assert
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance spec-assert
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice seed --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice run --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli slice assert --db /tmp/amk-slice.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance seed --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
```

## Core Concepts

### Source Event

An append-only observed input: user message, assistant response, tool result,
imported note, document excerpt, or maintenance event. Source events are
evidence, not automatically trusted memory.

### Candidate Memory

A proposed durable memory extracted by a Keeper, imported from a source, or
recorded manually. Candidates remain reviewable or quarantined until policy or
review promotes them.

### Active Memory

A reviewed or policy-approved memory item with provenance, lifecycle state,
trust metadata, graph/evidence links, and audit history.

### Router

The pre-model read path. It selects allowed, relevant, budgeted memory and
returns prompt-ready content with reasons and source ids.

### Keeper

The post-turn write path. It records saved turns and proposes candidate memory
or graph commands. Keeper output is reviewable by default.

### Scope, Lane, Namespace

The generic isolation model for reads, writes, prompt injection, lifecycle
actions, and exports. The starter `personal` and `professional` lanes are
templates over this model, not the only ontology.

## Trust And Safety

The short public trust model is in
[docs/trust-and-security.md](docs/trust-and-security.md). Deeper references:

- [docs/threat-model.md](docs/threat-model.md)
- [docs/security-identity-contract.md](docs/security-identity-contract.md)
- [docs/memory-lifecycle-contract.md](docs/memory-lifecycle-contract.md)
- [docs/recovery.md](docs/recovery.md)

In short:

- secret-like and prompt-injection-like content is quarantined;
- untrusted assistant, tool, web, and document claims stay reviewable by
  default;
- denied, deleted, distrusted, expired, superseded, or quarantined memory fails
  closed out of prompts;
- exports have redaction and approval paths;
- local custody remains the operator's responsibility.

## Adapter Certification

Adapters should prove compatibility by running the local conformance suite, not
by copying internal assumptions. Start with
[docs/adapter-certification.md](docs/adapter-certification.md).

Minimal commands:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance spec
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance seed --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance certify --db /tmp/amk-conformance.db --adapter-name my-runtime
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance registry-entry --db /tmp/amk-conformance.db --adapter-name my-runtime
```

A neutral adapter walkthrough lives in
[examples/generic-runtime-adapter/README.md](examples/generic-runtime-adapter/README.md).
Hermes is one optional adapter example, not the identity of the project.

## Extensions

Optional extensions are documented in [docs/extensions.md](docs/extensions.md).
They include:

- local HTTP and stdio MCP mirrors;
- local browser review and graph pages;
- provider prompt formatters;
- optional embedding/rerank providers;
- outcome/domain packs;
- Digital Brain style rendering;
- operator notifications and billing reconciliation;
- runtime adapters such as Hermes.

Extension rule: an extension may add a surface, renderer, provider, or domain
workflow, but it must not bypass lifecycle, policy, prompt-boundary,
import/export, or conformance invariants.

## Project Documents

First-pass docs:

- [SPEC.md](SPEC.md): public kernel behavior spec.
- [docs/what-is-amk.md](docs/what-is-amk.md): plain-language overview.
- [docs/kernel-charter.md](docs/kernel-charter.md): project boundary.
- [docs/amk-000-kernel-invariants.md](docs/amk-000-kernel-invariants.md):
  executable invariants.
- [docs/core-status-audit.md](docs/core-status-audit.md): current gate status.
- [docs/evidence-matrix.md](docs/evidence-matrix.md): claim-to-proof map.
- [docs/public-readiness-todo.md](docs/public-readiness-todo.md):
  readiness checklist.
- [docs/roadmap.md](docs/roadmap.md): next work, split by core, extension,
  later-hosted.

Adapter and operation docs:

- [docs/adapter-contract.md](docs/adapter-contract.md)
- [docs/adapter-certification.md](docs/adapter-certification.md)
- [docs/runtime-contract.md](docs/runtime-contract.md)
- [docs/memory-lifecycle-contract.md](docs/memory-lifecycle-contract.md)
- [docs/cross-model-context-contract.md](docs/cross-model-context-contract.md)
- [docs/review-workflow.md](docs/review-workflow.md)
- [docs/recovery.md](docs/recovery.md)
- [docs/resource-budgets.md](docs/resource-budgets.md)
- [docs/prompt-keeper-snapshots.md](docs/prompt-keeper-snapshots.md)
- [docs/extensions.md](docs/extensions.md)
- [docs/hosted-roadmap.md](docs/hosted-roadmap.md)

Historical planning docs:

- [docs/full-memory-gap-plan.md](docs/full-memory-gap-plan.md)
- [docs/v0-memory-contract.md](docs/v0-memory-contract.md)

Historical docs are useful context, but they are not release authority when
they disagree with the charter, AMK-000, SPEC, or machine-readable contract.

## Project Layout

```text
SPEC.md                    public kernel behavior spec
src/agent_memory_kernel/   local reference implementation
tests/                     unit, contract, conformance, safety fixtures
docs/                      public contracts, trust model, readiness evidence
examples/                  neutral and optional runtime/domain examples
adapters/                  optional adapter examples
templates/                 starter export/import templates
.github/workflows/tests.yml public CI evidence workflow
```

## Development

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Run a CLI smoke test:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli init --db /tmp/amk-demo.db
```

## License

MIT.
