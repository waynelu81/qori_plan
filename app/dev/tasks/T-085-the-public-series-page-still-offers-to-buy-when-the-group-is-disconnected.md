---
id: T-085
title: The public Series page still offers to buy when the Group is disconnected
stream: selling
status: draft
owner: unassigned
estimate: S
depends: T-058
blocks: none
---

# T-085 — The public Series page still offers to buy when the Group is disconnected

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 14 September 2026 from
> two reports that met the same thing: `T-064` and `T-074`.

## Why

`T-064` gave a creator a way to disconnect Stripe. The public page does not
know: `PublicSeriesController::show()` sends `isFree`, `priceCents` and
`currency`, and `public/Series.vue` renders the buy button from those alone.
A buyer who presses it reaches `CheckoutService`'s guard,
`errors.checkout.not_connected`, as a refusal after the click — the shape
`PLAN.md`'s beta gate forbids by name: a built-in action that knowingly leads
to a predictable refusal. Both reports said it wants a task of its own, after
`T-058`, because the money line on that page is what `T-058` rewrites.

Afterwards, a paid Series whose Group cannot take payment does not offer to
take one: the page says so in a sentence, and the creator's own Series page
says the same beside the price.

## Scope

**In:**

- A prop from `PublicSeriesController` saying whether the Group can be paid
  (`connect_account_id` present and the account's `charges_enabled`, read the
  way the Integrations page reads it).
- The public page replaces the buy button with one sentence from lang when it
  cannot; a free Series is unaffected.
- The creator's Series page shows the same fact beside the price, so the
  creator learns it before a buyer does.

**Out:**

- Re-enabling payouts, which is the Integrations page's job.
- Anything about a paused Group (`errors.access.not_accepting`), which is the
  older refusal and already has its own sentence.

## Before this can be ready

- Decide whether "can be paid" means an account id exists, or means
  `charges_enabled` on a read of that account. The first is a column read and
  can lie for an account whose onboarding stopped; the second is a Stripe
  call per page view unless the answer is cached on the Group, which `T-072`'s
  descriptor read already does for another field.
- Decide the sentence, and whether it names the creator ("Ruff Club is not
  taking payments yet") or stays neutral.
- Confirm `T-058` has landed, so the price line this edits is the shared one.

## Re-scope log

None.

## Notes

`T-064`'s report and `T-074`'s report; `T-074`'s case 4 is what a buyer meets
today.
