---
id: T-047
title: An Episode's position and the episode cap both read a stale count
stream: operations
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-047 — An Episode's position and the episode cap both read a stale count

## Why

`EpisodeService::add()` sets `'position' => $series->episodeCount() + 1`,
and `episodeCount()` returns `$this->episodes->count()` — the **loaded relation**,
which Eloquent caches on the instance after the first access. Adding a second
Episode through the same `$series` object reads the count from before the first
one existed, so both land on position 1.

`guardEpisodeLimit()` reads the same cached count, so the plan's
episodes-per-series cap has the identical blind spot: a caller in that shape can
pass a cap it has already reached.

**No production path hits it today**, which is the whole problem with it. Every
HTTP caller resolves the Series once per request and adds one Episode, so the
cache is never stale by the time it is read. It cost `T-042` a wrong test
fixture, it will cost the next person the same, and the first code that adds two
Episodes in one request turns it from a latent bug into duplicated positions in
the database. `T-026`'s guided first-Series flow is exactly that code.

Found on 11 September 2026 while writing `EpisodeOrderTest`, whose four-Episode
fixture came out as four Episodes all at position 1.

## Decisions taken to make this specifiable

**Count in the database, not in memory.** `$series->episodes()->count()` issues a
`SELECT count(*)` against the relation rather than reading a cached collection,
so it is correct whatever the caller has loaded. One query per add, on a path
that is already writing a row.

**`episodeCount()` itself is left alone.** It is read by five surfaces to render
a number beside a Series, and those callers have the relation loaded on purpose
— making it query every time would turn a Series list into N queries. What is
wrong is using a display count to compute a write.

**Both call sites, not just the position one.** The cap guard has the same bug
and a smaller blast radius, which is exactly the sort that gets left behind.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The position calculation and the cap check in `EpisodeService::add()`.
- A test that adding two Episodes through one loaded Series gives 1 and 2.

**Out:**

- `episodeCount()`'s own behaviour, and its display callers.
- Any other service reading a cached relation to compute a write.
  `AccessService` and `CampaignService` have not been read for this shape; that
  is a sweep and its own task.
- Making `add()` transactional. It writes one row.

## Files

| Path                                        | Change | Notes                               |
| ------------------------------------------- | ------ | ----------------------------------- |
| `app/Services/EpisodeService.php`           | edit   | Two reads, one method               |
| `tests/Feature/Series/EpisodeOrderTest.php` | edit   | 2 cases, and the fixture simplifies |

Flows: none — the call chain is unchanged; two reads of a cached relation
become one count query inside the same method.

## Database

None.

## Code

```php
// App\Services\EpisodeService::add() and ::guardEpisodeLimit()
$existing = $series->episodes()->count();
```

Not `$series->episodeCount()`. The comment at each site should say why, because
the two look interchangeable and one of them is a display helper.

`EpisodeOrderTest::seriesWithEpisodes()` currently refreshes the Series between
each add, with a comment explaining that it is working around this. Delete the
refresh and the comment; if the test still passes, the bug is gone.

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/Series/EpisodeOrderTest.php` — 2 new cases**

1. `test_two_episodes_added_through_one_instance_get_different_positions` —
   the defect, asserted directly. **Fails today**, giving 1 and 1.
2. `test_the_episode_cap_counts_episodes_added_through_one_instance` — a Group
   whose plan allows two, three adds through one instance, and the third is
   refused. **Fails today**: all three are allowed.

The existing four cases must keep passing with the fixture's refresh removed.
That is the regression proof.

## Acceptance

- [x] Adding two Episodes through one loaded Series gives positions 1 and 2
- [x] The episodes-per-series cap refuses correctly in the same shape
- [x] `EpisodeOrderTest`'s fixture no longer refreshes between adds
- [x] `episodeCount()` is unchanged, and its display callers are untouched
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

Worth noticing how this survived: the correct-looking call is the wrong one, the
wrong one is shorter, and every existing test adds Episodes one per request the
way the application does. Nothing was careless. The bug is only reachable from a
caller that does not exist yet.

Wording defects found while building it (17 September 2026), none of which
changed what was built: the cap check is its own private method, so an add runs
two count queries when a plan sets a cap and one otherwise, not "one query per
add"; no plan sets `episodes_per_series`, so test 2 sets
`qori.plans.start.episodes_per_series` to 2 itself; the fixture's comment said
the reload "mirrors production rather than working around it"; and only two of
the four existing cases fail without the fix. The stale reads beside it and the
race between two adds are draft `T-117`.

`T-083` (14 September 2026) moved `SeriesService::addEpisode()` and `guardEpisodeLimit()` to `App\Services\EpisodeService` as `add()`; the names above were updated to match. Nothing about the defect changed.
