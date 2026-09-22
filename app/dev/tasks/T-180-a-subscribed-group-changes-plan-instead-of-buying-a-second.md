---
id: T-180
title: A subscribed Group changes plan instead of buying a second one
stream: selling
status: draft
owner: unassigned
estimate: M
depends: none
blocks: none
---

# T-180 — A subscribed Group changes plan instead of buying a second one

## Why

A Group already paying for Start that clicks "Switch to Pro" on the billing
page is sent to a new Stripe Checkout, which creates a **second**
subscription. Nothing refuses it: `BillingController::subscribe()`,
`BillingService::subscribe()` and `Subscription::subscribeUrl()` never look
for the one the Group already has. The owner would pay for both plans, and
the webhook sets the plan from whichever event lands last.

Since `D-048` it is worse. A subscription is in one currency, and Stripe
refuses a second currency on the same customer: "You cannot combine
currencies on a single customer. This customer has an active subscription …
with currency eur" (`T-170`'s sandbox check, 22 September 2026). A Group
paying in EUR that picks USD in the currency menu before switching plan meets
a failed checkout.

Afterwards, a subscribed Group changes plan on the subscription it already
has, in the currency it already pays in.

## Decisions taken to make this specifiable

- **The owner's answers (`D-052`): an upgrade follows Claude's billing.** It
  takes effect at once, charges one full period of the new plan less the old
  plan's unused part, prorated to the second, and restarts the cycle. A
  downgrade takes effect at the end of the period already paid for, with no
  refund or credit. The change stays in the subscription's own currency.
- **Qori makes the change through Stripe's API, not the Customer Portal.** The
  API controls each part of Claude's shape exactly: the proration, the cycle
  restarting, and the change applying only once it is paid. It also keeps the
  owner on Qori's billing page, where the amount is shown before they
  confirm.
  - An upgrade updates the subscription's item with
    `proration_behavior=always_invoice`, `billing_cycle_anchor=now` and
    `payment_behavior=pending_if_incomplete`, and moves `metadata[plan]` with
    it, since `applySubscription()` reads the plan from there.
  - A downgrade is a subscription schedule whose next phase, at the current
    period's end, has the cheaper price and its `metadata[plan]`.
- **The owner sees what an upgrade will charge before confirming**, from
  Stripe's invoice preview for that change, so the figure is Stripe's own.
- **Qori keeps the subscription's id**: the webhook writes it on the Group,
  so a change never has to guess which subscription is the Group's.

## Preconditions

The Stripe sandbox with Start and Pro published by `T-172`.

## Scope

**In:**

- A subscribed Group's plan change moves its existing subscription to the new
  price, and never opens a second one.
- The currency of the change is the subscription's own, whatever the menu
  says.

**Out:**

- Moving every subscriber onto a new price after a price change (`D-048`: a
  separate decision).

## Files

To be settled when ready. Likely `app/Services/BillingService.php`,
`app/Integrations/Contracts/BillsGroups.php`,
`app/Integrations/Stripe/Subscription.php`,
`app/Http/Controllers/Share/BillingController.php`,
`resources/js/pages/share/Billing.vue`, `docs/flows/billing.md`.

## Database

To be settled when ready. Qori stores `stripe_customer_id` on the Group; it
may need the subscription's id and currency too.

## Code

To be settled when ready.

## Copy

To be settled when ready.

## Routes

To be settled when ready.

## Tests

To be settled when ready.

## Acceptance

- [ ] A subscribed Group that switches plan has one subscription afterwards, on the new plan, in its own currency
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~**How the change happens**~~ — decided 22 September 2026: through
  Stripe's API (Decisions).
- ~~**What the owner is charged at the moment of the change**~~ — answered 22
  September 2026 (`D-052`): Claude's shape, a full period of the new plan less
  the old plan's unused part, at once.
- ~~**Downgrades**~~ — answered 22 September 2026 (`D-052`): at the end of the
  period paid for. Read from Claude's documented cancellation, since its help
  pages do not cover a downgrade; the owner may correct it.
- The copy: the upgrade's confirm line with the amount, and the downgrade's
  "you keep Pro until …" line. Anyone's.
- Whether the billing page says, beside the currency menu, that a subscribed
  Group stays in the currency it pays in. Anyone's.
- A spike: an upgrade and a downgrade on a sandbox subscription, including one
  in a fixed currency. Keep the updated subscription and the schedule as
  fixtures. Anyone's.

## Re-scope log

None.

## Notes

- Found during `T-170`, 22 September 2026. The refusal was observed in the
  sandbox; the second subscription was read from the code, not reproduced.
