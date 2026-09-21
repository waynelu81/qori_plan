---
id: T-114
title: Stripe's payloads and webhooks are read in the Stripe folder
stream: selling
status: draft
owner: unassigned
estimate: L
depends: T-113
blocks: none
---

# T-114 — Stripe's payloads and webhooks are read in the Stripe folder

## Why

`D-022` puts everything Qori writes for a vendor in that vendor's folder, and
`T-112` and `T-113` moved Stripe's client and onboarding there. The rest of
what knows how Stripe works is still outside `app/Integrations/Stripe`:

- `ConnectAccount::fromStripe()`, `HostedCheckout::fromStripe()` and
  `GroupSubscription::fromStripe()` in `app/Data`, and `StripePeriod` in
  `app/Support`.
- `StripeWebhookController` computes Stripe's signature itself and reads event
  types, `mode`, `payment_status` and metadata.
- `BillingService::applySubscription()` takes Stripe's raw subscription array
  and its status words; `Group::isSubscribed()` compares them.
- `StripePurgeConnectedAccountsCommand` builds its own Stripe clients instead of
  `App\Integrations\Stripe\Client`.
- `App\Rules\StatementDescriptorSuffix` encodes Stripe's descriptor limits.
- A connection failure on any Stripe call other than the OAuth token exchange
  (`deauthorize()`, `account()`, `checkoutFor()`, `Subscription`) renders a raw
  500 rather than `upstream_unavailable` (`T-113` report).

The owner also asked, on 17 September 2026, for the direct charge in `Connect`
to become `beginDirectCharge()`, `finaliseDirectCharge()` and
`declineDirectCharge()`, as onboarding did in `T-113`. That refactor rewrites
the same webhook and fulfilment code, so it belongs here rather than beside
it.

## Decisions taken to make this specifiable

To be written once the questions below are answered.

## Preconditions

To be written.

## Scope

**In:**

- To be written.

**Out:**

- To be written.

## Files

To be written.

## Database

To be written.

## Code

To be written.

## Copy

To be written.

## Routes

To be written.

## Tests

To be written.

## Acceptance

- [ ] To be written
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- The owner's answer on the checkout trust gap found on 17 September 2026: a
  connected account can open its own Checkout Session whose metadata names
  another Group's Series, and the webhook grants it. Which fix — only
  checkouts Qori recorded at begin, comparing account and amount, or re-reading
  the session — decides what `finaliseDirectCharge()` takes and returns, and
  how it meets `T-102`'s pending row. Owner's question.
- The owner's answer on Stripe's two webhook scopes: platform events and
  connected-account events arrive on separate endpoints with separate signing
  secrets, and Qori checks one. Two secrets on one URL, or a second route.
  Owner's question.
- What `declineDirectCharge()` does at Stripe: close an open Checkout Session
  when the buyer cancels, or nothing. Owner's question.
- Whether this splits into a payload-and-signature move and the direct-charge
  refactor. Anyone's, once the answers above are in.

## Re-scope log

None.

## Notes

None.
