---
id: T-002
title: Error pages in Qori's own palette
stream: design
status: done
owner: claude
estimate: S
depends: none
blocks: T-003
---

# T-002 — Error pages in Qori's own palette

## Why

The 404 is Laravel's own bare white error view. It is the one surface in the
product that has never seen a Qori token, and it is reached by exactly the
people least able to tolerate it: somebody following a stale Series link, or a
Peer whose access was revoked. Found during redesign Day 2 and recorded in
`../walkthroughs.md`.

It also has no way out. A dead end with no link back is the failure the whole
recovery stream exists to prevent, and this is the cheapest instance of it.

## Scope

**In:**

- 404, 403, 419, 429, 500 and 503 in the paper/gold palette.
- One sentence per status saying what happened, and a way onward.

**Out:**

- Anything `AppException` renders. It already produces its own page with a
  message and a resolution (§23) — this is the _framework's_ fallback, for
  statuses Qori did not throw.
- A branded maintenance-mode page beyond 503.

## Files

| Path                                      | Change | Notes                           |
| ----------------------------------------- | ------ | ------------------------------- |
| `resources/views/errors/404.blade.php`    | new    |                                 |
| `resources/views/errors/403.blade.php`    | new    |                                 |
| `resources/views/errors/419.blade.php`    | new    |                                 |
| `resources/views/errors/429.blade.php`    | new    |                                 |
| `resources/views/errors/500.blade.php`    | new    |                                 |
| `resources/views/errors/503.blade.php`    | new    |                                 |
| `resources/views/errors/layout.blade.php` | new    | The shared frame all six extend |
| `lang/en/errors.php`                      | edit   | 6 entries under `pages`         |
| `tests/Feature/ErrorPagesTest.php`        | new    | 7 cases                         |

## Database

None.

## Code

Blade, not Inertia. An Inertia error page needs the app to boot far enough to
render a Vue root, and the case that matters most — a 500 — is the case where
that assumption is least safe. Blade renders from the framework alone.

`layout.blade.php` inlines its own CSS rather than pulling the Vite bundle, for
the same reason: a 500 caused by a build problem must not depend on the build.
Copy the token values from `resources/css/app.css` and **say in a comment that
they are duplicated and why**, so the next person to change the palette knows
this file exists.

Include the light and dark values, matched to `prefers-color-scheme`, and the
same `<style>` pre-paint background trick `resources/views/app.blade.php` uses.

Each page: the Qori mark on the gold tile, the status number, one sentence, and
one link — `/` for a signed-out visitor, `/dashboard` otherwise. `auth()->check()`
is available in Blade.

**Message and resolution (added by re-scope).** `layout.blade.php` takes two
optional view variables and falls back to the lang line for the status:

```blade
@php
    $message ??= __("errors.pages.{$status}.message");
    $resolution ??= __("errors.pages.{$status}.resolution");
@endphp
```

`AppException::render()` stops calling `abort()` for a failed GET and renders
the view itself, so the message and the resolution both survive:

```php
if ($request->isMethod('GET') && $this->redirectTo === null) {
    return response()->view('errors.'.$this->status(), [
        'status' => $this->status(),
        'message' => $this->publicMessage(),
        'resolution' => $this->resolution(),
        'exception' => $this,
    ], $this->status());
}
```

Its return type widens to include `Response`. Where no view exists for the
status, fall back to `abort()` — `ErrorCode` can produce statuses these six
files do not cover, and a missing view must not become a 500.

## Copy

| Key                | File                 | English                                                                                                                  |
| ------------------ | -------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `errors.pages.404` | `lang/en/errors.php` | message: `That page isn't here.` resolution: `The link may be old, or the thing it pointed at may have been taken down.` |
| `errors.pages.403` | `lang/en/errors.php` | message: `You don't have access to that.` resolution: `If you think you should, ask whoever shared it with you.`         |
| `errors.pages.419` | `lang/en/errors.php` | message: `That page had been sitting too long.` resolution: `Go back and try again — nothing was lost.`                  |
| `errors.pages.429` | `lang/en/errors.php` | message: `Too many tries, too quickly.` resolution: `Wait a minute and try again.`                                       |
| `errors.pages.500` | `lang/en/errors.php` | message: `Something went wrong on our side.` resolution: **omit**                                                        |
| `errors.pages.503` | `lang/en/errors.php` | message: `Qori is down for a moment.` resolution: `It should be back shortly.`                                           |

500 has no resolution deliberately. §23: omitting it means the path is final,
and inventing a hopeful suggestion for a dead end is the thing that rule
forbids. Do not write "try again later" — the reader has no way to know whether
that will help.

No status codes and no vendor names in the visible copy. The number is a visual
element, not the explanation.

## Routes

None.

## Tests

**New: `tests/Feature/ErrorPagesTest.php` — 7 cases**

1. `test_an_unknown_url_renders_the_qori_404` — assert 404 and the copy, not the
   Laravel default.
2. `test_the_404_offers_a_signed_out_visitor_the_way_home` — asserts `href="/"`.
3. `test_the_404_offers_a_signed_in_person_their_dashboard`.
4. `test_a_403_renders_the_qori_page` — `abort(403)` on a temporary test route.
5. `test_a_500_states_no_resolution` — the deliberate omission, asserted so
   somebody helpfully adding one has to argue with a test. Needs
   `withoutExceptionHandling()` disabled and `APP_DEBUG=false`.
6. `test_every_error_page_renders` — loop the six, assert each returns its
   status and contains its message.
7. `test_no_error_page_mentions_a_status_code_in_its_prose` — assert the lang
   strings contain no digits.

Added by re-scope:

8. `test_an_app_exception_shows_its_own_message` — GET a public Series URL that
   does not exist; assert "That series is no longer available", not "Not Found".
   **This fails before the change, which is the point.**
9. `test_an_app_exception_shows_its_resolution` — one with a resolution set.
10. `test_a_status_with_no_view_still_aborts` — an `AppException` whose status
    has no Blade file returns that status rather than a 500.

## Acceptance

- [x] All six render in the paper/gold palette, light and dark
- [x] Every page offers a way onward
- [x] 500 states no resolution, and a test holds that line
- [x] Nothing on these pages depends on the Vite build
- [x] The duplicated palette values carry a comment saying where they come from
- [x] An `AppException` on a GET shows its own §23 message and resolution
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)

## Re-scope log

**9 September 2026 — the "Out" section rested on a false premise.**

Expected, per the spec: `AppException` renders its own page with a message and
a resolution, so these six files are only the framework's fallback for statuses
Qori did not throw.

Found: `AppException::render()` calls `abort($status, $message)` for a failed
GET, and Laravel's own `errors::404` view is three lines that hardcode
`__('Not Found')` — it never reads `$exception->getMessage()`. Verified against
the running app: `/s/nadias-group/does-not-exist` throws
`errors.access.series_unavailable` ("That series is no longer available") and
renders **"Not Found"**. Every §23 message written for a page load is thrown
away today, and the resolution never leaves the exception at all.

Why this is a re-scope and not a note: building to the spec would have shipped
six pages that still discard that copy, and the section saying not to worry
about it would have stayed wrong. It changes what is built.

Why it was widened rather than split: the fix lives in the same view this task
creates, so a separate task would open the same files a second time, and the
six new pages would ship knowingly worse in between. Cost is roughly ten lines
in `AppException::render()` and three tests.

Re-scoped and set back to `doing` by the same person executing it, which is only
acceptable because the planner and the developer are the same person here. With
two people this goes back to the board.

## Notes

`bootstrap/app.php` registers no renderer for any of these statuses and there was
no `resources/views/errors/` directory — checked before starting, as the original
note asked.

**The layout does not fall back to lang for a missing resolution, and the design
changed during the build to make that possible.** The first version used
`$resolution ??= __("errors.pages.{$status}.resolution")`, which had two faults:
`__()` returns the _key_ when a line is missing, so the 500 page rendered the
literal string `errors.pages.500.resolution`; and an unset variable is
indistinguishable from one explicitly set to null, so an `AppException` that
deliberately withheld a resolution would have had the generic line put back
underneath it — the exact §23 violation this task was meant to respect. The
layout is now a pure renderer taking `$status`, `$message` and `$resolution`;
the six status views name their own copy, so "no resolution" is visible in
`500.blade.php` rather than implied. `AppException::render()` renders
`errors.layout` directly for the same reason.

**Found, not fixed — belongs to `T-011`.** `AppException::resolution()` falls
back to the ErrorCode's generic resolution when the specific lang key omits one.
So `errors.access.series_unavailable`, whose lang file carries the comment
"Final: the series cannot be reached at all, so there is nothing to retry",
renders "Check the link, or go back and try again." The omission that §23 calls
deliberate is undone by a fallback one level up. Not re-scoped into this task:
`resolution()` also feeds the JSON payload and every toast, so changing it is a
wider behavioural change than error pages, and it was invisible before this task
made resolutions visible on page loads. Added to `T-011`.
