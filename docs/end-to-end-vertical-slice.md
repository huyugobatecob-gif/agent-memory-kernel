# End-To-End Vertical Slice

This document defines the first executable full-memory slice. It is the minimum
demo that proves the architecture works as a runtime loop instead of only a set
of storage primitives.

## Goal

Prove this flow:

```text
save turn
-> Keeper extracts memory updates
-> memory is stored with provenance and permissions
-> Router selects allowed memory before the next call
-> prompt envelope shows exactly what is injected
-> model answers without graph access
-> post-turn Keeper updates memory again
```

## Fixture Conversation

Use one deterministic test fixture with these turns:

1. User states a professional project fact.
2. User states a personal preference.
3. User reports a successful loop attempt.
4. User reports a failed loop attempt.
5. User corrects a previous fact.
6. User deletes or distrusts one memory.
7. Tool or external text attempts prompt injection.
8. A different agent asks for professional context.
9. A different model asks for the same context.
10. A request tries to access denied project memory.

## Expected Behaviors

### Save Turn

- raw turn is stored in `conversation_turns`;
- message is linked in `thread_messages`;
- audit log records actor, scope, and source.

### Keeper Extracts

- Keeper creates structured output;
- graph commands validate;
- untrusted or high-impact items go to review;
- direct user-stated facts can become candidates;
- poisoning attempt is quarantined.

### Graph Updates

- project fact becomes a graph node or memory item;
- personal preference remains in personal lane;
- success and failure attempts are linked to first-class outcome records and
  active memory provenance;
- correction supersedes old memory;
- deletion suppresses retrieval and derived nodes.

### Router Retrieves

- professional query gets professional memory only;
- personal preference is excluded unless explicitly allowed;
- successful and failed attempts are both available for loop planning;
- stale/superseded fact is not returned;
- permission-denied project memory is skipped with an access decision.

### Prompt Envelope

Envelope includes:

- system core;
- rules digest;
- allowed profile hints;
- compact memory;
- `MEMORY_TREE_SUPPLEMENT`;
- recent messages;
- current request;
- metadata with selected and skipped branches.

Envelope excludes:

- quarantined content;
- deleted content;
- denied lanes;
- secrets;
- raw full graph.

### Cross-Model Reuse

The same selected memory is rendered through at least two provider adapters.
Providers may format messages differently, but selected memory and redactions
must be equivalent.

## Required Assertions

The slice is complete only if tests prove:

- a remembered fact is retrieved next turn;
- a corrected fact replaces the old fact;
- a deleted fact is absent from prompt envelope;
- a stale/conflict case is marked or suppressed;
- a permission-denied branch is skipped;
- a poisoning attempt is quarantined;
- personal lane does not leak into professional request;
- outcome memory returns one success and one failure branch;
- `outcome_pack` includes both branches with linked memory ids;
- main model payload does not contain the full graph;
- selected memory is provider-neutral.

## Suggested Commands

The first runtime hook slice is available through:

```bash
agent-memory before-model-call "Plan the next demo-site SEO refresh loop." \
  --db /tmp/amk-slice.db \
  --scope professional \
  --thread-id thread-runtime

agent-memory after-saved-turn \
  --db /tmp/amk-slice.db \
  --scope professional \
  --thread-id thread-runtime \
  --user-text "Plan the next demo-site SEO refresh loop." \
  --assistant-text "Reuse the successful refresh loop and track outcome memory."
```

The richer fixture is available through dedicated commands:

```bash
agent-memory slice seed --db /tmp/amk-slice.db
agent-memory slice run --db /tmp/amk-slice.db
agent-memory slice assert --db /tmp/amk-slice.db
agent-memory outcome --db /tmp/amk-slice.db pack --project slice-site
```

`tests/test_memory_store.py` contains
`test_runtime_before_and_after_model_call_vertical_slice` and
`test_executable_vertical_slice_seed_run_assert`. Together they prove the
minimal Router -> prompt envelope -> Keeper candidate loop and the richer
provider-neutral seed/run/assert fixture with correction, deletion,
professional/personal lane isolation, poisoning quarantine, and success/failure
outcome recall.

## Why This Comes First

This slice forces the repository to prove the hardest parts together:

- runtime contract;
- lifecycle propagation;
- cross-model prompt envelope;
- security and identity filtering;
- Router quality;
- Keeper write policy;
- user control.

Without this slice, the project can have many useful components while still not
being a full memory system.
