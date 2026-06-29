# Backup, Restore, And Migration Status

Agent Memory Kernel is local-first, so operational recovery starts with the
SQLite database file. The baseline recovery contract is:

- every runtime entrypoint calls `init_db()`, which applies additive schema
  setup and sets the current SQLite `user_version`;
- `migration-status` checks required tables, required columns, SQLite
  `quick_check`, and schema compatibility;
- `migration-changelog` reports the current schema migration state, pending
  migrations, recommended rollout gates, and recent local recovery audit
  events;
- `backup` creates a SQLite backup through the SQLite backup API;
- `restore` copies a backup into a target database path, runs additive schema
  setup, records a restore audit event, and returns migration status.
- `restore-drill` creates a backup, restores it into a drill database, checks
  migration status, and optionally verifies a probe query against restored
  active memory.
- `restore-drill-schedule` stores local due times for recurring drills and
  `run-due` executes active schedules, records last result, advances
  `next_due_at`, and opens an operator notification on failure.

Commands:

```bash
agent-memory migration-status --db .memory/demo.db
agent-memory migration-changelog --db .memory/demo.db
agent-memory backup --db .memory/demo.db --out .memory/backups/demo-backup.db
agent-memory restore --backup .memory/backups/demo-backup.db --target-db .memory/restored.db
agent-memory restore-drill --db .memory/demo.db --scope professional --probe-query "demo project"
agent-memory restore-drill-schedule --db .memory/demo.db set --name nightly --interval-hours 24 --scope professional --probe-query "demo project"
agent-memory restore-drill-schedule --db .memory/demo.db run-due --limit 5
```

The same surfaces are available through:

- HTTP: `POST /migration/status`, `POST /migration/changelog`,
  `POST /backup`, `POST /restore`, `POST /restore/drill`,
  `POST /restore/drill/schedule/set`, `POST /restore/drill/schedules`,
  `POST /restore/drill/schedule/run-due`
- MCP: `memory_migration_status`, `memory_migration_changelog`,
  `memory_backup_database`, `memory_restore_database`, `memory_restore_drill`,
  `memory_restore_drill_schedule_set`, `memory_restore_drill_schedules`,
  `memory_restore_drill_schedule_run_due`
- Python adapter wrapper: `migration_status()`, `migration_changelog()`,
  `backup_database()`, `restore_database()`, `restore_drill()`,
  `set_restore_drill_schedule()`, `restore_drill_schedules()`,
  `run_due_restore_drill_schedules()`

Safety defaults:

- backup refuses to overwrite an existing backup unless `--overwrite` is set;
- backup refuses to write over the active source database;
- restore refuses to overwrite an existing target unless `--overwrite` is set;
- restore refuses to use the same path as both backup source and target;
- restore validates the backup with SQLite `quick_check` before copying;
- restore-drill uses temporary artifacts by default, or keeps provided
  `--backup-path` / `--target-db` artifacts for operator review.
- restore-drill schedules only run when a supervisor, cron, agent, CLI, HTTP,
  or MCP client calls `run-due`; the kernel does not run a hidden background
  scheduler.

This is a local recovery baseline, not a hosted backup product. Production
deployments should add encrypted off-host backups, hosted retention policies, restore
artifact custody, hosted migration release-note publication, and alerting
transports around failed backups, failed restore drills, or failed schema
compatibility checks.
