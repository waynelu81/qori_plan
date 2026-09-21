---
id: T-058
title: One place formats money
stream: selling
status: done
owner: claude
estimate: S
depends: T-054
blocks: T-085, T-088
---

# T-058 — One place formats money

## Why

Six components each build their own `Intl.NumberFormat` to show an amount:
the public Series page, the Series list, the public pricing page, the Billing
page, and two admin pages. Four of them fall back to `'USD'` when the currency
is null. For a Series that fallback is unreachable since `T-054` coupled price
to currency; for an amount-off coupon it was simply wrong — a coupon with no
currency is refused by `errors.pricing.currency_required`, not priced in
dollars.

The owner, reviewing the public page on 12 September 2026: "USD is quite a
universal indicator, but still if the site is translated to Chinese, it should
be 美元 instead of USD." That is `currencyDisplay`, a formatting choice, and
today it would be six edits with one forgotten.

Afterwards five of the six call one function. The public pricing page keeps
its own formatter for now, by the owner's decision below, and the test names
it with the reason.

## Decisions taken to make this specifiable

**One function, no fallback.** `formatMoney(cents, currency)` takes a `number`
and a `string`. A caller holding `number | null` or `string | null` has to
narrow before calling, which is the point: the type forces a decision where a
fallback hid one. The `?? 0` beside each Series `?? 'USD'` goes too.

**The reader's locale, as today.** The locale argument stays `undefined`. What
`US$39.00` looks like is the browser's business; what code it is formatting is
Qori's.

**`currencyDisplay` is one exported constant, set to `'symbol'`.** Verified in a
browser on 12 September: `symbol` renders `US$39.00` for a zh-CN reader and
`USD 39.00` for an en-AU one; `name` renders `39.00美元` and `39.00 US dollars`.
The owner's preference points at `name`; the cost is "US dollars" spelled out
for every English reader, who are most of them. `'symbol'` is the default this
task ships, and flipping it is one word in one file rather than a hunt. That is
the whole reason the file exists.

**The public pricing page keeps its own formatter, on an allow-list.** The
owner, 15 September 2026: leave `resources/js/pages/Pricing.vue` on its own;
that public page goes through another round of design review before anyone
changes it. It is also the only formatter that trims ".00" from a whole price
(`minimumFractionDigits: price.amountCents % 100 === 0 ? 0 : 2`), which
`formatMoney` does not do, so moving it would have turned "$19" into "$19.00".
The test carries the page in an allow-list with that reason, a second case
fails once the page stops building its own formatter so the entry cannot
outlive it, and `T-088` (design, draft) brings the page onto `formatMoney`
after its review.

**No price reads as Free, and the guard says so in the type.** The public
Series page, the Series list and the admin Creator page guard only on the
boolean `isFree`, which tells TypeScript nothing about the separate
`priceCents: number | null` and `currency: string | null`, so a plain swap does
not typecheck. Each guard becomes
`isFree || priceCents === null || currency === null`. That adds no meaning:
`Series::isFree()` is true when `price_cents` is null, and `T-054`'s check
constraint `series_price_has_currency` makes a null price and a null or empty
currency the same fact, so the two new conditions are only true when `isFree`
already is. Billing's guard (`isFree || !currency`) already narrows, and the
admin Pricing price row is typed `string` against a NOT NULL column.

**"Free" is not this task's.** The pages render the literal `'Free'` beside
their formatter. That is inline copy and belongs to `T-006`; a money formatter
formats money.

## Preconditions

`T-054` merged, with its check constraint
(`database/migrations/2026_09_13_000002_couple_series_price_to_currency.php`).

**Data this task verifies against:** the development database holds no priced
Series, so the rendered text is compared outside the pages: in Node, each
page's old formatter options against `formatMoney`'s, for every currency in
`config/qori.php`'s Series currencies, a spread of locales and a range of
amounts, which must be identical.

**Equipment:** Node. A browser would add the pages themselves, but the Series
list and Billing need a signed-in owner with priced data and the two admin
pages a staff login with two-factor authentication.

## Scope

**In:**

- `resources/js/lib/money.ts` and five call sites: the public Series page, the
  Series list, Billing, admin Creator and admin Pricing.
- Removing every `?? 'USD'`, and the `?? 0` beside the three Series ones.
- A test that keeps formatting in one place, with the pricing page
  allow-listed.
- The draft for the pricing page, and its line in the design stream.

**Out:**

- `resources/js/pages/Pricing.vue`, by the owner's decision (`T-088`).
- The `'Free'` literals (`T-006`).
- Choosing `'name'` over `'symbol'`. The constant is the owner's to flip.
- Server-side money formatting. Nothing in PHP formats an amount for a screen.
- The price input's cents conversion in `SeriesForm.vue` and `SeriesService`:
  an editable value, not a displayed amount.

## Files

| Path                                                                                | Change | Notes                                          |
| ----------------------------------------------------------------------------------- | ------ | ---------------------------------------------- |
| `resources/js/lib/money.ts`                                                         | new    | `formatMoney`, `CURRENCY_DISPLAY`              |
| `resources/js/pages/public/Series.vue`                                              | edit   | Widen the free guard; call it                  |
| `resources/js/pages/share/series/Index.vue`                                         | edit   | Widen the free guard; call it                  |
| `resources/js/pages/share/Billing.vue`                                              | edit   | Call it, after the existing free guard         |
| `resources/js/pages/admin/Creator.vue`                                              | edit   | Widen the free guard; call it                  |
| `resources/js/pages/admin/Pricing.vue`                                              | edit   | Call it; the coupon branch narrows on currency |
| `tests/Feature/Design/MoneyFormatterTest.php`                                       | new    | 3 cases                                        |
| `docs/planning/tasks/T-088-the-public-pricing-page-uses-the-one-money-formatter.md` | new    | Draft, design stream                           |
| `docs/planning/streams/design.md`                                                   | edit   | `T-088` in the list                            |

## Database

None.

## Code

```ts
// resources/js/lib/money.ts
export const CURRENCY_DISPLAY: Intl.NumberFormatOptions['currencyDisplay'] =
    'symbol';

/** Integer cents and an ISO 4217 code, in the reader's locale. */
export function formatMoney(cents: number, currency: string): string {
    return new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency,
        currencyDisplay: CURRENCY_DISPLAY,
    }).format(cents / 100);
}
```

```ts
// public/Series.vue, share/series/Index.vue, admin/Creator.vue:
if (series.isFree || series.priceCents === null || series.currency === null) {
    return 'Free';
}

return formatMoney(series.priceCents, series.currency);
```

```ts
// admin/Pricing.vue — the coupon line narrows instead of inventing a currency:
coupon.amountOffCents !== null && coupon.currency !== null
    ? `${formatMoney(coupon.amountOffCents, coupon.currency)} off`
    : …
```

`share/Billing.vue` keeps `if (plan.isFree || !plan.currency) return 'Free'`
and then calls `formatMoney(plan.amountCents, plan.currency)`. The admin Pricing
price row calls `formatMoney(price.amountCents, price.currency)` in the
template, and its local `money()` goes.

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/Design/MoneyFormatterTest.php` — 3 cases**

Reads files, the same shape as `TabIndexTest`, because there is no JavaScript
test runner. The allow-list is a private `ownFormatter(): array` of
path => reason, as `ArchitectureTest::allowed()` is.

1. `test_one_place_builds_a_currency_formatter` — no `.vue` file under
   `resources/js` outside `ownFormatter()` contains `Intl.NumberFormat`.
   **Fails today**, five files.
2. `test_every_file_allowed_its_own_formatter_still_has_one` — every path in
   `ownFormatter()` exists and still contains `Intl.NumberFormat`. Passes
   today; fails once the pricing page moves, so the entry is removed with it.
3. `test_no_currency_fallback_remains` — no `.vue` or `.ts` file under
   `resources/js` contains `?? 'USD'` or `?? "USD"`. **Fails today**, four
   files.

**Changed:** none.

## Acceptance

- [x] One function formats every amount the product shows, except the public pricing page, which is allow-listed with its reason
- [x] No `?? 'USD'` anywhere in the front end
- [x] `currencyDisplay` is one constant, and the task's report says what the owner would change to get 美元
- [x] The public Series page, the Series list, Billing and both admin pages render the same text they did
- [x] The public pricing page is untouched
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Rendered values from the 12 September check, for whoever flips the constant:
zh-CN `symbol` → `US$39.00`, `name` → `39.00美元`; zh-TW `name` → `39.00 美元`;
ja-JP `name` → `39.00米ドル`; de-DE `symbol` → `39,00 $`, `name` → `39,00
US-Dollar`; en-AU `symbol` → `USD 39.00`, `name` → `39.00 US dollars`.

**Revised 15 September 2026, before it was claimed.** A check of this spec
against the code found three things the 13 September version had wrong: the
pricing page's `minimumFractionDigits`, which `formatMoney` cannot express; the
claim that every other call site's guard already narrows the currency, false
for three of them; and the coupon refusal's lang key, which is
`errors.pricing.currency_required`. The owner decided the first — the pricing
page stays out — and the other two are corrected above. Preconditions and
Acceptance were brought up to the 14 September template.

**The test was tightened during execution** (wording tier). An adversarial
review of the diff confirmed three gaps in the test as Tests describes it, and
the test was fixed in place rather than the section rewritten:

- Case 1 matches the currency option `style: 'currency'` instead of the word
  `Intl.NumberFormat`, in `.ts` files as well as `.vue`. A `.ts` helper or a
  `toLocaleString` call can no longer format money outside `money.ts`, and a
  type name such as `Intl.NumberFormatOptions` or a comment no longer trips it.
- `resources/js/lib/money.ts` is named in the test as the one place.
- Case 2 checks `money.ts` before the allow-list, so it still asserts once
  `T-088` empties the list, rather than becoming a test PHPUnit reports as
  risky.

Against the commit before this task, the new pattern finds the same five pages.
