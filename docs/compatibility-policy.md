# Compatibility Policy

This policy explains what third-party adapters can rely on during the
`v0.1.x` alpha line.

## Versioned Surfaces

The kernel exposes several versioned surfaces:

| Surface | Compatibility signal | Notes |
| --- | --- | --- |
| Package | `pyproject.toml` version | `0.1.x` is alpha. |
| Contract | `memory_contract()` and `contract assert` | Machine-readable behavioral contract. |
| Conformance | `conformance spec` and `conformance assert` | Public adapter behavior scenarios. |
| Schema | SQLite `user_version` and migration status | Local reference store version. |
| Bundle | `.amk` manifest version | Portable profile bundle format. |
| Lifecycle diff | `memory-diff-v0.1` | Human-readable mutation report shape. |
| Keeper extraction | `keeper-extraction-v0.1` | Low-cost model extraction contract. |

## Alpha Promise

During `0.1.x`, the project aims to keep the core behavioral contract stable
enough for local experimentation and adapter certification. It may still change
details when needed to preserve safety, lifecycle correctness, or conformance
clarity.

## Breaking Changes

A change is breaking if it removes or changes the meaning of:

- core lifecycle commands or their safety behavior;
- contract or conformance scenario ids;
- prompt-envelope selected-memory semantics;
- bundle fields required for provenance, lifecycle, policy, or audit;
- schema migrations without a compatibility path;
- reviewable Keeper behavior for untrusted sources;
- fail-closed behavior for denied, unsafe, inactive, or inaccessible memory.

Breaking changes should update:

- [SPEC.md](../SPEC.md)
- `memory_contract()`
- conformance scenarios
- [evidence-matrix.md](evidence-matrix.md)
- [release-checklist.md](release-checklist.md)
- migration or import/export docs when relevant

## Adapter Certification Drift

Adapters should not certify once and assume indefinite compatibility. Re-run:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance seed --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert --db /tmp/amk-conformance.db
PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance certify --db /tmp/amk-conformance.db --adapter-name my-runtime
```

Re-certify after:

- package version changes;
- contract or conformance version changes;
- adapter code changes;
- prompt formatting changes;
- import/export behavior changes;
- policy, identity, or lifecycle behavior changes.

## Extension Governance

Extensions are welcome when they consume the kernel contract. An extension must
not:

- promote untrusted memory without review or explicit policy;
- inject the full graph or raw database into prompts;
- bypass scope/lane/namespace isolation;
- revive deleted, distrusted, expired, superseded, rejected, or quarantined
  memory through a derived surface;
- export sensitive memory without redaction or approval paths;
- imply hosted security guarantees that the local kernel does not provide.

## Maintainer Expectations

Before accepting a compatibility-impacting change, maintainers should ask:

1. Does this strengthen or weaken the core memory lifecycle?
2. Does it need a conformance scenario?
3. Does it change adapter expectations?
4. Does it belong in core, extension, or later-hosted?
5. Is the README claim still backed by evidence?
