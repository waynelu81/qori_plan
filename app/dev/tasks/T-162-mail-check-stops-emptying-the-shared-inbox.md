---
id: T-162
title: Mail check stops emptying the shared inbox
stream: workflow
status: draft
owner: unassigned
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

None yet.

## Preconditions

None.

## Scope

**In:**

- `qori:mail:check` reads only what it sent, by recipient and by the message
  ids already there before it sends, as `tests/e2e/support/mailpit.ts` does.

**Out:**

- A Mailpit of Qori's own on dedicated ports, as Postgres has 5433. A larger
  change to `compose.yaml` and every developer's `.env`.

## Files

| Path                                          | Change | Notes                                |
| --------------------------------------------- | ------ | ------------------------------------ |
| `app/Console/Commands/MailCheckCommand.php`    | edit   | no `clear()`; count only new ids     |
| `app/Support/Mailpit.php`                      | edit   | `clear()` goes if nothing calls it   |
| `docs/tinker/mail.md`                          | edit   | the inbox is left as it was          |

Flows: none — a developer command; no call chain in `docs/flows` changes.

## Database

None.

## Code

To be settled when ready.

## Copy

None.

## Routes

None.

## Tests

To be settled when ready.

## Acceptance

- [ ] `qori:mail:check` leaves every message it did not send where it was
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- How `waitFor(count)` changes when the inbox is not empty at the start:
  baseline ids from `Mailpit` before sending, then wait for that many new
  ones. Anyone's, from the code.

## Re-scope log

None.

## Notes

Found while designing `T-161`'s credentials, 21 September 2026. The shared
Mailpit reported 95 accepted and 89 deleted that day, so the other project
deletes too: a message can vanish while a run waits for it.
