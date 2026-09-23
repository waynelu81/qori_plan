---
id: T-195
title: The three-part setup is retired
stream: onboarding
status: draft
owner: unassigned
estimate: M
depends: T-026
blocks: none
---

# T-195 — The three-part setup is retired

> **Draft.** Cut from `T-026` on 23 September 2026 when `D-056` replaced the
> three-part setup with one first-Series screen. What has to be decided before
> it can be marked `ready` is at the bottom.

## Why

After `T-026`, nothing sends anyone to setup's parts two and three, and part
one's name form is no longer the page at `share.setup`. What is left is code
with no way in: two pages, three routes, `SetupSteps`, the frame, the
`setup` flag on `GroupController`, and `User::onboardingNext()`, which still
decides nothing but is still read. `qori:reachability` will find the pages.

Afterwards they are gone, and the one thing part one did that nothing else
does moves: naming the Group gave it the URL of its new name while nothing had
been published (`T-177`). The dashboard's name card is now the only place a
Group is named, so it takes that rule.

## Decisions taken to make this specifiable

**The dashboard's name card follows `T-177`'s rule** (proposed). Renaming
moves the slug while no Series of the Group has ever been published, and never
after. `T-177` kept the card from moving it because a link might be out there;
nothing is out there before anything is published, which is the condition
`GroupService::nameInSetup()` already checks. Without it a creator who never
saw part one keeps "alex-s-group" in every link they send.

**The forwarding addresses stay.** `PaymentsDestination` and
`ConnectionsDestination` are how a vendor sends someone back to where they
started, and `T-028` reuses them to bring a creator back to the Series. Only
their setup callers go.

**The name record stays; the other two keys go.** `Group::hasChosenName()`
reads `onboarding_state.name`, and the dashboard's card depends on it.
`payments` and `storage` are no longer written or read.

## Preconditions

**Data this task verifies against:** a Group with no Series and an unnamed
Group with a published Series, for the slug rule.

**Equipment:** a browser, to confirm the name card and that no setup URL but
`share.setup` answers.

## Scope

**In:**

- Removing `SetupController::payments()`, `storage()`, `skip()` and
  `finish()`, their routes, `resources/js/pages/share/setup/Payments.vue` and
  `Storage.vue`, the frame, and `App\Support\SetupSteps`.
- `User::onboardingNext()` and `OnboardingService::skip()` and `complete()`,
  replaced by recording the name alone.
- The `setup` flag on `GroupController::update()`, and the card taking
  `T-177`'s slug rule.
- The setup lines in `lang/en/groups.php` that nothing reads, the design
  review's `692` and `693`, and the two fixups about parts one and three in
  `fixups.md`, which go with the pages.

**Out:**

- The forwarding addresses themselves (`T-028`).
- Dropping `users.onboarding_state`; the name record lives there.

## Files

| Path | Change | Notes |
| ---- | ------ | ----- |
| `app/Http/Controllers/Share/SetupController.php` | edit | Four actions go |
| `routes/share/setup.php` | edit | Four routes go |
| `app/Support/SetupSteps.php` | delete | |
| `resources/js/pages/share/setup/Payments.vue`, `resources/js/pages/share/setup/Storage.vue` | delete | |
| `app/Models/User.php` | edit | `onboardingNext()` goes |
| `app/Models/Group.php` | edit | `hasChosenName()` without `SetupSteps` |
| `app/Services/OnboardingService.php` | edit | `recordName()` replaces `skip()` and `complete()` |
| `app/Services/GroupService.php` | edit | `rename()` takes the slug rule; `nameInSetup()` folds into it |
| `app/Http/Controllers/Share/GroupController.php` | edit | No `setup` flag |
| `app/Http/Controllers/Settings/PaymentsFinaliseController.php` | edit | The comment and any setup branch |
| `app/Console/Commands/DesignReviewCommand.php` | edit | `692`, `693` go |
| `lang/en/groups.php` | edit | Unread `setup.*` lines go |
| `docs/flows/onboarding.md` | edit | The parts go |
| `tests/Feature/Share/SetupStepsTest.php` | delete | |
| `tests/Feature/Share/SetupTest.php`, `tests/Feature/Share/ConnectionAccountChangeTest.php`, `tests/Feature/Share/ConnectionsConnectTest.php`, `tests/Feature/Share/PaymentsOauthTest.php` | edit | The cases that start from part three |

## Database

None.

## Code

To be settled when ready.

## Copy

None new. Lines removed from `lang/en/groups.php` under `setup.*` once
nothing reads them.

## Routes

Removed: `share.setup.payments`, `share.setup.storage`, `share.setup.skip`,
`share.setup.finish`.

## Tests

To be written when ready: renaming from the card moves the slug before
anything is published and keeps it after; the four removed URLs answer 404;
the forwarding-address cases that started from part three start from the
Series page instead, or from Integrations.

## Acceptance

- [ ] No setup URL but `share.setup` and its two writes answers
- [ ] Renaming from the dashboard's card moves the URL until something is
      published, and never after
- [ ] `qori:reachability` names none of the removed pages
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- The card taking `T-177`'s slug rule. (the owner's, since it changes the
  link a creator shares; proposed yes)
- Which of `PaymentsFinaliseController`'s and `ConnectionFinaliseController`'s
  branches exist only for setup. (anyone's, from the code)
- Name the cases in the three connection and payment test files that start
  from part three. (anyone's)

## Re-scope log

None.

## Notes

None.
