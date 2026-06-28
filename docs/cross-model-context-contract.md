# Cross-Model Context Contract

This contract defines how the same memory follows different model providers
without giving those models direct access to the memory graph.

The core invariant:

```text
models receive selected context, never the full memory store.
```

## Provider-Neutral Envelope

The memory kernel returns a provider-neutral object:

```json
{
  "system": "...",
  "messages": [
    {"role": "user", "content": "Context excerpts..."},
    {"role": "user", "content": "<<< MEMORY_TREE_SUPPLEMENT >>>..."},
    {"role": "user", "content": "Current user request"}
  ],
  "metadata": {
    "thread_id": "seo-demo",
    "scope": "professional",
    "selected_branch_ids": [],
    "source_ids": [],
    "token_estimate": 0,
    "redactions": [],
    "warnings": []
  }
}
```

Adapters convert this object into OpenAI, Anthropic, Gemini, local model, or
other provider-specific message formats.

## Required Sections

The envelope should be assembled in this order:

1. system core;
2. safety and access notes;
3. rules digest;
4. user profile and addressing hints;
5. guarded brain/style append, if enabled;
6. compact active memory;
7. older thread excerpts and summaries;
8. `MEMORY_TREE_SUPPLEMENT`;
9. recent messages;
10. current user request.

Safety, permission, and redaction notes must never be dropped for token budget.

## Memory Tree Supplement

The supplement is a user-role context block because it is retrieved context, not
a new system instruction.

Shape:

```text
<<< MEMORY_TREE_SUPPLEMENT >>>
Branch: project / client-site
Why selected: ...
Trust: user-stated, high confidence
Summary: ...
Expanded content: ...
Evidence: turn_..., event_...
<<< END MEMORY_TREE_SUPPLEMENT >>>
```

Rules:

- branch labels are routing hints;
- expanded content is the grounding material;
- source trust must be visible;
- stale or conflicted memory must be marked;
- unauthorized or secret memory must be absent, not merely hidden by text.

## Guarded Brain/Style Append

Graph-level Digital Brain state may add a soft style preference to the system
section when a scope has enough classified graph nodes and a clear left/right
skew.

Rules:

- it is advisory only;
- it must be visible in `prompt_envelope.metadata.brain_style`;
- it must never override higher-priority instructions, user format requests,
  safety, or factual accuracy;
- it must be omitted when memory access is denied;
- adapters may suppress it with runtime policy;
- balanced or insufficient graph state should produce no append.

The local implementation exposes this via:

```bash
agent-memory graph brain-style --scope professional
```

and:

```text
POST /brain/style
```

Runtime prompt calls can suppress this layer:

```bash
agent-memory before-model-call "plan work" --disable-brain-style
```

## Token Budget Adapters

Provider adapters must accept:

- target model id;
- max input tokens;
- response reserve;
- priority order for shrinking;
- multimodal capability flags;
- tool-use capability flags.

Shrink order:

1. raw provenance excerpts;
2. expanded branch content;
3. older thread excerpts;
4. compact memory;
5. recent messages beyond minimum window.

Never shrink:

- system safety;
- permission notes;
- active critical rules;
- current user request.

## Cross-Provider Tests

The same memory fixture must be tested through at least two adapter shapes:

- OpenAI-style `system` plus `messages`;
- Anthropic-style system string plus messages;
- generic local-model prompt string.

Test assertions:

- selected memory is semantically identical across providers;
- unauthorized memory is absent across providers;
- token shrink behavior is deterministic;
- model-specific prompt boundaries do not turn retrieved memory into higher
  priority instructions;
- redaction markers remain visible.

## Redaction Rules

Adapters must redact:

- secrets;
- credentials;
- private memory outside selected lanes;
- memory denied by identity policy;
- quarantined sources;
- tool output marked untrusted and unsafe.

The envelope metadata should include a redaction count and reason, not the
redacted payload.

## Cross-Model Invariant

If a user switches from one model to another, the next model receives a fresh
prompt envelope from the same memory kernel. No provider-specific memory should
be treated as the source of truth.
