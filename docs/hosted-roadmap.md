# Hosted Roadmap

The open-source kernel is local-first. Hosted features are valuable future
layers, but they are not required for the core memory contract.

This document keeps hosted and platform work visible without letting it define
the local kernel.

## Later Hosted Features

- hosted multi-user API server;
- hosted multi-user web UI;
- hosted identity, tenancy, RBAC, and team administration;
- hosted adapter registry and public badge publishing;
- hosted dashboards and managed alerting;
- provider invoice fetching and billing administration;
- remote MCP deployment patterns;
- managed schedulers for workers, restore drills, and rollout checks;
- hosted sync and collaboration;
- KMS-backed key storage, rotation, and managed off-host backups;
- managed export custody and retention enforcement;
- live provider certification using real provider accounts;
- production rollout programs across many external runtimes.

## Promotion Rule

A hosted feature can move into the main implementation plan only if it is
converted into a local, provider-neutral contract first.

For example:

- `backup/restore` is core because local SQLite reliability is required.
- `managed off-host backups with KMS` is later-hosted because it depends on a
  cloud custody model.
- `stdio MCP server` is an adapter/reference interface.
- `remote hosted MCP` is later-hosted because it depends on network, auth, and
  deployment policy.

## Non-Goals For Local v1

Local v1 should not require:

- a hosted account;
- a remote service;
- a vector database;
- a specific model provider;
- a specific agent runtime;
- team tenancy;
- live billing integration;
- cloud key management.

The local kernel should be installable, inspectable, testable, and useful on one
machine.

