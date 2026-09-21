---
id: T-073
title: Get access from the Series page without leaving it
stream: onboarding
status: done
owner: claude
estimate: M
depends: none
blocks: T-074
---

# T-073 — Get access from the Series page without leaving it

## Why

The owner walked the Peer path on 13 September 2026 and called it broken into
pieces. From `GET /s/{group}/{series}` a stranger is offered "Sign in to get
access", which is a sign-in page; from there, a registration page that asks
whether they came to share or to learn, then a name, an email and a password;
then a wall that says a link was sent; then their mail app, on a phone a
different app; then the link, which lands them back on the Series; then the
consent box and the button they came for. Seven screens and one change of
app before anything is bought, for a person who arrived holding a link that
already says what they want.

Two of those screens exist to prove the address. That has to stay: a mistyped
address is an account nobody can recover, and it has to be caught before money
moves. But proving it does not need a link that opens somewhere else. A code
the person reads off the notification and types where they already are proves
the same thing, and on a phone the mail app never has to be opened — iOS and
Android show the code in the notification and offer to fill it.

Afterwards: a stranger types a name and an email on the Series page, a
six-digit code arrives, they type it on the same page, and they are signed in
with a verified address, still on the Series, one click from access. `T-074`
removes that last click. Somebody who already has an account types the same
email and gets the same code; the page never says which it was.

## Decisions taken to make this specifiable

**No password at the door.** A Peer receives; a password is for coming back,
and the magic link and this code both do that already. The account is created
with a random password nobody knows. Choosing one later belongs on the
security page and is not this task's.

**A typed code, not a second link.** The link stays on the sign-in page for
the people who like it. The code is six digits, hashed in the cache under the
user, valid ten minutes, five attempts, replaced by every resend. Verifying it
does exactly what following a magic link does: marks the address verified,
fires `Verified`, signs in, regenerates the session.

**One response for both kinds of address.** An email that already has an
account gets a code for that account; the name typed beside it is ignored. An
email that has none gets an account. The page says the same thing either way,
so it cannot be used to check who has signed up.

**Registered fires, with the intent already answered.** The new account is
created outside Fortify, and `Registered` is fired so the listeners that hang
off registration run. The request carries `signup_intent=learn` merged in
before the event, because `CreateGroupForNewUser` reads the request and a
Peer must not get a Group.

**The pending step lives in the session.** Which Series, which user, which
email, under one key, read by the page to render the code step and by the
verify action to know who is proving what. Forgotten on success and on "start
again".

**Guests only.** A signed-in person sees the button they always saw. The
start, resend and verify actions are behind `guest`.

## Preconditions

`T-008` done: `SignInDestination` already carries the Series through a detour
and `PublicSeriesController` already stores it. `T-036` done: the sign-in
composition is settled and this task does not touch it.

## Scope

**In:**

- `LoginCodeService` and `LoginCodeNotification`.
- The three guest actions on the Series page: start, resend, verify.
- The page's guest state becoming a name and email form, and a code step while
  a code is pending, with resend and a way to start over.
- Creating the Peer account without a password and without a Group.
- `docs/flows/auth.md` and `docs/flows/checkout.md` ("The path in"), and a
  `docs/tinker/auth.md` recipe for reading the code from Mailpit.

**Out:**

- Continuing to access after the code (`T-074`): here the person lands back on
  the page signed in, with the existing button and consent box.
- Offering the code on the sign-in page. The magic link is there.
- Setting a password for an account created here.
- Confirming name, email and timezone as a step (`T-027`'s remaining scope).

## Files

| Path                                                                  | Change | Notes                                                              |
| --------------------------------------------------------------------- | ------ | ------------------------------------------------------------------ |
| `app/Services/LoginCodeService.php`                                   | new    | Mint, store hashed, verify, forget                                 |
| `app/Notifications/LoginCodeNotification.php`                         | new    | The mail; code in the subject so a notification shows it           |
| `app/Support/SeriesAccessPending.php`                                 | new    | The session key and its shape                                      |
| `app/Http/Controllers/SeriesAccessController.php`                     | new    | `start()`, `resend()`, `verify()`                                  |
| `app/Http/Requests/StartSeriesAccessRequest.php`                      | new    | `name`, `email`                                                    |
| `app/Http/Requests/VerifySeriesAccessRequest.php`                     | new    | `code`                                                             |
| `app/Http/Controllers/PublicSeriesController.php`                     | edit   | `viewer.pending`, `join` copy                                      |
| `resources/js/pages/public/Series.vue`                                | edit   | Guest form; code step                                              |
| `routes/web.php`                                                      | edit   | Three POSTs                                                        |
| `lang/en/accesses.php`                                                | edit   | `join.*`                                                           |
| `lang/en/auth.php`                                                    | edit   | `code.*` (the mail)                                                |
| `lang/en/errors.php`                                                  | edit   | `access.code_wrong`, `access.code_spent`, `access.nothing_pending` |
| `docs/flows/auth.md`, `docs/flows/checkout.md`, `docs/tinker/auth.md` | edit   | The path in                                                        |
| `tests/Feature/Access/SeriesAccessCodeTest.php`                       | new    | 12 cases                                                           |

## Database

None. The code lives in the cache; the pending step in the session.

## Code

```php
namespace App\Services;

class LoginCodeService
{
    public const LIFETIME_MINUTES = 10;
    public const MAX_ATTEMPTS = 5;
    public const LENGTH = 6;

    /** Mint a code, store its hash with zero attempts under key($user) for LIFETIME_MINUTES, notify. Replaces any earlier code. */
    public function send(User $user): void;

    /**
     * True, and the code forgotten, on a match. False and one attempt spent on a
     * mismatch; the code is forgotten when attempts reach MAX_ATTEMPTS. False
     * with nothing stored — expired, spent, or never sent — without saying which.
     */
    public function verify(User $user, string $code): bool;

    /** Whether a code is outstanding for this user. */
    public function pending(User $user): bool;

    private static function key(User $user): string;   // 'login-code:'.$user->getKey()
}
```

The stored value is `['hash' => Hash::make($code), 'attempts' => 0]`. Six digits
from `random_int(0, 999999)`, zero-padded. Comparison through `Hash::check`.

```php
namespace App\Notifications;

class LoginCodeNotification extends Notification
{
    public function __construct(public string $code, public int $minutes) {}
    public function toMail(object $notifiable): MailMessage;   // subject auth.code.subject, lines auth.code.line, auth.code.ignore
}
```

```php
namespace App\Support;

class SeriesAccessPending
{
    public const KEY = 'series.access.pending';

    public static function remember(Series $series, User $user): void;   // ['series_id' => …, 'user_id' => …, 'email' => $user->email]
    /** @return ?array{series_id: string, user_id: string, email: string} */
    public static function peek(): ?array;
    public static function forget(): void;
}
```

```php
namespace App\Http\Controllers;

class SeriesAccessController extends Controller
{
    public function __construct(private LoginCodeService $codes) {}

    /**
     * Find the account for the address or create one — name, email, a random
     * password, no Group — then send a code and remember the step. Same
     * redirect either way: back to the Series page.
     */
    public function start(StartSeriesAccessRequest $request, string $seriesId): RedirectResponse;

    /** A fresh code for the pending user; nothing pending is errors.access.nothing_pending. */
    public function resend(Request $request, string $seriesId): RedirectResponse;

    /**
     * verify() true → markEmailAsVerified() if not already, event(Verified),
     * Auth::login(), session regenerate, forget pending, redirect to the Series
     * page. False → errors.access.code_wrong when a code is still pending,
     * errors.access.code_spent when none is.
     */
    public function verify(VerifySeriesAccessRequest $request, string $seriesId): RedirectResponse;
}
```

Creating the account: `User::create(['name', 'email', 'password' => Str::password(32)])`,
then `$request->merge(['signup_intent' => SignupIntent::Learn->value])` and
`event(new Registered($user))`. The Series is `Series::findForPeer($seriesId)`
and must be published, else `errors.access.series_unavailable`. On resend and
verify, a pending step naming a different Series than `{seriesId}` is
`errors.access.nothing_pending`.

`StartSeriesAccessRequest::rules()`: `name` required string max 120 (the profile
rule), `email` required email max 255. `VerifySeriesAccessRequest::rules()`:
`code` required, `digits:6`.

`PublicSeriesController::show()` gains, for a guest, `viewer.pending` as
`['email' => …]` when `SeriesAccessPending::peek()` names this Series, else
null; and a `join` array of the copy below, rendered whether or not a code is
pending. The `Sign in to get access` link stays, under the form, as the way
for somebody with a password.

In `Series.vue` the guest branch becomes: with no pending code, a `<Form>` to
`series.access.start` with `name`, `email` and the Continue button, the intro
above and the sign-in link below; with a pending code, `join.code_sent` naming
the email, an `InputOTP` of six slots named `code` in a `<Form>` to
`series.access.verify`, `join.code_help`, a resend `<Form>` to `series.access.resend`, and a
start-over `<Form method="delete">` to `series.access.cancel`, which forgets
the pending step.

## Copy

| Key                                        | File                   | English                                                                      |
| ------------------------------------------ | ---------------------- | ---------------------------------------------------------------------------- |
| `accesses.join.intro`                      | `lang/en/accesses.php` | Tell us who you are and we'll email you a code. Type it here and you're in.  |
| `accesses.join.name_label`                 | `lang/en/accesses.php` | Your name                                                                    |
| `accesses.join.email_label`                | `lang/en/accesses.php` | Your email                                                                   |
| `accesses.join.continue`                   | `lang/en/accesses.php` | Continue                                                                     |
| `accesses.join.code_sent`                  | `lang/en/accesses.php` | We sent a :length-digit code to :email.                                      |
| `accesses.join.code_label`                 | `lang/en/accesses.php` | Your code                                                                    |
| `accesses.join.code_help`                  | `lang/en/accesses.php` | It works for :minutes minutes. Nothing to open in your inbox — just type it. |
| `accesses.join.confirm`                    | `lang/en/accesses.php` | Confirm                                                                      |
| `accesses.join.resend`                     | `lang/en/accesses.php` | Send another code                                                            |
| `accesses.join.resent`                     | `lang/en/accesses.php` | A new code is on its way.                                                    |
| `accesses.join.start_over`                 | `lang/en/accesses.php` | Wrong address? Start again.                                                  |
| `accesses.join.have_password`              | `lang/en/accesses.php` | Have a password? Sign in instead.                                            |
| `auth.code.subject`                        | `lang/en/auth.php`     | Your Qori code is :code                                                      |
| `auth.code.line`                           | `lang/en/auth.php`     | Type :code on the page you came from. It works for :minutes minutes.         |
| `auth.code.ignore`                         | `lang/en/auth.php`     | If you didn't ask for this, ignore it. Nothing happens without the code.     |
| `errors.access.code_wrong.message`         | `lang/en/errors.php`   | That code didn't match.                                                      |
| `errors.access.code_wrong.resolution`      | `lang/en/errors.php`   | Check the latest email we sent and try again.                                |
| `errors.access.code_spent.message`         | `lang/en/errors.php`   | That code has expired or been used up.                                       |
| `errors.access.code_spent.resolution`      | `lang/en/errors.php`   | Send another code and try again.                                             |
| `errors.access.nothing_pending.message`    | `lang/en/errors.php`   | There's no sign-in in progress here.                                         |
| `errors.access.nothing_pending.resolution` | `lang/en/errors.php`   | Start again from the page you were on.                                       |

`:length` and `:minutes` are interpolated from the service's constants.

## Routes

| Verb   | Path                         | Name                   | Action                          | Middleware                     |
| ------ | ---------------------------- | ---------------------- | ------------------------------- | ------------------------------ |
| POST   | `s/{seriesId}/access`        | `series.access.start`  | `SeriesAccessController@start`  | `guest`, `throttle:magic-link` |
| POST   | `s/{seriesId}/access/resend` | `series.access.resend` | `SeriesAccessController@resend` | `guest`, `throttle:magic-link` |
| POST   | `s/{seriesId}/access/code`   | `series.access.verify` | `SeriesAccessController@verify` | `guest`, `throttle:6,1`        |
| DELETE | `s/{seriesId}/access`        | `series.access.cancel` | `SeriesAccessController@cancel` | `guest`                        |

`cancel()` forgets the pending step and redirects to the Series page. The
`magic-link` limiter keys on email and IP; `start()` and `resend()` both carry
an email (resend reads it from the pending step and the limiter reads the
input, so `resend()` merges the pending email into the request first).

## Tests

**New: `tests/Feature/Access/SeriesAccessCodeTest.php` — 12 cases**, with
`Notification::fake()` and a published free Series in a Group.

1. `test_a_stranger_gets_an_account_and_a_code_from_the_series_page` — POST
   start with a name and a new email: a `User` exists with that email,
   unverified, no password the test can know; `LoginCodeNotification` sent to
   it; 302 to the Series page; session holds the pending step for this Series.
2. `test_the_new_account_gets_no_group` — after case 1's POST, no Group has
   that user as owner and no Collaborator row exists for them.
3. `test_an_existing_address_gets_a_code_and_no_second_account` — POST start
   with an existing user's email and a different name: user count unchanged,
   the user's name unchanged, notification sent to that user, same 302.
4. `test_the_code_signs_in_and_verifies_the_address` — read the code from the
   faked notification; POST verify: authenticated as the user,
   `email_verified_at` set, `Verified` dispatched (`Event::fake([Verified::class])`),
   pending forgotten, 302 to the Series page.
5. `test_a_wrong_code_spends_an_attempt_and_signs_nobody_in` — guest still,
   `errors.access.code_wrong` flashed, the right code still works afterwards.
6. `test_five_wrong_codes_spend_the_code` — five wrong, then the right one:
   refused with `errors.access.code_spent`, guest still.
7. `test_a_code_expires` — `$this->travel(11)->minutes()` then the right code:
   `code_spent`.
8. `test_resend_replaces_the_code` — start, resend: two notifications; the
   first code fails, the second signs in.
9. `test_verify_without_a_start_is_refused` — no pending step: `nothing_pending`,
   302 to the Series page, guest still.
10. `test_start_over_forgets_the_step` — DELETE cancel: pending gone, the page
    renders the name and email form again.
11. `test_a_signed_in_person_keeps_the_button` — GET as a user: `viewer.pending`
    null, `viewer.signedIn` true; POST start as a user: redirected away by `guest`.
12. `test_starting_is_throttled` — four POSTs to start inside a minute from one
    address: the fourth answers 429.

## Acceptance

- [x] Signed out, at 360px, a stranger types a name and an email on the Series
      page, receives a code, types it on the same page, and is signed in with a
      verified address, still on the Series, with the access button showing
- [x] Somebody with an account and no password gets in the same way, and the
      page never says whether the address was known
- [x] The account created has no Group and no sharing nav
- [x] A wrong code, a spent code and a missing start are each refused with
      their own words, and none signs anybody in
- [x] The mail's subject carries the code, read from Mailpit
- [x] `docs/flows/auth.md` shows the code beside the link
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

Cut from `T-027` on 13 September 2026 as its first slice; `T-027` keeps the
name, email and timezone confirmation and the direct receiving welcome. The
consent box stays on the signed-in button here and moves onto the guest form
in `T-074`, which is also where the second click goes.

The code is the same proof the magic link is, and `MagicLinkLoginController::login()`
already documents why proving the inbox marks it verified. Do not duplicate
that paragraph; refer to it.
