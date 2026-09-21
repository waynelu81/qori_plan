---
id: T-156
title: Deleting an Episode takes its file and its asset row with it
stream: operations
status: draft
owner: unassigned
estimate: S
depends: none
blocks: T-091
---

# T-156 — Deleting an Episode takes its file and its asset row with it

> **Found on 20 September 2026** while grounding `T-091`'s `F01` against the
> deletion paths, and drafted because it has nothing to do with `T-091`:
> Qori leaks its own R2 objects today, with no vendor and no Peer involved.

## Why

`EpisodeService::remove()` deletes an Episode's **materials** and their objects
and then deletes the Episode row — and never touches the Episode's own file
(`app/Services/EpisodeService.php:301-332`). The comment one line above the
call it does make says exactly why that is wrong:

> Its materials and their objects first: the cascade would drop the rows and
> leave the files (`T-130`).

The same reasoning applies to the Episode itself and was not carried down.
`SeriesService::purge()` gets it right — it reads `content['path']`, checks
`isSelfHosted()`, and deletes the object inside a try/catch before the row
(`app/Services/SeriesService.php:286-309`) — so the two paths that remove the
same kind of row disagree, and the one a creator reaches from the interface is
the leaking one.

Afterwards both paths behave the same way, and the objects a deleted account
owned go before the database takes their rows.

## Decisions taken to make this specifiable

**This task stops the leak and cleans nothing up** (the owner, 20 September
2026). Whatever is already stranded in R2 or in `media_assets` is handled by
the owner's own sweeps of the production database and bucket before release,
so release is a clean slate. An orphan-finding command was drafted here and
taken out again: it would have been built to answer a question that will not
exist by the time anyone could run it, and a delete command nobody needs is a
delete command nobody has reason to be careful with.

**Both leaks are one bug.** An Episode upload writes a `media_assets` row with
`purpose = episode` (`app/Http/Controllers/Share/UploadController.php:40`,
`MediaAssetPurpose::Episode`) and the Episode stores only the key, in
`content['path']`. Nothing links them: `episodes` has no `media_asset_id`, as
`materials` does (`MaterialService::deleteObject():281`). So removing an
Episode strands **two** things — the object in R2 and the `media_assets` row
that describes it — and `SeriesService::purge()`, which deletes the object
correctly, strands the row all the same.

**The asset row goes with the object even though nothing reads it
afterwards.** It would be defensible to delete the object and leave the row,
since no code joins them. It is still wrong: `media_assets` is the register of
what Qori is holding, a row in it is a claim that an object exists, and a
register that lies is worse than no register — the owner's cleanup sweeps, and
anyone reasoning about storage later, have nothing else to read.

**`remove()` copies `purge()` rather than inventing a second shape** — the
same `isSelfHosted()` guard, the same empty-path check, the same try/catch
that logs and swallows. `purge()`'s comment gives the reason and it holds
here: a delete that throws on an object already gone would block the row
delete, and a missing object is the outcome wanted anyway.

**The object goes before the row, and the asset row after both.** This is
`MaterialService::removeAllOf()`'s order, whose own comment reads "Row before
asset, as `remove()`". A crash between them leaves an object nothing claims,
which a later sweep of the bucket can see; the reverse leaves a row claiming
an object that is gone, which nothing can tell from a live one.

**Account deletion is cleaned up in the controller, before the cascade, not
after it.** `ProfileController::destroy()` is `Auth::logout()`,
`$user->delete()`, invalidate (`:122-133`), and
`groups.owner_user_id → series.group_id → episodes.series_id` are all
`cascadeOnDelete` (`2026_09_08_000000_create_qori_schema.php:58`, `:84`,
`:105`). The database removes every row with no PHP running, and
`media_assets.group_id` is `cascadeOnDelete` too — so the registry that would
let anyone find those objects afterwards dies in the same statement. After the
cascade there is nothing left to reconcile against; it has to happen first.

**No new command, and nothing scheduled.** Every change here happens inside a
path that already exists and already deletes rows. Nothing runs on a timer,
so the Laravel Cloud sleep-timeout rule and the `onOneServer()` question that
`release-prerequisites.md` raises for scheduled work do not arise.

## Preconditions

**Data this task verifies against:** a clean database. Every case builds its
own Series, Episode and asset row through factories.

**Equipment:** none. `Storage::fake()` covers the disk, per §Tests; the
production bucket is not touched by any check here.

## Scope

**In:**

- `EpisodeService::remove()` deletes the Episode's object and its
  `media_assets` row.
- `SeriesService::purge()` deletes the `media_assets` row it already orphans.
- `ProfileController::destroy()` clears the owned Group's objects and asset
  rows before `$user->delete()`.

**Out:**

- **Cleaning up anything already stranded**, in R2 or in `media_assets`. The
  owner sweeps the production database and the bucket before release, so
  release starts clean (20 September 2026). An orphan-finding command was
  drafted here and removed on that decision.
- **Any command, and anything scheduled.** Follows from the above: there is
  nothing left for one to do.
- **Objects with no `media_assets` row at all.** Nothing is known to create
  one, and finding them would need a bucket listing, which is the owner's
  sweep rather than Qori's code.
- **Materials**, which already delete correctly through
  `MaterialService::removeAllOf()`.
- **`MailCheckCommand:287`'s `Series::query()->forGroup($group)->delete()`**,
  the one query-builder mass delete in the codebase. It runs against a
  scratch Group in a developer's mail check, never a customer's, and giving
  it the same treatment is noise in a task about a real leak — noted here so
  the next reader knows it was seen.
- Unconfirmed uploads that were signed and never finished. A different
  lifecycle, and nothing here touches them.

## Files

| Path                                                  | Change | Notes                                                           |
| ----------------------------------------------------- | ------ | --------------------------------------------------------------- |
| `app/Services/EpisodeService.php`                     | edit   | `remove()` deletes the object and the asset row before the row  |
| `app/Services/SeriesService.php`                      | edit   | `purge()` deletes the asset row it already leaves behind        |
| `app/Http/Controllers/Settings/ProfileController.php` | edit   | `destroy()` clears the owned Group's objects before the cascade |
| `app/Services/MediaAssetService.php`                  | new    | Where the shared "delete this key and its row" logic lives      |
| `tests/Feature/Media/OrphanedObjectTest.php`          | new    | 6 cases                                                         |
| `docs/flows/series.md` `docs/flows/storage.md`        | edit   | The delete and purge chains now say what happens to the object  |

Flows: `docs/flows/series.md` and `docs/flows/storage.md` above.

## Database

None.

## Code

```php
namespace App\Services;

class MediaAssetService
{
    /** Delete the object and its row; logs and swallows a storage failure, as purge() does. */
    public function forget(MediaAsset $asset): void;

    /** The object and row behind an Episode's content['path'], when it is self-hosted. */
    public function forEpisode(Episode $episode): ?MediaAsset;

    /** Every confirmed asset a Group holds, for the clear-out before an owner's account is deleted. */
    public function forgetGroup(string $groupId): int;
}
```

## Copy

None. No user-facing string changes; the only new output is a `Log::warning`
on a storage failure, which §Errors exempts as a diagnostic.

## Routes

None.

## Tests

**New: `tests/Feature/Media/OrphanedObjectTest.php` — 6 cases**

1. `test_it_deletes_the_object_when_an_episode_is_removed` — `Storage::fake()`,
   the key is gone after `remove()`.
2. `test_it_deletes_the_asset_row_when_an_episode_is_removed`.
3. `test_it_leaves_a_linked_episode_alone` — an Episode that is not
   self-hosted loses no object.
4. `test_it_removes_the_episode_when_the_object_cannot_be_deleted` — the disk
   throws, the row still goes, a warning is logged.
5. `test_it_deletes_the_asset_row_when_a_series_is_purged`.
6. `test_it_clears_the_groups_objects_before_the_account_is_deleted` — the
   objects are gone and the user row is too, in that order.

**Changed:**

- `tests/Feature/...` covering `EpisodeService::remove()` and
  `SeriesService::purge()` — they assert rows, not objects, so they should
  pass unchanged; confirm rather than assume.

## Acceptance

- [ ] Removing an Episode through the interface leaves no object and no asset row
- [ ] Purging a Series leaves no asset row
- [ ] Deleting an account leaves no object belonging to the Group it owned
- [ ] A storage failure never blocks a row delete
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree

## Before this can be ready

- ~~**How much is already stranded in the production bucket**, which decides
  whether this is a leak to stop or a cleanup to run as well.~~ ~~**Whether
  the orphan query wants an index.**~~ **Both answered 20 September 2026 by
  the owner:** neither matters, because the production database and the
  bucket are swept by hand before release and nothing built here will ever
  meet a pre-release orphan. This task stops the leak and nothing more.
- ~~**Whether `docs/tinker/storage.md` exists**, and which tinker file the
  recipe belongs in if not.~~ **Answered 20 September 2026:** it does not.
  `docs/tinker/` holds `uploads.md`. **Moot since the same day**, with the
  sweep gone: there is no new command to write a recipe for, and the three
  paths this task fixes are driven from the interface rather than from
  tinker.
- **Whether an Episode's object should be deleted at all when the Series is
  only marked for deletion**, rather than purged. `requestDeletion()` sets
  `delete_after` and changes nothing else, and `qori:series:purge` is what
  eventually runs — so today an Episode removed from a Series awaiting purge
  is the leaking path, and an Episode removed with the Series is not. This
  task treats them the same; confirm that is wanted — the owner's.

## Re-scope log

None.

## Notes

The two paths were written two weeks apart and neither is careless:
`purge()`'s docblock reasons carefully about ordering and about why it holds
no transaction, and `remove()`'s reasons carefully about renumbering and about
materials. Each thought about the object problem in its own frame and only one
of them was looking at the Episode's own file. That is worth remembering the
next time a second path is added to delete the same kind of row — the check is
not "is this code careful" but "do the two paths agree".
