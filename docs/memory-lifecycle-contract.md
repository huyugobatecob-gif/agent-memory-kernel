# Memory Lifecycle Contract

This contract defines what happens to memory after it is created, corrected,
deleted, distrusted, expired, or exported.

The core invariant:

```text
raw events are append-only;
active memory is correctable;
derived memory must follow source lifecycle changes.
```

## Lifecycle States

### Event

An event is immutable source material. It can be hidden from retrieval, but it
is not silently erased from audit history.

### Candidate

A candidate is a proposed durable memory. It can be:

- `pending`;
- `approved`;
- `rejected`;
- `quarantined`;
- `superseded`.

### Active Memory

Active memory can be retrieved. It must have:

- source event or turn;
- confidence;
- source trust;
- sensitivity;
- scope/lane;
- owner/project when applicable;
- correction and deletion history.

### Derived Memory

Derived memory includes:

- memory items;
- graph nodes;
- graph edges;
- semantic analyses;
- summaries;
- embeddings;
- style/brain aggregates;
- cached context packs;
- outcome patterns and gotchas.

Derived memory must preserve links to the sources that created it.

## Create

Create path:

```text
event -> candidate -> review/policy -> active memory -> memory item
      -> graph commands -> evidence -> retrieval
```

Rules:

- user-stated direct facts can be trusted only under user identity;
- assistant output is not a trusted fact by default;
- external documents and tool results are untrusted unless source policy says
  otherwise;
- secrets are quarantined;
- active rules require review unless explicitly trusted.

## Correct

Correction means the old active memory becomes superseded and the corrected
memory becomes active.

Required propagation:

- update active memory text;
- mark old memory as superseded;
- add correction audit event;
- update linked memory item;
- update graph node summaries and blobs;
- re-score or remove affected graph edges;
- invalidate stale embeddings;
- invalidate cached context packs;
- update style/brain aggregates if affected;
- keep old evidence for audit but prevent stale retrieval.

## Delete

Deletion means memory should not be retrieved anymore.

Required propagation:

- mark memory and memory item as deleted;
- remove from FTS/vector retrieval;
- mark graph nodes or edges inactive when they have no remaining active
  evidence;
- invalidate summaries that depend only on deleted memory;
- invalidate embeddings and cached context packs;
- update graph group counts and brain/style counts;
- keep audit record unless the deployment policy supports hard erasure.

## Distrust

Distrust means the memory may remain visible for audit but should not ground
answers.

Use for:

- stale facts;
- suspected poisoning;
- low-quality extractions;
- assistant-generated claims;
- external sources later found unreliable.

Required behavior:

- suppress from default retrieval;
- keep available for audit and conflict review;
- record who distrusted it and why;
- prevent derived rules from using it as a source.

## Expire And Decay

Memory can expire by date or decay by relevance.

Decay should affect:

- retrieval score;
- Router branch expansion depth;
- style/brain influence;
- outcome pattern priority.

Decay must not hide critical active constraints unless explicitly superseded or
deleted.

## Conflict Handling

When two active memories conflict:

1. prefer direct user-stated memory over inferred memory;
2. prefer trusted source over untrusted source;
3. prefer newer memory when trust is equal;
4. prefer project-scoped memory inside that project;
5. mark unresolved conflicts for review.

The prompt envelope should include the chosen memory and may include a concise
conflict note when it matters for the task.

Implementation surface:

- `conflict record` stores an explicit open relationship without suppressing
  either memory.
- `supersede` records a resolved `supersedes` relationship and marks the old
  memory and its memory item as `superseded`.
- Superseded memory is removed from active retrieval and active graph export
  through the same propagation path as delete, distrust, and expire.
- `conflict list` exposes open and resolved relationships for review and audit.

## Export

Export must include:

- active memories;
- review state;
- corrections and deletions;
- source references;
- graph nodes and edges;
- evidence;
- profile notes;
- project profiles;
- usage metadata when requested.

Export must not include secret payloads unless explicitly requested by a trusted
local user and encrypted.

## Verification Fixtures

The lifecycle is not complete until tests cover:

- create -> retrieve;
- correct -> old memory no longer retrieved;
- delete -> derived graph edge removed or disabled;
- distrust -> memory visible in audit but absent from prompt;
- conflict -> newer trusted memory wins;
- supersede -> old memory is absent from prompt and graph, resolved relation remains;
- stale -> low-priority retrieval;
- export/import -> lifecycle state preserved.
