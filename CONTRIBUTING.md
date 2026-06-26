# Contributing

Agent Memory Kernel should stay small, auditable, and useful without a hosted
service.

## Principles

- Keep memory lifecycle explicit: event -> candidate -> active memory.
- Preserve provenance for every active memory.
- Treat memory as a prompt/security boundary.
- Prefer small stable contracts over large ontologies.
- Keep domain-specific behavior in adapters or extensions.
- Make corrections and deletion easy.

## Local Checks

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Pull Requests

Good first contributions:

- better deterministic extractors;
- more adapter examples;
- migration tests;
- markdown import/export;
- documentation examples.

Please avoid adding required network services or required model API keys to the
core package.
