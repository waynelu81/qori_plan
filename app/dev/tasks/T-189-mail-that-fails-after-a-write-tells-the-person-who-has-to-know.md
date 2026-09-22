---
id: T-189
title: Mail that fails after a write tells the person who has to know
stream: delivery
status: draft
owner: unassigned
estimate: M
depends: none
blocks: none
---

# T-189 — Mail that fails after a write tells the person who has to know

## Why

`T-187` made the "you're in" email survive a provider that is down: the access
is written, the failure is reported, and nobody is told, because nothing on
the Peer's side went wrong. Three other sends have the same shape and cannot
take the same answer — somebody is waiting on each of them.

- **`InvitationService::send()`** writes every row in one transaction and then
  mails them one at a time. A provider that refuses the third of five leaves
  five rows saying `sent_at`, five counted against the day's allowance, two
  emails delivered and the creator on an error page that does not say which.
  Nothing on the invitations page distinguishes a row that went from one that
  did not.
- **`InvitationService::sendAgain()`** replaces the token before it mails, so
  a failed send has already stopped the link the invitee was holding. They are
  left with a dead link and no new one, and the creator is told only that
  something failed.
- **`CampaignService::send()`** sends per recipient inside a loop whose own
  comment says "a bad address should cost that recipient, not the rest of the
  list" — and there is no catch, so a throw ends the loop. The campaign is
  left `sending`, the untried recipients have no row, and `send()` refuses it
  from then on because it is no longer a draft. There is no way back to it
  from the UI.
- **`EmailChangeService::confirm()`** swaps the address and then tells the old
  one. A failure answers an error page for a change that has happened and
  cannot be undone by the person reading it.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

## Scope

**In:**

- A failed send after the write it follows, at the four sites above.

**Out:**

- The "you're in" email (`T-187`, done).
- Retrying or queueing anything. Nothing is `ShouldQueue` until a worker
  exists.
- Mail sent before a write, such as a sign-in code, where failing the request
  is the right answer.

## Files

To be settled when ready.

## Database

Possibly: a `campaigns` row needs a way back from `sending`, and an
invitation may need to record that its last send did not go.

## Code

To be settled when ready.

## Copy

Expected: what the creator sees when an invitation or a campaign did not go
out.

## Routes

None expected.

## Tests

To be settled when ready.

## Acceptance

- [ ] A send that fails after its write leaves the write standing, reports the failure, and tells whoever is waiting on that message
- [ ] A campaign a provider refused halfway can be finished or sent again, and says what happened
- [ ] An invitation that did not go is visible as one on the invitations page, and can be sent again
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **Where a creator sees a message that did not go.** `T-129` asks the same
  of the recording email; the two should answer it once, and this is the task
  that has three more senders behind the question.
- **Whether a failed invitation gives the day's allowance back.**
  `remainingToday()` counts rows by `sent_at`, so today a refused send still
  spends one of the free plan's ten.
- **`sendAgain()`'s ordering.** Mint the new token only once the mail has
  gone, or keep the old one working until the new link is used. The first is
  smaller; the second is kinder to someone who clicks the old link.
- **A campaign's way back from `sending`.** Finish the remaining recipients,
  or mark it failed and let the creator send it again to the ones with no row.
- **Whether the email-change notice is worth telling anyone about.** The
  change is done and the new address works; the old address is the one that
  cannot be reached.
- **Whether three or four sites earn a shared way to send after a write.**
  `T-187` deliberately wrote one `try`/`catch` rather than a helper for a
  single caller.

## Re-scope log

None.

## Notes

Found while building `T-187`, 23 September 2026.
