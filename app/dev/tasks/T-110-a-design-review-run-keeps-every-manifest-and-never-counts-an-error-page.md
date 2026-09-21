---
id: T-110
title: A design-review run keeps every manifest and never counts an error page
stream: design
status: draft
owner: unassigned
estimate: M
depends: none
blocks: none
---

# T-110 — A design-review run keeps every manifest and never counts an error page

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 17 September 2026 from
> [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md)'s
> Notes on capture reliability, which carry no finding number.

## Why

R-004's first full capture ran past the 900-second limit in
`app/Console/Commands/DesignReviewCommand.php:568` and left images with no
`run.json` or contact sheet, which `scripts/design-review/capture.mjs` writes
only after the last screen. The light and dark batches after it both started at
03:37, and the command names a run to the minute (line 151), so both wrote into
`2026-09-16-0337-6d0c761-dirty`; the dark manifest replaced the light one.

Both batches counted `270-integrations` and `710-restricted-integrations` as
captured though each rendered a 502 page, since the script checks only the path
it landed on. `730-new-series-validation` failed: the command signs it in as
Rita and asks for Fern's Fresh Start (line 493). Moving it to Fern is not
enough — Title is `required` in `resources/js/pages/share/series/Index.vue:252`,
so an empty submit stops at a browser bubble no screenshot shows.

Afterwards each invocation keeps its own manifest, a run keeps what it finished,
a screen counts only at the status it expects, and `730` shows Qori's error.

## Decisions taken to make this specifiable

- **One invocation, one directory nobody else can have**: `Y-m-d-His-<commit>`,
  then `-2`, `-3`, each claimed by `File::makeDirectory()` with `$force`, whose
  `false` is the collision — seconds alone collide when one shell line starts
  two batches. Batches stay separate runs.
- **The manifest is `<run>/run.json`, rewritten with `index.html` after every
  screen**, `completedAt` null until the end. The command's shared
  `storage/app/design-review/run.json` (line 127) is no longer written.
- **No total timeout; a 300-second idle timeout** (number provisional): screens
  keep lengthening runs, and a hang is silence; a timeout names the partial run.
- **A screen counts only at the status it expects**: 200, or its own
  `expectStatus` (404 for `100-not-found`), from the last main-frame document
  or `X-Inertia` response before the shot. `AppException::render()` answers a
  page load at its own status, so a 502 cannot pass. The image is kept; the
  file-rendered `9403`–`9503` screens are exempt.
- **`730` signs in as `owner-empty` and fills Title with three spaces**
  (provisional): the browser's `required` accepts them, and `TrimStrings`
  empties them for `StoreSeriesRequest` to refuse with the error Qori renders.
- **`contexts()` and `screens()` become public, filtered in `handle()`**
  (provisional), so a test reads the browser's manifest.

## Preconditions

**Data this task verifies against:** `DesignReviewSeeder`, seeded by the
command and by each new test case.

**Equipment:** for the run-based lines, the app at `--url`, headless Chromium,
over fifteen minutes for a full run, and a screen answering an error, as
Integrations did on 16 September — or the report says how the rule was shown.

## Scope

**In:**

- Per-invocation run directories and manifests, and an idle timeout.
- `status` per result and `expectStatus` per screen; a mismatch is a failure.
- `730` in Fern's context, reaching server validation; three tests; the recipe.

**Out:**

- The 502 itself, recorded on `T-044` against `IntegrationsController::show`.
- `720-register-validation`, an `expect` step and a component check (below);
  failing redirected screens; merging batches into one run.
- R-004's coverage recommendations, its F-1 to F-13, and `T-104` to `T-109`.

## Files

| Path                                           | Change | Notes                                                    |
| ---------------------------------------------- | ------ | -------------------------------------------------------- |
| `app/Console/Commands/DesignReviewCommand.php` | edit   | Directory, manifest, `expectStatus`, idle timeout, `730` |
| `scripts/design-review/capture.mjs`            | edit   | `status`, a write after every screen, incomplete marker  |
| `tests/Feature/DesignReviewFixtureTest.php`    | edit   | 3 new cases                                              |
| `docs/tinker/design-review.md`                 | edit   | Manifest location, incomplete runs, the status rule      |

## Database

None.

## Code

```php
// App\Console\Commands\DesignReviewCommand; use Carbon\CarbonInterface;
private const CAPTURE_IDLE_TIMEOUT_SECONDS = 300; // Process timeout: null
public function claimRunDirectory(string $parent, CarbonInterface $at, string $commit): string;
public function contexts(): array; // list<array<string, mixed>>
public function screens(): array;  // unfiltered; URL screens carry expectStatus

['730-new-series-validation', 'owner-empty', route('share.series.index', [$empty], absolute: false), [
    ['fill' => '#title', 'value' => '   '],
    ['click' => '#new-series button[type="submit"]'],
]],
```

`runLabel()` goes; `handle()` catches `ProcessTimedOutException`. In
`capture.mjs` results gain `status`; `writeRun(completedAt)` rewrites both files.

## Copy

None: console output and the contact sheet are developer diagnostics.

## Routes

None.

## Tests

No command test exists, and `capture.mjs` has no runner; a run proves its half.

**Changed: `tests/Feature/DesignReviewFixtureTest.php` — 3 new cases**

1. `test_it_gives_two_runs_started_in_the_same_second_their_own_directories` —
   a second claim at the same instant ends `-2`.
2. `test_every_signed_in_screen_opens_for_the_identity_it_signs_in_as` — no
   magic-link or guest screen answers an unexpected 403, 404 or 5xx; `730`
   does today.
3. `test_the_new_series_validation_screen_reaches_server_validation` — Fern
   posting a three-space title to `share.series.store` gets a `title` error.

## Acceptance

- [ ] Two invocations in the same second keep two manifests and contact sheets
- [ ] A full run finishes however long it takes; a stopped one keeps its screens
- [ ] A screen answering a status it does not expect, such as R-004's 502,
      fails and the command exits non-zero; `100-not-found` still counts
- [ ] `730-new-series-validation` photographs Qori's title error, as Fern
- [ ] The recipe describes the manifest, incomplete runs and the status rule
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Status alone, or the Inertia page component too, at the cost of an expected
  component per screen? — the stream owner's.
- `720-register-validation` submits inputs all `required` in
  `resources/js/pages/auth/Register.vue`, so likely shows an untouched form; fix
  it here with an `expect` selector, or in a draft? — the stream owner's.
- Three spaces for `730`, or 256 characters? — the stream owner's.
- Public `contexts()` and `screens()`, or a manifest class? — anyone's.
- 300 idle seconds and the `X-Inertia` status rule, against a full run — anyone's.

## Re-scope log

None.

## Notes

- `T-066` moved `600`–`695` to their worlds' owners; `730`, outside, was missed.
- Not in scope: the contact sheet's lane badge is always empty, because
  `contactSheet()` reads `row.lane` and no result row carries one.
