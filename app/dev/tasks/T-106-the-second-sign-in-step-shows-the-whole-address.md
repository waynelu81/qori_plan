---
id: T-106
title: The second sign-in step shows the whole address
stream: design
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-106 — The second sign-in step shows the whole address

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 17 September 2026 from
> [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-5.

## Why

`T-087` (`D-015`) gave sign-in a second step showing the address, with **Use a
different email** beside it in one bordered row. R-004 found the address cut
there: the mobile capture of `725-sign-in-validation` shows
`rita@design-review.qori.t…` above the neutral credential error, and the live
`030-sign-in` second step at 360px showed `sam@design-review…`, with the
action taking the other half of the row (walkthroughs, 16–17 September 2026).
`D-015` says a mistyped address shows up on this step; the domain is where
that typo hides, and it is cut off beside an error that deliberately does not
say whether the address has an account.

The cause is in `resources/js/components/auth/SignInMethods.vue`: the row at
line 223 is `flex min-w-0 items-center justify-between`, the address at line
226 is `min-w-0 truncate`, the action at line 234 is `shrink-0`. `T-087` added
`min-w-0` and `truncate` as a departure when a 63-character address pushed the
step past a 375px screen; that stopped the overflow by cutting the address.

Afterwards the whole address is on screen at every width, wrapping when it has
to, with Use a different email on its own line below it. Nothing else moves.

## Decisions taken to make this specifiable

**The address wraps with `wrap-anywhere` and is never cut.** An address has no
spaces. `overflow-wrap: anywhere` counts its break opportunities toward the
element's minimum width, so it cannot widen the parents `T-087` fixed with
`min-w-0`; `break-words` does not count them. Tailwind has the utility from
4.1, and 4.3.3 is installed. `min-w-0` stays.

**Use a different email goes below the address, inside the same bordered
block, start-aligned (provisional).** Beside, it takes half of a 360px row
however short the address. Inside the block it stays attached to the address
it corrects, not between the error and the method chooser.

**One arrangement at every width, no breakpoint.** The card is `max-w-sm`
(`resources/js/layouts/auth/AuthSimpleLayout.vue`, line 16), so the row is
nearly as narrow at 1440px, and a longer address is cut there by the same
classes.

**`title` and `-my-1` go; `py-1` stays.** `title` let a cut address be read
on hover and only repeats a whole one. The negative margin held a one-line
row's height; stacked, it would pull the action into the address. The 28px
height is unchanged; whether it must reach 44px is asked in `T-105`.

**Everything else stays.** DOM order is already address then action, so focus
order is unchanged; both `data-test` hooks stay; `InputError` stays directly
under the block, so `auth.failed` sits under the whole address.

## Preconditions

**Data this task verifies against:** the worlds `php artisan qori:design-review`
seeds, for `725-sign-in-validation`; live, any 60-character address, since an
unknown one reaches the second step and the neutral error (`T-087`'s report).

**Equipment:** a browser at 360px, and the harness with
`--only=725-sign-in-validation --viewport=mobile`.

## Scope

**In:**

- The second step's address block in `SignInMethods.vue`, lines 215–240, as
  decided above, with the comment at lines 215–220 rewritten to say why the
  address wraps.
- One source-reading case in `SignInCompositionTest`.

**Out:**

- `D-015`'s composition and `D-013`'s rules inside it: the two steps, Next
  asking nothing, the Password / Email link chooser, passkey, `LinkSent.vue`,
  and the neutral `auth.failed` and `auth.magic_link.sent` sentences.
- Touch-target heights on this step (F-4, `T-105`); inline English here and in
  `LinkSent.vue` (`T-006`); the keyboard walk (`T-022`).
- The auth layout's shift between steps, decided in `T-087`'s report; a new
  harness screen for this step, one of R-004's coverage notes that `T-110`
  also leaves out; harness reliability (`T-110`).
- Choosing where an address breaks, such as a `<wbr>` after `@`.

## Files

| Path                                             | Change | Notes                                                                     |
| ------------------------------------------------ | ------ | ------------------------------------------------------------------------- |
| `resources/js/components/auth/SignInMethods.vue` | edit   | Address block, lines 215–240: wraps, action below, no `title`, no `-my-1` |
| `tests/Feature/Auth/SignInCompositionTest.php`   | edit   | One source-reading case; 12 cases (was 11)                                |

Flows: none — layout only; `docs/flows/auth.md` names the address and Use a
different email without placing them.

## Database

None.

## Code

No script change. Provisional classes, for the stream owner to confirm at
360px: the row (line 223) becomes `border-input grid min-w-0 gap-1 rounded-md
border px-3 py-2`; the address (line 226) `min-w-0 text-sm font-medium
wrap-anywhere`, without `title`; the action (line 234) drops `-my-1` and
`shrink-0` and gains `justify-self-start`.

## Copy

None. `auth.sign_in.change_email` is unchanged; the address is what was typed.

## Routes

None.

## Tests

**Changed: `tests/Feature/Auth/SignInCompositionTest.php` — 12 cases (was 11)**

1. `test_the_second_step_shows_the_whole_address` — **new**: the opening tag
   carrying `data-test="sign-in-address"` has `wrap-anywhere` and neither
   `truncate` nor `text-ellipsis`.

The other 11 are unchanged. `test_the_page_has_one_email_field` counts the
literal email `type` attribute, so the new comment must not spell it
(`T-087`'s report). Placement is a browser check, not a source assertion.

## Acceptance

- [ ] At 360px, on the second step with a 60-character address, the whole
      address is on screen, wrapped, with no ellipsis and no page-level
      horizontal overflow
- [ ] Use a different email sits below the address and still returns to the
      first step with the address kept, focused and no error standing
- [ ] `725-sign-in-validation` at mobile shows the whole of
      `rita@design-review.qori.test` directly above the neutral credential
      error
- [ ] At 1440px the step shows the same arrangement
- [ ] The two steps, Next asking nothing, the Password / Email link choice,
      passkey and the neutral errors are as `D-015` left them
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Confirm Use a different email goes below the address inside the bordered
  block rather than under the block, from a 360px render of both — the stream
  owner's.
- `T-105` (F-4) sizes Next, Log in and Email me a sign-in link in the same
  `SignInMethods.vue` (lines 202, 301 and 321, outside this block), and asks
  whether Use a different email needs 44px: whichever is ready second depends
  on the other — the stream owner's.
- Measure the confirmation's address in `LinkSent.vue` (line 32, nothing to
  break an unbroken string) at 360px with a 60-character address. R-004 saw
  Sam's whole; if a long one overflows, whether that one class joins this task
  — anyone's to measure, the stream owner's to decide.

## Re-scope log

None.

## Notes

R-004 recorded the cut address at mobile only; whether its 1440px capture cuts
Rita's too was not written down. The no-breakpoint decision stands either way.
