---
id: T-107
title: Admin creator lists keep a readable name on a narrow screen
stream: design
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-107 — Admin creator lists keep a readable name on a narrow screen

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 17 September 2026 from
> [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-6.

## Why

On both mobile variants of `520-admin-creators` and `530-admin-creator`
(R-004 F-6), Group names and slugs in the list and Series titles in the detail
shrink to a sliver of their first character, while plan, status and counts
keep their width. Staff cannot tell rows apart without opening them. T-039
fixed this on the creator side only.

The markup shows why, and T-039's report found the same trap in `PageHeader`.
Identity is `min-w-0 flex-1` (`resources/js/pages/admin/Creators.vue:54`,
`resources/js/pages/admin/Creator.vue:173`): a zero flex basis beside fixed
`w-20`/`w-24` metadata in a `flex-wrap` row, which never forces a wrap. By
the classes' arithmetic, not a browser measurement, a 390px row has about
332px inside `px-4`, the border and `p-3`. The metadata and gaps take 328px,
leaving the name about 4px.

Afterwards, a narrow screen gives the name its own row with the metadata
below. Wide screens, and everything the console reads, stay as they are.

## Decisions taken to make this specifiable

**Identity gets its own first row, as in T-039, not a sideways-scrolling
table.** The pass allowed either. These rows are links in a flex list, not a
`<table>`, and sideways scrolling hides the metadata on a phone. The approach
is copied, not shared: `admin-console.md` never shares the layout.

**Names clamp at two lines when narrow and one when wide.** This uses
`line-clamp-2 sm:truncate`, as in `resources/js/pages/share/series/Index.vue:127`,
because a list still has to scan. _Provisional_: see the second question.

**Below `sm`, metadata is one wrapping line under the name, with no fixed
widths.** Fixed widths line up columns on a wide screen. In the detail row the
four widths and their gaps need 408px, and the row is 332px. The breakpoint
matches T-039 (`resources/js/components/shell/PageHeader.vue:55`).
_Provisional_: see the fourth question.

**Nothing the console reads changes.** `CreatorDirectory` already sends whole
names and titles. The defect is in the browser, and the tests hold that line.

## Preconditions

**Data this task verifies against:** the `DesignReviewSeeder` worlds, from
one `php artisan qori:design-review --only=admin-creator --viewport=mobile
--theme=both` (adding `--url` when the app is not at `APP_URL`; one command
per theme is how R-004 lost its light manifest). `530-admin-creator` is
Harbour Lane Studio; the long titles
are The Long Names Collective's, opened by hand at
`/admin/creators/01K4XNDES1GNREV1EWGRP0MANY`. The harness is draft T-110's.

**Equipment:** a browser emulating 360, 390, 640 and 768px, and the staff code
from `qori:design-review --totp`. No JavaScript test runner: checked by eye.

## Scope

**In:**

- Below `sm`, `admin/Creators.vue` rows put name and slug first, with plan,
  status and seats underneath.
- Below `sm`, `admin/Creator.vue` Series rows put the title first, with the
  status, counts and price underneath.
- Two server tests that the name and title arrive whole.

**Out:**

- The same pattern in `admin/Users.vue`, `admin/User.vue` and
  `admin/Pricing.vue`, which R-004 did not report (first question).
- Creator detail's header, stat grid and Sharing team rows, whose
  `justify-between` and `shrink-0` role already leave the name its width.
- The stale `/w/` before the slug (third question); the `AdminLayout.vue`
  header; touch targets, which T-105 (F-4) sets on sign-in and the Peer page
  only.
- Moving the admin pages' inline English and hardcoded nouns into lang (§13);
  this task adds no strings. Any change to `CreatorDirectory`,
  `ConsoleController`, routes or writes.

## Files

| Path                                       | Change | Notes                                                    |
| ------------------------------------------ | ------ | -------------------------------------------------------- |
| `resources/js/pages/admin/Creators.vue`    | edit   | Row: name and slug first below `sm`; metadata underneath |
| `resources/js/pages/admin/Creator.vue`     | edit   | Series row: title first below `sm`; metadata underneath  |
| `tests/Feature/Admin/ConsolePagesTest.php` | edit   | 2 cases; the `creator()` helper takes a Series title     |

Flows: none — layout classes only; `docs/flows/admin.md` stays true.

## Database

None.

## Code

No new components, props or PHP. Provisional classes, named finally once
checked by eye: identity `min-w-0 grow basis-full sm:basis-0`; metadata `sm:w-20`/`sm:w-24`.

## Copy

None. No sentence is added or changed.

## Routes

None.

## Tests

The server cannot test layout, only that the whole name reaches the page and
any shortening is the browser's (T-039's
`test_a_long_title_reaches_the_page_untruncated`).

**Changed: `tests/Feature/Admin/ConsolePagesTest.php` — 2 new cases**

1. `test_it_sends_a_long_group_name_whole_to_the_creator_list`: a Group name at
   `UpdateGroupRequest`'s 100-character limit reaches `creators.0.name`
   unchanged.
2. `test_it_sends_a_long_series_title_whole_to_the_creator_detail`: a long
   Series title reaches `creator.series.0.title` unchanged.

Total: 2. No existing case changes; `creator()` gains a title defaulting to
`'Getting Started'`.

## Acceptance

- [ ] At 390px in both themes, `520-admin-creators` shows each Group name on
      its own first line, with its slug beneath and plan, status and seats below
- [ ] At 390px in both themes, `530-admin-creator` shows each Series title on
      its own first line, with its metadata below
- [ ] At 390px, The Long Names Collective's detail shows the opening words of
      its longest title
- [ ] At 360px and 768px neither page overflows sideways and no name collapses
- [ ] At 1440px both pages look as they do today
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Do the unreported rows with the same pattern in `admin/Users.vue`,
  `admin/User.vue` (Shared) and `admin/Pricing.vue` (Plans, Coupons) come in?
  The stream owner's (wayne).
- Should a Series title in the detail clamp at two lines or wrap in full? The
  row is not a link, and the console shows the whole title nowhere else. The
  stream owner's.
- Is the stale `/w/` (`Creators.vue:59`, `Creator.vue:73`) fixed here, since
  the share routes are `/g/{group}` (`routes/share.php:25`)? The stream owner's.
- Is `sm` right for the detail row? At 640px its four columns leave the title
  about 150px. Anyone's, with a browser at 640 and 768px.

## Re-scope log

None.

## Notes

None.
