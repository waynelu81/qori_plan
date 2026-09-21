# UI/UX redesign

> Approved five-day redesign direction, interaction contract, QA matrix and release gate.

**Onboarding update, 2026-09-11:** the owner has since specified separate
Series-linked receiving onboarding and staged creator setup before guided
first-Series creation. See the [decision](decisions.md#onboarding-follows-the-entry-purpose-2026-09-11)
and [current onboarding plan](ui-onboarding.md). That direction supersedes this
brief's initial creator entry ordering; its direct-action, accessibility and
truthful-state contracts still apply within the relevant stage.

[Current plan](../../PLAN.md) | [Planning index](README.md) | [Terminology refactor](terminology-refactor.md)

Recorded 2026-09-08 after looking at the live surfaces, not from a moodboard.

A user who calls the UI ugly is describing **boilerplate chrome + empty inventory + no brand**. The backend, Connect, and nav modes ran ahead of a look. The earlier “Sharing is caring” direction is now retired; the product-language refactor is part of this pass, not decoration applied afterwards.

This is **one design week**, then stop. It is not a second visual language, not custom illustration, not Skool’s dark social feed, and not “add more KPI tiles.” Six zeros is worse than one sentence and a button.

## Honest review (2026-09-08)

**Verdict: the direction is strong; the original brief was not yet safe to hand to a developer without interpretation.** It correctly identifies the real problem — Qori shows system state before it shows something worth sharing — and its best decisions are the one-action `TeachDigest`, the object-first empty state, the narrow timebox and the refusal to fill space with KPIs.

The gaps were mostly UX, not taste:

- It specified colours and cards, but not the complete journey after a button is pressed.
- It proposed one `CourseCard` for three audiences whose jobs are different. Shared Series identity is right; one component with many flags is likely to become brittle.
- It did not cover mobile, keyboard use, focus, contrast, loading, validation, errors, permissions or plan-locked states.
- “Name your first Series” still sent a new creator to another page before they could name it. That is not yet a first-ten-minutes flow.
- Dark mode was described but not specified. An unfinished second theme is worse than one finished theme.
- “Every page must be assembled from four components” was too rigid. Consistency comes from shared foundations and behaviour, not forcing unlike pages into the same box.
- There was no review matrix or stop condition beyond visual instinct, so “one week” could easily turn into open-ended polish.

The revised plan below keeps the original visual direction and fixes those gaps.

## Product outcomes — the redesign succeeds only if these are true

1. A new creator can start a real Series from Share in **one primary action**, without landing on a second empty page.
2. At every activation state, the interface presents **one clear next step** and takes the user directly to the control that completes it.
3. A Series has the same visual identity in Share, Shared with me and public views, while each surface shows only the information its audience needs.
4. Empty, loading, error, permission-denied and plan-locked states all look intentional and never offer an action the current user cannot complete.
5. The primary creator and learner journeys work at 360px, 768px and desktop widths, with keyboard navigation and visible focus.
6. Warm paper + gold reads as calm and human, but never at the expense of contrast, trust or clarity.
7. No screen promises archive, customisation or any other capability that does not exist.

## Diagnosis (what is actually wrong)

**No identity.** `resources/css/app.css` is stock shadcn: `--primary` is near-black, `--background` is white, Instrument Sans, `--radius: 0.5rem`. Sidebar mark is the placeholder ring in `AppLogoIcon.vue` on a black square. `Welcome.vue` is still the starter kit (“Let’s get started” / Laravel ecosystem / laravel.com/docs). That single marketing page is the loudest “we forgot to finish” signal in the whole product.

**Two UIs.** Learner home (`pages/Dashboard.vue`) uses `Panel` / `StatTile` / `EmptyState`. Teach home (`pages/teach/Dashboard.vue`), courses index/show, billing, payouts still hand-roll `rounded-xl border p-4`. Same product, two levels of finish. The eye reads that as someone stopped halfway.

**The first session is a warehouse.** A new creator on `/w/{slug}` currently sees seats, 0 courses, 0 students, 0 contacts, 0 emails, role Owner. Those are existing implementation labels, not the target copy. The index is one muted line, “No courses yet.” `EmptyState` is a 20px ghost icon and two lines of gray. Honest, and blank. Teachable/Skool/Notion feel inhabited because they show **objects**. Qori shows **meters**.

**Lists instead of things.** A Series is currently rendered as a title, a status word and a price. No cover, no colour block, no face. Public `pages/public/Course.vue` is the same: type, title, button. There is no room to walk into.

**The opinion already exists and is unused.** `App\Services\TeachDigest` returns exactly one `nextAction` (no course → no lessons → unpublished → no students → gone quiet). Tests cover it. **`pages/teach/Dashboard.vue` does not consume it.** It renders six tiles. The 2026-09-07 shell-kit note said emptiness is lack of opinion, then rebuilt the _learner_ dashboard. The page a creator lives on was left as KPIs.

## What this is not

- More features on the home page. Missing EDM/video will still sit in gray boxes.
- Restyling every shadcn primitive in one pass. That produces a third UI.
- Dark-mode art, motion systems, custom illustration packs.
- Copying Skool. An invitation-led Group is not a feed.
- Hiring a brand agency before the five-day pass below. Tokens + one real Series object beat a PDF.

Admin `/admin/*` may stay kit-gray. Staff tool, not the product.

## Foundation (Day 1 — audit, tokens, welcome and auth)

Before changing code, capture the current `/`, login, zero-data Share home, one-Series creator view, Shared with me and public Series page at **360px and 1440px**. These are the before set and the visual regression checklist; do not redesign from memory.

Change CSS variables in `app.css`. Do not invent a new component library.

**Paper, not lab white.** Warm cream background; warm charcoal text. Dark mode is warm charcoal paper, not zinc-950. The product is a human place for sharing knowledge, not a terminal.

Starting tokens (candidates, not accessibility proof; tweak in the browser, test, then freeze — do not bikeshed for a week):

```
/* light */
--background: hsl(40 33% 97%);          /* paper */
--foreground: hsl(30 15% 12%);          /* ink */
--card: hsl(40 40% 99%);
--muted: hsl(36 20% 93%);
--muted-foreground: hsl(30 8% 40%);
--border: hsl(36 18% 88%);
--primary: hsl(36 70% 35%);             /* darker gold/ink — buttons, current nav */
--primary-foreground: hsl(40 33% 97%);
--sidebar-background: hsl(40 25% 95%);
--sidebar-primary: hsl(36 70% 35%);
--ring: hsl(36 70% 35%);
--radius: 0.75rem;                     /* slightly softer than kit 0.5rem */
```

Accent is **one gold**. Not rainbow chart colours on the dashboard. `--chart-*` can stay for later reports; they are not the brand.

Complete the token set that the current shadcn primitives actually consume: background, foreground, card, popover, primary, secondary, muted, accent, destructive, border, input, ring and every sidebar token. Define hover, pressed, disabled and focus treatment through those tokens rather than page-local colours.

Gold is an action/identity colour, not body copy and not the only status signal. Draft, published, failed and complete always have a text label or icon as well as colour. Check normal text at **4.5:1**, large text at **3:1**, and focus indicators/essential component boundaries at **3:1** against adjacent colours before freezing the palette. The original `38%` gold produced only about **4.09:1** against the proposed paper foreground; the darker `35%` starting value is intentional. A subtle decorative card border may remain lower contrast, but an input cannot rely on that border alone to look interactive.

**Dark mode decision:** if the theme switch is exposed, Day 1 must include a complete warm-charcoal palette and every screenshot/contrast check below must run in both themes. If the team cannot finish that in the week, remove or hide the switch and ship one excellent light theme. Do not leave inherited zinc tokens behind a Qori toggle.

**Type.** Keep Instrument Sans for UI. Add a **display size** for page titles: around `text-3xl` / `leading-tight` / `tracking-tight`, not `Heading variant="small"` everywhere. Body stays 14–16px. One scale, used.

Use one content-width and spacing rhythm across product pages. A page title, supporting sentence and primary action should align at every breakpoint; forms should not stretch to the full width of a desktop panel simply because space exists.

**Logo.** Keep the open-ring mark (the comment in `AppLogoIcon.vue` is the right idea). Put it on the gold, not on black. Wordmark “Qori” next to it; drop shipping the generic `name` from `.env` if that still reads as the Laravel app name.

**Welcome.vue — rewrite wholesale.** One focused screen, no Laravel copy, no docs links:

- Mark + **Qori**
- One line: **Your knowledge today. Their breakthrough tomorrow.** Confirm it in the Phase 0 screen test before repeating it elsewhere
- Subline: **Shape what you know into a Series and share it with the Peers you choose.**
- Sign in / **Start sharing** ("Start" alone is ambiguous)
- Paper background, gold button, no starter-kit illustration unless it is replaced

Auth layouts (`AuthSimpleLayout` etc.) pick up the same paper/gold so login is not a different product from welcome. Password, magic-link and verification screens must preserve the intended Series destination, explain what happens next and keep the primary action in the same place; visual polish must not reintroduce an authentication dead end.

**Day 1 done when:** the before/after set clearly belongs to Qori; `/` contains no Laravel residue; all surfaced themes use one complete semantic token set; contrast checks pass; and the auth detours still return to the page that initiated them.

## One coherent system (Day 2 — shell, navigation and responsive rules)

`components/shell/` owns product chrome. Keep and normalise `Panel`, `StatTile`, `DefinitionList` and `EmptyState`; add `PageHeader`, `InlineNotice` and `CourseCover` only where repeated use is already visible.

These are **defaults, not a gate**. A billing page and a Series builder should share tokens, spacing and behaviour without pretending to be the same component. Do not solve consistency with one giant component full of `variant`, `isPublic`, `isStudent` and `showProgress` flags.

Replace duplicated panel markup on:

- `pages/teach/Dashboard.vue` (worst offender)
- `pages/teach/courses/Index.vue`
- `pages/teach/courses/Show.vue`
- `pages/teach/Billing.vue`
- `pages/teach/Payouts.vue`
- `pages/teach/Contacts.vue`
- `pages/learning/Show.vue` (shell and spacing only)
- `pages/public/Course.vue` (public composition, shared foundations)

Use `rg "rounded-xl border" resources/js/pages` as an audit, not as a score. A remaining instance is fine when it represents a genuinely local layout; unexplained copies of the same card are not.

**Page contract:** every product page has one H1, an optional one-line description, one clearly ranked primary action, a consistent content width and a predictable place for notices. Do not put equal visual weight on every available action.

**Form contract:** visible labels, persistent help when needed, errors next to the field and an error summary for long forms, submit progress, double-submit protection, and success feedback that also says what to do next. A disabled action must either be self-explanatory or explain why nearby; never make the user guess from opacity.

**Empty-state contract:** an empty state sits in the same spatial container the real object will occupy. It includes a primary action only when the current role and plan permit that action. Otherwise it explains who can act or what must change; it never leads to a 403 or a plan-limit refusal.

**Responsive shell:** keep the current context-switcher model, but prove it at small widths. At 360px the desktop sidebar becomes the existing mobile drawer/sheet, the current hat or workspace remains visible before opening it, long workspace names truncate without hiding the switch control, and the primary page action remains reachable without horizontal scrolling. Do not invent a second mobile navigation model during this week.

**Day 2 done when:** Share, Series, billing, payouts and contacts share page geometry and interaction states; navigation clearly distinguishes **Shared with me** from the creator side of the selected Group on desktop and mobile; and no page depends on copied border/radius classes for its identity.

## First ten minutes produce an object (Day 3 — creator activation)

Share must not open on stats. It should answer two questions in order: **what am I creating?** and **what should I do next?**

**Hero is `TeachDigest.nextAction`.** `StudioDigest` in older notes means `TeachDigest`; use the class that exists. Extend the returned data only if necessary so the UI receives the action label, explanatory copy and route-helper-backed destination together rather than rebuilding product logic in Vue.

The action must land at the control that completes the task, not at a page that asks the user to find it:

| State              | Message                                                | Primary action            | Destination / completion signal                                                                                    |
| ------------------ | ------------------------------------------------------ | ------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| No Series          | “Name your first Series”                               | **Create a new Series**   | Open the visible minimal create form directly; after save, show the real Series and offer “Add your first Episode” |
| Series, 0 Episodes | “Add an Episode to {title}”                            | **Add the first Episode** | Episode form, focused; after save, show the Episode in place                                                       |
| Episodes, draft    | “{title} is ready”                                     | **Make ready to share**   | Existing publish control with blockers shown inline; success offers “Share with your first Peer”                   |
| Ready, 0 Peers     | “Share with your first Peer”                           | **Invite a Peer**         | Existing enrolment/access control, focused; success shows the Peer as an object, not only a toast                  |
| Peers gone quiet   | Use the existing digest intent with the resolved terms | **Review the Series**     | Series activity/progress section, not the top of a generic page                                                    |
| Nothing urgent     | Let recent Series objects lead                         | Contextual Series action  | Stats may appear below; they do not become a replacement hero                                                      |

Use Wayfinder route helpers; do not add hardcoded URL literals. Preserve back behaviour and browser focus when opening a dialog/sheet. If the current Series-create UI cannot be deep-linked or opened directly, change that UI rather than weakening the dashboard CTA. Internal routes may remain named `course` in this phase.

The first create form exposes only the fields the domain genuinely requires to create a draft. Advanced price, media and sharing-readiness decisions wait until the object exists. Reuse current server validation and defaults; this is progressive disclosure, not a second “quick Series” data path.

**Blocking state has priority over encouragement.** A paused workspace, over-cap workspace, missing permission or unavailable dependency supersedes the ordinary digest action. The page explains the real recovery path and shows only actions the current user may take. An admin must not receive an owner-only upgrade CTA; a workspace at its cap must not receive a create CTA that the server will reject.

Stats (Series, Peers, contacts, email allowance) go below a real Series or next action and only when their values help a decision. Seats and “Your role” do not belong in the first-run grid. System role may live in account/Group settings; it is not a result.

**Series-shaped empty state.** `pages/teach/courses/Index.vue` shows the silhouette of the object that will replace it: cover area, explicit “Your first Series will appear here” copy and “Create a new Series.” It must look intentionally empty, not like a loading skeleton or disabled Series. After save, the real object replaces it in the same location.

**Group identity is functional, not decorative.** The current auto-generated “Rita’s workspace” reaches Peers in email and makes public trust weaker. Add a small, reachable rename control and ask “What should people call your Group?” when the generated name is still unchanged. Do not block creating a Series, but surface this before making it ready or inviting people. Use `workspace` in code; resolve the configured customer-facing noun consistently in UI. This is the one small non-visual change worth admitting into redesign week because colour cannot repair an unnamed sender.

**Day 3 done when:** a new owner reaches a saved, named Series from Share without visiting a second empty page; every subsequent CTA lands at the relevant control; an owner, admin and over-cap Group each see an action they can actually complete; and success visibly advances the same page to the next state.

## A Series looks like the same Series everywhere (Day 4)

Share the Series' **identity**, not necessarily one whole card component. Keep internal component names such as `CourseCover` in this phase if renaming them adds risk without customer value.

- `CourseCover` owns the deterministic visual: a stable wash derived from an immutable value such as course id (not a mutable title), kept within the Qori gold/paper family. No image upload this week and no random rainbow.
- `StudioCourseCard` answers “what needs work?”
- `LearningCourseCard` answers “where do I continue?”
- The public page uses a `PublicCourseHero` composition, not a card stretched until it becomes a page.

They may share small primitives or slots if that stays clearer than three components, but do not create boolean-prop soup to prove reuse.

| Surface        | Information hierarchy                                                                                                       | Primary action                                         |
| -------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Share          | Cover, title, draft/ready label, Episode count, price                                                                       | Open/edit Series                                       |
| Shared with me | Cover, title, Group, “Shared by {name}”, progress, next Episode                                                             | Continue / Start                                       |
| Public         | Cover, title, Group, “Shared by {name}”, plain-language summary, Episode count or duration when known, real contents, price | Get access / Sign in / Open Series, according to state |

Rules shared across all three:

- The cover is decorative when the title is adjacent; do not make a screen reader hear duplicate Series names.
- Status and progress are never communicated by colour alone. Give progress an accessible name/value and write “3 of 8 Episodes,” not only a bar.
- One obvious card target. Do not nest an `a` around buttons or place competing invisible links over the card.
- Long titles, free Series, large prices and zero Episodes must not break the grid.
- Public copy shows only facts Qori has. Hide an empty “What’s inside” section rather than filling it with generic promises.
- Public trust comes from the named Group and person sharing it, a clear price and clear access state, not from adding badges Qori cannot substantiate.

“Pick up where you left off” already has the right opinion; put it on the Shared with me card so Continue belongs to a Series object, not a panel of text. On mobile, keep title/progress/action visible without requiring the cover to consume the first screen.

**Day 4 done when:** Share, Shared with me and public screenshots are unmistakably the same Series, yet nobody sees internal status or controls irrelevant to their job.

## Interaction, responsive and accessibility contract (applies throughout)

Every changed surface must be reviewed in these states where they can occur:

- initial/loading or submitting
- empty
- populated with one item
- populated with enough items to wrap or scroll
- validation failure
- server/network failure
- success
- permission-restricted
- plan-locked or workspace-paused

Do not use a spinner or skeleton where the server already delivered an honest empty state. Use a skeleton only for genuinely pending content and give it the same geometry as the result. Critical errors stay near the failed action with a recovery route; a disappearing toast is not an error strategy.

Minimum interaction and accessibility bar:

- semantic landmarks and one logical H1; headings do not skip levels for visual size
- all controls reachable and operable by keyboard, with visible focus that is not clipped by cards or drawers
- focus moves into an opened dialog/sheet and returns to its trigger on close
- minimum 44px touch targets for primary mobile controls
- no placeholder-only labels; errors are associated with fields; icon-only buttons have accessible names
- colour contrast as specified on Day 1; status never relies on colour alone
- reduced-motion preference respected; no animation is required for this redesign
- content remains usable at 200% zoom and at 360px without page-level horizontal scroll

## Copy and terminology

- Page titles use the display size; there is still only one H1.
- Follow [`terminology-refactor.md`](terminology-refactor.md). Qori-authored customer copy no longer defaults to **classroom**, **course**, **lesson**, **teacher** or **student**.
- Selected defaults are **Group**, **Series**, **Episode** and **Peer**, with **Share** as the creator mode and **Shared with me** as the receiving view. Prefer “Shared by {name}” instead of forcing a replacement for Teacher.
- Keep `workspace`, `course`, `lesson`, `enrolment`, provider jargon and system roles inside implementation or specialist screens where precision is necessary. Do not rename models or permissions as part of a copy pass.
- Every customer-facing noun comes from the resolved terminology layer, including empty states, validation, email, PDFs and signed-out public pages. Never concatenate arbitrary custom words into grammatically fragile fragments.
- Kill every archive promise while archive does not exist (walkthrough, 2026-09-06).
- Welcome, auth, Share and empty Series speak to a person with something worth sharing, not a school or admin console. “Team” and “Your role” are settings language, not a welcome.
- Button labels name the result: “Create a new Series,” “Add an Episode,” “Make ready to share,” “Invite a Peer,” not “Continue,” “Submit” or “Start” without an object.
- Errors say what happened and what the user can do next. Success messages confirm the object changed and expose the next useful action.
- Do not decorate emptiness with jokes, fake activity or sample metrics. A clear object-shaped state and one button are enough.

## Day 5 — secondary surfaces, review and release

Apply the shell and type hierarchy to billing, payouts and contacts. This is a consistency pass only: do not turn it into new pricing copy, charts or financial features. Give the Peer player a mobile/keyboard shell pass because it is a core journey; certificates, admin and the EDM composer inherit tokens unless visual QA shows a severe regression.

Run the review matrix before calling the week done:

| Surface                    | Required scenarios                                                                                                                  |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Welcome + auth             | Signed out; password; magic link; verification; intended return to public Series                                                    |
| Share                      | New owner; Series with no Episodes; draft ready; ready with no Peers; quiet Series; healthy Series; over-cap/paused; non-owner role |
| Series                     | Empty; one Series; several Series; long title; free and paid; draft and ready                                                       |
| Public Series              | Guest; signed-in without access; access granted; unavailable/not ready; login and verification detours                              |
| Shared with me             | Empty; not started; in progress; completed; revoked/unavailable Episode                                                             |
| Billing, payouts, contacts | Empty; populated; failure; role without access                                                                                      |

For every row, check 360px, 768px and 1440px; light and dark if dark ships; keyboard-only operation; visible focus; realistic long content; and no action that ends in a predictable refusal. Capture the after screenshots beside the Day 1 baseline.

Run the existing full quality gate. Add or update tests for `TeachDigest` state priority, action authorisation and destinations; do not rely only on snapshot appearance. Repeat the creator and Peer browser walkthroughs from the bottom of this file, including the magic-link/verification return path.

## Release gate and stop condition

The redesign is done when all of these are true:

- A zero-data creator sees a Series-shaped beginning and can create the Series from the first CTA.
- The next-action sequence can be completed end to end without hunting for a control.
- A one-Series creator sees a real object before aggregate numbers.
- Share, Shared with me and public views share Series identity without sharing irrelevant controls.
- `/` and auth contain no Laravel/starter residue.
- Customer-facing pages use the same tokens, H1 hierarchy, spacing, form states and focus treatment.
- The 360px and keyboard walkthroughs pass, contrast is checked, and the full existing test/quality gate is green.
- Remaining duplicated visual recipes are either moved into a shared primitive or deliberately documented; raw class-count reduction is not the goal.
- Every changed empty, error, permission and locked state gives a truthful recovery path.

Then **stop after Day 5**. Log anything else as a separate product task. If it still feels empty, the problem is likely missing real objects or identity — a named Group, a Series cover, a Peer row — not another round of CSS or more KPI tiles.

## Out of scope for this week

OAuth connection UI, campaign builder, live-session chrome, i18n wiring, custom illustration, uploaded Series covers, a purchased logo, replacing shadcn, new dashboard analytics, public reviews/testimonials and broad admin redesign. Do not block this week on `useqori.com`, live Stripe or a second font. Dark mode itself is not required, but an exposed broken dark theme is not allowed.

## Decisions added by this review

- Shared **Series identity** is required; a single universal `CourseCard` is not.
- A primary CTA routes to the completing control, never merely to the containing page.
- Blocking/permission state outranks activation copy.
- Group naming/rename is included because it affects public trust and Peer email, not because settings need more features.
- School-coded nouns are retired from Qori's default customer vocabulary; internal domain names remain stable during this refactor.
- Mobile, keyboard, contrast and non-happy-path states are part of the definition of done, not a later polish pass.
- One finished light theme is acceptable; two half-finished themes are not.
