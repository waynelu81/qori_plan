---
id: T-188
title: Connect events are verified with the Connect endpoint's secret
stream: selling
status: doing
owner: claude
estimate: S
depends: none
blocks: none
---

# T-188 — Connect events are verified with the Connect endpoint's secret

## Why

Qori verifies every Stripe webhook with one secret, `STRIPE_WEBHOOK_SECRET`
(`config/services.php:29`), and its comment says "Connect events arrive on the
platform endpoint, so one secret covers every creator". In live mode they do
not. Events on a creator's connected account — the `checkout.session.completed`
that turns a Peer's payment into access — come to an endpoint created with
`connect: true`. Qori's own plan billing events come to a different endpoint,
and each endpoint signs with its own secret
([docs.stripe.com/connect/webhooks](https://docs.stripe.com/connect/webhooks),
[the `connect` parameter](https://docs.stripe.com/api/webhook_endpoints/create)).
Locally, `stripe listen --forward-connect-to` signs both streams with one secret,
which is why nothing has failed. No real connected-account event has reached the
app yet (`T-103`).

Afterwards both endpoints' events are verified, and a Peer's live payment
becomes access.

Found on 22 September 2026, while the payments half of the privacy policy and
terms was checked against the code.

## Decisions taken to make this specifiable

Brought to ready on 28 September 2026, from the code and Stripe's documents.

**A URL each: `POST /webhooks/stripe` for Qori's own account, `POST
/webhooks/stripe/connect` for connected accounts, each verified with its own
secret.** Not one URL trying both secrets: that accepts either stream under
either secret, so an endpoint subscribed to the wrong events, or pointed at
the wrong URL, would go on working and nobody would learn which secret signed
what. With a URL each, the secret that verifies is the endpoint's own, and the
route says which. Both routes reach the one `StripeWebhookController`, whose
dispatch by event type does not change; only the secret it checks against
does, `services.stripe.webhook_secret` or the new
`services.stripe.connect_webhook_secret` (`STRIPE_CONNECT_WEBHOOK_SECRET`).

**The check moves into the Stripe folder.** Stripe's signature scheme is vendor
code (CLAUDE.md, "Where code lives"), and `app/Integrations/Stripe/Webhooks.php`
already builds the same signature for `qori:e2e`. `Webhooks::verify()` sits
beside `signature()`, and the controller hands it the raw body, the header and
the secret. The rest of the controller's reading of Stripe's payload stays for
`T-114`.

**What each endpoint subscribes to.** Qori's own: `checkout.session.completed`
and `customer.subscription.created`, `.updated` and `.deleted`. The Connect
endpoint: `checkout.session.completed` and `account.application.deauthorized`.
`T-102`, `T-103` and `T-166` add theirs when they are built.

**Locally one secret signs both.** `stripe listen --forward-to …/webhooks/stripe
--forward-connect-to …/webhooks/stripe/connect` signs both streams with the one
secret it prints, so both keys take that value in `.env`; `qori:e2e` mints a
different one for each, so its run proves the two are kept apart.

## Preconditions

None.

**Data this task verifies against:** a clean database.

**Equipment:** none for the tests. The sandbox check — each delivery refused
under the other endpoint's secret — needs a second, `connect: true` endpoint in
the Stripe sandbox, the owner's to create; the tests sign both kinds of
delivery themselves.

## Scope

**In:**

- The Connect route and its secret, and the check in the Stripe folder.
- `qori:e2e` and `qori:e2e:checkout-paid` signing the Peer's payment with the
  Connect secret, to the Connect URL.
- The docs that name the webhook, and `release-prerequisites.md`'s live-mode
  step naming both endpoints, their events and their secrets.

**Out:**

- The rest of the payload reading: `T-114`.
- Creating the live endpoints and setting the secrets in Laravel Cloud: the
  owner's release checklist.
- Refunds, delayed payments and account changes: `T-103`, `T-102`, `T-166`.

## Files

| Path                                                                                 | Change | Notes                                                    |
| ------------------------------------------------------------------------------------ | ------ | -------------------------------------------------------- |
| `config/services.php`                                                                | edit   | `connect_webhook_secret`, and the comment put right      |
| `.env.example`                                                                       | edit   | `STRIPE_CONNECT_WEBHOOK_SECRET`                          |
| `routes/web.php`                                                                     | edit   | `webhooks.stripe.connect`                                |
| `app/Integrations/Stripe/Webhooks.php`                                               | edit   | `verify()`                                               |
| `app/Http/Controllers/StripeWebhookController.php`                                   | edit   | the route's secret, checked through `Webhooks::verify()` |
| `app/Console/Commands/EndToEndCommand.php`                                           | edit   | mints both secrets                                       |
| `app/Console/Commands/EndToEndCheckoutPaidCommand.php`                               | edit   | the Connect secret and URL                               |
| `tests/Feature/Checkout/StripeWebhookTest.php`                                       | edit   | 4 cases                                                  |
| `tests/Feature/Checkout/PaidFulfilmentTest.php`                                      | edit   | the Peer's payment to the Connect URL                    |
| `tests/Feature/Console/EndToEndCheckoutPaidCommandTest.php`                          | edit   | the same                                                 |
| `docs/flows/checkout.md` `docs/flows/billing.md`                                     | edit   | which endpoint carries which events                      |
| `docs/tinker/e2e.md` `docs/tinker/e2e-first-share.md` `docs/tinker/design-review.md` | edit   | `--forward-connect-to`, and the second key               |

## Database

None.

## Code

```php
// App\Integrations\Stripe\Webhooks
/** Stripe's scheme: a t= within five minutes, and a v1 HMAC over "t.body" that matches. */
public static function verify(string $body, string $header, #[\SensitiveParameter] string $secret, ?int $now = null): bool;
```

## Copy

None.

## Routes

| Verb | Path                      | Name                      | Action                    |
| ---- | ------------------------- | ------------------------- | ------------------------- |
| POST | `webhooks/stripe/connect` | `webhooks.stripe.connect` | `StripeWebhookController` |

Without `PreventRequestForgery`, as `webhooks.stripe` is.

## Tests

**Changed: `tests/Feature/Checkout/StripeWebhookTest.php` — 4 new cases**

1. `test_a_connected_accounts_payment_is_taken_on_the_connect_url` — signed
   with the Connect secret; access is granted.
2. `test_the_connect_url_refuses_the_platform_secret`.
3. `test_the_platform_url_refuses_the_connect_secret`.
4. `test_a_url_with_no_secret_set_refuses_everything`.

**Changed:** `PaidFulfilmentTest` and `EndToEndCheckoutPaidCommandTest` post a
Peer's payment to the Connect URL under the Connect secret.

## Acceptance

- [ ] Each endpoint's deliveries are accepted under its own secret and refused under the other's
- [ ] `release-prerequisites.md` names both live endpoints, their events and both secrets
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~One URL for both endpoints, trying each secret, or a URL each?~~
  **Answered 28 September 2026:** a URL each (Decisions).
- ~~Name the events each endpoint subscribes to.~~ **Answered 28 September
  2026** (Decisions).

## Re-scope log

None.

## Notes

This blocks taking a live payment from a Peer, so it belongs before Stripe
activation, beside the other live-mode steps in `release-prerequisites.md`.
