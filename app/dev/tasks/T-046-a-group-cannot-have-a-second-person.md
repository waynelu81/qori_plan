---
id: T-046
title: Stop showing a seat count nobody can change
stream: reachability
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-046 — Stop showing a seat count nobody can change

## Why

`collaborators` is seat-capped at **1 on the free plan and 20 on every paid
one** (`config/qori.php`). The model exists, the role enum exists, the admin
console counts seats, and the Billing page shows the creator **"Team members:
1 of 20"**.

**Nothing creates a collaborator except `CreateGroupForNewUser`**, which adds the
person who made the Group. There is no route, no controller and no page for
inviting a second. Nineteen of those twenty seats cannot be filled by anybody
who pays for them.

## The owner's decision, 11 September 2026

> Collaborators are staff from the creator, not the creator's Peers who are
> invited or sold to the Series. Without collaborators, the creator as owner —
> one user — is enough to manage the workspace.

**So collaborators are deferred, and this task is no longer about building
them.** What remains is that the product tells a paying creator they have twenty
seats, and they have one. That is the part worth fixing today, and it is small.

## Decisions taken to make this specifiable

**Hide the number, keep the limit.** `team_members` stays in `config/qori.php`
because the cap is real and `guardPeerLimit`-style checks may read it later.
What goes is the row on the Billing page that reports a fraction of a thing
nobody can move.

**Hide, not zero, and not "coming soon".** A row reading "1 of 1" is a smaller
lie that is still a lie. A row promising a date is a commitment nobody has made.
The honest rendering of a feature that does not exist is nothing.

**The admin console keeps its seat counts.** Staff are reading what the database
holds, not being sold anything, and the count is true there.

**This is not a pricing change.** Nothing about what a plan costs or what it
includes moves. The plans do not advertise seats on the public pricing page —
checked — so the only place the claim is made to a paying customer is the
Billing page inside their own Group.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The "Team members" row on the Billing page.
- The seat figure on the Share dashboard digest, if it is shown there.
- A decision record, so this is a choice somebody can find rather than a gap.

**Out:**

- Building collaborator invitations. Deferred by owner decision; reopen with a
  new task if that changes.
- `config/qori.php`'s limits, which stay.
- The admin console.
- The `Collaborator` model, the role enum and everything that reads them. The
  owner record is a real row and the Group needs it.

## Files

| Path                                      | Change | Notes                                        |
| ----------------------------------------- | ------ | -------------------------------------------- |
| `resources/js/pages/share/Billing.vue`    | edit   | Drop the "Team members" row                  |
| `resources/js/pages/share/Dashboard.vue`  | edit   | Drop `seats` from the `Digest` type          |
| `app/Services/ShareDigest.php`            | edit   | Stop sending `seats` to the creator surfaces |
| `docs/planning/decisions.md`              | edit   | The deferral, dated, with the reason         |
| `tests/Feature/Share/BillingPageTest.php` | edit   | 1 case                                       |

**The Share dashboard already stopped rendering it.** Its docblock records that
"Your role" and "Team members" left the grid during the redesign, because a
first-run dashboard leading with "Owner, 1 of 1 seats" tells a creator nothing
they can act on. Only the TypeScript type still names it. The Billing page is
where the claim is still made.

`tests/Feature/Share/GroupSeatsTest.php` is **not** in this list and must not
change. It tests `seatsUsed()`, the cap and the owner seat at the model level;
all of that stays true and stays enforced. What this task removes is a number
shown to somebody who cannot act on it, not the rule behind it.

Check `DefinitionList.vue`'s docblock, which names seats among what the Billing
page shows. If it still does afterwards, the comment is wrong.

## Database

None. `collaborators` is unchanged and still holds the owner.

## Code

No new code. A prop stops being sent and two rows stop being rendered.

**Read `ShareDigest` before removing `seats` from it.** If the admin console's
queries share that shape, the console must keep its count — take it out of the
creator-facing payload only, not out of the class.

## Copy

None removed from lang. The Billing row's label is inline English (§13's unwired
i18n) and goes with the row.

## Routes

None.

## Tests

**Changed: `tests/Feature/Share/BillingPageTest.php` — 1 new case**

1. `test_the_billing_page_does_not_report_a_seat_count` — asserts the prop is
   **absent** rather than zero, so bringing it back is a deliberate act rather
   than a prop quietly reappearing.

No existing test asserts the digest's `seats` prop, so nothing should need
changing. `GroupSeatsTest`'s six cases must all still pass untouched; if one
does not, something removed a rule rather than a display.

## Acceptance

- [x] The Billing page shows no seat count **in its usage list** — two other
      claims on the same page survive, see the first entry under Notes
- [x] The Share dashboard shows no seat count
- [x] `config/qori.php` still carries the limits
- [x] The admin console still counts seats
- [x] The deferral is written in `decisions.md`, dated, with the owner's reason
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

**2026-09-11 — the owner answered the question this task was asking.** It was
drafted as "a Group cannot have a second person in it", with building
collaborator invitations as the assumed work and a note that deferring them was
the cheaper answer. The owner took that answer: one user manages the workspace,
and collaborators are the creator's own staff rather than anything the core loop
needs. What was left was the visible claim, which is this task.

## Notes

`lang/en/billing.php` still holds `plans.seats` and `plans.seats_unlimited`,
with a comment explaining that a team member is a seat on a plan rather than a
product noun. Leave them. They are correct lines describing a plan, and they are
not rendered to a creator by anything this task touches — deleting copy because
one caller stopped calling it is how a lang file loses the line the next caller
needed.

**The Billing page makes the seat claim in three places and this task named
one.** The usage list is gone. Two remain, and neither is in the Files table, so
both were left as the Scope requires:

1. `BillingController::limitLines()` builds the feature bullets for the
   synthesised current-plan card and includes `billing.limits.seats` — "20 team
   members" on a paid plan with no public price row. The Notes below say to
   leave those lang lines because nothing this task touches renders them. That
   is wrong: this controller renders them, on this page.
2. `subscription_prices.features` is owner-authored data. The development
   fixture seeds "1 studio login" and "20 studio logins", and both render on the
   Billing page today. Data, not code, so no task can fix it — the owner
   decides what a plan card claims.

Neither was checked when this task was written, which is also why the
"Decisions" section could say the claim is made in exactly one place. Worth its
own task, or an owner decision on the plan copy.

**The Notes name the wrong lang keys.** They are `billing.limits.seats` and
`billing.limits.seats_unlimited`, not `plans.seats`. The instruction to leave
them stands either way.
