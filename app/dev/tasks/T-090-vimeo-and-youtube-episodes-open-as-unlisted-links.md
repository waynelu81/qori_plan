---
id: T-090
title: Vimeo and YouTube Episodes open as unlisted links
stream: storage
status: draft
owner: unassigned
estimate: L
depends: T-044, T-089, T-094
blocks: none
---

# T-090 — Vimeo and YouTube Episodes open as unlisted links

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016`, the owner's BYO blueprint and the developer review of the same day;
> every path and line below re-checked against the code on 17 September 2026,
> and `D-018` folded in the same day. `D-019` was folded in on 17 September
> 2026: the paid-Series guard, its config flags and its copy are gone. `D-021`
> was folded in the same day: Check now beside an Episode's warning, one
> `qori:episodes:check` shared with `T-094`, and each tier's essential lines.
> The gatekeeper's rulings of the same day are folded in too: `T-094` owns that
> command, Check now and their two test files, this task depends on it and
> extends them, and a Check now press answers from `VideoCheck` as `T-094`'s
> container arm answers from `T-091`'s `EpisodeCheckOutcome`. Amended on
> 19 September 2026 from that day's cross-draft decisions: `T-094`'s container
> arm takes the providers `T-091`'s `VendorAccessService::handles()` accepts,
> which Vimeo and YouTube are not; `ListsVideos`' `$timeoutSeconds` is a
> budget each vendor's client may only shorten (`D-034`); and what dies with
> the play route is the Vimeo check inside `T-089`'s
> `SharedController::opensAs()`, because `T-089` put no `embeds()` on
> `EpisodeProvider`. After `T-044`'s update the same day: the picker's need
> for a live connection is this task's own rule, since `T-044`'s guard covers
> only `isAccountBound()` providers and YouTube's arm, added here, is false;
> both `Accounts` classes answer `T-044`'s `ConnectionLanding`; and the
> YouTube classes use `GoogleAccounts::TIMEOUT_SECONDS`, Google's one limit.

## Why

`D-016` grants each Peer at the vendor wherever the vendor has a per-person
grant, and says that where it does not — Vimeo, YouTube — **the Series is the
container**: the item is unlisted at the vendor and Qori shows its link only to
Peers with access. The vendor facts behind that, because this task has to
choose a scope and a picker rule from them: Vimeo retired "People I choose",
and its remaining per-person call takes a numeric Vimeo user id that no
endpoint resolves from an email and answers 403 without a user-defined access
list
([privacy settings](https://help.vimeo.com/hc/en-us/articles/12426199699985-About-video-privacy-settings),
[videos reference](https://developer.vimeo.com/api/reference/videos)); YouTube's
Data API has no method that adds or removes a viewer, and `privacyStatus` is
only `private`, `public` or `unlisted`
([videos](https://developers.google.com/youtube/v3/docs/videos)).

Today the code does the opposite of what `D-016` asks. `VimeoVideos::lockDown()`
(`app/Integrations/Vimeo/VimeoVideos.php:39-60`) PATCHes `privacy.view` to
`disable`, which Vimeo calls Embed only and documents as "not viewable on
Vimeo.com", then PUTs a domain whitelist whose response is never checked
(`:56-59`); nothing in the repository calls the method. `linkFor()` returns
`https://player.vimeo.com/video/{id}` with `embed: true` (`:62-86`), which is an
`<iframe>` and not a page to open, and the Peer page fetches it through the JSON
play route and frames it (`resources/js/pages/shared/Show.vue:82-113`, `:258`).
YouTube does not exist at all: no `ConnectionProvider` case
(`app/Enums/ConnectionProvider.php:12-21`), no `EpisodeProvider` case
(`app/Enums/EpisodeProvider.php:14-51`), nothing in
`EpisodeType::allowedProviders()` (`app/Enums/EpisodeType.php:29-37`). A Vimeo
Episode is a video id a creator typed into a text field
(`resources/js/pages/share/series/Show.vue:236-243`), stored as
`content['vimeo_id']` (`app/Http/Requests/Share/StoreEpisodeRequest.php:189`),
and nothing ever reads the video back, so a deleted or privatised video is
discovered by a Peer.

Afterwards a creator connects Vimeo or YouTube on `T-044`'s machinery, picks a
video from their own account instead of typing an id, and Qori stores the id and
— for Vimeo — the complete unlisted link with its privacy hash. `T-089`'s Open
route redirects the Peer to the vendor's own watch page in a new tab. `T-094`'s
daily command re-reads every stored video as well and tells the creator when one has been
deleted, made private or age-restricted, before a Peer meets it, and a creator
who has put one right presses Check now beside the warning rather than waiting
for the next run.

## Decisions taken to make this specifiable

**No grant row, no grant contract, and no container row.** The developer review
asked for "the shared Open route without requiring fictitious per-Peer grants".
`T-091`'s `GrantsPeerAccess`, `series_containers` and `vendor_grants` exist by
the time this task runs, because `T-094`, which it depends on, depends on
`T-091`, but nothing here uses them. So these two providers stay on
`ResolvesMedia`, bind no `grant-providers` integration, and `T-089`'s `open()`
wraps their answer in `VendorLink::fromMediaLink()`. That is exactly `T-091`'s
stated fallback ("when no `grant-providers` integration is bound for the
provider, `T-089`'s `fromMediaLink()` branch stays").
The blueprint's §4.5 note — link-only providers implement `grant()` as a no-op
returning `granted` — is not followed: a row that says `granted` with no vendor
permission behind it is the fiction the review objected to.

**So none of `VendorGrantStatus`'s six states arises here, and this task never
writes one.** `awaiting_identity`, `awaiting_acceptance`, `pending`,
`needs_creator`, `granted` and `revoked` all describe a permission at a vendor,
and there is no permission: a Peer with access opens the link, a Peer without
access never sees it. What `granted` means for the per-Peer providers — "checked
recently enough to be trusted" — is carried here by the Episode's own
`checked_at` and `check_code`, which the daily command writes and Open reads.
The one state with a Peer-facing analogue is `pending`: a vendor Qori could not
reach leaves `VideoCheck::Unreadable`, nobody is told, and the next run retries.

**The shared reconciliation triggers, and what each one means for these two.**
A creator who reconnects the _same_ Vimeo or YouTube account changes nothing
stored: the video ids, and Vimeo's link with its hash, stay valid, so there is
nothing to re-run. A creator who connects a _different_ account can make every
stored id unreadable with the new token; nothing detects that in the moment, and
the next `qori:episodes:check` writes `VideoCheck::Missing` on each Episode and
the creator re-picks. The other two triggers cannot arise: there is no Peer
vendor identity to confirm or change (`T-092` excludes both providers), and no
container to replace.

**The dedicated-container rule does not apply, and the picker says what does.**
`T-091`'s rule — one folder or meeting per Series, never shared between Series —
exists because a vendor container's membership is shared state. Nothing is
shared at the vendor here, so two Series may point at one video and removing an
Episode from one takes nothing from the other. What the picker has to say
instead is the truth about an unlisted link: anyone holding it can watch
(`series.videos.link_note`). `D-016` accepts forwarded links; this copy is there
so the creator is not surprised by it, not to reopen the decision.

**Vimeo and YouTube are two connections, not one.** YouTube gets
`ConnectionProvider::YouTube` on Google's OAuth client, beside
`ConnectionProvider::GoogleDrive`; `connections`' unique `(group_id, provider)`
(`database/migrations/2026_09_08_000000_create_qori_schema.php:193`) allows both,
and `T-044`'s draft anticipates it. A creator may use Drive for files and
YouTube for video with one Google account and two rows, each with its own scope
and its own tier. Connecting either sends the creator back to `T-044`'s
`u/connections/google/finalise`, because the URL a vendor sends a person back
to names the vendor, not the service (`D-033`): `ConnectionProvider::YouTube`'s
`vendor()` is Google, as `GoogleDrive`'s is, and which of the two is being
connected, with its tier, travels in the session state the begin step wrote.
YouTube registers no redirect URI of its own. Should it be given a Cloud
project of its own (`docs/planning/vendor-accounts.md`, YouTube's "Do this
first"), that project's OAuth client registers `u/connections/google/finalise`
too. Vimeo sends the creator back to `u/connections/vimeo/finalise`.

**Qori reads; it never changes a video's privacy.** YouTube's Developer Policy
III.E.3 forbids changing visibility unless the authorising user expressly
instructs it, and `D-016` asks for the narrowest scope that allows the rest. So
the scopes are `youtube.readonly` and Vimeo's `private`, the picker refuses a
video that is not shareable and says what to change at the vendor, and
`lockDown()` is deleted rather than reversed
([developer policies](https://developers.google.com/youtube/terms/developer-policies)).

**The picker is a page, not a JSON endpoint.** v1 is Inertia-only, so listing
the creator's videos is
`GET g/{group}/series/{series}/videos/{episodeProvider}` rendering
`share/series/PickVideo.vue`, with `?cursor=` for the next page and
`?episode={episodeId}` when an existing Episode is being re-pointed. The page
load takes the Series slug and the two writes take ids, as §21.3 requires. All
three sit in `routes/share/episodes.php`, whose header says today that
everything in it mutates and every parameter is an id (`:11-16`); that sentence
gains the picker page as its one exception rather than the routes being split
across two files. The picker needs a live connection for its provider because
it lists the creator's own videos with the creator's token:
`VideoLibraryService::page()` refuses without one, and that is this task's
rule. `T-044`'s guard in `EpisodeService::add()` does not reach these
Episodes: it covers only `EpisodeProvider::isAccountBound()` providers, and
neither of these is one, because a stored Vimeo or YouTube id plays without
the account — `T-044` says so of Vimeo's, and this task adds YouTube's arm,
false.

**The stored content is the id, plus the whole link for Vimeo.** Vimeo's Unlisted
adds a privacy hash to the URL and the hash must travel with the link
([privacy settings](https://help.vimeo.com/hc/en-us/articles/12426199699985-About-video-privacy-settings)),
so `content['url']` is stored as the vendor returned it and never rebuilt from
the id. YouTube's watch URL is `https://www.youtube.com/watch?v={id}` with
nothing secret in it, so only the id is stored and the URL is derived
(`https://support.google.com/youtube/answer/157177`). Vimeo keeps its existing
`vimeo_id` key (`StoreEpisodeRequest.php:189`); YouTube uses `youtube_id`.

**The daily check is `T-094`'s command, `qori:episodes:check`, and this task
adds its pass to it**, which is this task's answer to the review's "define
when successful grants are rechecked".
`T-091`'s `qori:access:reconcile` is a grants sweep running every few minutes
and is not a dependency here; this is a once-a-day read of stored items with no
grant in it, so what a Peer opens is verified against the vendor continuously
rather than only at the pick. YouTube's Developer Policy III.E.4 allows
Authorized Data other than tokens to be kept for no longer than 30 calendar
days, which makes a daily re-read the floor rather than a preference. `T-094`
defined the same signature for its folders' files, and `D-021` made them one
command. The stream order (`docs/planning/streams/storage.md`) makes `T-094`
the first complete journey, so `T-094` creates
`App\Console\Commands\CheckEpisodeItemsCommand` with
`VendorAccessService::checkItems()` as its pass and writes its one schedule
line; this task adds `VideoLibraryService::checkDue()` to the same per-Group
pass, widens `$description` to cover videos as well as files, and leaves the
signature and the schedule as `T-094` wrote them.

**Open reads the stored check and calls no vendor.** The blueprint suggested
re-reading on Open as well. YouTube's quota is 10,000 units a day for Qori's
whole Google project, shared by every creator
([getting started](https://developers.google.com/youtube/v3/getting-started)),
and priority 1 is a Peer opening the thing quickly; a vendor call on every click
spends both. So `linkFor()` refuses only when the last check said the video is
gone or private, and the Peer meets a Qori page rather than a dead tab.

**A creator who has fixed a video says so with Check now, and lands on the
answer** (`D-021`, 17 September 2026). A warning whose only way forward is
"Qori checks again tomorrow" leaves a creator who has just set a video back to
Unlisted with nothing to do but wait, and a Peer locked out until the next run.
So a Check now button (`series.episode_check.check_now`) sits beside every
`series.video_check.*` warning and posts to `share.series.episodes.check`.
`T-094` builds that route, `EpisodeCheckController`, its per-Episode throttle
(`EpisodeCheckController::MANUAL_CHECK_SECONDS`, `RateLimiter` key
`episode-check:{episodeId}`) and every `series.episode_check.*` line, with the
container arm for every provider `T-091`'s `VendorAccessService::handles()`
accepts, through its `checkEpisode()`; Vimeo and YouTube have no
`grant-providers` integration, so `handles()` refuses them and the controller
answers 404 until this task's arm exists. This task adds the Vimeo and YouTube
arm, dispatching on `$episode->provider` ahead of the container arm: it
re-reads that one Episode through `VideoLibraryService::check()` with
`REQUEST_TIMEOUT_SECONDS` as the budget, because it runs inside the creator's
own request, and the controller redirects back to the Series page, where the
warning has gone or is still there, with a flash that says which. The flash is
mapped from `check()`'s answer as the container arm maps `T-091`'s
`EpisodeCheckOutcome`: null is `series.episode_check.clear`,
`VideoCheck::Unreadable` is `series.episode_check.unreadable`, and any other
`VideoCheck` is `series.episode_check.still`. A press is one `videos.list`
read, one unit of the daily quota every creator shares, and `T-094`'s throttle
is what stops a double click spending two. A read that cannot reach the vendor
says so and changes nothing: `check()` never lets `VideoCheck::Unreadable`
replace what the last successful read found, in the command or here, so a
vendor having a bad minute neither hides a private video from the creator nor
lets a Peer through to it. The Series page offers the button only beside a
warning.

**An age-gated video is the creator's problem, not a refusal.** A Vimeo video
with no content rating, or an age-restricted YouTube video, still opens — the
vendor asks the viewer to sign in
([Vimeo age verification](https://vimeo.com/blog/post/vimeo-age-verification-2-0),
[YouTube age restriction](https://support.google.com/youtube/answer/2802167)).
Qori refuses one at the picker and warns the creator when a stored video becomes
one, and never blocks the Peer over it.

**Both providers are in the beta release, and so is every tier they offer**
(`D-018`). Nothing here waits on a decision about whether Vimeo or YouTube makes
beta. The question that was open was whether a tier whose sharing is weaker than
a creator might assume should be refused, and the answer is that it is offered
with that limitation stated on screen before the connection is made: the
platform a creator brings, and its rules, are the creator's own. Each tier's
copy also says what Qori recommends, in words a creator can act on — advice, not
a refusal and not a shrug.

**Vimeo Free is offered, Public-only** (`D-018`, 17 September 2026). Free and
legacy Basic accounts can only be Public or Private, and the API refuses
`unlisted` on them
([Vimeo OpenAPI](https://raw.githubusercontent.com/vimeo/openapi/master/api.yaml)),
so the tier copy says plainly that a video used here can only be Public — anyone
who comes across it on Vimeo can watch, and Qori cannot make it Unlisted — and
the creator connects anyway if they choose. The tier is not refused, it is not
gated behind a warning dialog and there is no fallback: that is what
bring-your-own storage means, and the owner said so directly on 17 September 2026. The picker accepts Public on Free, and Public or Unlisted on a paid plan.

**Vimeo and YouTube hold Episodes in any Series, priced or free** (`D-019`,
17 September 2026). A paid Series sells the creator's time and knowledge — the
live sessions, the work and the consultation they lead to — and a video on
either vendor is course material that comes with it, so nothing here guards a
price, flags a provider or holds an Episode back. A video may be Public or
Unlisted, as the creator prefers; Private is refused because a Peer cannot open
it. What each vendor's terms say is recorded in
`docs/planning/vendor-accounts.md`.

**Each tier's essential lines are the ones that decide whether a Peer can watch
at all** (`D-021` rule 4). `ProviderSections::ESSENTIAL` (Code) lists, for
Vimeo, the rating line (a Peer may be asked to log in and prove their age), the
tier's privacy line (Free is Public only; on a paid plan a Private video can't
be watched) and the team line; for YouTube, the Unlisted-or-Public line, the
age-restriction line and, on a work or school account, the admin line.
Replacing a video, the daily re-read and Enterprise's privacy restrictions go
in `more`, because none of them stops a Peer watching today, and there is no
one-folder-per-Series line to list, because nothing is shared at the vendor
(see above).

**The JSON play route dies here; `PlaybackTicketService::issue()` does not**
(the route is provisional — see below). `T-089` kept `shared.play`,
`PlaybackController`, the Vimeo check inside `SharedController::opensAs()` —
its `inline` arm, a private check rather than a method on `EpisodeProvider` —
`MediaLink::$embed` and the `<iframe>` alive for the Vimeo player alone and
named this task as the one that removes them. With `privacy.view` never set
to `disable` there is no whitelisted embedding domain, so the embed could not
play top-level anyway. `issue()` stays: it is the only path that still
returns an expiring `MediaLink`, and
`MediaLifetime` and the `link_ttl` rules are asserted through it
(`tests/Feature/Storage/MediaLifetimeTest.php:109-110`, `:146`) while `T-089`'s
`open()` wraps everything not Qori-hosted in an expiry-free `VendorLink`.
Removing a method whose last production caller has gone is worth doing and is
not worth doing inside this task.

**Vendor names stay in this task's copy.** `D-016` allows them in
provider-choice and Peer-prerequisite copy, as a stated exception to
`CLAUDE.md`'s no-vendor-names rule, and every sentence below that names Vimeo or
YouTube is a creator choosing between accounts or being told what to change in
one; `T-094`'s `series.episode_check.unreadable`, which this task's arm
flashes, tells a creator which one Qori could not reach just now. No
Peer-facing sentence here names a vendor.

## Preconditions

`T-044` done: `ConnectsAccounts`, `ConnectionService`, `ProviderTier`,
`lang/en/connections.php`, the Integrations page's provider sections and
`Connection::isLive()`. `T-089` done: `shared.episodes.open`,
`PlaybackTicketService::open()`, `SharedController::opensAs()` and
`App\Data\VendorLink`. `T-094` done: `CheckEpisodeItemsCommand`
(`qori:episodes:check`) and its schedule line, `EpisodeCheckController` with
`share.series.episodes.check` and `MANUAL_CHECK_SECONDS`, every
`series.episode_check.*` line, the `missingSince` prop on the creator's Series
page, `tests/Feature/Console/CheckEpisodeItemsCommandTest.php`,
`tests/Feature/Series/EpisodeCheckTest.php` and its `tests/Fixtures/google/`
responses — and, through `T-094`, `T-091`'s `VendorAccessService::checkEpisode()`
and `App\Enums\EpisodeCheckOutcome`.

**Data this task verifies against:** a clean database; the feature tests build
their own Series through `SeriesService::create()` and `EpisodeService::add()`,
as `tests/Feature/Storage/PlaybackTest.php:42-49` does, and fake every vendor
call from the fixtures below.

**Equipment:** a paid Vimeo account and a free one; a YouTube channel; a Google
Cloud OAuth client **in production**, not Testing, because a Testing client's
refresh tokens expire after seven days and cannot prove unattended checking
(https://developers.google.com/identity/protocols/oauth2) — which waits on the
privacy policy and terms being live on `useqori.com` (`vendor-accounts.md`,
Google Drive step 12); a second browser
signed out of both vendors.

**Spike — this task owns it, and it runs first.** No Vimeo or YouTube response
has been observed; every payload named in Code comes from vendor documentation
and is owed as a fixture. It is walked with **the exact scopes Qori will
request** — `private` at Vimeo, `youtube.readonly` at Google — never a broader
diagnostic token, because a wider scope can hide the step a creator will hit.
The steps: PATCH a video to Unlisted and read its `link`; open that link signed
out in the second browser; `POST /videos/{video_id}/versions` and confirm the
id, hash and privacy survive; leave a video unrated and open it signed out; list
the channel's uploads and read one video back; make a video private, then delete
another, and confirm `videos.list` shows each change; age-restrict one and
record which field says so; re-read the same video twice a day apart, to show a
repeated check is idempotent; and record one recoverable failure — a vendor 500
or a timeout — and that the next read clears it. Every response is kept dated
and redacted in the report. Its result is these fixtures, committed:
`tests/Fixtures/vimeo/oauth-token.json`, `me.json`, `me-videos.json`,
`video-get.json`, `errors-video-404.json`;
`tests/Fixtures/youtube/oauth-token.json`, `channels-list.json`,
`playlist-items-list.json`, `videos-list.json`, `videos-list-empty.json`.
Neither directory exists; `tests/Fixtures` holds only `planning` and
`reachability` today.

## Scope

**In:**

- `ConnectionProvider::YouTube` with its `vendor()` arm, `google` (`D-033`),
  `EpisodeProvider::YouTube` with its `connection()` arm and its
  `isAccountBound()` arm, false (`T-044`'s method), the two `ProviderTier`
  cases per vendor, and `EpisodeType::Video`'s allowed list.
- `VimeoAccounts` and `YouTubeAccounts` (`T-044`'s `ConnectsAccounts`), and the
  tier, limitation and recommendation copy for four tiers — Free Vimeo among
  them, offered with its Public-only limit stated (`D-018`) — with the
  `vimeo` and `youtube` entries in `T-044`'s `ProviderSections::ESSENTIAL`
  and each provider's `disconnect.in_qori` and `account_change.in_qori` lines
  (`D-021`).
- The `ListsVideos` contract, `VimeoVideos` rewritten, `YouTubeVideos` new, and
  `VideoLibraryService`.
- The picker page, its three routes, and re-pointing an existing Episode.
- `VideoLibraryService::checkDue()` added to `T-094`'s `qori:episodes:check`,
  the creator's warning beside a video Episode, and the Vimeo and YouTube arm
  of `T-094`'s `EpisodeCheckController`, which Check now beside that warning
  reaches through `share.series.episodes.check` (`D-021`). The command and the
  controller are extended here, never created.
- Deleting `lockDown()`, the play route, `PlaybackController`, the Vimeo
  check and `inline` arm in `T-089`'s `SharedController::opensAs()`,
  `MediaLink::$embed` and the `<iframe>` path.

**Out:**

- Any per-Peer grant, `vendor_grants`, `series_containers` or the
  `GrantsPeerAccess` contract (`T-091`) — nothing here creates a row in either.
- `CheckEpisodeItemsCommand` itself, its schedule line,
  `VendorAccessService::checkItems()`, `EpisodeCheckController` itself, its
  route, its throttle and container arm, every `series.episode_check.*` line
  and the `missingSince` prop (`T-094`); `VendorAccessService::checkEpisode()`
  and `EpisodeCheckOutcome`, which that arm reads (`T-091`).
- The Peer's vendor identity (`T-092`): neither vendor needs one.
- `PlaybackTicketService::issue()`, which keeps its signature and its tests;
  only the route and the controller that called it go.
- Vimeo's password showcase and YouTube's unlisted playlist. Both are real
  containers and both are a second mode; the spike's showcase and playlist steps
  answer whether they are worth a task, and the answer is a draft, not this.
- Uploading to either vendor, replacing a video from Qori, and reading analytics.
- Vimeo live events, and YouTube channel memberships — the members API is
  read-only and limited to the channel's own creator, so Qori can neither add nor
  check a member.
- Dropbox video, which `EpisodeType::Video` still allows and `T-096` owns.

**Split:** it stays whole. The two providers are one shape — connect, pick,
store, open, check — and splitting them would build the picker page, the
`checkDue()` pass and the `ListsVideos` contract twice or leave one provider waiting on a
file the other holds.

## Files

| Path                                                                                                                                                                                                                              | Change | Notes                                                                                                     |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------- |
| `app/Enums/ConnectionProvider.php` `app/Enums/EpisodeProvider.php` `app/Enums/EpisodeType.php`                                                                                                                                    | edit   | `YouTube` on the first two, `vendor()`, `connection()`, `isAccountBound()` (false), `allowedProviders()`  |
| `app/Enums/ProviderTier.php`                                                                                                                                                                                                      | edit   | `T-044` creates it with Google's two cases; four more here                                                |
| `app/Enums/VideoPrivacy.php` `app/Enums/VideoCheck.php`                                                                                                                                                                           | new    | The vendor state the picker reads, and the code the daily check writes                                    |
| `app/Integrations/Contracts/ListsVideos.php`                                                                                                                                                                                      | new    | Read-only: list, read one                                                                                 |
| `app/Integrations/Vimeo/VimeoVideos.php`                                                                                                                                                                                          | edit   | `lockDown()` deleted; `linkFor()` returns the stored page URL; `ListsVideos`                              |
| `app/Integrations/Vimeo/VimeoAccounts.php`                                                                                                                                                                                        | new    | `ConnectsAccounts`; no refresh token                                                                      |
| `app/Integrations/Google/YouTubeVideos.php` `app/Integrations/Google/YouTubeAccounts.php`                                                                                                                                         | new    | Beside `T-044`'s `GoogleAccounts`, on the same Google client                                              |
| `app/Data/VideoItem.php` `app/Data/VideoPage.php`                                                                                                                                                                                 | new    | What a picker row is                                                                                      |
| `app/Data/MediaLink.php`                                                                                                                                                                                                          | edit   | `$embed` removed with its last reader                                                                     |
| `app/Services/VideoLibraryService.php`                                                                                                                                                                                            | new    | Lists, attaches, checks                                                                                   |
| `app/Services/PlaybackTicketService.php`                                                                                                                                                                                          | edit   | The class docblock (`:16-26`): Vimeo is a page, not a framed player                                       |
| `app/Http/Controllers/Share/VideoPickerController.php`                                                                                                                                                                            | new    | `show`, `store`, `replace`                                                                                |
| `app/Http/Requests/Share/StoreVideoEpisodeRequest.php` `app/Http/Requests/Share/ReplaceEpisodeVideoRequest.php`                                                                                                                   | new    | Form Requests only                                                                                        |
| `app/Http/Controllers/Share/SeriesController.php`                                                                                                                                                                                 | edit   | `checkCode`, `checkUrl` and the picker URLs on each Episode (`:158-166`), beside `T-094`'s `missingSince` |
| `app/Http/Controllers/Share/EpisodeCheckController.php`                                                                                                                                                                           | edit   | `T-094`'s class; the Vimeo and YouTube arm and its flash mapping                                          |
| `app/Support/ProviderSections.php`                                                                                                                                                                                                | edit   | `vimeo` and `youtube` entries in `ESSENTIAL`; `T-044` creates the class                                   |
| `app/Http/Controllers/Shared/PlaybackController.php`                                                                                                                                                                              | delete | The JSON play route's action                                                                              |
| `app/Http/Controllers/Shared/SharedController.php`                                                                                                                                                                                | edit   | `T-089`'s `opensAs()` loses the `inline` branch                                                           |
| `app/Console/Commands/CheckEpisodeItemsCommand.php`                                                                                                                                                                               | edit   | `T-094`'s `qori:episodes:check`; the `checkDue()` call, `$description` widened                            |
| `app/Providers/IntegrationServiceProvider.php`                                                                                                                                                                                    | edit   | `YouTubeVideos` into `media-providers` (`:35`); a `video-libraries` tag; two connectors                   |
| `routes/share/episodes.php` `routes/shared.php`                                                                                                                                                                                   | edit   | Three picker routes and the header's id-only line qualified; `shared.play` removed                        |
| `resources/js/pages/share/series/PickVideo.vue`                                                                                                                                                                                   | new    | The picker                                                                                                |
| `resources/js/pages/share/series/Show.vue`                                                                                                                                                                                        | edit   | Video kinds link to the picker; the warning beside an Episode, with Check now                             |
| `resources/js/pages/shared/Show.vue`                                                                                                                                                                                              | edit   | The fetch, `openEpisode()`, `<iframe>` and `OpenEpisode` removed                                          |
| `lang/en/series.php` `lang/en/connections.php` `lang/en/errors.php`                                                                                                                                                               | edit   | Copy below; `connections.php` is `T-044`'s file; `series.episode_check.*` is `T-094`'s                    |
| `config/qori.php` `config/services.php`                                                                                                                                                                                           | edit   | `connections.youtube`, for the retention figure; Vimeo's client                                           |
| `database/migrations/2026_09_18_000000_add_item_checks_to_episodes.php`                                                                                                                                                           | new    | Two columns                                                                                               |
| `database/seeders/DesignReviewSeeder.php`                                                                                                                                                                                         | edit   | Its Vimeo content key is wrong today (`:353`, `:380`, `:699`) — see Notes                                 |
| `tests/Fixtures/vimeo/oauth-token.json` `tests/Fixtures/vimeo/me.json` `tests/Fixtures/vimeo/me-videos.json` `tests/Fixtures/vimeo/video-get.json` `tests/Fixtures/vimeo/errors-video-404.json`                                   | new    | From the spike; the directory is new                                                                      |
| `tests/Fixtures/youtube/oauth-token.json` `tests/Fixtures/youtube/channels-list.json` `tests/Fixtures/youtube/playlist-items-list.json` `tests/Fixtures/youtube/videos-list.json` `tests/Fixtures/youtube/videos-list-empty.json` | new    | From the spike; the directory is new                                                                      |
| `tests/Feature/Storage/VideoPickerTest.php` `tests/Feature/Storage/VideoEpisodeOpenTest.php`                                                                                                                                      | new    | 10 and 6 cases                                                                                            |
| `tests/Feature/Console/CheckEpisodeItemsCommandTest.php`                                                                                                                                                                          | edit   | `T-094`'s file; 8 cases added, the video pass                                                             |
| `tests/Feature/Series/EpisodeCheckTest.php`                                                                                                                                                                                       | edit   | `T-094`'s file; 4 cases added, the Vimeo and YouTube arm                                                  |
| `tests/Unit/Data/VideoItemTest.php`                                                                                                                                                                                               | new    | 2 cases                                                                                                   |
| `tests/Feature/Storage/PlaybackTest.php` `tests/Feature/Storage/OpenEpisodeTest.php` `tests/Feature/Storage/MediaLifetimeTest.php` `tests/Feature/Series/EpisodeRoutesTest.php`                                                   | edit   | See Tests; `OpenEpisodeTest.php` is `T-089`'s new file                                                    |
| `docs/flows/storage.md` `docs/flows/series.md` `docs/tinker/series.md`                                                                                                                                                            | edit   | The providers table and the Open chain; the picker chain; the recipe (`:44-46`)                           |

There is no `database/factories/EpisodeFactory.php` to change: Episodes are
built through `EpisodeService::add()` everywhere, and the two new columns are
nullable and written only by `VideoLibraryService::check()`, from the command
and from Check now, and cleared by a re-pick.

`docs/flows/vendor-access.md` is `T-091`'s and is not created or claimed here:
nothing in this task grants. `docs/project-plan.md` §8's Vimeo cell (`:222`)
still describes the domain whitelist; `T-094`, which this task depends on,
claims that file and rewrites §8, so this task leaves it alone — see Notes.
`routes/console.php` is not edited: the schedule line is `T-094`'s.

## Database

| Table      | Column       | Type       | Null | Default | Index / constraint                                          |
| ---------- | ------------ | ---------- | ---- | ------- | ----------------------------------------------------------- |
| `episodes` | `checked_at` | timestamp  | yes  | null    | Last successful vendor read; index `(provider, checked_at)` |
| `episodes` | `check_code` | string(30) | yes  | null    | A `VideoCheck` value, or null when the last read was clean  |

Migration: `database/migrations/2026_09_18_000000_add_item_checks_to_episodes.php`

`episodes` carries no `group_id` and no `BelongsToGroup`: tenancy lives on the
parent Series (`app/Models/Episode.php:11-20`), and these two columns change
nothing about that.

## Code

```php
namespace App\Enums;

// EpisodeProvider: case YouTube = 'youtube'; connection(): self::YouTube => ConnectionProvider::YouTube;
// isAccountBound(): self::YouTube => false — T-044's method; a YouTube id plays without the account, as a Vimeo id does

enum VideoPrivacy: string { case Public = 'public'; case Unlisted = 'unlisted'; case Private = 'private'; case Team = 'team'; }

/** What the daily read found. Null on the Episode means the last read was clean. */
enum VideoCheck: string
{
    case Missing = 'missing';              // deleted, or no longer readable with this connection
    case NotShareable = 'not_shareable';   // Vimeo Private or Team; YouTube private — the Peer is refused
    case AgeGated = 'age_gated';           // unrated or Mature on Vimeo; ytAgeRestricted — the Peer is not refused
    case Unreadable = 'unreadable';        // the vendor could not be asked; nobody is told, the next run retries
                                           // — this task's only analogue of VendorGrantStatus::Pending. Written only
                                           // over null or Unreadable: the three findings above stay until a read succeeds

    /** Whether a Peer opening this Episode is refused. Missing and NotShareable only. */
    public function blocksThePeer(): bool;
}
```

```php
namespace App\Integrations\Contracts;

/**
 * Reading a creator's own video library. Read-only on purpose: YouTube's
 * Developer Policy III.E.3 forbids an API client changing a video's visibility
 * unless the authorising user says to, and Qori never has that instruction.
 * $timeoutSeconds is the caller's budget, which the vendor's client may only
 * shorten: it waits the shorter of its own TIMEOUT_SECONDS and the budget
 * (D-034). It travels as a parameter, as T-044's and T-091's contracts take
 * it, because an integration may not import App\Services.
 */
interface ListsVideos
{
    public function provider(): EpisodeProvider;
    public function videos(Connection $connection, ?string $cursor, int $perPage, int $timeoutSeconds): VideoPage;
    /** @throws AppException notFound errors.series.video_not_found when the vendor no longer has it */
    public function video(Connection $connection, string $externalId, int $timeoutSeconds): VideoItem;
}

namespace App\Data;

class VideoItem
{
    public function __construct(
        public EpisodeProvider $provider,
        public string $externalId,
        public string $title,
        /** The watch page, exactly as the vendor gave it — Vimeo's privacy hash included. */
        public string $url,
        public VideoPrivacy $privacy,
        public bool $ageGated,
        public ?int $durationSeconds = null,
        public ?string $thumbnailUrl = null,
    ) {}

    /** Public or Unlisted, on any tier (D-019); Private and Vimeo's Team are not. */
    public function isShareable(): bool;
    /** @return array<string, mixed> vimeo_id + url, or youtube_id — the Episode content */
    public function content(): array;
}

class VideoPage { public function __construct(/** @var list<VideoItem> */ public array $items, public ?string $nextCursor = null) {} }
```

The four integration classes are `App\Integrations\Vimeo\{VimeoVideos,
VimeoAccounts}` and `App\Integrations\Google\{YouTubeVideos, YouTubeAccounts}` —
one folder per vendor account, so YouTube sits beside `T-044`'s `GoogleAccounts`
on the same Google client. `VimeoVideos` keeps `ResolvesMedia` and gains
`ListsVideos`; the two `Accounts` classes implement `T-044`'s `ConnectsAccounts`;
all four are bound in `IntegrationServiceProvider`, where `ResolvesMedia`
already names the method `provider()`.
`VimeoAccounts::refreshesOnSchedule()` is false — Vimeo issues no refresh token
and its Developer Addendum §5.4 forbids extending one — and
`YouTubeAccounts`'s is true, reusing `GoogleAccounts`' token and revoke URLs and
`config('services.google')`. Every call below sets its timeout inside the
integration, the shorter of the vendor's own limit and the budget passed in
(`D-034`): `VimeoVideos::TIMEOUT_SECONDS` is the 15 seconds
`app/Integrations/Vimeo/VimeoVideos.php:43` and `:58` set today, which
`VimeoAccounts` uses too, and both YouTube classes use
`GoogleAccounts::TIMEOUT_SECONDS` (20, `T-044`), Google's one limit, as they
reuse that class's endpoints; none retries. Both `Accounts` classes answer
`T-044`'s landing contract, a `ConnectionLanding` read in the vendor's words:
`YouTubeAccounts` reads Google's landing exactly as `GoogleAccounts` does and
checks `youtube.readonly` against its `requiredScopes()`; `VimeoAccounts`
reads `error=access_denied` as `Declined` (provisional until the spike's round
trip), checks `private`, and revokes a short token at Vimeo, best effort.
`VideoLibraryService` calls the contracts and never `Http::` itself. **No
field here has been observed**; each cites the vendor page and owes the
fixture its spike will produce.

| Call                                                                                                            | Read from it                                                                                                                                                                                                                | Fixture, owed                      |
| --------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Vimeo `GET /me/videos?fields=uri,name,link,duration,privacy.view,content_rating,pictures.sizes&page=&per_page=` | `data[]`, `paging.next` as the cursor ([reference](https://developer.vimeo.com/api/reference/videos))                                                                                                                       | `vimeo/me-videos.json`             |
| Vimeo `GET /videos/{id}?fields=…`                                                                               | `uri` (`/videos/987654321`), `name`, `link`, `privacy.view`, `content_rating`                                                                                                                                               | `vimeo/video-get.json`             |
| Vimeo `privacy.view` values                                                                                     | `anybody`=Public, `unlisted`=Unlisted, `nobody`=Private, `team`=Team, `disable`=Embed only                                                                                                                                  | —                                  |
| Vimeo `GET /me?fields=uri,name`                                                                                 | `ConnectedAccount` for the Integrations page                                                                                                                                                                                | `vimeo/me.json`                    |
| Vimeo `POST https://api.vimeo.com/oauth/access_token`, authorize `…/oauth/authorize`, scope `private`           | ([authentication](https://developer.vimeo.com/api/authentication))                                                                                                                                                          | `vimeo/oauth-token.json`           |
| YouTube `GET /youtube/v3/channels?part=contentDetails&mine=true` (1 unit)                                       | `items[0].contentDetails.relatedPlaylists.uploads`                                                                                                                                                                          | `youtube/channels-list.json`       |
| YouTube `GET /youtube/v3/playlistItems?part=contentDetails&playlistId=&maxResults=&pageToken=` (1 unit)         | the ids and `nextPageToken` ([playlistItems](https://developers.google.com/youtube/v3/docs/playlistItems/list))                                                                                                             | `youtube/playlist-items-list.json` |
| YouTube `GET /youtube/v3/videos?part=snippet,status,contentDetails&id=` (1 unit, up to 50 ids)                  | `status.privacyStatus` (`private\|public\|unlisted`), `contentDetails.contentRating.ytRating === 'ytAgeRestricted'`, `snippet.title`, `snippet.thumbnails` ([videos](https://developers.google.com/youtube/v3/docs/videos)) | `youtube/videos-list.json`         |
| YouTube, a video that is gone                                                                                   | an empty `items[]`                                                                                                                                                                                                          | `youtube/videos-list-empty.json`   |

`search.list` is never called: it costs 100 units and carries its own
100-calls-a-day cap, against one 10,000-unit daily quota shared by every creator
on Qori's project
([getting started](https://developers.google.com/youtube/v3/getting-started)).
`YouTubeVideos::linkFor()` returns `https://www.youtube.com/watch?v=` plus
`content['youtube_id']`; `VimeoVideos::linkFor()` returns `content['url']`
unchanged. Neither calls the vendor, and both refuse first — with
`AppException::notFound('errors.playback.item_unavailable', …)`, rendered by
`T-089`'s Open route as Qori's 404 page — when the Episode's `check_code` is a
`VideoCheck` whose `blocksThePeer()` is true.

```php
namespace App\Services;

class VideoLibraryService
{
    /** Seconds one vendor call may take inside the creator's own request. Provisional. */
    public const REQUEST_TIMEOUT_SECONDS = 5;
    /** Seconds one vendor call may take inside the daily command. Provisional. */
    public const SWEEP_TIMEOUT_SECONDS = 30;
    /** Videos on one picker page. Provisional. */
    public const PAGE_SIZE = 24;
    /** An Episode is re-read once it is this old. Provisional, and inside YouTube's 30-day limit. */
    public const RECHECK_HOURS = 20;

    /** @param iterable<ListsVideos> $libraries */
    public function __construct(private iterable $libraries, private CurrentGroup $current, private ConnectionService $connections) {}

    public function libraryFor(EpisodeProvider $provider): ?ListsVideos;   // null → errors.connections.not_available (T-044's key)
    /** The connection through ConnectionService::fresh(); refuses when it is not isLive(). */
    public function page(EpisodeProvider $provider, ?string $cursor): VideoPage;
    /** Reads the one video back before it is stored: shareable and not age-gated, or refused. */
    public function attach(EpisodeProvider $provider, string $externalId): VideoItem;
    /**
     * One Episode re-read; writes checked_at and check_code; never throws; null means clean. Returns what this
     * read found, Unreadable included, but never stores Unreadable over Missing, NotShareable or AgeGated.
     * checkDue() passes SWEEP_TIMEOUT_SECONDS; the video arm of T-094's EpisodeCheckController passes REQUEST_TIMEOUT_SECONDS (D-021).
     */
    public function check(Episode $episode, int $timeoutSeconds = self::SWEEP_TIMEOUT_SECONDS): ?VideoCheck;
    /** The command's pass for the current Group: Episodes on these providers older than RECHECK_HOURS. Rows touched. */
    public function checkDue(): int;
}
```

```php
namespace App\Http\Controllers\Share;

class VideoPickerController extends Controller
{
    use ResolvesShareSeries;

    public function __construct(private VideoLibraryService $videos) {}

    /** Inertia share/series/PickVideo; ?cursor= and ?episode= come from the request. */
    public function show(Request $request, string $group, string $series, EpisodeProvider $episodeProvider, Terminology $terminology): Response;
    public function store(StoreVideoEpisodeRequest $request, string $group, string $seriesId, EpisodeProvider $episodeProvider, EpisodeService $episodes, Terminology $terminology): RedirectResponse;
    /** The provider comes from the Episode, never the request: type and provider cannot move (EpisodeService:110-120). */
    public function replace(ReplaceEpisodeVideoRequest $request, string $group, string $seriesId, string $episodeId, EpisodeService $episodes, Terminology $terminology): RedirectResponse;
}

// App\Console\Commands\CheckEpisodeItemsCommand — T-094's class (D-021); this task edits it and creates nothing
// $signature and T-094's schedule line in routes/console.php stay as T-094 wrote them
protected $description = 'Re-read the files and videos every episode points at, and flag the ones that stopped working';
public function handle(VendorAccessService $vendorAccess, VideoLibraryService $videos, CurrentGroup $current): int;   // $videos added here
// foreach (Group::query()->cursor() as $group): $current->runFor($group, fn (): int => $vendorAccess->checkItems() + $videos->checkDue())
// — T-094's loop, with this task's term added; no acrossAllGroups() caller, as T-091's sweep and T-044's refresh do it.
```

```php
namespace App\Http\Controllers\Share;

/**
 * Check now beside an Episode's check warning (D-021). T-094's class: T-094 creates it with its route, its
 * MANUAL_CHECK_SECONDS throttle, the series.episode_check.* flashes and the container arm; this task adds the
 * Vimeo and YouTube arm and nothing else. Every Episode is read through the Series, so tenancy holds.
 */
class EpisodeCheckController extends Controller
{
    // __invoke()'s parameters are T-094's; VideoLibraryService $videos is this task's addition to them
}

// __invoke(), this task's arm only — the lookup, the 404s, the throttle and the wait flash before it are T-094's:
//   $flash = match ($episode->provider) {
//       EpisodeProvider::Vimeo, EpisodeProvider::YouTube => match ($videos->check($episode, VideoLibraryService::REQUEST_TIMEOUT_SECONDS)) {
//           null => 'series.episode_check.clear',
//           VideoCheck::Unreadable => 'series.episode_check.unreadable',
//           default => 'series.episode_check.still',   // Missing, NotShareable or AgeGated
//       },
//       // T-094's container arm, unchanged, for a provider T-091's VendorAccessService::handles() accepts:
//       // checkEpisode() returns EpisodeCheckOutcome — Clear → clear, Flagged → still,
//       // NeedsCreator → needs_creator, Unreadable → unreadable
//   };
//   the flash is filled and sent as T-094 fills and sends it for its own arm; back() to the Series page, which re-reads
//   checkCode and shows the warning or its absence
```

```php
// app/Support/ProviderSections.php — T-044's ESSENTIAL; these two entries are this task's. Keys are relative to
// connections.providers.<provider>.limits., in D-021's order: what a Peer needs, then what stops sharing outright.
'vimeo' => [
    'vimeo_free' => ['common.rating', 'vimeo_free.public', 'common.team'],
    'vimeo_paid' => ['common.rating', 'vimeo_paid.unlisted', 'common.team'],
],
'youtube' => [
    'youtube_personal' => ['common.unlisted', 'common.age'],
    'youtube_workspace' => ['common.unlisted', 'common.age', 'youtube_workspace.admin'],
],
```

`store()` calls `attach()`, then `EpisodeService::add($series, $title,
EpisodeType::Video, $episodeProvider, $item->content(), $isPreview)`, and flashes
`series.episode_added`. `replace()` calls `attach()`, then
`EpisodeService::update($series, $episodeId, ['content' => $item->content()])` —
which already accepts `content` (`app/Services/EpisodeService.php:121-140`) — and
clears `checked_at` and `check_code` so the next run re-reads the new video.

`SeriesController::show()` adds `'checkCode' => $episode->check_code?->value` to
each Episode (`:158-166`), beside `T-094`'s `missingSince`, which stays null on
a video Episode, `'checkUrl' => route('share.series.episodes.check', …)`
when that code is set and is not `unreadable` (null otherwise), and a picker URL
per video provider; `Show.vue` renders an `InlineNotice` from
`series.video_check.*` beside an Episode whose `checkUrl` is set, with a Check now
`Form` button labelled `series.episode_check.check_now` posting to `checkUrl`
inside it, and the Episode form replaces the reference field with a link to the picker
when the kind is Video and the provider is Vimeo or YouTube (`:198-203`,
`:236-243`). `T-089`'s `SharedController::opensAs()` becomes
`$episode->isLive() ? null : 'tab'`, and `resources/js/pages/shared/Show.vue`
loses `openEpisode()`, `open`, `opening`, `failed`, the `OpenEpisode` interface
and the `<iframe>` (`:63-113`, `:254-264`).

## Copy

| Key                                                                 | File                      | English                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `series.videos.title`                                               | `lang/en/series.php`      | Choose a video for this :series                                                                                                                                                                                                                                          |
| `series.videos.intro.vimeo`                                         | `lang/en/series.php`      | These are the videos in the Vimeo account you connected. Pick the one this :episode plays.                                                                                                                                                                               |
| `series.videos.intro.youtube`                                       | `lang/en/series.php`      | These are the videos on the YouTube channel you connected. Pick the one this :episode plays.                                                                                                                                                                             |
| `series.videos.link_note`                                           | `lang/en/series.php`      | Unlisted videos are open to anyone holding the link. Qori shows it only to :peer_plural with access, and can't stop one of them passing it on.                                                                                                                           |
| `series.videos.choose`                                              | `lang/en/series.php`      | Use this video                                                                                                                                                                                                                                                           |
| `series.videos.more`                                                | `lang/en/series.php`      | Show more                                                                                                                                                                                                                                                                |
| `series.videos.empty`                                               | `lang/en/series.php`      | There are no videos in this account yet. Upload one, then come back.                                                                                                                                                                                                     |
| `series.videos.replace_title`                                       | `lang/en/series.php`      | Choose a different video for :title                                                                                                                                                                                                                                      |
| `series.videos.unusable.private`                                    | `lang/en/series.php`      | Private, so only you can watch it. Change it to Public or Unlisted and it will show up here.                                                                                                                                                                             |
| `series.videos.unusable.team`                                       | `lang/en/series.php`      | Limited to your team, so anyone outside it is asked to log in. Change it to Public or Unlisted to use it here.                                                                                                                                                           |
| `series.videos.unusable.age_gated`                                  | `lang/en/series.php`      | Age-restricted, so only people signed in and over 18 can watch. Lift the restriction, or pick another video.                                                                                                                                                             |
| `series.video_replaced`                                             | `lang/en/series.php`      | That :episode plays :title now.                                                                                                                                                                                                                                          |
| `series.video_check.title`                                          | `lang/en/series.php`      | Check this :episode                                                                                                                                                                                                                                                      |
| `series.video_check.missing`                                        | `lang/en/series.php`      | Qori can no longer find this video in the account you connected. Nobody with access can watch it. Pick the video again, or remove the :episode.                                                                                                                          |
| `series.video_check.not_shareable`                                  | `lang/en/series.php`      | This video is private now, so nobody with access can watch it. Set it back to Public or Unlisted where it lives, then press Check now.                                                                                                                                   |
| `series.video_check.age_gated`                                      | `lang/en/series.php`      | This video is age-restricted now, so only people signed in and over 18 can watch it. Lift the restriction where it lives, then press Check now.                                                                                                                          |
| `connections.providers.vimeo.description`                           | `lang/en/connections.php` | Show videos from your own Vimeo account. :peer_plural with access watch them on vimeo.com, and nobody needs a Vimeo account.                                                                                                                                             |
| `connections.providers.vimeo.tiers.vimeo_free.label`                | `lang/en/connections.php` | Free Vimeo                                                                                                                                                                                                                                                               |
| `connections.providers.vimeo.tiers.vimeo_paid.label`                | `lang/en/connections.php` | Paid Vimeo plan                                                                                                                                                                                                                                                          |
| `connections.providers.vimeo.limits.common.rating`                  | `lang/en/connections.php` | Rate each video All Audiences. Without a rating, people in the UK, EU and Brazil who are not logged in to Vimeo may be asked to log in and prove their age.                                                                                                              |
| `connections.providers.vimeo.limits.common.team`                    | `lang/en/connections.php` | Don't limit a video to your team or workspace, or anyone outside it is asked to log in.                                                                                                                                                                                  |
| `connections.providers.vimeo.limits.common.replace`                 | `lang/en/connections.php` | To update a video, use Replace in Vimeo and the link stays the same. Deleting it and uploading again makes a new video, so the :episode needs picking again.                                                                                                             |
| `connections.providers.vimeo.limits.vimeo_free.public`              | `lang/en/connections.php` | Free Vimeo videos can only be Public or Private, and Qori can't make one Unlisted. A video you use here has to be Public: anyone who comes across it on Vimeo can watch.                                                                                                 |
| `connections.providers.vimeo.tiers.vimeo_free.recommended`          | `lang/en/connections.php` | Qori recommends a paid Vimeo plan if it matters to you who finds these videos. On Free it's your call, and Qori won't stand in the way.                                                                                                                                  |
| `connections.providers.vimeo.limits.vimeo_paid.unlisted`            | `lang/en/connections.php` | Set each video to Public or Unlisted. A Private video can't be watched by anyone you share with.                                                                                                                                                                         |
| `connections.providers.vimeo.limits.vimeo_paid.enterprise`          | `lang/en/connections.php` | On Enterprise, your admin's privacy restrictions can stop you setting a video to Unlisted.                                                                                                                                                                               |
| `connections.providers.vimeo.tiers.vimeo_paid.recommended`          | `lang/en/connections.php` | Public and Unlisted both work for :peer_plural with access; choose Unlisted if you'd rather keep a video off your Vimeo profile and out of Vimeo search.                                                                                                                 |
| `connections.providers.youtube.name`                                | `lang/en/connections.php` | YouTube                                                                                                                                                                                                                                                                  |
| `connections.providers.youtube.description`                         | `lang/en/connections.php` | Show videos from your own YouTube channel. :peer_plural with access watch them on youtube.com, and nobody needs an account.                                                                                                                                              |
| `connections.providers.youtube.tiers.youtube_personal.label`        | `lang/en/connections.php` | Personal or Brand Account channel                                                                                                                                                                                                                                        |
| `connections.providers.youtube.tiers.youtube_workspace.label`       | `lang/en/connections.php` | YouTube on a work or school account                                                                                                                                                                                                                                      |
| `connections.providers.youtube.limits.common.unlisted`              | `lang/en/connections.php` | Set each video to Unlisted or Public. People with access watch on YouTube without signing in.                                                                                                                                                                            |
| `connections.providers.youtube.limits.common.age`                   | `lang/en/connections.php` | Don't age-restrict the videos you use here. People would have to be signed in and over 18 to watch.                                                                                                                                                                      |
| `connections.providers.youtube.limits.common.replace`               | `lang/en/connections.php` | YouTube can't replace a video. Trimming it, or editing the title, keeps the link. Uploading it again makes a new link, so the :episode needs picking again.                                                                                                              |
| `connections.providers.youtube.limits.common.checks`                | `lang/en/connections.php` | YouTube only lets Qori keep what it reads for :days days, so Qori re-reads every video daily and tells you if one is deleted, made private or age-restricted.                                                                                                            |
| `connections.providers.youtube.tiers.youtube_personal.recommended`  | `lang/en/connections.php` | Public and Unlisted both work for :peer_plural with access; choose Unlisted if you'd rather keep a video off your channel page and out of YouTube search.                                                                                                                |
| `connections.providers.youtube.limits.youtube_workspace.admin`      | `lang/en/connections.php` | Your admin can turn YouTube off or block Qori. People watching on their own work or school account may be limited by their admin too.                                                                                                                                    |
| `connections.providers.youtube.tiers.youtube_workspace.recommended` | `lang/en/connections.php` | Public and Unlisted both work for :peer_plural with access, and Unlisted keeps a video off your channel page and out of YouTube search; check with your admin before you connect, so a policy change doesn't take your :episode_plural down with it.                     |
| `connections.providers.vimeo.disconnect.in_qori`                    | `lang/en/connections.php` | Your :episode_plural keep their videos, and :peer_plural with access keep watching them on Vimeo. Until you connect :account again, Qori can't check those videos or warn you if one is deleted or made private, and you can't pick new ones.                            |
| `connections.providers.vimeo.account_change.in_qori`                | `lang/en/connections.php` | Your :episode_plural use videos in :current. Once you switch, Qori checks them with :incoming, which can't see :current's Unlisted videos, so at its next check each of those is marked missing and stops opening from Qori until you pick a video again from :incoming. |
| `connections.providers.youtube.disconnect.in_qori`                  | `lang/en/connections.php` | Your :episode_plural keep their videos, and :peer_plural with access keep watching them on YouTube. Until you connect :account again, Qori can't check those videos or warn you if one is deleted, made private or age-restricted, and you can't pick new ones.          |
| `connections.providers.youtube.account_change.in_qori`              | `lang/en/connections.php` | Your :episode_plural keep their videos from :current, and Qori goes on checking them, because a Public or Unlisted video can be read from any account. Once you switch, the videos you can pick are :incoming's.                                                         |
| `errors.playback.item_unavailable.message`                          | `lang/en/errors.php`      | That :episode isn't there to watch any more.                                                                                                                                                                                                                             |
| `errors.playback.item_unavailable.resolution`                       | `lang/en/errors.php`      | Whoever shared it has been told. It's worth trying again in a day or two.                                                                                                                                                                                                |
| `errors.series.video_not_found.message`                             | `lang/en/errors.php`      | That video isn't in the account you connected any more.                                                                                                                                                                                                                  |
| `errors.series.video_not_found.resolution`                          | `lang/en/errors.php`      | Reload the list and pick one that is.                                                                                                                                                                                                                                    |
| `errors.series.video_not_shareable.message`                         | `lang/en/errors.php`      | That video can't be watched by anyone you share with.                                                                                                                                                                                                                    |
| `errors.series.video_not_shareable.resolution`                      | `lang/en/errors.php`      | Set it to Public or Unlisted where it lives, then pick it again.                                                                                                                                                                                                         |
| `errors.series.video_age_restricted.message`                        | `lang/en/errors.php`      | That video is age-restricted, so only people signed in and over 18 can watch it.                                                                                                                                                                                         |
| `errors.series.video_age_restricted.resolution`                     | `lang/en/errors.php`      | Lift the restriction where the video lives, then pick it again — or pick another video.                                                                                                                                                                                  |

Each tier also needs its `tiers.*.help` line and `connections.providers.vimeo.name`
("Vimeo"), in `T-044`'s shape. **All four tiers carry both a limits line and a
`tiers.*.recommended` line** (`D-018`): a tier that says only what it cannot do
is a shrug, and one that says only what Qori would prefer hides the limit, and
the creator reads both before connecting. The paid Vimeo and both YouTube
`recommended` lines present Public and Unlisted as equally fine, with Unlisted
for a creator who wants a video off their channel page or profile or out of
search (`D-019`). `:days` comes from
`config('qori.connections.youtube.data_retention_days')` — never restated in the
sentence. Every line with a noun placeholder is read through
`Terminology::line()`, and no article sits directly before one.

Which limitation lines sit above `T-044`'s disclosure is not in this table but
in `ProviderSections::ESSENTIAL` (Code); every other `limits.*` line above is in
`more`, in key order. Every `series.episode_check.*` line — `check_now`,
`clear`, `still`, `needs_creator`, `wait` and `unreadable` — belongs to Check now and is
`T-094`'s, written and filled there, so none is in this table; the
`unreadable` row this draft used to carry lives in `T-094` now. This task's arm
picks among `clear`, `still` and `unreadable` (Code) and adds no line. `still`
says "nothing has changed yet" even when a video moved from one finding to
another (private to age-restricted, say); the note beside the Episode names
the current one. The two
`disconnect.in_qori` and two `account_change.in_qori` lines are the ones
`T-044` asks of every connectable provider (`D-021` rule 3): no grant exists
for either vendor, so they say what happens to the stored videos and the
daily check, with `:account`, `:current` and `:incoming` filled as `T-044`
fills them. No
`series.video_check.*` line says Qori checks again tomorrow: the daily run
still happens, and Check now is the way a creator who has fixed something need
not wait for it (`D-021`).

## Routes

| Verb | Path                                                     | Name                          | Action                                |
| ---- | -------------------------------------------------------- | ----------------------------- | ------------------------------------- |
| GET  | `g/{group}/series/{series}/videos/{episodeProvider}`     | `share.series.videos.pick`    | `Share\VideoPickerController@show`    |
| POST | `g/{group}/series/{seriesId}/videos/{episodeProvider}`   | `share.series.videos.store`   | `Share\VideoPickerController@store`   |
| PUT  | `g/{group}/series/{seriesId}/episodes/{episodeId}/video` | `share.series.videos.replace` | `Share\VideoPickerController@replace` |

All three in `routes/share/episodes.php`, inside the existing `auth`,
`verified`, `group` group (`routes/share.php:24-27`); the file header's "every
parameter is an id" line (`:11-16`) gains the picker page as its exception.
`{episodeProvider}` binds implicitly to `EpisodeProvider`, and both routes add
`->whereIn('episodeProvider', ['vimeo', 'youtube'])`, so any other value —
`cloudflare_r2` or `google_drive` among them — is a 404 rather than a refusal
from `libraryFor()`, and each picker has one URL (`D-033`). The two it
carries have no underscore, so they need no slug. It is not `{provider}`, which `D-033` reserves for a
`ConnectionProvider` slug that `T-044` binds for every route: under that name
`vimeo` and `youtube` would be bound to `ConnectionProvider` cases, which the
actions' `EpisodeProvider` cannot take.
`share.series.episodes.check`
(`POST g/{group}/series/{seriesId}/episodes/{episodeId}/check`) is `T-094`'s
route; this task's arm is reached through it, and nothing is added to the file
for it (`D-021`).
**Removed:** `GET /shared/{series}/episodes/{episode}/play`, `shared.play`
(`routes/shared.php:42`), with `PlaybackController`.

## Tests

Every case fakes both vendors with `Http::fake()` from the fixtures above and
calls `Http::preventStrayRequests()` in `setUp()`. A Series used for a picker
case has a live `Connection` for its provider, because the picker lists the
creator's videos with their token and `VideoLibraryService::page()` refuses
without one — this task's rule, not `T-044`'s guard, which covers neither
provider.

**New: `tests/Feature/Storage/VideoPickerTest.php` — 10 cases**

1. `test_it_lists_the_connected_accounts_videos` — Vimeo; titles, privacy and the cursor reach the page.
2. `test_it_marks_a_private_video_as_unusable` — the row is listed with `series.videos.unusable.private` and no Use control.
3. `test_it_marks_an_age_restricted_video_as_unusable` — YouTube, `ytAgeRestricted`.
4. `test_choosing_a_vimeo_video_stores_the_id_and_the_whole_link` — `content['vimeo_id']` and `content['url']`, hash included.
5. `test_choosing_a_youtube_video_stores_the_id_alone` — `content['youtube_id']`, no url.
6. `test_choosing_a_video_that_is_no_longer_shareable_is_refused` — the read-back says Private; `errors.series.video_not_shareable`; no Episode.
7. `test_choosing_a_video_the_account_no_longer_has_is_refused` — 404 body; `errors.series.video_not_found`.
8. `test_re_picking_points_the_same_episode_at_another_video` — the Episode id is unchanged, `checked_at` and `check_code` cleared, progress intact.
9. `test_a_priced_series_accepts_a_video_episode` — a Series with `price_cents` and `currency` set; picking a Vimeo video and a YouTube video each stores an Episode, and nothing is refused.
10. `test_a_second_groups_series_is_not_found` — the picker is group-scoped.

**New: `tests/Feature/Storage/VideoEpisodeOpenTest.php` — 6 cases**

11. `test_a_vimeo_episode_redirects_to_the_stored_unlisted_link` — 302 to `vimeo.com`, hash intact; no vendor call.
12. `test_a_youtube_episode_redirects_to_the_watch_page` — 302 to `https://www.youtube.com/watch?v=…`.
13. `test_opening_records_the_episode_as_opened` — `T-089`'s gate still runs.
14. `test_a_video_the_last_check_could_not_find_is_refused_with_a_page` — `check_code` `missing`; 404 page carrying `errors.playback.item_unavailable.message`.
15. `test_an_age_gated_video_still_opens` — `check_code` `age_gated`; 302.
16. `test_the_play_route_is_gone` — `GET /shared/{id}/episodes/{id}/play` is a 404, and the Peer page carries no `<iframe>`.

**Extended: `tests/Feature/Console/CheckEpisodeItemsCommandTest.php` (`T-094`'s file) — 8 cases**

`T-094`'s cases in the file, its schedule case among them, stay as they are and
are expected to pass beside these.

17. `test_it_clears_the_code_on_a_video_that_is_still_fine` — `checked_at` moves, `check_code` null.
18. `test_it_flags_a_deleted_video` — empty `items[]`; `missing`.
19. `test_it_flags_a_video_that_went_private` — `not_shareable`.
20. `test_it_flags_an_age_restricted_video` — `age_gated`.
21. `test_a_vendor_that_cannot_be_asked_leaves_unreadable_and_tells_nobody` — 500 from the vendor on a clean Episode; `unreadable`; the Series page shows no notice.
22. `test_a_vendor_that_cannot_be_asked_keeps_the_last_finding` — an Episode already `not_shareable`, then a 500; `check_code` is still `not_shareable`, `checked_at` unchanged, and Open still refuses the Peer.
23. `test_it_skips_episodes_checked_within_the_cadence_and_crosses_groups` — a fresh Episode is not re-read; one due Episode in each of two Groups is.
24. `test_one_run_checks_videos_and_drive_files_together` — a Vimeo Episode and a `google_drive` Episode in one Group, faked from `vimeo/video-get.json` and `T-094`'s `tests/Fixtures/google/` responses; one `qori:episodes:check`; both are re-read, and each is written in its own shape.

**Extended: `tests/Feature/Series/EpisodeCheckTest.php` (`T-094`'s file) — 4 cases**

Each case posts to `share.series.episodes.check` as a collaborator of the Series' Group and follows the redirect to the Series page. `T-094`'s cases cover its container arm and everything before the arm is chosen — the throttle and its `wait` flash, and the 404 for another Group's Episode or one with nothing to check — so they hold for a video Episode with no case here; these cover the video arm.

25. `test_check_now_clears_a_video_the_creator_fixed` — `check_code` `not_shareable`; the fake answers Unlisted; one `videos.list` call; `check_code` null, `checked_at` moved; flash `series.episode_check.clear`; the Episode on the Series page has no `checkUrl`.
26. `test_check_now_on_a_video_that_is_still_private_keeps_the_warning` — the fake answers private; `check_code` `not_shareable`; flash `series.episode_check.still`.
27. `test_check_now_that_cannot_reach_the_vendor_changes_nothing_and_says_so` — a 500; `check_code` still `not_shareable`, `checked_at` unchanged; flash `series.episode_check.unreadable`.
28. `test_the_series_page_offers_check_now_only_beside_a_warning` — `checkUrl` is set for `missing`, `not_shareable` and `age_gated`, and null for a clean Episode and for `unreadable`; `missingSince` is null on every video Episode.

**New: `tests/Unit/Data/VideoItemTest.php` — 2 cases** (bare `PHPUnit\Framework\TestCase`)

29. `test_unlisted_and_public_are_shareable_and_private_is_not`
30. `test_the_content_shape_differs_by_provider` — Vimeo keeps the url, YouTube does not.

**Changed:**

- `tests/Feature/Storage/PlaybackTest.php` — `test_a_vimeo_video_resolves_to_an_embed_without_calling_vimeo` (`:143-155`) becomes `test_a_vimeo_video_resolves_to_its_watch_page`: the Episode content carries `vimeo_id` and `url`, the link is the stored url, and `MediaLink` no longer has `embed` to assert. `test_the_route_is_access_gated` (`:157-172`) goes with the play route — `T-089`'s `OpenEpisodeTest` gates the route that replaced it. The other `issue()` cases are untouched.
- `tests/Feature/Storage/OpenEpisodeTest.php` — `T-089`'s case 10: `opens` is now `tab` for a Vimeo Episode, never `inline`.
- `tests/Feature/Storage/MediaLifetimeTest.php` — the Vimeo Episode at `:98-100` stores `vimeo_id` and `url`, because `linkFor()` reads the url now; the lifetime assertions, the other cases and `MediaLifetime::minutesFor()` are unchanged.
- `tests/Feature/Series/EpisodeRoutesTest.php` — `test_a_vimeo_video_stores_its_id_not_a_path` (`:115-127`) posts through the picker instead of the reference field.
- `T-044`'s test that every `ProviderSections::ESSENTIAL` key exists and no tier lists more than `MAX_ESSENTIAL` runs over the `vimeo` and `youtube` entries with no new case.

Total: 30 new cases, 12 of them in `T-094`'s two files.

## Acceptance

- [ ] A creator connects Vimeo and YouTube from the Integrations page, reads the
      chosen tier's limitations and what Qori recommends before connecting, and
      picks a video from their own account without typing an id
- [ ] Free Vimeo is one of the four tiers on offer: its copy says the videos can
      only be Public and anyone who comes across one can watch, and the creator
      connects anyway — nothing refuses the tier, gates it behind a dialog or
      falls back to something else
- [ ] Each of the four tiers shows its recommendation and its essential lines
      above Connect, as `ProviderSections::ESSENTIAL` lists them, with every
      other line in the disclosure in the same section
- [ ] A Peer with access opens a Vimeo Episode and a YouTube Episode in a new
      tab, signed out of both vendors in a clean browser, and watches
- [ ] The creator replaces the video in Vimeo and the same Episode plays the new
      one; re-uploading on YouTube does not, and the daily check says so
- [ ] A deleted, privatised or age-restricted video is flagged to the creator on
      the Series page within a day, and the first two refuse the Peer with a
      Qori page rather than a dead vendor tab
- [ ] A creator who sets a flagged video back to Unlisted presses Check now and
      lands on the Series page with the warning gone and a flash saying so; one
      still private lands on the warning and `series.episode_check.still`; a
      vendor that cannot be reached leaves the warning where it was and flashes
      `series.episode_check.unreadable`
- [ ] `T-094`'s `qori:episodes:check` re-reads videos and folder files in one
      run, and its `EpisodeCheckController` answers Check now on a Vimeo and a
      YouTube Episode through this task's arm; this task adds no command,
      controller, route, schedule line or `series.episode_check.*` line
- [ ] The picker says plainly that anyone holding the link can watch, and no
      screen claims more protection than an unlisted link gives
- [ ] A priced Series holds a Vimeo and a YouTube Episode, and a Peer who bought
      it opens both
- [ ] Nothing sets a privacy setting, a domain whitelist or an embed rule at
      either vendor; `lockDown()`, the play route and the `<iframe>` are gone
- [ ] The spike's fixtures are committed, its responses kept dated and redacted
      in the report, and every faked payload comes from one
- [ ] `docs/flows/storage.md`, `docs/flows/series.md` and the tinker recipe
      describe what was built
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Is Vimeo Free offered at all, with its Public-only limitation stated, or is
  the dropdown paid-plans-only? Public means anyone on Vimeo can find the video
  — the owner's.~~ **Answered 17 September 2026 (`D-018`):** offered, with the
  Public-only limit and Qori's recommendation on screen before the creator
  connects. A tier is explained, never refused, and the platform a creator
  brings is the creator's own.
- ~~Do paid Series stay closed to both providers until YouTube's written approval
  (Developer Policies III.G.1.a/b) and Vimeo's §3.5 permission are in hand, and
  who asks? — the owner's.~~ **Answered 17 September 2026 (`D-019`):** both
  vendors hold Episodes in any Series, priced or free, with no guard or flag;
  nothing waits on either vendor's permission.
- Confirm the JSON play route, `PlaybackController`, `MediaLink::$embed` and the
  `<iframe>` die here, and that `PlaybackTicketService::issue()` stays until
  something else carries the ticket lifetimes — the owner's, recorded as `T-089`'s
  question and answered yes here.
- ~~`qori:episodes:check` as its own daily command, or folded into `T-091`'s
  `qori:access:reconcile` once that exists — the owner's, with `operations`.~~
  **Answered 17 September 2026 (`D-021`):** its own daily command, and one
  command with `T-094`, which had defined `qori:episodes:check` as well. On the
  same day the gatekeeper made `T-094` its owner: `T-094` creates
  `CheckEpisodeItemsCommand`, its schedule line, `EpisodeCheckController`,
  `share.series.episodes.check`, its throttle and every
  `series.episode_check.*` line, and this task adds its pass and its arm.
- The provisional numbers: `REQUEST_TIMEOUT_SECONDS` 5, `SWEEP_TIMEOUT_SECONDS`
  30, `PAGE_SIZE` 24, `RECHECK_HOURS` 20 — anyone's, with the spike's timings
  and YouTube's quota. The vendors' own limits are `VimeoVideos`' 15 seconds,
  as today, and `T-044`'s `GoogleAccounts::TIMEOUT_SECONDS` for YouTube.
- `VimeoAccounts` and `YouTubeAccounts` have no test cases here: their
  authorize URLs, `T-044`'s landing contract read in each vendor's words, the
  scope check, `refresh()` and `identity()` want cases of their own, as
  `T-044`'s `GoogleAccountsTest` has, and where they sit
  (`tests/Feature/Integrations/Vimeo/` and `tests/Feature/Integrations/Google/`)
  — anyone's, with `T-044`.
- `T-094`'s names used here — `CheckEpisodeItemsCommand`, its `handle()`
  parameters and per-Group closure, `VendorAccessService::checkItems()`,
  `EpisodeCheckController` and its `__invoke()` parameters,
  `MANUAL_CHECK_SECONDS`, the `series.episode_check.*` keys, the `missingSince`
  prop, its `tests/Fixtures/google/` responses and its two test files — and
  `T-091`'s `VendorAccessService::checkEpisode()` and `EpisodeCheckOutcome`,
  are taken from their drafts; re-check them when `T-094` is `ready` —
  anyone's.
- One shape for an Episode's check result: this draft adds
  `episodes.checked_at` and `check_code` columns and passes `checkCode` and
  `checkUrl`, while `T-091`'s `checkEpisode()` writes `content.checked_at` and
  `content.missing_since` and `T-094` passes `missingSince` and builds its
  Check now form's path on the page. One command and one Check now controller
  serve both, and two `checked_at`s on one Episode read as one fact. Does this
  task adopt `T-091`'s content keys and `T-094`'s `missingSince` (with the
  `VideoCheck` finding beside it), or add its columns as drafted — anyone's,
  with a developer.
- The four `disconnect.in_qori` and `account_change.in_qori` lines rest on
  unobserved behaviour: that a Vimeo token for another account cannot read an
  Unlisted video by id while a YouTube one can read any Public or Unlisted
  video, and that `check()` with no live connection stores nothing over a
  finding. The spike's steps confirm them — the spike's.
- The spike's answers, each of which can change a section above: whether the
  Unlisted link and its hash survive `POST /videos/{video_id}/versions`; which
  `content_rating` value means All Audiences; whether `private` alone is enough
  scope to list a creator's unlisted videos; whether Vimeo's token response
  carries `expires_on`; how OAuth chooses between a personal and a Brand Account
  channel — the spike's.
- Whether the daily read keeping a Vimeo token alive counts as "extending a
  token beyond its authorised duration" under Developer Addendum §5.4 — the
  owner's, and it is a legal reading, not a spike.
- ~~`docs/flows/storage.md`, `docs/flows/series.md` and `docs/tinker/series.md` are
  claimed by `T-094` too, and `docs/project-plan.md` §8 only by it; decide
  whether this task depends on `T-094`, or whether the provider table is split —
  the stream owner's.~~ Answered 17 September 2026: depends on `T-094`, which
  builds the item check and Check now (`D-021`).
- `T-044`'s names used here — `ConnectsAccounts`, `ConnectionService::fresh()`,
  `ProviderTier`, `Connection::isLive()`, `errors.connections.not_available`,
  `ProviderSections::ESSENTIAL` and `MAX_ESSENTIAL`, and
  `lang/en/connections.php`'s key shape — are taken from its draft; re-check when
  it is `ready` — anyone's.
- **From the privacy and terms drafts (`docs/pptcs/`, 19 September 2026):**
  YouTube's Developer Policies need the user to accept Qori's privacy policy
  before first use (III.A.2), a disconnect control and deleting stored YouTube
  data on disconnect or revocation (III.E), and backups kept 30 days or less.
  This draft keeps the video ids and tells the creator "Your Episodes keep
  their videos". Whether a kept video id is data YouTube requires deleted,
  and where acceptance is recorded, are settled before this is `ready` — the
  stream owner's, with `T-044`.
- **From the storage review's evidence table (20 September 2026):** the spike
  under Preconditions contradicts this task's own design. It is to be walked
  with "the exact scopes Qori will request — `private` at Vimeo,
  `youtube.readonly` at Google — never a broader diagnostic token", and its
  first step is to PATCH a video to Unlisted and read its `link`, while "Qori
  reads; it never changes a video's privacy" is the decision that chose those
  scopes in the first place. Either setting the privacy is creator-side setup
  done in the vendor's own web app before the spike starts, or the spike wants
  a scope this task refuses to ship. Recorded here and not resolved; the one
  answer ruled out is broadening consent to make the experiment pass — the
  owner's, with the spike.
- **From the storage review's rate-limit table (20 September 2026):** YouTube's
  quota-cost page (`V7`) keeps the 10,000-unit day for Qori's whole project and
  prices `videos.list` at one unit, which this task already reads as cheap.
  What it does not account for is that the unit is spent per stored Episode
  and not per Peer: `check()` takes one Episode, `checkDue()` walks them Group
  by Group, and enough Episodes falling due together spend the day every
  creator shares before a single Peer has opened anything — with the picker's
  `playlistItems` pages and every Check now on top. `videos.list` takes up to
  50 ids, as the call table already says, so the daily pass deduplicates video
  ids across Episodes and Groups and batches them, and `RECHECK_HOURS` is a
  number chosen against the bucket and not against staleness alone — anyone's,
  with the spike's timings.
- **From the storage review's rate-limit table (20 September 2026):** Vimeo's
  rate-limit page (`V8`) describes per-user, per-minute limits, a 429 and a
  pause of up to a minute, and publishes no general numeric allowance for the
  video API at all; the figure it does print belongs to its AI endpoints and is
  not the one to borrow. So the spike reads the applicable account's own limits
  and the response headers, and `checkDue()` needs a cooldown covering the rest
  of that authorisation's reads once one call comes back 429, rather than
  working on down the creator's videos and turning one throttle into a run of
  `VideoCheck::Unreadable` — anyone's, with the spike.
- **From the storage review's evidence table (20 September 2026):** the row on
  the combined Google authorisation names this task's "Vimeo and YouTube are
  two connections, not one" as documented and unobserved. Nobody has connected
  Drive and YouTube, and confirmed a Peer's Google identity, on one person and
  one project, then disconnected or rejected one of them and watched which of
  the other tokens stopped working. Until that is seen, the four
  `disconnect.in_qori` and `account_change.in_qori` lines, and the Integrations
  page's separate provider sections, promise an independence Qori has not
  observed — the spike's, with `T-044`.

## Re-scope log

None.

## Notes

`CLAUDE.md` says integrations expose `name()` and are bound in
`AppServiceProvider`; the code says `provider()`
(`app/Integrations/Contracts/ResolvesMedia.php:29`) and
`app/Providers/IntegrationServiceProvider.php:35`. This draft follows the code,
as `T-089` and `T-091` do.

`ResolvesMedia` still returns `MediaLink`, whose `expiresAt` is meaningless for
a vendor page that does not expire. `T-089`'s `VendorLink::fromMediaLink()`
drops it before the Peer surface sees it, and widening the contract for two
providers that are about to sit behind `T-091`'s `openLink()` would be a second
shape for one release. `linkFor()` therefore still computes a lifetime it does
not need — `T-089`'s `open()` drops it before the Peer surface sees it — which is
why `issue()`, `MediaLifetime::minutesFor()` and their tests stay as they are.

`DesignReviewSeeder` stores `['video_id' => '76979871']` for its Vimeo Episodes
(`:353`, `:380`, `:699`) while the request and the resolver use `vimeo_id`
(`StoreEpisodeRequest.php:189`, `VimeoVideos.php:64`), so every seeded Vimeo
Episode fails to resolve today. Fixed in the same edit as the new columns.

`docs/flows/storage.md:57` says Vimeo's protection is a domain whitelist set at
attach time, and `docs/project-plan.md:222` says the same; `D-016` voided both.
This task rewrites the flow row and leaves §8 to `T-094`.
`release-prerequisites.md:19` already says Vimeo Free is offered Public-only
(`D-018`) and that both vendors hold Episodes in paid Series with nothing to
wait on (`D-019`), so nothing there changes.

There is no config key for the Vimeo domain lock to remove: the lock lives in
`VimeoVideos::lockDown()`, which nothing in the repository calls, and in the two
documents above. `config/qori.php` gains `connections.youtube` beside
`T-044`'s `connections.google_drive`, holding YouTube's 30-day retention figure
so the copy interpolates it; Vimeo needs no key there.

`T-089` and `T-091` disagreed about where the Peer's grant-state copy lives;
`D-020` settled it as `shared.vendor_notice.*` in `lang/en/shared.php`, which
`T-089` creates. This task writes no Peer grant-state copy: a video the last
check refused still meets `errors.playback.item_unavailable`, because nothing
here is a grant.
