---
id: T-206
title: Session notices go out on a schedule
stream: classroom
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-206 — Session notices go out on a schedule

## Why

`T-128` built `qori:sessions:notify`, and nothing runs it: on 26 September
2026 the owner held its trigger until Laravel Cloud's scheduler had been seen
on Qori's environment. `T-204` saw it — 27 runs of 27, ten minutes apart, each
5 to 52 seconds after its minute, the environment woken from sleep for most of
them — and its probe is gone. Until this lands, a Peer's card promises an
email that does not go (`live.state.waiting`, `live.state.overdue.resolution`),
and every queued notice waits in the ledger for someone to run the command by
hand. Afterwards the scheduler runs it every thirty minutes, and a notice
leaves within thirty minutes, and under a minute more, of falling due.

## Decisions taken to make this specifiable

**Every thirty minutes**, the owner's choice on 27 September 2026, from
`T-204`'s numbers. Each run wakes the environment, and the command's queries
wake Neon's compute; the owner chose without the sleep timeout or the
database's suspend readings, which were offered as the cost to weigh.

**A schedule, not a queued job.** Nothing is `ShouldQueue` — the queue is
`deferred` and cannot retry (`CLAUDE.md`, `T-018`) — and the retry state is on
the row (`D-028`), so a sweep is what the ledger was built for. `T-204` showed
Cloud runs a scheduled task every time and wakes a sleeping environment to do
it.

**One run at a time: `withoutOverlapping(15)` and `onOneServer()`**, as the
command's docblock asks. Both lock through the cache store, and `T-204`'s probe
ran with both for all 27 runs. The overlap lock's fifteen minutes are this
task's own, not Laravel's default of a day. Laravel gives the lock back when a
run ends, and when a run is stopped by a signal it catches (SIGTERM, SIGINT or
SIGQUIT, with `pcntl` loaded). A run killed outright keeps the lock until it
expires, and at a day that is a day with no emails and nothing watching the
heartbeat yet (`T-019`). Fifteen minutes is over before the next run is due,
so a killed run costs nothing past itself. A run still going when the next one
starts meets the claim's row lock, which `T-128` built for two runs at once.
`onOneServer()`'s own lock is keyed by the minute and never outlives it.

**The interval is written once, in `routes/console.php`**, as the two daily
commands' are. Cloud reads the schedule at deploy, so an environment variable
would need a deploy to change it just as a code change does.

**Never more often than the environment's sleep timeout** (`T-128`'s spec).
Each run wakes the environment, which then stays up for the timeout, so a
shorter interval never lets it sleep. `T-204`'s runs put the timeout under ten
minutes, so thirty leaves it room.

## Preconditions

None.

**Data this task verifies against:** a clean database.

**Equipment:** none for the gate. The production line in Acceptance needs
Cloud's logs, which are the owner's to read.

## Scope

**In:**

- The schedule line for `qori:sessions:notify` in `routes/console.php`, with
  its reason.
- `NotifySessionsCommandTest`'s case asserting the command is not scheduled,
  rewritten to assert the interval and one run at a time.
- Saying so where the code and the docs say nothing runs it: the command's
  docblock, `docs/flows/live-sessions.md` and `docs/tinker/live-sessions.md`.

**Out:**

- A queued or delayed job, and a worker (`T-018`).
- Alerting on a heartbeat that stops (`T-019`).
- The card's copy: its lines already promise the email.
- `onOneServer()` on the two daily commands. It changes nothing until a second
  replica, which is stream `operations`' (`routes/console.php`).

## Files

| Path                                                  | Change | Notes                                                                                            |
| ----------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------ |
| `routes/console.php`                                  | edit   | The schedule line and its comment; the purge comment's "until something here uses onOneServer()" |
| `app/Console/Commands/NotifySessionsCommand.php`      | edit   | Docblock: what runs it                                                                           |
| `tests/Feature/Console/NotifySessionsCommandTest.php` | edit   | Case 5                                                                                           |
| `docs/flows/live-sessions.md`                         | edit   | The opening, "When a recording is published", the command's diagram, Stale, and "Not built yet"  |
| `docs/tinker/live-sessions.md`                        | edit   | "Publish a recording and send the email": what runs the command                                  |

## Database

None.

## Code

```php
// routes/console.php, after qori:connections:refresh, with a comment giving
// the owner's choice, T-204's numbers and the lock's fifteen minutes.
Schedule::command('qori:sessions:notify')
    ->everyThirtyMinutes()
    ->withoutOverlapping(15)
    ->onOneServer();
```

`everyThirtyMinutes()` is `*/30 * * * *`: on the hour and the half hour.

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/Console/NotifySessionsCommandTest.php` — still 5 cases**

- `test_it_is_not_scheduled_until_the_owner_chooses_a_trigger` becomes
  `test_it_is_scheduled_every_thirty_minutes_one_run_at_a_time`: exactly one
  event names `qori:sessions:notify`; its `expression` is `*/30 * * * *`;
  `withoutOverlapping` is true with `expiresAt` 15; `onOneServer` is true.

## Acceptance

- [x] `php artisan schedule:list` names `qori:sessions:notify` every thirty
      minutes
- [x] Pushed to `main`, which deploys the schedule to Cloud; that Cloud's logs
      show the heartbeat once every thirty minutes is the owner's to read,
      _asked_ 27 September 2026
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~**The interval**, the owner's (`decisions.md`, Decisions needed). _Asked_
  26 September 2026 with `T-204`'s numbers: every thirty minutes recommended,
  fifteen if the email should come sooner. What a run costs, to weigh it:~~
    - ~~**The app.** Each run keeps it up for the sleep timeout, so the sweep
      alone keeps it awake about timeout ÷ interval of the time. The timeout
      is the App cluster's Scale to Zero setting, _asked_ 26 September 2026;
      `T-204`'s runs put it under ten minutes.~~
    - ~~**The database and the cache.** The command queries every Group, so
      each run also wakes Neon's compute, which stays up for its own suspend
      timeout (five minutes unless changed), and the two locks touch the
      cache. `T-204`'s probe never queried the database, so its runs cannot
      say what that costs. Whether Neon and the cache slept between its runs
      is the owner's to read from the Neon Console and Cloud's cache metrics,
      _asked_ 26 September 2026 and moved here from `T-204`.~~

  **Answered 27 September 2026: every thirty minutes.** The owner chose
  without the two readings, which were asked as the cost to weigh and are not
  needed to build or test this.

## Added during execution

- `config/qori.php`: the comment on `creator_nudge_hours` still said
  "Provisional", and `T-129` decided twelve.

## Re-scope log

- **27 September 2026, Acceptance.** The second box read "After the deploy,
  Cloud's logs show the command's heartbeat once an interval (the owner's to
  read)", which no builder could tick. It now says what the build did, the
  push that deploys the schedule. The reading is asked of the owner and listed
  under Could not verify in the report.
- **27 September 2026, Scope.** Out said alerting on a heartbeat that stops is
  `T-019`'s. `T-019` lists five failure modes, and that is not one of them. A
  line asking whether it joins them is added under `T-019`'s "Before this can
  be ready".

## Notes

**27 September 2026: the owner read the runs in Cloud's logs.**
`qori:sessions:notify` logged its heartbeat at 01:00:13, 01:30:27 and 02:00:07
UTC — every thirty minutes, 7 to 27 seconds after the minute — each
`{"due": 0, "nudges_queued": 0, "sent": 0, "dry_run": false}`, after deploy 36
at 00:50 UTC. The second Acceptance box's reading is done.
