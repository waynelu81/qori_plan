---
id: T-076
title: Onboarding progress lives on the person, and the home route honours it
stream: onboarding
status: done
owner: claude
estimate: M
depends: T-075
blocks: T-078
---

# T-076 — Onboarding progress lives on the person, and the home route honours it

## Why

The owner registered afresh on 13 September 2026 and opened the verification
mail in a second tab. That tab landed on part one of setup, as `T-075` meant.
Back in the first tab, still showing "we sent a link", they refreshed — and
were on the dashboard, with setup never walked. Fortify's verification page,
asked for by somebody already verified, answers `redirect()->intended()` to
`fortify.home`, which is the home route, and the home route renders the home.
Every door `T-068` and `T-075` closed was a door of Qori's; this one is the
framework's, and the fix is not another door but the room: the home route
itself sends an owner whose onboarding is unfinished to the part they are on.

The same review gave a direction: the record of onboarding progress belongs
on the User, not the Group. Onboarding is a person's journey, a person owns
one Group, and a record on the person is what a progress experience on the
dashboard would read later. `T-075` put `setup_state` and `setup_completed_at`
on `groups`; this task moves them.

## Decisions taken to make this specifiable

**The facts stay where they are; the record moves.** Whether the name was
chosen is `groups.name_set_at`; whether Stripe is connected is
`groups.connect_account_id`. Whether a part was skipped or finished is the
person's, on `users.onboarding_state` and `users.onboarded_at`. So the
question is `User::onboardingNext(Group $group): ?string`, asked of the owner
about their Group, and `Group::setupNext()` goes.

**Creating a Group starts onboarding.** `GroupService::createFor()` clears the
owner's record, so "start sharing" for a learner begins the walk, and a
factory User — set up by default, like a factory Group — becomes a fresh owner
the moment a Group is made for them.

**Two home routes honour it.** `GET /dashboard` and `GET /g/{group}` redirect
an owner with an unfinished part to that part. Nothing else does: the frame's
own exits are Continue and Set this up later, and an owner who types a deeper
URL mid-setup is not fought. Admins are never redirected.

**One service for the writes.** `OnboardingService::skip()` and `complete()`,
taking the person and the Group; `GroupService` loses `skipSetup()` and
`completeSetupPart()`.

## Preconditions

`T-075` done.

## Scope

**In:**

- The two user columns, the migration's data step from the group columns, and
  the group columns dropped.
- `User::onboardingNext()`, `User::isOnboarded()`, `OnboardingService`.
- The home-route rule on both homes.
- The factory defaults and the seeder's owners.
- `docs/flows/auth.md`, `docs/tinker/groups.md`, `decisions.md`.

**Out:**

- A progress experience on the dashboard. This task makes it readable.
- Any change to what the three parts ask.

## Files

| Path                                                                          | Change | Notes                                                 |
| ----------------------------------------------------------------------------- | ------ | ----------------------------------------------------- |
| `database/migrations/2026_09_14_000001_move_onboarding_progress_to_users.php` | new    | Two columns on, two off, data carried                 |
| `app/Models/User.php`                                                         | edit   | Casts; `onboardingNext()`; `isOnboarded()`            |
| `app/Models/Group.php`                                                        | edit   | `setupNext()` removed                                 |
| `app/Services/OnboardingService.php`                                          | new    | `skip()`, `complete()`                                |
| `app/Services/GroupService.php`                                               | edit   | Setup writes removed; `createFor()` starts onboarding |
| `app/Http/Controllers/Share/SetupController.php`                              | edit   | The person; `OnboardingService`                       |
| `app/Http/Controllers/Share/GroupController.php`                              | edit   | The person's next part                                |
| `app/Http/Controllers/HomeController.php`                                     | edit   | Redirect while onboarding is unfinished               |
| `app/Http/Controllers/Share/DashboardController.php`                          | edit   | Same, for the owner                                   |
| `app/Support/SignInLanding.php`                                               | edit   | Asks the person                                       |
| `database/factories/UserFactory.php`, `GroupFactory.php`                      | edit   | Defaults and states                                   |
| `database/seeders/DesignReviewSeeder.php`                                     | edit   | Owners set up; Sage not                               |
| `docs/flows/auth.md`, `docs/tinker/groups.md`, `docs/planning/decisions.md`   | edit   |                                                       |
| `tests/Feature/Share/OnboardingHomeTest.php`                                  | new    | 6 cases                                               |
| `tests/Feature/Share/SetupStepsTest.php`, `SetupTest.php`                     | edit   | The record is the person's                            |

## Database

`users.onboarding_state` jsonb not null default `'{}'`; `users.onboarded_at`
timestamp nullable. Data step: for every Group with `setup_completed_at` set,
its owner gets the Group's `setup_state` and `setup_completed_at`. Then
`groups.setup_state` and `groups.setup_completed_at` are dropped. `down()`
reverses the shape without carrying data back.

## Code

```php
// App\Models\User
/** The first part of setup with no answer for this Group, or null. */
public function onboardingNext(Group $group): ?string;   // null when onboarded_at is set; name done when the Group has a chosen name; payments done when connected
public function isOnboarded(): bool;
```

```php
namespace App\Services;

class OnboardingService
{
    public function skip(User $user, Group $group, string $part): User;
    public function complete(User $user, Group $group, string $part): User;
    // both: validate against SetupSteps::PARTS, write onboarding_state, stamp onboarded_at when onboardingNext() is null
}
```

```php
// App\Http\Controllers\HomeController::index() — first thing
$owned = Group::query()->where('owner_user_id', $peer->getKey())->first();
if ($owned instanceof Group && ($next = $peer->onboardingNext($owned)) !== null) {
    return redirect()->to(SetupSteps::url($owned, $next));
}
// App\Http\Controllers\Share\DashboardController::show() — the same, when $current->isOwner()
```

`UserFactory::definition()` gains `onboarding_state` with every part answered
and `onboarded_at => now()`; a `notOnboarded()` state clears both.
`GroupFactory` loses the two columns and `unnamed()` only clears
`name_set_at`.

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/Share/OnboardingHomeTest.php` — 6 cases**

1. `test_the_home_route_sends_an_owner_with_unfinished_onboarding_to_setup` —
   fresh owner, GET `dashboard`: 302 to `share.setup`.
2. `test_the_group_home_sends_its_owner_to_setup_too` — GET `share.dashboard`:
   302 to the first unfinished part.
3. `test_refreshing_the_verification_page_once_verified_ends_on_setup` — the
   owner's walk: verified owner GETs `verification.notice` following
   redirects; the final page is `share/Setup`.
4. `test_a_learner_with_no_group_sees_the_home` — 200, `Dashboard`.
5. `test_an_onboarded_owner_sees_the_home` — factory owner and Group: 200.
6. `test_an_admin_of_an_unfinished_group_is_not_redirected` — GET
   `share.dashboard` as admin: 200.

**Changed:** `SetupStepsTest` asserts the person's `onboarding_state` and
`onboarded_at`; `SetupTest` calls `OnboardingService`.

## Acceptance

- [x] Verify in one tab, refresh the "we sent a link" tab: setup, not the dashboard
- [x] The record of skipped and finished parts is on the User
- [x] Existing set-up Groups' owners are stamped by the migration
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

Written and started in the same session as the review that asked for it.
