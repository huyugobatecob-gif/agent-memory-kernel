# Trust And Security

Agent Memory Kernel is a local memory contract, not a hosted security boundary.
It helps local operators keep long-lived memory auditable, reversible, and
policy-filtered before it reaches a model prompt.

## Trust Boundary

The local SQLite database is the source of truth. The operator owns the local
file, backups, passphrases, process permissions, and any off-host custody.

The kernel protects the memory lifecycle inside that boundary:

- source events are evidence, not automatically trusted memory;
- candidate memory is reviewable by default;
- active memory is only prompt-facing after policy or review;
- every prompt-facing selection carries provenance and selection reasons;
- lifecycle changes propagate to retrieval, graph, summary, export, and prompt
  surfaces.

## Unsafe Or Wrong Memory

When memory is wrong, harmful, stale, or no longer allowed, use the lifecycle
surface instead of editing the database by hand:

- `correct`: replace text while keeping revision history.
- `rollback`: restore a prior revision.
- `delete`: soft-delete and suppress prompt-facing retrieval.
- `distrust`: keep audit evidence while suppressing derived influence.
- `expire`: suppress memory after a validity window.
- `supersede`: mark a replacement as the current winner.
- `reject`: keep a candidate out of active memory.
- `quarantine`: keep secret-like or prompt-injection-like content out of active
  memory until explicit review.

These actions are documented in
[memory-lifecycle-contract.md](memory-lifecycle-contract.md).

## Prompt-Injection And Memory Poisoning

The kernel treats assistant guesses, tool output, web claims, imported
documents, and other external text as untrusted by default. Prompt-injection-like
or secret-like text is quarantined. Untrusted claims can be stored as evidence
or candidates without becoming active prompt context.

Relevant evidence:

- `PYTHONPATH=src python3 -m agent_memory_kernel.cli conformance assert`
- scenarios `secret_like_memory_is_quarantined`,
  `tool_prompt_injection_is_quarantined`,
  `untrusted_tool_claim_stays_reviewable`, and
  `assistant_guess_stays_reviewable`
- [threat-model.md](threat-model.md)

## Privacy And Export

The kernel supports redaction profiles, approval checks for sensitive full
exports, retention ledgers, and encrypted export envelopes. These are local
controls. The kernel does not operate a hosted export service or store cloud
keys.

Use:

```bash
PYTHONPATH=src python3 -m agent_memory_kernel.cli export-control --db /tmp/amk.db --scope professional --redaction-profile safe
PYTHONPATH=src python3 -m agent_memory_kernel.cli export-custody --db /tmp/amk.db --scope professional --redaction-profile safe
PYTHONPATH=src python3 -m agent_memory_kernel.cli export-bundle --db /tmp/amk.db --out workspace-memory.amk.json --scope professional --redaction-profile safe
```

## Recovery And Corruption

The kernel exposes migration status, kernel status, backup/restore, restore
drills, and SQLite quick checks. If a store is unavailable, incompatible, or
denied by policy, runtime read paths should fail closed to no-memory mode.

Relevant docs:

- [recovery.md](recovery.md)
- [security-identity-contract.md](security-identity-contract.md)
- [runtime-contract.md](runtime-contract.md)

## Explicit Non-Guarantees

Without a separate hosted/security wrapper, the kernel does not guarantee:

- tenant isolation across remote users;
- hosted auth, SSO, or team RBAC;
- cloud KMS or off-host key custody;
- remote MCP authentication;
- webhook/email/push delivery security;
- live provider invoice correctness;
- physical device security;
- protection from a local actor with unrestricted database write access.

Those are extension or later-hosted responsibilities. They must not be implied
by the v0.1.0 alpha README.
