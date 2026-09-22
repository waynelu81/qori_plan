---
id: T-155
title: The privacy policy and terms are reachable pages
stream: reachability
status: done
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
>
> **Re-scoped 22 September 2026** at the owner's word: "can you hook up
> /terms and /privacy from the draft first." The documents no longer hold it.
> Both pages serve the drafts, say so while a draft is unfinished, and
> finishing the words is release checklist. See **Re-scope log**.

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
them. _(22 September 2026: an unfinished document is served under a "This is
a draft" notice instead; see **Re-scope log**.)_

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

**Superseded 22 September 2026: the page says it is a draft, instead of a
test refusing the document.** The owner asked for the drafts to be served
first, and a test failing on a marker would fail from the day this landed. The
line it held moves into the open: `LegalDocument::isDraft()` looks for the same
two marks — a `PLANNED`, `CHECK` or `DECIDE` marker, or a capitalised
placeholder that is not a link's text — and while either is left the page shows
"This is a draft" above the document. The notice goes by itself with the last
mark. Finishing the words is release checklist on `PLAN.md`'s gate
(`PROCESS.md`, "Release checklist is not a prerequisite"), and the concern in
**Notes**, a draft passing for a policy someone stands behind, is what the
notice answers.

**The page is `public/Legal`, not `Legal`** (22 September 2026).
`resources/js/app.ts` gives the bare layout to `Welcome`, `Pricing` and every
page under `pages/public/`, and the app's sidebar to the rest. Served as
`Legal`, the policy sat beside "Shared with me" for a visitor arriving from
Google's consent screen.

**Every heading carries an id** (22 September 2026). The privacy policy's
contents list is 32 links to its own headings, and CommonMark gives a heading
no id. `HeadingPermalinkExtension` puts one on each heading itself, unprefixed
and with no visible anchor, so `#your-rights` lands.

**The footer's two labels are a shared prop, `legal`** (22 September 2026).
The home page is a `Route::inertia` with no controller, and props written there
are fixed when the routes load, so they would not follow a request's locale
once §13 adds one. `HandleInertiaRequests` shares `legal.privacy` and
`legal.terms` from `lang/en/legal.php`.

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
- **From 22 September 2026:** moving the two drafts now, rather than once
  signed off, and a "This is a draft" notice on each page while its document
  is unfinished. The notice's tests replace the two that refused one.

**Out:**

- **Resolving the markers or the placeholders.** That is the owner's and the
  lawyer's, and it is what keeps this a draft. _(22 September 2026: it no
  longer keeps this a draft. It is release checklist, and the draft notice
  shows until it is done.)_
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
| `app/Http/Controllers/LegalController.php` | new    | `privacy()` and `terms()`, each rendering the `public/Legal` page         |
| `app/Support/LegalDocument.php`            | new    | Loads and renders one committed markdown file                             |
| `resources/js/pages/public/Legal.vue`      | new    | One page for both documents; `title`, `html` and `draft` props (under `public/` for the bare layout, 22 September 2026) |
| `resources/legal/privacy-policy.md`        | new    | Moved from `docs/pptcs/` as a draft (22 September 2026)                   |
| `resources/legal/terms-and-conditions.md`  | new    | Moved from `docs/pptcs/` as a draft (22 September 2026)                   |
| `routes/web.php`                           | edit   | The two GET routes, beside `pricing`                                      |
| `resources/js/pages/Welcome.vue`           | edit   | Footer gains both links beside the copyright line                         |
| `lang/en/legal.php`                        | new    | Page titles and the two footer labels                                     |
| `tests/Feature/Legal/LegalPageTest.php`    | new    | 11 cases (7 before 22 September 2026)                                     |
| `docs/pptcs/README.md`                     | edit   | Says where the served copy now lives, and that the page says "draft" while a marker or placeholder is left (22 September 2026) |

Flows: none — two static pages whose whole call chain is a controller reading
a committed file. Nothing in `docs/flows/` describes it and nothing should.

## Added during execution

- `app/Http/Middleware/HandleInertiaRequests.php` — shares `legal`, the
  footer's two labels, because the home page has no controller to pass them
  (see **Decisions**).
- `resources/js/types/global.d.ts` — types that shared prop.

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

**From 22 September 2026:** `LegalDocument` also has
`isDraft(string $slug): bool`, and its constructor takes
`?string $directory = null` so tests can point it at fixtures. `html()` adds
`HeadingPermalinkExtension` with `apply_id_to_heading` on, `id_prefix` and
`fragment_prefix` empty and `insert` `none`. Each action renders
`public/Legal` with `title`, `html` and `draft`: `legal.draft.title` and
`legal.draft.description` while `isDraft()`, otherwise `null`.

## Copy

| Key             | File                | English              |
| --------------- | ------------------- | -------------------- |
| `privacy.title` | `lang/en/legal.php` | Privacy Policy       |
| `terms.title`   | `lang/en/legal.php` | Terms and Conditions |
| `privacy.link`  | `lang/en/legal.php` | Privacy              |
| `terms.link`    | `lang/en/legal.php` | Terms                |
| `draft.title`   | `lang/en/legal.php` | This is a draft      |
| `draft.description` | `lang/en/legal.php` | We are still finishing it before Qori launches. Words in square brackets are still to be filled in, and some sections describe features that are not available yet. |

The two `draft` keys were added on 22 September 2026.

## Routes

| Verb | Path       | Name            | Action                    |
| ---- | ---------- | --------------- | ------------------------- |
| GET  | `/privacy` | `legal.privacy` | `LegalController@privacy` |
| GET  | `/terms`   | `legal.terms`   | `LegalController@terms`   |

## Tests

**New: `tests/Feature/Legal/LegalPageTest.php` — 11 cases** (rewritten 22
September 2026: cases 5 and 6 of the first list, which refused a served
document with a marker or a placeholder, became the draft cases 6 to 9; 5 and
11 are new). Only cases 1 and 2 read the committed documents, so finishing
them cannot break a test; the rest read fixtures.

1. `test_it_shows_the_privacy_policy_to_a_visitor` — guest `GET /privacy` is
   200 and renders `public/Legal` with its title and an `<h1>`.
2. `test_it_shows_the_terms_to_a_visitor` — the same for `GET /terms`.
3. `test_it_renders_the_document_as_html` — a heading and bold text come back
   as `<h1 id="…">` and `<strong>`, not as markdown.
4. `test_it_strips_html_comments_from_a_rendered_document` — a document
   containing `<!-- CHECK … -->` renders without it.
5. `test_it_gives_each_heading_the_id_its_contents_links_use` — `## Your
   rights` becomes `<h2 id="your-rights">`, which `[…](#your-rights)` reaches.
6. `test_it_calls_a_document_with_a_drafting_marker_a_draft`
7. `test_it_calls_a_document_with_an_unfilled_placeholder_a_draft`
8. `test_it_does_not_call_a_finished_document_a_draft` — a capitalised link
   text such as `[GDPR](…)` is not a placeholder.
9. `test_it_shows_the_draft_notice_only_while_a_document_is_unfinished` —
   through the routes, one unfinished fixture and one finished.
10. `test_it_fails_when_a_document_is_missing` — `html('nothing')` throws
    `RuntimeException`.
11. `test_it_links_both_documents_from_the_home_page` — the home page gets the
    footer's two labels.

**Changed:**

- None. No existing test reads `routes/web.php`'s root level or the Welcome
  footer.

## Acceptance

- [x] `GET /privacy` and `GET /terms` answer 200 to a signed-out visitor
- [x] Both are linked from the home page footer, and
      `php artisan qori:reachability` reports no unreachable GET route
- [x] A served document that still carries a marker or a placeholder shows
      "This is a draft", and one with neither does not (in place of "Neither
      served document contains a marker or an unfilled placeholder", 22
      September 2026)
- [x] The rendered pages read correctly at mobile and desktop widths
- [x] `docs/pptcs/README.md` says where the served copy lives
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree

## Re-scope log

- **22 September 2026, the owner: "can you hook up /terms and /privacy from
  the draft first."** Asked after a conversation about what Apple covers for
  an iOS app and what a web app has to carry itself. What changed:
  - The documents no longer hold this task. Both drafts moved to
    `resources/legal/` and are served, and each page says "This is a draft"
    while its file carries a marker or a placeholder (**Decisions**). That
    replaces the two tests which refused such a file. **Before this can be
    ready** was about the documents alone — the 93 markers, the placeholders,
    the legal entity, the lawyer's review, the support address and whether the
    two addresses are final — so its bullets moved to
    `release-prerequisites.md`, under "The privacy policy and the terms", as
    release checklist, and the heading went with them.
  - **Notes**' reprieve had already ended. `T-159` tagged `GoogleAccounts` as
    an account connector (`IntegrationServiceProvider.php:76`) ahead of
    `T-094`, so from `T-159` on a creator could reach Google's consent screen
    and its two links, and `useqori.com/privacy` and `/terms` both still
    answered 404 on 22 September 2026.
  - Found while building, each under **Decisions**: the page has to be
    `public/Legal` to get the bare layout, headings need ids for the policy's
    contents links, and the home page's footer labels travel as a shared prop.

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

**22 September 2026.** Both paragraphs above were overtaken the same day. The
owner chose a labelled draft over the 404, and the reprieve had ended with
`T-159`, not `T-094` (**Re-scope log**). Two wording fixes in **Acceptance**:
`php artisan qori:tasks --check` became `bin/tasks --check` when planning moved
to `qori-plan` on 21 September, and the marker line became the draft notice's.
Two intended line breaks in the drafts ("Effective date" above "Version", and
the address in each "Contact us") were joined into one line by CommonMark, so
each now ends in a backslash; no wording changed.
