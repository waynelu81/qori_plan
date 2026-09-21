# qori-plan — agent instructions

Planning, design and brand for Qori. **The code is in the `qori` repository**,
beside this one as `../qori`. The coding conventions are in `../qori/CLAUDE.md`
and are not repeated here; this file covers the planning system only.

The two repositories were one until 21 September 2026. Planning was about a
third of the tracked files and changed several times a day, so every plan edit
committed against the application and tripped the frontend dev server into a
reload.

Current build status, known issues and what's next — imported so every session
starts with it, no need to go looking:

@./app/PLAN.md

## Work comes from a task file

Planning is three layers: `app/PLAN.md` holds intent and release gates;
`app/dev/streams/` says why each line of work exists; `app/dev/tasks/T-###-*.md`
is one task each. Read
[`app/dev/PROCESS.md`](app/dev/PROCESS.md) before picking anything up. The rules
that matter most:

- **Nobody approves** (`D-043`). Pick up any stream or task. A `draft` is
  yours to bring to `ready`: answer its **Before this can be ready** bullets
  from the code, decide and record them under **Decisions**, or ask.
- **Missing information or a prerequisite: ask wayne, and keep going.** The
  product owner is who you ask — for a product call, an account, a real
  sign-in, or a change to something settled — not who you wait for. Write the
  question in the task as _asked_ and carry on with everything that does not
  depend on it. An agent asks in its conversation; it never guesses.
- **Legal, policy, pricing and production setup are release checklist** on
  `app/PLAN.md`'s gate, never a prerequisite. Build the place in the product;
  the words land before release.
- Claim by setting `status: doing` and `owner:` in the front matter.
- **A `ready` spec changes openly, never silently.** If the code disagrees with
  it, write what you found under **Re-scope log**, rewrite what it changes, and
  carry on. Ask first only when the change alters what a person sees or does,
  or contradicts a `D-###`. Handing it back instead? Set `status: rescope`.
- Below re-scope sits the **departure** tier: a file the table forgot may be
  touched if it is added to the task under **Added during execution** and listed
  under **Departures** in the report. A `blocked` task carries
  `## Blocked on`; a `ready` `L` task names its split; a task touching
  `app/Http`, `app/Services`, `app/Listeners` or `routes/` names its
  `docs/flows` file or says why there is none; decisions are cited as `D-###`;
  every "Found, not fixed" bullet in a report ends in a disposition (`→ T-###`,
  `→ draft T-###` or `→ decided: …`). `bin/tasks --check` enforces all of it and
  [`PROCESS.md`](app/dev/PROCESS.md) gives the exact forms.
- The board is rendered, not committed: `bin/tasks` writes a local
  `app/dev/BOARD.md` and `--check` applies the rules. The check fails on a broken
  dependency, a file claimed by two tasks at once, or a `ready` task missing a
  section.
- Rationale goes in `app/dev/decisions.md`, browser evidence in
  `app/dev/walkthroughs.md`, finished narrative in `app/dev/status-history.md` —
  never in `app/PLAN.md`, which is capped at 150 lines.

```bash
bin/tasks           # render app/dev/BOARD.md locally
bin/tasks --check   # parse every task file and apply the rules
composer check      # bin/tasks --check, then the rule tests
```

## Paths in a task file point at the code repository

A task's **Files** table names paths as the code repository sees them —
`app/Services/AccessService.php`, `docs/flows/storage.md`, `lang/en/errors.php`.
They are relative to `../qori`, not to this repository, and the board's rules
read them that way. Do not rewrite them to `../qori/…`.

The one exception is a task whose work is planning itself; it names paths here.

## Where things are

| Path                 | What is in it                                             |
| -------------------- | --------------------------------------------------------- |
| `app/PLAN.md`        | Intent, build status, release gates. Capped at 150 lines.  |
| `app/project-plan.md`| The product spec, cited by the code as `§<section>`.       |
| `app/dev/`           | Process, streams, tasks, decisions, product specs          |
| `app/design/`        | Brand, UI documents, design reviews                        |
| `ios/`, `android/`   | Planning for the native apps                               |
| `playbook/`          | Reusable modules: what a product of this shape costs        |
| `bin/tasks`          | The board, formerly `php artisan qori:tasks`               |
| `tools/TaskBoard.php`| The reader and every rule it applies                       |

`app/project-plan.md` is cited from roughly 200 places in the code as
`docs/project-plan.md §8` and the like. A pointer file stays at that path in the
code repository, so those citations still resolve. **Section numbers are part of
that contract** — do not renumber them.

## Never rewritten

Planning history is a record: `app/dev/archive/`, the task files, the reports,
`decisions.md`, `status-history.md` and `walkthroughs.md`. Correct a document by
adding to it with a date, not by editing what it said at the time.

## Do not

- Commit `app/dev/BOARD.md` — it is rendered locally by `bin/tasks` and
  gitignored; a committed copy conflicted on every parallel claim or close.
- Commit anything under `app/dev/tasks/reports/evidence/`. Screenshots stay
  local; a report has to stand on its own in words.
- Put coding conventions here. They live in `../qori/CLAUDE.md`, once.
