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


class MemoryObservabilityTests(unittest.TestCase):
    def test_memory_observability_report_aggregates_router_keeper_and_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.db"
            store = MemoryStore(db)
            store.init_db()
            store.remember(
                "Rule: project obs-site should inspect memory observability before rollout.",
                scope="professional",
                actor="user",
                source_type="manual",
                auto_approve=True,
            )
            before = store.before_model_call(
                "Plan obs-site rollout with memory observability.",
                thread_id="obs-thread",
                scope="professional",
                agent_id="planner",
                model_id="main-model",
            )
            after = store.after_saved_turn(
                thread_id="obs-thread",
                scope="professional",
                user_text="Decision: obs-site rollout tracks Router and Keeper telemetry.",
                assistant_text="I will include telemetry checks.",
                agent_id="planner",
                model_id="main-model",
            )
            store.record_llm_usage(
                provider="openai",
                model="cheap-memory-model",
                scope="professional",
                thread_id="obs-thread",
                prompt_tokens=120,
                completion_tokens=30,
                cost=0.0125,
            )

            report = store.memory_observability_report(
                scope="professional",
                thread_id="obs-thread",
            )

            self.assertEqual(report["version"], "memory-observability-v0.1")
            self.assertEqual(report["slo"]["version"], "memory-observability-slo-v0.1")
            self.assertEqual(report["slo"]["status"], "pass")
            self.assertEqual(report["slo"]["thresholds"]["router_latency_slo_ms"], 750.0)
            self.assertEqual(report["router"]["run_count"], 1)
            self.assertEqual(report["router"]["latest_runs"][0]["router_run_id"], before["router_run_id"])
            self.assertTrue(report["router"]["latest_runs"][0]["selected_branch_ids"])
            self.assertGreater(report["router"]["latest_runs"][0]["token_estimate"], 0)
            self.assertIn("average_duration_ms", report["router"])
            self.assertIn("duration_ms", report["router"]["latest_runs"][0])
            self.assertGreaterEqual(report["router"]["average_duration_ms"], 0)
            self.assertGreaterEqual(report["router"]["latest_runs"][0]["duration_ms"], 0)
            self.assertEqual(report["keeper"]["job_count"], 1)
            self.assertEqual(report["keeper"]["status_counts"]["completed"], 1)
            self.assertEqual(report["keeper"]["latest_jobs"][0]["keeper_job_id"], after["keeper_job_id"])
            self.assertIn("average_duration_ms", report["keeper"])
            self.assertIn("duration_ms", report["keeper"]["latest_jobs"][0])
            self.assertGreaterEqual(report["keeper"]["average_duration_ms"], 0)
            self.assertGreaterEqual(report["keeper"]["latest_jobs"][0]["duration_ms"], 0)
            self.assertEqual(report["usage"]["call_count"], 1)
            self.assertEqual(report["usage"]["total_tokens"], 150)
            self.assertEqual(report["usage"]["by_model"]["openai:cheap-memory-model"]["cost"], 0.0125)
            self.assertEqual(report["usage"]["by_currency"]["USD"]["cost"], 0.0125)

            endpoint = handle_api_request(
                store,
                "/observability",
                {
                    "scope": "professional",
                    "thread_id": "obs-thread",
                    "router_latency_slo_ms": 0,
                    "keeper_latency_slo_ms": 0,
                },
            )
            self.assertEqual(endpoint["usage"]["total_tokens"], 150)
            self.assertEqual(endpoint["slo"]["status"], "warn")
            self.assertGreaterEqual(endpoint["slo"]["alert_count"], 1)
            self.assertGreaterEqual(endpoint["slo"]["router"]["breach_count"], 1)

            names = {tool["name"] for tool in list_mcp_tools()}
            self.assertIn("memory_observability", names)
            observability_tool = next(
                tool for tool in list_mcp_tools() if tool["name"] == "memory_observability"
            )
            self.assertIn(
                "router_latency_slo_ms",
                observability_tool["inputSchema"]["properties"],
            )
            store.close()

    def test_observability_cli_outputs_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "memory.db")
            store = MemoryStore(db)
            store.init_db()
            store.record_llm_usage(
                provider="openai",
                model="keeper-mini",
                scope="professional",
                thread_id="cli-thread",
                prompt_tokens=10,
                completion_tokens=5,
                cost=0.001,
            )
            store.close()

            parser = build_parser()
            args = parser.parse_args(
                [
                    "observability",
                    "--db",
                    db,
                    "--scope",
                    "professional",
                    "--thread-id",
                    "cli-thread",
                    "--router-latency-slo-ms",
                    "100",
                ]
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)

            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["version"], "memory-observability-v0.1")
            self.assertEqual(payload["slo"]["thresholds"]["router_latency_slo_ms"], 100.0)
            self.assertEqual(payload["usage"]["total_tokens"], 15)

    def test_billing_reconciliation_report_flags_cost_anomalies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.db"
            store = MemoryStore(db)
            store.init_db()
            store.record_llm_usage(
                provider="openai",
                model="keeper-mini",
                scope="professional",
                thread_id="billing-thread",
                prompt_tokens=100,
                completion_tokens=100,
                cost=0.02,
            )
            store.record_llm_usage(
                provider="openai",
                model="expensive-memory",
                scope="professional",
                thread_id="billing-thread",
                prompt_tokens=1,
                completion_tokens=0,
                cost=0.10,
            )
            store.record_llm_usage(
                provider="local",
                model="free-router",
                scope="professional",
                thread_id="billing-thread",
                prompt_tokens=20,
                completion_tokens=10,
                cost=0.0,
            )

            report = store.billing_reconciliation_report(
                scope="professional",
                thread_id="billing-thread",
                expected_cost=0.10,
                expected_currency="USD",
                tolerance=0.001,
                max_cost_per_1k=50.0,
            )

            self.assertEqual(report["version"], "billing-reconciliation-v0.1")
            self.assertEqual(report["status"], "warn")
            self.assertEqual(report["summary"]["call_count"], 3)
            self.assertEqual(report["totals"]["cost_by_currency"]["USD"], 0.12)
            self.assertEqual(report["by_provider"]["openai"]["calls"], 2)
            self.assertEqual(
                report["by_model"]["openai:expensive-memory"]["cost_per_1k_tokens_by_currency"]["USD"],
                100.0,
            )
            self.assertEqual(report["reconciliation"]["status"], "warn")
            names = {item["name"] for item in report["anomalies"]}
            self.assertIn("expected_cost_mismatch", names)
            self.assertIn("high_cost_per_1k", names)
            self.assertIn("tokens_without_cost", names)

            imported = store.import_billing_invoice(
                invoice_id="inv-openai-001",
                provider="openai",
                currency="USD",
                line_items=[
                    {
                        "model": "keeper-mini",
                        "scope": "professional",
                        "thread_id": "billing-thread",
                        "total_tokens": 200,
                        "amount": 0.02,
                    },
                    {
                        "model": "expensive-memory",
                        "scope": "professional",
                        "thread_id": "billing-thread",
                        "total_tokens": 1,
                        "amount": 0.10,
                    },
                ],
                actor="tester",
            )
            self.assertEqual(imported["version"], "billing-invoice-v0.1")
            self.assertEqual(imported["totals_by_currency"]["USD"], 0.12)

            invoice_report = store.billing_reconciliation_report(
                scope="professional",
                thread_id="billing-thread",
                provider="openai",
                currency="USD",
                tolerance=0,
            )
            self.assertEqual(invoice_report["reconciliation"]["status"], "pass")
            self.assertEqual(invoice_report["reconciliation"]["source"], "provider_invoice")
            self.assertEqual(invoice_report["provider_invoice"]["line_count"], 2)

            endpoint = handle_api_request(
                store,
                "/billing/reconcile",
                {
                    "scope": "professional",
                    "thread_id": "billing-thread",
                    "expected_cost": 0.12,
                    "tolerance": 0,
                    "max_cost_per_1k": 50.0,
                },
            )
            self.assertEqual(endpoint["reconciliation"]["status"], "pass")
            imported_endpoint = handle_api_request(
                store,
                "/billing/invoice/import",
                {
                    "invoice_id": "inv-local-001",
                    "provider": "local",
                    "currency": "USD",
                    "line_items": [
                        {
                            "model": "free-router",
                            "scope": "professional",
                            "thread_id": "billing-thread",
                            "total_tokens": 30,
                            "amount": 0,
                        }
                    ],
                    "actor": "api",
                },
            )
            self.assertEqual(imported_endpoint["status"], "imported")
            listed_endpoint = handle_api_request(
                store,
                "/billing/invoice/list",
                {"provider": "local", "thread_id": "billing-thread"},
            )
            self.assertEqual(listed_endpoint["count"], 1)
            mcp_names = {tool["name"] for tool in list_mcp_tools()}
            self.assertIn("memory_billing_reconcile", mcp_names)
            self.assertIn("memory_billing_invoice_import", mcp_names)
            self.assertIn("memory_billing_invoice_list", mcp_names)
            store.close()

    def test_billing_reconciliation_cli_outputs_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "memory.db")
            store = MemoryStore(db)
            store.init_db()
            store.record_llm_usage(
                provider="openai",
                model="keeper-mini",
                scope="professional",
                thread_id="billing-cli-thread",
                prompt_tokens=10,
                completion_tokens=5,
                cost=0.001,
            )
            store.close()
            invoice_file = Path(tmp) / "invoice.json"
            invoice_file.write_text(
                json.dumps(
                    {
                        "invoice_id": "inv-cli-001",
                        "provider": "openai",
                        "currency": "USD",
                        "line_items": [
                            {
                                "model": "keeper-mini",
                                "scope": "professional",
                                "thread_id": "billing-cli-thread",
                                "total_tokens": 15,
                                "amount": 0.001,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            parser = build_parser()
            args = parser.parse_args(
                [
                    "billing-invoice",
                    "--db",
                    db,
                    "import",
                    "--file",
                    str(invoice_file),
                ]
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)

            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue())["status"], "imported")

            args = parser.parse_args(
                [
                    "billing-invoice",
                    "--db",
                    db,
                    "list",
                    "--provider",
                    "openai",
                ]
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)

            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue())["count"], 1)

            args = parser.parse_args(
                [
                    "billing-reconcile",
                    "--db",
                    db,
                    "--scope",
                    "professional",
                    "--thread-id",
                    "billing-cli-thread",
                    "--provider",
                    "openai",
                    "--currency",
                    "USD",
                    "--tolerance",
                    "0",
                ]
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)

            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["version"], "billing-reconciliation-v0.1")
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["summary"]["call_count"], 1)


if __name__ == "__main__":
    unittest.main()
