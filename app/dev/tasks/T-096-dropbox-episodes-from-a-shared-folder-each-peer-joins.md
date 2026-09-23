---
id: T-096
title: Dropbox Episodes from a shared folder each Peer joins
stream: storage
status: draft
owner: unassigned
estimate: L
depends: T-044, T-091, T-092, T-094, T-095
blocks: none
---

# T-096 — Dropbox Episodes from a shared folder each Peer joins

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016`, the owner's BYO blueprint and the developer review of the same day;
> `D-018` folded in on 17 September 2026, and `D-020` and `D-021` the same day.
> Amended on 19 September 2026 from that day's cross-draft decisions: `grant()`
> takes `T-091`'s `App\Data\GrantIdentity`, a member Dropbox no longer lists is
> `GrantResult::ERROR_PERMISSION_GONE`, `ItemCheck`'s `name`, `mimeType` and
> `url` are `T-091`'s, `DropboxStorage` keeps its own timeout and every
> `$timeoutSeconds` is a budget that may only shorten it (`D-034`), the
> Dropbox tests sit under `tests/Feature/Integrations/Dropbox/`,
> `DropboxAccounts` and `DropboxSignIn` read their landings in Dropbox's words
> and answer `T-044`'s `ConnectionLanding` and `T-092`'s `IdentityLanding`,
> and the before-buying allowance is `:basic_storage_gb`, the config key
> `BuyerRequirements` now passes it under.

## Why

Dropbox is the only bring-your-own provider the code has, and it works the way
`D-016` superseded. `DropboxStorage::linkFor()` calls
`files/get_temporary_link` per play with the creator's token
(`app/Integrations/Dropbox/DropboxStorage.php:49-70`), and its docblock
(`:17-19`) gives that expiring link as the reason Dropbox is the BYO provider
and Google Drive is not; `docs/flows/storage.md:56` and
`docs/project-plan.md:221` say the same. Nothing connects a Dropbox account —
`T-044` ships Google first — nothing shares a folder, and no Peer is ever
named to Dropbox, so the creator's material reaches a Peer only as a link Qori
mints on their behalf. `ConnectionProvider::Dropbox`
(`app/Enums/ConnectionProvider.php:14`) and `EpisodeProvider::Dropbox`
(`app/Enums/EpisodeProvider.php:19`) exist, and `EpisodeType::allowedProviders()`
already offers Dropbox for file, video and audio
(`app/Enums/EpisodeType.php:29-37`), so the enums are the one part that does
not move.

Afterwards a creator connects Dropbox from the Integrations page, says which
kind of account it is, and reads what that tier cannot do and what Qori
recommends for it before connecting.
They pick one folder for a Series; Qori shares it and stores the
`shared_folder_id`. Every Peer with access and a confirmed Dropbox account is
added to that folder as a viewer with the notification off, and the grant sits
in `awaiting_acceptance` — the Peer's own step — until the member list shows
them joined, at the next re-check or at once when they press Check again
(`D-021`). A buyer reads before paying that the Series needs a Dropbox account,
one Join and room in their own Dropbox. Open is a redirect to the file on
dropbox.com. Anything the
creator later adds, replaces or moves into the folder reaches every member
with no new call, which is priority 2. A successful invitation is never shown
as finished access.

## Decisions taken to make this specifiable

**The picker is Qori's own folder list from `files/list_folder`, not the
Dropbox Chooser.** The Chooser runs in the browser, and its documentation says
neither which Dropbox account it reads when the browser is signed in to
another one, nor whether its default `preview` link type creates a shared link
beside the member grant (https://www.dropbox.com/developers/chooser). Either
answer would reach Qori unchecked: an id the connected token cannot read, or a
link nobody asked for. `T-095` observes `files/list_folder` and never calls the
Chooser, so the Chooser has no fixture and could not be specified from an
observed response anyway. The brief for this draft named the Chooser in folder mode;
this is the one place the draft departs from it, and the bullet below lets the
owner put it back.

**Dropbox joins `T-044`'s tier dropdown with three tiers**, `dropbox_basic`,
`dropbox_paid` and `dropbox_team`, from the blueprint's summary table. Every
line that is not tier-specific sits under `limits.common.*` — the invitation
cap, the storage cost and the 2027 terms bind Peers on every plan, which the
blueprint's first copy put under Basic alone. **All three tiers ship, whatever
`T-095` finds** (`D-018`, 17 September 2026): if Dropbox will not let a Basic
creator add a member at all, that is a vendor capability rather than a Qori
policy, so the tier stays in the dropdown and its entry says Dropbox needs a
paid plan to share a folder this way — the creator upgrades with Dropbox or
picks another provider. The spike's answer changes how plainly the tier says
it in advance and nothing in the Code: a refusal at grant time is
`needs_creator` with `connections.grants.reasons.insufficient_plan` either
way.

**Each tier entry says what Qori recommends as well as what the tier cannot
do** (`D-018`, 17 September 2026). A limitation with no advice beside it is
the hand-off the owner ruled out, so every tier carries a `recommended` line
in the Copy table beside its `label` and `help`, written in words a creator
can act on — upgrade, pick a different folder, ask an admin — and the
`limits.*` lines stay as the plain statement of what the tier will not do.

**Three lines per tier are essential and the rest sit in `T-044`'s
disclosure** (`D-021`, 17 September 2026). The `dropbox` entry in
`ProviderSections::ESSENTIAL` (under Code) puts `common.accounts` first on every
tier, because every Peer needs it; then what stops sharing outright on that
tier — `dropbox_basic.plan` and `dropbox_basic.video` on Basic,
`dropbox_team.outside` on Team, and on Paid, where nothing does,
`common.storage`, the cost a Peer is most often caught by; then
`common.folder` on Paid and Team, which on Basic gives way to its fourth
candidate because the picker repeats the folder rule in full
(`series.container.dropbox.explain`) and nothing else repeats the playback
limit before connecting. Every other line, the team-folder rule included (the
picker refuses a team folder and Team's `recommended` sentence names it), sits
under `more`, above Connect all the same.

**Dropbox video and audio are offered on every tier, with that tier's
streaming ceiling stated before the creator connects** (`D-018`,
17 September 2026). `EpisodeType::allowedProviders()` already offers Dropbox
for file, video and audio (`app/Enums/EpisodeType.php:29-37`) and nothing here
narrows it by tier: playback on a Basic account stops after the first
`:minutes` minutes for everyone but the creator, the tier's own line says so,
and its `recommended` line names a paid Dropbox plan for anything longer.
Refusing the Episode type would be Qori deciding what a creator may keep in
their own Dropbox, which `D-004` declined and `D-018` settles.

**The connector asks for four scopes and not `files.content.read`.**
`account_info.read`, `files.metadata.read`, `sharing.read`, `sharing.write` —
the routes below and nothing more; `files.content.read` exists only for
`get_temporary_link`, which this task deletes. The app is a scoped app with
**Full Dropbox** access, because an app-folder app cannot call a sharing route
and an app folder cannot be shared (`SharePathError` in
[sharing_folders.stone](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/sharing_folders.stone);
https://developers.dropbox.com/oauth-guide). `token_access_type=offline`
returns a refresh token that does not expire, so
`ConnectsAccounts::refreshesOnSchedule()` is false, as `T-044` assumes.

**One dedicated folder per Series, and the picker says what sharing it
shares.** `T-091`'s unique `(group_id, provider, external_id)` enforces it.
Dropbox adds its own rule: a folder cannot be shared if it sits inside a
shared folder or contains one (`inside_shared_folder`,
`contains_shared_folder`), and a team folder itself cannot take outside
members (`team_folder`) — so the picker refuses those three before `attach()`
reaches the constraint.

**`series_containers.external_id` is the `shared_folder_id`, and sharing can
be asynchronous, so the container has a preparing state.**
`sharing/share_folder` answers `.tag` `complete` with a `SharedFolderMetadata`
or `.tag` `async_job_id`
([sharing_folders.stone](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/sharing_folders.stone);
https://developers.dropbox.com/dbx-sharing-guide). This task adds
`SeriesContainerStatus::Sharing` to `T-091`'s enum: while it is set,
`external_id` holds `job:<async_job_id>`, no Peer is granted, every grant row
stays `pending` with `ERROR_CONTAINER_PREPARING`, and
`VendorAccessService::prepareContainers()` calls `checkContainer()` again —
from the sweep and from the creator's Series page — until
`check_share_job_status` answers `complete` and the real id replaces the job
id. One enum case and one method, not a second grant model; it is a change to
`T-091`'s Database section and carries a bullet for its owner.

**`ContainerCheck` gains `externalId` and `preparing`.** Dropbox is the first
provider whose picked reference (a folder path) is not the id Qori stores, and
the first whose container is not usable the moment it is checked. `T-091`'s
`ItemCheck` already carries nullable `name`, `mimeType` and `url`, which
`T-094`'s `describeItem()` reads (19 September 2026); this adds `externalId`
there too, for the re-resolve below.

**Every Dropbox call made in a web request carries `T-091`'s
`VendorAccessService::REQUEST_TIMEOUT_SECONDS` as its budget, and the sweep
carries `SWEEP_TIMEOUT_SECONDS`** (`D-034`). `DropboxStorage` keeps a timeout
of its own, `TIMEOUT_SECONDS`, the 15 seconds it sets today
(`app/Integrations/Dropbox/DropboxStorage.php:51`), and no retry;
`$timeoutSeconds`, the last argument of every method, is a budget that may
only shorten it, so each call waits whichever of the two is shorter. A timeout
answers `GrantResult::pending(GrantResult::ERROR_TIMEOUT)` rather than
throwing, so the Peer reads `T-091`'s `pending` sentence and nobody is asked
to act. `T-095` row 20 times every call against both figures.
`share_folder`'s asynchronous form is the case no timeout can wait out, which
is why the container has a preparing state rather than a longer one.
**No Dropbox outcome throws at all** — every one of them is a typed result
written on the grant row — so a fulfilment that has already written the
Access is never undone by a vendor failure and stays replayable. That is
`T-091`'s rule, and why `T-102` and `T-103` come before a paid Series uses
Dropbox.

**The Peer is named by `dropbox_id`, never by email.** An address that is not
the account's main email becomes a pending invitee rather than a member
([sharing_files.stone](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/sharing_files.stone);
https://help.dropbox.com/share/cant-access-shared), and `T-092` already stores
the `account_id` as the identity's `subject` from Dropbox's OpenID sign-in
(https://developers.dropbox.com/oidc-guide). `vendor_ref` is that same
`account_id`: Dropbox returns no permission id for a folder member, so the
row's key into the member list is the Peer's own account.

**A grant becomes `granted` only when `sharing/list_folder_members` shows the
Peer under `users`** (provisional — `T-095` row 21). The 200 from
`add_folder_member` is `awaitingAcceptance()`, because a new member still has
to mount the folder and `mount_folder` runs as the Peer, which Qori cannot do.
With `quiet: true` Dropbox sends no email and no device notification, so
Qori's own Series page is the Peer's only pointer to the Join step — that
sentence is this task's, as `T-092` says.

**A Peer who has joined says so with Check again, and is let in at once**
(`D-021`, 17 September 2026). The Join panel's action opens the folder on
dropbox.com in a new tab, so the Qori tab stays on the Series page, and
`T-091`'s Check again button (`shared.access.check`) sits after it. Pressing it
runs `VendorAccessService::checkNow()`, whose `verify()` ignores
`RECHECK_MINUTES`, so this task's `checkGrant()` reads `list_folder_members`
straight away and a Peer now under `users` is `granted` on the page they land
back on. The route, the throttle and the flashes are `T-091`'s; this task adds
none of them and only places the button in its panel.

**A buyer reads what Dropbox needs from them before paying** (`D-021`,
17 September 2026). `T-092` renders `App\Support\BuyerRequirements::for()`
beside the buy button and above its identity prompt on a free Series; this
task writes Dropbox's three lines under
`accesses.vendor.dropbox.before_buying.common.*` — a Dropbox account with a
verified email (a free one is enough), one Join in Dropbox once they have
access, and the space joining takes from their own Dropbox, with the free
allowance named `:basic_storage_gb`: `BuyerRequirements` passes every integer
and string entry of `qori.connections.dropbox` under its own key (`T-092`), so
the placeholder is the key that holds the figure, `basic_storage_gb` (2), the
one `limits.common.storage` reads too, and this task adds nothing to
`BuyerRequirements`. No tier lines are written: nothing a Peer has to bring
changes with the creator's Dropbox plan. `accesses.vendor.dropbox.join.space` stays at the Join step as
the repeat, for the Peer who reads it only when Dropbox says there isn't
room.

**A `granted` row is re-checked, and Open verifies before it redirects.**
`T-091` re-runs `checkGrant()` on `granted` rows past their `checked_at` (its
longer cadence, provisional) and on every Open, so first access is not the only
access Qori has evidence for. The case that needs it is Dropbox's own: a member
who later goes over quota has the folder taken off them
(https://help.dropbox.com/storage-space/over-quota), and the re-check finds
them in neither list and answers `pending` with
`GrantResult::ERROR_PERMISSION_GONE` — the code every provider's
`checkGrant()` gives a grant the vendor no longer holds (19 September 2026) —
so `T-091`'s `verify()` falls through to an attempt that adds them again,
which puts them back in `awaiting_acceptance` with the sentence naming
freeing space as their step.

**A repeated grant is not a failure.** The ensure step is idempotent, so
`add_folder_member` runs again for any row still `pending` or
`awaiting_acceptance`, and meets someone who is already a member or already an
invitee. Both answer `GrantResult::awaitingAcceptance($accountId)` — the add
never promotes a row, `checkGrant()` does — and `T-095` step 12 records the two
responses the code has to recognise.

**Open never sends a Peer to Dropbox before the grant is `granted`, and the
Join step lives on the Series page** (`D-020`, 17 September 2026). There is no
blocked page. While a Peer's Dropbox grant is not `granted`, `T-091` renders
the Series' Dropbox Episodes with their Open controls disabled and
`shared.vendor_notice.open_disabled` beside them, pointing at the notice
(id `access`) above the list. A page rendered before the state changed, a saved
link, or Open's own re-check finding the member gone still reaches `T-089`'s
`shared.episodes.open`, which turns `VendorLink::blocked()` into a redirect to
`shared.show` at `#access` with `shared.vendor_notice.redirected`. This task
adds no page and no route: it writes the Dropbox Join panel, and the notice
renders it in place of `T-091`'s generic
`shared.vendor_notice.reasons.awaiting_acceptance` line, selected by the
`provider` that `T-091`'s `vendor` prop carries. The other
three states keep `T-091`'s `shared.vendor_notice.reasons.*` sentences
(`T-092`'s prompt for `awaiting_identity`), so a `pending` Dropbox row says
when Qori tries next rather than "in a moment".

**Open is a 302 to the file's stored `preview_url`, with the folder as the
fallback** (provisional — `T-095` row 15 records the four URL shapes and which
one opens an Episode for a member). It is read once, at pick time, from
`sharing/get_file_metadata`, so building the link costs no vendor call — the
only Dropbox call Open can make is the re-check above; when the item check
has marked the file missing, Open sends the Peer to the container's own
`preview_url` instead, so they still see whatever is in the folder — the same
shape as `T-094`'s `webViewLink` fallback.

**Currency is Dropbox's own folder membership plus a re-resolve by path.**
Anything added, replaced or moved into the folder reaches every member with no
new grant (https://help.dropbox.com/share/join-folder-without-account;
https://developers.dropbox.com/dbx-sharing-guide). A file id survives moves and
renames, but a file created again with the same name gets a new one
(https://developers.dropbox.com/dbx-file-access-guide), so `checkItem()` lists
the container once, matches the stored `file_id`, then falls back to matching
`path_lower`; a match by path returns the new id on `ItemCheck::$externalId`
and the Episode is rewritten in place. Only a file gone from both is flagged.
The flag is `series.episode.dropbox.stale`, shown while `T-094`'s
`missingSince` prop is set on the Episode, and the creator who has put the
file back does not wait for the daily pass: the Check now button
(`share.series.episodes.check`) that `T-094` puts beside every Episode's check
warning reaches `T-091`'s `VendorAccessService::checkEpisode()`, which calls
this task's `checkItem()` for a Dropbox Episode (`D-021`, 17 September 2026).
The command is `T-094`'s `CheckEpisodeItemsCommand` (`qori:episodes:check`),
whose `checkItems()` pass loops over `checkEpisode()`; this task implements
`checkItem()` and builds nothing else for either.

**A refusal maps to one shared state by its Dropbox `.tag`,** in `T-091`'s
vocabulary, as the table under Code sets out. The three that matter: a
`rate_limit` — the unpublished daily invitation cap, which suspends all of the
creator's sharing for up to 24 hours
(https://help.dropbox.com/share/banned-links) — is `pending` with
`next_attempt_at` a day out, because retrying sooner cannot work and nobody
can act, and the Peer's `pending` sentence names that time (`D-020`);
`insufficient_plan` and every team-policy refusal are `needs_creator`, and a
creator who has upgraded or had the admin change the rule presses `T-091`'s
Try again now (`share.settings.integrations.retry`) rather than waiting for
the backoff (`D-021`); `bad_member/unverified_dropbox_id` is
`awaiting_identity`, because the Peer fixes it by verifying their address and
confirming again.

**Revoke is `remove_folder_member` with `leave_a_copy: false`, best effort.**
The `shared_folder_id` comes from the grant's own `external_container_id`,
because a replaced or removed container's row is already gone when the sweep
reaches it. A removal answering with an `async_job_id` is `RevokeResult::failed()` with
`ERROR_REMOVE_IN_PROGRESS`; `T-091`'s sweep calls the route again, and a
member already gone is treated as revoked. The job id is not stored — the
owner's terms are that revocation is best effort, and a second call is cheaper
than a column.

**What `T-091`'s three reconciliation triggers mean for Dropbox** (provisional
— `T-095` row 23 observes all three). A Peer confirming or changing an identity
(`T-092`) gives a different `dropbox_id`: `T-091` moves the row back to
`pending`, the next ensure adds the new account, and the account it replaced is
removed by the revoke pass, best effort. The creator reconnecting the **same**
account is a token swap and nothing more — the stored `shared_folder_id` still
answers, so the rows waiting on `invalid_access_token` simply succeed. A
**different** account is held by `T-044` for the creator to confirm before
anything applies (`D-021`); on Switch, that account's token cannot read the
stored id: `checkContainer()` answers `exists: false`, `T-091` marks the
container `Repick` and tells the creator to pick again, and no grant is
attempted until they do. People already in the old account's folder stay in
it: the new token cannot normally call `remove_folder_member` on a folder
another account owns, so once the creator picks again the revoke pass fails
up to `T-091`'s `REVOKE_ATTEMPTS` and stops, and only the old account can take
them off in Dropbox — the fact this task's
`connections.providers.dropbox.account_change.in_qori` states on `T-044`'s
confirmation page (provisional — `T-095` row 23). Replacing the container shares the new
folder and re-grants every Peer through the same ensure step.

**Replacing or removing the Dropbox folder goes through `T-091`'s
`ContainerChangeDialog`, and what it says is what Qori does** (`D-021`,
17 September 2026). Both take off, best effort through the revoke pass, the
members this task added: every `granted` and `awaiting_acceptance` row on the
old folder becomes revokable and `remove_folder_member` runs for its
`vendor_ref`. Nothing else in the creator's Dropbox moves — no file is touched,
people the creator added by hand stay, and the folder itself stays a shared
folder, because this task never calls `unshare_folder`; a creator who later
picks a folder around it meets `errors.series.container_nested`. A replace
adds one Dropbox consequence `T-091`'s generic sentence cannot know: every Peer
is a new invitee on the new folder, back in `awaiting_acceptance`, and cannot
open anything until they press Join again. So the dialog shows
`series.container.dropbox.change.replace` or `.remove` beneath `T-091`'s
`series.container_change.*` sentence — the action's `note`, which `T-091`'s
`containerImpact` entry fills from that key shape with no change to the dialog
or to its builder here — and the `checkEpisode()` call `T-091`
makes after a replace flags, on the page the creator lands on, every Dropbox
Episode whose file is not inside the new folder — a file moved across keeps
its `file_id` and is found, and one left behind matches neither its id nor its
old `path_lower` in the new folder's listing.

**No fallback is built for a Peer with too little Dropbox storage: the tier
copy states it before the creator connects, and the Peer is told what to do**
(`D-018`, 17 September 2026). Joining counts the folder's whole size against
the member's own storage, viewers included, and a member who later goes over
quota has the folder removed
(https://help.dropbox.com/storage-space/shared-folder-count-against-storage;
https://help.dropbox.com/storage-space/over-quota). Retrying cannot fix it, so
that Peer stays in `awaiting_acceptance` and `accesses.vendor.dropbox.join.space`
names freeing space as their step, while `limits.common.storage` says before
the connection is made that a shared folder costs each person their own space
and that somebody who has run out cannot join. Qori never switches that Peer
to a view-only link or to per-file grants behind the creator's back: the
platform a creator brings is the creator's own, and Qori states the limit,
says what it recommends, and lets them decide. Both alternatives are recorded
under Notes so a later reader does not re-propose them.

**The container and Episode pickers reuse `T-094`'s surfaces.**
`SeriesContainerController`, `StoreSeriesContainerRequest`, the folder panel on
the creator's Series page and `VendorAccessService::describeItem()` are
`T-094`'s, `ContainerChangeDialog` is `T-091`'s, and this task depends on
both, so they are edits here.

## Preconditions

`T-044` done, so `ProviderTier`, `ConnectsAccounts`, `ConnectionService`,
`lang/en/connections.php`, the Integrations page's provider sections,
`ProviderSections::ESSENTIAL` and `errors.series.provider_not_connected` exist;
`T-091` done, so `series_containers`, `vendor_grants`, `GrantsPeerAccess`, the
`app/Data` results, `VendorAccessService` with `checkNow()`, `impactOf()` and
`checkEpisode()`, `shared.access.check`, `ContainerChangeDialog` and
`qori:access:reconcile` exist; `T-092` done, so `IdentityProvider`,
`vendor_identities`, `ConfirmsPeerIdentity` and `BuyerRequirements` exist and
`identityFor()` answers with the Peer's confirmed Dropbox account; `T-095`
done, so `tests/Fixtures/dropbox/` holds every response named below; `T-094`
done, so `SeriesContainerController`, `StoreSeriesContainerRequest`, the folder
panel, `describeItem()`, `checkItems()`, `qori:episodes:check`,
`share.series.episodes.check` and the `missingSince` prop exist.

**Data this task verifies against:** a clean database for the tests. For the
browser walk, a Dropbox Plus creator connected on the Integrations page, one
published paid Series and one free Series, each with its own Dropbox folder
holding a PDF and a video **longer than the Basic streaming limit and inside
the Plus one**, so the Acceptance line about where playback stops can actually
be checked rather than assumed.

**Equipment:** the Dropbox app `T-095` registered, with `DROPBOX_APP_KEY` and
`DROPBOX_APP_SECRET` set and this environment's two redirect URIs on it,
`u/connections/dropbox/finalise` (`connections.oauth.finalise`) and
`u/identities/dropbox/finalise` (`T-092`'s `identities.finalise`). Both
landings take `{vendor}`, which is `dropbox` here because Dropbox is the
vendor and the service alike (`D-033`). Stripe test mode; two Dropbox accounts
in separate browser profiles, one with free space above the folder's size and
one below it; a phone; a visible browser at 400px and desktop widths.

**Spike:** `T-095`. Every request shape below is from the Stone spec or help
page cited beside it, and **every response field named below must appear in
the fixture named beside it, or the test that reads it is not written**.
Nothing here is an observed response yet.

## Scope

**In:**

- `App\Integrations\Dropbox\DropboxAccounts` (`T-044`'s `ConnectsAccounts`),
  `DropboxSignIn` (`T-092`'s `ConfirmsPeerIdentity`) and `DropboxStorage`
  reworked to `T-091`'s `GrantsPeerAccess`; the three tiers, each tier's
  limitation copy and the line saying what Qori recommends for it, the
  `dropbox` entry in `T-044`'s `ProviderSections::ESSENTIAL`, and the
  `disconnect.in_qori` and `account_change.in_qori` lines `T-044`'s Dialog and
  confirmation page show.
- `BrowsesStorage`, its Dropbox implementation and the browse route the two
  pickers read.
- Sharing the picked folder, the preparing state, `prepareContainers()` and
  the `Sharing` arm of the ensure step.
- The grant, the member-list check, the revoke, Open's link and the item
  check, with the failure mapping below.
- The Dropbox Join panel in the Series page's notice — its action opening the
  folder in a new tab, `T-091`'s Check again after it — selected by the
  `provider` on `T-091`'s `vendor` prop.
- Dropbox's before-buying lines, `accesses.vendor.dropbox.before_buying.common.*`.
- Replace and remove of the Dropbox folder through `ContainerChangeDialog`,
  with the Dropbox line beneath its sentence.
- The Episode content shape and its `describeItem()` confirmation.
- Removing `linkFor()` with its `get_temporary_link` call and the 240-minute
  ticket cap written inside it (`DropboxStorage.php:62-70`), and the
  `media-providers` binding; rewriting the three live places that still give
  the superseded reasoning.

**Out:**

- Google Drive, OneDrive, Zoom, Teams, Vimeo and YouTube.
- OAuth machinery itself, the tier dropdown component, reconnect, disconnect
  and `qori:connections:refresh` (`T-044`); the two tables, the ensure step,
  the states, the retry rule, the re-check cadence, the lock, the sweep and
  the Integrations page's failed-grant list (`T-091`); the Peer's sign-in
  pages and prompts (`T-092`); the Open route and its redirect of a blocked
  link (`T-089`), and the 502 page, which `T-113` shipped as
  `resources/views/errors/502.blade.php` on `errors.upstream_unavailable.*`.
- The Series-page notice itself, the disabled Open controls, Check again
  (`shared.access.check`), Try again now
  (`share.settings.integrations.retry`), `ContainerChangeImpact` and
  `ContainerChangeDialog` (`T-091`); the before-buying list and
  `BuyerRequirements` (`T-092`); the essential-and-more layout (`T-044`).
- `qori:episodes:check` (`CheckEpisodeItemsCommand`), Check now
  (`share.series.episodes.check`, `EpisodeCheckController`) and the
  `missingSince` prop, all `T-094`'s; this task implements the `checkItem()`
  the first two reach.
- Per-file grants, shared links, the Dropbox Chooser, and any fallback path
  for a Peer who cannot join — `D-018` settles that there is none, and the two
  alternatives considered are under Notes. The Chooser keeps its bullet below.
- Delayed payments and refunds (`T-102`, `T-103`), which come before any paid
  Series uses Dropbox.
- Detecting the creator's real plan from `users/get_current_account`; the tier
  is what the creator chose, as `T-044` built it.

## Files

| Path                                                                                                                 | Change | Notes                                                                                                                                                                                                                                                           |
| -------------------------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `app/Integrations/Dropbox/DropboxStorage.php`                                                                        | edit   | `ResolvesMedia` and `get_temporary_link` out, `GrantsPeerAccess` and `BrowsesStorage` in; `:17-19` rewritten                                                                                                                                                    |
| `app/Integrations/Dropbox/DropboxAccounts.php` `app/Integrations/Dropbox/DropboxSignIn.php`                          | new    | `T-044`'s and `T-092`'s contracts                                                                                                                                                                                                                               |
| `app/Integrations/Contracts/BrowsesStorage.php`                                                                      | new    | The picker's read, so no controller calls `Http::`                                                                                                                                                                                                              |
| `app/Data/StorageEntry.php`                                                                                          | new    | One folder or file in the browse list                                                                                                                                                                                                                           |
| `app/Data/ContainerCheck.php` `app/Data/ItemCheck.php` `app/Data/GrantResult.php`                                    | edit   | `T-091`'s; `externalId` and `preparing`; `ERROR_CONTAINER_PREPARING`                                                                                                                                                                                            |
| `app/Enums/SeriesContainerStatus.php` `app/Enums/ProviderTier.php`                                                   | edit   | `Sharing`; the three Dropbox tiers                                                                                                                                                                                                                              |
| `app/Services/VendorAccessService.php`                                                                               | edit   | `prepareContainers()`, the `Sharing` arm, the item id written back                                                                                                                                                                                              |
| `app/Providers/IntegrationServiceProvider.php`                                                                       | edit   | `DropboxStorage` into `T-091`'s `grant-providers`, `DropboxAccounts` into `T-044`'s `account-connectors`, `DropboxSignIn` into `T-092`'s `identity-providers`; `BrowsesStorage` bound to `DropboxStorage`; `DropboxStorage` out of `media-providers` (`:35-39`) |
| `app/Support/ProviderSections.php`                                                                                   | edit   | `T-044`'s; the `dropbox` entry in `ESSENTIAL`                                                                                                                                                                                                                   |
| `app/Http/Controllers/Share/DropboxController.php`                                                                   | new    | The browse route                                                                                                                                                                                                                                                |
| `app/Http/Requests/Share/BrowseDropboxRequest.php`                                                                   | new    |                                                                                                                                                                                                                                                                 |
| `app/Http/Requests/Share/StoreSeriesContainerRequest.php` `app/Http/Controllers/Share/SeriesContainerController.php` | edit   | `T-094`'s; `dropbox` in the provider rule, the folder refusals                                                                                                                                                                                                  |
| `app/Http/Requests/Share/StoreEpisodeRequest.php`                                                                    | edit   | A `dropbox` arm on `content()` (`:184-198`) above the `default`, which stays for `cloudflare_r2`                                                                                                                                                                |
| `app/Http/Controllers/Share/SeriesController.php`                                                                    | edit   | `T-094`'s; `prepareContainers($series)` in `show()` (`:137`) before the container prop is read                                                                                                                                                                  |
| `routes/share/payments.php`                                                                                          | edit   | The browse route beside `T-044`'s `share.connections.*`                                                                                                                                                                                                         |
| `resources/js/components/series/DropboxFolderPicker.vue`                                                             | new    | Folder mode and file mode, one component                                                                                                                                                                                                                        |
| `resources/js/pages/share/series/Show.vue`                                                                           | edit   | The `dropbox` arm of the Episode reference input (`:198-203`, `:290-296`), the folder panel slot; Dropbox replace and remove through `ContainerChangeDialog` with the Dropbox line                                                                              |
| `resources/js/pages/shared/Show.vue`                                                                                 | edit   | The Join panel in `T-091`'s notice: the action link, opening in a new tab, then `T-091`'s Check again                                                                                                                                                           |
| `lang/en/connections.php` `lang/en/series.php` `lang/en/accesses.php` `lang/en/errors.php`                           | edit   | Copy below; the first is `T-044`'s file; the third holds the Dropbox Join and before-buying lines, beside `T-091`'s state sentences in `T-089`'s `lang/en/shared.php`                                                                                           |
| `config/services.php` `config/qori.php` `.env.example`                                                               | edit   | `services.dropbox`; `qori.connections.dropbox`; the two app keys                                                                                                                                                                                                |
| `database/factories/SeriesContainerFactory.php`                                                                      | edit   | `T-091`'s; a `dropbox()` state                                                                                                                                                                                                                                  |
| `database/seeders/DesignReviewSeeder.php`                                                                            | edit   | `:355` and `:399` hold `['url' => …]`, which no Dropbox code has ever read                                                                                                                                                                                      |
| `tests/Feature/Integrations/Dropbox/DropboxGrantsTest.php` `tests/Feature/Series/DropboxContainerTest.php`           | new    | 17 and 12 cases; a vendor's own tests sit in `tests/Feature/Integrations/<Vendor>/`, as `Stripe/ClientTest.php` does                                                                                                                                            |
| `tests/Feature/Shared/DropboxJourneyTest.php` `tests/Feature/Integrations/Dropbox/DropboxAccountsTest.php`           | new    | 9 and 8 cases                                                                                                                                                                                                                                                   |
| `tests/Feature/Storage/PlaybackTest.php`                                                                             | edit   | The two Dropbox cases (`:107`, `:130`) — see Tests                                                                                                                                                                                                              |
| `docs/flows/vendor-access.md` `docs/flows/storage.md`                                                                | edit   | Created by `T-091`; the Dropbox chain added here; `:56`'s superseded reasoning rewritten                                                                                                                                                                        |
| `docs/tinker/series.md` `docs/project-plan.md`                                                                       | edit   | A recipe for sharing a folder by hand; §8's Dropbox row and §16's ticket line                                                                                                                                                                                   |

`docs/flows/vendor-access.md` and `docs/flows/storage.md` are the flow docs for
the `app/Http`, `app/Services` and `routes/` rows. `qori:reachability` sees the
browse route through its name in `DropboxFolderPicker.vue`
(`app/Support/Reachability.php:225` reads every `.vue` and `.ts` under
`resources/js`).

Rows marked `edit` on a file that is not in the repository yet are created by
the task named beside them — `T-044`, `T-091`, `T-092` or `T-094`, all four
dependencies of this one — and edited here once it lands.

## Database

None. `series_containers` and `vendor_grants` are `T-091`'s. This task writes
`series_containers.external_id` (the `shared_folder_id`, or `job:<id>` while
the status is `Sharing`), `url` (the folder's `preview_url`), `settings`
(`['path_lower' => …, 'name' => …]`) and `status`; and
`vendor_grants.vendor_ref` (the Peer's Dropbox `account_id`).
`episodes.content` (jsonb,
`database/migrations/2026_09_08_000000_create_qori_schema.php:113`) holds, for
`dropbox`: `file_id`, `name`, `path_lower`, `preview_url`, `checked_at`,
`missing_since` (null while the file is fine). The `path` key the old resolver
read (`DropboxStorage.php:40`) is not read again and no migration is written —
see Notes.

## Code

```php
namespace App\Enums;

// SeriesContainerStatus — T-091's enum
case Sharing = 'sharing';   // the vendor is still setting the container up; no grant is attempted

// ProviderTier — T-044's enum
case DropboxBasic = 'dropbox_basic';
case DropboxPaid = 'dropbox_paid';       // Plus, Family, Professional, Essentials
case DropboxTeam = 'dropbox_team';       // Standard, Business, Advanced, Business Plus, Enterprise
```

```php
namespace App\Integrations\Contracts;

/** Reading a connected account's own folders and files, for a picker. Never a grant. */
interface BrowsesStorage
{
    public function provider(): ConnectionProvider;
    /**
     * One level. $path is '' for the account root. $timeoutSeconds is the caller's budget, which the vendor's client
     * may only shorten: it waits the shorter of its own timeout and the budget (D-034). @return list<StorageEntry>
     */
    public function entries(Connection $connection, string $path, bool $includeFiles, int $timeoutSeconds): array;
}

// App\Data\StorageEntry — readonly string $id, $name, $path; readonly bool $isFolder.
```

```php
namespace App\Integrations\Dropbox;

/**
 * A creator's own Dropbox (D-016): one shared folder per Series, each Peer a
 * viewer member of it. Every $timeoutSeconds is the caller's budget — T-091's
 * REQUEST_TIMEOUT_SECONDS or SWEEP_TIMEOUT_SECONDS — which this client may only
 * shorten: each call waits the shorter of TIMEOUT_SECONDS and the budget (D-034).
 * The budget is passed in because an integration may not import app/Services
 * (tests/Feature/ArchitectureTest.php:139).
 */
class DropboxStorage implements BrowsesStorage, GrantsPeerAccess
{
    public const API = 'https://api.dropboxapi.com/2';
    /** Dropbox's own limit on one call, the 15 seconds DropboxStorage.php:51 sets today; a budget may only shorten it (D-034). */
    public const TIMEOUT_SECONDS = 15;
    /** external_id while a share is still running: the async job, not a folder. */
    public const JOB_PREFIX = 'job:';
    /** The invitation cap suspends sharing for up to a day; nothing sooner can succeed. */
    public const RATE_LIMIT_HOURS = 24;
    public const ERROR_NOT_A_FOLDER = 'not_a_folder';
    public const ERROR_REMOVE_IN_PROGRESS = 'remove_in_progress';
    public const ERROR_SHARE_JOB_FAILED = 'share_job_failed';    // needs_creator
    // A member Dropbox no longer lists is T-091's GrantResult::ERROR_PERMISSION_GONE, shared by every provider.

    public function provider(): ConnectionProvider;   // ConnectionProvider::Dropbox
    public function entries(Connection $connection, string $path, bool $includeFiles, int $timeoutSeconds): array;
    /** A folder path, or a job id: shares the folder, or reads the running job. */
    public function checkContainer(Connection $connection, string $externalId, int $timeoutSeconds): ContainerCheck;
    /** null identity → awaitingIdentity(), no call. Else add_folder_member by dropbox_id → awaitingAcceptance($accountId). */
    public function grant(Connection $connection, SeriesContainer $container, ?GrantIdentity $identity, string $email, int $timeoutSeconds): GrantResult;
    /** list_folder_members: vendor_ref under `users` → granted; under `invitees` → awaitingAcceptance; neither → pending(GrantResult::ERROR_PERMISSION_GONE). */
    public function checkGrant(Connection $connection, VendorGrant $grant, int $timeoutSeconds): GrantResult;
    /** remove_folder_member on $grant->external_container_id, leave_a_copy false; `complete` → revoked(); `async_job_id` → failed(ERROR_REMOVE_IN_PROGRESS). Never unshare_folder. */
    public function revoke(Connection $connection, VendorGrant $grant, int $timeoutSeconds): RevokeResult;
    /** content['preview_url'], or the container's url when content['missing_since'] is set. No call. accountHint is T-092's confirmed address. */
    public function openLink(Connection $connection, Episode $episode, ?VendorGrant $grant, int $timeoutSeconds): VendorLink;
    /** list_folder on the container, recursive: matched on file_id, then on path_lower — a path match answers externalId with the new id. The daily pass and Check now both reach it. */
    public function checkItem(Connection $connection, Episode $episode, int $timeoutSeconds): ItemCheck;

    private function client(Connection $connection, int $timeoutSeconds): PendingRequest;   // withToken, asJson, timeout(min(self::TIMEOUT_SECONDS, $timeoutSeconds)); no retry
    private function tag(Response $response): ?string;          // error['.tag'], then error['member_error']['.tag']
    private function failure(Response $response): GrantResult;  // the mapping table below
}
```

The calls, each with its reference and the `T-095` fixture its test reads.
Every route is `POST {API}/<route>` with a JSON body.

| Route                            | Body                                                                                                                               | Reference                                                                                                        | Fixture                                                                                                                                                                                                                         |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `files/list_folder`              | `{"path":"","recursive":false}`                                                                                                    | [files.stone](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/files.stone)                     | `files/list_folder.200.json`, `files/list_folder_continue.200.json`                                                                                                                                                             |
| `sharing/share_folder`           | `{"path":"/Series folder","acl_update_policy":"owner","force_async":false}`                                                        | [sharing_folders.stone](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/sharing_folders.stone) | `sharing/share_folder.complete.200.json`, `share_folder.async_job_id.200.json`, `share_folder.inside_shared_folder.<status>.json`, `share_folder.team_folder_path.<status>.json`, `share_folder.email_unverified.<status>.json` |
| `sharing/check_share_job_status` | `{"async_job_id":"…"}`                                                                                                             | sharing_folders.stone                                                                                            | `sharing/check_share_job_status.complete.200.json`                                                                                                                                                                              |
| `sharing/get_folder_metadata`    | `{"shared_folder_id":"…"}`                                                                                                         | sharing_folders.stone                                                                                            | `sharing/get_folder_metadata.creator.200.json`, `get_folder_metadata.other_account.<status>.json`                                                                                                                               |
| `sharing/add_folder_member`      | `{"shared_folder_id":"…","members":[{"member":{".tag":"dropbox_id","dropbox_id":"dbid:…"},"access_level":"viewer"}],"quiet":true}` | sharing_folders.stone; https://developers.dropbox.com/dbx-sharing-guide                                          | `sharing/add_folder_member.success.200.json` and each `add_folder_member.<tag>.<status>.json`                                                                                                                                   |
| `sharing/list_folder_members`    | `{"shared_folder_id":"…","limit":1000}`                                                                                            | sharing_folders.stone                                                                                            | `sharing/list_folder_members.200.json`, `list_folder_members.after_revoke.200.json`                                                                                                                                             |
| `sharing/remove_folder_member`   | `{"shared_folder_id":"…","member":{".tag":"dropbox_id","dropbox_id":"dbid:…"},"leave_a_copy":false}`                               | sharing_folders.stone                                                                                            | `sharing/remove_folder_member.200.json`, `check_remove_member_job_status.complete.200.json`                                                                                                                                     |
| `sharing/get_file_metadata`      | `{"file":"id:…"}`                                                                                                                  | [sharing_files.stone](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/sharing_files.stone)     | `sharing/get_file_metadata.creator.200.json`                                                                                                                                                                                    |

`failure()`, in `T-091`'s vocabulary. The `.tag` is what the fixture records;
this table is the candidate `T-095` confirms or corrects, and it is the same
table the spike's report owes.

| Dropbox outcome                                                                                                                                                                  | State                                                 | Who resolves                        |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- | ----------------------------------- |
| `add_folder_member` 200                                                                                                                                                          | `awaiting_acceptance`                                 | The Peer, by pressing Join          |
| `add_folder_member` repeated for an account already a member or already an invitee                                                                                               | `awaiting_acceptance`                                 | The Peer                            |
| `list_folder_members` shows the account under `users`                                                                                                                            | `granted`                                             | —                                   |
| `list_folder_members` shows it under `invitees`                                                                                                                                  | `awaiting_acceptance`                                 | The Peer                            |
| Under neither (`GrantResult::ERROR_PERMISSION_GONE`)                                                                                                                             | `pending`                                             | Nobody; the next attempt adds again |
| No confirmed Dropbox account, or `bad_member/unverified_dropbox_id`                                                                                                              | `awaiting_identity`                                   | The Peer (`T-092`)                  |
| `insufficient_plan`, `cant_share_outside_team`, `team_folder`, `no_permission`, `email_unverified`, `too_many_pending_invites`, `too_many_members`, `invalid_access_token` (401) | `needs_creator`                                       | The creator                         |
| `rate_limit`                                                                                                                                                                     | `pending`, `next_attempt_at` now + `RATE_LIMIT_HOURS` | Nobody                              |
| `429` with `Retry-After`, `too_many_write_operations`, a 5xx, a timeout, a container still `Sharing`                                                                             | `pending`                                             | Nobody                              |
| `remove_folder_member` `complete`, or a member already gone                                                                                                                      | `revoked`                                             | —                                   |

```php
// App\Services\VendorAccessService — additions to T-091's class
/**
 * Containers whose status is Sharing, for the current Group or one Series: checkContainer() once each with the
 * caller's budget, writing back the id the vendor settled on and setting Active. Called from retryDue() and from
 * SeriesController::show(). Never throws. Rows touched.
 */
public function prepareContainers(?Series $series = null, int $timeoutSeconds = self::REQUEST_TIMEOUT_SECONDS): int;
// ensureFor(), before attempt(): a container whose status is Sharing → pending, GrantResult::ERROR_CONTAINER_PREPARING,
//   next_attempt_at now + BACKOFF_MINUTES[0], no vendor call.
// attach(): stores ContainerCheck::$externalId ?? $externalId, and status Sharing when ContainerCheck::$preparing.
// describeItem() (T-094's): writes ItemCheck::$externalId back over content['file_id'] when the vendor re-resolved it.

// App\Data — T-091's results
class ContainerCheck { public ?string $externalId = null; public bool $preparing = false; /* exists, url, errorCode, upstream unchanged */ }
class ItemCheck      { public ?string $externalId = null; /* beside T-091's nullable name, mimeType and url */ }
// App\Data\GrantResult
public const ERROR_CONTAINER_PREPARING = 'container_preparing';   // pending
```

```php
// App\Support\ProviderSections — T-044's ordered constant gains; keys relative to connections.providers.dropbox.limits.
'dropbox' => [
    'dropbox_basic' => ['common.accounts', 'dropbox_basic.plan', 'dropbox_basic.video'],
    'dropbox_paid' => ['common.accounts', 'common.storage', 'common.folder'],
    'dropbox_team' => ['common.accounts', 'dropbox_team.outside', 'common.folder'],
],
```

```php
namespace App\Integrations\Dropbox;

/**
 * Endpoints from https://developers.dropbox.com/oauth-guide. Every call: ->timeout(min(DropboxStorage::TIMEOUT_SECONDS,
 * $timeoutSeconds)), Dropbox's one limit, which T-044's budget may only shorten (D-034), and no retry: a code is single-use.
 */
class DropboxAccounts implements ConnectsAccounts
{
    public const AUTHORIZE_URL = 'https://www.dropbox.com/oauth2/authorize';
    public const TOKEN_URL = 'https://api.dropboxapi.com/oauth2/token';
    public const REVOKE_URL = 'https://api.dropboxapi.com/2/auth/token/revoke';
    public const ACCOUNT_URL = 'https://api.dropboxapi.com/2/users/get_current_account';
    /** @var list<string> */
    public const SCOPES = ['account_info.read', 'files.metadata.read', 'sharing.read', 'sharing.write'];
    // provider(): Dropbox. refreshesOnSchedule(): false — a Dropbox refresh token does not expire. requiredScopes(): SCOPES.
    // supportsPkce(): true (provisional — see below).
    // beginConnection():     client_id, redirect_uri, response_type=code, scope (space-separated), token_access_type=offline, state,
    //                        code_challenge and code_challenge_method=S256 when given; no login hint
    // finaliseConnection():  T-044's contract — the landing read in Dropbox's words and answered as a ConnectionLanding, never
    //                        throwing, in Connect::finaliseOnboarding()'s order (app/Integrations/Stripe/Connect.php:74-151):
    //                        $matches = $expectedState !== '' && hash_equals($expectedState, the landing's state);
    //                        an error whose state is present and does not match → notFromQori(); error=access_denied, the OAuth 2.0
    //                        word for a refusal (RFC 6749 §4.1.2.1; provisional until a round trip shows Dropbox's) → declined();
    //                        any other error word → failed(<the word>); no error and ! $matches → notFromQori(); no code → failed();
    //                        no call on any of these. No arm answers adminBlocked(): no Dropbox landing word is known for a team
    //                        admin's refusal, and a team's sharing policy surfaces at the grant, as needs_creator.
    //                        POST TOKEN_URL form grant_type=authorization_code, code, client_id, client_secret, redirect_uri
    //                        (+ code_verifier when given) → access_token, expires_in, refresh_token, scope, account_id
    //                        [oauth2/token.offline.200.json]; a ConnectionException → failed('connection'); a 4xx or 5xx →
    //                        failed(<status>), logged with Dropbox's `error` word alone, never the body, which may quote the code;
    //                        a granted scope short of requiredScopes() → POST REVOKE_URL with that access token, best effort, then
    //                        scopeDeclined(); else connected(new ConnectionTokens(...)).
    // refresh():             POST TOKEN_URL form grant_type=refresh_token — no rotated refresh token is documented
    // revoke():              POST REVOKE_URL with the bearer token; it kills the refresh token too
    // identity():            POST ACCOUNT_URL, no body → account_id, name.display_name, email  [users/get_current_account.plus.200.json]
}

/** https://developers.dropbox.com/oidc-guide — Dropbox calls its OIDC support a preview that is safe for production. */
class DropboxSignIn implements ConfirmsPeerIdentity
{
    public const SCOPES = 'openid email';
    // provider(): IdentityProvider::Dropbox
    // beginConfirmation(): DropboxAccounts::AUTHORIZE_URL with response_type=code, scope=SCOPES, redirect_uri, state, nonce;
    //   client_id from config('services.dropbox.app_key'); no token_access_type, and no login hint, since none is recorded for Dropbox.
    // finaliseConfirmation(), T-092's contract, in the order GoogleSignIn reads Google's (T-092), with $matches as
    //   DropboxAccounts computes it:
    //   an error whose state is present and does not match → notFromQori(); error=access_denied → declined();
    //   any other error word → failed(<the word>); no error and ! $matches → notFromQori(); no code → failed(); no call on any of these;
    //   POST DropboxAccounts::TOKEN_URL form grant_type=authorization_code, code, redirect_uri, client_id, client_secret,
    //     ->timeout(min(DropboxStorage::TIMEOUT_SECONDS, $timeoutSeconds)), no retry → id_token  [oauth2/token.openid.200.json];
    //   no answer (a ConnectionException, a timeout included) → failed('connection'); a 4xx or 5xx → failed(<status>);
    //   the id_token's payload  [oauth2/token.openid.claims.json]: aud not the app key, exp past, or a nonce that is not
    //     hash_equals($expectedNonce) → failed('id_token') — T-095 step 17 sent no nonce, so whether Dropbox echoes one is
    //     unrecorded (provisional); email_verified not true → unverifiedEmail();
    //   else confirmed(new VendorIdentityData(Dropbox, sub, email)), sub being the account_id T-095 row 16 checks.
    //   Every token is discarded and the access_token is never read. No `use App\Services`.
}
```

```php
namespace App\Http\Controllers\Share;

class DropboxController extends Controller
{
    /**
     * JSON {entries, path}: one level of the owner's Dropbox. Owner only, as T-094's picker route is;
     * T-044's ConnectionService::fresh() first, and errors.series.provider_not_connected when there is
     * no live Dropbox connection. The budget is VendorAccessService::REQUEST_TIMEOUT_SECONDS, which the client may only shorten (D-034).
     */
    public function entries(
        BrowseDropboxRequest $request,
        string $group,
        CurrentGroup $current,
        ConnectionService $connections,
        BrowsesStorage $storage,
    ): JsonResponse;
}

// App\Http\Requests\Share\BrowseDropboxRequest — 'path' => ['nullable','string','max:500'], 'files' => ['boolean']
// App\Http\Requests\Share\StoreSeriesContainerRequest (T-094's) — 'provider' gains ConnectionProvider::Dropbox->value;
//   'external_id' carries the folder's path_lower, which checkContainer() turns into a shared_folder_id.
// App\Http\Requests\Share\StoreEpisodeRequest::content() — a new arm above the default (:196), which stays
//   as written for EpisodeProvider::CloudflareR2:
//   EpisodeProvider::Dropbox => ['file_id' => $reference, 'name' => $this->input('file_name'), 'path_lower' => $this->input('file_path')],
//   'file_name' and 'file_path' are ['nullable','string','max:500']; describeItem() overwrites all three from the vendor.
```

```php
// config/services.php
'dropbox' => ['app_key' => env('DROPBOX_APP_KEY'), 'app_secret' => env('DROPBOX_APP_SECRET')],
// config/qori.php, under 'connections' — every number the tier copy interpolates. BuyerRequirements (T-092) passes each
// integer and string entry under its own key, so before_buying.common.space names :basic_storage_gb.
'dropbox' => [
    'basic_storage_gb' => 2, 'basic_streaming_minutes' => 30, 'basic_bandwidth_gb' => 20,
    'basic_downloads_per_day' => 100000, 'paid_streaming_hours' => 2, 'paid_bandwidth_tb' => 1,
    'team_streaming_hours' => 4, 'team_bandwidth_tb' => 1, 'top_bandwidth_tb' => 4,
    'sharing_pause_hours' => 24, 'member_cap' => 1000,
],
```

`T-091`'s `vendor` prop carries `provider` and the container's `url`;
`Show.vue` renders
`accesses.vendor.dropbox.join.*` inside the notice (id `access`) in place of
`T-091`'s `shared.vendor_notice.reasons.awaiting_acceptance` sentence when it
is `dropbox` and the state is `awaiting_acceptance`, with the container's `url`
as the action link (`target="_blank"`, `rel="noopener"`), and `T-091`'s Check
again button after it — the same component `T-091` renders for the generic
line, posting `shared.access.check`, with no route or copy of this task's.
`SeriesController::show()` calls `prepareContainers($series)` before reading
the container, so a creator reloading the page finishes an asynchronous share
without waiting for the sweep. `T-091`'s `containerImpact` entry for a
Dropbox container carries `series.container.dropbox.change.replace` and
`.remove` as each action's `note`, found by key, and the folder panel's change
and remove controls open `ContainerChangeDialog` with that entry before
`share.series.container.store` or `.destroy` is posted. `DropboxFolderPicker.vue`
reads the browse route, walks one level at a time, and posts `external_id` and
`name` in folder mode, or `reference`, `file_name` and `file_path` into the
Episode form in file mode; `providerLabels` (`:290-296`) already spells
Dropbox, and the `allowed` map (`:198-203`) is unchanged. The `stale` line on a
Dropbox Episode row shows while `T-094`'s `missingSince` prop is set, read as
`T-094` passes it, and carries the Check now button `T-094` renders beside
every check warning; nothing Dropbox-specific is added to either.

## Copy

Numbers come from `config('qori.connections.dropbox.*')`; no sentence restates
one. Vendor names appear under `D-016`'s stated exception. The provider name,
the tier labels and every shared connection sentence are `T-044`'s.

| Key                                                             | File                      | English                                                                                                                                                                                                                                                                                                                                                           |
| --------------------------------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `connections.providers.dropbox.name`                            | `lang/en/connections.php` | Dropbox                                                                                                                                                                                                                                                                                                                                                           |
| `connections.providers.dropbox.description`                     | `lang/en/connections.php` | Share files from one Dropbox folder per :series. Everyone with access is invited to that folder, and whatever you put there reaches them.                                                                                                                                                                                                                         |
| `connections.providers.dropbox.tiers.dropbox_basic.label`       | `lang/en/connections.php` | Dropbox Basic                                                                                                                                                                                                                                                                                                                                                     |
| `connections.providers.dropbox.tiers.dropbox_basic.help`        | `lang/en/connections.php` | A free Dropbox account, or a plan still in its trial.                                                                                                                                                                                                                                                                                                             |
| `connections.providers.dropbox.tiers.dropbox_basic.recommended` | `lang/en/connections.php` | Best for documents and short clips. For longer video, or for a paid :series, Qori recommends a paid Dropbox plan — it lifts the playback and traffic limits.                                                                                                                                                                                                      |
| `connections.providers.dropbox.tiers.dropbox_paid.label`        | `lang/en/connections.php` | Dropbox Plus, Family, Professional or Essentials                                                                                                                                                                                                                                                                                                                  |
| `connections.providers.dropbox.tiers.dropbox_paid.help`         | `lang/en/connections.php` | A paid personal Dropbox plan.                                                                                                                                                                                                                                                                                                                                     |
| `connections.providers.dropbox.tiers.dropbox_paid.recommended`  | `lang/en/connections.php` | Recommended for most creators: long video plays, and the daily traffic allowance covers :series_plural shared widely. Everyone who joins still needs room in their own Dropbox.                                                                                                                                                                                   |
| `connections.providers.dropbox.tiers.dropbox_team.label`        | `lang/en/connections.php` | Dropbox for teams                                                                                                                                                                                                                                                                                                                                                 |
| `connections.providers.dropbox.tiers.dropbox_team.help`         | `lang/en/connections.php` | Standard, Business, Advanced, Business Plus or Enterprise, where an admin sets the sharing rules.                                                                                                                                                                                                                                                                 |
| `connections.providers.dropbox.tiers.dropbox_team.recommended`  | `lang/en/connections.php` | Recommended when your admin already allows sharing outside the team. Ask them before you connect, because Qori can't add anybody until they do, and pick a folder inside a team folder rather than the team folder itself.                                                                                                                                        |
| `connections.providers.dropbox.limits.common.accounts`          | `lang/en/connections.php` | Everyone you share with needs a Dropbox account with a verified email. They confirm it in Qori once, and must be signed in to it. A free account is enough.                                                                                                                                                                                                       |
| `connections.providers.dropbox.limits.common.join`              | `lang/en/connections.php` | Each person presses Join on your folder once, in Dropbox. Dropbox sends them nothing, so Qori shows them where.                                                                                                                                                                                                                                                   |
| `connections.providers.dropbox.limits.common.storage`           | `lang/en/connections.php` | Joining counts the whole folder's size against that person's own Dropbox space, and a free Dropbox account has :gigabytes GB. Somebody with less free space than the folder can't join, and later uploads that push them over lose them the folder. Qori recommends keeping each folder small enough for that, and telling people what it costs before they join. |
| `connections.providers.dropbox.limits.common.folder`            | `lang/en/connections.php` | Pick one folder for each :series and keep everything for it inside. Sharing the folder shares everything in it, :episode_plural or not. It can't sit inside another shared folder or hold one.                                                                                                                                                                    |
| `connections.providers.dropbox.limits.common.updating`          | `lang/en/connections.php` | To update a file, upload it with exactly the same name to the same place, and the :episode in Qori keeps pointing at it. A file uploaded under another name is a new file: people still see it in the folder, and the :episode in Qori needs picking again.                                                                                                       |
| `connections.providers.dropbox.limits.common.invites`           | `lang/en/connections.php` | Dropbox limits how many invitations you can send in a short time. Going over pauses all your sharing for up to :hours hours, so people who get access then wait. Qori keeps trying and lets them in as soon as Dropbox allows it.                                                                                                                                 |
| `connections.providers.dropbox.limits.common.members`           | `lang/en/connections.php` | One Dropbox folder holds up to :people people.                                                                                                                                                                                                                                                                                                                    |
| `connections.providers.dropbox.limits.common.terms`             | `lang/en/connections.php` | From 1 January 2027, Dropbox is for people aged 18 and over, and free accounts left unused for six months can be closed. Either one ends that person's access.                                                                                                                                                                                                    |
| `connections.providers.dropbox.limits.common.revoked`           | `lang/en/connections.php` | If you unlink Qori in your Dropbox account, nobody new gets access until you connect again, and while it is unlinked Qori can't take anyone off a folder, even when their access in Qori ends.                                                                                                                                                                    |
| `connections.providers.dropbox.limits.dropbox_basic.video`      | `lang/en/connections.php` | Video and audio stop after the first :minutes minutes for everyone except you, and play at up to 1080p.                                                                                                                                                                                                                                                           |
| `connections.providers.dropbox.limits.dropbox_basic.bandwidth`  | `lang/en/connections.php` | Up to :gigabytes GB and :downloads downloads a day can be viewed or taken from what you share. Over that, Dropbox pauses your sharing for :hours hours, and longer if it keeps happening.                                                                                                                                                                         |
| `connections.providers.dropbox.limits.dropbox_basic.plan`       | `lang/en/connections.php` | Adding people to a folder may need a paid Dropbox plan. Qori tells you if Dropbox refuses, and you can upgrade with Dropbox or share this :series from another provider instead.                                                                                                                                                                                  |
| `connections.providers.dropbox.limits.dropbox_paid.video`       | `lang/en/connections.php` | Video and audio stop after the first :hours hours for everyone except you, and play at up to 4K. Dropbox names Plus, Family and Professional for that limit and doesn't name Essentials.                                                                                                                                                                          |
| `connections.providers.dropbox.limits.dropbox_paid.bandwidth`   | `lang/en/connections.php` | Up to :terabytes TB a day can be viewed or taken from what you share. Over that, Dropbox pauses your sharing for :hours hours, and longer if it keeps happening.                                                                                                                                                                                                  |
| `connections.providers.dropbox.limits.dropbox_team.outside`     | `lang/en/connections.php` | Your team admin must allow adding people outside the team. The default is team members only, and then nobody can be added at all. If your admin allows only approved people, only their addresses work.                                                                                                                                                           |
| `connections.providers.dropbox.limits.dropbox_team.subfolder`   | `lang/en/connections.php` | Pick a folder inside a team folder, never the team folder itself.                                                                                                                                                                                                                                                                                                 |
| `connections.providers.dropbox.limits.dropbox_team.video`       | `lang/en/connections.php` | Video and audio stop after the first :hours hours for everyone except you on Standard, Advanced and Enterprise. Dropbox doesn't say what Business and Business Plus do.                                                                                                                                                                                           |
| `connections.providers.dropbox.limits.dropbox_team.bandwidth`   | `lang/en/connections.php` | Up to :terabytes TB a day on Standard and Business, and :top TB on Advanced, Business Plus and Enterprise.                                                                                                                                                                                                                                                        |
| `connections.providers.dropbox.limits.dropbox_team.leaving`     | `lang/en/connections.php` | If you leave the team, or your admin removes your account, every :episode that uses these files stops working.                                                                                                                                                                                                                                                    |
| `connections.grants.reasons.insufficient_plan`                  | `lang/en/connections.php` | your Dropbox plan doesn't allow adding people to this folder                                                                                                                                                                                                                                                                                                      |
| `connections.grants.reasons.cant_share_outside_team`            | `lang/en/connections.php` | your Dropbox admin doesn't allow adding people outside the team                                                                                                                                                                                                                                                                                                   |
| `connections.grants.reasons.team_folder`                        | `lang/en/connections.php` | people can't be added to a team folder itself; pick a folder inside it                                                                                                                                                                                                                                                                                            |
| `connections.grants.reasons.email_unverified`                   | `lang/en/connections.php` | the email on your Dropbox account isn't verified; verify it with Dropbox                                                                                                                                                                                                                                                                                          |
| `connections.grants.reasons.too_many_pending_invites`           | `lang/en/connections.php` | too many people you invited haven't joined yet                                                                                                                                                                                                                                                                                                                    |
| `connections.grants.reasons.too_many_members`                   | `lang/en/connections.php` | this Dropbox folder is full                                                                                                                                                                                                                                                                                                                                       |
| `connections.grants.reasons.no_permission`                      | `lang/en/connections.php` | your Dropbox account can't share this folder                                                                                                                                                                                                                                                                                                                      |
| `connections.providers.dropbox.disconnect.in_qori`              | `lang/en/connections.php` | :peer_plural already let in stay members of your folders in Dropbox and keep opening their :episode_plural from Qori. Nobody new is let in, even after pressing Join, and anyone whose access ends in the meantime stays in the folder, until you connect :account again: then Qori lets in everyone waiting and takes those people off.                          |
| `connections.providers.dropbox.account_change.in_qori`          | `lang/en/connections.php` | :peer_plural already in your folders in :current stay members until you remove them there; once you switch, Qori can't reach :current to do it for you. Their :episode_plural stop opening from Qori at their next check, until each folder is picked again from :incoming and they press Join on the new one.                                                    |
| `accesses.vendor.dropbox.join.title`                            | `lang/en/accesses.php`    | One step in Dropbox                                                                                                                                                                                                                                                                                                                                               |
| `accesses.vendor.dropbox.join.body`                             | `lang/en/accesses.php`    | :creator has invited :email to the Dropbox folder this :series is kept in. Open it in Dropbox, press Join once, then come back to this page and check again.                                                                                                                                                                                                      |
| `accesses.vendor.dropbox.join.space`                            | `lang/en/accesses.php`    | Joining uses as much of your own Dropbox space as the folder holds. If Dropbox says there isn't room, free some space and press Join again.                                                                                                                                                                                                                       |
| `accesses.vendor.dropbox.join.action`                           | `lang/en/accesses.php`    | Open the folder in Dropbox                                                                                                                                                                                                                                                                                                                                        |
| `accesses.vendor.dropbox.before_buying.common.account`          | `lang/en/accesses.php`    | A Dropbox account with a verified email address. A free one is enough, and you confirm which account in Qori once.                                                                                                                                                                                                                                                |
| `accesses.vendor.dropbox.before_buying.common.join`             | `lang/en/accesses.php`    | One step in Dropbox once you have access: press Join on the folder this :series is kept in. Qori shows you where.                                                                                                                                                                                                                                                 |
| `accesses.vendor.dropbox.before_buying.common.space`            | `lang/en/accesses.php`    | Joining uses as much of your own Dropbox space as the folder holds, and a free Dropbox account has :basic_storage_gb GB. If yours is nearly full, free some space first.                                                                                                                                                                                          |
| `series.container.dropbox.pick`                                 | `lang/en/series.php`      | Choose the Dropbox folder for this :series                                                                                                                                                                                                                                                                                                                        |
| `series.container.dropbox.explain`                              | `lang/en/series.php`      | Everyone with access to this :series can open everything inside the folder you choose, :episode_plural or not. Use a folder that holds only this :series, and not one inside another shared folder.                                                                                                                                                               |
| `series.container.dropbox.connect_first`                        | `lang/en/series.php`      | Connect Dropbox under Integrations to choose a folder.                                                                                                                                                                                                                                                                                                            |
| `series.container.dropbox.sharing`                              | `lang/en/series.php`      | Dropbox is still setting this folder up, so nobody can be invited yet. Qori checks again each time this page loads, and on its own, and invites everyone as soon as it is ready.                                                                                                                                                                                  |
| `series.container.dropbox.change.replace`                       | `lang/en/series.php`      | In Dropbox, each of them is invited to the new folder and has to press Join again before they can open anything; Qori shows them where. The old folder stays shared in your Dropbox, with anyone you added yourself, until you unshare it there.                                                                                                                  |
| `series.container.dropbox.change.remove`                        | `lang/en/series.php`      | Anyone you added to the folder yourself stays in it, and the folder stays shared in your Dropbox until you unshare it there.                                                                                                                                                                                                                                      |
| `series.episode.dropbox.pick`                                   | `lang/en/series.php`      | Choose a file from the folder                                                                                                                                                                                                                                                                                                                                     |
| `series.episode.dropbox.stale`                                  | `lang/en/series.php`      | Qori can no longer find this file in the folder. If you put it back in the same place under the same name, check now; otherwise pick it again. People still see whatever is in the folder.                                                                                                                                                                        |
| `errors.series.container_nested.message`                        | `lang/en/errors.php`      | That folder is inside another shared folder, or holds one.                                                                                                                                                                                                                                                                                                        |
| `errors.series.container_nested.resolution`                     | `lang/en/errors.php`      | Choose a folder that isn't shared yet and has no shared folder inside it.                                                                                                                                                                                                                                                                                         |
| `errors.series.container_team_folder.message`                   | `lang/en/errors.php`      | People outside your team can't be added to a team folder itself.                                                                                                                                                                                                                                                                                                  |
| `errors.series.container_team_folder.resolution`                | `lang/en/errors.php`      | Choose a folder inside it instead.                                                                                                                                                                                                                                                                                                                                |
| `errors.series.container_not_a_folder.message`                  | `lang/en/errors.php`      | That isn't a folder.                                                                                                                                                                                                                                                                                                                                              |
| `errors.series.container_not_a_folder.resolution`               | `lang/en/errors.php`      | Choose a folder, not a file.                                                                                                                                                                                                                                                                                                                                      |

Each tier's `recommended` line is what `D-018` asks for beside its `limits.*`
lines: the limitation says what the tier will not do, the recommendation says
what to do about it, and the Integrations page renders both before the
creator connects. `connections.providers.dropbox.limits.dropbox_basic.plan` is
written for either answer to `T-095` row 1 — "may need a paid Dropbox plan" if
a Basic creator is sometimes refused, and the plainer "needs a paid Dropbox
plan" if Basic is always refused. **No tier is dropped either way** (`D-018`):
a plan Dropbox will not let share is a vendor capability the entry states, not
a choice Qori takes away. Which three lines of each tier are essential is the
`ESSENTIAL` entry under Code; `T-044`'s test holds it to keys that exist and to
`MAX_ESSENTIAL`, and the order of the Copy table is the order `more` keeps.

`accesses.vendor.dropbox.join.space` is dropped if `T-095` row 5 shows an
invitee can open the folder without joining, which also removes
`limits.common.storage`, `before_buying.common.join` and `.space`, Paid's
`common.storage` from `ESSENTIAL`, and most of this task's reason to sit in
`awaiting_acceptance` at all. The three `before_buying.common` lines are in
the order `BuyerRequirements` lists them, and `.space` names
`:basic_storage_gb`, the key `BuyerRequirements` passes that figure under
(`T-092`), the same one `limits.common.storage` reads; `join.space` repeats
the cost at the Join step
without the number, because by then the Peer's own Dropbox is telling them
what is left. `disconnect.in_qori` and `account_change.in_qori` are the two
lines `T-044` asks of every connectable provider (`D-021` rule 3), written from
`T-091`'s rules for a connection that is not live and the switch fact under
Decisions; `:account`, `:current` and `:incoming` are filled as `T-044` fills
them. `:creator` is the Group's name, as `T-092`'s
`identities.prompt.body.dropbox` uses it, and `:email` the Peer's confirmed
Dropbox address, as `identities.open_with` uses it. "check again" in
`join.body` and "check now" in `episode.dropbox.stale` name the buttons
beside them — `T-091`'s `shared.vendor_notice.check_again` and `T-094`'s
`series.episode_check.check_now` — in running text rather than restating their
labels. The `shared.vendor_notice.reasons.*` sentences for `pending`,
`needs_creator` and `awaiting_identity`, the redirect and disabled-Open lines,
and the Check again flashes are `T-091`'s and `T-089`'s in
`lang/en/shared.php`; `series.container_change.*` is `T-091`'s, and the
`.change.*` lines here only add what is true of Dropbox alone; the sign-in
prompts and `identities.requirements.title` are `T-092`'s in
`lang/en/identities.php`. Nothing here repeats one.
Numbers not in `config` — 1080p, 4K and the two dates in
`limits.common.terms` — are Dropbox's own wording rather than a Qori limit, so
they are stated once here and nowhere else. `limits.common.members`'s figure is
the one number here that no fixture can back: 1,000 comes from Dropbox's team
deployment page (https://help.dropbox.com/plans/large-deployments) and is
unconfirmed for personal plans, and `T-095` says outright that a spike cannot
reach `too_many_members`. The runtime guard is the error tag, not the number,
so if the spike cannot confirm it the line is dropped rather than guessed at.
No line puts an article directly before a noun placeholder
(`tests/Feature/TerminologyTest.php`).

## Routes

| Verb | Path                                     | Name                                | Action                             |
| ---- | ---------------------------------------- | ----------------------------------- | ---------------------------------- |
| GET  | `/g/{group}/connections/dropbox/entries` | `share.connections.dropbox.entries` | `Share\DropboxController::entries` |

In `routes/share/payments.php`, beside `T-044`'s `share.connections.*` and
`share.settings.integrations`, inside the sharing group
(`routes/share.php:24-27`). JSON, not a page, so no slug is involved; `path` is
a query parameter naming a folder in the creator's own account. The container
writes are `T-094`'s `share.series.container.store` and `.destroy`, and Open is
`T-089`'s `shared.episodes.open`. The three buttons this task's surfaces show
are other tasks' routes, and nothing here adds one: Check again is `T-091`'s
`shared.access.check`, Try again now `T-091`'s
`share.settings.integrations.retry`, and Check now `T-094`'s
`share.series.episodes.check` (`D-021`).

## Tests

Every case fakes HTTP with the named fixture through
`Http::fake(['api.dropboxapi.com/*' => …])`, under a
`Http::preventStrayRequests()` in `setUp` as
`tests/Feature/Storage/PlaybackTest.php:36` has it and a per-case fake as
`:109` has it; the real `DropboxStorage` is resolved through `T-091`'s
`grant-providers` tag, and the Peer's identity comes from `T-092`'s factory.

**New: `tests/Feature/Integrations/Dropbox/DropboxGrantsTest.php` — 17 cases**

1. `test_it_shares_the_picked_folder_and_stores_the_shared_folder_id`
2. `test_an_asynchronous_share_leaves_the_container_preparing` — `externalId` is `job:…`, status `Sharing`.
3. `test_a_folder_inside_another_shared_folder_is_refused`
4. `test_a_team_folder_itself_is_refused`
5. `test_it_adds_the_peer_as_a_quiet_viewer_by_dropbox_id` — the body carries `dropbox_id`, `viewer` and `quiet`.
6. `test_a_grant_without_a_confirmed_dropbox_account_makes_no_call` — `awaiting_identity`; zero requests.
7. `test_a_new_grant_is_awaiting_acceptance_not_granted`
8. `test_the_member_list_promotes_a_joined_peer_to_granted`
9. `test_a_peer_only_in_the_invitee_list_stays_awaiting_acceptance`
10. `test_a_repeated_grant_for_an_existing_member_or_invitee_is_not_a_failure` — the ensure step runs twice; the row stays `awaiting_acceptance` and `last_error_code` is null.
11. `test_a_member_dropbox_lost_is_pending_and_added_again` — the re-check of a `granted` row whose account is in neither list answers `pending` with `GrantResult::ERROR_PERMISSION_GONE`, and the attempt it falls through to adds the account again.
12. `test_insufficient_plan_needs_the_creator`
13. `test_a_team_policy_refusal_needs_the_creator` — `cant_share_outside_team`.
14. `test_an_unverified_dropbox_id_waits_for_the_peer`
15. `test_the_invitation_cap_is_pending_until_tomorrow` — `rate_limit`; `next_attempt_at` ≈ +24 hours.
16. `test_a_429_is_pending_with_the_retry_after_and_a_timeout_carries_its_seconds` — and the fake received `REQUEST_TIMEOUT_SECONDS`, while the sweep's `SWEEP_TIMEOUT_SECONDS` is cut to `DropboxStorage::TIMEOUT_SECONDS` (`D-034`).
17. `test_it_removes_the_member_on_revoke_and_leaves_a_running_job_for_the_sweep`

**New: `tests/Feature/Series/DropboxContainerTest.php` — 12 cases**

18. `test_the_owner_browses_their_dropbox_folders`
19. `test_an_admin_cannot_browse_or_attach_a_folder`
20. `test_attaching_a_folder_creates_pending_rows_and_calls_no_grant`
21. `test_a_preparing_container_grants_nothing_and_says_so_on_the_series_page`
22. `test_the_sweep_finishes_an_asynchronous_share_and_the_next_ensure_grants`
23. `test_a_dropbox_episode_needs_the_series_folder_first`
24. `test_a_dropbox_episode_outside_the_folder_is_refused`
25. `test_a_dropbox_episode_stores_the_file_id_name_and_path`
26. `test_the_item_check_re_resolves_a_replaced_file_by_its_path` — `content['file_id']` rewritten, `missing_since` null.
27. `test_check_now_finds_a_dropbox_file_put_back_under_the_same_name` — POST `share.series.episodes.check` on an Episode with `missing_since` set; `list_folder` answers the stored `path_lower` with a new id; `content['file_id']` rewritten, `missing_since` null, flash `series.episode_check.clear`; no call beyond the container check and that listing (`D-021`).
28. `test_replacing_the_dropbox_folder_invites_everyone_again_and_takes_them_off_the_old_one` — `share.series.container.store` with a second folder; every Access has a `pending` row on the new container, which the next ensure leaves `awaiting_acceptance`; the revoke pass sends `remove_folder_member` with the old `shared_folder_id` from each grant's `external_container_id`; a Dropbox Episode whose file stayed in the old folder has `missing_since` set on the page the creator lands on; no `unshare_folder` reaches the fake.
29. `test_removing_the_dropbox_folder_takes_off_only_the_people_qori_added` — before the delete, the Series page carries `containerImpact.dropbox` whose `copy.replace.note` and `copy.remove.note` are the two `series.container.dropbox.change.*` lines; after `share.series.container.destroy`, the sweep sends `remove_folder_member` once per `vendor_ref` and nothing else: no `unshare_folder`, no `files/*` write (`D-021`).

**New: `tests/Feature/Shared/DropboxJourneyTest.php` — 9 cases**

30. `test_a_dropbox_series_lists_what_a_buyer_needs_before_paying` — `BuyerRequirements::for()` on the paid Series with an Active Dropbox container answers the three `accesses.vendor.dropbox.before_buying.common.*` lines in key order, `:basic_storage_gb` filled by key from `config('qori.connections.dropbox.basic_storage_gb')`, and the public Series page carries them beside the buy button (`D-021`).
31. `test_a_new_peer_who_buys_is_invited_in_the_same_request`
32. `test_the_series_page_names_the_dropbox_join_step_and_who_resolves_it` — `vendor` carries `provider` `dropbox`, state `awaiting_acceptance` and the folder `url`, and no Dropbox Episode on the page is openable.
33. `test_open_does_not_send_a_peer_to_dropbox_before_they_have_joined` — redirects to `shared.show` at `#access` with `shared.vendor_notice.redirected` (`D-020`), and offers no other way in: no shared link, no per-file grant, whatever the reason they have not joined (`D-018`).
34. `test_check_again_after_joining_grants_without_waiting_for_the_recheck` — a row `awaiting_acceptance` checked a minute ago, well inside `RECHECK_MINUTES`; `list_folder_members.200.json` shows the account under `users`; POST `shared.access.check` → row `granted`, redirect to `shared.show` at `#access` with `shared.vendor_notice.opened`; one `list_folder_members` call and no `add_folder_member` (`D-021`).
35. `test_open_redirects_to_the_file_once_the_member_list_shows_them`
36. `test_open_falls_back_to_the_folder_when_the_file_is_gone`
37. `test_an_episode_added_after_the_grant_opens_with_no_new_grant_call`
38. `test_revoking_access_removes_the_member`

**New: `tests/Feature/Integrations/Dropbox/DropboxAccountsTest.php` — 8 cases**

39. `test_the_authorize_url_asks_for_offline_access_and_the_four_scopes` — and not `files.content.read`.
40. `test_the_exchange_stores_the_refresh_token_and_the_chosen_tier` — `finaliseConnection()` with the expected `state` and a `code`, `oauth2/token.offline.200.json`: `Connected`; the landing then stores the refresh token and the tier chosen at begin; the token call's `timeout` option was the budget, and a budget above `DropboxStorage::TIMEOUT_SECONDS` was cut to it (`D-034`).
41. `test_a_missing_scope_is_refused_and_nothing_is_connected` — the token fixture's `scope` without `sharing.write`: `REVOKE_URL` called with that access token, `ScopeDeclined`, and the landing's 403 `errors.connections.scope_declined`; no row.
42. `test_dropbox_is_not_refreshed_on_a_schedule`
43. `test_a_peer_signs_in_with_dropbox_and_the_account_id_becomes_the_subject` — `finaliseConfirmation()` with the expected `state` and nonce and a `code`, `oauth2/token.openid.200.json` and `token.openid.claims.json`: `Confirmed`, its subject the claims' `sub`, which equals the `account_id`; no token kept.
44. `test_an_unverified_dropbox_email_is_refused` — the claims with `email_verified` false: `UnverifiedEmail`; nothing written.
45. `test_it_reads_the_connect_landing_in_dropboxs_words` — `finaliseConnection()` given `error=access_denied` answers `Declined`; another `error` word `Failed` with that word as `upstream`; a wrong `state`, with an error or without, `NotFromQori`; the expected `state` and no `code` `Failed` — none of these sends a request (`Http::assertNothingSent()`); then a 400 from the token endpoint (`{"error": "invalid_grant"}`, the OAuth guide's shape, until `T-095` keeps a refused exchange) `Failed` with `upstream` `400`, and a `ConnectionException` `Failed` with `connection`.
46. `test_it_reads_the_sign_in_landing_in_dropboxs_words` — `finaliseConfirmation()` given `error=access_denied` answers `Declined`; a wrong `state` `NotFromQori`; the expected `state` and no `code` `Failed`, none of them calling Dropbox; the claims with another `aud`, or with a `nonce` that is not the expected one, `Failed` with `id_token`.

Total: 46.

**Changed:**

- `tests/Feature/Storage/PlaybackTest.php` — `test_a_dropbox_file_is_fetched_with_the_creators_token` (`:107-128`) and `test_a_dropbox_episode_without_a_connection_fails_cleanly` (`:130-141`) both assert the resolver this task deletes. The first goes; the second becomes the `unsupported_provider` answer the play route now gives a Dropbox Episode.
- `tests/Feature/Share/IntegrationsProvidersTest.php` — `T-044`'s case 16, `test_only_providers_with_a_bound_connector_have_a_section`, asserts the page has `google_drive` and no `dropbox`; it gains the Dropbox section, and asserts each of the three tiers renders its `recommended` line, the three `ESSENTIAL` lines in order and every other limitation line under `more`, all before anything is connected (`D-018`, `D-021`). Wording, not a re-scope.
- `tests/Feature/EnvExampleTest.php` — the two `DROPBOX_*` keys join `.env.example`.

## Acceptance

- [ ] In a clean browser at 400px and desktop widths, a new Peer reads beside
      the buy button that the paid Series needs a Dropbox account, one Join and
      room in their own Dropbox, buys it (Stripe test mode), confirms their
      Dropbox account, is told to press Join, opens the folder in a new tab,
      presses Join once in Dropbox, returns to the Qori tab still on the Series
      page, presses Check again and is let in without waiting, then opens the
      PDF and the video in new tabs on dropbox.com
- [ ] The same walk for the free Series, from the Series link, with the same
      list above the identity prompt
- [ ] Before Join, the Series page says who resolves it and its Dropbox
      Episodes' Open controls are disabled; a saved Open link lands back on the
      Series page at the notice with the redirect line and never on Dropbox;
      after Join, nothing more is asked
- [ ] A Peer with less free space than the folder sees the sentence naming
      what they must do, never a dead page and never a claim of access, and is
      offered no other way in — the folder is the only path (`D-018`)
- [ ] The video Episode plays for that Peer on dropbox.com and stops where the
      connected tier's line says it stops — the release check `D-018` asks
      for, because a limitation is only honest on screen once somebody has
      watched it happen
- [ ] Running the grant a second time for the same Peer changes nothing and
      records no error; a Peer whose grant was already `granted` is re-checked
      rather than trusted, and one Dropbox has removed is added again
- [ ] After the creator adds a file to the folder and replaces another with a
      same-named upload, the same Peer opens both with nothing happening on
      either side; a file deleted and uploaded again to the same place is found
      again by its path, and Check now clears the `stale` line at once if it
      appeared in between; one uploaded under a new name keeps the `stale`
      line until it is picked again
- [ ] A refusal Dropbox is responsible for (a team account left at "Members
      only") is `needs_creator` with its reason on the Integrations page, and
      once the admin allows outside sharing Try again now invites the waiting
      Peer; the invitation cap is `pending`, the Peer's sentence names when
      Qori tries next, and the sweep invites them the next day
- [ ] An asynchronous share finishes without anyone waiting on it, and the
      Series page says so while it runs
- [ ] Revoking the Peer's access removes them from the folder in Dropbox
- [ ] Replacing the folder, and then removing it, each opens
      `ContainerChangeDialog` first with the Peer count, the Dropbox Episodes
      and the Dropbox line; afterwards Dropbox shows the people Qori added taken
      off the old folder, the files untouched and the folder still shared, and
      after the replace each Peer is asked to Join the new folder
- [ ] The tier dropdown shows, for each tier and on screen before the
      connection is made, what Qori recommends, its three essential
      limitations, and everything else in one collapsed disclosure, and every
      sentence comes from lang
- [ ] `docs/flows/vendor-access.md`, `storage.md`, the tinker recipe and
      `docs/project-plan.md` §8 describe what was built, and no live document
      still says Dropbox is the BYO provider because its links expire
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **`D-058`, 23 September 2026: Dropbox grants per file, and this draft is
  re-drafted on per-file grants**, as `T-094` was after `D-036`. What below
  rests on a shared folder each Peer joins — the Join panel, the storage copy,
  the folder picker, the container states and `series.container.dropbox.*` —
  is superseded. `T-095`'s report (`reports/T-095-2026-09-23-claude.md`) is
  what the re-draft rests on, and names what it still has to observe before it
  is ready: `remove_file_member_2`, `list_file_members` paged, whether a
  file's viewers can see each other, a team admin's outside-sharing policy
  against a file grant, and the invite cap for file invites. The first three
  are one probe on the accounts `T-095` left — anyone's.
- ~~`T-095` rows 1 and 2: whether a Basic creator, and a Plus creator, may add a
  read-only member at all — still the spike's to observe. **What its answer
  changes is settled (`D-018`, 17 September 2026):** no tier is dropped. A
  refusal is a vendor capability, so the tier entry says Dropbox needs a paid
  plan to share a folder this way and the creator upgrades or picks another
  provider. `insufficient_plan` on Plus as well would mean the folder grant is
  a team-plan feature, which is worth the stream owner knowing about the order,
  but it removes no tier from the dropdown either.~~ **Answered 23 September
  2026 (`T-095` step 0):** a free Basic creator adds a viewer on a folder and
  on a file, so no tier needs a refusal line. Plus was not observed; the owner
  judged it not applicable once Basic could (`D-058`).
- ~~`T-095` row 5: whether an invitee who has not joined can open the folder and
  a file through `preview_url`. If they can, `granted` moves to the 200 and the
  Join and storage copy goes — the spike's.~~ **Answered 23 September 2026
  (`T-095` step 18b):** yes, the whole list, with Download and Copy to
  Dropbox, before joining. Moot under `D-058`: a file grant has no Join.
- ~~What a Peer without enough free space gets: the supported case restricted
  and stated on the tier (this draft), a view-only folder link, per-file grants
  (a change to `T-091`'s grant model) or neither — the owner's.~~
  **Answered 17 September 2026 (`D-018`):** no fallback is built. The tier copy
  states before the creator connects that a shared folder costs each person
  their own Dropbox space and that somebody who has run out cannot join, and
  `accesses.vendor.dropbox.join.space` tells that Peer to free space and press
  Join again. Qori neither switches to a view-only link nor to per-file grants;
  both are recorded under Notes as considered and not taken.
- ~~`T-095` row 21: what `list_folder_members` shows before Join, after Join and
  after removal, and whether a creator token can tell a joined member from an
  invited one at all. If it cannot, `granted` has no evidence behind it and
  this task needs another rule — the spike's.~~ **Answered 23 September 2026
  (`T-095` step 18a):** it cannot. A Peer with a Dropbox account is under
  `users` from the grant, before joining. Under `D-058` the evidence is the
  file grant's own `success: viewer`.
- ~~`T-095` row 15: the URL shape a member opens a file at, and whether
  `sharing/get_file_metadata` gives a usable `preview_url` for a file inside a
  shared folder — the spike's.~~ **Answered 23 September 2026 (`T-095` steps
  9 and 13):** `get_file_metadata`'s `preview_url`,
  `https://www.dropbox.com/scl/fi/<key>/<name>?dl=0`, is the same for creator
  and Peer and opened the file directly for the Peer, for a file granted on its
  own and for one in a joined folder. Signed out it asks for sign-in and shows
  the file's name.
- ~~`sharing/share_folder` called again on a folder that is already shared: does
  it answer `complete` with the existing `shared_folder_id`, or an error?
  `T-095` step 4 shares each folder once and never repeats the call — the
  spike's, one extra call.~~ **Answered 23 September 2026 (`T-095`):** 409
  `bad_path/already_shared`, carrying the folder's whole metadata with its
  `shared_folder_id`. Moot under `D-058`, which shares no folder.
- Whether Dropbox's authorize endpoint accepts `code_challenge` and
  `code_challenge_method`. No digest records it and `T-095` step 1 builds the
  URL without them, so `supportsPkce()` is provisional. On the same first
  round trip: what a landing carries when the owner or a Peer declines, which
  the `Declined` arms read as `access_denied`, the OAuth 2.0 word, and whether
  the id token echoes the nonce `DropboxSignIn` sends — anyone's. **Partly
  answered 23 September 2026 (`T-095` step 17):** the id token carries no
  `nonce` claim, though one was sent. PKCE and a declined landing were not
  observed.
- Qori's own folder list against the Dropbox Chooser in folder mode, which this
  draft did not take and the brief named. The Chooser has no fixture and picks
  from whichever account the browser holds — the owner's, if they want it back.
- Whether a `rate_limit` grant should reach the creator. It is `pending`, and
  `T-091` shows only `needs_creator` rows on the Integrations page, so a
  creator whose sharing Dropbox paused learns nothing — the owner's, with
  `T-091`.
- Owner-only browsing, which also stops an admin adding a Dropbox Episode
  because the file picker reads the same route — the owner's, with `T-094`'s
  identical question.
- `SeriesContainerStatus::Sharing`, `ContainerCheck::$externalId` and
  `$preparing`, `ItemCheck::$externalId` and
  `GrantResult::ERROR_CONTAINER_PREPARING` are additions to `T-091`'s data
  model made here; confirm them there rather than leaving two tasks
  disagreeing — `T-091`'s owner's.
- ~~Whether this task should carry `depends: T-094` for the container surfaces it
  edits, or keep the stream's order as the only guarantee — the stream
  owner's. Check now on a `stale` Dropbox Episode (test 27) also needs
  `share.series.episodes.check` and its container arm, built by `T-094`, and
  the daily flag needs `T-094`'s `checkItems()`; the same answer covers both.~~
  Answered 17 September 2026: depends on `T-094`, which builds the item check
  and Check now (`D-021`). `VendorAccessService::checkEpisode()`, which test 28's
  after-replace flag also needs, is `T-091`'s and already a dependency.
- Whether the OAuth connector, the Peer sign-in and the grant connector are one
  task or three; a ready `L` names its split — the owner's.
- ~~Whether Dropbox video is offered on Basic at all, given its streaming
  ceiling, and whether representative long-video playback becomes a release
  check as the developer review asks — the owner's, with `T-095` row 19.~~
  **Answered 17 September 2026 (`D-018`):** video and audio are offered on
  every tier, with the tier's streaming ceiling stated before the creator
  connects and its `recommended` line naming a paid Dropbox plan for anything
  longer. The playback walk stays a release check — the Acceptance box above —
  because a limitation is only honest on screen once somebody has watched it
  happen; `T-095` row 19 still observes where playback stops.
- ~~Where a Peer whose grant is not `granted` lands, and in which file that
  sentence lives: `T-089` sends them back to `shared.show` and keeps Peer copy
  in `lang/en/accesses.php`, `T-091` renders `shared/OpenBlocked` and keeps it
  in `lang/en/shared.php`. This draft follows `T-089` — the route's owner, and
  the only file of the two that exists — and adds no page; settle it so one
  Dropbox Join sentence has one home — anyone's, with `T-089` and `T-091`.~~
  **Answered 17 September 2026 (`D-020`):** there is no `shared/OpenBlocked`.
  `T-089`'s Open redirects a blocked link to `shared.show` at `#access` with
  `shared.vendor_notice.redirected`, and `T-091` disables Open on the Series
  page while a grant is not `granted`. The generic state sentences are
  `T-091`'s `shared.vendor_notice.reasons.*` in `lang/en/shared.php`; the
  Dropbox Join panel is this task's `accesses.vendor.dropbox.join.*`, rendered
  in that notice in place of the `awaiting_acceptance` sentence, with
  `T-091`'s Check again after it. One sentence, one home, one page.
- ~~Whether `T-091`'s `ContainerChangeDialog` takes a provider's own line, as
  this draft assumes for `series.container.dropbox.change.*`, or those
  Dropbox facts — every Peer joins again after a replace, and the folder
  stays shared — move into `T-091`'s `series.container_change.*` per provider.
  Until it is settled the Files table carries a `note` prop as this task's
  edit to the dialog — `T-091`'s owner's.~~ **Settled 17 September 2026
  (`D-021`):** `T-091`'s `containerImpact` entry carries each action's `note`
  from `series.container.<provider>.change.<action>` when the key exists, and
  the dialog renders it; this task writes the two lines and edits neither.
- ~~How `BuyerRequirements` receives a provider's numbers: Dropbox's
  `before_buying.common.space` interpolates `:gigabytes` from
  `qori.connections.dropbox.basic_storage_gb`, the figure `ProviderSections`
  already passes to `limits.common.storage`; whether the two share one source
  of replacements — anyone's, with `T-044` and `T-092`.~~ **Settled
  17 September 2026 (`D-021`):** through this task's arm of `T-092`'s
  `BuyerRequirements::factsFor()`, reading the same config key
  `ProviderSections` reads, so the number has one source in `config/qori.php`.
  **Superseded 19 September 2026:** `T-092` removed `factsFor()`;
  `BuyerRequirements` passes the provider's config entries by key, so the line
  names `:basic_storage_gb` and this task edits nothing in
  `app/Support/BuyerRequirements.php`.
- How `ProviderSections` fills the numbers in this task's `limits.*` lines.
  `BuyerRequirements` now passes a provider's config entries under their own
  keys (`T-092`), so a before-buying line names the key; the `limits.*` lines
  here still name `:gigabytes`, `:minutes`, `:hours`, `:terabytes`,
  `:downloads`, `:people` and `:top`, and `limits.common.storage` and
  `limits.dropbox_basic.bandwidth` use `:gigabytes` for two different keys.
  If `T-044`'s `limitsFor()` fills by key too, as its own `:gigabytes` for
  `free_storage_gb` also has to settle, each line renames its placeholder to
  its key — anyone's, with `T-044`.
- Whether Basic's three essential lines should give way to the
  one-folder-per-Series rule, as Paid's and Team's include it. This draft keeps
  the plan refusal and the video ceiling above it, because the picker repeats
  the folder rule in full and nothing else repeats the playback limit before
  connecting — anyone's, with `T-044`'s provisional `MAX_ESSENTIAL`.
- **From the storage review's rate-limit table (20 September 2026):** Dropbox's
  performance guide (`V4`) publishes no rate number, holds the limit against
  the authorisation rather than the call, and counts the throttled call as
  well — so a 429 stops the connection, not the row that met it. The failure
  table above makes a `429` `pending` for that one grant and sets no
  `next_attempt_at`, so `T-091`'s sweep moves on to the next Peer on the same
  token and earns another; `rate_limit` already pauses everything for
  `RATE_LIMIT_HOURS`, and the 429 arm wants the same shape, keyed on the
  connection and taking its wait from `Retry-After` — anyone's, with `T-091`'s
  sweep.
- **From the storage review, F11 and its evidence table (20 September 2026):**
  `sharing/list_folder_members` is read once here with no cursor while
  `granted` means the Peer appears under `users`, so a folder whose member list
  runs past one page reports everybody beyond it as
  `GrantResult::ERROR_PERMISSION_GONE` and adds them again on the next pass.
  Revoke drops the `async_job_id` on the reasoning that a second call is
  cheaper than a column, and nobody has seen that a repeat converges rather
  than starting a fresh job each time. Both, with the `Sharing` state's
  `check_share_job_status`, are documented and not observed — `T-095`'s to
  answer, at rows 14 and 21 and in a pagination step it does not yet have.
- **From the storage review, F10 (20 September 2026):** `T-091`'s consumers
  still read a container — Try again now selects Accesses with one, its
  creator list loads `container.series`, and the Peer notice takes the provider
  and URL from one — which is the shape Dropbox needs and the reason the shared
  service must not be reshaped around Drive's per-file grants before `T-095`
  has said what Dropbox's unit is. Nothing here follows `D-036` onto files
  because Drive did; the queries and tests that read a container are settled
  with `T-091` before either task freezes — anyone's, with `T-091`.

## Inherited from T-152, 20 September 2026

`lang/en/connections.php` has no `providers.dropbox.name`, so
`errors.series.provider_not_connected`'s `:provider` interpolates the literal
key. It is unreachable today — nothing binds a Dropbox connector, so
`ConnectionService::connectorFor()` is null and the final
`provider_not_available` fires instead — and it becomes reachable the moment
this task binds one. Add the name key in the same change as the connector.

## Re-scope log

None.

## Notes

Two alternatives for a Peer with too little Dropbox space were considered and
not taken (`D-018`, 17 September 2026): a view-only folder link, which puts
content somewhere Qori cannot withdraw it from and quietly weakens every
Peer's access to serve one; and per-file grants instead of a folder, which
rewrites `T-091`'s grant model for one vendor's quota rule and loses the
currency that granting on a container buys. The limit is stated before the
creator connects instead.

The brief for this draft listed `files.content.read` among the scopes; the
research is explicit that only `get_temporary_link` needs it and that this task
deletes that call, and `T-095`'s final walkthrough (step 18) runs without it,
so it is not requested. The brief also named the Dropbox Chooser, which the
decision above replaces with Qori's own list.

`DesignReviewSeeder.php:355` and `:399` give Dropbox Episodes
`['url' => 'https://www.dropbox.com/s/…']`, a key `DropboxStorage::linkFor()`
has never read — it reads `content['path']` (`:40`). Neither shape survives
this task, and both are rewritten to the new content keys. No data migration is
written: the only Dropbox Episodes anywhere are that seeder's and the tests'.

`CLAUDE.md` still says integrations expose `name()` and are bound in
`AppServiceProvider`; the code says `provider()` (`ResolvesMedia.php:29`) and
`IntegrationServiceProvider` (`:24-40`), and this draft follows the code.

An earlier version of this draft listed `app/Support/MediaLifetime.php` as an
edit, on the reading that it capped a Dropbox ticket. It does not: nothing in
that class mentions Dropbox, and the 240-minute cap is written inside
`DropboxStorage::linkFor()` (`:62-70`), so it leaves with the method and
`MediaLifetime` and its test are untouched.

Removing `DropboxStorage` from `media-providers` leaves the JSON play route
answering `errors.playback.unsupported_provider`
(`app/Services/PlaybackTicketService.php:85-89`) for a Dropbox Episode. Nothing
links to it after `T-089` — `opensAs()` answers `tab` for Dropbox — and `T-090`
is expected to delete the route with the Vimeo embed; until then that is a
route with one unreachable branch, not a dead page a Peer can reach.

`release-prerequisites.md:20` already carries Dropbox production approval as an
owner prerequisite. A development app is capped at 500 linked users and frozen
for new ones two weeks after its 50th
(https://www.dropbox.com/developers/reference/developer-guide), and every Peer
who signs in with Dropbox under `T-092` probably counts, so the cap is reached
by Peers rather than by creators. That line is not edited here; the report
names what `T-095` found on the console.

**23 September 2026.** `T-095` finished: its report is
`reports/T-095-2026-09-23-claude.md`, and `D-058` moves Dropbox to per-file
grants, on which this draft is re-drafted.
