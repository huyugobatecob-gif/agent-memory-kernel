# Personal / Professional Demo

This demo shows the default public template: two simple memory lanes that work
for people who do not use iterative agent loops.

These two lanes are the default model in
[`docs/kernel-charter.md`](../../docs/kernel-charter.md).

## Run

```bash
PYTHONPATH=../../src python3 -m agent_memory_kernel.cli init --db /tmp/amk-personal-professional.db
```

Add a personal preference:

```bash
PYTHONPATH=../../src python3 -m agent_memory_kernel.cli remember \
  --db /tmp/amk-personal-professional.db \
  "I prefer concise technical updates with clear next steps." \
  --scope personal \
  --approve
```

Add a professional rule:

```bash
PYTHONPATH=../../src python3 -m agent_memory_kernel.cli remember \
  --db /tmp/amk-personal-professional.db \
  "Rule: professional project memories must include provenance and correction paths." \
  --scope professional \
  --approve
```

Ask for agent context:

```bash
PYTHONPATH=../../src python3 -m agent_memory_kernel.cli context-pack \
  --db /tmp/amk-personal-professional.db \
  "technical updates and project memory"
```

Export the vault:

```bash
PYTHONPATH=../../src python3 -m agent_memory_kernel.cli export \
  --db /tmp/amk-personal-professional.db \
  --out /tmp/amk-vault
```
