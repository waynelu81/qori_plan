---
id: T-081
title: Clone to green, one database per checkout, hooks and CI
stream: workflow
status: done
owner: claude
estimate: L
depends: none
blocks: none
---

# T-081 — Clone to green, one database per checkout, hooks and CI

## Why

The review of 14 September 2026 (`streams/workflow.md`): every clone and
worktree on a machine uses the single `qori_testing` database, `RefreshDatabase`
runs `migrate:fresh` per process and `ResetDatabaseCommandTest` resets it in
every teardown, so a developer running the gate beside an agent session drops
each other's tables — two reports this week list "nothing else running
against the test database" as a precondition for green. Pint, Prettier and
the board rules are only found inside the four-minute gate, and planning-only
commits have landed red. `composer setup` migrates before Postgres exists,
the root README is five lines of pre-rename vocabulary, CI runs Postgres 17
while every developer and Neon run 18, and CI has no concurrency, timeout or
cache. `config/qori.php` reads env keys `.env.example` never mentions.

## Decisions taken to make this specifiable

**Parallel tests through Laravel's own `--parallel`** (paratest), with the
`TestCase` guard widened to `/_testing(_test_\d+)?$/` so Laravel's per-process
database names pass and a misnamed database still fails closed.

**A second checkout sets `DB_DATABASE`** — `DB_DATABASE=qori_<name>_testing
php artisan test` — because phpunit's `<env>` does not override a shell
variable and neither does `.env.testing`. `postgres-init.sql` creates
`qori_testing` plus `qori_wt1_testing` to `qori_wt4_testing` so a worktree has
one waiting.

**Hooks the repo installs, no new tool**: `.githooks/pre-commit` and
`.githooks/pre-push`, activated by `git config core.hooksPath .githooks` from
`composer setup`. Pre-commit runs `vendor/bin/pint --dirty --test`, Prettier
and ESLint on the staged files, and `php artisan qori:tasks --check` when
anything under `docs/planning` is staged. Pre-push runs `vendor/bin/pint
--test`, `vendor/bin/phpstan analyse`, and `php artisan test --parallel
--exclude-group slow`; `QORI_SKIP_PUSH_TESTS=1` skips the tests for an
emergency push and the hook says so.

**CI tests what developers run**: `postgres:18`, `concurrency` with
cancel-in-progress per ref, `timeout-minutes: 15`, composer and npm caches.
The PHPStan result cache is cleared inside `types:check` so a local pass is
the same pass CI sees; the paragraph in `CLAUDE.md` that warns about it is
deleted by `T-082`.

## Preconditions

Docker with the Postgres container, as today. `T-080`, `T-082` and `T-083`
run alongside and do not touch this task's files; `T-082` deletes the PHPStan
trap paragraph from `CLAUDE.md` in step with the `types:check` change here.

## Scope

**In:**

- `brianium/paratest` as a dev dependency; `composer test:parallel`; the
  `TestCase` guard regex; `#[Group('slow')]` on `ResetDatabaseCommandTest`
  and `DesignReviewFixtureTest`, and the unconditional teardown reset in
  `ResetDatabaseCommandTest` dropped for cases that already end in `clear`.
- `composer setup` runs `docker compose up -d --wait` first, creates the
  testing databases idempotently, runs `wayfinder:generate --with-form`
  before `npm run build`, and installs the hooks path. `ci:check` clears the
  PHPStan cache and runs pint and `qori:tasks --check` before `vue-tsc`.
- `.githooks/pre-commit`, `.githooks/pre-push`, documented in `README.md`.
- `.env.example`: `SERVER_PORT=8001`, the duplicate `DB_DATABASE` line
  removed, every `env('QORI_*')` key that `config/` reads present with a
  comment; `tests/Feature/EnvExampleTest.php` asserts that stays true.
- `composer.json` `php: ^8.5`; `.nvmrc` and `engines.node` for Node 22.
- `.github/workflows/tests.yml`: `postgres:18`, `concurrency`,
  `timeout-minutes`, caches; the job-summary step stays.
- `phpstan.neon` analyses `lang/`, and any duplicate key it finds is fixed.
- `README.md` rewritten under 60 lines as the one entry point: what Qori is
  in current nouns, the fresh-clone recipe, the ports (8001, 8025, 5433), the
  second-checkout database line, the hooks, and an ordered reading list
  (`CLAUDE.md`, `docs/planning/PROCESS.md`, your stream, your task, the flow
  file).

**Out:**

- A branch or pull-request policy.
- Any file owned by `T-080`, `T-082` or `T-083`; in particular `CLAUDE.md`
  (`T-082` removes the trap paragraph) and `docs/planning/engineering-runbook.md`
  (`T-080`).

## Files

| Path                                                 | Change | Notes                                 |
| ---------------------------------------------------- | ------ | ------------------------------------- |
| `composer.json`                                      | edit   | paratest, scripts, php ^8.5           |
| `composer.lock`                                      | edit   |                                       |
| `package.json`                                       | edit   | engines.node                          |
| `package-lock.json`                                  | edit   | if npm rewrites it                    |
| `.nvmrc`                                             | new    | 22                                    |
| `.githooks/pre-commit`                               | new    |                                       |
| `.githooks/pre-push`                                 | new    |                                       |
| `.github/workflows/tests.yml`                        | edit   |                                       |
| `tests/TestCase.php`                                 | edit   | Guard regex                           |
| `phpunit.xml`                                        | edit   | Only if parallel needs it             |
| `phpstan.neon`                                       | edit   | `lang/` path                          |
| `.env.example`                                       | edit   |                                       |
| `docker/postgres-init.sql`                           | edit   | Worktree databases                    |
| `compose.yaml`                                       | edit   | Only if the init needs it             |
| `README.md`                                          | edit   | Rewritten                             |
| `tests/Feature/EnvExampleTest.php`                   | new    |                                       |
| `tests/Feature/Console/ResetDatabaseCommandTest.php` | edit   | slow group, teardown                  |
| `tests/Feature/DesignReviewFixtureTest.php`          | edit   | slow group                            |
| `lang/en/errors.php`                                 | edit   | Only if PHPStan finds a duplicate key |

### Added during execution

| Path                                               | Change | Notes                                                                          |
| -------------------------------------------------- | ------ | ------------------------------------------------------------------------------ |
| `app/Console/Commands/TestingDatabasesCommand.php` | new    | `qori:testing-databases`, the idempotent creation the Code section anticipates |

## Database

None in the application. Test databases `qori_wt1_testing` … `qori_wt4_testing`
created by the init script; Laravel's `--parallel` creates `qori_testing_test_N`
itself.

## Code

```php
// tests/TestCase.php
if (! preg_match('/_testing(_test_\d+)?$/', $database)) { throw new RuntimeException(...); }
```

```json
// composer.json scripts (shape)
"setup": ["docker compose up -d --wait", "composer install", "@php -r \"file_exists('.env') || copy('.env.example', '.env');\"", "@php artisan key:generate", "@php artisan qori:testing-databases", "@php artisan migrate --force", "npm install", "@php artisan wayfinder:generate --with-form", "npm run build", "git config core.hooksPath .githooks"],
"test:parallel": ["@php artisan test --parallel --recreate-databases"],
"types:check": ["phpstan clear-result-cache", "phpstan analyse"],
"ci:check": ["Composer\\Config::disableProcessTimeout", "@lint:check", "@php artisan qori:tasks --check", "npm run check", "npm run types:check", "@types:check", "@php artisan test"]
```

If creating the databases idempotently needs a command, add
`app/Console/Commands/TestingDatabasesCommand.php` (`qori:testing-databases`:
`CREATE DATABASE … ` for each name if missing, connecting to the `qori`
database) and list it in the report.

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/EnvExampleTest.php` — 2 cases**

1. `test_every_qori_env_key_read_by_config_is_in_the_example` — walk
   `config/*.php` for `env('QORI_…')`, assert each key appears in
   `.env.example`.
2. `test_the_example_has_no_duplicate_keys`.

**Changed:** `ResetDatabaseCommandTest`, `DesignReviewFixtureTest` gain the
slow group; the suite passes under `php artisan test --parallel` and under
`DB_DATABASE=qori_wt1_testing php artisan test`.

## Acceptance

- [x] `composer setup` on a clone with Docker running ends green with no manual step
- [x] `php artisan test --parallel` passes; `DB_DATABASE=qori_wt1_testing php artisan test` passes
- [x] A commit with a Prettier or pint violation is refused by the hook; a push runs phpstan and the fast tests
- [x] CI file has postgres:18, concurrency, timeout and caches
- [x] `EnvExampleTest` passes and `.env.example` names every `QORI_*` key
- [x] `npm run check:fix` run; `composer ci:check` green from a clean tree
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

The gate for this task runs in a worktree with its own database name; that
is the case this task exists for, so say in the report which name it used.
