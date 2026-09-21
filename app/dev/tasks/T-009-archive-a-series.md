---
id: T-009
title: Archive a Series, with the consequences stated before confirming
stream: recovery
status: done
owner: claude
estimate: M
depends: none
blocks: T-010, T-011
---

# T-009 — Archive a Series, with the consequences stated before confirming

## Why

`Series::STATUS_ARCHIVED` is declared on the model and referenced **nowhere
else in the codebase** — a constant with no behaviour behind it. So a creator
who goes over their plan cap has exactly one way back under it: pay more. The
over-cap notice on the Series index already says "or delete the ones you're no
longer sharing", which is not true, because nothing in the product deletes or
archives anything.

Archiving is the right first half: it takes a Series out of the cap and off the
public page while leaving every Peer who has access still able to open it. That
distinction is the point, and it has to be stated before the creator confirms —
somebody archiving a Series to get under a cap needs to know their paying Peers
are unaffected, and somebody expecting the Series to disappear needs to know it
will not.

## Scope

**In:**

- `SeriesService::archive()` and `::unarchive()`.
- An archive control on the Series page, with a confirmation naming the number
  of Peers who keep access.
- Archived Series excluded from the plan cap and from the public page.
- Archived Series still readable by Peers who already have access.

**Out:**

- Deleting a Series. That is `T-010`, and it has a different promise.
- Archiving a Group. `Group::STATUS_ARCHIVED` has the same problem and is a
  separate decision.
- Bulk archiving.

## Files

| Path                                              | Change | Notes                                                            |
| ------------------------------------------------- | ------ | ---------------------------------------------------------------- |
| `app/Models/Series.php`                           | edit   | `isArchived()`, `scopeArchived()`, exclude from `scopeCounted()` |
| `app/Services/SeriesService.php`                  | edit   | `archive()`, `unarchive()`                                       |
| `app/Http/Controllers/Share/SeriesController.php` | edit   | `archive()`, `unarchive()` actions                               |
| `app/Models/Group.php`                            | edit   | `seriesUsed()` must not count archived                           |
| `routes/share.php`                                | edit   | Two routes                                                       |
| `lang/en/series.php`                              | edit   | 4 keys                                                           |
| `resources/js/pages/share/series/Show.vue`        | edit   | Archive control + confirmation dialog                            |
| `resources/js/pages/share/series/Index.vue`       | edit   | Archived section and status label                                |
| `tests/Feature/Series/ArchiveSeriesTest.php`      | new    | 9 cases                                                          |

## Database

None. `series.status` already holds the value; this task gives it meaning.

Confirm before starting that `Series::STATUS_ARCHIVED === 'archived'` and that
no migration constrains `status` to an enum. If one does, this becomes a
re-scope.

## Code

```php
// App\Models\Series
public function isArchived(): bool;                         // status === STATUS_ARCHIVED
public function scopeArchived(Builder $query): Builder;     // where status = archived
public function scopeUnarchived(Builder $query): Builder;   // where status != archived

// App\Services\SeriesService
/**
 * Take a Series out of circulation without taking it away from anyone.
 *
 * Peers with access keep it — that is the whole difference between this and
 * deletion, and it is why the confirmation has to say so.
 */
public function archive(Series $series): Series;

public function unarchive(Series $series): Series;          // back to STATUS_DRAFT, never straight to published
```

`archive()` sets `status = STATUS_ARCHIVED` and saves. It must **not** touch
`accesses`.

`unarchive()` returns the Series to `STATUS_DRAFT`, never to `published`:
re-publishing is a decision the creator makes deliberately, and restoring a
Series straight to "shared" would put it back on a public page without anybody
choosing that. It must refuse when the Group is at its cap, via the existing
`AppException::planLimitReached` with `errors.series.cap_reached`.

`Group::seriesUsed()` changes to count `unarchived()` only. **Read the current
implementation before editing** — `isOverSeriesCap()` depends on it, and the
over-cap lock is what this task exists to give an exit to.

Controller actions take the series **id**, not the slug (§ route addressing):

```php
public function archive(string $group, string $seriesId, SeriesService $series, Terminology $terminology): RedirectResponse;
public function unarchive(string $group, string $seriesId, SeriesService $series, Terminology $terminology): RedirectResponse;
```

## Copy

| Key                         | File                 | English                                                                                                               |
| --------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `series.archived`           | `lang/en/series.php` | `:title is archived. The :peer_plural who had access keep it.`                                                        |
| `series.unarchived`         | `lang/en/series.php` | `:title is back, as a draft.`                                                                                         |
| `series.archive_confirm`    | `lang/en/series.php` | `{0} Nobody has access to this yet.\|{1} One :peer keeps their access.\|[2,*] :count :peer_plural keep their access.` |
| `errors.series.cap_reached` | `lang/en/errors.php` | message + resolution — check whether this key already exists before adding it                                         |

The confirmation copy is a `trans_choice` line, so it goes through
`Terminology::choice()`, not `__()`.

## Routes

| Verb | Path                                     | Name                     | Action                       |
| ---- | ---------------------------------------- | ------------------------ | ---------------------------- |
| POST | `/g/{group}/series/{seriesId}/archive`   | `share.series.archive`   | `SeriesController@archive`   |
| POST | `/g/{group}/series/{seriesId}/unarchive` | `share.series.unarchive` | `SeriesController@unarchive` |

POST rather than DELETE: nothing is deleted, and `T-010` needs DELETE.

## Tests

**New: `tests/Feature/Series/ArchiveSeriesTest.php` — 9 cases**

1. `test_a_creator_can_archive_a_series` — status becomes `archived`.
2. `test_archiving_leaves_every_access_intact` — an Access row before and after,
   unchanged, still `active()`.
3. `test_an_archived_series_still_opens_for_a_peer_who_has_access` — GET the
   peer's `/shared/{seriesId}` and assert 200.
4. `test_an_archived_series_is_gone_from_the_public_page` — GET the public URL
   and assert the not-found response.
5. `test_an_archived_series_does_not_count_against_the_plan_cap` — free plan at
   1 of 1, archive it, assert a second Series can now be created.
6. `test_archiving_lifts_the_over_cap_lock` — two Series on free (created on a
   paid plan, then downgraded), assert `isOverSeriesCap()` true; archive one;
   assert false.
7. `test_unarchiving_returns_a_series_as_a_draft` — never `published`.
8. `test_unarchiving_is_refused_at_the_cap` — assert the `AppException` and that
   the status stays `archived`.
9. `test_someone_outside_the_group_cannot_archive_it` — group scoping.

**Changed:**

- Any test asserting `seriesUsed()` or `isOverSeriesCap()` — grep for both
  before starting and list what you find here.

## Acceptance

- [x] `Series::STATUS_ARCHIVED` has behaviour behind it
- [x] Archiving takes a Series out of the cap and off the public page
- [x] Every Peer with access keeps it, and a test proves it
- [x] The confirmation names how many Peers keep access, before the click
- [x] Un-archiving returns a draft and is refused at the cap
- [x] Every promise of deletion is now true or reworded. There are **three**,
      and workers have split over which of them are in scope — they all are:
      the over-cap notice and the at-limit copy in
      `resources/js/pages/share/series/Index.vue`, and
      `errors.series.locked_over_cap` in `lang/en/errors.php`
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)

## Re-scope log

None.

## Notes

§7.2 puts refunds in the creator's own Stripe. Nothing in this task implies a
refund, and the confirmation copy does not use the word.

**The plan cap was counted in four places, not one.** The spec named
`Group::seriesUsed()` and warned to read it first; it did not know about the
other three, and changing only the one it named produced a half-working feature
that still refused to create anything:

1. `Group::seriesUsed()` — named in the spec. Now excludes archived.
2. `SeriesService::guardSeriesLimit()` — ran its own query. Now delegates to
   `seriesUsed()`, so the cap has one definition instead of two that can
   disagree. They already did: `isOverSeriesCap()` released the lock while this
   still refused to create anything.
3. `SeriesController::index()` — counted the rows it was about to render, which
   include archived ones, so the page said "1 of 1 used" immediately after
   archiving to get under the cap. **Found in a browser, not by the tests
   above**, and now covered by a test that asserts the prop rather than the
   model.
4. The at-limit copy in the New Series panel, which still offered "delete".

Not re-scoped — no acceptance criterion changed, and the extra work was one file
already claimed plus a line each in two others. But a spec that says "change
this counter" should list every place it is counted, and the next task of this
shape should be written that way.

**A trap for the next person in this controller.** `SetCurrentGroup` replaces
the `{group}` route parameter with the resolved `Group` model, so the argument
bound to `string $group` is not the slug a URL needs — building a redirect from
it throws `UrlGenerationException`. `store()` already worked around this by
reading `CurrentGroup`; the new actions do the same. The spec's signatures were
correct and still walked straight into it.

The cap's lang key is `errors.series.limit_reached`, not `cap_reached` as the
spec guessed. It already existed.

Archiving is deliberately **not** behind `guardSeriesUnlocked`. It is the escape
from that lock, and a guard there would leave upgrading as the only exit —
which is the state this task exists to end. Asserted directly on the service,
because a guard added later would still let every route test pass by way of the
controller redirecting.
