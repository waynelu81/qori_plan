---
id: T-211
title: Removing an Episode says what happened to the Series
stream: onboarding
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-211 — Removing an Episode says what happened to the Series

## Why

`EpisodeController::destroy()` picks its toast from the Series' state after
the removal: `series.episode_removed_unpublished` — ":episode removed. That
was the last one, so the :series went back to draft." — whenever the Series is
a draft (`app/Http/Controllers/Share/EpisodeController.php:112-118`). But
`EpisodeService::remove()` unpublishes only when it removes the last Episode
of a **published** Series. So every removal from a draft — the Series a new
creator is still putting together — says it was the last one and that the
Series went back to draft, however many Episodes are left and though it never
left draft. Seen on 27 September 2026 in `T-210`'s walk, removing the only
Episode of a Series that had never been published.

Afterwards the line says the Series went back to draft only when this removal
put it there.

## Decisions taken to make this specifiable

**What changed is read across the removal, in the controller.** The Series is
read before `remove()` and after it, and the unpublished line is chosen only
when it was published before and is a draft after. `remove()` keeps returning
the Series: a flag or a result object would widen a service signature for one
toast, when the two states are already in the controller's hands.

**No new copy.** Both lines exist and are right; only the choice between them
was wrong.

## Preconditions

None.

**Data this task verifies against:** a clean database.

**Equipment:** None.

## Scope

**In:**

- `EpisodeController::destroy()` chooses the line from the state before and
  after.

**Out:**

- Any other toast, and `remove()` itself.

## Files

| Path                                               | Change | Notes       |
| -------------------------------------------------- | ------ | ----------- |
| `app/Http/Controllers/Share/EpisodeController.php` | edit   | `destroy()` |
| `tests/Feature/Series/EpisodeRoutesTest.php`       | edit   | 4 cases     |

Flows: none — the call chain is unchanged, and no flow names which toast
`destroy()` shows.

## Database

None.

## Code

```php
// EpisodeController::destroy()
$series = $this->seriesById($seriesId);
$wasPublished = $series->isPublished();
$series = $episodeService->remove($series, $episodeId);
// series.episode_removed_unpublished only when $wasPublished && $series->isDraft()
```

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/Series/EpisodeRoutesTest.php` — 4 new cases**

1. `test_removing_one_of_several_episodes_from_a_draft_says_only_that`.
2. `test_removing_the_only_episode_of_a_draft_says_only_that`.
3. `test_removing_one_of_several_episodes_from_a_published_series_says_only_that`
   (Notes).
4. `test_removing_the_last_episode_of_a_published_series_says_it_went_back_to_draft`.

## Acceptance

- [x] The "went back to draft" line appears only when the removal unpublished
      the Series
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

The fourth case was added while building: with only the three first
written, choosing the line on "was published" alone passed them all, because
nothing removed one of several Episodes from a published Series.
