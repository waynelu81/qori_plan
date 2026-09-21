---
id: T-020
title: Rehearse a database restore and write down what happened
stream: operations
status: draft
owner: unassigned
estimate: M
depends: none
blocks: none
---

# T-020 — Rehearse a database restore and write down what happened

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

Neon has backups. Nobody has ever restored one, so what exists is a belief rather than a procedure. A restore first attempted during an incident is a restore attempted badly.

## Scope

**In:**

- Restoring a Neon backup to a scratch database, timing it, and writing the steps down.
- The same for R2 objects.
- Recording retention and the actual recovery point in `../operations-and-observability.md`.

**Out:**

- Automating restores.

## Before this can be ready

- Confirm what Neon's plan actually retains and for how long — the procedure depends on it and it should be read rather than assumed.

## Re-scope log

None.

## Notes

None.
