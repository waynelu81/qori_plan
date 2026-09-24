---
id: T-202
title: A Series is remembered whichever host the site was reached on
stream: onboarding
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-202 — A Series is remembered whichever host the site was reached on

## Why

"Have a password? Sign in instead." on a Series page stores the page to come
back to twice: as the framework's `url.intended`, and as `SignInDestination`
(`PublicSeriesController::signIn()`, `T-084`). The second is built with
`route('series.public', …)`, an absolute URL on whatever host the request came
in on, and `SignInDestination::remember()` silently refuses any URL whose host
is not `APP_URL`'s (`app/Support/SignInDestination.php:87-104`). So on a
second host nothing is stored, and everything that reads it quietly fails:
the verification wall cannot name the Series (`T-008`), verifying cannot
return to it, and since `T-196` the register page asks "What brings you
here?" again and the listener makes a Group for a Peer who leaves "I want to
share" ticked.

Found on 24 September 2026 walking `T-196`: the dev server reached at
`127.0.0.1:8001` with `APP_URL=http://localhost:8001` stored nothing, and the
same walk on `localhost:8001` worked. Nothing pins URLs to `APP_URL`
(no `URL::forceRootUrl()`), so production has the same exposure on any second
hostname that serves the app without redirecting — a `www.` or the platform's
default domain.

Afterwards the Series is remembered whichever host the page was reached on,
and a URL pointing off the application is still refused.

## Decisions taken to make this specifiable

**Store the path, not the absolute URL.** `signIn()` passes
`route('series.public', […], absolute: false)` to both keys. A path has no
host, which `isInternal()` already accepts, and every reader resolves it on
the host the person is on: `redirect()->intended()` hands the stored value to
`UrlGenerator::to()`, which makes a path absolute on the request's root, and
that is how `LoginResponse`, `TwoFactorLoginResponse`, `PasskeyLoginResponse`,
`MagicLinkLoginController`, Fortify's `RegisterResponse` and
`VerifyEmailResponse` all spend `url.intended` and the destination. The
verification wall, the register page (`T-196`) and `CreateGroupForNewUser`
read only the label or whether one is stored, and `SignInLanding::isHome()`
compares only the path. Nothing compares the stored URL with another.

**The host check stays.** It is what refuses a destination pointing off the
application — `https://example.net/…` and `//example.net/…` — and no reader
needs it to accept a second host once the value is a path.

**`signIn()`'s own redirect for somebody already signed in uses the same
path.** `redirect()->to()` resolves it on the request's host, as before.

## Preconditions

**Data this task verifies against:** a clean database; a published Series
from a factory.

**Equipment:** a browser reaching the dev server on a host other than
`APP_URL`'s (`127.0.0.1` against `localhost`).

## Scope

**In:**

- The Series page's sign-in link remembering its Series as a path, so it is
  kept on any host.

**Out:**

- Redirecting a second hostname to the canonical one: production
  configuration, on the release checklist if the owner wants it.
- `url.intended` as the `auth` guard and the `verified` wall write it: the
  framework's own absolute URL of the page the person asked for, which no
  host check reads.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Http/Controllers/PublicSeriesController.php` | edit | `signIn()` stores the path |
| `docs/flows/auth.md` | edit | "Where a sign-in returns to": the destination is a path |
| `tests/Feature/PublicSeriesTest.php` | edit | the host case; the stored value is the path |
| `tests/Feature/Auth/VerificationDetourTest.php` | edit | the stored value is the path |
| `tests/Feature/Auth/SignupIntentTest.php` | edit | `T-196` on another host |

## Database

None.

## Code

```php
// PublicSeriesController::signIn()
$url = route('series.public', ['group' => $group, 'series' => $series], absolute: false);
```

The rest of `signIn()` is unchanged: the same `$url` goes to `url.intended`,
to `SignInDestination::remember()` with the title, and to the signed-in
redirect.

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/PublicSeriesTest.php` — 1 new case, 1 changed**

1. `test_a_guest_is_remembered_on_a_host_other_than_the_app_url` — the
   sign-in link requested at `http://127.0.0.1/…` while `app.url` is
   `http://localhost`: `url.intended` and `SignInDestination::peek()` hold
   the Series' path, with its title.

`test_a_guest_is_remembered_when_they_ask_to_sign_in` asserts the path
instead of the absolute URL.

**Changed: `tests/Feature/Auth/SignupIntentTest.php` — 1 new case**

2. `test_signing_up_on_another_host_while_a_series_waits_makes_no_group` —
   the sign-in link and the registration both at `http://127.0.0.1`: the new
   user has no Group.

**Changed: `tests/Feature/Auth/VerificationDetourTest.php`**

`test_someone_already_verified_is_not_sent_through_any_of_this` asserts the
path in `SignInDestination::peek()`; its redirect assertion is unchanged,
because `assertRedirect()` resolves both sides.

2 new, 2 changed.

## Acceptance

- [x] The Series page's sign-in link remembers its Series on a host other than `APP_URL`'s, walked in a browser on `127.0.0.1`: sign-up there names the Series and makes no Group
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

**2026-09-24 — brought to ready.** The draft's one open bullet, answered from
the code: every reader of the stored URL either spends it through
`redirect()->intended()`, which resolves a path on the request's host, or
reads only its label or its presence (Decisions). The two tests that pinned
the absolute URL are in Files.

## Notes

None.
