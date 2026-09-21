---
id: T-019
title: Alert on the five failure modes that matter
stream: operations
status: draft
owner: unassigned
estimate: M
depends: T-018
blocks: none
---

# T-019 — Alert on the five failure modes that matter

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

Sentry receives `Log::error`, which means a failure is visible if somebody is looking. Nothing pages anyone. A payment that failed to become access is exactly the kind of thing that is quiet, expensive, and discovered by the customer.

**Sentry exists now.** Deployed to Laravel Cloud on 11 September 2026 and proved
with `php artisan sentry:test`. So the channel is no longer hypothetical and the
remaining work is entirely alert rules.

Two things to know before writing them:

- **Only 5xx reaches Sentry.** `bootstrap/app.php` filters on
  `AppException::shouldReport()`, which draws the line at status 500. A plan
  refusal, a 404 and a 403 are the error layer working and are deliberately
  silent. Any of the five conditions below that is _not_ naturally a 5xx needs
  something raised for it, rather than an alert rule that will never match.
- **`SENTRY_ENVIRONMENT` must be set per environment**, or a staging deploy
  files its noise into production's issue stream and the alert rules match both.

## Scope

**In:**

- Alerts on: payment/fulfilment mismatch, webhook failure, email bounce or complaint rate, queue age or failure, storage promotion failure.

**Out:**

- A metrics dashboard. Alerts are what wake somebody; a dashboard is what they open afterwards.

## Before this can be ready

- ~~Decide where an alert goes~~ **Decided 9 September 2026: Sentry.** Its app
  notifications and its email, both of which exist already — no new service and
  no new bill. Slack exists and is deliberately not a priority; a paging
  service manages a rotation there is nobody to rotate. This task is therefore
  about Sentry alert _rules_, not about choosing a channel: the work is naming
  the five conditions and making each one raise something Sentry can match on.
- Still to decide: whether "a payment that never became access" is detectable
  as an error at all, or needs a scheduled check over `payment_fulfilments`.
  The first is free and the second needs the scheduler, which needs `T-018`.
- `T-018` first: 'queue age' has no meaning until there is a queue that can age.

## Re-scope log

None.

## Notes

None.
