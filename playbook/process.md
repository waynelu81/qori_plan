# The planning process

The system Qori uses. It is small, and its value is almost entirely in two
rules — the frozen specification and the derived board.

The live version, with the exact forms, is
[`../app/dev/PROCESS.md`](../app/dev/PROCESS.md); the tool that enforces it is
[`../bin/tasks`](../bin/tasks). What follows is why it is shaped this way.

## Three layers

| Layer | Holds | Changes |
| --- | --- | --- |
| **The plan** | Intent, state, release gates. Capped at 150 lines. | When intent or release state moves |
| **Streams** | Why one line of work exists, in what order, who owns it | When the ordering or the reasoning changes |
| **Tasks** | One file each, specified down to the column and method name | Constantly |

**The board is derived, never committed.** It is rendered locally from the task
files. Qori committed it once; every claim or close rewrote its counts and
re-sorted its tables, so two people finishing on the same day conflicted in a
file neither had edited.

## The rules that carry the weight

**A ready specification is frozen.** If the code disagrees with it, the work
stops, what was found is written down, and the task goes back to planning. It
is not improvised. This is deliberately expensive, and the expense is the
point: improvisation is how two people build different things from one plan.

**Below that sits a departure tier**, because absolute rules get ignored. A
file the specification forgot may be touched if it is added to the task and
listed in the report. That is the pressure valve that keeps the freeze
credible.

**Every finding ends in a disposition** — a new task, a draft, or a recorded
decision not to. "Found, not fixed" with no next step is a note nobody reads
again, and a hundred of them is a backlog you cannot see.

**Decisions get ids and are appended, never edited.** A decision that was
reversed keeps its entry and the reversal cites it. The reason trail is what
lets the next person diverge safely, and it is the single most reusable
artefact the process produces — the modules in this playbook are mostly
distilled decisions.

**Status lives in the task files.** Not in an index, which is the shared file
that one-task-per-file exists to avoid.

## What caps parallelism

Not the number of ready tasks — **file overlap**. Two ready tasks that both
touch one controller are one task with extra steps. The board computes the
overlap and warns; splitting hot files is real work that buys real parallelism.

## What a task file has to contain

Enough that a competent person who was not in the conversation can execute it
without making a judgement call somebody has already made. In practice: the
files it will touch, the shape of the change in each, the acceptance test, its
dependencies, and its size. If it cannot name the files, it is not ready.

## Adapting it

The parts that transfer to any product: one file per task, a derived board,
frozen specifications with a departure tier, dispositions on findings, and
append-only decisions with ids.

The parts that are Qori's: the specific front-matter fields, the stream names,
and the size letters. Do not copy those without reading what they are for.
