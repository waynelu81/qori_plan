---
id: T-165
title: Integrations survives an account Stripe no longer knows
stream: selling
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-165 — Integrations survives an account Stripe no longer knows

## Why

A Group can hold an account id Stripe has stopped answering for: deleted in
the sandbox by `qori:stripe:purge-connected-accounts`, closed by its holder, or
removed from the platform without the `account.application.deauthorized`
event reaching Qori. Reading it answers 403 `account_invalid`, which
`Client::unwrap()` turns into `upstream_unavailable`, so Integrations renders
the 502 page — "A service Qori relies on isn't responding right now … This one
is on us" — and the owner can neither see the account nor disconnect it to
connect another. Walked on 22 September 2026 as Rita, on `harbour-lane-studio`,
whose `acct_1UF2SKKUCxNNHqBQ` the purge had deleted the day before (`T-164`'s
report). Afterwards the page says the account can no longer be reached and
offers Disconnect.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

## Scope

**In:**

- Integrations renders for a Group whose account Stripe no longer answers for,
  says so, and offers Disconnect.

**Out:**

- Clearing the id without the owner's click: a 403 can also be a key that
  stopped matching the platform, which would clear every creator's account.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Integrations/Stripe/Connect.php` | edit | tell `account_invalid` from other refusals |
| `app/Http/Controllers/Share/IntegrationsController.php` | edit | the state |
| `docs/flows/billing.md` | edit | the read |

## Database

None.

## Code

To be settled when ready.

## Copy

To be settled when ready.

## Routes

None.

## Tests

To be settled when ready.

## Acceptance

- [ ] Integrations renders for an account Stripe no longer knows, says so, and offers Disconnect
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Which answers mean "this account is gone" rather than "Stripe is down" or
  "our key is wrong": 403 `account_invalid` was observed; a 404 and a revoked
  OAuth grant have not been.
- Whether Disconnect for such an account skips the deauthorize call, which
  would refuse too (`T-163` meets the same shape for v2 accounts).
- What the design-review seeder writes, since `QORI_DESIGN_REVIEW_CONNECT_ACCOUNT`
  can name an account the purge has since deleted.

## Re-scope log

None.

## Notes

None.
