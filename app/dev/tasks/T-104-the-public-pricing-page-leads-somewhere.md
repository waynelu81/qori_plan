---
id: T-104
title: The public pricing page leads somewhere
stream: design
status: draft
owner: unassigned
estimate: S
depends: T-088
blocks: none
---

# T-104 — The public pricing page leads somewhere

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 17 September 2026 from
> [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-3.

## Why

`020-pricing` is a heading, a sentence and three plan cards, and then it stops.
R-004 found no sign-up, sign-in, home or plan-selection action and no linked
brand identity on any variant, so a visitor who arrives directly has to use
browser navigation to go anywhere. `resources/js/pages/Pricing.vue` has no
header, though the auth pages link `T-038`'s lockup home.

Afterwards the page says whose it is, links home, and ends on one Start
sharing into the signup that exists today, without suggesting that pressing a
plan card buys the plan. `T-088` rewrites the money line in the same file,
which is why this waits for it.

## Decisions taken to make this specifiable

**The plan cards stay information, and Start sharing goes to `register()` with
no parameter** (provisional). Registration knows no plan: `Register.vue` posts
`signup_intent`, name, email and passwords, with `share` checked by default;
`GroupService` starts every Group on `config('qori.default_plan')`, `free`; a
paid plan is bought at `GET /g/{group}/billing/subscribe/{plan}`, owner-only,
which redirects to Checkout. A button per card would drop its plan or have to
carry it through register, verification and setup.

**The header is a new `PublicHeader.vue` composing `AppLogoLockup` inside a
link to `home()`, and its Start sharing hides below `sm` as Welcome's does.**
The lockup reads the product name from the shared `name` prop, where
`Welcome.vue` types "Qori" beside its own copy of the mark. The Start sharing
after the cards shows at every width, because it is the one the page ends on.

**A signed-in visitor sees Go to Qori, to `dashboard()`, instead of both
doors** (provisional). `Welcome.vue` does the same, and `/pricing` sets no
`CurrentGroup` whose billing it could name.

**Copy is a `copy` prop from `PricingController`, out of a new
`lang/en/pricing.php`,** as `PublicSeriesController` passes `accesses.join.*`;
`PublicHeader.vue` takes its labels as props and holds no English. The note
names the Group noun, so it goes through `Terminology::line()`, with the
starting plan's name interpolated from `config('qori.plans')`.

## Preconditions

**Data this task verifies against:** `php artisan qori:reset basic` for plan
rows, and a verified account for the signed-in check.

**Equipment:** a browser at 390px and 1440px, signed out and signed in.

## Scope

**In:**

- A header: the lockup linked home, then Sign in and Start sharing for a
  guest, or Go to Qori for a signed-in visitor.
- One Start sharing after the plan cards, with one sentence naming the plan a
  new Group starts on; the four lines in `lang/en/pricing.php`.

**Out:**

- The advertised benefits (F-1, `T-011`); currency and precision (F-2,
  `T-088`); registration wording (F-8, `T-108`); touch-target sizes, which
  `T-105` (F-4) sets on sign-in and the Peer page only.
- An action on a plan card, a plan carried through registration, or any link
  to billing or Checkout.
- `Welcome.vue`, a link to `/pricing` from it, and this page's existing inline
  English (heading, intro, empty notice, "Free"), which is §13's conversion.

## Files

| Path                                         | Change | Notes                                             |
| -------------------------------------------- | ------ | ------------------------------------------------- |
| `resources/js/components/PublicHeader.vue`   | new    | Lockup linked home; both doors, or Go to Qori     |
| `resources/js/pages/Pricing.vue`             | edit   | Composes the header; closing Start sharing + note |
| `app/Http/Controllers/PricingController.php` | edit   | Adds the `copy` prop                              |
| `lang/en/pricing.php`                        | new    | Four lines                                        |
| `tests/Feature/PricingPageTest.php`          | new    | 5 cases                                           |

Flows: none — only a prop; `docs/flows/billing.md`'s `/pricing` read stands.

## Database

None.

## Code

`PricingController::__invoke()` renders `copy` beside `prices`: `signIn`,
`startSharing` and `goTo` (`:name` from `config('app.name')`) through `__()`,
and `startNote` through `Terminology::line()`, with `plan` from
`config('qori.plans.'.config('qori.default_plan').'.name')`. Register links
keep the `@chisel-registration` markers `Welcome.vue` uses.

## Copy

| Key                         | File                  | English                                                                         |
| --------------------------- | --------------------- | ------------------------------------------------------------------------------- |
| `pricing.nav.sign_in`       | `lang/en/pricing.php` | Sign in                                                                         |
| `pricing.nav.start_sharing` | `lang/en/pricing.php` | Start sharing                                                                   |
| `pricing.nav.go_to`         | `lang/en/pricing.php` | Go to :name                                                                     |
| `pricing.start.note`        | `lang/en/pricing.php` | Every new :group starts on the :plan plan. You choose a plan once it is set up. |

## Routes

None.

## Tests

**New: `tests/Feature/PricingPageTest.php` — 5 cases**

1. `test_it_passes_the_navigation_copy_from_lang` — labels equal their lines.
2. `test_it_names_the_plan_a_new_group_starts_on` — the default plan's name and
   the default Group noun are in `copy.startNote`.
3. `test_it_renders_for_a_signed_in_visitor` — `200`, `Pricing`, same `copy`.
4. `test_it_links_the_lockup_home_and_offers_both_doors` — `PublicHeader.vue`
   names `AppLogoLockup`, `home()`, `login()`, `register()` and `dashboard()`.
5. `test_it_gives_no_plan_card_an_action` — `Pricing.vue` has `register()`
   after the card loop and names neither `billing` nor `subscribe`.

**Changed:** none. `PricingModelTest` asserts `prices` only, and
`TerminologyTest`'s article walk reaches the new lang file by itself.

## Acceptance

- [ ] A guest on `/pricing` sees the mark and name linked to `/`, Sign in and
      Start sharing, at 390px and 1440px
- [ ] After the cards, Start sharing opens registration with sharing chosen,
      beside one sentence naming the plan a new Group starts on
- [ ] A signed-in visitor sees Go to Qori, to the dashboard, instead
- [ ] No plan card is a link or button; nothing reaches billing or Checkout
- [ ] No new English in a Vue file, and no noun or plan name spelled out
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Does a plan card carry its plan through register, verification and setup,
  or does every card share one Start sharing? (the owner's)
- Does a signed-in Group owner get Go to Qori, or their Plan and billing page?
  (the owner's)
- The note's wording, and whether it names the starting plan (the owner's).
- Does `Welcome.vue` adopt `PublicHeader` here, its labels moving to lang, or
  later? (the stream owner's)
- Does `AppLogoLockup`'s sidebar-shaped `row` read at header scale? (anyone's)
- Should `DesignReviewCommand` capture `020-pricing` signed in too, not only
  as guest? (the stream owner's)
- `T-088` lands first, so the price line this page keeps is already the shared
  formatter's; `T-088` is still a `draft` (anyone's).

## Re-scope log

None.

## Notes

The only link to `/pricing` is owner-only `share/Billing.vue`; Welcome has none.
