# How Qori planning works

> The rules for turning work into tasks, and tasks into commits, when more than
> one person is building at once.

[Current plan](../../PLAN.md) | Board: `php artisan qori:tasks` | [Planning index](README.md)

## The shape of it

There are three layers and they do different jobs.

| Layer      | Lives in                   | Answers                                   | Changes             |
| ---------- | -------------------------- | ----------------------------------------- | ------------------- |
| **Plan**   | [`PLAN.md`](../../PLAN.md) | What matters now, and what blocks release | Rarely              |
| **Stream** | [`streams/`](streams/)     | Why this body of work exists, in order    | When priority moves |
| **Task**   | [`tasks/`](tasks/)         | Exactly what to type                      | Never, once ready   |

A **stream** is a line of work one person can own end to end without waiting on
another stream. A **task** is one commit's worth of that line, specified far
enough that a developer who has never seen the codebase can complete it without
making a design decision.

**`PLAN.md` and `status-history.md` are the owner's.** Nobody else edits
either. Finishing a task changes a task file and adds a report; if it moves
release state, say so in the report and the owner moves the plan.

## One file per task, and why

Every task is its own file, `tasks/T-###-slug.md`. Tick boxes inside it.

This is the whole reason the structure exists. A single shared plan file is a
merge conflict every time two people finish something on the same afternoon,
and the conflicts land in exactly the lines that record what is done — so the
cost of parallel work is paid in lost state. Separate files never collide.

The same reasoning decides three more things:

- **The board is rendered, not committed.** A committed copy conflicted on
  every parallel claim or close — an index everyone has to edit is the shared
  file again, wearing a hat.
- **Status lives in task files only.** A stream file says what the stream is
  for, when it is done, and its tasks in order with one line of reason each.
  Never a status word, never a strikethrough: the board says what is done, and
  a test refuses a stream file that says it too.
- **Ids come from the tool.** `php artisan qori:tasks --new <stream> <slug>`
  copies the template under the next free id, so two people writing drafts on
  one afternoon do not both pick `T-087`.

```bash
php artisan qori:tasks                      # render BOARD.md locally from the task files
php artisan qori:tasks --check              # parse every task file and apply the rules, write nothing
php artisan qori:tasks --new selling vouchers-expire   # a draft stub with the next id
```

`tests/Feature/TaskBoardTest.php` is what actually holds the line, and
`--check` applies the same rules from the same code, so the two never disagree.
The gate fails on a dependency naming a task nobody created, a stream with no
file or no owner, a `ready` task missing a required section, a task in progress
claiming no files or a bare basename, two tasks in progress claiming the _same_
file, anything started ahead of what it depends on, a `blocks:` that disagrees
with the other tasks' `depends:`, a `blocked` task that does not say what and
whom it waits on, a ready `L` task that names no split, a task rewiring a flow
that names no flow doc, a stream carrying a status word, and a report from the
cutoff with an untriaged finding.

## Streams are features; files are layers

A stream is a slice of the product a person can own: selling, identity,
onboarding. The code is organised the other way, by layer: controllers,
services, pages. So every stream eventually wants the same few files —
`SeriesService`, `routes/share.php`, the Series controller — and the
one-file-per-task rule cannot stop two streams meeting in one of them.

What stops it is the dependency rule, which stays: **where two streams need
the same file, the task that touches it says so, and the other stream's task
depends on it.** That dependency is cheaper than the merge. `T-083` splits the
three hottest files so the rule has to fire less often; it does not replace
the rule.

## Scope is the contract

**The Scope section is what the task is. Acceptance is a checklist written from
it, and checklists are written from memory.**

When an Acceptance line asks for something the Scope excludes, or promises a
result the specified design cannot produce, that is a **defect in the task**:
satisfy the Scope, record the defect under Notes, and say so in the report. It
is not a re-scope, because nothing about what gets built has changed.

This rule exists because it was learned expensively. One task was run by five
people; two stopped and re-scoped it, three completed it, and every one of them
was reacting to the same wrong Acceptance line. The Scope had been right the
whole time. Without this rule the same task can be both correctly finished and
correctly abandoned, which makes the plan useless as a way of dividing work.

## Task lifecycle

```
draft ──▶ ready ──▶ doing ──▶ done
             ▲  ▲      │
             │  └─ rescope ┘
             │
             └──▶ blocked ──┘ (back to ready when the thing arrives)
```

| Status    | Means                                                                       |
| --------- | --------------------------------------------------------------------------- |
| `draft`   | The shape is known, the spec is not written. **Do not start one of these.** |
| `ready`   | Fully specified. Anyone may claim it.                                       |
| `doing`   | Somebody has it. Their name is in `owner`.                                  |
| `done`    | Merged, gate green, every box ticked.                                       |
| `rescope` | Reality disagreed with the spec. Back to planning; nobody works on it.      |
| `blocked` | Waiting on something outside the repo (an account, a decision, a vendor).   |

**Claiming a task** is one commit: set `status: doing` and `owner: <name>` in
the front matter, push. That is also how you find out somebody beat you to it.

**Claiming a draft for speccing** is the same move on a `draft`: set `owner:`
and leave the status alone. Anyone may spec. Write the sections with literal
names, then offer it to the stream owner, whose job is to approve it — set
`status: ready` — or send it back with the question it still leaves open. A
draft is not `ready` until its owner is.

**A `blocked` task carries a `## Blocked on` section** with a `What:` line
naming the thing and a `Who:` line naming the person who can supply it. A
task blocked on nobody is a task that waits forever, and the test says so. It
goes back to `ready` when the thing arrives; the stream owner does that.

**A `rescope` task is never reset to `ready` by the person who stopped it.** It
stays `rescope` until planning rewrites the spec — that status _is_ the signal,
and clearing it discards the only evidence that anything was wrong. An
instruction to "reset the tasks you worked on" means the ones you finished.

## The stream owner

Every stream file carries `owner:` in its front matter, and the owner is the
person to ask. They:

- rewrite a `rescope`d spec, or approve the rewrite somebody else offers;
- clear `blocked` when the thing in `## Blocked on` has arrived;
- approve a draft somebody else specified, by setting it `ready`;
- arbitrate when two tasks want one file — usually by adding the dependency;
- keep the stream's task list in order, and the reasons beside it true;
- triage the untriaged findings that `qori:tasks` counts against old reports.

`PLAN.md` states a target for the board: `ready` tasks at or above twice the
number of active developers, read from `config('qori.planning.ready_target')`.
`qori:tasks` warns below it and never fails on it; a thin board is a planning
debt, not a broken build, and the stream owners are who pay it down.

## What "fully specified" means

A `ready` task names things rather than describing them. The test is whether two
developers given the same task would produce the same column names, the same
method signatures and the same test names. If they would not, it is still a
draft.

Concretely, every section of [`tasks/TEMPLATE.md`](tasks/TEMPLATE.md) that
applies must be filled in with **literal names**:

- **Decisions taken to make this specifiable** — every choice somebody could
  have made the other way, with its reason. A choice hidden in the Code
  section is one the developer will re-make.
- **Preconditions** — the data the checks verify against and the equipment
  they need, so a check that silently reads an empty directory is not mistaken
  for a pass.
- **Files** — every path, marked `new` or `edit`, with the wiring rows the
  template lists. This is also how parallel work stays safe: two `doing` tasks
  claiming the same file is a collision, and the board shows it before either
  developer hits it. A task whose Files include anything under `app/Http`,
  `app/Services`, `app/Listeners` or `routes/` names the `docs/flows/*.md` it
  will keep true, or carries `Flows: none — <reason>`.
- **Database** — table name, each column with type, nullability, default, and
  the index or constraint it takes. The migration's file name.
- **Code** — class names with namespaces, method signatures with parameter and
  return types, property names, constant names and their values.
- **Copy** — every lang key, and the file it goes in. Never inline strings.
- **Routes** — verb, path, route name, controller and action.
- **Tests** — one line per case, with its `test_it_…` method name, and the total
  stated. A reviewer counts them.

**A spec that names a vendor payload cites where the shape came from**: an
observed response, with the date and the call, or a committed fixture under
`tests/Fixtures/<vendor>/`. Field names guessed from documentation are how
`contact_email` became `peer_email` and how a v2 requirements summary read
"nothing outstanding" for an account that had not started. If nobody has seen
the response, the spec's first step is a spike that does, and the spike's
result is a fixture.

Estimates are `S` (under half a day), `M` (a day), `L` (two or more — which
usually means it should have been two tasks). **A ready `L` task names its
split**: either `blocks:` lists the tasks it was cut to precede, or a `Split:`
line says why it stays whole.

## The re-scope rule, and the tier below it

**A `ready` task's spec is frozen.** If the codebase disagrees with it — a
column already exists, a method signature is wrong, the approach cannot work —
the developer does not improvise.

1. Stop.
2. Write what you found under **Re-scope log** in the task file.
3. Set `status: rescope`.
4. Push, and say so.

Planning then rewrites the spec and sets it back to `ready`. The task keeps its
id and its history.

This is deliberately expensive, because the alternative is worse: a task
improvised halfway through is a task nobody can review against anything, and a
spec that quietly stopped matching the code is a spec the next reader will
trust and be wrong.

**The trigger is a change to _what is built_, not to how it is worded.** Three
tiers, from cheapest:

| Tier          | When                                                                                                                             | What you do                                                                                                                                                    |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Wording**   | A typo, a lang key that reads badly, a test worth adding, a wrong Acceptance line.                                               | Fix it, note it under the task's **Notes**, list it in the report.                                                                                             |
| **Departure** | A file not in the Files table has to be touched — a route the spec forgot, a factory, a test the change broke, a `blocks:` line. | Touch it. Add it to the task under a heading **Added during execution** with the reason, and list it under **Departures** in the report, so the merge sees it. |
| **Re-scope**  | What gets built changes: the approach cannot work, a premise is false in a way that changes the design, a decision is needed.    | The four steps above.                                                                                                                                          |

A departure is not a licence to widen the task. It exists because a spec
that lists eleven files and needs a twelfth is the common case, and stopping
for it taught nobody anything.

## Finishing

A task is `done` when every box in its **Acceptance** section is ticked and
`composer ci:check` is green from a clean tree. Before that:

- **Every commit passes `npm run check`**, planning-only commits included —
  prettier formats the markdown under `docs/`, and a commit that only touched a
  task file has broken the gate for everyone else before now.
- **Grep the ready specs for everything you renamed.** Every route name, page,
  enum case, lang key or class the work renamed or removed is named somewhere
  in a `ready` spec written before it. Fix the wording where that is all it
  is, or set that task `rescope` with a log line where the rename changed what
  it builds. A spec that names a thing that no longer exists is the next
  developer's first hour.
- Set `status: done`, tick the boxes, and run `php artisan qori:tasks --check`
  — before the gate, because the gate includes it and a `done` task with
  `status: doing` fails it.

Then:

- **Write a report** in [`tasks/reports/`](tasks/reports/), one file per
  attempt. That directory's README is the protocol; the short version is that
  the report exists to tell whoever wrote the spec what was wrong with it, and
  a report that lists files and says nothing about the specification has told
  them nothing `git status` would not. Every "Found, not fixed" bullet ends in
  a disposition — a task, a draft, or a decision — so a finding is acted on
  the day it is written.
- Rationale worth keeping goes in [`decisions.md`](decisions.md), not the task —
  appended at the end under the day's heading, with the next `D-###`.
- Evidence about the _product_ — something a person learned by using it — goes
  in [`walkthroughs.md`](walkthroughs.md). Evidence about _this task_ stays in
  the report.
- The task file stays where it is. It is the record of what was asked for, and
  reading it beside the commit is how a reviewer checks the two agree.

**Say what you could not verify.** Not every worker has a browser, vendor
credentials, or data at a realistic scale, and a report that quietly omits the
check it could not run reads exactly like one where the check passed. The
report template has a line for this and **None** is rarely the honest answer.

## Reviewing rather than building

Everything above is about work that has not been done yet. Looking at work that
_has_ been done is organised separately, in
[`design-review/`](design-review/): passes and lanes rather than tasks and
streams, because a review is scoped and run by the same person and nothing about
it can be frozen in advance. Findings that need code come back here as ordinary
tasks in the `design` stream. That is the only join between the two.

## Writing a new stream

A stream file names its owner, its goal, its exit condition, and its tasks in
order with one line of reason each. Keep it short — the detail belongs in the
tasks, and the status belongs on the board. If a stream cannot be described
without describing another stream, they are one stream. Add it to
[`streams/README.md`](streams/README.md); a test looks for it there.

Streams are sized so that **their tasks touch disjoint sets of files**. Where
two streams genuinely need the same file, the task that touches it says so and
the other stream's task depends on it. That dependency is cheaper than the merge.
