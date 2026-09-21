---
id: T-160
title: Open grants the Peer on the Drive file and sends them to Drive
stream: storage
status: draft
owner: unassigned
estimate: M
depends: T-159
blocks: T-161
---

# T-160 — Open grants the Peer on the Drive file and sends them to Drive

## Why

Step 14 of [the first-share journey](../journeys/first-share.md): a Peer who
paid presses Open on a Google Drive Episode and lands in Drive's viewer, able
to see that one file. `D-040` settled how — the grant is made at Open, for that
item, inside the Peer's request — and `PlaybackTicketService::open()` already
marks the line it goes on. This is `T-091`'s happy path cut out of it: reader
on the file for the Peer's Qori email, `sendNotificationEmail=false`, then the
file's view link. `T-091`'s open questions become this step's branches, not
its gate.

## Before this can be ready

- The grant's record: read `T-091`'s Database section and take the smallest
  part of it that lets `T-103`'s revoke find the permission later (`D-041`),
  so the branch builds on this rather than replacing it.
- A refused grant — `cannotInviteNonGoogleUser`, `notFound` — answers
  `VendorLink::blocked()` with the vendor's reason in Qori's words, and Open
  again retries (`D-040`). Fixtures: `tests/Fixtures/google/errors-permissions-create-*`.
- A Peer whose Google account is not their Qori email is `T-092`, not this.

## Re-scope log

None.

## Notes

None.
