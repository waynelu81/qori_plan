---
id: T-095
title: Spike: Dropbox viewers on a shared folder across plans
stream: storage
status: draft
owner: unassigned
estimate: S
depends: none
blocks: T-096
---

# T-095 — Spike: Dropbox viewers on a shared folder across plans

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016` and the owner's BYO blueprint, and reviewed the same day against the
> developer's review of the plan that day. Reworked on 21 September 2026 on
> `D-042`: nothing is bought to run it, step 0 is the cheap gate that decides
> whether the rest is worth running, and the Equipment list is free
> provisioning throughout.

## Why

`D-016` grants Dropbox access on a shared folder: `sharing/share_folder` once
per Series, then `sharing/add_folder_member` once per Peer as a viewer with
`quiet: true`. Nobody at Qori has seen one of those responses. The
repository's only Dropbox call is `files/get_temporary_link`
(`app/Integrations/Dropbox/DropboxStorage.php:52`), the suite fakes its body
inline (`tests/Feature/Storage/PlaybackTest.php:109`), and `tests/Fixtures/`
holds `planning/` and `reachability/` and nothing from any vendor.
`PROCESS.md` says a spec that names a vendor payload cites an observed
response or a committed fixture, so `T-096` cannot be `ready` until this runs.

Three of the questions change `T-096`'s design, not its wording. The Stone
spec's `insufficient_plan` error on `add_folder_member` says adding a
read-only member needs a Pro or Business plan, while Dropbox Help says every
user can set "can view" — if the spec is right, a Basic creator cannot grant
at all. A joined shared folder counts its whole size against each member's
own storage, so a Basic Peer with 2 GB cannot join a bigger folder — unless an
invitee can view through the folder's `preview_url` without joining, which no
Dropbox page says either way. And a team account's default sharing setting
refuses everyone outside the team. Afterwards, each of these is a fixture
under `tests/Fixtures/dropbox/` and a dated answer struck into `T-096`.

**The contradiction is real, and both primary sources say so in their own
words** (read 21 September 2026, and written down here so the next reader
does not have to rediscover that the question is open). Dropbox's API
contract,
[`sharing_folders.stone`](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/sharing_folders.stone),
gives `insufficient_plan` in the `PermissionDeniedReason` union and says of
`add_folder_member`:

> The current user's account doesn't support this action. An example of this
> is when adding a read-only member. This action can only be performed by
> users that have upgraded to a Pro or Business plan.

and of `update_folder_member`:

> The current user's account doesn't support this action. An example of this
> is when downgrading a member from editor to viewer. This action can only be
> performed by users that have upgraded to a Pro or Business plan.

The reason's `InsufficientPlan` struct carries two fields Qori would have to
decide what to do with: a `message`, described in the spec as "A message to
tell the user to upgrade in order to support expected action", and a nullable
`upsell_url`. Against that,
[set-file-folder-permissions](https://help.dropbox.com/share/set-file-folder-permissions)
and the [shared-folder FAQ](https://help.dropbox.com/share/shared-folder-faq)
say that every account type, Basic included, can share a folder and set a
member to "can view", and that a viewer may view, download, share and comment
but not add, edit or delete. The Stone spec is the API contract; the Help
pages describe the web UI. Either could be stale, or the two could be
describing different paths, since nothing obliges dropbox.com's sharing panel
and `sharing/add_folder_member` to enforce the same rule. **Nothing published
settles it — only a call does**, which is why step 0 exists and runs before
anything else is provisioned or observed.

**The Peer-side trap is a separate question and survives either answer to
that one.** A joined shared folder counts its whole size against each
member's own storage, so a Basic Peer with 2 GB cannot join a folder larger
than their free space, and whether an invitee can view through the folder's
`preview_url` without joining is unanswered by any Dropbox page. No choice
about the _creator's_ plan fixes that: a Plus or Business creator's folder
still lands on the Peer's own quota the moment the Peer joins it. Rows 5 and
6 of the answer table are where it is settled, step 0 does not touch it, and
a spike that stops at step 0 leaves it open.

The same fixtures are what let `T-096` say, in `T-091`'s vocabulary, when a
Dropbox grant is `granted` — after Join, or on the invitation alone if an
invitee can view — and which failure is the Peer's to resolve, the creator's,
or a retry nobody has to act on.

## Decisions taken to make this specifiable

**Nothing is bought to run this spike, and the free-path question is asked
first** (`D-042`, 21 September 2026). Every account under Equipment is free,
paid provisioning is a last resort the owner takes rather than the spike, and
step 0 is the smallest set of calls that can say whether a free path exists
at all. Three consequences run through the rest of the file. The Dropbox for
teams trial is replaced by the **free Dropbox Business Development Account**,
granted by request, which is asked for on day one because the lead time is
unpublished and which step 0 does not wait for. No Plus account is
provisioned, so under step 0's outcome A — a Basic creator _can_ add a viewer
— every step that named `creator-plus` as the working creator runs on
`creator-basic` instead, which outcome A has just shown can do what those
steps need; `creator-plus` is then wanted only for rows 2, 17 and 19, the
three answers that are about the Plus tier itself, and whether one is
provisioned for them is the owner's. And under outcome B the spike stops,
because `D-042` puts an integration with no free working path back in front
of the owner to re-approach or drop, and the remaining twenty-three questions
are not worth a day each on a path Qori may never build.

**The spike calls the API from a shell and commits nothing under `app/`.**
What `T-096` needs is observed bodies; a class written before them would be
written twice. `DropboxStorage` is left as it is.

**One fixture per call and case, the raw body, named
`<namespace>/<route>.<case>.<status>.json`** (provisional — see below).
`Http::fake()` needs a body and a status, and no vendor fixture convention
exists yet. `T-093` and `T-097` both name flat files under the vendor
directory and keep the status in the README row; whichever of the three
spikes lands first sets the shape, and the others follow it (a wording
change, renaming the paths under Files and Code).

**Redaction is a fixed map, not judgement.** Emails become the role names
below at `example.test`; `display_name` becomes the role name; `account_id`
and `team_member_id` keep their `dbid:`/`dbmid:` prefix and get a stable
placeholder; tokens become `REDACTED`. Everything else — every `.tag`,
`error_summary`, `shared_folder_id`, file `id`, `rev`, `preview_url` (with
the account-specific segment marked) — stays verbatim. The map lives in the
fixture README as placeholder → role, never placeholder → real value. Every
README row carries the date, the account role, the status and the seconds
the call took.

**Grant by email in every step but one.** `T-096` grants by `dropbox_id`,
the `account_id` that `T-092` stores as the Peer's `subject`, but the email
form is what produces the "invitee, not member" case and the "account created
later" case, and the `dropbox_id` form is what produces
`unverified_dropbox_id`. Both shapes are needed, so both are observed.

**Peer tokens are full-scope for the diagnostic steps only.** Reading
`users/get_space_usage`, `sharing/list_mountable_folders` and
`sharing/mount_folder` as the Peer needs more than `openid email`. `T-092`'s
own shape is observed separately, by one `openid email` round trip, and the
final walkthrough (step 18) uses no Peer token at all and a creator token
holding only the scopes `T-096` will request — so a step the diagnostic token
papered over cannot hide.

**`granted` is evidence the Peer can open the folder now, never the 200 on
`add_folder_member`.** The developer review asks for API acceptance and usable
access to be told apart, and `T-091` makes every provider task say when its
grant is `granted`. So the spike records the one creator-token call that
tells an invitee from a member — `sharing/list_folder_members`, its `users`
and `invitees` lists — before and after Join and after removal, since that is
what `T-096`'s `checkGrant()` reads on Open and from the re-check of
`granted` rows (`checked_at`). Every failure met is written beside the
`VendorGrantStatus` it maps to and who resolves it; the mapping table under
Code is a candidate, and `T-096` states the final one from the fixtures.

**Every call is timed.** The `curl` helpers append the wall time, and a
stopwatch runs from the grant's 200 to the Peer's first open. The seconds are
what `VendorAccessService::REQUEST_TIMEOUT_SECONDS` (`T-091`, provisional 5)
is checked against, and `share_folder`'s asynchronous form is the case
`T-096`'s ensure step has to leave `pending`.

**The reconciliation triggers are observed as facts, not designed here.**
`T-091` re-runs grants when the creator reconnects the same account, marks
containers for a new pick when a different account is connected, and re-grants
when a container is replaced. What the vendor does in each case is a fixture:
a revoked token re-linked for the same account still reaches the same
`shared_folder_id`; a different account's token reading that id; the folder
renamed by the creator. The rename is the one the Dropbox research left open.

**View-without-Join is tested on the Peer who cannot Join.** It is the
decisive question: if a Peer with too little free space can still open files
through the folder's `preview_url`, the storage and Join bullets leave the
tier copy and a "cannot join" path is never needed.

**The invite-cap step runs last, on the Basic throwaway, and never on the
Plus account.** Reaching it suspends that account's sharing for up to
24 hours ([banned-links](https://help.dropbox.com/share/banned-links)), which
would stall every other step.

**The team tier is tested at its default.** "Members only" is the failure
`T-096`'s tier copy has to describe, so it is observed before the setting is
changed, then again after.

**`sharing/get_shared_link_metadata` is recorded only if `preview_url` turns
out to be a shared link.** Qori asks for no public share link today
(`DropboxStorage.php:21-22`) and `D-016` grants per Peer instead; the route
is in the brief as "or whatever Open needs", and what Open needs is decided by
what `preview_url` is.

**Long-video playback is a release check, not an optional observation.** The
review asks for it wherever Dropbox video is offered, and the tier copy will
state the streaming limit. It runs in the background from step 9 and costs no
extra step.

**Answers go into `T-096`, not `decisions.md`.** A spike learns facts about
the vendor; `T-096`'s "Before this can be ready" is where they are read. The
one choice the facts may leave the owner — what to do for a Peer who cannot
join — stays a bullet there, and the report's finding ends `→ T-096`. If the
facts mean Dropbox needs per-file grants, that is a change to `T-091`'s grant
model (one row per Access and container) and is written as a bullet for
`T-091`'s owner, never hidden in `T-096`'s connector.

## Preconditions

**Data this task verifies against:** nothing in Qori's database. Everything
is in Dropbox: a folder `/Qori spike` in each creator account holding
`episode-1.pdf` (about 1 MB) and `episode-2.mp4` (about 600 MB and longer than
30 minutes, for step 20); one file outside it, `/episode-4.pdf`, for the move
step; and to hand, `episode-3.pdf`, `episode-5.pdf` and a changed
`episode-1.pdf` for the currency and walkthrough steps.

**Step 0 needs far less than that, and gathering the rest before it has
answered is what `D-042` forbids:** one folder `/Qori spike` in
`creator-basic`'s account holding one small `episode-1.pdf`, both made in the
browser, so the gate needs no upload call and no `files.content.write`.
`episode-2.mp4` and every other file above is produced only once step 0 has
returned outcome A.

**Equipment.** ~~(provisional — the paid accounts are the owner's to approve,
see below)~~ **Rewritten 21 September 2026 on `D-042`: nothing here is bought.**
Both accounts this task once asked to pay for have a free route — the teams
trial becomes the free Business Development Account, and the Plus account
becomes Dropbox's own 30-day trial, cancelled before it bills — so the whole
roster is free and the question of whose card it goes on does not arise
unless step 0 answers that Basic cannot grant at all.

- A Dropbox app in the App Console: scoped, **Full Dropbox** access (an app
  folder cannot be shared — `SharePathError` in
  [sharing_folders.stone](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/sharing_folders.stone)),
  permissions `account_info.read`, `files.metadata.read`,
  `files.content.write` (the spike's own uploads; `T-096` does not need it),
  `sharing.read`, `sharing.write`, plus `openid` and `email`. The app itself
  costs nothing, and
  [developer support](https://www.dropbox.com/developers/support) states that
  any type of Dropbox account, free or paid, can use it — so every free
  account below can link to it. Development mode is enough:
  ~~the [developer guide](https://www.dropbox.com/developers/reference/developer-guide)
  caps a development app at 500 linked users and freezes new links two weeks
  after the 50th~~ **Corrected 21 September 2026 against
  [developer support](https://www.dropbox.com/developers/support):** what
  that page says is "Once your app links 50 Dropbox users, you will have two
  weeks to apply for and receive production status approval", which is a
  deadline to obtain approval rather than a freeze on new links; the 500
  figure is the developer guide's separate cap. This spike links seven
  accounts at its fullest and step 0 links one, so neither number is
  approached. The report records what the console says about applying for
  production, since that lead time gates `T-096`'s launch
  (`release-prerequisites.md:20`).
- Accounts, each on its own mailbox the spiker can read. All are free, and
  what the first draft asked for is struck below with its answer (`D-042`,
  21 September 2026). **Only `creator-basic` is created before step 0 has
  answered**; the rest are provisioned after it, which costs nothing but
  time and keeps the gate first.
    - `creator-basic` — Basic, verified, free. **Step 0's account.** With one
      invitable address it is everything step 0 needs, and the address does
      not have to hold a Dropbox account for the call to be answered.
    - `creator-plus` — Plus or Professional, on its **30-day free trial**,
      which costs nothing and is what `D-042` asks for before anything is
      bought. Dropbox offers the trial on Plus and Professional at
      [dropbox.com/plans](https://www.dropbox.com/plans), it gives full
      access to the paid features for the 30 days, and it can be
      [cancelled before billing](https://help.dropbox.com/plans/cancel-free-trial)
      from Manage account. **Put the cancellation in a calendar the day it
      starts** — an uncancelled trial is the purchase `D-042` says not to
      make, arriving by inattention. Not provisioned before step 0: if step 0
      answers that Basic can add a viewer, the working-creator steps run on
      `creator-basic` and the trial is wanted only for rows 2, 17 and 19,
      the Plus tier itself. One caveat the file already knew and which
      survives: **a trial gets Basic's sharing bandwidth**, per
      [banned-links](https://help.dropbox.com/share/banned-links) — that is a
      bandwidth cap, not a permissions cap, so it does not touch what
      `add_folder_member` answers, and it does bear on row 19's streaming
      limit, which should be recorded as measured on a trial rather than on
      a settled paid account.
    - `creator-team` — admin and member of a **free Dropbox Business
      Development Account**, ~~a Dropbox for teams trial~~, requested through
      [developer support](https://www.dropbox.com/developers/support)'s
      [form](https://docs.google.com/forms/d/e/1FAIpQLSfkzPmp9srHG9jwE3Uc0bFOwknN-rrLQWr1mf_3FGl86ydCiQ/viewform?entry.1304485640=Developer):
      "Development accounts are granted on a by-request basis and are
      contingent on additional terms and conditions outlined in the request
      form." It costs nothing and covers every `creator-team` scenario this
      task has — the team's outside-sharing default and the team folder
      itself — so "Who can be added to files and folders" is still left at
      its default. Two things follow. The grant is by request and the lead
      time is unpublished, so the form goes in on day one even though step 0
      does not wait for it. And **the form is where to ask whether the
      account carries Business-tier sharing behaviour**, because the Stone
      spec's sentence names Pro _or Business_ and a yes would make this a
      free observation of a working `add_folder_member`; until it answers,
      assume neither way.
    - `creator-unverified` — a fresh free Basic account whose email is never
      verified; also the unverified Peer.
    - `peer-roomy` — free Basic, verified, at least 1 GB free.
    - `peer-small` — free Basic, verified, filled so that free space is under
      the folder's size.
    - `peer-none` — an address with no Dropbox account until step 13.
- A domain with plus-addressing or a catch-all, for the invite loop's
  addresses (`spike+001@…`).
- A browser with a fresh profile per Peer, a Dropbox desktop client on one
  machine for the drag-replace check, a stopwatch, and `curl` and `jq`.

## Scope

**In:**

- **Step 0 first and on its own** (`D-042`): the one `add_folder_member` call
  that says whether a free Basic creator can add a viewer, run before any
  other account is created, any other file uploaded or any other fixture
  gathered. If it answers that a Basic creator cannot, the spike stops there
  and the report is the whole deliverable.
- Every call in the Code section, run as the account named, with each
  response body committed as a fixture, its status in the file name and its
  seconds in the README row.
- Every error tag met, especially `insufficient_plan`, `email_unverified`,
  `rate_limit`, `cant_share_outside_team`, `team_folder`,
  `inside_shared_folder`, `too_many_pending_invites`,
  `bad_member/unverified_dropbox_id`, `insufficient_quota`,
  `invalid_access_token` and a `429`. `too_many_members` fires at the
  folder's member cap, which real accounts cannot reach in a spike; it is
  recorded only if met, and the report says so.
- The creator-token evidence of Join and of removal, and each failure written
  beside the `VendorGrantStatus` it maps to and who resolves it.
- The Peer journey walked once more under exactly the permissions `T-096`
  will request: first access, later content, a repeated grant and one
  recoverable failure, each timed.
- The dated report, with the answer table below, and each answered bullet in
  `T-096`'s "Before this can be ready" struck with the date and the answer.
- The web URL shape a member opens a file at, for `T-096`'s Open.

**Out:**

- Any code under `app/`, any `Http::fake()` test, any lang key. The fixtures
  are `T-096`'s inputs; the Dropbox tier copy and Open-page copy are
  `T-096`'s (`T-044` binds Google alone); the Open route is `T-089`'s.
- The Chooser, per-file grants as a design (one `add_file_member` call is
  made, for the quiet-email question and the cap, and nothing more), shared
  links, and the Peer sign-in flow (`T-092`).
- The grant model, the ensure step, the states, the retry rule, the re-check
  cadence for `granted` rows and `qori:access:reconcile` (`T-091`, scheduled
  every few minutes, provisional); delayed payments and refunds (`T-102`,
  `T-103`), which come before any paid Series uses Dropbox. The spike measures
  what those numbers have to survive; it does not choose them.
- Buying anything (`D-042`). No Dropbox subscription, trial or seat is
  purchased to run this spike, and a step that cannot be observed on a free
  account is "not observed" with that reason rather than a request for a
  card. The only exception is an account the owner has already decided to
  provide after reading step 0's answer.
- Any decision. A fact that leaves a choice is written as a bullet for the
  owner in `T-096` — or for `T-091`'s owner where it changes the grant model
  — not taken here.

## Files

| Path                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Change | Notes                                                                                                 |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------- |
| `tests/Fixtures/dropbox/README.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | new    | Date, app, account roster, redaction map; per file: status, seconds, role, and the gap list           |
| `tests/Fixtures/dropbox/oauth2/token.offline.200.json`, `tests/Fixtures/dropbox/oauth2/token.offline.relinked.200.json`, `tests/Fixtures/dropbox/oauth2/token.openid.200.json`, `tests/Fixtures/dropbox/oauth2/token.openid.claims.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | new    | Tokens `REDACTED`; `relinked` is step 18's; the claims file is the decoded `id_token` payload         |
| `tests/Fixtures/dropbox/users/get_current_account.basic.200.json`, `tests/Fixtures/dropbox/users/get_current_account.plus.200.json`, `tests/Fixtures/dropbox/users/get_current_account.team.200.json`, `tests/Fixtures/dropbox/users/get_space_usage.before_join.200.json`, `tests/Fixtures/dropbox/users/get_space_usage.after_join.200.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | new    | One per tier; the two space files are `peer-roomy`                                                    |
| `tests/Fixtures/dropbox/files/upload.add.200.json`, `tests/Fixtures/dropbox/files/upload.overwrite.200.json`, `tests/Fixtures/dropbox/files/move_v2.200.json`, `tests/Fixtures/dropbox/files/list_folder.200.json`, `tests/Fixtures/dropbox/files/list_folder_continue.200.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | new    | The currency steps                                                                                    |
| `tests/Fixtures/dropbox/sharing/share_folder.complete.200.json`, `tests/Fixtures/dropbox/sharing/share_folder.async_job_id.200.json`, `tests/Fixtures/dropbox/sharing/check_share_job_status.complete.200.json`, `tests/Fixtures/dropbox/sharing/share_folder.email_unverified.<status>.json`, `tests/Fixtures/dropbox/sharing/share_folder.team_folder_path.<status>.json`, `tests/Fixtures/dropbox/sharing/share_folder.inside_shared_folder.<status>.json`, `tests/Fixtures/dropbox/sharing/list_folders.team.200.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | new    | `async_job_id` only if Dropbox returns it; `<status>` is what was observed                            |
| `tests/Fixtures/dropbox/sharing/add_folder_member.success.200.json`, `tests/Fixtures/dropbox/sharing/add_folder_member.insufficient_plan.<status>.json`, `tests/Fixtures/dropbox/sharing/add_folder_member.cant_share_outside_team.<status>.json`, `tests/Fixtures/dropbox/sharing/add_folder_member.team_folder.<status>.json`, `tests/Fixtures/dropbox/sharing/add_folder_member.bad_member.unverified_dropbox_id.<status>.json`, `tests/Fixtures/dropbox/sharing/add_folder_member.already_member.<status>.json`, `tests/Fixtures/dropbox/sharing/add_folder_member.already_invitee.<status>.json`, `tests/Fixtures/dropbox/sharing/add_folder_member.invalid_access_token.<status>.json`, `tests/Fixtures/dropbox/sharing/add_folder_member.rate_limit.<status>.json`, `tests/Fixtures/dropbox/sharing/add_folder_member.too_many_pending_invites.<status>.json`, `tests/Fixtures/dropbox/sharing/add_folder_member.oversize_members_arg.<status>.json`, `tests/Fixtures/dropbox/sharing/add_folder_member.too_many_members.<status>.json`, `tests/Fixtures/dropbox/sharing/too_many_requests.429.json` | new    | Each error file exists only if that error was met; the README lists the gap                           |
| `tests/Fixtures/dropbox/sharing/get_folder_metadata.creator.200.json`, `tests/Fixtures/dropbox/sharing/get_folder_metadata.peer_invited.<status>.json`, `tests/Fixtures/dropbox/sharing/get_folder_metadata.peer_joined.200.json`, `tests/Fixtures/dropbox/sharing/get_folder_metadata.renamed.200.json`, `tests/Fixtures/dropbox/sharing/get_folder_metadata.other_account.<status>.json`, `tests/Fixtures/dropbox/sharing/get_file_metadata.creator.200.json`, `tests/Fixtures/dropbox/sharing/get_file_metadata.peer_invited.<status>.json`, `tests/Fixtures/dropbox/sharing/get_file_metadata.peer_joined.200.json`, `tests/Fixtures/dropbox/sharing/list_folder_members.200.json`, `tests/Fixtures/dropbox/sharing/list_folder_members.after_revoke.200.json`, `tests/Fixtures/dropbox/sharing/list_mountable_folders.peer_invited.200.json`, `tests/Fixtures/dropbox/sharing/mount_folder.success.200.json`, `tests/Fixtures/dropbox/sharing/mount_folder.insufficient_quota.<status>.json`                                                                                                           | new    | What Open, Join, removal and the three reconciliation cases look like from each side                  |
| `tests/Fixtures/dropbox/sharing/remove_folder_member.200.json`, `tests/Fixtures/dropbox/sharing/check_remove_member_job_status.complete.200.json`, `tests/Fixtures/dropbox/sharing/add_file_member.success.200.json`, `tests/Fixtures/dropbox/sharing/get_shared_link_metadata.200.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | new    | The last only if `preview_url` is a shared link                                                       |
| `docs/planning/tasks/reports/T-095-YYYY-MM-DD-<owner>.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | new    | The answer table and the states table, per `reports/README.md`                                        |
| `docs/planning/tasks/T-096-dropbox-episodes-from-a-shared-folder-each-peer-joins.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | edit   | Strike each answered bullet with the date; a Notes line naming the report while it is a bare template |

Flows: none — nothing under `app/` changes; `T-091` writes
`docs/flows/vendor-access.md` and `T-096` edits it.

## Database

None.

## Code

No PHP. The literal calls, so two people running the spike make the same
ones. Argument names are the Stone spec's
([sharing_folders.stone](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/sharing_folders.stone),
[sharing_files.stone](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/sharing_files.stone),
[files.stone](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/files.stone),
[users.stone](https://raw.githubusercontent.com/dropbox/dropbox-api-spec/master/users.stone));
**no response field named below is observed until its fixture exists**, and
the HTTP status and body around an error's `.tag` are what the fixture
records, not what this task states.

```bash
API=https://api.dropboxapi.com/2
# $T is the token of the account each step names. -i keeps the status line
# and headers (Retry-After) in the capture; -w appends the wall time, which
# goes in the README row beside the fixture. The fixture is the body alone.
dbx() { curl -sS -i -w '\ntime_total=%{time_total}\n' -X POST "$API/$1" -H "Authorization: Bearer $T" -H 'Content-Type: application/json' -d "$2"; }
void() { curl -sS -i -w '\ntime_total=%{time_total}\n' -X POST "$API/$1" -H "Authorization: Bearer $T"; }
```

0. **The free-path gate, `creator-basic` alone, before anything else**
   (`D-042`). Four calls answer the question the rest of the spike hangs
   on, and no other account is created, no file uploaded and no other
   fixture gathered until they have. The account is a free Basic one and
   the folder is `/Qori spike` holding one small `episode-1.pdf`, both made
   in the browser.
    - (a) Step 1's authorize-and-exchange as `creator-basic`, with
      `scope=account_info.read+sharing.read+sharing.write` — step 1's list
      without the two `files.*` scopes, which none of these four calls needs
      → `oauth2/token.offline.200.json`.
    - (b) `void users/get_current_account` →
      `users/get_current_account.basic.200.json`, so the tier the answer
      belongs to is on the record rather than assumed.
    - (c) `dbx sharing/share_folder '{"path":"/Qori spike"}'` →
      `share_folder.complete.200.json`, for the `shared_folder_id`. If it
      answers asynchronously, poll `sharing/check_share_job_status` as step 4
      does; sharing is not the question here.
    - (d) `dbx sharing/add_folder_member '{"shared_folder_id":"…","members":[{"member":{".tag":"email","email":"peer-roomy@example.test"},"access_level":"viewer"}],"quiet":true}'`
      — one viewer, one call. The address need not hold a Dropbox account
      for the answer to come back.

    **Outcome A — a 200.** → `add_folder_member.success.200.json`, the first
    fixture. The Help pages are right, the Stone spec's Pro-or-Business
    sentence does not bind this route on a Basic account, and **no paid
    Dropbox account is needed to run this spike**. Steps 1 to 20 then run as
    written, with three adjustments: steps 1, 2, 4 and 5 are already done
    for `creator-basic` and are not repeated, their fixtures being step 0's;
    step 3 adds `episode-2.mp4` to the folder step 0 already shared, which
    step 20 needs; and every step that names `creator-plus` as the working
    creator runs on `creator-basic`, per the first decision above. The
    stopwatch step 5 starts at the working creator's 200 therefore starts at
    (d) here, and step 9 stops it.

    **Outcome B — `insufficient_plan`.** Record the HTTP status, the whole
    body, the `message` and whether `upsell_url` is present →
    `add_folder_member.insufficient_plan.<status>.json`. **The spike stops
    here and reports.** Under `D-042` an integration with no free working
    path goes back to the owner, who re-approaches it or drops it, and the
    twenty-three remaining questions are not worth answering about a path
    Qori may never build. The report gives row 1 as observed with its
    fixture, every other row as "not observed — the spike stopped at
    step 0", and one bullet for the owner.

    **What outcome B means for the product, and what it does not.** It does
    not mean Dropbox stops being offered. `D-018` is unchanged and `D-042`
    says so in as many words: every tier a creator brings is offered with
    its limits stated on screen, and none is refused — `D-042` narrows what
    Qori _spends_, not what Qori offers. So the question outcome B hands
    `T-096` is **what a Basic creator is told, and when**: at the
    connection, at the picker, or at the failed grant. Nor does outcome B
    mean an account has to be bought to carry on, because the free Business
    Development Account under Equipment is a Business-tier account and the
    Stone spec's sentence names Pro _or Business_ — so a free observation of
    a working `add_folder_member` may already be in hand, which is one of
    the things the request form is asked. Which of those the owner takes —
    the development account, a paid personal tier, or dropping Dropbox — is
    theirs, and this spike names the choice without settling it. Resuming on
    the development account is a fresh go-ahead from the owner, not a step
    the spike takes on its own.

1. **Tokens, each account.** Open
   `https://www.dropbox.com/oauth2/authorize?client_id=$DBX_APP_KEY&response_type=code&token_access_type=offline&scope=account_info.read+files.metadata.read+files.content.write+sharing.read+sharing.write`
   signed in as the account; with no `redirect_uri` the code is shown on
   screen ([oauth-guide](https://developers.dropbox.com/oauth-guide)). Then
   `curl -sS -X POST https://api.dropboxapi.com/oauth2/token -d code=… -d grant_type=authorization_code -d client_id=$DBX_APP_KEY -d client_secret=$DBX_APP_SECRET`
   → `oauth2/token.offline.200.json`. Record `expires_in` and whether a
   `refresh_token` is present.
2. **Tier, each creator.** `void users/get_current_account` →
   `users/get_current_account.{basic,plus,team}.200.json`. Record
   `account_type` per tier and whether it tells Plus from Professional, since
   `T-096`'s tier cases could otherwise be checked against it.
3. **Files, each creator.** `curl -sS -i -X POST https://content.dropboxapi.com/2/files/upload -H "Authorization: Bearer $T" -H 'Dropbox-API-Arg: {"path":"/Qori spike/episode-1.pdf","mode":"add"}' -H 'Content-Type: application/octet-stream' --data-binary @episode-1.pdf`
   → `files/upload.add.200.json`; the same for `episode-2.mp4` and
   `/episode-4.pdf`. Record each file's `id` and `rev`.
4. **Share, each creator.** `dbx sharing/share_folder '{"path":"/Qori spike"}'`
   → `share_folder.complete.200.json`, or `share_folder.async_job_id.200.json`
   and then `dbx sharing/check_share_job_status '{"async_job_id":"…"}'` until
   `complete`. Record `shared_folder_id` and `preview_url`, and the seconds to
   `complete` when it was asynchronous. Then, as the creator,
   `dbx sharing/get_folder_metadata '{"shared_folder_id":"…"}'` and
   `dbx sharing/get_file_metadata '{"file":"id:…"}'` →
   `get_folder_metadata.creator.200.json` and
   `get_file_metadata.creator.200.json`, the pair steps 7 and 9 compare the
   Peer's against. As `creator-team`, first on the team
   folder's own path → `share_folder.team_folder_path.<status>.json` (record
   whatever `ShareFolderError` comes back; the Stone spec lists `team_folder`
   under `add_folder_member`'s error rather than this route's, so the fixture
   is named for the path, not for a tag), then on a subfolder inside it. As
   `creator-plus`, once more on `/Qori spike/nested`, a subfolder of the
   folder just shared → `share_folder.inside_shared_folder.<status>.json`:
   the vendor's own nesting rule, which `T-096`'s picker states beside
   `T-091`'s one-folder-per-Series rule.
5. **Grant, each creator, `peer-roomy` by email.**
   `dbx sharing/add_folder_member '{"shared_folder_id":"…","members":[{"member":{".tag":"email","email":"peer-roomy@example.test"},"access_level":"viewer"}],"quiet":true}'`
   → `add_folder_member.success.200.json`, or the error met. **This is the
   Basic-versus-Plus question**: record the outcome per creator, and start
   the stopwatch at `creator-plus`'s 200; it stops at step 9's first open.
   Repeat the call as `creator-plus` for `peer-small@example.test`, whose
   un-joined invitation is what step 7 reads.
   As `creator-team` at the default, expect `cant_share_outside_team`; then
   change "Who can be added to files and folders" in the admin console
   ([manage-team-sharing](https://help.dropbox.com/share/manage-team-sharing)),
   record each option's exact label, approve `peer-roomy`'s address, repeat.
   Also as `creator-team`: `dbx sharing/list_folders '{"limit":100}'` →
   `list_folders.team.200.json` for the team folder's own `shared_folder_id`,
   then step 5 on that id → `add_folder_member.team_folder.<status>.json`.
6. **Quiet.** As `peer-roomy`, within five minutes and again after an hour:
   the mailbox (and spam), the dropbox.com notifications bell, the Shared
   page, the desktop and mobile apps if installed. Record where the invite
   appears and when. `dbx sharing/list_mountable_folders '{"limit":100}'` as
   the Peer → `list_mountable_folders.peer_invited.200.json`.
7. **View without Join.** As `peer-small` (invited by `creator-plus` in
   step 5, not joined): open the folder's `preview_url` from step 4 in the
   Peer's browser, and record whether the file list shows, whether
   `episode-1.pdf` opens and whether `episode-2.mp4` plays — without pressing
   Join. Then `dbx sharing/get_folder_metadata '{"shared_folder_id":"…"}'` and
   `dbx sharing/get_file_metadata '{"file":"id:…"}'` as the Peer →
   `get_folder_metadata.peer_invited.<status>.json`,
   `get_file_metadata.peer_invited.<status>.json`. Open the file
   `preview_url` from the creator's own `get_file_metadata.creator.200.json`
   as the Peer and record what it shows.
8. **Join and storage.** As `peer-roomy`: `void users/get_space_usage` →
   `get_space_usage.before_join.200.json`;
   `dbx sharing/mount_folder '{"shared_folder_id":"…"}'` →
   `mount_folder.success.200.json` — the API form of Join, so the successful
   shape is a fixture; the browser form is walked in step 18b — then
   `get_space_usage.after_join.200.json`. Record the difference against the
   folder's size ([shared-folder-count-against-storage](https://help.dropbox.com/storage-space/shared-folder-count-against-storage))
   and how long until `dbx files/list_folder '{"path":"/Qori spike","recursive":false}'`
   lists the folder in the Peer's own Dropbox. As `peer-small`: press Join
   and record what dropbox.com says
   ([shared-folder-cant-join](https://help.dropbox.com/share/shared-folder-cant-join));
   then `dbx sharing/mount_folder '{"shared_folder_id":"…"}'` →
   `mount_folder.insufficient_quota.<status>.json` (the tag as declared in
   `MountFolderError`; confirm it).
9. **Web URL shape.** As `peer-roomy` after Join: open the folder from
   Shared, open `episode-1.pdf` — stop the stopwatch from step 5 here and
   write the seconds in the report — and record the address bar with the
   account-specific segments marked; compare it with `preview_url` from
   `get_folder_metadata.peer_joined.200.json` and
   `get_file_metadata.peer_joined.200.json`, and with the creator's two.
   Record which of the four opens the Episode directly for the Peer, and
   whether any is a shared link (then `dbx sharing/get_shared_link_metadata '{"url":"…"}'`
   → `get_shared_link_metadata.200.json`). Start step 20's playback now and
   leave it running.
10. **Currency**, as `creator-plus`, one at a time, with `files/list_folder`
    before and `dbx files/list_folder/continue '{"cursor":"…"}'` after each:
    (a) upload `episode-3.pdf` on dropbox.com — a file no Episode will name,
    which is what the picker copy about folder contents rests on; (b) upload
    a changed `episode-1.pdf` on dropbox.com and choose Replace; (c) the same
    through the API with `"mode":"overwrite"` →
    `files/upload.overwrite.200.json`; (d) drag a replacement over it in the
    desktop client; (e)
    `dbx files/move_v2 '{"from_path":"/episode-4.pdf","to_path":"/Qori spike/episode-4.pdf"}'`
    → `files/move_v2.200.json`; (f) rename `/Qori spike` to `/Qori Series`
    on dropbox.com, `dbx sharing/get_folder_metadata '{"shared_folder_id":"…"}'`
    as the creator → `get_folder_metadata.renamed.200.json`, and record
    whether `peer-roomy` still sees the folder and under which name; then
    rename it back. After each of (a) to (e): is the file `id` kept
    ([dbx-file-access-guide](https://developers.dropbox.com/dbx-file-access-guide)
    says a new file with the same name gets a new one); does `peer-roomy`
    see it on reload, and after how long; does `peer-small` see it through
    `preview_url` if step 7 worked.
11. **Over quota** (run if time allows; "not run" is an honest report line).
    Fill `peer-roomy`'s own space to within 100 MB of 2 GB, then as
    `creator-plus` add a 300 MB file to the folder. Record whether Dropbox
    removes the folder from the Peer
    ([over-quota](https://help.dropbox.com/storage-space/over-quota)) and
    how soon.
12. **Idempotency and the member list.** Repeat step 5 for `peer-roomy` (now
    a member) → `add_folder_member.already_member.<status>.json`, and for
    `peer-none` twice → `add_folder_member.already_invitee.<status>.json`.
    Then `dbx sharing/list_folder_members '{"shared_folder_id":"…","limit":100}'`
    → `list_folder_members.200.json`: which list each Peer is in, and the
    `account_id` beside a member. The `users`/`invitees` split is the
    creator-token evidence of Join that `T-096`'s `checkGrant()` reads.
13. **Account created later.** With `peer-none` invited quietly in step 12,
    create a Dropbox account on that address; before verifying, check the
    Shared page and `list_mountable_folders`; verify; check again. Record
    whether the invite is there with no new call. Then invite `peer-roomy`
    at a second address that is not the account's main email and record
    whether `list_folder_members` shows an invitee rather than a user.
14. **Unverified.** As `creator-basic`,
    `"member":{".tag":"dropbox_id","dropbox_id":"dbid:…"}` for
    `creator-unverified`'s `account_id` →
    `add_folder_member.bad_member.unverified_dropbox_id.<status>.json`. As
    `creator-unverified`, step 4 →
    `share_folder.email_unverified.<status>.json`.
15. **Revoke.** As `creator-plus`, with `episode-1.pdf` open in
    `peer-roomy`'s browser:
    `dbx sharing/remove_folder_member '{"shared_folder_id":"…","member":{".tag":"email","email":"peer-roomy@example.test"},"leave_a_copy":false}'`
    → `remove_folder_member.200.json`; if it answers with an `async_job_id`,
    `dbx sharing/check_remove_member_job_status '{"async_job_id":"…"}'` →
    `check_remove_member_job_status.complete.200.json`. Record what the open
    file does, when the folder leaves the Peer's Dropbox, and what the step 9
    URLs show afterwards. Then `list_folder_members` again →
    `list_folder_members.after_revoke.200.json`: the Peer is gone from both
    lists, or is not.
16. **One file call.** As `creator-plus`, on `/episode-4.pdf` before step 10e:
    `dbx sharing/add_file_member '{"file":"id:…","members":[{".tag":"email","email":"peer-roomy@example.test"}],"quiet":true,"access_level":"viewer"}'`
    → `add_file_member.success.200.json`. Record whether an email arrives
    (the file-level `quiet` wording lost "email" on 12 May 2026 while the
    folder wording kept it — the two spec files disagree).
17. **OIDC, `peer-roomy`.** The authorize URL from step 1 with
    `scope=openid+email`; exchange; → `oauth2/token.openid.200.json` and the
    decoded `id_token` payload → `oauth2/token.openid.claims.json`
    ([oidc-guide](https://developers.dropbox.com/oidc-guide)). Record whether
    `sub` equals the `account_id` from `users/get_current_account`, and
    whether `email_verified` is present.
18. **The walkthrough under Qori's permissions.** As `creator-plus`, step 1
    again with `scope=account_info.read+files.metadata.read+sharing.read+sharing.write`
    — no `files.content.write` — and only that token from here. As
    `peer-roomy` (removed in step 15), a fresh browser profile, signed in
    through step 17's `openid email` round trip and holding no Peer token.
    Then, each timed from its 200: (a) step 5 by `dropbox_id`, the `sub`
    from step 17; (b) the Peer opens the folder `preview_url`, presses Join,
    opens `episode-1.pdf`; (c) the creator uploads `episode-5.pdf` on
    dropbox.com and the Peer reloads and opens it; (d) step 5 again — the
    repeated grant; (e) the recoverable failure: `void auth/token/revoke` as
    `creator-plus`, then step 5 for `spike+walk@…` →
    `add_folder_member.invalid_access_token.<status>.json`; re-link the same
    account (step 1) → `oauth2/token.offline.relinked.200.json`, repeat the
    call on the same `shared_folder_id` and record that it succeeds; (f) as
    `creator-basic`'s token, `dbx sharing/get_folder_metadata '{"shared_folder_id":"…"}'`
    on `creator-plus`'s folder → `get_folder_metadata.other_account.<status>.json`,
    what a connection to a different account finds when it reads a stored
    id. A step that only the diagnostic token got through is a finding.
19. **Invite cap, last, as `creator-basic`.** Loop step 5 with
    `spike+NNN@…`, one address per call, ten seconds apart, until the first
    error; record the count, the tag, the time, and any `Retry-After`
    ([dbx-performance-guide](https://developers.dropbox.com/dbx-performance-guide)).
    Then one call with 1,001 addresses in `members`, one over the per-request
    figure on [large-deployments](https://help.dropbox.com/plans/large-deployments),
    which is written for team deployments and unconfirmed for personal plans
    → `add_folder_member.oversize_members_arg.<status>.json`, whatever tag
    and status come back; this task names none. During the
    suspension: one `add_file_member`, to record whether the same cap blocks
    it. Probe hourly with one fresh address and record the first success:
    that is when it resets.
20. **Streaming, in the background from step 9.** As `peer-roomy` on
    `creator-basic`'s folder, play `episode-2.mp4` from the start and record
    where it stops
    ([video-audio-FAQ](https://help.dropbox.com/view-edit/video-audio-FAQ)).
    If `creator-basic` could add no member in step 5, that is row 1's answer
    and this row says so; the Plus folder's limit is not measured in an `S`.

The report's **Outcome** is this table, one row per question, each cell
"observed" with the fixture, or "not observed" with why. **Row 1 is step 0's
and is answered before any other row is attempted** (`D-042`); if it answers
that a Basic creator cannot add a viewer, every other row reads "not
observed — the spike stopped at step 0".

| #   | Question                                                                               | Decides in `T-096`                                                                  |
| --- | -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| 1   | Basic creator adds a viewer: success or `insufficient_plan` (step 0)                   | Whether Basic is a tier or "cannot"; and whether the spike goes on at all (`D-042`) |
| 2   | Plus creator adds a viewer                                                             | Same, for the paid personal tier                                                    |
| 3   | Team creator at the default, then after approving the address; the team folder itself  | The team tier's copy and error handling                                             |
| 4   | `quiet: true`: email, bell, Shared page, apps — where and when                         | Whether Open is the Peer's only pointer                                             |
| 5   | An invitee views the folder and a file through `preview_url` without Join              | Whether Join and storage bullets exist                                              |
| 6   | Join: `used` delta; `peer-small`'s error; what dropbox.com says                        | The "cannot join" path                                                              |
| 7   | Over quota after a creator upload: folder removed, and when                            | A creator warning, or nothing                                                       |
| 8   | Added (an Episode or not), replaced (site, API, desktop) and moved-in files: `id` kept | Episode lookup by `id` or by relative path; the picker line                         |
| 9   | Re-adding a member and an invitee: the response                                        | Whether the ensure step needs a lookup                                              |
| 10  | Account created later on the invited address, before and after verifying               | The "no Dropbox account yet" path                                                   |
| 11  | A second address becomes an invitee, not a member                                      | Why `T-092` collects the main address                                               |
| 12  | `dropbox_id` of an unverified account; `share_folder` from an unverified creator       | Two error rows                                                                      |
| 13  | Invite cap: count, first tag, reset time; file invites under it                        | The reconcile command's retry rule                                                  |
| 14  | Revoke: async or not; the open file; time to disappear; the member list after          | Whether revoke polls a job; what `revoked` is checked against                       |
| 15  | The four URL shapes, and which opens an Episode for the Peer                           | What Open stores or derives                                                         |
| 16  | OIDC `sub` equals `account_id`; `email_verified` present                               | `T-092`'s stored subject                                                            |
| 17  | `account_type` per tier                                                                | Whether the tier dropdown can be checked                                            |
| 18  | Production approval: what the console asks, and any stated lead time                   | `release-prerequisites.md`'s Dropbox line                                           |
| 19  | Streaming stops at 30 minutes on Basic                                                 | The tier's video line, and whether video is offered on Basic                        |
| 20  | Seconds per call; `share_folder` asynchronous or not; the stopwatch to first open      | `REQUEST_TIMEOUT_SECONDS` against Dropbox; when to say `pending`                    |
| 21  | `list_folder_members` before Join, after Join, after removal                           | When the grant is `granted`, and what `checkGrant()` reads                          |
| 22  | Nesting refused: `inside_shared_folder`                                                | The picker's nesting line beside `T-091`'s folder rule                              |
| 23  | Same account re-linked reaches the same id; a different account reading it; the rename | The reconnect, repick and rename handling (`T-091`'s triggers)                      |
| 24  | The walkthrough under Qori's scopes: first access, later content, repeat, recovery     | The release check `T-096` cites                                                     |

The report's **States** table is the same rows read the other way: each
outcome met, the fixture, the `VendorGrantStatus` it maps to and who resolves
it. The mapping below is the candidate, in `T-091`'s vocabulary; a fixture
confirms or corrects each line, and `T-096` states the final one.

| Outcome                                                                                                                                                                    | Candidate state       | Resolves                          |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- | --------------------------------- |
| `add_folder_member` 200 and the Peer in `invitees`, or in `users` but not yet joined                                                                                       | `awaiting_acceptance` | The Peer, by pressing Join        |
| The Peer in `users` and the folder mounted — or viewing through `preview_url` if row 5 says so                                                                             | `granted`             | —                                 |
| `mount_folder` → `insufficient_quota`                                                                                                                                      | `awaiting_acceptance` | The Peer, by freeing space        |
| `bad_member/unverified_dropbox_id`, or no confirmed identity yet                                                                                                           | `awaiting_identity`   | The Peer, by signing in (`T-092`) |
| `insufficient_plan`, `cant_share_outside_team`, `email_unverified`, `team_folder`, `no_permission`, `too_many_pending_invites`, `too_many_members`, `invalid_access_token` | `needs_creator`       | The creator                       |
| `rate_limit`, `429` with `Retry-After`, `too_many_write_operations`, a timeout, an `async_job_id` still running                                                            | `pending`             | Nobody; the next trigger retries  |
| `remove_folder_member` complete                                                                                                                                            | `revoked`             | —                                 |

## Copy

None. The facts feed `T-096`'s tier bullets and Open-page copy; that task
owns the lang keys. What the spike owes them is the States table: every
Peer-facing sentence names who can resolve a non-granted state, and "nothing
more is needed from you" is only ever said for `pending` — so an outcome the
Peer or the creator has to act on is never recorded as `pending` here.

## Routes

None.

## Tests

None. The fixtures are read by `T-096`'s tests; this task writes no test.

## Acceptance

**If step 0 answers that a Basic creator cannot add a viewer, the spike stops
there** (`D-042`) and the list below is read against that: the first box is
ticked, the fixture box is met by step 0's four fixtures and a README gap
list saying where the spike stopped, the answer-table box is met by row 1
observed and every other row "not observed — the spike stopped at step 0",
the report carries the bullet for the owner, and the boxes naming step 18,
the States table and production approval do not apply and say so. Otherwise
every box is read as written.

- [ ] Step 0 ran first — before any account but `creator-basic` existed,
      before any file was uploaded and before any other fixture was gathered
      — and row 1 of the answer table is "observed" with its fixture
- [ ] Nothing was bought to run the spike, and any step that could not be
      observed on a free account says so with that reason (`D-042`)
- [ ] Every fixture in the Files table exists, or the README's gap list says
      which error was not met and why; each body is verbatim under the
      redaction map, and the README states the date, the app, the account
      role, the status and the seconds for each file
- [ ] Every row of the answer table is "observed" with its fixture or "not
      observed" with the reason, in the report, and every row of the States
      table names its fixture beside the candidate state it confirms or
      corrects
- [ ] The walkthrough (step 18) is in the report with its seconds, and any
      step that only the diagnostic token got through is a finding
- [ ] Every bullet in `T-096`'s "Before this can be ready" that this spike
      answers is struck with the date and a one-line answer — or, while
      `T-096` is a bare template, a Notes line there names the report; any
      choice the facts leave the owner is written there as a bullet for the
      owner, and a change to the grant model as a bullet for `T-091`'s
- [ ] The report records the App Console's production-approval step and any
      lead time it states, and the scopes `T-096` needs without
      `files.content.write`
- [ ] Every "Found, not fixed" bullet in the report ends in a disposition
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Whether to pay for a Dropbox Plus account (or start its trial) and a
  Dropbox for teams trial for the spike, and on whose card — the owner's.~~
  **Answered 21 September 2026 by the owner, as `D-042`:** nothing is
  bought. The teams trial is replaced by the free Dropbox Business
  Development Account, granted by request; every other account is a free
  Basic one; and the Plus account is Dropbox's own 30-day trial, cancelled
  before it bills.

    The two outcomes of step 0 are different questions and should not be
    read as one. **Outcome A**, Basic can add a viewer: the spike runs in
    full, the working-creator steps run on `creator-basic`, and the trial is
    started only for rows 2, 17 and 19 — the Plus tier's own behaviour —
    then cancelled. **Outcome B**, Basic returns `insufficient_plan`: the
    spike stops and reports, because the remaining questions are not worth
    answering about a path Qori may not build, and the owner re-approaches
    the integration or drops it (`D-042`). The card question is theirs only
    in that second case, and it arrives with an observed reason in front of
    it rather than a guess.

- Whether the free Business Development Account carries Business-tier
  sharing behaviour. The Stone spec's sentence names Pro **or Business**, so
  if it does, `creator-team`'s free account is also the free observation of
  a working `add_folder_member`, and no personal paid tier is needed for
  row 1's successful case. Nothing published says either way; the request
  form is where to ask, and until it answers the roster assumes neither —
  the owner's, on the form.
- ~~Whether the steps and rows that name `creator-plus` run at all, given
  that no Plus account is provisioned, leaving rows 2, 17 and 19 as "not
  observed" and `T-096`'s paid-personal-tier copy resting on nothing — an
  exception to the evidence rule for the owner to record.~~ **Answered
  21 September 2026: they run, on the 30-day free trial** (Equipment above).
  It is free, it carries the full paid feature set, and it is cancellable
  before billing, so `D-042` is satisfied and no exception to `PROCESS.md`'s
  evidence rule is needed — every row gets an observed payload. Two things
  stay true rather than being waived: the trial has Basic's sharing
  bandwidth, so row 19's streaming limit is recorded as measured on a trial;
  and the cancellation is diarised, because `D-042` is about not buying
  anything and a trial nobody cancelled is a purchase made by inattention.
- Which domain the throwaway accounts and the invite loop's `spike+NNN@…`
  addresses use — the owner's.
- Whether the spike may apply for production approval on the App Console
  now, since that names the app `T-096` will ship with and the lead time is
  unpublished — the owner's.
- The fixture naming convention: `T-093` and `T-097` name flat files under
  the vendor directory with the status in the README row, this draft names
  `<namespace>/<route>.<case>.<status>.json`; whichever spike lands first
  sets it and the others rename — anyone's.
- Whether the invite-cap step (19) stays in an `S` spike when its wall clock
  is a day or more, or moves to `T-096`'s first week on a throwaway — anyone's.
- Whether the over-quota step (11), which the developer review asks for, is
  worth filling a Peer's 2 GB for, or the help page's word is taken —
  anyone's.
- **From the storage review's rate-limit table (20 September 2026):** Dropbox's
  performance guide (`V4`) publishes no rate number at all, holds the limit
  against the authorisation rather than the call, returns `Retry-After` on a
  429, and counts the throttled call itself. A 429 is therefore the whole
  connection's and not the one Peer's whose `add_folder_member` failed, and the
  invitation cap and ordinary API throttling are two limits with two resets:
  step 19 has to report them apart, and row 13 as drafted reads as one number —
  anyone's.
- **From the storage review, F10 (20 September 2026):** `D-036` put Google
  Drive's grants on files rather than on the folder, and that decision reaches
  no further. Whether a Dropbox grant sits on the shared folder or on a file is
  this spike's to settle on its own evidence — rows 5 and 21 are where that
  answer comes from — and `T-091`'s container-shaped queries and tests should
  not be frozen until this spike and `T-097` have both answered — anyone's,
  with `T-091`.
- **From the storage review, F11 and its evidence table (20 September 2026):**
  the Dropbox row it owns asks this spike for Basic viewer capability, Join
  with too little quota, `users` against `invitees`, the OIDC claims,
  member-list pagination, the asynchronous share and remove, rate-limit
  recovery and reconnect — and, by name, proof that retrying a remove without
  keeping its `async_job_id` converges, which row 14 sees once and `T-096`
  then relies on. Pagination is in none of the steps today, and `granted` rests
  on finding the Peer under `users`, so a folder whose member list runs past
  one page has no answer. What cannot safely be produced stays "not observed"
  in the Outcome table with its reason, and an exception to the evidence rule
  is the owner's to record rather than the spike's to waive — the owner's,
  with the two bullets above.

## Re-scope log

None.

## Notes

The two research digests disagree on the grant unit: one recommends per-file
grants (no Join, no Peer storage), the other the folder (every later file
reaches every member). `D-016` took the folder, and this spike tests that;
the one `add_file_member` call in step 16 is for the quiet-email question and
the cap, not a second design. If the facts leave per-file grants as the only
way a Peer without space can open anything, that is `T-091`'s grant model
changing, and the bullet goes to its owner.

`DropboxStorage.php:17-22` still gives `get_temporary_link` as the reason
Dropbox is the BYO provider and `docs/flows/storage.md:56` says the same.
Both describe what the code does today; `D-016` rewrites them with `T-096`'s
code, never before, and this spike touches neither.

`insufficient_plan` is the question the stream file names as the one that
can kill a tier (`docs/planning/streams/storage.md:136`), and step 0 is now
the whole of it. ~~If Basic returns it, `T-096` either drops Basic from the
tier dropdown or takes the owner's fallback for it~~ **Corrected
21 September 2026 (`D-042`, which restates `D-018`):** dropping the tier is
not one of the options. Every tier a creator brings is offered with its
limits stated on screen and none is refused, and `D-042` narrows what Qori
spends to find out rather than what Qori offers. So if Basic returns
`insufficient_plan`, the question `T-096` inherits is what a Basic creator is
told and when — at the connection, at the picker, or at the failed grant —
and the tier's presence in the dropdown is not in question. If Plus returns
it too, the folder grant is a team-plan feature and the stream's order
changes. Both outcomes are bullets for the owner in `T-096`, not decisions
here.

The Stone spec cited under Code lists `team_folder` under
`AddFolderMemberError` rather than `ShareFolderError`, so the first draft's
`share_folder.team_folder` fixture named a tag that route may never return.
Nothing here settles that: step 4 records whatever `share_folder` does say on
a team folder's path, and step 5 reaches `team_folder` by adding a member to
the team folder's own id. The fixtures decide which is which.

With steps 11, 19 and 20 run in full the wall clock is past an `S`; the two
bullets above are where that is decided, and the stopwatch steps are not the
reason. Step 0 is unaffected either way: four calls on one free account is
an hour, and on outcome B it is the whole task.
