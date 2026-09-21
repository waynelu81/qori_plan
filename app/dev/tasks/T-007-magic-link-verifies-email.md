---
id: T-007
title: A consumed magic link verifies the address it was sent to
stream: identity
status: done
owner: claude
estimate: S
depends: none
blocks: T-008
---

# T-007 — A consumed magic link verifies the address it was sent to

## Why

`MagicLinkLoginController::login()` signs the user in and leaves
`email_verified_at` alone. So somebody who proves control of their inbox — by
receiving a signed, single-use, 15-minute link at that exact address and
clicking it — is then sent to a "please verify your email" wall. The proof
already happened; the product just did not record it.

This is the same principle `EmailChangeService` already applies to a changed
address, and the reason the link is safe to trust: it is signed (ours),
expiring (recent), single-use (not replayed) and addressed (that mailbox).

## Scope

**In:**

- Marking the user verified when, and only when, a magic link is consumed.
- Firing Laravel's `Verified` event so anything listening behaves as it does
  after the ordinary verification click.

**Out:**

- Passkey sign-in. A passkey proves possession of a device, not of a mailbox.
- Password sign-in, which proves neither.
- The verification-detour copy — that is `T-008`.

## Files

| Path                                                     | Change | Notes                      |
| -------------------------------------------------------- | ------ | -------------------------- |
| `app/Http/Controllers/Auth/MagicLinkLoginController.php` | edit   | Mark verified in `login()` |
| `tests/Feature/Auth/MagicLinkTest.php`                   | edit   | Add 3 cases                |

## Database

None. `users.email_verified_at` already exists and is already cast to
`datetime`.

## Code

In `App\Http\Controllers\Auth\MagicLinkLoginController::login()`, between the
nonce check and `Auth::login($user)`:

```php
// A magic link is proof of the mailbox it was sent to: signed, expiring,
// single-use and addressed. Recording that is not a convenience — without
// it, somebody who has just proved control of their inbox is shown a wall
// asking them to prove control of their inbox.
if (! $user->hasVerifiedEmail()) {
    $user->markEmailAsVerified();

    event(new Verified($user));
}
```

`markEmailAsVerified()` comes from `Illuminate\Auth\MustVerifyEmail`, which
`App\Models\User` already uses; it saves the model and returns `bool`. Fire the
event separately rather than relying on the trait, which does not.

Add to the imports:

```php
use Illuminate\Auth\Events\Verified;
```

Guarded on `hasVerifiedEmail()` so a returning user's original verification
timestamp is not overwritten on every sign-in — the date is evidence of when
the mailbox was first proved, and moving it forward erases that.

## Copy

None. No user-facing string changes; the wall simply stops appearing.

## Routes

None.

## Tests

**Changed: `tests/Feature/Auth/MagicLinkTest.php` — 3 new cases**

1. `test_consuming_a_magic_link_verifies_an_unverified_address` — create a user
   with `email_verified_at = null`, request a link, follow it, assert
   `hasVerifiedEmail()` is true and the redirect is to `dashboard` rather than
   the verification notice.
2. `test_it_does_not_move_an_existing_verification_timestamp` — user verified
   at a known past time; consume a link; assert `email_verified_at` is
   unchanged to the second.
3. `test_it_dispatches_the_verified_event` — `Event::fake([Verified::class])`,
   consume a link, `Event::assertDispatched`.

Check first whether `tests/Feature/Auth/MagicLinkTest.php` exists under that
exact name; if the suite calls it something else, add the cases there rather
than creating a second file.

## Acceptance

- [x] An unverified user who follows a magic link lands on the dashboard, not
      the verification notice
- [x] A verified user's original timestamp survives a later magic-link sign-in
- [x] `Verified` fires exactly once, on the transition
- [x] Password sign-in still leaves verification alone (assert or reason about
      it — do not change that path)
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)

## Re-scope log

None.

## Notes

The test file is `tests/Feature/Auth/MagicLinkRoutesTest.php`, not
`MagicLinkTest.php` as the spec guessed — the cases were added there, which is
what the spec's own instruction said to do if the name differed.

A fourth case was added beyond the three specified:
`test_signing_in_with_a_password_does_not_verify_the_address`. The spec put
password sign-in under **Out** and said to "assert or reason about it"; a test
is the cheaper of the two, because the tempting next change is to make the
sign-in paths consistent, and consistency here would mean verifying an address
on evidence that does not exist.
