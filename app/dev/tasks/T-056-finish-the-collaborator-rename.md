---
id: T-056
title: Finish the Collaborator rename in the code that reads it
stream: operations
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-056 — Finish the Collaborator rename in the code that reads it

## Why

The domain was renamed on 9 September 2026 and `WorkspaceMember` became
`Collaborator`. The model moved; the words around it did not. `User::memberships()`
returns collaborators, `User::membershipFor()` returns one, `Group::members()`
lists them, `GroupService::addMember()` and `removeMember()` create and delete
them, `CurrentGroup::membership()` holds the current one, the admin console
sends them to the browser as `members` and `memberships`, and the error for a
duplicate is `errors.group.already_a_member`.

The owner asked on 13 September 2026 why the two words coexist and what a
Collaborator is for. The second question has an answer — everyone is a `User`,
and a `Collaborator` is the row that joins one to a Group with a role — and the
first is a defect: two names for one thing, in the code a new reader meets
first.

## Decisions taken to make this specifiable

**The row is a collaborator; the user's set of them is their collaborations.**
`$user->collaborators()` would read as the people who collaborate with them,
which is wrong. `$user->collaborations()` reads as the Groups they collaborate
in, which is right. `$group->collaborators()` reads correctly from the other
side.

**Seats keep their word.** `seatsUsed()`, `seatLimit`, `team_members` in config
and `billing.limits.seats` are about a plan's allowance, not about the row, and
`T-046` recorded why they stay. Only the names that mean _the Collaborator row_
change.

**English prose in docblocks is left where "membership" is the ordinary word.**
"Reaching here means membership" is a sentence, not an identifier. The
docblocks that describe a renamed method are updated with it.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- Every method, property, parameter, payload key, lang key and test that names
  the Collaborator row as a member or membership.
- The tinker recipes and flow docs that name those methods.

**Out:**

- The `collaborators` table, the `Collaborator` model, `CollaboratorRole` and
  `Collaborator::forUserAndGroup()`, which are already right.
- Seat vocabulary, anywhere.
- `docs/project-plan.md`, which keeps the old vocabulary by declaration.

## Files

| Path                                                   | Change | Renames                                                                        |
| ------------------------------------------------------ | ------ | ------------------------------------------------------------------------------ |
| `app/Models/User.php`                                  | edit   | `memberships()` → `collaborations()`, `membershipFor()` → `collaboratorFor()`  |
| `app/Models/Group.php`                                 | edit   | `members()` → `collaborators()`                                                |
| `app/Services/GroupService.php`                        | edit   | `addMember()` → `addCollaborator()`, `removeMember()` → `removeCollaborator()` |
| `app/Support/CurrentGroup.php`                         | edit   | `membership()` → `collaborator()`, and the property/params                     |
| `app/Http/Middleware/SetCurrentGroup.php`              | edit   | Local variable                                                                 |
| `app/Listeners/CreateGroupForNewUser.php`              | edit   | Caller                                                                         |
| `app/Admin/Queries/UserDirectory.php`                  | edit   | `memberships` payload key → `collaborations`                                   |
| `app/Admin/Queries/CreatorDirectory.php`               | edit   | `members` payload key → `collaborators`                                        |
| `resources/js/pages/admin/User.vue`                    | edit   | Type and prop                                                                  |
| `resources/js/pages/admin/Creator.vue`                 | edit   | Type, prop and one label                                                       |
| `lang/en/errors.php`                                   | edit   | `group.already_a_member` → `group.already_a_collaborator`                      |
| `database/seeders/DesignReviewSeeder.php`              | edit   | One parameter name                                                             |
| `tests/Feature/Auth/SignupIntentTest.php`              | edit   | Callers                                                                        |
| `tests/Feature/Share/GroupSeatsTest.php`               | edit   | Callers                                                                        |
| `tests/Feature/Share/RegistrationCreatesGroupTest.php` | edit   | Caller                                                                         |
| `tests/Feature/Admin/ConsolePagesTest.php`             | edit   | Prop path                                                                      |
| `tests/Feature/ErrorPagesTest.php`                     | edit   | Lang key                                                                       |
| `docs/flows/groups.md`, `docs/flows/admin.md`          | edit   | Method names                                                                   |
| `docs/tinker/groups.md`, `docs/tinker/auth.md`         | edit   | Method names                                                                   |

## Database

None. The table was already named correctly.

## Code

```php
// App\Models\User
/** @return HasMany<Collaborator, $this> */
public function collaborations(): HasMany;
public function collaboratorFor(Group $group): ?Collaborator;

// App\Models\Group
/** @return HasMany<Collaborator, $this> */
public function collaborators(): HasMany;

// App\Services\GroupService
public function addCollaborator(Group $group, User $user, CollaboratorRole $role = CollaboratorRole::Admin, bool $accepted = false): Collaborator;
public function removeCollaborator(Group $group, Collaborator $collaborator): void;

// App\Support\CurrentGroup
public function set(Group $group, ?Collaborator $collaborator = null): void;
public function collaborator(): ?Collaborator;
public function runFor(Group $group, Closure $callback, ?Collaborator $collaborator = null): mixed;
```

## Copy

| Key                                   | File                 | English                                                 |
| ------------------------------------- | -------------------- | ------------------------------------------------------- |
| `errors.group.already_a_collaborator` | `lang/en/errors.php` | unchanged: `That person is already part of this group.` |

The key moves; the sentence does not. `errors.group.already_a_member` is
removed rather than aliased, so a stale caller fails a test instead of
rendering a key.

## Routes

None.

## Tests

**New:** none. A rename adds no behaviour.

**Changed:** the five test files above, mechanically. `GroupSeatsTest`'s six
cases, `SignupIntentTest`, `RegistrationCreatesGroupTest`, `ConsolePagesTest`
and `ErrorPagesTest` must all pass with only the names changed; if one needs
more than a name, the rename touched behaviour and that is a re-scope.

A grep for `memberships\(|membershipFor\(|addMember\(|removeMember\(|->members\(\)|already_a_member|->membership\(\)`
across `app/`, `tests/`, `resources/js/`, `lang/`, `database/` and `docs/`
returns nothing when this is done.

## Acceptance

- [x] The grep above returns nothing
- [x] No seat name changed
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

`Collaborator::forUserAndGroup()` was the one call site that already used the
right word, and it is the one every renamed method delegates to.
