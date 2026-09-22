---
id: T-155
title: The privacy policy and terms are reachable pages
stream: reachability
status: doing
owner: claude
estimate: S
depends: none
blocks: none
---

# T-155 — The privacy policy and terms are reachable pages

> **Drafted 20 September 2026**, the day the owner pressed Publish app on the
> Google Cloud project. The consent screen every creator will see carries a
> privacy policy link and a terms link, both of which 404 today. The code here
> is half a day; what keeps this a draft is the documents, not the routes —
> see **Before this can be ready**.

## Why

`docs/pptcs/privacy-policy.md` and `docs/pptcs/terms-and-conditions.md` were
written on 19 September 2026 and nothing serves them. `routes/web.php` has no
privacy or terms route, and `https://useqori.com/privacy` and
`/terms` both answer 404 (checked 20 September 2026). Google's Branding page
for the published OAuth app points at both addresses, so the app is telling
every creator that a privacy policy exists where there is none; the beta gate
in `PLAN.md` asks for the same two documents, and brand verification checks
that the policy is live on the home page's domain.

Afterwards both are pages a visitor can read without an account, linked from
the home page footer, and a test refuses to let an unfinished document reach
them.

## Decisions taken to make this specifiable

**The document body is content, not interface copy, and stays in a markdown
file rather than `lang/en/`.** §23 puts every string a person reads into a
lang file so a second locale is a translation rather than a hunt, and that
rule is aimed at interface copy: a sentence assembled with a noun in it, a
button, an error. A nine-hundred-line legal document in a PHP array is
unreadable and unreviewable by the lawyer who has to sign it, and a translated
legal document is a separate legal act rather than a translation. The page's
own chrome — its title, its heading, the footer links — is interface copy and
does go in `lang/en/legal.php`.

**The served copy lives in `resources/legal/`, not `docs/pptcs/`.** A runtime
page must not read from `docs/`, whose own README frames those two files as
drafts carrying resolvable markers; the two directories answer different
questions, and a page that reads the drafting workspace publishes whatever
state it is in. The files move as part of this task, once the content is
signed off. `docs/pptcs/README.md` stays where it is as the research record of
what each vendor requires.

**Rendered per request with `Str::markdown()` and `html_input` set to
`strip`.** Stripping means the HTML-comment markers cannot reach the page even
if one survives review, and no raw HTML can enter the page from the file at
all. These are two pages read rarely; caching the render buys nothing worth
the invalidation bug it invites.

**`v-html` is correct here and is not the usual smell.** The source is a
committed file rendered by CommonMark with HTML stripped, never user input and
never a vendor payload.

**Paths `/privacy` and `/terms`, at root.** §"Route namespaces" leaves root to
`/`, `/dashboard` and well-known URIs; these are well-known, `/pricing`
already sits beside them, and `docs/pptcs/README.md` assumed these two exact
addresses when it researched what each vendor asks for. Route names are
`legal.privacy` and `legal.terms`, so Wayfinder gives
`import { privacy, terms } from '@/routes/legal'`.

**A test, not a README line, is what holds the publish blocker.**
`docs/pptcs/README.md` says every `PLANNED`, `CHECK` and `DECIDE` marker is a
publish blocker, and a sentence in a README blocks nothing. Two test cases
walk `resources/legal/*.md` and fail on a marker or on an unfilled
`[PLACEHOLDER]`, so a document cannot be served half-finished by accident.

## Preconditions

**Data this task verifies against:** a clean database. Neither page reads a
row.

**Equipment:** none. Both pages are checked from the terminal.

## Scope

**In:**

- Two unauthenticated GET routes, a controller, one Vue page and a small
  loader that renders a committed markdown file.
- Moving the two signed-off documents to `resources/legal/`.
- Footer links from the home page.
- Tests, including the two that refuse an unfinished document.

**Out:**

- **Resolving the markers or the placeholders.** That is the owner's and the
  lawyer's, and it is what keeps this a draft.
- **A version history or an "effective date" changelog.** The documents carry
  a `Version:` line; when one changes materially, the people it binds have to
  be told, and that is its own task in `delivery`.
- **Consent capture** — recording that a person accepted a version. Separate,
  and not needed to answer Google.
- **A cookie or consent banner.** Qori sets no third-party tracking cookie.
- Linking from anywhere but the home page footer. Sign-up and checkout are
  where a version-accepted record would belong, and that is Out above.

## Files

| Path                                       | Change | Notes                                                                     |
| ------------------------------------------ | ------ | ------------------------------------------------------------------------- |
| `app/Http/Controllers/LegalController.php` | new    | `privacy()` and `terms()`, each rendering the `Legal` page                |
| `app/Support/LegalDocument.php`            | new    | Loads and renders one committed markdown file                             |
| `resources/js/pages/Legal.vue`             | new    | One page for both documents; `title` and `html` props                     |
| `resources/legal/privacy-policy.md`        | new    | Moved from `docs/pptcs/`, markers and placeholders resolved               |
| `resources/legal/terms-and-conditions.md`  | new    | Moved from `docs/pptcs/`, markers and placeholders resolved               |
| `routes/web.php`                           | edit   | The two GET routes, beside `pricing`                                      |
| `resources/js/pages/Welcome.vue`           | edit   | Footer gains both links beside the copyright line                         |
| `lang/en/legal.php`                        | new    | Page titles and the two footer labels                                     |
| `tests/Feature/Legal/LegalPageTest.php`    | new    | 7 cases                                                                   |
| `docs/pptcs/README.md`                     | edit   | Says where the served copy now lives and that a test enforces the markers |

Flows: none — two static pages whose whole call chain is a controller reading
a committed file. Nothing in `docs/flows/` describes it and nothing should.

## Database

None.

## Code

```php
namespace App\Support;

class LegalDocument
{
    public const DIRECTORY = 'legal';

    /** @throws \RuntimeException when no document is committed under $slug */
    public function html(string $slug): string;
}
```

```php
namespace App\Http\Controllers;

class LegalController extends Controller
{
    public function __construct(private LegalDocument $documents) {}

    public function privacy(): Response;

    public function terms(): Response;
}
```

`html()` reads `resource_path('legal/'.$slug.'.md')` and returns
`Str::markdown($contents, ['html_input' => 'strip', 'allow_unsafe_links' => false])`.
Each action passes `title` from `lang/en/legal.php` and `html` to
`Inertia::render('Legal', …)`.

## Copy

| Key             | File                | English              |
| --------------- | ------------------- | -------------------- |
| `privacy.title` | `lang/en/legal.php` | Privacy Policy       |
| `terms.title`   | `lang/en/legal.php` | Terms and Conditions |
| `privacy.link`  | `lang/en/legal.php` | Privacy              |
| `terms.link`    | `lang/en/legal.php` | Terms                |

## Routes

| Verb | Path       | Name            | Action                    |
| ---- | ---------- | --------------- | ------------------------- |
| GET  | `/privacy` | `legal.privacy` | `LegalController@privacy` |
| GET  | `/terms`   | `legal.terms`   | `LegalController@terms`   |

## Tests

**New: `tests/Feature/Legal/LegalPageTest.php` — 7 cases**

1. `test_it_shows_the_privacy_policy_to_a_visitor` — guest `GET /privacy` is
   200 and renders the `Legal` component.
2. `test_it_shows_the_terms_to_a_visitor` — the same for `GET /terms`.
3. `test_it_renders_the_document_as_html` — the `html` prop carries the
   document's first heading as an `<h1>`, not as markdown.
4. `test_it_strips_html_comments_from_a_rendered_document` — a document
   containing `<!-- CHECK … -->` renders without it.
5. `test_it_keeps_no_unresolved_marker_in_a_served_document` — every file in
   `resources/legal/` is free of `PLANNED`, `CHECK` and `DECIDE`.
6. `test_it_keeps_no_unfilled_placeholder_in_a_served_document` — every file
   in `resources/legal/` is free of `[UPPER CASE]` placeholders.
7. `test_it_fails_when_a_document_is_missing` — `html('nothing')` throws
   `RuntimeException`.

**Changed:**

- None. No existing test reads `routes/web.php`'s root level or the Welcome
  footer.

## Acceptance

- [ ] `GET /privacy` and `GET /terms` answer 200 to a signed-out visitor
- [ ] Both are linked from the home page footer, and
      `php artisan qori:reachability` reports no unreachable GET route
- [ ] Neither served document contains a marker or an unfilled placeholder
- [ ] The rendered pages read correctly at mobile and desktop widths
- [ ] `docs/pptcs/README.md` says where the served copy lives
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree

## Before this can be ready

The code above is specified. Every bullet here is about the documents, and
each one is the owner's.

- **93 publish-blocking markers have to be resolved** — 46 in the privacy
  policy (23 `PLANNED`, 21 `CHECK`, 2 `DECIDE`) and 47 in the terms (28
  `PLANNED`, 9 `CHECK`, 10 `DECIDE`). `docs/pptcs/README.md` calls every one
  of them a publish blocker. `PLANNED` is the worst of the three: it marks
  text describing something Qori does not do yet, which in a privacy policy is
  not a placeholder but a false statement.
- **97 unfilled placeholders have to be filled** — 59 occurrences across 25
  distinct names in the policy, 38 across 14 in the terms. They render
  visibly: a visitor would read `[PRIVACY CONTACT EMAIL]`.
- **`[LEGAL ENTITY NAME]` and `[REGISTERED OR BUSINESS ADDRESS]` are not a
  wording question.** Both documents need a legal person to bind, and Qori
  does not name one yet. This is the largest bullet here and probably not the
  owner's alone.
- **An Australian lawyer must review both**, which `docs/pptcs/README.md`
  states as a requirement rather than a suggestion. Everything above should be
  resolved before that review rather than during it.
- **The support address has to exist and be monitored.** `[SUPPORT EMAIL]`
  appears 12 times across the two documents, and the same address is the user
  support email on Google's consent screen, where every creator sees it. A
  Cloudflare Email Routing rule is needed per address, so an address named
  here that has no rule bounces — the trap already recorded for `dmarc@` in
  `release-prerequisites.md`.
- **Whether `/privacy` and `/terms` are the final addresses**, since they are
  registered on Google's Branding page and changing one means editing it
  again. `docs/pptcs/README.md` assumed both.

## Re-scope log

None.

## Notes

The engineering here is deliberately small and the task is deliberately a
draft anyway. Splitting the routes out to ship ahead of the content was
considered and rejected: a page serving a document that says `[LEGAL ENTITY
NAME]` is worse than a 404, because a 404 is visibly broken and a published
draft looks like a policy someone stands behind.

What makes the 404 survivable in the meantime is that nothing reaches the
consent screen. `IntegrationServiceProvider` tags an empty
`account-connectors` list until `T-094`, so the Integrations section is
hidden and no creator can start a Google connect. That is a reprieve, not a
fix, and it ends the day `T-094` lands.
