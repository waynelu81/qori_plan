---
id: T-059
title: The sign-up choice is used once, and not stored
stream: identity
status: done
owner: claude
estimate: S
depends: none
blocks: T-060
---

# T-059 — The sign-up choice is used once, and not stored

## Why

The register form asks "What brings you here?" and the answer decides one
thing: whether a Group is made for the new account. That decision is taken
inside the registration request, by `CreateGroupForNewUser`, and never again.
Yet the answer is written to `users.signup_intent`, cast to an enum, carried on
every `User` for ever, and listed among the columns the shared user prop has to
be defended against.

The owner, 13 September 2026: "There is no need for signup_intent. It is a
runtime decision, required once, to show which onboarding flow the new user
needs to go through."

Nothing reads the column after registration. The durable fact it was standing
in for is whether the person has a Group, and `T-052` already lands a sign-in on
that. A column that is written once and read never is a column that will one
day be read by mistake — by a report, a console page, or an onboarding flow
that should have asked what the person has rather than what they once said.

## Decisions taken to make this specifiable

**The listener reads the request, not the user.** `CreateGroupForNewUser`
stays on the `Registered` event, so any future registration path still gets a
Group unless it says otherwise. It takes the current `Request` through its
constructor — ordinary container injection, not a global — and asks it for the
choice. In a console process the request is empty, the choice is absent, and
absent still means share, so seeders and commands behave exactly as before.

**The form and the validation stay.** The radio control, its field name and
`Rule::enum(SignupIntent::class)` are unchanged. What goes is the write.

**The enum stays, and stops being a model enum.** `SignupIntent` still validates
the form and names the branch the listener tests. It is no longer a column, so
it leaves `ModelEnumTest`'s column map and its reachability list. It keeps its
file, because moving it is churn that changes nothing.

**The onboarding drafts are unaffected.** `ui-onboarding.md` says a direct
registration "may retain the explicit creator/receiving choice". It does — on
the form, for the request. What `T-026` and `T-027` need afterwards is whether
a Group or a Series destination exists, and both are already durable.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The column, the cast, the fillable entry and the property.
- The listener reading the choice from the request.
- Every test and comment that names the column.

**Out:**

- The register form and its copy.
- The enum's location.
- Anything about what a new creator sees first (`T-026`).

## Files

| Path                                                                      | Change | Notes                                              |
| ------------------------------------------------------------------------- | ------ | -------------------------------------------------- |
| `database/migrations/2026_09_13_000003_drop_signup_intent_from_users.php` | new    | Drop; `down()` restores a nullable string          |
| `app/Models/User.php`                                                     | edit   | Property, fillable, cast                           |
| `app/Models/Enums/SignupIntent.php`                                       | edit   | Docblock: request-scoped, not a column             |
| `app/Actions/Fortify/CreateNewUser.php`                                   | edit   | Stop writing it; comment                           |
| `app/Listeners/CreateGroupForNewUser.php`                                 | edit   | Read the request; stale "two controllers" docblock |
| `app/Http/Middleware/HandleInertiaRequests.php`                           | edit   | One comment names the column                       |
| `tests/Feature/Auth/SignupIntentTest.php`                                 | edit   | 1 new case                                         |
| `tests/Feature/Enums/ModelEnumTest.php`                                   | edit   | Map entry, exemption, regex list                   |
| `tests/Feature/SharedUserPropTest.php`                                    | edit   | Fixture and docblock                               |
| `docs/planning/decisions.md`                                              | edit   | The decision, dated                                |

## Database

| Table   | Column          | Change  |
| ------- | --------------- | ------- |
| `users` | `signup_intent` | dropped |

Migration: `database/migrations/2026_09_13_000003_drop_signup_intent_from_users.php`

## Code

```php
// App\Listeners\CreateGroupForNewUser
public function __construct(private GroupService $groups, private Request $request) {}

// in handle(), replacing the read of $user->signup_intent:
if ($this->request->enum('signup_intent', SignupIntent::class) === SignupIntent::Learn) {
    return;
}
```

`Request::enum()` returns the case or null, and null falls through to making a
Group, which is what absent has always meant.

```php
// App\Actions\Fortify\CreateNewUser::create() — the rule stays, the write goes:
'signup_intent' => ['nullable', Rule::enum(SignupIntent::class)],
// User::create([...]) no longer has a 'signup_intent' key.
```

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/Auth/SignupIntentTest.php` — 1 case**

1. `test_the_choice_is_not_stored` — `Schema::hasColumn('users', 'signup_intent')`
   is false. **Fails today.**

**Changed:**

- `tests/Feature/Enums/ModelEnumTest.php` — `User.signup_intent` leaves the
  column map, `SignupIntent::Share` leaves the reachability exemptions, and
  `signup_intent` leaves the comparison regex. The enum is no longer a model
  enum and the test should stop treating it as one.
- `tests/Feature/SharedUserPropTest.php` — the fixture no longer sets the
  column; the docblock stops listing it.

The five existing `SignupIntentTest` cases must pass untouched. They assert
what a registration produces, which is the point: the behaviour is the same
with nothing stored.

## Acceptance

- [x] Registering with "learn" makes no Group; with "share" or nothing, one
- [x] `users` has no `signup_intent` column
- [x] The register form is unchanged
- [x] The decision is in `decisions.md`, dated, in the owner's words
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

The listener's docblock says it hangs off the event because "this codebase
carries two registration controllers, and only route ordering decides which
one runs". There is one now, Fortify's. The event is still the right hook —
for the registration path that does not exist yet — and the docblock should
say that instead.
