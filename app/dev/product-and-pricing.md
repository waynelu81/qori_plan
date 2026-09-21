# Product and pricing research

> Preserved strategic research. Deferred ideas do not override the beta decisions in the root plan.

[Current plan](../../PLAN.md) | [Planning index](README.md)

## Current review — 11 September 2026

**Owner clarification:** target creators already sharing material through
Google Drive, OneDrive, Dropbox and YouTube. Lead with those familiar names and
using existing files without moving them. Compare Qori and competitor
subscriptions directly for that audience, with no assumed external-hosting
surcharge. The [decision record](decisions.md#position-around-creators-existing-files-and-familiar-tools-2026-09-11)
and the review below capture the revised framing; provider names are a target
promise until the corresponding workflows work.

See [Pricing and competitor review](pricing-and-competitor-review-2026-09-11.md)
for the dated official-source comparison of **Thinkific, Teachable, Podia,
Payhip, Skool, Circle, Mighty Networks and Kajabi**, current Qori entitlements,
feature-readiness gaps and proposed packaging. The review distinguishes the
original price sketch from design fixtures and records current vendor-policy
caveats. Recommendations are for discussion; they do not change approved
decisions, application entitlements or live prices. Older research below is
preserved and must be read against the current root plan.

## Current addition — custom vocabulary as higher-tier identity

Qori's default language is being moved away from school-coded terms. An eligible higher tier may customise the customer-facing nouns for its Group, creator role, Series, Episode and Peer, including explicit singular and plural values. This is meaningful brand identity — a community can call its creator “Ruff” and its Peers “Ruffy/Ruffies” — rather than a cosmetic theme switch.

The defaults must remain complete and good enough without payment. Custom labels are display configuration only: they do not rename internal models, change Owner/Admin permissions or create a second access system. Exact tier packaging and downgrade behaviour still require a product decision. Full implementation plan: [`terminology-refactor.md`](terminology-refactor.md).

Captured from a working session and tidied into shape. Several of these
**revise** decisions already in `../project-plan.md`; that is noted where it
happens, so the spec can be updated deliberately rather than drifting. Open
questions are collected at the end — they are genuine forks, not gaps in the
notes.

## The Pro tier finally has a reason to exist

Two of the thoughts below solve the hole recorded under "Pricing: the floor is
right, the ceiling is missing". Start gives away unlimited courses, 20 logins,
0% and unlimited students, and nothing pulled anyone past it. Now something
does, and both gates are the same kind of thing: **not more capacity, but
control over how the creator appears.**

|                                                | Free                     | Start                    | Pro                                     |
| ---------------------------------------------- | ------------------------ | ------------------------ | --------------------------------------- |
| Listed in Qori's shared catalogue              | No                       | No                       | **Yes**                                 |
| Private group (students see all its courses)   | —                        | —                        | **Yes**                                 |
| Transactional mail — access, receipts, invites | Yes                      | Yes                      | Yes                                     |
| Campaign sending                               | 10/day                   | Yes                      | Yes                                     |
| Sends from                                     | Qori marketing subdomain | Qori marketing subdomain | **Their own domain**                    |
| Custom email templates                         | No                       | No                       | **Yes**                                 |
| System email (receipts, access)                | Qori's                   | Qori's                   | **Theirs**                              |
| Upsell block in the confirmation email         | No                       | No                       | **Yes**                                 |
| Reminders before a session                     | None                     | One, fixed timing        | **Several, own offsets and send times** |

Two sentences, and the second is the one that sells: _Start runs your school.
Pro makes it yours_ — your own group, your own domain, your own templates, your
own row in the catalogue. Every Pro line is about identity rather than capacity,
which is why none of them costs Qori anything that scales.

**The private group is the reason to buy Pro. The catalogue is not** — see the
answers below: restricted to Pro, it starts empty, and an empty catalogue is
worth nothing to the people paying to be in it. It becomes an argument in a
year, not at launch.

## A shared catalogue, and a private one for Pro

Creators publish courses to a **shared Qori catalogue split by category**. Pro
gets a private catalogue page of their own instead of sitting in the shared one.

- **Call it a catalogue, not a community.** Skool, Circle and Mighty have made
  "community" mean a discussion feed; a page that lists courses by category is a
  directory. Using their word invites the comparison Qori loses and promises a
  feature that is deliberately out of scope. _(Naming call, worth making before
  it reaches any UI copy.)_
- **This revises §1 and §11.** §1 says Qori is "not a stall that sells anything
  to strangers" and "does not go hunting for students"; §11 lists a public
  `/lessons` catalogue as optional and not v1 core. A shared, categorised
  catalogue _is_ a discovery surface. That may well be right — it is the cheapest
  acquisition loop a platform like this has, and it makes every creator's
  presence worth something to the next one — but it should be a stated revision,
  not a quiet one. The positioning sentence in §1 needs rewriting either way.
- **Listing starts at Pro, not Start** (settled below). §5's existing rule bars
  free from listing publicly; that now extends to Start, so §5 needs the edit.
- **It creates a moderation obligation nobody has costed.** Once Qori's own page
  carries other people's courses, Qori's brand is attached to their content.
  Approve-before-listing is the usual answer, and it means the admin console
  needs a second write surface (pricing was the first, §24.4) plus a queue
  somebody actually works through. Cheap to build, ongoing to run.
- **The "private page" turned out to be a private _group_, not a page** — see
  the answers below. It is a container of courses that students sign into, which
  makes it a membership rather than a marketing surface, and a much more valuable
  feature than a branded landing page would have been.

## Email: templates are the Pro gate

Pro customises email templates, **including system email** (payment success,
enrolment confirmation). Lower tiers send on Qori's templates.

- This is a clean gate because the EDM builder is being built anyway. The
  template system already plans two kinds — platform transactional and
  workspace-owned EDM. This adds a third relationship: a Pro workspace may
  **override** a platform transactional template with its own.
- **Pro also sends from its own domain**, which is the more important half of
  the gate and is about deliverability rather than packaging — see answer 1
  below. Custom templates and a custom sending domain are the same idea (their
  mail looks like theirs) and should ship together.
- **Two guardrails the override needs**, or a creator can silently break their
  own enrolments:
    - **Required merge fields.** A customised access email that loses the magic
      link is a course nobody can open, and the support ticket lands on Qori.
      Validate on save that every required field for that template kind is
      present, and refuse the save rather than warning.
    - **Transactional stays transactional.** A customised receipt must not
      inherit the marketing footer. §9's consent and unsubscribe gates are
      deliberately not applied to transactional mail; letting a creator paste an
      unsubscribe link into a receipt would let a student unsubscribe from their
      own course access.
- **Falling back cleanly matters.** A Pro workspace that lapses to Start still
  has custom templates on file. Reverting to Qori's defaults is the correct
  behaviour, and the custom ones should be kept rather than deleted so an
  upgrade restores them.

## Storage, properly defined this time

Four distinct roles that were previously blurred into one list:

| Role                                       | Who provides                    | Notes                                                                    |
| ------------------------------------------ | ------------------------------- | ------------------------------------------------------------------------ |
| **Course material** — docs, slides, images | **Qori's own storage** (R2)     | The default. **Fixed 100MB per file for every plan.**                    |
| **BYO drive** — any lesson file            | Google Drive, Dropbox, OneDrive | The creator's own account, their own bill                                |
| **Video**                                  | Vimeo, YouTube                  | Hosting, not drive storage — a different job                             |
| **Live**                                   | Zoom, Teams                     | Offered, never required. A creator with no live lessons connects nothing |

- **Qori storage is not a BYO option, and BYO is not Qori storage.** They are
  different roles: one is the convenience default for course material with a
  hard cap, the other is the creator's own drive. Listing them side by side as
  "providers" was the confusion.
- **A fixed 100MB replaces the per-plan cap.** `config('qori.storage.max_upload_mb')`
  currently reads 20/200/500 by plan; that becomes a single number. This is a
  code change, and it is the right direction — it drops storage as a plan lever,
  which the pricing note already argued against on the grounds that metering
  storage contradicts "their files stay theirs".
- **Video and audio still never touch Qori's storage.** Unchanged, and the 100MB
  cap makes it self-enforcing for anything but a very short clip.
- **§17.7 can close.** Audio had no provider; Drive, Dropbox and OneDrive all
  serve audio files perfectly well, so audio is simply a BYO-drive asset.

## What this costs in connectors

Everything above needs providers that do not exist yet. Today
`Lesson::allowedProviders()` knows `qori_s3`, `dropbox`, `vimeo`, `zoom`,
`teams`, and only Dropbox and Vimeo have resolvers (`DropboxStorage`,
`VimeoVideos`). Nothing has an OAuth connect flow at all.

New: **Google Drive**, **OneDrive**, **YouTube**. Plus the connect flow for
every provider, which is the missing half of §8 noted in Next item 6.

- **The by-asset security line applies to all three.** Drive, OneDrive and
  YouTube share the same property: their shareable link is permanent and
  anonymous, with no expiring-link primitive. That is the creator's tradeoff to
  make on their own file — but for **paid** video it becomes Qori's support
  ticket when it leaks. The line already proposed for Drive should cover
  YouTube identically: fine for free and preview lessons, an expiring-link
  provider required behind a paywall.
- **This revises §8 and §16.** §8 says "Google Drive v1 = no" and "YouTube
  trailer only"; §16 lists "Drive / YouTube as paywall" as out. Both change.

## Answered 2026-09-06, with what each answer implies

**1. EDM — leaning to no module at Pro or under; alternatively Pro sends from
their own Postmark domain and lower tiers from Qori's.** Not final.

The domain option is the better of the two, and the reason is stronger than a
feature gate: **it is reputation containment, not packaging.**

- If free and Start creators broadcast from `qori.com`, one creator's bad list —
  bought addresses, high bounce, spam complaints — damages the sending
  reputation of the domain every other creator shares. Including Qori's own
  transactional mail. The failure mode is that **magic-link sign-in stops
  arriving for everybody**, and domain reputation is slow and painful to rebuild.
- §9 already picks Postmark's separate transactional and broadcast streams,
  which isolates the stream and its IPs. It does not isolate the **domain** —
  the DKIM `d=` is still shared. So streams are necessary and not sufficient.
- That argues for a sharper rule than either option as drafted:
    - **Qori's primary domain carries transactional mail only.** Never marketing.
    - Lower-tier campaigns go from a **separate Qori marketing subdomain**, so a
      reputation problem cannot reach sign-in.
    - **Pro brings their own domain and DKIM**, making their reputation their own
      — which is also the thing a professional actually wants, since mail from
      their own domain is what their list recognises.

Two arguments against removing EDM below School:

- **§4's funnel depends on it.** The locked funnel is "they invite their people
  (EDM) → learner enrols on the web". Remove EDM from Start and the invite step
  disappears, which breaks the product's own central loop.
- **It surrenders a verified competitive advantage.** Skool sends no campaigns at
  all; Circle charges $99/month for its Email Hub, more than its entry plan. Mail
  included at the base tier is a real edge, and giving it up costs more than it
  saves.

The distinction that resolves it is **broadcast versus transactional**, which
§9's own four types already imply:

| Type                      | Nature                  | Availability                                             |
| ------------------------- | ----------------------- | -------------------------------------------------------- |
| Receipt + access          | Transactional           | Every tier, Qori's domain, always                        |
| Invite to a known contact | Transactional in effect | Every tier — the funnel needs it                         |
| Launch campaign to a list | Broadcast               | Paid tiers, marketing subdomain; Pro on their own domain |
| Stalled / new lesson      | Broadcast               | Same                                                     |

_Recommendation: keep EDM at all paid tiers, gate the sending domain rather than
the module._ The tier gate then falls out of a correct architecture instead of
being an arbitrary paywall.

**2. Start cannot list in the catalogue either — listing begins at Pro.**

Cleaner ladder, and it disposes of the moderation problem below. One consequence
worth planning around: **a catalogue restricted to the top public tier starts
empty**, and an empty catalogue is worth nothing to the creators paying to be in
it. Chicken and egg.

_So do not sell the catalogue as the reason to buy Pro._ The private group is the
reason; the catalogue is a bonus that becomes worth something later. Saying it
the other way round writes a cheque the product cannot cash for a year.

**3. The private Pro page is a private group — and it is bigger than a page.**

Not a landing page or a domain feature: a creator creates a **private group**,
their students sign in, and the group shows every private course available to
them. Expected to work particularly well in the iOS/Android app.

Followed through, this is **student memberships arriving through a different
door** — the thing §16 lists as out of v1, and the largest revenue-model gap in
the competitive analysis. A group is a container above courses, and enrolling
someone in the group grants access to everything inside it. That is a
membership.

Which is good news, because it means one feature answers three things:

- the Pro upgrade reason
- §16's memberships exclusion, which the market has moved past
- the mobile home screen — "your group" is a far better first screen than a flat
  list of individual enrolments

Modelling questions it raises, none answered yet:

- Is a group the **unit of enrolment**, replacing per-course enrolment, or an
  additional grant that sits alongside it? Enrolment is currently attached to one
  course (§21.1).
- Can a course belong to more than one group?
- Is a group the natural home for **recurring** billing later? It is the obvious
  shape for it — a monthly subscription to a group rather than to a course.
- Does a group have its own join page, or is access only ever granted by the
  creator?

**4. Nobody moderates the catalogue.**

Accepted — and the Pro-only restriction from (2) is what makes it safe. Price is
the filter: a creator paying for Pro is not posting spam. Real experience running
an events community page beats a theoretical worry, and the same shape applies.

One thing worth keeping that is not moderation: **a takedown path.** Not review
before listing, just the ability to unlist after a complaint — an `is_listed`
flag and a staff action. It is the difference between choosing not to review
things and being unable to respond when something needs removing, and a platform
hosting third-party content generally needs the second.

**5. 100MB is the whole-course limit, not per file, across all paid tiers.**

A materially different design from what was recorded, and a better one — it caps
what a course can put on Qori's own storage in total, which pushes anything
larger to BYO exactly as §8 intends.

Consequences:

- `config('qori.storage.max_upload_mb')` currently reads 20/200/500 **per plan,
  per file**. It becomes a single per-course aggregate. Code change.
- **The upgrade path is inert until prices exist.** The billing page works, but `SubscriptionPrice` rows are staff-managed data at `/admin/pricing` and a fresh install has none — so a creator sees "Paid plans aren't available just yet" and there is genuinely nothing to buy. Needs a staff user (`php artisan qori:staff:create`) and real Stripe `price_…` ids. **This is what "there is no upgrade function" actually was**: not a missing page, an unseeded price list.
- **A creator lands in "Learning" mode.** `/dashboard` is not `/w/*`, so the new context switcher reads _My learning_ even for someone who only teaches. Home shows both hats so nothing is hidden, but it under-sells the teaching side on the page a creator sees most.
- ~~**Over-cap courses are not locked.**~~ Built 2026-09-07 — see the Done entry above. Every course goes read-only together while a workspace is over its cap, capabilities stop and obligations do not, and the state is computed so getting back under lifts it.
- **No course editing.** A course's title, summary, price and now `hours` are set at creation and cannot be changed afterwards — there is no edit form. `hours` in particular is reachable only when first creating the course, which makes §12's certificate hours easy to miss. Small gap, awkward consequences.
- **`MediaAsset` has no `course_id`, so the total cannot currently be computed.**
  That is a gap in what was just built: the model carries `workspace_id` and
  `purpose` but nothing tying an asset to the course it belongs to. Enforcing a
  per-course cap needs that field, and needs the sign step to sum the workspace's
  stored assets for that course before signing.
- **The cap is a wall, not a ladder** — identical across paid tiers means hitting
  it cannot be solved by upgrading. That is fine and consistent with refusing to
  meter storage, but the error copy has to offer a real resolution, and the only
  honest one is "move this lesson to your own Drive or Dropbox". §23's rule about
  never inventing a hopeful suggestion applies directly.
- 100MB total is **tight for slide decks.** A few image-heavy PDF decks reach it.
  That is arguably the point, but it should be a deliberate choice rather than a
  discovery a creator makes halfway through building a course — the studio needs
  to show the running total against the cap, not just refuse the upload that
  crosses it.
- Free tier is unstated. §5 currently mentions 20MB per file on free; a
  whole-course number for free is still needed.
