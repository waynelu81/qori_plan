---
pass: R-000
date: YYYY-MM-DD
reviewer: your-name
lanes: surface, state
commit: 0000000
run: docs/design-review/YYYY-MM-DD-HHMM-0000000
status: open
---

# R-000 — one line naming what was looked at

> Copy to `passes/R-###-YYYY-MM-DD-slug.md`. Keep every heading. A section with
> nothing in it says **None**, so a reader can tell "nothing here" from "not
> considered".
>
> Read [`README.md`](README.md) first if you have not. `status` is `open` while
> findings still lack a disposition, and `closed` when every one of them has
> one — which is not the same as every one being fixed.

## Scope

**Lanes run:** > Name them. Each one links to its file in `lanes/`.

**Lanes not run, and why:** > The most useful line in this document when it is

> not empty. A pass that skipped `keyboard` because the browser pane was hidden
> has covered less than a pass that ran it, and a reader who assumes otherwise
> will trust a gap.

**Surfaces:** > Everything, or the ones that changed. If it is a subset, say

> what put those screens in scope and what is therefore unexamined.

## Evidence

> The run directory and the command that made it. The images are gitignored, so
> anything carrying a finding gets described in words below rather than pointed
> at.

```bash
php artisan qori:design-review
```

| What           | Where                        |
| -------------- | ---------------------------- |
| Screenshot run | `docs/design-review/…`       |
| Gate           | `composer ci:check` — result |
| Anything else  |                              |

## Findings

> One row per finding. **What is true now** and **what should be true instead**,
> both concrete enough to become a task without another conversation.
>
> `Where` is a screen name from the run (`650-many-series-index`) or a file and
> line. Severity is blocker, defect or polish — see the README.

| #   | Lane | Severity | Where | Now | Should be | Disposition |
| --- | ---- | -------- | ----- | --- | --------- | ----------- |
| F-1 |      |          |       |     |           |             |

**None** is a real answer and worth writing when it is true. It is rarely true
on a first pass over a surface.

## Held up

> What the pass looked at and found correct. Not padding: a lane that reports
> only problems reads as a list of everything wrong with the product, and the
> next reader cannot tell what has already been checked and is fine. Keep it to
> the things somebody might otherwise re-examine.

## Could not see

> What this pass had no way to check, and why — no visible browser, no device,
> no data at the right shape, a state the app does not hold still for. The
> harness cannot photograph a loading skeleton or a server failure; if those
> were in scope, say they were not seen.

## Disposition

> Where each finding went. One line each, with the task id once it exists.

| #   | Went to | Note |
| --- | ------- | ---- |
| F-1 |         |      |

## Notes

> Anything learned about reviewing itself — a check worth adding to a lane, a
> fixture the state matrix is missing, a screen the harness should capture and
> does not. This is how the lanes get better rather than staying as first
> written.

None.
