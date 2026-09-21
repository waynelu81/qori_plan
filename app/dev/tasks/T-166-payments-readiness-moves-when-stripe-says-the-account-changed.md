---
id: T-166
title: Payments readiness moves when Stripe says the account changed
stream: selling
status: draft
owner: unassigned
estimate: S
depends: T-164
blocks: none
---

# T-166 — Payments readiness moves when Stripe says the account changed

## Why

`T-164` remembers on `groups.payments_readiness` whether Stripe will take
payments for a Group's account, and the dashboard and the price field read it
there. It moves only when Qori reads the account — on Integrations, at the
connect landing, or when the local end-to-end run adopts one. So a creator who
finishes Stripe's steps keeps seeing "Stripe can't take payments for you yet"
on the dashboard until they open Integrations, and an account Stripe restricts
later is not noticed until then either. Stripe announces both with
`account.updated` on the Connect endpoint, which `StripeWebhookController`
acknowledges and ignores today (`docs/flows/billing.md`, "Not built yet").
Afterwards the event re-reads the account and the readiness moves on its own.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

## Scope

**In:**

- `account.updated` for a connected account re-reads it through
  `PaymentsService`, so its readiness moves.

**Out:**

- Telling the creator by email when payments stop: a product call for later.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Http/Controllers/StripeWebhookController.php` | edit | dispatch the event |
| `app/Services/PaymentsService.php` | edit | re-read the Groups holding the id |
| `docs/flows/billing.md` | edit | "Not built yet" |

## Database

None.

## Code

To be settled when ready.

## Copy

None.

## Routes

None.

## Tests

To be settled when ready.

## Acceptance

- [ ] `account.updated` moves the readiness of every Group holding that account
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Re-read the account, or read the event's own object: the event carries the
  v1 account, but trusting a body over a read is `T-114`'s open trust question.
- Whether the Connect endpoint is subscribed to `account.updated`: that is the
  platform's webhook configuration, a release checklist item, and local runs
  need `stripe listen` to forward it.
- How often Stripe sends it for one account, since each one would cost two
  Stripe calls.

## Re-scope log

None.

## Notes

None.
