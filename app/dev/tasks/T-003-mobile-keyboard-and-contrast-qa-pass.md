---
id: T-003
title: Mobile and contrast QA pass
stream: design
status: done
owner: claude
estimate: M
depends: T-001, T-002
blocks: T-022
---

# T-003 — Mobile and contrast QA pass

## Why

Days 1–3 checked contrast by calculation, once, in a scratch script that no
longer exists, and checked mobile by measuring `scrollWidth` on three pages.
Neither is a keyboard pass, and neither covers the dozen screens built since.
`T-001` closed with 360px explicitly unverified and the note that "the covers
sit in flex rows that already wrap" is an argument rather than an observation.

This closes the redesign's release gate. It is also the last chance to turn the
one-off checks into something that holds: a palette that was measured once will
drift the first time somebody adjusts a token.

## Decision taken to make this specifiable

Listed as blocking when this was a draft: do findings become fixes here, or
tasks of their own?

**Fix anything under roughly ten minutes; spawn the rest.** A QA pass that
fixes nothing produces a list nobody actions, and one that fixes everything
stops being reviewable. The line is defensible because it is about the size of
the change rather than its importance: a genuinely important finding that takes
a day is exactly the one that deserves its own spec and its own review.

Every finding is recorded either way — fixed ones in the report, spawned ones
as a new draft task with the evidence in it.

## Preconditions

- `php artisan wayfinder:generate --with-form`
- `php artisan serve --port=8001` and `npm run dev`
- A browser that can be driven at 360px and 1440px in both colour schemes.
  **Without one, do not claim this task** — two thirds of it is looking.
- Seeded data: at least one Group with a Series, an Episode and a Peer with
  access, so the pages are not all empty states. `docs/tinker/` has recipes.

## Scope

**In:**

- Every product page at 360px and 1440px, in both themes.
- Contrast, re-measured against the final palette — and turned into a test.

**Out:**

- **Tab order, focus visibility and escape behaviour.** Moved to `T-022` after
  the re-scope below — they cannot be observed in this environment, and a task
  cannot be finished on a criterion nobody can check.
- Automated accessibility tooling (axe, Lighthouse). Worth having; it adds a
  dependency and a new failing check, and belongs in its own task.
- The admin console. Its palette is deliberately distinct (§24) and it is staff
  software, not product.
- Fixes over ten minutes — see the decision above.
- Any new feature. If a page needs something it does not have, that is a
  finding, not a licence.

## Files

| Path                                    | Change | Notes                                                                                                                         |
| --------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `tests/Feature/PaletteContrastTest.php` | new    | Parses `app.css`, asserts WCAG ratios                                                                                         |
| `app/Support/Contrast.php`              | new    | sRGB relative luminance and ratio, so the test reads as a table                                                               |
| `docs/planning/walkthroughs.md`         | edit   | The pass, and what it found                                                                                                   |
| _various_                               | edit   | Whatever the under-ten-minutes fixes turn out to be. **List them in the report**, not here — they cannot be known in advance. |

## Database

None.

## Code

```php
namespace App\Support;

class Contrast
{
    /** @return array{int, int, int} */
    public static function rgb(string $hslOrHex): array;

    public static function luminance(string $colour): float;

    /** WCAG 2.1 contrast ratio, 1.0 to 21.0. */
    public static function ratio(string $foreground, string $background): float;

    /** Every `--token: value;` in one CSS block. @return array<string, string> */
    public static function tokens(string $css, string $selector): array;
}
```

`tokens()` takes the file's contents and a selector (`:root` or `.dark`) so the
test can read the real stylesheet rather than a copy of its values. A copy is
the thing that drifts.

Accept `hsl(H S% L%)` and `#rrggbb`. The stylesheet uses the first; the error
pages inline the second, and checking those too is free.

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/PaletteContrastTest.php` — 6 cases**

1. `test_normal_text_clears_four_and_a_half_to_one` — foreground on background,
   card, muted, accent and sidebar, in both themes. One assertion per pair with
   the pair named in the message.
2. `test_muted_text_clears_four_and_a_half_to_one` — the same surfaces.
3. `test_the_accent_clears_four_and_a_half_to_one_on_every_surface` — the gold.
   This is the one that moved twice during Day 1 and will move again.
4. `test_text_on_a_filled_control_clears_four_and_a_half_to_one` —
   `primary-foreground` on `primary`, and the same for destructive and success.
5. `test_boundaries_and_focus_rings_clear_three_to_one` — `input` and `ring`
   against their grounds.
6. `test_the_error_pages_use_the_same_values_as_the_stylesheet` — the inlined
   hexes in `errors/layout.blade.php` match the tokens they were copied from.
   That file says in a comment that they are duplicated; this is what makes the
   comment true a year from now.

Not tested, and say so in the report: tab order, focus visibility and escape
behaviour. There is no JavaScript test runner, so those are verified by hand
and by nothing else.

## Acceptance

- [x] Every product page checked at 360px and 1440px, both themes, with the
      list of pages in the report
- [x] No page scrolls sideways at 360px
- [x] Contrast is a test, and it passes
- [x] Findings under ten minutes are fixed and listed; the rest are spawned as
      draft tasks with evidence
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

**9 September 2026 — the keyboard third cannot be observed here.**

Expected: a browser can be driven at 360px in both themes, so tab order, focus
visibility and escape behaviour can be checked by hand. The Preconditions
section says as much and warns not to claim the task without one.

Found: the browser pane is **hidden**, and `document.hidden === true` has three
consequences that between them make the keyboard third unobservable.

- **Key events do not reach the document.** `Tab` with focus explicitly placed
  in a text field leaves `document.activeElement` unchanged. Tab order and
  focus rings cannot be checked at all.
- **CSS animations do not run in a hidden document**, so `animationend` never
  fires and Reka's exit transition never completes. Escape _does_ work — the
  dialog's `data-state` goes to `closed` — but it stays mounted and focus is
  never restored, so "returns focus sensibly" is untestable rather than
  failing.
- This is the third time a hidden pane has changed what is observable. The
  first was `requestAnimationFrame` never firing in `useDeepLinkedControl`
  (`T-003`'s sibling, Day 3), which shipped broken twice before it was noticed.

Why this is a re-scope and not a note: two acceptance criteria cannot be
satisfied or honestly ticked, and narrowing them to fit what I managed would be
the exact failure the "Scope is the contract" rule exists to prevent.

**Resolved by splitting rather than blocking.** The mobile and contrast thirds
are complete and independently valuable — sixteen pages measured, and the
palette is a test now rather than an afternoon's arithmetic. Blocking the whole
task would have shelved both. `T-022` carries the keyboard pass and is `blocked`
until somebody has a browser that receives key events.

Re-scoped and resolved by the same person executing it, which is only
acceptable because the planner and the developer are the same here. With two
people this goes back to the board.

## Notes

**Two fixes, both under the ten-minute line:**

- `errors/layout.blade.php` had three dark values that were hand-picked rather
  than converted — `--ink`, `--muted` and `--gold` had all drifted from the
  tokens they were copied from. The new contrast test caught this on its first
  run, which is a good sign about the test and a poor one about the comment
  that had been guarding them.
- `DialogContent` forwarded its own `showCloseButton` prop to Reka, which does
  not know it, so `showclosebutton="true"` landed on the DOM of every dialog in
  the product. `reactiveOmit` now drops it. Upstream shadcn-vue has the same
  bug.

**The contrast test is the durable half of this task.** Day 1 chose the palette
with a throwaway script; the gold moved twice and the dark destructive once on
numbers that existed for an afternoon. `PaletteContrastTest` parses
`resources/css/app.css`, so the next person to nudge a token finds out in the
same run that checks everything else.
