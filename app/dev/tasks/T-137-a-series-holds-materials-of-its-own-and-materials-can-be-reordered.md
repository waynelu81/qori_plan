---
id: T-137
title: A Series holds materials of its own, and materials can be reordered
stream: classroom
status: draft
owner: unassigned
estimate: M
depends: T-132
blocks: none
---

# T-137 — A Series holds materials of its own, and materials can be reordered

> **Draft.** Not to be started — see [`../PROCESS.md`](../PROCESS.md). What
> has to be true before it can be marked `ready` is listed at the bottom.
> Written on 18 September 2026 from `D-030` and `D-024`, as the last of the
> materials tasks after `T-130` and `T-131`, and held by the owner's condition
> that the pilot first shows material repeated across Episodes.

## Why

After `T-130` and `T-131` a material belongs to one Episode. The column that
would let it belong to the Series instead is already there —
`materials.episode_id` is nullable, `D-030` kept it "in the schema now and
reached by `T-137` later", and `MaterialService::add()` takes `Episode|Series`
and writes a row with `episode_id` null when handed a Series (`T-130`,
"Decisions", second bullet) — but no route reaches that arm and neither page
lists such a row. A course outline, a reading list or a syllabus has to be
attached to Episode 1 and attached again to every Episode where it is wanted,
which is the duplication the owner's condition on this task names
(`docs/planning/course-classroom.md`; `streams/classroom.md`, task 15).

A list's order is the order of adding. `MaterialService` numbers rows from 1
within their owner and closes the gap when one goes (`T-130`, "Position is per
owner"), and nothing moves one. Episodes have `EpisodeService::reorder()`
(`app/Services/EpisodeService.php:215-239`) behind two forms per row on the
creator's page (`resources/js/pages/share/series/Show.vue:432-478`,
`aria-label="Move up"` at `:451` and `"Move down"` at `:474`); a material list
has no such control, so a creator who uploaded the worksheet before the slides
either lives with it or removes and re-adds, and for a Qori-hosted file the
remove deletes the object (`T-130`, "Removing a material deletes the object
first").

Afterwards a creator adds materials to the Series itself from its page, up to
`config('qori.materials.per_series')`, and moves any material up or down within
its own list — the Series' own or one Episode's — with the two controls the
Episode rows already have. A Peer with access sees the Series' own materials
above the Episodes under "For the whole Series" and opens each through
`shared.materials.open` exactly as an Episode's material (`T-131`). `D-024`'s
rule holds: the public page and a preview render none of it.

## Decisions taken to make this specifiable

**Series-level rows reach `T-130`'s Series arm, and no second service method is
written for them.** `T-130` left `add(Series …)` in place for this task and
said so ("`T-137` widens nothing"): its `guardLimit()` reads
`qori.materials.per_series` when the owner is a Series, `guardRelease()`
refuses `after_session` on anything but a live Episode, `rowsOf()` reads the
rows with `episode_id` null, `renumber()` takes the same `Episode|Series`
owner and `removeAllOf(Series)` drops both levels on purge. This task adds one controller
action, one route and one mount per page in front of that arm.

**`per_series` counts the Series' own rows and never the Episodes'.** That is
what `T-130`'s `rowsOf($series, $owner)` counts for a Series owner, and it is
the right reading of `D-030`'s "a sanity cap on every plan": the two caps bound
two lists, and a ten-Episode course at thirty materials each would otherwise
be refused its first Series-level row.

**One reorder route serves both kinds of list, and the payload names the
owner.** `POST …/series/{seriesId}/materials/reorder` takes `materials[]` in
the new order, as `ReorderEpisodesRequest` takes `episodes[]`
(`app/Http/Requests/Share/ReorderEpisodesRequest.php:24-43`), and `episode_id`:
empty means the Series' own list, otherwise that Episode through
`ResolvesShareSeries::episodeIn()` (`T-130`). Two routes would be two actions
with one body, and the brief names one. An empty `episode_id` arrives as null,
because `ConvertEmptyStringsToNull` runs before validation; `episodeId()`
treats both the same.

**`MaterialService::reorder()` is `EpisodeService::reorder()` on a per-owner
list.** The payload is checked before the transaction opens; it must be
exactly the owner's current ids, each once, or the service throws
`errors.materials.reorder_mismatch` as `invalidRequest` (422,
`app/Exceptions/ErrorCode.php:37`) and nothing has been written; then one
`UPDATE` per row inside `DB::transaction()`, so the order is never
half-applied (`EpisodeService.php:201-239`). `guardSeriesUnlocked()` runs
first, as it does on every material action (`T-130`, "Every action is locked
with the Series"). The known set is read through `rowsOf()`, which is scoped
and bound to the owner, so a foreign id — another owner's, another Group's —
is simply not in it and the list is a mismatch; nothing outside the owner is
ever touched. The method returns `void`, as `remove()` does: the controller
answers `back()` and the page re-reads. On the page a mismatch is what every
failed action is — the message as an error toast with the resolution under
it, then a redirect back (`app/Exceptions/AppException.php:287-297`;
`docs/architecture/errors.md:83-86`) — and the re-read list shows the order
that actually holds.

**Move up and Move down, not drag-and-drop.** The Episode rows set the pattern
(`Show.vue:432-478`): each control is an Inertia `<Form>` posting the whole
new order, needs no library, and works with a keyboard and at 375 px. The two
buttons and the `moved()` helper (`:269-275`, a pure function over ids) go into
`MaterialList.vue`, beside `T-130`'s Edit and Remove, disabled with the page's
other controls while the Group is over its cap.

**The Series-level list is a second mount of the two existing components,
not a third component.** `D-024`: a page edit is a mount. `MaterialList.vue`'s
`episodeId` widens to accept null, it gains `reorderUrl`, and with a null
`episodeId` it reads the Series' own cap (`limits.perSeries`), empty line and
limit note. The Series-level mount passes `isLive: false`, so `T-130`'s
`MaterialForm.vue` never renders the release select and `with_episode`
applies; `MaterialForm.vue` and `PeerMaterialList.vue` (which takes no
`episodeId`) are not edited. On the creator's page the list sits in its own
`<Panel id="series-materials">` immediately above the Episodes' `<Panel flush>`
(`Show.vue:383`) — `T-132`'s chat card is far below, after `#series-details`
(`:655-657`), so the two never neighbour there. On the Peer's page it is a
`<Panel id="materials">` **after `T-132`'s `<PeerChatCard>` and immediately
above the Episodes' `<Panel>`** (`resources/js/pages/shared/Show.vue:192`),
which answers the question `T-132`'s Notes put to this draft: the chat card
is an action taken once and then collapsed with "I've joined", while the
Series' own materials are read again and again and belong nearest the
Episodes they precede. Above the Episodes rather than below, because what
applies to the whole course is read before Episode 1, and the owner put
course-wide items with the Series (`docs/planning/course-classroom.md`).
`Panel.vue` takes `title` and `description` as props
(`resources/js/components/shell/Panel.vue:17-18`), so both mounts hand it the
lang line and hold no English.

**`StoreMaterialRequest` learns that the route may carry no Episode.**
`T-130`'s `withValidator()` resolves `$this->route('episodeId')` through
`episodeIn()` to decide whether `after_session` is allowed; on the Series-level
route there is no `{episodeId}`, so that line becomes: not live unless the
route names an Episode and it is live. The refusal lands on the `release`
field, and the service refuses it too (`guardRelease()`), for the reason
`StoreEpisodeRequest` gives for its own duplication
(`app/Http/Requests/Share/StoreEpisodeRequest.php:21-25`).

**`SeriesController::show()` reads every material once and partitions on
`episode_id`.** `T-130`'s read groups by `episode_id`; a null key would land
under `''` by PHP's array rules, which is an accident rather than a design.
The rows are partitioned first — Series-level, then the rest grouped as
`T-130` groups them — and the per-row shape moves into one private
`materialRow()` so it is written once for both lists.

**`SharedController::show()` reads the Series' own rows in a second query.**
`T-131`'s `materialsByEpisode()` says `whereNotNull('episode_id')` and its name
stays true; a second indexed read costs less than a null-keyed group. It
still asks `MaterialService::isReleased()` — always true with no Episode
(`T-131`, "three states hold") — so the page and the route keep one answer.

**A Series-level open moves no `last_activity_at` and no
`opened_episode_ids`.** This is `T-131`'s answer rather than a choice left
open here: its `MaterialService::open()` calls `ProgressService::opened()`
inside `if ($episode instanceof Episode)`, and a Series-level row resolves no
Episode — `opened_episode_ids` has nowhere to put a Series either
(`app/Services/ProgressService.php:159-171` takes an Episode id). The
`access_opens` row with `episode_id` null is the whole record, and a later
task that wants such an open to count as activity reads that ledger.

**No flash after a reorder.** As `EpisodeController::reorder()`
(`app/Http/Controllers/Share/EpisodeController.php:110-119`): the list
re-renders in the new order, which is the confirmation. The Series-level
store flashes `T-130`'s `series.material_added` with the title.

**The Series-level limit note interpolates `:series_count`, not `:count`.**
`T-130`'s `materialsCopy()` already fills `count` with `per_episode` for
`materials.limit_note`, and one replacement array serves every `materials.*`
line, so the Series cap needs a name of its own. A longer key that starts
with `:series` is safe beside the noun: the translator replaces longer keys
first, which is the same property `:series_plural` relies on
(`app/Data/Vocabulary.php`, the docblock on `replacements()`).

**The public page changes nothing and is asserted.** `D-024`:
`PublicSeriesController::show()` reads titles only
(`app/Http/Controllers/PublicSeriesController.php:77-93`) and nothing this task
adds, and one case holds it to that for a Series-level row.

**Seeded once.** The design-review world's shared Series gets one Series-level
link, so the screenshots of both pages show the list above the Episodes.

**`config/qori.php` is not edited.** `T-123` declared
`qori.materials.per_series` (30) with the rest of the block; this task reads
it through the guard that is already there and passes it to the page as a
number, never restated.

## Preconditions

**Data this task verifies against:** a clean database. The creator-side tests
build their world as `T-130`'s `tests/Feature/Series/MaterialsTest.php` does
(an owner, a Group on `start` with `timezone` `Australia/Melbourne` and an
owner `Collaborator`, as `tests/Feature/Series/EpisodeRoutesTest.php:35-55`
builds them; a Series through `SeriesService::create()`; a File Episode and a
live Episode through `EpisodeService::add()` with `T-123`'s `startsAt` and
`lengthMinutes`; `Storage::fake((string) config('qori.storage.disk'))`); the
Peer-side tests as `T-131`'s `tests/Feature/Shared/OpenMaterialTest.php`
`scene()` does (a Brisbane Group, a published Series with one live and one
File Episode, a Peer granted through `AccessService::grant()`). Materials are
added through `MaterialService::add()` inside `CurrentGroup::runFor()`, never
through the factory, so the caps and guards run. The design-review world is
`php artisan db:seed --class=DesignReviewSeeder` (`docs/tinker/design-review.md`).

**Equipment:** a browser at 375 px width, for the Move up and Move down
controls beside a 200-character title on both lists (owner acceptance 13).
Nothing else — this task makes no vendor call.

**Spike:** none owed. No vendor payload is read: a pasted link is stored and
shown and never followed (`D-025`), and a Qori-hosted row is signed by
`T-131`'s route, unchanged.

## Scope

**In:**

- `MaterialService::reorder()` and its `guardOrder()`;
  `errors.materials.reorder_mismatch`.
- `ReorderMaterialsRequest`; the release check in `StoreMaterialRequest`
  when the route names no Episode.
- `MaterialController::storeForSeries()` and `reorder()`, and the two routes
  in `routes/share/series.php`.
- `SeriesController::show()`: `series.materials`, `series.materialsSummary`,
  `materials.limits.perSeries`, the `:series_count` replacement; the
  partition and `materialRow()`.
- `SharedController::show()`: `series.materials` and
  `materialCopy.seriesHeading`; `seriesMaterials()`.
- `MaterialList.vue`: Move up and Move down per row, `reorderUrl`, a nullable
  `episodeId`, the Series-level cap, empty line and limit note.
- The Series-level `<Panel>` on `share/series/Show.vue` above the Episodes,
  and `reorderUrl` on every per-Episode mount; the `<Panel id="materials">`
  on `shared/Show.vue` after the chat card and above the Episodes.
- `lang/en/materials.php`: `series_level.*`, `move_up`, `move_down`,
  `peer.series_heading`.
- One seeded Series-level material; `docs/flows/materials.md`;
  `docs/tinker/uploads.md`.

**Out:**

- Any change to `MaterialService::add()`, `update()`, `remove()`,
  `removeAllOf()`, `open()` or `isReleased()`: `T-130` and `T-131` wrote them
  to take a Series or a null Episode already.
- A new Peer route: a Series-level row opens through `shared.materials.open`
  as it is, and `routes/shared.php` is not touched.
- Moving a material from one list to another (an Episode's to the Series', or
  between Episodes): remove and add, as replacing a file is.
- Drag-and-drop, multi-select, or a "move to top" control.
- Reordering Episodes, which `EpisodeService::reorder()` already does and this
  task does not touch.
- The per-Series storage total (`T-139`); the total counts every material row
  of the Series, both levels, and `T-139` reads `series_id` for that.
- Series-level rows in the recording-ready email (`T-128` reads an Episode's
  after-session materials and nothing at Series level) or in the access email
  (`T-136`).
- Connected-tier rows (`T-094`, `T-096`, `T-098`); a pasted URL is a link.
- Homework submissions, marks, reminders (`D-030`); a Series-level homework
  row is allowed and behaves as an Episode's does, brief and due date and
  nothing more.
- The public page, guarded by a test.
- `config/qori.php`, `MaterialForm.vue`, `PeerMaterialList.vue`,
  `OpenMaterialController`, `SeriesService::purge()`, `MaterialFactory`.

## Files

| Path                                                  | Change | Notes                                                                                                                 |
| ----------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| `app/Services/MaterialService.php`                    | edit   | `reorder()`, private `guardOrder()`; `T-130`'s `rowsOf()`, `seriesOf()` and lock reused                               |
| `app/Http/Requests/Share/ReorderMaterialsRequest.php` | new    | `materials[]`, `episode_id`; `materialIds()`, `episodeId()`                                                           |
| `app/Http/Requests/Share/StoreMaterialRequest.php`    | edit   | The `after_session` check when the route carries no `{episodeId}`                                                     |
| `app/Http/Controllers/Share/MaterialController.php`   | edit   | `storeForSeries()`, `reorder()`                                                                                       |
| `app/Http/Controllers/Share/SeriesController.php`     | edit   | The partition, `materialRow()`, `series.materials`, `series.materialsSummary`, `limits.perSeries`, `:series_count`    |
| `app/Http/Controllers/Shared/SharedController.php`    | edit   | `series.materials`, `materialCopy.seriesHeading`; private `seriesMaterials()`                                         |
| `routes/share/series.php`                             | edit   | `share.series.materials.store`, `share.series.materials.reorder`                                                      |
| `resources/js/components/series/MaterialList.vue`     | edit   | Move up / Move down per row; `reorderUrl`; `episodeId` nullable; the Series-level cap, empty line, limit note         |
| `resources/js/pages/share/series/Show.vue`            | edit   | `<Panel id="series-materials">` above the Episodes; `materialsReorderUrl`; `reorderUrl` on every mount; prop types    |
| `resources/js/pages/shared/Show.vue`                  | edit   | `series.materials`; `<Panel id="materials">` after the chat card, above the Episodes; page-local `SharedMaterialCopy` |
| `lang/en/materials.php`                               | edit   | `series_level.heading`, `.help`, `.empty`, `.limit_note`; `move_up`, `move_down`; `peer.series_heading`               |
| `lang/en/errors.php`                                  | edit   | `materials.reorder_mismatch`, in the group `T-130` opened                                                             |
| `database/seeders/DesignReviewSeeder.php`             | edit   | One Series-level link on the shared Series, after `T-130`'s two rows                                                  |
| `docs/flows/materials.md`                             | edit   | "Series-level rows" and "Reordering"; the "Not built yet" line loses this task                                        |
| `docs/tinker/uploads.md`                              | edit   | "Attach it as a material" gains the Series arm and a reorder                                                          |
| `tests/Feature/Series/SeriesMaterialsTest.php`        | new    | 14 cases                                                                                                              |
| `tests/Feature/Shared/SeriesMaterialsPageTest.php`    | new    | 6 cases                                                                                                               |

Not edited, deliberately: `config/qori.php` (`T-123` declared `per_series`);
`resources/js/components/series/MaterialForm.vue` (takes `action` and
`isLive` already); `resources/js/components/series/PeerMaterialList.vue` (no
`episodeId` prop; mounts as it is, and its `PeerMaterialCopy` is widened
page-locally in `shared/Show.vue`, never in the component); `app/Http/Controllers/Shared/OpenMaterialController.php`
and `MaterialService::open()` (`T-131` accepts a null Episode: always
released, no anchor); `routes/shared.php` (no new Peer route);
`app/Services/SeriesService.php` (`T-130`'s `removeAllOf(Series)` drops both
levels); `database/factories/MaterialFactory.php` (its `definition()` is a
Series-level row already); `docs/flows/README.md` (`T-130` adds the
`materials.md` row); `docs/tinker/README.md` (no row to add — the recipe
extends `uploads.md`, as `T-130` says). The two routes are `POST`, so
`qori:reachability` has nothing to find; `MaterialService::reorder()` is
reached by the controller.

## Database

None. `materials.episode_id` is nullable since `T-130`'s migration (`D-030`),
and the index `(group_id, series_id, episode_id, position)` serves the
Series-level list with `episode_id` null as it serves an Episode's.

## Code

```php
// App\Services\MaterialService — T-130's class; one public method and one
// private guard added. rowsOf(), seriesOf() and guardSeriesUnlocked() are T-130's.

use Illuminate\Support\Collection;

/**
 * Put one owner's materials in a new order: the Series' own list, or one
 * Episode's. EpisodeService::reorder() on a per-owner list — the payload is
 * checked before the transaction opens, so a refusal is not a rollback, and
 * each row's position is one UPDATE inside it, so the order is never
 * half-applied.
 *
 * @param  list<string>  $materialIds  in the order they should appear
 */
public function reorder(Episode|Series $owner, array $materialIds): void;
// $series = $this->seriesOf($owner);
// $this->guardSeriesUnlocked($series->group, 'reorder materials');
// $rows = $this->rowsOf($series, $owner)->orderBy('position')->get();
// $this->guardOrder($rows, $materialIds);
//
// DB::transaction(function () use ($rows, $materialIds): void {
//     foreach ($materialIds as $index => $materialId) {
//         $rows->first(fn (Material $material): bool => (string) $material->getKey() === $materialId)
//             ?->fill(['position' => $index + 1])->save();
//     }
// });

/**
 * Exactly the owner's current rows, each once. A foreign id — another
 * owner's, another Group's — is a mismatch and is never moved: rowsOf() is
 * scoped and bound to the owner, so it is simply not in the set.
 *
 * @param  Collection<int, Material>  $rows
 * @param  list<string>  $materialIds
 */
private function guardOrder(Collection $rows, array $materialIds): void;
// $known = $rows->map(fn (Material $material): string => (string) $material->getKey())->all();
//
// if (count($materialIds) !== count($known)
//     || count(array_unique($materialIds)) !== count($materialIds)
//     || array_diff($known, $materialIds) !== []) {
//     throw AppException::invalidRequest(
//         'errors.materials.reorder_mismatch',
//         devMessage: 'Reorder payload did not list exactly the owner\'s existing materials.',
//     );
// }
```

```php
namespace App\Http\Requests\Share;

use Illuminate\Foundation\Http\FormRequest;

/**
 * A new order for one list of materials: the ids, and which list.
 *
 * `episode_id` empty means the Series' own list. Whether the ids are exactly
 * that list is MaterialService's check, as ReorderEpisodesRequest leaves the
 * same question to EpisodeService (:7-14).
 */
class ReorderMaterialsRequest extends FormRequest
{
    /** Authorised by the group middleware — reaching here means membership. */
    public function authorize(): bool;   // true

    /** @return array<string, array<int, string>> */
    public function rules(): array
    {
        return [
            'episode_id' => ['nullable', 'string'],
            'materials' => ['required', 'array'],
            'materials.*' => ['required', 'string'],
        ];
    }

    /**
     * The ids in the order they should appear.
     *
     * @return list<string>
     */
    public function materialIds(): array;
    // array_values(array_map(fn (mixed $id): string => (string) $id, (array) $this->validated('materials')))

    /** Null for the Series' own list — posted empty, or not at all. */
    public function episodeId(): ?string;
    // $id = $this->validated('episode_id'); return is_string($id) && $id !== '' ? $id : null;
}
```

```php
// App\Http\Requests\Share\StoreMaterialRequest::withValidator() — T-130's
// release check, now aware that the Series-level route carries no Episode.
// Replaces the line that resolved $this->route('episodeId') unconditionally.

if ($this->input('release') === MaterialRelease::AfterSession->value) {
    $episodeId = $this->route('episodeId');

    $live = is_string($episodeId)
        && $this->episodeIn($this->seriesById((string) $this->route('seriesId')), $episodeId)->isLive();

    if (! $live) {
        $validator->errors()->add(
            'release',
            app(Terminology::class)->line('errors.materials.release_needs_live.message'),
        );
    }
}
// `release` is tested first, as T-130 does, so a `with_episode` store on either
// route pays no Series lookup and no Episode scan.
```

```php
// App\Http\Controllers\Share\MaterialController — two actions beside T-130's
// store(), update() and destroy(). Ids only; $group is positional, as
// EpisodeController's docblock explains (:20-25).

/** A material of the Series itself: episode_id null (D-030). */
public function storeForSeries(
    string $group,
    string $seriesId,
    StoreMaterialRequest $request,
    MaterialService $materials,
    Terminology $terminology,
): RedirectResponse;
// $material = $materials->add($this->seriesById($seriesId), $request->material());
// Inertia::flash('toast', ['type' => 'success', 'message' => $terminology->line('series.material_added', ['title' => $material->title])]);
// return back();

/**
 * One list in a new order. No toast, as EpisodeController::reorder()
 * (:110-119): the list re-rendered in the new order is the confirmation.
 */
public function reorder(
    string $group,
    string $seriesId,
    ReorderMaterialsRequest $request,
    MaterialService $materials,
): RedirectResponse;
// $series = $this->seriesById($seriesId);
// $owner = $request->episodeId() === null ? $series : $this->episodeIn($series, $request->episodeId());
// $materials->reorder($owner, $request->materialIds());
// return back();
```

```php
// App\Http\Controllers\Share\SeriesController::show() — T-130's read, partitioned
// first so a null episode_id never becomes a '' key by accident. $scope and
// $terminology are the method's own (:148, :142).

[$own, $rest] = Material::query()
    ->where('series_id', $series->getKey())
    ->with('asset')
    ->orderBy('position')
    ->get()
    ->partition(fn (Material $material): bool => $material->episode_id === null);

$rows = $rest->groupBy('episode_id');   // T-130's per-Episode map reads $rows as before

// under 'series', beside 'episodes' (:158):
'materials' => $own->map(fn (Material $material): array => $this->materialRow($material))->values()->all(),
'materialsSummary' => $terminology->choice('materials.count', $own->count(), [], $scope),

// T-130's per-Episode 'materials' map calls $this->materialRow() too.

// under 'materials' => 'limits', beside 'perEpisode', 'note' and 'fileMb':
'perSeries' => (int) config('qori.materials.per_series'),

// materialsCopy()'s replacements gain one entry:
'series_count' => config('qori.materials.per_series'),

/**
 * One row as both lists show it: T-130's shape, written once.
 *
 * @return array{id: string, title: string, role: string, provider: string, release: string, position: int, note: ?string, dueAt: ?string, url: ?string, fileName: ?string}
 */
private function materialRow(Material $material): array;
```

```php
// App\Http\Controllers\Shared\SharedController::show() — beside T-131's additions;
// $model, $materials and $now are T-131's names.

// under 'series', beside 'episodes':
'materials' => $this->seriesMaterials($model, $materials, $now),

// under 'materialCopy', beside 'linkManaged' — through the $terminology
// T-125 injects, as T-131's linkManaged line does:
'seriesHeading' => $terminology->line('materials.peer.series_heading', [], $model->group),

/**
 * The Series' own rows (episode_id null), in T-131's row shape. A second read
 * beside materialsByEpisode(), whose whereNotNull() stays true. isReleased()
 * is asked with no Episode — always true — so the page and the route keep one
 * answer.
 *
 * @return list<array<string, mixed>>
 */
private function seriesMaterials(Series $series, MaterialService $materials, CarbonImmutable $now): array;
// Material::query()
//     ->forGroup($series->group)
//     ->where('series_id', $series->getKey())
//     ->whereNull('episode_id')
//     ->orderBy('position')
//     ->get()
//     ->map(fn (Material $material): array => [
//         'id' => (string) $material->getKey(),
//         'title' => $material->title,
//         'role' => $material->role->value,
//         'provider' => $material->provider->value,
//         'release' => $material->release->value,
//         'isReleased' => $materials->isReleased($material, null, $now),
//         'isOpenable' => $material->url() !== null || $material->provider === EpisodeProvider::CloudflareR2,   // T-131's key, false for a brief-only homework row
//         'note' => $material->note,
//         'dueAt' => $material->due_at?->toIso8601String(),
//     ])->values()->all()
```

```php
// routes/share/series.php — after share.series.materials.destroy (T-130),
// under its comment saying this task adds these two beside it.

// The Series' own materials (T-137): episode_id null. `reorder` cannot be
// read as a material id here — the only siblings with a parameter take
// PATCH and DELETE, as routes/share/episodes.php:21-26 already relies on —
// and it is named before them all the same.
Route::post('series/{seriesId}/materials/reorder', [MaterialController::class, 'reorder'])
    ->name('series.materials.reorder');
Route::post('series/{seriesId}/materials', [MaterialController::class, 'storeForSeries'])
    ->name('series.materials.store');
```

```ts
// resources/js/components/series/MaterialList.vue — T-130's component.
// One prop widened, one added, two entries on the copy and limits shapes,
// two controls per row.

export interface MaterialsCopy {
    // …T-130's fields, unchanged…
    move_up: string;
    move_down: string;
    series_level: {
        heading: string;
        help: string;
        empty: string;
        limit_note: string;
    };
}

export interface MaterialsLimits {
    perEpisode: number;
    perSeries: number;
    note: number;
    fileMb: number;
}

defineProps<{
    episodeId: string | null; // null for the Series' own list
    reorderUrl: string; // …/series/{seriesId}/materials/reorder
    // …every other prop as T-130 declares it…
}>();

// The list's own cap, empty line and limit note follow the owner:
// const cap = computed(() => props.episodeId === null ? props.limits.perSeries : props.limits.perEpisode);
// const emptyLine = computed(() => props.episodeId === null ? props.copy.series_level.empty : props.copy.empty);
// const limitNote = computed(() => props.episodeId === null ? props.copy.series_level.limit_note : props.copy.limit_note);
// T-130's `unless materials.length >= limits.perEpisode` reads `cap` instead.

/** The ids with the row at `index` moved by `by` places — Show.vue's moved() (:269-275), on materials. */
function moved(index: number, by: number): string[];

// Per row, before Edit and Remove, in the Episode rows' shape (Show.vue:432-478):
// <Form v-if="index > 0" :action="reorderUrl" method="post" v-slot="{ processing }">
//     <input type="hidden" name="episode_id" :value="episodeId ?? ''" />
//     <input v-for="id in moved(index, -1)" :key="id" type="hidden" name="materials[]" :value="id" />
//     <button type="submit" :disabled="processing || disabled" :aria-label="copy.move_up">↑</button>
// </Form>
// <Form v-if="index < materials.length - 1" :action="reorderUrl" method="post" v-slot="{ processing }">
//     <input type="hidden" name="episode_id" :value="episodeId ?? ''" />
//     <input v-for="id in moved(index, 1)" :key="id" type="hidden" name="materials[]" :value="id" />
//     <button type="submit" :disabled="processing || disabled" :aria-label="copy.move_down">↓</button>
// </Form>

// resources/js/pages/share/series/Show.vue
// SeriesDetail (:74) gains `materials: MaterialSummary[]; materialsSummary: string;`.
const materialsReorderUrl = computed(() => `${materialsUrl.value}/reorder`); // materialsUrl is T-130's
// Every per-Episode <MaterialList> mount gains :reorder-url="materialsReorderUrl".
// Immediately above the Episodes' <Panel flush> (:383):
// <Panel id="series-materials" :title="materials.copy.series_level.heading" :description="materials.copy.series_level.help">
//     <MaterialList :episode-id="null" :is-live="false" :materials="series.materials" :summary="series.materialsSummary"
//         :store-url="materialsUrl" :materials-url="materialsUrl" :reorder-url="materialsReorderUrl"
//         :copy="materials.copy" :limits="materials.limits" :timezone="timezone.name" :group-slug="groupSlug"
//         :upload-extensions="uploadExtensions" :disabled="lock.active" />
// </Panel>

// resources/js/pages/shared/Show.vue
// props.series gains `materials: PeerMaterial[]`. The copy prop is typed page-locally —
// PeerMaterialList.vue is not edited, so its PeerMaterialCopy keeps T-131's five fields:
import type {
    PeerMaterial,
    PeerMaterialCopy,
} from '@/components/series/PeerMaterialList.vue';

interface SharedMaterialCopy extends PeerMaterialCopy {
    seriesHeading: string; // materials.peer.series_heading
}

// The page's `materialCopy` prop (T-131) is retyped `materialCopy: SharedMaterialCopy`; the same
// object is handed to every <PeerMaterialList :copy> unchanged (structural typing admits the extra key).
// After T-132's <PeerChatCard> and immediately above the Episodes' <Panel> (:192):
// <Panel v-if="series.materials.length && !deletion?.purged" id="materials" :title="materialCopy.seriesHeading">
//     <PeerMaterialList :series-id="series.id" :materials="series.materials" :group-timezone="groupTimezone" :copy="materialCopy" />
// </Panel>
```

```php
// database/seeders/DesignReviewSeeder::sharedSeries() — after T-130's two
// Episode-level rows, with group_id set explicitly as every seeded row is:
//   Material 'Course outline' — series_id the shared Series, episode_id null, position 1,
//   role Material, provider Link, content ['url' => 'https://docs.google.com/document/d/design-review-outline'],
//   release WithEpisode.
```

`config('qori.materials.per_series')` is 30 (`T-123`), read here and never
restated: the guard reads it, the page carries it as `limits.perSeries`, and
the limit note interpolates it as `:series_count`.

`docs/flows/materials.md`: a section "Series-level rows" (the store chain
`POST …/series/{seriesId}/materials` → `StoreMaterialRequest` →
`MaterialController@storeForSeries` → `MaterialService::add(Series …)` → the
guards → `Material::create()` with `episode_id` null; the Peer's read in
`seriesMaterials()`; the open through `shared.materials.open` with no anchor
and no `ProgressService::opened()`) and a section "Reordering"
(`POST …/materials/reorder` → `ReorderMaterialsRequest` →
`MaterialController@reorder` → `episodeIn()` or the Series →
`MaterialService::reorder()` → `guardSeriesUnlocked()` → `guardOrder()` → one
`UPDATE` per row in a transaction; a mismatch is a 422 toast and nothing
moves). The "Not built yet" line that names this task loses it.

`docs/tinker/uploads.md`, "Attach it as a material": one more call,
`app(App\Services\MaterialService::class)->add($series, [...])` with the same
enums and no `after_session`, and a reorder —
`$materials->reorder($series, array_reverse($ids))` where `$ids` are the
Series' own rows in position order — with the note that passing anything but
exactly that list is refused.

## Copy

| Key                                            | File                    | English                                                                                                                        |
| ---------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `materials.series_level.heading`               | `lang/en/materials.php` | For the whole :series                                                                                                          |
| `materials.series_level.help`                  | `lang/en/materials.php` | Listed above the :episode_plural for every :peer with access — an outline, a reading list, anything that isn't one :episode's. |
| `materials.series_level.empty`                 | `lang/en/materials.php` | Nothing for the whole :series yet.                                                                                             |
| `materials.series_level.limit_note`            | `lang/en/materials.php` | Up to :series_count for the whole :series.                                                                                     |
| `materials.move_up`                            | `lang/en/materials.php` | Move up                                                                                                                        |
| `materials.move_down`                          | `lang/en/materials.php` | Move down                                                                                                                      |
| `materials.peer.series_heading`                | `lang/en/materials.php` | For the whole :series                                                                                                          |
| `errors.materials.reorder_mismatch.message`    | `lang/en/errors.php`    | That order didn't match the materials in this list.                                                                            |
| `errors.materials.reorder_mismatch.resolution` | `lang/en/errors.php`    | Reload the page and try again — someone may have changed the list in the meantime.                                             |

The `series_level.*` lines and `peer.series_heading` carry a noun and are read
through `Terminology::line()` with the Series' Group — on the creator's page
by `T-130`'s `materialsCopy()`, which resolves every `materials.*` line and
whose replacements gain `series_count` from `qori.materials.per_series`; on
the Peer's page in `show()`. `peer.series_heading` repeats
`series_level.heading`'s English on purpose: `T-131` put every Peer-side line
under `peer.*` so the two surfaces can diverge without a key moving, and this
task keeps that split rather than read a creator's key from the Peer's page,
so a translator sees the sentence twice and may render it twice. `move_up`
and `move_down` carry none and reach the component through the same `copy`
prop. The two error lines are noun-free
so the service can throw them without a Group in hand, as `T-131`'s are, and
mirror `errors.series.reorder_mismatch` (`lang/en/errors.php:222-225`). No
article sits before a placeholder; nothing here names a vendor, restates a
number, or sits under `live.*`. The Series-level store reuses `T-130`'s
`series.material_added`, unchanged.

## Routes

| Verb | Path                                             | Name                             | Action                                    |
| ---- | ------------------------------------------------ | -------------------------------- | ----------------------------------------- |
| POST | `/g/{group}/series/{seriesId}/materials/reorder` | `share.series.materials.reorder` | `Share\MaterialController@reorder`        |
| POST | `/g/{group}/series/{seriesId}/materials`         | `share.series.materials.store`   | `Share\MaterialController@storeForSeries` |

Both in `routes/share/series.php` after `share.series.materials.destroy`
(`T-130`), inside `routes/share.php`'s `auth`, `verified`, `group` group with
prefix `g/{group}` and name `share.` (`routes/share.php:24-34`). Ids only; a
slug resolves nothing (`app/Concerns/ResolvesShareSeries.php:36-39`). No Peer
route is added; `routes/shared.php` is not touched.

## Tests

**New: `tests/Feature/Series/SeriesMaterialsTest.php` — 14 cases**

`setUp` as `T-130`'s `MaterialsTest`: an owner, a Group on `start` with
`timezone` `Australia/Melbourne` and an owner `Collaborator`
(`tests/Feature/Series/EpisodeRoutesTest.php:35-55`), a Series through
`SeriesService::create()`, a File Episode and a live Episode through
`EpisodeService::add()`, `Storage::fake(...)`. Helpers: `storeUrl()`
(`route('share.series.materials.store', [$group->slug, $series->getKey()])`),
`reorderUrl()`, `linkPayload(array $overrides = [])`,
`add(Episode|Series $owner, array $overrides = []): Material` through
`MaterialService::add()` inside `CurrentGroup::runFor()`,
`ids(Episode|Series $owner): list<string>` (that owner's rows in position
order), `positions(Episode|Series $owner): list<int>`, and `toastContains()`
as `tests/Feature/Access/SeriesAccessCodeTest.php:87-90`.

1. `test_it_adds_a_material_to_the_series_itself` — POST `storeUrl()`
   with `linkPayload()`; 302; one row with `episode_id` null, `series_id` the
   Series', `position` 1, `group_id` this Group's; the toast is
   `series.material_added` with the title; both Episodes' lists are empty.
2. `test_it_numbers_series_level_rows_apart_from_each_episodes_rows` — two
   rows on the File Episode, two on the Series, one on the live Episode;
   `positions()` reads `[1, 2]`, `[1, 2]` and `[1]`.
3. `test_it_counts_the_per_series_cap_over_the_series_own_rows_only` —
   `config()->set('qori.materials.per_series', 2)`; two Series-level rows and
   three on the File Episode; a third Series-level POST leaves two, and the
   service throws `AppException` with `ErrorCode::InvalidRequest` whose
   `publicMessage()` is `errors.materials.series_limit.message` with `2`
   through `Terminology`; a further Episode-level add still succeeds.
4. `test_it_refuses_after_session_on_the_series_itself` — POST with `release`
   `after_session`; 422 on `release` with
   `errors.materials.release_needs_live.message` in the Group's words; no row;
   `MaterialService::add($series, …)` with `MaterialRelease::AfterSession`
   throws the same key.
5. `test_it_reorders_the_series_own_materials` — three Series-level rows;
   POST `reorderUrl()` with `episode_id` `''` and `materials`
   `[third, first, second]`; 302; `ids($series)` is that order and
   `positions($series)` is `[1, 2, 3]`; an Episode's rows are untouched.
6. `test_it_reorders_an_episodes_materials` — three rows on the live
   Episode; POST with `episode_id` its id; the titles come back in the new
   order; the File Episode's and the Series' rows keep theirs.
7. `test_it_refuses_a_reorder_that_is_not_exactly_the_lists_materials` —
   three payloads, each leaving every position as it was, the POST answering
   302 back with an `error` toast whose message is
   `errors.materials.reorder_mismatch.message` and the service throwing
   `AppException` with `ErrorCode::InvalidRequest` and that `publicMessage()`:
   a list missing one id; a Series-level id inside the live Episode's list;
   one id named twice.
8. `test_it_reorders_all_or_nothing` — `EpisodeOrderTest::throwOnEpisodeSave()`'s
   shape (`tests/Feature/Series/EpisodeOrderTest.php:78-89`) on
   `eloquent.saving: App\Models\Material`, thrown on the second save of a
   three-row reorder; the forced failure reaches the caller and
   `positions()` reads `[1, 2, 3]` in the original order (`:185-202`).
9. `test_it_refuses_series_level_actions_while_over_cap` —
   `OverCapLockTest::overCapGroup()`'s shape (`tests/Feature/Series/OverCapLockTest.php:59-71`:
   a second Series, then `forceFill(['plan' => 'free'])`); the Series-level
   POST and a reorder each leave the rows as they were, and the service
   throws `errors.series.locked_over_cap` with `ErrorCode::PlanLimitReached`.
10. `test_it_does_not_resolve_a_slug_on_a_series_level_action` — the Series slug
    in place of its id on both POSTs
    (`tests/Feature/Series/ShareSeriesRoutesTest.php:143-151`); nothing
    changes. A mutation is never an error page: `seriesById()` throws
    `errors.series.not_found` and `AppException::render()` flashes it as an
    `error` toast and lands back, because the GET branch is the only one that
    renders a status (`app/Exceptions/AppException.php:264-289`), so the
    assertion is the toast and the unchanged rows.
11. `test_it_refuses_another_groups_series_and_materials` — a second
    Group's Series id under this creator's `g/{group}` on both POSTs changes
    nothing and answers the same `errors.series.not_found` toast back, as
    `EpisodeRoutesTest.php:234-248` asserts for Episodes; a second Group's
    material id inside this Series' reorder list is a mismatch, and nothing
    moves in either Group.
12. `test_it_closes_the_gap_when_a_series_level_material_is_removed` — three
    Series-level rows; `DELETE` `share.series.materials.destroy` on the
    middle one; `positions($series)` reads `[1, 2]` and the Episodes' rows
    are untouched (`T-130`'s `renumber()` with a null Episode).
13. `test_it_leaves_progress_and_the_certificate_alone` — a Peer with an
    Access completes every Episode through `ProgressService::complete()` as
    `tests/Feature/Shared/CertificateTest.php:51-59` does, minting
    `certificate_code`; add a Series-level row, reorder the list, remove one;
    `opened_episode_ids`, `completed_episode_ids`, `completed_at` and
    `certificate_code` are unchanged and `episodeCount()` is unchanged (owner
    acceptance 12).
14. `test_it_lists_the_series_own_materials_on_the_creators_page_with_the_count_and_the_cap`
    — two Series-level rows and one on the live Episode; `assertInertia`
    sees `series.materials` with two rows in position order carrying `role`,
    `provider`, `release`, `dueAt`, `url` and `fileName`,
    `series.materialsSummary` naming `2`, `series.episodes.1.materials` with
    one row, `materials.limits.perSeries` equal to config, and
    `materials.copy.series_level.heading` and `.limit_note` present, the note
    containing `config('qori.materials.per_series')`.

**New: `tests/Feature/Shared/SeriesMaterialsPageTest.php` — 6 cases**

`scene()` as `T-131`'s `OpenMaterialTest`: a Brisbane Group on `start`, a
published Series with one live Episode two hours ahead and one File Episode,
a Peer granted through `AccessService::grant()`;
`own(array $overrides = []): Material` adding a Series-level link row through
`MaterialService::add($series, …)` inside `CurrentGroup::runFor()`;
`Http::preventStrayRequests()` in `setUp`.

15. `test_it_lists_the_series_own_materials_above_the_episodes_on_the_shared_page`
    — two Series-level rows; `assertInertia` sees `series.materials` with two
    rows in position order, each `isReleased` true, `materialCopy.seriesHeading`
    equal to `Terminology::line('materials.peer.series_heading', [], $group)`,
    and every `series.episodes.*.materials` empty.
16. `test_it_opens_a_series_level_material_through_the_same_route` — a
    Series-level link row; `GET` `shared.materials.open` is 302 to its url;
    an `access_opens` row with `target` material, `episode_id` null,
    `subject_id` the material's id and `group_id` the Access's;
    `opened_episode_ids` and `last_activity_at` are unchanged, because
    `T-131`'s `open()` calls `ProgressService::opened()` only when the row
    resolves an Episode.
17. `test_it_refuses_a_series_level_material_to_a_revoked_access` —
    `AccessService::revoke()`; the open route and `shared.show` each answer
    403 with `errors.access.not_granted.message`; no `access_opens` row.
18. `test_it_does_not_find_a_series_level_material_of_another_groups_series` — a
    second Group's Series with a Series-level row; this Series' id with that
    material's id is 404; the other Series' id is 403; the second Group's
    rows are untouched and no `access_opens` row is written.
19. `test_it_never_lists_series_level_materials_on_the_public_page` — a
    Series-level row on the published Series;
    `GET route('series.public', ['group' => $group->slug, 'series' => $series->slug])`
    `->assertInertia(fn ($page) => $page->missing('series.materials'))` and
    the body contains neither the material's title nor its url (`D-024`).
20. `test_it_uses_the_groups_own_word_for_series_in_both_headings` —
    `config()->set('qori.plans.start.custom_vocabulary', true)` and the
    Group's settings carrying the labels of
    `tests/Feature/TerminologyTest.php:36-50`. The creator's half needs the
    creator `scene()` does not build: an owner `Collaborator`
    (`EpisodeRoutesTest.php:35-55`) and `actingAs($owner)`, or the `group`
    middleware refuses the page before a prop is read. Then the creator's
    `materials.copy.series_level.heading` and the Peer's
    `materialCopy.seriesHeading` contain "Trail" and not "Series".

**Changed:** none. `T-130`'s `MaterialsTest.php` asserts each Episode's
`materials` and `T-131`'s `OpenMaterialTest.php` opens Episode-level rows;
both keep their answers, because `materialRow()` keeps the shape and
`materialsByEpisode()` keeps its `whereNotNull()`.

Total: 20 new cases.

## Acceptance

- [ ] A creator adds a link and an uploaded PDF to the Series itself from its
      page and sees them above the Episodes under "For the whole Series"; the
      thirty-first is refused with the count and a resolution, and the cap
      and the note come from config (owner acceptance 13)
- [ ] Move up and Move down on the Series' own list and on an Episode's list
      reorder that list alone, the other lists keep their order, a stale
      order lands back on the page with the toast and nothing moved, and at
      375 px the two controls sit beside a 200-character title without
      overflow (owner acceptance 13)
- [ ] A Peer with access sees the Series' own materials after the chat card
      and above the Episodes, and opens each in a new tab through the same
      route as an Episode's material; no access, a revoked Access and
      another Group's row meet the answers the tests name, and the public
      page shows none (owner acceptance 11)
- [ ] Adding, reordering or removing a Series-level material changes no
      Episode count, no `opened_episode_ids`, `completed_episode_ids`,
      `completed_at` or `certificate_code` (owner acceptance 12)
- [ ] `docs/flows/materials.md` describes both chains and its "Not built yet"
      line no longer names this task; the recipe in `docs/tinker/uploads.md`
      runs; the design-review seed shows the list on both pages
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Whether the pilot shows material repeated across Episodes, which is the
  condition the merged reference (`docs/planning/course-classroom.md`) and
  the stream (`streams/classroom.md`, task 15) put on this task — the
  owner's. Until it does, this stays a draft whatever the chain's state.
- `T-131` and `T-132` `ready`, so `MaterialList.vue`'s props,
  `SharedController::show()`'s `materialCopy` shape and
  `materialsByEpisode()`, `PeerChatCard.vue`'s place on `shared/Show.vue`,
  and both pages' mount order (`streams/classroom.md`, "Claim order") are
  frozen names this task cites by file and line — anyone's.
- Nothing else. `T-131` already settles what a Series-level open records
  (`open()` calls `ProgressService::opened()` only when the row resolves an
  Episode), so the two bullets above are the whole of it: the owner's
  condition, and two chains reaching `ready`.

## Re-scope log

None.

## Notes

Specified 18 September 2026 from `D-030` and `D-024` and the `classroom`
stream, which orders it after `T-132` on `resources/js/pages/share/series/Show.vue`
and puts it on the slip list: nothing here is promised for the sprint.

**The stream's claim order already carries this task on every file it shares.**
`streams/classroom.md` names it on `app/Http/Controllers/Share/SeriesController.php`,
`app/Http/Controllers/Shared/SharedController.php` (`:143`),
`resources/js/pages/shared/Show.vue` (`:149`),
`resources/js/pages/share/series/Show.vue` (`:155`),
`app/Services/MaterialService.php`, `lang/en/materials.php`,
`lang/en/errors.php`, `docs/flows/materials.md`, `docs/tinker/uploads.md` and
`database/seeders/DesignReviewSeeder.php`, each time after `T-132` and before
`T-138` or `T-139` — so nothing has to be added there. `MaterialList.vue` and
`routes/share/series.php` are under the list's three-task threshold
(`T-130`, `T-137`, `T-139` and `T-130`, `T-132`, `T-137`), and the
dependencies serialise both. `T-139` edits
`app/Services/MaterialService.php`, `MaterialList.vue` and
`share/series/Show.vue` and depends only on `T-130`; the lanes put `T-137`
and `T-139` on one developer in that order, which is what keeps the two from
being `doing` at once.

**`T-132`'s Notes asked this draft to say where the Series-level list sits
relative to `#chat`.** Answered under Decisions: after the chat card,
immediately above the Episodes' `<Panel>`, so the order on `shared/Show.vue`
is progress, chat, the Series' own materials, then the Episodes.

No draft elsewhere is edited. `T-130` left the Series arm of `add()`,
`rowsOf()`, `renumber()` and `removeAllOf()` taking a Series or a null Episode,
and wrote `errors.materials.series_limit` for this task; `T-131` left `open()`
and `isReleased()` accepting a null Episode. The one line of `T-130`'s that is
rewritten here is `StoreMaterialRequest::withValidator()`'s release check,
because with no `{episodeId}` on the route it would hand `episodeIn()` a null.

A brief-only homework row — `role` homework with neither a link nor a file,
which the sprint's reconciliation admits — needs nothing here: it is stored
and listed by `T-130`'s and `T-131`'s code, and a Series-level one renders in
the same mount with no Open control, exactly as an Episode's does.

`T-130`'s `MaterialFactory::definition()` is already a Series-level row
(`episode_id` null, position 1). The tests here still add through
`MaterialService::add()` so the cap and the guards run; the factory is for a
later task that needs rows without the service.

`moved()` exists twice after this task, in `Show.vue` (`:269-275`) and in
`MaterialList.vue`. Hoisting it into `resources/js/lib/` is a wording-tier
change for whoever next touches both.

A Series-level open writes `access_opens` with `episode_id` null and moves
nothing on the Access. Nothing reads `access_opens` yet (`T-131`, Out), so the
row waits for whichever task wants a per-material open count.

The brief allocated about seven cases; this draft lists twenty, because the
Peer's page and the open route earn the revoked, wrong-tenant, public-page
and vocabulary cases every Peer-surface change carries, and the reorder
earns the all-or-nothing and mismatch cases `EpisodeService::reorder()`
already has.

`qori:reachability` finds nothing here: two `POST` routes, and
`MaterialService::reorder()` is reached by the controller.
