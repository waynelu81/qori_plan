---
id: T-148
title: An upload nobody attached is swept
stream: operations
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-148 — An upload nobody attached is swept

> Start one with `php artisan qori:tasks --new <stream> <slug>`, which copies
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

An upload is confirmed before the form that uses it is saved. `FileUpload.vue`
signs, PUTs and confirms as soon as a file is chosen, and
`UploadService::confirm()` copies it under its live prefix and marks the
`media_assets` row `stored`; only the later form submit attaches it — as an
Episode's `content['path']`, or since `T-130` as a material's
`media_asset_id`. A creator who chooses a file and then closes the page, picks
another file with "Replace", or has the save refused leaves a stored object
under `episodes/` or `materials/` and a row that nothing points at. Nothing
deletes either: the R2 lifecycle rule covers `incomingUploads/` only, and
`MaterialService::remove()` and `SeriesService::purge()` reach an object
through the row that attaches it. Found while building `T-130`
(`reports/T-130-2026-09-19-wayne.md`). Afterwards a stored upload that nothing
has attached for long enough is deleted, object and row, by one sweep.

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
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- How long a stored, unattached upload is kept before the sweep takes it: long
  enough that a creator mid-form never loses a file — the owner's.
- Whether the sweep is a scheduled `qori:*` command or runs inside an existing
  one, given the queue is `deferred` and cannot retry (stream `operations`,
  `T-018`) — anyone's.
- What "attached" means in one query, across `episodes.content->>'path'` and
  `materials.media_asset_id`, and whatever `T-132`'s chat QR image adds —
  anyone's, read from the code when this is specified.

## Re-scope log

> Empty until something in the spec turns out to be wrong. Then: what was
> expected, what was found, and what it means for the spec. Set
> `status: rescope` and stop.

None.

## Notes

> Anything learned that the next reader would want and that does not belong in
> `decisions.md`.

None.
