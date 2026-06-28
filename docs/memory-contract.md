# Memory Contract

This contract is the public pass/fail boundary for integrations that want to
call Agent Memory Kernel a full runtime memory layer instead of a searchable
notes store.

The machine-readable version lives in `agent_memory_kernel.contract` and can be
printed with:

```bash
agent-memory contract
agent-memory contract assert
```

HTTP integrations can call:

```text
POST /contract
POST /contract/assert
```

## Closed Loop

Full memory means the system can repeat this loop safely:

```text
observe -> encode_with_provenance -> route_relevant_memory
-> act_with_selected_context -> verify_behavior -> revise_or_forget
```

Storage alone is not enough. A memory branch must be usable, auditable,
correctable, and safe to omit when access or trust is not sufficient.

## Lanes

Default public lanes:

- `personal`: user preferences, communication style, and stable personal
  context. Retrieval should be explicit by default.
- `professional`: work context, projects, decisions, rules, lessons, gotchas,
  and patterns. This is the default work lane.

Extension lanes:

- `project`: project-specific constraints, decisions, outcomes, and facts.
- `agent`: operational memory for a specific agent role or capability.
- `session`: short-lived thread context that may later be summarized.

Lane rules:

- personal memory must not enter professional-only prompts;
- project memory should require a project identity or trusted parent scope;
- agent memory should not be shared across roles unless policy allows it;
- session memory should expire or be summarized before becoming durable;
- cross-lane retrieval must be visible in prompt metadata and audit.

## Typed Memory

Starter memory kinds:

- `fact`
- `preference`
- `rule`
- `decision`
- `attempt`
- `outcome`
- `gotcha`
- `pattern`

Every active memory should carry:

- source event or turn;
- scope/lane;
- kind;
- confidence;
- sensitivity;
- source trust;
- status;
- provenance/source ids;
- lifecycle history for correction, rollback, deletion, distrust, expiry, and
  supersession.

## Read And Write Rules

Write actions covered by policy:

- `record`
- `auto_approve`
- `approve`
- `reject`
- `correct`
- `delete`
- `distrust`
- `expire`
- `outcome`
- `conflict`
- `supersede`

Default stance:

- direct user/manual facts can be trusted when policy allows;
- assistant, tool, web, and external document claims remain candidates by
  default;
- high-impact rules require review unless policy explicitly allows promotion;
- secret-like or prompt-injection-like content is quarantined;
- destructive lifecycle mutations require explicit authority.

## Graph-Derived Style

Digital Brain style is a derived prompt preference, not a durable user rule.

Rules:

- emit it only when memory access is allowed;
- include the decision in prompt metadata;
- keep it advisory and guarded;
- make it suppressible by runtime policy;
- never let it override explicit user instructions, safety, factual accuracy,
  or requested output format.

## Acceptance Gates

The built-in acceptance harness is the minimum deterministic gate:

```bash
agent-memory acceptance seed --db /tmp/amk-acceptance.db
agent-memory acceptance assert --db /tmp/amk-acceptance.db
```

HTTP integrations can call:

```text
POST /acceptance/seed
POST /acceptance/run
POST /acceptance/assert
```

The harness checks:

- the memory contract shape is stable;
- the runtime vertical slice passes;
- selected memory beats a no-memory baseline;
- selected branches and source ids are logged;
- denied memory fails closed;
- personal memory does not leak into professional prompts;
- unsafe memory stays absent from prompt-facing retrieval;
- correction and rollback affect active retrieval;
- Keeper writes stay reviewable;
- write policy blocks unauthorized approval.

The public conformance suite additionally checks that post-turn Keeper changes
are inspectable by Keeper job id and thread: saved turns, event, candidates,
affected surfaces, and audit trail must be visible to adapters.
It also checks that capability reports expose denied read/write actions and
that denied export or lifecycle mutation paths fail closed.

The machine-readable contract also names the completion gates for governed
read-time policy, inspection and operator control, derived-memory invalidation,
capability and consent, and operational failure behavior. These gates are part
of the full-memory bar even when the deterministic local fixture only checks a
smaller starter scenario.

This harness does not replace production evals. It is the first hard gate that
prevents the project from drifting back into "tables plus CLI" without proving
the behavior that makes memory useful.

## Production Completion Bar

The project can claim full memory when the deterministic acceptance harness and
real shadow traces prove that memory:

- automatically runs before and after agent turns;
- retrieves the right branch for real tasks;
- explains the read-time decision policy: relevance, recency, trust, scope,
  sensitivity, conflict status, graph distance, outcome value, and token budget;
- avoids stale, unsafe, and unauthorized branches;
- explains provenance and why memory was selected;
- supports correction, rollback, deletion, distrust, expiry, and supersession;
- invalidates derived summaries, graph surfaces, cached packs, outcome lessons,
  and graph-derived style when underlying memory changes;
- resolves current-best answers or marks unresolved conflicts instead of
  silently surfacing equal-trust contradictions;
- exposes who may read, write, promote, inject, distrust, export, and delete
  memory under multi-agent orchestration;
- supports inspection flows for remembered facts, prompt injections, last-turn
  changes, provenance, undo, distrust, and export;
- records whether prompt-facing memory helped, was ignored, was missing, or
  caused harm, without mutating active memory automatically;
- improves behavior compared with no-memory baseline;
- remains provider-neutral across model adapters;
- defines fallback behavior for slow, unavailable, corrupted, partially
  migrated, or oversized memory stores.
