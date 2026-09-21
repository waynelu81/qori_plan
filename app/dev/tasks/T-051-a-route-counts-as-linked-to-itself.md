---
id: T-051
title: The reachability scan counts a route's own definition as a link to it
stream: reachability
status: ready
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-051 — The reachability scan counts a route's own definition as a link to it

## Why

`Reachability::isLinked()` decides a route is reachable like this:

```php
if ($name !== '' && str_contains($haystack, $name)) {
    return true;
}
```

and `haystack()` is the contents of every file under `resources/js` (minus
generated ones), **every file under `app/` and `tests/`, and every file under
`routes/`**.

`routes/web.php` contains `->name('series.public')`. So `series.public` is in
the haystack, so `series.public` is linked, and the same is true of **every named
route in the application**. The route half of this scanner cannot report a named
route, ever. Only an unnamed one can fail the check, and this codebase names
everything.

`tests/` is the second door into the same room. `series.public` also appears in
nine test assertions and in `DesignReviewCommand`, any one of which would have
been enough on its own.

**The consequence, measured:** `GET /s/{group}/{series}` is the public selling
page. No Vue file references it, the generated helper has no importer, and a
creator has no way to reach it. The scan calls it linked. That is `T-050`, and
it is exactly the class of defect this command exists to report.

`T-012`'s report already said `tests/` counts as a caller — for the **method**
half, which it described as the weaker one, and it named the route half as the
part that catches an unreachable feature. The route half has the same hole and
one more.

## Decisions taken to make this specifiable

**Exclude `routes/` from the haystack, and exclude `tests/` too.** A route's own
registration is not a link to it, and neither is an assertion that visits it. A
test proves the route works; the question this command asks is whether a person
can get there.

**Keep `app/`.** A `route()` call in a controller or a mailable is a real link —
that is how a redirect and an email reach a page.

**Do not narrow the name match.** The looseness is deliberate and documented:
`route('series.public')`, `to_route(...)` and a Vue file naming the route all
have to count, and they do not share a syntax. The fix is the haystack, not the
match.

**Expect the first run after this to report real routes.** That is the point,
and it is why this is `S` and the findings it produces are not. Each one is
triaged the way `T-014` triaged the hand-walked list: finish the way in, or
allow-list it with a reason.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The route haystack, and what counts as a link.
- Tests that a route linked only from its own definition is reported, and a
  route linked only from a test is reported.
- Recording the first run's findings, without fixing them.

**Out:**

- Fixing what the first run reports. Each finding gets triaged like any other;
  `T-050` is already one of them.
- The method half of the scanner. It has the same `tests/` weakness, it is
  documented, and changing both at once means not knowing which change produced
  which finding.
- Any change to the allow-list mechanism, which works.

## Files

| Path                                 | Change | Notes                                     |
| ------------------------------------ | ------ | ----------------------------------------- |
| `app/Support/Reachability.php`       | edit   | The haystack, and the docblock's claim    |
| `tests/Feature/ReachabilityTest.php` | edit   | 3 cases                                   |
| `docs/planning/reachability.md`      | edit   | The first run's output, and what it means |

## Database

None.

## Code

```php
// App\Support\Reachability::haystack()
// app/ only. A route's own registration is not a link to it, and a test that
// visits it proves it works rather than that anybody can get there — which is
// the entire question this command asks.
return $this->contentsOf($this->frontendFiles(), $this->phpFiles(onlyApp: true));
```

`phpFiles()` is also used by the method half, which must keep counting `tests/`
until that half is looked at separately. Give the route half its own list rather
than changing the shared one.

## Copy

None. Console output aimed at a developer is a diagnostic, not copy (§23).

## Routes

None.

## Tests

**Changed: `tests/Feature/ReachabilityTest.php` — 3 new cases**

The fixture tree already exists and already registers a synthetic orphan.

1. `test_a_route_linked_only_by_its_own_definition_is_reported` — **fails
   today**, and is the whole task.
2. `test_a_route_linked_only_from_a_test_is_reported` — the second door.
3. `test_a_route_linked_from_a_controller_is_still_linked` — the regression
   guard. A redirect or an email that names a route must keep counting.

The existing cases must keep passing unchanged. If one does not, the fixture was
relying on the hole.

## Acceptance

- [ ] A route named only in `routes/` is reported
- [ ] A route reached only from a test is reported
- [ ] A route named from `app/` is still counted as linked
- [ ] The first real run's findings are written down, not fixed
- [ ] `composer ci:check` green from a clean tree
- [ ] Board regenerated (`php artisan qori:tasks`)
- [ ] Report written in `reports/`

## Re-scope log

None.

## Notes

**Two clean runs were reported as reassurance and were not.** The command has
said "0 unreachable routes" since 9 September, `PLAN.md` and the `reachability`
stream both quoted it, and on 11 September a hand walk found three capabilities
reachable from nothing plus a public page no creator can link to. The command
was not wrong about what it measured. It measured whether a route's name appears
in files that include the line declaring it.

Worth stating plainly in the report: a tool that always answers "fine" is worse
than no tool, because the absence of one prompts somebody to look.
