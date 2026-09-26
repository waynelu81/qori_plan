---
id: T-203
title: A test request starts with no current group
stream: workflow
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-203 — A test request starts with no current group

> Start one with `bin/tasks --new <stream> <slug>`, which copies
> this file under the next free id. Keep every heading, and delete the
> guidance in quotes. A section that does not apply says **None**, so a reader
> can tell "nothing to do here" from "nobody thought about it".
>
> `blocks:` is derived from every other task's `depends:` and a test asserts
> the field agrees with the derivation; write it for the reader, and fix it
> when the board says so.
>
> Read [`../PROCESS.md`](../PROCESS.md) first if you have not.

## Why

`CurrentGroup` is bound `scoped()` (`app/Providers/AppServiceProvider.php:31`)
and `SetCurrentGroup` fills it with a bare `set()`
(`app/Http/Middleware/SetCurrentGroup.php:46`). A real request starts in a
fresh container, but one test's requests share one application, so a Peer
request made after a creator request in the same test runs with the
creator's Group still current. That hides exactly the bug the Peer surface
is most exposed to — a group-scoped read with no `CurrentGroup::runFor()` —
because the leftover Group answers it. `T-126`'s and `T-127`'s tests work
round it by hand (`RecordingTest`'s `paste()` through `runFor()`,
`RecordingStateTest`'s `asPeer()` calling `forget()`); afterwards every test
request starts with no current Group, as a real one does, and those
workarounds can go (found by `T-127`'s test writer, 26 September 2026).

## Decisions taken to make this specifiable

> Every choice the spec makes that somebody could reasonably have made the
> other way, each as one bold sentence and its reason. This is where a draft
> becomes a spec: a task with a decision still open in it is not ready, and a
> decision hidden inside the Code section is one the developer will re-make.
> **None** only when the task genuinely had no choices in it.

## Preconditions

> Anything that must be true of the machine before this task can be done or
> verified — a running container, a generated directory, credentials, seeded
> data. **None** if it runs from a clean checkout.
>
> Worth its own section because a check that silently reads an empty directory
> reports success. `resources/js/routes` is generated and gitignored, so
> anything analysing it needs `php artisan wayfinder:generate --with-form`
> first, and finds nothing at all without it.

**Data this task verifies against:** > The rows the check needs — a seeded
world, a Group in a particular state, a realistic row count — and how to get
them (`php artisan qori:reset …`, a factory, a fixture). **A clean database**
when nothing more is needed.

**Equipment:** > A visible browser, vendor credentials, a mailbox, a phone —
whatever a check needs that a shell does not have. **None** when everything
can be verified from the terminal.

> **Spike, for vendor-facing work.** A spec that names a vendor payload cites
> where the shape came from: an observed response (the date and the call), or
> a committed fixture under `tests/Fixtures/<vendor>/`. Guessing the field
> names from documentation is how `contact_email` became `peer_email` and
> how a v2 requirements summary read "nothing outstanding" for an account
> that had not started. If nobody has seen the response, the first step is a
> spike that does, and its result is a fixture, not a memory.

## Scope

**In:**

- …

**Out:**

- …

> Name the things a reader would reasonably assume are included and are not.
> "Out" is the section that prevents a task from growing while it is being done.

## Files

| Path             | Change | Notes |
| ---------------- | ------ | ----- |
| `app/…`          | new    | …     |
| `resources/js/…` | edit   | …     |

> Every file, exactly, one row per file or several backticked paths in one
> cell — the parser reads all of them, expands a glob against the repository,
> and refuses a bare basename (`SeriesService.php` claims nothing the collision
> check can compare). Two `doing` tasks listing the same path is a collision
> the board will show — see PROCESS.md.
>
> **Wiring.** A file that is new is not reached by anything until something
> is edited to reach it. Go down this list and add the rows:
>
> - a route, in `routes/*.php`, for a new controller action
> - a nav or a link, for a new page; `qori:reachability` finds the ones you forget
> - a lang file, for every sentence a person reads
> - a flow doc, for a changed call chain: a `docs/flows/*.md` row here, or the
>   line below when nothing in `docs/flows/` describes the chain this touches
> - a tinker recipe, when a `docs/tinker/*.md` recipe drives what changed
> - `config/qori.php`, for a number that would otherwise be written twice
> - a factory or the design-review seeder, for a new column
>
> A task whose Files include anything under `app/Http`, `app/Services`,
> `app/Listeners` or `routes/` must either list a `docs/flows/*.md` path or
> carry the line below, and a test checks it.

Flows: none — > why no flow file changes, in a few words; delete this line
when a flow row is in the table.

## Database

> Table, column, type, nullability, default, index or constraint, and the
> migration's file name. **None** if the task touches no schema.

| Table | Column | Type | Null | Default | Index / constraint |
| ----- | ------ | ---- | ---- | ------- | ------------------ |

Migration: `database/migrations/YYYY_MM_DD_HHMMSS_<name>.php`

## Code

> Literal names. Namespaces, class names, method signatures with types,
> property and constant names. Enough that two developers would write the same
> declarations.

```php
namespace App\…;

class Thing
{
    public const SOME_KEY = 'value';

    public function doIt(Group $group, string $name): Result;
}
```

## Copy

> Every user-facing string, as a lang key and its file. Never inline (§23).
> **None** if the task adds no copy.

| Key | File | English |
| --- | ---- | ------- |

## Routes

> Verb, path, route name, controller action. **None** if no routes change.

| Verb | Path | Name | Action |
| ---- | ---- | ---- | ------ |

## Tests

> One line per case with its method name, and the total. A reviewer counts them
> against the file. Say which existing tests are expected to change and why.

**New: `tests/Feature/…Test.php` — N cases**

1. `test_it_…` — …

**Changed:**

- `tests/…` — …

## Acceptance

> The product lines first, then the closing lines in this order — status and
> the board check come before the gate, because the gate includes the board
> check and a task that is `done` with `status: doing` fails it.

- [ ] …
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Where the reset lives: a hook in `Tests\TestCase` around each request
  (Laravel's `beforeApplicationDestroyed()` is per test, not per request),
  or a terminating callback in `SetCurrentGroup`, or forgetting scoped
  instances between requests the way Octane does — anyone's, from the code.
- Which existing tests lean on the leak today and start failing once it is
  gone — anyone's: run the suite with the reset in place and list them.

## Re-scope log

> Empty until something in the spec turns out to be wrong. Then: what was
> expected, what was found, and what it means for the spec. Rewrite the
> sections it changes and carry on — or, if you are handing the task back,
> set `status: rescope` so the next person rewrites it.

None.

## Notes

> Anything learned that the next reader would want and that does not belong in
> `decisions.md`.

None.
