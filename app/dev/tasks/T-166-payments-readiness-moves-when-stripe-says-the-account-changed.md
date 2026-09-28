---
id: T-166
title: Payments readiness moves when Stripe says the account changed
stream: selling
status: done
owner: claude
estimate: S
depends: T-164
blocks: none
---

# T-166 — Payments readiness moves when Stripe says the account changed

## Why

`T-164` remembers on `groups.payments_readiness` whether Stripe will take
payments for a Group's account, and the dashboard and the price field read it
there. It moves only when Qori reads the account — on Integrations, at the
connect landing, or when the local end-to-end run adopts one. So a creator who
finishes Stripe's steps keeps seeing "Stripe can't take payments for you yet"
on the dashboard until they open Integrations, and an account Stripe restricts
later is not noticed until then either. Stripe announces both with
`account.updated` on the Connect endpoint, which `StripeWebhookController`
acknowledges and ignores today (`docs/flows/billing.md`, "Not built yet").
Afterwards the event re-reads the account and the readiness moves on its own.

## Decisions taken to make this specifiable

Brought to ready on 28 September 2026, from the code and Stripe's documents.

**The event is a cue, and the account is read again.** Stripe "doesn't
guarantee the delivery of events in the order that they're generated"
([docs.stripe.com/webhooks](https://docs.stripe.com/webhooks), Event ordering),
so the account inside one `account.updated` can be older than a state already
remembered: a late event from the middle of sign-up would move a ready account
back to "can't take payments yet". A read is the account as it is now. It is
also the read Integrations makes, account and `card_payments` capability
together, so the dashboard and Integrations cannot disagree about one account.
Nothing in the body is believed but the account id, which the signature
(`T-188`) vouches for, so `T-114`'s trust question does not arise here.

**One read serves every Group holding the id, and an id no Group holds costs
no call.** `groups.connect_account_id` is not unique, which is why `forget()`
clears every Group holding one; `refresh()` reads once and remembers the answer
on each. An event for an account Qori has let go of reads nothing.

**A read that fails is left for Stripe to send again.** `Client::unwrap()`
throws `upstream_unavailable`, and the delivery gets no 2xx — Stripe counts a
redirect as a failure too — so Stripe retries it, for up to three days in live
mode, and the retry reads the account as it is then. Acknowledging a failed
read instead would leave the readiness stale until the creator next opened
Integrations, which is the defect.

**The Connect endpoint subscribes to `account.updated`.** `T-188` named its
events and left this one for this task. `stripe listen --forward-connect-to`
forwards every event, so local runs need nothing new.

**How often it comes.** Stripe sends it whenever a connected account's
requirements or capabilities change, and tells platforms to watch it for
exactly that ([Handle verification with the
API](https://docs.stripe.com/connect/handling-api-verification)): several
times while a creator signs up, rarely after. Each costs one read, and a
second only while the account cannot charge.

## Preconditions

None.

**Data this task verifies against:** a clean database; the tests build the
Groups and sign the events themselves.

**Equipment:** none for the tests. A real delivery needs a sandbox connected
account and `stripe listen --forward-connect-to` running against the dev
server.

## Scope

**In:**

- `account.updated` for a connected account re-reads it through
  `PaymentsService`, so its readiness moves.
- `release-prerequisites.md`'s live-mode step: the Connect endpoint's events
  gain `account.updated`.

**Out:**

- Telling the creator by email when payments stop: a product call for later.

## Files

| Path                                               | Change | Notes                                                             |
| -------------------------------------------------- | ------ | ----------------------------------------------------------------- |
| `app/Http/Controllers/StripeWebhookController.php` | edit   | `account.updated` → `PaymentsService::refresh()`                  |
| `app/Services/PaymentsService.php`                 | edit   | `refresh()`; what a read leaves on a Group moves into `remember()` |
| `tests/Feature/Share/PaymentsReadinessTest.php`    | edit   | 5 cases                                                           |
| `docs/flows/billing.md`                            | edit   | the webhook's dispatch, readiness, and "Not built yet"            |
| `docs/tinker/e2e-first-share.md`                   | edit   | the event moves the readiness too                                 |

## Database

None.

## Code

```php
// App\Services\PaymentsService
/**
 * Stripe said an account changed: read it again, once, and remember what the
 * read found on every Group holding the id. An id no Group holds costs no call.
 *
 * @return int Groups read for
 */
public function refresh(string $accountId): int;
```

`StripeWebhookController` hands it `$event['account']` for `account.updated`
and answers `['handled' => 'account.updated']`, as it does for
`account.application.deauthorized`.

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/Share/PaymentsReadinessTest.php` — 5 new cases**,
each an `account.updated` signed with the Connect secret to the Connect URL,
with Stripe's reads faked from the fixtures:

1. `test_stripe_saying_the_account_changed_moves_its_readiness` — `incomplete`
   becomes `ready`.
2. `test_an_older_event_arriving_late_cannot_move_it_back` — the event carries
   the unfinished account, Stripe's read the ready one; the readiness stays
   `ready`.
3. `test_every_group_holding_the_account_moves_on_one_read` — two Groups, one
   request to Stripe.
4. `test_an_account_no_group_holds_is_acknowledged_without_a_call`.
5. `test_a_read_that_fails_is_left_for_stripe_to_send_again` — no 2xx, and the
   readiness unchanged.

## Acceptance

- [x] `account.updated` moves the readiness of every Group holding that account
- [x] `release-prerequisites.md` names `account.updated` among the Connect endpoint's events
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Re-read the account, or read the event's own object: the event carries the
  v1 account, but trusting a body over a read is `T-114`'s open trust question.~~
  **Answered 28 September 2026:** re-read (Decisions).
- ~~Whether the Connect endpoint is subscribed to `account.updated`: that is the
  platform's webhook configuration, a release checklist item, and local runs
  need `stripe listen` to forward it.~~ **Answered 28 September 2026:** it is
  added to `release-prerequisites.md`'s live-mode step, and `stripe listen`
  forwards it already (Decisions).
- ~~How often Stripe sends it for one account, since each one would cost two
  Stripe calls.~~ **Answered 28 September 2026:** on each change to the
  account's requirements or capabilities (Decisions).

## Re-scope log

None.

## Notes

None.
