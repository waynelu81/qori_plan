---
id: T-124
title: A creator corrects a live Episode's link, time and length
stream: classroom
status: done
owner: wayne
estimate: M
depends: T-123
blocks: T-125, T-126
---

# T-124 — A creator corrects a live Episode's link, time and length

## Why

A live Episode cannot be corrected once it exists. `UpdateEpisodeRequest::rules()`
accepts `title` and `is_preview` and nothing else
(`app/Http/Requests/Share/UpdateEpisodeRequest.php:24-30`);
`EpisodeService::update()` would fill `content` and `starts_at` if a caller
passed them (`app/Services/EpisodeService.php:132-136`), but its only caller is
`EpisodeController::update()` handing over `$request->validated()`
(`app/Http/Controllers/Share/EpisodeController.php:82`), so those two lines are
unreachable; and the row controls on the creator's Series page are Move up,
Move down and Remove (`resources/js/pages/share/series/Show.vue:424-498`). A
wrong join link, a session moved by a week or a class that ran ninety minutes
instead of sixty means delete-and-re-add, which gives the Episode a new id and
drops the old one from every Access's `opened_episode_ids` and
`completed_episode_ids` (`D-026`). And a class already held cannot be re-added
at its real time at all, because `StoreEpisodeRequest` refuses a past start
(`app/Http/Requests/Share/StoreEpisodeRequest.php:105-107`) — so the recording
`T-126` lets a creator paste has nowhere to go.

`T-123` gives a live Episode an `ends_at`, a `records` switch in `content` and
the `Link` provider, and moves the start out of `content` into the column.
This task makes those things editable. Afterwards every live row on the
creator's page opens an inline form holding the current join link, the start
in the Group's zone, the length in minutes and the Recorded switch, posting to
the PATCH route that already exists. `UpdateEpisodeRequest` reads the start in
the Group's zone exactly as `StoreEpisodeRequest` does and does not require it
to be ahead; `EpisodeService::update()` writes `starts_at` and `ends_at`,
merges `join_url` and `records` into `content` under a row lock through
`LiveSessionService::withLockedContent()`, and bumps `content.schedule_version`
when the schedule moved (`D-026`), which `T-133` reads as the calendar file's
`SEQUENCE`. The toast says the new start back in the Group's zone. The Episode
keeps its id, so nobody's progress moves.

## Decisions taken to make this specifiable

**The live fields ride on the existing PATCH and the existing `update()`; no
new route and no new service method.** The page that submits already holds the
Episode's id, `share.series.episodes.update` already takes it
(`routes/share/episodes.php:21-22`), and `update()` already runs the over-cap
lock and the id-only lookup (`EpisodeService.php:128-130`). Widening one path
keeps both rules in one place.

**The start is read in the Group's zone on edit exactly as on create, and the
two Form Requests share the conversion through a concern.** The body of
`StoreEpisodeRequest::startsAtUtc()` (`:58-70`) becomes
`App\Concerns\ReadsGroupLocalTime::groupLocalToUtc(mixed $raw)` — renamed, and
handed the value instead of reading `starts_at` itself, so a request can
convert any field — and `groupTimezone()` (`:79-82`) moves unchanged; both
requests `use` the trait. `startsAtUtc()` itself stays on `StoreEpisodeRequest`
as a one-line wrapper over `groupLocalToUtc()`, because `T-130` (`ready`)
names it as the shape its own request copies, so `prepareForValidation()`
(`:44`) is untouched and its behaviour unchanged. Two copies of the one rule
that decides which hour every Peer is told would be the drift `CLAUDE.md`
forbids, and `App\Concerns\ResolvesShareSeries` is the same shape for the same
reason. `T-123` edits `StoreEpisodeRequest` first and this task depends on it,
so the two edits are sequential, not a clash.

**`after:now` is not applied on edit.** `D-026`: editing may set a past start,
so a class already held can take its recording. Creation keeps `after:now`
through `T-123`'s `guardLiveSessionTime(..., creating: true)`; `update()` calls
the same guard with `creating: false`, which still insists on a Group timezone
and lets a past instant through.

**Length is edited as `length_minutes`, and `ends_at` is derived from it, never
posted.** The same field the create form takes (`T-123`), so a creator never
sees two ways to say when a session finishes. When only `length_minutes`
arrives, `ends_at` is the current `starts_at` plus the new length; when only
`starts_at` arrives, the current length (`Episode::lengthMinutes()`) is kept
and `ends_at` moves with the start; when both arrive, both are used. A length
is an integer from 1 to `config('qori.live.max_length_minutes')`, the ceiling
`T-123` declares, interpolated into the rule and never restated.

**`schedule_version` bumps once per save in which `starts_at` or `ends_at`
changed, compared as instants.** Resubmitting the form with the same time is
not a move, and a Peer's calendar entry must not update for nothing (`T-133`).
Eloquent's own dirty check on the two datetime columns is the comparison:
inside the lock the callback sets both, and `isDirty(['starts_at', 'ends_at'])`
decides the bump. A missing `schedule_version` reads as `1`
(`Episode::scheduleVersion()`), so the first bump writes `2` and `T-123`'s
migration has nothing to backfill.

**`join_url` sent empty removes the link; `join_url` absent leaves it.** A
creator who pasted the wrong link needs a way to have none while they find the
right one. Removal unsets the key rather than storing `null`, matching what
`StoreEpisodeRequest::content()`'s `array_filter` produces (`:190-195`), so
`content` has one shape for "no link". Any other value must be `https` and at
most 2048 characters (`D-025`).

**The edit form posts `join_url`, the content key, where the create form posts
`reference`.** The create form's `reference` is one field that becomes `path`,
`video_id`, `url` or `join_url` by provider (`StoreEpisodeRequest::content()`);
the edit form only ever carries a live Episode's link and never a
provider-shaped reference, so it names the key it writes. The difference is
deliberate.

**`records` is the create form's two radios, so `0` or `1` is posted every
time.** A checkbox left unticked sends nothing, and "nothing" must not mean
"unchanged" for the one switch whose off state matters: `records = false` is
what makes `T-127`'s `not_recorded` state honest. A radio group always posts
its checked value, so the edit form reuses `T-123`'s pair — `copy.recorded`
and `copy.liveOnly` under `copy.records` — with ids of its own,
`#live-edit-records-yes` and `#live-edit-records-no`, checked from
`episode.records`.

**Every write to a live Episode's `content` goes through
`LiveSessionService::withLockedContent()`, which this task creates.** `D-026`:
`DB::transaction()`, `lockForUpdate()` on the row, `content` re-read inside the
lock. The service holds this one method now; `T-125` adds `stateFor()`,
`joinWindow()` and `joinAllowed()`, `T-127` `declareNotRecorded()` and its
undo, `T-134` cancel, restore and copy, `T-143` `attachFound()`. The callback
is `Closure(array $content, Episode $locked): array`: it receives the re-read
`content` array and the locked row, and returns the array to save. The row
rides along as the second argument because `touchSchedule()` has to compare
the new start against the locked row's and write `starts_at` and `ends_at`
under the same lock; a callback that only reads `content` — `T-127`'s two
closures as drafted — takes one parameter and is unchanged. The service
assigns what comes back, saves the row and returns it. `Episode` carries no
`BelongsToGroup` (`app/Models/Episode.php:11-19`), so the lookup inside the
lock needs no current Group, which is what the sweeps `T-128` and `T-143` add
will rely on.

**`update()` stops accepting a raw `content` key.** Today's passthrough
(`:134`) would let a caller replace the whole payload outside the lock. The
four live keys are the only way in, and a non-live Episode's `content` is
never touched by `update()` at all.

**Live fields on a non-live Episode are dropped, not refused.** A File
Episode's form never sends them; a hand-made request that does is not a case
worth a sentence. The request still validates their shape whenever they are
present, so a malformed URL is a field error whatever the Episode's type.

**`title` becomes `sometimes|required`.** The inline form posts the live fields
and nothing else, and a field that is not sent is a field that does not change.
The existing title-only PATCH (`tests/Feature/Series/LiveSessionTest.php:273-296`)
is unchanged by this.

**The toast names the new start when the schedule moved, and says "updated"
otherwise.** `series.session_rescheduled` — `:title now starts :when.` — with
`:when` in the Group's zone and the zone named, formatted `j M Y, g:ia T` as
`store()`'s `series.session_scheduled` is (`EpisodeController.php:61-68`);
that format moves into a private `whenFor()` both actions call. Whether the
schedule moved is `$episode->wasChanged(['starts_at', 'ends_at'])` on the
Episode `update()` returns. A link or switch change alone gets
`series.episode_updated`.

**The panel's initial start value is rendered by the server in the Group's
zone.** A `datetime-local` input wants `Y-m-d\TH:i` with no offset, and the
zone maths belongs with the controller that already knows the zone
(`SeriesController::show()`, `:174-177`), not in the browser. So the live row's
prop gains `startsAtLocal`; `startsAt` (ISO, with offset) stays for
`SessionTime.vue`.

**The panel finds the PATCH action itself, and this task never edits
`share/series/Show.vue`.** The `classroom` stream's claim order gives the page
to `T-123`, then `T-130`, then `T-132`, and this task may be `doing` beside
`T-130`. `LiveSessionPanel.vue` therefore reads the Group slug from
`usePage().url.split('/')[2]`, as the page does (`Show.vue:164-165`), and the
Series id from `usePage().props.series.id`, and builds the action with
Wayfinder's `update` from `@/routes/share/series/episodes`, the way
`SeriesForm.vue` binds `updateSeries.form(...)` (`:30`, `:72-73`, `:106-107`).

**No email, no reminder rows, no vendor call.** `D-028`: a rescheduled session
sends no "moved" email this sprint; `T-138` deletes the Episode's `day_before`
rows on this path and `T-143` clears `recording_checked_at` here, and each
lists `app/Services/EpisodeService.php` as its own edit. The form says so in
one line, so a creator knows to tell their Peers themselves.

**The over-cap lock and the id-only rule apply as they do to every mutation.**
`guardSeriesUnlocked()` is already the first line of `update()`; the panel's
controls follow the page's `lock.active` prop as the row controls do
(`Show.vue:449`, `:472`, `:493`), read through `usePage().props.lock.active`
because `lock` is not among the panel's props (`T-123`) and this task does not
edit the page to pass it. A slug in `{seriesId}` is not found (`ResolvesShareSeries::seriesById()`),
and `tests/Feature/Series/ShareSeriesRoutesTest.php:143-150` is the pattern the
case here follows.

## Preconditions

**Data this task verifies against:** a clean database. The tests build a
Group on plan `start` with `timezone` `Australia/Melbourne`, an accepted owner
Collaborator and a Series, as `LiveSessionTest::scene()` does
(`tests/Feature/Series/LiveSessionTest.php:41-60`), and add a live Episode
through `EpisodeService::add()` with `T-123`'s `$startsAt` and `$lengthMinutes`
parameters. The over-cap case builds its Group as
`OverCapLockTest::overCapGroup()` does (`tests/Feature/Series/OverCapLockTest.php:59-71`).

**Equipment:** a browser at phone width and at desktop width, to see the
inline form open on a row without pushing the row controls off the screen.
Nothing else; there is no vendor call and no mail.

**Spike:** none owed. No vendor payload is read or written.

## Scope

**In:**

- `UpdateEpisodeRequest`: `join_url`, `starts_at` (converted from the Group's
  zone, no `after:now`), `length_minutes`, `records`; `title` as `sometimes`.
- `App\Concerns\ReadsGroupLocalTime`, used by both Episode requests.
- `EpisodeService::update()` widened; `touchSchedule()`; the
  `LiveSessionService` dependency by constructor.
- `App\Services\LiveSessionService::withLockedContent()`.
- `Episode::scheduleVersion()`.
- `EpisodeController::update()`'s toast branch and `whenFor()`.
- `SeriesController::show()`: `startsAtLocal` on each live row (`lengthMinutes`,
  `joinUrl` and `records` are `T-123`'s, already sent under those names), and
  the edit form's copy through the panel's copy prop.
- The inline edit form on `LiveSessionPanel.vue`, per live row.
- `docs/flows/series.md` "Editing a live Episode"; `docs/tinker/series.md`
  "Correct a live session".

**Out:**

- Cancel, undo and "Add the next session" (`T-134`).
- Deleting `day_before` reminder rows when the time changes (`T-138`), and
  clearing `recording_checked_at` (`T-143`); both edit this path later.
- A "moved" email (`D-028`: none this sprint), and "Copy message for your
  chat" (`T-135`).
- Changing an Episode's `type` or `provider` — replacing it stays the honest
  path (`EpisodeService.php:118-122`).
- Editing the title or the preview flag from the page. The PATCH still takes
  them; no control sends them yet, and none is added here.
- The Peer's card, `stateFor()` and `lang/en/live.php` (`T-125`).
- Any change to the create form or to `T-123`'s validation of a new Episode.
- `share/series/Show.vue`. Not touched — see the decisions.

## Files

| Path                                                  | Change | Notes                                                                                                                                                                       |
| ----------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `app/Concerns/ReadsGroupLocalTime.php`                | new    | `groupLocalToUtc(mixed $raw)` (the body of `startsAtUtc()`, renamed, handed the value), `groupTimezone()` — moved out of `StoreEpisodeRequest`                              |
| `app/Http/Requests/Share/StoreEpisodeRequest.php`     | edit   | `use ReadsGroupLocalTime`; `groupTimezone()` deleted; `startsAtUtc()` kept as a one-line wrapper over `groupLocalToUtc()`; `prepareForValidation()` and behaviour unchanged |
| `app/Http/Requests/Share/UpdateEpisodeRequest.php`    | edit   | `prepareForValidation()`, the four live fields, `title` as `sometimes`; the docblock's "deliberately not…" line kept                                                        |
| `app/Services/LiveSessionService.php`                 | new    | `withLockedContent()` only; `T-125` adds `stateFor()`, `joinWindow()`, `joinAllowed()`; `T-127`, `T-134`, `T-143` edit it                                                   |
| `app/Services/EpisodeService.php`                     | edit   | constructor takes `LiveSessionService`; `update()` widened; `touchSchedule()`; raw `content` passthrough removed                                                            |
| `app/Models/Episode.php`                              | edit   | `scheduleVersion(): int`                                                                                                                                                    |
| `app/Http/Controllers/Share/EpisodeController.php`    | edit   | `update()` picks the toast; `whenFor()` shared with `store()`                                                                                                               |
| `app/Http/Controllers/Share/SeriesController.php`     | edit   | live row prop `startsAtLocal` (beside `T-123`'s `lengthMinutes`, `joinUrl`, `records`); the edit form's copy lines                                                          |
| `resources/js/components/series/LiveSessionPanel.vue` | edit   | the inline edit form per live row, action from Wayfinder                                                                                                                    |
| `lang/en/series.php`                                  | edit   | `session_rescheduled`, `live.edit.*`                                                                                                                                        |
| `docs/flows/series.md`                                | edit   | "Editing a live Episode": the chain, the lock, `schedule_version`, what is not sent                                                                                         |
| `docs/tinker/series.md`                               | edit   | "Correct a live session" recipe after "Add episodes"                                                                                                                        |
| `tests/Feature/Series/EditLiveEpisodeTest.php`        | new    | 17 cases                                                                                                                                                                    |
| `tests/Feature/Series/LiveSessionServiceTest.php`     | new    | 2 cases                                                                                                                                                                     |

No route file changes: the PATCH exists. No config: `qori.live.max_length_minutes`
and `default_length_minutes` are `T-123`'s. No migration, factory or seeder:
`ends_at` is `T-123`'s column and `schedule_version` is a key in `content`.

## Database

None. `schedule_version` lives inside `episodes.content` (`D-026`), and
`episodes.ends_at` is added by `T-123`'s migration.

## Code

```php
namespace App\Concerns;

use App\Support\CurrentGroup;
use App\Support\Timezones;
use Carbon\CarbonImmutable;
use Throwable;

/**
 * A naive datetime-local string, read in the Group's zone and returned as UTC.
 *
 * The body of StoreEpisodeRequest::startsAtUtc() as it stood before this task,
 * renamed and handed the value instead of reading starts_at itself, and
 * groupTimezone() unchanged — moved so the create and the edit request cannot
 * disagree about what 9am means. The hour a creator types is measured in
 * their Group's zone; what a Peer sees is a display question.
 */
trait ReadsGroupLocalTime
{
    /** Null for a blank or unparseable value, so ['date'] can say "not a date" itself. */
    protected function groupLocalToUtc(mixed $raw): ?CarbonImmutable
    {
        if (! is_string($raw) || trim($raw) === '') {
            return null;
        }

        try {
            return CarbonImmutable::parse(trim($raw), $this->groupTimezone())->utc();
        } catch (Throwable) {
            return null;
        }
    }

    protected function groupTimezone(): string
    {
        return app(CurrentGroup::class)->get()?->timezone() ?? Timezones::fallback();
    }
}
```

```php
// App\Http\Requests\Share\StoreEpisodeRequest — `use ReadsGroupLocalTime;` at the top of the class;
// private groupTimezone() (:79-82) deleted; prepareForValidation() (:42-49) untouched. startsAtUtc()
// keeps its name and its docblock and becomes the one line below, so T-130's citation of it still holds.
private function startsAtUtc(): ?CarbonImmutable
{
    return $this->groupLocalToUtc($this->input('starts_at'));
}
```

```php
namespace App\Http\Requests\Share;

use App\Concerns\ReadsGroupLocalTime;
use Illuminate\Foundation\Http\FormRequest;

class UpdateEpisodeRequest extends FormRequest
{
    use ReadsGroupLocalTime;

    /** As StoreEpisodeRequest: the start becomes UTC before any rule sees it. */
    protected function prepareForValidation(): void
    {
        $utc = $this->groupLocalToUtc($this->input('starts_at'));

        if ($utc !== null) {
            $this->merge(['starts_at' => $utc->toIso8601String()]);
        }
    }

    /** @return array<string, array<int, string>> */
    public function rules(): array
    {
        return [
            // A field not sent is a field not changed; the live form sends no title.
            'title' => ['sometimes', 'required', 'string', 'max:200'],
            'is_preview' => ['boolean'],

            // Live fields (D-026). Validated for shape whenever present;
            // EpisodeService::update() drops them for a non-live Episode.
            // No after:now — a class already held may be moved to its real time.
            'join_url' => ['sometimes', 'nullable', 'string', 'url:https', 'max:2048'],
            'starts_at' => ['sometimes', 'date'],
            'length_minutes' => ['sometimes', 'integer', 'min:1', 'max:'.config('qori.live.max_length_minutes')],
            'records' => ['sometimes', 'boolean'],
        ];
    }
}
```

```php
namespace App\Services;

use App\Models\Episode;
use Closure;
use Illuminate\Support\Facades\DB;

/**
 * A live Episode's session (D-026). This task: the one write path. T-125 adds
 * stateFor(), joinWindow() and joinAllowed(); T-127 declareNotRecorded() and
 * declareRecorded(); T-134 cancel(), restore() and copy(); T-143 attachFound().
 */
class LiveSessionService
{
    /**
     * Run one write to a live Episode under a row lock.
     *
     * DB::transaction(), lockForUpdate() on the row, and the row re-read inside
     * the lock, so a sweep and a creator's edit cannot overwrite each other's
     * content. The callback receives the re-read content array and the locked
     * Episode, and returns the content to save; a column — starts_at, ends_at,
     * title, is_preview — is set on the locked row inside the callback. This
     * assigns what comes back, saves the row and returns it. A null content
     * column reaches the callback as []. Episode carries no group scope, so no
     * current Group is needed.
     *
     * @param  Closure(array<string, mixed>, Episode): array<string, mixed>  $callback
     */
    public function withLockedContent(Episode $episode, Closure $callback): Episode
    {
        return DB::transaction(function () use ($episode, $callback): Episode {
            /** @var Episode $locked */
            $locked = Episode::query()->whereKey($episode->getKey())->lockForUpdate()->firstOrFail();

            $locked->content = $callback($locked->content ?? [], $locked);

            $locked->save();

            return $locked;
        });
    }
}
```

```php
// App\Models\Episode — one accessor beside lengthMinutes() (T-123).

/** The calendar file's SEQUENCE (T-133). Absent reads as 1, so the first move writes 2. */
public function scheduleVersion(): int
{
    return (int) ($this->content['schedule_version'] ?? 1);
}
```

```php
// App\Services\EpisodeService — constructor added; update() rewritten; one private method.

public function __construct(private LiveSessionService $liveSessions) {}

/**
 * Change an Episode's own details, and a live Episode's session (D-026).
 *
 * Keys read: title, is_preview, starts_at (ISO UTC string or CarbonInterface),
 * length_minutes (int), join_url (string; blank removes it), records (bool).
 * A raw `content` key is no longer accepted: the live keys are the only way
 * into content, and they are merged under the row lock. Type and provider
 * still cannot change. Live keys on a non-live Episode are dropped.
 *
 * @param  array<string, mixed>  $attributes
 */
public function update(Series $series, string $episodeId, array $attributes): Episode
{
    $this->guardSeriesUnlocked($series->group, 'edit an episode');

    $episode = $this->episodeOrFail($series, $episodeId);

    $title = array_key_exists('title', $attributes) ? trim((string) $attributes['title']) : null;
    $isPreview = array_key_exists('is_preview', $attributes) ? (bool) $attributes['is_preview'] : null;

    if (! $episode->isLive()) {
        $episode->fill(array_filter(['title' => $title], fn ($value): bool => $value !== null));

        if ($isPreview !== null) {
            $episode->is_preview = $isPreview;
        }

        $episode->save();

        return $episode;
    }

    $startsAt = isset($attributes['starts_at']) ? $this->instant($attributes['starts_at']) : null;
    $lengthMinutes = isset($attributes['length_minutes']) ? (int) $attributes['length_minutes'] : null;

    // Timezone still required; a past instant allowed (T-123's flag).
    $this->guardLiveSessionTime($series, $episode->type, $startsAt, creating: false);

    return $this->liveSessions->withLockedContent($episode, function (array $content, Episode $locked) use ($attributes, $title, $isPreview, $startsAt, $lengthMinutes): array {
        if ($title !== null) {
            $locked->title = $title;
        }

        if ($isPreview !== null) {
            $locked->is_preview = $isPreview;
        }

        if (array_key_exists('join_url', $attributes)) {
            $url = trim((string) $attributes['join_url']);

            if ($url === '') {
                unset($content['join_url']);
            } else {
                $content['join_url'] = $url;
            }
        }

        if (array_key_exists('records', $attributes)) {
            $content['records'] = (bool) $attributes['records'];
        }

        if ($startsAt !== null || $lengthMinutes !== null) {
            $content = $this->touchSchedule($locked, $content, $startsAt, $lengthMinutes);
        }

        return $content;
    });
}

/**
 * Write the start and the derived end on the locked row, and bump
 * schedule_version in the content when either moved. Eloquent's dirty check
 * on the two datetime casts is the comparison, so resubmitting the same time
 * is not a move.
 *
 * @param  array<string, mixed>  $content
 * @return array<string, mixed>
 */
private function touchSchedule(Episode $locked, array $content, ?CarbonImmutable $startsAt, ?int $lengthMinutes): array
{
    $start = $startsAt ?? CarbonImmutable::instance($locked->starts_at);
    $length = $lengthMinutes ?? $locked->lengthMinutes() ?? (int) config('qori.live.default_length_minutes');

    $locked->starts_at = $start;
    $locked->ends_at = $start->addMinutes($length);

    if ($locked->isDirty(['starts_at', 'ends_at'])) {
        $content['schedule_version'] = $locked->scheduleVersion() + 1;
    }

    return $content;
}

private function instant(mixed $value): CarbonImmutable
{
    return $value instanceof CarbonInterface
        ? CarbonImmutable::instance($value)
        : CarbonImmutable::parse((string) $value);
}
```

```php
// App\Http\Controllers\Share\EpisodeController — update() and the shared formatter.
// Two imports join the list at :5-16, for whenFor()'s signature:
use App\Models\Episode;
use App\Models\Series;

public function update(
    string $group,
    string $seriesId,
    string $episodeId,
    UpdateEpisodeRequest $request,
    EpisodeService $episodeService,
    Terminology $terminology,
): RedirectResponse {
    $series = $this->seriesById($seriesId);
    $episode = $episodeService->update($series, $episodeId, $request->validated());

    Inertia::flash('toast', [
        'type' => 'success',
        // The hour said back when it moved, for the reason store() gives:
        // what was typed was a local time and what was stored is an instant.
        'message' => $episode->isLive() && $episode->wasChanged(['starts_at', 'ends_at'])
            ? $terminology->line('series.session_rescheduled', [
                'title' => $episode->title,
                'when' => $this->whenFor($episode, $series),
            ])
            : $terminology->line('series.episode_updated'),
    ]);

    return back();
}

/** The start in the Group's zone with the zone named; store() uses it too (its :61-68 inline today). */
private function whenFor(Episode $episode, Series $series): string
{
    return $episode->starts_at
        ->setTimezone($series->group?->timezone() ?? Timezones::fallback())
        ->format('j M Y, g:ia T');
}
```

```php
// App\Http\Controllers\Share\SeriesController::show() — on each Episode row (:158-166), one key
// beside T-123's endsAt, lengthMinutes, records and joinUrl, null for a non-live Episode:
'startsAtLocal' => $episode->isLive() && $episode->starts_at
    ? $episode->starts_at->setTimezone($scope?->timezone() ?? Timezones::fallback())->format('Y-m-d\TH:i')
    : null,

// and, in the copy object T-123 hands LiveSessionPanel.vue, four more lines through $terminology->line():
'edit' => [
    'open' => $terminology->line('series.live.edit.open'),
    'noEmail' => $terminology->line('series.live.edit.no_email'),
    'save' => $terminology->line('series.live.edit.save'),
    'close' => $terminology->line('series.live.edit.close'),
],
```

```ts
// resources/js/components/series/LiveSessionPanel.vue — the edit form, per live row.
import { computed, ref } from 'vue';
import { Form, usePage } from '@inertiajs/vue3';
import { update as updateEpisode } from '@/routes/share/series/episodes';

// T-123's exported `LiveEpisode` gains two keys. `id` is what the page's
// `EpisodeSummary` already carries; `startsAtLocal` is optional on the type so
// that `:episode="episode"` on the page still type-checks with no page edit,
// and is on every row at runtime because SeriesController::show() sends it.
//   id: string;
//   startsAtLocal?: string | null;   // 'Y-m-d\TH:i' in the Group's zone, from the server
// `LiveCopy` gains `edit: { open: string; noEmail: string; save: string; close: string }`.

const page = usePage<{ series: { id: string }; lock: { active: boolean } }>();
const groupSlug = computed(() => page.url.split('/')[2] ?? '');
const editing = ref(false);
// Row mode only, where `episode` is required (T-123).
const action = computed(() =>
    updateEpisode.form({
        group: groupSlug.value,
        seriesId: page.props.series.id,
        episodeId: props.episode?.id ?? '',
    }),
);
```

The form, shown when `editing` is true, is `<Form v-bind="action" v-slot="{ errors, processing }">`
with, in this order: `join_url` (`type="url"`, `:value="episode.joinUrl ?? ''"`,
under `copy.joinLink`); `starts_at` (`type="datetime-local"`,
`:value="episode.startsAtLocal"`, under `copy.starts`, whose `:zone` is the
Group's zone); `length_minutes` (`type="number"`, `min="1"`,
`:max="defaults.maxLengthMinutes"`, `:value="episode.lengthMinutes"`, under
`copy.length`); the create form's two radios named `records`,
`#live-edit-records-yes` (value `1`, `:checked="episode.records"`) labelled
`copy.recorded` and `#live-edit-records-no` (value `0`,
`:checked="!episode.records"`) labelled `copy.liveOnly`, under `copy.records`;
`<InputError>` under each field; the `copy.edit.noEmail` line; a submit
`Button` labelled `copy.edit.save` and a plain button labelled
`copy.edit.close` that sets `editing` false. The toggle that opens it is a
text button labelled `copy.edit.open`, rendered inside the panel's row-mode
output after the badge and the `copy.noLink` line (the row's Move and Remove
controls sit in the page's own markup, which this task does not touch). Every
control is `:disabled="processing || page.props.lock.active"`.
`defaults.maxLengthMinutes` and the field labels are the props `T-123` already
gives the panel for its create form; nothing is re-declared and no English is
written in the component.

`docs/flows/series.md` gains a section "Editing a live Episode" after
`T-123`'s "Live Episodes" subsection:

```
PATCH /g/{group}/series/{seriesId}/episodes/{episodeId}   (share.series.episodes.update)
  └─ UpdateEpisodeRequest         starts_at read in the Group's zone (ReadsGroupLocalTime); no after:now
       └─ EpisodeController@update
            └─ EpisodeService::update()
                 ├─ guardSeriesUnlocked()          the over-cap lock
                 ├─ episodeOrFail()                id only, inside this Series
                 ├─ guardLiveSessionTime(creating: false)   zone required, past allowed
                 └─ LiveSessionService::withLockedContent()  transaction + lockForUpdate + re-read
                      ├─ join_url set or unset, records set
                      └─ touchSchedule()           ends_at = starts_at + length; schedule_version++ when either moved
```

with the sentence that nothing is emailed and no reminder row is touched here.
`docs/tinker/series.md` gains "Correct a live session":

```php
$live = $series->fresh()->orderedEpisodes()->firstWhere('type', App\Enums\EpisodeType::Live);

$episodes->update($series->fresh(), (string) $live->getKey(), [
    'join_url' => 'https://zoom.us/j/987654321?pwd=abc',
    'starts_at' => now()->addWeeks(2),
    'length_minutes' => 90,
]);

$live->fresh()->ends_at;                    // two weeks on, 90 minutes after the start
$live->fresh()->scheduleVersion();          // 2
```

## Copy

| Key                          | File                 | English                                                             |
| ---------------------------- | -------------------- | ------------------------------------------------------------------- |
| `series.session_rescheduled` | `lang/en/series.php` | :title now starts :when.                                            |
| `series.live.edit.open`      | `lang/en/series.php` | Edit link, time and length                                          |
| `series.live.edit.no_email`  | `lang/en/series.php` | No email goes out about a change — tell your :peer_plural yourself. |
| `series.live.edit.save`      | `lang/en/series.php` | Save changes                                                        |
| `series.live.edit.close`     | `lang/en/series.php` | Close                                                               |

`session_rescheduled` sits beside `session_scheduled` (`lang/en/series.php:39`)
with a comment saying it is the same sentence for a move. `:when` is filled by
`whenFor()`. The four `live.edit.*` lines reach the component as props from
`SeriesController::show()`. `Close`, not "Cancel": `T-134` puts "Cancel
session" on the same row, and two buttons that both say cancel is the mistake
that loses a session. The field labels, the Recorded switch's wording and the
length ceiling's message are `T-123`'s and are reused; the validation message
for `length_minutes` is the framework's, with the ceiling interpolated from
config by the rule. `TerminologyTest` walks every line for an article before
a noun placeholder; none of these has one.

## Routes

None new. The existing route is widened by what its Form Request accepts:

| Verb  | Path                                                | Name                           | Action                            |
| ----- | --------------------------------------------------- | ------------------------------ | --------------------------------- |
| PATCH | `/g/{group}/series/{seriesId}/episodes/{episodeId}` | `share.series.episodes.update` | `Share\EpisodeController::update` |

## Tests

**New: `tests/Feature/Series/EditLiveEpisodeTest.php` — 17 cases**
(`scene()` as `LiveSessionTest.php:41-60`; a `live()` helper adding a Zoom
Episode through `EpisodeService::add()` starting `2026-10-01T09:00` Melbourne
with a 60-minute length; a `patch()` helper posting to
`route('share.series.episodes.update', [...])` as `LiveSessionTest.php:285-289`)

1. `test_it_corrects_the_join_link` — `join_url` `https://zoom.us/j/999`
   alone; `content['join_url']` is the new link, `starts_at` and `ends_at`
   unchanged, `scheduleVersion()` still `1`, title unchanged.
2. `test_it_removes_the_join_link_when_it_is_sent_empty` — `join_url` `''`;
   `content` has no `join_url` key.
3. `test_it_refuses_a_join_link_that_is_not_https` — `http://zoom.us/j/1`;
   `assertSessionHasErrors('join_url')`; content unchanged.
4. `test_it_moves_the_start_and_bumps_the_schedule_version` — `starts_at`
   `2026-10-15T09:00`, which is across Melbourne's daylight-saving boundary
   from the 1 October start; `starts_at` is `2026-10-14T22:00:00+00:00`,
   `ends_at` is `2026-10-14T23:00:00+00:00` (the old length kept),
   `scheduleVersion()` is `2`.
5. `test_it_reads_the_new_start_in_the_groups_zone` — `starts_at`
   `2026-10-02T09:00`; stored as `2026-10-01T23:00:00+00:00`, asserted as a
   literal string as `LiveSessionTest.php:130-133` does.
6. `test_it_changes_the_length_and_moves_the_end` — `length_minutes` `90`
   alone; `starts_at` unchanged, `ends_at` is `starts_at` + 90 minutes,
   `scheduleVersion()` is `2`.
7. `test_it_does_not_bump_the_schedule_version_for_an_unchanged_time` — the
   current start and length resubmitted; `scheduleVersion()` stays `1` and the
   toast is `series.episode_updated`.
8. `test_it_accepts_a_past_start_on_edit` — `starts_at` yesterday in the
   Group's zone; saved; the create route with the same value still
   `assertSessionHasErrors('starts_at')`.
9. `test_it_refuses_a_length_over_the_maximum` — `config('qori.live.max_length_minutes') + 1`;
   `assertSessionHasErrors('length_minutes')`.
10. `test_it_switches_recording_off_and_on` — `records` `0` then `1`;
    `content['records']` is `false` then `true`; `scheduleVersion()` untouched.
11. `test_it_ignores_live_fields_on_a_file_episode` — a File Episode PATCHed
    with `title`, `join_url`, `starts_at`, `records`; the title changes,
    `content` is still `['path' => …]`, `starts_at` and `ends_at` are null.
12. `test_it_says_the_new_start_back_in_the_groups_zone` — after case 4's
    PATCH, `assertSessionHas(Inertia\Support\SessionKey::FLASH_DATA, …)` sees a
    `success` toast equal to `series.session_rescheduled` with `:when`
    `15 Oct 2026, 9:00am AEDT`, read the way `tests/Feature/Access/SeriesAccessCodeTest.php:87-90` reads a
    toast.
13. `test_it_sends_no_email_when_a_session_moves` — `Notification::fake()`;
    case 4's PATCH; `Notification::assertNothingSent()`.
14. `test_it_keeps_the_episode_id_and_the_peers_progress` — an Access whose
    `completed_episode_ids` holds the Episode's id
    (`ProgressService::completeFor()`); after a move the Episode's id is the
    same and the Access still `hasCompleted()` it (owner acceptance 12).
15. `test_it_does_not_resolve_a_slug_on_the_patch` — the Series slug in
    `{seriesId}`; 404; nothing changed (`ShareSeriesRoutesTest.php:143-150`).
16. `test_it_cannot_edit_another_groups_episode` — a second scene's Series
    and Episode ids under the first Group's slug; 404; nothing changed.
17. `test_it_is_refused_while_the_group_is_over_its_cap` — `overCapGroup()`;
    the PATCH answers `ErrorCode::PlanLimitReached`; nothing changed.

**New: `tests/Feature/Series/LiveSessionServiceTest.php` — 2 cases**

1. `test_it_re_reads_the_row_inside_the_lock` — load the Episode, then write
   `content['join_url']` through `DB::table('episodes')` behind its back; call
   `withLockedContent()` with a callback that returns the `$content` it was
   handed plus `records => false`; the stored content holds both keys.
2. `test_it_saves_what_the_callback_set_and_returns_the_fresh_row` — the
   callback sets `title` and `ends_at` on the `$locked` Episode it was handed
   and returns `$content` unchanged; the returned Episode is not the instance
   passed in, and `fresh()` shows both.

**Changed:** none. `tests/Feature/Share/EpisodeServiceTest.php:162-181`
(`test_update_changes_the_title_and_preview_flag_only`) still holds for the
File Episode it uses, and `tests/Feature/Series/LiveSessionTest.php:273-296`
(`test_editing_an_episode_keeps_the_time_it_had`) still posts a title alone and
passes under `sometimes`. `tests/Feature/Series/EpisodeRoutesTest.php:155-166`
is unchanged for the same reason.

Total: 19 new cases.

## Acceptance

- [x] On the Series page, each live Episode row opens an inline form holding
      its current link, start in the Group's zone, length and Recorded switch,
      at phone width and at desktop width, with the Move and Remove controls
      still reachable
- [x] Saving a moved time shows the row's new time and a toast naming the new
      start with the zone; saving a link or the switch alone says "updated"
      (owner acceptance 2: the hour typed is read in the Group's zone and the
      stored instant is right on both sides of a daylight-saving boundary)
- [x] A class already held can be moved to its real, past time; adding a new
      live Episode with a past start is still refused
- [x] Moving the time or the length bumps `schedule_version` exactly once;
      resubmitting the same values bumps nothing (owner acceptance 14: the
      calendar file `T-133` builds updates on a reschedule and not otherwise)
- [x] The Episode keeps its id through every edit, and every Access's
      `opened_episode_ids` and `completed_episode_ids` still name it (owner
      acceptance 12)
- [x] A File Episode's PATCH drops the live fields; a slug in the action, another
      Group's Episode and an over-cap Group each get the refusal the tests name
- [x] No email is sent by a change, and the form says so
- [x] `docs/flows/series.md` describes the edit chain and the lock; the
      `docs/tinker/series.md` recipe runs
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Specified on 17 September 2026 from `D-026`, with `D-025` for the link's
shape and `D-028` for what is not sent. The owner's acceptance scenarios it
answers are 2, 12 and 14 (`docs/planning/course-classroom.md`).

**`T-125`'s draft is edited to list `app/Services/LiveSessionService.php` as
`edit`, not `new`, and to depend on this task:** this task creates the class
with `withLockedContent()`, and `T-125` adds `stateFor()`, `joinWindow()` and
`joinAllowed()` to it. Its front matter gained `T-124` under `depends:` on
18 September 2026, so the two are sequential on that file, as the `classroom`
stream's claim order says. `T-127`, `T-134` and `T-143` already say `edit`.

**The `withLockedContent()` callback is
`Closure(array $content, Episode $locked): array`, settled here.** `T-127`'s
two closures (`declareNotRecorded()`, `declareRecorded()`) take the content
array and return it, which is this shape with the second parameter left off,
so they stand as drafted. `T-134`'s draft is edited to it: its `cancel()` and
`restore()` closures take `array $content` and return it with `cancelled_at`
set or unset, and its Notes line saying `T-127` is rewritten to an
Episode-only shape is struck.

`T-123` already exports `LiveEpisode` from `LiveSessionPanel.vue`; this task
adds `id: string` and `startsAtLocal?: string | null` to it. `startsAtLocal`
is optional on the type because the page's `EpisodeSummary` lists `T-123`'s
keys by hand and does not import `LiveEpisode`, so a required key would fail
`:episode="episode"` on a page this task does not edit; `SeriesController::show()`
sends it on every row regardless. `lengthMinutes`, `joinUrl` and `records`
are `T-123`'s, sent under exactly those names, and this task adds nothing to
them.

`T-130` (`ready`) copies the shape of `StoreEpisodeRequest::startsAtUtc()` by
name into its `StoreMaterialRequest`, which is why that method stays as a
one-line wrapper over `groupLocalToUtc()` rather than being deleted;
`ReadsGroupLocalTime` is there for a later request to `use` instead of copying.

`T-138` and `T-143` each list `app/Services/EpisodeService.php` as their own
edit for what they add to this path (reminder rows, `recording_checked_at`);
nothing here anticipates either.

`UpdateEpisodeRequest`'s docblock ("Deliberately not the type or the
provider", `:7-14`) stays true and stays; the sentence about replacing the
Episode being one click is no longer the whole story for a live one, and the
docblock gains a line saying the session's own fields are edited in place.

**Executed 19 September 2026 — wording-tier fixes** (`reports/T-124-2026-09-19-wayne.md`):

- The Tests section's `patch()` helper collides with Laravel's own
  `TestCase::patch()` (PHP refuses the narrower visibility); it is
  `patchEpisode()`.
- `touchSchedule()` writes the two columns through `fill()`, not by assigning
  the properties: `Episode`'s `@property ?Carbon` describes what a read
  returns, and PHPStan (level 7) refuses a `CarbonImmutable` assigned to it.
- `touchSchedule()` leaves the row as it was when there is no start anywhere —
  a live Episode a service caller added without one, edited with a length
  alone. The Code section's `CarbonImmutable::instance($locked->starts_at)`
  would throw a `TypeError` there.
- `instant()` returns UTC. The dirty check compares what Eloquent would write,
  a wall-clock string in the value's own zone, so the same instant in another
  zone would count as a move and bump `schedule_version`.
- `EditLiveEpisodeTest::scene()` freezes the clock on 1 September 2026, as
  `T-123` does for `LiveSessionTest`: `live()` adds a 1 October session
  through the create guard, which refuses it from that day on.
- Cases 15 to 17 use `patchJson()`. A plain PATCH that fails answers a
  redirect with a toast, so "404" and "answers `plan_limit_reached`" are only
  visible as a status and an `error.code` on a JSON request.
- The form's three inputs take `:model-value`, not `:value`: the `Input`
  component owns its value through `v-model`, and a fallthrough `value` would
  fight it.
