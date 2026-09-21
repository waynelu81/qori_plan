---
stream: operations
---

# Stream: operations

**Goal.** Know when Qori is broken before a customer tells us, and be able to
put it back.

**Done when.** Payment/fulfilment mismatch, webhook failure, bounce and queue
age all raise an alert; a restore has been rehearsed at least once; and the
query plans for the hot paths have been looked at rather than assumed.

**State.** Sentry receives `Log::error`, and since 11 September 2026 it does so
from Laravel Cloud rather than from a dev machine. The queue is the `deferred`
driver, which runs work after the response and only when it succeeded — fine for
now, and not a worker. Nothing alerts. No restore has been attempted.

**The scheduler runs in production**, switched on by the owner on 11 September
2026, the same day `T-010` registered Qori's first scheduled command. Nothing
runs `schedule:run` locally, so the purge sweep still has to be driven by hand
here. One trap survives the switch and is worth re-reading before adding a
second command: Cloud captures `php artisan schedule:list` **at deploy time** to
decide when to wake the environment, so a change to a task's frequency does
nothing until the next deployment. See
[`../release-prerequisites.md`](../release-prerequisites.md).

**One question that becomes a bug the day compute is scaled.** Cloud runs the
scheduler on every replica of the cluster it is enabled on, and a task only
runs once across them if it says `onOneServer()`. `qori:series:purge` does not
say it. Two replicas would sweep the same Series twice at the same instant:
harmless in the ordinary case, because the second run finds the Episodes
already gone, and a race on the file deletion and the `purged_at` write in the
case that is not. Cheap to fix and currently costing nothing, which is exactly
how it will be missed. It belongs to whoever answers `T-018`, since that is
where the compute topology gets decided.

## Tasks, in order

1. `T-041` — The docs name the database Qori actually has: the recipes opened
   a connection that no longer existed, and running one found `T-042`
2. `T-042` — Episodes are rows, and four places still say they are embedded
3. `T-056` — Finish the Collaborator rename in the code that reads it
4. `T-060` — Domain enums live in `app/Enums`; a layer's contract stays with
   the layer
5. `T-057` — A share controller receives the slug its signature declares
6. `T-047` — An Episode's position and the episode cap both read a stale count
7. `T-018` — Choose and document the production queue topology
8. `T-019` — Alert on the five failure modes that matter
9. `T-020` — Rehearse a database restore and write down what happened
10. `T-021` — Review indexes and query plans on the hot paths
11. `T-069` — One command resets the development database to one of three
    states — small, and asked for three times in one day
12. `T-070` — Starter-kit leftovers nothing uses are deleted
13. `T-117` — Episode writes count what the database holds: `T-047`'s review
    found publish, remove and reorder reading the same stale list, and two
    adds at once can share a position
14. `T-118` — The words the renames mangled are put right: a buyer still reads
    "Please agree to be peered before granting."
15. `T-147` — Every listener is registered once: discovery and
    `AppServiceProvider` both register `CreateGroupForNewUser`, so every
    sign-up runs it twice, and only its early return keeps that harmless

The small code-health items go first because each is a correctness bug rather
than an unknown, and each was found by the last one: `T-042` found `T-047`,
and `T-054` found `T-057` the first time a controller trusted its own
signature.

## Notes

`T-018` gates the campaign work: §9's sending caps assume batches that can
retry, and the `deferred` driver cannot retry anything. Nothing may be marked
`ShouldQueue` until this lands.
