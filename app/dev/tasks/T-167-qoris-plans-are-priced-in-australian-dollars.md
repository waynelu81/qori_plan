---
id: T-167
title: Qori's plans are priced in Australian dollars
stream: selling
status: ready
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-167 — Qori's plans are priced in Australian dollars

## Why

`D-046` prices Start and Pro in AUD because that is what Qori's Stripe account
settles in, and Adaptive Pricing only converts a price in that currency. Three
places still assume USD:

- the console's new-price form fills in `USD`;
- `StoreSubscriptionPriceRequest` falls back to `USD` when the field is
  missing;
- `PricingSeeder` writes US$19 and US$49 design fixtures.

A staff member following the form would save a USD row beside an AUD Stripe
price, and the billing page would quote the wrong currency. Nobody has yet seen
Adaptive Pricing run through Qori's checkout.

Afterwards:

- the console defaults to AUD;
- the fixtures show `D-046`'s prices;
- one sandbox subscription paid in USD has proved the plan is still granted.

## Decisions taken to make this specifiable

- **Qori's billing currency is its own key, `qori.billing.currency`, not
  `qori.payments.default_currency`.** The second is the default for a Series
  price on the creator's own Stripe account (`SeriesController` reads it). The
  first is the settlement currency of Qori's own account. They match today by
  coincidence, and a creator-facing default must not change because Qori's
  account did.
- **The currency field stays editable and is not restricted to AUD.** Stripe's
  price is the authority and the row mirrors it. Refusing other currencies
  would not catch a wrong amount either, and it would have to be undone if
  Stripe later lets the account settle in USD.
- **The design fixtures take `D-046`'s monthly prices, A$55 and A$139, and get
  no annual row.** A design review then shows the price a creator will see.
  Annual waits until retention is understood (the 11 September review, §5).
- **An Adaptive-Priced subscription is proved with a payload Stripe actually
  sent, not with the documentation.** The spike keeps the
  `customer.subscription.created` object Stripe sends when someone pays in USD
  for an AUD price, and a test runs it through
  `BillingService::applySubscription()`. Qori reads the plan from `metadata`
  and the period end from the item, so nothing should change. The test keeps
  it that way.
- **The buyer's country is forced through the customer's email, as Stripe's
  testing guide does it** (`test+location_US@example.com`). Qori's own
  customers carry no email by design (`Subscription::customerFor()`). So the
  spike creates that customer in the sandbox by hand and puts its id on a local
  Group; no code changes for it.

## Preconditions

**Data this task verifies against:**

- A local Group, owned by a user, whose `stripe_customer_id` is a sandbox
  customer created with the email `test+location_US@example.com`.
- The local `start` monthly row, with `stripe_price_id` set to a sandbox price
  of A$55 a month.

**Equipment:**

- The Stripe sandbox with **Adaptive Pricing switched on** (Settings →
  Adaptive Pricing). This is an account setting, so the owner switches it on;
  _asked_ 22 September 2026.
- `stripe listen --forward-to localhost:8001/webhooks/stripe` running, with
  its secret in `.env`.
- A browser.

**Spike.** Nobody has observed an Adaptive-Priced subscription, so the first
step is to produce one:

1. Create the A$55 monthly price on the sandbox Start product.
2. Subscribe the Group from `/g/{group}/billing`.
3. Confirm that Stripe's page shows USD.
4. Pay with `4242 4242 4242 4242`.
5. Keep the `data.object` of the `customer.subscription.created` event that
   reached the webhook (`stripe events list --type
   customer.subscription.created --limit 1`).

## Scope

**In:**

- `qori.billing.currency`, set to `AUD`. The console form reads it, and so does
  `StoreSubscriptionPriceRequest` when the field is missing.
- `PricingSeeder`'s Start and Pro rows in AUD, at 5500 and 13900 cents.
- The spike above, its payload as a fixture, and a test that the payload
  grants Start.

**Out:**

- Creating the live prices, switching Adaptive Pricing on in live mode, and
  entering the live rows. These are release checklist (`D-046`, `release-prerequisites.md`).
- Showing a buyer abroad an estimate in their own currency on `/pricing` or the
  billing page. `formatMoney()` already writes `A$55` for a reader outside
  Australia; an estimate needs a source of exchange rates and is a product
  call nobody has asked for.
- Plan switching in the Customer Portal. It is not configured in the sandbox,
  so there is nothing to switch. When it is configured, run the same check on
  a switch.
- Coupons. An amount-off coupon carries its own currency and the console
  already requires one (`StoreSubscriptionCouponRequest`); staff enter AUD. A
  percent-off coupon has no currency.
- Tax: `T-168`.

## Files

| Path                                                         | Change | Notes                               |
| ------------------------------------------------------------ | ------ | ----------------------------------- |
| `config/qori.php`                                            | edit   | `billing.currency`, with its reason |
| `app/Http/Requests/Admin/StoreSubscriptionPriceRequest.php`  | edit   | falls back to the config value      |
| `app/Http/Controllers/Admin/PricingController.php`           | edit   | the `defaultCurrency` prop          |
| `resources/js/pages/admin/Pricing.vue`                       | edit   | the field's value from the prop     |
| `database/seeders/PricingSeeder.php`                         | edit   | AUD, 5500, 13900                    |
| `tests/Fixtures/stripe/subscription-adaptive-pricing-usd.json` | new  | the observed object                 |
| `tests/Fixtures/stripe/README.md`                            | edit   | its row                             |
| `tests/Feature/Checkout/AdaptivePricingTest.php`             | new    |                                     |
| `tests/Feature/Checkout/PricingModelTest.php`                | edit   | two cases                           |

Flows: none — no call chain changes; only the form's default currency moves into config.

## Database

None.

## Code

```php
// config/qori.php — a new top-level section after 'payments'
'billing' => [
    // What Qori's own plans are priced in: the settlement currency of its
    // Stripe account, which Adaptive Pricing requires before it shows a
    // buyer abroad their own currency (D-046).
    'currency' => 'AUD',
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

`PricingSeeder::plans()`: `1900` becomes `5500`, `4900` becomes `13900`, and
`'currency' => 'USD'` becomes `'currency' => 'AUD'`. The ids and the fake
`price_designreview…` ids are unchanged.

## Copy

None. The console's labels are unchanged, and Stripe's page is Stripe's.

## Routes

None.

## Tests

**New: `tests/Feature/Checkout/AdaptivePricingTest.php` — 1 case**

1. `test_a_subscription_paid_in_another_currency_grants_its_plan` — loads
   `subscription-adaptive-pricing-usd.json`, points its `metadata.group_id` at
   a factory Group on `free`, and runs it through
   `BillingService::applySubscription()`. Asserts that the plan is `start` and
   that `subscription_ends_at` is the first item's `current_period_end`.

**Changed: `tests/Feature/Checkout/PricingModelTest.php` — 2 new cases**

2. `test_a_price_saved_without_a_currency_is_in_the_billing_currency` — a staff
   owner posts to `/admin/pricing/prices` with no `currency`; the row's
   currency is `AUD`.
3. `test_the_console_offers_the_billing_currency` — `GET /admin/pricing` as a
   staff owner; the `defaultCurrency` prop is `AUD`.

Total: 3. The existing cases post `'currency' => 'USD'` explicitly and pass
unchanged: the field is not restricted.

## Acceptance

- [ ] The spike ran: Stripe's page showed USD for the `location_US` customer, and the subscription granted Start locally
- [ ] `subscription-adaptive-pricing-usd.json` holds the observed object, redacted by role, with its row in the fixtures README
- [ ] The console's new-price form fills in AUD, and a price saved without a currency is AUD
- [ ] `php artisan db:seed --class=PricingSeeder` writes Start at A$55 and Pro at A$139
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

- Written 22 September 2026 from `D-046`. The USD defaults were found while
  writing it: `Pricing.vue` has `value="USD"`, and
  `StoreSubscriptionPriceRequest::prepareForValidation()` falls back to
  `'USD'`.
- `T-164` (done the same day) wrote `tests/Fixtures/stripe/README.md` and its
  first five rows. Add this task's row below them, following that README's
  rules on redaction.
