---
id: T-100
title: Zoom live Episodes register each Peer once per Series
stream: storage
status: draft
owner: unassigned
estimate: L
depends: T-044, T-091, T-094, T-099, T-141, T-157
blocks: T-101
---

# T-100 — Zoom live Episodes register each Peer once per Series

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016`, the owner's BYO blueprint and the developer review of the same day,
> and amended on 17 September 2026 with `D-018`: Zoom is in the beta release,
> and a tier is explained rather than refused. Amended the same day with
> `D-020` (a Peer who cannot join yet is sent to the Series page's notice) and
> `D-021` (Check again and Try again now, the impact of replacing a meeting
> shown first, each tier's essential lines, and no before-buying line). Amended
> again on 18 September 2026 by the classroom decisions. `D-024` removes
> `captureRecording()` and the `EpisodeType::Video` arm for Zoom: a recording is
> a row in `episode_recordings`, never a second Episode. `D-026` keeps
> `content['join_url']` on every live Episode as the unconnected tier and keys
> this task's Series container on the same `content.meeting_id`, and renames
> this draft's `LiveSessionService` to `SeriesMeetingService`, because the state
> service of that name is `T-125`'s. `D-027` replaces
> `SchedulesMeetings::recordings()` and `App\Data\MeetingRecording` with
> `App\Integrations\Contracts\FindsRecordings` and
> `App\Integrations\Zoom\ZoomRecordings` (`T-142`), and moves this draft's
> `ZoomHttpClient` out of `app/Integrations/Concerns` into
> `app/Integrations/Zoom/ZoomClient` (`T-141`), which is where `D-022` says it
> belongs. Amended on 19 September 2026 from that day's cross-draft decisions:
> the Files table and `ZoomMeetings` now take `T-141`'s `ZoomClient`, so this
> draft depends on `T-141`; `grant()` takes `T-091`'s `App\Data\GrantIdentity`;
> a registrant Zoom no longer lists is `GrantResult::ERROR_PERMISSION_GONE`;
> every `$timeoutSeconds` is a budget `ZoomClient` may only shorten (`D-034`);
> and the Zoom tests sit under `tests/Feature/Integrations/Zoom/`, beside
> `T-141`'s and `T-142`'s. The rest of what `T-141`'s Notes ask of this draft
> is open at the bottom. Amended on 20 September 2026, when `T-091` was cut in
> three: the grant core stayed there, the creator's surfaces went to `T-157`,
> and the meeting half came here and to `T-101`. So this task now declares
> `ContainerChangeImpact::kind()`'s `meeting` arm and the four
> `series.container_change.meeting.replace.*` lines, which `T-101` cites rather
> than repeats, and depends on `T-157` for `VendorAccessService::impactOf()`,
> the `containerImpact` prop, `ContainerChangeDialog.vue` and Try again now.
> The same day `D-040` deleted the scheduled sweep, `qori:access:reconcile` and
> the Peer's Check again from `T-091`: a grant is attempted when a Peer presses
> Open, for the one item they are opening, and at no other time, so the
> sentences here that promised a scheduled retry say that instead. The
> consolidation pass that worked those findings through is recorded under
> Read-through, 20 September 2026.

## Why

A live Episode is a type with two providers and nothing behind either of them.
`EpisodeType::allowedProviders()` gives `Live` the pair `Zoom, Teams`
(`app/Enums/EpisodeType.php:35`), `EpisodeProvider::Zoom` maps to
`ConnectionProvider::Zoom` (`app/Enums/EpisodeProvider.php:23`, `:42-51`),
`T-029` gave the session a time in the Group's zone
(`app/Http/Requests/Share/StoreEpisodeRequest.php:105-107`) — and the join link
is a string the creator pastes, optional, labelled "Join link (optional for
now)" (`resources/js/pages/share/series/Show.vue:239-243`,
`StoreEpisodeRequest.php:190-195`). There is no `app/Integrations/Zoom`
directory, no `zoom` block in `config/services.php`, nothing bound in
`app/Providers/IntegrationServiceProvider.php:24-40`, and
`PlaybackTicketService::resolve()` throws `errors.playback.unsupported_provider`
for a live Episode (`app/Services/PlaybackTicketService.php:85-89`) — which is
why `T-089` gives one no Open control at all.

Afterwards a creator connects Zoom on `T-044`'s machinery, points the Series at
**one recurring fixed-time meeting** as its `series_containers` row, and each
live Episode is one occurrence of that meeting. `T-091`'s ensure step registers
every Peer with access exactly once, stores the registrant id and that Peer's
own `join_url`, and Open sends them straight into the session. Nothing is
pasted, and a Peer added an hour before a session can join it.

## Decisions taken to make this specifiable

**Zoom is in the beta release, like every other provider in this stream**
(`D-018`, 17 September 2026). The owner wants all seven available at beta, so
nothing here is written to wait its turn behind the storage journey, and
`PLAN.md`'s execution rule 5 and its "broad Zoom/Teams work" line — which this
draft used to read against — are the owner's to edit.

**Every Zoom tier is offered, Basic included, with what it cannot do said on
screen before the creator connects** (`D-018`). Registration needs a licensed
host on Pro or higher, cannot use the Personal Meeting ID and cannot use a No
Fixed Time recurring meeting
([KB0065026](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0065026)),
so on Basic there is no per-Peer grant and no revoke. That is what
`connections.providers.zoom.limits.zoom_basic.registration` says, beside
`connections.providers.zoom.tiers.zoom_basic.recommended`, which says what Qori
recommends instead; the creator decides from there, because the platform they
bring is theirs and Qori advises rather than refusing. Every Zoom line sits
under `connections.providers.zoom.*` in `T-044`'s shape — `tiers.<tier>.label`,
`help` and `recommended`, and `limits.common.*` and `limits.<tier>.*` — because
that is all `ProviderSections` reads. So `ProviderTier` gains five Zoom
cases and no `supported()` flag, `BeginConnectionRequest` validates the tier
without refusing one, and a Basic account that reaches a registration call
lands on the `zoom_host_unlicensed` or `zoom_registration_off` row of the table
in Code — a sentence naming what is wrong, not a silent failure.

**Each Zoom tier's essential lines are what a Peer needs, what stops Qori
registering anyone, and the one-meeting rule** (`D-021` rule 4), in that order
in `ProviderSections::ESSENTIAL` (Code): `limits.common.no_account` (nobody
needs a Zoom account unless the creator requires Zoom sign-in), then Basic's
`limits.zoom_basic.registration` or every paid tier's `limits.common.breaks`,
then `limits.common.one_meeting`. The occurrence cap, the idle expiry, the
waiting room, Zoom's own emails, recordings and the admin approval sit in
`T-044`'s disclosure, because each costs a session or a step rather than every
Peer's way in. The one-meeting rule is said again where the meeting is chosen
(`connections.meeting.shares_everything`).

**The container is one recurring fixed-time meeting per Series — `type` 8,
`settings.registration_type` 1 (register once, attend any occurrence),
`settings.approval_type` 0 (automatic).** Register-per-occurrence means one add
call per Peer per session against a cap of three a day, and manual approval
leaves the registrant with no join link; priority 1 rules both out. `T-099`
validates the mode (provisional — see below).

**The creator picks an existing meeting; Qori does not create one** (provisional
— see below). `D-016` says the creator picks what a Series holds with the
vendor's own picker, and the research designs Pick as list-then-read. Qori lists
the host's scheduled meetings, reads the chosen one, and where a setting it
needs is wrong offers one button that `PATCH`es it — with the creator's
go-ahead, never silently.

**A Series' meeting is dedicated to that Series.** `T-091`'s unique
`(group_id, provider, external_id)` on `series_containers` already forbids
sharing one; the picker copy says that everyone with access to this Series is
registered for every session on that meeting, whether or not it is an Episode.

**Each live Episode is one occurrence of that meeting, never a second meeting.**
`episodes.content` carries `meeting_id`, `occurrence_id` and `starts_at`;
`T-029`'s field still supplies the hour, read in the Group's zone. A meeting
holds at most 60 occurrences and its ID expires after 365 days with no
occurrence started
([KB0065026](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0065026),
[KB0064248](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0064248)).
Recreating the meeting breaks every stored `join_url`, so the copy says to add
each new session to the same meeting and Qori adds one by `PATCH`ing that
meeting.

**Zoom generates occurrences from a recurrence rule, so a time the rule does not
produce is a refusal the creator can act on, not a silent mismatch**
(provisional — `T-099` proves the mechanism). `SeriesMeetingService` matches the
submitted instant against the meeting's `occurrences[]`; when none matches it
extends the recurrence through `PATCH /meetings/{meetingId}` and re-reads; when
Zoom will not produce that time the creator is told to add the session in Zoom
and pick it here. The Episode form for a Zoom Series therefore offers the
meeting's occurrences rather than an empty datetime.

**The grant is a registrant, and the row is `granted` only when a `join_url`
comes back.** `POST /meetings/{meetingId}/registrants` returns `registrant_id`
and a per-registrant `join_url`; that link is the evidence `T-091` requires
before `granted`, because Zoom staff answered on the developer forum that a
meeting's own join link sends a registrant to the registration page, and a
later thread reports the API's link missing the `tk` token a web registration
carries. Those are forum answers rather than documentation, and `T-099` opens
one in a clean browser before, during and after a session
([thread 16645](https://devforum.zoom.us/t/zoom-join-url-sends-registrant-to-registration-url/16645),
[thread 79979](https://devforum.zoom.us/t/get-join-url-with-registration-token-from-api-call-add-a-meeting-registrant/79979)).
A `201` with no link is acceptance, not usable access, and is not `granted`.

**Zoom never answers two of `VendorGrantStatus`'s eight cases, and a Peer who
cannot join yet is sent to the Series page's notice, which says who resolves
it** (`D-020`). With `approval_type` 0 a registrant is approved as it is
created, so Zoom never answers `awaiting_acceptance`; Zoom needs no Peer vendor
account (`T-092`'s `IdentityProvider::forConnection()` answers null for
`ConnectionProvider::Zoom`), so it never answers `awaiting_identity`. The four
the table in Code produces are `granted`, `pending`, `needs_creator` and
`revoked`; `attempting` is the grant machinery's own transient, and
`revoke_failed` is where a best-effort cancel that did not land ends up. While
a Peer's row is not `granted`, the Series page renders each live Episode's Join
control disabled with `shared.vendor_notice.open_disabled` — `T-091`'s rule,
which the Join control this task adds follows — and `T-089`'s Open sends a
page rendered earlier, or a saved link, back to `shared.show` at `#access` with
`shared.vendor_notice.redirected`. The notice there is `T-091`'s, in
`lang/en/shared.php`, one sentence per state: on `pending` Qori resolves it, and
the sentence names no time, because `D-040` left no scheduled attempt to name —
the Peer's next Open is the next attempt, and `T-091`'s
`shared.vendor_notice.next_attempt.*` lines and its Check again went with the
sweep on 20 September 2026; on `needs_creator` the creator resolves it, and the
sentence says they have been told and nothing more is needed from the Peer, with
no Peer button. Those sentences are `T-091`'s and this task adds none; it relies
on each being true for every Zoom cause in the table in Code, and its tests hold
it to that.

**A reconnect, a different Zoom account and a replaced meeting each have one
answer, and all three run through `T-091`'s ensure step.** Same account
reconnected: the meeting id is still that host's, and every `needs_creator` row
goes `pending` and is tried again. A different Zoom account: a meeting belongs
to the host who scheduled it, so the stored id is unreachable and the container
goes `repick` with the creator told — `T-091`'s `container_repick`, not a Zoom
branch. A meeting replaced by another: `attach()` registers every active Access
on the new one and the old registrants are cancelled best effort. A Peer
confirming an identity triggers nothing here, because Zoom asks for none.

**Replacing a Series' meeting shows what it changes before it is posted**
(`D-021` rule 3). A meeting is replaced from `PickMeeting.vue`, not from the
Series page, so `MeetingController::show()` passes `T-157`'s `containerImpact`
— `VendorAccessService::impactOf()` on the Series' `Active` Zoom container,
local reads only — whenever one exists, and the page opens `T-157`'s
`ContainerChangeDialog` with the meeting wording this task declares (Copy),
before `store` or `repair` is posted: how many Peers with access move to the
new meeting, which live Episodes are sessions of this one, and, as the
dialog's note (`series.container.zoom.change.replace`), that their
registrations on this meeting are cancelled in the creator's Zoom account —
the revoke pass does that — while the meeting itself stays. Nothing reaches
Zoom until the creator confirms. After the replace, `T-091`'s `attach()`
checks each of those Episodes at once, in its replace branch, and
`checkItem()` reports every session whose `meeting_id` is not the new
meeting's as not found, so each carries `missing_since` and the creator's
Series page shows it with `series.episode.zoom.stale` on the page the creator
lands on. Check now cannot clear that flag — the session belongs to a meeting
the Series no longer uses — so the line offers none, and says to add the
session again from the new meeting (see the question below). A reconnect that
returns a different Zoom account is held by `T-044` for the creator to confirm
before `T-091` marks the meeting for re-pick, so that path shows its impact on
`T-044`'s confirmation page. Taking a meeting off a Series without choosing
another is not built here (Out).

**Qori looks the registrant up before every add, without exception.** Zoom
allows three add-registrant calls per registrant per meeting per UTC day, and
three blind adds lock that Peer out until 00:00 GMT
([rate limits](https://developers.zoom.us/docs/api/rate-limits/)). `grant()`
lists registrants by `status=approved`, then `pending`, then `denied` — the list
returns approved only by default — and `POST`s only when the email is absent.
`checkGrant()` uses the same lookup, so `T-091`'s re-check of a `granted` row
costs a read and never an add. The two things that reach Zoom after the first
attempt reach it through this same `grant()`: the Peer's Open, which `D-040`
makes the only moment a grant is attempted, and the creator's Try again now
(`T-157`'s `retryNeedingCreator()`). Both look the registrant up before they
add, so neither can spend an add blindly. Check again and
`VendorAccessService::checkNow()`, which this paragraph named until
20 September 2026, were deleted from `T-091` with `D-040`.

**The Peer's email is their Qori email, and the name is whatever Qori holds.**
Zoom requires `first_name`; Qori sends the Peer's name up to the first space,
the rest as `last_name`, and the email's local part when there is no name. It is
a value handed to a vendor and shown in the creator's Zoom registrant report,
not a sentence anyone reads in Qori, so it takes no lang key (see below).

**Failures split the way `T-091`'s states do, and a full meeting is the
creator's.** The mapping is in Code: 3043, 3161, 3000, 1001/3001 and "registration
not enabled" are `needs_creator`; the three-a-day cap is `pending` until the next
00:00 UTC; a plan rate limit is `pending` with `Retry-After`; a timeout is
`pending` through `VendorAccessService::REQUEST_TIMEOUT_SECONDS`, and the Peer
sees the `pending` sentence and tries again by pressing Open, which is the only
attempt `D-040` leaves — the scheduled `qori:access:reconcile` this sentence
named until 20 September 2026 is gone. A `needs_creator` row reaches the creator
in Zoom's section of the Integrations page, where `T-157`'s Try again now
(`share.settings.integrations.retry`) re-runs it once they have fixed the
meeting or the plan; the Peer is asked for nothing. Every
call here answers in the same response — Zoom's reference shows no long-running
operation to poll on these endpoints — so nothing is left half-done behind an
operation id; `T-099`'s fixtures are what say so rather than the reference.

**Revoke cancels the registrant, best effort.**
`PUT /meetings/{meetingId}/registrants/status` with `action: cancel`. No primary
source says whether a cancelled registrant's `join_url` stops working, or how
fast; the owner's terms make that acceptable and `T-099` records what it sees.

**A refusal is recorded, never thrown, and no paid Series runs on Zoom before
`T-102` and `T-103`.** `T-091`'s ensure step catches everything, so a Zoom
refusal after money has been taken becomes a row and a creator notice while the
Access stands: fulfilment stays replayable, and the grant neither blocks nor
undoes access. The only number that has to be known _before_ a sale is the
ceiling in the capacity question below, which is checked where the plan cap
already is.

**A buyer needs nothing from Zoom, so this task writes no
`accesses.vendor.zoom.before_buying.*` line** (`D-021` rule 1). A registrant
needs no Zoom account, confirms nothing and accepts nothing: Qori registers
their Qori email and name, approval is automatic, and their link comes back in
the same response. `T-092`'s `BuyerRequirements::for()` therefore returns
nothing for a Zoom Series, and nothing renders beside its buy button. The two
things that can still keep a buyer out are the creator's, and are said to the
creator: requiring Zoom sign-in on the meeting (`limits.common.no_account`, an
essential line) and the room size, which is the capacity question below. Zoom's
own emails reach a registrant (`limits.common.emails`), but they ask nothing of
them. If `T-099` finds that a registrant must do something after all, the line
is written then, not guessed now.

**Recordings are a link case with no grant.** A registration grants nothing for
a recording. The creator presses the control labelled
`series.meeting.add_recording` on a past session; Qori reads the host's
recordings, stores that instance's `share_url` and passcode on a new Video
Episode with `EpisodeProvider::Zoom`, and the Peer opens it through `T-089`'s
link route; when Zoom has none yet the answer is
`errors.meeting.no_recording`. Per-Peer recording registrants are rejected here:
registering by meeting id reaches only the latest recording (Zoom staff,
September 2022) and the per-instance workaround is undocumented.

**Webinars, Zoom Events and Webinars Plus are out.** The Webinars add-on mirrors
these endpoints but "register once" on a recurring webinar is unresearched; Zoom
Events registers through a different API whose removal is reported to be
impossible. Neither appears in the tier dropdown.

## Preconditions

`T-044` done, so `ConnectsAccounts`, `ProviderTier`, `lang/en/connections.php`,
the provider sections, reconnect and `qori:connections:refresh` exist; `T-091`
done, so `series_containers`, `vendor_grants`, `GrantsPeerAccess` and the ensure
step exist, `vendor_grants.join_url` among the columns its
`2026_09_20_000100_create_series_containers_and_vendor_grants.php` declares;
`T-157` done, so `VendorAccessService::impactOf()`, the `containerImpact` prop,
`ContainerChangeDialog.vue` and Try again now exist; `T-094` done, so
`qori:episodes:check`, Check now and the `missingSince` prop on the creator's
Series page exist; `T-099` done, so every payload below has a fixture.

**Data this task verifies against:** a clean database, plus a Group with a
chosen timezone — `EpisodeService::add()` calls `guardLiveSessionTime()`
(`app/Services/EpisodeService.php:46`), which refuses a live Episode when the
Group chose none (`:84-91`), as
`tests/Feature/Series/LiveSessionTest.php:47` sets up.

**Equipment:** a Zoom Workplace Pro account with a licensed host and a private
app inside that same account (no Marketplace review for development), one email
with no Zoom account to register as the Peer, and a browser for the join walk.

**Spike:** `T-099` commits every fixture this task reads, under
`tests/Fixtures/zoom/` and in its own `<group>/<call>.<case>.<status>` naming:
`oauth/token.authorization_code.200.json` and `oauth/token.refresh.200.json`;
`meetings/list.200.json` and `meetings/get.200.json` (a `type` 8 meeting with
`occurrences[]`, `recurrence` and `settings`); `meetings/patch.emails_off.*`,
`meetings/patch.add_occurrence.*` and `meetings/get.four_occurrences.200.json`;
`registrants/create.first.*`, `registrants/create.repeat.*`,
`registrants/list.approved.200.json` with its `pending` and `denied` pair, and
`registrants/status.cancel.*`; `recordings/get_meeting.200.json` and
`recordings/list_user.200.json`; and the refusals
`registrants/create.capacity.3043.*`, `create.host_not_allowed.3161.*`,
`create.meeting_missing.1001.*`, `create.no_access.3000.*`,
`create.rate_limited.429.json` and `create.invalid_token.401.json`. `T-099`'s
README records any it could not produce, and a refusal Qori has never seen is
not a branch this task claims to handle. **No field named below has been
observed by Qori.** Every shape comes from Zoom's own reference
([Meetings API](https://developers.zoom.us/docs/api/meetings/),
[api-hub endpoints.json](https://developers.zoom.us/api-hub/meetings/methods/endpoints.json))
and is an expectation until that fixture exists.

## Scope

**In:**

- Zoom OAuth on `T-044`'s machinery, and the tier dropdown with every tier's
  limitations and what Qori recommends, with the `zoom` entry in
  `ProviderSections::ESSENTIAL` and Zoom's `disconnect.in_qori` and
  `account_change.in_qori` lines (`D-021`).
- The meeting picker, the settings check and the one-button repair, with
  `T-157`'s `ContainerChangeDialog` before a meeting is replaced (`D-021`) —
  and this task's declaration of the wording that dialog reads for a meeting:
  `ContainerChangeImpact::kind()`'s `meeting` arm and the four
  `series.container_change.meeting.replace.*` lines, which `T-101` cites.
- The container attach through `VendorAccessService::attach()`, and occurrences
  becoming live Episodes.
- `ZoomMeetings` implementing `GrantsPeerAccess`: lookup, add, cancel, and the
  per-registrant `join_url` on Open.
- The recording Episode, as a stored link and passcode.
- The Peer's Series page and Open for a live Episode; the Join control follows
  `T-091`'s disabled state while the Peer's registration is not `granted`
  (`D-020`).

**Out:**

- The grant machinery, its states and the re-check cadence (`T-091`); connect,
  reconnect and token refresh themselves (`T-044`). The scheduled sweep this
  bullet also excluded no longer exists to exclude (`D-040`, 20 September 2026).
- The Peer notice's sentences (`T-091`); `ContainerChangeDialog` itself and Try
  again now (`T-157`) — this task declares that dialog's meeting lines and
  `kind()`'s `meeting` arm and nothing else of it; the before-buying list
  (`T-092`), for which Zoom has no line. Check again is gone (`D-040`).
- Taking a meeting off a Series without choosing another: a Series' meeting is
  replaced from the picker, never removed here.
- Teams (`T-101`), which stores a pasted link and connects nothing.
- Webinars, Zoom Events, Webinars Plus; per-Peer recording registrants.
- Zoom webhooks (`meeting.updated`, `meeting.deleted`, `recording.completed`)
  and `app_deauthorized`: all need a published app, and the scheduled re-read
  covers the same ground until then.
- Calendar invites, reminders and session notifications (`delivery`).
- Any change to `MediaLink`, the Qori-hosted ticket lifetimes, or Dropbox.

Split: it stays whole because the connector, the container and the grant are one
working journey and none of them ships alone. If it has to be cut, the line is
**Recordings** — a link case with no grant, which becomes its own task behind
this one.

## Files

| Path                                                                                                                                | Change | Notes                                                                                                                                                              |
| ----------------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `app/Integrations/Zoom/ZoomAccounts.php`                                                                                            | new    | `ConnectsAccounts` (`T-044`); `T-141` creates it — see the bullet at the bottom                                                                                    |
| `app/Integrations/Zoom/ZoomMeetings.php`                                                                                            | new    | `GrantsPeerAccess` (`T-091`) and `SchedulesMeetings`; takes `T-141`'s `ZoomClient` by constructor (`D-022`)                                                        |
| `app/Integrations/Contracts/SchedulesMeetings.php`                                                                                  | new    | List, read, repair, extend, recordings                                                                                                                             |
| `app/Data/MeetingSummary.php` `app/Data/MeetingDetail.php` `app/Data/MeetingOccurrence.php` `app/Data/MeetingRecording.php`         | new    | What the picker and the Episode form read                                                                                                                          |
| `app/Data/ContainerChangeImpact.php`                                                                                                | edit   | `kind()`'s `meeting` arm, and nothing else of the class; `T-091` creates it, not in the repo today                                                                 |
| `app/Enums/ProviderTier.php`                                                                                                        | edit   | Five Zoom cases, Basic included; no `supported()` — `T-044` creates the enum, not in the repo                                                                      |
| `app/Support/ProviderSections.php`                                                                                                  | edit   | The `zoom` entry in `ESSENTIAL`; `T-044` creates the class, not in the repo                                                                                        |
| `app/Enums/EpisodeType.php`                                                                                                         | edit   | `Video` gains `EpisodeProvider::Zoom`, for a recording (`:33`)                                                                                                     |
| `app/Services/SeriesMeetingService.php`                                                                                             | new    | Picker, attach, occurrence resolution, recording capture                                                                                                           |
| `app/Services/EpisodeService.php`                                                                                                   | edit   | `add()` takes the resolved occurrence; `guardLiveSessionTime()` is unchanged (`:46`)                                                                               |
| `app/Services/PlaybackTicketService.php`                                                                                            | edit   | The live refusal in `resolve()` (`:85-89`) no longer covers a Zoom Episode                                                                                         |
| `app/Http/Controllers/Share/MeetingController.php` `app/Http/Controllers/Share/RecordingController.php`                             | new    | Picker, `containerImpact` and repair; the recording Episode                                                                                                        |
| `app/Http/Requests/Share/AttachMeetingRequest.php`                                                                                  | new    | Form Requests only                                                                                                                                                 |
| `app/Http/Requests/Share/StoreEpisodeRequest.php`                                                                                   | edit   | `occurrence_id` for a Zoom live Episode; the Zoom branch of `content()` (`:190-195`)                                                                               |
| `app/Http/Controllers/Share/EpisodeController.php`                                                                                  | edit   | `store()` resolves the occurrence before `EpisodeService::add()`                                                                                                   |
| `app/Http/Controllers/Share/SeriesController.php`                                                                                   | edit   | The meeting's state and occurrences on the Series page; `T-094`'s `missingSince` unchanged                                                                         |
| `app/Http/Controllers/Shared/SharedController.php`                                                                                  | edit   | `T-089`'s `opensAs()` returns `tab` for a live Episode with a grant                                                                                                |
| `app/Providers/IntegrationServiceProvider.php`                                                                                      | edit   | `account-connectors`, `grant-providers`, a `meeting-schedulers` tag (`:35-39`)                                                                                     |
| `routes/share/series.php` `routes/share/episodes.php`                                                                               | edit   | The four routes below                                                                                                                                              |
| `resources/js/pages/share/series/PickMeeting.vue`                                                                                   | new    | The picker, the requirements, the repair button, and `T-157`'s `ContainerChangeDialog` before a replace                                                            |
| `resources/js/pages/share/series/Show.vue`                                                                                          | edit   | Live Episodes choose an occurrence; the pasted-link field goes for Zoom (`:236-262`); a Zoom Episode whose `missingSince` is set shows `series.episode.zoom.stale` |
| `resources/js/pages/shared/Show.vue`                                                                                                | edit   | A live Episode gets its Open link and its time (`:195-215`)                                                                                                        |
| `lang/en/connections.php` `lang/en/series.php` `lang/en/accesses.php` `lang/en/errors.php`                                          | edit   | Copy below; `connections.php` is `T-044`'s new file and is not in the repo today                                                                                   |
| `config/services.php` `config/qori.php` `.env.example`                                                                              | edit   | The Zoom client; the caps and room sizes; two env keys                                                                                                             |
| `database/seeders/DesignReviewSeeder.php`                                                                                           | edit   | Its live Episode's Zoom content takes the new shape (`:356`)                                                                                                       |
| `tests/Feature/Integrations/Zoom/ZoomConnectTest.php` `tests/Feature/Integrations/Zoom/ZoomMeetingPickerTest.php`                   | new    | 7 and 10 cases; every file that fakes Zoom sits in `tests/Feature/Integrations/Zoom/`, beside `T-141`'s and `T-142`'s                                              |
| `tests/Feature/Integrations/Zoom/ZoomGrantTest.php` `tests/Feature/Integrations/Zoom/ZoomLiveEpisodeTest.php`                       | new    | 16 and 11 cases                                                                                                                                                    |
| `tests/Feature/Integrations/Zoom/ZoomRecordingTest.php`                                                                             | new    | 5 cases                                                                                                                                                            |
| `tests/Feature/Series/LiveSessionTest.php` `tests/Feature/Series/EpisodeRoutesTest.php` `tests/Feature/Storage/OpenEpisodeTest.php` | edit   | See Tests; `OpenEpisodeTest.php` is `T-089`'s new file                                                                                                             |
| `docs/flows/vendor-access.md`                                                                                                       | edit   | `T-091` creates it, so not in the repo today; this adds the Zoom chain                                                                                             |
| `docs/flows/series.md` `docs/flows/storage.md`                                                                                      | edit   | The live chain (`series.md:127-129`); the providers table (`storage.md:100-104`)                                                                                   |
| `docs/tinker/zoom.md`                                                                                                               | new    | The recipe: connect, pick, register a Peer, open, cancel                                                                                                           |
| `docs/tinker/README.md`                                                                                                             | edit   | One index row for that recipe                                                                                                                                      |

## Database

**None.** The meeting id is `series_containers.external_id` and its settings
snapshot that row's `settings` jsonb; the registrant id is
`vendor_grants.vendor_ref` and the per-Peer link `vendor_grants.join_url` —
all four are `T-091`'s columns, declared in its
`2026_09_20_000100_create_series_containers_and_vendor_grants.php`. `join_url`
is `string(2048)`, nullable, default null, and stays declared exactly once
there although only this task and `T-101` read it: an `ALTER` for a nullable
string on a table the same release creates buys nothing, and a column each
meeting task declares for itself is a column that disappears from every task
at once (stream owner, 20 September 2026). The occurrence id, the meeting id
and a recording's `share_url` and passcode live in `episodes.content`, already
jsonb with an `'array'` cast
(`database/migrations/2026_09_08_000000_create_qori_schema.php:113`,
`app/Models/Episode.php:70`).

## Code

```php
namespace App\Integrations\Contracts;

/**
 * Reading and repairing the meeting a Series hangs off. $timeoutSeconds last, as GrantsPeerAccess takes it: the
 * caller's budget, which the vendor's client may only shorten — it waits the shorter of its own timeout and the
 * budget (D-034).
 */
interface SchedulesMeetings
{
    public function provider(): ConnectionProvider;
    /** @return list<MeetingSummary> — GET /v2/users/me/meetings?type=scheduled */
    public function meetings(Connection $connection, int $timeoutSeconds): array;
    /** GET /v2/meetings/{meetingId} — settings, recurrence and occurrences[] */
    public function meeting(Connection $connection, string $meetingId, int $timeoutSeconds): MeetingDetail;
    /** PATCH /v2/meetings/{meetingId} with only the settings in $issues; returns the re-read meeting. */
    public function repair(Connection $connection, string $meetingId, array $issues, int $timeoutSeconds): MeetingDetail;
    /** PATCH extending recurrence to cover $at; null when Zoom will not produce that time. */
    public function extendTo(Connection $connection, string $meetingId, CarbonInterface $at, int $timeoutSeconds): ?MeetingOccurrence;
    /** @return list<MeetingRecording> — GET /v2/users/me/recordings?from=&to=, filtered to this meeting */
    public function recordings(Connection $connection, string $meetingId, int $timeoutSeconds): array;
}
```

```php
namespace App\Integrations\Zoom;

/**
 * https://developers.zoom.us/docs/api/meetings/ and
 * https://developers.zoom.us/api-hub/meetings/methods/endpoints.json
 * Every response shape here is owed a fixture by T-099. Every call goes through T-141's ZoomClient, the only place
 * a Zoom base URL appears; every $timeoutSeconds is the caller's budget, which ZoomClient may only shorten (D-034).
 */
class ZoomMeetings implements GrantsPeerAccess, SchedulesMeetings
{
    public const MEETING_TYPE_RECURRING_FIXED = 8;   // type
    public const REGISTRATION_ONCE_ALL = 1;          // settings.registration_type
    public const APPROVAL_AUTOMATIC = 0;             // settings.approval_type
    public const ADDS_PER_REGISTRANT_PER_DAY = 3;

    // Container problems, reported in this order; the first four are repairable by PATCH.
    public const ISSUE_REGISTRATION_OFF = 'registration_off';    // settings.approval_type === 2
    public const ISSUE_MANUAL_APPROVAL = 'manual_approval';      // settings.approval_type === 1
    public const ISSUE_PER_OCCURRENCE = 'per_occurrence';        // settings.registration_type !== 1
    public const ISSUE_EMAILS_ON = 'emails_on';                  // registrants_confirmation_email / _email_notification
    public const ISSUE_NOT_RECURRING = 'not_recurring';          // type !== 8
    public const ISSUE_PERSONAL_ID = 'personal_id';              // settings.use_pmi === true
    public const ISSUE_REQUIRED_QUESTION = 'required_question';  // any custom question required
    public const ISSUE_OCCURRENCE_CAP = 'occurrence_cap';        // count(occurrences) >= the config cap

    public function __construct(private ZoomClient $client) {}   // T-141's, in app/Integrations/Zoom (D-022)

    public function provider(): ConnectionProvider;   // ConnectionProvider::Zoom

    /** GET the meeting; exists false with the first issue above as errorCode; url is the meeting's own join_url. */
    public function checkContainer(Connection $connection, string $externalId, int $timeoutSeconds): ContainerCheck;

    /**
     * Lookup, then add. $identity is always null — Zoom needs no Peer account (T-092).
     *   GET  /v2/meetings/{id}/registrants?status=approved|pending|denied&page_size=300
     *   POST /v2/meetings/{id}/registrants  {email, first_name, last_name}
     *        → {id, registrant_id, join_url, start_time, topic, participant_pin_code}
     * granted(registrant_id, join_url) only when join_url is present; a registrant listed pending or
     * denied with no link is needsCreator('zoom_manual_approval').
     */
    public function grant(Connection $connection, SeriesContainer $container, ?GrantIdentity $identity, string $email, int $timeoutSeconds): GrantResult;

    /**
     * The same three lookups by vendor_ref; a registrant Zoom no longer lists is pending(GrantResult::ERROR_PERMISSION_GONE),
     * the code T-091 shares for every provider's checkGrant(), so its verify() falls through to an attempt whose grant()
     * looks the registrant up before any add.
     */
    public function checkGrant(Connection $connection, VendorGrant $grant, int $timeoutSeconds): GrantResult;

    /** PUT /v2/meetings/{id}/registrants/status {action: 'cancel', registrants: [{id: vendor_ref}]} */
    public function revoke(Connection $connection, VendorGrant $grant, int $timeoutSeconds): RevokeResult;

    /** The grant's own join_url, never the meeting's; no vendor call. */
    public function openLink(Connection $connection, Episode $episode, ?VendorGrant $grant, int $timeoutSeconds): VendorLink;

    /**
     * The occurrence still exists on the Series' current meeting and is not deleted; read from that meeting, one
     * call. An Episode whose content meeting_id is another meeting's — every session after a replace — is not found.
     * What T-091's VendorAccessService::checkEpisode() and T-094's checkItems() loop call (D-021); nothing more is needed here.
     */
    public function checkItem(Connection $connection, Episode $episode, int $timeoutSeconds): ItemCheck;
}
```

| Zoom answer                             | `GrantResult`                                | `last_error_code`           |
| --------------------------------------- | -------------------------------------------- | --------------------------- |
| `201` with `join_url`                   | `granted()`                                  | cleared                     |
| `400` `3043` meeting at capacity        | `needsCreator()`                             | `zoom_capacity`             |
| `400` `3161` host cannot host           | `needsCreator()`                             | `zoom_host_unlicensed`      |
| `400` `3000` cannot access meeting info | `needsCreator()`                             | `zoom_meeting_unreadable`   |
| `404` `1001` / `3001` meeting gone      | `needsCreator()`, container marked `missing` | `zoom_meeting_missing`      |
| `404` registration not enabled          | `needsCreator()`                             | `zoom_registration_off`     |
| `429` three-a-day for this registrant   | `pending()`, next attempt at 00:00 UTC       | `zoom_registrant_daily_cap` |
| `429` plan rate limit                   | `pending()` with `Retry-After`               | `zoom_rate_limited`         |
| `401` invalid access token              | `needsCreator()` after `markForReconnect()`  | `connection_unusable`       |
| Timeout or transport failure            | `pending()`                                  | `timeout`                   |

```php
namespace App\Integrations\Zoom;

/** https://developers.zoom.us/docs/integrations/oauth/ and .../oauth-scopes-granular/ */
class ZoomAccounts implements ConnectsAccounts
{
    public const AUTHORIZE_URL = 'https://zoom.us/oauth/authorize';
    public const TOKEN_URL = 'https://zoom.us/oauth/token';   // Basic auth: client_id:client_secret
    public const REVOKE_URL = 'https://zoom.us/oauth/revoke';
    public const ME_URL = 'https://api.zoom.us/v2/users/me';
    /**
     * No offline scope exists; the refresh token lasts 90 days and rotates on every use.
     * This list is submitted once: adding a scope later triggers a complete security
     * re-review (KB0058021), so the Marketplace question below settles it before launch.
     */
    public const SCOPES = [
        'meeting:read:list_meetings', 'meeting:read:meeting', 'meeting:update:meeting',
        'meeting:write:registrant', 'meeting:read:list_registrants', 'meeting:update:registrant_status',
        'meeting:delete:registrant', 'cloud_recording:read:list_user_recordings',
        'cloud_recording:read:list_recording_files',
    ];
    // refreshesOnSchedule(): true — qori:connections:refresh keeps the 90 days from lapsing, one
    // connection at a time under T-044's AdvisoryLock, because two refreshes at once invalidate one.
    // supportsPkce(): true (provisional); identity(): GET ME_URL → id, email, display_name, account_id.
}
```

```php
namespace App\Services;

/**
 * The Series' meeting: picking it, attaching it, and resolving an Episode's occurrence on it. Not
 * App\Services\LiveSessionService, which exists already and is the live Episode's own write path and state (D-026).
 */
class SeriesMeetingService
{
    /** @param iterable<SchedulesMeetings> $schedulers */
    public function __construct(
        private iterable $schedulers,
        private VendorAccessService $vendorAccess,
        private ConnectionService $connections,
        private CurrentGroup $current,
    ) {}

    /** @return list<MeetingSummary> for the picker; refuses when nothing is connected. */
    public function meetingsFor(Group $group, ConnectionProvider $provider): array;
    /** checkContainer, then VendorAccessService::attach(); throws errors.meeting.* for the issue found. */
    public function attach(Series $series, ConnectionProvider $provider, string $meetingId): SeriesContainer;
    /** repair() for the repairable issues the creator agreed to, then attach(). */
    public function repair(Series $series, array $issues): SeriesContainer;
    /** @return list<MeetingOccurrence> the Episode form offers, in time order, future first. */
    public function occurrencesFor(Series $series): array;
    /**
     * The occurrence an Episode points at: matched by occurrence_id, else by instant, else extendTo().
     * Null is errors.series.session_not_an_occurrence — the creator adds the session in Zoom.
     */
    public function occurrenceFor(Series $series, ?string $occurrenceId, CarbonInterface $startsAt): ?MeetingOccurrence;
    /** The recording of a past occurrence as a new Video Episode; null when Zoom has none yet. */
    public function captureRecording(Series $series, Episode $session): ?Episode;
}
```

`EpisodeController::store()` calls `occurrenceFor()` before
`EpisodeService::add()` and merges `meeting_id`, `occurrence_id` and `starts_at`
into the content; `StoreEpisodeRequest::content()`'s Zoom branch (`:190-195`)
drops `join_url` and carries `occurrence_id` instead. Teams keeps the pasted
link until `T-101`.

```php
// config/services.php
'zoom' => ['client_id' => env('ZOOM_CLIENT_ID'), 'client_secret' => env('ZOOM_CLIENT_SECRET')],

// config/qori.php — connections.zoom; every number the copy interpolates lives here, not in a sentence
'zoom' => [
    'occurrence_cap' => 60,
    'registrants_per_occurrence' => 4999,
    'idle_days' => 365,
    'adds_per_registrant_per_day' => 3,
    // Business Plus is the one figure Zoom does not publish; 300 is the Business number
    // standing in until T-099's account shows otherwise, and the copy reads from here.
    'room_size' => ['zoom_pro' => 100, 'zoom_business' => 300, 'zoom_business_plus' => 300, 'zoom_enterprise' => 500],
    'recording_gigabytes' => ['zoom_pro' => 10, 'zoom_business' => 10, 'zoom_business_plus' => 15],
],
```

```php
// app/Support/ProviderSections.php — T-044's ESSENTIAL; this entry is this task's (D-021 rule 4). Keys are relative
// to connections.providers.zoom.limits., in order: what a Peer needs, what stops Qori registering anyone, the
// one-meeting rule. Every other limits line is in `more`.
'zoom' => [
    'zoom_basic' => ['common.no_account', 'zoom_basic.registration', 'common.one_meeting'],
    'zoom_pro' => ['common.no_account', 'common.breaks', 'common.one_meeting'],
    'zoom_business' => ['common.no_account', 'common.breaks', 'common.one_meeting'],
    'zoom_business_plus' => ['common.no_account', 'common.breaks', 'common.one_meeting'],
    'zoom_enterprise' => ['common.no_account', 'common.breaks', 'common.one_meeting'],
],
```

`MeetingController::show()` renders `share/series/PickMeeting` with the
meetings, the requirements and, when the Series already has an `Active` Zoom
container, `containerImpact` from `VendorAccessService::impactOf()` (`T-157`);
`PickMeeting.vue` opens `ContainerChangeDialog` with it before posting `store`
or `repair`, and posts straight away when there is none. `store()` and
`repair()` call `SeriesMeetingService::attach()`, which replaces an existing
container through `VendorAccessService::attach()`, whose replace branch calls
`checkEpisode()` on each affected Episode once the write has committed
(`T-091`). The `containerImpact` entry is built in `T-157`'s shape; what this
task declares is what the entry says for a meeting — `kind()`'s `meeting` arm
below, the four `series.container_change.meeting.replace.*` lines in Copy, and
`series.container.zoom.change.replace` as the replace `note`.

```php
namespace App\Data;

/**
 * T-091's class and T-091's signature; this task declares one arm of it (amended 20 September 2026, from the cut of
 * T-091). kind() is the switch that makes ContainerChangeDialog read series.container_change.meeting.* rather than
 * .folder.*. T-101 builds no second arm: Teams is a meeting too, and reads this one.
 */
class ContainerChangeImpact
{
    public function kind(): string;   // 'meeting' for ConnectionProvider::Zoom and ::Teams, 'folder' for the rest
}
```

## Copy

| Key                                                               | File                      | English                                                                                                                                                                                                                                                                                                                                 |
| ----------------------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `connections.providers.zoom.name`                                 | `lang/en/connections.php` | Zoom                                                                                                                                                                                                                                                                                                                                    |
| `connections.providers.zoom.description`                          | `lang/en/connections.php` | Run live sessions from your own Zoom account. Everyone with access is registered for you.                                                                                                                                                                                                                                               |
| `connections.providers.zoom.tiers.zoom_basic.label`               | `lang/en/connections.php` | Zoom Workplace Basic (free)                                                                                                                                                                                                                                                                                                             |
| `connections.providers.zoom.tiers.zoom_basic.help`                | `lang/en/connections.php` | Zoom's free plan, with no paid licence.                                                                                                                                                                                                                                                                                                 |
| `connections.providers.zoom.tiers.zoom_basic.recommended`         | `lang/en/connections.php` | We recommend Zoom Workplace Pro or higher: it's the lowest plan where Qori can register everyone with access for you. Upgrade before your first live :episode.                                                                                                                                                                          |
| `connections.providers.zoom.limits.zoom_basic.registration`       | `lang/en/connections.php` | Zoom Workplace Basic has no registration and no cloud recording, so Qori can't add anyone to your sessions. A live :episode needs Pro or higher.                                                                                                                                                                                        |
| `connections.providers.zoom.tiers.zoom_pro.label`                 | `lang/en/connections.php` | Zoom Workplace Pro                                                                                                                                                                                                                                                                                                                      |
| `connections.providers.zoom.tiers.zoom_pro.help`                  | `lang/en/connections.php` | Up to :people people in a session at once, and up to :registrants registered. Recordings share :gigabytes GB per licence.                                                                                                                                                                                                               |
| `connections.providers.zoom.tiers.zoom_pro.recommended`           | `lang/en/connections.php` | Pick one recurring meeting with a fixed time for each :series. If its registration settings aren't what Qori needs, Qori offers to change them for you.                                                                                                                                                                                 |
| `connections.providers.zoom.tiers.zoom_business.label`            | `lang/en/connections.php` | Zoom Workplace Business                                                                                                                                                                                                                                                                                                                 |
| `connections.providers.zoom.tiers.zoom_business.help`             | `lang/en/connections.php` | Up to :people people in a session at once. Recordings share :gigabytes GB per licence. Your admin may have locked settings Qori needs.                                                                                                                                                                                                  |
| `connections.providers.zoom.tiers.zoom_business.recommended`      | `lang/en/connections.php` | Before you connect, check with your Zoom admin that registration isn't locked off for your meetings, so Qori can register everyone with access for you.                                                                                                                                                                                 |
| `connections.providers.zoom.tiers.zoom_business_plus.label`       | `lang/en/connections.php` | Zoom Workplace Business Plus                                                                                                                                                                                                                                                                                                            |
| `connections.providers.zoom.tiers.zoom_business_plus.help`        | `lang/en/connections.php` | Up to :people people in a session at once. Recordings share :gigabytes GB per licence. Your admin may have locked settings Qori needs.                                                                                                                                                                                                  |
| `connections.providers.zoom.tiers.zoom_business_plus.recommended` | `lang/en/connections.php` | Before you connect, check with your Zoom admin that registration isn't locked off for your meetings, so Qori can register everyone with access for you.                                                                                                                                                                                 |
| `connections.providers.zoom.tiers.zoom_enterprise.label`          | `lang/en/connections.php` | Zoom Workplace Enterprise                                                                                                                                                                                                                                                                                                               |
| `connections.providers.zoom.tiers.zoom_enterprise.help`           | `lang/en/connections.php` | Up to :people people in a session at once, and cloud recording storage is unlimited. Your admin may have locked settings Qori needs.                                                                                                                                                                                                    |
| `connections.providers.zoom.tiers.zoom_enterprise.recommended`    | `lang/en/connections.php` | Before you connect, check with your Zoom admin that registration isn't locked off for your meetings, so Qori can register everyone with access for you.                                                                                                                                                                                 |
| `connections.providers.zoom.limits.common.no_account`             | `lang/en/connections.php` | People don't need a Zoom account. If you require Zoom sign-in, people without an account can't join.                                                                                                                                                                                                                                    |
| `connections.providers.zoom.limits.common.breaks`                 | `lang/en/connections.php` | Making a new meeting, switching to no fixed time, turning registration off or making a registration question required cuts everyone off.                                                                                                                                                                                                |
| `connections.providers.zoom.limits.common.one_meeting`            | `lang/en/connections.php` | Use one recurring meeting with a fixed time for each :series, and add every session to that same meeting.                                                                                                                                                                                                                               |
| `connections.providers.zoom.limits.common.occurrence_cap`         | `lang/en/connections.php` | One meeting holds up to :sessions sessions. After that you need a new meeting, and Qori registers everyone again.                                                                                                                                                                                                                       |
| `connections.providers.zoom.limits.common.idle`                   | `lang/en/connections.php` | The meeting stops working if no session is started for :days days.                                                                                                                                                                                                                                                                      |
| `connections.providers.zoom.limits.common.waiting_room`           | `lang/en/connections.php` | If the waiting room is on, people can only get in once you're there to admit them.                                                                                                                                                                                                                                                      |
| `connections.providers.zoom.limits.common.emails`                 | `lang/en/connections.php` | Zoom sends its own emails when you change the meeting.                                                                                                                                                                                                                                                                                  |
| `connections.providers.zoom.limits.common.recordings`             | `lang/en/connections.php` | Only recordings saved to Zoom's cloud can be shared. Don't set an expiry or auto-delete on one you share, and don't change who it's shared with.                                                                                                                                                                                        |
| `connections.providers.zoom.limits.common.admin`                  | `lang/en/connections.php` | Accounts with more than one user may need a Zoom admin to approve Qori before you can connect.                                                                                                                                                                                                                                          |
| `connections.meeting.title`                                       | `lang/en/connections.php` | Choose the meeting this :series runs on                                                                                                                                                                                                                                                                                                 |
| `connections.meeting.intro`                                       | `lang/en/connections.php` | Pick one recurring meeting with a fixed time. Each session of this :series is one of its occurrences.                                                                                                                                                                                                                                   |
| `connections.meeting.shares_everything`                           | `lang/en/connections.php` | Everyone with access to this :series is registered for every session on this meeting, whether or not you list it here. Use a meeting nothing else needs.                                                                                                                                                                                |
| `connections.meeting.requirements`                                | `lang/en/connections.php` | Qori needs registration on, set to register once for every session, approved automatically.                                                                                                                                                                                                                                             |
| `connections.meeting.repair`                                      | `lang/en/connections.php` | Let Qori change these settings                                                                                                                                                                                                                                                                                                          |
| `connections.meeting.repaired`                                    | `lang/en/connections.php` | Settings changed in Zoom, and this :series now runs on that meeting.                                                                                                                                                                                                                                                                    |
| `connections.meeting.none`                                        | `lang/en/connections.php` | No recurring meetings with a fixed time in this account yet. Schedule one in Zoom, then come back.                                                                                                                                                                                                                                      |
| `connections.grants.reasons.zoom_capacity`                        | `lang/en/connections.php` | the meeting is full, so nobody else can be registered for it                                                                                                                                                                                                                                                                            |
| `connections.grants.reasons.zoom_host_unlicensed`                 | `lang/en/connections.php` | the Zoom account doesn't have a licence that allows registration                                                                                                                                                                                                                                                                        |
| `connections.grants.reasons.zoom_meeting_missing`                 | `lang/en/connections.php` | that meeting no longer exists in Zoom; pick another one                                                                                                                                                                                                                                                                                 |
| `connections.grants.reasons.zoom_registration_off`                | `lang/en/connections.php` | registration is off on that meeting; turn it back on in Zoom, then press Try again now                                                                                                                                                                                                                                                  |
| `series.meeting.chosen`                                           | `lang/en/series.php`      | This :series now runs on that meeting.                                                                                                                                                                                                                                                                                                  |
| `series.meeting.session_added`                                    | `lang/en/series.php`      | :title is on the meeting, and everyone with access is registered for it.                                                                                                                                                                                                                                                                |
| `series.container_change.meeting.replace.title`                   | `lang/en/series.php`      | Change the meeting this :series runs on                                                                                                                                                                                                                                                                                                 |
| `series.container_change.meeting.replace.peers`                   | `lang/en/series.php`      | :count :peer_plural with access are registered on that meeting. Qori registers them on the meeting you pick and stops sending them to the old one.                                                                                                                                                                                      |
| `series.container_change.meeting.replace.episodes`                | `lang/en/series.php`      | :count :episode_plural are sessions of that meeting. Nobody can join them from Qori until you add each one again from the meeting you pick.                                                                                                                                                                                             |
| `series.container_change.meeting.replace.confirm`                 | `lang/en/series.php`      | Change the meeting                                                                                                                                                                                                                                                                                                                      |
| `series.container.zoom.change.replace`                            | `lang/en/series.php`      | In Zoom, their registrations on this meeting are cancelled. The meeting itself stays in your account.                                                                                                                                                                                                                                   |
| `series.episode.zoom.stale`                                       | `lang/en/series.php`      | This session belongs to the meeting this :series used before, so nobody can join it from Qori. Add it again from the new meeting.                                                                                                                                                                                                       |
| `connections.providers.zoom.disconnect.in_qori`                   | `lang/en/connections.php` | :peer_plural already registered stay registered for your meetings in Zoom and keep joining from Qori with their own links. Nobody new is registered, and anyone whose access ends in the meantime stays registered, until you connect :account again: then Qori registers everyone waiting and cancels those registrations.             |
| `connections.providers.zoom.account_change.in_qori`               | `lang/en/connections.php` | :peer_plural already registered stay registered for your meetings in :current until you cancel them there; once you switch, Qori can't reach :current to do it for you. Their live :episode_plural stop opening from Qori at their next check, until a meeting from :incoming is picked for each :series and Qori registers them on it. |
| `series.meeting.add_recording`                                    | `lang/en/series.php`      | Add the recording                                                                                                                                                                                                                                                                                                                       |
| `series.meeting.recording_added`                                  | `lang/en/series.php`      | The recording of :title is now :episode :position.                                                                                                                                                                                                                                                                                      |
| `accesses.live.join`                                              | `lang/en/accesses.php`    | Join the session                                                                                                                                                                                                                                                                                                                        |
| `accesses.live.no_account_needed`                                 | `lang/en/accesses.php`    | You don't need a Zoom account. Open the session from here when it starts.                                                                                                                                                                                                                                                               |
| `accesses.live.cancelled`                                         | `lang/en/accesses.php`    | This session was cancelled.                                                                                                                                                                                                                                                                                                             |
| `accesses.live.recording_passcode`                                | `lang/en/accesses.php`    | Passcode for this recording: :passcode                                                                                                                                                                                                                                                                                                  |
| `errors.meeting.not_recurring.message`                            | `lang/en/errors.php`      | That meeting only happens once.                                                                                                                                                                                                                                                                                                         |
| `errors.meeting.not_recurring.resolution`                         | `lang/en/errors.php`      | Pick a recurring meeting with a fixed time, so every session of this :series lives on one meeting.                                                                                                                                                                                                                                      |
| `errors.meeting.personal_id.message`                              | `lang/en/errors.php`      | That meeting uses your personal meeting room.                                                                                                                                                                                                                                                                                           |
| `errors.meeting.personal_id.resolution`                           | `lang/en/errors.php`      | Schedule a meeting with its own ID in Zoom, then pick that one.                                                                                                                                                                                                                                                                         |
| `errors.meeting.required_question.message`                        | `lang/en/errors.php`      | That meeting asks a required question when people register.                                                                                                                                                                                                                                                                             |
| `errors.meeting.required_question.resolution`                     | `lang/en/errors.php`      | Make the question optional in Zoom, so Qori can register people for you.                                                                                                                                                                                                                                                                |
| `errors.meeting.occurrence_cap.message`                           | `lang/en/errors.php`      | That meeting already holds :sessions sessions, which is as many as Zoom allows.                                                                                                                                                                                                                                                         |
| `errors.meeting.occurrence_cap.resolution`                        | `lang/en/errors.php`      | Schedule a new meeting for the sessions after these, and pick it for a new :series.                                                                                                                                                                                                                                                     |
| `errors.meeting.full.message`                                     | `lang/en/errors.php`      | This :series is full: :people people can be in the session at once.                                                                                                                                                                                                                                                                     |
| `errors.series.session_not_an_occurrence.message`                 | `lang/en/errors.php`      | That time isn't one of the meeting's sessions.                                                                                                                                                                                                                                                                                          |
| `errors.series.session_not_an_occurrence.resolution`              | `lang/en/errors.php`      | Add the session to the meeting in Zoom, then pick it here.                                                                                                                                                                                                                                                                              |
| `errors.meeting.no_recording.message`                             | `lang/en/errors.php`      | Zoom has no recording of that session yet.                                                                                                                                                                                                                                                                                              |
| `errors.meeting.no_recording.resolution`                          | `lang/en/errors.php`      | A cloud recording can take a while to appear after a session ends. Try again later.                                                                                                                                                                                                                                                     |

`errors.meeting.full` carries no `resolution` on purpose: for the buyer the
path is final until the creator's Zoom plan changes. Every number in these
lines is interpolated from `config('qori.connections.zoom')`, never written
into the sentence. `series.session_scheduled` (`lang/en/series.php:38`) still
says the hour back for a live Episode; `series.meeting.session_added` follows
it when the Series runs on a meeting. The sentences a Peer reads for a
`pending` or `needs_creator` grant are `T-091`'s
`shared.vendor_notice.reasons.*`, in `lang/en/shared.php` (`D-020`), with its
`open_disabled` and `redirected` lines; this task adds none, and the
`check_again` line this paragraph named until 20 September 2026 went with
`D-040`. The replace dialog's four meeting sentences are **this task's**, in
the table above: they say only what Qori stops doing, because the two vendors
do opposite things when the meeting changes — Zoom cancels the old
registrants, Teams tells Microsoft nothing — and the fact true of Zoom alone
rides in this task's `series.container.zoom.change.replace`, which the dialog
shows beneath them. `T-101` reads `.title` and `.confirm` from here and writes
no meeting line of its own. The dialog itself and Try again now
(`connections.grants.retry`) are `T-157`'s. `series.episode.zoom.stale` is the
flag a replace leaves on each old session; `T-094`'s `missingSince` prop
carries it, and this task reads it as `T-094` passes it. `disconnect.in_qori`
and `account_change.in_qori` are the two lines `T-044` asks of every
connectable provider (`D-021` rule 3), written from `T-091`'s rules for a
connection that is not live and from `openLink()`, which reads the stored
`join_url` and makes no call. There is no
`accesses.vendor.zoom.before_buying.*` line, because a registrant is asked for
nothing (see Decisions). Vendor names appear here under `D-016`'s stated
exception for provider-choice and Peer-prerequisite copy. Every tier carries a
`recommended` line and its limitation lines, in `T-044`'s key shape; which of
them sit above the disclosure is `ProviderSections::ESSENTIAL` (Code), not a
flag in this table. No tier line refuses a connection (`D-018`).
`zoom_basic.recommended` says "Upgrade before your first live :episode" rather
than "don't connect": Basic connects, and the limitation beside it says why
nothing will register until it is upgraded.

## Routes

| Verb | Path                                                         | Name                              | Action                     |
| ---- | ------------------------------------------------------------ | --------------------------------- | -------------------------- |
| GET  | `g/{group}/series/{series}/meeting`                          | `share.series.meeting.show`       | `MeetingController@show`   |
| POST | `g/{group}/series/{seriesId}/meeting`                        | `share.series.meeting.store`      | `MeetingController@store`  |
| POST | `g/{group}/series/{seriesId}/meeting/repair`                 | `share.series.meeting.repair`     | `MeetingController@repair` |
| POST | `g/{group}/series/{seriesId}/episodes/{episodeId}/recording` | `share.series.episodes.recording` | `RecordingController`      |

A slug on the page, ids on the writes (`routes/share/episodes.php:11-16`). The
first three sit in `routes/share/series.php`, the fourth in
`routes/share/episodes.php`, both inside the `g/{group}` `share.` group
(`routes/share.php:24-33`). The Peer needs no new route — Open is `T-089`'s
`shared.episodes.open` — and the connect routes are `T-044`'s.

## Tests

`Http::fake()` with the `T-099` fixtures in every case, and
`Http::preventStrayRequests()` in `setUp()`.

**New: `tests/Feature/Integrations/Zoom/ZoomConnectTest.php` — 7 cases**

1. `test_the_authorize_url_asks_for_every_scope_qori_needs`
2. `test_connecting_stores_the_account_and_its_tier`
3. `test_the_basic_tier_is_offered_with_its_limitation_and_still_connects`
4. `test_each_zoom_tier_puts_what_a_peer_needs_first_among_its_essential_lines` —
   `providers.zoom` on the Integrations page: `zoom_basic`'s `essential` is
   `no_account`, `registration`, `one_meeting` in that order, `zoom_pro`'s has
   `breaks` where Basic has `registration`, every tier has a `recommended`
   sentence, and `more` holds the rest (`D-018`, `D-021`)
5. `test_a_refresh_stores_the_rotated_refresh_token`
6. `test_an_invalid_grant_marks_the_connection_for_reconnect`
7. `test_only_the_group_owner_can_connect_zoom`

**New: `tests/Feature/Integrations/Zoom/ZoomMeetingPickerTest.php` — 10 cases**

8. `test_the_picker_lists_only_recurring_fixed_time_meetings`
9. `test_choosing_a_meeting_attaches_it_as_the_series_container`
10. `test_a_meeting_with_registration_off_is_refused_with_the_repairable_issue`
11. `test_repair_patches_only_the_settings_the_creator_agreed_to`
12. `test_a_personal_meeting_id_is_refused_and_is_not_repairable`
13. `test_a_required_registration_question_is_refused`
14. `test_a_meeting_at_the_occurrence_cap_is_refused`
15. `test_a_meeting_another_series_holds_is_refused` — `T-091`'s
    `errors.container.in_use`
16. `test_attaching_creates_a_pending_grant_for_every_active_access`
17. `test_the_picker_carries_what_replacing_the_meeting_changes` — a Series on a
    meeting, with two active Accesses and two sessions: `containerImpact` has
    provider `zoom`, `kind` `meeting`, `peers` 2, both Episodes,
    `copy.replace.title` `series.container_change.meeting.replace.title` and
    `copy.replace.note` `series.container.zoom.change.replace`; a Series with no
    meeting gets none; no request reaches Zoom until `store` is posted
    (`D-021`). `T-091`'s case 60 and the Zoom half of its case 28 were folded
    into this case on 20 September 2026 rather than added as cases of their
    own, because it already asserts the same entry; the `kind` and
    `copy.replace.title` clauses are what they contributed, and the totals
    below are unchanged

**New: `tests/Feature/Integrations/Zoom/ZoomGrantTest.php` — 16 cases**

18. `test_a_new_access_is_registered_and_its_join_url_is_stored`
19. `test_an_existing_registrant_is_found_before_any_add_is_attempted`
20. `test_a_repeat_ensure_makes_no_second_add_call`
21. `test_a_registrant_with_no_join_url_is_not_granted`
22. `test_the_daily_registrant_cap_waits_until_the_next_utc_midnight`
23. `test_a_plan_rate_limit_honours_retry_after`
24. `test_a_full_meeting_needs_the_creator`
25. `test_an_unlicensed_host_needs_the_creator`
26. `test_a_meeting_zoom_no_longer_has_marks_the_container_missing`
27. `test_a_timeout_leaves_the_grant_pending`
28. `test_revoking_an_access_cancels_the_registrant`
29. `test_a_recheck_of_a_granted_row_reads_the_registrant_list_and_adds_nothing`
30. `test_reconnecting_the_same_zoom_account_retries_a_needs_creator_row`
31. `test_connecting_a_different_zoom_account_sends_the_meeting_back_to_be_picked`
32. `test_open_on_a_row_held_by_the_daily_cap_never_spends_a_blind_add` — a row
    `pending` on `zoom_registrant_daily_cap`: pressing `shared.episodes.open`
    returns to `shared.show` at `#access` with
    `shared.vendor_notice.redirected`, and whatever attempt `T-091`'s Open path
    makes, `ZoomMeetings::grant()` lists registrants before any `POST`, so no
    add is spent blindly before the next 00:00 UTC. Rewritten 20 September 2026
    from `test_check_again_before_the_daily_cap_resets_makes_no_zoom_call`,
    which posted to the deleted `shared.access.check`; the number is kept and
    is not reused
33. `test_the_creators_retry_looks_each_registrant_up_before_adding` — a
    `needs_creator` row on `zoom_registration_off`: `T-157`'s Try again now
    (`share.settings.integrations.retry`, `retryNeedingCreator()`) for `zoom`
    lists registrants first and adds only an email Zoom does not hold.
    Re-attributed and renamed 20 September 2026: the control, its route and its
    copy are `T-157`'s, not `T-091`'s

**New: `tests/Feature/Integrations/Zoom/ZoomLiveEpisodeTest.php` — 11 cases**

34. `test_a_live_episode_takes_an_occurrence_of_the_series_meeting`
35. `test_a_time_the_meeting_does_not_hold_extends_the_recurrence`
36. `test_a_time_zoom_will_not_produce_is_refused_with_a_readable_error`
37. `test_the_episode_form_offers_the_meetings_occurrences`
38. `test_the_group_timezone_still_decides_what_the_hour_means` — `T-029`
39. `test_a_peer_opens_a_live_episode_at_their_own_join_url`
40. `test_a_peer_whose_grant_is_pending_sees_the_notice_and_no_join_link` —
    `vendor.state` `pending`; the notice is
    `shared.vendor_notice.reasons.pending` and promises no time, because
    `D-040` leaves no scheduled attempt to name; each live Episode's Join
    control is disabled with `shared.vendor_notice.open_disabled`; no
    `join_url` in the props (`D-020`). Rewritten 20 September 2026 from
    `test_a_peer_whose_grant_is_pending_sees_when_qori_tries_next_and_no_join_link`,
    which asserted the deleted `shared.vendor_notice.next_attempt.*` lines
41. `test_a_cancelled_occurrence_is_shown_as_cancelled_on_the_peers_page`
42. `test_open_on_a_zoom_grant_that_is_not_granted_returns_to_the_series_notice`
    — `shared.episodes.open` on a `needs_creator` row redirects to `shared.show`
    at `#access` with `shared.vendor_notice.redirected`; no request to Zoom
43. `test_a_needs_creator_zoom_grant_asks_nothing_of_the_peer` — the notice is
    `shared.vendor_notice.reasons.needs_creator` and offers the Peer no control
    at all; the Check again whose absence this case used to assert was deleted
    on 20 September 2026 (`D-040`), so the assertion is now that the notice
    renders and nothing beside it does
44. `test_replacing_the_meeting_flags_every_session_of_the_old_one` — after
    `store` with another meeting, `checkItem()` answers not found for each
    Episode whose `meeting_id` is the old meeting's, so each carries
    `missing_since` and the creator's Series page shows
    `series.episode.zoom.stale` on it with no Check now

**New: `tests/Feature/Integrations/Zoom/ZoomRecordingTest.php` — 5 cases**

45. `test_the_recording_of_a_past_session_becomes_a_video_episode`
46. `test_the_share_url_and_passcode_are_stored_on_the_episode`
47. `test_a_peer_opens_the_recording_through_the_shared_open_route`
48. `test_a_session_with_no_recording_yet_says_so`
49. `test_a_registration_does_not_grant_the_recording` — no registrant call is
    made for a recording Episode

Total new: 49 — 7, 10, 16, 11 and 5, recounted from the numbered cases on
20 September 2026 and unchanged by that pass. Cases 32, 33, 40 and 43 were
rewritten in place rather than retired, so every number still names a case; a
number is never reused.

**Changed:**

- `tests/Feature/Storage/OpenEpisodeTest.php` — `T-089`'s case 8,
  `test_a_live_episode_cannot_be_opened`, becomes
  `test_a_live_episode_without_a_grant_cannot_be_opened`: a Zoom Episode with a
  granted row redirects now.
- `tests/Feature/Series/LiveSessionTest.php` — its Zoom cases need a connection
  and a container, and the pasted-link assertions go.
- `tests/Feature/Series/EpisodeRoutesTest.php` — the same setup for its live
  posts.
- `T-044`'s test that every `ProviderSections::ESSENTIAL` key exists and no tier
  lists more than `MAX_ESSENTIAL` runs over the `zoom` entry with no new case.

## Acceptance

- [ ] A creator connects Zoom from the Integrations page having read, before
      connecting, what their tier cannot do and what Qori recommends; a Basic
      account connects too, told that registration is not part of that plan
- [ ] Each Zoom tier shows its recommendation and at most `MAX_ESSENTIAL`
      essential lines above Connect — that nobody needs a Zoom account among
      them — with every other line in the disclosure in the same section
- [ ] A Series is pointed at one recurring fixed-time meeting; a meeting with
      the wrong settings names what is wrong, and one click repairs the four
      repairable ones
- [ ] Every Peer with access is registered exactly once per Series, no add call
      is ever made without a lookup first, and Open sends each Peer to their own
      `join_url`
- [ ] One Peer, in a clean browser with no Zoom account, reaches two successive
      sessions of the same meeting from the same stored registration, and a
      session added after they got access is one of them
- [ ] A rescheduled or cancelled occurrence is shown as such rather than as a
      link that does nothing
- [ ] A capacity, licence or missing-meeting refusal reaches the creator on the
      Integrations page, where Try again now re-runs it without a blind add, and
      the Peer sees the Series page's notice saying the creator has been told,
      never a dead page or a Join control that does nothing
- [ ] A Peer held by Zoom's three-a-day cap reads that Qori is resolving it and
      is promised no time Qori cannot keep, and no press of Open before
      00:00 UTC costs an add, because the registrant lookup comes first
- [ ] Replacing a Series' meeting shows how many Peers are moved and which
      sessions need pointing at the new meeting before anything is posted, and
      the Series page the creator lands on flags those sessions
- [ ] A granted row is re-checked by reading the registrant list, and a
      reconnect of the same Zoom account or a connect of a different one each
      end in the state this task specifies
- [ ] The recording of a past session opens for a Peer with access, and no
      registration is claimed to cover it
- [ ] `docs/flows/vendor-access.md`, `series.md`, `storage.md` and the tinker
      recipe describe what was built
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Whether Zoom enters before beta at all: the open decision in `decisions.md`
  ("which integrations enter before beta") leaves it after the storage journey
  unless a representative creator runs live sessions — the owner's.~~
  **Answered 17 September 2026 (`D-018`):** all seven providers ship before
  beta, Zoom among them. The `storage` stream's order is the order they are
  built in, not a shortlist.
- What a Basic connection meets at the picker, now that it is offered rather
  than refused: registration needs a licensed host (KB0065026 above), so the
  repair `PATCH` that turns registration on is expected to be refused on that
  plan, and with which code is unobserved — `T-099`'s. Until it answers, the
  meeting is simply never attached and the picker keeps showing
  `connections.meeting.requirements`, which is what Basic's essential
  `limits.zoom_basic.registration` line warned about before the creator
  connected.
- Who submits the Zoom Marketplace app and whether unlisted after review is the
  target; creators outside Qori's own Zoom account cannot connect until it
  passes, and a scope added later triggers a complete re-review — the owner's.
- Whether Zoom's API terms allow storing registrant ids and join links, to be
  confirmed in that review; the terms forbid building copies of API data — the
  owner's.
- The creator picks an existing meeting rather than Qori creating one from the
  Series: picking follows `D-016` and surfaces an admin-locked account at pick
  time, creating guarantees the settings — the owner's.
- Whether registrants on a register-once meeting are covered for occurrences
  added **later**, and whether the stored `join_url` admits a Peer directly
  before, during and minutes after a session starts — `T-099`'s, and it decides
  whether one grant per Series holds at all.
- Whether a session at an arbitrary time can be added to one recurring meeting
  by `PATCH`, or Zoom only produces occurrences its recurrence rule implies —
  `T-099`'s; the Episode form's shape follows the answer.
- Whether a repeat add for an existing registrant returns the same
  `registrant_id`, and whether it counts against the three-a-day cap —
  `T-099`'s.
- Whether error `3043` fires at room size or at 4,999 registrants. If it is room
  size, that number is the Series' Peer ceiling and is checked in
  `CheckoutService::begin()` beside the plan cap
  (`app/Services/CheckoutService.php:37-49`), because fulfilment cannot refuse
  (`PLAN.md` rule 2). The Business Plus room size is the one figure Zoom does
  not publish, and the tier copy is reading a stand-in until it is confirmed —
  `T-099`'s, then the owner's.
- Whether `registrants_confirmation_email` and `registrants_email_notification`
  can be turned off through the API, and what a cancelled registrant's link does
  afterwards — `T-099`'s.
- ~~Whether showing a recording's Zoom passcode to every Peer with access is
  acceptable, given that the link and the passcode together are forwardable —
  the owner's.~~ **Answered 18 September 2026 (`D-027`):** the passcode is
  shown to every Peer with access, because that is what the creator pasted it
  for; whether it may ride in the URL is `T-122`'s to observe. The stored link
  is the share link when the vendor returns one, else the play link, and never
  a download token.
- ~~What a cancelled occurrence does to its Episode: hidden, marked cancelled,
  or left with a note — the owner's.~~ **Answered 18 September 2026
  (`D-026`):** marked cancelled. The live `content` carries `cancelled_at`,
  and `LiveSessionService::stateFor()` — `T-125`'s addition to the service
  that already exists, not this task's `SeriesMeetingService` — computes the
  `cancelled` state from it; the Episode row stays, so its progress ids
  survive. `T-134` builds cancel, undo and "Add the next session".
- The registrant's first name when a Peer has no name: the email's local part,
  as specified, or a lang line the creator sees in their Zoom report — anyone's.
- ~~Which file the Peer surface's copy lives in: `T-089` says `lang/en/accesses.php`
  and adds no `shared.php`, while `T-091`'s Copy table writes its grant-state
  sentences to `lang/en/shared.php`. This task's own Peer lines (`accesses.live.*`)
  follow `accesses.php`, and the grant-state sentences stay `T-091`'s wherever
  the two drafts settle — anyone's.~~ **Answered 17 September 2026 (`D-020`):**
  the grant-state sentences are `T-091`'s `shared.vendor_notice.reasons.*`, in
  `lang/en/shared.php`, which `T-089` creates, and a Peer who cannot join is
  sent to them on the Series page. This task's own Peer lines stay
  `accesses.live.*` in `accesses.php`, beside the other provider tasks'
  `accesses.vendor.*`.
- How a live Episode is pointed at the new meeting after a replace. This draft
  flags every session of the old meeting (`checkItem()`), and has no way to
  re-point an existing Episode at an occurrence, so today the creator removes
  and adds each one again, as a new Episode id that the ids already in
  `opened_episode_ids` and `completed_episode_ids`
  (`database/migrations/2026_09_08_000000_create_qori_schema.php:151-152`) do
  not name — anyone's, and the answer may be a re-point action on the Episode
  form.
- ~~`T-091`'s names used here — `ContainerChangeDialog`, `containerImpact`,
  `VendorAccessService::impactOf()`, `checkNow()`, `retryNeedingCreator()`,
  `checkEpisode()`, `shared.vendor_notice.*` and `series.container_change.*` —
  are taken from `D-020`, `D-021` and its draft. `T-091` now says its dialog
  opens from any page that builds its entry, `PickMeeting.vue` among them, and
  takes a provider's `note`, which carries the cancelled registrations here.
  Re-check when it is `ready` that its meeting sentences and this task's note
  together say what a Zoom replace does (registrations cancelled on the old
  meeting, everyone registered on the new one, the Zoom meetings themselves
  untouched) — anyone's.~~ **Answered 20 September 2026:** five of those eight
  names are no longer `T-091`'s. `ContainerChangeDialog`, `containerImpact`,
  `VendorAccessService::impactOf()` and `retryNeedingCreator()` went to `T-157`
  with the creator's surfaces, which is why `T-157` is now in `depends:`;
  `checkNow()` was deleted outright with `D-040` and is named nowhere in this
  file any more. `checkEpisode()` and `shared.vendor_notice.*` are still
  `T-091`'s, minus the `next_attempt.*` and Check-again lines `D-040` took.
  `series.container_change.*` is split: the four `meeting.replace.*` are this
  task's, in the Copy table, and the rest stay `T-091`'s. The re-check this
  bullet asked for is done and passes — the four meeting sentences say Qori
  registers everyone on the new meeting and stops sending them to the old one,
  and `series.container.zoom.change.replace` says the old registrations are
  cancelled and the Zoom meeting itself stays.
- **What `D-040` leaves of "register each Peer once per Series", which is
  what this task is named for — the stream owner's, and the sharpest thing
  this pass found.** A grant is attempted when a Peer presses Open, for the
  one item they are opening, and at no other time. `T-091`'s consolidation
  of 20 September 2026 settled the part this bullet first got wrong:
  `attach()` writes **no rows at all**, not a `pending` row per active Access,
  so a replaced meeting leaves nothing behind it and the first Open is the
  whole of the mechanism. Case 16 and the Decisions line saying a replaced
  meeting "registers every active Access on the new one", and the Acceptance
  line reading "Every Peer with access is registered exactly once per Series",
  were all written for the sweep and none of them is true as it stands.

    **A file and a live session are not the same thing here, and that is the
    ruling.** Granting a file at Open is exactly right: opening is when you
    need it, and nobody is worse off for the two seconds. A Zoom registration
    is a seat in a room that starts at a time — so under `D-040` nobody is a
    registrant until they press Open, which for a live Episode is the moment
    they join, at the start of the session, all at once. Three hundred Peers
    pressing Join in the same minute is three hundred `meeting/registrants`
    creates against a vendor that `T-093` watched serialise, inside a
    twelve-second request deadline each, against Zoom's own cap. `D-040`'s
    arithmetic was worked out for one Peer opening one file; it was not
    worked out for a cohort arriving together. Either this task registers
    ahead of the session — an exception to `D-040`, which is the owner's to
    grant — or the copy and the Acceptance line stop promising a registration
    that only happens on arrival.

    The smaller half is answered: `T-091`'s Open path **does** still honour
    `next_attempt_at`, and `BACKOFF_MINUTES` is now `[0, 1, 2, 5, 15]`, so a
    Peer refused by Zoom's cap can press again at once and the fifth press
    costs fifteen minutes. The dialog's
    `series.container_change.meeting.replace.peers` line is written to be true
    whichever way the ruling falls: it says Qori registers them on the new
    meeting and names no moment.

- `T-044`'s `ProviderSections::ESSENTIAL`, `MAX_ESSENTIAL` and its key shape
  are taken from its draft, and this task's Zoom copy moved into that shape;
  re-check when it is `ready` — anyone's.
- ~~Whether a recording is `EpisodeType::Video` with `EpisodeProvider::Zoom`, as
  specified, or its own kind — anyone's.~~ **Answered 18 September 2026
  (`D-027`):** neither. A recording is a row in `episode_recordings` belonging
  to the live Episode, so one session can hold several parts and be corrected
  without touching the Episode or the completion denominator. `T-126` creates
  the table; this task creates no Episode for a recording and drops the
  `EpisodeType::Video` arm the header amendment already removes.
- How a Peer joins a Zoom live Episode on the Series page. This draft's
  `SharedController.php` row has `T-089`'s `opensAs()` return `tab` for a live
  Episode with a grant, and its `shared/Show.vue` row, case 39 and the change
  to `OpenEpisodeTest` are written on that; `T-125` keeps `opens` null for
  every live Episode and joins through its own live card, whose Join links to
  `shared.episodes.open`. The design here is unchanged until `T-125` is
  `ready`; then the two are made to agree — anyone's.
- What `T-141`'s Notes ask of this draft beyond the client and the tests,
  which moved on 19 September 2026: the five `ProviderTier` cases,
  `ZoomAccounts`, the `zoom` block in `config/services.php` and its two env
  keys come from `T-141` rather than being created here, so their Files rows
  and the `ZoomAccounts` code go; the Copy rows `T-141` declares go, and
  `description`, `disconnect.in_qori`, `account_change.in_qori` and any tier
  `help` or `recommended` line this draft needs in its own words are
  rewritten as a stated edit of `T-141`'s copy; `ZoomConnectTest`'s seven
  cases are `T-141`'s ground, and `ZoomRecordingTest`'s five go with
  `captureRecording()` (`D-024`, `D-027`), so `T-142`'s `ZoomRecordingsTest`
  is the one recordings file in that folder. `T-141`'s `ZoomClient::api()`
  also retries a failed request (`READ_ATTEMPTS`), and the registrant add is a
  write that counts against Zoom's three a day, so a retried add is a blind
  one: this draft either gets a builder with no retry for its writes or keeps
  `api()` for its reads alone — anyone's, with `T-141`.
- Zoom's documented limits are plan- and account-wide and shared by every app
  installed on the account, which the storage review of 20 September 2026
  (`docs/planning/reviews/storage-2026-09-20-findings-codex.md`) read off Zoom's
  published API rate limits: on Pro, 30 requests a second for the light calls
  and 20 for the medium ones, the heavy calls sharing one allowance of 30,000 a
  day, and registration limited separately to three requests per registrant per
  meeting per UTC day and ten for a status change. The review reads that as
  justifying the look-before-add rule above, and asks for the daily reset this
  draft already carries — `pending` until the next 00:00 UTC rather than a fixed
  interval — to be kept. What it does not find here is account-level backoff:
  the table in Code answers a plan rate limit with `pending()` on the one row
  whose call met it, so the next Peer in the same sweep rediscovers the same
  account-wide limit instead of the cooldown being held once for the Zoom
  account — anyone's, with `T-091`.
  **That file no longer exists and cannot be recovered**, so these bullets are
  the review itself, to be read as the primary source and not as a summary of
  something a reader can go and check; `docs/planning/reviews/README.md` has the
  whole of it.
- The lookup before every add is not one call. The same review notes that the
  expensive scan is every registrant page and every status, so `grant()`'s
  three reads — approved, then pending, then denied — and their pagination are
  the real cost of the rule, repeated by `T-091`'s ensure step on every
  Series-page load, and the endpoint tiers and response headers those reads
  spend against have to come from `T-099` rather than the documentation
  (20 September 2026) — `T-099`'s to answer, then anyone's.
- No Zoom response fixture exists anywhere in the repository yet; the review of
  20 September 2026 checked and says so plainly. Every payload this draft names
  — the registrant create's `registrant_id` and `join_url`, the three list
  statuses, the cancel `PUT`, and each `3043`, `3161`, `3000`, `1001` and `429`
  row of the table in Code — is therefore a hypothesis taken from Zoom's
  reference, and `PROCESS.md` does not let a `ready` spec name a vendor payload
  on that footing — `T-099`'s and `T-122`'s to answer.
- A creator can change a live Episode's `join_url` **in place**, keeping the
  Episode id. `EpisodeService::update()` reads a `join_url` attribute and
  merges it into `content` (`app/Services/EpisodeService.php:219-227`), written
  through `LiveSessionService::withLockedContent()`
  (`app/Services/LiveSessionService.php:30-42`, the service that exists today,
  not this task's `SeriesMeetingService`), and nothing records or acts on
  the URL that was there before. It is the one true in-place vendor repoint in
  the codebase — every other replacement in Qori is a delete and a create with
  a new ULID — and it is the exception to the bullet above, which says this
  draft "has no way to re-point an existing Episode at an occurrence": for the
  pasted tier the path is already built and unwatched. `update()` gates on
  `isLive()` alone (`:191`) and never on the provider, so dropping the
  pasted-link field for Zoom (the `share/series/Show.vue` row in Files) narrows
  the path without closing it. What happens to a grant made against the meeting
  the Episode used to point at — cancelled at Zoom, re-registered on the new
  one, or left for the next ensure to find — is specified nowhere, and it has
  to be, because a `vendor_grants` row and its stored `join_url` outlive the
  edit that made them wrong — anyone's, with `T-091`.

## Amended 20 September 2026 — the meeting half moves here from T-091

**The stream owner answered `T-091`'s open question on 20 September 2026: the
meeting half of the container-change dialog leaves that task for `T-100` and
`T-101`, "the only tasks that would use it".** `T-091` wrote the half and then
asked whether it should stay there, waiting behind `D-024`, or move to the two
tasks that read it. It moves. Nothing is deleted from `T-091`, which stays the
record of where the half was written and why; what follows is what this task
now carries.

**What arrives.** The four things `T-091` names, in this task's reading of them:

- **`ContainerChangeImpact::kind()` answering `meeting`.** It is the switch
  that makes the dialog read `series.container_change.meeting.*` instead of
  `.folder.*`, and `T-091` specified it as `meeting` for Zoom and Teams,
  `folder` for every other container provider. The class stays `T-091`'s
  `app/Data/ContainerChangeImpact.php`; the `meeting` arm is this task's.
- **The eight `series.container_change.meeting.*` lines.** This task reads the
  four `replace.*` — `title`, `peers`, `episodes` and `confirm` — because a
  Zoom meeting is replaced from `PickMeeting.vue` and never removed (Scope).
  The four `remove.*` lines arrive with no reader; see the ruling at the end
  of this section, which drops them. `series.container_change.keep` is **not**
  one of the eight and is **`T-157`'s**, which declares it with the dialog it
  is a button on; it belongs to neither kind, and `T-091` writes no `series.*`
  line at all once its creator copy moved.
- **`T-091`'s test case 60**, `test_a_meeting_container_takes_the_meeting_lines`
  — a Zoom container, `kind` `meeting`, `copy.replace.title` the meeting line —
  **and the Zoom half of its case 28**, the clause asserting `kind()` answers
  `meeting` for a Zoom container where the rest of that case asserts `folder`.
  Both are Zoom, so neither goes to `T-101`.
- **`vendor_grants.join_url`** — `string(2048)`, nullable, default null — the
  per-Peer URL only this task and `T-101` read. It is also the column this
  task's own rule depends on: a registrant is `granted` only when a `join_url`
  comes back. ~~So the evidence and the place it is kept are now in one
  task.~~ **Ruled 20 September 2026:** the reading moved and the column did
  not. It stays declared in `T-091`'s create migration; see Database.

**Why it moves rather than waits.** What these lines may say is decided by what
each vendor does when the meeting changes, and the two vendors do opposite
things: **Zoom cancels the old registrants; Teams tells Microsoft nothing.** So
the shared lines say only what Qori stops doing — "Qori stops giving them this
one" — and say nothing about the creator's vendor account, while the fact true
of one vendor alone rides in that provider's own note. Here that note is
`series.container.zoom.change.replace`, already in this task's Copy table: "In
Zoom, their registrations on this meeting are cancelled. The meeting itself
stays in your account." `T-101` needs no equivalent, because it writes its own
Peers sentence, `connections.meeting.teams.replace_impact`, and no Episodes
sentence at all. Lines kept in `T-091` would have to be read against two vendor
behaviours neither of whose tasks that draft can see. The move also takes an arm
off `T-091`'s split problem: its `L` bullet listed "the meeting half" as cut
(c), conditional on this very answer.

**It arrives held.** `D-024` holds the live-session containers until they fit a
per-Episode join link (`D-026`), and moving the words did not lift the hold.
None of this is buildable because it is written here; it is written here so
that whoever lifts `D-024` finds it beside the Zoom behaviour that decides its
wording.

**What it means for this task's sections.** The bullets below said what each
section wanted; the stream owner ruled on the two open points the same day, and
the sections were worked on 20 September 2026 rather than left for whoever picks
the draft up. Where a bullet is struck, the strike is what it asked for and did
not get.

- **Database** stays **None**. ~~`T-091`'s create migration belongs to `T-091`,
  so declaring the column here means an `ALTER` on `vendor_grants` of this
  task's own, in the shape above.~~ **Ruled 20 September 2026:**
  `vendor_grants.join_url` stays declared exactly once, in `T-091`'s
  `2026_09_20_000100_create_series_containers_and_vendor_grants.php`, and the
  `ALTER` is dropped. An `ALTER` for a nullable string on a table the same
  release creates buys nothing, and a column each meeting task declares for
  itself is a column that disappears from every task at once. The Database
  section now says so and cites the migration.
- **Files** gained one row, `app/Data/ContainerChangeImpact.php` (`edit` — the
  `meeting` arm). No migration row, under the ruling above.
  `lang/en/series.php` was already an `edit` row and only grew.
- **Copy** gained the four `series.container_change.meeting.replace.*` lines
  with their English. ~~They sit in `T-091`'s table today.~~ **They did not:**
  they were in no Copy table anywhere, so this pass wrote them (Copy). They say
  only what Qori stops doing; the Zoom fact rides in
  `series.container.zoom.change.replace`, which was always this task's and is
  unaffected. The sentence that had to change was in **Copy**, not in
  Acceptance as this bullet said.
- **Code** carries `kind()`'s `meeting` arm, sketched after the
  `MeetingController::show()` paragraph, with the class and its signature left
  as `T-091`'s.
- **Tests** folded `T-091`'s case 60 and the Zoom half of its case 28 into this
  task's case 17 rather than adding cases, because
  `test_the_picker_carries_what_replacing_the_meeting_changes` already asserts
  the same entry; `kind` and `copy.replace.title` are the clauses they added.
  Every stated total was recounted from the numbered cases — 7, 10, 16, 11, 5
  and 49 — and none of them moved.
- **Scope**'s "In" bullet now names the meeting lines and `kind()` as this
  task's; the "Out" bullet sends the component itself to `T-157`, where it went
  with the creator's surfaces, and sends its meeting wording nowhere.

**The two things this task could not place have been ruled on**, by the stream
owner on 20 September 2026, so the next reader does not rediscover them.

- ~~Neither of the two tasks depends on the other — `T-101` depends on `T-091`
  alone — and both now want `app/Data/ContainerChangeImpact.php`,
  `lang/en/series.php` and the `join_url` column.~~ **Resolved by the
  dependency, which is what `PROCESS.md` has the stream owner do.** This task
  declares `ContainerChangeImpact::kind()`'s `meeting` arm and the four
  `series.container_change.meeting.replace.*` lines; `T-101` reads
  `.title` and `.confirm` from here and declares neither file. `T-100`
  `blocks: T-101`, and `T-101` carries `depends: T-091, T-100, T-157`. The
  `join_url` column is claimed by neither, because it never left `T-091`.
- ~~The four `series.container_change.meeting.remove.*` lines have no reader in
  either task.~~ **Dropped, not homed.** No task in the plan builds a meeting
  remove: a meeting is replaced from the picker and never removed here, `T-101`
  has no remove, and the only draft building a remove is `T-094`, for a Drive
  folder. Four lines describing an action nothing offers should not be written,
  so they are not in this task's Copy table; whichever task first builds a
  meeting remove writes them then.

## Read-through, 20 September 2026

A three-lens read of `T-091` before it was to be frozen found the cut of that
day was not clean, and some of what it found was this task's. The list is in
`T-091` under "Read-through, 20 September 2026 — what the cut left behind".
This task's share was worked through the same day, against the stream owner's
ruling recorded in the section above, and what follows is what each item
became. The task stays a `draft`: the pass fixed what the read-through named,
and did not write the sections a spec still needs.

- ~~It depends on `T-157` in substance — `impactOf()`, `containerImpact`,
  `ContainerChangeDialog`, `connections.grants.retry` — and does not say so in
  `depends:`.~~ **Answered 20 September 2026:** `T-157` is in `depends:` with
  `T-044`, `T-091`, `T-094`, `T-099` and `T-141`, and the body now agrees with
  it. Decisions, Preconditions, Files, Code, Copy and Scope attribute all four
  names to `T-157`, and Preconditions says what has to exist before this task
  starts.
- ~~Two live test cases post to `shared.access.check` and one exercises Try
  again now, all of which moved or were deleted.~~ **Answered 20 September
  2026:** four cases touched that machinery, not three. Case 32 is rewritten
  around `shared.episodes.open`, the only moment `D-040` leaves a grant to be
  attempted, and asserts the Zoom-side guarantee this task owns — the lookup
  before any `POST`. Case 33 is re-attributed to `T-157`'s Try again now. Case
  40 no longer asserts the deleted `shared.vendor_notice.next_attempt.*`
  lines. Case 43 no longer asserts the absence of a Check again that no longer
  exists. All four keep their numbers, and no number is reused.
- ~~It attributes five names to `T-091` that are no longer there.~~ **Answered
  20 September 2026** in the bullet under "Before this can be ready" that used
  to list them: `ContainerChangeDialog`, `containerImpact`,
  `VendorAccessService::impactOf()` and `retryNeedingCreator()` are `T-157`'s,
  `checkNow()` is deleted and named nowhere here, and `checkEpisode()` and
  `shared.vendor_notice.*` stay `T-091`'s.
- ~~It names `LiveSessionService` where `D-026` gave that name to `T-125` and
  this task's service is `SeriesMeetingService`.~~ **Answered 20 September
  2026:** the four places meaning this task's service — the occurrence rule in
  Decisions, the Files row, the class sketch in Code and the
  `MeetingController::show()` paragraph — read `SeriesMeetingService`, and the
  Files row is `app/Services/SeriesMeetingService.php`. Two places keep the old
  name deliberately, because it is a real class:
  `app/Services/LiveSessionService.php:30-42` is `withLockedContent()` in the
  repo today (opened 20 September 2026), and `stateFor()` is `T-125`'s addition
  to that same class, as its docblock says. Both now say which service they
  mean.
- ~~Its header summary stops at 19 September, so a reader never learns the
  meeting half arrived.~~ **Answered 20 September 2026:** the header carries
  the three-way cut of `T-091`, what this task declares because of it, what it
  depends on `T-157` for, and `D-040`.
- ~~The four `series.container_change.meeting.replace.*` lines it says "sit in
  `T-091`'s table today" do not: they are in no Copy table anywhere.~~
  **Answered 20 September 2026:** they are in this task's Copy table with their
  English, under the ruling that this task declares them and `T-101` cites
  `.title` and `.confirm` from here. They name no vendor and no count of their
  own: the Zoom fact is the note beneath them, and the two figures are
  interpolated.

Three things the list did not name were found while working it, and are fixed
here. `qori:access:reconcile` and the scheduled sweep were still promised in
Decisions, Preconditions and Scope after `D-040` deleted them. The states
paragraph still read "four of the six states" when `VendorGrantStatus` has
eight, and it now names the two Zoom never answers and the two the machinery
reaches on its own. The amendment placed the sentence it wanted changed in
Acceptance, and it was in Copy.

One thing is left and needs the stream owner rather than this pass: what
`D-040` leaves of registering every Peer when the meeting is attached, which is
the last bullet under "Before this can be ready". The recordings contradiction
`D-024` and `D-027` opened — `captureRecording()`, `ZoomRecordingTest` and the
`EpisodeType::Video` row still standing in the body the header says they left —
was already carried as an open bullet with `T-141`, and this pass left it
there.

## Re-scope log

None.

## Notes

**`app/Integrations/Zoom` does not exist today.** Nothing in `app/` talks to
Zoom: `app/Integrations` holds `CloudflareR2`, `Contracts`, `Dropbox`,
`Stripe` and `Vimeo`, and no `Concerns` (`D-022`). `T-141` creates the Zoom
folder with `ZoomClient`, which this task builds on (checked 19 September
2026). What this task supersedes is smaller than it looks — the pasted
`join_url` in `StoreEpisodeRequest::content()` (`:190-195`) with its "Join link
(optional for now)" label and `https://zoom.us/j/...` placeholder
(`resources/js/pages/share/series/Show.vue:239-243`, `:257-262`); the
`['meeting_id' => '918 2740 5566']` content in
`database/seeders/DesignReviewSeeder.php:356`,
which is not the shape this stores; and two "not built yet" paragraphs,
`docs/flows/series.md:127-129` and `docs/flows/storage.md:100-104`.
`EpisodeProvider::Zoom` and `ConnectionProvider::Zoom` are kept exactly as they
are.

`CLAUDE.md` still says integrations expose `name()` and are bound in
`AppServiceProvider`; the code says `provider()`
(`app/Integrations/Contracts/ResolvesMedia.php`) and
`app/Providers/IntegrationServiceProvider.php`. This draft follows the code, as
`T-089`, `T-091` and `T-044` do.

This task's `depends:` now agrees with all five of its dependencies' `blocks:`
— `T-044`, `T-091`, `T-094`, `T-099` and `T-141` each name `T-100`; `T-094`
joined on 17 September 2026, when the storage stream made it the first
complete journey, and `T-141` on 19 September 2026, when this draft took its
`ZoomClient`. The stream file lists `T-141` after this task, so its order
there is the stream owner's to move.

Zoom's own "meeting updated" emails reach registrants and cannot be suppressed
per person — the only answer found is a 2019 staff post, and the two email
settings are meeting-wide. The limitation copy says so rather than pretending
Qori is the only sender a Peer hears from.

Every `path:line` above was opened and checked on 17 September 2026, and the
draft was read against `T-044`, `T-089`, `T-091`, `T-092` and `T-099` so the
names it borrows are theirs. The line numbers move with the files; treat a
mismatch as a stale citation to fix, not as a re-scope.
