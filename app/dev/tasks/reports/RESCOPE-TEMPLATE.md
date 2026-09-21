---
task: T-000
owner: your-name
date: YYYY-MM-DD
outcome: rescope
gate: not run / 000 tests
---

# T-000 — re-scope

> Copy to `T-###-YYYY-MM-DD-<owner>.md`. You stopped. This explains why, well
> enough that planning can rewrite the spec without asking you a question.
>
> Before writing it, check the rule in [`README.md`](README.md): an Acceptance
> line that contradicts the Scope section is a **defect**, not a re-scope. Fix
> the Scope's work, record the defect in Notes, and file the other template.

## What the specification assumed

> Quote it. Which section, and what it said would be true.

## What is actually true

> The evidence. A file and a line, a command and its output, a test that fails.
> Not "it seems that" — show it.

## Why this changes what gets built

> The test for a re-scope. If the answer is "it does not, it just changes what I
> called something", this is not a re-scope and the wrong template is open.

## How far you got

> What is in the working tree right now, and whether it runs. Say clearly
> whether you left the partial work in place or removed it — the next person
> needs to know which they are looking at, and both are legitimate.

## What planning has to decide

> The question, put so it can be answered. Not "please advise" — a specific
> choice with the options you can see, and your recommendation if you have one.

## What you would keep

> If any of the work survives whatever is decided, say which part and why. A
> re-scope that throws away a correct implementation of the wrong thing has
> cost more than it needed to.
