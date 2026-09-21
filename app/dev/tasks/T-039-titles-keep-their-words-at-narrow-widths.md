---
id: T-039
title: A Series title keeps its identifying words on a narrow screen
stream: design
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-039 — A Series title keeps its identifying words on a narrow screen

## Why

`R-002` F-4, at 390px in both themes. The Series editor keeps the cover and the
status beside the title, so "Notes on Being Interrupted" becomes a four-line
column and the long-title fixture takes **eleven lines**, with its summary
squeezed beside it. In the Series list, full-width status labels truncate titles
to "Facilitating Difficult …", "What Nobody Tells Y…" and "Saying No Without
B…".

A Series is identified by its title. Losing the identifying words to status
chrome inverts what the row is for, and truncation lands hardest on exactly the
titles that need the most words.

## Decisions taken to make this specifiable

**The title gets the width; the status moves.** At narrow widths the status and
action drop below the title rather than competing with it on the same line. The
cover stays beside the title because it is identity rather than chrome, and it
is a fixed 40px that does not grow.

**Truncate later, not never.** A list still has to scan, so rows keep a bounded
height. What changes is the order of sacrifice: the status label wraps or moves
before the title gives up characters.

**Verification is explicitly incomplete here.** The responsive lane has never
been run, and `R-002` says a finding at one captured width is not a completed
responsive pass. This fixes what was photographed at 390px. The required
360px, 768px and zoom checks belong to that lane and this task does not claim
them.

## Preconditions

None beyond a clean checkout. A browser helps and the pane cannot resize
reliably while hidden, which is the same constraint that blocks `T-022`.

## Scope

**In:**

- The Series page header at narrow widths: title and summary get the content
  width.
- The Series list row at narrow widths: the title keeps its words.

**Out:**

- Desktop, where both compositions are fine and `R-002` says so.
- The form widths in F-6, which are partly stale after `T-031` and need a fresh
  capture first — `T-040`.
- Running the responsive lane. That is a review pass, not a task.
- The Series identity redesign proposed in `ui-redesign-next-sprint.md`, which
  would revisit these compositions entirely and should not be pre-empted by
  layout tweaks.

## Files

| Path                                           | Change | Notes                                   |
| ---------------------------------------------- | ------ | --------------------------------------- |
| `resources/js/components/shell/PageHeader.vue` | edit   | Action slot wraps below at narrow width |
| `resources/js/pages/share/series/Index.vue`    | edit   | Row: status below the title when narrow |
| `tests/Feature/Series/SeriesIdentityTest.php`  | edit   | 1 case                                  |

## Database

None.

## Code

No new components. The change is layout classes: the header's title block stops
sharing a row with its action below the `sm` breakpoint, and the list row's
status stops being a full-width sibling of the title.

`PageHeader` is shared, so check the other pages that use it before changing it
— a header fix that helps Series and breaks Peers is not a fix.

## Copy

None.

## Routes

None.

## Tests

There is no JavaScript test runner and layout is not server-testable, so the
suite cannot see this. What it can hold is that the title still reaches the page
in full, which is the property truncation must never be allowed to become.

**Changed: `tests/Feature/Series/SeriesIdentityTest.php` — 1 new case**

1. `test_a_long_title_reaches_the_page_untruncated` — the server sends the whole
   title and any shortening is the browser's, reversible by CSS. If this ever
   fails, somebody has moved truncation to the server, where it cannot be undone.

**Say plainly in the report that the visual result was verified by eye or not at
all.**

## Acceptance

- [x] At 390px the Series page title and summary have the content width
      (checked at 375px, the nearest emulated width)
- [x] At 390px list titles keep their identifying words
- [x] Desktop is unchanged
- [x] Every other page using `PageHeader` still looks right
- [x] The server still sends whole titles
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

`R-001` recorded that long titles held up. `R-002` found they do not at mobile
width and says so, and did not quietly amend the earlier pass. Worth knowing
that the two disagree and that the later one looked at more.
