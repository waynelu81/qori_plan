---
id: T-008
title: Explain the verification detour and return to where it started
stream: identity
status: done
owner: claude
estimate: M
depends: T-007
blocks: T-027
---

# T-008 — Explain the verification detour and return to where it started

## Why

Somebody who follows a Series link, signs up, and is sent to a verification wall
is told nothing about what is waiting for them, and on the commonest ordering is
never returned to the Series they came for. R-003 reproduced it in a browser:
register from a public Series, open the verification email, land on
`/dashboard?verified=1` with no Series and no way back to one.

The screen itself is the other half. It says "Please verify your email address
by clicking on the link we just emailed to you", offers Resend and Log out, and
**never names the address it sent to**. A person who mistyped their email has no
way to see that from this page, and Resend sends another message to the same
wrong address.

## The trace, which is what this task was waiting on

Read from the framework and Fortify source on 11 September 2026, not guessed.
Three ways in, and they do not behave the same:

| Path                                                             | What stores a destination                                                                                                                  | Where verification lands today  |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------- |
| **A. Register from a public Series, then open the email**        | `PublicSeriesController::show()` puts `url.intended`; Fortify's `RegisterResponse` **consumes it** on the redirect back to the Series page | `/dashboard?verified=1` — wrong |
| **B. Press Get access first, hit the wall, then open the email** | `EnsureEmailIsVerified` calls `Redirect::guest()`, which stores the **referrer** for a non-GET request, so the Series page is stored again | The Series page — already right |
| **C. Open the email on another device**                          | Nothing. The signed route is behind `auth`, so that device is sent to sign in, and `Redirect::guest()` stores the signed link              | `/dashboard?verified=1` — wrong |

**So the mechanism is not missing, it is single-use.** `redirect()->intended()`
reads the session key and forgets it, and on path A something else spends it
before verification can. Path B works today and must keep working; a fix that
re-implements returning would put the one correct path at risk.

Everything behind `['auth', 'verified']` feeds these three: `dashboard`,
`start-sharing`, `checkout.store`, `series.grant`, the whole of
`routes/share.php` and `routes/shared.php`, and the `verified` group in
`routes/settings.php`.

Two smaller findings from the same read, both in scope because they are one line
each: `config/fortify.php` has no `redirects` block, so every Fortify response
falls back to `fortify.home`; and nothing in the front end reads `?verified=1`,
so a successful verification is currently silent.

## Decisions taken to make this specifiable

**A second key, not a change to `url.intended`.** The intended URL is the
framework's and Fortify spends it correctly for sign-in. This adds
`App\Support\SignInDestination`, which holds where somebody was going **and what
to call it**, is not consumed by an ordinary redirect, and is cleared when the
detour ends. Path B keeps working because nothing about `url.intended` changes.

**A label, not a URL to be parsed.** The verification screen has to name what is
waiting, and resolving an arbitrary path back into a Series title is fragile in
exactly the case that matters. Whoever stores the destination already knows the
title, so it is stored alongside it.

**Nothing here changes when verification is required.** Same routes, same
middleware, same wall. This is about what the wall says and where it lets go.

## Preconditions

`T-007` shipped, so a consumed magic link already verifies the address and the
commonest reason for this detour is gone.

## Scope

**In:**

- A destination that survives registration, the wall, and a sign-in on a second
  device, until verification consumes it.
- Copy on the verification screen naming the address it sent to and what is
  waiting on the other side.
- Landing back on that destination when verification completes.

**Out:**

- Changing when verification is required.
- The confirmation of a **changed** email address from settings. It goes through
  the same screen and deliberately has no Series destination; the copy must hold
  for it, and its flow is not otherwise touched.
- Anything a Peer sees after arriving. Confirming name, timezone and payment is
  `T-027`, and this task hands over at the Series page.
- Naming a `redirects` block in `config/fortify.php`. One key is added for email
  verification and the rest keep falling back to `fortify.home`.

## Files

| Path                                              | Change | Notes                                             |
| ------------------------------------------------- | ------ | ------------------------------------------------- |
| `app/Support/SignInDestination.php`               | new    | Store, read, clear. Static, session-backed        |
| `app/Http/Responses/VerifyEmailResponse.php`      | new    | First custom Fortify response; new directory      |
| `app/Providers/FortifyServiceProvider.php`        | edit   | Bind the response; give the notice view its props |
| `app/Http/Controllers/PublicSeriesController.php` | edit   | Remember the destination beside `url.intended`    |
| `resources/js/pages/auth/VerifyEmail.vue`         | edit   | Say where it went and what is waiting             |
| `lang/en/auth.php`                                | edit   | 4 keys                                            |
| `tests/Feature/Auth/VerificationDetourTest.php`   | new    | 9 cases                                           |

`lang/en/auth.php` is also claimed by `T-036`. Neither may be `doing` while the
other is; they add to different parts of the file and will not conflict if run
in sequence.

**Added during execution:**

| Path                                             | Change | Notes                         |
| ------------------------------------------------ | ------ | ----------------------------- |
| `resources/js/layouts/auth/AuthSimpleLayout.vue` | edit   | One `v-if` on the description |

The layout's description is a static `defineOptions` value and everything this
screen says is per-person, so the copy is rendered in the page body instead and
the layout's paragraph is left with nothing in it. One `v-if` hides it. No other
auth page changes, because every one of them passes a description.

## Database

None. A destination belongs to a session, not to a user: it is answered within
minutes, it differs per device, and a column would outlive its own meaning.

## Code

```php
// App\Support\SignInDestination
private const KEY = 'auth.destination';

/** Where somebody was going, and what to call it on the way. */
public static function remember(string $url, ?string $label = null): void;

/** Read without spending. The notice screen asks this every render. */
public static function peek(): ?array;

/** Read and clear. The detour is over. */
public static function take(): ?array;
```

Only internal URLs are stored. `remember()` refuses anything whose host is not
this application's, because a stored destination is a redirect somebody else
could otherwise choose.

```php
// App\Http\Responses\VerifyEmailResponse — replacing Fortify's
$destination = SignInDestination::take();

return redirect()->intended(
    $destination['url'] ?? Fortify::redirects('email-verification').'?verified=1',
);
```

`intended()` stays underneath deliberately. Path B stores a perfectly good
intended URL and this must not take it away; the destination is the fallback
that fires when something already spent it.

## Copy

All four in `lang/en/auth.php`, under a new `verification` block.

| Key                             | English                                                       |
| ------------------------------- | ------------------------------------------------------------- |
| `auth.verification.sent_to`     | `We sent a link to :email.`                                   |
| `auth.verification.waiting`     | `Confirm your address and we'll take you straight to :label.` |
| `auth.verification.generic`     | `Confirm your address to finish setting up your account.`     |
| `auth.verification.wrong_email` | `Wrong address? Sign out and start again with the right one.` |

`:label` is a Series title, so no article and no plural is built around it — the
product-noun rules do not apply to a name somebody typed. `generic` is what the
changed-email path and a direct signup see, and it promises nothing about a
destination because they have none.

## Routes

None. Every URL involved already exists.

## Tests

**New: `tests/Feature/Auth/VerificationDetourTest.php` — 9 cases**

1. `test_registering_from_a_series_returns_there_after_verifying` — path A, end
   to end. **Fails today**, landing on the dashboard.
2. `test_hitting_the_wall_still_returns_to_the_series` — path B, which works
   today. This is the regression guard, not a new capability.
3. `test_verifying_after_signing_in_on_another_device_returns_to_the_series` —
   path C.
4. `test_the_notice_names_the_address_it_sent_to`
5. `test_the_notice_names_what_is_waiting_when_there_is_a_destination`
6. `test_the_notice_says_nothing_about_a_destination_when_there_is_none` — the
   changed-email path, which must not be told it is going to a Series.
7. `test_a_destination_is_cleared_once_it_has_been_used` — verifying twice does
   not send somebody back a second time.
8. `test_an_external_url_is_never_stored_as_a_destination`
9. `test_someone_already_verified_is_not_sent_through_any_of_this`

**Changed:** none. `EmailVerificationTest` asserts the dashboard fallback for a
user with no destination, which stays true.

## Acceptance

- [x] Registering from a public Series and verifying lands back on that Series
- [x] Pressing the access button first and verifying still lands there
- [x] Verifying from a second device lands there too, **where that device has
      opened the Series link** — see the first entry under Notes
- [x] The verification screen names the address it sent to
- [x] The screen names the Series when there is one, and claims nothing when
      there is not
- [x] A destination is used once and then gone
- [x] An external URL is never accepted as a destination
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**2026-09-11, R-003 F-1 — confirmed browser reproduction.** Open the free public
Series **Reading a Room Before You Speak**, follow **Sign in to get access →
Sign up**, select Learn and register a new account. Registration correctly
returns to the public Series with **Get access**. Before pressing that button,
open the new account's verification email: the person lands at
`/dashboard?verified=1` with no Series or return action.

**Path B was never walked.** R-003 found path A and inferred the rest; reading
`Redirector::guest()` shows path B storing the referrer for a non-GET request,
which means the access button already behaves. Worth knowing before anyone
rewrites the return path: two-thirds of this task is holding a destination that
registration spends, not building one.

**Nothing reads `?verified=1`.** Verification succeeds and the page it lands on
says nothing about it. Out of scope here because it is a dashboard question and
this task hands over at the Series, but it is the reason path A feels like
nothing happened rather than like something went wrong.

**Owner clarification, 2026-09-11.** The preserved destination continues through
`T-027`'s name, email and timezone confirmation and its payment or access step,
not into creator guidance. Series-linked entry stays a receiving journey even
for an account that owns a Group. `T-026` supplies staged setup for direct
creator entry instead. This task owns the destination up to the Series page and
hands it to `T-027` there.

**A session cannot follow somebody to a device it has never met.** The
Acceptance line "Verifying from a second device lands there too" asks for more
than the specified design can give, which PROCESS calls a defect in the task
rather than a re-scope: a destination lives in a session, and a browser that has
never opened the Series link has no session carrying one. What path C actually
fixes is the spend — a device that _has_ opened the link loses its intended URL
to the sign-in the signed link forces, and that is what the second key survives.
Reaching a device that never saw the Series needs the destination on the user or
on the signed link, and both were ruled out here on purpose. Test 3 walks the
reachable shape and says so in its docblock.

**The Scope's last "Out" bullet contradicts itself**, and the Files table
settles it. It excludes "Naming a `redirects` block in `config/fortify.php`" and
then says "One key is added for email verification" — which would be naming one.
`config/fortify.php` is not in the Files table and the Tests section requires
`EmailVerificationTest`'s dashboard fallback to keep passing, so no config key
was added. `Fortify::redirects('email-verification')` falls through to
`fortify.home` exactly as before.
