---
id: T-105
title: Primary mobile controls are large enough to touch
stream: design
status: draft
owner: unassigned
estimate: M
depends: none
blocks: none
---

# T-105 — Primary mobile controls are large enough to touch

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 17 September 2026 from
> [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-4.

## Why

The redesign brief asks for "minimum 44px touch targets for primary mobile
controls" (`docs/planning/ui-redesign.md:231`). R-004 measured it live at
360px and it fails on two screens. On sign-in (`030-sign-in`,
`725-sign-in-validation`), Log in and Email me a sign-in link are 36px high:
the shared `Button` at its `default` size, `h-9`
(`resources/js/components/ui/button/index.ts:24`). On the Peer Series page
(`410-shared-series`), Continue is 20px and Mark as done 16px: plain
`<button>`s styled as underlined text, as tall as their `text-sm` and
`text-xs` line and no taller (`resources/js/pages/shared/Show.vue:175-183`,
`:240-250`).

Afterwards, each of those controls, and Next on sign-in's first step, is at
least 44px high at 360px, measured on the element that takes the tap rather
than on a wrapper around it. The hierarchy does not change: Log in stays the
filled primary action, and Continue and Mark as done keep their text treatment.

## Decisions taken to make this specifiable

**Sign-in's actions get a new `touch` size on the shared `Button`, 44px at
every width, and `default` does not change** (provisional). Three call sites
in one composition need one height, and a height written three times drifts.
37 Vue files import `Button`, some beside an `h-9` `Input`; the rule is for
primary controls, and changing `default` would restyle pages nobody measured.

**Next is in, although R-004 names only Log in and the link request.** It is
the same `Button` on the first step of the same composition
(`resources/js/components/auth/SignInMethods.vue:202-204`); leaving it at
36px would put two heights in one sign-in.

**The Peer page's controls are fixed per page, as text with a 44px box**
(provisional). They are not `Button`s, and making Continue a filled button is
the receiving composition `docs/planning/ui-redesign-next-sprint.md` §5
intends to design. Mark as not done is the same element (`Show.vue:245-249`).

**No negative margin.** The `-my-1 py-1` `T-087` gave Use a different email
(`SignInMethods.vue:234`) would, under Mark as done, reach into the Episode
row's own button directly above (`Show.vue:195-229`): two controls, one tap.

## Preconditions

**Data this task verifies against:** the worlds `php artisan qori:design-review`
seeds, where Sam has two of four Episodes done
(`database/seeders/DesignReviewSeeder.php:466-477`). The three screens are at
`app/Console/Commands/DesignReviewCommand.php:312`, `:358` and `:487-492`.

**Equipment:** a visible browser at 360 × 800 and 1440 × 900 that reads an
element's bounding box. A screenshot cannot show a hit area.

## Scope

**In:**

- `buttonVariants` gains `touch`, used by Next, Log in and the link request.
- On `shared/Show.vue`, Continue and Mark as done / Mark as not done are each
  at least 44px high on their own element.

**Out:**

- The second step's address row, and where Use a different email sits in it:
  `T-106` (F-5). This task changes no class in that block.
- Use a different email (28px), the method chooser tabs, the passkey button
  and Send another link on sign-in, and View your certificate on the Peer
  page: not measured by R-004 (provisional, see below).
- Every other screen, Welcome's `h-10` buttons included
  (`resources/js/pages/Welcome.vue:87-97`): that audit is a review pass.
- Restyling Continue and the Shared with me cards (`T-027`, R-004 F-10);
  the Episode row and Continue becoming links (`T-089`).
- The certificate page's wording (`T-109`, F-12); focus order and rings
  (`T-022`); the inline English on both screens (§13) — this changes classes,
  not words.

## Files

| Path                                             | Change | Notes                                                |
| ------------------------------------------------ | ------ | ---------------------------------------------------- |
| `resources/js/components/ui/button/index.ts`     | edit   | `touch` in `size` (`:23-30`)                         |
| `resources/js/components/auth/SignInMethods.vue` | edit   | `size="touch"` at `:202`, `:301`, `:321`             |
| `resources/js/pages/shared/Show.vue`             | edit   | Continue `:175-183`, progress `:240-250`, row `:231` |
| `tests/Feature/Design/TouchTargetTest.php`       | new    | 3 cases, provisional                                 |

## Database

None.

## Code

Provisional. In `index.ts`, beside `default`:
`"touch": "h-11 px-4 py-2 has-[>svg]:px-3"` (`h-11` is 44px; `resources/css/app.css`
sets no `--spacing`). The three sign-in `Button`s gain `size="touch"`; Continue
and the progress form's submit gain `inline-flex min-h-11 items-center`.

## Copy

None. No sentence is added or changed.

## Routes

None.

## Tests

**New: `tests/Feature/Design/TouchTargetTest.php` — 3 cases** (provisional),
reading files as `tests/Feature/Design/TabIndexTest.php` does, because Vue
cannot be unit tested here (`:17-18`). The live measurement is the real check.

1. `test_it_keeps_the_touch_size_at_44px` — `touch` carries `h-11`.
2. `test_it_sizes_every_sign_in_action_for_touch` — the `Button`s with
   `data-test` `next-button`, `login-button` and `magic-link-button` carry
   `size="touch"`.
3. `test_it_gives_the_peer_page_controls_a_44px_box` — Continue and the
   progress submit in `Show.vue` carry `min-h-11`.

**Changed:** none expected; `tests/Feature/Auth/SignInCompositionTest.php`
asserts structure, not classes. Total: 3 new cases.

## Acceptance

- [ ] At 360 × 800, Next, Log in and Email me a sign-in link are each at least
      44px high on the `button` element itself
- [ ] At 360 × 800 on `410-shared-series`, Continue, Mark as done and Mark as
      not done are each at least 44px high on the `button` element itself, and
      no two controls' boxes overlap
- [ ] Log in and the link request still read as the primary action; Continue
      and Mark as done keep their text treatment, and 1440 × 900 changes by
      those heights alone
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- A `touch` size on `Button`, or `default` becoming 44px below `sm` so every
  mobile button qualifies; and every width, or below `sm` only — the stream
  owner's.
- Whether Use a different email (`py-1`, `SignInMethods.vue:232-239`, which
  `T-106` moves below the address without changing its height), the method
  chooser tabs (`py-1.5`,
  `resources/js/components/ui/tabs/TabsTrigger.vue:24`), the passkey button
  (`resources/js/components/PasskeyVerify.vue:49-63`), Send another link
  (`resources/js/components/auth/LinkSent.vue:48-57`) and View your
  certificate (`Show.vue:163-169`) are primary — the stream owner's.
- Order against `T-089` (storage), whose draft rewrites `Show.vue`'s Episode
  row and Continue as links: this task should land first and `T-089` carry
  `min-h-11` onto its anchor, or, if `T-089` is ready first, Continue's half
  moves onto that anchor. No `depends:` while both are drafts — the stream
  owner's.
- Order against `T-106`, which edits the address block (lines 215–240) of the
  same `SignInMethods.vue` step: whichever is ready second depends on the
  other — the stream owner's.
- Whether Mark as done's row padding (`pb-3`, `Show.vue:231`) shrinks so each
  Episode does not grow by the whole 28px, from a 360px capture — anyone's.
- Whether a source-reading test earns its place for a property only a
  browser measures — the stream owner's.

## Re-scope log

None.

## Notes

The measured heights are exactly the classes: `h-9` is 36px, and `text-sm`
and `text-xs` lines are 20px and 16px. No rendering quirk is involved. Live
evidence is in
[walkthroughs](../walkthroughs.md#16–17-september-2026--r-004-current-web-review).

Use a different email is 28px since `T-087`'s departure. Whether it needs 44px
is asked here, not in `T-106`, which only moves it.
