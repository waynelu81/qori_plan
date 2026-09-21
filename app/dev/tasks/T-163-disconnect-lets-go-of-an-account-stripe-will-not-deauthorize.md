---
id: T-163
title: Disconnect lets go of an account Stripe will not deauthorize
stream: selling
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-163 — Disconnect lets go of an account Stripe will not deauthorize

## Why

A creator whose Group holds an account Qori created on Accounts v2, before
`D-023`, cannot disconnect it. `PaymentsService::disconnect()` calls
`Connect::deauthorize()` first, Stripe answers "V2 Accounts cannot be
disconnected via this endpoint", the exception stops everything, and the id is
never cleared — the owner saw Disconnect fail twice on 21 September 2026
(`laravel.log`, 09:35 and 09:36). Afterwards Disconnect always lets go of the
id, and says the account itself is the creator's to close in Stripe.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

## Scope

**In:**

- Disconnect clears `connect_account_id` when Stripe refuses to deauthorize an
  account that is not an OAuth connection, and logs Stripe's code.

**Out:**

- Closing the account at Stripe: it is the creator's (`D-038`'s spirit — Qori
  removes only what it created, and the account is theirs).

## Files

| Path                                          | Change | Notes                          |
| --------------------------------------------- | ------ | ------------------------------ |
| `app/Services/PaymentsService.php`             | edit   | clear the id on a refusal      |
| `app/Integrations/Stripe/Connect.php`          | edit   | tell a v2 refusal from others  |
| `docs/flows/billing.md`                        | edit   | the disconnect path            |

## Database

None.

## Code

To be settled when ready.

## Copy

To be settled when ready: what the owner sees when the id is cleared and the
account stays open at Stripe.

## Routes

None.

## Tests

To be settled when ready.

## Acceptance

- [ ] Disconnect clears the id for an account Stripe will not deauthorize
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Which refusals clear the id and which stop: a v2 account's refusal clears
  it; a network failure or 5xx should probably still stop, so a creator is not
  told they disconnected when Stripe never heard. Anyone's, from the code.
- The line the owner reads. Owner's question, _asked_ 21 September 2026.

## Re-scope log

None.

## Notes

Found during `T-161`, 21 September 2026. The account (`acct_1UFnHLKUCxIWCyAo`,
email `rita@design-review.qori.test`) has since been purged from the sandbox
and the Group's id cleared by hand.
