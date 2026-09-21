---
task: T-000
owner: your-name
date: YYYY-MM-DD
outcome: done
gate: 000 tests, 0000 assertions
---

# T-000 — report

> Copy to `T-###-YYYY-MM-DD-<owner>.md`. Keep every heading. A section with
> nothing in it says **None**, so a reader can tell "nothing here" from "not
> considered".

## Outcome

> One paragraph. What now works that did not, in the terms a reader who has not
> seen the diff would use. Not a list of files.

## Verified

> How you know. Say which of these you actually did, and say plainly which you
> could not.

| What                             | How | Result |
| -------------------------------- | --- | ------ |
| `composer ci:check`              |     |        |
| The defect actually failed — how |     |        |
| State-specific browser walk      |     |        |

> **The defect actually failed** — the first row after the gate, because a fix
> for a bug nobody reproduced is a guess with a test attached. Say how you
> made it fail before the change: the failing test's message, the wrong page,
> the wrong row. If it never failed for you, say so — that is a finding about
> the spec.
>
> **State-specific browser walk** — not "light and dark" and not "360px", which
> were the rows here before and were ticked from habit. Name the state the
> change is about (a disconnected Group, an unverified person, an archived
> Series) and say you walked _that_ state in a browser, at the width where it
> matters. Both themes and both widths only when the change is visual.

**Could not verify:** > What you had no way to check, and why — no browser in
the session, no vendor credentials, no data at the right scale. This is the most
useful line in the report when it is not "nothing", and the least honest report
is the one that omits it. A reviewer who knows the gap can close it; a reviewer
who assumes coverage cannot.

## Where the specification was wrong

> One entry per defect, whether or not you worked around it. This is the point
> of the report. **Say which section**, quote what it said, and say what was
> actually true.

| Section | Said | Actually |
| ------- | ---- | -------- |
|         |      |          |

**None** is a real answer, and worth writing when it is true.

## Departures

> Anything you did that the specification did not ask for, and why. Extra test
> cases, a rename, a fix you made in passing, a file touched that the Files
> table did not list (say it is under "Added during execution" in the task). A
> reviewer comparing the diff to the spec will find these anyway; finding them
> here first is the difference between a judgement call and a surprise.

## Found, not fixed

> Things you noticed that belong to another task or to nobody yet. Do not fix
> them here — that is how a task grows until nobody can review it.
>
> **Every bullet ends in a disposition**, so a finding is acted on the day it
> is written rather than counted in a backlog (`qori:tasks` prints how many
> older ones still wait). One of three:
>
> - `→ T-###` — an existing task owns it; add a line there if it does not say so
> - `→ draft T-###` — it needs a task, and you wrote the draft
>   (`php artisan qori:tasks --new <stream> <slug>`) with the finding in its Why
> - `→ decided: <why not>` — it is not worth a task, and this is the reason
>
> A test refuses a report dated from 2026-09-15 with a bullet that ends in
> none of them. The tag goes at the very end of the bullet, after the last
> sentence.

- … → T-000

## Evidence

> Screenshots under `evidence/`, referenced by relative path. Describe what each
> one shows in words: the file is gitignored and the reader may not have it.

## Files

> Created and modified, as two lists. Last, because it is the least useful part
> of this document — `git status` says it better and always agrees with reality.
