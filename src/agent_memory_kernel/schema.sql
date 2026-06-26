PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS events (
    event_id       TEXT PRIMARY KEY,
    created_at     TEXT NOT NULL,
    actor          TEXT NOT NULL DEFAULT 'user',
    scope          TEXT NOT NULL DEFAULT 'professional',
    source_type    TEXT NOT NULL DEFAULT 'manual',
    source_ref     TEXT NOT NULL DEFAULT '',
    content        TEXT NOT NULL,
    metadata_json  TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS candidate_memories (
    candidate_id   TEXT PRIMARY KEY,
    event_id       TEXT NOT NULL REFERENCES events(event_id),
    created_at     TEXT NOT NULL,
    proposed_text  TEXT NOT NULL,
    kind           TEXT NOT NULL DEFAULT 'fact',
    scope          TEXT NOT NULL DEFAULT 'professional',
    confidence     TEXT NOT NULL DEFAULT 'medium',
    sensitivity    TEXT NOT NULL DEFAULT 'internal',
    source_trust   TEXT NOT NULL DEFAULT 'untrusted',
    status         TEXT NOT NULL DEFAULT 'pending',
    reason         TEXT NOT NULL DEFAULT '',
    extraction_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS memories (
    memory_id      TEXT PRIMARY KEY,
    candidate_id   TEXT REFERENCES candidate_memories(candidate_id),
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL,
    text           TEXT NOT NULL,
    kind           TEXT NOT NULL DEFAULT 'fact',
    scope          TEXT NOT NULL DEFAULT 'professional',
    confidence     TEXT NOT NULL DEFAULT 'medium',
    sensitivity    TEXT NOT NULL DEFAULT 'internal',
    source_trust   TEXT NOT NULL DEFAULT 'untrusted',
    status         TEXT NOT NULL DEFAULT 'active',
    expires_at     TEXT
);

CREATE TABLE IF NOT EXISTS nodes (
    node_id        TEXT PRIMARY KEY,
    memory_id      TEXT NOT NULL REFERENCES memories(memory_id),
    node_type      TEXT NOT NULL,
    label          TEXT NOT NULL,
    scope          TEXT NOT NULL DEFAULT 'professional'
);

CREATE TABLE IF NOT EXISTS edges (
    edge_id        TEXT PRIMARY KEY,
    source_node_id TEXT NOT NULL REFERENCES nodes(node_id),
    target_node_id TEXT NOT NULL REFERENCES nodes(node_id),
    edge_type      TEXT NOT NULL,
    memory_id      TEXT NOT NULL REFERENCES memories(memory_id)
);

CREATE TABLE IF NOT EXISTS sources (
    source_id      TEXT PRIMARY KEY,
    memory_id      TEXT NOT NULL REFERENCES memories(memory_id),
    event_id       TEXT NOT NULL REFERENCES events(event_id),
    source_type    TEXT NOT NULL,
    source_ref     TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id       TEXT PRIMARY KEY,
    created_at     TEXT NOT NULL,
    action         TEXT NOT NULL,
    target_type    TEXT NOT NULL,
    target_id      TEXT NOT NULL,
    actor          TEXT NOT NULL DEFAULT 'user',
    details_json   TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS review_actions (
    review_id      TEXT PRIMARY KEY,
    created_at     TEXT NOT NULL,
    candidate_id   TEXT NOT NULL REFERENCES candidate_memories(candidate_id),
    action         TEXT NOT NULL,
    actor          TEXT NOT NULL DEFAULT 'user',
    reason         TEXT NOT NULL DEFAULT ''
);

CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
USING fts5(text, kind, scope, content='memories', content_rowid='rowid');

CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, text, kind, scope)
    VALUES (new.rowid, new.text, new.kind, new.scope);
END;

CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, text, kind, scope)
    VALUES ('delete', old.rowid, old.text, old.kind, old.scope);
END;

CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, text, kind, scope)
    VALUES ('delete', old.rowid, old.text, old.kind, old.scope);
    INSERT INTO memories_fts(rowid, text, kind, scope)
    VALUES (new.rowid, new.text, new.kind, new.scope);
END;

CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidate_memories(status);
CREATE INDEX IF NOT EXISTS idx_candidates_scope ON candidate_memories(scope);
CREATE INDEX IF NOT EXISTS idx_memories_scope ON memories(scope);
CREATE INDEX IF NOT EXISTS idx_memories_status ON memories(status);
CREATE INDEX IF NOT EXISTS idx_events_scope ON events(scope);
CREATE INDEX IF NOT EXISTS idx_sources_memory ON sources(memory_id);
