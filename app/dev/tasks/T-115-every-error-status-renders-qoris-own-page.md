---
id: T-115
title: Every error status renders Qori's own page
stream: recovery
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-115 — Every error status renders Qori's own page

## Why

`AppException::render()` shows an error's own message and resolution on a page
load only when `resources/views/errors/{status}.blade.php` exists; otherwise it
aborts, and Laravel shows its bare page with no copy and no way back. `T-113`
found this for its new refusals and added views for 400, 422 and 502. The
statuses `ErrorCode` can still produce with no view — 401, 402 and 504 today —
still reach a person as the bare page in production, where debug is off, and
`docs/architecture/errors.md` says a failed page load carries the public
message. The design review renders only 403, 419, 429, 500 and 503
(`DesignReviewCommand`), so none of the added pages has been looked at either.

Afterwards every status an `AppException` can carry renders Qori's page with
its message, and the design review captures each of them.

## Decisions taken to make this specifiable

To be written once the question below is answered.

## Preconditions

To be written.

## Scope

**In:**

- To be written.

**Out:**

- To be written.

## Files

To be written.

## Database

None.

## Code

To be written.

## Copy

To be written.

## Routes

None.

## Tests

To be written.

## Acceptance

- [ ] To be written
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- One view per status, or `AppException::render()` falling back to
  `errors.layout` whenever the status has no view of its own. Anyone's.
- Which statuses the design review should capture beyond today's five.
  Anyone's.

## Re-scope log

None.

## Notes

None.
