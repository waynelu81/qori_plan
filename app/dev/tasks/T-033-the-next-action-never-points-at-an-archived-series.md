---
id: T-033
title: The next action never points at an archived Series
stream: design
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-033 — The next action never points at an archived Series

## Why

`ShareDigest::for()` opens with `Series::query()->forGroup($group)->get()` and
no `unarchived()` filter, and everything downstream inherits that. Two
consequences, found by review pass `R-002` (F-1) and by checking it.

**The dashboard can tell a creator to work on a Series it has taken out of
circulation.** `nextAction()` picks the first Series with no Episodes, then the
first Series that is not published. An archived Series satisfies both, because
archiving sets `status` to `Archived` and nothing else. R-002 photographed the
first case: "Workshops We No Longer Run has no Episodes yet · Add the first
Episode", on a Series the very next screen labels **Archived**.

**The second case is worse and the pass did not reach it.** `publish()` refuses
an archived Series — a guard `T-009` added deliberately, to close a plan-cap
bypass. So "Make ready to share" on an archived Series is a primary call to
action that leads to a **guaranteed refusal**. `PLAN.md`'s beta gate forbids
that by name: no built-in action may knowingly lead to a predictable 403 or
plan refusal.

**The same line hides a fifth place the plan cap is counted.**
`blockingAction()` reports `'used' => (string) $series->count()` over the
unfiltered collection, while `isOverSeriesCap()` counts through `seriesUsed()`,
which excludes archived. The read-only banner therefore tells a creator "You
have 3 and your plan includes 1" while the rule that locked them counts 2 — and
when they take the banner's own advice and archive one, **the number does not
move.** `T-009` found four places this count was duplicated and fixed them; this
is the fifth, and it survived because the count and the cap are computed by
different code paths a few lines apart.

## Decisions taken to make this specifiable

**Filter in the query, not at each use.** One `->unarchived()` on the opening
query fixes the next action, the blocking copy and the dashboard tile together,
and makes `$series->count()` and `Group::seriesUsed()` agree **by construction**
rather than by two people remembering the same rule. Filtering at each call site
is how a sixth place gets missed.

**`series.total` counts unarchived, and that is a change.** The tile it feeds
renders the value beside `series.limit`, which is the plan cap. A meter that
shows a limit has to count the way the limit counts, or it reports somebody as
over a cap they are within. Nothing new is added to hold the archived count: a
key nothing renders is the shape `T-023`'s reachability test exists to catch,
and the Series list already shows archived Series with their own status.

**`published` needs no change.** Archiving overwrites `status`, so an archived
Series returns false from `isPublished()` and was never in that count.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- One `unarchived()` filter on the digest's Series query.
- The tests that should have caught this, which do not exist.

**Out:**

- The other seven `R-002` findings. Each is its own task, and F-2 in
  particular is a different file and a different rule.
- Changing what archiving does, or what `publish()` refuses. Both are correct;
  the digest is what disagrees with them.
- The Series list page, which shows archived Series on purpose and labels them.

## Files

| Path                                | Change | Notes                               |
| ----------------------------------- | ------ | ----------------------------------- |
| `app/Services/ShareDigest.php`      | edit   | One filter, and why                 |
| `tests/Feature/ShareDigestTest.php` | edit   | 4 new cases, no changes to existing |

## Database

None.

## Code

```php
// App\Services\ShareDigest::for()
$series = Series::query()->forGroup($group)->unarchived()->get();
```

That is the whole fix. It carries a comment saying that the filter is what keeps
`$series->count()` and `Group::seriesUsed()` in agreement, because the next
person to add a count here needs to know that the agreement is deliberate rather
than a coincidence.

## Copy

None. `share.blocked.over_cap` and `over_cap_admin` already say ":used", and the
value passed into them becomes correct without the sentence changing.

## Routes

None.

## Tests

**Changed: `tests/Feature/ShareDigestTest.php` — 4 new cases, 13 existing
untouched.** The existing file mentions archiving nowhere, which is why `T-009`
could add archiving without this surfacing.

1. `test_an_archived_series_is_never_the_next_action` — a Group whose only
   Series is archived and empty is told to make a Series, not to add an Episode
   to the archived one.
2. `test_an_archived_series_is_never_offered_for_publishing` — an archived
   Series with Episodes, and a published Series with none of its own. The next
   action must not be "make ready" on the archived one, because `publish()`
   would refuse it. **This is the case that leads to a guaranteed refusal.**
3. `test_the_over_cap_banner_counts_the_way_the_cap_counts` — a Group over its
   cap with one Series archived: the `used` in the blocking action equals
   `seriesUsed()`, not the raw count.
4. `test_archiving_moves_the_number_the_banner_shows` — the same Group before
   and after archiving one more. The figure the creator is watching must change
   when they take the advice they were given. This is the property the fifth
   duplicate count broke, stated as behaviour rather than as an implementation
   detail.

**Changed elsewhere:** none expected. If an existing digest assertion moves,
that is a signal the filter reached further than intended — stop and re-scope.

## Acceptance

- [x] No next action ever names an archived Series
- [x] No next action leads to a refusal `publish()` would produce
- [x] The over-cap banner's figure equals `Group::seriesUsed()`
- [x] Archiving a Series moves that figure
- [x] The dashboard tile counts the way the limit beside it counts
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**All four tests failed before the fix, and their failure messages are the bug
stated plainly.** The second was the one worth writing down: the dashboard said
_"Retired Course is ready to share"_ about a Series `publish()` refuses. That is
the guaranteed-refusal case, reproduced rather than argued.

**Thirteen existing digest assertions were untouched**, which is the signal the
spec asked for. One filter reached exactly as far as intended.

R-002 routed F-1 to the design stream, and this follows that routing. The
plan-cap half is arguably a `recovery` concern, but splitting one query filter
across two streams to satisfy a taxonomy would be worse than either.
