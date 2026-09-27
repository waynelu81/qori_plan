---
id: T-192
title: A private note on each Peer
stream: classroom
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-192 — A private note on each Peer

> Written on 23 September 2026 from
> [the Kajabi note](../../design/competitor-kajabi.md), proposal 4, at the
> owner's word ("good idea"). Brought to ready on 27 September 2026 with the
> owner's answers of that day.

## Why

A tutor, a coach or anyone teaching a dozen people keeps what they know about
each one — where they are up to, what they asked for, what to remember next
time — in a spreadsheet or their head. Kajabi's coaching product keeps the
coach's private notes on each client beside the client's own, and it is the
part of that product a one-person teacher actually uses. Qori's `peers` table
is already the Group's CRM, one row per person, and has no room for a word.

Afterwards each row on the Peers page takes a short private note, which the
owner writes in place and the Group's collaborators read, shown again on the
Series page's Peer list — and which the Peer never sees anywhere: not on the
shared surface, not in an email, not on a certificate.

## Decisions taken to make this specifiable

**The note is on the Peer, not on the access.** The person is the same across
every Series they are in, and what a teacher remembers about them is too.

**The owner writes it; the owner and the Group's collaborators read it** (the
owner, 27 September 2026: "No admin don't write it. It is data for creator
and collaborator", read back and confirmed). The Peers page offers the owner
an Add or Edit on each row and shows an admin the note alone; the `PATCH`
refuses anyone but the owner with `errors.peers.owner_only`.

**It shows on the Peers page and on the Series page's Peer list** (the owner,
27 September 2026). It is written only on the Peers page; the Series page
shows it as a line under the Peer, as it shows whether they opened the chat
(`T-207`).

**Never in a Peer-facing payload, and never serialised by accident.** `Peer`
reaches the shared side only through `Access`, and no shared controller or
notification maps the column; beside that, `note` is in `Peer::$hidden`, so a
Peer model handed wholesale to a page or a JSON response leaves it out. The
two creator pages read the attribute by name. A test renders the Peer's own
Series page and the emails a Peer receives with a note in place and finds none
of it.

**Edited on the Peers page, in place, by an id.** `PATCH
g/{group}/peers/{peerId}` (ids act, slugs read), one field, `note`, through
`UpdatePeerNoteRequest`: nullable, at most `qori.limits.text.peer_note`
characters — 500, the draft's proposal — trimmed, an empty one clearing it. A
Peer of another Group is not found, as the Group middleware answers for any
row outside it.

**No flow file described the Peers page**, so `docs/flows/accesses.md`, whose
"creator side" section is the nearest, gains one: the list and its one write.

## Preconditions

**Data this task verifies against:** a clean database for the tests: a Group
with its owner and an admin, a published Series, and Peers granted to it.
The browser check uses the design-review world, whose Peers have no note, and
clears the one it writes.

**Equipment:** a browser at 390px, where the Peers page row has the least
room.

## Scope

**In:**

- The column, the request, the route, the owner's editor on the Peers page,
  and the note on both creator pages.
- The proof that no shared surface or email carries it.

**Out:**

- Notes per Series or per Episode; homework marking (`classroom`'s own).
- Export.
- The Peers page's existing inline English, which is `T-006`'s.

## Files

| Path                                                          | Change | Notes                                       |
| ------------------------------------------------------------- | ------ | ------------------------------------------- |
| `database/migrations/2026_09_27_000100_add_note_to_peers.php` | new    | `peers.note`                                |
| `app/Models/Peer.php`                                         | edit   | fillable; `$hidden`                         |
| `app/Http/Controllers/Share/PeerController.php`               | edit   | `index()` carries the note; `update()`      |
| `app/Http/Requests/Share/UpdatePeerNoteRequest.php`           | new    | one field, the length from config           |
| `routes/share/group.php`                                      | edit   | the `PATCH`                                 |
| `app/Http/Controllers/Share/SeriesController.php`             | edit   | `peers()` carries the note                  |
| `resources/js/pages/share/Peers.vue`                          | edit   | the note and the owner's editor on each row |
| `resources/js/pages/share/series/Show.vue`                    | edit   | the note under each Peer                    |
| `lang/en/peers.php`                                           | new    | the label, help, buttons and toasts         |
| `lang/en/errors.php`                                          | edit   | `peers.owner_only`                          |
| `config/qori.php`                                             | edit   | `limits.text.peer_note`                     |
| `docs/flows/accesses.md`                                      | edit   | "The Peers page"                            |
| `tests/Feature/Share/PeerNoteTest.php`                        | new    | 6 cases                                     |

## Database

| Table   | Column | Type | Null | Default | Index / constraint |
| ------- | ------ | ---- | ---- | ------- | ------------------ |
| `peers` | `note` | text | yes  | null    | none               |

Migration: `database/migrations/2026_09_27_000100_add_note_to_peers.php`

## Code

```php
// app/Http/Requests/Share/UpdatePeerNoteRequest.php
public function rules(): array;   // ['note' => ['nullable', 'string', 'max:'.config('qori.limits.text.peer_note')]]
public function note(): ?string;  // trimmed; '' is null

// App\Http\Controllers\Share\PeerController
public function update(string $group, string $peerId, UpdatePeerNoteRequest $request, CurrentGroup $current, Terminology $terminology): RedirectResponse;
// not the owner → AppException::forbidden('errors.peers.owner_only')
// Peer::query()->whereKey($peerId)->first() — scoped to the Group — or AppException::notFound()
// ->update(['note' => $request->note()]); toast peers.note.saved or peers.note.cleared; back()

// index() rows gain 'note' => $peer->note, and the page gains 'canEditNotes' => $current->isOwner()
// and 'noteCopy' from lang/en/peers.php.
// SeriesController::peers() rows gain 'note' => $access->peer?->note.
```

## Copy

| Key                       | File                 | English                                                                                                    |
| ------------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------- |
| `peers.note.label`        | `lang/en/peers.php`  | Note                                                                                                       |
| `peers.note.help`         | `lang/en/peers.php`  | Only you and whoever helps run this :group see it. Never shown to the :peer, in an email or anywhere else. |
| `peers.note.add`          | `lang/en/peers.php`  | Add a note                                                                                                 |
| `peers.note.edit`         | `lang/en/peers.php`  | Edit note                                                                                                  |
| `peers.note.save`         | `lang/en/peers.php`  | Save note                                                                                                  |
| `peers.note.cancel`       | `lang/en/peers.php`  | Cancel                                                                                                     |
| `peers.note.saved`        | `lang/en/peers.php`  | Note saved.                                                                                                |
| `peers.note.cleared`      | `lang/en/peers.php`  | Note removed.                                                                                              |
| `errors.peers.owner_only` | `lang/en/errors.php` | Only the owner can write notes. / Ask the owner to add it.                                                 |

The help line goes through `Terminology::line()` for `:group` and `:peer`;
neither noun follows "a" or "an".

## Routes

| Verb    | Path                       | Name                 | Action                   |
| ------- | -------------------------- | -------------------- | ------------------------ |
| `PATCH` | `g/{group}/peers/{peerId}` | `share.peers.update` | `PeerController::update` |

## Tests

**New: `tests/Feature/Share/PeerNoteTest.php` — 6 cases** (a Group with its
owner and an admin as Collaborators, a published Series, Peers granted through
`AccessService::grant()`)

1. `test_the_owner_writes_a_note_and_it_is_there_on_both_pages` — the toast,
   `peers.{n}.note` on the Peers page, `peers.{n}.note` on the Series page,
   `canEditNotes` true.
2. `test_an_empty_note_clears_it` — the column is null, the "removed" toast.
3. `test_the_note_is_limited_in_length` — 501 characters: an error on `note`,
   nothing saved.
4. `test_a_collaborator_reads_it_and_cannot_write_it` — the admin's page
   carries the note and `canEditNotes` false; the admin's `PATCH` answers 403
   with `errors.peers.owner_only`.
5. `test_another_groups_owner_cannot_reach_it` — 404, nothing saved.
6. `test_no_peer_facing_page_or_email_carries_it` — with a note in place: the
   Peer's Series page, the "you're in" email and `T-194`'s reminder contain
   none of it, and `Peer::toArray()` has no `note`.

## Acceptance

- [x] A note the owner types on a Peer's row is there on reload, on the Peers
      page and on the Series page's Peer list
- [x] A collaborator reads it and cannot write it
- [x] No shared-side page, email or serialised Peer carries the column
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Is the note also shown on the Series page's Peer list, beside progress, or
  only on the Peers page? (the owner's)~~ **Answered 27 September 2026:**
  both — edited on the Peers page, and shown on the Series page's Peer list
  (the owner's "yes to notes", given to that question and the next together;
  the reading is stated back to the owner).
- ~~Can an admin of the Group write it, or only the owner? (the owner's; the
  Peers page itself is readable by admins)~~ **Answered 27 September 2026:**
  "No admin don't write it. It is data for creator and collaborator", read
  back to the owner as: the owner writes it, the owner and the Group's
  collaborators read it — confirmed ("yes to notes"). It never shows in an
  email, or anywhere a Peer sees (Why).
- ~~Which flow doc describes the Peers page today — confirm the row above.
  (anyone's)~~ **Answered from the code, 27 September 2026:** none; the
  accesses flow gains a section (Decisions).
- ~~The length: 500 characters is proposed. (anyone's)~~ **Decided, 27
  September 2026:** 500, as `qori.limits.text.peer_note`.

## Re-scope log

**2026-09-27 — found while building.**

- **The dev database took the migration** before the browser check, the one
  pending migration, a nullable column; the note the check wrote was cleared
  through the page afterwards.

## Notes

None.
