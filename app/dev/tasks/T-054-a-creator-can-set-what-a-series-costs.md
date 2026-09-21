---
id: T-054
title: A creator can set what a Series costs
stream: selling
status: done
owner: claude
estimate: M
depends: none
blocks: T-049, T-058
---

# T-054 — A creator can set what a Series costs

## Why

A Series carries `price_cents` and `currency`, the public page shows the price,
checkout charges it, and **no form has ever sent either field**.
`StoreSeriesRequest` and `UpdateSeriesRequest` accept title, summary and hours;
`SeriesService::create()` accepts a price that no caller passes. The
`UpdateSeriesRequest` docblock says so in as many words and explains the
omission as a product question about people who have already paid.

The owner, 13 September 2026, testing: "I can't find anywhere to set price for
series." The one priced Series in the development database was priced by hand,
and it had a price with **no currency**, which is what a hand-set row looks
like — and which `Connect::checkoutFor()` would have sent to Stripe as an empty
string.

So this is the first task in the selling stream after the link, ahead of the
voucher: a discount needs a price to discount.

## Decisions taken to make this specifiable

**The product question is already answered by the data.** An `accesses` row
carries its own `price_cents` and `currency`, written at fulfilment. Changing a
Series' price changes what the next person pays and nothing about anyone who
already has access: their row, their receipt and their access are untouched.
The form says so in one sentence, and the two docblocks that called this an
unanswered question are corrected.

**A price never exists without a currency, and the database says so.** They
are one field pair on the form, validated together, written together, and a
check constraint refuses a row with one and not the other. The three `?? 'USD'`
fallbacks in the front end become dead code as a result; they are left for the
task that gives Qori one money formatter, and named in Notes.

**Major units in, cents stored.** A creator types `49.00`; the request validates
a decimal; the service stores `4900`. That is the only place the multiplication
happens.

**A short currency list, from config, with no zero-decimal currency in it.**
`qori.payments.currencies` mirrors the payout countries already in config:
AUD, NZD, GBP, USD, CAD, SGD, HKD, MYR, EUR. JPY is left out on purpose —
Stripe treats it as whole yen, so `price_cents` would be a lie for it, and
adding the branch is a separate decision. `default_currency` is `AUD`, matching
`default_country`.

**Price lives on the Series details form, not the create form.** A Series is
created as a draft and priced before it is made ready. The create form keeps
asking for the least it can.

**One notice when payouts are not connected.** A priced Series in a Group with
no Connect account is one the public page refuses at checkout with "isn't ready
to take payments yet". The creator should hear that before a buyer does, so the
form shows one sentence and a link to the Payouts page whenever a price is set
and `connect_account_id` is empty. Connected, not "ready": checking readiness
is a Stripe call and does not belong on a page load.

**Zero is not a price.** `Series::isFree()` already treats `0` as free. The form
refuses anything below one unit; leaving the field empty is how a Series becomes
free.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- Price and currency on the Series details form, with validation.
- The check constraint coupling the two columns.
- The not-connected notice on that form.

**Out:**

- Price on the create form.
- Changing what anyone who already paid was charged, or telling them.
- Vouchers (`T-049`), which depend on this.
- The three `?? 'USD'` fallbacks and the six independent `Intl.NumberFormat`
  calls in the front end. A shared money formatter is its own task.
- Zero-decimal currencies.
- Anything on the public page, which already renders both fields.

## Files

| Path                                                                        | Change | Notes                                              |
| --------------------------------------------------------------------------- | ------ | -------------------------------------------------- |
| `database/migrations/2026_09_13_000002_couple_series_price_to_currency.php` | new    | The check constraint; refuses if rows violate      |
| `config/qori.php`                                                           | edit   | `payments.currencies`, `payments.default_currency` |
| `app/Http/Requests/Share/UpdateSeriesRequest.php`                           | edit   | Two rules; docblock corrected                      |
| `app/Services/SeriesService.php`                                            | edit   | Two arms in `update()`; the multiplication         |
| `app/Http/Controllers/Share/SeriesController.php`                           | edit   | `show()` gains four props                          |
| `resources/js/components/series/SeriesForm.vue`                             | edit   | Two fields, the notice; docblock corrected         |
| `resources/js/pages/share/series/Show.vue`                                  | edit   | Passes the new props through                       |
| `lang/en/series.php`                                                        | edit   | 3 keys                                             |
| `tests/Feature/Series/SeriesPriceTest.php`                                  | new    | 9 cases                                            |

`StoreSeriesRequest` and the create form are deliberately not in this list.

## Database

| Table    | Column | Type | Null | Default | Index / constraint                                                              |
| -------- | ------ | ---- | ---- | ------- | ------------------------------------------------------------------------------- |
| `series` | —      | —    | —    | —       | `series_price_has_currency` check: `(price_cents IS NULL) = (currency IS NULL)` |

Migration: `database/migrations/2026_09_13_000002_couple_series_price_to_currency.php`

The migration first counts rows that would violate the constraint and **throws
with the count** rather than guessing a currency or silently freeing a Series.
Production has no such rows, because no form could make one; a development
database may, and the fix there is a one-line update chosen by a person.

## Code

```php
// config/qori.php, under 'payments'
'currencies' => ['AUD', 'NZD', 'GBP', 'USD', 'CAD', 'SGD', 'HKD', 'MYR', 'EUR'],
'default_currency' => 'AUD',
```

```php
// App\Http\Requests\Share\UpdateSeriesRequest::rules(), added
'price' => ['sometimes', 'nullable', 'numeric', 'min:1', 'max:99999'],
'currency' => ['sometimes', 'nullable', 'required_with:price', Rule::in(config('qori.payments.currencies'))],
```

```php
// App\Services\SeriesService::update(), added arms
if (array_key_exists('price', $attributes)) {
    $free = $attributes['price'] === null;
    $changes['price_cents'] = $free ? null : (int) round((float) $attributes['price'] * 100);
    $changes['currency'] = $free ? null : mb_strtoupper((string) $attributes['currency']);
}
```

`@param` on `update()` gains `price?: ?string, currency?: ?string`.

```php
// App\Http\Controllers\Share\SeriesController::show(), added props
'pricing' => [
    'currencies' => config('qori.payments.currencies'),
    'defaultCurrency' => config('qori.payments.default_currency'),
    'payoutsConnected' => filled($group->connect_account_id),
    'payoutsUrl' => route('share.payouts.show', $group->slug),
    'help' => $terminology->line('series.price_help', [], $group),
    'needsPayouts' => $terminology->line('series.price_needs_payouts', [], $group),
    'connectLabel' => __('series.price_connect_payouts'),
],
```

```ts
// SeriesForm.vue, added props
priceCents: number | null;
currency: string | null;
pricing: { currencies: string[]; defaultCurrency: string; payoutsConnected: boolean; payoutsUrl: string; help: string; needsPayouts: string; connectLabel: string };
```

Fields: `<Input name="price" type="number" min="1" step="0.01">` with default
value `priceCents / 100` or empty, beside a `<select name="currency">` over
`pricing.currencies` defaulting to the stored currency or `defaultCurrency`.
The notice renders when the price field is non-empty and
`!pricing.payoutsConnected`, with `connectLabel` linking to `payoutsUrl`.

## Copy

| Key                            | File                 | English                                                                                             |
| ------------------------------ | -------------------- | --------------------------------------------------------------------------------------------------- |
| `series.price_help`            | `lang/en/series.php` | `Leave it empty to share this :series for free. :peer_plural who already paid keep what they paid.` |
| `series.price_needs_payouts`   | `lang/en/series.php` | `Nobody can pay for this :series until you connect payouts.`                                        |
| `series.price_connect_payouts` | `lang/en/series.php` | `Connect payouts`                                                                                   |

## Routes

None. `share.series.update` and `share.payouts.show` both exist.

## Tests

**New: `tests/Feature/Series/SeriesPriceTest.php` — 9 cases**

1. `test_a_creator_can_set_a_price_and_currency` — PATCH with `price` and
   `currency`, both stored. **Fails today**: the fields are not validated and
   `update()` ignores them.
2. `test_a_price_is_stored_as_integer_cents` — `49.50` becomes `4950`.
3. `test_a_price_without_a_currency_is_refused` — 422 on `currency`.
4. `test_a_currency_outside_the_list_is_refused` — `JPY`, 422.
5. `test_a_price_below_one_unit_is_refused` — `0.50`, 422.
6. `test_clearing_the_price_makes_the_series_free` — empty `price`, both
   columns null, `isFree()` true.
7. `test_changing_the_price_does_not_touch_an_existing_access` — an access at
   `4900 AUD`, the Series repriced to `9900`, the access still says `4900`.
8. `test_the_series_page_says_when_payouts_are_not_connected` — the prop is
   false with no Connect account and true with one.
9. `test_the_database_refuses_a_price_without_a_currency` — a raw insert with
   one and not the other throws.

**Changed:** none expected. `EditSeriesTest::test_an_omitted_field_is_left_alone`
already asserts the `sometimes` behaviour this relies on.

## Acceptance

- [x] A creator can price a Series from its details form, in a listed currency
- [x] A price cannot be saved without a currency, in the form or the database
- [x] Emptying the price makes the Series free
- [x] Repricing leaves every existing access exactly as it was
- [x] The form says when nobody can pay yet, and links to Payouts
- [x] The two docblocks that called this an open question are corrected
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**Found while writing this, 13 September 2026.** The Series `How to use AI` in
the development database had `price_cents = 3000` and `currency = NULL`. It was
given `AUD` by hand so the owner could test checkout; the migration above would
have refused on it otherwise.

**The three fallbacks.** `public/Series.vue:66`, `share/series/Index.vue:69`
and `admin/Creator.vue:51` each read `currency ?? 'USD'`, and six components
each build their own `Intl.NumberFormat`. With the constraint in place the
fallback can never fire for a priced Series. One money formatter, with
`currencyDisplay` decided once, is the task that removes them.

**Why not the create form.** A Series cannot be sold until it is ready, and
readiness is decided on its page. Asking for money on the create form would put
the price before the Episodes.
