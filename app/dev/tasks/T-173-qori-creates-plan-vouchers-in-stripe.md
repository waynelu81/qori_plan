---
id: T-173
title: Qori creates plan vouchers in Stripe
stream: selling
status: doing
owner: claude
estimate: S
depends: T-172
blocks: none
---

# T-173 — Qori creates plan vouchers in Stripe

## Why

`D-048` makes Qori the source of truth for vouchers as well as prices. The
owner asked: "same goes for voucher?" Today staff create a coupon in Stripe's
dashboard, then a row in Qori's console with its id and the same terms typed
again.

The console also still accepts an amount-off coupon. That undoes a fixed
price: Stripe shows a buyer their own currency only when the session's
discounts carry that currency too, and otherwise falls back to the default,
AUD (`D-047`).

Afterwards:

- a voucher is created in Qori and Qori makes the Stripe coupon;
- changing its terms replaces the coupon;
- retiring it deletes the coupon;
- every plan voucher is a percentage off.

## Decisions taken to make this specifiable

- **Plan vouchers are percent-off.** `percent_off` becomes required, and a
  filled `amount_off_cents` is refused with `errors.pricing.percent_only`.
  `errors.pricing.discount_shape` and `errors.pricing.currency_required` lose
  their only callers and are removed. Existing rows keep their columns, and
  the list still labels an old amount-off coupon.
- **Saving a voucher creates its Stripe coupon**, with `POST /v1/coupons`:
  - `percent_off`, `duration`, and `duration_in_months` when it repeats;
  - `max_redemptions` from the row;
  - `redeem_by` from `expires_at`, as a Unix time;
  - `name`: the code. Stripe allows 40 characters, and so does Qori's `code`
    rule;
  - `metadata[qori_coupon_id]`, and an `Idempotency-Key`, as `T-172` does for
    prices.

  The row is written with the new `stripe_coupon_id` only after Stripe
  accepts. On a refusal nothing is saved, and the console shows
  `errors.pricing.publish_failed`, the key `T-172` adds.
- **Changing a voucher's terms creates a new coupon and deletes the old one.**
  Stripe does not allow the terms to be edited: "Other coupon details
  (currency, duration, amount_off) are, by design, not editable"
  ([Stripe](https://docs.stripe.com/api/coupons/update)). The terms are the
  percentage, duration, months, cap and expiry. Changing only `is_active`
  retires or restores the voucher without replacing it.
- **Retiring a voucher deletes its Stripe coupon** with
  `DELETE /v1/coupons/{id}`. New uses stop. Whether a subscription that
  already has the discount keeps it is what the spike confirms; the
  expectation is that it does.
- **The code a customer types stays Qori's.** Qori matches the code to the
  row, counts redemptions and passes the coupon id, as today. It does not use
  Stripe promotion codes, because the code is entered on Qori's page and never
  on Stripe's.
- **`PublishesPricing` gains `publishCoupon()` and `retireCoupon()`**,
  implemented in `App\Integrations\Stripe\Pricing` beside `T-172`'s price
  methods.
- **The console's `stripe_coupon_id` input goes.** The id shows read-only.

## Preconditions

**Data this task verifies against:** the seeded prices, published in the
sandbox by `T-172`, and a local Group owned by a user.

**Equipment:**

- The Stripe sandbox, with `STRIPE_SECRET` in `.env`.
- `stripe listen` running.
- A browser signed in to `/admin` as a staff owner.

**Spike.**

1. Create a 20%-off, three-month voucher in the local console. Keep the body
   of the create response as `tests/Fixtures/stripe/coupon-created.json`.
2. Subscribe a Group with its code.
3. Retire the voucher, then read the Group's upcoming invoice with
   `stripe invoices upcoming --customer <id>`, and record whether the
   discount is still on it.

## Scope

**In:**

- Percent-off only, and the two error keys going.
- Creating, replacing and deleting the Stripe coupon from the console.
- The `stripe_coupon_id` input going.
- `docs/flows/billing.md`: vouchers are created from Qori.

**Out:**

- A creator's discount on their own Series: `T-049`, a different thing on the
  creator's own Stripe account.
- Stripe promotion codes (see Decisions).

## Files

| Path | Change | Notes |
| ---- | ------ | ----- |
| `app/Integrations/Contracts/PublishesPricing.php` | edit | `publishCoupon()`, `retireCoupon()` |
| `app/Integrations/Stripe/Pricing.php` | edit | the coupon calls |
| `app/Http/Controllers/Admin/PricingController.php` | edit | creates, replaces and retires coupons |
| `app/Http/Requests/Admin/StoreSubscriptionCouponRequest.php` | edit | percent-off only; no id input |
| `resources/js/pages/admin/Pricing.vue` | edit | the coupon form loses amount, currency and id |
| `lang/en/errors.php` | edit | `pricing.percent_only` in; `discount_shape`, `currency_required` out |
| `docs/flows/billing.md` | edit | vouchers are created from Qori |
| `tests/Fixtures/stripe/coupon-created.json`, `tests/Fixtures/stripe/README.md` | new, edit | the observed response and its row |
| `tests/Feature/Integrations/Stripe/PricingTest.php` | edit | |
| `tests/Feature/Checkout/PricingModelTest.php` | edit | |

## Database

None. `stripe_coupon_id` exists; Qori now writes it.

## Code

```php
namespace App\Integrations\Contracts;

interface PublishesPricing
{
    // …T-172's two methods, then:

    /** Creates the coupon at the vendor and returns its id. */
    public function publishCoupon(SubscriptionCoupon $coupon): string;

    public function retireCoupon(string $vendorCouponId): void;
}
```

## Copy

| Key                               | File                 | English                                                                                                         |
| --------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------- |
| `pricing.percent_only.message`    | `lang/en/errors.php` | A plan voucher takes a percentage off, never an amount.                                                         |
| `pricing.percent_only.resolution` | `lang/en/errors.php` | Enter a percentage and clear the amount. An amount off would show buyers the price in :currency instead of their own. |

`:currency` is `config('qori.billing.settlement_currency')`, interpolated
rather than restated. The reader is staff.

## Routes

None.

## Tests

**Changed: `tests/Feature/Integrations/Stripe/PricingTest.php` — 3 new cases**

1. `test_a_voucher_is_created_as_a_percent_off_coupon` — the body carries
   `percent_off=20`, `duration=repeating`, `duration_in_months=3` and
   `name=<code>`, with an `Idempotency-Key`. The faked response is the
   fixture.
2. `test_its_expiry_becomes_redeem_by` — `expires_at` is sent as a Unix time.
3. `test_retiring_a_voucher_deletes_its_coupon` — `DELETE /v1/coupons/{id}`.

**Changed: `tests/Feature/Checkout/PricingModelTest.php` — 4 new cases, 1 replaced**

4. `test_saving_a_voucher_creates_it_at_the_vendor` — the contract is faked,
   and the row holds the id it returned.
5. `test_changing_a_vouchers_terms_replaces_its_coupon` — a new id is stored,
   and the fake records `retireCoupon(<old id>)`.
6. `test_a_coupon_needs_a_percentage` — no `percent_off`; errors on
   `percent_off`.
7. `test_an_amount_off_plan_coupon_is_refused` replaces
   `test_a_coupon_cannot_be_percent_and_amount_at_once`. An amount alone, and
   an amount with a percentage, each error on `amount_off_cents`, and nothing
   is created at the vendor.

Total: 7, one of them replacing an existing case.

## Acceptance

- [ ] The spike ran: the voucher reached Stripe and applied at checkout, and what retiring it did to the existing discount is recorded
- [ ] A voucher is created, replaced and retired from Qori's console, and its id is never typed
- [ ] An amount-off plan voucher is refused
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

- Written 22 September 2026 from `D-048`. The percent-off rule was first
  written into `T-169` under `D-047`, and moved here when `T-169` became the
  price calculation.
