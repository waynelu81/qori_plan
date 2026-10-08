# Qori: an independent review after the Mac restore

6 October 2026, for Wayne. It proposes; you decide.

**How it was made.** Two multi-agent runs, 21 agents, all read-only. Seven
surveys: code health with a full gate run, the board, the release path, an
outside view, and catalogues of Qori's and MyFareWatch's planning systems,
including how MyFareWatch's changed between 27 September and 6 October. Three
fact-checkers tried to refute every claim in the state reports: 89 confirmed, 17
corrected, none thrown out. Three reviewers proposed how to adopt MyFareWatch's
workflow from different angles (faithful port; keep what Qori does better;
lighter for one owner). A synthesiser merged 72 proposals into 27, six verifiers
checked each against the files (every one needed a correction, folded in
below), and a critic read the whole. The main session then re-checked the
security findings, CI, `gh`, production's cookies and the Postmark borrowing by
hand.

**What this review touched.** `bin/tasks` re-rendered the gitignored
`app/dev/BOARD.md`. With Telescope registered locally, the artisan commands the
review ran wrote about 4,700 rows to `telescope_entries` in the dev `qori`
database (`php artisan telescope:clear` removes them). The memory note
`pushing-qori` was corrected, because the remote and `gh` changed in the
restore. This file is new and uncommitted. Nothing else was written, staged or
pushed.

Code paths are relative to `qori`, planning paths to `qori-plan`. Next free ids
at HEAD: `D-059`, `T-214`.

## 1. Verdict

The code survived the restore intact and is in good health. The plan survived
too, but it has drifted. The product has not moved since 29 September. What
stands between Qori and a paying creator is your time, a few calls only you can
make, and the scope set by `D-018`. The build is not what holds it up.

- **The code gate is green on the restored Mac.** `composer ci:check` passes on
  the working tree: Pint, `vp check`, `vue-tsc`, PHPStan level 7 with no errors,
  and all 1,512 tests. **GitHub CI, though, has been red on every push to `main`
  since 8 September**, and Laravel Cloud deploys on push without waiting for it.
- **The board parses and its rules hold**: 213 tasks, 149 done, 58 draft, 4
  blocked, 1 ready, 1 doing. The one task in `doing` (T-201) was never committed,
  and 113 findings have no disposition.
- **The work left uncommitted** spans 22 September to 5 October: three bundles in
  `qori-plan` and a Telescope install in `qori`. All of it is recoverable, and
  some of it needs a fix before it is committed.
- **The restore left security debt outside the repositories**, and nobody had
  looked at it: FileVault is off and the decrypted restore kit is still in
  `~/Downloads`. This is the most urgent item in the review (§2).
- **MyFareWatch's newer workflow is worth adopting in a light form.** That means
  one build order, Done meaning walked as the customer, the owner's own read
  turned into tasks, a push rule, a history file and quoted owner rulings. Do
  not copy its dropped guards: it has no CI, no hooks and no board checker.
  Defer the heavy rework of Qori's tooling until the product has moved (§8).

## 2. This week, in order

1. **Close what could lock Qori out or leak it** (about 30 minutes, yours alone):
   - Turn FileVault on. `fdesetup status` says "FileVault is Off".
     `~/Downloads/restore` still holds, in plain text, `keys-and-config/ssh/`
     (`id_rsa`, `waynelu81` and `myfarewatch` private keys; `waynelu81` pushes
     `qori`, and a push to `main` deploys production), `qori~.env` and
     `qori~.env.e2e`, `db/qori.dump` and `qori_e2e.dump` (their encrypted token
     columns open with the APP_KEY in that `.env`), the old login keychain, and
     `downloads/.env` and `east1.pem`, which the kit's own README says belong to
     a former employer and should be deleted and reported. Keep only the three
     `.enc` archives, with the passphrase in a password manager.
   - **Zoho Mail.** The register asks you to confirm the plan is Forever Free,
     not the 15-day trial (`account-register.md:52-53`). If a trial started with
     the MX move on 24 September, it ends around 9 October, and it would take
     `accounts@` with it. `accounts@` is the Cloudflare login.
   - Sign in once to Zoho, Cloudflare, Laravel Cloud, Neon, Stripe, Google Cloud
     and GitHub, and store the recovery codes. The reset README says iCloud
     Keychain was off and the keychain restore was best effort. MyFareWatch's
     inventory records that you were locked out of Cloudflare until 3 October,
     and that its Sign in with Google through your personal Gmail still opens
     Qori's main login and cannot be unlinked.
   - Renew `useqori.com` for several years before 1 November. WHOIS says it
     expires 6 September 2027; the register says 11 September.
2. **Make the next push safe, and commit what a second reset would lose**:
   - Finish Telescope the way MyFareWatch did (§4).
   - Commit `.nvmrc` and watch one real CI run.
   - Commit the restore's leftovers in `qori-plan`, with the two fixes in §5.
   - Give `~/apps/qori-app` a private remote. It has one commit, six modified
     files, and an untracked `PLAN.md` plus 53 files under `docs/` that exist
     nowhere else but the encrypted backup.
3. **Walk the first share by hand, and read useqori.com as a stranger.**
   Prerequisites the restore took away (§3): reinstall the Stripe CLI and run
   `stripe login`, put `stripe listen`'s secret in both webhook keys, build the
   assets, and run `php artisan qori:e2e` once to prove the `.env.e2e` Drive
   token still works. This clears T-161 and T-121. It is the one input Qori has
   never had.
4. **Make the calls that set the order** (§9), in one message: beta scope, how
   to handle campaigns, and how many hours a week Qori gets beside MyFareWatch.
   Start the long-lead chain: the accountant on the legal entity, GST, and
   whether the ABN recorded on 6 October covers Qori.
5. **Adopt the light core of MyFareWatch's workflow** (§8, "Now") and stop
   there until steps 1 and 2 of the order have shipped.

## 3. State after the restore

| Area | State |
| --- | --- |
| `qori` git | `main` = `origin/main` = `5e3c641` (29 September). Remote is now `git@github.com:waynelu81/qori.git`; the `waynelu81repo` alias is gone. Hooks active (`core.hooksPath=.githooks`). |
| `qori-plan` git | `main` = `origin/main` = `42548c5` (29 September). No `vendor/`, no hooks, no CI; `composer check` cannot run until `composer install` (the offline cache lacks phpunit 12.5.35). |
| `gh` | Signed in as `waynelu81` and reads CI now (it could not before). |
| Toolchain | PHP 8.5.11 (MacPorts), Node 24.21, Composer 2.10; `vendor/` and `node_modules/` match their lockfiles. Docker runs under Colima. |
| Databases | `qori-postgres` (postgres:18, 5433) healthy. `qori`, `qori_testing`, `qori_wt1`, `qori_wt1..4_testing`, `qori_e2e` present; dev data matches the 28 September dump (17 users, 10 Groups, 24 Series). All 31 migrations ran, including Telescope's. The same container holds 12 MyFareWatch databases, so stopping or recreating it stops both products. |
| Mail | A standalone `mailpit` container shared by every project (not compose's `qori-mailpit`). |
| `.env`, `.env.testing`, `.env.e2e` | Present. `R2_BUCKET` is the test bucket and `QORI_STORAGE_DISK=r2`, so dev uploads hit real R2. `STRIPE_CONNECT_WEBHOOK_SECRET` is empty: it was never set, because the key came with T-188 on 28 September, after the `.env` was last written on 23 September. |
| Lost in the restore | The Stripe CLI (it was a global npm package; `command -v stripe` finds nothing, `~/.config/stripe` is gone). `public/build` (only a stale `public/hot` from 28 September). The T-201 probe scripts and tokens, which lived in a session scratchpad. |
| Intact (checked) | Claude memory (28 notes), `~/.claude/settings.json` including the read-only Laravel Cloud allow-list, SSH push authentication, the git identity, scheduled tasks (none before or after). |
| Leftovers | Worktree `qori/.claude/worktrees/laughing-robinson-64b58c` and branch `claude/laughing-robinson-64b58c`: already in `main`, nothing to recover. Dependabot PR #2 (actions/cache) is open and red. MyFareWatch's merged `-b001`, `-b003`, `-step2`, `-step3` and `-repro` checkouts and their databases. |
| Other repos without a remote | `qori-app`, `satori-app`, `roadtrip-cam`. `myfarewatch-plan` has 10 uncommitted files, including `D-110` to `D-117` and the pricing review. |

## 4. The code

**Gate** (each step of `composer ci:check`, run without fix flags):

| Step | Result |
| --- | --- |
| `pint --test` | pass |
| `npm run check` (`vp check`) | pass: 375 files formatted, no lint errors |
| `vue-tsc --noEmit` | pass |
| PHPStan level 7 | pass, 0 errors, no baseline |
| `php artisan test` | 1,512 passed, 8,669 assertions, 1 risky |

**GitHub CI.** The last green run on `main` was 7 September (`f225cd1`). Runs
from 8 to 12 September failed at "Setup Application". Every run since 14
September (`064cc10`) fails at "Setup Node", because `.github/workflows/tests.yml`
reads a `.nvmrc` that was never committed (logged in `fixups.md:40` on 21
September). Later steps have never run under the current workflow, so committing
`.nvmrc` is the first fix, not a known cure, and its 15-minute timeout has to hold
a serial suite on a two-core runner. T-081 and the README already say Node 22.
`.githooks/pre-push` runs Pint, PHPStan and the tests outside the `slow` group.
It never runs `vp check`, `vue-tsc` or the build, and it exits 0 when `vendor/`
is missing. Today a TypeScript error can deploy.

**The uncommitted Telescope install** (5 October; it also adds
`barryvdh/laravel-ide-helper` and three `.gitignore` lines). It works locally
and production can never load it: it is `require-dev`, `dont-discover`, and
registered only in `local`. Before it is committed:

1. Move the migration to `database/migrations/local/` and load it from
   `TelescopeServiceProvider`, as MyFareWatch did in `576cf44`. In
   `database/migrations/` it would run on Neon with the deploy's
   `migrate --force` once committed. Its connection also defaults to `mysql`
   (`config/telescope.php`), which fails the deploy if Laravel Cloud does not set
   `DB_CONNECTION`. Nobody has checked that setting.
2. Hide token fields in every environment. Locally it records Google, Dropbox and
   Stripe Connect token exchanges in plain text, including `client_secret`,
   `code`, `access_token` and `refresh_token`, along with magic-link emails and
   query bindings. The `connections` table encrypts those same tokens.
3. Keep `wayfinder:generate` out (one run wrote about 4,658 view entries), and
   schedule or document a prune.
4. Add a `qori/CLAUDE.md` line on what it is and where it runs, and give it a
   task (T-214), since work comes from a task file.

**Production, read from outside.** `useqori.com` and `/up` answer 200.
- `/privacy` and `/terms` serve the drafts with their placeholders visible: 21
  distinct, 19 in the privacy policy and 11 in the terms, some shared.
- `/pricing` has no public plan (`prices: []`) and shows "Pricing is being
  updated", in inline English.
- **Public sign-up is open** (`/auth/register` 200).
- **Sessions run on Laravel's cookie driver, not Valkey.** A 40-character cookie
  named for the session id carries the payload beside `qori-session`. That
  contradicts `qori/CLAUDE.md`, `app/PLAN.md:39` and `.env.example:74`, and it
  undercuts the `user_sessions` revocation design. The cache store, which rate
  limiting uses, is unknown.
- Nobody has read the Laravel Cloud deploy log, Sentry, or the scheduler's runs
  since 29 September. `5e3c641` was pushed; that it was deployed is assumed.

**Shared with MyFareWatch.** MyFareWatch's production mail used Qori's Postmark
configuration from 27 September until its own account was approved on
5 October. If Qori's server token is still in MyFareWatch's Laravel Cloud
environment, remove it and rotate it.

**Smaller items.** `composer audit` flags `league/commonmark` 2.10.0, one high
and one medium advisory; the only use is `Str::markdown` on Qori's own legal
text, so exposure is low, and `composer update league/commonmark` fixes it. The
full `npm audit` shows 3 critical advisories through `vite-plus` 0.3.0, fixed in
1.0 (a major upgrade). `qori:series:purge` and `qori:connections:refresh` lack
`onOneServer()`. `composer.json` is still named `laravel/vue-starter-kit` and
allows the removed Pest plugin. Departures from `qori/CLAUDE.md` worth a task:
AWS's SDK runs inside `SnsWebhookController`, `StripePurgeConnectedAccountsCommand`
calls Stripe directly, and `StripeWebhookController` reads payloads itself (T-114
covers this last one).

## 5. The plan: board, in flight, uncommitted

`bin/tasks --check` exits 0 with and without the uncommitted work. It warns about
113 untriaged findings (all in reports before the `2026-09-15` cutoff), and that
1 task is ready against a target of 4.

**Nothing is claimed at origin.** The last tasks done were T-153, T-166, T-182,
T-154, T-118, T-115, T-188, T-117, T-199, T-211, T-210 and T-156, closed 27–29
September: 22 in three days, most of them small.

**The uncommitted planning work is three bundles:**

- **A, 22 September: the companion edits from bringing T-097 to ready.**
  Citations moved after the split, and T-097's findings folded into T-098, with
  re-padding in T-099 and T-150. Coherent and finished. T-097's committed `ready`
  status rests on these edits, so commit them first.
- **B, 23 September: the Dropbox team-account spike T-201**, paused by you after
  steps 0 to 2 with step 3's uploads in. It adds `depends: T-201` to T-096, and
  three redacted fixtures in `qori/tests/Fixtures/dropbox/*-team.json`.
  - What it found so far: the team default lets anyone outside be added
    (`shared_folder_member_policy: anyone`), which contradicts T-095's premise.
  - Before committing, add the two unlisted fixtures under "Added during
    execution" and mark it `blocked` on you.
  - Resuming means re-linking at step 1 in a browser signed in as
    `support@useqori.com`.
  - Clean-up still owed on Dropbox: three test files, the "Qori team folder" and
    the Qori Share connection.
- **C, 26–28 September: `account-register.md`**, a row in `app/dev/README.md`, and
  a Cloudflare line in `release-prerequisites.md`. Fix three things before
  committing:
  1. The new line at `release-prerequisites.md:12` pushes the `:29` that T-095,
     T-097, T-044, T-096 and T-099 cite onto the Vimeo bullet. Fold it into an
     existing line.
  2. The Microsoft row (a US$7 Business Basic seat) contradicts `D-042`'s free
     sandbox or trial.
  3. The Cloudflare row should say the Google link survived.

  It overlaps `vendor-accounts.md` only on three test-month prices.

**Ready queue:** T-097, the OneDrive spike. It needs a Microsoft work tenant
that only you can open; the free E5 sandbox needs a qualifying subscription,
otherwise it is a trial cancelled before it bills.

**Blocked, all on you:**
- T-161: your walk by hand.
- T-121: the same walk; its blocker text is out of date.
- T-122: a paid Zoom month, which `D-042` sends back to you.
- T-022: a visible browser at your desk for the keyboard pass.

**The plan has drifted from the code**, and no check catches it (list in §10).

## 6. What stands between Qori and release

**None of the eight beta-gate boxes is ticked.** What each waits on:

| Gate | Waits on |
| --- | --- |
| Core loop at both widths | Your walk (T-161) |
| Real vendor smoke tests | T-161, then each provider |
| Production mail, queue, webhooks, alerts | T-018, T-019, T-017 (drafts); live Stripe webhooks |
| No predictable 403 or dead page | T-014, T-045 (campaigns: ship or hide), T-011 |
| Backup and restore exercised | T-020 (and Neon's retention, from you) |
| Legal checklist | Entity, ABN, Wise, the legal words, the five code places below, a lawyer |
| Five creators unaided | Recruiting, which nobody has started |
| `ci:check` green from a clean checkout | `.nvmrc`, then a real CI run |

**The money path has been built and scripted, never walked by hand end to end.**
Stripe's sign-in worked for you on 21 September, T-044's walk made a real Google
connection, and the T-161 script ran against Stripe test mode and Drive on 21
and 23 September. What no person has done is the round trip back to the Series,
the Picker on a real account, Stripe's Checkout with a card, the confirmation
step, and a real Drive grant on Open (first-share steps 7–9 and 12–14).

**Your chain to live money.** Accountant (entity, GST), ABN, Wise, the legal
words, live Stripe activation, live prices, both webhooks, the portal. An ABN was
recorded on 6 October in MyFareWatch's inventory. Whether it covers Qori depends
on the entity type, which is the accountant's question. Qori's own register does
not yet know about it.

**Five code places the legal drafts wait on, with no task yet**
(`release-prerequisites.md`, "Code the documents wait on"):
1. Terms accepted at sign-up, with the version recorded.
2. Billing says each plan renews until cancelled, and how to cancel.
3. Invitation and access emails name who added the person and link the privacy
   policy.
4. "yours to keep" squared with the deletion cascade.
5. The Customer Portal cancels at the end of the period.

**Disclosed rather than fixed.** Say which of these to fix instead:
- A Peer's Drive permission is never removed.
- Account deletion revokes neither the Google token nor Stripe's connection.
- Deleting a creator ends Peers' paid access silently.
- A signed-out visitor can see an invitation's address, name and price.
- Consent can be recorded from an unticked box.
- Sentry may carry IP addresses and form input.
- An over-cap Group can still sell.
- Vimeo embeds lack `dnt=1`.
- The cookie session driver (§4).

**Mail.**
- MX, SPF and DKIM are on Zoho AU.
- DMARC is `p=none` with reports to your personal Gmail, and there is no
  authorisation record for it, so in practice the reports go nowhere. Both
  documents say `dmarc@`.
- SES has no DNS records (`mail.useqori.com` answers only through the wildcard).

**Storage scope is the largest body of work.** `D-018` puts all seven providers
in beta, and you declined narrowing to Drive on 20 September ("I plan to do all,
it is a lot of work. But I see this is the major selling point for Qori").
- 17 open tasks, 7 of them L.
- No provider task is ready.
- The foundation T-091 is a 27,883-word draft. Many of its open bullets are
  recorded answers rather than questions, so its "18 open questions" overstates
  what is really open.
- Spikes have already thrown away two designs written ahead of them (`D-036`
  Drive, `D-058` Dropbox).
- Under `D-042`, providers that need paid accounts (Zoom, possibly Microsoft)
  come back to you.

**Two routes, in tasks:**

- **The plan as written** (beta gate plus all seven providers): about 60 open
  tasks on the beta streams, plus the storage stream, whose outside reviewer put
  a floor of 19 developer-days on it on 20 September, before any spec repair or
  vendor approval. Add the vendor reviews (Microsoft Partner Center, Dropbox
  production, the Zoom Marketplace, Google brand verification). **Two to three
  months or more.**
- **The smallest route to a paying creator** (Drive, Qori uploads, pasted links;
  the other providers after): about 20 tasks, roughly half S and half M. That is
  the five legal code places, T-102 and T-103 (T-103 re-scoped off T-091),
  T-013, T-017, T-018, T-019, T-020, T-011, T-045, T-184, T-198, T-212, T-088,
  T-104 and T-105. **About 2–3 weeks of engineering at late September's pace,
  when Qori had all your attention; 3–6 weeks of calendar time**, set by the
  lawyer and Stripe's review, not the build.

Free already allows 1 Series, 50 Peers and Peer payments at a 0% fee, so Qori's
own first dollar needs a creator who has outgrown Free.

## 7. The outside view

**Strengths.**
- Disciplined engineering, with its guards enforced by tests: PHPStan level 7
  with no baseline or ignores, ten ArchitectureTest guards, and 40.8k lines of
  tests against 37.0k of app PHP.
- No `ShouldQueue`, no mutable Carbon in models, no vendor HTTP in Services.
- The core loop exists in code and as a script.
- Production infrastructure is already up.
- 149 tasks done in about 20 days.
- `journeys/first-share.md` is the right lens, and `D-043` removed the approval
  bottleneck.
- The conventions carried over well enough to start MyFareWatch fast.

**Concerns.**
1. **No human walk, no creator.** Nothing in the plan records customer discovery
   beyond the gate line. The nearest input is the owner's course that
   `course-classroom.md` models. In the week after the loop went green, agents
   built about 20 classroom tasks while T-161 waited on you.
2. **Scope grew before anything was validated.** Seven providers before beta,
   plus custom vocabulary (51 PHP files, 18 Vue files), certificates (now
   switched off), campaigns (no way in) and six fixed currencies.
3. **The planning layer is out of proportion for one owner with agents.**
   - About 900k words in `qori-plan`.
   - 58 drafts averaging 3,800 words, longer than the average done task.
   - A 205-line task template, plus a 97-line report template and a 47-line
     re-scope template.
   - A ready target sized for two developers, and twelve streams, each "one
     person's line of work".
   - Your reading time is the scarce resource, not the agents' words.
4. **Hotspots.** `SeriesController::show()` spans about 380 lines with nine
   injected classes; `Show.vue` is 1,292 lines; `ConnectionService` is 883.
5. **Idle and at risk.** No commits since 29 September, and the uncommitted work
   above.

## 8. Adopting MyFareWatch's workflow

### What MyFareWatch changed

MyFareWatch copied Qori's *shape* on purpose: its brief says "Chosen to match my
Qori setup". That covers a 150-line PLAN.md, `§n`, `D-###`, `R-###` passes over
seven lanes, and the conventions. It left out Qori's *machinery*: streams,
`bin/tasks`, the rendered board, separate reports, `/do`, `/spec` and `/stream`,
CI and hooks. From 4 October it grew the following:

- **Done means walked** (MFW `D-098`, `WALKTHROUGH.md`). The builder opens every
  changed screen fresh, as a first-time customer, across the lanes. They fix
  blockers and defects before done, write polish down, and name what was not
  seen. MyFareWatch itself still lists `D-098` as "to confirm or overrule".
- **Your customer-language standard** (MFW `D-104` and `D-108`,
  `CUSTOMER-LANGUAGE.md`): natural sentences, the customer's words, the benefit
  before the rule.
- **Lighter `B-###` tasks** (a 69-line template) with "the traveller at that
  moment", the Report inside the file, a `decision` status, and your numbered
  decision queue on the board.
- **"The owner decides; a session proposes."** A recommendation is recorded as a
  `D-###` that the build follows until you rule, with your words quoted and
  dated. Open questions are kept as `Q<n>` rows, each with its default.
- **One build order, each step shipping before the next** (MFW `D-068`), with
  paid parts behind switches (MFW `D-100`).
- **Your own read of the live site as a stranger** (`R-003`) produced tasks
  B-011 to B-017 and reordered the board ("make sure the site is ready for
  customer to use and not feel half bake").
- **Built, merged, pushed and deployed as separate steps.** One planning session
  integrates: it trial-merges, merges and pushes on your quoted word, then reads
  production after each deploy.
- **A worktree per task**, with its own databases and ports.
- **A `history.md` that is never rewritten**, and an inventory of accounts with
  cost, status and login.
- **Telescope kept local**, with its migration in `migrations/local`.
- **CLAUDE.md points at PLAN.md** instead of `@`-importing it (you called the
  import "a convenience hack").
- **Independent decision documents**: "It proposes; you decide", closed by
  "What the owner decided". This file follows that shape.

**What dropping Qori's machinery cost it:**
- two sessions took `D-102`;
- statuses were written as prose ("blocked: deployed");
- a deploy went unrecorded (`9cf9129`);
- CLAUDE.md says "never push" while sessions push;
- there is no CI anywhere;
- the worktree rules live only in memory.

### Now: no ruling needed, or one you can overrule in the same message

- **Point at PLAN.md instead of importing it.**
  - Where: `qori-plan/CLAUDE.md:12-15`, whose "known issues and what's next" claim
    is untrue anyway, and the `@./PLAN.md` line in `qori/CLAUDE.md`.
  - For Qori this is about clarity, not tokens: the files are about 2.3k tokens,
    not MyFareWatch's 8k.
- **Bring the live instructions back in line with `D-043` and the split.**
  - PLAN.md:
    - rule 6 ("frozen", which contradicts PROCESS);
    - line 49 (T-044 is done);
    - the Waiting list (T-063, T-089 and the notify interval are answered);
    - the Updated line.
  - The slash commands:
    - `/spec`'s `approve` mode and "stream owner";
    - `/do`'s steps;
    - `/stream`'s "owner".
  - Stale command and path references:
    - `qori:tasks` in `app/dev/README.md`, `reports/README.md`,
      `reports/TEMPLATE.md` and the runbook;
    - `docs/planning` paths in `prompt-template.md` and
      `app/design/prompt-design-review.md`.
  - Broken links in the design-review README.
  - Claims about checks that do not run:
    - the board-rule claims in `qori/README.md` and the pre-commit comment;
    - the "CI prints the board" claims in `qori-plan/.gitignore` and `bin/tasks`.
  - Other stale statements:
    - `language.md:17` (custom vocabulary was decided on 9 September; the
      document is stale, not the code);
    - the struck-but-not-struck open decisions;
    - the risk register;
    - the Email Routing and DMARC lines in release-prerequisites;
    - MongoDB in `status-history.md`.
  - The memory notes that will contradict the new rules: `planning-gatekeeper`,
    `ready-bar-and-parallelism`, `storage-stream-review-before-build`,
    `worktrees-and-parallel-sessions`.
- **`app/dev/history.md`**: dated, never rewritten.
  - Repoint `qori-plan/CLAUDE.md:55`, PLAN.md:54 and PROCESS:73.
  - Record a push as "pushed" until someone reads the deploy.
- **Quote your rulings exactly, with the date.** The quote goes in the commit or
  the planning record, never containing a secret or a personal identifier.
- **Re-read the plan before building and before merging.** Take ids at commit
  time. Write the worktree merge recipe into PROCESS (it lives only in memory
  today); check lanes against each other, not only against `main`.
- **Decision documents.** This one is the first; your answers are appended under
  "What the owner decided".
- **Done means walked as the creator or the Peer** (offered as a default; MFW's
  own `D-098` is still unconfirmed).
  - Port `WALKTHROUGH.md` into `app/design/reviews/`, with Qori's own checks:
    - a Group with custom vocabulary;
    - the a/an rule;
    - `D-035` vendor names and `D-037` whose-storage lines;
    - `D-018`'s tier limitation lines;
    - 360 px with no sideways scroll;
    - both appearance modes;
    - 200% zoom and keyboard.
  - Mail lives in `app/Notifications/*`, not `resources/views/mail`.
  - Findings route through a valid disposition (`→ fixups.md` is not one).
- **Your customer-language standard over Qori's copy** (offered as a default).
  - Port it with a preface: §4–§6 are partly MyFareWatch-specific.
  - It works inside Qori's tested rules: lang keys, message plus resolution, and
    Terminology. `D-035` and `D-037` are not tested.

### Now, on your word

- **Telescope as T-214, MyFareWatch's shape** (§4).
- **A push of `qori`'s `main` is a production deploy.**
  - It happens only on your word for that change, quoted in the record, and is
    followed by a read of production.
  - `decisions.md:822-825` already says Cloud deploys on push, but no working
    rule (CLAUDE.md, PROCESS, `/do`) does.
  - If the permission check refuses a session's push, you run it.
  - Merging PR #2 on GitHub is also a deploy.
- **Make the gate real; do not copy MyFareWatch's lack of one.**
  - `.nvmrc` at 22 (T-081 and the README already say 22), then one watched CI
    run.
  - `pre-push` refuses to run without `vendor/`, and its comment says what it
    skips.
  - `composer install` in `qori-plan`, plus a pre-commit hook there running
    `bin/tasks --check`.
- **Commit the restore's leftovers** (§5), in this order: A, then C fixed, then B
  as `blocked`.
- **Your walk, written up as pass `R-005`**, whose findings become tasks.
  - Closing T-161 and T-121 needs reports.
  - T-121's Acceptance (`qori:e2e --only=pays`) has to be met or re-scoped.
- **One build order you hold**, in `app/dev/ORDER.md`.
  - Each step ships before the next.
  - Sessions add tasks inside a step freely; only a reorder needs your dated
    word, as MyFareWatch does in practice.
  - Streams stay as the "why" beneath it.
  - It amends `D-043`'s "Streams have no owner", and the documents that say
    "pick up any stream" move with it.

The proposed first order:

| Step | Ships | Holds |
| --- | --- | --- |
| 0 | Safe after the restore | T-214, `.nvmrc` and hooks, leftovers committed, stale worktree removed; your Zoho and domain chores |
| 1 | The first share walks clean by hand | Connect secret, your T-161 walk, T-121 closed, R-005 |
| 2 | Money in is safe | T-102, T-103 (re-scoped off T-091), T-013, T-198, T-200, T-184, R-005's findings; campaigns ship or hide |
| 3 | A stranger is told the truth | T-014, T-011, T-088 then T-104, T-105, T-108, T-212, T-213, the five legal code places, T-022 when you can |
| 4 | Know it broke, put it back | T-018, T-019, T-020, T-017, `onOneServer()`, SPF/DKIM/DMARC recorded |
| 5 | First creators | Your chain alongside from step 1; live prices, webhooks, portal; 3–5 creators walked |
| 6 | Providers, one at a time | Each from a free spike (`D-042`), shipped and walked before the next: Dropbox, OneDrive, Vimeo/YouTube, Zoom, Teams; T-091, T-092, T-094 rewritten from the code when the second provider starts |

### Next: once steps 1 and 2 have shipped

- **Build on a recorded default** when a call waits on you.
  - This takes a new `D-###` amending `qori/CLAUDE.md` rule 0's "Never guess
    one" and PROCESS's "never guesses".
  - `D-043` already allows working around a pending answer.
- **A `decision` status and a generated queue of your calls; retire `rescope`.**
  - The queue must migrate the real open calls first: the untagged "(the
    owner's)" bullets in 41 drafts, and about 37 lines in `decisions.md`
    "Decisions needed".
  - The `_asked_` marker finds almost none of them.
- **`--check` catches what MyFareWatch's board let through**: unknown statuses,
  duplicate T- or D- ids, and dangling references. It needs its own negative
  fixture root, because the shared fixture backs exact assertions.
- **A lighter template, about 75 lines, with "the creator or Peer at that
  moment".**
  - Keep the three placeholders `bin/tasks --new` replaces.
  - Handle `blocks:` and the L-split rule.
- **The report moves inside the task file.**
  - The parser needs `###` sections and an ISO date per attempt.
  - Keep the disposition check and the honesty rows.
- **A worktree per task whenever another session may run.**
  - Copy the main `.env` with its APP_KEY, or the encrypted token and 2FA
    columns cannot be read.
  - Run `createdb` through `docker exec`.
  - Stay inside the four-slot database pool.
- **Read production after every deploy** through a read-only Laravel Cloud
  token. Sentry stays yours to read.
- **Switches for what a stranger should not meet yet.**
  - Invite-only sign-up is the closest match to MFW `D-100`.
  - `/pricing` needs copy in lang, not a switch.
  - `peer_payments` on Free still says "confirm before launch".

### Later

- **Re-measure findings, and triage the 113 old ones once.** The triage file has
  to be declared a standing record.
- **Rewrite the brand guide.** Its Voice table and UX rules exist but still say
  "course", "student" and "TeachDigest". The generator needs inkscape, DejaVu
  fonts and PIL, none of which this Mac has.

### Skip

- **A hand-kept, committed board.** `D-014` exists because a committed board
  conflicted on every parallel claim.
- **What MyFareWatch left out:** CI and hooks, streams, the `owner:` field, the
  flow docs, the draft status, in-row edits to decisions, and rules kept only in
  memory.

### Keep from Qori, whatever is adopted

- Status lives in task files and the board is rendered (`D-014`).
- `bin/tasks --check` and TaskBoardTest.
- Append-only `decisions.md`.
- A disposition on every finding.
- The report's honesty rows: how the defect failed, "Could not verify", and
  "Where the specification was wrong".
- The Files table with the collision and flows rules.
- The three re-scope tiers.
- Spike first, with an observed payload or fixture.
- `D-042`'s free tiers.
- `journeys/first-share.md`.
- `fixups.md`.
- `docs/flows` and `docs/tinker`, so CLAUDE.md stays conventions only (MFW's
  grew to 55 KB).
- The code gate, repaired, never dropped.
- The plan and code commit pairing.
- `/do`, `/spec` and `/stream`, brought up to `D-043`.
- The playbook, which should now learn from MyFareWatch: the walkthrough,
  worktrees and order-first planning worked; no checker and a hand-kept board
  did not.

**One warning.** Most of these proposals add process. MyFareWatch got fast with
less, and its lesson is order and feedback, not tooling. Do the "Now" list and
the first two steps of the order. Hold the TaskBoard and template rework until
the product has moved.

## 9. Decisions for you

Each comes with the default that will be built if you say "the defaults".

1. **The restore's leftovers.** Commit A, then C with its three fixes, then B
   marked `blocked` on you, with its fixtures. *Default: yes.*
2. **Telescope.** Finish it as T-214 in MyFareWatch's shape and commit it.
   *Default: yes.*
3. **The push rule.** A push to `qori`'s `main` only on your word for that change,
   recorded with a production read. *Default: yes.*
4. **The gate.** `.nvmrc` at Node 22 and one watched CI run, `pre-push` refusing
   without `vendor/`, and a `bin/tasks --check` hook in `qori-plan`.
   *Default: yes.*
5. **Beta scope.**
   - **A:** all seven providers before beta, as `D-018` stands.
   - **B:** amend `D-018`, so beta opens on Drive, Qori uploads and pasted links,
     with the other providers following in order of creator demand.
   - **C:** keep `D-018` for public beta, but give 3–5 creators early access on
     Drive, uploads and links from step 5 while step 6 proceeds.

   *Default: C.*
6. **Campaigns** (T-045): ship or hide. *Default: hide.*
7. **Time.** How many hours a week Qori gets beside MyFareWatch. ORDER.md is a
   list without it. *No default; yours.*
8. **One build order you hold** (`ORDER.md`, the table above). *Default: yes.*
9. **Done means walked, in your customer language** (the walkthrough and the
   standard, adapted to Qori). *Default: yes.*
10. **Build on a recorded default** when a call waits on you (amend "Never guess
    one"). *Default: yes, after steps 1 and 2.*
11. **A read-only Laravel Cloud token for Qori**, so sessions can read deploys.
    *Default: yes, when step 0 ships.*
12. **Your walk.** When you can give it an hour at a visible browser.

## 10. Stale statements found

- `app/PLAN.md`:
  - line 49 (connections have "no way in", but T-044 is done);
  - rule 6 ("frozen");
  - the Waiting list (T-063, T-089, the notify interval);
  - the Updated line (ten commits changed it on 27 September);
  - line 39 (Valkey sessions).
- `qori-plan/CLAUDE.md:12-15`: PLAN.md has no "known issues" or "what's next".
- `qori/CLAUDE.md`: "Session and cache are Valkey in production"; "the init
  script creates `qori_wt1` to `qori_wt4`" (it creates only the `_testing` ones).
- `app/project-plan.md:3`: `/Users/dev/dev/qori`.
- `app/dev/README.md:71`, `prompt-template.md:50`, `reports/TEMPLATE.md:75,80`,
  `engineering-runbook.md:11`: `qori:tasks`.
- `decisions.md` "Open decisions": T-028, T-032 and T-043 are done but not
  struck.
- `risk-register.md`:
  - QORI-004 and QORI-005 are resolved in code;
  - QORI-001 and QORI-002 are only partly resolved;
  - there is no demand risk.
- `streams/language.md:17`: `custom_vocabulary` "false on every plan" (the code
  follows your 9 September decision).
- `release-prerequisites.md`:
  - lines 42 and 47 (Cloudflare Email Routing; DMARC to `dmarc@`);
  - line 55 (domain "registered 2026-09-11"; WHOIS says 6 September).
- `account-register.md`:
  - line 24 (renewal date);
  - the Microsoft row;
  - the Cloudflare row;
  - no ABN;
  - no Dropbox team account.
- `status-history.md`: MongoDB in the Status table; nothing added since
  21 September.
- `T-121`: its blocker asks for an `.env.e2e` that already exists.
- `T-122`: still cites `docs/planning/` and asks for a paid Zoom month.
- The `pushing-qori` memory: corrected today.
- Production page titles are all lowercase "qori".

## What the owner decided

**8 October 2026.**

- **Qori is its own project.** In the owner's words: "Qori is a separate project
  to Myfarewatch, so both can run at the same time. I am just try to borrow some
  planing from Myfarewatch." MyFareWatch is a source of planning patterns only.
  Qori shares no infrastructure, deployment, money or time budget with it.
  Decision 7 (hours a week beside MyFareWatch) falls away, and so does §6's
  caveat about late September's pace. MyFareWatch's databases sitting in the
  local `qori-postgres` container and the shared local Mailpit are conveniences
  of one developer's Mac and link nothing. If Qori's Postmark server token is
  still in MyFareWatch's environment (§4), that is a leftover to remove from
  MyFareWatch's side, not a dependency.
- **Telescope first.** In the owner's words: "So installed telescope Qori
  first?" It became `T-214`.
