---
id: T-052
title: Signing in lands on the side you last used
stream: identity
status: done
owner: claude
estimate: M
depends: none
blocks: none
---

# T-052 — Signing in lands on the side you last used

## Why

Every way of signing in ends on `/dashboard`, which is the **receiving** home:
Fortify's `LoginResponse` and `TwoFactorLoginResponse` fall through to
`fortify.home`, `MagicLinkLoginController::login()` names `route('dashboard')`
outright, and `laravel/passkeys` reads `config('passkeys.redirect', '/')` with
no config file published, so a passkey sign-in with nothing intended lands on
the **marketing page**. A creator who runs a Group arrives on "Shared with me",
reads "Nothing on the go", and scrolls to **You also share → Open** every time.

The owner, testing on 13 September 2026: "Right after login it is redirected to
the learner portal. It needs either an easy switchboard as starting page or to
detect what my last was. I am fully expecting to go to the creator page."

`R-003` F-2 recorded the first-run version of this and gave it to `T-026`,
whose disposition was "intent-appropriate initial landing, without turning
every dashboard visit into a redirect". This task is the returning-user
version, which is small and does not wait on an onboarding rebuild.

## Decisions taken to make this specifiable

**Remember, rather than guess.** The Group somebody last opened is written to
`users.last_group_id` at the moment Group context is established, and read back
at the next sign-in. It is on the user row rather than in the session because
the whole point is surviving a sign-out. It is written only when it changes, so
a page load inside a Group costs no write.

**Three fallbacks, in order.** The last Group, if they are still a member of it.
Otherwise the only Group, if they have exactly one. Otherwise `/dashboard`, the
receiving home, which already lists every Group under **You also share** and
offers **Start sharing** — so it is the switchboard for anyone with nothing to
remember. Nobody with no Group is redirected anywhere new.

**`intended()` stays on top on every path.** A guest sent to sign in from a
protected page still returns to that page; this only decides where somebody
lands when nothing was intended. Path B of `T-008` depends on this and must
keep working.

**`/dashboard` itself never redirects.** It stays a page a creator can visit to
see what they are receiving, exactly as R-003 asked.

**Registration is not touched.** `RegisterResponse` still lands on the
receiving home after signup; where a brand-new creator goes first is `T-026`'s
first-run frame, and a new account has no last Group anyway.

## Preconditions

None beyond a clean checkout. `laravel/passkeys` binds its login response
through a contract (`Laravel\Passkeys\Contracts\PasskeyLoginResponse`) in its
own provider's `register()`, so an application binding in `register()` replaces
it the same way `T-008` replaced Fortify's.

## Scope

**In:**

- Where password, two-factor, email-link and passkey sign-ins land when nothing
  was intended.
- Remembering the Group somebody last opened.

**Out:**

- Where registration lands (`T-026`).
- A switchboard page of its own. The receiving home already is one.
- The sidebar, the Group switcher, or anything about how hats are shown.
- Staff sign-in, which has its own guard and its own console.

## Files

| Path                                                                   | Change | Notes                                        |
| ---------------------------------------------------------------------- | ------ | -------------------------------------------- |
| `database/migrations/2026_09_13_000001_add_last_group_id_to_users.php` | new    | One nullable column, one foreign key         |
| `app/Models/User.php`                                                  | edit   | Property, `lastGroup()`                      |
| `app/Support/SignInLanding.php`                                        | new    | The three fallbacks, in one place            |
| `app/Http/Middleware/SetCurrentGroup.php`                              | edit   | Record the Group after context is set        |
| `app/Http/Responses/LoginResponse.php`                                 | new    | Replaces Fortify's                           |
| `app/Http/Responses/TwoFactorLoginResponse.php`                        | new    | Replaces Fortify's                           |
| `app/Http/Responses/PasskeyLoginResponse.php`                          | new    | Replaces the package's, JSON branch included |
| `app/Providers/FortifyServiceProvider.php`                             | edit   | Three bindings beside the existing one       |
| `app/Http/Controllers/Auth/MagicLinkLoginController.php`               | edit   | One line                                     |
| `tests/Feature/Auth/SignInLandingTest.php`                             | new    | 9 cases                                      |

`app/Providers/FortifyServiceProvider.php` is also claimed by `T-053`. Neither
may be `doing` while the other is; they add adjacent lines and run cleanly in
sequence.

## Database

| Table   | Column          | Type       | Null | Default | Index / constraint                                         |
| ------- | --------------- | ---------- | ---- | ------- | ---------------------------------------------------------- |
| `users` | `last_group_id` | `char(26)` | yes  | null    | foreign key → `groups.id`, **on delete set null**; indexed |

Migration: `database/migrations/2026_09_13_000001_add_last_group_id_to_users.php`

Set null on delete, not cascade: losing a Group must not lose the person.

## Code

```php
// App\Support\SignInLanding
/**
 * Where a signed-in person goes when nothing was intended: the Group they last
 * opened, else their only Group, else the receiving home. Absolute URL.
 */
public static function for(User $user): string;
```

`for()` checks membership with `$user->belongsToGroup()` before trusting
`last_group_id`, because a person removed from a Group keeps the column until
the Group is deleted, and must not be sent to a page that answers 404.

```php
// App\Models\User
/** @property ?string $last_group_id */
/** @return BelongsTo<Group, $this> */
public function lastGroup(): BelongsTo;
```

```php
// App\Http\Middleware\SetCurrentGroup::handle(), after app(CurrentGroup::class)->set():
if ($user->last_group_id !== $group->getKey()) {
    $user->forceFill(['last_group_id' => $group->getKey()])->saveQuietly();
}
```

`saveQuietly()`, because this is bookkeeping and no observer should fire for it.

```php
// App\Http\Responses\LoginResponse and TwoFactorLoginResponse
return $request->wantsJson()
    ? new JsonResponse('', 204)
    : redirect()->intended(SignInLanding::for(CurrentUser::orFail($request)));
```

```php
// App\Http\Responses\PasskeyLoginResponse — mirror the package's own shape,
// which answers JSON with the target URL so the browser-side ceremony can follow it:
$target = redirect()->intended(SignInLanding::for(CurrentUser::orFail($request)));

return $request->wantsJson()
    ? new JsonResponse(['redirect' => $target->getTargetUrl()])
    : $target;
```

```php
// App\Http\Controllers\Auth\MagicLinkLoginController::login(), last line
return redirect()->intended(SignInLanding::for($user));
```

Bindings go in `FortifyServiceProvider::register()` beside the
`VerifyEmailResponse` one: `LoginResponseContract`, `TwoFactorLoginResponseContract`
from `Laravel\Fortify\Contracts`, and `PasskeyLoginResponseContract` from
`Laravel\Passkeys\Contracts`.

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/Auth/SignInLandingTest.php` — 9 cases**

1. `test_a_creator_lands_on_the_group_they_last_used` — two Groups, the
   second recorded as last, password sign-in redirects to its dashboard.
   **Fails today**, landing on `/dashboard`.
2. `test_a_creator_with_one_group_lands_there_without_a_history` — no
   `last_group_id`, one membership.
3. `test_someone_with_no_group_lands_on_the_receiving_home` — the existing
   behaviour, kept on purpose.
4. `test_a_group_they_were_removed_from_is_not_used` — `last_group_id` names a
   Group with no membership row; falls through rather than 404.
5. `test_a_protected_page_they_were_sent_from_still_wins` — visit a Group page
   as a guest, sign in, land on that page and not on the remembered one.
6. `test_the_last_group_is_recorded_when_they_open_one` — open a Group's
   dashboard, read the column.
7. `test_an_email_link_sign_in_lands_the_same_way` — through
   `MagicLinkLoginController::urlFor()`.
8. `test_a_two_factor_sign_in_lands_the_same_way` — the response class called
   directly with an acting user, because the challenge ceremony is already
   covered by `TwoFactorChallengeTest`.
9. `test_a_passkey_sign_in_no_longer_lands_on_the_marketing_page` — the
   response class called directly, both branches: the JSON body's `redirect`
   and the redirect itself.

**Changed:** none expected. `AuthenticationTest` and `MagicLinkRoutesTest`
assert a `/dashboard` landing for factory users, who have no Group, which case
3 keeps true. If one of them changes, its fixture has gained a Group.

## Acceptance

- [x] A creator signing in by password, two-factor, email link or passkey lands
      on the Group they last opened
- [x] With no history and one Group, they land on it
- [x] With no Group, they land on the receiving home, as today
- [x] A passkey sign-in never lands on the marketing page
- [x] Being sent to sign in from a protected page still returns there
- [x] `/dashboard` is still a page, never a redirect
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

`config/passkeys.php` is not published. Publishing it to set `redirect` would
give one static URL for everyone, which is the problem this task exists to
fix; the response binding is the right lever and the config stays unpublished.

The landing rule is recorded in `decisions.md`, dated 13 September 2026.
