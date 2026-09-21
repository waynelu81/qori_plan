---
id: T-030
title: A long-form field is a textarea, and says how much room is left
stream: design
status: done
owner: claude
estimate: S
depends: none
blocks: T-031
---

# T-030 — A long-form field is a textarea, and says how much room is left

## Why

A Series summary is validated at 1,000 characters and collected in a
single-line `<input>`. A creator writing a paragraph sees roughly forty
characters of it at a time, scrolling sideways through their own sentence, with
nothing on screen saying how much room there is. There is no `<textarea>`
anywhere in the product and no textarea primitive to reach for.

The limit is also written down twice over — `max:1000` in PHP and nothing at
all in the browser — so the field silently accepts a 1,001st character and
refuses the submission afterwards. That is the same shape as the plan-limit
rule in `CLAUDE.md`: **interpolate the value, never restate it.** One number,
read by both sides.

This task is small on purpose. It exists to establish the control and the rule
before more long-form fields arrive, not to redesign a form.

## Decisions taken to make this specifiable

**No rich text, and this is not a step towards it.** Decided by the owner on
10 September 2026. A summary appears in list rows, page headers, the public
page and eventually an email subject line, and markup breaks every one of those.
Qori currently renders no untrusted HTML at all — the only two `v-html` uses in
the codebase are QR codes the server generated — and a WYSIWYG would introduce
the first such path on a public page. Not now.

**The limit lives in `config/qori.php`.** Not a constant on the model and not a
literal in the Vue. There is direct precedent three lines away in
`SeriesController::show()`, where `uploadExtensions` comes from config so the
form and the rule cannot drift, and the same reasoning applies here.

**A counter, not a hard stop.** The textarea carries `maxlength`, so the browser
refuses the 1,001st keystroke, and the count is shown throughout rather than
only once it is nearly full. A count that appears at 90% tells somebody they are
in trouble at the moment it is most annoying to find out.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- A `Textarea` UI primitive, matching the shape of the existing `Input`.
- A `TextareaField` composing label, textarea, live count and error.
- The one field in the product that needs it today: the Series summary on the
  create form.
- The character limit as one fact, read from config by both the validator and
  the page.

**Out:**

- Any rich text editor. See the decision above.
- `episodes.reference`. It is 500 characters and it is a path or a URL, which is
  a single-line value however long it gets.
- The admin pricing `tagline` and `features`. Both are in
  `StoreSubscriptionPriceRequest` and **neither has a form field**, so there is
  nothing to convert; that is a reachability finding rather than work for here.
- `campaigns.body`. Campaigns have no form at all — see `T-014`.
- The Series **edit** form, which is `T-031` and depends on this.

## Files

| Path                                               | Change | Notes                             |
| -------------------------------------------------- | ------ | --------------------------------- |
| `config/qori.php`                                  | edit   | A `limits` block                  |
| `resources/js/components/ui/textarea/Textarea.vue` | new    | Primitive, mirroring `Input.vue`  |
| `resources/js/components/ui/textarea/index.ts`     | new    | One export                        |
| `resources/js/components/TextareaField.vue`        | new    | Label, textarea, count, error     |
| `resources/js/pages/share/series/Index.vue`        | edit   | Summary becomes a `TextareaField` |
| `app/Http/Requests/Share/StoreSeriesRequest.php`   | edit   | `max` read from config            |
| `app/Http/Controllers/Share/SeriesController.php`  | edit   | `index()` sends the limits        |
| `tests/Feature/Series/SeriesTextFieldsTest.php`    | new    | 6 cases                           |

## Database

None. `series.summary` is already a `text` column.

## Code

```php
// config/qori.php
'limits' => [
    /*
    | How long a piece of long-form text may be, by field.
    |
    | Read by the Form Request and sent to the page, so the textarea's
    | maxlength and the validator's max are one number.
    */
    'text' => [
        'series_summary' => 1000,
    ],
],
```

```php
// App\Http\Requests\Share\StoreSeriesRequest
'summary' => ['nullable', 'string', 'max:'.config('qori.limits.text.series_summary')],
```

```vue
// resources/js/components/TextareaField.vue defineProps<{ name: string; label:
string; maxlength: number; modelValue?: string; defaultValue?: string; id?:
string; description?: string; placeholder?: string; error?: string; rows?:
number; // default 4 optional?: boolean; // renders the "(optional)" hint the
form already uses }>();
```

The count reads `{used} / {maxlength}`, is `aria-live="polite"` so a screen
reader hears it change, and is tied to the textarea with `aria-describedby` so
the limit is announced before somebody starts typing rather than after they hit
it.

## Copy

| Key | File | English                                                                                                                           |
| --- | ---- | --------------------------------------------------------------------------------------------------------------------------------- |
| —   | —    | **None.** The count is two numbers and a slash; "Summary" and "(optional)" already exist inline in the form (§13's unwired i18n). |

## Routes

None.

## Tests

**New: `tests/Feature/Series/SeriesTextFieldsTest.php` — 6 cases**

1. `test_a_summary_at_the_limit_is_accepted` — exactly the configured length.
2. `test_a_summary_over_the_limit_is_refused` — one character more.
3. `test_the_limit_comes_from_config` — override `qori.limits.text.series_summary`
   to a small number and assert the validator moves with it. This is the case
   that fails if somebody re-hardcodes `max:1000`.
4. `test_the_page_is_told_the_limit` — `limits.summary` reaches the create page,
   so the textarea cannot carry a different number from the validator.
5. `test_a_summary_is_optional` — nothing here makes it required.
6. `test_the_summary_survives_a_round_trip_with_newlines` — the point of a
   textarea: a multi-line value is stored and read back unchanged.

**Changed:** none expected.

## Acceptance

- [x] The Series summary is a textarea, not a single-line input
- [x] The remaining room is visible while typing, and announced
- [x] The limit is one number, read from config by both the validator and the page
- [x] A multi-line summary round-trips
- [x] No rich text editor is introduced, and no new HTML is rendered unescaped
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**There is exactly one long-form field in the product, and that is the finding.**
The task expected several. `series.summary` is the only one a person types.
`episodes.reference` is 500 characters of path or URL and stays single-line;
`subscription_prices.tagline` and `features.*` are validated in
`StoreSubscriptionPriceRequest` and **have no form field at all**, so there was
nothing to convert; `campaigns.body` has no form either. Two more instances of
the shape `T-012` looks for, found by looking for something else.

**`TextareaField` holds its own value rather than being uncontrolled.** The
create form submits through Inertia's `Form`, which reads the DOM and wants only
a starting value. An uncontrolled textarea would show a count frozen at its
initial length, which is worse than no count. Holding the value and mirroring it
outward serves both that form and `T-031`'s bound one.

The `Textarea` primitive belongs in `components/ui/` beside `Input` because it
is a styled element with no opinions. `TextareaField` is the thing forms
actually use, and it lives one level up beside `InputError` for the same reason
`GroupNameForm` does: it composes.
