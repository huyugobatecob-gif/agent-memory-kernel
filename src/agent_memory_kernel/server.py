"""Small stdlib HTTP API for Agent Memory Kernel."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .slice import assert_vertical_slice, run_vertical_slice, seed_vertical_slice
from .store import MemoryStore


def handle_api_request(store: MemoryStore, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Dispatch one API request against an initialized store."""
    path = _normalize_path(path)
    if path == "/health":
        return {"status": "ok"}
    if path == "/before-model-call":
        return store.before_model_call(**payload)
    if path == "/after-saved-turn":
        return store.after_saved_turn(**payload)
    if path == "/remember":
        text = str(payload.pop("text"))
        return store.remember(text, **payload)
    if path == "/search":
        query = str(payload.pop("query"))
        return {"results": store.search(query, **payload)}
    if path == "/context-pack":
        query = str(payload.pop("query"))
        return {"context": store.context_pack(query, **payload)}
    if path == "/tree-pack":
        query = str(payload.pop("query"))
        return {"tree": store.memory_tree_pack(query, **payload)}
    if path == "/review/list":
        return {"candidates": store.list_candidates(str(payload.get("status", "pending")))}
    if path == "/review/approve":
        candidate_id = str(payload.pop("candidate_id"))
        return {"memory_id": store.approve_candidate(candidate_id, **payload), "status": "active"}
    if path == "/review/reject":
        candidate_id = str(payload.pop("candidate_id"))
        store.reject_candidate(candidate_id, **payload)
        return {"candidate_id": candidate_id, "status": "rejected"}
    if path == "/slice/seed":
        return seed_vertical_slice(store)
    if path == "/slice/run":
        return run_vertical_slice(store)
    if path == "/slice/assert":
        return assert_vertical_slice(store)
    raise KeyError(f"unknown endpoint: {path}")


def run_server(db_path: str | Path, *, host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run the blocking HTTP service."""
    handler = make_handler(db_path)
    server = ThreadingHTTPServer((host, int(port)), handler)
    print(f"agent-memory api listening on http://{host}:{int(port)}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def make_handler(db_path: str | Path) -> type[BaseHTTPRequestHandler]:
    db_path = str(db_path)

    class MemoryAPIHandler(BaseHTTPRequestHandler):
        server_version = "AgentMemoryKernel/0.1"

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler name
            if _normalize_path(self.path) == "/health":
                self._send_json(200, {"status": "ok"})
                return
            self._send_json(404, {"error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler name
            try:
                payload = self._read_json()
                store = MemoryStore(db_path)
                store.init_db()
                try:
                    result = handle_api_request(store, self.path, payload)
                finally:
                    store.close()
                self._send_json(200, result)
            except KeyError as exc:
                self._send_json(404, {"error": "not_found", "detail": str(exc)})
            except Exception as exc:  # pragma: no cover - defensive HTTP boundary
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("content-length", "0") or "0")
            if length <= 0:
                return {}
            data = self.rfile.read(length)
            return json.loads(data.decode("utf-8"))

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("content-type", "application/json; charset=utf-8")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return MemoryAPIHandler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-memory-api")
    parser.add_argument("--db", default=".memory/memory.db")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    run_server(args.db, host=args.host, port=args.port)
    return 0


def _normalize_path(path: str) -> str:
    path = (path or "/").split("?", 1)[0].rstrip("/")
    return path or "/"


if __name__ == "__main__":
    raise SystemExit(main())
