---
id: T-094
title: 'Google Drive Episodes: each file shared with each Peer'
stream: storage
status: draft
owner: unassigned
estimate: L
depends: T-044, T-091, T-092, T-093, T-102, T-103, T-152
blocks: T-090, T-096, T-098, T-100
---

# T-094 — Google Drive Episodes: each file shared with each Peer

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.
>
> **Re-drafted on 20 September 2026 on `D-036`**, after `T-093`'s report
> ([`reports/T-093-2026-09-20-wayne.md`](reports/T-093-2026-09-20-wayne.md)):
> the grant is on the Episode's file, and a Series has no Google Drive folder.
> Everything the folder carried — the panel, the container states, the
> capacity guard on a folder, the rule that an Episode's file must sit inside
> it — is gone with it, and what is left is one picked file per Episode and
> one reader permission per Peer per file. The file name still says "from a
> Series folder": it is kept so `T-093`'s report and task keep their links.
>
> Written on 16 September 2026 from `D-016`, the owner's BYO blueprint and the
> developer review of the same day; amended on 17 September from `D-018`,
> `D-020` and `D-021`, on 18 September by the classroom decisions (`D-024`,
> `D-025`, `D-030`), and on 19 September from that day's cross-draft decisions
> (`GrantIdentity`, `GrantResult::ERROR_PERMISSION_GONE`, `ItemCheck`'s
> `name`, `mimeType` and `url`, `VendorAccessService::handles()`, `D-034`'s
> budgets, `tests/Feature/Integrations/Google/`, and `T-102` and `T-103`
> before the paid walk). Those amendments still hold except where the
> re-draft names them.

## Why

Nothing in the code can hold a Google Drive Episode. `EpisodeProvider` has
five cases and none is Google (`app/Enums/EpisodeProvider.php:17-25`),
`EpisodeType::allowedProviders()` offers Dropbox for every file, video and
audio Episode (`app/Enums/EpisodeType.php:29-37`), `ConnectionProvider` has no
Google case (`app/Enums/ConnectionProvider.php:14-20`), and two live documents
still say Drive is excluded because its links cannot be withdrawn
(`app/Integrations/Dropbox/DropboxStorage.php:17-19`,
`docs/flows/storage.md:56`) — the reasoning `D-016` superseded. The creator
setup page promises "Connecting Dropbox or Google Drive is coming"
(`lang/en/groups.php:68`, which `T-044` replaces), and `D-004` says Drive is
the storage this audience already pays for.

Afterwards, this is the first complete journey the developer review asked for.
A creator connected under `T-044` picks a file from their own Drive for each
Episode; every Peer with access holds a reader permission on each of those
files through `T-091`'s ensure step; Open (`T-089`) sends the Peer to the file
on Google's own site, signed in as the account they confirmed under `T-092`;
and a file the creator edits or uploads a new version of reaches them with no
further call. A file they add to a folder in Drive does not, and does not have
to: an Episode is a file the creator chose, and choosing it is what shares it
(`D-036`).

Both tiers `T-044` offers — Free Google Drive, and Google Workspace & G
Suite — reach a Peer the same way; `T-044` states each tier's limitations
before the connection is made, and this task is what makes those lines true.
Neither tier is ever turned away (`D-018`): a Workspace tenant whose
administrator has turned outside sharing off, and a Google account on the
legacy free edition, both connect, pick files and grant like any other — what
Google refuses arrives as a grant the creator has to resolve, naming what
their administrator has to allow, and what Google's terms ask of the creator
is said on screen and left to them.

## Decisions taken to make this specifiable

**The grant is on the Episode's file, one reader permission per Peer per
file** (`D-036`). `T-093` found that under `drive.file` a folder refuses every
sharing change — a new Peer, a repeat grant and a removal alike, with 403
`appNotAuthorizedToChild` — while any item beneath it has not been picked in
Qori, and that a file the creator drops in through Drive, a file in the trash,
a shortcut or a file inside a subfolder under Limit access is enough to stop
all three. The owner chose per-file grants on 20 September 2026. What the
folder gave up: a file the creator adds in Drive no longer reaches Peers by
itself, and a new Episode costs one grant per Peer. What it buys: nothing the
creator does in their own Drive can block a sale or a removal, a file moved
anywhere in that Drive keeps working because the permission is on the file,
and the cap is Google's documented 600 addresses for one file
(https://support.google.com/drive/answer/2494822) rather than an unmeasured
figure for a folder.

**A Series has no Google Drive container.** No folder is picked, stored,
replaced, removed or checked; `series_containers` holds no `google_drive`
row, and `series.container.*`, the folder panel, `ContainerChangeDialog`,
`containerImpact` and the container capacity guard are not part of this task.
An Episode's file may live anywhere in the creator's Drive, and Qori refuses
it only for what Google refuses: a file it cannot read, and a shortcut, whose
ACL is its parent's and which grants a Peer nothing
(https://developers.google.com/workspace/drive/api/guides/shortcuts,
confirmed by `T-093`, whose shortcut blocked its folder's sharing and could
not be authorised by picking).

**What `T-091` has to carry: a grant row per (Access, item).** `T-091`'s
draft has one row per (Access, container) and a contract whose `grant()`,
`checkGrant()` and `revoke()` take a `SeriesContainer`; its own Decisions say
that a provider needing per-item grants is "a change to this task's Database
section", and `T-093` is the spike that said so. This task is written against
that change: a grant row carries the Episode it belongs to and the file id it
was made on, `(access_id, provider, episode_id)` is unique, the ensure step
runs over the Series' granting items rather than one container, and a
provider says which model it grants on. The exact columns and contract are
`T-091`'s to write, and are the first open question below; nothing here works
until they exist.

**There is no fan-out, because nothing is granted before somebody opens it**
(`D-040`). A Series of ten Episodes and one new Peer used to be ten
`permissions.create` calls at 1.68 to 2.44 seconds each (`T-093`), and two
hundred Peers with one new Episode was two hundred. Now a purchase makes
none, adding an Episode makes none, and the only call is the one a Peer's
Open needs: one `permissions.create` on one file, in that Peer's own
request, for the Episode they pressed. A Peer who opens three Episodes of
twenty costs three calls, and the other seventeen are never made. There is
no bound to set because there is nothing to bound — `INLINE_GRANT_LIMIT` is
gone from `T-091` with the sweep — and the wait a Peer feels is one create
before the redirect, which the Open control has to show as a wait rather
than appear to do nothing.

**`granted` means the 200 from `permissions.create` arrived, and `vendor_ref`
is the permission `id` Google returned for that file.** The owner decided on
20 September 2026 not to measure how long Google takes to make a new reader
effective ("people can wait for few mins"), so there is no propagation
window, no `PROPAGATION_SECONDS` and no state between the 200 and `granted`.
`T-093` saw the same permission id for a grantee across every grant and
re-grant on one file; whether Google uses that same id on a different file is
not observed, so each row stores the id that file's call returned and
`checkGrant()` reads it back with the file it was made on.

**`grant()` reads the file's permissions before it writes.** Google says
concurrent permission changes on one item are unsupported and "only the last
update is applied"
(https://developers.google.com/workspace/drive/api/reference/rest/v3/permissions/create).
`T-093` saw no lost grant in three bursts of five, and saw Google apply them
about half a second apart, so the risk is small and the documentation still
stands. `permissions.list` on the file, matched on `emailAddress`, makes the
call idempotent and adopts a permission the creator had already given that
person; a read does not count against the sharing limit, and it halves the
creates under a retry storm. `T-093` also found that a create never lowers a
role the creator raised by hand and returns the role actually held, so this
task stores the id and never the role. Grants on one item still run one at a
time under `T-091`'s lock, taken per item rather than per container.

**Every refusal maps to one of `T-091`'s shared states, by Google's
`reason`.** `sharingRateLimitExceeded`, `rateLimitExceeded`,
`userRateLimitExceeded`, a timeout, a connection error and any 5xx are
`pending`, with `retryAfterSeconds` from `Retry-After` when Google sends one.
`invalidSharingRequest` — both Google's "ACL change not allowed" for an
external-sharing policy and the "you do not have permission to share" `T-093`
met on a file the creator may edit but not share — and `domainPolicy` are
`needs_creator`, and each names what the creator's administrator has to
allow. A 404 on the file is `needs_creator` with `ERROR_ITEM_MISSING`: the
creator picks the file again, which is also what a reconnect with a different
Google account leaves behind (`T-093`: another account's token gets 404 on a
file it never picked). A 401 is `needs_creator` with `T-091`'s
`ERROR_CONNECTION_UNUSABLE`; marking the connection for reconnect is
`ConnectionService::markForReconnect()` (`T-044`). `cannotInviteNonGoogleUser`
is `awaiting_identity` — `T-093` Q7 observed it, and it can only happen for an
account deleted after `T-092` confirmed it, since the address Qori grants on
is one the Peer signed in with. `appNotAuthorizedToChild` cannot arise on a
file, only on a parent operation this task never makes; if it ever comes back
it is `needs_creator` with the reason as Google sent it. Google Drive never
produces `awaiting_acceptance`: a reader needs no step of their own, so
`T-091`'s Check again (`shared.access.check`, `D-021`) shows for a Google
Drive grant only on a `pending` row that is due, and a Peer whose Open cannot
go to Google yet lands back on the Series page at `T-091`'s notice (`T-089`'s
redirect, `D-020`).

**Google Workspace is offered whatever the administrator has done**
(`D-018`). Qori tests no tenant before the connection and refuses no tier: an
administrator who has turned outside sharing off (`invalidSharingRequest`) or
turned third-party apps off for Drive (`domainPolicy`) surfaces on the first
grant as `needs_creator` — the mapping above — so the creator knows what to go
and ask for. Once the administrator has allowed it, the creator presses
`T-091`'s Try again now on the Integrations page
(`share.settings.integrations.retry`, `D-021`), which re-attempts those rows
through this class's `grant()` in the same request, until `T-091`'s
`REQUEST_DEADLINE_SECONDS` is spent, and leaves the rest due for the Peers'
own next Open; its flash promises nothing, since `T-044`'s `limits.google_workspace.propagation` line
says an administrator's change can take hours to reach Google's sharing.
`admin_policy_enforced` at consent is Google declining the connection, not
Qori declining the tier.

**The legacy free Google edition warns, and nothing here refuses it**
(`D-018`). `T-044`'s `legacy_free` line says the edition is for personal,
non-commercial use and that a priced Series may breach Google's terms, and the
creator decides. No guard, validation or refusal in this task reads the
edition, and a priced Series on such an account picks files, grants and opens
like any other.

**Open is a 302 to the file's `webViewLink`, with the Peer's address in
`authuser`.** `webViewLink` opens the file in the relevant Google viewer or
editor
(https://developers.google.com/workspace/drive/api/reference/rest/v3/files),
so documents open in Google's viewer and an MP4 plays in Drive's own player at
up to 1080p (https://support.google.com/drive/answer/2423694). `T-093`
confirmed that appending `authuser=<the Peer's Google address>` opens the file
as that account in a browser signed in to several, which is the common way a
Peer meets "You need access", so the link carries it. The link is read from
`files.get` when the Episode is created and stored in `episodes.content`, so
Open makes no `files.get`. There is no folder to fall back to: when the item
check has flagged the file, Open sends the Peer back to the Series page at
`T-091`'s notice, as it does for a grant that is not `granted` (`T-089`,
`D-020`). `accountHint` on the `VendorLink` is the confirmed identity's email,
read from `T-092`'s `App\Models\VendorIdentity::verifiedFor()`, and the
sentence that names it on the Series page is `T-092`'s `identities.open_with`.

**File, video and audio Episodes may all live on Google Drive.** Drive's
player is the vendor's own site, which is what `D-016` asks for, and the
1080p ceiling and the processing delay are in `T-044`'s tier copy. `T-093`
opened `episode.mp3` in Drive's web preview as a reader and it played, so
`EpisodeType::Audio` offers Google Drive too.

**The Episode stores the file id, name, MIME type and `webViewLink`, read
back from `files.get` when it is created.** The read goes through `T-091`'s
`checkItem()` on an unsaved `Episode`, so `EpisodeService` calls a contract
and never `Http::`; `T-091`'s `ItemCheck` carries nullable `name`, `mimeType`
and `url` for that, which this task's `checkItem()` fills and `describeItem()`
reads. `ItemCheck::$insideContainer` is not read for Google Drive and is null:
there is no container to be inside. A shortcut is refused by its MIME type,
and a file `files.get` cannot find is refused as not found.

**Currency is Google's own editing plus a daily item check.** Edits to Docs,
Sheets and Slides and Manage versions › Upload new version keep the file's id,
so the Peer sees the new content with no call from Qori — `T-093` watched both
with a Peer's account. "Keep both files", the website's same-name upload when
the creator chooses to keep both, deleting and re-uploading, and copying make
a new file with a new id, which the Peer cannot see at all under per-file
grants, so the Episode is stale until the creator picks the new file. A
scheduled `qori:episodes:check` re-reads `files.get` on every stored id, flags
to the creator any file that is trashed or gone, and leaves everything else
alone. `T-093` confirmed there is nothing cheaper: under `drive.file` the
token sees only what was picked, a folder listing comes back empty and the
change feed carries only authorised items, so `files.get` of stored ids is all
there is. A read that fails for a reason other than the file's absence — a
timeout, a 429 or a 5xx, carried in the result's `errorCode` — writes nothing.
`version` is no use as a signal: `T-093` watched it rise from 4 to 42 with no
change to the file's content, because permission changes raise it too.
`md5Checksum` is the uploaded bytes' MD5 and changes only when the content
does, and nothing in this task needs either.

**The daily run is never the only way a flag clears** (`D-021`). A creator who
has put a file back presses Check now beside the flag
(`share.series.episodes.check`), and `T-091`'s
`VendorAccessService::checkEpisode()` — the one-Episode check `checkItems()`
loops over — re-reads that one file with `REQUEST_TIMEOUT_SECONDS`, in the
same request, so the page the creator lands on shows the outcome.
`checkEpisode()` answers `T-091`'s `App\Enums\EpisodeCheckOutcome`, and the
flash is picked from it: `Clear` is `series.episode_check.clear`; `Flagged`
(the file is gone or trashed, and the Episode now carries `missing_since`) is
`series.episode_check.still`; `NeedsCreator` (the connection is unusable, so
nothing was asked) is `series.episode_check.needs_creator`; `Unreadable`
(Google did not answer in time, or errored; nothing is written and any earlier
flag stays) is `series.episode_check.unreadable`. It is throttled per Episode
by `EpisodeCheckController::MANUAL_CHECK_SECONDS` (provisional 60), and a
press inside the window says when the next one is allowed instead of failing.

**This task builds the one command and the one Check now controller**
(`D-021`). The stream's order makes this the first complete journey and adds
providers one at a time after it, so this task creates
`App\Console\Commands\CheckEpisodeItemsCommand` (`qori:episodes:check`) and
its single schedule line, `App\Http\Controllers\Share\EpisodeCheckController`
with its route `share.series.episodes.check`, its `MANUAL_CHECK_SECONDS`
throttle and every `series.episode_check.*` line, the `missingSince` prop on
the creator's Series page, and the two test files
`CheckEpisodeItemsCommandTest.php` and `EpisodeCheckTest.php`. The command's
pass here is `VendorAccessService::checkItems()`, and the controller's arm
takes every Episode whose provider `T-091`'s `VendorAccessService::handles()`
accepts and calls its `checkEpisode()`. `T-090` depends on this task and
extends what it finds, leaving the command's name, the schedule, the route,
the throttle and the copy as they are. `T-096` and `T-098` implement
`checkItem()` for their own providers and add nothing to either.

**The cap is Google's own number for one file, checked before a sale and
again at Open, and it counts the file rather than the Series** (`F09`, the
review of 20 September 2026). Google documents 600 individual addresses for
a single file (https://support.google.com/drive/answer/2494822), so
`qori.storage.google_drive.max_peers_per_file` is 600. The draft counted the
Series' active Accesses, which is the wrong number three ways: a file the
creator has already shared with readers by hand, a file used by a second
Series, and two checkouts that both pass at 599 before either writes an
Access. So `AccessService::guardItemCapacity()` counts **the grants Qori
holds on that physical file across the Group**, plus the outstanding
checkouts it has admitted, and refuses from `guardGrantlable()` on the
unpaid paths (`app/Services/AccessService.php:308`) and from
`CheckoutService::begin()` beside the Peer cap
(`app/Services/CheckoutService.php:48-50`); `fulfil()` never refuses
(`PLAN.md`, rule 2). Readers the creator added by hand are outside Qori's
count and cannot be made part of it without a `permissions.list` per
checkout, so the gap is real and stated: at the cap, Google's refusal
reaches the Peer at Open as `needs_creator`, and the creator's Integrations
page names the file. **Adding or replacing an Episode's file is an admission
point too** — a file at its cap cannot serve a Series that has more Peers
than it has room for — and the creator is told at the pick rather than at
the first Open. The number stays in config because Google may change it and
because a Series near it needs a decision, not a release.

**Picking is the owner's, with the owner's token, in the browser.** Only the
owner connects (`D-012`), and the Google Picker needs the account's own OAuth
token, the API key and the Cloud project number as `setAppId` — without
`setAppId` the pick grants the `drive.file` token nothing
(https://developers.google.com/workspace/drive/picker/reference/picker.pickerbuilder.setappid).
A small JSON route hands the current access token to the owner's own browser
for the pick and to nobody else, refreshing it first through `T-044`'s
`ConnectionService::fresh()`. The view is a plain `DocsView()` over the
creator's whole Drive, single select, with no parent and no folder selection:
there is no folder to start in, and `T-093` found that the picker authorises
what the person selects at the moment they press Select, whether or not the
page ever receives the callback — so a pick Qori loses is a file Qori may
read. The picker screen says what a picker needs from the browser, because
`T-093` met Safari refusing it with "The API developer key is invalid" and
published reports tie that, an empty list and a sign-in wall to a browser
blocking the `docs.google.com` frame's cookies.

**Google's limit is Google's own, and `$timeoutSeconds` is a budget that may
only shorten it** (`D-034`). `GoogleDrive` sets Google's limit on its `Http::`
chain, `GoogleAccounts::TIMEOUT_SECONDS` (20, `T-044`'s), as `T-092`'s
`GoogleSignIn` does, and no retry: a 429 or a 5xx is `pending` and `T-091`'s
retry rule takes it. Every method that reaches Google takes `int
$timeoutSeconds` last as the caller's budget, never a config key, and waits
whichever of the two is shorter. `T-093` timed every call: a create is 1.7 to
2.4 seconds on its own and up to 3.8 as the fifth of five at once on one file,
a delete 1.1 to 1.7, and every read under 0.9, against `T-091`'s
`REQUEST_TIMEOUT_SECONDS` of 5 — which is why the fan-out is bounded rather
than the budget raised.

**Reconciliation is `T-091`'s; this task adds the Series-page view of it.** A
Peer confirming or changing their Google account is `T-092`'s
`identityConfirmed()`. The creator reconnecting the same account makes `T-044`
dispatch `ConnectionReconnected`, and `T-091`'s listener
`ResumeGrantsAfterReconnect` calls `reconnected(sameAccount: true)`, which
re-runs every `needs_creator` grant; `T-093` confirmed the same account's new
token reaches every file picked before the reconnect, with no new pick. A
reconnect that returns a different Google account is held by `T-044` for the
creator to confirm (`D-021`), and Switch dispatches the event with
`sameAccount` false; every Drive Episode's file then belongs to an account the
new token cannot read, so `T-091` sets those rows `needs_creator` with
`ERROR_ITEM_REPICK`, the Integrations page names them, and the item check
flags each Episode on the Series page, where the creator picks each file
again. There is no container state to mark.

**Picking a different file for an Episode, or deleting the Episode, takes
the readers Qori added off the old file.** The Episode's grants are revoked
through `T-091`'s `revokeItem()`, one inline try each before the Episode is
deleted; what fails becomes `revoke_failed` on the creator's Integrations
page rather than being retried by anything (`D-040`), and the row survives
the Episode it pointed at, which is what makes the retry possible (`F01`).
The creator's file is otherwise left alone: Qori removes only the
permissions it created or adopted, and never the file (`D-038`). `series.episode.google_drive.replaced` says so where
the file is changed, as `T-091`'s container copy said it for a folder.

**The provider value is `google_drive`, on both enums.** `T-090` brings
YouTube, which is also a Google account; naming the storage product keeps the
two apart in `episodes.provider` and lets `EpisodeProvider::connection()` stay
a written-out map (`app/Enums/EpisodeProvider.php:42-51`).
`ConnectionProvider::GoogleDrive` is `T-044`'s case; this task adds the
`EpisodeProvider` case and the arm.

**This task's copy is the Episode's file on the creator's Series page, its
refusals, Google's own grant reasons, and what a buyer needs from Google.**
The tier limitation lines are `T-044`'s
(`connections.providers.google_drive.limits.*`) and this task adds only the
cap line beside them, in the tier's `more` disclosure since it stops nobody.
The two lines a buyer reads before paying
(`accesses.vendor.google_drive.before_buying.common.*`, `D-021`) are this
task's to write and `T-092`'s `BuyerRequirements` to render: a Google account,
and the work-or-school receiving policy that stops such an account opening
anything. `connections.grants.reasons.*` gains the Google codes the Workspace
pass observes, each naming what the creator's administrator has to allow.
Picker and Episode copy on the creator's Series page go in
`lang/en/series.php`, refusals in `lang/en/errors.php`. Vendor names appear
under `D-016`'s exception, on the surface where the creator is choosing which
vendor's file to use. Every line is authored whole and filled through
`Terminology::line()` (`app/Support/Terminology.php:89`).

## Preconditions

`T-044` done, so `ConnectionProvider::GoogleDrive`, `ProviderTier`, the Google
OAuth connect step (`drive.file` + offline), `ConnectionService::fresh()`,
`lang/en/connections.php` with the tier copy,
`errors.series.provider_not_connected`, `qori:connections:refresh`,
`AdvisoryLock` and `ConnectionReconnected` exist, and a different-account
reconnect is held for confirmation; `T-091` done **and carrying grants on an
item** (the first open question below), so the tables, the contract with
`App\Data\GrantIdentity`, `ItemCheck`, `GrantResult::ERROR_PERMISSION_GONE`
and `ERROR_ITEM_MISSING`, `VendorAccessService` with `handles()`, its lock,
`ResumeGrantsAfterReconnect`, `qori:access:reconcile`, Check again and Try
again now exist; `T-092` done, so `identityFor()` answers with the Peer's
confirmed Google address, `VendorIdentity::verifiedFor()` exists and
`BuyerRequirements::for()` renders the before-buying list; `T-093` done, so
`tests/Fixtures/google/` holds every response named below; `T-102` and `T-103`
done, so a delayed payment still becomes access and a refund revokes the grant
before the walk below buys a paid Series.

**Data this task verifies against:** a clean database for the tests. For the
browser walk, a Free Google Drive creator connected on the Integrations page,
one published paid Series and one free Series, each with a PDF, a Google Doc,
an MP3 and a 1080p MP4 that has finished processing, anywhere in that
creator's Drive.

**Equipment:** the owner's Google Cloud project
(`docs/planning/vendor-accounts.md`, Google Drive, steps 1 to 14), In
production once `useqori.com` serves its home page, privacy policy and terms,
and until then in Testing with every Google account the walk uses listed as a
test user — with `T-044`'s `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` and
this task's `GOOGLE_API_KEY` and `GOOGLE_PROJECT_NUMBER` set; Stripe test
mode; two Google identities in separate browser profiles (a Peer on Gmail, a
Peer on a non-Gmail Google account) plus a third Google account signed in
beside one of them, which is the case `authuser` exists for; a phone; a
visible browser at 400px and desktop widths.

**Spike:** `T-093`, whose fixtures are in `tests/Fixtures/google/` with an
index in its README. Every request shape below is from the Drive API reference
page cited beside it, and every response field named below appears in the
fixture named beside it. Two of the fixture names below are the spike's
folder calls (`permissions-create-folder.json`, `permissions-list-folder.json`,
`permissions-get.json`, `permissions-delete.txt`): a permission on a folder
and on a file are the same resource on the same endpoint, so the bodies serve
as they are, and the request's `fileId` is the only difference. Three
responses this task needs were not taken on a file and are the second open
question below.

## Scope

**In:**

- `EpisodeProvider::GoogleDrive`, its `connection()` arm, its
  `isAccountBound()` arm, true, and `EpisodeType::allowedProviders()` offering
  it for file, video and audio.
- `App\Integrations\Google\GoogleDrive` implementing `T-091`'s
  `GrantsPeerAccess` on items: grant, check the grant, revoke, open link,
  check the item; tagged `grant-providers`.
- The creator's Series page: pick a Drive file for an Episode, see the flag
  the item check raises with Check now beside it, and pick the file again.
- The picker token route, and the Picker itself in file mode over the
  creator's Drive.
- The Episode content shape and the `files.get` confirmation on create,
  through `describeItem()`.
- `qori:episodes:check` (`CheckEpisodeItemsCommand`), created here with its
  one schedule line, and `checkItems()` behind it as its first pass.
- `EpisodeCheckController` (`share.series.episodes.check`), created here with
  its route, `MANUAL_CHECK_SECONDS` and every `series.episode_check.*` line.
- The `missingSince` prop on each Episode of the creator's Series page, which
  `T-096`, `T-098` and `T-100` read as it is.
- Google Drive's two before-buying lines, which `T-092` renders.
- The cap line, the cap guard and its refusal, on Google's 600 per file.
- The Google grant reasons on the Integrations page, each naming what the
  creator's administrator has to allow.
- The docs rows below, including the first rewrite of `docs/project-plan.md`
  §8's Drive line, which `D-016` defers to the first provider.

**Out:**

- Any Series folder: the container row, its picker, its panel, its states,
  `series.container.*`, `ContainerChangeDialog`, `containerImpact` and the
  capacity guard on a folder (`D-036`). `T-091` keeps all of it for whichever
  provider still grants on a container.
- The OAuth connect, disconnect, reconnect and the held different-account
  confirmation, refresh, the tier dropdown and every tier limitation line
  (`T-044`); the tables, the ensure step, the timeouts, the retry rule, the
  re-check of granted rows, the reconcile command, the lock, the Integrations
  page's lists with Try again now, and the Peer's notice with Check again
  (`T-091`); the Peer's Google sign-in and `BuyerRequirements` (`T-092`); the
  Open route and its redirect back to the Series page (`T-089`, `D-020`).
- The video pass of `qori:episodes:check` and the Vimeo and YouTube arm of
  Check now (`T-090`).
- `EpisodeCheckOutcome` and what `checkEpisode()` answers (`T-091`).
- Delayed payments and refunds (`T-102`, `T-103`); `T-103`'s revoke reaches
  `revoke()` here through `T-091`'s `revokeFor()`.
- Shared-drive files beyond what `supportsAllDrives=true` gives for free;
  `setEnableDrives` is not offered in this task.
- Visitor sharing, `expirationTime`, `downloadRestrictions`, view history.
- Any read of a folder's children, a `changes` feed, or sharing anything the
  creator did not pick.
- Detecting the G Suite legacy free edition, and any check, tier or refusal
  built on it (`D-018`).
- Refusing, gating or testing a Workspace tenant before its first grant.

## Files

| Path                                                                                                      | Change | Notes                                                                                                                                                                                       |
| --------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `app/Enums/EpisodeProvider.php` `app/Enums/EpisodeType.php`                                               | edit   | `GoogleDrive` case, `connection()` and `isAccountBound()` (true) arms; `allowedProviders()` for file, video and audio                                                                       |
| `app/Integrations/Google/GoogleDrive.php`                                                                 | new    | The integration; `app/Integrations/Google/` is created by `T-044`                                                                                                                           |
| `app/Providers/IntegrationServiceProvider.php`                                                            | edit   | `GoogleDrive::class` in `T-091`'s `grant-providers` tag (beside `media-providers`, `:35-39`)                                                                                                |
| `app/Services/VendorAccessService.php`                                                                    | edit   | `T-091`'s class; `describeItem()`, `checkItems()` — the loop over `T-091`'s `checkEpisode()`                                                                                                |
| `app/Services/EpisodeService.php`                                                                         | edit   | Second constructor dependency after `T-044`'s, rebased on `T-124`'s and `T-130`'s constructor; `describeItem()` in `add()` after `guardProviderConnected()`; the grants a new Episode needs |
| `app/Services/AccessService.php` `app/Services/CheckoutService.php`                                       | edit   | `guardItemCapacity()` and its two callers                                                                                                                                                   |
| `app/Http/Controllers/Share/GoogleDriveController.php`                                                    | new    | The picker token                                                                                                                                                                            |
| `app/Http/Controllers/Share/SeriesController.php`                                                         | edit   | `picker` prop on `show()` (`:137`); `missingSince` on each Episode (`:158-166`), which `T-096`, `T-098` and `T-100` read as it is                                                           |
| `app/Http/Controllers/Share/EpisodeCheckController.php`                                                   | new    | Check now; `MANUAL_CHECK_SECONDS`; flashing from `EpisodeCheckOutcome`; `T-090` adds its arm                                                                                                |
| `app/Http/Requests/Share/StoreEpisodeRequest.php`                                                         | edit   | `google_drive` arm of `content()` (`:184-198`); `file_name`, `mime_type` inputs                                                                                                             |
| `app/Console/Commands/CheckEpisodeItemsCommand.php`                                                       | new    | `qori:episodes:check`; the pass is `checkItems()`; `T-090` adds `checkDue()`                                                                                                                |
| `routes/share/payments.php` `routes/share/episodes.php` `routes/console.php`                              | edit   | The picker route beside `T-044`'s `share.connections.*`; `share.series.episodes.check`; the one schedule line                                                                               |
| `resources/js/pages/share/series/Show.vue`                                                                | edit   | `allowed` map (`:198-203`), `providerLabels` (`:290-296`), the Drive file pick on the Episode form, Check now beside the flag                                                               |
| `resources/js/components/series/GoogleDrivePicker.vue` `resources/js/lib/googlePicker.ts`                 | new    | The Picker; loads `https://apis.google.com/js/api.js`                                                                                                                                       |
| `lang/en/connections.php` `lang/en/series.php` `lang/en/errors.php` `lang/en/accesses.php`                | edit   | Copy below; `connections.php` is `T-044`'s file; `provider_not_allowed.resolution` (`errors.php:186`)                                                                                       |
| `config/services.php` `config/qori.php` `.env.example`                                                    | edit   | `services.google.api_key`, `services.google.project_number` in `T-044`'s `google` block; the cap number                                                                                     |
| `app/Integrations/Dropbox/DropboxStorage.php`                                                             | edit   | Docblock `:17-19` only: Drive is no longer excluded                                                                                                                                         |
| `tests/Feature/Integrations/Google/GoogleDriveTest.php` `tests/Feature/Series/GoogleDriveEpisodeTest.php` | new    | 14 and 9 cases; a vendor's own tests sit in `tests/Feature/Integrations/<Vendor>/`, as `Stripe/ClientTest.php` does, and the Series page's in `Series/`                                     |
| `tests/Feature/Shared/GoogleDriveJourneyTest.php`                                                         | new    | 11 cases                                                                                                                                                                                    |
| `tests/Feature/Console/CheckEpisodeItemsCommandTest.php` `tests/Feature/Series/EpisodeCheckTest.php`      | new    | 4 cases; 6 cases; `T-090` adds its own to both                                                                                                                                              |
| `tests/Feature/Checkout/GoogleDriveCapTest.php`                                                           | new    | 3 cases                                                                                                                                                                                     |
| `docs/flows/vendor-access.md`                                                                             | edit   | Created by `T-091`; the Google chain, `qori:episodes:check` and Check now are added here                                                                                                    |
| `docs/flows/storage.md` `docs/flows/series.md` `docs/tinker/series.md` `docs/project-plan.md`             | edit   | The providers table and `:56`; the Episode content shape; a recipe; §8 and §16                                                                                                              |

`docs/flows/vendor-access.md` and `storage.md` are the flow docs for the
`app/Http`, `app/Services` and `routes/` rows. `qori:reachability` sees the
new routes through their names in `Show.vue`.

## Database

None. `vendor_grants` is `T-091`'s, with the item columns the first open
question below asks it for; this task writes `vendor_grants.vendor_ref` (the
permission id Google returned for that file). `episodes.content` (jsonb,
`create_qori_schema.php:113`) holds, for `google_drive`: `file_id`, `name`,
`mime_type`, `web_view_link`, `checked_at`, `missing_since` (null while the
file is fine).

## Code

```php
// EpisodeProvider
case GoogleDrive = 'google_drive';
// connection(): self::GoogleDrive => ConnectionProvider::GoogleDrive,   (T-044's case)
// isAccountBound(): self::GoogleDrive => true,   (T-044's method; the file id means nothing without the account)

// EpisodeType::allowedProviders()
self::File  => [EpisodeProvider::CloudflareR2, EpisodeProvider::Dropbox, EpisodeProvider::GoogleDrive],
self::Video => [EpisodeProvider::Vimeo, EpisodeProvider::Dropbox, EpisodeProvider::GoogleDrive],
self::Audio => [EpisodeProvider::Dropbox, EpisodeProvider::GoogleDrive],   // T-093 played an MP3 as a reader
```

```php
namespace App\Integrations\Google;

/**
 * A creator's own Google Drive (D-016, D-036): one picked file per Episode, one reader permission per Peer per file.
 * Every $timeoutSeconds is the caller's budget — T-091's REQUEST_TIMEOUT_SECONDS or SWEEP_TIMEOUT_SECONDS — which this
 * client may only shorten: each call waits whichever is shorter, GoogleAccounts::TIMEOUT_SECONDS (T-044's, Google's own
 * limit) or the budget (D-034).
 */
class GoogleDrive implements GrantsPeerAccess
{
    public const BASE = 'https://www.googleapis.com/drive/v3';
    public const SHORTCUT_MIME = 'application/vnd.google-apps.shortcut';
    /** files.get field mask, for a picked file and the item check. */
    public const FILE_FIELDS = 'id,name,mimeType,trashed,webViewLink';
    public const ERROR_NO_GOOGLE_ACCOUNT = 'no_google_account';   // cannotInviteNonGoogleUser (T-093 Q7)
    public const ERROR_SHORTCUT = 'shortcut';
    // A permission Google no longer holds is T-091's GrantResult::ERROR_PERMISSION_GONE; a file it no longer
    // returns is T-091's ERROR_ITEM_MISSING. Both are shared by every provider that grants on an item.

    public function provider(): ConnectionProvider;   // ConnectionProvider::GoogleDrive
    /** Which target this provider grants on (T-091, D-036), so the service knows whether a Series needs a row per container or per Episode. */
    public function grantsOn(): GrantTarget;          // GrantTarget::Item
    /** Container providers only; never asked of this one, which answers ContainerCheck(exists: false). */
    public function checkContainer(Connection $connection, string $externalId, int $timeoutSeconds): ContainerCheck;
    /** The row carries the file id in external_target_id and its Episode. null identity → awaitingIdentity(), no call. Else permissions.list on the file; the identity's email present → granted(id), no create. Else permissions.create → granted(id). */
    public function grant(Connection $connection, VendorGrant $grant, ?GrantIdentity $identity, string $email, int $timeoutSeconds): GrantResult;
    /** permissions.get(file, vendor_ref): 200 → granted(id); 404 → pending(GrantResult::ERROR_PERMISSION_GONE), which the next grant() re-creates; a 404 on the file itself → needsCreator(ERROR_ITEM_MISSING). */
    public function checkGrant(Connection $connection, VendorGrant $grant, int $timeoutSeconds): GrantResult;
    /** permissions.delete(file, vendor_ref); 204 and 404 are both revoked(). */
    public function revoke(Connection $connection, VendorGrant $grant, int $timeoutSeconds): RevokeResult;
    /** content['web_view_link'] with authuser=<the confirmed address> appended; null when content['missing_since'] is set, which T-089 turns into the redirect back to the Series page. No call. accountHint is VendorIdentity::verifiedFor($grant->access->user, IdentityProvider::forConnection($this->provider()))?->email (T-092). */
    public function openLink(Connection $connection, Episode $episode, ?VendorGrant $grant, int $timeoutSeconds): VendorLink;
    /** files.get on content['file_id']: exists (200, trashed false), insideContainer null, plus T-091's nullable name, mimeType and url (name, mimeType, webViewLink), which describeItem() reads. A timeout, 429 or 5xx sets errorCode and the caller writes nothing. */
    public function checkItem(Connection $connection, Episode $episode, int $timeoutSeconds): ItemCheck;

    private function client(Connection $connection, int $timeoutSeconds): PendingRequest;   // withToken, acceptJson, timeout(min(GoogleAccounts::TIMEOUT_SECONDS, $timeoutSeconds)); no retry
    private function existingPermission(Connection $connection, string $fileId, string $email, int $timeoutSeconds): ?string;
    private function failure(Response $response): GrantResult;   // the mapping below
    private function reason(Response $response): ?string;        // errors[0].reason, from the fixtures' shape
}
```

The calls, each with its reference page and the `T-093` fixture the test
reads:

| Call                                                                                                                                                                                 | Reference                                                                              | Fixture                                                                                                                                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET {BASE}/files/{fileId}?fields={FILE_FIELDS}&supportsAllDrives=true`                                                                                                              | https://developers.google.com/workspace/drive/api/reference/rest/v3/files/get          | `files-get-episode-file.json`, `files-get-trashed.json`, `errors-files-get-unpicked-404-notFound.json`, `errors-files-get-folder-other-account-404-notFound.json`                                                                                                      |
| `GET {BASE}/files/{fileId}/permissions?fields=permissions(id,type,role,emailAddress)&supportsAllDrives=true`                                                                         | https://developers.google.com/workspace/drive/api/reference/rest/v3/permissions/list   | `permissions-list-folder.json`, `permissions-list-folder-before-grant.json`                                                                                                                                                                                            |
| `GET {BASE}/files/{fileId}/permissions/{permissionId}?fields=id,type,role,emailAddress&supportsAllDrives=true`                                                                       | https://developers.google.com/workspace/drive/api/reference/rest/v3/permissions/get    | `permissions-get.json`, `errors-permissions-get-404-notFound-removed-by-hand.json`                                                                                                                                                                                     |
| `POST {BASE}/files/{fileId}/permissions?sendNotificationEmail=false&supportsAllDrives=true&fields=id,type,role,emailAddress` body `{"type":"user","role":"reader","emailAddress":…}` | https://developers.google.com/workspace/drive/api/reference/rest/v3/permissions/create | `permissions-create-folder.json`, `permissions-create-repeat.json`, `errors-permissions-create-401-authError.json`, `errors-permissions-create-403-cannotInviteNonGoogleUser-no-account.json`, `errors-permissions-create-400-invalidSharingRequest-cannot-share.json` |
| `DELETE {BASE}/files/{fileId}/permissions/{permissionId}?supportsAllDrives=true`                                                                                                     | https://developers.google.com/workspace/drive/api/reference/rest/v3/permissions/delete | `permissions-delete.txt`, `errors-permissions-delete-404-notFound.json`                                                                                                                                                                                                |

`failure()`: `reason` in `sharingRateLimitExceeded`, `rateLimitExceeded`,
`userRateLimitExceeded`, status 429 or 5xx, or a `ConnectionException` →
`pending`, `retryAfterSeconds` from the `Retry-After` header when present, a
`ConnectionException` with `T-091`'s `ERROR_TIMEOUT`. `reason`
`invalidSharingRequest` or `domainPolicy` → `needs_creator` with that reason.
A 404 on the file → `needs_creator` with `ERROR_ITEM_MISSING`. Status 401 →
`needs_creator` with `ERROR_CONNECTION_UNUSABLE`. `cannotInviteNonGoogleUser`
→ `awaitingIdentity()`. Anything else → `needs_creator` with the vendor's
`reason`. The result's `upstream` is the status and `reason`, for logs only.

```php
// App\Services\VendorAccessService — additions to T-091's class
/** files.get, through checkItem() on an unsaved Episode carrying $provider and $content, with REQUEST_TIMEOUT_SECONDS: the file exists and is not a shortcut. Throws AppException. Returns the content with name, mime_type and web_view_link filled. */
public function describeItem(Series $series, EpisodeProvider $provider, array $content): array;
/**
 * The item check's pass for the current Group: T-091's checkEpisode() on every Episode whose provider handles()
 * accepts. The EpisodeCheckOutcome each call answers is ignored here. Rows touched. This is the one scheduled thing
 * left in the storage stream (D-040) and it earns it: it looks for a file that moved, which no Open would discover
 * until a Peer met the error, where a missing grant is made the moment somebody asks for it.
 */
public function checkItems(): int;
// checkEpisode(Episode, int): EpisodeCheckOutcome is T-091's (D-021) — the one-Episode check this loop and Check now
// both call. It records into content.checked_at and content.missing_since and answers Clear, Flagged, NeedsCreator
// or Unreadable; only Check now reads the answer.

// App\Services\EpisodeService — add() gains, after T-044's guardProviderConnected():
public function __construct(private ConnectionService $connections, private VendorAccessService $vendorAccess) {}   // the first is T-044's
// — written before T-124's and T-130's constructor and T-123's add(); rebased on them once they land (see below)
// $content = $this->vendorAccess->describeItem($series, $provider, $content);  when $this->vendorAccess->handles($provider)
//   exists false                            → errors.series.episode_file_not_found
//   mimeType === GoogleDrive::SHORTCUT_MIME → errors.series.shortcut_not_allowed
// Nothing follows the save: no grant rows are written and no vendor is called for a grant (D-040). The first Peer
// to press Open on this Episode creates its row and grants it. guardItemCapacity() is checked here too, because
// adding a file already at its cap to a Series with more Peers than it has room for is an admission point (F09).

// App\Services\AccessService
/**
 * The physical file's room, not the Series' size (F09): the Group's granted and awaiting_acceptance rows on that
 * external_target_id, plus the checkouts already admitted against it, against
 * config('qori.storage.google_drive.max_peers_per_file'); errors.access.series_full. Readers the creator added by
 * hand are outside the count and the Decisions say so. Called from guardGrantlable() when ! $paid (:308), from
 * CheckoutService::begin() beside guardPeerLimit() (:48-50), and from EpisodeService::add() when a file is picked
 * or replaced; never from fulfil() (PLAN.md rule 2).
 */
public function guardItemCapacity(Series $series, ?string $externalTargetId = null): void;
```

```php
namespace App\Http\Controllers\Share;

class GoogleDriveController extends Controller
{
    /** JSON {token, apiKey, appId} for the Picker. Owner only; T-044's ConnectionService::fresh() first; errors.series.provider_not_connected when there is no live connection. */
    public function picker(string $group, CurrentGroup $current, ConnectionService $connections): JsonResponse;
}

// App\Http\Requests\Share\StoreEpisodeRequest::content(), new arm:
//   EpisodeProvider::GoogleDrive => ['file_id' => $reference, 'name' => $this->input('file_name'), 'mime_type' => $this->input('mime_type')],
//   'file_name' and 'mime_type' are ['nullable', 'string', 'max:200']; describeItem() overwrites both from files.get.
```

```php
// App\Console\Commands\CheckEpisodeItemsCommand — new (D-021); T-090 extends it
protected $signature = 'qori:episodes:check {--dry-run : Count what is due, call nothing}';
protected $description = 'Re-read every vendor-hosted Episode and flag the ones that stopped working';
public function handle(VendorAccessService $vendorAccess, CurrentGroup $current): int;
// foreach (Group::query()->cursor() as $group): $current->runFor($group, fn (): int => $vendorAccess->checkItems())
//   — Group::query() carries no BelongsToGroup, so no acrossAllGroups(). T-090 adds VideoLibraryService $videos to handle() and $videos->checkDue()
//   to the closure; it changes neither the signature's name nor the schedule
// per Episode, T-091's checkEpisode():
//   exists  → content.checked_at = now, missing_since = null
//   else content.missing_since ??= now — the creator's Series page shows series.episode.google_drive.stale on that row
// routes/console.php — the one schedule line. Provisional hour (see below)
Schedule::command('qori:episodes:check')->daily();
```

```php
namespace App\Http\Controllers\Share;

/** Check now beside an Episode's check warning (D-021). New; T-090 adds its Vimeo and YouTube arm. */
class EpisodeCheckController extends Controller   // ResolvesShareSeries
{
    /** Per Episode; provisional. RateLimiter key episode-check:{episodeId}. */
    public const MANUAL_CHECK_SECONDS = 60;

    /** POST share.series.episodes.check. Any collaborator who can manage the Series' Episodes, as EpisodeController allows: the vendor call uses the Group's connection server-side and no token leaves the server. */
    public function __invoke(string $group, string $seriesId, string $episodeId, VendorAccessService $vendorAccess, Terminology $terminology): RedirectResponse;
}
// $series = $this->seriesById($seriesId); $episode = $series->episodes()->findOrFail($episodeId)
// a provider no arm takes — handles() false — abort_if 404; nothing throttled or called
// RateLimiter::tooManyAttempts('episode-check:'.$episode->getKey(), 1) → series.episode_check.wait through
//   Terminology::choice() with :seconds from RateLimiter::availableIn(); back(); no call
// else hit(), then $vendorAccess->checkEpisode($episode, VendorAccessService::REQUEST_TIMEOUT_SECONDS):
//   EpisodeCheckOutcome::Clear        → series.episode_check.clear
//   EpisodeCheckOutcome::Flagged      → series.episode_check.still
//   EpisodeCheckOutcome::NeedsCreator → series.episode_check.needs_creator, :provider from connections.providers.<value>.name
//   EpisodeCheckOutcome::Unreadable   → series.episode_check.unreadable through Terminology::choice() on :seconds
// back() to the creator's Series page, which re-reads missingSince
```

```php
// config/services.php — T-044's 'google' block gains
'api_key' => env('GOOGLE_API_KEY'),                // the Picker's developer key
'project_number' => env('GOOGLE_PROJECT_NUMBER'),  // setAppId
// config/qori.php, under 'storage' — Google's documented figure for one file
'google_drive' => ['max_peers_per_file' => 600],
```

`SeriesController::show()` (`:137`) adds
`'picker' => ['connected' => bool, 'url' => route('share.connections.google_drive.picker', …), 'providerName' => …]`
with `providerName` from `connections.providers.google_drive.name` (`T-044`'s
key), and `'missingSince' => $episode->content['missing_since'] ?? null` on
each Episode (`:158-166`; null wherever the content has no such key, so
`T-096`, `T-098` and `T-100` read this one as it is). `Show.vue`'s Episode
form, for `google_drive`, replaces the reference input with
`GoogleDrivePicker`, which fills hidden `reference`, `file_name` and
`mime_type` from the callback's `docs[0]` (`picker-file-picked.json`), and
shows `series.episode.google_drive.pick` and
`series.episode.google_drive.browser` beside it, with
`series.episode.google_drive.explain` under them and, under that, the three
habit lines as a list titled `series.episode.google_drive.habits.title`. When
Google is not connected the form shows
`series.episode.google_drive.connect_first` in place of the pick. `googlePicker.ts` loads the API once and builds
`new google.picker.PickerBuilder().setAppId(appId).setOAuthToken(token).setDeveloperKey(apiKey).addView(new google.picker.DocsView())`
(https://developers.google.com/workspace/drive/picker/guides/web-picker). An
Episode row whose `missingSince` is set shows a `warning` `InlineNotice`
(`resources/js/components/shell/InlineNotice.vue`) titled
`series.episode.google_drive.stale_title`, described by
`series.episode.google_drive.stale`, and, inside it, Check now
(`series.episode_check.check_now`): a form posting to
`` `${episodesUrl}/${episode.id}/check` ``, as the row's delete form posts to
its own path (`:481-482`). The `providerLabels` map gains `google_drive` from
the `picker.providerName` prop, not an inline literal.

## Copy

`:people` comes from `config('qori.storage.google_drive.max_peers_per_file')`.
`:seconds` is `RateLimiter::availableIn()`, never the number written out, and
`series.episode_check.wait` and `.unreadable` go through
`Terminology::choice()` on it. `:provider` in `unreadable` and
`needs_creator` is `connections.providers.<value>.name` for the Episode's
`connection()`, so both lines serve `T-090`'s arm as they are. The tier
limitation lines, the provider name and the tier labels are `T-044`'s.

**The three habit lines are the whole of what this design asks of a creator,
so they are written where they pick and not buried in help.** Add a file:
choose it here. Change what people see: edit the file where it is, or upload a
new version over it, which keeps the same file — `T-093` step 13 row 2 saw the
id survive and `version` rise, and row 3 saw "Keep both files" make a file the
token cannot read at all. Stop people opening one: do it here, so the readers
Qori added come off. Each habit costs at most one stale Episode when it is
forgotten, which the daily check and Check now find and the creator repairs by
picking again; under a folder grant the same slip blocked every grant and
every removal in the Series, which is why `D-036` moved the grant to the file.
Nothing else a creator does in Drive matters — moving, renaming or refiling a
file keeps the permissions Qori made on it, as Drive's own warning on a move
says of anything shared directly.

| Key                                                                  | File                      | English                                                                                                                                                                           |
| -------------------------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `connections.providers.google_drive.limits.common.cap`               | `lang/en/connections.php` | Google lets up to :people people open one file. A :series with more :peer_plural than that needs a second copy of the file.                                                       |
| `connections.grants.reasons.invalidSharingRequest`                   | `lang/en/connections.php` | Google would not share this file — your organisation may not allow sharing outside it, or you may not be allowed to share this file; its owner or your administrator can allow it |
| `connections.grants.reasons.domainPolicy`                            | `lang/en/connections.php` | your organisation's admin has turned off third-party apps for Google Drive; they can allow Qori to share on your behalf                                                           |
| `series.episode.google_drive.pick`                                   | `lang/en/series.php`      | Choose the file in Google Drive                                                                                                                                                   |
| `series.episode.google_drive.explain`                                | `lang/en/series.php`      | Everyone with access to this :series can open the file you choose, and nothing else in your Drive. Edit it or upload a new version any time and they see it.                      |
| `series.episode.google_drive.habits.title`                           | `lang/en/series.php`      | Come back here to change what people can open                                                                                                                                     |
| `series.episode.google_drive.habits.add`                             | `lang/en/series.php`      | Adding a file in Google Drive shares it with nobody. Choose it here, and Qori lets everyone with access open it.                                                                  |
| `series.episode.google_drive.habits.version`                         | `lang/en/series.php`      | To change what people see, edit the file where it is or upload a new version over it. Saving a second copy makes a different file, so choose that one here.                       |
| `series.episode.google_drive.habits.remove`                          | `lang/en/series.php`      | To stop people opening a file, remove the :episode here or choose a different file. Deleting it in Google Drive leaves this :episode pointing at nothing until you come back.     |
| `series.episode.google_drive.browser`                                | `lang/en/series.php`      | The chooser needs you signed in to Google in this browser, with its cookies allowed. If nothing appears, allow cookies for this site and try again.                               |
| `series.episode.google_drive.connect_first`                          | `lang/en/series.php`      | Connect Google Drive under Integrations to choose a file.                                                                                                                         |
| `series.episode.google_drive.sharing`                                | `lang/en/series.php`      | Qori is letting everyone with access open this file. They can open it as soon as Google has let them in.                                                                          |
| `series.episode.google_drive.replaced`                               | `lang/en/series.php`      | Qori is taking the people it let in off the file you replaced. Your files are left as they are.                                                                                   |
| `series.episode.google_drive.stale_title`                            | `lang/en/series.php`      | Qori can't reach this file any more                                                                                                                                               |
| `series.episode.google_drive.stale`                                  | `lang/en/series.php`      | It was deleted, put in the bin, or replaced by a new copy, or it belongs to a Google account you are no longer connected with. Choose the file again.                             |
| `series.episode_check.check_now`                                     | `lang/en/series.php`      | Check now                                                                                                                                                                         |
| `series.episode_check.clear`                                         | `lang/en/series.php`      | Checked just now. That :episode opens for everyone with access.                                                                                                                   |
| `series.episode_check.still`                                         | `lang/en/series.php`      | Checked just now, and nothing has changed yet. The note beside the :episode says what's left.                                                                                     |
| `series.episode_check.needs_creator`                                 | `lang/en/series.php`      | Qori can't check that :episode until you reconnect :provider. The note on this page says what to do.                                                                              |
| `series.episode_check.wait`                                          | `lang/en/series.php`      | `{1} You checked a moment ago. You can check again in a second.\|[2,*] You checked a moment ago. You can check again in :seconds seconds.`                                        |
| `series.episode_check.unreadable`                                    | `lang/en/series.php`      | `{1} Qori couldn't reach :provider just now, so that :episode wasn't checked. You can try again in a second.\|[2,*] … in :seconds seconds.`                                       |
| `accesses.vendor.google_drive.before_buying.common.account`          | `lang/en/accesses.php`    | A Google account — Gmail, or any other address with a Google account. You sign in with it once in Qori, and the files open on Google's own site.                                  |
| `accesses.vendor.google_drive.before_buying.common.receiving_policy` | `lang/en/accesses.php`    | If that's a work or school account that only accepts files from approved organisations, it can't open these files. Use a personal Google account instead.                         |
| `errors.series.episode_file_not_found.message`                       | `lang/en/errors.php`      | That file couldn't be found in the connected account.                                                                                                                             |
| `errors.series.episode_file_not_found.resolution`                    | `lang/en/errors.php`      | Choose it again in Google Drive.                                                                                                                                                  |
| `errors.series.shortcut_not_allowed.message`                         | `lang/en/errors.php`      | That's a shortcut, not the file itself.                                                                                                                                           |
| `errors.series.shortcut_not_allowed.resolution`                      | `lang/en/errors.php`      | Choose the file it points at. A shortcut doesn't share the file.                                                                                                                  |
| `errors.access.series_full.message`                                  | `lang/en/errors.php`      | This :series can't let anyone else in right now.                                                                                                                                  |
| `errors.access.series_full.resolution`                               | `lang/en/errors.php`      | Ask whoever shared it with you to make room.                                                                                                                                      |
| `errors.series.provider_not_allowed.resolution`                      | `lang/en/errors.php`      | Video and audio need external storage — connect Google Drive, Vimeo or Dropbox and link the file there.                                                                           |

## Routes

| Verb | Path                                                      | Name                                    | Action                                |
| ---- | --------------------------------------------------------- | --------------------------------------- | ------------------------------------- |
| GET  | `/g/{group}/connections/google-drive/picker`              | `share.connections.google_drive.picker` | `Share\GoogleDriveController::picker` |
| POST | `/g/{group}/series/{seriesId}/episodes/{episodeId}/check` | `share.series.episodes.check`           | `Share\EpisodeCheckController`        |

Both inside the sharing group (`routes/share.php:24-27`): the picker route in
`routes/share/payments.php` beside `T-044`'s `share.connections.*` and
`share.settings.integrations` (`:20-21`), and the check route in
`routes/share/episodes.php` beside `series.episodes.destroy` — added here, and
used by `T-090`'s arm as it is (`D-021`). Ids on the writes; the picker is
JSON, not a page. Open stays `T-089`'s `shared.episodes.open`; Check again
(`shared.access.check`) and Try again now
(`share.settings.integrations.retry`) are `T-091`'s.

## Tests

Every case fakes HTTP with the named fixture through
`Http::fake(['www.googleapis.com/*' => …])` and `Http::preventStrayRequests()`
in `setUp`, as `tests/Feature/Storage/PlaybackTest.php:36` does; `T-091`'s
`VendorAccessService` is resolved with the real `GoogleDrive` in the tag, and
the Peer's identity comes from `T-092`'s `VendorIdentityFactory`.

**New: `tests/Feature/Integrations/Google/GoogleDriveTest.php` — 14 cases**

1. `test_it_grants_a_reader_on_the_file_with_notification_off` — `permissions-list-folder-before-grant.json` (no Peer on it), then `permissions-create-folder.json`; `assertSent` sees the file id in the path, the body and `Bearer`; `granted`, `vendorRef` is the fixture's `id`.
2. `test_a_permission_already_on_the_file_is_adopted_not_created` — the list shows the address; no POST; `granted` with the listed `id`.
3. `test_a_grant_without_an_identity_makes_no_call` — `awaiting_identity`; zero requests.
4. `test_a_rate_limit_is_pending_with_the_retry_after` — written only if `T-093`'s Workspace pass keeps a rate-limit body; otherwise `failure()`'s branch is covered by a unit test on the documented `reason` strings alone and this case is dropped from the count.
5. `test_a_refusal_to_share_needs_the_creator` — `errors-permissions-create-400-invalidSharingRequest-cannot-share.json`; `needs_creator`, `errorCode` `invalidSharingRequest`.
6. `test_an_address_without_a_google_account_is_awaiting_identity` — `errors-permissions-create-403-cannotInviteNonGoogleUser-no-account.json`.
7. `test_a_missing_file_needs_the_creator` — `errors-files-get-unpicked-404-notFound.json` on the permissions call's file; `ERROR_ITEM_MISSING`.
8. `test_a_timeout_is_pending_with_the_timeout_it_was_given` — `Http::fake` throws `ConnectionException`; `ERROR_TIMEOUT`; the request carried the seconds passed in, and a budget above `GoogleAccounts::TIMEOUT_SECONDS` was cut to it (`D-034`).
9. `test_an_expired_token_is_connection_unusable` — `errors-permissions-create-401-authError.json`.
10. `test_check_grant_reads_the_stored_permission_and_reports_it_gone` — `permissions-get.json` → `granted`; `errors-permissions-get-404-notFound-removed-by-hand.json` → `pending`, `GrantResult::ERROR_PERMISSION_GONE`.
11. `test_it_revokes_by_permission_id_and_treats_a_404_as_revoked` — `permissions-delete.txt`, then `errors-permissions-delete-404-notFound.json`.
12. `test_open_link_is_the_stored_link_with_authuser_and_the_account_hint` — no HTTP call; the URL ends `authuser=` the identity's address, and `accountHint` is that address.
13. `test_open_link_is_null_once_the_file_is_flagged` — `missing_since` set; `T-089` turns it into the redirect.
14. `test_check_item_reports_a_trashed_file_and_a_file_the_account_cannot_see` — `files-get-trashed.json`, then `errors-files-get-folder-other-account-404-notFound.json`, the shape a reconnect with a different account leaves.

**New: `tests/Feature/Series/GoogleDriveEpisodeTest.php` — 9 cases**

15. `test_a_drive_episode_stores_the_file_id_name_type_and_link` — the post carries `reference`, `file_name` and `mime_type` from `picker-file-picked.json`'s `docs[0]`; `files-get-episode-file.json`; `content` keys.
16. `test_a_file_the_account_cannot_read_is_refused` — `errors-files-get-unpicked-404-notFound.json`; `episode_file_not_found`.
17. `test_a_shortcut_is_refused` — a `files.get` whose `mimeType` is the shortcut type; `shortcut_not_allowed`.
18. `test_adding_an_episode_writes_no_grant_rows_and_calls_no_vendor` — three active Accesses; zero grant rows on the new Episode and zero `permissions` requests in the creator's request (`D-040`).
19. `test_the_first_open_grants_that_episode_and_only_that_episode` — a Peer opens the second of three Drive Episodes: one `permissions.create`, on that file, one row; the other two Episodes have no row at all.
20. `test_replacing_an_episodes_file_revokes_the_readers_of_the_old_one` — the old file's granted rows are each deleted with one inline call, what fails is `revoke_failed` on the Integrations page, and the toast is `series.episode.google_drive.replaced`.
21. `test_the_picker_endpoint_returns_the_owners_token_and_keys_or_says_google_is_not_connected` — `provider_not_connected`; an admin gets `T-044`'s owner refusal.
22. `test_the_series_page_carries_the_picker_props_and_the_browser_line` — `picker.connected`, `picker.url`, `picker.providerName`, and `series.episode.google_drive.browser` in the props whether or not Google is connected; the three `series.episode.google_drive.habits.*` lines resolve and carry no untranslated `:episode`.
23. `test_the_series_page_flags_an_episode_whose_file_is_gone` — `missingSince` on that Episode only; zero requests.

**New: `tests/Feature/Shared/GoogleDriveJourneyTest.php` — 11 cases**

24. `test_a_new_peer_who_buys_is_granted_on_every_episode_file_and_opens_one` — `CheckoutService::fulfil()` with an identity and two Episodes; both rows `granted`; `GET shared.episodes.open` is a 302 to the fixture's `webViewLink` with `authuser`.
25. `test_a_new_peer_who_claims_a_free_series_is_granted_in_the_same_request`.
26. `test_a_series_of_twenty_episodes_costs_one_call_for_one_open` — twenty Drive Episodes, one Peer, one Open: exactly one `permissions.create` in the whole journey (`D-040`).
27. `test_open_grants_the_one_episode_it_needs_when_its_row_is_still_pending` — one create in the Open request, then the 302.
28. `test_a_peer_without_a_google_identity_is_prompted_not_refused` — `awaiting_identity`; `T-092`'s prompt; Open redirects to `shared.show` at `#access` with the `shared.vendor_notice.redirected` flash (`T-089`, `D-020`); zero requests to Google.
29. `test_open_rereads_the_permission_and_regrants_when_google_lost_it` — a `granted` row with a stale `checked_at`; `permissions.get` is the 404 fixture; a create; 302 in the same request.
30. `test_a_pending_grant_is_retried_by_pressing_open_again` — the first Open answers `pending(ERROR_TIMEOUT)` and redirects to the notice; once the row is due, a second Open grants and redirects to Google.
31. `test_a_workspace_refusal_reaches_the_creator_with_its_reason` — the Integrations page lists the row with `connections.grants.reasons.invalidSharingRequest`; the Peer's page says `needs_creator`. Nothing refused the tier first.
32. `test_try_again_now_lets_a_refused_peer_in_once_google_allows_it` — `POST share.settings.integrations.retry` for `google-drive` (`D-033`); list then create; the row is `granted` in the same request; flash `connections.grants.retried` (`T-091`).
33. `test_revoking_access_deletes_the_reader_on_every_file` — `AccessService::revoke()`; one delete per Episode; rows `revoked`.
34. `test_a_buyer_sees_what_a_google_drive_series_needs_before_paying` — `BuyerRequirements::for()` on a Series with a `google_drive` Episode answers `before_buying.common.account` then `.receiving_policy`; the public page carries both beside the buy form; with no Drive Episode the list is empty; zero requests.

**New: `tests/Feature/Console/CheckEpisodeItemsCommandTest.php` — 4 cases**

35. `test_it_flags_an_episode_whose_file_is_gone_or_trashed`.
36. `test_it_clears_the_flag_when_the_file_is_back_and_touches_checked_at`.
37. `test_it_writes_nothing_when_google_does_not_answer` — a `ConnectionException`; no flag, no `checked_at`.
38. `test_it_is_scheduled_daily` — the schedule lists `qori:episodes:check` once.

`T-090` adds its own cases to this file; none is counted here.

**New: `tests/Feature/Series/EpisodeCheckTest.php` — 6 cases**

39. `test_check_now_clears_a_flag_once_the_file_is_back` — `files-get-episode-file.json`; `Clear`; `missing_since` null; flash `series.episode_check.clear`; the request carried `REQUEST_TIMEOUT_SECONDS`.
40. `test_check_now_keeps_the_flag_while_the_file_is_still_gone` — `files-get-trashed.json`; `Flagged`; flash `series.episode_check.still`.
41. `test_check_now_writes_nothing_and_says_why_when_google_is_unreachable` — `ConnectionException`; `Unreadable`; nothing written; flash with `:provider` and `:seconds`.
42. `test_check_now_says_reconnect_when_the_connection_is_unusable` — `NeedsCreator`; zero requests.
43. `test_check_now_is_throttled_per_episode` — a second press inside `MANUAL_CHECK_SECONDS` makes no request and flashes `series.episode_check.wait`; another Episode is not throttled.
44. `test_check_now_on_an_episode_with_nothing_to_check_or_in_another_group_is_not_found` — a `cloudflare_r2` Episode is a 404; an Episode id from another Group is a 404; zero requests.

**New: `tests/Feature/Checkout/GoogleDriveCapTest.php` — 3 cases**

45. `test_a_sale_is_refused_at_the_file_cap` — `begin()`; `series_full`.
46. `test_a_free_claim_and_a_creator_add_are_refused_at_the_file_cap`.
47. `test_fulfilment_is_never_refused_at_the_cap` — `fulfil()` one over; `granted`.

## Acceptance

- [ ] On the public page of the paid Series, before paying, the buyer reads
      that they need a Google account and that a work or school account
      limited to approved organisations can't open it
- [ ] In a clean browser at 400px and desktop widths, a new Peer buys the
      paid Series (Stripe test mode), confirms their Google account, and opens
      the PDF, the Doc, the MP3 and the MP4 from the Series page in new tabs
      on Google's site; after the creator uploads a new version of the PDF and
      edits the Doc, both open with the new content and nothing else happening
      on either side
- [ ] The same walk for the free Series, from the Series link
- [ ] A Peer signed in to a second Google account in the same browser still
      lands on the file as the account they confirmed, and on the phone the
      file opens in the Drive app or the browser
- [ ] Before choosing a file, the creator reads the three habits on the
      Episode form: come back here to add one, upload a new version over the
      file rather than saving a second copy, and remove it here rather than in
      Drive
- [ ] A creator who adds a fifth Episode to a Series with Peers sees the
      sharing line on it, and every Peer can open it the first time they
      press Open, without the creator doing anything
- [ ] A Workspace creator whose administrator has turned outside sharing off
      still connects, picks a file and reaches the grant — nothing in Qori
      refuses the tier first
- [ ] A grant Google refuses is `needs_creator` on the Integrations page with
      a reason naming what their administrator has to allow, and the Peer sees
      a sentence naming who resolves it, never a dead page — Open on it
      returns to the Series page at the notice; a slowed grant ends `pending`
      and a second Open, once the row is due, works
- [ ] Once the administrator allows sharing, the creator's Try again now lets
      the waiting Peer in, or says plainly that Google has not applied it yet
- [ ] A purchase, a claim and adding an Episode each make zero Drive calls,
      and a Peer who opens three Episodes of twenty costs three
      `permissions.create` and no more (`D-040`)
- [ ] A removal Google refuses is listed on the Integrations page with the
      Peer and the file, a Try again calls Google once more, and nothing
      retries it on its own
- [ ] A reader removed by hand in Drive is granted again on the Peer's next
      Open
- [ ] Revoking the Peer's access removes the reader from every file; a reload
      shows Google's "You need access" page
- [ ] A file put in the bin is flagged on the creator's Series page after
      `qori:episodes:check`; Open on it lands back on the Peer's Series page
      at the notice; restored, Check now beside the flag clears it at once,
      and a second press inside `MANUAL_CHECK_SECONDS` says when the next is
      allowed; with Google unreachable, Check now says so and the flag stays
- [ ] The creator reconnecting with a different Google account is asked to
      confirm first; Keep leaves every Episode working; Switch leaves each
      Drive Episode flagged for a new pick, and picking each file again lets
      every Peer in
- [ ] Picking a different file for an Episode takes the readers Qori added off
      the old file and leaves the creator's files alone
- [ ] The line about what the chooser needs from the browser is on screen
      wherever a file is picked, and every sentence comes from lang
- [ ] `docs/flows/vendor-access.md`, `storage.md`, `series.md`, the tinker
      recipe and `docs/project-plan.md` §8 describe what was built
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **Added 21 September 2026:** connecting from setup and picking a file for an
  Episode is cut out as `T-159`, for the first-share journey. This task keeps
  what is left once that exists.

- ~~**`T-091` carries grants on an item.** Its draft has one row per (Access,
  container) and a contract taking a `SeriesContainer`.~~ **Written into
  `T-091` on 20 September 2026:** `GrantTarget` and `grantsOn()`, the
  `target`, `episode_id` and `external_target_id` columns with their unique
  pairs, `grant()`, `checkGrant()` and `revoke()` taking the row,
  `revokeItem()`, `ERROR_ITEM_MISSING` and `ERROR_ITEM_REPICK`, the lock on
  the target, and six cases of its own — then re-drafted again on `D-040`,
  which removed `ensureItem()` and `INLINE_GRANT_LIMIT` along with the sweep.
  This task still waits for `T-091` to be `ready`, as `depends:` says.
- ~~The value of `INLINE_GRANT_LIMIT`.~~ **Gone with `D-040`.** Kept here only
  so a reader of an older link knows where it went —
  the owner's, with `T-091`.
- Three fixtures this task's tests name were taken on a folder, not a file:
  `permissions-create-folder.json`, `permissions-list-folder.json` and
  `permissions-get.json`. The resource and the endpoint are the same and the
  bodies differ only in which `fileId` the request carried, so they serve as
  they are; whether the tests rename them, or `T-093`'s Workspace pass takes
  the same three on a file, is anyone's.
- Whether `qori:episodes:check` and Check now — the command, its schedule
  line, `EpisodeCheckController`, its route and copy, the `missingSince` prop
  and the two test files, which `T-090`, `T-096` and `T-098` wait on — stay
  here or are cut into their own task; a ready `L` names its split — the
  owner's. A split takes all of it together.
- `EpisodeCheckController::MANUAL_CHECK_SECONDS` 60, the provisional throttle
  on Check now per Episode (`D-021`) — anyone's; `T-090` reads the constant
  this task declares.
- The hour `qori:episodes:check` runs: this draft schedules `daily()`, which
  is midnight in the app's timezone, and an earlier `T-090` draft proposed
  `dailyAt('04:00')`. One line, written here — anyone's, with operations.
- Whether the creator's Series page says anything while a new Episode's grants
  are still pending. This draft writes `series.episode.google_drive.sharing`
  and shows it until every row on that Episode is `granted`, which costs a
  count per Episode on the page; the alternative is silence, since the Peer's
  own page already explains a grant that is not ready — anyone's, with a
  designer.
- Whether picking a different file for an Episode is an edit or a new
  Episode. `UpdateEpisodeRequest` validates title and preview only
  (`app/Http/Requests/Share/UpdateEpisodeRequest.php:24-30`), so today the
  creator deletes and adds, which is what case 20 tests; a Change file control
  would need the request, the service and the revoke of the old file's
  readers — anyone's, and the copy line
  `series.episode.google_drive.replaced` assumes it exists.
- `D-030`'s materials arm: the picker writing each picked item as a
  `materials` row with `provider = google_drive` on `T-130`'s table, each
  material's file granted like an Episode's and `T-091`'s `checkItem()`
  reading those rows too: whether that is this task, with `T-130` added to
  `depends:`, or its own task after this one. `T-130`'s
  `materials_content_matches_provider` check admits only `link` and
  `cloudflare_r2` rows and `MaterialService` refuses `google_drive`, so
  whichever task writes the rows widens both — the stream owner's.
- `D-025`'s in-place pick: a row holding a pasted link (`provider = link`)
  becomes a `google_drive` row only when it is picked through this connector,
  in place and with no re-adding. `T-093`'s `files-get-episode-file.json` is
  the body it reads; no route, service method, `Show.vue` control or test is
  written for it yet — anyone's.
- The `EpisodeService`, `EpisodeProvider`, `StoreEpisodeRequest` and
  `resources/js/pages/share/series/Show.vue` edits above are written against
  the code before `T-123`, `T-124` and `T-130`, all three `ready` and touching
  the same files: `T-124` declares
  `EpisodeService::__construct(private LiveSessionService $liveSessions)` and
  `T-130` adds `MaterialService` to it, so this task's dependencies join that
  constructor rather than declaring one; `T-123` changes `add()`, adds
  `EpisodeProvider::Link`, and adds a `link` arm to `content()` and to the
  page's `allowed` map. They are rewritten against those three once they land —
  anyone's.
- The cap and the Picker's credentials sit outside `app/Integrations/Google`:
  `AccessService::guardItemCapacity()` reads a number only Google Drive has,
  and `GoogleDriveController::picker()` assembles the Picker's token, API key
  and app id itself. `D-022` puts a vendor's limits and its credentials in its
  folder and has entry points only delegate, so both move behind the Google
  folder, with the Service and the controller asking it — anyone's.
- With `T-044`: `ConnectionService::fresh()` as the on-demand refresh the
  picker route calls, the `google` block in `config/services.php`, and
  `connections.providers.google_drive.*` as the key shape — taken from its
  draft; re-check when `T-044` is `ready` — anyone's.
- With `T-090`: whether YouTube under the same Google account is a second
  `Connection` or the same one, given one connection per provider — anyone's.
- Whether a Series that sells to more people than one file may hold — Google's
  600 — needs anything beyond the refusal this task writes, such as a second
  copy of each file. The cap is config and the refusal exists; a Series that
  reaches it has no path forward in Qori today — the owner's.

### `D-040` re-drafts this task, 20 September 2026

**Done, 20 September 2026.** The Decisions, Code, Tests and Acceptance above
are written on `D-040`, and the question it left open is answered here:
**`qori:episodes:check` keeps its schedule.** It is not a grant sweep and
`D-040` does not reach it — it looks for a file that was moved, binned or
replaced, which no Open would discover until a Peer met the error and which
the creator is the only person who can fix. A missing grant is made the
moment somebody asks for it; a missing file has to be noticed before anybody
asks. It is the one scheduled thing left in this stream, and the Code
section says so where it is declared. What follows is the note written when
the re-draft was still owed.

The owner removed the scheduled sweep: a Drive grant is made when a Peer
presses Open on that Episode and at no other time, a purchase makes no
vendor call at all, and a failed revoke is listed for the creator rather
than retried. This task's grant timing, its pending states and its fan-out
bound follow `T-091`'s re-draft. Two things are this task's own to settle
when it happens: whether the daily `qori:episodes:check` goes the same way —
it looks for a file that moved rather than a grant that is missing, so it
may earn its schedule where the sweep did not — and what the creator's
unresolved-removals list says in Drive's terms.

### From the storage review, 20 September 2026

- **A Drive-only Series asks a buyer for no Google account at all** (`F03`).
  `VendorIdentityService::neededFor()` reads the Series' active
  `SeriesContainer` rows, and under `D-036` Drive has none, so checkout finds
  no missing identity, shows none of the before-buying lines this task
  writes, and fulfilment writes item grants straight to `awaiting_identity`.
  Confirming Google in account settings does not release them either, because
  `identityConfirmed()` filters by the row's container provider. Required
  providers have to be derived from the targets that actually grant,
  including item Episodes — anyone's, and it is a defect `D-036` introduced,
  not an open preference.
- **Adoption has no ownership rule** (`F02`). This task adopts an existing
  permission it finds in the list, but the same file may serve two Series and
  the same Google account two Qori people, and `permissions-create-repeat.json`
  shows Google returning the identical permission id. A repeat create over a
  writer returns the writer role
  (`permissions-create-repeat-over-writer.json`), so adoption also needs a
  stated policy for a pre-existing writer or inherited permission — anyone's.
- **The capacity guard counts Qori's Accesses, not the file's people**
  (`F09`). A file with readers the creator added by hand, or one used by a
  second Series, passes the check and fails at Google; two checkouts both
  pass at 599 before either writes an Access; and adding a Drive Episode to
  an already large Series is an admission point the guard never sees. The
  "second copy of the file" line is an open question written as an answer:
  copying breaks the promise that one edit reaches everyone, and there is no
  mapping from a cohort to a copy. Needs an honest published Series size and
  reservation against the physical target before payment — the owner's.
- **Folder captures are not evidence for a file journey** (`F11`). The claim
  that `T-093`'s permission fixtures "serve as they are" is what `D-036`
  itself disproves: the target changes the behaviour. The successful bodies
  are usable shapes, and the field names this task uses are all in the
  committed files, but nothing here has been observed on a directly shared
  file — grant, open, recheck, remove, repeat remove, reconnect, or a
  refusal at capacity. The rate-limit branch is specified from documented
  reason strings with no observed response, which `PROCESS.md` forbids.
  Extend `T-093` with a direct-file pass before this is `ready` — anyone's.
- **Replacement and deletion lose the work needed to revoke** (`F01`), and
  Open and refund run their vendor calls inline with no total deadline
  (`F08`). Both are `T-091`'s to fix; this task inherits whatever it decides.

## Re-scope log

None.

## Notes

**The 20 September 2026 re-draft.** `T-093`'s report is the evidence and
`D-036` the decision; everything the folder carried is gone from this file.
The file name still ends `-from-a-series-folder-shared-with-each-peer` so that
`T-093`'s task and report keep working links; the title in the front matter is
the one to read. What the folder design would have needed, and why the owner
chose against it, is in the report's Found, not fixed and in `D-036`.

**What a per-file grant costs, in calls, and why `D-040` changed the
answer.** Granting ahead of use, one Peer joining a Series with `E` Drive
Episodes was `E` creates each preceded by a list, and one Episode added to a
Series with `P` Peers was `P` creates — 1.68 to 2.44 seconds each at
`T-093`'s measurement, with Google applying concurrent changes on one file
about half a second apart. Granting at Open, the answer is **one list and
one create, once, per Peer per Episode they actually open**, and the Peer who
waits for it is the one who asked. The arithmetic that needed a sweep and a
bound no longer exists. Google publishes no sharing rate limit; a
`sharingRateLimitExceeded` is `pending` with its `Retry-After`, and `T-093`
met none in 109 calls.

**Where Peer copy lives** was settled by `D-020`: `T-089` creates
`lang/en/shared.php`, and `T-091`'s notice lines are `shared.vendor_notice.*`
there; this task's only Peer-facing lines are its two `before_buying` lines,
in `accesses.php`. `T-044` carries every tier limitation line under
`connections.providers.google_drive.limits.*`, and `T-092` the line naming the
Google address to open with.

**No `Content-Security-Policy` is set** anywhere under `app/`, `config/`,
`bootstrap/`, `routes/` or `resources/` (grep, 16 September 2026), so nothing
blocks `apis.google.com` or the Picker's frame today; a CSP added later has to
allow both.

**The Picker's browser problem is real.** `T-093` met Safari refusing the
Picker with "The API developer key is invalid", and the published reports it
collected tie that message, an empty list and a sign-in wall to a browser
blocking the `docs.google.com` frame's cookies — Safari and every browser on
iOS by default, Chrome Incognito, Firefox's strict mode, Brave with Shields
up, in-app webviews. `series.episode.google_drive.browser` is the line that
says so, and naming Google in it is allowed here under `D-016`'s exception
because the creator is choosing that vendor's file.

**`CLAUDE.md`** still says integrations expose `name()` and are bound in
`AppServiceProvider`; the code says `provider()` and
`IntegrationServiceProvider` (`:29-39`), and this draft follows the code.
