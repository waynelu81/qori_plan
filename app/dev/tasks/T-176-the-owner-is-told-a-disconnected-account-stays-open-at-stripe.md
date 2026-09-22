---
id: T-176
title: The owner is told a disconnected account stays open at Stripe
stream: selling
status: done
owner: claude
estimate: S
depends: T-163
blocks: none
---

# T-176 — The owner is told a disconnected account stays open at Stripe

## Why

Since `T-163`, Disconnect lets go of an account Stripe will not deauthorize —
one Qori made on Accounts v2 before `D-023` — and the owner read the same
"Stripe is disconnected" as for any other. That account stays open at Stripe,
with anything in it. The owner, 22 September 2026, asked whether to say so:
"Yes please." Afterwards they are told.

## Decisions taken to make this specifiable

- **Said when Stripe refused, not when it let go**: `Connect::deauthorize()`
  answers whether Stripe let go.
- **Not for an account the last read found unreachable** (`T-165`): Stripe
  answers the same refusal for a deleted v2 account, and "stays open" would
  not be true of it.
- **The words**: "Stripe is disconnected from Qori, but the account itself
  stays open at Stripe." with "Anything in it is still there. Close it in
  Stripe if you no longer need it." The owner can change them.

## Preconditions

None.

**Data this task verifies against:** a clean database.

**Equipment:** None.

## Scope

**In:**

- The toast after Disconnect says the account stays open when Stripe refused.

**Out:**

- Closing the account for the owner: it is theirs (`D-038`'s spirit).

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Integrations/Contracts/SellsSeries.php` | edit | `deauthorize(): bool` |
| `app/Integrations/Stripe/Connect.php` | edit | answers whether Stripe let go |
| `app/Services/PaymentsService.php` | edit | `disconnect(): bool` — the account stays open |
| `app/Http/Controllers/Share/PaymentsController.php` | edit | the toast |
| `lang/en/payments.php` | edit | `disconnected_kept`, `disconnected_kept_how` |
| `docs/flows/billing.md` | edit | the disconnect path |
| `tests/Feature/Share/PaymentsOauthTest.php` | edit | one changed, one new case |

## Database

None.

## Code

`SellsSeries::deauthorize(string $accountId): bool` — true when the vendor let
go. `PaymentsService::disconnect(Group $group): bool` — true when the account
stays open at the vendor.

## Copy

| Key | File | English |
| --- | --- | --- |
| `disconnected_kept` | `lang/en/payments.php` | "Stripe is disconnected from Qori, but the account itself stays open at Stripe." |
| `disconnected_kept_how` | `lang/en/payments.php` | "Anything in it is still there. Close it in Stripe if you no longer need it." |

## Routes

None.

## Tests

**Changed: `tests/Feature/Share/PaymentsOauthTest.php`**

1. `test_disconnect_lets_go_when_stripe_will_not_deauthorize` — now expects the
   kept-open toast
2. `test_disconnecting_an_unreachable_account_says_only_that_it_is_disconnected` — new

## Acceptance

- [x] After Disconnect, an account Stripe would not deauthorize is said to stay open at Stripe
- [x] An account the last read found unreachable is only said to be disconnected
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

None.
