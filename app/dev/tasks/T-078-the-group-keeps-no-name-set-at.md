---
id: T-078
title: The Group keeps no name_set_at; a chosen name is the owner's record
stream: onboarding
status: done
owner: claude
estimate: M
depends: T-076
blocks: none
---

# T-078 — The Group keeps no `name_set_at`; a chosen name is the owner's record

## Why

The owner reviewed the Group model on 14 September 2026: "there is no need to
store `name_set_at`". It was added by `T-068` so the product could ask for a
name once and know it had been answered, and it was the only honest answer
available then. `T-076` since made the person's `onboarding_state` the record
of every part of setup — except this one, which `User::onboardingNext()`
still reads from the Group as a "fact" beside the record. It is not a fact
like a connected account is; it is the same bookkeeping, kept twice, on two
tables.

Afterwards the Group has no `name_set_at`. Whether its name has been chosen is
the owner's record, `onboarding_state.name === 'done'`, written by the one
service that renames a Group, whoever typed the name. Everything that asked
`Group::hasChosenName()` keeps asking it and gets the same answer from the
new place. A skipped name stays "not chosen", so the dashboard keeps asking.

## Decisions taken to make this specifiable

**The reading API stays on the Group.** `Group::hasChosenName()` is called by
the dashboard, the digest and the walk; they do not care where the answer
lives. It reads the owner's record. `User::onboardingNext()` drops its `NAME`
arm and treats the name like storage: answered when the record has a key.

**A rename by anyone records on the owner.** An admin can rename the Group.
The question is "has this Group's name been chosen", and the record is the
owner's, so the owner's record is what a rename writes. `GroupService::rename()`
calls `OnboardingService::complete($group->owner, $group, SetupSteps::NAME)`.
`complete()` already stamps `onboarded_at` when nothing is left to answer, so
an established owner renaming from the dashboard card changes nothing else.

**Skipped is still not chosen.** `'skipped'` keeps the generated name and the
dashboard's name card; only `'done'` satisfies `hasChosenName()`. That is the
rule `OnboardingService`'s docblock already states.

**The data step writes the record, not a timestamp.** Every Group with
`name_set_at` set gives its owner `name => done`, merged into what the record
already holds. `down()` puts the column back empty; a chosen name is not
carried back, so after a rollback the dashboard asks again. Same shape as
`T-076`'s migration.

## Preconditions

`T-076` done (it is).

## Scope

**In:**

- The migration: data step, then the column dropped.
- `Group::hasChosenName()` reading the owner; `User::onboardingNext()` with
  no `NAME` arm; `GroupService::rename()` recording on the owner.
- The factory, the seeder, and every test that sets the column.
- `docs/flows/auth.md`, `docs/tinker/groups.md`, `decisions.md`.

**Out:**

- The dashboard's name card copy ("Name your Group" after the name is chosen
  is a separate found-not-fixed from `T-075`).
- `subscription_starts_at` and `stripe_customer_id` — `T-079`.
- Any change to what the name part of setup asks or where it lands.

## Files

| Path                                                                                                                 | Change | Notes                                                                  |
| -------------------------------------------------------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------- |
| `database/migrations/2026_09_14_000002_drop_name_set_at_from_groups.php`                                             | new    | Data step to owners' records; column dropped                           |
| `app/Models/Group.php`                                                                                               | edit   | `hasChosenName()` reads the owner; property, fillable, cast removed    |
| `app/Models/User.php`                                                                                                | edit   | `onboardingNext()` loses the `NAME` arm                                |
| `app/Services/GroupService.php`                                                                                      | edit   | Constructor takes `OnboardingService`; `rename()` records on the owner |
| `database/factories/GroupFactory.php`                                                                                | edit   | Column gone; `unnamed()` makes an owner whose record skipped the name  |
| `database/seeders/DesignReviewSeeder.php`                                                                            | edit   | Three `name_set_at` lines removed; owners' records already say it      |
| `docs/flows/auth.md`, `docs/tinker/groups.md`, `docs/planning/decisions.md`                                          | edit   | The record is the whole answer                                         |
| `tests/Feature/Share/GroupRenameTest.php`                                                                            | edit   | Owner's record instead of the column; 2 new cases                      |
| `tests/Feature/Share/SetupStepsTest.php`                                                                             | edit   | Assert the record, not the column                                      |
| `tests/Feature/ShareDigestTest.php`                                                                                  | edit   | `unnamedGroup()` through the factory state                             |
| `tests/Feature/Series/SeriesIdentityTest.php`, `ShareLinkTest.php`, `tests/Feature/Share/VocabularySettingsTest.php` | edit   | Drop the `name_set_at => now()` lines; the factory owner is named      |

## Database

| Table    | Column        | Type    | Null | Default | Index / constraint |
| -------- | ------------- | ------- | ---- | ------- | ------------------ |
| `groups` | `name_set_at` | dropped |      |         |                    |

Migration: `database/migrations/2026_09_14_000002_drop_name_set_at_from_groups.php`

```php
public function up(): void
{
    // Every named Group tells its owner's record so, merged into whatever the
    // record already holds. Postgres-only, like the project.
    DB::statement(<<<'SQL'
        UPDATE users
        SET onboarding_state = onboarding_state || '{"name": "done"}'::jsonb
        FROM groups
        WHERE groups.owner_user_id = users.id AND groups.name_set_at IS NOT NULL
    SQL);

    Schema::table('groups', fn (Blueprint $table) => $table->dropColumn('name_set_at'));
}

public function down(): void
{
    // Shape only. A chosen name is read from the owner's record and is not
    // carried back, so after a rollback the dashboard asks again.
    Schema::table('groups', fn (Blueprint $table) => $table->timestamp('name_set_at')->nullable()->after('name'));
}
```

## Code

```php
// App\Models\Group
/** Whether anybody has chosen this Group's name: the owner's record says done. */
public function hasChosenName(): bool
{
    /** @var array<string, string> $state */
    $state = $this->owner?->onboarding_state ?? [];

    return ($state[SetupSteps::NAME] ?? null) === 'done';
}
```

```php
// App\Models\User::onboardingNext() — the loop body
$done = $part === SetupSteps::PAYMENTS && filled($group->connect_account_id);

if (! $done && ! isset($state[$part])) {
    return $part;
}
```

```php
// App\Services\GroupService
public function __construct(private OnboardingService $onboarding) {}

public function rename(Group $group, string $name): Group
{
    $group->forceFill(['name' => trim($name)])->save();

    // Recorded on the owner whoever typed it: the Group's name is now chosen.
    $owner = $group->owner;

    if ($owner instanceof User) {
        $this->onboarding->complete($owner, $group, SetupSteps::NAME);
    }

    return $group;
}
```

`GroupFactory::definition()` loses `name_set_at`; a factory User already
records `name => done`, so a factory Group is named. `unnamed()` becomes:

```php
public function unnamed(): static
{
    return $this->state(fn (array $attributes) => [
        'owner_user_id' => User::factory()->state([
            'onboarding_state' => ['name' => 'skipped', 'payments' => 'skipped', 'storage' => 'skipped'],
        ]),
    ]);
}
```

A test that already passes its own `owner_user_id` and wants the Group
unnamed sets that owner's record instead (`User::factory()->notOnboarded()`
for a fresh owner; the skipped state above for an established one).

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/Share/GroupRenameTest.php` — 2 new cases**

1. `test_renaming_records_the_name_as_chosen_on_the_owner` — owner PATCHes a
   name: `owner->fresh()->onboarding_state['name'] === 'done'` and
   `hasChosenName()` true.
2. `test_an_admin_rename_records_on_the_owner_not_the_admin` — an admin
   PATCHes: the owner's record says done, the admin's is unchanged.

**Changed:**

- `tests/Feature/Share/GroupRenameTest.php` — the fixture sets the owner's
  record rather than `name_set_at => null`; the existing `hasChosenName()`
  assertions stand.
- `tests/Feature/Share/SetupStepsTest.php` — line 60 asserts the owner's
  record says done; line 72's null-column assertion goes.
- `tests/Feature/ShareDigestTest.php` — `group()` drops the column;
  `unnamedGroup()` is `Group::factory()->unnamed()`.
- `tests/Feature/Series/SeriesIdentityTest.php`, `ShareLinkTest.php`,
  `tests/Feature/Share/VocabularySettingsTest.php` — the `name_set_at => now()`
  lines go; nothing else.
- `tests/Feature/Share/OnboardingHomeTest.php`, `SetupTest.php`,
  `DesignReviewFixtureTest.php` — expected to pass unchanged; if one does not,
  the record and the fact disagree somewhere — stop and re-scope.

## Acceptance

- [x] `groups` has no `name_set_at`; the dev database's owner record says `name => done` after `php artisan migrate`
- [x] `hasChosenName()` is true after any rename and false for a skipped name
- [x] A fresh owner is still asked for the name first; an owner who skipped it is not sent back to setup by the home route
- [x] The dashboard name card and the digest's name prompt behave as before
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**Changed during execution**, and judged against the stop condition rather
than around it: two files the table did not name, and three test cases. The
redirect out of part one (`GroupController`) asked the request's copy of the
person, which had not seen the rename's write on `$group->owner`; it asks the
owner instance now. `OnboardingService::record()` merges into the stored
record so a stale copy cannot clobber it. Three tests held an owner a
service-level rename had written past, or asserted the old fact-over-record
rule for the name — see the report.

`hasChosenName()` loads the owner. The dashboard and the digest already hold
the Group and nothing else reads it in a loop, so this is one query, not N.
If a list of Groups ever asks it, eager-load `owner` there.
