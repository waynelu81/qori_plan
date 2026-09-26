---
id: T-126
title: A creator adds a recording link to a live Episode, and Peers watch it from the same card
stream: classroom
status: doing
owner: claude
estimate: M
depends: T-124, T-125
blocks: T-127
---

# T-126 — A creator adds a recording link to a live Episode, and Peers watch it from the same card

> **Draft.** Not specified to be started — see [`../PROCESS.md`](../PROCESS.md).
> What has to be decided before it can be marked `ready` is listed at the
> bottom. Written on 17 September 2026 from `D-024` and `D-027`, on top of
> `T-089`'s Open route and `T-125`'s card, both drafts.

## Why

A live Episode has nothing after the session. Its `content` holds a `join_url`
and, after `T-123`, the `records` switch
(`app/Http/Requests/Share/StoreEpisodeRequest.php:190-195` writes the arm
today), and nothing that could name a recording;
`PlaybackTicketService::resolve()` throws `errors.playback.unsupported_provider`
for a live Episode (`app/Services/PlaybackTicketService.php:83-89`); and
nothing in the schema can hold a recording
(`database/migrations/2026_09_08_000000_create_qori_schema.php:103-118`).
`T-100`'s draft made a recording a second Video Episode, which `D-024`
rejected: a second card is a second certificate requirement with no link back
to the class. After `T-125`, Join works while the clock says so and the card's
`waiting` line promises that if the session was recorded, the recording will be
added here — and there is no way to add one.

Afterwards, recordings are rows in `episode_recordings` (`D-027`). The creator
pastes the recording's link and its passcode on the same row of
`LiveSessionPanel.vue`; the row is published on paste, because the creator's
act is the review. `LiveSessionService::stateFor()` answers `ready` once Join
has closed and a published, unhidden recording exists, and the Peer's `LiveSessionCard.vue`
shows **Watch recording** — Part 1, Part 2 when there are several — with the
passcode beside it, as an `<a>` to `T-089`'s `shared.episodes.open` route with
`?recording={id}`. Watch passes the gate Join passes, writes one `access_opens`
row with `target = recording` and marks the Episode opened, exactly as `/play`
does today (`PlaybackTicketService.php:70`). Nothing is emailed yet: `T-128`
adds the notice to the paste. Hiding, a second link's control, "There's no
recording" and the `overdue` line are `T-127`'s.

## Decisions taken to make this specifiable

**A recording is a row in `episode_recordings`, never an entry in `content`.**
`D-027`: a homogeneous list with its own lifecycle, a uniqueness the sweep
must not violate and a foreign key from `T-128`'s ledger is a relational
entity, and adding the table after this task was frozen would be a re-scope of
a done task.

**A pasted link is published on paste.** `D-027`: `published_at = now()`,
`needs_review = false`, `source = link`, `vendor_ref = null`. Review-first is
for a recording Qori found (`T-143`), not one the creator chose.

**Watch is `T-089`'s Open route with `?recording={id}`, not a sibling route.**
Join and Watch pass the same gate — access, then the Episode, then the open
recorded — and the card renders one `<a>` shape for both. The card holds
neither id — `T-125` gives it `live` and `joinHref` and nothing else — so each
recording's `href` is built on the server, as
`route('shared.episodes.open', [$seriesId, $episodeId, 'recording' => $id])`,
and `resources/js/pages/shared/Show.vue` is not edited. The Episode stays
the unit of progress (`D-024`), so the recording is named as a part of it, in
the query, rather than as a thing of its own in the path. Whether a sibling
`shared.recordings.open` is preferred is listed under "Before this can be
ready".

**`open()` gains a nullable fourth parameter rather than a second method.**
`open(User $peer, string $seriesId, string $episodeId, ?string $recordingId = null)`,
as the brief names it. `T-091` puts its ensure-the-grant step into `open()`
between `admit()` and the resolve; a second method would need that step
twice. `issue()` and `admit()` are untouched, so `T-089`'s tests run as they
are.

**The Peer surface reads recordings inside `CurrentGroup::runFor($series->group, …)`,
set once by each caller that holds the Series.** `EpisodeRecording` carries
`BelongsToGroup`, so `Episode::recordings()` is scoped by `GroupScope`, which
throws with no current Group (`app/Models/Scopes/GroupScope.php:24`), and the
Peer is inside no Group. `->forGroup($series->group)` is the brief's helper
for a Peer read and would serve here — except inside `stateFor()`, whose
signature is the Episode and the clock (`T-125`) and which has no way to the
Group: `Series` carries `BelongsToGroup` too (`app/Models/Series.php:49`), so
`Episode::series()` is a scoped read as well. The `ready` arm therefore runs
under a context, and the two Peer callers that hold the Series set it once —
`SharedController::liveCard()` around its whole array,
`PlaybackTicketService::watch()` around its lookup — the way `connectionFor()`
already reads a Connection (`app/Services/PlaybackTicketService.php:112-115`).
Every read inside — the state, the list, the Watch lookup — then goes through
the same relation the creator's page uses. `T-131` and `T-132` read `Material`
and `SeriesChat` with `->forGroup($series->group)` because they query the model
with the Series in hand; this task diverges from them for the reason above,
and `acrossAllGroups()` is never used.

**`stateFor()` answers `Ready` once Join has closed: after `T-125`'s
`cancelled`, `upcoming` and `open` arms, before `not_recorded`, `waiting` and
`overdue`, and whatever `records` says.** The order is `cancelled`,
`upcoming`, `open`, `ready`, `not_recorded`, `waiting`, `overdue` — the one
`T-127` already builds on. A recording pasted before or during the session
must not take Join off the Peer's card, so the two clock arms that offer Join
keep winning until the window closes; from then on a recording is a fact Qori
holds and the Recorded/Live-only switch was the creator's plan, so `ready`
beats `not_recorded`.

**A pasted recording's `started_at` and `duration_minutes` are the Episode's
own `starts_at` and length.** `D-027` declares both columns not null; the
creator has no better figure than the schedule, and `T-144`'s list reads the
same two columns for a found recording, so both sources render alike.

**A hidden or unpublished recording answers a 404, `errors.live.recording_unavailable`
— not a 403, and not `D-020`'s redirect.** The Peer has access and the thing
is not there. `D-020`'s redirect to the Series page is for a link Qori will
not follow _yet_; a hidden recording is gone, and the `resolution` says where
what remains is listed.

**`group_id` is written explicitly on paste, from the Series.** The creator's
request has a current Group, so `BelongsToGroup`'s creating hook would stamp
it, but `T-143`'s sweep inserts the same rows from a command, and `T-125`'s
`AccessOpen::record()` sets it explicitly for the same reason. One rule for
every writer.

**A paste serialises on the Episode row.** `DB::transaction()` with
`lockForUpdate()` on the Episode — the row `LiveSessionService::withLockedContent()`
locks (`T-125`) and `T-143`'s `attachFound()` will lock — so `position` is
read under the lock and a paste and a sweep never interleave. The paste writes
no `content`, so it does not go through `withLockedContent()` itself.

**The creator's form shows on every live row that has no recording yet,
whatever the clock says.** A class held early, or recorded on a rehearsal
run, has a recording before the scheduled end, and the panel carries no state
until a later task gives it one. `T-127` adds "Add another link" beside the
list, so this task renders no form once a recording exists.

**The recording's URL never enters a Peer-facing prop.** The passcode does,
because `D-027` shows it to every Peer with access and the card prints it.
The link is reached only through Watch, so revoking an Access revokes the
recording, as `/play` does for a file. The creator's own page carries the URL,
because it is theirs.

**Copy is resolved on the server, one string per recording.** `label`,
`passcodeLine` and `availableLine` arrive as text in the prop, as `T-125`'s
`copy` does, so the card interpolates nothing and holds no English.

**`$by` reaches the log line and is not stored.** `D-027` has no column for
who pasted; the parameter is kept so `T-144`'s `publish(EpisodeRecording $recording, User $by)`
mirrors it, and the log line says who did it.

**`RecordingController` takes its services by method injection, as
`EpisodeController` does** (`app/Http/Controllers/Share/EpisodeController.php:34-40`),
and resolves the Episode inside the Series itself with
`errors.series.episode_not_found`: `EpisodeService::episodeOrFail()` is private
(`app/Services/EpisodeService.php:185-199`), and `ResolvesShareSeries` is not
edited because `T-130`'s `MaterialController` may be `doing` at the same time
and the concern is one file.

**No factory and no seeder row.** Tests create recordings through `paste()`,
as they create Episodes through `EpisodeService::add()` (there is no
`EpisodeFactory`), and `DesignReviewSeeder`'s live session is in the future
with nothing to watch.

**No email on paste in this task.** `T-128` adds
`SessionNoticeService::queueRecordingReady()` to `paste()`; the creator's flash
and the panel's help line say Peers see it on the page, and say nothing about
mail.

## Preconditions

**Data this task verifies against:** a clean database. The feature tests build
a Group with a chosen `timezone` and an owner Collaborator, as
`tests/Feature/Series/LiveSessionTest.php:41-60` does; a published Series with
one live Episode added through `EpisodeService::add()` with `T-123`'s
`$startsAt` and `$lengthMinutes` parameters; a Peer given access through
`AccessService::grant()`; and `Carbon::setTestNow()` to place the clock after
the scheduled end.

**Equipment:** none. `php artisan wayfinder:generate --with-form` after the
route is added, so `@/routes/share/series/episodes/recordings` exists for the
panel's form; the Peer's Watch `href` is built on the server and needs nothing
generated. A visible browser is useful to see the card, and not needed to
verify anything below.

**Spike:** none owed. No vendor payload is read; a `link` recording opens
exactly as stored.

## Scope

**In:**

- The `episode_recordings` table, `EpisodeRecording`, `RecordingSource`,
  `Episode::series()`, `Episode::recordings()`, `Episode::visibleRecordings()`.
- `RecordingService::paste()`, `StoreRecordingRequest`, `RecordingController::store()`
  and the route `share.series.episodes.recordings.store`.
- The `Ready` arm in `LiveSessionService::stateFor()`.
- Watch: `PlaybackTicketService::open()`'s `$recordingId` parameter and the
  private `watch()`; `OpenEpisodeController` reading `?recording=`;
  `AccessOpen::record()` with `OpenTarget::Recording`; `T-125`'s
  `ProgressService::opened()` call already on the path, unmoved.
- `LiveSessionPanel.vue`: the "Add the recording link" form on a live row with
  no recording, and the list of recordings on a row with one or more.
- `LiveSessionCard.vue`: in `ready`, **Watch recording** / **Watch part :part**
  per recording, the passcode line, "Available until :date" when set, and the
  `ready` sentence.
- `SeriesController::show()` and `SharedController::show()` props for both;
  `SharedController::liveCard()` running inside `runFor()`.
- Lang lines in `live.php`, `series.php`, `errors.php`.
- `docs/flows/live-sessions.md` and `docs/tinker/live-sessions.md`.

**Out:**

- Hide and unhide, "Add another link" once a recording exists, "There's no
  recording for this session", the `overdue` and `not_recorded` copy and the
  `records = false` rule (`T-127`).
- The `recording_ready` email, the `session_notices` ledger and
  `queueRecordingReady()` on paste (`T-128`); the creator's send-status line
  (`T-129`).
- Recordings Qori finds: `FindsRecordings`, `ZoomRecordings`, `openUrl()` for
  `source = zoom`, `qori:recordings:find`, review, Check now (`T-142` to
  `T-144`). A `zoom` row's source line on the panel is `T-143`'s lang line.
- `available_until` being set by anything: the column exists and the card
  renders the line when it is not null; only a finder writes it.
- Any change to `T-089`'s file and Dropbox arms, the Vimeo embed, or
  `T-125`'s Join arm and its states.
- A recording on a File, Video or Audio Episode; `paste()` refuses one.
- Cancel and copy (`T-134`), the calendar file (`T-133`), materials (`T-130`).
- `DesignReviewSeeder`: no past session with a recording is seeded here.

## Files

| Path                                                                  | Change | Notes                                                                                                 |
| --------------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------- |
| `database/migrations/2026_09_18_000200_create_episode_recordings.php` | new    | The table per `D-027`, with the partial unique index                                                  |
| `app/Enums/RecordingSource.php`                                       | new    | `Zoom`, `Link`                                                                                        |
| `app/Models/EpisodeRecording.php`                                     | new    | `HasUlids`, `BelongsToGroup`; `isVisible()`, `scopeVisible()`, `episode()`                            |
| `app/Models/Episode.php`                                              | edit   | `series()`, `recordings()`, `visibleRecordings()`                                                     |
| `app/Services/RecordingService.php`                                   | new    | `paste()`; `T-128` adds the notice call, `T-127` and `T-144` their methods                            |
| `app/Services/LiveSessionService.php`                                 | edit   | The `Ready` arm in `stateFor()`, after `open` and before `not_recorded`                               |
| `app/Services/PlaybackTicketService.php`                              | edit   | `open()` gains `?string $recordingId`; private `watch()`                                              |
| `app/Http/Requests/Share/StoreRecordingRequest.php`                   | new    | `url` https ≤ 2048, `passcode` ≤ 100                                                                  |
| `app/Http/Controllers/Share/RecordingController.php`                  | new    | `store()`                                                                                             |
| `app/Http/Controllers/Share/SeriesController.php`                     | edit   | `recordings` per live Episode; `recording` inside `T-123`'s `live.copy`                               |
| `app/Http/Controllers/Shared/OpenEpisodeController.php`               | edit   | Reads `?recording=` and passes it to `open()`                                                         |
| `app/Http/Controllers/Shared/SharedController.php`                    | edit   | `liveCard()` runs inside `runFor()`; `live.recordings` with `href`, and `states.ready` in `live.copy` |
| `routes/share/episodes.php`                                           | edit   | `share.series.episodes.recordings.store`                                                              |
| `resources/js/components/series/LiveSessionPanel.vue`                 | edit   | The form, posting through Wayfinder, and the list; `LiveCopy` gains `recording`                       |
| `resources/js/components/series/LiveSessionCard.vue`                  | edit   | Watch links, passcode, available-until, the `ready` sentence                                          |
| `lang/en/live.php`                                                    | edit   | `state.ready.message`, `recording.*`, `panel.recording.*`                                             |
| `lang/en/series.php`                                                  | edit   | `recording_added`                                                                                     |
| `lang/en/errors.php`                                                  | edit   | `recording_unavailable` and `not_live` inside `T-125`'s `live` group                                  |
| `docs/flows/live-sessions.md`                                         | edit   | The paste chain and the Watch chain, beside `T-125`'s Join chain                                      |
| `docs/tinker/live-sessions.md`                                        | edit   | Paste a recording by hand, read the state, open it as a Peer                                          |
| `tests/Feature/Shared/RecordingTest.php`                              | new    | 22 cases                                                                                              |
| `tests/Feature/Series/LiveSessionStateTest.php`                       | edit   | `T-125`'s; the scene sets the current Group so the `ready` arm's read resolves (see Tests)            |

Neither `resources/js/pages/share/series/Show.vue` nor
`resources/js/pages/shared/Show.vue` is edited: the Peer's `recordings`, each
with its `href`, and `copy.states.ready` travel inside `T-125`'s `live` prop,
which the page already hands to the card, and the panel's five lines travel
inside `T-123`'s `live.copy`, which the page already passes as
`:copy="live.copy"` in both modes. That keeps the stream's claim order on the
two pages. `routes/shared.php` is not edited: Watch is a query on `T-089`'s
route. No factory and no seeder row, for the reason under Decisions.
`docs/flows/README.md` and `docs/tinker/README.md` already carry `T-125`'s
rows for the two files edited here.

## Database

| Table                | Column                     | Type                         | Null | Default | Index / constraint                                               |
| -------------------- | -------------------------- | ---------------------------- | ---- | ------- | ---------------------------------------------------------------- |
| `episode_recordings` | `id`                       | ulid                         | no   |         | primary                                                          |
| `episode_recordings` | `group_id`                 | ulid, FK `groups`, cascade   | no   |         | index `(group_id, episode_id, position)`                         |
| `episode_recordings` | `episode_id`               | ulid, FK `episodes`, cascade | no   |         | unique `(episode_id, vendor_ref)` where `vendor_ref is not null` |
| `episode_recordings` | `position`                 | integer                      | no   |         | Part 1, Part 2 …, per Episode                                    |
| `episode_recordings` | `source`                   | string                       | no   |         | `RecordingSource` value                                          |
| `episode_recordings` | `vendor_ref`               | string                       | yes  | null    | the vendor's instance id; null for a pasted link                 |
| `episode_recordings` | `url`                      | string(2048)                 | no   |         | `D-025`'s limit                                                  |
| `episode_recordings` | `passcode`                 | string(100)                  | yes  | null    |                                                                  |
| `episode_recordings` | `started_at`               | timestamp                    | no   |         | the Episode's `starts_at` for a pasted link                      |
| `episode_recordings` | `duration_minutes`         | integer                      | no   |         | the Episode's length for a pasted link                           |
| `episode_recordings` | `available_until`          | date                         | yes  | null    | written only by a finder                                         |
| `episode_recordings` | `found_at`                 | timestamp                    | no   |         | the paste time for a pasted link                                 |
| `episode_recordings` | `published_at`             | timestamp                    | yes  | null    | now on paste; null while held for review (`T-143`)               |
| `episode_recordings` | `hidden_at`                | timestamp                    | yes  | null    | set by `T-127`                                                   |
| `episode_recordings` | `needs_review`             | boolean                      | no   | false   | set by `T-143`                                                   |
| `episode_recordings` | `created_at`, `updated_at` | timestamps                   | yes  |         |                                                                  |

Migration: `database/migrations/2026_09_18_000200_create_episode_recordings.php`

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/**
 * A live Episode's recordings, one row each (D-027).
 *
 * Rows rather than a list inside episodes.content: the sweep must never find
 * the same instance twice, which is a unique constraint; T-128's ledger points
 * at a recording, which is a foreign key; and a Part 2 arrives on its own.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('episode_recordings', function (Blueprint $table): void {
            $table->ulid('id')->primary();
            $table->foreignUlid('group_id')->constrained()->cascadeOnDelete();
            $table->foreignUlid('episode_id')->constrained()->cascadeOnDelete();
            $table->integer('position');
            $table->string('source');
            $table->string('vendor_ref')->nullable();
            $table->string('url', 2048);
            $table->string('passcode', 100)->nullable();
            $table->timestamp('started_at');
            $table->integer('duration_minutes');
            $table->date('available_until')->nullable();
            $table->timestamp('found_at');
            $table->timestamp('published_at')->nullable();
            $table->timestamp('hidden_at')->nullable();
            $table->boolean('needs_review')->default(false);
            $table->timestamps();

            $table->index(['group_id', 'episode_id', 'position']);
        });

        // Partial, as D-027 words it: Blueprint::unique() cannot express WHERE,
        // and every pasted row shares a null vendor_ref.
        DB::statement(
            'CREATE UNIQUE INDEX episode_recordings_episode_id_vendor_ref_unique '
            .'ON episode_recordings (episode_id, vendor_ref) WHERE vendor_ref IS NOT NULL',
        );
    }

    public function down(): void
    {
        Schema::dropIfExists('episode_recordings');
    }
};
```

## Code

```php
namespace App\Enums;

/** Where a recording came from (D-027). */
enum RecordingSource: string
{
    /** Found in the creator's Zoom cloud by qori:recordings:find (T-143). */
    case Zoom = 'zoom';

    /** Pasted by the creator, and published on paste. */
    case Link = 'link';
}
```

```php
namespace App\Models;

use App\Concerns\BelongsToGroup;
use App\Enums\RecordingSource;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Carbon;

/**
 * One recording of one live Episode (D-027).
 *
 * @property string $group_id
 * @property string $episode_id
 * @property int $position
 * @property RecordingSource $source
 * @property ?string $vendor_ref
 * @property string $url
 * @property ?string $passcode
 * @property Carbon $started_at
 * @property int $duration_minutes
 * @property ?Carbon $available_until
 * @property Carbon $found_at
 * @property ?Carbon $published_at
 * @property ?Carbon $hidden_at
 * @property bool $needs_review
 */
class EpisodeRecording extends Model
{
    use BelongsToGroup, HasUlids;

    protected $table = 'episode_recordings';

    /** @var list<string> */
    protected $fillable = [
        'group_id', 'episode_id', 'position', 'source', 'vendor_ref', 'url', 'passcode',
        'started_at', 'duration_minutes', 'available_until', 'found_at',
        'published_at', 'hidden_at', 'needs_review',
    ];

    /** @return array<string, string> */
    protected function casts(): array
    {
        return [
            'position' => 'integer',
            'source' => RecordingSource::class,
            'started_at' => 'datetime',
            'duration_minutes' => 'integer',
            'available_until' => 'date',
            'found_at' => 'datetime',
            'published_at' => 'datetime',
            'hidden_at' => 'datetime',
            'needs_review' => 'boolean',
        ];
    }

    /** @return BelongsTo<Episode, $this> */
    public function episode(): BelongsTo;   // belongsTo(Episode::class)

    /** Published and not hidden: the only rows a Peer ever sees (D-027). */
    public function isVisible(): bool;   // $this->published_at !== null && $this->hidden_at === null

    /**
     * @param  Builder<static>  $query
     * @return Builder<static>
     */
    public function scopeVisible(Builder $query): Builder;   // whereNotNull('published_at')->whereNull('hidden_at')
}
```

```php
// App\Models\Episode — two relations and one read, beside T-123's ends_at, isCancelled() and lengthMinutes()

/** @return BelongsTo<Series, $this> */
public function series(): BelongsTo;   // belongsTo(Series::class)

/**
 * Every recording, Part 1 first.
 *
 * EpisodeRecording carries BelongsToGroup, so this is scoped — and so is
 * series(), because Series carries the trait too. On the Peer surface both
 * are read inside CurrentGroup::runFor($series->group, …), set by the caller
 * that holds the Series: SharedController::liveCard() and
 * PlaybackTicketService::watch().
 *
 * @return HasMany<EpisodeRecording, $this>
 */
public function recordings(): HasMany;   // hasMany(EpisodeRecording::class)->orderBy('position')

/**
 * The rows a Peer may watch.
 *
 * @return Collection<int, EpisodeRecording>
 */
public function visibleRecordings(): Collection;
// $this->recordings->filter(fn (EpisodeRecording $recording): bool => $recording->isVisible())->values()
```

```php
namespace App\Services;

use App\Concerns\LocksOverCapSeries;
use App\Enums\RecordingSource;
use App\Exceptions\AppException;
use App\Models\Episode;
use App\Models\EpisodeRecording;
use App\Models\User;
use Carbon\CarbonImmutable;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

/**
 * A live Episode's recordings (D-027). This task: the paste. T-127 adds
 * hide(), unhide(); T-144 adds publish(), reject().
 */
class RecordingService
{
    use LocksOverCapSeries;

    /**
     * A link the creator pastes is published the moment it lands: the
     * creator's act is the review. $by reaches the log line only — D-027
     * has no column for who pasted.
     */
    public function paste(Episode $episode, string $url, ?string $passcode, User $by): EpisodeRecording;
    // // Series, not ?Series: the creator's request carries a Group, so the scoped read resolves or fails loudly.
    // $series = $episode->series()->firstOrFail();
    // $this->guardSeriesUnlocked($series->group, 'add a recording');
    // $this->guardLive($episode);
    //
    // return DB::transaction(function () use ($episode, $series, $url, $passcode, $by): EpisodeRecording {
    //     // The row T-143's sweep locks too, so a paste and a sweep never interleave.
    //     $locked = Episode::query()->whereKey($episode->getKey())->lockForUpdate()->firstOrFail();
    //     $now = CarbonImmutable::now();
    //
    //     $recording = $locked->recordings()->create([
    //         'group_id' => $series->group_id,
    //         'position' => (int) $locked->recordings()->max('position') + 1,
    //         'source' => RecordingSource::Link,
    //         'vendor_ref' => null,
    //         'url' => trim($url),
    //         'passcode' => filled($passcode) ? trim((string) $passcode) : null,
    //         'started_at' => $locked->starts_at,
    //         // ends_at is nullable in the schema, so the default stands in for a row without one.
    //         'duration_minutes' => $locked->lengthMinutes() ?? (int) config('qori.live.default_length_minutes'),
    //         'available_until' => null,
    //         'found_at' => $now,
    //         'published_at' => $now,
    //         'hidden_at' => null,
    //         'needs_review' => false,
    //     ]);
    //
    //     Log::info("Recording {$recording->getKey()} pasted on episode {$locked->getKey()} by user {$by->getKey()}.");
    //
    //     return $recording;
    // });

    /** Only a live Episode has a session to record. */
    private function guardLive(Episode $episode): void;
    // if (! $episode->isLive()) {
    //     throw AppException::invalidRequest(
    //         'errors.live.not_live',
    //         devMessage: "Episode {$episode->getKey()} is {$episode->type->value}, not live; it cannot take a recording.",
    //     );
    // }
}
```

```php
// App\Services\LiveSessionService::stateFor() — one arm added to T-125's match,
// after its `open` arm and before its `not_recorded` arm, so the order reads
// cancelled, upcoming, open, ready, not_recorded, waiting, overdue (T-127 keeps
// it; T-143 puts `review` between ready and not_recorded). Join keeps winning
// until its window closes; from then on a recording outranks content['records'],
// because a recording is a fact and the switch was a plan. The arm reads
// episode_recordings through the scope: the creator's request has a Group, and
// the Peer callers set one with runFor() (see Decisions).
return match (true) {
    isset($content['cancelled_at']) => LiveState::Cancelled,                    // T-125
    $now < $window->opensAt => LiveState::Upcoming,                             // T-125
    $now < $window->closesAt => LiveState::Open,                                // T-125
    $episode->visibleRecordings()->isNotEmpty() => LiveState::Ready,            // this task
    ($content['records'] ?? true) === false, isset($content['not_recorded_at']) => LiveState::NotRecorded,   // T-125
    $now < $episode->ends_at->toImmutable()->addHours((int) config('qori.live.recording_wait_hours')) => LiveState::Waiting,   // T-125
    default => LiveState::Overdue,                                              // T-125
};
```

```php
// App\Services\PlaybackTicketService — T-089's open() gains one parameter.
// issue() and admit() are unchanged.

use App\Enums\OpenTarget;
use App\Models\AccessOpen;
use App\Models\EpisodeRecording;

/**
 * With $recordingId, Watch: the published, unhidden recording of this
 * Episode, or errors.live.recording_unavailable. Without it, T-089's file and
 * vendor arms and T-125's Join arm, unchanged. T-125's opened() call stays
 * where it is, before the branch, so a Watch that fails marks the Episode
 * opened exactly as a blocked Join does.
 */
public function open(User $peer, string $seriesId, string $episodeId, ?string $recordingId = null): MediaLink|VendorLink;
// [$access, $series, $episode] = $this->admit($peer, $seriesId, $episodeId);
// $this->progress->opened($access, $episodeId);                        // T-125's line, unmoved
//
// if ($recordingId !== null) {
//     return $this->watch($access, $series, $episode, $recordingId);   // ahead of the live arm
// }
//
// … T-089's and T-125's lines, as they are

/**
 * Read in the creator's Group, as connectionFor() reads a Connection: the
 * Peer is inside no Group, EpisodeRecording is group-scoped, and forGroup()
 * cannot serve stateFor() (see Decisions), so every Peer read of a recording
 * uses the one mechanism. open() has already marked the Episode opened; only
 * the access_opens row waits for the visibility check.
 */
private function watch(Access $access, Series $series, Episode $episode, string $recordingId): VendorLink;
// $recording = $this->current->runFor(
//     $series->group,
//     fn (): ?EpisodeRecording => $episode->recordings()->whereKey($recordingId)->first(),
// );
//
// if (! $recording instanceof EpisodeRecording || ! $recording->isVisible()) {
//     throw AppException::notFound(
//         'errors.live.recording_unavailable',
//         devMessage: "Recording {$recordingId} is not a visible recording of episode {$episode->getKey()}.",
//     );
// }
//
// AccessOpen::record($access, OpenTarget::Recording, (string) $episode->getKey(), (string) $recording->getKey());
//
// // A link row opens exactly as stored (D-027). T-142 routes a zoom row through FindsRecordings::openUrl() here.
// return new VendorLink($recording->url, $episode->provider);
```

```php
// App\Http\Controllers\Shared\OpenEpisodeController::__invoke() — T-089's body, with the query read:
$recording = $request->query('recording');

$link = $tickets->open(
    CurrentUser::orFail($request),
    $seriesId,
    $episodeId,
    is_string($recording) && $recording !== '' ? $recording : null,
);
// … the blocked-link branch and redirect()->away($link->url), unchanged
```

```php
namespace App\Http\Requests\Share;

use Illuminate\Foundation\Http\FormRequest;

/** The recording link a creator pastes onto a live Episode (D-025, D-027). */
class StoreRecordingRequest extends FormRequest
{
    /** Authorised by the group middleware — reaching here means membership. */
    public function authorize(): bool;   // true

    /** @return array<string, array<int, string>> */
    public function rules(): array
    {
        return [
            // https only, at most 2048 characters (D-025). Laravel's url rule names the schemes it accepts.
            'url' => ['required', 'string', 'url:https', 'max:2048'],
            'passcode' => ['nullable', 'string', 'max:100'],
        ];
    }

    /** Named so it does not shadow Request::url(). */
    public function recordingUrl(): string;   // trim($this->string('url')->toString())

    public function passcode(): ?string;   // $this->filled('passcode') ? trim($this->string('passcode')->toString()) : null
}
```

```php
namespace App\Http\Controllers\Share;

use App\Concerns\ResolvesShareSeries;
use App\Exceptions\AppException;
use App\Http\Controllers\Controller;
use App\Http\Requests\Share\StoreRecordingRequest;
use App\Services\RecordingService;
use App\Support\CurrentUser;
use App\Support\Terminology;
use Illuminate\Http\RedirectResponse;
use Inertia\Inertia;

/** The recordings on one live Episode. Every parameter is an id; the Series carries the tenancy check. */
class RecordingController extends Controller
{
    use ResolvesShareSeries;

    public function store(
        string $group,
        string $seriesId,
        string $episodeId,
        StoreRecordingRequest $request,
        RecordingService $recordings,
        Terminology $terminology,
    ): RedirectResponse;
    // $series = $this->seriesById($seriesId);
    // $episode = $series->episodes()->whereKey($episodeId)->first()
    //     ?? throw AppException::notFound('errors.series.episode_not_found', devMessage: "Episode {$episodeId} is not part of series {$seriesId}.");
    //
    // $recordings->paste($episode, $request->recordingUrl(), $request->passcode(), CurrentUser::orFail($request));
    //
    // Inertia::flash('toast', [
    //     'type' => 'success',
    //     'message' => $terminology->line('series.recording_added', ['title' => $episode->title]),
    // ]);
    //
    // return back();
}
```

```php
// App\Http\Controllers\Share\SeriesController::show() — per Episode (:158-166), beside T-123's live fields.
// The creator's page carries the url: it is theirs. $scope is the current Group (:148).
'recordings' => $episode->isLive()
    ? $episode->recordings->map(fn (EpisodeRecording $recording): array => [
        'id' => (string) $recording->getKey(),
        'part' => $recording->position,
        'partLabel' => __('live.panel.recording.part', ['part' => $recording->position]),
        // Keyed by source, so T-143 adds live.panel.recording.source.zoom and nothing here changes.
        'sourceLine' => __('live.panel.recording.source.'.$recording->source->value, [
            'date' => $recording->found_at->setTimezone($scope?->timezone() ?? Timezones::fallback())->format('j M Y'),
        ]),
        'url' => $recording->url,
        'passcode' => $recording->passcode,
        'isVisible' => $recording->isVisible(),
    ])->values()->all()
    : [],

// Inside the copy object T-123 hands LiveSessionPanel.vue (`live.copy`), beside T-124's `edit` —
// the page already passes it as :copy="live.copy" in both modes, so no page edit and no second prop:
'recording' => [
    'title' => __('live.panel.recording.title'),
    'urlLabel' => __('live.panel.recording.url_label'),
    'urlHelp' => $terminology->line('live.panel.recording.url_help', [], $scope),
    'passcodeLabel' => __('live.panel.recording.passcode_label'),
    'submit' => __('live.panel.recording.submit'),
],
```

```php
// App\Http\Controllers\Shared\SharedController::liveCard() — T-125's body, wrapped. This task's
// edit to the method is the runFor(): T-125 does not set one, and without it stateFor()'s new
// arm and this list both throw from GroupScope (see Decisions). $group is T-125's $series->group.
private function liveCard(Episode $episode, Series $series, LiveSessionService $live, Terminology $terminology): array;
// $seriesId = (string) $series->getKey();
// $episodeId = (string) $episode->getKey();
//
// return app(CurrentGroup::class)->runFor($series->group, function () use (…): array {
//     $parts = $episode->visibleRecordings()->count();
//
//     return [
//         // …T-125's keys, as they are…
//
//         // The url never enters the prop. href is the Qori route, built here because the card
//         // holds neither id; Laravel appends the unmatched `recording` parameter as the query string.
//         'recordings' => $episode->visibleRecordings()->map(fn (EpisodeRecording $recording): array => [
//             'id' => (string) $recording->getKey(),
//             'part' => $recording->position,
//             'href' => route('shared.episodes.open', [$seriesId, $episodeId, 'recording' => (string) $recording->getKey()]),
//             'label' => $parts === 1
//                 ? __('live.recording.watch')
//                 : __('live.recording.watch_part', ['part' => $recording->position]),
//             'passcodeLine' => $recording->passcode === null
//                 ? null
//                 : __('live.recording.passcode', ['passcode' => $recording->passcode]),
//             'availableLine' => $recording->available_until === null
//                 ? null
//                 : __('live.recording.available_until', ['date' => $recording->available_until->format('j M Y')]),
//         ])->values()->all(),
//
//         'copy' => [
//             'states' => [
//                 // …T-125's five, as they are…
//                 'ready' => ['message' => $terminology->line('live.state.ready.message', [], $group)],
//             ],
//             // …T-125's join, joinAgain, noLink, records…
//         ],
//     ];
// });
```

```ts
// resources/js/components/series/LiveSessionCard.vue — props added to T-125's
interface PeerRecording {
    id: string;
    part: number;
    /** shared.episodes.open with ?recording=, built by the server; never the vendor's link. */
    href: string;
    label: string;
    passcodeLine: string | null;
    availableLine: string | null;
}
// `live.recordings: PeerRecording[]`, and `live.copy.states` gains `ready: { message: string }`.
// No route import and no new prop: the card holds neither id (T-125 gives it `live` and
// `joinHref`), so the href arrives ready-made, as joinHref does.
//
// In state 'ready', T-125's `line` renders copy.states.ready.message; then one block per recording in order:
//   <a :href="recording.href" target="_blank" rel="noopener">{{ recording.label }}</a>
//   <span v-if="recording.passcodeLine">{{ recording.passcodeLine }}</span>
//   <span v-if="recording.availableLine">{{ recording.availableLine }}</span>
// Mark as done is the page's existing form and is not touched.
```

```ts
// resources/js/components/series/LiveSessionPanel.vue — additions to T-123's
import { store as storeRecording } from '@/routes/share/series/episodes/recordings'; // generated by `php artisan wayfinder:generate --with-form`

interface CreatorRecording {
    id: string;
    part: number;
    partLabel: string;
    sourceLine: string;
    url: string;
    passcode: string | null;
    isVisible: boolean;
}
// T-123's exported `LiveCopy` gains
//   recording: { title: string; urlLabel: string; urlHelp: string; passcodeLabel: string; submit: string };
// filled by SeriesController::show() above and reaching the panel through the page's existing
// :copy="live.copy" in both modes — the panel's own pattern, no usePage() read for copy. The
// Episode row prop gains `recordings: CreatorRecording[]`.
//
// The list, when recordings.length > 0: one line per recording —
//   partLabel · sourceLine · <a :href="recording.url" target="_blank" rel="noopener">{{ recording.url }}</a> · passcode
// No control on the line; T-127 puts Hide there.
//
// The form, when recordings.length === 0, posting through Wayfinder with the three values T-124's
// `action` already computes in this component — `groupSlug` (usePage().url.split('/')[2]),
// `page.props.series.id` and the row's `episode.id`:
const recordingAction = computed(() =>
    storeRecording.form({
        group: groupSlug.value,
        seriesId: page.props.series.id,
        episodeId: props.episode?.id ?? '',
    }),
);
//   <Form v-bind="recordingAction" v-slot="{ errors, processing }">
//     <input id="recording-url" name="url" type="url" required />         label copy.recording.urlLabel, help copy.recording.urlHelp
//     <input id="recording-passcode" name="passcode" type="text" />       label copy.recording.passcodeLabel
//     <button type="submit" :disabled="processing || lock.active">{{ copy.recording.submit }}</button>
//   </Form>
// disabled under the over-cap lock as the Remove form is (resources/js/pages/share/series/Show.vue:474-497).
```

`routes/share/episodes.php`, after `series.episodes.reorder` (`:25-26`):

```php
use App\Http\Controllers\Share\RecordingController;

Route::post('series/{seriesId}/episodes/{episodeId}/recordings', [RecordingController::class, 'store'])
    ->name('series.episodes.recordings.store');
```

`docs/flows/live-sessions.md`: beside `T-125`'s Join chain, the paste chain
(`POST …/recordings` → `RecordingController::store()` → `RecordingService::paste()`
→ the row, published) and the Watch chain
(`GET …/open?recording=` → `OpenEpisodeController` → `PlaybackTicketService::open()`
→ `admit()` → `ProgressService::opened()` → `watch()` → `AccessOpen::record()`
→ 302 to the stored link), with the `episode_recordings` columns and the
arm order — `cancelled`, `upcoming`, `open`, `ready`, `not_recorded`,
`waiting`, `overdue` — so a visible row answers `ready` once Join has
closed. `docs/tinker/live-sessions.md`: paste a recording with
`app(App\Services\RecordingService::class)->paste($episode, 'https://…', '1234', $user)`
under a Group context, read `stateFor()` back, then
`app(App\Services\PlaybackTicketService::class)->open($peer, $seriesId, $episodeId, $recordingId)->url`
with no context set.

## Copy

| Key                                            | File                 | English                                                                                                                                                                                                     |
| ---------------------------------------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `live.state.ready`                             | `lang/en/live.php`   | The recording is here. It's a link the :creator manages, so if it stops working, let them know.                                                                                                             |
| `live.recording.watch`                         | `lang/en/live.php`   | Watch recording                                                                                                                                                                                             |
| `live.recording.watch_part`                    | `lang/en/live.php`   | Watch part :part                                                                                                                                                                                            |
| `live.recording.passcode`                      | `lang/en/live.php`   | Passcode: :passcode                                                                                                                                                                                         |
| `live.recording.available_until`               | `lang/en/live.php`   | Available until :date                                                                                                                                                                                       |
| `live.panel.recording.title`                   | `lang/en/live.php`   | Add the recording link                                                                                                                                                                                      |
| `live.panel.recording.url_label`               | `lang/en/live.php`   | Recording link                                                                                                                                                                                              |
| `live.panel.recording.url_help`                | `lang/en/live.php`   | Paste the link to the recording from your meeting app, or from wherever you keep it, and set its sharing so anyone with the link can watch. :peer_plural with access see it on this :episode straight away. |
| `live.panel.recording.passcode_label`          | `lang/en/live.php`   | Passcode, if the link has one                                                                                                                                                                               |
| `live.panel.recording.submit`                  | `lang/en/live.php`   | Add recording                                                                                                                                                                                               |
| `live.panel.recording.part`                    | `lang/en/live.php`   | Part :part                                                                                                                                                                                                  |
| `live.panel.recording.source.link`             | `lang/en/live.php`   | Added by you on :date                                                                                                                                                                                       |
| `series.recording_added`                       | `lang/en/series.php` | Recording added to :title. :peer_plural with access can watch it from the :episode now.                                                                                                                     |
| `errors.live.recording_unavailable.message`    | `lang/en/errors.php` | That recording isn't available.                                                                                                                                                                             |
| `errors.live.recording_unavailable.resolution` | `lang/en/errors.php` | Go back to the :episode. Anything you can watch is listed there.                                                                                                                                            |
| `errors.live.not_live.message`                 | `lang/en/errors.php` | Only a live :episode can have a recording.                                                                                                                                                                  |

`live.state.ready`, `live.panel.recording.url_help`, `series.recording_added`
and the two `errors.live` lines carry a noun and go through
`Terminology::line()` with the Group passed explicitly on the Peer surface;
the rest carry none and are read with `__()`. `:date` in `source.link` is the
Group's zone (the creator's page); `available_until` is a date with no zone.
No line names a vendor: the creator's help says "your meeting app", and the
Peer's says a link the :creator manages (`D-025`). No line under `live.*`
says "live now", "has ended", "on its way" or "processing" (`D-026`).
`errors.live.not_live` has no resolution: nothing in the product offers the
action, so the path is final. The `live` group in `errors.php` is added by
whichever of `T-125` and this task lands first.

## Routes

| Verb | Path                                                                   | Name                                     | Action                                                   |
| ---- | ---------------------------------------------------------------------- | ---------------------------------------- | -------------------------------------------------------- |
| POST | `/g/{group}/series/{seriesId}/episodes/{episodeId}/recordings`         | `share.series.episodes.recordings.store` | `Share\RecordingController::store`                       |
| GET  | `/shared/{seriesId}/episodes/{episodeId}/open?recording={recordingId}` | `shared.episodes.open` (exists, `T-089`) | `Shared\OpenEpisodeController::__invoke` reads the query |

The first sits in `routes/share/episodes.php` inside `routes/share.php`'s
`auth, verified, group` group with prefix `g/{group}` and name prefix `share.`
(`routes/share.php:24-31`); every parameter is an id. The second is not a
route change: `T-089`'s route gains a query parameter, and `routes/shared.php`
is untouched.

## Tests

**New: `tests/Feature/Shared/RecordingTest.php` — 22 cases**
(`RefreshDatabase`; `Http::preventStrayRequests()` in `setUp`; a `scene()`
helper on `LiveSessionTest.php:41-60`'s shape — Group on `start` with
`timezone` `Australia/Brisbane` and an owner Collaborator — a `liveSeries()`
helper that publishes a Series with one live Zoom Episode starting
`2026-10-03 10:00 UTC` for 90 minutes through `EpisodeService::add()`, a
`peerWith()` helper around `AccessService::grant()`, `Carbon::setTestNow()`
at `2026-10-03 14:00 UTC` unless a case says otherwise, and `paste()` called
with `app(CurrentGroup::class)->set($group)` as `OverCapLockTest.php:60-61`
does; `watchUrl($series, $episode, $recordingId)` builds
`route('shared.episodes.open', [$seriesId, $episodeId]).'?recording='.$recordingId`)

1. `test_it_publishes_a_pasted_link_at_once` — the row has `source` `link`,
   `published_at` set, `hidden_at` null, `needs_review` false, `vendor_ref`
   null, `position` 1, the url and passcode as given, `started_at` equal to
   the Episode's `starts_at`, `duration_minutes` 90, `found_at` now, and
   `group_id` the Series' Group.
2. `test_it_numbers_a_second_paste_as_the_next_part` — position 2; the first
   row is unchanged.
3. `test_it_refuses_a_recording_on_an_episode_that_is_not_live` — a File
   Episode: `AppException` carrying `errors.live.not_live`; no row.
4. `test_it_refuses_a_paste_while_the_group_is_over_its_cap` — the
   `overCapGroup()` recipe (`OverCapLockTest.php:59-71`) with a live Episode
   on the surviving Series: `errors.series.locked_over_cap`; no row.
5. `test_the_store_route_publishes_the_link_and_says_so` — the owner posts
   `url` and `passcode`: redirect back, one row, and
   `assertSessionHas(SessionKey::FLASH_DATA, …)` sees a `success` toast
   containing `series.recording_added` resolved with the title, the way
   `SeriesAccessCodeTest.php:157` reads one.
6. `test_the_store_route_refuses_a_link_that_is_not_https` — `http://…` and
   `not-a-link`: `assertSessionHasErrors('url')`; no row.
7. `test_a_slug_on_the_store_route_does_not_resolve` — the Series slug in
   place of the id, as `ShareSeriesRoutesTest.php:143-151`: no row.
8. `test_another_groups_episode_cannot_take_a_recording` — Group A's owner
   posts under A's prefix to Group B's Series and Episode ids: 404, no row.
9. `test_the_creators_page_lists_the_recording_on_its_episode` —
   `assertInertia`: `series.episodes.0.recordings.0` has `part` 1, the `url`,
   the `passcode`, `isVisible` true and a `sourceLine` containing
   `3 Oct 2026`; `recordingCopy.title` is `live.panel.recording.title`.
10. `test_the_peers_page_offers_watch_once_a_recording_is_published` —
    `series.episodes.0.live.state` is `ready`, `live.recordings.0.label` is
    `Watch recording`, `passcodeLine` is `Passcode: 1234`, `availableLine`
    null, and `series.episodes.0.live.recordings.0.url` is missing.
11. `test_two_recordings_are_offered_as_parts` — labels `Watch part 1` and
    `Watch part 2`, in that order.
12. `test_the_peers_page_offers_no_watch_before_a_recording_exists` — after
    the scheduled end with nothing pasted: state `waiting`, `recordings`
    empty (owner acceptance 5).
13. `test_a_hidden_recording_is_not_offered` — `hidden_at` set on the row:
    `recordings` empty and the state is not `ready`.
14. `test_ready_wins_over_the_clock` — `stateFor()` answers `Ready` for an
    Episode with a visible recording at three instants: an hour before the
    start, inside the Join window, and `recording_wait_hours` plus one after
    the end.
15. `test_watch_redirects_to_the_recordings_link` — 302 whose `Location` is
    exactly the pasted url; no JSON.
16. `test_watch_records_the_open_and_marks_the_episode_opened` — one
    `access_opens` row with `target` `recording`, the Episode id,
    `subject_id` the recording id and `group_id` the Access's;
    `$access->fresh()->hasOpened($episodeId)`; `last_activity_at` set.
17. `test_watch_on_a_hidden_recording_is_not_found` — 404 page showing
    `errors.live.recording_unavailable.message`; no `access_opens` row.
18. `test_watch_on_a_recording_held_for_review_is_not_found` — a row created
    with `published_at` null and `needs_review` true: 404.
19. `test_watch_on_another_groups_series_is_forbidden` — the Peer has access
    to A and follows Watch on B's Series and Episode: 403 with
    `errors.access.not_granted.message` (wrong tenant, owner acceptance 11).
20. `test_a_recording_id_from_another_episode_is_not_found` — the path names
    A's Series and Episode and the query names a recording on B's Episode:
    404; no `access_opens` row.
21. `test_a_revoked_access_cannot_watch` — `AccessService::revoke()`, then
    403; no row.
22. `test_the_recording_never_reaches_the_public_page` — `series.public` for
    the published Series: `assertDontSee` the url and the passcode, and the
    Inertia prop `series.episodes.0` has no `recordings` key (owner
    acceptance 11, `D-024`'s preview rule).

**Changed:** none. `open()`'s new parameter defaults to null, so `T-089`'s
`OpenEpisodeTest` and `T-125`'s `LiveSessionCardTest` run as written, and the
latter's boundary cases never produce `ready`.

Total: 22 new cases.

## Acceptance

- [ ] A creator pastes a recording link and its passcode on a live Episode's
      row and the page lists it as Part 1 with the date it was added; a second
      paste through the service is Part 2
- [ ] A Peer with access sees Watch recording and the passcode on the same
      card that offered Join, and Watch opens the pasted link in a new tab
      through `shared.episodes.open?recording=` (owner acceptance 4's page
      half; the email is `T-128`'s)
- [ ] After the scheduled end with nothing pasted, the card shows `T-125`'s
      `waiting` line and no Watch, and nothing is emailed (owner acceptance 5)
- [ ] Watch marks the Episode opened and writes one `access_opens` row with
      `target = recording`; Mark as done, the Episode count and the certificate
      are untouched (owner acceptance 12)
- [ ] A revoked Access, another Group's Series, a recording id from another
      Episode, a hidden recording and one held for review each meet the
      response the tests name — never a blank tab (owner acceptance 11)
- [ ] The public page carries no recording link and no passcode
- [ ] `docs/flows/live-sessions.md` describes the paste and the Watch chain,
      and `docs/tinker/live-sessions.md` pastes one by hand
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~`T-089` `ready`, with its three open questions answered, so
  `shared.episodes.open`, `OpenEpisodeController`, `PlaybackTicketService::open()`
  and `admit()`, `VendorLink` and `lang/en/shared.php` are frozen names —
  the owner's (the same bullet `T-125` carries).~~ **Answered 26 September
  2026:** `T-089` is `done`, and `T-125` read each name back from the code
  on 21 September and built on them.
- ~~Whether Watch is `?recording={id}` on `T-089`'s route, as this draft
  assumes, or a sibling `GET /shared/{seriesId}/episodes/{episodeId}/recordings/{recordingId}/open`
  named `shared.recordings.open` — anyone's, decided with `T-089`'s owner.
  The difference is one route line, `OpenEpisodeController`'s query read
  becoming a path parameter, and the card's `href`; nothing in the service
  changes.~~ **Decided 26 September 2026:** `?recording={id}`, as drafted.
  Join and Watch pass one gate and `T-125`'s controller already turns every
  answer of `open()` into a redirect, so a second route would repeat it.
- ~~`T-125` `ready`, so the `live` prop's key names, `live.copy`, `LiveState`,
  the arm order in `stateFor()` and `AccessOpen::record()` are frozen, and
  this draft's additions to them are literal — anyone's.~~ **Answered 26
  September 2026:** `T-125` is `done` (qori `94dd6c9`); the names are as this
  draft cites them, plus `LiveSessionService::isScheduled()`, which
  `liveCard()` is only called behind.

## Re-scope log

None.

## Notes

`T-125`'s draft is edited to declare `LiveState::Ready` and never answer it:
its `stateFor()` has no recording to see, its state cases stop at
`cancelled`, and this task adds the arm and the `live.state.ready` line.

`T-128`'s draft is edited to add `SessionNoticeService::queueRecordingReady()`
inside `RecordingService::paste()`, after the row is written and inside the
same transaction, and to soften `live.panel.recording.url_help` and
`series.recording_added` with the email once one goes; nothing here sends.

`T-127` adds Hide on the panel's list line, "Add another link" once a
recording exists, `hide()` and `unhide()` on `RecordingService`, and the
`overdue` and `not_recorded` arms. `T-143` adds `live.panel.recording.source.zoom`
and the first `zoom` rows; `T-142`'s `FindsRecordings::openUrl()` replaces the
stored url inside `watch()` for `source = zoom` only. A `link` row opens
exactly as stored, today and after.

Postgres treats nulls as distinct in a unique index, so the `WHERE vendor_ref
IS NOT NULL` clause is `D-027`'s wording made literal rather than a necessity;
it is kept so the index says what it is for.

The design stream may want `DesignReviewSeeder` to seed a past live session
with a pasted recording, so the `ready` card can be reviewed; that is a
seeder row and a design-review lane, not this task.
