---
id: T-121
title: A Peer pays for a Series in a browser
stream: workflow
status: blocked
owner: unassigned
estimate: M
depends: T-120
blocks: none
---

# T-121 — A Peer pays for a Series in a browser

## Why

`T-120` walks every way into a Series except the one that moves money. The
checkout path is built (`docs/flows/checkout.md`): a priced Series on a
Group with a connected account sends the buyer to Stripe's hosted Checkout,
and a signed `checkout.session.completed` webhook becomes the access. The
beta gate wants "real Stripe test-mode … smoke tests" and "payment-to-access
fulfilment" measured; nothing drives the browser side of it.

Afterwards a fourth journey prices the Series, sends a Peer through Stripe's
test-mode Checkout with the `4242` card, and sees the access arrive.

## Blocked on

What: the owner's `.env.e2e` (`D-045`) and `T-161`'s first run with it.
`T-161`'s first-share journey now pays for a Series in a browser: a real
Checkout Session on the owner's test account, completed by a signed
`checkout.session.completed` built from the session read back from Stripe —
this task's second webhook option, taken, with neither secret in Node (the run
signs with a secret it mints). What `T-161` does not do is drive Stripe's own
Checkout page with the `4242` card; the owner walks that by hand as its last
box. When that walk is recorded, this task is either closed as covered or
narrowed to the Checkout page alone.

Who: wayne — the `.env.e2e` values (`docs/tinker/e2e-first-share.md` in the
code repository) and the walk.

## Decisions taken to make this specifiable

**Stripe's real test mode, not a fake seller.** `STRIPE_SECRET` and
`STRIPE_WEBHOOK_SECRET` are set locally in test mode, the checkout code calls
Stripe through `Http::` with the `Stripe-Account` header, and `PLAN.md`'s
rule is that real vendor smoke tests validate payload shape. A fake
`SellsSeries` bound for the run would prove Qori's handling of a payload Qori
wrote, which the PHPUnit suite already does.

**The connected account is seeded, never connected by the journey.** Stripe's
OAuth sign-in asks for a real Stripe login, which no run may hold. The command
writes the owner-supplied account id onto the run's Group before the journey
starts; the journey prices the Series from the Series page and never visits
Integrations.

**Stripe's Checkout page is driven by Playwright**, on Stripe's own domain:
email, the `4242 4242 4242 4242` card, any future expiry, any CVC, a name,
then Pay. Stripe's test Checkout is stable enough for this and the run does
not need to own its selectors: a change there fails the journey loudly, which
is what the beta gate's smoke test is for.

The rest — the webhook path, the settings names, the assertion on "Confirming
your payment" giving way to the Series — waits on the block above.

## Preconditions

**Data this task verifies against:** the run's own database, plus the
sandbox connected account above.

**Equipment:** as `T-120`, plus Stripe test-mode keys in `.env` (present) and,
depending on the decision, the Stripe CLI logged in.

## Scope

**In:**

- A fourth journey, `paid-series.spec.ts`: price the Series, a stranger gets
  a code, is sent to Stripe Checkout, pays with the test card, is shown
  "Confirming your payment", and reaches `/shared/{id}` when the webhook
  lands.
- Whatever the command needs to seed the connected account and route the
  webhook.

**Out:**

- Refunds, disputes, a declined card, cancelling at Checkout.
- Qori's own subscription checkout (`billing.md`).
- Anything live-mode.

## Files

| Path                                       | Change | Notes                                    |
| ------------------------------------------ | ------ | ---------------------------------------- |
| `app/Console/Commands/EndToEndCommand.php` | edit   | Seeds the account; the webhook path      |
| `tests/e2e/paid-series.spec.ts`            | new    | The journey                              |
| `config/qori.php`                          | edit   | `e2e.connect_account`, read from `env()` |
| `.env.example`                             | edit   | The key above                            |
| `docs/tinker/e2e.md`                       | edit   | The fourth journey and what it needs     |

Flows: none — the journey drives the checkout flow as it is.

## Database

None.

## Code

To be written with literal names once the block clears; the shape is in the
decisions above.

## Copy

None.

## Routes

None.

## Tests

To be written with the Code section.

## Acceptance

- [ ] `php artisan qori:e2e --only=pays` sends a Peer through Stripe test-mode
      Checkout and ends on `/shared/{id}` with the access granted
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **Added 21 September 2026:** `T-161` takes the second option below — the
  completion read back from Stripe and delivered to `POST /webhooks/stripe`
  signed with the run's secret — for the first-share journey's script.

- The connected account id and the webhook decision — the owner's, under
  **Blocked on**.
- Whether the seeded account id is one env key (`QORI_E2E_CONNECT_ACCOUNT`)
  or an option (`--connect-account=`) — anyone's, once the first is answered.

## Re-scope log

None.

## Notes

Opened 17 September 2026 beside `T-120`, because the owner asked for the
payment flow in the same breath and the answer is that it can be walked the
day a sandbox connected account exists.
