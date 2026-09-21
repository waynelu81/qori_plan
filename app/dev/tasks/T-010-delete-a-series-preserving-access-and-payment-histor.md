---
id: T-010
title: Delete a Series on a seven-day timer
stream: recovery
status: done
owner: cursor
estimate: L
depends: T-009
blocks: T-011
---

# T-010 — Delete a Series on a seven-day timer

## Why

Archiving (`T-009`) takes a Series out of circulation and keeps everything.
There is no way to actually remove one, so a creator who made something by
mistake, or who no longer wants their work on Qori's storage, has no exit at
all.

Deletion here is deliberately slow. The creator asks; the Series is marked; a
scheduled job removes its resources once seven days are up. Nothing is
destroyed on the click, and the week is long enough to change your mind and
short enough that it does not become storage nobody meant to keep.

**What survives is what belongs to the Peer** — their payment record, their
access, and their certificate. **What goes is what belongs to the creator** —
the Episodes and the files behind them. That division is the whole design, and
every decision below follows from it.

## Decisions taken to make this specifiable

**Every Series can be deleted, including one somebody paid for.** This reverses
the earlier "a Series with paid access can never be hard-deleted", which was
recorded and then revised before it was built. The concern was never that
deletion is wrong; it was that somebody paid. Keeping the payment record and
the certificate answers that directly, and does it better than a rule that
would have left some Series undeletable forever.

**The Series row survives as a tombstone.** This is the important consequence
and it is not optional: `accesses.series_id` is `cascadeOnDelete`, so deleting
the row would take with it every access, every `price_cents`, every
`payment_reference` and every `certificate_code` — precisely the records the
decision says must stay. So the row remains, carrying its title and the fact
that it existed, and what is deleted is its **resources**.

A Peer opening a deleted Series therefore gets a page that says what happened,
not a 404. Their certificate still verifies, because §12's promise is about
what somebody did and that remains true after the material is gone.

**The Series keeps its Group, and a status says it is purged.**

An earlier draft of this spec nulled `series.group_id` to make the Series
"belong to nobody", then added a second column to remember what the first had
thrown away. A column whose only job is to undo another change is a smell, and
the simpler reading is the right one: a Series belongs to a Group, a Group has
an owner, and that link should not be cut.

"No longer belongs to the creator" is four things, and every one is reachable
without touching the relationship:

1. gone from their Series list,
2. not counted against the plan cap,
3. not editable, publishable or shareable,
4. not publicly reachable.

`T-009` already built the machinery — `Series::scopeUnarchived()` and
`Group::seriesUsed()` as the one definition of the cap. A purged Series joins
archived ones in being excluded, which is one line in one place rather than a
nullable relation across fifteen call sites, and it leaves
`App\Admin\Queries\CreatorDirectory` working untouched.

The one thing the null would have bought is survival of a future Group
deletion. Nothing deletes a Group today, and when something does it will face a
larger version of the same problem — `accesses.series_id` cascades too, so a
Peer's paid access already dies with a deleted Group. That hole is real and it
is a different task's to close.

**Requesting deletion does not unpublish.** The creator's call: they may
unpublish first or leave it live for the week, and both are legitimate — a
Series being taken down is exactly when its Peers might want a last look.
Instead, every surface showing it carries a countdown: this Series and
everything in it goes on {date}. The public page carries it too, because
somebody about to get access deserves to know it is about to disappear.

**A scheduled command, not a queued job.** `QUEUE_CONNECTION` is `deferred`,
which runs work in the same process after a successful response and cannot
retry — and nothing may be marked `ShouldQueue` until a real worker exists
(`T-018`). A command run by the scheduler needs neither, and the work is a
sweep rather than a per-request task.

## Preconditions

- The scheduler must actually be running in production. `routes/console.php` is
  empty and nothing is scheduled today, so **this task adds the first scheduled
  command Qori has**. Confirm before shipping that `php artisan schedule:run`
  is on a cron on Laravel Cloud; without it the sweep never runs and Series sit
  marked forever, which fails quietly and looks like nothing.
- R2 credentials for a real deletion smoke test, or a local disk equivalent.

## Scope

**In:**

- Requesting deletion, and cancelling it during the seven days.
- A scheduled command that sweeps expired requests.
- Deleting Episodes and their stored files.
- Keeping access, payment and certificate records intact.
- What a Peer sees when they open a Series whose resources are gone.

**Out:**

- Deleting a Group. Same shape, different blast radius, its own task.
- Deleting a single Episode. That already exists.
- Purging `media_assets` that no Episode references — a separate sweep, and
  the R2 lifecycle rule already covers `incomingUploads`.
- Making the retention period configurable. Seven days, in one constant.

## Files

| Path                                                                   | Change | Notes                                                    |
| ---------------------------------------------------------------------- | ------ | -------------------------------------------------------- |
| `database/migrations/YYYY_MM_DD_HHMMSS_add_delete_after_to_series.php` | new    | One column                                               |
| `app/Models/Series.php`                                                | edit   | `isPendingDeletion()`, `isDeleted()`, `scopeDeletable()` |
| `app/Services/SeriesService.php`                                       | edit   | `requestDeletion()`, `cancelDeletion()`, `purge()`       |
| `app/Console/Commands/PurgeSeriesCommand.php`                          | new    | `qori:series:purge`                                      |
| `routes/console.php`                                                   | edit   | Schedule it daily                                        |
| `app/Http/Controllers/Share/SeriesController.php`                      | edit   | Two actions                                              |
| `routes/share.php`                                                     | edit   | Two routes                                               |
| `lang/en/series.php`                                                   | edit   | 3 keys                                                   |
| `lang/en/errors.php`                                                   | edit   | 1 key                                                    |
| `resources/js/pages/share/series/Show.vue`                             | edit   | Request and cancel, in the panel `T-009` added           |
| `resources/js/pages/share/series/Index.vue`                            | edit   | A pending-deletion row state                             |
| `resources/js/pages/shared/Show.vue`                                   | edit   | What a Peer sees afterwards                              |
| `tests/Feature/Series/DeleteSeriesTest.php`                            | new    | 12 cases                                                 |

## Database

| Table    | Column         | Type        | Null | Default | Index / constraint |
| -------- | -------------- | ----------- | ---- | ------- | ------------------ |
| `series` | `delete_after` | `timestamp` | yes  | null    | index              |
| `series` | `purged_at`    | `timestamp` | yes  | null    | —                  |

`delete_after` is when the sweep may act; `purged_at` records that it did.
Two columns rather than one status, because "asked to be deleted" and "its
resources are gone" are different facts and a Series is briefly both.

Do **not** add `deleted_at` or reach for `SoftDeletes`. Laravel's soft delete
hides the row from every query, and this row has to stay visible: a Peer's
access points at it.

Migration: `database/migrations/2026_09_XX_000000_add_delete_after_to_series.php`

## Code

```php
// App\Models\Series
public function isPendingDeletion(): bool;   // delete_after !== null && purged_at === null
public function isPurged(): bool;            // purged_at !== null

/** Past its TTL and not yet swept. @param Builder<Series> $query */
public function scopeDeletable(Builder $query): Builder;

// App\Services\SeriesService
public const DELETE_AFTER_DAYS = 7;

/** Marks it. Deletes nothing. */
public function requestDeletion(Series $series): Series;

/** Any time before the sweep. */
public function cancelDeletion(Series $series): Series;

/**
 * Remove the resources, keep the record.
 *
 * Episodes and their files go. The Series row, every access, every payment
 * reference and every certificate code stay.
 */
public function purge(Series $series): Series;
```

`purge()` deletes each Episode's stored object through the storage disk before
deleting the Episode row, and tolerates an object that is already gone — a
sweep that throws on a missing file stops at the first one and leaves the rest
forever. Log it and continue.

`requestDeletion()` sets `delete_after = now()->addDays(self::DELETE_AFTER_DAYS)`
and **changes nothing else**. It does not unpublish and does not revoke: the
creator decides whether to take it down first, and a Series about to disappear
is exactly when its Peers might want a last look.

`purge()` sets `status = purged` and stamps `purged_at`, last, after the
Episodes and files are gone — so a sweep that fails partway leaves the Series
still sweepable rather than marked done with material still attached.

```php
// App\Console\Commands\PurgeSeriesCommand
protected $signature = 'qori:series:purge {--dry-run : List what would go, delete nothing}';
```

Scheduled daily in `routes/console.php`. `--dry-run` because the first run of a
destructive sweep should be readable before it is trusted.

The command must run **outside group scope**, so it needs
`Series::query()->acrossAllGroups()->deletable()`. That is a third crossing of
§21.5's boundary and it must be named as one in the docblock: a platform-wide
sweep is exactly the case the escape hatch exists for.

## Copy

| Key                            | File                 | English                                                                                      |
| ------------------------------ | -------------------- | -------------------------------------------------------------------------------------------- |
| `series.deletion_requested`    | `lang/en/series.php` | `:title will be deleted on :date. You can undo this until then.`                             |
| `series.deletion_cancelled`    | `lang/en/series.php` | `:title is staying. Nothing was deleted.`                                                    |
| `series.purged_for_peer`       | `lang/en/series.php` | `The creator has taken this :series down. Your certificate and your receipt are unaffected.` |
| `errors.series.already_purged` | `lang/en/errors.php` | message + resolution                                                                         |

The confirmation dialog reuses `series.archive_confirm`'s shape but must say
something different and stronger: name the number of Peers who lose the
material, say the date, and say what they keep.

## Routes

| Verb   | Path                                   | Name                   | Action                     |
| ------ | -------------------------------------- | ---------------------- | -------------------------- |
| DELETE | `/g/{group}/series/{seriesId}`         | `share.series.destroy` | `SeriesController@destroy` |
| POST   | `/g/{group}/series/{seriesId}/restore` | `share.series.restore` | `SeriesController@restore` |

DELETE for the request, because that is what the reader is asking for even
though nothing goes yet.

## Tests

**New: `tests/Feature/Series/DeleteSeriesTest.php` — 17 cases**

1. `test_requesting_deletion_marks_a_date_and_deletes_nothing`
2. `test_requesting_deletion_leaves_it_published` — the creator's call, not the
   product's
3. `test_a_peer_is_warned_before_the_material_goes` — the countdown, with the
   date, on the Peer's page and the public page
4. `test_a_creator_can_cancel_before_the_week_is_up`
5. `test_the_sweep_ignores_a_series_still_inside_its_window`
6. `test_the_sweep_removes_episodes_once_the_window_has_passed`
7. `test_the_sweep_deletes_the_stored_files` — `Storage::fake()`, assert missing
8. `test_the_sweep_keeps_the_access_row` — the payment record survives
9. `test_the_sweep_keeps_the_certificate_code` — §12: still verifiable, and it
   names the creator because the issuer lives on the access
10. `test_the_sweep_marks_it_purged` — status `purged`, `purged_at` stamped,
    `group_id` **unchanged**
11. `test_a_purged_series_no_longer_counts_against_the_plan_cap` — falls out of
    the null, and is asserted so it keeps falling out
12. `test_a_purged_series_is_gone_from_the_creators_list`
13. `test_a_peer_opening_a_purged_series_is_told_what_happened` — not a 404
14. `test_a_missing_file_does_not_stop_the_sweep` — delete the object first,
    assert the remaining Episodes still go
15. `test_the_dry_run_deletes_nothing`
16. `test_someone_outside_the_group_cannot_request_deletion`
17. `test_the_admin_console_still_shows_a_purged_series_against_its_creator` —
    free, because the Group link is intact; asserted so it stays free

**Changed:** `tests/Feature/Series/ArchiveSeriesTest.php` — confirm archiving
and pending-deletion do not fight. Expect no change; if one is needed, say why
in the report.

## Acceptance

- [x] Deletion is a request with a seven-day window, and nothing goes on the click
- [x] Requesting it changes nothing else — publishing stays the creator's call
- [x] Peers and public visitors are warned, with the date, before anything goes
- [x] The creator can cancel any time inside the window
- [x] A scheduled command sweeps expired requests, with `--dry-run`
- [x] Episodes and their files are removed
- [x] Access, payment reference and certificate code all survive, each proved
      by a test
- [x] A purged Series is out of the cap and out of the creator's lists, and
      still attributable to them in the admin console
- [x] `series.group_id` is untouched — no nullable relation, no second column
- [x] A Peer opening a purged Series is told what happened
- [x] The sweep survives a file that is already gone
- [x] Nothing is marked `ShouldQueue`
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**`accesses.series_id` is `cascadeOnDelete`, and this task must never delete a
Series row.** That constraint is the reason for the tombstone. If a later task
does want the row gone, it has to move the payment and certificate records
somewhere first — and that is a bigger decision than deletion, because it
changes where Qori's evidence lives.

`payment_fulfilments.series_id` and `campaigns.series_id` are `nullOnDelete`
and would survive a row deletion. `episodes.series_id` cascades, which is
convenient and is not relied on: the sweep deletes Episodes explicitly, because
it has to delete their files first.

**`status` gains its fourth value, which is one more than a string column
should be carrying in this codebase.** `T-023` converts these families to PHP
enums; it is not a dependency and this task should not wait for it, but write
`Series::STATUS_PURGED` in the same shape as its three siblings so the
conversion finds it where it expects to.

---

### What was actually true, 2026-09-11 (cursor)

**`T-023` has already run, and it went further than this task expected.**
There is no `Series::STATUS_PURGED` to write: `status` is an
`App\Models\Enums\SeriesStatus` cast, and `SeriesStatus::Purged` was declared
by `T-023` **ahead of its producer**, complete with `label() === 'Deleted'` and
`isLive() === false`. So the fourth value was already there and already
excluded from the cap. `tests/Feature/Enums/ModelEnumTest.php` even listed it
as knowingly unreachable, keyed to this task.

**`isDeleted()` in the Files table, `isPurged()` in the Code section.** Built
`isPurged()` — the Code section carries the signature and the semantics, the
tests name `purged`, and the column is `purged_at`.

**"12 cases" in the Files table, 17 in the Tests section.** Wrote the 17 the
Tests section names.

**The Files table is missing two files the Acceptance section requires.**
Test 3 and the Acceptance line both say the public page carries the countdown,
so `app/Http/Controllers/PublicSeriesController.php` and
`resources/js/pages/public/Series.vue` had to change too.

**The Copy table is missing three keys the task cannot be built without.** It
names the confirmation only in prose ("reuses `series.archive_confirm`'s shape
but must say something different and stronger") without giving a key or its
English, and gives no key at all for the countdown that Acceptance requires on
two surfaces. Added, in the shapes the prose asks for:

- `series.delete_confirm` — a `trans_choice` line naming the count, the date
  and what the Peers keep.
- `series.deletion_notice_for_peer` — the countdown for somebody who has access.
- `series.deletion_notice_public` — the countdown for a visitor who does not.

**`series.purged_for_peer` hardcoded the creator noun.** The specified English
reads "The creator has taken this :series down", which interpolates one noun
and spells the other out — and the creator noun is configurable. Written as
`:creator`.

**"One line in one place" was two places.** `Group::seriesUsed()` reads
`scopeUnarchived()`, so widening that scope handles the cap. The creator's list
is a separate query in `SeriesController::index()` that deliberately keeps
archived Series (they come back from there) and had to drop purged ones
explicitly. `scopeUnarchived()` now asks `SeriesStatus::live()` rather than
listing exceptions, so a fifth status answers the cap by answering the enum.

**Two tests the Tests section did not name had to change.**
`tests/Feature/Admin/ConsoleAccessTest.php` holds an allow-list of files
permitted to call `acrossAllGroups()`, and the sweep is the third crossing this
task explicitly sanctions — so the command is on that list now.
`tests/Feature/Enums/ModelEnumTest.php` listed `SeriesStatus::Purged` as
unreachable "T-010 — the purge sweep is not built"; that entry is gone.

`tests/Feature/Series/ArchiveSeriesTest.php` needed **no** change, as the
Tests section expected. Archiving and pending deletion do not interact:
archiving writes `status`, requesting deletion writes `delete_after`, and
neither reads the other.

**`purge()` deletes Qori-hosted objects only.** The Code section says "each
Episode's stored object", but a Dropbox path or a Vimeo id in `content` names a
file on the creator's own storage (§8). Removing a Series from Qori is not
permission to reach into their account, so the sweep skips anything whose
provider is not `QoriS3`.

**The scheduler precondition is still unmet, and now matters.** There is no
cron and no `schedule:run`/`schedule:work` process anywhere on this machine,
and `routes/console.php` had no schedule before this task. Until Laravel Cloud
runs the scheduler, a Series marked for deletion sits marked forever — which
looks exactly like nothing happening. The comment in `routes/console.php` says
so at the call site.
