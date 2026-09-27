---
id: T-162
title: Mail check stops emptying the shared inbox
stream: workflow
status: doing
owner: claude
estimate: S
depends: none
blocks: none
---

# T-162 — Mail check stops emptying the shared inbox

## Why

`php artisan qori:mail:check` calls `App\Support\Mailpit::clear()`, which
deletes every message in the Mailpit on 1025/8025 — and on the owner's machine
that Mailpit belongs to another project, whose container holds the ports so
`qori-mailpit` cannot start. Each run wipes that project's mail. `T-161` took
the same call out of `qori:e2e` (`D-045`): its journeys read their own
recipients and, for an address that repeats, only messages that arrived after
the step that sent them. Afterwards `qori:mail:check` deletes nothing either.

## Decisions taken to make this specifiable

Brought to ready on 27 September 2026, from the code.

**The run reads only what it sent: messages to its own four addresses whose
ids were not there when it started.** Every message goes to one of
`mail-check@qori.test`, `mail-check-peer@qori.test`,
`mail-check-moved@qori.test` and `mail-check-invited@qori.test` — the last is
the invitation's, and not one of `SCRATCH_EMAILS`, which are the accounts the
run creates — so the command names them once as `INBOXES`. It takes the ids
those addresses already hold before sending, as `inboxOf()` does in
`tests/e2e/support/mailpit.ts`, and waits for `EXPECTED` new ones. No clock is
compared, for the same reason `T-161` gives: a Docker VM's clock can drift.
Addresses are matched case-insensitively, on the client, as the e2e twin
matches them.

**`clear()` goes.** Nothing else calls it, and a method that empties a shared
inbox should not be one call away.

**The wait counts polls, through Laravel's `Sleep`.** Forty polls a quarter of
a second apart are the ten seconds `waitFor()` waited, and `Sleep::fake()`
lets a test run the whole command in no time. A wall-clock deadline would spin
for real seconds under a faked sleep.

**The command is tested with a faked Mailpit.** It needs a container to run
for real, and `MailContentTest` already judges the content without one; this
test fakes the Mailpit API with an old run's message and another project's
already in it, fakes the notifications, and asserts the run deletes nothing
and reads only its own fourteen.

**`--keep` keeps the scratch rows only.** The inbox is always left alone now,
so the option and its line say so.

## Preconditions

None. The tests fake Mailpit; the real run needs Mailpit on the ports
`.env` names, as before.

**Data this task verifies against:** a clean database for the tests; for the
real run, a private Mailpit and a freshly migrated `_testing` database, as
`T-138` ran it.

**Equipment:** Docker, for the real run.

## Scope

**In:**

- `qori:mail:check` reads only what it sent, by recipient and by the message
  ids already there before it sends, as `tests/e2e/support/mailpit.ts` does.
- `Mailpit::clear()` removed.

**Out:**

- A Mailpit of Qori's own on dedicated ports, as Postgres has 5433. A larger
  change to `compose.yaml` and every developer's `.env`.
- What the command checks in each message (`MailContent`), which is unchanged.

## Files

| Path                                             | Change | Notes                                        |
| ------------------------------------------------ | ------ | -------------------------------------------- |
| `app/Support/Mailpit.php`                        | edit   | `idsTo()`, `waitForNew()`; `clear()` removed |
| `app/Console/Commands/MailCheckCommand.php`      | edit   | `INBOXES`; reads only the new messages       |
| `docs/tinker/mail.md`                            | edit   | the inbox is left as it was                  |
| `tests/Feature/Console/MailCheckCommandTest.php` | new    | 3 cases                                      |

Flows: none — a developer command; no call chain in `docs/flows` changes.

## Database

None.

## Code

```php
// app/Support/Mailpit.php — the class docblock gains: nothing here deletes
// anything, because the Mailpit on 1025/8025 may be another project's (T-162).

/**
 * The ids of what these addresses hold now: a run's baseline.
 *
 * @param  list<string>  $to
 * @return list<string>
 */
public function idsTo(array $to): array;

/**
 * Messages to $to that $after does not name, newest first, polling until
 * $count have arrived or $seconds have passed. Returns what arrived, fewer than
 * $count on a timeout, so the caller can say how many did.
 *
 * @param  list<string>  $to
 * @param  list<string>  $after
 * @return list<array<string, mixed>>
 */
public function waitForNew(array $to, array $after, int $count, int $seconds = 10): array;
// four polls a second through Sleep::for(250)->milliseconds(); never deletes

/** @return list<array<string, mixed>> */
private function messagesTo(array $to): array;   // messages() filtered on To[].Address, case-insensitively
```

```php
// app/Console/Commands/MailCheckCommand.php
/** Every address a message goes to: the three accounts, and the invitation's. */
private const INBOXES = [
    'mail-check@qori.test',
    'mail-check-peer@qori.test',
    'mail-check-moved@qori.test',
    'mail-check-invited@qori.test',
];

// handle(): $before = $mailpit->idsTo(self::INBOXES) in place of clear();
// $arrived = $mailpit->waitForNew(self::INBOXES, $before, self::EXPECTED);
// count($arrived) < EXPECTED → "Expected 14 messages, saw N."; inspect($mailpit, $arrived)
// --keep: 'Leave the scratch rows in place'; cleanUp() says "Kept the scratch rows."
```

## Copy

None. Console output aimed at a developer is a diagnostic, not copy.

## Routes

None.

## Tests

**New: `tests/Feature/Console/MailCheckCommandTest.php` — 3 cases** (`MAIL_MAILER`
set to `smtp` in config, `Notification::fake()` and `Mail::fake()` so nothing
leaves, `Sleep::fake()`, and `Http::fake()` for Mailpit's `info`, `messages`
and `message/{id}`: the list answers first with the baseline — an old run's
message to `mail-check@qori.test` and another project's — and afterwards with
those plus fourteen new ones to the four inboxes)

1. `test_it_deletes_nothing_and_reads_only_what_it_sent` — exit 0, "All 14
   render"; no `DELETE` reaches Mailpit; `message/{id}` is asked for the
   fourteen new ids and never for the old run's or the other project's.
2. `test_it_says_how_many_arrived_when_some_do_not` — thirteen new: exit 1,
   "Expected 14 messages, saw 13.", and still no `DELETE`.
3. `test_it_matches_an_inbox_whatever_the_case` — one of the fourteen
   addressed `Mail-Check-Peer@QORI.test`: it is read.

**Changed:** none.

## Acceptance

- [ ] `qori:mail:check` leaves every message it did not send where it was
- [ ] A real run against a Mailpit holding other mail reads its own fourteen
      and leaves the rest
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~How `waitFor(count)` changes when the inbox is not empty at the start:
  baseline ids from `Mailpit` before sending, then wait for that many new
  ones. Anyone's, from the code.~~ **Answered from the code, 27 September
  2026:** as proposed, by recipient as well as by id, over the command's four
  inboxes (Decisions).

## Re-scope log

None.

## Notes

Found while designing `T-161`'s credentials, 21 September 2026. The shared
Mailpit reported 95 accepted and 89 deleted that day, so the other project
deletes too: a message can vanish while a run waits for it.
