---
id: T-088
title: The public pricing page uses the one money formatter
stream: design
status: draft
owner: unassigned
estimate: S
depends: T-058
blocks: T-104
---

# T-088 — The public pricing page uses the one money formatter

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

`T-058` put every amount the product shows through `formatMoney()` in
`resources/js/lib/money.ts`, except the public pricing page,
`resources/js/pages/Pricing.vue`. The owner kept that page out on 15 September
2026: it goes through another round of design review before anyone changes it.

It is also the one formatter that trims ".00" from a whole price
(`minimumFractionDigits: price.amountCents % 100 === 0 ? 0 : 2`), so a plan
reads "$19" there and would read "$19.00" through `formatMoney()` as it
stands. `MoneyFormatterTest::ownFormatter()` names the page with that reason,
and its second case fails once the page stops building its own formatter, so
the entry goes with this task.

## Scope

**In:**

- `resources/js/pages/Pricing.vue` calling `formatMoney()`.
- Removing the page from `ownFormatter()` in
  `tests/Feature/Design/MoneyFormatterTest.php`.

**Out:**

- Anything else the design review asks of the page; that is its own task.

## Before this can be ready

- The pricing page's design review (the owner's).
- Whether a whole price drops ".00": on this page only, which means an option
  on `formatMoney()`; everywhere, which means the rule moves into
  `formatMoney()` and changes the Series pages, Billing and admin; or nowhere,
  which means this page shows "$19.00" (the owner's).

## Re-scope log

None.

## Notes

None.

**17 September 2026 — [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-2.** Fresh `020-pricing` images show `$19/month` and `$49/month` without a currency identifier; the represented rows are USD while public Series explicitly show A$. Currency must be unambiguous. Design recommendation: use the shared formatter, name USD, and retain its current precision for this first correction rather than introduce an exceptional display rule. The owner still decides whole-price precision; this note does not mark that decision made. The review also found missing public navigation (F-3) and unsupported catalogue benefits (F-1); both remain outside this task's narrow scope. The review prerequisite now has fresh evidence, but this is not owner approval to make the task ready.
