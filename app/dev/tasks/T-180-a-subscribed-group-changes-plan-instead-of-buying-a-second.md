---
id: T-180
title: A subscribed Group changes plan instead of buying a second one
stream: selling
status: doing
owner: claude
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

- **The owner's answers (`D-052`, confirmed in `D-055`): an upgrade follows
  Claude's billing.** It takes effect at once, charges one full period of the
  new plan less the old plan's unused part, prorated to the second, and
  restarts the cycle. A downgrade takes effect at the end of the period
  already paid for, with no refund or credit: the new plan is charged from
  the next billing cycle. The change stays in the subscription's own
  currency.
- **Qori makes the change through Stripe's API, not the Customer Portal.** The
  API controls each part of Claude's shape exactly: the proration, the cycle
  restarting, and the change applying only once it is paid. It also keeps the
  owner on Qori's billing page, where the amount is shown before they
  confirm.
  - An upgrade updates the subscription's item with
    `proration_behavior=always_invoice`, `billing_cycle_anchor=now` and
    `payment_behavior=pending_if_incomplete`, and moves `metadata[plan]` with
    it, since `applySubscription()` reads the plan from there. Stripe lists
    `metadata` among the attributes a pending update supports, and the spike
    saw it move.
  - A downgrade is a subscription schedule whose next phase, at the current
    period's end, has the cheaper price, the subscription's currency, its
    discounts by id and `metadata[group_id]` and `metadata[plan]`.
- **Which plan is dearer is read from the rows**: the new row's
  `amount_cents` (USD, `D-048`) above the current plan's is an upgrade, and
  anything else is a downgrade. A current plan with no row is treated as the
  cheaper one.
- **The owner sees what an upgrade will charge before confirming**, from
  Stripe's invoice preview for that change, so the figure is Stripe's own.
  Stripe refuses a fixed `proration_date` beside `billing_cycle_anchor=now`
  ("You cannot specify `proration_date` when `billing_cycle_anchor=now`",
  sandbox, 22 September 2026), so the preview and the charge are each worked
  out at their own moment. The charge grows by about a cent every ten minutes
  a page stays open, so **the confirm form carries `quoted_at`, and a figure
  more than 15 minutes old is refused** and worked out again
  (`billing.change.quote_expired`).
- **A declined upgrade sends the owner to Stripe's page for its invoice.**
  With `pending_if_incomplete` the plan does not change: the subscription
  holds a `pending_update`, and its latest invoice is open with a
  `hosted_invoice_url`. That page takes another card or the bank's extra
  step, and paying it applies the change, which reaches Qori as
  `customer.subscription.updated` like any other change. The confirm page
  says so before the owner clicks.
- **A paid upgrade is applied from Stripe's answer at once**, so the owner
  lands on the plan they paid for instead of waiting for the webhook.
  `applySubscription()` is still the only writer of `groups.plan`, and now
  has two callers: the webhook and the upgrade, both handing it Stripe's own
  account of the subscription.
- **`applySubscription()` takes a `GroupSubscription`, read in the Stripe
  folder.** `App\Integrations\Stripe\SubscriptionReader::read()` turns the
  payload into it, for the webhook and for the API's answers. It replaces
  `GroupSubscription::fromStripe()`, since `CLAUDE.md` keeps a vendor's
  payload out of `app/Data` and out of a Service.
- **Qori keeps the subscription's id and currency**: the webhook writes them
  on the Group, so a change never has to guess which subscription is the
  Group's. An event for a different subscription is applied only when that
  subscription is paying, which is a new checkout; otherwise it is an old one
  ending, and it is ignored. This settles "the webhook sets the plan from
  whichever event lands last" above.
- **Qori records the scheduled downgrade on the Group** (`scheduled_plan`,
  `scheduled_plan_at`) once Stripe has accepted the schedule, so the billing
  page can say what happens and when without calling Stripe. The webhook
  clears them when the subscription has no schedule any more or has reached
  that plan. `groups.plan` still moves only through `applySubscription()`.
- **"Keep Pro" cancels a scheduled downgrade** by releasing the schedule. The
  spike saw the subscription keep its plan and its discount.
- **An upgrade releases any schedule first.** The schedule stays attached
  for the downgraded phase, and left in place it would move the upgraded
  subscription back at that phase's end.
- **Who can change plan:** a Group with a stored subscription whose status is
  `active` or `trialing`. One that is `past_due`, `unpaid`, `incomplete` or
  `paused` is told to settle the failed payment first
  (`errors.billing.change_needs_payment`). A Group whose subscription is
  anything but `canceled` or `incomplete_expired` is never sent to a second
  checkout: `subscribe` redirects it to the change page, and
  `BillingService::subscribe()` refuses it (`errors.billing.already_subscribed`).
- **The billing page for a subscribed Group has no currency menu.** Its cards
  show the subscription's currency, with `billing.currency.subscribed` in the
  menu's place. A currency the new plan has no figure in is refused before
  Stripe is asked (`errors.billing.plan_currency_unavailable`).
- **A buyer on Adaptive Pricing** is subscribed in AUD, presented in their
  own currency (Stripe's Adaptive Pricing page: the subscription event
  carries `presentment_details.presentment_currency`). The confirm page shows
  the AUD figure with `billing.change.upgrade.converted`. Not observed: a JPY
  subscription needs a card typed into Checkout, which is the owner's to do.

## Preconditions

**Data this task verifies against:** Start and Pro published in the sandbox
(`price_1UIQm2KUCxslwo7asJr9K2IV` and `price_1UIQm7KUCxslwo7aJY0JecTJ`,
re-saved from the local console's path on 22 September 2026), and a local
Group owned by a user.

**Equipment:** the Stripe sandbox with `STRIPE_SECRET` in `.env`; test clocks
for the period ends.

**Spike (ran 22 September 2026, before this was ready).** On test clocks, with
`pm_card_visa` and the published prices:

1. A EUR Start subscription, ten days in: the preview charged €64.33, which
   is €87.00 for a month of Pro less €22.67 for twenty unused days of Start.
   The update charged the same, restarted the cycle and moved
   `metadata[plan]`.
2. A downgrade back to Start: the schedule's second phase took `eur` without
   being told, and at the period end the subscription moved to Start, billed
   €34.00, and its metadata read `plan: start` with `group_id` kept.
3. A USD Pro subscription with a 20%, three-month voucher: the schedule
   carried the discount by its id, with its end unchanged. Releasing the
   schedule kept Pro and the discount.
4. An upgrade with `pm_card_chargeCustomerFail` as the default card: the
   subscription stayed on Start with `pending_update` holding the new price
   and `metadata[plan]`, and an open US$60.00 invoice with a
   `hosted_invoice_url`.

## Scope

**In:**

- A subscribed Group's plan change moves its existing subscription to the new
  price, and never opens a second one.
- The currency of the change is the subscription's own, whatever the menu
  says.
- The upgrade's preview and confirm page; the downgrade's confirm page, what
  the billing page says while it is scheduled, and cancelling it.
- The webhook keeping the subscription's id and currency.

**Out:**

- Moving every subscriber onto a new price after a price change (`D-048`: a
  separate decision).
- Cancelling a plan, and a cancelling subscription's own state: the Customer
  Portal's, as today.
- A change of interval (monthly to yearly): every plan is monthly.

## Files

| Path | Change | Notes |
| ---- | ------ | ----- |
| `database/migrations/2026_09_22_130000_add_subscription_to_groups.php` | new | four columns, below |
| `app/Models/Group.php` | edit | columns, `hasSubscription()`, `canChangePlan()` |
| `app/Data/GroupSubscription.php` | edit | `groupId`, `plan`, `currency`, `presentmentCurrency`, `hasSchedule`; `endsAt`; `fromStripe()` goes |
| `app/Data/PlanQuote.php` | new | an upgrade's preview |
| `app/Data/PlanUpgrade.php` | new | an upgrade's outcome |
| `app/Data/PlanChange.php` | new | what the confirm page states |
| `app/Integrations/Contracts/BillsGroups.php` | edit | four methods |
| `app/Integrations/Stripe/Subscription.php` | edit | the calls |
| `app/Integrations/Stripe/SubscriptionReader.php` | new | the payload read |
| `app/Services/BillingService.php` | edit | `planChange()`, `changePlan()`, `keepPlan()`; `subscribe()` refuses; `applySubscription(GroupSubscription)` |
| `app/Http/Controllers/StripeWebhookController.php` | edit | reads through `SubscriptionReader` |
| `app/Http/Controllers/Share/BillingController.php` | edit | `showChange()`, `change()`, `keepPlan()`; `subscribe()` redirects; `show()` props |
| `app/Http/Requests/Share/ChangePlanRequest.php` | new | `quoted_at` |
| `routes/share/group.php` | edit | three routes |
| `resources/js/pages/share/Billing.vue` | edit | subscribed currency, the scheduled change, links to the change page |
| `resources/js/pages/share/BillingChange.vue` | new | the confirm page |
| `lang/en/billing.php` | edit | `currency.subscribed`, `change.*` |
| `lang/en/errors.php` | edit | four `billing.*` keys |
| `docs/flows/billing.md` | edit | Flows: the change, the webhook's id |
| `tests/Fixtures/stripe/*.json`, `tests/Fixtures/stripe/README.md` | new, edit | the spike's five bodies |
| `tests/Feature/Integrations/Stripe/SubscriptionChangeTest.php` | new | |
| `tests/Feature/Checkout/PlanChangeTest.php` | new | |
| `tests/Feature/Checkout/SubscriptionTest.php` | edit | the reader; the webhook's id |

Fixtures, from the spike: `invoice-preview-upgrade-eur.json`,
`subscription-upgraded-eur.json`, `subscription-schedule-downgrade-eur.json`,
`subscription-downgraded-eur.json`, `subscription-upgrade-pending.json`.

## Database

`database/migrations/2026_09_22_130000_add_subscription_to_groups.php`, on
`groups`:

| Column | Type | Null | Notes |
| ------ | ---- | ---- | ----- |
| `stripe_subscription_id` | string | yes | on `$hidden`, like `stripe_customer_id` |
| `subscription_currency` | string(3) | yes | upper case, `EUR` |
| `scheduled_plan` | string | yes | the plan a scheduled downgrade moves to |
| `scheduled_plan_at` | timestampTz | yes | when it does |

No index: nothing queries them.

## Code

```php
namespace App\Integrations\Contracts;

interface BillsGroups
{
    // …the existing methods, then:

    /** What moving to this price at once would charge, from the vendor's preview. */
    public function quoteUpgrade(Group $group, SubscriptionPrice $price): PlanQuote;

    /** Moves the subscription at once, charging the difference; applied only once paid. */
    public function upgrade(Group $group, SubscriptionPrice $price): PlanUpgrade;

    /** Moves the subscription to this price when the paid period ends; returns when. */
    public function downgradeAtRenewal(Group $group, SubscriptionPrice $price): CarbonInterface;

    public function cancelScheduledChange(Group $group): void;
}
```

```php
namespace App\Data;

class PlanQuote { string $currency; int $amountDueCents; CarbonInterface $renewsAt; ?string $presentmentCurrency; }
class PlanUpgrade { GroupSubscription $subscription; ?string $paymentUrl; isPaid(): bool }
class PlanChange { bool $isUpgrade; SubscriptionPrice $from; SubscriptionPrice $to; string $currency; ?PlanQuote $quote; ?CarbonInterface $takesEffectAt; }
```

`BillingService`: `planChange(Group, string $plan): PlanChange`,
`changePlan(Group, string $plan): ?string` (the URL to finish paying at, or
null once changed or scheduled), `keepPlan(Group): void`,
`applySubscription(GroupSubscription): ?Group`.

## Copy

| Key | File | English |
| --- | ---- | ------- |
| `currency.subscribed` | `lang/en/billing.php` | You pay in :currency, and a change of plan stays in :currency. |
| `change.title` | `lang/en/billing.php` | Switch to :plan |
| `change.upgrade.summary` | `lang/en/billing.php` | :amount today: a :interval of :plan, less the unused part of :current. |
| `change.upgrade.renews` | `lang/en/billing.php` | :plan starts as soon as it's paid, and renews on :date. |
| `change.upgrade.converted` | `lang/en/billing.php` | Stripe charges it in :currency, at the day's exchange rate. |
| `change.upgrade.declined` | `lang/en/billing.php` | If your bank asks for another step, or the card is declined, Stripe's page opens to finish the payment. Your plan changes once it's paid. |
| `change.upgrade.confirm` | `lang/en/billing.php` | Pay :amount and switch |
| `change.downgrade.summary` | `lang/en/billing.php` | You keep :current until :date, the end of the period you've paid for. :plan starts then, at :amount a :interval. |
| `change.downgrade.confirm` | `lang/en/billing.php` | Switch to :plan on :date |
| `change.back` | `lang/en/billing.php` | Back to billing |
| `change.upgraded` | `lang/en/billing.php` | You're on :plan now. |
| `change.scheduled` | `lang/en/billing.php` | :plan starts on :date. You keep :current until then. |
| `change.pending` | `lang/en/billing.php` | Changes to :plan on :date. |
| `change.keep` | `lang/en/billing.php` | Keep :plan |
| `change.kept` | `lang/en/billing.php` | You're staying on :plan. |
| `change.starts` | `lang/en/billing.php` | Starts :date |
| `change.quote_expired` | `lang/en/billing.php` | The amount was out of date, so it's been worked out again. Check it and confirm. |
| `billing.already_subscribed.message` / `.resolution` | `lang/en/errors.php` | This group already has a plan. / Change plan from the billing page instead. |
| `billing.change_needs_payment.message` / `.resolution` | `lang/en/errors.php` | Your last payment didn't go through, so the plan can't change yet. / Update your card in Manage billing, then try again. |
| `billing.same_plan.message` | `lang/en/errors.php` | This group is already on :plan. |
| `billing.plan_currency_unavailable.message` | `lang/en/errors.php` | :plan has no price in :currency yet. |

`:amount` is `App\Support\Money::format()`; `:date` is `j M Y` in the Group's
timezone; `:currency` is the code, as `billing.currency.converted` has it.
`plan_currency_unavailable` has no resolution: the owner cannot fix it, and
only staff recalculating the price can. `same_plan` is final.

## Routes

| Verb | Path | Name | Action |
| ---- | ---- | ---- | ------ |
| GET | `g/{group}/billing/change/{plan}` | `share.billing.change.show` | `BillingController::showChange` |
| POST | `g/{group}/billing/change/{plan}` | `share.billing.change` | `BillingController::change` |
| DELETE | `g/{group}/billing/change` | `share.billing.change.destroy` | `BillingController::keepPlan` |

`{plan}` is the plan's key, as in `billing/subscribe/{plan}`. All three are
owner-only.

## Tests

**New: `tests/Feature/Integrations/Stripe/SubscriptionChangeTest.php` — 8 cases**

1. `test_an_upgrade_is_previewed_with_the_cycle_restarting`
2. `test_an_upgrade_is_charged_at_once_and_moves_the_plan`
3. `test_a_declined_upgrade_waits_on_the_invoice_page`
4. `test_an_upgrade_releases_a_scheduled_change_first`
5. `test_a_downgrade_is_scheduled_for_the_end_of_the_period`
6. `test_a_downgrade_updates_a_schedule_that_already_exists`
7. `test_keeping_the_plan_releases_the_schedule`
8. `test_the_reader_takes_the_currency_plan_and_schedule`

**New: `tests/Feature/Checkout/PlanChangeTest.php` — 11 cases**

9. `test_a_subscribed_group_is_sent_to_change_plan_not_to_checkout`
10. `test_the_upgrade_page_shows_the_vendors_amount`
11. `test_confirming_an_upgrade_applies_the_plan_at_once`
12. `test_a_declined_upgrade_sends_the_owner_to_pay`
13. `test_a_downgrade_is_scheduled_and_the_plan_kept`
14. `test_keeping_the_plan_cancels_the_scheduled_change`
15. `test_an_out_of_date_amount_is_worked_out_again`
16. `test_a_group_whose_payment_failed_cannot_change_plan`
17. `test_changing_plan_is_owner_only`
18. `test_a_plan_without_the_subscriptions_currency_is_refused`
19. `test_the_billing_page_shows_a_subscribed_groups_own_currency`

**Changed: `tests/Feature/Checkout/SubscriptionTest.php` — 3 new cases**

20. `test_the_webhook_keeps_the_subscriptions_id_and_currency`
21. `test_an_event_for_another_ended_subscription_is_ignored`
22. `test_the_scheduled_plan_is_cleared_once_it_starts`

The existing `applySubscription()` cases read their payloads through
`SubscriptionReader::read()`.

Total: 22 new.

## Acceptance

- [ ] A subscribed Group that switches plan has one subscription afterwards, on the new plan, in its own currency
- [ ] An upgrade shows Stripe's figure, charges it at once and restarts the cycle; a declined one leaves the plan as it was
- [ ] A downgrade keeps the dearer plan until the paid period ends, and can be cancelled until then
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
- ~~**Downgrades**~~ — answered 22 September 2026 (`D-052`), confirmed by the
  owner the same day (`D-055`): the new plan is charged from the next billing
  cycle.
- ~~The copy~~ — written (Copy).
- ~~Whether the billing page says a subscribed Group stays in its currency~~
  — it does, in the menu's place (Decisions).
- ~~A spike~~ — ran 22 September 2026 (Preconditions).

## Re-scope log

None.

## Notes

- Found during `T-170`, 22 September 2026. The refusal was observed in the
  sandbox; the second subscription was read from the code, not reproduced.
