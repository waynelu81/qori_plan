---
id: T-018
title: Choose and document the production queue topology
stream: operations
status: draft
owner: unassigned
estimate: M
depends: none
blocks: T-019
---

# T-018 — Choose and document the production queue topology

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

The queue is the `deferred` driver: work runs after the response, in the same process, and only when the response succeeded. It cannot retry, cannot be inspected, and loses everything on a crash. Nothing may be marked `ShouldQueue` until that changes — a rule currently held by nothing but a comment.

## Scope

**In:**

- A decision between `database` on Postgres and a hosted worker, with the reasoning.
- Whatever configuration and process supervision the decision implies.
- Failed-job visibility.

**Out:**

- Splitting campaigns into batches. That is what this unblocks, not what it is.

## Before this can be ready

- The decision itself. `decisions.md` already argues for `database` on Postgres as one fewer service than SQS or Valkey — confirm that and write it down, or argue otherwise.
- Note that deploying Laravel Cloud's managed queue silently sets `QUEUE_CONNECTION=cloud` for the environment regardless of configuration.

## Call sites waiting on this

> Added as they are found, so whoever lands the worker knows what to turn on.

- `ConnectionService::markForReconnect()` (`T-151`, 20 September 2026) sends
  `ConnectionNeedsReconnectNotification` synchronously from inside
  `AdvisoryLock`'s transaction, because nothing may be `ShouldQueue` yet. A
  Postmark call therefore happens inside a Postgres transaction holding a
  lock, and a send failure rolls the mark back, leaving the connection looking
  live until the next daily run. Bounded — `AdvisoryLock::WAIT_SECONDS` is 3 —
  and it goes away entirely when this task lands and that notification can be
  queued.

## Re-scope log

None.

## Notes

**18 September 2026 (`D-028`).** Deferred work dispatched from an artisan command does run: the framework flushes the deferred callbacks after the command finishes with exit code 0 (`vendor/laravel/framework/src/Illuminate/Foundation/Providers/FoundationServiceProvider.php:215-217`). `decisions.md`'s entry of 8 September 2026 and the comment in `config/queue.php` both say it never runs outside an HTTP response, and this task corrects both when it lands. What stays true is that a deferred callback cannot retry and is lost when the command exits non-zero, which is why nothing is `ShouldQueue`.

The `classroom` stream's two scheduled commands, `qori:sessions:notify` and `qori:recordings:find`, therefore send their mail inline rather than queueing it. Their per-run cap (`qori.live.sends_per_run`), the `session_notices` ledger and its retry state — `attempts`, `next_attempt_at`, `status` — are what stands in until this task lands, and a row left `failed` after `qori.live.notice_attempts` is what `T-019` alerts on.
