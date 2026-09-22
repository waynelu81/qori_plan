---
id: T-185
title: A Peer stays signed in between visits
stream: identity
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-185 — A Peer stays signed in between visits

## Why

A code from the Series page and a magic link both sign a person in with
`Auth::login($user)`, not remembered, and the session ends after
`SESSION_LIFETIME` minutes idle: 120 in `.env.example`. So a Peer who comes
back the next day asks for a new code, which is one more step on every visit
and one more Postmark email. It is the largest line in the email-cost estimate
of 22 September 2026, larger than invitations. The spec gives sessions 90 days
idle (`project-plan.md` §14's table: "90 days idle; max 2 concurrent").
Afterwards a Peer who signed in on a device is still signed in when they come
back to it.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

## Scope

**In:**

- How long a sign-in by code or magic link lasts on the device it was made on.

**Out:**

- The session registry and its cap, designed in
  `docs/architecture/sessions.md` and not built.

## Files

To be settled when ready.

## Database

To be settled when ready.

## Code

To be settled when ready.

## Copy

None expected.

## Routes

None.

## Tests

To be settled when ready.

## Acceptance

- [ ] A Peer who signed in with a code is still signed in on that device the next week
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- What production sets `SESSION_LIFETIME` to: the owner's, from Laravel
  Cloud. If it is already long, this task is smaller than it looks.
- How: a longer session lifetime, where sessions live in Valkey and a revoked
  one is destroyed with no cookie left to bring it back; or remember-me,
  which `docs/architecture/sessions.md` calls a hole until the registry
  treats a remembered sign-in as a new one.
- Whether creators get the same. A password or a passkey sends no email, so
  it is the Peers' codes that cost.
- What 90 days of sessions costs in Valkey's memory.

## Re-scope log

None.

## Notes

Found while estimating Qori's email costs for the owner, 22 September 2026.
