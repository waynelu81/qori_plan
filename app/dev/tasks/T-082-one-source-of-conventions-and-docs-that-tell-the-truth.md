---
id: T-082
title: One source of conventions, and docs that tell the truth
stream: workflow
status: done
owner: claude
estimate: L
depends: none
blocks: none
---

# T-082 — One source of conventions, and docs that tell the truth

## Why

The review of 14 September 2026 (`streams/workflow.md`): developers on Cursor
and on Claude Code start from different rules. `CLAUDE.md` mirrors
`.cursor/rules/*.mdc` by hand and they already disagree — the Cursor copy says
Episodes are embedded and one person may own several Groups, and calls
`app/Exceptions` "not created yet"; `CLAUDE.md` says the queue is `sync`
everywhere in one section and `deferred` in another, and tells the reader
not to commit a committed file. Six conventions are stated only in prose and
are already broken: inline `validate()` in five controllers, one inline
user-facing string, no test that Services carry no vendor HTTP or that `env()`
stays in `config/`. `docs/flows/series.md` says episodes are embedded, a
tinker recipe prints "there is no episodes table", `terminology-refactor.md`
tells the reader to keep `Workspace` and `Course`, and `project-plan.md`
§20–24 describe a reversed design in old names while `CLAUDE.md` rule 1 sends
every developer there. Two comments claim a flashed toast never shows on a
full page load; Inertia's source fires the flash event on the initial page
and the listener is registered before it.

## Decisions taken to make this specifiable

**`CLAUDE.md` is canonical.** Each `.cursor/rules/*.mdc` becomes front matter
plus one line pointing at the `CLAUDE.md` section; `DocumentationTest`
asserts no `.mdc` exceeds twelve lines or contains a rule sentence.

**An `ArchitectureTest` in the shape of `ConsoleAccessTest`**: walk `app/`,
`str_contains`, an allow-list with a reason per entry, `assertSame([])`.
Rules: no `Http::`/`StripeHttpClient`/vendor SDK in `app/Services`; no
`env(` outside `config/`; no `->validate(` in controllers; no `__('` whose
key contains a space or full stop; no `$request->user()`/`auth()->user()`
outside `App\Support\CurrentUser` and `HandleInertiaRequests`; no
`implements ShouldQueue`; no `use App\Services` or `use App\Http` inside
`app/Integrations`. `Share/EpisodeController.php` is allow-listed with the
reason "T-083 converts it"; the merge removes the entry.

**Architecture docs in current names**: `docs/architecture/{stack,tenancy,
sessions,errors,admin-console}.md` written from `project-plan.md` §20–24 with
the vocabulary mapping in `decisions.md`; the old sections are stubbed with a
dated pointer; `CLAUDE.md` rule 1 points at `docs/architecture/`.

**The toast comments are corrected, not the mechanism.** Inertia core's
`fireInitialEvents` queues the flash event on the initial page and
`app.ts` registers the listener at module level, so a flashed toast does show
after a full load. The `notice` prop stays for its UX reason.

## Preconditions

None. `T-080`, `T-081` and `T-083` run alongside and do not touch this task's
files. `T-081` makes `types:check` clear the PHPStan cache; this task deletes
the trap paragraph in `CLAUDE.md` that the change makes obsolete.

## Scope

**In:**

- `CLAUDE.md`: queue sentence → "deferred locally and in production, `sync`
  in tests, nothing `ShouldQueue`"; delete "Do not commit this file."; delete
  the PHPStan cache paragraph; list `planning.mdc` beside the other two;
  reword the Integrations rule to what the code does ("take Models and Enums
  in, hand `app/Data` or scalars out; never import `app/Services` or
  `app/Http`"); rule 1 points at `docs/architecture/`; the product-nouns
  pointer says `terminology-refactor.md` is history and the code is the
  authority; the board bullets already changed stay.
- `.cursor/rules/laravel-conventions.mdc`, `api-responses.mdc`,
  `testing-conventions.mdc`, `planning.mdc` reduced to pointers.
- `tests/Feature/ArchitectureTest.php` and the fixes it needs: Form Requests
  for `Admin/StaffSessionController`, `Admin/StaffTwoFactorController` (two),
  `Auth/MagicLinkLoginController`; `SecurityController` toast message to
  `lang/en/profile.php`; `SnsWebhookController`'s `Validator` allow-listed
  with its reason.
- `tests/Feature/DocumentationTest.php`: the `.mdc` size rule; a list of
  now-false claims ("embedded", "There is no episodes table", "Postmark
  (unwired)", "Workspace", "Course", "Lesson", "Enrolment" as nouns) checked
  over `docs/flows`, `docs/tinker`, `docs/architecture`, `CLAUDE.md` and
  `.cursor`, with the allow-list shape the database-history check uses.
- `docs/flows/series.md` embedded-episodes lines; `docs/tinker/series.md`
  recipe deleted; `docs/tinker/README.md` and `docs/flows/auth.md` "Postmark
  (unwired)"; `docs/flows/README.md` line 18; new `docs/flows/billing.md`
  (plan subscription, portal, webhook, Connect payouts moved out of
  `checkout.md`) and `docs/flows/onboarding.md` (setup parts, the record on
  the person, the home-route rule); `docs/planning/terminology-refactor.md`
  implementation boundary struck with a dated pointer to the decision.
- `docs/architecture/*.md` and the stubs in `docs/project-plan.md`.
- The two toast comments: `app/Http/Controllers/PublicSeriesController.php`
  and `tests/Feature/Checkout/ConfirmingTest.php`.

**Out:**

- A JavaScript test runner; loosening the string-reading sign-in tests.
- `docs/planning/PROCESS.md`, `README.md` at the root, stream files —
  `T-080` and `T-081` own those.
- `Share/EpisodeController.php` and anything under `routes/` — `T-083`.
- Terminology resolution style (`app()` versus injection).

## Files

| Path                                                      | Change | Notes                                                |
| --------------------------------------------------------- | ------ | ---------------------------------------------------- |
| `CLAUDE.md`                                               | edit   |                                                      |
| `.cursor/rules/laravel-conventions.mdc`                   | edit   | Pointer                                              |
| `.cursor/rules/api-responses.mdc`                         | edit   | Pointer                                              |
| `.cursor/rules/testing-conventions.mdc`                   | edit   | Pointer                                              |
| `.cursor/rules/planning.mdc`                              | edit   | Pointer                                              |
| `tests/Feature/ArchitectureTest.php`                      | new    |                                                      |
| `tests/Feature/DocumentationTest.php`                     | edit   |                                                      |
| `app/Http/Controllers/Admin/StaffSessionController.php`   | edit   | Form Request                                         |
| `app/Http/Controllers/Admin/StaffTwoFactorController.php` | edit   | Form Requests                                        |
| `app/Http/Controllers/Auth/MagicLinkLoginController.php`  | edit   | Form Request                                         |
| `app/Http/Requests/Admin/StaffLoginRequest.php`           | new    |                                                      |
| `app/Http/Requests/Admin/StaffTwoFactorCodeRequest.php`   | new    | One request for both code actions if the rules match |
| `app/Http/Requests/Auth/MagicLinkRequest.php`             | new    |                                                      |
| `app/Http/Controllers/Settings/SecurityController.php`    | edit   | Lang key                                             |
| `app/Http/Controllers/Settings/ProfileController.php`     | edit   | Only if the test finds a bypass                      |
| `lang/en/profile.php`                                     | edit   |                                                      |
| `app/Http/Controllers/PublicSeriesController.php`         | edit   | Comment                                              |
| `tests/Feature/Checkout/ConfirmingTest.php`               | edit   | Comment                                              |
| `docs/flows/README.md`                                    | edit   |                                                      |
| `docs/flows/series.md`                                    | edit   |                                                      |
| `docs/flows/auth.md`                                      | edit   |                                                      |
| `docs/flows/checkout.md`                                  | edit   | Payouts moved out                                    |
| `docs/flows/billing.md`                                   | new    |                                                      |
| `docs/flows/onboarding.md`                                | new    |                                                      |
| `docs/tinker/README.md`                                   | edit   |                                                      |
| `docs/tinker/series.md`                                   | edit   |                                                      |
| `docs/architecture/stack.md`                              | new    |                                                      |
| `docs/architecture/tenancy.md`                            | new    |                                                      |
| `docs/architecture/sessions.md`                           | new    |                                                      |
| `docs/architecture/errors.md`                             | new    |                                                      |
| `docs/architecture/admin-console.md`                      | new    |                                                      |
| `docs/project-plan.md`                                    | edit   | §20–24 stubbed                                       |
| `docs/planning/terminology-refactor.md`                   | edit   | Banner                                               |
| `tests/Feature/Admin/*.php`, `tests/Feature/Auth/*.php`   | edit   | Only where a Form Request changes an error shape     |

## Database

None.

## Code

```php
// tests/Feature/ArchitectureTest.php — one method per rule, e.g.
public function test_services_make_no_vendor_http_calls(): void;
public function test_env_is_read_only_in_config(): void;
public function test_controllers_validate_through_form_requests(): void;
public function test_no_user_facing_string_is_inline(): void;
public function test_the_request_user_goes_through_current_user(): void;
public function test_nothing_is_queued_before_a_worker_exists(): void;
public function test_integrations_import_no_app_layer(): void;
```

Each rule holds an `ALLOW` array of `path => reason` and asserts the offenders
minus the allow-list are `[]`, and a companion assertion that every allowed
path exists (`ConsoleAccessTest` shape).

## Copy

| Key                        | File                  | English             |
| -------------------------- | --------------------- | ------------------- |
| `profile.password_updated` | `lang/en/profile.php` | `Password updated.` |

## Routes

None.

## Tests

**New: `tests/Feature/ArchitectureTest.php` — 7 cases**, named above.

**Changed: `tests/Feature/DocumentationTest.php` — 2 new cases**

1. `test_every_cursor_rule_is_a_pointer_to_claude_md`
2. `test_no_live_document_makes_a_claim_the_code_reversed`

**Changed:** admin and auth tests only if a Form Request changes the error
key or redirect; say which in the report.

## Acceptance

- [x] `.cursor/rules/*.mdc` are pointers; `CLAUDE.md` has no contradiction on the queue, committing, or Episodes
- [x] `ArchitectureTest` passes with an allow-list a reader can audit
- [x] `docs/architecture/` reads in current names and `project-plan.md` §20–24 point at it
- [x] No live doc says episodes are embedded, Postmark is unwired, or the model is named Course
- [x] `npm run check:fix` run; `composer ci:check` green from a clean tree
- [x] Report written in `reports/`

## Re-scope log

None.

## Added during execution

| Path                    | Change | Reason                                                                                                                                                      |
| ----------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/flows/storage.md` | edit   | Carried two "embedded" claims the new `DocumentationTest` case names; it is a flow doc, which this task owns by stream, but the Files table did not list it |

## Notes

`T-083` converts `Share/EpisodeController`'s two inline validations; the
allow-list entry here is removed at the merge. Keep the rest of `CLAUDE.md`'s
voice: the rule, the failure that produced it, the exact command.

The `__('` rule in Decisions cannot be built as written — every lang key
contains full stops — so it is built as "a space anywhere, or a sentence
terminator at the end". The report has the rest.
