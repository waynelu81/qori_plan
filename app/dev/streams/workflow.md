---
stream: workflow
---

# Stream: workflow

**Goal.** Several developers, people and coding agents, can work on Qori at
once without treading on each other: claims are visible, files do not collide,
the gate can run on every machine, and the documents tell the truth.

**Done when.** A new developer goes from clone to a green gate with one
command; two people can close tasks on the same day without a merge conflict
in a file neither edited; every rule that prose states is checked by a test;
and the docs a task points at describe the code as it is.

**State, 14 September 2026.** A review of the planning and workflow for
several developers (thirteen agents, six dimensions, every finding refuted or
confirmed against the repo) found the primitives right and the multi-writer
pieces unexercised: a committed generated board, one shared test database,
three hot files every stream edits, rules mirrored by hand in two places, and
a report backlog nobody triages. The owner asked for everything except a
branch-and-PR flow to be built. The board left git the same day, and the
four packages were built at once in four worktrees, each against its own
test database, and merged that evening — the first time the repo carried
four lines of work at once. `T-083` ran a second time from the merged main
after its worktree was cut from the stale remote head.

## Tasks, in order

1. `T-080` — Planning mechanics for several hands: the parser reads every
   path and expands globs, `blocks:` is derived, streams have owners and no
   status, findings get dispositions, and the rules live in one place
2. `T-081` — Clone to green, one database per checkout, hooks and CI
3. `T-082` — One source of conventions, and docs that tell the truth
4. `T-083` — Split the Series hot files
5. `T-119` — The core loop runs in a browser on demand: one command rebuilds
   a database of the developer's choosing, serves from it, and drives
   register → verify → setup → Series → Episode → ready through Playwright,
   headless or on screen
6. `T-120` — The Peer half of the loop runs in a browser: a stranger with the
   link gets a code and finishes the Series; a learner registers and is
   given access; `--pause` holds each screen for a person watching
7. `T-121` — A Peer pays for a Series in a browser: Stripe test-mode
   Checkout end to end, once a sandbox connected account exists
8. `T-145` — The classroom loop runs in a browser: a far-timezone Peer misses a
   class, receives one email and finds the recording and the materials; the
   beta-gate evidence for `D-031`

The four were cut by file ownership rather than by topic, so they can run at
once in separate worktrees: `T-080` owns the planning tooling and process
documents, `T-081` the build and CI files, `T-082` `CLAUDE.md`, the Cursor
rules, the convention tests and the flow docs, and `T-083` the Series routes,
controller and service. Where one needs a change in another's file, the task
says so and the merge does it.

## Not in this stream

A branch-per-task, pull-request flow with a ruleset on `main`. The review put
it first; the owner left it out on 14 September 2026. Everything here works
with direct commits to `main` and would work better with branches.
