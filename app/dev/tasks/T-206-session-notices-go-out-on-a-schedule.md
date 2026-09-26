---
id: T-206
title: Session notices go out on a schedule
stream: classroom
status: draft
owner: unassigned
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
hand. Afterwards the scheduler runs it, and a notice leaves within one
interval, and under a minute more, of falling due.

## Decisions taken to make this specifiable

**A schedule, not a queued job.** Nothing is `ShouldQueue` — the queue is
`deferred` and cannot retry (`CLAUDE.md`, `T-018`) — and the retry state is on
the row (`D-028`), so a sweep is what the ledger was built for. `T-204` showed
Cloud runs a scheduled task every time and wakes a sleeping environment to do
it.

**One run at a time: `withoutOverlapping()` and `onOneServer()`**, as the
command's docblock asks. Both lock through the cache store, and `T-204`'s probe
ran with both for all 27 runs.

**The interval is written once, in `routes/console.php`**, as the two daily
commands' are. Cloud reads the schedule at deploy, so an environment variable
would need a deploy to change it just as a code change does.

**Never more often than the environment's sleep timeout** (`T-128`'s spec).
Each run wakes the environment, which then stays up for the timeout, so a
shorter interval never lets it sleep.

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
  docblock and `docs/flows/live-sessions.md`.

**Out:**

- A queued or delayed job, and a worker (`T-018`).
- Alerting on a heartbeat that stops (`T-019`).
- The card's copy: its lines already promise the email.

## Files

| Path                                                  | Change | Notes                                               |
| ----------------------------------------------------- | ------ | --------------------------------------------------- |
| `routes/console.php`                                  | edit   | The schedule line and its comment                   |
| `app/Console/Commands/NotifySessionsCommand.php`      | edit   | Docblock: what runs it                              |
| `tests/Feature/Console/NotifySessionsCommandTest.php` | edit   | Case 5                                              |
| `docs/flows/live-sessions.md`                         | edit   | "When a recording is published" and "Not built yet" |

## Database

None.

## Code

```php
// routes/console.php, after qori:connections:refresh. Thirty minutes if the
// owner picks the recommendation; the comment gives the reason and T-204's numbers.
Schedule::command('qori:sessions:notify')
    ->everyThirtyMinutes()
    ->withoutOverlapping()
    ->onOneServer();
```

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/Console/NotifySessionsCommandTest.php` — still 5 cases**

- `test_it_is_not_scheduled_until_the_owner_chooses_a_trigger` becomes
  `test_it_is_scheduled_at_the_chosen_interval_one_run_at_a_time`: exactly
  one event names `qori:sessions:notify`; its `expression` is the chosen
  interval's (`*/30 * * * *` for thirty minutes); `withoutOverlapping` and
  `onOneServer` are true.

## Acceptance

- [ ] `php artisan schedule:list` names `qori:sessions:notify` at the chosen
      interval
- [ ] After the deploy, Cloud's logs show the command's heartbeat once an
      interval (the owner's to read)
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **The interval**, the owner's (`decisions.md`, Decisions needed). _Asked_
  26 September 2026 with `T-204`'s numbers: every thirty minutes recommended,
  fifteen if the email should come sooner. What a run costs, to weigh it:
    - **The app.** Each run keeps it up for the sleep timeout, so the sweep
      alone keeps it awake about timeout ÷ interval of the time. The timeout
      is the App cluster's Scale to Zero setting, _asked_ 26 September 2026;
      `T-204`'s runs put it under ten minutes.
    - **The database and the cache.** The command queries every Group, so
      each run also wakes Neon's compute, which stays up for its own suspend
      timeout (five minutes unless changed), and the two locks touch the
      cache. `T-204`'s probe never queried the database, so its runs cannot
      say what that costs. Whether Neon and the cache slept between its runs
      is the owner's to read from the Neon Console and Cloud's cache metrics,
      _asked_ 26 September 2026 and moved here from `T-204`.

## Re-scope log

None.

## Notes

None.
