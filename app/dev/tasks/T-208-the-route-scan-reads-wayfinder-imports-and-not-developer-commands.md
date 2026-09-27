---
id: T-208
title: The route scan reads Wayfinder imports, and not developer commands
stream: reachability
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-208 — The route scan reads Wayfinder imports, and not developer commands

## Why

`T-051` took `routes/` and `tests/` out of the route half's haystack, and the
first run after it still reported no route. Classifying the evidence on
27 September 2026 found why three of the 47 GET routes pass: `security.edit`,
`share.vocabulary.edit` and `share.peers.index` are named in `app/` only by
`DesignReviewCommand`, a developer command that prints review URLs. Each is
reachable in the product — the settings layout imports `@/routes/security`,
the sidebar builds `` `${base}/peers` `` and the Group settings layout
`` `${base}/settings/vocabulary` `` — but the scan cannot see either shape: a
Wayfinder import names a module path and an export, not a route name, and
`${base}/…` hides the `/g/{group}` prefix the URI pattern needs. The scan is
right about the three by accident, and would call them unreachable the day the
command stopped naming them.

Afterwards a Wayfinder import of a route's helper counts as a link to that
route, and a developer command does not.

## Decisions taken to make this specifiable

None yet: see "Before this can be ready".

## Preconditions

`resources/js/routes` and `resources/js/actions` are generated and
gitignored; reading which helper belongs to which route may need
`php artisan wayfinder:generate --with-form` first.

**Data this task verifies against:** the fixture trees under
`tests/Fixtures/reachability/`, and the real tree's run.

**Equipment:** None.

## Scope

**In:**

- A Wayfinder import of a route helper counts as a link to its route.
- `app/Console` stops counting as a way in.

**Out:**

- The method half, which `T-051` left alone for the same reason.
- `${base}/…` template literals, unless the answer below is that they are
  worth matching.

## Files

| Path                                 | Change | Notes                         |
| ------------------------------------ | ------ | ----------------------------- |
| `app/Support/Reachability.php`       | edit   | What counts as a link         |
| `tests/Feature/ReachabilityTest.php` | edit   | A Wayfinder import; a command |
| `tests/Fixtures/reachability/**`     | new    | The trees those cases read    |

Flows: none — a developer tool; no flow describes it.

## Database

None.

## Code

To be written when the task is brought to ready.

## Copy

None. Console output aimed at a developer is a diagnostic, not copy.

## Routes

None.

## Tests

To be written when the task is brought to ready.

## Acceptance

- [ ] A route reached only through a Wayfinder import in a `.vue` or `.ts`
      file is not reported
- [ ] A route named only by a command under `app/Console` is reported
- [ ] The real tree's run is recorded in `app/dev/reachability.md`
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- How a Wayfinder import maps to a route: read the generated
  `resources/js/routes/**` (which needs generating in CI), or derive the
  module path and export from the route's name — `security.edit` is
  `@/routes/security` and `edit` — without reading generated files. Anyone's,
  from how Wayfinder names them.
- Whether `app/Console` is the whole of "developer-only" in `app/`, or whether
  other places name routes for developers only. Anyone's, from the code.
- Whether `${base}/…` template literals are worth matching, or whether every
  such link should become a Wayfinder import instead. Anyone's.

## Re-scope log

None.

## Notes

Found by `T-051` on 27 September 2026; its report has the evidence, and
`app/dev/reachability.md` the run.
