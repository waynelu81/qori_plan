---
id: T-192
title: A private note on each Peer
stream: classroom
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-192 — A private note on each Peer

> **Draft.** Written on 23 September 2026 from
> [the Kajabi note](../../design/competitor-kajabi.md), proposal 4, at the
> owner's word ("good idea"). What has to be decided before it can be marked
> `ready` is listed at the bottom.

## Why

A tutor, a coach or anyone teaching a dozen people keeps what they know about
each one — where they are up to, what they asked for, what to remember next
time — in a spreadsheet or their head. Kajabi's coaching product keeps the
coach's private notes on each client beside the client's own, and it is the
part of that product a one-person teacher actually uses. Qori's `peers` table
is already the Group's CRM, one row per person, and has no room for a word.

Afterwards each row on the Peers page takes a short private note, edited in
place, that the Peer never sees anywhere: not on the shared surface, not in an
email, not on a certificate.

## Decisions taken to make this specifiable

**The note is on the Peer, not on the access.** The person is the same across
every Series they are in, and what a teacher remembers about them is too.

**Never in a Peer-facing payload.** `Peer` is loaded on the shared side only
through `Access`; the column is left out of every array the shared controllers
and the notifications build, and a test proves it.

**Edited on the Peers page, in place, by an id.** `PATCH g/{group}/peers/{peerId}`
(ids act, slugs read), one field, a Form Request with the length from
`config('qori.limits.text.peer_note')`.

## Preconditions

**Data this task verifies against:** a Group with three Peers, one in two
Series. `php artisan qori:reset basic` gives one.

**Equipment:** a browser at 390px, where the Peers page row has the least
room.

## Scope

**In:**

- The column, the field, the request, the route and the page.
- The proof that no shared surface, email or certificate carries it.

**Out:**

- Notes per Series or per Episode; homework marking (`classroom`'s own).
- Showing the note anywhere but the Peers page and the Series page's Peer
  list, if the latter is wanted at all — see below.
- Export.

## Files

| Path                                                       | Change | Notes                                       |
| ---------------------------------------------------------- | ------ | ------------------------------------------- |
| `database/migrations/2026_09_23_000000_add_note_to_peers.php` | new | `peers.note`                                |
| `app/Models/Peer.php`                                      | edit   | Fillable; never appended to shared arrays   |
| `app/Http/Controllers/Share/PeerController.php`            | edit   | `update()`                                  |
| `app/Http/Requests/Share/UpdatePeerNoteRequest.php`        | new    | One field, the length from config           |
| `routes/share/group.php`                                   | edit   | The `PATCH`                                 |
| `resources/js/pages/share/Peers.vue`                       | edit   | The field on the row                        |
| `lang/en/peers.php`                                        | new    | Label, help, saved toast                    |
| `config/qori.php`                                          | edit   | `limits.text.peer_note`                     |
| `docs/flows/accesses.md`                                       | edit   | The Peers page's one write                  |
| `tests/Feature/Share/PeerNoteTest.php`                     | new    | Cases to be named when ready                |

## Database

| Table   | Column | Type | Null | Default | Index / constraint |
| ------- | ------ | ---- | ---- | ------- | ------------------ |
| `peers` | `note` | text | yes  | null    | none               |

Migration: `database/migrations/2026_09_23_000000_add_note_to_peers.php`

## Code

To be settled when the draft is brought to ready: `PeerController::update()`,
the request's rule, and the page's inline editor.

## Copy

To be settled when ready, in `lang/en/peers.php`: the label ("Note, only you
see it"), the help, the saved toast. Nouns through the terminology layer.

## Routes

| Verb    | Path                          | Name                 | Action                   |
| ------- | ----------------------------- | -------------------- | ------------------------ |
| `PATCH` | `g/{group}/peers/{peerId}`    | `share.peers.update` | `PeerController::update` |

## Tests

To be written when ready: the note saves and reloads on the Peers page; an
admin of another Group cannot write it; it is absent from every shared-side
response, from `SeriesAccessNotification`, `InvitationNotification` and the
certificate; the length limit holds.

## Acceptance

- [ ] A note typed on a Peer's row is there on reload, on the Peers page only
- [ ] No shared-side page, email or certificate carries the column
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Is the note also shown on the Series page's Peer list, beside progress, or
  only on the Peers page? (the owner's)
- Can an admin of the Group write it, or only the owner? (the owner's; the
  Peers page itself is readable by admins)
- Which flow doc describes the Peers page today — confirm the row above.
  (anyone's)
- The length: 500 characters is proposed. (anyone's)

## Re-scope log

None.

## Notes

None.
