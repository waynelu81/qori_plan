---
id: T-201
title: Spike: Dropbox file grants from a team account
stream: storage
status: blocked
owner: claude
estimate: S
depends: none
blocks: T-096
---

# T-201 — Spike: Dropbox file grants from a team account

## Blocked on

What: the probe for steps 3 to 8 and the clean-up of step 9, with the owner at
the controls. Paused by the owner on 23 September 2026 after steps 0 to 2 and
step 3's uploads (Notes). The probe's scripts and tokens lived in that
session's scratchpad and did not survive the Mac's restore, so step 1's link is
made again first. Parked as blocked on 8 October 2026, from the independent
review of 6 October.

Who: wayne. His terminal with the Dropbox app's key and secret, a fresh
browser signed in as `support@useqori.com`, and his clicks on the team's
admin settings. Still on Dropbox meanwhile: `team-own.pdf`, `team-own-2.pdf`,
`Qori team folder` with `team-shared.pdf`, and the Qori Share connection.

## Why

`D-058` put Dropbox on per-file grants, and `T-095` observed them only on
free personal accounts. A creator whose Dropbox belongs to a team is under an
admin's sharing policy, which can refuse anyone outside the team, and nobody
has seen what `add_file_member` answers under it, whether a grant already
made survives the admin switching it on, or where a team member's files sit
for the API. `T-096` names "a team admin's outside-sharing policy against a
file grant" as still open, and cannot be ready without it. The owner's free
Dropbox Business Development Account, requested during `T-095`, was granted
on 23 September 2026, so the team can now be observed at no cost (`D-042`).

## Decisions taken to make this specifiable

- **The file route only** (`D-058`). No folder is shared, and `T-095`'s
  folder-route team steps (`cant_share_outside_team`, `team_folder`,
  `list_folders`) are not run.
- **The team's account is a new address, never `creator-basic`'s.**
  `creator-basic` is the owner's real personal Dropbox; joining a team with it
  puts it under the team's admin and Dropbox's terms for the development
  account. `creator-team` uses an address that has never had a Dropbox
  account.
- **The creator holds `T-096`'s four scopes only** (`account_info.read`,
  `files.metadata.read`, `sharing.read`, `sharing.write`), as step 18 of
  `T-095` did, so every call observed is one `T-096` can make. Files are
  uploaded through dropbox.com.
- **The Peer is `peer-roomy`, outside the team, granted by `dropbox_id`**,
  which is how `T-092` grants after sign-in. Its token from `T-095` reads its
  side.
- **The policy is observed at its default, then at its strictest, then back
  at the default**, so the tier copy describes what a team creator meets
  without touching anything, and what a strict admin does to Peers who
  already had access.
- **Each account has its own browser, and none signs out during the run.**
  Dropbox keeps one signed-in account per browser, so sharing a browser would
  mean signing out and in between steps, and a step run as the wrong account
  is easy to miss. See Equipment.
- **The admin console is read by Claude and changed by the owner.** A policy
  change is an account setting, so the owner clicks it; Claude records the
  exact labels before and after.
- **A second team member runs only if the development account has a free
  seat** (step 7), and only as far as it answers whether an admin's
  members-only policy still lets a creator grant a colleague.

## Preconditions

**Data this task verifies against:** none in Qori. On Dropbox: the team,
empty at first; `peer-roomy` and its token from `T-095`; the app `Qori
Share`, with Enable additional users still on.

**Equipment:**

| Window | Browser                                                                     | Signed in as                                                         | Used for                                                                                                                                          |
| ------ | --------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| W1     | The owner's usual browser                                                   | `creator-basic`, as now                                              | Nothing. It is not touched, and nobody signs out of it                                                                                            |
| W2     | Claude's Chrome tab group                                                   | `peer-roomy`, as now                                                 | The Peer's side: opening what was granted                                                                                                         |
| W3     | The built-in browser pane in the Claude app, never yet signed in to Dropbox | `creator-team`, signed in by the owner, who types their own password | Accepting the invite, the admin console, uploads, and the app's consent screen. Claude reads it; the owner clicks anything that changes a setting |

The owner's terminal, with `DBX_APP_KEY` and `DBX_APP_SECRET` exported,
runs every probe, as in `T-095`. Tokens go to a `t201-secrets/` folder in
Claude's scratchpad (mode 600), which Claude never reads.

## Scope

**In** — the steps, in order:

0. **The invite, before it is accepted.** The owner shows Claude the
   invitation from Dropbox, and it is accepted in W3 so that `creator-team`
   gets the new address. If Dropbox addressed it to `creator-basic`'s
   address, it is not accepted with that account: the owner asks Dropbox's
   developer support to re-issue it to the new address, or takes the option
   Dropbox offers for keeping a personal account separate. Claude records
   that option's exact wording before anything is clicked.
1. **Link.** A probe prints an authorize link with `T-096`'s four scopes and
   `token_access_type=offline`. The owner opens it in W3, Claude records the
   consent screen, the owner presses Allow and pastes the code into the
   terminal. Then `users/get_current_account`: `account_type`, `team`,
   `team_member_id` and `root_info`.
2. **The admin console, read only.** In W3, Admin console → Settings →
   Sharing: every option's exact label and its default, and the licence count
   on the billing or members page.
3. **Where a member's files are.** In W3 the owner uploads `team-own.pdf`
   into their own folder, `team-own-2.pdf` beside it, and `team-shared.pdf`
   into the team's shared space or a team folder, whichever the account has.
   A probe runs `files/list_folder` on `""` without a path root and with
   `Dropbox-API-Path-Root: {".tag": "root", "root": <root_namespace_id>}`,
   then `files/get_metadata` on each file's id with and without the header.
4. **Grant at the default.** `add_file_member`, `peer-roomy` by
   `dropbox_id`, viewer, quiet, on `team-own.pdf` and on `team-shared.pdf`;
   `list_file_members` on each (`same_team`, `team_member_id`); the Peer's
   `get_file_metadata` on each. In W2, Claude opens both as the Peer, and
   records whether Dropbox marks them as coming from outside the Peer's
   account or team.
5. **The strictest setting.** The owner sets sharing outside the team to its
   most restrictive option in W3. Then, for five minutes, the Peer's
   `get_file_metadata` on both files, polled, and `list_file_members` as the
   creator: does the grant made at the default survive? In W2, Claude
   reloads both files.
6. **A new grant under it.** `add_file_member` for `peer-roomy` on
   `team-own-2.pdf`, never granted, and for `spike-walk` (an address with no
   Dropbox account) on `team-own.pdf`: the answer's shape, per member. Then
   `remove_file_member_2` for `peer-roomy` on `team-own.pdf`: does a removal
   still work while new grants are refused?
7. **A colleague as Peer, only if step 2 found a free seat.** Still at the
   strictest setting, the owner invites `peer-team` (a new address) from the
   admin console and accepts in a private window of W1's browser. Then
   `add_file_member` for `peer-team` on `team-own-2.pdf`, and
   `list_file_members` (`same_team: true`).
8. **Back to the default.** The owner restores the step 2 setting. The Peer's
   `get_file_metadata` on `team-shared.pdf`: back by itself, or does it need
   granting again? Then `add_file_member` for `peer-roomy` on
   `team-own-2.pdf`, which step 6 refused.

    **8b, unregistered integrations blocked** (added after step 2; see the
    Re-scope log). The owner sets "Connecting unregistered integrations" to
    its blocking option in W3. A probe calls `users/get_current_account` with
    `creator-team`'s token, and the owner opens step 1's authorize link again
    in W3, where Claude records what Dropbox shows. Nothing is allowed.

9. **Restore.** The owner sets both policies back to their defaults, deletes the
   three files in W3, and removes `Qori Share` from `creator-team`'s
   connected apps. The development account itself stays, under its terms.

**Out:**

- The folder route, by `D-058`.
- The invite cap and production approval, both judged not applicable by the
  owner during `T-095`.
- An admin removing the creator from the team. It ends the creator's token,
  which `T-096` already treats as `needs_creator`, and needs a second admin.
- A Peer whose own account is on a team that refuses content from outside
  it. It can be added if a creator or a buyer meets it.
- Anything written in Qori: this spike's output is fixtures and a report.

The questions, and what each answer means for `T-096`:

| #   | Question                                                                                                                         | Step | What the answer decides in `T-096`                                                                 |
| --- | -------------------------------------------------------------------------------------------------------------------------------- | ---- | -------------------------------------------------------------------------------------------------- |
| Q1  | What do `account_type`, `team` and `root_info` say for a team member, and do `root_namespace_id` and `home_namespace_id` differ? | 1    | Whether `T-096` stores the root namespace and sends a path root                                    |
| Q2  | Does a file in the team's shared space appear to the API without a path root, and does its id work either way?                   | 3    | Whether the file picker needs the header, or ids are enough                                        |
| Q3  | What are the sharing options' labels and defaults?                                                                               | 2    | The words the tier copy uses, and whether a team creator meets a refusal without touching anything |
| Q4  | At the default, does `add_file_member` grant an outside Peer on each file?                                                       | 4    | Whether a team creator works out of the box                                                        |
| Q5  | At the strictest setting, does a standing grant survive?                                                                         | 5    | Whether an admin's change silently cuts Peers who have paid, and what state Qori shows             |
| Q6  | At the strictest setting, what does a new grant answer, and does a removal still work?                                           | 6    | The error `T-096` maps to `needs_creator`, and its copy                                            |
| Q7  | Back at the default, does a cut Peer come back by themselves?                                                                    | 8    | Whether `T-096` re-grants after a policy is lifted, or waits for the next Open (`D-040`)           |
| Q8  | Can a creator grant a colleague on the team while outside sharing is off?                                                        | 7    | Whether a team using Qori internally is served under a strict policy                               |
| Q9  | With unregistered integrations blocked, does a connected creator's token keep working, and what does a new connection meet?      | 8b   | Whether `T-096` needs a `needs_creator` state and copy for an admin who blocks Qori                |

## Files

| Path                                                                                                                                                                                                                                                                                                              | Change | Notes                                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------- |
| `tests/Fixtures/dropbox/README.md`                                                                                                                                                                                                                                                                                | edit   | A section for the team run, with its roles, and the gaps                                             |
| `tests/Fixtures/dropbox/users-get-current-account-team.json`, `tests/Fixtures/dropbox/files-list-folder-team-no-path-root.json`, `tests/Fixtures/dropbox/files-list-folder-team-path-root.json`, `tests/Fixtures/dropbox/add-file-member-team-default.json`, `tests/Fixtures/dropbox/list-file-members-team.json` | new    | Named as `T-095`'s are. Any error is named by what came back, `errors-<call>-<status>-<reason>.json` |

### Added during execution

| Path | Change | Notes |
| --- | --- | --- |
| `tests/Fixtures/dropbox/users-features-get-values-team.json` | new | Step 1's features read; uncommitted in the code repository until the spike resumes |
| `tests/Fixtures/dropbox/oauth2-token-offline-team.json` | new | Step 1's token exchange, tokens `REDACTED`; uncommitted likewise |

Flows: none — a spike; nothing in the code changes.

## Database

None.

## Code

None. The probes are shell scripts in Claude's scratchpad, written in
`T-095`'s manner: bash 3.2, secrets handed to `curl` on stdin, a log Claude
reads, and a run against a fake Dropbox before the owner runs them.

## Copy

None.

## Routes

None.

## Tests

None: the fixtures are for `T-096`'s tests.

## Acceptance

- [ ] Q1 to Q7 and Q9 answered from observed responses, each with its
      fixtures, and Q8 answered or marked not run for want of a seat
- [ ] `creator-basic` is not a member of the team at any point
- [ ] Step 9 done: the policy at its default, the files deleted, the app
      removed from `creator-team`
- [ ] `T-096`'s "team policy" is struck with the answers and a date
- [ ] Every "Found, not fixed" bullet in the report ends in a disposition
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Which address the invitation was sent to, what it offers, and which new
  address `creator-team` takes — _asked_ of the owner, 23 September 2026.~~
  **Answered the same day:** the owner accepted it as `support@useqori.com`,
  and `wayne.lu81@gmail.com`, `creator-basic`, is still their personal
  Dropbox, unchanged. `creator-team` is `support@useqori.com`.
- ~~Whether the development account's terms limit how long it lasts or what
  may be done with it — _asked_ of the owner, who holds the email.~~
  **Decided rather than asked, 23 September 2026:** the spike runs now, which
  meets any time limit the terms could set, and it does nothing a
  development account is not for.

## Re-scope log

- **23 September 2026, step 0 ran before the draft reached the owner.** They
  accepted the invitation as `support@useqori.com`, a Qori address with no
  Dropbox account until then, so the question of joining with
  `creator-basic` never arose and nobody recorded Dropbox's options. W3 is
  still where `creator-team` signs in for steps 1 to 9.
- **23 September 2026, after step 2: one question added.** The admin
  console's Integrations tab has "Connecting unregistered integrations", set
  to Allow, described as whether members "can connect integrations that
  aren't officially registered in the Dropbox App Center". `Qori Share` is
  unregistered until production approval, so a team admin can keep a creator
  from connecting Qori at all. Step 8b, before Restore: the owner sets it to
  its blocking option; does `creator-team`'s standing token still answer, and
  what does a new connection meet in W3? That is Q9, and the owner sets it
  back in step 9.

## Notes

**Progress, 23 September 2026, paused by the owner until the next day.**
Steps 0 to 2 are done and step 3's uploads are in; the next thing to run is
the probe for steps 3 to 8. Observed so far, with fixtures saved uncommitted
in `tests/Fixtures/dropbox/` (`users-get-current-account-team.json`,
`users-features-get-values-team.json`, `oauth2-token-offline-team.json`):

- Step 1: the consent screen, which the owner described as the same as
  `T-095`'s, granted exactly `T-096`'s four scopes and a refresh token. The
  account is `business`, on the team "Test Qori", with a `team_member_id`.
  `root_info` is tagged `user`, yet its `root_namespace_id` and
  `home_namespace_id` differ and it carries `home_path`, the member folder
  named after the account. Features: `team_shared_dropbox` off,
  `distinct_member_home` on.
- The account's `team.sharing_policies` has `shared_folder_member_policy:
anyone` and `shared_folder_join_policy: from_anyone`: at the default, the
  team lets anyone be added. `T-095` had said a team's default refuses
  everyone outside it (its Why).
- Step 2: under Settings → External sharing, "Who can be added to files and
  folders" reads "Choose who members can add to files and folders — anyone,
  members only, or specific people outside your team that you approve", set
  to **Anyone**; its other options are **Members + approved people** and
  **Members only**. Under Integrations, "Connecting registered integrations"
  and "Connecting unregistered integrations" are both **Allow**. The plan is
  Dropbox Business with three licences, two free, and 5.03 TB.
- Step 3: the top level of a team member's All files holds only the member
  folder (`Wayne Lu`) and team folders; dropping a file there opens a picker
  that insists on a folder, although Content says "Everyone at Test Qori can
  edit at the top level". So `team-own.pdf` and `team-own-2.pdf` are in the
  member folder. `Qori team folder` was created as a team folder for "Only
  specific people", listed with 0 members, and the owner then added
  `support@useqori.com` to it and put `team-shared.pdf` inside.

The team request went in on 23 September 2026 through Dropbox's developer
support form, filled in the owner's Chrome and submitted by the owner, saying
Qori was in internal testing and not yet public.
