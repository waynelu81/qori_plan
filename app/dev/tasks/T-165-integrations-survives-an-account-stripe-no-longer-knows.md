---
id: T-165
title: Integrations survives an account Stripe no longer knows
stream: selling
status: done
owner: claude
estimate: S
depends: T-163
blocks: none
---

# T-165 — Integrations survives an account Stripe no longer knows

## Why

A Group can hold an account id Stripe has stopped answering for: deleted in
the sandbox by `qori:stripe:purge-connected-accounts`, closed by its holder, or
removed from the platform without the `account.application.deauthorized`
event reaching Qori. Reading it answers 403 `account_invalid`, which
`Client::unwrap()` turned into `upstream_unavailable`, so Integrations rendered
the 502 page — "A service Qori relies on isn't responding right now … This one
is on us" — and the owner could neither see the account nor disconnect it.
Walked on 22 September 2026 as Rita, on `harbour-lane-studio`, whose
`acct_1UF2SKKUCxNNHqBQ` the purge deleted the day before (`T-164`'s report).
Afterwards the page says Qori can no longer reach the account and offers
Disconnect.

## Decisions taken to make this specifiable

- **403 `account_invalid` is "gone", and nothing else is.** Observed on 16, 21
  and 22 September 2026: "does not have access to account … (or that account
  does not exist). Application access may have been revoked." — the same
  answer for a deleted account and a revoked grant. A key that is wrong for
  the platform answers 401 and stays the 502 page, because it is Qori's fault
  and every Group's.
- **It is a readiness, `unreachable`, not an error.** The account read answers
  `ConnectAccountReader::unreachable()`, so the page, the remembered readiness
  and the dashboard's warning all follow `T-164`'s path: it asks the creator,
  it has no step at Stripe, and the way out is the Disconnect button already
  on the page. The general "Open your Stripe dashboard" link is not shown for
  it, and nor is the owner note, which is about steps.
- **Nothing is cleared without the owner's click**: the same 403 would answer
  for every Group if the platform lost access wholesale.
- **The design-review seeder needs nothing**: a deleted account it writes back
  now shows as unreachable and disconnects.

## Preconditions

None.

**Data this task verifies against:** a clean database for the tests;
`harbour-lane-studio` for the walk, its id put back after.

**Equipment:** a browser; Stripe test mode for the observed answer.

## Scope

**In:**

- Integrations renders for an account Stripe no longer answers for, says so,
  and offers Disconnect.

**Out:**

- Clearing the id without the owner's click, above.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Integrations/Stripe/Connect.php` | edit | `account()` tells `account_invalid` apart |
| `app/Integrations/Stripe/ConnectAccountReader.php` | edit | `unreachable()` |
| `app/Enums/PaymentsReadiness.php` | edit | `Unreachable` |
| `lang/en/payments.php` | edit | `readiness.unreachable` |
| `app/Support/PaymentsReadinessCopy.php` | edit | the owner note only beside steps |
| `app/Http/Controllers/Share/IntegrationsController.php` | edit | no dashboard link for it |
| `resources/js/pages/share/settings/Integrations.vue` | edit | the status |
| `docs/flows/billing.md` | edit | the read |
| `tests/Feature/Share/PaymentsReadinessTest.php` | edit | one case |
| `tests/Unit/Integrations/Stripe/ConnectAccountReaderTest.php` | edit | one case |
| `tests/Fixtures/stripe/errors-account-403-account_invalid.json` | new | the observed answer |

**Added during execution** (the owner, 22 September 2026, on this page:
warnings and errors "just look similar to all the rest of text"):

| Path | Change | Notes |
| --- | --- | --- |
| `resources/js/components/share/PaymentsReadiness.vue` | edit | the headline is an `InlineNotice` in the readiness's tone |

## Database

None: `payments_readiness` is a string column, and `unreachable` is a new
value of the same enum.

## Code

```php
// ConnectAccountReader
public static function unreachable(string $accountId): ConnectAccount;

// PaymentsReadiness
case Unreachable = 'unreachable'; // asksTheCreator(): true
```

## Copy

| Key | File | English |
| --- | --- | --- |
| `readiness.unreachable.badge` | `lang/en/payments.php` | "Can't be reached" |
| `readiness.unreachable.headline` | `lang/en/payments.php` | "Qori can no longer reach this Stripe account." |
| `readiness.unreachable.body` | `lang/en/payments.php` | "It may have been closed, or Qori removed from it in Stripe. Disconnect it here, then connect the account you use now." |

## Routes

None.

## Tests

**Changed: 2 new cases**

1. `tests/Feature/Share/PaymentsReadinessTest.php` —
   `test_an_account_stripe_no_longer_answers_for_can_still_be_disconnected`
2. `tests/Unit/Integrations/Stripe/ConnectAccountReaderTest.php` —
   `test_an_account_stripe_no_longer_answers_for_is_unreachable`

## Acceptance

- [x] Integrations renders for an account Stripe no longer knows, says so, and offers Disconnect
- [x] A readiness that is not ready is shown in the brand's semantic colour
      with its icon — warning with steps to take, destructive for refused or
      unreachable, neutral while Stripe checks — and the badge agrees
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Built with `T-163`, which makes the Disconnect it offers work for such an
account: every account on the platform that Stripe no longer answers for was
made on Accounts v2, whose deauthorize answers 400.

The colours are `qori-brand-guidelines.md`'s semantic tokens — Warning
`#8A5A10`, Destructive `#B42318` — through `InlineNotice`, whose icons keep
colour from being the only signal. `PaymentsReadinessCopy` sends the tone, so
the badge and the notice cannot disagree.
