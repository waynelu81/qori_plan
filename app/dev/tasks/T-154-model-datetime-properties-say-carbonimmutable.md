---
id: T-154
title: Model datetime properties say CarbonImmutable
stream: workflow
status: draft
owner: unassigned
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

**None yet.** See "Before this can be ready".

## Preconditions

**Data this task verifies against:** a clean database.

**Equipment:** none.

**Spike:** none.

## Scope

**In:**

- The `@property` lines for `datetime`-cast attributes across `app/Models`, so
  they name what the cast returns.
- Whatever the change breaks in PHPStan, which is the point of making it.

**Out:**

- Changing `Date::use(CarbonImmutable::class)`. Immutable dates are the right
  default and this task is about telling the truth, not reversing the
  decision.
- Any behaviour change. If fixing a docblock reveals a second live bug of the
  `isDue()` shape, that bug is its own task with its own test, and this one
  records it under "Found, not fixed" rather than quietly fixing it.
- `app/Data` and anything that is not an Eloquent model, unless the sweep
  finds the same inaccuracy there.

## Files

> To be filled in. The sweep is `grep -rln '@property ?Carbon' app/Models`,
> seventeen files at the time of writing.

| Path | Change | Notes |
| ---- | ------ | ----- |

Flows: none — no call chain changes.

## Database

None.

## Code

> To be filled in once the type question below is answered.

## Copy

None.

## Routes

None.

## Tests

> Probably none of its own: PHPStan is the check, and a test that asserts a
> docblock is a test of a comment. Say so explicitly rather than leaving the
> section blank — and if the answer turns out to be that one guard test is
> worth having, name it here.

## Acceptance

- [ ] No `@property` line in `app/Models` claims a `datetime` cast returns
      something it does not
- [ ] PHPStan is green afterwards, and any error the change surfaced is either
      fixed with a test or recorded as a finding with a disposition
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **Which type should the docblocks name: `CarbonImmutable` or
  `CarbonInterface`?** `CarbonImmutable` is what is actually returned and is
  the most informative. `CarbonInterface` is what call sites should usually
  depend on, is what `EpisodeService:287` already uses correctly, and would
  survive `Date::use()` being changed again. They pull in different
  directions — precision against coupling — and the answer decides every line
  in the sweep. Anyone's, but it wants deciding once and writing into
  `CLAUDE.md` so the next model does not reintroduce it.
- **Does anything outside `app/Models` carry the same claim?** `app/Data`
  shapes hold `CarbonInterface` today, which is right, but the sweep has only
  been run over the models. Ten minutes; anyone's.
- **Is one guard worth having?** An `ArchitectureTest` case that walks the
  models and refuses a `@property ?Carbon` beside a `datetime` cast would stop
  it coming back, and this codebase already prefers a test to a convention
  where a test can hold the line (`CLAUDE.md`). Anyone's.

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
