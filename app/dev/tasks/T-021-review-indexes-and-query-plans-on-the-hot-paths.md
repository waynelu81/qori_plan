---
id: T-021
title: Review indexes and query plans on the hot paths
stream: operations
status: draft
owner: unassigned
estimate: M
depends: none
blocks: none
---

# T-021 — Review indexes and query plans on the hot paths

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

The schema migration declares indexes that were reasoned about rather than measured. There is no data yet, so this is not urgent — but the two in-PHP aggregations deferred during the Postgres migration (`ProgressService::report` and the digest's counts) are the known candidates.

## Scope

**In:**

- `EXPLAIN` on the group, access, campaign recipient, session and activity-log paths, against seeded volume.
- Pushing the two in-PHP aggregations into the database if the plans justify it.

**Out:**

- Speculative optimisation. If a plan is fine, say so and stop.

## Before this can be ready

- Seed data at a realistic size first — a plan against an empty table says nothing. Decide what 'realistic' is: `decisions.md` estimates ~24M rows/year for the largest table.

## Re-scope log

None.

## Notes

None.
