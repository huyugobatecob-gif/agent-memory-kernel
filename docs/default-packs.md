# Default Memory Packs

Agent Memory Kernel ships two starter packs: `personal` and `professional`.
They are useful defaults over the generic `scope`, `lane`, `namespace`, and
policy model. They are not the only valid ontology.

The machine-readable version is exposed as `memory_contract()["default_packs"]`.

## Personal

Use `personal` for memory that belongs to the user as a person:

- directly stated preferences;
- stable personal context;
- communication style;
- relationships and recurring personal context.

Do not use `personal` as a shortcut for secrets or unreviewed guesses. Secret
content still follows quarantine/redaction rules. Inferred personal facts remain
reviewable. Personal memory is withheld from professional-only prompts unless
an explicit policy allows cross-lane use and the prompt metadata records that
decision.

Default retrieval: explicit access only.

Vault template: [templates/vault/personal.md](../templates/vault/personal.md).

## Professional

Use `professional` for memory that belongs to work:

- project rules and decisions;
- constraints and collaborators;
- successful patterns and failed attempts;
- operational lessons and gotchas.

Do not use `professional` to smuggle private personal context into work prompts.
Assistant, tool, web, and external-document claims remain candidates until
policy or review approves them. Professional memory is still filtered by scope,
namespace, policy, trust, sensitivity, lifecycle state, and prompt budget.

Default retrieval: default work lane.

Vault template:
[templates/vault/professional.md](../templates/vault/professional.md).

## Extension Packs

Additional packs such as `project`, `agent`, `session`, SEO, research, support,
CRM, QA, or outcome loops can be layered on top of the same kernel primitives.
Extension packs must consume the kernel contract:

- source events remain append-only evidence;
- candidates remain reviewable;
- active memory remains policy-filtered;
- graph and summary surfaces inherit lifecycle restrictions;
- import/export preserves provenance and lifecycle state;
- prompt envelopes contain selected memory only, never the full graph.
