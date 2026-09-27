---
id: T-212
title: A session time reads the same on the server and in the browser
stream: classroom
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-212 — A session time reads the same on the server and in the browser

## Why

`SessionTime.vue` shows a Peer a live session's time in their own zone when it
is given none (`T-027`): "Given no `timezone` the time is shown in the reader's
own zone, which is what a Peer wants", read from
`Intl.DateTimeFormat().resolvedOptions().timeZone`. That is the browser's zone.
On the server there is no reader's zone, so the page Node renders shows the
server's own: UTC on Laravel Cloud. So in production a Peer in Sydney is sent
the session at the UTC hour, and the browser then renders it at the Sydney
hour — a hydration mismatch, and for a moment the wrong time for the one thing
they have to turn up for. On the dev server the machine's zone is also the
browser's, which is why nothing has logged it.

Found on 28 September 2026 while building `T-182`, which gave the component
the reader's locale from the server and left the zone to this task, because
changing it changes what a Peer sees.

Afterwards the time a Peer is sent is the time their browser shows.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

**Data this task verifies against:** a Series with a live session, read by a
Peer whose browser's zone is not the server's.

**Equipment:** a browser whose zone can be set apart from the server's, and
its console.

## Scope

**In:**

- The zone-less time on the Peer's Series page and wherever else
  `SessionTime` is given no `timezone`.

**Out:**

- The creator's line, which names its zone (`timezone` given).

## Files

To be written when the decision below is made.

## Database

None expected.

## Code

To be written.

## Copy

None expected.

## Routes

None.

## Tests

To be written: the browser's console at a zone apart from the server's.

## Acceptance

- [ ] A Peer's session time is the same in the page the server sends and after the browser renders it
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **Which zone the server renders for a Peer who has not chosen one.** Three
  candidates: render the zone-less line only after the browser mounts, with the
  Group's line alone in the server's page; use the Peer's chosen zone
  (`auth.user.timezone`) when they have one and only then fall back; or have
  the browser tell the server its zone once, in a cookie, as the sidebar tells
  it its state. The first is the smallest and shows nothing wrong, only
  something late; the third is the only one with no moment of either. Anyone's,
  unless it changes what a Peer reads first — then the stream owner's.

## Re-scope log

None.

## Notes

None.
