---
stream: storage
---

# Stream: storage

**Goal.** A creator's own files, videos and live sessions reach every Peer
with access, without leaving the account they already live in. The creator
connects Google Drive, OneDrive, Dropbox, Zoom, Teams, Vimeo or YouTube once,
picks what a Series holds, and Qori makes sure each Peer can open it on the
vendor's own site — by granting the Peer's vendor account where the vendor
allows it, and by showing the link only to Peers with access where it does not
(`D-016`).

**Done when.** A Peer who signs up, claims or buys can open every Episode of
the Series within moments, in a new tab on the vendor's site, and keeps seeing
whatever the creator adds, edits or replaces there; the creator connected the
account from the Integrations page, was told the limitations of the tier they
chose, and never had to re-share anything by hand; a grant that the vendor
refuses is retried by a scheduled command and surfaced to the creator, never
to the Peer as a dead page.

**All seven providers are in the beta release** (`D-018`, 17 September 2026),
and no tier is refused because the vendor's own rules make it awkward: the
limitations are stated on screen, Qori says what it recommends, and the
platform a creator brings is the creator's own.

## Why this is its own stream

`T-044` sat in `reachability` because connections were built with no way in.
The owner's decision of 15 September 2026 (`D-016`) made it the first slice
of something larger: every storage and live-session integration follows one
pattern — connect, pick, grant, open, revoke — and the tasks share a
foundation (`series_containers`, `vendor_grants`, one ensure-the-grant step,
one Open route) and a file set (`IntegrationsController`, `SharedController`,
`AccessService`, `routes/shared.php`, `routes/settings.php`,
`app/Integrations/*`). Splitting that across `reachability`, `selling` and
`onboarding` would put three owners in charge of one call chain.

The two priorities the owner set, in order, decide every trade-off here:

1. **A Peer gets working access right after signing up, claiming or buying.**
   The vendor account is confirmed before payment where a Series needs one,
   the grant runs inside the same request that creates the Access, and it runs
   again on the Series page, on Open and from a sweep, because the queue cannot
   retry.
2. **Peers always see the creator's current content.** Qori grants on a
   container — one folder or one recurring meeting per Series — so new
   material needs no new grant, and the vendor's own rules for what stays
   current are stated on screen when the creator picks the tier.

Downloads, forwarded links and airtight revocation are not concerns; revoke is
best effort. Nothing here re-argues that.

## Tasks, in order

The order follows `D-016`'s record and a developer's review of the plan on
16 September 2026: keep the architecture, prove Google Drive before the shared
foundation is frozen, deliver one complete journey — a new Peer buys, opens
the content, and sees the creator's later edit — and only then add providers
one at a time, each earning its place through a tested Peer journey. That
review is folded into the order below and into the tasks themselves; what it
asked for is recorded under Notes. **Every provider here is wanted in beta**
(`D-018`), so the order is the order they are built in, not a list of which
ones make it.

1. `T-111` — Qori's own storage is named for Cloudflare R2: a rename and a
   data migration, first because every provider task after it cites the
   offering's name (`D-022`)
2. `T-089` — Open is a link to a Qori route that sends the Peer to the vendor:
   every provider needs it, and it removes the popup a browser can block with
   no fallback
3. `T-044` — Connect a storage account, from onboarding or from a settings
   page: the Integrations page grows provider sections with a tier dropdown,
   the tier's limitations, reconnect, and the held different-account change;
   Google is its first provider
4. `T-151` — The token refresh keeps a connection alive: the daily command, the
   on-demand refresh before any vendor call, the one advisory lock and the
   reconnect email. Cut out of `T-044` on 20 September 2026 with `T-152`, because
   that task was `L` at 68 paths; both depend on it and on nothing else, so they
   run side by side after it, and `T-091` depends on this one for `fresh()`,
   `markForReconnect()` and `AdvisoryLock`
5. `T-152` — An Episode needs its provider connected: the refusal at add for a
   provider whose item id means nothing without the creator's account (`D-025`).
   It took `T-123` out of `T-044`'s `depends:` with it, and `T-094` and `T-098`
   each add their provider's arm
6. `T-093` — Spike: Google Drive folder grants under the narrow scope: the one
   experiment that can change the foundation's shape, so it runs before the
   foundation is specified to the column
7. `T-091` — Every Peer with access is granted on the Series container: the
   foundation the per-Peer providers share — the two tables, the contract,
   the ensure step on grant, Series page and Open, and the states that say
   who resolves a stalled grant. Re-drafted on 20 September 2026 (`D-040`):
   the grant is made when a Peer opens the file, and nothing sweeps
8. `T-092` — A Peer confirms the vendor account they will open with: the
   user-level identity under `/u/*`, confirmed by signing in with the vendor,
   prompted on the Series page and before payment
9. `T-094` — Google Drive Episodes, each file shared with each Peer: the
   first complete journey, and the release check for everything before it.
   Re-drafted on 20 September 2026 (`D-036`) after `T-093`: the grant is on
   the Episode's file and a Series has no Drive folder, so `T-091` carries
   grants on an item as well as on a container
10. `T-095` — Spike: Dropbox viewers on a shared folder across plans: run
    alongside the Drive work; it can rule the approach out
11. `T-097` — Spike: OneDrive silent invites and moved files: likewise, with
    personal and work accounts as separate answers
12. `T-090` — Vimeo and YouTube Episodes open as unlisted links: no grant
    machinery, in free and paid Series alike (`D-019`), once the playback checks
    are settled; it adds its pass to the Episode check `T-094` builds
13. `T-096` — Dropbox Episodes from a shared folder each Peer joins
14. `T-098` — OneDrive Episodes from a folder shared with each Peer
15. `T-099` — Spike: Zoom recurring-meeting registrants
16. `T-122` — Spike: a Zoom cloud recording is found from a pasted join link
    and opens for someone outside the account: `T-099`'s recording step on its
    own, so the `classroom` stream can specify detection against real payloads
    (`D-027`)
17. `T-141` — A creator connects the Zoom account they already have and is told
    whether it keeps cloud recordings: the Zoom section on `T-044`'s contract,
    which detection needs, and the Zoom client `T-100` builds on
18. `T-100` — Zoom live Episodes register each Peer once per Series
19. `T-142` — Qori finds a live Episode's Zoom cloud recording from the spike's
    fixtures: `FindsRecordings` and the Zoom folder; the sweep that uses it is
    `classroom`'s `T-143`
20. `T-101` — Teams live Episodes share one stored meeting link
21. `T-150` — Spike: can Qori upload a file into the connected Drive: the two
    questions `T-149` cannot be specified without — whether a browser may send
    the bytes straight to Google, and whether a folder the app made lets it
    upload and grant with nothing picked (20 September 2026)
22. `T-149` — One dialog adds files from any connected storage: Upload,
    Google Drive, Dropbox and OneDrive in one place, once two providers'
    choosers exist and `T-150` has said what Upload can be

The spikes come before their provider because each provider's spec has to cite
an observed response, and one result can change the design: whether the narrow
Google scope reaches a picked folder, whether a Basic Dropbox account can add
a viewer and whether a Peer can open a file before pressing Join, whether a
OneDrive invite with no email can be taken up, whether Zoom stops registration
at room size. `T-102` and `T-103` in `selling` come before any paid Series
uses a provider here.

## The review of 20 September 2026

An outside developer read the whole stream against
[`../reviews/storage-2026-09-20.md`](../reviews/storage-2026-09-20.md) and
returned twelve findings, nine of them P1. They are transferred into the
tasks they concern, under a dated heading in each one's "Before this can be
ready"; the review's own recommendation is **do not freeze the grant
foundation yet**, because `D-036`'s consequences never reached identity
discovery, permission ownership, deletion, replacement or recovery. Three
things it found are worth carrying here rather than only in a task:

- **The fan-out is two calls per grant, not one.** Six thousand grants is
  twelve thousand calls, 220 to 328 minutes serial at the seconds `T-093`
  measured. `T-091` said five inline grants cost about ten seconds; they cost
  11 to 16. Numbers taken from the spike's read timings were used for its
  write timings throughout, and the specifications that repeated them are
  corrected.
- **Nothing in the stream has observed a directly shared file.** Every Google
  fixture is a folder grant. `D-036` moved the target precisely because the
  target changes the behaviour, so `T-093` needs a direct-file pass before
  `T-094` can be `ready`.
- **Two of the three decisions it asked for were taken the same day.**
  Disconnect stays as `T-044` specifies it and `D-038`'s consequence line is
  corrected instead (`D-039`); the review's bounded cleanup period was
  declined, because holding a creator's token after they have asked Qori to
  let go is the opposite of what Disconnect means. And **every provider stays
  in the beta**: the owner declined narrowing the first storage release to
  Google Drive — "I plan to do all, it is a lot of work. But I see this is
  the major selling point for Qori" — so `D-018` stands and the order above
  is unchanged. What the review's arithmetic buys is an honest view of the
  size of it, not a shorter list. The third, whether a due `pending` item may
  offer Open, is still open and is `T-091`'s.

The stream's shape is therefore the same after the review as before it. What
changed is the foundation underneath: `T-091` and `T-094` carry nine findings
between them and neither can be `ready` until they are answered.

The reviewer's estimate arithmetic on the current order is in the same
document: sixteen drafts, one blocked, none ready, and nineteen developer-days
as a lower bound before the six small tasks, specification repair and vendor
approvals. It does not name a date and neither does this file.

## Where it touches other streams

`T-102` (a delayed payment still becomes access) and `T-103` (a refund
revokes the vendor grant) sit in `selling`, because they are about money
becoming access and the money path is that stream's. `T-092` meets `onboarding`
at the Series page and at checkout, where the vendor account is confirmed
before payment: `T-073` and `T-074` own that page and `T-092` adds one step to
it. `T-028`'s storage stage links to the provider sections `T-044` makes.
`T-043`'s invitations land on the Series page and pick up the same prompt and
ensure step, and say so in that draft.

The `classroom` stream (`D-024` to `D-031`) takes the pasted-link tier that
stands beside `D-016` until each connector here lands, so a creator can give a
join link, a recording and a material by pasting a URL Qori never follows. It
waits on `T-089` for the Open route the Peer's Join and Watch use, and on
`T-044` for the Zoom connection that automatic recording detection needs. It
amends six drafts in this stream — `T-044`, `T-089`, `T-091`, `T-094`, `T-100`
and `T-101` — and each says in its own header what changed and which decision
changed it.

## Notes

The research behind these drafts — every provider and account tier against the
five steps, with what is documented, what is community-reported and what is
still unproven — is the owner's blueprint document of 16 September 2026; the
task files carry the facts a developer needs and cite the vendor page for each.
What each account costs and how Qori gets developer access to it is
[`vendor-accounts.md`](../vendor-accounts.md).

**A developer reviewed this plan on 16 September 2026** and its four asks are
folded into the order above and into the tasks, so the review itself is not
kept:

1. Prove Google Drive before the shared foundation is frozen — `T-091` depends
   on `T-093`, and the first complete journey is the release check for
   everything before it.
2. Make "access within moments" measurable — every grant carries one of six
   states naming who resolves it, with short request timeouts, and grants
   already marked done are re-checked rather than trusted forever.
3. Give a Series its own container, and say on the picker that sharing a folder
   shares everything inside it.
4. Finish the specs before treating any of this as executable, and let each
   provider earn its place through a Peer journey somebody has walked.

**A designer reviewed the drafts on 17 September 2026.** Its five asks are
recorded as `D-020` and `D-021` and written into the tasks, so the review
itself is not kept either:

1. Show a buyer what the Series needs from them before they pay, and promise
   nothing about readiness at payment — `T-092` renders each provider's
   before-buying lines, which `T-094`, `T-096` and `T-098` write.
2. Let a person who has fixed something say so — Check again for a Peer
   (`T-091`, shown by `T-096` and `T-098`), Try again now for a creator's
   waiting grants (`T-091`), and Check now on an Episode's warning (`T-094`,
   which `T-090` extends).
3. One destination when Open cannot proceed: the Series page's notice, with one
   action per state (`D-020`; `T-089` and `T-091`).
4. Show the impact before a live folder, meeting or account changes, and say
   truthfully what Qori does in the vendor account — `T-091`'s dialog, used by
   the provider tasks, and `T-044`'s held account change and disconnect.
5. Setup that can be scanned: the recommendation and at most three essential
   limitations above Connect, the rest in a disclosure — `T-044`, with each
   provider task choosing its essential lines.

The same pass settled a collision the drafts had: `T-090` and `T-094` each
created `qori:episodes:check`. `T-094` builds the one command and Check now,
and `T-090`, `T-096`, `T-098` and `T-100` depend on it — the order above
already puts Google Drive's journey before the providers that follow it.
