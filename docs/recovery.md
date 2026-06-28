# Backup, Restore, And Migration Status

Agent Memory Kernel is local-first, so operational recovery starts with the
SQLite database file. The baseline recovery contract is:

- every runtime entrypoint calls `init_db()`, which applies additive schema
  setup and sets the current SQLite `user_version`;
- `migration-status` checks required tables, required columns, SQLite
  `quick_check`, and schema compatibility;
- `backup` creates a SQLite backup through the SQLite backup API;
- `restore` copies a backup into a target database path, runs additive schema
  setup, records a restore audit event, and returns migration status.

Commands:

```bash
agent-memory migration-status --db .memory/demo.db
agent-memory backup --db .memory/demo.db --out .memory/backups/demo-backup.db
agent-memory restore --backup .memory/backups/demo-backup.db --target-db .memory/restored.db
```

The same surfaces are available through:

- HTTP: `POST /migration/status`, `POST /backup`, `POST /restore`
- MCP: `memory_migration_status`, `memory_backup_database`,
  `memory_restore_database`
- Python/Hermes wrapper: `migration_status()`, `backup_database()`,
  `restore_database()`

Safety defaults:

- backup refuses to overwrite an existing backup unless `--overwrite` is set;
- backup refuses to write over the active source database;
- restore refuses to overwrite an existing target unless `--overwrite` is set;
- restore refuses to use the same path as both backup source and target;
- restore validates the backup with SQLite `quick_check` before copying.

This is a local recovery baseline, not a hosted backup product. Production
deployments should add encrypted off-host backups, hosted retention policies, restore
drills, migration changelogs, and alerting around failed backups or failed
schema compatibility checks.
