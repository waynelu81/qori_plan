---
id: T-154
title: Model datetime properties say CarbonImmutable
stream: workflow
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-154 — Model datetime properties say CarbonImmutable

> **Written on 20 September 2026 from a finding in `T-151`'s report**, where
> the inaccuracy this task fixes had already cost one silent bug.

## Why

`app/Providers/AppServiceProvider.php:118` calls
`Date::use(CarbonImmutable::class)`, so every `datetime` cast on every model
hands back a `CarbonImmutable`. Forty `@property ?Carbon` lines across
seventeen models say otherwise.

`CarbonImmutable` does not extend `Illuminate\Support\Carbon` or
`Carbon\Carbon` — they are siblings under `CarbonInterface`. So
`$model->some_at instanceof Carbon` is **always false**, and PHPStan, which
reads the docblocks, agrees that it is a sensible thing to write. That is not
hypothetical: `T-151` shipped `ConnectionService::isDue()` with exactly that
check and `fresh()` renewed nothing, ever, until a hand-written probe caught
it. The gate was green the whole time.

Afterwards the docblocks say what the casts return, and the next person who
writes an `instanceof` against a model's timestamp is told by static analysis
rather than by a user.

## Decisions taken to make this specifiable

Brought to ready on 28 September 2026, from the code.

**The docblocks name `CarbonImmutable`.** It is what every `datetime` cast
returns, since `AppServiceProvider` calls `Date::use(CarbonImmutable::class)`,
and it is the precision that catches `T-151`'s mistake: told a property is a
`CarbonImmutable`, PHPStan reports `instanceof Carbon` as always false, where
told `CarbonInterface` it lets the check stand, since a `Carbon` is one too.
Coupling to `Date::use()` is the point, not the cost: if that call ever
changes, the docblocks should be made to change with it.

**Nothing outside `app/Models` makes the claim.** Three files use
`Illuminate\Support\Carbon` — `CheckoutPending`, `ConnectionService` and
`LoginCodeService` — and each parses with it and declares what that returns,
so their types are true. `app/Data` holds `CarbonInterface`. Checked on 28
September 2026: 65 `@property` lines across 24 models, grown from the draft's
40 across 17.

**One guard, in `ArchitectureTest`: no model imports a mutable `Carbon`.** A
docblock cannot name `Carbon` without the import, so refusing
`use Illuminate\Support\Carbon;` and `use Carbon\Carbon;` in `app/Models`
holds the line without reading docblocks. And the rule goes into `CLAUDE.md`'s
Persistence section, so the next model is written right the first time.

**PHPStan's findings from the sweep are fixed at the call site.** A model
property now typed `CarbonImmutable` may be assigned a mutable `Carbon`
somewhere; each such site is corrected to what the cast would give, not the
docblock loosened.

## Preconditions

None.

**Data this task verifies against:** None; no behaviour changes.

**Equipment:** None.

## Scope

**In:**

- Every `@property` naming `Carbon` in `app/Models`, and the imports.
- Whatever PHPStan then reports at a call site.
- The guard and the `CLAUDE.md` line.

**Out:**

- The three files outside the models whose `Carbon` is true.

## Files

| Path                                 | Change | Notes                                       |
| ------------------------------------ | ------ | ------------------------------------------- |
| `app/Models/*.php`                   | edit   | `CarbonImmutable` in docblocks; the imports |
| `tests/Feature/ArchitectureTest.php` | edit   | 1 case                                      |
| `CLAUDE.md`                          | edit   | one line under Persistence                  |

Flows: none — no call chain changes.

## Database

None.

## Code

None: docblocks and imports only, and whatever call sites PHPStan names.

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/ArchitectureTest.php` — 1 new case**

1. `test_models_type_their_dates_as_carbon_immutable` — no file in
   `app/Models` imports `Illuminate\Support\Carbon` or `Carbon\Carbon`.

PHPStan is the rest of the proof: it reads the docblocks this changes.

## Acceptance

- [x] Every model datetime property says `CarbonImmutable`
- [x] `ArchitectureTest` refuses a mutable `Carbon` in a model, and `CLAUDE.md` says why
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~`CarbonImmutable` or `CarbonInterface`?~~ **Answered from the code, 28
  September 2026:** `CarbonImmutable` (Decisions).
- ~~Does anything outside `app/Models` carry the same claim?~~ **Answered 28
  September 2026:** no (Decisions).
- ~~Is one guard worth having?~~ **Answered 28 September 2026:** yes, on the
  imports (Decisions).

## Re-scope log

None.

## Notes

The finding came from `T-151`'s report of 20 September 2026. Its `isDue()` bug
is fixed there, with three test cases; this task is only about stopping the
next one.

Worth knowing for whoever claims it: the gate did not catch the original bug
and will not catch its siblings, because PHPStan believes the docblock. The
only reason this one surfaced is that somebody wrote a throwaway probe to
check a method the spec had no test case for.
