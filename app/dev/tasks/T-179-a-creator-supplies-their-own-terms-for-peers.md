---
id: T-179
title: A creator supplies their own terms for Peers
stream: onboarding
status: draft
owner: unassigned
estimate: M
depends: T-178
blocks: none
---

# T-179 — A creator supplies their own terms for Peers

## Why

`D-049` has every Peer agree to the terms for a Series before they get it, and
`T-178` shows Qori's own static agreement as those terms. The owner, 22
September 2026: "I think creator must create their own terms & agreement to
show on screen for their sale for their peer. might be one of the setup too,
or allow to set a template pick in each series." Afterwards a creator can
write their terms, or pick a template, and their Peers agree to those.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

## Scope

**In:**

- A creator's own terms, set once for the Group, and chosen per Series.

**Out:**

- Legal advice about what a creator's terms should say.

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

- [ ] A creator can set their own terms and a Series shows them instead of Qori's
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Where a creator writes them: a part of setup, Settings, or both — the owner
  named setup and a per-Series template pick.
- Templates: which ones Qori offers beside its own, and whether a creator can
  keep several and pick per Series.
- What a Peer who agreed to one version sees when the creator changes the
  terms: `T-178` records the version on the Access.
- Free text or a structured form, and how long terms can be.

## Re-scope log

None.

## Notes

None.
