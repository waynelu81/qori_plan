---
id: T-119
title: The core loop runs in a browser on demand
stream: workflow
status: done
owner: claude
estimate: M
depends: none
blocks: T-120
---

# T-119 — The core loop runs in a browser on demand

## Why

The beta gate's first line is that the creator and Peer core loop passes in a
clean browser session at mobile and desktop widths, and today the only way to
know is for a person to click through it. `walkthroughs.md` records four such
walks; each cost an afternoon and each was stale by the next commit. The
pieces to automate it are already in the repository — Playwright drives
`qori:design-review`, Mailpit holds every message the app sends and
`App\Support\Mailpit` reads it back — but nothing joins them into a run.

Afterwards one command, `php artisan qori:e2e`, rebuilds a database of the
developer's choosing, serves the app from it on its own port, and drives a
headless Chromium through registering, confirming the address from the real
verification email, the three parts of setup, creating a Series, adding an
Episode and making the Series ready to share. `--headed` shows the browser
while it does so. A failed step leaves a trace and a screenshot to open.

## Decisions taken to make this specifiable

**Playwright, with `@playwright/test` as the runner.** The `playwright`
library is already a dev dependency and its Chromium is installed for
`qori:design-review`; Laravel Dusk would add ChromeDriver and a second
browser stack for nothing. The library alone has no test runner, so the
matching `@playwright/test` (pinned to the same `1.63.0`) is added: it gives
steps, auto-waiting assertions, traces on failure and a list reporter,
which a manifest-driven script would have to reinvent.

**An artisan command is the trigger, and it starts its own server.**
`qori:design-review` asks for a running app and photographs whatever database
that app is on. A journey that registers and rebuilds cannot borrow the
developer's server, because the server decides the database. So `qori:e2e`
runs PHP's built-in server itself (`php -S`, the same `server.php` that
`artisan serve` uses) with the run's environment in the process environment:
`DB_DATABASE` set to the chosen database, `APP_URL` set to the run's own
origin so signed verification links validate, `MAIL_MAILER=smtp` so the
message reaches Mailpit, and `QORI_STORAGE_DISK=local` so nothing a run
uploads reaches the real bucket. Real environment variables win over `.env`
(Laravel's repository is immutable), which is the same mechanism
`DB_DATABASE=qori_wt1_testing php artisan test` relies on. `artisan serve` is
not used because it strips every variable not on its pass-through list.

**The database is an option, with a guard rather than a list.**
`--database=` names it, defaulting to `config('qori.e2e.database')`
(`qori_e2e`). The name must end in `_e2e` or `_testing` — so `qori_testing`,
the main test database, is allowed, as the owner asked — and the host must be
loopback, the same rule `qori:testing-databases` applies. The run creates the
database when it is missing and runs `migrate:fresh` plus `PricingSeeder` on
it every time, because a from-scratch registration is the point. `qori`, the
development database, fails the suffix rule and can never be rebuilt by this.

**Watching is a flag, and slowing down is another.** `--headed` passes
Playwright's own `--headed`; `--slow=<ms>` sets `slowMo` on the launch so a
person can follow what the run does. Both default off, so the command is
headless and full speed when nobody is looking.

**One journey file, one browser project per width.** The journey is a single
`test()` with a `test.step()` per stage, because every stage depends on the
one before it and a step's name is what the reporter prints. Playwright
projects `desktop` (1440×900) and `mobile` (390×844) run the same file;
`--viewport=desktop|mobile|both` chooses, defaulting to `desktop` so a headed
run shows one browser.

**Selectors are structural, not textual.** Ids and form actions
(`#group-name-input`, `form[action$="/setup/skip/payments"]`, `#publish`),
never button labels. The labels carry the Group's vocabulary (`Create Series`
is `Create {{ noun('series') }}`) and §13's i18n will move them; an id
survives both. The one text assertion is `Ready to share`, which is
`SeriesStatus::Published->label()` rendered by the server.

**The verification link is read from the message, not minted.**
`docs/tinker/auth.md` shows how to mint the signed URL without the email; a
run that did that would not know whether the email went. The spec polls
Mailpit's message list for one addressed to the run's person, takes the
first `href` containing `/auth/verify-email/` from its HTML body and follows
it. The response shape is the one `App\Support\Mailpit` already documents
(observed against v1.31.1: `{messages: [{ID, Subject, To}]}`, and a message
adds `HTML` and `Text`).

**Every run uses a fresh address.** `e2e+<timestamp>-<project>@example.test`,
so the mobile and desktop projects never share a person and a run against a
database that was not rebuilt still registers cleanly.

**A stale `public/hot` is refused, not trusted.** Laravel's Vite helper reads
`public/hot` and points every asset at the address inside it; a dev server
that stopped leaves the file behind and every page renders blank. The command
reads the file and asks that origin for `/@vite/client` before it starts; with
no `hot` file it requires `public/build/manifest.json`. Either failure names
the fix.

**Results go under `storage/app/e2e`**, which `storage/app/.gitignore`
already ignores. A trace and a screenshot are kept only for a failed test.

**No `.env.example` change.** The two numbers the command needs — the default
database and the port — sit in `config/qori.php` as literals, not `env()`
reads, because nothing but this command reads them and a developer overrides
them with the command's own options.

## Preconditions

**Data this task verifies against:** an empty database the command creates
itself. The PHPUnit cases need only `qori_testing`.

**Equipment:** Docker with `postgres` and `mailpit` from `compose.yaml` up
(`docker compose up -d`), Playwright's Chromium (`npx playwright install
chromium`), and either `npm run dev` running or `npm run build` done. A screen,
for `--headed`.

## Scope

**In:**

- `qori:e2e` with `--database=`, `--headed`, `--slow=`, `--viewport=`,
  `--only=` and `--port=`, refusing outside a local environment, a database
  name without the suffix, a non-loopback host, a cached configuration, an
  unreachable Mailpit, and missing or stale front-end assets.
- The Playwright configuration, two support modules (Mailpit, the person) and
  one journey: register → verify from the email → name the Group → skip
  payments → finish storage → create a Series → add a Vimeo Episode → make it
  ready to share.
- Four PHPUnit cases on the command's refusals.
- `docs/tinker/e2e.md` and its row in `docs/tinker/README.md`; the task's line
  in `streams/workflow.md`.

**Out:**

- The Peer half of the loop — granting access, the Peer opening an Episode,
  progress, the certificate. That is the next journey, once this one runs.
- Running the journey in CI, or from `composer ci:check`. It needs Docker, a
  browser and a built front end; the gate stays four minutes.
- A File Episode, which uploads. `QORI_STORAGE_DISK=local` makes it safe, and
  the journey adds a Vimeo reference instead because the upload flow is
  `docs/tinker/uploads.md`'s own job.
- A Peer, a password sign-in, a magic link or the staff console.
- Recording video of the run.

## Files

| Path                                            | Change | Notes                                                                      |
| ----------------------------------------------- | ------ | -------------------------------------------------------------------------- |
| `app/Console/Commands/EndToEndCommand.php`      | new    | `qori:e2e`                                                                 |
| `config/qori.php`                               | edit   | `e2e.database`, `e2e.port`                                                 |
| `tests/e2e/playwright.config.ts`                | new    | Reads `E2E_*` from the environment                                         |
| `tests/e2e/tsconfig.json`                       | new    | Node types for the e2e files only; the root `tsconfig.json` stays as it is |
| `tests/e2e/support/mailpit.ts`                  | new    | Wait for a message, pull a link out of it                                  |
| `tests/e2e/support/person.ts`                   | new    | A fresh name, address and password per run                                 |
| `tests/e2e/core-loop.spec.ts`                   | new    | The journey                                                                |
| `tests/Feature/Console/EndToEndCommandTest.php` | new    | 4 cases                                                                    |
| `package.json`, `package-lock.json`             | edit   | `@playwright/test@1.63.0` in `devDependencies`                             |
| `docs/tinker/e2e.md`                            | new    | The recipe                                                                 |
| `docs/tinker/README.md`                         | edit   | The table row                                                              |
| `docs/planning/streams/workflow.md`             | edit   | Task 5 in the list                                                         |

Flows: none — the run drives the registration, verification, setup and Series
flows as they are and rewires none of them.

## Database

None. The command creates a database and migrates it; no schema changes.

## Code

```php
namespace App\Console\Commands;

class EndToEndCommand extends Command
{
    protected $signature = 'qori:e2e
                            {--database= : The database the run rebuilds and serves from; must end in _e2e or _testing}
                            {--headed : Show the browser}
                            {--slow=0 : Milliseconds to pause between browser actions, for watching}
                            {--viewport=desktop : desktop, mobile or both}
                            {--only= : Only journeys whose title contains this}
                            {--port= : The port the run serves on}';

    protected $description = 'Drive the core loop through a real browser against a database of its own';

    /** @var list<string> */
    private const LOCAL_HOSTS = ['127.0.0.1', 'localhost', '::1'];

    /** What a database this command may rebuild is called. */
    private const DATABASE_SUFFIX = '/_(e2e|testing)$/';

    public function handle(Application $app, Mailpit $mailpit): int;

    /** The guard: the environment, the name, the host, the cached config, the inbox, the assets. Null when the run may go ahead. */
    private function refusal(Application $app, Mailpit $mailpit, string $database): ?string;

    /** Every variable the server and the migration run with. @return array<string, string> */
    private function environment(string $database, string $baseUrl): array;

    private function ensureDatabase(string $database): void;

    private function rebuild(array $environment): int;

    private function serve(string $port, array $environment): Process;

    private function waitUntilReachable(string $baseUrl, int $seconds = 15): bool;

    private function assetsRefusal(): ?string;

    /** @return list<string> */
    private function playwrightArguments(): array;

    private function playwright(array $environment, string $baseUrl): int;
}
```

`config/qori.php`:

```php
'e2e' => [
    'database' => 'qori_e2e',
    'port' => 8009,
],
```

The server's environment, over the current process's:
`APP_ENV=local`, `APP_URL=http://127.0.0.1:<port>`, `DB_DATABASE=<database>`,
`MAIL_MAILER=smtp`, `QORI_STORAGE_DISK=local`, `SESSION_DRIVER=file`,
`CACHE_STORE=file`. The migration runs as
`php artisan migrate:fresh --force --seed --seeder=Database\Seeders\PricingSeeder`
in the same environment. The server is
`php -S 127.0.0.1:<port> vendor/laravel/framework/src/Illuminate/Foundation/resources/server.php`
from `public/`, stopped in a `finally` whatever Playwright returned.

Playwright is `node_modules/.bin/playwright test --config tests/e2e/playwright.config.ts --reporter list`
plus `--headed`, `--grep <only>` and one `--project` per chosen viewport, with
`E2E_BASE_URL`, `E2E_MAILPIT_URL` (from `qori.mail.mailpit_url`),
`E2E_SLOW_MO` and `E2E_OUTPUT` (`storage/app/e2e`) in its environment.

```ts
// tests/e2e/support/mailpit.ts
export async function waitForMessage(
    to: string,
    timeoutMs = 15000,
): Promise<Message>;
export function linkIn(message: Message, pathContains: string): string;

// tests/e2e/support/person.ts
export function newPerson(project: string): {
    name: string;
    email: string;
    password: string;
};
```

## Copy

None. Console output is aimed at a developer.

## Routes

None.

## Tests

**New: `tests/Feature/Console/EndToEndCommandTest.php` — 4 cases**

1. `test_it_refuses_outside_a_local_environment` — with `app['env']` set to
   `production`, `qori:e2e` fails and its output names the environment.
2. `test_it_refuses_a_database_name_without_the_suffix` — in `local`,
   `--database=qori` fails and the output names the two suffixes.
3. `test_it_refuses_a_database_host_that_is_not_loopback` — in `local`, with
   the connection's host set to `db.example.com`, fails naming the host.
4. `test_it_refuses_when_no_inbox_answers` — in `local`, with `Http::fake()`
   answering Mailpit's `/api/v1/info` with `500`, fails naming
   `docker compose up -d mailpit`.

None of them reach the database, so no `RefreshDatabase`.

**Changed:** none.

## Acceptance

- [x] `php artisan qori:e2e` drives the journey headless from register to
      "Ready to share" against `qori_e2e`, and exits `0`
- [x] `php artisan qori:e2e --database=qori_testing` runs the same journey on
      the main test database
- [x] `php artisan qori:e2e --headed --slow=250` shows the browser doing it
- [x] A dev server that has stopped, or a missing build, is refused with the
      fix named
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Specified and approved on 17 September 2026: the owner asked for an
on-demand command, a way to watch or hide the browser, and a choice of
database including the main test database. Those three are the option
surface; everything else follows the design-review command.

Wording fixed on closing: the decision about the verification link said the
spec "polls Mailpit's search endpoint"; it lists the messages and matches the
recipient itself, so a `+` in the address never meets a query parser.

The server's environment gained one variable the Code section did not list,
`PHP_CLI_SERVER_WORKERS=1`. `.env` sets it to 4 for `artisan serve`, and with
it `php -S` forked children that outlived the stop sent to their parent and
held port 8009 and the output pipe after the run had finished.
