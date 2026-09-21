---
id: T-170
title: Qori's pages and checkout use the visitor's currency
stream: selling
status: draft
owner: unassigned
estimate: M
depends: T-168, T-169
blocks: none
---

# T-170 — Qori's pages and checkout use the visitor's currency

## Why

`D-047`: a buyer pays the fixed price in their own currency if it has one, and
the USD price otherwise. Today Qori cannot say which that is:

- `/pricing` and `/g/{group}/billing` quote each row's `amount_cents` in its
  base currency to everyone;
- the checkout names no currency, so Stripe picks one on its own page from
  where the buyer is.

A visitor in Germany would read US$39 on Qori's page and meet €35 on Stripe's.
The owner asked for the opposite: "make sure the price is same when they
landed in stripe page".

Afterwards:

- both pages quote the visitor's price — their currency's fixed amount, or
  USD;
- the checkout names that currency, so Stripe charges exactly what the page
  showed, wherever the buyer is.

## Decisions taken to make this specifiable

- **The checkout always names the currency the page quoted** (`currency` on
  the Checkout Session, lower-cased for Stripe). Stripe otherwise decides from
  where the buyer is when they open its page, and it has no call that tells
  Qori beforehand. Naming the currency is the guarantee (`D-047`). This
  bypasses Stripe's automatic localisation, which is the intent.
- **The currency travels on the subscribe link as a query field**, the way the
  coupon already does: `GET /g/{group}/billing/subscribe/{plan}?currency=EUR`.
  A currency the row has no fixed price in, or none at all, falls back to the
  row's base currency. Query keys are form fields, not path (`D-033`).
- **`BillsGroups::subscribeUrl()` gains a `string $currency` parameter**, and
  `BillingService::subscribe()` passes it through. The Stripe folder turns it
  into Stripe's lower-case code.
- **One class answers "which currency for this visitor":
  `App\Support\VisitorCurrency`.** It returns the first of: the visitor's
  choice, if the pages offer one (see below); the currency of the visitor's
  country; the base currency. A price row without a fixed amount in that
  currency quotes its base.
- **A country's currency comes from a map in config**,
  `qori.billing.country_currencies`: AU → AUD, NZ → NZD, GB → GBP, CA → CAD,
  SG → SGD, HK → HKD, MY → MYR, and each euro-area country → EUR. The pages
  never read the map directly.
- **Plan coupons already work in any currency**: `T-169` makes them
  percent-off.

## Preconditions

**Data this task verifies against:** the seeded prices with `T-169`'s fixed
amounts (`php artisan db:seed --class=PricingSeeder`).

**Equipment:**

- The Stripe sandbox, with a USD price that carries an EUR option on the
  Start product.
- `stripe listen` running.
- A browser.

**Spikes, both before the spec is final:**

1. **Does Cloudflare's country header reach the app?** `useqori.com` is on
   Cloudflare's nameservers (`release-prerequisites.md`). Cloudflare adds
   `CF-IPCountry` to a request only if the app's DNS record is proxied through
   it, and nobody has checked whether the record in front of Laravel Cloud is.
   Read one production request's headers. If the header is there, reading it
   is Cloudflare's code: `app/Integrations/Cloudflare`, behind a contract such
   as `LocatesVisitors`, bound in `IntegrationServiceProvider`. If it is not,
   the fallback is the region of the browser's first `Accept-Language` tag,
   which is weaker, and one more reason for a menu.
2. **What a named-currency subscription looks like.** In the sandbox:
   1. Create a session naming `currency=eur` on the USD price with its EUR
      option. Confirm Stripe's page shows €35 whatever the location.
   2. Pay, and keep the `customer.subscription.created` object as
      `tests/Fixtures/stripe/subscription-fixed-eur.json`. A test runs it
      through `BillingService::applySubscription()`.
   3. Record whether a customer that has paid in one currency can later start
      a subscription in another. Stripe has limited a customer to one
      currency, and a Group that moves country would hit that.

## Scope

**In:**

- `VisitorCurrency`, the config map, and the country lookup the first spike
  settles.
- `/pricing` and `/g/{group}/billing` quoting each plan in the visitor's
  currency.
- The subscribe link carrying `currency`, and the checkout naming it.
- The fixture and the test from the second spike.
- `docs/flows/billing.md`: how the currency is picked and named, and the fixed
  amounts `T-169` added.

**Out:**

- Creating the prices and their currency options in Stripe: release
  checklist (`D-047`).
- Plan switching in the Customer Portal. A subscription keeps its currency,
  and switching to a price without that option is Stripe's to refuse. Check it
  once the portal offers switching.
- Tax: `T-168`. Once Stripe Tax calculates, every currency option needs a tax
  behaviour (`D-047`, release checklist).

## Files

To be settled when ready. The provisional list:

| Path                                                    | Change | Notes                                         |
| ------------------------------------------------------- | ------ | --------------------------------------------- |
| `app/Integrations/Contracts/BillsGroups.php`            | edit   | `subscribeUrl()` takes the currency           |
| `app/Integrations/Stripe/Subscription.php`              | edit   | `currency` on the session                     |
| `app/Services/BillingService.php`                       | edit   | passes it through                             |
| `app/Http/Controllers/Share/BillingController.php`      | edit   | reads `currency`; quotes the visitor's price  |
| `app/Http/Controllers/PricingController.php`            | edit   | quotes the visitor's price                    |
| `app/Support/VisitorCurrency.php`                       | new    | the one answer                                |
| `config/qori.php`                                       | edit   | `billing.country_currencies`                  |
| `resources/js/pages/Pricing.vue`                        | edit   | the subscribe link carries the currency       |
| `resources/js/pages/share/Billing.vue`                  | edit   | the same                                      |
| `docs/flows/billing.md`                                 | edit   | the currency's path, and the fixed amounts    |
| `tests/Fixtures/stripe/subscription-fixed-eur.json`     | new    | the observed object                           |
| `tests/Fixtures/stripe/README.md`                       | edit   | its row                                       |
| `tests/Feature/Checkout/VisitorCurrencyTest.php`        | new    |                                               |

## Database

None.

## Code

To be settled when ready.

## Copy

To be settled when ready. There is no new sentence if the pages pick the
currency on their own; a menu needs its label and each option's name.

## Routes

None new. `share.billing.subscribe` gains the `currency` query field.

## Tests

To be settled when ready. At least: the checkout names the quoted currency; a
currency without a fixed price falls back to the base; each country in the map
quotes its currency; the EUR fixture grants its plan.

## Acceptance

- [ ] A visitor from a country with a fixed price sees that price on `/pricing` and on the billing page, and Stripe's page shows the same figure
- [ ] A visitor from anywhere else sees and pays the USD price
- [ ] The EUR subscription fixture grants its plan
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **Whether the pages offer a currency menu beside the prices, or pick from
  the visitor's country alone.** The owner's call, _asked_ 22 September 2026.
  The recommendation is country plus a menu: the menu covers a traveller or a
  VPN, and naming the currency at checkout keeps Stripe's page in step either
  way.
- The first spike: does `CF-IPCountry` reach the app? Anyone's.
- The second spike: the EUR fixture, and whether a customer can change
  currency. Anyone's.

## Re-scope log

None.

## Notes

- Written 22 September 2026 from `D-047`. The owner's question that shaped
  it: "How did Qori knows the country right now? Is that something we can ask
  stripe first so make sure the price is same when they landed in stripe
  page?" Qori does not know the country today. Stripe cannot be asked in
  advance, but it can be told.
