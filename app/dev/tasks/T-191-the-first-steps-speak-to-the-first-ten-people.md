---
id: T-191
title: The first steps speak to the first ten people
stream: onboarding
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-191 — The first steps speak to the first ten people

> Written on 23 September 2026 from
> [the positioning note](../../design/positioning-solo-creators.md), at the
> owner's word, and made ready the same day on the owner's answer.

## Why

The dashboard's first three next actions, the price field's help and the
invitation page's intro are accurate and say nothing about who the first
Series is for. The positioning note reads the target's first move off Justin
Welsh's: put the answer to the question people keep asking in one place, at a
price that is easy to say yes to, for the few people who already ask. Today
`first_series` says the name can change later, `first_episode` lists what
counts, `first_peer` says they need an account, `price_help` says empty is
free, and the invitation intro explains the personal link.

Afterwards each line says the same thing and one thing more: start with what
people already ask you, one Episode is enough, a small price you can raise,
the first few people you would tell. No number is written: the free plan's ten
a day is `invitations.form.daily`'s `:limit`, and stays there.

## Decisions taken to make this specifiable

**Only the `detail` lines change; every `message` and `label` stays.**
`ShareDigestTest` asserts the messages by their English ("Name your first
Series", four times), and the labels are the words on the buttons. The detail
is where the page has room for a second sentence.

**The first-Peer action keeps pointing at give-access.**
`ShareDigest::nextAction()` links `first_peer` to the Series page's
`give-access` anchor. Pointing it at invitations instead changes a Service and
what a person sees, and is its own task if the owner wants it; the new detail
is written to fit the control it has.

**The number is not restated.** "Ten a day" is
`config('qori.plans.free.invitations_per_day')`, and the invitation page
already says it through `invitations.form.daily` with `:limit`. The intro says
"the first few people".

**Qori gives the price advice.** It is the one line here that takes a stance
on the creator's business rather than describing Qori's; the owner said yes
to it on 23 September 2026.

**The first-Episode line stops promising text and a link.** It says "Text, a
file, a video, a link or a live session all count", and `EpisodeType` has
four cases — file, video, audio, live — with a pasted link a provider of live
sessions only. The new line names what exists.

**The lines pass the article rule as written.** No "a" or "an" sits
immediately before a placeholder; `TerminologyTest` walks every line.

## Preconditions

**Data this task verifies against:** an owner with no Series, then one draft
Series, then one ready Series with no Peer — the three states the next action
passes through. `php artisan qori:reset basic` and a fresh registration give
the first; the Series page gives the other two.

**Equipment:** none. The lines can be read on the dashboard and the two forms
in a browser, or from the lang files.

## Scope

**In:**

- `share.next.first_series.detail`, `share.next.first_episode.detail` and
  `share.next.first_peer.detail`.
- `series.price_help`.
- `invitations.page.intro`.

**Out:**

- The messages, labels and hrefs of the next actions, and `ShareDigest`.
- The Series index page's inline empty state ("Name it below. Nothing is
  shared until you say so."), which is `T-006`'s conversion.
- The panel on the Series page, `invitations.panel.*`, which describes the
  mechanism and stays.
- The home page (`T-190`) and the pricing page (`T-104`).

## Files

| Path                      | Change | Notes                |
| ------------------------- | ------ | -------------------- |
| `lang/en/share.php`       | edit   | Three `detail` lines |
| `lang/en/series.php`      | edit   | `price_help`         |
| `lang/en/invitations.php` | edit   | `page.intro`         |

Flows: none — lang lines only.

## Database

None.

## Code

None. The keys and their readers do not change.

## Copy

| Key                               | File                      | English                                                                                                                                                                             |
| --------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `share.next.first_series.detail`  | `lang/en/share.php`       | The thing people keep asking you about is a good place to start. Nothing is shared until you say so, and the name can change later.                                                 |
| `share.next.first_episode.detail` | `lang/en/share.php`       | One is enough to share it, and the rest can come as you go. A file, a video, audio or a live session all count.                                                                     |
| `share.next.first_peer.detail`    | `lang/en/share.php`       | Start with the first few people you would tell about it. They need a Qori account with the address you give, and nobody else can see it.                                            |
| `series.price_help`               | `lang/en/series.php`      | Leave it empty to share this :series for free. Start with a price that is easy to say yes to; you can raise it later, and :peer_plural who already paid keep what they paid.        |
| `invitations.page.intro`          | `lang/en/invitations.php` | Start with the first few people you would tell about it. Each person gets an email with a link of their own. It works only for their address, so it is no use to anyone they forward it to. |

## Routes

None.

## Tests

**New:** none. The lines are read through their keys, and the conventions
assert stable fields over prose unless the prose is the behaviour under test;
the behaviour does not change.

**Changed:** none expected. `ShareDigestTest` asserts `message`, which does
not change, and `TerminologyTest`'s article walk reads the new lines by
itself. A grep on 23 September 2026 found no test asserting `price_help` or
`page.intro`; if one appears, update it and note it here.

## Acceptance

- [x] A fresh owner's dashboard shows the three next actions in turn with the
      new detail lines, and the messages and buttons unchanged
- [x] The Series form's price help and the invitation page's intro read as
      specified
- [x] No number is written in any of the five lines, and no article sits
      immediately before a placeholder
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Pointing the first-Peer next action at invitations rather than give-access,
now that `T-043` and `T-181` exist, is worth its own task; the copy here fits
the control that exists.
