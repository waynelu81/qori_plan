---
id: T-143
title: `qori:recordings:find` looks for recordings with backoff and lands them for review
stream: classroom
status: draft
owner: unassigned
estimate: M
depends: T-129, T-142
blocks: T-144
---

# T-143 — `qori:recordings:find` looks for recordings with backoff and lands them for review

> **Draft.** Not to be started — see [`../PROCESS.md`](../PROCESS.md). What
> has to be settled before it can be marked `ready` is listed at the bottom.
> Written on 18 September 2026 from `D-027` and `D-026`, on `T-142`'s
> `FindsRecordings` contract and `T-129`'s nudge rule, for the sprint after
> the manual-replay checkpoint (`D-031`).

## Why

Nothing looks for a recording. After the checkpoint a recording reaches an
Episode one way: the creator pastes its link (`RecordingService::paste()`,
`T-126`), and the Peer's `waiting` card promises that "if it was recorded,
the recording will be added here" (`T-125`'s `live.state.waiting.message`)
on the strength of the creator remembering to. `T-141` stores a Zoom token
and the account's recording settings in `connections.settings`; `T-142`
reads a meeting's cloud recordings through
`App\Integrations\Contracts\FindsRecordings` and hands back
`App\Data\SessionRecording` shapes; and nothing calls it. Two things already
built have no writer: `episode_recordings.needs_review` (`T-126`'s column,
`D-027`) and `LiveState::Review` (`T-125`'s case, "returned from T-143").
`routes/console.php:28` schedules one command today, and `T-128` adds a
second; neither reads a vendor.

`D-027` says what happens instead: detection is a scheduled REST poll,
`qori:recordings:find`, with backoff for `recording_wait_hours` after the
scheduled end; a recording Qori finds lands with `published_at` null unless
the Series' `recording_publication` says `automatic`, and is held with
`needs_review` whatever that setting says when the match is ambiguous — two
or more instances in the window, a start more than
`match_tolerance_minutes` from `starts_at`, a duration under
`min_recording_minutes`, or a personal or vanity link. `D-028` moves the
creator's nudge to `recording_wait_hours` for a session Qori is looking for.
The owner's acceptance scenarios 6, 7 and 8 are this task's: review-first
never notifies until the creator publishes; automatic publication works
only when explicitly selected; a reused meeting, an early test recording, a
restarted meeting or several segments cannot silently attach the wrong
replay; and a duplicate or delayed find never duplicates an email.

Afterwards `qori:recordings:find` runs every five minutes (provisional),
walks every Group inside `CurrentGroup::runFor()`, and for each live Episode
that is `waiting`, on a provider with a finder, with a join link the finder
handles, in a Group whose connected account is usable and keeps cloud
recordings, and whose `recording_checked_at` is older than the backoff step
for its age, calls the finder once. What comes back is written under the
Episode's row lock by `LiveSessionService::attachFound()`: one
`episode_recordings` row per new `vendor_ref`, held for review by default,
published at once — and `recording_ready` queued through `T-128`'s ledger —
only on a Series switched to `automatic` and only when the match is clear.
The creator's panel reads `review` with the held rows, when Qori last
checked and when it checks next; the Peer's card still reads `waiting`
(`D-026`). The creator chooses per Series on the details form, review-first
on every Series until they do.

## Decisions taken to make this specifiable

**Candidates are narrowed by query on the columns and decided by
`stateFor()`, and the floor is Join closing.** `D-026`: state is computed,
never stored. The query takes live Episodes of this Group on a provider that
has a finder, with `ends_at` between `now − recording_wait_hours` and
`now − join_closes_after_minutes`; `stateFor($episode, $now)` must answer
`Waiting`, which excludes `cancelled`, `not_recorded`, a "Live only" session,
`ready` and `overdue` in one place instead of five JSON clauses. The brief's
"ended between 10 minutes and `recording_wait_hours` ago" becomes
`join_closes_after_minutes` (15) read through the state: a session is
`open` until then and nothing in the vendor's cloud is finished ten minutes
after a class, so a second number five minutes from the first would be one
more constant with no reason to differ. Listed under "Before this can be
ready".

**No vendor name reaches the Service or the query.** The providers swept are
the tagged finders' `provider()` values (`whereIn('provider', …)`), and
whether one link can be looked at is `FindsRecordings::handles($joinUrl)`.
`app/Integrations/Zoom/ZoomMeetingLink` is the only place a Zoom host or
path pattern appears (`T-142`, `D-022`). A personal-room or vanity link is
therefore never a candidate — `handles()` answers false — and the panel says
Qori cannot look for recordings of that link; `D-027`'s fourth hold reason
is applied before the call rather than after it, and `T-142` is asked to
confirm `handles()` behaves that way (below).

**The Group's connection is read once per candidate and decides three ways.**
`Connection::query()->where('provider', $episode->provider->connection())->first()`
inside `runFor()` — group-scoped, no `acrossAllGroups()`. It must be
`isLive()` (`T-044`: usable and not marked for reconnect) and its
`settings['cloud_recording']` must not be `false` (`T-141` writes the key;
`null` means unread and is still tried, because a Basic account already
answers `false`). Before the finder runs, `ConnectionService::fresh()` with
the same timeout renews an access token that lasts an hour (`T-141`'s
Notes). A Group with no usable connection is skipped without a vendor call.

**Backoff is a step table read from config, and every attempt stamps
`recording_checked_at`.** `qori.live.check_backoff` is `T-123`'s: every 15
minutes until 3 hours after the end, hourly until 24, every 4 hours until 48. `dueForCheck()` picks the step by hours since `ends_at` and asks whether
the last check is older than the step; `nextCheckAt()` is the same sum, for
the panel. The stamp is written whether the finder answered, found nothing
or threw: a vendor that is down is retried at the step's cadence rather
than every five minutes, and "last checked" on the panel is the last
attempt, which is the honest reading of the word. A `Throwable` from the
vendor is `report()`ed and the run goes on to the next Episode; one
Episode's failure never stops a sweep, and the heartbeat counts it.

**`attachFound()` writes under the row lock, skips what it already holds by
`vendor_ref`, and numbers parts by start time.** `T-124`'s
`withLockedContent()` is the lock every write to a live Episode uses
(`D-026`); its callback is `Closure(array $content, Episode $locked): array`
(`T-124`'s Decisions), so this task's writes set columns on `$locked` and
hand the content array straight back. Inside it the found list is filtered
against the Episode's existing `vendor_ref`s — a hidden, rejected, held or
published row is never inserted twice, which is what keeps `T-144`'s reject
final and answers owner acceptance 7 — then written in `startedAt` order with
`position` continuing from the highest existing, so Part 2 is the later
instance and a duplicate leaves no gap. The unique index
`(episode_id, vendor_ref)` (`T-126`) is the backstop for two sweeps racing,
not the mechanism.

**A visible recording ends the sweep for that Episode, so a later part
arrives by Check now or by a paste, never by the sweep.** `stateFor()` answers
`ready` the moment a row is published and unhidden (`T-126`), and `ready` is
not `waiting`, so the candidate query drops the Episode — which is the
property that stops Qori polling a vendor about a session whose recording the
creator has already pasted. The two-or-more hold therefore protects any find
that returns two instances at once, including one made by `T-144`'s Check now
after a first part was published; it is not a promise that the sweep keeps
watching afterwards. A creator whose meeting restarted and whose first part
published presses Check now, or pastes the second link.

**Publication is decided per row inside the lock from the Series setting
and `D-027`'s four reasons, and the Group's cap adds a fifth.** A row is
published (`published_at = $now`, `needs_review = false`) only when the
Series' `recording_publication` is `automatic` **and** the find returned
one instance **and** that instance started within `match_tolerance_minutes`
of `starts_at` **and** it ran at least `min_recording_minutes` **and** the
Group is not over its Series cap. Otherwise `published_at` stays null and
`needs_review` is true. The cap rule follows `LocksOverCapSeries`'s own
line (`app/Concerns/LocksOverCapSeries.php:19-26`): a held row changes
nothing a Peer sees, so the sweep still looks and holds; publishing changes
what the Group offers, so it does not. A count of two or more holds every
row of that find, including a later part returned beside a part already
published — the restarted meeting and the early test recording are exactly
the cases `D-027` names, and a held Part 2 costs the creator one click in
`T-144`. The reason is logged per row and not stored: `D-027`'s table has
no column for it, and `T-144`'s list shows the start and the length, which
is what the creator decides on.

**The email is queued by the caller that published, through `T-128`'s
method, and `LiveSessionService` takes no notice service.** `T-129` gives
`SessionNoticeService` a `LiveSessionService` by constructor promotion; a
`LiveSessionService` that took `SessionNoticeService` back would be a cycle
the container cannot build. So the orchestration that must queue —
`RecordingService::search()` — lives on `RecordingService`, which already
holds both (`T-127`, `T-128`) and gains `ConnectionService`; it calls
`fresh()`, the finder, `attachFound()`, and then
`queueRecordingReady($recording)` for each row that came back published. The
timeout is a parameter rather than a constant read inside, so `T-144`'s Check
now can call the same method instead of the `checkNow()` its draft declares —
proposed in the Notes, and `T-144`'s to take.

**`LiveState::Review` is the creator's reading of `waiting` or `overdue`
with a held row, from `creatorStateFor()`; `stateFor()` never returns it.**
`D-026`: `review` is creator only and a Peer sees `waiting`. `T-127`'s Notes
place the arm inside `stateFor()`, after its `ready` arm; doing that
would make `SharedController::liveCard()` and `LiveSessionCard.vue` — the
Peer's controller and card, neither this task's file in the stream's claim
order — render an unknown state as the time alone. A second method the
creator's controller calls keeps the one state model and leaves the Peer's
files untouched; `T-127`'s and `T-125`'s sentences are edited (Notes).
`Review` outranks
`waiting` and `overdue` only: a visible recording (`ready`), a declaration
(`not_recorded`) and a cancellation are decisions and outrank a held row.

**The nudge waits for Qori, and a held row is never nudged.** `D-028`:
`creator_recording_needed` goes at `creator_nudge_hours` without detection
and at `recording_wait_hours` with it. `SessionNoticeService::creatorNudgeCandidates()`
(`T-129`) gains a `reject()` of every Episode `isSearching()` — a finder
handles its link, a usable connection keeps cloud recordings, and
`recording_wait_hours` has not passed — and reads the state through
`creatorStateFor()`, so `review` is neither `waiting` nor `overdue` and the
"Add the recording of :title" email never goes to a creator who has one to
check. Whether a held row earns an email of its own is the owner's (below);
this task sends none.

**The setting rides the existing Series PATCH and the details form, hidden
until it can do something.** `UpdateSeriesRequest` gains one `sometimes`
enum rule; `SeriesService::update()` one change arm; `Series` the fillable
and the cast. `SeriesForm.vue` renders two radios only when the page prop
`recordingPublication.available` is true — this Group holds a usable
connection on a provider with a finder — because a switch that changes
nothing is the dead control `D-021` forbids. The form reads the prop from
`usePage().props`, as `T-126`'s panel reads `recordingCopy`, so
`share/series/Show.vue` is not edited (the stream gives that page to
`T-123`, `T-130`, `T-132` and `T-137`). The migration's default is
`review_first` on every Series, existing ones included: automatic
publication is chosen, never inherited (owner acceptance 6).

**A reschedule clears the last check.** `T-124` reserved the line: when
`touchSchedule()` finds `starts_at` or `ends_at` dirty it also nulls
`recording_checked_at`, so a session moved to its real time is looked at on
the next run rather than at the cadence its old age earned it.

**The vendor's name reaches the panel as `:provider`, from `T-141`'s
`connections.providers.<provider>.name`, and no line under `live.*` names
one.** `D-025` allows a vendor name on Join and Watch and `D-016` in
provider-choice copy, which is where `T-141`'s line stands; the panel's
detection lines interpolate it, so "Looking in your Zoom cloud" renders
and the lang file stays vendor-neutral. The same placeholder fills `T-126`'s
`live.panel.recording.source.zoom`, which this task adds. No line says
"live now", "has ended", "on its way" or "processing" (`D-026`); "last
checked" and "found" are things Qori did.

**One timeout here, and `search()`'s parameter is the seam.**
`LiveSessionService::SWEEP_TIMEOUT_SECONDS = 30` for the command, nobody
waiting, named after `T-091`'s and `T-044`'s sweep constants. Check now's
shorter one is `T-144`'s `LiveSessionService::CHECK_NOW_TIMEOUT_SECONDS = 5`,
which its draft already declares and which a creator waiting on a click is
the reason for; `search(Episode, CarbonImmutable, int $timeoutSeconds)` takes
the number rather than choosing it, so neither task declares the other's.

**The command is `T-128`'s shape.** `Group::query()->cursor()` inside
`CurrentGroup::runFor()`, `--dry-run` that lists candidates and calls
nothing, one `Log::info` heartbeat per run with the counts `T-019` will
watch, `Schedule::command(...)->everyFiveMinutes()->withoutOverlapping()->onOneServer()`
with the interval marked provisional. No `acrossAllGroups()` caller, so the
allow-list in `tests/Feature/Admin/ConsoleAccessTest.php:131-152` is
unchanged. A paused Group is swept like any other: the recording is
something its Peers already have, and `T-128` sends to a paused Group for
the same reason.

**`RecordingSource` is chosen by a `match` on the finder's provider, never
by the coincident value.** `EpisodeProvider::Zoom` and `RecordingSource::Zoom`
both spell `zoom`; `EpisodeProvider::connection()`'s docblock says why two
enums agreeing on a spelling is not a rule to lean on.

**Tests fake the finder, not Zoom.** A `Tests\Doubles\FindsRecordingsInMemory`
implements the contract with a preset list and a record of its calls, bound
in place of the tagged finders; `Http::preventStrayRequests()` proves no
request leaves. What `ZoomRecordings` does with a payload is `T-142`'s
suite against `T-122`'s fixtures; what Qori does with what it returns is
this one.

**No new config, no factory row, no seeder row.** Every number is `T-123`'s
`qori.live` block; `series.recording_publication` has a database default;
the design-review Series is not switched.

## Preconditions

**Data this task verifies against:** a clean database. The feature tests
build a Group on `start` with `timezone` `Australia/Brisbane`, an owner and
an accepted Collaborator as `tests/Feature/Series/LiveSessionTest.php:41-60`
does; a published Series; live Zoom Episodes through
`$series->episodes()->create([...])` with `starts_at` and `ends_at` in the
past and content `['join_url' => 'https://zoom.us/j/91827405566', 'records' => true]`,
as `T-129`'s tests do, because `EpisodeService::add()` refuses a past start;
a Zoom connection through `Connection::factory()->zoom()` (`T-141`) inside
`CurrentGroup::runFor()`, as `tests/Feature/Storage/PlaybackTest.php:112`
creates one; Peers through `AccessService::grant()`. The clock is a
`CarbonImmutable` passed in; the command cases move it with
`CarbonImmutable::setTestNow()`.

**Equipment:** none for the suite. For the walk in the last acceptance
line: `T-141`'s development app on Qori's own Zoom account, connected to a
local Group, and one meeting hosted from that account, recorded to the
cloud, whose join link is a live Episode's — then
`php artisan qori:recordings:find --dry-run` and the plain run, read back
through `docs/tinker/live-sessions.md`.

**Spike:** none owed by this task. It reads no vendor payload: every vendor
fact reaches it as an `App\Data\SessionRecording` from `T-142`, whose
shape `T-122`'s fixtures under `tests/Fixtures/zoom/recordings/` fix.

## Scope

**In:**

- `series.recording_publication` and `episodes.recording_checked_at`, the
  migration, `RecordingPublication`, `Series::$fillable`, the cast and
  `publishesRecordingsAutomatically()`.
- `LiveSessionService`: the tagged finders by constructor,
  `SWEEP_TIMEOUT_SECONDS`, `sweepCandidates()`, `finderProviders()`,
  `finderFor()`, `searchableConnection()`, `finderConnection()`,
  `dueForCheck()`, `nextCheckAt()`, `everyMinutesAt()`, `markChecked()`,
  `attachFound()`, `holdReason()`, `sourceFor()`, `isSearching()`,
  `creatorStateFor()`, `detectionFor()`.
- `RecordingService::search()` and its `ConnectionService` dependency;
  `App\Data\RecordingSearch`, `App\Data\RecordingDetection`,
  `App\Enums\DetectionStatus`.
- `EpisodeRecording::isHeld()`; `Episode::heldRecordings()`
  and the `recording_checked_at` cast.
- `FindRecordingsCommand` (`qori:recordings:find {--dry-run}`), the schedule
  line, the heartbeat; the `$finders` binding in
  `IntegrationServiceProvider`.
- `SessionNoticeService::creatorNudgeCandidates()`: the hold for a session
  Qori is looking for, and `creatorStateFor()` in its filter.
- `EpisodeService::touchSchedule()` clearing `recording_checked_at`.
- `UpdateSeriesRequest`, `SeriesService::update()`, `SeriesController::show()`'s
  `recordingPublication` prop, the radios on `SeriesForm.vue`.
- `SeriesController::show()`'s `state` from `creatorStateFor()`, the
  `detection` block per live Episode, the held rows' lines; the `review`
  state, the detection line and the held rows on `LiveSessionPanel.vue`.
- The lang lines, `docs/flows/live-sessions.md`, `docs/tinker/live-sessions.md`.

**Out:**

- Publish, reject, picking among several held rows, Check now and
  `CHECK_NOW_TIMEOUT_SECONDS` (`T-144`). Between this task and that one a held
  row is listed and cannot be published from the panel; the paste form and
  "There's no recording" stay the creator's way out (Notes).
- Looking again once a recording is visible: `ready` is not a candidate, so a
  later part reaches the Episode through `T-144`'s Check now or a paste (see
  the decision).
- Telling Peers about a corrected recording (`T-140`).
- `ZoomRecordings`, `ZoomMeetingLink`, `ZoomClient`, the `recording-finders`
  tag and `SessionRecording` (`T-142`); the connection page and its settings
  read (`T-141`); the fixtures (`T-122`).
- An email to the creator about a held recording; no `SessionNoticeKind`
  for it exists and this task adds none (below).
- Webhooks, `recording.completed`, `POST /webhooks/zoom` and anything that
  clears `recording_checked_at` from a vendor signal (`D-027`: after
  Marketplace publication, and then only as a speed-up).
- Re-reading the connection's recording settings on a schedule (`T-141`
  reads them at connect; `T-144`'s draft is told about Check now).
- Teams and Meet recordings: no finder exists, and a `teams` or `link`
  Episode says nothing on the panel about detection.
- Any Peer-facing change: no route, no line on `LiveSessionCard.vue`, no
  key in `SharedController::liveCard()`; a Peer reads `waiting` while a
  row is held, and the public page is unchanged.
- The `review` arm inside `stateFor()`; see the decision.
- A migration of `recording_publication` to a per-Episode setting, or a
  Group-level default; per Series is `D-027`'s.

## Files

| Path                                                                            | Change | Notes                                                                                                                  |
| ------------------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------- |
| `database/migrations/2026_09_18_000600_add_recording_publication_to_series.php` | new    | `series.recording_publication`, `episodes.recording_checked_at`                                                        |
| `app/Enums/RecordingPublication.php`                                            | new    | `ReviewFirst`, `Automatic`                                                                                             |
| `app/Enums/DetectionStatus.php`                                                 | new    | What the panel's detection line says                                                                                   |
| `app/Data/RecordingSearch.php`                                                  | new    | One search's outcome: found, inserted, published, held, failed, skipped                                                |
| `app/Data/RecordingDetection.php`                                               | new    | What the panel shows: status, provider, last and next check, held count                                                |
| `app/Models/Series.php`                                                         | edit   | `recording_publication` fillable and cast; `publishesRecordingsAutomatically()`                                        |
| `app/Models/Episode.php`                                                        | edit   | `recording_checked_at` fillable and cast; `heldRecordings()`                                                           |
| `app/Models/EpisodeRecording.php`                                               | edit   | `isHeld()`                                                                                                             |
| `app/Services/LiveSessionService.php`                                           | edit   | Constructor, `SWEEP_TIMEOUT_SECONDS`, candidates, backoff, `attachFound()`, `creatorStateFor()`, `detectionFor()`      |
| `app/Services/RecordingService.php`                                             | edit   | `search()`; `ConnectionService` promoted beside `T-127`'s and `T-128`'s                                                |
| `app/Services/SessionNoticeService.php`                                         | edit   | `creatorNudgeCandidates()` holds a searching Episode; filters through `creatorStateFor()`                              |
| `app/Services/EpisodeService.php`                                               | edit   | `touchSchedule()` nulls `recording_checked_at` when the schedule moved                                                 |
| `app/Services/SeriesService.php`                                                | edit   | `update()` writes `recording_publication`                                                                              |
| `app/Http/Requests/Share/UpdateSeriesRequest.php`                               | edit   | The enum rule                                                                                                          |
| `app/Http/Controllers/Share/SeriesController.php`                               | edit   | `recordingPublication` prop; `state` from `creatorStateFor()`; `detection`; held lines; `:provider` on the source line |
| `app/Console/Commands/FindRecordingsCommand.php`                                | new    | `qori:recordings:find {--dry-run}`                                                                                     |
| `app/Providers/IntegrationServiceProvider.php`                                  | edit   | `LiveSessionService` is given the `recording-finders` tag                                                              |
| `routes/console.php`                                                            | edit   | The schedule line beside `T-128`'s                                                                                     |
| `resources/js/components/series/SeriesForm.vue`                                 | edit   | Two radios, from `usePage().props.recordingPublication`, when available                                                |
| `resources/js/components/series/LiveSessionPanel.vue`                           | edit   | `review`; the detection line; held rows with no Hide                                                                   |
| `lang/en/live.php`                                                              | edit   | `panel.detection.*`, `panel.review.*`, `panel.recording.source.zoom`                                                   |
| `lang/en/series.php`                                                            | edit   | `recording_publication.*`                                                                                              |
| `docs/flows/live-sessions.md`                                                   | edit   | "Finding a recording": the sweep, the hold, the publication rule, the nudge's move                                     |
| `docs/flows/README.md`                                                          | edit   | The `live-sessions.md` row names the sweep                                                                             |
| `docs/tinker/live-sessions.md`                                                  | edit   | Candidates, a search by hand, `--dry-run`, switching a Series                                                          |
| `tests/Doubles/FindsRecordingsInMemory.php`                                     | new    | The finder double                                                                                                      |
| `tests/Feature/Series/FindRecordingsTest.php`                                   | new    | 18 cases                                                                                                               |
| `tests/Feature/Console/FindRecordingsCommandTest.php`                           | new    | 6 cases                                                                                                                |
| `tests/Feature/Series/RecordingPublicationTest.php`                             | new    | 6 cases                                                                                                                |
| `tests/Feature/Mail/RecordingNeededTest.php`                                    | edit   | +2 cases (`T-129`'s file)                                                                                              |

`config/qori.php` is not touched: `check_backoff`, `recording_wait_hours`,
`join_closes_after_minutes`, `match_tolerance_minutes`,
`min_recording_minutes` and `creator_nudge_hours` are `T-123`'s, read and
never redeclared. `routes/share/series.php` is not touched: the PATCH
exists. Neither `resources/js/pages/share/series/Show.vue` nor
`resources/js/pages/shared/Show.vue` nor
`app/Http/Controllers/Shared/SharedController.php` nor
`resources/js/components/series/LiveSessionCard.vue` is edited — see the
`creatorStateFor()` and `SeriesForm.vue` decisions. No factory or seeder
row: the column has a default. `qori:reachability` is unaffected: no new
route, and `share.settings.integrations` is already linked.

## Database

| Table      | Column                  | Type      | Null | Default        | Index / constraint                                                                      |
| ---------- | ----------------------- | --------- | ---- | -------------- | --------------------------------------------------------------------------------------- |
| `series`   | `recording_publication` | string    | no   | `review_first` | A `RecordingPublication` value; no index — read per Series inside the lock              |
| `episodes` | `recording_checked_at`  | timestamp | yes  | null           | None; the candidates query is served by `T-123`'s partial `episodes_live_ends_at_index` |

Migration: `database/migrations/2026_09_18_000600_add_recording_publication_to_series.php`

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Where a found recording goes, and when Qori last looked (D-027).
 *
 * Review-first is the default on every Series, existing ones included:
 * automatic publication is chosen on the Series, never inherited.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::table('series', function (Blueprint $table): void {
            $table->string('recording_publication')->default('review_first');
        });

        Schema::table('episodes', function (Blueprint $table): void {
            // When qori:recordings:find last looked at this session. Null
            // means never — or a reschedule since, which starts it over.
            $table->timestamp('recording_checked_at')->nullable();
        });
    }

    public function down(): void
    {
        Schema::table('episodes', function (Blueprint $table): void {
            $table->dropColumn('recording_checked_at');
        });

        Schema::table('series', function (Blueprint $table): void {
            $table->dropColumn('recording_publication');
        });
    }
};
```

## Code

```php
namespace App\Enums;

/** What a Series does with a recording Qori found (D-027). */
enum RecordingPublication: string
{
    /** Held with needs_review until the creator publishes it (T-144). The default. */
    case ReviewFirst = 'review_first';

    /** Published on the find, unless the match is ambiguous. */
    case Automatic = 'automatic';
}
```

```php
namespace App\Enums;

/**
 * What the creator's panel says about finding this session's recording.
 * Null on the panel (no line) for an Episode whose provider has no finder,
 * or whose state is ready, not_recorded or cancelled.
 */
enum DetectionStatus: string
{
    /** No usable connection for the provider: point at the Integrations page. */
    case NotConnected = 'not_connected';

    /** A connection whose settings say cloud recording is off (T-141). */
    case CloudRecordingOff = 'cloud_recording_off';

    /** No finder handles the join link — a personal room, a vanity link, or none. */
    case LinkNotSearchable = 'link_not_searchable';

    /** Upcoming or open: Qori will look after the session. */
    case WillSearch = 'will_search';

    /** Waiting: the sweep is looking, with a last and a next check. */
    case Searching = 'searching';

    /** Overdue: recording_wait_hours have passed and the sweep has stopped. */
    case Stopped = 'stopped';
}
```

```php
namespace App\Data;

use App\Models\EpisodeRecording;
use Carbon\CarbonImmutable;
use Illuminate\Support\Collection;

/** What one call to RecordingService::search() did. */
final class RecordingSearch
{
    /** Why nothing was called. Diagnostics, never copy. */
    public const SKIPPED_NO_FINDER = 'no_finder';

    public const SKIPPED_NO_CONNECTION = 'no_connection';

    /**
     * @param  Collection<int, EpisodeRecording>  $inserted  the rows written this time, published or held
     */
    public function __construct(
        /** What the finder returned, known rows included. */
        public int $found = 0,
        public Collection $inserted = new Collection,
        public int $published = 0,
        public int $held = 0,
        public ?CarbonImmutable $checkedAt = null,
        public ?CarbonImmutable $nextCheckAt = null,
        /** The vendor call threw; reported, stamped, nothing written. */
        public bool $failed = false,
        /** One of the SKIPPED_* constants when no call was made. */
        public ?string $skipped = null,
    ) {}

    /** No call was made; $skipped carries the reason. */
    public static function withoutCall(string $reason): self;

    /** The vendor threw; the attempt is stamped and nothing was written. */
    public static function afterFailure(CarbonImmutable $checkedAt, ?CarbonImmutable $nextCheckAt): self;
}
```

```php
namespace App\Data;

use App\Enums\ConnectionProvider;
use App\Enums\DetectionStatus;
use Carbon\CarbonImmutable;

/** What the creator's panel shows about detection for one live Episode. */
final class RecordingDetection
{
    public function __construct(
        public DetectionStatus $status,
        /** The connection's provider, for the lang name; null when the provider has no finder. */
        public ?ConnectionProvider $provider,
        public ?CarbonImmutable $checkedAt = null,
        public ?CarbonImmutable $nextCheckAt = null,
        /** Rows held for review on this Episode. */
        public int $held = 0,
    ) {}
}
```

```php
// App\Models\Series — beside T-126's and T-135's additions.

/** @property RecordingPublication $recording_publication */

// $fillable gains 'recording_publication'; casts() gains
'recording_publication' => RecordingPublication::class,

/** Whether a clear find is published without the creator (D-027). Review-first is the default. */
public function publishesRecordingsAutomatically(): bool;
// return $this->recording_publication === RecordingPublication::Automatic;
```

```php
// App\Models\Episode — beside T-123's ends_at and T-126's recordings().

/** @property ?Carbon $recording_checked_at */

// $fillable gains 'recording_checked_at'; casts() gains
'recording_checked_at' => 'datetime',

/**
 * Found by the sweep and waiting for the creator (D-027).
 *
 * @return Collection<int, EpisodeRecording>
 */
public function heldRecordings(): Collection;
// $this->recordings->filter(fn (EpisodeRecording $recording): bool => $recording->isHeld())->values()
```

```php
// App\Models\EpisodeRecording — beside T-126's isVisible() and scopeVisible().

/**
 * Found, not yet published, not rejected: the creator's to decide (D-027).
 *
 * needs_review is read as well as the two timestamps because it is the column
 * D-027 gives the fact, and publish() and reject() (T-144) both clear it; a row
 * with all three agreeing is the only held row this task ever writes.
 */
public function isHeld(): bool;
// return $this->needs_review && $this->published_at === null && $this->hidden_at === null;
```

No `scopeHeld()`: the two callers below read `Episode::heldRecordings()` off
the loaded relation, as `T-126`'s `visibleRecordings()` does, so the creator's
page and `T-129`'s nudge query do not gain one count query per live Episode.
This answers `T-144`'s open question "whether `T-143` declares
`EpisodeRecording::isHeld()` or a `scopeHeld()`": `isHeld()` and
`heldRecordings()`, and `T-144`'s row for `isHeld()` becomes a no-op.

```php
namespace App\Services;

use App\Data\RecordingDetection;
use App\Data\SessionRecording;
use App\Enums\DetectionStatus;
use App\Enums\EpisodeProvider;
use App\Enums\EpisodeType;
use App\Enums\LiveState;
use App\Enums\RecordingSource;
use App\Integrations\Contracts\FindsRecordings;
use App\Models\Connection;
use App\Models\Episode;
use App\Models\EpisodeRecording;
use App\Models\Series;
use Carbon\CarbonImmutable;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Log;

/**
 * T-124's lock, T-125's state, T-127's declarations, T-134's cancel and copy —
 * and, from this task, finding a recording (D-027). No vendor imports: the
 * finders are the tagged contract, and which link a vendor can look at is
 * the vendor folder's answer.
 */
class LiveSessionService
{
    // T-125's BLOCKED_NOT_OPEN, BLOCKED_NO_LINK and T-134's NEXT_SESSION_DAYS unchanged.

    /**
     * The sweep's vendor timeout: nobody is waiting. The value T-044's and
     * T-091's sweep constants carry. Check now's shorter one is T-144's
     * CHECK_NOW_TIMEOUT_SECONDS; search() takes the number as a parameter.
     */
    public const SWEEP_TIMEOUT_SECONDS = 30;

    /** Why a found row was held. Logged per row, never stored (D-027 has no column) and never copy. */
    public const HELD_REVIEW_FIRST = 'review_first';

    public const HELD_SEVERAL = 'several_found';

    public const HELD_START = 'start_far_from_schedule';

    public const HELD_SHORT = 'shorter_than_minimum';

    public const HELD_OVER_CAP = 'group_over_cap';

    /**
     * No default, exactly as PlaybackTicketService takes its tagged providers
     * (app/Services/PlaybackTicketService.php:32-36): a missing binding is a
     * container error, not an empty sweep that looks like nothing to do.
     *
     * @param  iterable<FindsRecordings>  $finders  the `recording-finders` tag (T-142), given in IntegrationServiceProvider
     */
    public function __construct(private iterable $finders) {}

    /**
     * The EpisodeProviders the tagged finders cover, de-duplicated. The one
     * place the set is derived, so the query, the connection read and the
     * panel all agree on which providers Qori can look in.
     *
     * @return Collection<int, EpisodeProvider>
     */
    public function finderProviders(): Collection;
    // return collect($this->finders)
    //     ->map(fn (FindsRecordings $finder): EpisodeProvider => $finder->provider())
    //     ->unique()
    //     ->values();

    /**
     * This Group's live Episodes the sweep should look at now (D-027):
     * on a provider with a finder, scheduled to end between
     * qori.live.recording_wait_hours and qori.live.join_closes_after_minutes
     * ago, `waiting` by stateFor(), with a link a finder handles, in a Group
     * whose connection is usable and keeps cloud recordings, and due by the
     * backoff table. Runs inside CurrentGroup::runFor(); Episode has no group
     * scope and is reached through this Group's Series.
     *
     * @return Collection<int, Episode>
     */
    public function sweepCandidates(CarbonImmutable $now): Collection;
    // $providers = $this->finderProviders();
    // if ($providers->isEmpty()) return new Collection;
    //
    // return Episode::query()
    //     ->where('type', EpisodeType::Live)
    //     ->whereIn('provider', $providers)
    //     ->whereIn('series_id', Series::query()->select('id'))                    // this Group's, through the scope
    //     ->whereBetween('ends_at', [
    //         $now->subHours((int) config('qori.live.recording_wait_hours')),
    //         $now->subMinutes((int) config('qori.live.join_closes_after_minutes')),
    //     ])
    //     ->with('recordings')
    //     ->orderBy('ends_at')
    //     ->get()
    //     ->filter(fn (Episode $episode): bool => $this->stateFor($episode, $now) === LiveState::Waiting)
    //     ->filter(fn (Episode $episode): bool => $this->finderFor($episode) !== null)
    //     ->filter(fn (Episode $episode): bool => $this->searchableConnection($episode) !== null)
    //     ->filter(fn (Episode $episode): bool => $this->dueForCheck($episode, $now))
    //     ->values();

    /** The tagged finder for this Episode's provider that handles its join link, or null. Vendor patterns live in the finder. */
    public function finderFor(Episode $episode): ?FindsRecordings;
    // $url = $episode->content['join_url'] ?? null;
    // if (! is_string($url) || $url === '') return null;
    // foreach ($this->finders as $finder) {
    //     if ($finder->provider() === $episode->provider && $finder->handles($url)) return $finder;
    // }
    // return null;

    /**
     * The current Group's connection this Episode's recordings would be read
     * with: the provider's, live (T-044), and not saying cloud recording is
     * off (T-141 writes settings.cloud_recording; null is unread and still tried).
     */
    public function searchableConnection(Episode $episode): ?Connection;
    // $provider = $episode->provider->connection();
    // if ($provider === null) return null;
    // $connection = Connection::query()->where('provider', $provider)->first();
    // if (! $connection instanceof Connection || ! $connection->isLive()) return null;
    // return ($connection->settings['cloud_recording'] ?? null) === false ? null : $connection;

    /** Any live connection in the current Group on a provider that has a finder — whether the Series setting can do anything. */
    public function finderConnection(): ?Connection;
    // $providers = $this->finderProviders()
    //     ->map(fn (EpisodeProvider $provider): ?ConnectionProvider => $provider->connection())
    //     ->filter()
    //     ->values();
    //
    // if ($providers->isEmpty()) return null;
    //
    // return Connection::query()->whereIn('provider', $providers)->get()
    //     ->first(fn (Connection $connection): bool => $connection->isLive());

    /**
     * Whether the last check is older than the backoff step for the
     * session's age (D-027). Never checked is due. The steps are
     * qori.live.check_backoff, first match by hours since ends_at; past the
     * last step nothing is due.
     */
    public function dueForCheck(Episode $episode, CarbonImmutable $now): bool;
    // $every = $this->everyMinutesAt($episode, $now);
    // if ($every === null) return false;
    // $last = $episode->recording_checked_at;
    // return $last === null || CarbonImmutable::instance($last)->addMinutes($every) <= $now;

    /** When the sweep looks next: the last check plus its step; null when never checked (due now) or past the last step. */
    public function nextCheckAt(Episode $episode, CarbonImmutable $now): ?CarbonImmutable;
    // $every = $this->everyMinutesAt($episode, $now); $last = $episode->recording_checked_at;
    // return $every === null || $last === null ? null : CarbonImmutable::instance($last)->addMinutes($every);

    /** The step's every_minutes for the session's age, or null past the table. */
    private function everyMinutesAt(Episode $episode, CarbonImmutable $now): ?int;
    // $hours = $episode->ends_at->toImmutable()->diffInMinutes($now) / 60;   // hours since the scheduled end, fractional
    // foreach ((array) config('qori.live.check_backoff') as $step) {
    //     if ($hours < (float) $step['until_hours']) return (int) $step['every_minutes'];
    // }
    // return null;

    /**
     * Stamp the attempt under the lock, writing nothing else. The failure
     * path's write. T-124's callback takes the re-read content and the locked
     * row and returns the content to save, so this hands it back untouched.
     */
    public function markChecked(Episode $episode, CarbonImmutable $now): Episode;
    // return $this->withLockedContent($episode, function (array $content, Episode $locked) use ($now): array {
    //     $locked->recording_checked_at = $now;
    //
    //     return $content;
    // });

    /**
     * Land what a finder returned (D-027), under the row lock: skip every
     * vendorRef the Episode already holds (hidden, rejected, held or
     * published — never inserted twice), write the rest in startedAt order
     * with position continuing, publish only when the Series says automatic
     * and the match is clear, and stamp recording_checked_at. Returns the
     * rows written; the caller queues recording_ready for the published ones.
     *
     * @param  list<SessionRecording>  $found
     * @return Collection<int, EpisodeRecording>
     */
    public function attachFound(Episode $episode, array $found, CarbonImmutable $now): Collection;
    // $inserted = new Collection;
    //
    // $this->withLockedContent($episode, function (array $content, Episode $locked) use ($found, $now, &$inserted): array {
    //     $locked->recording_checked_at = $now;
    //
    //     $series = Series::query()->findOrFail($locked->series_id);         // scoped: inside the Group
    //     $known = $locked->recordings()->whereNotNull('vendor_ref')->pluck('vendor_ref')->all();
    //     $position = (int) $locked->recordings()->max('position');
    //     $source = $this->sourceFor($locked->provider);
    //
    //     $new = collect($found)
    //         ->reject(fn (SessionRecording $recording): bool => in_array($recording->vendorRef, $known, true))
    //         ->sortBy(fn (SessionRecording $recording): int => $recording->startedAt->getTimestamp())
    //         ->values();
    //
    //     foreach ($new as $recording) {
    //         $reason = $this->holdReason($series, $locked, $recording, count($found));
    //         $published = $reason === null;
    //
    //         $row = $locked->recordings()->create([
    //             'group_id' => $series->group_id,
    //             'position' => ++$position,
    //             'source' => $source,
    //             'vendor_ref' => $recording->vendorRef,
    //             'url' => $recording->url,
    //             'passcode' => $recording->passcode,
    //             'started_at' => $recording->startedAt,
    //             'duration_minutes' => $recording->durationMinutes,
    //             'available_until' => $recording->availableUntil,
    //             'found_at' => $now,
    //             'published_at' => $published ? $now : null,
    //             'hidden_at' => null,
    //             'needs_review' => ! $published,
    //         ]);
    //
    //         Log::info("Recording {$row->getKey()} found for episode {$locked->getKey()}: ".($published ? 'published' : "held ({$reason})").'.');
    //         $inserted->push($row);
    //     }
    //
    //     return $content;                                                    // this task writes columns, never content
    // });
    //
    // return $inserted;

    /**
     * Null when the row may be published; else the HELD_* reason, checked in
     * this order: the Series setting, the Group's cap, several found, the
     * start outside qori.live.match_tolerance_minutes of starts_at, a length
     * under qori.live.min_recording_minutes (D-027).
     */
    public function holdReason(Series $series, Episode $episode, SessionRecording $recording, int $foundCount): ?string;
    // return match (true) {
    //     ! $series->publishesRecordingsAutomatically() => self::HELD_REVIEW_FIRST,
    //     $series->group?->isOverSeriesCap() ?? false => self::HELD_OVER_CAP,
    //     $foundCount >= 2 => self::HELD_SEVERAL,
    //     abs($episode->starts_at->toImmutable()->diffInMinutes($recording->startedAt, false)) > (int) config('qori.live.match_tolerance_minutes') => self::HELD_START,
    //     $recording->durationMinutes < (int) config('qori.live.min_recording_minutes') => self::HELD_SHORT,
    //     default => null,
    // };

    /** A match, not RecordingSource::from($provider->value): the two enums agreeing on a spelling is not a rule. */
    private function sourceFor(EpisodeProvider $provider): RecordingSource;
    // return match ($provider) { EpisodeProvider::Zoom => RecordingSource::Zoom };

    /**
     * Whether Qori is looking, or will still look, for this session's
     * recording: a finder handles its link, a usable connection keeps cloud
     * recordings, and recording_wait_hours have not passed. T-129's nudge
     * holds while this is true (D-028).
     */
    public function isSearching(Episode $episode, CarbonImmutable $now): bool;
    // return $episode->isLive()
    //     && $episode->ends_at !== null
    //     && $now < $episode->ends_at->toImmutable()->addHours((int) config('qori.live.recording_wait_hours'))
    //     && $this->finderFor($episode) !== null
    //     && $this->searchableConnection($episode) !== null;

    /**
     * The creator's reading of the state (D-026): `review` when the sweep
     * holds a row and the card would otherwise say waiting or overdue. A
     * Peer never sees it — SharedController calls stateFor(), which never
     * answers Review.
     */
    public function creatorStateFor(Episode $episode, CarbonImmutable $now): LiveState;
    // $state = $this->stateFor($episode, $now);
    // return in_array($state, [LiveState::Waiting, LiveState::Overdue], true) && $episode->heldRecordings()->isNotEmpty()
    //     ? LiveState::Review
    //     : $state;

    /**
     * What the panel's detection line should say, or null when there is
     * nothing to say: a provider with no finder, or a state that is ready,
     * not_recorded or cancelled. Reads the current Group's connection.
     *
     * stateFor(), not creatorStateFor(): whether Qori is still looking is a
     * fact about the clock, and an overdue session holding a row has stopped
     * being looked at however the panel labels it.
     */
    public function detectionFor(Episode $episode, CarbonImmutable $now): ?RecordingDetection;
    // if (! $episode->isLive()) return null;
    // if (! $this->finderProviders()->contains(fn (EpisodeProvider $provider): bool => $provider === $episode->provider)) return null;
    //
    // $state = $this->stateFor($episode, $now);
    // if (in_array($state, [LiveState::Ready, LiveState::NotRecorded, LiveState::Cancelled], true)) return null;
    // $provider = $episode->provider->connection();
    // $connection = Connection::query()->where('provider', $provider)->first();
    // $held = $episode->heldRecordings()->count();
    //
    // $status = match (true) {
    //     ! $connection instanceof Connection || ! $connection->isLive() => DetectionStatus::NotConnected,
    //     ($connection->settings['cloud_recording'] ?? null) === false => DetectionStatus::CloudRecordingOff,
    //     $this->finderFor($episode) === null => DetectionStatus::LinkNotSearchable,
    //     in_array($state, [LiveState::Upcoming, LiveState::Open], true) => DetectionStatus::WillSearch,
    //     $state === LiveState::Overdue => DetectionStatus::Stopped,
    //     default => DetectionStatus::Searching,                                   // Waiting
    // };
    //
    // return new RecordingDetection(
    //     $status,
    //     $provider,
    //     $episode->recording_checked_at?->toImmutable(),
    //     $status === DetectionStatus::Searching ? $this->nextCheckAt($episode, $now) : null,
    //     $held,
    // );
}
```

```php
// App\Services\RecordingService — T-126's paste(), T-127's hide()/unhide(), T-128's
// notice call; this task adds the search and one promoted dependency.

use App\Data\RecordingSearch;
use Throwable;
// CarbonImmutable and EpisodeRecording are already imported by T-126 and T-127.

public function __construct(
    private LiveSessionService $sessions,        // T-127
    private SessionNoticeService $notices,       // T-128
    private ConnectionService $connections,      // this task (T-044's service)
) {}

/**
 * Look once for this Episode's recording (D-027): the sweep with
 * LiveSessionService::SWEEP_TIMEOUT_SECONDS, Check now (T-144) with its own
 * shorter constant. Runs in the current Group. The finder's Throwable
 * is reported, the attempt stamped, and nothing written; a row that came
 * back published queues recording_ready through T-128's ledger.
 */
public function search(Episode $episode, CarbonImmutable $now, int $timeoutSeconds): RecordingSearch
{
    $finder = $this->sessions->finderFor($episode);

    if ($finder === null) {
        return RecordingSearch::withoutCall(RecordingSearch::SKIPPED_NO_FINDER);
    }

    $connection = $this->sessions->searchableConnection($episode);

    if ($connection === null) {
        return RecordingSearch::withoutCall(RecordingSearch::SKIPPED_NO_CONNECTION);
    }

    try {
        $connection = $this->connections->fresh($connection, $timeoutSeconds);
        $found = $finder->find($episode, $connection, $timeoutSeconds);
    } catch (Throwable $exception) {
        report($exception);
        $stamped = $this->sessions->markChecked($episode, $now);

        return RecordingSearch::afterFailure($now, $this->sessions->nextCheckAt($stamped, $now));
    }

    $inserted = $this->sessions->attachFound($episode, $found, $now);
    $published = $inserted->filter(fn (EpisodeRecording $recording): bool => $recording->isVisible());

    foreach ($published as $recording) {
        $this->notices->queueRecordingReady($recording);     // T-128: a second part queues nothing for anyone already told
    }

    return new RecordingSearch(
        found: count($found),
        inserted: $inserted,
        published: $published->count(),
        held: $inserted->count() - $published->count(),
        checkedAt: $now,
        // refresh(), not fresh(): attachFound() stamped recording_checked_at on
        // its own locked copy, and refresh() reloads this instance and returns it.
        nextCheckAt: $this->sessions->nextCheckAt($episode->refresh(), $now),
    );
}
```

```php
// App\Services\SessionNoticeService::creatorNudgeCandidates() — T-129's query,
// two lines changed (D-028: at recording_wait_hours with detection; never for a held row):

//     ->filter(fn (Episode $episode): bool => in_array(
//         $this->live->creatorStateFor($episode, $now),                 // was stateFor(): Review is neither Waiting nor Overdue
//         [LiveState::Waiting, LiveState::Overdue],
//         true,
//     ))
//     ->reject(fn (Episode $episode): bool => $this->live->isSearching($episode, $now))   // Qori is still looking; the nudge waits
//     ->values();
```

```php
// App\Services\EpisodeService::touchSchedule() — T-124's private method, one line
// added inside the dirty branch, which T-124's Scope reserved for this task.
// The branch is T-124's, unchanged apart from the added line:
if ($locked->isDirty(['starts_at', 'ends_at'])) {
    $content['schedule_version'] = $locked->scheduleVersion() + 1;
    // A moved session is looked at on the next run, not at the cadence its old age earned (D-027).
    $locked->recording_checked_at = null;
}
```

```php
// App\Services\SeriesService::update() — one more arm before the save (:130-132),
// and the docblock's @param shape gains recording_publication?: string.
if (array_key_exists('recording_publication', $attributes)) {
    $changes['recording_publication'] = RecordingPublication::from((string) $attributes['recording_publication']);
}
```

```php
// App\Http\Requests\Share\UpdateSeriesRequest::rules() — one rule, `sometimes` like every other:
// What happens to a recording Qori finds (D-027). Absent means unchanged.
'recording_publication' => ['sometimes', Rule::enum(RecordingPublication::class)],
```

```php
// App\Http\Controllers\Share\SeriesController::show() — LiveSessionService $sessions
// arrives by method injection (T-127). $now = CarbonImmutable::now();
// $zone = $scope?->timezone() ?? Timezones::fallback(), the Group's, as T-123's
// startsAtLocal reads it.

// One page-level prop, read by SeriesForm.vue from usePage().props:
'recordingPublication' => [
    // A live connection on a provider with a finder: without one the setting does nothing and is not shown (D-021).
    'available' => $sessions->finderConnection() !== null,
    'value' => $series->recording_publication->value,
    'title' => __('series.recording_publication.title'),
    'intro' => $terminology->line('series.recording_publication.intro', [], $scope),
    'reviewFirst' => __('series.recording_publication.review_first'),
    'reviewFirstHelp' => $terminology->line('series.recording_publication.review_first_help', [], $scope),
    'automatic' => __('series.recording_publication.automatic'),
    'automaticHelp' => $terminology->line('series.recording_publication.automatic_help', [
        'tolerance' => (string) config('qori.live.match_tolerance_minutes'),
        'minimum' => (string) config('qori.live.min_recording_minutes'),
    ], $scope),
],

// Inside T-127's `live` key per live Episode:
'state' => $sessions->creatorStateFor($episode, $now)->value,        // was stateFor(); the one place review is produced for a page
'detection' => $this->detection($episode, $sessions, $now, $scope, $terminology),

// Per recording, beside T-126's and T-127's keys:
'isHeld' => $recording->isHeld(),
'heldLine' => $recording->isHeld()
    ? __('live.panel.review.held_line', [
        'started' => $recording->started_at->setTimezone($zone)->format('j M Y, g:ia T'),
        'minutes' => (string) $recording->duration_minutes,
    ])
    : null,

// T-126's sourceLine is unchanged except for one more replacement inside its
// __() call, so live.panel.recording.source.zoom can name the vendor:
'sourceLine' => __('live.panel.recording.source.'.$recording->source->value, [
    'date' => $recording->found_at->setTimezone($zone)->format('j M Y'),      // T-126's
    'provider' => $this->providerName($episode->provider->connection()),      // this task's
]),

/** T-141's name for the provider, under D-016's provider-choice exception; '' for a provider nobody connects. */
private function providerName(?ConnectionProvider $provider): string;
// return $provider === null ? '' : __('connections.providers.'.$provider->value.'.name');

/**
 * The detection block the panel renders, every sentence resolved here.
 *
 * @return ?array{status: string, line: string, checked: ?string, found: ?string, integrationsUrl: ?string, integrationsLabel: ?string}
 */
private function detection(Episode $episode, LiveSessionService $sessions, CarbonImmutable $now, ?Group $scope, Terminology $terminology): ?array;
// $detection = $sessions->detectionFor($episode, $now);
// if ($detection === null) return null;
//
// $zone = $scope?->timezone() ?? Timezones::fallback();
// $replace = ['provider' => $this->providerName($detection->provider), 'hours' => (string) config('qori.live.recording_wait_hours')];
// $at = fn (CarbonImmutable $instant): string => $instant->setTimezone($zone)->format('j M Y, g:ia T');   // T-124's whenFor() format
//
// return [
//     'status' => $detection->status->value,
//     'line' => $terminology->line('live.panel.detection.'.$detection->status->value, $replace, $scope),
//     'checked' => match (true) {
//         $detection->status !== DetectionStatus::Searching => null,
//         $detection->checkedAt === null => __('live.panel.detection.not_checked_yet'),
//         $detection->nextCheckAt === null => __('live.panel.detection.checked_last', ['time' => $at($detection->checkedAt), ...$replace]),
//         default => __('live.panel.detection.checked', ['time' => $at($detection->checkedAt), 'next' => $at($detection->nextCheckAt)]),
//     },
//     'found' => $detection->held > 0
//         ? $terminology->choice('live.panel.review.found', $detection->held, $replace, $scope)
//         : null,
//     'integrationsUrl' => $detection->status === DetectionStatus::NotConnected ? route('share.settings.integrations', $scope?->slug) : null,
//     'integrationsLabel' => $detection->status === DetectionStatus::NotConnected ? __('live.panel.detection.integrations') : null,
// ];
```

```php
namespace App\Console\Commands;

use App\Models\Group;
use App\Services\LiveSessionService;
use App\Services\RecordingService;
use App\Support\CurrentGroup;
use Carbon\CarbonImmutable;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;

/**
 * Look in each connected meeting account for the recordings of live
 * sessions that ended recently (D-027).
 *
 * A command, not a queued job, for the reason PurgeSeriesCommand gives: the
 * queue is `deferred` and cannot retry, so the retry is the next run and
 * the backoff is on the row. Iterates every Group inside
 * CurrentGroup::runFor(), so nothing here crosses the group scope, and the
 * connection read for each Group is that Group's own.
 */
class FindRecordingsCommand extends Command
{
    protected $signature = 'qori:recordings:find {--dry-run : List the sessions Qori would look at, call nothing}';

    protected $description = 'Look for the cloud recordings of live sessions that ended recently, and land them for review';

    public function handle(LiveSessionService $sessions, RecordingService $recordings, CurrentGroup $current): int;
    // $now = CarbonImmutable::now(); $dryRun = (bool) $this->option('dry-run');
    // $tally = ['groups' => 0, 'candidates' => 0, 'found' => 0, 'published' => 0, 'held' => 0, 'failed' => 0];
    //
    // foreach (Group::query()->cursor() as $group) {
    //     $current->runFor($group, function () use ($sessions, $recordings, $now, $dryRun, &$tally): void {
    //         $candidates = $sessions->sweepCandidates($now);
    //         if ($candidates->isEmpty()) return;
    //         $tally['groups']++;
    //
    //         foreach ($candidates as $episode) {
    //             $tally['candidates']++;
    //             // $this->line(), not lang: a diagnostic for whoever reads the scheduler's output (§23).
    //             $this->line(sprintf('%s %s (%s)', $dryRun ? 'Would check' : 'Checking', $episode->title, $episode->getKey()));
    //             if ($dryRun) continue;
    //
    //             $search = $recordings->search($episode, $now, LiveSessionService::SWEEP_TIMEOUT_SECONDS);
    //             $tally['found'] += $search->found;
    //             $tally['published'] += $search->published;
    //             $tally['held'] += $search->held;
    //             $tally['failed'] += $search->failed ? 1 : 0;
    //         }
    //     });
    // }
    //
    // Log::info('qori:recordings:find', [...$tally, 'dry_run' => $dryRun]);   // the heartbeat T-019 reads
    // $this->line(sprintf('%s %d, found %d, published %d, held %d, failed %d.', $dryRun ? 'Would check' : 'Checked', $tally['candidates'], ...));
    // return self::SUCCESS;
}
```

```php
// app/Providers/IntegrationServiceProvider.php — beside T-142's tag line:
$this->app->when(LiveSessionService::class)
    ->needs('$finders')
    ->giveTagged('recording-finders');
```

```php
// routes/console.php — beside T-128's line, under its comment; five minutes provisional (D-028).
Schedule::command('qori:recordings:find')
    ->everyFiveMinutes()
    ->withoutOverlapping()
    ->onOneServer();
```

```ts
// resources/js/components/series/SeriesForm.vue — read from the page's props,
// as LiveSessionPanel.vue reads recordingCopy (T-126), so the page is not edited.
import { usePage } from '@inertiajs/vue3';

interface RecordingPublicationCopy {
    available: boolean;
    value: 'review_first' | 'automatic';
    title: string;
    intro: string;
    reviewFirst: string;
    reviewFirstHelp: string;
    automatic: string;
    automaticHelp: string;
}

const recordingPublication = computed(
    () =>
        usePage().props.recordingPublication as RecordingPublicationCopy | null,
);
// Rendered before the Save button, only when recordingPublication?.available:
//   <fieldset id="series-recording-publication">
//     <legend>{{ title }}</legend>  <p>{{ intro }}</p>
//     <input type="radio" id="series-recording-review-first" name="recording_publication" value="review_first" :checked="value === 'review_first'" :disabled="props.disabled" />  label reviewFirst, help reviewFirstHelp
//     <input type="radio" id="series-recording-automatic"    name="recording_publication" value="automatic"    :checked="value === 'automatic'"    :disabled="props.disabled" />  label automatic, help automaticHelp
//     <InputError :message="errors.recording_publication" />
//   </fieldset>
// No inline English: every word is in the prop.
```

```ts
// resources/js/components/series/LiveSessionPanel.vue — additions to T-127's
interface RecordingDetectionCopy {
    status:
        | 'not_connected'
        | 'cloud_recording_off'
        | 'link_not_searchable'
        | 'will_search'
        | 'searching'
        | 'stopped';
    line: string;
    /** "Last checked … · next check …", or null outside `searching`. */
    checked: string | null;
    /** "Qori found a recording …", or null when nothing is held. */
    found: string | null;
    integrationsUrl: string | null;
    integrationsLabel: string | null;
}
// The row's `live` object gains `detection: RecordingDetectionCopy | null` and its
// `state` union gains 'review'; each CreatorRecording gains `isHeld: boolean` and
// `heldLine: string | null`.
//
// Renders, under the session time in every state where `detection` is set:
//   <p>{{ detection.line }}</p>
//   <p v-if="detection.checked" class="text-muted-foreground text-sm">{{ detection.checked }}</p>
//   <TextLink v-if="detection.integrationsUrl" :href="detection.integrationsUrl">{{ detection.integrationsLabel }}</TextLink>
// In state 'review': `detection.found` above the list, then T-127's `waiting` controls
// (the paste form labelled "Add the recording link", There's no recording for this session).
// In the list, a row with `isHeld` renders `heldLine` after T-126's part and source
// lines and neither Hide nor Show again — T-144 puts Publish and Reject there.
// Everything else is T-126's and T-127's.
```

`docs/flows/live-sessions.md` gains "Finding a recording": the chain
`qori:recordings:find → CurrentGroup::runFor() → LiveSessionService::sweepCandidates() → RecordingService::search() → ConnectionService::fresh() → FindsRecordings::find() → LiveSessionService::attachFound() → SessionNoticeService::queueRecordingReady()`,
the candidate rule with its five conditions, the backoff table, the hold
reasons in order, `creatorStateFor()` beside `stateFor()` with the sentence
that a Peer never sees `review`, the nudge's move to `recording_wait_hours`,
and the setting on the Series. `docs/flows/README.md`'s row for the file
adds "the sweep that finds a recording". `docs/tinker/live-sessions.md`
gains the recipe:

```php
$group = App\Models\Group::first();
$now = Carbon\CarbonImmutable::now();
$current = app(App\Support\CurrentGroup::class);

// Who the sweep would look at in this Group, and why one is left out.
$current->runFor($group, fn () => app(App\Services\LiveSessionService::class)->sweepCandidates($now)->pluck('title'));
$current->runFor($group, fn () => app(App\Services\LiveSessionService::class)->detectionFor($episode, $now));

// One search by hand, with the sweep's timeout; what it found and what it held.
$current->runFor($group, fn () => app(App\Services\RecordingService::class)
    ->search($episode, $now, App\Services\LiveSessionService::SWEEP_TIMEOUT_SECONDS));

// Let this Series publish clear finds itself.
$current->runFor($group, fn () => app(App\Services\SeriesService::class)->update($series, ['recording_publication' => 'automatic']));
```

```bash
php artisan qori:recordings:find --dry-run   # names each candidate, calls nothing
php artisan qori:recordings:find             # then qori:sessions:notify sends what an automatic Series published
```

## Copy

All lines with a noun go through `Terminology::line()` with the Group; the
rest carry none and are read with `__()`. The one exception is
`live.panel.review.found`, which carries no noun and still goes through
`Terminology::choice()`, because it is the only plural line here and
`choice()` is this app's pluralising reader. `:provider` is `T-141`'s
`connections.providers.<provider>.name` ("Zoom"), interpolated by the
controller; no line below names a vendor itself. `:hours` is
`config('qori.live.recording_wait_hours')`, `:tolerance`
`match_tolerance_minutes`, `:minimum` `min_recording_minutes`, `:count` the
held rows, `:time`, `:next` and `:started` instants in the Group's zone,
`:minutes` a recording's length. No line under `live.*` says "live now",
"has ended", "on its way" or "processing" (`D-026`), and no article stands
directly before a placeholder
(`TerminologyTest::test_no_lang_line_puts_an_article_before_a_noun`).

| Key                                              | File                 | English                                                                                                                                                                                                                                                   |
| ------------------------------------------------ | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `live.panel.detection.not_connected`             | `lang/en/live.php`   | Connect :provider on the Integrations page and Qori looks for this session's recording for you.                                                                                                                                                           |
| `live.panel.detection.integrations`              | `lang/en/live.php`   | Open Integrations                                                                                                                                                                                                                                         |
| `live.panel.detection.cloud_recording_off`       | `lang/en/live.php`   | Cloud recording is off for your :provider account, so Qori can't find this session's recording. Turn it on and connect :provider again, or add the recording's link yourself.                                                                             |
| `live.panel.detection.link_not_searchable`       | `lang/en/live.php`   | Qori can't look for recordings of this join link. Add the recording's link when it's ready.                                                                                                                                                               |
| `live.panel.detection.will_search`               | `lang/en/live.php`   | After the session, Qori looks in your :provider cloud for the recording.                                                                                                                                                                                  |
| `live.panel.detection.searching`                 | `lang/en/live.php`   | Looking in your :provider cloud for the recording.                                                                                                                                                                                                        |
| `live.panel.detection.not_checked_yet`           | `lang/en/live.php`   | Not checked yet.                                                                                                                                                                                                                                          |
| `live.panel.detection.checked`                   | `lang/en/live.php`   | Last checked :time · next check :next                                                                                                                                                                                                                     |
| `live.panel.detection.checked_last`              | `lang/en/live.php`   | Last checked :time. Qori stops looking :hours hours after the scheduled end.                                                                                                                                                                              |
| `live.panel.detection.stopped`                   | `lang/en/live.php`   | Qori stopped looking in your :provider cloud :hours hours after the scheduled end.                                                                                                                                                                        |
| `live.panel.review.found`                        | `lang/en/live.php`   | {1} Qori found a recording and is holding it for you to check.\|[2,*] Qori found :count recordings and is holding them for you to check.                                                                                                                  |
| `live.panel.review.held_line`                    | `lang/en/live.php`   | Held for you to check · started :started · :minutes minutes                                                                                                                                                                                               |
| `live.panel.recording.source.zoom`               | `lang/en/live.php`   | Found in your :provider cloud on :date                                                                                                                                                                                                                    |
| `series.recording_publication.title`             | `lang/en/series.php` | When Qori finds a recording                                                                                                                                                                                                                               |
| `series.recording_publication.intro`             | `lang/en/series.php` | For every live :episode in this :series whose recording Qori looks for.                                                                                                                                                                                   |
| `series.recording_publication.review_first`      | `lang/en/series.php` | Hold it for me to check first                                                                                                                                                                                                                             |
| `series.recording_publication.review_first_help` | `lang/en/series.php` | Nothing is shown to your :peer_plural or emailed until you've checked it.                                                                                                                                                                                 |
| `series.recording_publication.automatic`         | `lang/en/series.php` | Publish it straight away                                                                                                                                                                                                                                  |
| `series.recording_publication.automatic_help`    | `lang/en/series.php` | Your :peer_plural see it and get one email as soon as it's found. It's still held for you when the match is unclear: more than one recording, one that started more than :tolerance minutes from the scheduled start, or one under :minimum minutes long. |

`stopped` says what Qori did rather than what it did not find, because an
overdue session may still be holding a row the creator has not looked at, and
`detection.found` sits beside it.

`live.panel.detection.checked_last` is reached only when
`qori.live.check_backoff`'s last step ends before `recording_wait_hours`;
with today's config both are 48, so it never renders — it is kept because the
two keys are independent and a shortened backoff must not leave "next check"
blank with no sentence.

`live.panel.recording.source.zoom` is the key `T-126` left for this task
("keyed by source"); its `:date` is the find in the Group's zone, as
`source.link`'s is. The Series PATCH's flash is `series.updated`
(`lang/en/series.php:27`), reused. Nothing is added to `errors.php`: an
unknown `recording_publication` value is the framework's field error, and
the sweep's refusals are logged, not shown.

## Routes

None new. The existing route is widened by what its Form Request accepts:

| Verb  | Path                           | Name                  | Action                           |
| ----- | ------------------------------ | --------------------- | -------------------------------- |
| PATCH | `/g/{group}/series/{seriesId}` | `share.series.update` | `Share\SeriesController::update` |

`qori:recordings:find` is a console command and `routes/console.php`
schedules it. No Peer route: a Peer reads `waiting` while a row is held,
through `T-125`'s page and `T-126`'s Watch, both unchanged.

## Tests

The finder double, bound in every `setUp` below:

```php
namespace Tests\Doubles;

/**
 * A FindsRecordings that answers from memory and remembers what it was
 * asked. What ZoomRecordings does with a payload is T-142's suite; what
 * Qori does with what comes back is these.
 */
final class FindsRecordingsInMemory implements FindsRecordings
{
    /** @var list<SessionRecording> */
    public array $returns = [];

    /** @var list<array{episode: string, timeout: int}> */
    public array $calls = [];

    /** Thrown once, then cleared, so a command test can make one call of several fail. */
    public ?Throwable $throws = null;

    public function provider(): EpisodeProvider;                 // EpisodeProvider::Zoom
    public function handles(string $joinUrl): bool;             // str_contains($joinUrl, 'zoom.us/j/')
    public function find(Episode $episode, Connection $connection, int $timeoutSeconds): array;   // records the call; when $throws is set, nulls it and throws it; else $returns
    public function openUrl(SessionRecording $recording): string;   // $recording->url
    public function cloudRecording(Connection $connection, int $timeoutSeconds): ?bool;   // true
}

// setUp():
// $this->finder = new FindsRecordingsInMemory;
// $this->app->when(LiveSessionService::class)->needs('$finders')->give(fn (): array => [$this->finder]);
// Http::preventStrayRequests();
```

**New: `tests/Feature/Series/FindRecordingsTest.php` — 18 cases**
(`RefreshDatabase`; `Notification::fake()`; a `scene()` helper as
`tests/Feature/Series/LiveSessionTest.php:41-60` with `timezone`
`Australia/Brisbane` and a published Series;
`liveEpisode(Series $series, CarbonImmutable $startsAt, int $lengthMinutes = 90, array $content = []): Episode`
through `$series->episodes()->create([...])` with `provider` Zoom,
`starts_at`, `ends_at`, content
`['join_url' => 'https://zoom.us/j/91827405566', 'records' => true, ...$content]`;
`zoomConnection(Group $group, ?bool $cloudRecording = true): Connection`
through `Connection::factory()->zoom($cloudRecording)->create(['group_id' => …])`
inside `CurrentGroup::runFor()`;
`found(string $ref, CarbonImmutable $startedAt, int $minutes): SessionRecording`
with url `https://zoom.us/rec/share/{$ref}`, passcode `pw-{$ref}`,
`availableUntil` `2026-12-02`, `isVideo` true; a fixed
`$now = CarbonImmutable::parse('2026-10-03T14:00:00Z')` and a session at
`2026-10-03T10:00:00Z` for 90 minutes; every service call inside
`CurrentGroup::runFor($group, …)`; `$this->service()` is
`app(LiveSessionService::class)` and `$this->recordings()` is
`app(RecordingService::class)`)

1. `test_a_waiting_zoom_session_with_a_searchable_link_is_a_candidate` — the
   session above, a Zoom connection; `sweepCandidates($now)` holds that one
   Episode and nothing else.
2. `test_a_session_that_is_not_waiting_is_never_a_candidate` — seven
   Episodes: starting tomorrow, ended five minutes before `$now`, with a
   pasted recording (`RecordingService::paste()`), `cancelled_at` set,
   `not_recorded_at` set, `records` false, ended 49 hours before `$now`;
   `sweepCandidates($now)` is empty; the session from case 1 added makes it
   one.
3. `test_a_group_without_a_live_connection_that_keeps_cloud_recordings_is_skipped`
   — no connection: empty; `Connection::factory()->zoom()->revoked()`:
   empty; `zoom(false)`: empty; `zoom(null)`: one (unread is still tried);
   `zoom(true)`: one. In every case `$this->finder->calls` stays empty.
4. `test_a_link_no_finder_handles_and_a_provider_without_a_finder_are_skipped`
   — `join_url` `https://zoom.us/my/wayne`: empty; content without a
   `join_url`: empty; a `Link` Episode with a Meet link and a `Teams`
   Episode: empty.
5. `test_it_looks_again_by_the_backoff_table_and_reads_it_from_config` —
   `recording_checked_at` null: due; ended 1 hour before `$now`, checked
   14 minutes before: not due, 15: due; ended 10 hours before, checked 59
   minutes before: not due, 60: due; ended 30 hours before, checked 239
   minutes before: not due, 240: due; `nextCheckAt()` equals the check plus
   the step in each; `config()->set('qori.live.check_backoff', [['until_hours' => 48, 'every_minutes' => 5]])`
   makes a check 5 minutes old due.
6. `test_a_found_recording_lands_held_for_review_by_default` — the finder
   returns `found('uuid-1', 10:02, 88)`; `search($episode, $now, 30)` has
   `found` 1, `held` 1, `published` 0, `failed` false; one row: `source`
   `zoom`, `vendor_ref` `uuid-1`, the url and passcode, `started_at` 10:02,
   `duration_minutes` 88, `available_until` `2026-12-02`, `found_at` `$now`,
   `published_at` null, `hidden_at` null, `needs_review` true, `position` 1,
   `group_id` the Group's; `isHeld()` true; `recording_checked_at` is `$now`;
   `$this->finder->calls[0]['timeout']` is 30; no `session_notices` row;
   `Notification::assertNothingSent()` (owner acceptance 6).
7. `test_the_creator_reads_review_and_the_peer_reads_waiting` — after case
   6: `creatorStateFor()` is `Review`, `stateFor()` is `Waiting`; the
   Peer's page (`shared.show`) has `series.episodes.0.live.state` `waiting`
   and `live.recordings` empty; Watch on the held row's id answers 404
   (`T-126`'s gate; owner acceptance 5).
8. `test_an_automatic_series_publishes_a_clear_find_and_queues_the_email` —
   `SeriesService::update($series, ['recording_publication' => 'automatic'])`;
   a Peer granted before; the same single find; `published` 1; the row has
   `published_at` `$now` and `needs_review` false; one `session_notices` row,
   `kind` `recording_ready`, `recording_id` the row, `user_id` the Peer;
   `stateFor()` is `Ready`; the Peer's page offers `Watch recording` (owner
   acceptance 6).
9. `test_two_instances_in_the_window_are_both_held_even_on_automatic` —
   automatic; `found('uuid-1', 10:01, 40)` and `found('uuid-2', 10:50, 45)`
   returned in reverse order; both rows held, positions 1 and 2 by start,
   `held` 2; no notice (owner acceptance 8).
10. `test_a_start_far_from_the_schedule_or_a_short_recording_is_held_on_automatic`
    — automatic; `found('uuid-1', 08:00, 60)`: held; on a second Episode
    `found('uuid-2', 10:00, 3)`: held; `config()->set('qori.live.match_tolerance_minutes', 180)`
    and the first find again on a third Episode: published — the number is
    read, not restated (owner acceptance 8: the early test recording).
11. `test_the_same_instance_is_never_inserted_twice` — `search()` twice with
    `uuid-1`: one row, `found` 1 and `inserted` empty the second time; set
    `hidden_at` on it (`T-144`'s reject writes the same column) and search
    again: still one row, still hidden (owner acceptance 7).
12. `test_a_later_part_becomes_part_two_and_sends_nothing_new` — automatic,
    a Peer; first search `uuid-1` alone: published, one notice row; second
    search returns `uuid-1` and `uuid-2`: one new row, `position` 2, held
    (`HELD_SEVERAL`); still one notice row; `qori:sessions:notify` sends
    once (owner acceptance 7 and 8).
13. `test_a_group_over_its_cap_holds_instead_of_publishing` — a Group taken
    over its cap and downgraded as
    `tests/Feature/Series/OverCapLockTest.php:59-71` does (that helper is
    private to its own class; copy the three lines), with an automatic Series
    and a clear find: held; no notice.
14. `test_a_vendor_failure_is_reported_stamped_and_writes_nothing` —
    `Exceptions::fake()`; `$this->finder->throws = AppException::upstreamUnavailable('errors.playback.provider_unavailable')`;
    `search()` has `failed` true; `Exceptions::assertReported(AppException::class)`;
    `recording_checked_at` is `$now`; no row; `nextCheckAt()` is `$now` plus
    15 minutes.
15. `test_the_connection_is_refreshed_before_the_finder_runs` —
    `$this->mock(ConnectionService::class)` expecting `fresh()` once with the
    Group's connection and `30`, returning it; the finder is then called
    once with that Episode.
16. `test_a_reschedule_clears_the_last_check` — `recording_checked_at` set;
    `EpisodeService::update($series, $id, ['starts_at' => …])` moves the
    session: null; a title-only update leaves it set.
17. `test_the_creator_page_shows_review_the_held_row_and_the_check_times` —
    after case 6, the owner's `share.series.show`: `series.episodes.0.live.state`
    is `review`; `detection.status` `searching`; `detection.line` contains
    `Zoom`; `detection.checked` contains `4 Oct 2026, 12:00am AEST` (the
    check at `$now`, in Brisbane) and `12:15am` (the next: the session
    ended two and a half hours before, so the step is 15 minutes);
    `detection.found` is the one-recording line;
    `live.recordings.0.isHeld` true, `.heldLine` contains `88`, `.sourceLine`
    contains `Zoom` and `4 Oct 2026` (`found_at` is `$now`, which is
    4 October in Brisbane), `.isVisible` false;
    `recordingPublication.available` true and `.value` `review_first`.
18. `test_the_detection_line_says_why_qori_cannot_look_and_nothing_where_it_does_not_apply`
    — no connection: `detection.status` `not_connected` with
    `integrationsUrl` `route('share.settings.integrations', $group->slug)`;
    `zoom(false)`: `cloud_recording_off`; a `/my/` link: `link_not_searchable`;
    a session tomorrow: `will_search`; ended 49 hours ago: `stopped` with
    `48` in the line; a Teams Episode, a ready Episode and a cancelled one:
    `detection` null.

**New: `tests/Feature/Console/FindRecordingsCommandTest.php` — 6 cases**
(the same helpers; `CarbonImmutable::setTestNow('2026-10-03T14:00:00Z')`)

1. `test_it_searches_every_groups_candidates_inside_that_groups_context` —
   two Groups, each with a Zoom connection and a waiting Episode; the finder
   returns one instance; `artisan('qori:recordings:find')` exits 0; two
   rows, each carrying its own Group's `group_id`; `$this->finder->calls`
   names each Episode once; a third Group with a waiting Episode and no
   connection gets no call and no row (wrong tenant: Group A's connection
   never serves Group C).
2. `test_dry_run_lists_candidates_and_calls_nothing` — `--dry-run` output
   contains the Episode's title; `calls` empty; `recording_checked_at` null;
   no row.
3. `test_it_logs_a_heartbeat_each_run` — `Log::spy()`; a run with nothing
   due: `info` once with `'qori:recordings:find'` and a context carrying
   `groups`, `candidates`, `found`, `published`, `held`, `failed`,
   `dry_run`.
4. `test_one_failing_episode_does_not_stop_the_run` — two candidates in one
   Group; the finder throws on the first call only (the double clears
   `throws` after throwing); exit 0; the second Episode has its row; the
   heartbeat's `failed` is 1.
5. `test_it_is_scheduled_every_five_minutes_without_overlap_on_one_server` —
   the event in `app(Schedule::class)->events()` whose `command` contains
   `qori:recordings:find` has `expression` `*/5 * * * *`,
   `withoutOverlapping` true and `onOneServer` true, as
   `T-128`'s case reads them.
6. `test_a_clear_find_on_an_automatic_series_reaches_the_peer_once` — an
   automatic Series, a Peer; `qori:recordings:find` then
   `qori:sessions:notify`: `Notification::assertSentToTimes($peer, RecordingReadyNotification::class, 1)`;
   both again: still 1 (owner acceptance 6 and 7).

**New: `tests/Feature/Series/RecordingPublicationTest.php` — 6 cases**
(`scene()` and `patch_()` as `tests/Feature/Series/EditSeriesTest.php:38-72`)

1. `test_a_series_holds_found_recordings_for_review_by_default` — a fresh
   Series' `recording_publication` is `ReviewFirst` and
   `publishesRecordingsAutomatically()` is false; a Series made through
   `SeriesService::create()` too.
2. `test_the_owner_switches_a_series_to_automatic_and_back` — PATCH
   `recording_publication` `automatic`: saved, the toast is
   `series.updated` with the title; PATCH `review_first`: saved.
3. `test_an_unknown_value_is_refused` — PATCH `recording_publication`
   `whenever`: `assertSessionHasErrors('recording_publication')`; the
   column is unchanged.
4. `test_a_patch_without_the_field_leaves_it_alone` — title only after
   case 2's switch: still `automatic`.
5. `test_the_setting_is_offered_only_when_a_live_connection_with_a_finder_exists`
   — `recordingPublication.available` false with no connection, true with
   `Connection::factory()->zoom()`, false with `->zoom()->revoked()`;
   `value` follows the column.
6. `test_the_setting_speaks_the_groups_vocabulary` — a `pro` Group (its plan
   carries `custom_vocabulary`, `config/qori.php`) with the labels
   `tests/Feature/TerminologyTest.php:36-45` holds:
   `recordingPublication.automaticHelp` and `.reviewFirstHelp` contain
   `Ruffies` and not `Peers`; `.intro` contains `Trail`; `.automaticHelp`
   contains `30` and `5`.

**Changed:**

- `tests/Feature/Mail/RecordingNeededTest.php` (`T-129`'s) — 2 cases added:
  `test_a_session_qori_is_looking_for_waits_for_the_full_recording_wait` —
  a Zoom connection and a searchable link, ended 13 hours before `$now`:
  not a candidate; ended 49 hours before: a candidate; a `Link` Episode
  ended 13 hours before: a candidate as today; and
  `test_a_session_with_a_held_recording_is_not_nudged` — a held row
  (written as case 6 above writes one): not a candidate at 13 hours, nor at 49. Its nine existing cases run unchanged: none of them creates a
  connection, so `isSearching()` is false throughout.
- `tests/Feature/Series/RecordingStateTest.php` (`T-127`'s) — unchanged;
  its `stateFor()` assertions hold because this task adds no arm there.
- `tests/Feature/Admin/ConsoleAccessTest.php` — unchanged; no
  `acrossAllGroups()` caller is added, so its allow-list
  (`tests/Feature/Admin/ConsoleAccessTest.php:131-152`) keeps its entries.

Total: 30 new cases, 2 added to an existing file.

## Acceptance

- [ ] A live Zoom Episode with a searchable join link, in a Group whose
      connected Zoom account keeps cloud recordings, is looked at by
      `qori:recordings:find` once Join has closed, again at the backoff
      cadence from `config('qori.live.check_backoff')`, and not after
      `recording_wait_hours`; the creator's panel says Qori is looking,
      when it last checked and when it checks next, with the vendor's name
      from `T-141`'s line and none in `lang/en/live.php`
- [ ] A found recording lands held for review on every Series by default;
      only a Series switched on its details form to "Publish it straight
      away" publishes, and then every Peer who had access gets one email
      through `qori:sessions:notify`; nothing is emailed for a held row
      (owner acceptance 6)
- [ ] Two instances in the window, a start more than
      `match_tolerance_minutes` from the schedule, a recording under
      `min_recording_minutes`, and a Group over its Series cap are held
      whatever the setting; the same instance is never inserted twice, a
      hidden or rejected row is never re-found, and a later part sends
      nothing to anybody already told (owner acceptance 7 and 8)
- [ ] While a row is held the Peer's card reads `waiting`, offers no Watch,
      and Watch on the held row's id is not found; the public page is
      unchanged (owner acceptance 5 and 11)
- [ ] A missing, revoked or cloud-recording-off connection and a link no
      finder handles each earn one honest line on the panel and no vendor
      call; a vendor failure is reported, stamps the attempt and leaves the
      run to finish the other Episodes (owner acceptance 9: local-only
      recording, no recording and disconnected Zoom each show a truthful
      status)
- [ ] The creator nudge waits for `recording_wait_hours` on a session Qori
      is looking for, goes at `creator_nudge_hours` on one it is not, and
      never goes for a session with a held row
- [ ] Moving a session clears its last check; `--dry-run` names each
      candidate and calls nothing; every run logs one heartbeat; the
      command is scheduled every five minutes without overlap on one server;
      no `acrossAllGroups()` caller and no `ShouldQueue` is added
- [ ] Against `T-141`'s development app on Qori's own Zoom account, one
      meeting recorded to the cloud is found by the plain run and lands
      held on its Episode, recorded in the report with the `--dry-run` and
      plain output
- [ ] `docs/flows/live-sessions.md` describes the sweep, the hold, the
      publication rule and the nudge's move; the `docs/tinker/live-sessions.md`
      recipe runs as written
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- `T-142` `ready`, so `FindsRecordings`, the `recording-finders` tag and
  `SessionRecording`'s properties (`vendorRef`, `url`, `passcode`,
  `startedAt`, `durationMinutes`, `availableUntil`, `isVideo`) are frozen —
  the storage owner's. With it, one answer this draft assumes: that
  `handles()` returns false for a personal-room or vanity link, because
  `ZoomMeetingLink::meetingId()` returns null for them, so `D-027`'s fourth
  hold reason is applied by never looking; if a personal-room id parses like
  any other, `T-142` needs a way to say so (a flag on `SessionRecording`, or
  `handles()` reading the id's shape) and this task's `holdReason()` gains an
  arm — the spike's (`T-122` question 6).
- The schedule interval: five minutes is provisional, chosen by the owner
  with `T-128`'s and `T-091`'s against Laravel Cloud's sleep timeout
  (`D-028`, `release-prerequisites.md:27`) — the owner's.
- Whether a held recording earns the creator an email of its own — a new
  `SessionNoticeKind`, say `recording_review_needed`, through `T-128`'s
  ledger — or the panel's `review` state alone, which is all this draft
  builds; without one, a creator who does not open the Series page is not
  told that Qori found something — the owner's.
- `T-044` `ready`, so `ConnectionService::fresh(Connection, int)` and
  `Connection::isLive()` are frozen names — the storage owner's.
- `T-129` `ready`, so `creatorNudgeCandidates()`'s query and its `filter()`
  are the lines this task edits — anyone's.
- The sweep's floor: Join closing (`join_closes_after_minutes`, 15, through
  `stateFor()`), as this draft says, or the brief's ten minutes as a class
  constant — anyone's.
- `T-127`'s "the creator-only `review` arm is `T-143`'s and sits between 4
  and 5 when it lands" against this draft's `creatorStateFor()`; confirm
  the stream owner prefers the Peer's files untouched to an arm in
  `stateFor()` — the classroom owner's.

## Re-scope log

None.

## Notes

Written on 18 September 2026 from `D-027`, `D-026` and `D-028`, for the
sprint after the manual-replay checkpoint (`D-031`). The merged sprint
reference is `docs/planning/course-classroom.md`; the owner's acceptance
scenarios this task answers are 5, 6, 7, 8, 9 and 11.

Edits to other drafts this spec implies:

- `T-127`'s draft is edited where its `stateFor()` docblock and Notes say
  "`T-143`'s creator-only `review` arm lands later, after ready": the `review`
  state is produced by `LiveSessionService::creatorStateFor()`, which
  `SeriesController::show()` calls in place of `stateFor()`; `stateFor()`
  keeps its seven arms and never answers `Review`, so
  `SharedController::liveCard()` and `LiveSessionCard.vue` need no change for
  it.
- `T-125`'s draft is edited where its `stateFor()` pseudocode carries the
  comment "`T-126` inserts Ready here; `T-143` inserts Review here": only
  `T-126`'s arm lands there.
- `T-144`'s draft loses its `EpisodeRecording::isHeld()` row, which this task
  declares, and its open question about `isHeld()` versus a `scopeHeld()` is
  answered here — `isHeld()` plus `Episode::heldRecordings()`, no scope. Its
  `isRejected()` stays its own, and its `reject()` must clear `needs_review`
  for the two readings of a held row to agree.
- `T-129`'s draft is edited to: `creatorNudgeCandidates()` filters through
  `creatorStateFor()` and rejects an Episode `isSearching()`, which is the
  "hold for an Episode Qori is looking for" its Notes reserved for this
  task.
- `T-126`'s draft is edited to: `SeriesController::show()`'s `sourceLine`
  passes `provider` beside `date`, so `live.panel.recording.source.zoom` can
  name the vendor through `T-141`'s line.
- `T-124`'s draft already reserves the `recording_checked_at` clear in
  `touchSchedule()` for this task; nothing there changes.
- `T-144`'s draft declares `LiveSessionService::checkNow()`, `canCheck()` and
  `App\Data\RecordingCheck`, and calls the finder itself. This task proposes
  it call
  `RecordingService::search($episode, CarbonImmutable::now(), LiveSessionService::CHECK_NOW_TIMEOUT_SECONDS)`
  instead, after its `recheck_seconds` throttle, so the sweep and the button
  cannot disagree about what a find does and only one place queues
  `recording_ready`; `RecordingCheck` then reads a `RecordingSearch` or is
  dropped for it. Taking that is `T-144`'s call, and its
  `CHECK_NOW_TIMEOUT_SECONDS` stays its own either way. `publish()` sets
  `published_at`, clears `needs_review` and calls `queueRecordingReady()`;
  `reject()` sets `hidden_at`, clears `needs_review` and keeps the row, which
  `attachFound()`'s `vendor_ref` filter then never re-inserts; the panel's
  held rows already carry `isHeld` and `heldLine`, and Publish and Reject go
  beside them. `T-141`'s Notes ask that Check now also re-read the
  connection's recording settings; that is `T-144`'s to take or decline.

Between this task and `T-144` a held recording is listed on the creator's
panel and cannot be published from it; the paste form and "There's no
recording for this session" (`T-127`) remain the creator's way out, and the
Peer reads `waiting` throughout. The stream orders `T-144` next and nothing
between them ships to a real creator.

The brief's candidate window starts ten minutes after the end; this draft
uses Join closing (`join_closes_after_minutes`, 15) through `stateFor()`,
so the sweep looks only at a session that is `waiting` and no second
constant is declared. Listed above as an open point.

`RecordingSource` has `Zoom` and `Link` (`T-126`); a second finder for
another provider adds a case there and an arm in `sourceFor()`, and nothing
else in this task names a vendor.

`SeriesService::update()`'s docblock lists the keys `update()` reads; the
`@param` shape gains `recording_publication?: string`, and the request's
enum rule is what makes the `from()` in the service safe.

`ArchitectureTest::test_services_make_no_vendor_http_calls` stays green:
the only `Http::` on this path is inside `T-141`'s `ZoomClient`, reached
through the contract. `test_integrations_import_no_app_layer` is `T-142`'s
concern: `FindsRecordings::find()` takes an `Episode` and a `Connection`
(Models), which the contract already allows.

`docs/flows/README.md:42-43` (the Zoom/Teams integration has no flow file)
is rewritten by `T-125` when `live-sessions.md` is created and kept true by
`T-141` for connecting; this task adds the sweep to that file and touches
the README's row only.

`T-127`'s report (26 September 2026): a Peer's Watch label counts every row
on the Episode, hidden ones too, so hiding Part 1 leaves "Watch part 2"
(`SharedController::liveCardInGroup()`), and `RecordingService::paste()`
numbers after the highest `position`. Both count a row this task holds for
review (`published_at` null) as well, so once held rows exist a Peer could
read "Watch part 2" with no Part 1 ever offered. Decide whether a held row
takes a position before it is published, or the label counts published rows
only.
