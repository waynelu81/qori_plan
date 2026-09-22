---
id: T-177
title: Naming the Group in setup gives it the URL of its name
stream: onboarding
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-177 — Naming the Group in setup gives it the URL of its name

## Why

A new Group gets a name Qori makes up and a slug from it — "Walk's group",
`walks-group` — and naming it in setup part one kept the slug on purpose, so
"Walk Studio" lived at `walks-group` in every URL, the public share link
included (the 21 September 2026 walk; the first-share journey's step 4). The
owner, 22 September 2026: naming the Group in setup should also set its URL,
"yes please". Afterwards it does, while nothing has been shared.

## Decisions taken to make this specifiable

- **From setup only.** A rename from the dashboard's card keeps the slug, as
  `GroupService::rename()` always has: links already sent carry it.
- **Only while the Group has never published a Series.** Before that no
  public link can exist; after, one may, and setup's part one is still
  reachable with Back.
- **The next free slug** of the new name, `harbour-lane-studio-2`, when
  another Group holds it; a Group keeps its own slug when the name makes the
  same one.

## Preconditions

None.

**Data this task verifies against:** a clean database.

**Equipment:** None.

## Scope

**In:**

- `GroupService::nameInSetup()`, and `GroupController` sending a setup naming
  to it.

**Out:**

- Redirecting the old slug to the new one: nothing was shared under it.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Services/GroupService.php` | edit | `nameInSetup()`; `uniqueSlug()` may keep the Group's own |
| `app/Http/Controllers/Share/GroupController.php` | edit | setup names through it |
| `docs/flows/onboarding.md` | edit | part one |
| `docs/tinker/groups.md` | edit | the recipe |
| `tests/Feature/Share/SetupTest.php` | edit | one changed, two new cases |
| `tests/Feature/Share/SetupStepsTest.php` | edit | the redirect under the new slug |
| `tests/e2e/support/creator.ts` | edit | reads the slug again after naming |

## Database

None.

## Code

```php
public function nameInSetup(Group $group, string $name): Group;               // GroupService
public function uniqueSlug(string $name, ?Group $except = null): string;       // was uniqueSlug(string $name)
```

## Copy

None.

## Routes

None.

## Tests

**Changed:**

1. `tests/Feature/Share/SetupTest.php` — `test_naming_the_group_from_setup_goes_to_payments`
   now lands under the new slug; `test_naming_in_setup_takes_the_next_free_url`
   and `test_a_group_that_has_published_keeps_its_url_when_named_in_setup` new
2. `tests/Feature/Share/SetupStepsTest.php` — the redirect under the new slug

## Acceptance

- [x] Naming the Group in setup gives it the slug of its name while nothing is published
- [x] A dashboard rename, and a Group that has published, keep the slug
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

None.
