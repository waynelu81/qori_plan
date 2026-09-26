---
id: T-204
title: Spike laravel cloud wakes a sleeping environment for a scheduled task
stream: operations
status: doing
owner: claude
estimate: S
depends: none
blocks: none
---

# T-204 — Spike laravel cloud wakes a sleeping environment for a scheduled task

> **Spike, and throwaway.** The owner asked on 26 September 2026 for code
> to test Laravel Cloud's scheduler before anything triggers
> `qori:sessions:notify` (`T-128`). Everything it adds is removed once the
> test has answered.

## Why

`T-128` built the session-notice sweep and the owner left its trigger out
until Laravel Cloud's behaviour is known. Cloud's guide
(<https://laravel.com/cloud/docs/scheduled-tasks>) says a scaled-to-zero
environment is woken for each scheduled task, from the `schedule:list` it
captures at deploy; that a woken environment stays up for the sleep timeout,
so a task more frequent than the timeout keeps it awake; and that
`withoutOverlapping()` and `onOneServer()` read the cache store on every run
and "may keep an attached database or cache awake". Nobody has seen any of
it on Qori's environment. This spike deploys a probe that records every run,
reads it back, and answers when a scheduled sweep would run, how late, and
whether the environment slept between runs.

## Decisions taken to make this specifiable

**The probe is a scheduled command that records a heartbeat, and a public
JSON page that reads them back.** `qori:cloud:probe` writes the time it ran,
the minute it was due, the lag, the container's age from `/proc` (a small age
after a quiet spell is a wake) and a hashed host; `GET /up/scheduler` returns
the runs, newest first. A page, because whoever checks after the deploy has
no access to Cloud's logs; the runs are logged too, for the dashboard.

**The cache holds the runs, not a table.** A migration may not run on deploy
(the deploy command was commented out on 22 September, and whether it still
is has to be asked), and the cache is Valkey in production.

**Every ten minutes by default, as the sweep would be scheduled.**
`QORI_CLOUD_PROBE_CRON` changes it, from the next deploy, and an empty value
schedules nothing. `withoutOverlapping()` and `onOneServer()` are on, because
`T-128`'s sweep would use both and Cloud warns about exactly them.

## Preconditions

> Anything that must be true of the machine before this task can be done or
> verified — a running container, a generated directory, credentials, seeded
> data. **None** if it runs from a clean checkout.
>
> Worth its own section because a check that silently reads an empty directory
> reports success. `resources/js/routes` is generated and gitignored, so
> anything analysing it needs `php artisan wayfinder:generate --with-form`
> first, and finds nothing at all without it.

**Data this task verifies against:** > The rows the check needs — a seeded
world, a Group in a particular state, a realistic row count — and how to get
them (`php artisan qori:reset …`, a factory, a fixture). **A clean database**
when nothing more is needed.

**Equipment:** > A visible browser, vendor credentials, a mailbox, a phone —
whatever a check needs that a shell does not have. **None** when everything
can be verified from the terminal.

> **Spike, for vendor-facing work.** A spec that names a vendor payload cites
> where the shape came from: an observed response (the date and the call), or
> a committed fixture under `tests/Fixtures/<vendor>/`. Guessing the field
> names from documentation is how `contact_email` became `peer_email` and
> how a v2 requirements summary read "nothing outstanding" for an account
> that had not started. If nobody has seen the response, the first step is a
> spike that does, and its result is a fixture, not a memory.

## Scope

**In:**

- `app/Console/Commands/CloudProbeCommand.php`, `app/Http/Controllers/CloudProbeController.php`,
  the schedule block in `routes/console.php`, the route in `routes/web.php`,
  `qori.cloud_probe` and a reachability allow-list entry in `config/qori.php`,
  `tests/Feature/Console/CloudProbeTest.php`.
- Reading the runs back after the deploy and writing down what they show.

**Out:**

- Choosing `T-128`'s trigger: the owner's, from this spike's answer.
- Laravel Cloud's queue workers and a delayed dispatch: Qori has no worker,
  and nothing is `ShouldQueue` (`CLAUDE.md`).

## Files

| Path                                            | Change | Notes                                        |
| ----------------------------------------------- | ------ | -------------------------------------------- |
| `app/Console/Commands/CloudProbeCommand.php`    | new    | Throwaway; `qori:cloud:probe`                |
| `app/Http/Controllers/CloudProbeController.php` | new    | Throwaway; `GET /up/scheduler`               |
| `routes/console.php`                            | edit   | Throwaway schedule block                     |
| `routes/web.php`                                | edit   | Throwaway route, root level against the rule |
| `config/qori.php`                               | edit   | `cloud_probe`; `probe.scheduler` allow-listed |
| `tests/Feature/Console/CloudProbeTest.php`      | new    | 3 cases                                      |

Flows: none — a throwaway probe, removed with its answer, describes no flow.

## Database

None.

## Code

See the files: every one is throwaway, and its docblock says so.

## Copy

None: the page is JSON for a developer, and the console line is a diagnostic.

## Routes

| Verb | Path            | Name              | Action                 |
| ---- | --------------- | ----------------- | ---------------------- |
| GET  | `/up/scheduler` | `probe.scheduler` | `CloudProbeController` |

## Tests

**New: `tests/Feature/Console/CloudProbeTest.php` — 3 cases**

1. `test_a_run_records_a_heartbeat_in_the_cache`
2. `test_the_page_reads_the_runs_back_newest_first_and_keeps_only_the_last_few`
3. `test_it_is_scheduled_on_the_configured_cron_one_run_at_a_time`

## Acceptance

- [x] The probe is deployed with the Scheduler toggle on, and
      `/up/scheduler` shows runs scheduled ten minutes apart
- [ ] The report says, from the runs: the lag against the due minute; whether
      the environment slept between runs (the container's age); and whether
      the database or the cache stayed awake, from the Cloud dashboard
- [ ] The owner has what they need to choose `T-128`'s trigger, and the probe
      is removed
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- The Cloud environment's sleep timeout — the owner's, to read off the App
  cluster's Scale to Zero setting. _Asked_ 26 September 2026. The runs imply
  it is under ten minutes (Notes).
- Whether the database (Neon's compute) and the cache (Laravel Valkey) slept
  between runs — the owner's, from the Neon Console and Cloud's cache
  metrics. _Asked_ 26 September 2026.
- ~~Whether the deploy command runs migrations now.~~ **Answered 26 September
  2026:** it does, once `T-205` pointed migrations at Neon's direct
  endpoint.

## Added during execution

- `.env.example` — `QORI_CLOUD_PROBE_CRON`, which `EnvExampleTest` requires of
  every `QORI_` key the config reads; the probe's first commit left it out,
  and `T-128`'s gate caught it (qori `51f9b38`).

## Re-scope log

> Empty until something in the spec turns out to be wrong. Then: what was
> expected, what was found, and what it means for the spec. Rewrite the
> sections it changes and carry on — or, if you are handing the task back,
> set `status: rescope` so the next person rewrites it.

None.

## Notes

**What the probe showed, 26 September 2026** (one read of `/up/scheduler` at
12:47 UTC, after the deploy of 09:39):

- **Every run happened.** 19 runs, one for each ten-minute mark from 09:40 to
  12:40, 9.3 to 10.7 minutes apart; none missed, none doubled.
- **The environment sleeps between runs.** 14 of the 19 found a container
  1.3 to 1.6 seconds old: Cloud had started it for that run. Four found one
  already up — 597, 141, 226 and 94 seconds — which is something else, most
  likely an inbound request, waking it first; the first run found the
  deploy's own container, 77 seconds old. So the sleep timeout is shorter than
  the ten-minute interval, and a woken environment then waits out that
  timeout before sleeping again.
- **A run starts 10 to 52 seconds after its minute**, 30 on average: Cloud
  wakes the environment somewhere in the due minute, and the command runs
  about a second and a half after the container starts.
- **The hashed host never changes** (`ff43e101`): containers share a
  hostname, so the container's age, not the host, is what tells one start
  from another.
- **For `T-128`'s trigger:** a schedule on Cloud is reliable and punctual
  enough for a recording email — nineteen of nineteen, under a minute late.
  Its cost is the wake: each run keeps the environment up for the sleep
  timeout, so the share of time awake is about the timeout over the
  interval, and an interval at or under the timeout never sleeps at all.

The probe's page is public: it holds times and a hashed host, nothing
personal. Every read of it wakes a sleeping environment for the sleep
timeout, which then shows in the next run's container age, so it is read
sparingly and each read noted.
