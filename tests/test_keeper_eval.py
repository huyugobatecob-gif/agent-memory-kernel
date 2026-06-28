from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from adapters.hermes_provider.hermes_provider import HermesMemoryProvider
from agent_memory_kernel.evals import keeper_eval_spec, run_keeper_eval
from agent_memory_kernel.mcp_server import MCPMemoryServer, list_mcp_tools
from agent_memory_kernel.server import handle_api_request
from agent_memory_kernel.store import MemoryStore


class KeeperEvalTests(unittest.TestCase):
    def test_keeper_eval_passes_default_rule_based_extractor(self) -> None:
        result = run_keeper_eval()

        self.assertEqual(result["version"], "keeper-eval-v0.1")
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["passed"])

    def test_keeper_eval_spec_http_mcp_and_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()
            spec = keeper_eval_spec()
            self.assertEqual(spec["version"], "keeper-eval-v0.1")
            http = handle_api_request(store, "/keeper-eval/run", {})
            self.assertTrue(http["passed"])
            store.close()

            server = MCPMemoryServer(Path(tmp) / "memory.db")
            names = {tool["name"] for tool in list_mcp_tools()}
            self.assertIn("memory_keeper_eval", names)
            called = server.handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "memory_keeper_eval", "arguments": {}},
                }
            )
            self.assertFalse(called["result"]["isError"])
            self.assertTrue(called["result"]["structuredContent"]["passed"])

            provider = HermesMemoryProvider(Path(tmp) / "provider.db")
            self.assertTrue(provider.keeper_eval()["passed"])
            provider.close()


if __name__ == "__main__":
    unittest.main()
