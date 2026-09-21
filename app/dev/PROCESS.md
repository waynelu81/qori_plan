# How Qori planning works

> The rules for turning work into tasks, and tasks into commits, when more than
> one person is building at once.

[Current plan](../PLAN.md) | Board: `bin/tasks` | [Planning index](README.md)

## Who does what

**Nobody approves.** A developer picks up a stream or a task, brings it to
`ready` if it is not there yet, builds it and closes it. There is no sign-off
between any two of those steps (`D-043`).

**The product owner is who you ask, not who you wait for.** Today that is
wayne. Ask when the answer is something only they have:

- a product call — what a person should see, which path comes first, whether
  something is wanted at all;
- anything outside the repositories — an account, a credential, a purchase, a
  real sign-in, a vendor's approval;
- a change to something recorded as settled — `PLAN.md`'s **Settled** list, or
  a `D-###`.

Everything else, decide. Read the code, pick the reasonable answer, and write
it under the task's **Decisions** with its reason. A choice somebody could
reasonably have made the other way is recorded, not escalated.

**Ask, then keep going.** Put the question to the product owner, write it under
the task's **Before this can be ready** marked _asked_, and carry on with every
part that does not depend on the answer. When the answer comes, strike the
bullet with the date and the answer. An agent asks in the conversation it is
running in; it never guesses an answer only the product owner has, and it
never waits in silence.

## Release checklist is not a prerequisite

A prerequisite is something the work cannot be **built or tested** without:
another task's code, a vendor's real response, a sandbox account. Only those
go in `depends:` or `## Blocked on`.

Privacy policy, terms, refund wording, support ownership, production
configuration, live vendor credentials, pricing and a vendor's app review are
**release checklist**. They sit on the release gate in [`PLAN.md`](../PLAN.md)
and never hold a task. Where one needs a place in the product — a disclosure
line before a vendor's consent screen, a link to the terms — build the place
and its copy key now; the final words land before release. If one has a long
lead time, the gate says so, so somebody starts it early.

## The shape of it

There are three layers and they do different jobs.

| Layer      | Lives in                 | Answers                                   | Changes                          |
| ---------- | ------------------------ | ----------------------------------------- | -------------------------------- |
| **Plan**   | [`PLAN.md`](../PLAN.md)  | What matters now, and what blocks release | When release state moves         |
| **Stream** | [`streams/`](streams/)   | Why this body of work exists, in order    | When whoever is on it learns why |
| **Task**   | [`tasks/`](tasks/)       | What to build, and how far it has got     | Openly, with a log, once ready   |

A **stream** is a line of work one person can pick up end to end without
waiting on another stream. A **task** is one commit's worth of that line.

**`PLAN.md` moves when release state moves.** Whoever's work ticks a release
gate or changes the build state updates it, in the commit that closes the task.
Its intent and its **Settled** list change only through a decision in
[`decisions.md`](decisions.md). [`status-history.md`](status-history.md) is
appended to, never rewritten.

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
- **Ids come from the tool.** `bin/tasks --new <stream> <slug>` copies the
  template under the next free id, so two people writing drafts on one
  afternoon do not both pick `T-087`.

```bash
bin/tasks                              # render app/dev/BOARD.md locally from the task files
bin/tasks --check                      # parse every task file and apply the rules, write nothing
bin/tasks --new selling vouchers-expire  # a draft stub with the next id
```

[`tests/TaskBoardTest.php`](../../tests/TaskBoardTest.php) is what actually
holds the line, and `--check` applies the same rules from the same code, so the
two never disagree. The gate fails on a dependency naming a task nobody
created, a stream with no file, a `ready` task missing a required section, a
task in progress claiming no files or a bare basename, two tasks in progress
claiming the _same_ file, anything started ahead of what it depends on, a
`blocks:` that disagrees with the other tasks' `depends:`, a `blocked` task
that does not say what and whom it waits on, a ready `L` task that names no
split, a task rewiring a flow that names no flow doc, a stream carrying a
status word, and a report from the cutoff with an untriaged finding.

## Streams are features; files are layers

A stream is a slice of the product a person can pick up: selling, identity,
onboarding. The code is organised the other way, by layer: controllers,
services, pages. So every stream eventually wants the same few files —
`SeriesService`, `routes/share.php`, the Series controller — and the
one-file-per-task rule cannot stop two streams meeting in one of them.

What stops it is the dependency rule: **where two streams need the same file,
the task that touches it says so, and the other stream's task depends on it.**
The two developers settle which goes first between themselves; the product
owner is asked only when it is a question of which matters more. That
dependency is cheaper than the merge. `T-083` splits the three hottest files
so the rule has to fire less often; it does not replace the rule.

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
whole time.

## Task lifecycle

```
draft ──▶ ready ──▶ doing ──▶ done
  │                  ▲  │
  └──────────────────┘  └──▶ blocked ──▶ back to doing when the thing arrives
   straight to doing, when you bring it to ready and build it yourself
```

| Status    | Means                                                                                                                              |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `draft`   | The shape is known and the spec is not written. Anyone may pick it up and bring it to `ready`.                                     |
| `ready`   | Whoever builds it can do so without an open question. Anyone may claim it.                                                         |
| `doing`   | Somebody has it. Their name is in `owner`.                                                                                         |
| `done`    | Merged, gate green, every box ticked.                                                                                              |
| `rescope` | Somebody found the spec wrong and handed it back rather than rewriting it. The log says what they found; the next person rewrites. |
| `blocked` | Waiting on something from outside the repositories that the work cannot be built or tested without.                                |

**Picking up a stream** is claiming its next task, in the order the stream file
gives. While you are on a stream, keep its order and its reasons true: reorder
it, split a task, add a draft for something you found. The board shows who is
on which stream from the tasks in `doing`; there is no separate field.

**Picking up a task** is one commit: set `status: doing` and `owner: <name>` in
the front matter, push. That is also how you find out somebody beat you to it.

**Bringing a draft to ready is yours to do.** Set `owner:` to yourself so
nobody specifies it twice. Work through **Before this can be ready**: answer
each bullet from the code, decide it and record it under **Decisions**, or ask
the product owner. Write the sections, delete that heading, and set
`status: ready` — or `status: doing` in the same commit, if you are the one
building it. Nobody signs it off.

**A `blocked` task carries a `## Blocked on` section** with a `What:` line
naming the thing and a `Who:` line naming the person who can supply it. Ask
them first; `blocked` is for when the answer is "not yet". Whoever sees the
thing arrive moves the task on. Pick up something else meanwhile.

The board warns when fewer than four tasks are `ready`
(`TaskBoard::READY_TARGET`) and never fails on it. A thin board means whoever
is between tasks brings a draft to ready. Old reports' untriaged findings,
which the board counts, are anyone's to triage.

## What ready means

A `ready` task leaves **no open question for the person who will build it**.
How much it names follows from who that is:

- **You are building it yourself.** The sections can be short. Scope,
  Decisions, Files and Tests carry the weight; method and column names can be
  settled in the code, and are then written into `docs/flows` in the code
  repository, which already records what the code does.
- **You are writing it for somebody else.** Name things rather than describe
  them. The test is whether two developers given the same task would produce
  the same column names, the same method signatures and the same test names.
  If they would not, it is still a draft.

Every heading of [`tasks/TEMPLATE.md`](tasks/TEMPLATE.md) is present; a section
that does not apply says **None**, so a reader can tell "nothing to do here"
from "nobody thought about it". Written for somebody else, each one that
applies is filled with **literal names**:

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

**A spec that names a vendor payload cites where the shape came from**, however
short it is: an observed response, with the date and the call, or a committed
fixture under `tests/Fixtures/<vendor>/` in the code repository. Field names
guessed from documentation are how `contact_email` became `peer_email` and how
a v2 requirements summary read "nothing outstanding" for an account that had
not started. If nobody has seen the response, the first step is a spike that
does, and the spike's result is a fixture.

Estimates are `S` (under half a day), `M` (a day), `L` (two or more — which
usually means it should have been two tasks). **A ready `L` task names its
split**: either `blocks:` lists the tasks it was cut to precede, or a `Split:`
line says why it stays whole.

## When the code disagrees with the spec

**A `ready` spec is changed openly, never silently.** When the code disagrees
with it — a column already exists, a method signature is wrong, the approach
cannot work — you neither improvise quietly nor stop and wait. Three tiers,
from cheapest:

| Tier          | When                                                                                                                             | What you do                                                                                                                                                    |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Wording**   | A typo, a lang key that reads badly, a test worth adding, a wrong Acceptance line.                                               | Fix it, note it under the task's **Notes**, list it in the report.                                                                                             |
| **Departure** | A file not in the Files table has to be touched — a route the spec forgot, a factory, a test the change broke, a `blocks:` line. | Touch it. Add it to the task under a heading **Added during execution** with the reason, and list it under **Departures** in the report, so the merge sees it. |
| **Re-scope**  | What gets built changes: the approach cannot work, a premise is false in a way that changes the design, a decision is needed.    | Write what you found under **Re-scope log**, rewrite the sections it changes, and carry on.                                                                    |

**Ask before building the rewrite** only when it changes what a person sees or
does, or contradicts a `D-###` or `PLAN.md`'s **Settled** list. Otherwise the
rewrite is yours; record it and keep going.

**If you are stopping rather than rewriting** — out of time, or the right fix is
in somebody else's stream — set `status: rescope` with the log filled in, and
push. The next person to pick the task up rewrites it.

The log is not optional in either case. A task changed halfway through with no
record is one nobody can review against anything, and a spec that quietly
stopped matching the code is one the next reader will trust and be wrong.

## Finishing

A task is `done` when every box in its **Acceptance** section is ticked and
`composer ci:check` is green from a clean tree in the code repository. Before
that:

- **Every planning commit passes `composer check`** here — `bin/tasks --check`
  then the rule tests. Code commits pass the code repository's own gate.
- **Grep the ready specs for everything you renamed.** Every route name, page,
  enum case, lang key or class the work renamed or removed may be named in a
  `ready` spec written before it. Fix the wording where that is all it is, or
  add a **Re-scope log** line to that task and rewrite the part the rename
  changed. A spec that names a thing that no longer exists is the next
  developer's first hour.
- Set `status: done`, tick the boxes, and run `bin/tasks --check`.

Then:

- **Write a report** in [`tasks/reports/`](tasks/reports/), one file per
  attempt. That directory's README is the protocol; the short version is that
  the report says what was wrong with the spec, and a report that lists files
  and says nothing about the specification has told the reader nothing
  `git status` would not. Every "Found, not fixed" bullet ends in a
  disposition — a task, a draft, or a decision — so a finding is acted on the
  day it is written.
- Rationale worth keeping goes in [`decisions.md`](decisions.md), not the task —
  appended at the end under the day's heading, with the next `D-###`.
- Evidence about the _product_ — something a person learned by using it — goes
  in [`walkthroughs.md`](walkthroughs.md). Evidence about _this task_ stays in
  the report.
- If the work moved release state, update [`PLAN.md`](../PLAN.md) in the same
  commit.
- The task file stays where it is. It is the record of what was asked for, and
  reading it beside the commit is how a reviewer checks the two agree.

**Say what you could not verify.** Not every worker has a browser, vendor
credentials, or data at a realistic scale, and a report that quietly omits the
check it could not run reads exactly like one where the check passed. The
report template has a line for this and **None** is rarely the honest answer.

## Reviewing rather than building

Everything above is about work that has not been done yet. Looking at work that
_has_ been done is organised separately, in
[`../design/reviews/`](../design/reviews/): passes and lanes rather than tasks
and streams, because a review is scoped and run by the same person and nothing
about it can be frozen in advance. Findings that need code come back here as
ordinary tasks in the `design` stream. That is the only join between the two.

## Writing a new stream

Anyone may write one. A stream file names its goal, its exit condition, and its
tasks in order with one line of reason each. Keep it short — the detail belongs
in the tasks, and the status belongs on the board. If a stream cannot be
described without describing another stream, they are one stream. Add it to
[`streams/README.md`](streams/README.md); a test looks for it there.

Streams are sized so that **their tasks touch disjoint sets of files**. Where
two streams genuinely need the same file, the task that touches it says so and
the other stream's task depends on it. That dependency is cheaper than the merge.
