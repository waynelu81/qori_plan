---
id: T-117
title: Episode writes count what the database holds
stream: operations
status: draft
owner: unassigned
estimate: S
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
  `episodeCount() === 0` (`app/Services/SeriesService.php:157`);
- `EpisodeService::remove()` cannot find the new Episode (`episodeOrFail()`,
  `app/Services/EpisodeService.php:188`) and decides its unpublish from
  `episodeCount() === 1` (`:170`);
- `EpisodeService::reorder()` refuses a payload listing it (`:220`).

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

To be written once the questions below are answered.

## Preconditions

To be written.

## Scope

**In:**

- To be written.

**Out:**

- To be written.

## Files

To be written.

## Database

To be written.

## Code

To be written.

## Copy

None.

## Routes

None.

## Tests

To be written.

## Acceptance

- [ ] To be written
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- The stale reads: count in the database at each site, as `T-047` did, or
  drop the loaded relation after every Episode write so every later read
  reloads. Anyone's.
- The race: lock the Series row (`lockForUpdate()` inside a transaction)
  around the count and insert, or make `(series_id, position)` unique and
  retry. A unique constraint also has to survive `reorder()` and `remove()`,
  which rewrite positions one row at a time. Anyone's.
- Whether the classroom sprint's lesson resources, which will have their own
  order, land first and should share the answer. The owner's.

## Re-scope log

None.

## Notes

None.
