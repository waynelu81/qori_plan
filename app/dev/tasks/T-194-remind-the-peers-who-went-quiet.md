---
id: T-194
title: Remind the Peers who went quiet
stream: classroom
status: draft
owner: unassigned
estimate: M
depends: none
blocks: none
---

# T-194 — Remind the Peers who went quiet

> **Draft.** Written on 23 September 2026 from
> [the Kajabi note](../../design/competitor-kajabi.md), proposal 7, at the
> owner's word ("yes — what's your proposition?"). The proposition is below;
> what the owner still has to say is at the bottom.

## Why

The dashboard already notices: `ShareDigest::quietAction()` counts the Peers
who started a Series and have not opened it for `qori.progress.stalled_days`,
and sends the creator to the Series page's progress section to "Review" it.
There is nothing to do there but look. §9 planned a stalled campaign for
exactly this and nothing built it; campaigns themselves are unreachable
(`T-045`).

Afterwards the progress section lists the quiet Peers and offers one button:
send each of them one email saying where they left off, with one link to the
next Episode. Only to the people who ticked the box that said the creator may
email them about this Series; once per quiet spell; counted against the plan's
email allowance; never automatic. The ones who did not tick the box are named
so the creator can reach them the way they usually do.

## Decisions taken to make this specifiable

**The creator sends it; Qori never does on its own.** Qori's honest line is
"we noticed", and a Peer who hears from their teacher unprompted is the
product; a Peer who hears from a robot on day seven is Kajabi's. Automatic
sending can be a plan lever later, as `T-138`'s reminders are.

**Consent is the existing box.** `peers.consented_at` set,
`peers.unsubscribed_at` null, and no suppression — the same test
`CampaignService` applies. A Peer with no consent is listed, not mailed.

**Once per spell.** `accesses.reminded_at`; a Peer reminded within
`stalled_days`, or active since the reminder, is not offered again.

**Metered as the creator's outbound mail.** Counted against `edm_per_day` and
`edm_per_month` through `CampaignService`'s allowance methods, so Free sends
ten a day and nothing is unbounded. This is the one decision the owner has not
confirmed — see below.

**Mail-only notification, not queued**, as `SeriesAccessNotification` is;
sent after the response on the deferred queue. Fifty Peers is the Free cap
and well inside one request.

**The unsubscribe is the campaign one.** Same route, same line, so the
Spam Act's functional unsubscribe holds and a Peer who opts out of one opts
out of both.

## Preconditions

**Data this task verifies against:** a Series with five Peers: two quiet with
consent, one quiet without, one quiet and already reminded, one active.
`php artisan qori:reset basic` and `last_activity_at` set by hand.

**Equipment:** Mailpit, to read the email and follow its link.

## Scope

**In:**

- The quiet list on the Series page's progress section: name, last opened,
  consent state, reminded date.
- One button for everyone eligible, the email, the ledger column, the meter.
- The named list of the ones without consent.

**Out:**

- Automatic sending; a schedule; a plan lever.
- Reminders per Peer chosen one at a time, until the pilot asks for it.
- Anything on the dashboard: the quiet next action keeps its "Review" label
  and href.

## Files

| Path                                                             | Change | Notes                                            |
| ---------------------------------------------------------------- | ------ | ------------------------------------------------ |
| `database/migrations/2026_09_23_000001_add_reminded_at_to_accesses.php` | new | `accesses.reminded_at`                       |
| `app/Models/Access.php`                                          | edit   | Cast; `isQuiet()`, `canBeReminded()`             |
| `app/Services/ReminderService.php`                               | new    | `quietFor(Series)`, `send(Series, User)`         |
| `app/Notifications/SeriesReminderNotification.php`               | new    | Mail only, not queued; the next Episode's link   |
| `app/Http/Controllers/Share/SeriesReminderController.php`        | new    | `store()`                                        |
| `routes/share/series.php`                                        | edit   | The `POST`                                       |
| `resources/js/pages/share/series/Show.vue`                       | edit   | The quiet list and the button, in `#progress`    |
| `lang/en/reminders.php`                                          | new    | The list, the button, the toast, the email       |
| `docs/flows/accesses.md`                                         | edit   | The reminder's chain                             |
| `tests/Feature/Share/SeriesReminderTest.php`                     | new    | Cases to be named when ready                     |

## Database

| Table      | Column        | Type      | Null | Default | Index / constraint |
| ---------- | ------------- | --------- | ---- | ------- | ------------------ |
| `accesses` | `reminded_at` | timestamp | yes  | null    | none               |

Migration: `database/migrations/2026_09_23_000001_add_reminded_at_to_accesses.php`

## Code

To be settled when ready. The shape: `ReminderService::quietFor(Series $series): Collection`
returns the quiet accesses with their Peer and eligibility;
`ReminderService::send(Series $series, User $sender): int` mails the
eligible ones, stamps `reminded_at`, counts the sends against the meter and
returns how many went.

## Copy

To be settled when ready, in `lang/en/reminders.php`. The email: subject
"Where you left off in :series"; the body names :creator, :series, the
Episode reached, one Continue, and the consent-and-unsubscribe line. The
page: the button "Send a reminder to :count", the list's states, the toast,
and the line for the ones without consent.

## Routes

| Verb   | Path                                  | Name                     | Action                            |
| ------ | ------------------------------------- | ------------------------ | --------------------------------- |
| `POST` | `g/{group}/series/{seriesId}/remind`  | `share.series.remind`    | `SeriesReminderController::store` |

## Tests

To be written when ready: the eligible are mailed and stamped, the
non-consenting are listed and not mailed, a reminded Peer is not offered
twice within the window, an active Peer is not offered, the meter refuses
past the day's allowance with the campaign's error, and an admin of another
Group gets 404.

## Acceptance

- [ ] The progress section lists the quiet Peers with consent state and last
      opened date, and names the ones who cannot be mailed
- [ ] One button sends one email each to the eligible, with a link to the next
      Episode, and the rows show the date
- [ ] Nothing is sent without consent, twice in a window, or past the plan's
      allowance
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- The proposition itself: creator-sent, consent-gated, once per spell, with
  the non-consenting named. (the owner's; put to them 23 September 2026)
- Counted against the plan's email allowance, so Free sends ten a day — or
  unmetered like `T-138`'s day-before reminders? (the owner's)
- Owner only, or admins too? (the owner's)
- Which "next Episode" the link opens: the first not completed, in order.
  (anyone's; proposed)

## Re-scope log

None.

## Notes

`T-138` and `T-140` are the same mechanism for live Episodes; whichever
lands first lends the other its notification shape.
