---
id: T-205
title: Migrations and transactions survive neons pooler
stream: operations
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-205 — Migrations and transactions survive neons pooler

> **A deploy fix.** The deploy of 26 September 2026 failed in its migrations;
> the owner asked for the fix, and for Laravel's own update to be checked.

## Why

The deploy of 26 September 2026 failed in `php artisan migrate --force`, at
the first pending migration, `2026_09_18_000100_create_access_opens`, with
`SQLSTATE[25P02]: current transaction is aborted` on its first foreign key.
Production's `DB_HOST` is Neon's pooler (`…-pooler.c-2.us-east-2.aws.neon.tech`),
which is PgBouncer in transaction mode. Laravel wraps a Postgres migration in
a transaction, and PDO's pgsql driver frees each server-side prepared
statement with a SQL `DEALLOCATE` the pooler cannot match; that fails without
being reported, the transaction aborts, and the next statement meets 25P02.
Laravel ships a fix — a direct endpoint for migrations, and emulated prepares
through the pooler — but applies it itself only to Laravel Cloud's own
Postgres (`pg.laravel.cloud`), in `Illuminate\Foundation\Cloud` and in
`v13.33.0`'s opt-in `DB_POOLING`. Qori's database is Neon's, so neither
applied. The same pooler also stands in front of every multi-statement
transaction a request makes.

## Decisions taken to make this specifiable

**Laravel 13's own pooled/direct support, configured for Neon.** A `direct`
entry on the `pgsql` connection makes Laravel mark it pooled, emulate
prepares through the pooler, and run migrations and schema changes on
`pgsql::direct`. The direct host is `DB_DIRECT_HOST`, else `DB_HOST` without
`-pooler` — Neon's naming, and the rule Laravel's Cloud hook uses for its
own. Locally there is no pooler and no direct entry, so nothing changes.

**`laravel/framework` to `v13.33.0`.** `v13.31.0` keeps Eloquent on the
direct connection during migrations (#61435); before it, a model resolved by
name fell back to the pooled connection, outside the migration's
transaction. Only the framework moved in the lockfile.

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

**In:** `config/database.php`, `composer.lock`, a commented `DB_DIRECT_HOST`
in `.env.example`, and a deploy that runs its migrations.

**Out:** Laravel Cloud's managed Postgres and `DB_POOLING`; Qori's database
stays Neon's.

## Files

| Path                  | Change | Notes                                           |
| --------------------- | ------ | ----------------------------------------------- |
| `config/database.php` | edit   | The direct endpoint on `pgsql`                  |
| `composer.lock`       | edit   | `laravel/framework` `v13.30.1` → `v13.33.0`     |
| `.env.example`        | edit   | `DB_DIRECT_HOST`, commented                     |

Flows: none — the database connection's configuration, which no flow names.

## Database

None: the fix is how migrations reach the database, not what they do.

## Code

The `direct` entry and the two variables above the `return` in `config/database.php`.

## Copy

None.

## Routes

None.

## Tests

None new: nothing in the suite has a pooler. Checked by hand with Neon's
pooled host name set: the connection has a direct endpoint at the host
without `-pooler`, emulates prepares when pooled and not when direct, and the
migrator resolves `pgsql::direct`. The full suite runs on the new framework.

## Acceptance

- [x] The next deploy runs its migrations, and the pending ones apply
- [x] The full suite passes on `laravel/framework` `v13.33.0`
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

None.

## Re-scope log

**2026-09-26 — the pooled host is in `DB_URL`.** The first fix (qori
`70d5f1c`) read the pooled host from `DB_HOST` alone, and the next deploy
failed the same way: the trace showed `v13.33.0`, but the migration still ran
as `pgsql` on the pooler, so no direct endpoint had been configured.
Production gives the connection as a URL, which Laravel parses over the other
keys when it connects, and `DB_HOST` then holds only its default. The pooled
host is now `DB_URL`'s when it is set, else `DB_HOST`'s (qori `d443d79`);
`DB_DIRECT_HOST` still overrides both, and is the lever if a deploy ever
fails this way again.

## Notes

The direct host is derived from `DB_URL` when it is set, else from
`DB_HOST`; see the Re-scope log.
