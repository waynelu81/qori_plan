---
id: T-131
title: A Peer opens materials before and after the session, and sees homework due in their own time
stream: classroom
status: ready
owner: unassigned
estimate: M
depends: T-125, T-130
blocks: T-132, T-145
---

# T-131 — A Peer opens materials before and after the session, and sees homework due in their own time

> **Draft.** Not to be started — see [`../PROCESS.md`](../PROCESS.md). What
> has to be true before it can be marked `ready` is listed at the bottom.
> Written on 17 September 2026 from `D-030`, `D-024` and `D-020`, as the
> Peer half of `T-130`.

## Why

After `T-130` a creator can attach up to `config('qori.materials.per_episode')`
materials to an Episode, and no Peer can reach one. `SharedController::show()`
sends each Episode as `id`, `title`, `position`, `type`, `startsAt`,
`isCompleted` and `isOpened` (`app/Http/Controllers/Shared/SharedController.php:134-142`)
and nothing else, and `resources/js/pages/shared/Show.vue` renders exactly that
row (`:194-229`). The only Peer path to an object on Qori's storage is
`PlaybackTicketService::issue()` (`app/Services/PlaybackTicketService.php:44-73`),
which resolves an _Episode_ through `ResolvesMedia::linkFor(Episode, ?Connection)`
(`app/Integrations/Contracts/ResolvesMedia.php:34`); `CloudflareR2Storage::linkFor()`
reads `content['path']` (`app/Integrations/CloudflareR2/CloudflareR2Storage.php:35`)
and `MediaLifetime::minutesFor()` takes only an Episode
(`app/Support/MediaLifetime.php:33-38`). A material is a row with a
`media_assets.key` or a pasted URL, not an Episode, so nothing today can sign
one or follow one.

`D-030` says release governs what Qori lists and when it signs a Qori-hosted
file's URL — "Shown after the session", never an embargo on a vendor's file —
and that a Qori-hosted material is reached through
`SignsStoredFiles::temporaryLink()` on `CloudflareR2Storage` with a lifetime
from the extension. `D-024` keeps the Series page as the Peer's one
destination, every Episode row anchored `#episode-{id}`; `D-020` sends a link
Qori will not follow yet back to that page, where the row holds the next
step. `D-025` calls a pasted link, on the Peer's side, a link the creator
manages.

Afterwards each Episode row on `/shared/{seriesId}` lists its materials under
Preparation, Material and Homework. Open is an `<a target="_blank">` to
`shared.materials.open`, which passes the gate the Series page passes, checks
release against `LiveSessionService::stateFor()`, logs the open to
`access_opens`, marks the Episode opened and answers 302 — to the pasted URL,
or to a signed R2 URL that lives as long as a document link does. An
`after_session` item is listed with "Shown after the session" and no link
until the join window has closed; its address opened early lands on the row
with a one-line toast. A homework row shows its brief and its due date in the
Peer's own zone with the Group's zone beside it. `T-132` mounts the chat card
beside this list, and `T-145` walks it.

## Decisions taken to make this specifiable

**The route passes the Series page's gate and answers it the same way.**
`Access::forUser($peer)->where('series_id', …)->first()`
(`SharedController.php:88-90`), absent → 403 `errors.access.not_granted`
(`:114-117`), the Series through `grantedSeries()` (`:123-127`). Never a
redirect into the page for a missing or revoked Access: the merged reference
(`docs/planning/course-classroom.md`) had one, the brief says 403, and a
revoked Peer following a saved link is owed the answer the Series page gives
them, not a page whose notice they no longer qualify for. The redirect is for
release alone.

**The open lives in `MaterialService::open()`; the controller only
redirects.** Entry points delegate (`CLAUDE.md`), the vendor call is a
contract read by a Service — as `PlaybackTicketService::open()` (`T-089`)
does for an Episode — and the JSON API will have to make the same decisions.

**The Material and its asset are read with `forGroup($series->group)`, never
through a relation.** `Material` and `MediaAsset` are `BelongsToGroup` and
the Peer is in no Group, so `$material->asset` would throw the way
`$access->series` does (`Access::grantedSeries()`,
`app/Models/Access.php:226-241`). `Series::findForPeer()` and
`Access::grantedSeries()` are the sanctioned crossings; `forGroup()`
(`app/Concerns/BelongsToGroup.php:52-57`) is a single-tenant read from
outside the context. No `acrossAllGroups()` caller is added, so
`tests/Feature/Admin/ConsoleAccessTest.php`'s allow-list is untouched.

**The answer is a `MaterialLink`, not a `MediaLink` and not `T-089`'s
`VendorLink`.** A pasted link has no expiry — the creator's sharing governs
it (`D-025`) — so `MediaLink`'s non-nullable `expiresAt` would be a lie;
`VendorLink`'s `blockedState` is a grant state and its `accountHint` is
`T-092`'s, and neither describes a row that is either released or not. Three
small factories and one question, `isReleased()`.

**Release is computed from `LiveSessionService::stateFor()`, and three states
hold.** An `after_session` row on a live Episode is held while the state is
`Upcoming`, `Open` or `Cancelled`: the join window has not closed (`D-026`:
`open` runs until `join_closes_after_minutes` after the scheduled end), or the
session was called off and "after the session" means nothing until Undo
(`T-134`). `Waiting`, `Review`, `Ready`, `Overdue` and `NotRecorded` release.
A `with_episode` row, a row on a non-live Episode and a Series-level row
(`episode_id` null, `T-137`) are always released. The list and the route both
ask `MaterialService::isReleased()`, so the page cannot show a link the route
refuses, and nothing is stored (`D-026`).

**A Qori-hosted material is signed through a second contract,
`SignsStoredFiles`, bound rather than tagged.** `ResolvesMedia` takes an
Episode and reads `content['path']`; a material has a key. One implementation
exists and only Qori's storage is Qori-hosted, so it is `bind()` beside
`SellsSeries` (`app/Providers/IntegrationServiceProvider.php:29-30`), not a
tag. `CloudflareR2Storage::linkFor()` delegates to the new method, so one
signing path serves both. The window is
`MediaLifetime::minutesForExtension($asset->extension)` — the stored column,
lower-cased already by `UploadKey::extensionOf()`
(`app/Support/UploadKey.php:72-75`) — and `minutesFor(Episode)` delegates to
the same table, so a PDF material and a PDF Episode expire alike. No config
changes; `link_ttl` (`config/qori.php:102-108`) is read as it is.

**An open is recorded twice, on purpose.**
`AccessOpen::record($access, OpenTarget::Material, $episodeId, $materialId)`
is the log `T-125` created for Join; `ProgressService::opened()`
(`app/Services/ProgressService.php:159`) moves `last_activity_at` and adds
the Episode to `opened_episode_ids`, because its own docblock says opening is
"reached an episode's material" and the stalled campaign reads
`last_activity_at` — a Peer who read the pre-reading has been back. Both
happen after the release check and before the signer, as
`PlaybackTicketService::open()` records before it resolves, so a signer that
fails still counts. A held row records nothing, and neither does a
brief-only homework row, whose guard runs first.

**Not yet is a 302 to the row with a toast, in `T-089`'s shape (`D-020`).**
`Inertia::flash('toast', ['type' => 'info', 'message' => …])` then
`redirect()->to(route('shared.show', $seriesId).'#episode-'.$episodeId)`, as
`PaymentsFinaliseController` flashes before a redirect
(`app/Http/Controllers/Settings/PaymentsFinaliseController.php:64-75`) and
`T-089`'s `OpenEpisodeController` does for a blocked link; Inertia fires the
flash event on a full page load too. The sprint brief names
`route('shared.episodes.show')` as the destination; that anchor route is
skipped and the redirect goes straight to the Series page, because a second
redirect would age the flash out before the page loads — the choice `T-125`
makes for its two blocked states. The toast names the `:episode` in the
Series' Group's words, resolved by `MaterialService::open()`, which holds the
Group already, and carried on `MaterialLink::$notice`, so the controller
reads nothing.

**A file that never arrived is a 404, not a signed link to nothing.** A
`cloudflare_r2` row whose asset is not `isStored()`
(`app/Models/MediaAsset.php:99-102`) or has no `key` answers
`errors.materials.unavailable`. Signing the incoming key would hand out a URL
that 404s at the bucket in a new tab — the predictable dead page the beta
gate forbids — and records no open.

**The list is one component under `resources/js/components/series/`, with
copy as props.** `PeerMaterialList.vue`, mounted once per Episode row by
`shared/Show.vue`: a page edit is a mount (`D-024`), and `T-132` mounts its
card after it in the stream's claim order. Every sentence arrives from
`SharedController::show()` as `materialCopy`; the component holds no English.
Rows are grouped preparation, then material, then homework, in `position`
order within each, because that is the order a Peer needs them in and the
creator's list is one list.

**The due date is an instant plus the Group's zone; the browser does the
Peer's half.** `dueAt` is ISO 8601 with offset and is rendered by
`SessionTime.vue` with `T-125`'s `groupTimezone` prop, exactly as the session
time is. A page-level `groupTimezone` prop carries `Group::timezone()`
(`app/Models/Group.php:221-232`), so a homework on a non-live Episode has the
zone too. `users.timezone` is the mail rule (`T-128`); on the page the
reader's browser zone is the Peer's own, and `T-125` is where they are asked
to keep the two in step.

**Homework has one control, Open, and the hand-in destination is
`content.url`.** `D-030` puts the hand-in destination in `content.url` and
`T-130`'s form takes one URL, so a `link` homework's Open goes there and a
Qori-hosted homework's Open goes to the upload, with the brief (`note`) saying
where to hand in; a Qori-hosted homework has no hand-in field this sprint. A
brief-only homework row — `provider = link`, `content = '[]'`, which the
sprint brief's reconciliation allows — has no control at all: the brief and
the due date are the homework, the row's `isOpenable` is false, and its
address answers `errors.materials.unavailable` before anything is recorded.
No tick and no submission (`D-030`).

**The public page changes nothing and gains a test.**
`PublicSeriesController::show()` sends titles only
(`app/Http/Controllers/PublicSeriesController.php:88-93`); one case asserts
no `materials` key and no material title or URL in the body for a preview
Episode (`D-024`).

**A provider this sprint cannot serve answers `unsupported`.** `google_drive`,
`dropbox` and `onedrive` rows are written by `T-094`, `T-096` and `T-098`,
which add their own arm to `open()`; until then the `match` default throws
`errors.playback.unsupported_provider`, a programmer's dead end no creator can
reach because `T-130`'s Form Request accepts only `cloudflare_r2` and `link`.

**`SharedController::show()` reads the Series' materials in one query and
takes `MaterialService` by method injection.** One `forGroup()` read of every
Episode-level row for the Series, grouped by `episode_id`, rather than a
query per Episode; method injection because `show()` is the one action that
reads materials, and `T-125` keeps the controller's constructor empty for this
task and `T-132`.

## Preconditions

**Data this task verifies against:** a clean database. The feature tests
build their own world: a Group with a `timezone`
(`Group::factory()->create(['plan' => 'start', 'timezone' => 'Australia/Brisbane'])`),
a Series through `SeriesService::create()`, a live Episode through
`EpisodeService::add()` with `T-123`'s `$startsAt` and `$lengthMinutes`
parameters, a File Episode as `tests/Feature/Access/SharedRoutesTest.php:27-35`
adds one, materials through `MaterialService::add()` (`T-130`), and a stored
file as
`MediaAsset::factory()->stored()->create(['group_id' => $group->getKey(), 'purpose' => MediaAssetPurpose::Material, 'key' => 'materials/'.$group->getKey().'/'.Str::ulid().'.pdf', 'extension' => 'pdf'])`
— the factory's `stored()` state writes an `episodes/` key
(`database/factories/MediaAssetFactory.php:40-47`), so the key is passed.
Nothing is written to the disk: the local disk signs a URL for a key whether
or not an object is there, which `tests/Feature/Storage/PlaybackTest.php:56-69`
already relies on.

**Equipment:** none for the tests. For the acceptance walk, a visible browser
at mobile and desktop widths, signed in as a Peer whose `users.timezone` is at
least eight hours from the Group's (the stream's exit condition), so the
due-date line shows two different zones.

**Spike:** none owed. This task introduces no vendor payload: a pasted link is
followed by the browser and never by Qori (`D-025`), and the signed R2 URL is
the one `CloudflareR2Storage::linkFor()` mints today.

## Scope

**In:**

- `shared.materials.open`, `OpenMaterialController`, `MaterialService::open()`
  and `isReleased()`, `App\Data\MaterialLink`.
- `SignsStoredFiles`, its `CloudflareR2Storage` implementation with
  `linkFor()` delegating to it, the binding; `MediaLifetime::minutesForExtension()`
  and `kindOfExtension()`.
- `SharedController::show()`: `materials` per Episode, `groupTimezone`,
  `materialCopy`.
- `PeerMaterialList.vue`, mounted under each Episode row of `shared/Show.vue`:
  three role groups, Open as a link, "Shown after the session", the brief, the
  due date in two zones, the "link the creator manages" line, and no control
  on a brief-only homework row.
- The Peer copy under `materials.peer.*`, the `materials.not_yet` toast, and
  `errors.materials.unavailable`; `T-130`'s `materials.roles.*`,
  `materials.due_prefix` and `errors.materials.not_found` are reused, not
  re-declared.
- `docs/flows/materials.md` (the Peer side), `docs/flows/storage.md` (the
  lifetime table applies to a material; the second contract),
  `docs/tinker/accesses.md` (opening a material by hand).

**Out:**

- Series-level materials (`episode_id` null) on the Peer page, and reorder:
  `T-137`. `open()` and `isReleased()` accept a null `episode_id` (always
  released, no anchor) so `T-137` adds a mount, not a branch.
- The chat card and `id="chat"`: `T-132`.
- Join and the live card: `T-125`. Watch and the recording line on the same
  card: `T-126`.
- The per-Series storage total and the running total on the form: `T-139`.
- Connected-tier rows — `google_drive`, `dropbox`, `onedrive` through a
  picker, the per-Peer grant, `checkItem()` growing a materials branch:
  `T-094`, `T-096`, `T-098`, `T-091`. This route answers `unsupported` for any
  provider but `cloudflare_r2` and `link`.
- Any change to the creator's list, form, `MaterialService::add()`,
  `update()` or `remove()`, the caps or the purge: `T-130`.
- Homework submissions, a "handed in" tick, a self-reported "I submitted
  this", a due-date reminder: not built (`D-030`).
- A read mark per material or a per-material open count on the creator's
  page: `access_opens` is written here and read by nothing until a later task
  wants it.
- The public page: unchanged, guarded by a test.
- Materials in the recording-ready email: `T-128` reads the same rows.
- The extensions `odt`, `ods`, `odp` and `epub`: the owner's (`D-030`);
  `MediaLifetime::DOCUMENT_EXTENSIONS` (`app/Support/MediaLifetime.php:29`) is
  not touched here.
- Timezone prompting for a Peer whose `users.timezone` is null: `T-125`.

## Files

| Path                                                     | Change | Notes                                                                                                                                      |
| -------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `app/Integrations/Contracts/SignsStoredFiles.php`        | new    | `temporaryLink(string $key, int $minutes): MediaLink`; `T-130` signs nothing — declared here per the sprint brief                          |
| `app/Integrations/CloudflareR2/CloudflareR2Storage.php`  | edit   | implements `SignsStoredFiles`; `linkFor()` delegates to `temporaryLink()`                                                                  |
| `app/Providers/IntegrationServiceProvider.php`           | edit   | `bind(SignsStoredFiles::class, CloudflareR2Storage::class)`                                                                                |
| `app/Support/MediaLifetime.php`                          | edit   | `minutesForExtension()`, `kindOfExtension()`, private `minutesForKind()`; `minutesFor()` delegates                                         |
| `app/Data/MaterialLink.php`                              | new    | url, provider, expiresAt, anchorEpisodeId, notice; `fromMediaLink()`, `pasted()`, `notReleased()`, `isReleased()`                          |
| `app/Services/MaterialService.php`                       | edit   | `open()`, `isReleased()`, `HELD_STATES`, private `storedAsset()`; four constructor dependencies                                            |
| `app/Http/Controllers/Shared/OpenMaterialController.php` | new    | 302 to the link, or to `shared.show#episode-{id}` with the `materials.not_yet` toast                                                       |
| `app/Http/Controllers/Shared/SharedController.php`       | edit   | `materials` per Episode, `groupTimezone`, `materialCopy`; `MaterialService` as a fifth parameter; private `materialsByEpisode()`           |
| `routes/shared.php`                                      | edit   | `shared.materials.open`                                                                                                                    |
| `resources/js/components/series/PeerMaterialList.vue`    | new    | the list; copy as props; no inline English                                                                                                 |
| `resources/js/pages/shared/Show.vue`                     | edit   | `GrantedEpisode.materials`, two props, one mount per row                                                                                   |
| `lang/en/materials.php`                                  | edit   | `peer.open`, `peer.after_session`, `peer.link_managed`, `not_yet`; `T-130` creates the file, and its `roles.*` and `due_prefix` are reused |
| `lang/en/errors.php`                                     | edit   | `materials.unavailable`, in the group `T-130` opens with `materials.limit`; `materials.not_found` is `T-130`'s and reused                  |
| `docs/flows/materials.md`                                | edit   | "Opening, from the Peer's side": the gate, release, the two redirects, the two records; `T-130` creates it                                 |
| `docs/flows/storage.md`                                  | edit   | "How long a link lives": a material's extension is consulted the same way; `SignsStoredFiles` named                                        |
| `docs/tinker/accesses.md`                                | edit   | "The peer surface crosses groups" gains `MaterialService::open()` by hand                                                                  |
| `tests/Feature/Shared/OpenMaterialTest.php`              | new    | 18 cases                                                                                                                                   |
| `tests/Feature/Storage/MediaLifetimeTest.php`            | edit   | 2 cases for `minutesForExtension()`                                                                                                        |

`qori:reachability` sees the new route through `PeerMaterialList.vue`'s
Wayfinder import and the generated `resources/js/routes/shared/materials`
file, which carries the URI (`Reachability::GENERATED`,
`app/Support/Reachability.php:37`; `isLinked()`, `:162-171`). No config, no
factory, no seeder: the numbers are `T-123`'s and the rows are `T-130`'s.

## Database

None. The rows this task reads are `T-130`'s `materials` and `T-125`'s
`access_opens`; it adds no column and no index.

## Code

```php
namespace App\Integrations\Contracts;

use App\Data\MediaLink;

/**
 * A short-lived URL for one object on Qori's own storage, by its stored key.
 *
 * Beside ResolvesMedia, not inside it: that contract takes an Episode and
 * reads content['path'], and a material is not an Episode. The key is
 * media_assets.key. The window is the caller's — MediaLifetime decides it
 * from the extension — so a PDF material and a PDF Episode expire alike.
 */
interface SignsStoredFiles
{
    public function temporaryLink(string $key, int $minutes): MediaLink;
}
```

```php
// App\Integrations\CloudflareR2\CloudflareR2Storage implements ResolvesMedia, SignsStoredFiles

public function temporaryLink(string $key, int $minutes): MediaLink;
// $expiresAt = now()->addMinutes($minutes);
// $disk = Storage::disk((string) config('qori.storage.disk'));
// $url = $disk->providesTemporaryUrls() ? $disk->temporaryUrl($key, $expiresAt) : $disk->url($key);   // today's :53-55, moved
// return new MediaLink(url: $url, expiresAt: $expiresAt, provider: $this->provider());

public function linkFor(Episode $episode, ?Connection $connection): MediaLink;
// the empty-path check at :35-42 unchanged, then:
// return $this->temporaryLink($path, MediaLifetime::minutesFor($episode));
```

```php
// App\Providers\IntegrationServiceProvider::register() — one line after :35
$this->app->bind(SignsStoredFiles::class, CloudflareR2Storage::class);
```

```php
// App\Support\MediaLifetime — the same table, reachable from an extension alone

public static function minutesFor(Episode $episode): int;              // self::minutesForKind(self::kindOf($episode))
public static function minutesForExtension(string $extension): int;   // self::minutesForKind(self::kindOfExtension($extension))
public static function kindOf(Episode $episode): string;              // unchanged, except the File arm reads self::kindOfExtension(pathinfo($path, PATHINFO_EXTENSION))

/** 'document', 'image' or 'default' from the extension alone, case-insensitive; today's fromPath() body. */
public static function kindOfExtension(string $extension): string;

private static function minutesForKind(string $kind): int;            // today's :35-37
```

```php
namespace App\Data;

use App\Enums\EpisodeProvider;
use Carbon\CarbonInterface;

/**
 * Where a Peer goes to open a material, or that they cannot yet (D-030).
 *
 * Not a MediaLink, because a pasted link has no expiry — the creator's own
 * sharing governs it (D-025). Not a VendorLink (T-089), whose blocked state
 * is a grant state and whose account hint is T-092's; a material row is
 * released or it is not, and that is the whole question here.
 */
class MaterialLink
{
    public function __construct(
        /** Null exactly when the material is not released yet. */
        public ?string $url,
        public EpisodeProvider $provider,
        /** Set for Qori storage, whose signed URL expires; null for a pasted link. */
        public ?CarbonInterface $expiresAt = null,
        /** The Episode row to send the Peer back to; set exactly when $url is null. */
        public ?string $anchorEpisodeId = null,
        /** The one sentence shown on that row (materials.not_yet, in the Series' Group's words); set exactly when $url is null. */
        public ?string $notice = null,
    ) {}

    /** The signer's answer: url, provider and expiresAt copied. */
    public static function fromMediaLink(MediaLink $link): self;

    /** A pasted URL, followed by the browser and never by Qori. */
    public static function pasted(string $url): self;   // provider EpisodeProvider::Link, no expiry

    /** Listed, not openable yet: no url, the row to land on and the sentence to show there. */
    public static function notReleased(EpisodeProvider $provider, string $episodeId, string $notice): self;

    /** @phpstan-assert-if-true string $this->url */
    public function isReleased(): bool;   // $this->url !== null
}
```

```php
// App\Services\MaterialService — T-130's class; two public methods, one constant and one private method added.
// No vendor import: the signer is the contract, bound in IntegrationServiceProvider.

public function __construct(
    private SignsStoredFiles $signer,
    private LiveSessionService $sessions,
    private ProgressService $progress,
    private Terminology $terminology,
) {}
// If T-130 gives the constructor dependencies of its own, these four are added beside them.

/** The states during which an after_session material stays listed and unopenable (D-026, D-030). */
private const HELD_STATES = [LiveState::Upcoming, LiveState::Open, LiveState::Cancelled];

/**
 * The Open route's answer, for one Peer.
 *
 * The gate is the Series page's (SharedController::show(), :88-127): the
 * Access row is the whole check and its absence is a 403, never a redirect
 * into the page. Then the row, read in the Series' Group because the Peer is
 * in none; then release against the session's computed state; then the
 * brief-only guard; then the two records; then the link. Recording comes before the signer, as
 * PlaybackTicketService::open() records before it resolves — a signer that
 * fails still counts as an open.
 */
public function open(User $peer, string $seriesId, string $materialId, CarbonImmutable $now): MaterialLink;
// $access = Access::forUser($peer)->where('series_id', $seriesId)->first()
//     ?? throw AppException::forbidden('errors.access.not_granted', devMessage: "User {$peer->getKey()} has no active access in series {$seriesId}.");
// $series = $access->grantedSeries()
//     ?? throw AppException::notFound('errors.access.series_unavailable');
// $material = Material::query()->forGroup($series->group)->where('series_id', $series->getKey())->whereKey($materialId)->first()
//     ?? throw AppException::notFound('errors.materials.not_found', devMessage: "Material {$materialId} is not in series {$seriesId}.");   // T-130's line, reused
// $episode = $material->episode_id === null ? null
//     : $series->orderedEpisodes()->first(fn (Episode $candidate): bool => (string) $candidate->getKey() === (string) $material->episode_id);
//
// if (! $this->isReleased($material, $episode, $now)) {
//     return MaterialLink::notReleased($material->provider, (string) $material->episode_id, $this->terminology->line('materials.not_yet', [], $series->group));
// }
//
// if ($material->isLink() && $material->url() === null) {      // a brief-only homework row: the brief and the due date are the homework, and there is nothing to open
//     throw AppException::notFound('errors.materials.unavailable', devMessage: "Material {$material->getKey()} is a brief-only homework row with no destination.");
// }
//
// AccessOpen::record($access, OpenTarget::Material, $material->episode_id, (string) $material->getKey());
//
// if ($episode instanceof Episode) {
//     $this->progress->opened($access, (string) $episode->getKey());
// }
//
// return match ($material->provider) {
//     EpisodeProvider::CloudflareR2 => $this->signed($material, $series),
//     EpisodeProvider::Link => MaterialLink::pasted((string) $material->url()),   // non-null: the brief-only guard above
//     default => throw AppException::unsupported(
//         'errors.playback.unsupported_provider',
//         ['provider' => $material->provider->value],
//         devMessage: "No Peer-side open for material provider '{$material->provider->value}' yet.",
//     ),
// };

/**
 * Whether Qori lists this material as openable now (D-030).
 *
 * Only an after_session row on a live Episode is ever held, and only while
 * the session's computed state is one of HELD_STATES. Shared with
 * SharedController::show(), so the page and the route cannot disagree.
 */
public function isReleased(Material $material, ?Episode $episode, CarbonImmutable $now): bool;
// return $material->release !== MaterialRelease::AfterSession
//     || ! $episode instanceof Episode
//     || ! $episode->isLive()
//     || ! in_array($this->sessions->stateFor($episode, $now), self::HELD_STATES, true);

/** The signed link for a Qori-hosted row, with the window its extension earns. */
private function signed(Material $material, Series $series): MaterialLink;
// $asset = $this->storedAsset($material, $series);
// return MaterialLink::fromMediaLink(
//     $this->signer->temporaryLink((string) $asset->key, MediaLifetime::minutesForExtension($asset->extension)),
// );

/**
 * The asset behind a Qori-hosted row, or a 404 — never a link to an object
 * that is not there. forGroup(), not the relation: MediaAsset is
 * BelongsToGroup and the Peer surface has no current Group (the trap
 * Access::grantedSeries() documents, app/Models/Access.php:226-241).
 */
private function storedAsset(Material $material, Series $series): MediaAsset;
// $asset = MediaAsset::query()->forGroup($series->group)->whereKey($material->media_asset_id)->first();
// if (! $asset instanceof MediaAsset || ! $asset->isStored() || $asset->key === null) {
//     throw AppException::notFound('errors.materials.unavailable', devMessage: "Material {$material->getKey()} points at asset {$material->media_asset_id}, which is not stored.");
// }
// return $asset;
```

```php
namespace App\Http\Controllers\Shared;

/**
 * The access-gated way to one material (D-030), by redirect (T-089's shape).
 *
 * Qori never proxies the bytes: a pasted link goes where the creator
 * pointed, a Qori-hosted file goes to a signed URL, and a row not released
 * yet goes back to its Episode on the Series page with one sentence (D-020).
 */
class OpenMaterialController extends Controller
{
    public function __construct(private MaterialService $materials) {}

    public function __invoke(Request $request, string $seriesId, string $materialId): RedirectResponse;
    // $link = $this->materials->open(CurrentUser::orFail($request), $seriesId, $materialId, CarbonImmutable::now());
    //
    // if (! $link->isReleased()) {                                   // D-020: back to the row, never a page of its own
    //     Inertia::flash('toast', ['type' => 'info', 'message' => (string) $link->notice]);   // resolved by the Service; the controller reads nothing
    //
    //     return redirect()->to(route('shared.show', $seriesId).'#episode-'.$link->anchorEpisodeId);
    // }
    //
    // return redirect()->away($link->url);
}
```

```php
// App\Http\Controllers\Shared\SharedController::show(Request $request, string $series, LiveSessionService $live, Terminology $terminology, MaterialService $materials): Response
// — T-125's signature with a fifth parameter by method injection; three more props, one more key per Episode.

$now = CarbonImmutable::now();
$byEpisode = $this->materialsByEpisode($model, $materials, $now);

// inside the episodes map (:134-142):
'materials' => $byEpisode[(string) $episode->getKey()] ?? [],

// beside 'progress':
'groupTimezone' => $model->group?->timezone() ?? Timezones::fallback(),   // the same value T-125 sends per live row
'materialCopy' => [
    'roles' => [                                                   // T-130's labels, reused
        'preparation' => __('materials.roles.preparation'),
        'material' => __('materials.roles.material'),
        'homework' => __('materials.roles.homework'),
    ],
    'open' => __('materials.peer.open'),
    'afterSession' => __('materials.peer.after_session'),
    'due' => __('materials.due_prefix'),                           // T-130's, reused
    'linkManaged' => $terminology->line('materials.peer.link_managed', [], $model->group),
],

/**
 * Every Episode-level material of the Series in one read, keyed by Episode id.
 *
 * @return array<string, list<array<string, mixed>>>
 */
private function materialsByEpisode(Series $series, MaterialService $materials, CarbonImmutable $now): array;
// $episodes = $series->orderedEpisodes()->keyBy(fn (Episode $episode): string => (string) $episode->getKey());
//
// return Material::query()
//     ->forGroup($series->group)
//     ->where('series_id', $series->getKey())
//     ->whereNotNull('episode_id')
//     ->orderBy('position')
//     ->get()
//     ->groupBy(fn (Material $material): string => (string) $material->episode_id)
//     ->map(fn (Collection $rows, string $episodeId): array => $rows->map(fn (Material $material): array => [
//         'id' => (string) $material->getKey(),
//         'title' => $material->title,
//         'role' => $material->role->value,
//         'provider' => $material->provider->value,
//         'release' => $material->release->value,
//         'isReleased' => $materials->isReleased($material, $episodes->get($episodeId), $now),
//         'isOpenable' => $material->url() !== null || $material->provider === EpisodeProvider::CloudflareR2,   // false for a brief-only homework row
//         'note' => $material->note,
//         'dueAt' => $material->due_at?->toIso8601String(),
//     ])->values()->all())
//     ->all();
```

```ts
// resources/js/components/series/PeerMaterialList.vue
import SessionTime from '@/components/series/SessionTime.vue';
import { open as openMaterial } from '@/routes/shared/materials'; // Wayfinder, from the route name

export interface PeerMaterial {
    id: string;
    title: string;
    role: 'preparation' | 'material' | 'homework';
    provider: string; // 'cloudflare_r2' | 'link' this sprint
    release: 'with_episode' | 'after_session';
    isReleased: boolean;
    isOpenable: boolean; // false for a brief-only homework row: provider link, no url
    note: string | null;
    dueAt: string | null; // ISO 8601 with offset; homework only
}

export interface PeerMaterialCopy {
    roles: Record<PeerMaterial['role'], string>;
    open: string;
    afterSession: string;
    due: string;
    linkManaged: string;
}

defineProps<{
    seriesId: string;
    materials: PeerMaterial[];
    groupTimezone: string;
    copy: PeerMaterialCopy;
}>();
```

Rendering rules for `PeerMaterialList.vue`, in order: three groups —
`preparation`, `material`, `homework` — each headed by `copy.roles[role]` and
rendered only when it has rows, rows in the order given (already `position`
order). A row whose `isOpenable` is false — a brief-only homework row — shows
its title and brief and nothing where the control would be, released or not,
because there is no destination. Otherwise a released row's control is
`<a :href="openMaterial.url([seriesId, material.id])" target="_blank" rel="noopener">{{ copy.open }}</a>`;
an unreleased row shows its title as text and `copy.afterSession` where the
control would be, with no link. `note` renders under the title with
`whitespace-pre-line`. A row with `dueAt` shows `copy.due` followed by
`<SessionTime :starts-at="material.dueAt" :group-timezone="groupTimezone" />`.
A `link` row shows `copy.linkManaged` as its secondary line. Nothing else is
said; there is no empty state, because the page mounts the list only when
the row has materials.

`resources/js/pages/shared/Show.vue`: `GrantedEpisode` (`:16-24` today) gains
`materials: PeerMaterial[]`; the props gain `groupTimezone: string` and
`materialCopy: PeerMaterialCopy`; inside each row's `<div v-for="episode …">`,
after the row's controls and after `T-125`'s `<LiveSessionCard>` where one is
mounted, one line:
`<PeerMaterialList v-if="episode.materials.length" :series-id="series.id" :materials="episode.materials" :group-timezone="groupTimezone" :copy="materialCopy" />`.

`routes/shared.php`: one `Route::get(...)` inside the existing group, with a
comment in the file's voice — ids, as every Peer route; the gate is the
access row; the release check is `MaterialService`'s.

`docs/flows/materials.md`, "Opening, from the Peer's side": the chain
`shared.materials.open` → `OpenMaterialController` → `MaterialService::open()`
(gate, `forGroup()` read, `isReleased()`, `AccessOpen::record()`,
`ProgressService::opened()`, `SignsStoredFiles` or the pasted URL) → 302;
the not-released redirect to `shared.show#episode-{id}`; the 404 for a file
that never arrived and for a brief-only homework row. `docs/flows/storage.md`, "How long a link lives depends
on what it points at": one sentence that a material's stored extension is
consulted the same way, and `SignsStoredFiles` named beside `ResolvesMedia`
as the second thing `CloudflareR2Storage` implements. `docs/tinker/accesses.md`,
"The peer surface crosses groups":
`app(App\Services\MaterialService::class)->open($peer, $series->id, $material->id, Carbon\CarbonImmutable::now())->url;`
with the no-context note the section already makes.

## Copy

| Key                                       | File                    | English                                                                               |
| ----------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------- |
| `materials.peer.open`                     | `lang/en/materials.php` | Open                                                                                  |
| `materials.peer.after_session`            | `lang/en/materials.php` | Shown after the session                                                               |
| `materials.peer.link_managed`             | `lang/en/materials.php` | A link the :creator manages — it opens on their side.                                 |
| `materials.not_yet`                       | `lang/en/materials.php` | That's shown after the session. The rest of this :episode is below.                   |
| `errors.materials.unavailable.message`    | `lang/en/errors.php`    | That material isn't here any more.                                                    |
| `errors.materials.unavailable.resolution` | `lang/en/errors.php`    | Whoever shared it may have taken it down. Go back to the page — what's left is there. |

The role headings and the "Due" prefix are `T-130`'s `materials.roles.*` and
`materials.due_prefix`, read with `__()` — this task adds no second line for
either. `open` and `after_session` carry no noun and are read with `__()`.
`link_managed` and `not_yet` carry one and go through `Terminology::line()`
with the Series' Group (`Vocabulary::KEYS`, `app/Data/Vocabulary.php:23`,
includes `creator`). `after_session` is `D-030`'s exact wording — never
"available after". Two error lines serve the route: a material id that is not
in the Series answers `T-130`'s `errors.materials.not_found`, and a row with
nothing behind it — a Qori-hosted file that never arrived, or a brief-only
homework row — answers the new `errors.materials.unavailable`, which is
noun-free so the Service can throw it without a Group in hand. Nothing here
sits under `live.*`, and nothing names a vendor.

## Routes

| Verb | Path                                             | Name                    | Action                                    |
| ---- | ------------------------------------------------ | ----------------------- | ----------------------------------------- |
| GET  | `/shared/{seriesId}/materials/{materialId}/open` | `shared.materials.open` | `Shared\OpenMaterialController::__invoke` |

Inside the existing `auth`, `verified`, `shared.` group
(`routes/shared.php:31-34`), beside `T-125`'s `shared.episodes.show` and
`T-089`'s `shared.episodes.open`. Ids, as every Peer route
(`routes/shared.php:21-25`). Nothing else changes.

## Tests

**New: `tests/Feature/Shared/OpenMaterialTest.php` — 18 cases**
(`RefreshDatabase`; `Http::preventStrayRequests()` in `setUp`; a private
`scene()` building a Brisbane Group on `start`, a Series with one live
Episode two hours ahead and 60 minutes long and one File Episode, published,
and a Peer granted through `AccessService::grant()`; `material()` adding a row
through `MaterialService::add()`; `storedAsset()` as under Preconditions;
`toastContains()` as `tests/Feature/Access/SeriesAccessCodeTest.php:87-90`)

1. `test_a_link_material_redirects_to_its_url` — a `link` row with
   `https://docs.google.com/presentation/d/abc/edit`; the GET is 302 with that
   `Location`; no request leaves.
2. `test_a_qori_hosted_material_redirects_to_a_signed_link_that_lives_as_long_as_a_document`
   — a `cloudflare_r2` row on a stored `.pdf`; the 302's `Location` contains
   the asset's key; `MaterialService::open()` called directly answers a
   `MaterialLink` whose `expiresAt` is at most
   `config('qori.storage.link_ttl.document')` minutes away.
3. `test_an_after_session_material_is_held_while_the_session_is_ahead` — an
   `after_session` row on the live Episode; the GET redirects to
   `route('shared.show', $seriesId).'#episode-'.$episodeId`;
   `assertSessionHas(SessionKey::FLASH_DATA, …)` sees an `info` toast whose
   message is `materials.not_yet` with the Group's `:episode`; no
   `access_opens` row; `hasOpened()` false.
4. `test_an_after_session_material_stays_held_while_the_session_is_open` —
   `$this->travelTo($startsAt->addMinutes(10))`; still the anchor redirect.
5. `test_an_after_session_material_opens_once_the_join_window_has_closed` —
   `$this->travelTo($endsAt->addMinutes(config('qori.live.join_closes_after_minutes') + 1))`;
   302 to the url.
6. `test_a_with_episode_material_on_a_live_episode_opens_before_the_session`
   — the default release; 302 to the url two hours ahead.
7. `test_someone_without_access_gets_a_forbidden_page_not_a_redirect` —
   403; sees `errors.access.not_granted.message`.
8. `test_a_revoked_access_gets_a_forbidden_page` — `AccessService::revoke()`,
   then 403.
9. `test_a_material_from_another_groups_series_is_not_found` — a second
   Group's Series and material; the Peer, granted only the first, requests
   the first Series' id with the second's material id → 404 with
   `errors.materials.not_found.message` (`T-130`'s line); the second Series'
   id with either material → 403.
10. `test_a_guest_is_sent_to_sign_in` — redirect to the sign-in page.
11. `test_opening_writes_an_access_open_and_marks_the_episode_opened` — an
    `access_opens` row with `target` material, the Access's id, the Episode's
    id, `subject_id` the material's id and `group_id` the Access's group;
    `$access->fresh()->hasOpened($episodeId)`; `last_activity_at` set.
12. `test_a_material_whose_file_never_arrived_is_not_found` — a
    `cloudflare_r2` row added through `MaterialService::add()` with a stored
    asset (`add()` refuses one that is not, `errors.materials.asset_not_found`),
    then `$asset->forceFill(['status' => MediaAssetStatus::Pending, 'key' => null])->save()`;
    404 with `errors.materials.unavailable.message`; no `access_opens` row.
13. `test_the_shared_page_lists_each_episodes_materials_with_their_release`
    — Inertia: `series.episodes.0.materials` has 2; `…0.isReleased` true and
    `…1.isReleased` false for the `after_session` row; `groupTimezone` is
    `Australia/Brisbane`; `materialCopy.afterSession` equals
    `__('materials.peer.after_session')`.
14. `test_a_homework_row_carries_its_brief_and_due_date_as_an_instant` — a
    `homework` row with a `note` and a `due_at`; the prop's `note` is the
    brief and `dueAt` is ISO 8601 with offset equal to the stored instant
    (the Peer's zone is the browser's, `SessionTime.vue`).
15. `test_the_public_page_and_a_preview_episode_carry_no_material` — the
    File Episode made `is_preview` with a `link` material; `GET
route('series.public', …)` `->assertInertia(fn ($page) => $page->missing('series.episodes.0.materials'))`
    and the body contains neither the material's title nor its URL.
16. `test_the_flash_uses_the_groups_own_word_for_episode` —
    `config()->set('qori.plans.start.'.Terminology::ENTITLEMENT, true)` and
    the Group created with `'settings' => [Terminology::SETTINGS_KEY => …]`
    carrying `episode => Practice`, as `tests/Feature/TerminologyTest.php:89-91`
    writes it (the labels are its `customLabels()`, `:36-45`); a held row's
    toast contains "Practice" and not "Episode".
17. `test_one_episode_mixes_a_qori_pdf_and_a_slides_link` — owner
    acceptance 10: both rows on one Episode; each GET lands on its own
    destination; the Slides row is stored `provider = link`.
18. `test_a_brief_only_homework_row_has_no_open_and_answers_not_found` — a
    `homework` row with `provider = link` and `content = '[]'`, built with
    `T-130`'s factory —
    `Material::factory()->forEpisode($episode)->homework()->state(['group_id' => $group->getKey(), 'content' => []])->create()`
    — because it is the reconciliation's brief-only row and no form builds
    it; the Inertia prop's `isOpenable` is false for it and true for a `link`
    row with a url and for a `cloudflare_r2` row; the GET is 404 with
    `errors.materials.unavailable.message`; no `access_opens` row and
    `hasOpened()` false.

**Changed:**

- `tests/Feature/Storage/MediaLifetimeTest.php` — 2 cases added:
  `test_an_extension_alone_gets_the_same_window_as_an_episode`
  (`minutesForExtension('pdf')` 3, `('png')` 10, `('sketch')` 10, each equal
  to `minutesFor()` of a File Episode with that path) and
  `test_an_extension_is_matched_regardless_of_case` (`'PDF'` → `document`,
  3). The six existing cases are untouched; `kindOf()` keeps its answers.

`tests/Feature/Storage/PlaybackTest.php` is not changed:
`test_a_qori_hosted_file_resolves_to_a_link` (`:56-69`) covers `linkFor()`
after the delegation as it is.

Total: 20 new cases.

## Acceptance

- [ ] On `/shared/{seriesId}`, each Episode row lists its materials under
      Preparation, Material and Homework, and a Peer with access opens a
      Qori-hosted PDF and a Slides link from one row, each in a new tab, and
      lands on the file and on Slides (owner acceptance 10)
- [ ] An `after_session` material reads "Shown after the session" with no
      link until the join window has closed, then opens; its address opened
      early lands on the Series page at that Episode with the
      `materials.not_yet` toast, never a page of its own (`D-020`)
- [ ] A homework row shows its brief and "Due" with the date in the Peer's
      own zone and the Group's zone beside it, at mobile and desktop widths,
      with the two zones at least eight hours apart (owner acceptance 2); a
      brief-only homework row shows its brief and due date and no Open
- [ ] No access, a revoked Access, another Group's material, a guest and a
      file that never arrived each meet the answer the tests name; the
      public page and a preview Episode show no material (owner acceptance 11)
- [ ] Every open writes `access_opens` with the Access's `group_id` and marks
      the Episode opened; nothing in `ProgressService::hasFinished()`,
      `completed_episode_ids` or certificates changes (owner acceptance 12)
- [ ] `docs/flows/materials.md` describes the open chain, and
      `docs/flows/storage.md` names `SignsStoredFiles` beside `ResolvesMedia`
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~`T-125` `ready`, so `LiveState`, `LiveSessionService::stateFor()`,
  `AccessOpen::record()`, `OpenTarget::Material`, the `#episode-{id}` anchors
  and `SessionTime.vue`'s `groupTimezone` prop are frozen names this task can
  cite by file and line — anyone's.~~ **Answered 21 September 2026:** `T-125`
  is `ready`, so those names are frozen and this spec cites them as written
  there.

## Re-scope log

None.

## Notes

`T-130`'s draft is read here for four names: `Material` (`HasUlids`,
`BelongsToGroup`) with an `asset(): BelongsTo` relation this task never
calls from the Peer surface, and `url()`, which the Link arm of `open()`
reads; `MaterialService` and its constructor, which gains `SignsStoredFiles`,
`LiveSessionService`, `ProgressService` and `Terminology` here;
`lang/en/materials.php`, which `T-130` creates with the creator's copy and
this task extends under `peer`; and `docs/flows/materials.md`, whose
creator-side chain `T-130` writes and this task adds "Opening, from the
Peer's side" to. If `T-130` spells any of these differently, this file follows
it at the wording tier.

`T-130`'s Decision that a homework with neither a link nor a file is not a row
this sprint is superseded by the sprint brief's reconciliation of 18 September
2026, for both tasks: a brief-only `homework` row is `provider = link` with
`content = '[]'`, the check constraint admits it, and this task lists it with
no Open control and answers its address with `errors.materials.unavailable`
before anything is recorded.

`groupTimezone` reaches the page twice once `T-125` and this task have both
landed: `T-125` sends it per live row as `live.groupTimezone`, and this task
sends it once at page level, both from `Group::timezone()`. The page-level
prop is the canonical one — a homework on a non-live Episode has no live row
to read it from — so `LiveSessionCard.vue` may read the page-level prop
instead of its own once both are in, and `T-132` and `T-133` read the
page-level one rather than add a third.

The merged reference (`docs/planning/course-classroom.md`) had the route send
an inactive Access back to the Episode row with a flash. This task follows the
brief and `SharedController::show()` instead: no active Access is a 403, and
the redirect is for release alone. A revoked Peer who follows a saved link
meets the same page the Series page gives them.

`MediaAssetFactory::stored()` writes an `episodes/` key
(`database/factories/MediaAssetFactory.php:40-47`). The tests pass a
`materials/` key explicitly rather than adding a factory state, because
`T-130` may add one and two states for one shape is a merge.

`docs/flows/storage.md:98-104` "Not built yet" still lists progress tracking
as unbuilt. `T-089` edits that file's "Getting to the media" and `T-123`
fixes `series.md`'s stale paragraph; this task touches only the lifetime
section and leaves that line to `T-089`'s owner.

`SharedController::show()` gains a fifth parameter by method injection,
`MaterialService $materials`, after `T-125`'s `LiveSessionService $live` and
`Terminology $terminology`, and reads the vocabulary through that
`$terminology` rather than `app()`. `T-125` and `T-126` edit the same method
before this task, and `T-125` keeps the controller's constructor empty for
this task and `T-132`; the stream's claim order (`streams/classroom.md`)
serialises the edits.

`T-126`'s report (26 September 2026): past `open`, `stateFor()` reads the
Episode's recordings, which are group-scoped, so a call with no current
Group throws — and `isReleased()` calls it from the Peer surface, which has
none. Both callers, `SharedController::show()`'s list and
`MaterialService::open()`, read it inside
`CurrentGroup::runFor($series->group, …)`, as `liveCard()` and
`PlaybackTicketService::watch()` do, and ask `isScheduled()` first, because
`stateFor()` throws for a live row with no start (`T-125`).
