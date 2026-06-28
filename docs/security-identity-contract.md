# Security And Identity Contract

Persistent cross-model memory is a prompt boundary and an access-control
surface. This contract defines the minimum security model before the project can
claim full memory.

## Core Invariant

```text
No actor reads or writes memory without identity, scope, trust, and audit.
```

## Identities

Every read and write should carry:

- `user_id`;
- `workspace_id`;
- `project_id` when applicable;
- `agent_id`;
- `model_id`;
- `tool_id` when memory comes from a tool;
- `source_type`;
- `source_ref`;
- `session_id` or `thread_id`.

Local single-user installs can use default identities, but the schema and API
must keep the fields explicit so hosted or team deployments do not need a new
contract.

## Access Scopes

Default scopes:

- `personal`: user-owned memory.
- `professional`: work memory for the user/workspace.
- `project`: project-specific memory.
- `agent`: operational memory for a specific agent role.
- `session`: short-lived memory.

Rules:

- personal memory is not returned to professional-only requests unless policy
  explicitly allows it;
- project memory is visible only inside that project or a trusted parent scope;
- agent memory is not visible to other agents unless role-sharing is allowed;
- session memory expires or is summarized before becoming durable;
- cross-tenant access is denied by default.

Implemented local runtime behavior:

- `before_model_call` accepts `allowed_scopes` and `denied_scopes`;
- a denied active scope returns a no-memory prompt envelope;
- denied scopes produce `access_decisions` and warnings;
- the main model never receives profile notes, thread messages, graph branches,
  source ids, or memory text for a denied active scope.

## Permissions

Minimum permissions:

- `memory.read`;
- `memory.write_event`;
- `memory.propose`;
- `memory.approve`;
- `memory.correct`;
- `memory.delete`;
- `memory.export`;
- `memory.admin`;

The Router requires `memory.read` for every branch it injects. The Keeper can
write events and propose graph commands, but it should not approve high-impact
rules unless policy grants that permission.

## Threat Model

The system must defend against:

- memory poisoning by user text, assistant output, tools, logs, and external
  documents;
- prompt injection stored as durable memory;
- malicious evidence that asks future models to ignore instructions;
- secret capture and later replay;
- cross-lane leakage;
- cross-user or cross-project leakage;
- compromised cached context packs;
- provider-specific prompt-boundary failures;
- stale memory overriding corrected memory;
- low-confidence inferred preferences becoming trusted facts.

## Write Policy

Trusted writes:

- explicit user profile notes;
- manually approved memories;
- system-generated maintenance metadata.

Review-required writes:

- assistant-generated summaries;
- inferred preferences;
- external document content;
- tool output;
- failed attempt explanations;
- new durable rules;
- node merges and destructive graph commands.

Quarantine writes:

- secrets;
- credentials;
- instructions that appear to target future models;
- content that asks to bypass policy;
- suspicious external text;
- high-impact memory from untrusted sources.

## Read Policy

Before injecting memory into a prompt:

1. authenticate the caller identity;
2. resolve requested scopes;
3. filter by permissions;
4. filter by sensitivity;
5. filter by quarantine/deletion/distrust state;
6. redact secrets;
7. log `why_allowed` or `why_denied`;
8. include only selected content in the prompt envelope.

## Encryption And Key Handling

Local-first deployments can store SQLite plainly by default, but production and
hosted modes should define:

- encrypted database option;
- encrypted export option;
- secret redaction before active memory;
- no provider API keys in profile exports unless explicitly encrypted;
- key rotation plan;
- backup and restore handling.

## Audit

Every memory access should be auditable:

- who read it;
- who wrote it;
- which model or tool used it;
- which prompt envelope included it;
- why it was selected;
- whether it was redacted;
- whether access was denied;
- what source evidence created it.

Audit logs must never depend only on provider logs.

## Red-Team Fixtures

Full memory requires tests for:

- poisoned user message;
- poisoned web/tool document;
- assistant hallucination saved as fact;
- secret in user text;
- cross-lane personal-to-professional leak;
- permission denied project memory;
- stale memory after correction;
- cached context pack invalidation;
- provider-specific prompt boundary failure;
- malicious evidence quoted in a prompt.

## End State

The memory system is safe enough for cross-model use only when a retrieved
memory branch can answer:

```text
who created me,
who can read me,
why I was allowed,
why I was recalled,
what evidence backs me,
how I can be corrected or removed.
```
