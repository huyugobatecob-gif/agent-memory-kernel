# Backlog Cutover

This backlog cutover applies the Kernel Charter to the implementation plan. New
work should be classified as `core`, `extension`, or `later-hosted` before it
is added to the roadmap.

## Labels

### `core`

Core work is required for the local memory kernel to be trustworthy and
portable. It must not depend on a specific runtime, hosted service, provider,
or domain.

Core examples:

- source events, candidates, active memories, and evidence;
- generic scope/lane/namespace policy isolation;
- review lifecycle and lifecycle mutations;
- Keeper and Router contracts;
- prompt envelope contract;
- deterministic retrieval and selection explanations;
- correction, delete, distrust, expire, supersede, rollback;
- derived-memory invalidation;
- provenance-preserving import/export;
- audit reports and why-memory-exists views;
- conformance scenarios and invariant tests.

### `extension`

Extension work adds optional capabilities without becoming a dependency of the
kernel.

Extension examples:

- Hermes, Codex, chat-agent, or coding-agent adapters;
- starter personal/professional templates;
- SEO, research, CRM, support, or QA memory packs;
- Memory Tree and other prompt renderers over the prompt envelope contract;
- outcome loop recipes;
- importer/exporter bridges for notes, documents, chats, task tools, and vaults;
- optional embeddings, ANN search, semantic rerank providers, and provider
  formatters;
- richer local review UI, graph browser, and conflict-review workflows;
- local notification payload builders and external sender bridges.

### `later-hosted`

Hosted work belongs to a future product or deployment layer. It can be
documented as future direction, but it is not needed for the open-source local
kernel.

Later-hosted examples:

- hosted multi-user API and hosted web UI;
- identity, tenancy, RBAC, and team administration;
- hosted dashboards, billing dashboards, and provider invoice fetchers;
- remote MCP hosting;
- managed alerts, schedulers, and rollout orchestration;
- KMS, managed off-host backup, and cloud custody;
- hosted adapter registry and hosted certification publishing;
- hosted sync and collaboration.

## Current Cutover

| Item | Classification | Why |
| --- | --- | --- |
| SQLite source of truth | core | Reference local store. |
| Raw source events and turns | core | Required provenance base. |
| Candidate and active memories | core | Required memory lifecycle. |
| Generic scope/lane/namespace policy model | core | Required isolation primitive. |
| Personal/professional starter templates | extension | Useful public defaults over the generic model. |
| Project/agent/session lanes | extension | Useful optional policy scopes. |
| Graph nodes, edges, evidence | core | Required tree and provenance model. |
| Advanced graph split/semantic compaction | extension | Optimization after evidence rules are stable. |
| Keeper extraction contract | core | Required post-turn memory write path. |
| LLM/provider-specific Keeper prompts | extension | Optional implementation of the contract. |
| Router retrieval contract | core | Required pre-turn memory read path. |
| ANN/vector retrieval | extension | Optional acceleration, not source of truth. |
| Prompt envelope read contract | core | Required agent boundary. |
| Memory Tree renderer | extension | Default renderer over selected memory, not the kernel ontology. |
| Provider prompt formatters | extension | Helpful adapter surface. |
| Review lifecycle | core | Trust boundary. |
| Browser review UI | extension | Human surface over core lifecycle. |
| Read/write/export/inject policies | core | Safety boundary. |
| Hosted identity, tenancy, RBAC | later-hosted | Hosted/team layer. |
| Capability and local delegation reports | core | Local policy explainability. |
| Billing reconciliation and invoice ingestion | extension | Operational integration, not memory truth. |
| Hosted billing dashboards | later-hosted | Hosted product surface. |
| Notification queue and payload builders | extension | Local/operator workflow. |
| Live email/push/webhook sending | extension | External sender integration. |
| Managed alerting | later-hosted | Hosted operations. |
| Backup/restore/migration checks | core | Local reliability. |
| KMS/off-host managed backup | later-hosted | Hosted/cloud custody. |
| Export redaction, approval, retention | core | Memory portability and privacy. |
| Hosted export custody | later-hosted | Deployment-specific governance. |
| Runtime hooks | core | Kernel must expose before/after contracts. |
| Hermes adapter | extension | Optional runtime example. |
| Hermes rollout | extension | Adapter-specific deployment. |
| SEO loop memory | extension | Domain pack over outcomes. |
| Outcome records | extension | Generic iterative-work pack. |
| Production rollout into all live runtimes | later-hosted | Deployment program, not kernel requirement. |
| Conformance golden traces | core | Proof of portability. |
| Hosted badge or registry publication | later-hosted | Ecosystem service. |

## Rules For Future Backlog Items

1. If the item changes memory truth, lifecycle, policy, retrieval, prompt
   boundary, import/export, or conformance, it is probably `core`.
2. If the item connects the kernel to a specific runtime, tool, domain, provider,
   or UI workflow, it is probably `extension`.
3. If the item requires multi-user hosting, managed infrastructure, cloud keys,
   public service deployment, billing operations, or tenant administration, it is
   `later-hosted`.
4. `extension` work may not weaken or bypass `core` invariants.
5. `later-hosted` work may not be listed as a blocker for local full-memory
   completion.
