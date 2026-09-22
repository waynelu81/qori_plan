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

None yet.

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

- **How the change happens**: through Stripe's Customer Portal, which has to
  be configured with the plans it may switch between, or through Qori calling
  Stripe to update the subscription's item. The portal is less code; the call
  keeps the owner on Qori's page. Anyone's, from the code and Stripe's docs.
- **What the owner is charged at the moment of the change**: a prorated
  difference now, the new price from the next renewal, or an immediate full
  charge. What a person pays and sees, so the owner's call.
- **Downgrades**, Pro to Start: at once or at the end of the period paid for.
  The owner's call, beside the one above.
- Whether the billing page should say, beside the currency menu, that a
  subscribed Group stays in the currency it pays in. Anyone's, once the two
  above are answered.

## Re-scope log

None.

## Notes

- Found during `T-170`, 22 September 2026. The refusal was observed in the
  sandbox; the second subscription was read from the code, not reproduced.
