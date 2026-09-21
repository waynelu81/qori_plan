# Task reports

> What a worker hands back when they finish, or when they stop.

[Process](../../PROCESS.md) | Board: `php artisan qori:tasks` | [Tasks](../)

## Why these exist

A task file says what to build. It does not say what happened when somebody
built it — which specifications turned out to be wrong, what could not be
verified, what the person noticed on the way past. That information reaches
whoever wrote the plan or it is lost, and running the same task with four
different developers made the loss obvious: they each found a different subset
of the same specification defects, and none of it was written anywhere the next
person would look.

A report is the channel back. One per attempt.

## Where they go

```
docs/planning/tasks/reports/
  T-009-2026-09-09-wayne.md        one attempt, one file, committed
  evidence/                        screenshots and captures, gitignored
```

**Naming:** `T-###-YYYY-MM-DD-<owner>.md`. Two people attempting the same task,
or the same person attempting it twice, produce two files. Never overwrite one:
a second attempt that disagrees with the first is the most useful thing in this
directory.

**Evidence is not committed.** Screenshots go in `evidence/` and are gitignored
— they are for the reviewer reading the report on the machine that produced it,
and a repository full of PNGs of a dialog box helps nobody six months later.
Reference them by relative path (`evidence/T-009-archive-dialog.png`); a reader
without the file loses a picture, not the argument. **So the report must stand
on its own in words.** If an image is carrying the finding, describe the finding.

## Which template

| Situation                                       | Template                                     | Task status afterwards |
| ----------------------------------------------- | -------------------------------------------- | ---------------------- |
| Finished it                                     | [`TEMPLATE.md`](TEMPLATE.md)                 | `done`                 |
| Stopped: the spec was wrong about what to build | [`RESCOPE-TEMPLATE.md`](RESCOPE-TEMPLATE.md) | `rescope`              |

**A re-scoped task is not reset to `ready`.** It stays `rescope` until planning
rewrites the spec. A worker who resets it has thrown away the signal — and an
instruction telling them to "reset the tasks you did" does not apply to a task
they deliberately did not do. This is worth stating because it has already
caught somebody out.

## The one rule that decides between them

**Scope is the contract. Acceptance is a checklist written from it.**

If an Acceptance line asks for something the Scope section excludes, or names a
finding the specified design cannot produce, that is a **defect in the task**:
record it under Notes, satisfy the Scope, and say in the report that the line
was wrong. It is not a re-scope, because nothing about what gets built changed.

Re-scope when **what must be built** changes: the approach cannot work, a
premise about the codebase is false in a way that changes the design, or
satisfying the Scope would require a decision nobody has made.

Wrong lang key names, a test file called something else, a missing helper the
Code section did not need — all Notes. None of them are re-scopes.

## Every finding ends in a disposition

"Found, not fixed" was the most useful section and the least acted on: 102
bullets across 37 reports, three of them repeated in two or three reports each
because nothing had a task and nobody was counting. From reports dated
**2026-09-15** on, every bullet under that heading ends in one of three tags,
and `TaskBoardTest` refuses a report that leaves one off:

| Tag                    | Means                                                                                                                    |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `→ T-###`              | An existing task owns it. Add a line to that task if it does not already say so.                                         |
| `→ draft T-###`        | It needs a task, and you wrote the draft — `php artisan qori:tasks --new <stream> <slug>` — with the finding in its Why. |
| `→ decided: <why not>` | It is not worth a task, and this is the reason. A later reader can disagree with a reason; they cannot with silence.     |

The tag is the last thing in the bullet. Older reports are not rewritten:
`php artisan qori:tasks` prints how many of their bullets are still untriaged,
and that number is the stream owners' backlog.

## What a report is for, and what it is not

It is for the person who wrote the spec. It answers: did this work, what was
wrong with what I gave you, and what should I not do again.

It is **not** a commit message, a changelog, or a summary of the diff. `git log`
holds those and holds them better. A report that lists every file it touched and
says nothing about the specification has told the reader nothing they could not
run `git status` for.
