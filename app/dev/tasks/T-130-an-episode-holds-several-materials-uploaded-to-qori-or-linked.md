---
id: T-130
title: An Episode holds several materials a creator adds, uploaded to Qori or linked
stream: classroom
status: done
owner: wayne
estimate: M
depends: T-123
blocks: T-128, T-131, T-132, T-139
---

# T-130 — An Episode holds several materials a creator adds, uploaded to Qori or linked

## Why

An Episode is one item. The row carries one `type`, one `provider` and one
`content` payload (`database/migrations/2026_09_08_000000_create_qori_schema.php:103-118`),
and `StoreEpisodeRequest::content()` writes exactly one reference per provider
(`app/Http/Requests/Share/StoreEpisodeRequest.php:184-198`). A creator with
slides, a worksheet and a reading for one class has nowhere to put them but
three more Episodes, and each of those is a certificate requirement:
`ProgressService::hasFinished()` counts every ordered Episode
(`app/Services/ProgressService.php:247-258`). An uploaded file is worse off
still: `media_assets` has no column pointing at anything (`:162-177`), so
nothing can find an upload from the Episode that uses it, count it, or delete
it with it — `SeriesService::purge()` deletes only the one object named in
`content['path']` (`app/Services/SeriesService.php:277-310`).

`D-024` makes the Episode the lesson: its own item stays as it is, and an
ordered list of materials sits beside it in a table of its own. `D-030` fixes
that table — `materials`, with a role, a provider, a release and a due date —
and `D-025` fixes the two providers this sprint admits: a document on Qori's
storage, addressed by its `media_assets` row, or a pasted `https` link that
Qori shows and never follows.

Afterwards a creator adds up to `config('qori.materials.per_episode')`
materials to each Episode from the Series page, labels each preparation,
material or homework, chooses whether a live Episode lists it with the
Episode or after the session, gives homework a brief and a due date read in
the Group's zone, and edits or removes any of them. Removing a material, its
Episode or its Series deletes the Qori-hosted object behind it. The Peer's
side — the list on their card and `shared.materials.open` — is `T-131`.

## Decisions taken to make this specifiable

**The table is `D-030`'s, and its content rule is one constraint, not a
comment.** A `link` row carries `content.url`, a `cloudflare_r2` row carries
`media_asset_id`, and a `homework` row may carry neither (below):
`materials_content_matches_provider`, one `CHECK` written with
`DB::statement()` as `role = 'homework' OR (provider = 'link' AND
jsonb_exists(content, 'url')) OR (provider = 'cloudflare_r2' AND
media_asset_id IS NOT NULL)`, with `jsonb_exists(content, 'url')` rather than
`content ? 'url'` because PDO rewrites a bare `?` as a placeholder.
`media_asset_id` is also unique: `remove()` deletes the object, so two rows
sharing one object would leave the survivor pointing at nothing. `D-030` names
neither the unique nor the spelling; both follow from what it says.

**`MaterialService` is the only way in and out, and it takes `Episode|Series`.**
The Series arm (`episode_id` null) is five lines — the Series-level cap, no
`after_session` — and exists so `purge()` can be tested against a Series-level
row and so `T-137` adds a route and a page rather than a service. No route
reaches it here.

**A pasted URL is `provider = link` whatever host it names (`D-025`).** No host
is parsed and nothing is fetched; a Slides address and a Dropbox address are
both links. `google_drive`, `dropbox` and `onedrive` are refused with
`errors.materials.provider_not_allowed` in the request and the service, so a
row becomes a provider's only through that provider's connector (`T-094`,
`T-096`, `T-098`). `EpisodeProvider::Link` is `T-123`'s.

**An upload is attached by its asset id, never by a path.** The form posts
`media_asset_id` from the confirm response's `id`
(`resources/js/lib/uploads.ts:21-28`), and `FileUpload.vue` gains a `stored`
emit carrying that response, because its model value is the path (`:57`) and
a path is not a row. The asset must be in this Group (a scoped `find()`, as
`UploadController::assetById()` does at `:68-80`), `stored`, of purpose
`Material`, and attached to no other row. The row's `content` for Qori storage
is `[]`; `media_assets.key` is where the bytes are.

**Removing a material deletes the object first, then the material row, then
its `media_assets` row.** The asset row is the bucket's index
(`app/Models/MediaAsset.php:18-21`), so a row for an object that is gone would
be a lie; objects before rows is `purge()`'s own order
(`app/Services/SeriesService.php:272-276`). The material row goes before the
asset row because `media_asset_id` is null on delete and the `CHECK` wants an
asset on a `cloudflare_r2` row: deleting the asset first would make Postgres
set the column null on a row still `cloudflare_r2`, and that update fails the
constraint inside the transaction — the hazard `series_chats` (`T-132`) avoids
the same way. `deleteObject()` deletes the object and hands back the asset;
the caller deletes the material, then the asset. Only a Qori-hosted object is
deleted, and a failure is logged and swallowed exactly as `purge()` does
(`:284-297`), for the same reason. A link is never touched.

**`EpisodeService::remove()` and `SeriesService::purge()` call
`MaterialService::removeAllOf()` before their own deletes.** The cascade would
drop the rows and leave the objects, and purge keeps the Series row so
nothing cascades at all (`D-030`). `SeriesService` gains its first
constructor. `EpisodeService`'s constructor is `T-124`'s
(`__construct(private LiveSessionService $liveSessions)`), and the stream's
claim order puts `T-124` before this task on `app/Services/EpisodeService.php`:
add `MaterialService` to the constructor `T-124` declares, or declare it if
`T-124` has not landed. Nothing constructs either service with `new` (checked
17 September 2026), and every test resolves them from the container.
`removeAllOf()` reads with
`forGroup($series->group_id)` and never through a relation, because
`qori:series:purge` reads across Groups with no current Group
(`app/Console/Commands/PurgeSeriesCommand.php:34-58`) and a scoped relation
query would throw there.

**The cap throws `invalidRequest`, not `planLimitReached`.** It is the same
number on every plan and not a tier lever (`D-030`); `plan_limit_reached`'s
public code and default copy say upgrade (`lang/en/errors.php:59-62`), which
would be a lie. The message interpolates `:count` and carries a resolution.

**`after_session` is refused on anything but a live Episode, in the request
and in the service.** The request puts the message on the field; the service
is the guarantee — the reason `StoreEpisodeRequest` gives for its own
duplication (`:21-25`).

**`due_at` is homework's alone and is read in the Group's zone.** Both
requests `use App\Concerns\ReadsGroupLocalTime` — `T-124`'s, where
`StoreEpisodeRequest::startsAtUtc()` (`:42-83`) moves — and convert with
`$this->groupLocalToUtc($this->input('due_at'))` in `prepareForValidation()`.
If `T-124` has not landed, each carries a private copy of `startsAtUtc()` on
`due_at`, to be replaced by the concern when it does. A due date on a row that
is not homework is nulled by the service rather than refused: a creator who
changes the role should not have to clear a field first.

**A homework row carries at most one link, and may carry none.** `D-030` puts
the hand-in destination in `content.url`; a template and a destination on one
row would be two links. A creator who has both adds the template as a
`material` row and the destination as the `homework` row, and the brief says
which is which. A homework whose brief and due date are the whole of it is a
row too: stored as `provider = link` with `content = '[]'` and no
`media_asset_id`, which the constraint's `role = 'homework'` arm admits; the
request requires `url` on a `link` row only when the role is not `homework`,
and `add()` writes `[]` when no url came. The Peer's list (`T-131`) shows
such a row with no Open control. A Qori-hosted homework has no hand-in field
this sprint.

**Editing changes the label, never the thing.** `update()` takes `title`,
`role`, `release`, `note` and `due_at`; `provider`, `url` and `media_asset_id`
are fixed at creation, as `EpisodeService::update()` refuses `type` and
`provider` (`:115-123`). Replacing a file is remove and add, and the object
goes with the row.

**Position is per owner and closed on removal.** Rows are numbered from 1
within their Episode (or within the Series for a Series-level row) and
renumbered when one goes, as `EpisodeService::remove()` does (`:156-183`), in
the same transaction.

**Every action is locked with the Series.** `add()`, `update()` and `remove()`
call `guardSeriesUnlocked()`, removal included, for the reason
`EpisodeService::remove()` gives (`:157-161`). `removeAllOf()` does not: its
callers already have.

**Store is nested under the Episode in `routes/share/episodes.php`; update
and destroy under the Series in `routes/share/series.php`.** Every parameter
is an id. A material belongs to one Episode today and to a Series tomorrow
(`T-137`), so the two verbs that change an existing row address it through
the Series, beside the two `T-137` adds.

**The page hands the components their copy and their numbers.** Neither
`MaterialList.vue` nor `MaterialForm.vue` holds English or a limit:
`SeriesController::show()` adds a `materials` prop carrying every
`materials.*` line through `Terminology::line()` and the three numbers from
config, and each Episode carries its rows and a `materialsSummary` line from
`Terminology::choice()`, because a `trans_choice` cannot run in the browser.
The list is mounted once per Episode row and its URLs are built the way the
page already builds `episodesUrl` (`resources/js/pages/share/series/Show.vue:167-190`).

**The creator's list opens nothing.** A row shows the pasted address or the
uploaded file's name and no Open control; signing a URL is the Peer's route
(`shared.materials.open`, `T-131`), and `SignsStoredFiles` belongs to that
task. Thirty rows under each of ten Episodes is three hundred, so each
Episode's list sits behind a `<details>` whose summary is the count.

**The public page is asserted, not changed.** `D-024`: it never renders a
material. `PublicSeriesController::show()` reads nothing this task adds
(`app/Http/Controllers/PublicSeriesController.php:77-126`), and one test holds
it to that.

**`config/qori.php` is not edited.** `T-123` declared `qori.materials.per_episode`,
`qori.materials.per_series`, `qori.limits.text.material_note` and the
`material` live prefix; this task reads them. `UploadService::sign()` already
takes any `MediaAssetPurpose` (`app/Services/UploadService.php:48-54`) and
`UploadKey::live()` reads the prefix from config by the case's value
(`app/Support/UploadKey.php:50-63`), so the new case is one line in the enum.

**Extensions stay as they are.** Adding `odt`, `ods`, `odp` and `epub` is the
owner's call (`D-030`) and not this task's; the copy names the per-file limit
and never "unlimited".

**Seeded and factoried.** The design-review world's live Episode gets a linked
deck and a homework row so the screenshots show the list, and a
`MaterialFactory` exists for `T-131`, `T-137` and `T-139`.

## Preconditions

**Data this task verifies against:** a clean database. The tests build a
Series through `SeriesService::create()` and its Episodes through
`EpisodeService::add()` with `T-123`'s signature — a live Episode needs a
Group with a `timezone` and a future `startsAt`
(`tests/Feature/Series/LiveSessionTest.php:41-60` builds such a Group). A
stored upload is `MediaAsset::factory()->stored()` with `purpose`
`MediaAssetPurpose::Material` and a `key` under `materials/{group}/`, and
`Storage::fake((string) config('qori.storage.disk'))` in `setUp` so the disk
assertions run against nothing real. The design-review world is
`php artisan db:seed --class=DesignReviewSeeder` (`docs/tinker/design-review.md`).

**Equipment:** a browser at 375 px width for the thirty-item list and a
200-character title (owner acceptance 13). Nothing else — this task makes no
vendor call.

**Spike:** none owed. No vendor payload is read: a pasted link is stored and
shown and never followed (`D-025`), and Qori's own bucket is the one already
exercised by `tests/Feature/Share/UploadTest.php`.

## Scope

**In:**

- The `materials` table, `Material`, `MaterialRole`, `MaterialRelease` and
  `MediaAssetPurpose::Material`.
- `MaterialService`: `add()`, `update()`, `remove()`, `removeAllOf()` and the
  guards — provider, release, cap, asset, lock.
- `EpisodeService::remove()` and `SeriesService::purge()` deleting the
  objects of the materials they drop, Episode-level and Series-level.
- `StoreMaterialRequest`, `UpdateMaterialRequest`, `MaterialController` and
  the three routes.
- `MaterialList.vue` and `MaterialForm.vue`, mounted on
  `share/series/Show.vue` under every Episode row; the provider inside "Add
  material"; the sharing help and the outside-sharing-off help (`D-025`,
  `D-018`); the per-file limit and the cap shown from config.
- `FileUpload.vue`'s `stored` emit, and `purpose="material"` on the form's
  uploader.
- `lang/en/materials.php`, the `materials` group in `errors.php`, three
  flashes in `series.php`.
- `MaterialFactory`, two seeded materials, `docs/flows/materials.md`,
  `docs/tinker/uploads.md`.

**Out:**

- The Peer's list, "Shown after the session", the release gate,
  `shared.materials.open`, `SignsStoredFiles`,
  `CloudflareR2Storage::temporaryLink()`,
  `MediaLifetime::minutesForExtension()`, `AccessOpen` on a material and
  `access_opens` (`T-131`). Nothing here signs a URL.
- Series-level materials on any page, their store route and reordering
  (`T-137`); the Series arm of `add()` exists and no route reaches it.
- The per-Series storage total and `config('qori.storage.series_total_mb')`
  (`T-139`); the per-file cap is unchanged.
- New upload extensions (the owner's, `D-030`).
- Picking from Google Drive, Dropbox or OneDrive, and rows with those
  providers (`T-094`, `T-096`, `T-098`); a pasted URL from any of them is a
  link.
- Homework submissions, an "I submitted this" mark, marks, reminders
  (`D-030`).
- Any change to `episodes.content`, `EpisodeType`, `UploadService`,
  `UploadKey`, `SignUploadRequest` or `config/qori.php`.
- Timed release on a date (`on_date`), weeks or modules.

## Files

| Path                                                         | Change | Notes                                                                                                  |
| ------------------------------------------------------------ | ------ | ------------------------------------------------------------------------------------------------------ |
| `database/migrations/2026_09_18_000400_create_materials.php` | new    | The table, its index, the unique and the `CHECK`                                                       |
| `app/Models/Material.php`                                    | new    | `HasUlids`, `BelongsToGroup`, `HasFactory`, `'[]'` default, relations, four helpers                    |
| `app/Enums/MaterialRole.php`                                 | new    | `preparation`, `material`, `homework`                                                                  |
| `app/Enums/MaterialRelease.php`                              | new    | `with_episode`, `after_session`                                                                        |
| `app/Enums/MediaAssetPurpose.php`                            | edit   | `Material = 'material'`; the prefix is `T-123`'s config entry                                          |
| `app/Services/MaterialService.php`                           | new    | `add()`, `update()`, `remove()`, `removeAllOf()`, the guards                                           |
| `app/Services/EpisodeService.php`                            | edit   | `MaterialService` joins `T-124`'s constructor; `remove()` drops the Episode's materials before the row |
| `app/Services/SeriesService.php`                             | edit   | Constructor; `purge()` drops every material before the Episodes                                        |
| `app/Concerns/ResolvesShareSeries.php`                       | edit   | `episodeIn()`                                                                                          |
| `app/Http/Requests/Share/StoreMaterialRequest.php`           | new    | Rules, `ReadsGroupLocalTime` on `due_at`, the asset and release checks, `material()`                   |
| `app/Http/Requests/Share/UpdateMaterialRequest.php`          | new    | Label fields only, `ReadsGroupLocalTime` on `due_at`, `changes()`                                      |
| `app/Http/Controllers/Share/MaterialController.php`          | new    | `store`, `update`, `destroy`                                                                           |
| `app/Http/Controllers/Share/SeriesController.php`            | edit   | `materials` and `materialsSummary` per Episode; the page-level `materials` prop                        |
| `routes/share/episodes.php`                                  | edit   | `share.series.episodes.materials.store`                                                                |
| `routes/share/series.php`                                    | edit   | `share.series.materials.update`, `share.series.materials.destroy`                                      |
| `resources/js/components/series/MaterialList.vue`            | new    | The rows behind a `<details>`, edit and remove per row, the add form                                   |
| `resources/js/components/series/MaterialForm.vue`            | new    | One form for add and edit; the provider, the uploader, the fields                                      |
| `resources/js/components/FileUpload.vue`                     | edit   | `stored` emit with the confirm response                                                                |
| `resources/js/pages/share/series/Show.vue`                   | edit   | Mounts `MaterialList` under each Episode row; `materialsUrl`; prop types                               |
| `lang/en/materials.php`                                      | new    | Every line the two components show                                                                     |
| `lang/en/series.php`                                         | edit   | `material_added`, `material_updated`, `material_removed`                                               |
| `lang/en/errors.php`                                         | edit   | The `materials` group                                                                                  |
| `database/factories/MaterialFactory.php`                     | new    | `link()`, `qoriHosted()`, `homework()`, `forEpisode()`                                                 |
| `database/seeders/DesignReviewSeeder.php`                    | edit   | A linked deck and a homework row on the shared Series' live Episode                                    |
| `docs/flows/materials.md`                                    | new    | The three calls, removal, purge, the link tier, what is not built                                      |
| `docs/flows/README.md`                                       | edit   | A row for `materials.md`                                                                               |
| `docs/flows/series.md`                                       | edit   | `remove()` and `purge()` drop materials; `MaterialService` in the lock list (`:222`)                   |
| `docs/architecture/tenancy.md`                               | edit   | A `materials` row in the group-owned tables (`:50-59`)                                                 |
| `docs/tinker/uploads.md`                                     | edit   | Purpose `Material`, "Attach it as a material", the `materials` prefix in clean-up                      |
| `tests/Feature/Series/MaterialsTest.php`                     | new    | 25 cases                                                                                               |
| `tests/Feature/Share/UploadTest.php`                         | edit   | `materials` joins the `tearDown` prefixes (`:60`); 1 case                                              |

Not edited, deliberately: `config/qori.php` (`T-123` declares every key this
reads), `app/Services/UploadService.php` and `app/Support/UploadKey.php` (both
already take any purpose; the prefix comes from config),
`app/Http/Requests/Share/SignUploadRequest.php` (`Rule::enum` admits the new
case), `app/Providers/IntegrationServiceProvider.php` (no contract here).
`docs/tinker/README.md` needs no row: the recipe extends `uploads.md`. The
three routes are `POST`, `PATCH` and `DELETE`, so `qori:reachability` has
nothing to find; `MaterialService`'s public methods are reached by the
controller and the two services.

## Database

| Table       | Column           | Type        | Null | Default          | Index / constraint                                                                                             |
| ----------- | ---------------- | ----------- | ---- | ---------------- | -------------------------------------------------------------------------------------------------------------- |
| `materials` | `id`             | ulid        | no   |                  | primary                                                                                                        |
| `materials` | `group_id`       | ulid        | no   |                  | FK `groups`, cascade; first in the index                                                                       |
| `materials` | `series_id`      | ulid        | no   |                  | FK `series`, cascade                                                                                           |
| `materials` | `episode_id`     | ulid        | yes  |                  | FK `episodes`, cascade; null is Series-level (`T-137`)                                                         |
| `materials` | `position`       | integer     | no   |                  | 1-based within the owner                                                                                       |
| `materials` | `role`           | string      | no   | `'material'`     | `MaterialRole`                                                                                                 |
| `materials` | `provider`       | string      | no   |                  | `EpisodeProvider`; `cloudflare_r2` or `link` this sprint                                                       |
| `materials` | `title`          | string(200) | no   |                  |                                                                                                                |
| `materials` | `note`           | text        | yes  |                  | at most `qori.limits.text.material_note`, enforced by the request                                              |
| `materials` | `content`        | jsonb       | no   | `'[]'`           | `{url}` for a link, `[]` for Qori storage or a brief-only homework; `CHECK materials_content_matches_provider` |
| `materials` | `media_asset_id` | ulid        | yes  |                  | FK `media_assets`, null on delete; **unique**; in the `CHECK`                                                  |
| `materials` | `release`        | string      | no   | `'with_episode'` | `MaterialRelease`                                                                                              |
| `materials` | `due_at`         | timestamp   | yes  |                  | UTC; homework only                                                                                             |
| `materials` | `created_at`     | timestamp   | yes  |                  |                                                                                                                |
| `materials` | `updated_at`     | timestamp   | yes  |                  |                                                                                                                |
| `materials` |                  |             |      |                  | index `(group_id, series_id, episode_id, position)`                                                            |

Migration: `database/migrations/2026_09_18_000400_create_materials.php`

```php
Schema::create('materials', function (Blueprint $table): void {
    $table->ulid('id')->primary();
    $table->foreignUlid('group_id')->constrained()->cascadeOnDelete();
    $table->foreignUlid('series_id')->constrained()->cascadeOnDelete();
    $table->foreignUlid('episode_id')->nullable()->constrained()->cascadeOnDelete();
    $table->integer('position');
    $table->string('role')->default('material');
    $table->string('provider');
    $table->string('title', 200);
    $table->text('note')->nullable();
    // A string default, because $attributes on the model is one too: a cast
    // never runs over a default (CLAUDE.md, Persistence).
    $table->jsonb('content')->default('[]');
    $table->foreignUlid('media_asset_id')->nullable()->constrained('media_assets')->nullOnDelete();
    $table->string('release')->default('with_episode');
    $table->timestamp('due_at')->nullable();
    $table->timestamps();
    $table->index(['group_id', 'series_id', 'episode_id', 'position']);
    // One object per row: remove() deletes the object.
    $table->unique('media_asset_id');
});

// One rule for role, provider and content (D-030): a link carries a url, Qori
// storage carries an asset, and a homework row may carry neither.
// jsonb_exists(), not `content ? 'url'`: PDO rewrites a bare ? as a placeholder.
DB::statement("ALTER TABLE materials ADD CONSTRAINT materials_content_matches_provider CHECK (role = 'homework' OR (provider = 'link' AND jsonb_exists(content, 'url')) OR (provider = 'cloudflare_r2' AND media_asset_id IS NOT NULL))");

// down(): Schema::dropIfExists('materials');
```

## Code

```php
namespace App\Enums;

/** What a material is for, on the Episode that holds it (D-030). */
enum MaterialRole: string
{
    case Preparation = 'preparation';
    case Material = 'material';
    case Homework = 'homework';
}

/**
 * When Qori lists a material (D-030). It decides what Qori lists and when it
 * signs a Qori-hosted file's URL (T-131), and is no embargo on a file kept
 * elsewhere.
 */
enum MaterialRelease: string
{
    case WithEpisode = 'with_episode';
    /** Only on a live Episode: off the list until the session's scheduled end. */
    case AfterSession = 'after_session';
}

// App\Enums\MediaAssetPurpose — one more case. Its live prefix is
// config('qori.storage.live_prefix.material') = 'materials', declared by T-123.
case Material = 'material';
```

```php
namespace App\Models;

use App\Concerns\BelongsToGroup;
use App\Enums\EpisodeProvider;
use App\Enums\MaterialRelease;
use App\Enums\MaterialRole;
use Database\Factories\MaterialFactory;
use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

/**
 * One thing a Peer needs for an Episode, beside the Episode's own item (D-024,
 * D-030): a document on Qori's storage, addressed by its media_assets row, or a
 * pasted link Qori shows and never follows (D-025).
 *
 * @property string $group_id
 * @property string $series_id
 * @property ?string $episode_id
 * @property int $position
 * @property MaterialRole $role
 * @property EpisodeProvider $provider
 * @property string $title
 * @property ?string $note
 * @property array<string, mixed> $content
 * @property ?string $media_asset_id
 * @property MaterialRelease $release
 * @property ?\Illuminate\Support\Carbon $due_at
 */
class Material extends Model
{
    /** @use HasFactory<MaterialFactory> */
    use BelongsToGroup, HasFactory, HasUlids;

    protected $table = 'materials';

    /** @var list<string> */
    protected $fillable = [
        'group_id', 'series_id', 'episode_id', 'position', 'role', 'provider',
        'title', 'note', 'content', 'media_asset_id', 'release', 'due_at',
    ];

    /** Raw storage value: a cast never runs over a default. */
    protected $attributes = ['content' => '[]'];

    /** @return array<string, string> */
    protected function casts(): array
    {
        return [
            'role' => MaterialRole::class,
            'provider' => EpisodeProvider::class,
            'release' => MaterialRelease::class,
            'content' => 'array',
            'position' => 'integer',
            'due_at' => 'datetime',
        ];
    }

    /** @return BelongsTo<Series, $this> */
    public function series(): BelongsTo;      // belongsTo(Series::class, 'series_id')

    /** @return BelongsTo<Episode, $this> */
    public function episode(): BelongsTo;     // belongsTo(Episode::class, 'episode_id')

    /** @return BelongsTo<MediaAsset, $this> */
    public function asset(): BelongsTo;       // belongsTo(MediaAsset::class, 'media_asset_id')

    public function isLink(): bool;           // $this->provider === EpisodeProvider::Link
    public function isQoriHosted(): bool;     // $this->provider->isQoriHosted()
    public function isHomework(): bool;       // $this->role === MaterialRole::Homework

    /** The pasted address; null for Qori storage and for a brief-only homework. */
    public function url(): ?string;           // $this->content['url'] ?? null
}
```

```php
namespace App\Services;

use App\Concerns\LocksOverCapSeries;
use App\Enums\EpisodeProvider;
use App\Enums\MaterialRelease;
use App\Enums\MaterialRole;
use App\Enums\MediaAssetPurpose;
use App\Exceptions\AppException;
use App\Models\Episode;
use App\Models\Material;
use App\Models\MediaAsset;
use App\Models\Series;
use App\Support\Terminology;
use Carbon\CarbonImmutable;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Throwable;

/**
 * The materials beside an Episode's own item (D-024, D-030).
 *
 * Every path in and out goes through here, so the cap, the release rule, the
 * link tier (D-025) and the object behind a Qori-hosted row are enforced once.
 * Reads on the removal paths use forGroup(), never the ambient scope or a
 * relation: qori:series:purge runs with no current Group.
 */
class MaterialService
{
    use LocksOverCapSeries;

    /**
     * Add a material to the end of an Episode's list, or of a Series' own
     * list (episode_id null; reached by T-137).
     *
     * @param  array{title: string, role: MaterialRole, provider: EpisodeProvider, release: MaterialRelease, url?: ?string, media_asset_id?: ?string, note?: ?string, due_at?: ?CarbonImmutable}  $attributes
     */
    public function add(Episode|Series $owner, array $attributes): Material;
    // $series = $this->seriesOf($owner);
    // $this->guardSeriesUnlocked($series->group, 'add material');
    // $this->guardProvider($attributes['provider']);
    // $this->guardRelease($series, $owner, $attributes['release']);   // required here; material() filled with_episode when the form posted none
    // $this->guardLimit($series, $owner);
    // $asset = $attributes['provider']->isQoriHosted() ? $this->assetOrFail($series, $attributes['media_asset_id'] ?? null) : null;
    // return DB::transaction(fn (): Material => Material::create([
    //     'group_id' => $series->group_id,
    //     'series_id' => $series->getKey(),
    //     'episode_id' => $owner instanceof Episode ? $owner->getKey() : null,
    //     'position' => $this->rowsOf($series, $owner)->count() + 1,   // counted in the database, as EpisodeService::add() does
    //     'role' => $attributes['role'],
    //     'provider' => $attributes['provider'],
    //     'title' => trim($attributes['title']),
    //     'note' => $attributes['note'] ?? null,
    //     'content' => $asset === null && filled($attributes['url'] ?? null) ? ['url' => $attributes['url']] : [],   // [] for Qori storage and for a brief-only homework; any other link row without a url is refused by the request and by the CHECK
    //     'media_asset_id' => $asset?->getKey(),
    //     'release' => $attributes['release'],
    //     'due_at' => $attributes['role'] === MaterialRole::Homework ? ($attributes['due_at'] ?? null) : null,
    // ]));

    /**
     * Change the label, never the thing: provider, url and asset are fixed.
     *
     * @param  array{title?: string, role?: MaterialRole, release?: MaterialRelease, note?: ?string, due_at?: ?CarbonImmutable}  $attributes
     */
    public function update(Material $material, array $attributes): Material;
    // $series = $material->series; guardSeriesUnlocked($series->group, 'edit material');
    // guardRelease($series, $material->episode ?? $series, $attributes['release'] ?? $material->release);   // a key absent from $attributes is unchanged
    // fill title/role/release/note; due_at kept only when the resulting role is Homework; save

    /** Object, then the material, then its media_assets row; the rest renumbered. */
    public function remove(Material $material): void;
    // $series = $material->series; guardSeriesUnlocked($series->group, 'remove material');
    // DB::transaction: $asset = $this->deleteObject($material, $material->group_id); $material->delete(); $asset?->delete();
    //     $this->renumber($series, $material->episode ?? $series);
    // The material row before the asset row: media_asset_id is null on delete and the CHECK wants an asset on a cloudflare_r2 row.

    /**
     * Every material an Episode holds, or every one a Series holds at either
     * level, with its object. Called by EpisodeService::remove() and
     * SeriesService::purge() before their own deletes; no lock, because both
     * callers have already taken it.
     *
     * @return int how many rows went
     */
    public function removeAllOf(Series $series, ?Episode $episode = null): int;
    // Material::query()->forGroup($series->group_id)->where('series_id', $series->getKey())
    //     ->when($episode, fn ($q) => $q->where('episode_id', $episode->getKey()))
    //     ->get()->each(function (Material $m) use ($series): void {
    //         $asset = $this->deleteObject($m, $series->group_id); $m->delete(); $asset?->delete();   // row before asset, as remove()
    //     })->count();

    private function seriesOf(Episode|Series $owner): Series;
    // $owner instanceof Series ? $owner : (Series::query()->whereKey($owner->series_id)->first() ?? throw AppException::notFound('errors.series.not_found'))

    /** D-025: only Qori's storage and a pasted link this sprint. */
    private function guardProvider(EpisodeProvider $provider): void;
    // in_array($provider, [EpisodeProvider::CloudflareR2, EpisodeProvider::Link], true) or
    // throw AppException::invalidRequest('errors.materials.provider_not_allowed', ['provider' => $provider->value], devMessage: ...)

    private function guardRelease(Series $series, Episode|Series $owner, MaterialRelease $release): void;
    // $release === AfterSession && ! ($owner instanceof Episode && $owner->isLive()) →
    // throw AppException::invalidRequest('errors.materials.release_needs_live', app(Terminology::class)->for($series->group)->replacements(), ...)

    private function guardLimit(Series $series, Episode|Series $owner): void;
    // $cap = (int) config($owner instanceof Episode ? 'qori.materials.per_episode' : 'qori.materials.per_series');
    // $this->rowsOf($series, $owner)->count() >= $cap →
    // throw AppException::invalidRequest($owner instanceof Episode ? 'errors.materials.limit' : 'errors.materials.series_limit',
    //     ['count' => (string) $cap] + app(Terminology::class)->for($series->group)->replacements(), devMessage: ...)

    /** Stored, of purpose Material, in this Group, attached nowhere else. */
    private function assetOrFail(Series $series, ?string $assetId): MediaAsset;
    // $asset = $assetId === null ? null : MediaAsset::query()->forGroup($series->group_id)->whereKey($assetId)->first();
    // $asset === null || ! $asset->isStored() || $asset->purpose !== MediaAssetPurpose::Material → invalidRequest('errors.materials.asset_not_found')
    // Material::query()->forGroup($series->group_id)->where('media_asset_id', $asset->getKey())->exists() → invalidRequest('errors.materials.asset_in_use')

    /** @return Builder<Material> */
    private function rowsOf(Series $series, Episode|Series $owner): Builder;
    // forGroup($series->group_id)->where('series_id', ...)->where('episode_id', $owner instanceof Episode ? $owner->getKey() : null)

    /**
     * The Qori-hosted object, and the media_assets row handed back for the
     * caller to delete after the material row (the CHECK; see remove()). A
     * failed delete is logged and swallowed, as SeriesService::purge() does
     * and for the same reason: an object already gone is the outcome this
     * wanted. Null for a link or a brief-only homework.
     */
    private function deleteObject(Material $material, string $groupId): ?MediaAsset;
    // if (! $material->isQoriHosted() || $material->media_asset_id === null) return null;
    // $asset = MediaAsset::query()->forGroup($groupId)->whereKey($material->media_asset_id)->first();
    // if ($asset?->key) { try { Storage::disk((string) config('qori.storage.disk'))->delete($asset->key); } catch (Throwable $e) { Log::warning('Could not delete a removed material object.', [...]); } }
    // return $asset;

    private function renumber(Series $series, Episode|Series $owner): void;
    // $this->rowsOf($series, $owner)->orderBy('position')->get()->each(...): position = index + 1, save
}
```

```php
// App\Concerns\ResolvesShareSeries — one more lookup, beside seriesById()
/**
 * An Episode of this Series, by id. Episodes carry no group scope; the
 * Series already passed it, so the check is membership.
 */
protected function episodeIn(Series $series, string $episodeId): Episode;
// $series->episodes->first(fn (Episode $e): bool => (string) $e->getKey() === $episodeId)
//     ?? throw AppException::notFound('errors.series.episode_not_found', devMessage: ...)
```

```php
// App\Services\EpisodeService — MaterialService joins the constructor T-124 declares
// (T-124's dependency first), or is declared alone if T-124 has not landed; and one line in remove()
public function __construct(private LiveSessionService $liveSessions, private MaterialService $materials) {}

// inside remove()'s transaction, before $episode->delete() (:173):
$this->materials->removeAllOf($series, $episode);

// App\Services\SeriesService — its first constructor, and one line in purge()
public function __construct(private MaterialService $materials) {}

// first statement of purge() (:277), before the Episodes loop — files before rows:
$this->materials->removeAllOf($series);
```

```php
namespace App\Http\Requests\Share;

/**
 * Adding a material to an Episode (D-030). The checks the service also makes
 * are here to put the message on a field, as StoreEpisodeRequest explains.
 */
class StoreMaterialRequest extends FormRequest
{
    use ReadsGroupLocalTime, ResolvesShareSeries;   // ReadsGroupLocalTime is T-124's; a private copy of StoreEpisodeRequest::startsAtUtc() on due_at until it lands

    /** D-025: a pasted link is at most this long. */
    public const URL_MAX = 2048;

    /** due_at from the Group's zone to UTC ISO: $this->groupLocalToUtc($this->input('due_at')), written back as UpdateEpisodeRequest (T-124) writes starts_at. */
    protected function prepareForValidation(): void;

    /** @return array<string, array<int, ValidationRule|array<mixed>|string>> */
    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:200'],
            'role' => ['required', Rule::enum(MaterialRole::class)],
            'provider' => ['required', Rule::in([EpisodeProvider::CloudflareR2->value, EpisodeProvider::Link->value])],
            // A link needs an address unless it is homework: a brief-only homework is a link row with no url (D-030).
            'url' => [Rule::requiredIf(fn (): bool => $this->input('provider') === EpisodeProvider::Link->value && $this->input('role') !== MaterialRole::Homework->value), 'nullable', 'string', 'url:https', 'max:'.self::URL_MAX],
            'media_asset_id' => ['required_if:provider,cloudflare_r2', 'nullable', 'string'],
            'release' => ['sometimes', Rule::enum(MaterialRelease::class)],
            'note' => ['nullable', 'string', 'max:'.config('qori.limits.text.material_note')],
            'due_at' => ['nullable', 'date'],
        ];
    }

    public function withValidator(Validator $validator): void;
    // after():
    //   provider cloudflare_r2: MediaAsset::query()->find($id) (scoped) missing, not stored, or purpose !== Material
    //       → errors()->add('media_asset_id', __('errors.materials.asset_not_found.message'));
    //     attached already (Material::query()->where('media_asset_id', $id)->exists())
    //       → errors()->add('media_asset_id', __('errors.materials.asset_in_use.message'));
    //   release after_session and ! $this->episodeIn($this->seriesById($this->route('seriesId')), $this->route('episodeId'))->isLive()
    //       → errors()->add('release', app(Terminology::class)->line('errors.materials.release_needs_live.message'));

    /** @return array<string, string> */
    public function messages(): array;
    // 'url.required' => __('errors.materials.url_required.message'),   // Rule::requiredIf reports as `required`
    // 'url.url' and 'url.max' => __('errors.materials.url_invalid.message', ['max' => self::URL_MAX]),
    // 'media_asset_id.required_if' => __('errors.materials.file_required.message'),
    // 'provider.in' => __('errors.materials.provider_not_allowed.message'),

    /**
     * What the service takes: enums, and the due date as an instant. `release`
     * is MaterialRelease::WithEpisode when the field is absent — a non-live
     * Episode's form posts none — so add() treats it as required.
     *
     * @return array{title: string, role: MaterialRole, provider: EpisodeProvider, release: MaterialRelease, url: ?string, media_asset_id: ?string, note: ?string, due_at: ?CarbonImmutable}
     */
    public function material(): array;
}

/** Editing a material's label (D-030): never its provider, link or file. */
class UpdateMaterialRequest extends FormRequest
{
    use ReadsGroupLocalTime;   // as StoreMaterialRequest

    protected function prepareForValidation(): void;   // the same due_at conversion

    public function rules(): array
    {
        return [
            'title' => ['sometimes', 'required', 'string', 'max:200'],
            'role' => ['sometimes', Rule::enum(MaterialRole::class)],
            'release' => ['sometimes', Rule::enum(MaterialRelease::class)],
            'note' => ['sometimes', 'nullable', 'string', 'max:'.config('qori.limits.text.material_note')],
            'due_at' => ['sometimes', 'nullable', 'date'],
        ];
    }

    /**
     * Only the fields posted: a key absent from the request is absent here,
     * and update() leaves it unchanged, `release` included.
     *
     * @return array{title?: string, role?: MaterialRole, release?: MaterialRelease, note?: ?string, due_at?: ?CarbonImmutable}
     */
    public function changes(): array;
}
```

```php
namespace App\Http\Controllers\Share;

/**
 * The materials beside an Episode (D-030). Everything here mutates, so every
 * parameter is an id; $group is declared because parameters arrive
 * positionally, as EpisodeController says.
 */
class MaterialController extends Controller
{
    use ResolvesShareSeries;

    public function store(string $group, string $seriesId, string $episodeId, StoreMaterialRequest $request, MaterialService $materials, Terminology $terminology): RedirectResponse;
    // $series = $this->seriesById($seriesId); $episode = $this->episodeIn($series, $episodeId);
    // $material = $materials->add($episode, $request->material());
    // Inertia::flash('toast', ['type' => 'success', 'message' => $terminology->line('series.material_added', ['title' => $material->title])]);
    // return back();

    public function update(string $group, string $seriesId, string $materialId, UpdateMaterialRequest $request, MaterialService $materials, Terminology $terminology): RedirectResponse;
    // $material = $materials->update($this->materialIn($this->seriesById($seriesId), $materialId), $request->changes());
    // flash series.material_updated with the title; back()

    public function destroy(string $group, string $seriesId, string $materialId, MaterialService $materials, Terminology $terminology): RedirectResponse;
    // $material = $this->materialIn(...); $title = $material->title; $materials->remove($material);
    // flash series.material_removed with the title; back()

    /** Scoped by the global scope and bound to this Series, so another tenant's id is simply not found. */
    private function materialIn(Series $series, string $materialId): Material;
    // Material::query()->whereKey($materialId)->where('series_id', $series->getKey())->first()
    //     ?? throw AppException::notFound('errors.materials.not_found', app(Terminology::class)->for($series->group)->replacements(), devMessage: ...)
}
```

```php
// App\Http\Controllers\Share\SeriesController::show() — additions to the render at :154

$rows = Material::query()
    ->where('series_id', $series->getKey())
    ->with('asset')
    ->orderBy('position')
    ->get()
    ->groupBy('episode_id');

// per Episode, beside the keys at :158-166:
'materials' => $rows->get((string) $episode->getKey(), collect())->map(fn (Material $material): array => [
    'id' => (string) $material->getKey(),
    'title' => $material->title,
    'role' => $material->role->value,
    'provider' => $material->provider->value,
    'release' => $material->release->value,
    'position' => $material->position,
    'note' => $material->note,
    'dueAt' => $material->due_at?->toIso8601String(),
    'url' => $material->url(),
    'fileName' => $material->asset?->name,
])->values()->all(),
'materialsSummary' => $terminology->choice('materials.count', $rows->get((string) $episode->getKey(), collect())->count(), [], $scope),

// page-level, beside 'limits':
'materials' => [
    // Every materials.* line, in the file's own nesting, through
    // Terminology::line() with $scope; the replacements are below.
    'copy' => $this->materialsCopy($scope, $terminology, $fileMb),
    'limits' => [
        'perEpisode' => (int) config('qori.materials.per_episode'),
        'note' => (int) config('qori.limits.text.material_note'),
        'fileMb' => $fileMb,   // (int) config('qori.storage.max_upload_mb.'.($scope?->plan ?? config('qori.default_plan'))) — $scope is ?Group, as UploadService::guardSize() reads the plan (:184-185)
    ],
],

/**
 * @return array<string, mixed>  the shape of lang/en/materials.php, resolved
 */
private function materialsCopy(?Group $scope, Terminology $terminology, int $fileMb): array;   // ?Group: $current->get() is nullable, and show() already writes $scope?->timezone()
// replacements: 'limit' => $fileMb, 'max' => config('qori.limits.text.material_note'),
//               'count' => config('qori.materials.per_episode'), 'timezone' => $scope?->timezone() ?? Timezones::fallback()
```

```ts
// resources/js/components/series/MaterialList.vue
export interface MaterialSummary {
    id: string;
    title: string;
    role: 'preparation' | 'material' | 'homework';
    provider: 'cloudflare_r2' | 'link';
    release: 'with_episode' | 'after_session';
    position: number;
    note: string | null;
    dueAt: string | null; // ISO with offset; shown pinned to the Group's zone through SessionTime
    url: string | null;
    fileName: string | null;
}

export interface MaterialsCopy {
    heading: string;
    empty: string;
    add: string;
    save: string;
    edit: string;
    remove: string;
    cancel: string;
    title_label: string;
    title_placeholder: string;
    role_label: string;
    role_help: string;
    roles: Record<MaterialSummary['role'], string>;
    provider_label: string;
    providers: Record<MaterialSummary['provider'], string>;
    url_label: string;
    url_placeholder: string;
    url_help: string;
    url_blocked_help: string;
    file_label: string;
    file_help: string;
    release_label: string;
    release_help: string;
    releases: Record<MaterialSummary['release'], string>;
    note_label: string;
    note_help: string;
    due_label: string;
    due_help: string;
    due_prefix: string;
    limit_note: string;
}

export interface MaterialsLimits {
    perEpisode: number;
    note: number;
    fileMb: number;
}

defineProps<{
    episodeId: string;
    isLive: boolean;
    materials: MaterialSummary[];
    summary: string; // the Episode's materialsSummary line, the <summary> of the <details>
    storeUrl: string; // …/episodes/{episodeId}/materials
    materialsUrl: string; // …/series/{seriesId}/materials; + `/${id}` for PATCH and DELETE
    copy: MaterialsCopy;
    limits: MaterialsLimits;
    timezone: string; // the Group's zone, for due dates and the due label
    groupSlug: string;
    uploadExtensions: string[];
    disabled: boolean; // lock.active
}>();
// <details> with the summary; inside: copy.empty when none, else one row per material —
// position, title, copy.roles[role], copy.providers[provider], url or fileName, copy.releases.after_session
// when release is after_session, `${copy.due_prefix} <SessionTime :starts-at="dueAt" :timezone="timezone" />`
// when dueAt — with an Edit toggle (editing = ref<string | null>) that swaps the row for
// <MaterialForm method="patch" :action="`${materialsUrl}/${material.id}`" :material="material" …/>, and a
// <Form method="delete" :action="`${materialsUrl}/${material.id}`"> Remove button, disabled with the page's other
// controls; then copy.limit_note and <MaterialForm method="post" :action="storeUrl" …/> unless materials.length >= limits.perEpisode.

// resources/js/components/series/MaterialForm.vue
defineProps<{
    action: string;
    method: 'post' | 'patch';
    material?: MaterialSummary; // edit mode when given: no provider, link or file fields
    isLive: boolean; // release select only when true; otherwise nothing is posted and StoreMaterialRequest::material() fills with_episode
    copy: MaterialsCopy;
    limits: MaterialsLimits;
    timezone: string;
    groupSlug: string;
    uploadExtensions: string[];
    disabled: boolean;
}>();
// Inertia <Form :action :method reset-on-success v-slot="{ errors, processing }"> as the page's forms are:
// title (Input, name="title"); role (select, name="role"); provider (select, name="provider", add only);
// url (Input, name="url", when provider is link; optional when role is homework — a brief-only homework posts none) with copy.url_help and copy.url_blocked_help;
// <FileUpload purpose="material" :group="groupSlug" :accept="…" :label="copy.file_label" @stored="assetId = $event.id" />
// with copy.file_help and <input type="hidden" name="media_asset_id" :value="assetId"> (when provider is cloudflare_r2, add only);
// release (select, name="release", when isLive) with copy.release_help;
// note (textarea, name="note", :maxlength="limits.note") with copy.note_help;
// due_at (Input type="datetime-local", name="due_at", when role is homework) labelled copy.due_label, with copy.due_help;
// <InputError> under each; the submit reads copy.add or copy.save.

// resources/js/components/FileUpload.vue — one emit, after `model.value = stored.path` (:57)
import type { StoredFile } from '@/lib/uploads';
const emit = defineEmits<{ stored: [file: StoredFile] }>();
emit('stored', stored);

// resources/js/pages/share/series/Show.vue
// EpisodeSummary gains `materials: MaterialSummary[]; materialsSummary: string;`
// props gain `materials: { copy: MaterialsCopy; limits: MaterialsLimits }`
const materialsUrl = computed(
    () => `${seriesUrl.value}/${props.series.id}/materials`,
);
// Under each Episode row's header (:400-500), inside the row's container:
// <MaterialList :episode-id="episode.id" :is-live="episode.type === 'live'" :materials="episode.materials"
//     :summary="episode.materialsSummary" :store-url="`${episodesUrl}/${episode.id}/materials`" :materials-url="materialsUrl"
//     :copy="materials.copy" :limits="materials.limits" :timezone="timezone.name" :group-slug="groupSlug"
//     :upload-extensions="uploadExtensions" :disabled="lock.active" />
```

```php
namespace Database\Factories;

/** @extends Factory<Material> */
class MaterialFactory extends Factory
{
    protected $model = Material::class;

    /** A link material at position 1 on a Series of its own Group; episode_id null. */
    public function definition(): array;
    // 'group_id' => Group::factory(), 'series_id' => fn (array $a) => Series::factory()->create(['group_id' => $a['group_id']])->getKey(),
    // 'episode_id' => null, 'position' => 1, 'role' => MaterialRole::Material, 'provider' => EpisodeProvider::Link,
    // 'title' => 'Week one slides', 'note' => null, 'content' => ['url' => 'https://example.test/slides'],
    // 'media_asset_id' => null, 'release' => MaterialRelease::WithEpisode, 'due_at' => null

    public function forEpisode(Episode $episode): static;                       // series_id and episode_id from it
    public function link(string $url): static;                                  // provider Link, content ['url' => $url]
    public function qoriHosted(MediaAsset $asset): static;                      // provider CloudflareR2, content [], media_asset_id
    public function homework(?CarbonImmutable $dueAt = null): static;           // role Homework, due_at
}
```

```php
// database/seeders/DesignReviewSeeder::sharedSeries() — after $this->episodes(...) (:352-357):
// find the live Episode by title in $series->fresh()->episodes and create, with group_id set explicitly as every seeded row is:
//   Material 'Clinic slides'      — role Material, provider Link, url https://docs.google.com/presentation/d/design-review-clinic, release AfterSession
//   Material 'Bring one room'     — role Homework, provider Link, url https://forms.example.test/design-review, note 'Describe a room you sat in this week: who spoke first, and what the room had already decided.', due_at = the Episode's starts_at + 7 days
```

`docs/flows/materials.md`: the shape (the table, `Material`, the one `CHECK`
and the brief-only homework row), the three calls
(`POST … /materials` → `StoreMaterialRequest` → `MaterialController@store` →
`MaterialService::add()` → the guards in order → `Material::create()`; `PATCH`
and `DELETE` likewise), removal (`deleteObject()` → the material row → the
`media_assets` row → `renumber()`, and why in that order), what removes
materials with the Episode and the Series
(`EpisodeService::remove()` and `SeriesService::purge()` → `removeAllOf()`,
`forGroup()` and why), the link tier (`D-025`: stored, shown, never
followed), and a "Not built yet" line: the Peer's list and
`shared.materials.open` (`T-131`), Series-level rows' route and reordering
(`T-137`), the Series total (`T-139`). A row in `docs/flows/README.md`.

`docs/tinker/uploads.md`: "Sign an upload" gains the purpose —
`$uploads->sign($group, $user, 'worksheet.pdf', 2048, App\Enums\MediaAssetPurpose::Material)`
and the confirmed key under `materials/{group}/`; a section "Attach it as a
material" calling `app(App\Services\MaterialService::class)->add($episode, [...])`
with the enums; `materials` joins the prefixes in "Clean up".

## Copy

| Key                                                | File                    | English                                                                                                                                                                                           |
| -------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `materials.heading`                                | `lang/en/materials.php` | Materials                                                                                                                                                                                         |
| `materials.count`                                  | `lang/en/materials.php` | {0} No materials\|{1} 1 material\|[2,\*] :count materials                                                                                                                                         |
| `materials.empty`                                  | `lang/en/materials.php` | Nothing here yet. Slides, a reading, a worksheet — whatever your :peer_plural need for this :episode.                                                                                             |
| `materials.add`                                    | `lang/en/materials.php` | Add material                                                                                                                                                                                      |
| `materials.save`                                   | `lang/en/materials.php` | Save                                                                                                                                                                                              |
| `materials.edit`                                   | `lang/en/materials.php` | Edit                                                                                                                                                                                              |
| `materials.remove`                                 | `lang/en/materials.php` | Remove                                                                                                                                                                                            |
| `materials.cancel`                                 | `lang/en/materials.php` | Cancel                                                                                                                                                                                            |
| `materials.title_label`                            | `lang/en/materials.php` | Title                                                                                                                                                                                             |
| `materials.title_placeholder`                      | `lang/en/materials.php` | Week 1 slides                                                                                                                                                                                     |
| `materials.role_label`                             | `lang/en/materials.php` | What it is                                                                                                                                                                                        |
| `materials.roles.preparation`                      | `lang/en/materials.php` | Preparation                                                                                                                                                                                       |
| `materials.roles.material`                         | `lang/en/materials.php` | Material                                                                                                                                                                                          |
| `materials.roles.homework`                         | `lang/en/materials.php` | Homework                                                                                                                                                                                          |
| `materials.role_help`                              | `lang/en/materials.php` | Preparation is read before the :episode, material goes with it, and homework has a brief and a due date.                                                                                          |
| `materials.provider_label`                         | `lang/en/materials.php` | Where it lives                                                                                                                                                                                    |
| `materials.providers.cloudflare_r2`                | `lang/en/materials.php` | Qori storage                                                                                                                                                                                      |
| `materials.providers.link`                         | `lang/en/materials.php` | A link                                                                                                                                                                                            |
| `materials.url_label`                              | `lang/en/materials.php` | Link                                                                                                                                                                                              |
| `materials.url_placeholder`                        | `lang/en/materials.php` | https://                                                                                                                                                                                          |
| `materials.url_help`                               | `lang/en/materials.php` | Set sharing to “anyone with the link can view” first. Qori shows the link to your :peer_plural with access and never opens it itself, so that setting is what lets them in.                       |
| `materials.url_blocked_help`                       | `lang/en/materials.php` | If the link lives in an organisation account whose administrator has turned outside sharing off, it won't open for your :peer_plural. Upload a PDF export to Qori instead.                        |
| `materials.file_label`                             | `lang/en/materials.php` | File                                                                                                                                                                                              |
| `materials.file_help`                              | `lang/en/materials.php` | Documents, slides and images, up to :limit MB each on your plan.                                                                                                                                  |
| `materials.release_label`                          | `lang/en/materials.php` | Listed for :peer_plural                                                                                                                                                                           |
| `materials.releases.with_episode`                  | `lang/en/materials.php` | With the :episode                                                                                                                                                                                 |
| `materials.releases.after_session`                 | `lang/en/materials.php` | After the session                                                                                                                                                                                 |
| `materials.release_help`                           | `lang/en/materials.php` | “After the session” keeps it off the list your :peer_plural see until the session's scheduled end. That decides what Qori lists — a file kept elsewhere is still whatever its own sharing allows. |
| `materials.note_label`                             | `lang/en/materials.php` | Note                                                                                                                                                                                              |
| `materials.note_help`                              | `lang/en/materials.php` | Up to :max characters. For homework, this is the brief: what to do, and where to hand it in.                                                                                                      |
| `materials.due_label`                              | `lang/en/materials.php` | Due, in :timezone                                                                                                                                                                                 |
| `materials.due_help`                               | `lang/en/materials.php` | Homework only. Each :peer sees it in their own time.                                                                                                                                              |
| `materials.due_prefix`                             | `lang/en/materials.php` | Due                                                                                                                                                                                               |
| `materials.limit_note`                             | `lang/en/materials.php` | Up to :count per :episode.                                                                                                                                                                        |
| `series.material_added`                            | `lang/en/series.php`    | :title added.                                                                                                                                                                                     |
| `series.material_updated`                          | `lang/en/series.php`    | :title saved.                                                                                                                                                                                     |
| `series.material_removed`                          | `lang/en/series.php`    | :title removed.                                                                                                                                                                                   |
| `errors.materials.limit.message`                   | `lang/en/errors.php`    | This :episode already holds :count materials.                                                                                                                                                     |
| `errors.materials.limit.resolution`                | `lang/en/errors.php`    | Remove one, or link a folder that holds the rest.                                                                                                                                                 |
| `errors.materials.series_limit.message`            | `lang/en/errors.php`    | This :series already holds :count materials of its own.                                                                                                                                           |
| `errors.materials.series_limit.resolution`         | `lang/en/errors.php`    | Remove one, or link a folder that holds the rest.                                                                                                                                                 |
| `errors.materials.not_found.message`               | `lang/en/errors.php`    | We couldn't find that material in this :series.                                                                                                                                                   |
| `errors.materials.not_found.resolution`            | `lang/en/errors.php`    | It may already have been removed — reload the :series.                                                                                                                                            |
| `errors.materials.provider_not_allowed.message`    | `lang/en/errors.php`    | Materials are uploaded to Qori or linked.                                                                                                                                                         |
| `errors.materials.provider_not_allowed.resolution` | `lang/en/errors.php`    | Choose one of the two — a link works for a file you keep elsewhere.                                                                                                                               |
| `errors.materials.url_required.message`            | `lang/en/errors.php`    | A link needs an address.                                                                                                                                                                          |
| `errors.materials.url_required.resolution`         | `lang/en/errors.php`    | Paste the address, starting with https://.                                                                                                                                                        |
| `errors.materials.url_invalid.message`             | `lang/en/errors.php`    | That doesn't look like an address Qori can show.                                                                                                                                                  |
| `errors.materials.url_invalid.resolution`          | `lang/en/errors.php`    | It needs to start with https:// and be under :max characters.                                                                                                                                     |
| `errors.materials.file_required.message`           | `lang/en/errors.php`    | Upload the file first.                                                                                                                                                                            |
| `errors.materials.file_required.resolution`        | `lang/en/errors.php`    | Choose it and let the upload finish before you save.                                                                                                                                              |
| `errors.materials.asset_not_found.message`         | `lang/en/errors.php`    | That upload isn't here any more.                                                                                                                                                                  |
| `errors.materials.asset_not_found.resolution`      | `lang/en/errors.php`    | Choose the file again and let it finish before you save.                                                                                                                                          |
| `errors.materials.asset_in_use.message`            | `lang/en/errors.php`    | That file is already attached to another material.                                                                                                                                                |
| `errors.materials.asset_in_use.resolution`         | `lang/en/errors.php`    | Edit that one, or upload the file again to attach it here too.                                                                                                                                    |
| `errors.materials.release_needs_live.message`      | `lang/en/errors.php`    | Only a live :episode can list something after the session.                                                                                                                                        |
| `errors.materials.release_needs_live.resolution`   | `lang/en/errors.php`    | Choose “With the :episode”, or add it to a live one.                                                                                                                                              |

Every line carrying a noun is read through `Terminology::line()` (or
`Terminology::choice()` for `materials.count`) with the Series' Group;
`:limit` is the plan's `max_upload_mb`, `:max` is
`qori.limits.text.material_note` (or `StoreMaterialRequest::URL_MAX` on
`url_invalid`), `:count` is `qori.materials.per_episode` or `per_series`, and
`:timezone` is the Group's zone — none restated. `materials.php` opens with a
header in `accesses.php`'s style (`lang/en/accesses.php:3-10`) saying failures
are in `errors.php`. `errors.materials.*` sits after the `upload` group with a
comment naming `D-030`; no key says "unlimited", "available after", or a
vendor's name.

## Routes

| Verb   | Path                                                          | Name                                    | Action                             |
| ------ | ------------------------------------------------------------- | --------------------------------------- | ---------------------------------- |
| POST   | `/g/{group}/series/{seriesId}/episodes/{episodeId}/materials` | `share.series.episodes.materials.store` | `Share\MaterialController@store`   |
| PATCH  | `/g/{group}/series/{seriesId}/materials/{materialId}`         | `share.series.materials.update`         | `Share\MaterialController@update`  |
| DELETE | `/g/{group}/series/{seriesId}/materials/{materialId}`         | `share.series.materials.destroy`        | `Share\MaterialController@destroy` |

The first in `routes/share/episodes.php` after `series.episodes.reorder`
(`:25-26`); the other two in `routes/share/series.php` after
`series.accesses.destroy` (`:61-62`), under a comment saying `T-137` adds the
Series-level store and reorder beside them. All inside `routes/share.php`'s
`auth`, `verified`, `group` group with prefix `g/{group}` and name `share.`
(`:24-34`). Ids only; a slug resolves nothing.

## Tests

**New: `tests/Feature/Series/MaterialsTest.php` — 25 cases**

`setUp` builds an owner, a Group on `start` with `timezone`
`Australia/Melbourne` and an owner `Collaborator` as
`tests/Feature/Series/EpisodeRoutesTest.php:35-53` does, a Series through
`SeriesService::create()`, a File Episode and a live Episode through
`EpisodeService::add()` with `T-123`'s `startsAt` and `lengthMinutes`, and
`Storage::fake((string) config('qori.storage.disk'))`. Helpers:
`storeUrl(Episode)`, `materialUrl(Material)`, `linkPayload(array $overrides = [])`,
`storedUpload(): MediaAsset` (`MediaAsset::factory()->stored()` with
`purpose` `Material`, `group_id` this Group's, `key`
`materials/{group}/{ulid}.pdf`, and `Storage::disk(...)->put($key, 'bytes')`),
and `add(Episode|Series, array): Material` calling the service inside
`CurrentGroup::runFor()`.

1. `test_a_creator_adds_a_link_material_to_an_episode` — POST with
   `provider` `link`, an `https` url, role `material`; one row with
   `position` 1, `content['url']`, `media_asset_id` null, `release`
   `with_episode`, `group_id` this Group's; the toast is `series.material_added`
   with the title (read as `tests/Feature/Access/SeriesAccessCodeTest.php:87-89`
   reads a toast).
2. `test_a_creator_adds_a_qori_hosted_material_from_a_confirmed_upload` —
   `storedUpload()` then POST with `provider` `cloudflare_r2` and its id; the
   row carries `media_asset_id`, `content` `[]`, and `url()` is null.
3. `test_a_pending_upload_cannot_be_attached` — a `pending` asset of purpose
   `Material`; 422 on `media_asset_id`; no row.
4. `test_an_upload_for_an_episode_cannot_be_attached_as_a_material` — a
   stored asset of purpose `Episode`; 422 on `media_asset_id`; no row.
5. `test_an_upload_from_another_group_cannot_be_attached` — a stored
   `Material` asset in another Group; 422 on `media_asset_id`; no row; the
   other Group's asset is untouched.
6. `test_an_upload_cannot_be_attached_twice` — the same asset on two POSTs;
   the second is 422 on `media_asset_id` (`asset_in_use`); one row.
7. `test_a_connected_provider_is_refused_this_sprint` — `google_drive` and
   `dropbox` each 422 on `provider`; the service called directly with
   `EpisodeProvider::Dropbox` throws `AppException` whose `publicMessage()`
   is `errors.materials.provider_not_allowed.message`.
8. `test_a_pasted_drive_url_is_stored_as_a_link` — a
   `https://docs.google.com/presentation/d/...` url; `provider` is `link`
   and `content['url']` is the address unchanged.
9. `test_a_link_must_be_https_and_under_the_length_cap` — `http://…`,
   `ftp://…` and an `https` url of `URL_MAX + 1` characters each 422 on
   `url`; nothing stored.
10. `test_the_per_episode_cap_is_refused_with_the_count` —
    `config()->set('qori.materials.per_episode', 2)`; two rows; a third
    POST leaves two; the service throws `AppException` with
    `ErrorCode::InvalidRequest` whose `publicMessage()` is the
    `errors.materials.limit.message` line with `2` through `Terminology`.
11. `test_after_session_is_only_for_a_live_episode` — `release`
    `after_session` on the File Episode is 422 on `release`; on the live
    Episode it stores `after_session`.
12. `test_a_homework_due_date_is_read_in_the_groups_zone` — role `homework`,
    `due_at` `2026-10-01T09:00`; stored `2026-09-30T23:00:00Z`.
13. `test_a_due_date_is_kept_only_on_homework` — role `material` with a
    `due_at`; stored null. A PATCH changing a homework row's role to
    `material` nulls its `due_at`.
14. `test_a_note_over_the_limit_is_refused` — `note` of
    `config('qori.limits.text.material_note') + 1` characters; 422 on `note`;
    at the limit it stores.
15. `test_editing_changes_the_label_and_never_the_link_or_the_file` — PATCH
    with a new title, role, note and `url`, `provider` and `media_asset_id`;
    the first three change and the last three do not; the toast is
    `series.material_updated`.
16. `test_removing_a_material_deletes_its_object_and_its_upload_row_and_renumbers_the_rest`
    — three rows, the middle one Qori-hosted; DELETE it; the object is
    missing on the fake disk, the `media_assets` row is gone, the two left are
    positions 1 and 2; the toast is `series.material_removed`.
17. `test_removing_an_episode_deletes_its_materials_and_their_objects` — a
    link and an upload on the File Episode; `EpisodeService::remove()`; no
    rows for it, the object missing, the other Episode's rows untouched.
18. `test_purging_a_series_deletes_every_materials_object_including_series_level_rows`
    — an upload on the live Episode and an upload on the Series itself
    through `add($series, …)`; `SeriesService::purge()` from
    `Series::query()->acrossAllGroups()` with no current Group, as the command
    does; both objects missing, no rows, the Series row still `Purged`.
19. `test_material_actions_are_refused_while_over_cap` — the
    `overCapGroup()` shape of `tests/Feature/Series/OverCapLockTest.php:56-71`;
    POST, PATCH and DELETE each leave the rows as they were and the service
    throws `errors.series.locked_over_cap`.
20. `test_a_slug_on_a_material_action_does_not_resolve` — the Series slug in
    place of its id on POST and DELETE; 404 and nothing changes.
21. `test_another_groups_series_cannot_take_a_material` — a second Group's
    Series id under this creator's `g/{group}` on POST; a second Group's
    material id on PATCH and DELETE; each 404 and nothing changes, as
    `EpisodeRoutesTest.php:234-248` asserts for Episodes.
22. `test_the_creators_page_lists_each_episodes_materials_in_order_with_the_copy_and_the_limits`
    — two rows on the live Episode; `assertInertia` sees
    `series.episodes.1.materials` in position order with `role`, `provider`,
    `release`, `dueAt`, `url` and `fileName`, `series.episodes.1.materialsSummary`
    naming `2`, `series.episodes.0.materials` empty with the zero line,
    `materials.limits.perEpisode` equal to config, and
    `materials.copy.file_help` containing the plan's `max_upload_mb`.
23. `test_the_public_page_never_lists_materials` — a published Series with a
    preview Episode carrying a material; the `public/Series` props carry no
    `materials` key on the page or on any Episode, and the response body
    does not contain the material's title or url (`D-024`).
24. `test_adding_a_material_leaves_progress_and_the_certificate_alone` — a
    Peer with an Access completes every Episode through
    `ProgressService::complete()` as `tests/Feature/Shared/CertificateTest.php:51-59`
    does, minting `certificate_code`; add, edit and remove a material;
    `opened_episode_ids`, `completed_episode_ids`, `completed_at` and
    `certificate_code` are unchanged and `episodeCount()` is unchanged
    (owner acceptance 12).
25. `test_a_homework_row_may_carry_only_a_brief_and_a_due_date` — POST with
    role `homework`, `provider` `link`, no `url`, a `note` and a `due_at`;
    one row with `provider` `link`, `content` `[]`, `url()` null,
    `media_asset_id` null and the due instant stored. The same POST with role
    `material` is 422 on `url` and stores nothing, and
    `Material::query()->create([...])` for a `material` row with `provider`
    `link` and `content` `[]` throws `Illuminate\Database\QueryException`
    naming `materials_content_matches_provider`.

**Changed:**

- `tests/Feature/Share/UploadTest.php` — `materials` joins the two prefixes
  `tearDown` removes (`:60`), and 1 new case,
  `test_a_material_upload_lands_under_the_materials_prefix`: sign with
  `purpose` `material`, PUT the bytes, confirm; the asset's `key` starts with
  `materials/{group}/` and its `purpose` is `MediaAssetPurpose::Material`.
  The existing cases are untouched.

Total: 26 new cases.

## Acceptance

- [x] A creator adds a link and an uploaded PDF to one Episode, labels each,
      and sees both rows under the Episode with the source, the label and the
      release; the form shows the cap and the per-file limit from config and
      never the word "unlimited" (owner acceptance 10, the link half, and 13)
- [x] A homework row, with a hand-in link or with none, shows its brief and
      its due date in the Group's zone, and the stored instant is that hour in
      UTC
- [x] "After the session" can be chosen only on a live Episode, and the field
      says so rather than an error page
- [x] The thirty-first material is refused with the count and a resolution;
      the thirty-item list and a 200-character title are usable at 375 px
      (owner acceptance 13)
- [x] Removing a material, removing its Episode, and purging its Series each
      leave no object under `materials/` and no `media_assets` row for it
- [x] Adding, editing or removing a material changes no `opened_episode_ids`,
      `completed_episode_ids`, `completed_at` or `certificate_code`, and no
      Episode count (owner acceptance 12)
- [x] Nothing on the public page names a material, and the Peer's page is
      unchanged until `T-131` (owner acceptance 11, `D-024`)
- [x] Every material action is refused while the Group is over its Series
      cap, and a slug or another Group's id on an action resolves nothing
- [x] `docs/flows/materials.md` describes the chains above and the recipe in
      `docs/tinker/uploads.md` runs
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Specified 17 September 2026 from `D-024`, `D-025` and `D-030` and the
`classroom` stream, which orders it after `T-123` on
`resources/js/pages/share/series/Show.vue` and `app/Services/EpisodeService.php`.

**Nothing here signs a URL.** `SignsStoredFiles`,
`CloudflareR2Storage::temporaryLink()` and
`MediaLifetime::minutesForExtension()` are `T-131`'s, where the Peer's route
is the one caller; the creator's row shows what a material is and opens
nothing. `T-131` reads a Qori-hosted material's key through
`Material::asset()` and its address through `Material::url()`.

**`T-094`'s draft is edited to** write each picked Drive item into a
`materials` row with `provider = google_drive` beside the Episode's primary
item (`D-024`, `D-030`); `provider` takes any `EpisodeProvider` and `content`
takes a provider's item keys, so nothing here changes for it.

**`T-137` widens nothing.** `MaterialService::add(Series …)` and
`removeAllOf(Series)` already take a Series and `errors.materials.series_limit`
exists; `T-137` adds the Series-level store route, the reorder route, the
list above the Episodes on both pages, and reads `qori.materials.per_series`
through the guard that is here.

**`T-139` sums `media_assets.size_bytes` over a Series' `materials` rows**;
`materials.series_id` and the unique `media_asset_id` are what make that total
computable, which `media_assets` alone could not.

The Group-zone conversion of a typed time is `T-124`'s
`App\Concerns\ReadsGroupLocalTime` (`groupLocalToUtc()`, `groupTimezone()`),
which moves `StoreEpisodeRequest::startsAtUtc()` out of that request. Both
Form Requests here `use` it. Until `T-124` lands, each carries a private copy
on `due_at` and swaps it for the concern in the commit that removes the copy;
the Series-level requests `T-137` adds `use` the concern outright.

`SeriesService` gains its first constructor. `EpisodeService`'s constructor is
`T-124`'s, and `app/Services/EpisodeService.php` and
`app/Http/Controllers/Share/SeriesController.php` are both files `T-124`
edits: the stream's claim order puts `T-124` before this task on
`EpisodeService.php`, and two `doing` tasks may not claim one file, so
`SeriesController.php` is serialised the same way. `MaterialService` is added
to the constructor `T-124` declares, `T-124`'s dependency first. Nothing
constructs either service with `new` (checked 17 September 2026 across `app`,
`tests`, `database` and `routes`), so no caller changes.

The added-extensions question (`odt`, `ods`, `odp`, `epub`) is the owner's
(`D-030`) and, if taken, is one commit touching
`config('qori.storage.allowed_uploads')` and
`MediaLifetime::DOCUMENT_EXTENSIONS` together; it is not this task's.

**Executed 19 September 2026 — wording-tier fixes** (`reports/T-130-2026-09-19-wayne.md`):

- `T-124` landed first, so both material requests `use ReadsGroupLocalTime`
  and `MaterialService` joins the constructor `T-124` declared; the private
  copies of `startsAtUtc()` this spec allowed for were never written.
- `MaterialFactory::forEpisode()` sets `group_id` as well as `series_id` and
  `episode_id`, read from the `series` table: otherwise the definition's own
  `Group::factory()` would give the material a Group its Series is not in.
- `MaterialsTest::setUp()` freezes the clock on 1 September 2026, as `T-123`
  does: the live Episode it adds starts on 1 October and the create guard
  refuses a past start.
- The cases the Tests section calls "422" or "404" send JSON, because a plain
  POST that fails validation answers a redirect; the cases that read a toast
  send a plain request, because a toast is flashed to the session.
- `update()` and `remove()` find the Series with one scoped lookup by
  `series_id` rather than the `series` relation; the same scope, and a
  not-found the relation would not have given.
- The creator's row shows every material's note, not only a homework's brief:
  the Acceptance asks for the brief, and a note is the same field.
- `MaterialList` re-mounts the add form after each add, so the uploader's file
  name and the role's own fields start again from nothing — the reset `T-123`
  found `<Form reset-on-success>` does not do for fields that mount later. And
  the form drops the asset id when the uploader's "Replace" empties its path.
