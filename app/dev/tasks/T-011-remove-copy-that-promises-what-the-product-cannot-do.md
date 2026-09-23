---
id: T-011
title: Remove copy that promises what the product cannot do
stream: recovery
status: draft
owner: unassigned
estimate: S
depends: T-009, T-010
blocks: none
---

# T-011 — Remove copy that promises what the product cannot do

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

The over-cap notice offers 'or delete the ones you're no longer sharing', which nothing in the product could do until this stream. There are likely more of these.

## Scope

**In:**

- An audit of copy that names an action, against the actions that exist.
- Rewriting or removing each one that does not.
- **`AppException::resolution()`'s fallback.** It falls back to the ErrorCode's
  generic resolution when the specific lang key omits one, so an omission §23
  calls deliberate ("this path is final") is undone one level up:
  `errors.access.series_unavailable` says there is nothing to retry and the
  reader is told "Check the link, or go back and try again." Found while
  building `T-002`, which made resolutions visible on page loads for the first
  time. It also feeds the JSON payload and every toast, so it is a wider change
  than it looks.

**Out:**

- Building the missing capability. If the copy describes something worth having, it becomes its own task.

## Before this can be ready

- ~~`T-009` and `T-010` land first — they turn some of these promises true, and
  the audit should run against the finished product rather than the current
  one.~~ **Satisfied 14 September 2026:** both are done. `T-009` made two of
  the promises true and `T-010` added deletion, which is the other word the
  copy has been using. The audit can run against the product as it is.
- Decide whether `resolution()` should stop falling back, or whether the lang
  files should say `'resolution' => null` explicitly where the omission is
  meant. The second is more typing and much harder to get wrong by accident.

## Re-scope log

None.

## Notes

None.

**17 September 2026 — [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-1/F-7.** The fresh local pricing catalogue advertises “20 studio logins” and “Public listing”; post-visual inspection traces these to PricingSeeder/database benefits, not proof of deployed production data. Check the release catalogue as well as the fixture against deferred collaborators and invitation-led scope. The paid A$89.00 Series also says “Type it here and you're in” about its verification code although payment follows. These are audit evidence for this draft, not permission to build the promised capabilities or a change to its status.

**23 September 2026.** The paid Series' "Type it here and you're in" is
`T-027`'s: it adds `accesses.join.intro_paid`, which says the code confirms
the address and payment follows. One more promise for this draft's audit,
found while specifying `T-027`: the public page badges an Episode "Preview"
(`resources/js/pages/public/Series.vue:516-520`) and nothing lets a guest open
one.
