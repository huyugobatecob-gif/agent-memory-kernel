# Roadmap

## v0.1: Local Kernel

Status: implemented in this template.

- SQLite store.
- CLI.
- Events, candidates, active memories.
- Manual review.
- Conservative auto-approval.
- Quarantine for secret-like text.
- Basic graph nodes and edges.
- Context packs.
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
- project-level memory packs.

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
- optional embedding search.

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
