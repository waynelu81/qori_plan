---
id: T-042
title: Episodes are rows, and the code still said otherwise
stream: operations
status: done
owner: claude
estimate: M
depends: none
blocks: none
---

# T-042 — Episodes are rows, and the code still said otherwise

## Why

**Episodes have their own table.** `episodes` has an id, a `series_id` foreign
key with `cascadeOnDelete`, and thirty-eight rows locally. `Series::episodes()`
is a plain `hasMany`. There is no `episodes` column on `series`.

Four places say otherwise, and one of them is load-bearing:

| Where                              | Says                                                                                                           |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `CLAUDE.md` §tenancy               | "Episodes are embedded in the Series row (`episodes` jsonb)"                                                   |
| `Episode.php` docblock             | "embedded inside its series document … it has no connection, no table"                                         |
| `SeriesService::removeEpisode()`   | "Because episodes are embedded, the delete and the renumber are one document write with no half-applied state" |
| `SeriesService::reorderEpisodes()` | "Because episodes are embedded, this rewrites one document — no transaction"                                   |

The last two are not stale prose. They are the **stated reason there is no
transaction**, and there is no `DB::transaction` anywhere in `SeriesService`.

`removeEpisode()` unpublishes the Series if it is the last Episode, deletes a
row, then loops the survivors calling `save()` once each. That is one delete and
N updates with nothing holding them together. A failure partway leaves exactly
the state the comment says it prevents — positions reading "1, 2, 4" — or a
Series unpublished with its Episode gone and the rest half-renumbered.
`reorderEpisodes()` has the same shape and the same comment.

Found on 11 September 2026 while checking a `docs/tinker/` recipe against the
database for `T-041`. The recipe asserted no `episodes` table existed; the
database disagreed.

## Decisions taken to make this specifiable

**The storage is right and the comments are wrong.** A separate table with a
foreign key and a cascade is the ordinary Postgres shape, it is what the
migration creates, and nothing here proposes moving Episodes back into a column.
What changes is the code that assumed otherwise.

**A transaction, not a rewrite.** The renumber loop is fine once it is atomic.
Wrapping is smaller, more reviewable, and does not touch the ordering logic that
five tests already cover.

**`CLAUDE.md` is in scope even though it is normally left alone.** It is the
file every agent reads first, and the sentence is false. `docs/project-plan.md`
§21.4 was corrected in `T-041`; this closes the same claim in the other two
places it lives.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- `DB::transaction()` around the two multi-row writes.
- The four false claims about embedding.
- A test that a failed renumber leaves no hole.

**Out:**

- Moving Episodes into a `jsonb` column. Not proposed and not wanted.
- Other multi-row writes. `AccessService` and `CheckoutService` may have the
  same shape and have not been read; that is a sweep and its own task.
- `docs/project-plan.md` §21.4, already corrected.

## Files

| Path                                        | Change | Notes                               |
| ------------------------------------------- | ------ | ----------------------------------- |
| `app/Services/SeriesService.php`            | edit   | Two transactions, two comments      |
| `app/Models/Episode.php`                    | edit   | The docblock                        |
| `CLAUDE.md`                                 | edit   | One sentence in the tenancy section |
| `tests/Feature/Series/EpisodeOrderTest.php` | new    | 4 cases                             |

**Added during execution.** The spec said four false claims. There were eight,
and the four it did not name were found by grepping rather than by reading the
files it listed. None changes what gets built — see the report:

| Path                                         | Change | Why it was missing                                        |
| -------------------------------------------- | ------ | --------------------------------------------------------- |
| `app/Models/Series.php`                      | edit   | Class docblock, plus a dead `@return EmbedsMany` block    |
| `routes/share.php`                           | edit   | "Episodes live inside their series document"              |
| `database/factories/SeriesFactory.php`       | edit   | "an Episode is only ever a subdocument"                   |
| `tests/Feature/Series/SeriesServiceTest.php` | edit   | A **test named** `test_episodes_are_embedded_and_ordered` |
| `app/Models/Access.php`                      | edit   | One phrase, "the series document"                         |

## Database

None. The schema is already correct; the code's belief about it is not.

## Code

```php
// App\Services\SeriesService::removeEpisode() and ::reorderEpisodes()
return DB::transaction(function () use (...): Series {
    // existing body
});
```

Both comments are replaced with the truth: episodes are rows, the delete and the
renumber are separate statements, and the transaction is what makes them one
unit. Say that the transaction is the guarantee, because the next reader will
otherwise wonder why it is there.

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/Series/EpisodeOrderTest.php` — 4 cases**

1. `test_removing_an_episode_closes_the_gap` — the property the comment claimed.
   Four Episodes, remove the second, assert positions 1, 2, 3.
2. `test_a_failed_renumber_leaves_no_hole` — force a failure inside the
   transaction and assert the original positions survive intact. **This is the
   case that fails today**, because there is no transaction to roll back.
3. `test_reordering_is_all_or_nothing` — the same property on the other method.
4. `test_removing_the_last_episode_of_a_published_series_unpublishes_it_atomically`
   — the unpublish and the delete are one unit, so a failure leaves the Series
   published with its Episode intact rather than in between.

**Changed:** none expected. The five existing ordering assertions in
`EpisodeRoutesTest` cover the happy path and should not move.

## Acceptance

- [x] Both multi-row writes are transactional
- [x] A failure partway leaves the Series exactly as it was
- [x] No comment claims episodes are embedded
- [x] `CLAUDE.md` and `Episode.php` describe the table that exists
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

`QORI-004` in the risk register was rewritten on 11 September to name this. Its
original form was about replica sets and transactions under the previous
database; the topology half resolved itself with the move to Postgres and the
assumption half did not.

Worth noticing how this survived: the comments were true when written, the
migration that made them false was correct, and no test asserts atomicity —
because atomicity was free and nobody writes a test for free things. The
storage changed underneath a comment nobody had reason to re-read.
