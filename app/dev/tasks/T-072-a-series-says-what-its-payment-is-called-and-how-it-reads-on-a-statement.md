---
id: T-072
title: A Series says what its payment is called, and how it reads on a card statement
stream: selling
status: done
owner: claude
estimate: M
depends: none
blocks: none
---

# T-072 — A Series says what its payment is called, and how it reads on a card statement

## Why

A Peer who buys a Series sees two pieces of text afterwards that Qori does
not control today: the payment's description, in Stripe's dashboard and on
the receipt, and the line on their card statement. Checkout sends neither, so
the receipt says whatever Stripe derives from the line item and the statement
says only the creator's static descriptor. A statement line a Peer does not
recognise is a dispute, and disputes are the creator's to fight (§7.2).

Stripe's Checkout Session accepts both through `payment_intent_data`:
`description`, an arbitrary string, and `statement_descriptor_suffix`, which
Stripe concatenates to the account's prefix with `* ` to form what the
cardholder sees. The suffix has rules, and Stripe truncates rather than
refuses when the total runs long, so the only place a mistake can be caught
is Qori's own validation. The owner asked for both fields on 13 September
2026, with validation that is sound.

Afterwards: a creator can set both on the Series form, the suffix is refused
unless it will appear exactly as typed, and Checkout carries both.

## Decisions taken to make this specifiable

**The rules are Stripe's, quoted.** From
[Statement descriptors](https://docs.stripe.com/get-started/account/statement-descriptors)
and [Set statement descriptors for connected accounts](https://docs.stripe.com/connect/statement-descriptors),
read on 2026-09-13:

- A complete descriptor "contains only Latin characters", "contains between
  5 and 22 characters, inclusive", "contains at least one letter (if using a
  prefix and a suffix, both require at least one letter)", and "doesn't
  contain any of the following special characters: `<`, `>`, `\`, `'` `"` `*`".
- "The suffix is concatenated with the prefix, the `*` symbol, and a space
  to form the complete statement descriptor." "Make sure that the total length
  of the concatenated descriptor is no more than 22 characters, including the
  `*` symbol and the space." Prefix `RUNCLUB` (7) leaves 13 for the suffix.
- "A static prefix … must contain between 2 and 10 characters, inclusive."
- "Card networks receive only the first 22 characters", so an overrun is
  truncated silently, not refused.
- "Dynamic suffixes are supported only for card charges." For card charges
  `statement_descriptor` itself "returns an error"; only the suffix may be set.
- Direct charges use "the connected account's static component", so the
  prefix in play is the creator's, from
  `settings.card_payments.statement_descriptor_prefix`, or the first ten
  characters of `settings.payments.statement_descriptor` when no prefix is set.

**Only the suffix is sent, never a full descriptor.** Checkout offers card
payment methods, and a full `statement_descriptor` on a card charge is an
error. Non-card methods keep the creator's static descriptor.

**The cap depends on the creator's prefix, and Qori remembers it.** The
suffix may be at most `22 − 2 − length(prefix)` characters. The prefix is the
creator's account setting; Qori stores it on the Group whenever it reads the
account, from the v1 fields above. Until it is known, the cap is the worst
case: a ten-character prefix leaves ten. `T-063` moves the account read to
v1, which is when the field is populated; until then the rule runs with the
worst case, which is still correct.

**Empty means "as before".** No description sends the Series title, which is
what the line item already carries. No suffix sends nothing, and the
creator's static descriptor stands.

**Validation messages are copy, in `series.php`**, not `validation.php`: they
name the Series and the prefix, which a generic message cannot.

## Preconditions

None beyond a clean checkout. `T-071` done, which it is.

## Scope

**In:**

- Two columns on Series, one on Group, one migration.
- The rule, the request, the service, the form, the Checkout payload.
- The prefix read into `ConnectAccount` and remembered by `PayoutsService`.
- Copy, tests, `docs/flows/checkout.md`.

**Out:**

- Kanji and kana suffixes for Japanese accounts (Qori has no JPY, `T-054`).
- Setting the creator's prefix or full descriptor from Qori. That is their
  Stripe dashboard's, and Stripe resets the prefix whenever the descriptor
  changes.
- The create form. A description and a suffix belong to a Series that is
  being priced, which happens on the edit form (`T-054`).

## Files

| Path                                                                      | Change | Notes                            |
| ------------------------------------------------------------------------- | ------ | -------------------------------- |
| `database/migrations/2026_09_13_000004_add_payment_wording_to_series.php` | new    | Three columns                    |
| `app/Rules/StatementDescriptorSuffix.php`                                 | new    | The rule                         |
| `app/Http/Requests/Share/UpdateSeriesRequest.php`                         | edit   | Two fields                       |
| `app/Services/SeriesService.php`                                          | edit   | `update()` handles both          |
| `app/Integrations/Stripe/Connect.php`                                     | edit   | `checkoutFor()` sends both       |
| `app/Data/ConnectAccount.php`                                             | edit   | `statementDescriptorPrefix`      |
| `app/Services/PayoutsService.php`                                         | edit   | `account()` remembers the prefix |
| `app/Http/Controllers/Share/SeriesController.php`                         | edit   | Props for the two fields         |
| `resources/js/components/series/SeriesForm.vue`                           | edit   | Two inputs, a counter, a preview |
| `lang/en/series.php`                                                      | edit   | Labels, help, refusals           |
| `docs/flows/checkout.md`                                                  | edit   | What Checkout sends              |
| `tests/Feature/Series/StatementDescriptorTest.php`                        | new    | 10 cases                         |
| `tests/Feature/Checkout/ConnectOnboardingTest.php`                        | edit   | 1 case for the prefix read       |

## Database

| Table    | Column                        | Type        | Null | Default | Index / constraint |
| -------- | ----------------------------- | ----------- | ---- | ------- | ------------------ |
| `series` | `payment_description`         | string(200) | yes  | null    | none               |
| `series` | `statement_descriptor_suffix` | string(22)  | yes  | null    | none               |
| `groups` | `statement_descriptor_prefix` | string(10)  | yes  | null    | none               |

Migration: `database/migrations/2026_09_13_000004_add_payment_wording_to_series.php`

## Code

```php
namespace App\Rules;

class StatementDescriptorSuffix implements ValidationRule
{
    public const FULL_LIMIT = 22;
    public const SEPARATOR = '* ';
    public const PREFIX_MAX = 10;
    /** @var list<string> */
    public const FORBIDDEN = ['<', '>', '\\', "'", '"', '*'];

    public function __construct(private ?string $prefix) {}

    /** 22 − 2 − the prefix's length; the worst case, 10, when the prefix is unknown. */
    public static function maxLengthFor(?string $prefix): int;

    public function validate(string $attribute, mixed $value, Closure $fail): void;
    // in order: printable ASCII only (`/^[\x20-\x7E]+$/`) → series.statement_latin
    //           none of FORBIDDEN                          → series.statement_forbidden
    //           at least one [A-Za-z]                      → series.statement_letter
    //           mb_strlen ≤ maxLengthFor($this->prefix)    → series.statement_too_long (:max, :prefix)
}
```

```php
// App\Http\Requests\Share\UpdateSeriesRequest::rules() — two more:
'payment_description' => ['sometimes', 'nullable', 'string', 'max:200'],
'statement_descriptor_suffix' => ['sometimes', 'nullable', 'string', new StatementDescriptorSuffix($this->prefix())],
// private function prefix(): ?string — app(CurrentGroup::class)->get()?->statement_descriptor_prefix
```

```php
// App\Services\SeriesService::update() — beside the price arm:
if (array_key_exists('payment_description', $attributes)) {
    $changes['payment_description'] = blank($attributes['payment_description']) ? null : trim((string) $attributes['payment_description']);
}
if (array_key_exists('statement_descriptor_suffix', $attributes)) {
    $changes['statement_descriptor_suffix'] = blank($attributes['statement_descriptor_suffix']) ? null : trim((string) $attributes['statement_descriptor_suffix']);
}
```

```php
// App\Integrations\Stripe\Connect::checkoutFor() — two more keys, the second only when filled:
'payment_intent_data[description]' => $series->payment_description ?? $series->title,
'payment_intent_data[statement_descriptor_suffix]' => $series->statement_descriptor_suffix,
```

```php
// App\Data\ConnectAccount — one more property, from the v1 shape when present, else null:
public ?string $statementDescriptorPrefix = null,
// settings.card_payments.statement_descriptor_prefix
//   ?? mb_substr(settings.payments.statement_descriptor, 0, 10)
//   ?? null

// App\Services\PayoutsService::account() — after the read:
// if the account's prefix is non-null and differs from $group->statement_descriptor_prefix, forceFill and saveQuietly
```

`SeriesController::show()` adds to `pricing`: `paymentDescription`,
`statementDescriptorSuffix`, `statementPrefix` (string or null),
`statementMax` (int, from `maxLengthFor`), and the labels and help below.
`SeriesForm.vue` renders both fields under the price: a text input for the
description with `maxlength="200"`; a text input for the suffix with
`:maxlength="pricing.statementMax"`, a live "n of max" count, and a preview
line reading `PREFIX* SUFFIX` when the prefix is known and `SUFFIX` alone
when it is not.

## Copy

| Key                                | File                 | English                                                                                               |
| ---------------------------------- | -------------------- | ----------------------------------------------------------------------------------------------------- |
| `series.payment_description_label` | `lang/en/series.php` | What the payment is called                                                                            |
| `series.payment_description_help`  | `lang/en/series.php` | On the receipt and in Stripe. Empty means the :series title.                                          |
| `series.statement_label`           | `lang/en/series.php` | On their card statement                                                                               |
| `series.statement_help`            | `lang/en/series.php` | Up to :max characters after :prefix*. Letters, numbers and spaces; it should say what they bought.    |
| `series.statement_help_unknown`    | `lang/en/series.php` | Up to :max characters, until Qori has read your Stripe statement prefix. Letters, numbers and spaces. |
| `series.statement_latin`           | `lang/en/series.php` | Card statements can only show plain Latin letters, numbers and punctuation.                           |
| `series.statement_forbidden`       | `lang/en/series.php` | Card statements can't show < > \ ' " or *.                                                            |
| `series.statement_letter`          | `lang/en/series.php` | It needs at least one letter.                                                                         |
| `series.statement_too_long`        | `lang/en/series.php` | Too long: :max characters at most, because :prefix* takes the rest of the 22 a statement shows.       |

`statement_help` and `statement_too_long` fill `:prefix` with the Group's
prefix; when it is unknown the unknown variant of help is shown and
`:prefix` in the refusal reads "your Stripe prefix".

## Routes

None.

## Tests

**New: `tests/Feature/Series/StatementDescriptorTest.php` — 10 cases**

1. `test_a_creator_can_set_a_description_and_a_suffix` — both stored,
   trimmed.
2. `test_clearing_either_stores_null`.
3. `test_the_suffix_refuses_each_forbidden_character` — six values, one per
   character in `FORBIDDEN`, each refused with `series.statement_forbidden`.
4. `test_the_suffix_needs_a_letter` — `12345` refused.
5. `test_the_suffix_refuses_non_latin_characters` — `漢字`, `café` refused.
6. `test_the_suffix_is_capped_by_the_prefix` — Group prefix `RUNCLUB`: a
   13-character suffix accepted, 14 refused with `:max` 13.
7. `test_the_suffix_is_capped_at_ten_when_the_prefix_is_unknown` — 10
   accepted, 11 refused.
8. `test_the_series_page_offers_the_fields_and_the_cap` — `pricing.statementMax`
   is 13 with the prefix and 10 without; both current values present.
9. `test_checkout_carries_both_to_stripe` — `Http::assertSent` sees
   `payment_intent_data[description]` and `[statement_descriptor_suffix]`.
10. `test_checkout_falls_back_to_the_title_and_sends_no_suffix` — description
    is the title; no suffix key.

**Changed: `tests/Feature/Checkout/ConnectOnboardingTest.php` — 1 new case**

- `test_the_account_read_remembers_the_statement_prefix` — a payload with
  `settings.card_payments.statement_descriptor_prefix` `RUNCLUB` leaves
  `groups.statement_descriptor_prefix` `RUNCLUB` after
  `PayoutsService::account()`; a payload without leaves it untouched.

## Acceptance

- [x] A creator can set a payment description and a statement suffix on the
      Series form, and see how many characters remain and how the line reads
- [x] Every rule quoted above is enforced before Stripe is asked, with a
      refusal that says which rule
- [x] Checkout sends both; an empty description sends the title, an empty
      suffix sends nothing
- [x] The Group remembers its prefix from an account read that carries it
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

Stripe's `description` has no documented length limit; 200 is Qori's,
chosen so it fits a receipt line and the dashboard list without wrapping.

The account read is v2 today and carries no descriptor fields that the
documentation confirms, so `statementDescriptorPrefix` will read null until
`T-063` moves the read to v1. The rule is correct either way; the cap is only
tighter than it needs to be for a creator with a short prefix.
