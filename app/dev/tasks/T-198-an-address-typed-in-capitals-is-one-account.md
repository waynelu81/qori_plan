---
id: T-198
title: An address typed in capitals is one account
stream: identity
status: draft
owner: unassigned
estimate: S
depends: T-027
blocks: none
---

# T-198 — An address typed in capitals is one account

## Why

Every Fortify path lowercases the address before it reads or writes one
(`config/fortify.php` `lowercase_usernames`: registration, password sign-in,
the reset link), and `EmailChangeService::request()` does the same. The Series
page's code step does not: `SeriesAccessController::start()` finds an account
whatever its case but creates a new one with the address as typed
(`app/Http/Controllers/SeriesAccessController.php:62` and `:74-78`). An account
made as `Sam@Example.test` then cannot be reached as `sam@example.test` by the
magic link (`MagicLinkLoginController.php:52`, an exact `where`) or by a
password reset (Fortify lowercases the input, the lookup is exact), and
`users.email`'s unique index is exact, so registering the lowercase address
makes a second account for the same inbox. Found while specifying `T-027`, 23
September 2026, from a read of the code; not reproduced in a browser.

Afterwards the code step stores the address lowercased, the magic link finds
an account whatever its case, and the accounts already stored in capitals are
brought into line.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

## Scope

**In:**

- The code step's new account, the magic link's lookup, and the rows already
  stored with capitals.

**Out:**

- Setting a password on an account the code step made: `T-199`.

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

- [ ] An account made from the Series page with capitals in its address signs in by magic link and resets its password with the address typed in lowercase
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- How many rows hold capitals in production and development, and whether any
  two differ only by case — a query, before the migration's shape is chosen,
  because lowercasing one of a pair would break the unique index.
- A pair that differs only by case: merge, rename one, or refuse and report —
  the owner's, if any exist.
- Whether the unique index becomes one on `lower(email)`, so a mixed-case row
  can never be written again whatever path writes it — anyone's.
- `T-027` edits `SeriesAccessController.php` first; this task follows it.

## Re-scope log

None.

## Notes

None.
