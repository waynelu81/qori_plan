---
id: T-070
title: Starter-kit leftovers nothing uses are deleted
stream: operations
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-070 — Starter-kit leftovers nothing uses are deleted

## Why

The Laravel Vue starter kit left files behind that nothing in Qori references:
a `DatabaseSeeder` that creates a "Test User", two components, three shadcn
directories, and the framework's own logo in `public/`. Each is a thing the
next reader has to rule out. The owner asked on 13 September 2026 for them to
go.

Afterwards: every file under `resources/js/components` is imported by
something, every seeder is run by something, and `public/` holds only assets
a page references or a crawler reads.

## Decisions taken to make this specifiable

**Reference, not origin, decides.** A starter file that Qori uses stays, and
several do: the auth pages, the settings pages, `UserFactory`, the tests that
still describe real behaviour. Only files with no importer, no renderer and no
runner go. Ambient type declarations (`global.d.ts`, `vue-shims.d.ts`) have
no importer by nature and stay.

**SSR is left alone.** `package.json` carries a `build:ssr` script with no
entry file to build, and `config/inertia.php` enables SSR by default. Whether
Qori renders on the server is an owner decision this task does not make; the
script and the config are noted, not touched.

**`robots.txt` stays.** Nothing imports it because crawlers read it.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The files below, and the one comment that named `DatabaseSeeder`.

**Out:**

- SSR script and config.
- Any starter file something still references.
- `tests/Unit`, which is an empty directory Git does not track, declared in
  `phpunit.xml` and harmless.

## Files

| Path                                          | Change | Notes                                    |
| --------------------------------------------- | ------ | ---------------------------------------- |
| `database/seeders/DatabaseSeeder.php`         | delete | Creates a "Test User"; nothing runs it   |
| `database/seeders/DesignReviewSeeder.php`     | edit   | One comment named it                     |
| `resources/js/components/Icon.vue`            | delete | No importer                              |
| `resources/js/components/HeadingSmall.vue`    | delete | No importer                              |
| `resources/js/components/ui/collapsible/`     | delete | No importer outside itself               |
| `resources/js/components/ui/navigation-menu/` | delete | No importer outside itself               |
| `resources/js/components/ui/select/`          | delete | No importer; pages use the native select |
| `public/logo.svg`                             | delete | The framework's wordmark; no reference   |

## Database

None.

## Code

None.

## Copy

None.

## Routes

None.

## Tests

**Changed:** none. The suite and `vue-tsc` are the check: a deleted file
something imported fails both.

## Acceptance

- [x] Each file above is gone and nothing referenced it
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

The inventory: every `.vue` under `resources/js/components` checked for an
importer by filename, every `components/ui/*` directory for an importer
outside itself, every page for a render by name in `app/`, `routes/` and
`config/`, every factory for a use in tests, every `public/` asset for a
reference in `resources/`, `app/` and `config/`.
