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
| Scope/lane/namespace isolation | partial | default scopes, read policies, lane isolation tests, derived summary/semantic fixtures, graph/evidence scope fixtures, selected-content and budget-trim prompt snapshots | Continue hardening provider-shaped prompt envelopes and namespace fixtures. |
| Graph nodes, edges, and evidence | partial | graph node/edge/evidence tables, browser data, graph commands, same-scope evidence filters | Expand graph conformance with correction/delete round trips across imported profiles. |
| Keeper contract | partial | deterministic extractor, LLM Keeper contract, queued worker | Expand conformance for false-positive writes, retries, and reviewable unsafe claims. |
| Router contract | partial | `before_model_call`, tree packs, explainability, feedback, selected-content snapshot, deterministic ranking snapshot, budget-trim snapshot, large-history bounded prompt snapshot | Expand adapter budget fixtures and latency/resource measurements. |
| Prompt envelope and renderers | partial | cross-model context contract, prompt format certification, no-full-graph conformance scenario, budget-trim conformance scenario, Memory Tree renderer | Add broader provider-shaped prompt-envelope snapshots and keep renderers behind the read contract. |
| Review and explainability | partial | review inbox, memory changes, router explain, lifecycle history | Keep "why remembered" and "why injected" available across CLI/API/MCP without policy bypass. |
| Read/write/export/inject policies | partial | read/write policy enforcement, capability reports | Preserve denial paths across import/export and all direct retrieval/export surfaces. |
| Import/export provenance | partial | profile export/import, lifecycle and policy state preservation, `.amk` bundle manifest/checksum round trip | Expand portable bundle tests across evidence chains and derived invalidation records. |
| Deterministic ranking | partial | local lexical/semantic reranking, current-best logic, deterministic ranking snapshot conformance, large-history bounded selection conformance | Expand latency/resource fixtures for very large stores. |
| Conformance and golden traces | partial | conformance CLI/spec/assert, acceptance harness, budget-trim trace, large-history bounded prompt trace | Add invariant matrix coverage for remaining kernel laws and provider-shaped prompt-envelope snapshots. |

## Not Core

| Capability | Status | Placement |
| --- | --- | --- |
| Hermes rollout | extension | `adapters/`, examples, deployment docs |
| Personal/professional starter templates | extension | default pack over generic scope/lane/namespace policy |
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

1. Keep `AMK-000` and the invariant matrix mapped to the code path and
   test/conformance scenario that proves every kernel law.
2. Expand scope/lane/namespace isolation coverage for provider-shaped prompts.
   Summaries, semantic analyses, graph branches, graph browser previews, graph
   evidence, and selected-content prompt envelopes now have scoped fixtures.
3. Add remaining deterministic prompt-envelope snapshots for provider-shaped
   prompts. Selected content, no tag-only injection, no-full-graph injection,
   and budget trimming now have local and conformance fixtures.
4. Expand export/import round-trip tests to cover provenance, tombstones, trust
   state, review history, policy metadata, evidence chains, and derived
   invalidation records.
5. Add remaining kernel-contract coverage for local API/versioning, capability
   grants, adapter budget fixtures, portable bundles, and latency/resource
   measurements. Large-history bounded selection now has local and conformance
   fixtures.
6. Keep examples universal until the kernel gates pass; runtime/domain examples
   must consume the kernel contract rather than shaping it.
