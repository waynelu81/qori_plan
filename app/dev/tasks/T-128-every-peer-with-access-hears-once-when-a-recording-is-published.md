---
id: T-128
title: Every Peer with access hears once when a recording is published
stream: classroom
status: doing
owner: claude
estimate: M
depends: T-127, T-130
blocks: T-129, T-136, T-138, T-140, T-145
---

# T-128 — Every Peer with access hears once when a recording is published

> **Draft.** Written on 17 September 2026 from `D-028` and the classroom
> brief; not to be started — see [`../PROCESS.md`](../PROCESS.md). What has
> to be decided before it can be marked `ready` is listed at the bottom.

## Why

Nothing tells a Peer that a recording exists. `T-126` puts the pasted link
on the Episode's card, so a Peer who reopens the Series page finds it — and
the Peer this stream exists for is the one fifteen hours away who missed the
class and has no reason to reopen anything. The only session-shaped mail
Qori sends is `SeriesAccessNotification`
(`app/Notifications/SeriesAccessNotification.php:46-63`), once, at the
grant; it reads its lines with `__()`, checks no suppression and is not
queued, because the queue is `deferred` and cannot retry (`:18-23`). The
only bulk sender is `CampaignService::send()`, which is consent-gated and
metered (`app/Services/CampaignService.php:97-100`) — the wrong gate for a
message that fulfils something the Peer already has. Nothing in the
codebase records a send that failed: `RecipientStatus::Failed`
(`app/Enums/RecipientStatus.php:19`) has no producer, as
`docs/tinker/mail.md` says under "What this does not tell you". And
`routes/console.php:15-27` still says the cron entry does not exist, which
has been false since the Laravel Cloud scheduler was enabled on 11 September
2026 (`docs/planning/release-prerequisites.md:24`).

The owner's proposal is explicit about the shape: send when the replay is
published, not when the meeting ends; dedupe by learner, lesson and
publication version; show creators send status; distinguish provider
acceptance from delivery; and make reliability part of the feature. `D-028`
turns that into a ledger, `session_notices`, that is the outbox: a row per
recipient per Episode per kind per publication, unique, so no sweep can send
twice; a status from `RecipientStatus`; a retry count and a next-attempt
time, so a failed send is tried again with backoff and then left where
`T-019` can see it. Recipients are worked out from active Accesses and
filtered by `SuppressionService::blockedForTransactional()`
(`app/Services/SuppressionService.php:109-112`) and nothing else.

Afterwards, `RecordingService::paste()` queues one pending row for every
Peer whose Access was granted by the time the Episode's first recording was
published, and `qori:sessions:notify` — every five minutes, provisional —
sends them inline, at most `qori.live.sends_per_run` a run, retries a failed
row at 15, 60 and 240 minutes and then leaves it `failed`. The email names
the session in the recipient's own zone with the Group's zone beside it when
they differ, and its button lands on `shared.episodes.show` (`D-024`), never
on the recording URL or a passcode. That zone rule is stated here once, in
`App\Support\ZonedTime`, and every later notice (`T-129`, `T-136`, `T-138`) cites it.

## Decisions taken to make this specifiable

**The row is inserted when the recording is published, not by the sweep.**
`RecordingService::paste()` (`T-126`) calls
`SessionNoticeService::queueRecordingReady($recording)` after the row is
written; `T-144`'s `publish()` and `T-140`'s re-send call the same method.
The sweep only sends. Publication is the one moment the recipient set is
known (`D-028`: Accesses granted before `published_at`), and it is a creator's
request, which already has a current Group, so the group-scoped `Access`
query needs no `runFor()` there. `queueRecordingReady()` reads the
publication number from `content['recording_publication'] ?? 1`, so `T-140`
bumps that key and calls the same method.

**Recipients are Accesses active at queue time whose `granted_at` is not
after the Episode's earliest published, unhidden recording.** The cut-off is
the earliest recording's `published_at`, not the pasted one's, so a second
part queues nothing for anyone — `D-028`: "a later part or a replaced link
sends nothing". The comparison is `<=`, not `<`: Eloquent writes timestamps
to the second (`vendor/laravel/framework/src/Illuminate/Database/Grammar.php:282-285`),
so a grant and a paste inside one second — every test, and `qori:mail:check`
— would otherwise compare equal and mail nobody. A Peer granted in the same
second as the paste is told; one granted a second later sees it on the page.
That reads `D-028`'s "granted before that recording's `published_at`" as
"not after, to the second" — a departure from the decision's word, made
here on purpose and recorded under Notes for `decisions.md` to carry —
and `recipientsFor()` is the one place the rule is coded: `T-140`'s re-send
and `T-144`'s publish call `queueRecordingReady()` and never restate it
with `<`. Rows need `user_id`; an Access with none (`accesses.user_id` is nullable in
the schema) is not a recipient.

**Insertion is one `insertOrIgnore()` with explicit ULIDs, `group_id` and
timestamps.** One statement for the whole class, idempotent under the unique
key, so a double-submitted paste or two overlapping publishes cannot raise a
constraint violation into a 500 and cannot double a row. It bypasses
`BelongsToGroup`'s creating hook (`app/Concerns/BelongsToGroup.php:25-29`)
and the model's casts, so `group_id` comes from the Access, `kind` and
`status` are written as their enum values, and `created_at`/`updated_at` are
set by hand. The return value is the number inserted.

**The window is applied twice, for two different failures.**
`queueRecordingReady()` queues nothing for a recording whose `published_at`
is older than `qori.live.notice_window_days` (`D-028`); on paste that is never
true, because paste sets `published_at` to now, but it is the rule the brief
names and `T-144`'s publish keeps it. `sendDue()` separately marks a row
`skipped` with `stale` when the row's own `created_at` is older than the same
window — the case is a scheduler that was off for a fortnight
(`release-prerequisites.md:24` says the toggle does nothing until the next
deploy), after which the first run would otherwise mail every class about a
recording three weeks old. `T-140`'s deliberate re-send of an old recording
meets the queue-time window; its draft decides how it passes it (see Notes).

**Everything is re-checked at send time, and a row that fails a check is
`skipped` with a reason in `error`.** `D-028`: recipients are worked out at
send time. Before each send: the row is not stale; the address is not
suppressed for transactional mail; the Peer still holds an active Access to
the Episode's Series; the session is not cancelled (`content['cancelled_at']`,
`D-026`'s key, written by `T-134` later and checked now); and, for
`recording_ready`, the Episode still has a published, unhidden recording.
Reasons are string constants on the service, diagnostics for the ledger and
`T-129`'s card, never copy — the same shape as `CampaignService::record()`
writing `'suppressed'` (`app/Services/CampaignService.php:108-116`).

**One command iterates the Groups and passes the remaining budget; the
service sends inside the current Group.** `NotifySessionsCommand` walks
`Group::query()->cursor()` inside `CurrentGroup::runFor()`
(`app/Support/CurrentGroup.php:88-101`) and calls
`sendDue($now, $budget - $sent)` per Group, stopping when the run's budget is
spent, so `qori.live.sends_per_run` is one counter for the run and not one
per Group. `sendDue(CarbonImmutable $now, ?int $limit = null)` is the brief's
signature with the cap optional: null means the config value. The service
reads the Group from `CurrentGroup` and adds no `acrossAllGroups()` caller,
so the allow-list in `tests/Feature/Admin/ConsoleAccessTest.php:130-150` is
unchanged — `Group` carries no group scope, and `PurgeSeriesCommand`'s
crossing (`app/Console/Commands/PurgeSeriesCommand.php:34`) is not copied.

**A run claims its batch in one short `DB::transaction()` with
`lockForUpdate()`, commits, and only then sends; each row's outcome is one
statement of its own, outside any transaction.** The claim reads this
Group's due rows oldest first, at most the limit, locks them, and on each
adds one to `attempts` and sets `next_attempt_at` to now plus the backoff
for that try (`BACKOFF_MINUTES[min(attempts, 3) - 1]`), leaving `status` as
it was; the `due` scope does not match a claimed row until that time. So a
second run that starts anyway waits for the claim's commit and finds
nothing due, and a run that dies between the commit and a row's outcome —
the process killed, the connection dropped — leaves that row to be retried
at the backoff, never re-sent at once. Sending inside the claiming
transaction was the other shape, and it is the wrong one: a rollback after
one or more messages had been handed to the mailer — a database error, a
lost connection, Neon closing a transaction that ran for two hundred SMTP
calls — would return every row to `pending`, and the next run would send
them all again, which is the duplicate the ledger exists to prevent
(`D-028`); and the lock would be held for the length of up to
`sends_per_run` network calls. What remains is one message sent twice if
the process dies after the mailer accepted it and before the `sent`
statement ran: a window of one statement per row, the bounded form of the
failure, accepted. The schedule adds `withoutOverlapping()->onOneServer()`
beside the claim, one reason each: the mutexes stop a second run starting,
and the row lock with `next_attempt_at` covers the run that starts anyway.
`onOneServer()` needs a cache shared across servers, which Valkey is in
production and `file` is on one machine locally.

**A failed send is caught, reported, and left to `BACKOFF_MINUTES`; the
first try plus `qori.live.notice_attempts` retries, then the row is left.**
`sendDue()` catches `Throwable` around `notify()`, calls `report()`, sets
`status` to `failed` and writes the exception's message to `error`. The try
was counted and its retry time set by the claim, so `failed()` keeps that
`next_attempt_at` — 15, 60 and then 240 minutes after the first, second and
third failed try — unless `attempts` now exceeds `notice_attempts` (3),
when it sets `next_attempt_at` to null and the `due` scope never matches
the row again; it stays `failed` for `T-019` to alert on and `T-129`'s card
to count. `attempts` counts every claimed try, a successful one included,
so the ledger says how many tries a message took. This is the first
producer of `RecipientStatus::Failed`. The constant's name follows `T-091`'s
`BACKOFF_MINUTES` on `vendor_grants`, which `D-028` names as the precedent.

**Suppression is the only gate.** No consent check, no daily or monthly
metering, no unsubscribe footer, and a paused Group still sends: the message
fulfils something the Peer already has, and `CampaignService`'s "a
hibernated group sends no EDM" (`app/Services/CampaignService.php:77-81`)
is about marketing (`D-028`). `blockedForTransactional()` is called once per
batch with every address in it, as `send()` does for marketing
(`:90-95`), never once per recipient.

**The email's button is `shared.episodes.show`, and the body carries no
recording link and no passcode.** `D-024` mints every email against that
route; the owner's proposal: the button points to the lesson, "not an
expiring media URL or a passcode pasted into an email". The passcode is on
the card for every Peer with access (`D-027`), where Watch is.

**Every date in a notice follows the recipient's `users.timezone`, else the
Group's, with the zone named and the Group's zone beside it when they
differ.** That is `D-028`'s answer to `T-025`'s question, stated here as
`App\Support\ZonedTime`, Qori's own helper with nothing vendor-specific in
it. `zoneFor()` reads the recipient's raw attribute with
`getAttributeValue()` — `User::timezone()` (`app/Models/User.php:84-89`)
falls back to UTC, which is not the rule, and the accessor-versus-method
trap its docblock names (`:79-82`) is avoided the same way — and falls back
to `Group::timezone()` (`app/Models/Group.php:221-231`), which itself falls
back to the owner's zone before UTC. `describe()` formats with
`'D j M Y, g:i a T'` — the creator's flash uses `'j M Y, g:ia T'`
(`app/Http/Controllers/Share/EpisodeController.php:63-67`); the weekday is
added because a class is a weekday appointment — and the lang line adds the
identifier, because `T` alone gives "CST" for Taipei and for Chicago. The
Group's zone is shown beside when the two identifiers differ; two aliases of
one zone shown twice is harmless.

**The notification is built with what it renders and runs no query.**
`RecordingReadyNotification` takes the Episode, the Series, the Group, a
`bool` for after-session materials and a nullable homework due time; the
service works those out (from `materials`, `T-130`) and the notification
formats. Nouns go through `app(Terminology::class)->line($key, $replace, $group)`
(`app/Support/Terminology.php:84-91`) with the Group passed explicitly,
because a sweep has no current Group (`D-028`), and titles are `:title` and
`:series_title`, never a noun placeholder. No `Queueable`, no `ShouldQueue`
(`tests/Feature/ArchitectureTest.php:123-130`).

**`qori:mail:check` sends the eighth message, through the service.**
`tests/Feature/Mail/MailContentTest.php:120-148` fails for any notification
the command never sends, and its senders map (`:162-168`) accepts a service
the command calls. So `MailCheckCommand` gives its scratch Group a zone and
its Series a live Episode, pastes a recording after the grant, runs
`sendDue()`, and expects eight (`EXPECTED`,
`app/Console/Commands/MailCheckCommand.php:47`); the map gains
`'RecordingReadyNotification' => 'SessionNoticeService'`. Excluding it with
a reason was the other choice, and it would have meant nobody reads it.

**Five minutes is provisional, and the stale comment goes.** `D-028` leaves
the interval to the owner, chosen with `T-091`'s against Laravel Cloud's
sleep timeout (`release-prerequisites.md:27`); the line is written with a
comment saying so. The block above `qori:series:purge` in
`routes/console.php:15-27` is replaced by one that says the scheduler has run
since 11 September 2026 and that a change to a frequency takes effect on the
next deploy. Each run logs one `Log::info` heartbeat with the counts, which
is what `T-019` will watch for a run that stopped.

**`--dry-run` counts and sends nothing.** `countDue($now)` per Group, the
total printed, no row touched. The same shape as `qori:series:purge`'s
option. `countDue()` runs for every Group on every run, dry or not — one
query per Group every five minutes, with nothing due most of the time.
Accepted at pilot scale, so the heartbeat's `due` is the same figure on a
dry and a real run; if the Group count ever makes it matter, moving the
count to `--dry-run` alone is `T-019`'s call, since the heartbeat is its.

**No page, no factory.** Send status on the creator's card is `T-129`'s.
There is no `EpisodeFactory` and a `SessionNoticeFactory` could not build its
own Episode; tests make rows through `queueRecordingReady()` and date one
back with `forceFill()` for the stale case, and `T-129`'s card tests do the
same.

## Preconditions

**Data this task verifies against:** a clean database. The feature tests
build a Group with a timezone and an owner the way
`tests/Feature/Series/LiveSessionTest.php:40-58` does, a Series through its
factory, a live Episode through `EpisodeService::add()` with `T-123`'s
`$startsAt` and `$lengthMinutes`, Accesses through `AccessService::grant()`
or `Access::factory()->forSeries($series)->forUser($peer)`
(`database/factories/AccessFactory.php:45-51` and `:53-56`), and a recording through
`RecordingService::paste()` (`T-126`). The clock is moved with
`CarbonImmutable::setTestNow()`, which the framework resets between tests.

**Equipment:** Mailpit on 1025/8025 for `qori:mail:check` and the tinker
recipe; nothing for the suite, which runs on the `array` mailer.

**Spike:** none owed. No vendor payload is read; the mailer is Laravel's.

## Scope

**In:**

- `session_notices`, `SessionNotice`, `SessionNoticeKind` with all four
  cases declared, though only `recording_ready` is produced here.
- `SessionNoticeService::queueRecordingReady()`, `sendDue()`, `countDue()`,
  the skip reasons, the backoff.
- `RecordingService::paste()` calling `queueRecordingReady()`.
- `RecordingReadyNotification` and its lines in `lang/en/live.php`.
- `ZonedTime` and the mail zone rule.
- `qori:sessions:notify` with `--dry-run`, the schedule line, the heartbeat,
  the corrected comment in `routes/console.php`.
- `qori:mail:check` sending and reading the eighth message.
- `docs/flows/live-sessions.md`, `docs/tinker/live-sessions.md`,
  `docs/tinker/mail.md`.

**Out:**

- `creator_recording_needed` and the "Recording email: sent to :sent,
  :failed failed" line on the creator's card (`T-129`).
- `day_before` and `session_cancelled`, the `.ics` attachment, the deletion
  of reminder rows on a time change (`T-138`).
- The deliberate re-send that bumps `publication` (`T-140`).
- `publish()` and `reject()` of a found recording (`T-144`); this task's
  `queueRecordingReady()` is what `publish()` will call.
- Any change to `config/qori.php`: every `qori.live.*` key this task reads is
  declared by `T-123`.
- A per-Peer "no reminders" preference, a consent gate, campaign metering,
  an unsubscribe footer, quiet hours, digests — `D-028` says none exists.
- Confirmed delivery, bounces and complaints against these rows (`T-032`,
  `T-017`); the ledger records acceptance by the mailer, and `sent` means
  handed over, not arrived.
- Alerting on rows left `failed` (`T-019`); this task leaves them where an
  alert can find them.
- A worker; sends are inline from the command, as `PurgeSeriesCommand`'s
  docblock (`app/Console/Commands/PurgeSeriesCommand.php:10-15`) explains.
- `SeriesAccessNotification` (`T-005`, `T-136`) and `T-025`'s pages.

## Files

| Path                                                               | Change | Notes                                                                                                                                                 |
| ------------------------------------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `database/migrations/2026_09_18_000300_create_session_notices.php` | new    | The ledger, `D-028`                                                                                                                                   |
| `app/Enums/SessionNoticeKind.php`                                  | new    | Four cases                                                                                                                                            |
| `app/Models/SessionNotice.php`                                     | new    | `HasUlids`, `BelongsToGroup`, `scopeDue()`, `isExhausted()`                                                                                           |
| `app/Services/SessionNoticeService.php`                            | new    | `queueRecordingReady()`, `sendDue()`, `countDue()`, `claim()`, `BACKOFF_MINUTES`, skip reasons                                                        |
| `app/Services/RecordingService.php`                                | edit   | `paste()` calls `queueRecordingReady()`; `SessionNoticeService` promoted in the constructor                                                           |
| `app/Notifications/RecordingReadyNotification.php`                 | new    | Mail only, not queued; `Terminology::line()` with the Group                                                                                           |
| `app/Support/ZonedTime.php`                                        | new    | `zoneFor()`, `describe()`, `FORMAT` — the mail zone rule                                                                                              |
| `app/Console/Commands/NotifySessionsCommand.php`                   | new    | `qori:sessions:notify {--dry-run}`; the Group loop; the heartbeat                                                                                     |
| `routes/console.php`                                               | edit   | The schedule line; the stale comment replaced                                                                                                         |
| `lang/en/live.php`                                                 | edit   | `mail.*` — `T-125` creates the file                                                                                                                   |
| `app/Console/Commands/MailCheckCommand.php`                        | edit   | `EXPECTED` 8; a zoned Group, a live Episode, a paste, `sendDue()`; the class and `inspect()` docblocks say eight where they say seven (`:35`, `:118`) |
| `docs/flows/live-sessions.md`                                      | edit   | "When a recording is published": queue, sweep, skips, retry — `T-125` creates the file                                                                |
| `docs/flows/README.md`                                             | edit   | The `live-sessions.md` row names the notices                                                                                                          |
| `docs/tinker/live-sessions.md`                                     | edit   | Paste, `--dry-run`, send, read in Mailpit — `T-125` creates the file                                                                                  |
| `docs/tinker/mail.md`                                              | edit   | Eight messages, the sample output                                                                                                                     |
| `tests/Feature/Mail/RecordingReadyTest.php`                        | new    | 18 cases                                                                                                                                              |
| `tests/Feature/Mail/ZonedTimeTest.php`                             | new    | 3 cases                                                                                                                                               |
| `tests/Feature/Console/NotifySessionsCommandTest.php`              | new    | 5 cases                                                                                                                                               |
| `tests/Feature/Mail/MailContentTest.php`                           | edit   | The senders map gains the new notification                                                                                                            |

No route file changes: the notice leaves by mail and its button is
`shared.episodes.show`, `T-125`'s route. No factory or seeder row: see the
last decision. `config/qori.php` is not touched: `T-123` declares
`qori.live.notice_window_days`, `notice_attempts`, `sends_per_run` and the
rest, and this task only reads them.

## Database

`session_notices` — the ledger (`D-028`). `HasUlids`, `BelongsToGroup`.

| Table             | Column                     | Type       | Null | Default   | Index / constraint                                                              |
| ----------------- | -------------------------- | ---------- | ---- | --------- | ------------------------------------------------------------------------------- |
| `session_notices` | `id`                       | ulid       | no   | —         | primary                                                                         |
| `session_notices` | `group_id`                 | ulid       | no   | —         | FK `groups` cascade; leads both indexes                                         |
| `session_notices` | `episode_id`               | ulid       | no   | —         | FK `episodes` cascade                                                           |
| `session_notices` | `user_id`                  | ulid       | no   | —         | FK `users` cascade; a Peer, or the Group owner (`T-129`)                        |
| `session_notices` | `recording_id`             | ulid       | yes  | null      | FK `episode_recordings` null on delete                                          |
| `session_notices` | `kind`                     | string     | no   | —         | `SessionNoticeKind` value                                                       |
| `session_notices` | `publication`              | smallint   | no   | 1         | `T-140` bumps it                                                                |
| `session_notices` | `status`                   | string     | no   | `pending` | `RecipientStatus` value                                                         |
| `session_notices` | `attempts`                 | smallint   | no   | 0         | Tries, successful included                                                      |
| `session_notices` | `next_attempt_at`          | timestamp  | yes  | null      | Null on an unclaimed pending, sent, skipped or exhausted row; the claim sets it |
| `session_notices` | `error`                    | text       | yes  | null      | The exception message, or a skip reason                                         |
| `session_notices` | `sent_at`                  | timestamp  | yes  | null      |                                                                                 |
| `session_notices` | `created_at`, `updated_at` | timestamps | yes  | null      |                                                                                 |
| `session_notices` | —                          | —          | —    | —         | unique `(episode_id, user_id, kind, publication)`                               |
| `session_notices` | —                          | —          | —    | —         | index `(group_id, status, next_attempt_at)`                                     |

Migration: `database/migrations/2026_09_18_000300_create_session_notices.php`

```php
Schema::create('session_notices', function (Blueprint $table): void {
    $table->ulid('id')->primary();
    $table->foreignUlid('group_id')->constrained()->cascadeOnDelete();
    $table->foreignUlid('episode_id')->constrained()->cascadeOnDelete();
    $table->foreignUlid('user_id')->constrained()->cascadeOnDelete();
    $table->foreignUlid('recording_id')->nullable()->constrained('episode_recordings')->nullOnDelete();
    $table->string('kind');
    $table->smallInteger('publication')->default(1);
    $table->string('status')->default('pending');
    $table->smallInteger('attempts')->default(0);
    $table->timestamp('next_attempt_at')->nullable();
    $table->text('error')->nullable();
    $table->timestamp('sent_at')->nullable();
    $table->timestamps();
    // One notice per person per Episode per kind per publication: the
    // guarantee that no sweep sends twice (D-028).
    $table->unique(['episode_id', 'user_id', 'kind', 'publication']);
    // The sweep's read: this Group's due rows.
    $table->index(['group_id', 'status', 'next_attempt_at']);
});
```

`down()` drops the table. The `campaign_recipients` block
(`database/migrations/2026_09_08_000000_create_qori_schema.php:215-228`) is
the precedent for the status and error columns.

## Code

```php
namespace App\Enums;

/** What a row in session_notices is about (D-028). Only RecordingReady is produced by T-128; T-129 and T-138 add theirs. */
enum SessionNoticeKind: string
{
    case RecordingReady = 'recording_ready';

    case DayBefore = 'day_before';

    case SessionCancelled = 'session_cancelled';

    case CreatorRecordingNeeded = 'creator_recording_needed';
}
```

```php
namespace App\Models;

use App\Concerns\BelongsToGroup;
use App\Enums\RecipientStatus;
use App\Enums\SessionNoticeKind;
use Carbon\CarbonImmutable;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Carbon;

/**
 * One person's copy of one notice about one Episode: the outbox (D-028).
 *
 * @property string $group_id
 * @property string $episode_id
 * @property string $user_id
 * @property ?string $recording_id
 * @property SessionNoticeKind $kind
 * @property int $publication
 * @property RecipientStatus $status
 * @property int $attempts
 * @property ?Carbon $next_attempt_at
 * @property ?string $error
 * @property ?Carbon $sent_at
 */
class SessionNotice extends Model
{
    use BelongsToGroup, HasUlids;

    protected $table = 'session_notices';

    /** @var list<string> */
    protected $fillable = [
        'group_id', 'episode_id', 'user_id', 'recording_id', 'kind', 'publication',
        'status', 'attempts', 'next_attempt_at', 'error', 'sent_at',
    ];

    // casts: kind => SessionNoticeKind::class, status => RecipientStatus::class,
    // publication => 'integer', attempts => 'integer', next_attempt_at => 'datetime',
    // sent_at => 'datetime', episode_id/user_id/recording_id => 'string'

    /** @return BelongsTo<Episode, $this> */
    public function episode(): BelongsTo;

    /** @return BelongsTo<User, $this> */
    public function user(): BelongsTo;

    /** @return BelongsTo<EpisodeRecording, $this> */
    public function recording(): BelongsTo;   // 'recording_id'

    /**
     * Unclaimed pending, or pending or failed with a retry that is due. A
     * claimed row carries a next_attempt_at in the future and does not match
     * until then; an exhausted row is failed with a null next_attempt_at and
     * never matches again.
     *
     * @param  Builder<SessionNotice>  $query
     * @return Builder<SessionNotice>
     */
    public function scopeDue(Builder $query, CarbonImmutable $now): Builder;
    // ->whereIn('status', [RecipientStatus::Pending, RecipientStatus::Failed])
    // ->where(fn (Builder $q) => $q
    //     ->where(fn (Builder $q) => $q
    //         ->where('status', RecipientStatus::Pending)
    //         ->whereNull('next_attempt_at'))
    //     ->orWhere('next_attempt_at', '<=', $now))

    /** Failed, and no retry is coming: what T-019 alerts on and T-129 counts. */
    public function isExhausted(): bool;   // status Failed && next_attempt_at === null
}
```

```php
namespace App\Services;

use App\Enums\RecipientStatus;
use App\Enums\SessionNoticeKind;
use App\Models\Access;
use App\Models\Episode;
use App\Models\EpisodeRecording;
use App\Models\Material;
use App\Models\Series;
use App\Models\SessionNotice;
use App\Models\User;
use App\Notifications\RecordingReadyNotification;
use App\Support\CurrentGroup;
use Carbon\CarbonImmutable;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Throwable;

/**
 * The session-notice outbox (D-028): rows are queued at publication and sent
 * by qori:sessions:notify, inline, with retry state on the row because the
 * queue is `deferred` and cannot retry.
 *
 * No vendor code and no acrossAllGroups(): the command establishes each
 * Group with CurrentGroup::runFor(), and every read here is scoped.
 */
class SessionNoticeService
{
    /**
     * Minutes to wait after the n-th failed try. The first try plus
     * config('qori.live.notice_attempts') retries, then the row is left
     * `failed` with a null next_attempt_at (D-028). Named after T-091's.
     */
    public const BACKOFF_MINUTES = [15, 60, 240];

    /** What `error` says on a skipped row. Ledger diagnostics, never copy. */
    public const SKIPPED_SUPPRESSED = 'suppressed';

    public const SKIPPED_ACCESS_INACTIVE = 'access_inactive';

    public const SKIPPED_RECORDING_UNAVAILABLE = 'recording_unavailable';

    public const SKIPPED_SESSION_CANCELLED = 'session_cancelled';

    public const SKIPPED_STALE = 'stale';

    public function __construct(
        private CurrentGroup $current,
        private SuppressionService $suppressions,
    ) {}

    /**
     * One pending recording_ready row per Peer with access, for a recording
     * just published. Idempotent: the unique key ignores a row that exists.
     *
     * Returns how many rows were inserted. Zero when the recording is not
     * published or is hidden, when it was published more than
     * config('qori.live.notice_window_days') ago, or when the session is
     * cancelled (content['cancelled_at']).
     *
     * Recipients: active Accesses to the Episode's Series with a user_id, whose
     * granted_at is on or before the Episode's earliest published, unhidden
     * recording's published_at — so a later part queues nothing (D-028).
     * publication = (int) ($episode->content['recording_publication'] ?? 1).
     *
     * Runs in the caller's Group context (a creator's request, or T-144's
     * sweep inside runFor()); every query is scoped.
     */
    public function queueRecordingReady(EpisodeRecording $recording): int;
    // $rows = $this->recipientsFor($episode, $firstPublishedAt)->map(fn (Access $access): array => [
    //     'id' => (string) Str::ulid(),
    //     'group_id' => $access->group_id,
    //     'episode_id' => $episode->getKey(),
    //     'user_id' => $access->user_id,
    //     'recording_id' => $recording->getKey(),
    //     'kind' => SessionNoticeKind::RecordingReady->value,
    //     'publication' => $publication,
    //     'status' => RecipientStatus::Pending->value,
    //     'attempts' => 0,
    //     'created_at' => $now,
    //     'updated_at' => $now,
    // ]);
    // return $rows->isEmpty() ? 0 : SessionNotice::query()->insertOrIgnore($rows->all());

    /**
     * Send this Group's due rows, oldest first, at most $limit (null: the
     * config value), and return how many went.
     *
     * Two steps, never one transaction. Claim: claim() locks the due rows
     * inside DB::transaction(), gives each attempts + 1 and a next_attempt_at
     * of $now plus BACKOFF_MINUTES[min(attempts, count(BACKOFF_MINUTES)) - 1],
     * status untouched, and commits. Send: outside any transaction, per
     * claimed row in order: stale → skipped; suppressed → skipped; no active
     * Access → skipped; session cancelled → skipped; no published, unhidden
     * recording → skipped; else notify() inside try/catch → sent, or failed.
     * Each outcome is one UPDATE of its own row, so a row's result is on disk
     * before the next message is handed over, and a run that dies leaves the
     * rest to be claimed again when their next_attempt_at is due — never a
     * rollback that returns a sent row to pending. Suppression is one
     * blockedForTransactional() call for the batch's addresses.
     */
    public function sendDue(CarbonImmutable $now, ?int $limit = null): int;

    /** This Group's due rows, for --dry-run. */
    public function countDue(CarbonImmutable $now): int;

    /**
     * The claim: this Group's due rows, oldest first, at most $limit, locked,
     * counted and given a retry time inside one short transaction, and
     * returned for sending after it commits.
     *
     * @return Collection<int, SessionNotice>
     */
    private function claim(CarbonImmutable $now, int $limit): Collection;
    // DB::transaction(fn (): Collection => SessionNotice::query()->due($now)->oldest()->limit($limit)->lockForUpdate()->get()
    //     ->each(fn (SessionNotice $notice) => $notice->forceFill([
    //         'attempts' => $notice->attempts + 1,
    //         'next_attempt_at' => $now->addMinutes(self::BACKOFF_MINUTES[min($notice->attempts + 1, count(self::BACKOFF_MINUTES)) - 1]),
    //     ])->save()))

    /** @return Collection<int, Access> */
    private function recipientsFor(Episode $episode, CarbonImmutable $grantedBy): Collection;
    // Access::query()->where('series_id', $episode->series_id)->active()
    //     ->whereNotNull('user_id')->where('granted_at', '<=', $grantedBy)->get()

    /** @return array{0: Episode, 1: Series} — scoped reads; a row whose Episode or Series is gone is skipped as access_inactive */
    private function subjectsFor(SessionNotice $notice): array;

    /** The notification for a row's kind; a match with one arm today, and T-129/T-138 add theirs. */
    private function notificationFor(SessionNotice $notice, Episode $episode, Series $series): RecordingReadyNotification;

    /** @return array{0: bool, 1: ?CarbonImmutable} after-session materials exist; the earliest homework due_at */
    private function materialsFor(Episode $episode): array;
    // Material::query()->where('episode_id', $episode->getKey())->get(), release === MaterialRelease::AfterSession; role === MaterialRole::Homework with due_at

    private function skip(SessionNotice $notice, string $reason): void;
    // status Skipped, error $reason, next_attempt_at null

    private function sent(SessionNotice $notice, CarbonImmutable $now): void;
    // status Sent, sent_at $now, error null, next_attempt_at null — the try was counted by claim()

    private function failed(SessionNotice $notice, Throwable $exception): void;
    // report($exception); status Failed; error Str::limit($exception->getMessage(), 500);
    // next_attempt_at = $notice->attempts > config('qori.live.notice_attempts')
    //     ? null                        // exhausted: never due again
    //     : $notice->next_attempt_at    // the retry claim() already set
}
```

```php
// App\Services\RecordingService (T-126) — one promoted dependency and one call.
public function __construct(/* T-126's */ ..., private SessionNoticeService $notices) {}

public function paste(Episode $episode, string $url, ?string $passcode, User $by): EpisodeRecording
{
    // ... T-126's body writes the row with published_at = now ...
    $this->notices->queueRecordingReady($recording);

    return $recording;
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
use Carbon\CarbonImmutable;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;

/**
 * "The recording of :title is ready" (D-028). Mail only. Not queued, and no
 * Queueable: the sender is a command that has already decided to send inline.
 *
 * Built with what it renders and runs no query, so a test can construct it.
 * Every noun goes through Terminology::line() with the Group passed
 * explicitly, because a sweep has no current Group.
 */
class RecordingReadyNotification extends Notification
{
    public function __construct(
        private Episode $episode,
        private Series $series,
        private Group $group,
        private bool $hasAfterSessionMaterials = false,
        private ?CarbonImmutable $homeworkDueAt = null,
    ) {}

    /** @return array<int, string> */
    public function via(object $notifiable): array;   // ['mail']

    public function toMail(User $notifiable): MailMessage;
    // $terminology = app(Terminology::class);
    // $zone = ZonedTime::zoneFor($notifiable, $this->group);
    // $groupZone = $this->group->timezone();
    // $replace = ['name' => $notifiable->name, 'title' => $this->episode->title, 'series_title' => $this->series->title];
    // $line = fn (string $key, array $extra = []): string => $terminology->line($key, [...$replace, ...$extra], $this->group);
    //
    // subject  live.mail.recording_ready.subject
    // greeting live.mail.greeting
    // line     live.mail.recording_ready.intro
    // line     live.mail.recording_ready.session   ['when' => ZonedTime::describe($this->episode->starts_at, $zone, $groupZone)]   when starts_at is set
    // line     live.mail.recording_ready.materials  when $hasAfterSessionMaterials
    // line     live.mail.recording_ready.homework   ['when' => ZonedTime::describe($this->homeworkDueAt, $zone, $groupZone)]        when $homeworkDueAt
    // action   live.mail.recording_ready.action → route('shared.episodes.show', ['seriesId' => $this->series->getKey(), 'episodeId' => $this->episode->getKey()])
    // line     live.mail.recording_ready.outro
}
```

```php
namespace App\Support;

use App\Models\Group;
use App\Models\User;
use Carbon\CarbonImmutable;
use Carbon\CarbonInterface;

/**
 * A time as it is written in a message (D-028): the recipient's own zone when
 * they chose one, else the Group's; the zone always named; the Group's zone
 * beside it when the two differ. T-129, T-136 and T-138 render every date
 * through this.
 */
final class ZonedTime
{
    /** "Thu 1 Oct 2026, 9:00 am AEST". The identifier follows in the lang line, because T alone is ambiguous. */
    public const FORMAT = 'D j M Y, g:i a T';

    /** users.timezone when set, else the Group's — never UTC by omission when the Group has answered. */
    public static function zoneFor(User $recipient, Group $group): string;
    // $own = $recipient->getAttributeValue('timezone');
    // return is_string($own) && $own !== '' ? $own : $group->timezone();

    /** live.mail.when, or live.mail.when_both with the Group's time when $zone !== $groupZone. */
    public static function describe(CarbonInterface $at, string $zone, string $groupZone): string;
    // $mine = CarbonImmutable::instance($at)->setTimezone($zone)->format(self::FORMAT);
    // $zone === $groupZone
    //     ? __('live.mail.when', ['time' => $mine, 'zone' => $zone])
    //     : __('live.mail.when_both', ['time' => $mine, 'zone' => $zone,
    //           'group_time' => CarbonImmutable::instance($at)->setTimezone($groupZone)->format(self::FORMAT), 'group_zone' => $groupZone])
}
```

```php
namespace App\Console\Commands;

use App\Models\Group;
use App\Services\SessionNoticeService;
use App\Support\CurrentGroup;
use Carbon\CarbonImmutable;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;

/**
 * Send the session notices that are due (D-028).
 *
 * A command, not a queued job, for the reason PurgeSeriesCommand gives:
 * the queue is `deferred` and cannot retry, so the retry state is on the
 * row and the next run picks up what this one missed. Iterates every Group
 * inside CurrentGroup::runFor(), so nothing here crosses the group scope.
 */
class NotifySessionsCommand extends Command
{
    protected $signature = 'qori:sessions:notify {--dry-run : Count what is due, send nothing}';

    protected $description = 'Send the session notices that are due, at most qori.live.sends_per_run a run';

    public function handle(SessionNoticeService $notices, CurrentGroup $current): int;
    // $now = CarbonImmutable::now(); $dryRun = (bool) $this->option('dry-run');
    // $budget = (int) config('qori.live.sends_per_run'); $due = 0; $sent = 0;
    // countDue() runs for every Group on every run, dry or not: one query per Group, accepted at pilot scale (Decisions).
    // foreach (Group::query()->cursor() as $group) {
    //     $current->runFor($group, function () use (...): void {
    //         $due += $notices->countDue($now);
    //         if (! $dryRun && $sent < $budget) {
    //             $sent += $notices->sendDue($now, $budget - $sent);
    //         }
    //     });
    // }
    // Log::info('qori:sessions:notify', ['due' => $due, 'sent' => $sent, 'dry_run' => $dryRun]);   // the heartbeat T-019 reads
    // $this->line(sprintf('%s %d, %d due.', $dryRun ? 'Would send up to' : 'Sent', $dryRun ? min($due, $budget) : $sent, $due));   // diagnostic, not copy
    // return self::SUCCESS;
}
```

```php
// routes/console.php — the block at :15-27 is replaced by this comment, and the line is added beside qori:series:purge.

/*
| The schedule. Laravel Cloud runs `schedule:run` every minute since 11
| September 2026 (docs/planning/release-prerequisites.md). Two things it does
| not do: a changed frequency takes effect on the next deploy, because the
| wake-up schedule is captured then; and a task without onOneServer() runs on
| every replica.
|
| qori:sessions:notify: every five minutes is provisional — the owner sets
| the interval against the sleep timeout, with T-091's (D-028). Never more
| often than that timeout.
*/
Schedule::command('qori:sessions:notify')
    ->everyFiveMinutes()
    ->withoutOverlapping()
    ->onOneServer();
```

```php
// App\Console\Commands\MailCheckCommand — the eighth message.
private const EXPECTED = 8;
// The class docblock ("renders all seven", :35) and inspect()'s ("make seven times", :118) say eight.
// scratch(): $group->update(['timezone' => 'Australia/Brisbane']); $peer created with 'timezone' => 'America/New_York';
//   inside runFor, after the file Episode: $episode = app(EpisodeService::class)->add(
//       $series, 'Live clinic', EpisodeType::Live, EpisodeProvider::Link,
//       ['join_url' => 'https://meet.google.com/abc-defg-hij', 'records' => true], false,
//       CarbonImmutable::now()->addDay(), 60);
//   returns [$user, $series, $peer, $episode]
// send(): after the grant, inside the same runFor:
//   app(RecordingService::class)->paste($episode, 'https://example.test/recordings/one', null, $user);
//   app(SessionNoticeService::class)->sendDue(CarbonImmutable::now());
```

`lang/en/live.php` gains a `mail` block under `T-125`'s file header, with a
comment stating the zone rule and pointing at `App\Support\ZonedTime`.

`docs/flows/live-sessions.md` gains "When a recording is published":
`RecordingService::paste()` → `SessionNoticeService::queueRecordingReady()`
→ `session_notices` rows; `qori:sessions:notify` → `sendDue()` per Group →
the claim, the five skips, `RecordingReadyNotification`, the backoff and
what an exhausted row means. `docs/flows/README.md`'s row for the file names the
notices. `docs/tinker/live-sessions.md` gains the recipe below;
`docs/tinker/mail.md` says eight where it says seven, and the sample output
gains "The recording of Live clinic is ready .. ok".

```php
// docs/tinker/live-sessions.md — "Publish a recording and send the email"
$episode = App\Models\Episode::query()->where('type', 'live')->first();
$series = App\Models\Series::query()->acrossAllGroups()->whereKey($episode->series_id)->first();
app(App\Support\CurrentGroup::class)->runFor($series->group, fn () =>
    app(App\Services\RecordingService::class)->paste($episode, 'https://example.test/recordings/one', null, $series->group->owner));
```

```bash
php artisan qori:sessions:notify --dry-run   # "Would send up to 2, 2 due."
php artisan qori:sessions:notify             # then read it at http://localhost:8025
```

## Copy

All in `lang/en/live.php`. `:title` is the Episode's title, `:series_title`
the Series', `:name` the recipient's; `:series` and `:episode` are the
Group's nouns through `Terminology::line()`. `:when` is `ZonedTime::describe()`'s
answer, itself `live.mail.when` or `live.mail.when_both`. No line says "live
now", "has ended", "on its way" or "processing" (`D-026`); no line names a
vendor; no article stands before a noun placeholder.

| Key                                   | File               | English                                                                                                      |
| ------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------ |
| `live.mail.greeting`                  | `lang/en/live.php` | Hi :name,                                                                                                    |
| `live.mail.when`                      | `lang/en/live.php` | :time (:zone)                                                                                                |
| `live.mail.when_both`                 | `lang/en/live.php` | :time (:zone) · :group_time (:group_zone)                                                                    |
| `live.mail.recording_ready.subject`   | `lang/en/live.php` | The recording of :title is ready                                                                             |
| `live.mail.recording_ready.intro`     | `lang/en/live.php` | The recording of :title is ready to watch. It's on your :series page, with everything else for that session. |
| `live.mail.recording_ready.session`   | `lang/en/live.php` | The session was scheduled for :when.                                                                         |
| `live.mail.recording_ready.materials` | `lang/en/live.php` | Materials shown after the session are on the same page.                                                      |
| `live.mail.recording_ready.homework`  | `lang/en/live.php` | Homework is due :when.                                                                                       |
| `live.mail.recording_ready.action`    | `lang/en/live.php` | Open the :episode                                                                                            |
| `live.mail.recording_ready.outro`     | `lang/en/live.php` | You're getting this because you have access to :series_title.                                                |

"Was scheduled for" states the schedule, which Qori observed; "is ready to
watch" states the creator's act. Neither claims the session ended
(`D-026`). The console's `Would send up to …` and the heartbeat are
diagnostics for a developer and are not copy.

## Routes

None. The notice leaves by mail; its button is `shared.episodes.show`
(`T-125`), and `qori:sessions:notify` is a console command.

## Tests

**New: `tests/Feature/Mail/RecordingReadyTest.php` — 18 cases**
(`RefreshDatabase`; `Notification::fake()` except where a real send is
forced; a `scene()` helper as `LiveSessionTest.php:40-58` with a Group in
`Australia/Brisbane`, a Series, a live Episode starting 1 November 2026
09:00 Brisbane through `EpisodeService::add()`, and Peers through
`AccessService::grant()` inside `CurrentGroup::runFor()`; a `paste()`
helper calling `RecordingService::paste()` in the same context; the clock
moved with `CarbonImmutable::setTestNow()`)

1. `test_it_queues_one_pending_row_per_peer_with_access_when_a_recording_is_pasted`
   — two Peers granted, then a paste in the same second; two rows, `kind`
   `recording_ready`, `publication` 1, `status` pending, `attempts` 0,
   `recording_id` the pasted row, `group_id` the Series' Group.
2. `test_it_queues_nothing_for_a_peer_granted_after_publication` — paste, move the
   clock a minute, grant a third Peer; still two rows.
3. `test_it_queues_nothing_new_for_a_second_part_and_sends_nothing_more` — paste,
   grant a Peer, paste again; the first Peers' rows are unchanged, the late
   Peer has none; `sendDue()` sends two and a second run sends none.
4. `test_it_queues_nothing_for_a_recording_published_longer_ago_than_the_window`
   — a recording whose `published_at` is `notice_window_days + 1` days ago
   (written directly); `queueRecordingReady()` returns 0.
5. `test_it_queues_nothing_for_a_cancelled_session` — `content['cancelled_at']`
   set before the paste; 0 rows.
6. `test_it_marks_the_row_sent_and_mails_the_peer` — `sendDue()`
   returns 1; `status` sent, `sent_at` now, `attempts` 1, `error` null;
   `Notification::assertSentTo($peer, RecordingReadyNotification::class)`.
7. `test_it_skips_a_suppressed_address_and_sends_nothing` —
   `SuppressionService::hardBounce($peer->email)` (as
   `tests/Feature/Campaigns/SuppressionTest.php:37`); `status` skipped,
   `error` `suppressed`; `assertNotSentTo`.
8. `test_it_skips_a_revoked_access_at_send_time` — queue, then
   `AccessService::revoke()`; skipped, `access_inactive`.
9. `test_it_skips_a_recording_hidden_before_the_run` — queue, then
   `hidden_at` set on the only recording; skipped, `recording_unavailable`.
10. `test_it_skips_a_session_cancelled_before_the_run` — queue, then
    `content['cancelled_at']`; skipped, `session_cancelled`.
11. `test_it_skips_a_row_older_than_the_window_as_stale` — queue, then
    `forceFill(['created_at' => now()->subDays(8)])->save()`; skipped,
    `stale`; nothing sent.
12. `test_it_retries_a_failed_send_with_backoff_and_then_leaves_it` — no
    `Notification::fake()`; `Mail::shouldReceive('mailer')->andThrow(new RuntimeException('down'))`
    installed before the first run, which every send meets because
    `MailChannel::send()` asks the manager for a mailer per message
    (`vendor/laravel/framework/src/Illuminate/Notifications/Channels/MailChannel.php:66`);
    run at t0: failed, `attempts` 1, `error` `down`, `next_attempt_at`
    t0+15m; at t0+14m: untouched; at t0+15m: `attempts` 2, next t0+75m; at
    t0+75m: `attempts` 3, next t0+315m; at t0+315m: `attempts` 4,
    `next_attempt_at` null, `isExhausted()`; a run at t0+1d touches nothing.
13. `test_it_sends_at_most_the_configured_number_a_run_and_the_next_run_continues`
    — `config(['qori.live.sends_per_run' => 2])`, three Peers; first run
    returns 2 and one row stays pending; second run returns 1.
14. `test_it_points_the_button_at_the_episode_address_and_carries_no_recording_link_or_passcode`
    — a paste with a passcode; `toMail()`'s `actionUrl` is
    `route('shared.episodes.show', [...])`; neither the recording URL nor
    the passcode appears in the subject, the lines or the action.
15. `test_it_speaks_the_groups_vocabulary` — a Group entitled as
    `TerminologyTest::entitle()` does (`tests/Feature/TerminologyTest.php:47-50`
    — read it: it sets the plan's `Terminology::ENTITLEMENT` config key, and
    without it the labels are ignored, `:99-100`), with
    `settings[Terminology::SETTINGS_KEY]` as `customLabels()` (`:36-45`); the
    intro says "your Trail page" and the action "Open the Practice"; default
    nouns for a Group that is not entitled.
16. `test_it_shows_the_session_in_the_peers_zone_with_the_groups_zone_beside_it`
    — the Peer in `America/New_York`; the session line contains
    "Sat 31 Oct 2026, 7:00 pm EDT (America/New_York)" and
    "Sun 1 Nov 2026, 9:00 am AEST (Australia/Brisbane)" — owner acceptance 2
    across the 1 November 2026 boundary, on the mail.
17. `test_it_uses_the_groups_zone_alone_when_the_peer_has_not_chosen_one`
    — `users.timezone` null; the line names Brisbane once and no second zone.
18. `test_it_names_after_session_materials_and_homework_due_in_the_peers_zone`
    — an `after_session` material and a `homework` material with `due_at`
    (`T-130`'s `MaterialService::add()`); both lines present, the due time
    in New York with Brisbane beside it; absent when there are no such rows.

**New: `tests/Feature/Mail/ZonedTimeTest.php` — 3 cases** (Feature, not
Unit: `describe()` reads lang)

1. `test_it_names_the_zone_and_shows_the_groups_zone_beside_a_different_one`
   — `describe()` for 2026-10-31 23:00 UTC with `America/New_York` and
   `Australia/Brisbane` is the `when_both` line with both strings of case 16.
2. `test_it_shows_one_time_when_the_zones_agree` — the same instant with
   Brisbane twice is the `when` line, once.
3. `test_it_falls_back_to_the_groups_zone_and_not_to_utc` —
   `zoneFor()` on a User with no zone and a Group in Brisbane is
   `Australia/Brisbane`; with a Group that has no zone but an owner in
   Melbourne, `Australia/Melbourne`; a User with `Europe/London` gets it.

**New: `tests/Feature/Console/NotifySessionsCommandTest.php` — 5 cases**

1. `test_it_sends_due_notices_for_every_group_inside_that_groups_context` —
   two Groups, a pasted recording and a Peer in each; `artisan('qori:sessions:notify')`
   exits 0; both rows sent, each `group_id` its own Group's; each mail's
   nouns are that Group's.
2. `test_it_caps_the_run_and_not_each_group` — `sends_per_run` 1, two Groups
   with one row each; one sent, one pending after the run.
3. `test_it_counts_what_is_due_and_sends_nothing_on_a_dry_run` — `--dry-run` prints
   the count; every row still pending; `Notification::assertNothingSent()`.
4. `test_it_logs_a_heartbeat_each_run` — `Log::spy()`; after a run with
   nothing due, `info` was called once with `'qori:sessions:notify'` and a
   context carrying `due`, `sent` and `dry_run`.
5. `test_it_is_scheduled_every_five_minutes_without_overlap_on_one_server` —
   the event in `app(Schedule::class)->events()` whose `command` contains
   `qori:sessions:notify` has `expression` `*/5 * * * *`,
   `withoutOverlapping` true and `onOneServer` true
   (`vendor/laravel/framework/src/Illuminate/Console/Scheduling/ManagesAttributes.php:14,63,77`).

**Changed:**

- `tests/Feature/Mail/MailContentTest.php` — the senders map at `:162-168`
  gains `'RecordingReadyNotification' => 'SessionNoticeService'`; no new
  method. Without it `test_every_notification_class_is_covered_by_the_command`
  fails on the new class.

Total: 26 new cases.

## Acceptance

- [ ] A creator pastes a recording link on a live Episode; every Peer who
      had access when it was pasted receives one email, the session time in
      their own zone with the Group's zone beside it when they differ, and
      its button lands on the Episode's card where Watch is (owner acceptance 4)
- [ ] Nothing is queued or sent when the scheduled end passes without a
      recording; no email goes before a recording is published, and the
      email never carries the recording URL or a passcode (owner acceptance 5)
- [ ] A second part, a hidden recording, a cancelled session, a revoked
      Access, a suppressed address and a stale row each leave a `skipped` row
      or no row, and never a message
- [ ] A send that fails is retried after 15, 60 and 240 minutes and then left
      `failed` with a null `next_attempt_at`, and the exception is reported
- [ ] `qori:sessions:notify` sends at most `qori.live.sends_per_run` a run
      across every Group, logs one heartbeat, is scheduled every five minutes
      without overlap on one server, and `--dry-run` sends nothing
- [ ] A Group with its own vocabulary gets its own words in the email, with
      the Group passed to `Terminology::line()` explicitly
- [ ] `php artisan qori:mail:check` sends and reads eight messages, and the
      eighth shows both zones
- [ ] `routes/console.php` no longer says the cron entry does not exist;
      `docs/flows/live-sessions.md` describes the chain; the recipes in
      `docs/tinker/live-sessions.md` and `docs/tinker/mail.md` run as written
- [ ] No `acrossAllGroups()` caller is added and no `ShouldQueue`
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- The schedule interval: five minutes is provisional, and `D-028` gives the
  choice to the owner, made together with `T-091`'s interval against Laravel
  Cloud's sleep timeout (`release-prerequisites.md:27`) — the owner's.
  _Asked_ 26 September 2026, with 15 or 30 minutes suggested against the
  sleep timeout; built at five minutes, as provisional, meanwhile. `T-091`'s
  half is moot (its sweep was removed under `D-040`), so this interval is
  the only one to choose. The answer changes one line in
  `routes/console.php` and case 5 of `NotifySessionsCommandTest`.
- ~~`T-126` and `T-127` `ready`, so `RecordingService::paste()`'s signature,
  `EpisodeRecording`'s columns and `hidden_at` are frozen — anyone's; keep
  draft until they are.~~ **Answered 26 September 2026:** both are `done`
  (qori `e40e651`, `99f2915`); the signature, the columns and `hidden_at` are
  as this spec cites them, with what the Re-scope log says.

## Re-scope log

**2026-09-26 — reconciled with `T-126`, `T-127` and the code as built.**

- **`RecordingService` already has a constructor** (`T-127`:
  `LiveSessionService $sessions`); `SessionNoticeService $notices` is promoted
  beside it. `paste()` writes the row inside a transaction with the Episode
  locked, and calls `queueRecordingReady()` inside that transaction, after
  the row and `T-127`'s withdrawal of a "not recorded" declaration, so the
  recording and its notices commit together.
- **`routes/console.php`'s stale comment is already gone**: since
  20 September it says the Scheduler is on and running. This task adds the
  schedule line and its own comment, and leaves that block alone.
- **`qori:mail:check` sends nine messages, not seven** (`T-043`'s invitation
  and `T-151`'s reconnect came since), so this makes ten; its class docblock
  still says eight and is corrected with it.
- **The notice waits for the card.** `T-126` lets a recording be pasted before
  the session ends, and `T-126`'s own Decisions keep Join on the card until
  its window closes; a notice sent at once would say "ready to watch" while
  the card still offered Join. `queueRecordingReady()` gives a row queued
  before Join's window closes a `next_attempt_at` of that close, so the `due`
  scope leaves it until then; one queued after is due at once, as specified.
- **A live row with no start queues nothing.** It has no card for Watch to be
  on (`T-125`'s `isScheduled()`), and no window to wait for.
- **A Peer the sweep skipped because nothing was visible still hears once.**
  Pasting a wrong link, hiding it and pasting again — `T-127`'s correction —
  could leave every row `skipped` as `recording_unavailable` if a sweep ran
  while nothing was visible, and the unique key would then ignore the new
  paste's rows for good: the class would never hear. `queueRecordingReady()`
  re-arms those rows (pending again, the new recording's id), and
  `RecordingService::unhide()` calls it too, because showing a recording
  again makes one visible just as a paste does. A row that was `sent` is never
  re-armed: a replaced link sends nothing (`D-028`).

## Notes

`T-126`'s draft is edited to: `RecordingService` takes `SessionNoticeService`
by constructor promotion and `paste()` calls `queueRecordingReady($recording)`
after the row is written; `app/Services/RecordingService.php` is listed here
as an edit for that one call.

`T-130`'s and `T-136`'s front matter is edited to the brief's table:
`T-130` `blocks: T-128, T-131, T-132, T-139` and `T-136`
`depends: T-128, T-132`, so `blocks:` here is the inverse of every other
task's `depends:` and `php artisan qori:tasks --check` agrees. This task
depends on `T-130` because its mail carries the after-session materials
line and the homework due line, and `T-136` depends on this task for
`App\Support\ZonedTime`. `T-136`'s Decisions and its "Before this can be
ready" still say `T-128` is not in its chain and offer to create `ZonedTime`
itself; that wording is `T-136`'s writer's to bring in line, and the
alternative is closed.

`D-028` says `recording_ready` goes to Accesses "granted before that
recording's `published_at`", and the brief wrote it `granted_at < published_at`;
`recipientsFor()` codes `<=` for the reason under Decisions. `D-028`'s
wording is to be amended — a one-line note under a day's heading in
`decisions.md` saying "before" means "not after, to the second" — so nobody
writing `T-140` or `T-144` implements `<`.

`T-140`'s draft, when written, needs a way past the queue-time window: a
deliberate re-send of a recording published more than
`qori.live.notice_window_days` ago is refused by `queueRecordingReady()` as
specified. A named parameter on that method is the obvious shape, and its
writer decides. The same call site decides the recipient cut-off for a
correction — this task's "earliest published recording" rule excludes Peers
who joined after the first publication, which is right for a first notice
and may not be for a corrected one.

`T-129` and `T-138` insert their kinds through the same `insertOrIgnore()`
shape and add a `match` arm in `notificationFor()`; `sendDue()`'s five skips
apply to every kind, and the `recording_unavailable` skip is the
`recording_ready` arm's alone. `T-129`'s "sent to :sent, :failed failed"
reads `status` and `isExhausted()` from this table.

`T-025`'s Scope line "Per-Peer timezones. Still not wanted" is superseded
by `D-028`, and its owner rewrites it; `App\Support\ZonedTime` is what its
mail half would reuse.

`T-032` (mail arriving through Postmark) comes before `recording_ready`
reaches a real Peer (`D-031`). It is a prerequisite for the pilot, not for
this task: the suite and `qori:mail:check` prove the message renders and the
ledger records what the mailer accepted, and `sent` means exactly that.

`RecipientStatus::Failed` gets its first producer here, which
`docs/tinker/mail.md` says was missing; Mailpit's on-demand SMTP failures
are the way to see one by hand.

`onOneServer()` and `withoutOverlapping()` both use the cache. Locally that
is `file`, which is fine on one machine; in production it is Valkey. A
`CACHE_STORE=array` environment would make both no-ops, which is one more
reason the batch is locked in the database too.
