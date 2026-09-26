---
id: T-129
title: The creator is told when a recording is missing, and sees whether the recording email went
stream: classroom
status: doing
owner: claude
estimate: S
depends: T-128
blocks: T-134, T-143
---

# T-129 — The creator is told when a recording is missing, and sees whether the recording email went

> Written on 17 September 2026 from `D-028`, on the ledger `T-128` builds;
> reconciled with `T-128` as built and made ready on 27 September 2026 (the
> Re-scope log says what changed).

## Why

A live Episode whose recording never arrives is silent on both sides. Nothing
scheduled sends mail today: `routes/console.php:28` holds the one scheduled
command, `qori:series:purge`, and every notification is sent inline from a
request (`app/Notifications/SeriesAccessNotification.php:19-22`). `T-128`
builds the `session_notices` ledger and the Peer's `recording_ready` email,
and nothing in it addresses the creator: the person who can end a `waiting`
card is the one person the sweep never writes to. On the other side of the
same fact, the creator's Series page lists each Episode with its title, type,
provider and start (`app/Http/Controllers/Share/SeriesController.php:158-166`)
and says nothing about whether any email went. `RecipientStatus` already
separates "tried and could not" from "deliberately not sent"
(`app/Enums/RecipientStatus.php:18-22`) and the ledger writes one of them per
row (`D-028`), so the facts exist and no page reads them.

Afterwards, `qori:sessions:notify` also queues one `creator_recording_needed`
row for the Group owner per live Episode that was scheduled to end more than
`qori.live.creator_nudge_hours` ago with nothing published, and
`SessionNoticeService::sendDue()` mails it as
`RecordingNeededNotification`: the scheduled end in the owner's zone, the two
things the card offers (`T-127`'s "Add the recording link" and "There's no
recording for this session") and a button to the creator's Series page. It
goes through the same ledger, suppression filter and retry as
`recording_ready`, once per Episode, never for a cancelled, not-recorded or
live-only session (`D-028`). The creator's Series page reads the
`recording_ready` rows per live Episode and says how many were sent, how many
failed, how many are still to go and how many addresses Qori no longer writes
to — where "sent" means the mail service accepted it, which is all Qori can
see until `T-032` proves arrival.

With automatic detection (`T-143`) the nudge moves to
`qori.live.recording_wait_hours` for an Episode Qori is still looking for;
this task writes the rule `T-143` then edits, and this sprint every Episode is
one without detection.

## Decisions taken to make this specifiable

**The nudge is a ledger row of the same kind as every other notice, and the
command sends it.** `D-028` makes `session_notices` the one outbox, with
suppression, the per-run cap and the three-attempt retry already on it, and
its unique key `(episode_id, user_id, kind, publication)` is what makes "once
per session" a constraint rather than a hope. A direct `notify()` from a sweep
would be a second send path with none of that.

**The send-time skips branch by kind: the active-Access and
recording-available checks are `recording_ready`'s, not the nudge's.**
`T-128` re-checks every row before sending and skips one whose recipient
holds no active Access to the Episode's Series. The Group owner holds no
Access — `accesses` are Peers, never the creator (`CLAUDE.md`, Tenancy) — so
that check applied to a nudge row would skip every one and send nothing. A
nudge row meets the stale, suppressed and session-cancelled checks and no
other; `recording_unavailable` was already the `recording_ready` arm's
alone, and `T-138`'s reminder kinds keep the Access check. The branch is
written inside `sendDue()` as part of this task's edit to
`app/Services/SessionNoticeService.php`, and `T-128`'s draft is told (see
Notes).

**Candidates are narrowed by query and decided by `stateFor()`.** `D-026`
says the state is computed and never stored, so the query narrows on the two
columns — live, `ends_at` inside the window — and
`LiveSessionService::stateFor($episode, $now)` says the rest: `waiting` and
`overdue` are nudged; `ready`, `cancelled` and `not_recorded` (which is what
`records = false` becomes after the end) are not. One state model, no JSON
`where` clauses that would have to agree with it.

**A Series nobody has access to is nudged like any other.** `D-028`
conditions the nudge on the scheduled end, the state and the window, and
nothing else; the classroom brief names no Access condition either. The
query therefore carries no `accesses` clause, and the email's sentence about
Peers stays true as written, because it is conditional ("every :peer with
access gets one email"). Whether a class nobody has been granted should skip
the nudge is a product choice the owner can still make — asked 26 September
2026 — and adding it later is one `whereIn` and one test case, not a
rewrite.

**The window closes at `qori.live.notice_window_days`.** `T-123` backfills
`ends_at` on every existing live Episode, so without a floor the first run
after deploy would mail every creator about every session they ever held. The
same number bounds `recording_ready` (`T-128`), for the same reason.

**The recipient is the Group owner, once.** `D-028` names the owner, and
`Group::owner()` is a `BelongsTo` (`app/Models/Group.php:127-130`). Admins are
not written to; a Group whose owner cannot be loaded is skipped and logged.
The unique key holds the "once": a nudge whose retries are spent is left
`failed` for `T-019`, not re-queued.

**The time in the email is the scheduled end, rendered by `T-128`'s rule.**
The recipient's `users.timezone`, else the Group's, zone named, the Group's
zone beside it when different — `T-128` states the rule and declares the
helper that renders it, `App\Support\ZonedTime` with
`zoneFor(User $recipient, Group $group): string` and
`describe(CarbonInterface $at, string $zone, string $groupZone): string`;
this task calls those two and adds no formatter, format string or lang line
of its own.

**The email is sent to no Peer, and says so.** Its last line tells the owner
they alone received it, because the Peer's card already says the recording
will be added and an email will follow (`D-026`); a creator who assumed the
Peers had been nagged too would write to them twice.

**The tally is a typed shape, read in one query per Series, and `failed`
means the retries are spent.** `App\Data\NoticeTally` carries four counts
(`CLAUDE.md`: a multi-field shape between layers is a value object), and
`SessionNoticeService::talliesFor(Series, SessionNoticeKind)` fills one per
Episode from a single query grouped by `episode_id`, `status` and
`next_attempt_at IS NULL`, so a Series with ten live Episodes costs one read,
not ten. A `failed` row whose `next_attempt_at` is still set is one `T-128`
will try again (`SessionNotice::isExhausted()` is false for it), and the card
counts it under `pending`; `failed` counts exhausted rows only — `status =
failed AND next_attempt_at IS NULL` — so the card never says "couldn't be
sent" fifteen minutes after a first failure that three retries may yet clear.

**The status line is whole sentences from lang, one per count, and "sent" is
defined.** Each sentence is a `trans_choice` line resolved through
`Terminology::choice()` so `:peer_plural` is the Group's word; the controller
concatenates whole sentences and builds none from fragments. A help line says
that "sent" means the mail service accepted it and Qori cannot yet see whether
it arrived — the owner's ask that acceptance and delivery never be confused,
and `D-028`'s "confirmed delivery stays `T-032`'s". Nothing is shown for an
Episode with no rows: a line that says "none sent" before publication would
read as a fault.

**The failed sentence says the retries are spent, with the number from
config.** `:attempts` is `qori.live.notice_attempts`, which under `T-128` is
the number of retries after the first try (its case 12: `attempts` reaches 4
before `next_attempt_at` is null), not the number of tries in all. Since a
counted `failed` row is exhausted, the sentence speaks in the past — Qori
tried again that many times — and says that the recording stays on the Series
page whatever the email does, which is the recovery a creator has.

**The page is not edited, and the tally rides on the row.** The stream's
claim order gives `share/series/Show.vue` to `T-123`, `T-130`, `T-132` and
`T-137` and says every other creator-side change edits a component. `T-123`
mounts `LiveSessionPanel.vue` on each live row with `:episode="episode"`,
typed by the panel's own `LiveEpisode` interface, and `T-123`, `T-126` and
`T-127` put a live Episode's facts on the row itself — `records`, `joinUrl`,
`state`, `notRecordedAt`, `recordings` — each null or empty off a live
Episode. So `SeriesController::show()` adds one more, `recordingEmail`, null
off a live Episode, and `LiveEpisode` gains one optional field. A separate
prop could only reach the panel through a page line, which is the edit this
task avoids.

**The status line is spans.** The row renders inside the page's paragraph,
which is why `T-127`'s actions are buttons and never forms: the HTML parser
tears a block element out of a `<p>`. The summary and the help are two
`<span class="mt-1 block">` lines, as the panel's other lines are, and when
anything failed the summary carries `InlineNotice`'s warning icon and colour
(`AlertTriangle`, `text-warning`), so colour is never the only signal.

**A nudge is checked again before it goes.** The email says no recording has
been added yet. Queueing and sending happen in one run, but a failed send is
tried again 15, 60 and 240 minutes later, and in between the creator may add
the link or say there is none. So `sendDue()` skips a nudge row whose Episode
is no longer `waiting` or `overdue`, as `resolved`, through the same
`isScheduled()` and `stateFor()` the candidates are chosen by.

**Detection changes nothing here.** `T-143` edits
`creatorNudgeCandidates()` to hold an Episode Qori is still looking for until
`recording_wait_hours`; this task neither reads a Connection nor names a
vendor.

**`qori:mail:check` sends the nudge through the service, not by building the
notification.** The command's own rule
(`app/Console/Commands/MailCheckCommand.php:212-213`) and
`MailContentTest::test_every_notification_class_is_covered_by_the_command`
(`tests/Feature/Mail/MailContentTest.php:122-152`) both require it; the scratch
Series gains a second live Episode — `T-128` adds the first and pastes a
recording on it, so that one is `ready` and never a candidate — moved into
the past through `EpisodeService::update()`, which `T-124` lets set a past
start.

**No route, no config key, no schema.** The kind exists in
`SessionNoticeKind` (`T-128`), the numbers are `T-123`'s, and the creator
acts on the buttons `T-127` put on the panel.

## Preconditions

**Data this task verifies against:** a clean database. The feature tests
build a Group with a timezone and an owner as
`tests/Feature/Series/LiveSessionTest.php:41-60` does, a published Series with
one active Access granted through `AccessService::grant()` inside
`CurrentGroup::runFor()` with `Notification::fake()` already on, and a live
Episode created through `$series->episodes()->create([...])` with `starts_at`
and `ends_at` set in the past, because `EpisodeService::add()` refuses a past
start (`app/Services/EpisodeService.php:107-111`, `errors.series.starts_in_past`).
`$now` is a fixed `CarbonImmutable` passed in, never `now()`.

**Equipment:** none to verify from the terminal. Mailpit
(`docs/tinker/mail.md`) to read the nudge by eye, through `qori:mail:check`.

**Spike:** none owed; no vendor is called.

## Scope

**In:**

- `SessionNoticeService::creatorNudgeCandidates()` and `queueCreatorNudges()`,
  the `CreatorRecordingNeeded` arm in `notificationFor()`, and the per-kind
  branch of the skips inside `sendDue()`.
- `RecordingNeededNotification`, with its copy under
  `live.mail.recording_needed.*`.
- `qori:sessions:notify` calling `queueCreatorNudges()` before `sendDue()`
  in each Group, and listing candidates under `--dry-run`.
- `NoticeTally`, `SessionNoticeService::talliesFor()`, the `recordingEmail`
  key inside each live Episode's `live` prop from `SeriesController::show()`,
  and the status line on `LiveSessionPanel.vue`.
- `qori:mail:check` sending the nudge; `docs/flows/live-sessions.md` and
  `docs/tinker/live-sessions.md`.

**Out:**

- The ledger, `sendDue()`'s retry and cap, `RecordingReadyNotification` and
  the command (`T-128`), and what runs the command (`T-206`).
- The `+48 h` rule for an Episode Qori is looking for, `recording_checked_at`,
  and any read of a Connection (`T-143`).
- Cancel, Undo and "Add the next session" (`T-134`); the card already skips a
  cancelled Episode here, and `T-134` asserts it from its side.
- `day_before` and `session_cancelled` (`T-138`); the deliberate re-send and
  `publication` above 1 (`T-140`).
- Any email to a Peer, and any status line on the Peer's card.
- An email to an admin, or a per-creator "stop nudging me" setting; neither
  exists and neither is implied.
- Confirmed delivery, bounces and complaints on the ledger (`T-032`, `T-017`).
- A new Vue page, a new route, a new config key, a migration.

## Files

| Path                                                  | Change | Notes                                                                                                                                                                               |
| ----------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `app/Services/SessionNoticeService.php`               | edit   | `creatorNudgeCandidates()`, `queueCreatorNudges()`, the `CreatorRecordingNeeded` arm in `notificationFor()`, the per-kind checks in `sendDue()`, `SKIPPED_RESOLVED`, `talliesFor()` |
| `app/Notifications/RecordingNeededNotification.php`   | new    | mail only, not queued; copy through `Terminology::line()` with the Group; the time through `ZonedTime`                                                                              |
| `app/Data/NoticeTally.php`                            | new    | sent, failed (exhausted), pending (a retry still due included), skipped                                                                                                             |
| `app/Console/Commands/NotifySessionsCommand.php`      | edit   | `queueCreatorNudges()` between `countDue()` and `sendDue()`; candidates listed under `--dry-run`; `nudges_queued` in the heartbeat                                                  |
| `app/Http/Controllers/Share/SeriesController.php`     | edit   | `recordingEmail` on each live row from `talliesFor()`, beside `state`; `recordingEmail()`                                                                                           |
| `resources/js/components/series/LiveSessionPanel.vue` | edit   | `recordingEmail` on `LiveEpisode`; the status line as spans, with the warning icon when anything failed                                                                             |
| `lang/en/live.php`                                    | edit   | `mail.recording_needed.*`, `notices.recording_ready.*`                                                                                                                              |
| `app/Console/Commands/MailCheckCommand.php`           | edit   | a second live Episode moved into the past; the nudge queued and sent through the service; `EXPECTED` 11                                                                             |
| `docs/tinker/mail.md`                                 | edit   | the message count and the nudge in the list                                                                                                                                         |
| `docs/flows/live-sessions.md`                         | edit   | "Telling the creator" and "The tally on the creator's page"                                                                                                                         |
| `docs/tinker/live-sessions.md`                        | edit   | driving the nudge by hand                                                                                                                                                           |
| `tests/Feature/Mail/RecordingNeededTest.php`          | new    | 10 cases                                                                                                                                                                            |
| `tests/Feature/Series/RecordingEmailStatusTest.php`   | new    | 3 cases                                                                                                                                                                             |
| `tests/Feature/Mail/MailContentTest.php`              | edit   | `$senders` gains the nudge (`:162-168`)                                                                                                                                             |
| `tests/Feature/Console/NotifySessionsCommandTest.php` | edit   | the heartbeat case gains `nudges_queued`                                                                                                                                            |

`resources/js/pages/share/series/Show.vue` is deliberately not listed — see
"The page is not edited" above. `routes/console.php` is `T-206`'s: nothing
schedules the command yet, and this task adds no line of its own.
`config/qori.php` is `T-123`'s: `creator_nudge_hours`, `notice_window_days`
and `notice_attempts` are read, never declared here.

## Database

None. `session_notices` and `SessionNoticeKind::CreatorRecordingNeeded` are
`T-128`'s; a nudge row carries `recording_id` null and `publication` 1.

## Code

```php
// App\Services\SessionNoticeService — the additions below to T-128's class. The
// constructor is T-128's and unchanged: CurrentGroup as $current,
// SuppressionService as $suppressions, LiveSessionService as $sessions.
//
// private const NUDGE_STATES = [LiveState::Waiting, LiveState::Overdue];
// public const SKIPPED_RESOLVED = 'resolved';   // a nudge whose Episode no longer needs one
//
// /** The nudge's premise: a scheduled live Episode that is waiting or overdue. */
// private function needsRecording(Episode $episode, CarbonImmutable $now): bool;
// // return $this->sessions->isScheduled($episode)
// //     && in_array($this->sessions->stateFor($episode, $now), self::NUDGE_STATES, true);

/**
 * Live Episodes in the current Group that are waiting on their creator (D-028):
 * scheduled to end more than qori.live.creator_nudge_hours ago and inside
 * qori.live.notice_window_days, in a state that needs a recording. Whether
 * anybody has been granted is not asked (D-028 names no such condition). Runs
 * inside CurrentGroup::runFor(), so Series and the ledger are scoped; Episode
 * has no scope of its own and is reached through the Group's Series. T-143
 * adds the hold for an Episode Qori is looking for.
 *
 * @return Collection<int, Episode>
 */
public function creatorNudgeCandidates(CarbonImmutable $now): Collection;
// return Episode::query()
//     ->where('type', EpisodeType::Live)
//     ->whereBetween('ends_at', [
//         $now->subDays((int) config('qori.live.notice_window_days')),
//         $now->subHours((int) config('qori.live.creator_nudge_hours')),
//     ])
//     ->whereIn('series_id', Series::query()->select('id'))                       // this Group's, through the scope
//     ->whereNotIn('id', SessionNotice::query()
//         ->where('kind', SessionNoticeKind::CreatorRecordingNeeded)
//         ->select('episode_id'))                                                  // the unique key is the backstop
//     ->with('recordings')                                                          // T-126's relation; stateFor() reads it
//     ->orderBy('ends_at')
//     ->get()
//     ->filter(fn (Episode $episode): bool => $this->needsRecording($episode, $now))
//     ->values();

/**
 * One pending creator_recording_needed row per candidate, to the Group's owner,
 * through the insertOrIgnore() shape queueRecordingReady() uses (T-128):
 * explicit ULIDs, group_id, enum values and timestamps, idempotent under the
 * unique key, no transaction. A Group with no loadable owner inserts nothing
 * and is logged. Returns how many were inserted.
 */
public function queueCreatorNudges(CarbonImmutable $now): int;
// $group = $this->current->get(); $owner = $group?->owner;
// if ($group === null || $owner === null) { Log::warning(...); return 0; }
// $rows = $this->creatorNudgeCandidates($now)->map(fn (Episode $episode): array => [
//     'id' => (string) Str::ulid(),
//     'group_id' => $group->getKey(),
//     'episode_id' => $episode->getKey(),
//     'user_id' => $owner->getKey(),
//     'recording_id' => null,
//     'kind' => SessionNoticeKind::CreatorRecordingNeeded->value,
//     'publication' => 1,
//     'status' => RecipientStatus::Pending->value,
//     'attempts' => 0,
//     'created_at' => $now,
//     'updated_at' => $now,
// ]);
// return $rows->isEmpty() ? 0 : SessionNotice::query()->insertOrIgnore($rows->all());

// In notificationFor() — T-128's private method, whose return type widens from
// RecordingReadyNotification to Illuminate\Notifications\Notification — one more arm.
// $series is the one T-128's subjectsFor() resolved for the row, and $group the
// one sendDue() read from CurrentGroup; nothing is re-queried. T-128's materials
// read moves inside its own arm, the only one that uses it:
//
//     private function notificationFor(SessionNotice $notice, Episode $episode, Series $series, Group $group): Notification;
//     // return match ($notice->kind) {
//     //     SessionNoticeKind::RecordingReady => new RecordingReadyNotification($episode, $series, $group, ...$this->materialsFor($episode)),
//     //     SessionNoticeKind::CreatorRecordingNeeded => new RecordingNeededNotification($episode, $series, $group),
//     //     default => throw new LogicException(...),   // T-138's kinds
//     // };
//
// The recipient is $notice->user (the owner), filtered through
// SuppressionService::blockedForTransactional() exactly as a Peer is.

// In sendDue(), the per-row checks branch by kind. T-128's order stands; its
// Access check is gated, because the owner holds no Access to their own Series,
// and the nudge gains one check of its own:
//
//     stale                            → SKIPPED_STALE                  every kind
//     no such user                     → SKIPPED_ACCESS_INACTIVE        every kind
//     suppressed                       → SKIPPED_SUPPRESSED             every kind
//     the Episode or Series is gone    → SKIPPED_ACCESS_INACTIVE        every kind
//     no active Access to the Series   → SKIPPED_ACCESS_INACTIVE        every kind but CreatorRecordingNeeded
//     content['cancelled_at'] set      → SKIPPED_SESSION_CANCELLED      every kind
//     no published, unhidden recording → SKIPPED_RECORDING_UNAVAILABLE  RecordingReady only
//     before Join's window closes      → postponed to the close         RecordingReady only
//     no longer waiting or overdue     → SKIPPED_RESOLVED               CreatorRecordingNeeded only
//     notify() inside try/catch        → sent, or failed with backoff
//
// A nudge row therefore reaches notify() unless it is stale, suppressed, the
// session was cancelled, or the creator added a recording or said there is
// none after it was queued. T-138 adds its own gated checks.

/**
 * How the ledger stands for one kind across a Series, one grouped query:
 * episode id → NoticeTally. An Episode with no rows is absent from the array.
 * `failed` is exhausted rows only (status failed, next_attempt_at null); a
 * failed row with a retry still due counts as pending.
 *
 * @return array<string, NoticeTally>
 */
public function talliesFor(Series $series, SessionNoticeKind $kind): array;
// SessionNotice::query()->where('kind', $kind)
//     ->whereIn('episode_id', $series->episodes()->select('id'))
//     ->selectRaw('episode_id, status, (next_attempt_at is null) as exhausted, count(*) as n')
//     ->groupBy('episode_id', 'status', DB::raw('next_attempt_at is null'))
//     ->get()
//     → one NoticeTally per episode_id:
//         Sent → sent; Skipped → skipped; Pending → pending;
//         Failed and exhausted → failed; Failed and not exhausted → pending;
//         any other status is ignored
```

```php
namespace App\Data;

/**
 * What the notice ledger says about one Episode and one kind (D-028). "sent"
 * is acceptance by the mail service, not arrival — T-032 owns arrival;
 * "failed" is a row whose retries are spent, and a retry still due is pending.
 */
class NoticeTally
{
    public function __construct(
        public int $sent = 0,
        public int $failed = 0,
        public int $pending = 0,
        public int $skipped = 0,
    ) {}

    public static function empty(): self;

    public function total(): int;      // the four added

    public function isEmpty(): bool;   // total() === 0
}
```

```php
namespace App\Notifications;

use App\Models\Episode;
use App\Models\Group;
use App\Models\Series;
use App\Models\User;
use App\Support\Terminology;
use App\Support\ZonedTime;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;

/**
 * "Add the recording" — the one email a creator gets about a session (D-028).
 * Mail only, not queued (no worker; T-018), sent by qori:sessions:notify from
 * the ledger and never from a request. Checks nothing itself: the command has
 * already filtered the address.
 */
class RecordingNeededNotification extends Notification
{
    public function __construct(
        private Episode $episode,
        private Series $series,
        private Group $group,
    ) {}

    /** @return array<int, string> */
    public function via(object $notifiable): array;   // ['mail']

    public function toMail(User $notifiable): MailMessage;
    // $terminology = app(Terminology::class);
    // $zone = ZonedTime::zoneFor($notifiable, $this->group);                       // T-128's helper, as declared there
    // $replace = ['title' => $this->episode->title, 'name' => $notifiable->name,
    //             'when' => ZonedTime::describe($this->episode->ends_at, $zone, $this->group->timezone())];
    // (new MailMessage)
    //     ->subject($terminology->line('live.mail.recording_needed.subject', $replace, $this->group))
    //     ->greeting($terminology->line('live.mail.greeting', $replace, $this->group))   // T-128's shared line
    //     ->line($terminology->line('live.mail.recording_needed.intro', $replace, $this->group))
    //     ->line($terminology->line('live.mail.recording_needed.paste', [], $this->group))
    //     ->line($terminology->line('live.mail.recording_needed.none', [], $this->group))
    //     ->action(
    //         $terminology->line('live.mail.recording_needed.action', [], $this->group),
    //         route('share.series.show', ['group' => $this->group->slug, 'series' => $this->series->slug]),
    //     )
    //     ->line($terminology->line('live.mail.recording_needed.outro', [], $this->group));
    // Every line goes through Terminology::line() with the Group passed, because
    // the sweep has no current Group (D-028).
}
```

```php
// App\Console\Commands\NotifySessionsCommand — T-128's per-Group closure gains
// the nudge step between the count and the send, on T-128's shape: countDue()
// in every mode, the remaining run budget passed to sendDue(), the run stopped
// when the budget is spent. `due` is counted before the nudges are queued, so
// under --dry-run the count and the candidate lines add up rather than overlap.
// The candidates are listed under --dry-run only, as Scope says: listing them
// on a real run too would read them twice, once to print and once to queue.
//
// CurrentGroup::runFor($group, function () use ($now, $dryRun, $budget, $notices, &$due, &$queued, &$sent): void {
//     $due += $notices->countDue($now);
//     if ($dryRun) {
//         foreach ($notices->creatorNudgeCandidates($now) as $episode) {
//             $this->line(sprintf('Would queue a nudge: %s (%s)', $episode->title, $episode->getKey()));
//         }                                                    // diagnostics, not copy (§23)
//
//         return;                                              // counted and listed; nothing written or sent
//     }
//     $queued += $notices->queueCreatorNudges($now);
//     if ($sent < $budget) {
//         $sent += $notices->sendDue($now, $budget - $sent);
//     }
// });
//
// The heartbeat T-128 writes per run gains one key, beside due, sent and dry_run:
// Log::info('qori:sessions:notify', ['due' => $due, 'nudges_queued' => $queued, 'sent' => $sent, 'dry_run' => $dryRun]);
```

```php
// App\Http\Controllers\Share\SeriesController::show() — SessionNoticeService by
// method injection beside LiveSessionService; one read before the map, and one
// key on each row beside T-127's `state` and `notRecordedAt`, null off a live
// Episode as theirs are. $scope is the Group, as `materialsSummary` reads it:
// Terminology::choice() takes a ?Group.
//
// $tallies = $notices->talliesFor($series, SessionNoticeKind::RecordingReady);
// ...
// 'recordingEmail' => $episode->isLive()
//     ? $this->recordingEmail($tallies[(string) $episode->getKey()] ?? NoticeTally::empty(), $scope, $terminology)
//     : null,

/**
 * The counts and the sentences the panel shows for the recording email. Whole
 * sentences from lang, joined with a space; null summary when no row exists.
 *
 * @return array{sent: int, failed: int, pending: int, skipped: int, summary: ?string, help: string}
 */
private function recordingEmail(NoticeTally $tally, ?Group $group, Terminology $terminology): array;
// $sentences = [$terminology->choice('live.notices.recording_ready.sent', $tally->sent, [], $group)];
// if ($tally->failed > 0)  $sentences[] = $terminology->choice('live.notices.recording_ready.failed', $tally->failed, ['attempts' => (int) config('qori.live.notice_attempts')], $group);
// if ($tally->pending > 0) $sentences[] = $terminology->choice('live.notices.recording_ready.pending', $tally->pending, [], $group);
// if ($tally->skipped > 0) $sentences[] = $terminology->choice('live.notices.recording_ready.skipped', $tally->skipped, [], $group);
// return [...counts, 'summary' => $tally->isEmpty() ? null : implode(' ', $sentences),
//         'help' => __('live.notices.recording_ready.help')];
```

```ts
// resources/js/components/series/LiveSessionPanel.vue — one optional field on
// the row type the panel already reads `state` from (T-123's `LiveEpisode`,
// as T-126 and T-127 extend it), so the page and its types need no change and
// no new prop is declared.
interface RecordingEmailStatus {
    sent: number;
    failed: number;
    pending: number;
    skipped: number;
    /** Whole sentences, already in the Group's words. Null when no row exists. */
    summary: string | null;
    /** What "sent" means. Shown under the summary. */
    help: string;
}

export interface LiveEpisode {
    // ...T-123's, T-126's and T-127's fields...
    recordingEmail?: RecordingEmailStatus | null;
}
```

The panel renders the status under the recording list whenever the row's
`recordingEmail?.summary` is set: two `<span class="mt-1 block">` lines, the
summary and then the help, muted as the rest of the row is; when
`failed > 0` the summary line starts with `InlineNotice`'s warning icon
(`AlertTriangle`, `text-warning`, `aria-hidden`) and takes `text-warning`.
Spans, because the row sits inside the page's paragraph (Decisions). No new
inline English: every word arrives in the prop.

`app/Console/Commands/MailCheckCommand.php`: `T-128` already gives the
scratch Group a zone, adds a live Episode (`Live clinic`, a day ahead) and
pastes a recording on it, so that Episode is `ready` and never a candidate.
This task adds a **second** live Episode in `scratch()`, inside the same
`runFor()`, after `T-128`'s — added an hour ahead, because `add()` refuses a
past start, then moved into the past through `T-124`'s `update()`:

```php
$nudged = app(EpisodeService::class)->add(
    $series, 'Missing recording', EpisodeType::Live, EpisodeProvider::Link,
    ['join_url' => 'https://meet.google.com/abc-defg-hij', 'records' => true], false,
    CarbonImmutable::now()->addHour(), 60,
);
app(EpisodeService::class)->update($series, $nudged->getKey(), [
    'starts_at' => CarbonImmutable::now()->subHours(14),
    'length_minutes' => 60,
]);
```

`scratch()` returns it beside `T-128`'s (`[$user, $series, $peer, $episode, $nudged]`).
In `send()`, after the grant and `T-128`'s paste, inside the same `runFor()`,
`queueCreatorNudges(CarbonImmutable::now())` goes before `T-128`'s
`sendDue(CarbonImmutable::now()->addDays(2))` — two days on, because the
Peer's notice waits for Join's window to close — which then sends both; the
nudged session is overdue by then, and still needs its recording. `EXPECTED`
becomes 11 (`T-128` made it 10), the class docblock says eleven, and the
subject `live.mail.recording_needed.subject` joins the list
`docs/tinker/mail.md` prints.

`docs/flows/live-sessions.md`: a "Telling the creator" section — the chain
`qori:sessions:notify → CurrentGroup::runFor() → SessionNoticeService::creatorNudgeCandidates() → queueCreatorNudges() → sendDue() → RecordingNeededNotification`,
the window, the states that qualify and the ones that never do, and the
recipient — and "The tally on the creator's page" —
`SeriesController::show() → SessionNoticeService::talliesFor()`, what "sent"
means, and that the Peer's card is unaffected by any of it.

`docs/tinker/live-sessions.md`: a recipe that lists the candidates for one
Group and runs the command dry:

```php
$group = App\Models\Group::first();
$now = Carbon\CarbonImmutable::now();

app(App\Support\CurrentGroup::class)->runFor(
    $group,
    fn () => app(App\Services\SessionNoticeService::class)->creatorNudgeCandidates($now)->pluck('title'),
);
```

```bash
php artisan qori:sessions:notify --dry-run   # names each candidate, writes nothing
```

## Copy

All in `lang/en/live.php`. The `mail.*` lines are read through
`Terminology::line()` with the Group; the `notices.*` count lines are
`trans_choice` lines read through `Terminology::choice()`; `help` carries no
noun and is read with `__()`. No line below says "live now", "has ended", "on
its way" or "processing" (`D-026`).

| Key                                    | File               | English                                                                                                                                                                                                                                         |
| -------------------------------------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `live.mail.recording_needed.subject`   | `lang/en/live.php` | Add the recording of :title                                                                                                                                                                                                                     |
| `live.mail.recording_needed.intro`     | `lang/en/live.php` | :title was scheduled to end :when, and no recording has been added to it yet.                                                                                                                                                                   |
| `live.mail.recording_needed.paste`     | `lang/en/live.php` | If it was recorded, paste the link on the :series page and every :peer with access gets one email about it.                                                                                                                                     |
| `live.mail.recording_needed.none`      | `lang/en/live.php` | If it wasn't recorded, say so on the same page and the :peer_plural see that instead of waiting.                                                                                                                                                |
| `live.mail.recording_needed.action`    | `lang/en/live.php` | Open the :series                                                                                                                                                                                                                                |
| `live.mail.recording_needed.outro`     | `lang/en/live.php` | This is the only reminder for this session, and it went to you alone.                                                                                                                                                                           |
| `live.notices.recording_ready.sent`    | `lang/en/live.php` | {0} Recording email: not sent to anybody yet.\|{1} Recording email: sent to one :peer.\|[2,*] Recording email: sent to :count :peer_plural.                                                                                                     |
| `live.notices.recording_ready.failed`  | `lang/en/live.php` | {1} One couldn't be sent after Qori tried again :attempts times. The recording stays on the :series page either way.\|[2,*] :count couldn't be sent after Qori tried again :attempts times. The recording stays on the :series page either way. |
| `live.notices.recording_ready.pending` | `lang/en/live.php` | {1} One is still to go.\|[2,*] :count are still to go.                                                                                                                                                                                          |
| `live.notices.recording_ready.skipped` | `lang/en/live.php` | {1} One address Qori no longer writes to.\|[2,*] :count addresses Qori no longer writes to.                                                                                                                                                     |
| `live.notices.recording_ready.help`    | `lang/en/live.php` | Sent means the mail service accepted it. Qori can't yet see whether it arrived.                                                                                                                                                                 |

The greeting is `T-128`'s shared `live.mail.greeting` ("Hi :name,"), read
here and not declared again. `:when` is `ZonedTime::describe()`'s answer for
the scheduled end (`T-128`'s `live.mail.when` or `live.mail.when_both`);
`:attempts` is `config('qori.live.notice_attempts')`, the retries after the
first try; `:count` is the branch's own count. No article sits directly
before a noun placeholder, which
`TerminologyTest::test_no_lang_line_puts_an_article_before_a_noun` checks.

## Routes

None. The nudge is sent by `T-128`'s command and the tally rides on the
existing `share.series.show` page.

## Tests

**New: `tests/Feature/Mail/RecordingNeededTest.php` — 10 cases**
(`Notification::fake()` in `setUp`; a `scene()` helper as
`tests/Feature/Series/LiveSessionTest.php:41-60` with the owner's own
`timezone` as a parameter; `liveEpisode(Series $series, CarbonImmutable $endsAt, array $content = [])`
creating through `$series->episodes()->create([...])` with `starts_at` an hour
before `$endsAt`, `content` `['join_url' => 'https://zoom.us/j/123', 'records' => true, ...$content]`;
`grant(Series, User)` inside `CurrentGroup::runFor()`; a fixed
`$now = CarbonImmutable::parse('2026-10-02T12:00:00Z')`; every service call
inside `CurrentGroup::runFor($group, …)`)

1. `test_it_queues_one_nudge_for_the_owner_and_sends_it` — ended 13 hours
   before `$now`, one active Access; `queueCreatorNudges($now)` returns 1 and
   the row has kind `creator_recording_needed`, `user_id` the owner,
   `recording_id` null, `publication` 1, status `pending`; `sendDue($now)`
   returns 1, the row is `sent` with `sent_at`;
   `Notification::assertSentTo($owner, RecordingNeededNotification::class)`;
   `assertNotSentTo($peer, RecordingNeededNotification::class)`.
2. `test_it_waits_the_configured_hours_and_forgets_after_the_window` — ended
   11 hours ago: no candidate; ended 8 days ago: no candidate;
   `config(['qori.live.creator_nudge_hours' => 2])` makes the first one a
   candidate, so the number is read and not restated.
3. `test_it_sends_nothing_once_a_recording_is_published_and_again_once_it_is_hidden`
   — `RecordingService::paste()` (`T-126`): no candidate;
   `RecordingService::hide()` (`T-127`): a candidate again, because the state
   decides and the row does not.
4. `test_it_skips_cancelled_not_recorded_and_live_only_sessions` — three
   Episodes ended 13 hours ago with `cancelled_at`, `not_recorded_at` and
   `records => false` in `content`: zero candidates; a fourth with no Access
   at all is a candidate, because `D-028` names no such condition.
5. `test_it_nudges_once_across_runs` — in this order: with one candidate
   Episode, queue and send, then queue and send again: one row,
   `assertSentToTimes($owner, RecordingNeededNotification::class, 1)`. Then
   add a second candidate Episode and run a third time: two rows, the first
   untouched (`updated_at` and `sent_at` unchanged), and
   `assertSentToTimes($owner, RecordingNeededNotification::class, 2)`.
6. `test_it_skips_a_suppressed_owner_address` —
   `SuppressionService::hardBounce($owner->email)` before `sendDue()`: the row
   is `skipped`, `Notification::assertNothingSent()`.
7. `test_it_names_the_scheduled_end_in_the_owners_zone_with_the_groups_beside_it`
   — owner `America/New_York`, Group `Australia/Brisbane`, `ends_at`
   `2026-10-01T02:00:00Z`: `toMail($owner)->render()` contains `EDT` and
   `AEST`; the action URL is
   `route('share.series.show', ['group' => $group->slug, 'series' => $series->slug])`;
   with the owner's `timezone` null the body names `AEST` once and no other
   zone.
8. `test_it_speaks_the_groups_vocabulary` — a `pro` Group with the labels
   `tests/Feature/TerminologyTest.php:85-96` uses and an Episode title without
   the word: the rendered mail contains `Trail` and `Ruffies` and neither
   `Series` nor `Peers`; the subject carries the Episode title.
9. `test_it_dry_runs_without_writing_or_sending` — one candidate;
   `$this->artisan('qori:sessions:notify --dry-run')->expectsOutputToContain($episode->title)->assertSuccessful()`;
   no `session_notices` row, `assertNothingSent()`; the plain run then
   writes one row and sends once.
10. `test_a_nudge_is_skipped_when_the_creator_answers_before_it_goes` — two
    candidates queued and not yet sent; one gets a recording through
    `RecordingService::paste()`, the other is declared not recorded through
    `LiveSessionService::declareNotRecorded()` (`T-127`); `sendDue($now)`
    sends nothing and leaves both rows `skipped` with `error` `resolved`.

**New: `tests/Feature/Series/RecordingEmailStatusTest.php` — 3 cases**
(the creator signed in; rows written with
`SessionNotice::query()->create([...])` inside `CurrentGroup::runFor()`;
props read as `LiveSessionTest.php:256-266` does)

1. `test_it_tallies_the_recording_email_per_live_episode` — for one live
   Episode, `recording_ready` rows: two `sent`, one `failed` with
   `next_attempt_at` null, one `failed` with `next_attempt_at` an hour ahead,
   one `pending`, one `skipped`, and one `creator_recording_needed` row that
   must not count; `series.episodes.0.recordingEmail` is
   `sent 2, failed 1, pending 2, skipped 1`, `summary` contains
   `sent to 2 Peers`, `One couldn't be sent after Qori tried again 3 times`
   and `2 are still to go`, `help` is `live.notices.recording_ready.help`.
2. `test_it_says_nothing_for_an_episode_without_rows_and_nothing_at_all_for_a_file`
   — a live Episode with no rows: counts 0 and `summary` null; a File Episode:
   `recordingEmail` null, as its `state` is.
3. `test_it_counts_in_the_groups_words` — the `pro` Group and labels of case 8
   above, two `sent` rows: `summary` contains `Ruffies` and not `Peers`.

**Changed:**

- `tests/Feature/Mail/MailContentTest.php` — the `$senders` map (`:162-168`)
  gains `'RecordingNeededNotification' => 'SessionNoticeService'`; no method
  changes.
- `tests/Feature/Console/NotifySessionsCommandTest.php` —
  `test_it_logs_a_heartbeat_each_run` pins the heartbeat's whole context, so
  both of its expectations gain `'nudges_queued' => 0`.

Total: 13 new cases.

## Acceptance

- [ ] A live Episode scheduled to end more than `qori.live.creator_nudge_hours`
      ago with no published recording, whether or not anybody has been
      granted, gets the Group owner one email on the next
      `qori:sessions:notify` run and never a second, whether the run repeats
      or a later part is added
- [ ] A cancelled session, one declared not recorded, one marked Live only,
      and a session older than `qori.live.notice_window_days` send nothing
      (owner acceptance 9: no recording shows truthful status and a creator
      recovery)
- [ ] The email names the scheduled end in the owner's zone with the Group's
      zone beside it when the two differ, speaks the Group's words, links to
      the creator's Series page and says it went to the owner alone
- [ ] A suppressed owner address is skipped and the ledger says so; a failed
      send follows `T-128`'s retry and is then left for `T-019`
- [ ] A nudge whose session gets its recording, or is declared not recorded,
      before the email goes is skipped as `resolved`, and nothing is sent
- [ ] The creator's Series page says, on each live Episode with any
      `recording_ready` row, how many were sent, failed, are still to go and
      were skipped, in the Group's words, with what "sent" means beneath it;
      a failed row with a retry still due counts as still to go, an Episode
      with no rows shows nothing, and the Peer's card is unchanged
- [ ] `--dry-run` names each candidate and writes and sends nothing
- [ ] `qori:mail:check` sends the nudge through the service and reads it back
- [ ] `docs/flows/live-sessions.md` describes the nudge and the tally, and
      `docs/tinker/live-sessions.md` drives both
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~`qori.live.creator_nudge_hours` is 12, provisional (`D-028`): confirm, or
  change the number in `T-123`'s config block — anyone's.~~ **Decided
  27 September 2026: 12.** Sooner would land while an ordinary upload is
  still being processed or shared; later leaves the class waiting longer
  before anyone reminds the creator. The Peer's card waits 48 hours
  (`recording_wait_hours`) before it says overdue, so at twelve the creator
  hears well before their class sees that.
- ~~`T-128` `ready`, so `SessionNoticeService`'s constructor,
  `notificationFor()`, the skips inside `sendDue()`, `SessionNotice`'s
  attributes, `NotifySessionsCommand`'s per-Group closure and
  `App\Support\ZonedTime` are frozen as this draft cites them — anyone's;
  keep draft until it is.~~ **Answered 27 September 2026:** `T-128` is `done`
  (qori `ad23982`), and this spec is reconciled with it — see the Re-scope
  log.
- ~~Whether a Series with no active Access should skip the nudge. `D-028` and
  this draft nudge regardless; if the owner wants silence for a class nobody
  has been granted, `creatorNudgeCandidates()` gains
  `->whereIn('series_id', Access::query()->active()->select('series_id'))`
  and one case, and the fourth case's last clause flips — the owner's.~~
  _Asked_ 26 September 2026 and unanswered. Built as `D-028` has it —
  nudged regardless — since the build does not wait on a change the owner
  may never ask for, and the flip stays one `whereIn` and one case.

## Re-scope log

**2026-09-27 — reconciled with `T-128` and the code as built.**

- **A live row's facts are keys on the row, not a `live` array.** `T-123`,
  `T-126` and `T-127` put `records`, `joinUrl`, `state`, `notRecordedAt` and
  `recordings` on each row of `series.episodes`, each null or empty off a
  live Episode. `recordingEmail` joins them. The status test reads
  `series.episodes.0.recordingEmail`, and a File Episode's is null.
- **The status line is spans.** The row renders inside the page's paragraph
  (`resources/js/pages/share/series/Show.vue`, the `<p>` around
  `LiveSessionPanel`), and both `InlineNotice`'s `<div>` and the draft's
  `<p>` lines are torn out of a paragraph by the HTML parser, which is why
  `T-127`'s actions are buttons. So the lines are spans, and the failed case
  carries `InlineNotice`'s warning icon and colour (Decisions).
- **`SessionNoticeService` is as `T-128` built it.** The constructor already
  holds `LiveSessionService` as `$sessions`, not `$live`: `T-128` needed the
  Join window. `notificationFor()` already takes the Group as its fourth
  parameter. Its return type widens, and its materials read moves into the
  `recording_ready` arm, the only one that uses it.
- **`sendDue()`'s checks as built** are stale, no such user, suppressed, the
  Episode or Series gone, no active Access, cancelled, then
  `recording_ready`'s own: nothing visible, and postponed until Join closes.
  Only the Access check is gated by kind. A row whose Episode or Series is
  gone is skipped for every kind, as it is today.
- **A nudge is checked again before it goes** (Decisions), which the draft
  did not do: a retry 15, 60 or 240 minutes later could otherwise tell a
  creator no recording has been added when one had been. It adds
  `SKIPPED_RESOLVED`, an Acceptance line and `RecordingNeededTest`'s tenth
  case.
- **`qori:mail:check` sends ten since `T-128`**, so this makes eleven, not
  nine. Its send clock is two days on, `T-128`'s, and the nudged session is
  still waiting on its recording then.
- **Candidates are listed under `--dry-run` only**, as Scope says. The
  Code's sketch printed them on every run, which would read them twice. The
  heartbeat gains `nudges_queued`, and `NotifySessionsCommandTest` pins the
  heartbeat's whole context, so its file joins the table.
- **Nothing schedules `qori:sessions:notify`** — the owner's hold of
  26 September 2026, now `T-206`'s. The nudge is queued and sent whenever
  the command runs, by hand until `T-206` lands, as `T-128`'s notices are.
- **`bin/tasks --check` in `qori-plan`** replaces `php artisan qori:tasks
  --check`: the planning moved on 21 September 2026.

## Notes

`T-143` edits `creatorNudgeCandidates()`, not the command: an Episode Qori is
still looking for (`provider = zoom`, a usable Connection, a link a finder
`handles()`) is held until `qori.live.recording_wait_hours`, and everything
else keeps the rule here. `T-134` relies on the fourth case: a cancelled
Episode is never a candidate because `stateFor()` says `cancelled`, so its
own "cancelled sends no nudge" test asserts through this method.

`Episode` has no `series()` relation today (`app/Models/Episode.php`);
`T-126` adds it (its Files row for `app/Models/Episode.php`), and
`app/Models/Episode.php` is not this task's file. The arm in
`notificationFor()` needs neither: it receives the Series `T-128`'s
`subjectsFor()` resolved for the row and re-queries nothing.

`T-128`'s draft is edited to make the active-Access skip per kind: its Notes
sentence "`sendDue()`'s five skips apply to every kind" becomes "stale,
suppressed and session-cancelled apply to every kind; the active-Access skip
is every kind but `creator_recording_needed`, and `recording_unavailable` is
`recording_ready`'s alone", its `sendDue()` docblock says the same, and
`notificationFor()`'s return type is `Illuminate\Notifications\Notification`
so this task's arm and `T-138`'s fit without a second widening.

`RecipientStatus` carries `Bounced` and `Complained` for campaigns; the ledger
never writes them (`D-028`), so `talliesFor()` counts four statuses and
ignores the rest rather than inventing a fifth sentence.

`docs/tinker/mail.md:27` already says "all seven" beside a listing of six;
`T-128` and this task each move the count, and whichever lands second makes
the sentence true.
