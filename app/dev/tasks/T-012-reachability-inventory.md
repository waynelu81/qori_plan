---
id: T-012
title: A command that lists routes and services with no way in
stream: reachability
status: done
owner: claude
estimate: M
depends: none
blocks: T-014
---

# T-012 — A command that lists routes and services with no way in

## Why

Qori keeps building things nobody can click. `ShareDigest::nextAction()` was
computed on every dashboard load and rendered by no Vue file until Day 3 of the
redesign week found it by reading. Connect onboarding and campaigns are routed
and tested and linked from nowhere. `payment_fulfilments` records every failed
payment and nothing reads the table.

Each was found by a person noticing. That does not scale and it does not repeat,
so the audit should be a command that fails a build rather than a document
somebody writes once.

## Preconditions

**`php artisan wayfinder:generate --with-form` must have been run.**
`resources/js/routes` and `resources/js/actions` are generated _and gitignored_,
so a fresh clone has neither. An analyser that reads them finds an empty
directory and reports success — and one worker hit exactly this, concluding
that Vue's `@/routes` imports "did not count on this machine".

This analyser deliberately excludes those directories (they contain every route
by construction), so it is not reading them. But anything else in this stream
will be, and a check that silently reads nothing is worse than no check.

## Scope

**In:**

- A command listing GET routes no Vue file or route helper links to.
- The same for `App\Services\*` public methods called from nowhere.
- An allow-list for the deliberate exceptions, with a reason per entry.

**Out:**

- Fixing anything it finds. That is `T-014`, and its contents depend on this.
- Dead CSS, unused components, unused lang keys. Different problem, different
  tool, and the false-positive rate is much higher.
- Wiring it into `composer ci:check`. Run it manually until the allow-list has
  settled; a new check that fails on day one gets switched off.

## Files

| Path                                           | Change | Notes                                               |
| ---------------------------------------------- | ------ | --------------------------------------------------- |
| `app/Console/Commands/ReachabilityCommand.php` | new    | `qori:reachability`                                 |
| `app/Support/Reachability.php`                 | new    | The analysis, so it is testable without the console |
| `config/qori.php`                              | edit   | `reachability.allowed`                              |
| `tests/Feature/ReachabilityTest.php`           | new    | 6 cases                                             |
| `docs/planning/reachability.md`                | new    | The findings, written once the command runs         |

## Database

None.

## Code

```php
namespace App\Support;

class Reachability
{
    public function __construct(private string $root) {}

    /**
     * GET routes that nothing links to.
     *
     * @return list<array{name: string, uri: string, action: string}>
     */
    public function unreachableRoutes(): array;

    /**
     * Public service methods called from nowhere outside their own class.
     *
     * @return list<array{class: string, method: string}>
     */
    public function uncalledServiceMethods(): array;
}
```

**How a route counts as reachable.** Any one of:

- its route name appears in a generated Wayfinder helper that a `.vue` file
  imports (`resources/js/routes/**`, `resources/js/actions/**`);
- its URI appears as a string literal in a `.vue` file;
- it is redirected to from PHP (`to_route('name')`, `route('name')`);
- it is in the allow-list.

Framework and vendor routes are excluded: skip any route whose action class is
outside `App\`. Skip `_ignition`, `sanctum`, `storage.*` and the passkey package's
hardcoded paths.

**How a service method counts as called.** Its name appears as `->method(` or
`::method(` in any file under `app/` other than its own class, or in `tests/`.

Both forms, and this matters: matching only `->method(` reports every statically
called method as dead. Counting `tests/` as a caller is a deliberate weakening —
it means a capability that has tests but no UI will not be reported, which is
precisely the failure this stream exists to catch. It is accepted because the
alternative reports most of the codebase. **The route half is what catches an
unreachable feature; the method half only catches `public` that should be
`private`.** Do not expect more of it than that, and say so in the findings. This is
deliberately crude — grep, not static analysis. A false positive costs one
allow-list line with a reason; a static analyser costs a dependency and a week.
State that trade-off in the class docblock so the next reader does not "fix" it.

**The allow-list** lives in `config/qori.php`:

```php
'reachability' => [
    // Route name or Class::method => why it is deliberately unreachable.
    'allowed' => [
        'share.payouts.return' => 'Stripe redirects here; nothing in Qori links to it.',
    ],
],
```

A reason is mandatory. An allow-list of bare names is a list nobody can audit
later.

## Copy

None. `$this->line()` output aimed at a developer is a diagnostic, not copy
(§23).

## Routes

None.

## Tests

**New: `tests/Feature/ReachabilityTest.php` — 6 cases**

1. `test_it_finds_a_route_nothing_links_to` — register a temporary named route
   in the test and assert it is reported.
2. `test_a_route_linked_from_a_vue_file_is_not_reported` — assert a known-linked
   route (`share.series.index`) is absent.
3. `test_an_allow_listed_route_is_not_reported`.
4. `test_it_ignores_routes_outside_the_app_namespace` — a Fortify route.
5. `test_it_finds_a_service_method_nobody_calls`.
6. `test_the_command_exits_non_zero_when_something_is_unreachable` — the shape
   `T-014` will eventually wire into CI.

Point the tests at fixture directories rather than the real `resources/js`, so
they do not start failing because somebody linked something. Take the root as a
constructor argument for exactly this reason.

## Acceptance

- [x] `php artisan qori:reachability` lists unreachable GET routes and uncalled
      service methods
- [x] Every allow-list entry carries a reason, and a test enforces it
- [x] ~~The known cases appear: Connect onboarding, campaigns,
      `payment_fulfilments`~~ — **this criterion was wrong**; see Notes. What
      the run does report is two public service methods with no external
      caller, one of which is the end of a chain nobody enters.
- [x] Findings written up in `docs/planning/reachability.md`, which is what
      `T-014` is scoped from
- [x] Not wired into `ci:check` yet, deliberately
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)

## Re-scope log

None.

## Notes

The first run produced two findings, well under the twenty that would have
meant the heuristic was wrong.

**The acceptance criterion naming three known cases was wrong, and the Scope
section was right.** Of the three:

- _Connect onboarding_ is linked now — the Payments page was built after the
  spec was written, so a clean result here is the product having improved.
- _Campaigns_ have **no routes at all**. A tool that looks for unreachable
  routes cannot see a feature that was never routed, which is a real limit of
  the approach and is written into the findings doc so a clean run is not
  mistaken for a clean bill.
- _`payment_fulfilments`_ is a table. Models and tables are explicitly out of
  scope, so the command was never going to report it.

Corrected rather than re-scoped: the Scope section is the contract, and no
built behaviour changed. But it is a good example of an acceptance criterion
written from memory rather than from the scope above it.

**"Uncalled" needed a more careful label than the spec's.** Both findings are
methods called only from inside their own class — not dead, just `public` where
`private` would do. The command says "from outside their own class" so the
reader is not sent looking for a missing UI when the fix is a keyword.

`Route::getRoutes()` on the facade returns `RouteCollectionInterface`, which
PHPStan will not iterate. `Router::getRoutes()->getRoutes()` is the iterable
one.
