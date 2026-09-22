---
id: T-170
title: Qori's pages and checkout use the visitor's currency
stream: selling
status: doing
owner: claude
estimate: M
depends: T-168, T-169, T-172
blocks: none
---

# T-170 — Qori's pages and checkout use the visitor's currency

## Why

`D-048`: a buyer whose currency has a fixed price pays that price. Anyone
else pays in their own currency, converted from the AUD price by Adaptive
Pricing. Today Qori cannot say which applies:

- `/pricing` and `/g/{group}/billing` quote each row's `amount_cents` in USD
  to everyone;
- the checkout names no currency, so Stripe picks one on its own page from
  where the buyer is.

A visitor in Germany would read US$39 on Qori's page and meet €34 on Stripe's.
The owner asked for the opposite: "make sure the price is same when they
landed in stripe page".

Afterwards:

- both pages offer USD, EUR and AUD, plus the visitor's own currency when it
  is none of those, with the visitor's own selected;
- a fixed currency shows its fixed price, and the checkout names it, so
  Stripe charges exactly what the page showed;
- a currency without a fixed price shows the USD price with a line saying
  checkout charges their own currency, and the checkout names none, so
  Adaptive Pricing converts.

## Decisions taken to make this specifiable

- **The pages offer USD, EUR and AUD always, plus the visitor's own currency
  when it is none of those three.** The owner, 22 September 2026: "I would
  show 3 fixed currency + visitor's country if different from 3, USD EUR
  AUD". The three are `qori.billing.offered_currencies`, a subset of the
  fixed currencies. The fourth option can be a fixed currency, for example
  GBP from the UK, or one without a fixed price, for example JPY from Japan.
- **The visitor's own currency is selected first.** A visitor Qori cannot
  place gets USD, and no fourth option.
- **A fixed currency shows its fixed price.** The subscribe link carries it
  (`?currency=GBP`), and the checkout names it (`currency=gbp` on the
  Checkout Session). Stripe localises only a session that names no currency,
  so naming one is what guarantees Stripe's page shows Qori's figure
  (`D-047`).
- **A currency without a fixed price shows the USD price, with
  `billing.currency.converted` beneath it.** The owner, 22 September 2026,
  "Yes", to "US$39 with a line saying checkout charges their own currency".
  The subscribe link carries no currency, and the checkout names none, so
  Adaptive Pricing converts from AUD (`D-048`). The line says "where
  possible", because Adaptive Pricing does not reach every country; Stripe
  shows AUD to a buyer it cannot convert for.
- **Switching currency happens in the page.** The props carry every offered
  plan's amounts, so the menu only changes which one shows. Nothing is
  remembered between pages: the billing page, after sign-in, selects the
  visitor's own currency again.
- **A country's currency comes from ICU, not from a hand-kept map.** For
  country `XX`, the currency is `NumberFormatter` on locale `en_XX`, read with
  `getTextAttribute(NumberFormatter::CURRENCY_CODE)`. Checked on 22 September
  2026: JP gives JPY, DE gives EUR, GB gives GBP, NG gives NGN.
- **The country comes from Cloudflare's `CF-IPCountry` header, and failing
  that from the browser's language.**
  - `App\Integrations\Cloudflare\VisitorCountry` implements
    `App\Integrations\Contracts\LocatesVisitors` and reads the header from the
    headers it is handed. It returns null for Cloudflare's `XX` (unknown) and
    `T1` (Tor).
  - `App\Support\VisitorCurrency` falls back to the region of the first
    `Accept-Language` tag, for example `en-GB`.
  - Both always run; the first spike records which one production uses. A
    spoofed header only changes which currency is selected first. Every fixed
    price is rounded up from the USD figure, so no choice costs less than USD.
- **`BillsGroups::subscribeUrl()` gains `?string $currency`**, last, after the
  coupon. `BillingService::subscribe()` passes it through, and
  `Subscription::subscribeUrl()` adds `currency` in lower case when it is not
  null. `BillingController::subscribe()` reads `currency` the way it already
  reads `coupon`. A value that is not one of the row's `fixedCurrencies()`
  becomes null, which is not an error: it is the Adaptive Pricing path.
- **Plan coupons work in any currency**: `T-173` makes them percent-off.

## Preconditions

**Data this task verifies against:** the seeded prices, with `T-169`'s fixed
amounts (`php artisan db:seed --class=PricingSeeder`), and a local Group owned
by a user.

**Equipment:**

- The Stripe sandbox, with Start published by `T-172`.
- Adaptive Pricing switched on. The owner confirmed it is on, 22 September
  2026; the sandbox's own setting is the one this check needs.
- `stripe listen` running.
- A browser.

**Spikes, run first:**

1. **Does Cloudflare's country header reach the app?** Read one production
   request's headers, from Laravel Cloud's logs or a temporary log line
   removed in the same task. Record which path production uses. Both paths are
   built either way.
2. **What a named-currency subscription looks like.** In the sandbox:
   1. Subscribe from the billing page with EUR selected. Confirm Stripe's page
      shows €34 whatever the location. Keep the `customer.subscription.created`
      object as `tests/Fixtures/stripe/subscription-fixed-eur.json`.
   2. Subscribe a Group whose sandbox customer was created with
      `test+location_JP@example.com`, with its own currency selected. Confirm
      yen, and keep the object as
      `tests/Fixtures/stripe/subscription-adaptive-jpy.json`.
   3. Record whether a customer that has paid in one currency can later start
      a subscription in another. Stripe has limited a customer to one
      currency, and a Group that moves country would hit that.

## Scope

**In:**

- `LocatesVisitors`, the Cloudflare reader, the `Accept-Language` fallback,
  `VisitorCurrency`, `CurrencyOffer`, and `SubscriptionPrice::amountsFor()`.
- The currency menu on `/pricing` and `/g/{group}/billing`, and the converted
  line.
- The subscribe link carrying `currency`, and the checkout naming a fixed one.
- The two fixtures and their tests.
- `docs/flows/billing.md`: how the currency is picked and named.

**Out:**

- Creating the prices in Stripe: `T-172`. The live ones are published from
  the production console (release checklist).
- Carrying the chosen currency through registration. The billing page selects
  the visitor's own currency again.
- Plan switching in the Customer Portal. A subscription keeps its currency,
  and switching to a price without that option is Stripe's to refuse. Check
  it once the portal offers switching.
- Tax: `T-168`. Once Stripe Tax calculates, every currency option needs a tax
  behaviour (`D-047`, release checklist).

## Files

| Path | Change | Notes |
| ---- | ------ | ----- |
| `app/Integrations/Contracts/LocatesVisitors.php` | new | `countryFrom(array $headers): ?string` |
| `app/Integrations/Cloudflare/VisitorCountry.php` | new | reads `CF-IPCountry` |
| `app/Providers/IntegrationServiceProvider.php` | edit | binds it |
| `app/Support/VisitorCurrency.php` | new | the offer for a request |
| `app/Data/CurrencyOffer.php` | new | offered, selected, converted |
| `app/Models/SubscriptionPrice.php` | edit | `amountsFor(CurrencyOffer $offer)` |
| `config/qori.php` | edit | `billing.offered_currencies` |
| `app/Integrations/Contracts/BillsGroups.php` | edit | `subscribeUrl()` takes the currency |
| `app/Integrations/Stripe/Subscription.php` | edit | `currency` on the session |
| `app/Services/BillingService.php` | edit | passes it through |
| `app/Http/Controllers/PricingController.php` | edit | the offer and the amounts |
| `app/Http/Controllers/Share/BillingController.php` | edit | the same; reads `currency` on subscribe |
| `resources/js/components/billing/CurrencyPicker.vue` | new | the menu |
| `resources/js/pages/Pricing.vue` | edit | the menu, the amounts, the line, the link |
| `resources/js/pages/share/Billing.vue` | edit | the same |
| `lang/en/billing.php` | edit | the label and the line |
| `docs/flows/billing.md` | edit | the currency's path |
| `tests/Fixtures/stripe/subscription-fixed-eur.json`, `tests/Fixtures/stripe/subscription-adaptive-jpy.json` | new | the observed objects |
| `tests/Fixtures/stripe/README.md` | edit | their rows |
| `tests/Feature/Checkout/VisitorCurrencyTest.php` | new | |
| `tests/Feature/Integrations/Cloudflare/VisitorCountryTest.php` | new | |
| `tests/Feature/Checkout/SubscriptionTest.php` | edit | the currency on the session |

## Database

None.

## Code

```php
// config/qori.php, in the 'billing' section
// Offered on the pricing and billing pages beside the visitor's own currency
// (D-048). Each must be in fixed_currencies or be `currency` itself.
'offered_currencies' => ['USD', 'EUR', 'AUD'],
```

```php
namespace App\Integrations\Contracts;

interface LocatesVisitors
{
    /** @param array<string, list<string>|string> $headers  @return ?string ISO 3166 alpha-2, upper case */
    public function countryFrom(array $headers): ?string;
}

namespace App\Data;

final class CurrencyOffer
{
    /** @param list<string> $currencies in display order: the offered three, then the visitor's own */
    public function __construct(
        public array $currencies,
        public string $selected,
        public ?string $converted, // the visitor's own currency when it has no fixed price
    ) {}
}

namespace App\Support;

final class VisitorCurrency
{
    public function __construct(private LocatesVisitors $locator) {}

    public function offer(Request $request): CurrencyOffer;
}

namespace App\Models;

class SubscriptionPrice extends Model
{
    /** @return array<string, int> cents for each offered currency that has a fixed price here */
    public function amountsFor(CurrencyOffer $offer): array;
}
```

```php
// BillsGroups::subscribeUrl(), with the new last parameter
public function subscribeUrl(
    Group $group,
    string $plan,
    string $successUrl,
    string $cancelUrl,
    ?SubscriptionCoupon $coupon = null,
    ?string $currency = null,
): HostedCheckout;
```

Both pages gain the props `currencies` (a list of `{ code, fixed }`),
`selectedCurrency`, and `convertedLine` (the filled `billing.currency.converted`
line, or null). Each plan gains `amounts`, from `amountsFor()`.
`CurrencyPicker.vue` names each option with the browser's
`Intl.DisplayNames(undefined, { type: 'currency' })`, so no currency name is
written in copy.

## Copy

| Key                         | File                  | English                                                                                                   |
| --------------------------- | --------------------- | --------------------------------------------------------------------------------------------------------- |
| `billing.currency.label`    | `lang/en/billing.php` | Currency                                                                                                  |
| `billing.currency.converted` | `lang/en/billing.php` | At checkout you'll pay in :currency where possible, converted at the day's rate plus a conversion fee.  |

`:currency` is the ISO code, for example `JPY`. The pages receive both lines
as props, as `BillingController` already does for `billing.limits`.

## Routes

None new. `share.billing.subscribe` gains the `currency` query field, read
like `coupon`.

## Tests

**New: `tests/Feature/Checkout/VisitorCurrencyTest.php` — 11 cases**

1. `test_a_visitor_from_the_uk_is_offered_gbp_beside_the_three` —
   `CF-IPCountry: GB`; currencies USD, EUR, AUD and GBP; GBP selected; no
   converted line.
2. `test_a_visitor_from_germany_is_offered_the_three_with_eur_selected` — DE;
   no fourth option.
3. `test_a_visitor_from_japan_is_offered_yen_as_converted` — JP; JPY fourth
   and selected; the converted line names JPY; the plan shows its USD amount.
4. `test_an_unplaced_visitor_gets_usd` — no header, no `Accept-Language`; the
   three, USD selected.
5. `test_the_browser_language_places_a_visitor_without_the_header` —
   `Accept-Language: en-GB`; GBP selected.
6. `test_the_pricing_page_carries_each_plans_amounts` — Start's `amounts`
   are USD 3900, EUR 3400, AUD 5500, plus GBP 3000 for a UK visitor.
7. `test_the_billing_page_offers_the_same` — as the owner of a Group, on
   `/g/{group}/billing`.
8. `test_subscribing_in_a_fixed_currency_names_it_at_checkout` —
   `?currency=GBP`; the session body carries `currency=gbp`.
9. `test_subscribing_in_any_other_currency_names_none` — `?currency=JPY`, and
   no `currency` at all; the body has no `currency`.
10. `test_a_fixed_currency_subscription_grants_its_plan` — the EUR fixture
    through `BillingService::applySubscription()`.
11. `test_a_converted_subscription_grants_its_plan` — the JPY fixture.

**New: `tests/Feature/Integrations/Cloudflare/VisitorCountryTest.php` — 2 cases**

12. `test_it_reads_the_country_header` — `cf-ipcountry: gb` gives `GB`.
13. `test_unknown_and_tor_are_no_country` — `XX` and `T1` give null.

**Changed: `tests/Feature/Checkout/SubscriptionTest.php`**: the existing
subscribe cases pass unchanged; the currency cases are 8 and 9 above.

Total: 13.

## Acceptance

- [ ] Both spikes ran and are recorded: which path production uses to place a visitor, both fixtures, and whether a customer can change currency
- [ ] A visitor from a country with a fixed price sees that price on `/pricing` and on the billing page, and Stripe's page shows the same figure
- [ ] USD, EUR and AUD are always offered, and the visitor's own currency beside them when it is none of those
- [ ] A visitor whose currency has no fixed price sees the USD price and the converted line, and Stripe's page shows their currency
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

- Written 22 September 2026 from `D-047`. The owner's question that shaped
  it: "How did Qori knows the country right now? Is that something we can ask
  stripe first so make sure the price is same when they landed in stripe
  page?" Qori does not know the country today. Stripe cannot be asked in
  advance, but it can be told.
- `D-048`, the same evening, brought Adaptive Pricing back for currencies
  without a fixed price. Naming the currency became something the checkout
  does only for a fixed one.
- **An Adaptive-priced renewal can charge a different amount** (`T-172`'s
  sandbox check, 22 September 2026). Stripe's page for a Japanese buyer read
  "1 AUD = 116.3961 JPY. Charges will vary based on exchange rates", and its
  terms "charge you in JPY at the displayed exchange rate or the exchange rate
  at the time of billing". The ECB's mid-rate that day was about 112.25, so
  the rate carries Stripe's conversion fee, as `D-046` says. The converted line
  should not suggest the yen figure is fixed: its wording is this task's to
  settle when it is built.
- Brought to ready the same evening with the owner's two answers, asked
  22 September 2026 and answered then:
  - the menu: "I would show 3 fixed currency + visitor's country if different
    from 3, USD EUR AUD";
  - a visitor without a fixed price: "Yes" to the USD price with a line.

  The reading written into Decisions: the three always, the visitor's own
  fourth and selected, a fixed fourth shown at its price, and one without a
  fixed price shown in USD with the line.
