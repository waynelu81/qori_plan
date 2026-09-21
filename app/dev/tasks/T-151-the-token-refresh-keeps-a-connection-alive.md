---
id: T-151
title: The token refresh keeps a connection alive
stream: storage
status: done
owner: claude
estimate: M
depends: T-044
blocks: T-091
---

# T-151 — The token refresh keeps a connection alive

> **Cut out of `T-044` on 20 September 2026**, which was `L` at 68 paths and
> named this as part (b) of its own split under "Before this can be ready".
> Nothing here is invented: the decisions, the code and the eight test cases
> are `T-044`'s, moved whole. One thing is answered rather than moved — the
> storage review's `F08`, that the advisory lock had no acquisition budget —
> because the lock is this task's file and the finding has nowhere else to go.

## Why

A creator connects Google Drive once and expects it to keep working. Google's
refresh tokens die after six months unused, past 100 live tokens per account
per client, on revocation, and after seven days while the Cloud app is in
Testing; Microsoft's last 90 days and are replaced on every use; Zoom's last
90 days and rotate. Without renewal, `T-044`'s connection works until the
access token expires and then fails silently — and the person who finds out is
a Peer who cannot open an Episode.

Afterwards a dead or dying token is found by a daily command or by the call
that needs it, the creator is emailed once, and the Integrations page says
what to do.

## Decisions taken to make this specifiable

**Renewal is a daily `qori:connections:refresh`, plus an on-demand refresh
before any use.** The queue is `deferred` and cannot retry
(`config/queue.php:16-39`), so a scheduled command is the durable path, as
`qori:series:purge` is (`routes/console.php:28`). On-demand alone would leave a
token that nobody touches for six months to die; the schedule alone would
leave a token that expires between runs unusable for up to a day.

**The command is scheduled `->daily()` alone, with no `onOneServer()`.**
`qori:series:purge` is scheduled the same way (`routes/console.php:28`). Until
a second replica exists, two overlapping runs can only refresh a row twice,
one after the other under the lock; `onOneServer()` comes with that replica,
which is `operations`'.

**One advisory lock class for the whole app.** `AdvisoryLock`
(`pg_advisory_xact_lock` inside a transaction, keyed by a namespace and a key)
in this task's `'connection'` namespace, and `T-091`'s container lock calls it
rather than keeping a `ContainerLock` of its own — decided on `T-044`,
19 September 2026.

**The lock waits at most `AdvisoryLock::WAIT_SECONDS`, and says whether it got
it** (storage review `F08`, 20 September 2026). A blocking
`pg_advisory_xact_lock` can hold a request for an unbounded time in front of a
vendor call that `D-034` bounds carefully, which makes the budget a lie. So the
transaction does `SET LOCAL lock_timeout` first and `run()` answers `bool`: true
when it took the lock and ran the callback, false when it did not and did not.
A callback's own result is captured by the closure, because a returned value
could not tell "the callback answered null" from "the callback never ran".

**A busy lock is never a failure.** Somebody else is refreshing the same row
right now, which is the system working. `refresh()` answers
`RefreshResult::unavailable()` and **does not** increment `refresh_failures`;
`fresh()` returns the row it re-read and lets the caller use the token it has,
which is either still valid or about to be renewed by the holder. Counting a
busy lock would mark a healthy connection for reconnect after three quiet
collisions.

**Under the lock the row is read again before its refresh token is used**, so a
second caller that waited uses the token the first one stored — Microsoft and
Zoom replace theirs on every use — and `fresh()` refreshes only if the row it
re-read is still inside `REFRESH_MARGIN_MINUTES`.

**`invalid_grant` marks at once; anything else is counted, and the third in a
row marks.** A revoked token will never come back, so waiting three days to
say so helps nobody. A timeout or a 500 is usually Google having a minute, and
marking a live connection for reconnect on one of those sends the creator to
do work they did not need to do. `REFRESH_FAILURES_BEFORE_RECONNECT` is 3, so a
silently dead token is found within days rather than when a Peer arrives.

**The owner is emailed once per death, on the call that marks the row.**
`ConnectionService::markForReconnect()` sends
`ConnectionNeedsReconnectNotification` only when `needs_reconnect_at` was not
already set, so the next day's run — and `T-091`'s vendor 401, which calls the
same method with `'unauthorized'` — add no second email.

**The command walks Groups and never calls `acrossAllGroups()`.**
`Group::query()->cursor()` with `CurrentGroup::runFor()` around each, as
`T-091`'s sweep does. `acrossAllGroups()` has two permitted callers and the
admin query layer (`CLAUDE.md`), and a console command is neither.

**No schema.** `T-044`'s migration adds all four columns, because its connect
step writes and clears every one of them. This task adds no table and no
column.

**`GoogleAccounts::refresh()` and its three cases stay on `T-044`.** A
connector that does not implement its own interface does not compile, so
`ConnectsAccounts::refresh()`, `refreshesOnSchedule()`, `RefreshResult` and
Google's implementation of them are `T-044`'s. The seam is between a connector
that _can_ refresh a token and Qori _deciding when to_: this task is the
second.

## Preconditions

**Data this task verifies against:** a clean database.

**Equipment:** none. Every vendor call is faked.

**`T-044` done**, for the `connections` columns, `Connection::needsReconnect()`
and `isLive()`, `ConnectsAccounts` with `refresh()` and `refreshesOnSchedule()`,
`RefreshResult`, `GoogleAccounts::refresh()`, `ConnectionService` with
`connectorFor()`, the `account-connectors` tag, `tests/Doubles/ConnectsNothing.php`
and `lang/en/connections.php`.

**Spike:** the refresh bodies are `T-093`'s fixtures under
`tests/Fixtures/google/`: `oauth-refresh.json` and
`errors-oauth-token-400-invalid_grant.json`, both from its step 15. Nothing
here names a response field those files do not show.

## Scope

**In:**

- `App\Support\AdvisoryLock`, with its acquisition budget.
- `ConnectionService::fresh()`, `refresh()`, `refreshDue()` and
  `markForReconnect()`, and the four constants they read.
- `Connection::markForReconnect()` and `scopeRefreshable()`.
- `qori:connections:refresh`, its `--dry-run`, and the daily schedule.
- `ConnectionNeedsReconnectNotification` and its copy.
- `ConnectionFactory`'s `expiring()` state.

**Out:**

- `ConnectsAccounts::refresh()`, `refreshesOnSchedule()`, `RefreshResult` and
  `GoogleAccounts::refresh()` — `T-044`'s, with their three cases (Decisions).
- The Integrations page's `needs_reconnect` status line and the Reconnect
  button, which are `T-044`'s: this task sets the state the page already
  renders.
- `App\Listeners\ResumeGrantsAfterReconnect` and `VendorAccessService`'s calls
  to `fresh()` and `markForReconnect()` (`T-091`).
- `T-091`'s container lock, which calls `AdvisoryLock` in its own task.
- Any refresh for Dropbox or Vimeo: `refreshesOnSchedule()` is false for both
  (`T-044`'s Decisions), and their connectors are `T-096`'s and `T-090`'s.
- Retrying a marked row automatically. A marked connection waits for the
  creator to reconnect, which is `T-044`'s Reconnect button.

## Files

| Path                                                                                 | Change | Notes                                                                                        |
| ------------------------------------------------------------------------------------ | ------ | -------------------------------------------------------------------------------------------- |
| `app/Support/AdvisoryLock.php`                                                       | new    | The one lock; `T-091` calls it for its container lock                                        |
| `app/Models/Connection.php`                                                          | edit   | `markForReconnect()`, `scopeRefreshable()`; `T-044` adds the fillable, casts and the readers |
| `app/Services/ConnectionService.php`                                                 | edit   | `fresh()`, `refresh()`, `refreshDue()`, `markForReconnect()` and four constants              |
| `app/Notifications/ConnectionNeedsReconnectNotification.php`                         | new    | To the Group's owner; not queued (`app/Notifications/SeriesAccessNotification.php:19-22`)    |
| `app/Console/Commands/RefreshConnectionsCommand.php`                                 | new    | `qori:connections:refresh`                                                                   |
| `routes/console.php`                                                                 | edit   | `Schedule::command('qori:connections:refresh')->daily()`                                     |
| `lang/en/connections.php`                                                            | edit   | The five `mail.reconnect.*` lines; `T-044` creates the file                                  |
| `database/factories/ConnectionFactory.php`                                           | edit   | `expiring()`; `T-044` adds `google()` and `needsReconnect()`                                 |
| `docs/flows/storage.md`                                                              | edit   | A Renewal section under Connections, which `T-044` writes                                    |
| `docs/tinker/connections.md`                                                         | edit   | A recipe for expiring a token and running the command; `T-044` creates the file              |
| `tests/Feature/Console/RefreshConnectionsCommandTest.php`                            | new    | 8 cases                                                                                      |
| `tests/Unit/Support/AdvisoryLockTest.php`                                            | new    | 3 cases                                                                                      |
| `app/Console/Commands/MailCheckCommand.php` `tests/Feature/Mail/MailContentTest.php` | edit   | Added during execution — the reconnect email joins `qori:mail:check`, so somebody reads it   |

`app/Data/RefreshResult.php` is `T-044`'s and is not created here.

## Added during execution

- `app/Console/Commands/MailCheckCommand.php` and
  `tests/Feature/Mail/MailContentTest.php` —
  `MailContentTest::test_every_notification_class_is_covered_by_the_command`
  refuses any notification `qori:mail:check` never sends, because nobody has
  then read it. This task adds the sixth such notification and the Files table
  did not carry either file, so the gate failed on the first full run.
  `send()` now creates a connection and calls
  `ConnectionService::markForReconnect()` — through the service that owns the
  message, never by constructing the notification, which is that command's own
  documented rule — `EXPECTED` moves from 7 to 8, and the test's sender map
  gains `ConnectionNeedsReconnectNotification => ConnectionService`. The
  scratch row goes with the Group in `purgeScratch()`, which cascades.

## Database

None. `T-044`'s
`database/migrations/2026_09_20_000000_add_reconnect_state_to_connections.php`
adds `needs_reconnect_at`, `reconnect_reason`, `refreshed_at` and
`refresh_failures`, because its connect step writes and clears all four
(Decisions).

## Code

```php
namespace App\Support;

/** The one advisory lock: this task's 'connection' namespace, and T-091's container lock, which calls it rather than keeping a class of its own. */
final class AdvisoryLock
{
    /** Bounds the wait for the lock (F08), so a request never queues longer than the call it guards is allowed to take. */
    public const WAIT_SECONDS = 3;

    /**
     * DB::transaction, then SET LOCAL lock_timeout = $waitSeconds * 1000 || 'ms',
     * then SELECT pg_advisory_xact_lock(hashtext(?), hashtext(?)) with $namespace and $key.
     * A QueryException whose SQLSTATE is '55P03' (lock_not_available) is the budget running out and is answered false;
     * every other QueryException is a real fault and is rethrown.
     *
     * @param  Closure(): void  $callback  captures whatever it produces; a returned value could not tell an answer of null
     *                                     from a callback that never ran
     * @return bool  true when the lock was taken and $callback ran, false when it was not and $callback did not
     */
    public static function run(string $namespace, string $key, Closure $callback, int $waitSeconds = self::WAIT_SECONDS): bool;
}
```

```php
namespace App\Models;

class Connection extends Model
{
    /** needs_reconnect_at now, reconnect_reason; nothing else — ConnectionService::markForReconnect() decides who is told. */
    public function markForReconnect(string $reason): void;
    /** usable, has a refresh token, not marked for reconnect. */
    public function scopeRefreshable(Builder $query): Builder;
}
```

```php
namespace App\Services;

class ConnectionService
{
    // SWEEP_TIMEOUT_SECONDS (30) is T-044's, declared there and read here as the command's budget, which nobody waits on
    public const REFRESH_MARGIN_MINUTES = 5;
    public const REFRESH_FAILURES_BEFORE_RECONNECT = 3;
    public const LOCK_NAMESPACE = 'connection';

    /** When expires_at is within REFRESH_MARGIN_MINUTES: takes the lock, re-reads the row, and refreshes it only if it is still within the
     *  margin; returns the fresh row. A lock it could not take within AdvisoryLock::WAIT_SECONDS returns the re-read row unrefreshed, because
     *  the holder is renewing it now. T-091's VendorAccessService calls this before each vendor call, passing its own shorter budget
     *  from a Peer's request. */
    public function fresh(Connection $connection, int $timeoutSeconds = self::REQUEST_TIMEOUT_SECONDS): Connection;
    /** One row under AdvisoryLock::run(self::LOCK_NAMESPACE, $connection->getKey(), …), re-read inside the lock before its refresh token is
     *  used; records the outcome; never throws. A lock it could not take answers RefreshResult::unavailable() and counts no failure. */
    public function refresh(Connection $connection, int $timeoutSeconds = self::REQUEST_TIMEOUT_SECONDS): RefreshResult;
    /** The command's pass for the current Group: refreshable rows whose connector refreshesOnSchedule(), each with SWEEP_TIMEOUT_SECONDS. Rows touched. */
    public function refreshDue(): int;
    /** $connection->markForReconnect($reason), and ConnectionNeedsReconnectNotification to the Group's owner only when the row was not
     *  marked already, so each dead token emails once. Reasons: 'invalid_grant' and 'refresh_failed' from refresh(); 'unauthorized'
     *  from T-091's VendorAccessService on a vendor 401. */
    public function markForReconnect(Connection $connection, string $reason): void;
}
```

`refresh()` on `renewed` stores the tokens, `refreshed_at`, and zeroes
`refresh_failures`; on `revoked` calls `markForReconnect('invalid_grant')`; on
`unavailable` from the connector increments `refresh_failures` and calls
`markForReconnect('refresh_failed')` at `REFRESH_FAILURES_BEFORE_RECONNECT`; on
`unavailable` because the lock was busy, changes nothing.
`markForReconnect()` is where the owner is emailed, once, on the call that
marks the row.

```php
// App\Console\Commands\RefreshConnectionsCommand
protected $signature = 'qori:connections:refresh {--dry-run : Count what would be refreshed, call nothing}';
protected $description = 'Renew the storage and live-session tokens that expire when unused, in every group';
public function handle(ConnectionService $connections, CurrentGroup $current): int;
// foreach (Group::query()->cursor() as $group): $current->runFor($group, fn (): int => $connections->refreshDue()) — no acrossAllGroups() caller, as T-091's sweep

// routes/console.php
Schedule::command('qori:connections:refresh')->daily();   // no onOneServer() until a second replica exists, as qori:series:purge
```

`ConnectionNeedsReconnectNotification` takes the `Connection` and sends `mail`
only, to the Group's owner, built from the `connections.mail.reconnect.*` keys
with `:provider` the provider's `connections.providers.<provider>.name`,
`:account` the row's `account_name`, `:group_name` the Group's name and
`:name` the owner's. The action links to the Integrations page.

## Copy

`T-044` creates `lang/en/connections.php`; these five lines are added to it.

| Key                                      | File                      | English                                                                                                                                                                               |
| ---------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `connections.mail.reconnect.subject`     | `lang/en/connections.php` | :provider needs a fresh sign-in                                                                                                                                                       |
| `connections.mail.reconnect.greeting`    | `lang/en/connections.php` | Hi :name,                                                                                                                                                                             |
| `connections.mail.reconnect.intro`       | `lang/en/connections.php` | Qori can no longer reach the :provider account (:account) connected to :group_name. That happens when access is removed, a password is reset, or the account goes unused for a while. |
| `connections.mail.reconnect.consequence` | `lang/en/connections.php` | People already let in keep opening what you share from there. Until you connect again, nobody new is let in, and anyone whose access ends stays in your account.                      |
| `connections.mail.reconnect.action`      | `lang/en/connections.php` | Connect again                                                                                                                                                                         |
| `connections.mail.reconnect.outro`       | `lang/en/connections.php` | It takes a minute, and nothing else changes.                                                                                                                                          |

## Routes

None. The schedule is a console entry, not a route.

## Tests

**New: `tests/Feature/Console/RefreshConnectionsCommandTest.php` — 8 cases**

1. `test_it_refreshes_refreshable_rows_in_every_group` — one Google row in each of two Groups; both `refreshed_at` set.
2. `test_it_skips_providers_that_do_not_refresh_on_a_schedule` — a Dropbox row through `ConnectsNothing`; no call.
3. `test_it_skips_revoked_and_marked_rows`.
4. `test_invalid_grant_marks_the_row_and_emails_the_owner` — `Notification::fake()`; `reconnect_reason` `invalid_grant`; one notification; a second `ConnectionService::markForReconnect()` on the marked row, as `T-091`'s 401 would make, sends none.
5. `test_a_transient_failure_is_counted_and_the_third_marks_the_row` — two runs leave `refresh_failures` 2 and no mark; the third marks `refresh_failed` and notifies once.
6. `test_it_takes_the_connection_lock` — `DB::listen` sees `pg_advisory_xact_lock` with the row's key.
7. `test_dry_run_calls_nothing` — counts only.
8. `test_it_is_scheduled_daily`.

**New: `tests/Unit/Support/AdvisoryLockTest.php` — 3 cases**

This file extends `Tests\TestCase` with `RefreshDatabase`, not the bare
PHPUnit case: the lock is a Postgres statement (`CLAUDE.md`'s rule sends
anything touching the container to `tests/Feature`, and this is the exception
the rule's own wording allows — it is pure logic with one dependency, the
database; if the gate's architecture test disagrees, the file moves to
`tests/Feature/Support/` and nothing else changes).

9. `test_it_runs_the_callback_under_the_lock_and_answers_true` — `DB::listen` sees `SET LOCAL lock_timeout` then `pg_advisory_xact_lock` with both hashed arguments; the callback ran; `true`.
10. `test_a_lock_it_cannot_take_answers_false_without_running_the_callback` — a second connection holds the same namespace and key in an open transaction; `run()` with `waitSeconds: 1` answers `false`, the callback never ran, and no exception left the method.
11. `test_another_query_fault_is_not_swallowed` — a callback throwing a `QueryException` whose SQLSTATE is not `55P03` propagates.

**Changed:**

- `database/factories/ConnectionFactory.php` — `expiring()`, a row whose
  `expires_at` is inside `REFRESH_MARGIN_MINUTES`. No test case of its own;
  the cases above use it.

Total: 11 cases, all in new files.

## Acceptance

- [x] `qori:connections:refresh` runs daily, walks every Group without
      `acrossAllGroups()`, refreshes one connection at a time under the lock,
      and skips a provider whose connector does not refresh on a schedule
- [x] A token Google answers `invalid_grant` for marks the row and emails the
      owner once; a transient failure is counted and the third in a row marks
      it and emails once; a second mark on an already-marked row emails nobody
- [x] `fresh()` renews a token inside the margin before the call that needs it,
      and a caller passing a shorter budget than
      `ConnectionService::REQUEST_TIMEOUT_SECONDS` gets the shorter one
      (`D-034`)
- [x] The lock waits at most `AdvisoryLock::WAIT_SECONDS` and then gives up
      without running its callback and without counting a failure, so no
      request queues longer than the call it guards may take (`F08`)
- [x] The Integrations page, which `T-044` built, shows the reconnect state
      this task sets, and Reconnect clears it
- [x] `docs/flows/storage.md`'s Renewal section and
      `docs/tinker/connections.md`'s recipe describe what was built
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

Nothing. `T-044` carried this to a specified state before the split, and the
one finding it still owed — `F08`'s missing acquisition budget — is answered
in Decisions above and specified in Code.

## Re-scope log

None.

## Notes

`T-091` depends on this task as well as on `T-044`, because its
`VendorAccessService` calls `fresh()` before each vendor call and
`markForReconnect($connection, 'unauthorized')` on a vendor 401, and its
container lock is `AdvisoryLock`. Its `App\Listeners\ResumeGrantsAfterReconnect`
listens for `T-044`'s `ConnectionReconnected` and is that task's, not this one's.

The lock's `bool` return is a change from the signature `T-044` and `T-091`
wrote down, `run(string, string, Closure): mixed`. It comes from `F08`: a
bounded wait has an outcome, and a caller that cannot see the outcome has to
guess whether its callback ran. `T-091` is a draft and its citation is updated
with this split.
