---
id: T-163
title: Disconnect lets go of an account Stripe will not deauthorize
stream: selling
status: done
owner: claude
estimate: S
depends: none
blocks: T-165
---

# T-163 — Disconnect lets go of an account Stripe will not deauthorize

## Why

A creator whose Group holds an account Qori created on Accounts v2, before
`D-023`, could not disconnect it. `PaymentsService::disconnect()` called
`Connect::deauthorize()` first, Stripe answered "V2 Accounts cannot be
disconnected via this endpoint", the exception stopped everything, and the id
was never cleared — the owner saw Disconnect fail twice on 21 September 2026
(`laravel.log`, 09:35 and 09:36). Afterwards Disconnect lets go of the id
whenever Stripe answers, and stops only when Stripe could not be asked.

## Decisions taken to make this specifiable

- **A 4xx lets go; no answer or a 5xx stops.** A 4xx is Stripe saying it never
  will: 400 `v2_account_disconnection_unsupported` for an account made on
  Accounts v2 (observed 22 September 2026 for both such accounts on the
  platform), and the same or another refusal for one that is gone or no longer
  connected. The creator asked Qori to let go, so the refusal is logged at
  warning with Stripe's code and the id is cleared. No answer (which used to
  surface as a raw 500) or a 5xx throws `upstream_unavailable` and leaves the
  id, so nobody is told they disconnected when Stripe never heard.
- **The owner reads the same line either way**: "Stripe is disconnected.
  Connect again whenever you're ready." It is true from Qori's side for every
  account. A line saying the account itself stays open at Stripe is the
  owner's to write and stays asked (21 September 2026).

## Preconditions

None.

**Data this task verifies against:** a clean database for the tests; the
design-review world's `harbour-lane-studio`, whose account is a deleted v2
one, for the walk.

**Equipment:** a browser; Stripe test mode for the observed answers.

## Scope

**In:**

- `Connect::deauthorize()` tells a refusal from Stripe not hearing, and lets go
  on a refusal.

**Out:**

- Closing the account at Stripe: it is the creator's (`D-038`'s spirit — Qori
  removes only what it created, and the account is theirs).

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Integrations/Stripe/Connect.php` | edit | `deauthorize()` |
| `app/Integrations/Contracts/SellsSeries.php` | edit | what `deauthorize()` promises |
| `app/Services/PaymentsService.php` | edit | `disconnect()`'s account of it |
| `docs/flows/billing.md` | edit | the disconnect path |
| `tests/Feature/Share/PaymentsOauthTest.php` | edit | two cases |
| `tests/Fixtures/stripe/errors-oauth-deauthorize-400-v2_account_disconnection_unsupported.json`, `tests/Fixtures/stripe/README.md` | new, edit | the observed refusal |

## Database

None.

## Code

`SellsSeries::deauthorize(string $accountId): void` keeps its signature:
it returns when Stripe let go or refused with a 4xx, and throws
`upstream_unavailable` on no answer or a 5xx.

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/Share/PaymentsOauthTest.php` — 2 new cases**

1. `test_disconnect_lets_go_when_stripe_will_not_deauthorize`
2. `test_disconnect_stops_when_stripe_cannot_be_asked` — no answer, then a 500

## Acceptance

- [x] Disconnect clears the id for an account Stripe will not deauthorize
- [x] Disconnect keeps the id when Stripe could not be asked
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Built with `T-165` on 22 September 2026: an account Stripe no longer answers
for is shown with Disconnect on offer, and this is what makes that Disconnect
work.
