---
id: T-159
title: Google Drive connects from setup, and an Episode is picked from it
stream: storage
status: draft
owner: unassigned
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

## Before this can be ready

- How the Picker gets a token: an owner-only route answering
  `ConnectionService::fresh()`'s access token with the API key and the project
  number (`GOOGLE_API_KEY`, `GOOGLE_PROJECT_NUMBER`, both set). Name the route
  by `D-032`/`D-033`, and decide whether it is the first JSON response in a v1
  that is otherwise Inertia-only.
- Which Episode kinds take Google Drive — File, Video and Audio all preview in
  Drive's viewer.
- What an Episode stores from the Picker: file id, name and MIME type, shaped
  from `tests/Fixtures/google/files-get-episode-file.json`.
- The line beside the option, by `D-037`: it changes who can open the file in
  the creator's Drive, never the file.
- Walking it needs the owner's config — the Google redirect URI and the test
  users (journey, "What to do" 1) — and one real Google sign-in, which an agent
  does not do.

## Re-scope log

None.

## Notes

None.
