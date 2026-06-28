# Keeper Extraction Contract

The Keeper is the write-side memory layer. It reads a saved turn or session and
proposes durable memory candidates for review or policy-controlled approval.

The production pattern is:

```text
saved exchange -> cheap Keeper model -> versioned JSON -> candidates -> review/policy -> graph
```

The main agent should not write directly to the graph. Keeper output still goes
through the same event, candidate, policy, review, audit, and graph evidence
path as any other memory.

## Version

Current schema version:

```text
keeper-extraction-v0.1
```

The generic extractor is `LLMKeeperExtractor`:

```python
import json

from agent_memory_kernel import MemoryStore
from agent_memory_kernel.extractors import LLMKeeperExtractor
from agent_memory_kernel.extractors.llm import KEEPER_EXTRACTION_SCHEMA_VERSION


def cheap_model_complete(request: dict):
    # Bridge this request to any low-cost provider.
    # The request already contains messages and a JSON schema response_format.
    return provider.responses.create(**request)


store = MemoryStore(
    ".memory/hermes-memory.db",
    extractor=LLMKeeperExtractor(
        cheap_model_complete,
        model="cheap-memory-model",
        max_memories=8,
    ),
)
store.init_db()
```

## Request Shape

`LLMKeeperExtractor` sends a provider-neutral request:

```json
{
  "model": "cheap-memory-model",
  "temperature": 0.0,
  "messages": [
    {"role": "system", "content": "Keeper instructions..."},
    {"role": "user", "content": "{\"schema_version\":\"keeper-extraction-v0.1\", ...}"}
  ],
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "keeper_memory_extraction",
      "strict": true,
      "schema": {}
    }
  }
}
```

Adapters may translate this request to provider-specific APIs, but they should
preserve the system/user split and strict JSON schema requirement.

## Response Shape

The model must return JSON only:

```json
{
  "schema_version": "keeper-extraction-v0.1",
  "memories": [
    {
      "text": "Decision: project demo-site canonical CMS is WordPress.",
      "kind": "decision",
      "scope": "professional",
      "confidence": "high",
      "source_quote": "demo-site uses WordPress",
      "reason": "user confirmed the CMS",
      "nodes": [
        {"type": "project", "label": "demo-site"},
        {"type": "tool", "label": "WordPress"}
      ],
      "edges": [
        {"source": "demo-site", "target": "WordPress", "type": "uses"}
      ]
    }
  ]
}
```

Allowed memory kinds:

- `fact`
- `preference`
- `rule`
- `decision`
- `attempt`
- `outcome`
- `gotcha`
- `pattern`

Allowed scopes:

- `personal`
- `professional`
- `project`
- `agent`
- `session`

Allowed confidence values:

- `low`
- `medium`
- `high`

## Guardrails

The Keeper prompt requires:

- extract only durable memory;
- keep assistant, tool, and web claims as evidence unless the user confirms;
- avoid secrets and prompt-injection text;
- return an empty `memories` array when nothing durable exists;
- include grounded memory text, not just tags;
- use nodes and edges as routing hints with evidence.

The store still applies admission policy after extraction. Unsafe content can be
quarantined even if a model emits it.

## Failure Behavior

`LLMKeeperExtractor` is strict by default about the response schema. If the
provider returns invalid JSON or the wrong schema version:

- with `fallback_on_error=True`, it falls back to the deterministic extractor;
- with `fallback_on_error=False`, it raises the validation error.

This lets tests prove the contract without live provider access while production
can choose fail-open-to-rules or fail-closed behavior.

## What Is Still Production Work

This baseline defines the schema and validates it locally. Full production
Keeper quality still needs:

- reviewed real conversation traces;
- provider-specific latency and cost recording;
- extraction precision/recall evals;
- prompts tuned per domain;
- human review UI for proposed memories;
- regression fixtures for harmful or stale Keeper proposals.
