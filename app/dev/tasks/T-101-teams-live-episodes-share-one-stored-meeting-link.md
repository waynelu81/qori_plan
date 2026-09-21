---
id: T-101
title: Teams live Episodes share one stored meeting link
stream: storage
status: draft
owner: unassigned
estimate: M
depends: T-091, T-100, T-157
blocks: none
---

# T-101 — Teams live Episodes share one stored meeting link

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016`, the owner's BYO blueprint and the developer review of the same day;
> amended 17 September 2026 from `D-018`, which puts Teams in the beta release
> and offers every tier with its limits and Qori's advice on screen; amended
> the same day from `D-020` (a Peer who cannot join is sent to the Series
> page's notice) and `D-021` (each tier's essential lines above a disclosure,
> and the impact of a new link shown before it is saved). Amended on
> 18 September 2026 by `D-024` and `D-026`: `content['join_url']` on each live
> Episode is the primary link and `series_containers.url` is optional beside it,
> so a Series may hold sessions at different links and this draft's
> once-per-Series link is the connected convenience rather than the only place a
> link lives; and the Teams link parser moves from `app/Data/TeamsMeetingLink`
> to `app/Integrations/Teams/TeamsMeetingLink`, because a class that knows a
> vendor's host and path patterns is that vendor's code (`D-022`). Amended on
> 20 September 2026 by the cut of `T-091` in three and by `D-040`: the grant
> core stayed in `T-091`, the creator's surfaces went to `T-157`, and the
> meeting half of the container-change dialog came here and to `T-100`, which
> declares `ContainerChangeImpact::kind()`'s `meeting` arm and the
> `series.container_change.meeting.replace.*` lines — this task reads two of
> them and declares neither, so `depends:` now names all three tasks; and a
> grant is made when a Peer presses Open and at no other time, so the scheduled
> sweep this draft leaned on, and the Peer's Check again with it, are gone.

## Why

A live Episode on Microsoft Teams is a text field and nothing else.
`EpisodeType::allowedProviders()` gives `Live` the pair `Zoom, Teams`
(`app/Enums/EpisodeType.php:35`), `EpisodeProvider::Teams` maps to
`ConnectionProvider::Teams` (`app/Enums/EpisodeProvider.php:25`, `:42-51`), and
the join link is a string the creator pastes into a field labelled "Join link
(optional for now)" under a Zoom placeholder
(`resources/js/pages/share/series/Show.vue:236-243`, `:257-262`), stored as
`content['join_url']` (`app/Http/Requests/Share/StoreEpisodeRequest.php:184-196`).
Nothing reads it back: `PlaybackTicketService::resolve()` throws
`errors.playback.unsupported_provider` for a live Episode (`:75-89`), so the
Peer sees a row with a time and no way in, and `T-089` gives one no Open control
at all. There is no `app/Integrations/Teams`, no `teams` block in
`config/services.php`, nothing tagged in
`app/Providers/IntegrationServiceProvider.php:24-40`.

Teams is the one provider in `D-016` where **no per-Peer grant exists at any
tier**: personal Microsoft accounts have no online-meeting API
([create onlineMeeting](https://learn.microsoft.com/en-us/graph/api/application-post-onlinemeetings?view=graph-rest-1.0),
personal account "Not supported"), and the work-account webinar path needs
admin-consented app-only scopes, returns `204` with no registration id, and
cannot say that one registration covers later sessions
([post registrations](https://learn.microsoft.com/en-us/graph/api/virtualeventwebinar-post-registrations?view=graph-rest-1.0)).
So `D-016`'s other half applies: **the Series is the container**, and Qori shows
one stored link only to Peers with access.

Afterwards the creator pastes the join link of a recurring meeting they made in
Teams, once per Series. Qori validates it, stores it as that Series'
`series_containers` row, shows the chosen tier's limits and what Qori
recommends for it beside the field, and hands the link to every Peer with
access through `T-089`'s Open route. Nothing is connected, no Microsoft API is
called, and a Peer needs no Microsoft account.

## Decisions taken to make this specifiable

**Teams is in the beta release, and a tier is explained rather than refused.**
`D-018` (17 September 2026) puts every provider the `storage` stream orders
into beta, Teams among them, and settles how a tier is offered: Qori takes
whatever kind of Teams account the creator brings, states that tier's limits on
screen before they save, and says what it recommends beside them. Teams free's
60 minutes and 100 people, the lobby wait and the Teams app a phone needs are
therefore copy the creator reads and weighs, not rules the code applies —
nothing here counts a minute, caps a Peer or declines a tier, because the
meeting is on the creator's own account and the platform they bring is theirs.
What binds Qori rather than the creator is untouched by that record and stays
open below.

**No OAuth, no connection and no Microsoft API call anywhere in this task.** The
review's line is "do not make Peer Microsoft sign-in or creator OAuth a
prerequisite for a pasted-link feature unless a demonstrated requirement needs
it", and the research shows none: the only Graph capability that would help —
setting the lobby through `lobbyBypassSettings` — needs
`OnlineMeetings.ReadWrite`, which Microsoft's default policy keeps out of user
consent ([permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference)).
`ConnectionProvider::Teams` therefore stays not `connectable()` and Teams grows
no Integrations section — which answers `T-044`'s open question about whether
Teams is exempt from its connection guard: it is, and a Teams Episode is never
refused for a missing connection.

**The container is one recurring meeting's join link, on `T-091`'s
`series_containers`.** `provider` is `ConnectionProvider::Teams`, `url` is the
link exactly as pasted, `external_id` is the meeting id parsed out of it — or
`link:<32 hex>` when the shape is one the parser does not know — and
`settings['tier']` is the kind of account the creator said it is on. `T-091`'s
unique `(group_id, provider, external_id)` gives the dedicated-container rule
for free inside a Group: one meeting cannot serve two of that Group's Series,
and the form says everyone with access can open that meeting whether or not a
session is listed as an Episode.

**A grant row per Access, `granted` at once, with no vendor call — and what
`granted` means here is said on screen rather than implied.** `TeamsMeetings`
implements `GrantsPeerAccess` (`T-091`) and its `grant()` returns
`GrantResult::granted($container->external_id, $container->url)` without
touching Microsoft, so Open and revoke stay uniform. The row is not a fiction:
it records which link this Peer was given and when, and `revoke()` is
what stops Qori showing it. It is the one place where `granted` does not mean a
vendor confirmed anything — whether a Peer gets into the session is decided by
the creator's lobby and meeting policy, which no Microsoft API will tell Qori,
so the lobby is copy read _before_ the session rather than a grant state.
`T-090` refuses the same no-op for Vimeo and YouTube; the difference is that
this task has a container row to point at and a link to hand out per Peer.

**`awaiting_identity` and `awaiting_acceptance` never arise, `pending` almost
never does, and no call can time out.** There is no Peer Microsoft account to
confirm — `T-092`'s `IdentityProvider::forConnection()` answers null for
`ConnectionProvider::Teams` — and nothing at the vendor to accept. Every method
still takes the caller's timeout — `VendorAccessService::REQUEST_TIMEOUT_SECONDS`,
inside the request where every grant is now made (`D-040`) — and ignores it,
because it answers from the container row: `T-091`'s `ERROR_TIMEOUT` is
unreachable here, and `pending` survives only as its catch-all
(`ERROR_UNEXPECTED`). `needs_creator`
has one cause: a stored link that no longer parses, the state after the
allow-list is tightened. So a Peer sees the join control, or, while their row
is not `granted`, the join control disabled with
`shared.vendor_notice.open_disabled` and `T-091`'s notice at `#access`
(`D-020`): on `needs_creator` it says the creator has been told and asks
nothing of the Peer; on the catch-all `pending` the next press of Open re-runs
`grant()` from the container row with no request to Microsoft, which is the
only thing that retries a Peer's row now that the sweep and the Peer's Check
again are gone (`D-040`, 20 September 2026). `T-089`'s Open sends a page
rendered earlier, or a saved link, back to that notice with
`shared.vendor_notice.redirected`. Those sentences are `T-091`'s, in
`lang/en/shared.php`, and this task adds none.

**A `granted` row is re-read rather than trusted.** Open passes `T-091`'s
`verifyGranted: true`, and a `granted` row whose `checked_at` is older than
`RECHECK_MINUTES` is re-read the next time that Peer presses Open rather than
by a sweep (`D-040`); both land in `checkGrant()`, which re-reads the
container's stored link. A link the creator replaced or broke is
therefore caught the next time any Peer opens the Episode, rather than the next
time somebody complains — current access, not only first access.

**The lobby is said in advance and never presented as done.** Anonymous
participants wait in the lobby unless "Who can bypass the lobby" is Everyone,
and even then until a verified participant starts the meeting, because
"Anonymous users and dial-in callers can start a meeting" is off by default; the
org-wide anonymous setting is being replaced by a per-organiser policy, and
policy changes take up to 24 hours
([anonymous users](https://learn.microsoft.com/en-us/microsoftteams/anonymous-users-in-meetings),
[who can bypass the lobby](https://learn.microsoft.com/en-us/microsoftteams/who-can-bypass-meeting-lobby),
[meeting settings reference](https://learn.microsoft.com/en-ie/MicrosoftTeams/settings-policies-reference)).
The creator's instructions are explicit on the form, and the Peer's page says
they may wait — holding the URL alone does not get anybody in.

**The tier lives on the container, not on a connection.** `D-016`'s dropdown
hangs off connecting an account and there is none here, so the form asks which
kind of Teams account hosts the meeting and stores it in
`series_containers.settings['tier']`. `ProviderTier` (`T-044`'s enum) gains
`teams_free`, `teams_personal` and `teams_work`; each renders its own limitation
bullets with every number interpolated from `config('qori.connections.teams')`,
and one line saying what Qori recommends for that tier. All three save the same
way: the dropdown records which account the meeting is on, and no branch of it
refuses anything. The copy sits under `connections.providers.teams.*` in
`T-044`'s shape — `tiers.<tier>.label`, `help` and `recommended`, and
`limits.common.*` and `limits.<tier>.*` — although no Integrations section
renders it, so the essential split below reads Teams' lines exactly as it reads
every connected provider's.

**The form is laid out as a connection section is: the recommendation, at most
three essential lines, then one disclosure holding the rest, all above Save**
(`D-021` rule 4). `ProviderSections::ESSENTIAL` gains a `teams` entry (Code),
and `TeamsMeetingController::show()` splits each tier's lines by it into
`essential` and `more` through `T-044`'s public
`ProviderSections::limitsFor()`, with `T-044`'s `essentialLabel` and each
tier's `moreLabel`. The
essential lines are what a Peer needs (Chrome or Edge on a computer, or the
Teams app on a phone), what ends or blocks a session on that tier (Teams free's
time limit; a work admin turning off joining without an account) and the
one-meeting-per-Series rule; the forwarded link and recordings go in `more`.
The two meeting instructions — use a meeting nothing else needs, and set the
lobby to let everyone in — are not tier limitations but steps on the meeting
itself, so they sit beside the join-link field, where the meeting is chosen
(`connections.meeting.teams.shares_everything` and `.lobby`), always open, as
`T-100`'s picker carries `connections.meeting.shares_everything`.

**Each live Episode may carry its own link, and the Series' link is the
default.** That one join link serves every occurrence of a recurring meeting is
stated only in a community answer
([Q&A 2280509](https://learn.microsoft.com/en-us/answers/questions/2280509/get-specific-instance-of-a-recurring-onlinemeeting)),
with no primary source found, so the per-Episode field survives — validated the
same way, optional, empty meaning "the Series' meeting". If the walk shows one
link does cover every occurrence, the field stays for the creator who runs each
session as its own meeting; if it does not, only the copy changes.

**A changed link replaces the container, through `T-091`'s `attach()`, and it
is the only reconciliation trigger Teams has.** The old `series_containers` row
is deleted, its grants become revokable, every active Access gets a pending row
on the new container, and each Peer is granted on it the next time they press
Open — nothing is granted ahead of use (`D-040`). The other two triggers
never fire for this provider: there is no identity for a Peer to confirm or
change, and no connection to reconnect, so `T-091`'s `reconnected()` has nothing
of Teams' to pick up. Revoking a Teams grant is a row write with no vendor
call, and the creator is told plainly that the old link keeps working for
anybody who kept it — `D-016` accepts forwarded links and this task does not
pretend otherwise.

**A new link shows what it changes before it is saved** (`D-021` rule 3). When
the Series already has a Teams container, `TeamsMeetingController::show()`
passes `T-157`'s `containerImpact` (`VendorAccessService::impactOf()`, local
reads only) and `TeamsMeeting.vue` opens `T-157`'s `ContainerChangeDialog`
before `store` is posted — both went to that task with the creator's surfaces
on 20 September 2026. The shared meeting sentences are `T-100`'s, and are
written for a meeting Qori registers people on: they say Qori checks each
session against the new meeting and some may need setting again, and nothing in
them says the old link keeps working. Neither is true of a pasted link — Qori
tells Microsoft nothing — so `show()` builds the entry in `T-091`'s
`ContainerChangeImpact` shape from `T-100`'s meeting `replace.title` and
`replace.confirm` and `T-157`'s `series.container_change.keep`, with
`connections.meeting.teams.replace_impact` as its `peers` sentence — how many
Peers with access see the new link, that nothing
changes in Teams, and that the old link still works for anyone who kept it —
and `episodes` null, which the dialog does not render. It lists no Episodes as
needing attention, because a live Episode with no link of its own follows the
Series' meeting and one with its own link is untouched. Nothing is written until the creator
confirms; a Series with no Teams container posts straight away.

**The grant never stands between money and access.** `TeamsMeetings` makes no
request and `T-091`'s ensure step catches everything, so nothing here can
refuse, delay or undo an Access; if the grant row cannot be written, the Access
still stands and the Peer's next press of Open writes it (`D-040`), which is
what keeps `T-102`'s replay honest.

**No new service.** `VendorAccessService::attach()` is the only write, so
`TeamsMeetingController` takes it by constructor. `LiveSessionService` is
`T-100`'s, for Zoom's listing, occurrence matching and repair — Teams has none
of those, and depending on it would put a paste form behind a Marketplace review.

**Recordings are out.** A Teams recording lands in the organiser's OneDrive,
people outside the organisation cannot open it, and it is deleted after 120 days
by default
([recording storage change](https://learn.microsoft.com/en-us/microsoftteams/tmr-meeting-recording-change),
[expiration policy](https://learn.microsoft.com/en-us/microsoftteams/manage-teams-recording-expiration-policy)).
Sharing one means moving it into the Series' OneDrive folder, which is `T-098`'s
container and its re-share. The limitation copy says so rather than leaving the
creator to find out.

**No paid Series on Teams until the terms are read and `T-102` and `T-103` have
landed.** Microsoft's API terms forbid reselling or sublicensing access to a
Microsoft Offering
([terms of use](https://learn.microsoft.com/en-us/legal/microsoft-apis/terms-of-use)),
though this task calls no API and may not be bound by them; what may bind is
Teams free's own terms, which the blueprint records as forbidding one-sided
communications with no clause captured. `D-018`'s "explained, never refused"
does not reach either one: a clause binding Qori is not the creator's to accept
on Qori's behalf, and a limitation is only stated on screen once somebody has
read it, so neither becomes a line in the Copy table by guesswork. Both are open
below, and a free Series runs on any tier meanwhile.

## Preconditions

`T-091` done, so `series_containers`, `vendor_grants` with its `join_url`
column, `GrantsPeerAccess`, the ensure step and
`VendorAccessService::attach()` exist; it depends on `T-044`, `T-089` and the
Google spike `T-093`, so `ProviderTier`, `lang/en/connections.php` and
`shared.episodes.open` come with it. `T-157` done, for
`VendorAccessService::impactOf()`, the `containerImpact` prop and
`ContainerChangeDialog.vue`. `T-100` done, for
`ContainerChangeImpact::kind()`'s `meeting` arm and the two
`series.container_change.meeting.replace.*` lines this task reads. `depends:`
names those three and the board derives the rest.

**Data this task verifies against:** a clean database, plus a Group with a
chosen timezone — `EpisodeService::add()` calls `guardLiveSessionTime()`
(`app/Services/EpisodeService.php:46`, `:76-91`), which refuses a live Episode
when the Group chose none, as `tests/Feature/Series/LiveSessionTest.php:47`
sets up.

**Equipment:** a Microsoft Teams (free) account to schedule a recurring meeting
and, where one can be borrowed, a Microsoft 365 work tenant; a clean browser
with no Microsoft account signed in; a phone, to see the Teams app requirement;
and a second person or profile to be admitted from the lobby.

**Spike:** none owed, and none exists — the stream's four spikes (`T-093`,
`T-095`, `T-097`, `T-099`) are for providers with an API. **This task parses no
vendor payload and claims no response shape, because it makes no request.** The
only vendor data it touches is the join URL, and the host and path forms below
are provisional: no page in the research names them. The walk in Acceptance
settles them and commits the redacted links it saw as
`tests/Fixtures/teams/join_links.json` — the fixture this task owes and the
parser's tests read.

## Scope

**In:**

- The Series' Teams meeting: a paste form, validation, the tier with its
  recommendation, essential lines and a disclosure holding the rest (the
  `teams` entry in `ProviderSections::ESSENTIAL`, `D-021`), `T-157`'s
  `ContainerChangeDialog` before a link is replaced, and
  `VendorAccessService::attach()` writing the container.
- `TeamsMeetings` implementing `GrantsPeerAccess` with no vendor call, tagged
  `grant-providers`.
- The optional per-Episode link, validated the same way.
- The Peer's Series page and Open for a live Teams Episode, with the lobby and
  browser lines said before the session.

**Out:**

- Any Microsoft OAuth, Graph call, webinar, registration or lobby write; any
  Peer Microsoft sign-in (`T-092` excludes Teams).
- Recordings, which need `T-098`'s OneDrive container.
- The Peer notice's sentences (`T-091`); `ContainerChangeDialog` itself and
  `VendorAccessService::impactOf()` behind it (`T-157`);
  `ContainerChangeImpact::kind()`'s `meeting` arm and the two
  `series.container_change.meeting.replace.*` lines this task reads (`T-100`);
  the before-buying list (`T-092`), for which this task writes no
  Teams line (see below).
- Clearing a Series' meeting: `T-091` has `attach()` and no `detach()`, so a
  meeting is replaced, never removed (see below).
- Calendar invites, reminders and session mail (`delivery`).
- Zoom (`T-100`), and any change to `MediaLink`, the Qori-hosted tickets,
  Dropbox or Vimeo.
- Reading the meeting's own settings to check the lobby: no API for it on a
  personal account, an admin needed on a work one.

## Files

| Path                                                                                       | Change | Notes                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `app/Integrations/Teams/TeamsMeetings.php`                                                 | new    | `GrantsPeerAccess`; the one integration with no HTTP client at all                                                                                                             |
| `app/Integrations/Teams/TeamsMeetingLink.php`                                              | new    | `parse()`, the meeting id and the host; a class that knows a vendor's link shapes is that vendor's code, so it is not in `app/Data` (`D-022`, `CLAUDE.md`)                     |
| `app/Enums/ProviderTier.php`                                                               | edit   | Three Teams cases; `T-044` creates the enum, so it is not in the repo today                                                                                                    |
| `app/Support/ProviderSections.php`                                                         | edit   | The `teams` entry in `ESSENTIAL`; `T-044` creates the class, not in the repo today                                                                                             |
| `app/Integrations/Contracts/GrantsPeerAccess.php` `app/Services/VendorAccessService.php`   | edit   | `?Connection` for a provider that is not `connectable()` — `T-091`'s files, see below                                                                                          |
| `app/Http/Controllers/Share/TeamsMeetingController.php`                                    | new    | `show()`, with the essential split and `containerImpact`, and `store()`                                                                                                        |
| `app/Http/Requests/Share/StoreTeamsMeetingRequest.php`                                     | new    | Link and tier; Form Requests only                                                                                                                                              |
| `app/Http/Requests/Share/StoreEpisodeRequest.php`                                          | edit   | The Teams arm of `content()` and its link rule (`:184-196`)                                                                                                                    |
| `app/Http/Controllers/Share/SeriesController.php`                                          | edit   | The `meeting` prop on the Series page (`:154-177`)                                                                                                                             |
| `app/Http/Controllers/Shared/SharedController.php`                                         | edit   | `T-089`'s `opensAs()`: `tab` for a live Teams Episode that has a link (`:207-214`)                                                                                             |
| `app/Providers/IntegrationServiceProvider.php`                                             | edit   | `TeamsMeetings` in the `grant-providers` tag (`:35-39`)                                                                                                                        |
| `routes/share/series.php`                                                                  | edit   | The two routes below                                                                                                                                                           |
| `resources/js/pages/share/series/TeamsMeeting.vue`                                         | new    | The paste form and its two meeting steps; the tier, its recommendation, essential lines and `T-044`'s `collapsible` holding the rest; `ContainerChangeDialog` before a replace |
| `resources/js/pages/share/series/Show.vue`                                                 | edit   | A link to that page; the Teams arm of `referenceLabel` and its placeholder (`:236-262`)                                                                                        |
| `resources/js/pages/shared/Show.vue`                                                       | edit   | The Open anchor and the lobby lines for a live Episode (`:199`, `:206-210`)                                                                                                    |
| `lang/en/connections.php` `lang/en/series.php` `lang/en/accesses.php` `lang/en/errors.php` | edit   | Copy below; `connections.php` is `T-044`'s file                                                                                                                                |
| `config/qori.php`                                                                          | edit   | `connections.teams`: the hosts and every number the copy interpolates                                                                                                          |
| `database/factories/SeriesContainerFactory.php`                                            | edit   | A `teams()` state; `T-091` creates the factory                                                                                                                                 |
| `tests/Feature/Storage/TeamsMeetingTest.php` `tests/Feature/Storage/TeamsGrantTest.php`    | new    | 11 and 7 cases                                                                                                                                                                 |
| `tests/Feature/Storage/TeamsLiveEpisodeTest.php`                                           | new    | 10 cases                                                                                                                                                                       |
| `tests/Unit/Integrations/Teams/TeamsMeetingLinkTest.php`                                   | new    | 5 cases; it mirrors the class into the vendor's folder, so `tests/Unit/Integrations/` is new                                                                                   |
| `tests/Feature/Storage/OpenEpisodeTest.php` `tests/Feature/Series/EpisodeRoutesTest.php`   | edit   | See Tests; `OpenEpisodeTest.php` came with `T-089`, which is `done`                                                                                                            |
| `docs/flows/vendor-access.md`                                                              | edit   | `T-091` creates it; this adds the Teams chain, which calls no vendor                                                                                                           |
| `docs/flows/series.md` `docs/flows/storage.md`                                             | edit   | The live chain (`series.md:125-129`); the providers paragraph (`storage.md:98-104`)                                                                                            |
| `docs/tinker/teams.md`                                                                     | new    | The recipe: paste a link, grant a Peer, open it, replace the link                                                                                                              |
| `docs/tinker/README.md`                                                                    | edit   | One index row for that recipe                                                                                                                                                  |

## Database

**None.** The link is `series_containers.url`, the meeting id its `external_id`,
the tier its `settings` jsonb, and the Peer's row is `vendor_grants` with
`vendor_ref` holding the meeting id and `join_url` the link — all `T-091`'s
columns, `join_url` among them: `string(2048)`, nullable, default null, declared
once in `T-091`'s create migration
`2026_09_20_000100_create_series_containers_and_vendor_grants.php` and nowhere
else (20 September 2026). Neither this task nor `T-100` alters it, because a
column three tasks each half-declare is a column that disappears the moment the
first of them is edited. A per-session link is `episodes.content`, already
jsonb with an `'array'` cast
(`database/migrations/2026_09_08_000000_create_qori_schema.php:113`,
`app/Models/Episode.php:70`); the session's time is `episodes.starts_at`, which
`T-029` fills.

## Code

```php
namespace App\Integrations\Teams;

/**
 * A Teams join link the creator pasted, and what Qori can read out of it.
 *
 * Teams' hosts and path shapes are Teams' business, so the parser lives in the
 * vendor's folder rather than app/Data (D-022). The host and path forms are
 * provisional: no Microsoft page in the research names them, and
 * tests/Fixtures/teams/join_links.json settles them. Nothing here is a vendor
 * payload — Qori never calls Microsoft for a Teams Episode.
 */
class TeamsMeetingLink
{
    public function __construct(
        public string $url,
        /** Parsed from the link, or 'link:'.<32 hex chars> when its shape is unknown. */
        public string $meetingId,
        public string $host,
    ) {}

    /** Null when the URL is malformed or its host is not in config('qori.connections.teams.link_hosts'). */
    public static function parse(string $url): ?self;
}
```

```php
namespace App\Integrations\Teams;

/**
 * Teams has no per-person grant at any tier (D-016), so the Series is the
 * container: Qori shows one stored join link to Peers with access. The only
 * GrantsPeerAccess implementation that makes no request — every method answers
 * from the container row, and $connection is always null because
 * ConnectionProvider::Teams is not connectable() (T-044).
 */
class TeamsMeetings implements GrantsPeerAccess
{
    public const ERROR_LINK_UNUSABLE = 'teams_link_unusable';

    public function provider(): ConnectionProvider;   // ConnectionProvider::Teams

    /** $externalId is the parsed meeting id; exists is TeamsMeetingLink::parse($url) !== null. */
    public function checkContainer(?Connection $connection, string $externalId, int $timeoutSeconds): ContainerCheck;

    /** granted($container->external_id, $container->url), or needsCreator(ERROR_LINK_UNUSABLE) when the stored url no longer parses. */
    public function grant(?Connection $connection, SeriesContainer $container, ?VendorIdentity $identity, string $email, int $timeoutSeconds): GrantResult;

    /** The same answer as grant(), so T-091's re-check costs nothing. */
    public function checkGrant(?Connection $connection, VendorGrant $grant, int $timeoutSeconds): GrantResult;

    /** RevokeResult::revoked() always: Qori stops showing the link and Microsoft is told nothing. */
    public function revoke(?Connection $connection, VendorGrant $grant, int $timeoutSeconds): RevokeResult;

    /** The Episode's own content['join_url'] when it has one, else the grant's join_url. No accountHint. */
    public function openLink(?Connection $connection, Episode $episode, ?VendorGrant $grant, int $timeoutSeconds): VendorLink;

    /** An Episode link that still parses, or no link of its own; never a vendor read. */
    public function checkItem(?Connection $connection, Episode $episode, int $timeoutSeconds): ItemCheck;
}
```

| What happened                          | `GrantResult`                       | `last_error_code`     |
| -------------------------------------- | ----------------------------------- | --------------------- |
| The container's url parses             | `granted(meeting id, url)`          | cleared               |
| The container's url no longer parses   | `needsCreator(ERROR_LINK_UNUSABLE)` | `teams_link_unusable` |
| Anything thrown inside the ensure step | `T-091`'s `pending()` catch-all     | `unexpected`          |

`awaiting_identity` and `awaiting_acceptance` are unreachable here, and no
timeout is, because no call is made.

```php
namespace App\Http\Controllers\Share;

class TeamsMeetingController extends Controller
{
    use ResolvesShareSeries;

    public function __construct(private VendorAccessService $vendorAccess) {}

    /**
     * The form: the current link and tier; the two meeting steps; the tiers, each with its label, help,
     * recommended, essential, more and moreLabel, split by T-044's ProviderSections::limitsFor(ConnectionProvider::Teams,
     * $tier, …), which reads ESSENTIAL['teams'] (at most MAX_ESSENTIAL, the rest in key order), with T-044's essentialLabel;
     * and containerImpact from $this->vendorAccess->impactOf() (T-157's) when the Series has an Active Teams container,
     * built in T-091's ContainerChangeImpact shape — kind meeting and the replace.title and replace.confirm lines are
     * T-100's — with connections.meeting.teams.replace_impact as copy.replace.peers and episodes null (D-021).
     */
    public function show(string $group, string $series, Terminology $terminology): Response;

    /**
     * attach() with ConnectionProvider::Teams, the parsed meeting id, the url and ['tier' => …];
     * replaces the Series' existing Teams container, so every Peer is regranted on the new link.
     */
    public function store(string $group, string $seriesId, StoreTeamsMeetingRequest $request): RedirectResponse;
}

// App\Http\Requests\Share\StoreTeamsMeetingRequest
// rules(): 'join_url' => ['required', 'string', 'max:2048'], 'tier' => ['required', Rule::enum(ProviderTier::class)]
// withValidator(): TeamsMeetingLink::parse() must answer, else errors.meeting.not_a_teams_link on
//                  join_url; the tier's provider() must be ConnectionProvider::Teams.
public function link(): ?TeamsMeetingLink;

// App\Http\Requests\Share\StoreEpisodeRequest — the Teams arm of content() (:190-195) keeps
// ['join_url' => …, 'starts_at' => …] and gains one rule: a Teams live Episode's reference, when
// not blank, must parse. Blank means the Series' meeting. The Zoom arm is T-100's to change.

// App\Http\Controllers\Shared\SharedController — T-089's opensAs() (:207-214): a live Episode
// answers 'tab' when its Series has a Teams container or the Episode carries its own link, and
// null otherwise, which is what it answers today.
```

```php
// config/qori.php — connections.teams; every number the copy interpolates lives here
'teams' => [
    // Provisional: confirmed from the links the walk records, not from any Microsoft page.
    'link_hosts' => ['teams.microsoft.com', 'teams.live.com'],
    'link_paths' => ['/l/meetup-join/', '/meet/'],
    'free' => ['minutes' => 60, 'people' => 100],
    'personal' => ['hours' => 30, 'people' => 300],
    'work' => ['hours' => 30, 'people' => 300, 'enterprise_people' => 1000],
    'recording_days' => 120,
],
```

```php
// app/Support/ProviderSections.php — T-044's ESSENTIAL; this entry is this task's (D-021 rule 4), read by
// TeamsMeetingController::show() because Teams has no Integrations section. Keys are relative to
// connections.providers.teams.limits., in order: what a Peer needs, what ends or blocks a session on that tier,
// the one-meeting rule. link_travels and recordings are in `more`.
'teams' => [
    'teams_free' => ['common.browser', 'teams_free.time_limit', 'common.one_meeting'],
    'teams_personal' => ['common.browser', 'common.one_meeting'],
    'teams_work' => ['common.browser', 'teams_work.admin', 'common.one_meeting'],
],
```

Teams free's 60 minutes and 100 people are confirmed
([create a meeting in Teams free](https://support.microsoft.com/en-us/teams/free/meetings/create-a-meeting-in-microsoft-teams-free));
Microsoft 365 Personal and Family give 30-hour meetings and 300 people
([subscriptions for Teams free](https://support.microsoft.com/en-us/office/learn-more-about-subscriptions-for-microsoft-teams-free-1061bbd0-6d97-46a6-8ca0-21059be3eee3));
work plans give 300 interactive attendees on Business and 1,000 on Enterprise
([feature comparison](https://learn.microsoft.com/en-us/microsoftteams/meetings-events-feature-comparison)).

## Copy

| Key                                                            | File                      | English                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| -------------------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `connections.providers.teams.name`                             | `lang/en/connections.php` | Microsoft Teams                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `connections.providers.teams.description`                      | `lang/en/connections.php` | Run live sessions in a Teams meeting you already have. There is no account to connect: paste the meeting's join link and Qori shows it to people with access.                                                                                                                                                                                                                                                                                             |
| `connections.providers.teams.tiers.teams_free.label`           | `lang/en/connections.php` | Microsoft Teams (free)                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `connections.providers.teams.tiers.teams_free.help`            | `lang/en/connections.php` | A personal Microsoft account with no Microsoft 365 subscription.                                                                                                                                                                                                                                                                                                                                                                                          |
| `connections.providers.teams.tiers.teams_free.recommended`     | `lang/en/connections.php` | Best for short sessions. Plan each one to end inside :minutes minutes and this :series to stay under :people people. Teams ends the session, not Qori.                                                                                                                                                                                                                                                                                                    |
| `connections.providers.teams.limits.teams_free.time_limit`     | `lang/en/connections.php` | Teams ends each session after :minutes minutes, and a session holds up to :people people.                                                                                                                                                                                                                                                                                                                                                                 |
| `connections.providers.teams.tiers.teams_personal.label`       | `lang/en/connections.php` | Microsoft 365 Personal or Family                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `connections.providers.teams.tiers.teams_personal.help`        | `lang/en/connections.php` | Sessions run up to :hours hours and hold up to :people people.                                                                                                                                                                                                                                                                                                                                                                                            |
| `connections.providers.teams.tiers.teams_personal.recommended` | `lang/en/connections.php` | Recommended where sessions run long or this :series fills up: :hours hours and :people people cover both.                                                                                                                                                                                                                                                                                                                                                 |
| `connections.providers.teams.tiers.teams_work.label`           | `lang/en/connections.php` | A work or school Microsoft 365 account                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `connections.providers.teams.tiers.teams_work.help`            | `lang/en/connections.php` | Sessions run up to :hours hours and hold up to :people people on business plans, :enterprise_people on enterprise plans.                                                                                                                                                                                                                                                                                                                                  |
| `connections.providers.teams.tiers.teams_work.recommended`     | `lang/en/connections.php` | Ask your admin to allow joining without an account before you invite anyone, and allow a day for that change.                                                                                                                                                                                                                                                                                                                                             |
| `connections.providers.teams.limits.teams_work.admin`          | `lang/en/connections.php` | Your admin can turn off joining without an account. A change can take a day to take effect.                                                                                                                                                                                                                                                                                                                                                               |
| `connections.providers.teams.limits.common.browser`            | `lang/en/connections.php` | People without a Microsoft account join from Chrome or Edge on a computer, and need the Microsoft Teams app on a phone.                                                                                                                                                                                                                                                                                                                                   |
| `connections.providers.teams.limits.common.one_meeting`        | `lang/en/connections.php` | Use one recurring meeting for this :series and hold every session in it. A different meeting means a new link for everyone.                                                                                                                                                                                                                                                                                                                               |
| `connections.providers.teams.limits.common.link_travels`       | `lang/en/connections.php` | Anyone the link reaches can try to join, and taking someone's access away does not change the link.                                                                                                                                                                                                                                                                                                                                                       |
| `connections.providers.teams.limits.common.recordings`         | `lang/en/connections.php` | Teams saves recordings in your OneDrive, where people outside your organisation cannot open them, and deletes them after :days days unless you change that.                                                                                                                                                                                                                                                                                               |
| `connections.meeting.teams.title`                              | `lang/en/connections.php` | The Teams meeting this :series runs on                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `connections.meeting.teams.intro`                              | `lang/en/connections.php` | Schedule one recurring meeting in Teams, then paste its join link here. Qori shows it to everyone with access, and to nobody else.                                                                                                                                                                                                                                                                                                                        |
| `connections.meeting.teams.label`                              | `lang/en/connections.php` | Join link                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `connections.meeting.teams.help`                               | `lang/en/connections.php` | In Teams, open the meeting and copy its join link, or copy "Join the meeting now" out of the invitation.                                                                                                                                                                                                                                                                                                                                                  |
| `connections.meeting.teams.shares_everything`                  | `lang/en/connections.php` | Everyone with access to this :series can open that meeting, whether or not the session is listed here. Use a meeting nothing else needs.                                                                                                                                                                                                                                                                                                                  |
| `connections.meeting.teams.lobby`                              | `lang/en/connections.php` | In the meeting options, set who can bypass the lobby to everyone. People joining without a Microsoft account still wait until you start the session.                                                                                                                                                                                                                                                                                                      |
| `connections.meeting.teams.tier`                               | `lang/en/connections.php` | Which kind of Teams account is this meeting on?                                                                                                                                                                                                                                                                                                                                                                                                           |
| `connections.meeting.teams.saved`                              | `lang/en/connections.php` | This :series runs on that meeting now, and everyone with access can open it.                                                                                                                                                                                                                                                                                                                                                                              |
| `connections.meeting.teams.replaced`                           | `lang/en/connections.php` | Everyone with access sees the new link now. The old one still works for anyone who kept it.                                                                                                                                                                                                                                                                                                                                                               |
| `connections.meeting.teams.replace_impact`                     | `lang/en/connections.php` | `{0} Nobody has access yet, so nobody sees a new link. Nothing changes in Teams, so the old link still works for anyone who kept it.\|{1} One :peer with access will see the new link instead of this one. Nothing changes in Teams, so the old link still works for anyone who kept it.\|[2,*] :count :peer_plural with access will see the new link instead of this one. Nothing changes in Teams, so the old link still works for anyone who kept it.` |
| `connections.grants.reasons.teams_link_unusable`               | `lang/en/connections.php` | the join link saved for that :series is not one Qori can read any more; paste it again                                                                                                                                                                                                                                                                                                                                                                    |
| `series.meeting.teams.set_up`                                  | `lang/en/series.php`      | Set the Teams meeting for this :series                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `series.meeting.teams.none`                                    | `lang/en/series.php`      | No Teams meeting yet, so nobody with access can join a session.                                                                                                                                                                                                                                                                                                                                                                                           |
| `accesses.live.teams_lobby`                                    | `lang/en/accesses.php`    | You may wait in the lobby until :creator starts the session and lets you in.                                                                                                                                                                                                                                                                                                                                                                              |
| `accesses.live.teams_no_account`                               | `lang/en/accesses.php`    | You do not need a Microsoft account. Join from Chrome or Edge on a computer, or install the Microsoft Teams app on a phone.                                                                                                                                                                                                                                                                                                                               |
| `accesses.live.no_link_yet`                                    | `lang/en/accesses.php`    | :creator has not added the link for this session yet.                                                                                                                                                                                                                                                                                                                                                                                                     |
| `errors.meeting.not_a_teams_link.message`                      | `lang/en/errors.php`      | That is not a Teams join link.                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `errors.meeting.not_a_teams_link.resolution`                   | `lang/en/errors.php`      | In Teams, open the meeting and copy its join link. It starts with teams.microsoft.com or teams.live.com.                                                                                                                                                                                                                                                                                                                                                  |

`accesses.live.join` ("Join the session") is `T-100`'s key for the same control;
whichever task lands first writes it and the second reuses it. `:creator` is the
Group's name, as `T-091` uses it. Every number is interpolated from
`config('qori.connections.teams')`, never written into a sentence. Vendor names
appear here under `D-016`'s stated exception for provider-choice and
Peer-prerequisite copy. The Episode form's label for the optional per-session
link is `referenceLabel` in `resources/js/pages/share/series/Show.vue:236-243`
— existing inline English under §13's unwired i18n, whose Teams arm this task
rewords rather than adding a sentence to a page that cannot read lang yet.

Each tier's `recommended` line is the second half of `D-018`: the `help` and
`limits` lines say what a tier cannot do, the `recommended` line says what Qori
advises doing about it, and both are on screen before the creator saves. Neither
is enforced anywhere — no tier is refused and no number is checked in code, so
the creator weighs them against this Series and chooses. A terms line for Teams
free is deliberately **not** in this table: no clause has been read, and a
restriction nobody has read is not one Qori states; see below.

The tier and limitation keys follow `T-044`'s shape under
`connections.providers.teams.*`; which limitation lines sit above the
disclosure is `ProviderSections::ESSENTIAL` (Code), not a flag in this table,
and the disclosure's label is `T-044`'s. Teams free's time limit is a
`limits.teams_free.*` line rather than its `help`, so that it can be essential,
and the admin line is `limits.teams_work.*` because only that tier has an
admin. `connections.meeting.teams.shares_everything` and `.lobby` are the two
steps on the meeting itself and sit beside the join-link field, always open.
`connections.meeting.teams.replace_impact` stands in for
`series.container_change.meeting.replace.peers`, which `T-100` declares, inside
`T-157`'s `ContainerChangeDialog`, with no Episodes sentence beside it; it goes
through `Terminology::choice()` with the number of active Accesses as `:count`,
as the `series.container_change.*` lines it sits beside do. The two shared
lines this task does read — `series.container_change.meeting.replace.title` and
`.confirm` — are `T-100`'s and appear in no row above, which is what
`depends: T-100` buys. The Peer notice's sentences are `T-091`'s
`shared.vendor_notice.*` (`D-020`), and no `accesses.vendor.teams.before_buying.*`
line is written here (see below).

## Routes

| Verb | Path                                        | Name                               | Action                         |
| ---- | ------------------------------------------- | ---------------------------------- | ------------------------------ |
| GET  | `g/{group}/series/{series}/meeting/teams`   | `share.series.meeting.teams.show`  | `TeamsMeetingController@show`  |
| POST | `g/{group}/series/{seriesId}/meeting/teams` | `share.series.meeting.teams.store` | `TeamsMeetingController@store` |

A slug on the page load and an id on the write (§21.3,
`routes/share/series.php:17-19`), both inside the `g/{group}` `share.` group.
The Peer needs no new route — Open is `T-089`'s `shared.episodes.open`. `T-100`
adds `share.series.meeting.*` for Zoom's picker under the same prefix; the two
sit side by side and no row collides.

## Tests

`Http::preventStrayRequests()` in `setUp()` of every file here, which is the
assertion that matters most: this provider must never reach the network.

**New: `tests/Feature/Storage/TeamsMeetingTest.php` — 11 cases**

1. `test_a_pasted_join_link_becomes_the_series_container` — provider `teams`,
   `url` stored as pasted, `external_id` the parsed id.
2. `test_a_link_whose_shape_it_cannot_read_is_stored_under_a_hash`
3. `test_a_link_that_is_not_a_teams_join_link_is_refused` — no container written.
4. `test_a_meeting_another_series_holds_is_refused` — `T-091`'s
   `errors.container.in_use`.
5. `test_the_tier_the_creator_chose_is_stored_on_the_container`
6. `test_pasting_a_new_link_replaces_the_container_and_regrants_every_peer`
7. `test_another_groups_series_cannot_be_given_a_meeting` — 404.
8. `test_the_series_page_links_to_the_meeting_page_and_names_the_tiers_limits`
9. `test_every_tier_saves_and_shows_its_limits_and_what_qori_recommends` — the
   free tier is stored like the other two and nothing refuses it; each tier's
   `help`, `recommended` and every `limits` line reach the page, between
   `essential` and `more` (`D-018`).
10. `test_each_tier_puts_its_essential_lines_above_the_disclosure` — `teams_free`'s
    `essential` is `browser`, `time_limit`, `one_meeting` in that order,
    `teams_work`'s has `admin` where free has `time_limit`, `more` holds
    `link_travels` and `recordings`, and `shares_everything` and `lobby` are
    beside the field for every tier (`D-021`).
11. `test_the_meeting_page_carries_what_replacing_the_link_changes` — a Series
    with a Teams container and two active Accesses: `containerImpact` has
    `kind` `meeting`, the arm `T-100` declares, `peers` 2,
    `copy.replace.peers` the `[2,*]` branch of
    `connections.meeting.teams.replace_impact` with `:count` filled, and
    `copy.replace.episodes` null; a Series with no container gets none; no
    container is written by `show()` (`D-021`).

**New: `tests/Feature/Storage/TeamsGrantTest.php` — 7 cases**

12. `test_a_new_access_is_granted_on_the_meeting_with_no_request_to_microsoft`
13. `test_the_grant_stores_the_meeting_id_and_the_join_link`
14. `test_a_repeat_ensure_changes_nothing`
15. `test_a_recheck_of_a_granted_row_keeps_it_granted`
16. `test_a_stored_link_that_no_longer_parses_needs_the_creator`
17. `test_revoking_an_access_marks_the_grant_revoked`
18. `test_a_series_with_no_meeting_creates_no_grant_row`

**New: `tests/Feature/Storage/TeamsLiveEpisodeTest.php` — 10 cases**

19. `test_a_live_teams_episode_opens_at_the_series_meeting_link` — 302 from
    `shared.episodes.open`.
20. `test_an_episode_with_its_own_link_opens_at_that_link`
21. `test_an_episode_link_that_is_not_a_teams_link_is_refused`
22. `test_a_peer_without_access_cannot_open_the_meeting` — 403.
23. `test_a_live_episode_with_no_meeting_shows_no_open_control` — `opens` null,
    `accesses.live.no_link_yet` on the row.
24. `test_the_peer_is_told_about_the_lobby_and_that_no_account_is_needed`
25. `test_the_session_time_is_still_read_in_the_groups_zone` — `T-029`.
26. `test_opening_records_the_episode_as_opened` — through `T-089`'s gate.
27. `test_open_on_a_teams_grant_that_needs_the_creator_returns_to_the_series_notice`
    — a stored link that no longer parses: `shared.episodes.open` redirects to
    `shared.show` at `#access` with `shared.vendor_notice.redirected`; the notice
    is `shared.vendor_notice.reasons.needs_creator`, which asks nothing of the
    Peer, and the live Episode's Join control is disabled (`D-020`).
28. `test_open_on_a_pending_teams_row_grants_it_without_calling_microsoft` — a
    row left `pending` by the catch-all: the Peer presses Open,
    `shared.episodes.open` turns the row `granted` from the container row and
    sends them to the meeting, and no request leaves the test. Rewritten on
    20 September 2026 and keeping its number: it asserted the Peer's Check
    again and `shared.access.check`, deleted with `shared.vendor_notice.opened`
    when `D-040` made pressing Open the only thing that grants a row. The
    behaviour it guards — a catch-all `pending` row becoming `granted` from the
    container row, with nothing asked of Microsoft — is unchanged.

**New: `tests/Unit/Integrations/Teams/TeamsMeetingLinkTest.php` — 5 cases**

Extends `Tests\TestCase`, not the bare PHPUnit one: `parse()` reads `config()`.
It mirrors the class, which is `App\Integrations\Teams\TeamsMeetingLink`
(`D-022`), so `tests/Unit/Integrations/` is new; `tests/Feature/Integrations/`
already holds `Google` and `Stripe`, so the shape is the codebase's. Cases 29
to 32 read `tests/Fixtures/teams/join_links.json`, which the walk commits;
until it exists they cannot be written honestly.

29. `test_it_reads_the_meeting_id_from_a_meetup_join_link`
30. `test_it_reads_the_meeting_code_from_a_teams_live_link`
31. `test_it_hashes_a_link_whose_id_it_cannot_read`
32. `test_it_refuses_a_link_on_another_host`
33. `test_it_refuses_something_that_is_not_a_url`

Total new: 33.

**Changed:**

- `tests/Feature/Storage/OpenEpisodeTest.php` — `T-089`'s case 8,
  `test_a_live_episode_cannot_be_opened`, becomes
  `test_a_live_episode_with_no_meeting_cannot_be_opened`: a Teams Episode whose
  Series has a meeting redirects now.
- `tests/Feature/Series/EpisodeRoutesTest.php` — the comment at `:131` saying a
  live Episode's join link "comes from Zoom or Teams" is reworded to say Teams'
  link is pasted per Series.

## Acceptance

- [ ] A creator pastes the join link of one recurring Teams meeting for a
      Series, chooses the kind of account it is on, and sees that tier's limits,
      what Qori recommends for it and the lobby instruction on the same page
      before saving
- [ ] Every tier saves, the free one included: no tier is refused and no session
      length or head count is checked in code (`D-018`)
- [ ] The form shows the chosen tier's recommendation and at most
      `MAX_ESSENTIAL` essential lines above Save, with the rest in one closed
      disclosure beside them, and the two meeting steps — a meeting nothing
      else needs, the lobby set to everyone — always open beside the link field
- [ ] Pasting a new link for a Series that has one shows how many Peers will
      see it and that the old link still works for anyone who kept it, before
      anything is saved
- [ ] A Peer whose row is not `granted` sees the Join control disabled and the
      Series page's notice saying who resolves it, and Open on a stale page
      lands them there rather than on a dead page
- [ ] Anything that is not a Teams join link is refused with a sentence naming
      what to paste, and a meeting another Series holds is refused
- [ ] Every Peer with access sees the link on the Series page and opens the
      session through `T-089`'s route in a new tab; a Peer without access does
      not, and no request is made to Microsoft on any of these paths
- [ ] Walked once with a Teams account (Equipment): an external participant
      joins from a clean browser, a signed-out participant joins from Chrome or
      Edge, lobby admission is observed and described, and the creator changes
      the meeting link and every Peer sees the new one
- [ ] That same walk records whether one link serves every occurrence of the
      recurring meeting, including one added afterwards, commits the redacted
      links it saw as `tests/Fixtures/teams/join_links.json`, and is written up
      with its date in `walkthroughs.md`
- [ ] A live Episode with no meeting shows no Open control and says so, rather
      than a control that does nothing
- [ ] `docs/flows/vendor-access.md`, `series.md`, `storage.md` and the tinker
      recipe describe what was built
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Whether Teams enters before beta at all: the open decision in `decisions.md`
  ("which integrations enter before beta", 16 September 2026) leaves Zoom and
  Teams after beta unless a representative creator runs live sessions, and
  `PLAN.md`'s settled list still defers "broad Zoom/Teams work" — the owner's.
  Written so it can wait: nothing before it depends on it.~~ **Answered
  17 September 2026 (`D-018`):** Teams is in the beta release, with every other
  provider the `storage` stream orders. `PLAN.md`'s rule 5 and its Zoom/Teams
  line are the owner's to edit and both now disagree with that record; nothing
  in this task waits on either.
- The join-link allow-list — hosts `teams.microsoft.com` and `teams.live.com`,
  paths `/l/meetup-join/` and `/meet/` — is provisional and comes from no
  Microsoft page in the research; the walk pastes real links from each tier and
  records their shapes — anyone's, then the parser follows.
- Whether one join link serves every occurrence of a recurring meeting, later
  occurrences included. Only a community answer says so; if it does not hold,
  the per-Episode link becomes required and the copy says a link per session —
  the walk's.
- Whether Teams free's terms forbid one-sided communications, and what that
  means for a Series of lectures. The blueprint records the restriction with no
  clause and no URL, so finding the clause is the first step — Microsoft's
  Services Agreement is where the personal-account restrictions sit, unconfirmed
  for this one. `D-018` does not answer it and does not license guessing at it:
  a limitation is stated on screen because somebody read it, so no
  `connections.providers.teams.limits.teams_free.terms` line is written until
  the clause is in hand.
  Reading it is anyone's; what it means for a Series of lectures is the owner's.
  It holds no tier back meanwhile — Teams free is offered with the limits above.
- Whether a paid Series may run on Teams at all, given Microsoft's API terms
  against reselling access to a Microsoft Offering — which this task arguably
  never touches, since it calls no API — and, either way, `T-102` and `T-103`
  land first — the owner's. This is the one limit here that is **not** the
  creator's to accept: it binds Qori, so `D-018` leaves it open (as it does
  `T-090`'s two clauses) rather than making it copy on the form.
- Whether `T-091` widens `GrantsPeerAccess` and its ensure step to
  `?Connection` for providers that are not `connectable()`, or Teams gets past
  the connection guard another way. Its current spec makes a missing connection
  `needs_creator` before any provider is asked, which would stall every Teams
  grant — anyone's, with `T-091`, and it is a change to that task's Code
  section rather than something this connector may work around.
- Whether a creator can clear a Series' meeting rather than only replace it:
  `T-091` has `attach()` and no `detach()`, so a Series that stops running live
  sessions keeps a container granting a link nobody lists. `T-094`'s draft now
  adds `VendorAccessService::detach()` and `share.series.container.destroy` for
  a Drive folder; whether Teams uses them, behind a remove wording in
  `ContainerChangeDialog`, is the same question — anyone's, with `T-094` and
  `T-157`. The four `series.container_change.meeting.remove.*` lines are not
  written anywhere meanwhile; see the amendment below.
- Where a Teams `needs_creator` row reaches the creator. `T-157` shows those
  rows, and Try again now, in the provider's section of the Integrations page,
  and Teams has none, so `connections.grants.reasons.teams_link_unusable` has
  nowhere to appear today. The Teams meeting page is the likely place, and
  pasting the link again is the fix, so Try again now may not be needed here —
  anyone's, with `T-157`.
- ~~Whether `ContainerChangeDialog` takes a provider's own sentence, as this
  draft passes `connections.meeting.teams.replace_impact`, or `T-091` writes a
  Teams variant of its meeting wording. Its meeting wording describes people
  taken off the old meeting in the creator's account, which never happens for
  Teams, and it lists Episodes that need attention, which Teams has none of —
  anyone's, with `T-091`.~~ **Settled 17 September 2026 (`D-021`):** a page
  other than the Series page builds `T-091`'s entry itself and may leave a
  sentence null; this task passes `replace_impact` as the Peers sentence and no
  Episodes sentence.
- Whether a Teams Series writes `accesses.vendor.teams.before_buying.common.*`
  (`D-021` rule 1). A Peer needs Chrome or Edge on a computer, or the Teams app
  on a phone (`limits.common.browser`), which a buyer on a phone would want to
  know before paying; `D-021` names Google Drive's, Dropbox's, OneDrive's and
  Zoom's lines and not Teams', and a paid Series waits on the terms question
  above anyway. If yes, the line is `common.browser`'s Peer-facing form and
  `T-092` renders it with nothing more — the stream owner's.
- `T-044`'s `ProviderSections::ESSENTIAL`, `MAX_ESSENTIAL`, `essentialLabel`,
  `moreLabel`, its `collapsible` component and its key shape are taken from its
  draft, and this task's Teams copy moved into that shape. `T-044` exposes the
  split as `ProviderSections::limitsFor()`, which `TeamsMeetingController::show()`
  calls, because `ProviderSections::props()` only covers `connectable()`
  providers; re-check the signature when `T-044` is `ready` — anyone's.
- The borrowed names used here are taken from `D-020`, `D-021` and the drafts
  they sit in, and are to be re-checked when those tasks are `ready` — anyone's.
  `shared.vendor_notice.*` is `T-091`'s; `containerImpact`,
  `VendorAccessService::impactOf()` and `ContainerChangeDialog` are `T-157`'s
  since 20 September 2026; `ContainerChangeImpact::kind()`'s `meeting` arm and
  the `series.container_change.meeting.replace.*` lines are `T-100`'s.
  `shared.access.check` was in this list until 20 September 2026 and is gone
  with `D-040`, which is what case 28 above records.
- Whether the tier belongs on the container, as specified, or Teams gets an
  Integrations section with a tier and no connection behind it — the owner's,
  with `T-044`.
- ~~Which file the Peer surface's copy lives in: `T-089` keeps
  `lang/en/accesses.php` and adds no `shared.php`, while `T-091`'s Copy table
  writes its grant-state sentences to `lang/en/shared.php`. This task's Peer
  lines follow `accesses.php`, as `T-100`'s do — anyone's.~~ **Answered
  17 September 2026 (`D-020`):** the grant-state sentences are `T-091`'s
  `shared.vendor_notice.*`, in `lang/en/shared.php`, which `T-089` creates, and a
  Peer who cannot join is sent to them on the Series page. This task's own Peer
  lines stay `accesses.live.*` in `accesses.php`, as `T-100`'s do.
- Whether the lobby line sits on every live Episode row or once above the list,
  and whether it names the creator — the owner's, with `design`.
- `T-089`'s `opensAs()` answering `tab` for a live Teams Episode (Files row and
  Code above) disagrees with `T-125`, the classroom Join task, which keeps it
  null for a live Episode and gives the Peer a Join button instead
  (`D-024`, `D-026`). Settle which one the Series page reads before this is
  `ready` — anyone's, with `T-125`.
- `F10` in the storage review of 20 September 2026
  (`docs/planning/reviews/storage-2026-09-20-findings-codex.md`) reads the
  arrangement above as a contradiction rather than an open question: Teams
  deliberately has no Connection, yet `TeamsMeetings` implements
  `GrantsPeerAccess`, whose connection argument is non-null, and `T-091`'s
  service stops before it calls any provider when no live connection exists, so
  a Teams grant reaches `needs_creator` instead of the immediate `granted` this
  task promises. The review's recommendation is to move the stored-link delivery
  onto the existing access-gated link path rather than add a nullable-connection
  exception to the permission machinery for a link that never calls a vendor.
  Recorded here, not resolved: it is the same ground as the `?Connection` bullet
  above and the two are settled together — the owner's, with `T-091`.
  **That file no longer exists and cannot be recovered**, so these bullets are
  the review itself, to be read as the primary source and not as a summary of
  something a reader can go and check; `docs/planning/reviews/README.md` has the
  whole of it.
- The same review owes Teams no API fixture, because this design calls no
  Microsoft endpoint, and still holds that documentation alone does not prove
  the Peer journey: its evidence table asks for browser evidence on each tier
  this task offers — `teams_free`, `teams_personal` and `teams_work` — walked
  with an attendee outside the creator's organisation, and for the pasted-link
  shapes each tier actually produces (20 September 2026). That is more than the
  allow-list bullet above asks for, which only pastes links from each tier, and
  it is the outside attendee who tests the lobby and meeting-policy claims in
  Decisions — anyone's.
- **A Teams container with no connection is settled here now, not by `T-091`.**
  The decision below sends the meeting half to the tasks that use it and sends
  this question with it, so the two bullets above — the `?Connection` widening
  and `F10` — stop being questions this draft files against `T-091` and become
  questions this draft answers. `TeamsMeetings` takes `?Connection` because
  Teams connects nothing, while `T-091`'s ensure step reads a missing
  connection as `needs_creator` before any provider is asked, so on today's two
  specs every Teams grant stalls in a state the creator has no way to clear —
  there is no Teams section on the Integrations page to clear it from. Either
  the widening is written here as a stated edit of `T-091`'s
  `GrantsPeerAccess` and `VendorAccessService`, the two rows this task's Files
  table already claims, or the review's alternative is taken and the stored
  link is delivered on the existing access-gated link path with no grant row at
  all. Those are two different products rather than two wordings, so it is a
  decision and not a departure — the stream owner's.
- A creator can change a live Episode's `join_url` **in place**, keeping the
  Episode id. `EpisodeService::update()` reads a `join_url` attribute and
  merges it into `content` (`app/Services/EpisodeService.php:219-227`), written
  through `LiveSessionService::withLockedContent()`
  (`app/Services/LiveSessionService.php:30-42`), gated on `isLive()` alone
  (`:191`) and never on the provider, and nothing records or acts on the URL
  that was there before. It is the one true in-place vendor repoint in the
  codebase — every other replacement in Qori is a delete and a create with a
  new ULID — and the per-Episode link this task validates goes in through that
  same attribute. Two things follow that this draft does not say. `openLink()`
  prefers the Episode's own `content['join_url']` over the grant's, so after
  such an edit the link a Peer is shown is one no `vendor_grants` row records,
  and Decisions' claim that the row "records which link this Peer was given and
  when" stops holding. And a Peer who kept the old link keeps it, which this
  task says plainly of a replaced container and nowhere of a replaced Episode
  link. What happens to a grant made against the link the Episode used to carry
  — rewritten, revoked and re-granted, or left alone because Microsoft was
  never told anything either way — has to be stated — anyone's, with `T-091`.

## Amended 20 September 2026 — the meeting half moves here from T-091

**The stream owner answered `T-091`'s open question on 20 September 2026: the
meeting half of the container-change dialog leaves that task for `T-100` and
`T-101`, "the only tasks that would use it".** `T-091` wrote the half and then
asked whether it should stay there, waiting behind `D-024`, or move to the two
tasks that read it. It moves. Nothing is deleted from `T-091`, which stays the
record of where the half was written and why. What arrives here is less than
what arrives at `T-100`, because this task reads two of the lines and writes its
own for everything else. A second ruling of the same day settled where each
piece is _declared_: **`T-100` declares the meeting half and this task cites
it**, which is what `depends: T-091, T-100, T-157` records.

**What arrives, and who declares it.** The four things `T-091` names, in this
task's reading, with that ruling applied to each:

- **`ContainerChangeImpact::kind()` answering `meeting`, declared by `T-100`.**
  `T-091` specified it as `meeting` for Zoom and Teams, so a Teams container
  needs the arm as much as a Zoom one: without it the dialog reads
  `series.container_change.folder.*` at a Series whose container is a link. Two
  tasks cannot declare one arm, so `T-100` writes it and this task reads it.
  The class itself stays `T-091`'s `app/Data/ContainerChangeImpact.php`, and
  this task's Files table claims neither the class nor the arm.
- **Two of the eight `series.container_change.meeting.*` lines, `T-100`'s to
  declare as well.** `TeamsMeetingController::show()` builds the entry itself
  (`D-021`, settled 17 September 2026) from the meeting `replace.title` and
  `replace.confirm`, with `connections.meeting.teams.replace_impact` as its own
  `peers` sentence and `episodes` null. `series.container_change.keep` is not
  one of the eight and is **`T-157`'s**, which declares it in its own Copy
  table: it is the dialog's Keep button, it belongs to neither kind, and
  `T-091` writes no `series.*` line at all once its creator copy moved. This
  task declares no shared meeting line, and the four `remove.*` lines are
  written nowhere at all; see the last section.
- **No test case.** `T-091`'s case 60 is a Zoom container and goes to `T-100`
  with the Zoom half of `T-091`'s case 28. Case 11 here,
  `test_the_meeting_page_carries_what_replacing_the_link_changes`, is already
  the Teams equivalent and gains one assertion, that a Teams container's `kind`
  is `meeting`.
- **`vendor_grants.join_url`, which stays `T-091`'s to declare** —
  `string(2048)`, nullable, default null, in its create migration
  `2026_09_20_000100_create_series_containers_and_vendor_grants.php`. This task
  reads it twice: `grant()` answers
  `granted($container->external_id, $container->url)`, and `openLink()` falls
  back to the stored link when the Episode carries none of its own. Reading a
  column is not declaring it, so Database stays "**None**".

**Why the copy is split the way it is, and why that is the reason it moved.**
Zoom cancels the old registrants; Teams tells Microsoft nothing. The shared
meeting lines — `T-091`'s until this ruling, `T-100`'s now — are written to say
only what **Qori** stops doing and nothing about the creator's vendor account,
and a fact true of one vendor alone rides in that provider's
`series.container.<provider>.change.replace` note —
`T-100` has one, saying the registrations on the old meeting are cancelled, and
this task has none, because nothing of Teams' changes at all. It is also why
this task substitutes its own Peers sentence instead of reusing
`series.container_change.meeting.replace.peers`: the shared line says Qori stops
giving Peers the old meeting, and the honest sentence here has to add that the
old link keeps working for anybody who kept it. Wording answerable to two vendor
behaviours cannot sit in a draft that can see neither.

**It arrives held.** `D-024` holds `T-091`'s live-session containers until they
fit a per-Episode join link (`D-026`), and names this task's own once-per-Series
Teams link in the same sentence. Moving the words did not lift the hold; it put
them beside the Teams behaviour that decides them.

**What it means for this task's sections**, worked through on the consolidation
pass of 20 September 2026 rather than left named for the next reader:

- **Database** stays "**None**" and now says where `join_url` is declared:
  once, in `T-091`'s create migration
  `2026_09_20_000100_create_series_containers_and_vendor_grants.php`. The
  `ALTER` on `vendor_grants` this section proposed earlier that day is dropped,
  and the conditional around it with it — neither this task nor `T-100`
  declares the column, because a column three tasks half-declare is one that
  disappears the moment `T-091` is edited to match them.
- **Files** claims no row for `app/Data/ContainerChangeImpact.php`: `T-100`
  declares the arm and this task reads it. `lang/en/series.php` stays an `edit`
  row for this task's own `series.meeting.teams.*` lines, and `depends: T-100`
  is what keeps the two tasks from being `doing` in it at once.
- **Copy** already carries `connections.meeting.teams.replace_impact`, and the
  note under that table now cites `T-100` for the
  `series.container_change.meeting.replace.peers` it stands in for and for the
  `replace.title` and `replace.confirm` this task reads, and `T-157` for the
  `ContainerChangeDialog` all three appear in.
- **Code** and **Tests** take case 11's assertion that a Teams container's
  `kind` is `meeting`, and `show()`'s docblock now says which of the three
  tasks owns each borrowed name. No stated total moves: recounted from the
  numbered cases, 11 + 7 + 10 + 5 = 33.
- **Scope**'s "Out" bullet sends `ContainerChangeDialog` and
  `VendorAccessService::impactOf()` to `T-157`, the `meeting` arm and the two
  lines to `T-100`, and the Peer notice's sentences to `T-091`.
- **Decisions** and **Preconditions** lost the scheduled sweep,
  `qori:access:reconcile`, `SWEEP_TIMEOUT_SECONDS` and `RECHECK_HOURS`, all
  deleted from `T-091` by `D-040`: a grant is made when a Peer presses Open,
  for the one item they are opening, so Open is both what re-reads a stale
  `granted` row and what retries a catch-all `pending` one.

**Both of the things this amendment could not place are placed**, by the stream
owner on 20 September 2026.

- **Neither task depended on the other, and now this one does.** `depends:` was
  `T-091` alone while this task read two lines and an enum arm `T-100`
  declares, and three surfaces `T-157` owns; it reads `T-091, T-100, T-157`.
  That settles the file clash `PROCESS.md` has the stream owner arbitrate: the
  Files row for `app/Data/ContainerChangeImpact.php` is `T-100`'s alone, the
  `join_url` column is `T-091`'s alone, and `lang/en/series.php`, which both
  tasks genuinely write to, is behind the dependency.
- **The four `series.container_change.meeting.remove.*` lines are not written,
  here or anywhere.** No task in the plan builds a meeting remove: this one
  replaces a link and has no remove, `T-100` replaces a meeting from the picker
  and never removes one, and the only draft building a remove is `T-094`, for a
  Drive folder. Four lines describing an action nothing offers are not written
  against the chance that something offers it later; if the `detach()` question
  above is answered yes for Teams, the task that builds the remove writes them
  then. Closed rather than passed on.

## Read-through, 20 September 2026

A three-lens read of `T-091` before it was to be frozen found the cut of that
day was not clean, and some of what it found is this task's. The list is in
`T-091` under "Read-through, 20 September 2026 — what the cut left behind".
The items naming this task were worked through on the consolidation pass of
20 September 2026, against the stream owner's ruling of the same day; each is
struck below with what it became.

- ~~It depends on `T-157` and on `T-100` in substance and says neither in
  `depends:`.~~ **Answered 20 September 2026:** `depends: T-091, T-100, T-157`,
  and the body agrees — `VendorAccessService::impactOf()`, the
  `containerImpact` prop and `ContainerChangeDialog` are cited to `T-157`
  throughout, and `ContainerChangeImpact::kind()`'s `meeting` arm and the two
  `series.container_change.meeting.replace.*` lines to `T-100`, which declares
  them.
- ~~Case 28 asserts `shared.access.check` and `shared.vendor_notice.opened`,
  both deleted.~~ **Answered 20 September 2026:** case 28 keeps its number and
  now presses Open, which is what grants a row under `D-040`. The behaviour it
  guarded — a row left `pending` by the catch-all becoming `granted` from the
  container row with nothing asked of Microsoft — is what it still guards.
- ~~Its header summary stops at 18 September.~~ **Answered 20 September 2026:**
  the blockquote carries the cut of `T-091` in three, where the meeting half
  went, and `D-040`.
- ~~Its Database still says "None" while attributing `join_url` to `T-091` and
  proposing an `ALTER` — if `T-091` is edited to match, the column disappears
  from every task.~~ **Answered 20 September 2026:** the column is declared
  once, in `T-091`'s create migration, and named there in this task's Database
  section; the `ALTER` and the conditional around it are gone from the
  amendment above.
- ~~Unrelated to the cut: the header moves the parser to
  `app/Integrations/Teams/TeamsMeetingLink` per `D-022` while the Files table
  still lists `app/Data/TeamsMeetingLink.php`.~~ **Answered 20 September
  2026:** the Files table, the Code sketch's namespace and the parser's unit
  test all sit under `app/Integrations/Teams` now, and `CLAUDE.md` is
  unambiguous that a class knowing a vendor's link shapes is that vendor's
  code.

Five more stale citations the same pass fixed, none of them on that list.
Decisions and Preconditions still ran grants off a scheduled sweep, naming
`qori:access:reconcile`, `SWEEP_TIMEOUT_SECONDS` and `RECHECK_HOURS`, all
deleted from `T-091` by `D-040`; the Integrations page that a `needs_creator`
row reaches the creator on is `T-157`'s, not `T-091`'s;
`SharedController::opensAs()` had moved to `:207-214`; Notes listed an
`app/Integrations` that no longer exists (`Concerns` and `Qori` are gone,
`CloudflareR2` and `Google` are there) and said `CLAUDE.md` still asks for
`name()`, which it has not for some time; and `OpenEpisodeTest.php` and
`tests/Unit/Data/` are in the repo now that `T-089` is `done`. Every stated
test total was recounted from the numbered cases and all four were right:
11 + 7 + 10 + 5 = 33.

Two things the same pass found and did not settle, both already bullets under
"Before this can be ready": whether `GrantsPeerAccess` and the ensure step widen
to `?Connection` or the stored link is delivered on the access-gated link path
instead (`F10`, the stream owner's), and what happens to a grant made against a
per-Episode `join_url` a creator then edits in place. The first decides whether
this task's Files table keeps its two `T-091` rows at all.

## Re-scope log

None.

## Notes

**`app/Integrations/Teams` does not exist, and neither does anything else
Teams-shaped.** `app/Integrations` holds `CloudflareR2`, `Contracts`,
`Dropbox`, `Google`, `Stripe` and `Vimeo` (checked 20 September 2026);
`config/services.php` has one vendor block, for Stripe (`:25`). This task
creates the folder, with both of its `new` rows — `TeamsMeetings` and
`TeamsMeetingLink` — and nothing above should be read as though either the
folder or the parser is there today. What this task supersedes is small: the
pasted `join_url` in `StoreEpisodeRequest::content()` (`:190-195`) with its
"Join link (optional for now)" label and `https://zoom.us/j/...` placeholder
(`resources/js/pages/share/series/Show.vue:236-243`, `:257-262`), and the two
"not built yet" paragraphs saying the Zoom/Teams OAuth would populate a live
Episode's content (`docs/flows/series.md:125-129`,
`docs/flows/storage.md:98-104`) — there is no OAuth here to build.
`EpisodeProvider::Teams`, `ConnectionProvider::Teams` and
`EpisodeType::allowedProviders()` are kept exactly as they are, and
`database/seeders/DesignReviewSeeder.php:356` seeds a Zoom live Episode, not a
Teams one, so nothing there changes.

~~`CLAUDE.md` still says integrations expose `name()` and are bound in
`AppServiceProvider`; the code says `provider()`
(`app/Integrations/Contracts/ResolvesMedia.php:29`) and
`app/Providers/IntegrationServiceProvider.php`. This draft follows the code, as
`T-044`, `T-089`, `T-091` and `T-100` do.~~ **Answered 20 September 2026:**
`CLAUDE.md` says `provider()` and names
`app/Providers/IntegrationServiceProvider.php` as where contracts are bound and
tagged, so the conventions and the code agree and this draft follows both.

This task answers `T-044`'s open question "whether Teams stays exempt from the
connection guard" — it does — and its `depends:` names `T-091` for the grant
core, `T-100` for the meeting half it reads and `T-157` for the creator's
surfaces it renders.

Every `path:line` above was opened and checked on 17 September 2026, and the
ones this consolidation pass touched again on 20 September 2026:
`SharedController::opensAs()` had moved to `:207-214`,
`tests/Feature/Storage/OpenEpisodeTest.php` and `tests/Unit/Data/` exist now
that `T-089` is `done`, and `lang/en/shared.php` is in the repo. Line numbers
move with the files; treat a mismatch as a stale citation to fix, not as a
re-scope.
