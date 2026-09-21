---
id: T-060
title: Domain enums live in app/Enums
stream: operations
status: done
owner: claude
estimate: S
depends: T-059
blocks: none
---

# T-060 — Domain enums live in app/Enums

## Why

Eighteen enums live in `app/Models/Enums`. The directory name claims they back
columns, and since `T-059` one of them does not: `SignupIntent` validates a form
and names a branch, and is never stored. The claim was only ever enforced by
`ModelEnumTest`'s explicit column map, not by the folder, so the folder was
doing no work the test does not — and now it is wrong for one file.

They are not model internals either. `EpisodeProvider` is read in ten files
outside `app/Models`, `AccessStatus` in five, `EpisodeType` in five: checkout,
access, playback, mail and the console all speak these words. Filing them
under Models says "reach through a model to get one", which nothing does. And
`php artisan make:enum` puts the next one in `app/Enums`, which is where the
next contributor will look.

The owner asked for an opinion on 13 September 2026 and then for the move.

## Decisions taken to make this specifiable

**`app/Enums`, flat.** One home for the domain's closed vocabularies. No
per-feature scattering: the reason these exist is that several features share
one word for one state.

**Two layer-owned enums stay put.** `App\Exceptions\ErrorCode` is the public
contract of the error layer (§23); `App\Admin\StaffRole` and `StaffAbility` are
the console's authorisation vocabulary (§24). Both directories are places
`CLAUDE.md` names as where that layer's code lives. The rule: a word several
layers share goes in `app/Enums`; a contract one layer owns stays with the
layer.

**`git mv`, so history follows the files.**

**`ModelEnumTest` keeps its name and its job.** It still maps columns to enums
and checks reachability from the map; only the directory it reads changes. Its
directory-walking case is renamed so it stops claiming the namespace is
"models".

## Preconditions

`T-059` merged, so the enum that motivated this is already request-scoped.

## Scope

**In:**

- Moving the eighteen files and rewriting the namespace everywhere it is
  imported or spelled.
- The two path-based reads in `ModelEnumTest`.
- The "Where code lives" list in `CLAUDE.md` and its `.cursor` mirror.

**Out:**

- `ErrorCode`, `StaffRole`, `StaffAbility`.
- Any enum's cases, methods or backing values.
- Done task files that name the old path. They are history.

## Files

| Path                                                        | Change | Notes                                              |
| ----------------------------------------------------------- | ------ | -------------------------------------------------- |
| `app/Enums/*.php`                                           | moved  | From `app/Models/Enums/`, seventeen files          |
| Every importer in `app/`, `tests/`, `database/`             | edit   | `App\Models\Enums` → `App\Enums`; 107 files        |
| `tests/Feature/Enums/ModelEnumTest.php`                     | edit   | Two `app_path()` reads, one message, one case name |
| `CLAUDE.md`, `.cursor/rules/laravel-conventions.mdc`        | edit   | One line each under "Where code lives"             |
| `docs/planning/pricing-and-competitor-review-2026-09-11.md` | edit   | Names the old path                                 |
| `docs/planning/decisions.md`                                | edit   | The placement rule                                 |

## Database

None.

## Code

```php
namespace App\Enums;   // was App\Models\Enums, in all seventeen files
```

```php
// tests/Feature/Enums/ModelEnumTest.php
$declaration = app_path('Enums/'.class_basename($enum).'.php');
$files = $this->phpFilesIn(app_path('Enums'));
// and the case test_every_enum_lives_in_the_models_enums_namespace
// becomes test_every_domain_enum_lives_in_the_enums_namespace
```

## Copy

None.

## Routes

None.

## Tests

**New:** none. A move adds no behaviour.

**Changed:** `ModelEnumTest`, mechanically, as above. Every other test changes
only its `use` lines. If anything needs more than a namespace, the move touched
behaviour and that is a re-scope.

A grep for `Models\\Enums` and `Models/Enums` over `app/`, `tests/`,
`database/`, `config/`, `CLAUDE.md` and `.cursor/` returns nothing when this is
done.

## Acceptance

- [x] `app/Models/Enums` no longer exists and `app/Enums` holds eighteen enums
- [x] The grep above returns nothing
- [x] `ErrorCode`, `StaffRole` and `StaffAbility` are where they were
- [x] `CLAUDE.md` and its mirror say where enums live and why the two stay
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

`ModelEnumTest` was named for the refactor that created it (`T-023`) and the
name still describes what it checks: that model attributes with a closed set of
values are enums, round-trip, and are reachable. It is not renamed here.
