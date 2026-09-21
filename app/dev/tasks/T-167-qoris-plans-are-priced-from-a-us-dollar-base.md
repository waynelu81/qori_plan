---
id: T-167
title: Qori's plans are priced from a US dollar base
stream: selling
status: ready
owner: unassigned
estimate: S
depends: none
blocks: T-169
---

# T-167 — Qori's plans are priced from a US dollar base

## Why

`D-047` makes USD the default currency of every plan's Stripe price. It is
what the prices were planned in, and what a buyer pays when their own currency
has no fixed price. The code already speaks USD, but only by accident:

- the literal `'USD'` is written into the console's new-price form;
- it is the fallback in `StoreSubscriptionPriceRequest` when the field is
  missing;
- the design fixtures in `PricingSeeder` are US$19 and US$49 placeholders,
  not the planned US$39 and US$99.

`T-169` needs the base currency in one place, to refuse a fixed amount in it,
and so does `T-170`, to fall back to it.

Afterwards:

- `qori.billing.currency` is that one place;
- the console and the request both read it;
- the fixtures carry US$39 and US$99.

## Decisions taken to make this specifiable

- **Qori's billing currency is its own key, `qori.billing.currency`, not
  `qori.payments.default_currency`.** The second is the default for a Series
  price on the creator's own Stripe account (`SeriesController` reads it), and
  it is AUD. The first is the default currency of Qori's own plan prices. They
  answer different questions, and a creator-facing default must not change
  because Qori's pricing did.
- **The currency field stays editable and is not restricted to the base.**
  Stripe's price is the authority and the row mirrors it. Refusing other
  currencies would not catch a wrong amount either.
- **The design fixtures take the planned monthly prices, US$39 and US$99, and
  get no annual row.** A design review then shows the price a creator will see.
  Annual waits until retention is understood (the 11 September review, §5).
- **No sandbox check here.** This task was first written with an Adaptive
  Pricing check, and Adaptive Pricing is off under `D-047`. The check that a
  subscription paid in a fixed currency still grants its plan belongs to
  `T-170`, where the checkout first names a currency.

## Preconditions

**Data this task verifies against:** a clean database.

**Equipment:** none.

## Scope

**In:**

- `qori.billing.currency`, set to `USD`. The console form reads it, and so
  does `StoreSubscriptionPriceRequest` when the field is missing.
- `PricingSeeder`'s Start and Pro rows at 3900 and 9900 cents, in
  `qori.billing.currency`.

**Out:**

- Fixed amounts in the major currencies: `T-169`.
- Quoting the visitor's currency on Qori's pages, and naming it at checkout:
  `T-170`.
- Plan coupons: `T-169` makes them percent-off.
- Creating the live prices and entering the live rows: release checklist
  (`release-prerequisites.md`, `D-047`).
- Tax: `T-168`.

## Files

| Path                                                        | Change | Notes                               |
| ----------------------------------------------------------- | ------ | ----------------------------------- |
| `config/qori.php`                                           | edit   | `billing.currency`, with its reason |
| `app/Http/Requests/Admin/StoreSubscriptionPriceRequest.php` | edit   | falls back to the config value      |
| `app/Http/Controllers/Admin/PricingController.php`          | edit   | the `defaultCurrency` prop          |
| `resources/js/pages/admin/Pricing.vue`                      | edit   | the field's value from the prop     |
| `database/seeders/PricingSeeder.php`                        | edit   | 3900 and 9900 in the config currency |
| `tests/Feature/Checkout/PricingModelTest.php`               | edit   | two cases                           |

Flows: none — no call chain changes; only the base currency moves into config.

## Database

None.

## Code

```php
// config/qori.php — a new top-level section after 'payments'
'billing' => [
    // The default currency of every plan's Stripe price: what the prices are
    // planned in, and what a buyer pays when their own currency has no fixed
    // price (D-047).
    'currency' => 'USD',
],
```

```php
// StoreSubscriptionPriceRequest::prepareForValidation()
$this->merge(['currency' => mb_strtoupper((string) $this->input('currency', config('qori.billing.currency')))]);

// PricingController::index() — one more prop
'defaultCurrency' => (string) config('qori.billing.currency'),
```

`admin/Pricing.vue` gains the prop `defaultCurrency: string`, and the currency
input's `value="USD"` becomes `:value="defaultCurrency"`.

`PricingSeeder::plans()`: `1900` becomes `3900`, `4900` becomes `9900`, and
`'currency' => 'USD'` becomes `'currency' => config('qori.billing.currency')`.
The row ids and the fake `price_designreview…` ids are unchanged.

## Copy

None. The console's labels are unchanged.

## Routes

None.

## Tests

**Changed: `tests/Feature/Checkout/PricingModelTest.php` — 2 new cases**

1. `test_a_price_saved_without_a_currency_is_in_the_billing_currency` — with
   `config(['qori.billing.currency' => 'EUR'])`, so the test cannot pass on
   the old literal, a staff owner posts to `/admin/pricing/prices` with no
   `currency`; the row's currency is `EUR`.
2. `test_the_console_offers_the_billing_currency` — with the same config,
   `GET /admin/pricing` as a staff owner; the `defaultCurrency` prop is `EUR`.

Total: 2. The existing cases post `'currency' => 'USD'` explicitly and pass
unchanged.

## Acceptance

- [ ] The console's new-price form and a price saved without a currency both take `qori.billing.currency`
- [ ] `php artisan db:seed --class=PricingSeeder` writes Start at US$39 and Pro at US$99
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

- **22 September 2026, before anyone claimed it.** Written that morning as
  "Qori's plans are priced in Australian dollars" for `D-046`: an AUD base, a
  console defaulting to AUD, A$55 and A$139 fixtures, and a sandbox check that
  an Adaptive-Priced subscription still grants its plan. The same afternoon,
  `D-047` moved the base to USD, gave the major currencies fixed prices, and
  switched Adaptive Pricing off. Everything was rewritten except the config key
  and the console wiring: the title, Why, the Decisions on fixtures and on the
  check, Preconditions, Scope, Files and Tests. The file was renamed from
  `T-167-qoris-plans-are-priced-in-australian-dollars.md`, and the fixed
  amounts went to `T-169`.

## Notes

- The USD literals were found while writing the first version:
  `Pricing.vue` has `value="USD"`, and
  `StoreSubscriptionPriceRequest::prepareForValidation()` falls back to
  `'USD'`.
