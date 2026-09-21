# Module: reachability

**What it is.** Proving that everything built can actually be reached. A tested
service with no route, and a route with no link, are both invisible — and both
look finished on a board.

**Done when.** A command lists every route and service method nothing reaches,
and the list is empty or every entry is deliberate.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| How is "unreachable" detected? | A command that walks routes and service methods and reports what nothing links to | Review does not catch it; the feature works when you test it directly. |
| Is it a gate or a report? | A report, read deliberately | A gate would fail on every legitimately-unlinked thing and be disabled within a week. |
| When is a feature "done"? | When a person can reach it, not when its tests pass | Qori shipped three fully-tested features with no way in. |

## Build order

1. **The command**: every GET route, every public service method, and what
   references each.
2. **An allow-list with a reason per entry**, so a deliberate omission is
   recorded rather than re-found every run.
3. **Read it at the end of every stream**, not continuously.

## Rules that bite

- **Finish vertical slices.** A service with no UI is not a finished feature.
- **"Built, with no way in" is a status worth tracking on the plan itself.**
  Qori carried it as a headline for weeks, which is the only reason it got
  fixed.

## Native contract

Not applicable to the client, but the same failure exists: an endpoint no
screen calls.

## Traps

| Symptom | Cause |
| --- | --- |
| "We built that months ago — nobody could get to it" | Completion judged on tests, not reach. |
| "The unreachable list is ignored" | No reasons on the allow-list, so the signal drowned. |

## Proven / Not proven

**Proven**: the command, its allow-list, and the finding that three built
features had no route or link.

## Source

Qori tasks `T-012`, `T-046`, `T-067`. Stream `reachability`.
