# Decision record

> Settled product and architecture choices, each with its reasoning, so a
> later reader can tell whether the reason still holds.
>
> **Entries have ids and are appended at the end.** A decision is `D-###` in
> its heading and is cited by that id. A new one goes at the **end** of
> `## Decisions`, under the heading for the day it was made — never at the
> top, and never inside an older entry, so two people recording decisions on
> one afternoon add lines at the same place in the file and git merges them
> without a conflict. Amending a decision is a new entry that cites the old
> one. The bullets under "Earlier decisions" predate the ids and keep their
> shape.

[Current plan](../../PLAN.md) | [Planning index](README.md)

## Open decisions

### Decisions needed (14 September 2026; the storage drafts added 16 September 2026)

One line per draft that waits on the owner, read from each draft's "Before
this can be ready". A stream owner strikes a line with the date when the
answer is written into the task.

- `T-006` — How Vue reads lang: a shared Inertia prop per page, or a
  client-side dictionary. The whole design, and it is not made.
- `T-011` — Whether `AppException::resolution()` stops falling back to the
  code's generic resolution, or lang files say `'resolution' => null` where
  the omission is meant.
- `T-013` — What a staff member does with a failed fulfilment row they cannot
  retry: email the creator, or run a command that does not exist yet.
- `T-018` — The production queue: `database` on Postgres, as the earlier
  entry argues, or otherwise; and what Laravel Cloud's managed queue does to
  `QUEUE_CONNECTION`.
- `T-020` — What Neon's plan retains and for how long — the owner holds the
  account, and the restore procedure depends on the answer.
- ~~`T-025` — Whether a Peer's dates follow their own zone or the Group's.~~
  **Answered 17 September 2026 (`D-028`):** their own, falling back to the
  Group's, with the zone named and the Group's zone beside it.
- `T-028` — Which storage connector ships first, or whether each is
  deferred; waits on `T-044`'s answers too.
- `T-032` — Which receiving mailboxes count (Gmail and Outlook are the two
  that matter), where the evidence lives, and whether a missing receipt
  blocks the task.
- `T-040` — The one readable form width, as a named token rather than a
  third judgement call. The fresh capture it waited for arrived with `R-004`
  on 17 September 2026: Title and Hours both measured 934px at 1440px.
- `T-043` — Whether an invitation link is single-use and whether it expires;
  what a price of nothing on a paid Series means for the creator's numbers.
- `T-044` — ~~Whether disconnecting leaves each Peer's vendor access in place or
  revokes it first; whether the Episode form keeps offering a provider whose
  connector is not built yet;~~ **answered:** access stays in place (`D-021`),
  and the form keeps offering every provider (`D-018`). Still open: the Google
  app published and brand-verified before any creator connects; whether the
  Google Drive section shows before `T-094` can use it (recommended: hidden
  until then); and how the task is split (19 September 2026).
- `T-045` — Whether campaigns ship before beta at all, or are hidden with a
  recorded reason; and if they ship, what sending waits on and what the
  consent gate is.
- `T-049` — Redemption limits; what a voucher may do to a free Series and to
  zero; where the code is entered; what a creator sees; which timezone the
  dates are read in.
- `T-055` — The support route for the address-changed alert; a stable HTTPS
  home for the logo; the promotional-content decision below; the
  message-by-message copy.
- `T-079` — What reads `subscription_starts_at`; whether a trial's
  `start_date` counts; whether the console shows it.
- `T-084` — Clear the intended URL when the sign-in page renders, or bind it
  to the guest session that stored it.
- `T-085` — Whether "can be paid" is an account id or `charges_enabled`, and
  whether the sentence names the creator.
- `T-086` — The rename line's wording, with `:group` interpolated.
- `T-088` — Whether a whole price drops ".00" on the public pricing page.
  `R-004` recommends naming USD and keeping the shared formatter's current
  precision for the first correction.
- ~~`T-089` — Whether a Peer whose vendor access is not ready yet meets a small
  page on the new tab or is sent back to the Series page; whether the JSON play
  route dies with the Vimeo embed; whether the 502 page belongs here or in
  `recovery`.~~ **Answered:** the Series page (`D-020`, 17 September 2026); the
  play route is `T-090`'s to remove; the 502 page shipped with `T-113`
  (19 September 2026).
- ~~`T-090` — Whether a paid Series may use YouTube or Vimeo before YouTube's
  written approval and Vimeo's §3.5 permission are in hand.~~ **Answered
  17 September 2026 (`D-019`):** yes, both vendors hold Episodes in any Series,
  because what a paid Series sells is the creator's time and knowledge, not the
  video. Vimeo Free answered the same day (`D-018`): offered, Public-only
  stated.
- `T-091` — ~~Whether one Series may mix providers; whether a folder or meeting
  belongs to one Series and no other;~~ **answered 17 September 2026
  (`D-025`):** mixing allowed, one container per provider, dedicated to one
  Series, one connected provider recommended and not enforced. Still open: the
  timeout, re-check and sweep numbers, which `T-093`'s timings inform; and
  whether grants waiting on the creator also appear on the Series' Peer list.
- `T-092` — How long a Peer's return from signing in with a vendor may wait
  while their other Series are caught up; and whether the page reads
  "Connected accounts".
- ~~`T-093` — Who holds the Google Cloud project and the four test identities;
  whether the Workspace pass may follow the free-tier result; and whether the
  600-address cap is measured on a folder or left provisional.~~ **Answered
  19 September 2026:** the owner, on a `useqori.com` Google account, as the
  production project; the Workspace pass may follow; the cap is not measured
  and `T-094` holds it in config.
- `T-094` — ~~Whether one folder serves one Series and no other~~ (answered
  18 September 2026, `D-025`), and whether an admin may pick files with the
  owner's token. The legacy free Google edition
  answered 17 September 2026 (`D-018`): it warns, it does not refuse.
- `T-095` — Whether to pay for a Dropbox Plus account and a team trial, on
  whose card; and whether the spike may apply for production approval while it
  runs.
- `T-096` — Answered 17 September 2026 (`D-018`): the storage and Join steps
  are stated on screen and no fallback is built, and Dropbox video is offered
  with its streaming limits stated. What remains is whether a `rate_limit`
  grant, which `T-091` counts as Qori's to retry, should still reach the
  creator.
- `T-097` — Whose account registers the Entra app; whether a paid work tenant
  and a Microsoft 365 subscription are bought for the test.
- `T-098` — Whether free OneDrive and Microsoft 365 Basic are one dropdown
  entry or two, and whether the task splits into connect, grant and Peer
  sign-in. Which tiers ship answered 17 September 2026 (`D-018`): all of
  them, each with its limits stated.
- `T-099` — Whether to pay for a Zoom Pro licence to run the spike, and
  whether storing a registrant id and join link per Peer is allowed under
  Zoom's API terms. Zoom's place in beta answered 17 September 2026
  (`D-018`).
- `T-100` — Whether the creator picks an existing meeting or Qori creates one
  from the Series. ~~Whether showing a recording's passcode to every Peer is
  acceptable; and what a cancelled occurrence does to its Episode.~~
  **Answered 17 September 2026:** the passcode is shown to every Peer with
  access (`D-027`); a cancelled session is `cancelled_at` on the Episode, with
  Undo (`D-026`).
- `T-122` — A month of Zoom Workplace Pro, the user-managed General app in
  development mode, and a beta-share request for one outside account; the
  spike waits on all three (`D-031`).
- `T-128` — The interval for `qori:sessions:notify` against Laravel Cloud's
  sleep timeout, chosen with `T-091`'s sweep (`D-028`).
- `T-130` — Whether `odt`, `ods`, `odp` and `epub` join the upload allow-list
  (`D-030`).
- `T-139` — The Free plan's per-Series storage figure beside the 100 MB the
  paid plans were given on 6 September 2026 (`D-030`).
- `T-101` — Whether a paid Series may run on Teams under Microsoft's terms,
  and where a Teams tier lives when there is no connection behind it. Teams'
  place in beta answered 17 September 2026 (`D-018`).
- `T-102` — Whether Qori restricts checkout to cards or leaves the creator's
  Stripe settings to decide; and whether a buyer whose delayed payment failed
  is emailed, and from which stream.
- `T-103` — Whether a partial refund takes access away; whether a chargeback
  does what a refund does; whether the buyer is told a refund is why the Series
  closed; and whether the creator's Peer list shows a refunded Peer.
- `T-104` — Whether each plan card carries its plan through registration and
  setup or every card leads to one Start sharing; and what a signed-in owner
  sees there instead.
- `T-105` — Whether a 44px touch size is a new button size or the default below
  the small breakpoint; and which controls beyond the ones `R-004` measured
  count as primary.
- `T-108` — The two registration hints' wording, especially the receiving verb;
  and whether "I want to learn" moves to lang with them, since it carries the
  same course framing.
- `T-109` — The certificate's new sentences, including "marked every Episode
  done"; and whether "Issued by" and "This certifies that" overstate too.
- ~~`T-170` — Whether Qori's pricing and billing pages offer a currency menu
  beside the prices, or pick from the visitor's country alone; and what they
  show a visitor whose currency has no fixed price (22 September 2026, `D-047`,
  `D-048`).~~ **Answered 22 September 2026:** USD, EUR and AUD always, plus
  the visitor's own currency when it is none of those; a visitor without a
  fixed price sees the USD price with a line saying checkout charges their
  own currency.
- ~~`T-180` — When a subscribed Group changes plan: whether the owner pays a
  prorated difference at once or the new price from the next renewal, and
  whether a downgrade happens at once or at the end of the period paid for
  (22 September 2026).~~ **Answered the same day (`D-052`):** Claude's
  billing. An upgrade is charged at once, prorated, and restarts the cycle; a
  downgrade takes effect at the end of the period paid for.

### Open decision: promotional content in access confirmations (2026-09-13)

**Proposed by the designer; not owner-approved or implemented.** The preserved
[communications policy](communications-policy.md#pro-can-upsell-in-the-confirmation-email)
allows Pro offers in confirmation mail and asserts they do not alter its
transactional type or require an unsubscribe footer. That categorical
assumption is not supported by current guidance: ACMA specifically identifies
advertising inside service/shipping messages without unsubscribe as a problem.
[ACMA common mistakes](https://www.acma.gov.au/telemarketing-and-e-marketing-common-issues-and-mistakes)

The [email design proposal](ui-system-email.md) recommends factual access and
purchase messages, with Pro offers in separate consented promotional mail.
This preserves delivery of essential security/access messages when someone
opts out of promotions. It changes the earlier composition proposal, so it is
recorded as a decision for the owner, not a review finding or a task.

If the combined variant is retained, settle its classification, consent,
suppression scope, sending stream and unsubscribe treatment before making it
ready. Do not copy the old “no unsubscribe” assertion into a template as though
the receipt/access subject alone determines its requirements. The deferred
custom-template/editor direction is otherwise unchanged.

## Decisions

Oldest first. The bullets directly below predate the ids; everything after
them is one entry per decision, `D-###`, under the day it was made, and the
next entry goes at the end of the file.

### Earlier decisions

- **The rename went all the way through, not just the copy** (2026-09-09, owner
  direction). This **reverses** the "Implementation boundary" section of
  [`terminology-refactor.md`](terminology-refactor.md), which said to keep
  `Workspace`, `Course`, `Lesson` and `Enrollment` as internal names.
    - **Why the reversal is evidence-led.** That boundary existed to avoid "a
      high-risk database/API migration for a brand-language decision", and its
      acceptance criteria listed what it was protecting: "existing links,
      purchases, access, progress, certificates, API clients and analytics
      continue working". None of those exist yet — Neon holds no rows,
      `routes/api.php` exposes no endpoints, there are no users and no bookmarks.
      The risk it guarded against reappears the day Qori has customers, so doing
      it now was the cheap moment and the last one.
    - **The mapping**, including the parts the spec did not name:
      `Workspace→Group`, `Course→Series`, `Lesson→Episode`, `Enrolment→Access`,
      `Contact→Peer`, `WorkspaceMember→Collaborator`, `Teach→Share`,
      `Learning→Shared`, `Student→Peer`, `Teacher→Creator`. Tables and columns
      moved too (`workspace_id→group_id`, `course_id→series_id`,
      `contact_id→peer_id`), as did URLs: `/w/`→`/g/`, `/c/`→`/s/`,
      `/learning`→`/shared`, and route names `teach.*`→`share.*`.
    - **Four collisions a bulk rename creates, recorded because the next one will
      do the same.** `Series` is its own plural, so `$courses` (the service) and
      `$course` (the model) collapsed into one variable in two controllers, and
      `coursesUrl`/`courseUrl` collapsed in a Vue page. `Contact` and `Student`
      both became `Peer`, silently merging two _different_ dashboard measures —
      people holding access, and everyone the Group knows — into one duplicated
      array key; they are now `peersWithAccess` and `peers`. And the nav's own
      `NavGroup`/`groups` clashed with the product's Group, so nav sections are
      `NavSection`/`sections`.
    - **What a case-sensitive rename misses**: SCREAMING_CASE constants
      (`TYPE_NEW_LESSON`, `CONSENT_STUDENT`, `PURPOSE_LESSON`) whose _values_ were
      rewritten while their names were not, and ALL-CAPS string literals in tests.
      Both were found by the suite rather than by grep.
    - **Prose that must not be renamed**: "contact us" in error copy. Protected
      with a sentinel through the rewrite.
    - Verified by 390 tests, PHPStan level 7 and a clean `vue-tsc` — and the type
      check earned its keep, catching `Passkey.id` still typed `number` after the
      move to ULIDs.

- **The queue is `deferred`, not `sync`** (2026-09-08). `deferred` runs a job in
  the same process but after the response is sent, so a request stops waiting on
  mail — with no worker and no `jobs` table, which is why it is reachable today
  when a real queue is not. Two properties are sharp edges rather than
  preferences, and both were verified rather than read:
    - **It is not durable.** `InvokeDeferredCallbacks::terminate()` only invokes
      callbacks when the response status is < 400, and `DeferredQueue` does not
      mark them `always`. Probed directly: a 200 response ran the callback, a 500
      dropped it silently. Under `sync` it would already have run.
    - **It only flushes over HTTP.** Nothing in the console kernel invokes
      deferred callbacks, so a job dispatched from an artisan command never runs.
      No Qori command dispatches one today; check before adding one.
    - Consequence for design: anything whose loss would break an obligation — the
      course-access email above all — must either not be queued, or wait for a
      real worker. Nothing implements `ShouldQueue` yet, so this is a rule for the
      first thing that does.
    - When a real queue is wanted, `database` on Postgres
      (`SELECT ... FOR UPDATE SKIP LOCKED`) is one fewer service to run than SQS or
      a Valkey queue. Note that deploying Laravel Cloud's managed queue silently
      sets `QUEUE_CONNECTION=cloud` for the environment regardless of what is
      configured.

- **Four product decisions, taken 9 September 2026** by the owner, after the
  planning restructure surfaced them as things blocking specific tasks rather
  than as open questions in general.

    - **Custom vocabulary unlocks at Pro.** Free and Start speak Qori's words.
      School inherits it, because School is Pro negotiated rather than a
      different feature set. `config/qori.php` is the whole of the change;
      `Terminology` already reads the flag.

    - ~~**A Series with paid access can never be hard-deleted.**~~ **Revised
      9 September 2026**, before it was built. Deletion is available on every
      Series and works by a **seven-day TTL**: the creator asks, the Series is
      marked, and a scheduled job deletes its resources once the week is up.
      Nothing is destroyed on the click, which is the property the original
      rule was reaching for — the concern was never "deletion is wrong", it was
      "somebody paid for this". A week is enough to change your mind and short
      enough not to become storage nobody meant to keep.

        **What survives is what belongs to the Peer**: their payment record,
        their access, and their certificate. What goes is what belongs to the
        creator: the Episodes and the files behind them. That division is why
        this is safe and it is the whole of the design.

        Archiving (`T-009`) remains the instant, reversible option and the exit
        from the over-cap lock. Deletion is the deliberate one.

        **Requesting deletion does not unpublish.** The creator chooses whether
        to take it down first, and a Series about to disappear is exactly when
        its Peers might want a last look. Every surface showing it carries a
        countdown instead — the public page included, because somebody about to
        get access deserves to know it is about to go.

        **The Series keeps its Group, and a status marks it purged.** An earlier
        version of this decision nulled `series.group_id` so the row would
        "belong to nobody", then added a second column to remember what the
        first had thrown away — a column whose only job is to undo another
        change. Asking "so how does a Series relate to a creator then?" is what
        unpicked it. A Series belongs to a Group and a Group has an owner; that
        link should not be cut. Everything "no longer belongs to the creator"
        means in practice — out of their list, out of the plan cap, not
        editable, not publicly reachable — is reachable through the scope
        machinery `T-009` already built, in one line rather than a nullable
        relation across fifteen call sites, and the admin console keeps working
        untouched.

        The one thing the null would have bought is surviving a future Group
        deletion. Nothing deletes a Group today, and when something does it
        will face a larger version of the same problem: `accesses.series_id`
        cascades, so a Peer's paid access already dies with a deleted Group. A
        real hole, and a different task's.

        The certificate survives either way, because it names `$access->group`
        rather than `$series->group` — the issuer is recorded on the Peer's
        side of the division.

    - **Certificates inherit a Group's custom nouns.** A certificate is the
      Group's document and the one artefact a Peer shows to somebody else, so
      Qori's word for it should not override theirs. The reservation — that a
      custom noun may mean nothing to a stranger — is answered by naming the
      Group beside the noun, not by taking the noun away. This does _not_
      unlock custom certificate templates, which stay deferred until after
      beta.

    - **Alerts go through Sentry** — its own app notifications and its email,
      both of which exist already. No Slack and no paging service: Slack is
      available and deliberately not a priority, and paging exists to manage a
      rotation there is nobody to rotate. Revisit if the email stops being
      read, which is the signal that matters rather than the tool.

- **One terminology registry, and the four rules it enforces** (2026-09-09).
  Qori's customer-facing nouns resolve through `App\Support\Terminology`, which
  returns a complete `App\Data\Vocabulary` for a Group. Defaults live in
  `lang/en/terminology.php` because they are copy, and a second locale should be
  a translation file rather than a hunt through `app/Data`. One shared Inertia
  prop carries them to every page, guests included; `useTerminology()` reads it,
  and there are deliberately no client-side defaults to fall back on — a copy of
  the words in TypeScript is the second home this layer exists to prevent.

    The rules are worth stating because each one was a live bug, not a
    hypothetical:

    - **Both forms are stored; neither is derived.** The share dashboard
      rendered "2 seriess" — Series is its own plural, and the count line
      appended an `s`. A count picks its form with `Term::for()`, which tests
      `=== 1` so that zero takes the plural.
    - **Fallback is atomic.** A Group that renamed Series and left Peer alone
      gets the whole default set, never "Trail" beside "Peer". Half a custom
      vocabulary reads as a bug in the customer's own product, and no reader can
      tell which half was intended.
    - **No article immediately before a noun placeholder.** "an :episode" is
      right for Episode and wrong for Trail. "a new :episode" is safe, because
      the article agrees with "new" — and a test walks every lang line to
      enforce it. This is the same failure as the rename's "Add a episode",
      caught earlier and one substitution later.
    - **Code may not change a customer's casing.** Nouns arrive capitalised and
      stay that way, which settled the walkthrough's open question about
      lowercase nouns in navigation: capitalised wins, because the alternative
      is lowercasing a word someone else chose.

    The entitlement is the plan feature `custom_vocabulary`, **false on every plan
    today**. Which paid tier unlocks it is an open product decision, and shipping
    it enabled for a tier would answer that question by accident; the decision is
    one boolean rather than a code change.

    Resolution is memoised per request, keyed by group id — not a cache store. A
    shared cache needs invalidating on every settings write, nothing writes custom
    labels yet, and an unproven cache can only be wrong. The partitioning still
    buys the property worth having now: two Groups rendered in one process never
    share an entry.

    A vocabulary is presentation data and decides nothing. A Group calling its
    Peers "Ruffies" has renamed a label, not granted a permission, and no
    authorisation check may read from this class.

- **Application data moves from MongoDB to Neon Postgres** (2026-09-08, owner
  direction after review). This **reverses** the earlier "MongoDB-only is
  settled, not provisional" entry below, and the reversal is evidence-led rather
  than a change of taste. That entry gave two reasons — schema flexibility and
  avoiding long column-change migrations — and the codebase now contradicts
  both: all 15 migrations are index-only, so the migration burden never went
  away, and every model carries a fixed 6–15 field schema with no heterogeneity.
  The document-store benefits invoked in §21.4 are unused: **zero** aggregation
  pipelines, **zero** transaction call sites, and `embedsMany` used exactly once.
    - **What it cost instead.** The `'array'`-cast bug (trap 8) — a cast that
      silently stores a JSON string no query can see — reached six models across
      two separate discoveries, because nothing declares a column type. Uniqueness
      lives in eight hand-written index migrations rather than constraints.
      `RefreshDatabase` is replaced by `TruncatesMongoCollections` in 49 test
      files. Passkeys and Sanctum needed hand-rolled model swaps and Cashier was
      expected to need one. CLAUDE.md carries a standing list of Eloquent features
      that do not work.
    - **Timing is the argument for doing it now.** There are no production users,
      and the price rises with every feature. This is the cheapest it will ever be.
    - **What would have justified staying**, recorded so the reversal is
      falsifiable: write volume beyond a single primary, genuinely shapeless
      documents, always-single-key access, or multi-master geographic writes. None
      describe Qori, whose access pattern is "everything scoped to one workspace"
      — the most relational shape there is.
    - **Scale is not the concern.** The largest table is `campaign_recipients`; on
      this file's own model (1,000 Start creators × 2,000 sends/month) that is
      ~24M rows/year, which one Postgres handles without partitioning. If sharding
      is ever needed, `workspace_id` is already on every workspace-owned model and
      indexed first, which is exactly the Citus co-location key.
    - **Unchanged:** Valkey for session/cache, R2 for files. One source of truth,
      derived stores only when a measured failure demands one.

- **School language is no longer Qori's fixed customer vocabulary** (2026-09-08,
  owner direction). The product should feel like knowledge moving between people,
  not a school assigning status to teachers and students. The selected defaults
  are **Group**, **Series**, **Episode** and **Peer**, with **Share** as the
  creator mode and **Shared with me** as the receiving view. Prefer “Shared by
  {name}” to inventing a fixed replacement for Teacher. Higher tiers may replace
  the nouns with explicit singular/plural labels — for example, creator “Ruff”
  and Peers “Ruffy/Ruffies” — but labels never alter Owner/Admin permissions.
  “Explore” is rejected because it implies a public catalogue. Existing
  `Workspace`, `Course`, `Lesson` and `Enrollment` code names remain stable in
  the first refactor. Full plan: [`terminology-refactor.md`](terminology-refactor.md).

- **Leading brand line: “Your knowledge today. Their breakthrough tomorrow.”**
  (2026-09-08, working selection). It is more distinctive than “Sharing is
  caring” and keeps the relationship between one person's experience and
  another person's outcome without calling either person a teacher or student.
  Confirm it on Welcome, signup and a real public Series before using it broadly;
  reporting and status copy continues to say progress rather than breakthrough.

- **Redesign before more product chrome** (2026-09-08, reviewed). The empty/ugly read is the Laravel starter kit plus meters, not missing EDM. One week: warm paper + gold semantic tokens, Welcome/auth rewrite, a coherent shell, `TeachDigest.nextAction` wired to the completing control, a deterministic shared `CourseCover` with audience-specific Share/Shared with me/public compositions, Group rename, and mobile/accessibility/state QA. Admin may stay kit-gray. Do not add KPI tiles to fill space. Full spec: [`ui-redesign.md`](ui-redesign.md).

- **Storage is BYO, and that is an advantage — never price it in** (2026-09-06,
  from the competitive analysis). A first pass at the comparison put Vimeo
  Standard ($20/mo) in Qori's cost column; that was wrong. Where a creator keeps
  their video is their account and their bill, most of this ICP already pays for
  Google Workspace or Dropbox, and the marginal cost to them is zero. The
  competitors' "included video hosting" is the same fact wearing a different hat
  — it is why Mighty caps Launch at 200GB, why Kajabi meters, and why leaving any
  of them is a migration rather than an export. Say this in onboarding.

- **§8's Google Drive exclusion needs revisiting, and the line should be drawn by
  asset rather than by provider.** The technical objection is correct: Drive has
  no expiring-link primitive. "Anyone with the link" is permanent and contradicts
  §8's "a copied link stops working"; proxying through the app costs $0.10/GiB,
  fine for a 2MB PDF and ruinous for a 500MB video; permissioning each student's
  Google account is unworkable. But a blanket refusal is Qori imposing a security
  model on someone else's file, which sits badly beside "their files stay theirs"
  — and Drive is the storage this ICP already pays for and already shares course
  material from. Proposed line: **Drive allowed for documents and preview
  lessons; an expiring-link provider required for paid video**, where a leak
  becomes Qori's support ticket. That maps onto the shape
  `Lesson::allowedProviders()` already has.

- **Pricing: the floor is right, the ceiling is missing** (2026-09-06). With
  storage out of the comparison, Start at ~$44 sits against the three
  competitors that also charge 0% — Teachable Builder $89, Skool Pro $99, Podia
  Shaker $99 — at half their price with strictly more freedom. A creator at
  $10k/month saves $505/month against Podia Mover, so $44 is an 11x value ratio
  and $79 would still be 6x. The category is also moving up while abandoning the
  bottom (Kajabi $149→$179 ungrandfathered, Teachable's free plan gone, no free
  tier at Podia or Circle).
    - **Start still stays cheap.** It is the first step off forever-free, the ICP
      is genuinely price-sensitive, and Qori is unproven with real gaps.
    - **The actual hole: nothing makes anyone pay more than $44.** Start already
      carries unlimited courses, 20 logins, 0% and unlimited students, and §5 still
      lists Pro's extras as "TBD". A creator upgrades for nothing.
    - **Contacts / email volume is the only value metric that survives Qori's own
      positioning.** It scales with their real business, costs Qori real money in
      Postmark, and is what Kajabi and Circle already meter so buyers accept it —
      and it breaks neither promise, being no cut of sales and no charge per
      student. The mechanism already exists as the 10-sends/day free cap. Ruled
      out: a percentage of sales (it is the whole thesis), students (the
      anti-Teachable position, enforced in the schema), studio seats (the 20 is an
      anti-sharing cap, not an SKU), storage (would argue against "their files stay
      theirs"). Domain, certificates and listing are fine Pro/School gates but they
      are switches, not meters — they do not grow with the account.

- **School is not on the public pricing page** (2026-09-06, human's call).
  Released to Pro customers on request. A public ~$499 beside $44 makes the
  product look like it is not for a one-person practice and invites a
  negotiation. The one thing it costs is the anchor, since a visible top tier
  lifts middle-tier conversion — recover that by showing a third column with a
  name and no number ("School — for teams and institutions, talk to us"), so Pro
  reads as the sensible middle and no figure is on the page to argue with.
  Note `SubscriptionPrice` already carries `is_public` separately from
  `is_active`, so this needs no schema change — a School row is active and not
  public.

- **Competitive position, researched 2026-09-06** (full analysis published as an
  artifact; sources are third-party review and comparison sites, not vendor
  pages, so figures are directional). The thesis in one line: **every
  competitor's 0% is a promise, Qori's is a property.** Teachable, Thinkific,
  Kajabi, Podia and Skool all advertise 0% on upper tiers, every one conditional
  on using their payment rail — bring your own Stripe to Thinkific Basic and it
  is +5%, to Kajabi +2%. Those zeroes are pricing decisions, and pricing
  decisions get revised. Direct charges with no application fee mean there is no
  code path where student money passes through Qori.
    - **Three category-wide complaints Qori structurally cannot receive**: payouts
      held 45–90+ days (no Qori-held balance exists); lock-in through the payment
      rail (customers and cards already live in the creator's Stripe); success
      raising the bill (Teachable caps Starter at 100 students, Kajabi cut Basic's
      contacts from 10,000 to 2,500 while raising the price — enrolments are not
      seats in this schema).
    - **Two it can**, because they are commitments rather than properties: price
      rises without grandfathering, and billing/cancellation traps. The latter is
      the single most widespread complaint in the category — Teachable sits at
      3.1/5 on Trustpilot with 41% one-star, Circle at 2/5, both on billing rather
      than features. Qori bills through Stripe's hosted portal where a customer can
      cancel themselves; that shape needs to survive contact with a growth target.
    - **The gaps, verified against the repo rather than the plan**: no public
      course page (`/pricing` is Qori's own SaaS page and checkout is POST-only, so
      §4's locked funnel has nowhere to land — this is the blocking one); no
      Google Drive; no student memberships; no progress or completion model (which
      also blocks §12 certificates and §9's stalled-learner campaign); no quiz
      lesson type; no coupons on course sales, only `SubscriptionCoupon` for Qori's
      own billing; no drip; no discussion; no analytics.

- **Object storage is Cloudflare R2 on a direct Cloudflare account**, not
  Laravel Cloud's resold object storage (decided 2026-09-06, once the rates were
  visible). Needs `league/flysystem-aws-s3-v3` in composer; env vars and CORS get
  wired by hand rather than injected from the Laravel Cloud dashboard, which is
  the whole of what the direct account costs in effort.
    - **Both are R2.** Laravel Cloud says so on its own rate card: "S3-compatible
      object storage powered by Cloudflare R2. Same rates in every region — no
      egress fees." So this is a question of margin and free tier, not of product.

        |                            | Laravel Cloud                   | Direct R2                                                |
        | -------------------------- | ------------------------------- | -------------------------------------------------------- |
        | Free tier                  | none                            | 10 GB-mo, 1M Class A, 10M Class B — ongoing, not a trial |
        | Storage                    | $0.02 /GB-mo                    | $0.015 /GB-mo (+33%)                                     |
        | Class A (writes, **LIST**) | $0.005 /1k = $5.00/M            | $4.50/M (+11%)                                           |
        | Class B (reads)            | $0.0005 /1k = $0.50/M           | $0.36/M (+39%)                                           |
        | Egress                     | free                            | free                                                     |
        | Buckets on Starter         | 1                               | unlimited                                                |
        | Billing                    | draws down the shared $5 credit | separate, its own card                                   |

        The free tier decides it. Laravel Cloud's resale has none, so storage starts
        eating the $5 credit — the credit compute needs — from the first byte.

    - **Qori's storage bill is small because §8 keeps video and audio off it.**
      What lands in the bucket is avatars, cover images, lesson documents and the
      EDM template files (JSON + MJML + compiled HTML, tens of KB each). At a
      rough 50MB per active workspace, the free 10GB covers ~200 workspaces; 1,000
      workspaces is ~50GB, i.e. 40GB billable, i.e. **$0.60/month**. The decision
      that made storage cheap was made in §8, not here.
    - **10M free reads a month is not a constraint** — 1,000 students opening 100
      files each is 1% of it. Writes are rarer still.
    - **`LIST` is a Class A op, priced like a write.** Never enumerate the bucket
      to build a UI. The file index lives in Mongo and objects are addressed by a
      known key. This is the one way Qori could make ops expensive.
    - **Signing costs nothing.** `temporaryUrl` is local HMAC, not an API call, and
      `QoriStorage::linkFor()` has no `exists()`/`headObject` before it — so
      `MediaLifetime`'s short TTLs are free, and re-issuing a link on every click
      stays free. Do not add an existence check there without knowing it converts
      every playback click into a billed op.
    - **The real bandwidth trap is serving files through PHP.** R2's free egress is
      free _out of the bucket_; Laravel Cloud bills data transfer at **$0.10/GiB**
    above each compute size's included allowance (allowance number not published
    on the page — it renders per compute size in the dashboard; check it there).
    Stream a file with `Storage::download()` and the bytes leave via compute, so
    you pay $0.10/GiB and R2's free egress buys nothing. Qori is already on the
      right side of this: `PlaybackController` returns the signed URL as JSON and
      the browser fetches R2 directly, so no lesson file ever crosses compute.
      **Keep it that way** — this is the single most expensive thing to get wrong.
    - R2 sets visibility per bucket rather than per object, but that does not mean
      two buckets: keep **one private bucket** and put a Cloudflare Worker on a
      custom domain in front of the public-facing prefixes, the same shape as
      CloudFront proxying a private S3 origin. Public assets get a CDN and the
      bucket never opens. §8's private material keeps using `temporaryUrl`, which
      is already what `QoriStorage` does. Prefix separation (`lessons/`,
      `public/`, `templates/`) from day one.
    - **Laravel Cloud billing, verified.** Starter is $5/mo plus usage, first month
    free, $5 in monthly usage credits that top up automatically — Laravel's own
      words: "you only ever pay for usage beyond them". What that pool covers is
      **not** enumerated on either pricing page; the widely-quoted list including
      object storage comes from a Laravel News article, not from Laravel. Moot now
      that storage is billed by Cloudflare instead.

- **Uploads are presigned-PUT direct to R2, confirmed by a frontend callback the
  server verifies** (researched 2026-09-06, not yet built). The AWS flow carries
  over: the app receives the intent, decides the key, signs a URL, the browser
  PUTs the bytes straight to R2, and the app is told when it lands. R2 presigns
  GET, HEAD, PUT and DELETE, up to a 7-day expiry.
    - **The one S3 mechanism that does not carry over is presigned POST.** R2's
      docs are explicit: "POST (multipart form uploads via HTML forms) is not
      currently supported." That is the form-policy upload, and its
      `content-length-range` condition is the only way S3 enforces a **maximum
      size at the edge**, before bytes land. On R2 that enforcement does not exist,
      so `qori.storage.max_upload_mb` (20/200/500 by plan) is **the app's job, not
      the bucket's**.
        - **`Content-Type` is not enforced either — corrected 2026-09-07, tested
          against the real bucket.** The earlier note here said a mismatched type
          gets a 403 and the declared type is therefore enforced for free. It is
          not. Laravel signs with `X-Amz-SignedHeaders=host` — visible in the URL
          itself — so the signature covers the host and nothing else, and a PUT
          signed for `application/pdf` sent as `Content-Type: text/plain` returns
          **200** with R2 storing `text/plain`. The signed type is a default for the
          stored object, not a constraint on the upload.
        - So **the bucket enforces nothing about the object**: not size, not type.
          Both are checked after the bytes land, in `UploadService::confirm()`,
          which is why the incoming prefix exists — an object becomes an asset only
          once it has been looked at. The mime comparison in `confirm()` is
          load-bearing enforcement, not a defensive assertion; do not let it be
          tidied away as redundant.
        - Size is verified the same way: `HEAD` the key on confirm, compare to the
          plan cap, reject if over. One Class B op, $0.00000036.
        - Signing `Content-Length` was floated as possible exact-match enforcement.
          Given the above it is moot — with only `host` signed, no request header is
          enforced at all.
    - **Frontend callback, not a webhook.** R2 event notifications exist but
      deliver **only to Cloudflare Queues** — there is no direct HTTPS webhook
      destination. Consuming them means a Queue plus a consumer Worker or HTTP
      pull: a second runtime and a second thing to keep deployed, to learn
      something the browser already knows. Skip it.
        - The callback is **untrusted** — a client can claim an upload that never
          happened or lie about its size — so the confirm endpoint never takes its
          word. It `HEAD`s the key and reads the real size and content type from R2.
          Same guarantee as a webhook, no Worker.
        - Make confirm **idempotent**, the same way the Stripe webhook fulfils
          through `EnrolmentService`: a double-clicked confirm is a no-op.
        - Revisit only if an upload can finish without the browser present
          (server-to-server, or a tab that closes mid-upload). Not Qori's case —
          §8 keeps video and audio external, so what uploads here is PDFs and slides.
    - **The presigned URL is a bearer credential: whoever holds it can write that
      key.** So the **server decides the key** — never accept a client-supplied
      path — and scopes it under the workspace before signing, checking membership
      and plan cap at _sign_ time rather than confirm time. Take the path from the
      client and a creator can write into another workspace's prefix; this is the
      storage equivalent of the `BelongsToWorkspace` rule, and nothing else
      enforces it.
    - **Lifecycle rules are needed, and they only cover half the problem.** R2
      supports both shapes (1000 rules/bucket; dashboard, `putBucketLifecycle
Configuration`, or `wrangler r2 bucket lifecycle`):
        - `AbortIncompleteMultipartUpload` / `DaysAfterInitiation` — **set this one
          regardless.** Aborted multipart parts are invisible to the app: they are
          not objects, they do not appear in a LIST, and they _are_ billed as
          storage. Lifecycle is the only thing that can reach them. Qori's files are
          small enough for a single PUT, but the SDK switches to multipart above a
          threshold on its own, so it will happen.
        - Prefix-filtered age-based expiry — for objects uploaded and then abandoned.
    - **Orphan cleanup is a quarantine prefix, `uploads/`, with one lifecycle
      rule** — the human's own proven pattern from S3, adopted over the pending
      registry I first proposed. Sign the PUT into `incomingUploads/{workspace_id}/{ulid}`;
      on confirm, HEAD it, verify size and type, then CopyObject to
      `lessons/{workspace_id}/{ulid}.{ext}`. Nothing reaches the live prefix until
      it has passed.
        - **The invariant is the reason**, not the tidiness: everything under
          `lessons/` is validated _by construction_. Writing straight to the final
          key means an oversized or wrong-type object lands on a live path and is
          deleted afterwards, and a confirm that never arrives leaves an unverified
          object at a real key until a sweep runs. Here a failed check needs no
          cleanup action at all — the rule collects it.
        - **Do not delete the source.** Lifecycle already guarantees it, and an
          explicit delete adds a failure path (copy succeeded, delete failed) for
          something that is handled for free. A few hours of double-store at these
          volumes is pennies.
        - **No scheduler needed** — which matters, because Qori has none configured.
          A registry sweep would have depended on infrastructure that does not exist,
          and would fail silently and permanently if it were ever misconfigured. A
          lifecycle rule is declarative, visible in the Cloudflare dashboard, and
          runs whether or not the app is healthy.
        - The extra CopyObject is **1 Class A op, $0.0000045 per upload**. That was
          the whole cost of the objection, and it is not worth the invariant.
        - The prefix is `incomingUploads`, named by the human from the same pattern
          they have run on S3 for years.
    - **One rule, both actions, scoped to `uploads/`.** A lifecycle rule carries an
      expiry _and_ `AbortIncompleteMultipartUpload` together, and `incomingUploads/`
      is the only prefix a browser ever PUTs to — so the entire cleanup story is a single
      rule on a single prefix: **delete objects older than 2 days, abort incomplete
      multipart uploads.** Two days is generous against an expected lifetime of
      minutes, and the slack costs nothing.
    - **`media_assets` in Mongo survives, as a registry only.** It is no longer the
      cleanup mechanism, but the file index still cannot live in the bucket:
      `LIST` is a Class A op. Written at confirm time, once the object is in
      `lessons/`.
    - **Two bits of bucket configuration a direct account does not do for you**,
      both of which Laravel Cloud would have injected: **CORS** on the bucket
      (allowed origin, `PUT`, and the headers being signed), and knowing that
      **presigned URLs only work on the S3 API domain, never a custom domain** —
      so uploads go to `*.r2.cloudflarestorage.com` even though public reads go
      through the Worker on a custom domain. Both matter for CORS and CSP.
    - **Laravel already ships the local half of this.** A disk with
      `'serve' => true` gets signed upload URLs and an `Illuminate\Filesystem\
ReceiveFile` route for free, so the whole flow runs locally with no bucket.
      A hand-written shim was built and then deleted on finding it. Note that
      `Storage::fake()` is **not** usable here: it stubs temporary upload URLs with
      a placeholder that routes nowhere, so a round trip through it asserts only
      that a string was produced — `UploadTest` uses the real `local` disk and
      cleans up after itself.
    - Installed `league/flysystem-aws-s3-v3`. `QORI_STORAGE_DISK` is still `local`
      until the bucket exists.

- **Valkey is the largest Laravel Cloud add-on, and it is optional.** The
  smallest size, Valkey 250MB, caps at **$6.00/mo** — more than the Starter base
  — though it scales to zero, as do 1GB ($24) and 2.5GB ($48); everything from
  5GB up is always-on. Session + cache on Valkey stays the decision for
  production, but note the exit: `mongodb/laravel-mongodb` ships `MongoStore`,
  `MongoLock` and `MongoDbSessionHandler`, so session and cache can run on the
  Atlas cluster that is already being paid for, at no extra infrastructure cost.
  Worth taking if $6/mo matters pre-revenue; worth reversing the moment session
  reads show up in Atlas load.

- **MongoDB Atlas is the biggest infrastructure line at scale, and it is not on
  any Laravel Cloud invoice.** M0 is free and fine for now; M10 is ~$57/mo. Once
  Qori has real traffic, Atlas costs an order of magnitude more than compute,
  storage and Valkey combined. Laravel Cloud's own MySQL/Postgres and Managed
  Queues rate cards are irrelevant here — Qori uses neither, and the queue lives
  in Mongo.

- **The API names its workspace in a header, not the path and not the token**
  (2026-09-06, revises §22.2's wording). `X-Qori-Workspace: {id}` is read by the
  same `SetCurrentWorkspace` middleware the web uses, so both surfaces share one
  resolver and one membership check. API URLs stay `/api/v1/courses`; the web
  keeps `/w/{workspace}` for §21.6's bookmarkable studio URLs. The workspace is
  deliberately **not** in the token: §22.1 caps sessions at 3 and counts tokens,
  so a token-per-workspace would let a creator with three schools exhaust their
  whole session budget by switching between them.

- **EDM builder: Templatical** (`@templatical/editor`), pending a spike.
  Embeddable drag-and-drop editor SDK, framework-neutral with Vue support, **JSON
  in / MJML out** — and MJML is the requirement, because it compiles to
  table-based HTML that survives Outlook where a CSS-grid builder would not.
  Free where Beefree is not. 13k weekly npm downloads, actively published.
    - **Licence is FSL-1.1-MIT — source-available, not OSI open source.** It bars
      "competing use", i.e. shipping it inside something that substitutes for the
      licensor's own product; each version converts to MIT two years after release.
      Embedding it in a course platform is squarely permitted. Never expose the
      builder itself as a standalone Qori product.
    - **0.x and five months old.** 87 versions in five months means active
      development and a moving API — pin the exact version.
    - **Store the JSON and the MJML as files in object storage, never in Mongo.**
      A BSON document is capped at 16MB and a template with inlined assets can
      approach it; these blobs are never queried, only fetched whole; and keeping
      them out of the database keeps the working set and the backups small.
      Immutable keys per version make template history free.
    - **Render MJML → HTML at save time and store the result as a file too.** Not
      because Node is unavailable — Laravel Cloud runs Node 24 — but because
      shelling out per send would put a subprocess on the hot path of every
      recipient. Rendering once at save and re-rendering in bulk as a job is the
      same shape as any other cache. Sanitise server-side before storing if the
      render happened in the browser.
    - GrapesJS is **ruled out**: real client feedback on it was poor.
    - **Two kinds of template, one component.** Qori's own transactional templates
      are platform data (staff-managed, like `SubscriptionPrice`); a creator's EDM
      templates are workspace-owned (§9). Different ownership and permissions, so
      model them separately and share the Vue editor between them — not one model
      with a nullable `workspace_id`.

- **The API deliberately exposes no payment endpoints.** §4 locks "no payments in
  the app — no Apple/Google IAP", so course checkout and Qori subscription
  billing stay web-only and the native app opens a browser for both. This is a
  store-compliance and revenue-share decision, not a scheduling one: shipping a
  purchase endpoint the app could reach is what turns Qori into something Apple
  takes 15–30% of. Encode it in `routes/api.php` itself, so nobody adds one back
  by reflex.

- **Web and app share the Services layer, never HTTP.** The webapp must not
  consume its own JSON API: Inertia's whole benefit is server-driven props with
  no client state layer, and self-consuming would pay double serialization and an
  extra hop to solve a problem that does not exist. Controllers are thin adapters
  over the same services — `Inertia::render` on one side, `Data` classes on the
  other. `AppException`, Form Requests and `BelongsToWorkspace` already work
  identically on both.
    - The rule that keeps it true: **a controller may shape and may authorise; any
      decision an API would also have to make belongs in a service.** The current
      violation is `EnrolmentController::store`, which does the email → user →
      "no account" decision itself; an API endpoint would have to repeat all three.
    - `/api/v1` is versioned and the web is not, deliberately: both halves of the
      web deploy together, while a native app in a store calls the old API forever.

- **PHPStan runs at level 7 with zero errors, and stays there.** The two vendor
  PHPDoc problems are handled the sanctioned way rather than with a baseline or
  an ignore: `Attribute::make(get: ...)` instead of the `Attribute::get()`
  shortcut, whose return type trips template invariance, and `stubs/Passkeys.stub`
  to say that `usePasskeyModel()` accepts the Mongo-backed model this app
  deliberately swaps in. A baseline would have hidden the `workspacePaused()` bug.

- **`forWorkspace()` is not `acrossAllWorkspaces()`**, and the split came out of
  testing the §24.3 rule rather than reading it. Several services were calling
  the escape hatch to do `acrossAllWorkspaces()->where('workspace_id', $x)` —
  a single-tenant read that simply cannot rely on ambient context. That now has
  its own scope, so the real escape hatch stays rare enough that a test can
  enforce where it appears.

- **Route namespaces settled: group by function, not by package.** `/auth/*` for
  becoming authenticated, `/u/*` for managing your own account, `/w/{workspace}/*`
  for the studio, `/learning/*` for the student surface; root left to `/`,
  `/dashboard` and well-known URIs. Fortify's URLs move via `config/fortify.php`
  `paths` rather than by taking over its route registration — keys must be
  **nested, not dotted**, or they are silently ignored. `laravel/passkeys`
  hardcodes `/passkeys/*` and `/user/passkeys*`, so those are the one group that
  could not be moved.

- **Route addressing settled: slugs are for reading, ids are for acting.** A GET
  that renders a page takes a slug, because that URL is typed, bookmarked and
  shared. Every state change takes the model id — the page submitting already
  holds it, so re-matching a slug gains nothing and loses rename-safety. The API,
  when it exists, uses ids throughout, with slugs allowed only as a search
  filter. Route parameters are named for what they carry (`{course}` vs
  `{courseId}`), and a test asserts a slug posted to a mutation does not resolve.
  One real exception: `/learning/{course}` uses an id even on a page load,
  because course slugs are unique per workspace (§21.3) and student routes carry
  no workspace prefix (§21.6), so a slug identifies nothing there.

- **Deployment belongs to Laravel Cloud, not to GitHub Actions.** No deploy,
  build-and-ship or release workflow goes in `.github/workflows/` — Cloud builds
  and deploys on push, and a second pipeline doing the same thing is a second
  thing to keep correct. Actions is for lint and tests only, if it is kept.

- **`bin/check.sh` removed** (2026-09-05). It existed to capture migrate + test
  output into `storage/logs/check.out` for an agent session that had no shell.
  The suite is run directly in a terminal instead — `php artisan test` — and a
  committed script is not worth carrying for that indirection.

- `AppException` can now name a redirect target (`->redirectTo($url)`). Its `render()` still turns a failed GET into an error page by default, because a failed page load usually has nowhere to go back to — but a spent magic link does: its resolution is "request a new link from the sign-in page", which is only useful if the reader lands on that page. The default is unchanged, so this is opt-in per throw site.

- Admin console settled (docs/project-plan.md §24): separate `Staff` model and guard rather than a flag on `User` — guards are independent session keys, so one browser can hold both a staff and a creator login. Console is read-only; writes arrive later through impersonation into the creator UI, which keeps every staff change on the same validated path a creator uses. `/admin` path prefix, 404 for non-staff, everything audited. Content and enrolment views are blocked until those models exist.

- Sessions/tokens settled (docs/project-plan.md §22): one `user_sessions` collection registers web (cookie/Valkey) and app (Sanctum token) logins together; cap raised from §6's 2 to **3** (web + app + spare), LRU eviction. Sanctum for app tokens only, Mongo-backed model, no SPA mode, tokens never carry a workspace. Web revocation needs both a Valkey destroy and a per-request registry check; remember-me must not resurrect a revoked session.

- Tenancy settled (docs/project-plan.md §21): workspace is the organising unit; global user identity (email unique platform-wide); studio membership and enrolment are separate collections so students are never seats; lessons embedded in the course document; studio routes prefixed `/w/{workspace}`; a user may own/join many workspaces, so the Stripe customer is the workspace not the user.

- ~~MongoDB-only is **settled**, not provisional: chosen for schema flexibility and to avoid long column-change migrations, with Neon Postgres experience elsewhere as the comparison. Accepted cost: hand-rolled adapters for SQL-assuming packages (passkeys done; Cashier expected).~~ **Superseded 2026-09-08** by the Neon Postgres entry above; kept because the reasoning is still the right test to apply to the next store.

- Email provider: **Postmark** (docs/project-plan.md §9). Not yet wired — `MAIL_MAILER=log` everywhere today, so email verification and password reset mail currently go nowhere.

- Session/cache: Laravel Valkey (`redis` driver) in production, set directly in Laravel Cloud's dashboard, relying on the `phpredis` extension already on Laravel Cloud's runtime — no `predis/predis` composer package. Local dev uses the plain `file` driver for both instead, so no local Redis/Valkey instance is needed.

- ~~No SQL anywhere. MongoDB Atlas for every model; Laravel Valkey is the one exception, and it's scoped to session + cache only; queue lives in Mongo, not Valkey, not SQL.~~ **Superseded 2026-09-08.** Every model is on Neon Postgres; Valkey is still session + cache only; the queue is the `deferred` driver.
- One Stripe platform account (Qori's own), creators onboard as connected accounts, student charges are **direct** charges, not destination — 0% platform take on lesson checkout (docs/project-plan.md §7).
- Magic link is additive to Fortify's email/password login, not a replacement — revised from the original plan draft. **Reconfirmed by the owner on 2026-09-10:** sign-in must offer Password and Email link as choices; QR login from the Qori app comes later. The shared-form layout is a [design proposal](ui-components-and-sign-in.md), not an instruction to disable existing passkeys or start implementation.
- Video and audio are never stored on Qori's own S3 — always external (Vimeo / BYO) — docs/project-plan.md §8.
- Do not add `declare(strict_types=1)`.
- Do not add a repository layer. (Written of MongoDB; it survives the move to Postgres unchanged.)

### 11 September 2026

<a id="onboarding-follows-the-entry-purpose-2026-09-11"></a>

#### D-001 — Onboarding follows the entry purpose

**Owner direction, clarified after R-003.** A person registering from a Series
link, including an EDM link, confirms basic details (name, email and personal
timezone), completes verification/payment as required, receives access and opens
that same Series. No creator onboarding belongs in this path, including when
the account also has creator access. A free Series or existing access does not
require another payment.

Creators instead confirm basic details, then advanced/Group details including
timezone, then storage, integrations and seller payment setup, followed by a
guided first-Series flow. **Storage, integrations and seller payment setup are
all skippable during setup.** The owner specifically confirmed that seller
payment setup should be prompted before selling a paid Series, rather than
required before creating any Series.

This supersedes the earlier checklist-only/no-wizard recommendation in the
onboarding research and drafts, and the suggestion to create the first Series
before creator setup. The first-Series action contract still applies when the
person reaches the creation guide. Existing permissions, confirmed payment and
access rules continue to apply; an entry purpose is not a permission role.

The [onboarding plan](ui-onboarding.md) specifies the target paths and identifies
what remains unbuilt. T-008/T-026/T-027/T-028 remain drafts pending implementation
specification. R-003 remains unchanged as historical evidence.

#### D-002 — Selling is its own stream

Three pieces of work — surfacing the public Series link, inviting people to a
Series, and vouchers — share one file set and one question: can a creator
actually sell and share what they made. None of the seven existing streams
describes that. `delivery` is transactional mail and `reachability` is routing,
and putting a commerce decision under either one made the wrong concern the
owner of it. See [`streams/selling.md`](streams/selling.md).

The seam with `onboarding` is deliberate and worth keeping: `T-043` sends an
invitation and stops. `T-027` owns what happens when somebody opens one.

#### D-003 — Collaborators are deferred; one owner runs a Group

**Owner direction.** Collaborators are the creator's own staff, not the Peers
they invite or sell to. Without them, the creator as owner — one user — is
enough to run a Group, and nothing in the core loop needs a second person.

So collaborator invitations are not built, and are not a beta feature. What is
fixed instead is the claim: `config/qori.php` caps team members at 1 on the free
plan and 20 on every paid one, and the Billing page tells a paying creator
"Team members: 1 of 20" when nineteen of those seats cannot be filled by
anybody. `T-046` removed the number and kept the limit, on 12 September 2026.

Everything else stays: the `Collaborator` model, the role enum, `seatsUsed()`,
the cap enforcement and the admin console's counts. The owner seat is a real row
and the Group needs it. Reopen this with a new decision if a customer asks for a
second person, rather than by quietly adding an invite button.

<a id="position-around-creators-existing-files-and-familiar-tools-2026-09-11"></a>

#### D-004 — Position around creators' existing files and familiar tools

**Owner clarification in the pricing discussion.** Qori targets creators who
already keep and share teaching material in Google Drive, OneDrive or Dropbox,
and use services such as YouTube for video. Their existing workflow is the
starting point. The owner has attended several creator Series delivered through
Drive shares; this is evidence for the chosen audience, not a claim about every
creator in the market.

Lead with the familiar provider names and the benefit of starting with existing
files: **“Start sharing with the files you already have.”** The target supporting
message is to connect Google Drive, OneDrive or Dropbox, add existing YouTube
videos, and organise the material into a Series without moving the source files.
Qori supplies the structure, participant access, progress, communication and
optional payment experience. Cloud storage and video-hosting technology are
provided by the services the creator already uses.

For this audience, compare Qori's subscription directly with competitor
subscriptions on the same billing basis, showing platform and processing fees
separately. **Do not automatically add a Vimeo or storage subscription to Qori's
price.** Existing provider subscriptions are existing expenses; a sufficient
free provider plan creates no additional storage subscription expense. This
reaffirms the September 6 BYO decision and corrects the emphasis of the first
September 11 review. Customers seeking a complete replacement for their storage,
video, website and marketing stack are outside this primary positioning.

The provider list is the intended product promise, not a statement of current
connector availability. Google Drive, OneDrive and YouTube are absent from the
current Episode/Connection provider enums. A working link-based flow should say
“use your existing links”; “connect” requires the corresponding connection flow.
“Without moving your files” does not promise automatic migration of another
platform's course structure, student history or permissions. Provider access
rules still apply, including the shareability of an unlisted YouTube link.

This records positioning and comparison assumptions. It does not change prices,
approve a provider implementation, or change the current beta sequence. Detail
and proposed copy: [pricing review](pricing-and-competitor-review-2026-09-11.md#owner-clarification-existing-files-are-the-starting-point).

### 13 September 2026

#### D-005 — A price never exists without a currency

No form had ever set a Series price, and the one hand-priced Series in
development had a price with no currency — the shape checkout would have sent
to Stripe as an empty string. The two columns are now one field pair: validated
together, written together, and refused by a database check constraint when one
is present without the other. Repricing changes what the next person pays and
nothing about anyone who already has access, because an access row carries its
own price and currency from fulfilment. The currency list mirrors the payout
countries and **excludes zero-decimal currencies** (JPY) until somebody decides
how `price_cents` should read for them. `T-054`.

#### D-006 — Signing in lands where you last were; signing out lands on sign-in

**Owner direction, from a walkthrough.** Every sign-in landed on the receiving
home, and the owner — a creator — expected the creator page. Sign-out landed on
the marketing page, which a registered person has no use for.

Sign-in lands on the Group the person last opened, remembered on the user row so
it survives signing out; failing that, their only Group; failing that, the
receiving home, which already lists every Group and offers **Start sharing**.
The receiving home itself never redirects, so it stays the switchboard. The
intended URL always wins, so a guest sent to sign in from a protected page still
returns there. `T-052`.

Sign-out lands on the sign-in page with one sentence saying so, under its own
flash key. Not a holding page: its two options would be "sign in again", which
that page is, and "close the tab", which needs no button. `T-053`.

Registration is unchanged; where a brand-new creator goes first belongs to the
onboarding stream (`T-026`).

#### D-007 — The sign-up choice is used once, and not stored

**Owner direction.** "There is no need for signup_intent. It is a runtime
decision, required once, to show which onboarding flow the new user needs to
go through."

The register form still asks what brings somebody here, and the answer still
decides whether a Group is made — inside the registration request, read from
the request by the listener on the `Registered` event, and never again. The
column is dropped. What is durable is whether the person has a Group, and
sign-in already lands on that (`T-052`). An onboarding flow that needs to know
which path somebody is on asks what they have, not what they once said. `T-059`.

#### D-008 — Domain enums live in `app/Enums`; a layer's contract stays with the layer

`app/Models/Enums` claimed every enum in it backed a column, and after `T-059`
one did not. The claim was only ever enforced by `ModelEnumTest`'s column map,
so the folder name was doing no work the test does not. The eighteen domain
enums moved to `app/Enums`, flat, which is also where `make:enum` puts the next
one. `App\Exceptions\ErrorCode` and `App\Admin\StaffRole` / `StaffAbility` stay
where they are: each is the contract of one layer, and each layer's directory is
already named in `CLAUDE.md` as where its code lives. No per-feature scattering —
these words exist because several features share them. `T-060`.

#### D-009 — Qori asks the country before creating a Connect account

**Decision.** Creating a connected account sends `identity.country` and
nothing else Stripe's own form can ask: no entity type, no requested
capability. The country is the one question on the Integrations page, and it
is required on the POST (`T-062`).

**Why.** The task first wanted the country left to Stripe too, on the
hosted-onboarding page's word that a full-dashboard owner can pick any
country. The sandbox refused every shape without one: a v2 account with a
dashboard must carry a merchant configuration, and a merchant configuration
must carry a country. That sentence describes accounts that reach onboarding
without a merchant configuration, which v2 will not create with a dashboard.
Asking the entity type on Qori's page, from a two-entry select, was the part
that could go: the read-back of an account created this way carries no entity
type and no capabilities until Stripe's form has asked.

**Consequences.** `ConnectPayoutsRequest` keeps one required rule;
`qori.payments.entity_types` is gone. A creator who would rather choose the
country on Stripe's own signup, or who already has an account, takes the
OAuth door (`T-063`), where Stripe's signup asks everything.

#### D-010 — Connect: OAuth beside v2 creation, and every account read through v1

**Decision.** Two doors to one column. Creating an account stays on Accounts
v2 (`POST /v2/core/accounts`, `T-062`); connecting an account a creator
already has runs on Stripe's OAuth endpoints beside it (`T-063`), because the
Accounts v2 page lists OAuth under "you must use Accounts v1" and OAuth is the
only flow Stripe provides for "use the account I have". Both doors end in
`groups.connect_account_id`, and every account is read back through
`GET /v1/accounts/{id}` whichever door it came through — the same page says a
v2 id "can still" be passed to a v1 endpoint and is answered in the v1 shape.
`ConnectAccount` reads `charges_enabled`, `payouts_enabled`,
`details_submitted`, `country`, `default_currency` and the statement
descriptor settings from that shape; the v2 reader is gone.

**Why.** About half of creators already hold a Stripe account, the owner's
figure from six years of e-commerce, and the direction with it: connect the
one they have, without a second KYC, beside creating a new one. The v1 read
also retires a wrong answer: the v2 reader mapped "nothing outstanding" from
a requirements summary Stripe returns as null when nothing is due, so a
finished sandbox account read as unsubmitted on 13 September 2026. One reader
in the shape Checkout already speaks cannot drift that way.

**Consequences.** `STRIPE_CLIENT_ID` is configuration; without it the
existing-account door is not offered and disconnect only forgets, so nothing
depends on OAuth being enabled. The landing route lives under `/u`, because
Stripe matches `redirect_uri` exactly and a Group slug cannot be in it; the
Group and a nonce travel in the session. `T-044` will want the same callback
shape for storage and video, and that is when the pattern becomes a shared
concern. Stripe says OAuth "isn't recommended for new Connect platforms" and
cannot connect a Standard account another platform controls since June 2021;
neither stops a creator connecting their own.

#### D-011 — Onboarding progress lives on the person

**Decision.** Which parts of creator setup were skipped or finished, and when
the walk ended, are recorded on the User (`onboarding_state`,
`onboarded_at`), not on the Group. The Group keeps the facts the walk is read
beside: a chosen name, a connected account. `User::onboardingNext(Group)` is
the question; `OnboardingService` makes the writes; `GroupService::createFor()`
clears the record so making a Group starts the walk. The two home routes send
an owner with an unfinished part to it.

**Amended 14 September 2026 (`T-078`).** The chosen name left the Group too.
`groups.name_set_at` is dropped; `Group::hasChosenName()` reads the owner's
record, which `GroupService::rename()` writes whoever typed the name. The
Group keeps one fact the walk reads beside the record, the connected account.
The owner's review of the model: the column was the same bookkeeping kept twice.

**Why.** Onboarding is a person's journey, a person owns one Group, and a
progress experience on the dashboard would read the person. The owner said so
on 13 September 2026, reviewing `T-075`, which had put the record on the
Group. The same review found Fortify's verification page sending a verified
owner to the home route past setup; the home route honouring the record is
the fix that catches every framework redirect at once.

#### D-012 — One Group per person

**Decision.** A person owns one Group. It is created when they register as a
creator, or the first time a learner chooses to share, and it is where every
Series they make lives. Its plan, its payout account and its storage and video
connections are the settings of their account, one connection per provider,
disconnected before it can be connected again. Nothing in the product creates
a second Group, and `GroupService::createFor()` refuses to (`T-065`).

A person may also be an admin in Groups other people own. That is the only
reason the sharing side has a switcher, and the only case in which one person
sees more than one Group. An admin works with the owner's Stripe and storage,
never their own, because the money and the files are the owner's.

**Why.** `docs/project-plan.md` §21.7 said a user may own several workspaces
and that one person running two schools has two subscriptions. Nothing was
ever built to reach that state, and the owner's model of the product, stated
on 13 September 2026, is the opposite: one school, one learning surface, one
Stripe, one Drive, one plan. The design-review fixture gave Rita five Groups so
one sign-in could photograph every state, which is what put a five-entry
switcher in front of the owner while testing and made the gap visible.

**Consequences.** §21.7 is rewritten. The fixture gives each world its own
owner (`T-066`). Integrations become a settings page, with Stripe as the first
section and storage and video joining it under `T-044` (`T-067`). `T-062` and
`T-063` are aimed at that page. `CLAUDE.md` carries the rule so nobody builds
a "new Group" door without meeting this entry. The `/g/{group}/` prefix stays:
it names the one Group, and it is what lets an admin's session tell the
owner's work from their own.

#### D-013 — Sign-in asks for the email first, then the method

**Decision.** The sign-in page has one email field at the top and, under it,
the choice between Password and Email link. Only the chosen method's controls
follow. Passkey is a separate function and stays below the rule, on its own.
`T-036`'s tabs-first composition is superseded; its other rules stand: one
email field, manual activation so arrow keys never change the operation, a
confirmation that replaces the form, the neutral "if that email has an
account" sentence, and nothing removed.

**Why.** The owner's review on 13 September 2026: passkey is a complete,
separate function, but Email link and Password are options that both need the
address first, and the choice belongs after it. One form whose action follows
the choice is what lets the field sit above the chooser without being
duplicated in each panel or remounted on every switch (`T-077`).

### 14 September 2026

#### D-014 — Planning mechanics for several hands

**Decision.** Status lives in task files only; every stream has an owner in
its front matter; anyone may spec a draft by taking `owner:` on it, and the
stream owner approves; a "Found, not fixed" bullet ends in a disposition from
reports dated 15 September 2026; `blocks:` is derived from `depends:` and the
field has to agree; decisions get ids and are appended at the end of this
file under the day's heading. `T-080`, from the workflow review of the same
day.

**Why.** Closing a task edited the stream file, prepended to this file at the
same line and touched `PLAN.md`, so two people finishing in one stream on one
afternoon conflicted in prose that neither had written. The Files-table
parser read one path per row and treated a glob as a string, so the collision
check missed the rows most likely to collide. Nothing acted on a report
finding: 102 bullets across 37 reports, three repeated in two or three reports
each with no task. Task ids were picked by hand, only the owner promoted
drafts, no stream had an owner, and `blocks:` was wrong in ten places. Each
rule here is checked by `TaskBoardTest` and `qori:tasks --check` from one
implementation, so the prose and the gate cannot drift apart again.

**Consequences.** Old reports are counted, not rewritten. A branch-per-task
flow is not part of this; the owner left it out.

### 15 September 2026

#### D-015 — Sign-in asks for the address alone, then the ways in

**Decision.** Sign-in is two steps in one component. The first asks only for
the email and has **Next**; the second shows the address with a way back to
change it, then the Password / Email link choice and the chosen method's
controls. Passkey stays below both. `D-013`'s rules stand inside the second
step: one form, one posted address, manual activation, the confirmation
replacing the form. **Next asks the server nothing**: the second step appears
for any well-formed address, whether or not it has an account.

**Why.** The owner, the same morning `T-077` had shipped: they wanted the
order of a large mail provider's sign-in, where the address is accepted first
and only then are the password and the email link offered. The server is not
consulted because a first step that answered "no account" would be an
unthrottled way to discover who is registered, and the link request's neutral
sentence and Fortify's single failure message exist to prevent exactly that
(`T-087`).

**Consequences.** Nobody is told on the first step that an address is
unknown; a mistyped address shows up on the second, as a failed password or a
link that never arrives. There is no URL per step, so the browser's Back
button leaves sign-in rather than returning to the address, and a reload
starts at the first step.

#### D-016 — BYO content opens on the vendor's site, granted per Peer on a container

**Decision.** Every bring-your-own storage and live-session integration
follows one pattern. The creator **connects** the vendor account once, with
the narrowest scope that allows the rest plus offline access, and Qori keeps
the refresh token. The creator **picks** what a Series holds with the vendor's
own picker, and Qori stores the item ids on Episodes. When a Peer gets access,
Qori **grants** with the creator's token: it adds the Peer's own vendor
account as a viewer of one container per Series — a Google Drive, OneDrive or
Dropbox folder, or one Zoom recurring meeting — with the vendor's notification
off, and stores the id that comes back. The Peer **opens** each Episode in a
new tab on the vendor's site. On a refund or removal Qori **revokes** that
grant, best effort. Where the vendor has no per-person grant — Vimeo, YouTube,
Teams meetings, Zoom recordings — the Series is the container: the item is
unlisted at the vendor and Qori shows its link only to Peers with access.
Qori's own storage keeps its short-lived tickets; nothing about `qori_s3`
changes.

Two terms come with it. The creator chooses the account tier from a dropdown
when connecting — for Google, "Free Google Drive" or "Google Workspace & G
Suite" — and each tier's limitations are stated on screen before the
connection is made. A Peer of a Series on Google Drive, OneDrive or Dropbox
adds their vendor account as a prerequisite, by signing in with that vendor
once; the record is the person's, not a Group's, so it is confirmed once for
every Series they ever join.

**Why.** The owner, 15 September 2026, on reading a Google Drive design built
on `permissions.create` with the creator's `drive.file` token: "this solution
is exactly what I thought from the beginning", and the design in Qori's terms
"needs to be the blueprint for all the rest of storage/live stream
integration". The same day the owner set the priorities that decide every
trade-off, in order: a Peer gets working access right after signing up,
claiming or buying; and Peers always see the creator's current content.
Downloads, forwarded links and airtight revocation are not concerns —
creators in the owner's experience accept them, the material goes out of date
fast, and revocation is rare. The qualities the owner values: no bytes through
Qori and nothing copied; files stay in the creator's account so edits reach
Peers; video and audio can come from the vendor; each Peer can be removed
through the vendor's API. Granting on a container rather than per file is what
serves the second priority — a new Episode needs no new grants, and far fewer
calls count against the vendors' sharing limits.

**What this supersedes.** The undated bullet under "Earlier decisions" that
called "permissioning each student's Google account" unworkable and drew the
line at Drive for documents only; it is cited here, not rewritten.
`docs/project-plan.md` §8's "Google Drive v1 = no", Dropbox by
`get_temporary_link`, Vimeo "private + embed whitelist", "on attach: force
private, strip public shares", and the enrolment-check-then-ticket playback
line for BYO providers; §16's "Qori S3 + Dropbox + Vimeo tickets" in and
"Drive / YouTube as paywall" out; and the reasoning in `docs/flows/storage.md`
that Drive is excluded because its links cannot be withdrawn. `D-004` stays as
written: it positioned Qori around these providers and declined to approve an
implementation, and this record approves Google Drive and OneDrive beside
Dropbox. The spec text is rewritten when the first provider lands, and the
flow doc with the code, never before.

**Consequences.** A `storage` stream holds the work, with `T-044` moved into
it and re-specified: the Integrations page grows provider sections with the
tier dropdown, the limitation copy, reconnect and token refresh. New drafts,
one per piece: Open as a Qori route that redirects (`T-089`), Vimeo and
YouTube as unlisted links (`T-090`), the grant foundation (`T-091`), the
Peer's vendor identity (`T-092`), then a spike and a provider task each for
Google Drive, Dropbox, OneDrive and Zoom (`T-093` to `T-100`) and the Teams
link (`T-101`); `T-102` and `T-103` in `selling` for the paid path and for
refunds. Vimeo needs a paid plan for Unlisted, not for domain locking, so the
domain-lock rationale in `release-prerequisites.md` is void. Vendor names may
appear in the provider-choice and Peer-prerequisite copy, as a stated
exception to the no-vendor-names rule, because the person is choosing between
those vendors. Which providers enter before beta — and so what `PLAN.md`'s
rule 5 and its Zoom/Teams deferral become — is the owner's, recorded under
"Open decisions" above; nothing here changes `PLAN.md`. The questions each
draft still carries for the owner are listed there too, one line per draft.

### 16 September 2026

#### D-017 — A stored destination belongs to the sign-in that asked for it

**Decision.** Reading a Series page stores nothing. **Have a password? Sign in
instead.** goes through `GET /s/{group}/{series}/sign-in`, which stores the
page and shows sign-in. A magic link returns to what a browser is holding only
when that browser asked for that account's link; otherwise it forgets both
keys and lands where a sign-in with nothing stored lands. The code sign-in on a
Series page forgets both keys. The password, two-factor and passkey responses
are unchanged.

**Why.** Every sign-in regenerates the session and keeps its data, so a
destination written for one sign-in waited for whoever signed in next in that
browser. Three browser walks landed on a page that belonged to someone else's
visit (`T-072`, `T-062`, `T-075`), and both shapes reproduced again on
16 September 2026. The draft's two shapes were ruled out: clearing on the
sign-in page render breaks returning from a protected page, whose redirect
stores the page and then renders sign-in; and a session id stored beside the
URL is the same id at the stale write and at the next person's sign-in
(`T-084`).

**Consequences.** Two people at one browser are still one browser. When the
first asked to sign in, or was bounced from a protected page, and walked away,
the second signing in there with a password, a passkey or a link asked for
there lands on the first person's page. Closing that needs the destination to
travel in the sign-in page's URL instead of the session, which would reverse
`T-008`'s second key. A link minted by `qori:magic-link` no longer returns to
a page the browser was on.

### 17 September 2026

#### D-018 — Every provider is in beta, and a tier is explained rather than refused

**Decision.** Two answers from the owner on 17 September 2026, both amending
`D-016`.

**All seven providers ship before beta.** Google Drive, OneDrive, Dropbox,
Zoom, Teams, Vimeo and YouTube — the whole list the `storage` stream orders,
not a subset. This amends `PLAN.md`'s execution rule 5, which bars new
integrations before the web core loop reaches beta, and the settled line
deferring "broad Zoom/Teams work". The `storage` stream blocks release, and
`PLAN.md` moves with this record.

**A tier is explained, never refused.** Qori offers every tier a creator can
bring and states that tier's limitations on screen before they connect. Where
the vendor's own rules make the sharing weaker than a creator might assume —
Vimeo Free, which can only make a video Public; a Peer's Dropbox storage
quota; a Workspace administrator who has turned outside sharing off; the
non-commercial terms on personal Microsoft 365 and on the legacy free Google
edition — Qori says so plainly and lets the creator decide. **The platform a
creator brings, and its rules, are the creator's own.** That is what
bring-your-own storage means, and a refusal would be Qori imposing its
security model on somebody else's files, which `D-004` already declined to do.

**Qori advises; it does not hand the creator a shrug.** Each tier's copy says
what Qori recommends as well as what the tier cannot do, in words a creator can
act on. "Your videos will be public to anyone with the link" is a limitation
worth saying; refusing to connect the account is not Qori's call.

**Why.** The owner, 17 September 2026: "i want all of those listed to be
available during beta release", and "do not overthink those security loop
hole… a creator comes with vimeo free which only offer public only video is
their responsibility. this is the whole goal of byo storage. We can emphasis
on platform limitation which creator should know. we only advice what is
recommended not a handoff approach."

**What this does not cover.** Two clauses bind **Qori**, not the creator:
YouTube's developer policies and Vimeo's developer agreement both restrict
charging people for access to content served through their APIs. A creator
cannot accept those on Qori's behalf, so they stay the owner's to answer —
see `vendor-accounts.md` and the line under "Decisions needed".

**Consequences.** `PLAN.md`'s rule 5 and its settled Zoom/Teams line are the
owner's to edit, and both now disagree with this record. `streams/README.md`
marks `storage` as blocking beta. `T-090` offers Vimeo Free with its
Public-only limit stated; `T-094` warns rather than refuses on the legacy free
Google edition; `T-096` states the Dropbox storage and Join steps instead of
building a fallback; `T-098` ships every OneDrive tier; `T-099`, `T-100` and
`T-101` lose their "does this enter beta at all" question. The spikes still run
before their providers: a limitation is only honest on screen once somebody has
watched it happen. `docs/planning/vendor-accounts.md` records what the owner
must open, sign up for and pay for to build and test each one.

#### D-019 — Vimeo and YouTube hold Episodes in paid Series too

**Decision.** Vimeo and YouTube are storage options for every Series, priced
or free, with no guard, flag or waiting state on a paid one. A video on either
may be Public or Unlisted; only Private is refused, because a Peer cannot open
it. This amends `D-018`, which kept both vendors out of paid Series until
YouTube's written approval and Vimeo's written permission arrived.

**Why.** The owner, 17 September 2026: "What the creator selling is the
consultation and all the associate knowledge, not the actual video itself. The
video is the material or one of the course material, It can/should be public if
it is on youtube. What creator is selling is their time and knowledge with live
session and work and make lead to free consultation session afterward." A paid
Series on Qori charges for the creator's time, their live sessions and what
they know; a video on YouTube or Vimeo is one of the materials that comes with
it, often public already, and nobody pays to watch it. On that reading the
clauses `D-018` set aside — YouTube's Developer Policies III.G.1.a and
III.G.1.b and Vimeo's Developer Addendum §3.5 — are not what a paid Series
does, and the owner has taken that reading.

**Consequences.** `T-090` drops its paid-Series guard, the two
`paid_series_allowed` config flags and their copy, and recommends Public or
Unlisted as the creator prefers rather than steering them to Unlisted.
`vendor-accounts.md` keeps what each clause says and how to write to each
vendor, as reference rather than as a gate; asking Vimeo is still free if the
owner ever wants it in writing. `release-prerequisites.md` no longer lists
either permission as blocking.

#### D-020 — A Peer who cannot open yet goes back to the Series page, where the notice holds the next step

**Decision.** When Open cannot send a Peer to the vendor because their grant is
not `granted`, the destination is the Series page, `shared.show`, at its
access notice (`#access`), with a one-line flash saying why they landed there.
There is no `shared/OpenBlocked` page. Three things are decided together:

- **Destination.** `shared.show` for that Series. The Series page already
  carries every state's sentence — `T-091`'s notice, `T-092`'s identity
  prompt, `T-096`'s and `T-098`'s vendor steps — so each state has one sentence
  in one place. While a grant is not `granted`, the Series page renders the
  affected Episodes' Open controls as disabled, pointing at the notice, so the
  redirect only catches a page rendered before the state changed, a saved
  link, or Open's own re-check finding a permission gone.
- **Primary action, one per state.** `awaiting_identity`: Sign in with the
  vendor (`T-092`). `awaiting_acceptance`: the vendor's own step (join the
  Dropbox folder, open Microsoft's invitation), with Check again beside it
  (`D-021`). `pending`: no button while Qori is retrying; the sentence says
  when Qori tries next, and never "in a moment" when the next attempt is hours
  away; once the row is due, Check again appears. `needs_creator`: no Peer
  action; the sentence says the creator has been told and that nothing more is
  needed from the Peer.
- **Return path.** Every vendor step a Peer is sent on returns them to, or
  tells them to come back to, `shared.show`. `T-092`'s sign-in already
  returns there; the Dropbox and Microsoft steps open in a new tab, so the
  Qori tab stays on the Series page with Check again in reach.

**Why.** A designer's review of the storage drafts on 17 September 2026 found
the two drafts describing each other's choice: `T-089` shipped no page and
said `T-091` sent the Peer back to the Series, while `T-091` rendered
`shared/OpenBlocked` and said `T-089` built it; `T-096` recorded the
disagreement. A second page would hold a second copy of every sentence and
need a return path of its own, and the Series page is where the Peer came from
and where each state's action already sits.

**Consequences.** `T-089`'s controller turns `VendorLink::blocked()` into the
redirect and its open question is answered; `T-091` drops `shared/OpenBlocked`,
renames `shared.open_blocked.reasons.*` to `shared.vendor_notice.reasons.*` and
disables Open while a grant is not `granted`; `T-096`'s disagreement bullet is
answered; `T-092`, `T-096`, `T-098` and `T-100` write their sentences for the
notice.

#### D-021 — Guidance sits where a person acts, and a wait they can end has a button

**Decision.** Four rules from the same designer's review, 17 September 2026.
They change where the copy `D-018` asks for appears, not what `D-018` decided:
every tier is still offered, and its recommendation and every limitation are
still on screen before the creator connects.

1. **A buyer sees what the Series needs from them before paying.** Beside the
   buy button on the public Series page, and above `T-092`'s identity prompt
   on a free Series, a short list says what this Series' provider needs from a
   Peer: an account on the address they will confirm, a step at the vendor, the
   space the vendor takes from their own account. The lines are
   `accesses.vendor.<provider>.before_buying.<common|tier>.*`, chosen by the
   creator's tier where it matters; `T-092` renders them and each provider
   task writes its own. No line promises the Series is ready the moment payment
   goes through: Qori starts letting the account in when it does, and the
   Series page says what, if anything, is left.
2. **A person who has fixed something can say so, and sees the result.** A
   Peer on `awaiting_acceptance`, or on a `pending` row that is due, has Check
   again (`shared.access.check`), which runs the check at once. A creator has
   Check now beside an Episode's check warning (`share.series.episodes.check`)
   and Try again now on the Integrations list of people waiting on them
   (`share.settings.integrations.retry`). Each is throttled; a throttled press
   says when the next one is allowed instead of failing. Each ends on a page
   that shows the outcome: the state moved, or "checked just now" with the
   sentence still naming what is left. "Qori checks again tomorrow" is never
   the only way forward. The throttle numbers are provisional in the tasks.
3. **The impact of changing something live is shown before it applies.**
   Replacing or removing a Series' folder or meeting, disconnecting a provider,
   and a reconnect that lands on a different account each show first how many
   Peers are affected and which Episodes will need attention, and say
   truthfully what Qori will do in the vendor account (take people it let in
   off the old folder) and what it leaves alone (the creator's files). A
   reconnect that returns a different account is held for the creator to
   confirm or cancel, not applied on return.
4. **Connection setup can be scanned.** Each tier shows its recommendation and
   at most three essential limitations above Connect; the rest sit in one
   disclosure in the same section, also above Connect. Essential means what
   Peers will need, what stops sharing outright on that tier, and the
   one-folder-per-Series rule. Specific guidance is repeated where it applies:
   the folder-sharing sentence when a folder is chosen, account requirements
   before a purchase.

**Why.** The review found a Dropbox Peer first learning that joining uses their
own storage at the Join step after paying; OneDrive's account requirements
written for the creator alone; `identities.prompt.before_paying` promising the
Series "ready the moment your payment goes through", which a pending grant or
an unjoined folder can break; a Peer who has joined waiting out
`RECHECK_MINUTES`, and a creator who fixed a video's privacy told Qori looks
again tomorrow; a folder replacement applied with no preview, and removal copy
saying nothing in the account changed while the sweep removes readers; and
every limitation listed above Connect as one wall. Advice-first stays; the
advice moves to where it can be acted on.

**Consequences.** `T-044` splits each tier's limits into essential and more,
and holds a different-account reconnect for confirmation; `T-091` adds Check
again, Try again now and the replacement and removal impact; `T-094` builds
`qori:episodes:check` and the per-Episode Check now, and `T-090`, `T-096`,
`T-098` and `T-100` now depend on it, because the drafts had `T-090` and
`T-094` each creating the same command; `T-092` renders the before-buying list; `T-094`, `T-096`
and `T-098` write their provider's lines and put folder changes behind the
impact dialog; `T-090`, `T-100` and `T-101` mark their essential limitations.

#### D-022 — Everything Qori writes for a vendor lives in that vendor's folder, and Qori's storage is CloudflareR2

**Decision.** Code that knows how a vendor works — its endpoints, headers,
auth, payload fields, status words, signature scheme and limits — lives in
`app/Integrations/<Vendor>`, for every kind of vendor Qori has code of its own
for: payments, mail, logging, queue, storage, video. There is no shared folder
for vendor code: `app/Integrations/Concerns` goes, and nothing vendor-specific
sits in `app/Support`, `app/Data`, `app/Concerns`, `app/Enums`, `app/Rules`, a
Service, a Model or a controller. One vendor's code uses another's by
importing it from that vendor's folder. `app/Integrations/Contracts` stays
shared, because a contract states what Qori needs and holds no vendor code.
Entry points stay where Laravel expects them and only hand the vendor's part
to its folder. `CLAUDE.md`, under "Where code lives", is the rule's one
statement.

The folder names the vendor service. The storage Qori itself provides runs on
Cloudflare R2, so its offering is `EpisodeProvider::CloudflareR2`
(`cloudflare_r2`, stored on every Episode that uses it) and its code is
`app/Integrations/CloudflareR2`. A storage offering on AWS S3 would be `AWSS3`
beside it. Both are Qori-hosted; a creator still reads "Qori storage".

**Why.** The owner, 17 September 2026: code from one vendor stays in one
folder, for mail, logging, Stripe, queue and anything else, and apart from
business logic there should be no common folder like `Concerns`.
`app/Integrations/Concerns` held one file, used only by Stripe. `Qori` named
Qori rather than the vendor behind it, so a second storage vendor would have
had no name.

**Consequences.** `T-111` renames the storage offering and migrates the
stored value; `T-112` moves Stripe's HTTP client into `app/Integrations/Stripe`
and deletes `Concerns`. Code written before the rule that still breaks it —
the `fromStripe()` factories in `app/Data`, `StripePeriod` and `Mailpit` in
`app/Support`, the Stripe and SNS webhook controllers verifying signatures
themselves, `BillingService` reading Stripe's raw subscription, the Stripe
purge command's own HTTP calls, the statement descriptor rule in `app/Rules`,
and `UploadService` importing a vendor class — is listed with a disposition in
`T-112`'s report rather than moved here. Drafts that plan a client in
`Integrations/Concerns` (`T-098`, `T-100`) or vendor parsing in `app/Data`
(`T-101`, `T-102`, `T-103`), or cite `qori_s3` and `QoriStorage`, follow the
rule when they are specified.

#### D-023 — Qori connects the Stripe account a creator brings, and never opens one

**Decision.** Payouts connect only through Stripe's OAuth: the owner is sent to
Stripe's own page, signs in to the account they have or opens one there, and
comes back with the account Qori stores. Qori no longer creates connected
accounts on Accounts v2, mints account links, or asks a country. In
`App\Integrations\Stripe\Connect` onboarding is three methods:
`beginOnboarding` builds the sign-in URL, `finaliseOnboarding` reads the
landing and exchanges the code, and `declineOnboarding` is what
`finaliseOnboarding` calls when the creator stopped partway. Accounts are
still read through v1. This supersedes `D-009` and amends `D-010`, which put
OAuth beside creation.

**Why.** The owner, 17 September 2026: opening a Stripe account is the
creator's concern, and Qori should only run the OAuth flow that lets them
choose. Stripe's page asks everything an account needs, including where the
creator is based, so Qori's page asks nothing.

**Consequences.**

- **OAuth is required to get paid at all.** Every environment needs Connect
  OAuth enabled in the Stripe dashboard, its redirect URI registered and
  `STRIPE_CLIENT_ID` set. Until then the page says payments cannot be
  connected, and the connect route refuses. The local `.env` has no client id
  on 17 September 2026, so no one can connect payouts locally until the owner
  adds it.
- **Accepted:** Stripe no longer recommends OAuth for new Connect platforms
  and points them at its hosted onboarding instead, and OAuth cannot connect
  an account another platform controls. If Stripe narrows OAuth further, Qori
  has no second way in.
- **Accounts Qori already created stay connected.** Qori can no longer mint a
  link to resume one; the Integrations page sends an unfinished account to the
  creator's Stripe dashboard. Whether deauthorising works on an account Qori
  created rather than one connected through OAuth is unverified.
- `T-113` removes the create door, the refresh and account-link return routes,
  `ConnectPayoutsRequest` and `qori.payments.countries`. The drafts `T-044`,
  `T-091`, `T-092`, `T-102` and `T-103` cite code that moves, and the sandbox
  walks in `T-102` and `T-103` now need an account connected through OAuth.

#### D-024 — An Episode is the lesson, and a Peer has one destination for it

**Decision.** An Episode holds its live session, its recordings, an ordered
list of materials and its homework. It stays the unit of progress and
certificates — `ProgressService::hasFinished()` counts Episodes and nothing
else — and a recording is never a second Episode. Nothing migrates: an
existing Episode's own `type`, `provider` and `content` remain its primary
item, and `materials` and `episode_recordings` are rows beside it; folding the
primary item into `materials` is a later task, once the storage providers
write there, and it keeps every Episode id. The Peer's destination stays the
Series page under `/shared`, which `D-020` fixed as the one place every state
has its sentence: each Episode row carries `id="episode-{id}"`, and a stable
address `GET /shared/{seriesId}/episodes/{episodeId}` (`shared.episodes.show`)
passes the same access gate as the Series page and answers 302 to that
anchor. Every email, calendar file and copied message is minted against
`shared.episodes.show`, so a page of its own can replace the redirect later
without breaking a link already sent. `is_preview` stays a label on the
primary item: the public page renders an Episode's title and time and never a
join link, a recording, a material or the chat card, and every new `/shared/*`
route requires an active Access.

**Why.** Both proposals of 17 September 2026 — the owner's research proposal
and Claude's independent plan — reached the lesson-as-Episode shape on their
own: five cards for one class is five certificate requirements and no link
from the recording to the class. They differed on the Peer's page. The owner's
wanted a lesson route; Claude's the Series page anchor. The merge takes the
address from the first and the page from the second, because `D-020` rejected
a second page precisely because it "would hold a second copy of every sentence
and need a return path of its own", and the owner's proposal itself asks that
a lesson page "not create a second competing provider-access workflow". A
migration now would re-scope `T-089`, `T-090` and `T-094` at once, since every
storage draft reads `episodes.content`.

**Consequences.** `T-100`'s `captureRecording()` (a recording as a new Video
Episode) and its `EpisodeType::Video` arm for Zoom go; `T-094` keeps its one
Drive file per Episode as the primary item and its picker also writes
`materials` rows; `T-101`'s once-per-Series Teams link and `T-091`'s
live-session containers are held until they fit a per-Episode join link
(`D-026`). `T-125` mints the route and the anchors; `T-130` and `T-126` add
the rows. Each new card is its own component under
`resources/js/components/series/`, so a page edit is a mount.

#### D-025 — A pasted link is the unconnected tier, standing in beside D-016 until each provider lands

**Decision.** A pasted `https` URL of at most 2048 characters is a supported
way to give a join link, a recording and a material, shown only to Peers with
access and never followed by Qori itself. It stands in beside `D-016`, not in
place of it: a row that holds a pasted URL is `provider = link` whatever host
the URL names — never `google_drive`, `dropbox` or `onedrive` with a bare URL
— and it becomes that provider's row only when picked through that
provider's connector (`T-094`, `T-096`, `T-098`), in place, with no re-adding.
A live Episode pasted from a Zoom link keeps `provider = zoom`, from Teams
`teams`, and from Meet or anything else the new `EpisodeProvider::Link`, whose
`connection()` is null. The creator is told to set the vendor's sharing to
"anyone with the link can view", that a Workspace administrator who has turned
outside sharing off makes the link fail for Peers and a PDF export uploaded
to Qori is the way round it (`D-018`), and the Peer's copy calls it a link the
creator manages. `T-044`'s drafted refusal in `EpisodeService::add()` is
narrowed: `guardProviderConnected()` applies only to a provider whose
`content` is an account-bound item id, never to a live Episode with a pasted
`join_url` nor to a `link` row; only automatic recording detection needs a
connection. `T-091`'s two open container questions are answered here: a
Series may hold one container per provider (its unique
`(group_id, series_id, provider)` stays), a container is dedicated to one
Series, and setup recommends one connected storage provider per Series and
does not enforce it, because each connected provider costs each Peer one more
vendor sign-in (`T-092`). `D-016`'s exception for vendor names in copy extends
to the chat platforms a creator chooses between (`D-029`) and to the meeting
vendor named on Join and Watch, where the person is about to leave for that
vendor; those names reach Vue as props from lang, never inline.

**Why.** The owner's proposal: external links "must be named as manually
managed links and agreed as temporary scope explicitly. They must not be
presented as finished Drive/OneDrive/Dropbox connectors or replace the owner's
per-Peer grant design. All seven providers remain in the beta plan." Claude's
proposal had the same build and called it an amendment; the record is a
stand-in because `D-016` is the owner's blueprint and `D-018` keeps every
provider in beta. A URL Qori does not interpret is not vendor code under
`D-022`. `T-044`'s refusal rested on nothing reading `join_url`, which Join
(`T-125`) makes false, and `D-018` says a tier is explained, never refused.
`StoreEpisodeRequest::content()` already stores `join_url`;
`EpisodeProvider::connection()` is an exhaustive `match`, so `Link` is one
arm.

**Consequences.** `T-044` is edited: the guard's exemption in its own words,
and the Teams bullet struck. `T-091`'s first two bullets are struck with
today's date. `T-123` adds `Link`; `T-130` creates `materials` with
`provider` from `EpisodeProvider`; the storage stream's order is unchanged —
Google Drive first, Zoom after `T-044`.

#### D-026 — A live Episode has an end and one start, its state is computed, and the copy states the schedule

**Decision.** `episodes.ends_at` joins `starts_at`: nullable in the schema,
backfilled `starts_at + 60 minutes` on existing live rows in the same
migration, required by the Form Request for `type = live`, entered as a
length in minutes (default 60, at most 12 hours), with a partial index on
live rows. `starts_at` becomes the column's alone: `content` no longer
carries a start. The live `content` keeps `join_url`, `records` (the
creator's "Recorded" or "Live only" switch, default true), `cancelled_at`,
`not_recorded_at` and `schedule_version` (bumped on every change to
`starts_at` or `ends_at`, and the calendar file's `SEQUENCE`), and reserves
`meeting_id` (written by the Zoom folder when a finder reads the link,
`T-142`) and `occurrence_id` (written only by the connected tier, `T-100`), so
an Episode created on the pasted tier can be mapped to an occurrence in
place. Editing may set a past start, so a class already held can take its
recording; creation keeps `after:now`. Every write to a live Episode's
`content` runs inside `DB::transaction()` with `lockForUpdate()` on the row
and re-reads `content` inside the lock. The state a card shows — `upcoming`,
`open`, `waiting`, `review` (creator only; a Peer sees `waiting`), `ready`,
`overdue`, `not_recorded`, `cancelled` — is computed by
`App\Services\LiveSessionService::stateFor(Episode $episode, CarbonImmutable $now): LiveState`
from the two columns, the clock, `content` and the Episode's recordings, and
is never stored. The clock decides which action is offered: Join from
`qori.live.join_opens_minutes` (15) before the start until
`join_closes_after_minutes` (15) after the scheduled end, a secondary "Still
in the session? Join again" for `join_grace_after_minutes` (120), then the
recording line; `recording_wait_hours` (48) turns `waiting` into `overdue`.
The copy states the schedule and never a fact Qori has not observed: no lang
line under `live.*` says "live now", "has ended", "on its way" or
"processing" this sprint; `open` reads as Join with the scheduled window,
`waiting` as scheduled to end at a time, and if it was recorded the recording
will be added here and an email will follow. A vendor signal, when webhooks
exist after Marketplace publication, may sharpen the copy and never changes
the state model. Every number is in `config('qori.live')` and interpolated,
never restated. Zoom's Series container and per-Peer registrants (`D-016`,
`T-100`) are unchanged and remain the connected tier; the pasted `join_url`
per Episode is the unconnected tier, and "Add the next session" copies an
Episode with its link seven days on.

**Why.** The owner's proposal: "a clock alone must not claim that the host is
live", "a scheduled end time is not evidence that the actual meeting ended",
say "processing" only with evidence, and "do not silently replace [the Series
container] with one meeting per lesson". Claude's proposal supplied the
states, the windows and the reason no event exists: there is no
`app/Integrations/Zoom`, webhooks cannot be relied on before publication, and
the card has to work for Teams, Meet and a pasted link too. The schema is the
same under both positions; the disagreement was copy, and copy is a lang
rule. `starts_at` is written twice today (`EpisodeService::add()` copies it
out of `$content['starts_at']`), and `UpdateEpisodeRequest` accepts only a
title and a preview flag, so fixing a link or moving a session means
delete-and-re-add, which loses the ids in `opened_episode_ids` and
`completed_episode_ids`.

**Consequences.** `T-123` adds the columns, the switch and the config block;
`T-124` the edit; `T-125` the state and the copy; `T-134` cancel and copy.
`T-100`'s draft is edited: it keeps `join_url`, keys its container on the
same `meeting_id`, and its picker-and-attach service is renamed so
`LiveSessionService` is this state's; `T-101`'s draft is edited so
`content['join_url']` is primary and `series_containers.url` optional;
`DesignReviewSeeder`'s live Episode takes a `join_url`.

#### D-027 — A recording is a row of its own, published on paste, held for review when Qori found it

**Decision.** Recordings live in `episode_recordings` (`HasUlids`,
`BelongsToGroup`): `group_id`, `episode_id` (cascade), `position`, `source`
(`RecordingSource`: `zoom`, `link`), `vendor_ref` (nullable; the vendor's
instance id), `url`, `passcode` (nullable), `started_at`, `duration_minutes`,
`available_until` (nullable date), `found_at`, `published_at` (nullable),
`hidden_at` (nullable), `needs_review` (boolean, default false); unique
`(episode_id, vendor_ref)` where `vendor_ref` is not null; index
`(group_id, episode_id, position)`. A link the creator pastes is published on
paste, because the creator's act is the review. A recording Qori finds lands
with `published_at` null unless the Series' `recording_publication`
(`RecordingPublication`: `review_first`, the default; `automatic`) says
otherwise, and it is held with `needs_review` whatever that setting says when
the match is ambiguous: two or more instances in the window, an instance
whose start is more than `qori.live.match_tolerance_minutes` (30) from
`starts_at`, a duration under `qori.live.min_recording_minutes` (5), or a
meeting id from a personal or vanity link. Only a completed video file is ever
a recording; a transcript or an audio-only file never is, and the stored link
is the share link when the vendor returns one, else the play link, never a
download token. The passcode is shown to every Peer with access, because that
is what the creator pasted it for; whether it rides in the URL is the spike's.
Peers see `ready` only when a recording is published and not hidden; hiding
keeps the row so a sweep never finds it twice; `available_until` is shown so
an auto-delete is never a surprise. Detection is a scheduled REST poll,
`qori:recordings:find`, with backoff for `recording_wait_hours` after the
scheduled end, matching on `occurrence_id` when stored and on the instance's
start within `[starts_at − 60 min, ends_at + 120 min]` otherwise, provisional
until `T-122`'s fixtures; webhooks come only after Marketplace publication
and only as a speed-up that clears the Episode's `recording_checked_at`,
because Qori's queue cannot retry a delivery it has accepted and the poll is
the reconciliation. Open makes no vendor call: Watch goes to the stored link,
and only Check now and the sweep re-read the vendor.

**Why.** Both proposals wanted the recording on the same card and the poll
rather than webhooks; the owner's added review-first, the hold for ambiguous
matches (Maven documents an early test recording replacing a future event's
Join), the completed-video rule and "do not store a temporary download token".
Claude's proposal put the list in jsonb under a row lock and named the table
as the fallback; the table is chosen now because a homogeneous list with its
own lifecycle, a uniqueness the sweep must not violate ("Uniqueness is a real
constraint now, not a hand-written index", `CLAUDE.md`) and a foreign key from
the notice ledger is a relational entity, and adding it after `T-126` is
frozen would be a re-scope of a done task. An email cannot be unsent, so the
review step belongs before the send.

**Consequences.** `T-126` creates the table and the paste; `T-127` hide,
another, not recorded and overdue; `T-142` to `T-144` the finder, the sweep,
review and Check now, with a migration adding `series.recording_publication`
and `episodes.recording_checked_at`. `T-100` loses
`SchedulesMeetings::recordings()`, `MeetingRecording` and
`Integrations/Concerns/ZoomHttpClient.php` (`D-022`) in favour of
`FindsRecordings`, `ZoomRecordings` and `ZoomClient`. `T-099`'s recording
step becomes `T-122`'s.

#### D-028 — Session notices are transactional, and the ledger is the outbox

**Decision.** `session_notices` (`HasUlids`, `BelongsToGroup`): `episode_id`
(cascade), `user_id` (cascade; a Peer, or the Group owner), `recording_id`
(nullable, null on delete), `kind` (`SessionNoticeKind`: `recording_ready`,
`day_before`, `session_cancelled`, `creator_recording_needed`), `publication`
(smallint, default 1), `status` (`RecipientStatus`, default `pending`),
`attempts` (smallint, default 0), `next_attempt_at` (nullable), `error`
(nullable text), `sent_at` (nullable); unique
`(episode_id, user_id, kind, publication)`; index
`(group_id, status, next_attempt_at)`. `qori:sessions:notify` inserts
`pending` rows inside a transaction, so two runs cannot both send, then sends
them inline, at most `qori.live.sends_per_run` (200) a run, and retries a
`failed` row when `next_attempt_at` is due up to `qori.live.notice_attempts`
(3) with backoff; after that the row stays `failed` for `T-019` to alert on,
and the creator's card reads how many were sent and how many failed from the
ledger. Confirmed delivery stays `T-032`'s. Recipients are worked out at send
time: active Accesses, filtered by
`SuppressionService::blockedForTransactional()` and nothing else — no consent
gate, no campaign metering, no unsubscribe footer; a per-Peer "no reminders"
preference does not exist and is not implied. `recording_ready` goes on every
plan when a recording is published, once per Episode per Peer, to Accesses
granted before that recording's `published_at` and only for a recording
published within `qori.live.notice_window_days` (7); later joiners see it on
the page, a later part or a replaced link sends nothing, and a deliberate
re-send bumps `publication` from a creator action (`T-140`).
`creator_recording_needed` goes to the Group owner at
`qori.live.creator_nudge_hours` (12, provisional) after the scheduled end
without detection, and at `recording_wait_hours` with it; never for a
cancelled or not-recorded session. Reminders follow
`communications-policy.md`: Free none, Start and above one fixed
`day_before`; Pro's several offsets and its own template wait for custom
templates, which `PLAN.md` defers, and no hour-before is built. A change to
`starts_at` or `ends_at` deletes the Episode's `day_before` rows so the
reminder fires for the new time, and no "moved" email goes; a cancellation
sends `session_cancelled` only to those who already hold a `day_before` row,
and Undo does not re-send. Every date in a notice is rendered in the
recipient's `users.timezone`, falling back to the Group's, with the zone named
and the Group's zone beside it when different — which answers `T-025`'s open
question: a Peer's dates follow their own zone. Every line that carries a noun
goes through `Terminology::line($key, $replace, $group)` with the Group passed
explicitly, because a sweep has no current Group. The commands iterate
`Group::query()->cursor()` inside `CurrentGroup::runFor()` and add no
`acrossAllGroups()` caller. The schedule interval is the owner's, chosen with
`T-091`'s against Laravel Cloud's sleep timeout; each run logs a heartbeat.

**Why.** The owner's proposal: "Add a durable worker or scheduled processor
... and an outbox for notifications, with retry state and deduplication ...
Reliability is part of this feature", "show creators send status", "dedupe by
learner, lesson, publication version", "start with one configurable pre-class
reminder and cancellation/reschedule handling". Claude's proposal supplied
the ledger, the unique key, the recipient window and the transactional basis.
`CLAUDE.md` forbids `ShouldQueue` before a worker exists and `deferred` cannot
retry, so the retry lives on the ledger, as `T-091`'s `vendor_grants` already
does; a per-Peer window keeps a late joiner from being mailed for every past
Episode on the first run. `communications-policy.md` already decided the
reminder tiers, and a fixed hour-before for Pro would amend it for a task
first on the slip list.

**Consequences.** `T-128` builds the ledger, `recording_ready` and the
command; `T-129` the creator nudge and the send status; `T-138` the reminders
and the cancellation; `T-140` the deliberate re-send. `T-025`'s Scope line
"Per-Peer timezones. Still not wanted" is superseded, and its owner rewrites
it; `T-005` still owns the rest of the access email's vocabulary. `T-018` is
told that deferred work from an artisan command does run after exit 0
(`FoundationServiceProvider.php:215-217`), which the 8 September 2026 entry
above got wrong.

#### D-029 — A chat invite is creator content

**Decision.** `series_chats` (`HasUlids`, `BelongsToGroup`): `series_id`
(cascade), `position`, `platform` (`ChatPlatform`: `whatsapp`, `wechat`,
`wecom`, `other`), `url` (nullable), `media_asset_id` (nullable, null on
delete; a QR image under `MediaAssetPurpose::ChatCode` and the live prefix
`chat-codes`), `expires_on` (nullable date), `note` (string 300, nullable);
exactly one of `url` or `media_asset_id`, and a removal drops the chat row
before its asset so a nulled asset never meets the check; `qori.chats.per_series` (1) rows
in v1, the column kept for later. Peers with access see a "Join the chat" card
on the Series page and nowhere else, dismiss it with "I've joined", and open
it through `shared.chats.open`, which redirects a link or serves the signed
image and logs the open. Emails point at the Series page's `#chat`, never at
the invite, so a replaced link strands nobody. After `expires_on` the card
hides the code and the creator is told to replace it. Qori calls no chat
vendor, reads no link host and has no `app/Integrations` folder for any of
them; removal from a chat is by hand, and the creator's Peer list shows who
opened the card. Platform names in the picker and on the card extend
`D-016`'s vendor-name exception and reach Vue as props from
`lang/en/chats.php`.

**Why.** Both proposals: the invite belongs on the Series, behind access, with
a copyable announcement and no automatic messaging. Neither WhatsApp nor
WeChat offers an API that can manage a creator's existing group. The owner's
course uses those two; nine platforms with identical behaviour is vocabulary
without code, and `CLAUDE.md` keeps enums small. WeChat group codes last seven
days, which is why the expiry exists.

**Consequences.** `T-132`. `SeriesService::purge()` deletes the rows and
their images itself, because it keeps the Series row and nothing cascades.

#### D-030 — Materials: a list on the Episode, labelled and released, capped by config

**Decision.** `materials` (`HasUlids`, `BelongsToGroup`): `series_id`
(cascade), `episode_id` (nullable, cascade; null is Series-level, kept in the
schema now and reached by `T-137` later), `position`, `role` (`MaterialRole`:
`preparation`, `material`, `homework`), `provider` (`EpisodeProvider`;
`cloudflare_r2` or `link` this sprint), `title` (200), `note` (text, at most
`qori.limits.text.material_note` = 2000, shared with the textarea), `content`
(jsonb, `'array'` cast, string default `'[]'`; `{url}` for a link, `{}` for
Qori storage, a provider's item keys later), `media_asset_id` (nullable, null
on delete; required for `cloudflare_r2`), `release` (`MaterialRelease`:
`with_episode`, `after_session`; the second only on a live Episode), `due_at`
(nullable; homework, entered in the Group's zone and converted in the Form
Request); index `(group_id, series_id, episode_id, position)`; one check constraint says
the content matches the provider — a `link` row carries a `url`, a
`cloudflare_r2` row carries a `media_asset_id`, and a `homework` row may carry
neither, because a brief and a due date are a homework on their own.
`media_asset_id` is unique, since removing a material deletes its object.
`qori.materials.per_episode` and `per_series` are 30, provisional, a sanity
cap on every plan and not a tier lever, and the error interpolates `:count`
and carries a resolution. Release governs what Qori lists and when it signs a
Qori-hosted file's URL — "Shown after the session", never "available after" —
and is no embargo on a vendor's file, which a Peer inside a granted folder can
browse to. Qori's per-file caps are unchanged; the 100 MB per-Series total
the owner set on 6 September 2026 is `T-139`, once the Free figure is set, and
until then the copy says the per-file limit and never "unlimited". Adding
`odt`, `ods`, `odp` and `epub` is the owner's call: if taken, both
`config('qori.storage.allowed_uploads')` and
`MediaLifetime::DOCUMENT_EXTENSIONS` change in one commit and `zip` stays out
because it would let video in. Homework is a `homework` row with a brief, a due
date shown in the Peer's zone and at most one link — a template, or the
hand-in destination the brief names; it has no submissions, marks or ticks,
a self-reported "I submitted this" is a later Peer-scoped row and never a
claim that anything arrived, and it never gates the certificate. A
Qori-hosted material is reached through `SignsStoredFiles::temporaryLink()`
on `CloudflareR2Storage` with a lifetime from the extension.
`EpisodeService::remove()` and `SeriesService::purge()` delete the
Qori-storage objects of the materials they drop, by `media_assets.key`,
because purge keeps the Series row and nothing cascades.

**Why.** The owner's proposal: 30 items, configurable, tested with a creator
who has 15 to 30 files; labels "preparation, lesson material or homework";
release "governs what Qori lists, not an embargo on the vendor's files"; keep
the per-file caps; homework with an external destination. Claude's proposal
supplied the table, the release gate, the signing contract and the purge
obligation. `media_assets` has no link to any Episode today, so
`materials.media_asset_id` is the first way an upload is addressable for
deletion and totals.

**Consequences.** `T-130` and `T-131`; `T-137` for Series-level rows and
reorder; `T-139` for the total. `T-094` writes picked Drive items into the
same rows with `provider = google_drive`, and `T-091`'s `checkItem()` and the
replacement impact grow a materials branch so a replaced folder flags picked
materials too.

#### D-031 — The sprint is the manual-replay checkpoint, in a classroom stream

**Decision.** The checkpoint the owner named is the sprint: `T-122` to `T-133`
in the order the `classroom` stream lists them, so that a Peer in another
timezone can miss a class, receive one email, open the same link and find the
recording, the materials and the homework — with the recording pasted by the
creator. Automatic detection (`T-141` to `T-144`) is the sprint after, on
`T-044`'s contract, with `T-122`'s fixtures committed now, and the storage
stream's order is unchanged: Google Drive before Zoom. `T-134` to `T-140`
follow in that order and none is promised. A `classroom` stream (owner wayne)
holds the work and blocks beta: a live Episode is a dead end for a Peer
today, and `D-018` put the meeting vendors in the release. `T-043` is not a
prerequisite — the public link and the code sign-in are how a new attendee
gets in — and `T-032` comes before `recording_ready` reaches a real Peer.
`T-145` is the beta-gate evidence. `PLAN.md`'s execution rule 5 and its
settled "broad Zoom/Teams work" line move with `D-018` and this record.

**Why.** Both proposals reached the cut on their own: the owner's ("It would
be misleading to promise this entire production flow in one ordinary sprint
... a narrower pilot checkpoint: lesson page, multiple resources, verified
live join, creator-published replay and durable email") and Claude's option
(b). `T-100` depends on four unowned drafts and `T-044` is `L` with Google
first; a chain like that does not land in two weeks, and the beta
authorization URL for a Zoom app lasts twelve weeks at most, so the
Marketplace submission is prepared this sprint. Twelve tasks on two
developers with two Vue pages serialising most of them is honest, not
comfortable.

**Consequences.** The stream file carries the lanes, the claim order and the
slip order. Day one is the owner's: a month of Zoom Workplace Pro and the
development app (`T-122` waits on them), `T-089`'s three open questions, the
schedule interval. The two proposals are folded into
`docs/planning/course-classroom.md` and removed.

### 19 September 2026

#### D-032 — A flow's steps are begin, processing and finalise; fulfil is what a customer is owed

**Decision.** A flow that leaves Qori and comes back names its first step
`beginX()` and its last `finaliseX()`, and each step between them, when there
is more than one, `processingX()`. The URL, the route name and the controller
of a step carry the same word, so the landing a vendor sends a person back to
is `…/finalise`, `….finalise` and `…FinaliseController`. `fulfilX()` is kept
for delivering what a customer is owed — the access a payment bought, the
email or notification that says so — and finishing Qori's own logic and data
is `finaliseX()`. No step is named `return`, `callback`, `complete` or
`start`, and a remembered place to go afterwards is a destination, as
`SignInDestination` already is. The rule is in `CLAUDE.md` under Style.

**Why.** The owner, reviewing the Google Drive chain: "return is awful
naming". The Stripe refactor the owner started (`T-113`) already reads this way —
`SellsSeries::beginOnboarding()` and `finaliseOnboarding()` — while its
landing kept `PayoutsReturnController` and `u/payouts/stripe/return`, and the
connection and identity drafts copied the landing's name rather than the
contract's.

**Consequences.** The drafts `T-044`, `T-092`, `T-096`, `T-098` and `T-141` are
renamed in place: `connections.oauth.finalise` at
`u/connections/{provider}/finalise`, `ConnectionFinaliseController`,
`ConnectionsDestination`, `ConnectionService::beginConnection()` and
`finaliseConnection()`, and `identities.finalise` at
`u/identities/{provider}/finalise`. `T-146` renames the code that predates the
rule, starting with the Stripe landing, whose redirect URI the owner
re-registers at Stripe. Finished tasks and their reports keep the old names,
because they are records.

#### D-033 — URLs are hyphenated words, a flow's URLs say begin and finalise, and a vendor's landing names the vendor

**Decision.** A URL's path is lowercase words joined by hyphens, with no
underscores and no abbreviated words beyond the one-letter namespaces `g/`,
`u/` and `s/`; query keys are form fields and are not covered. A value stored with an underscore reaches a URL through
its enum's `slug()`: `ConnectionProvider::GoogleDrive` is stored as
`google_drive` and is addressed as `google-drive`, and `{provider}` is bound
back from the slug, so the stored value, the lang keys and the config keys
keep their underscores. The URL a vendor sends a person back to names the
vendor, never the service: `u/{flow}/{vendor}/finalise`. That gives
`u/payouts/stripe/finalise`, `u/connections/google/finalise` for Google Drive
and YouTube alike, `u/connections/microsoft/finalise` for OneDrive, and
`u/identities/google/finalise`. The service being connected and its tier
travel in the session state the begin step wrote, as they already did. The
Connect button is that begin step, and its URL, route name and action say so
as the landing's say `finalise`: `g/{group}/connections/{provider}/begin`,
`share.connections.begin`, `ConnectionsController::begin()`; Stripe's is
`g/{group}/payouts/stripe/begin`, `share.payouts.begin`,
`PayoutsController::begin()`; a Peer's identity begins at
`u/identities/{vendor}/begin`.

**Why.** The owner, on the Google Drive setup:
"/u/connections/google_drive/finalise is not good url naming convention. do
short form /u/connections/gd/finalise or hyphen
/u/connections/google-drive/finalise", and then "and also
/u/identities/google/finalise. Why the url is not consistent?" The hyphen,
not the short form: `gd` reads as nothing to a person, and the next short
form collides (`db` for Dropbox, or the database). The inconsistency was
real. Connections are keyed by service, because a creator connects Google
Drive and YouTube separately, each with its own tier and scopes. Identities
are keyed by account, because a Peer's one Google account opens anything
Google shares with it. Each landing copied its own key into its URL. A
landing is registered per vendor in that vendor's console, so naming it by
vendor gives one rule for every landing and one fewer Google redirect URI.
Then, on the Connect button: "Connect button use begin and finalise also."

**Consequences.** `T-044` gives `ConnectionProvider` `slug()`, `fromSlug()`
and `vendor()`, binds `{provider}` from the slug, and moves its landing to
`u/connections/{vendor}/finalise`. `{provider}` is reserved for that slug:
`T-092`'s routes name their parameter `{vendor}` and `T-090`'s
`{episodeProvider}`, so the binding never meets an `IdentityProvider` or an
`EpisodeProvider`. `T-098`'s landing becomes
`u/connections/microsoft/finalise`. `T-044`'s Connect route becomes
`share.connections.begin`, `T-092`'s begin URL gains `/begin`, and `T-146`
renames Stripe's `share.payouts.oauth` with its landing. YouTube needs no
redirect URI of its own. `vendor-accounts.md` gives the owner the new
addresses.

#### D-034 — A vendor's client sets its timeout, and a caller inside a person's request may only shorten it

**Decision.** Each vendor's client in `app/Integrations/<Vendor>` sets its own
timeout and retry on its `Http::` chain, as `CLAUDE.md` says. A contract method
that a Service calls while a person waits takes `int $timeoutSeconds` as a
budget, and the client uses whichever is shorter, its own limit or the budget;
the sweeps pass their longer budget. The two landings that exchange a code at
Google wait the same: `ConnectionService::REQUEST_TIMEOUT_SECONDS` (10) for a
creator's connect (`T-044`) and `VendorIdentityService::REQUEST_TIMEOUT_SECONDS`
(10) for a Peer's sign-in (`T-092`), while a grant made inline keeps
`VendorAccessService::REQUEST_TIMEOUT_SECONDS` (5) (`T-091`). All three numbers
stay provisional until `T-093` records how long each call takes.

**Why.** The readiness audit of 19 September 2026 found `T-044` bounding
Google's token exchange at 10 seconds and `T-092` bounding the same call at 5,
and every storage contract taking its timeout from a Service while
`CLAUDE.md` gives it to the vendor's client. Both were right about different
things: how long a vendor may take is the vendor's limit, and how long a
person may be kept waiting is Qori's.

**Consequences.** `CLAUDE.md` says so beside the vendor-folder rule. `T-092`
declares its own constant for the exchange; the contracts in `T-044`, `T-091`,
`T-092`, `T-094`, `T-096`, `T-098` and `T-141` describe `$timeoutSeconds` as a
budget the client may only shorten.

#### D-035 — A vendor is named in public copy only with the owner's confirmation, and Stripe is confirmed

**Decision.** Public copy names no vendor, as `CLAUDE.md` says, unless the
owner confirms that one vendor by name. Stripe is confirmed: Qori releases
with Stripe as its only payment gateway, so the creator's copy says "Connect
Stripe" rather than "Connect payments" or "Connect payouts". Each further
vendor needs its own confirmation.

**Why.** The owner, 19 September 2026: whether to name a vendor depends on how
a person reads the line, weighed against when Qori should keep its
implementation hidden, for security and to protect its tech stack. Where the
person has to act at the vendor (signing in to Stripe, opening their Stripe
dashboard), the name is what makes the line clear. Where the vendor is only
how Qori works inside, naming it tells a reader nothing useful and tells
everyone how Qori is built.

**Consequences.** `CLAUDE.md` carries the exception beside the no-vendor-names
rule, with the confirmed list. `lang/en/series.php`'s two price lines say
Stripe (`acefed7`), as `lang/en/payments.php` already did. A worker who wants
another vendor's name in copy asks the owner first. It is not a wording fix.

### 20 September 2026

#### D-036 — Google Drive grants per file, and a Series has no Drive folder

**Decision.** On Google Drive, Qori grants each Peer a reader permission on
each Episode's file, one grant per Peer per file, and a Series has no Google
Drive container. The creator picks a file from anywhere in their Drive; Qori
never asks for a folder, never shares one, and never requires an Episode's
file to sit in a particular place. `D-016`'s container grant and `D-025`'s
one-container-per-provider rule no longer describe Google Drive. Whether they
still describe Dropbox and OneDrive is for `T-095` and `T-097` to find out,
and neither spike's design is changed by this.

**Why.** `T-093` (`reports/T-093-2026-09-20-wayne.md`) found that the narrow
permission Qori asks for, `drive.file`, refuses every sharing change on a
folder while any item beneath it has not been picked in Qori — a new Peer, a
repeat grant and a removal alike, with the same 403 `appNotAuthorizedToChild`.
One file the creator drops into the folder through Drive, one file left in the
trash, one shortcut, or one file inside a subfolder under Limit access is
enough. A folder design would therefore need the creator to pick every item
beneath the folder before each sale and each removal, and Qori cannot even
read the blocking item's name to ask for it: the token gets a 404 on anything
unpicked, and the refusal carries only an id. The owner, 20 September 2026,
after the report: "go with per-file grants".

**Consequences.** `T-094` is re-drafted on per-file grants: an Episode is one
picked Drive file, a grant is a reader permission on that file, the folder
panel and its picker, the container states, `series.container.*` and the
container capacity guard all go, and Google's documented cap of 600 addresses
for one file is the real number rather than an unmeasured figure for a folder.
`T-091` keeps its container model for whichever provider still needs it and
gains grants on an item, which its own Decisions anticipated as a change to
its Database section. Two things `D-016` promised go with the folder: a file
the creator adds in Drive no longer reaches Peers by itself, and a new Episode
needs one grant per Peer, so the fan-out is bounded per request and finished
by `T-091`'s sweep. Two things arrive with it: nothing the creator does in
their own Drive can block a sale, and a file moved anywhere in that Drive
keeps working, because the permission is on the file.

#### D-037 — Every action says whose storage it touches

**Decision.** Wherever a creator acts on a file that lives in connected
storage, Qori says which side of the line the action falls on before it
happens. Every such action is one of three shapes, and the words name the
shape: it **writes a file to your storage** (uploading, and creating the
folder Qori uploads into), it **changes who can open a file in your storage**
and never the file itself (letting a Peer in, taking one off), or it
**changes nothing outside Qori** (naming an Episode, reordering, editing what
Qori holds about it). The line goes beside the action, not in help, and the
rule binds every BYO integration: `T-094` Google Drive, `T-096` Dropbox,
`T-098` OneDrive, `T-090` YouTube and `T-149`'s dialog above them.

**Why.** The owner, 20 September 2026: "always prompt the creator, does this
action interact directly with your storage or just qori i think it is good
interaction." A creator's Drive holds everything else they own, and BYO's
premise (`D-016`) is that those files stay theirs — a promise only legible if
each action says which side it is on. The distinction is not academic:
`T-093` showed Qori's grants are real Google permissions the creator can see
in Drive's own sharing dialog, and an upload would be a real file against
their quota, while an Episode's name and order never leave Qori. Under
per-file grants (`D-036`) the creator is also the only person who can repair
a file Qori cannot reach, and they can only do that with an accurate model of
what Qori does and does not touch.

**Consequences.** `CLAUDE.md` carries the rule beside the copy rules, as
`D-035` carries its exception. Each vendor task writes the line for each of
its actions as lang copy, never inline, and `T-149` writes the dialog's,
where a creator first meets the distinction. An action nobody can classify
into one of the three shapes is a sign the action is doing two things.

#### D-038 — Qori never deletes a creator's file

**Decision.** No Qori action removes a file from a creator's connected
storage: never deleted, never put in the bin, never moved out of where they
keep it. What Qori removes is only what Qori added — the permissions it
created or adopted. This holds even for a file Qori uploaded itself: if the
Episode is then abandoned, the file stays where it was put and Qori says so
rather than tidying up after itself.

**Why.** The owner, 20 September 2026: "don't delete creator files." The
capability exists — `drive.file` lets an app delete or trash any file it
created or the creator picked — so the refusal has to be written down rather
than assumed. The asymmetry decides it: a wrong grant is one
`permissions.delete` from repaired, while a wrong delete may take the only
copy of something Qori never had. `T-094`'s copy already promises "Your files
are left as they are", and that promise is what makes connecting a Drive
holding everything else they own a reasonable thing to do.

**Consequences.** `T-149`'s uploader offers no remove-from-storage, and its
undo removes the Episode alone. Removing an Episode, replacing its file and
disconnecting a provider all revoke permissions and leave every file. No call
in `app/Integrations/*` deletes or trashes a vendor file — `files.delete` and
`trashed: true` on Drive, and each other vendor's equivalent, never appear,
which is narrow enough for `ArchitectureTest` to assert once a vendor folder
exists to assert it against.

#### D-039 — Disconnecting a provider leaves every permission standing

**Decision.** Disconnect drops the tokens and revokes nothing, exactly as
`T-044` specifies: every permission Qori added at the vendor stays, an
Episode keeps pointing at its file, and what stops is Qori's ability to act.
`D-038`'s consequence line named disconnecting a provider among the paths
that revoke permissions; that one clause is wrong and is corrected here, and
the rest of `D-038` stands. The owner, 20 September 2026, on the storage
review's proposal that Qori keep the creator's authority for a bounded
cleanup period after disconnect: "disconnect is enough follow T-044. light
touches."

**Why.** The review is right about the cost. `T-093` watched a Peer keep
their access after the creator removed Qori from their Google account, and a
refund after a disconnect has nothing left to revoke with. But the cure is
worse: holding a creator's encrypted refresh token after they have asked Qori
to let go of their account is the opposite of what the person pressing
Disconnect believes they are doing, and it is precisely the retention a
creator would be angry to discover. Disconnect is someone saying stop, and
Qori stops. The creator keeps two ways to finish the job — reconnect the same
account and remove the Peers, or remove them in the vendor's own sharing
dialog, where every permission Qori made is already visible to them.

**Consequences.** `T-044` is unchanged, and its disconnect bullet is settled
rather than open. The impact dialog `D-021` put in front of disconnect says
plainly that the people already let in keep their access until the creator
reconnects or removes them at the vendor: that sentence is the whole of what
this decision costs a creator, so it is not optional and not a disclosure in
a disclosure. A refund, a removal or an Episode deletion that happens while
no connection exists leaves its rows unrevoked; `T-091` and `T-103` record
them as unresolved and say so, rather than retrying for ever or reporting a
cleanup that never happened. `T-091`'s durable revocation intent, which the
review asks for under `F01`, is still needed for every other path — it simply
has no authority to spend once the connection has gone.

#### D-040 — A grant is made when a Peer opens the file, and nothing sweeps

**Decision.** Qori makes a vendor grant at the moment a Peer presses Open on
an Episode, for that one item, inside their request, and at no other time.
There is no scheduled reconciliation: `qori:access:reconcile` and its
five-minute schedule are not built. Nothing is granted ahead of use — a
purchase writes the Access and makes no vendor call, and the Series page
offers Open on every Episode the Peer has paid for whether or not a
permission exists yet. A grant that fails is retried by the person pressing
Open again. **Revocation keeps its inline attempt at refund and removal**,
once, and a revoke that fails is not retried by Qori: the row is recorded
unresolved and listed for the creator on the Integrations page — who could
not be removed, from which file — with a Try again they press themselves.
The owner, 20 September 2026: "I would rather do a per file sweep when the
user open it. I do accept there is always going to be gap in the system,
user would need to retry. I would suspend the proposal to make grant 100% in
favor of simple one way flow for the release."

**Why.** **A grant nobody uses is work nobody needed.** Granting at purchase
means one call per Peer per Episode whether or not it is ever opened, and the
storage review costed a Series of twenty Episodes and three hundred Peers at
twelve thousand calls and 220 to 328 minutes. On demand, Qori makes exactly
the grants people use, at the moment they use them, and the fan-out has
nothing left to solve. **The machinery that made the eager path safe was most
of the foundation's complexity**: an inline limit, pending rows carrying
attempt counts and next-attempt times, a fair bounded scheduler with a
checkpoint and an overlap guard, and an unsettled argument about whether Qori
needs a queue worker at all. None of it is needed when the work happens
because somebody asked for it. **And it is one way in**: a Peer who cannot
open presses Open again, with no second mechanism to understand and no
background progress for a page to report.

The costs are accepted, not hidden. The Peer waits two to three seconds at
the click, once per Episode. A vendor refusal reaches them directly. And a
gap is possible by design — the owner's words — so the states that name a
person still stop the journey, because a Peer pressing Open against a
creator's dead connection is the one case where retrying is not the answer.

**Consequences.** `T-091` and `T-094` are re-drafted on this, and it is a
larger change than `D-036` was. The sweep, its command, its schedule, its
timeouts and its tests go, and with them `INLINE_GRANT_LIMIT`, the retry
timing on a `pending` row and the fan-out bound `D-036` needed. **Open on a
not-yet-granted item becomes required**, which reverses the note struck in
`T-091` earlier the same day: the argument for declining it was that the
sweep would arrive within minutes, and there is no sweep now. `D-016`'s
blueprint moves its third step from the moment a Peer gets access to the
moment they open an item; steps one, two, four and five stand. The review's
`F07` dissolves with the scheduler, `F08`'s request deadline matters more
because Open now calls a vendor inside a person's request, and `F01`'s
durable revocation intent survives all of it: the unresolved list is exactly
a record that has to outlive the Episode it points at. What this decision
does not settle is whether `T-094`'s daily `qori:episodes:check` goes the
same way; it checks for a file that moved rather than a grant that is
missing, and it is asked separately.

#### D-041 — A vendor permission belongs to its last entitlement, not to one grant row

**Decision.** Where more than one Qori grant would sit over the same physical
vendor permission, the permission is keyed by **(connected account, target,
principal)** — whose account it was created with, which file or container it
sits on, and which person it was granted to — and Qori revokes it only when
the **last** entitlement over it ends. The bookkeeping row stays one per
`(group_id, access_id, episode_id)`, which is Qori's own; the physical
permission is a different thing with a different key, and the two are not the
same count. Every read and write of that key happens under the same advisory
lock as the grant it belongs to. The owner, 20 September 2026, choosing it
over the two alternatives below.

**Why.** The storage review's `F02` showed three ordinary situations that
produce two Qori grants over one vendor permission: the same file used by two
Series, two Episodes pointing at one file, and two Qori people who confirmed
the same Google account. In each, revoking either grant takes away access the
other one still entitles — and under `D-040` the person who discovers it is a
Peer pressing Open on something they paid for, which is exactly the failure
the foundation exists to prevent.

The alternatives were weighed and refused. **Restricting reuse** — refusing
the second grant until the invariant holds — is far simpler to specify and
refuses things creators legitimately do; one file serving two Series is
normal, not an edge case, and a product that forbids it to keep its
bookkeeping tidy has chosen the wrong side. **Owning the permission per
Series and accepting the collision** is cheapest of all and means a Peer can
silently lose a file they paid for, with nothing in Qori able to explain it.
The cost of the decision taken is a reference count and a revoke path that
has to ask a question before it acts; that cost is paid once, in the
foundation, by the task best placed to pay it.

**Consequences.** `T-091` carries it: the index
`(group_id, provider, external_target_id, principal)` is already in its
Database section for exactly this lookup, and its revoke step becomes "is
this the last entitlement over this permission" rather than "is this row
revokable". `principal` must therefore be written at the attempt and never
overwritten (`F04`), because a permission Qori cannot name the principal of
is one it can neither find nor count. `T-092` inherits the sharpest case: two
Qori people confirming the same vendor identity are two Accesses and one
principal, so its identity confirmation has to expect an existing permission
rather than treat one as an error. `T-094`, `T-096` and `T-098` cite this
rather than each deciding it, and a provider whose vendor de-duplicates
permissions on its own side says so in its own task instead of assuming this
one does the work. What this does not settle is what a **shared** permission
should say to a creator reading the unresolved-removals list, where one row
may be held open by an entitlement in a Series they are not looking at.

#### D-042 — A vendor integration is developed on free tiers, or it is re-approached

**Decision.** Every vendor integration is spiked and built against **free
accounts and free developer programs**. Paid provisioning is not planned for
and not budgeted; it is a last resort, taken only once a free path has been
looked for and shown not to exist. Where an integration cannot be developed
without one, the work stops and goes back to the owner, **who re-approaches
it or drops it** — dropping is now a real outcome, which amends `D-018`'s
"all seven providers ship before beta". The owner, 21 September 2026: "Plan
for free in development until it can't be done then will re-approach or drop
the integration."

**Why.** Seven providers, each wanting accounts across several tiers, is a
standing subscription bill for software nobody has yet decided to keep. The
two spikes that prompted this asked between them for a Dropbox Plus account,
a Dropbox teams trial and a paid Microsoft work tenant, and neither had been
run — so the money would have been spent to find out whether the integration
was worth the money. Buying an account to discover whether an integration is
viable is the wrong order, and it is the order that quietly converts an
open question into a sunk cost somebody then defends.

**The distinction this turns on, and it is easy to lose.** There are two
different plan questions and they have different answers. _Whose plan pays
for development_ is this record: Qori's, and the answer is nothing. _Which
creator tier the shipped integration supports_ is `D-018`, unchanged — every
tier a creator can bring is offered, its limits stated on screen, and none
refused. This record does not narrow what Qori offers a creator. It narrows
what Qori will spend to find out, and accepts the consequence: an integration
whose working path cannot be observed for free is an integration Qori cannot
specify from an observed payload, and `PROCESS.md` will not let it be `ready`
on a guess. That is the route by which a paid-only vendor gets dropped — not
a judgement about its customers.

**The order of work follows from it.** A spike answers "does the free path
work" **first**, in the smallest number of calls that can answer it, before
any other fixture is gathered and before any account is bought. Where the
answer is no, the spike stops there and reports; the remaining questions are
not worth answering about a path Qori may not build.

**Consequences.** `T-095` and `T-097` carry it directly and each gains a
cheap first step. Two free paths were found on 21 September 2026 and are
recorded in those tasks: Microsoft's **365 Developer Program E5 sandbox**
(25 licences, 90 days, renewing on real development activity), which removes
`T-097`'s paid work tenant entirely; and Dropbox's **free Business
Development Account**, granted by request, which covers `T-095`'s team
scenarios. What neither covers is a Dropbox Pro or Plus creator, and that is
the open one: Dropbox's own API spec says adding a read-only member "can only
be performed by users that have upgraded to a Pro or Business plan" while
Dropbox Help says every account can set "can view". `T-095`'s first step is
now the single call that settles it. `T-096` and `T-098` inherit whatever it
answers. Every later vendor task cites this record rather than re-deciding
it, and a task that finds no free path says so under **Blocked on** and
stops, rather than asking for a card.

**Corrected the same day, and the correction is the more useful half.** The
paragraph above says Microsoft's E5 developer sandbox "removes `T-097`'s paid
work tenant entirely". It does not, and the claim was made from a search
summary rather than the source. The developer program's
[FAQ](https://learn.microsoft.com/en-us/office/developer-program/microsoft-365-developer-program-faq)
lists exactly three qualifying paths — an eligible Visual Studio Professional
or Enterprise _standard_ subscription, the ISV Success Program or an eligible
MAICPP tier, or a Premier or Unified Support contract — and there is no open
signup at any price; an existing Microsoft 365 enterprise subscription does
not qualify an account either. Setup also requires a Microsoft Customer
Agreement billing account with an active Azure subscription linked, which
cannot be bypassed.

What actually satisfies this record for both vendors is the same instrument:
**a vendor's own free trial, cancelled before it bills.** Dropbox offers 30
days on Plus and Professional; Microsoft offers a month on Microsoft 365
Business, which is a real work tenant with a Global Administrator. Both give
full access to the paid behaviour, which is what `PROCESS.md`'s evidence rule
needs, and both cost nothing if cancelled. So the rule this record sets down
for every later vendor task is: **look for the free tier, then the free
developer programme, then the vendor's own trial with its cancellation
diarised the hour it starts** — and only then bring it back to the owner. An
uncancelled trial is the purchase this record forbids, arriving by
inattention, so the diary entry is part of the instrument and not an
afterthought.

The wider lesson is cheaper to learn here than in a task: **a free developer
programme is gated on a relationship, and a trial is gated on nothing.** The
programme is worth more when it is open — ninety renewable days against
thirty — so it is asked for first; but a plan built on one before eligibility
is checked is a plan resting on a fact nobody verified, which is how this
record came to state one.

### 21 September 2026

#### D-043 — Nobody approves a task: whoever picks it up brings it to ready, and asks for what is missing

**Decision.** Streams have no owner and tasks have no approver. A developer
picks up a stream or a task, takes a draft to `ready` themselves, and builds
it. What only the product owner can supply — a product call, an account, a
real sign-in, a change to something recorded as settled — is **asked**,
written into the task as asked, and worked around meanwhile; it is not a gate.
A `ready` spec found wrong is rewritten by whoever found it, with the finding
logged, rather than stopped for planning to rewrite. **Release checklist items
— privacy policy, terms, refund wording, support ownership, production
configuration, pricing, a vendor's app review — sit on `PLAN.md`'s release
gate and never hold a task.** The owner, 21 September 2026: "The developer
need to be able to just pickup a stream, a task to work on. It should be able
to change from draft to ready. If there are missing information or
prerequisite just ask." And earlier the same day: "How can a privacy or terms
and condition stopping a stream to go into development. Those honestly would
be just pure checklist prerelease."

**Why.** Every stream named an owner, and all twelve named the same person, so
every draft-to-ready approval, every `blocked` clearance and every rescope
rewrite queued on one desk. On the morning of this record the board stood at
77 done, 8 ready and 69 draft, with drafts carrying up to 39 open questions
each (`T-091`), and some of those questions were legal and policy ones no line
of code depends on: `T-044` handed "the privacy-and-terms disclosure before
Connect" to the stream owner, and `T-101` held a paid Teams Series "until the
terms are read". Specification had become the bottleneck rather than building.
The approval step bought review, and its price was that nothing moved while the
one reviewer was elsewhere.

**What is kept, because it is the record and not the gate.** The Re-scope log
is still required — a spec changed halfway through with no log is one nobody
can review — and only the stop-and-wait is gone. Decisions still get ids and
reasons. Every "Found, not fixed" bullet still ends in a disposition. The
board's collision and dependency rules still fail the gate, because they
protect two developers from each other, not from a missing signature. How much
a ready spec must name now follows from who builds it: literal names when it is
written for somebody else, less when the writer is the builder.

**Consequences.** `PROCESS.md`'s "The stream owner" section is replaced by
"Who does what" and "Release checklist is not a prerequisite". `owner:` leaves
every stream file's front matter, `bin/tasks --check` no longer requires it,
and the board prints who is on each stream from the tasks in `doing`.
`PLAN.md` is updated by whoever's work moves release state, in the closing
commit; its intent and **Settled** list still change only through a decision
here. Rule 0 of the code repository's `CLAUDE.md` changes to match. `T-089`,
recorded in the classroom stream as waiting "only on the stream owner's
approval", waits on nothing. The existing drafts are not rewritten in a sweep:
each keeps its **Before this can be ready** list, and whoever picks one up
works through it under these rules — moving a legal or policy bullet onto the
release gate where that is all it was.

#### D-044 — Certificates are suspended, not removed, until they are reworked

**Decision.** Certificates and the hours log are switched off behind one flag,
`config('qori.certificates.enabled')` (`QORI_CERTIFICATES`), off by default.
Every surface is hidden or answers 404 — the public check page, the Peer's
record and its nav item, the certificate link on a finished Series, and the
creator's Hours field — and **minting is unchanged**: a finished Access still
gets its code. `T-109` is where they come back. The owner, 21 September 2026:
"suspend certificate feature first, the current implementation does not work.
I do not want to spend effort right now to correct it. Shall pick it up in the
future."

**Why this shape.** Deleting the code would make the rework rebuild what exists;
leaving it visible shows Peers something the owner says does not work. A flag
keeps the code under test — the existing certificate tests switch it on — and
keeps the data growing, so a Peer who finishes during the suspension has a
valid code on the day it returns. The routes answer 404 rather than an error
because an error that names a feature nobody can see is worse than a page that
is not there.

**Consequences.** `T-158` builds it. What exactly fails was not recorded — the
owner did not want to spend the time — and `T-109` carries that as its first
question. `PLAN.md`'s settled line, that certificates state only what Qori can
prove, is untouched: it governs what a certificate says when there is one.

#### D-045 — End-to-end credentials live in a gitignored `.env.e2e`; absent means skipped, present means it must run

**Decision.** The first-share journey's real vendor values — the owner's Stripe
test connected account, their Google Drive refresh token, a file they picked
through the Picker, and a second Google account that plays the Peer — live in
**`.env.e2e`** in the code repository, gitignored, or in `.env` if the owner
prefers. `bootstrap/app.php` loads it after `.env` and before configuration,
only when `APP_ENV` is `local`, only for `qori:e2e` and `qori:e2e:connect`,
only its `QORI_E2E_*` keys, and not at all when git would commit it.
`php artisan qori:e2e:capture` writes it from what the owner did once in local
Qori, so nobody copies a token by hand.

**No file and no key anywhere, the journey is skipped and the run passes** — on
another machine, in a fresh clone, in CI. **Once the file exists, a missing key
or a value that no longer works fails the run** and names the key and the fix.
The owner, 21 September 2026: "For any local test or e2e test, please read from
.env or maybe a designated gitignore file. if the test is run on other machine
other than local or designated not exists, just let those test pass or skip."

Where a person must be at a vendor, the run is hardcoded (the owner's word, the
same day): Stripe's sign-in and Google's consent are replaced by adopting the
owner's account and token through `PaymentsService::adopt()` and
`ConnectionService::adopt()`; the Picker by posting the Episode form with the
picked file; the card by a signed `checkout.session.completed` built from the
real session read back from Stripe (`T-121`'s second option). Node never holds
a secret, and the run signs with a webhook secret minted for that run.

**Why this shape.** A separate file lets a command own it and rewrite it whole
without touching the owner's `.env`, and deleting it switches the journey off.
`.env.local` was ruled out because Laravel loads it *instead of* `.env` when
`APP_ENV=local` is in the environment; `.env.testing` is committed and is
PHPUnit's. Skipping only when nothing was set up keeps a half-filled file from
passing for green: the review of the first design found that skipping on any
vendor refusal would hide a Qori regression behind "credentials do not fit".
Loading inside PHP, before config, keeps `config/*.php` the only reader of the
environment and keeps the refresh token out of Node, where a Playwright trace
would keep it.

**Consequences.** `T-161` builds it; `docs/tinker/e2e-first-share.md` is the
owner's guide. PHPUnit stays fully faked and never reads the file. `qori:e2e`
no longer empties Mailpit, whose 1025/8025 may be another project's: journeys
read their own recipients, and the fixed Peer address reads only messages that
arrived after the step that sent them. `qori:mail:check` still empties it →
`T-162`. An agent may read the vendors' consoles for the owner but never signs
in, types a secret or changes a setting without asking for that one change.

### 22 September 2026

#### D-046 — Qori's subscription is priced in Australian dollars and shown in the buyer's currency by Adaptive Pricing; no merchant of record at launch

**Decision.** Qori sells its plans from its own Stripe account through Stripe
Billing, as built, with every price in **AUD**, and switches on Stripe's
**Adaptive Pricing** so that Stripe's checkout shows a buyer outside Australia
the price in their own currency. Stripe pays out AUD to a Wise Business account
(or an ordinary Australian bank account); Wise converts to USD only what Qori
spends with suppliers who bill in USD. There is no merchant of record at launch.
The owner, 22 September 2026: "I don't mind getting paid AUD … i can
absolutely get paid aud and use wise business just to pay my service charge",
then "subscription use Adaptive Pricing. I want to get to price where i plan
earlier close to my competitor pricing."

**The prices.** Each AUD price is the planned USD price of the
[11 September review](pricing-and-competitor-review-2026-09-11.md#5-recommended-plan-structure)
at the mid-market rate, rounded to a whole dollar. At 0.7126 USD to the AUD
(21 September 2026):

| Plan          | Planned  | AUD price  | What a buyer in the US pays, with Stripe's 2–4% conversion |
| ------------- | -------- | ---------- | ---------------------------------------------------------- |
| Start monthly | US$39    | **A$55**   | about US$40–41                                             |
| Pro monthly   | US$99    | **A$139**  | about US$101–103                                           |
| Start annual  | US$390   | A$550      | about US$400–408                                           |
| Pro annual    | US$990   | A$1,390    | about US$1,010–1,030                                       |

A buyer who chooses to pay in AUD on Stripe's page avoids Stripe's conversion
fee and pays their own bank's rate instead. The review's conditions still
stand: Pro's price needs a demonstrated reason to upgrade before it is promoted
broadly, annual waits until retention is understood, and US$49 for Start
(A$69) is a later test, not the launch price.

**Why AUD, not USD.** Adaptive Pricing converts a price only when its
currency is one the account settles in
([Stripe](https://docs.stripe.com/payments/currencies/localize-prices/adaptive-pricing.md?payment-ui=stripe-hosted)),
and an Australian account settles AUD. USD payouts for Australian accounts are
offered to "a limited number of businesses in Australia", only to an
Australian bank's USD account and never to Wise, for 1% per payout with a
US$10 minimum
([Stripe](https://support.stripe.com/questions/receiving-usd-nzd-payouts-for-australia-users)).
USD prices without that cost Qori Stripe's 2% conversion on every charge and
still show a foreign buyer USD. AUD with Adaptive Pricing costs Qori nothing in
conversion at checkout; the buyer pays the conversion, as they would to their
bank for any foreign price. Wise's roughly 0.5% applies only to what Qori
spends in USD.

**Why the mid-market rate, not the buyer's.** Setting the AUD price so the US
buyer's figure lands on US$39 after Stripe's fee would make Start A$53 and Pro
A$135: Qori would absorb the buyer's conversion fee on every sale, Australians'
included.

**Why no merchant of record.** Paddle (about 5% + 50¢, the most established),
Polar, Creem and Dodo (about 4%, younger), Lemon Squeezy (slowing since Stripe
bought it) and Stripe Managed Payments (Stripe's fees plus 3.5%, mainly US
businesses so far) were compared on 22 September 2026. What they add is
worldwide sales-tax handling. Qori's buyers are mostly businesses — a business
abroad that gives a VAT or GST number accounts for the tax itself — and Qori is
registered nowhere, so at launch that work is small, while a merchant of record
would be a second billing integration. `BillsGroups` keeps the switch to one
contained, and it is worth revisiting if many buyers turn out to be private
individuals in the EU or UK, where VAT is owed from the first such sale.

**Consequences.**

- `project-plan.md` §5's "Currency (locked for SaaS): USD" and §7's plans "in
  USD" are superseded, and it says so where they stood. §7.1's Wise Business
  payout in AUD stands.
- Pricing stays release checklist (`D-043`). The live AUD prices, Adaptive
  Pricing and Stripe Tax monitoring switched on, and the account's own setup are
  in [`release-prerequisites.md`](release-prerequisites.md). The AUD prices are
  re-derived on the day they are created if the rate has moved more than 5%
  from 0.7126. A later change is a new Stripe price, and existing subscribers
  stay on theirs until they are moved.
- Qori's own pages quote AUD. `formatMoney()` writes `A$55` for a reader
  outside Australia and `$55` for one inside it (`T-058`), so no page quotes a
  foreign price Qori does not charge.
- `T-167`: the console and the design fixtures default to AUD, and a sandbox
  subscription paid in USD proves the plan is still granted. `T-168`: the
  checkout asks a business for its tax number; tax calculation stays off until
  Qori registers somewhere.
- Whether to register for GST below the A$75k threshold (overseas suppliers add
  10% GST to what they bill Qori until it is registered), and whether the AUD
  price includes GST once it is, are questions for Qori's accountant, on the
  release checklist.
- Apple's in-app purchase for a subscription sold inside an iOS app is
  untouched: native apps are deferred (`PLAN.md`, Settled).

#### D-047 — Qori's plans are priced from a USD base, with fixed prices in the major currencies; Adaptive Pricing is off (amends `D-046`)

**Decision.**

- Each plan's Stripe price has **USD as its default currency**: US$39 for
  Start and US$99 for Pro, the figures the prices were planned in.
- It also carries **fixed amounts in the major currencies**, which the owner
  sets, as Stripe `currency_options`: AUD, EUR, GBP, CAD, NZD and SGD to begin
  with.
- A buyer pays the fixed price in their own currency if it has one, and the
  USD price otherwise.
- **Adaptive Pricing is switched off**, so no price Qori quotes moves with the
  exchange rate.
- Qori's pages decide the currency and name it on the checkout session, so
  Stripe's page shows the price Qori's page showed.

The owner reached this over the afternoon of 22 September 2026, after
`D-046`:

- "i can't let customer see fluctuating price every day, i need Hybrid Setup
  for price and I define majority flat price for major currency".
- For a currency without a fixed price: "USD for everyone else", then "I mean
  Base on USD price".
- "my goal is to avoid stripe 2% charge". Three trade-offs were offered: AUD
  and USD only, many fixed currencies, or AUD for everyone. The owner chose
  **many fixed currencies**, accepting the fee.

**Why USD is the default currency.** When a price has no option for the
buyer's currency, "the Session presents to the customer in the default
currency"
([Stripe](https://docs.stripe.com/payments/checkout/localize-prices/manual-currency-prices.md?payment-ui=stripe-hosted)).
With USD as the default, Stripe's own fallback is the owner's rule, even for a
session that names no currency. USD is also the currency the prices were
planned in, the one competitors charge in, and the one Qori's console and
design fixtures already use.

**Why Adaptive Pricing is off.** Every buyer now meets a fixed price, so
Adaptive Pricing has nothing left to convert. It converts only a price in a
currency the account settles in, which is AUD, no longer the default. Fixed
prices override it for their own currencies anyway ("Manually defined
multi-currency prices override Adaptive Pricing for those currencies, even if
it's enabled"). Switching it off makes sure no session ever shows a converted
amount.

**Why Qori names the currency.** Stripe decides the currency on its own page,
from where the buyer is when they open it, and has no call that tells Qori
beforehand what that will be. Naming the currency on the session reverses
this: whatever Qori quoted, Stripe charges ("the Checkout Session's currency is
always EUR (`eur`) regardless of the customer's location"). The owner asked
for exactly that guarantee: "make sure the price is same when they landed in
stripe page".

**What it costs.** Qori's Stripe account settles in AUD, so every charge in
another currency is converted, and Stripe's conversion fee of 2% falls on
Qori: about 80¢ on a US$39 plan. Only an Australian's A$55 escapes it. The
only ways to avoid the fee are charging in AUD, or Adaptive Pricing, which
moves the buyer's price, so the owner took fixed prices over the fee. It can
shrink two ways:

- **USD payouts.** If Stripe admits the account (it serves "a limited number
  of businesses in Australia"), USD charges settle in USD, and the 2% becomes
  1% per payout, with a US$10 minimum
  ([Stripe](https://support.stripe.com/questions/receiving-usd-nzd-payouts-for-australia-users)).
  The payouts must go to an Australian bank's USD account — NAB, not Wise —
  and Qori's USD suppliers can be paid from there.
- **Natural hedge.** Qori's costs are mostly USD, so USD revenue moves with
  them.

**Proposed fixed prices.** US$39 and US$99 at the rates of 21 September 2026,
rounded to a local price point. The rates: EUR 1.1473, GBP 1.3373, NZD 0.5722
and AUD 0.7126 USD; 1.4013 CAD and 1.2759 SGD to the USD. The owner sets the
final figures when the live prices are created (release checklist).

| Currency      | Start  | Pro     | At the rate          |
| ------------- | ------ | ------- | -------------------- |
| USD (default) | $39    | $99     | —                    |
| AUD           | A$55   | A$139   | A$54.7 / A$138.9     |
| EUR           | €35    | €89     | €34.0 / €86.3        |
| GBP           | £29    | £75     | £29.2 / £74.0        |
| CAD           | C$55   | C$139   | C$54.7 / C$138.7     |
| NZD           | NZ$69  | NZ$175  | NZ$68.2 / NZ$173.0   |
| SGD           | S$49   | S$129   | S$49.8 / S$126.3     |

HKD (HK$299 / HK$779) and MYR (RM159 / RM399) can join the list the same way.
A buyer in any other currency pays in USD, and their own bank converts. That
includes JPY, which `amount_cents` could not describe (`T-054`).

**What stands from `D-046`:** Stripe Billing, no merchant of record, AUD
payouts to Wise Business, prices anchored on US$39 and US$99 at the mid-market
rate, the GST questions for the accountant, and `T-168`.

**What this supersedes in `D-046`:** AUD as the prices' default currency,
Adaptive Pricing, and "Qori's own pages quote AUD".

**Consequences.**

- Qori's pricing and billing pages quote the visitor's price — their
  currency's fixed amount, or USD — and the checkout names that currency
  (`T-170`). How Qori picks a visitor's currency is the owner's call, asked
  the same day.
- **Plan coupons are percent-off.** Stripe shows a buyer their own currency
  only when the session's discounts carry that currency too, so an amount-off
  coupon in one currency would pull the session back to the default (`T-169`).
- **Tax, later:** once Stripe Tax calculates (`T-168`'s switch), each currency
  option needs a `tax_behavior`, or Stripe presents the default currency
  instead.
- Release checklist: Adaptive Pricing stays off, and each live price is
  created in USD with the owner's fixed amounts as currency options. Applying
  for USD payouts, and opening a NAB USD account for them, is optional and
  worth doing once USD sales are steady.
- `T-167` is re-scoped to a USD base. `T-169` holds the fixed amounts on the
  price row and in the console. `T-170` quotes and charges the visitor's
  currency.

#### D-048 — Qori sets each plan's price in USD and calculates the fixed currencies from it; Stripe's price is in AUD with Adaptive Pricing for the rest; Qori publishes prices and vouchers to Stripe (amends `D-047`)

**Decision.**

- **Staff set one number per plan: its USD price** (Start US$39, Pro US$99),
  in Qori. They type nothing else about money.
- **Every fixed currency is calculated from it**: the USD amount at the day's
  mid-market rate, **rounded up to a whole unit** of that currency. US$39 is
  A$54.64, so **A$55**; €33.94, so **€34**; £29.12, so **£30**.
- **Stripe's price has AUD as its default currency**, at the calculated AUD
  amount, and carries the other fixed currencies as `currency_options`. USD is
  among them, at the USD price itself.
- **Adaptive Pricing is on.** It converts from AUD for every currency that has
  no fixed price.
- **Qori is the source of truth, and it writes to Stripe.** Publishing a price
  creates the Stripe price. Changing one never edits a Stripe price: Qori
  creates a new one and archives the old. Existing subscribers stay on the
  price they bought until someone deliberately moves them. That move is a
  separate decision, not taken here. Plan vouchers are created in Stripe by
  Qori the same way.

The owner, 22 September 2026, after `D-047`: "When I said price is base on
USD i mean USD $39 for starter, use 39 to calculate and get $55 for AUD and
set AUD to 55 in stripe, same goes with EUR GBP etc. All the price is base on
USD. when I change price I only edit Qori USD price and every other fix
currency calculate from USD round up to full dollar. Base turn on adaptive
pricing in stripe which is base on AUD for otther currency outside of fixed
one." Earlier, on who holds the truth: "can the stripe pricing be injected
from Qori and Qori is the source of truth? same goes for voucher?"

**Why AUD is Stripe's default currency when USD is Qori's.** Adaptive Pricing
converts only a price in a currency the account settles in, and Qori's account
settles in AUD. The AUD amount is itself calculated from USD, so every price
traces back to the USD figure, including the ones Adaptive Pricing converts
from AUD.

**The fixed prices, calculated.** The European Central Bank's reference rates
of 21 September 2026: USD 1.1490 to the EUR, AUD 1.6098, GBP 0.85780, CAD
1.6091, NZD 2.0035, SGD 1.4647, HKD 9.0144, MYR 4.6850. The result replaces
`D-047`'s hand-rounded table. The owner's rule, not a price point, decides
the figure: €34 and £30, not €35 and £29.

| Currency                  | Start, from US$39     | Pro, from US$99         |
| ------------------------- | --------------------- | ----------------------- |
| AUD (Stripe's default)    | A$55 (54.64)          | A$139 (138.70)          |
| EUR                       | €34 (33.94)           | €87 (86.16)             |
| GBP                       | £30 (29.12)           | £74 (73.91)             |
| CAD                       | C$55 (54.62)          | C$139 (138.64)          |
| NZD                       | NZ$69 (68.00)         | NZ$173 (172.63)         |
| SGD                       | S$50 (49.72)          | S$127 (126.20)          |
| HKD, if added             | HK$306 (305.97)       | HK$777 (776.70)         |
| MYR, if added             | RM160 (159.02)        | RM404 (403.67)          |

Rounding up is to the whole unit, and a figure already whole stays as it is.
The NZD Start figure is 68.0039 before rounding, so it becomes NZ$69.

**Where the rates come from (decided, not asked).** The European Central
Bank's daily reference rates. They are free, official and need no account,
and they cover every currency above; the rate between two non-euro
currencies is worked out through the euro. The rates used are stored with each
published price, so any figure can be explained later. Another source is one
integration to swap.

**Why Qori writes to Stripe.** Stripe does not let an amount be edited once it
exists:

- a price's `unit_amount` and currency are not updatable
  ([Stripe](https://docs.stripe.com/api/prices/update));
- a coupon's "currency, duration, amount_off" are "by design, not editable"
  ([Stripe](https://docs.stripe.com/api/coupons/update)).

So a price that changes is a new Stripe price whatever happens. Typing the
same amounts into Stripe and into Qori, across as many as eight currencies,
is how the page and the charge come to disagree.

**What it costs.**

- An Australian's A$55 carries no conversion fee.
- A sale in any other fixed currency pays Stripe's 2% conversion, on Qori's
  side.
- Everyone else pays through Adaptive Pricing: the buyer pays Stripe's 2–4%,
  and Qori receives AUD with no conversion fee.
- USD payouts, which would cut USD sales to 1%, remain optional (`D-047`).

**What stands from `D-047`:**

- fixed prices for the major currencies;
- the checkout names the currency for a fixed-price buyer, so Stripe's page
  shows the price Qori's page showed;
- plan coupons are percent-off;
- each currency option needs a tax behaviour before Stripe Tax calculates.

**What this supersedes in `D-047`:**

- USD as Stripe's default currency;
- Adaptive Pricing off;
- "USD for everyone else";
- the hand-rounded table.

**Consequences.**

- **The checkout names the currency only when it is a fixed one.** For any
  other currency it names none, so Adaptive Pricing converts (`T-170`).
- What Qori's page shows a visitor whose currency has no fixed price is the
  owner's call, asked the same day. The proposal is the USD price, with a line
  saying checkout charges their own currency.
- A price that has not been re-published does not follow the market. Its
  fixed amounts stay as calculated until staff re-publish.
- Tasks:
  - `T-167` keeps USD as Qori's currency.
  - `T-169` calculates the fixed prices.
  - `T-172` publishes prices to Stripe, and `T-173` creates vouchers in
    Stripe.
  - `T-170` names the currency only for a fixed-price buyer.
- The release checklist turns Adaptive Pricing back on. Prices and coupons
  are no longer created by hand in Stripe's dashboard: Qori's admin publishes
  them.

#### D-049 — A Peer agrees to the terms of what they get, Qori's own until creators write theirs; emails from the creator are optional (amends §9)

**Decision.** Before a Peer gets a Series — free or paid, from the stranger's
form, the signed-in button or checkout — they tick one required box: they
agree to the terms for that Series, shown on the page. Until a creator can
supply their own terms (`T-179`: a setup step, or a template picked per
Series), the terms are a static agreement Qori supplies, versioned, and the
version and time are recorded on the Access. Agreeing to hear from the creator
by email stays on the page as its own box, **optional and unticked**: a Peer
who leaves it gets access and is not emailed by campaigns.

The owner, 22 September 2026, asked whether a Peer must agree to the creator's
emails to get free access: "I think creator must create their own terms &
agreement to show on screen for their sale for their peer. might be one of the
setup too, or allow to set a template pick in each series. For now please
draft a static and use as Qori supplied agreement."

**Why this shape.** What a Peer is entering is an agreement with the creator
about what they get, which is what the terms say. Consent to marketing is a
different thing, and making it the price of access is the bundling privacy
law treats as consent not freely given. §9 asked for consent explicitly and
blocking so that no Peer was created without the question; the question is
still asked on the same screen, and a Peer who says no is simply not a
campaign recipient.

**Consequences.** `T-178` builds it and changes `ConsentTest`, whose rule this
reverses. A paid Peer's choices travel in the checkout session's metadata to
the webhook that grants the access, so a purchase records consent only when
the box was ticked. The agreement's words are a draft Qori supplies, and a
legal read before release is on the release checklist. Accesses a creator
gives by hand carry no terms: nobody was shown a screen.

#### D-050 — An invitation is for one address and one Series, lasts as long as the creator says, and carries its own price (settles `T-043`'s open questions)

**Decision.** A creator invites people to one Series, up to ten at a time. Each
invitation is bound to **the address it was sent to and that Series** — one
per pair, so the creator sees that an address was already invited, and when,
before sending again; sending again replaces the link and the terms rather
than adding a second invitation. Accepting it needs that address: a guest
proves it with the code the Series page already sends, and a signed-in person
must be signed in with it.

It **expires** when the creator says: a number of days, 30 unless they choose
otherwise, or the end of the Series' last live session when it has one ahead.
Qori shows the creator when the date they picked runs past that last session
and leaves the choice to them, because a Peer who can no longer join a live
session can still want the Series. **A Series has no dates of its own**, and
none are added: a self-paced Series has no end to watch, and its invitations
simply expire.

Each person's **price is prefilled with the Series' price** and the creator may
change it to anything the Series could be priced at, or to nothing: free, a
discount for one person, or a percentage off for the whole batch. The price is
stored on the invitation, in the Series' currency; a free Series invites for
free.

The owner, 22 September 2026: "invitation tied to the address as well as series
so it can be option to track address is already invited at date/time. it
should still good to have ttl, watch out for series end time. Logically
thinking a peer can still buy the series even though peer can't join the live
session should able to do replay. I lean towards creator decide. Just thought
series start and end shouldn't be mandatory because it can be a completely
offline self learning." And: "A free invitation to a paid Series is simply a
prefill set price allow override for creator. Doesn't have to be free,
flexible enough to be like 30% discount."

**Why this shape.** Binding to the address makes a forwarded link worth
nothing to a stranger — the code goes to the invited inbox — which is what
makes a free or discounted invitation safe to send at all, and it needs no
single-use rule on top. Binding to the Series makes "already invited" a fact
the page can show instead of a second email. The creator knows their course;
a date Qori enforced against the last session would stop the sale the owner
described.

**Consequences.** `T-043` sends and lists invitations and makes the link
resolve; `T-181` accepts them on the Series page, free or at the invitation's
price, through the code step and checkout that already exist, and `T-027`
keeps the rest of its receiving journey. An accepted free invitation is an
Access given away — no price, counted against the Peer cap like any grant —
and a paid one is a sale at the price paid. Invitations are transactional
mail, not campaigns (`T-045`): no suppression list or monthly allowance, but a
daily cap on the free plan, `invitations_per_day` beside `edm_per_day`, 10 as
§5 has it. The number is pricing, and so release checklist.

#### D-051 — The merchant-of-record revisit counts every EU and UK subscriber with no valid VAT number, business or not (amends `D-046`)

**Decision.** `D-046` revisits having no merchant of record "if many buyers
turn out to be private individuals in the EU or UK". What it counts instead
is **EU and UK subscribers who gave no valid VAT number**, whoever they are:
the Stripe customer's billing country is in the EU or the UK, and its
`tax_ids` holds no VAT number, or one that Stripe's check against the
government record has not returned as `verified`. `T-168` already saves both
on the customer, so the count is read from Stripe and nothing in the code
changes. The rest of `D-046`, as `D-047` and `D-048` amend it, stands, and so
does `T-168`'s rule that the number is never required.

Raised on 22 September 2026, when the owner asked how a solo developer can
earn before working through the law, and recorded at the owner's word: "yes
please".

**Why the number, not the person.** `D-046` reasons from the number — "a
business abroad that gives a VAT or GST number accounts for the tax itself" —
but names its trigger by the person. The two differ for a buyer Qori will see
often: a solo creator trading below their country's VAT threshold, who is a
business and often has no VAT number.

- **EU.** A supplier may treat a customer established in the EU who has not
  given it a VAT identification number as a non-taxable person (Council
  Implementing Regulation (EU) No 282/2011, Article 18(2),
  [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32011R0282)).
  For a supplier outside the EU, that is a consumer sale, taxed from the
  first one.
- **UK.** HMRC's guidance for digital services is to treat a sale with no VAT
  registration number as business-to-consumer. Accepting other evidence that
  the buyer is in business is the supplier's choice, not the buyer's right
  ([GOV.UK](https://www.gov.uk/guidance/the-vat-rules-if-you-supply-digital-services-to-private-consumers)),
  and Qori's checkout collects only the number.

**The count matters from one.** Qori owes VAT in a country from its first such
sale there, as `D-046` says, so "many" never decides whether anything is owed.
It decides the cheaper way to pay it: registering — the EU's non-Union OSS is
one registration and one quarterly return for every member state, and the UK
is a registration of its own — or a merchant of record behind `BillsGroups`,
which takes a share of every sale (`D-046` compares them).

**Consequences.** Stripe Tax threshold monitoring will not raise this count at
launch: Stripe notifies only once an account has had US$10,000 of revenue in
the previous year ([Stripe](https://docs.stripe.com/tax/monitoring)), while
the EU and UK owe from the first sale. Step 5 of
[`release-prerequisites.md`](release-prerequisites.md) now says so.

#### D-052 — A plan change follows Claude's billing: an upgrade is charged at once, prorated, and restarts the cycle; a downgrade takes effect when the paid period ends (settles `T-180`'s open questions)

**Decision.**

- **An upgrade takes effect at once.** It is any move to a dearer plan, such
  as Start to Pro. The Group is charged one full period of the new plan, less
  the unused part of the old one. The billing cycle restarts at that moment,
  and the next renewal is the new plan's full price. Before the owner
  confirms, Qori shows what will be charged.
- **A downgrade takes effect at the end of the period already paid for.**
  Until then the Group keeps the dearer plan. Nothing is refunded or credited.
- **A change stays in the currency the Group already pays in.** Stripe refuses
  a second currency on one customer (`T-170`'s sandbox check).
- **A converted renewal may charge a different amount**, and that is
  accepted. A buyer on Adaptive Pricing is charged at each payment's rate
  (`T-172`).

The owner, 22 September 2026: "I really like claude's pricing prorata by
minute, can that be implemented in qori so to downgrade follow claude as
well", and "A converted price can change at each renewal. probably can't do
anything at this moment, just have to accept this."

**What Claude's billing does, as its help pages say.** On an upgrade mid-cycle,
"you are charged for one full billing cycle of the new plan, less a prorated
amount for value remaining in your old plan", "you'll reset your billing
cycle and receive an immediate invoice for the change", and "Your next
renewal invoice charges the full price"
([Claude Help Center](https://support.claude.com/en/articles/16607638-understanding-your-pro-or-max-plan-invoices)).
A cancellation "will take effect at the end of your current billing period
and you can continue using your paid plan until then"
([Claude Help Center](https://support.claude.com/en/articles/8325617-cancel-your-pro-or-max-subscription)).
The pages say nothing about a downgrade between two paid plans. Ending at the
paid period is Claude's documented way of giving up a plan, and it needs no
refund or credit, so it is the reading taken here. If the owner meant a
downgrade prorated at once, with a credit, this decision changes.

**How Stripe does it (for `T-180`).** Stripe prorates by the second, finer than
"by minute".

- An upgrade updates the subscription's item to the new price with
  `proration_behavior=always_invoice` and `billing_cycle_anchor=now`, which is
  Claude's shape: a full period of the new plan less the old plan's unused
  part, invoiced at once. `payment_behavior=pending_if_incomplete` applies the
  change only if that payment succeeds.
- A downgrade is a subscription schedule whose next phase, at the current
  period's end, moves to the cheaper price and the cheaper plan's metadata.
- The price shown before an upgrade comes from Stripe's invoice preview for
  that change, so Qori quotes the figure Stripe will charge.

**Consequences.** `T-180`'s owner questions are answered. It also needs the
subscription's own id, which Qori does not keep today (a Group holds only
`stripe_customer_id`), and the preview and confirm step on the billing page.
