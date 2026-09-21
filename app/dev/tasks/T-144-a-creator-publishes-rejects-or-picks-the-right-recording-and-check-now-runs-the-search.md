---
id: T-144
title: A creator publishes, rejects or picks the right recording, and Check now runs the search at once
stream: classroom
status: draft
owner: unassigned
estimate: M
depends: T-143
blocks: none
---

# T-144 — A creator publishes, rejects or picks the right recording, and Check now runs the search at once

> **Draft.** Not specified to the last name yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). Written on 18 September 2026 from `D-027`
> and `D-021`, on top of `T-126`'s recordings, `T-127`'s review controls,
> `T-128`'s ledger and `T-143`'s sweep, the last of which is still a draft;
> what has to be reconciled with its finished spec is listed at the bottom.

## Why

After `T-143`, a recording Qori finds lands in `episode_recordings` with
`published_at` null: on `review_first`, every find; on `automatic`, every
ambiguous one — two instances in the window, a start further than
`qori.live.match_tolerance_minutes` from `starts_at`, a duration under
`qori.live.min_recording_minutes`, or a personal or vanity link (`D-027`). The
creator's panel shows `review` with `T-143`'s "last checked" line and nothing
to act on. There is no way to publish the held row, no way to say it is the
wrong one, and no way to make Qori look again before the backoff's next step
(`qori.live.check_backoff`: every 15 minutes for three hours, then hourly,
then every four hours). A creator who has just watched their meeting app
finish processing waits up to four hours for a sweep, and every Peer reads
`waiting` the whole time. `D-021` rule 2 says a wait a person can end has a
button, throttled, and that a throttled press says when the next one is
allowed instead of failing.

Afterwards the panel lists every held recording with when it started and how
long it ran, and offers **Publish** and **Not this one** on each. Publish
makes the row what a Peer sees and queues the `recording_ready` email
`T-128` sends; Not this one keeps the row, hidden and never published, so the
same instance is never attached twice (`D-027`), and publishing it later is
the undo. When several are held — a rehearsal and the class, a restarted
meeting, two segments — the creator publishes the right ones and rejects the
rest, and nothing is attached silently (owner acceptance 8). **Check now**
runs `T-143`'s `RecordingService::search()` for that one Episode at once with
`LiveSessionService::CHECK_NOW_TIMEOUT_SECONDS`, the five seconds a creator
waiting on a click is worth, so review-first, the ambiguity hold and the
`recording_ready` queue apply exactly as in the sweep, and ends on the page
with the outcome: found and published, found and held, nothing new, the
vendor could not be reached, or "checked just now — try again in :seconds
seconds" when the last check, by anyone, was within
`qori.live.recheck_seconds`.

## Decisions taken to make this specifiable

**Publish and Not this one act on the row, through `T-126`'s
`RecordingController` and `RecordingService`, taking the Series and ids as
`T-127`'s `hide()` does, plus `User $by` for the log line.** `T-126`'s Notes
named `publish(EpisodeRecording $recording, User $by)`; `T-127` then settled
that a recording action takes `(Series $series, string $episodeId, string $recordingId)`
and resolves the row through `recordingOf()` inside `liveEpisodeOf()`, so
another Group's ids are not found rather than forbidden
(`app/Concerns/ResolvesShareSeries.php:36-39`). This task follows `T-127`'s
shape and keeps `$by`, which reaches the log line only — `D-027` has no
column for who reviewed.

**A rejected recording is a hidden, never-published row: `hidden_at` set,
`published_at` null, `needs_review` false.** No `rejected_at` column and no
new state. `D-027` already says hiding keeps the row so a sweep never finds
it twice, and the partial unique `(episode_id, vendor_ref)` is what makes
that true; a rejection is the same fact before publication.
`EpisodeRecording::isRejected()` names the case beside `T-126`'s `isVisible()`
and `T-143`'s `isHeld()`, and is the only accessor this task adds.

**Publishing a rejected row is the undo.** `publish()` clears `hidden_at`.
A creator who pressed Not this one on the right recording has one control to
press next, and nothing new to learn; no un-reject route exists.

**Not this one refuses a published row; Hide is that row's control.**
`errors.live.already_published`, resolution "Hide it instead". A published row
has been announced (`T-128`), and `T-127`'s Hide is the action whose meaning
Peers and the ledger already have; the panel offers exactly one of the two
per row, so only a stale page reaches the refusal.

**Publish is idempotent, and a second press queues nothing.** `publish()`
returns a published row as it is; `T-128`'s `queueRecordingReady()` is one
`insertOrIgnore()` under the ledger's unique key, so even a race between two
presses cannot double a row (owner acceptance 7).

**Publishing one held row leaves the others held.** Several segments are
Part 1 and Part 2 (`D-027`); a rehearsal beside the class is one to publish
and one to reject. Each held row is answered by the creator, and `review`
persists until none is left.

**Check now is `RecordingService::checkNow()`, a throttle in front of
`T-143`'s `RecordingService::search()`.** `T-143` put the orchestration that
has to queue an email on `RecordingService` for a container reason:
`SessionNoticeService` takes a `LiveSessionService`, so a `LiveSessionService`
that took `SessionNoticeService` back would be a cycle. Check now is the same
orchestration with a shorter timeout, so it is the same method with a
throttle in front — the sweep and the button cannot disagree about what a
find does, and this task adds no second rule about publishing, holding or
notifying.

**A Check now claims the Episode under the row lock before it calls the
vendor, and calls the vendor after the lock is released.** `T-143`'s
`episodes.recording_checked_at` is the throttle:
`LiveSessionService::claimCheck()` runs `T-124`'s `withLockedContent()`,
re-reads the column inside the lock, and either writes `$now` and answers
`null` or leaves the row untouched and answers the instant that blocks the
press. So a double press, or a press beside the sweep, cannot both call the
vendor, and a five-second vendor call never holds a row lock. A press within
`config('qori.live.recheck_seconds')` of the last check — the sweep's
included — is told "checked just now" with the seconds left, which is
`D-021` rule 2 exactly. `search()` stamps the same column again with the same
`$now` through `markChecked()` or `attachFound()`; writing one instant twice
is cheaper than a second code path.

**The throttle is the row's column, not `RateLimiter`.** One fact, shared
with the sweep: a creator who presses a minute after a sweep is told the
truth about when Qori last looked, and there is no cache key to expire
separately. `Reachability` and the existing `throttle:` middleware
(`routes/settings.php:73`) guard routes by request rate, which is a different
question.

**The finder runs with `LiveSessionService::CHECK_NOW_TIMEOUT_SECONDS = 5`,
this task's constant beside `T-143`'s `SWEEP_TIMEOUT_SECONDS = 30`.** A
person is waiting on this call and nobody is waiting on the sweep, so the two
numbers belong to the two tasks that have the reason for them;
`search(Episode, CarbonImmutable, int $timeoutSeconds)` takes the number as a
parameter rather than choosing it, which is the seam `T-143` left.

**Check now's outcome is `T-143`'s `App\Data\RecordingSearch`, widened by one
skip reason.** `search()` already answers found, inserted, published, held,
`checkedAt`, `nextCheckAt`, `failed` and `skipped`; the only fact it has no
word for is "you pressed too soon". So this task adds
`RecordingSearch::SKIPPED_TOO_SOON`, the `tooSoon()` named constructor and
`secondsToWait()`, rather than a second outcome shape for one action. On such
a press `nextCheckAt` carries the instant the next press is honoured rather
than the sweep's next step: the field answers one question — when is it
worth looking again — and both callers read it that way.

**On `automatic` an unambiguous find is published without a second press
(owner acceptance 6), and two instances in the window are held even then
(owner acceptance 8).** Both are `attachFound()`'s rules, reached through
`search()`; the `recording_ready` rows for what it published are queued by
`search()` too. This task states the behaviour in Acceptance and tests it,
and writes none of it.

**Check now is rendered in `waiting`, `review`, `overdue` and `ready`, and
only when `checkAvailable`.** `ready` is included because the sweep's
candidate rule skips an Episode with a visible recording (`T-143`), so a
second segment after Part 1 is published can only be found by hand. Not in
`upcoming`, `open`, `not_recorded` or `cancelled`. The service refuses a press
it cannot honour with `errors.live.check_unavailable`, which only a stale page
reaches: `D-018` explains rather than refuses, and the explanation is the
button's absence with `T-141`'s connection copy beside it.

**`checkAvailable` is `LiveSessionService::canCheck()`, built from `T-143`'s
own lookups rather than a second copy of the candidate rule.**
`$episode->isLive()`, a tagged finder from `finderFor()`, a usable connection
from `searchableConnection()` — which is where `settings.cloud_recording`
(`T-141`'s key) being false rules the Episode out — and a
`creatorStateFor()` in `waiting`, `review`, `overdue` or `ready`. Reading the
state rather than re-listing `records()`, `isCancelled()` and
`isNotRecorded()` keeps one state model: a session declared not recorded, a
cancelled one and a `records: false` one are already states, and a rule that
repeated them would drift from `T-127`'s. No vendor host or path pattern
appears outside `T-142`'s folder (`D-022`); the service asks the contract.

**A vendor failure during Check now is an outcome, not an exception.**
`T-143`'s `search()` catches the finder's `Throwable`, reports it, stamps the
attempt through `markChecked()` and answers `RecordingSearch::afterFailure()`;
nothing is written. So Check now flashes `series.recording_check_failed`
rather than `T-142`'s `upstreamUnavailable`, and the press still counted:
the next one waits `recheck_seconds`, which is the right answer to a vendor
that just failed.

**"There's no recording for this session" is not offered in `review`.** A
held row is a candidate the creator has to answer first. Rejecting every
held row returns the card to `waiting` or `overdue`, where `T-127` offers
the declaration.

**Outcome copy is chosen on the server, in one order: too soon, failed,
published, held, nothing.** `attachFound()` holds every instance when two or
more fall in the window, so one check does not publish some and hold others;
the order is stated so a future rule change has one place to think about.

**`T-143`'s per-recording `heldLine` becomes `startedLine` on every row.**
`T-143` renders the start and the length only under a held row
(`live.panel.review.held_line`); a rejected row and a published one want the
same two facts, and a creator picking between a 4-minute rehearsal at 9:02
and a 58-minute class at 10:01 is reading them beside rows that are neither.
So the condition is dropped, the key moves to `live.panel.recording.started`,
and there is one sentence rather than two saying the same thing — a
`T-143` draft edit, recorded in Notes. Pasted rows carry it too (`T-126`
sets theirs from the Episode's own schedule), so the two sources render
alike. `D-027` stores no reason for a hold, so the panel shows the facts and
not a verdict.

**No vendor name in this task's copy.** `D-025` allows one on Join and Watch
and for chat platforms; "your connected account" and "your meeting app" are
what the panel and the flashes say. `T-143`'s `review` line is its own.

**No page edit, no `SharedController` edit, no `routes/shared.php` edit.**
Peers see nothing new: a published row is `T-126`'s `ready` and Watch. The
panel receives whole objects (`T-127`'s decision), so `share/series/Show.vue`
is not touched and the stream's claim order holds.

**Tests fake the finder, not Zoom, through `T-143`'s
`Tests\Doubles\FindsRecordingsInMemory`.** `T-143` settled it: what
`ZoomRecordings` does with a payload is `T-142`'s suite against `T-122`'s
fixtures, and what Qori does with what comes back is these. The double
records the timeout it was called with, which is how this task proves the
button uses `CHECK_NOW_TIMEOUT_SECONDS` and not the sweep's, and
`Http::preventStrayRequests()` proves no request leaves. Held rows for the
publish and reject cases are written directly, as `attachFound()` writes
them, so those cases call no finder at all.

**Progress and certificates are untouched.** Publish, reject and check write
`episode_recordings`, `episodes.recording_checked_at` and `session_notices`,
never `accesses`; `ProgressService::hasFinished()` counts Episodes (`D-024`).

## Preconditions

**Data this task verifies against:** a clean database. The feature tests
build a Group on `start` with `timezone` `Australia/Brisbane`, its owner and
an accepted Collaborator as `tests/Feature/Series/LiveSessionTest.php:41-60`
does; a published Series with one live Zoom Episode
(`join_url` `https://zoom.us/j/91827405566`) through `EpisodeService::add()`
with `T-123`'s `$startsAt` one hour ahead and `lengthMinutes: 60`; a Zoom
`Connection` through `Connection::factory()->zoom()` (`T-141`'s state, which
writes `settings.cloud_recording`) inside `CurrentGroup::runFor()`; held rows
written through `$episode->recordings()->create([...])` with `source` `zoom`,
a `vendor_ref`, `published_at` null and `needs_review` true — the shape
`attachFound()` writes — under `app(CurrentGroup::class)->set($group)`; a
Peer through `AccessService::grant()`; `CarbonImmutable::setTestNow()` past
the scheduled end; `T-143`'s `Tests\Doubles\FindsRecordingsInMemory` bound in
place of the tagged finders and `Http::preventStrayRequests()` in `setUp`, as
`T-143`'s own suite does.
`php artisan wayfinder:generate --with-form` after the routes are added, so
`@/routes/share/series/episodes/recordings` exports `publish`, `reject` and
`check`.

**Equipment:** none. A browser for the last acceptance walk, at mobile width
too.

**Spike:** none owed by this task. It reads no vendor payload: the finder
does, and its suite is `T-142`'s against `T-122`'s fixtures under
`tests/Fixtures/zoom/recordings/`.

## Scope

**In:**

- `RecordingService::publish()`, `reject()` and `checkNow()`;
  `EpisodeRecording::isRejected()`.
- `LiveSessionService::CHECK_NOW_TIMEOUT_SECONDS`, `canCheck()` and
  `claimCheck()`;
  `RecordingSearch::SKIPPED_TOO_SOON`, `tooSoon()` and `secondsToWait()`.
- `RecordingController::publish()`, `reject()` and `check()`, and the three
  routes.
- `SeriesController::show()`: `publishedAt`, `needsReview` and `startedLine`
  on each creator-side recording (`startedLine` widening `T-143`'s
  `heldLine`); `checkAvailable` on each live Episode; the `livePanel` copy
  for the held list, the rejected label, the check help and the three action
  labels.
- `LiveSessionPanel.vue`: the held list with Publish and Not this one, the
  rejected label with Publish, and Check now by state.
- The lang lines, the `errors.live` additions, the flow and tinker edits.

**Out:**

- The sweep, its backoff and candidate rule, `search()`, `attachFound()`,
  `markChecked()`, `finderFor()`, `searchableConnection()`,
  `SWEEP_TIMEOUT_SECONDS`, `App\Data\RecordingSearch` itself,
  `EpisodeRecording::isHeld()`,
  the `recording_checked_at` and `series.recording_publication` columns,
  `creatorStateFor()`, the detection block and the `recording_publication`
  setting on the Series form (`T-143`).
- `FindsRecordings`, `ZoomRecordings`, `ZoomMeetingLink`, `openUrl()` on
  Watch and the fixtures (`T-142`, `T-122`); the Zoom connection and its
  settings (`T-141`).
- The `recording_ready` email, the ledger and `queueRecordingReady()`
  (`T-128`); the creator nudge and the send-status line (`T-129`); the
  deliberate re-send (`T-140`).
- Paste (`T-126`); Hide, Show again and the not-recorded declaration
  (`T-127`).
- Editing a held row's link or passcode; deleting a row; storing why a row
  was held (`D-027` has no column for it).
- A reason shown to the Peer while a row is held: the Peer's copy is `waiting`
  (`T-125`, `T-143`).
- Webhooks clearing `recording_checked_at` (`D-027`: after Marketplace
  publication).
- Rendering the last-checked time and the sweep's next check on the panel
  (`T-143`'s line); a countdown on the button.
- Any Peer-facing change, `SharedController`, `routes/shared.php`,
  `LiveSessionCard.vue`.

## Files

| Path                                                  | Change | Notes                                                                                                                                                    |
| ----------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `app/Services/RecordingService.php`                   | edit   | `publish()`, `reject()`, `checkNow()` beside `T-126`'s `paste()`, `T-127`'s `hide()`/`unhide()` and `T-143`'s `search()`                                 |
| `app/Services/LiveSessionService.php`                 | edit   | `CHECK_NOW_TIMEOUT_SECONDS`, `canCheck()`, `claimCheck()`                                                                                                |
| `app/Data/RecordingSearch.php`                        | edit   | `T-143`'s shape gains `SKIPPED_TOO_SOON`, `tooSoon()` and `secondsToWait()`                                                                              |
| `app/Models/EpisodeRecording.php`                     | edit   | `isRejected()` beside `T-143`'s `isHeld()`                                                                                                               |
| `app/Http/Controllers/Share/RecordingController.php`  | edit   | `publish()`, `reject()`, `check()` beside `store()`, `hide()`, `unhide()`                                                                                |
| `app/Http/Controllers/Share/SeriesController.php`     | edit   | `publishedAt`, `needsReview`, `startedLine` (widening `T-143`'s `heldLine`) per recording; `checkAvailable` per live Episode; `livePanel`                |
| `routes/share/episodes.php`                           | edit   | `recordings.publish`, `recordings.reject`, `recordings.check`                                                                                            |
| `resources/js/components/series/LiveSessionPanel.vue` | edit   | The held list, Publish / Not this one, the rejected label, Check now by state                                                                            |
| `lang/en/live.php`                                    | edit   | `panel.recording.started` (replacing `T-143`'s `panel.review.held_line`), `panel.held.intro`, `panel.recording.rejected`, `panel.check.*`, three actions |
| `lang/en/series.php`                                  | edit   | `recording_published`, `recording_rejected`, `recording_check_*`                                                                                         |
| `lang/en/errors.php`                                  | edit   | `live.already_published`, `live.check_unavailable`                                                                                                       |
| `docs/flows/live-sessions.md`                         | edit   | "Reviewing a found recording": the publish, reject and Check now chains and the throttle                                                                 |
| `docs/tinker/live-sessions.md`                        | edit   | Hold a row by hand, publish it, reject it, run Check now against a fake                                                                                  |
| `tests/Feature/Series/RecordingReviewTest.php`        | new    | 24 cases                                                                                                                                                 |

No config: `recheck_seconds` is `T-123`'s key, read and never redeclared. No
migration, factory or seeder: every column is `T-126`'s or `T-143`'s, and
`ConnectionFactory::zoom()` is `T-141`'s. Neither page is edited, for the
reason under Decisions. `docs/flows/README.md` and `docs/tinker/README.md`
already carry `T-125`'s rows for the two files edited here.
`tests/Doubles/FindsRecordingsInMemory.php` is used unchanged and so is not a
row. `qori:reachability` sees the three routes through their Wayfinder
imports in the panel (`Reachability::isLinked()`,
`app/Support/Reachability.php:162-171`).
`app/Providers/IntegrationServiceProvider.php` is not listed: `T-143` already
gives `LiveSessionService` the tagged `recording-finders`.

## Database

None. `episode_recordings.published_at`, `hidden_at` and `needs_review` are
`T-126`'s columns (`D-027`); `episodes.recording_checked_at` and
`series.recording_publication` are `T-143`'s.

## Code

```php
namespace App\Models;

class EpisodeRecording extends Model   // T-126's model and isVisible(); T-143's isHeld() and scopeHeld()
{
    /**
     * "Not this one": never published, hidden. The row stays so the unique
     * (episode_id, vendor_ref) keeps a sweep from attaching it again. The
     * complement of T-143's isHeld() among unpublished rows.
     */
    public function isRejected(): bool;
    // return $this->published_at === null && $this->hidden_at !== null;
}
```

```php
namespace App\Services;

use App\Concerns\LocksOverCapSeries;
use App\Data\RecordingSearch;
use App\Exceptions\AppException;
use App\Models\EpisodeRecording;
use App\Models\Series;
use App\Models\User;
use Carbon\CarbonImmutable;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class RecordingService   // T-126's paste(), T-127's recordingOf()/hide()/unhide() and T-143's search() are unchanged
{
    use LocksOverCapSeries;

    /** T-127 promoted LiveSessionService, T-128 SessionNoticeService, T-143 ConnectionService. Nothing new here. */
    public function __construct(
        private LiveSessionService $sessions,
        private SessionNoticeService $notices,
        private ConnectionService $connections,
    ) {}

    /**
     * The creator's review of a recording Qori found (D-027): it becomes
     * what a Peer sees, and every Peer with access is queued one email
     * (T-128). Idempotent: a published row is answered as it is and nothing
     * is queued again. On a rejected row this is the undo — hidden_at is
     * cleared. $by reaches the log line only, as in paste().
     */
    public function publish(Series $series, string $episodeId, string $recordingId, User $by): EpisodeRecording;
    // $this->guardSeriesUnlocked($series->group, 'publish a recording');
    // $recording = $this->recordingOf($this->sessions->liveEpisodeOf($series, $episodeId), $recordingId);
    //
    // if ($recording->published_at !== null) {
    //     return $recording;
    // }
    //
    // return DB::transaction(function () use ($recording, $by): EpisodeRecording {
    //     $recording->forceFill(['published_at' => now(), 'hidden_at' => null, 'needs_review' => false])->save();
    //
    //     // Recipients: active Accesses granted on or before the Episode's earliest
    //     // visible recording's published_at (T-128's rule), so a Part 2 queues nothing.
    //     $queued = $this->notices->queueRecordingReady($recording);
    //
    //     Log::info("Recording {$recording->getKey()} published by user {$by->getKey()}; {$queued} recording_ready notices queued.");
    //
    //     return $recording;
    // });

    /**
     * "Not this one." The row stays, hidden and never published, so the same
     * vendor instance is never attached again. A published row is refused:
     * Hide (T-127) is its control. Rejecting a rejected row is a no-op.
     */
    public function reject(Series $series, string $episodeId, string $recordingId, User $by): EpisodeRecording;
    // $this->guardSeriesUnlocked($series->group, 'reject a recording');
    // $recording = $this->recordingOf($this->sessions->liveEpisodeOf($series, $episodeId), $recordingId);
    //
    // if ($recording->published_at !== null) {
    //     throw AppException::invalidRequest(
    //         'errors.live.already_published',
    //         devMessage: "Recording {$recordingId} is published; hide it rather than rejecting it.",
    //     );
    // }
    //
    // if ($recording->hidden_at === null) {
    //     $recording->forceFill(['hidden_at' => now(), 'needs_review' => false])->save();
    //     Log::info("Recording {$recording->getKey()} rejected by user {$by->getKey()}.");
    // }
    //
    // return $recording;

    /**
     * Look for this Episode's recording now (D-021 rule 2): the throttle,
     * then T-143's search() with the creator's timeout. The claim is written
     * under the row lock by claimCheck(), so a double press, or a press
     * beside the sweep, cannot both call the vendor; search() stamps the
     * same column again with the same $now, which is the same instant.
     *
     * The vendor is never called outside the lock's decision and never
     * inside the lock. A finder that throws is search()'s to report: this
     * method never throws for a vendor.
     */
    public function checkNow(Series $series, string $episodeId, User $by, CarbonImmutable $now): RecordingSearch;
    // $this->guardSeriesUnlocked($series->group, 'check for a recording');
    // $episode = $this->sessions->liveEpisodeOf($series, $episodeId);
    //
    // if (! $this->sessions->canCheck($episode, $now)) {
    //     throw AppException::invalidRequest(
    //         'errors.live.check_unavailable',
    //         devMessage: "Episode {$episodeId} has no usable connection, no finder for its join link, or a state Qori does not search.",
    //     );
    // }
    //
    // $recheck = (int) config('qori.live.recheck_seconds');
    // $blocking = $this->sessions->claimCheck($episode, $now, $recheck);
    //
    // if ($blocking instanceof CarbonImmutable) {
    //     return RecordingSearch::tooSoon($blocking, $blocking->addSeconds($recheck));
    // }
    //
    // $outcome = $this->search($episode->fresh(), $now, LiveSessionService::CHECK_NOW_TIMEOUT_SECONDS);
    //
    // Log::info("Check now on episode {$episodeId} by user {$by->getKey()}: {$outcome->found} found, {$outcome->published} published, {$outcome->held} held.");
    //
    // return $outcome;
}
```

```php
namespace App\Services;

use App\Enums\LiveState;
use App\Models\Episode;
use Carbon\CarbonImmutable;
use Closure;

class LiveSessionService   // T-124's, T-125's, T-127's, T-134's and T-143's class; these join them
{
    /** A creator is waiting on this click. The sweep's longer SWEEP_TIMEOUT_SECONDS is T-143's. */
    public const CHECK_NOW_TIMEOUT_SECONDS = 5;

    /**
     * Whether Check now can do anything for this Episode. Built from T-143's
     * own lookups rather than a second copy of its candidate rule: a tagged
     * finder for the join link, a live connection that does not say cloud
     * recording is off, and a state Qori would search. `ready` is included
     * because the sweep stops once a recording is visible, so a second
     * segment can only be found by hand.
     *
     * Read by SeriesController::show() to render the button, and by
     * RecordingService::checkNow() before it claims the row.
     */
    public function canCheck(Episode $episode, CarbonImmutable $now): bool;
    // return $episode->isLive()
    //     && $this->finderFor($episode) !== null                                  // T-143
    //     && $this->searchableConnection($episode) !== null                       // T-143: cloud_recording false rules it out
    //     && in_array(
    //         $this->creatorStateFor($episode, $now),                             // T-143: review, and never shown to a Peer
    //         [LiveState::Waiting, LiveState::Review, LiveState::Overdue, LiveState::Ready],
    //         true,
    //     );

    /**
     * Claim the next check for this Episode under the row lock (D-021 rule 2).
     *
     * Answers null when the claim was taken — recording_checked_at is $now and
     * the caller may call the vendor — and the blocking instant when the last
     * check, the sweep's included, was less than $recheckSeconds ago. Reading
     * and writing inside T-124's lock is what stops two presses, or a press
     * beside the sweep, from both calling out; the vendor is called after the
     * transaction has committed, so a five-second call never holds a lock.
     *
     * The callback is T-124's shape: it is handed the re-read content and the
     * locked row and returns the content to save. The content is returned
     * unchanged both ways; the column is written on the row, which the
     * service saves.
     */
    public function claimCheck(Episode $episode, CarbonImmutable $now, int $recheckSeconds): ?CarbonImmutable;
    // $blocking = null;
    //
    // $this->withLockedContent($episode, function (array $content, Episode $locked) use ($now, $recheckSeconds, &$blocking): array {
    //     $last = $locked->recording_checked_at?->toImmutable();
    //
    //     if ($last !== null && $last->addSeconds($recheckSeconds)->isAfter($now)) {
    //         $blocking = $last;   // nothing written; save() finds nothing dirty
    //
    //         return $content;
    //     }
    //
    //     $locked->recording_checked_at = $now;
    //
    //     return $content;
    // });
    //
    // return $blocking;

    // T-143's and T-124's, cited for what this task reads and never redeclares:
    //
    // public const SWEEP_TIMEOUT_SECONDS = 30;
    // public function withLockedContent(Episode $episode, Closure $callback): Episode;       // T-124
    // public function liveEpisodeOf(Series $series, string $episodeId): Episode;             // T-127
    // public function creatorStateFor(Episode $episode, CarbonImmutable $now): LiveState;    // T-143
    // public function finderFor(Episode $episode): ?FindsRecordings;                         // T-143
    // public function searchableConnection(Episode $episode): ?Connection;                   // T-143
    // public function attachFound(Episode $episode, array $found, CarbonImmutable $now): Collection;   // T-143
}
```

```php
// App\Data\RecordingSearch — T-143's shape. One skip reason and two members join it;
// every other field, and the class itself, is T-143's and unchanged.

/** The press came inside qori.live.recheck_seconds of the last check (D-021 rule 2). */
public const SKIPPED_TOO_SOON = 'too_soon';

/**
 * Nothing was called: the last check, by this creator or by the sweep, was
 * too recent. $checkedAt is that earlier check and $nextCheckAt is when the
 * next press is honoured — the same question the sweep's $nextCheckAt
 * answers, asked of the button.
 */
public static function tooSoon(CarbonImmutable $checkedAt, CarbonImmutable $nextAllowedAt): self;
// return new self(checkedAt: $checkedAt, nextCheckAt: $nextAllowedAt, skipped: self::SKIPPED_TOO_SOON);

/** Whole seconds until it is worth looking again, at least 1; 0 when nothing is due. */
public function secondsToWait(CarbonImmutable $now): int;
// return $this->nextCheckAt === null ? 0 : max(1, (int) ceil($now->diffInSeconds($this->nextCheckAt)));
```

```php
namespace App\Http\Controllers\Share;

use App\Concerns\ResolvesShareSeries;
use App\Data\RecordingSearch;
use App\Http\Controllers\Controller;
use App\Services\LiveSessionService;
use App\Services\RecordingService;
use App\Support\CurrentUser;
use App\Support\Terminology;
use Carbon\CarbonImmutable;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Inertia\Inertia;

/**
 * T-126's store() and T-127's hide()/unhide() are unchanged. Route parameters
 * arrive positionally and come first; $group is declared because of that and
 * never read — see SeriesController.
 */
class RecordingController extends Controller
{
    use ResolvesShareSeries;

    public function publish(string $group, string $seriesId, string $episodeId, string $recordingId, Request $request, RecordingService $recordings, Terminology $terminology): RedirectResponse;
    // $recordings->publish($this->seriesById($seriesId), $episodeId, $recordingId, CurrentUser::orFail($request));
    // Inertia::flash('toast', ['type' => 'success', 'message' => $terminology->line('series.recording_published')]);
    //
    // return back();

    public function reject(string $group, string $seriesId, string $episodeId, string $recordingId, Request $request, RecordingService $recordings, Terminology $terminology): RedirectResponse;
    // $recordings->reject($this->seriesById($seriesId), $episodeId, $recordingId, CurrentUser::orFail($request));
    // Inertia::flash('toast', ['type' => 'success', 'message' => $terminology->line('series.recording_rejected')]);
    //
    // return back();

    /** One sentence per outcome, chosen here in the order Decisions states: too soon, failed, published, held, nothing. */
    public function check(string $group, string $seriesId, string $episodeId, Request $request, RecordingService $recordings, LiveSessionService $sessions, Terminology $terminology): RedirectResponse;
    // $series = $this->seriesById($seriesId);
    // $title = $sessions->liveEpisodeOf($series, $episodeId)->title;   // the flash names it; checkNow() resolves the row again under its own guards
    // $now = CarbonImmutable::now();
    // $outcome = $recordings->checkNow($series, $episodeId, CurrentUser::orFail($request), $now);
    //
    // [$type, $message] = match (true) {
    //     $outcome->skipped === RecordingSearch::SKIPPED_TOO_SOON => ['info', $terminology->line('series.recording_check_throttled', ['title' => $title, 'seconds' => (string) $outcome->secondsToWait($now)])],
    //     $outcome->failed => ['error', $terminology->line('series.recording_check_failed', ['title' => $title])],
    //     $outcome->published > 0 => ['success', $terminology->choice('series.recording_check_published', $outcome->published, ['title' => $title])],
    //     $outcome->held > 0 => ['success', $terminology->choice('series.recording_check_held', $outcome->held, ['title' => $title])],
    //     default => ['info', $terminology->line('series.recording_check_none', ['title' => $title])],
    // };
    //
    // // canCheck() has already refused the two other skip reasons, so the match's
    // // default is genuinely "the finder looked and found nothing new".
    // Inertia::flash('toast', ['type' => $type, 'message' => $message]);
    //
    // return back();
}
```

```php
// App\Http\Controllers\Share\SeriesController::show() — three keys on each creator-side
// recording (T-126's map, where T-127 added hiddenAt and T-143 isHeld; $zone is the Group's
// resolved zone, $scope?->timezone() ?? Timezones::fallback(), already read at :175):
'publishedAt' => $recording->published_at?->toIso8601String(),
'needsReview' => $recording->needs_review,
// T-143's `heldLine` becomes this, on every row rather than only a held one:
'startedLine' => __('live.panel.recording.started', [
    'when' => $recording->started_at->setTimezone($zone)->format('j M Y, g:ia T'),
    'minutes' => (string) $recording->duration_minutes,
]),

// one key on each live Episode's `live` object (T-127's `state` — T-143's creatorStateFor() —
// and `notRecordedAt` and T-143's `detection` sit beside it). $now is the one
// CarbonImmutable::now() show() already reads for the state:
'checkAvailable' => $sessions->canCheck($episode, $now),

// and the `livePanel` prop (T-127's) gains:
'heldIntro' => $terminology->line('live.panel.held.intro'),
'rejected' => __('live.panel.recording.rejected'),
'checkHelp' => $terminology->line('live.panel.check.help'),
'checkReadyHelp' => $terminology->line('live.panel.check.ready_help'),
'actions' => [
    // ...T-127's hide, unhide, addAnother, notRecorded, undoNotRecorded...
    'publish' => __('live.panel.actions.publish'),
    'reject' => __('live.panel.actions.reject'),
    'check' => __('live.panel.actions.check'),
],
```

`LiveSessionPanel.vue` (creator) — imports
`{ publish, reject, check } from '@/routes/share/series/episodes/recordings'`
(Wayfinder). Each control is an Inertia `<Form>` posting to the helper's URL
with no fields, `:disabled="processing || lock.active"`, exactly as `T-127`'s
Hide and the Move up form (`resources/js/pages/share/series/Show.vue:434-456`).
The recording row type gains `publishedAt: string | null` and
`needsReview: boolean`, and `T-143`'s `heldLine: string | null` becomes
`startedLine: string`; the live object gains `checkAvailable: boolean`.
`isHeld` is `T-143`'s and is what the list branches on. What renders:

| Row                                           | Line                                                                     | Controls                      |
| --------------------------------------------- | ------------------------------------------------------------------------ | ----------------------------- |
| Held (`isHeld`)                               | `startedLine`, the link (the creator's, as `T-126` renders it), passcode | **Publish**, **Not this one** |
| Rejected (`publishedAt` null, `hiddenAt` set) | `startedLine`, then `livePanel.rejected`                                 | **Publish**                   |
| Published (`publishedAt` set)                 | `T-126`'s and `T-127`'s line, plus `startedLine`                         | `T-127`'s Hide / Show again   |

The held rows are grouped first under `livePanel.heldIntro` when any exists,
whatever the state, then the rest of the list. Check now renders as one
`<Form>` when `live.checkAvailable` and `live.state` is `waiting`, `review`
or `overdue` (with `livePanel.checkHelp` beneath) or `ready` (with
`livePanel.checkReadyHelp` beneath); `T-143`'s `review` line stays where
`T-143` put it. "There's no recording for this session" is not rendered in
`review` (see Decisions). Nothing else on the panel changes.

`routes/share/episodes.php`, after `T-127`'s four lines:

```php
Route::post('series/{seriesId}/episodes/{episodeId}/recordings/{recordingId}/publish', [RecordingController::class, 'publish'])
    ->name('series.episodes.recordings.publish');
Route::post('series/{seriesId}/episodes/{episodeId}/recordings/{recordingId}/reject', [RecordingController::class, 'reject'])
    ->name('series.episodes.recordings.reject');
Route::post('series/{seriesId}/episodes/{episodeId}/recordings/check', [RecordingController::class, 'check'])
    ->name('series.episodes.recordings.check');
```

`docs/flows/live-sessions.md`: a "Reviewing a found recording" section —
`POST …/publish` → `RecordingController::publish()` → `RecordingService::publish()`
→ the row published → `SessionNoticeService::queueRecordingReady()`;
`POST …/reject` → `reject()` → the row hidden, never published, kept for the
unique key; `POST …/recordings/check` → `RecordingController::check()` →
`RecordingService::checkNow()` → `LiveSessionService::canCheck()` →
`claimCheck()` claims `recording_checked_at` under `withLockedContent()` or
answers the blocking instant → `RecordingService::search()` (`T-143`'s, with
`CHECK_NOW_TIMEOUT_SECONDS`) → `FindsRecordings::find()` → `attachFound()` →
`queueRecordingReady()` for what it published → one flash per outcome; and
the sentence that the sweep and Check now share one column, one search and
one rule.
`docs/tinker/live-sessions.md`: write a held row by hand, read
`creatorStateFor()` (`review`),
`app(App\Services\RecordingService::class)->publish($series, $episodeId, $recordingId, $user)`,
`reject(...)`, then
`app(App\Services\RecordingService::class)->checkNow($series, $episodeId, $user, CarbonImmutable::now())`
against `T-143`'s recipe for standing a finder in, and the second call inside
a minute answering `skipped: too_soon`.

## Copy

| Key                                        | File                 | English                                                                                                                                                                                                                                                                            |
| ------------------------------------------ | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `live.panel.held.intro`                    | `lang/en/live.php`   | Qori found these in your connected account. Publish the right one — your :peer_plural only see what you publish, and each gets one email when you do.                                                                                                                              |
| `live.panel.recording.started`             | `lang/en/live.php`   | Started :when · :minutes min                                                                                                                                                                                                                                                       |
| `live.panel.recording.rejected`            | `lang/en/live.php`   | Rejected. Qori won't add this one again.                                                                                                                                                                                                                                           |
| `live.panel.check.help`                    | `lang/en/live.php`   | Qori looks again on its own. Press this to look right now.                                                                                                                                                                                                                         |
| `live.panel.check.ready_help`              | `lang/en/live.php`   | Qori stops looking once a recording is published. If the session had more than one part, check again here.                                                                                                                                                                         |
| `live.panel.actions.publish`               | `lang/en/live.php`   | Publish                                                                                                                                                                                                                                                                            |
| `live.panel.actions.reject`                | `lang/en/live.php`   | Not this one                                                                                                                                                                                                                                                                       |
| `live.panel.actions.check`                 | `lang/en/live.php`   | Check now                                                                                                                                                                                                                                                                          |
| `series.recording_published`               | `lang/en/series.php` | Recording published. Your :peer_plural with access can watch it from the :episode now, and each gets one email.                                                                                                                                                                    |
| `series.recording_rejected`                | `lang/en/series.php` | Rejected. Qori won't add that one again.                                                                                                                                                                                                                                           |
| `series.recording_check_throttled`         | `lang/en/series.php` | :title was checked just now. You can check again in :seconds seconds.                                                                                                                                                                                                              |
| `series.recording_check_none`              | `lang/en/series.php` | Nothing new for :title in your connected account just now.                                                                                                                                                                                                                         |
| `series.recording_check_failed`            | `lang/en/series.php` | Qori couldn't reach your connected account to look for :title. Try again in a moment.                                                                                                                                                                                              |
| `series.recording_check_published`         | `lang/en/series.php` | `{1} Found the recording of :title and published it. Your :peer_plural can watch it from the :episode now, and each gets one email.\|[2,*] Found :count recordings of :title and published them. Your :peer_plural can watch them from the :episode now, and each gets one email.` |
| `series.recording_check_held`              | `lang/en/series.php` | `{1} Found one recording of :title. Check it's the right one, then publish it.\|[2,*] Found :count recordings of :title. Publish the right ones and reject the rest.`                                                                                                              |
| `errors.live.already_published.message`    | `lang/en/errors.php` | That recording is already published.                                                                                                                                                                                                                                               |
| `errors.live.already_published.resolution` | `lang/en/errors.php` | Hide it instead if it's the wrong one.                                                                                                                                                                                                                                             |
| `errors.live.check_unavailable.message`    | `lang/en/errors.php` | Qori can't look for a recording of this session.                                                                                                                                                                                                                                   |
| `errors.live.check_unavailable.resolution` | `lang/en/errors.php` | Add the recording link yourself when you have it.                                                                                                                                                                                                                                  |

`live.panel.held.intro`, `live.panel.check.*`, `series.recording_published`
and the two `trans_choice` lines carry a noun and go through
`Terminology::line()` or `Terminology::choice()`
(`app/Support/Terminology.php:89`, `:108`); the two `trans_choice` lines
are written whole per count, as `series.archive_confirm` is
(`lang/en/series.php:57`), and `:count` is what `choice()` injects. The action
labels and the `started` and `rejected` lines carry no noun and are read with
`__()` on the panel. Every flash `check()` writes goes through
`Terminology::line()` or `choice()` whether or not it names a noun, because
one action resolving its sentences two ways is how the next line added
misses the Group's own words. `:seconds`
is `RecordingSearch::secondsToWait()`, computed from
`config('qori.live.recheck_seconds')` and never restated; `:when` is the
Group's zone with the zone named, as `series.session_scheduled` shows it;
`:minutes` is the row's `duration_minutes`. No line names a vendor: the
creator's connected account is "your connected account" (`D-025`). No line
under `live.*` says "live now", "has ended", "on its way" or "processing"
(`D-026`), and no article sits directly before a placeholder
(`TerminologyTest::test_no_lang_line_puts_an_article_before_a_noun`).
`errors.live.check_unavailable` carries a resolution because the paste path
is always open; `already_published` points at Hide because that is the
control the row has.

## Routes

| Verb | Path                                                                                 | Name                                       | Action                               |
| ---- | ------------------------------------------------------------------------------------ | ------------------------------------------ | ------------------------------------ |
| POST | `/g/{group}/series/{seriesId}/episodes/{episodeId}/recordings/{recordingId}/publish` | `share.series.episodes.recordings.publish` | `Share\RecordingController::publish` |
| POST | `/g/{group}/series/{seriesId}/episodes/{episodeId}/recordings/{recordingId}/reject`  | `share.series.episodes.recordings.reject`  | `Share\RecordingController::reject`  |
| POST | `/g/{group}/series/{seriesId}/episodes/{episodeId}/recordings/check`                 | `share.series.episodes.recordings.check`   | `Share\RecordingController::check`   |

All three in `routes/share/episodes.php`, inside `routes/share.php`'s
`auth`, `verified`, `group` group with prefix `g/{group}` and name prefix
`share.` (`routes/share.php:24-27`). Ids throughout: every one mutates
(`routes/share/episodes.php:19-26` for the pattern). No Peer route: Peers
see a published row through `T-126`'s Watch on `shared.episodes.open`.

## Tests

**New: `tests/Feature/Series/RecordingReviewTest.php` — 24 cases**
(`RefreshDatabase`; `Notification::fake()`; in `setUp`, `T-143`'s double and
its binding — `$this->finder = new FindsRecordingsInMemory;`,
`$this->app->when(LiveSessionService::class)->needs('$finders')->give(fn (): array => [$this->finder]);`
— and `Http::preventStrayRequests()`, which proves no request leaves;
private helpers `scene()` as `tests/Feature/Series/LiveSessionTest.php:41-60`
with `timezone` `Australia/Brisbane`; `liveEpisode(Series $series): Episode`
through `EpisodeService::add()` — Zoom, `join_url`
`https://zoom.us/j/91827405566`, `$startsAt` one hour ahead,
`lengthMinutes: 60` — followed by
`CarbonImmutable::setTestNow($episode->ends_at->addHour())`;
`zoomConnection(Group $group, ?bool $cloudRecording = true): Connection`
through `T-141`'s `Connection::factory()->zoom($cloudRecording)` inside
`CurrentGroup::runFor()`;
`held(Episode $episode, string $vendorRef, CarbonImmutable $startedAt, int $minutes): EpisodeRecording`
writing the row directly under `app(CurrentGroup::class)->set($group)`;
`found(string $ref, CarbonImmutable $startedAt, int $minutes): SessionRecording`
as `T-143`'s suite builds one, loaded into `$this->finder->returns`;
`peer(Series $series): User` through `AccessService::grant()`; a refusal on
a POST asserted as `tests/Feature/Access/SeriesAccessCodeTest.php:87-90` and
`:157` do — `assertRedirect()` then `assertSessionHas(SessionKey::FLASH_DATA, $this->toastContains(...))`,
because a POST that throws an `AppException` flashes and redirects rather
than answering a status (`app/Exceptions/AppException.php:284-288`);
a creator-side state read on
`app(LiveSessionService::class)->creatorStateFor($episode->fresh(), CarbonImmutable::now())`
and a Peer-side one on `stateFor()`)

1. `test_publishing_a_held_recording_makes_it_visible` — one held row; POST
   publish; `published_at` set, `needs_review` false, `hidden_at` null;
   `creatorStateFor()` is `Ready`; the Peer's page has `series.episodes.0.live.state`
   `ready` and `live.recordings.0.id` the row; the success toast is
   `series.recording_published`.
2. `test_publishing_queues_one_recording_ready_row_per_peer_with_access` —
   two Peers granted before; publish; two `session_notices` rows with `kind`
   `recording_ready`, `status` `pending`, `recording_id` the row, one per
   Peer (owner acceptance 6).
3. `test_nothing_is_queued_while_a_recording_is_held` — one held row, one
   Peer; no `session_notices` row; the Peer's page has `live.state` `waiting`
   and `live.recordings` empty (owner acceptance 6).
4. `test_publishing_twice_queues_nothing_more` — publish, then POST publish
   again; the ledger count is unchanged; the second answers the same success
   toast, no error (owner acceptance 7).
5. `test_rejecting_a_held_recording_keeps_the_row_hidden` — POST reject;
   `hidden_at` set, `published_at` null, `needs_review` false; the row still
   exists; `creatorStateFor()` is back to `Waiting`; the Peer's page lists
   nothing; the toast is `series.recording_rejected`.
6. `test_a_published_recording_cannot_be_rejected` — `T-126`'s `paste()`,
   then POST reject; the error toast is
   `errors.live.already_published.message`; `hidden_at` still null.
7. `test_publishing_a_rejected_recording_is_the_undo` — reject, then POST
   publish; `hidden_at` null, `published_at` set; `Ready`; one ledger row per
   Peer.
8. `test_the_creator_picks_one_of_several_held_recordings` — two held rows
   (`vendor_ref` `a` at 9:02 for 4 minutes, `b` at 10:01 for 58); publish
   `b`, reject `a`; the Peer's `live.recordings` has one row, `b`, labelled
   `Watch recording`; `a` keeps its `vendor_ref` and `hidden_at` (owner
   acceptance 8).
9. `test_the_creators_page_carries_the_held_rows_facts_and_controls` — one
   held and one rejected row: `assertInertia` sees the held row with
   `isHeld` true, `needsReview` true, `publishedAt` null, `hiddenAt` null and
   a `startedLine` containing `10:01am AEST` and `58 min`; the rejected row
   with `hiddenAt` non-null and a `startedLine` of its own;
   `livePanel.actions.publish` equal to `live.panel.actions.publish`;
   `live.checkAvailable` true with a usable connection.
10. `test_check_now_is_unavailable_without_a_usable_connection` — no
    Connection, then a revoked one (`ConnectionFactory::revoked()`,
    `database/factories/ConnectionFactory.php:38`): `live.checkAvailable`
    false both times; POST check answers the error toast
    `errors.live.check_unavailable.message`; `recording_checked_at` stays
    null; `$this->finder->calls` stays empty.
11. `test_check_now_is_unavailable_when_cloud_recording_is_off` —
    `Connection::factory()->zoom(false)`: the same three assertions;
    `zoom(null)` — unread settings — leaves `checkAvailable` true, as
    `T-143`'s `searchableConnection()` says.
12. `test_check_now_is_unavailable_for_a_link_no_finder_handles` — a live
    Episode on `EpisodeProvider::Link` with a Meet URL and a usable Zoom
    Connection: `checkAvailable` false and the POST refused; the finder is
    never called.
13. `test_check_now_is_unavailable_for_a_cancelled_or_not_recorded_session` —
    `content.not_recorded_at` set through `T-127`'s `declareNotRecorded()`:
    `checkAvailable` false and the POST refused; `records` false: the same;
    `content.cancelled_at` set: the same.
14. `test_check_now_runs_the_finder_at_once_and_holds_the_find_on_review_first` —
    the finder returns one recording; POST check; one `episode_recordings`
    row with `source` `zoom`, that `vendorRef`, `published_at` null,
    `needs_review` true; `recording_checked_at` equals the frozen now;
    `$this->finder->calls` holds one call with `timeout` 5, which is
    `LiveSessionService::CHECK_NOW_TIMEOUT_SECONDS` and not the sweep's 30; the
    toast is `series.recording_check_held` for one; the Peer's page still
    `waiting` with no Watch; no `session_notices` row (owner acceptance 6).
15. `test_check_now_publishes_at_once_on_automatic_when_the_match_is_clear` —
    `series.recording_publication` `automatic`; one recording at the
    scheduled start for 58 minutes; the row has `published_at` set and
    `needs_review` false; one ledger row per Peer; the toast is
    `series.recording_check_published` for one; the Peer's page is `ready`
    (owner acceptance 6).
16. `test_check_now_holds_two_instances_even_on_automatic` — `automatic`;
    the finder returns two; both rows `published_at` null and `needs_review`
    true; the toast is `series.recording_check_held` containing `2`; no
    ledger row (owner acceptance 8).
17. `test_check_now_finds_nothing_new_for_an_instance_already_rejected` — a
    held row whose `vendor_ref` is the one the finder returns, rejected;
    travel 61 seconds; POST check; still one row, still rejected; the toast
    is `series.recording_check_none` (owner acceptance 7).
18. `test_check_now_in_ready_can_find_a_second_part` — Part 1 pasted; the
    finder returns a `vendorRef` not yet stored; POST check; a second row
    held; `creatorStateFor()` is `Review` while `stateFor()` stays `Ready`;
    the Peer's `live.recordings` has Part 1 only (owner acceptance 8).
19. `test_a_second_press_inside_the_throttle_says_checked_just_now_and_calls_nothing` —
    POST check; travel 10 seconds; POST check again: `$this->finder->calls`
    still holds one call, the info toast is
    `series.recording_check_throttled` containing `50`; travel to 61
    seconds after the first: a third press calls the finder again.
20. `test_a_sweep_check_counts_toward_the_throttle` — `recording_checked_at`
    set 30 seconds ago by hand, as the sweep leaves it; POST check answers
    the throttled toast containing `30` and calls the finder not at all.
21. `test_a_finder_that_fails_leaves_the_check_claimed` —
    `$this->finder->throws = AppException::upstreamUnavailable(...)`; POST
    check; the error toast is `series.recording_check_failed`, not the
    finder's own message, because `T-143`'s `search()` reports and answers
    `afterFailure()`; `recording_checked_at` equals now; no row; a press 10
    seconds later is throttled.
22. `test_a_slug_on_a_review_action_does_not_resolve` — POST publish with the
    Series slug as `seriesId`, as
    `tests/Feature/Series/ShareSeriesRoutesTest.php:143-151` does: the
    redirect and the `errors.series.not_found.message` toast, and the row
    unchanged.
23. `test_another_groups_recording_is_not_found` — a second Group's owner
    posts publish, reject and check under their own `g/{group}` with the
    first Group's Series, Episode and recording ids: each answers the
    `errors.series.not_found.message` toast, nothing changed, the finder
    never called.
24. `test_the_over_cap_lock_refuses_publish_reject_and_check` — the group of
    `OverCapLockTest::overCapGroup()`
    (`tests/Feature/Series/OverCapLockTest.php:59-71`) with a live Episode on
    the surviving Series: each POST answers the over-cap toast
    (`errors.series.locked_over_cap`, whose `:used` and `:limit` the trait
    fills, `app/Concerns/LocksOverCapSeries.php:48-56`); the finder is never
    called and `recording_checked_at` stays null.

The renamed-vocabulary case: `test_the_flashes_use_the_groups_own_words` is
folded into case 1 — the Group is entitled and given
`settings[Terminology::SETTINGS_KEY]` as
`tests/Feature/TerminologyTest.php:36-51` and `:85-97` do, and the success
toast contains `Ruffies`. The publish flash is the one sentence here with a
noun a Peer never sees; the email itself is `T-128`'s and has its own
renamed-vocabulary case there.

**Changed:** none expected. `T-127`'s `RecordingStateTest` asserts keys this
task adds beside, never replaces; `T-143`'s sweep tests set
`recording_checked_at` themselves and never call `checkNow()`. `T-143`'s
assertion on `live.recordings.0.heldLine` reads `startedLine` after this
task, which is the one line its suite has to follow — listed here rather
than as a changed file, because `T-143` lands first and its writer is told
in Notes.

Total: 24 new cases.

## Acceptance

- [ ] A creator with a held recording sees it on the panel with when it
      started and how long it ran, publishes it, and the Peer's card is
      `ready` with Watch within the same minute; every Peer with access has
      one `recording_ready` row, and none existed before the publish (owner
      acceptance 6)
- [ ] On `automatic`, Check now on a clear match publishes without a second
      press; two instances in the window are held even on `automatic`, the
      creator publishes one and rejects the other, and the Peer sees only the
      published one (owner acceptance 8)
- [ ] A rejected recording keeps its row, is never attached again by Check
      now or the sweep, can be published later as the undo, and a second
      Publish on a published row queues nothing (owner acceptance 7)
- [ ] A press inside `recheck_seconds` of the last check — by the creator or
      the sweep — calls nothing and says how many seconds to wait; every
      press ends on the page with its outcome (`D-021` rule 2)
- [ ] Check now is offered only where it can act and never without a usable
      connection with cloud recording on; a stale press is refused with a
      resolution, a vendor failure ends in a sentence rather than an error
      page, and the call goes out with `CHECK_NOW_TIMEOUT_SECONDS`, not the
      sweep's
- [ ] A slug on an action, another Group's ids and the over-cap lock each
      meet the flash the tests name; no Peer route is added and the public
      page is unchanged (owner acceptance 11)
- [ ] Publishing, rejecting and checking change no Episode count, no Peer's
      progress and no certificate (owner acceptance 12)
- [ ] No line under `live.*` says "live now", "has ended", "on its way" or
      "processing"; no line in this task names a vendor; `:seconds` comes from
      config and is never restated
- [ ] `docs/flows/live-sessions.md` carries the three chains and the shared
      throttle; the tinker recipe publishes, rejects and checks by hand
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- `T-143` `ready`, so its names are frozen. This task reads, and never
  redeclares, `RecordingService::search()`, `App\Data\RecordingSearch`,
  `LiveSessionService::SWEEP_TIMEOUT_SECONDS`, `finderFor()`,
  `searchableConnection()`, `creatorStateFor()`, `attachFound()`,
  `markChecked()`, `EpisodeRecording::isHeld()` and
  `episodes.recording_checked_at`; and it asks `T-143` for two edits (see
  Notes). Every one of those is in `T-143`'s draft today and none is settled
  until it is `ready` — anyone's, with `T-143`'s writer.
- `T-141`'s `connections.settings.cloud_recording` key (`bool|null`) is what
  `searchableConnection()` reads and so what `canCheck()` depends on, and
  `ConnectionFactory::zoom(?bool)` is what the tests build; confirm both
  survive `T-141`'s approval — anyone's.
- `T-141`'s Notes ask that Check now also re-read the connected account's
  recording settings before searching, which `T-143` left to this task. It is
  declined in this draft: `T-143`'s `search()` already refreshes the token
  through `ConnectionService::fresh()`, and a second vendor call inside a
  five-second budget is the wrong place to learn that cloud recording was
  turned off. Confirm the decline, or take it and say which call it is — the
  storage owner's.
- Where the creator-side recording list sits after `T-126`, `T-127` and
  `T-143` reconcile (`episode.recordings` or `episode.live.recordings`), so
  the three keys above land in the right map — anyone's.
- `recheck_seconds` 60 is provisional (`D-021`: the throttle numbers are);
  whether it stands for a five-second vendor call — the owner's.

## Re-scope log

None.

## Notes

`T-126`'s draft is edited where its Notes name
`publish(EpisodeRecording $recording, User $by)`: this task takes the Series
and ids as `T-127`'s `hide()` does and keeps `$by` for the log line, so the
five recording actions share one shape.

`T-143`'s draft is edited twice. Its per-recording `heldLine` becomes
`startedLine`, computed for every row rather than only a held one, and its
`live.panel.review.held_line` key becomes `live.panel.recording.started`;
its one assertion on `heldLine` follows. And its candidate rule's docblock
says that `recording_checked_at` is also what a Check now writes, so a press
pushes the sweep's next step out by the same backoff. Nothing else of
`T-143`'s moves: the search, the outcome shape, `SWEEP_TIMEOUT_SECONDS` and
`isHeld()` are read as they stand. One line in `T-143`'s own Notes still
calls this task's timeout `CHECK_TIMEOUT_SECONDS`; its Decisions, its Scope
and the constant's docblock all name `CHECK_NOW_TIMEOUT_SECONDS` and put it
here, and that Notes line is a wording fix there.

`T-128`'s `queueRecordingReady()` docblock says "T-144's sweep"; it means
`T-143`'s, and that is a wording fix there.

Part numbers after picking follow `T-127`'s rule that a label is the row's
`position`: publishing the third of three held rows leaves one visible
recording, labelled `Watch recording` by `T-126`'s single-part rule;
publishing the first and third gives `Watch part 1` and `Watch part 3`. A
creator who wants Part 2 rather than Part 3 hides and pastes; renumbering is
not built.

No reason for a hold is stored (`D-027` has no column), so the panel shows
the start and the length and lets the creator judge. If the pilot shows
creators cannot tell a rehearsal from the class by those two facts, a
`review_reason` column is a decision, not this task.

`check()` resolves the Episode once for the title and `checkNow()` resolves
it again under its own guards; a second indexed read is cheaper than an
outcome that carries a title it did not compute.

`D-021` rule 2 names the creator's Check now `share.series.episodes.check`;
that is `T-094`'s per-Episode storage check. This task's
`share.series.episodes.recordings.check` is the recording search, a different
thing on the same panel, and the two are never one button.

`T-140`'s deliberate re-send bumps `content.recording_publication` and calls
the same `queueRecordingReady()` `publish()` calls here; a publish never
bumps it.

A refusal on a creator POST is a redirect with an error toast, never a 404
status: `AppException::render()` only builds an error page for a GET
(`app/Exceptions/AppException.php:264-288`), and the repository's `404`
assertions on a POST are either `postJson()` (`tests/Feature/Share/UploadTest.php:318-325`)
or a middleware `abort()`. Cases 22 and 23 are written that way. Several
sibling drafts — `T-130`'s cases 20 and 21 among them — still say "404" for
the same shape of case; that is theirs to correct, → `decided: each task's
writer, when it is claimed`.
