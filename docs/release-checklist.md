# Release Checklist

Use this checklist before tagging or presenting the repository as a public
`v0.1.0 alpha` artifact.

## Release Status

Public wording:

```text
v0.1.0 alpha: kernel-complete local reference implementation with executable
conformance contracts.
```

Do not describe the project as a hosted platform, managed memory service, or
final universal standard.

## Required Commands

Run from the repository root:

```bash
git status --short --branch
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

## Manual Checks

- README starts with kernel purpose, current status, what this is, what this is
  not, core loop, quickstart, evidence, trust, adapter certification, and
  extension boundary.
- [evidence-matrix.md](evidence-matrix.md) has no unsupported major public
  claims.
- [public-readiness-todo.md](public-readiness-todo.md) marks each item done or
  explicitly deferred with rationale.
- Historical docs are labeled as historical and are not first-pass release
  authority.
- Hosted/platform/provider/domain examples remain optional.
- Package version and alpha classifier match the public status language.

## CI

The GitHub workflow in [../.github/workflows/tests.yml](../.github/workflows/tests.yml)
runs the local proof commands. After pushing, confirm the workflow result before
tagging.

## Do Not Release If

- any required command fails;
- README overclaims hosted, provider, team, billing, notification, or remote
  security guarantees;
- adapter certification cannot run locally;
- conformance scenarios are stale against the contract;
- lifecycle, policy, or prompt-boundary behavior changed without updated tests
  and docs.
