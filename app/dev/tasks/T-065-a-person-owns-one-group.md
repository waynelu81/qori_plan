---
id: T-065
title: A person owns one Group, and the service refuses a second
stream: identity
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-065 — A person owns one Group, and the service refuses a second

## Why

The rule is recorded in `decisions.md` (2026-09-13): a person owns one Group,
created at registration or the first time a learner chooses to share, and the
switcher exists only because a person may be an admin in Groups other people
own. The code already behaves that way by accident — registration creates one,
`HomeController::startSharing()` creates one only when the person can reach
none, and no page, button or route creates a second — but nothing says so. A
"new Group" door could be added tomorrow without meeting the decision.

Afterwards: `GroupService::createFor()` refuses to create a Group for a person
who already owns one, and three tests pin the rule from the three directions
it can be approached.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The guard in `createFor()`.
- Three tests.

**Out:**

- The switcher, `last_group_id`, `SignInLanding` and `accessibleGroups()`.
  They serve admins of other people's Groups and stay.
- The design-review fixture, which writes `Group` rows directly and gives Rita
  five. That is `T-066`.
- Any change to how a collaborator is invited.

## Files

| Path                                            | Change | Notes     |
| ----------------------------------------------- | ------ | --------- |
| `app/Services/GroupService.php`                 | edit   | The guard |
| `tests/Feature/Share/OneGroupPerPersonTest.php` | new    | 3 cases   |

## Database

None.

## Code

```php
// App\Services\GroupService::createFor(), first thing:
if (Group::query()->where('owner_user_id', $owner->getKey())->exists()) {
    throw new LogicException(
        "User {$owner->getKey()} already owns a Group; a person owns one (decisions.md, 2026-09-13)."
    );
}
```

`LogicException`, not `AppException`: no user can reach this — every caller
checks first or runs once per registration — so a hit is a programmer error
and should read as one.

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/Share/OneGroupPerPersonTest.php` — 3 cases**

1. `test_a_second_group_for_the_same_owner_is_refused` — `createFor()` twice
   for one user throws `LogicException`; one Group exists afterwards.
2. `test_a_learner_who_starts_sharing_gets_one_group_and_keeps_it` — a user
   with no Group hits the route behind `HomeController::startSharing()` twice;
   one Group exists and both responses land on its dashboard.
3. `test_an_admin_who_starts_sharing_lands_on_the_group_they_help_run` — a
   user who is an admin on somebody else's Group and owns none hits the same
   route: redirected to that Group's dashboard, and no Group is created.

**Changed:** none. `GroupSeatsTest` creates one Group per fresh user.

## Acceptance

- [x] `createFor()` refuses a second owned Group
- [x] Starting to share never creates a Group for somebody who can already
      reach one
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

None.
