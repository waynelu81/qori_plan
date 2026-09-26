---
id: T-134
title: A creator can cancel a live Episode, undo it, and add the next session
stream: classroom
status: doing
owner: claude
estimate: M
depends: T-129
blocks: T-135, T-138
---

# T-134 — A creator can cancel a live Episode, undo it, and add the next session

> Specified on 18 September 2026 from `D-026` and `D-028`; first on the slip
> list after the manual-replay checkpoint (`D-031`). Reconciled with `T-124`
> to `T-129` as built on 27 September 2026 — the Re-scope log says what
> changed, and it overrides the sketches below where they differ.

## Why

After `T-123` to `T-129` a live Episode has an end, an inline edit form, a
computed state with Join, a recording on the same card and the notices — and
no way to be called off. `content.cancelled_at` is the key `D-026` reserved
for it, and nothing writes it: `Episode::isCancelled()` reads it (`T-123`),
`LiveSessionService::stateFor()` answers `Cancelled` on it as its first arm
and `joinAllowed()` refuses on it (`T-125`), and
`SessionNoticeService::creatorNudgeCandidates()` skips it (`T-129`), all
without a caller. So a class the creator has to call off has two choices. Leave
it, and at 8:45 the card offers Join to every Peer, at 10:15 it says a
recording will be added, two days later it reads overdue, and the Group owner
is nudged about a class that never ran. Or Remove it
(`resources/js/pages/share/series/Show.vue:481-497`), which deletes the row and
with it the Episode's id from every Access's `opened_episode_ids` and
`completed_episode_ids`, with no undo but re-adding. And a ten-week course is
ten passes through the New Episode form (`LiveSessionPanel.vue` in `form`
mode, `T-123`): the same link, length and switch typed ten times when nine of
them are the same as the last.

`D-026` fixes both: the live `content` keeps `cancelled_at`, and "Add the next
session" copies an Episode with its link seven days on. Afterwards every live
row on the creator's page carries **Cancel session**, which writes
`cancelled_at` under the row lock and nothing else; the card reads cancelled
on both pages within the minute, Join is refused inside its window and lands
on the card, no recording line shows, no nudge is queued; **Undo** clears the
key and puts back exactly what was there. **Add the next session** makes a
new live Episode at the end of the Series at the same local time in the
Group's zone a week on — or the first such slot still ahead — with this one's
title, provider, join link, length and Recorded switch, through
`EpisodeService::add()` so the plan's cap, the over-cap lock and the timezone
guard apply once. No email goes out about any of it this sprint (`D-028`):
`T-138` sends `session_cancelled` to the Peers who were reminded, and edits
`cancel()` to do it.

## Decisions taken to make this specifiable

**Cancel and Undo are one key, `content.cancelled_at`, written under the row
lock through `withLockedContent()`, and nothing else on the row changes.**
`D-026` names the key and requires the lock on every write to a live
Episode's `content`; `T-124`'s callback receives the locked, re-read Episode
(`Closure(Episode): void`) and this task uses that shape, not the array shape
`T-127`'s draft assumed. `starts_at`, `ends_at`, `schedule_version`, the
recordings and the materials are untouched, so Undo restores the row exactly
— including a hidden recording, which stays hidden.

**Cancel is refused while a Peer can see a recording, with `T-127`'s key.**
`LiveSessionService`'s "a fact outranks a claim" rule for `declareNotRecorded()`
holds here for the same reason: a class with a visible recording was held, and
saying it was cancelled would hide the recording from every Peer behind a
state. `errors.live.has_recording` already carries the resolution ("Hide it
first if it's the wrong one"), so no new line is written. The check runs
inside `withLockedContent()`'s callback, on the locked row: `T-127`'s
`declareNotRecorded()` checks before it takes the lock, which leaves a gap in
which a `paste()` lands a visible recording on a session that is then
cancelled — the state the refusal exists to prevent — and the callback here
already holds the locked Episode, so the check moves inside and the throw
rolls the transaction back. Cancelling a cancelled session and restoring one
that is not cancelled are no-ops that answer the same success flash, so a
double click is not an error.

**Otherwise Cancel is allowed at any time, `open` included, with no
confirmation dialog.** A host calling a class off at 8:50 is the case the
button exists for, and Undo is the confirmation: a cancel is reversible in
one click, which a dialog would only slow down. Join is refused from the same
instant because `joinAllowed()` already reads `isCancelled()` (`T-125`).

**Join on a cancelled session is `BLOCKED_NOT_OPEN`, as `T-125` built it; no
third blocked state is added.** The toast `live.join.not_open` says Join is
not open for that Episode and that its time is below, both true; the anchor
lands on the card, and the card's own line says the session was cancelled.
`D-020` puts the sentence on the page, not in the redirect, and a
`BLOCKED_CANCELLED` arm would touch `PlaybackTicketService` and
`OpenEpisodeController` for one word the card already says.

**The next session is the same wall-clock time in the Group's zone,
`NEXT_SESSION_DAYS` later, stepped forward by the same amount until it is
ahead of now.** A 9:00 AEST class on 1 October 2026 in Melbourne is 23:00 UTC
the day before; 168 hours later is 8 October 10:00 AEDT, because daylight
saving starts on 4 October. `addDays()` on a zoned `CarbonImmutable` keeps the
hour across the change; adding hours does not. `EpisodeService::add()`
refuses a past start (`app/Services/EpisodeService.php:107-112`, kept by
`T-123` with `creating: true`), so a copy taken after the class ran would be
the predictable refusal the beta gate forbids; "the next session" after a
class that has already happened is the next weekly slot still ahead. The
number is `LiveSessionService::NEXT_SESSION_DAYS`, a class constant
interpolated into the help line as `:days` and written into no sentence.
`D-026` says every `qori.live` number is in `config('qori.live')`; this is the
one kept out of config on purpose, settled by the sprint's cross-task
reconciliation of 18 September 2026, because `config/qori.php` is `T-123`'s
alone in this stream (the stream's claim order names its only two
exceptions, `T-125`'s reachability row and `T-138`'s plan key) and this is
one number one method reads.

**`copy()` goes through `EpisodeService::add()`, resolved from the container
inside the method.** The cap (`guardEpisodeLimit()`, `EpisodeService.php:268-289`),
the lock and the timezone guard then apply once, in the one place they live.
`EpisodeService` takes `LiveSessionService` by constructor (`T-124`), so the
reverse dependency by constructor would be a cycle the container cannot
build; `app(EpisodeService::class)` inside `copy()` is the same move
`EpisodeService::guardLiveSessionTime()` makes for `Terminology`
(`EpisodeService.php:94`).

**What is copied: the title verbatim, the provider, `join_url`, `records`
and the length. Nothing else.** The brief names the link, the length, the
switch and the title. The copy has no `cancelled_at`, `not_recorded_at`,
`schedule_version`, `meeting_id` or `occurrence_id`, no recordings, no
materials (the next class has its own, `T-130`) and `is_preview` false — a
preview is chosen for one Episode, not inherited (`D-024`). It goes to the
end of the Series, which `add()` does. The source may be in any state, a
cancelled one included: this week's class cancelled and next week's added is
the common case.

**"Add the next session" is on every live row; "Cancel session" on every live
row except `ready` and `cancelled`; Undo stands where Cancel stood in
`cancelled`.** A course is built after each class as often as before the
first, so the copy is never hidden by state. `ready` would be refused, so the
button is not offered; a stale page's POST meets the service's refusal.

**`copy(Series, Episode)` takes the model; the controller resolves it with
`liveEpisodeOf()`.** The brief's signature. `cancel()` and `restore()` take
`(Series, string $episodeId)` as `T-127`'s `declareNotRecorded()` does,
because their controller actions hold an id; `copy()` takes the Episode
because a tinker caller and `T-135` hold one. A non-live Episode, one outside
the Series or one with no start is an `InvalidArgumentException`: a
programmer error, since the controller passes what `liveEpisodeOf()` returned
and the form never makes a live Episode without a start.

**The copy's flash says the new start back in the Group's zone, through a
shared concern.** `T-124` wrote the format once as
`EpisodeController::whenFor()`, private. This task moves it unchanged into
`App\Concerns\FormatsSessionStart` and both controllers `use` it, so the hour
is formatted one way (`CLAUDE.md`: lookups and formats shared through a
concern, not duplicated per controller). The other two flashes name the title
and nothing else.

**The Peer card's `cancelled` line is one message with no resolution.** Final,
so `D-026`'s rule for `not_recorded` applies: no hopeful next step. The card
shows the time and that line and nothing else — no Recorded badge, no Join,
no Join again, no Watch. The materials on the row are `T-131`'s and stay
listed, which is what the owner's proposal asked for.

**Both components take their lines as props; `SharedController::liveCard()`
gains one key and `SeriesController::show()` five.** No inline English in Vue
(`CLAUDE.md`), and no page edit on either side: the panel receives the whole
`livePanel` object (`T-127`) and the card the whole `copy` object (`T-125`).
The stream's claim order carries this task on
`app/Http/Controllers/Shared/SharedController.php` (one key in `liveCard()`,
after `T-133`) and on `LiveSessionCard.vue` (between `T-133` and `T-138`),
and not on `app/Services/EpisodeService.php`.

**No email, no reminder rows, no calendar change here.** `D-028`: a
cancellation sends `session_cancelled` only to holders of a `day_before` row,
which `T-138` builds and adds to `cancel()`; `T-133` reads `isCancelled()` for
`STATUS:CANCELLED` and its `SEQUENCE` is `schedule_version`, which a cancel
does not bump; `T-135` puts "Copy message for your chat" beside Undo. A test
pins `Notification::assertNothingSent()` so the promise in the panel's line
is true until `T-138` rewrites it.

**The three actions are id-only, over-cap-locked, and on
`LiveSessionController`.** `T-127`'s decision for session actions;
`guardSeriesUnlocked()` is the first line of `cancel()` and `restore()`, as
`EpisodeService::update()` does (`EpisodeService.php:128`), and `copy()`
inherits the guard from `EpisodeService::add()`, which it calls, so it has no
line of its own — a second guard there would be the same refusal twice.
`ResolvesShareSeries::seriesById()` runs inside group scope, so another
Group's Series is not found rather than forbidden
(`app/Concerns/ResolvesShareSeries.php:41-53`); on a POST or DELETE that
answer is a redirect back with the `errors.series.not_found` toast, never a
status page (`app/Exceptions/AppException.php:264-283`).

**`app/Services/EpisodeService.php` is not touched.** The stream's claim order
does not list this task on it; nothing here needs a change there, and
`copy()` is a caller of `add()`, not an edit to it.

**The daylight-saving week is asserted with literals.** As
`tests/Feature/Series/LiveSessionTest.php:112-134` does, so the test disagrees
with the code rather than repeating it.

## Preconditions

**Data this task verifies against:** a clean database. The tests build a
Group on plan `start` with `timezone` `Australia/Melbourne`, its owner as an
accepted Collaborator and a Series, as
`tests/Feature/Series/LiveSessionTest.php:41-60` does; travel the clock to
`2026-09-20T00:00:00Z` first, so a live Episode starting
`CarbonImmutable::parse('2026-10-01T09:00:00', 'Australia/Melbourne')->utc()`
(`2026-09-30T23:00:00+00:00`) with `lengthMinutes: 60` and content
`['join_url' => 'https://zoom.us/j/91827405566', 'records' => true]` passes
`EpisodeService::add()`'s past-start refusal; a Peer through
`AccessService::grant()`; a recording through `T-126`'s
`RecordingService::paste()` and `T-127`'s `hide()`; the over-cap scene as
`OverCapLockTest::overCapGroup()` builds it
(`tests/Feature/Series/OverCapLockTest.php:59-72`) but on `scene()`'s Group,
which has `timezone` `Australia/Melbourne` — `overCapGroup()` creates its
Group with no zone, and `EpisodeService::add()` refuses a live Episode for a
Group with no chosen zone (`errors.series.timezone_required`,
`app/Services/EpisodeService.php:88-96`) — so the live Episode and a second
Series are added on plan `start` before `plan` is forced to `free`; nudge
candidates read inside
`CurrentGroup::runFor()` as `T-129`'s tests do. `php artisan wayfinder:generate --with-form`
before the Vue build, so the three route helpers exist.

**Equipment:** a browser at phone width and at desktop width, for the
acceptance walk: the three controls on a live row without pushing Move and
Remove off the screen, and the Peer's card reading cancelled. No vendor call,
no mailbox, no credentials.

**Spike:** none owed. Nothing here reads a vendor payload; the join link is
copied as a string and never followed (`D-025`).

## Scope

**In:**

- `LiveSessionService::cancel()`, `restore()`, `copy()`, `nextSlotFor()` and
  `NEXT_SESSION_DAYS`.
- `LiveSessionController::cancel()`, `restore()`, `copy()` and the three
  routes.
- `App\Concerns\FormatsSessionStart`, used by `EpisodeController` and
  `LiveSessionController`.
- `SeriesController::show()`: `cancelledAt` on the live prop; the five
  `livePanel` lines. `SharedController::liveCard()`: the `cancelled` line.
- `LiveSessionPanel.vue`: Cancel session, Undo, Add the next session with its
  help line, the `cancelled` arm. `LiveSessionCard.vue`: the `cancelled` arm.
- The six lines in `lang/en/live.php` and the three flashes in
  `lang/en/series.php`.
- `docs/flows/live-sessions.md`, `docs/flows/series.md`,
  `docs/tinker/live-sessions.md`.

**Out:**

- `session_cancelled` to reminded Peers, `day_before` rows, and the rewrite of
  the panel's "no email goes out" line once one does (`T-138`).
- `STATUS:CANCELLED` in the calendar file (`T-133`).
- "Copy message for your chat" in `cancelled` and the chat lines (`T-135`);
  what the public page shows a buyer for a cancelled session (`T-135` picks
  the next session and skips a cancelled one; `PublicSeriesController` is
  not edited here).
- A cancelled session's recordings: they are not hidden, deleted or
  re-numbered; hiding is `T-127`'s and stays the only removal (`D-027`).
- Rescheduling: a cancel does not move `starts_at` or bump
  `schedule_version`; a creator who wants the class on another day edits it
  (`T-124`) instead.
- Copying more than one session at once, a recurrence rule, or a copy at any
  interval but the constant.
- Copying materials, a chat card or a recording onto the next session
  (`T-130`, `T-132`).
- A third blocked state on Join, or any change to `PlaybackTicketService`,
  `OpenEpisodeController`, `routes/shared.php` or `shared/Show.vue`.
- `share/series/Show.vue`, `app/Services/EpisodeService.php`,
  `config/qori.php` — none is edited.

## Files

| Path                                                   | Change | Notes                                                                                |
| ------------------------------------------------------ | ------ | ------------------------------------------------------------------------------------ |
| `app/Services/LiveSessionService.php`                  | edit   | `NEXT_SESSION_DAYS`; `cancel()`, `restore()`, `copy()`, `nextSlotFor()`              |
| `app/Http/Controllers/Share/LiveSessionController.php` | edit   | `cancel()`, `restore()`, `copy()` beside `T-127`'s `notRecorded()` and `recorded()`  |
| `app/Concerns/FormatsSessionStart.php`                 | new    | `whenFor()`, moved from `EpisodeController`                                          |
| `app/Http/Controllers/Share/EpisodeController.php`     | edit   | `use FormatsSessionStart`; its private `whenFor()` (`T-124`) deleted                 |
| `app/Http/Controllers/Share/SeriesController.php`      | edit   | `cancelledAt` on each live Episode's `live`; `livePanel` gains five lines            |
| `app/Http/Controllers/Shared/SharedController.php`     | edit   | `liveCard()`'s `copy` gains `cancelled`                                              |
| `routes/share/episodes.php`                            | edit   | `cancel`, `restore`, `copy`                                                          |
| `resources/js/components/series/LiveSessionPanel.vue`  | edit   | Cancel session, Undo, Add the next session and its help; the `cancelled` arm         |
| `resources/js/components/series/LiveSessionCard.vue`   | edit   | the `cancelled` arm: the time and one line                                           |
| `lang/en/live.php`                                     | edit   | `state.cancelled.message`, `panel.cancelled`, `panel.copy_help`, three action labels |
| `lang/en/series.php`                                   | edit   | `session_cancelled`, `session_restored`, `session_copied`                            |
| `docs/flows/live-sessions.md`                          | edit   | the `cancelled` row's writer; "Cancelling, and the next session"; "Not built yet"    |
| `docs/flows/series.md`                                 | edit   | "Adding episodes": `LiveSessionService::copy()` as the second caller of `add()`      |
| `docs/tinker/live-sessions.md`                         | edit   | cancel, undo and copy by hand                                                        |
| `tests/Feature/Series/CancelLiveEpisodeTest.php`       | new    | 19 cases                                                                             |

No config: `config/qori.php` is `T-123`'s, and the one number this task adds
is a class constant. No migration, factory or seeder: `cancelled_at` is a key
in `episodes.content` (`D-026`). `qori:reachability` sees the three routes
through their Wayfinder helpers in `LiveSessionPanel.vue`
(`Reachability::isLinked()`).

## Database

None. `cancelled_at` lives inside `episodes.content` (`D-026`); the column
and the `records` key are `T-123`'s.

## Code

```php
namespace App\Services;

use App\Concerns\LocksOverCapSeries;
use App\Enums\EpisodeType;
use App\Exceptions\AppException;
use App\Models\Episode;
use App\Models\Series;
use App\Support\Timezones;
use Carbon\CarbonImmutable;
use InvalidArgumentException;

class LiveSessionService   // T-124's, T-125's and T-127's class; these join withLockedContent(), stateFor() and liveEpisodeOf()
{
    use LocksOverCapSeries;

    /**
     * How far on "Add the next session" puts the copy: the same local time
     * in the Group's zone, this many days later. Interpolated into
     * live.panel.copy_help as :days and written into no sentence.
     */
    public const NEXT_SESSION_DAYS = 7;

    /**
     * Call a session off (D-026). content.cancelled_at is written under the
     * row lock and nothing else on the row changes, so restore() puts back
     * exactly what was there. Refused while a Peer can see a recording, as
     * declareNotRecorded() is: a fact outranks a claim — checked inside the
     * lock, so a paste() between the check and the write cannot leave a
     * cancelled session with a visible recording; the throw rolls the
     * transaction back. Cancelling a cancelled session is a no-op. T-138
     * queues session_cancelled from here.
     */
    public function cancel(Series $series, string $episodeId): Episode;
    // $this->guardSeriesUnlocked($series->group, 'cancel a live session');
    // $episode = $this->liveEpisodeOf($series, $episodeId);
    //
    // return $this->withLockedContent($episode, function (Episode $locked): void {
    //     if ($locked->recordings()->visible()->exists()) {
    //         throw AppException::invalidRequest(
    //             'errors.live.has_recording',
    //             devMessage: "Episode {$locked->getKey()} has a visible recording; hide it before cancelling the session.",
    //         );
    //     }
    //
    //     if ($locked->isCancelled()) {
    //         return;
    //     }
    //
    //     $locked->content = [...$locked->content, 'cancelled_at' => CarbonImmutable::now()->toIso8601String()];
    // });

    /** Undo. Idempotent: clearing an absent key still answers the Episode. Re-sends nothing (D-028). */
    public function restore(Series $series, string $episodeId): Episode;
    // $this->guardSeriesUnlocked($series->group, 'restore a cancelled live session');
    // $episode = $this->liveEpisodeOf($series, $episodeId);
    //
    // return $this->withLockedContent($episode, function (Episode $locked): void {
    //     $content = $locked->content;
    //     unset($content['cancelled_at']);
    //     $locked->content = $content;
    // });

    /**
     * "Add the next session": a new live Episode at the end of the Series, at
     * the same local time NEXT_SESSION_DAYS on — or the first such slot still
     * ahead — with this one's title, provider, join_url, records and length,
     * and nothing else (D-026). Through EpisodeService::add(), so the cap, the
     * lock and the timezone guard apply once; resolved from the container
     * because EpisodeService takes this service by constructor (T-124).
     *
     * A non-live Episode, one outside $series or one with no start is a
     * programmer error: the controller passes what liveEpisodeOf() returned,
     * and the form never makes a live Episode without a start.
     */
    public function copy(Series $series, Episode $episode): Episode;
    // if (
    //     ! $episode->isLive()
    //     || (string) $episode->series_id !== (string) $series->getKey()
    //     || $episode->starts_at === null
    //     || $episode->ends_at === null
    // ) {
    //     throw new InvalidArgumentException("Episode {$episode->getKey()} cannot be copied as the next session of series {$series->getKey()}.");
    // }
    //
    // $content = (array) $episode->content;
    //
    // return app(EpisodeService::class)->add(
    //     $series,
    //     $episode->title,
    //     EpisodeType::Live,
    //     $episode->provider,
    //     [
    //         ...array_filter(['join_url' => $content['join_url'] ?? null]),
    //         'records' => (bool) ($content['records'] ?? true),
    //     ],
    //     false,
    //     $this->nextSlotFor($episode, $series->group?->timezone() ?? Timezones::fallback(), CarbonImmutable::now()),
    //     $episode->lengthMinutes(),
    // );

    /**
     * The same wall-clock time in the Group's zone, NEXT_SESSION_DAYS later,
     * stepped forward by the same amount until it is ahead of $now. addDays()
     * on a zoned instant keeps the hour across a daylight-saving change;
     * adding hours would not. Answers UTC.
     */
    private function nextSlotFor(Episode $episode, string $zone, CarbonImmutable $now): CarbonImmutable;
    // $next = $episode->starts_at->toImmutable()->setTimezone($zone)->addDays(self::NEXT_SESSION_DAYS);
    //
    // while ($next <= $now) {
    //     $next = $next->addDays(self::NEXT_SESSION_DAYS);
    // }
    //
    // return $next->utc();
}
```

```php
namespace App\Concerns;

use App\Models\Episode;
use App\Models\Series;
use App\Support\Timezones;

/**
 * A live Episode's start said back in the Group's zone with the zone named,
 * for a flash. T-124 wrote this as EpisodeController::whenFor(); it moves
 * here unchanged so the copy's flash cannot format the hour a second way.
 */
trait FormatsSessionStart
{
    protected function whenFor(Episode $episode, Series $series): string
    {
        return $episode->starts_at
            ->setTimezone($series->group?->timezone() ?? Timezones::fallback())
            ->format('j M Y, g:ia T');
    }
}

// App\Http\Controllers\Share\EpisodeController: `use FormatsSessionStart;` beside
// ResolvesShareSeries, and T-124's private whenFor() deleted. store() and
// update() call $this->whenFor() exactly as before.
```

```php
namespace App\Http\Controllers\Share;

use App\Concerns\FormatsSessionStart;
use App\Concerns\ResolvesShareSeries;
use App\Http\Controllers\Controller;
use App\Services\LiveSessionService;
use App\Support\Terminology;
use Illuminate\Http\RedirectResponse;
use Inertia\Inertia;

class LiveSessionController extends Controller   // T-127's; three actions join notRecorded() and recorded()
{
    use FormatsSessionStart, ResolvesShareSeries;

    public function cancel(string $group, string $seriesId, string $episodeId, LiveSessionService $sessions, Terminology $terminology): RedirectResponse;
    // $episode = $sessions->cancel($this->seriesById($seriesId), $episodeId);
    // Inertia::flash('toast', ['type' => 'success', 'message' => $terminology->line('series.session_cancelled', ['title' => $episode->title])]);
    // return back();

    public function restore(string $group, string $seriesId, string $episodeId, LiveSessionService $sessions, Terminology $terminology): RedirectResponse;
    // $episode = $sessions->restore($this->seriesById($seriesId), $episodeId);
    // Inertia::flash('toast', ['type' => 'success', 'message' => $terminology->line('series.session_restored', ['title' => $episode->title])]);
    // return back();

    public function copy(string $group, string $seriesId, string $episodeId, LiveSessionService $sessions, Terminology $terminology): RedirectResponse;
    // $series = $this->seriesById($seriesId);
    // $next = $sessions->copy($series, $sessions->liveEpisodeOf($series, $episodeId));
    // Inertia::flash('toast', ['type' => 'success', 'message' => $terminology->line('series.session_copied', [
    //     'title' => $next->title,
    //     'when' => $this->whenFor($next, $series),
    // ])]);
    // return back();
}
```

```php
// routes/share/episodes.php — after T-127's four, inside the same file.
Route::post('series/{seriesId}/episodes/{episodeId}/cancel', [LiveSessionController::class, 'cancel'])
    ->name('series.episodes.cancel');
Route::delete('series/{seriesId}/episodes/{episodeId}/cancel', [LiveSessionController::class, 'restore'])
    ->name('series.episodes.restore');
Route::post('series/{seriesId}/episodes/{episodeId}/copy', [LiveSessionController::class, 'copy'])
    ->name('series.episodes.copy');
```

```php
// App\Http\Controllers\Share\SeriesController::show() — on the `live` key of
// each live Episode, beside T-127's `state` and `notRecordedAt`:
'cancelledAt' => $episode->content['cancelled_at'] ?? null,

// and in the top-level `livePanel` prop T-127 shaped, beside its lines:
'cancelled' => $terminology->line('live.panel.cancelled'),
'copyHelp' => $terminology->line('live.panel.copy_help', ['days' => (string) LiveSessionService::NEXT_SESSION_DAYS]),
'actions' => [
    // ...T-127's hide, unhide, addAnother, notRecorded, undoNotRecorded...
    'cancel' => __('live.panel.actions.cancel'),
    'undoCancel' => __('live.panel.actions.undo_cancel'),
    'copy' => __('live.panel.actions.copy'),
],
```

```php
// App\Http\Controllers\Shared\SharedController::liveCard() — one more key in
// `copy`, through Terminology::line() with the Series' Group as every line there is:
'cancelled' => $terminology->line('live.state.cancelled.message', [], $group),
```

```ts
// resources/js/components/series/LiveSessionPanel.vue — three more helpers and
// three more controls. The row prop gains `cancelledAt: string | null`; the
// `livePanel` prop gains `cancelled`, `copyHelp` and the three action labels.
import {
    cancel as cancelSession,
    copy as copySession,
    restore as restoreSession,
} from '@/routes/share/series/episodes';

// livePanel: {
//     ...T-127's keys...
//     cancelled: string;
//     copyHelp: string;
//     actions: { ...T-127's...; cancel: string; undoCancel: string; copy: string };
// }
```

Each control is an Inertia `<Form>` posting to the helper's URL with no
fields, `:disabled="processing || lock.active"`, exactly as `T-127`'s Hide
and Undo are. What renders, by `live.state`:

| `state`                                                                                                      | Panel                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| every state                                                                                                  | **Add the next session** (`copySession`, POST) with `livePanel.copyHelp` beneath it in the muted style of `T-124`'s `noEmail` line                                                       |
| `upcoming`, `open`, `waiting`, `review`, `overdue`, `not_recorded` — every state but `ready` and `cancelled` | `T-123`'s, `T-124`'s, `T-126`'s and `T-127`'s controls unchanged, then **Cancel session** (`cancelSession`, POST). `review` is creator-only and reached by `T-143`; it inherits this row |
| `ready`                                                                                                      | `T-126`'s and `T-127`'s controls unchanged; no Cancel session                                                                                                                            |
| `cancelled`                                                                                                  | `livePanel.cancelled`, then **Undo** (`restoreSession`, DELETE) and Add the next session. The edit form, the paste form, the recording list and `T-127`'s controls do not render         |

```ts
// resources/js/components/series/LiveSessionCard.vue — LiveCard.copy gains
// `cancelled: string`. One more arm in the template T-125 wrote; the `phase`
// computed already returns 'cancelled' unchanged, because it is not one of
// the three clock states it re-derives.
//   phase 'cancelled'    → <SessionTime :starts-at="live.startsAt" :ends-at="live.endsAt" :group-timezone="live.groupTimezone" />
//                          <p>{{ live.copy.cancelled }}</p>
//                          nothing else: no records badge, no Join, no Join again, no Watch, no resolution
```

`docs/flows/live-sessions.md`: the state table's `cancelled` row names
`LiveSessionService::cancel()` as its writer and `restore()` as its undo; a
section "Cancelling, and the next session" after `T-127`'s "Correcting a
recording":

```
POST   /g/{group}/series/{seriesId}/episodes/{episodeId}/cancel   (share.series.episodes.cancel)
DELETE /g/{group}/series/{seriesId}/episodes/{episodeId}/cancel   (share.series.episodes.restore)
  └─ LiveSessionController@cancel / @restore
       └─ LiveSessionService::cancel() / restore()
            ├─ guardSeriesUnlocked()            the over-cap lock
            ├─ liveEpisodeOf()                  id only, inside this Series, live only
            └─ withLockedContent()              cancelled_at set or unset; nothing else on the row
                 └─ cancel only, inside the lock: refused while recordings()->visible()->exists()   (errors.live.has_recording; the transaction rolls back)

POST   /g/{group}/series/{seriesId}/episodes/{episodeId}/copy     (share.series.episodes.copy)
  └─ LiveSessionController@copy
       └─ LiveSessionService::copy()
            ├─ nextSlotFor()                    same local time, NEXT_SESSION_DAYS on, first slot still ahead
            └─ EpisodeService::add()            the cap, the lock, the timezone guard; content = join_url + records
```

with three sentences: Join on a cancelled session is refused by
`joinAllowed()` and lands on the card with `live.join.not_open`;
`creatorNudgeCandidates()` never lists a cancelled Episode because `stateFor()`
says so; nothing is emailed and no reminder row is touched here (`T-138`).
"Not built yet" loses cancel and gains "a cancellation email (`T-138`)".

`docs/flows/series.md`, "Adding episodes": one sentence that
`LiveSessionService::copy()` is the second caller of `EpisodeService::add()`
and passes the guards the same way, with a pointer to `live-sessions.md` for
cancel.

`docs/tinker/live-sessions.md`, after `T-127`'s four calls:

```php
$sessions = app(App\Services\LiveSessionService::class);
$live = $series->fresh()->orderedEpisodes()->firstWhere('type', App\Enums\EpisodeType::Live);

$sessions->cancel($series->fresh(), (string) $live->getKey())->isCancelled();    // true
$sessions->stateFor($live->fresh(), Carbon\CarbonImmutable::now());             // LiveState::Cancelled, whatever the clock says
$sessions->restore($series->fresh(), (string) $live->getKey())->isCancelled();   // false

$next = $sessions->copy($series->fresh(), $live->fresh());
$next->starts_at->setTimezone($group->timezone())->format('D j M Y, g:ia T');    // the same time, seven days on
$next->content;                                                                  // join_url and records only
$next->position;                                                                 // last in the Series
```

## Copy

| Key                              | File                 | English                                                                                                                 |
| -------------------------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `live.state.cancelled.message`   | `lang/en/live.php`   | This session was cancelled.                                                                                             |
| `live.panel.cancelled`           | `lang/en/live.php`   | Cancelled. Your :peer_plural see that on the :series page, and nobody can join. No email goes out — tell them yourself. |
| `live.panel.copy_help`           | `lang/en/live.php`   | Adds the next :episode :days days on at the same time, with this session's link, length and recording setting.          |
| `live.panel.actions.cancel`      | `lang/en/live.php`   | Cancel session                                                                                                          |
| `live.panel.actions.undo_cancel` | `lang/en/live.php`   | Undo                                                                                                                    |
| `live.panel.actions.copy`        | `lang/en/live.php`   | Add the next session                                                                                                    |
| `series.session_cancelled`       | `lang/en/series.php` | :title is cancelled. Your :peer_plural see that on the :series page.                                                    |
| `series.session_restored`        | `lang/en/series.php` | :title is back on.                                                                                                      |
| `series.session_copied`          | `lang/en/series.php` | Next session added: :title starts :when.                                                                                |

`live.state.cancelled` carries no resolution on purpose: it is final. The
three action labels and the help line's "this session's" say **session** on
purpose, the fixed word for one meeting of a live Episode, as `T-127`'s
labels do; `:episode` in `live.panel.copy_help` names the row that is added,
which is the Group's noun and never a fixed word (`CLAUDE.md`, product
nouns). The two words name different things and are not interchangeable.
`:days`
is `LiveSessionService::NEXT_SESSION_DAYS`, interpolated in
`SeriesController::show()` and written into no sentence; `:when` is
`FormatsSessionStart::whenFor()`'s result, the new start in the Group's zone
with the zone named. The lines carrying a noun go through
`Terminology::line()`; the three action labels carry none and are read with
`__()`. No line under `live.*` says "live now", "has ended", "on its way" or
"processing" (`D-026`); no vendor is named; no article sits directly before a
noun placeholder (`TerminologyTest::test_no_lang_line_puts_an_article_before_a_noun`).
`live.panel.cancelled` and `series.session_cancelled` say no email goes out,
which is true until `T-138`; `T-138` rewrites both when the cancellation
email exists. Nothing is added to `errors.php`: cancel with a visible
recording reuses `T-127`'s `errors.live.has_recording`, a non-live Episode
`errors.live.not_live`, the cap `errors.series.episode_limit_reached`, the lock
`errors.series.locked_over_cap`.

## Routes

| Verb   | Path                                                       | Name                            | Action                                 |
| ------ | ---------------------------------------------------------- | ------------------------------- | -------------------------------------- |
| POST   | `/g/{group}/series/{seriesId}/episodes/{episodeId}/cancel` | `share.series.episodes.cancel`  | `Share\LiveSessionController::cancel`  |
| DELETE | `/g/{group}/series/{seriesId}/episodes/{episodeId}/cancel` | `share.series.episodes.restore` | `Share\LiveSessionController::restore` |
| POST   | `/g/{group}/series/{seriesId}/episodes/{episodeId}/copy`   | `share.series.episodes.copy`    | `Share\LiveSessionController::copy`    |

All three in `routes/share/episodes.php`, inside `routes/share.php`'s `auth`,
`verified`, `group` group with prefix `g/{group}` and name prefix `share.`
(`routes/share.php:24-34`). Ids throughout: every one mutates. No Peer route:
the Peer's side is the existing card and `T-125`'s Join, which already refuses
a cancelled session.

## Tests

**New: `tests/Feature/Series/CancelLiveEpisodeTest.php` — 19 cases**
(`RefreshDatabase`; `setUp` calls `$this->travelTo(CarbonImmutable::parse('2026-09-20T00:00:00Z'))`;
private helpers `scene()` as `LiveSessionTest.php:41-60` with `timezone`
`Australia/Melbourne`, `live(Series $series, array $content = [], int $lengthMinutes = 60): Episode`
through `EpisodeService::add()` starting `2026-10-01T09:00:00` Melbourne,
`peer(Series $series): User` through `AccessService::grant()`,
`act(string $route, string $method, Series $series, Episode $episode)` posting
to `route('share.series.episodes.'.$route, ['group' => $group->slug, 'seriesId' => $series->getKey(), 'episodeId' => $episode->getKey()])`,
`state(Episode $episode, string $melbourne): LiveState` calling
`app(LiveSessionService::class)->stateFor($episode->fresh(), CarbonImmutable::parse($melbourne, 'Australia/Melbourne'))`,
and `toastContains()` as `tests/Feature/Access/SeriesAccessCodeTest.php:86-89`
reads a toast through `Inertia\Support\SessionKey::FLASH_DATA`)

1. `test_cancel_writes_cancelled_at_and_both_pages_read_cancelled` — POST
   cancel; `content['cancelled_at']` is an ISO string and `isCancelled()` is
   true; `state()` is `Cancelled` at `2026-10-01 08:00`, `09:30` and
   `2026-10-03 10:01`; the Peer's page (`shared.show`) has
   `series.episodes.0.live.state` `cancelled` and `.live.copy.cancelled` equal
   to `live.state.cancelled.message`; the creator's page has
   `series.episodes.0.live.state` `cancelled`, `.live.cancelledAt` non-null and
   `livePanel.cancelled` equal to the Group's line; the success toast is
   `series.session_cancelled` with the title.
2. `test_cancelling_a_cancelled_session_is_a_no_op` — a second POST: the
   stored `cancelled_at` string is unchanged, the same success toast, no
   error.
3. `test_undo_clears_cancelled_at_and_the_card_returns_to_the_clock` — cancel,
   then DELETE; the key is absent; `state()` is `Open` at `09:30`; the Peer's
   page has `live.state` `open`; the toast is `series.session_restored` with
   the title.
4. `test_undo_on_a_session_that_is_not_cancelled_is_a_no_op` — DELETE with
   nothing cancelled: the same success toast; `content` unchanged.
5. `test_a_session_with_a_visible_recording_cannot_be_cancelled` —
   `RecordingService::paste()`; POST cancel: the error toast is
   `errors.live.has_recording.message`, `cancelled_at` absent;
   `RecordingService::hide()`, then the same POST succeeds; after DELETE the
   recording is still hidden (`hidden_at` non-null).
6. `test_join_is_refused_for_a_cancelled_session_inside_its_window` — cancel;
   `travelTo` `2026-10-01 09:30` Melbourne; the Peer's GET on
   `shared.episodes.open` is a 302 to
   `route('shared.show', $seriesId).'#episode-'.$episodeId` with an `info`
   toast `live.join.not_open`; `AccessOpen::query()->forGroup($group)` holds no
   row; after DELETE the same GET is a 302 to
   `https://zoom.us/j/91827405566` (owner acceptance 14: no stale live
   destination is followed).
7. `test_a_cancelled_session_is_never_a_creator_nudge_candidate` — a live
   Episode written through `$series->episodes()->create([...])` with
   `starts_at` and `ends_at` 13 hours before a fixed `$now`, content
   `['join_url' => 'https://zoom.us/j/1', 'records' => true]`, one active
   Access; inside `CurrentGroup::runFor($group, …)`,
   `SessionNoticeService::creatorNudgeCandidates($now)` has one; after
   `LiveSessionService::cancel()` it has none; after `restore()` it has one
   again.
8. `test_cancel_and_undo_send_nothing` — the scene and the Peer built first,
   then `Notification::fake()`, because `peer()` grants through
   `AccessService::grant()`, which sends `SeriesAccessNotification`
   (`app/Services/AccessService.php:47`) and would fail the assertion for a
   reason unrelated to cancel; POST cancel and DELETE;
   `Notification::assertNothingSent()`; `session_notices` has no row.
9. `test_the_next_session_is_a_week_on_at_the_same_local_time_across_the_daylight_change`
   — POST copy on the 1 October session (`2026-09-30T23:00:00+00:00`); the
   Series has two Episodes; the second's `starts_at` is
   `2026-10-07T22:00:00+00:00` (8 October 9:00am AEDT), `ends_at`
   `2026-10-07T23:00:00+00:00`, `position` 2; the first is unchanged; the
   toast is `series.session_copied` with `:when` `8 Oct 2026, 9:00am AEDT`.
10. `test_the_next_session_copies_the_link_length_switch_and_title_and_nothing_else`
    — a source with `join_url`, `records => false`, `lengthMinutes: 90`,
    `is_preview` true, `content.not_recorded_at` and `schedule_version` 3
    written by hand, one pasted then hidden recording, then cancelled; POST
    copy; the copy has the same `title`, `provider` `Zoom`, `type` `Live`,
    `content` exactly `['join_url' => …, 'records' => false]`,
    `lengthMinutes()` 90, `isCancelled()` false, `isNotRecorded()` false,
    `scheduleVersion()` 1, `recordings()->count()` 0, `is_preview` false.
11. `test_the_next_session_from_a_class_already_held_lands_on_the_next_slot_still_ahead`
    — `travelTo('2026-10-20T00:00:00Z')`; POST copy on the 1 October session;
    the copy's `starts_at` is `2026-10-21T22:00:00+00:00` (22 October 9:00am
    AEDT), not 8 or 15 October.
12. `test_the_next_session_keeps_a_pasted_link_on_the_link_provider` — a
    source on `EpisodeProvider::Link` with a Meet URL; the copy is `Link` with
    the same `join_url`.
13. `test_the_next_session_respects_the_episode_cap` —
    `config()->set('qori.plans.start.episodes_per_series', 1)`; POST copy: the
    error toast is `errors.series.episode_limit_reached.message` containing
    `1`; `episodeCount()` stays 1.
14. `test_the_service_refuses_a_copy_of_anything_but_a_live_session_of_this_series`
    — `copy($series, $fileEpisode)` throws `InvalidArgumentException`;
    `copy($otherSeries, $liveEpisode)` throws `InvalidArgumentException`; a
    POST copy on the File Episode answers the error toast
    `errors.live.not_live.message` from `liveEpisodeOf()`.
15. `test_a_slug_on_any_of_the_three_actions_does_not_resolve` — the Series
    slug as `seriesId` on cancel, restore and copy: each answers a redirect
    back with the `errors.series.not_found.message` toast
    (`toastContains()`); nothing written — `cancelled_at` absent,
    `episodeCount()` 1. State, never a status, as
    `tests/Feature/Series/ShareSeriesRoutesTest.php:143-150` does:
    `seriesById()` throws `AppException::notFound`, and
    `AppException::render()` answers a status page only on a GET; on a POST
    or DELETE it flashes the toast and answers `back()`
    (`app/Exceptions/AppException.php:264-283`).
16. `test_another_groups_session_is_not_found` — a second Group's owner posts
    all three under their own `g/{group}` with the first Group's Series and
    Episode ids: each answers a redirect back with the
    `errors.series.not_found.message` toast; the row and the count untouched
    (`tests/Feature/Series/EpisodeRoutesTest.php:234-248`; owner acceptance
    11).
17. `test_the_over_cap_lock_refuses_all_three` — `scene()`'s Group, which has
    `timezone` `Australia/Melbourne`, with the live Episode and a second
    Series added on plan `start`, then `plan` forced to `free` as
    `overCapGroup()` does (`tests/Feature/Series/OverCapLockTest.php:59-72`;
    that helper's own Group has no zone, so `add()` would refuse the live
    Episode); cancel, restore and copy each answer the
    `errors.series.locked_over_cap.message` toast; nothing written.
18. `test_cancel_undo_and_copy_leave_progress_and_certificates_alone` — a
    Series of the one live Episode; the Peer completes it through
    `ProgressService::completeFor()` and holds a `certificate_code`; cancel,
    undo, copy; `completed_episode_ids` and `certificate_code` unchanged
    (owner acceptance 12).
19. `test_the_panel_lines_speak_the_groups_words` — a `pro` Group with custom
    labels, as `tests/Feature/TerminologyTest.php` builds one:
    `livePanel.cancelled` contains the Group's word for Peers and not `Peers`;
    `livePanel.copyHelp` contains the Group's word for Episode and `7`.

**Changed:** none. `tests/Feature/Series/LiveSessionStateTest.php` case 7 and
`tests/Feature/Mail/RecordingNeededTest.php` case 4 write `cancelled_at` by
hand and stay green; `tests/Feature/Series/EditLiveEpisodeTest.php` case 12
reads the flash `whenFor()` formats and is unchanged by the move into the
concern.

Total: 19 new cases.

## Acceptance

- [ ] On the creator's Series page, Cancel session on a live row makes the
      Peer's card read "This session was cancelled." and the creator's row
      read the cancelled line within the same minute, at phone width and at
      desktop width, with Move and Remove still reachable
- [ ] A Peer who follows a saved Join link to a cancelled session inside its
      window lands on the card, never on the meeting; after Undo the same link
      opens the meeting again (owner acceptance 14: no message sends a stale
      live destination, and nothing is sent at all)
- [ ] Cancel is refused while a recording is visible, with the line that says
      to hide it first; Undo puts back exactly what was there, a hidden
      recording included
- [ ] Add the next session on a 1 October 9:00am AEST session makes an 8
      October 9:00am AEDT session with the same title, link, length and
      Recorded switch and nothing else, at the end of the Series; taken after
      the class ran, it lands on the next weekly slot still ahead; the toast
      names the new start with the zone
- [ ] The next session meets the plan's Episode cap and the over-cap lock
      exactly as the New Episode form does
- [ ] A cancelled session is never nudged, and no email leaves for a cancel,
      an undo or a copy
- [ ] Neither cancelling, undoing nor copying changes a Peer's progress or a
      certificate (owner acceptance 12); a wrong-tenant creator and a slug on
      any action are sent back with the not-found toast and write nothing
      (owner acceptance 11)
- [ ] No line under `live.*` says "live now", "has ended", "on its way" or
      "processing"; the number of days is interpolated from the constant
- [ ] `docs/flows/live-sessions.md` carries the `cancelled` row's writer and
      the two chains; `docs/flows/series.md` names the second caller of
      `add()`; the `docs/tinker/live-sessions.md` recipe runs
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~`T-129` `ready`, and with it the chain: `T-126`'s `Episode::recordings()`,
  `RecordingService::paste()`; `T-127`'s `LiveSessionController`,
  `LiveSessionService::liveEpisodeOf()`, `EpisodeRecording::scopeVisible()`,
  the `livePanel` prop shape and `errors.live.has_recording`; `T-129`'s
  `SessionNoticeService::creatorNudgeCandidates()` — frozen names this spec
  builds on. Anyone's, once each is `ready`.~~ **Answered 27 September
  2026:** all of them are `done` (`T-129` qori `a03f90d`); where the names
  or shapes differ from this spec, the Re-scope log says how.

## Re-scope log

**2026-09-27 — reconciled with `T-124` to `T-129` and the code as built.**

- **`withLockedContent()`'s callback is `(array $content, Episode $locked):
  array`**, as `T-127` built it and its docblock says: the re-read content in,
  the content to save out, and a column set on `$locked` inside. The
  `Closure(Episode): void` shape this spec and its Notes defend never
  shipped, and the code is the authority. `cancel()` returns the content
  with `cancelled_at` added, or as it was when already cancelled;
  `restore()` returns it with the key unset.
- **`declareNotRecorded()` already checks for a visible recording inside the
  lock**, on the locked row, so the `paste()` race the Decisions describe is
  closed there; `cancel()` checks the same way, with the same
  `errors.live.has_recording` and the Group's replacements.
- **`LiveSessionController` takes `LiveSessionService` by constructor**
  (`T-127`: the primary service), and `Terminology` by method. The three
  actions follow `notRecorded()` and `recorded()`.
- **The creator's row carries its facts as keys, and the panel's lines are
  `live.copy.panel`.** There is no per-row `live` array and no `livePanel`
  prop (`T-129` met the same): `cancelledAt` joins `state`, `notRecordedAt`
  and `recordingEmail` on the row, null off a live Episode, and `cancelled`,
  `copyHelp` and `actions.{cancel, undoCancel, copy}` join `T-127`'s lines
  under `live.copy.panel`.
- **The Peer's card keys its lines by state**: the line is
  `copy.states.cancelled.message`, where `T-125` left room for it, not
  `copy.cancelled`. The card's `phase` already passes `cancelled` through
  and `line` already reads it; Join, Join again and Watch already stay off in
  that phase, so the template's one change is the Recorded badge, which
  `cancelled` hides.
- **The panel's controls are buttons through `router.visit()`**, `T-127`'s
  `act()`, not `<Form>`s: the row sits inside the page's `<p>`, where the
  HTML parser tears a form out. In `cancelled` the recording-email lines
  (`T-129`) go with the recording list.
- **Add the next session is offered only on a row with a start.** The New
  Episode form requires one for a live Episode, so only a row from before
  `T-123` or from tinker lacks it, and `copy()` refuses that as a programmer
  error; hiding the button keeps a click from reaching the refusal.
- **Test paths:** the creator's page reads `series.episodes.0.state`,
  `.cancelledAt` and `live.copy.panel.*`; the Peer's reads
  `series.episodes.0.live.state` and `.live.copy.states.cancelled.message`.
- **`bin/tasks --check` in `qori-plan`** replaces `php artisan qori:tasks
  --check` in Acceptance: the planning moved on 21 September 2026.

## Notes

Specified on 18 September 2026 from `D-026` and `D-028`, with `D-024` for the
preview flag and `D-027` for the recordings; the merged story is in
[`../course-classroom.md`](../course-classroom.md). First on the slip list
after the checkpoint (`D-031`), because a ten-week course is ten copies.

Edits to other drafts this spec implies:

- `T-138`'s draft is edited to: it edits `LiveSessionService::cancel()` to
  queue `session_cancelled` for holders of a `day_before` row (inside the same
  transaction as the key, or after it — its choice), leaves `restore()` alone
  because Undo re-sends nothing (`D-028`), and rewrites `live.panel.cancelled`
  and `series.session_cancelled`, which say no email goes out.
- `T-138`'s draft is edited to: its `docs/flows/series.md` row strikes the "a
  cancellation email (`T-138`)" line from `docs/flows/live-sessions.md`'s
  "Not built yet", where this task writes it beside the cancel chain, and not
  from `docs/flows/series.md`, which never carries it.
- `T-133`'s draft is edited to: `STATUS:CANCELLED` reads
  `Episode::isCancelled()`, written by this task's `cancel()`; a cancel does
  not bump `schedule_version`, so `SEQUENCE` is unchanged by it and the
  status line alone tells a calendar the entry is off.
- `T-135`'s draft is edited to: "Copy message for your chat" in `cancelled`
  sits beside Undo in the arm this task adds to `LiveSessionPanel.vue`, and
  its `live.chat_message.cancelled` is its own line; the public page's "next
  session" skips an Episode that `isCancelled()`.
- `T-127`'s draft is edited to: `withLockedContent()`'s callback receives the
  locked `Episode` (`T-124`, `ready`), not an array; its two closures follow
  the shape this task's `cancel()` and `restore()` show, and
  `declareNotRecorded()` runs its visible-recording check inside the callback
  as `cancel()` does, so the same `paste()` race is closed there too.

The sprint's cross-task reconciliation of 18 September 2026 gave
`withLockedContent()`'s callback an array shape (the re-read `content` in,
the array to save out). `T-124` is `ready` and frozen with
`Closure(Episode $locked): void`, so that reconciliation line is superseded
by `T-124`'s spec, and `T-127`'s draft is aligned to it above; the next
writer should not flip it back.

`T-124`'s `whenFor()` moves into `App\Concerns\FormatsSessionStart` with its
body unchanged; the edit to `EpisodeController` is mechanical, and `T-124`'s
case 12 still reads the same flash.

The stream's claim order carries this task on `LiveSessionCard.vue` and on
`SharedController.php` (one key in `liveCard()`), and not on
`app/Services/EpisodeService.php`, which this spec does not edit.

`M` holds with nineteen cases. The three service methods are a few lines each
over `withLockedContent()` and `EpisodeService::add()`, the concern is a
move, the controller actions are three-line delegates on `T-127`'s pattern
and the two component arms are one template branch each; most of the cases
are one POST and two or three assertions on a shared `scene()`. Cases 7, 18
and 19 stay although siblings cover the ground nearby: `T-129` hands the
cancelled-candidate assertion to this task from its side (`T-129`, Scope),
18 is owner acceptance 12 on this task's own three actions rather than on
materials, and 19 pins that the two new lines with a noun in them reach the
page through `Terminology::line()` with the Group, which
`TerminologyTest` cannot see.

The public page still lists a cancelled Episode with its time, because
`PublicSeriesController::show()` sends title, type, preview flag and
`starts_at` and nothing this task writes (`T-123` case 15 pins that shape).
What a buyer should see for one is `T-135`'s, which reads `isCancelled()`
when it picks the next session.

`Episode::isCancelled()` has been readable since `T-123`, and two earlier
tests (`LiveSessionStateTest` case 7, `RecordingNeededTest` case 4) write the
key by hand to reach the arms this task gives a writer; they stay as they are.

The daylight-saving arithmetic in cases 9 and 11: Melbourne moves from AEST
(+10) to AEDT (+11) on 4 October 2026, so 9:00am local is 23:00 UTC the day
before on 1 October and 22:00 UTC the day before from 8 October on. Adding
168 hours to the first would give 10:00am on 8 October, which is the bug the
zoned `addDays()` exists to avoid.
