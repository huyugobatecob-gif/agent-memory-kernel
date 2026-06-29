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


def _array(description: str, items: dict[str, Any]) -> dict[str, Any]:
    return {"type": "array", "description": description, "items": items}


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
    "memory_prompt_budget": {
        "endpoint": "/prompt-budget",
        "description": "Resolve the effective memory prompt budget for a main model.",
        "inputSchema": _schema(
            {
                "model_id": _string("Main model id, such as gpt-4.1-mini or claude-sonnet.", ""),
                "token_budget": _integer("Requested memory token budget. Zero uses model default.", 0),
            }
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
    "memory_observability": {
        "endpoint": "/observability",
        "description": "Summarize Router, Keeper, and LLM usage telemetry for memory operations.",
        "inputSchema": _schema(
            {
                "scope": _string("Optional memory scope/lane.", ""),
                "thread_id": _string("Optional thread id.", ""),
                "limit": _integer("Maximum recent Router/Keeper/usage rows.", 20),
            }
        ),
    },
    "memory_migration_status": {
        "endpoint": "/migration/status",
        "description": "Check SQLite schema version, required tables/columns, and migration compatibility.",
        "inputSchema": _schema(
            {
                "integrity_check": _boolean("Run SQLite quick_check.", True),
            }
        ),
    },
    "memory_conformance_certify": {
        "endpoint": "/conformance/certify",
        "description": "Run public conformance scenarios and return an adapter compatibility badge report.",
        "inputSchema": _schema(
            {
                "adapter_name": _string("Adapter or runtime name.", "mcp-runtime"),
                "adapter_version": _string("Adapter or runtime version.", ""),
                "seed_fixture": _boolean("Seed the public conformance fixture before certifying.", False),
            }
        ),
    },
    "memory_backup_database": {
        "endpoint": "/backup",
        "description": "Create a SQLite backup of the memory database.",
        "inputSchema": _schema(
            {
                "out_path": _string("Backup database path to create."),
                "actor": _string("Actor creating the backup.", "mcp"),
                "overwrite": _boolean("Overwrite an existing backup path.", False),
            },
            ["out_path"],
        ),
    },
    "memory_restore_database": {
        "endpoint": "/restore",
        "description": "Restore a SQLite backup into a target database path.",
        "inputSchema": _schema(
            {
                "backup_path": _string("Backup database path to restore from."),
                "target_path": _string("Target database path to create."),
                "actor": _string("Actor restoring the backup.", "mcp"),
                "overwrite": _boolean("Overwrite an existing target database.", False),
            },
            ["backup_path", "target_path"],
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
    "memory_review_inbox": {
        "endpoint": "/review/inbox",
        "description": "Show review candidates with source context, risk flags, graph preview, and operator handles.",
        "inputSchema": _schema(
            {
                "status": _string("Inbox status filter: open, pending, quarantined, approved, rejected, or all.", "open"),
                "scope": _string("Optional memory scope/lane.", ""),
                "limit": _integer("Maximum inbox items.", 50),
            }
        ),
    },
    "memory_notifications_list": {
        "endpoint": "/notifications/list",
        "description": "List operator notifications for review, export, and maintenance work.",
        "inputSchema": _schema(
            {
                "status": _string("Notification status: open, acknowledged, resolved, or all.", "open"),
                "scope": _string("Optional memory scope/lane.", ""),
                "topic": _string("Optional notification topic.", ""),
                "severity": _string("Optional severity: info, warning, high, or critical.", ""),
                "assigned_to": _string("Optional assigned operator filter.", ""),
                "sla_status": _string(
                    "Optional SLA filter: overdue, due_soon, on_track, no_due_date, invalid_due_date, or resolved.",
                    "",
                ),
                "target_type": _string("Optional target type filter.", ""),
                "target_id": _string("Optional target id filter.", ""),
                "limit": _integer("Maximum notifications.", 50),
            }
        ),
    },
    "memory_notification_escalations": {
        "endpoint": "/notifications/escalations",
        "description": "List SLA-driven notification escalations without sending transports.",
        "inputSchema": _schema(
            {
                "scope": _string("Optional memory scope/lane.", ""),
                "assigned_to": _string("Optional assigned operator filter.", ""),
                "include_acknowledged": _boolean("Include acknowledged unresolved notifications.", True),
                "limit": _integer("Maximum escalations.", 50),
            }
        ),
    },
    "memory_notifications_transport": {
        "endpoint": "/notifications/transport",
        "description": "Build webhook, email, or push payloads for operator notifications.",
        "inputSchema": _schema(
            {
                "transport": _string("Transport shape: webhook, email, or push.", "webhook"),
                "status": _string("Notification status: open, acknowledged, resolved, or all.", "open"),
                "scope": _string("Optional memory scope/lane.", ""),
                "topic": _string("Optional notification topic.", ""),
                "severity": _string("Optional severity: info, warning, high, or critical.", ""),
                "assigned_to": _string("Optional assigned operator filter.", ""),
                "sla_status": _string(
                    "Optional SLA filter: overdue, due_soon, on_track, no_due_date, invalid_due_date, or resolved.",
                    "",
                ),
                "limit": _integer("Maximum payloads.", 50),
            }
        ),
    },
    "memory_notification_assign": {
        "endpoint": "/notifications/assign",
        "description": "Assign an operator notification to a reviewer.",
        "inputSchema": _schema(
            {
                "notification_id": _string("Notification id."),
                "assigned_to": _string("Reviewer or operator id."),
                "actor": _string("Assigning actor.", "reviewer"),
                "due_at": _string("Optional due timestamp.", ""),
                "reason": _string("Assignment reason.", ""),
            },
            ["notification_id", "assigned_to"],
        ),
    },
    "memory_notification_ack": {
        "endpoint": "/notifications/ack",
        "description": "Acknowledge an operator notification without resolving it.",
        "inputSchema": _schema(
            {
                "notification_id": _string("Notification id."),
                "actor": _string("Acknowledging actor.", "reviewer"),
                "reason": _string("Acknowledgement reason.", ""),
            },
            ["notification_id"],
        ),
    },
    "memory_notification_resolve": {
        "endpoint": "/notifications/resolve",
        "description": "Resolve an operator notification after the required action is complete.",
        "inputSchema": _schema(
            {
                "notification_id": _string("Notification id."),
                "actor": _string("Resolving actor.", "reviewer"),
                "reason": _string("Resolution reason.", ""),
            },
            ["notification_id"],
        ),
    },
    "memory_review_batch": {
        "endpoint": "/review/batch",
        "description": "Approve or reject multiple review candidates with per-item results.",
        "inputSchema": _schema(
            {
                "action": _string("Batch action: approve or reject."),
                "candidate_ids": {
                    "type": "array",
                    "description": "Candidate ids to process.",
                    "items": {"type": "string"},
                },
                "actor": _string("Reviewing actor.", "mcp"),
                "reason": _string("Shared review reason.", ""),
                "dry_run": _boolean("Preview policy and per-item results without mutating memory.", False),
                "stop_on_error": _boolean("Stop processing after the first item error.", False),
            },
            ["action", "candidate_ids"],
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
    "memory_correct": {
        "endpoint": "/memory/correct",
        "description": "Correct active memory text and invalidate derived memory surfaces.",
        "inputSchema": _schema(
            {
                "memory_id": _string("Active memory id to correct."),
                "text": _string("Replacement memory text."),
                "actor": _string("Correcting actor.", "mcp"),
                "reason": _string("Correction reason.", ""),
            },
            ["memory_id", "text"],
        ),
    },
    "memory_lifecycle_batch": {
        "endpoint": "/memory/lifecycle-batch",
        "description": "Batch correct, delete, distrust, or expire active memories with optional dry-run.",
        "inputSchema": _schema(
            {
                "operations": _array(
                    "Lifecycle operations: {action, memory_id, text?, reason?}.",
                    {"type": "object"},
                ),
                "actor": _string("Batch actor.", "mcp"),
                "reason": _string("Default reason.", ""),
                "dry_run": _boolean("Preview without mutating memory.", False),
                "stop_on_error": _boolean("Stop after the first item error.", False),
            },
            ["operations"],
        ),
    },
    "memory_delete": {
        "endpoint": "/memory/delete",
        "description": "Soft-delete active memory and suppress prompt-facing retrieval.",
        "inputSchema": _schema(
            {
                "memory_id": _string("Active memory id to delete."),
                "actor": _string("Deleting actor.", "mcp"),
                "reason": _string("Delete reason.", ""),
            },
            ["memory_id"],
        ),
    },
    "memory_distrust": {
        "endpoint": "/memory/distrust",
        "description": "Mark active memory as distrusted while keeping it for audit.",
        "inputSchema": _schema(
            {
                "memory_id": _string("Active memory id to distrust."),
                "actor": _string("Distrusting actor.", "mcp"),
                "reason": _string("Distrust reason.", ""),
            },
            ["memory_id"],
        ),
    },
    "memory_expire": {
        "endpoint": "/memory/expire",
        "description": "Expire active memory and suppress prompt-facing retrieval.",
        "inputSchema": _schema(
            {
                "memory_id": _string("Active memory id to expire."),
                "actor": _string("Expiring actor.", "mcp"),
                "reason": _string("Expiry reason.", ""),
            },
            ["memory_id"],
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
    "memory_export_control": {
        "endpoint": "/export/control",
        "description": "Preview export policy, scope counts, and aggregate risk before memory leaves the store.",
        "inputSchema": _schema(
            {
                "actor": _string("Exporting actor.", "mcp"),
                "scope": _string("Optional memory scope/lane.", ""),
                "project": _string("Optional project filter.", ""),
                "redaction_profile": _string("Redaction profile: full, safe, or metadata.", "full"),
                "approval_id": _string("Optional approved sensitive export approval id.", ""),
                "retention_days": _integer("Optional retention days for this export.", 0),
            }
        ),
    },
    "memory_export_custody": {
        "endpoint": "/export/custody",
        "description": "Preview encrypted export key custody and artifact handling without storing secrets.",
        "inputSchema": _schema(
            {
                "actor": _string("Exporting actor.", "mcp"),
                "scope": _string("Optional memory scope/lane.", ""),
                "project": _string("Optional project filter.", ""),
                "redaction_profile": _string("Redaction profile: full, safe, or metadata.", "safe"),
                "approval_id": _string("Optional approved sensitive export approval id.", ""),
                "retention_days": _integer("Optional retention days for this export.", 0),
                "artifact_ref": _string("Optional external artifact reference.", ""),
                "passphrase_env": _string("Environment variable containing export passphrase.", "AGENT_MEMORY_EXPORT_PASSPHRASE"),
                "offhost_required": _boolean("Require off-host encrypted artifact custody.", True),
            }
        ),
    },
    "memory_export_profile": {
        "endpoint": "/export/profile",
        "description": "Export project profile and memory tree, optionally applying a redaction profile.",
        "inputSchema": _schema(
            {
                "actor": _string("Exporting actor.", "mcp"),
                "scope": _string("Optional memory scope/lane.", ""),
                "project": _string("Optional project filter.", ""),
                "redaction_profile": _string("Redaction profile: full, safe, or metadata.", "full"),
                "approval_id": _string("Optional approved sensitive export approval id.", ""),
                "retention_days": _integer("Optional retention days for this export.", 0),
                "artifact_ref": _string("Optional external artifact reference.", ""),
            }
        ),
    },
    "memory_vault_export": {
        "endpoint": "/vault/export",
        "description": "Export active memory as a machine-readable local markdown vault.",
        "inputSchema": _schema(
            {
                "out_dir": _string("Output directory for the vault.", "agent-memory-vault"),
                "actor": _string("Exporting actor.", "mcp"),
                "scope": _string("Optional memory scope/lane.", ""),
                "redaction_profile": _string("Redaction profile: full, safe, or metadata.", "full"),
                "approval_id": _string("Optional approved sensitive export approval id.", ""),
                "retention_days": _integer("Optional retention days for this export.", 0),
            }
        ),
    },
    "memory_vault_import": {
        "endpoint": "/vault/import",
        "description": "Import a machine-readable local markdown vault through the review lifecycle.",
        "inputSchema": _schema(
            {
                "in_dir": _string("Vault directory to import.", "agent-memory-vault"),
                "actor": _string("Importing actor.", "vault-import"),
                "auto_approve": _boolean("Auto-approve imported candidates when policy allows it.", False),
            }
        ),
    },
    "memory_export_encrypted_profile": {
        "endpoint": "/export/encrypted-profile",
        "description": "Export an encrypted project profile envelope.",
        "inputSchema": _schema(
            {
                "actor": _string("Exporting actor.", "mcp"),
                "scope": _string("Optional memory scope/lane.", ""),
                "project": _string("Optional project filter.", ""),
                "redaction_profile": _string("Redaction profile: full, safe, or metadata.", "full"),
                "approval_id": _string("Optional approved sensitive export approval id.", ""),
                "retention_days": _integer("Optional retention days for this export.", 0),
                "artifact_ref": _string("Optional external artifact reference.", ""),
                "passphrase_env": _string("Environment variable containing passphrase.", "AGENT_MEMORY_EXPORT_PASSPHRASE"),
            }
        ),
    },
    "memory_import_encrypted_profile": {
        "endpoint": "/import/encrypted-profile",
        "description": "Import an encrypted project profile envelope.",
        "inputSchema": _schema(
            {
                "envelope": {
                    "type": "object",
                    "description": "Encrypted export envelope.",
                },
                "passphrase_env": _string("Environment variable containing passphrase.", "AGENT_MEMORY_EXPORT_PASSPHRASE"),
            },
            ["envelope"],
        ),
    },
    "memory_export_approval_request": {
        "endpoint": "/export/approval/request",
        "description": "Request one-time approval for a sensitive full export.",
        "inputSchema": _schema(
            {
                "actor": _string("Actor that will perform the export.", "mcp"),
                "requested_by": _string("Operator requesting approval.", "mcp"),
                "scope": _string("Optional memory scope/lane.", ""),
                "project": _string("Optional project filter.", ""),
                "export_kind": _string("Export kind: profile or markdown.", "profile"),
                "redaction_profile": _string("Redaction profile: full, safe, or metadata.", "full"),
                "reason": _string("Reason for the export request.", ""),
            }
        ),
    },
    "memory_export_approval_list": {
        "endpoint": "/export/approval/list",
        "description": "List sensitive export approval requests.",
        "inputSchema": _schema(
            {
                "status": _string("Status filter.", "pending"),
                "actor": _string("Optional exporting actor filter.", ""),
                "scope": _string("Optional memory scope/lane.", ""),
                "limit": _integer("Maximum approvals.", 50),
            }
        ),
    },
    "memory_export_approval_approve": {
        "endpoint": "/export/approval/approve",
        "description": "Approve a pending sensitive export approval request.",
        "inputSchema": _schema(
            {
                "approval_id": _string("Export approval id."),
                "actor": _string("Approving operator.", "reviewer"),
                "reason": _string("Approval reason.", ""),
            },
            ["approval_id"],
        ),
    },
    "memory_export_approval_reject": {
        "endpoint": "/export/approval/reject",
        "description": "Reject a pending sensitive export approval request.",
        "inputSchema": _schema(
            {
                "approval_id": _string("Export approval id."),
                "actor": _string("Rejecting operator.", "reviewer"),
                "reason": _string("Rejection reason.", ""),
            },
            ["approval_id"],
        ),
    },
    "memory_export_retention_list": {
        "endpoint": "/export/retention/list",
        "description": "List recorded exports and retention status.",
        "inputSchema": _schema(
            {
                "status": _string("Status filter.", "active"),
                "actor": _string("Optional exporting actor filter.", ""),
                "scope": _string("Optional memory scope/lane.", ""),
                "expired_only": _boolean("Only active records past expires_at.", False),
                "limit": _integer("Maximum records.", 50),
            }
        ),
    },
    "memory_export_retention_enforce": {
        "endpoint": "/export/retention/enforce",
        "description": "Mark active export records expired after expires_at.",
        "inputSchema": _schema(
            {
                "actor": _string("Retention actor.", "system"),
            }
        ),
    },
    "memory_export_retention_purge": {
        "endpoint": "/export/retention/purge",
        "description": "Mark an export record purged after external artifact cleanup.",
        "inputSchema": _schema(
            {
                "export_id": _string("Export record id."),
                "actor": _string("Purging operator.", "reviewer"),
                "reason": _string("Purge reason.", ""),
            },
            ["export_id"],
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
    "memory_graph_browser": {
        "endpoint": "/graph/browser",
        "description": "Build graph browser data with nodes, edges, and source previews.",
        "inputSchema": _schema(
            {
                "scope": _string("Optional memory scope/lane.", ""),
                "node_type": _string("Optional graph node type.", ""),
                "query": _string("Optional node label/summary search.", ""),
                "limit": _integer("Maximum nodes.", 50),
                "evidence_limit": _integer("Maximum source previews per node or edge.", 3),
            }
        ),
    },
    "memory_graph_optimize": {
        "endpoint": "/graph/optimize",
        "description": "Run a graph maintenance pass such as duplicate consolidation.",
        "inputSchema": _schema(
            {
                "mode": _string(
                    "Optimization mode: record_linkage, consolidate_duplicates, knowledge_consistency, llm_check, interests_reconnect, hemisphere_markup, or brain_calibration.",
                    "record_linkage",
                ),
                "scope": _string("Memory scope/lane.", "professional"),
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
    "memory_conflict_detect": {
        "endpoint": "/conflict/detect",
        "description": "Detect likely active-memory conflicts and optionally record open conflict records.",
        "inputSchema": _schema(
            {
                "scope": _string("Optional memory scope/lane.", ""),
                "kind": _string("Optional memory kind.", ""),
                "limit": _integer("Maximum detections.", 50),
                "min_overlap": {
                    "type": "number",
                    "description": "Minimum containment overlap.",
                    "default": 0.5,
                },
                "min_jaccard": {
                    "type": "number",
                    "description": "Minimum Jaccard overlap.",
                    "default": 0.35,
                },
                "record": _boolean("Record detections as open conflicts.", False),
                "actor": _string("Actor for recorded conflicts.", "system"),
                "reason": _string("Reason for recorded conflicts.", ""),
            }
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
    "memory_keeper_eval": {
        "endpoint": "/keeper-eval/run",
        "description": "Run offline Keeper extraction regression evals.",
        "inputSchema": _schema({}),
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
