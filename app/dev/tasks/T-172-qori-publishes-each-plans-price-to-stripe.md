---
id: T-172
title: Qori publishes each plan's price to Stripe
stream: selling
status: doing
owner: claude
estimate: M
depends: T-169
blocks: T-170, T-173
---

# T-172 — Qori publishes each plan's price to Stripe

## Why

`D-048` makes Qori the source of truth for prices. Today staff create each
price in Stripe's dashboard, then type its `price_…` id into Qori's console.
Once `T-169` calculates six currencies per price, typing them again in Stripe
is where Qori's page and Stripe's charge come to disagree.

Afterwards, saving a price in Qori creates the Stripe price itself:

- AUD as its default currency, at the calculated amount;
- every other fixed currency, and USD, as currency options;
- the price it replaces archived, and the new id stored.

Staff never enter an id, and the hybrid can be checked end to end in the
sandbox.

## Decisions taken to make this specifiable

- **A contract in Qori's terms, `App\Integrations\Contracts\PublishesPricing`,
  implemented by `App\Integrations\Stripe\Pricing`**, bound in
  `IntegrationServiceProvider`. It has two methods, `publishPrice()` and
  `retirePrice()`. `T-173` adds the voucher methods to the same contract.
- **One Stripe product per plan, with a fixed id: `qori_plan_<plan>`**, for
  example `qori_plan_start`. Stripe accepts an id when a product is created.
  Publishing reads `GET /v1/products/qori_plan_<plan>`, and creates the
  product only on a 404, named after the row's `name`. So a plan never gets a
  second product, and Qori stores no product id.
- **The Stripe price**, created with `POST /v1/prices`:
  - `currency`: `qori.billing.settlement_currency`, lower-cased (`aud`);
  - `unit_amount`: `currency_options['AUD']`;
  - `currency_options[<cur>][unit_amount]` for every other entry of
    `currency_options`, plus `currency_options[usd][unit_amount]` =
    `amount_cents`;
  - `recurring[interval]`: the row's interval; `product`: the plan's product;
  - `lookup_key`: `qori_<plan>_<interval>`, with `transfer_lookup_key=true`;
  - `nickname`: the row's `name`;
  - `metadata[qori_price_id]` and `metadata[rates_on]`.

  `tax_behavior` is left unset until Qori registers for tax (`T-168`,
  release checklist).
- **Every create sends an `Idempotency-Key`.** `Client::getClientV1()` retries
  twice, and a retried create without a key could leave two live prices. The
  key is `qori-price-` followed by a hash of the request body, so the same
  price asked for twice is one price.
- **A price is saved only once Stripe has accepted it.** The row's id is
  assigned before publishing, so the metadata can carry it. Stripe is called
  first, and the row is written with the new `stripe_price_id` only after
  Stripe accepts. On a refusal nothing is saved, and the console shows
  `errors.pricing.publish_failed`, with Stripe's error in `upstream`. A row
  never points at a price Stripe does not have.
- **Qori publishes only when an amount or the interval changes.** Editing only
  the words keeps the Stripe price (`T-169` keeps the amounts too). A new
  price, a changed USD amount, or a recalculation publishes.
- **The replaced price is archived after the new one is saved**, with
  `active=false`. If archiving fails, the new id stays saved and the failure
  is logged. A price archived late is harmless: nothing in Qori points at it,
  and its lookup key has already moved.
- **Existing subscribers stay where they are** (`D-048`). An archived price
  stops new purchases and leaves the subscriptions on it running. The spike
  confirms this.
- **Retiring a row in Qori archives its Stripe price.**
- **The console's `stripe_price_id` input goes.** The id shows read-only in
  the list.
- **Seeders never publish.** The design fixtures keep their fake ids. Each
  environment publishes with its own key, so the sandbox and live each get
  their own prices, and live prices are published from the production
  console.

## Preconditions

**Data this task verifies against:** the seeded prices, and a local Group
owned by a user.

**Equipment:**

- The Stripe sandbox, with `STRIPE_SECRET` in `.env`.
- **Adaptive Pricing switched on in the sandbox** (Settings → Adaptive
  Pricing). It is an account setting, so the owner switches it on: asked 22
  September 2026, and the owner confirmed it on the same evening. Stripe keeps
  the setting separately for the sandbox and live, so if the check shows AUD
  where yen is expected, the sandbox's setting is the first thing to look at.
- `stripe listen --forward-to localhost:8001/webhooks/stripe` running.
- A browser signed in to `/admin` as a staff owner.

**Spike: the hybrid, end to end in the sandbox.** Record each step in the
report.

1. Save Start at US$39 in the local console. `T-169` calculates it, and this
   task publishes it. Read it back with
   `stripe prices retrieve <id> -d "expand[]=currency_options"` and keep the
   body of the create response as
   `tests/Fixtures/stripe/price-created-start.json`.
2. Subscribe a Group whose sandbox customer was created with the email
   `test+location_US@example.com`. Stripe's page shows US$39.00, the fixed
   price.
3. Do the same with `test+location_JP@example.com`. Stripe's page shows yen
   converted from A$55: Adaptive Pricing.
4. Change Start to US$45. A new price exists, the old one is archived, and the
   subscription from step 2 still shows US$39 on its upcoming invoice.

## Scope

**In:**

- The contract, `Stripe\Pricing`, the product and price calls, archiving, and
  the idempotency key.
- The console saving through Stripe, and the `stripe_price_id` input going.
- Retiring a row archiving its price.
- `docs/flows/billing.md`: the price list is published from Qori.

**Out:**

- Vouchers in Stripe: `T-173`.
- Moving existing subscribers onto a new price (`D-048`: a separate decision).
- Adding new prices to the Customer Portal's plan-switching list. The portal
  does not switch plans today. When it does, each published price has to be
  offered there too.
- Tax behaviour on the prices: release checklist, before `T-168`'s switch
  goes on.

## Files

| Path | Change | Notes |
| ---- | ------ | ----- |
| `app/Integrations/Contracts/PublishesPricing.php` | new | `publishPrice()`, `retirePrice()` |
| `app/Integrations/Stripe/Pricing.php` | new | products, prices, archiving |
| `app/Providers/IntegrationServiceProvider.php` | edit | binds the contract |
| `app/Http/Controllers/Admin/PricingController.php` | edit | publishes before saving; retiring archives |
| `app/Http/Requests/Admin/StoreSubscriptionPriceRequest.php` | edit | `stripe_price_id` is no longer an input |
| `resources/js/pages/admin/Pricing.vue` | edit | the id read-only |
| `lang/en/errors.php` | edit | `pricing.publish_failed` |
| `docs/flows/billing.md` | edit | the price list is published from Qori |
| `tests/Fixtures/stripe/price-created-start.json`, `tests/Fixtures/stripe/README.md` | new, edit | the observed create response and its row |
| `tests/Feature/Integrations/Stripe/PricingTest.php` | new | |
| `tests/Feature/Checkout/PricingModelTest.php` | edit | |

## Database

None. `stripe_price_id` exists; Qori now writes it.

## Code

```php
namespace App\Integrations\Contracts;

interface PublishesPricing
{
    /** Creates the price at the vendor and returns its id. */
    public function publishPrice(SubscriptionPrice $price): string;

    public function retirePrice(string $vendorPriceId): void;
}
```

`App\Integrations\Stripe\Pricing` implements it on `Client::getClientV1()`,
sending `Idempotency-Key` on every `POST` that creates.
`PricingController::storePrice()` and `retirePrice()` take `PublishesPricing`
by method injection.

## Copy

| Key                                  | File                 | English                                                              |
| ------------------------------------ | -------------------- | -------------------------------------------------------------------- |
| `pricing.publish_failed.message`     | `lang/en/errors.php` | The payment provider didn't accept this, so nothing was saved.      |
| `pricing.publish_failed.resolution`  | `lang/en/errors.php` | Try again. If it keeps failing, the logs say what was refused.      |

The reader is staff. The copy names no vendor (`D-035`), even here.

## Routes

None.

## Tests

**New: `tests/Feature/Integrations/Stripe/PricingTest.php` — 6 cases**

1. `test_it_creates_the_plans_product_the_first_time` — the product `GET`
   answers 404; one `POST /v1/products` with `id=qori_plan_start`.
2. `test_it_reuses_the_plans_product` — the `GET` answers 200; no product is
   created.
3. `test_the_price_is_based_in_the_settlement_currency_with_every_other_as_an_option`
   — the body carries `currency=aud`, `unit_amount=5500`,
   `currency_options[usd][unit_amount]=3900`,
   `currency_options[eur][unit_amount]=3400`, `recurring[interval]=month`,
   `lookup_key=qori_start_month` and `transfer_lookup_key=true`. The faked
   response is the fixture.
4. `test_every_create_carries_an_idempotency_key` — present on the product and
   price `POST`s, and the same for the same body.
5. `test_it_returns_the_new_prices_id` — the id from the fixture.
6. `test_retiring_archives_the_price` — `POST /v1/prices/{id}` with
   `active=false`.

**Changed: `tests/Feature/Checkout/PricingModelTest.php` — 5 new cases**

7. `test_saving_a_price_publishes_it_and_stores_the_id` — the contract is
   faked, and the row holds the id it returned.
8. `test_a_price_is_not_saved_when_the_vendor_refuses_it` — the contract
   throws; there is no row, and errors carry `pricing.publish_failed`.
9. `test_changing_the_amount_publishes_a_new_price_and_retires_the_old` — the
   fake records `retirePrice(<old id>)`.
10. `test_editing_only_the_words_does_not_republish` — a tagline change; the
    contract is not called.
11. `test_retiring_a_row_retires_its_price`.

Total: 11.

## Acceptance

- [ ] The spike ran, and each of its four steps is recorded: fixed USD for the US customer, yen for the Japanese one, the old subscription unmoved
- [ ] Saving a price creates it in Stripe with AUD as its default and every other currency as an option, and stores the id
- [ ] A refused publish saves nothing; a words-only edit publishes nothing
- [ ] Staff can no longer type a `price_…` id
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

- Written 22 September 2026 from `D-048`, the owner's "can the stripe pricing
  be injected from Qori and Qori is the source of truth?". Stripe's price
  update allows only `active`, `currency_options`, `lookup_key`, `metadata`,
  `nickname`, `tax_behavior` and `transfer_lookup_key`
  ([Stripe](https://docs.stripe.com/api/prices/update)). The currency options
  could be changed in place, but this task always creates a new price, so
  there is never a question of which subscribers pay which amount.
