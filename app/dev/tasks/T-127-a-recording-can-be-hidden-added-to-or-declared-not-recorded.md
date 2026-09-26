---
id: T-127
title: A recording can be hidden, added to, or declared not recorded, and an overdue session says so
stream: classroom
status: doing
owner: claude
estimate: M
depends: T-126
blocks: T-128, T-133
---

# T-127 — A recording can be hidden, added to, or declared not recorded, and an overdue session says so

> **Draft.** Not specified to the last name yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). Written on 17 September 2026 from `D-026`
> and `D-027`, beside `T-123` to `T-126`, which were being written the same
> day; what has to be reconciled with their finished specs is listed at the
> bottom.

## Why

Today a live Episode is a time and nothing else. Opening one throws
`errors.playback.unsupported_provider` (`app/Services/PlaybackTicketService.php:75-89`),
the Peer's page renders its start and no control
(`resources/js/pages/shared/Show.vue:206-209`), and the creator's row offers
Preview, Move and Remove (`resources/js/pages/share/series/Show.vue:424-498`).
`T-123` to `T-126` give it an end, an edit form, a computed state with Join,
and a recording pasted after class that a Peer watches from the same card.
What none of them covers is the class that goes wrong. Once `T-125` lands,
`stateFor()` answers `overdue` after `recording_wait_hours` and `not_recorded`
when `records` is false or `content['not_recorded_at']` is set, and the card
has a message line for each; what is missing is everything that reaches them.
Nothing writes `not_recorded_at`, so a class that was never recorded — the
host forgot, the recording was local, the plan does not keep one — reads
`not_recorded` only if the creator chose "Live only" before it, and otherwise
sits in `waiting` and then `overdue`; the Peer's `overdue` line says no
recording has been added and names no next step; nothing writes
`episode_recordings.hidden_at`, so a creator who pasted the wrong link has no
way to take it back short of deleting the Episode, which loses every Peer's
`opened_episode_ids` and `completed_episode_ids`; and the creator's panel has
no control for any of it.

`D-026` names the two states that close those gaps, `overdue` and
`not_recorded`; `T-125` declares their arms in `stateFor()`, and `D-027` says
a hidden recording keeps its row so a sweep never finds it twice. This task
builds the writers and the controls that reach them. Afterwards a creator
hides a recording and shows it again, pastes a second link that becomes Part
2 on the same card, and says "There's no recording for this session", which
the card states as final; a session whose creator chose "Live only" reads the
same way once Join closes; and `recording_wait_hours` after the scheduled end
with nothing to watch, the Peer is told no recording has been added and that
an email will come if one is — a promise `T-128` keeps — while the creator
sees the same fact and the two things they can do about it.

## Decisions taken to make this specifiable

**"Not recorded" is a key in the live `content`, written under the row lock,
and a visible recording outranks it.** `content.not_recorded_at` is the key
`D-026` reserved; it is written through `T-124`'s
`LiveSessionService::withLockedContent()` like every other write to a live
Episode's `content`, in the shape `T-124` fixed: the callback receives the
locked, re-read `Episode` (`Closure(Episode): void`), sets what it wants on
it, and the service saves. `stateFor()` answers `ready` before it looks at
the key, because `T-126` placed its `Ready` arm ahead of every clock-based
arm — a recording a Peer can see is a fact and the declaration is a claim —
and `declareNotRecorded()` refuses while a published, unhidden recording
exists (`errors.live.has_recording`, with "hide it first" as the resolution).
The two can therefore coexist only through a stale page, and then the
recording wins.

**This task changes no arm of `stateFor()`; the order is `T-125`'s with
`T-126`'s `Ready` arm where `T-126` put it.** `T-125` declares `cancelled`,
`upcoming`, `open`, `not_recorded` (`records` false, or `not_recorded_at`
set), `waiting` and `overdue`, in that order, and its boundary cases pin
them. `T-126` inserts `Ready` from `Episode::visibleRecordings()` — already
"published and not hidden", so there is nothing here to narrow — after
`cancelled` and before every arm that reads the clock, and its
`test_ready_wins_over_the_clock` pins that: a recording pasted during a
session makes the card `ready`, not `open`, and a "Live only" session with a
recording pasted anyway is `ready`. The order every test and flow-doc line
in this task assumes is therefore cancelled, ready, upcoming, open,
not_recorded, waiting, overdue. `T-125`'s placeholder comment placing
`Ready` after `not_recorded` is the one that loses, because `T-126` is the
task that writes the arm (see Notes).

**A declaration may be made at any time and takes effect when Join closes.**
It has the same meaning as the "Live only" switch (`records` false, `T-123`)
chosen before the class, so it gets the same treatment and no timing refusal
(`D-018`: explained, never refused). Before `ends_at + join_closes_after_minutes`
the card is `upcoming` or `open` by the clock and still offers Join; after it,
`not_recorded` replaces `waiting` and `overdue`. The "Still in the session?
Join again" secondary that `T-125` shows in `waiting` shows in `not_recorded`
on the same condition, because the declaration says nothing about whether the
meeting is still running.

**Hide and unhide are POSTs on the recording with no body and no Form Request,
and Undo is a DELETE on `not-recorded`.** Like `share.series.publish`
(`routes/share/series.php:36-37`), there is nothing to validate; the id in the
path is the whole request. Hiding a hidden row and showing a visible one are
no-ops that flash the same line, so a double click is not an error. The
declaration is a DELETE because it withdraws something the creator made, and
the pair reads as one path with two verbs, which is how the brief names it
(`share.series.episodes.not_recorded` / `.recorded`).

**The over-cap lock applies to all four.** Each changes what Peers see, which
is what the lock exists to stop (`app/Concerns/LocksOverCapSeries.php:40-47`),
so both services `use LocksOverCapSeries` and call `guardSeriesUnlocked()`
first, as `EpisodeService::update()` does (`app/Services/EpisodeService.php:128`).

**The services take the Series and ids, as `EpisodeService` does, and one
public lookup answers "the live Episode with this id in this Series".**
`LiveSessionService::liveEpisodeOf(Series, string)` throws
`errors.series.episode_not_found` for an id outside the Series and
`errors.live.not_live` (`T-126`'s key) for a File, Video or Audio Episode;
`RecordingService` takes `LiveSessionService` by constructor promotion and
uses it, and `T-134`'s cancel and copy use it too. `T-126`'s
`RecordingController::store()` makes the same two checks in two places — an
inline lookup throwing `errors.series.episode_not_found`, then
`RecordingService::guardLive()` — so this task makes `store()` a caller of
`liveEpisodeOf()` as well, and one lookup carries the rule for every creator
action. `paste()` keeps its `Episode` parameter, because the brief fixes that
signature and `T-128` builds on it, and keeps `guardLive()` as its own check,
because tinker and `T-126`'s
`test_it_refuses_a_recording_on_an_episode_that_is_not_live` call `paste()`
directly. The controllers resolve the Series through
`ResolvesShareSeries::seriesById()`, which runs inside group scope, so another
Group's Series is not found rather than forbidden
(`app/Concerns/ResolvesShareSeries.php:41-45`).

**Hide and unhide join `T-126`'s `RecordingController`; the declaration gets a
new `LiveSessionController`.** The two pairs act on different rows. A
recording action belongs beside `store()`; a session action belongs with
`T-134`'s cancel, restore and copy, so `EpisodeController` — which `T-124`
widened — stays the CRUD of any Episode and grows no live arms.

**"A Peer may see it" is `T-126`'s definition, read and never re-declared.**
`EpisodeRecording::isVisible()`, `scopeVisible()` and
`Episode::visibleRecordings()` are `T-126`'s (its Files rows and Code block):
published and not hidden. `T-126`'s `Ready` arm, its Watch gate and its two
props already read them; `declareNotRecorded()` reads `visibleRecordings()`,
and `T-128`'s recipient rule and `T-143`'s candidate rule read the same one
later. This task adds nothing to `EpisodeRecording`.

**The creator's panel reads the same `LiveState` the Peer's card does, from
two keys flat on the Episode row.** `SeriesController::show()` puts `state`
from `stateFor()` and `notRecordedAt` beside `T-123`'s `endsAt`,
`lengthMinutes`, `records` and `joinUrl` on each Episode row; there is no
per-Episode `live` object on the creator's page — `live` there is `T-123`'s
page-level `{defaults, providerLabel, copy}`. Each recording row keeps
`T-126`'s shape, whose `isVisible` is what Hide changes; no `hiddenAt` is
sent, because the panel needs the boolean and nothing else. The panel chooses
its controls from `state`. There is no second state model in Vue, and the
creator sees `overdue` at the same minute the Peer does.

**No page edit on either side, and one key in `SharedController::liveCard()`.**
`LiveSessionPanel.vue` reads its new lines from a page-level `livePanel` prop
through `usePage().props`, exactly as `T-126`'s panel reads `recordingCopy`,
so `share/series/Show.vue` does not change and `T-134` and `T-144` add keys
to the same prop. `LiveSessionCard.vue` reads `copy.overdue` and
`copy.notRecorded`, which `T-125`'s `liveCard()` already builds as flat
strings with no resolution slot; the one line `T-125` left to this task,
`live.state.overdue.resolution`, reaches the card only through a new key
there, `copy.overdueResolution`. So
`app/Http/Controllers/Shared/SharedController.php` is an edit of one key
and one count, `shared/Show.vue` is not edited — `T-126` extended the card's
props the same way without touching the page's `LiveCard` type — and the
stream's claim order on `SharedController` gains this task (see Notes).

**The `overdue` resolution promises an email, and `T-128` keeps the promise.**
"You'll get an email if one is added" is the honest line `D-026` asks for:
Qori has observed nothing, and the one thing it can promise is its own
behaviour. The card's states are this task's, so the sentence is written here,
one task ahead of the mechanism; the stream orders `T-128` next and nothing
between them ships to a real Peer (`T-032`).

**Copy homes.** Peer lines under `live.state.<state>.message|resolution` and
creator panel lines and labels under `live.panel.*`, both in `lang/en/live.php`
(`T-125`'s file), reaching Vue as props; creator flashes in
`lang/en/series.php`; refusals in the `live` group of `lang/en/errors.php`
that `T-125` and `T-126` create.
The number in the creator's `overdue` line is `recording_wait_hours`
interpolated as `:hours`, never restated. No line under `live.*` says "live
now", "has ended", "on its way" or "processing" (`D-026`).

**Parts keep their numbers.** A Peer told "Part 2" in the chat finds Part 2:
the label is the row's `position`, so hiding Part 1 leaves "Part 2" on the
card, not a renumbered "Part 1". `T-126`'s `liveCard()` labels a row "Watch
recording" when `$parts === 1` and counts the visible rows, which would
relabel the survivor "Watch recording"; so `$parts` becomes a count of every
row on the Episode (`$episode->recordings->count()`) — one line in
`SharedController`, listed under Files — and a hidden Part 1 still leaves
"Watch part 2". A recording that never had a sibling still reads "Watch
recording".

**"Add another link" is `T-126`'s form, offered again.** In `ready` the panel
opens the same paste form under that label; in `waiting` and `overdue` it is
"Add the recording link". One form, two labels, both props.

**Check now is not rendered.** It is `T-144`'s and needs a connection and a
finder. A button that does nothing is the dead end `D-021` forbids, so the
panel leaves no placeholder; the brief's "later Check now placeholder" is this
sentence.

**Progress and certificates are untouched.** The four actions write
`episode_recordings.hidden_at` and `episodes.content` and nothing on
`accesses`; `ProgressService::hasFinished()` counts Episodes (`D-024`), which
none of this adds or removes (owner acceptance 12).

## Preconditions

**Data this task verifies against:** a clean database. The feature tests build
a Group with `timezone` `Australia/Brisbane`, its owner and an accepted
Collaborator as `tests/Feature/Series/LiveSessionTest.php:41-60` does, a
published Series, a live Episode through `EpisodeService::add()` with
`$startsAt` one hour ahead (creation refuses a past start,
`app/Services/EpisodeService.php:107-112`), a recording through `T-126`'s
`RecordingService::paste()`, and a Peer through `AccessService::grant()`. The
clock is moved with `$this->travelTo()`: `stateFor()` takes `$now` explicitly
and both of its page callers, `SeriesController::show()` and
`SharedController::liveCard()`, pass `CarbonImmutable::now()`, which honours the
travelled clock. `php artisan wayfinder:generate --with-form` before the Vue
build, so the four new route helpers exist.

**Equipment:** none. A browser for the last acceptance walk, at mobile width
too.

**Spike:** none owed. This task introduces no vendor payload; a link is stored
as pasted and never followed by Qori (`D-025`).

## Scope

**In:**

- `RecordingService::hide()`, `unhide()` and `recordingOf()`; the hide and
  unhide routes on `RecordingController`, whose `store()` resolves its
  Episode through `liveEpisodeOf()` from here on.
- `LiveSessionService::liveEpisodeOf()`, `declareNotRecorded()` and
  `declareRecorded()`; the not-recorded and recorded routes on a new
  `LiveSessionController`. No arm of `stateFor()` changes.
- `Episode::records()` and `isNotRecorded()`.
- The Peer card in `overdue` (message and resolution) and `not_recorded`; the
  grace secondary in `not_recorded`; in `SharedController::liveCard()`,
  `copy.overdueResolution` and `$parts` counting every row so Part numbers
  hold.
- The creator panel's controls per state: Hide / Show again on each row with a
  "Hidden from :peer_plural" label, Add another link in `ready`, There's no
  recording for this session in `waiting` and `overdue`, Undo in
  `not_recorded`, the `overdue` line with its hours.
- `SeriesController::show()`: `state` and `notRecordedAt` flat on each
  Episode row; the `livePanel` page prop.
- The lang lines, two keys in the `errors.live` group, the flow and tinker
  edits.

**Out:**

- The `recording_ready` email and the `session_notices` ledger (`T-128`); the
  creator nudge and the send-status line on the panel (`T-129`).
- Cancel, Undo cancel and Add the next session (`T-134`). `stateFor()` keeps
  the `cancelled` arm `T-125` wrote, and nothing writes `cancelled_at` yet.
- Check now, publish, reject, `needs_review` and the `review` state (`T-143`,
  `T-144`) — no placeholder control.
- Telling Peers about a corrected recording (`T-140`).
- Editing a pasted recording's URL or passcode: hide it and paste again.
- Deleting a recording row. Hiding is the only removal (`D-027`).
- The calendar file (`T-133`).
- Any change to `T-126`'s Watch gate, `PlaybackTicketService::open()`,
  `routes/shared.php` or `shared/Show.vue`: this task adds no Peer route, and
  its `SharedController` edit is one key and one count inside `liveCard()`.
- Materials and the chat card (`T-130` to `T-132`).

## Files

| Path                                                   | Change | Notes                                                                                                    |
| ------------------------------------------------------ | ------ | -------------------------------------------------------------------------------------------------------- |
| `app/Services/LiveSessionService.php`                  | edit   | `liveEpisodeOf()`, `declareNotRecorded()`, `declareRecorded()`; no arm of `stateFor()` changes           |
| `app/Services/RecordingService.php`                    | edit   | `recordingOf()`, `hide()`, `unhide()`; takes `LiveSessionService`; `paste()` and `guardLive()` unchanged |
| `app/Models/Episode.php`                               | edit   | `records()`, `isNotRecorded()`                                                                           |
| `app/Http/Controllers/Share/RecordingController.php`   | edit   | `hide()`, `unhide()` beside `T-126`'s `store()`, whose inline Episode lookup becomes `liveEpisodeOf()`   |
| `app/Http/Controllers/Share/LiveSessionController.php` | new    | `notRecorded()`, `recorded()`; `T-134` adds `cancel()`, `restore()`, `copy()`                            |
| `app/Http/Controllers/Share/SeriesController.php`      | edit   | `state` and `notRecordedAt` flat on each Episode row; the `livePanel` page prop                          |
| `app/Http/Controllers/Shared/SharedController.php`     | edit   | `liveCard()`: `copy.overdueResolution`; `$parts` counts every row                                        |
| `routes/share/episodes.php`                            | edit   | the four routes                                                                                          |
| `resources/js/components/series/LiveSessionPanel.vue`  | edit   | controls per state; the hidden label; Undo                                                               |
| `resources/js/components/series/LiveSessionCard.vue`   | edit   | `overdue` with its resolution, `not_recorded`; the grace secondary in `not_recorded`                     |
| `lang/en/live.php`                                     | edit   | `state.overdue.resolution`, `panel.*`                                                                    |
| `lang/en/series.php`                                   | edit   | four flashes                                                                                             |
| `lang/en/errors.php`                                   | edit   | existing `live` group: `has_recording`, `recording_not_found`                                            |
| `docs/flows/live-sessions.md`                          | edit   | the two writers, the four actions and their routes; the state table is unchanged                         |
| `docs/tinker/live-sessions.md`                         | edit   | hide, show again, declare, undo; moving the clock                                                        |
| `tests/Feature/Series/RecordingStateTest.php`          | new    | 16 cases                                                                                                 |

No config: `recording_wait_hours` and `join_closes_after_minutes` are
`T-123`'s keys, read and never redeclared. No migration, factory or seeder: no
column changes. `qori:reachability` sees the four routes through their
Wayfinder helpers in `LiveSessionPanel.vue`.

## Database

None. `episode_recordings.hidden_at` is `T-126`'s column (`D-027`), and
`content.not_recorded_at` is a key `D-026` reserved in the live `content`
jsonb.

## Code

```php
namespace App\Enums;

// LiveState is T-125's and does not change. The two cases this task makes
// reachable from a creator's action:
//   case NotRecorded = 'not_recorded';
//   case Overdue = 'overdue';
```

```php
namespace App\Models;

class Episode extends Model
{
    /** The creator's "Recorded" switch (D-026, T-123). True when the key is absent. */
    public function records(): bool;
    // return (bool) ($this->content['records'] ?? true);

    /** "There's no recording for this session" has been said, and not undone. */
    public function isNotRecorded(): bool;
    // return ($this->content['not_recorded_at'] ?? null) !== null;

    // T-126's, unchanged and read here: recordings(): HasMany ordered by position;
    // visibleRecordings(): Collection of the loaded rows that isVisible().
}

// EpisodeRecording::isVisible() and scopeVisible() are T-126's and are not
// touched: "published and not hidden" is declared once, there.
```

```php
namespace App\Services;

use App\Concerns\LocksOverCapSeries;
use App\Enums\LiveState;
use App\Exceptions\AppException;
use App\Models\Episode;
use App\Models\Series;
use Carbon\CarbonImmutable;

class LiveSessionService
{
    use LocksOverCapSeries;

    /**
     * T-125's, with T-126's Ready arm, and NOT edited here. The order every
     * case below assumes, cited so a reader need not open two files:
     *   cancelled (T-125; T-134 writes the key) → ready (T-126, from
     *   visibleRecordings(), ahead of every clock arm) → upcoming → open →
     *   not_recorded (T-125: records false, or not_recorded_at set — this
     *   task writes the key) → waiting → overdue. T-143's creator-only
     *   `review` arm lands later, after ready.
     */
    public function stateFor(Episode $episode, CarbonImmutable $now): LiveState;

    /**
     * The Episode with this id inside this Series, and it is live.
     *
     * errors.series.episode_not_found (404) for an id outside the Series;
     * errors.live.not_live (422; T-126's key) for a File, Video or Audio Episode.
     */
    public function liveEpisodeOf(Series $series, string $episodeId): Episode;
    // $episode = $series->episodes()->whereKey($episodeId)->first();
    // if (! $episode instanceof Episode) { throw AppException::notFound('errors.series.episode_not_found', devMessage: "Episode {$episodeId} is not part of series {$series->getKey()}."); }
    // if (! $episode->isLive()) { throw AppException::invalidRequest('errors.live.not_live', devMessage: "Episode {$episodeId} is {$episode->type->value}, not live."); }
    // return $episode;

    /**
     * "There's no recording for this session." Allowed at any time; refused
     * while a Peer can see a recording, because a fact outranks a claim.
     */
    public function declareNotRecorded(Series $series, string $episodeId): Episode;
    // $this->guardSeriesUnlocked($series->group, 'declare a session not recorded');
    // $episode = $this->liveEpisodeOf($series, $episodeId);
    // if ($episode->visibleRecordings()->isNotEmpty()) {
    //     throw AppException::invalidRequest('errors.live.has_recording', devMessage: "Episode {$episodeId} has a visible recording; hide it before declaring the session not recorded.");
    // }
    // return $this->withLockedContent($episode, function (Episode $locked): void {
    //     $locked->content = [...$locked->content, 'not_recorded_at' => CarbonImmutable::now()->toIso8601String()];
    // });

    /** Undo. Idempotent: clearing an absent key still answers the Episode. */
    public function declareRecorded(Series $series, string $episodeId): Episode;
    // $this->guardSeriesUnlocked($series->group, 'undo a not-recorded declaration');
    // $episode = $this->liveEpisodeOf($series, $episodeId);
    // return $this->withLockedContent($episode, function (Episode $locked): void {
    //     $content = $locked->content;
    //     unset($content['not_recorded_at']);
    //     $locked->content = $content;
    // });

    // T-124's, unchanged, cited for the callback shape this task relies on:
    // public function withLockedContent(Episode $episode, Closure $callback): Episode;
    //   @param Closure(Episode): void — DB::transaction(): lockForUpdate() on the
    //   row, re-read it, hand the locked Episode to the callback, save it, return it.
}
```

```php
namespace App\Services;

use App\Concerns\LocksOverCapSeries;
use App\Exceptions\AppException;
use App\Models\Episode;
use App\Models\EpisodeRecording;
use App\Models\Series;

class RecordingService   // T-126's; paste() and its private guardLive() are unchanged
{
    use LocksOverCapSeries;

    public function __construct(private LiveSessionService $sessions) {}

    /** The recording with this id on this Episode. errors.live.recording_not_found (404). */
    public function recordingOf(Episode $episode, string $recordingId): EpisodeRecording;
    // return $episode->recordings()->whereKey($recordingId)->first()
    //     ?? throw AppException::notFound('errors.live.recording_not_found', devMessage: "Recording {$recordingId} is not on episode {$episode->getKey()}.");

    /**
     * Take a recording off the card. The row stays, so a sweep never finds
     * it twice (D-027). Hiding a hidden row is a no-op.
     */
    public function hide(Series $series, string $episodeId, string $recordingId): EpisodeRecording;
    // $this->guardSeriesUnlocked($series->group, 'hide a recording');
    // $recording = $this->recordingOf($this->sessions->liveEpisodeOf($series, $episodeId), $recordingId);
    // if ($recording->hidden_at === null) { $recording->forceFill(['hidden_at' => now()])->save(); }
    // return $recording;

    /** Put it back. Showing a visible row is a no-op. */
    public function unhide(Series $series, string $episodeId, string $recordingId): EpisodeRecording;
    // $this->guardSeriesUnlocked($series->group, 'show a recording again');
    // $recording = $this->recordingOf($this->sessions->liveEpisodeOf($series, $episodeId), $recordingId);
    // if ($recording->hidden_at !== null) { $recording->forceFill(['hidden_at' => null])->save(); }
    // return $recording;
}
```

```php
namespace App\Http\Controllers\Share;

use App\Concerns\ResolvesShareSeries;
use App\Http\Controllers\Controller;
use App\Services\LiveSessionService;
use App\Services\RecordingService;
use App\Support\Terminology;
use Illuminate\Http\RedirectResponse;
use Inertia\Inertia;

class RecordingController extends Controller   // T-126's; these two join store()
{
    use ResolvesShareSeries;

    // store(): T-126's inline lookup (`$series->episodes()->whereKey($episodeId)->first() ?? throw …episode_not_found`)
    // becomes `$sessions->liveEpisodeOf($this->seriesById($seriesId), $episodeId)`, with
    // LiveSessionService $sessions added to its method injection; nothing else in it changes.

    public function hide(string $group, string $seriesId, string $episodeId, string $recordingId, RecordingService $recordings, Terminology $terminology): RedirectResponse;
    // $recordings->hide($this->seriesById($seriesId), $episodeId, $recordingId);
    // Inertia::flash('toast', ['type' => 'success', 'message' => $terminology->line('series.recording_hidden')]);
    // return back();

    public function unhide(string $group, string $seriesId, string $episodeId, string $recordingId, RecordingService $recordings, Terminology $terminology): RedirectResponse;
    // $recordings->unhide(...); flash series.recording_shown; return back();
}

/**
 * What a live session is, as opposed to what it holds: not recorded, and
 * later (T-134) cancelled, restored and copied. Every action mutates, so every
 * parameter is an id; $group is declared because route parameters arrive
 * positionally — see SeriesController.
 */
class LiveSessionController extends Controller
{
    use ResolvesShareSeries;

    public function notRecorded(string $group, string $seriesId, string $episodeId, LiveSessionService $sessions, Terminology $terminology): RedirectResponse;
    // $episode = $sessions->declareNotRecorded($this->seriesById($seriesId), $episodeId);
    // Inertia::flash('toast', ['type' => 'success', 'message' => $terminology->line('series.session_not_recorded', ['title' => $episode->title])]);
    // return back();

    public function recorded(string $group, string $seriesId, string $episodeId, LiveSessionService $sessions, Terminology $terminology): RedirectResponse;
    // $episode = $sessions->declareRecorded(...); flash series.session_recorded with title; return back();
}
```

```php
// App\Http\Controllers\Share\SeriesController::show() — the per-Episode map
// (:158-166) gains two keys beside T-123's endsAt, lengthMinutes, records and
// joinUrl and T-126's recordings. LiveSessionService arrives by method
// injection on show(); stateFor() reads the same loaded `recordings` relation
// T-126's list maps, so no query is added per row.
'state' => $episode->isLive() ? $sessions->stateFor($episode, CarbonImmutable::now())->value : null,
'notRecordedAt' => $episode->isLive() ? ($episode->content['not_recorded_at'] ?? null) : null,
// T-123's records line becomes a caller of the accessor this task adds (a wording change, same value):
'records' => $episode->isLive() ? $episode->records() : null,
// T-126's recordings map is unchanged: id, part, partLabel, sourceLine, url,
// passcode, isVisible — the last is what Hide flips; no hiddenAt is added.

// A top-level page prop beside T-123's `live` and T-126's `recordingCopy`, read
// by the panel from usePage().props; every line with a noun through
// $terminology->line() so :peer_plural is the Group's word:
'livePanel' => [
    'overdue' => $terminology->line('live.panel.overdue', ['hours' => (string) config('qori.live.recording_wait_hours')]),
    'overdueHelp' => $terminology->line('live.panel.overdue_help'),
    'notRecorded' => $terminology->line('live.panel.not_recorded'),
    'hidden' => $terminology->line('live.panel.hidden'),
    'actions' => [
        'hide' => __('live.panel.actions.hide'),
        'unhide' => __('live.panel.actions.unhide'),
        'addAnother' => __('live.panel.actions.add_another'),
        'notRecorded' => __('live.panel.actions.not_recorded'),
        'undoNotRecorded' => __('live.panel.actions.undo_not_recorded'),
    ],
],
```

`LiveSessionPanel.vue` (creator) — `T-123`'s `LiveEpisode` row prop gains
`state: LiveState | null` and `notRecordedAt: string | null`; the lines above
are read as `usePage().props.livePanel as LivePanelCopy`, exactly as `T-126`
reads `recordingCopy`, so the page is not edited. It imports
`{ hide, unhide } from '@/routes/share/series/episodes/recordings'` and
`{ notRecorded, recorded } from '@/routes/share/series/episodes'` (Wayfinder;
`share.series.episodes.not_recorded` exports as `notRecorded`). Each control is
an Inertia `<Form>` posting to the helper's URL with no fields, `:disabled="processing || lock.active"`,
exactly as the Move up form at `share/series/Show.vue:434-456`. What renders,
by `episode.state`:

| `state`            | Panel                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------- |
| `upcoming`, `open` | `T-123`'s fields and `T-124`'s edit, unchanged                                                    |
| `waiting`          | `T-126`'s paste form labelled "Add the recording link"; **There's no recording for this session** |
| `overdue`          | `livePanel.overdue` and `overdueHelp`; the paste form; **There's no recording for this session**  |
| `ready`            | the list; the paste form labelled **Add another link**                                            |
| `not_recorded`     | `livePanel.notRecorded`; **Undo**                                                                 |
| `cancelled`        | `T-134`'s                                                                                         |

The list renders whenever `episode.recordings` is non-empty, whatever the
state: each row `T-126`'s `partLabel`, `sourceLine` and link, then **Hide**
when `isVisible` is true, else the `livePanel.hidden` label and **Show
again**.

`LiveSessionCard.vue` (Peer) — reads `T-125`'s flat `copy`: phase `overdue`
renders `live.copy.overdue` and, under it, `live.copy.overdueResolution`
(the one key this task adds to `liveCard()`), no Join, no Watch;
`not_recorded` renders `live.copy.notRecorded` alone and, while
`Date.now() < Date.parse(live.joinAgainUntil)` as `T-125`'s `waiting`
secondary does, the same "Join again" secondary when `live.joinUrlPresent`.
The card's `copy` prop type gains `overdueResolution: string` on the
component, as `T-126` added `ready`. Part labels are `T-126`'s `label`, built
in `liveCard()` from the row's `part`; the card does not change for them.
Nothing else on the card changes.

```php
// App\Http\Controllers\Shared\SharedController::liveCard() — two lines change.
// Inside T-125's copy, beside 'overdue':
'overdueResolution' => $terminology->line('live.state.overdue.resolution', [], $group),
// and T-126's count, so a surviving Part 2 keeps its number (see Decisions):
$parts = $episode->recordings->count();   // was $episode->visibleRecordings()->count()
// T-125's $records line becomes $episode->records() — a wording change, same value.
```

`docs/flows/live-sessions.md`: the state table is unchanged; its
`not_recorded` row gains the sentence that `declareNotRecorded()` writes the
key, and a "Correcting a recording" section lists the four routes, the
services they call and the lock. `docs/tinker/live-sessions.md`: the four
calls by hand and `Carbon::setTestNow()` to reach `overdue`.

## Copy

| Key                                          | File                 | English                                                                                       |
| -------------------------------------------- | -------------------- | --------------------------------------------------------------------------------------------- |
| `live.state.overdue.resolution`              | `lang/en/live.php`   | You'll get an email if one is added.                                                          |
| `live.panel.overdue`                         | `lang/en/live.php`   | No recording has been added, and it's more than :hours hours since the scheduled end.         |
| `live.panel.overdue_help`                    | `lang/en/live.php`   | Add the link when you have it, or say there's no recording so your :peer_plural stop waiting. |
| `live.panel.not_recorded`                    | `lang/en/live.php`   | Marked as not recorded. Your :peer_plural are told this session wasn't recorded.              |
| `live.panel.hidden`                          | `lang/en/live.php`   | Hidden from :peer_plural                                                                      |
| `live.panel.actions.hide`                    | `lang/en/live.php`   | Hide                                                                                          |
| `live.panel.actions.unhide`                  | `lang/en/live.php`   | Show again                                                                                    |
| `live.panel.actions.add_another`             | `lang/en/live.php`   | Add another link                                                                              |
| `live.panel.actions.not_recorded`            | `lang/en/live.php`   | There's no recording for this session                                                         |
| `live.panel.actions.undo_not_recorded`       | `lang/en/live.php`   | Undo                                                                                          |
| `series.recording_hidden`                    | `lang/en/series.php` | Recording hidden. Your :peer_plural no longer see it.                                         |
| `series.recording_shown`                     | `lang/en/series.php` | Recording shown again.                                                                        |
| `series.session_not_recorded`                | `lang/en/series.php` | :title is marked as not recorded.                                                             |
| `series.session_recorded`                    | `lang/en/series.php` | :title can take a recording again.                                                            |
| `errors.live.has_recording.message`          | `lang/en/errors.php` | This session already has a recording your :peer_plural can see.                               |
| `errors.live.has_recording.resolution`       | `lang/en/errors.php` | Hide it first if it's the wrong one.                                                          |
| `errors.live.recording_not_found.message`    | `lang/en/errors.php` | We couldn't find that recording on this session.                                              |
| `errors.live.recording_not_found.resolution` | `lang/en/errors.php` | Reload the :series and try again.                                                             |

`live.state.overdue.message` and `live.state.not_recorded.message` exist from
`T-125` with the English this task wanted ("No recording has been added for
this session yet." / "This session wasn't recorded.") and are not re-declared;
`errors.live.not_live` is `T-126`'s and is reused by `liveEpisodeOf()`.
`live.state.not_recorded` carries no resolution on purpose: it is final. Every
line with a noun goes through
`Terminology::line()`; the five action labels carry none and are read with
`__()`. `:hours` is `config('qori.live.recording_wait_hours')`. No line above
says "live now", "has ended", "on its way" or "processing", and no article
sits directly before a placeholder (`TerminologyTest::test_no_lang_line_puts_an_article_before_a_noun`).

## Routes

| Verb   | Path                                                                                | Name                                      | Action                                     |
| ------ | ----------------------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------ |
| POST   | `/g/{group}/series/{seriesId}/episodes/{episodeId}/recordings/{recordingId}/hide`   | `share.series.episodes.recordings.hide`   | `Share\RecordingController::hide`          |
| POST   | `/g/{group}/series/{seriesId}/episodes/{episodeId}/recordings/{recordingId}/unhide` | `share.series.episodes.recordings.unhide` | `Share\RecordingController::unhide`        |
| POST   | `/g/{group}/series/{seriesId}/episodes/{episodeId}/not-recorded`                    | `share.series.episodes.not_recorded`      | `Share\LiveSessionController::notRecorded` |
| DELETE | `/g/{group}/series/{seriesId}/episodes/{episodeId}/not-recorded`                    | `share.series.episodes.recorded`          | `Share\LiveSessionController::recorded`    |

All four in `routes/share/episodes.php`, inside `routes/share.php`'s `auth`,
`verified`, `group` group with prefix `g/{group}` and name prefix `share.`
(`routes/share.php:24-27`). Ids throughout: every one mutates. No Peer route.

## Tests

**New: `tests/Feature/Series/RecordingStateTest.php` — 16 cases**
(`RefreshDatabase`; private helpers `scene()` as
`LiveSessionTest.php:41-60` with `timezone` `Australia/Brisbane`,
`liveEpisode(Series $series, CarbonImmutable $startsAt, bool $records = true): Episode`
through `EpisodeService::add()` with `lengthMinutes: 60`,
`pasted(Episode $episode): EpisodeRecording` through `RecordingService::paste()`,
`peer(Series $series): User` through `AccessService::grant()`; a refusal on a
POST is asserted the way `tests/Feature/Access/SeriesAccessCodeTest.php:157`
asserts one — `assertRedirect()` then
`assertSessionHas(SessionKey::FLASH_DATA, …)` on the error toast's message;
a state is asserted on `app(LiveSessionService::class)->stateFor($episode->fresh(), CarbonImmutable::now())`
after `$this->travelTo()`)

1. `test_hiding_a_recording_takes_the_card_out_of_ready` — paste; POST hide;
   `hidden_at` set; at end + 1 h the state is `Waiting`; the Peer's page has
   `series.episodes.0.live.state` `waiting` and `live.recordings` empty.
2. `test_showing_a_hidden_recording_again_restores_ready` — hide, then POST
   unhide; `hidden_at` null; `Ready`; the Peer's page lists it again.
3. `test_a_hidden_recording_cannot_be_watched` — hide; the Peer's GET on
   `shared.episodes.open` with `?recording=` answers 404 with
   `errors.live.recording_unavailable.message` (`T-126`'s gate), never a
   redirect to the URL and never a 403.
4. `test_hiding_one_part_leaves_the_other_with_its_number` — two pastes;
   hide Part 1; `Ready`; the Peer's `live.recordings` holds one row whose
   `part` is 2 and whose `label` is `Watch part 2`, not `Watch recording`.
5. `test_a_session_can_be_declared_not_recorded` — POST not-recorded;
   `content.not_recorded_at` set; at end + 1 h the state is `NotRecorded`;
   the Peer's page has `live.state` `not_recorded`; the success toast is
   `series.session_not_recorded` with the title.
6. `test_a_declaration_before_the_end_leaves_join_until_it_closes` — declare
   at start − 1 h; `Upcoming`; at the start `Open`; at end + 16 min
   `NotRecorded`.
7. `test_undo_clears_the_declaration` — DELETE; the key is absent; `Waiting`;
   a second DELETE redirects with the same success toast and no error.
8. `test_a_live_only_session_reads_not_recorded_after_its_end` — `records`
   false; `Open` during; `NotRecorded` at end + 16 min; still `NotRecorded`
   at end + 49 h, never `Overdue`.
9. `test_a_visible_recording_refuses_the_declaration` — paste, then POST
   not-recorded; the error toast is `errors.live.has_recording.message`;
   `not_recorded_at` absent; hide it and the same POST succeeds.
10. `test_a_session_with_nothing_after_the_wait_is_overdue_on_both_pages` — no
    recording; at end + 48 h + 1 min the state is `Overdue`; the Peer's page
    has `live.state` `overdue` and `live.copy.overdueResolution` equal to
    the Group's `live.state.overdue.resolution`; the creator's page has
    `series.episodes.0.state` `overdue` and the page prop `livePanel.overdue`
    containing `48`.
11. `test_a_non_live_episode_has_no_session_to_declare` — a File Episode;
    POST not-recorded; the error toast is `errors.live.not_live.message`.
12. `test_a_slug_on_a_recording_action_does_not_resolve` — POST hide with the
    Series slug as `seriesId`; 404; `hidden_at` still null.
13. `test_another_groups_session_is_not_found` — a second Group's owner posts
    hide under their own `g/{group}` with the first Group's Series, Episode
    and recording ids; 404; the row is untouched.
14. `test_the_over_cap_lock_refuses_all_four` — the group of
    `OverCapLockTest::overCapGroup()` (`tests/Feature/Series/OverCapLockTest.php:59-72`);
    hide, unhide, not-recorded and recorded each answer the
    `errors.series.locked_over_cap.message` toast.
15. `test_hiding_and_declaring_leave_progress_and_certificates_alone` — a
    Series with the live Episode alone; the Peer completes it through
    `ProgressService::completeFor()` and holds a `certificate_code`; hide the
    recording, then declare the session not recorded;
    `completed_episode_ids`, `certificate_code` and `Series::episodeCount()`
    unchanged (owner acceptance 12).
16. `test_the_creator_page_lists_hidden_recordings_and_the_declaration` —
    hide and declare; the creator's page has
    `series.episodes.0.recordings.0.isVisible` false,
    `series.episodes.0.notRecordedAt` non-null and the page prop
    `livePanel.hidden` equal to the Group's `live.panel.hidden`.

**Changed:** none expected. `T-126`'s hidden-recording case sets `hidden_at`
by hand and stays green; its two part-label cases have no hidden row, so the
all-rows `$parts` count answers what the visible count did; its `store()`
cases meet the same `episode_not_found` and `not_live` keys from
`liveEpisodeOf()`; `T-125`'s boundary cases assert the clock arms, which this
task does not move.

Total: 16 new cases.

## Acceptance

- [ ] A creator with a pasted recording hides it, the card leaves `ready` on
      both pages within the same minute, the Peer's Watch link is gone and a
      saved one answers the not-available page; Show again brings it back
- [ ] A second link becomes Part 2 on the same card, and hiding Part 1 leaves
      "Part 2" on the Peer's card, not "Part 1"
- [ ] "There's no recording for this session" on a class already held makes
      the Peer's card final — no Join, no Watch, no resolution — and Undo
      returns it to `waiting`; the same declaration on a session still ahead
      leaves Join in place until Join closes
- [ ] A session created with "Live only" reads `not_recorded` once Join
      closes, without the creator doing anything
- [ ] 48 hours after the scheduled end with nothing visible, the Peer reads
      that no recording has been added and that an email will come if one is;
      the creator reads the same fact with the hours interpolated, and has
      Add the recording link and There's no recording for this session, and
      no control that does nothing (owner acceptance 9: no recording and a
      local-only recording each show a truthful status and a way out)
- [ ] Neither hiding nor declaring changes an Episode count, a Peer's
      progress or a certificate (owner acceptance 12); a wrong-tenant creator
      and a slug on an action each meet a 404, and the over-cap lock refuses
      all four
- [ ] No line under `live.*` says "live now", "has ended", "on its way" or
      "processing"; every number on the panel comes from `config('qori.live')`
- [ ] `docs/flows/live-sessions.md` carries the four actions and names the
      two writers, with its state table unchanged; the tinker recipe reaches
      `overdue` with the clock moved
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~`T-126` `ready`, so `RecordingService`, `EpisodeRecording`,
  `RecordingController` and the Peer prop's recording shape are frozen: this
  draft assumes `T-126`'s creator controller is
  `App\Http\Controllers\Share\RecordingController` with `store()`, that
  `EpisodeRecording` casts `hidden_at` and `published_at` to `datetime`, and
  that `Episode::recordings(): HasMany` exists — anyone's, with `T-126`'s
  writer.~~ **Answered 26 September 2026:** `T-126` is `done` (qori
  `e40e651`), and all three hold; where its shapes differ from what this
  draft read, the Re-scope log says so.
- ~~`T-124`'s `withLockedContent()` callback shape: this draft assumes the
  callback receives the re-read `content` array and returns the array to
  save; if it receives the locked `Episode` instead, the two closures above
  are rewritten and nothing else changes — anyone's, from `T-124`'s finished
  Code section.~~ **Answered 18 September 2026:** `T-124` is `ready` and
  declares `@param Closure(Episode): void` — the callback receives the
  locked, re-read Episode and the service saves. The two closures above use
  that shape.
- ~~`T-125`'s `live.copy` prop shape on the Peer page: this draft assumes it
  carries every `live.state.*` line keyed by state
  (`copy.states.overdue.message`), so the two new states need no
  `SharedController` edit; if it carries only the current state's line,
  `app/Http/Controllers/Shared/SharedController.php` joins the Files table as
  an edit and the stream's claim order gains this task on that file — anyone's.~~
  **Answered 18 September 2026** from `T-125`'s Code: `liveCard()` builds
  `copy` as flat strings (`copy.overdue`, `copy.notRecorded`) with no
  resolution slot, so `SharedController` is listed as an edit of one key,
  `copy.overdueResolution`, and the claim order gains this task (Notes).
- ~~Whether `T-125`'s `lang/en/live.php` already carries `live.state.overdue.*`
  and `live.state.not_recorded.*` (its brief says "every state line"): if so,
  this task edits their English to the lines above rather than adding them,
  and the Copy table's first three rows are marked edit — anyone's.~~
  **Answered 18 September 2026:** `T-125`'s Copy table carries both message
  lines with the same English; the two rows are removed here and only
  `live.state.overdue.resolution` is this task's.
- ~~Whether `T-123`'s `Episode` gained a `records()` accessor; if so the Code
  section cites it instead of adding one — anyone's.~~ **Answered 18
  September 2026:** `T-123`'s Files row gives `Episode` only `isCancelled()`
  and `lengthMinutes()`; its `records()` is `StoreEpisodeRequest`'s. This task
  declares `Episode::records()`, and the two existing readers become its
  callers (Notes).
- ~~Whether `errors.live.not_live` is first thrown by `T-126`'s `paste()`, in
  which case this task reuses the key and drops its row — anyone's, with
  `T-126`'s writer.~~ **Answered 18 September 2026:** `T-126`'s
  `RecordingService::guardLive()` throws it and its Files row creates the key;
  the row is dropped here and `liveEpisodeOf()` reuses it.

## Re-scope log

**2026-09-26 — reconciled with `T-125` and `T-126` as built.** Written on
17–18 September beside four drafts; three of them are now code (qori
`94dd6c9` and `e40e651`), and these things here read them otherwise:

- **The arm order.** Decisions and the Code block say `T-126` put `ready`
  "after `cancelled`, before every clock arm", citing its
  `test_ready_wins_over_the_clock`. `T-126`'s own Decisions said the opposite
  — Join keeps winning until its window closes — and that is what was built,
  its test 14 corrected to match: `cancelled`, `upcoming`, `open`, `ready`,
  `not_recorded`, `waiting`, `overdue`. Nothing this task builds depends on
  the difference: every state case below reads a clock after Join closes, or
  test 6's before-and-during, where no recording exists.
- **The card's copy.** "`T-125`'s flat `copy.overdue` / `copy.notRecorded` with
  no resolution slot" is not what `T-125` built: `copy.states` is keyed by
  state, each `{ message, resolution? }`, and the card already renders a
  `resolution` under the message. So `live.state.overdue.resolution` reaches
  the card as `copy.states.overdue.resolution` — one key in `liveCard()`.
  Test 10 reads that path.
- **The panel's copy.** `livePanel` was to be a page-level prop "exactly as
  `T-126`'s panel reads `recordingCopy`"; `T-126` put its lines inside the
  existing `live.copy` instead (`live.copy.recording`), which the page already
  hands the panel in both modes. The same inner keys go there, as
  `live.copy.panel`, so there is one place the panel's copy comes from and no
  `usePage()` read for copy. Tests 10 and 16 read `live.copy.panel.*`.
- **`withLockedContent()`'s callback.** The Before bullet answered on
  18 September says `Closure(Episode): void`; `T-124` built
  `Closure(array $content, Episode $locked): array` — the callback returns the
  content to save. The two closures are written in that shape, and
  `declareNotRecorded()` reads the visible recordings inside the lock, where a
  paste (which locks the same row) cannot slip in between the check and the
  write.
- **Nouns in the three refusals.** `errors.live.not_live`, `has_recording` and
  `recording_not_found` carry `:episode`, `:peer_plural` and `:series`, and an
  `AppException` fills only the replacements it is given, so each is thrown
  with the Group's vocabulary (`Terminology::for($group)->replacements()`), as
  `RecordingService::guardLive()` already does.
- **A live row with no start.** `T-125` found these exist and gave
  `LiveSessionService::isScheduled()`; `stateFor()` throws for one. The
  creator's `state` key is `stateFor()` only behind `isScheduled()`, else null,
  so such a row cannot 500 the creator's page.
- **The Wayfinder names.** Wayfinder keeps a route name's underscore, so
  `share.series.episodes.not_recorded` exports as `not_recorded`, not
  `notRecorded`; the panel imports it under an alias.
- **The panel's controls are not forms.** The live row renders inside the
  page's `<p>` (`T-126` found this for its paste form), and a server-rendered
  `<form>` there is torn out of the paragraph by the HTML parser. Hide, Show
  again, the declaration and Undo are buttons that post through Inertia's
  router, disabled while one is in flight or the Group is over its cap.
- **`T-126`'s paste form** is a toggle on every live row with no recording,
  whatever the clock says (its Decisions). This task keeps that, labels it
  "Add another link" once a Peer can see one, and takes it off a row that has
  been declared not recorded — Undo first — rather than hiding it in
  `upcoming` and `open` as the panel table's first row implies.
  `RecordingController::store()` already resolves its Episode through
  `ResolvesShareSeries::episodeIn()`, not an inline lookup; it becomes a
  caller of `liveEpisodeOf()` as the Code says.

Three things the spec did not decide, decided here because a person sees them:

- **A declared session reads "Live only" on both badges.** The Decisions give
  the declaration "the same meaning as the 'Live only' switch"; left alone,
  the Peer's card would print "Recorded" beside "This session wasn't
  recorded.", and its own tick would move a declared session to `waiting`
  when Join closes. `liveCard()`'s `records` is `records()` and not
  `isNotRecorded()`; the creator's row badge reads the same, while its Edit
  form keeps the switch's own value. Undo puts both back.
- **"Join again" in `ready` too** (`T-126`'s report, Found, not fixed). The
  route admits Join until the grace ends whatever the recording, so a class
  that runs over keeps its way back in when Part 1 is already up; the card
  shows the secondary above the Watch list on the same condition as in
  `waiting` and `not_recorded`.
- **A "Live only" session after its end** reads `not_recorded` with no
  declaration to undo: the panel offers no Undo there (it would clear nothing)
  and keeps `T-126`'s paste toggle, because a recording pasted anyway is
  `ready`.

## Notes

Edits to other drafts this spec implies:

- `T-126`'s draft is edited to: `RecordingController::store()`'s inline
  Episode lookup is replaced by `LiveSessionService::liveEpisodeOf()` when
  this task lands, `paste()` and `guardLive()` stay as written, and
  `liveCard()`'s `$parts` counts every row from this task on.
- `T-125`'s draft is edited to: its placeholder comment in `stateFor()`
  ("T-126 inserts Ready here", after `not_recorded`) and its Notes line
  saying `T-126` inserts `ready` "between `not_recorded` and `waiting`" read
  as `T-126` placed the arm — after `cancelled`, before every clock arm — so
  the three specs give one order. Its `liveCard()` `$records` line becomes a
  call to `Episode::records()`, a wording change.
- `T-123`'s `SeriesController` line
  `'records' => (bool) ($episode->content['records'] ?? true)` becomes a call
  to `Episode::records()` in this task, a wording change with the same value;
  `T-123` is `ready` and its spec is not edited for it.
- `T-144`'s Code comment "T-126's model; T-127 added isVisible() and
  scopeVisible()" and its line "`T-127`'s `isVisible()`" are edited to name
  `T-126`, which declares both.
- `docs/planning/streams/classroom.md`'s claim order for
  `app/Http/Controllers/Shared/SharedController.php` gains this task between
  `T-125` and `T-131` (one key and one count in `liveCard()`).

`T-128` keeps the promise this task's `live.state.overdue.resolution` makes.
Between this task landing and `T-128`, the sentence is one task ahead of its
mechanism; the stream orders `T-128` next, `T-032` stands before any Peer
reads it, and the line is written here because the card's states are this
task's. `T-129` nudges the creator at `creator_nudge_hours`, which is what
makes "if one is added" likely rather than a hope.

`T-134` adds `cancel()`, `restore()` and `copy()` to
`LiveSessionController` and reuses `liveEpisodeOf()`; its draft is edited to
name that controller rather than `EpisodeController`.

`T-143`'s `review` state is creator-only and sits after the `ready` arm of
`stateFor()`; its candidate rule skips an Episode that `isNotRecorded()` —
this task's helper — or has a visible recording — `T-126`'s
`visibleRecordings()`. `T-128`'s recipient rule reads `T-126`'s `visible()`.

The stream's claim order lists this task on `LiveSessionPanel.vue`,
`LiveSessionCard.vue` and `lang/en/live.php` and on neither page; this spec
honours that by reading page-level props from `usePage().props` in the panel
and flat `copy` keys in the card. `SharedController` is the one addition to
the claim order, above. `SeriesController.php` is not in the claim order at
all and is listed here as an edit because the creator's state has to come
from `stateFor()`; `T-126` edits it first for the recordings list, and the
two are serialised by the dependency.

`docs/flows/README.md:42-43` still says the live-episode integration has no
flow file; `T-125` creates `docs/flows/live-sessions.md` and rewrites that
line, so this task edits the file and not the README.
