# Public Readiness To Do

This list turns the council review into a concrete work queue.

Current truthful status:

```text
v0.1.0 alpha: kernel-complete local reference implementation with executable
conformance contracts.
```

Do not market the repository as a fully universal memory standard until the
public surface, trust model, release evidence, and adapter story are tightened.

Baseline evidence at the time this list was created:

- commit: `75b9a21`
- `PYTHONPATH=src python3 -m agent_memory_kernel.cli contract assert`: pass
- `PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance spec-assert`: pass
- `PYTHONPATH=src python3 -m unittest discover -s tests`: 120 tests OK

## P0: Public Front Door

Goal: make a new external reader understand the kernel in five minutes without
reading historical project context.

- [ ] Rewrite the top of `README.md` around the core causal pipeline:
  `source event -> candidate -> review/policy -> active memory -> evidence ->
  Router-selected prompt envelope -> saved turn -> Keeper proposal`.
- [ ] Replace the long headline feature inventory with a short kernel-only
  summary.
- [ ] Move platform-like features out of the first-pass README path:
  HTTP/MCP deployment, browser UI, billing, notifications, Digital Brain,
  embeddings, Hermes, SEO, production rollout, hosted/team concepts.
- [ ] Add a "What this is not" section near the top:
  not hosted SaaS, not runtime orchestrator, not vector DB, not billing or
  notification system, not Hermes/SEO-specific.
- [ ] Add a "Current status" block that reconciles `v0.1.0`, alpha package
  metadata, and "v1 gates done" language.
- [ ] Keep extension links, but place them after the kernel quickstart and
  conformance evidence.

Done when:

- a first-time reader can tell what is core in under five minutes;
- README no longer reads like a platform feature inventory;
- `v0.1.0 alpha` and internal v1-gate language no longer conflict.

## P0: Five-Minute Kernel Quickstart

Goal: prove the kernel loop without domain, hosted, provider, or runtime setup.

- [ ] Add a minimal quickstart section that runs only local commands:
  `init`, `remember`, `review`, `before-model-call`, `after-saved-turn`,
  `memory-explain`, and `conformance assert`.
- [ ] Add expected output snippets for the successful path.
- [ ] Add one "no memory allowed" or denied-policy example so fail-closed
  behavior is visible.
- [ ] Point to `examples/reference-loop-demo/README.md` only after the minimal
  quickstart.

Done when:

- a user can install and verify the local kernel without reading extension docs;
- the quickstart uses neutral project-iteration examples, not SEO or Hermes.

## P0: Evidence Matrix

Goal: make every readiness claim traceable to a command, test, or document.

- [ ] Create a matrix with columns: claim, command/test, doc, current status,
  and last verified commit.
- [ ] Include at least these claims:
  local source of truth, candidate lifecycle, active lifecycle, prompt boundary,
  Keeper safety, Router selection, scope/lane/namespace isolation,
  import/export provenance, recovery/versioning, audit/explainability,
  conformance, and no-memory fallback.
- [ ] Link this matrix from README and `docs/core-status-audit.md`.
- [ ] Record the latest known evidence for commit `75b9a21`, then keep it
  updated when tests or docs change.

Done when:

- no major public readiness claim depends on prose alone;
- future contributors can update evidence without reading the whole repo.

## P0: Status And Roadmap Reconciliation

Goal: remove contradictory release language.

- [ ] Decide the public wording:
  `v0.1.0 alpha, kernel-complete local reference implementation`.
- [ ] Update `README.md`, `docs/roadmap.md`, and
  `docs/core-status-audit.md` to use the same wording.
- [ ] Replace old `partial` / `missing` roadmap language with current
  `done`, `extension`, `later-hosted`, and `post-v1 hardening` language.
- [ ] Make `docs/full-memory-gap-plan.md` and `docs/v0-memory-contract.md`
  visibly historical at the top and remove them from first-pass navigation.

Done when:

- there is one public status story;
- historical docs cannot be mistaken for current release authority.

## P0: Extension And Archive Cut

Goal: prevent extension sprawl from weakening the kernel boundary.

- [ ] Create or designate an extension docs area for:
  HTTP/MCP deployment, browser UI, billing, notifications, Digital Brain,
  embeddings, Hermes, SEO/domain packs, production rollout, hosted/team
  concepts.
- [ ] Move or relabel first-pass references so extensions consume the kernel
  contract rather than define it.
- [ ] Add a short extension rule:
  extensions must not bypass lifecycle, policy, prompt-boundary, or
  import/export invariants.
- [ ] Ensure `README.md` and `docs/roadmap.md` point to extension docs only
  after the kernel contract and quickstart.

Done when:

- deleting extension examples would not change the core contract;
- no extension feature appears as required for local v0.1.0 use.

## P1: Trust, Privacy, And Security Front Door

Goal: make "auditable memory" credible for sensitive long-lived state.

- [ ] Add a short public trust model page or front-door section that summarizes:
  secrets, PII, redaction, deletion, retention, prompt-injection resistance,
  memory poisoning, tamper evidence, backup/restore, and corrupted-store
  behavior.
- [ ] Link existing deeper docs:
  `docs/threat-model.md`, `docs/security-identity-contract.md`,
  `docs/memory-lifecycle-contract.md`, and `docs/recovery.md`.
- [ ] Add a plain-language "when memory is wrong or harmful" section:
  correct, rollback, delete, distrust, expire, supersede, quarantine.
- [ ] Clarify local file and database custody assumptions.
- [ ] Clarify what the kernel does not guarantee without a hosted/security
  wrapper: tenant isolation, remote auth, cloud KMS, team RBAC.

Done when:

- a cautious adopter can understand privacy and safety boundaries before
  installing;
- trust claims are tied to tests or explicit non-goals.

## P1: Governance And Compatibility Policy

Goal: make third-party adopters understand what can change.

- [ ] Add a compatibility policy for:
  schema version, contract version, conformance version, CLI behavior, Python
  API behavior, bundle format, and migration expectations.
- [ ] Clarify what counts as a breaking change.
- [ ] Clarify how adapter certification changes over time.
- [ ] Add maintainer expectations for accepting extensions, adapters, and
  contract changes.
- [ ] Keep MIT license visible, but add governance notes beyond the license.

Done when:

- outside adapters know what compatibility promise they can rely on;
- future schema/contract changes have a documented path.

## P1: Adapter Certification Path

Goal: make the executable conformance contract the main adoption path.

- [ ] Add a "Certify your adapter" guide.
- [ ] Include the exact commands:
  `conformance spec`, `conformance seed`, `conformance assert`,
  `conformance certify`, and `conformance registry-entry`.
- [ ] Add a minimal example adapter that is not Hermes-specific.
- [ ] Add a sample local compatibility badge output.
- [ ] Add a checklist for adapters:
  no full-graph prompt injection, no policy bypass, no lifecycle bypass,
  no untrusted auto-promotion, import/export provenance preserved.

Done when:

- an external runtime can prove compatibility without private project context;
- Hermes is clearly one optional adapter, not the reference identity.

## P1: Independent And Adversarial Fixtures

Goal: strengthen "universal" claims with evidence outside the current fixture.

- [ ] Add third-party namespace adversarial fixtures for:
  agent roles, import packages, bundles, and domain packs.
- [ ] Add import-path fixtures for hostile or malformed external sources beyond
  the current bundle coverage.
- [ ] Add corrupted-store and stale-backup recovery drills beyond current
  migration, quick-check, backup/restore, and interrupted bundle rollback.
- [ ] Add interrupted export and interrupted non-bundle import tests.
- [ ] Add cross-version bundle/import matrices when a second public schema or
  contract version exists.

Done when:

- "universal" has evidence across multiple namespaces and adapter-like paths;
- adversarial import and recovery behavior is not only bundle-specific.

## P1: CI And Release Evidence

Goal: make test evidence visible without trusting local claims.

- [ ] Add CI that runs:
  py_compile, unit tests, contract assert, conformance spec-assert, slice
  seed/run/assert, conformance seed/assert, and `git diff --check`.
- [ ] Publish CI status in README once the workflow exists.
- [ ] Add release checklist output tied to exact commit ids.
- [ ] Add signed or reproducible release notes if the package is published.
- [ ] Decide whether to tag `v0.1.0` or keep it as source-only alpha until
  public docs are cut down.

Done when:

- a reader can verify the repo state from CI, not only local notes;
- release artifacts match package metadata and docs.

## P2: Scale And Resource Proof

Goal: avoid overclaiming performance while keeping local-first reliability.

- [ ] Add larger local-history benchmarks beyond deterministic bounded-history
  conformance.
- [ ] Record retrieval latency, prompt-build latency, export size, import size,
  and backup/restore time for representative local stores.
- [ ] Define soft budget targets for v0.1.0 and explicit non-goals for larger
  deployments.
- [ ] Keep ANN/vector/provider reranking as optional post-policy extensions.

Done when:

- README can make bounded, honest resource claims;
- performance work does not become a hidden provider or hosted dependency.

## P2: Live Prompt And Keeper Snapshots

Goal: show real adapter-shaped behavior without live provider dependence.

- [ ] Add neutral prompt-envelope snapshots for at least two adapter shapes.
- [ ] Add Keeper proposal snapshots for direct user, assistant guess, tool
  output, and imported document cases.
- [ ] Keep snapshots deterministic and provider-free.
- [ ] Use live provider examples only as optional extension evidence.

Done when:

- users can inspect what the main model would receive;
- unsafe Keeper behavior remains visibly reviewable.

## Not In This To Do

These are useful later, but they should not block the public v0.1.0 kernel
front door:

- hosted SaaS;
- remote hosted MCP;
- billing product;
- live notification senders;
- team RBAC;
- hosted registry;
- cloud KMS/off-host custody;
- domain packs beyond examples;
- provider-specific live certification.
