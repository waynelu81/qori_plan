---
id: T-160
title: Open grants the Peer on the Drive file and sends them to Drive
stream: storage
status: doing
owner: claude
estimate: M
depends: T-159
blocks: T-161
---

# T-160 — Open grants the Peer on the Drive file and sends them to Drive

## Why

Step 14 of [the first-share journey](../journeys/first-share.md): a Peer who
paid presses Open on a Google Drive Episode and lands in Drive's viewer, able
to see that one file. `D-040` settled how — the grant is made at Open, for that
item, inside the Peer's request — and `PlaybackTicketService::open()` already
marks the line it goes on. This is `T-091`'s happy path cut out of it: reader
on the file for the Peer's Qori email, `sendNotificationEmail=false`, then the
file's view link. `T-091`'s open questions become this step's branches, not
its gate.

## Decisions taken to make this specifiable

- **`T-091`'s names, the smallest part of its table.** `vendor_grants` with
  `T-091`'s column names and only what an Open-time item grant writes; its
  containers, retries and checks are its own to add. `VendorGrantStatus`
  carries all eight of `T-091`'s cases and `entitles()`, so nothing is renamed
  later. `VendorAccessService` is the name `T-091` gave the caller.
- **Granted once, then trusted.** A `granted` row for this Access and Episode
  sends the Peer straight to Drive with no vendor call (`D-040`: nothing
  re-checks). A permission removed by hand in Drive is a branch.
- **The Qori address is the principal.** `T-092` lets a Peer name another.
- **What a refusal means** — `cannotInviteNonGoogleUser` is
  `awaiting_identity`, the Peer's to resolve; a dead connection, a 401 or a
  404 is `needs_creator`; a 5xx or no answer stays `pending`, and Open again
  retries (`D-040`). The call is the one `T-093` recorded:
  `POST files/{id}/permissions?sendNotificationEmail=false&supportsAllDrives=true`.
- **The Peer's budget is shorter than the daily command's** (`D-034`):
  `fresh()` and the grant each get `VendorAccessService::REQUEST_TIMEOUT_SECONDS`.
- **A blocked Open says why in its toast**, one lang line per state; the
  "what's left is below" notice it pointed at was never built.
- **Peer-facing copy names Google**, because the Peer has to know which
  account to make. `D-035` wants the owner's word first — _asked_.

## Preconditions

None beyond `T-159`. The tests fake Google with `T-093`'s fixtures.

## Scope

**In:** the table, model and enums; the grant contract and Google's
implementation; the Drive resolver; the service; the step in
`PlaybackTicketService::open()`; the toast per state; copy; the flow doc.

**Out:** revoking (`T-103`), re-checking, a Peer's other Google account
(`T-092`), containers and the creator's retry list (`T-091`, `T-157`).

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `database/migrations/2026_09_21_000000_create_vendor_grants_table.php` | new | |
| `app/Models/VendorGrant.php` | new | `BelongsToGroup` |
| `app/Enums/VendorGrantStatus.php` | new | `T-091`'s eight cases |
| `app/Enums/GrantTarget.php` | new | `container`, `item` |
| `app/Data/GrantResult.php` | new | vendor-neutral |
| `app/Integrations/Contracts/GrantsItemAccess.php` | new | |
| `app/Integrations/Google/GoogleDriveFiles.php` | new | resolver and granter |
| `app/Providers/IntegrationServiceProvider.php` | edit | tags it |
| `app/Services/VendorAccessService.php` | new | `ensureGrant()` |
| `app/Services/PlaybackTicketService.php` | edit | the marked line |
| `app/Http/Controllers/Shared/OpenEpisodeController.php` | edit | the toast per state |
| `lang/en/shared.php` | edit | `vendor_notice.*` |
| `docs/flows/storage.md` | edit | Opening a Drive Episode |
| `tests/Feature/Storage/OpenDriveEpisodeTest.php` | new | |

## Database

`vendor_grants`: `id` ulid primary; `group_id` FK cascade; `access_id` FK
cascade; `target` string default `item`; `episode_id` FK null on delete,
nullable; `provider` string; `external_target_id` string; `principal` string
nullable; `vendor_ref` string nullable; `status` string default `pending`;
`last_error_code` string(100) nullable; `granted_at` timestamp nullable;
timestamps. Unique `(group_id, access_id, episode_id)`; index
`(group_id, provider, external_target_id, principal)`.

## Code

`VendorAccessService::ensureGrant(Access $access, Series $series, Episode $episode, User $peer): ?VendorGrantStatus`
— null when the Peer may go, the blocking state otherwise.
`GrantsItemAccess::grantReader(Connection $connection, string $itemId, string $email, int $timeoutSeconds): GrantResult`.

## Copy

`shared.vendor_notice.awaiting_identity`, `.needs_creator`, `.pending`.

## Routes

None.

## Tests

**New: `tests/Feature/Storage/OpenDriveEpisodeTest.php` — 6 cases**

1. `test_open_grants_the_peer_and_sends_them_to_drive`
2. `test_a_second_open_sends_them_without_asking_google`
3. `test_no_google_account_on_that_address_waits_on_the_peer`
4. `test_a_dead_connection_waits_on_the_creator_and_asks_google_nothing`
5. `test_google_failing_leaves_it_pending_for_the_next_open`
6. `test_nobody_without_access_is_granted`

## Acceptance

- [ ] A Peer with access pressing Open on a Drive Episode is granted reader and lands on the file
- [ ] A refusal lands them back on the Series with the reason
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

None.
