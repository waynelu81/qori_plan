---
id: T-085
title: The public Series page still offers to buy when the Group is disconnected
stream: selling
status: done
owner: claude
estimate: S
depends: T-058
blocks: none
---

# T-085 — The public Series page still offers to buy when the Group is disconnected

## Why

`T-064` gave a creator a way to disconnect Stripe, and setup lets a creator
skip it; either way the public page did not know. `PublicSeriesController::show()`
sent `isFree`, `priceCents` and `currency`, and `public/Series.vue` offered the
name-and-email form, the code step and "Get access — A$20.00" from those
alone. A buyer who pressed it reached `CheckoutService`'s guard,
`errors.checkout.not_connected`, as a refusal after the click — the shape
`PLAN.md`'s beta gate forbids by name. The 21 September 2026 walk found it
worse: "pressing it posts, the server answers `unsupported_operation` … and the
page shows nothing" (`walkthroughs.md`). The public pages mount no Toaster, so
the refusal was flashed to nobody.

Afterwards a priced Series whose Group holds no account says so in a sentence
naming the Group, in place of every way to buy it, and any toast the server
flashes at a page without the app shell appears.

## Decisions taken to make this specifiable

- **"Can be paid" means the Group holds an account id** — a column read, no
  Stripe call. For an account that is connected and cannot take payments yet,
  the owner accepts a Peer meeting Stripe's own refusal ("We just notify and
  advice … that's for the creator to deal with", 22 September 2026), and
  `T-164` tells the creator. So only a Group with no account is held back.
- **The sentence names the Group**: ":name isn't taking payments for this
  :series yet. Let them know you'd like it." The page already names the Group
  above the title, and a named sentence tells the reader who to tell. The owner
  can change the words.
- **It stands in for all three ways in**: the stranger's name-and-email form,
  the code step and the signed-in button all end in checkout. A free Series and
  anybody who already has access are unaffected.
- **Every layout mounts a Toaster.** The fix for the invisible refusal is the
  layout, not this page: the pages that take no app shell (the public pages,
  the landing and pricing pages, setup) take a `BareLayout` that adds only the
  Toaster, and the sign-in and console layouts mount one. That also makes
  `T-164`'s note after connecting Stripe in setup visible, which landed on a
  setup page.
- **The creator's side needed nothing**: the price field has said "Nobody can
  pay for this :series until you connect Stripe" with a Connect link since
  `T-054`, which was this draft's third bullet.

## Preconditions

None.

**Data this task verifies against:** a clean database for the tests; the
design-review world's `harbour-lane-studio` for the walk, its account cleared
for the walk and put back after.

**Equipment:** a browser.

## Scope

**In:**

- `notTakingPayments` on the public page for a priced Series whose Group holds
  no account, shown in place of the forms and the button.
- A Toaster on every layout.
- The two copy fixups in the lines this touches: the consent box and the
  checkout refusals say the Group's Series noun, capitalised.

**Out:**

- A paused Group (`errors.access.not_accepting`), which has its own sentence.
- An account that exists and cannot take payments: the owner's call above.
- Continue staying disabled until consent is ticked with no hint why
  (`fixups.md`): it waits on the owner's answer to whether free access needs
  consent at all.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Http/Controllers/PublicSeriesController.php` | edit | `notTakingPayments`; the consent line through Terminology |
| `resources/js/pages/public/Series.vue` | edit | the sentence in place of the forms |
| `lang/en/accesses.php` | edit | `not_taking_payments`; `consent.peer` says `:series` |
| `lang/en/errors.php` | edit | `checkout.not_connected`, `free_series`, `already_granted` say `:series` |
| `app/Services/CheckoutService.php` | edit | the three refusals carry the Group's nouns |
| `app/Integrations/Stripe/Connect.php` | edit | its own `not_connected` carries them too |
| `resources/js/layouts/BareLayout.vue` | new | no shell, a Toaster |
| `resources/js/app.ts` | edit | shell-less pages take `BareLayout` |
| `resources/js/layouts/AuthLayout.vue` | edit | a Toaster |
| `resources/js/layouts/AdminLayout.vue` | edit | a Toaster |
| `docs/flows/checkout.md` | edit | the page, and where the toast appears |
| `docs/architecture/errors.md` | edit | every layout mounts the Toaster |
| `tests/Feature/PublicSeriesTest.php` | edit | four cases |
| `tests/Feature/Access/SeriesAccessContinueTest.php` | edit | the refusal's words with the noun filled |

## Database

None.

## Code

```php
// PublicSeriesController::show(), beside `notice`:
'notTakingPayments' => ! $model->isFree() && blank($model->group?->connect_account_id)
    ? app(Terminology::class)->line('accesses.not_taking_payments', ['name' => $model->group->name ?? ''], $model->group)
    : null,
```

## Copy

| Key | File | English |
| --- | --- | --- |
| `not_taking_payments` | `lang/en/accesses.php` | ":name isn't taking payments for this :series yet. Let them know you'd like it." |
| `consent.peer` | `lang/en/accesses.php` | "I agree that :creator can email me about this :series." |
| `checkout.not_connected.message` | `lang/en/errors.php` | "This :series isn't ready to take payments yet." |
| `checkout.free_series.message` | `lang/en/errors.php` | "This :series is free, so there is nothing to pay." |
| `checkout.already_granted.message` | `lang/en/errors.php` | "You already have access to this :series." |

## Routes

None.

## Tests

**Changed: `tests/Feature/PublicSeriesTest.php` — 4 new cases**

1. `test_a_priced_series_with_no_payment_account_says_so_instead_of_selling`
2. `test_a_priced_series_with_an_account_is_offered_as_before`
3. `test_a_free_series_is_never_held_back_for_payments`
4. `test_the_consent_sentence_uses_the_groups_noun`

**Changed:**

- `tests/Feature/Access/SeriesAccessContinueTest.php` — the refusal after the
  code compares the whole message with the Group's noun filled in.

## Acceptance

- [x] A priced Series whose Group holds no account shows the sentence in place
      of the forms and the button; with an account, or free, it is offered as before
- [x] A toast flashed at a page without the app shell appears
- [x] The consent box and the checkout refusals say the Group's Series noun
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

- 22 September 2026: the draft said the buyer "reaches … a refusal after the
  click". The walk and the code say the refusal never appeared: no Toaster on
  a page without the app shell. The Toaster on every layout joins the scope,
  because a sentence before the click leaves the refusal for a page loaded
  before the account went, and it too has to be seen.

## Notes

`T-064`'s report and `T-074`'s report; `T-074`'s case 4 is what a buyer meets
today.

22 September 2026, from `T-164`: for an account that is connected and cannot
take payments, the owner accepts a Peer meeting Stripe's refusal — "We just
notify and advice … that's for the creator to deal with" — and `T-164` tells the
creator. In test mode Stripe creates the Checkout Session for such an account
(observed that day), so the buyer reaches Stripe's page rather than Qori's
refusal.
