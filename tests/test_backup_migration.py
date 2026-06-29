from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel.cli import build_parser
from agent_memory_kernel.mcp_server import list_mcp_tools
from agent_memory_kernel.server import handle_api_request
from agent_memory_kernel.store import MemoryStore


class BackupMigrationTests(unittest.TestCase):
    def test_migration_status_and_backup_restore_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.db"
            backup = Path(tmp) / "backup.db"
            restored_db = Path(tmp) / "restored.db"
            drill_backup = Path(tmp) / "drill-backup.db"
            drill_restored = Path(tmp) / "drill-restored.db"
            store = MemoryStore(db)
            store.init_db()
            store.remember(
                "Decision: backup-site recovery must preserve approved memory.",
                scope="professional",
                actor="user",
                source_type="manual",
                auto_approve=True,
            )

            migration = store.migration_status()
            self.assertEqual(migration["status"], "pass")
            self.assertEqual(migration["schema_version"], 1)
            self.assertTrue(migration["compatible"])

            backup_result = store.backup_database(backup, actor="tester")
            self.assertEqual(backup_result["status"], "created")
            self.assertEqual(backup_result["integrity_check"], "ok")
            self.assertTrue(backup.exists())

            with self.assertRaises(FileExistsError):
                store.backup_database(backup, actor="tester")

            restore_result = MemoryStore.restore_database(backup, restored_db, actor="tester")
            self.assertEqual(restore_result["status"], "restored")
            self.assertEqual(restore_result["integrity_check"], "ok")
            self.assertEqual(restore_result["migration"]["status"], "pass")

            restored = MemoryStore(restored_db)
            restored.init_db()
            self.assertTrue(restored.search("backup-site", scope="professional"))
            restored.close()

            drill = store.restore_drill(
                backup_path=drill_backup,
                target_path=drill_restored,
                scope="professional",
                probe_query="backup-site",
                actor="tester",
            )
            self.assertEqual(drill["version"], "database-restore-drill-v0.1")
            self.assertEqual(drill["status"], "pass")
            self.assertTrue(drill["artifacts"]["retained"])
            self.assertEqual(drill["probe_result_count"], 1)
            self.assertTrue(drill_backup.exists())
            self.assertTrue(drill_restored.exists())
            store.close()

    def test_backup_restore_api_mcp_and_cli_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.db"
            backup = Path(tmp) / "api-backup.db"
            restored_db = Path(tmp) / "api-restored.db"
            drill_backup = Path(tmp) / "api-drill-backup.db"
            drill_restored = Path(tmp) / "api-drill-restored.db"
            cli_backup = Path(tmp) / "cli-backup.db"
            cli_restored = Path(tmp) / "cli-restored.db"
            cli_drill_backup = Path(tmp) / "cli-drill-backup.db"
            cli_drill_restored = Path(tmp) / "cli-drill-restored.db"
            store = MemoryStore(db)
            store.init_db()
            store.remember(
                "Rule: migration status should be checked before memory rollout.",
                scope="professional",
                actor="user",
                source_type="manual",
                auto_approve=True,
            )

            status = handle_api_request(store, "/migration/status", {})
            self.assertEqual(status["status"], "pass")

            backup_result = handle_api_request(
                store,
                "/backup",
                {"out_path": str(backup), "actor": "api"},
            )
            self.assertEqual(backup_result["status"], "created")

            restore_result = handle_api_request(
                store,
                "/restore",
                {"backup_path": str(backup), "target_path": str(restored_db), "actor": "api"},
            )
            self.assertEqual(restore_result["status"], "restored")
            drill_result = handle_api_request(
                store,
                "/restore/drill",
                {
                    "backup_path": str(drill_backup),
                    "target_path": str(drill_restored),
                    "scope": "professional",
                    "probe_query": "migration status",
                    "actor": "api",
                },
            )
            self.assertEqual(drill_result["status"], "pass")
            self.assertEqual(drill_result["probe_result_count"], 1)

            names = {tool["name"] for tool in list_mcp_tools()}
            self.assertIn("memory_migration_status", names)
            self.assertIn("memory_backup_database", names)
            self.assertIn("memory_restore_database", names)
            self.assertIn("memory_restore_drill", names)

            parser = build_parser()
            args = parser.parse_args(["migration-status", "--db", str(db)])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue())["status"], "pass")

            args = parser.parse_args(["backup", "--db", str(db), "--out", str(cli_backup)])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue())["status"], "created")
            self.assertTrue(cli_backup.exists())

            args = parser.parse_args(
                ["restore", "--backup", str(cli_backup), "--target-db", str(cli_restored)]
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue())["status"], "restored")
            self.assertTrue(cli_restored.exists())

            args = parser.parse_args(
                [
                    "restore-drill",
                    "--db",
                    str(db),
                    "--backup-path",
                    str(cli_drill_backup),
                    "--target-db",
                    str(cli_drill_restored),
                    "--scope",
                    "professional",
                    "--probe-query",
                    "migration status",
                ]
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)
            self.assertEqual(code, 0)
            cli_drill = json.loads(stdout.getvalue())
            self.assertEqual(cli_drill["status"], "pass")
            self.assertTrue(cli_drill_backup.exists())
            self.assertTrue(cli_drill_restored.exists())
            store.close()


if __name__ == "__main__":
    unittest.main()
