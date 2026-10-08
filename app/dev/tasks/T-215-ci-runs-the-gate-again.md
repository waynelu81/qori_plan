---
id: T-215
title: CI runs the gate again
stream: workflow
status: doing
owner: claude
estimate: S
depends: none
blocks: none
---

# T-215 — CI runs the gate again

> **Written on 8 October 2026** from the independent review of 6 October (§4)
> and the fixup of 21 September, on the owner's word the same day ("yes, please
> pick up the next task"). Brought to ready from the code and claimed in one
> step.

## Why

GitHub's `tests` workflow has failed on every push to `main` since
8 September. The last green run was `f225cd1` on 7 September. From `064cc10`
(T-081, 14 September) on, every run stops at "Setup Node", because
`.github/workflows/tests.yml` reads `node-version-file: .nvmrc` and the file
was never committed. T-081's Files table listed it; `fixups.md` has carried the
line since 21 September. Laravel Cloud deploys on push without waiting for CI,
so the only gate that actually ran on those deploys was the pre-push hook, which
skips the formatter, `vue-tsc` and the build. The beta gate "`ci:check` green
from a clean checkout" cannot be ticked while this stands.

Afterwards a push to `main` and every pull request run the whole gate again:
the install, the build and `composer ci:check` from a clean checkout.

## Decisions taken to make this specifiable

Brought to ready on 8 October 2026, from the code.

**`.nvmrc` says `24`, not the `22` T-081 listed.** T-081's report says
`engines.node` is `>=22` because "the owner's machine runs Node 24", and it
picked 22 for CI. Nothing actually runs 22: the owner's machine runs 24.21, and
`decisions.md` records that Laravel Cloud runs Node 24. `tests.yml`'s own rule
for PHP is that testing a version nothing runs would be testing the wrong
thing. `engines.node` stays `>=22`, the floor `vite-plus` accepts
(`^22.18.0 || >=24.11.0`), and README's "Node 22 (`.nvmrc`)" becomes Node 24.

**Every step after "Setup Node" has never run under this workflow, so it is
proved before it is trusted.** A fresh clone runs the workflow's steps in order
on this Mac: copy `.env.example` to `.env`, `composer install`, `npm ci`,
`key:generate`, `wayfinder:generate --with-form`, `npm run build`, then
`composer ci:check` on its own test database. Whatever breaks there is fixed in
this task.

**The timeout and its comment follow the suite as it is now.** "The gate takes
about four minutes" was true on 14 September. On 8 October the serial suite
alone took 6 min 5 s locally (1,512 tests), and a hosted runner is slower.
The timeout is set from the clean-clone run, with room.

**The stale comment above "Run CI Checks" loses "the board rules".** The board
moved to `qori-plan` on 21 September and `composer ci:check` no longer runs
it.

**The real run comes from GitHub, on the owner's word.** A push to `main`
deploys production, and a pull request runs the workflow without deploying.
Which one, and when, is the owner's call. The task is done once one GitHub run
of `tests` passes and is read.

**Dependabot's PR #2 (actions/cache 4 → 6.1) is out.** Once CI is green it can
be rebased and judged on its own run. Merging it on GitHub is a push to `main`,
which deploys.

## Preconditions

None.

**Data this task verifies against:** the GitHub run of `tests` for the commit
that carries the fix, read with `gh run view`.

**Equipment:** None; `gh` reads the runs.

## Scope

**In:**

- `.nvmrc`.
- `tests.yml`'s timeout and comments, and whatever the clean-clone run shows
  the workflow needs.
- README's Node line.
- Deleting the fixup line.

**Out:**

- The pre-push hook's coverage (formatter, `vue-tsc`, build) and its exit
  without `vendor/`.
- Dependabot's PR #2.
- `qori-plan` getting CI or hooks of its own.

## Files

| Path                         | Change | Notes                                      |
| ---------------------------- | ------ | ------------------------------------------ |
| `.nvmrc`                     | new    | `24`                                       |
| `.github/workflows/tests.yml` | edit   | timeout and comments; what the run shows   |
| `README.md`                  | edit   | Node 24                                    |

Flows: none — no call chain changes.

## Database

None.

## Code

None.

## Copy

None.

## Routes

None.

## Tests

None new. The proof is the clean-clone run of the workflow's steps, then the
first GitHub run.

## Acceptance

- [ ] `.nvmrc` is committed, and README names the same version
- [ ] A fresh clone runs the workflow's steps in order to a green `composer ci:check`
- [ ] `tests.yml`'s timeout and comments say what is true on 8 October
- [ ] One GitHub run of `tests` for the fix passes, read with `gh run view`
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Node 22 or 24?~~ **Answered from the code, 8 October 2026:** 24
  (Decisions).
- ~~Push or pull request for the first run?~~ **Answered 8 October 2026:**
  the owner's call at the time (Decisions).

## Re-scope log

None.

## Notes

The runs from 8 to 12 September failed at a step called "Setup Application",
which T-081 replaced. They are history, not a second cause.
