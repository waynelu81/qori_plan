---
id: T-167
title: Qori's plans are priced from a US dollar base
stream: selling
status: done
owner: claude
estimate: S
depends: none
blocks: T-169
---

# T-167 — Qori's plans are priced from a US dollar base

## Why

`D-048`: staff set every plan's price in USD, and every fixed currency is
calculated from it. The code already speaks USD, but only by accident:

- the literal `'USD'` is written into the console's new-price form and into
  `StoreSubscriptionPriceRequest`'s fallback;
- the design fixtures in `PricingSeeder` are US$19 and US$49 placeholders,
  not the planned US$39 and US$99.

`T-169` calculates from the USD price and needs its currency in one place.
`T-170` quotes it.

Afterwards:

- `qori.billing.currency` is that one place;
- the fixtures carry US$39 and US$99.

## Decisions taken to make this specifiable

- **Qori's billing currency is its own key, `qori.billing.currency`, not
  `qori.payments.default_currency`.** The second is the default for a Series
  price on the creator's own Stripe account (`SeriesController` reads it), and
  it is AUD. The first is the currency Qori's own plan prices are set in. They
  answer different questions, and a creator-facing default must not change
  because Qori's pricing did.
- **The console's currency field is left to `T-169`, which removes it.**
  Under `D-048` a price is always set in USD, so wiring the field to config
  here would be undone there.
- **The design fixtures take the planned monthly prices, US$39 and US$99, and
  get no annual row.** A design review then shows the price a creator will see.
  Annual waits until retention is understood (the 11 September review, §5).
- **No sandbox check here.** The end-to-end check of the hybrid is in `T-172`,
  where Qori first publishes a price to Stripe.

## Preconditions

**Data this task verifies against:** a clean database.

**Equipment:** none.

## Scope

**In:**

- `qori.billing.currency`, set to `USD`.
- `PricingSeeder`'s Start and Pro rows at 3900 and 9900 cents, in
  `qori.billing.currency`.

**Out:**

- The console form's currency field, and the fixed amounts: `T-169`.
- Publishing prices to Stripe: `T-172`. Vouchers: `T-173`.
- Quoting the visitor's currency on Qori's pages: `T-170`.
- Tax: `T-168`.

## Files

| Path                                          | Change | Notes                                |
| --------------------------------------------- | ------ | ------------------------------------ |
| `config/qori.php`                             | edit   | the `billing` section and `currency` |
| `database/seeders/PricingSeeder.php`          | edit   | 3900 and 9900 in the config currency |
| `tests/Feature/Checkout/PricingModelTest.php` | edit   | one case                             |

## Database

None.

## Code

```php
// config/qori.php — a new top-level section after 'payments'
'billing' => [
    // The currency staff set every plan's price in. Every fixed currency is
    // calculated from it, rounded up to a whole unit (D-048).
    'currency' => 'USD',
],
```

`PricingSeeder::plans()`: `1900` becomes `3900`, `4900` becomes `9900`, and
`'currency' => 'USD'` becomes `'currency' => config('qori.billing.currency')`.
The row ids and the fake `price_designreview…` ids are unchanged.

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/Checkout/PricingModelTest.php` — 1 new case**

1. `test_the_design_prices_are_the_planned_usd_prices` — after
   `PricingSeeder`, Start is 3900 and Pro is 9900, both in
   `qori.billing.currency`.

Total: 1.

## Acceptance

- [x] `qori.billing.currency` is `USD`, with its reason
- [x] `php artisan db:seed --class=PricingSeeder` writes Start at US$39 and Pro at US$99
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

- **22 September 2026, before anyone claimed it.** Written that morning as
  "Qori's plans are priced in Australian dollars" for `D-046`: an AUD base, a
  console defaulting to AUD, A$55 and A$139 fixtures, and a sandbox check that
  an Adaptive-Priced subscription still grants its plan. That afternoon
  `D-047` moved the base to USD and switched Adaptive Pricing off. The task was
  rewritten and renamed from
  `T-167-qoris-plans-are-priced-in-australian-dollars.md`; the fixed amounts
  went to `T-169`.
- **22 September 2026, that evening, still unclaimed.** `D-048` keeps USD as
  the currency staff set, but calculates every other one from it and switches
  Adaptive Pricing back on. `T-169` now removes the console's currency field,
  so the form and request wiring left this task. So did its second test.
  Files, Code and Tests shrank to match.

## Notes

- The USD literals were found while writing the first version:
  `Pricing.vue` has `value="USD"`, and
  `StoreSubscriptionPriceRequest::prepareForValidation()` falls back to
  `'USD'`. `T-169` removes both.
