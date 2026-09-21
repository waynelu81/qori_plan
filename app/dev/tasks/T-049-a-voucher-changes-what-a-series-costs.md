---
id: T-049
title: A voucher that changes what a Series costs
stream: selling
status: draft
owner: unassigned
estimate: M
depends: T-054
blocks: none
---

# T-049 — A voucher that changes what a Series costs

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

A Series carries a price — `price_cents` and `currency`, both nullable, where
null means free rather than zero. There is no way to charge anything other than
that price. A creator running a launch, a returning-customer offer or a partner
deal has to edit the Series price for everybody or not run it.

Owner direction, 11 September 2026: a Series needs a voucher, carrying a **code**,
a **price that overrides the original**, a **start date**, an **expiry date**
and an **active flag**.

## The thing this must not be confused with

**`SubscriptionCoupon` already exists and is not this.** It discounts **Qori's
own subscription plans**, holds a `stripe_coupon_id`, a `percent_off`, a
`duration_in_months` and a `redeemed_count`, is created by staff at
`/admin/pricing/coupons`, and applies on the platform's Stripe account.

A Series voucher is the creator's discount on the creator's product, settling on
the creator's **connected** account (§7.2). Different owner, different Stripe
account, different money. Extending `SubscriptionCoupon` to cover both would put
Qori's revenue and a creator's revenue in one table with one `is_active` flag,
and the first bug in it would be somebody's takings.

## Decisions taken to make this specifiable

**Both a percentage and an overriding price, with percentage the default.**
Owner direction. A percentage scales across Series and an override does not, so
percentage is what a creator reaches for first and what the form should offer
first. The override is there for the case a creator wants a Series to cost a
specific number with this code, whatever it costs without one.

**A coupon may never raise a price: `min(discounted, price_cents)`.** Owner
direction, and the rule that makes an override safe at Group level. A code
overriding to $19 applied to a $9 Series charges $9. Without it a "discount"
becomes a surcharge the first time a creator lowers a Series price and forgets
a code that names a higher one.

**Rounding is the percentage's cost and it has to be decided, not defaulted.**
A percentage of an integer cent amount is a fraction. `intdiv` truncates in the
buyer's favour and `round()` does not. Pick one, write it down, and assert it on
a price that does not divide cleanly, because a discount that is a cent out is a
discount somebody screenshots.

**A window and a flag, both.** A date range says when it is meant to run; the
flag says whether it runs at all. A creator turning something off in a hurry
should not have to edit a date, and a date that has passed should not need the
flag touched. Either one being false means no discount.

**The currency does not change.** A voucher sets an amount in the Series'
existing currency. A code that changes which currency is charged is a different
feature and a worse idea.

**A coupon belongs to the Group, and names the Series it applies to.** Owner
direction, and the structure follows from the code being a namespace: a buyer
types `SUMMER25` on a Series page and Qori has to resolve it deterministically,
so uniqueness is enforced per Group whichever way it is modelled. A Series-owned
coupon would still need a Group-scoped unique index, at which point it is
Group-owned with an applicability list. So: `coupons` carries `group_id` and uses
`BelongsToGroup` like every other group-owned model, with a join table naming the
Series it covers.

An **override** price with a Group-wide coupon is the sharp edge: one code
setting both a $39 and a $99 Series to $19 is a 51% discount and an 81% one. The
creator has to see what each Series becomes at the moment they attach it, which
is why the join is explicit rather than "all of them by default" for that kind.

## Preconditions

None beyond a clean checkout, though `T-050` is worth landing first: a discount
code is for handing out, and today a creator has no link to hand out with it.

## Scope

**In, provisionally:**

- Vouchers belonging to a Series: code, overriding price, start, expiry, active.
- Entering a code on the public page, and what the reader is charged.
- Managing them from the Series builder.

**Out:**

- Free-trial codes, and codes that span more than one Group.
- Usage limits and per-person limits. Named below as a decision, deliberately
  not assumed into the scope.
- Qori's own subscription coupons, which are staff-managed and unrelated.
- Per-person invitation prices, which are `T-043` and are not a code anybody
  types.

## Before this can be ready

- **Decide whether a voucher can be redeemed more than once, and by how many
  people.** A code with no limit that reaches a forum is a Series sold at the
  discount forever. `SubscriptionCoupon` has `max_redemptions` and
  `redeemed_count` for exactly this reason, which is evidence the question has
  already been answered once in this product.
- **Decide what a voucher may do to a free Series, and to zero.** A code that
  makes a paid Series free is the common case and it bypasses checkout entirely,
  which means access is granted on a page with no payment — a different code
  path from the paid one, and the one worth testing hardest.
- ~~Decide whether codes live in Stripe or in Qori.~~ **Answered 11 September
  2026: Qori owns them.** A `coupons` table, Qori's arithmetic, Qori's window and
  redemption count, and a `unit_amount` sent to Stripe that Qori has already
  discounted. This is the decision that set the size of the task, and it is the
  larger of the two options.
- **Decide where the code is entered**, now that Qori owns it: on the public page
  before pressing buy is the obvious place, and it means the page has to
  re-price without a reload and the server has to re-check the code at session
  creation rather than trusting what the page sent.
- **Decide what a creator sees.** A code nobody has used and a code used two
  hundred times look identical without a count, and the count is the thing that
  tells a creator whether the launch worked.
- **Decide the timezone the dates are read in.** `T-024` settled that the
  Group's zone is what a scheduled time means, because the person choosing it is
  the creator. An expiry at midnight is a moment somebody has to be right about.

## Re-scope log

None.

## Notes

**Qori owning the arithmetic means Qori owns the race.** Two people using the
last redemption of a capped code at the same moment is a real concurrency
question, and the answer has to be a database constraint rather than a read
followed by a write. `SeriesService` had exactly this shape of bug until
`T-042`.

**A 100% coupon is a different code path, and it is the one to test hardest.**
It produces a price of nothing, which means no checkout session at all and
access granted on a page where no money moved. Stripe's own answer to this is a
session with `payment_status` of `no_payment_required`, which
`StripeWebhookController` currently ignores — it only acts on `paid`. Whichever
route is taken, that branch needs a test before it is written.

**`T-050` first.** A discount code is for handing out, and today a creator has
no link to hand out with it.
