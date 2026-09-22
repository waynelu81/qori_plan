---
id: T-182
title: Every page renders the same on the server and in the browser
stream: design
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-182 — Every page renders the same on the server and in the browser

## Why

Every page logs "Hydration completed but contains mismatches" in the browser's
console, once per load: the Series list, a Series, the invitations page on 22
September 2026 (`T-043`'s walk), and the dashboard, Billing and the home page
when `T-046`'s report first recorded it on 12 September and said it needed a
task. A mismatch means the markup the server rendered and the browser's first
render disagree, which is how a page shows the wrong state until something
touches it. Afterwards no page logs one.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

## Scope

**In:**

- Finding what differs between the server's render and the browser's first
  one, on every page, and making them agree.

**Out:**

- Anything a page shows on purpose only in the browser, which renders after
  hydration rather than differently during it.

## Files

To be settled when ready.

## Database

None.

## Code

To be settled when ready.

## Copy

None.

## Routes

None.

## Tests

To be settled when ready.

## Acceptance

- [ ] No page logs a hydration mismatch in a clean browser, at mobile and desktop widths
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- What differs: Vue logs the node in development builds, so one page read in
  the dev server names the culprit. Common ones are a date formatted in the
  server's zone and the browser's, the theme read from `localStorage`, and
  anything reading `window`.
- Whether one shared cause — the app shell, the theme — explains every page.
- Found on the public Series page, 22 September 2026 (`T-181`): every price.
  The server renders "$89.00" and the browser "A$89.00", because
  `formatMoney()` in `resources/js/lib/money.ts` formats in the runtime's own
  locale, which differs between the server's render and the visitor's
  browser. Whether other pages differ for the same reason — dates are the
  likely next one — is the rest of this task.

## Re-scope log

None.

## Notes

Found again during `T-043`'s browser walk, 22 September 2026.
