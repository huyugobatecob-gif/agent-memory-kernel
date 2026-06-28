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
