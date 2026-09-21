---
id: T-139
title: Qori storage counts a Series' total, not only each file
stream: classroom
status: draft
owner: unassigned
estimate: S
depends: T-130
blocks: none
---

# T-139 — Qori storage counts a Series' total, not only each file

> **Draft.** Specified to the method name, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). The one thing it waits on is at the
> bottom. Written on 18 September 2026 from `D-030` and the owner's answer of
> 6 September 2026.

## Why

Qori's storage has one cap and it is per file. `UploadService::guardSize()`
(`app/Services/UploadService.php:182-201`) compares each upload with
`config('qori.storage.max_upload_mb.{plan}')`, whose own comment says "Per
file, not per group" (`config/qori.php:110-111`), and nothing anywhere adds
files up. The owner answered on 6 September 2026 that 100 MB is the
whole-course limit across every paid tier, not a per-file one
(`docs/planning/product-and-pricing.md:272`), and the same note recorded why
it could not be built then (`:286-290`): `media_assets` carries `group_id` and
`purpose` and nothing tying a file to a Series
(`database/migrations/2026_09_08_000000_create_qori_schema.php:162-177`).
`T-130` changes that. A material row points at its file through
`materials.media_asset_id` and at its Series through `materials.series_id`,
which `D-030` names as "the first way an upload is addressable for deletion
and totals".

Afterwards, each plan's per-Series total sits in
`config('qori.storage.series_total_mb')` beside the per-file cap. Signing a
material upload refuses a file that would take the Series past it, before
any signed URL exists, and creating the material row refuses again against
the size the bucket reported, because the size a browser declares is a claim
(`docs/flows/storage.md:190-193`). The creator's material form says how much
the Series is using against the total before they pick a file, and a refusal
says where the file belongs instead: on their own drive, added as a link
(`D-025`). The per-file caps stay as they are (`D-030`), and the Free plan's
figure is the one thing this task waits on.

## Decisions taken to make this specifiable

**The key is `qori.storage.series_total_mb`, per plan, in `config/qori.php`,
and this task declares it.** `T-123` declares every `qori.live`,
`qori.materials` and `qori.chats` key and says in its own words that
"`storage.series_total_mb` is not declared — its Free figure is the owner's
(`T-139`)" (`T-123`, "Decisions"), so this is one of the stream's declared
exceptions to "`config/qori.php` is `T-123`'s", beside `T-125`'s reachability
row and `T-138`'s plan key; `streams/classroom.md:153` already carries all
three, in claim order. The shape is `max_upload_mb`'s
(`config/qori.php:112-117`), a plan slug to a number, so the two caps are
read the same way and sit together. A `null` value is no total, as `null`
already means unlimited under `qori.plans` (`config/qori.php:282`); a plan the
list does not name reads the default plan's, as `guardSize()` does for the
per-file cap (`UploadService.php:184-185`). Each cap gets one reader on
`Group` — `seriesStorageMb()` new, `maxUploadMb()` moved out of
`guardSize()` — so the guard and the page cannot disagree about a number.

**The total is the sum of `media_assets.size_bytes` over stored assets that a
material row of this Series points at, and nothing else.**
`Series::materialBytes()` computes it with a `whereIn` subquery rather than a
join: both models carry `BelongsToGroup`, whose scope adds an unqualified
`where('group_id', …)` (`app/Models/Scopes/GroupScope.php:24`) and whose
`forGroup()` adds the same column unqualified
(`app/Concerns/BelongsToGroup.php:52-57`), so a join between two such tables
is an ambiguous column. Both queries read with `forGroup($this->group_id)`,
so the method answers with or without a current Group. Pending assets never
count (their bytes may never arrive), link materials have no asset, a
brief-only homework row has none either, and Series-level rows (`episode_id`
null, reached by `T-137`) count the same as Episode-level ones because both
carry `series_id`. An Episode's own primary file — `content['path']` on a
`cloudflare_r2` Episode (`D-024`) — has no row pointing at it and is not
counted; that is a gap recorded under Notes, not a rule.

**The guard runs twice, in one trait, for the same reason the per-file cap
does.** `sign()` checks with the size the browser declared, so that no signed
URL is issued for a file that cannot fit; `MaterialService::add()` checks
again with the size `confirm()` read back from the bucket, because R2
enforces nothing at the edge and the declared size decides only whether to
sign (`docs/flows/storage.md:190-193`). Without the second check a client
declaring one byte could put a 500 MB deck on a Series whose total is 100,
and an asset signed against one Series' total could be attached to a fuller
Series in the same Group, because `media_assets` still carries no
`series_id`. Both checks are `guardSeriesStorage()` on a new
`App\Concerns\CapsSeriesStorage` trait, the way `LocksOverCapSeries` gives
`guardSeriesUnlocked()` to more than one Service
(`app/Concerns/LocksOverCapSeries.php:48`).

**A row the total refuses discards its object before the throw.** By the
time `add()` runs, `confirm()` has promoted the object under `materials/`
and the R2 lifecycle rule covers only the incoming prefix
(`config/qori.php:127-131`), so a refused row would leave a stored object no
page can reach and nothing ever collects. `MaterialService::discardAsset()`
deletes the object, then its `media_assets` row, logged and swallowed on
failure exactly as `T-130`'s `deleteObject()` is and for the same reason; the
form's hidden `media_asset_id` then meets `T-130`'s `asset_not_found`, whose
copy already says to choose the file again. A retry is a fresh upload, which
is what `errors.upload.type_mismatch` already says of a refused confirm.

**A material upload names its Series at signing.** `SignUploadRequest` gains
`series_id`, required when `purpose` is `material` and not read otherwise;
`UploadController::sign()` resolves it with `seriesById()` from
`ResolvesShareSeries`, which is scoped to the current Group so another
tenant's id is simply not found (`app/Concerns/ResolvesShareSeries.php:36-39`);
`UploadService::sign()` takes it as a nullable `Series` after `$purpose`. An
Episode upload sends nothing new and behaves as it does today. `uploadFile()`
and `FileUpload.vue` carry the id as an argument and a prop;
`MaterialForm.vue` supplies it from a `seriesId` prop that `MaterialList.vue`
passes through from `T-130`'s mount in `share/series/Show.vue`, where
`props.series.id` is already in hand (`:173-190`).

**It is a plan-limit refusal whose resolution never says upgrade.**
`AppException::planLimitReached()` and `errors.upload.series_total`, the same
code and status as the per-file cap (`UploadService.php:195-199`;
`ErrorCode::PlanLimitReached` is a 403, `app/Exceptions/ErrorCode.php:35`).
`T-130` chose `invalidRequest` for `materials.per_episode`, and its reason
does not carry over: that cap is one number with no plan key, so
`plan_limit_reached` would name a plan where none is involved. This total is
read from `series_total_mb.{plan}` exactly as `max_upload_mb.{plan}` is, the
Free figure is the owner's and may sit below the paid plans' (the one open
question below), and a plan whose value is `null` is never refused at all —
so which plan a Group is on decides whether and where the guard fires, and
the public code says so. The two guards sit in one Service, read config of
one shape and answer one status, which is what lets `uploads.ts` show either
refusal the same way. The upgrade the code's name implies is never written:
the total is the same on every paid plan — "a wall, not a ladder"
(`product-and-pricing.md:291`) — so the resolution's only honest next step is
the creator's own drive and a link (`D-025`), or removing a file, and
`plan_limit_reached`'s default copy (`lang/en/errors.php:59-62`) is not
reached because the key is always given. `:total` is interpolated from
config, and `:series` comes through the Group's vocabulary passed in
`$replace`, as `EpisodeService::guardLiveSessionTime()` passes it
(`app/Services/EpisodeService.php:90-96`), because
`AppException::publicMessage()` reads a line with plain `__()`
(`app/Exceptions/AppException.php:179-186`).

**The running total rides on `T-130`'s page props, as two lang lines and two
numbers.** `T-130` has `SeriesController::show()` resolve every
`materials.*` line through `materialsCopy()` into `materials.copy` and put
the caps in `materials.limits`. This task adds `storage.used` and
`storage.used_no_total` to `lang/en/materials.php`, gives `materialsCopy()`
the `used` and `total` replacements, and adds `seriesMb` and `usedBytes` to
`materials.limits`; `MaterialForm.vue` shows `copy.storage.used` when
`limits.seriesMb` is a number and `copy.storage.used_no_total` otherwise. The
sentence is rendered on the server because it names the Series noun; the
no-total line states usage only, because `T-130`'s `materials.file_help`
beside it already names the per-file limit, and `D-030` wants that limit
said and "unlimited" never. The numbers refresh with the page after each
material is saved, which is when the total moves. No new inline English in
Vue, and no new page-level prop.

**`uploads.ts` reads the refusal from where `AppException` puts it.**
`post()` throws `payload?.message` (`resources/js/lib/uploads.ts:59-63`), but
an `AppException` answers `{ error: { code, message, resolution } }`
(`app/Exceptions/AppException.php:251`, `:306-321`), so every service refusal
at signing — the per-file cap included — has shown the fallback "That upload
could not be completed." rather than its own copy. The message and the
resolution are joined and thrown, so the drive suggestion is what the creator
reads under the file button. The existing fallback string stays: it is §13's
unwired i18n, and this task adds no inline English beside it.

**Nothing changes for Episode uploads, and no per-file number moves.**
`product-and-pricing.md:141` proposed one fixed per-file number in place of
the plan ladder; `D-030` says the per-file caps are unchanged and the total
is this task's. So a 200 MB file on Start is refused by the total with the
total's message, and the per-file ladder is left for the owner.

## Preconditions

**Data this task verifies against:** a clean database. The tests build a
Group on the `start` plan with its owner as a collaborator, one Series and
two Episodes through the factories, `SeriesService::create()` and
`EpisodeService::add()` (the shape of
`tests/Feature/Series/EpisodeRoutesTest.php:35-55`); stored files through
`MediaAsset::factory()->stored()` with `purpose` `material` and a chosen
`size_bytes`; and material rows through `T-130`'s `MaterialFactory`
(`forEpisode()`, `qoriHosted()`) or `MaterialService::add()` inside
`CurrentGroup::runFor()`. `Storage::fake((string) config('qori.storage.disk'))`
in `setUp`, as `T-130`'s `MaterialsTest` does. Nothing is PUT to a signed URL
here — case 7 writes its object to the fake disk directly — so the real
`local` disk `UploadTest` needs (`tests/Feature/Share/UploadTest.php:18-33`)
is not involved.

**Equipment:** none. The line on the form and the refusal under the file
button are asserted as props and JSON; a browser only confirms what the tests
already say.

**Spike:** none owed. This task calls no vendor and reads no vendor payload.

## Scope

**In:**

- `qori.storage.series_total_mb` per plan; `Group::seriesStorageMb()` and
  `Group::maxUploadMb()`; `Series::materialBytes()`.
- `CapsSeriesStorage::guardSeriesStorage()`, called by
  `UploadService::sign()` for a material upload and by
  `MaterialService::add()` for a Qori-hosted material, with
  `discardAsset()` on the second refusal.
- `series_id` on the sign request, resolved in the current Group; the
  `Series` parameter on `sign()`; the id carried by `uploadFile()`,
  `FileUpload.vue`, `MaterialList.vue` and `MaterialForm.vue`.
- `materials.limits.seriesMb`, `materials.limits.usedBytes` and the two
  `materials.copy.storage.*` lines on the creator's Series page, shown on
  `MaterialForm.vue`; `T-130`'s inline per-file read in the controller
  becomes `Group::maxUploadMb()`.
- `uploads.ts` reading an `AppException`'s message and resolution.
- `errors.upload.series_total`, `errors.upload.series_required`, the two
  `materials.storage.*` lines, the flow and tinker paragraphs.

**Out:**

- The Free plan's figure: the draft ships `null` for `free`, and the owner's
  number replaces it before this is `ready` (`D-030`).
- Counting an Episode's own `content['path']` file, or any Episode upload,
  in the total; the rule is materials-only this sprint, because `D-024` keeps
  the primary item outside `materials`. Recorded under Notes.
- Any change to `max_upload_mb` or `allowed_uploads`, and the
  `odt`/`ods`/`odp`/`epub` question, which is the owner's (`D-030`).
- A total across a Group. The number the owner chose is per Series — "per
  course", in that note's older vocabulary — and not per Group
  (`product-and-pricing.md:272`); storage as a plan lever was rejected the
  same day, because metering storage contradicts "their files stay theirs"
  (`:141-145`, `:291-293`).
- Freeing space. Removal is `T-130`'s `MaterialService::remove()` and already
  deletes the object; this task only makes the total fall with it.
- Series-level material rows and reorder (`T-137`); they count when they
  exist, and nothing here creates one.
- Chat QR images (`MediaAssetPurpose::ChatCode`, `T-132`): not materials,
  not counted; `qori.chats.code_max_mb` is their cap.
- A sweep for stored assets no row points at. `discardAsset()` stops this
  task's own path from leaving one; a sweep for any other cause is not
  built.
- Anything on the Peer's page. Peers never see a creator's storage.

## Files

| Path                                              | Change | Notes                                                                                                                      |
| ------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------- |
| `config/qori.php`                                 | edit   | `storage.series_total_mb` beside `max_upload_mb`, with its comment; the one storage key `T-123` leaves to this task        |
| `app/Concerns/CapsSeriesStorage.php`              | new    | `guardSeriesStorage(Series, int)`                                                                                          |
| `app/Models/Group.php`                            | edit   | `seriesStorageMb(): ?int`, `maxUploadMb(): int`                                                                            |
| `app/Models/Series.php`                           | edit   | `materialBytes(): int`                                                                                                     |
| `app/Services/UploadService.php`                  | edit   | `sign()` takes `?Series $series`; the guard for `purpose` material; `guardSize()` reads `Group::maxUploadMb()`             |
| `app/Services/MaterialService.php`                | edit   | `add()` guards with the confirmed size before the insert; `discardAsset()` (`T-130`'s file)                                |
| `app/Http/Requests/Share/SignUploadRequest.php`   | edit   | `series_id`, required for a material; its `messages()` entry                                                               |
| `app/Http/Controllers/Share/UploadController.php` | edit   | resolves the Series with `seriesById()` and hands it to `sign()`                                                           |
| `app/Http/Controllers/Share/SeriesController.php` | edit   | `materials.limits` gains `seriesMb`, `usedBytes`; `materialsCopy()` gains `used`, `total`; `$fileMb` reads `maxUploadMb()` |
| `resources/js/lib/uploads.ts`                     | edit   | `seriesId` argument; reads `error.message` and `error.resolution`                                                          |
| `resources/js/components/FileUpload.vue`          | edit   | `seriesId?: string` prop with `seriesId: undefined` in the defaults, passed through                                        |
| `resources/js/components/series/MaterialList.vue` | edit   | `seriesId` prop, passed to `MaterialForm` (`T-130`'s component)                                                            |
| `resources/js/components/series/MaterialForm.vue` | edit   | `seriesId` prop; `series-id` on `FileUpload`; the storage line (`T-130`'s component)                                       |
| `resources/js/pages/share/series/Show.vue`        | edit   | `:series-id="series.id"` on `T-130`'s `MaterialList` mount, one attribute                                                  |
| `lang/en/errors.php`                              | edit   | `upload.series_total`, `upload.series_required`                                                                            |
| `lang/en/materials.php`                           | edit   | `storage.used`, `storage.used_no_total` (`T-130`'s file)                                                                   |
| `docs/flows/storage.md`                           | edit   | "The three calls" gains the guard; "Size is checked after the upload" gains the material row                               |
| `docs/flows/materials.md`                         | edit   | the second check and the discard in `add()`; the total leaves its "Not built yet" line (`T-130`'s file)                    |
| `docs/tinker/uploads.md`                          | edit   | the material `sign()` call gains `$series`; "Watch the guards fire" gains the total                                        |
| `tests/Feature/Share/SeriesStorageTotalTest.php`  | new    | 9 cases                                                                                                                    |

No route, factory or seeder row: the sign route gains a field, not a path
(`routes/share/uploads.php:17`); no column is added; `DesignReviewSeeder`
seeds no Qori-hosted material (`T-130`'s two are links), so nothing there
counts. `qori:reachability` sees nothing new, because no GET is added.

## Database

None. The total is computed from `materials.media_asset_id` and
`media_assets.size_bytes`, both present once `T-130` lands; nothing is
stored.

## Code

```php
// config/qori.php — under 'storage', directly after 'max_upload_mb' (:112-117)
/*
| Per Series, across every file a material row points at. The owner's
| answer of 6 September 2026: 100 MB on every paid plan, the same number
| on each — a wall rather than a ladder, because metering storage would
| contradict "their files stay theirs" — with anything larger kept on the
| creator's own drive and added as a link (D-025, D-030). The Free figure
| is the owner's and unset until it is chosen. Null is no total, as it is
| under qori.plans; the per-file cap above still applies first. Declared
| here by T-139, not T-123, because the figure was not known in time.
*/
'series_total_mb' => [
    'free' => null, // the owner's figure — T-139, "Before this can be ready"
    'start' => 100,
    'pro' => 100,
    'school' => 100,
],
```

```php
// App\Models\Group — beside limit() (:146-151)

/**
 * The most one Series may keep on Qori's own storage, in MB, or null when
 * the plan sets no total. A plan the list does not name reads the default
 * plan's, as the per-file cap does.
 */
public function seriesStorageMb(): ?int;
// $totals = (array) config('qori.storage.series_total_mb');
// $plan = array_key_exists($this->plan, $totals) ? $this->plan : (string) config('qori.default_plan');
// $value = $totals[$plan] ?? null;
//
// return $value === null ? null : (int) $value;

/** The per-file cap, in MB — the read UploadService::guardSize() made inline until T-139. */
public function maxUploadMb(): int;
// return (int) (config('qori.storage.max_upload_mb.'.$this->plan)
//     ?? config('qori.storage.max_upload_mb.'.config('qori.default_plan')));
```

```php
// App\Models\Series — beside episodeCount() (:138)

/**
 * Bytes this Series keeps on Qori's storage: every stored asset a material
 * row of this Series points at, Episode-level and Series-level alike.
 *
 * A subquery, not a join — GroupScope and forGroup() both add an
 * unqualified group_id. forGroup() on both, so the answer is the same with
 * or without a current Group. Pending assets, link materials, brief-only
 * homework and an Episode's own file are not in it (T-139).
 */
public function materialBytes(): int;
// return (int) MediaAsset::query()
//     ->forGroup($this->group_id)
//     ->where('status', MediaAssetStatus::Stored)
//     ->whereIn('id', Material::query()
//         ->forGroup($this->group_id)
//         ->where('series_id', $this->getKey())
//         ->whereNotNull('media_asset_id')
//         ->select('media_asset_id'))
//     ->sum('size_bytes');
```

```php
namespace App\Concerns;

use App\Exceptions\AppException;
use App\Models\Series;
use App\Support\Terminology;

/**
 * The per-Series total on Qori's own storage (D-030; the owner's answer of
 * 6 September 2026).
 *
 * Run twice on purpose, like the per-file cap: at sign() with the size the
 * browser declared, so no signed URL exists for a file that cannot fit,
 * and at MaterialService::add() with the size confirm() read back from the
 * bucket, because the declared size is a claim and R2 enforces nothing.
 */
trait CapsSeriesStorage
{
    protected function guardSeriesStorage(Series $series, int $addingBytes): void;
    // $group = $series->group;
    // $limitMb = $group->seriesStorageMb();
    //
    // if ($limitMb === null) {
    //     return;
    // }
    //
    // $used = $series->materialBytes();
    //
    // if ($used + $addingBytes <= $limitMb * 1024 * 1024) {
    //     return;
    // }
    //
    // throw AppException::planLimitReached(
    //     'errors.upload.series_total',
    //     [...app(Terminology::class)->for($group)->replacements(), 'total' => $limitMb],
    //     devMessage: "{$used} + {$addingBytes} bytes exceeds the {$limitMb}MB Series total on the {$group->plan} plan for Series {$series->getKey()}.",
    // );
}
```

```php
// App\Services\UploadService — `use CapsSeriesStorage, LocksOverCapSeries;`

public function sign(
    Group $group,
    User $user,
    string $filename,
    int $sizeBytes,
    MediaAssetPurpose $purpose = MediaAssetPurpose::Episode,
    ?Series $series = null,
): UploadTicket;
// After guardSize($group, $sizeBytes) (:66) and before the MediaAsset is built (:70):
//
// if ($purpose === MediaAssetPurpose::Material) {
//     if ($series === null) {
//         // A programmer error: SignUploadRequest refuses the request first.
//         throw new InvalidArgumentException('A material upload names its Series.');
//     }
//
//     $this->guardSeriesStorage($series, $sizeBytes);
// }

private function guardSize(Group $group, int $sizeBytes): void;
// $limitMb = $group->maxUploadMb();   // in place of the two-line config read at :184-185; the rest unchanged
```

```php
// App\Services\MaterialService (T-130) — `use CapsSeriesStorage, LocksOverCapSeries;`
//
// In add(), after `$asset = … assetOrFail(…)` and before the DB::transaction
// that creates the row:
//
//     if ($asset !== null) {
//         try {
//             $this->guardSeriesStorage($series, (int) $asset->size_bytes);
//         } catch (AppException $refused) {
//             $this->discardAsset($asset);
//
//             throw $refused;
//         }
//     }
//
// $series is T-130's `$this->seriesOf($owner)`, already in hand; the size is
// the one confirm() wrote back from the bucket.

/**
 * A stored object no row will point at: the object, then its media_assets
 * row. Logged and swallowed on failure as deleteObject() is, and for the
 * same reason. Called when the total refuses the row, so a refused upload
 * leaves nothing under materials/ — the lifecycle rule collects only the
 * incoming prefix.
 */
private function discardAsset(MediaAsset $asset): void;
// if ($asset->key !== null) {
//     try {
//         Storage::disk((string) config('qori.storage.disk'))->delete($asset->key);
//     } catch (Throwable $e) {
//         Log::warning('Could not delete a refused material object.', ['asset' => $asset->getKey(), 'key' => $asset->key, 'error' => $e->getMessage()]);
//     }
// }
// $asset->delete();
```

```php
// App\Http\Requests\Share\SignUploadRequest — one rule added to rules() (:31-36)
'series_id' => ['required_if:purpose,'.MediaAssetPurpose::Material->value, 'string', 'max:26'],

// and one entry added to messages() (:52-57), beside 'extension.in' (:55) and for the
// same reason: there is no lang/en/validation.php, so the framework's own
// required_if line would be a user-readable string that lives in no lang file.
'series_id.required_if' => __('errors.upload.series_required.message'),
```

```php
// App\Http\Controllers\Share\UploadController — `use ResolvesShareSeries;`

public function sign(SignUploadRequest $request, UploadService $uploads, CurrentGroup $current): JsonResponse;
// $purpose = MediaAssetPurpose::tryFrom($request->string('purpose')->toString()) ?? MediaAssetPurpose::Episode;
//
// // Scoped by the global scope: another Group's id is not found, which is
// // also the honest answer to give (ResolvesShareSeries).
// $series = $purpose === MediaAssetPurpose::Material
//     ? $this->seriesById($request->string('series_id')->toString())
//     : null;
//
// $ticket = $uploads->sign(
//     $current->get(),
//     CurrentUser::orFail($request),
//     $request->string('filename')->toString(),
//     (int) $request->integer('size'),
//     $purpose,
//     $series,
// );
```

```php
// App\Http\Controllers\Share\SeriesController::show() — T-130's `materials` prop, four lines changed
//
// T-130's $scope is `$current->get()` and therefore ?Group, which is why its
// $fileMb line reads the plan through `$scope?->plan`. The two readers below
// are on Group, so the Group is named once and the Series supplies it when
// there is no current one — a Series always has a Group.
//
// $group = $scope ?? $series->group;
// $fileMb = $group->maxUploadMb();          // in place of T-130's inline config read
// $usedBytes = $series->materialBytes();
// $seriesMb = $group->seriesStorageMb();
//
// 'materials' => [
//     'copy' => $this->materialsCopy($scope, $terminology, $fileMb, $usedBytes, $seriesMb),
//     'limits' => [
//         'perEpisode' => …,          // T-130
//         'note' => …,                // T-130
//         'fileMb' => $fileMb,        // T-130
//         'seriesMb' => $seriesMb,    // null when the plan sets no total
//         'usedBytes' => $usedBytes,
//     ],
// ],

/**
 * @return array<string, mixed>  the shape of lang/en/materials.php, resolved
 */
private function materialsCopy(?Group $scope, Terminology $terminology, int $fileMb, int $usedBytes, ?int $seriesMb): array;
// T-130's three parameters and its four replacements are unchanged — 'limit' => $fileMb,
// 'max', 'count', 'timezone' — and two are added after them:
//     'used' => number_format($usedBytes / 1_048_576, 1),
//     'total' => $seriesMb ?? 0,
// so materials.storage.used and materials.storage.used_no_total resolve like every other
// line. 'total' is 0 and unread when the plan sets no total: the page shows used_no_total.
```

```ts
// resources/js/lib/uploads.ts
export async function uploadFile(
    group: string,
    file: File,
    onProgress: (percent: number) => void = () => {},
    purpose = 'episode',
    seriesId?: string,
): Promise<StoredFile>;
// The sign body gains `series_id: seriesId` — JSON.stringify drops it when undefined.
//
// post(): the thrown message becomes
//     payload?.error?.message
//         ? [payload.error.message, payload.error.resolution].filter(Boolean).join(' ')
//         : (payload?.message ?? payload?.errors?.extension?.[0] ?? 'That upload could not be completed.')
// — the AppException shape first, then today's chain (:59-63) unchanged.
// Nothing else in the file changes.
```

```ts
// resources/js/components/FileUpload.vue — one prop, handed to uploadFile() as its fifth argument (:50-55).
// The props are declared through withDefaults(defineProps<…>(), { … }) (:19-27): the type gains
seriesId?: string;
// and the defaults object gains
seriesId: undefined,
// exactly as `accept` is declared on both.
```

```ts
// resources/js/components/series/MaterialList.vue (T-130) — one prop, passed to both
// <MaterialForm> mounts as :series-id, and the two exported types this task widens
// (both are declared here and imported by MaterialForm.vue and share/series/Show.vue):
seriesId: string;
// MaterialsLimits gains `seriesMb: number | null; usedBytes: number;`
// MaterialsCopy gains `storage: { used: string; used_no_total: string }`

// resources/js/components/series/MaterialForm.vue (T-130) — one prop; the types are imported
seriesId: string;
// <FileUpload purpose="material" :group="groupSlug" :series-id="seriesId" … />
// <p class="text-muted-foreground text-sm">{{ limits.seriesMb === null ? copy.storage.used_no_total : copy.storage.used }}</p>
//     under copy.file_help, rendered when the chosen provider is cloudflare_r2 (add only, as the file field is)

// resources/js/pages/share/series/Show.vue — on T-130's <MaterialList …> mount
:series-id="series.id"
```

A refusal at signing already reaches `InputError` through `FileUpload.vue`
(`:58-61`, `:116`); with `uploads.ts` fixed, what it shows is the message
and the resolution.

`docs/flows/storage.md`, "The three calls" (`:156-177`): a
`guardSeriesStorage(Series, declared size)` line under `guardSize` (`:161`)
for a material upload, reading `config('qori.storage.series_total_mb.{plan}')`;
"Size is checked after the upload, not before it" (`:190-193`) gains a
sentence saying the Series total is enforced again when the material row is
created, against the confirmed size, and that a refused row discards its
object. `docs/flows/materials.md` (`T-130`'s): the same two sentences where
`add()`'s guards are listed, and the Series total leaves its "Not built yet"
line. `docs/tinker/uploads.md`: `T-130`'s "Sign an upload" call for a
material gains `$series` as its sixth argument, and "Watch the guards fire"
(`:60-83`) gains a material upload signed for a Series whose total is spent,
answering `errors.upload.series_total`.

## Copy

| Key                                     | File                    | English                                                                                        |
| --------------------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------- |
| `errors.upload.series_total.message`    | `lang/en/errors.php`    | That file would take this :series past the :total MB it can keep on Qori.                      |
| `errors.upload.series_total.resolution` | `lang/en/errors.php`    | Keep it on your own drive and add it here as a link, or remove a file from this :series first. |
| `errors.upload.series_required.message` | `lang/en/errors.php`    | That file wasn't sent from the page it belongs to, so nothing was uploaded.                    |
| `materials.storage.used`                | `lang/en/materials.php` | Using :used MB of the :total MB this :series can keep on Qori.                                 |
| `materials.storage.used_no_total`       | `lang/en/materials.php` | Using :used MB on Qori.                                                                        |

`:total` comes from config and `:used` from the database; neither is
restated anywhere. `:series` is the Group's word, filled from
`Vocabulary::replacements()` in the exception's `$replace` and by
`materialsCopy()` on the page. The resolution names no vendor and never
suggests a bigger plan, because the total is the same on every paid plan.
`used_no_total` is the line while a plan has no total; it states usage and
nothing about a limit, because `T-130`'s `materials.file_help` directly
above it already says "up to :limit MB each", and nothing says "unlimited"
(`D-030`). `errors.upload.series_total` sits after `too_large` in the
`upload` group (`lang/en/errors.php:545-548`), with a comment naming `D-030` and
saying why the resolution does not lead with upgrade; `series_required`
sits after it. `series_required` carries no resolution, deliberately: the
form always sends the id, so only a client Qori did not build can reach the
line, and there is nothing a person can do about that from where they are —
the omission is `type_mismatch`'s, for the same reason.

## Routes

None. `POST /g/{group}/uploads` (`share.uploads.sign`,
`routes/share/uploads.php:17`) gains the `series_id` field and keeps its
path, name and action.

## Tests

**New: `tests/Feature/Share/SeriesStorageTotalTest.php` — 9 cases**

`setUp` builds a Group on `start` with its owner as a collaborator
(`tests/Feature/Share/UploadTest.php:42-56`), one Series through
`SeriesService::create()` and two File Episodes through
`EpisodeService::add()`, and fakes the disk. A private
`storedMaterial(Episode $episode, int $bytes): Material` creates
`MediaAsset::factory()->stored()->create(['group_id' => $this->group->getKey(), 'purpose' => MediaAssetPurpose::Material, 'key' => 'materials/{group}/{ulid}.pdf', 'size_bytes' => $bytes])`
and the row with `T-130`'s
`Material::factory()->forEpisode($episode)->qoriHosted($asset)->create(['group_id' => $this->group->getKey()])`
— `group_id` passed explicitly on both, because `MaterialFactory::definition()`
opens a fresh Group and `forEpisode()` copies only `series_id` and
`episode_id` (`T-130`, "Code"), so a row left to the factory would land in a
Group of its own and `Series::materialBytes()`, reading with `forGroup()`,
would never see it. The method itself needs no current Group. A
private `sign(array $payload = []): TestResponse` posts to
`share.uploads.sign` with `filename` `deck.pdf`, `size` 1024, `purpose`
`material` and `series_id` the Series' id, the payload merged over it as
`tests/Feature/Share/UploadTest.php:68-74` merges its own — then
`array_filter(…, fn ($value): bool => $value !== null)` over the result, so a
case passing `['series_id' => null]` sends the field absent rather than empty
(cases 5 and 6 need it gone, and `+` cannot remove a key). Sizes are in MB
below and bytes in the file.

1. `test_it_refuses_a_material_upload_that_would_take_the_series_past_its_total`
   — 60 and 35 stored on the two Episodes; signing 6 answers 403 with
   `error.code` `plan_limit_reached`, `error.message` equal to
   `errors.upload.series_total.message` with `100`, `error.resolution` set;
   no `media_assets` row is written.
2. `test_it_signs_a_material_upload_that_lands_exactly_on_the_total` — 95
   stored; signing 5 answers 200 and one pending row.
3. `test_the_total_counts_only_stored_assets_that_material_rows_of_this_series_point_at`
   — two stored materials, a pending material asset with a row, a stored
   asset no row points at (an Episode's own `content['path']`), a link
   material, and a stored material on another Series in the same Group;
   `Series::materialBytes()` equals the two stored materials' bytes and
   nothing more, read with no current Group set.
4. `test_a_plan_with_no_total_is_never_refused_for_the_total` —
   `config()->set('qori.storage.series_total_mb.start', null)`; 95 stored;
   signing 10 answers 200.
5. `test_an_episode_upload_needs_no_series_and_is_outside_the_total` — 100
   stored; `sign()` with `purpose` `episode`, `series_id` null and 10 answers
   200, because neither the field nor the guard applies to an Episode upload.
6. `test_a_material_upload_names_a_series_in_this_group` —
   `sign(['series_id' => null])` answers 422 on `series_id` with
   `errors.upload.series_required.message`; another Group's Series id answers
   404 with `error.code` `not_found`, as does this Series' own slug in place
   of its id — the field is acted on, so it carries an id; none of the three
   writes a row.
7. `test_the_material_row_is_refused_when_the_confirmed_size_crosses_the_total_and_the_object_goes`
   — 95 stored; an asset of purpose `Material` stored by the factory at 10
   with its object put on the fake disk;
   `MaterialService::add($episode, ['title' => 'Deck', 'role' => MaterialRole::Material, 'provider' => EpisodeProvider::CloudflareR2, 'release' => MaterialRelease::WithEpisode, 'media_asset_id' => $asset->getKey()])`
   inside `CurrentGroup::runFor()` throws `AppException` whose
   `publicMessage()` is `errors.upload.series_total.message`; no `materials`
   row exists, the object is missing from the disk and the `media_assets`
   row is gone.
8. `test_the_creator_page_carries_the_running_total_and_the_limit` — 60
   stored; `GET share.series.show` has `materials.limits.usedBytes`
   `62914560`, `materials.limits.seriesMb` `100`, `materials.limits.fileMb`
   `200` and `materials.copy.storage.used` containing
   `60.0 MB of the 100 MB` (asserted as
   `tests/Feature/Series/SeriesTextFieldsTest.php:107-110` asserts a limit);
   then `config()->set('qori.storage.series_total_mb.start', null)` and the
   page has `materials.limits.seriesMb` null and
   `materials.copy.storage.used_no_total` containing `60.0 MB`.
9. `test_the_refusal_and_the_line_use_the_groups_word_for_series` — its own
   `pro` Group, owner, collaborator and Series, with
   `settings[Terminology::SETTINGS_KEY]` naming a Series a "Trail" as
   `tests/Feature/TerminologyTest.php:85-97` names one; `pro` carries
   `custom_vocabulary => true` in config (`config/qori.php:350`), so nothing
   sets the entitlement by hand. 100 stored; signing 1 answers 403 whose
   `error.message`, and that Series page's `materials.copy.storage.used`,
   both contain `Trail` and neither contains `Series`.

**Changed:** none. `tests/Feature/Share/UploadTest.php` sends no `purpose` at
all (`:68-74`), so every case there signs as an Episode and meets neither the
new field nor the guard; its Group is on `free` (`:47-50`), whose total is
`null` until the owner sets it;
`tests/Feature/Series/MaterialsTest.php` (`T-130`) adds materials well under
any total.

Total: 9 new cases.

## Acceptance

- [ ] On a Start Group, the material form says how much the Series is using
      against 100 MB before a file is picked, in the Group's own word for
      Series
- [ ] A file that would take the Series past the total is refused when it is
      picked, under the file button, with the drive-and-link resolution; no
      signed URL and no asset row exist
- [ ] A file that lands under or exactly on the total is stored, and the line
      moves once the material is saved
- [ ] A material whose confirmed size crosses the total is refused when its
      row is created, although its declared size was signed, and nothing is
      left under `materials/` for it
- [ ] An Episode's own upload, a link material, a pending upload and another
      Series' files never change the number
- [ ] A plan with no total is never refused for the total; its line states
      usage, the per-file limit stays in the file help beside it, and nothing
      says "unlimited"
- [ ] `docs/flows/storage.md` and `docs/tinker/uploads.md` show the guard
      where it runs
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- The Free plan's figure for `series_total_mb.free`, which replaces the
  `null` in the config block before this task is `ready`, and with it
  whether Free sits below the paid plans' 100 MB or matches it — the owner's
  (`D-030`; `docs/planning/decisions.md:129`;
  `docs/planning/product-and-pricing.md:301-302`).

## Re-scope log

None.

## Notes

**Follow-up, not fixed here.** An Episode with `provider = cloudflare_r2`
keeps its file at `content['path']` and no `materials` row points at it, so
the total is materials-only. When `D-024`'s later task folds the primary item
into `materials`, the total covers it with no change to `materialBytes()`.
The flow doc says so beside the guard.

**Found on the way.** `resources/js/lib/uploads.ts:59-63` reads
`payload?.message`, and an `AppException` answers `{ error: { … } }`
(`app/Exceptions/AppException.php:251`), so the per-file cap's own copy has
never reached the creator; the fallback line has. Fixed here because the
resolution is the point of this refusal. Not a departure: the file is in the
table.

**The per-file caps above the total.** Start's 200 MB and Pro's 500 MB
per-file caps (`config/qori.php:112-117`) sit above a 100 MB total, so on a
paid plan the total is the tighter of the two for every file the per-file cap
still allows, and it is the total's copy a creator reads. `guardSize()` runs
first, though, so a file above the per-file cap itself — 250 MB on Start —
keeps answering `errors.upload.too_large` and never reaches the total's
guard. That ordering is deliberate: `guardSize()` also catches a zero-byte
upload, and neither refusal misleads. `D-030` says the per-file caps are
unchanged, so this task leaves them; folding the ladder into one number is
the owner's, if ever.

**Claim order.** No stream edit is owed: `streams/classroom.md` already names
`T-139` on its `config/qori.php` line (`:153`, after `T-123`, `T-125` and
`T-138`) and on its `resources/js/pages/share/series/Show.vue` line (`:155`,
after `T-137`), which is the one attribute this task puts on the page
(`:series-id="series.id"` on `T-130`'s mount); it also names this task on
`app/Models/Series.php`, `app/Services/MaterialService.php`,
`lang/en/materials.php`, `lang/en/errors.php`,
`app/Http/Controllers/Share/SeriesController.php`, `docs/flows/materials.md`,
`docs/flows/storage.md` and `docs/tinker/uploads.md`. `T-123`'s own spec
names this task for `storage.series_total_mb` (`T-123`, "Decisions"), so the
declaration here needs no further sanction. The lanes put `T-137` and this
task on one developer in that order, and the files the two share are
`MaterialList.vue`, `share/series/Show.vue` and
`app/Http/Controllers/Share/SeriesController.php` (`T-137` adds
`limits.perSeries` beside this task's `seriesMb` and `usedBytes`). `T-137`
does not edit `MaterialForm.vue`, and its `episodeId: string | null` and
`reorderUrl` props and this task's `seriesId` prop do not meet.

**`T-130`'s spec needs no edit.** It lists the total as out, names this task
in its flow doc's "Not built yet" line and provides `MaterialFactory` for it,
and this task lands after it, editing six of its files: `MaterialService.php`,
`MaterialList.vue`, `MaterialForm.vue`, `lang/en/materials.php`,
`docs/flows/materials.md` and the `materials` prop in `SeriesController`.
`T-130`'s tinker line `$uploads->sign($group, $user, 'worksheet.pdf', 2048, MediaAssetPurpose::Material)`
is true until this task lands and then needs `$series` as a sixth argument;
the `docs/tinker/uploads.md` row above is that change. `T-130`'s private
`deleteObject(Material, string)` may delegate its object-and-row half to
`discardAsset()` once both exist; that is wording-tier for whoever touches
it next.

**Where the number comes from.** `docs/planning/product-and-pricing.md:272-302`
records the 6 September 2026 answer, its consequences and the unstated Free
figure; `D-030` carries it into this sprint, whose story is in
`docs/planning/course-classroom.md`.
