---
id: T-186
title: The "you're in" email sends on the broadcast mailer
stream: delivery
status: ready
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-186 — The "you're in" email sends on the broadcast mailer

## Why

`SeriesAccessNotification`, the "you're in" email, goes through Postmark with
the sign-in codes and magic links, at $1.20 per 1,000 past Postmark's first
10,000. It is the one Postmark message that is not a step in something a
person is doing that minute, so the owner moved it to the broadcast side on
22 September 2026 (`D-054`): SES, at $0.10–0.16 per 1,000, from the campaign
domain. Afterwards it sends on `qori.mail.broadcast` from
`qori.mail.broadcast_from`, and still reaches everyone who gains access:
consent, unsubscribes and complaints stop campaigns, not this.

## Decisions taken to make this specifiable

- **Only the "you're in" email moves** (`D-054`). Sign-in codes, magic links,
  verification, password resets, email changes and invitations stay on the
  default mailer. An invitation that silently does not arrive is worse than
  none, and it is the email that gets a person in.
- **Moving provider does not make it marketing.** It is still sent on every
  new or restored access, whatever the Peer's consent, unsubscribe or
  `marketing` suppression — `docs/flows/campaigns.md`, "Transactional mail is
  not a campaign". Only an `all` suppression stops it: a permanent bounce,
  where the mailbox does not exist, and a bounce rate is what SES reviews an
  account on. `docs/flows/campaigns.md` already says `all` stops
  "Everything, transactional included", and nothing implements that today:
  `SuppressionService::blockedForTransactional()` has no caller. This makes
  it true for this email; the others are out of scope.
- **Until the broadcast mailer is set up, it stays on the default.**
  `qori.mail.broadcast` is `log` wherever SES is not configured — locally,
  in the e2e runs, and in production today — and a "you're in" email written
  to a log is one a Peer never gets. So the message leaves the default mailer
  only when the broadcast mailer is not `log`. Campaigns do not fall back: a
  campaign must never reach the transactional provider. Locally the email
  still lands in Mailpit, so `invited-peer.spec.ts` keeps following it with no
  change.
- **It sends from the broadcast address under Qori's own name, and replies
  go where they go today.** SES sends only from an identity verified in it,
  which is the `mail.` subdomain, so the address changes with the mailer. The
  name stays `mail.from.name`, because the email is Qori's rather than a
  creator's campaign, and `replyTo` is `mail.from.address`, so a Peer's reply
  reaches the same place as before. On the default mailer nothing changes,
  since Postmark accepts only its verified senders.
- **The service decides whom to mail, the notification how.** The bounce
  check sits in `AccessService::announce()`, beside the call it guards, as
  `CampaignService::send()` checks `blockedForMarketing()` before it sends.

## Preconditions

None.

**Data this task verifies against:** A clean database.

**Equipment:** A Mailpit on 1025/8025 for the e2e journey. Another project's
container may be the one holding the port; `qori:e2e` reads without emptying
it. Never run `qori:mail:check` here, which empties it (`T-162`).

## Scope

**In:**

- `SeriesAccessNotification` choosing the broadcast mailer and address when
  one is configured.
- `AccessService::announce()` skipping an address suppressed for everything.
- The tests, config comments and docs that say campaigns are the only email
  off the default mailer.

**Out:**

- Setting SES up in production: production access, the `mail.` identity,
  `QORI_MAIL_BROADCAST=ses`, and an account-level suppression list that
  suppresses bounces only. Release checklist, in
  `app/dev/release-prerequisites.md` (`D-054`).
- Queuing the email. Nothing is `ShouldQueue` until a worker exists.
- Invitations and every other notification.
- A bounce check before any other transactional email.

## Files

| Path                                             | Change | Notes                                                                                              |
| ------------------------------------------------ | ------ | -------------------------------------------------------------------------------------------------- |
| `app/Notifications/SeriesAccessNotification.php` | edit   | broadcast mailer, `broadcast_from` under `mail.from.name`, `replyTo` `mail.from.address`, unless `log` |
| `app/Services/AccessService.php`                 | edit   | `SuppressionService` injected; `announce()` returns early on an `all` suppression                  |
| `app/Notifications/CampaignNotification.php`     | edit   | docblock: no longer "the only notification that leaves the default mailer"                        |
| `config/qori.php`                                | edit   | the `mail` comment: the "you're in" email opts out as well, and stays on the default while `log`   |
| `.env.example`                                   | edit   | the campaign mail comment's "(magic links, receipts, access)"                                      |
| `tests/Feature/Campaigns/MailSeparationTest.php` | edit   | the transactional example becomes `LoginCodeNotification`; three cases below                       |
| `tests/Feature/Access/AccessServiceTest.php`     | edit   | two cases below                                                                                    |
| `docs/flows/campaigns.md`                        | edit   | "the only notification in the app that sets its own mailer", and the transactional list           |
| `docs/flows/accesses.md`                         | edit   | the access email's mailer, its fallback while `log`, and the bounce check                          |
| `docs/tinker/mail.md`                            | edit   | "Every transactional message": the "you're in" line is on the broadcast mailer where one is set    |

## Database

None.

## Code

```php
namespace App\Services;

class AccessService
{
    public function __construct(
        private CurrentGroup $current,
        private SuppressionService $suppressions,
    ) {}

    // Returns before notifying when
    // $this->suppressions->blockedForTransactional([$user->email]) is not empty.
    private function announce(Access $access, Series $series, User $user, Group $group): void;
}
```

```php
namespace App\Notifications;

class SeriesAccessNotification extends Notification
{
    // Unchanged lines, then, when config('qori.mail.broadcast') !== 'log':
    //   ->mailer((string) config('qori.mail.broadcast'))
    //   ->from((string) config('qori.mail.broadcast_from'), (string) config('mail.from.name'))
    //   ->replyTo((string) config('mail.from.address'), (string) config('mail.from.name'))
    public function toMail(User $notifiable): MailMessage;
}
```

## Copy

None. The email's words do not change.

## Routes

None.

## Tests

**Changed: `tests/Feature/Campaigns/MailSeparationTest.php` — 1 changed, 3 new**

1. `test_transactional_mail_stays_on_the_default_mailer` — built from
   `LoginCodeNotification` now: a sign-in code is the message the split
   protects.
2. `test_the_access_email_leaves_the_default_mailer` — `qori.mail.broadcast`
   `ses` gives the message mailer `ses`.
3. `test_the_access_email_sends_from_the_broadcast_domain_under_qoris_name` —
   `from` is `broadcast_from` with `mail.from.name`, and `replyTo` is
   `mail.from.address`.
4. `test_the_access_email_stays_on_the_default_mailer_while_broadcast_is_the_log`
   — with `log`, the message's mailer is null and `from` is empty.

**Changed: `tests/Feature/Access/AccessServiceTest.php` — 2 new**

1. `test_a_permanent_bounce_stops_the_access_email` — an `all` suppression on
   the address: granting sends nothing.
2. `test_a_complaint_does_not_stop_the_access_email` — a `marketing`
   suppression: granting sends it.

Five new, one changed. `MailContentTest` keeps its sender map unchanged, and
`test_the_default_and_broadcast_mailers_are_not_the_same` stays as it is.

## Acceptance

- [ ] With `QORI_MAIL_BROADCAST=ses`, the "you're in" email uses the broadcast mailer, sends from `QORI_MAIL_BROADCAST_FROM` under `MAIL_FROM_NAME`, and replies to `MAIL_FROM_ADDRESS`
- [ ] With `QORI_MAIL_BROADCAST=log`, it stays on the default mailer and address, and `php artisan qori:e2e --only="invited-peer"` still follows it from Mailpit
- [ ] A permanent bounce stops it; a complaint, an unsubscribe and no consent do not
- [ ] Every other notification stays on the default mailer
- [ ] `docs/flows/campaigns.md` and `docs/flows/accesses.md` say which mailer it takes and when
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

At the email-cost estimate given to the owner on 22 September 2026 —
10,000 free creators — this is about 50,000 emails a month: $60 on Postmark,
$5–8 on SES. It is 7% of what Postmark carries today and 18% once `T-185` and
the other cuts land.

Until SES has production access, keep `QORI_MAIL_BROADCAST` unset or `log` in
production. In the sandbox SES refuses every address not verified in it, so
`ses` there would fail every "you're in" email rather than fall back.
