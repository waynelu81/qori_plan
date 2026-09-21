---
id: T-061
title: Stripe is sent the owner's email under the field it recognises
stream: selling
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-061 — Stripe is sent the owner's email under the field it recognises

## Why

The domain rename of 9 September 2026 (`f74757a`) rewrote every `contact` to
`peer`, and one of them was not Qori's word. Stripe's `contact_email`
parameter on `POST /v2/core/accounts` became `peer_email`, which Stripe refuses:

```
Stripe account creation failed: Some fields in the request were invalid: 'peer_email: Unknown field.'
```

No connected account has been created since. The local log holds twelve of
those refusals from the owner's own testing on 13 September, which is also why
the purchase attempted that day could not work: the seller Group never got an
account. `ConnectOnboardingTest` asserts the fields it cares about and the
email was not one of them, so the suite stayed green throughout.

Afterwards: creation sends `contact_email`, and a test fails if the key is ever
renamed again.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The one key in `Connect::createAccount()`.
- One test that pins it.

**Out:**

- Anything about _what_ the account is created with — country, entity type,
  capabilities. That is `T-062`.
- `docs/flows/checkout.md`: no wiring changes.

## Files

| Path                                               | Change | Notes        |
| -------------------------------------------------- | ------ | ------------ |
| `app/Integrations/Stripe/Connect.php`              | edit   | One key      |
| `tests/Feature/Checkout/ConnectOnboardingTest.php` | edit   | One new case |

## Database

None.

## Code

```php
// App\Integrations\Stripe\Connect::createAccount() — the payload key
'contact_email' => $group->owner?->email,
```

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/Checkout/ConnectOnboardingTest.php` — 1 new case**

1. `test_the_owner_email_travels_as_contact_email` — creation sends
   `contact_email` equal to the owner's address and no `peer_email` key.
   **Fails today.**

No existing case changes.

## Acceptance

- [x] `POST /v2/core/accounts` carries `contact_email` and no `peer_email`
- [x] A test fails if the key is renamed again
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

The rename was checked for other vendor casualties: `grep -rn "peer_"
app/Integrations` finds only this key. The `group_id` and `group_slug`
metadata keys in the same payload are Qori's own names and were meant to
change.
