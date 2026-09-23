---
id: T-200
title: A changed address keeps one Peer row per Group
stream: selling
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-200 — A changed address keeps one Peer row per Group

## Why

`AccessService::peerFor()` finds a Group's Peer row by email alone
(`app/Services/AccessService.php:188-190`), and `peers` is unique on
`(group_id, email)`, not on the person. `EmailChangeService::confirm()` swaps
the address on `users` and nowhere else (`:80-106`). So after a Peer changes
their address, the next access any Group gives them finds no row, creates a
second one for the same `user_id`, and counts them against the Group's Peer
limit again (`guardPeerLimit()`); the first row keeps their consent and
history, the second starts blank. Invitations match on the address the same
way (`Invitation::isFor()`, `app/Models/Invitation.php:115-118`). Found while
specifying `T-027`, 23 September 2026, from a read of the code; not
reproduced.

Afterwards a person is one Peer row per Group whatever address they use now,
and the creator's list shows the address they use now.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

## Scope

**In:**

- Finding a Group's Peer row for a signed-in person, and what an address
  change does to the rows that already exist.

**Out:**

- The address's case: `T-198`.

## Files

To be settled when ready.

## Database

To be settled when ready.

## Code

To be settled when ready.

## Copy

To be settled when ready.

## Routes

To be settled when ready.

## Tests

To be settled when ready.

## Acceptance

- [ ] A Peer who changes their address and is given another Series by the same Group is still one Peer row, counted once
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Look up by `user_id` first and by email second, or also rewrite
  `peers.email` when the address changes — anyone's; the first keeps the row a
  creator already knows, the second keeps the unique index meaningful.
- Whether the creator sees the old address, the new one, or both — the
  owner's, because the row is the creator's record of who they know
  (`D-049`'s consent sits on it).
- Two rows that already exist for one `user_id` in one Group: merge them, and
  whose consent wins — anyone's, with a query first to see if any exist.
- A waiting invitation to the old address after the change — `T-181`'s rules
  (`D-050`, `D-053`) say it is bound to the address; confirm that stands.

## Re-scope log

None.

## Notes

None.
