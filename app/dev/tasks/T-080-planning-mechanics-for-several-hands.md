---
id: T-080
title: Planning mechanics for several hands
stream: workflow
status: done
owner: claude
estimate: L
depends: none
blocks: none
---

# T-080 — Planning mechanics for several hands

## Why

The review of 14 September 2026 (`streams/workflow.md`) found the planning
primitives right and the multi-writer mechanics missing. Closing a task edits
the stream file, prepends to `decisions.md` at the same line and touches
`PLAN.md`, so two people finishing in one stream on one afternoon conflict in
prose. The Files-table parser reads one path per row and treats globs as
literal strings, so the collision test misses the rows most likely to collide.
Nothing acts on a "Found, not fixed" bullet (102 across 37 reports, three
findings repeated in two or three reports each with no task). Task ids are
picked by hand. Only the owner promotes drafts, and no stream has an owner.
`blocks:` is a hand-kept inverse of `depends:` and is already wrong in ten
places. The board left git in the commit that opened this task; this task
does the rest of the planning mechanics.

## Decisions taken to make this specifiable

**Status lives in task files only.** A stream file states its goal, its
done-when, and its tasks in order with a one-line reason each — never a
status word or strikethrough; the board says what is done.

**Every stream has an owner**, in front matter, and the owner is who rewrites
a rescoped spec, clears `blocked`, and arbitrates a file clash.

**Anyone may spec.** A draft may be claimed for speccing (`status: speccing`
is not a new status — use `owner:` on a `draft`), the sections written, and
the result offered to the stream owner; the owner's job becomes approving.

**A "Found, not fixed" bullet ends in a disposition** for reports dated from
2026-09-15: `→ T-###`, `→ draft T-###`, or `→ decided: <why not>`. Older
reports are counted as untriaged, not rewritten.

**`blocks:` is derived.** The renderer computes it from `depends:`; the
front-matter field stays for readers but a test asserts it agrees.

**Decisions get ids and append at the end.** `D-###` in the heading, cited by
id; new entries go under a dated heading at the end of `## Decisions`; the
five settled entries under "Open decisions" move below it.

## Preconditions

None. `T-081`, `T-082` and `T-083` run alongside in separate worktrees and do
not touch this task's files.

## Scope

**In:**

- `TaskBoard::files()` captures every backticked path in a row's first cell
  and expands globs against the repo; bare basenames are rejected by a test.
- `qori:tasks` gains `--new <stream> <slug>` (next id from the highest file,
  stub from the template, `status: draft`, `owner: unassigned`), prints an
  "Untriaged findings" count (report bullets without a disposition), a "Spec
  overlaps" section (ready tasks sharing a file with a task whose report is
  dated in the last seven days), and a warning when `ready` tasks number
  fewer than the target in `PLAN.md` ("ready ≥ 2 × active developers"; read
  the number from a `qori.planning.ready_target` config key defaulting to 4).
- `TaskBoardTest` cases: every backticked path is captured; a glob expands;
  a stream file carries `owner:`; a stream file holds no `~~` and no bold
  status word; every `T-###` a stream names exists and belongs to it;
  `blocks:` agrees with `depends:`; a `blocked` task has `## Blocked on`
  naming the thing and the person; a ready `L` task names its split or its
  `blocks:`; a report dated from 2026-09-15 has a disposition on every
  "Found, not fixed" bullet; a ready or doing task whose Files include a path
  under `app/Http`, `app/Services`, `app/Listeners` or `routes/` lists a
  `docs/flows/*.md` path or the line `Flows: none — <reason>`; every stream
  file appears in `streams/README.md`.
- `TEMPLATE.md` gains `## Decisions taken to make this specifiable` and
  `## Preconditions` (with fixed lines "Data this task verifies against" and
  "Equipment"), a "Spike" note for vendor-facing work, and a wiring checklist
  under Files; the required-section list covers ready and doing tasks only,
  so old done tasks do not fail. Acceptance order: status, board check and
  `npm run check:fix` precede the gate.
- `reports/TEMPLATE.md`: replace the theme/width rows with "The defect
  actually failed — how" and "State-specific browser walk"; the "Found, not
  fixed" section explains the disposition tags.
- `PROCESS.md`: the departure tier beside the re-scope rule (a file not in
  the table may be touched if added under "Added during execution" and listed
  under Departures; rescope stays for "what gets built changes"); streams are
  features and files are layers, keep the dependency rule; the speccing
  claim; the stream owner's duties; every commit, planning-only ones
  included, passes `npm run check`; before `done`, grep ready specs for every
  route, page, enum, lang key or class the work renamed and patch or rescope;
  a ready spec that names a vendor payload cites an observed response or a
  committed fixture under `tests/Fixtures/<vendor>/`; `PLAN.md` and
  `status-history.md` are the owner's. Add `ready ↔ blocked` to the diagram.
- `decisions.md`: ids, the five settled entries moved below `## Decisions`,
  append-at-end rule stated at the top, and a dated "Decisions needed" list
  under Open decisions with one line per draft that waits on the owner
  (read each draft's "Before this can be ready").
- Stream files: `owner: wayne` front matter on all ten, status words and
  strikethroughs removed, `streams/README.md` table listing every stream
  including onboarding, selling and workflow.
- `engineering-runbook.md`: a numbered "Spec traps" list from the reports
  (AppException on non-GET redirects back; Vue cannot read a lang key; a
  stale `url.intended` outranks the landing; a model instance is stale within
  one request once another instance of the row is written; `$attributes`
  defaults are raw storage values; RefreshDatabase never runs a migration's
  data step against real rows; `sometimes` skips every rule).
- Planning edits: `T-028` depends on `T-044`; `T-011`'s satisfied
  precondition struck with a date; three draft tasks written from repeated
  findings — `T-084` a stale intended URL survives another person's sign-in,
  `T-085` the public Series page still offers to buy when the Group is
  disconnected, `T-086` the dashboard rename card still says "Name your
  Group" once named; `docs/planning/reachability.md` added to
  `docs/planning/README.md`; the five ready tasks get a Flows line if the new
  rule needs one.

**Out:**

- A branch-per-task or pull-request flow, owner handles, `reviewed_by`, `pr:`
  — the owner left `T-001`-of-the-review out.
- Splitting `decisions.md` into files.
- Rewriting old reports' bullets.
- Any file owned by `T-081`, `T-082` or `T-083`.

## Files

| Path                                                          | Change | Notes                                               |
| ------------------------------------------------------------- | ------ | --------------------------------------------------- |
| `app/Support/TaskBoard.php`                                   | edit   | Parser, derived blocks, untriaged, overlaps, target |
| `app/Console/Commands/TasksCommand.php`                       | edit   | `--new`, the printed sections                       |
| `config/qori.php`                                             | edit   | `planning.ready_target`                             |
| `tests/Feature/TaskBoardTest.php`                             | edit   | The cases above                                     |
| `tests/Fixtures/planning/docs/planning/tasks/T-001-first.md`  | edit   | Fixture rows as the parser needs                    |
| `tests/Fixtures/planning/docs/planning/tasks/T-002-second.md` | edit   |                                                     |
| `tests/Fixtures/planning/docs/planning/streams/fixture.md`    | edit   |                                                     |
| `docs/planning/PROCESS.md`                                    | edit   |                                                     |
| `docs/planning/README.md`                                     | edit   | reachability.md row                                 |
| `docs/planning/tasks/TEMPLATE.md`                             | edit   |                                                     |
| `docs/planning/tasks/reports/TEMPLATE.md`                     | edit   |                                                     |
| `docs/planning/tasks/reports/README.md`                       | edit   | Disposition tags                                    |
| `docs/planning/decisions.md`                                  | edit   |                                                     |
| `docs/planning/engineering-runbook.md`                        | edit   | Spec traps                                          |
| `docs/planning/streams/README.md`                             | edit   |                                                     |
| `docs/planning/streams/delivery.md`                           | edit   | owner, status words                                 |
| `docs/planning/streams/design.md`                             | edit   |                                                     |
| `docs/planning/streams/identity.md`                           | edit   |                                                     |
| `docs/planning/streams/language.md`                           | edit   |                                                     |
| `docs/planning/streams/onboarding.md`                         | edit   |                                                     |
| `docs/planning/streams/operations.md`                         | edit   |                                                     |
| `docs/planning/streams/reachability.md`                       | edit   |                                                     |
| `docs/planning/streams/recovery.md`                           | edit   |                                                     |
| `docs/planning/streams/selling.md`                            | edit   |                                                     |
| `docs/planning/streams/workflow.md`                           | edit   |                                                     |
| `docs/planning/tasks/T-011-*.md`                              | edit   | Struck precondition                                 |
| `docs/planning/tasks/T-028-*.md`                              | edit   | depends T-044                                       |
| `docs/planning/tasks/T-047-*.md`                              | edit   | Flows line if needed                                |
| `docs/planning/tasks/T-048-*.md`                              | edit   |                                                     |
| `docs/planning/tasks/T-051-*.md`                              | edit   |                                                     |
| `docs/planning/tasks/T-057-*.md`                              | edit   |                                                     |
| `docs/planning/tasks/T-058-*.md`                              | edit   |                                                     |
| `docs/planning/tasks/T-084-*.md`                              | new    | draft                                               |
| `docs/planning/tasks/T-085-*.md`                              | new    | draft                                               |
| `docs/planning/tasks/T-086-*.md`                              | new    | draft                                               |

Any other `docs/planning/tasks/T-*.md` whose `blocks:` disagrees with
`depends:` is also edited, to make the derived value and the field agree.

### Added during execution

| Path                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Reason                                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/planning/tasks/T-002-*.md`, `docs/planning/tasks/T-008-*.md`, `docs/planning/tasks/T-016-*.md`, `docs/planning/tasks/T-024-*.md`, `docs/planning/tasks/T-032-*.md`, `docs/planning/tasks/T-041-*.md`, `docs/planning/tasks/T-054-*.md`, `docs/planning/tasks/T-059-*.md`, `docs/planning/tasks/T-061-*.md`, `docs/planning/tasks/T-062-*.md`, `docs/planning/tasks/T-064-*.md`, `docs/planning/tasks/T-068-*.md`, `docs/planning/tasks/T-075-*.md`, `docs/planning/tasks/T-076-*.md` | `blocks:` disagreed with the derived value — the clause above, now with names                                                                           |
| `docs/planning/tasks/T-044-*.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                           | `blocks: T-028`, the inverse of the `T-028` edit the Scope asks for                                                                                     |
| `docs/planning/tasks/T-049-*.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                           | `depends: T-054` — the field said `T-054` blocks it, and a voucher on a price needs the price, so the dependency was kept rather than the claim dropped |
| `docs/planning/tasks/T-022-*.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                           | The only `blocked` task; the new rule needs its `## Blocked on` with `What:` and `Who:`                                                                 |
| `tests/Fixtures/planning/docs/planning/tasks/reports/T-001-2026-09-15-someone.md`                                                                                                                                                                                                                                                                                                                                                                                                          | New fixture: the disposition rule is only known to catch anything if it is shown catching one, and the live directory has no report from the cutoff     |

## Database

None.

## Code

```php
// App\Support\TaskBoard
/** @return list<string> every backticked path in the first cell of every Files row, globs expanded against $root */
private function files(string $contents): array;
/** @return array<string, list<string>> task id => ids that depend on it, derived from depends: */
public function blockedBy(): array;
/** @return list<array{id: string, file: string, with: string}> ready tasks sharing a file with a task reported in the last seven days */
public function overlaps(): array;
/** @return int report bullets under "Found, not fixed" with no disposition tag */
public function untriaged(): int;
public function readyTarget(): int;   // config('qori.planning.ready_target')
```

```php
// App\Console\Commands\TasksCommand
protected $signature = 'qori:tasks {--check} {--stdout} {--new= : stream/slug for a draft stub}';
```

The disposition pattern: a bullet under `## Found, not fixed` ends with
`→ T-###`, `→ draft T-###` or `→ decided: ` followed by text. The rule applies
to reports whose front matter `date:` is 2026-09-15 or later.

## Copy

None (console output aimed at developers is diagnostics).

## Routes

None.

## Tests

**Changed: `tests/Feature/TaskBoardTest.php` — 12 new cases**

1. `test_every_backticked_path_in_a_files_row_is_captured`
2. `test_a_glob_in_a_files_row_expands_against_the_repo`
3. `test_a_files_row_may_not_be_a_bare_basename`
4. `test_every_stream_has_an_owner`
5. `test_a_stream_file_carries_no_status_words`
6. `test_every_task_a_stream_names_exists_and_belongs_to_it`
7. `test_blocks_agrees_with_depends`
8. `test_a_blocked_task_says_what_and_whom_it_waits_on`
9. `test_a_ready_l_task_names_its_split`
10. `test_a_report_from_the_cutoff_disposes_of_every_finding`
11. `test_a_task_that_rewires_a_flow_names_its_flow_file`
12. `test_every_stream_is_listed_in_the_streams_index`

Plus `test_the_board_renders_from_the_task_files` extended for the derived
`blocks` column if the renderer shows it.

## Acceptance

- [x] `php artisan qori:tasks --check` passes on the live directory with every new rule
- [x] `php artisan qori:tasks --new workflow example` writes a draft stub with the next id (delete it afterwards)
- [x] The five settled decisions sit under `## Decisions` with `D-###` ids; "Decisions needed" lists every draft's owner question
- [x] No stream file carries a status word; every stream has an owner and is in the index
- [x] `T-084`, `T-085`, `T-086` exist as drafts with "Before this can be ready"
- [x] `npm run check:fix` run; `composer ci:check` green from a clean tree
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

The rendered board is gitignored since the commit that opened this task; do
not restore it. Where a rule would fail on an old `done` task, scope the rule
to ready and doing tasks rather than editing history.
