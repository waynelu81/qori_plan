---
id: T-043
title: Invite people to a Series, ten at a time
stream: selling
status: done
owner: claude
estimate: L
depends: T-032
blocks: T-181
---

# T-043 — Invite people to a Series, ten at a time

## Why

`PLAN.md` calls Qori "an invitation-led knowledge-sharing product". **There are
no invitations.**

`AccessController::store()` takes an email address, looks for a `User` with it,
and refuses when there is none. Its own comment says why and says what is
missing:

> Access grants access to episodes, and access needs somewhere to sign in to —
> so this path only adds people who already have an account. The §4 funnel
> reaches everyone else through an EDM invitation instead, and that flow is not
> built yet, so say so rather than half-grant them.

That is an honest refusal rather than a bug. Its consequence is that a creator's
actual audience — a list of email addresses belonging to people who have never
heard of Qori — cannot be reached at all.

## What the owner asked for, 11 September 2026

A creator opens a Series, presses a button, and gets a page for inviting people
to **that** Series.

- **Up to ten people per batch.** Pressing **Add** appends an empty row.
- **Pasting ten addresses copied out of a spreadsheet fills ten rows.** One
  paste into the first email field, ten rows populated, not one field holding
  ten addresses separated by tabs.
- **Per person: email required; first name, last name and price all optional.**
- **A price of nothing is a real answer.** Somebody invited at no charge
  confirms and gets access without being sent to checkout.

**Yes, a Series has a price.** `series.price_cents` and `series.currency`, both
nullable, where null means free rather than zero — a deliberate distinction,
because it decides whether anybody is sent to checkout at all. The per-person
price on an invitation therefore overrides that Series price for that person,
and "0" and "leave it blank" are two different instructions.

## Decisions taken to make this specifiable

The owner's answers of 22 September 2026 are `D-050`. What follows is that
decision in this task's terms, with the 11 September decisions kept where they
still hold and marked where they changed.

**This task sends, and makes the link resolve. `T-181` accepts.** The seam is
the Series page: this task's link remembers the invitation and lands there,
exactly as a shared Series link does, and `T-181` teaches that page and the
code step, the button and checkout what an invitation changes. `T-027` keeps
the rest of its receiving journey (22 September 2026; it said `T-027` owned
all of the arrival before).

**An invitation is its own row, one per address per Series** (`D-050`). It was
to be carried on `peers` (11 September); a Peer is one per address per
*Group*, and an invitation has a price, an expiry and a link per Series, so it
is a table of its own, `invitations`. No Peer row is made until someone
accepts: `AccessService::grant()` makes it then, through `peerFor()`, which is
where that half was always meant to run.

**Access is created on acceptance, not on invitation** (11 September, kept).

**One batch is one action, and a bad row does not lose the other nine**
(11 September, kept). Ten rows validated together, reported per row, and either
all send or none do.

**Sending again replaces, and the creator sees what came before.** Each row
shows, as it is typed or pasted, whether that address already has access
(refused: there is nothing to invite them to) or was already invited, and when.
Sending to an invited address again gives it a new link, price and expiry on
the same row; the old link stops working. The invitations list offers **Send
again** and **Withdraw** per invitation. A creator sending again by hand is
re-inviting; reminders Qori sends on its own stay out (11 September's "chasing"
is still a separate decision).

**The price is prefilled and belongs to the invitation** (`D-050`). Every row
of a priced Series starts at the Series' price; the creator may change it to
0, for free, or to anything from 1 to 99,999 as a Series price may be, and a
percentage off can be applied to every row at once. Stored as `price_cents`
and `currency`, the Series' currency. A free Series invites for free and shows
no price column.

**It expires when the creator says** (`D-050`): 7, 14, 30, 60 or 90 days, 30
unless changed, or "until the last live session ends" when the Series has a
live Episode ahead, not cancelled. When a number of days runs past that
session the page says so, and sends anyway. The last session is worked out
from the Episodes (`Series::lastSessionEndsAt()`); no dates are added to a
Series.

**The link is bound to the address.** A random token, only its hash stored, in
a lowercase hex path segment; following it remembers the invitation for that
Series in the session (`InvitationPending`) and redirects to the Series page,
so the token leaves the address bar. What the page then does with it is
`T-181`'s.

**The creator vouches for the list.** A required box, "I know these people,
and they expect to hear from me", as Give access has its own; who sent is
recorded on the invitation (`invited_by_user_id`). Unlike Give access, it
records no consent to the creator's emails: the Peer answers that themselves
when they accept (`D-049`).

**"Invite", not "campaign"** (11 September, kept): transactional mail through
the default mailer, no suppression list or monthly allowance. But a free plan
may send **10 a day** (`invitations_per_day`, beside `edm_per_day`, counted
from `sent_at` since the start of the day as campaigns count theirs), and
Send again is throttled to 6 a minute. A plan's Peer cap is not checked when
sending — nobody is a Peer until they accept — and the page says how much room
is left when a plan has a cap.

**Paste.** Pasting into any email box with a newline, a tab, a comma or a
semicolon in the text fills rows from that box on, up to ten: each line is a
row, split on tabs (or commas and semicolons when there are none); the cell
that looks like an address is the email, and the other cells, in order, are
the first and last name. A column, a row and a two-column selection out of a
spreadsheet all work, and anything past ten is dropped with a line saying so.
## Preconditions

`T-032`, done: mail from `useqori.com` arrives.

**Data this task verifies against:** a clean database for the tests; the
design-review world's Harbour Lane Studio ("Reading a Room Before You Speak",
priced) for the browser walk, with the invitation sent to the local inbox.

**Equipment:** a browser, and Mailpit on 8025 — read by message, never emptied
(another project shares it).

## Scope

**In:**

- An **Invite people** panel on the Series page, linking to the invitations
  page, and the page: up to ten rows of email, first name, last name and, for
  a priced Series, price; Add and remove; paste to fill; a percentage off for
  every row; how long it lasts; the creator's box; Send.
- The `invitations` table, the rules above, and the email.
- The invitations list: address, name, price, status (Waiting, Accepted,
  Expired, Withdrawn), when sent and when it ends; Send again and Withdraw.
- The link, which remembers the invitation and lands on the Series page.
- `qori:mail:check` sends one.

**Out:**

- What the Series page, the code step, the button and checkout do with an
  invitation: `T-181`.
- Campaigns and broadcast, which are `T-045`.
- Importing a list from a file (11 September, kept).
- Reminders Qori sends by itself.
- Vouchers. A per-person price is not a code anybody types — see `T-049`.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `database/migrations/2026_09_22_000200_create_invitations_table.php` | new | the table below |
| `database/factories/InvitationFactory.php` | new | |
| `app/Models/Invitation.php` | new | `status()`, `isWaiting()`, `isFree()` |
| `app/Enums/InvitationStatus.php` | new | Waiting, Accepted, Expired, Withdrawn — worked out, not stored |
| `app/Data/InvitationRow.php` | new | one row of the batch |
| `app/Services/InvitationService.php` | new | send, send again, withdraw, the daily count |
| `app/Support/InvitationPending.php` | new | the followed link, in the session |
| `app/Support/Money.php` | new | cents and a currency as the email writes them |
| `app/Http/Controllers/Share/InvitationController.php` | new | the page, send, send again, withdraw |
| `app/Http/Controllers/InvitationLinkController.php` | new | the link in the email |
| `app/Http/Requests/Share/StoreInvitationsRequest.php` | new | per-row rules, and the rows' own refusals |
| `app/Notifications/InvitationNotification.php` | new | the email |
| `app/Models/Series.php` | edit | `invitations()`, `lastSessionEndsAt()` |
| `app/Http/Controllers/Share/SeriesController.php` | edit | the panel's URL and words |
| `app/Console/Commands/MailCheckCommand.php` | edit | sends one invitation |
| `config/qori.php` | edit | `invitations_per_day` per plan; `qori.invitations` batch, days, default |
| `routes/share/series.php` | edit | four routes |
| `routes/web.php` | edit | the link |
| `resources/js/pages/share/series/Invitations.vue` | new | the page |
| `resources/js/pages/share/series/Show.vue` | edit | the panel |
| `lang/en/invitations.php` | new | every word of it |
| `lang/en/errors.php` | edit | `invitations.*` |
| `docs/flows/invitations.md` | new | the flow |
| `docs/flows/README.md` | edit | lists it |
| `docs/tinker/invitations.md` | new | the recipe |
| `docs/tinker/README.md` | edit | lists it |
| `tests/Feature/Invitations/SendInvitationsTest.php` | new | |
| `tests/Feature/Invitations/ManageInvitationsTest.php` | new | the list, send again, withdraw |
| `tests/Feature/Invitations/InvitationLinkTest.php` | new | |

## Added during execution

- `tests/Feature/Mail/MailContentTest.php` — its map of which service sends
  each notification is written by hand, and the new email is sent by
  `InvitationService`.

## Database

| Table | Column | Type | Null | Default | Index / constraint |
| --- | --- | --- | --- | --- | --- |
| `invitations` | `id` | `ulid` | no | | primary |
| `invitations` | `group_id` | `ulid` | no | | FK `groups`, cascade |
| `invitations` | `series_id` | `ulid` | no | | FK `series`, cascade |
| `invitations` | `email` | `varchar(255)` | no | | lowercased; unique `(group_id, series_id, email)` |
| `invitations` | `first_name` | `varchar(100)` | yes | null | |
| `invitations` | `last_name` | `varchar(100)` | yes | null | |
| `invitations` | `price_cents` | `integer` | yes | null | null: a free Series; 0: free for them |
| `invitations` | `currency` | `char(3)` | yes | null | with `price_cents` |
| `invitations` | `token_hash` | `char(64)` | no | | unique; SHA-256 of the link's token |
| `invitations` | `expires_at` | `timestamp` | no | | |
| `invitations` | `sent_at` | `timestamp` | no | | the last send; index `(group_id, sent_at)` |
| `invitations` | `accepted_at` | `timestamp` | yes | null | `T-181` writes it |
| `invitations` | `access_id` | `ulid` | yes | null | FK `accesses`, null on delete; `T-181` |
| `invitations` | `withdrawn_at` | `timestamp` | yes | null | |
| `invitations` | `invited_by_user_id` | `ulid` | yes | null | FK `users`, null on delete |
| `invitations` | `created_at`, `updated_at` | `timestamp` | yes | | `created_at` is the first invitation |

Migration: `database/migrations/2026_09_22_000200_create_invitations_table.php`

## Code

```php
class InvitationRow { public function __construct(public string $email, public ?string $firstName, public ?string $lastName, public ?int $priceCents) {} }
enum InvitationStatus: string { case Waiting = 'waiting'; case Accepted = 'accepted'; case Expired = 'expired'; case Withdrawn = 'withdrawn'; }
class InvitationService {
    /** @param list<InvitationRow> $rows @return list<Invitation> — all or none; refuses a draft Series and the daily cap */
    public function send(Series $series, User $by, array $rows, CarbonImmutable $expiresAt): array;
    public function sendAgain(Invitation $invitation, User $by): Invitation;   // a new link, as long as the first
    public function withdraw(Invitation $invitation): Invitation;
    public function remainingToday(Group $group): ?int;                        // null: no cap
}
// Series::lastSessionEndsAt(): ?Carbon — the latest ends_at of a live Episode not cancelled
// InvitationPending::remember(Invitation), ::for(Series): ?Invitation, ::forget()
// Money::format(int $cents, string $currency): string
```

## Copy

Every line in `lang/en/invitations.php`, with the Group's nouns; the page holds
no English of its own. The ones a person reads first:

| Key | English |
| --- | --- |
| `panel.title` | "Invite people" |
| `panel.description` | "Up to :batch at a time, by email, each with their own price. They get in with a code sent to them — no password." |
| `page.title` | "Invite people to :title" |
| `form.price_help` | "Prefilled with the price of this :series. 0 makes it free for them." |
| `form.expires_after` | "That is after the last live session, on :date. Whoever accepts later gets the :series without the live sessions." |
| `form.attest` | "I know these people, and they expect to hear from me." |
| `form.invited` | "Invited :date" |
| `form.has_access` | "Already has access" |
| `mail.subject` | ":name invited you to :title" |
| `mail.discounted` | "Your price is :price, instead of :listed." |
| `mail.expires` | "This invitation is for :email and works until :date." |
| `errors.invitations.daily_limit` | "Your plan sends :limit invitations a day." / "Send the rest tomorrow, or move to a paid plan to send more." |

## Routes

| Method | Path | Name | Controller |
| --- | --- | --- | --- |
| GET | `g/{group}/series/{series}/invitations` | `share.series.invitations.index` | `Share\InvitationController@index` |
| POST | `g/{group}/series/{seriesId}/invitations` | `share.series.invitations.store` | `Share\InvitationController@store` |
| POST | `g/{group}/series/{seriesId}/invitations/{invitationId}/resend` | `share.series.invitations.resend` | `Share\InvitationController@resend` |
| POST | `g/{group}/series/{seriesId}/invitations/{invitationId}/withdraw` | `share.series.invitations.withdraw` | `Share\InvitationController@withdraw` |
| GET | `s/{group}/{series}/invitation/{token}` | `series.invitation` | `InvitationLinkController` |

Withdraw is a POST, like archive: nothing is deleted.

## Tests

**`tests/Feature/Invitations/SendInvitationsTest.php`:**

1. `test_a_batch_sends_one_email_per_row_and_stores_each_invitation`
2. `test_each_row_is_prefilled_from_the_series_price_and_may_be_changed`
3. `test_a_price_of_zero_is_free_and_a_price_under_one_is_refused`
4. `test_a_free_series_invites_for_free`
5. `test_a_bad_row_refuses_the_batch_and_says_which_row`
6. `test_an_address_that_already_has_access_is_refused`
7. `test_inviting_an_invited_address_again_replaces_its_link`
8. `test_more_than_ten_rows_are_refused`
9. `test_the_creator_must_vouch_for_the_list`
10. `test_a_draft_series_cannot_be_invited_to`
11. `test_the_free_plan_sends_ten_a_day`
12. `test_it_expires_after_the_days_chosen_or_with_the_last_live_session`
13. `test_another_groups_series_cannot_be_invited_to`

**`tests/Feature/Invitations/ManageInvitationsTest.php`:**

1. `test_the_page_lists_each_invitation_with_its_status`
2. `test_sending_again_mails_a_new_link_and_the_old_one_stops_working`
3. `test_withdrawing_stops_the_link`
4. `test_the_page_shows_the_last_live_session_and_the_room_left`

**`tests/Feature/Invitations/InvitationLinkTest.php`:**

1. `test_the_link_remembers_the_invitation_and_lands_on_the_series_page`
2. `test_an_unknown_link_lands_on_the_series_page_remembering_nothing`
3. `test_the_token_is_stored_only_as_its_hash`

`MailContentTest::test_every_notification_class_is_covered_by_the_command`
holds the mail check to sending it.

## Acceptance

- [x] A creator invites up to ten people to a ready Series from its page: paste fills the rows, each price starts at the Series' and can be changed or discounted, and the page says how long the invitation lasts
- [x] Each person gets one email with their own link; an address already invited says when, and one with access is refused
- [x] The list shows every invitation's status; Send again replaces the link, Withdraw stops it
- [x] The link lands on the Series page remembering the invitation
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

Answered 22 September 2026:

- ~~**Decide whether an invitation link is single-use, and whether it expires.**~~
  Bound to the address and the Series, and it expires when the creator says
  (`D-050`). Forwarded, it is worth nothing: the code goes to the invited
  inbox.
- ~~**Decide what a price of nothing on a paid Series means for the creator's
  numbers.**~~ An Access given away, as a creator's grant is: no price, and the
  Peer counts. A discounted invitation is a sale at the price paid (`D-050`).
  `ShareDigest` needs nothing new.
- ~~Read `AccessService::peerFor()` before specifying.~~ It is `grant()`'s own,
  and `grant()` is how an accepted invitation makes its Peer (`T-181`).
- ~~Confirm the paste shape against a real spreadsheet copy.~~ All three shapes
  are supported; see **Decisions**.
- ~~**An accepted invitation lands on the Series page and lets it do the
  rest.**~~ It does: `T-181` ends on `shared.show`, as every access path does.

## Re-scope log

- 22 September 2026, **Code**: `Series::lastSessionEndsAt()` returns
  `?CarbonInterface`, not `?Carbon` — dates are immutable here. Nothing a
  person sees changes.

## Notes

`PLAN.md`'s beta gate includes "five representative creators can create and
share a Series without developer help; invited Peers understand how to get
access and continue". As things stand, those five creators can only share with
people who already have Qori accounts, so that gate cannot be attempted. This is
the largest single gap between the plan and the build.

- 22 September 2026: brought to ready by the owner's answers (`D-050`) and cut
  in two, sending here and accepting in `T-181`, which this blocks.
