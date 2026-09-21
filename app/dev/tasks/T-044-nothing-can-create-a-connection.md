---
id: T-044
title: Connect a storage account, from onboarding or from a settings page
stream: storage
status: done
owner: claude
estimate: L
depends: T-067, T-093
blocks: T-028, T-090, T-091, T-094, T-096, T-098, T-100, T-141, T-151, T-152, T-153
---

# T-044 — Connect a storage account, from onboarding or from a settings page

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016`, the owner's BYO blueprint and the developer review of the same day,
> and amended on 17 September 2026 by `D-018`: every provider is in the beta
> release, and every tier a creator can hold is offered with Qori's
> recommendation and that tier's limitations on screen before they connect.
> Amended again the same day by `D-021`, after a designer's review of the
> storage drafts: each tier shows its recommendation, at most three essential
> limitations and a disclosure holding the rest, all above Connect; the
> disconnect Dialog names the Series it affects and says what happens to people
> already let in; and a reconnect that returns a different account is held for
> the creator to confirm. Amended on 18 September 2026 by `D-025`: the Episode
> refusal applies only where an Episode's `content` is an item id that means
> nothing without the creator's account, `EpisodeProvider::isAccountBound()` —
> Dropbox today, Google Drive and OneDrive when they land — so a pasted join
> link, a `link` row and a Vimeo id are never refused. Amended on 19 September
> 2026 by `D-033`: a provider is addressed by its slug, `google-drive`, the
> Connect button is the begin step, `share.connections.begin`, and the landing
> is addressed by its vendor, `u/connections/google/finalise`, one address for
> Google Drive and YouTube; and the same day by `D-022` and `D-034`: the
> landing's words are read in the Google folder and answered as a
> `ConnectionLanding`, as `T-113` did for Stripe, and every connector timeout
> is a budget the vendor's client may only shorten. It replaces the draft of
> 11 September 2026 wholesale; what that draft decided and what `D-016`
> superseded is under Notes.

## Why

The `connections` table exists with encrypted `access_token` and
`refresh_token` casts, `expires_at`, `revoked_at`, `isUsable()`, `hasExpired()`
and `revoke()` (`app/Models/Connection.php:53-112`), and **nothing in the
product creates, renews or reconnects one**: no route, no controller, no page
(`docs/flows/storage.md:7-8`), and outside the model nothing reads
`refresh_token` or calls `hasExpired()`. `ConnectionProvider` names Dropbox,
Vimeo, Zoom and Teams and no Google (`app/Enums/ConnectionProvider.php:12-21`).
`EpisodeService::add()` checks that the provider is permitted for the type
(`guardEpisodeType()`, `app/Services/EpisodeService.php:389-407`, called from
`:57`) and nothing about whether the
Group has that provider connected, so a creator can publish a Dropbox Episode
that no Peer will ever open — its path opens only through the creator's token
(`app/Integrations/Dropbox/DropboxStorage.php:31-38`) — and the Peer is who
finds out. The Integrations page renders Stripe alone
(`app/Http/Controllers/Share/IntegrationsController.php:29-76`), and its own
docblock (`:17-20`) and `Integrations.vue:31` say storage joins it here. Part
three of creator setup promises "Connecting Dropbox or Google Drive is coming"
(`lang/en/groups.php:68`, `resources/js/pages/share/setup/Storage.vue:36`).

Afterwards, the Integrations page has one section per provider whose connector
is bound: the creator picks the tier of account they hold from every tier that
provider offers, reads what Qori recommends for that tier and what that tier
cannot do before connecting — the few lines that matter most first, the rest
one click away in the same section — connects, reconnects when Qori has lost
access, confirms or cancels a reconnect that came back as a different account,
and disconnects knowing which Series it touches; a daily command keeps the
tokens alive and tells the owner when it cannot; an Episode whose item id
needs an account the Group has not connected is refused to the creator with a
sentence; and setup's part three links here instead of promising. Google
Drive is the first provider wired end to end, and all seven are in the beta
release (`D-018`), so a missing section means a task that has not landed yet,
never a provider Qori declined. `T-091` fills each section's slot with the
container and the grants that need the creator; every other provider adds its
own OAuth details, tier copy and connector in its own task.

## Decisions taken to make this specifiable

**The settings page is the deliverable; setup links to it and leaves a
forwarding address.** One OAuth round trip, one implementation
(`T-075` said so; `SetupController::storage()`,
`app/Http/Controllers/Share/SetupController.php:88-107`). The storage part
stores `route('share.setup.storage')` through a new `ConnectionsDestination`,
the twin of `PaymentsDestination` (`app/Support/PaymentsDestination.php:7-31`), and the
OAuth landing takes it once, before anything else and whatever happens, as
Stripe's landing does (`PaymentsFinaliseController.php:38`): a creator who
connects from setup lands back in setup, and a landing refused for its state
(`errors.connections.oauth_state`), its scope
(`errors.connections.scope_declined`) or a failed exchange
(`errors.connections.exchange_failed`) leaves it spent, so the fresh start
from Integrations each of those errors sends the creator to stays on
Integrations. The one outcome that needs it afterwards, a held account change,
puts back what it took (below).

**A section appears only for a provider with a bound `ConnectsAccounts`
connector, and this task binds Google Drive alone.** A section that says
"coming" is the line this task removes from setup, moved. All seven providers
are in the beta release (`D-018`), so the page is a build order and not a
shortlist: every provider gets its section before beta, and nothing here
withholds one. `ProviderTier` carries Google's two tiers; each provider task
adds its own cases beside its connector, its recommendation and limitation
copy, its `ProviderSections::ESSENTIAL` entry, its `disconnect.in_qori` and
`account_change.in_qori` lines and its `ConnectionProvider` case where one is
missing, with that case's `vendor()` arm (`D-033`), reading the
blueprint's summary table for the names. `T-090` makes YouTube a connection
of its own (`ConnectionProvider::YouTube`), and the unique `(group_id, provider)`
index (`database/migrations/2026_09_08_000000_create_qori_schema.php:193`)
allows it beside Google Drive. Naming Dropbox's or Zoom's tiers here would
decide them ahead of `T-096` and `T-141`, which add them beside their
connectors once `T-095` and `T-122` have run.

**The tier is chosen before Connect, posted with it, stored in
`connections.settings['tier']`, and changeable afterwards.** `D-016` says the
limitations are stated on screen before the connection is made, so the
dropdown gates the button; a creator who picked wrong changes it with one PATCH
rather than a disconnect.

**Every tier a creator can hold is offered, and no tier is withheld because
the vendor's rules make the sharing weaker than a creator might assume**
(`D-018`). Both of Google's tiers are in the dropdown here, the legacy free
edition of G Suite among them under `google_workspace`, and each provider task
adds every tier its provider sells, including Vimeo Free, Zoom Basic and
personal Microsoft 365. The platform a creator brings, and its rules, are the
creator's own — that is what bring-your-own storage means, and refusing the
connection would be Qori imposing its security model on somebody else's files,
which `D-004` already declined to do. A tier is never a reason to fail a
request: nothing in `ConnectionService`, `BeginConnectionRequest` or
`ProviderSections` branches on which tier was picked beyond which copy it
shows.

**Each tier entry carries what Qori recommends, in one sentence, and what that
tier cannot do, split into the lines that matter most and the rest.** The
owner, 17 September 2026: "we only advice what is recommended not a handoff
approach" (`D-018`). Limitations alone read as a disclaimer — true,
unactionable, and easy to scroll past — and a recommendation alone hides the
thing the creator will be caught by. Google Drive's two tiers carry twelve and
seventeen limitation lines, and every limitation listed above Connect as one wall is what
a designer's review of the storage drafts on 17 September 2026 found, so
`D-021` rule 4 splits them. `ProviderSections` returns per tier `recommended`
(the sentence), `essential` (an ordered list of at most
`ProviderSections::MAX_ESSENTIAL` lines, common and tier lines together) and
`more` (every other line, in key order). `ProviderSection.vue` renders the
recommendation, then the essential list, then one disclosure holding `more`,
closed by default and labelled with its count, **all above the Connect
button**, and keeps the same three blocks after connecting. `D-018`'s promise
stands unchanged: every line for the tier is on the page, in the same section,
before Connect — none is dropped, moved to a link, or left for after the
connection is made — and a test checks that `essential` and `more` together
are exactly the tier's lines.

**Which lines are essential is an ordered constant, not a flag in the lang
file.** `ProviderSections::ESSENTIAL` maps provider → tier → keys relative to
`connections.providers.<provider>.limits.`, in the order shown. Essential means
`D-021`'s three things, in that order: what a Peer needs (an account); what
stops sharing outright on that tier (an admin who must allow outside sharing,
Vimeo Free's Public-only videos, a plan that may refuse adding people, a
recording cut off for everyone but the creator); and the one-folder-per-Series
rule. Everything else goes in `more`. Google Drive's entry, chosen by those
criteria: `google_free` is `common.accounts`, `common.folder` — nothing on a
personal account stops sharing outright, so it has two; `google_workspace` is
`common.accounts`, `google_workspace.external_sharing`, `common.folder`.
`google_workspace.admin_apps` stays in `more` because Google refuses it at
consent and the landing says so (`errors.connections.admin_blocked`), while an
admin who has turned outside sharing off is only found when a grant fails.
Each provider task adds its own entry beside its tiers, and a test fails when
a listed key does not exist or a tier lists more than `MAX_ESSENTIAL`. No
component under `resources/js/components/ui` discloses content today (alert,
avatar, badge, breadcrumb, button, card, checkbox, dialog, dropdown-menu,
input, input-otp, label, separator, sheet, sidebar, skeleton, sonner, spinner,
tabs, textarea, tooltip), so this task adds shadcn-vue's `collapsible` over
`reka-ui`'s Collapsible primitives (`package.json:22`), the way `tabs/` wraps
`TabsRoot` (`resources/js/components/ui/tabs/Tabs.vue`).

**Begin is a POST under `/g/{group}` that names the service, owner-only; the
landing is a GET at `u/connections/{vendor}/finalise` that names the vendor,
exact path** (`D-033`). Google matches `redirect_uri` against the client's
registered list exactly
(https://developers.google.com/identity/protocols/oauth2/web-server), so the
Group cannot be in the path — the same reason Stripe's landing sits at
`u/payments/stripe/finalise` (`routes/settings.php:52-60`,
`app/Http/Controllers/Settings/PaymentsFinaliseController.php:15-27`). The address a vendor matches is the one
registered in that vendor's console, so the landing names whose sign-in it
finishes, never the service being connected: Google Drive lands on
`u/connections/google/finalise`, and so does `T-090`'s YouTube — one Google
landing, registered once on Google's client for both. Begin names the service,
because that is what the creator connects, each with its own tier and scopes:
`POST g/{group}/connections/google-drive/begin`, the stored `google_drive`
reaching the URL through `ConnectionProvider::slug()`. The step says `begin`
in its URL, its route name and its action (`share.connections.begin`,
`ConnectionsController::begin()`), as the landing's say `finalise`. The Group,
provider, tier, nonce and PKCE verifier travel in the session under one key,
as `PaymentsService::OAUTH_SESSION` does (`app/Services/PaymentsService.php:31`,
`:82-89`), so the landing learns which service it is finishing from the
session, never from its path. It takes `ConnectionsDestination` before
anything can throw, finds the Group in the session, checks the person owns it,
refuses a landing whose vendor is not the pending provider's `vendor()`
exactly as it refuses a mismatched state, and only then hands the landing to
the pending provider's connector, which spends the code
(`PaymentsFinaliseController.php:38-59`). The landing takes `finalise` per
`D-032`. Only the owner connects, changes a tier or disconnects: project-plan
§15, `PaymentsController::guardOwner()`
(`app/Http/Controllers/Share/PaymentsController.php:74-82`), `D-012`. An admin
reads a note where the button would be.

**The landing's words are the vendor's, so the vendor's folder reads them and
answers in Qori's** (`D-022`), as `T-113` did for Stripe: the controller hands
`$request->query()` to the Service, and the Service hands it on to the
connector, which is where Stripe's
`finaliseOnboarding(array $landing, string $expectedState): OnboardingOutcome`
reads its own (`app/Integrations/Contracts/SellsSeries.php:40-49`,
`app/Data/OnboardingOutcome.php`). `ConnectsAccounts::finaliseConnection()`
takes the landing, the pending `state`, the `redirect_uri` begin sent, the
PKCE verifier and a timeout budget, spends the code and answers a
`ConnectionLanding`: `Connected` with the tokens, `Declined`, `AdminBlocked`,
`ScopeDeclined`, `NotFromQori`, or `Failed` with the vendor's own code as
`upstream`. It never throws for anything the landing or the token endpoint
says, so `ConnectionService::finaliseConnection()` decides what each status
means for the Group without knowing a Google word, and maps each to what this
draft already names: `Declined` is the toast `connections.declined` with
nothing written; `NotFromQori` is `errors.connections.oauth_state`, 403;
`AdminBlocked` is `errors.connections.admin_blocked`, 403; `ScopeDeclined` is
`errors.connections.scope_declined`, 403, the connector having revoked the
short token first; `Failed` is `errors.connections.exchange_failed`, 502,
through `AppException::upstreamUnavailable()` carrying the landing's
`upstream`; `Connected` goes on to the identity read and the write below.
`GoogleAccounts` reads `error=access_denied`, `admin_policy_enforced` and
`org_internal`, the `code`, and the granted `scope`, and no Google word
reaches `app/Services` or the controller. `T-092`'s identity landing takes the
same shape as `IdentityLanding`.

**`state` is bound to the session with `hash_equals`, and PKCE is sent when
the connector says it supports it** (provisional — see below). The connector
compares the landing's `state` with the pending one, as
`Connect::finaliseOnboarding()` does
(`app/Integrations/Stripe/Connect.php:74-151`), before it spends anything. The
verifier is kept beside the nonce; Google's authorization endpoint accepts
`code_challenge` with `S256` per the web-server page, and this task's own
round trip confirms it against the real client — `T-093` takes its tokens
from the OAuth 2.0 Playground (its step 2), so the spike never exercises
Qori's client.

**The creator's connect asks Google for
`https://www.googleapis.com/auth/drive.file` and nothing else, with
`access_type=offline`, `prompt=consent` and `include_granted_scopes=true`, and
the identity is read through `about.get`.** `drive.file` is the scope Google
classes non-sensitive and recommends
(https://developers.google.com/workspace/drive/api/guides/api-specific-auth);
asking for `openid email` as well, for the account name, would put a second
permission on the creator's consent screen under granular consent
(https://developers.google.com/identity/protocols/oauth2/resources/granular-permissions)
for an identity `about.get` already gives. The project's consent screen
declares three scopes — `drive.file`, and the `openid` and `userinfo.email`
that `T-092`'s Peer sign-in asks for on the same client
(`docs/planning/vendor-accounts.md:158-164`) — and each request names only
its own: declaring a scope asks nobody for it.
`GET drive/v3/about?fields=user(permissionId,emailAddress,displayName)`, the
mask `T-093`'s step 2 uses, answers under `drive.file`
(https://developers.google.com/workspace/drive/api/reference/rest/v3/about/get);
`external_id` takes `permissionId`, and `account_name` takes `emailAddress`,
or `displayName` when `emailAddress` is absent, which the User resource says
it may be
(https://developers.google.com/workspace/drive/api/reference/rest/v3/User) —
the name a creator recognises on the page either way, while sameness is
decided by the id alone. A response with no `permissionId`, or with neither
name, is a failed identity read, and nothing is written (provisional until
`T-093`'s `about-get.json` shows the fields, see below).
`prompt=consent` because Google issues a refresh token on the first consent
only unless asked again (web-server page), and a reconnect is exactly the case
that needs one.

**The granted `scope` is checked in the connector, before the Service sees a
token.** Granular consent can let a person untick a scope, though Google
shows no checkbox for a request naming one scope that is not a sign-in scope
(granular-permissions page above), so a token without `drive.file` should not
come back, and the check is the guard for the day one does:
`GoogleAccounts::finaliseConnection()` compares the token response's `scope`
with its `requiredScopes()`, revokes a token without `drive.file` at Google,
best effort, and answers `ScopeDeclined`, so the creator is told and nothing
is written or held.

**Reconnecting the same account refreshes the tokens and keeps the row at
once; a reconnect that returns a different account is held until the creator
confirms it.** Same or different is `external_id` against the identity that
comes back, compared for any existing row, disconnected ones included, because
what was picked with the old account needs picking again either way. `D-021`
rule 3: a change whose effect on people is live is shown before it applies. So
when the identity differs, `finaliseConnection()` writes nothing to the row. The new
tokens, the account, the tier and the previous `external_id` are kept in the
session under `ConnectionService::ACCOUNT_CHANGE_SESSION`, encrypted with
`Crypt::encryptString()` — the session is not encrypted
(`config/session.php:50`, `SESSION_ENCRYPT` false) and the tokens are
encrypted everywhere else they rest (`app/Models/Connection.php` casts) — for
`ACCOUNT_CHANGE_MINUTES` (provisional). The landing sends the owner to
`share/settings/ConnectionAccountChange`, which names the account the Series
use, the account just signed in with, and every Series using that provider with
its count of Peers with access, and says what switching does. **Switch** applies
what the landing applied before this rule: tokens replaced, `external_id`,
`account_name` and tier written, reconnect state cleared, and
`ConnectionReconnected` raised with `sameAccount` false, so `T-091` marks the
containers for a new pick. What the page says about people already let in
follows `T-091` and `T-094` as drafted, in `connections.providers.<provider>.account_change.in_qori`:
`reconnected()` leaves `granted` rows alone and sends the rest to
`needs_creator` with `ERROR_CONTAINER_REPICK`; a `granted` row's next re-check
reads the old folder's permission with the new account's token, which Google
answers as gone (`T-094`'s `checkGrant()`, `pending(ERROR_PERMISSION_GONE)`),
so `verify()` falls through to `attempt()`, which finds the container `repick`;
the reader Qori added stays on the old folder, and after the switch Qori has no
token for that account to take them off. **Keep** forgets the hold and changes nothing on the
row; it tells the vendor to revoke the held token, best effort, as the scope
refusal does, so the account the creator did not choose is not left listing
Qori. A hold older than `ACCOUNT_CHANGE_MINUTES` is forgotten when read and
applies nothing, and the creator is told to connect again. The landing has
already taken `ConnectionsDestination` when it holds, so it puts back what it
took; Switch, Keep and an expired hold each take it, so a connect started from
setup still returns there and no destination outlives the choice (the lesson
of `D-017`). Both paths dispatch `App\Events\ConnectionReconnected` with
`sameAccount` — the same account at the landing, a different one at Switch;
this task registers no listener. `T-091` registers
`App\Listeners\ResumeGrantsAfterReconnect` on it, and that listener is what
calls `VendorAccessService::reconnected(Connection, bool $sameAccount)`: same
account, every `needs_creator` grant of that provider goes back to `pending`
and is retried at once; a different account marks the Group's containers for
that provider for re-pick and tells the creator which Series need it. Until
the reconnect, a connection that `needsReconnect()` is what holds that
provider's grants at `needs_creator` — the state the creator resolves — and
`isLive()` is the test `T-091`'s ensure step reads. The developer review of
16 September 2026 asked for the two shapes to be told apart.

**This task creates no `vendor_grants` row and marks nothing `granted`; its
three connection states map onto the stream's `VendorGrantStatus` vocabulary
rather than adding to it.** A connection is `not_connected`, `connected` or
`needs_reconnect` on the page. `connected` says nothing about any Peer's
access — `granted` is `T-091`'s to set, per provider, when the Peer can open
the container, which is never API acceptance alone. `needs_reconnect` is the
one state here that a grant row reflects: `T-091`'s ensure step reads
`isLive()` false as `needs_creator` (the creator resolves, by reconnecting),
and the Integrations page's `needs_reconnect` sentence is where that creator
is sent. The reconnect above is one of the stream's three reconciliation
triggers and the only one this task raises; a Peer confirming or changing an
identity (`T-092`) and a container being replaced (`T-091`) are the other
two, all routed through `T-091`'s ensure step. The dedicated-container rule —
one folder per Series, never shared between Series, and sharing the folder
shares everything inside it — is stated here in the limitation copy
(`limits.common.folder` below), one of every Google tier's essential lines, so
it sits above the disclosure before the creator connects; `T-094`'s picker says
it again at the pick (`D-021` rule 4). A vendor call inside a web request here
is the creator's own token exchange, identity read or revoke, given
`REQUEST_TIMEOUT_SECONDS` below as its budget (`D-034`). `T-091`'s
`VendorAccessService` calls `fresh()` before each vendor call, passing its own
shorter `VendorAccessService::REQUEST_TIMEOUT_SECONDS` inside a Peer's
request, and on a timeout its row stays `pending` — nobody needs to act, and
the Peer is told so; and it calls
`markForReconnect($connection, 'unauthorized')` when a vendor answers 401, so
a token Google has revoked is found by the first call that meets it rather
than by the next daily run.

**Disconnect keeps the row, drops the tokens through `revoke()`
(`Connection.php:105-112`), and tells the vendor best effort; every permission
Qori added at the vendor stays, and there is no revoke pass first.** An
Episode pointing at a file keeps pointing at it; Qori's ability to act is what
stops (`T-010`'s purge follows the same rule). What that means for people
already let in was settled by `D-021` on 17 September 2026 (the struck bullet
on `T-091`'s `verify()` under "Before this can be ready"): they keep opening,
nobody new is let in, and their grants wait for the same account to
reconnect. Revoking hundreds of grants before dropping a token would be a long
synchronous request, and `D-016` makes revocation best effort.

**The disconnect Dialog names the Series it affects and says what happens to
people already let in, exactly as the drafts build it** (`D-021` rule 3).
`ConnectionService::impactOf()` reads, locally and with no vendor call, every
Series in the Group holding an Episode whose `EpisodeProvider::connection()`
(`app/Enums/EpisodeProvider.php:50-60`) is the connection's provider, with each
Series' count of active Accesses (`Access::scopeActive()`,
`app/Models/Access.php:221`); the Dialog lists them, or says none uses the
provider yet, as the Stripe Dialog already carries a server-side count
(`pricedSeriesCount`, `Integrations.vue:50`, `:224`; `T-064`). Until `T-094` adds
`EpisodeProvider::GoogleDrive`, Google Drive's list is always empty. What the
sentence says follows from what is specified, not from what would be pleasant:

- Here, Qori drops its own tokens and asks the vendor to revoke them, best
  effort, and takes nothing away at the vendor: the creator's files stay, and
  every reader Qori added stays on the folder in the creator's account until
  the creator removes them there.
- In `T-091`, with the connection not `isLive()`, the ensure step calls that
  vendor for nothing. A grant for a Peer not yet let in reaches `attempt()` and
  becomes `needs_creator` with `ERROR_CONNECTION_UNUSABLE`; `verify()` leaves a
  `granted` or `awaiting_acceptance` row and its `checked_at` as they are; and
  Open on a `granted` row still answers the provider's `openLink()`, which
  reads what Qori stored and makes no call. So a Peer already let in keeps
  opening from Qori, nobody new is let in, and a revoke try counts as failed,
  so a Peer whose access ends meanwhile stays on the folder.
- Reconnecting the same account afterwards raises `ConnectionReconnected` with
  `sameAccount` true: `T-091` sets every `needs_creator` row due at once, so
  the Peers who were waiting are let in, and resets the revokes that failed
  while disconnected, so the sweep takes anyone whose access ended off the
  folder.

The first sentence is the same for every provider and lives in
`connections.disconnect_body`; what happens inside Qori depends on how a
provider grants and opens, so it is a line per provider,
`connections.providers.<provider>.disconnect.in_qori`, written here for Google
Drive and by each provider task for its own. `disconnect_body` says that
nobody Qori let in is removed, because no provider's disconnect removes
anyone.

**A connector says whether its tokens need renewing on a schedule**,
`ConnectsAccounts::refreshesOnSchedule()`, because the vendors differ. Google
refresh tokens die after six months unused, past 100 live tokens per account
per client, on revocation, and after seven days while the Cloud app is in
Testing (https://developers.google.com/identity/protocols/oauth2;
https://support.google.com/cloud/answer/15549945); Microsoft's last 90 days
and are replaced on every use
(https://learn.microsoft.com/en-us/entra/identity-platform/refresh-tokens);
Zoom's last 90 days and rotate, and a concurrent refresh invalidates one
(https://developers.zoom.us/docs/integrations/oauth/). Dropbox refresh tokens
do not expire (https://developers.dropbox.com/oauth-guide) and Vimeo issues
none and forbids extending a token's duration
(https://developer.vimeo.com/api/authentication;
https://vimeo.com/legal/service-terms/api). So it is true for Google,
Microsoft and Zoom and false for Dropbox and Vimeo. **When Qori acts on that
— the daily command, the on-demand refresh, the lock and the email — is
`T-151`'s**, cut from this task on 20 September 2026; this task builds the
columns those write to and the connector method they call.

**An Episode whose item id means nothing without a connected account is
refused at add** (`D-025`) — `T-152`'s, cut from this task on 20 September
2026, which is why `T-123` left this task's `depends:` with it. The refusal
reads `ConnectionService::connectorFor()` and `Connection::isLive()`, both
built here, and the two sentences it shows are that task's copy.

**Refusals Google reports at consent are mapped to a sentence; the rest are
`T-094`'s.** `admin_policy_enforced` and `org_internal` arrive in the landing's
`error` parameter (web-server page) and mean the creator's admin blocks Qori;
`GoogleAccounts` answers them `AdminBlocked`, and the Service says
`errors.connections.admin_blocked`. Everything else about a Workspace policy
surfaces only when a grant fails (`T-093`'s Workspace pass, step 17, decides
which is which: rows c, d and e at connect, the rest at a grant).

**Vendor facts that appear in copy come from `config/qori.php`, never twice.**
Google's 15 GB free storage
(https://support.google.com/googleone/answer/9312312), the five-day review of a
flagged file (https://support.google.com/drive/answer/2463328) and the 24-hour
admin propagation
(https://knowledge.workspace.google.com/admin/drive/manage-external-sharing-for-your-organization)
are interpolated.

**The landing needs no reachability allow-list entry.** The list has been
empty since `T-113` (`config/qori.php:464-465`), and the scan counts a
`route()` naming a route anywhere in `app/` or `tests/` as a link to it
(`app/Support/Reachability.php:154-171`, `:239-242`):
`ConnectionsController::begin()`'s
`route('connections.oauth.finalise', $provider->vendor())` is that link, as
`PaymentsController::begin()`'s `route('payments.oauth.finalise')` is for
Stripe's landing (`app/Http/Controllers/Share/PaymentsController.php:41`).

**Every provider section is built without calling its vendor, so one vendor
that cannot be read cannot take the page down** (`R-004`, Notes).
`ProviderSections::props()` reads the `connections` rows, the lang file and
`impactOf()`'s local query, and nothing else: a section's status comes from
the row — `needs_reconnect` is written by the refresh command or a vendor 401,
never discovered while the page renders — and no connector method is called
to draw it. So a vendor that is down changes no section, and every section's
Connect, tier change and disconnect keep working. Stripe's section is the one
that still reads its vendor on every render; whether that is fixed here is
the stream owner's (below).

## Preconditions

**Data this task verifies against:** a clean database. For the browser check,
a Group whose owner is signed in, with no connection.

**Equipment:** a Google Cloud project with the Drive API enabled and an OAuth
client of type Web application whose authorised redirect URIs include
`http://localhost:8001/u/connections/google/finalise`, and
`https://useqori.com/u/connections/google/finalise` in production — one
address per environment for Google Drive and `T-090`'s YouTube alike
(`D-033`); the client id and secret in `.env` as `GOOGLE_CLIENT_ID` and
`GOOGLE_CLIENT_SECRET`; a consent screen declaring `drive.file`, and the
`openid` and `userinfo.email` `T-092` uses on the same client
(`docs/planning/vendor-accounts.md:158-164`), of which the creator's connect
requests `drive.file` alone. Publishing status Testing is enough for the round
trip; **In production** is the owner's prerequisite for release, not for this
task (`docs/planning/release-prerequisites.md:20`), because while the app is
Testing every refresh token dies after seven days
(https://support.google.com/cloud/answer/15549945), and the report records
which status the round trip ran under. A visible browser for one real round
trip. `T-067` done, which it is; `T-093` done, whose fixtures the Tests read
and whose Q1 decides whether `drive.file` stands; `T-123` done, which adds
`EpisodeProvider::Link` beside the arm this task adds.

**Spike:** every Google body this task names is one of `T-093`'s fixtures
under `tests/Fixtures/google/`: `oauth-token.json` and `about-get.json` from
its step 2, and `oauth-refresh.json`, `oauth-revoke.txt` and
`errors-oauth-token-400-invalid_grant.json` from its step 15. Nothing under
Code names a response field those files do not show. The one exception is
declared: Google shows no checkbox when a request names one scope that is not
a sign-in scope
(https://developers.google.com/identity/protocols/oauth2/resources/granular-permissions),
so `T-093` expects to observe no scope-declined token and keeps
`oauth-token-scope-declined.json` only if its screen offered one. When it did
not, this task adds that file itself: `oauth-token.json` with `scope` edited
by hand to `openid https://www.googleapis.com/auth/userinfo.email` — what
`include_granted_scopes=true` could carry from `T-092`'s sign-in on the same
client, without `drive.file` — and a row in `tests/Fixtures/google/README.md`
marking it edited, not observed. `T-093` takes its tokens from the OAuth 2.0
Playground, so what Google does with Qori's own client's `code_challenge` and
`prompt=consent` is this task's round trip to observe (see below).

## Scope

**In:**

- Provider sections on the Integrations page: a dropdown holding every tier the
  provider offers, the chosen tier's recommendation sentence, its essential
  limitation lines and a disclosure holding the rest, all above Connect;
  status, Connect, Reconnect, Disconnect with a Dialog naming the Series that
  use the provider, an admin's note, and an empty slot per section for
  `T-091`'s container and grants.
- `ProviderSections::ESSENTIAL` with Google Drive's entry, and the
  `collapsible` UI component the disclosure is built from.
- The generic machinery: `ConnectsAccounts`, `ConnectionService`, begin and
  landing, state and PKCE, the landing read in the vendor's folder and
  answered as a `ConnectionLanding` (`D-022`), token exchange into
  `connections`, tier update, disconnect and its impact read,
  `ConnectionReconnected`, `ConnectionsDestination`, and `ConnectionProvider`'s
  slug and vendor with the `{provider}` binder (`D-033`).
- The held different-account reconnect: the session hold, the confirmation
  page, Switch and Keep.
- The Google Drive connector, `ConnectionProvider::GoogleDrive`,
  `ProviderTier` with both of Google's tiers, `lang/en/connections.php` with
  Google's copy: a recommendation and the limitations per tier.
- Setup's part three: the link and the copy.
- `docs/flows/storage.md` (Connections), `docs/flows/onboarding.md` (part
  three and its forwarding address), `docs/tinker/connections.md`.

**Out:**

- The Google Picker, folder choice, `EpisodeProvider::GoogleDrive` and its
  `isAccountBound()` arm, `EpisodeType::allowedProviders()` and the grant
  itself (`T-093`, `T-094`).
- The token renewal this task's row is shaped for: `AdvisoryLock`,
  `ConnectionService::fresh()`, `refresh()`, `refreshDue()` and
  `markForReconnect()`, `Connection::markForReconnect()` and
  `scopeRefreshable()`, `qori:connections:refresh` and the reconnect email
  (`T-151`, cut from this task on 20 September 2026). `ConnectsAccounts`
  declares `refresh()` and `refreshesOnSchedule()` here and `GoogleAccounts`
  implements them here, because a connector that does not implement its own
  interface does not compile; deciding _when_ to call them is `T-151`'s.
- The refusal in `EpisodeService::add()` for an account-bound provider, and
  `EpisodeProvider::isAccountBound()` (`D-025`) — `T-152`, cut from this task
  the same day, which takes `T-123` out of this one's `depends:` with it.
- `series_containers`, `vendor_grants`, the ensure step and the reconcile
  sweep (`T-091`); `App\Listeners\ResumeGrantsAfterReconnect`, which acts on
  `ConnectionReconnected`.
- Dropbox, Vimeo, Zoom, OneDrive and YouTube connectors, their tiers, their
  recommendation and limitation copy, their `ProviderSections::ESSENTIAL`
  entries and their `disconnect.in_qori` and `account_change.in_qori` lines
  (`T-096`, `T-090`, `T-141`, `T-098`) — Vimeo Free, Zoom Basic and personal
  Microsoft 365 among them, each stating its limits rather than being refused
  (`D-018`). Zoom's registrants are `T-100`'s.
- What a Vimeo or YouTube picker needs from a connection (`T-090`); no Vimeo
  Episode is refused here (`D-025`).
- Series that hold a `T-091` container and no Episode yet in the disconnect and
  account-change lists: `series_containers` is `T-091`'s table (see below).
- The Peer's own vendor identity (`T-092`).
- Anything the deauthorise webhooks a vendor may send; `PaymentsService::forget()`
  has no analogue here yet.
- Moving files between accounts, or deleting anything at a vendor.

## Files

| Path                                                                                                                                                                                                                                       | Change | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `database/migrations/2026_09_20_000000_add_reconnect_state_to_connections.php`                                                                                                                                                             | new    | Four columns; `settings` backfilled and given its default                                                                                                                                                                                                                                                                                                                                                                                 |
| `app/Models/Connection.php`                                                                                                                                                                                                                | edit   | Fillable, casts, `needsReconnect()`, `isLive()`, `tier()`                                                                                                                                                                                                                                                                                                                                                                                 |
| `app/Enums/ConnectionProvider.php`                                                                                                                                                                                                         | edit   | `GoogleDrive`, `connectable()`, `slug()`, `fromSlug()`, `vendor()`, `vendors()` (`D-033`)                                                                                                                                                                                                                                                                                                                                                 |
| `app/Enums/ProviderTier.php`                                                                                                                                                                                                               | new    | `GoogleFree`, `GoogleWorkspace`; each provider task adds its own                                                                                                                                                                                                                                                                                                                                                                          |
| `app/Enums/ConnectionLandingStatus.php`                                                                                                                                                                                                    | new    | What a landing came to, in Qori's words: six cases                                                                                                                                                                                                                                                                                                                                                                                        |
| `app/Integrations/Contracts/ConnectsAccounts.php`                                                                                                                                                                                          | new    | The contract                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `app/Integrations/Google/GoogleAccounts.php`                                                                                                                                                                                               | new    | The first connector: reads Google's landing (`D-022`) and sets its own timeout (`D-034`)                                                                                                                                                                                                                                                                                                                                                  |
| `app/Data/ConnectionTokens.php` `app/Data/ConnectedAccount.php` `app/Data/ConnectionLanding.php` `app/Data/RefreshResult.php` `app/Data/ConnectionOutcome.php` `app/Data/ConnectionImpact.php` `app/Data/HeldAccountChange.php`            | new    | Shapes between the layers; `ConnectionLanding` is a connector's answer to a landing, and the last two are the Series a provider touches and the held different-account reconnect                                                                                                                                                                                                                                                          |
| `app/Services/ConnectionService.php`                                                                                                                                                                                                       | new    | Begin, finalise, tier, disconnect, impact, the account-change hold with switch and keep                                                                                                                                                                                                                                                                                                                                                   |
| `app/Support/ConnectionsDestination.php` `app/Support/ProviderSections.php`                                                                                                                                                                | new    | The forwarding address; the page props, `ESSENTIAL` and `MAX_ESSENTIAL`                                                                                                                                                                                                                                                                                                                                                                   |
| `app/Events/ConnectionReconnected.php`                                                                                                                                                                                                     | new    | `T-091`'s `ResumeGrantsAfterReconnect` listens                                                                                                                                                                                                                                                                                                                                                                                            |
| `app/Http/Controllers/Share/ConnectionsController.php`                                                                                                                                                                                     | new    | `begin()`, `update()`, `disconnect()`, `accountChange()`, `switchAccount()`, `keepAccount()`                                                                                                                                                                                                                                                                                                                                              |
| `app/Http/Controllers/Settings/ConnectionFinaliseController.php`                                                                                                                                                                           | new    | The landing, invokable: takes `ConnectionsDestination` first and hands `$request->query()` to the Service; a held account change redirects to the confirmation page                                                                                                                                                                                                                                                                       |
| `app/Http/Requests/Share/BeginConnectionRequest.php` `app/Http/Requests/Share/UpdateConnectionRequest.php`                                                                                                                                 | new    | `tier`                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `app/Http/Controllers/Share/IntegrationsController.php`                                                                                                                                                                                    | edit   | `providers` prop from `ProviderSections`                                                                                                                                                                                                                                                                                                                                                                                                  |
| `app/Http/Controllers/Share/SetupController.php`                                                                                                                                                                                           | edit   | `storage()`: the link and the forwarding address                                                                                                                                                                                                                                                                                                                                                                                          |
| `app/Providers/IntegrationServiceProvider.php`                                                                                                                                                                                             | edit   | `account-connectors` tag beside `media-providers` (`:35-39`)                                                                                                                                                                                                                                                                                                                                                                              |
| `app/Providers/AppServiceProvider.php`                                                                                                                                                                                                     | edit   | `Route::bind('provider', …)` in `boot()`: the `ConnectionProvider` whose slug the path carries, any other value a 404 (`D-033`)                                                                                                                                                                                                                                                                                                           |
| `routes/share/payments.php`                                                                                                                                                                                                                | edit   | Six connection routes; header covers connections                                                                                                                                                                                                                                                                                                                                                                                          |
| `routes/settings.php`                                                                                                                                                                                                                      | edit   | The landing under `/u`, its `{vendor}` limited to `ConnectionProvider::vendors()`                                                                                                                                                                                                                                                                                                                                                         |
| `config/services.php` `config/qori.php` `.env.example`                                                                                                                                                                                     | edit   | `google` block; `connections` block; the two env keys                                                                                                                                                                                                                                                                                                                                                                                     |
| `resources/js/components/share/ProviderSection.vue`                                                                                                                                                                                        | new    | One section: recommendation, essential lines, the disclosure, status, buttons, the disconnect Dialog with its Series list; `#grants` slot for `T-091`                                                                                                                                                                                                                                                                                     |
| `resources/js/components/ui/collapsible/Collapsible.vue` `resources/js/components/ui/collapsible/CollapsibleTrigger.vue` `resources/js/components/ui/collapsible/CollapsibleContent.vue` `resources/js/components/ui/collapsible/index.ts` | new    | shadcn-vue's `collapsible` over `reka-ui`'s `CollapsibleRoot`, `CollapsibleTrigger` and `CollapsibleContent`; nothing under `components/ui` discloses today                                                                                                                                                                                                                                                                               |
| `resources/js/pages/share/settings/ConnectionAccountChange.vue`                                                                                                                                                                            | new    | The held account change: both accounts, the Series list, Switch and Keep                                                                                                                                                                                                                                                                                                                                                                  |
| `resources/js/pages/share/settings/Integrations.vue`                                                                                                                                                                                       | edit   | Renders one `ProviderSection` per `providers` entry                                                                                                                                                                                                                                                                                                                                                                                       |
| `resources/js/pages/share/setup/Storage.vue`                                                                                                                                                                                               | edit   | The link; `copy.later` becomes `copy.connect`                                                                                                                                                                                                                                                                                                                                                                                             |
| `lang/en/connections.php`                                                                                                                                                                                                                  | new    | Copy below                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `lang/en/errors.php` `lang/en/groups.php`                                                                                                                                                                                                  | edit   | `connections.*`; `setup.storage_connect*`                                                                                                                                                                                                                                                                                                                                                                                                 |
| `database/factories/ConnectionFactory.php`                                                                                                                                                                                                 | edit   | `google()` and `needsReconnect()` states                                                                                                                                                                                                                                                                                                                                                                                                  |
| `docs/flows/storage.md` `docs/flows/onboarding.md` `docs/flows/README.md` `docs/tinker/README.md`                                                                                                                                          | edit   | Connections section rewritten, the held account change and the disconnect Dialog's Series read among it; part three's line (`onboarding.md:19`) and the forwarding-address paragraph (`:24-33`), which names `ConnectionsDestination` beside `PaymentsDestination`; the two index rows                                                                                                                                                    |
| `docs/tinker/connections.md`                                                                                                                                                                                                               | new    | A recipe, including reading and expiring a held account change                                                                                                                                                                                                                                                                                                                                                                            |
| `tests/Feature/Share/ConnectionsConnectTest.php` `tests/Feature/Share/ConnectionsDisconnectTest.php`                                                                                                                                       | new    | 16 and 4 cases; the first file's cases 41 to 45 are numbered after case 40, so the numbers other drafts cite stay put                                                                                                                                                                                                                                                                                                                     |
| `tests/Feature/Share/IntegrationsProvidersTest.php` `tests/Feature/Integrations/Google/GoogleAccountsTest.php`                                                                                                                             | new    | 4 and 7 cases: case 20 is withdrawn, and the second file's cases 46 and 47 are numbered after case 45; the second under `tests/Feature/Integrations/<Vendor>/`, as Stripe's shipped `tests/Feature/Integrations/Stripe/ClientTest.php` and the Zoom drafts' tests are                                                                                                                                                                     |
| `tests/Feature/Share/ConnectionAccountChangeTest.php` `tests/Feature/Share/ProviderSectionsTest.php`                                                                                                                                       | new    | 4 and 3 cases; numbered after the refresh command's so the numbers other drafts cite stay put                                                                                                                                                                                                                                                                                                                                             |
| `tests/Feature/Share/SetupStepsTest.php`                                                                                                                                                                                                   | edit   | +2 cases; see Tests                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `tests/Fixtures/google/oauth-token-scope-declined.json`                                                                                                                                                                                    | new    | Only when `T-093` kept none: `oauth-token.json` with `scope` edited by hand (Preconditions)                                                                                                                                                                                                                                                                                                                                               |
| `tests/Fixtures/google/README.md`                                                                                                                                                                                                          | edit   | That file's row, marked edited, not observed; nothing when `T-093` observed one                                                                                                                                                                                                                                                                                                                                                           |
| `tests/Doubles/ConnectsNothing.php`                                                                                                                                                                                                        | new    | A `ConnectsAccounts` whose `provider()` is given in the constructor: `refreshesOnSchedule()` and `supportsPkce()` false, `requiredScopes()` empty, `beginConnection()` `'https://connects-nothing.test'`, `finaliseConnection()` `ConnectionLanding::failed()`, `refresh()` `RefreshResult::unavailable()`, `revoke()` nothing, `identity()` a `LogicException`; a test tags it `account-connectors`; beside `AcceptsEverySnsMessage.php` |

`docs/flows/vendor-access.md` is `T-091`'s and is not created here. Nothing
else that adds an Episode changes, because Dropbox is the one account-bound
provider today: `tests/e2e/support/creator.ts` adds a Vimeo Episode with
nothing connected (`:109-125`) and keeps doing so, and
`tests/Feature/Series/EpisodeRoutesTest.php` and
`tests/Feature/Series/LiveSessionTest.php` add Vimeo, Zoom and Qori-hosted
Episodes only.

## Database

| Table         | Column               | Type        | Null | Default | Index / constraint                                                                                                                                                    |
| ------------- | -------------------- | ----------- | ---- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `connections` | `needs_reconnect_at` | timestamp   | yes  | null    | Set by `markForReconnect()`: a failed refresh, or `T-091`'s vendor 401; cleared by a successful connect                                                               |
| `connections` | `reconnect_reason`   | string(100) | yes  | null    | `invalid_grant` and `refresh_failed` written here; `unauthorized` by `T-091`'s `VendorAccessService` on a vendor 401                                                  |
| `connections` | `refreshed_at`       | timestamp   | yes  | null    | Last successful refresh                                                                                                                                               |
| `connections` | `refresh_failures`   | smallint    | no   | 0       | Consecutive; reset on success                                                                                                                                         |
| `connections` | `settings`           | jsonb       | no   | `'[]'`  | Was nullable with no default (`create_qori_schema.php:191`); the migration writes `'[]'` over every null row before `nullable(false)`; the string default, never `[]` |

`settings` keys this task writes: `tier` (a `ProviderTier` value). Migration:
`database/migrations/2026_09_20_000000_add_reconnect_state_to_connections.php`,
after `T-111`'s `2026_09_17_000000` and the classroom stream's `2026_09_18`
set, and before the two that build on this table, `T-091`'s
`2026_09_20_000100` and `T-092`'s `2026_09_20_000200`.

## Code

```php
namespace App\Enums;

enum ConnectionProvider: string
{
    case GoogleDrive = 'google_drive';   // new; Dropbox, Vimeo, Zoom, Teams unchanged
    /** False for Teams: T-101 stores a pasted link and connects nothing. */
    public function connectable(): bool;
    /** The case as a URL writes it (D-033): the value with '_' replaced by '-', so google_drive is google-drive. The row, lang and config keep the value. */
    public function slug(): string;
    /** The case whose slug() equals $slug exactly, else null, so the stored google_drive finds nothing. What Route::bind('provider') reads. */
    public static function fromSlug(string $slug): ?self;
    /** Whose sign-in the landing finishes, the {vendor} in u/connections/{vendor}/finalise (D-033). A match with no default arm, as
     *  EpisodeProvider::connection() is: GoogleDrive 'google', Dropbox 'dropbox', Vimeo 'vimeo', Zoom 'zoom', Teams 'microsoft'.
     *  T-090 adds YouTube's arm, 'google', and T-098 OneDrive's, 'microsoft', beside their cases. */
    public function vendor(): string;
    /** @return list<string> every case's vendor() once, in case order: the landing's whereIn() constraint. */
    public static function vendors(): array;
}

enum ProviderTier: string
{
    case GoogleFree = 'google_free';
    case GoogleWorkspace = 'google_workspace';
    // Each provider task adds its cases with its connector (T-090, T-096, T-098, T-141);
    // the blueprint's summary table is the source of the names. Every tier the provider
    // sells gets a case, however awkward its limits (D-018); a tier is explained on the
    // page, never left out of the dropdown.
    public function provider(): ConnectionProvider;
    /** @return list<self> */
    public static function forProvider(ConnectionProvider $provider): array;
}

enum EpisodeProvider: string
{
    // CloudflareR2, Dropbox, Vimeo, Zoom, Teams and T-123's Link unchanged; one method added beside connection() (:42-51).
    /**
     * Whether this provider's content is an item id that means nothing without the creator's account, so an Episode on it
     * needs a live connection before it is added (D-025). A match with no default arm, as connection() is: Dropbox true;
     * CloudflareR2, Vimeo, Zoom, Teams and Link false — Vimeo's id plays without the account (VimeoVideos::linkFor(),
     * app/Integrations/Vimeo/VimeoVideos.php:62-86), and a live Episode's join_url is the pasted tier. T-094 adds
     * GoogleDrive's arm, true; T-098 OneDrive's, true; T-090 YouTube's, false.
     */
    public function isAccountBound(): bool;
}

/** How a creator's round trip to a vendor's sign-in ended, in Qori's words (D-022), as OnboardingStatus is for Stripe's. */
enum ConnectionLandingStatus: string
{
    case Connected = 'connected';           // a token came back carrying every requiredScopes() entry
    case Declined = 'declined';             // the creator stopped at the vendor; nothing to store or undo
    case AdminBlocked = 'admin_blocked';    // the account's administrator does not let Qori in
    case ScopeDeclined = 'scope_declined';  // a token came back without a required scope; the connector has revoked it
    case NotFromQori = 'not_from_qori';     // the landing's state is not the one this session sent
    case Failed = 'failed';                 // no token Qori can keep: another error word, no code, a refused or unanswered exchange
}
```

```php
namespace App\Models;

class Connection extends Model
{
    // fillable += needs_reconnect_at, reconnect_reason, refreshed_at, refresh_failures
    // casts   += needs_reconnect_at, refreshed_at => 'datetime'; refresh_failures => 'integer'
    public function needsReconnect(): bool;      // revoked_at !== null || needs_reconnect_at !== null
    public function isLive(): bool;              // isUsable() && ! needsReconnect() — what T-091's ensure step should read
    public function tier(): ?ProviderTier;       // ProviderTier::tryFrom($this->settings['tier'] ?? '')
    // markForReconnect() and scopeRefreshable() are T-151's, on this same class
}
```

```php
namespace App\Integrations\Contracts;

interface ConnectsAccounts
{
    public function provider(): ConnectionProvider;
    public function supportsPkce(): bool;
    /** True for Google, Microsoft and Zoom; false for Dropbox and Vimeo (see Decisions). */
    public function refreshesOnSchedule(): bool;
    /** @return list<string> the scopes a token must carry; finaliseConnection() checks the granted ones against these. */
    public function requiredScopes(): array;
    public function beginConnection(string $redirectUrl, string $state, ?string $codeChallenge, ?string $loginHint): string;
    /**
     * Read the landing the vendor sent the owner back with and spend its code (D-022), as SellsSeries::finaliseOnboarding()
     * does. The landing's words are the vendor's, so they are read here and answered in Qori's; never throws for anything the
     * landing or the token endpoint says. A state that is not $expectedState spends nothing. A token short of
     * requiredScopes() is revoked at the vendor, best effort, and answered scopeDeclined().
     * @param array<string, mixed> $landing the query as the vendor sent it
     */
    public function finaliseConnection(array $landing, string $expectedState, string $redirectUrl, ?string $codeVerifier, int $timeoutSeconds): ConnectionLanding;
    /** Never throws: transport and 5xx are RefreshResult::unavailable(), invalid_grant is ::revoked(). */
    public function refresh(string $refreshToken, int $timeoutSeconds): RefreshResult;
    /** Best effort; a failure is logged. */
    public function revoke(Connection $connection, int $timeoutSeconds): void;
    /** @throws AppException upstreamUnavailable, langKey errors.connections.exchange_failed, upstream the vendor's status or 'connection' */
    public function identity(string $accessToken, int $timeoutSeconds): ConnectedAccount;
}
```

Every `$timeoutSeconds` is a budget the connector's client may only shorten
(`D-034`): the client sets its own timeout on its `Http::` chain and uses
whichever is shorter, its own or the caller's, so a caller inside a person's
request can make a call wait less and never more. The budget travels as a
parameter, as `T-091`'s contract methods take it, because an integration may
not import `App\Services` (`tests/Feature/ArchitectureTest.php:139-147`) and
the numbers live on the service: `ConnectionService::REQUEST_TIMEOUT_SECONDS`
(10) for the landing's exchange, the identity read and the owner's revoke,
`SWEEP_TIMEOUT_SECONDS` (30) for the command, and `T-091`'s own
`VendorAccessService::REQUEST_TIMEOUT_SECONDS` (5) when it calls `fresh()`
inside a Peer's request.

```php
namespace App\Data;

class ConnectionTokens { public function __construct(public string $accessToken, public ?string $refreshToken, public ?CarbonInterface $expiresAt, /** @var list<string> */ public array $scopes) {} public function hasScope(string $scope): bool; }
class ConnectedAccount { public function __construct(public string $externalId, public string $name, public ?string $email = null) {} }
class RefreshResult    { public function __construct(public ?ConnectionTokens $tokens, public bool $revoked = false, public ?string $upstream = null) {} public static function renewed(ConnectionTokens $tokens): self; public static function revoked(?string $upstream = null): self; public static function unavailable(?string $upstream = null): self; public function isRenewed(): bool; }
/** A connector's answer to a landing, built in the vendor's folder; tokens only when Connected, upstream only when Failed. */
class ConnectionLanding { public function __construct(public ConnectionLandingStatus $status, public ?ConnectionTokens $tokens = null, public ?string $upstream = null) {} public static function connected(ConnectionTokens $tokens): self; public static function declined(): self; public static function adminBlocked(): self; public static function scopeDeclined(): self; public static function notFromQori(): self; public static function failed(?string $upstream = null): self; }
/** What a landing came to for the Group. connection is null for declined() alone: the creator stopped at the vendor and nothing was written. */
class ConnectionOutcome { public function __construct(public ?Connection $connection, public bool $first = false, public bool $sameAccount = false, public ?string $previousExternalId = null, public bool $held = false) {} public static function declined(): self; public function isDeclined(): bool; }
/** Local reads only. series: every Series using the provider, ordered by title, each with its count of active Accesses. */
class ConnectionImpact { public function __construct(public ConnectionProvider $provider, /** @var list<array{id: string, title: string, slug: string, peers: int}> */ public array $series) {} public function isEmpty(): bool; }
/** What the session holds while the owner decides; built from the decrypted payload. */
class HeldAccountChange { public function __construct(public string $groupId, public string $connectionId, public ConnectionProvider $provider, public ProviderTier $tier, public ConnectionTokens $tokens, public ConnectedAccount $account, public ?string $previousExternalId, public CarbonInterface $heldAt) {} public function hasExpired(): bool; /* heldAt + ConnectionService::ACCOUNT_CHANGE_MINUTES is past */ }
```

```php
namespace App\Integrations\Google;

/** Endpoints from https://developers.google.com/identity/protocols/oauth2/web-server. */
class GoogleAccounts implements ConnectsAccounts
{
    public const AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/v2/auth';
    public const TOKEN_URL = 'https://oauth2.googleapis.com/token';
    public const REVOKE_URL = 'https://oauth2.googleapis.com/revoke';
    public const ABOUT_URL = 'https://www.googleapis.com/drive/v3/about';
    public const SCOPE_DRIVE_FILE = 'https://www.googleapis.com/auth/drive.file';
    /** Google's own limit on one call (D-034), as Stripe's client sets 20 (app/Integrations/Stripe/Client.php:29, :57); provisional with the Service's numbers. */
    public const TIMEOUT_SECONDS = 20;
    // provider(): GoogleDrive; supportsPkce(): true (provisional); refreshesOnSchedule(): true; requiredScopes(): [SCOPE_DRIVE_FILE]
    // beginConnection():    client_id, redirect_uri, response_type=code, scope, access_type=offline, prompt=consent,
    //                       include_granted_scopes=true, state, login_hint, code_challenge, code_challenge_method=S256
    // finaliseConnection(), in Connect::finaliseOnboarding()'s order (app/Integrations/Stripe/Connect.php:74-151), so a forged or stale
    //                       landing spends nothing; $matches = $expectedState !== '' && hash_equals($expectedState, the landing's state):
    //                       an error whose state is present and does not match → notFromQori(); error=access_denied → declined();
    //                       error=admin_policy_enforced or org_internal → adminBlocked(); any other error word → failed(<the word>);
    //                       no error and ! $matches → notFromQori(); no code → failed();
    //                       POST TOKEN_URL form grant_type=authorization_code, code, client_id, client_secret, redirect_uri, code_verifier
    //                       → access_token, expires_in, refresh_token, scope (space-separated), token_type  [T-093's oauth-token.json];
    //                       a ConnectionException → failed('connection'); a 4xx or 5xx → failed(<status>), logged with Google's error
    //                       word alone, never the body, which may quote the code;
    //                       a granted scope short of requiredScopes() → POST REVOKE_URL with that access token, best effort, then
    //                       scopeDeclined()  [T-093's oauth-token-scope-declined.json]; else connected(new ConnectionTokens(...)).
    // refresh():            POST TOKEN_URL form grant_type=refresh_token, refresh_token, client_id, client_secret
    //                       → access_token, expires_in, scope, token_type; refresh_token absent unless rotated  [T-093's oauth-refresh.json]
    //                       400 with error=invalid_grant → RefreshResult::revoked()  [T-093's errors-oauth-token-400-invalid_grant.json]
    // revoke():             POST REVOKE_URL form token=<refresh or access token>  [T-093's oauth-revoke.txt]
    // identity():           GET ABOUT_URL?fields=user(permissionId,emailAddress,displayName)  [T-093's about-get.json] →
    //                       new ConnectedAccount(externalId: permissionId, name: emailAddress ?? displayName, email: emailAddress);
    //                       no permissionId, or neither name → AppException::upstreamUnavailable(upstream: 'about_incomplete',
    //                       langKey: errors.connections.exchange_failed); a ConnectionException or a 4xx/5xx likewise, upstream 'connection' or the status
    // Every call: ->timeout(min(self::TIMEOUT_SECONDS, $timeoutSeconds)) and no retry(): a code is single-use, and the daily
    // command is a refresh's retry. Client id and secret from config('services.google').
}
```

```php
namespace App\Services;

class ConnectionService
{
    public const OAUTH_SESSION = 'connections.oauth';   // state, code_verifier, group_id, provider, tier
    public const ACCOUNT_CHANGE_SESSION = 'connections.account_change';   // one Crypt::encryptString() payload: HeldAccountChange's fields
    public const ACCOUNT_CHANGE_MINUTES = 10;           // provisional — see below; how long a different-account reconnect waits for Switch or Keep
    public const REQUEST_TIMEOUT_SECONDS = 10;          // provisional (D-034); the budget for the creator's own token exchange, identity read and revoke
    public const SWEEP_TIMEOUT_SECONDS = 30;            // provisional (D-034); no caller waits on it — T-151's command and T-091's sweep read it
    // REFRESH_MARGIN_MINUTES, REFRESH_FAILURES_BEFORE_RECONNECT and LOCK_NAMESPACE are T-151's, on this same class

    /** @param iterable<ConnectsAccounts> $connectors */
    public function __construct(private iterable $connectors, private CurrentGroup $current) {}

    public function connectorFor(ConnectionProvider $provider): ?ConnectsAccounts;   // null → errors.connections.not_available
    /** Puts the session entry, then the vendor URL; login_hint is the owner's email. $redirectUrl, which begin() passes, is
     *  route('connections.oauth.finalise', $provider->vendor()): the vendor, never the provider's slug or value (D-033). */
    public function beginConnection(Group $group, ConnectionProvider $provider, ProviderTier $tier, string $redirectUrl): string;
    /** $vendor is the landing's {vendor}, not a provider (D-033); $landing is the query as the vendor sent it, read by the connector alone.
     *  Reads the pending connect under OAUTH_SESSION: none, one for another Group, or one whose provider's vendor() is not $vendor is refused
     *  exactly as a mismatched state is — AppException::forbidden('errors.connections.oauth_state'), 403, no code spent and nothing written.
     *  Otherwise forgets the entry, then hands $landing to the pending provider's connector with the entry's state and code_verifier,
     *  $redirectUrl and REQUEST_TIMEOUT_SECONDS, and maps its ConnectionLanding:
     *    Declined      → ConnectionOutcome::declined(), nothing written;
     *    NotFromQori   → AppException::forbidden('errors.connections.oauth_state');
     *    AdminBlocked  → AppException::forbidden('errors.connections.admin_blocked');
     *    ScopeDeclined → AppException::forbidden('errors.connections.scope_declined'), the connector having revoked the token;
     *    Failed        → AppException::upstreamUnavailable(devMessage: …, upstream: $landing->upstream, langKey: 'errors.connections.exchange_failed');
     *    Connected     → identity() with REQUEST_TIMEOUT_SECONDS, then the row for the pending provider and tier is upserted, or, when a
     *                    row exists whose external_id differs, the change is held and nothing is written (outcome held true). */
    public function finaliseConnection(Group $group, string $vendor, array $landing, string $redirectUrl): ConnectionOutcome;
    /** The hold for this Group and provider; null when there is none, it cannot be decrypted, or it hasExpired() — an expired one is forgotten here. */
    public function heldAccountChange(Group $group, ConnectionProvider $provider): ?HeldAccountChange;
    /** Writes the held tokens, account and tier to the row exactly as finaliseConnection() writes a connect, dispatches ConnectionReconnected(sameAccount: false, previousExternalId), forgets the hold. Null, with nothing written, when heldAccountChange() is null or names another connection. */
    public function switchAccount(Connection $connection): ?ConnectionOutcome;
    /** Forgets the hold; revoke() at the vendor with the held tokens on an unsaved Connection, best effort, as the scope refusal does. The row is untouched. False when there was no live hold. */
    public function keepAccount(Connection $connection): bool;
    /** The Series using the connection's provider in the current Group: an Episode whose EpisodeProvider::connection() is that provider. No vendor call. */
    public function impactOf(Connection $connection): ConnectionImpact;
    public function updateTier(Connection $connection, ProviderTier $tier): void;
    /** revoke() at the vendor best effort, then $connection->revoke(). */
    public function disconnect(Connection $connection): void;
    // fresh(), refresh(), refreshDue() and markForReconnect() are T-151's, on this same class
}
```

`finaliseConnection()` writes `access_token`, `refresh_token` (kept from the row when the
vendor sent none), `expires_at`, `external_id`, `account_name`,
`settings['tier']`, clears `revoked_at`, `needs_reconnect_at`,
`reconnect_reason`, `refresh_failures`, and dispatches
`ConnectionReconnected` with `sameAccount` true when a row existed for the same
`external_id`. When a row exists and `external_id` differs, it writes none of
that: it puts `Crypt::encryptString(json_encode([...]))` under
`ACCOUNT_CHANGE_SESSION` — group id, connection id, provider, tier, the
`ConnectionTokens` fields, the `ConnectedAccount` fields, the row's
`external_id`, and `held_at` — replacing any earlier hold, and returns an
outcome with `held` true. `switchAccount()` writes the fields above from the
hold, then dispatches `ConnectionReconnected` with `sameAccount` false and the
previous `external_id`. The connector checks the scopes before the Service
sees a token, so a token without `drive.file` is never held: `ScopeDeclined`
arrives with the token already revoked and throws
`AppException::forbidden('errors.connections.scope_declined')`. An
`identity()` that throws leaves nothing written and nothing held.
`impactOf()` reads `Series::query()` in the current Group with an Episode whose
`provider` is one of the `EpisodeProvider` cases whose `connection()` is the
row's provider, and `withCount` of its Accesses under `scopeActive()`.
What a failed refresh does to the row, and who is emailed about it, is
`T-151`'s.

```php
namespace App\Support;

class ConnectionsDestination { public const KEY = 'connections.destination'; public static function remember(string $url): void; public static function take(): ?string; }

class ProviderSections
{
    /** Limitation lines a tier shows above its disclosure, at most: D-021 rule 4's "at most three". */
    public const MAX_ESSENTIAL = 3;

    /**
     * provider value → tier value → keys relative to connections.providers.<provider>.limits., in the order shown.
     * D-021 rule 4: what a Peer needs, what stops sharing outright on that tier, the one-folder-per-Series rule.
     * Each provider task adds its entry beside its ProviderTier cases (T-090, T-096, T-098, T-141).
     * @var array<string, array<string, list<string>>>
     */
    public const ESSENTIAL = [
        'google_drive' => [
            'google_free' => ['common.accounts', 'common.folder'],
            'google_workspace' => ['common.accounts', 'google_workspace.external_sharing', 'common.folder'],
        ],
    ];

    /** One entry per bound connector whose provider is connectable(), keyed by provider value:
     *  name, description, status ('not_connected'|'connected'|'needs_reconnect'), accountName, connectionId,
     *  beginUrl route('share.connections.begin', [group slug, the provider's slug()]) — built here, because the entry's key is the
     *  stored value and a URL built from it is a 404 (D-033),
     *  tiers [{value, label, help, recommended, essential, more, moreLabel}] — every case ProviderTier::forProvider()
     *  returns, none filtered (D-018), each with its own lines so the dropdown switches them before Connect —
     *  tier (the stored tier, else the first),
     *  labels {tierLabel, recommendedLabel, essentialLabel, connect, reconnect, ownerNote},
     *  disconnect {label, title, body, inQori, seriesIntro, series [{title, url, line}], none, confirm, keep} or null, inQori from
     *  connections.providers.<provider>.disconnect.in_qori,
     *  series from ConnectionService::impactOf(), url route('share.series.show'), line connections.series_using.row
     *  through Terminology::choice() with the Series' peers count — every string through Terminology.
     *  No connector method is called: status comes from the row, so a vendor that is down changes no section (R-004). */
    public static function props(Group $group, Terminology $terminology, ConnectionService $connections): array;

    /**
     * Every connections.providers.<provider>.limits.common.* line, then every limits.<tier>.* line, in the lang file's
     * key order, split by ESSENTIAL: essential in ESSENTIAL's order, more in key order. Nothing dropped, nothing twice.
     * A tier with no ESSENTIAL entry puts every line in more.
     * @return array{essential: list<string>, more: list<string>}
     */
    public static function limitsFor(ConnectionProvider $provider, ProviderTier $tier, Group $group, Terminology $terminology): array;
}
```

```php
namespace App\Events;
class ConnectionReconnected { public function __construct(public Connection $connection, public bool $sameAccount, public ?string $previousExternalId) {} }

namespace App\Http\Controllers\Share;
class ConnectionsController extends Controller
{
    public function __construct(private ConnectionService $connections) {}
    public function begin(BeginConnectionRequest $request, string $group, ConnectionProvider $provider, CurrentGroup $current): Response;      // owner; the Connect button's begin step (D-033); Inertia::location($url) as CheckoutController::store() (:53-58), the form being an Inertia POST
    public function update(UpdateConnectionRequest $request, string $group, string $connectionId, CurrentGroup $current): RedirectResponse;   // owner; toast connections.tier.saved
    public function disconnect(string $group, string $connectionId, CurrentGroup $current): RedirectResponse;                                  // owner; toast connections.disconnected
    /** Owner. heldAccountChange() null → ConnectionsDestination::take() or Integrations, toast connections.account_change.expired (info).
     *  Else Inertia::render('share/settings/ConnectionAccountChange', [provider name, current (the row's account_name), incoming (the held account's name),
     *  series and none from impactOf() as ProviderSections builds them, inQori from connections.providers.<provider>.account_change.in_qori,
     *  copy through Terminology with :minutes from ACCOUNT_CHANGE_MINUTES,
     *  switchUrl, keepUrl]). */
    public function accountChange(string $group, ConnectionProvider $provider, CurrentGroup $current): Response|RedirectResponse;
    /** Owner. switchAccount() null → toast connections.account_change.expired; else toast connections.account_changed. Either way ConnectionsDestination::take() or Integrations. */
    public function switchAccount(string $group, string $connectionId, CurrentGroup $current): RedirectResponse;
    /** Owner. keepAccount() false → toast connections.account_change.expired; else toast connections.account_change.kept. Either way ConnectionsDestination::take() or Integrations. */
    public function keepAccount(string $group, string $connectionId, CurrentGroup $current): RedirectResponse;
    private function guardOwner(CurrentGroup $current): void;   // errors.connections.owner_only
}

namespace App\Http\Controllers\Settings;
class ConnectionFinaliseController extends Controller
{
    public function __construct(private ConnectionService $connections) {}
    /** $vendor is the path's {vendor}, a string the route's whereIn() has limited to ConnectionProvider::vendors(); the provider and tier
     *  being finished come from the session entry, never the path (D-033). No Google word is read here (D-022).
     *  First, before anything can throw, $destination = ConnectionsDestination::take(), as PaymentsFinaliseController takes PaymentsDestination (:38).
     *  Then the Group from the session entry (none → errors.connections.oauth_state); owner check (errors.connections.owner_only);
     *  $outcome = finaliseConnection($group, $vendor, $request->query(), route('connections.oauth.finalise', $vendor)), the redirect_uri
     *  begin sent, since another vendor is refused before the code is spent:
     *  isDeclined() → info toast connections.declined;
     *  held → ConnectionsDestination::remember($destination) when $destination is not null, then
     *         to_route('share.connections.account_change', [group slug, $outcome->connection->provider->slug()]) with no toast;
     *  otherwise a success toast, connections.connected or connections.reconnected;
     *  then $destination, or Integrations when it is null. */
    public function __invoke(Request $request, string $vendor): RedirectResponse;
}
```

```php
// App\Providers\AppServiceProvider::boot() — {provider} is a ConnectionProvider slug in every route that has one (D-033)
Route::bind('provider', fn (string $slug): ConnectionProvider => ConnectionProvider::fromSlug($slug) ?? abort(404));

// routes/settings.php — under auth only, beside payments.oauth.finalise (:59-60); one landing per vendor, not per provider (D-033)
Route::get('u/connections/{vendor}/finalise', ConnectionFinaliseController::class)
    ->whereIn('vendor', ConnectionProvider::vendors())
    ->name('connections.oauth.finalise');
```

```php
// config/services.php — the one Cloud client; T-092 reads the same keys and registers its own redirect URI on it
'google' => ['client_id' => env('GOOGLE_CLIENT_ID'), 'client_secret' => env('GOOGLE_CLIENT_SECRET')],
// config/qori.php
'connections' => ['google_drive' => ['free_storage_gb' => 15, 'review_days' => 5, 'admin_propagation_hours' => 24]],
```

`SetupController::storage()` calls
`ConnectionsDestination::remember(route('share.setup.storage', $model->slug))` and
passes `'connect' => ['url' => route('share.settings.integrations', $model->slug), 'label' => __('groups.setup.storage_connect_label')]`
with `copy.connect` in place of `copy.later`. `ProviderSection.vue` takes one
`providers` entry and renders, in this order and above the Connect button
whether or not the account is connected: the dropdown (a `Form` PATCH once
connected, the Connect form's field before); for the tier the dropdown shows,
`recommendedLabel` with its one sentence, `essentialLabel` with the `essential`
list, and a `Collapsible`, closed on first render, whose trigger reads the
tier's `moreLabel` and whose content is the `more` list; then the status badge,
the buttons, and the `Dialog` copied from the Stripe section
(`Integrations.vue:212-253`). The Dialog's description is `body`, then `seriesIntro`
with one line per `series` entry, each a link to that Series, then `inQori`;
or `body` and `none` when the list is empty. It exposes
`<slot name="grants" />`. `ConnectionAccountChange.vue` renders `title`,
`intro`, the two accounts under their labels, `seriesIntro` with the same
Series lines and `inQori` (from the provider's `account_change.in_qori`), or
`none`, then `expires`, and two `Form` POSTs, Switch (`switchUrl`, primary) and Keep
(`keepUrl`, outline), in the settings layout `Integrations.vue` uses. The page
is reached by the landing's `to_route()`, which `Reachability` reads as a link
(`app/Support/Reachability.php:162-171`), so it needs no allow-list entry.

## Copy

| Key                                                                           | File                      | English                                                                                                                                                                                                                                                                                                                                    |
| ----------------------------------------------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `connections.providers.google_drive.name`                                     | `lang/en/connections.php` | Google Drive                                                                                                                                                                                                                                                                                                                               |
| `connections.providers.google_drive.description`                              | `lang/en/connections.php` | Share files from one folder per :series in your own Google Drive. Everyone with access is let in on that folder, and whatever you put there reaches them.                                                                                                                                                                                  |
| `connections.providers.google_drive.tiers.google_free.label`                  | `lang/en/connections.php` | Free Google Drive                                                                                                                                                                                                                                                                                                                          |
| `connections.providers.google_drive.tiers.google_free.help`                   | `lang/en/connections.php` | A personal Google account, including Google One.                                                                                                                                                                                                                                                                                           |
| `connections.providers.google_drive.tiers.google_free.recommended`            | `lang/en/connections.php` | Good for a personal account: keep one folder for each :series, and watch your :gigabytes GB so you can still upload updates.                                                                                                                                                                                                               |
| `connections.providers.google_drive.tiers.google_workspace.label`             | `lang/en/connections.php` | Google Workspace & G Suite                                                                                                                                                                                                                                                                                                                 |
| `connections.providers.google_drive.tiers.google_workspace.help`              | `lang/en/connections.php` | Choose this if your Google account has an admin: a company or school account, or Google Workspace on a Gmail address.                                                                                                                                                                                                                      |
| `connections.providers.google_drive.tiers.google_workspace.recommended`       | `lang/en/connections.php` | Check with your admin that apps and sharing outside your organisation are allowed before you connect, and keep each :series folder in your own Drive unless you manage the shared drive it sits in.                                                                                                                                        |
| `connections.providers.google_drive.limits.common.accounts`                   | `lang/en/connections.php` | Everyone you share with needs a Google account. They confirm it in Qori once, and must be signed in to that account when they open anything.                                                                                                                                                                                               |
| `connections.providers.google_drive.limits.common.folder`                     | `lang/en/connections.php` | Pick one folder for each :series and keep everything for it inside. Sharing the folder shares everything in it, :episode_plural or not, and a file you add there reaches everyone at once.                                                                                                                                                 |
| `connections.providers.google_drive.limits.common.shortcuts`                  | `lang/en/connections.php` | Move files into the folder. A shortcut to a file does not share it.                                                                                                                                                                                                                                                                        |
| `connections.providers.google_drive.limits.common.limited_access`             | `lang/en/connections.php` | Don't set a subfolder to limited access. People can see it but can't open it.                                                                                                                                                                                                                                                              |
| `connections.providers.google_drive.limits.common.updating`                   | `lang/en/connections.php` | To update a file, edit Google Docs, Sheets and Slides directly, or use Manage versions and Upload new version. Keep both files, re-uploading or copying makes a new file: people still see it in the folder, but the :episode in Qori needs picking again.                                                                                 |
| `connections.providers.google_drive.limits.common.video_processing`           | `lang/en/connections.php` | A new video can take a while to process before other people can watch it.                                                                                                                                                                                                                                                                  |
| `connections.providers.google_drive.limits.common.flagged`                    | `lang/en/connections.php` | If Google flags a file, nobody else can open it until Google reviews it, which takes about :days days.                                                                                                                                                                                                                                     |
| `connections.providers.google_drive.limits.common.rate`                       | `lang/en/connections.php` | When many people join at once, Google may slow sharing and some people may wait a little.                                                                                                                                                                                                                                                  |
| `connections.providers.google_drive.limits.common.receiving_policy`           | `lang/en/connections.php` | Someone whose work or school account only accepts files from approved organisations won't be able to open yours.                                                                                                                                                                                                                           |
| `connections.providers.google_drive.limits.common.names_visible`              | `lang/en/connections.php` | People you let in can see each other's names when they have the same Google Doc, Sheet or Slide open at the same time.                                                                                                                                                                                                                     |
| `connections.providers.google_drive.limits.common.revoked`                    | `lang/en/connections.php` | If you remove Qori's access in your Google account, nobody new gets access until you connect again.                                                                                                                                                                                                                                        |
| `connections.providers.google_drive.limits.google_free.storage`               | `lang/en/connections.php` | Your files use your Google storage: :gigabytes GB on a free account, shared with Gmail and Photos. When it is full you can't upload updates.                                                                                                                                                                                               |
| `connections.providers.google_drive.limits.google_workspace.admin_apps`       | `lang/en/connections.php` | Your admin must let third-party apps use Google Drive and must not block Qori. Qori tests this when you connect and tells you if Google refuses.                                                                                                                                                                                           |
| `connections.providers.google_drive.limits.google_workspace.external_sharing` | `lang/en/connections.php` | Your admin must allow sharing outside your organisation, including to personal Gmail addresses. If sharing is limited to approved organisations, most people can't be added.                                                                                                                                                               |
| `connections.providers.google_drive.limits.google_workspace.later_blocks`     | `lang/en/connections.php` | Qori finds out about other blocked settings the next time it shares, and tells you. If your admin turns outside sharing off later, people already added lose access.                                                                                                                                                                       |
| `connections.providers.google_drive.limits.google_workspace.shared_drive`     | `lang/en/connections.php` | For a folder in a shared drive, you need Manager or Content manager access, and the shared drive must allow people from outside your organisation and people who aren't members.                                                                                                                                                           |
| `connections.providers.google_drive.limits.google_workspace.propagation`      | `lang/en/connections.php` | Admin changes can take up to :hours hours to apply.                                                                                                                                                                                                                                                                                        |
| `connections.providers.google_drive.limits.google_workspace.legacy_free`      | `lang/en/connections.php` | The old free edition of G Suite is for personal, non-commercial use only. If you sell :series_plural, we recommend a paid edition — Qori connects it either way, and those terms are between you and Google.                                                                                                                               |
| `connections.providers.google_drive.disconnect.in_qori`                       | `lang/en/connections.php` | :peer_plural already let in stay on your folders in Google Drive and keep opening their :episode_plural from Qori. Nobody new is let in, and anyone whose access ends in the meantime stays on the folder, until you connect :account again: then Qori lets in everyone waiting and takes those people off.                                |
| `connections.providers.google_drive.account_change.in_qori`                   | `lang/en/connections.php` | :peer_plural already let in stay on your folders in :current until you remove them there; once you switch, Qori can't reach :current to do it for you. Qori can't confirm their access there either, so their :episode_plural stop opening from Qori at their next check, until each folder and its files are picked again from :incoming. |
| `connections.tier.label`                                                      | `lang/en/connections.php` | Which kind of account?                                                                                                                                                                                                                                                                                                                     |
| `connections.tier.recommended_label`                                          | `lang/en/connections.php` | What we recommend                                                                                                                                                                                                                                                                                                                          |
| `connections.tier.essential_label`                                            | `lang/en/connections.php` | Know this before you connect                                                                                                                                                                                                                                                                                                               |
| `connections.tier.more_label`                                                 | `lang/en/connections.php` | Everything else to know (:count)                                                                                                                                                                                                                                                                                                           |
| `connections.tier.saved`                                                      | `lang/en/connections.php` | Noted. The advice and limitations shown are for :tier.                                                                                                                                                                                                                                                                                     |
| `connections.status.not_connected`                                            | `lang/en/connections.php` | Not connected                                                                                                                                                                                                                                                                                                                              |
| `connections.status.connected`                                                | `lang/en/connections.php` | Connected as :account                                                                                                                                                                                                                                                                                                                      |
| `connections.status.needs_reconnect`                                          | `lang/en/connections.php` | Qori lost its access to :account. Connect again to keep letting people in.                                                                                                                                                                                                                                                                 |
| `connections.connect`                                                         | `lang/en/connections.php` | Connect :provider                                                                                                                                                                                                                                                                                                                          |
| `connections.reconnect`                                                       | `lang/en/connections.php` | Connect again                                                                                                                                                                                                                                                                                                                              |
| `connections.owner_only_note`                                                 | `lang/en/connections.php` | Connecting accounts is the owner's to do.                                                                                                                                                                                                                                                                                                  |
| `connections.connected`                                                       | `lang/en/connections.php` | :provider is connected as :account.                                                                                                                                                                                                                                                                                                        |
| `connections.reconnected`                                                     | `lang/en/connections.php` | :provider is connected again, on the same account.                                                                                                                                                                                                                                                                                         |
| `connections.account_changed`                                                 | `lang/en/connections.php` | :provider is connected as :account now. Anything picked from :previous needs picking again.                                                                                                                                                                                                                                                |
| `connections.account_change.title`                                            | `lang/en/connections.php` | Switch :provider to :incoming?                                                                                                                                                                                                                                                                                                             |
| `connections.account_change.intro`                                            | `lang/en/connections.php` | You signed in to :provider as :incoming, which isn't the account your :series_plural use. Nothing has changed yet.                                                                                                                                                                                                                         |
| `connections.account_change.current_label`                                    | `lang/en/connections.php` | The account your :series_plural use                                                                                                                                                                                                                                                                                                        |
| `connections.account_change.incoming_label`                                   | `lang/en/connections.php` | The account you just signed in with                                                                                                                                                                                                                                                                                                        |
| `connections.account_change.series_intro`                                     | `lang/en/connections.php` | If you switch, whatever these :series_plural use from :current needs picking again from :incoming, and nobody new is let in on them until it is:                                                                                                                                                                                           |
| `connections.account_change.none`                                             | `lang/en/connections.php` | No :series uses :provider yet, so nothing needs picking again.                                                                                                                                                                                                                                                                             |
| `connections.account_change.expires`                                          | `lang/en/connections.php` | This choice waits :minutes minutes. After that nothing changes, and you can connect again to switch.                                                                                                                                                                                                                                       |
| `connections.account_change.switch`                                           | `lang/en/connections.php` | Switch to :incoming                                                                                                                                                                                                                                                                                                                        |
| `connections.account_change.keep`                                             | `lang/en/connections.php` | Keep :current                                                                                                                                                                                                                                                                                                                              |
| `connections.account_change.kept`                                             | `lang/en/connections.php` | Nothing changed. :incoming wasn't connected.                                                                                                                                                                                                                                                                                               |
| `connections.account_change.expired`                                          | `lang/en/connections.php` | That choice waited too long, so nothing changed. Connect :provider again to switch accounts.                                                                                                                                                                                                                                               |
| `connections.declined`                                                        | `lang/en/connections.php` | Nothing was connected. You can try again whenever you like.                                                                                                                                                                                                                                                                                |
| `connections.disconnect_label`                                                | `lang/en/connections.php` | Disconnect :provider                                                                                                                                                                                                                                                                                                                       |
| `connections.disconnect_title`                                                | `lang/en/connections.php` | Disconnect :provider?                                                                                                                                                                                                                                                                                                                      |
| `connections.disconnect_body`                                                 | `lang/en/connections.php` | Qori forgets its access to :account and changes nothing in it: your files stay where they are, and nobody Qori let in is removed.                                                                                                                                                                                                          |
| `connections.disconnect_series_intro`                                         | `lang/en/connections.php` | These :series_plural use :provider:                                                                                                                                                                                                                                                                                                        |
| `connections.disconnect_none`                                                 | `lang/en/connections.php` | No :series uses :provider yet, so disconnecting affects nobody.                                                                                                                                                                                                                                                                            |
| `connections.series_using.row`                                                | `lang/en/connections.php` | `{0} :title, nobody with access yet\|{1} :title, :count :peer with access\|[2,*] :title, :count :peer_plural with access`                                                                                                                                                                                                                  |
| `connections.disconnect_confirm`                                              | `lang/en/connections.php` | Disconnect                                                                                                                                                                                                                                                                                                                                 |
| `connections.disconnect_keep`                                                 | `lang/en/connections.php` | Keep it                                                                                                                                                                                                                                                                                                                                    |
| `connections.disconnected`                                                    | `lang/en/connections.php` | :provider is disconnected. Connect again whenever you're ready.                                                                                                                                                                                                                                                                            |
| `errors.connections.owner_only`                                               | `lang/en/errors.php`      | Only the owner can connect or disconnect an account. / Ask the owner to make the change.                                                                                                                                                                                                                                                   |
| `errors.connections.oauth_state`                                              | `lang/en/errors.php`      | That sign-in didn't start from Qori, so nothing was connected. / Start again from Integrations.                                                                                                                                                                                                                                            |
| `errors.connections.scope_declined`                                           | `lang/en/errors.php`      | Qori wasn't given access to your files, so nothing was connected. / Try again, and allow access to your files when you're asked.                                                                                                                                                                                                           |
| `errors.connections.admin_blocked`                                            | `lang/en/errors.php`      | Your organisation's admin doesn't allow Qori to use this account. / Ask your admin to allow Qori, or connect a personal account that holds the files.                                                                                                                                                                                      |
| `errors.connections.exchange_failed`                                          | `lang/en/errors.php`      | We couldn't finish connecting the account. / Try again in a moment. Nothing was changed.                                                                                                                                                                                                                                                   |
| `errors.connections.not_available`                                            | `lang/en/errors.php`      | That kind of account can't be connected yet. (final, no resolution)                                                                                                                                                                                                                                                                        |
| `groups.setup.storage_connect`                                                | `lang/en/groups.php`      | To share files from your own Google Drive, connect it from your :group's Integrations page — now, or whenever you're ready. Documents you upload to Qori need nothing connected.                                                                                                                                                           |
| `groups.setup.storage_connect_label`                                          | `lang/en/groups.php`      | Connect an account                                                                                                                                                                                                                                                                                                                         |

Every tier has both a `recommended` line and its `limits.*` lines, and a tier
with only one of them is incomplete (`D-018`): the recommendation is what Qori
would do in the creator's place, the limits are what that tier cannot do, and
neither stands in for the other. Every tier also has a
`ProviderSections::ESSENTIAL` entry naming at most `MAX_ESSENTIAL` of its
lines, and every provider with a tier has its `disconnect.in_qori` and
`account_change.in_qori` lines, written from what its connector and `T-091`
actually do (`D-021` rule 3). `errors.connections.not_available` is about a
provider Qori has not wired yet, never about a tier — no tier is refused
anywhere in this task.

An `errors.*` row reads message / resolution; the two marked final omit their
resolution deliberately (`docs/architecture/errors.md`).
`errors.connections.scope_declined` names no checkbox, because Google shows
none for a request naming `drive.file` alone (Decisions).
`groups.setup.storage_later` is removed.
`:provider`, `:account`, `:previous` and `:tier` are filled from
`connections.providers.*.name`, the row's `account_name`, the previous
`account_name` and the tier's label; on the account-change page `:current` is
the row's `account_name` and `:incoming` the held account's name; `:minutes` is
`ConnectionService::ACCOUNT_CHANGE_MINUTES`; `:count` in
`connections.tier.more_label` is the length of that tier's `more`, and in
`connections.series_using.row` the Series' active Accesses, through
`Terminology::choice()`; `:title` is the Series' title. No sentence names a
vendor inline; `D-016`'s exception covers the provider names and the tier copy.
`disconnect.in_qori` renders only when the Dialog's Series list is not empty,
and `account_change.in_qori` likewise on its page, because both speak about
people already let in. The limitation lines whose bullets the blueprint marks
"(spike)" — the 600-address cap — are not here; `T-094` adds them if `T-093`
confirms them. `connections.grants.*` are `T-091`'s keys in this file.

## Routes

| Verb   | Path                                                         | Name                                      | Action                                |
| ------ | ------------------------------------------------------------ | ----------------------------------------- | ------------------------------------- |
| POST   | `g/{group}/connections/{provider}/begin`                     | `share.connections.begin`                 | `ConnectionsController@begin`         |
| PATCH  | `g/{group}/connections/{connectionId}`                       | `share.connections.update`                | `ConnectionsController@update`        |
| DELETE | `g/{group}/connections/{connectionId}`                       | `share.connections.disconnect`            | `ConnectionsController@disconnect`    |
| GET    | `g/{group}/connections/{provider}/account-change`            | `share.connections.account_change`        | `ConnectionsController@accountChange` |
| POST   | `g/{group}/connections/{connectionId}/account-change/switch` | `share.connections.account_change.switch` | `ConnectionsController@switchAccount` |
| POST   | `g/{group}/connections/{connectionId}/account-change/keep`   | `share.connections.account_change.keep`   | `ConnectionsController@keepAccount`   |
| GET    | `u/connections/{vendor}/finalise`                            | `connections.oauth.finalise`              | `ConnectionFinaliseController`        |

`{provider}` carries a `ConnectionProvider` slug, never the stored value
(`D-033`): the URL says `google-drive` where the row, the lang keys and the
config keys keep `google_drive`. The binder under Code, in
`AppServiceProvider::boot()` (`:38-44`), turns it back into the case for every
route that has one, and an unknown slug, or the stored value with its
underscore, is a 404, so each resource has one URL. The actions keep their
typed `ConnectionProvider $provider`, because Laravel's implicit enum binding
passes an instance the binder already made straight through
(`vendor/laravel/framework/src/Illuminate/Routing/ImplicitRouteBinding.php:92-94`).
The way out needs the same care: `route()` writes a backed enum as its value
(`RouteUrlGenerator.php:302-304`, `enum_value()`), which is now a 404, so every
`route()` naming a provider passes `$provider->slug()`, never the case, and
`ProviderSections` builds each section's `beginUrl` rather than leaving the
page to build it from a key that is the stored value. `{provider}` is kept for
that slug alone: any other enum in a URL takes a parameter named for it, as
`T-092`'s `{vendor}` and `T-090`'s `{episodeProvider}` do, so the binder never
meets one. The landing's `{vendor}` is a plain string, limited by
`whereIn('vendor', ConnectionProvider::vendors())` to the vendors a provider
names, so anything else is a 404 before the controller runs; which provider
and tier it finishes comes from the session, as Decisions says. The six group
routes sit in `routes/share/payments.php` beside the payments actions; the
landing sits in `routes/settings.php` under `auth` only, as
`payments.oauth.finalise` does (`:59-60`), and is owner-checked in the
controller. The confirmation page is a `GET` that renders, so it names the
provider by its slug, which reads in a URL; Switch and Keep act on the row, so
they take its id (`CLAUDE.md`, route addressing). Keep is a `POST` rather than
a `DELETE` because it answers a question and leaves the connection as it is;
the hold it discards lives in the session, not in a row.

## Tests

Every case fakes the vendor with `Http::fake()` and `T-093`'s fixture bodies
under `tests/Fixtures/google/`; a test that needs a connector for a provider
with none uses a double `tests/Doubles/ConnectsNothing.php`. Line numbers
under Changed are today's; `T-123`, which lands first, edits
`EpisodeServiceTest.php` too.

**New: `tests/Feature/Share/ConnectionsConnectTest.php` — 16 cases**

Cases 41 to 45, after case 40 below, are this file's too.

1. `test_the_owner_is_sent_to_google_with_the_narrow_scope_and_offline_access` — a POST to `g/{group}/connections/google-drive/begin`, the slug; 302 host `accounts.google.com`; `scope`, `access_type=offline`, `prompt=consent`, `include_granted_scopes=true`, `state` of 40 chars, `code_challenge_method=S256`, `redirect_uri` = `route('connections.oauth.finalise', 'google')`; session holds state, verifier, group, provider, tier.
2. `test_an_admin_is_refused` — 403, `errors.connections.owner_only`.
3. `test_a_tier_is_required_and_must_belong_to_the_provider` — missing, and `dropbox_basic` on Google, both 422.
4. `test_a_provider_with_no_connector_is_refused` — `ConnectionProvider::Zoom`: `errors.connections.not_available`.
5. `test_the_landing_stores_encrypted_tokens_the_account_and_the_tier` — `oauth-token.json`, `about-get.json`; raw `access_token` is not the plaintext; `external_id`, `account_name`, `expires_at`, `settings.tier` set; toast `connections.connected`; 302 to Integrations.
6. `test_a_mismatched_state_spends_nothing` — 403 `errors.connections.oauth_state`; no row; no token call.
7. `test_a_landing_for_a_group_the_person_does_not_own_is_refused`.
8. `test_declining_at_google_connects_nothing` — `error=access_denied` with the pending `state`; toast `connections.declined`; no row; session entry gone.
9. `test_a_token_without_drive_file_is_revoked_and_refused` — `oauth-token-scope-declined.json`, observed by `T-093` or edited by hand here (Preconditions); revoke endpoint called; `errors.connections.scope_declined`; no row.
10. `test_reconnecting_the_same_account_refreshes_tokens_and_clears_reconnect` — a row marked `invalid_grant`; after the landing `needs_reconnect_at` null, tokens replaced, `ConnectionReconnected` dispatched with `sameAccount` true; toast `connections.reconnected`; nothing under `ConnectionService::ACCOUNT_CHANGE_SESSION`.
11. `test_connecting_a_different_account_is_held_and_nothing_is_written` — `external_id` differs; the row's tokens, `external_id`, `account_name` and `settings.tier` unchanged; no `ConnectionReconnected` dispatched (`Event::fake()`); the session holds `ACCOUNT_CHANGE_SESSION`, and its raw value contains neither the fixture's `access_token` nor its `refresh_token`; `ConnectionsDestination::KEY` holds the setup URL it held before the landing, taken and put back; 302 to `share.connections.account_change` for `google-drive`, with no toast.

**New: `tests/Feature/Share/ConnectionsDisconnectTest.php` — 4 cases**

12. `test_disconnecting_drops_the_tokens_and_keeps_the_row` — revoke endpoint called; `revoked_at` set; `external_id` kept.
13. `test_a_vendor_that_refuses_the_revoke_does_not_stop_the_disconnect`.
14. `test_an_admin_cannot_disconnect_change_the_tier_or_answer_an_account_change` — both 403; so are `share.connections.account_change`, `…account_change.switch` and `…account_change.keep`, each with `errors.connections.owner_only` and the row unchanged.
15. `test_the_owner_changes_the_tier_after_connecting` — PATCH; `settings.tier`; toast `connections.tier.saved`.

**New: `tests/Feature/Share/IntegrationsProvidersTest.php` — 4 cases**

16. `test_only_providers_with_a_bound_connector_have_a_section` — `providers` has `google_drive` and no `dropbox`; the `google_drive` entry's `beginUrl` is `route('share.connections.begin', [$group->slug, 'google-drive'])`.
17. `test_every_tier_is_offered_with_a_recommendation_and_its_limitations` — `tiers` holds every case `ProviderTier::forProvider(GoogleDrive)` returns, none filtered, each with a non-empty `recommended`, a non-empty `essential` and a `moreLabel`; for each tier `essential` followed by `more` holds every `limits.common.*` and `limits.<tier>.*` line exactly once (`D-018`: nothing is dropped from the page); `google_free`'s `essential` is the accounts line then the folder line, and its `more` includes `15 GB`; `google_workspace`'s `essential` is the accounts, external-sharing and folder lines in that order, its `more` includes `24 hours` and the legacy-free line, and neither list holds a storage line.
18. `test_the_three_statuses_render_their_sentence` — none, connected, needs reconnect; each render sends nothing (`Http::assertNothingSent()`), so no section waits on its vendor (`R-004`).
19. `test_an_admin_sees_the_note_and_no_buttons`.

Case 20, `test_the_landing_route_is_on_the_reachability_allow_list`, is
withdrawn: the landing needs no entry (Decisions). Its number is not reused,
so the numbers after it stay put.

**New: `tests/Feature/Integrations/Google/GoogleAccountsTest.php` — 7 cases**

Cases 46 and 47, after case 45 below, are this file's too.

21. `test_it_reads_the_token_response` — `finaliseConnection()` with the expected `state` and a `code`: `Connected`, its `ConnectionTokens` from `oauth-token.json`, scopes split on space, `expiresAt` ≈ now + `expires_in`; the token call carried the `code_verifier` and the `redirect_uri` it was given.
22. `test_a_refresh_without_a_new_refresh_token_keeps_the_old_one` — `oauth-refresh.json`.
23. `test_invalid_grant_is_a_revoked_result_not_an_exception`.
24. `test_a_timeout_is_an_unavailable_result` — `Http::fake` throwing `ConnectionException`.
25. `test_it_reads_the_identity_from_about` — the request carries `fields=user(permissionId,emailAddress,displayName)`; `about-get.json` → `externalId` its `permissionId`, `name` its `emailAddress`; the same body without `emailAddress` → `name` its `displayName`; without `permissionId` → `AppException` for `errors.connections.exchange_failed`.

Cases 26 to 33 were `tests/Feature/Console/RefreshConnectionsCommandTest.php`
and moved to `T-151` with the refresh on 20 September 2026; the three cases in
`tests/Feature/Share/EpisodeServiceTest.php` and the changes to
`tests/Feature/Storage/MediaLifetimeTest.php` and `PlaybackTest.php` moved to
`T-152` with the Episode guard. Neither set is renumbered, as case 20's
withdrawal was not, so the numbers other drafts cite stay put.

**Changed: `tests/Feature/Share/SetupStepsTest.php` — +2 cases**

- `test_the_storage_part_links_to_integrations_and_remembers_the_destination`
  (`ConnectionsDestination::KEY` holds the storage URL),
  `test_returning_from_google_lands_back_on_storage` (the landing 302s to
  `share.setup.storage` and forgets the key).

**New: `tests/Feature/Share/ConnectionAccountChangeTest.php` — 4 cases**

Each starts from case 11's landing: a Google row for account A and a hold for account B.

34. `test_the_account_change_page_names_both_accounts_and_the_series_that_use_the_provider` — Inertia component `share/settings/ConnectionAccountChange`; `current` is A's `account_name`, `incoming` is B's; `series` empty and `none` set, since no Episode can be on Google Drive before `T-094`; `expires` built with `ConnectionService::ACCOUNT_CHANGE_MINUTES`; `switchUrl` and `keepUrl` carry the row's id.
35. `test_switching_applies_the_held_account` — POST `share.connections.account_change.switch`: same row id; tokens replaced; `external_id` and `account_name` are B's; `settings.tier` the held tier; reconnect state cleared; `ConnectionReconnected` dispatched once with `sameAccount` false and A's `external_id`; hold gone; toast `connections.account_changed`; 302 to Integrations; `ConnectionsDestination::KEY` taken.
36. `test_keeping_the_account_changes_nothing` — POST `share.connections.account_change.keep`: the row equal to before, attribute for attribute; no `ConnectionReconnected`; Google's revoke endpoint called with B's token; hold gone; toast `connections.account_change.kept`; `ConnectionsDestination::KEY` taken.
37. `test_an_expired_hold_applies_nothing` — `travel(ConnectionService::ACCOUNT_CHANGE_MINUTES + 1)->minutes()`: GET the page redirects to Integrations with toast `connections.account_change.expired` and the hold is forgotten; with a fresh hold travelled past the limit, POST switch leaves A's row unchanged, dispatches no event and flashes the same toast; `ConnectionsDestination::KEY` taken in both.

**New: `tests/Feature/Share/ProviderSectionsTest.php` — 3 cases**

38. `test_every_essential_key_exists_and_no_tier_lists_more_than_the_maximum` — for every provider and tier in `ProviderSections::ESSENTIAL`: at most `MAX_ESSENTIAL` keys, none twice, each starting `common.` or `<tier>.` and `Lang::has("connections.providers.{$provider}.limits.{$key}")`; and every `ProviderTier` case whose provider is `connectable()` has an entry.
39. `test_every_provider_with_a_tier_says_what_disconnecting_and_switching_do` — for each `connectable()` provider some `ProviderTier` case names, `Lang::has()` for `connections.providers.<provider>.disconnect.in_qori` and `…account_change.in_qori`; Teams, which connects nothing (`T-101`), needs neither.
40. `test_the_disconnect_dialog_lists_the_series_using_the_provider` — `ConnectsNothing` tagged for Dropbox and a Dropbox connection; one Series with a Dropbox Episode, two active Accesses and one revoked; one Series with a Qori-hosted Episode alone; the `dropbox` section's `disconnect.series` holds the first Series alone, its `url` `route('share.series.show')`, and `ConnectionService::impactOf()` gives it `peers` 2; the `google_drive` section's `disconnect.series` is empty with `none` set; no HTTP call is made (`Http::assertNothingSent()`).

**New, continued: `tests/Feature/Share/ConnectionsConnectTest.php` — 5 cases**

41 and 42 added with `D-033`, 43 to 45 with the landing's move into the
Google folder (`D-022`); numbered after case 40 rather than after case 11, so
the numbers other drafts cite stay put.

41. `test_a_landing_for_another_vendor_spends_nothing` — a pending Google Drive connect from case 1's POST, then `u/connections/dropbox/finalise` with its `state` and a `code`: 403 `errors.connections.oauth_state`, as case 6; no row; no token call (`Http::assertNothingSent()`).
42. `test_a_provider_is_addressed_by_its_slug_alone` — POST `g/{group}/connections/google-drive/begin` with a tier: 302 to `accounts.google.com`, as case 1; the same POST to `g/{group}/connections/google_drive/begin`: 404, and nothing under `ConnectionService::OAUTH_SESSION`; `u/connections/google-drive/finalise`: 404, because the landing takes a vendor.
43. `test_an_admin_block_at_google_connects_nothing` — the pending connect's `state` with `error=admin_policy_enforced`, and again with `error=org_internal`: 403 `errors.connections.admin_blocked` each time; no row; no token call (`Http::assertNothingSent()`); `ConnectionService::OAUTH_SESSION` gone.
44. `test_a_code_google_will_not_exchange_connects_nothing` — the token endpoint answering 400 with `errors-oauth-token-400-invalid_grant.json`'s body, then a `ConnectionException`: 502 `errors.connections.exchange_failed` each time; no row and nothing under `ConnectionService::ACCOUNT_CHANGE_SESSION`.
45. `test_a_landing_that_fails_spends_the_forwarding_address` — with `ConnectionsDestination::KEY` holding the setup URL: a mismatched `state` (403 `errors.connections.oauth_state`), a token without `drive.file` (403 `errors.connections.scope_declined`) and a refused exchange (502 `errors.connections.exchange_failed`) each leave `ConnectionsDestination::KEY` missing from the session, as `tests/Feature/Share/PaymentsOauthTest.php` asserts for Stripe's.

**New, continued: `tests/Feature/Integrations/Google/GoogleAccountsTest.php` — 2 cases**

46. `test_it_reads_the_landing_in_googles_words` — `finaliseConnection()` given `error=access_denied` answers `Declined`; `admin_policy_enforced` and `org_internal` `AdminBlocked`; `error=invalid_request` `Failed` with `upstream` `invalid_request`; an error whose `state` is another nonce `NotFromQori`; no error and a wrong `state` `NotFromQori`; the expected `state` and no `code` `Failed`; and not one of these sends a request (`Http::assertNothingSent()`).
47. `test_the_callers_budget_only_ever_shortens_googles_own_timeout` — read from the fake's `$options['timeout']`: the landing's token call, given `ConnectionService::REQUEST_TIMEOUT_SECONDS`, is sent with 10; a refresh given `SWEEP_TIMEOUT_SECONDS` is sent with `GoogleAccounts::TIMEOUT_SECONDS`, 20 (`D-034`).

Total: 40 cases, 38 in new files — 51 before the split of 20 September 2026,
which took eight to `T-151` and three to `T-152`; 47 and 42 before
19 September 2026, when case 20 was withdrawn and cases 43 to 47 were added.

## Acceptance

- [x] The Integrations page shows a Google Drive section whose dropdown holds
      every tier Google sells, none withheld, and whose recommendation
      sentence and limitation lines change with the tier, read from lang with
      the numbers interpolated; Connect asks Google for `drive.file` alone,
      with offline access, and lands back with the account named
- [x] Above the Connect button, before and after connecting, each tier shows
      its recommendation, at most `ProviderSections::MAX_ESSENTIAL` essential
      lines in `ESSENTIAL`'s order, and one closed disclosure labelled with its
      count that opens to every other line; seen in a browser at mobile and
      desktop widths, with no line of the tier missing from the section
- [x] No tier is refused anywhere: a connected account works the same on every
      tier, and the only refusal is the Episode one, for an account-bound
      provider the Group has not connected
- [x] Reconnecting the same account keeps the row and clears the reconnect
      state at once; a reconnect that returns a different account writes
      nothing and lands on `ConnectionAccountChange`, naming both accounts and
      the Series using the provider; Switch applies it and says what was picked
      needs picking again, Keep and a hold older than
      `ACCOUNT_CHANGE_MINUTES` change nothing; the landing and Switch raise
      `ConnectionReconnected`, Keep and an expired hold do not
- [x] Disconnect keeps the row and drops the tokens; its Dialog lists the
      Series using the provider with their counts of Peers with access, and
      says what happens to people already let in as Decisions describes; an
      admin sees a note and is refused on every write
- [x] Google's words in the landing are read in `app/Integrations/Google`
      alone: nothing under `app/Services` or `app/Http` names
      `access_denied`, `admin_policy_enforced` or `org_internal`
- [x] Setup's part three links to Integrations, no longer says "coming", and
      a connect started from it returns to it; a landing that fails spends
      the forwarding address
- [x] One real round trip through Qori's own Google client, its publishing
      status named, recorded in the report with whether Google took
      `code_challenge` and what `prompt=consent` showed — the two things
      `T-093`'s Playground tokens cannot show
- [x] `docs/flows/storage.md`'s Connections section, `docs/flows/onboarding.md`'s
      part three and forwarding address, the flows index and
      `docs/tinker/connections.md` describe what was built, the held account
      change and the disconnect Dialog's Series read among it
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

> **Set `ready` on 20 September 2026** by the stream owner, who also took the
> split (three ways, `T-151` and `T-152`) and the Google Drive section
> question (hidden until `T-094`). Three stale line citations were corrected
> against the tree at `78cec6f` first — `config/qori.php:464-465`,
> `EpisodeService::guardEpisodeType()` at `:389-407` called from `:57`, and
> `EpisodeProvider::connection()` at `:50-60` — because a frozen spec that
> points a developer at the wrong line is frozen wrong. `ConnectionProvider`
> has no methods at all today, so `slug()`, `fromSlug()`, `vendor()`,
> `vendors()` and `connectable()` are all net-new on an enum of four bare
> cases.
>
> Two bullets below stay open and neither blocks the build. `F11`'s real
> Google OAuth round trip is the owner's to run — it needs a Google sign-in,
> which an agent must not perform — and the Acceptance already requires it
> before this task is `done`; the code is written against `T-093`'s fixtures
> meanwhile. The privacy-and-terms disclosure before Connect is the stream
> owner's with `T-090` and `T-098`.

- ~~What happens to vendor-side grants when a creator disconnects: nothing (the
  draft), or a best-effort revoke pass before the tokens are dropped, which
  `T-091`'s sweep would have to run — the owner's. The disconnect Dialog's
  `disconnect_body` and `disconnect.in_qori` are written for "nothing" and
  change with the answer.~~ **Answered 17 September 2026 (`D-021`), struck
  19 September 2026:** nothing, as the struck bullet on `T-091`'s `verify()`
  below records. Vendor-side permissions stay and there is no revoke pass:
  people already let in keep opening, nobody new is let in, and the grants
  wait for the same account to reconnect. `disconnect_body` now says nobody
  Qori let in is removed, beside `disconnect.in_qori` and the reconnect
  email. The separate question of deleting what Qori holds on disconnect is
  the last bullet, and open.
- ~~Whether `external_id` is `about.get`'s `user.permissionId` and
  `account_name` its `emailAddress`, from an observed `about-get.json`; and
  `oauth-refresh.json` and `oauth-revoke.txt`, which `T-093`'s fixture set
  does not name — `T-093`'s, or this task's own first round trip, whichever
  runs first; anyone's.~~ **Answered 19 September 2026:** `T-093` keeps
  `about-get.json` in its step 2, with the mask
  `user(permissionId,emailAddress,displayName)` used here, and
  `oauth-refresh.json` and `oauth-revoke.txt` in its step 15, and this task
  depends on it. `external_id` is `permissionId`; `account_name` is
  `emailAddress`, falling back to `displayName`, since Google says the
  address may be absent (Decisions).
- What `T-093`'s bodies show when it runs: whether `about-get.json` carries
  `emailAddress`, and whether `oauth-refresh.json` carries a new
  `refresh_token`, which Code handles either way — the spike's. **`T-093`, 20
  September 2026:** `about-get.json` carries `emailAddress`, `displayName` and
  `permissionId` under `drive.file` alone. No refresh returned a new
  `refresh_token` (`oauth-refresh.json`).
- Whether Google's web-server flow accepts `code_challenge` with `S256` from
  Qori's own client, and whether `prompt=consent` belongs on every connect or
  only on a reconnect — the spike's in name, but `T-093` takes its tokens from
  the Playground and exercises neither, so this task's own first round trip
  answers both unless a code-flow step is added to the spike, and test 1
  changes with the answer; anyone's.
- `REQUEST_TIMEOUT_SECONDS` 10 for the landing's exchange,
  `SWEEP_TIMEOUT_SECONDS` 30 and `GoogleAccounts::TIMEOUT_SECONDS` 20, against
  the seconds `T-093` records per call; `D-034` keeps all three provisional
  until then — anyone's. **`T-093`, 20 September 2026:** the token endpoint
  took 0.54 to 0.68 s over nine calls, `about.get` 0.46 s, and the revoke
  endpoint 1.18 and 1.26 s.
- `T-093`'s findings for the connect step, from its report's Found, not
  fixed (`reports/T-093-2026-09-20-wayne.md`):
    - Removing Qori in the person's Google account kills live access tokens at
      once (401), and the next refresh is 400 `invalid_grant`
      (`errors-oauth-token-400-invalid_grant.json`).
    - Peers keep what was already shared with them.
    - The same account reconnecting keeps every pick.
    - The revoke endpoint answers 200 with the body `{` and `}`
      (`oauth-revoke.txt`).
    - Google documents that a revoke ends the project's tokens for every
      client, which would end `T-092`'s sign-in for the same person.
    - The "Google hasn't verified this app" warning appeared for `drive.file`
      alone in Testing, and whether it survives Publish app is unobserved.

    Folding these into Code and Copy is anyone's.

- ~~Whether Teams stays exempt from the connection guard, which is what
  `T-101`'s pasted-link design implies and its draft has not yet said —
  anyone's, with `T-101`.~~ **Answered 18 September 2026 (`D-025`):** Teams is
  exempt, and so is every other provider whose `content` is not an
  account-bound item id. The guard is narrowed rather than given an exception
  per vendor — see Decisions and Notes.
- ~~`->daily()` with no `onOneServer()`, as `qori:series:purge` runs today, until
  a second replica exists (`release-prerequisites.md`) — the owner's, with
  `operations`.~~ **Decided 19 September 2026:** `->daily()` alone, as
  `qori:series:purge` runs (`routes/console.php:28`). Until a second replica
  exists, two overlapping runs can only refresh a row twice, one after the
  other under the lock; `onOneServer()` comes with that replica, which is
  `operations`'.
- The Google Cloud app published and brand-verified, and the redirect URI for
  production registered (`release-prerequisites.md:20`); until then every
  token dies in seven days and the connect step shows an unverified consent
  screen — the owner's. This gates release, not this task: Testing is enough
  for its round trip.
- Whether Workspace Individual has admin sharing controls, which decides if
  the `google_workspace` help line sends those creators the right way — the
  spike's; anyone's.
- ~~`T-091`'s `ContainerLock::run(ConnectionProvider, string, Closure)` and this
  task's `AdvisoryLock::run(string, string, Closure)` are two classes around
  one `pg_advisory_xact_lock` statement; whether `ContainerLock` becomes a
  call to `AdvisoryLock` or the two stay — the stream owner's, before either
  is `ready`.~~ **Decided 19 September 2026:** one class. `T-091` calls this
  task's `AdvisoryLock::run(string $namespace, string $key, Closure $callback)`
  for its container lock and keeps no `ContainerLock`.
- ~~Whether the Episode form keeps offering Dropbox, Vimeo and Zoom behind the
  refusal, or stops offering each until its connector exists — anyone's, with
  `T-096`, `T-090` and `T-100`.~~ **Answered 17 September 2026 (`D-018`):** the
  form keeps offering all three. Every provider is in the beta release, so each
  connector lands before release and the refusal covers a gap that closes;
  removing an option and putting it back is work for a state that is temporary
  by decision.
- ~~`T-067`'s `blocks:` line lacks `T-044`, so `php artisan qori:tasks --check`
  reports the derivation mismatch until it is added — the board's; anyone's.~~
  **Answered 16 September 2026:** `T-067` now says `blocks: T-044, T-062`.
- `ConnectionService::ACCOUNT_CHANGE_MINUTES` at 10, provisional from
  `D-021`, against how long a creator takes to read the page after Google's
  consent screen — anyone's. `ProviderSections::MAX_ESSENTIAL` at 3, listed
  beside it until 19 September 2026, is not open: `D-021` rule 4 says "at
  most three".
- Google Drive's `ESSENTIAL` entry: `google_free` has two lines because nothing
  on a personal account stops sharing outright, and `google_workspace.admin_apps`
  is left in `more` because Google refuses it at consent. Whether a reviewer
  reads `D-021`'s criteria the same way — the stream owner's.
- ~~The disconnect Dialog's and the account-change page's `in_qori` sentences
  rest on `T-091` as drafted on 17 September 2026: `attempt()` turns a row
  `needs_creator` without a vendor call when the connection is not usable, but
  `verify()` is not given the same guard, so a `granted` row's re-check either
  guards the same way or calls `checkGrant()` with no token, which `T-094` maps
  to the same `connection_unusable`, or throws into `ERROR_UNEXPECTED`. Every
  branch ends with the row not `granted` and Open sending the Peer to the
  Series page, which is all the sentence claims; which state the Peer then
  reads is `T-091`'s to settle — anyone's, with `T-091`.~~ **Settled
  17 September 2026 (`D-021`):** `T-091` guards `verify()` too. While the
  connection is not `isLive()` it makes no call and leaves `granted` and
  `awaiting_acceptance` rows as they are, Open still answers `openLink()`, and
  a revoke try fails until the same account reconnects. People already let in
  keep opening; the Dialog's sentences, `disconnect_body` and the reconnect
  email say that. A switch to a different account is not this case — the new
  connection is live, and its re-check reads the old folder as gone — so
  `account_change.in_qori` still says their Episodes stop opening at the next
  check.
- `ConnectionService::impactOf()` reads Episodes only, because
  `series_containers` does not exist until `T-091`. Whether `T-091` extends it
  to a Series holding a container and no Episode yet, so the disconnect Dialog
  and the account-change page list that Series too — anyone's, with `T-091`.
- Whether Keep's best-effort revoke of the held token is wanted, or Keep should
  only forget the hold; the draft revokes so the account the creator did not
  choose does not keep listing Qori — anyone's.
- ~~How each provider section fails on its own, so a vendor that cannot be
  read does not take down the page and its disconnect actions (`R-004`, see
  Notes)~~ — **answered 19 September 2026 in Decisions:** no provider section
  calls its vendor to render, so none can. Still open: whether Stripe's
  section, which does, is fixed here or in a `recovery` task — the stream
  owner's. `IntegrationsController::show()` calls `PaymentsService::account()`
  on every render and nothing catches a failure
  (`app/Http/Controllers/Share/IntegrationsController.php:32`), so Stripe
  down is the whole page down, the Google section and its Disconnect with it.
  **Recommended: here**, because this task already rewrites both files the
  fix touches: `show()` catches the `AppException` an unreadable account
  throws and renders Stripe's section with `status` `unavailable`, one
  `payments.unavailable` sentence and its disconnect Dialog, with one more
  case in `IntegrationsProvidersTest`; `lang/en/payments.php` joins Files. If
  `recovery` takes it, nothing here changes.
- **From the privacy and terms drafts (`docs/pptcs/`, 19 September 2026) —
  two things the connect step may owe the vendors:** Google's Workspace User
  Data and Developer Policy asks for a disclosure shown in the product
  immediately before Google's consent screen, not only in the privacy policy;
  and Microsoft's APIs Terms s.5(b)-(c) and YouTube's Developer Policies III.E
  expect Qori to delete what it holds when a creator disconnects, where this
  draft drops the tokens and keeps the row and the item ids. Whether the
  Integrations page gains a short disclosure before Connect, and what
  disconnect deletes, is re-checked against the vendor pages the README cites
  — the stream owner's, with `T-090` and `T-098`.
- ~~Whether the Google Drive section shows before `T-094` can use it — the
  owner's.~~ **Answered 20 September 2026: hidden until then**, as recommended.
  Until `T-094` adds `EpisodeProvider::GoogleDrive` and its picker, a
  connected Drive holds nothing a Series can use, yet setup's
  `groups.setup.storage_connect` would send a new creator to connect it.
  The reasoning, which the answer took: so connecting is never a dead end
  (`PLAN.md`'s beta gate: no built-in action knowingly leads to a dead page):
  `T-094`, not this task, adds `GoogleAccounts`
  to the `account-connectors` tag, in the same change as its picker; this
  task's tests tag it themselves, as they tag `ConnectsNothing`, and its
  browser walk and real round trip run with the tag line added locally and
  not committed, which the report says; and setup's part three shows its link
  and `storage_connect` only while `ProviderSections::props()` has a section,
  `storage_why` alone before.
- ~~**The split** — the stream owner's. This is `L` with 68 paths in Files, 51
  test cases and one migration, well past what `PROCESS.md` means by `L`.~~
  **Done 20 September 2026, three ways as recommended:** `T-151` took the
  token refresh and `T-152` the Episode guard, both are in `blocks:` above,
  and `T-123` left `depends:` with `T-152`. This task is now about 57 paths
  and 40 test cases and stays `L`. The reasoning, for the record: the
  cut the audit of 19 September 2026 proposed is four: (a) connect, landing,
  tier and disconnect with `GoogleAccounts`; (b) the token refresh —
  `qori:connections:refresh`, `fresh()`, `refresh()`, `markForReconnect()`,
  `AdvisoryLock` and the reconnect email; (c) the held different-account
  change; (d) the Episode guard. **Recommended: three, not four.** (b) and
  (d) become tasks of their own: (d) is six files — `EpisodeProvider`,
  `EpisodeService`, `lang/en/errors.php`'s two keys and three test files —
  and takes `T-123` from this task's `depends:` with it; (b) is about a dozen
  paths, the refresh fixtures' tests among them, and `T-091`, which needs
  `fresh()`, `markForReconnect()` and `AdvisoryLock`, depends on it as well as
  on this. Both depend on (a) — (d) for `ConnectionService::connectorFor()`,
  (b) for the row and the contract — and not on each other, so they run side
  by side. (c) stays with (a): the landing has three outcomes, a new account,
  the same one and a different one, and cutting the third out leaves (a)
  needing an interim answer for a different account that `D-021` rule 3 does
  not give.

### From the storage review, 20 September 2026

- ~~**Disconnect and account switch make later cleanup impossible, and
  `D-038` now says the opposite** (`F05`).~~ **Settled 20 September 2026 by
  `D-039`: disconnect stays as this task specifies it.** The owner declined
  the bounded cleanup period — "disconnect is enough follow T-044. light
  touches" — because holding a creator's token after they have asked Qori to
  let go is the opposite of what Disconnect means to the person pressing it.
  `D-038`'s consequence line is corrected instead. What this task still owes
  is the sentence in `D-021`'s impact dialog saying that the people already
  let in keep their access until the creator reconnects or removes them at
  the vendor. The original finding, for the record: This task drops the tokens and
  leaves every permission standing; `D-038` says disconnecting revokes
  permissions and leaves files. `T-093` observed that Peers keep their access
  after the creator removes Qori from their account, so this is not a
  hypothetical. The review proposes a decision record, **"Disconnect retires
  permission authority only after cleanup is accounted for"**: stop new
  grants, keep the old encrypted authority for a bounded cleanup period,
  record what could not be revoked, then retire the token. The alternative is
  to keep immediate destruction, amend `D-038`, and give the creator a
  concrete manual cleanup list — the owner's, and one of the three decisions
  this review asks for.
- **The advisory lock has no acquisition budget** (`F08`). It is specified as
  a blocking `pg_advisory_xact_lock`, so a request can wait an unbounded time
  before a call that is itself well bounded by `D-034` — anyone's.
- **No Google OAuth round trip has ever been observed** (`F11`). Every token
  body in the fixtures came from the Playground, which sends no nonce and
  uses its own redirect, so this task's code exchange, PKCE, nonce and
  consent outcomes are specified from documentation. The first step of
  building it is a spike that exchanges a real code against Qori's own
  registered redirect — anyone's.
- **Whether Google's provider sections are independent is unknown.** One
  Cloud project will hold Drive, YouTube and the Peer's sign-in; `T-093`
  could only read documentation on what a revoke in one does to the others.
  Connect all three on one account and disconnect one before promising a
  creator that the sections stand alone — anyone's.

## Re-scope log

None.

## Notes

The draft of 11 September 2026 decided three things that stand: the settings
page is the deliverable and onboarding links to it; connect and disconnect
both live there; disconnecting deletes nothing. `D-016` superseded its other
three: "nothing between" — no token repair, which the developer review of
16 September 2026 named as the gap — is replaced by reconnect and the refresh
command; the Zoom and Teams exclusion was left to `decisions.md`'s "Open
decisions" and `D-018` closed it on 17 September 2026 — both are in the beta
release, in `T-100`, `T-141` and `T-101`, and none is this task's; the Vimeo
domain-lock reasoning is void, since Unlisted needs the paid plan and Episodes
open on vimeo.com (`T-090`).

Where the sources disagreed with the code, the code was followed. `CLAUDE.md`
said then that contracts are bound in `AppServiceProvider` and integrations
expose `name()`; they are bound in `IntegrationServiceProvider` (`:29-39`) and
expose `provider()` (`app/Integrations/Contracts/ResolvesMedia.php:29`), which
is what `CLAUDE.md` says now. The tiers research asked for `drive.file` plus
`openid email`; `D-016` and the blueprint's Google section ask for
`drive.file` alone, and this task reads the account through `about.get`
instead. `docs/flows/storage.md:56` and
`DropboxStorage.php:17-19` still say Drive is excluded because its links cannot
be withdrawn; that reasoning is superseded by `D-016`, and the playback lines
are `T-094`'s to rewrite when Drive Episodes exist — this task rewrites only
the Connections section and the "no connector is live" line.

**17 September 2026 — from [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md),
routed by the planning gatekeeper.** Both Integrations captures rendered a 502
page, "A service Qori relies on isn't responding right now", instead of the
page. The pass treated it as a local dependency failure, but the cause is in
the code: `IntegrationsController::show` calls `PaymentsService::account()` on
every render and nothing catches a failure, so when Stripe cannot be read the
whole page is gone — including the disconnect a creator would need.
This task adds a section per provider to that page, and each would inherit the
same failure. Before this is `ready`, the spec should say that every section
reads its own vendor independently, and that one vendor's failure renders that
section's own sentence while the rest of the page, and its disconnect actions,
still work. Whether the Stripe section's existing read is fixed here or in a
`recovery` task of its own is the stream owner's call. Answered in part on
19 September 2026: Decisions says why no provider section can fail this way,
and the Stripe half is an open bullet with a recommendation.

`routes/console.php:18-22` says the cron does not exist and `PLAN.md` records
the Scheduler enabled on 11 September 2026; `T-091`, which depends on this
task, rewrites that comment, so this task adds its line beneath it and leaves
the comment alone. `T-093` was updated on 16 September 2026 to exercise the
creator's reconnect in both shapes and to keep
`files-get-folder-after-reconnect.json`; its open question — tokens from the
Playground or from a code-flow handler — is answered by this task existing:
the spike keeps the Playground, and this task's own round trip is the second
observation. On 19 September 2026 it took on the rest of this task's Google
bodies: `about-get.json` in its step 2, `oauth-refresh.json` and
`oauth-revoke.txt` in its step 15.

`T-091`'s draft already carries the six `VendorGrantStatus` states and
`VendorAccessService::reconnected(Connection, bool $sameAccount)` on
16 September 2026. From 19 September 2026 it also calls this task's
`AdvisoryLock` for its container lock, calls `fresh()` before each vendor call
and `markForReconnect($connection, 'unauthorized')` on a vendor 401, and
registers `App\Listeners\ResumeGrantsAfterReconnect` on
`ConnectionReconnected`; nothing here waits on it.

`docs/planning/vendor-accounts.md` records what the owner must open, sign up
for and pay for per provider (`D-018`), so the prerequisites behind each
section of this page have a home and Preconditions here names only what a
developer sets up locally. Two clauses in it bind Qori rather than the creator
— YouTube's developer policies and Vimeo's developer agreement on charging for
access — and stay the owner's open questions; they belong to `T-090`'s
sections, not to this task's Google one, and nothing here waits on them.

`lang/en/connections.php` is created here and shared: `T-091` adds
`connections.grants.*`, each provider task its `connections.providers.<value>.*`,
with a `recommended` line and its limitation lines for every tier it names, its
`disconnect.in_qori` and `account_change.in_qori` lines, and, in
`ProviderSections::ESSENTIAL`, which of those limitation lines sit above the
disclosure (`D-021`).
The Integrations page's Stripe copy stays inline (`Integrations.vue:75-92`),
as `T-067` left it; nothing new on the page is inline.

**18 September 2026 — `D-025` narrows the refusal**, which left with `T-152`
on 20 September 2026 and is kept here because it is why `T-123` was ever a
dependency. `guardProviderConnected()` applies only to a provider whose `content` is an
account-bound item id — `dropbox`, `google_drive`, `onedrive` — where the id
means nothing without the account that holds it. It never applies to a
live Episode carrying a pasted `join_url` (`zoom`, `teams`, or the new
`EpisodeProvider::Link`), nor to a `link` material row: a pasted URL is a
supported unconnected tier standing in beside `D-016` until each connector
lands, and `D-018`'s rule is that a tier is explained, never refused. Only
automatic recording detection needs the Zoom connection, and that is `T-141`
and `T-142`. `T-123` adds `EpisodeProvider::Link` with `connection()` returning
null, so the guard skips it by construction rather than by a list this task has
to keep. Corrected on 19 September 2026: this note first listed `vimeo`
among the account-bound providers. It is not one — `VimeoVideos::linkFor()`
builds the player URL from the id without the account
(`app/Integrations/Vimeo/VimeoVideos.php:62-86`), and the browser runs add a
Vimeo Episode with nothing connected (`tests/e2e/support/creator.ts:109-125`)
— so the guard's list is `EpisodeProvider::isAccountBound()` (Decisions), and
what `T-090`'s Vimeo picker needs is `T-090`'s.

**19 September 2026 — `depends: T-067, T-093, T-123`**, which became
`T-067, T-093` on 20 September 2026 when `T-152` took the Episode guard and
`T-123` with it. `T-093` because every
Google body the Tests read is its fixture, and because its Q1 can change this
task's Google half: a picked folder that refuses a permission leaves the owner
choosing between per-file grants and the restricted `drive` scope, and the
second changes `GoogleAccounts::requiredScopes()`, the consent copy and the
Acceptance, and brings Google's restricted-scope verification before any
creator connects. `T-123` because it adds `EpisodeProvider::Link` to the file
this task adds `isAccountBound()` to, and edits `EpisodeService.php`,
`EpisodeServiceTest.php`, `lang/en/errors.php` and `config/qori.php` before
it. `T-124` and `T-130`, ready in `classroom`, also edit
`app/Services/EpisodeService.php`, and `T-130` `lang/en/errors.php` and
`docs/flows/README.md`; `php artisan qori:tasks` shows the clash if one is
`doing` beside this, and whoever claims second rebases. Since the split,
`app/Services/EpisodeService.php` and `lang/en/errors.php`'s two `series.*`
keys are `T-152`'s and this task touches neither, so the only clash left with
`classroom` is `config/qori.php`.

**20 September 2026 — three defects in this task, found while executing it.**
Each is recorded here rather than improvised around, as
[`PROCESS.md`](../PROCESS.md)'s "Scope is the contract" requires: the Scope
was satisfied in every case and nothing about what was built changed.

1. **Tests 3 and 4 cannot both hold as written.** Case 3 wants a tier that
   does not belong to the provider refused by validation; case 4 wants Zoom,
   which names no `ProviderTier` case at all, refused with
   `errors.connections.not_available` by the Service. If
   `BeginConnectionRequest` always narrows to `ProviderTier::forProvider()`,
   Zoom 422s on every value before the Service can answer. Built: the rule
   narrows with `->only($offered)` when the provider offers tiers and falls
   back to a plain `Rule::enum(ProviderTier::class)` when it offers none, so a
   provider with no tier gets the honest answer — the account cannot be
   connected — rather than a field error about a dropdown nobody was shown.
   Case 3's own example, `dropbox_basic`, is not a `ProviderTier` case, so it
   422s either way.
2. **Cases 35 and 37 each ask for two things one request cannot both do.**
   Both say "302 to Integrations" _and_ "`ConnectionsDestination::KEY` taken".
   With a forwarding address present the redirect goes there, not to
   Integrations — which is what the Decisions paragraph requires. Built: the
   two readings are split across the cases rather than a third behaviour
   invented. Case 35 runs with no forwarding address and asserts Integrations
   and an absent key; case 36 runs with one and asserts the redirect goes to
   it; case 37 asserts Integrations on the GET and the spent address on the
   POST. Every clause is covered; no single request asserts both, because none
   can.
3. **Tests 2, 14 and 19 expect 403, which a form POST does not get.**
   `AppException::render()` (`app/Exceptions/AppException.php:248-288`)
   returns a status response only when the request expects JSON or the method
   is `GET`; otherwise it flashes the toast and returns `back()`. That is the
   app's global behaviour for every form POST and is not this task's to
   change. Built: those cases use `postJson`/`deleteJson` and assert 403 with
   the `error.code`, which satisfies the spec literally. Note that the
   neighbouring `tests/Feature/Share/PaymentsDisconnectTest.php:119-126`
   asserts the same refusal the other way, as a redirect, so the browser path
   for these refusals is specified nowhere and asserted nowhere — carried into
   the report as a finding.

**20 September 2026 — `needs_reconnect_at` was renamed after this task
shipped.** It is `reconnect_required_at` now, by
`database/migrations/2026_09_20_000300_rename_reconnect_column_and_google_personal_tier.php`,
and `ProviderTier::GoogleFree` / `google_free` is
`ProviderTier::GooglePersonal` / `google_personal` with the label "Personal
Google account". The same change stamps `refreshed_at` in
`ConnectionService::write()`, so a first connect records when Qori obtained
its tokens rather than leaving the column null until something renews them.
Everything above is left as it was written, because it is the record of what
was built on the day; read the column and tier names in it as the old ones.
The vocabulary around the column — `needsReconnect()`, `markForReconnect()`,
`ConnectionNeedsReconnectNotification`, `reconnect_reason` and the "Connect
again" button — is unchanged.
