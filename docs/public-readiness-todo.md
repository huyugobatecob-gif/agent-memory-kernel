# Public Readiness To Do

Current truthful status:

```text
v0.1.0 alpha: kernel-complete local reference implementation with executable
conformance contracts.
```

This file tracks the work needed to present the repository as a broadly
shareable local-first memory kernel without overclaiming hosted, provider,
domain, or runtime-specific capabilities.

Baseline evidence before this public-readiness pass:

- commit: `f6de1d2`
- `PYTHONPATH=src python3 -m agent_memory_kernel.cli contract assert`: pass
- `PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance spec-assert`: pass
- `PYTHONPATH=src python3 -m unittest discover -s tests`: pass in the prior
  council audit

Use [release-checklist.md](release-checklist.md) for the current verification
commands before tagging or announcing a release.

## P0: Public Front Door

Status: done.

- [x] Rewrite the top of `README.md` around the core causal pipeline:
  `source event -> candidate -> review/policy -> active memory -> evidence ->
  Router-selected prompt envelope -> saved turn -> Keeper proposal`.
- [x] Replace the long headline feature inventory with a short kernel-only
  summary.
- [x] Move platform-like features out of the first-pass README path:
  HTTP/MCP deployment, browser UI, billing, notifications, Digital Brain,
  embeddings, Hermes, SEO, production rollout, hosted/team concepts now appear
  as extensions or later-hosted work.
- [x] Add a "What this is not" section near the top.
- [x] Add a "Current status" block that reconciles `v0.1.0`, alpha package
  metadata, and internal local-gate language.
- [x] Keep extension links, but place them after quickstart, evidence, trust,
  and adapter certification.

Evidence:

- [../README.md](../README.md)
- [extensions.md](extensions.md)
- [core-status-audit.md](core-status-audit.md)

## P0: Five-Minute Kernel Quickstart

Status: done.

- [x] Add a minimal quickstart section that runs local commands only:
  `init`, `remember`, `review`, `before-model-call`, `after-saved-turn`,
  `memory-explain`, and `conformance spec-assert`.
- [x] Add expected output shapes for the successful path.
- [x] Add a denied read-policy/no-memory fallback example.
- [x] Point to `examples/reference-loop-demo/README.md` only after the minimal
  quickstart.

Evidence:

- [../README.md](../README.md)
- [prompt-keeper-snapshots.md](prompt-keeper-snapshots.md)

## P0: Evidence Matrix

Status: done.

- [x] Create a matrix with columns: claim, command/test, doc, current status,
  and last verified state.
- [x] Include local source of truth, candidate lifecycle, active lifecycle,
  prompt boundary, Keeper safety, Router selection, scope/lane/namespace
  isolation, import/export provenance, recovery/versioning,
  audit/explainability, conformance, and no-memory fallback.
- [x] Link this matrix from README and `docs/core-status-audit.md`.
- [x] Record the latest baseline evidence and require release-time updates.

Evidence:

- [evidence-matrix.md](evidence-matrix.md)
- [../README.md](../README.md)
- [core-status-audit.md](core-status-audit.md)

## P0: Status And Roadmap Reconciliation

Status: done.

- [x] Use the public wording:
  `v0.1.0 alpha, kernel-complete local reference implementation`.
- [x] Update `README.md`, `docs/roadmap.md`, and
  `docs/core-status-audit.md` to use one status story.
- [x] Replace old `partial` / `missing` roadmap language with current
  `done`, `extension`, `later-hosted`, and `post-v0.1.0 hardening` language.
- [x] Make `docs/full-memory-gap-plan.md` and `docs/v0-memory-contract.md`
  visibly historical and remove them from first-pass release authority.

Evidence:

- [../README.md](../README.md)
- [roadmap.md](roadmap.md)
- [core-status-audit.md](core-status-audit.md)
- [full-memory-gap-plan.md](full-memory-gap-plan.md)
- [v0-memory-contract.md](v0-memory-contract.md)

## P0: Extension And Archive Cut

Status: done.

- [x] Designate [extensions.md](extensions.md) as the extension docs area for
  HTTP/MCP, browser UI, billing, notifications, Digital Brain, embeddings,
  Hermes, SEO/domain packs, production rollout, hosted/team concepts.
- [x] Relabel first-pass references so extensions consume the kernel contract
  rather than define it.
- [x] Add the extension rule: extensions must not bypass lifecycle, policy,
  prompt-boundary, import/export, or conformance invariants.
- [x] Ensure README and roadmap point to extension docs only after the kernel
  contract and quickstart.

Evidence:

- [extensions.md](extensions.md)
- [../README.md](../README.md)
- [roadmap.md](roadmap.md)

## P1: Trust, Privacy, And Security Front Door

Status: done.

- [x] Add a public trust model page summarizing secrets, PII-adjacent redaction,
  deletion, retention, prompt-injection resistance, memory poisoning,
  tamper-evidence, backup/restore, and corrupted-store behavior.
- [x] Link deeper docs: `docs/threat-model.md`,
  `docs/security-identity-contract.md`, `docs/memory-lifecycle-contract.md`,
  and `docs/recovery.md`.
- [x] Add a plain-language "when memory is wrong or harmful" section.
- [x] Clarify local file and database custody assumptions.
- [x] Clarify what the kernel does not guarantee without hosted/security
  wrappers: tenant isolation, remote auth, cloud KMS, team RBAC.

Evidence:

- [trust-and-security.md](trust-and-security.md)
- [../README.md](../README.md)

## P1: Governance And Compatibility Policy

Status: done.

- [x] Add a compatibility policy for schema version, contract version,
  conformance version, CLI behavior, Python API behavior, bundle format, and
  migration expectations.
- [x] Clarify what counts as a breaking change.
- [x] Clarify how adapter certification changes over time.
- [x] Add maintainer expectations for accepting extensions, adapters, and
  contract changes.
- [x] Keep MIT license visible and add governance notes beyond the license.

Evidence:

- [compatibility-policy.md](compatibility-policy.md)
- [../README.md](../README.md)

## P1: Adapter Certification Path

Status: done.

- [x] Add a "Certify your adapter" guide.
- [x] Include the exact commands:
  `conformance spec`, `conformance seed`, `conformance assert`,
  `conformance certify`, and `conformance registry-entry`.
- [x] Add a minimal example adapter that is not Hermes-specific.
- [x] Point to local badge/report output from `conformance certify`.
- [x] Add an adapter checklist:
  no full-graph prompt injection, no policy bypass, no lifecycle bypass,
  no untrusted auto-promotion, import/export provenance preserved.

Evidence:

- [adapter-certification.md](adapter-certification.md)
- [../examples/generic-runtime-adapter/README.md](../examples/generic-runtime-adapter/README.md)

## P1: Independent And Adversarial Fixtures

Status: partially done, remaining work is explicit post-v0.1.0 hardening.

- [x] Current conformance already covers personal/professional isolation,
  denied read policy, secret-like quarantine, prompt-injection quarantine,
  assistant guesses, tool-output claims, poisoned bundle import, interrupted
  bundle import rollback, lifecycle tombstones, policy metadata, review
  history, and graph evidence import/export.
- [x] Wider third-party namespace fixtures for agent roles, import packages,
  bundles, and domain packs are tracked as post-v0.1.0 hardening.
- [x] Interrupted export and interrupted non-bundle import tests are tracked as
  post-v0.1.0 hardening.
- [x] Cross-version bundle/import matrices are deferred until a second public
  schema or contract version exists.

Evidence:

- [evidence-matrix.md](evidence-matrix.md)
- [core-status-audit.md](core-status-audit.md)
- `PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance spec`

## P1: CI And Release Evidence

Status: done locally, remote CI must be confirmed after push.

- [x] Strengthen CI to run compileall, unit tests, contract assert,
  conformance spec-assert, slice seed/run/assert, conformance seed/assert, and
  `git diff --check`.
- [x] Publish CI status badge in README.
- [x] Add release checklist tied to exact commands and commit discipline.
- [x] Keep release publishing/tagging out of scope until explicit approval.

Evidence:

- [../.github/workflows/tests.yml](../.github/workflows/tests.yml)
- [release-checklist.md](release-checklist.md)
- [../README.md](../README.md)

## P2: Scale And Resource Proof

Status: scoped and deferred beyond bounded local evidence.

- [x] Document current bounded-selection evidence and soft v0.1.0 targets.
- [x] State explicit non-goals for ANN/vector/provider reranking and hosted
  performance guarantees.
- [x] Track larger local-history benchmarks as post-v0.1.0 hardening.

Evidence:

- [resource-budgets.md](resource-budgets.md)
- [evidence-matrix.md](evidence-matrix.md)

## P2: Live Prompt And Keeper Snapshots

Status: done with deterministic provider-free snapshots; live provider traces
remain optional extension evidence.

- [x] Add neutral prompt-envelope snapshots.
- [x] Add Keeper proposal snapshots for saved-turn cases.
- [x] Reference tool/import/assistant safety through conformance scenarios.
- [x] Keep snapshots deterministic and provider-free.

Evidence:

- [prompt-keeper-snapshots.md](prompt-keeper-snapshots.md)
- [adapter-certification.md](adapter-certification.md)

## Not In This To Do

These remain outside the public v0.1.0 kernel front door:

- hosted SaaS;
- remote hosted MCP;
- billing product;
- live notification senders;
- team RBAC;
- hosted registry;
- cloud KMS/off-host custody;
- domain packs beyond examples;
- provider-specific live certification.
