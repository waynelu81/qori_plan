---
id: T-103
title: A refund revokes access and the vendor grant
stream: selling
status: draft
owner: unassigned
estimate: M
depends: T-091
blocks: T-094
---

# T-103 — A refund revokes access and the vendor grant

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016`, the owner's BYO blueprint and the developer review of the same day.

## Why

`D-016`'s fifth step is revoke: on a refund, Qori asks the vendor to remove the
Peer's grant with the creator's token, best effort. Nothing in the code can
reach that step, because nothing reacts to a refund at all. The webhook handles
`customer.subscription.*`, `account.application.deauthorized` and
`checkout.session.completed`, and answers every other type with `ignored`
(`app/Http/Controllers/StripeWebhookController.php:39-61`);
`docs/flows/checkout.md:129-131` says so in as many words. A creator who
refunds a Peer in their own Stripe dashboard — which is where refunds live,
because the charge is direct and the creator is merchant of record
(`docs/project-plan.md:190-193`) — leaves that Peer with the Series, and with
a viewer permission on the creator's own folder or meeting.

Afterwards `charge.refunded` on the creator's connected account finds the
`payment_fulfilments` row, records the refund on it, revokes the Access and —
through `T-091`'s hook inside `AccessService::revoke()` — asks the vendor to
drop the grant, with the scheduled sweep retrying whatever the vendor refused.
A refund that overtakes its own payment leaves no Access behind it, because
the row it wrote is the guard `T-102`'s `fulfil()` reads.

This task and `T-102` are why the `storage` stream puts both before any paid
Series uses a provider: a sale that ends and cannot reach the vendor is the
one case that leaves standing access on somebody else's account.

## Decisions taken to make this specifiable

**Qori never issues a refund; it only reacts to one.** §7.2 locks direct
charges on full-dashboard accounts, so refunds and disputes sit in the
creator's own Stripe (`docs/project-plan.md:184-196`), and
`docs/flows/series.md:232` already treats revoking access as "half of a
refund". Nothing here calls Stripe.

**The trigger is `charge.refunded`, delivered as a connected-account event.**
It "occurs whenever a charge is refunded, including partial refunds"
(<https://docs.stripe.com/api/events/types#event_types-charge.refunded>), and a
direct charge belongs to the creator's account, so the event carries `account`
at the top level beside `type` (<https://docs.stripe.com/connect/webhooks>) —
the field `account.application.deauthorized` already reads
(`StripeWebhookController.php:51-55`). The endpoint stays one URL with one
secret (`config/services.php:25-42`, `routes/web.php:46-48`), and the owner
subscribes it to connected-account events (provisional — see below).

**The row is found by `payment_reference`, which is the PaymentIntent.**
`fulfil()` stores the session's `payment_intent`
(`StripeWebhookController.php:86`, `app/Services/CheckoutService.php:166-179`),
and a Charge carries `payment_intent`, `amount`, `amount_refunded`, `refunded`
and `currency` (<https://docs.stripe.com/api/charges/object>). The charge id is
stored beside it rather than used to search, because Qori never sees a `ch_…`
until the refund arrives.

**Only a full refund revokes** (provisional — the owner's). `refunded` is true
only when the charge is fully refunded, so fullness is
`refunded === true || amount_refunded >= amount`. A partial refund is recorded
and changes nothing else: the creator giving half the money back has not taken
the Series away, and guessing otherwise takes something away that nobody asked
to take.

**The signed payload is trusted and the charge is not re-read.** The signature
proves Stripe sent it (`StripeWebhookController.php:100-127`), and a retrieve
would put a vendor call inside the webhook for no new fact. To survive
out-of-order delivery, `refunded_amount_cents` takes the larger of what is
stored and what the event carries, and `refunded_at`, once set, is never
cleared.

**A refund is a timestamp beside the status, not a new `FulfilmentStatus`
case.** The status answers "did the money become access", and after a refund
the answer is still "it did, and then it was given back" — `T-102` builds four
states around that question and adding a fifth would change what `isSettled()`
and Confirming mean.

**The Access revoked is the one the row names, and only while it is active.**
`payment_fulfilments.access_id` is written by `fulfil()`
(`CheckoutService.php:142-144`), so it names the Access this payment produced;
nothing searches for another. A row whose `access_id` is null has nothing to
revoke. Re-revoking is skipped rather than repeated, so a redelivered event
does not re-stamp `revoked_at`.

**The vendor grant is not revoked here, and no grant state is written here.**
This task creates no grant and marks nothing `granted`; when a grant becomes
`granted` is each provider task's to state. `T-091` puts
`VendorAccessService::revokeFor($access)` inside `AccessService::revoke()`, so
this task calls `revoke()` and gets it, and what happens to each
`VendorGrantStatus` stays `T-091`'s. Its `granted` and
`awaiting_acceptance` rows are tried once each with
`VendorAccessService::REQUEST_TIMEOUT_SECONDS` (provisional 5), which is what
bounds the cost this adds to a webhook; a refusal or a timeout leaves the row
to `qori:access:reconcile`, up to `VendorAccessService::REVOKE_ATTEMPTS`. The
states still waiting on somebody stop being chased of their own accord,
because `VendorGrant::scopeDue()` and `scopeRecheckable()` each require an
active Access: `pending` (Qori was going to retry, nobody had to act) and
`needs_creator` (the creator had to reconnect, lift a policy or raise a plan)
leave the retry pass, the re-check of `granted` rows stops, and
`awaiting_identity` (the Peer had to confirm a vendor account, `T-092`) was
never retried. None of it can stop the Access being revoked or reach the
buyer: with no Access, the Series page refuses before a grant state is read.

**One container per Series is what makes a refund safe to act on.** `T-091`
allows one grant row per (Access, container), and a container is dedicated to
one Series rather than shared between them, so dropping this Series' grant
cannot take away material the same person still holds through another Series
they paid for. If a provider forces that rule to change, it changes in
`T-091` and this task's revoke is re-read against it — it is not something to
work around from the money side.

**A refund is a revoke, not a reconciliation.** `T-091`'s reconciliation
triggers are a Peer confirming or changing an identity (`T-092`), the creator
reconnecting the same account or connecting a different one, and a container
being replaced. A refund is none of them: it ends the Access, and the ensure
step is never run for it again.

**`AccessService::revoke()` establishes its own Group context.** A webhook has
no current Group, `vendor_grants` is group-owned, and
`docs/flows/accesses.md:63-71` already says a service reachable from both sides
establishes context rather than assuming it. `grant()` does exactly this
(`app/Services/AccessService.php:54`); `revoke()` gains the same wrapper.

**The refund is recorded before the Access is revoked.** If anything after the
write throws, the webhook answers non-2xx, Stripe redelivers, and the
redelivery finishes the job with the guard already in place. The reverse order
would let a redelivery that failed halfway grant the Series back through
`T-102`'s landing-page fulfilment.

**A refunded row never renders Confirming.** `T-102`'s `confirmingFor()` shows
a `pending` row with `completed_at` set for as long as the money is in flight;
a refund settles it, so that lookup gains one condition and the buyer meets the
ordinary refusal instead of a page saying their bank is still confirming.

**Nobody is told anything new** (provisional — the owner's). The buyer meets
the refusal that already exists on the Series page —
`errors.access.not_granted` (`lang/en/errors.php:293-296`), raised by
`SharedController::show()` when `Access::forUser()` finds no active row
(`app/Http/Controllers/Shared/SharedController.php:114-117`,
`app/Models/Access.php:253-259`) — and Stripe's own refund receipt is what
tells them why. The creator's Peer list already shows active accesses only
(`app/Http/Controllers/Share/SeriesController.php:293-310`, `:299`), so a
refunded Peer leaves the list the way a removed one does. No new copy, and so
no new lang key.

**A refund that later fails, and a dispute, are out.** Both are real and both
are a different question — whether access comes back — and neither can be
specified from documentation alone.

## Preconditions

`T-091` done, so `VendorAccessService::revokeFor()`, the `vendor_grants` row
and `qori:access:reconcile`'s revoke pass exist. `T-102` in practice first: it
writes the `payment_fulfilments` row at `begin()`, so a refund that overtakes
the payment has a row to mark, and its `fulfil()` reads the column this task
adds. Tests run on the local Postgres (`_testing`).

**Data this task verifies against:** a clean database.

**Equipment:** the Stripe CLI signed in to the sandbox, forwarding
connected-account events: `stripe listen --forward-connect-to
localhost:8001/webhooks/stripe` (<https://docs.stripe.com/cli/listen>) — a
plain `--forward-to`, which is what `release-prerequisites.md:16` records,
forwards platform events only and delivers nothing for a direct charge. The
Group whose Connect account `T-062` created, with one paid Series bought
end to end, so there is a real `pi_…` to refund.

**Spike:** no separate task; the fixtures are this task's first step. The field
names above come from the Stripe object and event references, not from an
observed response, and an expected response is not a fixture. Before the tests
below are written, capture from the sandbox and commit, redacted and dated:
`tests/Fixtures/stripe/charge-refunded-full.json` and
`tests/Fixtures/stripe/charge-refunded-partial.json` — the first from a full
refund of that payment, the second from `stripe refunds create --amount …
--stripe-account acct_…`. `stripe trigger` may cover `charge.refunded`
(<https://docs.stripe.com/cli/trigger>); check `stripe trigger --help` for the
installed version, and otherwise refund in the Dashboard and take the payload
from the connected account's event log. `tests/Fixtures/stripe/` is created by
`T-102`.

## Scope

**In:**

- `charge.refunded` dispatched in `StripeWebhookController`, as a
  connected-account event.
- `App\Data\ChargeRefund`, and `CheckoutService::refund()`: find the row,
  record the refund, revoke the Access on a full refund.
- `payment_fulfilments`: `refunded_at`, `refunded_amount_cents`,
  `charge_reference`, and an index on `payment_reference`.
- `AccessService::revoke()` establishing Group context, so the `T-091` hook
  inside it can read group-owned rows from a webhook.
- One condition on `T-102`'s `confirmingFor()`, so a refunded row does not
  confirm.
- `docs/flows/checkout.md` and `accesses.md`; the vendor half in
  `docs/flows/vendor-access.md`, which `T-091` creates.

**Out:**

- Issuing a refund from Qori, and any refund UI for the creator — §7.2.
- Partial refunds changing access — the owner's, below.
- `refund.updated` / `charge.refund.updated`, a refund that fails after the
  fact, and every `charge.dispute.*` event.
- The vendor call itself, the grant row and its retries — `T-091`'s
  `revokeFor()` and `qori:access:reconcile`.
- The delayed-payment events, the Confirming page and the landing-page
  fulfilment — `T-102`; this task adds one condition to its lookup and
  respecifies none of it.
- Telling the buyer or the creator that a refund landed, and any staff view of
  refunded rows (`app/Enums/FulfilmentStatus.php:5-11` points at `T-013`).
- Anything in `T-089`'s Open route: a Peer whose Access is revoked fails the
  access check before a grant is ever read.

## Files

| Path                                                                                                   | Change | Notes                                                                                                |
| ------------------------------------------------------------------------------------------------------ | ------ | ---------------------------------------------------------------------------------------------------- |
| `database/migrations/2026_09_18_000000_add_refunds_to_payment_fulfilments.php`                         | new    | Three columns, one index                                                                             |
| `app/Data/ChargeRefund.php`                                                                            | new    | The event's charge, typed                                                                            |
| `app/Models/PaymentFulfilment.php`                                                                     | edit   | Columns, casts, `isRefunded()`; `group()` too, if `T-102` has not; still not group-scoped (`:11-18`) |
| `app/Services/CheckoutService.php`                                                                     | edit   | `refund()`, and one condition in `T-102`'s `confirmingFor()`                                         |
| `app/Services/AccessService.php`                                                                       | edit   | `revoke()` wrapped in `CurrentGroup::runFor()`; `T-091`'s hook stays inside it                       |
| `app/Http/Controllers/StripeWebhookController.php`                                                     | edit   | The `charge.refunded` branch, before the `checkout.session.*` dispatch                               |
| `database/factories/PaymentFulfilmentFactory.php`                                                      | edit   | A `refunded()` state. Not in the repo today: `T-102` creates it, so `new` if this task runs first    |
| `tests/Fixtures/stripe/charge-refunded-full.json` `tests/Fixtures/stripe/charge-refunded-partial.json` | new    | Captured from the sandbox, redacted, dated                                                           |
| `tests/Feature/Checkout/RefundTest.php`                                                                | new    | 12 cases                                                                                             |
| `tests/Feature/Access/AccessServiceTest.php`                                                           | edit   | One case: revoke outside Group context                                                               |
| `docs/flows/checkout.md`                                                                               | edit   | "The path back" gains the refund event; `:129-131` stops saying refunds are not built                |
| `docs/flows/accesses.md`                                                                               | edit   | "The creator side" (`:101-108`): a refund is the second way an Access is revoked                     |
| `docs/flows/vendor-access.md`                                                                          | edit   | Not in the repo today: `T-091` creates it. The money path into `revokeFor()`                         |
| `docs/tinker/accesses.md`                                                                              | edit   | A "Refund one" recipe beside `T-102`'s "Pay for one"                                                 |

The flow rows this task owes are in the table above. Two of those paths do not
exist yet and neither is this task's to create: `docs/flows/vendor-access.md`
comes with `T-091`, `database/factories/PaymentFulfilmentFactory.php` with
`T-102`.

## Database

Only what changes; the table is in
`database/migrations/2026_09_09_000000_create_payment_fulfilments_table.php`.

| Table                 | Column                  | Type        | Null | Default | Index / constraint                                                                 |
| --------------------- | ----------------------- | ----------- | ---- | ------- | ---------------------------------------------------------------------------------- |
| `payment_fulfilments` | `refunded_at`           | timestamp   | yes  | null    | Set once, when the charge is fully refunded; never cleared                         |
| `payment_fulfilments` | `refunded_amount_cents` | integer     | yes  | null    | The charge's `amount_refunded`, in the row's existing `currency` (`:40`)           |
| `payment_fulfilments` | `charge_reference`      | string(255) | yes  | null    | The `ch_…` the refund was made against; Qori learns it only from this event        |
| `payment_fulfilments` | —                       | —           | —    | —       | index `(payment_reference)` — the refund lookup; the column has none today (`:38`) |

Migration: `database/migrations/2026_09_18_000000_add_refunds_to_payment_fulfilments.php`

## Code

```php
namespace App\Data;

/**
 * A refunded charge, as the webhook received it. Field names from the Stripe
 * charge object (https://docs.stripe.com/api/charges/object); the fixtures confirm them.
 */
class ChargeRefund
{
    public function __construct(
        public string $chargeId,               // id, ch_…
        public ?string $paymentReference,      // payment_intent, pi_…
        public ?string $connectedAccountId,    // the event's top-level `account`
        public ?int $amountCents,              // amount
        public ?int $refundedCents,            // amount_refunded
        public ?string $currency,
        public bool $fullyRefunded = false,    // refunded
    ) {}

    /** @param array<string, mixed> $charge */
    public static function fromStripe(array $charge, ?string $account): self;

    /** refunded, or amount_refunded at or above amount — either answer means the whole charge came back. */
    public function isFull(): bool;
}
```

```php
namespace App\Models;

class PaymentFulfilment extends Model
{
    // fillable gains refunded_at, refunded_amount_cents, charge_reference;
    // casts gain refunded_at => 'datetime' and refunded_amount_cents => 'integer'
    public function isRefunded(): bool;       // refunded_at !== null
    public function group(): BelongsTo;       // T-102 adds this; it is needed here either way
}
```

```php
namespace App\Services;

class CheckoutService
{
    public function __construct(
        private SellsSeries $payments,
        private AccessService $accesses,
    ) {}

    /**
     * A refund the creator made in their own Stripe. Best effort and idempotent: the row is
     * marked first, the Access is revoked only while it is still active, and T-091's
     * revokeFor() runs inside AccessService::revoke(). Returns the row, or null when the
     * charge names no payment this app knows.
     */
    public function refund(ChargeRefund $refund): ?PaymentFulfilment;
}
```

`refund()`, in order:

1. `$row = PaymentFulfilment::query()->where('payment_reference', $refund->paymentReference)->first()`,
   skipped when `paymentReference` is null. No row: `Log::warning` with the
   charge id and the account, return null — a charge carries no Qori metadata
   (`app/Integrations/Stripe/Connect.php:197-218` sets it on the session only),
   so nothing else can identify the buyer.
2. When `$row->group?->connect_account_id` and `$refund->connectedAccountId`
   are both filled and differ: `Log::warning`, return null. A direct charge
   belongs to exactly one connected account.
3. Write, whatever the amount: `charge_reference`, `refunded_amount_cents` =
   `max((int) $row->refunded_amount_cents, (int) $refund->refundedCents)`, and
   `refunded_at` = `now()` when `$refund->isFull()` and `refunded_at` is null.
   `status` is untouched.
4. Return the row when the refund is not full.
5. `$access = $row->access_id === null ? null : Access::query()->forGroup((string) $row->group_id)->whereKey($row->access_id)->first()`
   — `forGroup()`, not `acrossAllGroups()`: this is a single-tenant read with
   no ambient context, which is what that scope is for
   (`app/Concerns/BelongsToGroup.php:38-57`), and `existingAccess()` already
   reads that way (`CheckoutService.php:182-190`).
6. `$access?->isActive()` → `$this->accesses->revoke($access)`. Nothing else.

```php
// App\Services\AccessService::revoke — the context wrapper
public function revoke(Access $access): Access
{
    $group = $access->group;   // Group is not group-scoped, so this loads with no context

    return $group === null
        ? $this->revokeRow($access)
        : $this->current->runFor($group, fn (): Access => $this->revokeRow($access));
}

/** The two writes as they are today (:126-134), plus T-091's $this->vendorAccess->revokeFor($access). */
private function revokeRow(Access $access): Access;
```

```php
// App\Http\Controllers\StripeWebhookController::__invoke — after the deauthorized branch (:51-55)
if ($type === 'charge.refunded') {
    $checkout->refund(ChargeRefund::fromStripe(
        (array) ($event['data']['object'] ?? []),
        isset($event['account']) ? (string) $event['account'] : null,
    ));

    return response()->json(['handled' => $type]);
}
```

```php
// App\Services\CheckoutService::confirmingFor — T-102's lookup, one condition
// $row = PaymentFulfilment::latestFor($peer, $seriesId);
// return $row?->isRefunded() ? null : $row;   // then T-102's pending / completed / failed rules
```

Nothing catches around step 6. A database failure propagates, the webhook
answers non-2xx and Stripe redelivers, which is the case a retry can fix —
the same reasoning `CheckoutService::fulfil()` records at `:75-82`. A vendor
failure inside `revokeFor()` never reaches here at all: `T-091` records it on
the grant row and `qori:access:reconcile` retries it up to
`VendorAccessService::REVOKE_ATTEMPTS`.

## Copy

**None.** The buyer meets `errors.access.not_granted`, which exists
(`lang/en/errors.php:293-296`), and no screen in this task says the word
refund — see the decision above, and the bullet below if the owner wants one.

## Routes

**None.** `webhooks.stripe` (`routes/web.php:46-48`) carries a new event type
and keeps its verb, path, name and controller.

## Tests

Every case sends a payload built from the matching fixture under
`tests/Fixtures/stripe/`, with the ids and the account swapped in, through the
signed `send()` helper (`tests/Feature/Checkout/StripeWebhookTest.php:49-62`);
the vendor is `T-091`'s `tests/Doubles/GrantsEveryPeer`, bound the way `T-091`
binds it — `when(VendorAccessService::class)->needs('$providers')->give(…)` —
with `Http::preventStrayRequests()`, so no test here reaches a vendor.

**New: `tests/Feature/Checkout/RefundTest.php` — 12 cases**

1. `test_a_full_refund_revokes_the_access` — the Access is `revoked` with
   `revoked_at` set, and the response is 200.
2. `test_a_full_refund_records_the_refund_on_the_payment` — `refunded_at`,
   `refunded_amount_cents` and `charge_reference` are written and `status`
   still reads `granted`.
3. `test_a_full_refund_asks_the_vendor_to_drop_every_grant` — the double saw
   one `revoke()` per `vendor_grants` row, and the rows read `revoked`.
4. `test_a_vendor_refusal_still_revokes_the_access` — the double refuses; the
   Access is `revoked`, the grant row is left for the sweep, the response is 200.
5. `test_a_partial_refund_leaves_the_access_alone` — the Access stays active,
   `refunded_at` is null, `refunded_amount_cents` is the part refunded.
6. `test_a_refund_that_overtakes_the_payment_leaves_no_access` — a `pending`
   row with no `access_id` is marked, nothing is revoked, and a following
   `checkout.session.async_payment_succeeded` grants nothing (`T-102`'s guard).
7. `test_a_redelivered_refund_changes_nothing` — the same event twice leaves
   one `revoked_at` and one `refunded_at`, unchanged by the second.
8. `test_an_out_of_order_refund_never_lowers_the_amount` — the partial event
   after the full one keeps the larger `refunded_amount_cents` and
   `refunded_at`.
9. `test_a_refund_for_another_connected_account_is_ignored` — the event's
   `account` does not match the Group's; the Access stays active.
10. `test_a_refund_for_an_unknown_payment_is_acknowledged` — no row, 200, no
    access anywhere touched.
11. `test_a_refunded_buyer_is_refused_on_the_series_page` — `GET /shared/{id}`
    after the refund is a 403 with `errors.access.not_granted`, not Confirming.
12. `test_a_stalled_grant_is_no_longer_chased_after_a_refund` — a row left
    `pending`, one left `needs_creator` and one left `awaiting_identity`; after
    the refund `VendorGrant::due()` and `->recheckable(now())` return none of
    them. This asserts `T-091`'s active-Access rule from the money side rather
    than restating it.

**Changed:**

- `tests/Feature/Access/AccessServiceTest.php` — one case,
  `test_revoking_works_outside_group_context`: `CurrentGroup::forget()`, then
  `revoke()` writes the row and reaches `T-091`'s hook without a
  `RuntimeException` from `CurrentGroup::idOrFail()`
  (`app/Support/CurrentGroup.php:56-67`).
- `tests/Feature/Checkout/StripeWebhookTest.php` — not edited here, and named
  because it looks as though it should be: `test_other_events_are_acknowledged`
  (`:164-173`) uses `invoice.paid`, so the new branch leaves it passing.
  `T-102` does edit this file.

## Acceptance

- [ ] A full refund on a creator's connected account revokes that Peer's
      Access and asks the vendor to drop every grant it holds for the Series,
      within `REQUEST_TIMEOUT_SECONDS` per row, and a vendor refusal neither
      stops the revoke nor reaches the buyer
- [ ] After a refund nothing keeps chasing that Peer's grants: `pending`,
      `needs_creator` and `awaiting_identity` rows leave the retry and
      re-check passes, and only `granted` and `awaiting_acceptance` rows stay
      with the sweep, as its revokable ones
- [ ] A partial refund is recorded and changes nothing else
- [ ] A refund that arrives before the payment settles leaves no Access, then
      or later
- [ ] The same event delivered twice, or out of order, leaves the same row
- [ ] A refunded buyer meets the ordinary refusal on the Series page, never a
      Confirming page
- [ ] The fixtures under `tests/Fixtures/stripe/` are captured from the
      sandbox, dated and redacted, and every payload in the tests is built
      from one
- [ ] `docs/flows/checkout.md`, `accesses.md`, `vendor-access.md` and the
      tinker recipe describe what was built
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Does a partial refund take access away? Full-refund-only is the provisional
  choice — the owner's.
- Does a chargeback (`charge.dispute.closed`, `lost`) do what a refund does,
  or is it its own task? — the owner's.
- Is the buyer told a refund is why the Series closed, rather than meeting
  `errors.access.not_granted`? — the owner's.
- Does the creator's Peer list show a refunded Peer rather than dropping them
  silently? No column exists (`SeriesController.php:293-310`) — the owner's.
- Can one endpoint and one signing secret carry platform and
  connected-account events, or does live need a second endpoint, a
  `STRIPE_CONNECT_WEBHOOK_SECRET` and a second accepted signature?
  `release-prerequisites.md:15` lists neither, and
  `account.application.deauthorized` already rests on the answer untested —
  the owner's, from the dashboard.
- `charge.refunded`'s exact payload, and whether `stripe trigger` can produce
  a partial one, before the field names become fixtures — anyone's, with the
  sandbox.
- Should `depends:` name `T-102` as well? This reads the row `begin()` writes
  and adds a condition to `confirmingFor()`, but `T-102` carries
  `blocks: none` — anyone's, with the board.
- Does `T-091`'s `revokeFor()` establish Group context itself, as its
  `ensureFor()` does, making the wrapper on `revoke()` belt and braces? —
  anyone's, with `T-091`.
- `T-102`'s names (`latestFor()`, `confirmingFor()`, `group()`,
  `PaymentFulfilmentFactory`, `tests/Fixtures/stripe/`) are from its draft and
  need re-checking when `T-102` is `ready` — anyone's.

### From the storage review, 20 September 2026

- **A refund cannot revoke what the grant rows no longer remember** (`F01`,
  `F02`). Rows still `pending` are excluded from cleanup here, yet a create
  whose response was lost may have produced a real permission; a permission
  shared with another active purchase must not be deleted by this refund at
  all; and a refund racing a grant has no specified order. All three wait on
  `T-091`'s durable revocation intent and its ownership rule — anyone's.
- **The safety argument still assumes a container dedicated to one Series**,
  which `D-036` removed for Drive. Re-read it against item grants before this
  is `ready` — anyone's.
- **Who authorises and performs a refund when the creator cannot deliver**
  (`F06`) is unspecified under the direct-charge arrangement, and it is the
  only exit a buyer has when a grant can never be made — the owner's.

## Re-scope log

None.

## Notes

This task shares seven paths with `T-102` — `CheckoutService.php`,
`StripeWebhookController.php`, `PaymentFulfilment.php`,
`PaymentFulfilmentFactory.php`, `tests/Fixtures/stripe/` (different files in
one new directory), `docs/flows/checkout.md` and `docs/tinker/accesses.md` —
and three with `T-091`: `AccessService.php`, `docs/flows/accesses.md` and
`docs/flows/vendor-access.md`. None of them overlaps line for line; this task
adds one method, one branch, one wrapper and a paragraph each to the four
documents. But whichever runs second rebases onto the other, and two `doing`
tasks claiming one of those paths is the collision the board exists to show.

`payment_fulfilments` is deliberately not group-scoped
(`PaymentFulfilment.php:11-18`), and the new columns do not change that. It is
why `refund()` names the Group explicitly on the Access read rather than
relying on ambient context, and why `revoke()` has to establish that context
before `T-091`'s hook touches the group-owned `vendor_grants`.

A residual hole the owner may want closed in whichever task runs second: a
charge carries none of Qori's metadata, because `Connect::checkoutFor()` sets
`metadata[…]` on the session and only `payment_intent_data[description]` on
the payment (`app/Integrations/Stripe/Connect.php:197-218`). Sending
`payment_intent_data[metadata]` as well would make every charge name its
Series, Group and buyer, so a refund could be attributed even with no
fulfilment row. It is one line in `Connect.php`, which `T-102` edits and this
task does not.

`CLAUDE.md` still says integrations expose `name()` and are bound in
`AppServiceProvider`; the code says `provider()` and
`IntegrationServiceProvider` (`app/Providers/IntegrationServiceProvider.php:24-40`),
and this task follows the code.
