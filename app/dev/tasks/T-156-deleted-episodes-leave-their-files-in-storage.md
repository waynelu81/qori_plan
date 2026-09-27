---
id: T-156
title: Deleting an Episode takes its file and its asset row with it
stream: operations
status: doing
owner: claude
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
(`app/Services/EpisodeService.php:329-360`). The comment one line above the
call it does make says exactly why that is wrong:

> Its materials and their objects first: the cascade would drop the rows and
> leave the files (`T-130`).

The same reasoning applies to the Episode itself and was not carried down.
`SeriesService::purge()` gets it right — it reads `content['path']`, checks
`isSelfHosted()`, and deletes the object inside a try/catch before the row
(`app/Services/SeriesService.php:282-321`) — so the two paths that remove the
same kind of row disagree, and the one a creator reaches from the interface is
the leaking one.

Afterwards both paths behave the same way, delete only what the Group's own
register holds, and the objects a deleted account owned go before the database
takes their rows.

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
`materials` does (`MaterialService::deleteObject():442`). So removing an
Episode strands **two** things — the object in R2 and the `media_assets` row
that describes it — and `SeriesService::purge()`, which deletes the object
correctly, strands the row all the same.

**The asset row goes with the object even though nothing reads it
afterwards.** It would be defensible to delete the object and leave the row,
since no code joins them. It is still wrong: `media_assets` is the register of
what Qori is holding, a row in it is a claim that an object exists, and a
register that lies is worse than no register — the owner's cleanup sweeps, and
anyone reasoning about storage later, have nothing else to read.

**Only an object the Group's own register holds is deleted, and only when no
other Episode of the Group still names it** (27 September 2026, from the
code). An Episode's `content['path']` is the `reference` the form posted
(`StoreEpisodeRequest::content()`), checked for nothing but its length, so it
can name any key in the bucket — another Group's included, and a Peer sees
keys in every signed link. `purge()` deletes that path as it finds it, so today
a creator can have another Group's file deleted by pointing an Episode at it
and deleting their own Series; `remove()` doing the same would make it
immediate. So the delete looks the key up among the Series' Group's stored
`media_assets` and deletes nothing it does not find there. And a hand-made
request can put one key in two Episodes, so an object another Episode of the
Group still names stays, with its row. Stopping such a path being written at
all is `T-210`, drafted with this finding.

**Both paths call one method rather than each keeping a copy** —
`MediaAssetService::deleteEpisodeObject()`, which keeps `purge()`'s
`isSelfHosted()` guard, its empty-path check and its try/catch that logs and
swallows. `purge()`'s comment gives the reason for the last and it holds here:
a delete that throws on an object already gone would block the row delete, and
a missing object is the outcome wanted anyway.

**The object goes first, then the Episode row, then the asset row.** This is
`purge()`'s "files before rows" and `MaterialService::removeAllOf()`'s "row
before asset". A crash after the object leaves rows naming a file that is
gone, which the creator sees and removes again; the reverse would strand an
object nothing names, which only a listing of the bucket could find. In
`remove()` all three happen inside its existing transaction.

**An Episode removed from a Series awaiting deletion loses its file too**
(27 September 2026, from the code). `remove()` deletes the Episode row at once
whatever the Series' state, and `cancelDeletion()` clears only the date —
nothing brings a removed Episode back — so keeping its file would strand it
for good.

**Account deletion deletes the objects before the cascade, and leaves the rows
to it.** `ProfileController::destroy()` is `Auth::logout()`, `$user->delete()`,
invalidate (`:122-134`), and `groups.owner_user_id → series.group_id →
episodes.series_id` are all `cascadeOnDelete`
(`2026_09_08_000000_create_qori_schema.php:58`, `:84`, `:105`). The database
removes every row with no PHP running, and `media_assets.group_id` is
`cascadeOnDelete` too — so the register that would let anyone find those
objects dies in the same statement, and the objects have to go first. The
rows cannot: `materials_content_matches_provider` and
`series_chats_one_way_in` refuse a Qori-hosted material or a code chat whose
`media_asset_id` is nulled, and deleting such an asset row directly fails with
a check violation, while the cascade from `groups` takes them all at once
without one (both probed on 27 September 2026). So every stored object in the
owned Group's register goes — Episodes', materials' and chat codes' alike —
and then `$user->delete()` takes the rows.

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
- `SeriesService::purge()` deletes the `media_assets` row it already orphans,
  and only an object the Group's register holds.
- `ProfileController::destroy()` deletes the owned Group's objects before
  `$user->delete()`.

**Out:**

- **Cleaning up anything already stranded**, in R2 or in `media_assets`. The
  owner sweeps the production database and the bucket before release, so
  release starts clean (20 September 2026). An orphan-finding command was
  drafted here and removed on that decision.
- **Any command, and anything scheduled.** Follows from the above: there is
  nothing left for one to do.
- **Refusing an Episode path the Group never uploaded**, on the way in:
  `T-210`.
- **Objects with no `media_assets` row at all.** Nothing is known to create
  one, and finding them would need a bucket listing, which is the owner's
  sweep rather than Qori's code. A path with no row is now left alone by
  `purge()` too, where it used to be deleted.
- **Materials and chats**, which already delete correctly through
  `MaterialService::removeAllOf()` and `SeriesChatService::purgeFor()`.
- **`MailCheckCommand`'s `Series::query()->forGroup($group)->delete()`**,
  the one query-builder mass delete in the codebase. It runs against a
  scratch Group in a developer's mail check, never a customer's, and giving
  it the same treatment is noise in a task about a real leak — noted here so
  the next reader knows it was seen.
- Unconfirmed uploads that were signed and never finished. Their objects sit
  in the incoming prefix, which the bucket's lifecycle rule expires.

## Files

| Path                                                  | Change | Notes                                                              |
| ----------------------------------------------------- | ------ | ------------------------------------------------------------------ |
| `app/Services/MediaAssetService.php`                  | new    | The Episode's object, and an owner's objects before the cascade    |
| `app/Services/EpisodeService.php`                     | edit   | `remove()`: the object, the Episode row, the asset row             |
| `app/Services/SeriesService.php`                      | edit   | `purge()` calls the service, and deletes the asset row it orphaned |
| `app/Http/Controllers/Settings/ProfileController.php` | edit   | `destroy()` deletes the owned Group's objects first                |
| `tests/Feature/Media/OrphanedObjectTest.php`          | new    | 9 cases                                                            |
| `docs/flows/series.md` `docs/flows/storage.md`        | edit   | What removing, purging and deleting an account take with them      |

## Database

None.

## Code

```php
namespace App\Services;

class MediaAssetService
{
    /**
     * The object behind a Qori-hosted Episode, deleted, and its media_assets row
     * handed back for the caller to delete after the Episode row. Null, and
     * nothing deleted, when the Episode is not Qori-hosted, has no path, names a
     * key the Series' Group holds no stored asset for, or shares it with another
     * of the Group's Episodes. A storage failure is logged and swallowed.
     */
    public function deleteEpisodeObject(Series $series, Episode $episode): ?MediaAsset;

    /**
     * Every stored object in the register of each Group the person owns, before
     * their account's cascade takes the rows.
     *
     * @return int how many objects were deleted
     */
    public function deleteObjectsOwnedBy(User $owner): int;
}
```

`EpisodeService` and `SeriesService` take it by constructor; `ProfileController::destroy()`
by method injection.

## Copy

None. No user-facing string changes; the only new output is a `Log::warning`
on a storage failure, which §Errors exempts as a diagnostic.

## Routes

None.

## Tests

**New: `tests/Feature/Media/OrphanedObjectTest.php` — 9 cases**

1. `test_removing_an_episode_deletes_its_object_and_asset_row` — through the
   creator's delete request.
2. `test_removing_an_episode_from_a_series_awaiting_deletion_deletes_them_too`.
3. `test_removing_a_linked_episode_deletes_no_object`.
4. `test_a_storage_failure_does_not_block_the_removal` — the disk throws, the
   Episode and asset rows still go, and a warning is logged.
5. `test_purging_a_series_deletes_the_asset_rows_too`.
6. `test_an_episode_naming_another_groups_file_deletes_nothing` — neither
   removing it nor purging its Series touches the other Group's object or row.
7. `test_a_file_another_episode_still_names_is_kept`.
8. `test_deleting_an_account_deletes_the_owned_groups_objects` — an Episode's,
   a material's and a chat code's; the account, the Group and every asset row
   gone with them.
9. `test_deleting_an_account_leaves_a_group_it_only_helps_run_alone` — the
   person is an admin in another Group, whose objects stay.

**Changed:**

- `tests/Feature/...` covering `EpisodeService::remove()` and
  `SeriesService::purge()` — they assert rows, not objects, so they should
  pass unchanged; confirm rather than assume.

## Acceptance

- [ ] Removing an Episode through the interface leaves no object and no asset row
- [ ] Purging a Series leaves no asset row
- [ ] Neither ever deletes an object its Group's register does not hold, or one
      another of its Episodes names
- [ ] Deleting an account leaves no object belonging to the Group it owned
- [ ] A storage failure never blocks a row delete
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

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
- ~~**Whether an Episode's object should be deleted at all when the Series is
  only marked for deletion**, rather than purged.~~ **Answered from the code,
  27 September 2026:** yes — a removed Episode never comes back, whatever the
  Series' state (Decisions).

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
