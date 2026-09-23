---
id: T-195
title: The three-part setup is retired
stream: onboarding
status: done
owner: claude
estimate: M
depends: T-026
blocks: none
---

# T-195 — The three-part setup is retired

> Cut from `T-026` on 23 September 2026 when `D-056` replaced the three-part
> setup with one first-Series screen; brought to ready and claimed the same
> day.

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

**The dashboard's name card follows `T-177`'s rule** (the owner, 23 September 2026: "yes, rename should change the address until published"). Renaming
moves the slug while no Series of the Group has ever been published, and never
after. `T-177` kept the card from moving it because a link might be out there;
nothing is out there before anything is published, which is the condition
`GroupService::nameInSetup()` already checks. Without it a creator who never
saw part one keeps "alex-s-group" in every link they send.

**The forwarding addresses stay.** `PaymentsDestination` and
`ConnectionsDestination` are how a vendor sends someone back to where they
started, and `T-028` reuses them to bring a creator back to the Series. Only
their setup callers go.

**After a rename that moved the URL, the card lands on the dashboard at the
new one.** The card used to come `back()` to the page it was on, which is the
old URL once the slug moves: a 404. A rename that keeps the slug still comes
back.

**The forwarding addresses' landings keep their code; only their comments
change.** `PaymentsFinaliseController` and `ConnectionFinaliseController` take
the address first and spend it whatever happens. Nothing there is setup's
alone, and `T-028` is the caller now.

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
- `docs/flows/onboarding.md` keeps its first-Series section; only the parts and
  their record go.
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
| `resources/js/layouts/setup/Layout.vue` | delete | The frame; only the two parts used it |
| `resources/js/app.ts` | edit | The `share/setup/` layout case |
| `resources/js/components/share/GroupNameForm.vue` | edit | The `setup` prop and hidden field |
| `app/Http/Controllers/Settings/ConnectionFinaliseController.php`, `app/Http/Controllers/Share/ConnectionsController.php` | edit | Comments that name setup |
| `docs/tinker/groups.md`, `docs/flows/storage.md`, `docs/flows/billing.md` | edit | Setup's parts leave the docs |
| `tests/Feature/Share/OnboardingHomeTest.php`, `tests/Feature/ShareDigestTest.php` | edit | Only if a rename there now moves a slug they read |
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

**Changed: `tests/Feature/Share/SetupTest.php`** — the three `setup`-flag
naming cases become the card's: `test_naming_the_group_from_the_card_moves_the_url_before_anything_is_published`,
`test_naming_the_group_takes_the_next_free_url`,
`test_a_group_that_has_published_keeps_its_url_when_renamed`; the two that
skipped parts use `finish()`; new `test_the_retired_parts_of_setup_answer_404`.

**New in `tests/Feature/Series/SeriesReturnTest.php`:**
`test_integrations_reached_any_other_way_clears_both_addresses`.

**Deleted:** `tests/Feature/Share/SetupStepsTest.php`.

**Changed:** `ConnectionAccountChangeTest`, `ConnectionsConnectTest`,
`PaymentsOauthTest` — the address they plant is a page that still exists.

## Acceptance

- [x] No setup URL but `share.setup` and its two writes answers
- [x] Renaming from the dashboard's card moves the URL until something is
      published, and never after
- [x] `qori:reachability` names none of the removed pages
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Added during execution

- `app/Http/Controllers/Share/IntegrationsController.php` — with setup's part
  three gone, nothing leaves a forwarding address and then links to
  Integrations, so a plain visit now clears both (D-017); `T-028`'s decision
  to leave them was only for part three.
- `tests/e2e/support/creator.ts`, `tests/e2e/core-loop.spec.ts`,
  `tests/e2e/first-share.spec.ts`, `app/Console/Commands/EndToEndCommand.php`,
  `docs/tinker/e2e.md` — the browser journeys walked the three parts (name,
  skip payments, finish) and had been failing since `T-026`; they now land on
  the first-Series screen, look around first, and name the Group from the
  dashboard.
- `tests/Feature/Share/GroupRenameTest.php` — pinned that a rename never
  moves the slug; it now arranges a published Series first.
- `docs/flows/README.md`, `docs/tinker/connections.md`,
  `docs/tinker/design-review.md` — lines that named the parts.
- `app/Support/PaymentsDestination.php`, `app/Support/ConnectionsDestination.php`
  — docblocks that described setup as the caller.

## Re-scope log

None.

## Notes

None.
