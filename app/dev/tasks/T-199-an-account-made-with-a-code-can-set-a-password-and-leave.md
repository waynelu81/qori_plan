---
id: T-199
title: An account made with a code can set a password and leave
stream: identity
status: doing
owner: claude
estimate: M
depends: none
blocks: none
---

# T-199 — An account made with a code can set a password and leave

## Why

The Series page's code step makes a Peer's account with `Str::password(32)`,
a password nobody knows (`app/Http/Controllers/SeriesAccessController.php:77`,
`T-073`), and `docs/flows/auth.md` says choosing one later is the security
page's job. That page sits behind `RequirePassword`
(`routes/settings.php:86-90`), setting a password asks for the current one
(`PasswordUpdateRequest.php:21`), and so does deleting the account
(`ProfileDeleteRequest.php:21`). Two-factor and passkeys are managed behind
the same confirmation (`config/fortify.php`, `confirmPassword`). A Peer who
came in by code can do none of it except by finding "Forgot password" first,
which nothing on those pages points to — and which fails outright for an
address stored with capitals (`T-198`). Found while specifying `T-027`,
23 September 2026, from a read of the code; not walked in a browser.

Afterwards a person with no password of their own proves who they are with a
code emailed to their address, and can then set a password, manage two-factor
and passkeys, and delete their account.

## Decisions taken to make this specifiable

Brought to ready on 27 September 2026, from the code.

**`users.password_set_at`, a nullable timestamp, says whether the person chose
a password.** Not a `password` column that may be null: Fortify's login, the
`current_password` rule and every `Hash::check` read a string there, and a
null would still say nothing about the accounts that already hold a random
one. `CreateNewUser` (registration), `ResetUserPassword` (a reset) and
`SecurityController::update()` set it. `User::hasChosenPassword()` reads it.

**Every existing account starts with it empty.** Nothing tells the two kinds
apart after the fact: the code step and registration both leave a hash, and
owning a Group is not the answer either — registering to learn makes none
(`CreateGroupForNewUser`) and a Peer's Start sharing makes one
(`HomeController::startSharing()`). So an existing account that does know
its password is treated as one that may not, until it sets a password again:
its confirm step offers the emailed code beside the password field it has
today, and its password form asks for no current password. The accounts made
before release are few and the owner's; every new one is marked from its first
password. The user factory marks its accounts, whose password is known, and
gains a `withoutPassword()` state for the code step's kind.

**An emailed code confirms who a person is, in place of a password, for anyone
who has not chosen one.** The confirm step (`auth/confirm-password`) keeps its
password field and its passkey and adds "Email me a code". The code is
`LoginCodeService`'s — the Series page's six digits, lifetime and attempts,
sent in the plain "Your Qori code is" email — and a right one marks the session
confirmed exactly as the password does, `$request->session()->passwordConfirmed()`.
So the security page, two-factor and passkeys, all behind that step, open with
nothing else changed. The code routes answer 404 to a person who has chosen a
password: the option is not theirs, and they have the faster path.

**Setting a first password asks for no current password, and needs a
confirmation still in date.** The security page is only reached through the
confirm step, so for a person with no password the form drops "Current
password" and reads as choosing one; `PasswordUpdateRequest` excludes
`current_password` for them and refuses the change if the session's
confirmation is older than `auth.password_timeout`, since the `PUT` route
itself is not behind `RequirePassword`.

**Deleting the account takes the emailed code in place of the password.** The
Profile page is not behind the confirm step, so the delete dialog carries the
code itself, as it carries the password today: for a person with no password
it replaces the password field with "Email me a code" and a code field, and
`ProfileDeleteRequest` checks the code through `LoginCodeService::verify()`
instead of `current_password`, with the Series page's two refusals,
`errors.access.code_wrong` and `code_spent`.

**Two-factor and passkeys are offered as they are today, once the session is
confirmed.** A passkey signs a person in on its own, with no password, which is
exactly what someone without one wants; two-factor as Fortify builds it
seconds a password sign-in, and turning it on without a password changes
nothing until one is set. Whether a magic link or a code should ask for the
second factor is its own question and not this one.

**The words for leaving are release checklist** (`D-043`). The place is built
here, with plain lines for what each control does; what deleting means for a
purchase or a certificate is the policy's to say.

## Preconditions

None.

**Data this task verifies against:** a clean database, and on the dev server a
fresh account made by the Series page's code step.

**Equipment:** a mailbox that shows the code: a private Mailpit for the walk,
or `Notification::fake()` in tests.

## Scope

**In:**

- `users.password_set_at`, set by registration, a reset and a change.
- The confirm step's emailed code, for a person with no chosen password.
- The security page's password form, and the delete dialog, for that person.

**Out:**

- The address's case: `T-198`.
- Whether a magic link or a code sign-in asks for a second factor.
- The policy words for deleting an account (release checklist).

## Files

| Path                                                                     | Change | Notes                                                        |
| ------------------------------------------------------------------------ | ------ | ------------------------------------------------------------ |
| `database/migrations/2026_09_28_000100_add_password_set_at_to_users.php` | new    | the column, empty for every existing row                     |
| `app/Models/User.php`                                                    | edit   | cast, `hasChosenPassword()`                                  |
| `database/factories/UserFactory.php`                                     | edit   | set by default; `withoutPassword()`                          |
| `app/Actions/Fortify/CreateNewUser.php`                                  | edit   | sets it                                                      |
| `app/Actions/Fortify/ResetUserPassword.php`                              | edit   | sets it                                                      |
| `app/Http/Controllers/Settings/SecurityController.php`                   | edit   | sets it on update; `hasPassword` and copy on the page        |
| `app/Http/Controllers/Auth/ConfirmByCodeController.php`                  | new    | `begin()`, `finalise()`                                      |
| `app/Http/Requests/Auth/ConfirmByCodeRequest.php`                        | new    | the code                                                     |
| `app/Http/Requests/Settings/PasswordUpdateRequest.php`                   | edit   | no current password, a confirmation in date                  |
| `app/Http/Requests/Settings/ProfileDeleteRequest.php`                    | edit   | the code in place of the password                            |
| `app/Http/Controllers/Settings/ProfileController.php`                    | edit   | `hasPassword` and copy for the dialog                        |
| `app/Providers/FortifyServiceProvider.php`                               | edit   | the confirm view's props                                     |
| `routes/magic-link.php`                                                  | edit   | the two code routes, beside the other `/auth` additions      |
| `resources/js/pages/auth/ConfirmPassword.vue`                            | edit   | "Email me a code"                                            |
| `resources/js/pages/settings/Security.vue`                               | edit   | the form without a current password                          |
| `resources/js/components/DeleteUser.vue`                                 | edit   | the code in place of the password                            |
| `lang/en/auth.php`                                                       | edit   | `confirm_code.*`                                             |
| `lang/en/profile.php`                                                    | edit   | `first_password.*`, `delete_code.*`                          |
| `tests/Feature/Settings/AccountWithoutPasswordTest.php`                  | new    | 12 cases                                                     |
| `docs/flows/auth.md`                                                     | edit   | the confirm step's code, and what a code-made account can do |

## Database

| Table   | Column            | Type      | Null | Default | Index / constraint |
| ------- | ----------------- | --------- | ---- | ------- | ------------------ |
| `users` | `password_set_at` | timestamp | yes  | null    | none               |

Migration: `database/migrations/2026_09_28_000100_add_password_set_at_to_users.php`

## Code

```php
// App\Models\User
public function hasChosenPassword(): bool; // password_set_at !== null

// App\Http\Controllers\Auth\ConfirmByCodeController
public function begin(Request $request, LoginCodeService $codes): RedirectResponse;          // sends; 404 when a password was chosen
public function finalise(ConfirmByCodeRequest $request, LoginCodeService $codes): RedirectResponse; // verifies; passwordConfirmed(); redirect()->intended(route('security.edit'))
```

## Copy

| Key                            | File          | English                                                             |
| ------------------------------ | ------------- | ------------------------------------------------------------------- |
| `auth.confirm_code.offer`      | `auth.php`    | No password yet? We'll email a code to :email instead.              |
| `auth.confirm_code.send`       | `auth.php`    | Email me a code                                                     |
| `auth.confirm_code.sent`       | `auth.php`    | We emailed a code to :email.                                        |
| `auth.confirm_code.label`      | `auth.php`    | Code                                                                |
| `auth.confirm_code.submit`     | `auth.php`    | Confirm with the code                                               |
| `profile.first_password.title` | `profile.php` | Choose a password                                                   |
| `profile.first_password.body`  | `profile.php` | You signed in with a code. A password lets you sign in without one. |
| `profile.delete_code.body`     | `profile.php` | We'll email a code to :email to check it's you.                     |
| `profile.delete_code.label`    | `profile.php` | Code                                                                |

Refusals reuse `errors.access.code_wrong` and `errors.access.code_spent`.

## Routes

| Verb | Path                                  | Name                             | Action                             |
| ---- | ------------------------------------- | -------------------------------- | ---------------------------------- |
| POST | `auth/confirm-password/code/begin`    | `password.confirm.code.begin`    | `ConfirmByCodeController@begin`    |
| POST | `auth/confirm-password/code/finalise` | `password.confirm.code.finalise` | `ConfirmByCodeController@finalise` |

Both behind `auth`; `begin` on `throttle:magic-link`, `finalise` on
`throttle:6,1`, as the Series page's code routes are.

## Tests

**New: `tests/Feature/Settings/AccountWithoutPasswordTest.php` — 12 cases**

1. `test_registering_records_a_chosen_password`.
2. `test_the_code_step_makes_an_account_with_none` — through the Series page.
3. `test_a_reset_records_it`.
4. `test_the_confirm_step_offers_the_code_only_without_a_chosen_password`.
5. `test_the_right_code_confirms_and_opens_the_security_page`.
6. `test_a_wrong_code_confirms_nothing`.
7. `test_the_code_routes_are_not_for_a_person_with_a_password` — 404.
8. `test_a_first_password_needs_no_current_one` — and is recorded.
9. `test_a_first_password_waits_for_a_confirmation_in_date`.
10. `test_a_password_change_still_needs_the_current_one`.
11. `test_deleting_without_a_password_takes_the_emailed_code`.
12. `test_a_wrong_code_deletes_nothing`.

**Changed:** none expected — the factory marks its accounts, so every existing
test's user still has a password it knows. Confirm rather than assume.

## Acceptance

- [ ] A Peer who came in by code sets a password and deletes their account without using "Forgot password"
- [ ] Two-factor and passkeys open to them once confirmed by code
- [ ] Nothing changes for a person who chose a password
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~How Qori knows a person never chose a password.~~ **Answered from the
  code, 27 September 2026:** `password_set_at` (Decisions).
- ~~What proves identity in place of the password for those two actions.~~
  **Answered 27 September 2026:** the emailed code (Decisions).
- ~~Whether the security page offers passkeys and two-factor to a person with
  no password.~~ **Answered 27 September 2026:** as today, once confirmed
  (Decisions).
- ~~Deleting an account is the person's to do whatever the policy wording
  says.~~ **Answered:** the place is built here; the words are release
  checklist (`D-043`).

## Re-scope log

None.

## Notes

None.
