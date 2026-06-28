"""Minimal stdio MCP server for Agent Memory Kernel.

The implementation intentionally stays dependency-free. It exposes the same
orchestrator surface as the HTTP API through JSON-RPC MCP tool calls, so agents
can use memory without importing Python modules or shelling out to the CLI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .server import handle_api_request
from .store import MemoryStore


PROTOCOL_VERSION = "2025-06-18"
SERVER_NAME = "agent-memory-kernel"
SERVER_VERSION = "0.1.0"


def _schema(properties: dict[str, dict[str, Any]], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": True,
    }


def _string(description: str, default: str | None = None) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "string", "description": description}
    if default is not None:
        schema["default"] = default
    return schema


def _integer(description: str, default: int | None = None) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "integer", "description": description}
    if default is not None:
        schema["default"] = default
    return schema


def _boolean(description: str, default: bool | None = None) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "boolean", "description": description}
    if default is not None:
        schema["default"] = default
    return schema


MCP_TOOLS: dict[str, dict[str, Any]] = {
    "memory_before_model_call": {
        "endpoint": "/before-model-call",
        "description": "Build the prompt envelope before the main model call.",
        "inputSchema": _schema(
            {
                "query": _string("Current user request or task."),
                "thread_id": _string("Conversation thread id.", "default"),
                "scope": _string("Memory scope/lane.", "professional"),
                "user_id": _string("User id.", "user"),
                "agent_id": _string("Calling agent id.", "agent"),
                "model_id": _string("Main model id.", ""),
                "mode": _string("Runtime mode such as default or no-memory.", "default"),
                "token_budget": _integer("Prompt memory token budget.", 1200),
                "limit": _integer("Maximum selected memory branches.", 8),
                "recent_messages": _integer("Recent thread messages to include.", 8),
                "enable_brain_style": _boolean("Include guarded graph-derived style hint.", True),
            },
            ["query"],
        ),
    },
    "memory_before_turn": {
        "endpoint": "/before-turn",
        "description": "Orchestrator hook: retrieve memory and build prompt context before an agent turn.",
        "inputSchema": _schema(
            {
                "query": _string("Current user request or task."),
                "thread_id": _string("Conversation thread id.", "default"),
                "scope": _string("Memory scope/lane.", "professional"),
                "user_id": _string("User id.", "user"),
                "agent_id": _string("Calling agent id.", "agent"),
                "model_id": _string("Main model id.", ""),
                "mode": _string("Runtime mode such as chat or shadow.", "chat"),
                "token_budget": _integer("Prompt memory token budget.", 12000),
                "limit": _integer("Maximum selected memory branches.", 8),
                "recent_messages": _integer("Recent thread messages to include.", 6),
                "enable_brain_style": _boolean("Include guarded graph-derived style hint.", True),
            },
            ["query"],
        ),
    },
    "memory_build_prompt_context": {
        "endpoint": "/build-prompt-context",
        "description": "Orchestrator hook: return the final agent-ready prompt envelope.",
        "inputSchema": _schema(
            {
                "query": _string("Current user request or task."),
                "thread_id": _string("Conversation thread id.", "default"),
                "scope": _string("Memory scope/lane.", "professional"),
                "user_id": _string("User id.", "user"),
                "agent_id": _string("Calling agent id.", "agent"),
                "model_id": _string("Main model id.", ""),
                "token_budget": _integer("Prompt memory token budget.", 12000),
                "limit": _integer("Maximum selected memory branches.", 8),
            },
            ["query"],
        ),
    },
    "memory_retrieve_context": {
        "endpoint": "/retrieve-context",
        "description": "Orchestrator hook: retrieve expanded graph branches and tree supplement.",
        "inputSchema": _schema(
            {
                "query": _string("Task or search query."),
                "scope": _string("Optional memory scope/lane.", ""),
                "limit": _integer("Maximum branches.", 8),
                "depth": _integer("Graph neighbor expansion depth.", 1),
                "include_raw": _boolean("Include raw memory excerpts.", True),
                "raw_chars": _integer("Maximum raw chars per branch.", 700),
                "actor": _string("Calling agent id for inject policy enforcement.", "agent"),
            },
            ["query"],
        ),
    },
    "memory_after_saved_turn": {
        "endpoint": "/after-saved-turn",
        "description": "Save a completed turn and run or queue Keeper extraction.",
        "inputSchema": _schema(
            {
                "thread_id": _string("Conversation thread id.", "default"),
                "user_message": _string("User message text."),
                "assistant_message": _string("Assistant response text."),
                "scope": _string("Memory scope/lane.", "professional"),
                "user_id": _string("User id.", "user"),
                "agent_id": _string("Calling agent id.", "agent"),
                "model_id": _string("Main model id.", ""),
                "keeper_mode": _string("sync or queue.", "sync"),
                "write_policy": _string("propose_only or allow_policy_auto_approve.", "propose_only"),
                "source_ref": _string("External source reference.", ""),
            },
            ["user_message", "assistant_message"],
        ),
    },
    "memory_after_turn": {
        "endpoint": "/after-turn",
        "description": "Orchestrator hook: save the exchange and run or queue Keeper extraction after an agent turn.",
        "inputSchema": _schema(
            {
                "thread_id": _string("Conversation thread id.", "default"),
                "user_text": _string("User message text."),
                "assistant_text": _string("Assistant response text."),
                "scope": _string("Memory scope/lane.", "professional"),
                "user_id": _string("User id.", "user"),
                "agent_id": _string("Calling agent id.", "agent"),
                "model_id": _string("Main model id.", ""),
                "keeper_mode": _string("sync or queue.", "sync"),
                "auto_approve": _boolean("Attempt policy-controlled auto-approval.", False),
            },
            ["user_text", "assistant_text"],
        ),
    },
    "memory_ingest_graph": {
        "endpoint": "/ingest-graph",
        "description": "Orchestrator hook: ingest Keeper-style graph updates as reviewable memory.",
        "inputSchema": _schema(
            {
                "updates": {
                    "type": "array",
                    "description": "Graph update objects with text, label, summary, relation, target, or evidence.",
                    "items": {"type": "object"},
                },
                "scope": _string("Memory scope/lane.", "professional"),
                "actor": _string("Calling agent id.", "agent"),
                "source_ref": _string("Source reference.", ""),
                "auto_approve": _boolean("Attempt policy-controlled auto-approval.", False),
            },
            ["updates"],
        ),
    },
    "memory_changes": {
        "endpoint": "/memory-changes",
        "description": "Inspect what Keeper changed after a saved turn.",
        "inputSchema": _schema(
            {
                "keeper_job_id": _string("Specific Keeper job id.", ""),
                "thread_id": _string("Thread id for recent change list.", ""),
                "scope": _string("Optional memory scope/lane.", ""),
                "limit": _integer("Maximum recent changes.", 20),
            }
        ),
    },
    "memory_derived_invalidations": {
        "endpoint": "/derived-invalidations",
        "description": "Inspect derived-memory invalidation records after correction or lifecycle changes.",
        "inputSchema": _schema(
            {
                "memory_id": _string("Optional memory id to inspect.", ""),
                "scope": _string("Optional memory scope/lane.", ""),
                "action": _string("Optional lifecycle action filter.", ""),
                "limit": _integer("Maximum invalidation records.", 50),
            }
        ),
    },
    "memory_operational_status": {
        "endpoint": "/operational/status",
        "description": "Report local runtime memory health and configured failure fallback behavior.",
        "inputSchema": _schema(
            {
                "max_db_bytes": _integer("Warn when the SQLite file exceeds this size.", 536870912),
                "integrity_check": _boolean("Run SQLite quick_check.", True),
            }
        ),
    },
    "memory_search": {
        "endpoint": "/search",
        "description": "Search active memory with provenance-aware results.",
        "inputSchema": _schema(
            {
                "query": _string("Search query."),
                "scope": _string("Optional memory scope/lane.", ""),
                "limit": _integer("Maximum results.", 10),
                "actor": _string("Calling agent id for read policy enforcement.", "agent"),
            },
            ["query"],
        ),
    },
    "memory_context_pack": {
        "endpoint": "/context-pack",
        "description": "Return compact context pack text for a query.",
        "inputSchema": _schema(
            {
                "query": _string("Task or search query."),
                "scope": _string("Optional memory scope/lane.", ""),
                "limit": _integer("Maximum memory entries.", 8),
                "actor": _string("Calling agent id for read policy enforcement.", "agent"),
            },
            ["query"],
        ),
    },
    "memory_tree_pack": {
        "endpoint": "/tree-pack",
        "description": "Return expanded Memory Tree Supplement for prompt injection.",
        "inputSchema": _schema(
            {
                "query": _string("Task or search query."),
                "scope": _string("Optional memory scope/lane.", ""),
                "limit": _integer("Maximum branches.", 8),
                "depth": _integer("Graph neighbor expansion depth.", 1),
                "include_raw": _boolean("Include raw memory excerpts.", True),
                "raw_chars": _integer("Maximum raw chars per branch.", 700),
                "actor": _string("Calling agent id for inject policy enforcement.", "agent"),
            },
            ["query"],
        ),
    },
    "memory_remember": {
        "endpoint": "/remember",
        "description": "Record a memory candidate or trusted memory item.",
        "inputSchema": _schema(
            {
                "text": _string("Memory text to record."),
                "scope": _string("Memory scope/lane.", "professional"),
                "actor": _string("Actor writing the memory.", "mcp"),
                "source_type": _string("Source type.", "mcp"),
                "source_ref": _string("Source reference.", ""),
                "sensitivity": _string("Sensitivity level.", "internal"),
                "auto_approve": _boolean("Attempt policy-controlled auto-approval.", False),
            },
            ["text"],
        ),
    },
    "memory_review_list": {
        "endpoint": "/review/list",
        "description": "List review candidates for human or operator approval.",
        "inputSchema": _schema(
            {
                "status": _string("Candidate status.", "pending"),
            }
        ),
    },
    "memory_review_approve": {
        "endpoint": "/review/approve",
        "description": "Approve a pending memory candidate.",
        "inputSchema": _schema(
            {
                "candidate_id": _string("Candidate id to approve."),
                "actor": _string("Approving actor.", "mcp"),
                "reason": _string("Approval reason.", ""),
            },
            ["candidate_id"],
        ),
    },
    "memory_review_reject": {
        "endpoint": "/review/reject",
        "description": "Reject a pending memory candidate.",
        "inputSchema": _schema(
            {
                "candidate_id": _string("Candidate id to reject."),
                "actor": _string("Rejecting actor.", "mcp"),
                "reason": _string("Rejection reason.", ""),
            },
            ["candidate_id"],
        ),
    },
    "memory_capability_check": {
        "endpoint": "/capability/check",
        "description": "Report effective read/write memory capabilities for an agent.",
        "inputSchema": _schema(
            {
                "actor": _string("Calling agent id.", "agent"),
                "scope": _string("Memory scope/lane.", "professional"),
                "project": _string("Optional project id.", ""),
                "read_actions": {
                    "type": "array",
                    "description": "Optional read actions to check.",
                    "items": {"type": "string"},
                },
                "write_actions": {
                    "type": "array",
                    "description": "Optional write actions to check.",
                    "items": {"type": "string"},
                },
            }
        ),
    },
    "memory_graph_nodes": {
        "endpoint": "/graph/nodes",
        "description": "List active memory graph nodes.",
        "inputSchema": _schema(
            {
                "scope": _string("Optional memory scope/lane.", ""),
                "node_type": _string("Optional graph node type.", ""),
                "limit": _integer("Maximum nodes.", 50),
            }
        ),
    },
    "memory_graph_edges": {
        "endpoint": "/graph/edges",
        "description": "List active memory graph edges.",
        "inputSchema": _schema(
            {
                "scope": _string("Optional memory scope/lane.", ""),
                "limit": _integer("Maximum edges.", 50),
            }
        ),
    },
    "memory_current_best": {
        "endpoint": "/current-best",
        "description": "Explain current-best retrieval and conflict suppression for a query.",
        "inputSchema": _schema(
            {
                "query": _string("Question or topic."),
                "scope": _string("Optional memory scope/lane.", ""),
                "limit": _integer("Maximum candidates.", 8),
            },
            ["query"],
        ),
    },
    "memory_router_explain": {
        "endpoint": "/router-explain",
        "description": "Explain a recorded Router run.",
        "inputSchema": _schema(
            {
                "router_run_id": _string("Router run id."),
            },
            ["router_run_id"],
        ),
    },
    "memory_worker_run": {
        "endpoint": "/worker/run",
        "description": "Process queued Keeper jobs once.",
        "inputSchema": _schema(
            {
                "limit": _integer("Maximum jobs to process.", 10),
                "actor": _string("Worker actor id.", "mcp-worker"),
            }
        ),
    },
}


class MCPMemoryServer:
    """Small JSON-RPC dispatcher for MCP stdio transports."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)

    def handle_message(self, message: dict[str, Any]) -> dict[str, Any] | None:
        if "id" not in message:
            return None
        request_id = message.get("id")
        method = str(message.get("method", ""))
        params = message.get("params") or {}
        try:
            result = self._dispatch(method, params if isinstance(params, dict) else {})
        except Exception as exc:  # pragma: no cover - defensive protocol boundary
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": str(exc)},
            }
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _dispatch(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if method == "initialize":
            return {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            }
        if method == "ping":
            return {}
        if method == "tools/list":
            return {"tools": list_mcp_tools()}
        if method == "tools/call":
            return self._call_tool(params)
        raise ValueError(f"unsupported MCP method: {method}")

    def _call_tool(self, params: dict[str, Any]) -> dict[str, Any]:
        tool_name = str(params.get("name", ""))
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            return _tool_error("tool arguments must be an object")
        tool = MCP_TOOLS.get(tool_name)
        if not tool:
            return _tool_error(f"unknown tool: {tool_name}")

        store = MemoryStore(self.db_path)
        store.init_db()
        try:
            result = handle_api_request(store, str(tool["endpoint"]), dict(arguments))
        finally:
            store.close()
        return _tool_result(result)


def list_mcp_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "description": str(tool["description"]),
            "inputSchema": tool["inputSchema"],
        }
        for name, tool in MCP_TOOLS.items()
    ]


def run_mcp_stdio(db_path: str | Path, *, input_stream: Any = None, output_stream: Any = None) -> None:
    """Run the newline-delimited JSON-RPC stdio MCP server."""
    input_stream = input_stream or sys.stdin
    output_stream = output_stream or sys.stdout
    server = MCPMemoryServer(db_path)
    for line in input_stream:
        line = line.strip()
        if not line:
            continue
        response = server.handle_message(json.loads(line))
        if response is None:
            continue
        output_stream.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
        output_stream.flush()


def _tool_result(payload: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return {
        "content": [{"type": "text", "text": text}],
        "structuredContent": payload,
        "isError": False,
    }


def _tool_error(message: str) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": message}],
        "isError": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-memory-mcp")
    parser.add_argument("--db", default=".memory/memory.db")
    args = parser.parse_args(argv)
    run_mcp_stdio(args.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
