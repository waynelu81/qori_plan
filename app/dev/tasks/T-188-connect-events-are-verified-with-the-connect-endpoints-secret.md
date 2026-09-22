---
id: T-188
title: Connect events are verified with the Connect endpoint's secret
stream: selling
status: draft
owner: unassigned
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

None yet.

## Preconditions

**Data this task verifies against:** a clean database.

**Equipment:** a Stripe sandbox with two webhook endpoints, one of them created
with `connect: true`, to confirm each delivery is refused under the other's
secret and accepted under its own.

## Scope

**In:**

- Accepting a delivery signed by either endpoint's secret, or separating the
  two endpoints, whichever **Before this can be ready** settles.
- The release checklist's live-mode step naming both endpoints and both secrets.

**Out:**

- What the Connect endpoint subscribes to beyond `checkout.session.completed`
  and `account.application.deauthorized`: refunds are `T-103`, delayed
  payments `T-102`.

## Files

| Path                                          | Change | Notes                                      |
| --------------------------------------------- | ------ | ------------------------------------------ |
| `config/services.php`                         | edit   | A second secret, or a list of them         |
| `app/Integrations/Stripe/Webhooks.php`        | edit   | Verification against the Connect secret    |
| `app/Http/Controllers/StripeWebhookController.php` | edit | Only if the endpoints are separated        |
| `.env.example`                                | edit   | The second key                             |
| `docs/flows/checkout.md`                      | edit   | Which endpoint carries which events        |

## Database

None.

## Code

To be settled when the draft is brought to ready.

## Copy

None.

## Routes

None, unless the endpoints are separated.

## Tests

To be written when the draft is brought to ready: a delivery signed with the
Connect secret is accepted, one signed with neither secret is refused.

## Acceptance

- [ ] A delivery signed with either endpoint's secret is accepted, and one
      signed with neither is refused
- [ ] `release-prerequisites.md` names both live endpoints and both secrets
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- One URL for both endpoints, trying each secret, or a URL each
  (`/webhooks/stripe` and `/webhooks/stripe/connect`)? Qori's existing controller
  already tells the two kinds apart by the event's `account` field.
- Read the live-mode endpoint set-up in `release-prerequisites.md` and name the
  events each endpoint subscribes to.

## Re-scope log

None.

## Notes

This blocks taking a live payment from a Peer, so it belongs before Stripe
activation, beside the other live-mode steps in `release-prerequisites.md`.
