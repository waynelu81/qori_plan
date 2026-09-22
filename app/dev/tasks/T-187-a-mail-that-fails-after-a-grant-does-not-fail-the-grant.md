---
id: T-187
title: A mail that fails after a grant does not fail the grant
stream: delivery
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-187 — A mail that fails after a grant does not fail the grant

## Why

`AccessService::grant()` writes the access and then sends the "you're in"
email in the same call, unqueued, so a transport that throws — a provider
outage, or SES switched on before it has production access — escapes
`grant()` after the access exists. A Peer who just typed their code gets an
error page for something that worked, and sees Open only on reloading.
`CheckoutService::fulfil()` catches only `AppException`, so the Stripe webhook
answers 500, Stripe retries, the retry finds the access and sends nothing, and
the buyer never gets the email. Postmark failures do the same today; `D-054`
adds a way for this email to fail. Afterwards a failed send is reported and
the grant answers as it would have.

## Decisions taken to make this specifiable

- **The catch is at the send, not around the grant.** It goes in
  `AccessService::announce()`, around the one `notify()` call, because that is
  the line whose failure must not reach a caller — everything the grant
  promised is already written and committed by then. Wrapping `grant()`
  instead would swallow the failures that *should* reach a caller: a peer
  limit, a locked Series, a database that went away.
- **A `Throwable`, not a mail exception.** A transport throws
  `Symfony\Component\Mailer\Exception\TransportException`, but a lang key that
  is not there throws something else, and neither is a reason to take an
  access back. The narrow catch would be the one that lets the next kind of
  failure through.
- **Reported, not shown.** `report($e)` — the logs today, Sentry when Qori
  has one. The Peer is told nothing, because nothing is wrong on their side:
  they have the access they asked for, and the page opens. The creator is
  told nothing either, for now: no surface shows a message that did not go,
  and `T-129` is already the task that asks where a creator sees one. Building
  a second answer here would mean two.
- **The email is not resent.** Nothing is `ShouldQueue` until a worker
  exists, and a synchronous retry against a provider that is down is another
  timeout on somebody's page load. What replaces it, when it matters, is
  `T-129`'s answer and a resend the creator can press.
- **Only this send moves.** `InvitationService::send()` and `sendAgain()`
  mail after their writes too, and so does `EmailChangeService::confirm()` —
  the same shape, a different answer. An invitation spent from the day's
  allowance on a link that never went is something the creator has to be
  told, and `sendAgain()` has already replaced the working link by then.
  Quietly swallowing those would turn a visible failure into an invisible
  one. They get their own task; this one is the email that is guaranteed to
  come after money or a grant.
- **Stripe stops retrying, and that is right.** Once the send cannot escape
  `grant()`, `fulfil()` records the fulfilment, marks the invitation and
  answers 200. The payment *was* fulfilled — the access exists — and today's
  retry only finds the access active and sends nothing anyway, so the 500 buys
  the buyer nothing and costs the fulfilment row and the invitation mark a
  round trip. A database failure still propagates
  (`test_a_transient_failure_still_propagates_so_stripe_retries`).

## Preconditions

None.

**Data this task verifies against:** A clean database.

## Scope

**In:**

- A failed "you're in" send after a grant.

**Out:**

- Retrying the email. There is no queue worker, and nothing is `ShouldQueue`
  until there is.
- Mail sent before anything is written, such as a sign-in code, where failing
  the request is the right answer.
- Invitations and the email-change notice, which mail after a write too and
  need the creator or the account holder told. Their own task.
- Showing a creator or staff that a message did not go (`T-129`).

## Files

| Path                                              | Change | Notes                                                               |
| ------------------------------------------------- | ------ | -------------------------------------------------------------------- |
| `app/Services/AccessService.php`                  | edit   | `announce()` catches a failed send, reports it, and returns          |
| `tests/Feature/Access/AccessServiceTest.php`      | edit   | 1 new case: the access stands and the failure is reported            |
| `tests/Feature/Checkout/PaidFulfilmentTest.php`   | edit   | 1 new case: the webhook is not failed by it                          |
| `docs/flows/accesses.md`                          | edit   | the `announce()` line and its paragraph                              |
| `docs/flows/checkout.md`                          | edit   | one sentence: a failed access email does not fail the webhook        |

## Database

None.

## Code

```php
namespace App\Services;

class AccessService
{
    private function announce(Access $access, Series $series, User $user, Group $group): void
    {
        // Unchanged: the suppression check returns first.

        try {
            $user->notify(new SeriesAccessNotification($access, $series, $group->name));
        } catch (Throwable $e) {
            report($e);
        }
    }
}
```

## Copy

None. Nobody is told anything new.

## Routes

None.

## Tests

**Changed: `tests/Feature/Access/AccessServiceTest.php` — 1 new**

1. `test_a_failed_send_does_not_undo_the_access` — the mail factory hands back
   a mailer that throws `TransportException`; `grant()` returns, the access is
   active, and `Exceptions::assertReported()` sees the failure.

**Changed: `tests/Feature/Checkout/PaidFulfilmentTest.php` — 1 new**

1. `test_a_failed_access_email_does_not_fail_the_payment` — the same mailer,
   through `fulfil()` with an invitation in the metadata: an Access comes back,
   the `payment_fulfilments` row says `granted`, the invitation is accepted,
   and the failure is reported.
   `test_a_transient_failure_still_propagates_so_stripe_retries` stays green
   beside it, which is the pair that says what is swallowed and what is not.

## Acceptance

- [x] A transport that throws while sending the "you're in" email leaves the access granted, the request answering as a sent one would, and the failure reported
- [x] A paid checkout whose "you're in" email fails still records the fulfilment, marks a followed invitation and answers the webhook
- [x] A failure that is not the send — a plan limit, a database that went away — still reaches the caller
- [x] `docs/flows/accesses.md` says what a failed send does
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Found while building `T-186`, 22 September 2026.
