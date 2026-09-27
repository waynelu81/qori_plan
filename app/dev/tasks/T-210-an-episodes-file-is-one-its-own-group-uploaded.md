---
id: T-210
title: An Episode's file is one its own Group uploaded
stream: storage
status: doing
owner: claude
estimate: M
depends: none
blocks: none
---

# T-210 — An Episode's file is one its own Group uploaded

## Why

A Qori-hosted Episode keeps its file as a key in `content['path']`, and that
key is whatever the form posted as `reference`
(`app/Http/Requests/Share/StoreEpisodeRequest.php`, `content()`'s default
arm), checked for nothing but its length. `EpisodeService::add()` stores it as
it comes, and `CloudflareR2Storage::linkFor()` signs whatever it names. So a
creator can make an Episode out of any key in the bucket — another Group's
file, a material, a chat code — and keys are not secret: every signed link a
Peer opens carries its key in the path. A Peer of one Group who runs a Group
of their own can keep reading a file after their access is taken away, by
pasting its key into an Episode of theirs.

Materials and chats already refuse this. `StoreMaterialRequest` and
`StoreChatRequest` look the upload up through the Group's own scope, want it
stored and of their purpose, and refuse one already attached elsewhere
(`errors.materials.asset_in_use`). An Episode is the one path that never
learned to, because it keeps a key in `content` where they keep a
`media_asset_id`. Afterwards an Episode is made only from an Episode upload of
its own Group that no other Episode holds, and Qori signs no Qori-hosted
Episode whose key is not one.

Found on 27 September 2026 while bringing `T-156` to ready: its deletes were
about to trust the same key. `T-156` makes every delete look the key up in the
Group's register and delete nothing it does not find; this task does the same
for the way in and for the way out.

## Decisions taken to make this specifiable

Brought to ready on 27 September 2026, from the code.

**The key is checked twice: when the Episode is made, and when its file is
signed.** On the way in, `StoreEpisodeRequest` refuses a Qori-hosted
`reference` that is not an Episode upload of the current Group, or that
another Episode of the Group already holds — on the field, at the moment of
the mistake, as `StoreMaterialRequest` does for a material. On the way out,
`PlaybackTicketService::resolve()` — the one place a Qori-hosted Episode is
signed, for `issue()` and `open()` alike — refuses one whose key is not an
Episode upload of the Series' Group. That is the wall every other caller
meets, whatever wrote the row: a seeder, a command, a future API, or a row
made before this task.

**Not in `EpisodeService::add()`.** The harm is in reading and in deleting,
and both are guarded where they happen — the signing here, the deletes by
`T-156`. A guard in `add()` would make `DesignReviewSeeder` (five Episodes on
`design-review/*.pdf`), `MailCheckCommand` (`a.pdf`) and 38 test setups in 23
files register uploads nothing ever reads, and would protect nothing the
signing wall leaves open. This departs from the pattern §8's provider rules
follow, where the service repeats the request's check; the difference is that
a provider breach is harm at the moment of writing, and a foreign key is harm
only when it is read.

**No `media_asset_id` column on `episodes`.** A foreign key would not stop a
cross-Group reference by itself: `episodes` has no `group_id` to compose one
with, so whose upload it is stays application logic either way. And the key is
what `CloudflareR2Storage::linkFor()`, `MediaLifetime` and
`MediaAssetService::deleteEpisodeObject()` already read; a column would be a
migration, a backfill and a second copy of one fact.

**An upload is found as `MediaAssetService` finds one**: the Group's
`media_assets` row of purpose `episode` at that key. A key is written only when
an upload is stored, so a pending one is not found. The lookup moves into one
public method on `MediaAssetService` that the request, the playback service
and the delete all call, so the three cannot drift.

**The refusal's words.** A key the Group holds no Episode upload for reads as
`errors.upload.not_received` — "That file didn't finish uploading." — which is
what a person meets it as: an upload that never arrived. One another Episode
holds is new, `errors.series.episode_file_in_use`, with the Episode noun
through `Terminology`. A Peer sent to a file the Group never uploaded meets
`errors.playback.missing_content`, as for an Episode with no path.

## Preconditions

None.

**Data this task verifies against:** a clean database.

**Equipment:** None.

## Scope

**In:**

- `StoreEpisodeRequest` refuses a Qori-hosted `reference` that is not an
  Episode upload of the current Group, or that another Episode of the Group
  holds.
- `PlaybackTicketService::resolve()` refuses to sign a Qori-hosted Episode
  whose key is not an Episode upload of the Series' Group.
- `MediaAssetService` gains the one lookup all three use.

**Out:**

- A guard in `EpisodeService::add()` (Decisions).
- Episodes already stored with a foreign key. Pre-release data is swept by
  the owner (`T-156`'s decision of 20 September 2026), and the signing wall
  refuses them meanwhile.
- `DesignReviewSeeder`'s five Qori-hosted Episodes, which point at files that
  exist nowhere and could not be opened before this either.
- Materials and chats, which check this already.

## Files

| Path                                               | Change | Notes                                                   |
| -------------------------------------------------- | ------ | ------------------------------------------------------- |
| `app/Services/MediaAssetService.php`               | edit   | `episodeUpload()`, used by the delete as well           |
| `app/Http/Requests/Share/StoreEpisodeRequest.php`  | edit   | the two refusals, on `reference`                        |
| `app/Services/PlaybackTicketService.php`           | edit   | `resolve()` refuses a key the Group holds no upload for |
| `lang/en/errors.php`                               | edit   | `series.episode_file_in_use`                            |
| `tests/Feature/Storage/EpisodeUploadOwnerTest.php` | new    | 7 cases                                                 |
| `docs/flows/storage.md`                            | edit   | the check on the way in and on the way out              |

## Database

None.

## Code

```php
namespace App\Services;

class MediaAssetService
{
    /** The Group's Episode upload at this key, or null: what makes a key an Episode's own. */
    public function episodeUpload(string $groupId, string $key): ?MediaAsset;

    /** Whether an Episode of the Group other than $except names this key; today's private anotherEpisodeNames(). */
    public function isNamedByAnEpisode(string $groupId, string $key, ?Episode $except = null): bool;
}
```

## Copy

| Key                                            | File         | English                                   |
| ---------------------------------------------- | ------------ | ----------------------------------------- |
| `errors.series.episode_file_in_use.message`    | `errors.php` | That file is already in another :episode. |
| `errors.series.episode_file_in_use.resolution` | `errors.php` | Upload it again to add it here too.       |

## Routes

None.

## Tests

**New: `tests/Feature/Storage/EpisodeUploadOwnerTest.php` — 7 cases**

1. `test_an_episode_is_made_from_the_groups_own_upload` — through the form.
2. `test_another_groups_upload_is_refused` — an error on `reference`, and no
   Episode.
3. `test_a_materials_upload_is_refused`.
4. `test_an_unfinished_upload_is_refused` — a pending asset, which has no key.
5. `test_an_upload_another_episode_holds_is_refused`.
6. `test_a_peer_is_not_sent_to_a_file_the_group_never_uploaded` — an Episode
   made through the service on another Group's key; opening it is
   `missing_content`, and no link names that key.
7. `test_a_peer_is_sent_to_the_groups_own_upload`.

**Changed:**

- The playback tests that open a Qori-hosted Episode on a path no upload
  wrote — `tests/Feature/Storage/OpenEpisodeTest.php`, `PlaybackTest.php` and
  `MediaLifetimeTest.php` at least — write the upload's register row first,
  as `DeleteSeriesTest::seriesWithFile()` does since `T-156`. Run the suite
  to find the rest rather than trusting this list.

## Acceptance

- [ ] An Episode cannot be made from another Group's upload, a material's or a
      chat's, an unfinished upload, or an upload another Episode holds
- [ ] No Qori-hosted Episode is signed unless its key is an Episode upload of
      its Group
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~**Whether the Episode should carry a `media_asset_id`** as materials and
  chats do.~~ **Answered from the code, 27 September 2026:** no (Decisions).
- ~~**The refusal's words**, and whether they reuse
  `errors.materials.asset_not_found` / `asset_in_use`.~~ **Answered
  27 September 2026:** `errors.upload.not_received` and a new
  `errors.series.episode_file_in_use` (Decisions).
- ~~**What happens to the callers that make a Qori-hosted Episode with no
  upload behind it**, if `add()` refuses one.~~ **Answered 27 September
  2026:** `add()` does not refuse; the signing wall does, and the playback
  tests that open such an Episode write the upload's row (Decisions, Tests).

## Re-scope log

None.

## Notes

None.
