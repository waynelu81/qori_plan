---
id: T-014
title: Finish or explicitly hide each unreachable capability
stream: reachability
status: draft
owner: unassigned
estimate: L
depends: T-012
blocks: none
---

# T-014 — Finish or explicitly hide each unreachable capability

> **Draft, and now an index rather than a task.** The list it was waiting for
> exists, and the work has been split into `T-044`, `T-045` and `T-046`. Close
> this when those three are done rather than starting it.

## Why

Written as a placeholder for "there are probably others; `T-012` is what
produces the list". `T-012` ran on 9 September 2026 and reported nothing, which
was correct and not reassuring: it looks for **routes with no link**, and a
capability with no routes at all is invisible to it. Its own report said so.

The list was produced by hand on 11 September 2026, by walking every model and
service against the controllers and pages that reach them.

| Capability            | Built                                                                                            | Reached by                            | Task    |
| --------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------- | ------- |
| Connections           | Table with encrypted tokens, `DropboxStorage`, `VimeoVideos`, `PlaybackTicketService` reads them | **Nothing**                           | `T-044` |
| Campaigns             | `CampaignService`, two models, a notification, 16 tests, an unsubscribe route, an SES webhook    | **Nothing**                           | `T-045` |
| Collaborators         | Model, role enum, seat caps priced at 1 free and 20 paid, admin console counts them              | Group creation only                   | `T-046` |
| `payment_fulfilments` | Written on every checkout outcome                                                                | **Nothing**                           | `T-013` |
| `EmailSuppression`    | Table and `SuppressionService`                                                                   | **Nothing** feeds it                  | `T-017` |
| Connect onboarding    | Was the original example here                                                                    | The Payments page, since the redesign | —       |

Two of the six already had tasks. Three did not. The sixth turned out to be
fixed.

`T-044` moved to the `storage` stream on 16 September 2026 (`D-016`), which
grew around it; it still closes the Connections row here.

## Scope

**In:**

- Nothing directly. Each row above is owned by the task named beside it.

**Out:**

- Everything. This file exists so the inventory has one home and so the next
  person does not redo the walk.

## Before this can be ready

Nothing, and it should not become ready. It is an index. Close it when `T-044`,
`T-045` and `T-046` are done, or delete it and keep the table somewhere that is
not a task.

## Re-scope log

None.

## Notes

**The estimate was right and the shape was wrong.** "L" was recorded because
this was really one task per finding, and the file said to split it once the
list existed. That is what happened. The reason it sat for two days is that the
list was expected to come from a command, and the command cannot see this class
of finding.
