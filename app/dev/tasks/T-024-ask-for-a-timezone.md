---
id: T-024
title: Ask for a timezone, and store it
stream: onboarding
status: done
owner: claude
estimate: M
depends: none
blocks: T-025, T-026, T-027, T-029
---

# T-024 — Ask for a timezone, and store it

## Why

**No table in Qori has a timezone column.** `config('app.timezone')` is `'UTC'`,
so anything Qori renders server-side — an email, a certificate, a PDF — states a
time in UTC without saying so. Anything rendered in the browser uses
`toLocaleDateString()` and is therefore in the viewer's zone by accident rather
than by choice, which is right today and stops being right the moment the same
date has to appear in both places and agree.

**The concrete thing it breaks is a live session.** `episodes.starts_at` is
validated with `['nullable', 'date']`, so a naive `2026-10-01T09:00` from a
form is parsed as UTC. A creator in Melbourne scheduling 9am would be
scheduling their Peers' 7pm, and everyone would be told the wrong hour with
complete confidence. `T-029` is that task and this is its prerequisite: a
timezone is **mandatory for a Series with a live Episode** and optional
otherwise.

It also blocks scheduling generally. `communications-policy.md` settled on
2026-09-06 that a reminder set for 9am sends at 9am **in the Group's zone**,
because the person choosing the time is the creator and it should mean what
they meant. That decision has had nowhere to live for three months.

## Decisions taken to make this specifiable

**Two timezones, because there are two questions.** The person's answers "what
should this date say to me"; the Group's answers "what does 9am mean". They will
usually be identical and they are not the same fact — a creator who moves
countries wants their interface to follow and their scheduled sends not to.

**Ask once, at first run, with the browser's guess pre-filled.**
`Intl.DateTimeFormat().resolvedOptions().timeZone` is right almost always, so
the question is a confirmation rather than a search. It is a _question_, not a
silent capture: a value nobody was shown is a value nobody can correct, and this
one decides when their Peers get emailed.

**Nullable, and never guessed on the server.** A user who has not answered has
`null`, and every consumer falls back to `config('app.timezone')` explicitly.
Storing a server-inferred guess would make "we asked" and "we assumed"
indistinguishable, which is the thing `groups.name_set_at` already exists to
avoid.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- `users.timezone` and `groups.timezone`.
- A first-run prompt with the browser's zone pre-filled.
- Changing it later, in user settings and in Group settings.
- Validation against the real tz database.

**Out:**

- Using it. Every consumer is `T-025` — this task stores a value and changes
  nothing about how a date is displayed, deliberately, so the two are reviewable
  apart.
- Per-Peer timezones. `communications-policy.md` says the schema does not
  preclude one later; it is not wanted now.
- A timezone on `Peer`. Same reason.

## Files

| Path                                                                         | Change | Notes                                  |
| ---------------------------------------------------------------------------- | ------ | -------------------------------------- |
| `database/migrations/2026_09_10_000000_add_timezone_to_users_and_groups.php` | new    | Two nullable columns                   |
| `app/Models/User.php`                                                        | edit   | `$fillable`, `@property`, `timezone()` |
| `app/Models/Group.php`                                                       | edit   | Same                                   |
| `app/Support/Timezones.php`                                                  | new    | The valid list, and the fallback       |
| `app/Http/Controllers/Settings/TimezoneController.php`                       | new    | `update`                               |
| `app/Http/Requests/Settings/UpdateTimezoneRequest.php`                       | new    | One field                              |
| `app/Http/Controllers/Share/GroupController.php`                             | edit   | Group timezone alongside the rename    |
| `app/Http/Requests/Share/UpdateGroupRequest.php`                             | edit   | Optional `timezone`                    |
| `app/Http/Middleware/HandleInertiaRequests.php`                              | edit   | Share the resolved zone                |
| `routes/settings.php`                                                        | edit   | One route                              |
| `lang/en/profile.php`                                                        | edit   | 2 keys                                 |
| `lang/en/groups.php`                                                         | edit   | 1 key                                  |
| `resources/js/pages/settings/Profile.vue`                                    | edit   | The field                              |
| `resources/js/components/share/GroupNameForm.vue`                            | edit   | Group zone beside the name             |
| `resources/js/components/TimezoneField.vue`                                  | new    | Select + browser guess                 |
| `tests/Feature/Settings/TimezoneTest.php`                                    | new    | 9 cases                                |

**Added during execution**, because the table above could not be built without
them. None of them changes what gets built — see the report:

| Path                                                  | Change | Why it was missing                                 |
| ----------------------------------------------------- | ------ | -------------------------------------------------- |
| `app/Services/GroupService.php`                       | edit   | `setTimezone()`; every other Group write is here   |
| `app/Http/Controllers/Settings/ProfileController.php` | edit   | Sends the zone list, the chosen flag and the label |
| `app/Http/Controllers/Share/DashboardController.php`  | edit   | Sends the zone list to the first-run card          |
| `resources/js/pages/share/Dashboard.vue`              | edit   | Passes the list through to `GroupNameForm`         |
| `resources/js/types/auth.ts`                          | edit   | `timezone` on the `User` type                      |
| `resources/js/composables/useShareContext.ts`         | edit   | `timezone` and `timezoneChosen` on `GroupRef`      |
| `tests/Feature/SharedUserPropTest.php`                | edit   | Already named under **Tests**, not under **Files** |

## Database

| Table    | Column     | Type         | Null | Default | Index / constraint |
| -------- | ---------- | ------------ | ---- | ------- | ------------------ |
| `users`  | `timezone` | `string(64)` | yes  | null    | —                  |
| `groups` | `timezone` | `string(64)` | yes  | null    | —                  |

`string`, not an enum or a foreign key: the tz database changes when
governments change their minds, and a value Qori validated in 2026 must still
load in 2031 even if the zone has since been renamed.

64 characters covers the longest current identifier
(`America/Argentina/ComodRivadavia`, 32) with room for whatever comes next.

Migration: `database/migrations/2026_09_XX_000000_add_timezone_to_users_and_groups.php`

## Code

```php
namespace App\Support;

class Timezones
{
    /** Every identifier PHP will accept, for the select and the validator. */
    public static function all(): array;          // list<string>

    /** Grouped by region, because a flat list of 400 is not a control. */
    public static function grouped(): array;      // array<string, list<string>>

    public static function isValid(string $timezone): bool;
}
```

Built from `DateTimeZone::listIdentifiers()` rather than a hand-kept array, so
the list cannot go stale. Cache it for the request; do not cache it across
requests, because it is cheap and a stale cache here is a validation failure
nobody can reproduce.

```php
// App\Models\User and App\Models\Group
/**
 * The zone this record's times mean, or the application default.
 *
 * Never a guess: null means nobody has said, and the caller gets UTC and
 * knows it. Inferring one server-side would make "asked" and "assumed"
 * indistinguishable.
 */
public function timezone(): string;   // $this->timezone ?? config('app.timezone')
```

Both models get the same method name and the same fallback. `Group::timezone()`
falls back to its **owner's** zone before the application default — a Group
created by somebody in Melbourne should not schedule in UTC because nobody
opened Group settings.

Share the user's resolved zone on the Inertia `auth.user` payload. That payload
is an allow-list with a test asserting its exact key set (`SharedUserPropTest`),
so **that test will fail until it is updated** — expected, and the point of it.

## Copy

| Key                      | File                  | English                                   |
| ------------------------ | --------------------- | ----------------------------------------- |
| `profile.timezone.saved` | `lang/en/profile.php` | `Times will show in :timezone.`           |
| `profile.timezone.label` | `lang/en/profile.php` | `Your timezone`                           |
| `groups.timezone.saved`  | `lang/en/groups.php`  | `Your :group schedules in :timezone now.` |

The field's help text has to say what it is _for_, because "timezone" alone
reads as a preference and this one decides when other people get emailed.

## Routes

| Verb  | Path          | Name                      | Action                      |
| ----- | ------------- | ------------------------- | --------------------------- |
| PATCH | `/u/timezone` | `profile.timezone.update` | `TimezoneController@update` |

The Group's zone rides on the existing `share.group.update`, because it belongs
with the name — both are "what this Group is", and a second route for one field
is a second route to remember.

## Tests

**New: `tests/Feature/Settings/TimezoneTest.php` — 9 cases**

1. `test_a_user_can_set_their_timezone`
2. `test_an_unknown_timezone_is_rejected` — `Mars/Olympus_Mons`
3. `test_an_empty_timezone_is_rejected`
4. `test_a_user_without_one_falls_back_to_the_application_default` — and the
   fallback is UTC, asserted, so a change to `config/app.php` is visible here
5. `test_a_group_can_set_its_own_timezone`
6. `test_a_group_without_one_falls_back_to_its_owners` — the case that stops a
   Melbourne creator scheduling in UTC by omission
7. `test_a_group_whose_owner_has_none_falls_back_to_the_application_default`
8. `test_the_users_timezone_reaches_the_shared_inertia_prop`
9. `test_setting_a_timezone_does_not_change_any_displayed_date` — this task
   stores and does not consume; `T-025` is what makes dates move

**Changed:** `tests/Feature/SharedUserPropTest.php` — the exact-key-set
assertion gains `timezone`. That test is designed to fail on a new field; note
in the report that it did.

## Acceptance

- [x] A person and a Group can each hold a timezone, and neither is guessed
- [x] The first-run prompt pre-fills the browser's zone and asks rather than
      assumes
- [x] An invalid identifier is refused
- [x] A Group with none falls back to its owner's, then to the app default
- [x] Nothing displayed changes yet
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**`timezone()` and `timezone` collide, and it is a 500 rather than a wrong
answer.** The spec names the method `timezone()` and the column `timezone`.
When the attribute is not in `$attributes` — a model constructed in memory and
never hydrated, which is every `User::create()` before it is re-read — Eloquent
falls through to relation resolution, finds the method, and throws
`App\Models\User::timezone must return a relationship instance`. It surfaced
on `SharedUserPropTest` as a 500 naming neither the column nor the page.

Kept the name, because changing it is a change to what is built. Guarded
twice instead: `protected $attributes = ['timezone' => null]` on both models so
the key always exists, and `getAttributeValue()` rather than `$this->timezone`
inside the methods, so the accessor cannot resolve to the method again on a
partially selected row. Every caller outside the models reads
`getAttributeValue('timezone')` for the same reason.

**The "filled in from your device" note has to be a computed, not a constant.**
Read once at setup it survived the save — Inertia swaps the props and Vue
reuses the instance — so the field went on claiming the value came from the
device after the creator had saved it themselves. Caught in a browser, not by a
test; there is no JavaScript test runner in this project.

`Peer` deliberately has no timezone. `communications-policy.md` allows one
later with a fallback to the Group's; adding it now would be a column with no
consumer and a question nobody asked.
