---
id: T-115
title: Every error status renders Qori's own page
stream: recovery
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-115 — Every error status renders Qori's own page

## Why

`AppException::render()` shows an error's own message and resolution on a page
load only when `resources/views/errors/{status}.blade.php` exists; otherwise it
aborts, and Laravel shows its bare page with no copy and no way back. `T-113`
found this for its new refusals and added views for 400, 422 and 502. The
statuses `ErrorCode` can still produce with no view — 401, 402 and 504 today —
still reach a person as the bare page in production, where debug is off, and
`docs/architecture/errors.md` says a failed page load carries the public
message. The design review renders only 403, 419, 429, 500 and 503
(`DesignReviewCommand`), so none of the added pages has been looked at either.

Afterwards every status an `AppException` can carry renders Qori's page with
its message, and the design review captures each of them.

## Decisions taken to make this specifiable

Brought to ready on 28 September 2026, from the code.

**An `AppException` on a page load renders Qori's layout whatever its
status.** `errors.layout` takes a status, a message and a resolution and
nothing else (`resources/views/errors/layout.blade.php`); a status view only
supplies the default copy for a status Qori did not throw, and the exception
brings its own. So `AppException::render()` stops checking for a status view
before using the layout, and stops falling through to `abort()` without one:
401, 402 and 504 carry their own words like every other status, and so will
any status `ErrorCode` gains later. Not one view per status: a view for each
would repeat the layout's inputs, and the next status added would be missing
one again.

**Any other status falls back to `errors/4xx` or `errors/5xx`.** Laravel looks
for the status view, then for its range's, before its own bare page
(`Handler::getHttpExceptionView()`). So a status the framework raises and Qori
has no page for — a wrong verb's 405, a body too large's 413 — lands on Qori's
page with generic words. The 4xx page says the request did not go through and
to go back and try again; the 5xx page reuses the 500's words, with no
resolution, for the reason `errors.pages.500` gives. Each shows its own number
as the layout shows every number.

**The design review renders every page there is.** Today it renders 403, 419,
429, 500 and 503; it adds 400, 422 and 502 — `T-113`'s pages, never looked at —
and the two fallbacks. The 404 stays live, as the proof that a rendered view
is the same picture as the error.

## Preconditions

None.

**Data this task verifies against:** a clean database.

**Equipment:** None.

## Scope

**In:**

- `AppException::render()` using the layout for every status.
- `errors/4xx` and `errors/5xx`, and the 4xx copy.
- The design review's error pages, and `ErrorPagesTest`'s lists.

**Out:**

- A JSON or a form post's refusal, which never render a page.
- The words of the existing pages.

## Files

| Path                                           | Change | Notes                                     |
| ---------------------------------------------- | ------ | ----------------------------------------- |
| `app/Exceptions/AppException.php`              | edit   | `render()`: the layout for every status   |
| `resources/views/errors/4xx.blade.php`         | new    | generic copy, the status's own number     |
| `resources/views/errors/5xx.blade.php`         | new    | the 500's copy, the status's own number   |
| `lang/en/errors.php`                           | edit   | `pages.4xx`                               |
| `app/Console/Commands/DesignReviewCommand.php` | edit   | `errorPages()` renders every page         |
| `tests/Feature/ErrorPagesTest.php`             | edit   | 4 cases, and the lists of pages           |
| `docs/architecture/errors.md`                  | edit   | the failed page load, whatever its status |

Flows: none — no call chain changes, only which view a failure renders.

## Database

None.

## Code

```php
// AppException::render(), on a GET with nowhere named to go:
return response()->view('errors.layout', [
    'status' => $this->status(),
    'message' => $this->publicMessage(),
    'resolution' => $this->resolution(),
], $this->status());
```

## Copy

| Key                           | File         | English                         |
| ----------------------------- | ------------ | ------------------------------- |
| `errors.pages.4xx.message`    | `errors.php` | That request didn't go through. |
| `errors.pages.4xx.resolution` | `errors.php` | Go back and try again.          |

The 5xx page uses `errors.pages.500`.

## Routes

None.

## Tests

**Changed: `tests/Feature/ErrorPagesTest.php` — 4 new cases, one rewritten**

1. `test_an_app_exception_with_no_status_view_shows_its_own_words` — a 504
   `upstreamTimeout()` on a page load: the status, its message and its
   resolution, not the framework's page. Replaces
   `test_a_status_with_no_view_still_aborts`, whose premise goes.
2. `test_every_error_code_renders_the_qori_page` — each `ErrorCode`'s status,
   thrown on a page load with debug off.
3. `test_a_framework_4xx_with_no_page_falls_back_to_qoris` — a 405 from a
   route that answers only POST.
4. `test_a_framework_5xx_with_no_page_falls_back_to_qoris` — `abort(504)`.

`test_every_error_page_renders` and
`test_no_error_page_mentions_a_status_code_in_its_prose` walk every page,
the fallbacks included.

## Acceptance

- [x] Every status an `AppException` can carry renders Qori's page with its own message on a page load
- [x] A status the framework raises with no page of its own renders Qori's 4xx or 5xx page
- [x] The design review renders every error page
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~One view per status, or `AppException::render()` falling back to
  `errors.layout`.~~ **Answered from the code, 28 September 2026:** the
  layout, for every status, and `4xx`/`5xx` for the framework's own
  (Decisions).
- ~~Which statuses the design review should capture beyond today's five.~~
  **Answered 28 September 2026:** every page there is (Decisions).

## Re-scope log

None.

## Notes

None.
