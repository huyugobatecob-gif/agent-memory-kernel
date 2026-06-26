# Hermes Provider Adapter

This folder is a starter adapter boundary for Hermes.

The current implementation is intentionally thin: Hermes should call the kernel
instead of duplicating memory storage logic.

## Responsibilities

The adapter should:

- build context packs before an agent plans work;
- record session summaries, decisions, attempts, successes, and failures;
- leave durable promotion to policy or review;
- expose pending memory review to the user or operator.

## Non-Responsibilities

The adapter should not:

- silently approve untrusted model output;
- rewrite memory without audit;
- hide source provenance;
- store private project-specific logic in the public kernel.

See `hermes_provider.py` for the minimal provider shape.
