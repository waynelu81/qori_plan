---
id: T-013
title: Failed fulfilments in the admin console
stream: reachability
status: draft
owner: unassigned
estimate: M
depends: none
blocks: none
---

# T-013 — Failed fulfilments in the admin console

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

`payment_fulfilments` records every paid checkout Qori is told about, including the ones that failed to become access. Nothing reads the table. PLAN.md calls it 'the queue, queryable as status = failed, oldest first' — and there is no way to run that query without a shell.

## Scope

**In:**

- An admin console page listing failed fulfilments, oldest first.
- Enough context per row to act: session id, amount, Group, and the recorded reason.

**Out:**

- Retrying a fulfilment from the console. The console is read-only by design (§24); writes arrive later through impersonation.

## Before this can be ready

- Confirm what a staff member is meant to _do_ with a failed row, since they cannot retry it from here. If the answer is 'email the creator', this page needs to say so; if it is 'run a command', the command has to exist first and is a separate task.

## Re-scope log

None.

## Notes

None.
