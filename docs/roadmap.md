# Roadmap

This roadmap follows the [Kernel Charter](kernel-charter.md),
[AMK-000](amk-000-kernel-invariants.md), and
[Backlog Cutover](backlog-cutover.md).

The project should remain a local-first memory kernel. Adapters, packs,
embeddings, hosted services, and domain rollouts are valuable only when they
consume the kernel contract instead of redefining it.

The public spec is [../SPEC.md](../SPEC.md), and the current implementation
state is tracked in [core-status-audit.md](core-status-audit.md).

## v0.1: Local Kernel Baseline

Status: implemented in this template.

Included:

- SQLite source of truth;
- CLI;
- source events, candidates, active memories;
- conversation turns, thread messages, and summaries;
- generic scope/lane/namespace policy isolation with personal/professional
  starter templates;
- memory items;
- manual review and conservative auto-approval;
- quarantine for secret-like and prompt-injection-like content;
- persistent graph nodes, graph edges, node evidence, and edge evidence;
- Keeper runs, graph command normalization, and graph command audit;
- context packs, Memory Tree Packs, and context builder packs;
- write-policy and read-policy enforcement;
- correction, deletion, distrust, expiration, supersession, and rollback paths;
- export control, redaction profiles, encrypted export/import, vault export,
  retention, and approval flows;
- backup, restore, migration, and restore-drill commands;
- local HTTP API, stdio MCP server, and worker processing;
- formal Memory Contract, acceptance harness, and conformance suite;
- provider-neutral runtime loop and reference demo.

## v0.2: Kernel Charter Cutover

Goal: make the repository read as a memory kernel, not a platform roadmap.

Core work:

- keep [../SPEC.md](../SPEC.md) as the public kernel behavior spec;
- keep [kernel-charter.md](kernel-charter.md) as the governing boundary;
- keep [amk-000-kernel-invariants.md](amk-000-kernel-invariants.md) as the
  executable invariant contract;
- keep [backlog-cutover.md](backlog-cutover.md) as the classification rule for
  new work;
- keep [core-status-audit.md](core-status-audit.md) current with `done`,
  `partial`, `missing`, `extension`, and `later-hosted` status;
- keep [implementation-plan.md](implementation-plan.md) scoped to local kernel
  completion;
- move hosted/platform work to [hosted-roadmap.md](hosted-roadmap.md);
- keep domain and runtime examples under `examples/` and `adapters/`;
- keep optional retrieval and provider work as extensions.

Done when:

- contributors can identify `core`, `extension`, and `later-hosted` work;
- hosted features are not local full-memory blockers;
- personal/professional templates do not define the kernel ontology;
- runtime/domain examples point back to the kernel contract.

## v0.3: Memory Safety Invariants

Goal: make memory governance enforceable.

Core work:

- deleted memory cannot reappear from retained evidence;
- distrusted sources cannot influence retrieval, summaries, or derived memory;
- scope/lane/namespace boundaries cannot leak across prompt, graph, summary,
  browser, or export surfaces by default;
- derived memory invalidates after correction, deletion, distrust, expiration,
  or supersession;
- exports preserve provenance, tombstones, trust state, policy metadata, review
  history, and evidence chains;
- prompt envelopes contain selected, policy-filtered, budgeted memory only,
  never the full graph;
- local actors cannot bypass capability grants;
- local histories stay bounded and predictable.
- maintain an invariant matrix that maps each law to code paths and executable
  proof.

Evidence required:

- invariant tests;
- conformance golden traces;
- lifecycle mutation reports;
- export/import fixtures;
- prompt-envelope fixtures;
- bounded-selection fixtures;
- latency/resource fixtures.

## v0.4: Reference Loop And Explainability

Goal: make the local loop boring, inspectable, and easy to operate.

Core work:

- preserve raw turns before Keeper extraction;
- keep Keeper writes reviewable by default;
- keep Router retrieval deterministic and policy-filtered;
- expose selected/skipped branch reasons;
- add or strengthen human-readable memory diffs;
- add or strengthen "why this memory exists" reports;
- keep review, correction, delete, distrust, expire, and rollback flows
  available through stable interfaces.

Evidence required:

- `slice seed/run/assert`;
- review inbox and lifecycle tests;
- Router explainability tests;
- no-memory fallback tests.

## v0.5: Portable Bundles, API, And Resource Budgets

Goal: make the kernel portable and dependable for third-party adopters.

Core work:

- stable CLI/API surface and versioning policy;
- `.amk` portable bundle manifest with schema and contract versions;
- import/export round trips preserving ids, provenance, policies, evidence,
  review history, pending/rejected review queues, lifecycle state, and
  tombstones;
- policy simulator and dry-run behavior for read/write/inject/export/lifecycle;
- deterministic ranking spec with stable tie-breakers;
- local capability grants for actors and adapters;
- latency/resource budgets for large histories beyond bounded selection.

Evidence required:

- bundle round-trip tests;
- policy dry-run fixtures;
- ranking golden traces;
- API/versioning checks;
- bounded-selection golden traces;
- latency/resource fixtures.

## v0.6: Adapter Contracts

Goal: let external systems use the kernel without copying internal assumptions.

Extension work:

- runtime adapter contract for pre-call retrieval and post-turn Keeper work;
- importer/exporter contract for provenance and lifecycle preservation;
- retrieval-enhancer contract for embeddings or rerankers after policy
  filtering;
- adapter capability levels: read-only, write-capable, lifecycle-capable,
  graph-capable, export-capable, and prompt-injection capable;
- local adapter certification through conformance scenarios.

Examples:

- provider-neutral reference loop;
- personal/professional starter templates;
- chat agent adapter;
- coding agent adapter;
- optional Hermes adapter;
- notes/vault importer.

## v0.7: Domain Packs

Goal: support iterative workflows without turning them into kernel assumptions.

Extension work:

- outcome loop pack;
- SEO loop pack;
- research memory pack;
- support/CRM memory pack;
- QA/testing memory pack.

Rules:

- packs must use core memory kinds and policies;
- packs may add graph conventions and examples;
- packs must not require hosted infrastructure;
- packs must not bypass review or lifecycle invariants.

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

None of these are blockers for the local full-memory kernel.
