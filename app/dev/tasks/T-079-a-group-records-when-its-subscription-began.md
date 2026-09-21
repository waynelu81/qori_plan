---
id: T-079
title: A Group records when its subscription began
stream: selling
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-079 — A Group records when its subscription began

> **Draft.** Written from the owner's Group-model review on 14 September 2026.
> One question keeps it from `ready`: what reads the date. See below.

## Why

The owner asked for `groups.subscription_starts_at`. Today
`BillingService::applySubscription()` writes `subscription_status`,
`subscription_ends_at` and `plan` from every subscription event Stripe sends,
and nothing records when the paid plan began. A Group on Pro cannot be told
how long it has been on Pro, the console cannot sort paying Groups by age,
and the measure "time from signup to first paid plan" has no second date.

## What the same review settled

**`stripe_customer_id` stays.** The owner asked what it is for, doubting a
direct charge needs one. It does not: a Peer buying a Series is a direct
charge on the creator's connected account and never touches it. The column
is Qori's own customer for the Group — `Subscription::customerFor()` creates
it on Qori's platform account and passes it to Checkout in subscription mode
and to the billing portal, both of which require a customer. It is the plan
subscription's, not the Series sale's (§7.1 against §7.2), and it is read.

## Proposed

`groups.subscription_starts_at`, timestamp, nullable. Written in
`applySubscription()` from Stripe's `start_date` — the moment the
subscription was created, stable across renewals, unlike
`current_period_start`. Kept when the subscription ends, paired with
`subscription_ends_at`, so a lapsed Group still shows the span it paid for;
overwritten when a new subscription starts. `GroupSubscription` gains
`startedAt`.

## Before this can be ready

- **What reads it.** The Billing page's Current plan panel ("Pro since
  14 September 2026")? The admin console's Group view? A measure in
  `PLAN.md`'s list? A column nothing reads is the pattern this codebase
  removes, so the task names its reader before it is claimed.
- Whether a trial's `start_date` counts as the subscription beginning, or
  the first paid period does (`trial_end`). Stripe's `start_date` is the
  former.
- Whether the console (§24) shows it, which decides whether an
  `App\Admin\Queries` change is in scope.

## Scope

**In:** the column, the write in `applySubscription()`, the data shape, one
reader, one test.

**Out:** anything about `stripe_customer_id`; Connect; the checkout.

## Files

| Path                                                                             | Change | Notes                                          |
| -------------------------------------------------------------------------------- | ------ | ---------------------------------------------- |
| `database/migrations/2026_09_14_000003_add_subscription_starts_at_to_groups.php` | new    | Nullable timestamp after `subscription_status` |
| `app/Models/Group.php`                                                           | edit   | Property, fillable, cast                       |
| `app/Services/BillingService.php`                                                | edit   | Written from `start_date`                      |
| `app/Data/GroupSubscription.php`                                                 | edit   | `startedAt`                                    |
| `tests/Feature/Checkout/SubscriptionTest.php`                                    | edit   | 1 new case                                     |
| The reader, once chosen                                                          | edit   |                                                |

## Database

| Table    | Column                   | Type      | Null | Default | Index / constraint |
| -------- | ------------------------ | --------- | ---- | ------- | ------------------ |
| `groups` | `subscription_starts_at` | timestamp | yes  | null    | none               |

## Code

```php
// App\Services\BillingService::applySubscription() — beside subscription_ends_at
'subscription_starts_at' => isset($subscription['start_date']) && is_numeric($subscription['start_date'])
    ? now()->setTimestamp((int) $subscription['start_date'])
    : $group->subscription_starts_at,
```

## Copy

To be decided with the reader.

## Routes

None.

## Tests

**Changed: `tests/Feature/Checkout/SubscriptionTest.php` — 1 new case**

1. `test_applying_a_subscription_records_when_it_began` — a
   `customer.subscription.updated` payload with `start_date` sets the column;
   a later payload without it leaves it standing.

## Acceptance

- [ ] The column is written from every subscription event and survives one without `start_date`
- [ ] The chosen reader shows it
- [ ] `composer ci:check` green from a clean tree
- [ ] Board regenerated (`php artisan qori:tasks`)
- [ ] Report written in `reports/`

## Re-scope log

None.

## Notes

`StripePeriod` exists because `current_period_end` moved off the subscription
object in API 2025-03-31. `start_date` has not moved and sits on the
subscription itself; if it ever does, the resolution belongs beside
`StripePeriod::endsAt()`, not in the service.
