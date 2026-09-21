# Browser walkthroughs

> Observed end-to-end browser behaviour, fixes and open UX findings.

[Current plan](../../PLAN.md) | [Planning index](README.md)

## End-to-end walkthrough, 2026-09-06

Driven through the real UI as a creator (Rita), two students (Sam, Priya), and a
password reset. Everything below was observed in a browser, not inferred.

**Works, unprompted:** register → workspace auto-created → studio dashboard →
create course → publish → enrol a student by email → student sees "My learning"
→ opens their course → access email arrives correctly branded → forgot password
→ reset link → new password → sign in.

### Fixed since (all verified in the browser, 2026-09-06)

- **A creator can add a lesson.** Route, controller, form request and form. The
  provider list narrows with the lesson kind so §8's rule is visible before
  submitting, not just enforced after. Reorder and remove work; removing the last
  lesson of a published course takes it back to draft.
- **A student can open a lesson.** The course page calls `/play` on click. A PDF
  opens in a new tab, a Vimeo video embeds in place, and the asset-aware TTLs
  were confirmed live: **~3 minutes for the PDF, ~240 for the video**, with an
  unenrolled user refused.
- **Navigation exists.** Inertia shares the user's workspaces, so the sidebar has
  Home / My learning / Studio / Courses. `/dashboard` is a real home showing both
  hats; the studio dashboard counts courses, students and contacts instead of
  saying "not built yet".
- **Email verification is enforced.** `User` now implements `MustVerifyEmail`,
  which is what Laravel's `verified` middleware keys on — without it the
  middleware silently passed everyone. Confirmed end to end: an unverified
  session lands on the verification screen, the email sends, the signed link
  works. Tests had missed it because `UserFactory` verifies by default, so a test
  now asserts the unverified case explicitly.
- **The Laravel logo is gone**, replaced by a placeholder Qori mark, and the
  starter kit's Repository/Documentation links are removed.

### Found by browser walkthrough, 2026-09-06 (both fixed)

- **Magic-link sign-in was broken from the UI.** `Login.vue` posted to
  `/login/magic-link`, a route that moved to `/auth/magic-link` when auth was
  namespaced. Nothing was sent and nothing errored — the form simply 404'd. The
  suite missed it because the tests post to the route _name_ while the Vue held
  a hardcoded literal. Fixed by using the generated Wayfinder helper, which
  cannot drift, and the same treatment applied to the new public page rather
  than leaving three more literals to rot the same way.
- **Public pages wore the signed-in app shell.** `app.ts` fell through to
  `AppLayout` for everything but `Welcome`, so a signed-out visitor saw a sidebar
  of things they could not reach — "My learning" beside a "Sign in to enrol"
  button. Pre-existing: `/pricing` had it too. Now `Welcome`, `Pricing` and
  anything under `public/` take no layout.

### Full workflow walkthrough, 2026-09-06 (second pass)

Driven end to end in a browser after the progress work, as creator (Wayne),
guest, and student (Priya). Every step observed, not inferred.

**Worked, unbroken:** create a course → add a lesson → publish (correctly
refused while it had none) → public page renders for a signed-out stranger →
"Sign in to enrol" → magic link → **returned to the course page** → enrol →
correctly diverted to verify → **returned to the course page again** → enrolled
→ access email "You're in: Sourdough From Scratch" → landed in the player →
progress 0% → mark as done → 100% and "Finished" → the creator's "Where students
stop" report shows 1 of 1 finished.

Also confirmed on the way:

- **The `used/limit` rule is already built** where it matters most. Rita's
  free-plan course index reads "1 of 1 course used on your plan" with "Your plan
  includes 1 course. Upgrade to add more, or archive one you're no longer
  teaching" — the counter and the upgrade-before-delete ordering, both already
  right. The rule recorded above is partly a description of existing behaviour.
- **A free enrolment stores `price_cents` as null**, not zero, so §21.1's "the
  creator gave this away" survives the whole round trip.
- `completed_at` is stamped, and the report reads it.

**One copy defect:** that same message offers to "archive one you're no longer
teaching", and **archiving does not exist**. It promises a way out that is not
there, which is worse than naming the two that are. Either build archive — it is
close to the read-only lock the downgrade policy already needs — or change the
sentence.

### Still open from the walkthrough

- **A magic link does not verify the email it was sent to.** Clicking a signed
  link delivered to an address proves control of that address — the same proof
  the verification email provides — yet a student who signs in that way is still
  sent to the verification screen. Observed on a real student account during the
  progress walkthrough. Arguably a one-line fix in the magic-link controller, but
  it is an auth policy call rather than an obvious bug, so it is recorded rather
  than changed.
- **Enrolling sends an unverified student to the verification screen with no
  warning.** Correct behaviour — access is granted to an identity, and an
  unverified address is one nobody has proven they own. **Milder than first
  recorded**: the 2026-09-06 walkthrough confirmed `url.intended` survives the
  detour, so verifying returns them to the course page rather than a dashboard.
  The destination is right; only the explanation is missing. A line on the
  verification screen naming what they were in the middle of would close it.
  Copy, not a bug.

- No way to rename a workspace. The auto-generated "Rita's workspace" reaches
  students in the access email, which reads oddly for a school.
- No studio UI for Connect onboarding or campaigns — both routed and tested,
  neither reachable by clicking. **Billing is now done** (see Done above);
  Connect and campaigns are the two left.
- ~~No file **upload**~~ — built 2026-09-06. A `qori_s3` lesson now gets a file
  picker that uploads straight to the bucket; other providers still take a
  pasted reference, which is correct, since those files live elsewhere.
- `Welcome.vue` still links to laravel.com/docs — the marketing page needs
  rewriting wholesale anyway.

## 9 September 2026 — the core loop on the renamed domain

Driven in a real browser immediately after the internal rename and the Postgres
migration, against an empty database, as a brand-new account.

**Worked, unbroken:** register → email verification → Home (Shared) → open Group
→ create a Series → pick a file → direct upload to R2 → confirm → Episode
attached. The Share dashboard shows Team members, Series against the plan cap,
Peers _with access right now_, People you know, and the email allowance.

**Found and fixed on the way:** the bulk rename produced **“Add a episode”**. A
case-sensitive find-and-replace cannot know that `lesson` and `episode` take
different articles, and the terminology spec had already warned about exactly
this under custom labels — “avoid a/an before custom terms”. Twenty-six files
carried it. Corrected in both directions; there were no `an group`-style errors,
because the words that gained a consonant were not preceded by `an`.

**Copy worth revisiting in the redesign week**, recorded rather than fixed now:

- “You also share” on the learner home reads oddly as a heading; it was “You
  also teach”, and the noun-less rename leaves it ambiguous.
- Product nouns are lowercase in navigation (“My series”, “Series”) while the
  spec capitalises them as product nouns. One convention should win.
- The auto-generated Group name is “Nadia's group”, which reads worse than the
  old “Nadia's workspace” did and is the first thing a Peer sees in an
  invitation. Group rename is already a Priority 2 item; this raises its value.

## 9 September 2026 — the terminology registry, and what it found

Driven after `App\Support\Terminology` was wired into the screens, on a local
Group deliberately put on a paid plan so the unlimited branch of the count copy
would render.

**The share dashboard said “2 seriess”.** Not a typo — the count line built the
plural by appending an `s`, and Series is its own plural. The free plan's series
cap is 1, so the branch that renders it had never once been reached on a real
account; every screenshot before this one had a `1` in it. Three more screens
pluralised a product noun the same way (`episode${n === 1 ? '' : 's'}` twice, an
`? 'episode' : 'episodes'` ternary once), all correct today only because the
noun happens to be regular. `forCount()` replaced every one.

**Two leftovers from the rename, both customer-visible:**

- The Peers table's status badge read **“Grantled”**. “Enrolled” lost its stem
  to the rename and kept its ending. No test could catch it: it is a valid
  string in the right place, and only a person reading the screen can see that
  it is not a word. It reads “Has access” now.
- The same page's empty state said “when they **grant in a series**”, from
  “enrol in a course”.

**The public page put the creator's verb on the buyer's button.** “Grant”,
“Grant — $49” and “Sign in to grant” were what a visitor saw; granting is what
the creator does. All three now say “Get access”. This is the same class of
error as “Grantled”, and the same reason nothing caught it — a rename maps
words, not who is speaking.

**Fixed from the previous walkthrough's list:** product nouns are capitalised
everywhere now, because they arrive from the vocabulary already capitalised and
code may not lowercase a customer's own word. The nav label and its destination
also stopped disagreeing — “My series” pointed at a page headed “My shared”;
both are “Shared with me”, the name the terminology spec gives that view.

**Still open, and now the redesign's:** “You also share” as a heading, and the
auto-generated “Nadia's group”.

**Confirmed end to end:** publishing a Series flashed “Your Series is ready to
share — the Peers you grant can open it now”, a lang line whose nouns were
filled by the registry rather than written into the sentence.

## 9 September 2026 — redesign Day 1, paper and gold

Checked at 1280px and 360px, in both themes, signed in and signed out.

**The palette is one set per theme, not a light theme with a dark patch.** Every
value was measured against the surfaces it actually lands on before being
frozen, and two moved as a result: the gold to **33%** lightness (the brand
kit's 38% measured 4.09:1 on paper, and even 35% fell to 4.48:1 on the
sidebar's slightly darker ground), and the dark destructive to **62%** (58%
measured 4.44:1). Everything now clears 4.5:1 for text and 3:1 for boundaries
and focus rings, in both themes.

**Two things would have flashed or clashed and neither is in the CSS file.**
The root Blade template painted `oklch(1 0 0)` before the stylesheet arrived, so
every page load would have shown white and then resolved to cream; it now paints
the paper hex, with a comment tying it to `--background`. And Tailwind v4's
border-colour compatibility shim was pinned to `gray-200` — a cool grey drawn
around everything on a warm page.

**Deleted rather than restyled:** `AuthCardLayout.vue`, `AuthSplitLayout.vue`
and `PlaceholderPattern.vue`. Nothing routes to any of them. Keeping them means
every future token change has to be applied to code that never renders — and
code that never renders gets neither tests nor eyes, which is exactly how
"Grantled" survived.

**Found while running the gate:** `composer ci:check` failed two tests whenever
a dev server happened to be running. `npm run dev` also warms an Inertia SSR
server, `config/inertia.php` had `ssr.enabled` hardcoded true, and every Inertia
response in the suite was then making a real HTTP round trip to it — two tests
using `Http::fake()` turned that into a visible failure, and the rest were
quietly doing network I/O and passing for an unrelated reason. SSR is now
env-driven and off in `.env.testing`.

**Type.** Every page in the product used `Heading variant="small"`, so a page
title and a section heading inside it were the same 16px and nothing said what
you were looking at. `Heading` gained a `page` variant at the display size, and
it renders an `h1` — the page titles were all `h2` with no `h1` above them.

## 9 September 2026 — redesign Day 2, one shell

**The panel audit went from 19 to 2.** `rg "rounded-xl border" resources/js/pages`
found nineteen hand-rolled cards that had drifted apart in padding, border
colour and whether they were clickable — six of them on the Share dashboard
alone, where three tiles showed a limit and three did not, one was a link and
five were not, and the email tile carried its own copy of the progress bar
`StatTile` already had, including its own `bg-amber-500`. That is why the
warning colour existed in two places with two different values.

The two that remain are deliberate: the certificate's print card, which has
`print:border-0` rules nothing else needs, and the public Series episode list,
which sits outside the app shell.

**Three components were added and one was taken away.** `PageBody` declares the
content width once — pages had each been repeating `flex h-full flex-1 flex-col
gap-6 p-4`, so the product was as wide as the window and a two-column form
stretched to 2000px because the space existed. `PageHeader` owns the H1 and the
primary action beside it. `InlineNotice` replaced four bespoke warning boxes,
including the starter kit's `bg-red-50` delete-account panel, which followed no
theme at all. `Heading` lost the `page` variant it gained on Day 1: `PageHeader`
does that job now, and two components claiming one job is how a page title ends
up rendered two ways.

**Copy the shell surfaced:** the Series list printed `series.status` directly,
so the label was whatever the database column said — "PUBLISHED", in caps, on a
product whose spec word is "Ready to share". The Series builder's own publish
button said "Publish" for the same reason. Both now say what the state is, with
a success-toned tick rather than colour alone. And the give-access panel, its
field label and its button were all saying the same three words; the field only
ever wanted an email address.

**360px, checked rather than assumed.** `documentElement.scrollWidth` equals
`clientWidth` on the Series builder, the Share dashboard and billing — no page
scrolls sideways. The sidebar becomes the existing drawer, and the header now
names the current Group before the drawer is opened: `useShareContext` was
extracted from `AppSidebar` so the header can answer "which Group am I in" from
the same place, rather than the answer living behind a hamburger.

**Not fixed, and worth a Day 5 line:** the 404 page is still Laravel's own bare
white error view. It is the one surface in the product that has never seen a
Qori token.

## 9 September 2026 — redesign Day 3, the dashboard gets an opinion

**`ShareDigest::nextAction()` had never been rendered.** It was computed on
every Share dashboard load, returned to Inertia, and read by no Vue file — the
class's docblock argued that "a dashboard feels empty for want of an opinion
rather than for want of numbers", and the opinion had never reached a creator.
The dashboard meanwhile ran its own copies of the same four counts.

It now leads the page, and three rules shape it. **Blocking outranks
encouraging**: a paused Group or one over its cap is answered before any
suggestion, because inviting somebody to share when sharing is disabled is
worse than saying nothing. **Only actions this person can take**: §15 keeps
billing with the owner, so an admin over the cap is told who can change the
plan rather than handed an upgrade button that answers 403. **The destination
is the control**: every href carries a fragment — `#new-episode`, `#publish`,
`#give-access` — and `useDeepLinkedControl` puts the cursor in the first field
when the page arrives.

**That composable was written wrong the first time and the browser proved it.**
Bound to `onMounted` alone, it worked on a hard refresh and did nothing on
every link inside the product, because the app layout is persistent and only
the page component swaps on a client-side visit. It listens to Inertia's
`navigate` now. The second version was also wrong: `requestAnimationFrame`
never fires in a hidden tab, so the whole behaviour depended on the window
being in front. It uses `nextTick` plus a timeout.

**Group rename exists.** `PATCH /g/{group}`, a form on the Share home, and a
`name_set_at` column so the question is asked once. The slug deliberately does
not move — it is in every link already sent and every access email already
delivered, so reassigning it would break all of those to fix a display name.
The prompt sits in the middle of the ladder rather than at the top: a generated
name must not stop anyone making their first Series, only sharing it.

**One thing the browser caught that the tests could not.** With the name form
placed inside the next-action card, a brand-new Group showed a card headed
"Name your first Series" with a field pre-filled with the _Group's_ name — two
correct conditions producing one nonsensical screen. The card now keys on which
action it is showing, not on whether the name has been chosen.

**Walked end to end on an empty Group:** "Name your first Series" → the create
form → the Series page, where the publish control is disabled and the reason is
in the empty state beside it → back on the dashboard, the action has advanced to
"Ink and Wash has no Episodes yet". Each step's success visibly moved the page
to the next state, which is Day 3's release gate.

## 9 September 2026 — redesign Day 5, the QA pass

**Sixteen pages at 360px, and none of them scrolls sideways.** Measured rather
than argued: `scrollWidth - clientWidth` was 0 on every product page, including
the two built last — the vocabulary settings form, whose three-column field
layout stacks correctly, and the Series builder, which was the widest thing in
the product before the shell landed.

**The palette is a test now.** Day 1 chose it with a throwaway script; the gold
moved twice and the dark destructive once, on numbers that existed for an
afternoon and were written down nowhere a change could disagree with them.
`PaletteContrastTest` parses `resources/css/app.css` and checks every pair in
both themes — body text and muted text on six surfaces, the gold on everything
it can land on, text on filled controls, and the 3:1 boundaries.

**It caught something on its first run.** `errors/layout.blade.php` inlines its
palette because it may not depend on the Vite build, and carried a comment
saying the six values were duplicated and must be kept in step. Three of the
dark ones had been hand-picked rather than converted and had already drifted.
The comment had been true when written and false ever since; the test is what
makes it true again.

**And a prop leaking through a component that exists to stop that.**
`DialogContent` forwarded its own `showCloseButton` into Reka, so
`showclosebutton="true"` was on the DOM of every dialog in the product.

**What could not be done, and why it matters beyond this task.** The keyboard
third — tab order, focus rings, escape and focus return — was not verified,
because the browser pane was hidden and `document.hidden === true` stops key
events reaching the document _and_ stops CSS animations running. Escape does
reach the dialog; what happens after it is gated on an `animationend` that
never fires. Split into `T-022`, blocked.

This is the third time a hidden pane has quietly changed what was observable
here. The first cost two wrong implementations of `useDeepLinkedControl` before
anybody noticed. The failure mode is always the same shape: nothing errors, the
environment simply answers a different question than the one being asked.

## 11 September 2026 — registration and first run

Walked by Codex in local Qori at `http://localhost:8001`, dark theme, with
three synthetic accounts: **Onboarding Review Creator**, **Onboarding Review
Peer** and **Onboarding Review Invited**. The last name identifies a review
account; that path began at a public Series link, not an actual invitation email.
Verification URLs were read from each account's mail in the local log. No
external email delivery was exercised.

**Direct creator signup.** On `/auth/register`, left **I want to share**
selected, completed the form and reached `/auth/verify-email`. The page offered
resend and logout but did not show the submitted address or next destination.
Following the verification URL reached `/dashboard`, under **Shared with me**:
**Nothing on the go** appeared before **You also share / Onboarding's group /
Open**. There was no creator-onboarding handoff after the signup choice.

**The creation pieces work once found.** Open led to `/g/onboardings-group`,
where **Name your first Series / Create Series** appeared above a Group-name
and timezone form and four zero meters. The timezone field displayed the
device's Brisbane suggestion and asked for confirmation. **Create Series**
opened the visible form at `/g/onboardings-group/series#new-series`. Saving
**First steps in sharing**, with optional fields empty and without saving the
Group name or timezone, created a real private draft. The result showed the
Episode form, the disabled sharing control with its missing-Episode reason,
and feedback to add an Episode. The walk stopped before creating an Episode.

**Direct receiving signup.** Signed out, registered with **I want to learn**,
then followed its logged verification URL. `/dashboard` showed **Nothing on
the go** and a general explanation of future shared Series. The only prominent
action was **Start sharing** in a separate **Want to share?** panel. There was
no creator Group, but there was also no explanation of opening the sender's
link or checking the receiving address.

**Public-Series signup and immediate verification.** Signed out, opened
`/s/harbour-lane-studio/reading-a-room-before-you-speak`, followed **Sign in to
get access → Sign up**, selected Learn and registered. Registration returned
correctly to **Reading a Room Before You Speak**, with **Get access**. Opened
the verification email immediately, without pressing Get access: Qori landed
at `/dashboard?verified=1`, showing the empty receiving home with no requested
Series or return action. This is the confirmed order of operations; the branch
that attempts Get access before verifying was not exercised.

**Evidence and scope.**
`docs/design-review/2026-09-11-onboarding-journey/` contains the manually
captured contact sheet, manifest and named images `810`–`880`. The pane was
measured at 455 × 556 during capture; no responsive override was applied.
HEAD recorded during the walk was `a3c7c42484b6c19830b596b180c70a6a530418a2`,
with concurrent working-tree changes; it had moved to
`7b314d3fe0b227ecc29bfc7202e9f7f08a920f49` by write-up. This is not an atomic
commit capture. The full-page Group image has a repeated lower strip from
stitching; it is not a second email meter in the DOM or a finding.

No full invitation/access, payment, consumption, different-device, keyboard,
responsive, contrast or failure-state pass was run. Three local review accounts
and one private draft remain in the development database; no application fix
was made. [R-003](design-review/passes/R-003-2026-09-11-registration-and-first-run.md)
records the findings; [onboarding direction](ui-onboarding.md) and existing
drafts T-008/T-026/T-027 record the planning response.

## 16–17 September 2026 — R-004 current web review

Codex used a dedicated local Qori server on port 8016 with the documented
DesignReviewSeeder worlds. Static evidence is the `0337` run described in
[R-004](design-review/passes/R-004-2026-09-17-final-web-review.md); its dark
manifest survives, with light companion images after the same-minute output
collision. The visible in-app browser used `127.0.0.1:8016`, measured
`document.hidden === false`, and received keyboard input. Captures were at
390/1440px; live Peer layout checks used 360 × 800, 768 × 1024 and 1440 × 900.
These are not actual 200% zoom or physical-device checks.

**Sign-in.** The email-first page accepted the synthetic Sam fixture address.
Next put focus in Password. With the Password tab active, keyboard arrow
navigation moved focus to Email link while Password remained selected; Enter
activated Email link. The focus ring was visible. Requesting a link showed a
disabled loading action followed by the dedicated neutral Check your email
state, full address, resend and change-email actions. Delivery to a real mail
client was not tested. The second-step address was truncated at 360px; main
sign-in actions measured 36px tall. Routine fixture access subsequently used
`qori:magic-link`, so that login is not evidence that the emailed link was
opened or that the password/passkey methods succeeded.

**Existing Peer.** Sam's dashboard Continue opened Reading a Room Before You
Speak with two of four Episodes done and a named continuation for Silence,
and what it costs. The page reflowed at 360, 768 and 1440px without page-level
horizontal overflow. Continue measured 20px high at 360px and Mark as done
16px. Opening the audio Episode showed Opening, then a persistent That didn't
open / We couldn't open that episode just now message. No provider content
opened, so consumption is unverified. Marking the third Episode done saved
3 of 4 and advanced Continue to the fourth; marking the fourth exposed
Finished and a certificate. The certificate was opened and inspected, including
its incorrect implication that the Group had separately marked completion
(R-004 F-12). The third/fourth checkmarks were returned to their original
unchecked values. The new completion stamp and certificate remain by the
existing sticky-certificate contract; this is not a fully restored database.

**Mobile drawer.** On the Peer page at 360px, opening the sidebar moved focus
to its Qori link. Shift-Tab wrapped to the account button, Tab wrapped back,
and Escape removed the dialog and returned focus to Toggle sidebar. Visibility
was checked during these actions. This verifies this drawer, not every modal,
menu, focus target or both-theme keyboard sequence.

**Creator.** Fern's empty Fresh Start home already has a first-Series action.
It opened `/g/fresh-start/series#new-series` and focused Title. A blank submit
showed the browser's required-field bubble. The Title and numeric Hours inputs
both measured 934px at a 1440px viewport. Saving only the title created the
private draft R-004 review — first Series at
`/g/fresh-start/series/r-004-review-first-series`. The page explained that an
Episode was required before sharing and showed the Episode form. A local PNG
fixture was prepared for a file Episode; the browser chooser timed out, and a
second attempt through the visible Choose file control failed with a stale
backend element. No upload or Episode creation was verified. The private draft
remains. This is evidence through draft creation only, not a completed
creator → Episode → ready → share → new-recipient journey.

**Boundaries.** No external invitation, purchase, provider connection or
real-world email delivery occurred. New registration, typed-code verification,
recipient basic-details confirmation, D-017's full return matrix, payment
fulfilment and creator setup resumption were not driven in this pass. Setup
screens were visually inspected in the harness. The intended Integrations
pages rendered local dependency errors. Application source remained identical
across the relevant concurrent commits by the comparison recorded in R-004.
No application fixes or commits were made. This entry supplies bounded
keyboard/journey evidence to T-022/T-026/T-027 without changing task status.
