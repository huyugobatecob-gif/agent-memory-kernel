# Memory Tree Pack

Memory Tree Pack is the branch-oriented retrieval format for agents that need
working context before planning or execution.

It is not a replacement for storage. It is a retrieval view over the persistent
graph-tree storage:

```text
conversation_turns / events
  -> candidate memories
  -> active memories
  -> memory_items
  -> memory_graph_nodes / memory_graph_edges
  -> node_evidence / edge_evidence
  -> tree pack
```

## Why It Exists

Flat memory search answers "which notes mention this query?" A tree pack answers
"which prior branches of work should the agent understand before acting?"

This matters when old dialogue, decisions, failed attempts, or successful
patterns are relevant but should not be dumped into the prompt wholesale.

## Shape

```text
Root
  query
  scope
  retrieval mode

Branch
  category / label
  why selected
  active memories
  related nodes
  memory graph nodes
  relationships
  raw provenance
```

The top of the tree stays compact. The bottom of the tree keeps enough raw
source material for an agent to understand what actually happened.

## Retrieval Layers

The deterministic v0 implementation uses five layers:

1. Active memory text search.
2. Legacy graph node search for compatibility.
3. Persistent graph node search over labels, node types, blobs, summaries, and
   linked memory items.
4. Dependency-free semantic reranking over active memories, compact items, and
   graph summaries/blobs.
5. Optional graph neighbor expansion by depth.

Future implementations can replace or enrich the local reranker with provider
embeddings or an LLM extractor without changing the output contract.

## Persistent Graph Tree

The graph-tree layer is made of:

- `memory_items`: compact durable facts, decisions, rules, attempts, outcomes,
  gotchas, and patterns.
- `memory_graph_nodes`: deduplicated nodes such as People, Projects, Interests,
  Documents, Data, Tools, Rules, Decisions, Attempts, Outcomes, Gotchas, and
  Patterns.
- `memory_graph_edges`: weighted relationships between nodes.
- `node_evidence` and `edge_evidence`: source-backed proof for every node and
  relationship.
- `keeper_runs` and `graph_commands`: audit trail for extraction and applied
  graph updates.
- `memory_graph_groups`: grouped counts for graph browsers.
- `semantic_analyses`: facts, chronology, key topics, people, events, and
  verified entities.
- `graph_optimization_runs`: record-linkage, consistency, LLM-check,
  interests-reconnect, hemisphere-markup, and brain-calibration runs.
- `digital_brain_state`: left/right counts and calibration metadata.

Nodes dedupe by:

```text
scope + node_type + canonical_key
```

Each graph node has `label`, `blob`, `summary`, `importance`, `confidence`,
`aliases_json`, `topics_json`, `chronology_json`, `verified_status`,
`hemisphere`, visual coordinates, `embedding_json`, and `metadata_json`.

## Agent Contract

Agents should treat branch labels and tags as routing hints, not ground truth.
The grounding material is:

- active memory text;
- memory items;
- graph relationships;
- source trust and confidence;
- raw provenance excerpts;
- audit-backed correction and deletion history.

Before planning, Hermes or another orchestrator should ask for:

```bash
agent-memory tree-pack "planning SEO content loop" --scope professional
```

For the full context-builder shape:

```bash
agent-memory build-context "planning SEO content loop" --scope professional
```

For graph maintenance and profile export:

```bash
agent-memory graph groups --scope professional
agent-memory graph optimize --mode record_linkage --scope professional
agent-memory export-profile --scope professional
```

The agent receives the returned markdown alongside the task. After the task,
the orchestrator records a new event or session summary so the next tree can
include what was learned.

## Personal And Professional Memory

The public template starts with two lanes:

- `personal`: preferences, style, stable personal facts.
- `professional`: projects, decisions, rules, attempts, outcomes, gotchas.

Teams can add project, agent, session, success/failure, or loop-specific lanes
as extensions. The tree pack does not require those extensions to be useful.

## SEO / Loop Extension

For iterative work, the most useful branches usually look like:

```text
project / client-site
  attempt
  outcome
  failed_because
  succeeded_because
  lesson
  reusable_rule
```

The kernel should store all relevant events as provenance, but only promote
durable lessons, patterns, gotchas, and decisions into active memory after
policy or review.

## Implementation Notes

The current `MemoryStore.memory_tree_pack()` output is markdown because it can
be passed directly to agents. `MemoryStore.retrieve_tree()` returns the same
structure as a Python dictionary for adapters or future API servers.

Recommended adapter behavior:

- use `tree_pack()` before planning;
- use `context_builder_pack()` for non-trivial scoped tasks;
- use `remember()` after work;
- use `record_turn()` for raw conversation history;
- keep review and correction in the kernel;
- never let untrusted external content silently become a durable rule.
