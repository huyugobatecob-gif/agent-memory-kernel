# Memory Vault Template

This folder is a human-readable export target.

The default pack contract is documented in
[docs/default-packs.md](../../docs/default-packs.md) and exposed through
`memory_contract()["default_packs"]`. These Markdown files are review/export
surfaces over the kernel contract, not the source of truth.

Generated exports contain:

- `personal.md`
- `professional.md`
- `project.md`
- `agent.md`
- `session.md`
- `pending-review.md`

The SQLite database remains the source of truth. Markdown is for review,
sharing, backup, and editing workflows.
