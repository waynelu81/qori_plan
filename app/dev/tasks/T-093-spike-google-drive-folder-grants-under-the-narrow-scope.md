---
id: T-093
title: Spike: Google Drive folder grants under the narrow scope
stream: storage
status: done
owner: wayne
estimate: S
depends: none
blocks: T-044, T-091, T-094
---

# T-093 — Spike: Google Drive folder grants under the narrow scope

> Set `ready` by the stream owner on 19 September 2026. It runs once the
> owner's Google setup exists (`docs/planning/vendor-accounts.md`, Google
> Drive, steps 1 to 14). Written on 16 September 2026 from
> `D-016` and the owner's BYO blueprint, and specified from the owner's
> answers and the readiness audit of 19 September 2026: the Cloud project is
> the owner's and is checked here, not created; the spike runs In production
> only if `useqori.com` serves its home page, privacy policy and terms, and
> in Testing otherwise; and it keeps the fixtures `T-044`, `T-092` and
> `T-094` asked of it.

## Why

`D-016` builds Google Drive on one call: `permissions.create` on a Series
folder, made with the creator's `drive.file` token, once per Peer. Google
documents `drive.file` as per-file access to files the person opens with the
app or picks in the Picker
(https://developers.google.com/workspace/drive/api/guides/api-specific-auth),
and the Picker's `setSelectFolderEnabled` says only that it lets the person
select a folder
(https://developers.google.com/workspace/drive/picker/reference/picker.docsview.setselectfolderenabled).
No Google page says whether a folder picked that way accepts a permission
from that token, or whether the files inside it are visible to it. Nothing
under `app/` calls a Google API: `ConnectionProvider` has no Google case
(`app/Enums/ConnectionProvider.php:14-20`), `DropboxStorage`
(`app/Integrations/Dropbox/DropboxStorage.php:17-19`) and
`docs/flows/storage.md:56` still say Drive is excluded, and `tests/Fixtures/`
holds only the planning and reachability harness fixtures — no vendor
response at all.

`PROCESS.md` refuses a spec that names a vendor payload nobody has observed,
so `T-094`, and the Google parts of `T-044` and `T-092`, cannot be `ready`
until somebody makes these calls and keeps what came back. Afterwards:
`tests/Fixtures/google/` holds every response the Google integration will be
tested against — the creator's connect and the Peer's sign-in as well as the
grant — a report answers the ten questions below in order, with the seconds
each call took and who resolves each refusal, and `T-094` is specified from
it.

## Decisions taken to make this specifiable

**Nothing under `app/` is written, and the creator's tokens carry
`https://www.googleapis.com/auth/drive.file` alone.** The consent screen
declares `drive.file`, `openid` and `userinfo.email`
(`docs/planning/vendor-accounts.md`, Google Drive, step 9), the last two for
`T-092`'s Peer sign-in; every creator authorisation here requests
`drive.file` and nothing else, the one Peer sign-in, in step 2, requests
`openid email`, and no Drive call is made with a Peer's token. The calls are
made with `curl` against the REST endpoints, tokens come from Google's OAuth
2.0 Playground configured with the owner's local-development client (step 10
of the same section, whose redirect URIs include
`https://developers.google.com/oauthplayground`), and the pick runs from one
throwaway HTML page outside the repository, served at
`http://localhost:8000`. `T-044` owns the connect step and `T-094` the
integration class; a spike that starts either pre-empts a spec that is not
ready yet. The narrow scope is the one Qori will request, so a broader
diagnostic token cannot hide a step the Peer journey needs.

**The spike runs In production if `useqori.com` serves its home page,
privacy policy and terms when it starts, and in Testing otherwise.** Google
requires those three links of every external app in production
(https://support.google.com/cloud/answer/15549049); drafts of the last two
are in `docs/pptcs/`, and neither is published on 19 September 2026. In
Testing, every Google account the spike uses is listed under Test users, and
the free-tier pass finishes within 7 days of step 2's first consent, because
a Testing client's authorisations and their refresh tokens expire 7 days
after consent (https://support.google.com/cloud/answer/15549945). Nothing Q1
to Q10 asks depends on the status, and no step measures how long a token
lives: the report says which status the spike ran under, and for how long a
refresh token lasts in production it cites Google's documentation — no fixed
lifetime, ended by revocation, six months unused and the other reasons
listed there (https://developers.google.com/identity/protocols/oauth2) —
rather than measuring it. The Workspace pass, which may trail, runs In
production, or re-authorises whenever a token lapses. Brand verification is
skipped either way: the spike records what the unverified consent screen
shows, because `T-044`'s connect step shows the same screen until it is done
(`docs/planning/vendor-accounts.md`, Google Drive, step 13).

**A fixture is the response body, verbatim in content and
formatter-normalised in whitespace, named by the call and the case.** No
envelope: `Http::response()` takes a body and a status, so the file is the
body, an error's name carries its status and `reason`, and
`tests/Fixtures/google/README.md` lists date, call, request, status, seconds
and account role per file in one table. `npm run check:fix` re-indents JSON
under `tests/` — `vite.config.ts` ignores nothing there, and the pre-commit
hook checks staged JSON — so a fixture may lose Google's own indentation; its
keys, values and their order stay exactly as Google sent them, and
`Http::response()` does not care about whitespace. `vite.config.ts` is not
changed. This is the first vendor fixture directory in the repository, so it
sets the shape the other spikes follow.

**Redaction is by role, and ids stay.** Every address becomes its role
(`creator@example.com`, `peer-gmail@example.com`,
`peer-google-nongmail@example.com`, `peer-no-account@example.com`) and every
display name likewise; file, folder and permission ids, and the id token's
`sub`, stay as observed, because a faked id is how a shape drifts, and the
folder is deleted when the spike ends. Tokens — the id token among them —
the client secret and the API key never enter a fixture: a token becomes
`REDACTED`, and the id token's claims are recorded decoded in the README.

**Parallel creates use at least three distinct Google accounts.** Google says
concurrent permission changes on one item are unsupported and only the last
is applied; with two writers one loss is visible, with three the report can
say which one, and the count used is stated.

**Timing is a person with a stopwatch, three runs, not a script.** The number
`T-094`'s copy and ensure step are designed around is how long a Peer waits
after clicking Open; a script timing the API sees nothing of the Drive page.

**Every call is timed, and every refusal is classified by who resolves it.**
The seconds per call are what the three request budgets `D-034` leaves
provisional are checked against:
`VendorAccessService::REQUEST_TIMEOUT_SECONDS` (5, `T-091`) against the
permission calls — one that routinely takes longer would leave every grant
`pending` on the Series page — `ConnectionService::REQUEST_TIMEOUT_SECONDS`
(10, `T-044`) against the token endpoint, `about.get` and the revoke, and
`VendorIdentityService::REQUEST_TIMEOUT_SECONDS` (10, `T-092`) against the
token endpoint. The Playground shows no timing, so the token endpoint is
timed through step 15's refresh, made with `curl` for that reason: the code
exchange in each landing calls the same endpoint. The report names, for
each error body kept, whether Qori retries it alone (`pending`), the creator
must act (`needs_creator`) or the Peer must (`awaiting_identity`), in
`T-091`'s `VendorGrantStatus` words, so `T-094`'s mapping is copied from
observation rather than written from memory.

**The creator's reconnect is exercised in both shapes.** The same account
re-authorising, where `T-091` expects stored ids to keep working and grants
to re-run, and a different account, where it expects the stored folder id to
be unusable and the container re-picked; a spike that only revokes the token
leaves both expectations as inferences.

**The currency actions run on one Episode file, in the order listed**, with
`files.get` read before and after each, so the three states are told apart by
the same fields `T-094`'s item check will read.

**Free Google Drive first, and the task closes on it; the Workspace pass may
finish afterwards** (the owner, 19 September 2026). Workspace admin changes
take up to 24 hours to apply
(https://knowledge.workspace.google.com/admin/drive/manage-external-sharing-for-your-organization),
so the Workspace pass is bounded by the calendar, not by effort. Its results
go in a second dated report under this id, and each `T-094` bullet it answers
is struck then.

**The 600-address cap is not measured** (the owner, 19 September 2026).
Google documents the cap for a single file
(https://support.google.com/drive/answer/2494822); reaching it on a folder
needs 600 distinct grantees, which only a Workspace tenant's user directory
can supply. The report records it as unmeasured, and `T-094` carries a cap
from config that can be changed without a release.

## Preconditions

**Data this task verifies against:** A clean database. The spike never
touches Qori's own database; every row it reads is Google's.

**Equipment:**

- The owner's Google Cloud project, set up as
  `docs/planning/vendor-accounts.md` says under Google Drive, steps 1 to 14,
  less step 13's brand verification, and less step 12's Publish app while
  the pages the decision above names are not live: the Drive API and the
  Picker API enabled; a consent screen set to External that declares
  `https://www.googleapis.com/auth/drive.file`, `openid` and
  `https://www.googleapis.com/auth/userinfo.email` (step 9); the
  local-development client, a Web application whose authorised redirect URIs
  include `https://developers.google.com/oauthplayground` (step 10); the
  Picker's API key (step 11), whose website restrictions admit
  `http://localhost:8000/*` as well as `https://docs.google.com/*` — the
  first is not among step 11's, so the owner adds it; and, in Testing, every
  Google account below listed under Test users (step 8). Its four values
  (step 14) go to whoever runs the spike.
- Four Google-side identities, each in its own browser profile: the creator
  on a personal Gmail; `peer-gmail`; `peer-google-nongmail`, a Google account
  created on a non-Gmail address; `peer-no-account`, a mailbox the tester
  reads that has no Google account. At least one more Google account for the
  parallel run. The owner holds several Google accounts and mailboxes with no
  Google account (19 September 2026); a `useqori.com` address forwarded by
  Cloudflare Email Routing, which needs a rule per address, can become
  `peer-google-nongmail`, and another forwarded address that is never signed
  up stays `peer-no-account`.
- For the Workspace pass: a tenant where the tester is super admin, external
  sharing On at the start, one shared drive, and either a second tenant or a
  separate org unit whose receiving rule accepts only allowlisted domains.
  The edition is recorded, because Business Starter has no trust rules. The
  owner names the tenant and its edition before steps 16 and 17, the only
  steps that wait on it; the edition decides whether rows e, f and g of
  step 17 can run at all.
- Drive for desktop on the creator's machine; an Android phone and an iPhone
  with the Drive app; a stopwatch.
- Content in the creator's My Drive: a folder `Qori spike` holding
  `episode.pdf`, `episode.mp4` (1080p, about 200 MB, so processing is
  observable), `episode.mp3` and a Google Doc; a folder `Elsewhere` holding
  `moved.pdf`; `unshared.pdf` at the root, shared with nobody.

## Scope

**In:**

- The numbered steps under Code, run as written, each answered in the
  report or marked as not run with the reason; the status and the seconds of
  every call in the README index.
- One fixture per observed response, listed under Code, redacted by the
  rule above and indexed in `tests/Fixtures/google/README.md`, which also
  names the publishing status and records the id token's decoded claims.
- The report, `docs/planning/tasks/reports/T-093-YYYY-MM-DD-<owner>.md`,
  on the report template, whose Outcome answers the ten questions in order,
  names the fixture that shows each answer, says who resolves each refusal
  kept, and names the publishing status the spike ran under.
- Carrying the answers into `T-094`: each bullet under its "Before this can
  be ready" that this spike answers struck with the date, the answer and the
  fixture.

**Out:**

- Any code under `app/`, `resources/`, `routes/` or `lang/`; the connect
  step (`T-044`); the integration class, tables and ensure step (`T-091`,
  `T-094`); the Peer's Google sign-in (`T-092`), beyond the one Playground
  sign-in whose response step 2 keeps; Open (`T-089`).
- The `VendorGrantStatus` enum and the mapping from Google's errors to its
  cases: the enum is `T-091`'s and the mapping `T-094`'s; this spike keeps
  the bodies and says who resolves each.
- A folder shared between two Series: the container rule is one dedicated
  folder per Series (`D-025`), so no step here puts one folder under two.
- Creating, configuring or publishing the Cloud project, and brand
  verification: the owner's (`docs/planning/vendor-accounts.md`, Google
  Drive, steps 1 to 14); step 1 only checks them.
- `downloadRestrictions`, `expirationTime` and visitor sharing: downloads are
  not a concern (`D-016`), Qori revokes by itself, and visitor sharing needs
  Google's own email (https://support.google.com/drive/answer/9195194).
- The Dropbox and OneDrive spikes (`T-095`, `T-097`), and revoke on refund
  (`T-103`), which reaches Google through `T-094`'s revoke, tested against
  step 14's fixture.

## Files

| Path                                                                                            | Change | Notes                                                                                                                 |
| ----------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| `tests/Fixtures/google/README.md`                                                               | new    | Index: file, date, call, request, status, seconds, account role; the publishing status; the id token's decoded claims |
| `tests/Fixtures/google/*.json`                                                                  | new    | One per observed response, named under Code                                                                           |
| `tests/Fixtures/google/permissions-delete.txt`                                                  | new    | Status line and headers of the empty 204                                                                              |
| `tests/Fixtures/google/oauth-revoke.txt`                                                        | new    | Status line and headers of the revoke call, and its body if one came                                                  |
| `docs/planning/tasks/reports/T-093-YYYY-MM-DD-<owner>.md`                                       | new    | The report; the ten answers in order                                                                                  |
| `docs/planning/tasks/T-094-google-drive-episodes-from-a-series-folder-shared-with-each-peer.md` | edit   | Strike each bullet answered, with the date, the answer and the fixture                                                |

Flows: none — nothing under `app/` or `routes/` changes; `docs/flows/vendor-access.md` is written with `T-091`'s code, never before it.

## Database

None.

## Code

None under `app/`. A spike's code is the calls it makes, so they are listed
here in order. Every request shape below is from the reference page cited
beside it; every response shape is whatever comes back, kept verbatim in
content, and nothing in `T-044`, `T-092` or `T-094` may name a Google
response field this directory does not show. Every `curl` runs with
`-w '\n%{http_code} %{time_total}\n'`, and the status and the seconds go in
the README index row beside the fixture, so the three request budgets
`D-034` leaves provisional are set from measured calls rather than guessed.

**Setup**

0. **The cited pages, re-read.** Before step 1, whoever runs the spike
   re-reads every Google page this file cites — they were read for the
   blueprint behind `D-016` — and lists in the report each one that no
   longer says what is attributed to it here. The steps still run as
   written: what comes back is the observation.
1. **The project, checked.** The Cloud project, its clients and the key are
   the owner's (`docs/planning/vendor-accounts.md`, Google Drive, steps 1 to
   14), and nothing here creates or publishes them. Check each setting under
   Equipment in the console, the publishing status included, and hand
   anything missing back to the owner before step 2. Record in the report:
   the project number, the client id, the publishing status, and in words
   what the consent screen shows for an unverified app.
2. **Tokens.** In the OAuth 2.0 Playground tick "Use your own OAuth
   credentials" and enter the local-development client's id and secret;
   with the access type Offline, authorise
   `https://www.googleapis.com/auth/drive.file` alone as the creator, and
   exchange the code. Keep the token response as `oauth-token.json` with
   `access_token` and `refresh_token` replaced by `REDACTED`, keeping
   `scope`, `token_type`, `expires_in` and any other field; record whether
   `refresh_token_expires_in` is among them, which Google sets only for
   access granted for a limited time
   (https://developers.google.com/identity/protocols/oauth2/web-server).
   Check `scope`. Granular consent can let a person untick a scope, but
   Google says its screen does not apply to a request for one scope that is
   not a sign-in scope
   (https://developers.google.com/identity/protocols/oauth2/resources/granular-permissions),
   so expect no checkbox. If the screen offers none, the report says so and
   no `oauth-token-scope-declined.json` is kept: `T-044`'s scope-declined
   case uses a response edited by hand from `oauth-token.json`, which
   `T-044` adds with a README row marking it edited, not observed. If it
   offers one, authorise once more with it unticked and keep that response
   as `oauth-token-scope-declined.json`. Then
   `GET https://www.googleapis.com/drive/v3/about?fields=user(permissionId,emailAddress,displayName)`
   (https://developers.google.com/workspace/drive/api/reference/rest/v3/about/get)
   → `about-get.json`, from which `T-044` takes `external_id` and
   `account_name`; record whether `emailAddress` came back, which the User
   resource says may be absent
   (https://developers.google.com/workspace/drive/api/reference/rest/v3/User).
   Last, the Peer's sign-in (`T-092`): in `peer-gmail`'s profile, with the
   access type Online because `T-092` asks for no offline access, authorise
   `openid email` against the same client and exchange the code →
   `oidc-token.json`, with `access_token` and `id_token` replaced by
   `REDACTED`. Decode the id token before redacting it
   (https://developers.google.com/identity/openid-connect/openid-connect) and
   record in the README the values of `sub`, `email` (as its role) and
   `email_verified`, and the names of every other claim it carries, since
   `T-092` also checks `aud`, `exp` and `nonce`.
3. **Content.** Create the folders and files listed under Equipment.

**Pick**

4. **The picker page.** One HTML page in the tester's scratch directory,
   served at `http://localhost:8000` by `php -S localhost:8000`, loading
   `https://apis.google.com/js/api.js` and building
   `new google.picker.PickerBuilder().setAppId(<project number>).setOAuthToken(<token>).setDeveloperKey(<key>).addView(new google.picker.DocsView(google.picker.ViewId.FOLDERS).setSelectFolderEnabled(true).setIncludeFolders(true))`
   (https://developers.google.com/workspace/drive/picker/guides/web-picker;
   `setAppId` takes the Cloud project number, and without it the pick grants
   the token nothing,
   https://developers.google.com/workspace/drive/picker/reference/picker.pickerbuilder.setappid).
   The page signs nobody in: the token is the Playground's, pasted into it.
   The key's website restrictions must admit `http://localhost:8000/*` as
   well as `https://docs.google.com/*`, where the Picker draws its frame
   (web-picker guide above). Pick `Qori spike`; keep the callback's payload,
   the object it receives with `action` `picked`, as
   `picker-folder-picked.json`.
5. **The folder under the token.**
   `GET https://www.googleapis.com/drive/v3/files/{folderId}?fields=id,name,mimeType,parents,trashed,capabilities/canShare,webViewLink,driveId&supportsAllDrives=true`
   (https://developers.google.com/workspace/drive/api/reference/rest/v3/files/get)
   → `files-get-folder.json`; `trashed` is in the mask because `T-094`'s
   container check reads it. A 404 here means the pick granted nothing:
   keep it as `errors-files-get-folder-404-notFound.json` and see Decides.

**The ten questions**

6. **Q1 — does a picked folder accept a permission?**
   `POST https://www.googleapis.com/drive/v3/files/{folderId}/permissions?sendNotificationEmail=false&supportsAllDrives=true&fields=id,type,role,emailAddress,displayName`
   with body `{"type":"user","role":"reader","emailAddress":"<peer-gmail>"}`
   (https://developers.google.com/workspace/drive/api/reference/rest/v3/permissions/create;
   `sendNotificationEmail` defaults to true). Keep
   `permissions-create-folder.json`, or the error as
   `errors-permissions-create-<status>-<reason>.json`. Then
   `GET …/permissions/{permissionId}?fields=*` → `permissions-get.json`, and
   `GET …/files/{folderId}/permissions?fields=*` →
   `permissions-list-folder.json`.
7. **Q2 — does the token see files nobody picked?**
   `GET https://www.googleapis.com/drive/v3/files?q='{folderId}'+in+parents+and+trashed=false&fields=files(id,name,mimeType,parents,trashed)`
   (https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list)
   → `files-list-folder.json`; record which of the four files appear. Then
   `files.get` on `episode.pdf` by the id in the Drive UI's URL, before it is
   picked → `files-get-unpicked.json` or
   `errors-files-get-unpicked-404-notFound.json`. Then pick `episode.pdf`
   through a second view, `new google.picker.DocsView().setParent(folderId)`,
   keeping that callback's payload, a single file picked, as
   `picker-file-picked.json` — `T-094` fills an Episode from its `docs[0]` —
   and
   `GET …/files/{fileId}?fields=id,name,mimeType,parents,trashed,version,md5Checksum,webViewLink,webContentLink,videoMediaMetadata`
   → `files-get-episode-file.json`. Last,
   `GET https://www.googleapis.com/drive/v3/changes/startPageToken`, add a
   file in the Drive UI, `GET …/changes?pageToken=<token>&fields=*`
   (https://developers.google.com/workspace/drive/api/reference/rest/v3/changes/list)
   → `changes-list.json`; record whether the new file is in it.
8. **Q3 — is a repeat grant the same id?** Repeat step 6 for the same
   address → `permissions-create-repeat.json`; record the status and whether
   `id` equals the first. The Permission resource says `id` identifies the
   grantee, not the file
   (https://developers.google.com/workspace/drive/api/reference/rest/v3/permissions),
   so the same id is expected and the status is undocumented. Then make the
   Peer an editor in the Drive UI and create as `reader` once more →
   `permissions-create-repeat-over-writer.json`, with `permissions.get` after
   it to see whether the role was downgraded.
9. **Q4 — do parallel creates lose grants?** Delete every Peer permission.
   Fire one create per distinct account in one burst (`xargs -P` or
   backgrounded `curl`s; the count in the report) → `permissions-create-parallel-1.json`
   … `-N.json`, then `permissions.list` → `permissions-list-after-parallel.json`.
   A grantee missing from the list is the loss Google describes: "only the
   last update is applied"
   (https://developers.google.com/workspace/drive/api/reference/rest/v3/permissions/create).
   Three bursts; one loss in three decides.
10. **Q5 — does the 600 cap apply to a folder?** Not measured (see
    Decisions): the report writes `unmeasured` beside Google's figure for a
    single file, and `T-094` carries its cap from config.
11. **Q6 — how long until a Peer can open it?** As `peer-gmail` in a profile
    signed in to that account only: start the clock at step 6's 200, open the
    Episode file's `webViewLink`, stop when the PDF renders. Delete and
    re-create; three runs, each in seconds. Then the folder's `webViewLink`,
    then "Shared with me". Once more as `peer-google-nongmail`. Then, signed
    in to a different Google account, open the same link: record the page in
    words (expected "You need access",
    https://support.google.com/drive/answer/6211862) and whether appending
    `authuser=<peer email>` lands on the right account — unresearched, so
    the answer is whatever is seen. Then on Android and on iOS: which app
    opened, which account it used, whether `episode.mp4` played or was still
    processing (https://support.google.com/drive/answer/2423694). Then, as
    `peer-gmail` on the web, open `episode.mp3` from the folder in Drive's
    preview and record whether it plays: `T-094` keeps Audio Episodes off
    Google Drive until that has been seen. The seconds from the 200 to the
    render are what decide when `T-094` writes `granted`: a 200 that opens
    at once means API acceptance is usable access; a wait means the row
    stays `pending` until a `permissions.get` or a later re-check confirms
    it, and the report says which.
12. **Q7 — an address with no Google account.** Step 6 for
    `peer-no-account` with `sendNotificationEmail=false` →
    `permissions-create-no-account.json` or
    `errors-permissions-create-<status>-<reason>-no-account.json`. Google's
    help says the person must sign up before a share is possible
    (https://support.google.com/drive/answer/6033939) and its error page is
    silent on the API case
    (https://developers.google.com/workspace/drive/api/guides/handle-errors).
    Then again with `sendNotificationEmail=true`: the status, whether
    Google's email arrived in that mailbox, and what it offered. Then create
    a Google account on that address
    (https://support.google.com/accounts/answer/27441), open the link, read
    `permissions.list`: record whether an earlier grant now opens.
13. **Q8 — the currency actions.** On `episode.pdf` from step 7, in this
    order, `files.get` before and after each with the step 7 field list, and
    `peer-gmail` opening the folder and the file after each. Every row ends
    in one of three states:

    - **Current** — the Peer opens it with no new grant, and the id Qori
      would have stored is unchanged.
    - **Visible, new id** — the Peer opens it in the folder, but it is a
      different file, so an Episode holding the old id is stale.
    - **Blocked** — the Peer sees it, or nothing, and cannot open it.

    | #   | Action                              | How                                                                                 | Expected, from the research                                                                                                                                                                                  | Fixture                                        |
    | --- | ----------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------- |
    | 1   | Add a file                          | Upload `added.pdf` into the folder in the Drive UI                                  | Current: children inherit the folder's permissions (https://developers.google.com/workspace/drive/api/guides/manage-sharing)                                                                                 | `files-get-added.json`                         |
    | 2   | Upload new version                  | `episode.pdf` › Manage versions › Upload new version                                | Current, id kept: inferred from `files.update` editing the same resource (https://developers.google.com/workspace/drive/api/reference/rest/v3/files/update; https://support.google.com/drive/answer/2409045) | `files-get-after-new-version.json`             |
    | 3   | Keep both files                     | Upload a file named `episode.pdf`, choose Keep both files                           | Visible, new id: inferred, not stated by Google                                                                                                                                                              | `files-get-after-keep-both.json`               |
    | 4   | Same-name upload, web               | Upload `episode.pdf` again, accept the default                                      | Help says a revision (https://support.google.com/drive/answer/2424368); community threads say a copy                                                                                                         | `files-get-after-same-name-web.json`           |
    | 5   | Same-name upload, Drive for desktop | Copy `episode.pdf` over the synced folder's copy                                    | Unknown                                                                                                                                                                                                      | `files-get-after-same-name-desktop.json`       |
    | 6   | Move in                             | Move `moved.pdf` from `Elsewhere` into the folder                                   | Current: access re-evaluated against the new parent (manage-sharing, as row 1)                                                                                                                               | `files-get-moved-in.json`                      |
    | 7   | Shortcut                            | Add to the folder a shortcut to `unshared.pdf`                                      | Blocked: a shortcut grants nothing (https://support.google.com/drive/answer/9700156; https://developers.google.com/workspace/drive/api/guides/shortcuts)                                                     | `files-get-shortcut.json`                      |
    | 8   | Limited-access subfolder            | Create `Sub` with `sub.pdf` inside, set `Sub` to Limited access in the share dialog | Blocked; also record whether the token sees `Sub` at all (https://developers.google.com/workspace/drive/api/guides/limited-expansive-access)                                                                 | `files-get-limited-subfolder.json` or an error |
    | 9   | Move out                            | Move `episode.pdf` to `Elsewhere`                                                   | Blocked; `parents` changes                                                                                                                                                                                   | `files-get-moved-out.json`                     |
    | 10  | Trash                               | Trash `added.pdf`                                                                   | Blocked; `trashed` true                                                                                                                                                                                      | `files-get-trashed.json`                       |

    Record per row: the state, the id before and after, and whether
    `files.get` under the token still answered.

14. **Q9 — revoke.**
    `DELETE https://www.googleapis.com/drive/v3/files/{folderId}/permissions/{permissionId}?supportsAllDrives=true`
    (https://developers.google.com/workspace/drive/api/reference/rest/v3/permissions/delete)
    while `peer-gmail` has `episode.mp4` playing. Keep the status line and
    headers as `permissions-delete.txt` (the body is empty); record the
    seconds until a reload shows "You need access" and whether the video
    stopped. Then `permissions.get` on the deleted id →
    `errors-permissions-get-404-notFound.json`, and the delete again →
    `errors-permissions-delete-<status>-<reason>.json`. Then grant
    `peer-gmail` once more, remove them by hand in the Drive share dialog
    rather than through the API, and `permissions.get` the stored id →
    `errors-permissions-get-404-notFound-removed-by-hand.json`, or whatever
    comes back: this is the case `T-091`'s re-check of granted rows
    (`checked_at`) and the read Open makes before trusting a `granted` row
    have to catch, and its body is what `T-094` tests that read against.
15. **Q10 — every other error met, and what recovers each.** First the one
    recoverable failure the review asks every spike to record: with the
    access token expired (`expires_in` from step 2 has passed) or replaced by
    a garbage string, repeat step 6 →
    `errors-permissions-create-401-<reason>.json`
    (https://developers.google.com/workspace/drive/api/guides/handle-errors).
    Refresh the token with `curl`: `POST https://oauth2.googleapis.com/token`
    with `grant_type=refresh_token`, the refresh token, the client id and the
    client secret (https://developers.google.com/identity/protocols/oauth2/web-server)
    → `oauth-refresh.json`, redacted as step 2's token is, recording whether
    a new `refresh_token` came back; repeat step 6 with the new access token
    → the 200. Then revoke the app at
    https://myaccount.google.com/permissions as the creator and refresh the
    same way → `errors-oauth-token-400-invalid_grant.json`
    (https://developers.google.com/identity/protocols/oauth2); as
    `peer-gmail`, open the file again and record whether access already
    granted survives the revoke — the blueprint infers it does. Re-authorise
    as the same creator and, without picking again, run step 5 and step 6
    for a fresh Peer address under the new token →
    `files-get-folder-after-reconnect.json` and
    `permissions-create-after-reconnect.json`, or the errors. Then authorise
    as one of the parallel-run accounts and `files.get` the same folder id →
    `errors-files-get-folder-other-account-<status>-<reason>.json`, expected
    404; this is the "different account" reconnect, where `T-091` marks the
    container for re-pick. Any `sharingRateLimitExceeded`,
    `rateLimitExceeded` or `userRateLimitExceeded` body met at any step, with
    its `Retry-After` header if one came (handle-errors page above) →
    `errors-<call>-<status>-<reason>.json`. A creator who is only an editor:
    have a second account own a folder, share it to the creator as editor
    with "Editors can change permissions and share" off, and pick it;
    `files.get` it with step 5's mask → `files-get-folder-cannot-share.json`,
    expected `capabilities.canShare` false, which `T-094`'s container check
    refuses on; then run step 6 on it → record the body; the blueprint infers
    a refusal and nothing documents one. Last, the revoke `T-044`'s
    disconnect makes:
    `curl -i -X POST -d token=<the creator's refresh token> https://oauth2.googleapis.com/revoke`
    (web-server page above) → `oauth-revoke.txt`, its status line and
    headers, and its body if one came. The report labels every error in this
    step with who resolves it, in `T-091`'s words: `pending` (Qori retries,
    nobody acts), `needs_creator` (reconnect, an admin policy, a plan or a
    cap) or `awaiting_identity` (the Peer's account); the mapping itself is
    written in `T-094`.

**The Workspace pass**

16. **Baseline.** As the Workspace creator with external sharing On, repeat
    step 2 for the creator's token and `about.get` only, then steps 4, 5, 6
    and 11 for `peer-gmail`. Record the edition. A response whose shape
    differs from its free-tier fixture is kept under the same name with
    `-workspace` before the extension; one that matches is recorded as
    matching.
17. **One setting at a time**, each followed by step 6 for a fresh Peer
    address and by `peer-gmail` reopening the file, recording the time from
    the change to the first differing response, up to 24 hours. Restore each
    before the next.

    | #   | Setting                                      | Where in the Admin console                                                                                                         | Expected, from the research                                                                                                                                                                         | Fixture                                                            |
    | --- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
    | a   | External sharing Off                         | Apps › Google Workspace › Drive and Docs › Sharing settings                                                                        | 400 `invalidSharingRequest`, "ACL change not allowed" (https://developers.google.com/workspace/drive/api/guides/handle-errors); the existing Peer loses access (manage-external-sharing page above) | `errors-workspace-sharing-off-400-invalidSharingRequest.json`      |
    | b   | Allowlisted domains, without gmail.com       | Same                                                                                                                               | A refusal; wording undocumented                                                                                                                                                                     | `errors-workspace-allowlist-<status>-<reason>.json`                |
    | c   | Drive SDK off                                | Drive and Docs › Features and Applications                                                                                         | 403 `domainPolicy`, "The domain administrators have disabled Drive apps." (handle-errors; https://knowledge.workspace.google.com/admin/drive/allow-third-party-apps-for-drive-files)                | `errors-workspace-sdk-off-403-domainPolicy.json`                   |
    | d   | Unconfigured third-party apps blocked        | Security › API controls › App access control                                                                                       | `admin_policy_enforced` in the consent redirect's `error` parameter (https://developers.google.com/identity/protocols/oauth2/web-server)                                                            | `errors-workspace-consent-admin_policy_enforced.txt` (the URL)     |
    | e   | Drive Restricted, "not high-risk" box off    | Security › API controls › Google Workspace services › Drive                                                                        | The refresh token is revoked; keep the token endpoint's body (https://knowledge.workspace.google.com/admin/apps/control-which-third-party-and-internal-apps-access-google-workspace-data)           | `errors-workspace-restricted-<status>-<reason>.json`               |
    | f   | Drive Restricted, box on                     | Same                                                                                                                               | Unknown: decides whether `drive.file` counts as not high-risk (the page's example matches it and does not name it)                                                                                  | `permissions-create-workspace-restricted-allowed.json` or an error |
    | g   | Shared drive refusing non-members            | The shared drive's settings; pick a folder in it with `setEnableDrives(true)`                                                      | A refusal; record the creator's role (https://knowledge.workspace.google.com/admin/drive/manage-shared-drives-as-an-admin)                                                                          | `errors-workspace-shared-drive-<status>-<reason>.json`             |
    | h   | Peer tenant accepts only allowlisted domains | The second tenant's receiving setting (https://knowledge.workspace.google.com/admin/security/help-prevent-drive-spam-and-phishing) | Possibly a 200 with no way in: record the create response and what the Peer sees on open                                                                                                            | `permissions-create-peer-tenant-allowlist.json`                    |

**Decides**

- Step 6 succeeding and rows 1, 2 and 6 of step 13 ending **Current** is the
  design `D-016` describes: Google ships on the folder grant, and `T-094` is
  specified on it. Row 1 is also the evidence for the picker copy `T-094`
  carries — that sharing the folder shares everything inside it, Episodes or
  not.
- Step 11's seconds decide when `T-094` writes `granted`, and step 14's
  by-hand removal decides what its re-check of granted rows has to read.
  Step 11's MP3 decides whether `T-094` lets an Audio Episode live on Google
  Drive.
- Every call's seconds decide the three request budgets `D-034` leaves
  provisional.
- Step 2's `about-get.json` decides whether `T-044` can name the account
  from `drive.file` alone. It and step 15's `oauth-refresh.json` and
  `oauth-revoke.txt` are what `T-044`'s identity read, refresh and revoke
  are tested against; step 2's `oidc-token.json` is what `T-092`'s sign-in
  is tested against.
- Step 15 decides what `T-091`'s two reconnect triggers can rely on: whether
  the same account's new token reaches the stored folder without a re-pick,
  and whether a different account's token is refused on it.
- Step 5 or step 6 refused is the kill result. `T-094` is re-drafted on one
  of the two fallbacks the blueprint names — per-file grants with a fan-out
  per new Episode, or the Restricted `drive` scope and Google's security
  assessment — and that choice is the owner's, not this spike's.
- Step 9 losing a grant makes the per-folder lock in `T-091` mandatory
  rather than defensive.
- Step 8's status and id decide which branch of `T-094`'s ensure step the
  repeat-grant test covers.
- Step 12's body decides what `T-092`'s sign-in prerequisite has to promise:
  whether an address without an account is refused loudly or accepted
  silently.
- Step 7 decides whether `T-094`'s scheduled item check can rely on anything
  beyond `files.get` of stored ids.
- Step 17 decides which Workspace refusals `T-044` can detect at connect time
  (c, d, e) and which `T-094` can only report after a failed grant (a, b, g,
  h).

**The fixture set**, every one listed in `README.md`: `oauth-token.json`,
`oauth-token-scope-declined.json` only if step 2's screen offered the
checkbox, `about-get.json`, `oidc-token.json`, `picker-folder-picked.json`,
`files-get-folder.json`, `files-list-folder.json`, `files-get-unpicked.json`
or its 404, `picker-file-picked.json`, `files-get-episode-file.json`,
`changes-list.json`, `permissions-create-folder.json`,
`permissions-get.json`, `permissions-list-folder.json`,
`permissions-create-repeat.json`,
`permissions-create-repeat-over-writer.json`,
`permissions-create-parallel-N.json`, `permissions-list-after-parallel.json`,
`permissions-create-no-account.json` or its error, the ten `files-get-*.json`
of step 13, `permissions-delete.txt`,
`errors-permissions-get-404-notFound.json`,
`errors-permissions-get-404-notFound-removed-by-hand.json` or what came back,
`errors-permissions-create-401-<reason>.json`, `oauth-refresh.json`,
`errors-oauth-token-400-invalid_grant.json`,
`files-get-folder-after-reconnect.json`,
`permissions-create-after-reconnect.json`,
`errors-files-get-folder-other-account-<status>-<reason>.json`,
`files-get-folder-cannot-share.json`, `oauth-revoke.txt`, and every
`errors-*.json` met.

## Copy

None.

## Routes

None.

## Tests

None. A spike commits no test: its output is the fixtures, which the tests
of `T-044`, `T-092` and `T-094` load into `Http::fake()`, each stating its
own count.

## Acceptance

- [x] Every numbered step run, or marked in the report as not run with the
      reason
- [x] One fixture per response in the set above, verbatim in content with
      the formatter's whitespace, redacted by role, indexed in
      `tests/Fixtures/google/README.md` with date, call, request, status,
      seconds and account role; the README names the publishing status and
      records the id token's `sub`, `email` and `email_verified`, decoded
- [x] The report's Outcome answers Q1 to Q10 in order, naming the fixture
      that shows each answer and, for every error kept, who resolves it in
      `T-091`'s words; step 13's table filled with a state per row; step 17's
      table filled, or dated as pending with the time of each setting change
- [x] The report names the publishing status the spike ran under, and cites
      Google's documentation for how long a refresh token lasts in production
- [x] Every "Found, not fixed" bullet in the report ends in a disposition
- [x] `T-094` carries the answers: each bullet under its "Before this can be
      ready" that this spike answers struck with the date, the answer and the
      fixture
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Added during execution

| Path                                                                                     | Change | Notes                                                                                                                                   |
| ---------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/planning/tasks/T-044-nothing-can-create-a-connection.md`                           | edit   | The report's dispositions: the bodies and seconds its open bullets waited on, and the disconnect and reconnect findings as a new bullet |
| `docs/planning/tasks/T-091-every-peer-with-access-is-granted-on-the-series-container.md` | edit   | The report's dispositions: the observed seconds for its provisional numbers, and its reconnect and re-check answers                     |
| `docs/planning/tasks/T-149-one-dialog-adds-files-from-any-connected-storage.md`          | new    | The draft the report's "→ draft T-149" names: one dialog across storage providers, which the owner asked for on 19 September 2026       |

## Re-scope log

None.

## Notes

The estimate is `S` for the free-tier pass, steps 0 to 15. The Workspace
pass is bounded by Google's propagation window, not by effort, and the
Decisions let it trail.

`lang/en/groups.php:68` still promises "Connecting Dropbox or Google Drive
is coming"; `T-044` replaces it, not this spike.

`T-094` has been a full draft since 16 September 2026, and its "Before this
can be ready" already carries this spike's questions, the step 5 mask and
the MP3 among them, so the Notes line this file once allowed for a bare
template is gone.

`docs/planning/tasks/reports/README.md` names the report
`T-093-YYYY-MM-DD-<owner>.md` and, from 15 September 2026, refuses a
finding without a disposition; most of this spike's findings will end
`→ T-094`.

The blueprint's own research disagreed with itself on the folder: the tier
research advised picking files only because no primary source covers a
picked folder's children, and the priorities research designed the folder
grant because Google applies inheritance to the Peer whatever Qori can see.
Steps 6 and 7 are the two halves of that disagreement, and both are answered
before `T-094` is made `ready`.
