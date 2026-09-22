---
id: T-006
title: Convert the remaining inline English in Vue to lang keys
stream: language
status: draft
owner: unassigned
estimate: L
depends: none
blocks: none
---

# T-006 — Convert the remaining inline English in Vue to lang keys

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

Vue templates still hold inline English (§13's unwired i18n). Every noun now resolves through the vocabulary, but the sentences around them do not, so a second locale is still a hunt through the codebase rather than a translation file.

## Scope

**In:**

- Moving user-visible strings out of `.vue` files into `lang/en/*.php`.
- A `useLang()`-shaped reader on the client, or the strings passed as props — whichever is chosen.

**Out:**

- A second locale. This makes one possible; it does not add one.

## Before this can be ready

- Decide how Vue reads lang: a shared Inertia prop carrying the page's strings, or a client-side dictionary. This is the whole design and it is not made.
- Estimate is L, which per PROCESS.md usually means it should be several tasks. Split it by page group before making it ready.

## Re-scope log

None.

## Notes

- The admin console's pages hold their labels inline too, for example
  `resources/js/pages/admin/Pricing.vue`. `T-169` (22 September 2026) started
  `lang/en/admin.php`, with its new labels passed to the page as props; the
  console's older labels are the rest of that file's job.
- `resources/js/components/auth/LinkSent.vue` still says "Use a different
  email" inline. The sign-in composition's second step says the same words
  from `auth.sign_in.change_email` (`T-087`), so that key is the one to use.
