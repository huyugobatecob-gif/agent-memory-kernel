"""Normalize Keeper graph commands before they reach the store."""

from __future__ import annotations

from typing import Any

from .policy import normalize_confidence, normalize_scope


GRAPH_COMMAND_VERSION = "graph-command-v0.1"
GRAPH_COMMAND_TYPES = {
    "upsert_node",
    "merge_node",
    "rename_node",
    "update_summary",
    "upsert_edge",
    "attach_evidence",
    "mark_conflict",
}
GRAPH_NODE_TYPES = {
    "agent",
    "attempt",
    "data",
    "decision",
    "document",
    "event",
    "fact",
    "gotcha",
    "interest",
    "memory",
    "outcome",
    "pattern",
    "person",
    "preference",
    "project",
    "rule",
    "tool",
}


def normalize_graph_commands(
    updates: list[dict[str, Any]],
    *,
    default_scope: str = "professional",
    default_confidence: str = "medium",
) -> list[dict[str, Any]]:
    """Return safe, bounded, versioned graph command dictionaries."""
    if not isinstance(updates, list):
        raise TypeError("graph command updates must be a list")
    scope = normalize_scope(default_scope)
    confidence = normalize_confidence(default_confidence)
    commands = []
    for index, update in enumerate(updates[:100]):
        if not isinstance(update, dict):
            raise TypeError("each graph command update must be an object")
        command = _normalize_one(update, scope=scope, confidence=confidence)
        command["version"] = GRAPH_COMMAND_VERSION
        command["index"] = index
        commands.append(command)
    if not commands:
        raise ValueError("at least one graph command is required")
    return commands


def graph_commands_to_extraction(commands: list[dict[str, Any]]) -> dict[str, Any]:
    """Build extraction_json content for candidate_memories."""
    nodes: list[dict[str, str]] = []
    edges: list[dict[str, str]] = []
    for command in commands:
        command_type = command["command_type"]
        if command_type in {"upsert_node", "merge_node", "rename_node", "update_summary", "attach_evidence"}:
            node = {**command.get("node", {})}
            if command.get("summary") and not node.get("summary"):
                node["summary"] = command["summary"]
            if node.get("label") and _node_key(node) not in {_node_key(item) for item in nodes}:
                nodes.append(_node_extract(node))
        elif command_type == "upsert_edge":
            source = command.get("source", {})
            target = command.get("target", {})
            for node in (source, target):
                if node.get("label") and _node_key(node) not in {_node_key(item) for item in nodes}:
                    nodes.append(_node_extract(node))
            if source.get("label") and target.get("label"):
                edges.append(
                    {
                        "source": source["label"],
                        "target": target["label"],
                        "type": command.get("edge_type", "relates_to"),
                    }
                )
    return {
        "version": GRAPH_COMMAND_VERSION,
        "nodes": nodes,
        "edges": edges,
        "graph_commands": commands,
        "metadata": {"graph_command_count": len(commands)},
    }


def graph_commands_to_text(commands: list[dict[str, Any]]) -> str:
    """Render graph commands into durable memory text for review."""
    lines = ["Graph command batch:"]
    for command in commands:
        command_type = command["command_type"]
        if command_type == "upsert_edge":
            source = command["source"]
            target = command["target"]
            line = (
                f"- Relationship: [{source['type']}] {source['label']} "
                f"-[{command['edge_type']}]-> [{target['type']}] {target['label']}"
            )
        elif command_type == "mark_conflict":
            line = (
                "- Conflict: "
                f"{command.get('memory_id', '(current memory)')} conflicts with "
                f"{command.get('other_memory_id', '(missing other memory)')}"
            )
        else:
            node = command.get("node", {})
            line = f"- Node: [{node.get('type', 'memory')}] {node.get('label', '')}"
        if command.get("summary"):
            line += f"; summary: {command['summary']}"
        if command.get("evidence"):
            line += f"; evidence: {command['evidence']}"
        lines.append(line)
    return "\n".join(lines)


def _normalize_one(update: dict[str, Any], *, scope: str, confidence: str) -> dict[str, Any]:
    command_type = _command_type(update)
    item_confidence = normalize_confidence(str(update.get("confidence", confidence)))
    item_scope = normalize_scope(str(update.get("scope", scope)))
    evidence = _clean_text(update.get("evidence") or update.get("source_quote") or update.get("quote"), 1200)
    summary = _clean_text(update.get("summary") or update.get("description"), 800)
    reason = _clean_text(update.get("reason"), 600)

    if command_type == "upsert_edge":
        source = _node_ref(
            update.get("source"),
            fallback_type=update.get("source_type"),
            fallback_label=update.get("source_label"),
        )
        target = _node_ref(
            update.get("target"),
            fallback_type=update.get("target_type"),
            fallback_label=update.get("target_label"),
        )
        if not source["label"] or not target["label"]:
            raise ValueError("upsert_edge requires source and target labels")
        edge_type = _clean_identifier(update.get("edge_type") or update.get("type") or update.get("relation"))
        if edge_type in GRAPH_NODE_TYPES:
            edge_type = "relates_to"
        return {
            "command_type": "upsert_edge",
            "scope": item_scope,
            "confidence": item_confidence,
            "source": source,
            "target": target,
            "edge_type": edge_type or "relates_to",
            "label": _clean_text(update.get("label"), 160),
            "summary": summary,
            "evidence": evidence,
            "reason": reason,
        }

    if command_type == "mark_conflict":
        return {
            "command_type": "mark_conflict",
            "scope": item_scope,
            "confidence": item_confidence,
            "memory_id": _clean_text(update.get("memory_id"), 80),
            "other_memory_id": _clean_text(update.get("other_memory_id") or update.get("target_memory_id"), 80),
            "relation": _clean_identifier(update.get("relation") or "conflicts_with"),
            "summary": summary,
            "evidence": evidence,
            "reason": reason,
        }

    node = _node_ref(
        update.get("node"),
        fallback_type=update.get("node_type") or update.get("kind") or update.get("type"),
        fallback_label=update.get("label") or update.get("text") or update.get("memory"),
    )
    if not node["label"]:
        raise ValueError(f"{command_type} requires a node label or text")
    return {
        "command_type": command_type,
        "scope": item_scope,
        "confidence": item_confidence,
        "node": node,
        "summary": summary or _clean_text(update.get("text") or update.get("memory"), 800),
        "evidence": evidence or _clean_text(update.get("text") or update.get("memory"), 1200),
        "reason": reason,
    }


def _command_type(update: dict[str, Any]) -> str:
    raw = str(
        update.get("command")
        or update.get("command_type")
        or update.get("action")
        or update.get("op")
        or ""
    ).strip().lower()
    raw = raw.replace("-", "_")
    if raw in {"create_node", "update_node"}:
        raw = "upsert_node"
    if raw in {"create_edge", "link_nodes"}:
        raw = "upsert_edge"
    if raw in GRAPH_COMMAND_TYPES:
        return raw
    if update.get("source") or update.get("source_label") or update.get("target") or update.get("target_label"):
        return "upsert_edge"
    return "upsert_node"


def _node_ref(value: Any, *, fallback_type: Any = None, fallback_label: Any = None) -> dict[str, str]:
    if isinstance(value, dict):
        node_type = value.get("type") or value.get("node_type") or fallback_type or "memory"
        label = value.get("label") or value.get("name") or fallback_label or ""
        summary = value.get("summary") or ""
    else:
        node_type = fallback_type or "memory"
        label = value if value is not None else fallback_label
        summary = ""
    node_type = _clean_node_type(node_type)
    return {
        "type": node_type,
        "label": _clean_text(label, 240),
        "summary": _clean_text(summary, 800),
    }


def _clean_node_type(value: Any) -> str:
    node_type = _clean_identifier(value)
    return node_type if node_type in GRAPH_NODE_TYPES else "memory"


def _clean_identifier(value: Any) -> str:
    text = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    cleaned = "".join(ch for ch in text if ch.isalnum() or ch == "_")
    return cleaned[:64]


def _clean_text(value: Any, limit: int) -> str:
    return " ".join(str(value or "").strip().split())[:limit]


def _node_key(node: dict[str, Any]) -> tuple[str, str]:
    return (str(node.get("type", "")), str(node.get("label", "")).lower())


def _node_extract(node: dict[str, str]) -> dict[str, str]:
    result = {"type": node.get("type", "memory"), "label": node.get("label", "")}
    if node.get("summary"):
        result["summary"] = node["summary"]
    return result
