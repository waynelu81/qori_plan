---
id: T-183
title: The creator reads the invitation before it goes, and every email counts toward the day
stream: selling
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-183 — The creator reads the invitation before it goes, and every email counts toward the day

## Why

The owner's questions once `T-043` and `T-181` were built, 22 September 2026:
"Is resend count as day quota? should we show subject and content for creator
to see? test send? i preferred not / able to change subject? / able to change
email content?" Today the creator sends an email they never see, and the free
plan's ten a day counts invitations rather than emails, so one person can be
sent the same invitation again and again in a day. Afterwards the creator
reads what each person will get before sending, and every invitation email
Qori sends counts.

## Decisions taken to make this specifiable

- **No test send** (`D-053`). The owner: "test send? i preferred not." The
  preview is how the creator sees the email.

## Preconditions

None.

## Scope

**In:**

- The subject and words of the invitation, shown on the invitations page
  before sending.
- Whatever the owner decides below about changing them.
- Send again, and an address typed into the form again, counting against the
  free plan's day.

**Out:**

- A test send (`D-053`).
- Reminders Qori sends on its own (`D-053`).
- Campaigns' own daily cap, `edm_per_day`, unless the owner moves the day's
  boundary for both.

## Files

To be settled when ready.

## Database

To be settled when ready: a column for the creator's note, if the owner wants
one.

## Code

To be settled when ready.

## Copy

To be settled when ready.

## Routes

None expected.

## Tests

To be settled when ready.

## Acceptance

- [ ] The creator reads the subject and words of the invitation before sending, filled in as the first person will get them
- [ ] Every invitation email counts toward the free plan's day, Send again included, and nobody is sent the same invitation twice in one day
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- What the code does today, read 22 September 2026:
  `InvitationService::sendAgain()` refuses once the day's allowance is spent
  and moves the invitation's `sent_at` to now, and `sentToday()` counts
  invitations whose `sent_at` is today. So a Send again of one first sent on
  an earlier day takes one of today's ten, and one already sent today takes
  nothing more however often it is sent; so does an address typed into the
  form again, which `write()` replaces in place. Allowing one email per
  address per Series a day makes the count exact with no new table.
- The day is UTC's (`now()->startOfDay()`, and `app.timezone` is `UTC`), so
  in Sydney the ten come back at 10 am, or 11 am in daylight saving, while the
  page says "left today". `CampaignService::guardDailyCap()` counts the same
  way. Whether the day becomes the Group's own, from `Group::timezone()`, and
  campaigns' with it.
- _Asked_, recommended: **every email counts.** Send again takes one of the
  day's ten, and an address sent its invitation today is not sent another
  until tomorrow, which also stops one person being emailed over and over.
- _Asked_, recommended: **the creator sees the email.** Subject and body,
  read-only, rendered from `InvitationNotification` itself so the preview
  cannot drift from what is sent, filled with the first row's name and price
  and the chosen expiry.
- _Asked_, recommended: **the subject stays Qori's**, ":name invited you to
  :title". It is what a recipient and a spam filter judge first, the Group's
  name and the Series' title already make it theirs, and a free-text subject
  from Qori's own domain is the easiest way to make Qori's mail look like
  phishing. That reputation is shared by every Group and by every sign-in
  code.
- _Asked_, recommended: **the words stay Qori's, with room for a note from
  the creator.** Plain text, one per batch, its length in config, shown in the
  email under the creator's name as theirs, with links left as text, and kept
  on each invitation so Send again carries it. The facts — price, expiry, the
  link, whose address it is for — stay Qori's, so a note cannot say "free"
  over an invitation priced at A$89.

## Re-scope log

None.

## Notes

Recorded with `D-053`. The email-cost estimate given to the owner the same
day counts invitations at the free plan's cap, 300 a month a Group.
