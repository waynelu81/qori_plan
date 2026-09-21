---
id: T-045
title: Campaigns are built, tested, and reachable from nowhere
stream: reachability
status: draft
owner: unassigned
estimate: M
depends: none
blocks: none
---

# T-045 — Campaigns are built, tested, and reachable from nowhere

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

`CampaignService` has `draft()`, `send()`, `unsubscribe()`, `allowance()` and
`sentThisMonth()`. There are `Campaign` and `CampaignRecipient` models, a
`CampaignNotification`, sixteen tests in `tests/Feature/Campaigns`, a working
`/unsubscribe/{peer}` route and an SES webhook for bounces.

**There is no controller and no page.** No route in the application mentions a
campaign. A creator cannot draft one, cannot send one, and cannot see the
monthly allowance the service calculates for them.

This is `PLAN.md`'s execution rule 1 in its purest form: "A tested service with
no reachable UI is not a finished feature — and the product has produced three
of those." This is the largest of them.

Found on 11 September 2026 while auditing the plan against what is built.
`qori:reachability` reports nothing here and cannot: it looks for routes with no
link, and a capability with no routes is invisible to it. Its own report said so
on 9 September.

## Scope

**In, provisionally:**

- One decision: finish the minimum way in, or hide it and record why.
- If finishing: drafting, sending, and the allowance a creator is held to.
- If hiding: a decision record, and whatever it takes to make the deferral
  honest rather than silent.

**Out:**

- SES and broadcast sending at scale. §9 treats that as its own decision and
  `release-prerequisites.md` still lists SES production access as outstanding.
- Building a template system. `PLAN.md` defers custom transactional templates.

## Before this can be ready

- **Decide first whether this ships at all before beta.** It is not in the
  north star loop, no beta gate mentions it, and the `delivery` stream is about
  transactional mail rather than marketing. Hiding it with a recorded reason is
  a legitimate and probably cheaper answer than finishing it, and this task
  should not be specified as a build before that question is put.
- **If it ships: decide what sending is blocked on.** `send()` is inline while
  the queue is `sync`, so a large list blocks the request. `T-018` owns the
  queue and nothing may be marked `ShouldQueue` before a worker exists. That
  makes the queue a real dependency rather than a nicety.
- **If it ships: decide the consent gate.** §9's sending caps and the
  suppression list both exist; `T-017` feeds suppressions from a real provider
  and is itself a draft. Sending marketing mail before bounces are handled is
  how a sending domain's reputation is spent.
- **If it is hidden: decide what "hidden" means for tested code.** Leaving
  sixteen passing tests against a capability nobody can reach is how this
  situation arose. The decision record has to say what happens to them.

## Re-scope log

None.

## Notes

Split out of `T-014` on 11 September 2026, which said "split it once the list
exists". The list exists now: `T-044`, `T-045` and `T-046` are it.
