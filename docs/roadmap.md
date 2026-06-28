# Roadmap

## v0.1: Local Kernel

Status: implemented in this template.

- SQLite store.
- CLI.
- Events, candidates, active memories.
- Conversation turns, thread messages, and thread summaries.
- Memory items.
- Manual review.
- Conservative auto-approval.
- Quarantine for secret-like text.
- Persistent graph nodes and edges.
- Node and edge evidence.
- Keeper runs and graph commands audit.
- Light Model semantic analyses.
- Profile notes, project profile metadata, and profile export.
- LLM usage stats.
- Graph groups, optimization runs, and Digital Brain calibration.
- Context packs.
- Memory Tree Packs.
- Context builder packs.
- Markdown vault export.
- Tests.

## v0.2: Outcome Memory

Goal: make iterative work smarter.

Planned:

- first-class `attempt`, `outcome`, `lesson`, `pattern`, `gotcha` kinds;
- outcome scoring;
- success/failure comparison;
- reusable rule extraction;
- conflict detection between old and new rules;
- project-level tree packs;
- success/failure branches inside tree packs.

This is the layer that makes loops powerful for SEO projects, QA projects,
research projects, and agent optimization.

## v0.2 Full Memory Gap

The automatic memory gap plan is tracked in
[full-memory-gap-plan.md](full-memory-gap-plan.md). It adds the missing
production layers around the local kernel:

- pre-turn Memory Router;
- post-turn Keeper;
- prompt envelope;
- Hermes before/after hooks;
- API/MCP service mode;
- background worker;
- review and security hardening.

Before v0.2 can be called full memory, these contracts must be implemented and
tested:

- [runtime-contract.md](runtime-contract.md): pre-call Router, post-turn Keeper,
  and failure behavior.
- [memory-lifecycle-contract.md](memory-lifecycle-contract.md): create,
  correct, delete, distrust, expire, conflict, and export behavior.
- [cross-model-context-contract.md](cross-model-context-contract.md):
  provider-neutral prompt envelope and `MEMORY_TREE_SUPPLEMENT`.
- [security-identity-contract.md](security-identity-contract.md): identity,
  scopes, permissions, audit, redaction, and poisoning defense.
- [end-to-end-vertical-slice.md](end-to-end-vertical-slice.md): executable
  save-retrieve-ingest scenario with permission and poisoning checks.

Current status: the first local runtime hook slice exists through
`before-model-call`, `after-saved-turn`, `MemoryStore.before_model_call()`,
`MemoryStore.after_saved_turn()`, and the Hermes provider wrapper. It proves the
Router/envelope/Keeper candidate loop. The richer `slice seed/run/assert`
fixture now checks corrected memory, deleted memory, professional/personal lane
separation, success/failure loop retrieval, and poisoning quarantine. Full v0.2
still requires the remaining permission and service-mode gates above.
Delete, distrust, and expire now suppress retrieval and active graph export.

## v0.3: Adapters

Goal: let agent frameworks use the kernel without copy-pasting logic.

Planned:

- Hermes provider adapter;
- simple HTTP API;
- MCP server;
- file-based vault adapter;
- optional OpenAI extractor;
- optional provider embeddings;
- optional semantic reranker.

## v0.4: Review UI

Goal: make memory maintenance practical for non-technical users.

Planned:

- review inbox;
- approve/reject/correct flows;
- source preview;
- graph browser;
- conflict warnings;
- export controls.

## v1.0: Stable Memory Contract

Goal: stable interfaces for external users.

Requirements:

- documented migration path;
- stable schema;
- stable provider interface;
- security review;
- import/export format;
- production examples.
