# Module: developer workflow

**What it is.** How several people — or several agents — work on one codebase
at once without standing on each other, and how a fresh clone gets to green.

**Done when.** A new checkout reaches a passing gate with one command, two
people can work in parallel without sharing a database or a file, and the
conventions have exactly one home.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| Where do the conventions live? | **One file**, and every other rules file is a pointer to it with a test enforcing that | Qori kept per-tool copies; they had already disagreed about a core data-model fact. |
| Is the task board committed? | No — rendered locally, printed by CI | Every claim rewrote its counts and re-sorted its tables, so two people finishing on one day conflicted in a file neither had edited. |
| One database for the suite? | One per checkout | Two suites on one database deadlock. |
| What enforces the planning rules? | A command, shared with the test suite, so there is one implementation | Two hand-kept copies of a rule is the same problem as two copies of a convention. |
| Does status live in one index? | No — in the task files, derived into a board | An index is the shared file that one-task-per-file exists to avoid. |
| Where does planning live? | **Its own repository** | See below. |

## Planning does not belong in the code repository

Qori kept them together for months. Planning grew to a third of the tracked
files and changed several times a day. Three costs, none obvious at the start:

- **Every plan edit was a commit against the application**, so the code's
  history stopped being about the code.
- **The frontend dev server watched the same tree**, so editing a task file
  reloaded the browser.
- **Parallel work collided in planning files** that had nothing to do with the
  code being written.

Splitting them is cheap if the tooling is portable — the board reader was 950
lines with a single framework call in it. Leave signposts at the old paths:
pointer files where the plan used to be, so the hundreds of citations in
docblocks still resolve, and a line at the top of the conventions file, which
is the one file every session reads.

## Build order

1. **One conventions file**, plus a test that other rules files are pointers.
2. **Clone-to-green**: one command from fresh checkout to passing gate.
3. **The gate itself** — format, lint, types, static analysis, tests — as one
   command, run by CI and by people.
4. **Hooks** that run only what finishes in seconds, and skip loudly when
   dependencies are missing.
5. **One database per checkout**, created by a command. Needs 2.
6. **Task files, one per unit of work**, with the board derived. Needs 3.
7. **Browser walkthroughs on demand** for the core loops — the thing tests do
   not cover. Needs 2.
8. **Split hot files** that every parallel task needs to touch. Needs 6.

## Rules that bite

- **File overlap caps parallelism, not the number of ready tasks.** Two ready
  tasks touching one controller are one task.
- **A specification changes in the open, never silently.** If the code
  disagrees with the spec, whoever found it logs what they found, rewrites the
  part that changed, and carries on. Qori first made this a full stop back to
  planning, behind a single approver, and the queue in front of that approver
  became the bottleneck (`D-043`). Keep the log; drop the wait.
- **Nobody approves, and release checklist is not a prerequisite.** Whoever
  picks a task up brings it to ready and asks the product owner only for what
  only they have. Legal copy, pricing and production setup go on the release
  gate, never in a task's dependencies.
- **Every finding ends in a disposition.** "Found, not fixed" with no next step
  is a note nobody will read again.
- **A worktree cut before a big structural change still carries the old
  structure**, and merging it fights the change.

## Traps

| Symptom | Cause |
| --- | --- |
| "Two people finishing on one day conflicted in a file neither edited" | A committed, generated index. |
| "The rules files disagree" | Copies instead of pointers. |
| "The test suite deadlocks" | Two checkouts, one database. |
| "Editing a document reloaded the browser" | The dev server watching the whole tree. |
| "The gate passes locally and fails in CI" | A cached static-analysis result over a changed type. |

## Proven / Not proven

**Proven**: one conventions file with the pointer test; clone-to-green;
one database per checkout; the derived board and its rules; browser walks of
both halves of the core loop; the planning split itself.

**Not proven**: more than a handful of genuinely parallel developers.

## Source

Qori tasks `T-080`, `T-081`, `T-082`, `T-083`, `T-119`, `T-120`.
Decision `D-014`. Stream `workflow`.
