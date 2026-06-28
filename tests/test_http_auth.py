from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel import MemoryStore
from agent_memory_kernel.server import _request_is_authorized, make_handler


class HTTPAuthTests(unittest.TestCase):
    def test_request_authorization_accepts_bearer_or_header_token(self) -> None:
        self.assertTrue(_request_is_authorized({"authorization": "Bearer secret"}, "secret"))
        self.assertTrue(_request_is_authorized({"x-agent-memory-token": "secret"}, "secret"))
        self.assertFalse(_request_is_authorized({"authorization": "Bearer wrong"}, "secret"))
        self.assertTrue(_request_is_authorized({}, ""))

    def test_http_handler_auth_boundary_without_socket_bind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.db"
            store = MemoryStore(db)
            store.init_db()
            store.remember(
                "Decision: auth-site memory is protected.",
                scope="professional",
                auto_approve=True,
            )
            store.close()

            handler_class = make_handler(db, auth_token="secret")
            sent: list[tuple[int, dict]] = []
            handler = handler_class.__new__(handler_class)
            handler.headers = {}
            handler._send_json = lambda status, payload, **_kwargs: sent.append((status, payload))

            self.assertFalse(handler._require_auth())
            self.assertEqual(sent[0][0], 401)
            self.assertEqual(sent[0][1]["error"], "unauthorized")

            handler.headers = {"authorization": "Bearer secret"}
            self.assertTrue(handler._require_auth())


if __name__ == "__main__":
    unittest.main()
