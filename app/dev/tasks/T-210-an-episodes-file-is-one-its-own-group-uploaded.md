---
id: T-210
title: An Episode's file is one its own Group uploaded
stream: storage
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-210 — An Episode's file is one its own Group uploaded

## Why

A Qori-hosted Episode keeps its file as a key in `content['path']`, and that
key is whatever the form posted as `reference`
(`app/Http/Requests/Share/StoreEpisodeRequest.php`, `content()`'s default
arm), checked for nothing but its length. `EpisodeService::add()` stores it as
it comes, and `CloudflareR2Storage::linkFor()` signs whatever it names. So a
creator can make an Episode out of any key in the bucket — another Group's
file, a material, a chat code — and keys are not secret: every signed link a
Peer opens carries its key in the path. A Peer of one Group who runs a Group
of their own can keep reading a file after their access is taken away, by
pasting its key into an Episode of theirs.

Materials and chats already refuse this. `StoreMaterialRequest` and
`StoreChatRequest` look the upload up through the Group's own scope, want it
stored and of their purpose, and refuse one already attached elsewhere
(`errors.materials.asset_in_use`). An Episode is the one path that never
learned to, because it keeps a key in `content` where they keep a
`media_asset_id`. Afterwards an Episode can only be made from a stored
Episode upload of its own Group that no other Episode holds, as a material
can.

Found on 27 September 2026 while bringing `T-156` to ready: its deletes were
about to trust the same key. `T-156` makes every delete look the key up in the
Group's register and delete nothing it does not find; this task stops the key
being written in the first place.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

**Data this task verifies against:** a clean database.

**Equipment:** None.

## Scope

**In:**

- `StoreEpisodeRequest` refuses a Qori-hosted `reference` that is not a
  stored Episode upload of the current Group, or that another Episode of the
  Group already holds.
- `EpisodeService::add()` refuses the same, for every caller that is not the
  form.

**Out:**

- Episodes already stored with a foreign key. Pre-release data is swept by
  the owner (`T-156`'s decision of 20 September 2026).
- Materials and chats, which check this already.

## Files

To be written when the decisions below are made.

## Database

None expected.

## Code

To be written.

## Copy

To be written: one refusal, in `errors.php`.

## Routes

None.

## Tests

To be written.

## Acceptance

- [ ] An Episode cannot be made from another Group's upload, a material's or a
      chat's, an unfinished upload, or an upload another Episode holds
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **Whether the Episode should carry a `media_asset_id`** as materials and
  chats do, with a foreign key, instead of a key looked up in
  `content['path']` — the stronger shape, and a migration plus a change to
  `CloudflareR2Storage::linkFor()` — or keep the key and check it on the way
  in — anyone's, from the code.
- **The refusal's words**, and whether they reuse
  `errors.materials.asset_not_found` / `asset_in_use` — anyone's.

## Re-scope log

None.

## Notes

None.
