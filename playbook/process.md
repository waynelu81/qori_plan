# The planning process

The system Qori uses. It is small, and its value is almost entirely in three
rules — nobody approves, a spec changes only in the open, and the board is
derived.

The live version, with the exact forms, is
[`../app/dev/PROCESS.md`](../app/dev/PROCESS.md); the tool that enforces it is
[`../bin/tasks`](../bin/tasks). What follows is why it is shaped this way.

## Three layers

| Layer | Holds | Changes |
| --- | --- | --- |
| **The plan** | Intent, state, release gates. Capped at 150 lines. | When intent or release state moves |
| **Streams** | Why one line of work exists, and in what order | When the ordering or the reasoning changes |
| **Tasks** | One file each, specified as far as whoever builds it needs | Constantly |

**The board is derived, never committed.** It is rendered locally from the task
files. Qori committed it once; every claim or close rewrote its counts and
re-sorted its tables, so two people finishing on the same day conflicted in a
file neither had edited.

## The rules that carry the weight

**Nobody approves.** Whoever picks a task up brings it to ready and builds it.
The product owner is who you ask — for a product call, an account, a real
sign-in — and the work carries on around the question rather than waiting for
the answer. Qori ran the other way first: every stream had an owner, all of
them the same person, and every draft-to-ready, every unblock and every spec
rewrite queued on that one desk. By the day it was reversed, 69 tasks were
drafts against 8 ready, and specification rather than building was what held
the product back.

**Release checklist is not a prerequisite.** Privacy policy, terms, pricing,
production configuration and a vendor's app review go on the release gate and
never hold a task. Where one needs a place in the product — a disclosure line
before a vendor's consent screen — build the place now and write the words
before release. Qori let several of these sit in task specs as open questions,
and each one held code that did not depend on it.

**A ready specification changes in the open, never silently.** If the code
disagrees with it, whoever found it writes down what they found, rewrites the
part that changed, and carries on; they ask first only when the change alters
what a person sees or contradicts a recorded decision. The log is the point:
a spec that quietly stopped matching the code is one the next reader trusts
and is wrong about, and a change with no record is one nobody can review.

**Below that sits a departure tier.** A file the specification forgot may be
touched if it is added to the task and listed in the report. Stopping for the
twelfth file of an eleven-file spec taught nobody anything.

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

No open question for the person who will build it. When that is the person
writing it, the files, the decisions, the scope and the tests are enough. When
it is written for somebody else, it names things — column names, method
signatures, test names — so two people given it would build the same thing.
Either way, if it cannot name the files, it is not ready.

## Adapting it

The parts that transfer to any product: one file per task, a derived board,
no approval step, release checklist kept off the dependency graph,
specifications that change openly with a departure tier below them,
dispositions on findings, and append-only decisions with ids.

The parts that are Qori's: the specific front-matter fields, the stream names,
and the size letters. Do not copy those without reading what they are for.
