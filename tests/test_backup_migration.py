from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent_memory_kernel.cli import build_parser
from agent_memory_kernel.mcp_server import MCPMemoryServer, list_mcp_tools
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

            changelog = store.migration_changelog(limit=10)
            self.assertEqual(changelog["version"], "migration-changelog-v0.1")
            self.assertEqual(changelog["status"], "pass")
            self.assertTrue(changelog["compatible"])
            self.assertIn("restore-drill", {gate["name"] for gate in changelog["recommended_gates"]})
            self.assertFalse(changelog["pending_migrations"])
            self.assertIn(
                "backup_database",
                {event["action"] for event in changelog["recent_recovery_events"]},
            )

            restored_again = MemoryStore(restored_db)
            restored_again.init_db()
            restored_changelog = restored_again.migration_changelog(limit=10)
            self.assertIn(
                "restore_database",
                {event["action"] for event in restored_changelog["recent_recovery_events"]},
            )
            restored_again.close()

            past_due = (
                datetime.now(timezone.utc) - timedelta(seconds=1)
            ).replace(microsecond=0).isoformat()
            schedule = store.set_restore_drill_schedule(
                name="nightly-recovery",
                interval_hours=24,
                scope="professional",
                probe_query="backup-site",
                start_at=past_due,
                artifact_dir=Path(tmp) / "scheduled-artifacts",
                retain_artifacts=True,
                actor="tester",
            )
            self.assertEqual(schedule["version"], "restore-drill-schedule-v0.1")
            self.assertTrue(schedule["due"]["due"])

            schedules = store.list_restore_drill_schedules(due_only=True)
            self.assertEqual(schedules["due_count"], 1)
            scheduled_run = store.run_due_restore_drill_schedules(
                limit=1,
                actor="tester",
            )
            self.assertEqual(scheduled_run["status"], "pass")
            self.assertEqual(scheduled_run["processed"], 1)
            self.assertEqual(scheduled_run["runs"][0]["result"]["probe_result_count"], 1)
            self.assertEqual(
                scheduled_run["runs"][0]["schedule"]["last_status"],
                "pass",
            )
            self.assertTrue(any((Path(tmp) / "scheduled-artifacts").glob("*backup.db")))
            self.assertEqual(store.list_restore_drill_schedules(due_only=True)["count"], 0)

            store.set_restore_drill_schedule(
                name="bad-probe",
                interval_hours=24,
                scope="professional",
                probe_query="definitely-missing-probe",
                start_at=past_due,
                actor="tester",
            )
            failed_schedule = store.run_due_restore_drill_schedules(
                limit=1,
                actor="tester",
            )
            self.assertEqual(failed_schedule["status"], "fail")
            self.assertEqual(
                store.list_notifications(topic="restore_drill")["count"],
                1,
            )
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

            kernel_status = store.kernel_status()
            self.assertEqual(kernel_status["version"], "kernel-status-v0.1")
            self.assertEqual(kernel_status["status"], "pass")
            self.assertTrue(kernel_status["compatible"])
            self.assertEqual(kernel_status["versions"]["schema"], 1)
            self.assertEqual(kernel_status["versions"]["contract"], "memory-contract-v0.2")
            self.assertEqual(kernel_status["versions"]["bundle"], "amk-bundle-v0.1")
            self.assertEqual(
                kernel_status["surfaces"]["mcp"],
                ["memory_kernel_status"],
            )

            kernel_endpoint = handle_api_request(store, "/kernel/status", {})
            self.assertEqual(kernel_endpoint["status"], "pass")
            self.assertEqual(kernel_endpoint["versions"]["schema"], 1)

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

            changelog = handle_api_request(store, "/migration/changelog", {"limit": 5})
            self.assertEqual(changelog["version"], "migration-changelog-v0.1")
            self.assertEqual(changelog["status"], "pass")
            self.assertIn("migration-status", {gate["name"] for gate in changelog["recommended_gates"]})

            past_due = (
                datetime.now(timezone.utc) - timedelta(seconds=1)
            ).replace(microsecond=0).isoformat()
            api_schedule = handle_api_request(
                store,
                "/restore/drill/schedule/set",
                {
                    "name": "api-nightly",
                    "interval_hours": 24,
                    "scope": "professional",
                    "probe_query": "migration status",
                    "start_at": past_due,
                    "actor": "api",
                },
            )
            self.assertEqual(api_schedule["version"], "restore-drill-schedule-v0.1")
            self.assertTrue(api_schedule["due"]["due"])
            api_schedules = handle_api_request(
                store,
                "/restore/drill/schedules",
                {"status": "active", "due_only": True},
            )
            self.assertEqual(api_schedules["count"], 1)
            api_run_due = handle_api_request(
                store,
                "/restore/drill/schedule/run-due",
                {"limit": 1, "actor": "api"},
            )
            self.assertEqual(api_run_due["status"], "pass")
            self.assertEqual(api_run_due["processed"], 1)

            names = {tool["name"] for tool in list_mcp_tools()}
            self.assertIn("memory_kernel_status", names)
            self.assertIn("memory_migration_status", names)
            self.assertIn("memory_migration_changelog", names)
            self.assertIn("memory_backup_database", names)
            self.assertIn("memory_restore_database", names)
            self.assertIn("memory_restore_drill", names)
            self.assertIn("memory_restore_drill_schedule_set", names)
            self.assertIn("memory_restore_drill_schedules", names)
            self.assertIn("memory_restore_drill_schedule_run_due", names)

            kernel_call = MCPMemoryServer(db).handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 7,
                    "method": "tools/call",
                    "params": {"name": "memory_kernel_status", "arguments": {}},
                }
            )
            self.assertFalse(kernel_call["result"]["isError"])
            self.assertEqual(kernel_call["result"]["structuredContent"]["status"], "pass")

            parser = build_parser()
            args = parser.parse_args(["kernel-status", "--db", str(db)])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue())["version"], "kernel-status-v0.1")

            args = parser.parse_args(["migration-status", "--db", str(db)])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue())["status"], "pass")

            args = parser.parse_args(["migration-changelog", "--db", str(db), "--limit", "5"])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue())["version"], "migration-changelog-v0.1")

            args = parser.parse_args(
                [
                    "restore-drill-schedule",
                    "--db",
                    str(db),
                    "set",
                    "--name",
                    "cli-nightly",
                    "--interval-hours",
                    "24",
                    "--scope",
                    "professional",
                    "--probe-query",
                    "migration status",
                    "--start-at",
                    past_due,
                ]
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue())["name"], "cli-nightly")

            args = parser.parse_args(
                ["restore-drill-schedule", "--db", str(db), "list", "--due-only"]
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue())["count"], 1)

            args = parser.parse_args(
                ["restore-drill-schedule", "--db", str(db), "run-due", "--limit", "1"]
            )
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
