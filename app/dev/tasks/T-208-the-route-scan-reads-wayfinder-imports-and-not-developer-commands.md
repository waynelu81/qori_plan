---
id: T-208
title: The route scan reads Wayfinder imports, and not developer commands
stream: reachability
status: doing
owner: claude
estimate: S
depends: none
blocks: none
---

# T-208 — The route scan reads Wayfinder imports, and not developer commands

## Why

`T-051` took `routes/` and `tests/` out of the route half's haystack, and the
first run after it still reported no route. Classifying the evidence on
27 September 2026 found why three of the 47 GET routes pass: `security.edit`,
`share.vocabulary.edit` and `share.peers.index` are named in `app/` only by
`DesignReviewCommand`, a developer command that prints review URLs. Each is
reachable in the product — the settings layout imports `@/routes/security`,
the sidebar builds `` `${base}/peers` `` and the Group settings layout
`` `${base}/settings/vocabulary` `` — but the scan cannot see either shape: a
Wayfinder import names a module path and an export, not a route name, and
`${base}/…` hides the `/g/{group}` prefix the URI pattern needs. The scan is
right about the three by accident, and would call them unreachable the day the
command stopped naming them.

Afterwards a Wayfinder import of a route's helper counts as a link to that
route, a developer command does not, and the six hand-built `${base}/…` links
are Wayfinder calls the scan can read.

## Decisions taken to make this specifiable

Brought to ready on 27 September 2026, from the code and the generated files.

**A Wayfinder import is matched by deriving the import from the route's
name, not by reading the generated files.** Every route import in
`resources/js` is a named import, `import { edit as editSecurity } from
'@/routes/security'`, some over several lines, and none is a namespace
import. Wayfinder files a route named `a.b.c` in the module `@/routes/a/b`
under the export `c`, keeping the segments' dashes in the path and their
underscores in the export (`not_recorded`), camel-casing the last segment's
dashes (`series.sign-in` → `signIn`), and suffixing a JavaScript reserved word
with `Method` (`series.public` → `publicMethod`). The scan applies the same
rule forward from each route's name and looks for that export in an import
from that module. The generated files are gitignored and exist only after
generation, and they record a route's URL, not its name; the scan must work
from a clean checkout.

**`app/Console` stops counting as a way in.** A command's output reaches a
developer, not a person. Everything else in `app/` stays: a redirect, an
email, a vendor's return address, a URL in a prop. `app/Admin` is the staff
console, which is a real audience, and stays.

**The six `${base}/…` links become Wayfinder calls**, rather than the scan
learning to read `${base}`: they are the only such links (in
`AppSidebar.vue` and `layouts/share-settings/Layout.vue`), a helper call is
checked by the type checker where a hand-built path is not, and matching a
variable named `base` would be a rule about one spelling. The URI pattern
stays for the `/g/${…}/…` paths the pages build in full.

## Preconditions

None. The scan reads source files; nothing generated is needed.

**Data this task verifies against:** the fixture trees under
`tests/Fixtures/reachability/`, and the real tree's run.

**Equipment:** a browser, to click the six converted links once.

## Scope

**In:**

- The route half's haystack and matching: Wayfinder imports counted,
  `app/Console` left out.
- The six `${base}/…` hrefs as Wayfinder calls.
- The real tree's run, recorded in `app/dev/reachability.md`.

**Out:**

- The method half, which `T-051` left alone for the same reason.
- Any other hand-built URL; the URI pattern keeps reading the full ones.

## Files

| Path                                                                         | Change | Notes                                       |
| ---------------------------------------------------------------------------- | ------ | ------------------------------------------- |
| `app/Support/Reachability.php`                                               | edit   | Wayfinder imports; no `app/Console`         |
| `resources/js/components/AppSidebar.vue`                                     | edit   | four hrefs as Wayfinder calls               |
| `resources/js/layouts/share-settings/Layout.vue`                             | edit   | two hrefs as Wayfinder calls                |
| `tests/Feature/ReachabilityTest.php`                                         | edit   | 5 cases                                     |
| `tests/Fixtures/reachability/wayfinder/resources/js/pages/Imports.vue`       | new    | named, aliased, multi-line and renamed ones |
| `tests/Fixtures/reachability/command-only/app/Console/Commands/PrintsIt.php` | new    | a route only a command names                |

Flows: none — a developer tool and two navigation links; no flow describes
either.

## Database

None.

## Code

```php
// App\Support\Reachability

/** JavaScript's reserved words, which Wayfinder suffixes with "Method". */
private const RESERVED = ['break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default', 'delete', 'do', 'else', 'enum', 'export', 'extends', 'false', 'finally', 'for', 'function', 'if', 'implements', 'import', 'in', 'instanceof', 'interface', 'let', 'new', 'null', 'package', 'private', 'protected', 'public', 'return', 'static', 'super', 'switch', 'this', 'throw', 'true', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield'];

// haystack(): the frontend and app/, less app/Console.
// wayfinderImports(string $frontend): array<string, true>  — "module|export" for every
//     name in every `import { … } from '@/routes…'`, aliases dropped.
// isLinked(): … || isset($imports[self::wayfinderImport($route->getName())])
// wayfinderImport(string $name): string — "@/routes/a/b|c" by the rule above
```

## Copy

None. Console output aimed at a developer is a diagnostic, not copy.

## Routes

None.

## Tests

**Changed: `tests/Feature/ReachabilityTest.php` — 5 new cases**

1. `test_a_route_imported_through_wayfinder_is_linked` — a named import with
   an alias.
2. `test_a_multi_line_import_counts_every_name_in_it`.
3. `test_a_dashed_or_reserved_route_name_is_matched_as_wayfinder_exports_it`
   — `sign-in` as `signIn`, `public` as `publicMethod`, `not_seen` as itself.
4. `test_an_import_from_another_module_does_not_count` — the same export name
   from a different module links nothing.
5. `test_a_route_named_only_by_a_console_command_is_reported`.

The existing cases pass unchanged.

## Acceptance

- [ ] A route reached only through a Wayfinder import in a `.vue` or `.ts`
      file is not reported
- [ ] A route named only by a command under `app/Console` is reported
- [ ] The sidebar and the Group settings links go where they went, as
      Wayfinder calls
- [ ] The real tree's run is recorded in `app/dev/reachability.md`
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~How a Wayfinder import maps to a route: read the generated
  `resources/js/routes/**` (which needs generating in CI), or derive the
  module path and export from the route's name — `security.edit` is
  `@/routes/security` and `edit` — without reading generated files. Anyone's,
  from how Wayfinder names them.~~ **Answered from the code, 27 September
  2026:** derived from the name (Decisions).
- ~~Whether `app/Console` is the whole of "developer-only" in `app/`, or whether
  other places name routes for developers only. Anyone's, from the code.~~
  **Answered from the code, 27 September 2026:** it is; the staff console is
  a real audience (Decisions).
- ~~Whether `${base}/…` template literals are worth matching, or whether every
  such link should become a Wayfinder import instead. Anyone's.~~ **Decided,
  27 September 2026:** the six become Wayfinder calls (Decisions).

## Re-scope log

None.

## Notes

Found by `T-051` on 27 September 2026; its report has the evidence, and
`app/dev/reachability.md` the run.
