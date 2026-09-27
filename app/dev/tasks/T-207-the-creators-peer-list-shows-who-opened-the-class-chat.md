---
id: T-207
title: The creator's Peer list shows who opened the class chat
stream: classroom
status: doing
owner: claude
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

Afterwards each row of the creator's Peer list says, under the address, either
"Opened the class chat on 5 Oct 2026." or "Hasn't opened the class chat yet."
while the Series has a chat, and nothing about one while it has none.

## Decisions taken to make this specifiable

Brought to ready on 27 September 2026, from the code as `T-132` built it.

**The row states the latest open of the chat the Series has now, dated.**
`access_opens` holds one row per open, with `subject_id` the chat's id and
`opened_at` its time (`SeriesChatService::open()`, `AccessOpen::record()`).
The latest open, not the first and not a count: the date answers the one
question a creator can act on — did they open it since I replaced the code —
and a second open is a Peer finding the link again, not a fact for the
creator. The date is `'j M Y'` in the Group's zone, as `chats.form.expires`
dates the code on the same page, and the line is whole in lang.

**Only the chat the Series has now counts.** Opens are read for the Series'
current chat ids. A chat removed and added again is a new row with a new id,
possibly a new group, so a Peer who opened the old one reads "Hasn't opened"
until they open the new one. An edited chat keeps its id and its opens — a
WeChat code refreshed each week is the same group — and the date says whether
an open came before the edit.

**Keyed by Access.** `AccessService::grant()` reactivates a revoked Access
rather than writing a second row, so a Peer who comes back keeps their earlier
opens, dated; nothing here needs to join on the person.

**A Peer with no open is shown as such, while the Series has a chat.** Finding
who hasn't is the reason a creator looks: admission to the chat and removal
from it are by hand (`D-029`). With no chat on the Series the rows say nothing
about one — "Hasn't opened the class chat" there would point at nothing.

**Opened, never joined.** Qori cannot see the chat, and "I've joined" is the
Peer's browser's memory that never reaches the server (`T-132`). The line says
what the log knows.

**The read sits beside its writer.** `SeriesChatService::lastOpens(Series)`
answers `[accessId => CarbonImmutable]` in one grouped query — `max(opened_at)`
per `access_id` over the Series' chat ids — addressed by the Series' Group as
`chatsOf()` is, so it reads the same in a request and in tinker. `peers()`
calls it once for the page, never per row.

## Preconditions

**Data this task verifies against:** a clean database. Each case builds a
Brisbane Group with a published Series, grants Peers through
`AccessService::grant()`, adds a chat through `SeriesChat::factory()`, and
records opens through `SeriesChatService::open()` under `$this->travelTo()`.
For the browser check, the design-review world (`docs/tinker/design-review.md`),
whose chat card was seeded by `T-132` (`CHAT0001`).

**Equipment:** a browser, to read the line on the creator's Series page.

**Spike:** none owed. Nothing here reads a vendor.

## Scope

**In:**

- `SeriesChatService::lastOpens()`.
- `SeriesController::show()`: each Peer row's `chatLine`.
- `resources/js/pages/share/series/Show.vue`: the line under the address.
- `lang/en/chats.php`: `creator.opened`, `creator.not_opened`.
- `docs/flows/chats.md`, `docs/tinker/uploads.md`.

**Out:**

- Who is in the chat. Qori calls no chat vendor (`D-029`).
- "I've joined", which is the Peer's browser's memory and never reaches the
  server (`T-132`).
- A count of opens, or a list of them. The log keeps every row for whoever
  needs one later.
- The row's existing inline English ("joined", "paid", "Remove"), which is
  §13's unwired i18n and is converted with the page.

## Files

| Path                                              | Change | Notes                                  |
| ------------------------------------------------- | ------ | -------------------------------------- |
| `app/Services/SeriesChatService.php`              | edit   | `lastOpens()`                          |
| `app/Http/Controllers/Share/SeriesController.php` | edit   | `peers()` carries `chatLine`           |
| `resources/js/pages/share/series/Show.vue`        | edit   | The Peer rows show it                  |
| `lang/en/chats.php`                               | edit   | `creator.opened`, `creator.not_opened` |
| `docs/flows/chats.md`                             | edit   | The reader of the `access_opens` rows  |
| `docs/tinker/uploads.md`                          | edit   | An open, then `lastOpens()`            |
| `tests/Feature/Series/PeerListChatOpensTest.php`  | new    | 6 cases                                |

No route changes; the page and its controller exist. `docs/flows/chats.md` is
the flow file for the Service and the controller change.

## Database

None. `access_opens` is indexed `(group_id, access_id, opened_at)`, which the
grouped read uses.

## Code

```php
// app/Services/SeriesChatService.php

/**
 * When each Peer last opened this Series' chat, keyed by Access id, for the
 * creator's Peer list (T-207). Only the chats the Series has now count: a
 * chat removed and added again is a new row, so the old one's opens do not;
 * an edited chat keeps its id and its opens, and the date says which came
 * first. Addressed by the Series' Group, as chatsOf() is.
 *
 * @return array<string, CarbonImmutable>
 */
public function lastOpens(Series $series): array;
// $chatIds = $this->chatsOf($series)->pluck('id')->map(fn ($id): string => (string) $id)->all();
// if ($chatIds === []) return [];
// return AccessOpen::query()->forGroup($series->group_id)
//     ->where('target', OpenTarget::Chat)->whereIn('subject_id', $chatIds)
//     ->groupBy('access_id')->selectRaw('access_id, max(opened_at) as last_opened_at')
//     ->pluck('last_opened_at', 'access_id')
//     ->map(fn (string $at): CarbonImmutable => CarbonImmutable::parse($at, 'UTC'))
//     ->all();
```

```php
// App\Http\Controllers\Share\SeriesController::show() — SeriesChatService is
// method-injected beside the other services; the chat list is built once and
// read twice.
$chatList = $this->chats($series, $terminology);
'peers' => $this->peers($series, $chatList === [] ? null : $chatService->lastOpens($series)),
'chats' => $chatList,

/**
 * @param  ?array<string, CarbonImmutable>  $chatOpens  null when the Series has no chat
 */
private function peers(Series $series, ?array $chatOpens): array;
// each row gains, beside wasPaid:
// 'chatLine' => $chatOpens === null ? null : (isset($chatOpens[$id])
//     ? __('chats.creator.opened', ['date' => $chatOpens[$id]->setTimezone($zone)->format('j M Y')])
//     : __('chats.creator.not_opened')),
// $zone = $series->group?->timezone() ?? Timezones::fallback()
```

```ts
// resources/js/pages/share/series/Show.vue
interface PeerSummary {
    // ...as today...
    /** Whether they opened the class chat, and when (T-207); null while the Series has none. */
    chatLine: string | null;
}
// Under the address line in each Peer row:
// <p v-if="peer.chatLine" class="text-muted-foreground text-sm">{{ peer.chatLine }}</p>
```

`docs/flows/chats.md`: a "Who opened it" section — `SeriesController::show() →
SeriesChatService::lastOpens()`, the rules above, and that the line says
"opened", never "joined". `docs/tinker/uploads.md`, in "Attach it to a chat"
before the removal: a Peer granted, `$chats->open()`, then
`$chats->lastOpens($series)` keyed by the Access.

## Copy

| Key                        | File                | English                           |
| -------------------------- | ------------------- | --------------------------------- |
| `chats.creator.opened`     | `lang/en/chats.php` | Opened the class chat on :date.   |
| `chats.creator.not_opened` | `lang/en/chats.php` | Hasn't opened the class chat yet. |

A new group, `creator`, beside `form` and `peer`. `:date` is `'j M Y'` in the
Group's zone. Neither line carries a noun, so both are read with `__()`, and
neither puts "a" or "an" before one.

## Routes

None.

## Tests

**New: `tests/Feature/Series/PeerListChatOpensTest.php` — 6 cases** (a Brisbane
Group on Start with its owner as a Collaborator, a published Series of one File
Episode, Peers granted through `AccessService::grant()`, a chat from
`SeriesChat::factory()->forSeries()`, and opens through
`SeriesChatService::open()` under `$this->travelTo()`; the creator's page from
`route('share.series.show', …)`, read at `peers.{n}.chatLine`)

1. `test_it_says_when_each_peer_last_opened_the_chat` — one Peer opens at
   `2026-10-01T22:00Z` and again at `2026-10-04T20:00Z`, the other never: the
   first reads "Opened the class chat on 5 Oct 2026." (Brisbane's day, not
   UTC's 4 October), the second "Hasn't opened the class chat yet."
2. `test_it_says_nothing_while_the_series_has_no_chat` — opens recorded, then
   the chat removed through `SeriesChatService::remove()`: every row's
   `chatLine` is null.
3. `test_an_edited_chat_keeps_its_opens_and_a_new_one_starts_afresh` — an open,
   then `update()` with a new link: still "Opened … on" the same day; then
   `remove()` and a new chat: "Hasn't opened the class chat yet."
4. `test_it_counts_only_this_series_chat` — a Peer with access to two Series
   of the Group opens the second one's chat: the first Series' row reads
   "Hasn't opened".
5. `test_a_peer_granted_again_keeps_their_open` — an open, the Access revoked
   through `AccessService::revoke()` and granted again: the row reads the same
   "Opened … on" line.
6. `test_it_reads_the_opens_once_for_the_page` — five Peers, each opening:
   the page's queries against `access_opens` number one.

**Changed:** none. `SeriesChatTest` and `OpenChatTest` assert the writer and
the chat panel, which do not change.

## Acceptance

- [ ] A creator sees, on each Peer row, whether that Peer has opened the
      class chat card, and on which day in the Group's zone
- [ ] A Series with no chat says nothing about one on its Peer rows
- [ ] A chat removed and added again starts afresh; an edited one keeps its
      opens
- [ ] `docs/flows/chats.md` describes the read, and `docs/tinker/uploads.md`
      reads it by hand
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~What the row says: that the Peer opened the chat, when they last did, or
  both; and whether a chat replaced since then counts — anyone's, from how
  `T-132` built `access_opens`' `subject_id`.~~ **Answered from the code,
  27 September 2026:** the latest open of the chat the Series has now, dated
  in the Group's zone; a chat added again starts afresh and an edited one
  keeps its opens (Decisions).
- ~~Whether a Peer with no open is shown as such, or the row says nothing —
  anyone's, weighed against the Peer list's other lines.~~ **Decided,
  27 September 2026:** shown, while the Series has a chat; nothing while it
  has none (Decisions).

## Re-scope log

None.

## Notes

Drafted by `T-132` on 27 September 2026, from `D-029`'s last clause and
`T-132`'s "Before this can be ready". The draft named
`tests/Feature/Series/SeriesChatTest.php` for the cases; they are a file of
their own, because that one tests the panel and the writer, which this task
does not change.
