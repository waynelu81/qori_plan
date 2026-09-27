---
id: T-209
title: The chat message carries the Series' public link
stream: classroom
status: doing
owner: claude
estimate: S
depends: T-135
blocks: none
---

# T-209 — The chat message carries the Series' public link

## Why

`T-135` built the message a creator copies for the class chat with the
Episode's own address and nothing else, and asked whether it should also carry
the Series' public page, for somebody in the chat who has no access yet. On
27 September 2026 the owner answered yes. Afterwards each message ends with a
line pointing such a person at the public page, while there is one to point
at.

## Decisions taken to make this specifiable

**One line of its own, after the state's message, while the Series is
published.** The public page resolves only for a published Series
(`Series::findPublic()`), so a draft's or an archived Series' message would
carry a dead link; the creator's share link is withheld on the same test
(`SeriesController::show()`'s `share.url`). The line is a whole sentence in
lang, `live.chat_message.public`, joined to the message with a newline, so
each state keeps one value and none needs a twin that differs by a line.

**Every state that has a message carries it.** Somebody new to the chat
reads a cancellation or a recording notice as much as a schedule, and one
rule is easier to trust than three.

**The address is `series.public`, built with the Group's slug and the
Series', as the share link builds it.** Never the meeting link (`D-024`).

## Preconditions

None.

**Data this task verifies against:** a clean database, as
`SessionChatMessageTest` builds it: a Melbourne Group, a published Series
with one live Episode.

**Equipment:** None; the copy control is `T-135`'s and unchanged.

## Scope

**In:**

- `SessionChatMessage::for()` appends `live.chat_message.public` while the
  Series is published.
- `lang/en/live.php`: `chat_message.public`.
- The flow and the tinker recipe, which print the message.

**Out:**

- Anything else in the message, the copy control, and when a row offers it.

## Files

| Path                                              | Change | Notes                            |
| ------------------------------------------------- | ------ | -------------------------------- |
| `app/Support/SessionChatMessage.php`              | edit   | the public line, while published |
| `lang/en/live.php`                                | edit   | `chat_message.public`            |
| `docs/flows/live-sessions.md`                     | edit   | "Copying a message for the chat" |
| `docs/tinker/live-sessions.md`                    | edit   | the printed messages             |
| `tests/Feature/Series/SessionChatMessageTest.php` | edit   | three cases change, two new      |

## Database

None.

## Code

```php
// App\Support\SessionChatMessage::for(), after the state's message:
// while $series->isPublished() and it has a Group,
//   $message."\n".__('live.chat_message.public', [
//       'series_title' => $series->title,
//       'public_url' => route('series.public', ['group' => $group->slug, 'series' => $series->slug]),
//   ])
```

## Copy

| Key                        | File               | English                                                |
| -------------------------- | ------------------ | ------------------------------------------------------ |
| `live.chat_message.public` | `lang/en/live.php` | Not in :series_title yet? Get access here: :public_url |

"Get access" is what the public page's button says. No noun placeholder, so
`__()`; no "a" or "an" before one.

## Routes

None. `series.public` exists.

## Tests

**Changed: `tests/Feature/Series/SessionChatMessageTest.php`** — cases 1 to 3
expect the public line after each message, and case 4's expected lines gain
it.

**New, in the same file — 2 cases:**

1. `test_the_public_link_is_the_page_that_resolves` — the last line's address,
   followed as a guest, answers the public Series page.
2. `test_a_series_not_published_carries_no_public_link` — the Series
   archived: the message is the state's alone.

## Acceptance

- [ ] A published Series' chat message ends with the public page's address
- [ ] A draft or archived Series' message carries none
- [ ] The address in the message is the page that resolves
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

From the owner's answer of 27 September 2026 to `T-135`'s question, which
`decisions.md` records.
