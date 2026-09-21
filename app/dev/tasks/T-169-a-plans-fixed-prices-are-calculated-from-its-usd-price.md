---
id: T-169
title: A plan's fixed prices are calculated from its USD price
stream: selling
status: ready
owner: unassigned
estimate: M
depends: T-167, T-168
blocks: T-170, T-172
---

# T-169 — A plan's fixed prices are calculated from its USD price

## Why

`D-048`: staff set one number per plan, its USD price, and every fixed
currency is calculated from it at the day's mid-market rate, rounded up to a
whole unit. US$39 becomes A$55, €34 and £30. Today:

- a `subscription_prices` row holds one amount and one currency;
- staff would have to work out and type every other currency by hand;
- nothing records which rate made which figure.

Afterwards, saving a plan's USD price fetches the day's rates, calculates
every fixed currency, and stores the amounts and the rates beside it. The
console shows them. Publishing to Stripe is `T-172`.

## Decisions taken to make this specifiable

- **The row keeps USD in `amount_cents` and `currency`, and gains three
  columns.** `currency_options` is a jsonb map from currency code to integer
  cents, AUD included. `exchange_rates` is a jsonb map from currency code to
  the rate from USD, as a decimal string. `rates_on` is the date the rates are
  for. They belong to the price and change with it; a child table would add a
  join for no reader that needs one. The map mirrors Stripe's own
  `currency_options`.
- **The currencies calculated are `qori.billing.fixed_currencies`**: AUD, EUR,
  GBP, CAD, NZD and SGD, the list in `D-048`. It must include
  `qori.billing.settlement_currency` (AUD), because Stripe's price is based in
  it (`T-172`), and a test holds that. Only two-decimal currencies belong in
  it: `amount_cents` would misdescribe JPY, which Adaptive Pricing converts
  instead. Adding HKD or MYR is a one-line change.
- **Rounding is up, to a whole unit, in decimal arithmetic, never floats.** In
  that currency's cents, the amount is
  `ceil(usd_cents × rate / 100) × 100`. A figure already whole stays as it
  is. `bcmath` does the arithmetic on the rate's decimal string. This is the
  owner's rule (`D-048`): US$39 × 1.743690 is NZ$68.0039, so NZ$69.
- **Rates come from the European Central Bank's daily reference rates**
  (`D-048`, decided rather than asked): free, official, no account, and they
  cover every fixed currency. The ECB quotes against the euro, so the rate
  from USD to a currency is `rate[currency] / rate[USD]`, and USD to EUR is
  `1 / rate[USD]`. Rates are kept to 6 decimal places.
- **Rates sit behind a contract in Qori's terms**,
  `App\Integrations\Contracts\QuotesExchangeRates`. The ECB's code, its URL,
  its XML and its timeout live in `app/Integrations/EuropeanCentralBank`. It
  is bound in `IntegrationServiceProvider`, like `BillsGroups`.
- **A price is recalculated when its USD amount changes, or when staff tick
  "Recalculate at today's rates"** (the form field `recalculate`). Editing
  only its name, tagline, features or flags keeps its amounts: correcting a
  typo must never reprice a plan, and under `T-172` it would publish a new
  Stripe price. A new price is always calculated. If the rates cannot be
  fetched, nothing is saved, and the console says so with
  `errors.pricing.rates_unavailable`, the ECB's failure going in `upstream`. A
  price is never saved with amounts that were not calculated.
- **The console stops asking for a currency.** The form takes the USD amount
  only, `currency` is always `qori.billing.currency`, and the calculated
  amounts and the rates date show in the list beside each price.
- **The design fixtures carry `D-048`'s table as static values.** A seeder
  never calls a vendor: `PricingSeeder` writes the calculated amounts, the
  rates and `rates_on` = 2026-09-21 as data.

## Preconditions

**Data this task verifies against:** a clean database, then
`php artisan db:seed --class=PricingSeeder`.

**Equipment:** a browser signed in to `/admin` as a staff owner, and network
access to `www.ecb.europa.eu` for the one live fetch.

**Spike.** Fetch
`https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml` once and
commit the body as `tests/Fixtures/ecb/eurofxref-daily.xml`, with a README row
giving the date observed. The 21 September 2026 values `D-048` quotes were
read from that file: USD 1.1490, AUD 1.6098, GBP 0.85780, CAD 1.6091, NZD
2.0035, SGD 1.4647.

## Scope

**In:**

- The three columns, their casts and defaults.
- `SubscriptionPrice::amountIn()` and `fixedCurrencies()`.
- `qori.billing.fixed_currencies` and `qori.billing.settlement_currency`.
- The contract, the ECB reader, the `ExchangeRates` shape, the calculator.
- The console form and list, the `recalculate` checkbox, and
  `PricingController::storePrice()` calculating before it saves.
- `PricingSeeder` carrying `D-048`'s table.
- `docs/flows/billing.md`: the price list section says how a price's amounts
  are calculated.

**Out:**

- Creating the price in Stripe, and the `stripe_price_id` input: `T-172`.
- Vouchers, which become percent-off and are created in Stripe: `T-173`.
- Quoting the visitor's currency on `/pricing` and the billing page: `T-170`.
- Recalculating on a schedule. A fixed price moves only when staff save it
  (`D-048`).
- Moving existing subscribers to a new price (`D-048`: a separate decision).

## Files

| Path | Change | Notes |
| ---- | ------ | ----- |
| `database/migrations/2026_09_22_100000_add_fixed_prices_to_subscription_prices.php` | new | three columns |
| `app/Models/SubscriptionPrice.php` | edit | fillable, casts, defaults, `amountIn()`, `fixedCurrencies()` |
| `config/qori.php` | edit | `billing.fixed_currencies`, `billing.settlement_currency` |
| `app/Integrations/Contracts/QuotesExchangeRates.php` | new | the contract |
| `app/Integrations/EuropeanCentralBank/ReferenceRates.php` | new | fetches and reads the ECB file |
| `app/Data/ExchangeRates.php` | new | base, date, rates |
| `app/Support/FixedPrices.php` | new | the calculation |
| `app/Providers/IntegrationServiceProvider.php` | edit | binds the contract |
| `app/Http/Requests/Admin/StoreSubscriptionPriceRequest.php` | edit | no `currency` input; always `qori.billing.currency` |
| `app/Http/Controllers/Admin/PricingController.php` | edit | calculates on save; the amounts in the summary |
| `resources/js/pages/admin/Pricing.vue` | edit | the USD input; the amounts and date in the list |
| `lang/en/errors.php` | edit | `pricing.rates_unavailable` |
| `database/seeders/PricingSeeder.php` | edit | `D-048`'s table |
| `database/factories/SubscriptionPriceFactory.php` | edit | a `withFixedPrices(array $cents)` state |
| `docs/flows/billing.md` | edit | how the amounts are calculated |
| `tests/Fixtures/ecb/eurofxref-daily.xml`, `tests/Fixtures/ecb/README.md` | new | the observed file |
| `tests/Unit/Support/FixedPricesTest.php` | new | |
| `tests/Feature/Integrations/EuropeanCentralBank/ReferenceRatesTest.php` | new | |
| `tests/Feature/Checkout/PricingModelTest.php` | edit | |

## Database

| Table                 | Column             | Type  | Null | Default | Index / constraint |
| --------------------- | ------------------ | ----- | ---- | ------- | ------------------ |
| `subscription_prices` | `currency_options` | jsonb | no   | `'{}'`  | none               |
| `subscription_prices` | `exchange_rates`   | jsonb | no   | `'{}'`  | none               |
| `subscription_prices` | `rates_on`         | date  | yes  | null    | none               |

Migration: `database/migrations/2026_09_22_100000_add_fixed_prices_to_subscription_prices.php`

The model's `$attributes` defaults are the raw strings `'{}'`, not `[]`
(`../qori/CLAUDE.md`, Persistence). The two maps are cast `'array'`, and
`rates_on` is cast `'immutable_date'`.

## Code

```php
// config/qori.php, in the 'billing' section T-167 adds
// The currency Qori's Stripe account pays out in: each Stripe price's default
// currency, which Adaptive Pricing converts from (D-048).
'settlement_currency' => 'AUD',
// The currencies a plan's fixed price is calculated in from its USD price,
// rounded up to a whole unit (D-048). Must include settlement_currency.
// Two-decimal only.
'fixed_currencies' => ['AUD', 'EUR', 'GBP', 'CAD', 'NZD', 'SGD'],
```

```php
namespace App\Integrations\Contracts;

interface QuotesExchangeRates
{
    /** @param list<string> $currencies */
    public function ratesFrom(string $base, array $currencies): ExchangeRates;
}

namespace App\Data;

final class ExchangeRates
{
    /** @param array<string, string> $rates currency => rate from $base, 6 decimal places */
    public function __construct(
        public string $base,
        public CarbonImmutable $on,
        public array $rates,
    ) {}
}

namespace App\Support;

final class FixedPrices
{
    /** @return array<string, int> currency => cents, each a whole unit, rounded up */
    public static function calculate(int $baseCents, ExchangeRates $rates): array;
}

namespace App\Models;

class SubscriptionPrice extends Model
{
    /** cents in $currency: amount_cents for the row's own, the map's for a fixed one, else null */
    public function amountIn(string $currency): ?int;

    /** @return list<string> the row's own currency, then the map's keys */
    public function fixedCurrencies(): array;
}
```

`PricingController::storePrice()` takes `QuotesExchangeRates` by method
injection. For a new price, a changed `amount_cents` or `recalculate` set, it
asks for the rates from `qori.billing.currency` to
`qori.billing.fixed_currencies`, calculates, and writes `currency_options`,
`exchange_rates` and `rates_on` with the rest. Otherwise it leaves those
three as they are. A failed fetch throws `AppException` with `upstream` set to
the ECB's error. The request gains `'recalculate' => ['boolean']`.

## Copy

| Key                                   | File                 | English                                                                  |
| ------------------------------------- | -------------------- | ------------------------------------------------------------------------ |
| `pricing.rates_unavailable.message`   | `lang/en/errors.php` | Today's exchange rates couldn't be fetched, so nothing was saved.        |
| `pricing.rates_unavailable.resolution` | `lang/en/errors.php` | Try again in a few minutes. The price stays as it was until then.       |

The reader is staff, like the other `pricing` keys.

## Routes

None.

## Tests

**New: `tests/Unit/Support/FixedPricesTest.php` — 4 cases**

1. `test_it_rounds_up_to_a_whole_unit` — 3900 at AUD 1.401044 is 5500, and
   at GBP 0.746562 is 3000.
2. `test_a_figure_just_over_a_whole_unit_rounds_up` — 3900 at NZD 1.743690
   (68.0039) is 6900.
3. `test_a_whole_figure_stays_whole` — 1000 at a rate of 2.000000 is 2000,
   not 2100.
4. `test_it_uses_decimal_arithmetic` — 1000 at a rate of 1.100000 is 1100.
   In floating point, 10 × 1.1 is 11.000000000000002, which a ceiling would
   turn into 1200.

**New: `tests/Feature/Integrations/EuropeanCentralBank/ReferenceRatesTest.php` — 3 cases**

5. `test_it_reads_rates_from_usd_through_the_euro` — `Http::fake()` with the
   fixture; USD to AUD is `1.401044`, and USD to EUR is `0.870322`.
6. `test_the_date_is_the_files_date` — `on` is 2026-09-21.
7. `test_a_currency_the_file_lacks_is_refused` — asking for `XYZ` throws.

**Changed: `tests/Feature/Checkout/PricingModelTest.php` — 5 new cases**

8. `test_saving_a_price_calculates_its_fixed_amounts` — the rates contract is
   faked with the fixture's rates. A staff owner saves Start at 3900; the
   row's `currency_options` is `D-048`'s Start column, and `rates_on` is
   2026-09-21.
9. `test_a_price_is_not_saved_when_the_rates_cannot_be_fetched` — the
   contract throws; errors carry `pricing.rates_unavailable`, and there is no
   row.
10. `test_a_price_is_always_in_the_billing_currency` — posting
    `currency=EUR` still saves USD.
11. `test_amount_in_answers_from_the_row` — `amountIn('AUD')` 5500,
    `amountIn('USD')` 3900, `amountIn('JPY')` null.
12. `test_the_fixed_currencies_include_the_settlement_currency` — the config
    holds `settlement_currency` inside `fixed_currencies`.
13. `test_editing_only_the_words_keeps_the_amounts` — a saved price's tagline
    changes; the rates contract is not called, and the amounts and `rates_on`
    are unchanged.
14. `test_recalculating_fetches_todays_rates` — the same USD amount with
    `recalculate` set; the contract is called and the amounts follow the new
    rates.

Total: 14. `test_saving_the_same_plan_and_interval_updates_in_place` and the
other existing cases post through the faked contract and otherwise pass
unchanged.

## Acceptance

- [ ] Saving Start at US$39 stores `D-048`'s Start column, the rates and their date
- [ ] Rounding is up to a whole unit, in decimal arithmetic
- [ ] A price is never saved when the rates cannot be fetched
- [ ] Editing only a price's words never recalculates it
- [ ] The console takes a USD amount and shows each calculated currency with the rates date
- [ ] `php artisan db:seed --class=PricingSeeder` writes `D-048`'s table
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

- **22 September 2026, before anyone claimed it.** Written that afternoon as
  "A plan's price holds a fixed amount in each major currency" for `D-047`:
  staff typing each currency's amount beside the USD one, and plan coupons
  made percent-off. The same evening `D-048` replaced the typing with a
  calculation from USD, rounded up. The rewritten parts are the title, Why,
  Decisions, Scope, Files, Database, Code, Copy and Tests. The file was
  renamed from `T-169-a-plans-price-holds-a-fixed-amount-in-each-major-currency.md`.
  The coupon rule moved to `T-173`, which creates vouchers in Stripe. It now
  depends on `T-168` too, for `docs/flows/billing.md`.

## Notes

- The ECB publishes once a working day, around 16:00 in Frankfurt. A price
  saved on a weekend uses Friday's rates, and `rates_on` says so.
