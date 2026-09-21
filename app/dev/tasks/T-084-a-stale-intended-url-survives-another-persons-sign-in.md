---
id: T-084
title: A stale intended URL survives another person's sign-in
stream: identity
status: done
owner: claude
estimate: M
depends: none
blocks: none
---

# T-084 — A stale intended URL survives another person's sign-in

## Why

`PublicSeriesController::show()` writes `url.intended` and `auth.destination`
on every guest visit, so that a sign-in from the Series page returns there.
Nothing ties either key to the sign-in it was meant for. Every sign-in path
regenerates the session, and `Store::regenerate()` changes the id and keeps
the data; only sign-out's `invalidate()` empties it. So a browser that passed
a Series as a guest, or was bounced to sign-in from a page and then left,
hands the next sign-in there a destination that was never theirs. Three
browser walks landed on "We couldn't find that group" or on a Series instead
of setup (`T-072`, `T-062`, `T-075`), and on 16 September 2026 both shapes
were reproduced again with a link minted by `qori:magic-link`.

Afterwards, reading a Series stores nothing; asking to sign in from it does.
A link opened in a browser that did not ask for that account's link forgets
what the browser was holding, and lands where a sign-in with nothing intended
lands. The code sign-in on a Series page leaves nothing behind.

## Decisions taken to make this specifiable

**Reading a Series stores nothing; asking to sign in from it does.** The page
stored on every guest view, so whoever signed in next in that browser — by a
typed address, a registration from the home page, or a link — was sent to a
page they had only passed. **Have a password? Sign in instead.** is the page's
one way to the sign-in page, so it goes through a route that stores the page
and then shows sign-in. The code form needs nothing stored: its redirects
already name the Series.

**The new route is a GET, by slug, like the page.** It is a link a person
follows, and it takes the two slugs the page's own URL carries. Nothing on the
page prefetches it, and a crawler that follows it stores a destination in a
session nobody holds. A signed-in person who reaches it is sent back to the
Series with nothing stored.

**The page gets the route as a prop, `signInUrl`.** The page's props carry the
Series id and not its slugs, which were removed as unread; a prepared URL puts
nothing back that the page would have to assemble.

**A link returns to what this browser holds only if this browser asked for
that account's link.** The link is the one sign-in that can finish somewhere
other than where it began — another device, another browser, the
`qori:magic-link` command — and all three reports' walks were that shape.
`store()` records the account in the session, only when the address has one,
with the response unchanged either way, so the record says nothing about who
is registered. `login()` pulls the record and, when it names any other
account or nothing, forgets both keys before `intended()` runs.

**Both keys are forgotten together, by `SignInDestination::forget()`.** `T-008`
made them a pair written in one place. A pair cleared by halves leaves the
verification wall naming a page the sign-in no longer returns to.

**The code sign-in on a Series page forgets both keys.** It is the one sign-in
that spent neither, so a destination stored before it waited for a later
sign-in that was never meant to have it.

**The password, two-factor and passkey responses do not change.** They already
spend `url.intended` through `intended()`, and after this they can only find
one stored by a page this browser asked to return to, or by the guard's own
redirect from a protected page. A named destination left after a verified
sign-in has no reader but a re-opened verification link, which returns that
same person to the page they asked for; sign-out empties the rest.

**Not the draft's first shape, clearing on the sign-in page render.** The
guard's redirect stores the protected page and then renders sign-in, so
clearing on render would break returning from every protected page. Storing
on the request that asks for sign-in is what "unless the page it came from set
one" needed.

**Not the draft's second shape, the session id beside the URL.** The id only
changes at sign-in and sign-out, so the stale URL and the next person's
sign-in share one id, and the comparison passes exactly when it should fail.

**No time limit on a stored destination.** The reported cases close without
one, any number would strand a slow legitimate sign-in, and the session's own
lifetime already bounds it.

**What this leaves, on purpose.** Two people at one browser, where the first
asked to sign in, or was bounced from a protected page, and walked away, and
the second signs in there with a password, a passkey or a link asked for
there: the second still lands on the first person's page. Qori cannot tell two
guests at one browser apart. Closing it needs the destination to travel in
the sign-in page's URL instead of the session, which changes how every
destination moves and reverses `T-008`'s choice of a second key beside
`url.intended`. Recorded as `D-017`.

## Preconditions

**Data this task verifies against:** a clean database for the tests. For the
browser walk, a probe creator with a free published Series and a probe account
with no Group, made in tinker through `GroupService`, `SeriesService` and
`EpisodeService` as `qori:mail:check` does, and deleted afterwards.

**Equipment:** a browser against `localhost:8001`, and
`php artisan qori:magic-link` to mint a link the browser did not ask for.

## Scope

**In:**

- `GET /s/{group}/{series}/sign-in` stores both keys for a guest and shows
  sign-in; `show()` stores nothing and hands the page that URL for **Have a
  password? Sign in instead.**
- The link request records the account asked for; opening a link for any other
  account, or with no record, forgets both keys.
- `SignInDestination::forget()`, clearing both keys.
- The code sign-in forgets both keys.
- A test for each sign-in path, the Series page's tests, and the verification
  detour tests that stored a destination by reading a Series.
- `docs/flows/auth.md`, `docs/flows/series.md`, `docs/tinker/auth.md`,
  `D-017`.

**Out:**

- Where a sign-in lands when nothing is stored — `T-052` settled that.
- The register response, which spends `url.intended` returning a new account to
  the page it asked to sign in from, and is right to.
- The password, two-factor, passkey and verification responses (Decisions).
- Two guests at one browser (Decisions, last).
- A stored page the right person can no longer open, such as a Group they were
  removed from; that is the ordinary not-found page with its way home.
- Emptying the rest of the session when a link signs a second account in over
  a first.

## Files

| Path                                                     | Change | Notes                                                                     |
| -------------------------------------------------------- | ------ | ------------------------------------------------------------------------- |
| `app/Http/Controllers/PublicSeriesController.php`        | edit   | `show()` stores nothing and passes `signInUrl`; new `signIn()`            |
| `routes/web.php`                                         | edit   | `GET s/{group}/{series}/sign-in`, `series.sign-in`                        |
| `resources/js/pages/public/Series.vue`                   | edit   | `signInUrl` prop; the "Have a password?" link follows it                  |
| `app/Support/SignInDestination.php`                      | edit   | `forget()`                                                                |
| `app/Http/Controllers/Auth/MagicLinkLoginController.php` | edit   | `REQUESTED_KEY`; `store()` records the account, `login()` compares        |
| `app/Http/Controllers/SeriesAccessController.php`        | edit   | `verify()` forgets both keys                                              |
| `tests/Feature/Auth/StaleDestinationTest.php`            | new    | 10 cases                                                                  |
| `tests/Feature/PublicSeriesTest.php`                     | edit   | 1 changed, 3 new                                                          |
| `tests/Feature/Auth/VerificationDetourTest.php`          | edit   | 5 changed: they ask to sign in from the Series instead of only reading it |
| `docs/flows/auth.md`                                     | edit   | Where a sign-in returns to; the link's record; the code path              |
| `docs/flows/series.md`                                   | edit   | The guest row                                                             |
| `docs/tinker/auth.md`                                    | edit   | A minted link lands on the account's own landing                          |
| `docs/planning/decisions.md`                             | edit   | `D-017`                                                                   |

## Database

None.

## Code

```php
// App\Http\Controllers\PublicSeriesController

// No longer writes url.intended or auth.destination. Adds one prop:
// 'signInUrl' => route('series.sign-in', ['group' => $group, 'series' => $series])
public function show(Request $request, string $group, string $series): Response;

/**
 * Have a password? Sign in instead: the one way from a Series page to the
 * sign-in page, and the one place a destination is stored for it (T-084).
 */
public function signIn(Request $request, string $group, string $series): RedirectResponse;
```

`signIn()`, in order: `Series::findPublic($group, $series)`, else
`AppException::notFound('errors.access.series_unavailable')`, as `show()`;
`$url = route('series.public', ['group' => $group, 'series' => $series])`;
signed in (`CurrentUser::of($request) !== null`) → `redirect()->to($url)` with
nothing stored; a guest → `$request->session()->put('url.intended', $url)`,
`SignInDestination::remember($url, $model->title)`, then
`redirect()->route('login')`. The comment `show()` carries about both keys
moves here.

```php
// App\Support\SignInDestination

/**
 * Nothing is waiting any more, or what is waiting belongs to another
 * sign-in: the framework's intended URL and the named destination, together.
 */
public static function forget(): void; // Session::forget([self::KEY, 'url.intended'])
```

```php
// App\Http\Controllers\Auth\MagicLinkLoginController

/** The account this browser last asked for a link to (T-084). */
private const REQUESTED_KEY = 'auth.magic_link.requested';
```

- `store()`: inside `if ($user)`, after `notify()`,
  `$request->session()->put(self::REQUESTED_KEY, (string) $user->getKey())`.
  An address with no account leaves the session as it was. The response is
  unchanged.
- `login()`: after the nonce check and before `markEmailAsVerified()`,

```php
if ($request->session()->pull(self::REQUESTED_KEY) !== (string) $user->getKey()) {
    SignInDestination::forget();
}
```

```php
// App\Http\Controllers\SeriesAccessController::verify()
// directly after SeriesAccessPending::forget():
SignInDestination::forget();
```

```ts
// resources/js/pages/public/Series.vue — defineProps adds
/** Have a password? Sign in instead: stores this page, then sign-in (T-084). */
signInUrl: string;
```

The guest branch's `<Link :href="login()">` becomes `<Link :href="signInUrl">`,
with no `prefetch`, and the `login` import goes.

## Copy

None. The link keeps `accesses.join.have_password`.

## Routes

| Verb | Path                          | Name             | Action                          |
| ---- | ----------------------------- | ---------------- | ------------------------------- |
| GET  | `/s/{group}/{series}/sign-in` | `series.sign-in` | `PublicSeriesController@signIn` |

No middleware, like `series.public`.

## Tests

**New: `tests/Feature/Auth/StaleDestinationTest.php` — 10 cases**

Setup: a published Series `beginner-piano` in a Group `ritas-piano`; a user
with no Group, so a sign-in with nothing stored lands on `route('dashboard')`.
Private helpers `askToSignIn(): void` (GET `series.sign-in` as a guest),
`requestAs(User $user, bool $json = false): Request` as in
`SignInLandingTest`, and `linkRequestedFor(User $user): string` as
`SignInCompositionTest::signedLinkFor()`.

1. `test_a_password_sign_in_after_only_reading_a_series_lands_where_nothing_was_intended`
   — GET `series.public`, POST `login.store`; redirects to `route('dashboard')`.
2. `test_a_password_sign_in_asked_for_from_a_series_returns_there` — ask, POST
   `login.store`; redirects to the Series.
3. `test_a_two_factor_sign_in_asked_for_from_a_series_returns_there` — ask,
   then `TwoFactorLoginResponse::toResponse()`; the target is the Series.
4. `test_a_passkey_sign_in_asked_for_from_a_series_returns_there` — ask, then
   `PasskeyLoginResponse::toResponse()` with JSON; `redirect` is the Series.
5. `test_a_link_asked_for_in_this_browser_returns_to_the_series` — ask, POST
   `magic-link.store`, GET the link; redirects to the Series.
6. `test_a_link_asked_for_elsewhere_forgets_what_this_browser_was_holding` —
   ask, GET `MagicLinkLoginController::urlFor($user)`; redirects to
   `route('dashboard')`, and `url.intended` and `SignInDestination::peek()` are
   both null.
7. `test_a_link_for_another_account_than_the_one_asked_for_forgets_it` — ask,
   POST `magic-link.store` for one account, GET a minted link for another;
   redirects to `route('dashboard')`, both keys null.
8. `test_a_link_asked_for_elsewhere_after_a_protected_page_lands_where_nothing_was_intended`
   — GET `share.dashboard` for a Group the user is not in (redirects to
   `login`), GET a minted link; redirects to `route('dashboard')`.
9. `test_registering_after_only_reading_a_series_does_not_return_there` — GET
   `series.public`, POST `register.store` (`signup_intent` `learn`), then the
   verification link; neither redirect is the Series, and the second is
   `route('dashboard')`.
10. `test_the_code_sign_in_on_a_series_page_leaves_nothing_behind` — ask, then
    `series.access.start` and `series.access.verify` with the faked code;
    signed in, both keys null.

**Changed: `tests/Feature/PublicSeriesTest.php` — 1 changed, 3 new**

- `test_a_guest_is_remembered_for_after_they_sign_in` becomes
  `test_a_guest_is_remembered_when_they_ask_to_sign_in` — GET `series.sign-in`
  redirects to `login`; `url.intended` is the Series and
  `SignInDestination::peek()` is `['url' => …, 'label' => 'Beginner Piano']`.
- `test_a_guest_who_only_reads_is_not_remembered` — new: GET `series.public`;
  the page's `signInUrl` is `route('series.sign-in', …)`, and both keys are null.
- `test_someone_signed_in_who_asks_to_sign_in_is_sent_back_to_the_series` —
  new: redirects to the Series, both keys null.
- `test_asking_to_sign_in_from_an_unpublished_series_is_not_found` — new: a
  draft Series answers 404, both keys null.

**Changed: `tests/Feature/Auth/VerificationDetourTest.php` — 5 changed**

`test_registering_from_a_series_returns_there_after_verifying`,
`test_verifying_after_signing_in_on_another_device_returns_to_the_series`,
`test_the_notice_names_what_is_waiting_when_there_is_a_destination`,
`test_a_destination_is_cleared_once_it_has_been_used` and
`test_someone_already_verified_is_not_sent_through_any_of_this` each read the
Series as a guest to store a destination. Each now asks to sign in from it
(a private `signInUrl(Series $series): string`, GET redirecting to `login`)
and asserts the rest unchanged. Path B's test does not change.

**Must not change:** `SignInCompositionTest::test_the_intended_destination_survives_a_link_sign_in`
(its link is requested in the same session), `SignInLandingTest`,
`MagicLinkRoutesTest`, `SeriesAccessCodeTest`.

## Acceptance

- [x] Reading a Series as a guest stores nothing; **Have a password? Sign in instead.** stores the page and shows sign-in
- [x] After asking from a Series, a password, second-factor, passkey or link sign-in asked for in the same browser returns to it
- [x] A link opened in a browser that did not ask for that account's link lands on that account's landing, with nothing left stored
- [x] The code sign-in on a Series page leaves nothing stored
- [x] In a browser, a Series read as a guest and a Group page bounced to sign-in, each followed by a link from `qori:magic-link` for another account, land on that account's own landing
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Specified on 16 September 2026, when the owner asked for it to be done; that
request is the approval the draft was waiting on. The three questions it
carried were answered the same day. The shape is neither of the draft's two
(Decisions). `regenerate()` is the whole story: `Store::regenerate()` migrates
the id and keeps the attributes, `invalidate()` alone flushes them, and the
magic link, passkey and two-factor controllers each regenerate the same way
Fortify's pipeline does. In a browser, a Series read as a guest and then a
link minted for another account landed on the Series, and a Group page
bounced to sign-in and then a minted link landed on "We couldn't find that
group." The tests are named above.

The estimate moved from S to M: the draft pictured one fix, and the spec is
three small ones with a test for every sign-in path.

The decision is `D-017`, not the `D-016` this spec first named: another
session took `D-017` in the same working tree, for BYO content on the vendor's
site, while this was being built.

The reports that found it: `T-072` (a deleted throwaway user's Group),
`T-062` (the same, on the way to Integrations), `T-075` (a guest visit to a
Series winning over the setup landing).
