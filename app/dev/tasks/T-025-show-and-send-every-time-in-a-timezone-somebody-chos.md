---
id: T-025
title: Show and send every time in a timezone somebody chose
stream: onboarding
status: draft
owner: unassigned
estimate: M
depends: T-024
blocks: none
---

# T-025 — Show and send every time in a timezone somebody chose

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

`T-024` stores a timezone and deliberately changes nothing. This is what consumes it. Every date in the interface is formatted by the browser today, so it is already the viewer's zone by accident; everything rendered server-side has no zone at all and comes out in `config('app.timezone')`, which is UTC. The two disagree the moment the same date appears in an email and on a page.

## Scope

**In:**

- Server-rendered dates — mail, certificates, PDFs — in the recipient's zone.
- A named zone beside any absolute time a person has to act on, so "9am" is never ambiguous.
- Scheduled sends interpreted in the Group's zone, per `communications-policy.md`.

**Out:**

- Per-Peer timezones. Still not wanted.
- Relative formatting ("3 days ago"), which needs no zone and already works.

## Before this can be ready

- Inventory every place a date reaches a person: Vue `toLocaleDateString` calls, notification bodies, the certificate, `ProgressService`'s stalled window. Guessing that list is how one of them stays in UTC.
- ~~Decide whether a Peer's dates follow _their_ zone or the Group's. The reading matters for an access email: the send time is the Group's business, the date shown inside it is the reader's.~~ **Answered 18 September 2026 (`D-028`):** a Peer's dates follow their own `users.timezone`, falling back to the Group's, with the zone named and the Group's zone beside it when the two differ; the mail rule is stated once, in `T-128`'s `App\Support\ZonedTime`, and every other task cites it rather than re-deciding.

## Re-scope log

None.

## Notes

**18 September 2026 (`D-028`).** The Scope line above, "Per-Peer timezones. Still not wanted", is superseded: a session notice renders every date in the recipient's own zone. The stream owner rewrites that line before this task is `ready`, so the Scope and the answered question agree. `T-005` still owns the rest of the access email's vocabulary.
