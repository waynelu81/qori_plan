# Engineering runbook

> Environment facts, hard-won implementation traps, commands and agent workflow.

[Current plan](../../PLAN.md) | [Planning index](README.md)

## Planning

```bash
bin/tasks                       # render app/dev/BOARD.md locally (gitignored, in ../qori-plan)
php artisan qori:tasks --check  # is it stale? (the test suite asks this too)
```

Run it to see the board after any change to a task file's front matter. `BOARD.md` is rendered locally
and excluded from the formatter; editing it by hand is undone by the next run.
See `PROCESS.md` for the lifecycle and the re-scope rule, and
`tasks/reports/README.md` for what to hand back when a task is finished.

## Spec traps

Seven things the task reports found that a spec written from the code's
surface gets wrong. Read before specifying anything that touches them; each
one has cost at least one attempt.

1. **An `AppException` thrown on anything but a GET answers with a redirect
   back and a flash, not an error page.** A spec that says "the page shows the
   error" has to name the page that renders the flash — `T-073` found a free
   grant failing validation with a message nothing displayed — and a test
   asserts the redirect and the session key, not a 4xx.
2. **Vue cannot read a lang key.** The Copy table names a key and a file, and
   a Vue page cannot call `__()`; the sentence reaches it as a prop the
   controller fills. A spec that puts a page string in the Copy table without
   the prop has specified half of it, and the other half is the inline
   English `T-006` exists to remove.
3. **A stale `url.intended` outranks the landing.** Every response class that
   calls `redirect()->intended()` — password, passkey, two-factor, magic link,
   verification — goes wherever the session says first. The Series page writes
   that key on every guest visit and `regenerate()` keeps it, so a spec about
   "where sign-in lands" is really about "when nothing is intended", and a
   browser check that visited a page as a guest first will contradict it
   (`T-072`, `T-075`; `T-084` is the task).
4. **A model instance is stale within one request once another instance of
   the same row is written.** `actingAs()` holds one `User`; a service that
   loads and writes its own copy leaves the test's copy with the old values,
   where a real request would load afresh. Assert on `fresh()` or re-read the
   acting user between requests (`T-078`), and expect the same shape in any
   listener that receives a model the controller also holds.
5. **`$attributes` defaults are raw storage values.** A jsonb default is
   `'[]'` and an enum-backed column's default is the backing string, because
   no cast runs over the defaults array; the wrong shape surfaces as an error
   that names neither the model nor the column (trap 8 above, and
   `EmailSuppression` on 10 September).
6. **`RefreshDatabase` never runs a migration's data step against real
   rows.** A migration that backfills or converts is tested only against
   empty tables, so a spec for one names the check against a seeded database
   (`php artisan qori:reset`, then the migration, then the rows) as
   equipment under Preconditions, or the data step ships untested.
7. **`sometimes` skips every rule in its list when the field is absent.**
   `sometimes|required|string` is not required; it is required only when
   sent, which is what lets a PATCH omit a field. A spec that wants a field
   present on every request says `required`, and a test posts without the
   field to prove which one the rule is.

**On a fresh clone, generate the route helpers before anything reads them:**

```bash
php artisan wayfinder:generate --with-form
```

`resources/js/routes`, `resources/js/actions` and `resources/js/wayfinder` are
generated and gitignored. Vue imports from `@/routes` will not resolve until
this has run, and any tool that analyses those directories will read an empty
one and report success. The `--with-form` flag is not optional: without it the
`.form()` variants disappear and roughly ten pages stop typechecking.

## Driving a browser

**Check `document.hidden` before trusting anything a browser tells you.**

```js
document.hidden === false; // or every observation below is wrong
```

A hidden pane renders, screenshots and measures perfectly, and then silently
answers a different question than the one asked. It has caught this project
out three times:

- `requestAnimationFrame` never fires, so anything scheduled on a frame does
  nothing. `useDeepLinkedControl` shipped broken twice before this was noticed;
  it uses `nextTick` plus a timeout for exactly this reason.
- CSS animations do not run, so `animationend` never fires and any component
  whose unmount is gated on it stays mounted forever. Reka's dialogs set
  `data-state="closed"` and never leave the DOM.
- Key events do not reach the document. `Tab` with focus explicitly placed
  leaves `activeElement` unchanged, so tab order and focus rings cannot be
  observed at all.

Layout, geometry, computed styles, text content and click-driven navigation are
all reliable while hidden. Anything involving time, animation or the keyboard
is not.

## Start here

This project was designed and built across a long agent session whose chat
history does not carry over. Everything decided in it was deliberately written
down instead, in four places:

| Where                  | What                                                                                                              |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `git log`              | The reasoning. Commit messages explain _why_, not just what — read them before assuming a decision was arbitrary. |
| `../project-plan.md`   | Product spec, and §20–24 for architecture decisions with rationale                                                |
| `docs/flows/`          | What the code actually does today, with real call chains                                                          |
| `docs/tinker/`         | How to drive each flow by hand                                                                                    |

**As of 2026-09-05 this code has been executed: migrations run and all 89 tests
pass.** Until then none of it had — the tenancy foundation, the error layer, the
magic-link nonce and the whole course model were all written without a runnable
environment. The first job in any session is still:

```bash
php artisan migrate && php artisan test
```

Ten traps found and fixed the hard way, all worth not rediscovering.

> **Four of these are from the MongoDB era and no longer apply.** Qori moved to
> Neon Postgres on 8 September 2026. They are kept, annotated, and **not
> renumbered**, because the numbering is cited from code — `SeriesController`
> says "trap 5" twice — and because a present-day rule that descends from one of
> them is easier to trust when its ancestor is still on record. The vocabulary
> in the older entries predates the 9 September rename; the code is the
> authority.

1. ~~`Schema::create()` throws on MongoDB once a collection exists.~~
   **Superseded.** Migrations now declare tables, constraints and indexes
   together, and `Schema::create()` is the ordinary way to write one (§21.9).
2. ~~`RefreshDatabase` does not work on Mongo.~~ **Superseded.** It is the
   harness: it migrates and rolls back per test, and the truncation concern
   that replaced it is gone with `Tests\Concerns\TruncatesMongoCollections`.
3. `SubstituteBindings` runs before route middleware, so studio controllers must
   resolve workspace-owned models by hand.
4. `routes/auth.php` was dead code that silently 404'd anything added to it.
5. **Route parameters reach a controller action positionally, in URI order.** An
   action on `/w/{workspace}/courses/{course}` must declare `$workspace` first
   even though the middleware already supplies the context — omit it and the
   action receives the workspace slug as its course slug, with no error. This
   made every course page 404 and made publish silently do nothing. A
   `string $group` parameter is the slug as typed: `SetCurrentGroup` puts the
   Group in `CurrentGroup` and leaves the parameter alone (`T-057`).
6. **`$request->string()` returns a `Stringable`, and handing that to the query
   builder sends an object, not a string.** No exception, no match — magic-link
   emails were never sent. Always `->toString()` before a `where()`. Found on
   MongoDB and **still live**: the driver changed, the `Stringable` did not, and
   `MagicLinkLoginController` still carries the comment explaining it.
7. **`composer ci:check` can pass locally and fail in CI, because PHPStan caches
   results per file.** Adding the `staff` guard widened `$request->user()` to
   `Staff|User` everywhere, but files that had not changed were served from the
   cache and never re-analysed. CI has no cache, so it found three more errors in
   files the change never touched. When a change alters a _type everything
   depends on_ — a guard, a base model, a container binding — run
   `vendor/bin/phpstan clear-result-cache` before believing a green local run.
8. ~~**An `'array'` cast on a Mongo field stores a JSON string, not a document.**~~
   **Superseded, and inverted — which is why it is worth keeping.** Under
   MongoDB the cast made a payload opaque to the database: `lessons.content.x`
   matched nothing, so the aggregation that was the stated reason for choosing
   MongoDB could never have worked. It was found twice, on six models, because
   a cast passes a round-trip test and fails a query one.

    On Postgres the same cast is **required**: a `jsonb` column needs
    `'array'` to map to a PHP array, and Postgres still indexes and queries
    inside it. `CLAUDE.md` states this and warns explicitly not to carry the old
    instinct across, which is the sentence this entry exists to explain.

    One half did survive the move. `$attributes` defaults hold **raw storage
    values, so a cast does not run over them** — a jsonb default must be written
    `'[]'` rather than `[]`, and `EmailSuppression` hit the same shape again on
    10 September with an enum where a string belonged.

9. **Git cannot carry an empty directory, and PHPUnit 12 treats a missing
   testsuite directory as fatal.** `tests/Unit` emptied when the starter kit's
   example test was removed, so it existed on the machine the tests were written
   on and in no clone anywhere: green locally, `error code 2` on every fresh
   checkout. Held CI red from its first run. `tests/Unit/.gitkeep` fixes it — and
   the general lesson is that a suite only ever run in one working copy cannot
   see this class of bug at all.

10. **An S3 endpoint with the bucket already in it writes every object one
    prefix too deep, and says nothing.** Cloudflare's dashboard shows R2's S3
    API address as `https://{account}.r2.cloudflarestorage.com/{bucket}`, so
    that is what gets pasted into `R2_ENDPOINT` — but with
    `use_path_style_endpoint` the SDK appends `/{bucket}/{key}` to whatever the
    endpoint is, giving `…/useqori-app-bucket/useqori-app-bucket/lessons/x.pdf`.
    Nothing fails. `put`, `get`, `exists` and presigned browser PUTs all
    succeed, because the doubled segment simply becomes part of the key.
    **Only `copy` notices**, and it fails as `NoSuchKey` on an object that
    demonstrably exists — because `CopySource` is a _header_ built as
    `/{bucket}/{key}` rather than a URL path, so it alone is not doubled. The
    endpoint must be the account host with no path. `config/filesystems.php`
    now trims a trailing bucket segment rather than trusting the env var, since
    the wrong value is the one on screen. The general lesson: an object store
    has no schema to violate, so a key-shape bug is invisible until two
    operations disagree about how a key is built.

## Working with an agent session

**Claude Code** runs on this machine with a real shell: run `php artisan`,
`composer`, `npm`, `docker compose` and the test suite directly. Prefer running
things over asking.

**Cowork** (desktop app) runs in an isolated VM with no PHP and loopback-only
networking, so it cannot run any of that. There, the human runs the suite in a
terminal and pastes what matters — there is no wrapper script for it any more.

## How to run

```bash
php artisan test
```

Feature tests run against local Postgres on port 5433, in a separate
`qori_testing` database pinned in `phpunit.xml`. A second checkout or worktree
on the same machine sets its own — `DB_DATABASE=qori_wt1_testing php artisan
test` — because two suites on one database deadlock; `php artisan test
--parallel` gives each process `qori_testing_test_N`. `RefreshDatabase` is the
harness: it migrates and rolls back per test, so there is no truncation list to
keep. `Tests\TestCase` refuses any database whose name does not end in
`_testing` (or `_testing_test_N`), or a non-local host.

```bash
composer dev
```

Runs the Laravel dev server, queue listener, and Vite together (see `composer.json` `scripts.dev`).

## Local mail

```bash
docker compose up -d          # Postgres on 5433, Mailpit on 1025 and 8025
php artisan qori:mail:check   # send all six transactional messages, read them back
```

Mailpit replaced MailHog on 10 September 2026. The ports are the same, so it is
close to a drop-in; what it adds is the REST API `qori:mail:check` reads messages
back through, an HTML compatibility check against caniemail data, and a link
checker. MailHog's last release was 2020.

Read anything that arrives at http://localhost:8025. Recipe:
[`../tinker/mail.md`](../tinker/mail.md).

Three things worth knowing before you go looking for a message that is not there:

- **`MAIL_MAILER=log` sends nothing anywhere you can read it.** `.env.example`
  now defaults to `smtp` for that reason. `qori:mail:check` refuses to run on
  `log` and says so, rather than reporting an empty inbox.
- **`qori:magic-link` deliberately sends no mail.** It prints a URL. It exists
  because there was no inbox; now there is one, and it is still the fastest way
  to sign in as somebody.
- **The test suite stays on `array` and must not be pointed at Mailpit.** A
  suite that needs a container running is a suite that fails on a clean clone.
  What is tested in PHPUnit is the checking logic, against strings, in
  `tests/Feature/Mail/MailContentTest.php`.

None of this says anything about **arrival**. Mailpit is a sink on your machine.
Deliverability, SPF, DKIM and inbox placement need a real provider, which is
`T-015` and `T-032`.

## Trap: a database variable that is one character from the old one

The first deploy on Postgres returned 200 for `/`, `/auth/login` and
`/auth/register`, and **500 for `/pricing` alone** — the only public page that
queries. The error named `Host: 127.0.0.1, Port: 5432, Database: qori`.

`127.0.0.1` is the development fallback in `config/database.php`; `qori` is not
a default. So the discrete variables were being read and the URL was not. The
cause was `DB_URI` set instead of `DB_URL` — `DB_URI` being the then-current
variable name, carried over by habit from the connection string that used to
live there.

Two things follow, both now in the code:

- `AppServiceProvider::guardProductionDatabase()` refuses to boot production
  against `127.0.0.1`, `localhost` or `::1`. A convenient development default
  must not be reachable where it can only mean misconfiguration — the same shape
  as `CloudflareR2Uploads` refusing a local disk in production. Override with
  `QORI_ALLOW_LOCAL_DATABASE=true`.
- `.env.example` documents the **discrete** variables rather than `DB_URL`. A
  Neon connection string carries no explicit port, so `DB_URL` leaves `port` to
  `DB_PORT`, and a stale `DB_PORT` then silently wins over the URL — the same
  bug hit once locally before this one hit in production.

The general lesson: a misconfiguration that leaves most of the site working is
worse than one that takes it all down, because "deployed successfully" and
"working" stop being the same claim.
