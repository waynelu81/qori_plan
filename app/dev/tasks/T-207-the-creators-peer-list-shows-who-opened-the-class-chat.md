---
id: T-207
title: The creator's Peer list shows who opened the class chat
stream: classroom
status: draft
owner: unassigned
estimate: S
depends: T-132
blocks: none
---

# T-207 — The creator's Peer list shows who opened the class chat

## Why

`D-029` says the creator's Peer list shows who opened the class chat card,
because Qori cannot see who joined the chat itself and removal from it is by
hand. `T-132` writes one `access_opens` row, target `chat`, every time a Peer
follows the card, and reads none back. Its brief kept the list out, and on
27 September 2026 the split was decided: the reader is this task. Until it
lands, a creator can see who has access and cannot see who has found the chat.

## Decisions taken to make this specifiable

None yet: see "Before this can be ready".

## Preconditions

None.

**Data this task verifies against:** a clean database, with `access_opens`
rows written through `SeriesChatService::open()`.

**Equipment:** a visible browser, to see the column on the creator's Series
page.

## Scope

**In:**

- On the creator's Series page, each Peer row says whether that Peer has
  opened the chat card, read from `access_opens` with target `chat`.

**Out:**

- Who is in the chat. Qori calls no chat vendor (`D-029`).
- "I've joined", which is the Peer's browser's memory and never reaches the
  server (`T-132`).

## Files

| Path                                                | Change | Notes                                    |
| --------------------------------------------------- | ------ | ---------------------------------------- |
| `app/Http/Controllers/Share/SeriesController.php`   | edit   | `peers()` carries the chat-open fact     |
| `resources/js/pages/share/series/Show.vue`          | edit   | The Peer rows show it                    |
| `lang/en/chats.php`                                 | edit   | The line on the row                      |
| `docs/flows/chats.md`                               | edit   | The reader of the `access_opens` rows    |
| `tests/Feature/Series/SeriesChatTest.php`           | edit   | The row says it, and only for this chat  |

## Database

None.

## Code

To be written when the task is brought to ready.

## Copy

To be written when the task is brought to ready.

## Routes

None.

## Tests

To be written when the task is brought to ready.

## Acceptance

- [ ] A creator sees, on each Peer row, whether that Peer has opened the
      class chat card
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- What the row says: that the Peer opened the chat, when they last did, or
  both; and whether a chat replaced since then counts — anyone's, from how
  `T-132` built `access_opens`' `subject_id`.
- Whether a Peer with no open is shown as such, or the row says nothing —
  anyone's, weighed against the Peer list's other lines.

## Re-scope log

None.

## Notes

Drafted by `T-132` on 27 September 2026, from `D-029`'s last clause and
`T-132`'s "Before this can be ready".
