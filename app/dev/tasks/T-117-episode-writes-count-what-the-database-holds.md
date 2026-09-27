---
id: T-117
title: Episode writes count what the database holds
stream: operations
status: done
owner: claude
estimate: M
depends: none
blocks: none
---

# T-117 — Episode writes count what the database holds

## Why

`T-047` made `EpisodeService::add()` count a Series' Episodes in the database,
so several adds through one Series get positions 1, 2, 3. Its review found the
same stale read in the writes beside it. When the caller loaded the Series'
Episodes before an add, the same instance still misses the new Episode
afterwards:

- `SeriesService::publish()` refuses with `errors.series.no_episodes`, because
  `episodeCount() === 0` (`app/Services/SeriesService.php:160`);
- `EpisodeService::remove()` cannot find the new Episode (`episodeOrFail()`,
  `app/Services/EpisodeService.php:368`, which `update()` shares) and decides
  its unpublish from `episodeCount() === 1` (`:343`);
- `EpisodeService::reorder()` refuses a payload listing it (`:402`).

A reviewer confirmed each with a throwaway test on 17 September 2026:
`->load('episodes')`, then `add()`, then the call. No request does this today;
a flow that shows a Series' Episodes and then adds and publishes in one request
would.

`add()` also counts, counts again for the cap, and then inserts with no lock,
and `(series_id, position)` is a plain index, not unique
(`database/migrations/2026_09_08_000000_create_qori_schema.php:117`). Two adds
to one Series at the same moment, such as a double-submitted form, can take the
same position or both pass the cap.

Afterwards every Episode write decides from what the database holds, and two
adds at once cannot share a position.

## Decisions taken to make this specifiable

Brought to ready on 28 September 2026, from the code.

**Each decision reads the database where it is made, as `T-047` did.**
`publish()` counts with `$series->episodes()->count()`; `episodeOrFail()`,
which `update()` and `remove()` share, finds the Episode with
`$series->episodes()->whereKey()`; `remove()` decides its unpublish from the
same count; `reorder()` reads the ids, and each Episode it moves, from the
query. Not dropping the loaded relation after each write instead: the stale
instance is the caller's, and a write through any other instance would leave
it stale again.

**Two writes to one Series' positions are taken one at a time, under the
Series row's lock.** `add()`, `remove()` and `reorder()` read the Series row
`lockForUpdate()` inside their transaction — through `forGroup()`, since a
command or a test may call them with no current Group — and count, check the
cap and write positions under it; `add()` gains the transaction it lacks, and
`reorder()` moves its payload check inside, so the ids it checks are the ids
it writes. Not a unique `(series_id, position)`: `reorder()` and `remove()`
renumber one row at a time, which a plain unique constraint refuses halfway,
and a deferred one would turn a double-submitted form into a 500 where the
lock turns it into a short wait.

**Materials share the answer.** The classroom's lesson resources landed first,
as `T-130`'s materials, with their own order per Episode and per Series: so
`MaterialService::add()` counts its position and checks its cap under the same
Series lock, and `remove()` renumbers under it. One lock per Series for both
kinds of position, since what races is a creator's double submit, and it
touches one Series.

## Preconditions

None.

**Data this task verifies against:** a clean database.

**Equipment:** None.

## Scope

**In:**

- The stale reads in `publish()`, `update()`, `remove()` and `reorder()`.
- The Series lock around `EpisodeService::add()`, `remove()` and `reorder()`,
  and `MaterialService::add()` and `remove()`.

**Out:**

- Reordering materials: `T-137`.
- Any other write that does not number positions.

## Files

| Path                                                        | Change | Notes                                          |
| ----------------------------------------------------------- | ------ | ---------------------------------------------- |
| `app/Services/EpisodeService.php`                           | edit   | reads from the query; the lock in three writes |
| `app/Services/SeriesService.php`                            | edit   | `publish()` counts in the database             |
| `app/Services/MaterialService.php`                          | edit   | the lock in `add()` and `remove()`             |
| `app/Concerns/LocksSeriesPositions.php`                     | new    | `lockSeriesRow()`, shared by both services     |
| `tests/Feature/Series/EpisodeWritesReadTheDatabaseTest.php` | new    | 7 cases                                        |

Flows: `docs/flows/series.md` names `EpisodeService`'s writes and not how they
count, so nothing there changes; the lock is recorded in the services'
docblocks.

## Database

None.

## Code

```php
namespace App\Concerns;

trait LocksSeriesPositions
{
    /** The Series row, locked FOR UPDATE until the surrounding transaction ends; read through forGroup(). */
    private function lockSeriesRow(Series $series): void;
}
```

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/Series/EpisodeWritesReadTheDatabaseTest.php` — 7 cases**

Each of the first four loads a Series' Episodes, adds one through the same
instance, and then makes the call the review made on 17 September 2026:

1. `test_publishing_after_an_add_through_a_loaded_series_succeeds`.
2. `test_removing_an_episode_added_through_a_loaded_series_finds_it`.
3. `test_the_unpublish_is_decided_from_the_database` — a published Series
   keeps its status when one of two Episodes goes.
4. `test_reorder_takes_an_episode_added_through_a_loaded_series`.

The last three record the SQL, as `AdvisoryLockTest` does:

5. `test_an_add_counts_and_inserts_under_the_series_lock` — the `FOR UPDATE`
   read of the Series comes before the count and the insert, in one
   transaction.
6. `test_remove_and_reorder_write_positions_under_the_lock`.
7. `test_a_material_is_numbered_and_renumbered_under_the_same_lock` (Notes).

**Changed:** none expected. Confirm rather than assume.

## Acceptance

- [x] Every Episode write decides from what the database holds
- [x] Two writes to one Series' positions cannot interleave, Episodes or materials
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~The stale reads: count in the database at each site, or drop the loaded
  relation after every Episode write.~~ **Answered from the code, 28 September
  2026:** at each site (Decisions).
- ~~The race: lock the Series row, or make `(series_id, position)` unique and
  retry.~~ **Answered 28 September 2026:** the lock (Decisions).
- ~~Whether the classroom sprint's lesson resources land first and should
  share the answer — the owner's.~~ **Answered from the code, 28 September
  2026:** they landed first, as `T-130`'s materials, and share it
  (Decisions).

## Re-scope log

None.

## Notes

Written while building, 28 September 2026:

- The seventh case covers a material's `remove()` as well as its `add()`, and
  is named for both; the fifth sets an Episode cap in config, because no plan
  sets one yet (§17.4) and without one the cap's count never runs.
- A material's upload is checked under the lock too, not only its cap and
  position: a double submit could otherwise attach one file to two materials,
  which `assetOrFail()` refuses only when the first has already committed.
- `lockSeriesRow()` refuses to run outside a transaction, where the lock would
  end with its own statement. Nothing reaches that today; it guards the next
  caller.
