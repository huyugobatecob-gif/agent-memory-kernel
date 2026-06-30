# AMK-Native Memory Revisions And Bounded Recall

This note defines the narrow Memoir-inspired layer AMK accepts without taking
Memoir's storage model or product identity.

## Boundary

SQLite, AMK IDs, source events, review actions, policy decisions, active
memory rows, and evidence links remain the source of truth. Git-shaped words
are UI metaphors only:

- a revision is a SQLite audit record, not a Git commit;
- a draft scope is a proposal view over candidates, not an independent branch
  of truth;
- a merge is a review decision or proposal, never an automatic active-memory
  mutation;
- a taxonomy path is an alias/index, not the memory identity.

## Revision And Change Schema

`memory_revisions` remains the compatibility table for corrections and
rollbacks. The v1 layer enriches it with optional metadata:

- `parent_revision_id`: previous revision/changelog entry when known;
- `branch_id`: draft scope or adapter branch that proposed the change;
- `change_type`: `activate`, `correct`, `rollback`, or `proposal`;
- `evidence_id`: source event or evidence row backing the change;
- `review_id`: review action that approved or rejected the change;
- `policy_scope`: scope/lane the policy decision used;
- `taxonomy_path`: optional human-readable alias at the time of change;
- `conflict_policy`: `append`, `replace`, `confidence_gated`,
  `llm_merge_as_proposal`, or `reject`;
- `status`: `active`, `proposal`, or `rolled_back`.

## Taxonomy Aliases

`memory_taxonomy_aliases` maps canonical AMK IDs to stable path handles. The
path helps callers summarize and fetch memory by exact handles, but it does not
replace `memory_id`, `candidate_id`, `event_id`, or evidence IDs.

Default aliases are generated on activation from scope, kind, extraction
metadata, and memory ID. Adapters may add richer aliases, but collisions never
overwrite identity.

## Draft Scopes

`memory_draft_scopes` and `memory_draft_items` represent branch-like proposal
views. Drafts can group candidate memories and proposed conflict resolutions.
They cannot inject prompt context directly and cannot create active memories
without normal review/policy approval.

## Conflict Policies

The layer records conflict policy vocabulary as review metadata:

- `append`: reviewer may keep both statements;
- `replace`: reviewer may supersede or correct a prior statement;
- `confidence_gated`: reviewer should prefer higher-confidence evidence;
- `llm_merge_as_proposal`: LLM output is only a candidate proposal;
- `reject`: surface the conflict without writing an active memory.

No conflict policy mutates active memory by itself.

## Bounded Recall

Caller-driven recall is a two-step read-only flow:

1. `bounded_recall_summarize` returns scoped buckets and exact taxonomy paths.
2. `bounded_recall_get` fetches chosen paths or memory IDs with provenance.

Every read enforces read policy, returns exact `memory_id` and source event
references, and excludes inactive, rejected, stale, or quarantined content from
prompt-ready output.

## Quarantined Watch Import

Watch/import records local files as source events and reviewable candidates:

- content hash and chunk hash are stored for reproducibility;
- chunk records are written to `memory_import_chunks`;
- source type is `watch_import`;
- auto-approval is disabled by default;
- prompt-injection-like or secret-like text remains quarantined by admission
  policy.

Imported text is evidence until reviewed. It is not active memory.

## Later Audit UI

A future UI may show lineage, rollback, graph, timeline, review state, draft
scope membership, and import provenance. That UI must consume these tables and
the existing lifecycle APIs; it must not introduce a separate write path.

## Required Tests

Any extension using this layer must prove:

- import/watch and bounded recall do not write active memory;
- active changes carry provenance, evidence/source IDs, policy scope, and
  review linkage when applicable;
- recall is scope/capability bounded and cites exact handles;
- prompt-injection-like imported evidence stays quarantined;
- rejected, inactive, or rolled-back memory does not leak into prompt envelopes;
- exports/imports preserve lifecycle and policy metadata;
- MCP/Hermes/UI adapters cannot bypass review.
