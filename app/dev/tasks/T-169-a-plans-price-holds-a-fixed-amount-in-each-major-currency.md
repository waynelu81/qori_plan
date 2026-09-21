---
id: T-169
title: A plan's price holds a fixed amount in each major currency
stream: selling
status: ready
owner: unassigned
estimate: M
depends: T-167
blocks: T-170
---

# T-169 — A plan's price holds a fixed amount in each major currency

## Why

`D-047` gives each plan's Stripe price fixed amounts in the major currencies,
as Stripe `currency_options`, and Qori's pages have to quote the same figures.
Two things stand in the way today:

- A `subscription_prices` row holds one amount and one currency. Qori cannot
  know a fixed price, and the console has nowhere to record one.
- An amount-off coupon would undo the fixed prices. Stripe shows a buyer their
  own currency only when the session's discounts carry that currency too, and
  otherwise falls back to the price's default currency, USD.

Afterwards:

- the row holds a fixed amount per currency;
- the console edits those amounts beside the USD one;
- the model answers "what does this plan cost in X";
- a plan coupon is a percentage off.

## Decisions taken to make this specifiable

- **The fixed amounts are a jsonb map on the row, `currency_options`, from a
  currency code to integer cents** — `{"AUD": 5500, "EUR": 3500}`. They belong
  to the price, change with it and are read with it. A child table would add a
  join and a row per currency for no reader that needs one. The map mirrors
  Stripe's own `currency_options` on the price. The USD amount stays in
  `amount_cents` and `currency`, the price's default currency (`T-167`).
- **The currencies that may carry a fixed price are `qori.billing.currencies`**:
  AUD, EUR, GBP, CAD, NZD, SGD, HKD and MYR. These are the two-decimal
  currencies a Series may be priced in, less USD, which is the base.
  Zero-decimal currencies such as JPY pay the USD price (`D-047`). Which of the
  eight actually have a price is the owner's call, made as data: a currency is
  in a row's map or it is not.
- **The console checks the map's shape, and Stripe stays the authority on the
  amounts.** Keys must be in `qori.billing.currencies` and differ from the
  row's own currency; values are whole cents, at least 1. A blank input means
  no fixed price in that currency and is left out of the map. Qori does not
  read Stripe's price back to compare: staff enter what they typed in Stripe,
  as they already do for the USD amount and the `price_…` id.
- **`SubscriptionPrice::amountIn(string $currency): ?int` answers what a plan
  costs in a currency.** It returns `amount_cents` for the row's own currency,
  the fixed amount for a currency in the map, and null otherwise. Null means
  there is no fixed price, so the buyer pays the price in `currency`, the
  base (`D-047`). `SubscriptionPrice::fixedCurrencies(): list<string>` returns the
  row's own currency first, then the map's keys. `T-170` reads both.
- **The console refuses an amount-off plan coupon.** An amount-off coupon without
  the buyer's currency makes Stripe show the default currency, so the fixed
  price is gone for anyone who uses it (`D-047`). `percent_off` becomes
  required, and a filled `amount_off_cents` is refused with
  `errors.pricing.percent_only`. Existing rows keep their columns, and the list
  still labels an old amount-off coupon. `errors.pricing.discount_shape` and
  `errors.pricing.currency_required` lose their only callers and are removed.

## Preconditions

**Data this task verifies against:** a clean database, then
`php artisan db:seed --class=PricingSeeder`.

**Equipment:** a browser, signed in to `/admin` as a staff owner.

## Scope

**In:**

- The `currency_options` column, its cast and its default.
- `SubscriptionPrice::amountIn()` and `fixedCurrencies()`.
- `qori.billing.currencies`.
- The console: one amount input per billing currency on the price form, the
  fixed amounts in the list of prices, validation, and the audit entry, which
  already records the validated data.
- `PricingSeeder` giving Start and Pro `D-047`'s proposed fixed amounts in AUD,
  EUR, GBP, CAD, NZD and SGD.
- Plan coupons refused unless they are a percentage.

**Out:**

- Quoting a fixed price on `/pricing` or the billing page, and the checkout's
  currency: `T-170`.
- Creating the fixed amounts in Stripe, and the owner's final figures: release
  checklist (`release-prerequisites.md`, `D-047`).
- Reading Stripe's price back to check the amounts agree. It is worth doing
  once staff enter real prices, and it is a new call into the Stripe folder.
  See Notes.
- Annual prices: they wait until retention is understood (the 11 September
  review, §5).

## Files

| Path                                                                          | Change | Notes                                        |
| ----------------------------------------------------------------------------- | ------ | -------------------------------------------- |
| `database/migrations/2026_09_22_100000_add_currency_options_to_subscription_prices.php` | new    | the column                                   |
| `app/Models/SubscriptionPrice.php`                                            | edit   | fillable, cast, default, the two methods     |
| `config/qori.php`                                                             | edit   | `billing.currencies`                         |
| `app/Http/Requests/Admin/StoreSubscriptionPriceRequest.php`                   | edit   | the map's rules                              |
| `app/Http/Requests/Admin/StoreSubscriptionCouponRequest.php`                  | edit   | percent-off only                             |
| `app/Http/Controllers/Admin/PricingController.php`                            | edit   | `currencyOptions` in the summary; `billingCurrencies` prop |
| `resources/js/pages/admin/Pricing.vue`                                        | edit   | the inputs and the list; the coupon form loses amount and currency |
| `lang/en/errors.php`                                                          | edit   | `pricing.percent_only` in; `discount_shape`, `currency_required` out |
| `database/seeders/PricingSeeder.php`                                          | edit   | the fixed amounts                            |
| `database/factories/SubscriptionPriceFactory.php`                             | edit   | a `withFixedPrices(array $cents)` state      |
| `tests/Feature/Checkout/PricingModelTest.php`                                 | edit   | see Tests                                    |

Flows: none — the console's save path is unchanged. `T-170` writes the fixed amounts into `docs/flows/billing.md` along with the chain that reads them.

## Database

| Table                 | Column             | Type  | Null | Default | Index / constraint |
| --------------------- | ------------------ | ----- | ---- | ------- | ------------------ |
| `subscription_prices` | `currency_options` | jsonb | no   | `'{}'`  | none               |

Migration: `database/migrations/2026_09_22_100000_add_currency_options_to_subscription_prices.php`

The model's `$attributes` default is the raw string `'{}'`, not `[]`
(`../qori/CLAUDE.md`, Persistence), and the cast is `'array'`.

## Code

```php
// config/qori.php, in the 'billing' section T-167 adds
// The currencies a plan may carry a fixed price in, beside its own (D-047).
// Two-decimal only: amount_cents would misdescribe JPY, whose buyers pay
// the base price instead.
'currencies' => ['AUD', 'EUR', 'GBP', 'CAD', 'NZD', 'SGD', 'HKD', 'MYR'],
```

```php
namespace App\Models;

class SubscriptionPrice extends Model
{
    /** @return int|null cents in $currency, or null when that currency has no fixed price */
    public function amountIn(string $currency): ?int;

    /** @return list<string> the row's own currency, then the map's keys */
    public function fixedCurrencies(): array;
}
```

`StoreSubscriptionPriceRequest`:

- `prepareForValidation()` upper-cases the map's keys and drops blank values.
- `rules()` gains `'currency_options' => ['array']` and
  `'currency_options.*' => ['integer', 'min:1']`.
- `withValidator()` refuses a key outside `qori.billing.currencies`, or equal
  to `currency`, on the field `currency_options.<KEY>`, with the framework's
  `in` message.

`StoreSubscriptionCouponRequest`: `percent_off` becomes `required`, and
`withValidator()` adds `errors.pricing.percent_only` on `amount_off_cents` when
that field is filled. The `discount_shape` and `currency_required` checks go.

`PricingController::summarise()` adds
`'currencyOptions' => $price->currency_options`, and `index()` adds
`'billingCurrencies' => config('qori.billing.currencies')`.

## Copy

| Key                             | File                | English                                                                                                                                                  |
| ------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pricing.percent_only.message`  | `lang/en/errors.php` | A plan coupon takes a percentage off, never an amount.                                                                                                  |
| `pricing.percent_only.resolution` | `lang/en/errors.php` | Enter a percentage and clear the amount. An amount off would show every buyer the plan in :currency instead of their own currency.                    |

`:currency` is `config('qori.billing.currency')`, interpolated rather than
restated. The reader is staff, as with the other `pricing` keys.

## Routes

None.

## Tests

**Changed: `tests/Feature/Checkout/PricingModelTest.php`: 6 new cases, 1 replaced**

1. `test_a_price_keeps_its_fixed_amounts_by_currency` — a staff owner saves
   Start at 3900 USD with `currency_options` AUD 5500 and EUR 3500. The row's
   map is exactly those two. `amountIn('AUD')` is 5500, `amountIn('USD')` is
   3900, and `amountIn('JPY')` is null.
2. `test_a_blank_fixed_amount_is_left_out` — `currency_options[GBP]` blank; the
   map has no GBP.
3. `test_a_fixed_amount_in_an_unlisted_currency_is_refused` —
   `currency_options[JPY]`; errors on `currency_options.JPY`; no row.
4. `test_a_fixed_amount_in_the_default_currency_is_refused` —
   `currency_options[USD]` on a USD price; errors on `currency_options.USD`.
5. `test_the_console_lists_each_prices_fixed_amounts` — `GET /admin/pricing`;
   the seeded Start row's `currencyOptions` carries AUD 5500, and the
   `billingCurrencies` prop is the config list.
6. `test_a_coupon_needs_a_percentage` — no `percent_off`; errors on
   `percent_off`.
7. `test_an_amount_off_plan_coupon_is_refused` replaces
   `test_a_coupon_cannot_be_percent_and_amount_at_once`. An amount alone, and
   an amount with a percentage, each error on `amount_off_cents`, and no row is
   written.

Total: 7, one of them replacing an existing case. The existing coupon cases
post `percent_off` and pass unchanged.

## Acceptance

- [ ] A price saved with fixed amounts keeps them, and `amountIn()` answers from them
- [ ] The console's price form has an input per billing currency, and its list shows each price's fixed amounts
- [ ] An amount-off plan coupon is refused with `errors.pricing.percent_only`
- [ ] `php artisan db:seed --class=PricingSeeder` writes `D-047`'s proposed fixed amounts
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

- Written 22 September 2026 from `D-047`. The seeder's fixed amounts are the
  proposal in `D-047`, not the owner's final prices: Start AUD 5500, EUR 3500,
  GBP 2900, CAD 5500, NZD 6900, SGD 4900; Pro AUD 13900, EUR 8900, GBP 7500,
  CAD 13900, NZD 17500, SGD 12900.
- Checking the row against Stripe's price is left out on purpose. If staff
  enter a fixed amount that differs from Stripe's, Qori's page quotes one
  figure and Stripe charges another. A read-back when a price is saved would
  catch it. Whoever finds this biting first drafts that task.
