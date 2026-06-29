# Roadmap

This roadmap follows the [Kernel Charter](kernel-charter.md),
[AMK-000](amk-000-kernel-invariants.md), [SPEC](../SPEC.md), and
[Backlog Cutover](backlog-cutover.md).

Public status:

```text
v0.1.0 alpha: kernel-complete local reference implementation with executable
conformance contracts.
```

The project should remain a local-first memory kernel. Adapters, packs,
embeddings, hosted services, and domain rollouts are valuable only when they
consume the kernel contract instead of redefining it.

## v0.1.0 Alpha: Local Kernel Reference

Status: implemented as a local reference implementation and covered by the
release checklist in [release-checklist.md](release-checklist.md).

Included:

- SQLite local source of truth;
- source events, candidates, active memories, review history, audit trails;
- Router-selected prompt envelopes;
- Keeper saved-turn and candidate proposal path;
- graph/evidence records and Memory Tree rendering;
- scope/lane/namespace isolation;
- read/write/export/lifecycle policy checks;
- correction, rollback, delete, distrust, expire, supersede, conflict, and
  current-best flows;
- profile/bundle/vault export and import with provenance and redaction;
- backup, restore, migration, and recovery checks;
- formal memory contract, acceptance harness, conformance suite, and
  deterministic vertical slice;
- optional local HTTP, stdio MCP, browser UI, provider formatter, embedding,
  notification, billing, and adapter examples as extension surfaces.

Not included as v0.1.0 blockers:

- hosted SaaS;
- hosted multi-user API/UI;
- hosted team RBAC;
- remote hosted MCP;
- cloud KMS/off-host custody;
- managed billing or notification delivery;
- hosted registry and badge publication;
- live provider certification;
- production rollout into any named runtime.

## v0.1.x Public Hardening

Goal: make the alpha easier for outside adopters to understand, verify, and
extend without private project context.

Core/public work:

- keep README kernel-first;
- keep [evidence-matrix.md](evidence-matrix.md) current;
- keep [trust-and-security.md](trust-and-security.md) visible from the front
  door;
- keep [compatibility-policy.md](compatibility-policy.md) current with schema,
  contract, conformance, CLI, Python API, and bundle changes;
- keep [adapter-certification.md](adapter-certification.md) as the main
  external adoption path;
- keep CI green for tests, contract assert, conformance spec assert, vertical
  slice, conformance fixture, compileall, and whitespace checks.

Post-v0.1.0 hardening:

- wider third-party namespace adversarial fixtures;
- interrupted export and interrupted non-bundle import fixtures;
- stale-backup and corrupted-store drills beyond current recovery evidence;
- larger local resource benchmarks;
- adapter-specific prompt and Keeper snapshots;
- cross-version bundle/import matrices once a second public schema or contract
  version exists.

## v0.2: Adapter Ecosystem

Goal: let external systems use the kernel without copying internal assumptions.

Extension work:

- neutral runtime adapter examples;
- adapter certification reports and local badge output;
- importer/exporter compatibility examples;
- retrieval-enhancer examples that run after policy filtering;
- provider formatter examples that keep memory outside hidden system surfaces;
- optional runtime adapters such as Hermes, LangGraph, AutoGen, CrewAI, chat
  apps, coding agents, and notes/vault systems.

Rules:

- adapters must pass local conformance before claiming compatibility;
- adapters must not inject the full graph or raw database into prompts;
- adapters must not bypass review, lifecycle, policy, import/export, or prompt
  boundary invariants.

## v0.3: Domain And Outcome Packs

Goal: support iterative workflows without turning them into kernel assumptions.

Extension work:

- outcome loop pack;
- research memory pack;
- support/CRM memory pack;
- QA/testing memory pack;
- SEO loop pack as one optional domain example;
- personal/professional starter templates maintained as default packs.

Rules:

- packs must use core memory kinds and policies;
- packs may add graph conventions and examples;
- packs must not require hosted infrastructure;
- packs must not bypass review or lifecycle invariants;
- packs must not define the kernel ontology.

## Later Hosted

Tracked in [hosted-roadmap.md](hosted-roadmap.md).

Later-hosted work includes:

- hosted multi-user API/UI;
- tenancy, RBAC, and team administration;
- hosted dashboards, billing, and managed alerting;
- remote MCP hosting;
- KMS/off-host backup custody;
- managed schedulers;
- hosted adapter registry and badge publishing;
- live provider certification;
- hosted sync and collaboration.

None of these are blockers for the local v0.1.0 alpha kernel.
