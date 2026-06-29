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

CREATE TABLE IF NOT EXISTS memory_conflicts (
    conflict_id      TEXT PRIMARY KEY,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL,
    scope            TEXT NOT NULL DEFAULT 'professional',
    memory_id        TEXT NOT NULL REFERENCES memories(memory_id),
    other_memory_id  TEXT NOT NULL REFERENCES memories(memory_id),
    relation         TEXT NOT NULL DEFAULT 'conflicts_with',
    status           TEXT NOT NULL DEFAULT 'open',
    winner_memory_id TEXT REFERENCES memories(memory_id),
    reason           TEXT NOT NULL DEFAULT '',
    metadata_json    TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS memory_revisions (
    revision_id             TEXT PRIMARY KEY,
    memory_id               TEXT NOT NULL REFERENCES memories(memory_id),
    created_at              TEXT NOT NULL,
    actor                   TEXT NOT NULL DEFAULT 'user',
    previous_text           TEXT NOT NULL,
    new_text                TEXT NOT NULL,
    reason                  TEXT NOT NULL DEFAULT '',
    rollback_of_revision_id TEXT NOT NULL DEFAULT '',
    metadata_json           TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS derived_invalidations (
    invalidation_id TEXT PRIMARY KEY,
    created_at      TEXT NOT NULL,
    memory_id       TEXT NOT NULL REFERENCES memories(memory_id),
    action          TEXT NOT NULL,
    actor           TEXT NOT NULL DEFAULT 'system',
    scope           TEXT NOT NULL DEFAULT 'professional',
    reason          TEXT NOT NULL DEFAULT '',
    surfaces_json   TEXT NOT NULL DEFAULT '{}',
    metadata_json   TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS memory_write_policies (
    policy_id     TEXT PRIMARY KEY,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    agent_id      TEXT NOT NULL DEFAULT '*',
    scope         TEXT NOT NULL DEFAULT '*',
    action        TEXT NOT NULL DEFAULT '*',
    decision      TEXT NOT NULL DEFAULT 'allow',
    reason        TEXT NOT NULL DEFAULT '',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(agent_id, scope, action)
);

CREATE TABLE IF NOT EXISTS memory_read_policies (
    policy_id     TEXT PRIMARY KEY,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    agent_id      TEXT NOT NULL DEFAULT '*',
    scope         TEXT NOT NULL DEFAULT '*',
    action        TEXT NOT NULL DEFAULT 'inject',
    decision      TEXT NOT NULL DEFAULT 'allow',
    reason        TEXT NOT NULL DEFAULT '',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(agent_id, scope, action)
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

CREATE TABLE IF NOT EXISTS outcome_records (
    outcome_id          TEXT PRIMARY KEY,
    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL,
    scope               TEXT NOT NULL DEFAULT 'professional',
    project             TEXT NOT NULL DEFAULT '',
    loop_id             TEXT NOT NULL DEFAULT '',
    outcome_status      TEXT NOT NULL DEFAULT 'unknown',
    score               REAL NOT NULL DEFAULT 0,
    hypothesis          TEXT NOT NULL DEFAULT '',
    action              TEXT NOT NULL DEFAULT '',
    result              TEXT NOT NULL DEFAULT '',
    cause               TEXT NOT NULL DEFAULT '',
    lesson              TEXT NOT NULL DEFAULT '',
    next_recommendation TEXT NOT NULL DEFAULT '',
    memory_id           TEXT REFERENCES memories(memory_id),
    candidate_id        TEXT REFERENCES candidate_memories(candidate_id),
    event_id            TEXT REFERENCES events(event_id),
    status              TEXT NOT NULL DEFAULT 'pending',
    metadata_json       TEXT NOT NULL DEFAULT '{}'
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

CREATE TABLE IF NOT EXISTS provider_invoice_items (
    invoice_item_id TEXT PRIMARY KEY,
    imported_at     TEXT NOT NULL,
    invoice_id      TEXT NOT NULL DEFAULT '',
    provider        TEXT NOT NULL DEFAULT '',
    model           TEXT NOT NULL DEFAULT '',
    scope           TEXT NOT NULL DEFAULT 'all',
    thread_id       TEXT NOT NULL DEFAULT '',
    period_start    TEXT NOT NULL DEFAULT '',
    period_end      TEXT NOT NULL DEFAULT '',
    total_tokens    INTEGER NOT NULL DEFAULT 0,
    amount          REAL NOT NULL DEFAULT 0,
    currency        TEXT NOT NULL DEFAULT 'USD',
    source_ref      TEXT NOT NULL DEFAULT '',
    status          TEXT NOT NULL DEFAULT 'active',
    metadata_json   TEXT NOT NULL DEFAULT '{}'
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

CREATE TABLE IF NOT EXISTS memory_export_approvals (
    approval_id       TEXT PRIMARY KEY,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    requested_by      TEXT NOT NULL DEFAULT 'user',
    actor             TEXT NOT NULL DEFAULT 'user',
    approved_by       TEXT NOT NULL DEFAULT '',
    rejected_by       TEXT NOT NULL DEFAULT '',
    scope             TEXT NOT NULL DEFAULT 'all',
    project           TEXT NOT NULL DEFAULT '',
    export_kind       TEXT NOT NULL DEFAULT 'profile',
    redaction_profile TEXT NOT NULL DEFAULT 'full',
    status            TEXT NOT NULL DEFAULT 'pending',
    reason            TEXT NOT NULL DEFAULT '',
    decision_reason   TEXT NOT NULL DEFAULT '',
    risk_flags_json   TEXT NOT NULL DEFAULT '[]',
    scope_counts_json TEXT NOT NULL DEFAULT '{}',
    used_at           TEXT,
    metadata_json     TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS memory_export_records (
    export_id          TEXT PRIMARY KEY,
    created_at         TEXT NOT NULL,
    updated_at         TEXT NOT NULL,
    actor              TEXT NOT NULL DEFAULT 'user',
    scope              TEXT NOT NULL DEFAULT 'all',
    project            TEXT NOT NULL DEFAULT '',
    export_kind        TEXT NOT NULL DEFAULT 'profile',
    redaction_profile  TEXT NOT NULL DEFAULT 'full',
    content_included   INTEGER NOT NULL DEFAULT 0,
    approval_id        TEXT NOT NULL DEFAULT '',
    retention_days     INTEGER NOT NULL DEFAULT 30,
    expires_at         TEXT NOT NULL DEFAULT '',
    status             TEXT NOT NULL DEFAULT 'active',
    artifact_ref       TEXT NOT NULL DEFAULT '',
    risk_flags_json    TEXT NOT NULL DEFAULT '[]',
    metadata_json      TEXT NOT NULL DEFAULT '{}',
    purged_at          TEXT,
    purge_reason       TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS memory_notifications (
    notification_id TEXT PRIMARY KEY,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'open',
    severity        TEXT NOT NULL DEFAULT 'info',
    topic           TEXT NOT NULL,
    scope           TEXT NOT NULL DEFAULT 'professional',
    actor           TEXT NOT NULL DEFAULT 'system',
    assigned_to     TEXT NOT NULL DEFAULT '',
    assigned_by     TEXT NOT NULL DEFAULT '',
    assigned_at     TEXT,
    due_at          TEXT NOT NULL DEFAULT '',
    target_type     TEXT NOT NULL DEFAULT '',
    target_id       TEXT NOT NULL DEFAULT '',
    title           TEXT NOT NULL DEFAULT '',
    message         TEXT NOT NULL DEFAULT '',
    action_path     TEXT NOT NULL DEFAULT '',
    dedupe_key      TEXT NOT NULL DEFAULT '',
    metadata_json   TEXT NOT NULL DEFAULT '{}',
    acknowledged_at TEXT,
    acknowledged_by TEXT NOT NULL DEFAULT '',
    resolved_at     TEXT,
    resolved_by     TEXT NOT NULL DEFAULT '',
    resolve_reason  TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS memory_notification_deliveries (
    delivery_id     TEXT PRIMARY KEY,
    notification_id TEXT NOT NULL REFERENCES memory_notifications(notification_id),
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    transport       TEXT NOT NULL DEFAULT 'webhook',
    destination     TEXT NOT NULL DEFAULT '',
    status          TEXT NOT NULL DEFAULT 'queued',
    payload_json    TEXT NOT NULL DEFAULT '{}',
    attempt_count   INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TEXT,
    delivered_at    TEXT,
    actor           TEXT NOT NULL DEFAULT 'system',
    error           TEXT NOT NULL DEFAULT '',
    metadata_json   TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS restore_drill_schedules (
    schedule_id       TEXT PRIMARY KEY,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    name              TEXT NOT NULL UNIQUE,
    status            TEXT NOT NULL DEFAULT 'active',
    scope             TEXT NOT NULL DEFAULT 'all',
    probe_query       TEXT NOT NULL DEFAULT '',
    interval_hours    INTEGER NOT NULL DEFAULT 24,
    artifact_dir      TEXT NOT NULL DEFAULT '',
    retain_artifacts  INTEGER NOT NULL DEFAULT 0,
    next_due_at       TEXT NOT NULL DEFAULT '',
    last_run_at       TEXT,
    last_status       TEXT NOT NULL DEFAULT '',
    last_result_json  TEXT NOT NULL DEFAULT '{}',
    last_error        TEXT NOT NULL DEFAULT '',
    actor             TEXT NOT NULL DEFAULT 'system',
    metadata_json     TEXT NOT NULL DEFAULT '{}'
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

CREATE TABLE IF NOT EXISTS router_feedback (
    feedback_id    TEXT PRIMARY KEY,
    created_at     TEXT NOT NULL,
    router_run_id  TEXT NOT NULL REFERENCES router_runs(router_run_id),
    memory_id      TEXT NOT NULL DEFAULT '',
    branch_id      TEXT NOT NULL DEFAULT '',
    actor          TEXT NOT NULL DEFAULT 'reviewer',
    rating         TEXT NOT NULL DEFAULT 'neutral',
    score          REAL NOT NULL DEFAULT 0,
    reason         TEXT NOT NULL DEFAULT '',
    metadata_json  TEXT NOT NULL DEFAULT '{}'
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
    idempotency_key    TEXT NOT NULL DEFAULT '',
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

CREATE TABLE IF NOT EXISTS shadow_trace_evals (
    eval_id          TEXT PRIMARY KEY,
    shadow_trace_id  TEXT NOT NULL REFERENCES shadow_traces(shadow_trace_id),
    created_at       TEXT NOT NULL,
    actor            TEXT NOT NULL DEFAULT 'reviewer',
    status           TEXT NOT NULL DEFAULT 'pass',
    score            REAL NOT NULL DEFAULT 0,
    expected_json    TEXT NOT NULL DEFAULT '{}',
    checks_json      TEXT NOT NULL DEFAULT '[]',
    findings_json    TEXT NOT NULL DEFAULT '[]',
    metadata_json    TEXT NOT NULL DEFAULT '{}'
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
CREATE INDEX IF NOT EXISTS idx_memory_conflicts_status ON memory_conflicts(status);
CREATE INDEX IF NOT EXISTS idx_memory_conflicts_scope ON memory_conflicts(scope);
CREATE INDEX IF NOT EXISTS idx_memory_revisions_memory ON memory_revisions(memory_id);
CREATE INDEX IF NOT EXISTS idx_memory_write_policies_lookup ON memory_write_policies(agent_id, scope, action);
CREATE INDEX IF NOT EXISTS idx_memory_read_policies_lookup ON memory_read_policies(agent_id, scope, action);
CREATE INDEX IF NOT EXISTS idx_memory_export_approvals_status ON memory_export_approvals(status, scope);
CREATE INDEX IF NOT EXISTS idx_memory_export_records_status ON memory_export_records(status, expires_at);
CREATE INDEX IF NOT EXISTS idx_memory_notifications_status ON memory_notifications(status, updated_at);
CREATE INDEX IF NOT EXISTS idx_memory_notifications_scope ON memory_notifications(scope, status);
CREATE INDEX IF NOT EXISTS idx_memory_notifications_target ON memory_notifications(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_notification_deliveries_status ON memory_notification_deliveries(status, updated_at);
CREATE INDEX IF NOT EXISTS idx_notification_deliveries_notification ON memory_notification_deliveries(notification_id);
CREATE INDEX IF NOT EXISTS idx_notification_deliveries_transport ON memory_notification_deliveries(transport, status);
CREATE INDEX IF NOT EXISTS idx_restore_drill_schedules_due ON restore_drill_schedules(status, next_due_at);
CREATE INDEX IF NOT EXISTS idx_restore_drill_schedules_scope ON restore_drill_schedules(scope, status);
CREATE INDEX IF NOT EXISTS idx_events_scope ON events(scope);
CREATE INDEX IF NOT EXISTS idx_sources_memory ON sources(memory_id);
CREATE INDEX IF NOT EXISTS idx_conversation_turns_thread ON conversation_turns(thread_id);
CREATE INDEX IF NOT EXISTS idx_thread_messages_thread ON thread_messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_thread_summaries_thread ON thread_summaries(thread_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_memory ON memory_items(memory_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_event ON memory_items(event_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_scope ON memory_items(scope);
CREATE INDEX IF NOT EXISTS idx_memory_items_type ON memory_items(item_type);
CREATE INDEX IF NOT EXISTS idx_outcome_records_project ON outcome_records(project);
CREATE INDEX IF NOT EXISTS idx_outcome_records_scope_status ON outcome_records(scope, outcome_status);
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
CREATE INDEX IF NOT EXISTS idx_provider_invoice_provider_period ON provider_invoice_items(provider, period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_provider_invoice_scope_thread ON provider_invoice_items(scope, thread_id);
CREATE INDEX IF NOT EXISTS idx_provider_invoice_status ON provider_invoice_items(status, invoice_id);
CREATE INDEX IF NOT EXISTS idx_graph_optimizations_scope ON graph_optimization_runs(scope);
CREATE INDEX IF NOT EXISTS idx_router_runs_thread ON router_runs(thread_id);
CREATE INDEX IF NOT EXISTS idx_router_feedback_run ON router_feedback(router_run_id);
CREATE INDEX IF NOT EXISTS idx_router_feedback_memory ON router_feedback(memory_id);
CREATE INDEX IF NOT EXISTS idx_keeper_jobs_thread ON keeper_jobs(thread_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_keeper_jobs_idempotency
    ON keeper_jobs(idempotency_key)
    WHERE idempotency_key != '';
CREATE INDEX IF NOT EXISTS idx_shadow_traces_thread ON shadow_traces(thread_id);
CREATE INDEX IF NOT EXISTS idx_shadow_trace_evals_trace ON shadow_trace_evals(shadow_trace_id);
