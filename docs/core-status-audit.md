# Core Status Audit

This audit tracks what is already implemented, what is partial, and what is
missing for the local Agent Memory Kernel. It keeps implementation work focused
on kernel correctness instead of rebuilding completed features or drifting into
adapters, domain packs, or hosted platform work.

Status labels:

- `done`: implemented and covered by current tests or contracts.
- `partial`: implemented in the repository, but needs stronger invariant,
  conformance, or cross-surface proof.
- `missing`: required for the kernel goal and not yet represented well enough
  in code, tests, or docs.
- `extension`: useful but not a local-kernel blocker.
- `later-hosted`: future hosted/platform work.

## Kernel Core

| Capability | Status | Evidence | Remaining gate |
| --- | --- | --- | --- |
| SQLite local source of truth | done | `src/agent_memory_kernel/schema.sql`, `MemoryStore`, migration/recovery docs | Keep migrations compatible. |
| Raw source events and saved turns | done | `record_turn`, `after_saved_turn`, source event lifecycle | Ensure retained evidence cannot re-enter prompts after linked memory is inactive. |
| Candidate memory lifecycle | done | review workflow, candidate tables, quarantine policy | Keep assistant/tool/web claims reviewable by default. |
| Active memory lifecycle | partial | approve, correct, rollback, delete, distrust, expire, supersede | Prove every lifecycle change hides or invalidates all derived prompt/export surfaces. |
| Personal/professional lanes | partial | default scopes, read policies, lane isolation tests, derived summary/semantic scope fixtures | Continue lane isolation hardening for graph branches and prompt-envelope snapshots. |
| Graph nodes, edges, and evidence | partial | graph node/edge/evidence tables, browser data, graph commands | Prove graph-derived content inherits source lifecycle, trust, and lane restrictions. |
| Keeper contract | partial | deterministic extractor, LLM Keeper contract, queued worker | Expand conformance for false-positive writes, retries, and reviewable unsafe claims. |
| Router contract | partial | `before_model_call`, tree packs, explainability, feedback | Add prompt-envelope snapshots proving selected content only and deterministic budget trimming. |
| Prompt envelope / Memory Tree Supplement | partial | cross-model context contract, prompt format certification | Add golden traces for no full-graph leakage and no tag-only injection. |
| Review and explainability | partial | review inbox, memory changes, router explain, lifecycle history | Keep "why remembered" and "why injected" available across CLI/API/MCP without policy bypass. |
| Read/write/export/inject policies | partial | read/write policy enforcement, capability reports | Preserve denial paths across import/export and all direct retrieval/export surfaces. |
| Import/export provenance | partial | profile export/import, lifecycle and policy state preservation | Define and test a portable memory package format/checksum story. |
| Deterministic ranking | partial | local lexical/semantic reranking, current-best logic | Keep deterministic baseline independent of embeddings and provider calls. |
| Conformance and golden traces | partial | conformance CLI/spec/assert, acceptance harness | Add invariant matrix coverage for every kernel law and prompt-envelope snapshots. |

## Not Core

| Capability | Status | Placement |
| --- | --- | --- |
| Hermes rollout | extension | `adapters/`, examples, deployment docs |
| SEO loop memory | extension | domain pack over generic outcome records |
| Provider prompt formatters | extension | adapter compatibility, not kernel truth |
| Embeddings and ANN indexes | extension | retrieval enhancement after policy filtering |
| Rich browser UI | extension | optional operator surface over core lifecycle |
| Notifications and external senders | extension | operator workflow integration |
| Billing dashboards and invoice fetchers | extension/later-hosted | operational integration, not memory truth |
| Hosted identity, tenancy, RBAC | later-hosted | hosted/team product layer |
| KMS/off-host managed backups | later-hosted | cloud custody layer |
| Hosted registry and badge publishing | later-hosted | ecosystem service |

## Immediate Kernel Gaps

1. Build an invariant matrix that maps every kernel law to the code path and
   test/conformance scenario that proves it.
2. Harden remaining lane isolation for derived content: graph branches and
   prompt-envelope snapshots. Summaries and semantic analyses now have scoped
   source-memory fixtures.
3. Add deterministic prompt-envelope snapshots for selected content, no
   tag-only injection, no full-graph injection, and budget trimming.
4. Expand export/import round-trip tests to cover provenance, tombstones, trust
   state, review history, policy metadata, evidence chains, and derived
   invalidation records.
5. Keep examples universal until the kernel gates pass; runtime/domain examples
   must consume the kernel contract rather than shaping it.
