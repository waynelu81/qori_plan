---
id: T-194
title: Remind the Peers who went quiet
stream: classroom
status: doing
owner: claude
estimate: M
depends: none
blocks: none
---

# T-194 — Remind the Peers who went quiet

> Written on 23 September 2026 from
> [the Kajabi note](../../design/competitor-kajabi.md), proposal 7, at the
> owner's word ("yes — what's your proposition?"). Brought to ready on
> 27 September 2026 with the owner's answers of that day, reconciled with the
> code as it stands.

## Why

The dashboard already notices: `ShareDigest::quietAction()` counts the Peers
who started a Series and have not opened it for `qori.progress.stalled_days`,
and sends the creator to the Series page's progress section to "Review" it.
There is nothing to do there but look. §9 planned a stalled campaign for
exactly this — `CampaignType::Stalled` exists — and nothing built it;
campaigns themselves are unreachable (`T-045`).

Afterwards the progress section lists the quiet Peers and offers the owner one
button: send each of them one email saying where they left off, with one link
to the next Episode. Only to the people who ticked the box that said the
creator may email them; once per quiet spell; counted against the plan's email
allowance; never automatic. The ones who cannot be mailed are named, so the
creator can reach them the way they usually do.

## Decisions taken to make this specifiable

**One click, by the owner, never automatic** (the owner, 27 September 2026:
"per click manual trigger … No admin function"). Qori's honest line is "we
noticed", and a Peer who hears from their teacher is the product; a Peer who
hears from a robot on day seven is not. An admin sees the list and a line
saying the owner sends reminders; the route refuses them with
`errors.reminders.owner_only`.

**Quiet is one rule, on the model.** `Access::isQuiet(CarbonInterface $now)`:
active, not complete, and `last_activity_at` set and older than
`qori.progress.stalled_days`. `ProgressService::report()` and
`ShareDigest::quietAction()` each spell the same rule today; both call the
method instead, so the list, the count on the progress panel and the
dashboard's action cannot disagree.

**Who can be mailed is the campaign's test, in the campaign's order.** A
quiet Peer whose address is suppressed for marketing
(`SuppressionService::blockedForMarketing()`) is `blocked`; one who
unsubscribed is `unsubscribed`; one with no `consented_at` is `no_consent`
(`D-049`: the creator's email is the Peer's choice); one reminded in this
spell is `reminded`; everyone else is `remindable`. A Peer in the first three
is named, never mailed.

**Once per quiet spell, read from the campaign ledger.** A reminder is a
`Stalled` campaign with the Series' id, one per click, and a
`campaign_recipients` row per Peer mailed. A quiet Access has been reminded
this spell when such a row for its Peer and its Series was sent after its
`last_activity_at`; once the Peer comes back and goes quiet again, they can be
reminded again. No column is added: the ledger the meter already counts is
the record.

**Counted against the plan's allowance, all or nothing.** The rows are
`campaign_recipients`, so `CampaignService`'s daily cap (`edm_per_day`, ten on
Free) and monthly allowance count them with no second counter, and a campaign
sent the same day shares the cap (the owner: "it count against the daily
quota"). Both guards run before anything is sent, through a new public
`CampaignService::guardAllowance(Group, int $wanted)`, and refuse with the
campaign's own errors. A paused Group sends none (`errors.campaign.group_paused`).

**On the broadcast mailer, and on the default while that is `log` —
_asked_.** The reminder is consent-gated, metered mail, so it leaves on the
broadcast mailer and domain as campaigns do, from the creator's name. Until
SES is set up the broadcast mailer is `log` everywhere, production included
(`D-054`), and a campaign written to a log reaches nobody while the page says
"sent". `SeriesAccessNotification` meets the same gap by staying on the
default mailer while the broadcast one is `log` (`T-186`), and the reminder
does the same, bounded by the daily cap. Whether this mail may travel on the
transactional provider until SES is live is the owner's; asked 27 September
2026, and built this way meanwhile — a one-line change either way.

**The link opens the first Episode not completed, in position order**, at
its own address, `shared.episodes.show` (`D-024`); the Series page when every
Episode is completed but the Access is not marked complete.

**Mail-only notification, sent in the request, not queued**, as campaigns are:
the daily cap bounds a click to ten on Free, and nothing is `ShouldQueue`
before a real worker exists (`CLAUDE.md`). It goes to the Peer row's address
on the anonymous route, as `CampaignNotification` does, and carries the
campaign's "from" line and its unsubscribe, so an opt-out from one is an
opt-out from both.

**Every date the page shows is written on the server**, `'j M Y'` in the
Group's zone, as the chat panel's are; the list's lines are whole sentences in
`lang/en/reminders.php`, with the Peer nouns through `Terminology`.

## Preconditions

**Data this task verifies against:** a clean database for the tests: a Group
on Free with its owner and an admin, a published Series of three File
Episodes, and Peers granted through `AccessService::grant()` whose
`last_activity_at`, `completed_episode_ids` and consent are set by hand. The
browser walk uses the design-review world with one of its Peers made quiet
and put back afterwards.

**Equipment:** a private Mailpit for `qori:mail:check`, which sends the
reminder too.

## Scope

**In:**

- `Access::isQuiet()`, and `ProgressService` and `ShareDigest` reading it.
- `App\Services\QuietReminderService`: `quietFor()` and `send()`.
- `App\Data\QuietPeer`, `App\Enums\QuietPeerStatus`.
- `CampaignService::guardAllowance()`, public.
- `SeriesReminderNotification`.
- `share.series.reminders.store` and its controller.
- The quiet list and the owner's button in the progress panel, as
  `QuietPeers.vue`.
- `lang/en/reminders.php`; `errors.reminders.owner_only`.
- `qori:mail:check` sends the reminder.
- `docs/flows/campaigns.md`, `docs/tinker/mail.md`.

**Out:**

- Automatic sending; a schedule; a plan lever.
- Choosing Peers one at a time, until the pilot asks for it.
- The dashboard's quiet action, which keeps its "Review" label and link.
- Campaigns themselves, which stay unreachable (`T-045`).

## Files

| Path                                                | Change | Notes                                                             |
| --------------------------------------------------- | ------ | ----------------------------------------------------------------- |
| `app/Models/Access.php`                             | edit   | `isQuiet()`                                                       |
| `app/Services/ProgressService.php`                  | edit   | the stalled count reads `isQuiet()`                               |
| `app/Services/ShareDigest.php`                      | edit   | `quietAction()` reads `isQuiet()`                                 |
| `app/Services/CampaignService.php`                  | edit   | `guardAllowance()`, public                                        |
| `app/Services/QuietReminderService.php`             | new    | `quietFor()`, `send()`                                            |
| `app/Data/QuietPeer.php`                            | new    | one quiet Peer and whether they can be reminded                   |
| `app/Enums/QuietPeerStatus.php`                     | new    | `remindable`, `reminded`, `no_consent`, `unsubscribed`, `blocked` |
| `app/Notifications/SeriesReminderNotification.php`  | new    | mail only; the next Episode's address                             |
| `app/Http/Controllers/Share/ReminderController.php` | new    | `store()`                                                         |
| `routes/share/series.php`                           | edit   | the `POST`                                                        |
| `app/Http/Controllers/Share/SeriesController.php`   | edit   | the `reminders` prop                                              |
| `resources/js/components/series/QuietPeers.vue`     | new    | the list and the button                                           |
| `resources/js/pages/share/series/Show.vue`          | edit   | mounts it in `#progress`                                          |
| `lang/en/reminders.php`                             | new    | the list, the button, the toast, the email                        |
| `lang/en/errors.php`                                | edit   | `reminders.owner_only`                                            |
| `app/Console/Commands/MailCheckCommand.php`         | edit   | sends the reminder; `EXPECTED` 15 and public                      |
| `docs/flows/campaigns.md`                           | edit   | the reminder's chain                                              |
| `docs/tinker/mail.md`                               | edit   | fifteen messages                                                  |
| `tests/Feature/Series/QuietReminderTest.php`        | new    | 8 cases                                                           |
| `tests/Feature/Mail/MailContentTest.php`            | edit   | the notification's sender                                         |
| `tests/Feature/Console/MailCheckCommandTest.php`    | edit   | reads `EXPECTED`                                                  |

## Database

None. `campaigns` has `type`, `series_id` and `sent_at`, and
`campaign_recipients` has `peer_id` and `sent_at`, which is all the ledger
needs.

## Code

```php
// app/Models/Access.php
/** Granted, not finished, and not seen for qori.progress.stalled_days (T-194). */
public function isQuiet(CarbonInterface $now): bool;

// app/Enums/QuietPeerStatus.php
enum QuietPeerStatus: string
{
    case Remindable = 'remindable';
    case Reminded = 'reminded';
    case NoConsent = 'no_consent';
    case Unsubscribed = 'unsubscribed';
    case Blocked = 'blocked';
}

// app/Data/QuietPeer.php
final class QuietPeer
{
    public function __construct(
        public Access $access,
        public Peer $peer,
        public QuietPeerStatus $status,
        public ?CarbonImmutable $remindedAt,
    ) {}
}

// app/Services/QuietReminderService.php
class QuietReminderService
{
    public function __construct(
        private CampaignService $campaigns,
        private SuppressionService $suppressions,
        private CurrentGroup $current,
    ) {}

    /** The Series' quiet Peers, the longest quiet first. @return list<QuietPeer> */
    public function quietFor(Series $series, CarbonImmutable $now): array;

    /**
     * Mails every remindable quiet Peer, in one Stalled campaign; answers how
     * many went. Refuses anyone but the owner, a paused Group, and a send past
     * the day's or the month's allowance, before anything is sent.
     */
    public function send(Series $series, User $by, CarbonImmutable $now): int;
}

// app/Services/CampaignService.php — the two private guards, behind one public door
public function guardAllowance(Group $group, int $wanted): void;
```

```php
// POST g/{group}/series/{seriesId}/reminders → ReminderController::store()
// → QuietReminderService::send($series, CurrentUser::orFail($request), now())
// → toast Terminology::choice('reminders.sent', $count, [], $group); back()
```

`SeriesController::show()` adds `reminders`: `quiet` (each row's id, name or
email, `lastSeen` and `statusLine`, both whole lines), `remindable`, `canSend`
(`CurrentGroup::isOwner()`), the button's line for the count and the note an
admin reads. `QuietPeers.vue` renders them under the Episode bars, and
nothing when nobody is quiet.

## Copy

| Key                             | File                    | English                                                                                                      |
| ------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------ |
| `reminders.heading`             | `lang/en/reminders.php` | Gone quiet                                                                                                   |
| `reminders.intro`               | `lang/en/reminders.php` | Not back for :days days or more, and not finished.                                                           |
| `reminders.last_seen`           | `lang/en/reminders.php` | Last here :date                                                                                              |
| `reminders.status.remindable`   | `lang/en/reminders.php` | Will be reminded                                                                                             |
| `reminders.status.reminded`     | `lang/en/reminders.php` | Reminded on :date                                                                                            |
| `reminders.status.no_consent`   | `lang/en/reminders.php` | Hasn't agreed to emails from you — reach them your own way                                                   |
| `reminders.status.unsubscribed` | `lang/en/reminders.php` | Unsubscribed from your emails                                                                                |
| `reminders.status.blocked`      | `lang/en/reminders.php` | Their address can't receive email                                                                            |
| `reminders.send`                | `lang/en/reminders.php` | {1} Remind 1 :peer\|[2,*] Remind :count :peer_plural                                                         |
| `reminders.none`                | `lang/en/reminders.php` | Nobody here can be reminded right now.                                                                       |
| `reminders.counts`              | `lang/en/reminders.php` | Counts against your daily email allowance.                                                                   |
| `reminders.owner_note`          | `lang/en/reminders.php` | Only the owner sends reminders.                                                                              |
| `reminders.sent`                | `lang/en/reminders.php` | {0} Nobody to remind right now.\|{1} Reminder sent to 1 :peer.\|[2,*] Reminders sent to :count :peer_plural. |
| `reminders.mail.subject`        | `lang/en/reminders.php` | Where you left off in :series_title                                                                          |
| `reminders.mail.intro`          | `lang/en/reminders.php` | :creator noticed you haven't been back to :series_title for a while.                                         |
| `reminders.mail.next`           | `lang/en/reminders.php` | Next up: :episode_title.                                                                                     |
| `reminders.mail.action`         | `lang/en/reminders.php` | Pick up where you left off                                                                                   |
| `errors.reminders.owner_only`   | `lang/en/errors.php`    | Only the owner can send reminders. / Ask the owner to send them.                                             |

The email's greeting, "from" line and unsubscribe are `campaigns.mail.*`.
`:days` is `qori.progress.stalled_days`; `:date` is `'j M Y'` in the Group's
zone. No line puts "a" or "an" before a noun.

## Routes

| Verb   | Path                                    | Name                           | Action                      |
| ------ | --------------------------------------- | ------------------------------ | --------------------------- |
| `POST` | `g/{group}/series/{seriesId}/reminders` | `share.series.reminders.store` | `ReminderController::store` |

## Tests

**New: `tests/Feature/Series/QuietReminderTest.php` — 8 cases** (a Brisbane
Group on Free, its owner and an admin as Collaborators, a published Series of
three File Episodes, Peers granted and then made quiet by setting
`last_activity_at` ten days back; `Notification::fake()`)

1. `test_it_lists_who_went_quiet_and_whether_each_can_be_reminded` —
   remindable, no consent and unsubscribed Peers listed with their lines, the
   longest quiet first; an active and a finished Peer not listed.
2. `test_the_owner_reminds_everyone_who_can_be_in_one_click` — two mailed on
   the anonymous route, a `Stalled` campaign with the Series' id and two sent
   recipients, the toast, and the rows now "Reminded on …".
3. `test_a_peer_is_reminded_once_a_quiet_spell` — a second click mails
   nobody; activity after the reminder, then ten more days, makes the Peer
   remindable again.
4. `test_it_counts_against_the_days_allowance` — nine sent today and two
   remindable on Free: refused with `errors.campaign.daily_limit`, nothing
   sent; the reminders a send makes appear in `CampaignService::allowance()`.
5. `test_only_the_owner_can_send` — the admin's post answers 403 with
   `errors.reminders.owner_only`, nothing sent; the admin's page carries
   `canSend` false.
6. `test_the_email_opens_the_first_episode_not_finished_and_can_be_unsubscribed_from`
   — subject with the Series' title, the action at `shared.episodes.show` for
   the second Episode when the first is completed, the unsubscribe link, the
   creator's name; the broadcast mailer when it is set, the default while it
   is `log`.
7. `test_a_suppressed_address_is_named_and_never_mailed` — `blocked`, not
   mailed.
8. `test_another_groups_owner_is_not_found` — 404.

**Changed:**

- `tests/Feature/Mail/MailContentTest.php` — the sender map gains
  `SeriesReminderNotification` → `QuietReminderService`.
- `tests/Feature/Console/MailCheckCommandTest.php` — counts
  `MailCheckCommand::EXPECTED`, not fourteen.
- The existing progress and dashboard tests pass unchanged: the rule moved,
  it did not change.

## Acceptance

- [ ] The progress section lists the quiet Peers with when they were last
      here, and says which can be reminded and why the rest cannot
- [ ] The owner's one click sends one email each to the remindable, with a
      link to the next Episode, and the rows show the date
- [ ] Nothing is sent without consent, twice in a quiet spell, past the day's
      or the month's allowance, or by anyone but the owner
- [ ] `qori:mail:check` renders the reminder among fifteen
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~The proposition itself: creator-sent, consent-gated, once per spell, with
  the non-consenting named. (the owner's; put to them 23 September 2026)~~
  **Answered 27 September 2026:** a manual trigger, one click, never
  automatic. The consent gate is `D-049`'s, not this task's choice, and once
  per spell with the non-consenting named stands as proposed.
- ~~Counted against the plan's email allowance, so Free sends ten a day — or
  unmetered like `T-138`'s day-before reminders? (the owner's)~~ **Answered
  27 September 2026:** counted against the daily allowance.
- ~~Owner only, or admins too? (the owner's)~~ **Answered 27 September
  2026:** the owner only; no admin sends it.
- ~~Which "next Episode" the link opens: the first not completed, in order.
  (anyone's; proposed)~~ **Decided 27 September 2026:** as proposed
  (Decisions).

## Re-scope log

**2026-09-27 — reconciled with the code as it stands.**

- **No `accesses.reminded_at`.** The draft added a column; the campaign
  ledger already records who was mailed and when, and the meter counts it, so
  once per spell is read from `campaign_recipients` of a `Stalled` campaign
  with the Series' id.
- **`ReminderService` is `QuietReminderService`**, beside a new public
  `CampaignService::guardAllowance()`, since the two guards are private today.
- **The route is `reminders`, a collection's `POST`**, named
  `share.series.reminders.store`, not `remind`.
- **The mailer** follows `T-186`'s fallback, and the question is put to the
  owner (Decisions).
- **The flow file is `docs/flows/campaigns.md`**, which already owns the
  Stalled type, not `accesses.md`.

## Notes

`T-138` and `T-140` are the same mechanism for live Episodes; whichever
lands first lends the other its notification shape.
