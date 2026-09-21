---
id: T-171
title: The Episode form offers only storage that can be connected
stream: storage
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-171 — The Episode form offers only storage that can be connected

## Why

The Episode form listed Dropbox for File, Video and Audio from a copy of
`EpisodeType::allowedProviders()` kept in `share/series/Show.vue`, and every
save of it is refused: Dropbox is account-bound and no connector is bound for
it, so `EpisodeService::guardProviderConnected()` answers "That storage can't
be connected to Qori yet" (`T-152`). The 21 September 2026 walk met it as the
first-share journey's step-9 branch, "offered, then refused on save".
Afterwards the form offers only what a save can accept, from the server.

## Decisions taken to make this specifiable

- **Offered means allowed, less an account-bound provider with no connector
  bound** — exactly the case `guardProviderConnected()` refuses as "not
  available". A provider that can be connected and is not yet (Google Drive
  before its consent) stays, because the form says how to connect it.
- **The server sends the list; the page keeps no copy.** A second list in the
  page is how Dropbox outlived the rule that refuses it.
- **A kind with nothing left is not offered.** None is empty today — Audio has
  Google Drive since `T-159` — so this changes nothing a creator sees now.

## Preconditions

None.

**Data this task verifies against:** a clean database for the tests; the
design-review world's `harbour-lane-studio` for the walk.

**Equipment:** a browser.

## Scope

**In:**

- `EpisodeService::offeredProviders()`, the `episodeProviders` prop, and the
  form listing it.

**Out:**

- Binding a Dropbox connector, which offers Dropbox again with no change
  here (`T-096`).
- The Episode edit form, which changes an Episode's title and content, not
  where it lives.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Services/EpisodeService.php` | edit | `offeredProviders()` |
| `app/Http/Controllers/Share/SeriesController.php` | edit | `episodeProviders` |
| `resources/js/pages/share/series/Show.vue` | edit | lists it; no copy of the rule |
| `docs/flows/series.md` | edit | the table, current again, and what the form offers |
| `docs/flows/storage.md` | edit | the rule's snippet, current again |
| `docs/tinker/series.md` | edit | `offeredProviders()` |
| `tests/Feature/Share/EpisodeServiceTest.php` | edit | one case |
| `tests/Feature/Share/DriveEpisodeTest.php` | edit | one case |

## Database

None.

## Code

```php
// EpisodeService
/** @return list<EpisodeProvider> */
public function offeredProviders(EpisodeType $type): array;

// SeriesController::show(): 'episodeProviders' => [type value => list of provider values], empty kinds dropped
```

## Copy

None.

## Routes

None.

## Tests

**Changed: 2 new cases**

1. `tests/Feature/Share/EpisodeServiceTest.php` —
   `test_the_form_is_offered_only_storage_that_can_be_connected`
2. `tests/Feature/Share/DriveEpisodeTest.php` —
   `test_the_episode_form_offers_drive_and_never_dropbox`

## Acceptance

- [x] The Episode form offers no Dropbox for any kind, and Audio offers Google Drive
- [x] The list comes from the server; the page holds no copy of the rule
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

The first-share journey's "What to do" named this without a task on 21
September 2026; it became one on 22 September because it changes a page prop
and names a flow doc.
