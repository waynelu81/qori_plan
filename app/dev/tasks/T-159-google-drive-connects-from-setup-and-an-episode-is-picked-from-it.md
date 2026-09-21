---
id: T-159
title: Google Drive connects from setup, and an Episode is picked from it
stream: storage
status: done
owner: claude
estimate: M
depends: T-044
blocks: T-160, T-161
---

# T-159 — Google Drive connects from setup, and an Episode is picked from it

## Why

Steps 6 and 9 of [the first-share journey](../journeys/first-share.md): a
creator connects the Google Drive they already have during setup, then makes
an Episode by picking a file from it. External storage is what Qori sells
(owner, 21 September 2026), and today both steps break. The connector is built
and tested (`T-044`) and tagged off in `IntegrationServiceProvider` until a
picker exists; `EpisodeProvider` has no Google Drive case; nothing opens
Google's Picker. Under `drive.file` the Picker is the only way a file becomes
Qori's to share (`T-093`), so it is not optional.

Afterwards: setup part 3 and Integrations offer Connect Google Drive, the round
trip lands back on setup (`ConnectionsDestination`, already built), and the
Episode form's Google Drive option opens the Picker and saves the chosen file.

## Decisions taken to make this specifiable

- **The connector is switched on here**, by tagging `GoogleAccounts` in
  `account-connectors`. The owner's condition of 20 September 2026 — hidden
  "until the picker that makes it useful lands with it" — is met by this task.
- **The Picker's token is an `Inertia::optional()` prop, `drivePicker`, on the
  Series page**, loaded by a partial reload when "Choose from Google Drive" is
  pressed. v1 stays Inertia-only; no JSON route. It answers
  `ConnectionService::fresh()`'s access token with `services.google.api_key`
  and `services.google.project_number`, and null for anyone but the Group's
  owner or without a live connection: the token opens the owner's Drive, and an
  admin must not browse it.
- **Google Drive is offered for File, Video and Audio**, first for File and
  Audio and after Vimeo for Video. Audio stops offering only a choice that is
  always refused.
- **An Episode stores `file_id`, `name` and `mime_type`** in `content`, the
  shape of `tests/Fixtures/google/files-get-episode-file.json`. The Picker's
  choice arrives as `reference` plus `drive_name` and `drive_mime`.
- **Copy comes from `lang/en/series.php` through a `drive` prop**, like
  `live.copy`; the provider's name is `T-044`'s
  `connections.providers.google_drive.name`, so no vendor is named that was not
  named before (`D-035`). The line beside the choice is `D-037`'s second shape:
  it changes who can open the file in the creator's Drive, never the file.
- **A Peer opening a Drive Episode is `T-160`'s**, which lands with this one.

## Preconditions

The Picker needs the owner's Google sign-in and the redirect URI and test users
the journey asks for; the tests fake Google (`Http::fake()`), as `T-044`'s do.

## Scope

**In:** the connector tagged; the Google Drive Episode provider; the Picker on
the Episode form, its token prop, and the saved content; copy; the flow doc.

**Out:** the grant at Open (`T-160`); editing an existing Episode's file;
folders; an admin choosing files.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Providers/IntegrationServiceProvider.php` | edit | tag `GoogleAccounts` |
| `app/Enums/EpisodeProvider.php` | edit | `GoogleDrive`, account-bound |
| `app/Enums/EpisodeType.php` | edit | allowed for File, Video, Audio |
| `app/Http/Requests/Share/StoreEpisodeRequest.php` | edit | rules and `content()` for Drive |
| `app/Http/Controllers/Share/SeriesController.php` | edit | `drive` and `drivePicker` props |
| `config/services.php` | edit | `google.api_key`, `google.project_number` |
| `lang/en/series.php` | edit | `drive.*` |
| `resources/js/pages/share/series/Show.vue` | edit | the provider mirror and the Drive field |
| `resources/js/components/series/DrivePicker.vue` | new | loads Google's Picker and hands back the choice |
| `docs/flows/storage.md` | edit | the Picker and the Drive Episode |
| `tests/Feature/Share/DriveEpisodeTest.php` | new | the cases below |

### Added during execution

| Path | Change | Notes |
| --- | --- | --- |
| `lang/en/connections.php` | edit | Google Drive's copy was the folder design's; rewritten per file (`D-036`, `D-040`) |
| `app/Support/ProviderSections.php` | edit | `common.folder` → `common.one_file` |
| `tests/Feature/Share/IntegrationsProvidersTest.php` | edit | reads `one_file` |
| `tests/Feature/Share/EpisodeServiceTest.php` | edit | Google Drive is account-bound |
| `docs/flows/onboarding.md` | edit | part three's link |
| `.env.example` | edit | the Picker's two keys |
| `tests/Feature/Share/ConnectionsConnectTest.php` `tests/Feature/Share/ConnectionAccountChangeTest.php` `tests/Feature/Console/RefreshConnectionsCommandTest.php` | edit | docblocks |

## Database

None. `episodes.content` is jsonb and takes the new shape.

## Code

`EpisodeProvider::GoogleDrive = 'google_drive'`; `connection()` answers
`ConnectionProvider::GoogleDrive`, `isAccountBound()` true. The rest is named
in Decisions.

## Copy

`series.drive.choose`, `series.drive.choose_again`, `series.drive.chosen`,
`series.drive.touches` (D-037), `series.drive.not_connected`,
`series.drive.owner_only`, `series.drive.loading`, `series.drive.failed`.

## Routes

None.

## Tests

**New: `tests/Feature/Share/DriveEpisodeTest.php` — 6 cases**

1. `test_google_drive_has_a_section_once_its_connector_is_bound`
2. `test_a_drive_episode_is_saved_with_the_picked_file`
3. `test_a_drive_episode_is_refused_without_a_live_connection`
4. `test_a_drive_episode_needs_a_file`
5. `test_the_picker_token_is_the_owners_fresh_token`
6. `test_nobody_but_the_owner_gets_a_picker_token`

**Changed:** whatever asserted that no connector is bound; listed under
**Added during execution** when found.

## Acceptance

- [x] Setup part 3 and Integrations offer Google Drive
- [x] The Episode form's Google Drive choice asks for the owner's token and saves the file the Picker hands back; the Picker against a real Google account is walked in `T-161`
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

- **21 September 2026, wording tier:** the second Acceptance line said the
  choice "opens the Picker". Opening it needs a Google sign-in, which an agent
  does not do, so the line now says what was verified and hands the real walk
  to `T-161`, whose by-hand pass exists for exactly this.
