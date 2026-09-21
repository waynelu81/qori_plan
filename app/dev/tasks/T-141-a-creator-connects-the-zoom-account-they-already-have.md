---
id: T-141
title: A creator connects the Zoom account they already have and is told whether it keeps cloud recordings
stream: storage
status: draft
owner: unassigned
estimate: M
depends: T-044, T-122
blocks: T-100, T-142
---

# T-141 — A creator connects the Zoom account they already have and is told whether it keeps cloud recordings

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 18 September 2026 from
> `D-027`, `D-031`, `D-021` and `D-018`, on `T-044`'s `ConnectsAccounts`
> contract, with the Zoom half of `T-100`'s draft moved here. It reads
> `T-122`'s `recordings/user_settings.*` and `recordings/user_me.*` fixtures
> and the two `oauth/token.*` fixtures whichever spike authorises the app
> first captures, none of which exist yet. Amended on 19 September 2026 from
> `D-034`: `ZoomClient` keeps its own timeout, and a caller's
> `$timeoutSeconds` is a budget that may only shorten it. The same day
> `T-100` took `ZoomClient` and moved its tests under
> `tests/Feature/Integrations/Zoom/`, so it depends on this task.

## Why

Nothing in Qori can hold a Zoom token. `app/Integrations/` has `CloudflareR2`,
`Contracts`, `Dropbox`, `Stripe` and `Vimeo` and no Zoom folder; every mention
of Zoom under `app/` names it and does nothing with it —
`ConnectionProvider::Zoom` (`app/Enums/ConnectionProvider.php:18`),
`EpisodeProvider::Zoom` and its `connection()` arm
(`app/Enums/EpisodeProvider.php:23,48`), `EpisodeType::Live`'s allowed
providers (`app/Enums/EpisodeType.php:35`) and the join-link arm of
`StoreEpisodeRequest::content()`
(`app/Http/Requests/Share/StoreEpisodeRequest.php:190`), which stores a string
nothing calls; `app/Providers/IntegrationServiceProvider.php:35`
tags three media providers and binds no connector; `config/services.php` has a
`stripe` block (`:27`) and nothing for Zoom; `docs/flows/storage.md:7` says
"No connector is live" and `docs/flows/README.md:42-43` says the Zoom/Teams
integration has no flow file because it is not built. `T-044` builds the
connect machinery with Google Drive as its first provider, and `T-100` drafted
Zoom's connector inside the registrant journey — an `L` task on four unowned
drafts, with its HTTP client in `app/Integrations/Concerns/ZoomHttpClient.php`,
which `D-022` forbids and
`ArchitectureTest::test_integrations_keep_no_shared_concerns_folder`
(`tests/Feature/ArchitectureTest.php:45`) refuses. `D-027` makes recording
detection a scheduled REST poll with the creator's own token, and `D-031` puts
that detection the sprint after the manual checkpoint, on `T-044`'s contract;
so the connector has to land before `T-142` and `T-143`, without waiting on
registrants, and it has to tell the creator the one fact that decides whether
detection can work at all: whether their Zoom plan keeps cloud recordings.
Today no screen can, because nothing reads Zoom's settings.

Afterwards the Integrations page has a Zoom section on `T-044`'s
`ProviderSection.vue`: five tiers in the dropdown, Basic included, each with
what Qori recommends and at most three essential limitations above Connect
(`D-021` rule 4). Connect sends the owner to Zoom's authorization page through
`T-044`'s `share.connections.begin`; the landing exchanges the code through
`App\Integrations\Zoom\ZoomAccounts`, reads `GET /users/me` for the account
and `GET /users/me/settings` for its recording settings, and stores the tokens
encrypted with the tier and four booleans in `connections.settings`. The
section then says, in a sentence beside the status, whether that account
keeps cloud recordings — on, off, or could not be read — and what to do in
each case; nothing is refused (`D-018`). Disconnecting says that recordings
already added keep working and new ones won't be found (`D-021` rule 3).
`qori:connections:refresh` renews the row's rotating refresh token.
`T-142`'s finder reads the stored token and `T-143`'s sweep skips a
connection whose `settings.cloud_recording` is false.

## Decisions taken to make this specifiable

**Zoom lands on `T-044`'s `ConnectsAccounts` unchanged, with one addition to
a Data shape: `ConnectedAccount` gains `settings`.** Connect, the landing,
the held account change, disconnect and the refresh sweep are `T-044`'s and
this task rewires none of them. What Zoom adds is a few facts about the
account, read at the same moment as its identity, and `ConnectedAccount` is
what `identity()` returns; so it carries them, as Qori's own keys, and
`ConnectionService::finaliseConnection()` and `switchAccount()` write them beside
`tier`, merged over the row's existing `settings` so a key another task stores
there later survives a reconnect. A second contract for "what the connector
learned" would be one more thing to bind for one consumer. The merge writes
what the connector answered, `null` included: a reconnect whose settings call
failed replaces a stored `true` with `null`, so the page says the setting
could not be read rather than repeating a value from an earlier connect that
may no longer hold. The held account change carries `settings` too —
`T-044`'s hold payload and `heldAccountChange()`'s rebuild gain the array
(Notes) — so a Switch writes the settings the landing read for the incoming
account, never the outgoing one's.

**The settings are read inside `identity()`, as a second call, best effort.**
The landing already holds the access token there and nowhere else; a separate
step would need the token handed around again. A settings call that fails —
`T-122` question 5 leaves open whether a Basic account answers
`GET /users/me/settings` at all (`recordings/user_settings.basic.<status>.json`)
— leaves the settings unknown, logs at warning, and the connect succeeds. A
tier is explained, never refused (`D-018`), and the page's `unknown` line says
what happened.

**Four booleans under the reference's key names, resolved in the Zoom
folder; Zoom's words never leave `app/Integrations/Zoom`.** The merged
reference and the sprint brief name the three fields Zoom is read for —
`recording.cloud_recording`, `recording.auto_recording` and
`recording.authenticated_view_cloud_recoding` (Zoom's spelling as `T-122`
reads it; the fixture decides) — and this task stores them under those names,
`cloud_recording`, `auto_recording` and `authenticated_view_cloud_recoding`,
with `licensed` from `/users/me`'s `type`, each `bool|null`, so a developer
reading the fixture, the row and `T-143`'s `settings.cloud_recording` sees
one word for one fact. The _values_ are Qori's: at Zoom `auto_recording` is a
word (`none`, `local`, `cloud`) and it is stored as the boolean `=== 'cloud'`,
because `CLAUDE.md` says what a vendor's value means is worked out in the
vendor's folder and nothing vendor-specific sits in `app/Support`;
`ProviderSections` reads booleans under opaque keys and holds no Zoom rule,
as a Model may hold a vendor's id in a column without knowing what it means.
`cloud_recording` is `false` when the settings say so **or** when the settings
could not be read and the account is not licensed, because a Basic account
has no cloud recording (`docs/planning/course-classroom.md`, "When there's no
cloud recording"); `null` only when neither is known.

**The page tells the creator what was read, beside the tier they chose, and
never compares the two.** `T-044` branches on nothing but which copy a tier
shows, and this task keeps that: a creator who picked Pro while the settings
say cloud recording is off gets the `off` line and its resolution, and the
dropdown stays as they set it. The lines come from a generic
`ProviderSections::ACCOUNT_LINES` constant and `accountLines()` — provider →
settings key → state (`on`, `off`, `unknown`) → lang key — so `app/Support`
reads opaque settings keys and holds no Zoom rule. An entry may name a key it
`requires`: the `auto_recording` and `authenticated_view_cloud_recoding`
lines render only when `cloud_recording` is `true`, because telling a Basic
account, or one whose settings could not be read, to turn on automatic cloud
recording or to change who may view cloud recordings is advice it cannot act
on; an `off` or `unknown` cloud line stands alone. `ProviderSection.vue`
renders the list under the status badge; no Vue page changes.

**Settings are read at connect and reconnect, not on a schedule.**
`qori:connections:refresh` swaps tokens and reads nothing else; a creator who
upgrades to Pro or turns cloud recording on connects again, and the `off` line
says so. A daily settings read per connection is a vendor call nobody asked
for; Check now (`T-144`) is where a later re-read belongs, and its draft is
told (Notes).

**`requiredScopes()` names the four scopes this story reads; the seventeen
frozen on the app are `T-122`'s.** `user:read:user` (`/users/me`),
`user:read:settings` (`/users/me/settings`),
`cloud_recording:read:list_recording_files` and
`meeting:read:list_past_instances` (`T-142`'s two reads). Zoom's authorization
URL carries no `scope` parameter — the app's configured scopes are what a user
grants — and `ZoomAccounts::finaliseConnection()` checks the token response's
`scope` against `requiredScopes()` itself, as `T-044`'s contract has every
connector do: a token missing one is revoked at Zoom, best effort, and
answered `ScopeDeclined`, which `ConnectionService` shows as
`errors.connections.scope_declined`, as it does Google's. The exact granular
spellings are question 8 of the spike (below).

**The landing's words are Zoom's, so `ZoomAccounts::finaliseConnection()`
reads them and answers a `ConnectionLanding`** (`T-044`'s contract, `D-022`).
It compares the landing's `state` with the pending one by `hash_equals`
before it spends anything, so a mismatch, with an error or without, is
`NotFromQori`. `error=access_denied`, the OAuth 2.0 word for a refusal
(https://www.rfc-editor.org/rfc/rfc6749#section-4.1.2.1), is `Declined`; any
other `error` word is `Failed` with that word as `upstream`; no `code` is
`Failed`. No Zoom landing word is recorded for an account whose admin has
not approved the app (`limits.common.admin`), so no arm answers
`AdminBlocked`; that and the refusal word are provisional until this task's
first round trip shows what Zoom sends back. The exchange then answers
`Connected`, `ScopeDeclined`, or `Failed` with `connection` when Zoom does not
answer and the status when it refuses the code — never an exception, so
`ConnectionService` decides what each means for the Group.

**Zoom has no offline scope; the refresh token is the offline access.** Every
code exchange returns a refresh token that lasts 90 days and rotates on each
use (`vendor-accounts.md`, Zoom section), so `refreshesOnSchedule()` is true
and `T-044`'s daily `qori:connections:refresh` keeps the 90 days from lapsing
under its `AdvisoryLock`, because two refreshes at once invalidate one. The
access token lasts an hour; `T-142` and `T-143` call
`ConnectionService::fresh()` before the finder, which is `T-044`'s existing
rule for any vendor call (Notes).

**The token endpoint takes HTTP Basic with the client id and secret,
form-encoded, and PKCE is sent when the connector says it supports it
(provisional).** Zoom's OAuth reference authenticates the token call with the
client credentials in the `Authorization` header, not the body, and
documents `code_challenge` with `S256`; `supportsPkce()` answers `true` until
this task's first round trip says otherwise. `T-044` already keeps the
verifier beside the nonce, so nothing new travels in the session.

**`ZoomClient` sets its own timeout and retry, a caller's `$timeoutSeconds` is
a budget that may only shorten the timeout, and the retry names what it
retries** (`D-034`). `ZoomClient::TIMEOUT_SECONDS` is Zoom's own limit on one
call (provisional — see below), and `api()` and `oauth()` wait whichever is
shorter, it or the budget. `T-044` passes its
`ConnectionService::REQUEST_TIMEOUT_SECONDS` inside a request and
`SWEEP_TIMEOUT_SECONDS` from the command, as its contract's methods take
them, because an integration may not import `App\Services`
(`tests/Feature/ArchitectureTest.php:139`). The OAuth
endpoints get no retry — an authorization code is single-use, the reason
`Stripe\Client::getClientOAuth()` gives — and the API reads get
`retry(2, 200, $when, throw: false)` with `$when` accepting a
`ConnectionException` or a server error only. Laravel's default retries every
failed response, 4xx included
(`vendor/laravel/framework/src/Illuminate/Http/Client/PendingRequest.php:1088`,
`$shouldRetry` is `true` with no callback), and a `401` or `404` asked twice
is a wasted call and a slower landing. `T-142`'s `ZoomRecordings` inherits
the same client. `unwrap()` throws `AppException::upstreamUnavailable` with
`upstream` set to the status and Zoom's own `code` and `message` in
`devMessage`, as `Stripe\Client::unwrap()` does; a `401` reaches the caller as
that exception, and `T-044`'s `refresh()` path is what turns a refused refresh
into `needs_reconnect`.

**`external_id` is `/users/me`'s `id`; `account_name` is its `email`.** As
`T-044` takes `permissionId` and `emailAddress` from Google: the id is what
stays the same when an address changes, and the address is what a person
recognises on the page. `display_name` is not stored, because no column holds
it. Provisional until `recordings/user_me.pro.200.json`.

**Five tiers, Basic included, with `T-100`'s tier values.** `ProviderTier` gains
`ZoomBasic`, `ZoomPro`, `ZoomBusiness`, `ZoomBusinessPlus` and
`ZoomEnterprise`, offered in that order, cheapest first. Every tier a creator
can hold is in the dropdown (`D-018`); `T-100`'s draft loses the cases and
its `ZoomAccounts` to this task and adds its registration lines beside these
when it lands (Notes).

**The essential lines follow `D-021` rule 4 for a provider with no container
this sprint, Basic's differ from the paid tiers', and a line about cloud
recording is keyed under each paid tier, never under `common`.** `T-044`'s
`limitsFor()` shows every `limits.common.*` line on every tier, nothing
dropped, so a `common` line has to be true on Basic too; "cloud recording
must be on", "if Zoom deletes a recording", "Qori can only look for the
recording of a session whose join link…" and "Zoom can take up to :hours
hours" are not, and beside `zoom_basic.no_cloud_recording` they would
contradict it. Those four — `cloud_setting`, `auto_delete`, `meeting_links`
and `wait` — sit under `zoom_pro`, `zoom_business`, `zoom_business_plus` and
`zoom_enterprise`, the same English four times, written once in
`lang/en/connections.php` as one local array spread into each paid tier's
`limits` entry (Copy); `common` keeps `sharing`, `no_account` and `admin`,
which hold on Basic. On every paid tier: what stops sharing outright is cloud
recording being off in the settings (`<tier>.cloud_setting`); what Peers need
is a recording shared with everyone who has the link, because "Sign in to
Zoom" and on-demand registration wall off anyone without a Zoom account
(`common.sharing`); the one-folder rule has no counterpart until `T-100`'s
container, so the third slot goes to `<tier>.auto_delete`, the one limitation
that takes a recording away after Peers already have it — the three the
merged reference names. On Basic there
is no cloud recording to auto-delete, so its three are what stops sharing
outright (`zoom_basic.no_cloud_recording`), the meeting length that turns one
class into several meetings (`zoom_basic.meeting_length`, which the reference
counts among Basic's three) and `common.sharing`, which still says what Peers
need once a recording is put anywhere. `common.no_account` sits in `more`: it
is reassurance, not a limit. `T-100` replaces the entry when its container
arrives.

**The disconnect and account-change lines say what the finder does with a
stored link: nothing.** Watch goes to the stored link and makes no vendor
call (`D-027`), so recordings already added keep working; the finder needs a
token, so new ones are not found until the account is connected again. A
switch to another account changes where Qori looks, not what is stored.

**Vendor names in this copy are under `D-016`'s stated exception for
provider-choice copy, and the only vendor named is the one being chosen.**
Zoom is named because the creator is choosing whether to connect Zoom and on
which plan — the footing `T-044`'s Google lines stand on; `D-025` extends the
same exception to the chat platforms and to Join and Watch, and the sprint
brief allows a vendor name nowhere else. The merged reference's Basic
sentence names two video hosts to upload a local recording to; that is a
recommendation of other providers inside Zoom's limits, which no exception
covers, so `zoom_basic.no_cloud_recording` says "somewhere :peer_plural can
open with the link" and names neither. No line here is under `live.*`, and
none reaches a Peer.

**Every number in the copy comes from `config('qori.connections.zoom')`.**
`basic_meeting_minutes` (40, provisional until spike question 5) and
`processing_hours` (24, Zoom's own "occasionally up to 24 hours"). The
reference's "about twice the session's length" is not written: it would be a
second processing figure in a sentence beside the configured one, and the
ceiling is what a creator waiting for a recording needs. The block sits
inside `T-044`'s `connections` key beside `google_drive`; `qori.live` is
`T-123`'s and this task reads none of it.

**The revoke call sends the token as a form field, provisional.** Zoom's
reference shows `POST /oauth/revoke?token=…` with the token in the query
string, and a query string is what request logs keep. The draft sends it
form-encoded under Basic auth; if the first round trip shows Zoom refusing
that, the query form is used and the report says so.

**No new route, page or Vue page.** Zoom rides `T-044`'s six connection routes
and its landing. The begin route and the account-change page carry the slug
`zoom` in `{provider}`; the landing is `u/connections/zoom/finalise`, named
for the vendor rather than the service (`D-033`). The section is a mount of
`ProviderSection.vue`, which is the whole point of `T-044`'s shape. The one Vue
change is the list of account lines under the status badge.

**The connector's tests sit under `tests/Feature/Integrations/Zoom/`, beside
`T-142`'s.** `T-142` names `tests/Feature/Integrations/Zoom/ZoomRecordingsTest.php`
and both classes share `ZoomClient` and the same fixture directory, so one
folder holds everything that fakes Zoom, as `T-044`'s `GoogleAccountsTest.php`
sits in `tests/Feature/Integrations/Google/`.

**Every field read from Zoom is cited to a fixture.** `oauth/token.*` are
named by `T-099` and carried by `T-122`'s Files table too, captured by
whichever spike authorises the app first; `recordings/user_me.*` and
`recordings/user_settings.*` are `T-122`'s. Where a fixture is not yet committed the field is an expectation
from Zoom's reference, and the draft says so in "Before this can be ready".
Tests fake Zoom with `Http::fake()` and the fixture bodies, and a Zoom
connection in a test is `Connection::factory()->zoom()`.

## Preconditions

`T-044` done, so `ConnectsAccounts`, `ConnectionLanding` and its
`ConnectionLandingStatus`, `ConnectionTokens`, `ConnectedAccount`,
`RefreshResult`, `ProviderTier`, `ProviderSections`, `ConnectionService`,
`ConnectionsController`, `ConnectionFinaliseController`, the six routes and the
landing, `ProviderSection.vue`, `lang/en/connections.php`,
`ConnectionFactory`'s `needsReconnect()` and `expiring()` states,
`qori:connections:refresh` and `docs/tinker/connections.md` exist. `T-122`
done, so `tests/Fixtures/zoom/README.md`, the `recordings/user_*` fixtures
and the two `oauth/token.*` fixtures exist.

**Data this task verifies against:** a clean database. For the browser walk,
any Group owned by the signed-in person, with no Zoom connection.

**Equipment:** the General app in development mode on Qori's own Zoom
account (`docs/planning/vendor-accounts.md`, Zoom section, steps 1–7), its
development client id and secret in `.env` as `ZOOM_CLIENT_ID` and
`ZOOM_CLIENT_SECRET`, and `http://127.0.0.1:8001/u/connections/zoom/finalise`
on the app's redirect allow list — the numeric address, because Zoom's forum
reports `localhost` refused (step 5), which means `APP_URL=http://127.0.0.1:8001`
for the walk, since the landing URL is built from it. A browser signed in as
the owner. The Pro licence on that account shows the `on` line; the Basic
outside account under the beta share, if `T-122` obtained it, shows the `off`
line.

**Spike:** `T-122` commits `recordings/user_settings.pro.200.json`,
`recordings/user_settings.basic.<status>.json`,
`recordings/user_me.pro.200.json` and `recordings/user_me.basic.<status>.json`
under `tests/Fixtures/zoom/`, in `T-099`'s `<group>/<call>.<case>.<status>`
naming, and — because the storage stream runs it first and its Files table
carries the row — `oauth/token.authorization_code.200.json` and
`oauth/token.refresh.200.json`, captured on the way to its bearer token under
`T-099`'s redaction map. If `T-099` authorises the app first, the same two
paths are its, and this task reads them from whichever spike committed them.
`oauth/token.refresh_reused.<status>.json` is `T-099`'s alone and is not a
precondition: until it exists the reused-token case fakes a 400 body
`{"error": "invalid_grant"}` from Zoom's OAuth reference, and swaps in the
fixture when `T-099` lands (Tests, case 5). **No field named in this task has
been observed by Qori.** Every shape comes from Zoom's OAuth and Users references and is an
expectation until its fixture exists.

## Scope

**In:**

- `app/Integrations/Zoom/ZoomClient.php`: the API and OAuth request builders
  and `unwrap()`, with its own timeout that a caller's budget may only
  shorten (`D-034`), no retry on OAuth, two attempts on reads for transport
  failures and server errors only.
- `app/Integrations/Zoom/ZoomAccounts.php` implementing `ConnectsAccounts`:
  the authorization URL, the code exchange, refresh, revoke, and `identity()`
  reading `/users/me` and `/users/me/settings` into `ConnectedAccount`, tagged
  `account-connectors`.
- `ConnectedAccount::$settings`, written by `ConnectionService::finaliseConnection()`
  and `switchAccount()` beside `tier`, merged over the row's `settings`.
- Five `ProviderTier` cases; `ProviderSections::ESSENTIAL['zoom']`,
  `ACCOUNT_LINES`, `accountLines()` and the `account` entry in `props()`; the
  list in `ProviderSection.vue`.
- Zoom's copy in `lang/en/connections.php`: name, description, five tiers'
  labels, help and recommendations, the limitation lines, the account lines,
  `disconnect.in_qori` and `account_change.in_qori`.
- `config/services.php`'s `zoom` block, the two env keys in `.env.example`,
  `config/qori.php`'s `connections.zoom` numbers.
- `ConnectionFactory::zoom()`.
- `docs/flows/storage.md`'s Connections section (the Zoom row and the
  settings read) and a Zoom paragraph in `docs/tinker/connections.md`.
- `tests/Feature/Integrations/Zoom/`, created here for `ZoomAccountsTest.php`;
  `T-142` adds `ZoomRecordingsTest.php` beside it.

**Out:**

- Finding a recording (`T-142`), the sweep and the review hold (`T-143`),
  publish, reject and Check now (`T-144`).
- Registrants, the meeting picker and the Series container (`T-100`,
  `T-091`); Teams (`T-101`).
- Zoom webhooks and `app_deauthorized`, which need a published app; the
  Marketplace submission itself (the owner's, `vendor-accounts.md`).
- Re-reading the settings on a schedule or from Check now; changing any Zoom
  setting by API (`cloud_recording:update:recording_settings` is on the
  frozen list and unused here).
- Any Peer-facing copy or route, and any change to the Episode form: a Zoom
  join link is pasted whether or not Zoom is connected (`D-025`), and
  `guardProviderConnected()`'s exemption for live Episodes is `T-044`'s.
- A before-buying line (`T-092`): Zoom asks a Peer for nothing.
- Storing `auto_delete_cmr_days` or anything else the spike reads beyond the
  four booleans.

## Files

| Path                                                      | Change | Notes                                                                                                         |
| --------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| `app/Integrations/Zoom/ZoomClient.php`                    | new    | `api()`, `oauth()`, `unwrap()`; the only Zoom base URLs                                                       |
| `app/Integrations/Zoom/ZoomAccounts.php`                  | new    | `ConnectsAccounts`; identity plus settings                                                                    |
| `app/Data/ConnectedAccount.php`                           | edit   | `settings` (`T-044` creates the file, not in the repo today)                                                  |
| `app/Services/ConnectionService.php`                      | edit   | `finaliseConnection()` and `switchAccount()` merge `settings` from the account beside `tier` (`T-044`'s file) |
| `app/Enums/ProviderTier.php`                              | edit   | Five Zoom cases; `provider()` arm; `forProvider(Zoom)` order (`T-044`'s file)                                 |
| `app/Support/ProviderSections.php`                        | edit   | `ESSENTIAL['zoom']`, `ACCOUNT_LINES`, `accountLines()`, `account` in `props()` (`T-044`'s file)               |
| `app/Providers/IntegrationServiceProvider.php`            | edit   | `ZoomAccounts` in the `account-connectors` tag                                                                |
| `resources/js/components/share/ProviderSection.vue`       | edit   | Renders `account.lines` under the status badge (`T-044`'s file)                                               |
| `lang/en/connections.php`                                 | edit   | Copy below (`T-044`'s new file)                                                                               |
| `config/services.php`                                     | edit   | `zoom` block                                                                                                  |
| `config/qori.php`                                         | edit   | `connections.zoom` inside `T-044`'s `connections` key                                                         |
| `.env.example`                                            | edit   | `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET`                                                                        |
| `database/factories/ConnectionFactory.php`                | edit   | `zoom()` state                                                                                                |
| `docs/flows/storage.md`                                   | edit   | Connections section (`:80`): the Zoom row, what the landing stores, what disconnect leaves                    |
| `docs/tinker/connections.md`                              | edit   | A Zoom paragraph: fake the round trip, read `settings`, run the refresh (`T-044`'s new file)                  |
| `tests/Feature/Integrations/Zoom/ZoomAccountsTest.php`    | new    | 11 cases; the directory is new, and `T-142` adds `ZoomRecordingsTest.php` beside it                           |
| `tests/Feature/Share/ZoomConnectTest.php`                 | new    | 11 cases                                                                                                      |
| `tests/Feature/Share/ProviderSectionsTest.php`            | edit   | +1 case (`T-044`'s file)                                                                                      |
| `tests/Feature/Console/RefreshConnectionsCommandTest.php` | edit   | +1 case (`T-044`'s file)                                                                                      |
| `tests/Feature/Share/ConnectionsConnectTest.php`          | edit   | Its "no connector" case stops using Zoom (`T-044`'s file); see Tests                                          |

The fixtures this task reads are `T-122`'s — `recordings/user_*` and, by its
conditional Files row, the two `oauth/token.*` — and are not created here. No route file changes; no seeder writes a connection.

## Database

None. Keys this task writes to `connections.settings` (jsonb, `'array'` cast,
`app/Models/Connection.php:83`), beside `T-044`'s `tier`, under the names the
merged reference gives Zoom's fields (Decisions):

| Key                                 | Type         | Written from                                                                                                |
| ----------------------------------- | ------------ | ----------------------------------------------------------------------------------------------------------- |
| `cloud_recording`                   | `bool\|null` | `recording.cloud_recording`; `false` when unreadable and `licensed` is `false`; `null` when unknown         |
| `auto_recording`                    | `bool\|null` | `recording.auto_recording === 'cloud'`, the word resolved in the Zoom folder; `null` when unreadable        |
| `authenticated_view_cloud_recoding` | `bool\|null` | `recording.authenticated_view_cloud_recoding` (Zoom's spelling as `T-122` reads it); `null` when unreadable |
| `licensed`                          | `bool\|null` | `/users/me` `type === 2`; `false` for any other integer; `null` when absent                                 |

## Code

```php
namespace App\Integrations\Zoom;

use App\Exceptions\AppException;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Client\PendingRequest;
use Illuminate\Http\Client\RequestException;
use Illuminate\Http\Client\Response;
use Illuminate\Support\Facades\Http;
use Throwable;

/**
 * HTTP behaviour for Zoom's REST API and its OAuth endpoints, injected into
 * ZoomAccounts (T-141), ZoomRecordings (T-142) and ZoomMeetings (T-100). The
 * only place a Zoom base URL appears. Laravel's HTTP client, as Stripe\Client:
 * Http::fake() must be able to intercept every call. Every $timeoutSeconds is
 * the caller's budget, which this client may only shorten: each request waits
 * the shorter of TIMEOUT_SECONDS and the budget (D-034).
 */
class ZoomClient
{
    public const API_URL = 'https://api.zoom.us/v2';

    public const OAUTH_URL = 'https://zoom.us/oauth';

    /** Zoom's own limit on one request, which a caller's budget may only shorten (D-034). Provisional — see below. */
    public const TIMEOUT_SECONDS = 15;

    /** Attempts per API read, transport failures and 5xx only. */
    public const READ_ATTEMPTS = 2;

    public const READ_RETRY_MILLISECONDS = 200;

    /**
     * Http::acceptJson()->withToken($accessToken)->baseUrl(self::API_URL)->timeout(min(self::TIMEOUT_SECONDS, $timeoutSeconds))
     *     ->retry(self::READ_ATTEMPTS, self::READ_RETRY_MILLISECONDS, self::retryWhen(...), throw: false)
     */
    public function api(string $accessToken, int $timeoutSeconds): PendingRequest;

    /**
     * Http::asForm()->withBasicAuth(config('services.zoom.client_id'), config('services.zoom.client_secret'))
     *     ->baseUrl(self::OAUTH_URL)->timeout(min(self::TIMEOUT_SECONDS, $timeoutSeconds)) — no retry: an authorization
     *     code is single-use.
     */
    public function oauth(int $timeoutSeconds): PendingRequest;

    /**
     * The JSON body of a 2xx. Otherwise AppException::upstreamUnavailable(devMessage:
     * "Zoom {$context} failed: {code} {message}" from Zoom's error body
     * ({"code": 124, "message": "Invalid access token"}) or "no message", upstream: (string) status,
     * langKey: $langKey).
     *
     * @return array<string, mixed>
     */
    public function unwrap(Response $response, string $context, ?string $langKey = null): array;

    /** True for a ConnectionException, or a RequestException whose response is a 5xx; false for every 4xx. */
    private static function retryWhen(Throwable $exception): bool;
}
```

```php
namespace App\Integrations\Zoom;

use App\Data\ConnectedAccount;
use App\Data\ConnectionLanding;
use App\Data\ConnectionTokens;
use App\Data\RefreshResult;
use App\Enums\ConnectionProvider;
use App\Exceptions\AppException;
use App\Integrations\Contracts\ConnectsAccounts;
use App\Models\Connection;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Support\Facades\Log;

/**
 * https://developers.zoom.us/docs/integrations/oauth/ (authorize, token, revoke) and
 * https://developers.zoom.us/docs/api/users/ (users/me, users/me/settings).
 * Every field is an expectation until its fixture under tests/Fixtures/zoom/ exists.
 * Every $timeoutSeconds T-044's contract passes is a budget ZoomClient may only shorten (D-034).
 */
class ZoomAccounts implements ConnectsAccounts
{
    public const AUTHORIZE_URL = 'https://zoom.us/oauth/authorize';

    public const SCOPE_USER = 'user:read:user';

    public const SCOPE_USER_SETTINGS = 'user:read:settings';

    public const SCOPE_RECORDING_FILES = 'cloud_recording:read:list_recording_files';

    public const SCOPE_PAST_INSTANCES = 'meeting:read:list_past_instances';

    /** /users/me `type`: 1 Basic, 2 Licensed; anything else is not licensed. Provisional until recordings/user_me.*. */
    public const USER_TYPE_LICENSED = 2;

    /** recording.auto_recording value that means every meeting records to the cloud. */
    public const AUTO_RECORDING_CLOUD = 'cloud';

    public function __construct(private ZoomClient $client) {}

    public function provider(): ConnectionProvider;            // ConnectionProvider::Zoom

    public function supportsPkce(): bool;                      // true (provisional — see "Before this can be ready")

    public function refreshesOnSchedule(): bool;               // true: the refresh token lasts 90 days and rotates on use

    /** @return list<string> [SCOPE_USER, SCOPE_USER_SETTINGS, SCOPE_RECORDING_FILES, SCOPE_PAST_INSTANCES] */
    public function requiredScopes(): array;

    /**
     * AUTHORIZE_URL.'?'.http_build_query([response_type => code, client_id, redirect_uri, state]
     *     + ($codeChallenge === null ? [] : [code_challenge => $codeChallenge, code_challenge_method => 'S256'])).
     * No scope (the app's configured scopes are granted) and no login hint (Zoom has no parameter for one;
     * $loginHint is ignored).
     */
    public function beginConnection(string $redirectUrl, string $state, ?string $codeChallenge, ?string $loginHint): string;

    /**
     * T-044's contract: read the landing and spend its code, never throwing (D-022), in Connect::finaliseOnboarding()'s
     * order (app/Integrations/Stripe/Connect.php:74-151), so a forged or stale landing spends nothing.
     * $matches = $expectedState !== '' && hash_equals($expectedState, the landing's state):
     *   an error whose state is present and does not match → notFromQori(); error=access_denied → declined();
     *   any other error word → failed(<the word>); no error and ! $matches → notFromQori(); no code → failed();
     *   no call on any of these. No arm answers adminBlocked(): no Zoom landing word is recorded for it
     *   (provisional, as access_denied is, until the first round trip).
     * $this->client->oauth($timeoutSeconds)->post('/token', [grant_type => authorization_code, code, redirect_uri
     *     (+ code_verifier when given)]) → access_token, token_type, refresh_token, expires_in (3600),
     *     scope (space-separated)  [oauth/token.authorization_code.200.json];
     *   a ConnectionException → failed('connection'); a non-2xx → failed((string) status), logged with Zoom's `error`
     *   word alone, never the body, which may quote the code;
     *   a granted scope short of requiredScopes() → ->oauth($timeoutSeconds)->post('/revoke', [token => that access_token]),
     *   best effort, then scopeDeclined(); else connected(tokensFrom()).
     */
    public function finaliseConnection(array $landing, string $expectedState, string $redirectUrl, ?string $codeVerifier, int $timeoutSeconds): ConnectionLanding;

    /**
     * ->post('/token', [grant_type => refresh_token, refresh_token]) → a new pair, the refresh token rotated
     * [oauth/token.refresh.200.json] → RefreshResult::renewed(tokensFrom()).
     * A 400 whose `error` is invalid_grant → RefreshResult::revoked('400')  [oauth/token.refresh_reused.<status>.json];
     * any other non-2xx → ::unavailable((string) status); a ConnectionException → ::unavailable(null). Never throws.
     */
    public function refresh(string $refreshToken, int $timeoutSeconds): RefreshResult;

    /**
     * ->post('/revoke', [token => $connection->access_token]). Best effort: a non-2xx or a
     * ConnectionException is Log::warning('Zoom revoke failed', [...]) and swallowed. Nothing when access_token is null.
     */
    public function revoke(Connection $connection, int $timeoutSeconds): void;

    /**
     * $me = unwrap($this->client->api($accessToken, $timeoutSeconds)->get('/users/me'), 'identity')
     *     → id (externalId), email (name and email), type  [recordings/user_me.*];
     * then ->get('/users/me/settings') → recording.*  [recordings/user_settings.*], best effort: a non-2xx,
     * a ConnectionException, or a body with no `recording` array is Log::warning() and null to settingsFrom().
     * The first call failing throws through unwrap().
     */
    public function identity(string $accessToken, int $timeoutSeconds): ConnectedAccount;

    /** access_token, refresh_token, now()->addSeconds(expires_in), explode(' ', scope). */
    private function tokensFrom(array $body): ConnectionTokens;

    /**
     * licensed: is_int($me['type'] ?? null) ? $me['type'] === USER_TYPE_LICENSED : null.
     * cloud_recording: is_bool($settings['recording']['cloud_recording'] ?? null) ? that : ($licensed === false ? false : null).
     * auto_recording: is_string($settings['recording']['auto_recording'] ?? null) ? that === AUTO_RECORDING_CLOUD : null.
     * authenticated_view_cloud_recoding: is_bool($settings['recording']['authenticated_view_cloud_recoding'] ?? null) ? that : null.
     * The keys are the reference's names for Zoom's fields; the values are booleans, so nothing outside this
     * folder ever sees 'cloud'.
     *
     * @param  array<string, mixed>  $me
     * @param  ?array<string, mixed>  $settings
     * @return array{cloud_recording: ?bool, auto_recording: ?bool, authenticated_view_cloud_recoding: ?bool, licensed: ?bool}
     */
    private function settingsFrom(array $me, ?array $settings): array;
}
```

```php
namespace App\Data;

// T-044's shape, one property added. Keys are Qori's own; the connector maps the vendor's.
class ConnectedAccount
{
    /** @param array<string, bool|null> $settings written to connections.settings beside tier */
    public function __construct(public string $externalId, public string $name, public ?string $email = null, public array $settings = []) {}
}

// App\Services\ConnectionService — T-044's finaliseConnection() and switchAccount(), one expression changed in each.
// Where T-044 writes 'settings' => ['tier' => $tier->value] (over the row's array), write:
//     'settings' => array_merge($connection?->settings ?? [], ['tier' => $tier->value], $account->settings),
// so a connector's keys and the tier replace their previous values and every other key in the column survives.
// Nulls are not filtered out: a key the connector could not read this time is written null over the old value.
// HeldAccountChange carries the ConnectedAccount, settings included: T-044's ACCOUNT_CHANGE_SESSION payload gains
// the account's settings array and heldAccountChange() rebuilds ConnectedAccount with it, so a Switch writes the
// settings the landing read for the incoming account.
```

```php
namespace App\Enums;

enum ProviderTier: string
{
    // T-044's Google cases unchanged
    case ZoomBasic = 'zoom_basic';
    case ZoomPro = 'zoom_pro';
    case ZoomBusiness = 'zoom_business';
    case ZoomBusinessPlus = 'zoom_business_plus';
    case ZoomEnterprise = 'zoom_enterprise';

    // provider(): the five Zoom cases → ConnectionProvider::Zoom
    // forProvider(ConnectionProvider::Zoom) → [ZoomBasic, ZoomPro, ZoomBusiness, ZoomBusinessPlus, ZoomEnterprise] — the dropdown's order
}
```

```php
namespace App\Support;

use App\Models\Connection;
use App\Models\Group;

class ProviderSections
{
    public const ESSENTIAL = [
        // T-044's google_drive entry unchanged
        'zoom' => [
            'zoom_basic' => ['zoom_basic.no_cloud_recording', 'zoom_basic.meeting_length', 'common.sharing'],
            'zoom_pro' => ['zoom_pro.cloud_setting', 'common.sharing', 'zoom_pro.auto_delete'],
            'zoom_business' => ['zoom_business.cloud_setting', 'common.sharing', 'zoom_business.auto_delete'],
            'zoom_business_plus' => ['zoom_business_plus.cloud_setting', 'common.sharing', 'zoom_business_plus.auto_delete'],
            'zoom_enterprise' => ['zoom_enterprise.cloud_setting', 'common.sharing', 'zoom_enterprise.auto_delete'],
        ],
    ];

    /**
     * provider value → connections.settings key → state → key relative to connections.providers.<provider>.account.,
     * in the order shown. State is 'on' for true, 'off' for false, 'unknown' for null or absent. A state with no
     * entry renders nothing. 'requires' is not a state: it names another settings key of the same provider that
     * must be true for the entry to render at all. The keys are the settings keys the provider's connector
     * writes; the values are booleans, and this class knows nothing of what the vendor calls them.
     *
     * @var array<string, array<string, array<string, string>>>
     */
    public const ACCOUNT_LINES = [
        'zoom' => [
            'cloud_recording' => ['on' => 'cloud_recording_on', 'off' => 'cloud_recording_off', 'unknown' => 'cloud_recording_unknown'],
            'auto_recording' => ['requires' => 'cloud_recording', 'off' => 'auto_recording_off'],
            'authenticated_view_cloud_recoding' => ['requires' => 'cloud_recording', 'on' => 'sign_in_required'],
        ],
    ];

    /**
     * The lines a row's settings earn under ACCOUNT_LINES[$connection->provider->value], in that order, skipping
     * every entry whose 'requires' key is not true in the row's settings, each
     * $terminology->line("connections.providers.{$provider}.account.{$line}", ['account' => $connection->account_name], $group).
     * Empty for a provider with no entry.
     *
     * @return list<string>
     */
    public static function accountLines(Connection $connection, Group $group, Terminology $terminology): array;

    // props(): every provider entry gains 'account' => ['lines' => self::accountLines(...)] when status is
    // connected or needs_reconnect, and 'account' => null when not_connected.
}
```

```php
// app/Providers/IntegrationServiceProvider.php — T-044's tag, one class added
$this->app->tag([GoogleAccounts::class, ZoomAccounts::class], 'account-connectors');

// config/services.php
'zoom' => [
    // The General app on Qori's own Zoom account (docs/planning/vendor-accounts.md, Zoom
    // section). The development pair until Marketplace approval; swap to the production
    // pair after it (step 12). Only Qori's own account can connect on the development pair.
    'client_id' => env('ZOOM_CLIENT_ID'),
    'client_secret' => env('ZOOM_CLIENT_SECRET'),
],

// config/qori.php — inside T-044's 'connections' key, beside 'google_drive'
'zoom' => [
    // Basic meetings end after this many minutes. Provisional: T-122 question 5 reads the current figure.
    'basic_meeting_minutes' => 40,
    // The longest Zoom says a cloud recording may take to become available ("occasionally up to 24 hours").
    'processing_hours' => 24,
],

// .env.example — beside GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
ZOOM_CLIENT_ID=
ZOOM_CLIENT_SECRET=
```

```php
// database/factories/ConnectionFactory.php
/** A connected account: provider Zoom, a refresh token, expires_at an hour on, settings tier zoom_pro with the four booleans. */
public function zoom(?bool $cloudRecording = true): static;
// settings: ['tier' => 'zoom_pro', 'cloud_recording' => $cloudRecording, 'auto_recording' => true,
//            'authenticated_view_cloud_recoding' => false, 'licensed' => $cloudRecording !== false]
```

```ts
// resources/js/components/share/ProviderSection.vue — one field added to T-044's `provider` prop
account: { lines: string[] } | null;
// Rendered as a <ul> under the status badge when `account` is set and `lines` is not empty; nothing otherwise.
// The strings arrive filled from lang; the component adds no words of its own.
```

## Copy

| Key                                                               | File                      | English                                                                                                                                                                                                                                                   |
| ----------------------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `connections.providers.zoom.name`                                 | `lang/en/connections.php` | Zoom                                                                                                                                                                                                                                                      |
| `connections.providers.zoom.description`                          | `lang/en/connections.php` | Connect the Zoom account you host live :episode_plural from. Qori reads its recording settings and shows here whether that account keeps cloud recordings.                                                                                                |
| `connections.providers.zoom.tiers.zoom_basic.label`               | `lang/en/connections.php` | Zoom Workplace Basic (free)                                                                                                                                                                                                                               |
| `connections.providers.zoom.tiers.zoom_basic.help`                | `lang/en/connections.php` | Zoom's free plan, with no paid licence.                                                                                                                                                                                                                   |
| `connections.providers.zoom.tiers.zoom_basic.recommended`         | `lang/en/connections.php` | We recommend Zoom Workplace Pro or higher: it's the lowest plan that keeps cloud recordings, which Qori needs to find a recording for you. On Basic, record to your computer and add the recording's link to the :episode yourself.                       |
| `connections.providers.zoom.tiers.zoom_pro.label`                 | `lang/en/connections.php` | Zoom Workplace Pro                                                                                                                                                                                                                                        |
| `connections.providers.zoom.tiers.zoom_pro.help`                  | `lang/en/connections.php` | One paid licence. Cloud recording is included.                                                                                                                                                                                                            |
| `connections.providers.zoom.tiers.zoom_pro.recommended`           | `lang/en/connections.php` | Turn on cloud recording and automatic cloud recording in your Zoom settings, and share each recording with everyone who has the link. Qori reads those settings when you connect and shows them here.                                                     |
| `connections.providers.zoom.tiers.zoom_business.label`            | `lang/en/connections.php` | Zoom Workplace Business                                                                                                                                                                                                                                   |
| `connections.providers.zoom.tiers.zoom_business.help`             | `lang/en/connections.php` | Paid licences for a team. Your Zoom admin may have locked the recording settings.                                                                                                                                                                         |
| `connections.providers.zoom.tiers.zoom_business.recommended`      | `lang/en/connections.php` | Before you connect, check with your Zoom admin that cloud recording is allowed on your account and that recordings can be shared with everyone who has the link.                                                                                          |
| `connections.providers.zoom.tiers.zoom_business_plus.label`       | `lang/en/connections.php` | Zoom Workplace Business Plus                                                                                                                                                                                                                              |
| `connections.providers.zoom.tiers.zoom_business_plus.help`        | `lang/en/connections.php` | Paid licences for a team. Your Zoom admin may have locked the recording settings.                                                                                                                                                                         |
| `connections.providers.zoom.tiers.zoom_business_plus.recommended` | `lang/en/connections.php` | Before you connect, check with your Zoom admin that cloud recording is allowed on your account and that recordings can be shared with everyone who has the link.                                                                                          |
| `connections.providers.zoom.tiers.zoom_enterprise.label`          | `lang/en/connections.php` | Zoom Workplace Enterprise                                                                                                                                                                                                                                 |
| `connections.providers.zoom.tiers.zoom_enterprise.help`           | `lang/en/connections.php` | Paid licences for a large organisation. Your Zoom admin may have locked the recording settings.                                                                                                                                                           |
| `connections.providers.zoom.tiers.zoom_enterprise.recommended`    | `lang/en/connections.php` | Before you connect, check with your Zoom admin that cloud recording is allowed on your account and that recordings can be shared with everyone who has the link.                                                                                          |
| `connections.providers.zoom.limits.zoom_basic.no_cloud_recording` | `lang/en/connections.php` | Zoom Workplace Basic doesn't keep cloud recordings, so Qori can't find a recording for you. Record to your computer from the Zoom desktop app, upload it somewhere :peer_plural can open with the link, and add its link to the :episode after the class. |
| `connections.providers.zoom.limits.zoom_basic.meeting_length`     | `lang/en/connections.php` | Basic meetings end after :minutes minutes, so a longer class becomes more than one meeting and more than one recording.                                                                                                                                   |
| `connections.providers.zoom.limits.common.sharing`                | `lang/en/connections.php` | Share each recording with "Everyone with the recording link". Under "Sign in to Zoom" or on-demand registration, :peer_plural without a Zoom account can't watch.                                                                                         |
| `connections.providers.zoom.limits.common.no_account`             | `lang/en/connections.php` | Nobody needs a Zoom account to join a session or to watch a recording shared with everyone who has the link.                                                                                                                                              |
| `connections.providers.zoom.limits.common.admin`                  | `lang/en/connections.php` | Accounts with more than one user may need a Zoom admin to approve Qori before you can connect.                                                                                                                                                            |
| `connections.providers.zoom.limits.<paid>.cloud_setting`          | `lang/en/connections.php` | Cloud recording must be on in your Zoom settings, and each class recorded to the cloud. A recording saved to your computer can't be found by Qori — add its link to the :episode yourself.                                                                |
| `connections.providers.zoom.limits.<paid>.auto_delete`            | `lang/en/connections.php` | If Zoom deletes a recording — an expiry date, auto-delete, or your cloud storage filling up — it's gone for :peer_plural too. Qori shows the date a recording is available until, and can't keep a copy.                                                  |
| `connections.providers.zoom.limits.<paid>.meeting_links`          | `lang/en/connections.php` | Qori can only look for the recording of a session whose join link carries a meeting ID from this account. For your personal meeting room, a vanity link or another host's meeting, add the recording's link yourself.                                     |
| `connections.providers.zoom.limits.<paid>.wait`                   | `lang/en/connections.php` | A cloud recording isn't there the moment a session ends: Zoom can take up to :hours hours to make it available.                                                                                                                                           |
| `connections.providers.zoom.account.cloud_recording_on`           | `lang/en/connections.php` | Cloud recording is on for :account, which is what Qori needs to look for recordings of your live :episode_plural.                                                                                                                                         |
| `connections.providers.zoom.account.cloud_recording_off`          | `lang/en/connections.php` | Cloud recording is off for :account, so Qori can't find recordings for you. Turn it on in Zoom (Pro or higher), then connect again so Qori reads the new setting — or add each recording's link to the :episode yourself.                                 |
| `connections.providers.zoom.account.cloud_recording_unknown`      | `lang/en/connections.php` | Qori couldn't read whether :account keeps cloud recordings. Connect again to try once more; until then, add each recording's link to the :episode yourself.                                                                                               |
| `connections.providers.zoom.account.auto_recording_off`           | `lang/en/connections.php` | Automatic cloud recording is off for :account. Turn it on in Zoom so no class goes unrecorded — or press Record to the cloud at the start of every class.                                                                                                 |
| `connections.providers.zoom.account.sign_in_required`             | `lang/en/connections.php` | :account only lets people watch cloud recordings after signing in to Zoom, so :peer_plural without a Zoom account can't open them. Turn off "Only authenticated users can view cloud recordings" in Zoom's recording settings.                            |
| `connections.providers.zoom.disconnect.in_qori`                   | `lang/en/connections.php` | Recordings already added to your :episode_plural keep working. New ones won't be found until you connect Zoom again; add them yourself in the meantime.                                                                                                   |
| `connections.providers.zoom.account_change.in_qori`               | `lang/en/connections.php` | Recordings already added keep working. From now on Qori looks for recordings in :incoming rather than :current, so a session hosted from :current after the switch needs its recording link added by hand.                                                |

Every tier has a `recommended` line and its `limits.*` lines, in `T-044`'s key
shape, and which of them sit above the disclosure is
`ProviderSections::ESSENTIAL` (Code), not a flag here. `<paid>` stands for
each of `zoom_pro`, `zoom_business`, `zoom_business_plus` and
`zoom_enterprise`: the four lines are one local array in
`lang/en/connections.php`, spread into each paid tier's `limits` entry, so
every key exists and the English is written once; `common` holds only lines
true on Basic too (Decisions). `name`, `description`, every tier's `label`,
`help` and `recommended`, `common.no_account`, `common.admin`,
`disconnect.in_qori` and `account_change.in_qori` also appear in `T-100`'s
draft with other English; this task owns them, and `T-100`'s draft is edited
to drop its rows and rewrite what it must when it lands (Notes). `:account`,
`:current`
and `:incoming` are filled as `T-044` fills them; `:minutes` is
`config('qori.connections.zoom.basic_meeting_minutes')` and `:hours` is
`config('qori.connections.zoom.processing_hours')`; the nouns are
`Terminology`'s. No line refuses a tier (`D-018`), and
`disconnect.in_qori` renders only when the Dialog's Series list is not
empty, as `T-044` renders it — `ConnectionService::impactOf()` counts a Series
with a live Episode on `EpisodeProvider::Zoom`, whose `connection()` is this
row's provider. No `errors.*` line is added: the exchange, state, scope and
owner refusals are `T-044`'s.

## Routes

None. Zoom rides `T-044`'s routes. The begin route and the account-change page
carry the slug `zoom` in `{provider}`: `POST g/{group}/connections/zoom/begin`
(`share.connections.begin`) and
`GET g/{group}/connections/zoom/account-change`
(`share.connections.account_change`). `PATCH` and
`DELETE g/{group}/connections/{connectionId}` (`share.connections.update`,
`share.connections.disconnect`) and the account change's switch and keep take
the row's id. The landing, `GET u/connections/zoom/finalise`
(`connections.oauth.finalise`), names the vendor rather than the service
(`D-033`), and is the redirect URI registered on the app.

## Tests

Every case fakes Zoom with `Http::fake()` and the fixture bodies under
`tests/Fixtures/zoom/`; the two `oauth/token.*` are captured by whichever
spike authorises the app first (`T-122`, by the stream's order) and
`recordings/user_*` are `T-122`'s. A case that needs a token body with a different `scope`, or a
settings body with a different value, edits the fixture's array in the test
rather than adding a fixture nobody observed.

**New: `tests/Feature/Integrations/Zoom/ZoomAccountsTest.php` — 10 cases**

1. `test_it_builds_the_authorize_url_with_no_scope_and_no_login_hint` — host `zoom.us`, path `/oauth/authorize`; `response_type=code`, `client_id`, `redirect_uri`, `state`, `code_challenge` and `code_challenge_method=S256` present; no `scope`; the hint argument ignored; with `null` for the challenge, neither PKCE field.
2. `test_it_reads_the_token_response` — `finaliseConnection()` with the expected `state` and a `code`, `oauth/token.authorization_code.200.json`: `Connected`, whose `ConnectionTokens` has `scopes` split on space, `refreshToken` set, `expiresAt` within a second of now + `expires_in`; `Http::assertSent()` sees Basic auth from `services.zoom` and a form body with `grant_type=authorization_code`, `code`, `redirect_uri`, `code_verifier`.
3. `test_a_refused_code_is_an_exchange_failure_and_is_not_retried` — a 400 body → `Failed` with `upstream` `400`, and no exception; `Http::assertSentCount(1)`; a `ConnectionException` → `Failed` with `connection`.
4. `test_a_refresh_returns_the_rotated_pair` — `oauth/token.refresh.200.json`: `RefreshResult::isRenewed()`, both tokens differ from the ones sent; `Http::assertSent()` sees a form body with `grant_type=refresh_token` and the token that was sent.
5. `test_a_reused_refresh_token_is_a_revoked_result_not_an_exception` — a 400 body `{"error": "invalid_grant"}` from Zoom's OAuth reference until `oauth/token.refresh_reused.<status>.json` exists, then that fixture (Preconditions): `revoked` true, `tokens` null, no exception, `Http::assertSentCount(1)`.
6. `test_a_timeout_is_an_unavailable_result` — `Http::fake` throwing `ConnectionException`: `tokens` null, `revoked` false, `upstream` null; the request's `timeout` option was the budget passed in, and a budget above `ZoomClient::TIMEOUT_SECONDS` was cut to it (`D-034`).
7. `test_it_reads_the_identity_and_the_recording_settings` — `recordings/user_me.pro.200.json` and `recordings/user_settings.pro.200.json`: `externalId` is `id`, `name` and `email` are `email`, `settings` has the four keys with `cloud_recording` true and `licensed` true; `auto_recording` is whether the fixture's `recording.auto_recording` is `cloud`, and `authenticated_view_cloud_recoding` equals the fixture's boolean.
8. `test_a_basic_account_reads_as_keeping_no_cloud_recordings` — `recordings/user_me.basic.<status>.json` with `recordings/user_settings.basic.<status>.json`: `cloud_recording` false whether the settings answered false or were refused; `licensed` false.
9. `test_an_unreadable_settings_call_leaves_the_settings_unknown_and_still_identifies` — `user_me.pro` with the settings call answering 500 twice: `ConnectedAccount` returned, `cloud_recording` null, `auto_recording` null, `authenticated_view_cloud_recoding` null, `licensed` true; `Http::assertSentCount(3)` (one identity read, `ZoomClient::READ_ATTEMPTS` settings tries).
10. `test_a_read_retries_a_server_error_and_never_a_client_error` — `/users/me` answering 500 then 200 and the settings call 200 → the `ConnectedAccount` returned after two requests to `/users/me` and one to `/users/me/settings`, `Http::assertSentCount(3)`; `/users/me` answering 401 → `AppException` with `ErrorCode::UpstreamUnavailable` and `upstream` `401` after one call, `Http::assertSentCount(1)`.

**New: `tests/Feature/Share/ZoomConnectTest.php` — 11 cases**

Each starts from `T-044`'s helpers: an owner, their Group, `actingAs`, the
Integrations page at `share.settings.integrations`.

11. `test_the_page_offers_five_zoom_tiers_each_with_a_recommendation_and_at_most_three_essential_lines` — `providers.zoom.tiers` holds `zoom_basic`, `zoom_pro`, `zoom_business`, `zoom_business_plus`, `zoom_enterprise` in that order; each `recommended` non-empty; each `essential` has at most `ProviderSections::MAX_ESSENTIAL` entries in `ESSENTIAL`'s order; `essential` followed by `more` equals every `limits.common.*` and `limits.<tier>.*` line for that tier; `zoom_basic`'s lines hold none of the `cloud_setting`, `auto_delete`, `meeting_links` or `wait` English, and each paid tier's `essential` plus `more` holds each of the four exactly once; `zoom_basic`'s `more` includes the `:minutes` figure nowhere and its `essential` includes it once; `account` is null.
12. `test_the_landing_stores_the_account_and_settings_and_the_page_says_cloud_recording_is_on` — `POST share.connections.begin` with `provider` `zoom` and `tier` `zoom_pro`, then the landing with the session's state and a code, the Pro fixtures faked: the row's raw `access_token` column is not the plaintext; `external_id` is the fixture's `id`, `account_name` its `email`, `expires_at` about an hour on, `settings` equals `['tier' => 'zoom_pro']` plus the four keys; toast `connections.connected`; 302 to Integrations; the page then shows `providers.zoom.status` `connected` and `providers.zoom.account.lines` exactly the `cloud_recording_on` line with the account name.
13. `test_a_basic_account_connects_and_is_told_it_keeps_no_cloud_recordings` — the Basic fixtures with `tier` `zoom_basic`: status `connected`, nothing refused, `lines` is exactly `[cloud_recording_off]` — no `auto_recording_off` or `sign_in_required` whatever the Basic settings body says, because both require `cloud_recording` — and `settings.tier` still `zoom_basic`.
14. `test_an_unreadable_settings_call_still_connects_and_says_so` — settings 500: status `connected`, `lines` is exactly `[cloud_recording_unknown]`.
15. `test_sign_in_required_and_no_auto_recording_each_add_their_line` — the Pro settings fixture edited to `auto_recording` `none` and `authenticated_view_cloud_recoding` true, `cloud_recording` still true: three lines, in `ACCOUNT_LINES` order.
16. `test_a_token_missing_a_required_scope_is_revoked_and_refused` — the token fixture with `user:read:settings` removed from `scope`: the revoke endpoint called with that access token; `errors.connections.scope_declined`; no row.
17. `test_connecting_again_re_reads_the_settings_and_keeps_other_keys` — `Connection::factory()->zoom(false)` with an extra `settings` key `meeting_id`, then the landing with the Pro fixtures for the same `id`: `cloud_recording` true, `meeting_id` still there, `ConnectionReconnected` dispatched with `sameAccount` true, toast `connections.reconnected`.
18. `test_connecting_again_with_an_unreadable_settings_call_replaces_a_known_setting_with_unknown` — `Connection::factory()->zoom()` (`cloud_recording` true), then the landing with `user_me.pro` for the same `id` and the settings call answering 500: `settings.cloud_recording`, `auto_recording` and `authenticated_view_cloud_recoding` all null, `licensed` true, `tier` kept, `ConnectionReconnected` dispatched with `sameAccount` true; the page's `lines` is exactly `[cloud_recording_unknown]`, not the earlier `on` line.
19. `test_switching_to_another_account_writes_that_accounts_settings` — `Connection::factory()->zoom(false)` with `external_id` A, then the landing with the Pro fixtures whose `id` is B: held and nothing written, as `T-044`'s case 11 asserts for Google; `POST share.connections.account_change.switch`: `external_id` B, `settings` holds `cloud_recording` true and the other three keys from the Pro fixtures beside the held `tier`, `ConnectionReconnected` dispatched with `sameAccount` false and A.
20. `test_the_disconnect_dialog_says_recordings_already_added_keep_working` — a connected row, a Series with a live `EpisodeProvider::Zoom` Episode and one active Access: `providers.zoom.disconnect.inQori` is `disconnect.in_qori` and `disconnect.series` has one row; `DELETE share.connections.disconnect` calls the revoke endpoint with Basic auth and the access token, sets `revoked_at`, keeps `external_id` and `settings`.
21. `test_the_zoom_lines_speak_the_groups_vocabulary` — a Group on a plan with `custom_vocabulary` and custom Episode and Peer nouns: the `cloud_recording_on` line, `limits.common.sharing` and `disconnect.in_qori` carry the Group's words and never "Episode" or "Peer".

**New, continued: `tests/Feature/Integrations/Zoom/ZoomAccountsTest.php` — 1 case**

22. `test_it_reads_the_landing_in_zooms_words` — `finaliseConnection()` given `error=access_denied` answers `Declined`; another `error` word `Failed` with that word as `upstream`; an error whose `state` is another nonce, and no error with a wrong `state`, `NotFromQori`; the expected `state` and no `code` `Failed`; none of these sends a request (`Http::assertNothingSent()`). Then the expected `state` and a `code`, with the token fixture's `scope` short of `user:read:settings`: `ScopeDeclined`, after one call to `/oauth/revoke` carrying that access token.

**Changed:**

- `tests/Feature/Share/ProviderSectionsTest.php` (`T-044`'s) — +1:
  `test_every_account_line_key_exists` — for every provider, key and entry in
  `ProviderSections::ACCOUNT_LINES`: every entry key other than `requires` is
  one of `on`, `off`, `unknown` and its line has
  `Lang::has("connections.providers.{$provider}.account.{$line}")`; a
  `requires` value names another key of the same provider's entry. Its
  `test_every_essential_key_exists_and_no_tier_lists_more_than_the_maximum`
  now walks the `zoom` entry with no change.
- `tests/Feature/Console/RefreshConnectionsCommandTest.php` (`T-044`'s) — +1:
  `test_it_renews_a_zoom_row_and_stores_the_rotated_refresh_token` —
  `Connection::factory()->zoom()->expiring()`, `oauth/token.refresh.200.json`;
  after the run `refresh_token` is the fixture's, `refreshed_at` set,
  `settings` untouched.
- `tests/Feature/Share/ConnectionsConnectTest.php` (`T-044`'s) — its case 4,
  `test_a_provider_with_no_connector_is_refused`, uses
  `ConnectionProvider::Zoom` today and must use a provider with no connector
  once Zoom is bound (`Dropbox` until `T-096`); no case added.

`tests/Feature/Share/IntegrationsProvidersTest.php` is **not** changed and is
not claimed: its case 16, `test_only_providers_with_a_bound_connector_have_a_section`,
asserts that `providers` holds `google_drive` and no `dropbox`, so a bound
`zoom` section leaves it green. If `T-044` tightens that case to an exact list
before this task is claimed, add `zoom` to it there.

Total: 24 cases, 22 in new files. No Peer-surface route and no notification
is added, so the wrong-tenant, revoked-Access and renamed-vocabulary rules
apply only through case 21.

## Acceptance

- [ ] The Integrations page shows a Zoom section with five tiers in the
      dropdown, cheapest first, each with what Qori recommends and at most
      three essential limitations above Connect and the rest in one
      disclosure, connected or not
- [ ] Connect sends the owner to Zoom's authorization page and back; the row
      holds the tokens encrypted, the account, the tier and the four settings,
      and the section reads "Connected as" the account's email
- [ ] After connecting, the section says whether that account keeps cloud
      recordings — on, off, or could not be read — and what to do in each
      case; a Basic account connects and is told, and nothing is refused
      (`D-018`)
- [ ] Disconnecting names the Series using Zoom, says recordings already added
      keep working and new ones won't be found (`D-021`; owner acceptance 9's
      disconnected-Zoom status), and revokes the token at Zoom best effort
- [ ] `php artisan qori:connections:refresh` renews a Zoom row and stores the
      rotated refresh token
- [ ] Every field read from Zoom is cited to a fixture under
      `tests/Fixtures/zoom/`, and no test reaches Zoom
- [ ] The walk against the development app on Qori's own Zoom account —
      connect, see the `on` line, disconnect, connect again — recorded in the
      report, with `APP_URL` on the numeric address and whether PKCE and the
      form-encoded revoke were accepted
- [ ] `docs/flows/storage.md`'s Connections section names Zoom, what the
      landing stores and what disconnect leaves; `docs/tinker/connections.md`
      drives a faked Zoom round trip
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- `T-044` `ready`, with its contract frozen and `ConnectedAccount::$settings`
  accepted into it — or another way for a connector to hand back what it
  learned about the account, in which case the Code section follows it — the
  storage owner's.
- `T-122`'s `recordings/user_settings.pro.200.json`,
  `recordings/user_settings.basic.<status>.json`,
  `recordings/user_me.pro.200.json` and `recordings/user_me.basic.<status>.json`:
  the field names under `recording.*`, whether a Basic account answers the
  settings call at all, and whether `/users/me` `type` tells Basic from
  Licensed as expected — the spike's (question 5).
- `oauth/token.authorization_code.200.json` and `oauth/token.refresh.200.json`
  committed: `T-122`'s Files table carries them only if it authorises the app
  before `T-099` runs, which the stream's order says it does; if `T-099` ran
  first they are its, at the same paths, and this task depends on `T-122`
  alone either way. `token.refresh_reused` is not waited for (Preconditions)
  — the spike's.
- The exact granular spellings of the four scopes `requiredScopes()` names,
  from the app's Scopes page — the spike's (question 8).
- Whether Request to Share (beta) admits an outside creator. If it does not,
  the description gains a line saying that until Marketplace review passes
  only Qori's own account can connect, and the beta gate's five representative
  creators (`PLAN.md`) wait for publication — the spike's (question 10).
- Basic's current meeting-length figure and wording, for
  `basic_meeting_minutes` and `limits.zoom_basic.meeting_length` — the
  spike's (question 5).
- Whether Zoom's authorization endpoint accepts `code_challenge` from this
  client, so `supportsPkce()` stays `true`; whether `/oauth/revoke` takes
  the token form-encoded or only in the query string; and what the landing
  carries when the owner declines, and when an admin has not approved Qori,
  which the `Declined` arm (`access_denied`) and the absent `AdminBlocked`
  arm rest on — this task's first round trip; anyone's.
- `errors.connections.scope_declined` now says Qori wasn't given access to
  "your files" and asks the creator to allow it (`T-044`), which is
  Google's case; whether `T-044` makes it provider-neutral or this task adds a
  Zoom-specific key — anyone's, with `T-044`.
- `ZoomClient::TIMEOUT_SECONDS` 15, Zoom's own limit on one request, which a
  caller's budget may only shorten (`D-034`): borrowed from what Qori's
  Dropbox and Vimeo clients set today
  (`app/Integrations/Dropbox/DropboxStorage.php:51`,
  `app/Integrations/Vimeo/VimeoVideos.php:43`) until this task's first round
  trip or `T-122` times the calls — anyone's.
- **From the privacy and terms drafts (`docs/pptcs/`, 19 September 2026):**
  Zoom's Marketplace review expects the app to act on `app_deauthorized` and
  delete the user's data, and this draft puts that webhook out of scope and
  keeps `external_id` and `settings` on disconnect (test 20). It is needed
  before Marketplace publication; bring it in, or name the task that does —
  the stream owner's.
- `F08` in the storage review of 20 September 2026
  (`docs/planning/reviews/storage-2026-09-20-findings-codex.md`) does the
  arithmetic on the retry this task specifies. `api()`'s
  `retry(2, 200, $when, throw: false)` makes every read two attempts at the same
  per-call timeout with a 200 ms delay between them, and one landing makes two
  reads — the identity and the recording settings — so the ordinary case is two
  calls and four attempts. At a five-second budget, two timed-out reads alone
  cost about 20.4 seconds before any token refresh is attempted, and the creator
  waits all of it on a page that is supposed to say whether they are connected.
  `D-034` bounds one call and not a person's whole request, so the review asks
  for a total request deadline with the remaining budget passed through refresh,
  lock acquisition and each retry, and for the elapsed time to be tested rather
  than only the timeout handed to each fake — the storage owner's, with `T-044`.
  **That file no longer exists and cannot be recovered**, so these bullets are
  the review itself, to be read as the primary source and not as a summary of
  something a reader can go and check; `docs/planning/reviews/README.md` has the
  whole of it.
- No Zoom response fixture exists anywhere in the repository yet; the review of
  20 September 2026 checked and says so plainly. `tests/Fixtures/` holds
  `google/`, `planning/` and `reachability/` and nothing from Zoom, so every
  field this task names — `recording.cloud_recording`,
  `recording.auto_recording`, `recording.authenticated_view_cloud_recoding`,
  `/users/me`'s `type`, and the token response's `expires_in` and rotated
  `refresh_token` — is a hypothesis taken from Zoom's reference. The fixture
  bullets above are the same wait seen from the other end; this is why none of
  them may be settled as a wording question — the spike's.

## Re-scope log

None.

## Notes

Written 18 September 2026 from `D-027`, `D-031`, `D-021` and `D-018`. The
merged sprint reference is `docs/planning/course-classroom.md`; its "When
there's no cloud recording" section is where the three essential limits, the
Basic sentence and the three Zoom fields come from.

`T-100`'s draft is edited to: take its five `ProviderTier` cases,
`ZoomAccounts`, the `zoom` block in `config/services.php` and the two env
keys from this task rather than creating them; drop
`app/Integrations/Concerns/ZoomHttpClient.php` for `ZoomClient`, which
`D-027` already records; keep its `connections.zoom` numbers (room sizes,
occurrence cap) as an addition to the block this task opens; put its tests
under `tests/Feature/Integrations/Zoom/` beside this task's and `T-142`'s
rather than `tests/Feature/Storage/Zoom*Test.php`; and, in its Copy table,
drop every row this task declares. On 19 September 2026 `T-100` took
`ZoomClient` and moved its tests, and depends on this task since; the rest is
a bullet under its Before this can be ready. Its Copy today declares the same
keys with other English, and one key is declared by one task, so the split
is:

- This task owns `connections.providers.zoom.name`, `.description`, every
  `tiers.<tier>.label`, `.help` and `.recommended` for the five tiers,
  `limits.common.no_account`, `limits.common.admin`, `disconnect.in_qori` and
  `account_change.in_qori`.
- `T-100` keeps only its registration keys: `limits.common.breaks`,
  `.emails`, `.idle`, `.occurrence_cap`, `.one_meeting`, `.waiting_room` and
  `.recordings`, and `limits.zoom_basic.registration`.
- Where `T-100` needs different English under a key this task owns — its
  `description` ("Everyone with access is registered for you"), its
  `tiers.zoom_pro.help` with `:people` and `:gigabytes`, its
  `disconnect.in_qori` and `account_change.in_qori` about registrations —
  `T-100` _rewrites_ `description`, `disconnect.in_qori`,
  `account_change.in_qori` and whichever tier `help` or `recommended` lines it
  must when it lands, as a stated edit of a done task's copy, and replaces
  `ESSENTIAL['zoom']` with its own once its container exists.

`T-044`'s draft is edited to give `ConnectedAccount` a `settings` array
written by `finaliseConnection()` and `switchAccount()` beside `tier`, merged over the
row's existing `settings` with nulls written as answered; to carry that array
in the `ACCOUNT_CHANGE_SESSION` payload (its "the `ConnectedAccount` fields"
gains `settings`) and rebuild it in `heldAccountChange()`, so
`switchAccount()` has it; and its `ConnectionsConnectTest` case 4 to use a
provider other than Zoom for "no connector".

`T-122`'s Files table already carries `oauth/token.authorization_code.200.json`
and `oauth/token.refresh.200.json` as a conditional row — only if it
authorises the app before `T-099` runs — and nothing there is edited: the
storage stream runs `T-122` on day 1, so this task depends on `T-122` alone
for them and needs no third dependency; if `T-099` runs first the same paths
are its. `oauth/token.refresh_reused.<status>.json` stays `T-099`'s, and case
5 fakes the body until it exists.

`T-142` and `T-143` call `ConnectionService::fresh()` before the finder runs:
a Zoom access token lasts an hour, and `qori:connections:refresh` runs daily
to keep the 90-day refresh token alive, not to keep the access token fresh.
`T-142`'s `ZoomRecordings` takes `ZoomClient` by constructor and calls
`api()` and `unwrap()` as this task declares them. `T-144`'s Check now is the
natural place to re-read the recording settings, so a creator who upgraded
need not reconnect; its draft is told.

The brief's "authorize URL with offline access" is satisfied by Zoom's
refresh token, which every exchange returns; Zoom has no offline scope and no
`access_type` parameter.

The `connections.zoom` numbers sit in `T-044`'s `connections` key of
`config/qori.php`, not in `T-123`'s `live` block: they describe a vendor's
plan, not a session.

The description, the Basic recommendation and the `on` line say only what
this task makes true — the settings are read and shown, and cloud recording
is what Qori needs — because between this task and `T-143` the connection
stores tokens and settings and nothing reads them but the page and the
refresh sweep. `T-143`'s draft is edited to rewrite
`connections.providers.zoom.description` and `account.cloud_recording_on`
when detection lands, saying recordings are found, as a stated edit of a done
task's copy; `T-100` does the same for registration (above).

`T-122` also reads `recording.auto_delete_cmr_days`; `T-142` may use it for a
recording's `availableUntil` when the recording payload carries no date. It
is not stored here.

`docs/flows/README.md:42-43` stays true: connecting is `storage.md`'s
Connections section, and the live chain is `T-125`'s `live-sessions.md`.

`docs/planning/streams/storage.md` lists fifteen tasks and not `T-122`,
`T-141` or `T-142`, though `streams/classroom.md` and `D-031` place all three
in `storage`; adding the rows, after `T-044` and before `T-099`, is the stream
owner's.
