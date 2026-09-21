---
id: T-098
title: OneDrive Episodes from a folder shared with each Peer
stream: storage
status: draft
owner: unassigned
estimate: L
depends: T-044, T-091, T-092, T-094, T-097, T-152
blocks: none
---

# T-098 — OneDrive Episodes from a folder shared with each Peer

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016`, the owner's BYO blueprint and the developer review of the same day.
> Amended on 17 September 2026 from `D-020` and `D-021`, after a designer's
> review of the storage drafts: the invitation step lives in the Series page's
> notice with Check again beside it, a flagged file has Check now, a folder
> change shows its impact first, each tier names its essential lines, and a
> buyer sees what OneDrive needs from them before paying. Amended on
> 19 September 2026 from that day's cross-draft decisions: `grant()` takes
> `T-091`'s `App\Data\GrantIdentity`, a permission the drive no longer holds
> is `GrantResult::ERROR_PERMISSION_GONE`, `ItemCheck`'s `name`, `mimeType`
> and `url` are `T-091`'s, the Graph client moves out of
> `app/Integrations/Concerns` into `app/Integrations/Microsoft/GraphClient`
> (`D-022`), it keeps its own timeout and every `$timeoutSeconds` is a budget
> that may only shorten it (`D-034`), the grant lock is `T-091`'s through
> `T-044`'s `AdvisoryLock`, the Microsoft tests sit under
> `tests/Feature/Integrations/Microsoft/`, `MicrosoftAccounts` and
> `MicrosoftSignIn` read their landings in Microsoft's words and answer
> `T-044`'s `ConnectionLanding` and `T-092`'s `IdentityLanding`, and
> `EpisodeProvider::OneDrive` takes `T-044`'s `isAccountBound()`, true.

## Why

Nothing in the code can hold a OneDrive Episode. `ConnectionProvider` names
Dropbox, Vimeo, Zoom and Teams (`app/Enums/ConnectionProvider.php:12-21`),
`EpisodeProvider` five cases with no Microsoft one
(`app/Enums/EpisodeProvider.php:14-51`), `EpisodeType::allowedProviders()`
offers Dropbox for every file, video and audio Episode
(`app/Enums/EpisodeType.php:29-37`), and the only trace of the vendor anywhere
under `app/` is the comment at `app/Providers/IntegrationServiceProvider.php:32-34`
saying OneDrive is "a class and a line here". Nothing confirms a Peer's
Microsoft account either: `ConfirmsPeerIdentity` names Google's class and
leaves the Microsoft one to this task (`T-092`, Code).

Afterwards a creator on any of the three tiers `T-097` walked connects OneDrive
from the Integrations page (`T-044`), picks one dedicated folder per Series and
the files inside it, and every Peer with access is invited on that folder
through `T-091`'s ensure step, silently, with the creator's own token. Open
(`T-089`) sends the Peer to the item on Microsoft's site as the account they
confirmed (`T-092`), and a file the creator uploads or replaces in the folder is
expected to reach them with no further call — `T-097` Q3 and Q5 are what turn
that into an observation. A file _moved_ in reaches them after the folder is
shared again, which Microsoft says is needed and which Qori does on its own
([Share OneDrive files and folders](https://support.microsoft.com/en-us/office/share-onedrive-files-and-folders-9fcc2f7d-de0c-4cec-93b0-a82024800c07)).
Every tier ships (`D-018`): free OneDrive and Microsoft 365 Basic, Personal and
Family, and work or school. `T-097` still walks each one before this task is
written, because a limitation is only honest on screen once somebody has
watched it happen.

## Decisions taken to make this specifiable

**OneDrive is one connection with three tiers, and every one of them ships**
(`D-018`, 17 September 2026). `onedrive_free` (free OneDrive or Microsoft
365 Basic), `onedrive_personal` (Microsoft 365 Personal or Family) and
`onedrive_work`. Free and paid personal are split because their terms differ —
the Services Agreement §14.h.i makes Basic non-commercial
(<https://www.microsoft.com/en-us/servicesagreement>) while the Family and
Personal supplement lifts that restriction for a subscription
(<https://www.microsoft.com/en-us/useterms/microsoft-365-family-and-personal-english>)
— and a tier is what the limitation copy hangs on. Nothing gates them:
`ProviderTier::forProvider()` returns all three, `BeginConnectionRequest`'s
`Rule::in` accepts all three, and Basic's non-commercial clause is a sentence
in that tier's copy for the creator to weigh before connecting — never a
refusal, and never a validation rule. The platform a creator brings, and its
rules, are the creator's own.

**Each tier carries a recommendation as well as its limitations** (`D-018`).
Stating what a tier cannot do without saying what to do about it is the shrug
the owner ruled out, so each of the three gets a
`connections.providers.onedrive.tiers.{tier}.recommended` sentence — what that
tier is good for, and what to choose instead when it is the wrong fit — beside
the `limits.*` lines that say what it cannot do. `T-044`'s `ProviderSection.vue`
renders, for the chosen tier and all above Connect, the recommendation, then the
tier's essential lines, then every other line in one collapsed disclosure
(`D-021`), so this task writes the sentences and OneDrive's entry in
`ProviderSections::ESSENTIAL`, and nothing else.

**Each tier's essential lines are what a Peer needs, what stops sharing
outright, and the one-folder rule** (`D-021`). Free: `onedrive_free.accounts`
and `common.folder`. Personal or Family: `onedrive_personal.accounts` and
`common.folder`. Work or school: `onedrive_work.guests`, `onedrive_work.admin`
and `common.folder`, three being `ProviderSections::MAX_ESSENTIAL`. The two
personal tiers stop at two because nothing on them refuses a share outright — the daily
limit delays people, and Basic's non-commercial clause binds the creator rather
than the share — and the free tier's `recommended` sentence already names both
charging and a rush, so `daily` and `terms` sit in the disclosure; on the work
tier the admin line is the one that stops sharing, and `restricted`, `expiry`,
`sign_in`, `employer`, `guest_of` and `daily` are its details and edge cases.

**A work tenant that refuses guests is a grant that needs the creator, never a
tier Qori withholds** (`D-018`). Qori cannot read a tenant's settings before it
shares, and an organisation that has to be asked is an ordinary outcome rather
than a reason to keep the tier off the dropdown. The `onedrive_work` copy says
before connecting what the administrator has to allow — sharing with new
guests, and this creator inviting them — and a refusal at grant time is
`needs_creator` with `ERROR_GUESTS_REFUSED`, whose reason on the Integrations
page names those same two settings, so the creator knows what to ask for rather
than only that something failed.

**The creator picks from Qori's own Graph listing, not the v8 File Picker**
(provisional — see below). The picker runs on SharePoint-resource tokens and
needs `MyFiles.Read` or Graph `Files.Read` on work accounts and
`OneDrive.ReadWrite` on personal ones, a second resource beyond the scope the
grant needs
([File pickers](https://learn.microsoft.com/en-us/onedrive/developer/controls/file-pickers/?view=odsp-graph-online)),
and `D-016` asks for the narrowest scope that allows the rest. `T-097` captures
no picker response and excludes it by name (its Out), so a picker could not be
specified from an observed payload anyway, while its `drive-me.json` and
`children-folder.json` are exactly the listing this uses. The brief for this
draft named the v8 picker; this is the one place the draft departs from it, and
the bullet below lets the owner put it back — the ids are verified against
Graph either way, so the choice changes the browse control and nothing else.

**The container is a dedicated folder, never the drive root and never the
Personal Vault.** Permissions cannot be created on the root of a personal drive
and Vault items cannot be shared
([invite](https://learn.microsoft.com/en-us/graph/api/driveitem-invite?view=graph-rest-1.0);
[Unable to share OneDrive files](https://support.microsoft.com/en-us/office/unable-to-share-onedrive-files-18755580-24f3-408d-afda-bd8d0f7ed5a2)),
so both are refused at the pick with a sentence rather than at the grant with a
vendor error. One folder per Series, never shared between Series, is `T-091`'s
rule, settled by `D-025`. `limits.common.folder` says it before
connecting, and `series.container.onedrive.explain` says again that everyone
with access can open everything inside the folder, Episodes or not, above
`OneDriveBrowser` every time it opens in folder mode — the first pick, every
change and a re-pick — because that is where the folder is chosen (`D-021`).

**`series_containers.external_id` is `{driveId}!{itemId}`, and the Episode
stores both ids as well.** A drive item id is unique only within its drive
([driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0)),
so the drive travels with the item; `OneDrive::split()` is the one place the
two are separated, and `episodes.content` keeps `drive_id` and `item_id` beside
`name` and `web_url` so Open needs no call.

**`grant()` lists the folder's permissions before it invites.** It makes the
call idempotent whatever `T-097` Q6 finds about a repeat invite, and the same
read is what shows a link-type permission covering several people — the case
the developer review asks to inspect before removal is built. A `GET` is not a
sharing call, so it does not spend the sharing budget a work tenant is held to,
which the research records as 300 sharing calls per five minutes per app per
tenant and Microsoft's throttling guidance describes without that figure
([throttling](https://learn.microsoft.com/en-us/sharepoint/dev/general-development/how-to-avoid-getting-throttled-or-blocked-in-sharepoint-online));
a 429 is handled by its `Retry-After` either way. Grants on one folder still
run one at a time under `T-091`'s container lock, which it takes through
`T-044`'s `AdvisoryLock::run()`.

**The invite body is exactly four keys: `recipients`, `roles: ["read"]`,
`requireSignIn: true`, `sendInvitation: false`.** `requireSignIn` and
`sendInvitation` cannot both be false
([invite](https://learn.microsoft.com/en-us/graph/api/driveitem-invite?view=graph-rest-1.0)),
and `T-097` step 3 captures that refusal as `invite-400-both-false.json`.
`retainInheritedPermissions` is _reported_ to answer 404 rather than documented
to, so it is never sent and nothing here rests on it. One recipient per call,
so a 207 partial success cannot mix two Peers' answers into one row.

**A grant is `granted` only when `T-097` Q1 and Q11 say a Peer can open now**
(provisional — see below). Microsoft documents no take-up path with its own
email off: the grantee stays empty "until the invitation is redeemed"
([permission](https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0)).
If Q1 shows the Peer opens after a silent invite, the 200 is `granted` and
`checkGrant()` re-reads the permission on Open and on the sweep's longer
cadence. If it shows a step is left, the 200 is `awaitingAcceptance()`, this
task sends `sendInvitation: true` for that tier, the tier copy says an email
arrives, and the Peer-facing sentence names opening it as the Peer's step —
never "nothing more is needed from you", which `T-091` reserves for `pending`
and `needs_creator` (`D-020`).

**The invitation step sits in `T-091`'s notice on the Series page, with Check
again beside it** (`D-020`, `D-021`). There is no page of its own: on
`awaiting_acceptance` with provider `onedrive`, the notice at `#access` on
`shared.show` shows `accesses.vendor.onedrive.awaiting_acceptance` in place of
`shared.vendor_notice.reasons.awaiting_acceptance`, then
`accesses.vendor.onedrive.open_folder` linking to the container's `url` — the
folder's `webUrl` — in a new tab, so the Qori tab stays on the page that holds
`T-091`'s `shared.vendor_notice.check_again`. Check again is `T-091`'s
`shared.access.check` into `VendorAccessService::checkNow()`, which calls this
task's `checkGrant()` at once instead of after `RECHECK_MINUTES`; a filled
grantee lands the Peer back on the notice with `shared.vendor_notice.opened`,
and an invitation still standing with `shared.vendor_notice.checked` and the
same sentence. This task adds no route. While the row is not `granted`, `T-091`
renders the Series' OneDrive Episodes' Open disabled, and an Open that still
reaches `T-089`'s route — a page rendered before the state changed, a saved
link — is redirected to that notice. Whether opening the folder as the invited
account takes the invitation up, or only the email's own link does, is
`T-097` Q1's; if only the email does, `open_folder` is dropped and the sentence
alone names the email.

**A buyer is told what OneDrive needs from them before paying** (`D-021`).
`T-092`'s `BuyerRequirements::for()` renders
`accesses.vendor.onedrive.before_buying.<tier>.*` for the creator's tier beside
the buy button, and above the identity prompt on a free Series; OneDrive writes
no `common` line, because the account a Peer needs differs by tier. On both
personal tiers that is one line: a personal Microsoft account on the
address the Peer confirms, which most work or school addresses cannot have — the
fact `limits.*.accounts` gives the creator, said now to the person who needs the
account. On the work tier it is three: any address works, with a code Microsoft
emails when there is no account; the Peer joins the creator's organisation as a
guest and meets its sign-in rules; and their own employer may block files from
another organisation. `before_buying.{tier}.invitation` is written, last in
that tier's lines, only for a tier where `T-097` Q1 shows a take-up step. No
line names a wait or says the Series is ready once payment goes through; the
Series page's notice says what is left.

**A permission that covers several people is never deleted for one Peer.**
`revoke()` reads the stored permission's shape — a `link` with
`grantedToIdentitiesV2` holding more than the row's own Peer — and answers
`RevokeResult::failed(ERROR_SHARED_PERMISSION)` with a `Log::warning` and no
vendor call at all, rather than cutting off everybody else. Revocation is best
effort under `D-016`, and `revokeGrants`, which can remove one identity from
such a link, is beta and not for production.

**Moved-in files are repaired by inviting every Peer on the folder again, and
the change is found by listing the folder's children on a cadence.** Retrying
old failures discovers nothing, so detection is a read of its own:
`checkContainer()` returns a `contentsToken` — the children's ids and
`lastModifiedDateTime`, hashed — which `VendorAccessService::repairChangedContainers()`
compares with `series_containers.settings['contents_token']` on the sweep. A
change puts every `granted` row on that container back to `pending` with
`ERROR_FOLDER_CHANGED` and `next_attempt_at` null, and `T-091`'s own retry rule
re-invites each Peer. It costs one call per Peer per change, bounded and
stated. Graph's `delta` call is the alternative if `T-097` shows it reports
moved-in items reliably; the cadence is `config('qori.connections.onedrive.children_check_minutes')`,
provisional 60. If Q4 shows only a per-item invite repairs a moved-in file,
that is a change to `T-091`'s one grant row per (Access, container), recorded
there — never hidden in this connector.

**Every refusal maps to one of `T-091`'s six states.** 429 and 503 are
`pending` with `retryAfterSeconds` from `Retry-After`, as are a timeout, a
transport error and any other 5xx — Qori retries and nobody acts. A tenant
whose sharing level excludes new guests, whose guest-invite setting forbids
invitations, or whose consent was refused, is `needs_creator` with the sentence
naming the setting
([external sharing](https://learn.microsoft.com/en-us/sharepoint/turn-external-sharing-on-or-off);
[collaboration settings](https://learn.microsoft.com/en-us/entra/external-id/external-collaboration-settings-configure)).
A 401 is `needs_creator` with `T-091`'s `ERROR_CONNECTION_UNUSABLE`, with no
second try here: `T-091`'s `VendorAccessService` refreshes the token before
every call and marks the connection for reconnect on this answer, and an
integration never calls a Service. A 404 on the folder is
`needs_creator` with `ERROR_CONTAINER_MISSING`. A personal-account gate —
`accountVerificationRequired`, `hipCheckRequired` — is `needs_creator`; both
codes are reported rather than documented on the invite reference, so the
branch is written against the code string and owes a body from `T-097` step 8.
The daily sharing refusal is `pending` with `next_attempt_at` a day out,
because retrying sooner cannot work and nobody can act; `T-097` Q9 gives the
body and says whether it names a reset. That row is the case `D-020` has in
mind: `T-091`'s `shared.vendor_notice.reasons.pending` names when Qori tries
next rather than "in a moment", and Check again stays hidden until the row is
due. A creator whose admin has changed a refused setting presses `T-091`'s Try
again now on the Integrations page (`share.settings.integrations.retry`,
`D-021`), which runs this task's `grant()` inline for up to `T-091`'s
`MANUAL_RETRY_LIMIT` of the waiting Peers and leaves the rest due for the sweep;
its flash promises nothing, because Qori cannot know when a tenant's change has
applied.

**Open is a 302 to the item's stored `web_url`, with the folder as the
fallback, and `@microsoft.graph.downloadUrl` is never given to a Peer.** That
URL is pre-authenticated, so it carries no sign-in and no grant check for as
long as it lasts
([driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0)),
while `webUrl` is the page Microsoft's own sharing documentation describes a
person opening. This is not a link-expiry scheme — `D-016` leaves forwarding
and airtight revocation out — only a choice of which of two stored URLs a Peer
is sent to. When the item check has set `missing_since`, Open lands in the
folder instead, so the Peer still sees whatever is there — the same shape as
`T-094`'s fallback.

**Check now reaches this task only through `checkItem()`** (`D-021`). The
creator's Check now beside `series.episode.onedrive.stale` posts to
`share.series.episodes.check`, whose `EpisodeCheckController` sends a container
provider's Episode to `T-091`'s `VendorAccessService::checkEpisode()`, which
re-checks the folder and then calls `OneDrive::checkItem()` with the timeout it
is given. The controller, the route and `qori:episodes:check` are `T-094`'s,
with its container arm and `checkItems()` pass, and `T-090` extends them for
video; this task implements `checkItem()` and nothing more. A file moved out and back keeps its item id, so Check now
clears its flag; a file deleted and uploaded again is a new item, so the flag
stays and the `stale` line says to pick it again.

**File and video Episodes may live on OneDrive; audio is provisional.** Video
streams in Microsoft's own player, which is the vendor's own site `D-016` asks
for. No source covers audio and `T-097`'s content set holds `episode.pdf` and
`episode.mp4` only, so `EpisodeType::Audio` gains OneDrive on the spike's word
and not before (see below).

**The Peer's Microsoft sign-in is this task's class.** `T-092` builds the
route, the page and the service and leaves the Microsoft connector here: the
`/common` authority, `scope=openid email`, `prompt=select_account`, the
identity keyed on `oid` + `tid`, and `xms_edov` as the verified-email claim the
app registration opts into
([optional claims](https://learn.microsoft.com/en-us/entra/identity-platform/optional-claims-reference)).
The email claim can be wrong or change, so it is never what authorises. Both
Microsoft classes read their landing in Microsoft's words — the `error` word
and the AADSTS number that opens `error_description`
([error response](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow#error-response))
— and answer in Qori's: `MicrosoftAccounts` a `T-044` `ConnectionLanding`,
`MicrosoftSignIn` a `T-092` `IdentityLanding` (Code).

**Microsoft's limit is `GraphClient`'s, and `$timeoutSeconds` is a budget
that may only shorten it** (`D-034`). `GraphClient` sets its own timeout on its
`Http::` chain, `GraphClient::TIMEOUT_SECONDS` (provisional — see below),
which `MicrosoftAccounts` and `MicrosoftSignIn` use at the sign-in endpoints
too rather than a second number for one vendor, and no retry: a 429 or 503 is `pending` with its `Retry-After`, and `T-091`'s
retry rule takes it. Every method that reaches Graph takes
`int $timeoutSeconds` last as the caller's budget, never a config key of this
integration's own, and waits whichever of the two is shorter; a web request
passes `VendorAccessService::REQUEST_TIMEOUT_SECONDS`, the sweep
`SWEEP_TIMEOUT_SECONDS`. An integration may not import `app/Services`
(`tests/Feature/ArchitectureTest.php:139`), which is why the budget travels.
`T-097` Q12 times an invite against those figures; if it runs longer, the
in-request grant lands `pending` and the sweep is the real path.

**What `T-091`'s three reconciliation triggers mean here.** A Peer confirming
or changing an identity gives a different address: the row goes back to
`pending`, the next ensure invites the new one, and the permission it replaced
is deleted by the revoke pass, best effort. The creator reconnecting the
**same** account is a token swap — the stored drive and item ids still answer,
so rows waiting on a 401 simply succeed. A **different** account is held by
`T-044` for the creator to confirm, on a page naming the Series whose folders
and Episodes will need picking again (`D-021`). On Switch the new account cannot
read those ids, `checkContainer()` answers `exists: false`, and `T-091` marks
the container `repick` and tells the creator (`T-097` step 8 is that read); Qori
no longer holds a token for the old account, so nothing is removed there.
Replacing the container is `T-091`'s `attach()`, unchanged, behind the dialog
below.

**Publisher verification is an owner prerequisite, not code.** Risk-based
step-up consent blocks user consent for an unverified multi-tenant app asking
non-basic permissions (AADSTS90094), so most work-tenant creators would need
admin approval without it
([step-up consent](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-risk-based-step-up-consent);
[publisher verification](https://learn.microsoft.com/en-us/entra/identity-platform/publisher-verification-overview)).
`MicrosoftAccounts` reads AADSTS90094 on the landing as `AdminBlocked`,
which `T-044`'s landing shows as `errors.connections.admin_blocked`; `T-097`
Q10 measures how often it happens and updates `release-prerequisites.md`.

**The creator's container surfaces are `T-094`'s, reused.**
`SeriesContainerController`, `StoreSeriesContainerRequest`, the folder panel on
the creator's Series page and `VendorAccessService::describeItem()` are that
task's, and this task depends on `T-094`, so they are edits here.

**Changing or removing the folder shows its impact first** (`D-021`). With an
Active OneDrive container, choosing a different folder in `OneDriveBrowser` or
pressing `series.container.remove` opens `T-091`'s `ContainerChangeDialog` with
the `containerImpact` prop — the active Accesses on the Series and its OneDrive
Episodes — and the `PUT` or `DELETE` is sent only on confirm. The dialog's
folder copy is `T-091`'s `series.container_change.*`, with OneDrive as
`:vendor`. What it says is true here because `revoke()` builds each old
permission's path from the grant's own `external_container_id`, so the sweep
deletes the Peers' permissions on a folder whose row is already gone, and no
call touches a file. The exception is a link permission covering several
people, which `revoke()` leaves in place (`ERROR_SHARED_PERMISSION`): if
`T-097` Q6 shows invites land that way, "taken off this one" is not true for
OneDrive, and this task adds `series.container.onedrive.change.replace` and
`.remove` saying so, which `T-091`'s `containerImpact` entry carries as the
dialog's note. After a
replace, `T-091` runs `checkEpisode()` on each OneDrive Episode against the new
folder at once, at the point its own spec names, so a file outside it carries
`series.episode.onedrive.stale` on the page the creator lands on. The toasts
are `T-094`'s `series.container.replaced` and `series.container.removed`, the
second no longer saying nothing in the account changed; this task writes no
removal line of its own.

## Preconditions

`T-044` done, so `ProviderTier`, `ConnectsAccounts`, `ConnectionService`, the
provider sections, reconnect, `qori:connections:refresh` and
`lang/en/connections.php` exist; `T-091` done, so `series_containers`,
`vendor_grants`, `GrantsPeerAccess` with `App\Data\GrantIdentity`,
`GrantResult::ERROR_PERMISSION_GONE`, `ItemCheck`'s `name`, `mimeType` and
`url`, `VendorAccessService`, its container lock on `T-044`'s `AdvisoryLock`
and `qori:access:reconcile` exist; `T-092` done, so `IdentityProvider`,
`VendorIdentity`, `ConfirmsPeerIdentity`, the `/u/identities` routes and the
Series-page prompt exist; `T-094` done, so `SeriesContainerController`,
`StoreSeriesContainerRequest`, the folder panel, `describeItem()`,
`checkItems()`, `qori:episodes:check`, `share.series.episodes.check` and the
`missingSince` prop exist; `T-097` done, so `tests/Fixtures/microsoft/` holds
every response named below and its report has answered Q1 to Q13.

**Data this task verifies against:** a clean database for the tests. For the
browser walk, a connected creator on each of the three tiers, with one paid
and one free Series, each holding its own folder with a PDF, an Office document
and an MP4 inside it, plus one file outside the folder to move in.

**Equipment:** the Entra app registration `T-097` used, with this environment's
redirect URIs, `u/connections/microsoft/finalise` and
`u/identities/microsoft/finalise` — each names the vendor, never the service
(`D-033`) — and the `xms_edov` optional claim; `MICROSOFT_CLIENT_ID` and
`MICROSOFT_CLIENT_SECRET` set; Stripe test mode; one Peer on an outlook.com
account and one on a non-Microsoft address, in separate clean browser profiles;
for the work tier, a paid tenant and a Peer from outside it; a phone; a visible
browser at 400px and desktop widths.

**Spike:** `T-097`. Every request shape below is from the Graph page cited
beside it, and every response field named below must appear in the fixture
named beside it, or the test that reads it is not written. Three fixtures may
not exist — `invite-work-207.json`, `invite-429.json` and
`invite-personal-cap.json` are captured only if reached — and the Tests section
says what happens to the cases that need them. No field here is presented as
observed; the fixtures are what turn each into an observation.

## Scope

**In:**

- `ConnectionProvider::OneDrive` and its `vendor()` arm, `microsoft`
  (`D-033`), `EpisodeProvider::OneDrive` with its `connection()` arm and its
  `isAccountBound()` arm, true — a drive item id means nothing without the
  creator's account, so `T-044`'s guard asks for the connection first —
  `EpisodeType::allowedProviders()` for file and video,
  `IdentityProvider::forConnection()`'s Microsoft arm and three `ProviderTier`
  cases, every one of them offered (`D-018`).
- `App\Integrations\Microsoft\MicrosoftAccounts` (`ConnectsAccounts`),
  `OneDrive` (`GrantsPeerAccess`) and `MicrosoftSignIn` (`ConfirmsPeerIdentity`),
  tagged `account-connectors`, `grant-providers` and `identity-providers`.
- The Graph listing route behind the creator's browse control, the container
  pick and the Episode pick from inside the folder, the refusals for the root,
  the Vault and an item outside the folder.
- `contentsToken` on `ContainerCheck` and `repairChangedContainers()` on
  `VendorAccessService`, called from `qori:access:reconcile`.
- The tier limitation and recommendation copy, OneDrive's entry in
  `ProviderSections::ESSENTIAL`, and the `disconnect.in_qori` and
  `account_change.in_qori` lines `T-044`'s Dialog and confirmation page show
  (`D-021`).
- The Peer-facing OneDrive sentences inside `T-091`'s `#access` notice, with the
  new-tab folder link beside its Check again (`D-020`), and the
  `before_buying` lines `T-092` renders (`D-021`).
- `series.container.onedrive.explain` at every folder pick, the folder change
  and removal behind `T-091`'s `ContainerChangeDialog`, and Check now beside
  the `stale` line (`D-021`).
- The Microsoft grant reasons on the Integrations page.
- `docs/flows/vendor-access.md` and `docs/flows/storage.md`.

**Out:**

- The OAuth machinery, the tier dropdown, the essential-and-more layout,
  reconnect and its different-account confirmation, disconnect and its dialog,
  and the token refresh command (`T-044`); the two tables, the ensure step, the
  states, the retry rule, the lock, the sweep, the Integrations page's
  failed-grant and re-pick lists, Check again, Try again now, the disabled Open
  on the Series page, `ContainerChangeDialog` and its copy (`T-091`); the
  identity page, its routes, the Series-page prompt and the before-buying list
  (`T-092`); the Open route and its redirect to the Series page's notice
  (`T-089`, `D-020`); `checkEpisode()` (`T-091`); Check now's controller and
  route, `qori:episodes:check`, its container arm, `checkItems()` and the
  `missingSince` prop (`T-094`).
- Audio Episodes on OneDrive, until the question below is answered.
- SharePoint team sites and shared libraries, which need the admin-only `.All`
  scopes; only the creator's own OneDrive is in.
- `createLink` and `revokeGrants` (both beta), download blocking,
  `expirationDateTime` and invite passwords. Downloads and airtight revocation
  are not concerns (`D-016`).
- Teams recordings moved into the Series folder (`T-101`), and Zoom (`T-099`,
  `T-100`).
- Delayed payments and refunds (`T-102`, `T-103`), which land before any paid
  Series uses this provider; `T-103`'s revoke reaches `revoke()` here through
  `T-091`'s `revokeFor()`. Nothing in this connector can fail a fulfilment or
  undo an Access: every method answers with a `GrantResult` and never throws,
  so a Microsoft refusal is a row `T-091` replays, not a webhook that fails
  after the Access is committed.
- Publisher verification itself, and any per-container cap guard — Microsoft
  publishes 50,000 unique permissions per library item, 5,000 recommended
  ([SharePoint limits](https://learn.microsoft.com/en-us/office365/servicedescriptions/sharepoint-online-service-description/sharepoint-online-limits)),
  far above a Series' Peer count.

## Files

| Path                                                                                                                                          | Change | Notes                                                                                                                                                                                                                  |
| --------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `app/Enums/ConnectionProvider.php` `app/Enums/EpisodeProvider.php` `app/Enums/EpisodeType.php`                                                | edit   | `OneDrive` cases, the `vendor()`, `connection()` and `isAccountBound()` (true, `T-044`'s method) arms, `allowedProviders()` for file and video                                                                         |
| `app/Enums/ProviderTier.php` `app/Enums/IdentityProvider.php`                                                                                 | edit   | `T-044`'s and `T-092`'s enums: three tiers, none of them gated; the Microsoft arm                                                                                                                                      |
| `app/Integrations/Microsoft/MicrosoftAccounts.php` `app/Integrations/Microsoft/OneDrive.php` `app/Integrations/Microsoft/MicrosoftSignIn.php` | new    | The three connectors                                                                                                                                                                                                   |
| `app/Integrations/Microsoft/GraphClient.php`                                                                                                  | new    | `OneDrive`'s one Graph client, by constructor: the bearer, its own timeout, the `Retry-After` read, the error shape; in the vendor's folder, as `T-141`'s `ZoomClient` is (`D-022`)                                    |
| `app/Providers/IntegrationServiceProvider.php`                                                                                                | edit   | Three tags (`:35-39`); the OneDrive comment at `:32-34` goes                                                                                                                                                           |
| `app/Support/ProviderSections.php`                                                                                                            | edit   | `T-044`'s; the `onedrive` entry in `ESSENTIAL` (`D-021`)                                                                                                                                                               |
| `app/Data/ContainerCheck.php`                                                                                                                 | edit   | `T-091`'s; gains `contentsToken`                                                                                                                                                                                       |
| `app/Services/VendorAccessService.php`                                                                                                        | edit   | `T-091`'s; `repairChangedContainers()`                                                                                                                                                                                 |
| `app/Console/Commands/ReconcileAccessCommand.php`                                                                                             | edit   | `T-091`'s; the repair pass per Group                                                                                                                                                                                   |
| `app/Http/Controllers/Share/OneDriveController.php`                                                                                           | new    | `items()`: the creator's folders and their children, owner only                                                                                                                                                        |
| `app/Http/Controllers/Share/SeriesContainerController.php` `app/Http/Requests/Share/StoreSeriesContainerRequest.php`                          | edit   | `T-094`'s; `onedrive` in the provider rule                                                                                                                                                                             |
| `app/Http/Requests/Share/StoreEpisodeRequest.php`                                                                                             | edit   | `onedrive` arm of `content()` (`:184-198`); `drive_id`, `file_name` inputs                                                                                                                                             |
| `app/Http/Controllers/Share/SeriesController.php`                                                                                             | edit   | `container` and `browse` props on `show()` (`:137`); `T-094`'s `missingSince` covers a `onedrive` Episode as given                                                                                                     |
| `routes/share/payments.php`                                                                                                                   | edit   | The listing route beside `share.connections.*`                                                                                                                                                                         |
| `resources/js/pages/share/series/Show.vue`                                                                                                    | edit   | `allowed` (`:198-203`), `providerLabels` (`:290-296`), the folder panel, the two picks; `explain` at every folder pick; change and remove through `T-091`'s `ContainerChangeDialog`; Check now beside the `stale` line |
| `resources/js/components/series/OneDriveBrowser.vue`                                                                                          | new    | The listing control; folder mode and file mode                                                                                                                                                                         |
| `resources/js/pages/shared/Show.vue`                                                                                                          | edit   | The OneDrive sentences and the new-tab folder link inside `T-091`'s `#access` notice, beside its Check again, chosen by that prop's `provider`                                                                         |
| `lang/en/connections.php` `lang/en/series.php` `lang/en/errors.php` `lang/en/accesses.php`                                                    | edit   | Copy below; the first is `T-044`'s file, the last is the Peer surface's                                                                                                                                                |
| `config/services.php` `config/qori.php` `.env.example`                                                                                        | edit   | The `microsoft` block; the `connections.onedrive` block; two env keys                                                                                                                                                  |
| `database/factories/SeriesContainerFactory.php` `database/factories/VendorIdentityFactory.php`                                                | edit   | `T-091`'s and `T-092`'s; `oneDrive()` and `microsoft()` states                                                                                                                                                         |
| `tests/Feature/Integrations/Microsoft/OneDriveTest.php` `tests/Feature/Series/OneDriveContainerTest.php`                                      | new    | 15 and 15 cases; a vendor's own tests sit in `tests/Feature/Integrations/<Vendor>/`, as `Stripe/ClientTest.php` does                                                                                                   |
| `tests/Feature/Shared/OneDriveJourneyTest.php`                                                                                                | new    | 13 cases                                                                                                                                                                                                               |
| `tests/Feature/Integrations/Microsoft/MicrosoftSignInTest.php` `tests/Feature/Integrations/Microsoft/MicrosoftAccountsTest.php`               | new    | 5 and 6 cases                                                                                                                                                                                                          |
| `docs/flows/vendor-access.md` `docs/flows/storage.md`                                                                                         | edit   | `T-091` creates the first; the OneDrive chain and the providers table (`:51-57`)                                                                                                                                       |
| `docs/tinker/connections.md`                                                                                                                  | edit   | `T-044`'s recipe gains the OneDrive walk                                                                                                                                                                               |

Every path above marked `edit` that does not exist today is created by another
task — `T-044`, `T-091`, `T-092` or `T-094`, each a dependency — and the Notes
column says which.
`docs/flows/vendor-access.md` and `docs/flows/storage.md` are the flow docs for
the `app/Http`, `app/Services`, `app/Console` and `routes/` rows.
`qori:reachability` sees the listing route through its name in `Show.vue`.

## Database

None. `series_containers` and `vendor_grants` are `T-091`'s. This task writes
`series_containers.external_id` (`{driveId}!{itemId}`), `url` (the folder's
`webUrl`) and `settings` (`name`, `contents_token`, `contents_checked_at`), and
`vendor_grants.vendor_ref` (the permission `id`). `episodes.content` (jsonb,
`database/migrations/2026_09_08_000000_create_qori_schema.php:113`) holds, for
`onedrive`: `drive_id`, `item_id`, `name`, `web_url`, `checked_at`,
`missing_since` (null while the file is fine). `connections.settings['tier']`
takes one of the three tier values, and `connections` is already unique on
`(group_id, provider)` (`:193`), so one OneDrive account per Group.

## Code

```php
namespace App\Enums;

// ConnectionProvider
case OneDrive = 'onedrive';
// ConnectionProvider::vendor(): self::OneDrive => 'microsoft',   // T-044's method; the landing is u/connections/microsoft/finalise (D-033)
// EpisodeProvider
case OneDrive = 'onedrive';
// EpisodeProvider::connection(): self::OneDrive => ConnectionProvider::OneDrive,
// EpisodeProvider::isAccountBound(): self::OneDrive => true,   // T-044's method: the item id means nothing without the account
// IdentityProvider::forConnection(): ConnectionProvider::OneDrive => self::Microsoft,

// EpisodeType::allowedProviders()
self::File  => [EpisodeProvider::CloudflareR2, EpisodeProvider::Dropbox, EpisodeProvider::OneDrive],
self::Video => [EpisodeProvider::Vimeo, EpisodeProvider::Dropbox, EpisodeProvider::OneDrive],
self::Audio => [EpisodeProvider::Dropbox],   // unchanged until the MP3 question below is answered

// ProviderTier — T-044's enum
case OneDriveFree = 'onedrive_free';           // free OneDrive or Microsoft 365 Basic
case OneDrivePersonal = 'onedrive_personal';   // Microsoft 365 Personal or Family
case OneDriveWork = 'onedrive_work';           // OneDrive for work or school
/** forProvider() returns all three for OneDrive: no tier is gated, each is offered with its limitations (D-018). */
```

```php
// App\Support\ProviderSections — T-044's class; OneDrive's entry in ESSENTIAL (D-021).
// Keys are relative to connections.providers.onedrive.limits.; order is render order; every other limits line is `more`.
'onedrive' => [
    'onedrive_free' => ['onedrive_free.accounts', 'common.folder'],
    'onedrive_personal' => ['onedrive_personal.accounts', 'common.folder'],
    'onedrive_work' => ['onedrive_work.guests', 'onedrive_work.admin', 'common.folder'],
],
```

```php
namespace App\Integrations\Microsoft;

/**
 * A creator's own OneDrive (D-016): one folder per Series, one read permission per Peer. Every $timeoutSeconds is
 * the caller's budget — T-091's REQUEST_TIMEOUT_SECONDS or SWEEP_TIMEOUT_SECONDS — which GraphClient may only
 * shorten: each call waits the shorter of GraphClient::TIMEOUT_SECONDS and the budget (D-034).
 */
class OneDrive implements GrantsPeerAccess
{
    public const BASE = 'https://graph.microsoft.com/v1.0';
    public const FOLDER_FACET = 'folder';
    /** Minutes Microsoft's emailed one-time code lasts for a work-tenant guest; :minutes in the copy below. Provisional until T-097 Q8 sees one. */
    public const GUEST_CODE_MINUTES = 30;
    /** driveItem select mask for the folder, a picked file and the item check. */
    public const ITEM_FIELDS = 'id,name,size,webUrl,folder,file,parentReference,lastModifiedDateTime';
    public const ERROR_FOLDER_CHANGED = 'folder_changed';        // pending; the re-invite that repairs a moved-in file
    public const ERROR_GUESTS_REFUSED = 'guests_refused';        // needs_creator; sharing level or guest-invite setting
    public const ERROR_ACCOUNT_GATED = 'account_gated';          // needs_creator; accountVerificationRequired, hipCheckRequired
    public const ERROR_DAILY_LIMIT = 'daily_limit';              // pending, a day out
    public const ERROR_SHARED_PERMISSION = 'shared_permission';  // revoke only; never deleted
    public const ERROR_NOT_SHAREABLE = 'not_shareable';          // the drive root or a Personal Vault item
    // A permission the drive no longer holds is T-091's GrantResult::ERROR_PERMISSION_GONE, shared by every provider.

    public function __construct(private GraphClient $graph) {}

    public function provider(): ConnectionProvider;   // ConnectionProvider::OneDrive
    /** GET the folder and its children: exists when 200 and the folder facet is present; url is webUrl; contentsToken is sha1 of each child's id and lastModifiedDateTime. */
    public function checkContainer(Connection $connection, string $externalId, int $timeoutSeconds): ContainerCheck;
    /** null identity → awaitingIdentity(), no call. Else GET permissions; the address present → granted(id) or awaitingAcceptance(id); absent → POST invite. */
    public function grant(Connection $connection, SeriesContainer $container, ?GrantIdentity $identity, string $email, int $timeoutSeconds): GrantResult;
    /** GET permissions/{vendor_ref}: a filled grantee → granted(id); an invitation still standing → awaitingAcceptance(id); 404 → pending(GrantResult::ERROR_PERMISSION_GONE). */
    public function checkGrant(Connection $connection, VendorGrant $grant, int $timeoutSeconds): GrantResult;
    /** A link permission covering more than this Peer → failed(ERROR_SHARED_PERMISSION), no call. Else DELETE on the drive and item split from the grant's external_container_id, so a replaced or removed folder is still reached; 204 and 404 are both revoked(). */
    public function revoke(Connection $connection, VendorGrant $grant, int $timeoutSeconds): RevokeResult;
    /** content['web_url'], or the container's url when content['missing_since'] is set; no call. accountHint is the confirmed Microsoft address. */
    public function openLink(Connection $connection, Episode $episode, ?VendorGrant $grant, int $timeoutSeconds): VendorLink;
    /** GET the item: exists, insideContainer = parentReference.id is the container's item id, plus T-091's nullable name, mimeType and url (name, file.mimeType, webUrl), which describeItem() reads. The whole of Check now's OneDrive branch (D-021): checkEpisode() calls it with the budget it was given. */
    public function checkItem(Connection $connection, Episode $episode, int $timeoutSeconds): ItemCheck;

    /** @return array{0: string, 1: string} driveId and itemId from "{driveId}!{itemId}". */
    public static function split(string $externalId): array;
    private function invitePayload(string $email, bool $sendInvitation): array;
    private function failure(Response $response): GrantResult;   // the table below, reading GraphClient's retryAfter() and errorCode()
}

/**
 * Microsoft Graph for this folder's classes — what the draft had as a trait in app/Integrations/Concerns, which
 * D-022 retires (ArchitectureTest::test_integrations_keep_no_shared_concerns_folder, tests/Feature/ArchitectureTest.php:45).
 * A class taken by constructor, as T-141's ZoomClient is by ZoomAccounts.
 */
class GraphClient
{
    /**
     * Microsoft's own limit on one call, which a caller's budget may only shorten (D-034): Graph's, and the sign-in
     * endpoints' for MicrosoftAccounts and MicrosoftSignIn, rather than a second number for one vendor. Provisional — see below.
     */
    public const TIMEOUT_SECONDS = 15;

    /** Http::withToken($connection->access_token)->acceptJson()->timeout(min(self::TIMEOUT_SECONDS, $timeoutSeconds)); no retry. */
    public function request(Connection $connection, int $timeoutSeconds): PendingRequest;
    /** Seconds from the Retry-After header of a 429 or 503; null when there is none. */
    public function retryAfter(Response $response): ?int;
    /** Graph's error.code, for failure() and the result's upstream; null when the body carries none. */
    public function errorCode(Response $response): ?string;
}
```

The calls, with the reference page and the `T-097` fixture each test reads:

| Call                                                                        | Reference                                                                                 | Fixture                                                                                                                                                                                      |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET {BASE}/me/drive`                                                       | <https://learn.microsoft.com/en-us/graph/api/drive-get?view=graph-rest-1.0>               | `drive-me.json`                                                                                                                                                                              |
| `GET {BASE}/drives/{driveId}/items/{itemId}/children?$select={ITEM_FIELDS}` | <https://learn.microsoft.com/en-us/graph/api/driveitem-list-children?view=graph-rest-1.0> | `children-folder.json`                                                                                                                                                                       |
| `GET {BASE}/drives/{driveId}/items/{itemId}?$select={ITEM_FIELDS}`          | <https://learn.microsoft.com/en-us/graph/api/driveitem-get?view=graph-rest-1.0>           | `item-other-account.json`; a file inside the folder has no capture of its own, so `checkItem()`'s cases are shaped from one entry of `children-folder.json`, which carries the same fields   |
| `POST {BASE}/drives/{driveId}/items/{itemId}/invite`                        | <https://learn.microsoft.com/en-us/graph/api/driveitem-invite?view=graph-rest-1.0>        | `invite-personal-200.json`, `invite-personal-repeat.json`, `invite-work-200.json`, `invite-work-existing-guests.json`, `invite-work-guest-invites-off.json`, `invite-401-expired-token.json` |
| `GET {BASE}/drives/{driveId}/items/{itemId}/permissions`                    | <https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0>    | `permissions-folder.json`, `permissions-second-folder.json`                                                                                                                                  |
| `GET {BASE}/drives/{driveId}/items/{itemId}/permissions/{permId}`           | <https://learn.microsoft.com/en-us/graph/api/permission-get?view=graph-rest-1.0>          | `permission-get-before-open.json`, `permission-get-after-open.json`, `permission-get-next-day.json`                                                                                          |
| `DELETE {BASE}/drives/{driveId}/items/{itemId}/permissions/{permId}`        | <https://learn.microsoft.com/en-us/graph/api/permission-delete?view=graph-rest-1.0>       | 204, README row only                                                                                                                                                                         |

`failure()`: 429 or 503 → `pending` with `Retry-After`; a `ConnectionException`
→ `pending(GrantResult::ERROR_TIMEOUT)`; any other 5xx →
`pending(GrantResult::ERROR_UNEXPECTED)`; 401 → `needs_creator` with
`GrantResult::ERROR_CONNECTION_UNUSABLE`, with no retry (`T-091` refreshed
first and marks the connection); 404 on the
folder → `needs_creator` with `GrantResult::ERROR_CONTAINER_MISSING`; the
tenant refusals `T-097` Q7 captures → `needs_creator(ERROR_GUESTS_REFUSED)`;
`accountVerificationRequired` and `hipCheckRequired` →
`needs_creator(ERROR_ACCOUNT_GATED)`; the daily-limit body from Q9 →
`pending(ERROR_DAILY_LIMIT, retryAfterSeconds: 86400)`. `upstream` is the
status and Graph's `error.code`, for logs only.

Every outcome this connector can produce, and who the Peer's sentence names:

| Outcome                                                             | State                 | Who resolves it                                       |
| ------------------------------------------------------------------- | --------------------- | ----------------------------------------------------- |
| No confirmed Microsoft identity, no call made                       | `awaiting_identity`   | The Peer, by signing in with Microsoft (`T-092`)      |
| Invite accepted, a take-up step left (only if `T-097` Q1 says so)   | `awaiting_acceptance` | The Peer, by opening Microsoft's invitation           |
| 429, 503, other 5xx, timeout, transport error, `ERROR_DAILY_LIMIT`  | `pending`             | Nobody — Qori retries                                 |
| `ERROR_FOLDER_CHANGED` after a moved-in file                        | `pending`             | Nobody — the next sweep re-invites                    |
| Tenant refusal, account gate, 401 after one refresh, container gone | `needs_creator`       | The creator, from the Integrations page's failed list |
| Grantee filled in, or Q1 says the silent invite is usable access    | `granted`             | Nobody; re-checked on Open and on the sweep's cadence |
| `AccessService::revoke()` or `T-103`, best effort                   | `revoked`             | Nobody                                                |

```php
namespace App\Integrations\Microsoft;

/** Endpoints from https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow. */
class MicrosoftAccounts implements ConnectsAccounts
{
    public const AUTHORIZE_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize';
    public const TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token';
    public const SCOPES = ['Files.ReadWrite', 'offline_access', 'User.Read'];
    /** AADSTS number on a landing whose tenant needs an admin to consent first (step-up consent above). */
    public const ADMIN_CONSENT_REQUIRED = 'AADSTS90094';
    // supportsPkce(): true; refreshesOnSchedule(): true — a refresh token lasts 90 days and is replaced on
    //   every use (https://learn.microsoft.com/en-us/entra/identity-platform/refresh-tokens), so the newest is stored.
    // requiredScopes(): SCOPES less offline_access, whose proof is the refresh_token in the same response; matched as
    //   T-097's token-authorization-code.json spells the granted scope (provisional), and less User.Read if the bullet below drops it.
    // Every call: ->timeout(min(GraphClient::TIMEOUT_SECONDS, $timeoutSeconds)), Microsoft's one limit (D-034), and no retry.
    // finaliseConnection(): T-044's contract, in Connect::finaliseOnboarding()'s order (app/Integrations/Stripe/Connect.php:74-151),
    //   never throwing; $matches = $expectedState !== '' && hash_equals($expectedState, the landing's state):
    //   an error whose state is present and does not match → notFromQori(); an error_description opening with
    //   ADMIN_CONSENT_REQUIRED, whatever the error word → adminBlocked()  [T-097 step 7's consent-w1.txt shows the word];
    //   error=access_denied, the page's word for a person who declined → declined(); any other error word → failed(<the AADSTS
    //   number, else the word>); no error and ! $matches → notFromQori(); no code → failed(); no call on any of these.
    //   POST TOKEN_URL form client_id, client_secret, grant_type=authorization_code, code, redirect_uri, code_verifier
    //   → access_token, refresh_token, expires_in, scope  [token-authorization-code.json]; a ConnectionException →
    //   failed('connection'); a 4xx or 5xx → failed(<status>), logged with Microsoft's error word and AADSTS number, never the body;
    //   a granted scope short of requiredScopes() → scopeDeclined(), the token dropped unstored: the auth-code page documents no
    //   endpoint that revokes one token (provisional); else connected(new ConnectionTokens(...)).
    // refresh(): POST TOKEN_URL form grant_type=refresh_token  [token-refresh.json]; error=invalid_grant → RefreshResult::revoked().
    // identity(): GET {OneDrive::BASE}/me → id, displayName, mail ?? userPrincipalName (User.Read),
    //   https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0. T-097 captures no /me
    //   response, so this owes a me.json from its step 1 — or the scope question below drops the call for
    //   drive-me.json's owner.user, which is captured.
}

class MicrosoftSignIn implements ConfirmsPeerIdentity
{
    public const SCOPES = 'openid email';
    // provider(): IdentityProvider::Microsoft
    // beginConfirmation(): MicrosoftAccounts::AUTHORIZE_URL, the /common authority: response_type=code, scope=SCOPES,
    //   redirect_uri, state, nonce, prompt=select_account, login_hint when given; client_id from config('services.microsoft').
    // finaliseConfirmation(), T-092's contract, in the order GoogleSignIn reads Google's (T-092), with $matches as
    //   MicrosoftAccounts computes it: an error whose state is present and does not match → notFromQori();
    //   error=access_denied → declined(); any other error word → failed(<the AADSTS number, else the word>), a tenant that lets
    //   its members consent to nothing included, since a Peer cannot change that; no error and ! $matches → notFromQori();
    //   no code → failed(); no call on any of these;
    //   POST MicrosoftAccounts::TOKEN_URL form client_id, client_secret, grant_type=authorization_code, code, redirect_uri,
    //     ->timeout(min(GraphClient::TIMEOUT_SECONDS, $timeoutSeconds)), no retry → id_token  [oidc-token-personal.json,
    //     oidc-token-work.json]; no answer → failed('connection'); a 4xx or 5xx → failed(<status>);
    //   the id_token's payload  [oidc-claims-personal.json, oidc-claims-work.json]: aud not the client id, exp past, no email,
    //     or a nonce that is not hash_equals($expectedNonce) → failed('id_token'); xms_edov not true → unverifiedEmail();
    //   else confirmed(new VendorIdentityData(Microsoft, oid, email, tenant: tid)). Every token is discarded; the access_token
    //   is never read. No `use App\Services`.
}
```

```php
// App\Data\ContainerCheck — T-091's class, one addition
public ?string $contentsToken = null;   // what the provider computes from the container's children; null where the vendor's inheritance needs no repair

// App\Services\VendorAccessService — T-091's class, one method
/** For each Active container whose provider answers a contentsToken: checkContainer() with SWEEP_TIMEOUT_SECONDS,
 *  compare with settings['contents_token'], and on a change put every granted row back to pending with
 *  ERROR_FOLDER_CHANGED and next_attempt_at null, then store the new token and contents_checked_at.
 *  Throttled by config('qori.connections.onedrive.children_check_minutes'). Containers touched. */
public function repairChangedContainers(): int;
// ReconcileAccessCommand::handle() calls it inside the same runFor() as retryDue().

// App\Http\Controllers\Share\OneDriveController
/** JSON {folders: [{id, name}], files: [{id, name, webUrl, size}]} for $request->query('folder') or the drive root.
 *  Owner only (errors.series.container_owner_only); ConnectionService::fresh() first;
 *  errors.series.provider_not_connected when there is no live connection. The root is listed and never pickable. */
public function items(string $group, Request $request, CurrentGroup $current, ConnectionService $connections): JsonResponse;

// App\Http\Requests\Share\StoreEpisodeRequest::content(), new arm
EpisodeProvider::OneDrive => ['drive_id' => $this->input('drive_id'), 'item_id' => $reference, 'name' => $this->input('file_name')],
// 'drive_id' and 'file_name' are ['nullable', 'string', 'max:200']; describeItem() overwrites name and web_url from Graph.

// config/services.php
'microsoft' => ['client_id' => env('MICROSOFT_CLIENT_ID'), 'client_secret' => env('MICROSOFT_CLIENT_SECRET')],
// config/qori.php, under 'connections'
'onedrive' => ['children_check_minutes' => 60],   // provisional — see below. No tier list: every tier ships (D-018)
```

`SeriesController::show()` (`:137`) adds `'container'` as `T-094` defines it and
`'browse' => ['connected' => bool, 'url' => route('share.connections.onedrive.items', …)]`.
`Show.vue` renders `OneDriveBrowser` in folder mode for the container pick and
in file mode, rooted at the container's item id, for the Episode pick; it fills
hidden `reference`, `drive_id` and `file_name`. In folder mode
`series.container.onedrive.explain` sits above the listing at every pick — the
first, a change, and the re-pick under `repick` or `missing` — as `T-094`'s
panel does. With an Active container, a folder chosen there and
`series.container.remove` both open `ContainerChangeDialog` with `T-091`'s
`containerImpact` prop, and the `PUT` or `DELETE` is posted from its confirm;
cancelling posts nothing. `T-094`'s `missingSince` prop is read from any
Episode's `content`, so a `onedrive` Episode carries it with nothing added
here, and this task reads it as `T-094` passes it: a row where it is set shows `series.episode.onedrive.stale` with `series.episode_check.check_now`
beside it, posting to `share.series.episodes.check`. Every sentence arrives as a prop through
`Terminology::line()` (`app/Support/Terminology.php:89`).

`T-091`'s `vendor` prop carries `provider` and the container's `url`.
`shared/Show.vue`, inside the
`#access` notice, renders `accesses.vendor.onedrive.awaiting_acceptance` when the
state is `awaiting_acceptance` and the provider `onedrive`, then
`accesses.vendor.onedrive.open_folder` as a link to that `url` with
`target="_blank"` and `rel="noopener"`, then `T-091`'s Check again form.

## Copy

`:minutes` is `OneDrive::GUEST_CODE_MINUTES`, interpolated rather than written
into either sentence that states it. The Integrations page's own headings,
buttons and tier dropdown are `T-044`'s, and the shared `series.container.*`
lines are `T-094`'s; neither is repeated here.

Each of the three tiers has a `recommended` sentence and its `limits.*` lines,
and a tier with only one of them is incomplete (`D-018`, and `T-044` says the
same): the recommendation is what Qori would do in the creator's place, the
limits are what that tier cannot do, and neither stands in for the other. No
line here refuses a tier or withholds one — `onedrive_free.terms` states
Microsoft's non-commercial clause and leaves the choice with the creator, and
the `onedrive_work` lines name what an administrator has to allow so a creator
can go and ask. Which lines show above Connect and which sit in `T-044`'s
disclosure is OneDrive's `ProviderSections::ESSENTIAL` entry under Code; the
disclosure keeps this table's order (`D-021`).

The `before_buying` lines are what a buyer needs from their side, said before
they pay (`D-021`). OneDrive writes no `common` line, because the account a
Peer needs differs by tier; the two personal tiers carry the same sentence under
their own keys. `before_buying.{tier}.invitation` stands for one row per tier,
written last in that tier's lines, and only for a tier where `T-097` Q1 shows a
take-up step. None of them states a number, so `BuyerRequirements` passes this
provider nothing but the Terminology nouns.

`disconnect.in_qori` and `account_change.in_qori` are the two lines `T-044`
asks of every connectable provider (`D-021` rule 3), written from `T-091`'s
rules for a connection that is not live — no call, people already let in keep
opening, a revoke waits for the same account — and from the switch paragraph
under Decisions, where Qori holds no token for the old account.

| Key                                                                  | File                      | English                                                                                                                                                                                                                                                                                                                                                   |
| -------------------------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `connections.providers.onedrive.name`                                | `lang/en/connections.php` | OneDrive                                                                                                                                                                                                                                                                                                                                                  |
| `connections.providers.onedrive.description`                         | `lang/en/connections.php` | Share files from one folder per :series in your own OneDrive. Everyone with access is let in on that folder, and whatever you put there reaches them.                                                                                                                                                                                                     |
| `connections.providers.onedrive.tiers.onedrive_free.label`           | `lang/en/connections.php` | Free OneDrive or Microsoft 365 Basic                                                                                                                                                                                                                                                                                                                      |
| `connections.providers.onedrive.tiers.onedrive_free.help`            | `lang/en/connections.php` | A personal Microsoft account with no subscription, or the Basic subscription.                                                                                                                                                                                                                                                                             |
| `connections.providers.onedrive.tiers.onedrive_free.recommended`     | `lang/en/connections.php` | Good for sharing with a few people at no cost: check everyone can use a personal Microsoft account, and choose Microsoft 365 Personal instead if you charge for access or expect a rush.                                                                                                                                                                  |
| `connections.providers.onedrive.tiers.onedrive_personal.label`       | `lang/en/connections.php` | Microsoft 365 Personal or Family                                                                                                                                                                                                                                                                                                                          |
| `connections.providers.onedrive.tiers.onedrive_personal.help`        | `lang/en/connections.php` | A personal Microsoft account with one of those subscriptions.                                                                                                                                                                                                                                                                                             |
| `connections.providers.onedrive.tiers.onedrive_personal.recommended` | `lang/en/connections.php` | What we would choose for a paid :series: no admin to ask, no non-commercial terms to weigh, and everyone signs in with their own personal Microsoft account.                                                                                                                                                                                              |
| `connections.providers.onedrive.tiers.onedrive_work.label`           | `lang/en/connections.php` | OneDrive for work or school                                                                                                                                                                                                                                                                                                                               |
| `connections.providers.onedrive.tiers.onedrive_work.help`            | `lang/en/connections.php` | Choose this if your Microsoft account has an admin: a company, school or organisation account.                                                                                                                                                                                                                                                            |
| `connections.providers.onedrive.tiers.onedrive_work.recommended`     | `lang/en/connections.php` | Good when the people you share with use any address: ask your admin to allow guest sharing before you connect, and choose Microsoft 365 Personal instead if the answer is no.                                                                                                                                                                             |
| `connections.providers.onedrive.limits.common.folder`                | `lang/en/connections.php` | Pick one folder for each :series and keep everything for it inside. Sharing the folder shares everything in it, :episode_plural or not. Your whole OneDrive and anything in Personal Vault can't be shared.                                                                                                                                               |
| `connections.providers.onedrive.limits.common.uploading`             | `lang/en/connections.php` | Upload new files straight into the folder. Files you move in from somewhere else reach people once Qori shares the folder again, on its next check.                                                                                                                                                                                                       |
| `connections.providers.onedrive.limits.common.updating`              | `lang/en/connections.php` | To update a file, upload the new version with the same name into the same folder. Deleting and uploading again makes a different file, and the :episode in Qori needs picking again.                                                                                                                                                                      |
| `connections.providers.onedrive.limits.common.own_drive`             | `lang/en/connections.php` | Only files in your own OneDrive can be used, not a team site or a shared library.                                                                                                                                                                                                                                                                         |
| `connections.providers.onedrive.limits.common.revoked`               | `lang/en/connections.php` | If you remove Qori's access in your Microsoft account, nobody new gets access until you connect again.                                                                                                                                                                                                                                                    |
| `connections.providers.onedrive.limits.onedrive_free.accounts`       | `lang/en/connections.php` | Everyone you share with needs a free personal Microsoft account on the address they confirm in Qori. Most work or school addresses can't be used to make one.                                                                                                                                                                                             |
| `connections.providers.onedrive.limits.onedrive_free.daily`          | `lang/en/connections.php` | Microsoft limits how much a free account can share each day and doesn't say how much. If many people join at once, some may wait up to a day.                                                                                                                                                                                                             |
| `connections.providers.onedrive.limits.onedrive_free.terms`          | `lang/en/connections.php` | Microsoft's terms say Microsoft 365 Basic is for personal, non-commercial use. Check with Microsoft before charging for access.                                                                                                                                                                                                                           |
| `connections.providers.onedrive.limits.onedrive_personal.accounts`   | `lang/en/connections.php` | Everyone you share with needs a personal Microsoft account on the address they confirm in Qori. Most work or school addresses can't be used to make one.                                                                                                                                                                                                  |
| `connections.providers.onedrive.limits.onedrive_personal.daily`      | `lang/en/connections.php` | Microsoft allows more sharing each day on this plan, but doesn't say how much.                                                                                                                                                                                                                                                                            |
| `connections.providers.onedrive.limits.onedrive_work.guests`         | `lang/en/connections.php` | People can use any address. Anyone without a Microsoft account signs in with a code Microsoft emails them, which lasts :minutes minutes, and needs a fresh one the next day.                                                                                                                                                                              |
| `connections.providers.onedrive.limits.onedrive_work.guest_of`       | `lang/en/connections.php` | Each person becomes a guest in your organisation and accepts its terms the first time they open anything.                                                                                                                                                                                                                                                 |
| `connections.providers.onedrive.limits.onedrive_work.admin`          | `lang/en/connections.php` | Your admin must allow sharing with new guests, let you invite them, and let you connect Qori. Unless you are the admin, expect to ask.                                                                                                                                                                                                                    |
| `connections.providers.onedrive.limits.onedrive_work.restricted`     | `lang/en/connections.php` | If sharing is limited to existing guests or to approved domains, new people can't be added.                                                                                                                                                                                                                                                               |
| `connections.providers.onedrive.limits.onedrive_work.expiry`         | `lang/en/connections.php` | If your admin makes guest access end after a set number of days, people lose access then, including people who paid.                                                                                                                                                                                                                                      |
| `connections.providers.onedrive.limits.onedrive_work.sign_in`        | `lang/en/connections.php` | Your organisation's sign-in rules for guests, such as two-step verification, add steps the first time someone opens a file.                                                                                                                                                                                                                               |
| `connections.providers.onedrive.limits.onedrive_work.employer`       | `lang/en/connections.php` | Someone whose own employer blocks working with other organisations won't be able to open your files.                                                                                                                                                                                                                                                      |
| `connections.providers.onedrive.limits.onedrive_work.daily`          | `lang/en/connections.php` | Microsoft limits how many new guests an organisation can add each day, and far fewer while the organisation is new. A busy launch may leave some people waiting.                                                                                                                                                                                          |
| `connections.grants.reasons.guests_refused`                          | `lang/en/connections.php` | your organisation does not allow sharing with new guests, or not to this person's address; your admin has to allow guest sharing and let you invite them                                                                                                                                                                                                  |
| `connections.grants.reasons.account_gated`                           | `lang/en/connections.php` | Microsoft has asked you to verify your account before it will share anything else                                                                                                                                                                                                                                                                         |
| `connections.grants.reasons.daily_limit`                             | `lang/en/connections.php` | your account has shared as much as Microsoft allows today; Qori tries again tomorrow                                                                                                                                                                                                                                                                      |
| `connections.grants.reasons.folder_changed`                          | `lang/en/connections.php` | the folder changed and Qori is sharing it again                                                                                                                                                                                                                                                                                                           |
| `connections.providers.onedrive.disconnect.in_qori`                  | `lang/en/connections.php` | :peer_plural already let in keep their access to your folders in OneDrive and keep opening their :episode_plural from Qori. Nobody new is let in, even after opening an invitation, and anyone whose access ends in the meantime keeps it on the folder, until you connect :account again: then Qori lets in everyone waiting and takes those people off. |
| `connections.providers.onedrive.account_change.in_qori`              | `lang/en/connections.php` | :peer_plural already let in keep their access to your folders in :current until you remove it there; once you switch, Qori can't reach :current to do it for you. Their :episode_plural stop opening from Qori at their next check, until each folder and its files are picked again from :incoming.                                                      |
| `series.container.onedrive.pick`                                     | `lang/en/series.php`      | Choose the OneDrive folder for this :series                                                                                                                                                                                                                                                                                                               |
| `series.container.onedrive.explain`                                  | `lang/en/series.php`      | Everyone with access to this :series can open everything inside the folder you choose, :episode_plural or not. Use one folder that holds only this :series.                                                                                                                                                                                               |
| `series.container.onedrive.connect_first`                            | `lang/en/series.php`      | Connect OneDrive under Integrations to choose a folder.                                                                                                                                                                                                                                                                                                   |
| `series.episode.onedrive.pick`                                       | `lang/en/series.php`      | Choose a file from the folder                                                                                                                                                                                                                                                                                                                             |
| `series.episode.onedrive.stale`                                      | `lang/en/series.php`      | This file is no longer in the folder, or was replaced with a different one. If you've moved it back, check now; if you uploaded it again, pick it again. People still see whatever is in the folder.                                                                                                                                                      |
| `accesses.vendor.onedrive.awaiting_acceptance`                       | `lang/en/accesses.php`    | Microsoft has emailed you an invitation to :creator's folder. Open the folder once as that account, then come back to this tab and check again.                                                                                                                                                                                                           |
| `accesses.vendor.onedrive.open_folder`                               | `lang/en/accesses.php`    | Open the folder in OneDrive                                                                                                                                                                                                                                                                                                                               |
| `accesses.vendor.onedrive.sign_in_code`                              | `lang/en/accesses.php`    | If :email has no Microsoft account, Microsoft emails you a code to sign in with. It lasts :minutes minutes, and the next day needs a fresh one.                                                                                                                                                                                                           |
| `accesses.vendor.onedrive.before_buying.onedrive_free.account`       | `lang/en/accesses.php`    | A personal Microsoft account on the address you confirm in Qori. A free one is enough, and any personal address can have one, but most work or school addresses can't.                                                                                                                                                                                    |
| `accesses.vendor.onedrive.before_buying.onedrive_personal.account`   | `lang/en/accesses.php`    | A personal Microsoft account on the address you confirm in Qori. A free one is enough, and any personal address can have one, but most work or school addresses can't.                                                                                                                                                                                    |
| `accesses.vendor.onedrive.before_buying.onedrive_work.address`       | `lang/en/accesses.php`    | Any address you can receive email at works. If it has no Microsoft account, Microsoft emails you a code to sign in with when you open something.                                                                                                                                                                                                          |
| `accesses.vendor.onedrive.before_buying.onedrive_work.guest`         | `lang/en/accesses.php`    | The first time you open anything, you join the organisation sharing this :series as a guest, accept its terms, and may be asked for extra sign-in steps such as two-step verification.                                                                                                                                                                    |
| `accesses.vendor.onedrive.before_buying.onedrive_work.employer`      | `lang/en/accesses.php`    | If you use a work or school address, your own organisation may block files shared by another. A personal address avoids that.                                                                                                                                                                                                                             |
| `accesses.vendor.onedrive.before_buying.{tier}.invitation`           | `lang/en/accesses.php`    | Once you have access, open the folder once from the invitation Microsoft emails you. The page for this :series shows you where.                                                                                                                                                                                                                           |
| `errors.series.container_root_not_allowed.message`                   | `lang/en/errors.php`      | Your whole OneDrive can't be shared.                                                                                                                                                                                                                                                                                                                      |
| `errors.series.container_root_not_allowed.resolution`                | `lang/en/errors.php`      | Make one folder for this :series, put its files inside, and choose that.                                                                                                                                                                                                                                                                                  |
| `errors.series.personal_vault_not_allowed.message`                   | `lang/en/errors.php`      | Nothing in Personal Vault can be shared.                                                                                                                                                                                                                                                                                                                  |
| `errors.series.personal_vault_not_allowed.resolution`                | `lang/en/errors.php`      | Move it into the folder for this :series, then pick it again.                                                                                                                                                                                                                                                                                             |
| `errors.series.provider_not_allowed.resolution`                      | `lang/en/errors.php`      | Video and audio need external storage — connect Google Drive, OneDrive, Vimeo or Dropbox and link the file from there.                                                                                                                                                                                                                                    |

`errors.series.provider_not_allowed.resolution` is a wording edit of the line
at `lang/en/errors.php:186`, which `T-094` rewrites first; this task adds
OneDrive to the providers `T-094`'s line names.
`errors.series.container_required`, `episode_file_not_found`,
`file_outside_folder`, `container_not_found` and `container_owner_only` are
`T-094`'s and `errors.series.provider_not_connected` is `T-044`'s; all six are
reused unchanged. The Peer's `pending`, `needs_creator` and `awaiting_identity`
sentences are `T-091`'s `shared.vendor_notice.reasons.*`, and each already names
who resolves it: `pending` says when Qori tries next, `needs_creator` that the
creator has been told, and both that nothing more is needed from the Peer
(`D-020`). `awaiting_acceptance` is the one state this task answers in
OneDrive's own words, chosen by the `provider` on that notice, and its sentence
points at `T-091`'s Check again rather than naming a wait. Check again, Try
again now and Check now — their buttons, flashes and throttle sentences — are
`T-091`'s `shared.vendor_notice.*` and `connections.grants.*` lines and
`T-094`'s `series.episode_check.*` lines; the replace and remove
dialog is `T-091`'s `series.container_change.*`; none is repeated here. The
line naming which account to open with is `T-092`'s
`identities.open_with`, and `accesses.vendor.onedrive.sign_in_code` sits beside
it rather than restating it. Vendor names appear under `D-016`'s exception, on
the surfaces where a person is choosing between vendors or being told which
account to use. No line puts an article directly before a placeholder
(`tests/Feature/TerminologyTest.php:218`).

## Routes

| Verb   | Path                                     | Name                               | Action                                     |
| ------ | ---------------------------------------- | ---------------------------------- | ------------------------------------------ |
| GET    | `/g/{group}/connections/onedrive/items`  | `share.connections.onedrive.items` | `Share\OneDriveController::items`          |
| PUT    | `/g/{group}/series/{seriesId}/container` | `share.series.container.store`     | `Share\SeriesContainerController::store`   |
| DELETE | `/g/{group}/series/{seriesId}/container` | `share.series.container.destroy`   | `Share\SeriesContainerController::destroy` |

The listing route is new and sits in `routes/share/payments.php` beside
`share.connections.*` and `settings.integrations` (`:20-21`); it is JSON, not a
page, and takes no slug. The two container rows are `T-094`'s in
`routes/share/series.php`, listed because the folder panel posts to them; this
task adds no line there.
The OAuth landing is `T-044`'s `connections.oauth.finalise`, the identity landing
`T-092`'s `identities.finalise`, and Open is `T-089`'s `shared.episodes.open`;
none of the three changes. Both landings name the vendor, never the service
(`D-033`), so a creator connecting OneDrive comes back to
`u/connections/microsoft/finalise`, with `onedrive` and the tier carried in
`T-044`'s session state, and a Peer confirming their account comes back to
`u/identities/microsoft/finalise`. The three buttons `D-021` adds post to
routes this task does not add either: Check again to `T-091`'s
`shared.access.check`, Try again now to `T-091`'s
`share.settings.integrations.retry` with provider `onedrive`, and Check now to
`T-094`'s `share.series.episodes.check`. OneDrive needs nothing in any of them
beyond `checkGrant()`, `grant()` and `checkItem()`.

## Tests

Every case fakes HTTP with the named `T-097` fixture through
`Http::fake(['graph.microsoft.com/*' => …, 'login.microsoftonline.com/*' => …])`
and `Http::preventStrayRequests()` in `setUp`, as
`tests/Feature/Storage/PlaybackTest.php:36` does. `T-091`'s
`VendorAccessService` is resolved with the real `OneDrive` in the
`grant-providers` tag, and the Peer's identity comes from `T-092`'s
`VendorIdentityFactory`.

**New: `tests/Feature/Integrations/Microsoft/OneDriveTest.php` — 15 cases**

1. `test_it_invites_the_peer_on_the_folder_with_no_notification` — `permissions-folder.json` without the address, then `invite-personal-200.json`; `assertSent` sees the four-key body and `Bearer`; `vendorRef` is the fixture's permission `id`.
2. `test_a_permission_already_on_the_folder_is_read_not_invited` — no POST.
3. `test_a_grant_without_an_identity_makes_no_call` — `awaiting_identity`; zero requests.
4. `test_an_invitation_not_yet_taken_up_is_awaiting_acceptance` — `permission-get-before-open.json`; `isGranted()` false.
5. `test_check_grant_promotes_the_row_once_the_grantee_is_filled_in` — `permission-get-after-open.json`; `granted`, fresh `checked_at`.
6. `test_check_grant_reports_a_permission_the_drive_no_longer_has` — 404; `pending`, `GrantResult::ERROR_PERMISSION_GONE`.
7. `test_a_throttled_invite_is_pending_with_the_retry_after` — `invite-429.json`.
8. `test_a_timeout_is_pending_with_the_timeout_it_was_given` — `ConnectionException`; the request carried the seconds passed in, and a budget above `GraphClient::TIMEOUT_SECONDS` was cut to it (`D-034`).
9. `test_a_tenant_that_refuses_new_guests_needs_the_creator` — `invite-work-existing-guests.json` and `invite-work-guest-invites-off.json`; `ERROR_GUESTS_REFUSED`.
10. `test_a_401_answers_connection_unusable_with_no_retry` — `invite-401-expired-token.json`; one request; `ERROR_CONNECTION_UNUSABLE` (the refresh and the reconnect mark are `T-091`'s cases 61 and 62).
11. `test_it_revokes_by_permission_id_and_treats_a_404_as_revoked` — the path is built from the grant's `external_container_id`, so a grant whose container row is gone still reaches the folder.
12. `test_it_never_deletes_a_permission_that_covers_several_people` — a link permission from `permissions-folder.json`; `ERROR_SHARED_PERMISSION`; zero requests.
13. `test_open_link_is_the_stored_web_url_with_the_account_hint` — no HTTP call.
14. `test_open_link_falls_back_to_the_folder_when_the_file_is_missing` — `missing_since` set.
15. `test_check_container_refuses_the_drive_root_and_a_file_and_returns_a_contents_token` — `drive-me.json`, `children-folder.json`.

**New: `tests/Feature/Series/OneDriveContainerTest.php` — 15 cases**

16. `test_the_owner_attaches_a_onedrive_folder_to_a_series` — `external_id` is `{driveId}!{itemId}`, `url`, `settings.name` and `settings.contents_token`; a `pending` grant per active Access; zero invite calls.
17. `test_the_drive_root_is_refused_as_a_container` — `container_root_not_allowed`.
18. `test_a_onedrive_episode_needs_the_series_folder_first` — `container_required`.
19. `test_a_onedrive_episode_outside_the_folder_is_refused` — `file_outside_folder`.
20. `test_a_onedrive_episode_stores_the_drive_item_name_and_link` — the four `content` keys.
21. `test_an_item_in_the_personal_vault_is_refused` — `personal_vault_not_allowed`.
22. `test_an_admin_cannot_attach_a_folder_or_list_the_drive` — `container_owner_only`.
23. `test_the_listing_endpoint_returns_folders_and_files_or_says_onedrive_is_not_connected` — `provider_not_connected`.
24. `test_every_tier_is_offered_with_its_recommendation_its_essential_lines_and_the_rest` — all three `ProviderTier` OneDrive cases pass `BeginConnectionRequest` and the dropdown offers all three; for each tier `recommended` is its sentence, `essential` is its `ProviderSections::ESSENTIAL` entry in that order, and `more` holds every other `limits.*` line for that tier in the Copy table's order, with `:minutes` interpolated.
25. `test_the_folder_sharing_sentence_is_shown_at_the_first_pick_and_at_a_change` — the creator's Series page carries `series.container.onedrive.explain` with no container, with an `Active` one and with a `missing` one.
26. `test_the_series_page_passes_the_impact_of_changing_the_onedrive_folder` — `containerImpact.onedrive` has provider `onedrive`, the count of active Accesses, and the Series' OneDrive Episodes and not its Vimeo one; zero Graph requests.
27. `test_replacing_the_folder_checks_every_onedrive_episode_against_the_new_one` — `PUT` with an Active container; the old rows are `revokable()`; an item whose `parentReference.id` is the new folder keeps `missing_since` null and one outside it has `missing_since` set before the creator's page renders; toast `series.container.replaced`.
28. `test_removing_the_folder_leaves_the_files_and_the_sweep_deletes_each_permission` — `DELETE`; toast `series.container.removed`; `qori:access:reconcile` sends one `DELETE …/permissions/{permId}` per granted row, on the drive and item split from `external_container_id`, and no other write.
29. `test_check_now_clears_a_file_moved_back_into_the_folder` — an Episode with `missing_since` set; `POST share.series.episodes.check`; the item answers inside the folder; `missing_since` null, `checked_at` now; flash `series.episode_check.clear`.
30. `test_check_now_keeps_the_flag_on_a_file_still_outside_the_folder` — the item answers with another parent; `missing_since` unchanged; flash `series.episode_check.still`; the row still shows `series.episode.onedrive.stale`.

**New: `tests/Feature/Shared/OneDriveJourneyTest.php` — 13 cases**

31. `test_a_new_peer_who_buys_is_invited_on_the_folder_and_opens_the_file` — `CheckoutService::fulfil()` with a confirmed identity; `GET shared.episodes.open` is a 302 to the fixture's `webUrl`.
32. `test_a_new_peer_who_claims_a_free_series_is_invited_in_the_same_request`.
33. `test_a_peer_without_a_microsoft_identity_is_prompted_not_refused` — `awaiting_identity`; `T-092`'s prompt; the Series page renders the OneDrive Episodes' Open disabled, and `GET shared.episodes.open` redirects to `shared.show` at `#access` with flash `shared.vendor_notice.redirected`.
34. `test_a_peer_whose_invitation_is_not_taken_up_is_told_what_is_left_to_do` — the `#access` notice holds `accesses.vendor.onedrive.awaiting_acceptance`, never the pending sentence, with `accesses.vendor.onedrive.open_folder` linking to the container's `url` and `shared.vendor_notice.check_again` beside it.
35. `test_check_again_after_opening_the_invitation_lets_the_peer_in` — an `awaiting_acceptance` row checked a minute ago; `POST shared.access.check`; `permission-get-after-open.json`; row `granted`; redirect to `shared.show` at `#access` with flash `shared.vendor_notice.opened`; Open is then a 302 to `webUrl`.
36. `test_check_again_before_the_invitation_is_opened_says_so_and_changes_nothing` — `permission-get-before-open.json`; row still `awaiting_acceptance`; flash `shared.vendor_notice.checked`; the notice still holds the invitation sentence.
37. `test_a_peer_held_by_the_daily_limit_is_told_when_qori_tries_next` — a `pending` row with `ERROR_DAILY_LIMIT` and `next_attempt_at` a day out; the notice's sentence names that time and not "in a moment"; no Check again until the row is due, then Check again; zero Graph requests on the page load.
38. `test_open_rereads_the_permission_and_invites_again_when_the_drive_lost_it` — a `granted` row with a stale `checked_at`; 404 on the permission; an invite; 302 in the same request.
39. `test_an_episode_added_to_the_folder_opens_with_no_new_invite` — a second Episode; zero invite calls.
40. `test_a_file_moved_into_the_folder_re_invites_every_peer_on_the_next_sweep` — a changed `children-folder.json`; `qori:access:reconcile` puts the rows `pending` with `ERROR_FOLDER_CHANGED` and invites again.
41. `test_revoking_access_deletes_the_permission` — `AccessService::revoke()`; row `revoked`.
42. `test_try_again_now_invites_a_peer_the_tenant_refused_once_the_admin_allows_guests` — a `needs_creator` row with `ERROR_GUESTS_REFUSED`; the owner posts `share.settings.integrations.retry` for `onedrive`; `invite-work-200.json`; the row leaves `needs_creator`; flash `connections.grants.retried`.
43. `test_the_before_buying_list_names_what_the_creators_onedrive_tier_needs` — `BuyerRequirements::for()` on a Series with an Active OneDrive container gives the `onedrive_free.account` line on the free tier, the same sentence on `onedrive_personal`, and `address`, `guest` and `employer` in that order on `onedrive_work`; the public Series page renders them beside the buy button, and above the identity prompt on a free Series.

**New: `tests/Feature/Integrations/Microsoft/MicrosoftSignInTest.php` — 4 cases**

44. `test_it_reads_the_object_id_tenant_and_verified_email_from_the_id_token` — `finaliseConfirmation()` with the expected `state` and nonce and a `code`, `oidc-token-personal.json`, `oidc-claims-personal.json`: `Confirmed`, `oid` the subject, `tid` the tenant, the claim's email; no token retained.
45. `test_an_unverified_email_is_refused` — `xms_edov` false: `UnverifiedEmail`; nothing written.
46. `test_the_authorize_url_carries_the_common_authority_and_the_sign_in_scopes`.
47. `test_a_confirmed_microsoft_identity_backfills_a_waiting_grant` — an `awaiting_identity` row is invited at the finalise step.

**New: `tests/Feature/Integrations/Microsoft/MicrosoftAccountsTest.php` — 6 cases**

48. `test_the_authorize_url_asks_for_files_readwrite_offline_access_and_user_read` — and its `redirect_uri` is `route('connections.oauth.finalise', 'microsoft')`, never `onedrive` (`D-033`).
49. `test_it_exchanges_the_code_and_stores_the_account_and_the_refresh_token` — `finaliseConnection()` with the expected `state` and a `code` answers `Connected` from `token-authorization-code.json`; the landing then stores the account and the refresh token; `identity()` reads `GET /me`; the token call's `timeout` option was the budget, and a budget above `GraphClient::TIMEOUT_SECONDS` was cut to it (`D-034`).
50. `test_a_refresh_replaces_the_stored_refresh_token` — `token-refresh.json`; the old one is not kept.
51. `test_an_invalid_grant_marks_the_connection_for_reconnect`.
52. `test_a_consent_refusal_names_the_admin_policy` — an `error_description` opening with AADSTS90094 on the landing, shaped from `consent-w1.txt` once `T-097` records it: `MicrosoftAccounts` answers `AdminBlocked`, the landing is 403 `errors.connections.admin_blocked`, and no token call is made.
53. `test_it_reads_the_connect_landing_in_microsofts_words` — `finaliseConnection()` given `error=access_denied` answers `Declined`; another error word `Failed` with the AADSTS number as `upstream`, or the word when there is none; a wrong `state`, with an error or without, `NotFromQori`; the expected `state` and no `code` `Failed` — none of these sends a request (`Http::assertNothingSent()`); then a token response whose `scope` lacks `Files.ReadWrite` `ScopeDeclined`, with no call after the exchange; a 400 `Failed` with `upstream` `400`; a `ConnectionException` `Failed` with `connection`.

**New, continued: `tests/Feature/Integrations/Microsoft/MicrosoftSignInTest.php` — 1 case**

54. `test_it_reads_the_sign_in_landing_in_microsofts_words` — `finaliseConfirmation()` given `error=access_denied` answers `Declined`; another error word `Failed`; a wrong `state` `NotFromQori`; the expected `state` and no `code` `Failed`, none of them calling Microsoft; claims with another `aud`, a past `exp`, no email or another `nonce` `Failed` with `id_token`.

Total: 54. Case 7 is written only if `T-097` captured a 429 body; otherwise it
is dropped from the count and the `Retry-After` branch is covered against the
documented 429 shape with no fixture, and the report says so. Cases 29 and 30
shape the item read from one entry of `children-folder.json`, as the calls table
says. Cases 29 and 30 post to `T-094`'s Check now.

**Changed:** `tests/Feature/Enums/ModelEnumTest.php` — no edit expected: both
new cases are produced outside their declaring file by `OneDrive::provider()`
and `EpisodeProvider::connection()`, which is what its orphan check asks for
(`:158-177`). `tests/Feature/EnvExampleTest.php` — the two `MICROSOFT_*` keys
join `.env.example`. `tests/Feature/Series/EpisodeRoutesTest.php` and
`tests/Feature/TerminologyTest.php` — run; neither pins `allowedProviders()`
today, and the second walks the new lang lines. `T-044`'s test that every
`ProviderSections::ESSENTIAL` key exists and no tier lists more than
`MAX_ESSENTIAL` — run over OneDrive's entry, with no edit.

## Acceptance

- [ ] For each of the three tiers, in a clean browser at 400px and desktop
      widths: a new Peer buys the paid Series (Stripe test mode), confirms
      their Microsoft account, and opens the PDF, the document and the MP4 in
      new tabs on Microsoft's site
- [ ] The same walk for the free Series, from the Series link
- [ ] After the creator uploads a new file, replaces one with a same-name
      upload and moves one in from elsewhere, the same Peer opens all three —
      the moved one after `qori:access:reconcile` has shared the folder again
- [ ] Every tier is offered in the dropdown and none is refused, and the
      recommendation and the limitations shown before connecting are the ones
      for the tier chosen: its `ESSENTIAL` lines under the recommendation and
      every other line in one disclosure, all above Connect, at 400px and
      desktop widths
- [ ] Before paying, a buyer on the paid Series' public page sees the lines for
      the creator's tier beside the buy button, and on the free Series above
      the identity prompt, on each tier
- [ ] A grant the vendor refuses (sharing set to existing guests on the work
      tenant) is `needs_creator` on the Integrations page with a reason naming
      what the administrator has to allow, and the Peer sees a sentence naming
      who resolves it, never a dead page; once the setting is changed, Try again
      now lets the waiting Peer in or says who still waits, without promising
      when; a throttled grant ends `pending`, the Peer's sentence says when Qori
      tries next, the sweep retries, Open then works
- [ ] On a tier with a take-up step: while the grant is `awaiting_acceptance`,
      the Series page's OneDrive Open controls are disabled and the `#access`
      notice names the invitation; the Peer opens the folder in a new tab, comes
      back, presses Check again and lands on the notice with Open working; a
      press before opening says it checked just now and changes nothing; a
      saved Open link lands on the notice with its one-line flash
- [ ] The grant runs inside the request that creates the Access and never
      blocks it: a Microsoft call that outlasts
      `VendorAccessService::REQUEST_TIMEOUT_SECONDS` leaves the row `pending`,
      the Peer sees the pending sentence, and the sweep finishes it — timed on
      each tier against `T-097` Q12
- [ ] A permission removed by hand in OneDrive is granted again on the Peer's
      next Open, which re-reads the stored permission rather than trusting a
      `granted` row; revoking access removes the permission, and a permission
      covering several people is left alone with a warning logged
- [ ] The picker refuses the drive root and a Personal Vault item, says at the
      first pick and at a change that the folder shares everything inside it,
      and every sentence on the folder panel comes from lang
- [ ] Changing or removing the folder shows the Peer count and the OneDrive
      Episodes before anything is sent; after a change, a file outside
      the new folder is flagged on the page the creator lands on; after a
      removal the files are untouched and the sweep takes each Peer's
      permission off the old folder
- [ ] A file moved out of the folder is flagged; moved back, Check now clears
      the flag at once, and a second press inside the throttle says when the
      next is allowed
- [ ] `docs/flows/vendor-access.md`, `docs/flows/storage.md` and the tinker
      recipe describe what was built, tier by tier
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- `T-097` Q1 and Q11: whether a silent invite is usable access, and whether
  re-reading the permission shows it. They decide whether the 200 is `granted`
  or `awaiting_acceptance`, whether `sendInvitation: true` becomes this task's
  fallback for a tier, and what `checkGrant()` can read. They also decide
  whether opening the folder's `webUrl` as the invited account takes the
  invitation up, so whether the notice carries `open_folder` (`D-020`), and
  which tiers get `before_buying.{tier}.invitation` (`D-021`) — the spike's.
- `T-097` Q3 and Q4: whether an uploaded file reaches an existing Peer, and
  what repairs a moved-in one. If only a per-item invite repairs it, that is a
  change to `T-091`'s grant model, recorded there, and `repairChangedContainers()`
  is re-drafted — the spike's, then the owner's.
- `T-097` Q6: whether the invite response is a direct or a link permission, and
  whether a repeat returns the same id. It decides what `vendor_ref` holds,
  how often revoke has to refuse, and whether `ContainerChangeDialog`'s "taken
  off this folder" is true for OneDrive or needs a OneDrive form (`D-021`) —
  the spike's.
- `T-097` Q7, Q9 and Q12: the tenant refusal bodies, the daily-limit body and
  number, and an invite's wall time against `REQUEST_TIMEOUT_SECONDS`. The
  first two are the `failure()` mapping, the third says whether the in-request
  grant lands or the sweep is the real path — the spike's.
- `GraphClient::TIMEOUT_SECONDS` 15, Microsoft's own limit on one call —
  Graph's and the sign-in endpoints' — which a caller's budget may only
  shorten (`D-034`): borrowed from what Qori's
  Dropbox and Vimeo clients set today
  (`app/Integrations/Dropbox/DropboxStorage.php:51`,
  `app/Integrations/Vimeo/VimeoVideos.php:43`) until `T-097` Q12 times an
  invite — anyone's.
- `T-097` Q10: whether publisher verification is needed before work-tenant
  creators can consent, and its lead time — the owner's, and on the beta path
  now that the work tier ships (`D-018`).
- ~~Which tiers go in `config('qori.connections.onedrive.tiers')` at release.
  `['onedrive_work']` is a placeholder, not a recommendation; the answer is one
  per family that `T-097` walked end to end — the owner's, on the report.~~
  **Answered 17 September 2026 (`D-018`):** all three ship, and OneDrive ships
  with every other provider in the stream. There is no allow-list and no config
  key: each tier is offered with its limitations and its recommendation on
  screen, and the creator decides.
- The v8 File Picker instead of the Graph listing, accepting
  `OneDrive.ReadWrite` on personal accounts and a SharePoint scope on work
  ones. This draft chose the listing on `D-016`'s narrowest-scope rule and
  `T-097`'s exclusion of the picker; the brief named the picker — the owner's.
- Whether `User.Read` stays in the scopes, or `GET /me/drive`'s `owner.user`
  serves `ConnectsAccounts::identity()` and the scope list drops to the two the
  research names — anyone's, with `T-044`.
- Whether an MP3 plays in OneDrive's viewer for a Peer. `T-097`'s content set
  holds no audio file; until somebody has seen one, `Audio` keeps OneDrive out
  of `allowedProviders()` — anyone's, with the spike.
- Whether free OneDrive and Microsoft 365 Basic stay one entry in the dropdown
  or become two. Both ship either way (`D-018`); what is open is how they are
  labelled, because Basic is sold with sharing features the free tier lacks and
  its daily cap is unpublished, so the `terms` and `daily` lines are true of
  Basic and unproven of free, and one entry states both — the owner's.
- `children_check_minutes` at 60, and whether Graph's `delta` call replaces the
  children listing — anyone's, with the spike's Q4 evidence.
- Whether this `L` task splits: the three connectors — connect, grant, Peer
  sign-in — are three commits, and a ready `L` names its split — the owner's.
- `ContainerCheck` gaining `contentsToken` and `VendorAccessService` gaining
  `repairChangedContainers()` are changes to `T-091`'s Code section; confirm
  with that task rather than adding them here — anyone's, with `T-091`. The
  three `ProviderTier` cases are a plain addition to `T-044`'s enum, which
  filters nothing (`D-018`).
- ~~Whether this task or `T-094`/`T-096` creates `SeriesContainerController`,
  `StoreSeriesContainerRequest` and the folder panel, since the stream's order
  may not be the build order — the owner's, as the file-clash arbiter. The same
  gap holds for the item check: `CheckEpisodeItemsCommand`,
  `EpisodeCheckController`, `share.series.episodes.check`, the daily pass and
  the container arm are `T-094`'s (`D-021`), and `depends:` did not name it, so if
  this task runs before `T-094`, only the check after a replace sets
  `missing_since` (`T-091`'s `checkEpisode()`, already a dependency), nothing
  flags a file day to day and there is no Check now — the owner's, with the
  stream order.~~ Answered 17 September 2026: depends on `T-094`, which builds
  the item check and Check now (`D-021`). `T-094` also creates
  `SeriesContainerController`, `StoreSeriesContainerRequest` and the folder
  panel, which this task edits.
- Whether Basic's `terms` line belongs among the free tier's essential lines.
  This draft reads it as binding the creator rather than stopping a share, and
  leaves it in the disclosure because the tier's `recommended` sentence already
  names charging — anyone's, with `T-044`.
- `connections.grants.reasons.daily_limit` ("Qori tries again tomorrow") and
  `connections.grants.reasons.folder_changed` explain rows that are `pending`,
  and `T-091`'s Integrations page lists only `needs_creator` rows, so neither
  line is ever shown as specified; the Peer's `pending` sentence already says
  when Qori tries next (`D-020`). Drop both, or have `T-091` list those rows
  too — anyone's, with `T-091`.
- A read of one file inside the folder: `T-097` captures only
  `item-other-account.json`, so `checkItem()`'s cases are shaped from
  `children-folder.json`. Whether the spike adds an `item-get.json` — anyone's,
  with the spike.
- **From the privacy and terms drafts (`docs/pptcs/`, 19 September 2026):**
  Microsoft's APIs Terms s.5(b)-(c) expect Qori to delete what it holds when a
  creator disconnects; this draft, like `T-044`, keeps the row and the item
  ids. Settle it with `T-044`'s disconnect before `ready` — anyone's.
- **From the storage review's rate-limit table (20 September 2026):**
  Microsoft's SharePoint throttling guidance (`V5`), the page Graph's service
  limits send a file caller to, gives 3,000 requests per five minutes per user,
  tenant resource budgets that depend on the licence, and five resource units
  for every permission operation, reads included. Two lines above rest on the
  older reading: the 300 sharing calls per five minutes, struck from `T-097`'s
  sources table on the same date and to go from the paragraph on `grant()` with
  it, and the argument beside it that a `GET` costs nothing because it is not a
  sharing call — a permission list spends five units like any other permission
  call, so listing before every invite doubles what a fan-out costs. A 429 is
  the user's and the tenant's rather than the row's, and `failure()` gives its
  `Retry-After` to one grant while `T-091`'s sweep takes the next Peer on the
  same token — anyone's, with `T-091`'s sweep.
- **From the storage review, F11 and its evidence table (20 September 2026):**
  every Graph payload named under Code is documented and unobserved, and the
  row `T-097` owns is what settles it — personal and work walked separately,
  silent redemption, the permission's shape, removing one member of a shared
  link, the moved-in file's repair, the verified identity claims and the
  throttles. One outcome is missing whatever the spike finds: `revoke()`
  answers `RevokeResult::failed(ERROR_SHARED_PERMISSION)` with a `Log::warning`
  and no vendor call, so a Peer Qori cannot take off a shared link leaves
  nobody anything to see or act on, and an unresolved cleanup needs a visible
  end — `T-097`'s to answer, then the owner's.
- **From the storage review, F10 (20 September 2026):** `T-091`'s consumers
  still read a container — Try again now selects Accesses with one, its creator
  list loads `container.series`, and the Peer notice takes the provider and URL
  from one — which is the shape this task needs and supplies, since
  `checkItem()` fills `insideContainer` from `parentReference.id` where Drive's
  item result leaves it null. That is the reason the shared service must not be
  reshaped around Drive's per-file grants before `T-097` has said what
  OneDrive's unit is; the queries and tests that read a container are settled
  with `T-091` before either task freezes — anyone's, with `T-091`.

## Re-scope log

None.

## Notes

The brief for this draft grouped free, Basic, Personal and Family as one
personal tier with non-commercial terms. That is right for Basic under the
Services Agreement §14.h.i and wrong for Personal and Family: their supplement
says the non-commercial restriction does not apply to Microsoft 365
subscription services, and the supplement governs in a conflict. No
non-commercial clause was found for free OneDrive with no subscription, so the
copy claims none. The three tiers here follow the blueprint's summary table.

`T-097`'s Notes say `T-098` carries `depends: none` and `blocks: none` while
that file says `blocks: T-098`; this draft sets `depends: T-044, T-091, T-092,
T-097`, which is the edit that was owed and agrees with all four of their
`blocks:` lines. `T-094` joined `depends:` on 17 September
2026, when the storage stream made `T-094` the first complete journey and its
`blocks:` became `T-090, T-096, T-098, T-100`.

Microsoft's two dates for retiring SharePoint's own verification codes
disagree — July per the FAQ, 1–31 October 2026 per MC1243549 — so a
work-tenant Peer in this window may meet either sign-in, and re-sharing is what
creates the guest account for someone who does not have one. The re-invite this
task already sends on a folder change is the same call.

`CLAUDE.md` still says integrations expose `name()` and are bound in
`AppServiceProvider`; the code says `provider()` and
`IntegrationServiceProvider` (`app/Providers/IntegrationServiceProvider.php:29-39`),
and this draft follows the code. `docs/flows/storage.md:7-8` still says no
connector is live and `:56` still explains why Dropbox rather than Drive; both
are `T-044`'s and `T-094`'s to correct, and this task adds its own row to the
providers table (`:51-57`) rather than rewriting theirs.

An Episode's `content` cannot be edited from the creator's page
(`app/Http/Requests/Share/UpdateEpisodeRequest.php:24-30` validates title and
preview only), so a stale file is fixed by picking again, which makes a new
Episode and orphans its progress by id
(`app/Http/Controllers/Shared/SharedController.php:140-141`) — today's
behaviour, and not this task's to change. The `stale` line says so.

The siblings disagreed about where the Peer's grant-state copy lives: `T-091`'s
draft put it in `lang/en/shared.php`, while `T-089` said it did not, and kept
the Peer surface in `lang/en/accesses.php`, which `T-096` follows. ~~Which file
holds it.~~ Answered 17 September 2026 (`D-020`): `T-089` creates
`lang/en/shared.php`, the four state sentences are
`shared.vendor_notice.reasons.*` there beside the notice's buttons and flashes,
and each provider's own sentences stay under `accesses.vendor.<provider>.*`, as
this task's rows already are.
