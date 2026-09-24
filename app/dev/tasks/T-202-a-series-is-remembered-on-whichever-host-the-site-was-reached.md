---
id: T-202
title: A Series is remembered whichever host the site was reached on
stream: onboarding
status: draft
owner: unassigned
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

**Proposed: store the path, not the absolute URL.** `signIn()` passes
`route('series.public', […], absolute: false)` to both keys. A path has no
host, which `isInternal()` already accepts, and a redirect to a path stays on
whatever host the person is on — which is also the right answer for
`url.intended`. The host check stays for what it is for: refusing a
destination that points somewhere else.

## Preconditions

**Data this task verifies against:** a clean database; a published Series
from a factory.

**Equipment:** a browser reaching the dev server on a host other than
`APP_URL`'s (`127.0.0.1` against `localhost`).

## Scope

**In:**

- The Series page's sign-in link remembering its Series on any host.

**Out:**

- Redirecting a second hostname to the canonical one: production
  configuration, release checklist.
- Any other writer of `url.intended`; only `signIn()` writes
  `SignInDestination`.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Http/Controllers/PublicSeriesController.php` | edit | `signIn()` stores the path |
| `docs/flows/auth.md` | edit | "Where a sign-in returns to": the destination is a path |
| `tests/Feature/PublicSeriesTest.php` | edit | the host case |

## Database

None.

## Code

`PublicSeriesController::signIn()`: `$url = route('series.public', ['group'
=> $group, 'series' => $series], false);` — the rest unchanged.

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/PublicSeriesTest.php` — 1 new case**

1. `test_a_guest_is_remembered_on_a_host_other_than_the_app_url` — the
   sign-in link requested on `http://127.0.0.1` with `app.url` at
   `http://localhost`: `SignInDestination::peek()` holds the Series' path and
   title.

`test_a_guest_is_remembered_when_they_ask_to_sign_in` and the `T-084` cases
that assert the stored URL may need the path instead of the absolute URL.

## Acceptance

- [ ] The Series page's sign-in link remembers its Series on a host other than `APP_URL`'s, walked in a browser on `127.0.0.1`
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Confirm the proposal against every reader of the stored URL:
  `VerifyEmailResponse`, the verification wall and the `T-084` forgetting,
  and that a relative `url.intended` survives Fortify's `RegisterResponse`
  and `LoginResponse`.

## Re-scope log

None.

## Notes

None.
