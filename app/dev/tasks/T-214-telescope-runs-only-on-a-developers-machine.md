---
id: T-214
title: Telescope runs only on a developer's machine
stream: workflow
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-214 — Telescope runs only on a developer's machine

> **Written on 8 October 2026** from the independent review of 6 October
> (`app/dev/reviews/2026-10-06-independent-review.md` §4), on the owner's word
> the same day: "So installed telescope Qori first?" Brought to ready from the
> code and claimed in one step.

## Why

On 5 October `laravel/telescope` and `barryvdh/laravel-ide-helper` were
installed in the main checkout and left uncommitted, with no task behind them.
The install works locally and production can never load Telescope (it is
`require-dev`, kept out of package discovery, and registered only in `local`).
But its published migration sits in `database/migrations/`, so the first push
that carries it would have the deploy's `migrate --force` create three Telescope
tables on Neon. Its storage connection also defaults to `mysql`. And locally it
records OAuth token exchanges, sign-in codes and 2FA codes in plain text, while
the `connections` table encrypts those same tokens.

Afterwards Telescope is a local debugging aid that nothing else can see: its
migration only exists where it runs, the secrets it would record are masked, and
`qori/CLAUDE.md` says what it is and where it may run.

## Decisions taken to make this specifiable

Brought to ready on 8 October 2026, from the code.

**The migration moves to `database/migrations/local/` and only
`TelescopeServiceProvider` loads it.** That keeps the deploy, the tests'
`RefreshDatabase` and any pending-migration check from ever seeing it. A
`shouldRun()` guard would also work here, because Qori's `/up` is Laravel's
default, but MyFareWatch tried that first and dropped it, and the folder makes
the rule visible in the tree. The filename stays the same, so the dev database's
existing row still matches it.

**Secrets are hidden in every environment, local included.** The stub returns
early in `local`, which is the only place Telescope runs, so as published it
hides nothing that matters. Hidden request fields: `_token`, `code`,
`code_verifier`, `client_secret`, `refresh_token`, `access_token`, `token`,
`recovery_code` and `current_password` (Telescope already hides `password` and
`password_confirmation`). Hidden response fields: `access_token`,
`refresh_token` and `id_token`. Hidden headers: `cookie`, `x-csrf-token`,
`x-xsrf-token` and `stripe-signature` (Telescope already hides `authorization`).
These names come from what `app/Integrations` sends and what the sign-in, code
and 2FA forms post. Hiding `code` also masks a coupon code locally, which costs
nothing.

**The storage connection defaults to `pgsql`, as `config/database.php` does.**
It only matters locally now, but a `mysql` default in a Postgres app is a trap.

**`wayfinder:generate` is ignored.** One run recorded about 4,658 view entries
on 6 October, and the Vite plugin runs it on every route change.

**The path stays `/telescope`.** Qori's URL rules keep the root level for `/`,
`/dashboard` and well-known URIs. Telescope is registered only in `local` and
answers nowhere else, so the exception is recorded in `qori/CLAUDE.md` rather
than spent on a config override.

**Nothing schedules `telescope:prune`.** The scheduler runs in production,
where Telescope is not installed. `qori/CLAUDE.md` names `telescope:clear` and
`telescope:prune` for whoever wants a smaller table.

**`laravel-ide-helper` ships in the same commit.** It came in with Telescope,
and its generated files are already ignored. It needs no code.

**This borrows MyFareWatch's pattern (its webapp `576cf44`) and nothing
else.** The two products share no code, infrastructure or deployment.

## Preconditions

None.

**Data this task verifies against:** the dev `qori` database's `migrations`
row `2026_10_05_103738_create_telescope_entries_table` (batch 16), which must
still read Ran after the move.

**Equipment:** None.

## Scope

**In:**

- The install as it stands (the composer files, `.gitignore`, the providers,
  `config/telescope.php`), with the migration moved and the changes above.
- One line in `qori/CLAUDE.md`.

**Out:**

- Telescope anywhere but `local`, and any gate for it.
- Watchers beyond the changes above.

## Files

| Path                                                                             | Change | Notes                                         |
| -------------------------------------------------------------------------------- | ------ | --------------------------------------------- |
| `composer.json`                                                                  | edit   | the two dev dependencies, `dont-discover`     |
| `composer.lock`                                                                  | edit   | as Composer wrote it on 5 October             |
| `.gitignore`                                                                     | edit   | ide-helper's files and `coverage.xml`         |
| `app/Providers/AppServiceProvider.php`                                           | edit   | registers Telescope in `local` alone          |
| `app/Providers/TelescopeServiceProvider.php`                                     | new    | loads `migrations/local`; hides secrets       |
| `config/telescope.php`                                                           | new    | `pgsql` default; `wayfinder:generate` ignored |
| `database/migrations/local/2026_10_05_103738_create_telescope_entries_table.php` | new    | moved from `database/migrations/`             |
| `CLAUDE.md`                                                                      | edit   | one line under Where code lives               |

Flows: none — no call chain a person reaches changes.

## Database

None in any shared environment. Locally the three Telescope tables already
exist, and the migration's row still matches.

## Code

`TelescopeServiceProvider::register()` calls
`$this->loadMigrationsFrom(database_path('migrations/local'))`, and
`hideSensitiveRequestDetails()` hides the fields above with no environment
check.

## Copy

None.

## Routes

None that a creator or Peer reaches. Telescope's own routes exist only in
`local`.

## Tests

None new. `phpunit.xml` pins `TELESCOPE_ENABLED=false` and the tests run in
`testing`, where Telescope is never registered. The proof is the gate, plus
`php artisan migrate:status` still reading the Telescope row as Ran locally, and
`php artisan migrate:status --env=testing` not listing it.

## Acceptance

- [x] The migration is in `database/migrations/local/` and only `TelescopeServiceProvider` loads it
- [x] Locally `migrate:status` reads its row as Ran; under `testing` it is not listed
- [x] OAuth token fields, sign-in and 2FA codes are masked in every environment
- [x] The storage connection defaults to `pgsql`, and `wayfinder:generate` is ignored
- [x] `qori/CLAUDE.md` says what Telescope is and where it runs
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Where does the migration live?~~ **Answered from the code, 8 October 2026:**
  `database/migrations/local/` (Decisions).
- ~~Which fields are secret?~~ **Answered 8 October 2026** from
  `app/Integrations` and the forms (Decisions).
- ~~Should the path move off the root level?~~ **Answered 8 October 2026:** no;
  the exception is recorded (Decisions).

## Re-scope log

None.

## Notes

The dev database's `telescope_entries` holds rows from the 6 October review
session, along with token exchanges recorded before this task masked them.
`php artisan telescope:clear` empties it.
