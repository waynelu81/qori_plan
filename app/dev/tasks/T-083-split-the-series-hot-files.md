---
id: T-083
title: Split the Series hot files
stream: workflow
status: done
owner: claude
estimate: L
depends: none
blocks: none
---

# T-083 — Split the Series hot files

## Why

The review of 14 September 2026 (`streams/workflow.md`): streams are
features and files are layers, so every stream that touches a Series lands in
the same three files. `app/Http/Controllers/Share/SeriesController.php` is
claimed by twelve tasks across six streams, `routes/share.php` by twelve,
`app/Services/SeriesService.php` by eight; the service is 625 lines with
fourteen public methods spanning Episode CRUD and the Series lifecycle. The
moment drafts are promoted, four developers edit one controller in a week and
the collision rule serialises whole streams. `Share/EpisodeController` also
carries two of the codebase's inline `validate()` calls.

## Decisions taken to make this specifiable

**Route names, paths and Vue imports do not change.** Vue reaches Series
routes by name through `@/routes/share/series`; the split moves code, not
URLs. `routes/share.php` stays as the file that requires the split files, so
every task's Files table that names it stays true.

**Split by verb family.** `SeriesController` keeps `index`, `store`, `update`
and `show`; a new `SeriesLifecycleController` takes `publish`, `archive`,
`unarchive`, `destroy` and `restore`. The shared lookup stays in
`App\Concerns\ResolvesShareSeries`.

**Episodes get their own service.** `EpisodeService` takes `addEpisode`,
`updateEpisode`, `removeEpisode` and `reorderEpisodes` (renamed `add`,
`update`, `remove`, `reorder`); `SeriesService` keeps create, update, the
lifecycle and `uniqueSlug`. Anything in `SeriesService` the Episode methods
shared moves with them or becomes a small `App\Support` helper.

**The Episode controller validates through Form Requests**:
`StoreEpisodeRequest` and `UpdateEpisodeRequest` under `app/Http/Requests/Share/`.

## Preconditions

None. `T-080`, `T-081` and `T-082` run alongside and do not touch this task's
files; `T-082`'s `ArchitectureTest` allow-lists `EpisodeController` until
this merges.

## Scope

**In:**

- `routes/share.php` split into `routes/share/{group,setup,series,episodes,
uploads,payouts}.php` along its existing comment sections, with
  `routes/share.php` requiring them inside the same group and middleware.
- The controller split, the service extraction, the two Form Requests.
- Every test that constructs `SeriesService` for an Episode method or names
  a moved controller action.
- `database/seeders/DesignReviewSeeder.php` and `app/Console/Commands/*` if
  they call a moved method.

**Out:**

- `docs/flows/series.md` — `T-082` owns `docs/flows`; the merge adds the
  paragraph describing the new files.
- Any behaviour change. Every existing test passes with at most a class name
  or method name changed.
- `PublicSeriesController`, `SeriesAccessController`, checkout.

## Files

| Path                                                       | Change | Notes                                                        |
| ---------------------------------------------------------- | ------ | ------------------------------------------------------------ |
| `routes/share.php`                                         | edit   | Requires the split files                                     |
| `routes/share/group.php`                                   | new    |                                                              |
| `routes/share/setup.php`                                   | new    |                                                              |
| `routes/share/series.php`                                  | new    |                                                              |
| `routes/share/episodes.php`                                | new    |                                                              |
| `routes/share/uploads.php`                                 | new    |                                                              |
| `routes/share/payouts.php`                                 | new    |                                                              |
| `app/Http/Controllers/Share/SeriesController.php`          | edit   | index, store, update, show                                   |
| `app/Http/Controllers/Share/SeriesLifecycleController.php` | new    | publish, archive, unarchive, destroy, restore                |
| `app/Http/Controllers/Share/EpisodeController.php`         | edit   | EpisodeService, Form Requests                                |
| `app/Http/Requests/Share/StoreEpisodeRequest.php`          | new    |                                                              |
| `app/Http/Requests/Share/UpdateEpisodeRequest.php`         | new    |                                                              |
| `app/Services/SeriesService.php`                           | edit   | Episode methods out                                          |
| `app/Services/EpisodeService.php`                          | new    |                                                              |
| `database/seeders/DesignReviewSeeder.php`                  | edit   | Only if it calls a moved method                              |
| `tests/Feature/Series/*.php`                               | edit   | Class and method names                                       |
| `tests/Feature/Share/EpisodeTest.php`                      | edit   | If it exists; otherwise the Episode tests wherever they live |

Every other file under `tests/` that references a moved method is also
edited; the report lists them.

## Added during execution

Files the Files table did not list, touched under PROCESS.md's departure
tier, each with the reason:

| Path                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Change | Reason                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/Feature/ArchitectureTest.php`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | edit   | `T-082` merged first, so the allow-list entry `'app/Http/Controllers/Share/EpisodeController.php' => 'T-083 converts it'` is removed here rather than at the merge; the rule now guards the controller                                              |
| `docs/flows/series.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | edit   | The paragraph describing the new files, and the four lines that named `SeriesController@publish` and `SeriesService::addEpisode/reorderEpisodes`. This is the flow doc the task keeps true                                                          |
| `app/Http/Requests/Share/ReorderEpisodesRequest.php`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | new    | `StoreEpisodeRequest` already existed; the two inline `validate()` calls were `update()` and `reorder()`, so the second new Form Request is for reorder                                                                                             |
| `app/Support/DeletionDate.php`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | new    | `SeriesController::deletionDate()` was a private helper that `show()`/`summarise()` (staying) and `destroy()` (moving) both use; one helper rather than the same format string in two controllers                                                   |
| `tests/Feature/Share/EpisodeServiceTest.php`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | new    | Named under Tests, absent from the table                                                                                                                                                                                                            |
| `app/Console/Commands/MailCheckCommand.php`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | edit   | Scope names `app/Console/Commands/*` "if they call a moved method"; this one calls `addEpisode()`                                                                                                                                                   |
| `tests/Feature/ShareDigestTest.php`, `tests/Feature/Access/AccessServiceTest.php`, `tests/Feature/Access/ShareAccessRoutesTest.php`, `tests/Feature/Access/SharedRoutesTest.php`, `tests/Feature/Admin/ConsolePagesTest.php`, `tests/Feature/Checkout/BuyButtonTest.php`, `tests/Feature/Checkout/CheckoutTest.php`, `tests/Feature/Checkout/StripeWebhookTest.php`, `tests/Feature/Shared/CertificateTest.php`, `tests/Feature/Shared/ProgressTest.php`, `tests/Feature/Storage/MediaLifetimeTest.php`, `tests/Feature/Storage/PlaybackTest.php` | edit   | Every other test that built a Series through `addEpisode()`; the table only anticipated `tests/Feature/Series/*.php`                                                                                                                                |
| `docs/tinker/series.md`, `docs/tinker/accesses.md`, `docs/tinker/uploads.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | edit   | Recipes that drove `addEpisode()` and `reorderEpisodes()`; CLAUDE.md says a recipe stays runnable when its flow changes. Only the lines naming the moved methods, plus the `Episode::TYPE_*` constants those same lines used, which no longer exist |
| `docs/planning/tasks/T-047-episode-position-comes-from-a-stale-count.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | edit   | A `ready` spec naming `SeriesService::addEpisode()` and a Files row for `SeriesService.php`; PROCESS.md's "grep the ready specs for everything you renamed", wording only                                                                           |

## Database

None.

## Code

```php
namespace App\Services;

class EpisodeService
{
    public function add(Series $series, string $title, string $type, array $content = [], array $attributes = []): Episode; // signature follows SeriesService::addEpisode exactly
    public function update(Series $series, string $episodeId, array $attributes): Series;
    public function remove(Series $series, string $episodeId): Series;
    public function reorder(Series $series, array $episodeIds): Series;
}
```

```php
namespace App\Http\Controllers\Share;

class SeriesLifecycleController extends Controller
{
    use ResolvesShareSeries;
    public function publish(...): RedirectResponse;
    public function archive(...): RedirectResponse;
    public function unarchive(...): RedirectResponse;
    public function destroy(...): RedirectResponse;
    public function restore(...): RedirectResponse;
}
```

Signatures copy the existing actions exactly; only the class moves.

```php
// routes/share.php (shape)
Route::middleware([...])->prefix('g/{group}')->name('share.')->group(function (): void {
    require __DIR__.'/share/group.php';
    require __DIR__.'/share/setup.php';
    require __DIR__.'/share/series.php';
    require __DIR__.'/share/episodes.php';
    require __DIR__.'/share/uploads.php';
    require __DIR__.'/share/payouts.php';
});
```

`php artisan route:list --name=share.` before and after must list the same
names, methods and URIs; the report includes the diff (empty).

## Copy

None.

## Routes

None change. The same names, verbs and paths, declared in six files.

## Tests

**New: `tests/Feature/Share/EpisodeServiceTest.php` — 4 cases**, one per
method, moved from wherever `SeriesService`'s Episode cases live today if
they exist there, else written.

**Changed:** every test naming `SeriesService::addEpisode` and friends or a
lifecycle action's controller class; behaviour assertions unchanged.

## Acceptance

- [x] `route:list --name=share.` is identical before and after
- [x] `SeriesService` has no Episode method; `EpisodeService` has four
- [x] `EpisodeController` validates through Form Requests
- [x] No Vue file changed
- [x] `npm run check:fix` run; `composer ci:check` green from a clean tree
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

Wayfinder regenerates `resources/js/actions/**` and `resources/js/routes/**`
from the route table; both are gitignored, and route names are what the Vue
files import, so the generated action file for the old controller class
disappearing is expected.

Wording-tier defects found on execution, none of which changed what was
built (details in the report):

- **Decisions / Files:** `StoreEpisodeRequest` already existed. The two inline
  `validate()` calls were in `update()` and `reorder()`, so the Form Requests
  written are `UpdateEpisodeRequest` and `ReorderEpisodesRequest`.
- **Code:** the `add()` sketch (`string $type, array $attributes`) did not
  match `addEpisode()`; the "exactly" comment was followed, so the signature is
  `(Series, string, EpisodeType, EpisodeProvider, array $content = [], bool
$isPreview = false): Episode`. `update()` returns `Episode`, not `Series`.
- **Tests:** "4 cases" — seven Episode cases already lived in
  `SeriesServiceTest`; all seven moved, and `update()`/`remove()` each got the
  case they lacked, so `EpisodeServiceTest` has nine.
- **Files:** `tests/Feature/Share/EpisodeTest.php` does not exist; the Episode
  route tests are `tests/Feature/Series/EpisodeRoutesTest.php`, inside the glob
  row.
- **Preconditions:** `T-082` was merged before this started, so its allow-list
  entry was removed here, not at the merge.
