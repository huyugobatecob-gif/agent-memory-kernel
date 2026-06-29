from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel.mcp_server import MCPMemoryServer, list_mcp_tools, run_mcp_stdio
from agent_memory_kernel.store import MemoryStore


class MCPServerTests(unittest.TestCase):
    def test_mcp_initialization_lists_tools_and_calls_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "memory.db")
            store = MemoryStore(db)
            store.init_db()
            store.remember(
                "Hermes SEO agents should retrieve the Memory Tree Supplement before answering.",
                scope="professional",
                actor="user",
                source_type="manual",
                auto_approve=True,
            )
            store.close()

            server = MCPMemoryServer(db)
            initialized = server.handle_message(
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
            )
            self.assertEqual(initialized["result"]["serverInfo"]["name"], "agent-memory-kernel")
            self.assertIn("tools", initialized["result"]["capabilities"])

            listed = server.handle_message(
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
            )
            names = {tool["name"] for tool in listed["result"]["tools"]}
            self.assertIn("memory_before_model_call", names)
            self.assertIn("memory_prompt_budget", names)
            self.assertIn("memory_before_turn", names)
            self.assertIn("memory_after_turn", names)
            self.assertIn("memory_retrieve_context", names)
            self.assertIn("memory_ingest_graph", names)
            self.assertIn("memory_after_saved_turn", names)
            self.assertIn("memory_graph_nodes", names)
            self.assertIn("memory_graph_browser", names)
            self.assertIn("memory_graph_optimize", names)
            self.assertIn("memory_conflict_detect", names)
            self.assertIn("memory_changes", names)
            self.assertIn("memory_capability_check", names)
            self.assertIn("memory_export_control", names)
            self.assertIn("memory_export_custody", names)
            self.assertIn("memory_export_profile", names)
            self.assertIn("memory_vault_export", names)
            self.assertIn("memory_vault_import", names)
            self.assertIn("memory_export_encrypted_profile", names)
            self.assertIn("memory_import_encrypted_profile", names)
            self.assertIn("memory_export_approval_request", names)
            self.assertIn("memory_export_approval_list", names)
            self.assertIn("memory_export_approval_approve", names)
            self.assertIn("memory_export_approval_reject", names)
            self.assertIn("memory_export_retention_list", names)
            self.assertIn("memory_export_retention_enforce", names)
            self.assertIn("memory_export_retention_purge", names)
            self.assertIn("memory_derived_invalidations", names)
            self.assertIn("memory_observability", names)
            self.assertIn("memory_migration_status", names)
            self.assertIn("memory_conformance_certify", names)
            self.assertIn("memory_backup_database", names)
            self.assertIn("memory_restore_database", names)
            self.assertIn("memory_review_inbox", names)
            self.assertIn("memory_review_batch", names)
            self.assertIn("memory_notifications_list", names)
            self.assertIn("memory_notification_escalations", names)
            self.assertIn("memory_notifications_transport", names)
            self.assertIn("memory_notification_assign", names)
            self.assertIn("memory_notification_ack", names)
            self.assertIn("memory_notification_resolve", names)
            self.assertIn("memory_correct", names)
            self.assertIn("memory_lifecycle_batch", names)
            self.assertIn("memory_delete", names)
            self.assertIn("memory_distrust", names)
            self.assertIn("memory_expire", names)

            called = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "memory_search",
                        "arguments": {"query": "Hermes Memory Tree", "scope": "professional"},
                    },
                }
            )
            result = called["result"]
            self.assertFalse(result["isError"])
            self.assertIn("structuredContent", result)
            self.assertIn("results", result["structuredContent"])
            self.assertIn("Hermes SEO agents", json.dumps(result["structuredContent"]))

            prompt_budget = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 30,
                    "method": "tools/call",
                    "params": {
                        "name": "memory_prompt_budget",
                        "arguments": {"model_id": "llama-3.1-8b", "token_budget": 12000},
                    },
                }
            )
            self.assertFalse(prompt_budget["result"]["isError"])
            self.assertEqual(
                prompt_budget["result"]["structuredContent"]["effective_token_budget"],
                4000,
            )

            conflict_detect = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 31,
                    "method": "tools/call",
                    "params": {
                        "name": "memory_conflict_detect",
                        "arguments": {"scope": "professional", "kind": "decision"},
                    },
                }
            )
            self.assertFalse(conflict_detect["result"]["isError"])
            self.assertEqual(
                conflict_detect["result"]["structuredContent"]["version"],
                "conflict-detection-v0.1",
            )

            capability = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "memory_capability_check",
                        "arguments": {"actor": "designer", "scope": "professional"},
                    },
                }
            )
            self.assertFalse(capability["result"]["isError"])
            self.assertEqual(
                capability["result"]["structuredContent"]["version"],
                "capability-consent-v0.1",
            )

            certification = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 41,
                    "method": "tools/call",
                    "params": {
                        "name": "memory_conformance_certify",
                        "arguments": {
                            "adapter_name": "mcp-test-adapter",
                            "adapter_version": "0.1",
                            "seed_fixture": True,
                        },
                    },
                }
            )
            self.assertFalse(certification["result"]["isError"])
            self.assertEqual(
                certification["result"]["structuredContent"]["version"],
                "agent-memory-adapter-certification-v0.1",
            )
            self.assertEqual(certification["result"]["structuredContent"]["status"], "pass")

            export_control = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "memory_export_control",
                        "arguments": {"actor": "designer", "scope": "professional"},
                    },
                }
            )
            self.assertFalse(export_control["result"]["isError"])
            self.assertEqual(
                export_control["result"]["structuredContent"]["version"],
                "export-control-v0.1",
            )

            export_custody = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 51,
                    "method": "tools/call",
                    "params": {
                        "name": "memory_export_custody",
                        "arguments": {"actor": "designer", "scope": "professional"},
                    },
                }
            )
            self.assertFalse(export_custody["result"]["isError"])
            self.assertEqual(
                export_custody["result"]["structuredContent"]["version"],
                "export-custody-v0.1",
            )

            export_profile = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "tools/call",
                    "params": {
                        "name": "memory_export_profile",
                        "arguments": {
                            "actor": "designer",
                            "scope": "professional",
                            "redaction_profile": "safe",
                        },
                    },
                }
            )
            self.assertFalse(export_profile["result"]["isError"])
            self.assertEqual(
                export_profile["result"]["structuredContent"]["export_metadata"]["redaction"]["profile"],
                "safe",
            )
            self.assertNotIn("Hermes SEO agents", json.dumps(export_profile["result"]["structuredContent"]))

            vault_export = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 61,
                    "method": "tools/call",
                    "params": {
                        "name": "memory_vault_export",
                        "arguments": {
                            "out_dir": str(Path(tmp) / "mcp-vault"),
                            "actor": "designer",
                            "scope": "professional",
                        },
                    },
                }
            )
            self.assertFalse(vault_export["result"]["isError"])
            self.assertEqual(
                vault_export["result"]["structuredContent"]["version"],
                "vault-adapter-v0.1",
            )
            vault_import = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 62,
                    "method": "tools/call",
                    "params": {
                        "name": "memory_vault_import",
                        "arguments": {
                            "in_dir": str(Path(tmp) / "mcp-vault"),
                            "actor": "designer",
                        },
                    },
                }
            )
            self.assertFalse(vault_import["result"]["isError"])
            self.assertEqual(
                vault_import["result"]["structuredContent"]["version"],
                "vault-adapter-v0.1",
            )

            saved_turn = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 7,
                    "method": "tools/call",
                    "params": {
                        "name": "memory_after_saved_turn",
                        "arguments": {
                            "thread_id": "seo-demo",
                            "scope": "professional",
                            "user_message": "Decision: use memory before SEO planning.",
                            "assistant_message": "I will call the memory hook first.",
                            "agent_id": "planner",
                        },
                    },
                }
            )
            self.assertFalse(saved_turn["result"]["isError"])
            self.assertIn("keeper_job_id", saved_turn["result"]["structuredContent"])

    def test_mcp_tool_error_is_tool_result_not_protocol_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "memory.db")
            server = MCPMemoryServer(db)
            called = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "missing_tool", "arguments": {}},
                }
            )
            self.assertTrue(called["result"]["isError"])
            self.assertIn("unknown tool", called["result"]["content"][0]["text"])

    def test_mcp_stdio_uses_newline_json_rpc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "memory.db")
            input_stream = io.StringIO(
                json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
                + "\n"
            )
            output_stream = io.StringIO()
            run_mcp_stdio(db, input_stream=input_stream, output_stream=output_stream)

            response = json.loads(output_stream.getvalue())
            self.assertEqual(response["id"], 1)
            self.assertEqual(
                len(response["result"]["tools"]),
                len(list_mcp_tools()),
            )


if __name__ == "__main__":
    unittest.main()
