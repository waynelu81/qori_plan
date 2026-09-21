---
id: T-174
title: Making a Series ready lands on its share link
stream: onboarding
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-174 — Making a Series ready lands on its share link

## Why

The share link sits below the Episode form, the details, the price, the
statement copy and the Peers, on one long page, and "Make ready to share" left
the creator at the top with no sign of it (the 21 September 2026 walk, and the
first-share journey's step 10: "the link is at the bottom of a very long
page"). Afterwards, making a Series ready scrolls the page to its share link
and puts focus on the Copy button.

## Decisions taken to make this specifiable

- **In the page, not by a redirect's fragment.** The publish form is an
  Inertia visit; a fragment on the redirect does not survive the XHR that
  follows it, and `useDeepLinkedControl` reads the fragment only on mount and
  on navigation.
- **Watched on the Series' status turning from draft to ready**, not on the
  form's success: the button's form is gone once the Series is ready.
- **The Copy button takes focus**, because copying the link is what comes
  next.

## Preconditions

None.

**Data this task verifies against:** the design-review world's draft
"Notes on Being Interrupted", put back to draft after the walk.

**Equipment:** a browser.

## Scope

**In:**

- Scrolling to the share link and focusing Copy when a Series becomes ready.

**Out:**

- Moving the share link higher on the page — the object hierarchy
  `ui-redesign-next-sprint.md` §2 proposes rebuilding.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `resources/js/pages/share/series/Show.vue` | edit | the watch |

## Database

None.

## Code

A `watch` on `props.series.status`: draft → published scrolls `#share-link`
into view and focuses its button.

## Copy

None.

## Routes

None.

## Tests

None in PHPUnit: the behaviour is the browser's, and the repository has no
browser test harness beyond the e2e journeys. Walked instead.

## Acceptance

- [x] "Make ready to share" ends with the share link in view and Copy focused
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

None.
