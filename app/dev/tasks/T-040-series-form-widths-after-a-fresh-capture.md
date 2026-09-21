---
id: T-040
title: Bring the Series and access form widths into the page rhythm
stream: design
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-040 — Bring the Series and access form widths into the page rhythm

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to happen before it can be marked
> `ready` is at the bottom, and in this case it is a measurement rather than a
> decision.

## Why

`R-002` F-6, at desktop width. The New Series fields — including the short
numeric Hours field — span almost the whole content panel, as does the "Give
someone access" email field, unlike the bounded Group-name and account forms.
The redesign brief says a form must not stretch merely because space exists.

## Scope

**In:**

- Constraining those form interiors to the readable form width already used
  elsewhere, while keeping the shared page and panel alignment.

**Out:**

- The Series edit form, which `T-031` already bounded at `sm:max-w-xl`.
- Changing the panel or page geometry, which `R-002` records as holding up.

## Before this can be ready

- **A fresh capture.** This is the one finding `R-002` explicitly flags as at
  risk of being stale: `T-030` and `T-031` changed these exact forms during the
  review, and the pass says its run "no longer establishes the latest
  working-tree UI". Re-run `php artisan qori:design-review` and look at the
  Series screens before specifying anything.
- **Decide what the readable form width is, once.** `T-031` chose `sm:max-w-xl`
  for the Series edit form by matching `GroupNameForm`'s `sm:max-w-md` in spirit
  rather than by measuring. Two forms with two different bounds is the same
  drift in a smaller font. This should become a named token or a documented
  class rather than a third judgement call.

## Re-scope log

None.

## Notes

Whoever picks this up should read `ui-redesign-next-sprint.md` §4 first, which
proposes the same constraint as part of a wider hierarchy pass. If that sprint is
about to run, this belongs inside it rather than ahead of it.

**17 September 2026 — [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-11.** Fresh `220-series-index`, `605-empty-series-index` and `635-one-series-index` desktop captures reconfirm the broad New Series form; the access form is broad too. Live at 1440px, both Title and Hours measured 934px. The old capture-staleness concern is resolved for these observations; the shared readable-width decision is not. Keep the existing exclusion of the Series edit form and decide the named form-interior rule with the next-sprint composition once.
