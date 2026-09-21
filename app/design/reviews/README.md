# Design review

> How a design gets looked at on purpose, by whom, against what, and what
> happens to what they find.

[Current plan](../../../PLAN.md) | [Planning index](../README.md) | [Process](../PROCESS.md) | [Lanes](lanes/) | [Redesign brief](../ui-redesign.md)

## Why this exists separately from tasks

Building and reviewing fail differently, so they are organised differently.

A **task** is one commit's worth of work, specified so completely that somebody
who has never seen the codebase produces the same result. Its spec is frozen
because the person who wrote it is not the person who will do it.

A **pass** is a look at what is already there. Nothing is frozen, because the
person who scopes a pass is the person who runs it, and the whole value is in
what they did not expect to find. A pass produces **findings**, and a finding
that needs code becomes an ordinary task in the [`design`](../streams/design.md)
stream. That is the join between the two systems, and it is the only one.

So: streams and tasks answer _what should we build_. Passes and lanes answer
_is what we built any good_, and hand the answer back as tasks.

## What starts a pass

**The owner asks for one.** That is the whole trigger.

Not a schedule, not a commit hook, not a release gate. A weekly rhythm produces
reports with nothing in them, and a per-commit trigger is the one people switch
off in a busy week. Qori has one person deciding what the product should look
like, and a review nobody asked for is a review nobody reads.

## The seven lanes

A lane is a question about the design, paired with the equipment needed to
answer it. They are split by equipment rather than by screen, and that split was
learned the expensive way: `T-003` bundled mobile, contrast and keyboard into
one task, and its report concluded that these were _"three passes with three
different equipment requirements. Two of them need only a renderer; one needs an
input device."_ A lane that needs a thing you do not have should fail loudly at
the start, not two thirds of the way through.

| Lane                              | Asks                                                      | Needs                          |
| --------------------------------- | --------------------------------------------------------- | ------------------------------ |
| [surface](lanes/surface.md)       | Does every screen look like the same product?             | A renderer                     |
| [state](lanes/state.md)           | Does it hold up when the data is not friendly?            | Fixtures, a renderer           |
| [responsive](lanes/responsive.md) | Does it work at the widths people actually use?           | A resizable renderer           |
| [contrast](lanes/contrast.md)     | Can it be read, in both themes?                           | The stylesheet                 |
| [keyboard](lanes/keyboard.md)     | Can it be operated without a mouse?                       | A **visible** browser          |
| [copy](lanes/copy.md)             | Does it say true things, in Qori's words?                 | `lang/`, the terminology layer |
| [journey](lanes/journey.md)       | Can a person get through the loop without being stranded? | A driveable browser, fixtures  |

A pass names the lanes it is running. Running one lane is a pass. Running all
seven is a pass. What is not allowed is a pass that ran three lanes and reports
as though it covered the design.

## Evidence

Most lanes start from a screenshot run:

```bash
php artisan qori:design-review            # everything, both widths, both themes
php artisan qori:design-review --lane=state
```

That is [`docs/tinker/design-review.md`](../../tinker/design-review.md). It
writes a run directory named for the commit it was taken at, and the images are
gitignored — **so a pass has to stand on its own in words**, exactly as a task
report does. Reference a screenshot by its path within the run and describe what
it shows; a reader without the file should lose a picture, not the finding.

The harness is evidence, not judgement. It can tell you a page renders; it
cannot tell you the page is good.

## Handing a pass to somebody else

[`prompt-design-review.md`](../../../prompt-design-review.md) at the repository
root is the brief to paste. It is the sibling of
[`prompt-template.md`](../../../prompt-template.md), which does the same job for
building rather than reviewing, and it is a template for the same reason: when a
pass goes wrong in a way that brief could have prevented, the fix belongs there.

## Writing a pass

One file, `passes/R-###-YYYY-MM-DD-slug.md`, from [`TEMPLATE.md`](TEMPLATE.md).

**One file, not a spec and a report.** Tasks split those two because a task is
handed between people and a reviewer needs to check that what was asked for and
what happened agree. A pass is scoped and run by the same person on the same
afternoon, so a second document would be ceremony rather than a check. The file
starts as scope and gains findings; `ls passes/` is the thread.

Passes are numbered `R-001` upward and never renumbered. A second look at the
same lanes a month later is a new pass, and the old one stays exactly as it was
— two passes disagreeing is the most useful thing in this directory.

## What a finding is

| Severity    | Means                                                                                           |
| ----------- | ----------------------------------------------------------------------------------------------- |
| **blocker** | Contradicts the release gate or the interaction contract. Somebody is stopped, misled or stuck. |
| **defect**  | The design is wrong here, but the path still works.                                             |
| **polish**  | Noticed and worth remembering. Not worth a task yet.                                            |

Every finding says **what is true now** and **what should be true instead**. A
finding that only says something is ugly cannot be turned into a task, and a
finding that proposes a fix without naming the problem cannot be argued with.

## What happens to findings

| Finding                          | Goes to                                               |
| -------------------------------- | ----------------------------------------------------- |
| Needs code                       | A task in the [`design`](../streams/design.md) stream |
| Changes what the product intends | [`decisions.md`](../decisions.md), then maybe a task  |
| Already covered by an open task  | A note on that task, and the finding cites it         |
| Nothing to do                    | Stays in the pass, marked accepted, with the reason   |

**Do not fix findings inside the pass.** A pass that turns into a working
session stops being a record of what the design was on that day, which is the
one thing it is for. The exception is a one-line copy fix in `lang/`, and even
that gets written down.

A pass is finished when every finding has a disposition. Not when every finding
is fixed — those are different, and conflating them is how a review turns into
an open-ended polish week the redesign brief explicitly refuses.
