---
id: T-199
title: An account made with a code can set a password and leave
stream: identity
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-199 — An account made with a code can set a password and leave

## Why

The Series page's code step makes a Peer's account with `Str::password(32)`,
a password nobody knows (`app/Http/Controllers/SeriesAccessController.php:77`,
`T-073`), and `docs/flows/auth.md` says choosing one later is the security
page's job. That page sits behind `RequirePassword`
(`routes/settings.php:86-90`), setting a password asks for the current one
(`PasswordUpdateRequest.php:21`), and so does deleting the account
(`ProfileDeleteRequest.php:21`). A Peer who came in by code can do neither
except by finding "Forgot password" first, which nothing on those pages
points to — and which fails outright for an address stored with capitals
(`T-198`). Found while specifying `T-027`, 23 September 2026, from a read of
the code; not walked in a browser.

Afterwards a person with no password of their own can set one and can delete
their account, proving who they are some other way than a password they were
never given.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

## Scope

**In:**

- Setting a first password, and deleting the account, for a person who never
  chose one.

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

- [ ] A Peer who came in by code sets a password and deletes their account without using "Forgot password"
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- How Qori knows a person never chose a password: a nullable
  `password_set_at`, or a `password` column that may be null — anyone's; the
  second touches every `Hash::check` path.
- What proves identity in place of the password for those two actions: a code
  to the address (`LoginCodeService`, as the Series page uses), or a fresh
  magic-link sign-in — anyone's, reusing what exists.
- Whether the security page offers passkeys and two-factor to a person with
  no password, or only after they set one — anyone's in the identity stream.
- Deleting an account is the person's to do whatever the policy wording says;
  the place is built here, and the words are release checklist (`D-043`).

## Re-scope log

None.

## Notes

None.
