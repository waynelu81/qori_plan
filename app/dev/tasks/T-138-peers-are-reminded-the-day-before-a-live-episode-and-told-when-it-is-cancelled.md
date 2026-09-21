---
id: T-138
title: Peers are reminded the day before a live Episode, and told when it is cancelled
stream: classroom
status: draft
owner: unassigned
estimate: M
depends: T-128, T-133, T-134
blocks: none
---

# T-138 — Peers are reminded the day before a live Episode, and told when it is cancelled

> **Draft.** Written on 18 September 2026 from `D-028` and the classroom
> brief; not to be started — see [`../PROCESS.md`](../PROCESS.md). It builds
> on names three drafts hold (`T-128`'s ledger, `T-133`'s calendar file,
> `T-134`'s cancel), so it waits on all three becoming `ready`; what has to
> happen before it can be marked `ready` is listed at the bottom.

## Why

Nothing reminds a Peer that a class is tomorrow. `T-128` builds the outbox —
`session_notices`, `qori:sessions:notify`, the retry state on the row — and
produces one kind, `recording_ready`; `T-129` adds `creator_recording_needed`;
`SessionNoticeKind::DayBefore` and `SessionCancelled` exist as cases with no
producer. `communications-policy.md` decided the tiers on 6 September 2026 —
Free none, Start one fixed, Pro several
(`docs/planning/communications-policy.md:55-64`) — and left four questions
open (`:68-85`): reminders before what, on whose clock, whether they are
metered, and that nothing ran a schedule. `D-028` answers every one: before a
live Episode's `starts_at`; rendered in the recipient's own zone with the
Group's beside it; unmetered, with the per-run cap and the unique ledger as
the guard; and the Laravel Cloud scheduler has run since 11 September 2026
(`docs/planning/release-prerequisites.md:24`). `T-124` moves a session and
sends nothing, saying in its form that no email goes out, and leaves the
deletion of reminder rows to this task; `T-134` writes `cancelled_at`, its
panel and its toast say no email goes out, and a Peer who was reminded of
Tuesday is told nowhere that Tuesday is off. `T-133` builds the calendar file
and serves it from the card, attached to nothing.

Afterwards, on a Group whose plan allows it, every run of
`qori:sessions:notify` queues one `day_before` row per active Access for each
live Episode whose reminder time has arrived —
`qori.live.reminder_minutes_before` before the start — and sends it in the
same run: the session in the Peer's zone with the Group's zone beside it,
when Join opens, whether a recording will follow, the calendar file attached,
and a button that lands on the Episode's card. A Peer granted after that run
is reminded on the next one while the start is still more than an hour away.
A change to the start or the length deletes the Episode's reminders so they
go again for the new time, and no "moved" email goes. Cancelling tells every
Peer who was already reminded, once; Undo tells nobody anything and reminds
nobody twice. Free Groups get none of it; the Peer's card says a reminder is
coming only where one is, and the creator's panel and toast say who was
told. Every rule here is `D-028`'s; the code is the first place it is written
down as code.

## Decisions taken to make this specifiable

**Whether a Group gets reminders is a boolean plan key,
`qori.plans.<plan>.session_reminders`, read through `Group::allows()`.**
`Group::allows(string $feature)` (`app/Models/Group.php:156-159`) is already
how a plan grants a feature (`public_listing`, `custom_vocabulary`), and the
block's own docblock says limits live in config so pricing can change without
touching stored data. Free `false`; Start, Pro and School `true`, from
`communications-policy.md:55-64` and `D-028`. This is the one exception to
the stream's "`config/qori.php` — `T-123` only": the key is a tier lever
under `plans` (`config/qori.php:287-367`), not a `live.*` number, and `T-123`
has landed before this task can be claimed (the chain is `T-123` → `T-124` →
`T-126` → `T-127` → `T-128` → here), so the two edits never overlap.

**The reminder is queued by the sweep, from the clock, never at grant or at
creation.** `D-028`: recipients are worked out at send time. A grant cannot
know whether the reminder time has arrived, and creation cannot know who
will hold access in three weeks. `queueReminders($now)` runs per Group inside
the command's `runFor()` beside `T-129`'s `queueCreatorNudges($now)`, before
`sendDue()`, so a row queued this run goes this run, and a Peer granted after
the first queue is picked up by the next.

**The window is `starts_at − reminder_minutes_before ≤ now < starts_at − LATE_REMINDER_CUTOFF_MINUTES`,
and the cutoff is a constant on the service, `60`.** The first bound is
`T-123`'s config key; the second is not copy, is written once, and
`config/qori.php`'s `live` block is `T-123`'s to declare. A reminder that
lands with less than an hour to go is noise beside the card's own Join, which
opens `qori.live.join_opens_minutes` before the start. If the owner wants the
cutoff tunable it moves into `qori.live` in a task of its own.

**`insertOrIgnore()` under the unique key is the idempotence, exactly as
`T-128`.** `(episode_id, user_id, kind, publication)` means a second run
inserts nothing, and a Peer who already holds a `day_before` row for the
Episode — whatever its status — is never queued again. That one fact is also
what makes Undo "not re-send" below. The two producers here write their rows
through one private `pendingRow()`, the same shape `T-128`'s
`queueRecordingReady()` writes inline; `T-128`'s array is not touched.

**A change to `starts_at` or `ends_at` deletes every `day_before` row of the
Episode, `sent` ones included, inside the lock.** `D-028`: "so the reminder
fires for the new time, and no 'moved' email goes". The block sits in
`T-124`'s `withLockedContent()` callback after the `touchSchedule()` call, on
`$locked->isDirty(['starts_at', 'ends_at'])` — still true there, because the
save happens after the callback — so the delete and the move are one commit.
A Peer reminded of Tuesday is reminded again of Thursday, by design. A link or
Recorded-switch change alone deletes nothing, and resubmitting the same time
deletes nothing, because `touchSchedule()` only dirties the columns when they
moved.

**Cancelling queues `session_cancelled` for those who hold a `sent`
`day_before` row, and deletes the rows that had not gone.** `D-028`: "a
cancellation sends `session_cancelled` only to those who already hold a
`day_before` row". Read as a `sent` row: the person who received the
reminder is the person who might turn up, and a pending or failed row is a
reminder nobody received, so there is nothing to retract. The pending row is
deleted rather than left for `T-128`'s cancelled check to skip, because a
`skipped` row would block a fresh reminder after Undo under the unique key.
Both writes happen inside `T-134`'s `cancel()` lock callback, so a cancel and
its notices are one commit. Confirmation of the reading is asked for below.

**`cancel()` resolves `SessionNoticeService` from the container, not by
constructor.** `T-129` promotes `LiveSessionService` into
`SessionNoticeService` for `stateFor()`, so the reverse injection would be a
cycle the container cannot build. `app(SessionNoticeService::class)` inside
`cancel()` is the move `T-134` already makes for `EpisodeService` inside
`copy()`, for the same reason. `EpisodeService` takes the notice service by
constructor: nothing on that side points back.

**Undo touches the ledger not at all.** `sent` `day_before` rows stay and
block a second reminder under the unique key; a `session_cancelled` row not
yet sent is skipped at send time when `content['cancelled_at']` is no longer
set; a Peer whose pending reminder was deleted at cancel gets a fresh row on
the next run if the window still holds. No "it's back on" email (`D-028`);
`T-135`'s copied message is the creator's way to say so.

**`sendDue()`'s checks become kind-aware, and three skip reasons are added.**
`T-128`'s stale, suppressed and access-inactive checks apply to every kind;
its `session_cancelled` check applies to every kind but `SessionCancelled`;
its `recording_unavailable` stays `RecordingReady`'s. New:
`SKIPPED_SESSION_RESTORED` for a `SessionCancelled` row whose session is no
longer cancelled; `SKIPPED_SESSION_PASSED` for a `DayBefore` row whose
`starts_at` is not ahead of `$now` — the scheduler-was-off case, where the
first run after a fortnight must not remind anybody of last week; and
`SKIPPED_PLAN_EXCLUDED` for a `DayBefore` row whose Group no longer
`allows('session_reminders')` — a downgrade between queue and send. Reasons
are string constants, diagnostics for the ledger, never copy, as `T-128`'s
are. The order is stated in Code.

**Two notifications, built with what they render, as `T-128`'s is.**
`SessionReminderNotification(Episode, Series, Group, string $calendar)` — the
calendar file's text is handed in, produced by
`CalendarInvite::for($episode, $series)` (`T-133`) in `notificationFor()`, so
the notification runs no query and a test can construct it, and the sweep
builds one file per row. `SessionCancelledNotification(Episode, Series, Group)`.
Nouns go through `app(Terminology::class)->line($key, $replace, $group)` with
the Group passed explicitly because a sweep has no current Group (`D-028`);
dates through `App\Support\ZonedTime`, the mail zone rule `T-128` states. No
`Queueable`, no `ShouldQueue`.

**The reminder attaches the calendar file under `T-133`'s download name;
the cancellation attaches nothing.** `MailMessage::attachData()`
(`vendor/laravel/framework/src/Illuminate/Notifications/Messages/MailMessage.php:308-312`)
with `CalendarInvite::filenameFor($episode)` and `CalendarInvite::MIME`, so
the file a Peer gets by mail is the file the card serves, named and typed by
the one class that knows the format. `T-133` declares both the name and the
MIME constant; this task declares no calendar constant of its own. `T-133` left the
cancellation's attachment to this task: its file is `METHOD:PUBLISH`, and a
cancel does not bump `SEQUENCE`, so whether a calendar application applies a
re-imported `STATUS:CANCELLED` is not something Qori has observed. A promise
that might be false is left out; the cancellation says to remove the entry
by hand. Both buttons are `shared.episodes.show` (`D-024`) and the file's own
`URL` is the same route (`T-133`), so nothing in either message is a vendor
destination and the join link appears nowhere — owner acceptance 14's "no
message sends a stale live destination".

**The reminder says what the creator's switch says, and nothing Qori has not
observed.** `records` true: "Can't make it? If the session is recorded, the
recording will be added to the same page and you'll get an email" —
conditional, because the creator can still declare it not recorded
(`T-127`), and the email is `T-128`'s. `records` false: "live only and won't
be recorded". `D-026`'s rule holds: no line under `live.*` says "live now",
"has ended", "on its way" or "processing".

**One shared outro, `live.mail.outro`, for the two notices this task adds.**
Both end with the same sentence. `T-128`'s `live.mail.recording_ready.outro`
is word for word the same line and is **not** touched here: it is another
task's key, and repointing it is a wording-tier follow-up either owner may
take, not this task's work. So this task adds one key and reads it from both
notifications.

**The Peer's card gets one line in `upcoming`, shown until the reminder is
due, or nothing.** `SharedController::liveCard()` (`T-125`) adds
`copy.reminder`: the line when `$group->allows('session_reminders')` and
`$now` is earlier than `starts_at − reminder_minutes_before`, else `null`;
the card renders it under the `upcoming` message when present. Bounded at
the reminder time rather than the cutoff so the line never says "you'll get"
about a reminder that has already gone; a Peer granted inside the window
sees no line and gets the email on the next run. On Free the line is absent,
which is the honest form of "Free gets none" — `T-135`'s copied message is
the nudge there. No English in Vue; the shape gains one nullable key, on the
page that declares it (`T-125` puts `LiveCard` in `shared/Show.vue`), as
`T-133`'s type-only edit does.

**The creator's "no email goes out" lines are picked by plan, in the
controllers that already build them.** `T-134` hands this task the rewrite
of `live.panel.cancelled` and `series.session_cancelled`, and `T-124`'s
`series.live.edit.no_email` stops being the whole truth on a plan whose
reminders go again after a move. Each keeps its wording for a Group whose
plan sends nothing, and gains a sibling key for one that does:
`SeriesController::show()` picks `livePanel.cancelled` and `edit.noEmail` by
`$series->group->allows('session_reminders')`, `LiveSessionController::cancel()`
picks the toast the same way. The prop names do not change, so
`LiveSessionPanel.vue` is not edited.

**`--dry-run` queues nothing.** `T-129` returns from the per-Group closure
before queueing on a dry run; the reminder step sits after that return. The
heartbeat gains `reminders_queued`.

**`qori:mail:check` sends twelve.** `T-128` makes it eight and `T-129` nine;
this task adds a second upcoming live Episode to the scratch Series, queues
the reminders — two, because `T-128`'s Episode is a day ahead as well —
sends them, cancels the new Episode and sends the cancellation, with the
scratch Group on plan `start`. `T-128`'s Episode cannot be the one cancelled:
it holds a pasted recording, and `T-134` refuses that. `MailContentTest`'s
senders map gains both notifications. `EXPECTED` becomes `12`.

**An archived Series sends no reminder.** `queueReminders()` reads the
Episodes of `Series::query()->unarchived()` (`app/Models/Series.php:288-291`):
archiving is the creator's "not now", and a purged Series has no Episodes.
A cancelled session is dropped in PHP through `T-123`'s
`Episode::isCancelled()`, as `T-129`'s candidates are filtered, rather than
by a JSON path in SQL. `recording_ready` needs no archive rule, because a
paste is the creator's act.

**No new table, column, route or factory.** The ledger and its unique key
are `T-128`'s and `kind` already carries both cases; nothing is downloaded
here (`T-133` serves the file); tests make rows through `queueReminders()`
and `queueCancellation()` and move the clock with
`CarbonImmutable::setTestNow()`.

**`communications-policy.md` is annotated, not rewritten.** Its four open
questions get their answers with the date and `D-028`; its Pro row stays as
intent, with one line saying Pro gets the one fixed reminder until custom
templates. It is a live policy document, not planning history, and nothing
else in the repository says where those questions went.

## Preconditions

**Data this task verifies against:** a clean database. The feature tests
build the scene `T-128`'s tests build: a Group on plan `start` with
`timezone` `Australia/Brisbane` and an owner, the way
`tests/Feature/Series/LiveSessionTest.php:40-58` does; a Series through its
factory; the clock set to `2026-10-01 00:00:00` UTC with
`CarbonImmutable::setTestNow()` before anything is added, because
`EpisodeService::add()` refuses a past start; a live Episode "Live clinic"
through `EpisodeService::add()` with `T-123`'s `$startsAt` (1 November 2026
09:00 Brisbane, which is 31 October 23:00 UTC) and `$lengthMinutes` 60,
content `['join_url' => 'https://zoom.us/j/91827405566', 'records' => true]`;
Peers through `AccessService::grant()` inside `CurrentGroup::runFor()`. The
framework resets the test clock between tests.

**Equipment:** Mailpit on 1025/8025 for `qori:mail:check` and the tinker
recipe; a calendar application (Apple Calendar or Google Calendar) to import
the attached `.ics` once and see it land at the right hour in the reader's
zone. Nothing for the suite, which runs on the `array` mailer.

**Spike:** none owed. No vendor payload is read or written; the calendar
file is an open standard (`T-133`) and the mailer is Laravel's.

## Scope

**In:**

- `qori.plans.{free,start,pro,school}.session_reminders`.
- `SessionNoticeService::queueReminders()`, `queueCancellation()`,
  `forgetReminders()`, the private `pendingRow()` and `activeAccessesFor()`,
  `LATE_REMINDER_CUTOFF_MINUTES`, the three skip reasons, the kind-aware
  checks in `sendDue()`, two arms in `notificationFor()`.
- `SessionReminderNotification` with the calendar file attached, and
  `SessionCancelledNotification`; their lines in `lang/en/live.php`.
- `EpisodeService::update()` deleting the Episode's reminders when the
  schedule moved; `LiveSessionService::cancel()` queueing the cancellation.
- `qori:sessions:notify` queueing reminders before it sends; the heartbeat's
  `reminders_queued`; `--dry-run` queueing nothing.
- The Peer card's `upcoming` reminder line; the creator's panel, edit-form
  and toast lines picked by plan.
- `qori:mail:check` sending and reading twelve.
- `docs/flows/live-sessions.md`, `docs/flows/series.md`,
  `docs/tinker/live-sessions.md`, `docs/tinker/mail.md`, the annotation in
  `communications-policy.md`.

**Out:**

- An hour-before reminder, Pro's several offsets and its own template
  (`D-028`: they wait for custom templates, which `PLAN.md` defers).
- A "moved" email on a reschedule, and an "it's back on" email after Undo
  (`D-028`).
- A calendar file on the cancellation mail (see the decision above).
- A per-Peer "no reminders" preference, quiet hours, digests, a consent
  gate, campaign metering, an unsubscribe footer (`D-028`).
- Reminders on Free: a policy amendment the owner has not made (`D-028`
  leaves the question open).
- `CalendarInvite` and `shared.episodes.calendar` (`T-133`); `cancel()`,
  `restore()`, `copy()` and the `cancelled` copy on the card (`T-134`);
  `T-124`'s edit path beyond the one block this task adds to it.
- `recording_ready` (`T-128`), `creator_recording_needed` (`T-129`), the
  deliberate re-send (`T-140`).
- A reminder tally on the creator's card: `T-129`'s "Recording email: sent to
  :sent, :failed failed" reads `recording_ready` rows, and widening it is its
  own wording task.
- Confirmed delivery (`T-032`), alerting on exhausted rows (`T-019`), a
  worker (`T-018`).
- Reminders for a Series with no live Episode: `communications-policy.md`'s
  first question is answered as live Episodes only.
- The next session on the public page before buying (`T-135`).
- Any change to `LiveSessionPanel.vue`: its props keep their names and
  receive the plan-picked lines.

## Files

| Path                                                   | Change | Notes                                                                                                                                                                                                           |
| ------------------------------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `config/qori.php`                                      | edit   | `plans.{free,start,pro,school}.session_reminders`; the one exception to `T-123`'s claim, see decisions                                                                                                          |
| `app/Services/SessionNoticeService.php`                | edit   | `queueReminders()`, `queueCancellation()`, `forgetReminders()`, `pendingRow()`, `activeAccessesFor()`, `LATE_REMINDER_CUTOFF_MINUTES`, three skip reasons, kind-aware `sendDue()`, two `notificationFor()` arms |
| `app/Notifications/SessionReminderNotification.php`    | new    | Mail only, not queued; the `.ics` attached under `T-133`'s name and `CalendarInvite::MIME`; `Terminology::line()` with the Group                                                                                |
| `app/Notifications/SessionCancelledNotification.php`   | new    | Mail only, not queued; no attachment                                                                                                                                                                            |
| `app/Services/EpisodeService.php`                      | edit   | `SessionNoticeService` by constructor; `forgetReminders()` inside the lock when the schedule moved                                                                                                              |
| `app/Services/LiveSessionService.php`                  | edit   | `cancel()` resolves `SessionNoticeService` and calls `queueCancellation()` inside its lock                                                                                                                      |
| `app/Console/Commands/NotifySessionsCommand.php`       | edit   | `queueReminders($now)` per Group beside `T-129`'s nudges, before sending; `reminders_queued` in the heartbeat                                                                                                   |
| `app/Http/Controllers/Shared/SharedController.php`     | edit   | `copy.reminder` on the live card                                                                                                                                                                                |
| `app/Http/Controllers/Share/SeriesController.php`      | edit   | `livePanel.cancelled` and `edit.noEmail` picked by plan                                                                                                                                                         |
| `app/Http/Controllers/Share/LiveSessionController.php` | edit   | `cancel()`'s toast picked by plan                                                                                                                                                                               |
| `resources/js/components/series/LiveSessionCard.vue`   | edit   | The reminder line under `upcoming`                                                                                                                                                                              |
| `resources/js/pages/shared/Show.vue`                   | edit   | Type only: `LiveCard['copy']` gains `reminder: string \| null`                                                                                                                                                  |
| `lang/en/live.php`                                     | edit   | `mail.day_before.*`, `mail.session_cancelled.*`, `mail.outro`, `state.upcoming.reminder`, `panel.cancelled_notified`                                                                                            |
| `lang/en/series.php`                                   | edit   | `session_cancelled_notified`, `live.edit.reminders_again`                                                                                                                                                       |
| `app/Console/Commands/MailCheckCommand.php`            | edit   | `EXPECTED` 12; the scratch Group on `start`; a second live Episode; queue, send, cancel, send                                                                                                                   |
| `docs/flows/live-sessions.md`                          | edit   | "Reminders and cancellations": the queue, the two chains, the skips; "Not built yet" loses `T-134`'s "a cancellation email (`T-138`)" line                                                                      |
| `docs/flows/series.md`                                 | edit   | "Editing a live Episode" (`T-124`) gains `forgetReminders()` in its chain                                                                                                                                       |
| `docs/tinker/live-sessions.md`                         | edit   | "Remind, then cancel"                                                                                                                                                                                           |
| `docs/tinker/mail.md`                                  | edit   | Twelve messages, the sample output                                                                                                                                                                              |
| `docs/planning/communications-policy.md`               | edit   | The four open questions annotated with `D-028`'s answers and the date; the Pro row's stand-in line                                                                                                              |
| `tests/Feature/Mail/SessionReminderTest.php`           | new    | 16 cases                                                                                                                                                                                                        |
| `tests/Feature/Mail/SessionCancelledTest.php`          | new    | 9 cases                                                                                                                                                                                                         |
| `tests/Feature/Console/NotifySessionsCommandTest.php`  | edit   | 2 cases                                                                                                                                                                                                         |
| `tests/Feature/Shared/LiveSessionCardTest.php`         | edit   | 1 case                                                                                                                                                                                                          |
| `tests/Feature/Series/CancelLiveEpisodeTest.php`       | edit   | 1 case; cases 1 and 2 read the plan-picked keys                                                                                                                                                                 |
| `tests/Feature/Series/EditLiveEpisodeTest.php`         | edit   | 1 case                                                                                                                                                                                                          |
| `tests/Feature/Mail/MailContentTest.php`               | edit   | The senders map gains both notifications                                                                                                                                                                        |

No route file changes: both notices leave by mail, their buttons are
`shared.episodes.show` (`T-125`), and `qori:sessions:notify` is `T-128`'s
command with one more step. No migration, factory or seeder: the ledger is
`T-128`'s and nothing new is stored. No new `routes/console.php` line: the
existing schedule runs the queue step. `docs/flows/README.md`'s row for
`live-sessions.md` already names the notices (`T-128`) and is unchanged.

## Database

None. `session_notices` (`T-128`, `D-028`) already carries `kind` with
`day_before` and `session_cancelled` as values, and its unique key
`(episode_id, user_id, kind, publication)` is what this task relies on.

## Code

```php
// config/qori.php — one key per plan inside the existing 'plans' block
// (config/qori.php:287-367), last in each plan's array, after custom_vocabulary.
// The comment is written once, above free's key; the other three carry none.

'plans' => [

    'free' => [
        // ...the plan's existing keys, ending custom_vocabulary => false...

        /*
        | Reminders before a live Episode (docs/planning/communications-policy.md,
        | D-028). Free none; Start and above one fixed day_before, in Qori's words,
        | qori.live.reminder_minutes_before before the start. Pro's own offsets and
        | its own template wait for custom templates, which PLAN.md defers, so Pro
        | and School read the same as Start here. Read through
        | Group::allows('session_reminders') by SessionNoticeService, by the Peer's
        | card to say whether a reminder is coming, and by the creator's pages to
        | say who is told.
        */
        'session_reminders' => false,
    ],

    'start' => [/* ...existing keys... */ 'session_reminders' => true],
    'pro' => [/* ...existing keys... */ 'session_reminders' => true],
    'school' => [/* ...existing keys... */ 'session_reminders' => true],

],
```

```php
// App\Services\SessionNoticeService — added to T-128's class, beside T-129's
// nudges. Imports gained: App\Enums\EpisodeType, App\Models\Group,
// App\Notifications\SessionCancelledNotification,
// App\Notifications\SessionReminderNotification, App\Support\CalendarInvite,
// Illuminate\Notifications\Notification.

/**
 * A reminder queued with less than this to go is noise beside the card's own
 * Join, so a grant inside it gets no reminder. A constant, not config:
 * config/qori.php's live block is T-123's, and this number is written once.
 */
public const LATE_REMINDER_CUTOFF_MINUTES = 60;

/** The session was undone before the cancellation went. */
public const SKIPPED_SESSION_RESTORED = 'session_restored';

/** The start had passed by the time the reminder was due to go. */
public const SKIPPED_SESSION_PASSED = 'session_passed';

/** The Group's plan stopped allowing reminders between queue and send. */
public const SKIPPED_PLAN_EXCLUDED = 'plan_excluded';

/**
 * One pending day_before row per active Access, for every live Episode of
 * this Group whose reminder time has arrived and whose start is still more
 * than LATE_REMINDER_CUTOFF_MINUTES away (D-028). Idempotent under the
 * unique key: a run finds nothing new for a Peer who already holds a row,
 * and a Peer granted after the first run is picked up by the next.
 *
 * Zero for a Group whose plan does not allow reminders, for a cancelled
 * session and for an archived Series. Runs inside CurrentGroup::runFor().
 * Returns how many rows were inserted.
 */
public function queueReminders(CarbonImmutable $now): int;
// $group = $this->current->get();
//
// if (! $group instanceof Group || ! $group->allows('session_reminders')) {
//     return 0;
// }
//
// $episodes = Episode::query()
//     ->where('type', EpisodeType::Live)
//     // Series is group-scoped and the scope survives in the subquery, so this
//     // is this Group's Series and nobody else's. Archived and purged are out.
//     ->whereIn('series_id', Series::query()->unarchived()->select('id'))
//     ->where('starts_at', '<=', $now->addMinutes((int) config('qori.live.reminder_minutes_before')))
//     ->where('starts_at', '>', $now->addMinutes(self::LATE_REMINDER_CUTOFF_MINUTES))
//     ->get()
//     ->reject(fn (Episode $episode): bool => $episode->isCancelled());   // T-123's accessor, as T-129 filters
//
// $rows = $episodes->flatMap(fn (Episode $episode): Collection => $this->activeAccessesFor($episode)
//     ->map(fn (Access $access): array => $this->pendingRow(
//         $access->group_id, $episode->getKey(), $access->user_id, SessionNoticeKind::DayBefore, $now,
//     )));
//
// return $rows->isEmpty() ? 0 : SessionNotice::query()->insertOrIgnore($rows->all());

/**
 * The session is cancelled: tell everyone who was already reminded, and
 * drop the reminders that had not gone (D-028). Called inside
 * LiveSessionService::cancel()'s lock, so it runs in the creator's Group
 * and commits with the cancellation. Returns how many session_cancelled
 * rows were inserted.
 */
public function queueCancellation(Episode $episode): int;
// $now = CarbonImmutable::now();
//
// $reminded = SessionNotice::query()
//     ->where('episode_id', $episode->getKey())
//     ->where('kind', SessionNoticeKind::DayBefore)
//     ->where('status', RecipientStatus::Sent)
//     ->get();
//
// $rows = $reminded->map(fn (SessionNotice $notice): array => $this->pendingRow(
//     $notice->group_id, $notice->episode_id, $notice->user_id, SessionNoticeKind::SessionCancelled, $now,
// ));
//
// // A reminder nobody received is nothing to retract, and a skipped row
// // would block a fresh one after Undo under the unique key.
// SessionNotice::query()
//     ->where('episode_id', $episode->getKey())
//     ->where('kind', SessionNoticeKind::DayBefore)
//     ->where('status', '!=', RecipientStatus::Sent)
//     ->delete();
//
// return $rows->isEmpty() ? 0 : SessionNotice::query()->insertOrIgnore($rows->all());

/**
 * The schedule moved: every day_before row goes, sent ones included, so the
 * next run reminds everyone of the new time and no "moved" email is needed
 * (D-028). Called inside EpisodeService::update()'s lock. Returns how many
 * rows went.
 */
public function forgetReminders(Episode $episode): int;
// return SessionNotice::query()
//     ->where('episode_id', $episode->getKey())
//     ->where('kind', SessionNoticeKind::DayBefore)
//     ->delete();

/**
 * Active Accesses to the Episode's Series with a user_id — T-128's
 * recipientsFor() without the granted_at bound.
 *
 * @return Collection<int, Access>
 */
private function activeAccessesFor(Episode $episode): Collection;
// Access::query()->where('series_id', $episode->series_id)->active()->whereNotNull('user_id')->get()

/**
 * One insertOrIgnore() row, the shape T-128's queueRecordingReady() writes
 * inline: an explicit ULID, group_id from the caller, enum values as
 * strings, timestamps by hand, because insertOrIgnore() bypasses the
 * creating hook and the casts. recording_id null, publication 1.
 *
 * @return array<string, mixed>
 */
private function pendingRow(string $groupId, string $episodeId, string $userId, SessionNoticeKind $kind, CarbonImmutable $now): array;

// sendDue() — the per-row checks, in order, kind-aware. Everything T-128 has
// stays; the three marked lines are new. Every check that fails writes
// status Skipped, error <reason>, next_attempt_at null, as T-128's skip() does.
//
//  1. stale                                   → SKIPPED_STALE                  every kind
//  2. suppressed                              → SKIPPED_SUPPRESSED             every kind
//  3. no active Access to the Series          → SKIPPED_ACCESS_INACTIVE        every kind (T-129's owner row: T-129's rule)
//  4. content['cancelled_at'] set             → SKIPPED_SESSION_CANCELLED      every kind but SessionCancelled
//  5. content['cancelled_at'] not set         → SKIPPED_SESSION_RESTORED       SessionCancelled only     (new)
//  6. $episode->starts_at <= $now             → SKIPPED_SESSION_PASSED         DayBefore only            (new)
//  7. ! $group->allows('session_reminders')   → SKIPPED_PLAN_EXCLUDED          DayBefore only            (new)
//  8. no published, unhidden recording        → SKIPPED_RECORDING_UNAVAILABLE  RecordingReady only
//  9. notify() inside try/catch               → sent, or failed with backoff

/**
 * The notification for a row's kind. Four arms once T-129 and this task
 * have landed; the return type is Notification. The calendar file is built
 * here, once per row, so the notification runs no query.
 */
private function notificationFor(SessionNotice $notice, Episode $episode, Series $series): Notification;
// $group = $series->group;
//
// return match ($notice->kind) {
//     SessionNoticeKind::RecordingReady => new RecordingReadyNotification(/* T-128's arguments */),
//     SessionNoticeKind::CreatorRecordingNeeded => new RecordingNeededNotification(/* T-129's arguments */),
//     SessionNoticeKind::DayBefore => new SessionReminderNotification($episode, $series, $group, CalendarInvite::for($episode, $series)),
//     SessionNoticeKind::SessionCancelled => new SessionCancelledNotification($episode, $series, $group),
// };
```

```php
namespace App\Notifications;

use App\Models\Episode;
use App\Models\Group;
use App\Models\Series;
use App\Models\User;
use App\Support\CalendarInvite;
use App\Support\Terminology;
use App\Support\ZonedTime;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;

/**
 * "Coming up: :title" (D-028): the one fixed reminder Start and above get,
 * qori.live.reminder_minutes_before before the start. Mail only, not
 * queued, no Queueable: the sender is a command that sends inline.
 *
 * Built with what it renders and runs no query: the calendar file arrives
 * as text, so a test can construct this and the sweep builds one file per
 * row. Every noun goes through Terminology::line() with the Group passed
 * explicitly, because a sweep has no current Group.
 */
class SessionReminderNotification extends Notification
{
    public function __construct(
        private Episode $episode,
        private Series $series,
        private Group $group,
        /** CalendarInvite::for($episode, $series) — T-133's RFC 5545 text */
        private string $calendar,
    ) {}

    /** @return array<int, string> */
    public function via(object $notifiable): array;   // ['mail']

    public function toMail(User $notifiable): MailMessage;
    // $terminology = app(Terminology::class);
    // $zone = ZonedTime::zoneFor($notifiable, $this->group);
    // $groupZone = $this->group->timezone();
    // $records = ($this->episode->content['records'] ?? true) !== false;
    // $replace = ['name' => $notifiable->name, 'title' => $this->episode->title, 'series_title' => $this->series->title];
    // $line = fn (string $key, array $extra = []): string => $terminology->line($key, [...$replace, ...$extra], $this->group);
    //
    // subject  live.mail.day_before.subject
    // greeting live.mail.greeting
    // line     live.mail.day_before.intro      ['when' => ZonedTime::describe($this->episode->starts_at, $zone, $groupZone)]
    // line     live.mail.day_before.join       ['minutes' => (int) config('qori.live.join_opens_minutes')]
    // line     $records ? live.mail.day_before.recorded : live.mail.day_before.live_only
    // line     live.mail.day_before.calendar
    // action   live.mail.day_before.action → route('shared.episodes.show', ['seriesId' => $this->series->getKey(), 'episodeId' => $this->episode->getKey()])
    // line     live.mail.outro
    // ->attachData($this->calendar, CalendarInvite::filenameFor($this->episode), ['mime' => CalendarInvite::MIME])
}
```

```php
namespace App\Notifications;

/**
 * "Cancelled: :title" (D-028). Goes only to a Peer who was already reminded
 * of this session, because the reminder is what they would otherwise act
 * on; Undo sends nothing after it. Mail only, not queued. No attachment: a
 * calendar file that a calendar may not apply is not sent.
 */
class SessionCancelledNotification extends Notification
{
    public function __construct(
        private Episode $episode,
        private Series $series,
        private Group $group,
    ) {}

    /** @return array<int, string> */
    public function via(object $notifiable): array;   // ['mail']

    public function toMail(User $notifiable): MailMessage;
    // the same $terminology, $zone, $groupZone, $replace and $line as the reminder
    //
    // subject  live.mail.session_cancelled.subject
    // greeting live.mail.greeting
    // line     live.mail.session_cancelled.intro
    // line     live.mail.session_cancelled.session   ['when' => ZonedTime::describe($this->episode->starts_at, $zone, $groupZone)]
    // line     live.mail.session_cancelled.calendar
    // line     live.mail.session_cancelled.next
    // action   live.mail.session_cancelled.action → route('shared.episodes.show', ['seriesId' => $this->series->getKey(), 'episodeId' => $this->episode->getKey()])
    // line     live.mail.outro
}
```

```php
// App\Services\EpisodeService — T-124's constructor gains one dependency, and
// its update() callback one block after the touchSchedule() call. Nothing else
// in the method changes.

public function __construct(
    private LiveSessionService $liveSessions,
    private SessionNoticeService $notices,
) {}

// Inside T-124's withLockedContent() callback — signature unchanged,
// function (array $content, Episode $locked): array — between its
//     if ($startsAt !== null || $lengthMinutes !== null) {
//         $content = $this->touchSchedule($locked, $content, $startsAt, $lengthMinutes);
//     }
// and its closing `return $content;`:
if ($locked->isDirty(['starts_at', 'ends_at'])) {
    // D-028: the old time's reminders go, sent ones included, so the next
    // run reminds everyone of the new one. Inside the lock, so the delete
    // and the move are one commit. No email goes about the move.
    $this->notices->forgetReminders($locked);
}
```

```php
// App\Services\LiveSessionService — T-134's cancel(), with one line inside its
// lock callback. The service is resolved here, not promoted: T-129 gives
// SessionNoticeService a LiveSessionService, and the reverse would be a
// cycle — the same reason T-134's copy() resolves EpisodeService. restore()
// is T-134's and touches the ledger not at all. The callback keeps T-124's
// signature, function (array $content, Episode $locked): array.

public function cancel(Series $series, string $episodeId): Episode
{
    // ...T-134's guard, lookup and has_recording refusal, unchanged...

    return $this->withLockedContent($episode, function (array $content, Episode $locked): array {
        if ($locked->isCancelled()) {
            return $content;
        }

        $content['cancelled_at'] = CarbonImmutable::now()->toIso8601String();   // T-134's write
        app(SessionNoticeService::class)->queueCancellation($locked);           // this task's line

        return $content;
    });
}
```

```php
// App\Console\Commands\NotifySessionsCommand::handle() — T-129's loop with one
// more line in it. The signature, --dry-run and T-128's countDue()-first shape
// are unchanged, and T-129's early return on a dry run covers this step too.

// $reminders = 0;
// foreach (Group::query()->cursor() as $group) {
//     $current->runFor($group, function () use ($notices, $now, $dryRun, $budget, &$queued, &$reminders, &$due, &$sent): void {
//         $due += $notices->countDue($now);                   // T-128: every run, dry or not, before anything is queued
//         // ...T-129's candidate lines...
//         if ($dryRun) {
//             return;                                          // writes and sends nothing
//         }
//         $queued += $notices->queueCreatorNudges($now);      // T-129
//         $reminders += $notices->queueReminders($now);       // this task: before sendDue(), so a row queued this run goes this run
//         if ($sent < $budget) {
//             $sent += $notices->sendDue($now, $budget - $sent);
//         }
//     });
// }
// Log::info('qori:sessions:notify', ['due' => $due, 'nudges_queued' => $queued, 'reminders_queued' => $reminders, 'sent' => $sent, 'dry_run' => $dryRun]);
// `due` is counted before this run's queueing, as T-128 and T-129 have it, so a
// reminder queued and sent in the same run is absent from it and present in
// `reminders_queued`, which is the key this task's test reads.
// The console line is T-128's, and on --dry-run it adds ' Reminders not queued.' — a diagnostic, not copy.
```

```php
// App\Http\Controllers\Shared\SharedController::liveCard() — one more line in
// T-125's copy array, flat beside 'join', 'joinAgain', 'noLink' and 'records'
// and not inside 'states', because it is not a state line: it can accompany
// the upcoming state or be absent. $now, $group and $terminology are already
// in scope there ($group is nullable, as T-125 has it).
'reminder' => $group?->allows('session_reminders')
    && $episode->starts_at
    && $now < $episode->starts_at->toImmutable()->subMinutes((int) config('qori.live.reminder_minutes_before'))
        ? $terminology->line('live.state.upcoming.reminder', [], $group)
        : null,
```

```php
// App\Http\Controllers\Share\SeriesController::show() — two of the lines
// T-124 and T-134 already build, now picked by plan. $series is the page's
// Series; its Group is the relation BelongsToGroup gives (app/Concerns/BelongsToGroup.php:33).
$notifies = $series->group->allows('session_reminders');

// T-124's edit block:
'noEmail' => $terminology->line($notifies ? 'series.live.edit.reminders_again' : 'series.live.edit.no_email'),
// T-134's livePanel block:
'cancelled' => $terminology->line($notifies ? 'live.panel.cancelled_notified' : 'live.panel.cancelled'),
```

```php
// App\Http\Controllers\Share\LiveSessionController::cancel() — T-134's action;
// the Series is held so the toast can read its plan.
// $series = $this->seriesById($seriesId);
// $episode = $sessions->cancel($series, $episodeId);
// $key = $series->group->allows('session_reminders') ? 'series.session_cancelled_notified' : 'series.session_cancelled';
// Inertia::flash('toast', ['type' => 'success', 'message' => $terminology->line($key, ['title' => $episode->title])]);
// return back();
```

```ts
// resources/js/pages/shared/Show.vue — T-125's interface, one key:
//   interface LiveCard { …; copy: { …; reminder: string | null } }

// resources/js/components/series/LiveSessionCard.vue — one line, in the
// `upcoming` phase only. T-125's card renders the state line from
// `copy.states[phase]` as `{{ line.message }}`; `reminder` is a flat key on
// `copy` beside `join`, `noLink` and `records`, not a state line, so:
//   phase 'upcoming' → after T-133's "Add to calendar" link:
//                      <p v-if="live.copy.reminder">{{ live.copy.reminder }}</p>
// No other phase changes. No inline English anywhere in the file.
```

```php
// App\Console\Commands\MailCheckCommand — the tenth to twelfth messages.
private const EXPECTED = 12;
// scratch(): T-128's $group->update([...]) becomes
//   $group->update(['timezone' => 'Australia/Brisbane', 'plan' => 'start']);
//   inside the same runFor, after T-128's 'Live clinic' and T-129's past Episode:
//   $office = app(EpisodeService::class)->add(
//       $series, 'Office hours', EpisodeType::Live, EpisodeProvider::Link,
//       ['join_url' => 'https://meet.google.com/abc-defg-hij', 'records' => false], false,
//       CarbonImmutable::now()->addHours(2), 60);
//   returned beside the others
// send(), after T-128's paste and T-129's nudge and their sendDue(), inside the same runFor:
//   $notices = app(SessionNoticeService::class);
//   $notices->queueReminders(CarbonImmutable::now());        // 'Live clinic' a day ahead and 'Office hours' two hours ahead are both in the window
//   $notices->sendDue(CarbonImmutable::now());               // 10: "Coming up: Live clinic"  11: "Coming up: Office hours"
//   app(LiveSessionService::class)->cancel($series->fresh(), $office->getKey());   // queues the cancellation for the reminded peer
//   $notices->sendDue(CarbonImmutable::now());               // 12: "Cancelled: Office hours"
```

`lang/en/live.php`'s `mail` block gains `day_before`, `session_cancelled`
and `outro`; its `state.upcoming` block gains `reminder`; its `panel` block
gains `cancelled_notified`. All under `T-125`'s file header; the `mail`
comment `T-128` writes about the zone rule covers the new lines.
`lang/en/series.php` gains `session_cancelled_notified` beside `T-134`'s
`session_cancelled` and `live.edit.reminders_again` beside `T-124`'s
`live.edit.no_email`.

`docs/flows/live-sessions.md` gains "Reminders and cancellations" after
`T-129`'s "Telling the creator":

```
qori:sessions:notify — every run, per Group inside CurrentGroup::runFor()
  ├─ SessionNoticeService::queueReminders($now)
  │    ├─ Group::allows('session_reminders')                    Free: nothing
  │    ├─ live Episodes of unarchived Series, not cancelled,
  │    │    starts_at − reminder_minutes_before ≤ now < starts_at − LATE_REMINDER_CUTOFF_MINUTES
  │    └─ insertOrIgnore day_before per active Access           the unique key is the idempotence
  └─ sendDue($now) → SessionReminderNotification + the .ics (CalendarInvite::for(), filenameFor())
       skips: stale · suppressed · access_inactive · session_cancelled · session_passed · plan_excluded

PATCH /g/{group}/series/{seriesId}/episodes/{episodeId} with a new start or length (T-124)
  └─ EpisodeService::update() → withLockedContent() → touchSchedule() → forgetReminders()
       every day_before row goes; the next run reminds everyone of the new time; no "moved" email

POST /g/{group}/series/{seriesId}/episodes/{episodeId}/cancel (T-134)
  └─ LiveSessionService::cancel() → withLockedContent() → queueCancellation()
       ├─ session_cancelled per sent day_before row
       └─ pending and failed day_before rows deleted
  └─ next run: sendDue() → SessionCancelledNotification; skipped session_restored if undone first

DELETE …/cancel (Undo, T-134): nothing on the ledger. Sent reminders stay and block a repeat;
a reminder that had not gone is queued again by the next run if the window still holds.
```

with the sentence that Free gets none, that the button in both messages is
`shared.episodes.show`, and that the creator's panel, edit form and cancel
toast say who is told by plan; its "Not built yet" loses "a cancellation email
(`T-138`)", which `T-134` writes there beside the cancel chain.
`docs/flows/series.md`: "Editing a live Episode" (`T-124`) gains the
`forgetReminders()` line in its chain, and nothing else — it never carries the
cancellation-email line.
`docs/tinker/live-sessions.md` gains "Remind, then cancel" after `T-129`'s
recipe:

```php
$episode = App\Models\Episode::query()->where('type', 'live')->first();
$series = App\Models\Series::query()->acrossAllGroups()->find($episode->series_id);
$group = $series->group;
$group->update(['plan' => 'start']);                                        // Free gets none

$reminderTime = Carbon\CarbonImmutable::instance($episode->starts_at)
    ->subMinutes((int) config('qori.live.reminder_minutes_before'));
$current = app(App\Support\CurrentGroup::class);
$notices = app(App\Services\SessionNoticeService::class);

$current->runFor($group, fn () => $notices->queueReminders($reminderTime));  // one per Peer with access
App\Models\SessionNotice::query()->forGroup($group)->where('kind', 'day_before')->get(['user_id', 'status']);
```

```bash
php artisan qori:sessions:notify        # sends them; read "Coming up: …" at http://localhost:8025
```

```php
$current->runFor($group, fn () => app(App\Services\LiveSessionService::class)->cancel($series->fresh(), $episode->getKey()));
App\Models\SessionNotice::query()->forGroup($group)->where('kind', 'session_cancelled')->count();   // as many as were reminded
```

```bash
php artisan qori:sessions:notify        # "Cancelled: …"
```

`docs/tinker/mail.md` says twelve where `T-129` made it say nine, and the
sample output gains "Coming up: Live clinic .. ok", "Coming up: Office hours
.. ok" and "Cancelled: Office hours .. ok".
`docs/planning/communications-policy.md:68-85`: each of the four open
questions gains one line, "Answered 18 September 2026 (`D-028`): …", and the
table's Pro cell gains "— one fixed reminder until custom templates
(`D-028`)".

## Copy

`:title` is the Episode's title, `:series_title` the Series', `:name` the
recipient's; `:series`, `:episode` and `:peer_plural` are the Group's nouns
through `Terminology::line()`; `:when` is `ZonedTime::describe()`'s answer,
itself `live.mail.when` or `live.mail.when_both` (`T-128`); `:minutes` is
`qori.live.join_opens_minutes`. No line says "live now", "has ended", "on
its way" or "processing" (`D-026`); no line names a vendor; no article
stands before a noun placeholder; no number is restated. `live.mail.greeting`,
`when` and `when_both` are `T-128`'s and are reused.

| Key                                    | File                 | English                                                                                                                                                             |
| -------------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `live.mail.day_before.subject`         | `lang/en/live.php`   | Coming up: :title                                                                                                                                                   |
| `live.mail.day_before.intro`           | `lang/en/live.php`   | :title is scheduled for :when.                                                                                                                                      |
| `live.mail.day_before.join`            | `lang/en/live.php`   | You can join from your :series page from :minutes minutes before the start.                                                                                         |
| `live.mail.day_before.recorded`        | `lang/en/live.php`   | Can't make it? If the session is recorded, the recording will be added to the same page and you'll get an email.                                                    |
| `live.mail.day_before.live_only`       | `lang/en/live.php`   | This session is live only and won't be recorded.                                                                                                                    |
| `live.mail.day_before.calendar`        | `lang/en/live.php`   | A calendar file is attached, so you can add the session to your calendar.                                                                                           |
| `live.mail.day_before.action`          | `lang/en/live.php`   | Open the :episode                                                                                                                                                   |
| `live.mail.session_cancelled.subject`  | `lang/en/live.php`   | Cancelled: :title                                                                                                                                                   |
| `live.mail.session_cancelled.intro`    | `lang/en/live.php`   | :title has been cancelled.                                                                                                                                          |
| `live.mail.session_cancelled.session`  | `lang/en/live.php`   | It was scheduled for :when.                                                                                                                                         |
| `live.mail.session_cancelled.calendar` | `lang/en/live.php`   | If you added it to your calendar, remove it there.                                                                                                                  |
| `live.mail.session_cancelled.next`     | `lang/en/live.php`   | If another session is added, you'll find it on your :series page.                                                                                                   |
| `live.mail.session_cancelled.action`   | `lang/en/live.php`   | Open your :series page                                                                                                                                              |
| `live.mail.outro`                      | `lang/en/live.php`   | You're getting this because you have access to :series_title.                                                                                                       |
| `live.state.upcoming.reminder`         | `lang/en/live.php`   | You'll get a reminder by email before it starts.                                                                                                                    |
| `live.panel.cancelled_notified`        | `lang/en/live.php`   | Cancelled. Your :peer_plural see that on the :series page, and nobody can join. Anyone already reminded by email gets one saying it's off — tell the rest yourself. |
| `series.session_cancelled_notified`    | `lang/en/series.php` | :title is cancelled. Your :peer_plural see that on the :series page, and anyone already reminded by email gets one saying so.                                       |
| `series.live.edit.reminders_again`     | `lang/en/series.php` | Nobody is emailed about the change — tell your :peer_plural yourself. The usual reminder goes out again for the new time.                                           |

"Is scheduled for" and "was scheduled for" state the schedule, which Qori
observed; "has been cancelled" states the creator's act. "If the session is
recorded" is conditional on purpose: the switch says the creator intends to,
and `T-127` lets them say afterwards that it was not. The card's line
promises a reminder and not its hour, and is shown only until the reminder
is due. "Gets one saying it's off" states what the ledger queues; the send
is the next run's, minutes away, and a suppressed address is the one case
it is not literally true — the same standing as `T-134`'s "see that on the
:series page" for a Peer who never opens it. `T-134`'s `live.panel.cancelled`
and `series.session_cancelled` and `T-124`'s `series.live.edit.no_email` are
unchanged and still read on a Group whose plan sends nothing. The console's
"Reminders not queued." and the heartbeat are diagnostics for a developer
and are not copy.

## Routes

None. Both notices leave by mail with `shared.episodes.show` (`T-125`) as
their button, and `qori:sessions:notify` is `T-128`'s console command.

## Tests

**New: `tests/Feature/Mail/SessionReminderTest.php` — 16 cases**
(`RefreshDatabase`; `Notification::fake()`; a `scene(string $plan = 'start')`
helper as `T-128`'s and the Preconditions above: the clock at
`2026-10-01 00:00:00` UTC, a Group in `Australia/Brisbane` on that plan with
an owner, a Series, the live Episode "Live clinic" through
`EpisodeService::add()` starting `2026-11-01 09:00` Brisbane —
`2026-10-31T23:00:00Z` — for 60 minutes with
`['join_url' => 'https://zoom.us/j/91827405566', 'records' => true]`; a
`grant(User $peer)` helper calling `AccessService::grant()` inside
`CurrentGroup::runFor()`; `queue(CarbonImmutable $now)` and
`send(CarbonImmutable $now)` calling `queueReminders()` and `sendDue()` in
the same context; `reminderTime()` = `starts_at` minus
`config('qori.live.reminder_minutes_before')`; the clock moved with
`CarbonImmutable::setTestNow()`)

1. `test_it_queues_one_day_before_row_per_peer_when_the_reminder_time_arrives`
   — two Peers; `queue(reminderTime − 1 min)` returns 0 and no row exists;
   `queue(reminderTime)` returns 2; each row `kind` `day_before`, `status`
   pending, `publication` 1, `attempts` 0, `recording_id` null, `group_id`
   the Group's.
2. `test_it_queues_nothing_new_on_a_second_run` — after case 1's rows,
   `queue(reminderTime + 5 min)` returns 0 and still two rows.
3. `test_it_reminds_a_peer_granted_after_the_first_run_on_the_next_while_the_start_is_far_enough_away`
   — queue at `reminderTime`; grant a third Peer at `starts_at − 5 h`;
   queue → 1 new row for the third; the first two untouched.
4. `test_it_gives_no_reminder_to_a_peer_granted_inside_the_cutoff` — a Peer
   granted at `starts_at − 30 min`; queue → 0.
5. `test_it_queues_no_reminder_on_a_free_group_and_one_on_every_paid_plan`
   — `scene('free')`: queue at `reminderTime` → 0 and
   `config('qori.plans.free.session_reminders')` is false; for `start`,
   `pro`, `school`: the config key is true and a scene on that plan queues
   one row.
6. `test_it_queues_no_reminder_for_a_cancelled_session_or_an_archived_series`
   — `content['cancelled_at']` set (written directly, as `T-128`'s case 5
   does) → queue 0; a fresh scene with `status` `SeriesStatus::Archived` →
   queue 0.
7. `test_it_mails_the_reminder_with_both_zones_the_button_and_the_calendar_file`
   — the Peer's `timezone` `America/New_York`; `send()` returns 1; the row
   is sent with `sent_at` and `attempts` 1;
   `Notification::assertSentTo($peer, SessionReminderNotification::class, fn ($n) => …)`
   reads `toMail($peer)`: the joined `introLines` contain
   "Sat 31 Oct 2026, 7:00 pm EDT (America/New_York)" and
   "Sun 1 Nov 2026, 9:00 am AEST (Australia/Brisbane)" (owner acceptance 2,
   across the 1 November boundary, on the mail); `actionUrl` is
   `route('shared.episodes.show', ['seriesId' => …, 'episodeId' => …])`;
   `rawAttachments[0]['name']` is `CalendarInvite::filenameFor($episode)`
   (`live-clinic.ics`), its `options['mime']` `CalendarInvite::MIME`, and its
   `data` contains `UID:{episodeId}@useqori.com`, the `DTSTART` line for
   31 October 2026 23:00 UTC and `SEQUENCE:1`.
8. `test_it_uses_the_groups_zone_alone_when_the_peer_has_not_chosen_one` —
   `users.timezone` null; the intro names Brisbane once and no second zone.
9. `test_it_says_the_recording_will_follow_only_when_the_session_is_recorded`
   — `records` true: the `day_before.recorded` line present, `live_only`
   absent; `records` false (`EpisodeService::update()` with `records` 0):
   the reverse.
10. `test_it_speaks_the_groups_vocabulary` — a `pro` Group with
    `settings[Terminology::SETTINGS_KEY]` as
    `tests/Feature/TerminologyTest.php:85-97` (labels at `:41-43`); the
    action reads "Open the Practice" and the join line names the Trail;
    default nouns on `start`.
11. `test_it_never_carries_the_join_link` — the join URL appears in neither
    the subject, the greeting, any line, `actionUrl` nor the attachment's
    data.
12. `test_it_deletes_the_reminders_when_the_time_moves_so_they_go_again_for_the_new_time`
    — queue and send at `reminderTime` (a sent row);
    `EpisodeService::update()` with `starts_at` two days later inside
    `runFor()`; no `day_before` row remains; queue at the new
    `reminderTime` → a fresh pending row; send → the Peer has received two
    `SessionReminderNotification`s, the second naming the new time (owner
    acceptance 14).
13. `test_it_resets_the_reminders_for_a_length_change_and_not_for_a_link_change`
    — `length_minutes` 90 → the rows are gone; queue again; `join_url`
    changed → the rows stay; the same start and length resubmitted → the
    rows stay.
14. `test_it_skips_a_reminder_for_a_session_already_started` — queue at
    `reminderTime`; send at `starts_at + 1 min` → `status` skipped, `error`
    `session_passed`; `assertNothingSent()`.
15. `test_it_skips_a_reminder_when_the_group_drops_to_free_before_the_run`
    — queue; `plan` set to `free`; send → skipped, `plan_excluded`; nothing
    sent.
16. `test_it_skips_a_reminder_for_a_revoked_access_and_a_suppressed_address`
    — two Peers queued; `AccessService::revoke()` on one and
    `SuppressionService::hardBounce()` on the other's address; send →
    `access_inactive` and `suppressed` in `error`, nothing sent — `T-128`'s
    checks, proven to cover this kind.

**New: `tests/Feature/Mail/SessionCancelledTest.php` — 9 cases** (the same
helpers; `remind()` = queue and send at `reminderTime`; `cancel()` and
`restore()` call `LiveSessionService::cancel($series, $episodeId)` and
`restore($series, $episodeId)` inside `runFor()`)

1. `test_it_queues_a_cancellation_for_every_peer_who_was_reminded_and_nobody_else`
   — two Peers reminded (sent rows), a third granted after that run with no
   row; `cancel()`; two `session_cancelled` rows, pending, `publication` 1,
   `recording_id` null, `user_id` the two reminded Peers; none for the
   third.
2. `test_it_drops_a_reminder_still_pending_at_cancel_and_tells_that_peer_nothing`
   — a Peer whose `day_before` row was queued and not sent; cancel → no
   `session_cancelled` row for them and their `day_before` row is gone; the
   sent rows of the others stay.
3. `test_it_queues_nothing_more_when_cancel_runs_twice` — a second
   `cancel()` (a no-op on the key, `T-134`) → still two rows;
   `queueCancellation()` called directly a second time returns 0.
4. `test_it_mails_the_cancellation_with_the_scheduled_time_in_both_zones_and_no_join_link_or_attachment`
   — the Peer in `America/New_York`; send → sent although
   `content['cancelled_at']` is set; the subject starts "Cancelled:"; the
   session line carries both zone strings of the reminder test's case 7;
   `actionUrl` is `route('shared.episodes.show', …)`; `rawAttachments` is
   empty; the join URL appears nowhere.
5. `test_it_skips_the_cancellation_when_undo_comes_before_the_run` — cancel,
   restore, send → skipped, `session_restored`;
   `assertNotSentTo($peer, SessionCancelledNotification::class)`.
6. `test_it_does_not_remind_an_already_reminded_peer_again_after_undo` —
   reminded, cancel, restore; queue at `reminderTime + 10 min` → 0 new
   rows; send → nothing more sent.
7. `test_it_queues_a_dropped_reminder_again_after_undo` — a pending row
   deleted at cancel; restore; queue → a fresh pending row; send → the
   reminder goes.
8. `test_it_never_reminds_a_cancelled_session` — cancel, no undo; queue at
   `reminderTime` → 0 rows; nothing sent.
9. `test_it_speaks_the_groups_vocabulary_in_the_cancellation` — a `pro`
   Group with custom labels; the `next` line names the Trail and the action
   reads "Open your Trail page"; default nouns on `start`.

**Changed:**

- `tests/Feature/Console/NotifySessionsCommandTest.php` (`T-128`) — 2 new
  cases: `test_it_queues_due_reminders_before_sending_and_counts_them_in_the_heartbeat`
  (a `start` Group with one Peer and a session a day ahead;
  `artisan('qori:sessions:notify')` exits 0; the `day_before` row exists
  and is sent in that same run; `Log::spy()` sees `info` with
  `reminders_queued` 1) and `test_it_queues_no_reminders_on_a_dry_run`
  (`--dry-run` on the same scene: no row, nothing sent).
- `tests/Feature/Shared/LiveSessionCardTest.php` (`T-125`) — 1 new case,
  `test_it_promises_a_reminder_only_on_a_plan_that_sends_one_and_only_before_the_reminder_time`:
  the Inertia prop `live.copy.reminder` is the line on a `start` Group two
  days ahead, `null` on a `free` Group, `null` on a `start` Group twelve
  hours ahead.
- `tests/Feature/Series/CancelLiveEpisodeTest.php` (`T-134`) — its scene is
  a `start` Group, so cases 1 and 2 now read the toast as
  `series.session_cancelled_notified` and `livePanel.cancelled` as
  `live.panel.cancelled_notified`; 1 new case,
  `test_it_says_who_is_told_by_plan`: on `free` the toast is
  `series.session_cancelled` and the panel line `live.panel.cancelled`; on
  `start` the two `_notified` lines. Its case 8 (`assertNothingSent()` and
  no `session_notices` row after cancel and undo) still holds: nobody was
  reminded, so `queueCancellation()` inserts nothing.
- `tests/Feature/Series/EditLiveEpisodeTest.php` (`T-124`) — 1 new case,
  `test_it_says_the_reminder_goes_again_on_a_plan_that_sends_one`: the
  creator's page prop `edit.noEmail` is `series.live.edit.reminders_again`
  on `start` and `series.live.edit.no_email` on `free`. Its
  `test_it_sends_no_email_when_a_session_moves` still passes:
  `forgetReminders()` sends nothing.
- `tests/Feature/Mail/MailContentTest.php` — the senders map at `:162-168`
  gains `'SessionReminderNotification' => 'SessionNoticeService'` and
  `'SessionCancelledNotification' => 'SessionNoticeService'`; no new
  method. Without it `test_every_notification_class_is_covered_by_the_command`
  fails on both classes.

Total: 30 new cases.

## Acceptance

- [ ] On a Start Group, every Peer with access to a live Episode receives one
      reminder `qori.live.reminder_minutes_before` before the start, with
      the session in their own zone and the Group's zone beside it when they
      differ, the calendar file attached under its download name, and a
      button that lands on the Episode's card; a Peer granted later is
      reminded on the next run while the start is more than an hour away
      (owner acceptance 2)
- [ ] On a Free Group nobody is reminded, the card promises no reminder, and
      the creator's panel, edit form and cancel toast keep `T-124`'s and
      `T-134`'s wording; on a plan that reminds they say who is told
- [ ] Moving a session's time or length deletes its reminders and they go
      again for the new time; a link or switch change leaves them; no
      "moved" email goes (owner acceptance 14)
- [ ] Cancelling a session tells every Peer who was reminded of it, once, and
      nobody who was not; Undo sends nothing and reminds nobody twice; no
      message carries the join link or a vendor destination
- [ ] A reminder for a session whose start has passed, for a Group that
      dropped to Free, for a suppressed address or for a revoked Access is
      skipped with its reason in the ledger, never sent
- [ ] `qori:sessions:notify` queues reminders before it sends, in the same
      run, and its heartbeat counts them; `--dry-run` queues nothing and
      sends nothing
- [ ] A Group with its own vocabulary gets its own words in both messages,
      with the Group passed to `Terminology::line()` explicitly
- [ ] `php artisan qori:mail:check` sends and reads twelve messages, and the
      attached `.ics` imports into a calendar at the right hour
- [ ] `docs/flows/live-sessions.md` describes the queue, both chains and the
      skips, and no longer lists a cancellation email as unbuilt;
      `docs/flows/series.md`'s "Editing a live Episode" names
      `forgetReminders()`; the recipes in `docs/tinker/live-sessions.md` and
      `docs/tinker/mail.md` run as written; `communications-policy.md`'s
      open questions carry their answers
- [ ] No `acrossAllGroups()` caller is added in app code (the tinker recipe
      resolves one Series by key, as `T-128`'s does), no `ShouldQueue`, no new
      inline English in Vue, and `LiveSessionService` gains no constructor
      dependency
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- The config key's shape: `qori.plans.<plan>.session_reminders`, a boolean
  read through `Group::allows()`, Free `false` and Start, Pro and School
  `true`, from `communications-policy.md:55-64` — confirm — anyone's.
- Who is told of a cancellation: this draft reads `D-028`'s "those who
  already hold a `day_before` row" as a `sent` row, and drops a pending or
  failed one so Undo can queue it afresh — confirm — the stream owner's.
- `T-128` `ready`, so the ledger, `sendDue()`'s checks, `ZonedTime` and the
  row shape are frozen; `T-133` `ready`, so `CalendarInvite::for()`,
  `filenameFor()`, its `URL` and `SEQUENCE` are; `T-134` `ready`, so
  `cancel(Series, string)`, `restore()` and `cancelled_at` are — anyone's;
  keep draft until all three are.
- The schedule interval is the owner's (`D-028`) and is inherited from
  `T-128`; nothing here adds a scheduled line.

## Re-scope log

None.

## Notes

Specified on 18 September 2026 from `D-028`, with `D-026` for the copy rule
and `D-024` for the button. The owner's acceptance scenarios it answers are
2 and 14 (`docs/planning/course-classroom.md`). `T-129` lands before this
task through `T-134`, so its nudge step, its `notificationFor()` arm and its
`qori:mail:check` count are assumed present.

**`T-128`'s draft is edited to:** apply its `session_cancelled` check to every
kind but `SessionCancelled`. That is the only edit owed: `notificationFor()`'s
return type already widens to `Illuminate\Notifications\Notification` in
`T-129`, which lands first. Its `live.mail.recording_ready.outro` and this
task's `live.mail.outro` carry one sentence; folding one into the other is a
wording-tier change either owner may make and neither task requires.

**`T-134`'s draft is edited to:** resolve `SessionNoticeService` with
`app()` inside `cancel()`'s lock callback and call `queueCancellation($locked)`
there, as its `copy()` resolves `EpisodeService`; leave the ledger alone in
`restore()`; and expect its cases 1 and 2 to read the plan-picked keys on
its `start` scene once this task lands. Its "cancelled sends no nudge" case
is unaffected: `T-129`'s candidates skip a cancelled Episode by
`cancelled_at`. Separately, and not this task's to fix: its `cancel()` and
`restore()` render the lock callback as `function (Episode $locked): void`
and assign `$locked->content` inside it, where `T-124` — `ready`, and the
task that declares `withLockedContent()` — passes
`function (array $content, Episode $locked): array` and assigns what comes
back. This task's block uses `T-124`'s signature, which is the frozen one.

**`T-133`:** its "if it chooses" is answered — the cancellation attaches
nothing, for the reason in the decision above; the reminder attaches
`for()` under `filenameFor()` and adds no calendar code of its own.

**`T-124` (ready)** already says this task lists
`app/Services/EpisodeService.php` for the reminder rows; the block goes
inside its lock callback and nothing else in `update()` changes. Its
`series.live.edit.no_email` line stays for Free, where it is still the whole
truth.

**Claim order (`streams/classroom.md`):** already carries this task last on
`SharedController`, `shared/Show.vue`, `LiveSessionCard.vue`,
`SeriesController`, `EpisodeService`, `LiveSessionService`,
`SessionNoticeService`, `config/qori.php`, `lang/en/live.php`,
`lang/en/series.php`, `docs/flows/series.md`, `docs/flows/live-sessions.md`
and `docs/tinker/live-sessions.md`, so nothing here needs the stream owner.
`LiveSessionController` is not listed there because fewer than four tasks
touch it and the dependencies already order them (`T-127`, `T-134`, here).
The type-only page row exists because `T-125` declares `LiveCard` on the
page; if that interface moves into the card, the row goes.

`communications-policy.md:129-140` ("the creator picks one, for the
workspace") governs the send time of a creator-set reminder, which does not
exist yet: the fixed reminder is an instant, `starts_at − reminder_minutes_before`,
and needs no zone; how a time is rendered follows `D-028`. Its question 3's
answer is the per-run cap and the unique ledger, as `D-028` records.

`D-028` leaves open whether Free should get `day_before`. If the owner
amends the policy, it is one boolean here and nothing else.

A second reminder kind (an hour before, say) would be one more
`SessionNoticeKind` case, one more queue method with its own window, and one
more notification, on the same ledger; `D-028` builds none.

`T-129`'s "Recording email: sent to :sent, :failed failed" reads
`recording_ready` rows through `talliesFor()`; the reminder rows sit in the
same table with the same statuses, so a "Reminder: sent to …" line is a
wording-sized follow-up when somebody asks for it.

`T-135`'s copied message is the only nudge before a session on Free, which
is why the card's reminder line is absent there rather than saying "no
reminder".
