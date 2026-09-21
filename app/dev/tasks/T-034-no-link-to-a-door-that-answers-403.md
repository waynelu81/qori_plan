---
id: T-034
title: The Payments page stops linking a non-owner to billing
stream: design
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-034 — The Payments page stops linking a non-owner to billing

## Why

`R-002` F-2. The Payments page ends with "Looking for what you pay Qori? That's
on **Plan and billing**", and the link is unconditional.
`BillingController` throws `errors.billing.owner_only` for anybody who is not the
Group's owner (§15), and `AppSidebar` already hides the billing nav item from
them. So an invited admin is shown a door in one place, has it hidden in
another, and is refused when they use it.

`PLAN.md`'s beta gate says no built-in action may knowingly lead to a predictable 403. The refusal itself is good — R-002 records that the billing page names the
owner as the person who can act and offers a way back — but a page should not
send somebody there to read it.

## Decisions taken to make this specifiable

**Say who handles it rather than removing the sentence.** An admin looking for
what the Group pays has a real question, and deleting the paragraph leaves them
with no answer at all. The existing refusal copy already knows the answer: "Ask
whoever owns this group to make the change." The page can say the same thing
before the click instead of after it.

**Read `auth.currentGroup.isOwner`, not a new prop.** It is already on every
page through `HandleInertiaRequests`, and `useShareContext()` already exposes it
— which is how `AppSidebar` gates the same item. A controller change would add a
second source for one fact.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The billing link on the Payments page, shown to owners only.
- A sentence for everybody else that answers the question without a link.
- A test asserting a non-owner is not offered the link.

**Out:**

- The billing refusal itself, which is correct.
- The other `R-002` findings. F-1 is `T-033`, done; the rest are unrouted.
- Auditing every other link in the product for the same shape. Worth doing and
  it is a `reachability` pass rather than a one-line fix — noted in the report.

## Files

| Path                                      | Change | Notes                                |
| ----------------------------------------- | ------ | ------------------------------------ |
| `resources/js/pages/share/Payouts.vue`    | edit   | Gate the link, and the fallback line |
| `tests/Feature/Share/PayoutsPageTest.php` | new    | 3 cases                              |

## Database

None.

## Code

```vue
// resources/js/pages/share/Payouts.vue import { useShareContext } from
'@/composables/useShareContext'; const { current } = useShareContext(); const
isOwner = computed(() => current.value?.isOwner === true);
```

`=== true` rather than a truthiness check: `isOwner` is optional on `GroupRef`,
and an absent value must read as "not the owner" rather than as unknown.

The owner keeps the sentence and the link. Everybody else gets the same question
answered without one, in the words the refusal already uses: what they pay Qori
is the owner's to see, and the owner is who to ask.

## Copy

Vue templates keep their inline English (§13's unwired i18n, tracked in `T-006`).
The new sentence must not be a fourth wording of a fact `errors.billing.owner_only`
already states — keep it recognisably the same sentence.

## Routes

None.

## Tests

**New: `tests/Feature/Share/PayoutsPageTest.php` — 3 cases**

The page is Vue and there is no JavaScript test runner, so what is asserted is
the prop the template branches on. That is the honest limit and the report
should say so.

1. `test_the_owner_is_told_they_own_billing` — `auth.currentGroup.isOwner` is
   true for the owner on the Payments page.
2. `test_an_admin_is_not` — false for an invited admin on the same page, which
   is the branch that hides the link.
3. `test_an_admin_who_follows_the_link_anyway_is_still_refused` — the guard is
   the rule and the template is the courtesy. Posting straight at
   `share.billing` as an admin still fails.

**Changed:** none expected.

## Acceptance

- [x] An invited admin is not offered a billing link on the Payments page
- [x] They are still told who to ask
- [x] The owner's link is unchanged
- [x] `BillingController` still refuses a non-owner regardless
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**The route is `share.payouts.show`, not `share.payouts`.** The Tests section
implied the shorter name and the suite said so immediately. A one-word fix and
not a re-scope.

**Both branches were checked in a browser**, seated as a real admin in a real
Group: no billing link anywhere on the page, and the footer reading "That's the
owner's to see — ask whoever owns this Group." The owner's link is unchanged.

The sidebar has gated this item since it was written. The footer was added later
and did not inherit the rule, which is the ordinary way a permission boundary
develops a hole: the second place to mention a capability does not know the
first place had a condition on it.
