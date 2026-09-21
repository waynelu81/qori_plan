---
id: T-057
title: A share controller receives the slug its signature declares
stream: operations
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-057 — A share controller receives the slug its signature declares

## Why

Twenty methods across six controllers under `/g/{group}` declare
`string $group`, and each receives the **Group model coerced to a string** —
its JSON, through `Model::__toString()`. `SetCurrentGroup::fromRoute()` resolves
the slug to a model and then writes the model back onto the route parameter,
"so controllers that do type-hint Group receive the same instance". No public
share controller method type-hints `Group`. The write-back serves nobody and
mis-types everybody.

It was invisible because nothing read the value: every method takes its Group
from `CurrentGroup`, and the parameter is in the signature only because route
parameters arrive positionally (engineering runbook, trap 5).
`SeriesController::show()` says so in a comment that calls it a slug. `T-054`
found it the first time anybody used it — `route('share.payouts.show', $group)`
threw an `UrlGenerationException` with the model's JSON in the message.

## Decisions taken to make this specifiable

**Delete the write-back; do not retype twenty signatures.** Laravel's implicit
binding runs in `SubstituteBindings`, in the `web` group, before any route
middleware — so a method that type-hints `Group` already holds the model by the
time `SetCurrentGroup` looks, and `fromRoute()`'s "either shape" branch is
right without writing anything. Retyping the signatures to `Group` would work
too, and would also change which 404 a wrong slug gets: the framework's
`ModelNotFoundException` instead of `errors.group.not_found`, whose copy is
deliberately vague so a non-member cannot confirm a slug exists. One deleted
line keeps that.

**Prove it with a route, not a controller.** A test registers a probe route
under the same middleware and returns the parameter. That asserts the mechanism
rather than one controller's use of it, and fails today with a JSON body.

**The public controller is out of scope and right.** `PublicSeriesController`
is not behind the `group` middleware; its `string $group` is a real slug and
`Series::findPublic()` reads it.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The write-back in `SetCurrentGroup::fromRoute()`, and its docblock.
- The one comment that now describes the coercion as a fact of life.
- One sentence in the runbook's trap 5, so the next reader knows the parameter
  is the slug and not the model.

**Out:**

- Changing any controller signature.
- Using `$group` in any controller. `CurrentGroup` stays the source.
- `PublicSeriesController`.

## Files

| Path                                              | Change | Notes                                 |
| ------------------------------------------------- | ------ | ------------------------------------- |
| `app/Http/Middleware/SetCurrentGroup.php`         | edit   | Delete the write-back; docblock       |
| `app/Http/Controllers/Share/SeriesController.php` | edit   | The `payoutsUrl` comment from `T-054` |
| `docs/planning/engineering-runbook.md`            | edit   | Trap 5, one sentence                  |
| `tests/Feature/Share/GroupParameterTest.php`      | new    | 2 cases                               |

Flows: none — no route, action or service call moves; the middleware stops
rewriting a parameter it never needed to, and the flow docs never described
the write-back.

## Database

None.

## Code

```php
// App\Http\Middleware\SetCurrentGroup::fromRoute() — delete this line:
$request->route()?->setParameter('group', $group);
```

The docblock above `fromRoute()` says instead: implicit binding substitutes the
parameter only when the controller signature type-hints the model, and it runs
before this middleware, so the parameter is either the model already or the raw
slug; resolve either shape and write nothing back, because writing the model
back turned every `string $group` signature into the model's JSON.

```php
// tests/Feature/Share/GroupParameterTest.php — the probe, registered in the test:
Route::middleware(['web', 'auth', 'verified', 'group'])
    ->get('g/{group}/probe-string', fn (string $group): string => $group);

Route::middleware(['web', 'auth', 'verified', 'group'])
    ->get('g/{group}/probe-model', fn (Group $group): string => $group->slug);
```

Registered inside the test method, before the request, the way
`ErrorPagesTest` registers throw-away routes.

## Copy

None.

## Routes

None in the application. Two probe routes exist only inside the test.

## Tests

**New: `tests/Feature/Share/GroupParameterTest.php` — 2 cases**

1. `test_a_string_parameter_is_the_slug` — a member requests the string probe
   and the body is the slug. **Fails today**: the body is the Group's JSON.
2. `test_a_group_parameter_is_the_model` — a member requests the model probe
   and the body is the slug, proving implicit binding still supplies the model
   with the write-back gone.

**Changed:** none. `GroupScopingTest` and every share-surface test pass
unchanged, because none of them read the parameter.

## Acceptance

- [x] A `string $group` parameter under `/g/{group}` is the slug
- [x] A `Group $group` parameter under `/g/{group}` is the model
- [x] The wrong-slug 404 is still `errors.group.not_found`
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Added during execution

| Path                                                       | Change | Notes                                                                                                                         |
| ---------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `docs/flows/groups.md`                                     | edit   | Its diagram and "The middleware resolves the slug itself" described the write-back; both now say the parameter stays the slug |
| `app/Http/Controllers/Share/SeriesLifecycleController.php` | edit   | `archive()`'s comment said `SetCurrentGroup` replaces `{group}` with the model; a second comment the Scope did not name       |

## Re-scope log

None.

## Notes

Worth noticing how it survived: the write-back was added for a caller that
never existed, the coercion is silent because Eloquent models stringify to
JSON, and every controller had already been taught to ignore the parameter.
Nothing was careless. It was found by the first line of code to trust the
signature.

Wording defects found while building it (17 September 2026), none of which
changed what was built: the Flows line said the flow docs never described the
write-back, but `docs/flows/groups.md` did in two places, so it is under Added
during execution; "Twenty methods across six controllers" is 25 across nine
since `T-083` and the Setup, Integrations and Payouts work; and
`share.payouts.show` in Why no longer exists. A third test case asserts the
Acceptance line about the wrong-slug 404, which the two specified cases did not
cover. Scope named "the one comment" describing the coercion; there were two.
Decisions said binding runs "before any route middleware"; `auth` sorts ahead
of it, and what matters, that it runs before `group`, holds. Case 2 as
specified passed on the old code too, so it also asserts that `CurrentGroup`
holds the same instance binding produced, which is true only if binding ran
first.
