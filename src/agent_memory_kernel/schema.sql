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

CREATE TABLE IF NOT EXISTS conversation_turns (
    turn_id        TEXT PRIMARY KEY,
    thread_id      TEXT NOT NULL DEFAULT 'default',
    created_at     TEXT NOT NULL,
    role           TEXT NOT NULL,
    actor          TEXT NOT NULL DEFAULT 'user',
    scope          TEXT NOT NULL DEFAULT 'professional',
    content        TEXT NOT NULL,
    metadata_json  TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS thread_messages (
    message_id     TEXT PRIMARY KEY,
    thread_id      TEXT NOT NULL DEFAULT 'default',
    turn_id        TEXT REFERENCES conversation_turns(turn_id),
    created_at     TEXT NOT NULL,
    role           TEXT NOT NULL,
    actor          TEXT NOT NULL DEFAULT 'user',
    content        TEXT NOT NULL,
    metadata_json  TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS thread_summaries (
    summary_id     TEXT PRIMARY KEY,
    thread_id      TEXT NOT NULL DEFAULT 'default',
    created_at     TEXT NOT NULL,
    scope          TEXT NOT NULL DEFAULT 'professional',
    summary        TEXT NOT NULL,
    summary_type   TEXT NOT NULL DEFAULT 'rolling',
    metadata_json  TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS memory_items (
    item_id        TEXT PRIMARY KEY,
    memory_id      TEXT REFERENCES memories(memory_id),
    event_id       TEXT REFERENCES events(event_id),
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL,
    item_type      TEXT NOT NULL DEFAULT 'fact',
    scope          TEXT NOT NULL DEFAULT 'professional',
    text           TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'active',
    confidence     TEXT NOT NULL DEFAULT 'medium',
    sensitivity    TEXT NOT NULL DEFAULT 'internal',
    source_trust   TEXT NOT NULL DEFAULT 'untrusted',
    owner          TEXT NOT NULL DEFAULT '',
    project        TEXT NOT NULL DEFAULT '',
    expires_at     TEXT,
    metadata_json  TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS memory_graph_nodes (
    graph_node_id  TEXT PRIMARY KEY,
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL,
    node_type      TEXT NOT NULL,
    label          TEXT NOT NULL,
    canonical_key  TEXT NOT NULL,
    scope          TEXT NOT NULL DEFAULT 'professional',
    group_label    TEXT NOT NULL DEFAULT '',
    blob           TEXT NOT NULL DEFAULT '',
    summary        TEXT NOT NULL DEFAULT '',
    importance     REAL NOT NULL DEFAULT 0.5,
    confidence     TEXT NOT NULL DEFAULT 'medium',
    status         TEXT NOT NULL DEFAULT 'active',
    aliases_json   TEXT NOT NULL DEFAULT '[]',
    topics_json    TEXT NOT NULL DEFAULT '[]',
    chronology_json TEXT NOT NULL DEFAULT '[]',
    verified_status TEXT NOT NULL DEFAULT 'unverified',
    verified_at    TEXT,
    verifier       TEXT NOT NULL DEFAULT '',
    hemisphere     TEXT NOT NULL DEFAULT '',
    visual_x       REAL,
    visual_y       REAL,
    embedding_json TEXT NOT NULL DEFAULT '[]',
    metadata_json  TEXT NOT NULL DEFAULT '{}',
    UNIQUE(scope, node_type, canonical_key)
);

CREATE TABLE IF NOT EXISTS memory_graph_edges (
    graph_edge_id          TEXT PRIMARY KEY,
    created_at             TEXT NOT NULL,
    updated_at             TEXT NOT NULL,
    source_graph_node_id   TEXT NOT NULL REFERENCES memory_graph_nodes(graph_node_id),
    target_graph_node_id   TEXT NOT NULL REFERENCES memory_graph_nodes(graph_node_id),
    edge_type              TEXT NOT NULL,
    label                  TEXT NOT NULL DEFAULT '',
    weight                 REAL NOT NULL DEFAULT 1.0,
    confidence             TEXT NOT NULL DEFAULT 'medium',
    status                 TEXT NOT NULL DEFAULT 'active',
    source_memory_id       TEXT REFERENCES memories(memory_id),
    source_event_id        TEXT REFERENCES events(event_id),
    evidence_count         INTEGER NOT NULL DEFAULT 0,
    metadata_json          TEXT NOT NULL DEFAULT '{}',
    UNIQUE(source_graph_node_id, target_graph_node_id, edge_type)
);

CREATE TABLE IF NOT EXISTS node_evidence (
    evidence_id    TEXT PRIMARY KEY,
    graph_node_id  TEXT NOT NULL REFERENCES memory_graph_nodes(graph_node_id),
    item_id        TEXT REFERENCES memory_items(item_id),
    memory_id      TEXT REFERENCES memories(memory_id),
    event_id       TEXT REFERENCES events(event_id),
    created_at     TEXT NOT NULL,
    source_ref     TEXT NOT NULL DEFAULT '',
    quote          TEXT NOT NULL DEFAULT '',
    confidence     TEXT NOT NULL DEFAULT 'medium'
);

CREATE TABLE IF NOT EXISTS edge_evidence (
    evidence_id    TEXT PRIMARY KEY,
    graph_edge_id  TEXT NOT NULL REFERENCES memory_graph_edges(graph_edge_id),
    item_id        TEXT REFERENCES memory_items(item_id),
    memory_id      TEXT REFERENCES memories(memory_id),
    event_id       TEXT REFERENCES events(event_id),
    created_at     TEXT NOT NULL,
    source_ref     TEXT NOT NULL DEFAULT '',
    quote          TEXT NOT NULL DEFAULT '',
    confidence     TEXT NOT NULL DEFAULT 'medium'
);

CREATE TABLE IF NOT EXISTS keeper_runs (
    run_id         TEXT PRIMARY KEY,
    event_id       TEXT REFERENCES events(event_id),
    memory_id      TEXT REFERENCES memories(memory_id),
    created_at     TEXT NOT NULL,
    model          TEXT NOT NULL DEFAULT 'rule-based-keeper-v0',
    status         TEXT NOT NULL DEFAULT 'completed',
    extracted_json TEXT NOT NULL DEFAULT '{}',
    notes_json     TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS graph_commands (
    command_id     TEXT PRIMARY KEY,
    run_id         TEXT REFERENCES keeper_runs(run_id),
    created_at     TEXT NOT NULL,
    command_type   TEXT NOT NULL,
    payload_json   TEXT NOT NULL DEFAULT '{}',
    status         TEXT NOT NULL DEFAULT 'applied'
);

CREATE TABLE IF NOT EXISTS memory_graph_groups (
    group_id       TEXT PRIMARY KEY,
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL,
    scope          TEXT NOT NULL DEFAULT 'professional',
    group_label    TEXT NOT NULL,
    node_type      TEXT NOT NULL,
    node_count     INTEGER NOT NULL DEFAULT 0,
    edge_count     INTEGER NOT NULL DEFAULT 0,
    metadata_json  TEXT NOT NULL DEFAULT '{}',
    UNIQUE(scope, group_label, node_type)
);

CREATE TABLE IF NOT EXISTS semantic_analyses (
    analysis_id            TEXT PRIMARY KEY,
    run_id                 TEXT REFERENCES keeper_runs(run_id),
    event_id               TEXT REFERENCES events(event_id),
    memory_id              TEXT REFERENCES memories(memory_id),
    created_at             TEXT NOT NULL,
    analyzer               TEXT NOT NULL DEFAULT 'rule-based-light-model-v0',
    scope                  TEXT NOT NULL DEFAULT 'professional',
    facts_json             TEXT NOT NULL DEFAULT '[]',
    chronology_json        TEXT NOT NULL DEFAULT '[]',
    key_topics_json        TEXT NOT NULL DEFAULT '[]',
    people_json            TEXT NOT NULL DEFAULT '[]',
    events_json            TEXT NOT NULL DEFAULT '[]',
    verified_entities_json TEXT NOT NULL DEFAULT '[]',
    metadata_json          TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS profile_notes (
    profile_note_id TEXT PRIMARY KEY,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    scope           TEXT NOT NULL DEFAULT 'professional',
    note_type       TEXT NOT NULL,
    title           TEXT NOT NULL DEFAULT '',
    content         TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active',
    metadata_json   TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS project_profiles (
    profile_id                    TEXT PRIMARY KEY,
    created_at                    TEXT NOT NULL,
    updated_at                    TEXT NOT NULL,
    scope                         TEXT NOT NULL DEFAULT 'professional',
    project                       TEXT NOT NULL DEFAULT '',
    access_json                   TEXT NOT NULL DEFAULT '{}',
    env_snapshot_json             TEXT NOT NULL DEFAULT '{}',
    saved_model_choices_json      TEXT NOT NULL DEFAULT '{}',
    data_enrichment_snapshot_json TEXT NOT NULL DEFAULT '{}',
    metadata_json                 TEXT NOT NULL DEFAULT '{}',
    UNIQUE(scope, project)
);

CREATE TABLE IF NOT EXISTS llm_usage_stats (
    usage_id      TEXT PRIMARY KEY,
    created_at    TEXT NOT NULL,
    provider      TEXT NOT NULL DEFAULT '',
    model         TEXT NOT NULL DEFAULT '',
    scope         TEXT NOT NULL DEFAULT 'professional',
    thread_id     TEXT NOT NULL DEFAULT '',
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens  INTEGER NOT NULL DEFAULT 0,
    cost          REAL NOT NULL DEFAULT 0,
    currency      TEXT NOT NULL DEFAULT 'USD',
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS graph_optimization_runs (
    optimization_id TEXT PRIMARY KEY,
    created_at      TEXT NOT NULL,
    optimization_type TEXT NOT NULL,
    scope           TEXT NOT NULL DEFAULT 'professional',
    status          TEXT NOT NULL DEFAULT 'completed',
    before_json     TEXT NOT NULL DEFAULT '{}',
    after_json      TEXT NOT NULL DEFAULT '{}',
    findings_json   TEXT NOT NULL DEFAULT '[]',
    metadata_json   TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS router_runs (
    router_run_id            TEXT PRIMARY KEY,
    created_at               TEXT NOT NULL,
    thread_id                TEXT NOT NULL DEFAULT 'default',
    scope                    TEXT NOT NULL DEFAULT 'professional',
    user_id                  TEXT NOT NULL DEFAULT '',
    agent_id                 TEXT NOT NULL DEFAULT '',
    model_id                 TEXT NOT NULL DEFAULT '',
    mode                     TEXT NOT NULL DEFAULT 'chat',
    query                    TEXT NOT NULL,
    token_budget             INTEGER NOT NULL DEFAULT 0,
    selected_branch_ids_json TEXT NOT NULL DEFAULT '[]',
    access_decisions_json    TEXT NOT NULL DEFAULT '[]',
    warnings_json            TEXT NOT NULL DEFAULT '[]',
    metadata_json            TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS keeper_jobs (
    keeper_job_id      TEXT PRIMARY KEY,
    created_at         TEXT NOT NULL,
    thread_id          TEXT NOT NULL DEFAULT 'default',
    scope              TEXT NOT NULL DEFAULT 'professional',
    user_id            TEXT NOT NULL DEFAULT '',
    agent_id           TEXT NOT NULL DEFAULT '',
    model_id           TEXT NOT NULL DEFAULT '',
    turn_ids_json      TEXT NOT NULL DEFAULT '[]',
    event_id           TEXT NOT NULL DEFAULT '',
    candidate_ids_json TEXT NOT NULL DEFAULT '[]',
    status             TEXT NOT NULL DEFAULT 'completed',
    warnings_json      TEXT NOT NULL DEFAULT '[]',
    metadata_json      TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS shadow_traces (
    shadow_trace_id         TEXT PRIMARY KEY,
    created_at              TEXT NOT NULL,
    thread_id               TEXT NOT NULL DEFAULT 'default',
    scope                   TEXT NOT NULL DEFAULT 'professional',
    user_id                 TEXT NOT NULL DEFAULT '',
    agent_id                TEXT NOT NULL DEFAULT '',
    model_id                TEXT NOT NULL DEFAULT '',
    mode                    TEXT NOT NULL DEFAULT 'shadow',
    query                   TEXT NOT NULL,
    router_run_id           TEXT NOT NULL DEFAULT '',
    keeper_job_id           TEXT NOT NULL DEFAULT '',
    selected_branch_ids_json TEXT NOT NULL DEFAULT '[]',
    candidate_ids_json      TEXT NOT NULL DEFAULT '[]',
    saved_turn_ids_json     TEXT NOT NULL DEFAULT '[]',
    write_policy            TEXT NOT NULL DEFAULT 'propose_only',
    status                  TEXT NOT NULL DEFAULT 'recorded',
    warnings_json           TEXT NOT NULL DEFAULT '[]',
    metadata_json           TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS digital_brain_state (
    state_id       TEXT PRIMARY KEY,
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL,
    scope          TEXT NOT NULL DEFAULT 'professional',
    left_count     INTEGER NOT NULL DEFAULT 0,
    right_count    INTEGER NOT NULL DEFAULT 0,
    calibration_json TEXT NOT NULL DEFAULT '{}',
    metadata_json  TEXT NOT NULL DEFAULT '{}',
    UNIQUE(scope)
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
CREATE INDEX IF NOT EXISTS idx_conversation_turns_thread ON conversation_turns(thread_id);
CREATE INDEX IF NOT EXISTS idx_thread_messages_thread ON thread_messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_thread_summaries_thread ON thread_summaries(thread_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_memory ON memory_items(memory_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_event ON memory_items(event_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_scope ON memory_items(scope);
CREATE INDEX IF NOT EXISTS idx_memory_items_type ON memory_items(item_type);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_scope_type ON memory_graph_nodes(scope, node_type);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_label ON memory_graph_nodes(label);
CREATE INDEX IF NOT EXISTS idx_graph_edges_source ON memory_graph_edges(source_graph_node_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_target ON memory_graph_edges(target_graph_node_id);
CREATE INDEX IF NOT EXISTS idx_node_evidence_node ON node_evidence(graph_node_id);
CREATE INDEX IF NOT EXISTS idx_edge_evidence_edge ON edge_evidence(graph_edge_id);
CREATE INDEX IF NOT EXISTS idx_graph_groups_scope ON memory_graph_groups(scope);
CREATE INDEX IF NOT EXISTS idx_semantic_analyses_scope ON semantic_analyses(scope);
CREATE INDEX IF NOT EXISTS idx_profile_notes_scope_type ON profile_notes(scope, note_type);
CREATE INDEX IF NOT EXISTS idx_llm_usage_scope_thread ON llm_usage_stats(scope, thread_id);
CREATE INDEX IF NOT EXISTS idx_graph_optimizations_scope ON graph_optimization_runs(scope);
CREATE INDEX IF NOT EXISTS idx_router_runs_thread ON router_runs(thread_id);
CREATE INDEX IF NOT EXISTS idx_keeper_jobs_thread ON keeper_jobs(thread_id);
CREATE INDEX IF NOT EXISTS idx_shadow_traces_thread ON shadow_traces(thread_id);
