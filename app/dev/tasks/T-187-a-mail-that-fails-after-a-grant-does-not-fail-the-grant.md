---
id: T-187
title: A mail that fails after a grant does not fail the grant
stream: delivery
status: draft
owner: unassigned
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

None yet.

## Preconditions

None.

## Scope

**In:**

- A failed "you're in" send after a grant.

**Out:**

- Retrying the email. There is no queue worker, and nothing is `ShouldQueue`
  until there is.
- Mail sent before anything is written, such as a sign-in code, where failing
  the request is the right answer.

## Files

To be settled when ready.

## Database

None expected.

## Code

To be settled when ready.

## Copy

None expected.

## Routes

None.

## Tests

To be settled when ready.

## Acceptance

- [ ] A transport that throws while sending the "you're in" email leaves the access granted, the request answering as a sent one would, and the failure reported
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Where the catch sits: in `AccessService::announce()`, around the one call,
  or wherever else Qori sends after a write. `InvitationService::send()`
  mails after its transaction too, and there a failure the creator is not
  told about means an invitation they think went.
- How it is reported: `report($e)` reaches the logs and Sentry once Qori has
  one. Whether the creator or staff should see a failed "you're in", and
  where — `T-129` asks the same of the recording email.

## Re-scope log

None.

## Notes

Found while building `T-186`, 22 September 2026.
