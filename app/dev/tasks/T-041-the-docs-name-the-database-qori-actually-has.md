---
id: T-041
title: The documentation names the database Qori actually has
stream: operations
status: done
owner: claude
estimate: L
depends: none
blocks: none
---

# T-041 — The documentation names the database Qori actually has

## Why

Qori moved to Neon Postgres on 8 September 2026. **The documentation still says
MongoDB Atlas in about a hundred places**, and the worst of them are not
footnotes.

`docs/project-plan.md` §20 opens "**Database:** MongoDB Atlas via the
`mongodb/laravel-mongodb` package — **no SQL anywhere in the app.**" `CLAUDE.md`
sends every agent to that file for architecture, so the single document an agent
is told to trust describes a database this product does not have.

`docs/tinker/` is worse in a different way, because it does not merely mislead —
it fails. Every recipe there opens `DB::connection('mongodb')`, a connection
that no longer exists, so the commands error. That directory's own README says a
recipe that no longer runs is worse than no recipe, because it costs the reader
the debugging time to find out.

And this blocks something concrete. `T-020` rehearses a database restore and
writes down what happened. Rehearsing a restore against a runbook that describes
an Atlas cluster is not a rehearsal.

## Decisions taken to make this specifiable

**The rule is: does this sentence describe how Qori works, or record a decision
that was made and reversed?** The first is wrong and gets fixed. The second is
the reason trail and gets kept.

That distinction decides every file below and it is not cosmetic. Deleting the
Mongo history would strip the reason from rules that still bind — `CLAUDE.md`
warns that a jsonb `'array'` cast is "the exact inverse of the old Mongo rule,
where the same cast was trap 8", and that warning only works if the old rule is
still on record somewhere.

**The archive is never touched.** `docs/planning/archive/PLAN-2026-09-08.md`
holds 45 references and is a byte-for-byte copy of the plan as it stood.
`docs/planning/README.md` says do not silently rewrite it, and this task does
not.

**A premise can go stale while its conclusion survives.** Several passages argue
for a design _because_ "MongoDB has no foreign keys". Postgres has them, so the
premise is now false — and in most of these cases the conclusion is still right
for a different reason. `Group::seatsUsed()` is a live count because no foreign
key maintains a denormalised counter, which is true of Postgres too. **Each of
these must be re-argued, not find-and-replaced.** Where the conclusion does not
survive, that is a finding for the report, not a silent edit.

**Superseded blocks get a dated header, not deletion.** The runbook's numbered
traps and the observability TTL-index section describe a system that no longer
exists. They become a marked, dated section saying so, with a pointer to the
present-day rule that descends from each — which is more useful than either
leaving them to mislead or deleting the reasoning.

## Preconditions

None beyond a clean checkout. **Check the board first**: this touches
`docs/planning/` widely and another task in flight may hold one of these files.

## Scope

**In:**

- Every passage describing Qori's database, queue, transactions, foreign keys or
  hosting in the present tense.
- Every `docs/tinker/` recipe that will not run.
- The runbook's Mongo-era traps, marked as history rather than deleted.

**Out:**

- `docs/planning/archive/`. Never.
- `decisions.md` and `status-history.md`, which are the record of what was
  decided and when. The Mongo entry in `decisions.md` is already struck through
  and marked superseded, which is exactly right.
- The four references in `CLAUDE.md` and `.cursor/rules/` that name Mongo to
  explain a rule that still binds. Each says what replaced it; leave them.
- Renaming anything in code. This is documentation.
- Rewriting §20's _reasoning_ about why Postgres won. `decisions.md` holds it.

## Files

| Path                                            | Refs | Treatment                                                                   |
| ----------------------------------------------- | ---- | --------------------------------------------------------------------------- |
| `docs/project-plan.md`                          | 8    | §20 database, §21.3 foreign keys, §21.4 embedding, §22 Sanctum and sessions |
| `docs/tinker/README.md`                         | 10   | The connection check, the environment table, `DB_URI`                       |
| `docs/tinker/series.md`                         | 3    | Rewrite the raw-document queries as `jsonb`                                 |
| `docs/tinker/accesses.md`                       | 2    | Same                                                                        |
| `docs/tinker/auth.md`                           | 2    | Reset tokens are a table                                                    |
| `docs/tinker/groups.md`                         | 1    | `listIndexes()` → `pg_indexes`                                              |
| `docs/planning/engineering-runbook.md`          | 8    | Traps marked as the Mongo era; "How to run" corrected                       |
| `docs/flows/auth.md`                            | 3    | Collections → tables                                                        |
| `docs/flows/campaigns.md`                       | 1    | Re-argue the live count                                                     |
| `docs/flows/groups.md`                          | 1    | Same                                                                        |
| `docs/flows/series.md`                          | 1    | `Episode` extends the ordinary Eloquent model                               |
| `docs/flows/storage.md`                         | 1    | Backup wording                                                              |
| `docs/planning/operations-and-observability.md` | 3    | Atlas sizing; the TTL-index section marked superseded                       |
| `docs/planning/risk-register.md`                | 3    | QORI-004 and the port collision, both resolved                              |
| `docs/planning/billing-and-plan-behaviour.md`   | 1    | Pruning no longer gets a TTL index for free                                 |
| `docs/planning/reporting-social-and-flags.md`   | 1    | "no constraints, no triggers" is false now                                  |
| `tests/Feature/DocumentationTest.php`           | new  | 3 cases                                                                     |

**Not touched, deliberately:** `docs/planning/archive/PLAN-2026-09-08.md` (45),
`docs/planning/decisions.md` (18), `docs/planning/status-history.md` (24),
`CLAUDE.md` (2), `.cursor/rules/` (4).

## Database

None. This task changes no schema and no code.

## Code

None, beyond the test below.

## Copy

None. No user-facing string mentions a database.

## Routes

None.

## Tests

Prose cannot be unit tested, but "does this file claim we run Mongo" can be, and
that is the property worth holding — the docs drifted for three days without
anything noticing.

**New: `tests/Feature/DocumentationTest.php` — 3 cases**

1. `test_no_live_document_claims_qori_runs_mongodb` — walks `docs/`, `CLAUDE.md`
   and `.cursor/rules/`, fails on `mongo` or `atlas` case-insensitively, with an
   allow-list of the five paths named above **and a reason string against each**.
   Names the file and line on failure.
2. `test_every_tinker_recipe_uses_a_connection_that_exists` — greps
   `docs/tinker/` for `DB::connection('…')` and asserts each named connection is
   configured. This is the case that catches a recipe which cannot run.
3. `test_the_allow_list_only_holds_files_that_exist` — so a renamed archive does
   not silently widen the exemption to nothing.

**Changed:** none expected.

## Acceptance

- [x] No document describing Qori today names MongoDB or Atlas
- [x] Every `docs/tinker/` recipe names a connection that exists
- [x] Superseded reasoning is marked and dated, not deleted
- [x] Every "MongoDB has no foreign keys" argument is re-argued or removed, and
      any conclusion that did not survive its premise is in the report
- [x] The archive, `decisions.md` and `status-history.md` are untouched
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**Running a recipe rather than reading it found a real bug.** The rewritten
`docs/tinker/series.md` asserted there is no `episodes` table. There is one,
with a foreign key and thirty-eight rows, and `Series::episodes()` is a plain
`hasMany`. Four places still said Episodes were embedded, and two of them were
the stated reason `SeriesService` takes no transaction around a delete-then-
renumber. `T-042` covers it; `QORI-004` was rewritten to name it.

**One recipe was wrong on its first draft too.** `inet_server_port()` answers
5432, because that is the port inside the container; the host maps 5433 to it.
The recipe now reads the port from config, which is the number that tells you
whose database you reached.

**Two sentences were fixed slightly beyond the Mongo sweep**, because the Mongo
claim and the embedding claim were the same sentence in `docs/flows/series.md`
and `docs/project-plan.md` §21.4. Correcting half of a false sentence is not an
option.

`PLAN.md`'s stream table lists seven streams and `onboarding` is not among them,
although it has a stream file and six tasks. Unrelated to this task, noticed
while placing it, and worth a line from whoever next edits that file — which is
capped at 150 lines and currently sits at 148.
