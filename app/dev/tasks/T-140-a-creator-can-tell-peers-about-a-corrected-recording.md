---
id: T-140
title: A creator can tell Peers about a corrected recording
stream: classroom
status: draft
owner: unassigned
estimate: S
depends: T-128
blocks: none
---

# T-140 — A creator can tell Peers about a corrected recording

> **Draft.** Written on 18 September 2026 from `D-028` and the classroom
> brief; not to be started — see [`../PROCESS.md`](../PROCESS.md). What has
> to be decided before it can be marked `ready` is listed at the bottom.

## Why

After `T-128`, a Peer hears about a recording exactly once, and nothing can
make it twice. `SessionNoticeService::queueRecordingReady()` inserts one
`session_notices` row per Peer under the unique key
`(episode_id, user_id, kind, publication)` and reads the publication number
from `content['recording_publication'] ?? 1`, which nothing writes; `D-028`
says a later part or a replaced link sends nothing, and `T-128` builds it that
way. So when a creator pastes the wrong link, hides it (`T-127`) and pastes
the right one, every Peer who followed the first email holds a link the
creator has since replaced, and the only path to a second email — a row with
a different publication — has no action behind it. `T-128`'s Notes say so and
hand two questions to this task: how a deliberate re-send passes the
queue-time window, and who its recipients are.

Afterwards, a visible recording's row on `LiveSessionPanel.vue` carries
"Email :peer_plural about this recording again". The press bumps
`content.recording_publication` under the row lock, queues one
`recording_ready` row per Peer with access under the new number, and
`qori:sessions:notify` sends them on its next run; the mail is the same one,
with one more line saying the link was replaced, and it points at
`shared.episodes.show` as every notice does (`D-024`). A second press inside
`qori.live.recheck_seconds` is refused with the seconds left. `D-028`: "a
deliberate re-send bumps `publication` from a creator action (`T-140`)"; the
owner's proposal, folded into `docs/planning/course-classroom.md`: "A link
refresh alone should not notify everyone again. An intentional corrected
replay can offer a separate 'Notify learners of this update' action."

## Decisions taken to make this specifiable

**The press is the only way a Peer is told twice, and it bumps a number
rather than deleting rows.** The unique key stays the guarantee that no sweep
sends twice (`D-028`); the rows of publication 1 stay in the ledger, which is
the publication history the owner asked to retain. The bump is a write to a
live Episode's `content`, so it runs inside
`LiveSessionService::withLockedContent()` (`D-026`; `T-124`'s callback shape,
`Closure(array $content, Episode $locked): array` — the re-read content in,
the content to save out). An absent key reads as 1, so the first press writes
2 — the same rule as `Episode::scheduleVersion()`.

**`recording_publication` is a sixth key in the live `content`, and
`decisions.md` carries a line saying so.** `D-026` fixes the live payload as
`join_url`, `records`, `cancelled_at`, `not_recorded_at` and
`schedule_version`, with `meeting_id` and `occurrence_id` reserved; the
counter is not on that list. It is `D-028`'s, which gives `publication` a
column on `session_notices` and says a deliberate re-send bumps it from a
creator action, and `T-128` already reads `content['recording_publication'] ?? 1`
without anything writing it. A counter on `episodes` would be a column and a
migration for one integer that only a live Episode has; the live `content` is
where every other live-only fact lives. So the key is added here and
`decisions.md` gains a one-line note under a day's heading extending `D-026`'s
list, so the next reader of `D-026` finds it (see Notes).

**A re-send goes to every Peer with an active Access at the press, and the
notice window is not applied.** `D-028`'s two limits on the first notice —
Accesses granted before `published_at`, and a recording published within
`qori.live.notice_window_days` — keep the automatic notice from mailing a late
joiner about every old recording on the first run after deploy. A press is
one Episode at one moment, and the Peer who joined after the first publication
has only ever seen the wrong link, so they are the person this email is for.
The shape is the one `T-128`'s Notes suggest: a named flag, `deliberate`, on
`queueRecordingReady()`; with it, `recipientsFor()` is called with now as the
cut-off and the window check is skipped. `sendDue()`'s stale check is
untouched, because the rows are created at the press. Confirm — see the
bottom.

**The recording named in the route must be visible, and the session not
cancelled.** The button sits on a visible recording's row, so the id names
what the creator is looking at, and the rows carry that `recording_id` so the
ledger says which link the email was about. A hidden or unpublished one is
refused with `errors.live.notify_hidden`; a cancelled session with
`errors.live.notify_cancelled`. Nothing writes `cancelled_at` until `T-134`,
so the second guard cannot fire yet; `Episode::isCancelled()` exists from
`T-123`, and a guard that costs one line is cheaper than a state `T-134` then
has to remember here.

**The same notification goes, with one more line when it is not the first.**
`RecordingReadyNotification` gains `int $publication = 1` as its last
constructor argument, and above 1 the body says the link was replaced. A
Peer who receives "The recording of :title is ready" twice with nothing else
has been told nothing. Not a second notification class: `MailContentTest`
would then require `qori:mail:check` to send it too, and one class with one
sender is what `T-128` set up. The subject is unchanged, so mail clients
thread the two.

**The throttle is Laravel's `RateLimiter`, keyed on the Episode, sized by
`qori.live.recheck_seconds`, and a throttled press is refused with the
seconds left.** `LoginRequest::ensureIsNotRateLimited()`
(`app/Http/Requests/Auth/LoginRequest.php:61-77`) is the precedent, `hit()`
and `availableIn()` included; the cache is `array` under test
(`.env.testing:57`) and Valkey in production. `D-021`'s second rule asks that
a throttled press says when the next one is allowed, and
`AppException::rateLimited()` lands the creator back on the panel with the
message and the resolution, which is what `AppException::render()` does for
every refusal on a POST (`app/Exceptions/AppException.php:284-288`). The key
is the Episode, not the recording, because a re-send is about the card. The
number is read from config and interpolated, never restated. A timestamp on
the row was the other choice, and it is the one `T-144` makes for Check now:
there the throttle is `episodes.recording_checked_at` (`T-143`'s column),
because that press and the sweep share one fact about when Qori last looked,
and a creator pressing a minute after a sweep has to be told the truth. A
re-send has no sweep to share a fact with — nothing but this button ever
sends a second email — so what is being guarded is a double click, which is
what `RateLimiter` is for, and a throttle that survives a cache flush buys
nothing here. Whether the two should share the number at all is the last
question at the bottom.

**The button is one more `livePanel` action on a visible recording's row,
with one help line under the list.** `T-127` fixed what the panel shows per
state and put Hide on each row; this button goes beside Hide on a row whose
`hiddenAt` is null, and the help line renders once under the list while any
row is visible. Both sentences arrive inside `T-127`'s `livePanel` object
from `SeriesController::show()`, so `share/series/Show.vue` is not edited and
the stream's claim order holds. No disabled-until state on load: the refusal
says the seconds, and a page loaded a minute ago is stale anyway.

**The flash counts what was queued, not what was sent, and names no
interval.** `notifyAgain()` returns the insert count; the toast is a
`trans_choice` line through `Terminology::choice()` so `:peer_plural` is the
Group's word, and it says "will get" because the send is the next run's,
whose interval is the owner's (`D-028`). Its `{0}` branch says nobody has
access, so no email goes; the bump still happens, harmlessly, because the
next Peer granted sees the recording on the page whatever the number says.

**`$by` reaches the log line only.** As `T-126`'s `paste()`: `D-027` has no
column for who acted, and a `Log::info` line naming the user and the new
publication is what a support question needs.

**The tally on the creator's card reads the latest publication, and `T-129`
implements that.** After one re-send to twelve Peers, a tally over every row
reads "sent to 24", which counts emails and not Peers. `talliesFor()` is
`T-129`'s method and this task cannot depend on `T-129` (its place in the
table is fixed), so `T-129`'s draft is edited to group by `publication` and
keep each Episode's highest — see Notes. Nothing here touches
`app/Data/NoticeTally.php`.

**No schema, no config, no seeder.** The number lives in the live `content`
jsonb, which needs no migration; `recheck_seconds` is `T-123`'s key, read and
never redeclared; the route takes ids and sits in `routes/share/episodes.php`
like every other creator action on an Episode.

## Preconditions

**Data this task verifies against:** a clean database. The suite builds what
it needs: a Group in `Australia/Brisbane` with a Series, a live Episode
through `EpisodeService::add()`, Peers through `AccessService::grant()` inside
`CurrentGroup::runFor()`, and a recording through `RecordingService::paste()`
— the helpers `tests/Feature/Series/RecordingStateTest.php` (`T-127`)
declares. The design-review seeder is not touched.

**Equipment:** none for the suite, which runs on the `array` mailer and the
`array` cache (`.env.testing:57`). Mailpit on 1025/8025 for the tinker recipe,
which reads the second email by hand.

**Spike:** none owed. No vendor payload is read: the recording URL is stored
as pasted and never followed (`D-025`), and the mailer is Laravel's.

## Scope

**In:**

- `POST …/recordings/{recordingId}/notify`,
  `share.series.episodes.recordings.notify`, `RecordingController::notify()`.
- `RecordingService::notifyAgain()`: the three refusals, the throttle, the
  bump under the lock, the queue, the log line.
- `SessionNoticeService::queueRecordingReady()` gains `bool $deliberate`;
  `notificationFor()` passes the row's `publication` to the notification.
- `Episode::recordingPublication()`.
- `RecordingReadyNotification::$publication` and the `corrected` line.
- The button and its help line on `LiveSessionPanel.vue`; the flash; the
  three error keys.
- `docs/flows/live-sessions.md` and `docs/tinker/live-sessions.md`.

**Out:**

- A different subject, template or wording for the corrected email beyond
  the one line; custom transactional templates are deferred (`PLAN.md`).
- Telling Peers that a join link, a time or a length changed: no email goes on
  a reschedule (`T-124`, `D-028`), and cancellation is `T-138`'s.
- Re-sending a reminder or a creator nudge: only `recording_ready` has a
  publication that moves.
- Choosing recipients, writing a message, or previewing the mail.
- A disabled button while the throttle runs, or the throttle shown on load.
- `T-144`'s publish, which calls `queueRecordingReady()` without the flag as
  a first notice, and its Check now, which throttles on
  `episodes.recording_checked_at` (`T-143`'s column) and not on a cache key.
- The Peer's card: nothing on it changes, because the corrected link is
  already there (`T-126`, `T-127`).
- The tally's narrowing to the latest publication: `T-129`'s, by the edit in
  Notes.

## Files

| Path                                                  | Change | Notes                                                                                                       |
| ----------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------- |
| `routes/share/episodes.php`                           | edit   | `share.series.episodes.recordings.notify`, after `T-127`'s four                                             |
| `app/Http/Controllers/Share/RecordingController.php`  | edit   | `notify()` beside `T-126`'s `store()` and `T-127`'s `hide()`, `unhide()`                                    |
| `app/Services/RecordingService.php`                   | edit   | `notifyAgain()`, `NOTIFY_THROTTLE_KEY`; `RateLimiter` and `Log` imported                                    |
| `app/Services/SessionNoticeService.php`               | edit   | `queueRecordingReady()` gains `bool $deliberate = false`; `notificationFor()` passes `$notice->publication` |
| `app/Notifications/RecordingReadyNotification.php`    | edit   | `int $publication = 1`; `lineIf()` for `live.mail.recording_ready.corrected`                                |
| `app/Models/Episode.php`                              | edit   | `recordingPublication()` beside `T-124`'s `scheduleVersion()`                                               |
| `app/Http/Controllers/Share/SeriesController.php`     | edit   | `livePanel.actions.notify`, `livePanel.notifyHelp` beside `T-127`'s keys                                    |
| `resources/js/components/series/LiveSessionPanel.vue` | edit   | the button on a visible row; the help line under the list; `notify` imported from Wayfinder                 |
| `lang/en/live.php`                                    | edit   | `mail.recording_ready.corrected`, `panel.actions.notify`, `panel.notify_help`                               |
| `lang/en/series.php`                                  | edit   | `recording_notified`                                                                                        |
| `lang/en/errors.php`                                  | edit   | `live.notify_hidden`, `live.notify_cancelled`, `live.notify_too_soon` in the `live` group `T-125` creates   |
| `docs/flows/live-sessions.md`                         | edit   | "Telling Peers again": the chain, the flag, the throttle, what the sweep does with publication 2            |
| `docs/tinker/live-sessions.md`                        | edit   | the press by hand; `--dry-run` showing the new rows; the second email in Mailpit                            |
| `tests/Feature/Series/RecordingNotifyTest.php`        | new    | 13 cases                                                                                                    |

No page edit: the button and its copy travel inside `T-127`'s `livePanel`
object and the row's `recordings` list, which the panel already receives, so
`resources/js/pages/share/series/Show.vue` keeps the stream's claim order.
No migration, factory or seeder: no column changes, and `recording_publication`
is a key in the live `content` jsonb (see Database). No `config/qori.php`: `recheck_seconds` is
`T-123`'s and only read. `routes/shared.php` is untouched: the Peer's side is
the mail and `shared.episodes.show`. `app/Data/NoticeTally.php` and
`tests/Feature/Mail/MailContentTest.php` are untouched: no new notification
class, and the tally's change is `T-129`'s. `docs/flows/README.md` and
`docs/tinker/README.md` already carry `T-125`'s rows for the two files edited
here. `qori:reachability` sees the route through the Wayfinder import in the
panel.

## Database

None. `recording_publication` is a key in `episodes.content`, the live jsonb
payload, read as 1 when absent. It is a sixth key beside `D-026`'s five
(`join_url`, `records`, `cancelled_at`, `not_recorded_at`,
`schedule_version`): `D-026`'s list does not carry it, `D-028` implies it, and
`T-128` already reads it — the Decisions section says why it goes here and
Notes says what `decisions.md` gains. `session_notices.publication` is
`T-128`'s column and takes the value.

## Code

```php
// App\Models\Episode — one accessor beside scheduleVersion() (T-124).

/**
 * Which recording email this is (D-028). Absent reads as 1, so the first
 * deliberate re-send writes 2; T-128's queue reads it for every row.
 */
public function recordingPublication(): int
{
    return (int) ($this->content['recording_publication'] ?? 1);
}
```

```php
// App\Services\SessionNoticeService (T-128) — two edits, nothing new declared.

/**
 * One pending recording_ready row per Peer with access. T-128's docblock
 * stands; this adds the flag.
 *
 * With $deliberate (T-140), the creator pressed the button: recipients are
 * every active Access with a user_id at the moment of the call, whatever its
 * granted_at, and the notice window is not applied. The cancelled check
 * stays. publication is $episode->recordingPublication(), which the caller
 * has already bumped.
 */
public function queueRecordingReady(EpisodeRecording $recording, bool $deliberate = false): int;
// $episode = $recording->episode;
// if (! $recording->isVisible() || $episode->isCancelled()) { return 0; }
// $now = CarbonImmutable::now();
//
// if ($deliberate) {
//     $grantedBy = $now;
// } else {
//     ... T-128's lines: the earliest visible recording's published_at; return 0 when it is
//         older than config('qori.live.notice_window_days'); $grantedBy = that instant ...
// }
//
// $publication = $episode->recordingPublication();          // was content['recording_publication'] ?? 1 inline
// $rows = $this->recipientsFor($episode, $grantedBy)->map(...T-128's row shape, 'publication' => $publication...);
// return $rows->isEmpty() ? 0 : SessionNotice::query()->insertOrIgnore($rows->all());

// notificationFor(): the RecordingReady arm gains the row's publication as the last argument.
//     SessionNoticeKind::RecordingReady => new RecordingReadyNotification(
//         $episode, $series, $group, $hasAfterSessionMaterials, $homeworkDueAt, $notice->publication,
//     ),
```

```php
namespace App\Services;

use App\Exceptions\AppException;
use App\Models\Episode;
use App\Models\Series;
use App\Models\User;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\RateLimiter;

class RecordingService   // T-126's; the constructor already carries LiveSessionService $sessions (T-127) and SessionNoticeService $notices (T-128)
{
    /** The throttle's cache key prefix; the Episode id follows it. One press per config('qori.live.recheck_seconds'). */
    public const NOTIFY_THROTTLE_KEY = 'recording-notify:';

    /**
     * Tell every Peer with access about this recording again (D-028): bump
     * the Episode's recording_publication under the row lock, then queue one
     * recording_ready row per Peer under the new number. The rows leave with
     * the next qori:sessions:notify run. Returns how many were queued.
     *
     * Refused for a hidden or unpublished recording (errors.live.notify_hidden),
     * a cancelled session (errors.live.notify_cancelled) and a second press
     * inside the throttle (errors.live.notify_too_soon, naming the seconds
     * left). A refused press does not spend the throttle. $by reaches the
     * log line only.
     */
    public function notifyAgain(Series $series, string $episodeId, string $recordingId, User $by): int;
    // $this->guardSeriesUnlocked($series->group, 'email peers about a recording again');
    // $episode = $this->sessions->liveEpisodeOf($series, $episodeId);        // T-127: 404 outside the Series, 422 when not live
    // $recording = $this->recordingOf($episode, $recordingId);               // T-127: errors.live.recording_not_found
    //
    // if (! $recording->isVisible()) {
    //     throw AppException::invalidRequest(
    //         'errors.live.notify_hidden',
    //         devMessage: "Recording {$recordingId} on episode {$episodeId} is hidden or unpublished; nothing to announce.",
    //     );
    // }
    //
    // if ($episode->isCancelled()) {
    //     throw AppException::invalidRequest(
    //         'errors.live.notify_cancelled',
    //         devMessage: "Episode {$episodeId} is cancelled; no recording email goes out.",
    //     );
    // }
    //
    // $key = self::NOTIFY_THROTTLE_KEY.$episode->getKey();
    //
    // if (RateLimiter::tooManyAttempts($key, 1)) {
    //     throw AppException::rateLimited(
    //         'errors.live.notify_too_soon',
    //         [
    //             'seconds' => (string) RateLimiter::availableIn($key),
    //             'window' => (string) config('qori.live.recheck_seconds'),
    //         ],
    //         devMessage: "Recording email for episode {$episodeId} requested again inside the throttle.",
    //     );
    // }
    //
    // T-124's callback: the re-read content in, the content to save out. The
    // second argument is the locked row, so the accessor reads the locked value.
    // $locked = $this->sessions->withLockedContent($episode, fn (array $content, Episode $row): array => [
    //     ...$content,
    //     'recording_publication' => $row->recordingPublication() + 1,
    // ]);
    //
    // // The queue reads the publication from the recording's Episode; hand it the
    // // re-read row so a stale relation cannot queue under the old number.
    // $recording->setRelation('episode', $locked);
    // $queued = $this->notices->queueRecordingReady($recording, deliberate: true);
    //
    // RateLimiter::hit($key, (int) config('qori.live.recheck_seconds'));
    //
    // Log::info(sprintf(
    //     'Recording %s on episode %s announced again as publication %d by user %s: %d queued.',
    //     $recordingId, $episodeId, $locked->recordingPublication(), $by->getKey(), $queued,
    // ));
    //
    // return $queued;
}
```

```php
// App\Notifications\RecordingReadyNotification (T-128) — one argument and one line.

public function __construct(
    private Episode $episode,
    private Series $series,
    private Group $group,
    private bool $hasAfterSessionMaterials = false,
    private ?CarbonImmutable $homeworkDueAt = null,
    /** Above 1, the body says the link was replaced (T-140). */
    private int $publication = 1,
) {}

// toMail(): after live.mail.recording_ready.intro and before .session —
//     ->lineIf($this->publication > 1, $line('live.mail.recording_ready.corrected'))
// SimpleMessage::lineIf() (vendor/laravel/framework/src/Illuminate/Notifications/Messages/SimpleMessage.php:167).
// Subject, action and every other line are T-128's, unchanged.
```

```php
namespace App\Http\Controllers\Share;

use App\Services\RecordingService;
use App\Support\CurrentUser;
use App\Support\Terminology;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Inertia\Inertia;

class RecordingController extends Controller   // T-126's; joins store(), hide(), unhide()
{
    // use ResolvesShareSeries;  — T-126's, unchanged; seriesById() runs inside group scope,
    // so another Group's Series is not found rather than forbidden.

    /** Every parameter is an id; $group is declared because route parameters arrive positionally (see SeriesController). */
    public function notify(
        string $group,
        string $seriesId,
        string $episodeId,
        string $recordingId,
        Request $request,
        RecordingService $recordings,
        Terminology $terminology,
    ): RedirectResponse;
    // $queued = $recordings->notifyAgain($this->seriesById($seriesId), $episodeId, $recordingId, CurrentUser::orFail($request));
    //
    // Inertia::flash('toast', [
    //     'type' => 'success',
    //     'message' => $terminology->choice('series.recording_notified', $queued, ['count' => $queued]),
    // ]);
    //
    // return back();
}
```

```php
// App\Http\Controllers\Share\SeriesController::show() — inside T-127's livePanel array.
'livePanel' => [
    // ...T-127's keys...
    'notifyHelp' => $terminology->line('live.panel.notify_help', [], $scope),
    'actions' => [
        // ...T-127's five...
        'notify' => $terminology->line('live.panel.actions.notify', [], $scope),
    ],
],
```

```ts
// resources/js/components/series/LiveSessionPanel.vue — one control on T-127's recording row.
// livePanel.actions gains `notify: string`; livePanel gains `notifyHelp: string`.
//
// import { hide, unhide, notify } from '@/routes/share/series/episodes/recordings';   // Wayfinder; T-127 imports the first two
//
// On each row of live.recordings whose hiddenAt is null, after T-127's Hide form —
// the same Inertia <Form> with no fields, posting to the helper's URL with the four ids:
//   <Form :action="notify.url({ group, seriesId, episodeId, recordingId: recording.id })" method="post" v-slot="{ processing }">
//     <button type="submit" :disabled="processing || lock.active">{{ livePanel.actions.notify }}</button>
//   </Form>
//
// Once under the list, while any row's hiddenAt is null:
//   <p class="text-muted-foreground text-xs">{{ livePanel.notifyHelp }}</p>
//
// A hidden row keeps T-127's label and Show again and gets no button. No new inline English.
```

`routes/share/episodes.php`, after `T-127`'s `share.series.episodes.recorded`:

```php
Route::post('series/{seriesId}/episodes/{episodeId}/recordings/{recordingId}/notify', [RecordingController::class, 'notify'])
    ->name('series.episodes.recordings.notify');
```

`docs/flows/live-sessions.md` gains "Telling Peers again", beside `T-128`'s
"When a recording is published":
`POST …/recordings/{recordingId}/notify → RecordingController::notify() → RecordingService::notifyAgain()`
→ the three refusals and the throttle → `LiveSessionService::withLockedContent()`
bumps `content.recording_publication` → `SessionNoticeService::queueRecordingReady(deliberate: true)`
→ rows under the new number for every active Access → `qori:sessions:notify`
sends them with `sendDue()`'s five checks unchanged →
`RecordingReadyNotification` with the `corrected` line. State a paste or a
hide never sends a second email, and that the ledger keeps the earlier rows.

`docs/tinker/live-sessions.md` gains "Email everyone again about a corrected
link", after `T-128`'s recipe:

```php
$episode = App\Models\Episode::query()->where('type', 'live')->first();
$series = App\Models\Series::query()->acrossAllGroups()->whereKey($episode->series_id)->first();
$recording = app(App\Support\CurrentGroup::class)->runFor($series->group, fn () => $episode->recordings()->visible()->first());

app(App\Support\CurrentGroup::class)->runFor($series->group, fn () =>
    app(App\Services\RecordingService::class)->notifyAgain($series, $episode->getKey(), $recording->getKey(), $series->group->owner));
// 2 — one row per Peer with access, under publication 2

$episode->fresh()->recordingPublication();   // 2
```

```bash
php artisan qori:sessions:notify --dry-run   # the new rows are due
php artisan qori:sessions:notify             # the second email, with "replaced the link", at http://localhost:8025
```

## Copy

Every line with a noun goes through `Terminology::line()` or
`Terminology::choice()`; the mail line is read with the Group passed
explicitly, because the sweep has no current Group (`D-028`). `:seconds` and
`:window` come from `RateLimiter::availableIn()` and
`config('qori.live.recheck_seconds')`; `:count` is the branch's own count. No
line under `live.*` says "live now", "has ended", "on its way" or
"processing" (`D-026`); no line names a vendor; no article stands directly
before a noun placeholder
(`TerminologyTest::test_no_lang_line_puts_an_article_before_a_noun`).

| Key                                       | File                 | English                                                                                                                                                                            |
| ----------------------------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `live.panel.actions.notify`               | `lang/en/live.php`   | Email :peer_plural about this recording again                                                                                                                                      |
| `live.panel.notify_help`                  | `lang/en/live.php`   | Use this after you've replaced a wrong link. Everyone with access right now gets one more email, pointing at this :episode. Adding or hiding a link on its own sends nothing.      |
| `live.mail.recording_ready.corrected`     | `lang/en/live.php`   | The link to this recording has been replaced. The one on the :episode page is the right one.                                                                                       |
| `series.recording_notified`               | `lang/en/series.php` | {0} Nobody has access to this :series yet, so no email goes out.\|{1} One :peer will get the recording email again.\|[2,*] :count :peer_plural will get the recording email again. |
| `errors.live.notify_hidden.message`       | `lang/en/errors.php` | That recording is hidden, so there's nothing to tell your :peer_plural about.                                                                                                      |
| `errors.live.notify_hidden.resolution`    | `lang/en/errors.php` | Show it again first, or email them about the one they can see.                                                                                                                     |
| `errors.live.notify_cancelled.message`    | `lang/en/errors.php` | This session is cancelled, so no recording email goes out.                                                                                                                         |
| `errors.live.notify_cancelled.resolution` | `lang/en/errors.php` | Undo the cancellation first if it went ahead after all.                                                                                                                            |
| `errors.live.notify_too_soon.message`     | `lang/en/errors.php` | You asked for this email less than :window seconds ago.                                                                                                                            |
| `errors.live.notify_too_soon.resolution`  | `lang/en/errors.php` | Try again in :seconds seconds.                                                                                                                                                     |

`series.recording_notified` is a `trans_choice` line resolved through
`Terminology::choice()`, like `series.archive_confirm`
(`lang/en/series.php:57`, resolved at
`app/Http/Controllers/Share/SeriesController.php:259-263`). "Will get" states
what was queued; the send is the next run's. The help line says "sends
nothing" for a paste or a hide because that is `T-128`'s rule and the reason
the button exists, and "right now" because the recipients are every active
Access at the press and not `D-028`'s publication cut-off.

The corrected line names nobody. `:creator` is a Terminology placeholder here
and the creator's own name in `accesses.php`
(`SeriesAccessNotification::__construct(..., string $creator)`), so one key
would mean two things in two files; and a Peer needs to know the link changed,
not who changed it.

## Routes

| Verb | Path                                                                                | Name                                      | Action                              |
| ---- | ----------------------------------------------------------------------------------- | ----------------------------------------- | ----------------------------------- |
| POST | `/g/{group}/series/{seriesId}/episodes/{episodeId}/recordings/{recordingId}/notify` | `share.series.episodes.recordings.notify` | `Share\RecordingController::notify` |

In `routes/share/episodes.php`, inside `routes/share.php`'s `auth`,
`verified`, `group` group with prefix `g/{group}` and name prefix `share.`
(`routes/share.php:24-34`). Ids throughout: it mutates. No Peer route: the
Peer's side is the mail, whose button is `shared.episodes.show` (`T-125`).

## Tests

**New: `tests/Feature/Series/RecordingNotifyTest.php` — 13 cases**
(`RefreshDatabase`; `Notification::fake()` in `setUp`; the helpers
`tests/Feature/Series/RecordingStateTest.php` (`T-127`) declares — `scene()`
as `LiveSessionTest.php:41-60` with `timezone` `Australia/Brisbane`,
`liveEpisode()` through `EpisodeService::add()`, `pasted()` through
`RecordingService::paste()`, `peer()` through `AccessService::grant()` — and
`notifyUrl(Group, Series, Episode, EpisodeRecording): string` from
`route('share.series.episodes.recordings.notify', [...])`; the creator signed
in with `actingAs()`; the clock moved with `$this->travel()`; a refusal on the
POST asserted as `tests/Feature/Access/SeriesAccessCodeTest.php:157` asserts
one — `assertRedirect()` then
`assertSessionHas(SessionKey::FLASH_DATA, $this->toastContains(...))`; ledger
rows read with `SessionNotice::query()` inside `CurrentGroup::runFor()`)

1. `test_it_queues_a_row_for_every_peer_with_access_under_the_next_publication`
   — two Peers, a paste; POST notify; `recording_publication` is 2; two
   `recording_ready` rows with `publication` 2, `status` pending,
   `recording_id` the recording, `group_id` the Group; the two
   publication-1 rows are untouched; the success toast is
   `series.recording_notified` with `2` and the Group's Peer plural.
2. `test_it_includes_a_peer_who_joined_after_the_first_email` — a paste,
   the clock moved a minute, a third Peer granted; that Peer has no
   publication-1 row; POST notify; they have a publication-2 row.
3. `test_it_sends_a_second_email_with_the_corrected_line` — a paste and
   `sendDue()` (one sent); POST notify; `sendDue()` again returns 1;
   `Notification::assertSentToTimes($peer, RecordingReadyNotification::class, 2)`;
   the second notification's `toMail($peer)->render()` contains
   `live.mail.recording_ready.corrected` with the default nouns, and the
   first's does not; both action URLs are `route('shared.episodes.show', [...])`.
4. `test_it_re_sends_a_recording_older_than_the_notice_window` —
   `published_at` written back `notice_window_days + 1` days; POST notify
   queues one row per Peer; `sendDue()` sends it, because the row itself is
   new and not stale.
5. `test_it_refuses_a_hidden_recording` — `RecordingService::hide()`; POST
   notify; the error toast is `errors.live.notify_hidden.message`;
   `recording_publication` absent; no publication-2 row.
6. `test_it_refuses_a_cancelled_session` — `content['cancelled_at']` written
   directly; the error toast is `errors.live.notify_cancelled.message`; no
   row queued.
7. `test_a_second_press_inside_the_throttle_is_refused_with_the_seconds_left`
   — POST twice at once; the second's error toast is
   `errors.live.notify_too_soon.message` and its description contains a
   number of seconds no greater than `config('qori.live.recheck_seconds')`;
   `recording_publication` is 2; `$this->travel((int) config('qori.live.recheck_seconds') + 1)->seconds()`;
   a third POST succeeds with `recording_publication` 3 and rows under 3.
8. `test_a_refused_press_does_not_spend_the_throttle` — hide, POST (refused),
   unhide, POST at once: success, `recording_publication` 2.
9. `test_it_speaks_the_groups_vocabulary` — the scene built with `plan`
   `pro` rather than `scene()`'s `start`, because the labels are ignored
   without the `custom_vocabulary` entitlement
   (`app/Support/Terminology.php:135`) and only `pro` and `school` carry it
   (`config/qori.php:350`, `:364`); `settings[Terminology::SETTINGS_KEY]` is
   `TerminologyTest::customLabels()`
   (`tests/Feature/TerminologyTest.php:36-45`, set as `:89-91` does); the success toast contains
   `Ruffies` and not `Peers`; after `sendDue()` the second mail's `corrected`
   line names the Group's Episode word and not `Episode`; the creator's page
   has `livePanel.actions.notify` containing `Ruffies`.
10. `test_a_slug_on_the_action_does_not_resolve` — POST with the Series slug
    as `seriesId`; 404; `recording_publication` absent.
11. `test_another_groups_recording_is_not_found` — a second Group's owner
    posts under their own `g/{group}` with the first Group's Series, Episode
    and recording ids; 404; nothing queued in either Group.
12. `test_a_revoked_peer_gets_nothing` — two Peers, one revoked with
    `AccessService::revoke()` before the press: one row queued, none for the
    revoked; the other revoked after the press and before `sendDue()`: that
    row is `skipped` with `access_inactive` and
    `Notification::assertNotSentTo($revoked, RecordingReadyNotification::class)`
    — owner acceptance 11.
13. `test_the_over_cap_lock_refuses_it` — the Group of
    `OverCapLockTest::overCapGroup()`
    (`tests/Feature/Series/OverCapLockTest.php:59-72`) with a live Episode
    and a paste made before the downgrade; POST notify answers the
    `errors.series.locked_over_cap.message` toast; nothing queued;
    `recording_publication` absent.

**Changed:** none. `tests/Feature/Mail/RecordingReadyTest.php` (`T-128`)
holds, because `queueRecordingReady()`'s new parameter defaults to the old
behaviour and the notification's new argument defaults to 1;
`tests/Feature/Series/RecordingStateTest.php` (`T-127`) holds, because no
state arm and no publication-1 row moves.

Total: 13 new cases.

## Acceptance

- [ ] On the creator's Series page, a visible recording's row carries "Email
      :peer_plural about this recording again" beside Hide, with the help line
      under the list; a hidden row carries Show again and no such button
- [ ] Pressing it lands back on the page with a toast counting the Peers,
      `recording_publication` becomes 2, and the ledger holds one pending
      `recording_ready` row per Peer with access under publication 2, the
      earlier rows still there
- [ ] The next `php artisan qori:sessions:notify` run mails each of them once
      more; the mail says the link was replaced and its button is the
      Episode's `shared.episodes.show` address
- [ ] A Peer who was granted access after the first email gets this one
- [ ] A recording published more than `qori.live.notice_window_days` ago can
      still be announced this way
- [ ] A second press within `qori.live.recheck_seconds` is refused with the
      seconds left; after them a press goes again as publication 3
- [ ] A hidden recording, a cancelled session, a slug, another Group's ids
      and the over-cap lock are each refused as specified, and none of them
      queues a row
- [ ] A revoked Peer receives nothing, before or after the press — owner
      acceptance 11
- [ ] A paste or a hide on its own still sends no email (`T-128`'s rule holds)
- [ ] `docs/flows/live-sessions.md` and `docs/tinker/live-sessions.md`
      describe the press, and the tinker recipe runs
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- `T-128` `ready`, so `queueRecordingReady()`, `recipientsFor()`,
  `notificationFor()` and the notification's constructor are frozen and the
  flag and the sixth argument here are additions to a known shape — anyone's;
  keep draft until it is.
- The recipient rule for a re-send — every active Access at the press, the
  seven-day window not applied (the second decision above) — the owner's to
  confirm, because `D-028` fixed the first notice's rule and left the
  re-send's to this task.
- Whether a re-send should share `qori.live.recheck_seconds` with `T-144`'s
  Check now or wants a longer window of its own: 60 seconds stops a double
  click and nothing more — the owner's; provisional under `D-021`.
- Whether `decisions.md` takes the one-line note extending `D-026`'s live
  `content` list with `recording_publication`, or whether the counter belongs
  on `episodes` as a column after all — the owner's, because `D-026` is the
  decision being extended.

## Re-scope log

None.

## Notes

`T-128`'s draft is not edited: its Notes hand the window and the recipient
cut-off to this task, and the flag on `queueRecordingReady()` is added here
with a default that keeps `T-128`'s behaviour. Its `publication` read moves
onto `Episode::recordingPublication()` in the same edit, a wording change.

`T-129`'s draft is edited to group `talliesFor()` by `publication` as well as
`episode_id` and `status`, keep each Episode's highest publication, and add
one case — rows under two publications for one Episode; the counts are the
highest's — so "Recording email: sent to :count :peer_plural" reads the
latest email once this task lands. Its Scope Out bullet "the deliberate
re-send and `publication` above 1 (`T-140`)" is the one to narrow: the action
stays this task's, and what `T-129` gains is the grouping, so its own line
does not go wrong the first time a creator presses the button. The change is
three lines in a grouped query and cheaper to write from the start than to
re-open; this task cannot carry it because its dependency is `T-128` alone
and the method is `T-129`'s.

`T-124` is `ready` and declares `withLockedContent()`, so its callback shape
is frozen: `Closure(array $content, Episode $locked): array`, the re-read
content in and the content to save out, with the service assigning and
saving. `T-127`'s and `T-144`'s drafts write their closures as
`function (Episode $locked): void` and their writers align them, a wording
change; this task follows `T-124`.

`T-144`'s `publish()` calls `queueRecordingReady()` without the flag: a
recording Qori found and the creator approved is a first notice, with
`D-028`'s recipients and window. Its Check now reads the same
`recheck_seconds` number but throttles on `episodes.recording_checked_at`
(`T-143`'s column), which it chose so the press and the sweep share one fact;
this task's throttle is a `RateLimiter` key, for the reason under Decisions.
Both edit `RecordingController.php` after this task, which is where the
`classroom` stream's claim order already puts them
(`docs/planning/streams/classroom.md`: `T-126`, `T-127`, `T-140`, `T-144`).

`decisions.md` gains a one-line note under a day's heading saying `D-026`'s
live `content` list also carries `recording_publication`, written by `D-028`'s
re-send and read by `T-128`'s queue — so a reader of `D-026` alone does not
treat the key as a stray. The last bullet above is the owner's confirmation of
that note.

The bump happens even when nobody has access, and that is harmless: the next
Peer granted sees the recording on the page whatever the number says, and
`queueRecordingReady()` at their grant is not a path that exists — a grant
never queues a notice. A throttle test moves the clock with
`$this->travel()`; the `array` cache store honours it because
`InteractsWithTime::currentTime()` reads `Carbon::now()`
(`vendor/laravel/framework/src/Illuminate/Support/InteractsWithTime.php:61-63`).

The brief sized this at four tests; thirteen are listed because the
wrong-tenant, revoked, vocabulary, slug and over-cap cases are house rules for
every creator action, and each refusal is one case. The estimate stays `S`: one route, one method, one flag,
one line in a mail, one button.

`T-128`'s report (26 September 2026): the recipient cut-off is the Episode's
earliest *visible* recording, so hiding a wrong link and pasting its
replacement moves it — a Peer granted between the two is mailed about the
replacement, though the class was told of the first link and `D-028` says
later joiners see it on the page. That follows `T-128`'s Decisions, which
left the cut-off for a correction to this task: whether a correction mails
Peers who joined after the first publication is decided here, at the one
call site, `SessionNoticeService::queueRecordingReady()`.
